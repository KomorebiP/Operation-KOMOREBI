import copy
from dataclasses import replace
import pickle
import unittest

import numpy as np

from rrct import (
    AdaptiveFeedbackRegulator,
    FeedbackTelemetry,
    IntentionCalibrationRecord,
    RRCTAgent,
    compute_feedback_telemetry,
    local_transition_jacobian,
)


def _telemetry(
    control_signal: float,
    *,
    surprise: float = 0.0,
    redundancy: float = 0.0,
) -> FeedbackTelemetry:
    return FeedbackTelemetry(
        surprise=surprise,
        differentiation=0.4,
        redundancy=redundancy,
        saturation=0.3,
        temporal_novelty=0.5,
        salience_entropy=0.6,
        demand=0.5,
        congestion=0.4,
        control_signal=control_signal,
    )


def _agent(seed: int, *, feedback_mode: str = "adaptive", **overrides) -> RRCTAgent:
    options = {
        "projector_ranks": (3, 6, 9, 12),
        "seed": seed,
        "feedback_mode": feedback_mode,
    }
    options.update(overrides)
    return RRCTAgent(12, **options)


class FeedbackTelemetryTests(unittest.TestCase):
    def test_telemetry_is_finite_bounded_deterministic_and_nonmutating(self) -> None:
        states = np.asarray(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]],
            dtype=np.float64,
        )
        salience = np.asarray([0.2, 0.7, 0.4], dtype=np.float64)
        workspace = np.asarray([0.8, -0.2, 0.1], dtype=np.float64)
        prediction_error = np.asarray([0.1, -0.4, 0.2], dtype=np.float64)
        previous_workspace = np.asarray([-0.2, 0.3, 0.1], dtype=np.float64)
        originals = tuple(
            value.copy()
            for value in (
                states,
                salience,
                workspace,
                prediction_error,
                previous_workspace,
            )
        )

        first = compute_feedback_telemetry(
            specialist_states=states,
            specialist_salience=salience,
            workspace=workspace,
            prediction_error=prediction_error,
            previous_workspace=previous_workspace,
        )
        second = compute_feedback_telemetry(
            specialist_states=states,
            specialist_salience=salience,
            workspace=workspace,
            prediction_error=prediction_error,
            previous_workspace=previous_workspace,
        )

        self.assertEqual(first, second)
        values = np.asarray(tuple(first.__dict__.values()), dtype=np.float64)
        self.assertTrue(np.all(np.isfinite(values)))
        self.assertTrue(np.all((0.0 <= values) & (values <= 1.0)))
        for value, original in zip(
            (states, salience, workspace, prediction_error, previous_workspace),
            originals,
        ):
            np.testing.assert_array_equal(value, original)

    def test_telemetry_input_validation_fails_closed(self) -> None:
        valid = {
            "specialist_states": np.eye(2),
            "specialist_salience": np.ones(2),
            "workspace": np.ones(2),
            "prediction_error": np.zeros(2),
            "previous_workspace": np.zeros(2),
        }
        invalid_cases = (
            {"specialist_states": np.ones(2)},
            {"specialist_states": np.asarray([[1.0, np.nan]])},
            {"specialist_salience": np.ones(3)},
            {"specialist_salience": np.asarray([1.0, -0.1])},
            {"workspace": np.ones(3)},
            {"prediction_error": np.asarray([0.0, np.inf])},
            {"previous_workspace": np.ones(3)},
        )
        for replacement in invalid_cases:
            with self.subTest(replacement=tuple(replacement)):
                arguments = dict(valid)
                arguments.update(replacement)
                with self.assertRaises(ValueError):
                    compute_feedback_telemetry(**arguments)

    def test_workspace_access_is_activity_gated_and_rank_one_is_not_differentiated(self) -> None:
        base = {
            "specialist_states": np.eye(3),
            "specialist_salience": np.ones(3),
            "workspace": np.asarray([0.2, 0.0, 0.0]),
            "prediction_error": np.zeros(3),
            "previous_workspace": np.zeros(3),
        }
        rank_one = compute_feedback_telemetry(
            **base,
            workspace_proposal_states=np.asarray([[1.0, 0.0, 0.0]]),
            workspace_weights=np.ones(1),
        )
        orthogonal = compute_feedback_telemetry(
            **base,
            workspace_proposal_states=np.eye(3),
            workspace_weights=np.full(3, 1.0 / 3.0),
        )
        tiny = compute_feedback_telemetry(
            **base,
            workspace_proposal_states=1e-12 * np.eye(3),
            workspace_weights=np.full(3, 1.0 / 3.0),
        )
        self.assertEqual(rank_one.differentiation, 0.0)
        self.assertGreater(orthogonal.differentiation, 0.8)
        self.assertLess(tiny.differentiation, 1e-8)
        self.assertGreater(rank_one.temporal_novelty, 0.99)

    def test_closure_is_tempered_by_surprise_at_fixed_recurrent_drive(self) -> None:
        low = AdaptiveFeedbackRegulator(0.7, 0.7).update(
            _telemetry(0.6, surprise=0.0)
        )
        high = AdaptiveFeedbackRegulator(0.7, 0.7).update(
            _telemetry(0.6, surprise=1.0)
        )
        self.assertEqual(low.desired_recurrent_gain, high.desired_recurrent_gain)
        self.assertLess(high.desired_closure_gain, low.desired_closure_gain)

    def test_regulator_rejects_invalid_telemetry_without_mutation(self) -> None:
        regulator = AdaptiveFeedbackRegulator(0.7, 0.8)
        before = pickle.dumps(regulator, protocol=5)
        invalid = (
            replace(_telemetry(0.5), control_signal=-0.01),
            replace(_telemetry(0.5), congestion=1.01),
            replace(_telemetry(0.5), surprise=np.nan),
            replace(_telemetry(0.5), demand=True),
        )
        for telemetry in invalid:
            with self.subTest(telemetry=telemetry):
                with self.assertRaises(ValueError):
                    regulator.update(telemetry)
                self.assertEqual(pickle.dumps(regulator, protocol=5), before)
        with self.assertRaises(TypeError):
            regulator.update(object())
        self.assertEqual(pickle.dumps(regulator, protocol=5), before)


class AdaptiveFeedbackRegulatorTests(unittest.TestCase):
    def test_updates_are_deterministic(self) -> None:
        first = AdaptiveFeedbackRegulator(
            0.8,
            0.9,
            minimum_gain=0.2,
            maximum_gain=1.2,
            adaptation_rate=0.4,
            maximum_step=0.08,
            deadband=0.01,
        )
        second = AdaptiveFeedbackRegulator(
            0.8,
            0.9,
            minimum_gain=0.2,
            maximum_gain=1.2,
            adaptation_rate=0.4,
            maximum_step=0.08,
            deadband=0.01,
        )
        sequence = (
            _telemetry(0.1, redundancy=0.8),
            _telemetry(0.9, surprise=0.7),
            _telemetry(0.4, surprise=0.2, redundancy=0.3),
        )
        for telemetry in sequence:
            self.assertEqual(first.update(telemetry), second.update(telemetry))
        self.assertEqual(first.snapshot(), second.snapshot())

    def test_slew_bounds_and_deadband(self) -> None:
        deadband = AdaptiveFeedbackRegulator(
            0.7,
            0.7,
            minimum_gain=0.2,
            maximum_gain=1.2,
            adaptation_rate=1.0,
            maximum_step=0.1,
            deadband=0.1,
        )
        quiet = deadband.update(_telemetry(0.55))
        self.assertEqual(quiet.next_recurrent_gain, 0.7)
        self.assertEqual(quiet.next_closure_gain, 0.7)
        self.assertFalse(quiet.recurrent_slew_limited)
        self.assertFalse(quiet.closure_slew_limited)

        regulator = AdaptiveFeedbackRegulator(
            0.2,
            0.2,
            minimum_gain=0.2,
            maximum_gain=1.2,
            adaptation_rate=1.0,
            maximum_step=0.1,
            deadband=0.0,
        )
        high = regulator.update(_telemetry(1.0, surprise=1.0))
        self.assertAlmostEqual(high.next_recurrent_gain, 0.3)
        self.assertAlmostEqual(high.next_closure_gain, 0.3)
        self.assertTrue(high.recurrent_slew_limited)
        self.assertTrue(high.closure_slew_limited)
        for _ in range(40):
            record = regulator.update(_telemetry(1.0, surprise=1.0))
            self.assertLessEqual(
                abs(record.next_recurrent_gain - record.applied_recurrent_gain),
                regulator.maximum_step + 1e-15,
            )
            self.assertLessEqual(
                abs(record.next_closure_gain - record.applied_closure_gain),
                regulator.maximum_step + 1e-15,
            )
            self.assertTrue(
                regulator.minimum_gain
                <= record.next_recurrent_gain
                <= regulator.maximum_gain
            )
            self.assertTrue(
                regulator.minimum_gain
                <= record.next_closure_gain
                <= regulator.maximum_gain
            )
        self.assertEqual(regulator.current_recurrent_gain, regulator.maximum_gain)

        for invalid in (-0.1, 1.21, np.nan, True):
            with self.subTest(invalid=invalid):
                before = pickle.dumps(regulator, protocol=5)
                with self.assertRaises(ValueError):
                    regulator.set_current(invalid, 0.5)
                self.assertEqual(pickle.dumps(regulator, protocol=5), before)

    def test_snapshot_roundtrip_has_no_aliasing(self) -> None:
        source = AdaptiveFeedbackRegulator(0.8, 0.9)
        source.update(_telemetry(0.2, surprise=0.3, redundancy=0.7))
        snapshot = source.snapshot()
        target = AdaptiveFeedbackRegulator(0.8, 0.9)
        target.load_snapshot(snapshot)
        self.assertEqual(target.snapshot(), source.snapshot())

        snapshot["configuration"]["deadband"] = 0.7
        snapshot["last_record"]["telemetry"]["surprise"] = 0.9
        self.assertEqual(target.snapshot(), source.snapshot())

    def test_snapshot_tampering_is_rejected_transactionally(self) -> None:
        source = AdaptiveFeedbackRegulator(0.8, 0.9)
        source.update(_telemetry(0.2, surprise=0.3, redundancy=0.7))
        valid = source.snapshot()

        corruptions = []
        unknown = copy.deepcopy(valid)
        unknown["future_field"] = 1
        corruptions.append(unknown)

        bad_digest = copy.deepcopy(valid)
        bad_digest["current_recurrent_gain"] += 0.01
        corruptions.append(bad_digest)

        bad_count = copy.deepcopy(valid)
        bad_count["update_count"] = 2
        bad_count["digest"] = source._digest_payload(
            {key: value for key, value in bad_count.items() if key != "digest"}
        )
        corruptions.append(bad_count)

        bad_bound = copy.deepcopy(valid)
        bad_bound["current_recurrent_gain"] = 2.0
        bad_bound["digest"] = source._digest_payload(
            {key: value for key, value in bad_bound.items() if key != "digest"}
        )
        corruptions.append(bad_bound)

        bad_telemetry = copy.deepcopy(valid)
        bad_telemetry["last_record"]["telemetry"]["surprise"] = 1.1
        bad_telemetry["digest"] = source._digest_payload(
            {key: value for key, value in bad_telemetry.items() if key != "digest"}
        )
        corruptions.append(bad_telemetry)

        inconsistent_record = copy.deepcopy(valid)
        inconsistent_record["last_record"]["desired_recurrent_gain"] += 0.1
        inconsistent_record["digest"] = source._digest_payload(
            {
                key: value
                for key, value in inconsistent_record.items()
                if key != "digest"
            }
        )
        corruptions.append(inconsistent_record)

        for corrupted in corruptions:
            with self.subTest(fields=tuple(corrupted)):
                target = AdaptiveFeedbackRegulator(0.8, 0.9)
                target.update(_telemetry(0.9))
                before = pickle.dumps(target, protocol=5)
                with self.assertRaises(ValueError):
                    target.load_snapshot(corrupted)
                self.assertEqual(pickle.dumps(target, protocol=5), before)


class AdaptiveFeedbackAgentTests(unittest.TestCase):
    @staticmethod
    def _observations(count: int = 8) -> np.ndarray:
        coordinates = np.arange(12, dtype=np.float64)
        return np.stack(
            [np.sin(0.23 * coordinates + 0.41 * lag) for lag in range(count)]
        )

    def test_default_fixed_mode_preserves_exact_trace(self) -> None:
        implicit = _agent(2401, feedback_mode="fixed")
        explicit = _agent(
            2401,
            feedback_mode="fixed",
            feedback_minimum_gain=0.0,
            feedback_maximum_gain=2.0,
            feedback_adaptation_rate=1.0,
            feedback_maximum_step=0.9,
            feedback_deadband=0.8,
        )
        for observation in self._observations():
            first = implicit.step(observation)
            second = explicit.step(observation)
            np.testing.assert_array_equal(first.feature_vector(), second.feature_vector())
            self.assertEqual(first.selected_specialists, second.selected_specialists)
        self.assertIsNone(implicit.feedback_snapshot()["regulator"])
        self.assertIsNone(explicit.feedback_snapshot()["regulator"])

    def test_adaptation_is_next_step_only_and_deterministic(self) -> None:
        adaptive = _agent(2402, feedback_mode="adaptive")
        manual = _agent(2402, feedback_mode="manual")
        first_observation, second_observation = self._observations(2)

        adaptive_first = adaptive.step(first_observation)
        manual_first = manual.step(first_observation)
        np.testing.assert_array_equal(
            adaptive_first.feature_vector(), manual_first.feature_vector()
        )
        first_record = adaptive.last_feedback_control
        self.assertIsNotNone(first_record)
        self.assertEqual(first_record.applied_recurrent_gain, adaptive.recurrent_gain)
        self.assertEqual(first_record.applied_closure_gain, adaptive.closure_gain)
        self.assertEqual(adaptive.current_recurrent_gain, first_record.next_recurrent_gain)
        self.assertEqual(adaptive.current_closure_gain, first_record.next_closure_gain)

        manual.set_active_feedback(
            adaptive.current_recurrent_gain,
            adaptive.current_closure_gain,
        )
        adaptive_second = adaptive.step(second_observation)
        manual_second = manual.step(second_observation)
        np.testing.assert_array_equal(
            adaptive_second.feature_vector(), manual_second.feature_vector()
        )
        self.assertEqual(adaptive_second.selected_specialists, manual_second.selected_specialists)

        first = _agent(2403)
        second = _agent(2403)
        for observation in self._observations():
            np.testing.assert_array_equal(
                first.step(observation).feature_vector(),
                second.step(observation).feature_vector(),
            )
            self.assertEqual(first.last_feedback_control, second.last_feedback_control)
        self.assertEqual(first.feedback_snapshot(), second.feedback_snapshot())

    def test_step_result_audits_dose_and_recurrence_ablation_freezes_control(self) -> None:
        adaptive = _agent(2410)
        result = adaptive.step(self._observations(1)[0])
        record = adaptive.last_feedback_control
        self.assertIsNotNone(record)
        self.assertEqual(result.applied_recurrent_gain, record.applied_recurrent_gain)
        self.assertEqual(result.applied_closure_gain, record.applied_closure_gain)
        self.assertEqual(result.next_recurrent_gain, record.next_recurrent_gain)
        self.assertEqual(result.next_closure_gain, record.next_closure_gain)
        self.assertEqual(result.feedback_telemetry, record.telemetry)
        np.testing.assert_array_equal(
            result.workspace_proposal_states.shape,
            (result.workspace_weights.size, adaptive.specialist_dim),
        )

        ablated = _agent(2411, ablations="recurrence")
        ablated_result = ablated.step(self._observations(1)[0])
        self.assertEqual(ablated_result.applied_recurrent_gain, 0.0)
        self.assertEqual(ablated_result.applied_closure_gain, 0.0)
        self.assertEqual(ablated_result.next_recurrent_gain, 0.0)
        self.assertEqual(ablated_result.next_closure_gain, 0.0)
        self.assertIsNone(ablated_result.feedback_telemetry)
        self.assertIsNone(ablated.last_feedback_control)
        self.assertEqual(ablated.feedback_regulator.update_count, 0)

    def test_outer_snapshot_is_strict_and_manual_change_invalidates_evidence(self) -> None:
        source = _agent(2412)
        source.step(self._observations(1)[0])
        valid = source.feedback_snapshot()
        target = _agent(2412)
        target.load_feedback_snapshot(valid)
        self.assertEqual(target.feedback_snapshot(), valid)

        corruptions = []
        string_gain = copy.deepcopy(valid)
        string_gain["current_recurrent_gain"] = str(
            string_gain["current_recurrent_gain"]
        )
        string_gain["digest"] = AdaptiveFeedbackRegulator._digest_payload(
            {key: value for key, value in string_gain.items() if key != "digest"}
        )
        corruptions.append(string_gain)
        integer_boolean = copy.deepcopy(valid)
        integer_boolean["adaptation_ablated"] = 0
        integer_boolean["digest"] = AdaptiveFeedbackRegulator._digest_payload(
            {key: value for key, value in integer_boolean.items() if key != "digest"}
        )
        corruptions.append(integer_boolean)
        for corrupted in corruptions:
            before = pickle.dumps(target, protocol=5)
            with self.assertRaises(ValueError):
                target.load_feedback_snapshot(corrupted)
            self.assertEqual(pickle.dumps(target, protocol=5), before)

        manual = _agent(2413, feedback_mode="manual")
        key_arguments = {
            "horizon": 2,
            "query_budget": 3,
            "candidate_magnitude": 0.2,
            "forecast_decay": 0.85,
            "forecast_mode": "learned",
            "max_delta_norm": 0.5,
        }
        old_key = manual._intention_base_configuration_key(**key_arguments)
        manual._append_intention_calibration_record(
            IntentionCalibrationRecord(
                sequence_id=0,
                calibration_key=old_key,
                plan_state_digest="test-state",
                planned_time=0,
                recorded_time=0,
                predicted_improvement=0.0,
                realized_improvement=0.0,
                optimism=0.0,
                selected_index=0,
                selected_delta_norm=0.0,
                horizon=2,
                forecast_mode="learned",
                outcome_source="shadow",
            )
        )
        manual.set_active_feedback(0.45, 0.55)
        self.assertEqual(manual.intention_calibration_snapshot()["count"], 0)
        self.assertEqual(
            manual.intention_calibration_snapshot()["last_reset_reason"],
            "manual_feedback_changed",
        )
        self.assertNotEqual(
            old_key,
            manual._intention_base_configuration_key(**key_arguments),
        )

    def test_reset_manual_mode_and_adaptation_ablation(self) -> None:
        adaptive = _agent(2404)
        for observation in self._observations(3):
            adaptive.step(observation)
        self.assertEqual(adaptive.feedback_regulator.update_count, 3)
        adaptive.reset()
        self.assertEqual(adaptive.time, 0)
        self.assertEqual(adaptive.feedback_regulator.update_count, 0)
        self.assertIsNone(adaptive.last_feedback_control)
        self.assertEqual(adaptive.current_recurrent_gain, adaptive.recurrent_gain)
        self.assertEqual(adaptive.current_closure_gain, adaptive.closure_gain)

        manual = _agent(2405, feedback_mode="manual")
        manual.set_active_feedback(0.45, 0.65)
        fixed = _agent(
            2405,
            feedback_mode="fixed",
            recurrent_gain=0.45,
            closure_gain=0.65,
        )
        observation = self._observations(1)[0]
        np.testing.assert_array_equal(
            manual.step(observation).feature_vector(),
            fixed.step(observation).feature_vector(),
        )
        self.assertEqual(manual.feedback_regulator.update_count, 0)
        self.assertIsNone(manual.last_feedback_control)
        with self.assertRaises(RuntimeError):
            fixed.set_active_feedback(0.5, 0.5)

        ablated = _agent(2406, ablations="feedback_adaptation")
        matched_fixed = _agent(2406, feedback_mode="fixed")
        for observation in self._observations(4):
            np.testing.assert_array_equal(
                ablated.step(observation).feature_vector(),
                matched_fixed.step(observation).feature_vector(),
            )
        self.assertEqual(ablated.feedback_regulator.update_count, 0)
        self.assertEqual(ablated.current_recurrent_gain, ablated.recurrent_gain)
        self.assertEqual(ablated.current_closure_gain, ablated.closure_gain)

    def test_counterfactual_queries_and_planning_do_not_mutate_adaptation(self) -> None:
        agent = _agent(2407)
        observations = self._observations(7)
        for observation in observations[:5]:
            agent.step(observation)
        future = observations[5:]
        delta = np.zeros(agent.self_dim, dtype=np.float64)
        delta[0] = 0.2
        before = pickle.dumps(agent, protocol=5)

        agent.counterfactual_self_query(delta, future)
        self.assertEqual(pickle.dumps(agent, protocol=5), before)
        agent.plan_endogenous_self_intention(
            horizon=2,
            query_budget=3,
            candidate_magnitude=0.2,
            selection_mode="rollout",
        )
        self.assertEqual(pickle.dumps(agent, protocol=5), before)

    def test_adaptive_local_jacobian_is_rejected(self) -> None:
        agent = RRCTAgent(
            4,
            n_levels=2,
            projector_ranks=(2, 4),
            n_specialists=2,
            specialist_dim=4,
            workspace_dim=4,
            self_dim=3,
            seed=2408,
            feedback_mode="adaptive",
        )
        with self.assertRaisesRegex(
            ValueError,
            "do not yet include adaptive feedback state",
        ):
            local_transition_jacobian(agent, np.zeros(4))


if __name__ == "__main__":
    unittest.main()

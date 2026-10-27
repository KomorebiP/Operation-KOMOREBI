import copy
import pickle
import unittest

import numpy as np

from rrct import IntentionCalibrationRecord, RRCTAgent


class IntentionCalibrationTests(unittest.TestCase):
    @staticmethod
    def _agent(seed: int = 2003) -> RRCTAgent:
        agent = RRCTAgent(
            12,
            projector_ranks=(3, 6, 9, 12),
            seed=seed,
            self_model_mode="frozen",
        )
        coordinates = np.arange(12, dtype=np.float64)
        for lag in range(7):
            agent.step(
                np.sin(coordinates * 0.31 + lag * 0.47),
                source="v08_calibration_prime",
            )
        return agent

    @staticmethod
    def _append_history(
        agent: RRCTAgent,
        *,
        optimism: float,
        count: int = 19,
    ) -> None:
        plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            calibration_mode="off",
        )
        for sequence_id in range(count):
            record = IntentionCalibrationRecord(
                sequence_id=sequence_id,
                calibration_key=plan.calibration_key,
                plan_state_digest=f"fixture-{sequence_id}",
                planned_time=sequence_id,
                recorded_time=sequence_id + 4,
                predicted_improvement=float(optimism),
                realized_improvement=0.0,
                optimism=float(optimism),
                selected_index=plan.raw_selected_index,
                selected_delta_norm=0.35,
                horizon=4,
                forecast_mode="learned",
                outcome_source="shadow",
            )
            agent._append_intention_calibration_record(record)

    def test_finite_sample_rank_and_nonnegative_threshold(self) -> None:
        ready, threshold = RRCTAgent._conformal_optimism_threshold(
            tuple(range(18)), alpha=0.05, minimum_records=1
        )
        self.assertFalse(ready)
        self.assertIsNone(threshold)
        ready, threshold = RRCTAgent._conformal_optimism_threshold(
            tuple(range(19)), alpha=0.05, minimum_records=1
        )
        self.assertTrue(ready)
        self.assertEqual(threshold, 18.0)
        ready, threshold = RRCTAgent._conformal_optimism_threshold(
            (-0.4,) * 19, alpha=0.05, minimum_records=19
        )
        self.assertTrue(ready)
        self.assertEqual(threshold, 0.0)

    def test_cold_start_abstains_and_abstention_teaches_nothing(self) -> None:
        agent = self._agent()
        plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            calibration_mode="conservative",
        )
        self.assertNotEqual(plan.raw_selected_index, 0)
        self.assertEqual(plan.selected_index, 0)
        self.assertTrue(plan.abstained)
        self.assertFalse(plan.calibration_ready)
        self.assertEqual(plan.abstention_reason, "calibration_not_ready")
        self.assertGreater(plan.raw_predicted_improvement, 0.0)
        self.assertEqual(plan.predicted_improvement, 0.0)
        receipt = agent.commit_endogenous_self_intention(plan)
        agent.evaluate_committed_intention(receipt, np.zeros((4, 12)))
        self.assertEqual(agent.intention_calibration_snapshot()["count"], 0)

    def test_threshold_equality_abstains_and_one_ulp_below_permits(self) -> None:
        equality_agent = self._agent(seed=2004)
        raw = equality_agent.plan_endogenous_self_intention(
            horizon=4, query_budget=4
        ).raw_predicted_improvement
        self._append_history(equality_agent, optimism=raw)
        equal_plan = equality_agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            calibration_mode="conservative",
        )
        self.assertEqual(equal_plan.raw_predicted_improvement, raw)
        self.assertEqual(equal_plan.uncertainty_threshold, raw)
        self.assertTrue(equal_plan.abstained)

        permitted = self._agent(seed=2004)
        self._append_history(
            permitted,
            optimism=float(np.nextafter(raw, -np.inf)),
        )
        permit_plan = permitted.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            calibration_mode="conservative",
        )
        self.assertFalse(permit_plan.abstained)
        self.assertEqual(permit_plan.selected_index, permit_plan.raw_selected_index)

    def test_live_exploration_adds_one_record_but_off_mode_does_not(self) -> None:
        future = np.ones((4, 12), dtype=np.float64) * 0.1
        off = self._agent(seed=2005)
        plan = off.plan_endogenous_self_intention(
            horizon=4, query_budget=4, calibration_mode="off"
        )
        receipt = off.commit_endogenous_self_intention(plan)
        off.evaluate_committed_intention(receipt, future)
        self.assertEqual(off.intention_calibration_snapshot()["count"], 0)

        explore = self._agent(seed=2005)
        plan = explore.plan_endogenous_self_intention(
            horizon=4, query_budget=4, calibration_mode="explore"
        )
        self.assertNotEqual(plan.selected_index, 0)
        receipt = explore.commit_endogenous_self_intention(plan)
        explore.evaluate_committed_intention(receipt, future)
        snapshot = explore.intention_calibration_snapshot()
        self.assertEqual(snapshot["count"], 1)
        self.assertEqual(snapshot["records"][0]["outcome_source"], "live")

    def test_shadow_calibration_is_labeled_and_leaves_core_state_unchanged(self) -> None:
        agent = self._agent(seed=2006)
        plan = agent.plan_endogenous_self_intention(
            horizon=4, query_budget=4, calibration_mode="explore"
        )
        before = agent.snapshot()
        record = agent.record_shadow_intention_calibration(
            plan, np.ones((4, 12), dtype=np.float64) * -0.15
        )
        after = agent.snapshot()
        self.assertEqual(record.outcome_source, "shadow")
        self.assertEqual(after["intention_calibration_count"], 1)
        for field in (
            "time",
            "resolution_level",
            "observation_forecaster_observed_count",
        ):
            self.assertEqual(before[field], after[field])
        for field in (
            "workspace",
            "self_state",
            "last_action",
            "observation_forecaster_last_observation",
        ):
            np.testing.assert_array_equal(before[field], after[field])

    def test_snapshot_round_trip_reset_semantics_and_corruption_rejection(self) -> None:
        source = self._agent(seed=2007)
        self._append_history(source, optimism=0.001)
        snapshot = source.intention_calibration_snapshot()
        source.reset()
        self.assertEqual(source.intention_calibration_snapshot(), snapshot)

        target = self._agent(seed=2007)
        target.load_intention_calibration_snapshot(snapshot)
        self.assertEqual(target.intention_calibration_snapshot(), snapshot)
        before = pickle.dumps(target, protocol=5)
        corrupted = copy.deepcopy(snapshot)
        corrupted["records"][0]["optimism"] += 0.1
        with self.assertRaises(ValueError):
            target.load_intention_calibration_snapshot(corrupted)
        self.assertEqual(pickle.dumps(target, protocol=5), before)

        receipt = target.reset_intention_calibration(reason="test invalidation")
        self.assertEqual(receipt["old_count"], 19)
        self.assertEqual(receipt["new_count"], 0)
        self.assertNotEqual(receipt["old_digest"], receipt["new_digest"])
        with self.assertRaises(ValueError):
            target.reset_intention_calibration(reason="")

    def test_calibration_update_stales_prior_plan_and_requires_exact_future(self) -> None:
        agent = self._agent(seed=2008)
        stale_plan = agent.plan_endogenous_self_intention(
            horizon=4, query_budget=4, calibration_mode="explore"
        )
        agent.record_shadow_intention_calibration(
            stale_plan, np.zeros((4, 12), dtype=np.float64)
        )
        with self.assertRaises(RuntimeError):
            agent.commit_endogenous_self_intention(stale_plan)

        fresh = self._agent(seed=2008)
        plan = fresh.plan_endogenous_self_intention(
            horizon=4, query_budget=4, calibration_mode="explore"
        )
        receipt = fresh.commit_endogenous_self_intention(plan)
        committed = pickle.dumps(fresh, protocol=5)
        with self.assertRaises(ValueError):
            fresh.evaluate_committed_intention(receipt, np.zeros((3, 12)))
        self.assertEqual(pickle.dumps(fresh, protocol=5), committed)

    def test_calibration_cannot_use_an_internal_forecast_as_revealed_outcome(self) -> None:
        agent = self._agent(seed=2009)
        before = pickle.dumps(agent, protocol=5)
        with self.assertRaises(ValueError):
            agent.execute_endogenous_self_intention(calibration_mode="explore")
        self.assertEqual(pickle.dumps(agent, protocol=5), before)


if __name__ == "__main__":
    unittest.main()

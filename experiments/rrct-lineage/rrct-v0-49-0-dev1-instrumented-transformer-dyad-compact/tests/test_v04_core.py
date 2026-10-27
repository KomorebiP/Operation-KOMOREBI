import copy
from dataclasses import replace
import unittest
from unittest.mock import patch

import numpy as np

from rrct import (
    DirectedWidestPathCutCertificate,
    HybridBranchSignature,
    LocalTransitionComputationError,
    LocalTransitionDiagnostics,
    RRCTAgent,
    continuous_state_vector,
    local_transition_jacobian,
    set_continuous_state_vector,
    widest_path_closure_details,
    widest_path_cut_certificate,
)
from rrct.dynamics import _hybrid_branch_signature


class PathSpecificGainTests(unittest.TestCase):
    def test_default_multipliers_preserve_exact_seeded_trace(self) -> None:
        implicit = RRCTAgent(6, seed=801, closure_gain=0.7)
        explicit = RRCTAgent(
            6,
            seed=801,
            closure_gain=0.7,
            self_feedback_gain=1.0,
            action_feedback_gain=1.0,
        )
        observations = np.random.default_rng(802).normal(size=(8, 6))
        for observation in observations:
            first = implicit.step(observation)
            second = explicit.step(observation)
            np.testing.assert_array_equal(first.feature_vector(), second.feature_vector())
            self.assertEqual(first.selected_specialists, second.selected_specialists)

    def test_each_feedback_path_has_an_independent_exact_zero(self) -> None:
        template = RRCTAgent(6, seed=803)
        template.step(np.linspace(-1.0, 1.0, 6))
        template.self_model.state = np.linspace(0.1, 0.8, template.self_dim)
        template._last_action = np.linspace(-0.4, 0.6, template.action_dim)
        observation = np.zeros(6)

        self_zero_a = copy.deepcopy(template)
        self_zero_b = copy.deepcopy(template)
        self_zero_a.set_path_gains(0.0, 1.0, reset=False)
        self_zero_b.set_path_gains(0.0, 1.0, reset=False)
        self_zero_b.self_model.state += 3.0
        np.testing.assert_array_equal(
            self_zero_a.step(observation).workspace,
            self_zero_b.step(observation).workspace,
        )

        action_zero_a = copy.deepcopy(template)
        action_zero_b = copy.deepcopy(template)
        action_zero_a.set_path_gains(1.0, 0.0, reset=False)
        action_zero_b.set_path_gains(1.0, 0.0, reset=False)
        action_zero_b._last_action += 3.0
        np.testing.assert_array_equal(
            action_zero_a.step(observation).workspace,
            action_zero_b.step(observation).workspace,
        )

    def test_effective_path_gains_and_snapshot_are_auditable(self) -> None:
        agent = RRCTAgent(
            6,
            closure_gain=0.4,
            self_feedback_gain=0.5,
            action_feedback_gain=1.5,
        )
        self.assertAlmostEqual(agent.effective_self_feedback_gain, 0.2)
        self.assertAlmostEqual(agent.effective_action_feedback_gain, 0.6)
        snapshot = agent.snapshot()
        self.assertEqual(snapshot["self_feedback_gain"], 0.5)
        self.assertEqual(snapshot["effective_self_feedback_gain"], 0.2)
        self.assertEqual(snapshot["action_feedback_gain"], 1.5)
        self.assertAlmostEqual(snapshot["effective_action_feedback_gain"], 0.6)

        ablated = RRCTAgent(
            6,
            closure_gain=4.0,
            self_feedback_gain=3.0,
            action_feedback_gain=2.0,
            ablations="recurrence",
        )
        self.assertEqual(ablated.effective_self_feedback_gain, 0.0)
        self.assertEqual(ablated.effective_action_feedback_gain, 0.0)

    def test_path_gain_updates_are_atomic_and_obey_reset_flag(self) -> None:
        agent = RRCTAgent(
            6, seed=804, self_feedback_gain=0.4, action_feedback_gain=0.6
        )
        agent.step(np.ones(6))
        before = agent.snapshot()
        for values in ((-1.0, 1.0), (1.0, np.inf), (np.nan, 1.0)):
            with self.assertRaises(ValueError):
                agent.set_path_gains(*values)
            self.assertEqual(agent.self_feedback_gain, 0.4)
            self.assertEqual(agent.action_feedback_gain, 0.6)

        agent.set_path_gains(0.2, 1.4, reset=False)
        self.assertEqual(agent.time, before["time"])
        np.testing.assert_array_equal(agent.workspace.state, before["workspace"])
        agent.set_path_gains(0.3, 0.8)
        self.assertEqual(agent.time, 0)
        np.testing.assert_array_equal(agent.workspace.state, np.zeros(16))

    def test_constructor_rejects_invalid_path_gains(self) -> None:
        for keyword in ("self_feedback_gain", "action_feedback_gain"):
            for value in (-0.1, np.inf, np.nan):
                with self.assertRaises(ValueError):
                    RRCTAgent(6, **{keyword: value})


class DirectedCutCertificateTests(unittest.TestCase):
    def test_known_graph_returns_complete_forward_cut(self) -> None:
        effects = np.asarray(
            [
                [0.0, 0.8, 0.1],
                [0.2, 0.0, 0.6],
                [0.4, 0.3, 0.0],
            ]
        )
        certificate = widest_path_cut_certificate(effects)
        self.assertIsInstance(certificate, DirectedWidestPathCutCertificate)
        self.assertEqual(certificate.weakest_pair, (1, 0))
        self.assertEqual(certificate.raw_capacity, 0.4)
        self.assertEqual(certificate.reachable_set, (1, 2))
        self.assertEqual(
            certificate.cut_edges,
            ((1, 0, 0.2), (2, 0, 0.4)),
        )
        with self.assertRaises(AttributeError):
            certificate.source = 0

    def test_zero_disconnection_and_ties_are_deterministic(self) -> None:
        disconnected = np.asarray(
            [[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        )
        first = widest_path_cut_certificate(disconnected)
        self.assertEqual(first.raw_capacity, 0.0)
        self.assertEqual(first.weakest_pair, (0, 2))
        self.assertEqual(first.reachable_set, (0, 1))
        self.assertTrue(all(weight == 0.0 for _, _, weight in first.cut_edges))

        tied_cycle = np.asarray(
            [[0.0, 0.5, 0.0], [0.0, 0.0, 0.5], [0.5, 0.0, 0.0]]
        )
        second = widest_path_cut_certificate(tied_cycle)
        self.assertEqual(second.weakest_pair, (0, 1))
        self.assertEqual(second.raw_capacity, 0.5)
        self.assertEqual(second.reachable_set, (0,))

    def test_random_small_graphs_satisfy_certificate_theorem(self) -> None:
        rng = np.random.default_rng(805)
        for node_count in range(2, 8):
            for _ in range(5):
                effects = rng.integers(0, 5, size=(node_count, node_count)).astype(
                    np.float64
                )
                np.fill_diagonal(effects, 0.0)
                details = widest_path_closure_details(effects)
                certificate = widest_path_cut_certificate(effects)
                self.assertEqual(certificate.raw_capacity, details.raw_strength)
                self.assertEqual(certificate.weakest_pair, details.weakest_pair)
                self.assertNotIn(certificate.target, certificate.reachable_set)
                reachable = set(certificate.reachable_set)
                expected_pairs = {
                    (source, target)
                    for source in reachable
                    for target in range(node_count)
                    if target not in reachable
                }
                self.assertEqual(
                    {(source, target) for source, target, _ in certificate.cut_edges},
                    expected_pairs,
                )
                self.assertTrue(
                    all(
                        weight <= certificate.raw_capacity
                        for _, _, weight in certificate.cut_edges
                    )
                )

    def test_invalid_effects_are_rejected_through_details_api(self) -> None:
        for effects in (
            np.zeros((2, 3)),
            np.asarray([[0.0, -1.0], [0.0, 0.0]]),
            np.asarray([[0.0, np.nan], [0.0, 0.0]]),
        ):
            with self.assertRaises(ValueError):
                widest_path_cut_certificate(effects)


class LocalDynamicsTests(unittest.TestCase):
    @staticmethod
    def _small_agent() -> RRCTAgent:
        return RRCTAgent(
            4,
            seed=806,
            action_dim=1,
            n_specialists=2,
            specialist_dim=3,
            workspace_dim=3,
            self_dim=2,
            memory_capacity=4,
        )

    def test_continuous_state_round_trip_and_validation(self) -> None:
        agent = self._small_agent()
        vector = np.linspace(-0.3, 0.4, 12)
        set_continuous_state_vector(agent, vector)
        np.testing.assert_array_equal(continuous_state_vector(agent), vector)
        vector[0] = 99.0
        self.assertNotEqual(continuous_state_vector(agent)[0], 99.0)
        for invalid in (np.zeros(11), np.full(12, np.nan), np.zeros((12, 1))):
            with self.assertRaises(ValueError):
                set_continuous_state_vector(agent, invalid)

    def test_branch_signature_detects_action_candidate_index_flip(self) -> None:
        result = self._small_agent().step(np.asarray([0.2, -0.1, 0.4, -0.3]))
        first_scores = np.full(result.action_scores.shape, -1.0)
        second_scores = np.full(result.action_scores.shape, -1.0)
        first_scores[1] = 0.0
        second_scores[2] = 0.0
        first = replace(result, action_scores=first_scores)
        second = replace(result, action_scores=second_scores)

        first_signature = _hybrid_branch_signature(first)
        second_signature = _hybrid_branch_signature(second)
        self.assertIsInstance(first_signature, HybridBranchSignature)
        self.assertEqual(
            first_signature.selected_specialists,
            second_signature.selected_specialists,
        )
        self.assertEqual(
            first_signature.next_resolution_level,
            second_signature.next_resolution_level,
        )
        self.assertEqual(first_signature.memory_indices, second_signature.memory_indices)
        self.assertEqual(first_signature.memory_written, second_signature.memory_written)
        self.assertEqual(first_signature.action_candidate_index, 1)
        self.assertEqual(second_signature.action_candidate_index, 2)
        self.assertNotEqual(first_signature, second_signature)

        tied_scores = np.full(result.action_scores.shape, -1.0)
        tied_scores[:2] = 1.0
        tied = replace(result, action_scores=tied_scores)
        self.assertEqual(
            _hybrid_branch_signature(tied).action_candidate_index, 0
        )

        with self.assertRaises(AttributeError):
            first_signature.action_candidate_index = 0

    def test_hybrid_branch_signature_validates_public_fields(self) -> None:
        valid = HybridBranchSignature(
            selected_specialists=("specialist_00",),
            action_candidate_index=2,
            next_resolution_level=1,
            memory_indices=(3, 1),
            memory_written=np.bool_(True),
        )
        self.assertEqual(valid.memory_indices, (3, 1))
        self.assertIs(valid.memory_written, True)

        invalid_options = (
            {"selected_specialists": ("specialist_00", "specialist_00")},
            {"action_candidate_index": 1.0},
            {"next_resolution_level": -1},
            {"memory_indices": (1, 1)},
            {"memory_written": 1},
        )
        base = {
            "selected_specialists": (),
            "action_candidate_index": 0,
            "next_resolution_level": 0,
            "memory_indices": (),
            "memory_written": False,
        }
        for options in invalid_options:
            with self.assertRaises((TypeError, ValueError)):
                HybridBranchSignature(**(base | options))

    def test_centered_jacobian_is_deterministic_immutable_and_nonmutating(self) -> None:
        agent = self._small_agent()
        agent.step(np.linspace(-0.5, 0.5, 4))
        state_before = continuous_state_vector(agent)
        snapshot_before = agent.snapshot()
        observation = np.asarray([0.2, -0.1, 0.4, -0.3])
        first = local_transition_jacobian(agent, observation, epsilon=2e-6)
        second = local_transition_jacobian(agent, observation, epsilon=2e-6)

        self.assertIsInstance(first, LocalTransitionDiagnostics)
        self.assertEqual(first.state_dimension, 12)
        np.testing.assert_array_equal(first.jacobian, second.jacobian)
        self.assertEqual(first.spectral_radius, second.spectral_radius)
        self.assertEqual(
            first.largest_singular_value, second.largest_singular_value
        )
        self.assertGreaterEqual(first.branch_switch_fraction, 0.0)
        self.assertLessEqual(first.branch_switch_fraction, 1.0)
        self.assertEqual(
            first.branch_switch_count, len(first.branch_switch_coordinates)
        )
        self.assertEqual(
            first.branch_switch_fraction,
            first.branch_switch_count / first.state_dimension,
        )
        self.assertEqual(len(first.positive_branch_signatures), 12)
        self.assertEqual(len(first.negative_branch_signatures), 12)
        self.assertEqual(
            first.positive_branch_signatures,
            second.positive_branch_signatures,
        )
        self.assertEqual(
            first.negative_branch_signatures,
            second.negative_branch_signatures,
        )
        self.assertTrue(
            all(
                isinstance(signature, HybridBranchSignature)
                for signature in first.positive_branch_signatures
                + first.negative_branch_signatures
            )
        )
        with self.assertRaises(AttributeError):
            first.positive_branch_signatures[0].memory_written = False
        self.assertFalse(first.jacobian.flags.writeable)
        with self.assertRaises(ValueError):
            first.jacobian.setflags(write=True)
        np.testing.assert_array_equal(continuous_state_vector(agent), state_before)
        self.assertEqual(agent.time, snapshot_before["time"])
        self.assertEqual(agent.resolution_level, snapshot_before["resolution_level"])

        expected_radius = float(np.max(np.abs(np.linalg.eigvals(first.jacobian))))
        expected_gain = float(np.linalg.svd(first.jacobian, compute_uv=False)[0])
        self.assertAlmostEqual(first.spectral_radius, expected_radius)
        self.assertAlmostEqual(first.largest_singular_value, expected_gain)

        with self.assertRaises(ValueError):
            replace(
                first,
                positive_branch_signatures=first.positive_branch_signatures[:-1],
            )
        tampered_positive = list(first.positive_branch_signatures)
        if tampered_positive[0] == first.negative_branch_signatures[0]:
            signature = tampered_positive[0]
            tampered_positive[0] = replace(
                signature,
                action_candidate_index=signature.action_candidate_index + 100,
            )
        else:
            tampered_positive[0] = first.negative_branch_signatures[0]
        with self.assertRaises(ValueError):
            replace(first, positive_branch_signatures=tuple(tampered_positive))

    def test_one_jacobian_column_matches_manual_centered_difference(self) -> None:
        agent = self._small_agent()
        observation = np.asarray([0.1, 0.2, -0.3, 0.4])
        epsilon = 1e-5
        diagnostic = local_transition_jacobian(agent, observation, epsilon=epsilon)
        base = continuous_state_vector(agent)
        positive = copy.deepcopy(agent)
        negative = copy.deepcopy(agent)
        positive_state = base.copy()
        negative_state = base.copy()
        positive_state[3] += epsilon
        negative_state[3] -= epsilon
        set_continuous_state_vector(positive, positive_state)
        set_continuous_state_vector(negative, negative_state)
        positive.step(observation)
        negative.step(observation)
        expected = (
            continuous_state_vector(positive) - continuous_state_vector(negative)
        ) / (2.0 * epsilon)
        np.testing.assert_array_equal(diagnostic.jacobian[:, 3], expected)

    def test_diagnostic_refuses_training_and_invalid_inputs(self) -> None:
        training = self._small_agent()
        training.train_self_model()
        with self.assertRaises(ValueError):
            local_transition_jacobian(training, np.zeros(4))

        frozen = self._small_agent()
        for epsilon in (0.0, -1.0, np.inf, np.nan):
            with self.assertRaises(ValueError):
                local_transition_jacobian(frozen, np.zeros(4), epsilon=epsilon)
        for observation in (np.zeros(3), np.full(4, np.nan)):
            with self.assertRaises(ValueError):
                local_transition_jacobian(frozen, observation)

    def test_step_failure_retains_partial_matrix_and_branch_records(self) -> None:
        agent = self._small_agent()
        original_step = RRCTAgent.step
        call_count = 0

        def fail_after_two_columns(
            step_agent: RRCTAgent,
            observation: np.ndarray,
            **options: object,
        ) -> object:
            nonlocal call_count
            if call_count == 4:
                raise RuntimeError("forced coordinate failure")
            call_count += 1
            return original_step(step_agent, observation, **options)

        with patch.object(RRCTAgent, "step", new=fail_after_two_columns):
            with self.assertRaises(LocalTransitionComputationError) as caught:
                local_transition_jacobian(agent, np.zeros(4))

        error = caught.exception
        self.assertEqual(error.stage, "finite_difference")
        self.assertIn("column 2", error.reason)
        self.assertIn("forced coordinate failure", error.reason)
        self.assertEqual(error.completed_columns, 2)
        self.assertEqual(error.state_dimension, 12)
        self.assertEqual(error.epsilon, 1e-5)
        self.assertEqual(len(error.positive_branch_signatures), 2)
        self.assertEqual(len(error.negative_branch_signatures), 2)
        self.assertTrue(np.all(np.isfinite(error.jacobian[:, :2])))
        self.assertTrue(np.all(np.isnan(error.jacobian[:, 2:])))
        self.assertFalse(error.jacobian.flags.writeable)
        with self.assertRaises(ValueError):
            error.jacobian.setflags(write=True)
        with self.assertRaises(AttributeError):
            error.completed_columns = 0

    def test_linear_algebra_failures_retain_complete_raw_matrix(self) -> None:
        observation = np.asarray([0.1, -0.2, 0.3, -0.4])
        for function_name, expected_stage in (("eigvals", "eigvals"), ("svd", "svd")):
            agent = self._small_agent()
            failure = np.linalg.LinAlgError(f"forced {function_name} failure")
            with patch.object(np.linalg, function_name, side_effect=failure):
                with self.assertRaises(LocalTransitionComputationError) as caught:
                    local_transition_jacobian(agent, observation)
            error = caught.exception
            self.assertEqual(error.stage, expected_stage)
            self.assertEqual(error.completed_columns, error.state_dimension)
            self.assertEqual(error.jacobian.shape, (12, 12))
            self.assertTrue(np.all(np.isfinite(error.jacobian)))
            self.assertEqual(len(error.positive_branch_signatures), 12)
            self.assertEqual(len(error.negative_branch_signatures), 12)

    def test_complete_nonfinite_error_can_retain_all_columns(self) -> None:
        signature = HybridBranchSignature(
            selected_specialists=(),
            action_candidate_index=0,
            next_resolution_level=0,
            memory_indices=(),
            memory_written=False,
        )
        error = LocalTransitionComputationError(
            jacobian=np.full((2, 2), np.nan),
            completed_columns=2,
            epsilon=1e-5,
            state_dimension=2,
            positive_branch_signatures=(signature, signature),
            negative_branch_signatures=(signature, signature),
            stage="nonfinite_jacobian",
            reason="forced retained nonfinite matrix",
        )
        self.assertEqual(error.completed_columns, 2)
        self.assertTrue(np.all(np.isnan(error.jacobian)))


if __name__ == "__main__":
    unittest.main()

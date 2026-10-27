"""Unit tests for agent-independent RRCT diagnostics."""

from __future__ import annotations

import unittest

import numpy as np

from rrct.metrics import (
    DiagnosticProfile,
    brier_score,
    broadcast_reach,
    causal_adjacency,
    conjunctive_signature,
    effective_rank,
    episodic_binding_accuracy,
    is_strongly_connected,
    metacognitive_calibration,
    nested_projector_residual,
    projector_consistency,
    self_location_prediction_score,
    temporal_persistence_auc,
)


class ReachAndPersistenceTests(unittest.TestCase):
    def test_broadcast_reach_from_changes_and_paired_callable(self) -> None:
        changes = np.array([0.4, 0.0, 0.8, 0.05])
        self.assertAlmostEqual(broadcast_reach(changes, threshold=0.1), 0.5)

        baseline = np.zeros((3, 4))
        intervened = baseline.copy()
        intervened[:, (0, 2)] = 1.0
        score = broadcast_reach(
            lambda _: baseline,
            lambda _: intervened,
            threshold=0.5,
            inputs="unused",
        )
        self.assertAlmostEqual(score, 0.5)

    def test_broadcast_reach_boolean_and_weighted(self) -> None:
        changes = np.array([[False, True, False], [True, False, False]])
        self.assertAlmostEqual(broadcast_reach(changes), 2.0 / 3.0)
        self.assertAlmostEqual(
            broadcast_reach(changes, weights=[1.0, 1.0, 4.0]), 1.0 / 3.0
        )

    def test_temporal_persistence_is_normalized_auc(self) -> None:
        curve = np.array([1.0, 0.5, 0.0])
        self.assertAlmostEqual(temporal_persistence_auc(curve), 0.5)
        self.assertAlmostEqual(
            temporal_persistence_auc(curve, times=[0.0, 2.0, 4.0]), 0.5
        )

    def test_temporal_persistence_from_paired_traces(self) -> None:
        baseline = np.zeros((3, 2))
        intervention = np.array([[1.0, 1.0], [0.5, 0.5], [0.0, 0.0]])
        self.assertAlmostEqual(
            temporal_persistence_auc(baseline, intervention), 0.5
        )


class RepresentationMetricTests(unittest.TestCase):
    def test_effective_rank_of_flat_and_isotropic_spectra(self) -> None:
        self.assertAlmostEqual(
            effective_rank([1.0, 1.0, 1.0, 1.0], spectrum=True), 1.0
        )
        self.assertAlmostEqual(
            effective_rank([4.0, 0.0, 0.0, 0.0], spectrum=True), 0.25
        )
        self.assertAlmostEqual(
            effective_rank([4.0, 0.0, 0.0, 0.0], spectrum=True, normalized=False),
            1.0,
        )

    def test_effective_rank_accepts_callable_samples(self) -> None:
        samples = np.eye(4)
        self.assertAlmostEqual(
            effective_rank(lambda: samples, center=False), 1.0, places=12
        )

    def test_brier_calibration_transform(self) -> None:
        confidence = np.array([0.9, 0.2, 0.8, 0.1])
        outcomes = np.array([1, 0, 1, 0])
        expected_brier = (0.01 + 0.04 + 0.04 + 0.01) / 4.0
        self.assertAlmostEqual(brier_score(confidence, outcomes), expected_brier)
        self.assertAlmostEqual(
            metacognitive_calibration(confidence, outcomes), 1.0 - expected_brier
        )

    def test_self_location_categorical_and_continuous(self) -> None:
        probabilities = np.array([[0.1, 0.9], [0.8, 0.2], [0.7, 0.3]])
        labels = np.array([1, 0, 1])
        self.assertAlmostEqual(
            self_location_prediction_score(probabilities, labels), 2.0 / 3.0
        )
        actual = np.array([-1.0, 1.0])
        self.assertAlmostEqual(
            self_location_prediction_score(actual, actual, mode="continuous"), 1.0
        )
        self.assertAlmostEqual(
            self_location_prediction_score(
                np.array([0.0, 2.0]), actual, mode="continuous", scale=1.0
            ),
            1.0 / (1.0 + 1.0),
        )

    def test_episodic_binding_requires_complete_tuple(self) -> None:
        actual = np.array([[1, -1, 1], [-1, -1, 1], [1, 1, -1]])
        predicted = actual.copy()
        predicted[1, 2] = -1
        self.assertAlmostEqual(
            episodic_binding_accuracy(predicted, actual), 2.0 / 3.0
        )


class ProjectorAndCausalityTests(unittest.TestCase):
    def test_exact_nested_projectors_have_zero_residual(self) -> None:
        coarse = np.diag([1.0, 0.0, 0.0])
        fine = np.diag([1.0, 1.0, 0.0])
        identity = np.eye(3)
        residual = nested_projector_residual([coarse, fine, identity])
        self.assertAlmostEqual(residual, 0.0)
        self.assertAlmostEqual(projector_consistency(residual), 1.0)

    def test_callable_projector_is_supported_with_probes(self) -> None:
        coarse = lambda x: np.asarray(x) * np.array([1.0, 0.0])
        fine = lambda x: np.asarray(x)
        probes = np.array([[1.0, 2.0], [-2.0, 3.0]])
        self.assertAlmostEqual(
            nested_projector_residual([coarse, fine], probes=probes), 0.0
        )

    def test_causal_adjacency_and_closure(self) -> None:
        baseline = np.zeros((4, 3))
        interventions = np.zeros((3, 4, 3))
        interventions[0, :, 1] = 1.0
        interventions[1, :, 2] = 1.0
        interventions[2, :, 0] = 1.0
        adjacency, effects = causal_adjacency(
            baseline,
            interventions,
            threshold=0.5,
            include_self=False,
            return_effects=True,
        )
        expected = np.array(
            [[False, True, False], [False, False, True], [True, False, False]]
        )
        np.testing.assert_array_equal(adjacency, expected)
        self.assertAlmostEqual(effects[0, 1], 1.0)
        self.assertTrue(is_strongly_connected(adjacency))
        expected[2, 0] = False
        self.assertFalse(is_strongly_connected(expected))

    def test_partial_interventions_map_to_source_rows(self) -> None:
        baseline = np.zeros((2, 3))
        interventions = np.zeros((1, 2, 3))
        interventions[0, :, 0] = 2.0
        adjacency = causal_adjacency(
            baseline, interventions, source_nodes=[2], threshold=1.0
        )
        self.assertTrue(adjacency[2, 0])
        self.assertEqual(int(np.sum(adjacency)), 1)


class SignatureTests(unittest.TestCase):
    def test_conjunctive_signature_uses_weakest_component(self) -> None:
        profile = DiagnosticProfile(
            broadcast_reach=0.8,
            temporal_persistence=0.7,
            differentiation=0.9,
            metacognitive_calibration=0.75,
            self_location=0.4,
            episodic_binding=0.8,
            projector_consistency=1.0,
            strongly_connected=True,
        )
        result = conjunctive_signature(profile, thresholds=0.5)
        self.assertAlmostEqual(result.omega, 0.8)
        self.assertEqual(result.bottleneck, "self_location")
        self.assertFalse(result.passes)
        self.assertEqual(result.as_dict()["profile"]["strongly_connected"], True)

    def test_causal_gate_forces_signature_to_zero(self) -> None:
        profile = DiagnosticProfile(
            broadcast_reach=1.0,
            temporal_persistence=1.0,
            differentiation=1.0,
            metacognitive_calibration=1.0,
            self_location=1.0,
            episodic_binding=1.0,
            projector_consistency=1.0,
            strongly_connected=False,
        )
        result = conjunctive_signature(profile, 0.5)
        self.assertEqual(result.omega, 0.0)
        self.assertEqual(result.bottleneck, "causal_closure")
        self.assertFalse(result.passes)

    def test_invalid_profile_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DiagnosticProfile(1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, True)


if __name__ == "__main__":
    unittest.main()

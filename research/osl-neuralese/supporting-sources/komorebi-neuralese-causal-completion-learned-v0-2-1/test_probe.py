from __future__ import annotations

import json
import os
import pickle
import unittest
from pathlib import Path

import numpy as np

from checkpoint_io import load_checkpoint, restricted_loads_for_test
from core import (
    D4_RELATIONS,
    D4_REPRESENTATIVE_WORDS,
    canonical_maps,
    compose_maps,
    d4_cayley_reduction,
    encode_tables,
    future_equivalence_curve,
    normalize_rows,
    positive_ray_angle,
    projective_word_tangent,
    run_batch,
    sample_batch,
    slots_for_word,
    tangent_basis,
    tangent_observability_tower,
)


ROOT = Path(__file__).resolve().parent


class CheckpointTests(unittest.TestCase):
    def test_restricted_loader_reads_expected_weights(self) -> None:
        prereg = json.loads((ROOT / "PREREGISTRATION.json").read_text(encoding="utf-8"))
        name = "projective_terminal_seed0.pt"
        checkpoint = load_checkpoint(ROOT / "checkpoints" / name, prereg["checkpoints"][name])
        self.assertEqual(checkpoint.weights.state_embedding.shape, (8, 8))
        self.assertEqual(checkpoint.weights.operator_encoder.shape, (64, 64))
        self.assertEqual(checkpoint.weights.decoder.shape, (8, 8))
        self.assertEqual(checkpoint.metadata["config"]["seed"], 0)

    def test_restricted_loader_rejects_arbitrary_global(self) -> None:
        payload = pickle.dumps(os.system, protocol=2)
        with self.assertRaises(pickle.UnpicklingError):
            restricted_loads_for_test(payload)


class AlgebraAndGeometryTests(unittest.TestCase):
    def test_registered_d4_relations_are_exact_in_environment(self) -> None:
        expected = np.arange(8)
        for word in D4_RELATIONS.values():
            self.assertTrue(np.array_equal(compose_maps(canonical_maps("d4"), word), expected))

    def test_cayley_reduction_covers_all_64_products(self) -> None:
        reduction = d4_cayley_reduction()
        self.assertEqual(len(reduction), 64)
        self.assertEqual(set(reduction.values()), set(range(8)))

    def test_positive_ray_angle_does_not_identify_negative_rays(self) -> None:
        vector = np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
        self.assertAlmostEqual(float(positive_ray_angle(vector, vector)[0]), 0.0)
        self.assertAlmostEqual(float(positive_ray_angle(vector, -vector)[0]), np.pi)

    def test_tangent_basis_is_orthonormal_and_transverse(self) -> None:
        ray = normalize_rows(np.arange(1.0, 9.0)[None, :])[0]
        basis = tangent_basis(ray)
        self.assertTrue(np.allclose(basis.T @ basis, np.eye(7), atol=1e-12))
        self.assertTrue(np.allclose(basis.T @ ray, 0.0, atol=1e-12))

    def test_projective_tangent_matches_finite_difference(self) -> None:
        rng = np.random.default_rng(123)
        matrix = rng.normal(size=(8, 8)) + np.eye(8)
        ray = normalize_rows(rng.normal(size=(1, 8)))[0]
        final, _, derivative = projective_word_tangent(ray, [matrix])
        basis = tangent_basis(ray)
        epsilon = 1e-7
        perturbed = normalize_rows((ray + epsilon * basis[:, 0])[None, :])[0]
        finite = normalize_rows((matrix @ perturbed)[None, :])[0]
        estimate = (finite - final) / epsilon
        self.assertLess(np.linalg.norm(estimate - derivative[:, 0]), 2e-6)


class LearnedReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        prereg = json.loads((ROOT / "PREREGISTRATION.json").read_text(encoding="utf-8"))
        name = "projective_terminal_seed0.pt"
        cls.checkpoint = load_checkpoint(ROOT / "checkpoints" / name, prereg["checkpoints"][name])

    def test_numpy_replay_has_exact_depth_one_accuracy(self) -> None:
        batch = sample_batch(np.random.default_rng(220_000), 2048, 1, family="d4")
        _, logits = run_batch(
            self.checkpoint.weights, batch, normalize_each_step=True, dtype=np.float32
        )
        self.assertEqual(float(np.mean(np.argmax(logits, axis=1) == batch.target)), 1.0)

    def test_positive_scales_preserve_registered_futures(self) -> None:
        batch = sample_batch(np.random.default_rng(77), 4, 0, family="d4")
        codes = encode_tables(self.checkpoint.weights, batch.tables, np.float64)
        starts = np.tile(self.checkpoint.weights.state_embedding, (4, 1))
        codes = np.repeat(codes, 8, axis=0)
        curve = future_equivalence_curve(
            self.checkpoint.weights, starts, 1000.0 * starts, codes, horizon=3
        )
        self.assertEqual(curve["equivalent_through_horizon_fraction"], [1.0, 1.0, 1.0, 1.0])

    def test_slot_conversion_tracks_random_visible_swap(self) -> None:
        batch = sample_batch(np.random.default_rng(88), 32, 0, family="d4")
        slots = slots_for_word(batch.canonical_to_slot, (0, 1, 0))
        rows = np.arange(32)
        self.assertTrue(np.array_equal(batch.maps[rows, slots[:, 0]], batch.maps[rows, batch.canonical_to_slot[:, 0]]))

    def test_tangent_observability_stays_within_projective_dimension(self) -> None:
        batch = sample_batch(np.random.default_rng(99), 1, 0, family="d4")
        codes = encode_tables(self.checkpoint.weights, batch.tables, np.float64)
        tower = tangent_observability_tower(
            self.checkpoint.weights,
            self.checkpoint.weights.state_embedding[0],
            codes[0],
            horizon=3,
        )
        self.assertEqual([row["depth"] for row in tower], [0, 1, 2, 3])
        self.assertTrue(all(0 <= row["rank"] <= 7 for row in tower))
        self.assertTrue(all(row["cumulative_trace"] > 0 for row in tower))


if __name__ == "__main__":
    unittest.main(verbosity=2)

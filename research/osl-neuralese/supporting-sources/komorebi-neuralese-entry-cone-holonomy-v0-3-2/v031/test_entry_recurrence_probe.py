#!/usr/bin/env python3
"""Synthetic structural and oracle tests for the entry/recurrent probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import entry_recurrence_probe as probe


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent


class ToyWeights:
    def __init__(self):
        self.state_embedding = np.eye(8, dtype=np.float32)
        transpose_encoder = np.zeros((64, 64), dtype=np.float32)
        for row in range(8):
            for column in range(8):
                transpose_encoder[row * 8 + column, column * 8 + row] = 1.0
        self.operator_encoder = transpose_encoder
        self.decoder = np.eye(8, dtype=np.float32)

    def validate(self):
        return None


class ToyCore:
    @staticmethod
    def encode_tables(weights, tables, dtype):
        requested = np.dtype(dtype)
        values = np.asarray(tables, dtype=requested)
        flat = values.reshape(-1, 64)
        encoded = flat @ weights.operator_encoder.astype(requested).T
        return encoded.reshape(values.shape)


def toy_batch(slot_swap: bool = False):
    rotation = np.array([1, 2, 3, 0, 5, 6, 7, 4], dtype=np.int64)
    reflection = np.array([4, 7, 6, 5, 0, 3, 2, 1], dtype=np.int64)
    canonical_maps = np.stack((rotation, reflection))
    mapping = np.array([1, 0], dtype=np.int64) if slot_swap else np.array([0, 1], dtype=np.int64)
    slot_maps = canonical_maps[np.argsort(mapping)]
    tables = np.eye(8, dtype=np.float32)[slot_maps]
    return SimpleNamespace(
        tables=tables[None, ...],
        maps=slot_maps[None, ...],
        canonical_to_slot=mapping[None, ...],
    )


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The structural suite runs in a sandbox where learned checkpoint files
        # are deliberately absent; validate only the inherited source bytes.
        cls.validation = probe.validate_source_package(
            SOURCE, include_checkpoint_bytes=False
        )

    def test_frozen_source_validation(self):
        self.assertTrue(self.validation["passed"])
        self.assertEqual(self.validation["validated_file_count"], 2)
        self.assertFalse(self.validation["checkpoint_bytes_included"])

    def test_registered_suffix_count(self):
        self.assertEqual(2 ** (probe.DEFAULT_HORIZON + 1) - 1, 511)
        self.assertEqual(8 * 511, 4088)
        self.assertEqual(3 * 8 * 511 * 8 * 2, 196224)

    def test_incoming_routes_reach_declared_semantic_state(self):
        batch = toy_batch(slot_swap=True)
        weights = ToyWeights()
        native, incoming, codes, maps = probe.incoming_representatives(
            weights, batch.tables[0], batch.maps[0], batch.canonical_to_slot[0], ToyCore
        )
        for generator in range(2):
            inverse = np.argsort(maps[generator])
            direct = probe.normalize_fail_closed(
                np.einsum("ij,qj->qi", codes[generator], native[inverse])
            )
            np.testing.assert_allclose(incoming[generator], direct, rtol=0.0, atol=0.0)
            np.testing.assert_array_equal(maps[generator, inverse], np.arange(8))

    def test_ideal_operator_system_collapses_entry_and_routes(self):
        batch = toy_batch(slot_swap=False)
        weights = ToyWeights()
        native, incoming, codes, maps = probe.incoming_representatives(
            weights, batch.tables[0], batch.maps[0], batch.canonical_to_slot[0], ToyCore
        )
        np.testing.assert_allclose(incoming[0], native, atol=0.0, rtol=0.0)
        np.testing.assert_allclose(incoming[1], native, atol=0.0, rtol=0.0)
        tree = probe.enumerate_suffix_tree(
            np.stack((native, incoming[0], incoming[1])), codes, maps, weights.decoder, 4
        )
        for scheme in range(3):
            summary = probe.scheme_summary(tree, scheme, 4)
            self.assertTrue(summary["strict_hard_pass"])
            self.assertEqual(summary["decision_count"], 8 * (2**5 - 1))
        comparison = probe.compare_schemes(tree, 1, 2, 4)
        self.assertTrue(comparison["hard_signature_equal"])
        self.assertEqual(comparison["horizons"][-1]["probability_max_abs_difference"], 0.0)

    def test_tree_shell_shapes_and_semantics(self):
        batch = toy_batch(slot_swap=True)
        weights = ToyWeights()
        native, incoming, codes, maps = probe.incoming_representatives(
            weights, batch.tables[0], batch.maps[0], batch.canonical_to_slot[0], ToyCore
        )
        tree = probe.enumerate_suffix_tree(
            np.stack((native, incoming[0], incoming[1])), codes, maps, weights.decoder, 5
        )
        for depth in range(6):
            self.assertEqual(tree.hidden[depth].shape, (3, 8, 2**depth, 8))
            self.assertEqual(tree.predictions[depth].shape, (3, 8, 2**depth))
            self.assertEqual(tree.semantics[depth].shape, (8, 2**depth))
            np.testing.assert_array_equal(tree.predictions[depth][0], tree.semantics[depth])

    def test_uniform_reanchoring_reports_repairs_and_regressions_separately(self):
        weights = ToyWeights()
        codes = np.stack((np.eye(8), np.eye(8)))
        maps = np.stack((np.arange(8), np.arange(8)))
        native = np.eye(8)
        bad = native.copy()
        bad[2] = native[6]
        tree = probe.enumerate_suffix_tree(np.stack((bad, native, native)), codes, maps, weights.decoder, 2)
        comparison = probe.compare_schemes(tree, 0, 1, 2)
        self.assertEqual(comparison["repaired_error_count"], 7)
        self.assertEqual(comparison["introduced_error_count"], 0)

    def test_execution_refuses_missing_freeze(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(FileNotFoundError):
                probe.validate_execution_freeze(Path(temporary) / "missing.json")

    def test_atomic_json_round_trip(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            probe.atomic_json(path, {"passed": True, "value": 3})
            self.assertIn('"passed": true', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import numpy as np

import run_v04_probe as probe


class ProbeUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = probe.import_package(probe.DEFAULT_PACKAGE)
        cls.maps = cls.api["canonical_maps"]("d4").astype(np.int64)

    def test_oriented_antipodes_are_pi(self) -> None:
        vector = np.array([1.0, 2.0, -3.0])
        self.assertAlmostEqual(probe.oriented_angle(vector, -vector), np.pi, places=12)

    def test_shortest_representatives_cover_d4(self) -> None:
        words = probe.shortest_d4_words(self.maps)
        reached = {probe.apply_state_word(self.maps, 0, word) for word in words}
        self.assertEqual(reached, set(range(8)))
        self.assertEqual(len(words), 8)

    def test_context_bank_is_deterministic_and_unique(self) -> None:
        first = probe.make_context_bank(self.api)
        second = probe.make_context_bank(self.api)
        self.assertEqual(first["receipt"]["sha256"], second["receipt"]["sha256"])
        self.assertTrue(first["receipt"]["unique"])
        self.assertEqual(first["tables"].shape, (32, 2, 8, 8))

    def test_official_census_strictly_loads_in_float32(self) -> None:
        checkpoints, _ = probe.verify_and_load_checkpoints(probe.DEFAULT_PACKAGE, self.api)
        self.assertEqual(len(checkpoints), 12)
        self.assertTrue(all(row["weights_only_load"] for row in checkpoints))
        self.assertTrue(all(row["strict_state_load"] for row in checkpoints))
        self.assertTrue(all(row["state_dict_digest_verified"] for row in checkpoints))
        for row in checkpoints:
            self.assertEqual(next(row["model"].parameters()).dtype, probe.torch.float32)

    def test_delayed_observability_rank_ladder(self) -> None:
        operator = np.array(
            [[1.0, 1.0, 0.0], [0.0, 2.0, 1.0], [0.0, 0.0, 2.0]],
            dtype=np.float64,
        )
        observation = np.array([[1.0, 0.0, 0.0]])
        ranks = []
        for horizon in range(3):
            stack = np.concatenate(
                [observation @ np.linalg.matrix_power(operator, power) for power in range(horizon + 1)],
                axis=0,
            )
            ranks.append(probe.relative_rank(stack, 1e-10)[0])
        self.assertEqual(ranks, [1, 2, 3])

    def test_anchor_compiler_closes_d4_relations(self) -> None:
        rng = np.random.default_rng(7)
        anchors, _ = np.linalg.qr(rng.normal(size=(12, 8)))
        operators = np.stack(
            [probe.compile_anchor_action(anchors, row) for row in self.maps], axis=0
        )
        for relation in probe.RELATIONS.values():
            residual = probe.matrix_word(operators, relation) @ anchors - anchors
            self.assertLess(np.linalg.norm(residual), 1e-10)

    def test_sha256_helper_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"first")
            first = probe.sha256_file(path)
            path.write_bytes(b"second")
            self.assertNotEqual(first, probe.sha256_file(path))


if __name__ == "__main__":
    unittest.main(verbosity=2)

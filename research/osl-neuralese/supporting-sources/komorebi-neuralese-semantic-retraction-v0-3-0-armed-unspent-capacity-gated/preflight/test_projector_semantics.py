from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


PROSPECTIVE = Path(__file__).resolve().parents[1] / "prospective"
if str(PROSPECTIVE) not in sys.path:
    sys.path.insert(0, str(PROSPECTIVE))

import run_factorial_probe as probe


def dense_orthogonal(seed: int) -> np.ndarray:
    """Return a deterministic dense rotation with a fixed QR sign convention."""

    generator = np.random.default_rng(seed)
    orthogonal, upper = np.linalg.qr(
        generator.standard_normal((probe.HIDDEN_DIM, probe.HIDDEN_DIM))
    )
    signs = np.sign(np.diag(upper))
    signs[signs == 0.0] = 1.0
    return orthogonal * signs


def explicit_rank_observation(
    projector32: np.ndarray,
) -> tuple[np.ndarray, float, float, int]:
    """Apply the frozen rank rule to the exact embedding of float32 bytes."""

    applied = np.ascontiguousarray(projector32, dtype=np.float32).astype(np.float64)
    singular = np.linalg.svd(applied, compute_uv=False)
    scale = max(applied.shape) * singular[0]
    tau32 = float(scale * np.finfo(np.float32).eps)
    tau64 = float(scale * np.finfo(np.float64).eps)
    effective_rank = int(np.count_nonzero(singular > tau32))
    return singular, tau32, tau64, effective_rank


class Float32ProjectorRankSemanticsTests(unittest.TestCase):
    def test_many_dense_rotated_rank8_projectors_pass(self) -> None:
        off_diagonal = ~np.eye(probe.HIDDEN_DIM, dtype=bool)

        for seed in range(256):
            with self.subTest(seed=seed):
                rotation = dense_orthogonal(seed)
                anchors32 = np.ascontiguousarray(
                    rotation[:, : probe.N_STATES].T,
                    dtype=np.float32,
                )
                projector32, audit = probe.construct_anchor_projector32(anchors32)
                singular, tau32, _, effective_rank = explicit_rank_observation(
                    projector32
                )

                self.assertEqual(projector32.dtype, np.dtype(np.float32))
                self.assertTrue(projector32.flags.c_contiguous)
                self.assertEqual(
                    int(np.count_nonzero(projector32[off_diagonal])),
                    probe.HIDDEN_DIM * (probe.HIDDEN_DIM - 1),
                )
                self.assertTrue(audit["pass"], msg=f"seed={seed}: {audit}")
                self.assertEqual(effective_rank, probe.N_STATES)
                self.assertEqual(audit["effective_rank"], probe.N_STATES)
                self.assertAlmostEqual(audit["rank_tolerance"], tau32, places=17)
                np.testing.assert_allclose(
                    audit["singular_values"],
                    singular,
                    rtol=1e-14,
                    atol=0.0,
                )
                self.assertGreaterEqual(
                    singular[probe.N_STATES - 1],
                    probe.PROJECTOR_RANK_GAP_FACTOR * tau32,
                )
                self.assertLessEqual(singular[probe.N_STATES], tau32)

    def test_genuine_dense_rank9_projector_fails_rank8_boundary(self) -> None:
        rotation = dense_orthogonal(90210)
        projector64 = (
            rotation[:, : probe.N_STATES + 1]
            @ rotation[:, : probe.N_STATES + 1].T
        )
        projector32 = np.ascontiguousarray(projector64, dtype=np.float32)
        singular, tau32, _, effective_rank = explicit_rank_observation(projector32)
        applied = projector32.astype(np.float64)

        self.assertLess(float(np.max(np.abs(applied @ applied - applied))), 1e-6)
        self.assertLess(float(np.max(np.abs(applied.T - applied))), 1e-6)
        self.assertAlmostEqual(float(np.trace(applied)), 9.0, delta=1e-6)
        self.assertEqual(effective_rank, probe.N_STATES + 1)
        self.assertGreater(singular[probe.N_STATES], tau32)
        self.assertLessEqual(singular[probe.N_STATES + 1], tau32)

        rank8_boundary_passes = (
            effective_rank == probe.N_STATES
            and singular[probe.N_STATES - 1]
            >= probe.PROJECTOR_RANK_GAP_FACTOR * tau32
            and singular[probe.N_STATES] <= tau32
        )
        self.assertFalse(rank8_boundary_passes)

    def test_discarded_values_can_exceed_float64_default_tolerance(self) -> None:
        rotation = dense_orthogonal(7)
        anchors32 = np.ascontiguousarray(
            rotation[:, : probe.N_STATES].T,
            dtype=np.float32,
        )
        projector32, audit = probe.construct_anchor_projector32(anchors32)
        singular, tau32, tau64, effective_rank = explicit_rank_observation(projector32)
        discarded = singular[probe.N_STATES :]

        self.assertTrue(np.all(discarded > tau64))
        self.assertTrue(np.all(discarded <= tau32))
        self.assertGreater(
            int(np.linalg.matrix_rank(projector32.astype(np.float64))),
            probe.N_STATES,
        )
        self.assertEqual(effective_rank, probe.N_STATES)
        self.assertEqual(audit["effective_rank"], probe.N_STATES)
        self.assertTrue(audit["criteria"]["sigma9_at_most_tau"])


if __name__ == "__main__":
    unittest.main()

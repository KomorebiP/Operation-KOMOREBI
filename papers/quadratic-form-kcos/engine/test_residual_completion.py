import unittest
import numpy as np

from residual_completion import residual_rank_bounds, complete_residual_range, stream_complete_residual_range


class ResidualCompletionTests(unittest.TestCase):
    def test_completed_core_matches_full_spectrum(self):
        rng = np.random.default_rng(31)
        A = rng.normal(size=(18, 14))
        U = rng.normal(size=(18, 9))
        c = complete_residual_range(A, U)
        sv_true = np.linalg.svd(A, compute_uv=False)
        self.assertLess(
            np.linalg.norm(c.completed_singular_values - sv_true) / np.linalg.norm(sv_true),
            1e-12,
        )

    def test_rank_bounds_are_valid(self):
        rng = np.random.default_rng(32)
        A = rng.normal(size=(20, 15))
        U = rng.normal(size=(20, 12))
        Q, _ = np.linalg.qr(U, mode='reduced')
        F = A - Q @ (Q.T @ A)
        rank = np.linalg.matrix_rank(F, tol=1e-10)
        b = residual_rank_bounds(A, U)
        self.assertLessEqual(b.integer_lower_bound, rank)
        self.assertGreaterEqual(b.orthogonal_complement_upper_bound, rank)

    def test_streamed_completion_matches_full_spectrum(self):
        rng = np.random.default_rng(33)
        A = rng.normal(size=(21, 17))
        U = rng.normal(size=(21, 11))
        truth = np.linalg.svd(A, compute_uv=False)
        for bs in (1, 3, 7, 20):
            c = stream_complete_residual_range(A, U, block_size=bs)
            rel = np.linalg.norm(c.completed_singular_values-truth)/np.linalg.norm(truth)
            self.assertLess(rel, 1e-11)


if __name__ == '__main__':
    unittest.main(verbosity=2)

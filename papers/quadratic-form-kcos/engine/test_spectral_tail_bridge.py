import unittest
import numpy as np

from spectral_tail_bridge import (
    certify_operator_pruning,
    range_core_certificate,
    spectral_interval_from_pruned_operator,
    dual_budget_greedy_schedule,
)


class SpectralTailBridgeTests(unittest.TestCase):
    def test_block_norm_bound_dominates_operator_norm(self):
        rng = np.random.default_rng(1)
        widths = [3, 4, 2]
        n = sum(widths)
        E = rng.normal(size=(n, n))
        E = 0.5 * (E + E.T)
        H0 = rng.normal(size=(n, n))
        H0 = 0.5 * (H0 + H0.T)
        H = H0 + E
        cert = certify_operator_pruning(H, H0, widths)
        self.assertLessEqual(
            cert.exact_operator_error,
            cert.block_norm_error_bound + 1e-12
        )

    def test_weyl_interval_contains_true_eigenvalues(self):
        rng = np.random.default_rng(2)
        A = rng.normal(size=(16, 12))
        H = A.T @ A
        E = rng.normal(size=H.shape)
        E = 0.5 * (E + E.T)
        E *= 1e-3 / np.linalg.norm(E, ord=2)
        H0 = H - E
        cert = certify_operator_pruning(H, H0, [4,4,4])
        interval = spectral_interval_from_pruned_operator(
            H0, cert.block_norm_error_bound
        )
        true = np.linalg.eigvalsh(H)[::-1]
        self.assertTrue(np.all(true >= interval.lower - 1e-10))
        self.assertTrue(np.all(true <= interval.upper + 1e-10))

    def test_range_core_interval_contains_true_singular_values(self):
        rng = np.random.default_rng(3)
        A = rng.normal(size=(20, 15))
        U = rng.normal(size=(20, 7))
        cert = range_core_certificate(A, U)
        true = np.linalg.svd(A, compute_uv=False)
        self.assertTrue(
            np.all(true >= cert.lower_singular_values - 1e-10)
        )
        self.assertTrue(
            np.all(true <= cert.upper_singular_values + 1e-10)
        )


    def test_dual_budget_scheduler_respects_both_budgets(self):
        from budget_scheduler import edge_risks_depth
        B = np.array([
            [1.0, 0.10, 0.01],
            [0.10, 1.0, 0.02],
            [0.01, 0.02, 1.0],
        ])
        rho = np.array([1.0, 0.0, 0.0])
        risks = edge_risks_depth(B, rho, 3)
        r = dual_budget_greedy_schedule(
            B, risks, query_budget=0.2, operator_budget=0.03
        )
        self.assertTrue(r.certificate_valid)
        self.assertLessEqual(r.additive_query_bound, 0.2 + 1e-15)
        self.assertLessEqual(r.operator_norm_bound, 0.03 + 1e-15)


    def test_tail_bracket_contains_true_probability(self):
        import math
        from spectral_tail_bridge import positive_quadratic_tail_bracket
        from kcos_v2 import adaptive_kcos_logsf
        rng = np.random.default_rng(9)
        A = rng.normal(size=(12, 10))
        H = A.T @ A
        E = rng.normal(size=H.shape)
        E = 0.5 * (E + E.T)
        E *= 1e-3 / np.linalg.norm(E, ord=2)
        H0 = H - E
        eps = np.linalg.norm(E, ord=2)
        interval = spectral_interval_from_pruned_operator(H0, eps)
        lam = np.linalg.eigvalsh(H)[::-1]
        mean = float(np.sum(lam))
        q = mean + 4.0 * math.sqrt(2.0 * np.sum(lam * lam))
        true = adaptive_kcos_logsf(q, lam, relative_tolerance=1e-9)
        bracket = positive_quadratic_tail_bracket(
            q, interval, relative_tolerance=1e-8
        )
        self.assertLessEqual(bracket.lower_log_p, true.log_p + 1e-9)
        self.assertGreaterEqual(bracket.upper_log_p, true.log_p - 1e-9)


if __name__ == "__main__":
    unittest.main(verbosity=2)

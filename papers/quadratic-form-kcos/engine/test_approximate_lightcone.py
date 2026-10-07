import unittest
import numpy as np

from approximate_lightcone import (
    apply_polynomial,
    block_transfer_matrix,
    phase_norm_vector,
    polynomial_difference_envelope,
    power_difference_envelope,
    power_phase_envelope,
    threshold_operator,
)


class ApproximateLightConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(20260923)
        cls.q = 9
        cls.r = 4
        cls.widths = [cls.r] * cls.q
        n = cls.q * cls.r

        L = np.zeros((n, n))
        for h in range(cls.q):
            sh = slice(h * cls.r, (h + 1) * cls.r)
            L[sh, sh] = 2.1 * np.eye(cls.r) + 0.04 * rng.normal(size=(cls.r, cls.r))
            if h + 1 < cls.q:
                sg = slice((h + 1) * cls.r, (h + 2) * cls.r)
                L[sh, sg] = 0.10 * rng.normal(size=(cls.r, cls.r))
        H0 = L.T @ L

        E = np.zeros_like(H0)
        for h in range(cls.q):
            for g in range(h + 2, cls.q):
                sh = slice(h * cls.r, (h + 1) * cls.r)
                sg = slice(g * cls.r, (g + 1) * cls.r)
                C = rng.normal(size=(cls.r, cls.r))
                E[sh, sg] = C
                E[sg, sh] = C.T
        E /= np.linalg.norm(E, ord=2)
        H = H0 + 0.04 * E
        scale = np.linalg.norm(H, ord=2)
        cls.H = H / scale
        cls.H0 = H0 / scale
        cls.B = block_transfer_matrix(cls.H, cls.widths)
        cls.B0 = block_transfer_matrix(cls.H0, cls.widths)
        cls.X = np.zeros((n, 3))
        cls.X[:cls.r] = rng.normal(size=(cls.r, 3))
        cls.rho = phase_norm_vector(cls.X, cls.widths)

    def test_phase_envelope(self):
        Y = self.X.copy()
        for k in range(1, 8):
            Y = self.H @ Y
            actual = phase_norm_vector(Y, self.widths)
            bound = power_phase_envelope(self.B, self.rho, k)
            self.assertTrue(np.all(actual <= bound + 1e-12))

    def test_thresholded_power_difference(self):
        Y = self.X.copy()
        Y0 = self.X.copy()
        for k in range(1, 8):
            Y = self.H @ Y
            Y0 = self.H0 @ Y0
            actual = phase_norm_vector(Y - Y0, self.widths)
            bound = power_difference_envelope(self.B, self.B0, self.rho, k)
            self.assertTrue(np.all(actual <= bound + 1e-12))

    def test_polynomial_difference(self):
        coeff = [0.2, -0.8, 1.3, -0.7, 0.25]
        actual = phase_norm_vector(
            apply_polynomial(self.H, self.X, coeff)
            - apply_polynomial(self.H0, self.X, coeff),
            self.widths,
        )
        bound = polynomial_difference_envelope(
            self.B, self.B0, self.rho, coeff
        )
        self.assertTrue(np.all(actual <= bound + 1e-12))

    def test_hard_threshold_bound(self):
        Ht, Bt, _ = threshold_operator(self.H, self.widths, 0.003)
        k = 5
        actual = phase_norm_vector(
            np.linalg.matrix_power(self.H, k) @ self.X
            - np.linalg.matrix_power(Ht, k) @ self.X,
            self.widths,
        )
        bound = power_difference_envelope(self.B, Bt, self.rho, k)
        self.assertTrue(np.all(actual <= bound + 1e-12))

    def test_exact_case_recovers_zero_leakage(self):
        # H0 is block tridiagonal and X starts in phase zero.
        Y = self.X.copy()
        for k in range(1, 6):
            Y = self.H0 @ Y
            norms = phase_norm_vector(Y, self.widths)
            self.assertLessEqual(np.max(norms[k + 1:]), 1e-13)


if __name__ == "__main__":
    unittest.main(verbosity=2)

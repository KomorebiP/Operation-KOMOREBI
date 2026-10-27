import math
import unittest
import numpy as np
from scipy import stats

from quadratic_form_engine import (
    PositiveQuadraticFormEngine,
    NoncentralPositiveQuadraticFormEngine,
)


class NoncentralPositiveEngineTests(unittest.TestCase):
    def test_isotropic_noncentral_chisquare(self):
        n = 8
        scale = 0.35
        mu = np.linspace(-0.8, 0.9, n)
        Sigma = np.eye(n)
        M = np.eye(n)
        eng = NoncentralPositiveQuadraticFormEngine.from_gaussian_quadratic(
            mu, Sigma, M, scale=scale
        )
        nc = float(np.sum(mu*mu))
        # Choose a right-tail point well above the mean.
        q = scale * stats.ncx2.isf(1e-7, df=n, nc=nc)
        r = eng.logsf(q, relative_tolerance=1e-8)
        ref = stats.ncx2.logsf(q/scale, df=n, nc=nc)
        self.assertTrue(r.certificate_passed)
        self.assertLess(abs(r.log_p-ref), 2e-7)

    def test_diagonal_reduction_parameters(self):
        var = np.array([0.4, 1.2, 2.0, 0.7])
        mdiag = np.array([1.5, 0.5, 2.0, 0.8])
        mu = np.array([0.2, -0.5, 0.7, 1.1])
        eng = NoncentralPositiveQuadraticFormEngine.from_gaussian_quadratic(
            mu, np.diag(var), np.diag(mdiag)
        )
        expected_w = var * mdiag
        expected_nc = mu*mu / var
        order = np.argsort(expected_w)[::-1]
        self.assertTrue(np.allclose(eng.weights, expected_w[order], rtol=1e-12, atol=1e-12))
        self.assertTrue(np.allclose(eng.noncentrality, expected_nc[order], rtol=1e-11, atol=1e-11))
        self.assertLess(abs(eng.shift), 1e-11)

    def test_singular_covariance_keeps_deterministic_shift(self):
        mu = np.array([0.5, 2.0])
        Sigma = np.diag([1.0, 0.0])
        M = np.eye(2)
        eng = NoncentralPositiveQuadraticFormEngine.from_gaussian_quadratic(
            mu, Sigma, M
        )
        self.assertEqual(eng.weights.size, 1)
        self.assertAlmostEqual(eng.weights[0], 1.0, places=12)
        self.assertAlmostEqual(eng.noncentrality[0], 0.25, places=12)
        self.assertAlmostEqual(eng.shift, 4.0, places=12)

    def test_zero_mean_matches_central_moments(self):
        rng = np.random.default_rng(12)
        B = rng.normal(size=(6, 6))
        Sigma = B @ B.T
        C = rng.normal(size=(6, 6))
        M = C @ C.T
        mu = np.zeros(6)

        nc = NoncentralPositiveQuadraticFormEngine.from_gaussian_quadratic(
            mu, Sigma, M
        )
        central = PositiveQuadraticFormEngine.from_gaussian_quadratic(Sigma, M)
        self.assertAlmostEqual(nc.mean, central.mean, places=9)
        self.assertAlmostEqual(nc.variance, central.variance, places=7)
        self.assertLess(np.max(nc.noncentrality), 1e-20)


if __name__ == "__main__":
    unittest.main(verbosity=2)

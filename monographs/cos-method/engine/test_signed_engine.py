import math
import unittest
import numpy as np
from scipy import stats

from quadratic_form_engine import SignedCentralQuadraticFormEngine
from generalized_tail import signed_central_logsf, signed_derivative
from generalized_packets import packetized_signed_central_logsf


class SignedCentralEngineTests(unittest.TestCase):
    def test_mixed_laplace_exact_control(self):
        a=0.07
        weights=np.array([a,a,-a,-a])
        eng=SignedCentralQuadraticFormEngine.from_spectrum(weights)
        for p in [1e-4,1e-8,1e-20,1e-50,1e-100,1e-200]:
            q=2*a*math.log(0.5/p)
            r=eng.logsf(q,relative_tolerance=1e-9,max_K=262144)
            self.assertLess(abs(r.log10_p-math.log10(p)),2e-8)
            # Low-rank mixed characteristic functions decay slowly; the value
            # is exact-control accurate but the current analytic COS-series
            # certificate is intentionally allowed to reject the result.
            if p <= 1e-8:
                self.assertFalse(r.certificate_passed)

    def test_negative_finite_endpoint_exact_control(self):
        a=0.02
        df=80
        weights=-a*np.ones(df)
        eng=SignedCentralQuadraticFormEngine.from_spectrum(weights)
        for p in [1e-8,1e-30,1e-100,1e-200]:
            x=stats.chi2.ppf(p,df)
            q=-a*x
            r=eng.logsf(q,relative_tolerance=1e-9,max_K=262144)
            self.assertTrue(r.certificate_passed)
            self.assertLess(abs(r.log10_p-math.log10(p)),2e-8)
        z=eng.logsf(0.0)
        self.assertEqual(z.p_value,0.0)
        self.assertEqual(z.log_p,-math.inf)

    def test_gaussian_quadratic_diagonal_reduction(self):
        variance=np.array([0.5,1.2,0.8,2.0])
        mdiag=np.array([2.0,-1.5,0.4,-0.25])
        eng=SignedCentralQuadraticFormEngine.from_gaussian_quadratic(
            np.diag(variance),np.diag(mdiag)
        )
        expected=np.sort(variance*mdiag)
        observed=np.sort(eng.eigenvalues)
        self.assertTrue(np.allclose(observed,expected,rtol=1e-12,atol=1e-12))

    def test_packetized_matches_exact_mixed_multiscale(self):
        rng=np.random.default_rng(44)
        pos=np.exp(rng.uniform(math.log(0.002),math.log(0.08),180))
        neg=-np.exp(rng.uniform(math.log(0.001),math.log(0.04),160))
        w=np.r_[pos,neg]
        theta=0.94/(2*np.max(pos))
        q=signed_derivative(theta,w,1)
        exact=signed_central_logsf(q,w,relative_tolerance=1e-10,max_K=262144)
        packet=packetized_signed_central_logsf(q,w,relative_tolerance=1e-8,max_K=262144)
        self.assertTrue(exact.passed)
        self.assertTrue(packet.passed)
        self.assertLess(abs(packet.log10_p-exact.log10_p),2e-8)


if __name__=='__main__':
    unittest.main(verbosity=2)

import math
import unittest
import numpy as np

from residual_trace_cap import (
    residual_spectrum_certificate,
    trace_cap_log_mgf_upper,
    trace_frobenius_cap_log_mgf_upper,
    trace_cap_tail_bracket,
)


class ResidualTraceCapTests(unittest.TestCase):
    def test_exact_additive_identity(self):
        rng = np.random.default_rng(1)
        A = rng.normal(size=(18, 14))
        U, _ = np.linalg.qr(rng.normal(size=(18, 7)), mode='reduced')
        B = U.T @ A
        F = A - U @ B
        lhs = A.T @ A
        rhs = B.T @ B + F.T @ F
        rel = np.linalg.norm(lhs-rhs) / np.linalg.norm(lhs)
        self.assertLess(rel, 1e-12)

    def test_trace_is_exact(self):
        rng = np.random.default_rng(2)
        A = rng.normal(size=(20, 15))
        U = rng.normal(size=(20, 8))
        cert = residual_spectrum_certificate(A, U)
        true_trace = float(np.trace(A.T @ A))
        self.assertAlmostEqual(cert.exact_total_trace, true_trace, places=10)

    def test_log_mgf_envelope_dominates_exact(self):
        rng = np.random.default_rng(3)
        A = rng.normal(size=(16, 12))
        U = rng.normal(size=(16, 6))
        cert = residual_spectrum_certificate(A, U)
        H = A.T @ A
        lam = np.linalg.eigvalsh(H)
        theta = 0.1 / np.linalg.eigvalsh(H).max()
        exact = float(-0.5*np.sum(np.log1p(-2*theta*lam)))
        upper = trace_cap_log_mgf_upper(theta, cert)
        self.assertLessEqual(exact, upper + 1e-10)

    def test_tail_bracket_contains_exact_kcos_tail(self):
        from kcos_v2 import adaptive_kcos_logsf
        rng = np.random.default_rng(4)
        A = rng.normal(size=(18, 14))
        U = rng.normal(size=(18, 9))
        cert = residual_spectrum_certificate(A, U)
        lam = np.linalg.eigvalsh(A.T @ A)[::-1]
        mean = float(np.sum(lam))
        q = mean + 5*math.sqrt(2*np.sum(lam*lam))
        true = adaptive_kcos_logsf(q, lam, relative_tolerance=1e-9)
        br = trace_cap_tail_bracket(q, cert, relative_tolerance=1e-8)
        self.assertLessEqual(br.lower_log_p, true.log_p + 1e-9)
        self.assertGreaterEqual(br.upper_log_p, true.log_p - 1e-9)

    def test_trace_frobenius_cap_envelope_dominates_exact(self):
        rng = np.random.default_rng(5)
        for _ in range(12):
            A = rng.normal(size=(15, 11))
            U = rng.normal(size=(15, 7))
            cert = residual_spectrum_certificate(A, U)
            H = A.T @ A
            lam = np.linalg.eigvalsh(H)
            theta = 0.08 / lam.max()
            exact = float(-0.5*np.sum(np.log1p(-2*theta*lam)))
            upper = trace_frobenius_cap_log_mgf_upper(theta, cert)
            self.assertLessEqual(exact, upper + 1e-10)


if __name__ == '__main__':
    unittest.main(verbosity=2)

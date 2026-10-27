import unittest
import numpy as np
import mpmath as mp
from scipy.linalg import hadamard

from verified_spectrum import (
    certify_float64_factor_spectrum,
    certified_float64_factor_logsf,
)


class VerifiedSpectrumTests(unittest.TestCase):
    def test_dense_exact_binary_factor_contains_known_spectrum(self):
        n = 64
        Q = hadamard(n, dtype=np.float64) / 8.0
        singular = np.repeat(np.array([1.0, 0.75, 0.5, 0.25]), 16)
        A = Q * singular[None, :]
        cert = certify_float64_factor_spectrum(
            A, candidate_digits=50, interval_dps=65, working_dps=95
        )
        exact = [1.0]*16 + [0.5625]*16 + [0.25]*16 + [0.0625]*16
        with mp.workdps(100):
            for lo_s, hi_s, value in zip(cert.lower, cert.upper, exact):
                self.assertLessEqual(mp.mpf(lo_s), mp.mpf(value))
                self.assertGreaterEqual(mp.mpf(hi_s), mp.mpf(value))

    def test_outward_endpoint_serialization_does_not_collapse(self):
        Q = hadamard(64, dtype=np.float64) / 8.0
        singular = np.repeat(np.array([1.0, 0.75, 0.5, 0.25]), 16)
        A = Q * singular[None, :]
        cert = certify_float64_factor_spectrum(
            A, candidate_digits=50, interval_dps=65, working_dps=95
        )
        with mp.workdps(100):
            self.assertLess(mp.mpf(cert.lower[0]), mp.mpf("1"))
            self.assertGreater(mp.mpf(cert.upper[0]), mp.mpf("1"))

    def test_random_dense_reference_containment(self):
        rng = np.random.default_rng(12091)
        A = rng.normal(size=(10, 15))
        A *= np.geomspace(1.0, 0.15, 15)[None, :]
        A /= np.sqrt(15)
        cert = certify_float64_factor_spectrum(
            A, candidate_digits=55, interval_dps=70, working_dps=105
        )

        with mp.workdps(105):
            Amp = mp.matrix([
                [
                    mp.mpf(float(A[i, j]).as_integer_ratio()[0])
                    / float(A[i, j]).as_integer_ratio()[1]
                    for j in range(A.shape[1])
                ]
                for i in range(A.shape[0])
            ])
            vals, _ = mp.eigsy(Amp * Amp.T)
            exact = [vals[i] for i in range(len(vals)-1, -1, -1)]
            for lo_s, hi_s, value in zip(cert.lower, cert.upper, exact):
                self.assertLessEqual(mp.mpf(lo_s), value)
                self.assertGreaterEqual(mp.mpf(hi_s), value)

    def test_end_to_end_matrix_tail_fail_closed_contract(self):
        n = 64
        Q = hadamard(n, dtype=np.float64) / 8.0
        singular = np.repeat(np.array([1.0, 0.75, 0.5, 0.25]), 16)
        A = Q * singular[None, :]
        result = certified_float64_factor_logsf(
            "131.33201485100517",
            A,
            relative_accuracy="1e-10",
            initial_candidate_digits=50,
            max_candidate_digits=80,
            candidate_step=30,
            interval_dps=65,
            tail_accuracy_fraction="0.05",
            tail_kwargs=dict(
                initial_K=64,
                initial_L="10",
                initial_interval_dps=50,
                max_K=4096,
                max_L=18,
                max_interval_dps=120,
                working_dps=170,
            ),
        )
        self.assertTrue(result.certified)
        self.assertLess(
            mp.mpf(result.achieved_relative_ratio_minus_one),
            mp.mpf("1e-10"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

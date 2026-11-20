"""Reproducible exact certificates for the conjecture reading edition.

Author: Komorebi P.
Runs the published arithmetic verifiers on their recorded finite domains.
"""
import unittest

from sequence_euler_spectral_jet import certify
from sequence_arithmetic_subminors import audit


class ConjectureApplicationCertifications(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.euler = certify()
        cls.minors = audit()

    def test_euler_spectral_finite_range(self):
        self.assertEqual(self.euler["status"], "passed")
        self.assertEqual(self.euler["total_spectral_comparisons"], 665)
        self.assertEqual(len(self.euler["spectral_checks"]), 19)

    def test_period_jumps_and_jets(self):
        self.assertEqual(self.euler["total_jump_comparisons"], 306)
        self.assertEqual(self.euler["total_jet_equivalences"], 2025)
        self.assertEqual(len(self.euler["jet_checks"]), 9)

    def test_high_index_nonobstruction(self):
        item = self.euler["known_positive_controls"][0]
        self.assertEqual((item["p"], item["n"]), (43, 978))
        self.assertTrue(item["weighted_pair"])
        self.assertFalse(item["weighted_triple"])

    def test_equal_stride_hankel_numerators(self):
        self.assertEqual(self.minors["status"], "passed")
        self.assertEqual(self.minors["equal_stride_checks"], 8960)

    def test_unequal_stride_prime_support(self):
        self.assertEqual(self.minors["unequal_stride_checks"], 11520)
        self.assertIn("4/45", self.minors["arithmetic_subminor_counterexample"])


if __name__ == "__main__":
    unittest.main()

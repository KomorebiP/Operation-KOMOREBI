"""Regression controls for precision-independent fail-closed decisions."""
from decimal import Decimal
from fractions import Fraction
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
import mpmath as mp
from mpmath import iv

from accuracy_driven import certified_positive_logsf
from directed_accuracy import (directed_relative_accuracy, scaled_accuracy_budget,
                               outward_interval_string, interval_endpoint_strings)
from interval_kcos import interval_positive_logsf
from verified_spectrum import certified_float64_factor_logsf


OUTER = "[-1.00000000000000000001, -0.99999999999999999999]"


def mock_tail(interval=OUTER):
    return SimpleNamespace(
        certified=True, passed_positive_sum=True, log10_interval=interval,
        arithmetic_only_log10_interval=interval,
        support_alias_bound_interval="[0, 0]", series_tail_bound_interval="[0, 0]",
    )


class DirectedContractTests(unittest.TestCase):
    def test_nonfinite_serializer_endpoints(self):
        self.assertEqual(outward_interval_string(iv.mpf(["-inf", "+inf"])),
                         "[-inf, +inf]")
        self.assertEqual(outward_interval_string(iv.mpf("-inf")), "[-inf, -inf]")
        with self.assertRaises(ValueError):
            outward_interval_string(iv.mpf("nan"))

    def test_decimal_serialization_encloses_exact_binary_endpoints(self):
        previous = iv.dps
        try:
            for digits in [15, 50, 90]:
                iv.dps = digits
                for interval in [iv.mpf(0.1), iv.mpf(1) / 3, -iv.mpf(1) / 3,
                                 iv.mpf("1e-5000") / 7, iv.mpf("1e5000") / 7]:
                    left, right = interval_endpoint_strings(outward_interval_string(interval))
                    def exact(raw):
                        sign, mantissa, exponent, _ = raw
                        value = Fraction(int(mantissa))
                        value *= Fraction(2) ** int(exponent)
                        return -value if sign else value
                    lower, upper = interval._mpi_
                    self.assertLessEqual(Fraction(Decimal(left)), exact(lower))
                    self.assertGreaterEqual(Fraction(Decimal(right)), exact(upper))
            iv.dps = 15
            x = iv.mpf(1) / 3
            old_left, old_right = interval_endpoint_strings(str(x))
            lower, upper = x._mpi_
            self.assertGreater(Fraction(Decimal(old_left)), exact(lower))
            self.assertLess(Fraction(Decimal(old_right)), exact(upper))
        finally:
            iv.dps = previous

    def test_low_default_precision_cannot_collapse_acceptance_width(self):
        with mp.workdps(15):
            # This is the precise witness to the historical point-parser bug.
            self.assertEqual(mp.mpf("-1.00000000000000000001"),
                             mp.mpf("-0.99999999999999999999"))
            result = directed_relative_accuracy(OUTER, "1e-30", dps=120)
        self.assertFalse(result.accepted)
        self.assertGreater(Decimal(result.ratio_upper), Decimal("1e-20"))

    def test_reported_ratio_is_an_upper_bound_and_precision_is_restored(self):
        previous = iv.dps
        result = directed_relative_accuracy(OUTER, "1e-18", dps=120)
        self.assertEqual(iv.dps, previous)
        self.assertTrue(result.accepted)
        with mp.workdps(180):
            exact = mp.expm1(mp.log(10) * mp.mpf("2e-20"))
            self.assertGreaterEqual(mp.mpf(result.ratio_upper), exact)

    def test_matrix_wrapper_rejects_collapsed_false_certificate(self):
        spectrum = SimpleNamespace(lower=("1",) * 4, upper=("1",) * 4)
        with mp.workdps(15), patch("verified_spectrum.certify_float64_factor_spectrum",
                                 return_value=spectrum), \
                patch("verified_spectrum.certified_positive_logsf",
                      return_value=mock_tail()):
            result = certified_float64_factor_logsf(
                "2", np.eye(4), relative_accuracy="1e-30",
                initial_candidate_digits=50, max_candidate_digits=50,
            )
        self.assertFalse(result.certified)
        self.assertEqual(result.log10_interval, OUTER)

    def test_matrix_wrapper_preserves_literal_outer_endpoints(self):
        spectrum = SimpleNamespace(lower=("1",) * 4, upper=("1",) * 4)
        with mp.workdps(15), patch("verified_spectrum.certify_float64_factor_spectrum",
                                 return_value=spectrum), \
                patch("verified_spectrum.certified_positive_logsf",
                      return_value=mock_tail()):
            result = certified_float64_factor_logsf(
                "2", np.eye(4), relative_accuracy="1e-18",
                initial_candidate_digits=50, max_candidate_digits=50,
            )
        self.assertTrue(result.certified)
        self.assertEqual(result.log10_interval, OUTER)
        self.assertGreater(Decimal(result.achieved_relative_ratio_minus_one), 0)

    def test_accuracy_wrapper_uses_directed_decision_and_retains_tolerance(self):
        tolerance = "1.000000000000000000000001e-30"
        params = {"theta": "1", "upper": "2", "eta": "1.5"}
        with mp.workdps(15), patch("accuracy_driven.design_positive_tail_parameters",
                                 return_value=params), \
                patch("accuracy_driven.interval_positive_logsf", return_value=mock_tail()):
            result = certified_positive_logsf(
                "2", ["1"] * 4, relative_accuracy=tolerance,
                initial_K=32, max_K=32, initial_L="8", max_L=8,
                initial_interval_dps=50, max_interval_dps=50,
            )
        self.assertFalse(result.certified)
        self.assertEqual(result.requested_relative_accuracy, tolerance)
        self.assertGreater(Decimal(result.achieved_relative_ratio_minus_one), 0)

    def test_subordinate_budget_is_conservative(self):
        requested, fraction = "1.000000000000000000000001e-30", "0.1"
        budget = scaled_accuracy_budget(requested, fraction, dps=120)
        with mp.workdps(180):
            self.assertLessEqual(mp.mpf(budget), mp.mpf(requested) * mp.mpf(fraction))
            self.assertGreater(mp.mpf(budget), 0)

    def test_backend_rejects_outside_positive_contract(self):
        base = dict(q_decimal="1", eigenvalue_decimals=["0.1"] * 4,
                    theta_decimal="1", upper_decimal="2", eta_decimal="2",
                    K=8, interval_dps=50)
        changes = [dict(q_decimal="-1"), dict(eigenvalue_decimals=["-0.1"] * 4),
                   dict(eigenvalue_decimals=["0"] * 4), dict(eta_decimal="5"),
                   dict(upper_decimal="1"), dict(eta_decimal="1"),
                   dict(eigenvalue_decimals=["0.1"] * 2), dict(K=0),
                   dict(q_decimal="Infinity")]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                interval_positive_logsf(**(base | change))

    def test_accuracy_validation_rejects_nonfinite_or_nonpositive(self):
        for tolerance in ["0", "-1", "NaN", "Infinity"]:
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                directed_relative_accuracy(OUTER, tolerance)


if __name__ == "__main__":
    unittest.main(verbosity=2)

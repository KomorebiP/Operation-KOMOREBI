import math
import unittest
from decimal import Decimal, localcontext
from directed_accuracy import interval_endpoint_strings, directed_relative_accuracy

from interval_kcos import (
    design_positive_tail_parameters,
    even_df_scaled_chi_square_logsf_interval,
    interval_positive_logsf,
    scaled_chi_square_target_point,
)


class IntervalKCOSTests(unittest.TestCase):
    def _run_control(self, target):
        q = scaled_chi_square_target_point(
            -target,
            coefficient_decimal="0.02",
            df=80,
            working_dps=220,
            output_digits=180,
        )
        eig = ["0.02"] * 80
        params = design_positive_tail_parameters(
            q, eig, L="10", working_dps=220, output_digits=180
        )
        result = interval_positive_logsf(
            q,
            eig,
            theta_decimal=params["theta"],
            upper_decimal=params["upper"],
            eta_decimal=params["eta"],
            K=128,
            interval_dps=90,
        )
        exact = even_df_scaled_chi_square_logsf_interval(
            q,
            coefficient_decimal="0.02",
            df=80,
            interval_dps=90,
        )

        self.assertGreater(exact["width_decades"], 0.0)
        self.assertTrue(result.passed_positive_sum)
        self.assertLessEqual(result.log10_lower, exact["log10_upper"])
        self.assertGreaterEqual(result.log10_upper, exact["log10_lower"])
        self.assertLess(result.multiplicative_ratio_minus_one, 1e-8)
        return result

    def test_1e100(self):
        self._run_control(100)

    def test_1e1000(self):
        self._run_control(1000)

    def test_1e5000(self):
        self._run_control(5000)

    def test_reported_width_uses_unrounded_endpoints(self):
        result = self._run_control(1000)
        left, right = interval_endpoint_strings(result.log10_interval)
        with localcontext() as ctx:
            ctx.prec = 160
            expected = float(Decimal(right) - Decimal(left))
        self.assertTrue(math.isclose(result.width_decades, expected, rel_tol=1e-13))
        accuracy = directed_relative_accuracy(result.log10_interval, "1e-8", dps=140)
        self.assertTrue(math.isclose(
            result.multiplicative_ratio_minus_one, float(accuracy.ratio_upper),
            rel_tol=1e-13,
        ))

    def test_arithmetic_width_survives_binary64_endpoint_collapse(self):
        result = self._run_control(5000)
        left, right = interval_endpoint_strings(result.arithmetic_only_log10_interval)
        self.assertEqual(float(left), float(right))
        with localcontext() as ctx:
            ctx.prec = 200
            expected = float(Decimal(right) - Decimal(left))
        self.assertGreater(expected, 0.0)
        self.assertGreater(result.arithmetic_only_width_decades, 0.0)
        # Outward decimal serialization can enlarge a very narrow interval.
        # Bound that enlargement by one final-place unit at each endpoint,
        # plus the final advisory conversion to binary64.
        with localcontext() as ctx:
            ctx.prec = 200
            quantum = sum(Decimal(1).scaleb(Decimal(v).as_tuple().exponent)
                          for v in (left, right))
            observed = Decimal.from_float(result.arithmetic_only_width_decades)
            error = abs(observed - (Decimal(right) - Decimal(left)))
            self.assertLessEqual(error, quantum + abs(observed) * Decimal("2e-16"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

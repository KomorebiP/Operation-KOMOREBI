import math
import unittest

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

        self.assertTrue(result.passed_positive_sum)
        self.assertLessEqual(result.log10_lower, exact["log10_upper"])
        self.assertGreaterEqual(result.log10_upper, exact["log10_lower"])
        self.assertLess(result.multiplicative_ratio_minus_one, 1e-8)

    def test_1e100(self):
        self._run_control(100)

    def test_1e1000(self):
        self._run_control(1000)

    def test_1e5000(self):
        self._run_control(5000)


if __name__ == "__main__":
    unittest.main(verbosity=2)

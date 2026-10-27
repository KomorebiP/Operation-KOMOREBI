import unittest
from interval_kcos import scaled_chi_square_target_point
from accuracy_driven import certified_positive_logsf

class AccuracyDrivenTests(unittest.TestCase):
    def test_targets(self):
        eig = ["0.02"]*80
        for depth in [100,1000,5000]:
            q = scaled_chi_square_target_point(
                -depth, coefficient_decimal="0.02", df=80,
                working_dps=240, output_digits=190
            )
            for eps in ["1e-8","1e-10","1e-12","1e-14"]:
                r = certified_positive_logsf(
                    q, eig, relative_accuracy=eps,
                    initial_K=32, initial_L="8", initial_interval_dps=50,
                    max_K=8192, max_L=20, max_interval_dps=140,
                )
                self.assertTrue(r.certified, (depth, eps, r))

    def test_fail_closed(self):
        eig=["0.02"]*80
        q=scaled_chi_square_target_point(
            -5000, coefficient_decimal="0.02", df=80,
            working_dps=220, output_digits=180
        )
        r=certified_positive_logsf(
            q,eig,relative_accuracy="1e-40",
            initial_K=32, initial_L="8", initial_interval_dps=30,
            max_K=32, max_L=8, max_interval_dps=30,
        )
        self.assertFalse(r.certified)
        self.assertIsNotNone(r.failure_reason)

if __name__=="__main__":
    unittest.main(verbosity=2)

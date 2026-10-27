import unittest

import numpy as np

from rrct.projectors import NestedOrthogonalProjectors


class ProjectorTests(unittest.TestCase):
    def test_exact_reconstruction_and_nesting(self) -> None:
        bank = NestedOrthogonalProjectors(12, ranks=(2, 5, 8, 12), seed=4)
        audit = bank.validate(atol=1e-10)
        self.assertTrue(audit["valid"])
        x = np.random.default_rng(5).normal(size=12)
        np.testing.assert_allclose(bank.reconstruct(bank.decompose(x)), x, atol=1e-10)
        for i in range(len(bank)):
            for j in range(len(bank)):
                expected = bank.matrix(min(i, j))
                np.testing.assert_allclose(
                    bank.matrix(i) @ bank.matrix(j), expected, atol=1e-10
                )

    def test_unresolved_norm_reaches_zero_at_identity(self) -> None:
        bank = NestedOrthogonalProjectors(10, n_levels=4, seed=6)
        residuals = bank.residual_norms(np.arange(1.0, 11.0))
        self.assertAlmostEqual(float(residuals[-1]), 0.0, places=10)


if __name__ == "__main__":
    unittest.main()

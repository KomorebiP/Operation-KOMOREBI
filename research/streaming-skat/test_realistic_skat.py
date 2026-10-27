import unittest
import numpy as np

from benchmark_realistic_skat import (
    simulate_copy_ld_fixed,
    simulate_gaussian_ld,
    covariates,
    process_full,
    stream_kernel_raw,
    spectrum_from_kernel,
)


class RealisticSKATTests(unittest.TestCase):
    def test_copy_ld_is_reproducible_and_valid_genotype(self):
        G1, maf1 = simulate_copy_ld_fixed(
            n=120, m=300, block=30, copy_prob=0.9, seed=11
        )
        G2, maf2 = simulate_copy_ld_fixed(
            n=120, m=300, block=30, copy_prob=0.9, seed=11
        )
        self.assertTrue(np.array_equal(G1, G2))
        self.assertTrue(np.array_equal(maf1, maf2))
        self.assertTrue(np.all(np.isin(G1, [0.0, 1.0, 2.0])))

    def test_streamed_raw_kernel_matches_materialized_factor(self):
        G, maf = simulate_gaussian_ld(
            n=140, m=500, block=25, rho=0.8, seed=12
        )
        _, Qx = covariates(140, seed=13)
        _, Kfull, _, _ = process_full(G, maf, Qx)

        for bs in [17, 61, 149]:
            Ks, _ = stream_kernel_raw(G, maf, Qx, bs)
            rel = np.linalg.norm(Ks-Kfull) / np.linalg.norm(Kfull)
            self.assertLess(rel, 2e-12)

    def test_spectrum_is_psd_after_kernel_construction(self):
        G, maf = simulate_copy_ld_fixed(
            n=100, m=250, block=25, copy_prob=0.85, seed=14
        )
        _, Qx = covariates(100, seed=15)
        _, K, _, _ = process_full(G, maf, Qx)
        lam, _, _ = spectrum_from_kernel(K)
        self.assertTrue(np.all(lam >= 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)

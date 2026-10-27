from __future__ import annotations

import unittest


try:
    import torch
except ImportError:
    torch = None


@unittest.skipIf(torch is None, "PyTorch is not installed")
class NumericDiagnosticTests(unittest.TestCase):
    def test_decoded_basis_supports_biasless_projection(self) -> None:
        from g1d.dynamic import decoded_injection_basis

        projection = torch.nn.Linear(3, 5, bias=False)
        basis, summary = decoded_injection_basis(projection)
        self.assertEqual(tuple(basis.shape), (5, 3))
        self.assertFalse(summary["decoder_has_bias"])
        reconstructed = basis @ (basis.T @ projection.weight.detach().double())
        self.assertTrue(
            torch.allclose(reconstructed, projection.weight.detach().double(), atol=1e-10)
        )

    def test_geometry_detects_rank_one_collapse(self) -> None:
        from g1d.geometry import geometry_summary, matrix_spectrum

        generator = torch.Generator().manual_seed(11)
        scalar = torch.randn(120, 1, generator=generator)
        features = scalar @ torch.ones(1, 12)
        labels = torch.arange(120) % 6
        result = geometry_summary(features, labels)
        self.assertAlmostEqual(result["covariance_stable_rank"], 1.0, places=8)
        spectrum = matrix_spectrum(torch.ones(20, 10))
        self.assertAlmostEqual(spectrum["stable_rank"], 1.0, places=8)
        self.assertGreater(spectrum["top1_energy_fraction"], 0.999999)

    def test_geometry_handles_zero_features_explicitly(self) -> None:
        from g1d.geometry import geometry_summary, matrix_spectrum

        labels = torch.arange(12) % 6
        geometry = geometry_summary(torch.zeros(12, 4), labels)
        self.assertEqual(geometry["mean_pairwise_cosine"], 0.0)
        spectrum = matrix_spectrum(torch.zeros(5, 3))
        self.assertEqual(spectrum["stable_rank"], 0.0)
        self.assertEqual(spectrum["rank_for_99pct_energy"], 0)

    def test_paired_geometry_identical(self) -> None:
        from g1d.geometry import paired_geometry

        features = torch.arange(60, dtype=torch.float32).reshape(10, 6) + 1
        result = paired_geometry(features, features.clone())
        self.assertEqual(result["mean_l2_difference"], 0.0)
        self.assertAlmostEqual(result["mean_cosine_similarity"], 1.0, places=10)

    def test_probe_recovers_separable_classes(self) -> None:
        from g1d.probes import diagnostic_probe

        def split(rows_per_class: int, noise_seed: int):
            generator = torch.Generator().manual_seed(noise_seed)
            labels = torch.arange(6).repeat_interleave(rows_per_class)
            features = torch.nn.functional.one_hot(labels, num_classes=6).float()
            features += 0.01 * torch.randn(features.shape, generator=generator)
            return features, labels

        train_x, train_y = split(20, 1)
        validation_x, validation_y = split(8, 2)
        iid_x, iid_y = split(10, 3)
        ood_x, ood_y = split(10, 4)
        result = diagnostic_probe(
            train_x,
            validation_x,
            iid_x,
            ood_x,
            train_y,
            validation_y,
            iid_y,
            ood_y,
            classes=6,
            permutation_count=127,
            seed=7,
        )
        self.assertEqual(result["tier"], "STRONG_LINEAR")
        self.assertEqual(result["ridge"]["iid"]["accuracy"], 1.0)
        self.assertLessEqual(result["permutation_null"]["p_value"], 0.01)


if __name__ == "__main__":
    unittest.main()

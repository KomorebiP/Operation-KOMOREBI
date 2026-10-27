import unittest

import numpy as np

from rrct.learning import LatentFactorProbe, RidgeBinaryReadout, interaction_features


class LearningTests(unittest.TestCase):
    def test_interaction_feature_shapes(self) -> None:
        x = np.ones((5, 4))
        self.assertEqual(interaction_features(x, 1).shape, (5, 5))
        self.assertEqual(interaction_features(x, 2).shape, (5, 11))
        self.assertEqual(interaction_features(x, 3).shape, (5, 15))

    def test_cubic_readout_learns_three_bit_product(self) -> None:
        x = np.array(
            [[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)],
            dtype=float,
        )
        y = (np.prod(x, axis=1) > 0).astype(int)
        model = RidgeBinaryReadout(alpha=1e-6, degree=3).fit(x, y)
        self.assertEqual(model.score(x, y), 1.0)

    def test_latent_probe_reuses_factorization(self) -> None:
        rng = np.random.default_rng(7)
        factors = np.array(
            [[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)],
            dtype=float,
        )
        mixing = rng.normal(size=(3, 9))
        features = factors @ mixing
        probe = LatentFactorProbe(alpha=1e-6).fit(features, factors)
        self.assertEqual(probe.binding_accuracy(features, factors), 1.0)


if __name__ == "__main__":
    unittest.main()

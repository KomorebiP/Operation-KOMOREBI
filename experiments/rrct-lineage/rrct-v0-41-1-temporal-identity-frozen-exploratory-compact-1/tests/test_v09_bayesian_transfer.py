import copy
import pickle
import unittest

import numpy as np

from rrct import BayesianCausalTransferModel


class BayesianCausalTransferModelTests(unittest.TestCase):
    def test_exact_one_dimensional_posterior_and_prediction(self) -> None:
        model = BayesianCausalTransferModel(
            1,
            include_intercept=False,
            prior_precision=1.0,
            prior_shape=2.0,
            prior_scale=1.0,
            training=True,
        )
        self.assertTrue(model.observe([1.0], 0.5))
        snapshot = model.snapshot()
        np.testing.assert_allclose(snapshot["posterior_precision"], [[2.0]])
        np.testing.assert_allclose(snapshot["posterior_mean"], [0.25])
        self.assertEqual(snapshot["posterior_shape"], 2.5)
        self.assertEqual(snapshot["posterior_scale"], 1.0625)
        prediction = model.predict([1.0])
        self.assertEqual(prediction.mean, 0.25)
        self.assertEqual(prediction.scale_squared, 0.6375)
        self.assertEqual(prediction.variance, 1.0625)
        self.assertEqual(prediction.degrees_of_freedom, 5.0)
        self.assertAlmostEqual(
            prediction.variance,
            prediction.aleatoric_variance + prediction.epistemic_variance,
        )

    def test_student_t_probability_quantile_and_symmetry(self) -> None:
        model = BayesianCausalTransferModel(1)
        prediction = model.predict([0.5])
        self.assertEqual(prediction.cdf(prediction.mean), 0.5)
        self.assertEqual(prediction.probability_above(prediction.mean), 0.5)
        lower = prediction.quantile(0.05)
        upper = prediction.quantile(0.95)
        self.assertAlmostEqual(
            prediction.mean - lower,
            upper - prediction.mean,
            places=10,
        )
        self.assertAlmostEqual(prediction.cdf(lower), 0.05, places=10)
        self.assertAlmostEqual(prediction.lower_bound(0.95), lower, places=12)

    def test_fractional_batch_counts_one_shared_future_as_one_unit(self) -> None:
        model = BayesianCausalTransferModel(2, training=True)
        features = np.asarray([[1.0, 0.0], [0.0, 1.0], [0.5, -0.5]])
        targets = np.asarray([0.1, -0.1, 0.05])
        observed = model.observe_batch(
            features,
            targets,
            weights=np.full(3, 1.0 / 3.0),
        )
        self.assertEqual(observed, 3)
        self.assertEqual(model.observation_count, 3)
        self.assertAlmostEqual(model.effective_sample_count, 1.0)
        expected_xx = sum(
            np.outer(row, row) / 3.0 for row in features
        )
        np.testing.assert_allclose(model.sum_xx, expected_xx)

    def test_frozen_observation_and_prediction_are_nonmutating(self) -> None:
        model = BayesianCausalTransferModel(2)
        before = pickle.dumps(model, protocol=5)
        self.assertFalse(model.observe([0.1, 0.2], 0.3))
        self.assertEqual(model.observe_batch([[0.1, 0.2]], [0.3]), 0)
        model.predict([0.1, 0.2])
        self.assertEqual(pickle.dumps(model, protocol=5), before)

    def test_snapshot_round_trip_has_no_aliasing(self) -> None:
        source = BayesianCausalTransferModel(
            2,
            prior_scale=1e-4,
            coordinate_names=("left", "right"),
            training=True,
        )
        source.observe_batch([[0.2, 0.3], [-0.5, 0.8]], [0.02, -0.01])
        snapshot = source.snapshot()
        target = BayesianCausalTransferModel(
            2,
            prior_scale=1e-4,
            coordinate_names=("left", "right"),
        )
        target.load_snapshot(snapshot, freeze=True)
        self.assertEqual(source.posterior_digest(), target.posterior_digest())
        self.assertEqual(source.predict([0.3, -0.2]), target.predict([0.3, -0.2]))
        snapshot["sum_xy"][0] += 1.0
        self.assertNotEqual(snapshot["sum_xy"][0], target.sum_xy[0])

    def test_corruption_rejected_transactionally(self) -> None:
        source = BayesianCausalTransferModel(2, training=True)
        source.observe([0.2, -0.3], 0.1)
        snapshot = source.snapshot()
        target = BayesianCausalTransferModel(2)
        before = pickle.dumps(target, protocol=5)
        corruptions = []
        for field, value in (
            ("schema", "unknown"),
            ("feature_dim", 3),
            ("feature_dim", 2.0),
            ("implementation_version", True),
            ("include_intercept", 0),
            ("effective_sample_count", np.inf),
            ("observation_count", 1.5),
            ("observation_count", 1.0),
            ("sum_yy", -1.0),
            ("posterior_scale", np.nan),
            ("training", "yes"),
        ):
            invalid = copy.deepcopy(snapshot)
            invalid[field] = value
            corruptions.append(invalid)
        invalid_hash = copy.deepcopy(snapshot)
        invalid_hash["sum_xy"][0] += 0.01
        corruptions.append(invalid_hash)
        infeasible = copy.deepcopy(snapshot)
        infeasible["sum_xx"] = -np.eye(2)
        infeasible["array_hashes"]["sum_xx"] = source._array_digest(
            infeasible["sum_xx"]
        )
        corruptions.append(infeasible)
        unknown = copy.deepcopy(snapshot)
        unknown["future_field"] = "must-not-be-ignored"
        corruptions.append(unknown)
        for invalid in corruptions:
            with self.subTest(field=str(invalid)):
                with self.assertRaises((ValueError, FloatingPointError)):
                    target.load_snapshot(invalid)
                self.assertEqual(pickle.dumps(target, protocol=5), before)

    def test_invalid_inputs_are_rejected_without_mutation(self) -> None:
        model = BayesianCausalTransferModel(2, training=True)
        before = pickle.dumps(model, protocol=5)
        calls = (
            lambda: model.observe([0.0], 0.0),
            lambda: model.observe([1.1, 0.0], 0.0),
            lambda: model.observe([0.0, np.nan], 0.0),
            lambda: model.observe([0.0, 0.0], 1.1),
            lambda: model.observe([0.0, 0.0], 0.0, weight=0.0),
            lambda: model.observe_batch([[0.0, 0.0]], [0.0], weights=[2.0]),
        )
        for call in calls:
            with self.assertRaises(ValueError):
                call()
            self.assertEqual(pickle.dumps(model, protocol=5), before)

    def test_deterministic_repeated_training_is_bit_identical(self) -> None:
        first = BayesianCausalTransferModel(3, prior_scale=1e-4, training=True)
        second = BayesianCausalTransferModel(3, prior_scale=1e-4, training=True)
        features = np.asarray([[0.1, 0.2, 0.3], [-0.5, 0.4, 0.2]])
        targets = np.asarray([0.01, -0.02])
        first.observe_batch(features, targets)
        second.observe_batch(features, targets)
        self.assertEqual(pickle.dumps(first, protocol=5), pickle.dumps(second, protocol=5))


if __name__ == "__main__":
    unittest.main()

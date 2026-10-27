import copy
import pickle
import unittest

import numpy as np

from rrct import NonValencedObservationForecaster, RRCTAgent


class ObservationForecasterTests(unittest.TestCase):
    def test_constructor_rejects_nonfinite_nonintegral_and_boolean_scalars(self):
        for invalid in (0, -1, 2.5, np.inf, -np.inf, np.nan, True, "3"):
            with self.subTest(dimension=invalid):
                with self.assertRaises(ValueError):
                    NonValencedObservationForecaster(invalid)
        for invalid in (0.0, -0.1, 2.1, np.inf, -np.inf, np.nan, True, "0.08"):
            with self.subTest(learning_rate=invalid):
                with self.assertRaises(ValueError):
                    NonValencedObservationForecaster(2, learning_rate=invalid)
        with self.assertRaises(ValueError):
            NonValencedObservationForecaster(2, training=1)

    def test_training_freezing_snapshot_and_recursive_forecast(self):
        model = NonValencedObservationForecaster(3, learning_rate=0.08, training=True)
        first = np.asarray([0.2, -0.1, 0.3])
        second = np.asarray([0.3, 0.0, -0.2])
        model.observe(first)
        weights_before = model.weights.copy()
        model.observe(second)
        self.assertEqual(model.learning_steps, 1)
        self.assertFalse(np.array_equal(weights_before, model.weights))
        model.freeze()
        snapshot = model.snapshot()
        frozen_weights = model.weights.copy()
        model.observe(first)
        self.assertTrue(np.array_equal(frozen_weights, model.weights))
        forecast = model.forecast(5)
        self.assertEqual(forecast.shape, (5, 3))
        self.assertTrue(np.all(np.isfinite(forecast)))
        self.assertTrue(np.all(np.abs(forecast) <= 1.0))
        loaded = NonValencedObservationForecaster(3)
        loaded.load_snapshot(snapshot, freeze=True)
        loaded.observe(second)
        model.reset()
        model.observe(second)
        self.assertTrue(np.array_equal(model.forecast(5), loaded.forecast(5)))

    def test_snapshot_metadata_round_trip_and_history_reset(self):
        model = NonValencedObservationForecaster(2, learning_rate=0.3, training=True)
        model.observe([0.1, 0.2])
        model.observe([0.2, 0.4])
        model.freeze()
        snapshot = model.snapshot()
        self.assertEqual(
            snapshot["schema"],
            NonValencedObservationForecaster.SNAPSHOT_SCHEMA,
        )
        self.assertEqual(snapshot["dimension"], 2)
        self.assertEqual(snapshot["model_order"], 1)
        self.assertEqual(snapshot["activation"], "tanh")
        self.assertEqual(snapshot["dtype"], "float64")

        loaded = NonValencedObservationForecaster(
            2,
            learning_rate=1.5,
            training=True,
        )
        loaded.observe([0.8, -0.8])
        loaded.load_snapshot(snapshot, freeze=True)
        self.assertFalse(loaded.training)
        self.assertEqual(loaded.learning_rate, 0.3)
        self.assertEqual(loaded.learning_steps, model.learning_steps)
        self.assertEqual(loaded.observed_count, 0)
        with self.assertRaises(RuntimeError):
            loaded.forecast(1)
        loaded_snapshot = loaded.snapshot()
        self.assertEqual(
            set(snapshot),
            set(loaded_snapshot),
        )
        for field in snapshot:
            if isinstance(snapshot[field], np.ndarray):
                self.assertTrue(
                    np.array_equal(snapshot[field], loaded_snapshot[field])
                )
            else:
                self.assertEqual(snapshot[field], loaded_snapshot[field])

        snapshot["weights"][0, 0] += 1.0
        snapshot["bias"][0] += 1.0
        self.assertFalse(np.array_equal(snapshot["weights"], loaded.weights))
        self.assertFalse(np.array_equal(snapshot["bias"], loaded.bias))

    def test_invalid_snapshot_metadata_is_rejected_transactionally(self):
        source = NonValencedObservationForecaster(2, training=True)
        source.observe([0.1, 0.2])
        source.observe([0.2, 0.3])
        snapshot = source.snapshot()
        target = NonValencedObservationForecaster(2, learning_rate=0.4)
        target.observe([-0.4, 0.5])

        corruptions = (
            ("schema", "unknown"),
            ("dimension", 3),
            ("dimension", np.inf),
            ("model_order", 2),
            ("model_order", 1.5),
            ("activation", "linear"),
            ("update_rule", "unknown"),
            ("normalized_lms_epsilon", np.inf),
            ("normalized_lms_epsilon", 2e-8),
            ("dtype", "float32"),
            ("learning_rate", np.inf),
            ("learning_rate", 0.0),
            ("learning_steps", np.inf),
            ("learning_steps", 1.5),
            ("learning_steps", -1),
            ("learning_steps", True),
            ("weights", np.zeros((2, 3))),
            ("weights", np.full((2, 2), np.nan)),
            ("bias", np.zeros(3)),
            ("bias", np.asarray([0.0, np.inf])),
        )
        for field, value in corruptions:
            with self.subTest(field=field, value=repr(value)):
                invalid = copy.deepcopy(snapshot)
                invalid[field] = value
                before = pickle.dumps(target, protocol=5)
                with self.assertRaises(ValueError):
                    target.load_snapshot(invalid)
                self.assertEqual(pickle.dumps(target, protocol=5), before)

        missing = copy.deepcopy(snapshot)
        missing.pop("weights")
        with self.assertRaises(ValueError):
            target.load_snapshot(missing)
        with self.assertRaises(TypeError):
            target.load_snapshot([])
        with self.assertRaises(ValueError):
            target.load_snapshot(snapshot, freeze=1)

    def test_episode_reset_breaks_temporal_pairing_without_erasing_learning(self):
        model = NonValencedObservationForecaster(2, training=True)
        model.observe([0.1, 0.2])
        model.observe([0.2, 0.3])
        self.assertEqual(model.learning_steps, 1)
        weights = model.weights.copy()
        model.reset()
        model.observe([0.9, -0.9])
        self.assertEqual(model.learning_steps, 1)
        self.assertTrue(np.array_equal(weights, model.weights))

    def test_forecast_is_nonmutating_and_rejects_invalid_inputs(self):
        model = NonValencedObservationForecaster(2)
        with self.assertRaises(RuntimeError):
            model.forecast(2)
        with self.assertRaises(ValueError):
            model.observe([1.0])
        model.observe([0.1, 0.2])
        before = pickle.dumps(model, protocol=5)
        model.forecast(20)
        self.assertEqual(pickle.dumps(model, protocol=5), before)
        for invalid in (0, -1, 2.5, np.inf, -np.inf, np.nan, True, "2"):
            with self.assertRaises((TypeError, ValueError)):
                model.forecast(invalid)

    def test_nonfinite_internal_arithmetic_cannot_corrupt_parameters(self):
        model = NonValencedObservationForecaster(2, training=True)
        model.observe([1e308, -1e308])
        before_weights = model.weights.copy()
        before_bias = model.bias.copy()
        with self.assertRaises(FloatingPointError):
            model.observe([1e308, 1e308])
        self.assertTrue(np.array_equal(model.weights, before_weights))
        self.assertTrue(np.array_equal(model.bias, before_bias))
        self.assertEqual(model.learning_steps, 0)

    def test_forecaster_learning_cannot_change_ordinary_agent_trajectory(self):
        first = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=1901)
        second = copy.deepcopy(first)
        first.observation_forecaster.train()
        observations = [np.sin(np.arange(12) + lag) for lag in range(8)]
        first_steps = [first.step(x) for x in observations]
        second_steps = [second.step(x) for x in observations]
        for left, right in zip(first_steps, second_steps):
            self.assertTrue(
                np.array_equal(left.feature_vector(), right.feature_vector())
            )
            self.assertTrue(np.array_equal(left.action_scores, right.action_scores))
            self.assertTrue(
                np.array_equal(left.resolution_scores, right.resolution_scores)
            )
        self.assertGreater(first.observation_forecaster.learning_steps, 0)
        self.assertEqual(second.observation_forecaster.learning_steps, 0)


if __name__ == "__main__":
    unittest.main()

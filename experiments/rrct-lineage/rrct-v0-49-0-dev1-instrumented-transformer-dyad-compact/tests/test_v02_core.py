import unittest

import numpy as np

from rrct import RRCTAgent, balanced_matrix


class BalancedInitializationTests(unittest.TestCase):
    def test_rectangular_nonzero_singular_values_are_equal(self) -> None:
        for rows, columns in ((9, 4), (4, 9), (6, 6)):
            matrix = balanced_matrix(17, rows, columns, gain=0.7)
            singular_values = np.linalg.svd(matrix, compute_uv=False)
            np.testing.assert_allclose(
                singular_values,
                np.full(min(rows, columns), 0.7),
                atol=1e-12,
                rtol=1e-12,
            )

    def test_initializer_is_seeded_and_validates_gain(self) -> None:
        np.testing.assert_array_equal(
            balanced_matrix(3, 5, 2), balanced_matrix(3, 5, 2)
        )
        for gain in (-1.0, np.inf, np.nan):
            with self.assertRaises(ValueError):
                balanced_matrix(0, 2, 2, gain=gain)


class GainControlTests(unittest.TestCase):
    def test_gain_validation_and_effective_ablation(self) -> None:
        for keyword in ("recurrent_gain", "closure_gain"):
            for value in (-0.1, np.inf, np.nan):
                with self.assertRaises(ValueError):
                    RRCTAgent(6, **{keyword: value})
        agent = RRCTAgent(
            6,
            recurrent_gain=4.0,
            closure_gain=3.0,
            ablations=("recurrence",),
        )
        self.assertEqual(agent.effective_recurrent_gain, 0.0)
        self.assertEqual(agent.effective_closure_gain, 0.0)

    def test_zero_recurrent_gain_exactly_matches_recurrence_ablation(self) -> None:
        zero_gain = RRCTAgent(
            6, seed=21, recurrent_gain=0.0, closure_gain=0.0
        )
        ablated = RRCTAgent(
            6,
            seed=21,
            recurrent_gain=1.7,
            closure_gain=0.0,
            ablations=("recurrence",),
        )
        sequence = np.random.default_rng(22).normal(size=(8, 6))
        for observation in sequence:
            zero_result = zero_gain.step(observation)
            ablated_result = ablated.step(observation)
            np.testing.assert_array_equal(
                zero_result.feature_vector(), ablated_result.feature_vector()
            )

    def test_zero_closure_gain_removes_self_feedback(self) -> None:
        baseline = RRCTAgent(6, seed=23, closure_gain=0.0)
        changed = RRCTAgent(6, seed=23, closure_gain=0.0)
        cue = np.linspace(-1.0, 1.0, 6)
        baseline.step(cue)
        changed.step(cue)
        changed.self_model.state += 0.5
        zero = np.zeros(6)
        np.testing.assert_array_equal(
            baseline.step(zero).workspace,
            changed.step(zero).workspace,
        )


class SelfPredictionLearningTests(unittest.TestCase):
    def _train_agent(self) -> RRCTAgent:
        agent = RRCTAgent(6, seed=31)
        self.assertEqual(agent.self_model_mode, "frozen")
        initial = agent.predictor_snapshot()
        agent.train_self_model()
        sequence = np.random.default_rng(32).normal(size=(12, 6))
        for observation in sequence:
            agent.step(observation)
        learned = agent.predictor_snapshot()
        total_change = np.linalg.norm(
            learned["prediction_weights"] - initial["prediction_weights"]
        ) + np.linalg.norm(learned["workspace_skip"] - initial["workspace_skip"])
        self.assertGreater(float(total_change), 0.0)
        return agent

    def test_learning_is_opt_in_and_ablation_gated(self) -> None:
        frozen = RRCTAgent(6, seed=30)
        initial = frozen.predictor_snapshot()
        for observation in np.eye(6):
            frozen.step(observation)
        final = frozen.predictor_snapshot()
        np.testing.assert_array_equal(
            initial["prediction_weights"], final["prediction_weights"]
        )
        np.testing.assert_array_equal(
            initial["workspace_skip"], final["workspace_skip"]
        )
        self.assertEqual(frozen.self_learning_updates, 0)

        disabled = RRCTAgent(
            6,
            seed=30,
            self_model_mode="train",
            ablations=("self_model",),
        )
        for observation in np.eye(6):
            disabled.step(observation)
        self.assertEqual(disabled.self_learning_updates, 0)

    def test_freeze_and_reset_preserve_learned_parameters(self) -> None:
        agent = self._train_agent()
        self.assertGreater(agent.self_learning_updates, 0)
        agent.freeze_self_model()
        learned = agent.predictor_snapshot()
        update_count = agent.self_learning_updates
        agent.reset()
        for observation in np.eye(6):
            agent.step(observation)
        held_out = agent.predictor_snapshot()
        self.assertEqual(agent.self_model_mode, "frozen")
        self.assertEqual(agent.self_learning_updates, update_count)
        np.testing.assert_array_equal(
            learned["prediction_weights"], held_out["prediction_weights"]
        )
        np.testing.assert_array_equal(
            learned["workspace_skip"], held_out["workspace_skip"]
        )

    def test_seeded_rebuild_erases_learning(self) -> None:
        agent = RRCTAgent(6, seed=33)
        initial = agent.predictor_snapshot()
        agent.train_self_model()
        for observation in np.random.default_rng(34).normal(size=(10, 6)):
            agent.step(observation)
        self.assertGreater(agent.self_learning_updates, 0)
        agent.freeze_self_model()
        agent.reset(seed=33)
        rebuilt = agent.predictor_snapshot()
        self.assertEqual(agent.self_learning_updates, 0)
        np.testing.assert_array_equal(
            initial["prediction_weights"], rebuilt["prediction_weights"]
        )
        np.testing.assert_array_equal(
            initial["workspace_skip"], rebuilt["workspace_skip"]
        )

    def test_snapshot_loading_supports_exact_matched_traces(self) -> None:
        source = self._train_agent()
        source.freeze_self_model()
        predictor = source.predictor_snapshot()

        first = RRCTAgent(6, seed=35)
        second = RRCTAgent(6, seed=35)
        first.load_predictor_snapshot(predictor)
        second.load_predictor_snapshot(predictor)
        sequence = np.random.default_rng(36).normal(size=(7, 6))
        for observation in sequence:
            np.testing.assert_array_equal(
                first.step(observation).feature_vector(),
                second.step(observation).feature_vector(),
            )
        self.assertEqual(first.self_model_mode, "frozen")
        self.assertEqual(first.self_learning_updates, source.self_learning_updates)

    def test_learning_reduces_error_on_a_predictable_heldout_trace(self) -> None:
        generator = np.random.default_rng(123)
        motif = generator.normal(size=(10, 6))
        training_trace = np.tile(motif, (20, 1))
        heldout_trace = np.tile(motif, (10, 1))

        trained = RRCTAgent(6, seed=55, self_model_mode="train")
        for observation in training_trace:
            trained.step(observation)
        trained.freeze_self_model()
        trained.reset()

        untrained = RRCTAgent(6, seed=55, self_model_mode="frozen")

        def prediction_rmse(agent: RRCTAgent) -> float:
            predictions = []
            targets = []
            for observation in heldout_trace:
                result = agent.step(observation)
                predictions.append(result.predicted_workspace)
                targets.append(result.workspace)
            return float(
                np.sqrt(
                    np.mean(
                        np.square(
                            np.asarray(predictions) - np.asarray(targets)
                        )
                    )
                )
            )

        self.assertLess(prediction_rmse(trained), prediction_rmse(untrained))


if __name__ == "__main__":
    unittest.main()

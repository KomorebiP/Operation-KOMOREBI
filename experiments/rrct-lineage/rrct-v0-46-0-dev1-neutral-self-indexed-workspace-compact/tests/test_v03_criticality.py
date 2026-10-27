import unittest

import numpy as np

from rrct import (
    RRCTAgent,
    WidestPathClosureDetails,
    hysteresis_area,
    interaction_residual,
    is_strongly_connected,
    max_slope_interval,
    widest_path_closure_details,
    widest_path_closure_strength,
)


class WidestPathClosureTests(unittest.TestCase):
    def test_details_preserve_full_capacity_and_weakest_pair(self) -> None:
        effects = np.asarray(
            [
                [0.0, 0.8, 0.1],
                [0.2, 0.0, 0.6],
                [0.4, 0.3, 0.0],
            ]
        )
        details = widest_path_closure_details(effects, normalize=0.8)
        self.assertIsInstance(details, WidestPathClosureDetails)
        self.assertEqual(details.strength, 0.5)
        self.assertEqual(details.normalized_strength, 0.5)
        self.assertEqual(details.raw_strength, 0.4)
        self.assertEqual(details.normalization, 0.8)
        self.assertEqual(details.weakest_pair, (1, 0))
        np.testing.assert_array_equal(
            details.capacity_matrix,
            np.asarray(
                [
                    [0.0, 0.8, 0.6],
                    [0.4, 0.0, 0.6],
                    [0.4, 0.4, 0.0],
                ]
            ),
        )
        self.assertFalse(details.capacity_matrix.flags.writeable)
        with self.assertRaises(ValueError):
            details.capacity_matrix[0, 1] = 0.0
        with self.assertRaises(ValueError):
            details.capacity_matrix.setflags(write=True)
        with self.assertRaises(AttributeError):
            details.raw_strength = 0.0

    def test_weakest_pair_ties_use_lexicographic_order(self) -> None:
        cycle = np.asarray(
            [
                [0.0, 0.5, 0.0],
                [0.0, 0.0, 0.5],
                [0.5, 0.0, 0.0],
            ]
        )
        details = widest_path_closure_details(cycle)
        self.assertEqual(details.weakest_pair, (0, 1))
        self.assertEqual(details.raw_strength, 0.5)
        expected = np.full((3, 3), 0.5)
        np.fill_diagonal(expected, 0.0)
        np.testing.assert_array_equal(details.capacity_matrix, expected)

    def test_scalar_api_delegates_exactly_to_details(self) -> None:
        effects = np.random.default_rng(71).uniform(0.0, 1.0, size=(5, 5))
        np.fill_diagonal(effects, 0.0)
        details = widest_path_closure_details(effects, normalize=0.35)
        self.assertEqual(
            widest_path_closure_strength(effects, normalize=0.35),
            details.strength,
        )

    def test_directed_max_min_closure_and_normalization(self) -> None:
        effects = np.asarray(
            [
                [0.0, 0.8, 0.1],
                [0.2, 0.0, 0.6],
                [0.4, 0.3, 0.0],
            ]
        )
        self.assertAlmostEqual(widest_path_closure_strength(effects), 0.4)
        self.assertAlmostEqual(
            widest_path_closure_strength(effects, normalize=0.8), 0.5
        )

    def test_disconnected_pair_forces_zero_and_diagonal_is_ignored(self) -> None:
        disconnected = np.asarray([[100.0, 0.7], [0.0, 200.0]])
        self.assertEqual(widest_path_closure_strength(disconnected), 0.0)

    def test_raw_strength_is_the_continuous_scc_threshold_margin(self) -> None:
        effects = np.asarray(
            [
                [0.0, 0.8, 0.1],
                [0.2, 0.0, 0.6],
                [0.4, 0.3, 0.0],
            ]
        )
        strength = widest_path_closure_strength(effects)
        for threshold in (0.05, 0.25, 0.35, 0.45, 0.7):
            self.assertEqual(
                is_strongly_connected(effects > threshold),
                strength > threshold,
            )

    def test_invalid_effect_matrices_and_normalizers_are_rejected(self) -> None:
        invalid_matrices = (
            np.zeros((2, 3)),
            np.zeros((1, 1)),
            np.asarray([[0.0, -0.1], [0.2, 0.0]]),
            np.asarray([[0.0, np.nan], [0.2, 0.0]]),
            np.asarray([0.0, 1.0]),
        )
        for effects in invalid_matrices:
            with self.assertRaises(ValueError):
                widest_path_closure_strength(effects)
            with self.assertRaises(ValueError):
                widest_path_closure_details(effects)
        for normalize in (0.0, -1.0, np.inf, np.nan):
            with self.assertRaises(ValueError):
                widest_path_closure_strength(np.ones((2, 2)), normalize=normalize)
            with self.assertRaises(ValueError):
                widest_path_closure_details(np.ones((2, 2)), normalize=normalize)


class SurfaceAndRampTests(unittest.TestCase):
    def test_interaction_residual_removes_additive_baselines(self) -> None:
        rows = np.asarray([0.0, 1.0, 2.0])
        columns = np.asarray([0.0, 3.0, 5.0, 8.0])
        additive = rows[:, None] + columns[None, :]
        np.testing.assert_array_equal(
            interaction_residual(additive), np.zeros_like(additive)
        )
        interaction = rows[:, None] * columns[None, :]
        surface = additive + interaction
        np.testing.assert_allclose(interaction_residual(surface), interaction)

    def test_interaction_residual_validates_shape_and_finiteness(self) -> None:
        for surface in (
            np.asarray([1.0, 2.0]),
            np.empty((0, 2)),
            np.asarray([[1.0, np.inf]]),
        ):
            with self.assertRaises(ValueError):
                interaction_residual(surface)

    def test_hysteresis_area_sorts_paired_unique_gains(self) -> None:
        gains = np.asarray([2.0, 0.0, 1.0])
        upward = np.asarray([2.0, 0.0, 1.0])
        downward = np.zeros(3)
        self.assertAlmostEqual(
            hysteresis_area(gains, upward, downward, normalize=False), 2.0
        )
        self.assertAlmostEqual(hysteresis_area(gains, upward, downward), 0.5)

    def test_hysteresis_degenerate_cases_safely_return_zero(self) -> None:
        self.assertEqual(hysteresis_area([1.0], [2.0], [3.0]), 0.0)
        self.assertEqual(
            hysteresis_area([0.0, 1.0], [2.0, 2.0], [2.0, 2.0]), 0.0
        )

    def test_hysteresis_rejects_ambiguous_or_nonfinite_series(self) -> None:
        invalid = (
            ([0.0, 0.0], [0.0, 1.0], [0.0, 1.0]),
            ([0.0, 1.0], [0.0], [0.0, 1.0]),
            ([0.0, np.nan], [0.0, 1.0], [0.0, 1.0]),
            ([], [], []),
        )
        for gains, upward, downward in invalid:
            with self.assertRaises(ValueError):
                hysteresis_area(gains, upward, downward)

    def test_max_slope_interval_sorts_and_returns_signed_slope(self) -> None:
        interval, slope = max_slope_interval(
            [2.0, 0.0, 1.0, 3.0],
            [5.0, 0.0, 1.0, 4.0],
        )
        self.assertEqual(interval, (1.0, 2.0))
        self.assertEqual(slope, 4.0)

        interval, slope = max_slope_interval([0.0, 1.0, 2.0], [0.0, -3.0, -2.0])
        self.assertEqual(interval, (0.0, 1.0))
        self.assertEqual(slope, -3.0)

    def test_max_slope_rejects_insufficient_or_ambiguous_series(self) -> None:
        invalid = (
            ([0.0], [1.0]),
            ([0.0, 0.0], [1.0, 2.0]),
            ([0.0, 1.0], [1.0]),
            ([0.0, 1.0], [1.0, np.inf]),
        )
        for gains, response in invalid:
            with self.assertRaises(ValueError):
                max_slope_interval(gains, response)


class AgentGainSetterTests(unittest.TestCase):
    def _trained_agent(self) -> RRCTAgent:
        agent = RRCTAgent(6, seed=51)
        agent.train_self_model()
        for observation in np.random.default_rng(52).normal(size=(6, 6)):
            agent.step(observation)
        agent.freeze_self_model()
        return agent

    def test_invalid_gain_update_is_atomic(self) -> None:
        agent = RRCTAgent(6, recurrent_gain=0.7, closure_gain=0.8)
        for recurrent, closure in (
            (-1.0, 1.0),
            (1.0, -1.0),
            (np.inf, 1.0),
            (1.0, np.nan),
        ):
            with self.assertRaises(ValueError):
                agent.set_gains(recurrent, closure)
            self.assertEqual(agent.recurrent_gain, 0.7)
            self.assertEqual(agent.closure_gain, 0.8)

    def test_reset_false_preserves_dynamic_and_learned_state(self) -> None:
        agent = self._trained_agent()
        before = agent.snapshot()
        predictor_before = agent.predictor_snapshot()
        agent.set_gains(0.4, 1.3, reset=False)
        after = agent.snapshot()
        predictor_after = agent.predictor_snapshot()

        self.assertEqual(after["time"], before["time"])
        np.testing.assert_array_equal(after["workspace"], before["workspace"])
        np.testing.assert_array_equal(after["self_state"], before["self_state"])
        np.testing.assert_array_equal(after["last_action"], before["last_action"])
        np.testing.assert_array_equal(
            after["memory"]["items"], before["memory"]["items"]
        )
        np.testing.assert_array_equal(
            predictor_after["prediction_weights"],
            predictor_before["prediction_weights"],
        )
        np.testing.assert_array_equal(
            predictor_after["workspace_skip"], predictor_before["workspace_skip"]
        )
        self.assertEqual(agent.self_learning_updates, before["self_learning_updates"])
        self.assertEqual(agent.self_model_mode, "frozen")

    def test_reset_true_clears_dynamics_but_retains_learning(self) -> None:
        agent = self._trained_agent()
        predictor_before = agent.predictor_snapshot()
        updates = agent.self_learning_updates
        agent.set_gains(0.2, 0.3)

        self.assertEqual(agent.time, 0)
        np.testing.assert_array_equal(agent.workspace.state, np.zeros(agent.workspace_dim))
        np.testing.assert_array_equal(agent.self_model.state, np.zeros(agent.self_dim))
        self.assertEqual(len(agent.memory), 0)
        predictor_after = agent.predictor_snapshot()
        np.testing.assert_array_equal(
            predictor_after["prediction_weights"],
            predictor_before["prediction_weights"],
        )
        np.testing.assert_array_equal(
            predictor_after["workspace_skip"], predictor_before["workspace_skip"]
        )
        self.assertEqual(agent.self_learning_updates, updates)
        self.assertEqual(agent.self_model_mode, "frozen")


if __name__ == "__main__":
    unittest.main()

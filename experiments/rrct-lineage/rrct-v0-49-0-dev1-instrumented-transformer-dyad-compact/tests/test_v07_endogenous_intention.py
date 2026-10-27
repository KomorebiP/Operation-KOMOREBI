import pickle
import unittest

import numpy as np

from rrct import RRCTAgent


class EndogenousSelfIntentionTests(unittest.TestCase):
    """Contract tests for bounded, internally generated self intentions."""

    @staticmethod
    def _agent(*, seed: int = 1701, ablations=()) -> RRCTAgent:
        agent = RRCTAgent(
            12,
            projector_ranks=(3, 6, 9, 12),
            seed=seed,
            ablations=ablations,
        )
        coordinates = np.arange(12, dtype=np.float64)
        for lag in range(7):
            agent.step(
                np.sin(coordinates * 0.31 + lag * 0.47),
                source="v07_intention_prime",
            )
        return agent

    @staticmethod
    def _assert_step_equal(first, second) -> None:
        self_fields = (
            "observation",
            "workspace",
            "self_state",
            "predicted_workspace",
            "prediction_error",
            "action",
            "action_scores",
            "resolution_scores",
        )
        for field in self_fields:
            np.testing.assert_array_equal(
                getattr(first, field),
                getattr(second, field),
            )
        assert first.time == second.time
        assert first.next_resolution_level == second.next_resolution_level
        assert first.selected_specialists == second.selected_specialists

    def test_endogenous_plan_is_exactly_deterministic_for_matched_agents(self) -> None:
        first_agent = self._agent(seed=1702)
        second_agent = self._agent(seed=1702)

        first = first_agent.execute_endogenous_self_intention()
        second = second_agent.execute_endogenous_self_intention()

        self.assertEqual(first.candidate_count, second.candidate_count)
        self.assertEqual(first.queried_count, second.queried_count)
        np.testing.assert_array_equal(first.selected_delta, second.selected_delta)
        np.testing.assert_array_equal(
            first.forecast_observations,
            second.forecast_observations,
        )
        for field in (
            "predicted_baseline_error",
            "predicted_selected_error",
            "realized_baseline_error",
            "realized_selected_error",
            "realized_improvement",
            "prediction_error",
        ):
            self.assertEqual(getattr(first, field), getattr(second, field))
        self.assertEqual(len(first.realized_steps), len(second.realized_steps))
        for first_step, second_step in zip(
            first.realized_steps, second.realized_steps
        ):
            self._assert_step_equal(first_step, second_step)

    def test_candidates_forecast_and_objective_are_generated_internally(self) -> None:
        agent = self._agent(seed=1703)
        plan = agent.execute_endogenous_self_intention(
            horizon=4,
            query_budget=8,
            candidate_magnitude=0.35,
        )

        self.assertGreaterEqual(plan.candidate_count, 2)
        self.assertGreaterEqual(plan.candidate_count, plan.queried_count)
        self.assertEqual(plan.queried_count, min(8, plan.candidate_count))
        self.assertEqual(np.asarray(plan.selected_delta).shape, (agent.self_dim,))
        self.assertEqual(
            np.asarray(plan.forecast_observations).shape,
            (4, agent.observation_dim),
        )
        self.assertEqual(len(plan.realized_steps), 4)
        self.assertTrue(np.all(np.isfinite(plan.forecast_observations)))
        self.assertLessEqual(
            plan.predicted_selected_error,
            plan.predicted_baseline_error + 1e-12,
        )

    def test_query_budget_is_a_hard_cap_and_invalid_budgets_are_rejected(self) -> None:
        for budget in (2, 3, 8, 24, 25):
            plan = self._agent(seed=1710 + budget).execute_endogenous_self_intention(
                horizon=2,
                query_budget=budget,
            )
            self.assertEqual(
                plan.queried_count,
                min(budget, plan.candidate_count),
            )
            self.assertLessEqual(plan.queried_count, budget)

        for invalid in (0, 1, 26, -1, 2.5, np.nan, np.inf):
            with self.assertRaises((TypeError, ValueError)):
                self._agent(seed=1721).execute_endogenous_self_intention(
                    query_budget=invalid
                )

    def test_selected_intervention_and_every_retained_value_remain_bounded(self) -> None:
        magnitude = 0.2
        plan = self._agent(seed=1730).execute_endogenous_self_intention(
            horizon=4,
            query_budget=8,
            candidate_magnitude=magnitude,
        )

        selected_delta = np.asarray(plan.selected_delta, dtype=np.float64)
        self.assertTrue(np.all(np.isfinite(selected_delta)))
        self.assertLessEqual(np.linalg.norm(selected_delta), magnitude + 1e-12)
        for field in (
            "predicted_baseline_error",
            "predicted_selected_error",
            "realized_baseline_error",
            "realized_selected_error",
            "realized_improvement",
            "prediction_error",
        ):
            self.assertTrue(np.isfinite(getattr(plan, field)), field)
        for field in (
            "predicted_baseline_error",
            "predicted_selected_error",
            "realized_baseline_error",
            "realized_selected_error",
            "prediction_error",
        ):
            self.assertGreaterEqual(getattr(plan, field), 0.0, field)
        for step in plan.realized_steps:
            for values in (
                step.workspace,
                step.self_state,
                step.action,
                step.prediction_error,
            ):
                self.assertTrue(np.all(np.isfinite(values)))

        for invalid in (0.0, -0.1, 0.500001, np.nan, np.inf):
            with self.assertRaises(ValueError):
                self._agent(seed=1731).execute_endogenous_self_intention(
                    candidate_magnitude=invalid
                )
        for invalid in (0, -1, 2.5):
            with self.assertRaises((TypeError, ValueError)):
                self._agent(seed=1732).execute_endogenous_self_intention(
                    horizon=invalid
                )

    def test_selected_intention_is_committed_to_the_live_agent(self) -> None:
        agent = self._agent(seed=1740)
        time_before = agent.time
        plan = agent.execute_endogenous_self_intention(
            horizon=4,
            query_budget=8,
            candidate_magnitude=0.35,
        )

        self.assertEqual(agent.time, time_before + 4)
        self.assertEqual(len(plan.realized_steps), 4)
        self.assertIs(agent.last_result, plan.realized_steps[-1])
        np.testing.assert_array_equal(
            agent.last_result.workspace,
            plan.realized_steps[-1].workspace,
        )
        np.testing.assert_array_equal(
            agent.last_result.self_state,
            plan.realized_steps[-1].self_state,
        )
        self.assertAlmostEqual(
            plan.realized_improvement,
            plan.realized_baseline_error - plan.realized_selected_error,
        )
        self.assertEqual(plan.prediction_error, 0.0)
        self.assertAlmostEqual(
            plan.realized_baseline_error,
            plan.predicted_baseline_error,
        )
        self.assertAlmostEqual(
            plan.realized_selected_error,
            plan.predicted_selected_error,
        )

    def test_unseen_realized_future_is_retained_and_forecast_error_is_auditable(self) -> None:
        agent = self._agent(seed=1750)
        realized = np.asarray(
            [
                np.linspace(-0.35, 0.45, 12) * (lag + 1)
                + 0.1 * np.cos(np.arange(12) + lag)
                for lag in range(4)
            ],
            dtype=np.float64,
        )
        plan = agent.execute_endogenous_self_intention(
            horizon=4,
            query_budget=8,
            candidate_magnitude=0.35,
            realized_observations=realized,
        )

        forecast = np.asarray(plan.forecast_observations, dtype=np.float64)
        self.assertEqual(forecast.shape, realized.shape)
        self.assertFalse(np.array_equal(forecast, realized))
        self.assertEqual(len(plan.realized_steps), len(realized))
        for step, observation in zip(plan.realized_steps, realized):
            np.testing.assert_array_equal(step.observation, observation)
        self.assertGreater(plan.prediction_error, 0.0)
        self.assertAlmostEqual(
            plan.realized_improvement,
            plan.realized_baseline_error - plan.realized_selected_error,
        )

        shorter = self._agent(seed=1751).execute_endogenous_self_intention(
            horizon=4,
            realized_observations=realized[:-1],
        )
        self.assertEqual(np.asarray(shorter.forecast_observations).shape[0], 4)
        self.assertEqual(len(shorter.realized_steps), 3)
        with self.assertRaises(ValueError):
            self._agent(seed=1752).execute_endogenous_self_intention(
                horizon=4,
                realized_observations=[],
            )

    def test_self_ablation_eliminates_intention_specific_improvement(self) -> None:
        agent = self._agent(seed=1760, ablations=("self_model",))
        time_before = agent.time
        plan = agent.execute_endogenous_self_intention(
            horizon=4,
            query_budget=8,
            candidate_magnitude=0.35,
        )

        self.assertEqual(agent.time, time_before + 4)
        self.assertEqual(plan.queried_count, min(8, plan.candidate_count))
        self.assertAlmostEqual(
            plan.predicted_selected_error,
            plan.predicted_baseline_error,
        )
        self.assertAlmostEqual(
            plan.realized_selected_error,
            plan.realized_baseline_error,
        )
        self.assertAlmostEqual(plan.realized_improvement, 0.0)
        self.assertEqual(plan.prediction_error, 0.0)

    def test_plan_is_pure_commit_is_guarded_and_evaluation_is_transactional(self) -> None:
        agent = self._agent(seed=1770)
        before = pickle.dumps(agent, protocol=5)
        plan = agent.plan_endogenous_self_intention(horizon=4, query_budget=4)
        self.assertEqual(pickle.dumps(agent, protocol=5), before)
        self.assertEqual(len(plan.queries), 4)
        self.assertEqual(plan.candidate_deltas.shape, (25, 12))
        self.assertEqual(plan.proxy_scores.shape, (25,))

        stale = self._agent(seed=1771)
        stale_plan = stale.plan_endogenous_self_intention()
        stale.step(np.zeros(12))
        with self.assertRaises(RuntimeError):
            stale.commit_endogenous_self_intention(stale_plan)

        receipt = agent.commit_endogenous_self_intention(plan)
        committed = pickle.dumps(agent, protocol=5)
        with self.assertRaises(ValueError):
            agent.evaluate_committed_intention(receipt, [])
        self.assertEqual(pickle.dumps(agent, protocol=5), committed)
        evaluation = agent.evaluate_committed_intention(
            receipt, np.ones((4, 12), dtype=np.float64) * 0.1
        )
        self.assertEqual(len(evaluation.realized_steps), 4)

    def test_hidden_future_cannot_change_any_precommit_field(self) -> None:
        first = self._agent(seed=1780)
        second = self._agent(seed=1780)
        plan_a = first.plan_endogenous_self_intention(horizon=4, query_budget=4)
        plan_b = second.plan_endogenous_self_intention(horizon=4, query_budget=4)
        self.assertEqual(plan_a.state_digest, plan_b.state_digest)
        self.assertEqual(plan_a.selected_index, plan_b.selected_index)
        self.assertEqual(plan_a.queried_indices, plan_b.queried_indices)
        np.testing.assert_array_equal(plan_a.selected_delta, plan_b.selected_delta)
        np.testing.assert_array_equal(plan_a.forecast_observations, plan_b.forecast_observations)
        receipt_a = first.commit_endogenous_self_intention(plan_a)
        receipt_b = second.commit_endogenous_self_intention(plan_b)
        first.evaluate_committed_intention(receipt_a, np.zeros((4, 12)))
        second.evaluate_committed_intention(receipt_b, np.ones((4, 12)))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

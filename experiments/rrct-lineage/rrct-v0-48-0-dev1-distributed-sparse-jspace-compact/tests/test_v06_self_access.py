import unittest

import numpy as np

from rrct import RRCTAgent


class ProspectiveSelfAccessTests(unittest.TestCase):
    def _agent(self, *, ablations=()):
        agent = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=1601, ablations=ablations)
        for lag in range(7):
            agent.step(np.sin(np.arange(12) + lag))
        return agent

    def test_query_is_deterministic_and_does_not_mutate_live_state(self):
        agent = self._agent()
        before = agent.snapshot()
        delta = np.eye(12)[0] * 0.35
        future = [np.zeros(12) for _ in range(5)]
        first = agent.counterfactual_self_query(delta, future)
        second = agent.counterfactual_self_query(delta, future)
        after = agent.snapshot()
        self.assertTrue(np.array_equal(first.workspace_delta, second.workspace_delta))
        self.assertGreater(first.response_norm, 0.0)
        self.assertEqual(before["time"], after["time"])
        self.assertTrue(np.array_equal(before["workspace"], after["workspace"]))
        self.assertTrue(np.array_equal(before["self_state"], after["self_state"]))

    def test_self_ablation_removes_queried_self_response(self):
        agent = self._agent(ablations=("self_model",))
        query = agent.counterfactual_self_query(np.eye(12)[0] * 0.35, [np.zeros(12)] * 4)
        self.assertEqual(query.response_norm, 0.0)

    def test_selection_matches_exhaustive_prospective_scores(self):
        agent = self._agent()
        candidates = [np.eye(12)[i] * sign * 0.35 for i in range(3) for sign in (1, -1)]
        objective = np.linspace(-1.0, 1.0, 16)
        selected, scores, queries = agent.select_self_counterfactual(
            candidates, [np.zeros(12)] * 4, objective
        )
        self.assertEqual(selected, int(np.argmax(scores)))
        self.assertEqual(len(queries), len(candidates))
        self.assertTrue(all(np.isfinite(scores)))

    def test_execution_commits_selected_future_and_audits_exact_prediction(self):
        agent = self._agent()
        candidates = [np.eye(12)[i] * sign * 0.35 for i in range(3) for sign in (1, -1)]
        objective = np.linspace(-1.0, 1.0, 16)
        time_before = agent.snapshot()["time"]
        plan = agent.execute_self_counterfactual(
            candidates, [np.zeros(12)] * 4, objective
        )
        self.assertEqual(plan.selected_index, int(np.argmax(plan.predicted_scores)))
        self.assertEqual(plan.prediction_error, 0.0)
        self.assertEqual(plan.realized_score, plan.predicted_score)
        self.assertEqual(agent.snapshot()["time"], time_before + 4)
        self.assertTrue(np.array_equal(plan.realized_steps[-1].workspace, plan.query.intervened_workspace[-1]))

    def test_execution_enforces_nonvalenced_intervention_bound(self):
        agent = self._agent()
        with self.assertRaises(ValueError):
            agent.execute_self_counterfactual(
                [np.ones(12)], [np.zeros(12)], np.zeros(16), max_delta_norm=0.5
            )

    def test_unseen_realized_future_produces_auditable_forecast_error(self):
        agent = self._agent()
        candidates = [np.eye(12)[i] * sign * 0.35 for i in range(3) for sign in (1, -1)]
        forecast = [np.zeros(12)] * 4
        realized = [np.linspace(-0.2, 0.3, 12) * (lag + 1) for lag in range(4)]
        plan = agent.execute_self_counterfactual(
            candidates,
            forecast,
            np.linspace(-1.0, 1.0, 16),
            realized_observations=realized,
        )
        self.assertGreater(plan.prediction_error, 0.0)

    def test_selector_materializes_one_shot_future_once(self):
        agent = self._agent()
        future = (np.zeros(12) for _ in range(4))
        candidates = [np.eye(12)[0] * 0.35, -np.eye(12)[0] * 0.35]
        _, _, queries = agent.select_self_counterfactual(
            candidates, future, np.ones(16)
        )
        self.assertEqual(queries[0].baseline_workspace.shape[0], 4)
        self.assertEqual(queries[1].baseline_workspace.shape[0], 4)

    def test_invalid_queries_are_rejected(self):
        agent = self._agent()
        with self.assertRaises(ValueError):
            agent.counterfactual_self_query(np.zeros(11), [np.zeros(12)])
        with self.assertRaises(ValueError):
            agent.counterfactual_self_query(np.zeros(12), [])
        with self.assertRaises(ValueError):
            agent.select_self_counterfactual([], [np.zeros(12)], np.zeros(16))


if __name__ == "__main__":
    unittest.main()

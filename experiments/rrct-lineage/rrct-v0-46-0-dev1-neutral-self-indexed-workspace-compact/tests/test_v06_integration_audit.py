import pickle
import unittest

import numpy as np

from rrct import RRCTAgent


class V06SelfCounterfactualIntegrationAuditTests(unittest.TestCase):
    """Integration guards for the prospective self-query API."""

    def _agent(self, **overrides):
        options = {
            "projector_ranks": (3, 6, 9, 12),
            "seed": 1601,
        }
        options.update(overrides)
        agent = RRCTAgent(12, **options)
        for lag in range(7):
            agent.step(np.sin(np.arange(12, dtype=np.float64) + lag))
        return agent

    @staticmethod
    def _candidates():
        basis = np.eye(12, dtype=np.float64)
        return [basis[index] * sign * 0.35 for index in range(3) for sign in (1, -1)]

    def test_query_and_selector_do_not_mutate_complete_live_training_agent(self):
        # Training mode is the stronger case: simulated branches update their
        # copied predictors, but no update may escape into the live object.
        agent = self._agent(self_model_mode="train")
        before = pickle.dumps(agent, protocol=5)
        future = [np.linspace(-0.3, 0.4, 12) for _ in range(4)]

        agent.counterfactual_self_query(self._candidates()[0], future)
        agent.select_self_counterfactual(
            self._candidates(), future, np.linspace(-1.0, 1.0, 16)
        )

        self.assertEqual(pickle.dumps(agent, protocol=5), before)

    def test_zero_delta_is_an_exact_paired_identity(self):
        agent = self._agent()
        query = agent.counterfactual_self_query(
            np.zeros(12), [np.zeros(12) for _ in range(5)]
        )

        self.assertTrue(np.array_equal(query.baseline_workspace, query.intervened_workspace))
        self.assertTrue(np.array_equal(query.workspace_delta, np.zeros_like(query.workspace_delta)))
        self.assertTrue(np.array_equal(query.baseline_actions, query.intervened_actions))
        self.assertTrue(np.array_equal(query.action_delta, np.zeros_like(query.action_delta)))
        self.assertEqual(query.baseline_resolutions, query.intervened_resolutions)
        self.assertEqual(query.response_norm, 0.0)

    def test_selector_keeps_candidate_baselines_matched_and_scores_as_documented(self):
        agent = self._agent()
        objective = np.linspace(-1.0, 1.0, 16)
        selected, scores, queries = agent.select_self_counterfactual(
            self._candidates(), [np.zeros(12)] * 4, objective
        )

        for query in queries[1:]:
            self.assertTrue(np.array_equal(query.baseline_workspace, queries[0].baseline_workspace))
            self.assertTrue(np.array_equal(query.baseline_actions, queries[0].baseline_actions))
            self.assertEqual(query.baseline_resolutions, queries[0].baseline_resolutions)
        expected = tuple(float(query.intervened_workspace[-1] @ objective) for query in queries)
        self.assertEqual(scores, expected)
        self.assertEqual(selected, int(np.argmax(expected)))

    def test_query_outputs_do_not_alias_caller_arrays(self):
        agent = self._agent()
        delta = self._candidates()[0]
        observation = np.linspace(-0.5, 0.5, 12)
        query = agent.counterfactual_self_query(delta, [observation])
        saved_delta = query.self_delta.copy()
        saved_baseline = query.baseline_workspace.copy()

        delta[:] = 99.0
        observation[:] = -99.0

        self.assertTrue(np.array_equal(query.self_delta, saved_delta))
        self.assertTrue(np.array_equal(query.baseline_workspace, saved_baseline))
        self.assertFalse(np.shares_memory(query.self_delta, delta))
        self.assertFalse(np.shares_memory(query.baseline_workspace, observation))
        self.assertFalse(np.shares_memory(query.workspace_delta, query.baseline_workspace))

    def test_workspace_response_norm_can_miss_a_real_action_response(self):
        # With both explicit feedback paths off, the queried self state still
        # enters the controller.  For this deterministic trace it changes the
        # action while leaving every reported workspace exactly unchanged.
        agent = self._agent(self_feedback_gain=0.0, action_feedback_gain=0.0)
        query = agent.counterfactual_self_query(
            self._candidates()[0], [np.zeros(12)] * 6
        )

        self.assertEqual(query.response_norm, 0.0)
        self.assertGreater(float(np.linalg.norm(query.action_delta)), 0.0)

    def test_selection_is_explicitly_dependent_on_supplied_future_observations(self):
        agent = self._agent()
        objective = np.linspace(-1.0, 1.0, 16)
        rng = np.random.default_rng(991)
        futures = [rng.normal(size=(4, 12)) for _ in range(10)]

        first = agent.select_self_counterfactual(self._candidates(), futures[0], objective)[0]
        later = agent.select_self_counterfactual(self._candidates(), futures[9], objective)[0]

        self.assertNotEqual(first, later)

    def test_zero_objective_reveals_directional_score_and_first_tie_break(self):
        agent = self._agent()
        candidates = self._candidates()
        selected, scores, queries = agent.select_self_counterfactual(
            candidates, [np.zeros(12)] * 4, np.zeros(16)
        )

        self.assertEqual(scores, (0.0,) * len(candidates))
        self.assertEqual(selected, 0)
        terminal_norms = [float(np.linalg.norm(query.intervened_workspace[-1])) for query in queries]
        self.assertGreater(max(terminal_norms) - min(terminal_norms), 0.0)

        reversed_selected, reversed_scores, _ = agent.select_self_counterfactual(
            list(reversed(candidates)), [np.zeros(12)] * 4, np.zeros(16)
        )
        self.assertEqual(reversed_scores, (0.0,) * len(candidates))
        self.assertEqual(reversed_selected, 0)
        self.assertFalse(np.array_equal(candidates[selected], list(reversed(candidates))[reversed_selected]))


if __name__ == "__main__":
    unittest.main()

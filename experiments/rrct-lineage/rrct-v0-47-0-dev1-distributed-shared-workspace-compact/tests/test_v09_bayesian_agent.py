import copy
import pickle
import unittest

import numpy as np

from rrct import RRCTAgent


class BayesianTransferAgentTests(unittest.TestCase):
    @staticmethod
    def _agent(seed: int = 2203) -> RRCTAgent:
        agent = RRCTAgent(
            12,
            projector_ranks=(3, 6, 9, 12),
            seed=seed,
            self_model_mode="frozen",
        )
        coordinates = np.arange(12, dtype=np.float64)
        for lag in range(8):
            agent.step(
                np.sin(coordinates * 0.31 + lag * 0.47),
                source="v09_bayesian_prime",
            )
        return agent

    @staticmethod
    def _future(offset: float = 0.0) -> np.ndarray:
        coordinates = np.arange(12, dtype=np.float64)
        return np.stack(
            [np.sin(coordinates * 0.31 + (8 + lag) * 0.47 + offset) for lag in range(4)]
        )

    def _trained(self, seed: int = 2203) -> RRCTAgent:
        agent = self._agent(seed)
        agent.train_bayesian_transfer()
        plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="rollout",
        )
        agent.record_shadow_bayesian_transfer(plan, self._future())
        agent.freeze_bayesian_transfer()
        return agent

    def test_feature_map_is_bounded_precommit_and_noop_is_exactly_zero(self) -> None:
        agent = self._agent()
        before = pickle.dumps(agent, protocol=5)
        plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=25,
            selection_mode="rollout",
        )
        self.assertEqual(plan.bayesian_features.shape, (25, 20))
        np.testing.assert_array_equal(plan.bayesian_features[0], np.zeros(20))
        self.assertTrue(np.all(np.abs(plan.bayesian_features) <= 1.0))
        self.assertEqual(plan.bayesian_means[0], 0.0)
        self.assertEqual(plan.bayesian_standard_deviations[0], 0.0)
        self.assertEqual(plan.bayesian_lower_bounds[0], 0.0)
        self.assertEqual(pickle.dumps(agent, protocol=5), before)

    def test_shadow_update_counts_one_episode_and_preserves_live_core(self) -> None:
        agent = self._agent(seed=2204)
        agent.train_bayesian_transfer()
        plan = agent.plan_endogenous_self_intention(horizon=4, query_budget=4)
        before = agent.snapshot()
        update = agent.record_shadow_bayesian_transfer(plan, self._future(0.1))
        after = agent.snapshot()
        self.assertEqual(update.outcome_source, "shadow")
        self.assertEqual(update.candidate_indices, plan.queried_indices[1:])
        self.assertEqual(update.observation_count_after, 3)
        self.assertAlmostEqual(update.effective_sample_count_after, 1.0)
        self.assertNotEqual(update.posterior_digest_before, update.posterior_digest_after)
        for field in ("time", "resolution_level"):
            self.assertEqual(before[field], after[field])
        for field in ("workspace", "self_state", "last_action"):
            np.testing.assert_array_equal(before[field], after[field])

    def test_training_requires_revealed_exact_suffix_and_stales_plan(self) -> None:
        agent = self._agent(seed=2205)
        frozen_plan = agent.plan_endogenous_self_intention(horizon=4, query_budget=4)
        with self.assertRaises(RuntimeError):
            agent.record_shadow_bayesian_transfer(frozen_plan, self._future())
        agent.train_bayesian_transfer()
        plan = agent.plan_endogenous_self_intention(horizon=4, query_budget=4)
        committed = pickle.dumps(agent, protocol=5)
        with self.assertRaises(ValueError):
            agent.record_shadow_bayesian_transfer(plan, self._future()[:3])
        self.assertEqual(pickle.dumps(agent, protocol=5), committed)
        agent.record_shadow_bayesian_transfer(plan, self._future())
        with self.assertRaises(RuntimeError):
            agent.commit_endogenous_self_intention(plan)

    def test_mutated_plan_arrays_fail_closed(self) -> None:
        agent = self._agent(seed=2211)
        agent.train_bayesian_transfer()
        plan = agent.plan_endogenous_self_intention(horizon=4, query_budget=4)
        before = pickle.dumps(agent, protocol=5)
        plan.bayesian_features[1, 0] += 0.01
        with self.assertRaises(RuntimeError):
            agent.record_shadow_bayesian_transfer(plan, self._future())
        self.assertEqual(pickle.dumps(agent, protocol=5), before)

        fresh = self._agent(seed=2212)
        commit_plan = fresh.plan_endogenous_self_intention(horizon=4, query_budget=4)
        commit_plan.candidate_deltas[1, 0] += 0.01
        with self.assertRaises(RuntimeError):
            fresh.commit_endogenous_self_intention(commit_plan)

    def test_always_zero_is_a_measured_noop_trajectory(self) -> None:
        agent = self._agent(seed=2213)
        plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="always_zero",
        )
        self.assertEqual(plan.selected_index, 0)
        np.testing.assert_array_equal(plan.selected_delta, np.zeros(agent.self_dim))
        receipt = agent.commit_endogenous_self_intention(plan)
        result = agent.evaluate_committed_intention(
            receipt, self._future(), update_calibration=False
        )
        self.assertAlmostEqual(result.realized_improvement, 0.0, places=15)
        self.assertAlmostEqual(
            result.realized_baseline_error,
            result.realized_selected_error,
            places=15,
        )

    def test_snapshot_round_trip_reset_and_configuration_guard(self) -> None:
        source = self._trained(seed=2206)
        snapshot = source.bayesian_transfer_snapshot()
        source.reset()
        self.assertEqual(
            source.bayesian_transfer.posterior_digest(),
            snapshot["model"]["posterior_digest"],
        )
        target = self._agent(seed=2206)
        target.load_bayesian_transfer_snapshot(snapshot, freeze=True)
        self.assertEqual(target.bayesian_transfer_snapshot()["digest"], snapshot["digest"])
        target.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="bayesian_mean",
        )
        with self.assertRaises(RuntimeError):
            target.plan_endogenous_self_intention(
                horizon=3,
                query_budget=4,
                selection_mode="bayesian_mean",
            )
        target.reset(seed=2207)
        self.assertEqual(target.bayesian_transfer.observation_count, 0)
        self.assertIsNone(target.bayesian_transfer_snapshot()["transfer_key"])

    def test_corrupt_agent_snapshot_is_transactionally_rejected(self) -> None:
        source = self._trained(seed=2208)
        snapshot = source.bayesian_transfer_snapshot()
        target = self._agent(seed=2208)
        before = pickle.dumps(target, protocol=5)
        corrupted = copy.deepcopy(snapshot)
        corrupted["updates"][0]["normalized_targets"] = (2.0,) * 3
        with self.assertRaises(ValueError):
            target.load_bayesian_transfer_snapshot(corrupted)
        self.assertEqual(pickle.dumps(target, protocol=5), before)

    def test_snapshot_metadata_integers_are_strict(self) -> None:
        source = self._trained(seed=2214)
        snapshot = source.bayesian_transfer_snapshot()
        target = self._agent(seed=2214)
        before = pickle.dumps(target, protocol=5)
        for field, invalid_value in (
            ("schema_version", 1.5),
            ("schema_version", "1"),
            ("schema_version", True),
            ("update_count", 1.9),
            ("update_count", "1"),
        ):
            with self.subTest(field=field, value=invalid_value):
                corrupted = copy.deepcopy(snapshot)
                corrupted[field] = invalid_value
                with self.assertRaises(ValueError):
                    target.load_bayesian_transfer_snapshot(corrupted)
                self.assertEqual(pickle.dumps(target, protocol=5), before)
        corrupted = copy.deepcopy(snapshot)
        corrupted["foreign_metadata"] = 1
        with self.assertRaises(ValueError):
            target.load_bayesian_transfer_snapshot(corrupted)
        self.assertEqual(pickle.dumps(target, protocol=5), before)

    def test_bayesian_cold_start_abstains_and_exposes_uncertainty(self) -> None:
        agent = self._agent(seed=2209)
        mean_plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="bayesian_mean",
        )
        credible_plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="bayesian_credible",
            bayesian_confidence=0.95,
        )
        self.assertEqual(mean_plan.selected_index, 0)
        self.assertTrue(mean_plan.abstained)
        self.assertEqual(credible_plan.selected_index, 0)
        self.assertTrue(credible_plan.abstained)
        self.assertTrue(all(value > 0.0 for value in credible_plan.bayesian_standard_deviations[1:]))
        self.assertTrue(all(value < 0.0 for value in credible_plan.bayesian_lower_bounds[1:]))

    def test_bayesian_selection_uses_posterior_not_rollout_score(self) -> None:
        agent = self._agent(seed=2210)
        template = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="rollout",
        )
        agent.train_bayesian_transfer()
        targets = np.asarray([-0.02, -0.01, 0.08], dtype=np.float64)
        agent.bayesian_transfer.observe_batch(
            template.bayesian_features[1:],
            targets,
            weights=np.full(3, 1.0 / 3.0),
        )
        agent._bayesian_transfer_key = template.bayesian_transfer_key
        agent.freeze_bayesian_transfer()
        plan = agent.plan_endogenous_self_intention(
            horizon=4,
            query_budget=4,
            selection_mode="bayesian_mean",
        )
        self.assertEqual(
            plan.selected_index,
            plan.queried_indices[int(np.argmax(plan.bayesian_means))],
        )
        self.assertGreater(plan.predicted_improvement, 0.0)
        self.assertNotEqual(plan.selected_index, 0)


if __name__ == "__main__":
    unittest.main()

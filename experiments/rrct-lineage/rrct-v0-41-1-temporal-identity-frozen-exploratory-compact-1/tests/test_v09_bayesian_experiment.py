import copy
import tempfile
import unittest
from pathlib import Path

from rrct.bayesian_transfer_experiment import (
    _bayesian_risk_coverage_rows,
    _prime_agent,
    _save_transfer_snapshot,
    _train_predictors,
    _train_transfer,
    load_transfer_snapshot_artifact,
)
from rrct.experiments import _episodes


class BayesianTransferExperimentArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = 2309
        cls.predictor, cls.forecaster = _train_predictors(
            seed=cls.seed,
            episode_count=8,
            delay=5,
        )
        cls.episodes = _episodes(8, seed=cls.seed + 20_000, delay=7)
        cls.real, cls.control, cls.rows = _train_transfer(
            seed=cls.seed,
            episodes=cls.episodes,
            predictor_snapshot=cls.predictor,
            forecaster_snapshot=cls.forecaster,
            horizon=4,
            candidate_magnitude=0.35,
        )

    def _load(self, snapshot: dict) -> None:
        agent = _prime_agent(
            seed=self.seed,
            predictor_snapshot=self.predictor,
            forecaster_snapshot=self.forecaster,
            prefix=self.episodes[0].observations[:-4],
            transfer_snapshot=snapshot,
        )
        self.assertEqual(agent.bayesian_transfer_snapshot()["digest"], snapshot["digest"])

    def test_real_and_permuted_receipts_round_trip_in_memory(self) -> None:
        self.assertEqual(len(self.rows), 8 * 24)
        for name, snapshot, provenance in (
            ("real", self.real, "shadow"),
            ("control", self.control, "permuted_control"),
        ):
            with self.subTest(name=name):
                self.assertEqual(snapshot["update_count"], 8)
                self.assertEqual(snapshot["model"]["observation_count"], 8 * 24)
                self.assertEqual(snapshot["model"]["effective_sample_count"], 8.0)
                self.assertEqual(
                    {row["outcome_source"] for row in snapshot["updates"]},
                    {provenance},
                )
                self._load(copy.deepcopy(snapshot))

    def test_real_and_permuted_npz_artifacts_round_trip_without_pickle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for name, snapshot in (("real", self.real), ("control", self.control)):
                with self.subTest(name=name):
                    path = Path(directory) / f"{name}.npz"
                    _save_transfer_snapshot(path, snapshot)
                    loaded = load_transfer_snapshot_artifact(path)
                    self._load(loaded)

    def test_permuted_control_cannot_resume_training(self) -> None:
        agent = _prime_agent(
            seed=self.seed,
            predictor_snapshot=self.predictor,
            forecaster_snapshot=self.forecaster,
            prefix=self.episodes[0].observations[:-4],
            transfer_snapshot=self.control,
        )
        with self.assertRaises(RuntimeError):
            agent.train_bayesian_transfer()
        with self.assertRaises(ValueError):
            agent.load_bayesian_transfer_snapshot(self.control, freeze=False)

    def test_control_mapping_corruption_is_rejected(self) -> None:
        corrupted = copy.deepcopy(self.control)
        corrupted["updates"][0]["target_episode_index"] = len(corrupted["updates"])
        target = _prime_agent(
            seed=self.seed,
            predictor_snapshot=self.predictor,
            forecaster_snapshot=self.forecaster,
            prefix=self.episodes[0].observations[:-4],
        )
        with self.assertRaises(ValueError):
            target.load_bayesian_transfer_snapshot(corrupted)

    def test_unknown_npz_model_array_is_rejected(self) -> None:
        corrupted = copy.deepcopy(self.real)
        corrupted["model"]["foreign_array"] = corrupted["model"]["sum_xy"].copy()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "foreign.npz"
            _save_transfer_snapshot(path, corrupted)
            loaded = load_transfer_snapshot_artifact(path)
            target = _prime_agent(
                seed=self.seed,
                predictor_snapshot=self.predictor,
                forecaster_snapshot=self.forecaster,
                prefix=self.episodes[0].observations[:-4],
            )
            with self.assertRaises(ValueError):
                target.load_bayesian_transfer_snapshot(loaded)

    def test_risk_curve_has_a_real_forced_abstain_endpoint(self) -> None:
        calibration = [
            {
                "seed": 1,
                "bank": "bayes",
                "policy_raw_predicted_improvement": value,
            }
            for value in (0.1, 0.2)
        ]
        predictions = []
        policies = []
        for episode, (candidate, prediction, realized) in enumerate(
            ((3, 0.3, 0.02), (4, -0.1, -0.03))
        ):
            predictions.append(
                {
                    "seed": 1,
                    "evaluation_episode": episode,
                    "episode_hash": f"episode-{episode}",
                    "queried_position": 1,
                    "candidate_index": candidate,
                    "rollout_predicted_improvement": 0.0,
                    "bayesian_predicted_improvement": prediction,
                    "bayesian_lower_bound_95": prediction - 0.1,
                    "realized_improvement": realized,
                }
            )
            acted = prediction > 0.0
            policies.append(
                {
                    "seed": 1,
                    "evaluation_episode": episode,
                    "arm": "bayes_mean",
                    "acted": acted,
                    "selected_index": candidate if acted else 0,
                    "selected_improvement": realized if acted else 0.0,
                }
            )
        rows = _bayesian_risk_coverage_rows(
            seeds=(1,),
            calibration_rows=calibration,
            evaluation_predictions=predictions,
            policy_evaluations=policies,
        )
        forced = next(row for row in rows if row["threshold_label"] == "forced_abstain")
        zero = next(
            row for row in rows if row["threshold_label"] == "minimum_effect_zero"
        )
        self.assertEqual(forced["action_count"], 0)
        self.assertEqual(forced["action_coverage"], 0.0)
        self.assertTrue(forced["forced_abstain_endpoint"])
        self.assertTrue(zero["matches_bayes_mean_api"])


if __name__ == "__main__":
    unittest.main()

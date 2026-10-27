import csv
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import rrct.predictor_dose as dose_module
from rrct.cli import _flatten_tokens, build_parser
from rrct.environment import task_names
from rrct.predictor_dose import (
    PREDICTOR_DOSE_ROW_FIELDS,
    run_predictor_dose,
    transform_predictor_snapshot,
    verify_predictor_transform,
)


class PredictorDoseTransformTests(unittest.TestCase):
    @staticmethod
    def _snapshot() -> dict[str, object]:
        rng = np.random.default_rng(1201)
        return {
            "prediction_weights": rng.normal(size=(16, 12)),
            "workspace_skip": rng.normal(size=(16, 16)),
            "learning_steps": 37,
            "learning_rate": 0.03,
        }

    def test_exact_endpoints_cover_all_outputs_and_are_deterministic(self) -> None:
        snapshot = self._snapshot()
        zero = transform_predictor_snapshot(snapshot, dose=0.0, seed=1202)
        one = transform_predictor_snapshot(snapshot, dose=1.0, seed=1202)
        repeated = transform_predictor_snapshot(snapshot, dose=1.0, seed=1202)

        np.testing.assert_array_equal(zero.orthogonal_matrix, np.eye(16))
        np.testing.assert_array_equal(
            zero.snapshot["prediction_weights"], snapshot["prediction_weights"]
        )
        np.testing.assert_array_equal(
            zero.snapshot["workspace_skip"], snapshot["workspace_skip"]
        )
        self.assertTrue(zero.invariants["endpoint_identity_exact"])
        with self.assertRaises(ValueError):
            zero.orthogonal_matrix[0, 0] = 2.0
        with self.assertRaises(ValueError):
            zero.snapshot["prediction_weights"][0, 0] = 2.0

        self.assertEqual(one.pairs, repeated.pairs)
        np.testing.assert_array_equal(
            one.orthogonal_matrix, repeated.orthogonal_matrix
        )
        self.assertEqual(
            one.orthogonal_matrix_sha256,
            repeated.orthogonal_matrix_sha256,
        )
        self.assertEqual(
            sorted(index for pair in one.pairs for index in pair), list(range(16))
        )
        self.assertEqual(len(one.pairs), 8)
        self.assertTrue(
            set(np.unique(one.orthogonal_matrix)).issubset({-1.0, 0.0, 1.0})
        )
        self.assertEqual(np.count_nonzero(one.orthogonal_matrix), 16)
        for first, second in one.pairs:
            np.testing.assert_array_equal(
                one.snapshot["prediction_weights"][first],
                -snapshot["prediction_weights"][second],
            )
            np.testing.assert_array_equal(
                one.snapshot["prediction_weights"][second],
                snapshot["prediction_weights"][first],
            )
            np.testing.assert_array_equal(
                one.snapshot["workspace_skip"][first],
                -snapshot["workspace_skip"][second],
            )
            np.testing.assert_array_equal(
                one.snapshot["workspace_skip"][second],
                snapshot["workspace_skip"][first],
            )
        self.assertTrue(one.invariants["endpoint_signed_pair_permutation_exact"])

    def test_all_doses_share_one_q_and_preserve_strict_invariants(self) -> None:
        snapshot = self._snapshot()
        pairs = None
        for dose in (0.0, 0.25, 0.5, 0.75, 1.0):
            transformed = transform_predictor_snapshot(
                snapshot, dose=dose, seed=1203
            )
            if pairs is None:
                pairs = transformed.pairs
            self.assertEqual(transformed.pairs, pairs)
            self.assertTrue(transformed.invariants["all_passed"])
            self.assertEqual(transformed.invariants["atol"], 1e-12)
            self.assertEqual(transformed.invariants["rtol"], 1e-12)
            np.testing.assert_allclose(
                transformed.snapshot["prediction_weights"],
                transformed.orthogonal_matrix @ snapshot["prediction_weights"],
                atol=1e-12,
                rtol=1e-12,
            )
            np.testing.assert_allclose(
                transformed.snapshot["workspace_skip"],
                transformed.orthogonal_matrix @ snapshot["workspace_skip"],
                atol=1e-12,
                rtol=1e-12,
            )

    def test_deliberate_corruption_fails_retained_invariants(self) -> None:
        snapshot = self._snapshot()
        transformed = transform_predictor_snapshot(
            snapshot, dose=0.5, seed=1204
        )
        corrupted = {
            key: value.copy() if isinstance(value, np.ndarray) else value
            for key, value in transformed.snapshot.items()
        }
        corrupted["prediction_weights"][0, 0] += 1e-5
        report = verify_predictor_transform(
            snapshot,
            corrupted,
            transformed.orthogonal_matrix,
        )
        self.assertFalse(report["all_passed"])
        self.assertFalse(report["checks"]["shared_q_prediction_weights"])
        self.assertGreater(report["prediction_shared_q_max_abs_error"], 1e-6)

    def test_transform_validates_dose_and_frozen_output_dimension(self) -> None:
        snapshot = self._snapshot()
        for invalid in (-0.1, 1.1, np.nan, np.inf):
            with self.assertRaises(ValueError):
                transform_predictor_snapshot(snapshot, dose=invalid, seed=1)
        short = dict(snapshot)
        short["prediction_weights"] = np.zeros((14, 12))
        short["workspace_skip"] = np.zeros((14, 14))
        with self.assertRaises(ValueError):
            transform_predictor_snapshot(short, dose=0.5, seed=1)


class PredictorDoseGateTests(unittest.TestCase):
    def test_positive_and_two_sided_gate_directions_are_distinct(self) -> None:
        seeds = tuple(range(8))
        positive = dose_module._positive_association_gate(
            np.ones(8),
            seeds=seeds,
            resamples=128,
            rng=np.random.default_rng(1205),
        )
        negative_not_allowed = dose_module._positive_association_gate(
            -np.ones(8),
            seeds=seeds,
            resamples=128,
            rng=np.random.default_rng(1205),
        )
        negative_two_sided = dose_module._two_sided_association_gate(
            -np.ones(8),
            seeds=seeds,
            resamples=128,
            rng=np.random.default_rng(1205),
        )
        self.assertTrue(positive["supported"])
        self.assertFalse(negative_not_allowed["supported"])
        self.assertTrue(negative_two_sided["supported"])
        self.assertEqual(negative_two_sided["aggregate_direction"], "negative")

    def test_average_ranks_handle_ties_and_constant_metric_as_zero(self) -> None:
        ranks = dose_module._average_ranks([3.0, 1.0, 1.0, 4.0])
        np.testing.assert_array_equal(ranks, [3.0, 1.5, 1.5, 4.0])
        self.assertEqual(
            dose_module._spearman_average_rank([0.0, 0.5, 1.0], [2.0] * 3),
            0.0,
        )

    def test_closure_association_is_descriptive_without_support_gate(self) -> None:
        rows = []
        for seed in range(8):
            for dose in (0.0, 0.5, 1.0):
                rows.append(
                    {
                        "seed": seed,
                        "dose": dose,
                        "heldout_prediction_rmse": dose,
                        "self_to_workspace_effect": -dose,
                        "closure_strength": dose,
                    }
                )
        _, gates = dose_module._dose_statistics(
            rows,
            seeds=tuple(range(8)),
            doses=(0.0, 0.5, 1.0),
            bootstrap_resamples=128,
            bootstrap_seed=1206,
        )
        closure = gates["dose_vs_closure_strength"]
        self.assertEqual(closure["inferential_gate"], "none_descriptive_only")
        self.assertIsNone(closure["supported"])


class PredictorDoseRunnerTests(unittest.TestCase):
    @staticmethod
    def _base_snapshot() -> dict[str, object]:
        prediction = np.arange(16 * 12, dtype=np.float64).reshape(16, 12) / 100
        workspace_skip = np.eye(16, dtype=np.float64)
        return {
            "prediction_weights": prediction,
            "workspace_skip": workspace_skip,
            "learning_steps": 9,
        }

    @classmethod
    def _mock_result(
        cls,
        *args: object,
        predictor_snapshot: dict[str, object],
        seed: int,
        **_: object,
    ) -> tuple[dict[str, object], np.ndarray]:
        base = cls._base_snapshot()
        dose_proxy = 0.0 if np.array_equal(
            predictor_snapshot["prediction_weights"], base["prediction_weights"]
        ) else 1.0
        snapshot_id = dose_module._predictor_snapshot_id(predictor_snapshot)
        task_accuracy = {task: 0.6 + 0.01 * dose_proxy for task in task_names()}
        profile = {
            "broadcast_reach": 0.7,
            "temporal_persistence": 0.3 + 0.01 * dose_proxy,
            "differentiation": 0.4,
            "metacognitive_calibration": 0.7,
            "self_location": 0.5,
            "episodic_binding": 0.6,
            "projector_consistency": 1.0,
            "strongly_connected": True,
        }
        result = {
            "predictor_snapshot_id": snapshot_id,
            "loaded_predictor_snapshot_id": snapshot_id,
            "self_model_mode_during_scoring": "frozen",
            "self_learning_updates": 9,
            "self_learning_updates_before_test": 9,
            "self_learning_updates_after_test": 9,
            "self_learning_updates_during_test": 0,
            "heldout_prediction_rmse": 0.1 + dose_proxy + seed * 1e-5,
            "self_to_workspace_effect": 0.02 - 0.01 * dose_proxy,
            "closure_strength": 0.03 + 0.01 * dose_proxy,
            "closure_raw_strength": 0.01 + 0.001 * dose_proxy,
            "profile": profile,
            "signature": {
                "omega": 0.8,
                "passes": False,
                "bottleneck": "temporal_persistence",
            },
            "task_accuracy": task_accuracy,
            "factor_accuracy": {"context": 0.6, "object": 0.6, "actuator": 0.6},
            "mean_task_accuracy": float(np.mean(list(task_accuracy.values()))),
            "projector_residual": 0.0,
            "resolution_histogram": {"0": 1, "1": 2, "2": 3, "3": 2},
            "intervention_magnitude": 0.35,
            "causal_adjacency": np.ones((4, 4), dtype=int).tolist(),
            "causal_effects": np.full((4, 4), 0.1).tolist(),
            "closure_capacity_matrix": np.full((4, 4), 0.1).tolist(),
            "closure_bottleneck_pair": [0, 1],
            "closure_cut_certificate": {
                "source": 0,
                "target": 1,
                "raw_capacity": 0.1,
                "reachable_set": [0],
                "cut_edges": [[0, 1, 0.1]],
                "node_count": 4,
            },
            "recurrent_gain": 1.0,
            "closure_gain": 1.0,
            "self_feedback_gain": 1.0,
            "action_feedback_gain": 1.0,
        }
        return result, np.zeros(3)

    def _mock_run(self, output: Path) -> dict[str, object]:
        with (
            patch.object(
                dose_module,
                "_episodes",
                side_effect=lambda count, **kwargs: list(range(count)),
            ),
            patch.object(
                dose_module,
                "_train_predictor_snapshot",
                side_effect=lambda episodes, **kwargs: self._base_snapshot(),
            ),
            patch.object(dose_module, "evaluate_variant", side_effect=self._mock_result),
            patch.object(
                dose_module,
                "_audit_closure_row",
                return_value={"passed": True, "mocked_independent_audit": True},
            ),
        ):
            return run_predictor_dose(
                output,
                seeds=(1207, 1208),
                doses=(0.0, 1.0),
                train_episode_count=8,
                test_episode_count=8,
                bootstrap_resamples=64,
                bootstrap_seed=1209,
            )

    def test_mocked_runner_is_deterministic_and_csv_is_lossless(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first_path = Path(temporary) / "first"
            second_path = Path(temporary) / "second"
            first = self._mock_run(first_path)
            second = self._mock_run(second_path)
            self.assertEqual(first, second)
            self.assertEqual(first["status"], "completed_without_seed_filtering")
            self.assertEqual(len(first["runs"]), 4)
            self.assertEqual(len(first["per_dose_aggregates"]), 2)
            self.assertEqual(
                first["association_gates"]["dose_vs_closure_strength"][
                    "inferential_gate"
                ],
                "none_descriptive_only",
            )
            for artifact in first["artifacts"]:
                self.assertTrue((first_path / artifact).is_file())

            with (first_path / "predictor_dose.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                encoded = next(csv.DictReader(handle))
            reconstructed = {
                field: json.loads(encoded[field]) for field in PREDICTOR_DOSE_ROW_FIELDS
            }
            self.assertEqual(reconstructed, first["runs"][0])

    def test_invariant_failure_is_retained_and_skips_evaluator(self) -> None:
        original = transform_predictor_snapshot

        def corrupt(snapshot: dict[str, object], *, dose: float, seed: int):
            transformed = original(snapshot, dose=dose, seed=seed)
            invariants = dict(transformed.invariants)
            invariants["all_passed"] = False
            invariants["deliberate_test_corruption"] = True
            return replace(transformed, invariants=invariants)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "invariant_failure"
            with (
                patch.object(
                    dose_module,
                    "_episodes",
                    side_effect=lambda count, **kwargs: list(range(count)),
                ),
                patch.object(
                    dose_module,
                    "_train_predictor_snapshot",
                    return_value=self._base_snapshot(),
                ),
                patch.object(
                    dose_module,
                    "transform_predictor_snapshot",
                    side_effect=corrupt,
                ),
                patch.object(dose_module, "evaluate_variant") as evaluator,
            ):
                summary = run_predictor_dose(
                    output,
                    seeds=(1210,),
                    doses=(0.0, 1.0),
                    train_episode_count=8,
                    test_episode_count=8,
                    bootstrap_resamples=16,
                )
            evaluator.assert_not_called()
            self.assertEqual(summary["status"], "stopped_protocol_contradiction")
            self.assertEqual(len(summary["runs"]), 2)
            self.assertTrue(
                all(row["status"] == "stopped_invariant_failure" for row in summary["runs"])
            )
            self.assertEqual(
                summary["association_gates"]["status"],
                "not_computed_after_protocol_stop",
            )

    def test_seed_setup_failure_retains_every_planned_dose(self) -> None:
        doses = (0.0, 0.25, 0.5, 0.75, 1.0)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "setup_failure"
            with patch.object(
                dose_module, "_episodes", side_effect=RuntimeError("setup broke")
            ):
                summary = run_predictor_dose(
                    output,
                    seeds=(1211,),
                    doses=doses,
                    train_episode_count=8,
                    test_episode_count=8,
                    bootstrap_resamples=16,
                )
            self.assertEqual(len(summary["runs"]), len(doses))
            self.assertEqual(
                [row["dose"] for row in summary["runs"]], list(doses)
            )
            self.assertTrue(
                all(
                    row["status"] == "stopped_seed_setup_exception"
                    for row in summary["runs"]
                )
            )
            self.assertEqual(summary["per_dose_aggregates"], [])

    def test_nonempty_output_is_refused_before_training(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "occupied"
            output.mkdir()
            (output / "keep.txt").write_text("keep", encoding="utf-8")
            with patch.object(dose_module, "_train_predictor_snapshot") as trainer:
                with self.assertRaises(ValueError):
                    run_predictor_dose(
                        output,
                        seeds=(1212,),
                        doses=(0.0, 1.0),
                        train_episode_count=8,
                        test_episode_count=8,
                        bootstrap_resamples=16,
                    )
            trainer.assert_not_called()

    def test_frozen_gains_reject_every_nonexact_value(self) -> None:
        for field in (
            "recurrent_gain",
            "closure_gain",
            "self_feedback_gain",
            "action_feedback_gain",
        ):
            for invalid in (0.0, 1.0001, np.nan, np.inf):
                with tempfile.TemporaryDirectory() as temporary:
                    with self.assertRaises(ValueError):
                        run_predictor_dose(
                            Path(temporary) / "unused",
                            seeds=(1213,),
                            doses=(0.0, 1.0),
                            train_episode_count=8,
                            test_episode_count=8,
                            bootstrap_resamples=16,
                            **{field: invalid},
                        )

    def test_real_nonconfirmatory_smoke_uses_actual_loaded_snapshot_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "real_smoke"
            summary = run_predictor_dose(
                output,
                seeds=(1217,),
                doses=(0.0, 1.0),
                train_episode_count=8,
                test_episode_count=8,
                bootstrap_resamples=16,
                bootstrap_seed=1218,
            )
            self.assertEqual(summary["status"], "completed_without_seed_filtering")
            self.assertEqual(
                summary["protocol_scope"], "nonconfirmatory_or_smoke_configuration"
            )
            for row in summary["runs"]:
                self.assertEqual(row["stop_reason"], [])
                self.assertEqual(
                    row["scoring_predictor_snapshot_id"],
                    row["transformed_snapshot_id"],
                )
                self.assertEqual(row["self_learning_updates_during_test"], 0)

    def test_cli_maps_every_frozen_predictor_dose_option(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "predictor-dose",
                "--seeds",
                "3,5",
                "--doses",
                "0,.25,1",
                "--recurrent-gain",
                "1",
                "--closure-gain",
                "1",
                "--self-feedback-gain",
                "1",
                "--action-feedback-gain",
                "1",
                "--train-episodes",
                "12",
                "--test-episodes",
                "6",
                "--train-delay",
                "4",
                "--test-delay",
                "9",
                "--persistence-horizon",
                "5",
                "--bootstrap-resamples",
                "40",
                "--bootstrap-seed",
                "99",
            ]
        )
        self.assertEqual(_flatten_tokens(parsed.seeds), (3, 5))
        self.assertEqual(_flatten_tokens(parsed.doses), (0.0, 0.25, 1.0))
        self.assertEqual(parsed.intervention_horizon, 5)
        self.assertEqual(parsed.bootstrap_resamples, 40)
        self.assertEqual(parsed.bootstrap_seed, 99)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

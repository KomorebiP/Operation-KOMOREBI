"""Focused tests for v0.3 gain, path, and mediation experiments."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from rrct.cli import _flatten_tokens, build_parser
from rrct.experiments import (
    INTERVENTION_MAGNITUDE,
    MEDIATION_CONDITIONS,
    PROFILE_THRESHOLDS,
    SHUFFLED_SELF_MODEL_CONDITION,
    V03_VALIDATION_SEEDS,
    _episodes,
    _shuffled_predictor_snapshot,
    evaluate_variant,
    run_gain_surface,
    run_hysteresis_sweep,
    run_phase_sweep,
    run_predictor_mediation,
)


def _fake_surface_evaluation(
    name: str,
    ablations: tuple[str, ...],
    train_episodes: object,
    test_episodes: object,
    *,
    seed: int,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_model_condition: str = "trained_self_model",
    predictor_snapshot: object = None,
) -> tuple[dict[str, object], np.ndarray]:
    del name, ablations, train_episodes, test_episodes, predictor_snapshot
    closure_strength = 0.1 + 0.2 * recurrent_gain + 0.3 * closure_gain
    persistence = float(np.clip(0.2 + 0.1 * recurrent_gain, 0.0, 1.0))
    profile = {field: 0.75 for field in PROFILE_THRESHOLDS}
    profile["temporal_persistence"] = persistence
    profile["strongly_connected"] = bool(recurrent_gain + closure_gain > 0)
    tasks = {
        "product": 0.75,
        "majority": 0.75,
        "context_object": 0.75,
        "object_actuator": 0.75,
    }
    result: dict[str, object] = {
        "self_model_condition": self_model_condition,
        "self_model_mode_during_scoring": "frozen",
        "self_learning_updates": 10,
        "self_learning_updates_before_test": 10,
        "self_learning_updates_after_test": 10,
        "self_learning_updates_during_test": 0,
        "heldout_prediction_rmse": 0.2 + seed * 1e-6,
        "recurrent_gain": recurrent_gain,
        "closure_gain": closure_gain,
        "closure_strength": closure_strength,
        "closure_raw_strength": closure_strength * INTERVENTION_MAGNITUDE,
        "closure_bottleneck_pair": [0, 1],
        "intervention_magnitude": INTERVENTION_MAGNITUDE,
        "causal_effects": np.full((4, 4), 0.05).tolist(),
        "closure_capacity_matrix": np.full((4, 4), 0.05).tolist(),
        "task_accuracy": tasks,
        "mean_task_accuracy": 0.75,
        "profile": profile,
        "signature": {
            "omega": 1.1 if profile["strongly_connected"] else 0.0,
            "passes": bool(profile["strongly_connected"]),
            "bottleneck": "temporal_persistence",
        },
    }
    return result, np.ones(3, dtype=np.float64)


def _fake_predictor_snapshot(
    train_episodes: object,
    *,
    seed: int,
) -> dict[str, object]:
    del train_episodes
    return {
        "prediction_weights": np.full((3, 2), seed / 100.0),
        "workspace_skip": np.eye(3) * (1.0 + seed / 100.0),
        "learning_steps": 10,
    }


class ClosureAndSurfaceTests(unittest.TestCase):
    def test_evaluate_variant_adds_continuous_closure_outside_omega(self) -> None:
        train = _episodes(8, seed=301, delay=3)
        test = _episodes(8, seed=302, delay=4)
        result, _ = evaluate_variant(
            "trained_self_model",
            (),
            train,
            test,
            seed=303,
        )
        self.assertGreaterEqual(result["closure_strength"], 0.0)
        self.assertTrue(np.isfinite(result["closure_strength"]))
        self.assertTrue(np.isfinite(result["self_to_workspace_effect"]))
        self.assertAlmostEqual(
            result["closure_raw_strength"],
            result["closure_strength"] * INTERVENTION_MAGNITUDE,
        )
        self.assertEqual(np.asarray(result["causal_effects"]).shape, (4, 4))
        self.assertEqual(
            np.asarray(result["closure_capacity_matrix"]).shape,
            (4, 4),
        )
        self.assertEqual(len(result["closure_bottleneck_pair"]), 2)
        self.assertNotIn("closure_strength", result["profile"])
        self.assertNotIn("closure_strength", PROFILE_THRESHOLDS)
        self.assertEqual(INTERVENTION_MAGNITUDE, 0.35)

    def test_gain_surface_keeps_all_seeds_and_bootstraps_cells(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.evaluate_variant",
            side_effect=_fake_surface_evaluation,
        ), patch(
            "rrct.experiments._train_predictor_snapshot",
            side_effect=_fake_predictor_snapshot,
        ) as train_snapshot:
            summary = run_gain_surface(
                directory,
                seeds=(3, 5),
                recurrent_gains=(0.0, 0.5),
                closure_gains=(0.0, 0.5),
                train_episode_count=8,
                test_episode_count=8,
                bootstrap_resamples=2_000,
            )
            self.assertEqual(len(summary["runs"]), 8)
            self.assertEqual(len(summary["aggregates"]), 4)
            self.assertFalse(summary["threshold_policy"]["lowered_or_retuned"])
            self.assertFalse(summary["threshold_policy"]["closure_strength_enters_omega"])
            self.assertEqual(train_snapshot.call_count, 2)
            self.assertTrue(summary["parameters"]["matched_predictor"])
            self.assertTrue(
                all(np.asarray(row["causal_effects"]).shape == (4, 4) for row in summary["runs"])
            )
            for seed in (3, 5):
                identifiers = {
                    row["predictor_snapshot_id"]
                    for row in summary["runs"]
                    if row["seed"] == seed
                }
                self.assertEqual(len(identifiers), 1)
                self.assertNotEqual(identifiers, {""})
                self.assertEqual(
                    {
                        row["self_learning_updates"]
                        for row in summary["runs"]
                        if row["seed"] == seed
                    },
                    {10},
                )
            for aggregate in summary["aggregates"]:
                self.assertEqual(aggregate["seeds_included"], [3, 5])
                closure = aggregate["metrics"]["closure_strength"]
                self.assertIn("bootstrap_ci95_lower", closure)
                self.assertIn("bootstrap_ci95_upper", closure)
            residual = np.asarray(
                summary["interaction_residuals"]["trained_self_model"]["residual"]
            )
            np.testing.assert_allclose(residual, 0.0, atol=1e-15)
            interaction = summary["interaction_residuals"]["trained_self_model"]
            self.assertEqual(interaction["count_positive_seed_interior_means"], 0)
            self.assertEqual(interaction["seed_count"], 2)
            self.assertIn("bootstrap_ci95_lower", interaction)
            self.assertFalse(interaction["positive_interaction_supported"])
            self.assertEqual(
                interaction["validation_rule"]["required_positive_seed_count"],
                6,
            )
            for name in ("gain_surface.csv", "gain_surface.json", "gain_surface.png"):
                self.assertTrue((Path(directory) / name).is_file())
            with (Path(directory) / "gain_surface.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                csv_row = next(csv.DictReader(handle))
            self.assertEqual(np.asarray(json.loads(csv_row["causal_effects"])).shape, (4, 4))

    def test_phase_sweep_can_select_dense_trained_only_condition(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.evaluate_variant",
            side_effect=_fake_surface_evaluation,
        ), patch(
            "rrct.experiments._train_predictor_snapshot",
            side_effect=_fake_predictor_snapshot,
        ) as train_snapshot:
            summary = run_phase_sweep(
                directory,
                seeds=(7,),
                gains=(0.2, 0.25, 0.3),
                train_episode_count=8,
                test_episode_count=8,
                conditions=("trained_self_model",),
                matched_predictor=True,
            )
            self.assertEqual(len(summary["runs"]), 3)
            self.assertEqual(train_snapshot.call_count, 1)
            self.assertEqual(summary["schema"], "rrct.experimental_sweep.v0.3")
            self.assertEqual(summary["parameters"]["conditions"], ["trained_self_model"])
            self.assertTrue(summary["parameters"]["matched_predictor"])
            self.assertEqual(
                len({row["predictor_snapshot_id"] for row in summary["runs"]}),
                1,
            )
            self.assertIn(
                "closure_strength",
                summary["steepest_observed_intervals"]["trained_self_model"],
            )


class HysteresisAndMediationTests(unittest.TestCase):
    def test_small_real_hysteresis_protocol_includes_doubled_settle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            summary = run_hysteresis_sweep(
                directory,
                seeds=(11,),
                gains=(0.0, 0.4),
                train_episode_count=8,
                settle_cycles=1,
                measurement_cycles=1,
                drive_period=2,
                persistence_horizon=2,
                bootstrap_resamples=2_000,
            )
            self.assertEqual(len(summary["runs"]), 8)
            self.assertEqual(
                {row["settle_multiplier"] for row in summary["runs"]}, {1, 2}
            )
            self.assertEqual(
                {row["direction"] for row in summary["runs"]},
                {"upward", "downward"},
            )
            self.assertTrue(
                all(
                    row["self_learning_updates_during_measurement"] == 0
                    for row in summary["runs"]
                )
            )
            self.assertIn(
                "doubled_settle_absolute_sensitivity",
                summary["per_seed_hysteresis"][0],
            )
            gate = summary["hysteresis_gate_statistics"]
            self.assertIn("declared_settle_area_median", gate)
            self.assertIn("doubled_settle_area_median", gate)
            self.assertIn("doubled_settle_retention_median", gate)
            self.assertIn("aggregate_median_retention_ratio", gate)
            self.assertEqual(
                gate["retention_gate_statistic"],
                "aggregate_median_retention_ratio",
            )
            self.assertIn("doubled_settle_count_at_or_above_threshold", gate)
            self.assertIn("not evidence", summary["interpretation_boundary"])

    def test_shuffle_preserves_spectra_and_real_mediation_freezes(self) -> None:
        rng = np.random.default_rng(401)
        snapshot = {
            "prediction_weights": rng.normal(size=(6, 4)),
            "workspace_skip": rng.normal(size=(6, 6)),
            "learning_steps": 12,
        }
        shuffled, permutation = _shuffled_predictor_snapshot(snapshot, seed=402)
        self.assertEqual(sorted(permutation.tolist()), list(range(6)))
        for key in ("prediction_weights", "workspace_skip"):
            np.testing.assert_allclose(
                np.linalg.svd(snapshot[key], compute_uv=False),
                np.linalg.svd(shuffled[key], compute_uv=False),
            )

        with tempfile.TemporaryDirectory() as directory:
            summary = run_predictor_mediation(
                directory,
                seeds=(13,),
                train_episode_count=8,
                test_episode_count=8,
                bootstrap_resamples=2_000,
            )
            self.assertEqual(
                tuple(row["condition"] for row in summary["runs"]),
                MEDIATION_CONDITIONS,
            )
            self.assertTrue(
                all(row["self_learning_updates_during_test"] == 0 for row in summary["runs"])
            )
            self.assertTrue(
                all(np.asarray(row["causal_effects"]).shape == (4, 4) for row in summary["runs"])
            )
            shuffled_row = next(
                row
                for row in summary["runs"]
                if row["condition"] == SHUFFLED_SELF_MODEL_CONDITION
            )
            self.assertIsNotNone(shuffled_row["predictor_row_permutation"])
            self.assertIn(
                "shuffled_trained_self_model",
                summary["paired_rmse_differences_vs_trained"],
            )
            contrasts = summary["paired_contrasts_vs_trained"]
            for condition in (
                "untrained_self_model",
                "shuffled_trained_self_model",
            ):
                self.assertIn("heldout_prediction_rmse", contrasts[condition])
                self.assertIn("win_counts", contrasts[condition]["heldout_prediction_rmse"])
                for field in ("closure_strength", "self_to_workspace_effect"):
                    self.assertIn("bootstrap_ci95_lower", contrasts[condition][field])
                    self.assertIn("bootstrap_ci95_upper", contrasts[condition][field])
            with (Path(directory) / "predictor_mediation.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 4)


class V03CliTests(unittest.TestCase):
    def test_new_cli_contract_accepts_comma_and_space_lists(self) -> None:
        parser = build_parser()
        surface = parser.parse_args(
            [
                "gain-surface",
                "--seeds",
                "3,5",
                "7",
                "--recurrent-gains",
                "0,0.2",
                "0.4",
                "--closure-gains",
                "0,0.3",
                "--conditions",
                "trained_self_model,untrained_self_model",
            ]
        )
        self.assertEqual(_flatten_tokens(surface.seeds), (3, 5, 7))
        self.assertEqual(_flatten_tokens(surface.recurrent_gains), (0.0, 0.2, 0.4))
        self.assertEqual(_flatten_tokens(surface.closure_gains), (0.0, 0.3))
        self.assertEqual(
            _flatten_tokens(surface.conditions),
            ("trained_self_model", "untrained_self_model"),
        )
        hysteresis = parser.parse_args(["hysteresis-sweep"])
        mediation = parser.parse_args(["predictor-mediation"])
        dense = parser.parse_args(["phase-sweep", "--matched-predictor"])
        self.assertEqual(_flatten_tokens(hysteresis.seeds), V03_VALIDATION_SEEDS)
        self.assertEqual(_flatten_tokens(mediation.seeds), V03_VALIDATION_SEEDS)
        self.assertTrue(dense.matched_predictor)


if __name__ == "__main__":
    unittest.main()

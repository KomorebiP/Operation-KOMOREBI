"""Tests for the v0.2 fixed-threshold and continuous-gain sweeps."""

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
    DEFAULT_PHASE_GAINS,
    DEFAULT_SWEEP_SEEDS,
    PROFILE_THRESHOLDS,
    SELF_MODEL_CONDITIONS,
    SWEEP_ROW_FIELDS,
    _episodes,
    evaluate_variant,
    run_phase_sweep,
    run_seed_sweep,
)


def _fake_evaluation(
    name: str,
    ablations: tuple[str, ...],
    train_episodes: object,
    test_episodes: object,
    *,
    seed: int,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_model_condition: str = "trained_self_model",
) -> tuple[dict[str, object], np.ndarray]:
    del name, train_episodes, test_episodes
    base = {
        "trained_self_model": 0.82,
        "untrained_self_model": 0.62,
        "no_self_model": 0.32,
    }[self_model_condition]
    score = float(np.clip(base * (0.5 + 0.5 * recurrent_gain), 0.0, 1.0))
    profile = {field: score for field in PROFILE_THRESHOLDS}
    profile["strongly_connected"] = bool(recurrent_gain > 0.0)
    ratios = {
        field: score / threshold for field, threshold in PROFILE_THRESHOLDS.items()
    }
    omega = min(ratios.values()) if profile["strongly_connected"] else 0.0
    task_accuracy = {
        "product": score,
        "majority": score,
        "context_object": score,
        "object_actuator": score,
    }
    updates = 19 if self_model_condition == "trained_self_model" else 0
    result: dict[str, object] = {
        "ablations": list(ablations),
        "self_model_condition": self_model_condition,
        "self_model_mode_during_scoring": "frozen",
        "self_learning_updates": updates,
        "self_learning_updates_before_test": updates,
        "self_learning_updates_after_test": updates,
        "self_learning_updates_during_test": 0,
        "heldout_prediction_rmse": float(1.0 - score + seed * 1e-6),
        "recurrent_gain": float(recurrent_gain),
        "closure_gain": float(closure_gain),
        "task_accuracy": task_accuracy,
        "mean_task_accuracy": score,
        "profile": profile,
        "signature": {
            "omega": float(omega),
            "passes": bool(omega >= 1.0),
            "bottleneck": min(ratios, key=ratios.get),
        },
    }
    return result, np.ones(3, dtype=np.float64)


class SweepArtifactTests(unittest.TestCase):
    def test_seed_sweep_writes_unfiltered_csv_json_and_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.evaluate_variant", side_effect=_fake_evaluation
        ):
            summary = run_seed_sweep(
                directory,
                seeds=(3, 5),
                train_episode_count=8,
                test_episode_count=8,
            )
            destination = Path(directory)
            for artifact in ("seed_sweep.csv", "seed_sweep.json", "seed_sweep.png"):
                self.assertTrue((destination / artifact).is_file(), artifact)
                self.assertGreater((destination / artifact).stat().st_size, 0)
            self.assertEqual(
                (destination / "seed_sweep.png").read_bytes()[:8],
                b"\x89PNG\r\n\x1a\n",
            )

            self.assertEqual(len(summary["runs"]), 2 * len(SELF_MODEL_CONDITIONS))
            self.assertFalse(summary["threshold_policy"]["lowered_or_retuned"])
            self.assertEqual(summary["threshold_policy"]["thresholds"], PROFILE_THRESHOLDS)
            for aggregate in summary["aggregates"]:
                self.assertEqual(aggregate["seeds_included"], [3, 5])
                self.assertEqual(aggregate["seed_count"], 2)

            with (destination / "seed_sweep.csv").open(newline="", encoding="utf-8") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual(tuple(csv_rows[0]), SWEEP_ROW_FIELDS)
            self.assertEqual(len(csv_rows), 6)
            loaded = json.loads((destination / "seed_sweep.json").read_text())
            self.assertTrue(loaded["aggregation_policy"]["all_prespecified_seeds_included"])

    def test_phase_sweep_aggregates_every_gain_and_condition(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.evaluate_variant", side_effect=_fake_evaluation
        ):
            summary = run_phase_sweep(
                directory,
                seeds=(7,),
                gains=(0.0, 0.5),
                train_episode_count=8,
                test_episode_count=8,
            )
            self.assertEqual(len(summary["runs"]), 6)
            self.assertEqual(len(summary["aggregates"]), 6)
            self.assertEqual(
                {row["gain"] for row in summary["runs"]}, {0.0, 0.5}
            )
            self.assertTrue(
                all(row["recurrent_gain"] == row["closure_gain"] for row in summary["runs"])
            )
            destination = Path(directory)
            for artifact in ("phase_sweep.csv", "phase_sweep.json", "phase_sweep.png"):
                self.assertTrue((destination / artifact).is_file(), artifact)


class SweepProtocolTests(unittest.TestCase):
    def test_trained_predictor_is_frozen_for_heldout_scoring(self) -> None:
        train = _episodes(8, seed=101, delay=3)
        test = _episodes(8, seed=102, delay=4)
        trained, _ = evaluate_variant(
            "trained_self_model",
            (),
            train,
            test,
            seed=103,
            self_model_condition="trained_self_model",
        )
        untrained, _ = evaluate_variant(
            "untrained_self_model",
            (),
            train,
            test,
            seed=103,
            self_model_condition="untrained_self_model",
        )
        self.assertEqual(trained["self_model_mode_during_scoring"], "frozen")
        self.assertGreater(trained["self_learning_updates"], 0)
        self.assertEqual(trained["self_learning_updates_during_test"], 0)
        self.assertEqual(untrained["self_learning_updates"], 0)
        self.assertEqual(untrained["self_learning_updates_during_test"], 0)
        self.assertTrue(np.isfinite(trained["heldout_prediction_rmse"]))
        self.assertTrue(np.isfinite(untrained["heldout_prediction_rmse"]))

    def test_cli_accepts_comma_and_space_separated_tokens(self) -> None:
        parser = build_parser()
        phase = parser.parse_args(
            [
                "phase-sweep",
                "--seeds",
                "3,5",
                "7",
                "--gains",
                "0,0.2",
                "0.4",
                "--train-episodes",
                "8",
                "--test-episodes",
                "8",
            ]
        )
        self.assertEqual(_flatten_tokens(phase.seeds), (3, 5, 7))
        self.assertEqual(_flatten_tokens(phase.gains), (0.0, 0.2, 0.4))
        seed = parser.parse_args(["seed-sweep"])
        self.assertEqual(_flatten_tokens(seed.seeds), DEFAULT_SWEEP_SEEDS)
        self.assertEqual(DEFAULT_PHASE_GAINS, (0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2))

    def test_invalid_gain_grid_is_rejected_without_threshold_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                run_phase_sweep(directory, seeds=(1,), gains=(0.0, -0.1))
            with self.assertRaises(ValueError):
                run_seed_sweep(directory, seeds=(1, 1))


if __name__ == "__main__":
    unittest.main()

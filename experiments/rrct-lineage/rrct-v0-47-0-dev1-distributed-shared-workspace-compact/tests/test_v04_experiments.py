"""Focused nonconfirmatory tests for the v0.4 mechanistic experiment arms."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from rrct.cli import _flatten_tokens, build_parser
from rrct.criticality import (
    widest_path_closure_details,
    widest_path_cut_certificate,
)
from rrct.experiments import (
    INTERVENTION_MAGNITUDE,
    V04_BOOTSTRAP_SEED,
    V04_VALIDATION_SEEDS,
    _agent,
    _audit_closure_row,
    _episodes,
    _path_decomposition_contrasts,
    _write_structured_csv,
    _warmed_intervention_diagnostics,
    run_local_dynamics,
    run_path_decomposition,
)


def _certificate_record(effects: np.ndarray) -> dict[str, object]:
    closure = widest_path_closure_details(
        effects,
        normalize=INTERVENTION_MAGNITUDE,
    )
    certificate = widest_path_cut_certificate(effects)
    return {
        "causal_effects": effects.tolist(),
        "closure_cut_certificate": {
            "source": certificate.source,
            "target": certificate.target,
            "raw_capacity": certificate.raw_capacity,
            "reachable_set": list(certificate.reachable_set),
            "cut_edges": [list(edge) for edge in certificate.cut_edges],
            "node_count": certificate.node_count,
        },
        "closure_capacity_matrix": closure.capacity_matrix.tolist(),
        "intervention_magnitude": INTERVENTION_MAGNITUDE,
        "closure_bottleneck_pair": list(closure.weakest_pair),
        "closure_raw_strength": closure.raw_strength,
    }


def _factorial_rows(
    seeds: tuple[int, ...],
    *,
    closure_value: object,
    persistence_value: object,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in seeds:
        for recurrence in (0.0, 1.0):
            for self_gain in (0.0, 1.0):
                for action_gain in (0.0, 1.0):
                    cell = (recurrence, self_gain, action_gain)
                    rows.append(
                        {
                            "seed": seed,
                            "recurrent_gain": recurrence,
                            "self_feedback_gain": self_gain,
                            "action_feedback_gain": action_gain,
                            "closure_strength": float(closure_value(cell)),
                            "temporal_persistence": float(
                                persistence_value(cell)
                            ),
                        }
                    )
    return rows


class V04FactorialAndCutTests(unittest.TestCase):
    def test_exact_factorial_formulas_gates_and_necessity_guard(self) -> None:
        seeds = tuple(range(8))

        def model(cell: tuple[float, float, float]) -> float:
            recurrence, self_gain, action_gain = cell
            return (
                1.0
                + 2.0 * recurrence
                + 3.0 * self_gain
                + 4.0 * action_gain
                + 5.0 * recurrence * self_gain * action_gain
            )

        rows = _factorial_rows(
            seeds,
            closure_value=model,
            persistence_value=model,
        )
        contrasts, necessity = _path_decomposition_contrasts(
            rows,
            seeds=seeds,
            bootstrap_resamples=500,
            bootstrap_seed=V04_BOOTSTRAP_SEED,
        )
        self.assertEqual(
            contrasts["self_contribution_at_recurrence_1"][
                "closure_strength"
            ]["mean"],
            8.0,
        )
        self.assertEqual(
            contrasts["action_contribution_at_recurrence_1"][
                "closure_strength"
            ]["mean"],
            9.0,
        )
        self.assertEqual(
            contrasts["recurrence_contribution_with_both_paths"][
                "closure_strength"
            ]["mean"],
            7.0,
        )
        self.assertEqual(
            contrasts["self_action_interaction_at_recurrence_1"][
                "closure_strength"
            ]["mean"],
            5.0,
        )
        self.assertEqual(
            contrasts["self_action_interaction_at_recurrence_0"][
                "closure_strength"
            ]["mean"],
            0.0,
        )
        self.assertEqual(
            contrasts["three_way_interaction"]["closure_strength"]["mean"],
            5.0,
        )
        self.assertTrue(
            contrasts["self_contribution_at_recurrence_1"][
                "closure_strength"
            ]["supported"]
        )
        descriptive = contrasts["three_way_interaction"]["closure_strength"]
        self.assertNotIn("supported", descriptive)
        self.assertEqual(descriptive["decision_rule"], "none; descriptive retention only")
        self.assertFalse(necessity["recurrence"]["closure_strength"]["necessary"])

        def full_and_removals(cell: tuple[float, float, float]) -> float:
            return 1.0 if cell == (1.0, 1.0, 1.0) else 0.0

        guarded_rows = _factorial_rows(
            seeds,
            closure_value=full_and_removals,
            persistence_value=lambda cell: 0.0,
        )
        _, guarded_necessity = _path_decomposition_contrasts(
            guarded_rows,
            seeds=seeds,
            bootstrap_resamples=100,
            bootstrap_seed=V04_BOOTSTRAP_SEED,
        )
        for path_name in ("recurrence", "self_feedback", "action_feedback"):
            self.assertTrue(
                guarded_necessity[path_name]["closure_strength"]["necessary"]
            )
            self.assertFalse(
                guarded_necessity[path_name]["temporal_persistence"]["necessary"]
            )

    def test_cut_audit_detects_certificate_corruption(self) -> None:
        effects = np.asarray(
            [
                [0.0, 0.4, 0.1, 0.2],
                [0.3, 0.0, 0.5, 0.1],
                [0.2, 0.3, 0.0, 0.4],
                [0.1, 0.2, 0.3, 0.0],
            ],
            dtype=np.float64,
        )
        record = _certificate_record(effects)
        self.assertTrue(_audit_closure_row(record)["passed"])
        corrupted = json.loads(json.dumps(record))
        corrupted["closure_cut_certificate"]["reachable_set"] = [
            corrupted["closure_cut_certificate"]["source"],
            corrupted["closure_cut_certificate"]["target"],
        ]
        self.assertFalse(_audit_closure_row(corrupted)["passed"])


class V04RunnerTests(unittest.TestCase):
    def test_small_real_path_runner_retains_all_cells_and_refuses_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            summary = run_path_decomposition(
                directory,
                seeds=(3,),
                train_episode_count=8,
                test_episode_count=8,
                intervention_horizon=2,
                bootstrap_resamples=100,
            )
            self.assertEqual(summary["status"], "completed_without_seed_filtering")
            self.assertEqual(len(summary["runs"]), 8)
            self.assertTrue(summary["all_cut_audits_passed"])
            self.assertTrue(all(row["self_learning_updates_during_test"] == 0 for row in summary["runs"]))
            self.assertTrue(all("conjunctive_signature" in row for row in summary["runs"]))
            self.assertTrue(
                all(
                    row["loaded_predictor_snapshot_id"]
                    == row["predictor_snapshot_id"]
                    for row in summary["runs"]
                )
            )
            for name in (
                "path_decomposition.json",
                "path_decomposition.csv",
                "path_decomposition.png",
            ):
                self.assertTrue((Path(directory) / name).is_file())
            with self.assertRaisesRegex(ValueError, "new or empty"):
                run_path_decomposition(
                    directory,
                    seeds=(3,),
                    train_episode_count=8,
                    test_episode_count=8,
                    bootstrap_resamples=10,
                )

    def test_path_runner_retains_every_planned_cell_after_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.evaluate_variant",
            side_effect=RuntimeError("deliberate path failure"),
        ):
            summary = run_path_decomposition(
                directory,
                seeds=(13,),
                train_episode_count=8,
                test_episode_count=8,
                bootstrap_resamples=10,
            )
            self.assertEqual(summary["status"], "stopped_protocol_contradiction")
            self.assertEqual(len(summary["runs"]), 8)
            self.assertTrue(
                all(row["row_status"] == "protocol_exception" for row in summary["runs"])
            )
            self.assertTrue((Path(directory) / "path_decomposition.json").is_file())

    def test_structured_csv_round_trips_null_empty_list_and_empty_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "structured.csv"
            _write_structured_csv(
                path,
                ("causal_effects", "closure_cut_certificate", "jacobian_shape"),
                [
                    {
                        "causal_effects": None,
                        "closure_cut_certificate": {},
                        "jacobian_shape": [],
                    }
                ],
            )
            values = path.read_text(encoding="utf-8").splitlines()[1].split(",")
            # CSV quoting makes manual splitting ambiguous for nonempty arrays,
            # but these exact tokens must remain distinct and JSON-decodable.
            self.assertIn("null", values)
            self.assertIn("{}", values)
            self.assertIn("[]", values)

    def test_warmed_diagnostics_preserve_terminal_agent_and_use_full_warmup(self) -> None:
        agent = _agent(11)
        episode = _episodes(8, seed=12, delay=3)[0]
        for observation in episode.observations:
            agent.step(observation, source="test_full_warmup")
        terminal_time = agent.time
        terminal_workspace = agent.workspace.state.copy()
        diagnostics = _warmed_intervention_diagnostics(agent, horizon=2)
        self.assertEqual(agent.time, terminal_time)
        np.testing.assert_array_equal(agent.workspace.state, terminal_workspace)
        self.assertEqual(diagnostics.baseline.shape[0], 2)
        self.assertEqual(diagnostics.interventions.shape[:2], (4, 2))

    def test_local_runner_retains_158_signatures_and_deterministic_npy_hashes(self) -> None:
        summaries = []
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for directory in (first, second):
                summaries.append(
                    run_local_dynamics(
                        directory,
                        seeds=(5,),
                        recurrent_gains=(0.0, 1.0),
                        train_episode_count=8,
                        intervention_horizon=2,
                        bootstrap_resamples=100,
                    )
                )
            first_rows, second_rows = summaries[0]["runs"], summaries[1]["runs"]
            self.assertEqual(
                [row["jacobian_sha256"] for row in first_rows],
                [row["jacobian_sha256"] for row in second_rows],
            )
            for directory, row in zip((first, first), first_rows):
                matrix_path = Path(directory) / row["jacobian_file"]
                matrix = np.load(matrix_path, allow_pickle=False)
                self.assertEqual(matrix.shape, (158, 158))
                self.assertEqual(len(row["positive_branch_signatures"]), 158)
                self.assertEqual(len(row["negative_branch_signatures"]), 158)
                self.assertEqual(
                    hashlib.sha256(matrix_path.read_bytes()).hexdigest(),
                    row["jacobian_sha256"],
                )
            self.assertIn("per_gain_aggregates", summaries[0])
            self.assertIn("supporting_recurrence_vs_persistence", summaries[0])

    def test_local_runner_retains_exception_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.local_transition_jacobian",
            side_effect=RuntimeError("deliberate local failure"),
        ):
            summary = run_local_dynamics(
                directory,
                seeds=(7,),
                recurrent_gains=(0.0, 1.0),
                train_episode_count=8,
                intervention_horizon=2,
                bootstrap_resamples=10,
            )
            self.assertEqual(summary["status"], "stopped_protocol_contradiction")
            self.assertEqual(len(summary["runs"]), 2)
            self.assertTrue(
                all(row["row_status"] == "protocol_exception" for row in summary["runs"])
            )
            self.assertTrue((Path(directory) / "local_dynamics.json").is_file())

    def test_local_runner_retains_raw_matrix_exposed_by_failure(self) -> None:
        class RawJacobianFailure(RuntimeError):
            def __init__(self) -> None:
                super().__init__("deliberate nonfinite Jacobian")
                self.jacobian = np.full((158, 158), np.nan, dtype=np.float64)
                self.completed_columns = 17
                self.stage = "finite_check"
                self.epsilon = 1e-5
                self.state_dimension = 158
                self.positive_branch_signatures = ()
                self.negative_branch_signatures = ()

        with tempfile.TemporaryDirectory() as directory, patch(
            "rrct.experiments.local_transition_jacobian",
            side_effect=RawJacobianFailure(),
        ):
            summary = run_local_dynamics(
                directory,
                seeds=(17,),
                recurrent_gains=(0.0, 1.0),
                train_episode_count=8,
                intervention_horizon=2,
                bootstrap_resamples=10,
            )
            row = summary["runs"][0]
            self.assertTrue(row["raw_jacobian_retained"])
            self.assertFalse(row["raw_jacobian_finite"])
            self.assertEqual(row["raw_jacobian_nonfinite_count"], 158 * 158)
            self.assertEqual(row["jacobian_completed_columns"], 17)
            self.assertEqual(row["jacobian_failure_stage"], "finite_check")
            matrix_path = Path(directory) / row["jacobian_file"]
            self.assertTrue(matrix_path.is_file())
            self.assertTrue(np.isnan(np.load(matrix_path, allow_pickle=False)).all())
            self.assertIn(row["jacobian_file"], summary["artifacts"])


class V04CliTests(unittest.TestCase):
    def test_cli_maps_every_frozen_path_and_local_option(self) -> None:
        parser = build_parser()
        path = parser.parse_args(
            [
                "path-decomposition",
                "--seeds",
                "3,5",
                "--recurrent-gains",
                "0,1",
                "--self-feedback-gains",
                "0",
                "1",
                "--action-feedback-gains",
                "0,1",
                "--closure-gain",
                "0.8",
                "--train-delay",
                "4",
                "--test-delay",
                "9",
                "--horizon",
                "6",
                "--bootstrap-seed",
                "99",
            ]
        )
        self.assertEqual(_flatten_tokens(path.seeds), (3, 5))
        self.assertEqual(_flatten_tokens(path.recurrent_gains), (0.0, 1.0))
        self.assertEqual(path.closure_gain, 0.8)
        self.assertEqual(path.intervention_horizon, 6)
        self.assertEqual(path.bootstrap_seed, 99)

        local = parser.parse_args(
            [
                "local-dynamics",
                "--seeds",
                "7,11",
                "--gains",
                "0,.5,1",
                "--closure-gain",
                ".9",
                "--self-feedback-gain",
                ".8",
                "--action-feedback-gain",
                ".7",
                "--warmup-episodes",
                "1",
                "--finite-difference-epsilon",
                "2e-5",
                "--persistence-horizon",
                "5",
                "--bootstrap-seed",
                "101",
            ]
        )
        self.assertEqual(_flatten_tokens(local.seeds), (7, 11))
        self.assertEqual(_flatten_tokens(local.recurrent_gains), (0.0, 0.5, 1.0))
        self.assertEqual(local.warmup_episodes, 1)
        self.assertEqual(local.epsilon, 2e-5)
        self.assertEqual(local.intervention_horizon, 5)
        self.assertEqual(local.bootstrap_seed, 101)
        defaults = parser.parse_args(["local-dynamics"])
        self.assertEqual(_flatten_tokens(defaults.seeds), V04_VALIDATION_SEEDS)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from osl_lab.replication import AggregationError, aggregate_runs, render_markdown, write_aggregate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _package_manifest_sha256() -> str:
    manifest = Path(__file__).resolve().parent.parent / "MANIFEST.json"
    return _sha256_file(manifest) if manifest.is_file() else "a" * 64


def _classification(accuracy: float, n: int = 100) -> dict:
    return {
        "n": n,
        "exact_correct": int(round(accuracy * n)),
        "accuracy": accuracy,
        "macro_precision": accuracy - 0.01,
        "macro_recall": accuracy - 0.02,
        "macro_f1": accuracy - 0.015,
        "micro_f1": accuracy,
    }


def _write_diagnostic_arm(
    run: Path,
    arm: str,
    *,
    lexical_accuracy: float,
    canonical_accuracy: float,
    renamed_accuracy: float,
    prediction_consistency: float,
    pair_joint_correctness: float,
    change_sensitivity: float,
    invariance_specificity: float,
    pair_level_completeness: float,
    pair_level_specificity: float,
    heldout_pair_accuracy: float | None = None,
    heldout_triple_accuracy: float | None = None,
    renaming_split_accuracy: float | None = None,
    correct_minus_scrambled_accuracy: float = 0.0,
    correct_vs_scrambled_prediction_change: float = 0.0,
) -> None:
    heldout_pair_accuracy = (
        lexical_accuracy if heldout_pair_accuracy is None else heldout_pair_accuracy
    )
    heldout_triple_accuracy = (
        lexical_accuracy if heldout_triple_accuracy is None else heldout_triple_accuracy
    )
    renaming_split_accuracy = (
        renamed_accuracy if renaming_split_accuracy is None else renaming_split_accuracy
    )
    experiment = run / "experiments" / f"transformer__{arm}"
    _write(experiment / "training_summary.json", {"arm": arm})
    _write(
        experiment / "evaluation_results.json",
        {
            "behavior": {
                "splits": {
                    "lexical": _classification(lexical_accuracy),
                    "heldout_pair": _classification(heldout_pair_accuracy),
                    "heldout_triple": _classification(heldout_triple_accuracy),
                    "renaming": _classification(renaming_split_accuracy),
                },
                "renaming": {
                    "declared_groups": 20,
                    "pair_groups": 20,
                    "triplet_groups": 20,
                    "canonical_accuracy": canonical_accuracy,
                    "renamed_accuracy": renamed_accuracy,
                    "prediction_consistency": prediction_consistency,
                    "pair_joint_correctness": pair_joint_correctness,
                    "robustness_gap": canonical_accuracy - renamed_accuracy,
                    "correct_calibration_accuracy": renamed_accuracy,
                    "scrambled_accuracy": renamed_accuracy
                    - correct_minus_scrambled_accuracy,
                    "correct_minus_scrambled_accuracy": correct_minus_scrambled_accuracy,
                    "correct_vs_scrambled_prediction_change": correct_vs_scrambled_prediction_change,
                    "correct_only_success_rate": max(0.0, correct_minus_scrambled_accuracy),
                },
            },
            "counterfactual": {
                "pair_groups": 10,
                "affected_pair_groups": 10,
                "unaffected_pair_groups": 10,
                "affected_queries": 20,
                "unaffected_queries": 20,
                "affected_joint_accuracy": change_sensitivity - 0.05,
                "unaffected_joint_accuracy": invariance_specificity - 0.05,
                "change_sensitivity": change_sensitivity,
                "invariance_specificity": invariance_specificity,
                "pair_level_completeness": pair_level_completeness,
                "pair_level_specificity": pair_level_specificity,
            },
        },
    )


def _run(
    root: Path,
    name: str,
    *,
    data_seed: int,
    model_seed: int,
    lexical_accuracy: float,
    completed: bool = True,
    gate_status: str = "PASS",
) -> Path:
    run = root / name
    _write(
        run / "run_metadata.json",
        {
            "schema": "osl.micro-emergence.run-metadata.v1",
            "data_seed": data_seed,
            "model_seed": model_seed,
            "package_manifest_sha256": _package_manifest_sha256(),
            "completed": completed,
        },
    )
    _write(
        run / "manifest.json",
        {
            "files": {
                "lexical": {
                    "path": "lexical.jsonl",
                    "records": 100,
                    "sha256": _sha256_text(f"lexical-bytes-data-seed-{data_seed}"),
                    "semantic_sha256": _sha256_text(
                        f"lexical-semantic-data-seed-{data_seed}"
                    ),
                }
            }
        },
    )
    _write(
        run / "baseline_results.json",
        {
            "models": {
                "majority": {
                    "by_split": {"splits": {"lexical": _classification(0.45)}}
                },
                "tfidf": {
                    "by_split": {"splits": {"lexical": _classification(0.55)}}
                },
            }
        },
    )
    experiment = run / "experiments" / "transformer__answer_only"
    _write(experiment / "training_summary.json", {"arm": "answer_only"})
    _write(
        experiment / "evaluation_results.json",
        {"behavior": {"splits": {"lexical": _classification(lexical_accuracy)}}},
    )
    _write(
        run / "EVIDENCE_ADJUDICATION.json",
        {
            "arm": "answer_only",
            "architecture": None,
            "gates": {
                "lexical_beyond_control": {
                    "status": gate_status,
                    "observed": lexical_accuracy,
                }
            },
        },
    )
    return run


def _config(
    path: Path,
    *,
    arms: list[str] | None = None,
    data_seeds: list[int] | None = None,
    model_seeds: list[int] | None = None,
    splits: list[str] | None = None,
    learned_binding_gate: dict | None = None,
) -> Path:
    replication = {
        "data_seeds": data_seeds or [101, 202],
        "model_seeds": model_seeds or [11],
        "baseline_gate_min_margin": 0.0,
    }
    if splits is not None:
        replication["splits"] = splits
    if learned_binding_gate is not None:
        replication["learned_binding_gate"] = learned_binding_gate
    _write(
        path,
        {
            "dataset": {
                "split_sizes": {
                    "train": 10,
                    "renaming_train": 5,
                    "renaming_scrambled_train": 5,
                    "iid_validation": 5,
                    "lexical": 10,
                }
            },
            "training": {
                "architectures": ["transformer"],
                "arms": arms or ["answer_only"],
            },
            "replication": replication,
        },
    )
    config_sha256 = _sha256_file(path)
    for metadata_path in sorted((path.parent / "runs").rglob("run_metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["config_sha256"] = config_sha256
        _write(metadata_path, metadata)
    return path


def _three_arm_cell(
    root: Path,
    *,
    data_seed: int,
    model_seed: int,
    correct_gain: float = 0.10,
) -> Path:
    run = _run(
        root,
        f"data_{data_seed}/model_{model_seed}",
        data_seed=data_seed,
        model_seed=model_seed,
        lexical_accuracy=0.58,
    )
    common = {
        "change_sensitivity": 0.70,
        "invariance_specificity": 0.78,
        "pair_level_completeness": 0.62,
        "pair_level_specificity": 0.74,
    }
    _write_diagnostic_arm(
        run,
        "answer_only",
        lexical_accuracy=0.58,
        canonical_accuracy=0.76,
        renamed_accuracy=0.50,
        prediction_consistency=0.62,
        pair_joint_correctness=0.45,
        heldout_pair_accuracy=0.64,
        heldout_triple_accuracy=0.60,
        correct_minus_scrambled_accuracy=0.0,
        **common,
    )
    _write_diagnostic_arm(
        run,
        "role_bind_scrambled",
        lexical_accuracy=0.62,
        canonical_accuracy=0.78,
        renamed_accuracy=0.58,
        prediction_consistency=0.72,
        pair_joint_correctness=0.56,
        heldout_pair_accuracy=0.70,
        heldout_triple_accuracy=0.66,
        correct_minus_scrambled_accuracy=0.01,
        correct_vs_scrambled_prediction_change=0.08,
        **common,
    )
    _write_diagnostic_arm(
        run,
        "role_bind_augmented",
        lexical_accuracy=0.64,
        canonical_accuracy=0.80,
        renamed_accuracy=0.58 + correct_gain,
        prediction_consistency=0.86,
        pair_joint_correctness=0.56 + correct_gain,
        heldout_pair_accuracy=0.68,
        heldout_triple_accuracy=0.64,
        correct_minus_scrambled_accuracy=correct_gain,
        correct_vs_scrambled_prediction_change=0.32,
        **common,
    )
    return run


def test_crossed_seed_aggregation_and_gate_rates(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _run(runs, "data_101/model_11", data_seed=101, model_seed=11, lexical_accuracy=0.60)
    _run(
        runs,
        "data_202/model_11",
        data_seed=202,
        model_seed=11,
        lexical_accuracy=0.50,
        gate_status="FAIL",
    )
    result = aggregate_runs(runs, config=_config(tmp_path / "confirmatory.json"))

    assert result["matrix_completeness"]["complete"] is True
    assert len(result["replicates"]) == 2
    assert [row["data_seed"] for row in result["replicates"]] == [101, 202]
    summary = result["summaries"]["per_arm_split"][0]
    accuracy = summary["metrics"]["accuracy"]
    assert accuracy["mean"] == pytest.approx(0.55)
    assert accuracy["sd"] == pytest.approx(math.sqrt(0.005))
    assert accuracy["min"] == 0.50
    assert accuracy["max"] == 0.60
    assert summary["strongest_baseline_gate"]["counts"] == {
        "PASS": 1,
        "FAIL": 1,
        "INCOMPLETE": 0,
    }
    explicit = result["summaries"]["explicit_behavioral_gates"][0]
    assert explicit["gate"] == "lexical_beyond_control"
    assert explicit["pass_rate_all"] == 0.5


def test_incomplete_runs_are_excluded_and_reported(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _run(
        runs,
        "complete",
        data_seed=101,
        model_seed=11,
        lexical_accuracy=0.60,
    )
    _run(
        runs,
        "partial",
        data_seed=202,
        model_seed=11,
        lexical_accuracy=0.99,
        completed=False,
    )
    result = aggregate_runs(runs, config=_config(tmp_path / "confirmatory.json"))
    assert len(result["replicates"]) == 1
    assert result["replicates"][0]["accuracy"] == 0.60
    assert result["skipped_runs"] == [
        {"run": "partial", "reason": "run_metadata.completed is not true"}
    ]
    assert result["matrix_completeness"]["missing_runs"] == [
        {"data_seed": 202, "model_seed": 11}
    ]


def test_strict_mode_rejects_duplicate_seed_cells(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _run(runs, "first", data_seed=101, model_seed=11, lexical_accuracy=0.60)
    _run(runs, "retry", data_seed=101, model_seed=11, lexical_accuracy=0.62)
    with pytest.raises(AggregationError, match="duplicate evaluation"):
        aggregate_runs(runs, strict=True)


def test_json_and_markdown_are_deterministic(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _run(runs, "z_run", data_seed=202, model_seed=11, lexical_accuracy=0.50)
    _run(runs, "a_run", data_seed=101, model_seed=11, lexical_accuracy=0.60)
    config = _config(tmp_path / "confirmatory.json")
    first = aggregate_runs(runs, config=config)
    first_markdown = render_markdown(first)
    output = tmp_path / "aggregate"
    write_aggregate(first, output)
    json_bytes = (output / "REPLICATION_SUMMARY.json").read_bytes()
    markdown_bytes = (output / "REPLICATION_REPORT.md").read_bytes()

    second = aggregate_runs(runs, config=config)
    write_aggregate(second, output)
    assert second == first
    assert render_markdown(second) == first_markdown
    assert (output / "REPLICATION_SUMMARY.json").read_bytes() == json_bytes
    assert (output / "REPLICATION_REPORT.md").read_bytes() == markdown_bytes


def test_expected_seed_flags_override_config_seed_grid(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _run(runs, "only", data_seed=7, model_seed=8, lexical_accuracy=0.60)
    result = aggregate_runs(
        runs,
        config=_config(tmp_path / "confirmatory.json"),
        expected_data_seeds=[7],
        expected_model_seeds=[8],
    )
    assert result["expected"]["data_seeds"] == [7]
    assert result["expected"]["model_seeds"] == [8]
    assert result["matrix_completeness"]["complete"] is True


def test_mislabeled_seed_artifacts_are_not_aggregated(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run = _run(runs, "bad", data_seed=101, model_seed=11, lexical_accuracy=0.60)
    _write(run / "resolved_config.json", {"data_seed": 999, "model_seed": 11})
    result = aggregate_runs(runs)
    assert result["replicates"] == []
    assert result["errors"] == [
        {
            "run": "bad",
            "reason": "resolved_config.data_seed=999 does not match run metadata 101",
        }
    ]


def test_paired_role_binding_diagnostics_and_within_seed_contrast(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run = _run(
        runs,
        "data_101/model_11",
        data_seed=101,
        model_seed=11,
        lexical_accuracy=0.60,
    )
    _write_diagnostic_arm(
        run,
        "answer_only",
        lexical_accuracy=0.60,
        canonical_accuracy=0.80,
        renamed_accuracy=0.50,
        prediction_consistency=0.60,
        pair_joint_correctness=0.45,
        change_sensitivity=0.55,
        invariance_specificity=0.75,
        pair_level_completeness=0.40,
        pair_level_specificity=0.70,
        heldout_pair_accuracy=0.66,
        heldout_triple_accuracy=0.62,
        correct_minus_scrambled_accuracy=0.01,
    )
    _write_diagnostic_arm(
        run,
        "role_bind_scrambled",
        lexical_accuracy=0.62,
        canonical_accuracy=0.81,
        renamed_accuracy=0.60,
        prediction_consistency=0.72,
        pair_joint_correctness=0.56,
        change_sensitivity=0.60,
        invariance_specificity=0.76,
        pair_level_completeness=0.45,
        pair_level_specificity=0.71,
        heldout_pair_accuracy=0.70,
        heldout_triple_accuracy=0.66,
        correct_minus_scrambled_accuracy=0.01,
        correct_vs_scrambled_prediction_change=0.10,
    )
    _write_diagnostic_arm(
        run,
        "role_bind_augmented",
        lexical_accuracy=0.64,
        canonical_accuracy=0.82,
        renamed_accuracy=0.78,
        prediction_consistency=0.90,
        pair_joint_correctness=0.72,
        change_sensitivity=0.80,
        invariance_specificity=0.78,
        pair_level_completeness=0.70,
        pair_level_specificity=0.72,
        heldout_pair_accuracy=0.68,
        heldout_triple_accuracy=0.64,
        correct_minus_scrambled_accuracy=0.12,
        correct_vs_scrambled_prediction_change=0.35,
    )
    config = _config(
        tmp_path / "confirmatory.json",
        arms=["answer_only", "role_bind_augmented", "role_bind_scrambled"],
        data_seeds=[101],
        model_seeds=[11],
        splits=["lexical", "heldout_pair", "heldout_triple", "renaming"],
        learned_binding_gate={"minimum_positive_seed_cells": 1},
    )
    result = aggregate_runs(
        runs,
        config=config,
        expected_data_seeds=[101],
        expected_model_seeds=[11],
    )

    assert result["matrix_completeness"]["complete"] is True
    diagnostics = {row["arm"]: row for row in result["diagnostic_replicates"]}
    assert set(diagnostics) == {
        "answer_only",
        "role_bind_scrambled",
        "role_bind_augmented",
    }
    assert {
        "canonical_accuracy",
        "renamed_accuracy",
        "prediction_consistency",
        "pair_joint_correctness",
        "robustness_gap",
        "pair_groups",
        "triplet_groups",
        "correct_minus_scrambled_accuracy",
    } <= set(diagnostics["answer_only"]["renaming"])
    assert set(diagnostics["answer_only"]["counterfactual"]) == {
        "pair_groups",
        "affected_pair_groups",
        "unaffected_pair_groups",
        "affected_queries",
        "unaffected_queries",
        "affected_joint_accuracy",
        "unaffected_joint_accuracy",
        "change_sensitivity",
        "invariance_specificity",
        "pair_level_completeness",
        "pair_level_specificity",
    }

    contrast = result["role_binding_contrasts"][0]
    assert contrast["data_seed"] == 101
    assert contrast["model_seed"] == 11
    assert contrast["complete"] is True
    assert contrast["diagnostics"]["renaming"]["renamed_accuracy"][
        "role_bind_augmented_minus_role_bind_scrambled"
    ] == pytest.approx(0.18)
    assert contrast["diagnostics"]["renaming"]["renamed_accuracy"][
        "role_bind_augmented_minus_answer_only"
    ] == pytest.approx(0.28)
    assert contrast["splits"]["heldout_pair"][
        "role_bind_augmented_minus_role_bind_scrambled"
    ] == pytest.approx(-0.02)
    assert contrast["primary"]["correct_calibration_gain_at_test"] == 0.12
    assert result["role_binding_contrast_issues"] == []

    summary = result["summaries"]["learned_role_binding_contrast"][0]
    endpoints = summary["diagnostics"]["renaming"]["prediction_consistency"]
    assert endpoints["answer_only"]["mean"] == 0.60
    assert endpoints["role_bind_scrambled"]["mean"] == 0.72
    assert endpoints["role_bind_augmented"]["mean"] == 0.90
    assert endpoints[
        "role_bind_augmented_minus_role_bind_scrambled"
    ]["mean"] == pytest.approx(0.18)
    assert summary["splits"]["heldout_triple"][
        "role_bind_augmented_minus_role_bind_scrambled"
    ]["mean"] == pytest.approx(-0.02)
    assert result["learned_binding_h2_gate"]["status"] == "PASS"
    markdown = render_markdown(result)
    assert "Bounded learned-binding contrast (not emergence)" in markdown
    assert "| transformer | renamed_accuracy | 1 |" in markdown
    assert "does not establish emergence" in markdown


def test_six_cell_h2_gate_uses_crossed_seed_strata(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    for data_seed in (101, 202):
        for model_seed in (11, 22, 33):
            _three_arm_cell(
                runs,
                data_seed=data_seed,
                model_seed=model_seed,
                correct_gain=0.10,
            )
    config = _config(
        tmp_path / "confirmatory.json",
        arms=["answer_only", "role_bind_augmented", "role_bind_scrambled"],
        data_seeds=[101, 202],
        model_seeds=[11, 22, 33],
        splits=["lexical", "heldout_pair", "heldout_triple", "renaming"],
        learned_binding_gate={
            "minimum_mean_renamed_accuracy_gain_over_scrambled_arm": 0.05,
            "minimum_mean_pair_joint_gain_over_scrambled_arm": 0.05,
            "minimum_mean_correct_calibration_gain_at_test": 0.05,
            "minimum_positive_seed_cells": 5,
            "require_positive_each_data_seed_mean": True,
            "minimum_correct_arm_renamed_accuracy": 0.60,
            "minimum_correct_arm_prediction_consistency": 0.80,
            "minimum_correct_arm_pair_joint_correctness": 0.55,
            "maximum_mean_heldout_pair_accuracy_loss": 0.05,
            "maximum_mean_heldout_triple_accuracy_loss": 0.05,
        },
    )
    result = aggregate_runs(runs, config=config)

    gate = result["learned_binding_h2_gate"]
    assert gate["status"] == "PASS"
    architecture = gate["architectures"][0]
    assert architecture["expected_crossed_cells"] == 6
    assert architecture["complete_crossed_cells"] == 6
    assert architecture["positive_complete_cells"] == 6
    assert all(
        row["all_primary_means_positive"]
        for row in architecture["data_seed_positive_effects"]
    )
    assert len(architecture["crossed_seed_strata"]["by_data_seed"]) == 2
    assert len(architecture["crossed_seed_strata"]["by_model_seed"]) == 3
    summary = result["summaries"]["learned_role_binding_contrast"][0]
    assert len(summary["strata"]["by_data_seed"]) == 2
    assert len(summary["strata"]["by_model_seed"]) == 3
    assert summary["primary_metrics"][
        "renamed_accuracy_gain_over_scrambled_arm"
    ]["mean"] == pytest.approx(0.10)
    assert summary["splits"]["heldout_pair"][
        "role_bind_augmented_minus_role_bind_scrambled"
    ]["mean"] == pytest.approx(-0.02)
    assert "not assumed IID datasets" in gate["analysis_unit"]


def test_h2_gate_fails_when_only_four_of_six_cells_are_positive(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    for data_seed in (101, 202):
        for model_seed in (11, 22, 33):
            _three_arm_cell(
                runs,
                data_seed=data_seed,
                model_seed=model_seed,
                correct_gain=-0.01 if model_seed == 33 else 0.10,
            )
    config = _config(
        tmp_path / "confirmatory.json",
        arms=["answer_only", "role_bind_augmented", "role_bind_scrambled"],
        data_seeds=[101, 202],
        model_seeds=[11, 22, 33],
        splits=["lexical", "heldout_pair", "heldout_triple", "renaming"],
        learned_binding_gate={"minimum_positive_seed_cells": 5},
    )
    result = aggregate_runs(runs, config=config)

    architecture = result["learned_binding_h2_gate"]["architectures"][0]
    assert result["learned_binding_h2_gate"]["status"] == "FAIL"
    assert architecture["positive_complete_cells"] == 4
    assert architecture["checks"]["positive_complete_seed_cells"]["status"] == "FAIL"
    assert architecture["checks"][
        "mean_renamed_accuracy_gain_over_scrambled_arm"
    ]["status"] == "PASS"
    assert all(
        row["all_primary_means_positive"]
        for row in architecture["data_seed_positive_effects"]
    )


def test_missing_scrambled_arm_preserves_partial_report_and_incomplete_gate(
    tmp_path: Path,
) -> None:
    runs = tmp_path / "runs"
    run = _run(
        runs,
        "data_101/model_11",
        data_seed=101,
        model_seed=11,
        lexical_accuracy=0.58,
    )
    common = {
        "canonical_accuracy": 0.78,
        "renamed_accuracy": 0.68,
        "prediction_consistency": 0.86,
        "pair_joint_correctness": 0.66,
        "change_sensitivity": 0.70,
        "invariance_specificity": 0.78,
        "pair_level_completeness": 0.62,
        "pair_level_specificity": 0.74,
        "heldout_pair_accuracy": 0.68,
        "heldout_triple_accuracy": 0.64,
        "correct_minus_scrambled_accuracy": 0.10,
    }
    _write_diagnostic_arm(run, "answer_only", lexical_accuracy=0.58, **common)
    _write_diagnostic_arm(run, "role_bind_augmented", lexical_accuracy=0.64, **common)
    config = _config(
        tmp_path / "confirmatory.json",
        arms=["answer_only", "role_bind_augmented", "role_bind_scrambled"],
        data_seeds=[101],
        model_seeds=[11],
        splits=["lexical", "heldout_pair", "heldout_triple", "renaming"],
        learned_binding_gate={"minimum_positive_seed_cells": 1},
    )
    result = aggregate_runs(runs, config=config)

    assert result["learned_binding_h2_gate"]["status"] == "INCOMPLETE"
    assert result["role_binding_contrast_issues"] == [
        {
            "data_seed": 101,
            "model_seed": 11,
            "architecture": "transformer",
            "arm_row_counts": {
                "answer_only": 1,
                "role_bind_scrambled": 0,
                "role_bind_augmented": 1,
            },
            "reason": "contrast requires exactly one evaluation for all three central arms",
        }
    ]
    assert {row["arm"] for row in result["summaries"]["per_arm_split"]} == {
        "answer_only",
        "role_bind_augmented",
    }
    assert "No complete matched three-arm seed cells were available." in render_markdown(result)


def test_scrambled_training_shard_is_not_an_expected_evaluation_split(
    tmp_path: Path,
) -> None:
    runs = tmp_path / "runs"
    _run(runs, "one", data_seed=101, model_seed=11, lexical_accuracy=0.60)
    result = aggregate_runs(
        runs,
        config=_config(
            tmp_path / "confirmatory.json",
            data_seeds=[101],
            model_seeds=[11],
        ),
    )
    assert result["expected"]["splits"] == ["lexical"]


def test_config_hash_mismatch_excludes_only_the_invalid_run(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    bad = _run(
        runs,
        "data_101/model_11",
        data_seed=101,
        model_seed=11,
        lexical_accuracy=0.99,
    )
    _run(
        runs,
        "data_202/model_11",
        data_seed=202,
        model_seed=11,
        lexical_accuracy=0.60,
    )
    config = _config(tmp_path / "confirmatory.json")
    metadata_path = bad / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["config_sha256"] = "0" * 64
    _write(metadata_path, metadata)

    result = aggregate_runs(runs, config=config)

    assert [(row["data_seed"], row["accuracy"]) for row in result["replicates"]] == [
        (202, 0.60)
    ]
    assert result["completed_runs"] == [
        {
            "run": "data_202/model_11",
            "data_seed": 202,
            "model_seed": 11,
            "evaluation_rows": 1,
        }
    ]
    assert result["errors"][0]["run"] == "data_101/model_11"
    assert "does not match the supplied config" in result["errors"][0]["reason"]
    assert result["provenance_audit"]["supplied_config_sha256"] == _sha256_file(config)
    assert (
        result["provenance_audit"]["accepted_package_manifest_sha256"]
        == result["provenance_audit"]["current_package_manifest_sha256"]
        == _package_manifest_sha256()
    )
    with pytest.raises(AggregationError, match="invalid completed run artifact"):
        aggregate_runs(runs, config=config, strict=True)


def test_nonuniform_package_hashes_are_all_excluded_without_local_manifest(
    tmp_path: Path,
) -> None:
    import osl_lab.replication as replication_module

    runs = tmp_path / "runs"
    first = _run(runs, "first", data_seed=101, model_seed=11, lexical_accuracy=0.60)
    second = _run(runs, "second", data_seed=202, model_seed=11, lexical_accuracy=0.61)
    first_metadata_path = first / "run_metadata.json"
    second_metadata_path = second / "run_metadata.json"
    first_metadata = json.loads(first_metadata_path.read_text(encoding="utf-8"))
    second_metadata = json.loads(second_metadata_path.read_text(encoding="utf-8"))
    first_metadata["package_manifest_sha256"] = "1" * 64
    second_metadata["package_manifest_sha256"] = "2" * 64
    _write(first_metadata_path, first_metadata)
    _write(second_metadata_path, second_metadata)

    original_project_root = replication_module.PROJECT_ROOT
    replication_module.PROJECT_ROOT = tmp_path / "installed_without_source_manifest"
    try:
        result = aggregate_runs(runs)
        assert result["replicates"] == []
        assert result["completed_runs"] == []
        assert [row["run"] for row in result["errors"]] == ["first", "second"]
        assert all("not uniform" in row["reason"] for row in result["errors"])
        assert result["provenance_audit"]["current_package_manifest_sha256"] is None
        assert result["provenance_audit"]["accepted_package_manifest_sha256"] is None
        with pytest.raises(AggregationError, match="invalid completed run artifact"):
            aggregate_runs(runs, strict=True)
    finally:
        replication_module.PROJECT_ROOT = original_project_root


def test_dataset_manifest_mismatch_excludes_the_entire_data_seed_only(
    tmp_path: Path,
) -> None:
    runs = tmp_path / "runs"
    for data_seed in (101, 202):
        for model_seed in (11, 22):
            _run(
                runs,
                f"data_{data_seed}/model_{model_seed}",
                data_seed=data_seed,
                model_seed=model_seed,
                lexical_accuracy=0.60,
            )
    bad_manifest_path = runs / "data_101/model_22/manifest.json"
    bad_manifest = json.loads(bad_manifest_path.read_text(encoding="utf-8"))
    bad_manifest["files"]["lexical"]["records"] = 99
    _write(bad_manifest_path, bad_manifest)
    config = _config(
        tmp_path / "confirmatory.json",
        data_seeds=[101, 202],
        model_seeds=[11, 22],
    )

    result = aggregate_runs(runs, config=config)

    assert {(row["data_seed"], row["model_seed"]) for row in result["replicates"]} == {
        (202, 11),
        (202, 22),
    }
    assert [row["run"] for row in result["errors"]] == [
        "data_101/model_11",
        "data_101/model_22",
    ]
    assert all("not identical across model seeds" in row["reason"] for row in result["errors"])
    assert set(
        result["provenance_audit"]["accepted_dataset_descriptors_by_data_seed"]
    ) == {"202"}
    assert result["matrix_completeness"]["missing_runs"] == [
        {"data_seed": 101, "model_seed": 11},
        {"data_seed": 101, "model_seed": 22},
    ]
    with pytest.raises(AggregationError, match="invalid completed run artifact"):
        aggregate_runs(runs, config=config, strict=True)

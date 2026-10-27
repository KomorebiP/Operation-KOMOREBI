from __future__ import annotations

import json

import pytest

from osl_lab.adjudication import (
    adjudicate_behavioral_gates,
    adjudicate_learned_binding,
    build_evidence_adjudication,
)
from osl_lab.reporting import build_report


SPLITS = ("lexical", "heldout_pair", "heldout_triple", "renaming")


def _behavior(accuracy: float) -> dict:
    return {
        "splits": {split: {"accuracy": accuracy} for split in SPLITS},
        "balanced": {
            "splits": {
                split: {
                    "world_macro_accuracy": accuracy,
                    "query_macro_accuracy": accuracy,
                    "minimum_world_accuracy": accuracy,
                    "minimum_query_accuracy": accuracy,
                    "world_balanced_accuracy": accuracy,
                    "query_balanced_accuracy": accuracy,
                    "min_cell_accuracy": accuracy,
                }
                for split in SPLITS
            }
        },
    }


def _answer_only() -> dict:
    behavior = _behavior(0.80)
    behavior["renaming"] = {
        "declared_groups": 20,
        "pair_groups": 20,
        "complete_pair_groups": 20,
        "triplet_groups": 20,
        "complete_triplet_groups": 20,
        "pair_completeness": 1.0,
        "triplet_completeness": 1.0,
        "canonical_accuracy": 0.85,
        "renamed_accuracy": 0.80,
        "prediction_consistency": 0.90,
        "pair_joint_correctness": 0.75,
        "gold_consistency": 1.0,
        "robustness_gap": 0.05,
        "correct_calibration_accuracy": 0.80,
        "scrambled_accuracy": 0.55,
        "correct_minus_scrambled_accuracy": 0.25,
        "correct_vs_scrambled_prediction_change": 0.45,
        "correct_only_success_rate": 0.25,
        "triplet_gold_consistency": 1.0,
    }
    return {
        "behavior": behavior,
        "renaming": behavior["renaming"],
        "counterfactual": {
            "pair_groups": 20,
            "affected_joint_accuracy": 0.75,
            "unaffected_joint_accuracy": 0.80,
            "change_sensitivity": 0.90,
            "invariance_specificity": 0.90,
            "pair_level_completeness": 0.70,
            "pair_level_specificity": 0.85,
        },
    }


def _controls() -> dict:
    return {
        "models": {
            "majority": {"by_split": _behavior(0.55)},
            "tfidf": {"by_split": _behavior(0.72)},
        }
    }


def test_behavioral_adjudication_uses_strongest_control() -> None:
    result = adjudicate_behavioral_gates(_answer_only(), _controls())
    assert result["behavioral_status"] == "PASS"
    heldout = result["gates"]["split_advantage"]["splits"]["heldout_triple"]
    assert heldout["strongest_control"] == {"name": "tfidf", "accuracy": 0.72}
    assert heldout["margin_over_strongest_control"] == pytest.approx(0.08)
    assert result["gates"]["paired_renaming"]["status"] == "PASS"
    assert result["gates"]["learned_binding_h2"]["status"] == "PASS"
    assert result["claim_boundary"]["quotient_scope"] == "benchmark_only"
    assert result["claim_boundary"]["automatic_emergence_claim"] is False


def test_missing_paired_renaming_is_incomplete() -> None:
    answer = _answer_only()
    answer.pop("renaming")
    answer["behavior"].pop("renaming")
    result = adjudicate_behavioral_gates(answer, _controls())
    assert result["gates"]["paired_renaming"]["status"] == "INCOMPLETE"
    assert result["behavioral_status"] == "INCOMPLETE"


def test_h2_learned_binding_rejects_calibration_insensitivity() -> None:
    metrics = dict(_answer_only()["renaming"])
    metrics["correct_minus_scrambled_accuracy"] = 0.0
    metrics["correct_vs_scrambled_prediction_change"] = 0.05
    metrics["correct_only_success_rate"] = 0.0
    result = adjudicate_learned_binding(metrics)
    assert result["status"] == "FAIL"
    assert result["checks"]["correct_only_success_rate"]["status"] == "FAIL"
    assert result["latent_mechanism_claim"] is False


def test_adjudication_builder_writes_exact_portable_artifacts(tmp_path) -> None:
    experiment = tmp_path / "experiments" / "transformer__answer_only"
    experiment.mkdir(parents=True)
    (experiment / "evaluation_results.json").write_text(
        json.dumps(_answer_only()), encoding="utf-8"
    )
    (tmp_path / "baseline_results.json").write_text(
        json.dumps(_controls()), encoding="utf-8"
    )
    built = build_evidence_adjudication(tmp_path)
    json_path = tmp_path / "EVIDENCE_ADJUDICATION.json"
    markdown_path = tmp_path / "EVIDENCE_ADJUDICATION.md"
    assert built["json"] == str(json_path)
    assert built["markdown"] == str(markdown_path)
    assert json_path.is_file()
    assert markdown_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["sources"]["answer_only_evaluation"] == (
        "experiments/transformer__answer_only/evaluation_results.json"
    )
    assert payload["sources"]["frozen_controls"] == "baseline_results.json"
    assert payload["gates"]["split_advantage"]["status"] == "PASS"
    assert "benchmark-only" in markdown_path.read_text(encoding="utf-8")


def test_report_summary_is_portable_and_collects_adjudication(tmp_path) -> None:
    experiment = tmp_path / "experiments" / "transformer__answer_only"
    experiment.mkdir(parents=True)
    (experiment / "evaluation_results.json").write_text(
        json.dumps(_answer_only()), encoding="utf-8"
    )
    (tmp_path / "baseline_results.json").write_text(
        json.dumps(_controls()), encoding="utf-8"
    )
    result = build_report(tmp_path, tmp_path / "reports", make_figures=False)
    summary = json.loads((tmp_path / "reports" / "SUMMARY.json").read_text(encoding="utf-8"))
    assert summary["run_dir"] == "."
    assert any(source["path"] == "EVIDENCE_ADJUDICATION.json" for source in summary["sources"])
    assert result["adjudication"]["status"] == "PASS"

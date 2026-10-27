from __future__ import annotations

import numpy as np
import pytest

from osl_lab.metrics import (
    balanced_group_summary,
    classification_metrics,
    compute_algebra_residuals,
    counterfactual_metrics,
    evaluate_by_split,
    paired_renaming_metrics,
)
from osl_lab.soft_quotient import (
    exact_partition,
    fit_soft_quotient,
    lumpability_residual,
    temperature_hardening_sweep,
)


def test_classification_and_split_metrics() -> None:
    records = [
        {"answer": "yes", "split": "iid", "world": "algebra"},
        {"answer": "no", "split": "iid", "world": "algebra"},
        {"answer": "yes", "split": "lexical", "world": "provenance"},
    ]
    predictions = ["yes", "yes", "yes"]
    metrics = classification_metrics([r["answer"] for r in records], predictions)
    assert metrics["accuracy"] == pytest.approx(2 / 3)
    assert metrics["confusion_matrix"] == [[0, 1], [0, 2]]
    split = evaluate_by_split(records, predictions)
    assert split["splits"]["iid"]["accuracy"] == 0.5
    assert split["splits"]["lexical"]["accuracy"] == 1.0


def test_split_query_and_balanced_summaries() -> None:
    records = [
        {"answer": "a", "split": "iid", "world": "w1", "question_id": "q1"},
        {"answer": "b", "split": "iid", "world": "w1", "question_id": "q1"},
        {"answer": "c", "split": "iid", "world": "w1", "question_id": "q2"},
        {"answer": "d", "split": "iid", "world": "w2", "question_id": "q1"},
        {"answer": "e", "split": "lexical", "world": "w2", "question_id": "q1"},
    ]
    predictions = ["a", "wrong", "c", "wrong", "e"]
    result = evaluate_by_split(records, predictions)
    assert result["split_queries"]["iid::w1::q1"]["accuracy"] == 0.5
    assert result["split_queries"]["lexical::w2::q1"]["accuracy"] == 1.0
    iid = result["balanced"]["splits"]["iid"]
    assert iid["world_macro_accuracy"] == pytest.approx((2 / 3 + 0.0) / 2)
    assert iid["query_macro_accuracy"] == pytest.approx((0.5 + 1.0 + 0.0) / 3)
    assert iid["minimum_world_accuracy"] == 0.0
    assert iid["minimum_query_accuracy"] == 0.0
    assert iid["min_cell"]["key"] == "w2::q1"
    direct = balanced_group_summary(records, predictions, split="iid")
    assert direct == iid


def test_paired_renaming_metrics() -> None:
    records = [
        {
            "id": "p1-c",
            "answer": "yes",
            "metadata": {"pair_id": "p1", "variant": "canonical"},
        },
        {
            "id": "p1-r",
            "answer": "yes",
            "metadata": {"pair_id": "p1", "variant": "renamed"},
        },
        {
            "id": "p1-s",
            "answer": "yes",
            "metadata": {"pair_id": "p1", "variant": "scrambled"},
        },
        {
            "id": "p2-c",
            "answer": "no",
            "metadata": {"pair_id": "p2", "variant": "canonical"},
        },
        {
            "id": "p2-r",
            "answer": "no",
            "metadata": {"pair_id": "p2", "variant": "renamed"},
        },
        {
            "id": "p2-s",
            "answer": "no",
            "metadata": {"pair_id": "p2", "variant": "scrambled"},
        },
        {
            "id": "unpaired",
            "answer": "yes",
            "metadata": {"pair_id": "p3", "variant": "canonical"},
        },
    ]
    result = paired_renaming_metrics(
        records, ["yes", "yes", "no", "no", "yes", "yes", "yes"]
    )
    assert result["declared_groups"] == 3
    assert result["pair_groups"] == 2
    assert result["triplet_groups"] == 2
    assert result["pair_completeness"] == pytest.approx(2 / 3)
    assert result["triplet_completeness"] == pytest.approx(2 / 3)
    assert result["canonical_accuracy"] == 1.0
    assert result["renamed_accuracy"] == 0.5
    assert result["prediction_consistency"] == 0.5
    assert result["pair_joint_correctness"] == 0.5
    assert result["gold_consistency"] == 1.0
    assert result["robustness_gap"] == 0.5
    assert result["correct_calibration_accuracy"] == 0.5
    assert result["scrambled_accuracy"] == 0.0
    assert result["correct_minus_scrambled_accuracy"] == 0.5
    assert result["correct_vs_scrambled_prediction_change"] == 0.5
    assert result["correct_only_success_rate"] == 0.5
    assert result["triplet_gold_consistency"] == 1.0
    assert result["unpaired_canonical_records"] == 1


def test_counterfactual_completeness_and_specificity() -> None:
    records = [
        {"question_id": "q1", "answer": "closed", "metadata": {"pair_id": "p", "variant": 0}},
        {"question_id": "q1", "answer": "open", "metadata": {"pair_id": "p", "variant": 1}},
        {"question_id": "q2", "answer": "Mira", "metadata": {"pair_id": "p", "variant": 0}},
        {"question_id": "q2", "answer": "Mira", "metadata": {"pair_id": "p", "variant": 1}},
    ]
    result = counterfactual_metrics(records, ["closed", "open", "Mira", "Mira"])
    assert result["affected_queries"] == 1
    assert result["unaffected_queries"] == 1
    assert result["change_sensitivity"] == 1.0
    assert result["invariance_specificity"] == 1.0
    assert result["pair_level_completeness"] == 1.0
    assert result["pair_level_specificity"] == 1.0


def test_exact_algebraic_relations_have_zero_residual() -> None:
    projection = np.diag([1.0, 0.0])
    swap = np.array([[0.0, 1.0], [1.0, 0.0]])
    diagonal = np.diag([2.0, 3.0])
    matrices = {
        "q": projection,
        "a": swap,
        "a_inv": swap,
        "d": diagonal,
        "product": diagonal @ projection,
    }
    laws = [
        {"kind": "idempotent", "op": "q"},
        {"kind": "inverse", "left": "a", "right": "a_inv"},
        {"kind": "commute", "left": "q", "right": "d"},
        {"kind": "composition", "composed": "product", "left": "d", "right": "q"},
    ]
    result = compute_algebra_residuals(matrices, laws)
    assert result["count"] == 4
    assert result["max_residual"] == pytest.approx(0.0, abs=1e-12)


def test_exact_partition_and_lumpability() -> None:
    transition = np.array(
        [
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ],
        dtype=float,
    )
    transitions = {"flip_within_block": transition}
    observations = np.array([0, 0, 1, 1])
    result = exact_partition(transitions, observations)
    assert result["symbol_count"] == 2
    residual = lumpability_residual(transition, result["membership"])
    assert residual["relative_residual"] == pytest.approx(0.0, abs=1e-12)


def test_fuzzy_quotient_and_temperature_sweep_are_deterministic() -> None:
    transition = np.eye(4)
    transitions = {"stay": transition}
    observations = np.array([[0.0], [0.1], [0.9], [1.0]])
    first = fit_soft_quotient(transitions, observations, 2, seed=9, temperature=0.2)
    second = fit_soft_quotient(transitions, observations, 2, seed=9, temperature=0.2)
    np.testing.assert_allclose(first["membership"], second["membership"])
    assert np.allclose(first["membership"].sum(axis=1), 1.0)
    sweep = temperature_hardening_sweep(
        transitions, observations, 2, [1.0, 0.1], seed=9
    )
    assert [row["temperature"] for row in sweep["rows"]] == [1.0, 0.1]

"""Behavioral, counterfactual, and algebraic metrics for Micro OSL."""

from __future__ import annotations

from collections import defaultdict
import math
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .model import canonical_json


def _safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def classification_metrics(
    gold: Sequence[Any],
    predicted: Sequence[Any],
    *,
    labels: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """Compute exact accuracy and macro/micro categorical statistics."""

    if len(gold) != len(predicted):
        raise ValueError("gold and predicted must have equal lengths")
    gold_strings = [str(value) for value in gold]
    predicted_strings = [str(value) for value in predicted]
    classes = (
        sorted({str(value) for value in labels})
        if labels is not None
        else sorted(set(gold_strings) | set(predicted_strings))
    )
    index = {label: position for position, label in enumerate(classes)}
    confusion = np.zeros((len(classes), len(classes)), dtype=np.int64)
    for truth, guess in zip(gold_strings, predicted_strings):
        if truth not in index or guess not in index:
            raise ValueError("A label was omitted from the explicit label set")
        confusion[index[truth], index[guess]] += 1
    per_class: dict[str, dict[str, float | int]] = {}
    precisions: list[float] = []
    recalls: list[float] = []
    f1_values: list[float] = []
    for label, position in index.items():
        tp = int(confusion[position, position])
        fp = int(confusion[:, position].sum() - tp)
        fn = int(confusion[position, :].sum() - tp)
        support = int(confusion[position, :].sum())
        precision = _safe_divide(tp, tp + fp)
        recall = _safe_divide(tp, tp + fn)
        f1 = _safe_divide(2 * precision * recall, precision + recall)
        precisions.append(precision)
        recalls.append(recall)
        f1_values.append(f1)
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    correct = int(np.trace(confusion))
    total = len(gold_strings)
    return {
        "n": total,
        "accuracy": _safe_divide(correct, total),
        "exact_correct": correct,
        "macro_precision": float(np.mean(precisions)) if precisions else 0.0,
        "macro_recall": float(np.mean(recalls)) if recalls else 0.0,
        "macro_f1": float(np.mean(f1_values)) if f1_values else 0.0,
        "micro_f1": _safe_divide(correct, total),
        "labels": classes,
        "confusion_matrix": confusion.tolist(),
        "per_class": per_class,
    }


def _subset_metrics(
    records: Sequence[Mapping[str, Any]], predictions: Sequence[Any], indices: Sequence[int]
) -> dict[str, Any]:
    return classification_metrics(
        [records[index].get("answer", "") for index in indices],
        [predictions[index] for index in indices],
    )


def _group_accuracy_summary(
    records: Sequence[Mapping[str, Any]],
    predictions: Sequence[Any],
    indices: Sequence[int],
) -> dict[str, Any]:
    """Summarize accuracy without letting large worlds or queries dominate.

    A query cell is a ``world::question_id`` pair.  The minimum-cell endpoint
    is deliberately reported with its key and support so a small weak cell is
    visible rather than hidden inside a pooled score.
    """

    world_groups: dict[str, list[int]] = defaultdict(list)
    query_cells: dict[str, list[int]] = defaultdict(list)
    for index in indices:
        record = records[index]
        world = str(record.get("world", "unspecified"))
        question_id = str(record.get("question_id", record.get("question", "unspecified")))
        world_groups[world].append(index)
        query_cells[f"{world}::{question_id}"].append(index)

    world_metrics = {
        key: _subset_metrics(records, predictions, members)
        for key, members in sorted(world_groups.items())
    }
    cell_metrics = {
        key: _subset_metrics(records, predictions, members)
        for key, members in sorted(query_cells.items())
    }
    world_accuracies = [float(value["accuracy"]) for value in world_metrics.values()]
    cell_accuracies = [float(value["accuracy"]) for value in cell_metrics.values()]
    minimum_world_accuracy = min(world_accuracies) if world_accuracies else 0.0
    minimum_query_accuracy = min(cell_accuracies) if cell_accuracies else 0.0
    minimum_key = (
        min(cell_metrics, key=lambda key: (float(cell_metrics[key]["accuracy"]), key))
        if cell_metrics
        else None
    )
    minimum = cell_metrics.get(minimum_key, {}) if minimum_key is not None else {}
    world_macro_accuracy = float(np.mean(world_accuracies)) if world_accuracies else 0.0
    query_macro_accuracy = float(np.mean(cell_accuracies)) if cell_accuracies else 0.0
    return {
        "n": len(indices),
        "world_count": len(world_metrics),
        "query_cell_count": len(cell_metrics),
        "cell_definition": "world::question_id",
        "world_macro_accuracy": world_macro_accuracy,
        "query_macro_accuracy": query_macro_accuracy,
        "minimum_world_accuracy": minimum_world_accuracy,
        "minimum_query_accuracy": minimum_query_accuracy,
        # Descriptive aliases retained for downstream readers using the first
        # v0.1.1 metric names.
        "world_balanced_accuracy": world_macro_accuracy,
        "query_balanced_accuracy": query_macro_accuracy,
        "min_cell_accuracy": float(minimum.get("accuracy", 0.0)),
        "min_cell": {
            "key": minimum_key,
            "accuracy": float(minimum.get("accuracy", 0.0)),
            "n": int(minimum.get("n", 0)),
        },
    }


def balanced_group_summary(
    records: Sequence[Mapping[str, Any]],
    predictions: Sequence[Any],
    *,
    split: str | None = None,
) -> dict[str, Any]:
    """Return world-balanced, query-balanced, and minimum-cell accuracy.

    When ``split`` is supplied, only records with that exact split label are
    included.  The function is public so report and replication code can use
    the same aggregation rule without reconstructing it from nested metrics.
    """

    if len(records) != len(predictions):
        raise ValueError("records and predictions must have equal lengths")
    indices = [
        index
        for index, record in enumerate(records)
        if split is None or str(record.get("split", "unspecified")) == str(split)
    ]
    return _group_accuracy_summary(records, predictions, indices)


def evaluate_by_split(
    records: Sequence[Mapping[str, Any]], predictions: Sequence[Any]
) -> dict[str, Any]:
    """Evaluate pooled and balanced behavior across the registered groups."""

    if len(records) != len(predictions):
        raise ValueError("records and predictions must have equal lengths")
    all_indices = list(range(len(records)))
    split_groups: dict[str, list[int]] = defaultdict(list)
    world_groups: dict[str, list[int]] = defaultdict(list)
    cross_groups: dict[str, list[int]] = defaultdict(list)
    renderer_groups: dict[str, list[int]] = defaultdict(list)
    query_groups: dict[str, list[int]] = defaultdict(list)
    split_query_groups: dict[str, list[int]] = defaultdict(list)
    law_side_groups: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        split = str(record.get("split", "unspecified"))
        world = str(record.get("world", "unspecified"))
        split_groups[split].append(index)
        world_groups[world].append(index)
        cross_groups[f"{split}::{world}"].append(index)
        renderer_groups[str(record.get("renderer", "unspecified"))].append(index)
        question_id = str(record.get("question_id", record.get("question", "unspecified")))
        query_key = f"{world}::{question_id}"
        query_groups[query_key].append(index)
        split_query_groups[f"{split}::{query_key}"].append(index)
        metadata = _metadata(record)
        if metadata.get("law_side") is not None:
            law_side_groups[str(metadata["law_side"])].append(index)
    overall_balanced = _group_accuracy_summary(records, predictions, all_indices)
    result = {
        "overall": _subset_metrics(records, predictions, all_indices),
        "splits": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(split_groups.items())
        },
        "worlds": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(world_groups.items())
        },
        "split_world": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(cross_groups.items())
        },
        "renderers": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(renderer_groups.items())
        },
        "queries": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(query_groups.items())
        },
        "split_queries": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(split_query_groups.items())
        },
        "law_sides": {
            key: _subset_metrics(records, predictions, indices)
            for key, indices in sorted(law_side_groups.items())
        },
        "balanced": {
            **overall_balanced,
            "overall": overall_balanced,
            "splits": {
                key: _group_accuracy_summary(records, predictions, indices)
                for key, indices in sorted(split_groups.items())
            },
        },
    }
    # Baselines call this function directly, so including the paired diagnostic
    # here makes the same renaming endpoints available to frozen controls.
    result["renaming"] = paired_renaming_metrics(records, predictions)
    return result


def exact_state_accuracy(gold_states: Sequence[Any], predicted_states: Sequence[Any]) -> dict[str, Any]:
    if len(gold_states) != len(predicted_states):
        raise ValueError("gold_states and predicted_states must have equal lengths")
    gold = [canonical_json(value) for value in gold_states]
    predicted = [canonical_json(value) for value in predicted_states]
    correct = sum(a == b for a, b in zip(gold, predicted))
    return {"n": len(gold), "exact_correct": correct, "exact_accuracy": _safe_divide(correct, len(gold))}


def _metadata(record: Mapping[str, Any]) -> Mapping[str, Any]:
    value = record.get("metadata", {})
    return value if isinstance(value, Mapping) else {}


def paired_renaming_metrics(
    records: Sequence[Mapping[str, Any]], predictions: Sequence[Any]
) -> dict[str, Any]:
    """Evaluate semantic preservation and calibration use on renaming triplets.

    Pairing is explicit.  Each eligible record must provide
    ``metadata.pair_id`` and ``metadata.variant``.  Canonical and correctly
    calibrated ``renamed`` variants supply the original pair diagnostic.  A
    ``scrambled`` variant has the same target and token multiset but an
    incorrect calibration, supplying a matched mapping-use control.  Top-level
    fields with the same names are accepted for older hand-built fixtures.  No
    inferred text-similarity pairing is attempted.
    """

    if len(records) != len(predictions):
        raise ValueError("records and predictions must have equal lengths")
    grouped: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    seen = {"canonical": 0, "renamed": 0, "scrambled": 0}
    for index, record in enumerate(records):
        metadata = _metadata(record)
        pair_id = metadata.get("pair_id", record.get("pair_id"))
        variant = str(metadata.get("variant", record.get("variant", ""))).strip().lower()
        if pair_id is None or variant not in seen:
            continue
        grouped[str(pair_id)][variant].append(index)
        seen[variant] += 1

    pair_comparisons: list[tuple[str, int, int]] = []
    triplet_comparisons: list[tuple[str, int, int, int]] = []
    complete_pair_groups = complete_triplet_groups = 0
    unpaired_canonical = unpaired_renamed = unpaired_scrambled = 0
    for pair_id, variants in sorted(grouped.items()):
        canonical = sorted(variants.get("canonical", []), key=lambda i: str(records[i].get("id", i)))
        renamed = sorted(variants.get("renamed", []), key=lambda i: str(records[i].get("id", i)))
        scrambled = sorted(variants.get("scrambled", []), key=lambda i: str(records[i].get("id", i)))
        paired = min(len(canonical), len(renamed))
        tripled = min(len(canonical), len(renamed), len(scrambled))
        complete_pair_groups += int(bool(canonical and renamed))
        complete_triplet_groups += int(bool(canonical and renamed and scrambled))
        pair_comparisons.extend(
            (pair_id, canonical[offset], renamed[offset]) for offset in range(paired)
        )
        triplet_comparisons.extend(
            (pair_id, canonical[offset], renamed[offset], scrambled[offset])
            for offset in range(tripled)
        )
        unpaired_canonical += len(canonical) - paired
        unpaired_renamed += len(renamed) - paired
        unpaired_scrambled += len(scrambled) - tripled

    canonical_correct = renamed_correct = 0
    prediction_matches = joint_correct = gold_matches = 0
    for _, canonical_index, renamed_index in pair_comparisons:
        canonical_gold = str(records[canonical_index].get("answer", ""))
        renamed_gold = str(records[renamed_index].get("answer", ""))
        canonical_prediction = str(predictions[canonical_index])
        renamed_prediction = str(predictions[renamed_index])
        left_correct = canonical_prediction == canonical_gold
        right_correct = renamed_prediction == renamed_gold
        canonical_correct += int(left_correct)
        renamed_correct += int(right_correct)
        prediction_matches += int(canonical_prediction == renamed_prediction)
        joint_correct += int(left_correct and right_correct)
        gold_matches += int(canonical_gold == renamed_gold)

    pair_count = len(pair_comparisons)
    canonical_accuracy = _safe_divide(canonical_correct, pair_count)
    renamed_accuracy = _safe_divide(renamed_correct, pair_count)

    correct_calibration_correct = scrambled_correct = 0
    correct_vs_scrambled_changed = correct_only_success = 0
    triplet_gold_matches = 0
    for _, canonical_index, renamed_index, scrambled_index in triplet_comparisons:
        canonical_gold = str(records[canonical_index].get("answer", ""))
        renamed_gold = str(records[renamed_index].get("answer", ""))
        scrambled_gold = str(records[scrambled_index].get("answer", ""))
        renamed_prediction = str(predictions[renamed_index])
        scrambled_prediction = str(predictions[scrambled_index])
        renamed_is_correct = renamed_prediction == renamed_gold
        scrambled_is_correct = scrambled_prediction == scrambled_gold
        correct_calibration_correct += int(renamed_is_correct)
        scrambled_correct += int(scrambled_is_correct)
        correct_vs_scrambled_changed += int(renamed_prediction != scrambled_prediction)
        correct_only_success += int(renamed_is_correct and not scrambled_is_correct)
        triplet_gold_matches += int(canonical_gold == renamed_gold == scrambled_gold)

    triplet_count = len(triplet_comparisons)
    correct_calibration_accuracy = _safe_divide(correct_calibration_correct, triplet_count)
    scrambled_accuracy = _safe_divide(scrambled_correct, triplet_count)
    group_count = len(grouped)
    return {
        "declared_groups": group_count,
        "pair_groups": pair_count,
        "complete_pair_groups": complete_pair_groups,
        "triplet_groups": triplet_count,
        "complete_triplet_groups": complete_triplet_groups,
        "pair_completeness": _safe_divide(complete_pair_groups, group_count),
        "triplet_completeness": _safe_divide(complete_triplet_groups, group_count),
        "canonical_records": seen["canonical"],
        "renamed_records": seen["renamed"],
        "scrambled_records": seen["scrambled"],
        "unpaired_canonical_records": unpaired_canonical,
        "unpaired_renamed_records": unpaired_renamed,
        "unpaired_scrambled_records": unpaired_scrambled,
        "canonical_accuracy": canonical_accuracy,
        "renamed_accuracy": renamed_accuracy,
        "prediction_consistency": _safe_divide(prediction_matches, pair_count),
        "pair_joint_correctness": _safe_divide(joint_correct, pair_count),
        "gold_consistency": _safe_divide(gold_matches, pair_count),
        "robustness_gap": float(canonical_accuracy - renamed_accuracy),
        "robustness_gap_definition": "canonical_accuracy - renamed_accuracy",
        "correct_calibration_accuracy": correct_calibration_accuracy,
        "scrambled_accuracy": scrambled_accuracy,
        "correct_minus_scrambled_accuracy": float(
            correct_calibration_accuracy - scrambled_accuracy
        ),
        "correct_minus_scrambled_accuracy_definition": (
            "correct_calibration_accuracy - scrambled_accuracy on complete triplets"
        ),
        "correct_vs_scrambled_prediction_change": _safe_divide(
            correct_vs_scrambled_changed, triplet_count
        ),
        "correct_only_success_rate": _safe_divide(correct_only_success, triplet_count),
        "correct_only_success_definition": (
            "renamed prediction correct and matched scrambled prediction wrong"
        ),
        "triplet_gold_consistency": _safe_divide(triplet_gold_matches, triplet_count),
    }


def counterfactual_metrics(
    records: Sequence[Mapping[str, Any]], predictions: Sequence[Any]
) -> dict[str, Any]:
    """Measure completeness on affected queries and specificity elsewhere.

    Records are matched by ``metadata.pair_id`` (or the legacy top-level
    ``counterfactual_group``), then by ``question_id``.  A matched query is
    affected exactly when its gold answer changes across the two variants.
    """

    if len(records) != len(predictions):
        raise ValueError("records and predictions must have equal lengths")
    grouped: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for index, record in enumerate(records):
        meta = _metadata(record)
        pair_id = meta.get("pair_id", record.get("counterfactual_group"))
        if pair_id is None:
            continue
        question_id = str(record.get("question_id", record.get("question", "")))
        grouped[str(pair_id)][question_id].append(index)

    affected = unaffected = 0
    affected_correct = unaffected_correct = 0
    affected_changed = unaffected_preserved = 0
    complete_pairs = specific_pairs = eligible_pairs = 0
    affected_pair_groups = unaffected_pair_groups = 0
    for questions in grouped.values():
        pair_affected_ok: list[bool] = []
        pair_unaffected_ok: list[bool] = []
        contributed = False
        for indices in questions.values():
            if len(indices) < 2:
                continue
            # Stable ordering makes results independent of input record order.
            indices = sorted(
                indices,
                key=lambda i: str(_metadata(records[i]).get("variant", records[i].get("id", i))),
            )[:2]
            left, right = indices
            gold_left = str(records[left].get("answer", ""))
            gold_right = str(records[right].get("answer", ""))
            pred_left = str(predictions[left])
            pred_right = str(predictions[right])
            both_correct = pred_left == gold_left and pred_right == gold_right
            if gold_left != gold_right:
                affected += 1
                affected_correct += int(both_correct)
                changed = pred_left != pred_right
                affected_changed += int(changed)
                pair_affected_ok.append(bool(both_correct and changed))
            else:
                unaffected += 1
                unaffected_correct += int(both_correct)
                preserved = pred_left == pred_right
                unaffected_preserved += int(preserved)
                pair_unaffected_ok.append(bool(both_correct and preserved))
            contributed = True
        if contributed:
            eligible_pairs += 1
            if pair_affected_ok:
                affected_pair_groups += 1
                complete_pairs += int(all(pair_affected_ok))
            if pair_unaffected_ok:
                unaffected_pair_groups += 1
                specific_pairs += int(all(pair_unaffected_ok))

    return {
        "pair_groups": eligible_pairs,
        "affected_pair_groups": affected_pair_groups,
        "unaffected_pair_groups": unaffected_pair_groups,
        "affected_queries": affected,
        "unaffected_queries": unaffected,
        "affected_joint_accuracy": _safe_divide(affected_correct, affected),
        "unaffected_joint_accuracy": _safe_divide(unaffected_correct, unaffected),
        "change_sensitivity": _safe_divide(affected_changed, affected),
        "invariance_specificity": _safe_divide(unaffected_preserved, unaffected),
        "pair_level_completeness": _safe_divide(complete_pairs, affected_pair_groups),
        "pair_level_specificity": _safe_divide(specific_pairs, unaffected_pair_groups),
    }


def frobenius_relative(error: np.ndarray, *references: np.ndarray, epsilon: float = 1e-12) -> float:
    denominator = sum(float(np.linalg.norm(value, ord="fro")) for value in references)
    return float(np.linalg.norm(error, ord="fro") / max(denominator, epsilon))


def idempotence_residual(matrix: Any) -> float:
    value = np.asarray(matrix, dtype=float)
    return frobenius_relative(value @ value - value, value)


def inverse_residual(left: Any, right: Any) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    identity = np.eye(a.shape[0])
    forward = frobenius_relative(b @ a - identity, identity)
    backward = frobenius_relative(a @ b - identity, identity)
    return float((forward + backward) / 2)


def commutator_residual(left: Any, right: Any) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    ab, ba = a @ b, b @ a
    return frobenius_relative(ab - ba, ab, ba)


def composition_residual(composed: Any, left: Any, right: Any) -> float:
    """Residual for applying ``right`` and then ``left``: C = left @ right."""

    c = np.asarray(composed, dtype=float)
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    return frobenius_relative(c - a @ b, c, a @ b)


def _matrix(matrices: Mapping[str, Any] | Sequence[Any], key: Any) -> np.ndarray:
    if isinstance(matrices, Mapping):
        return np.asarray(matrices[str(key)], dtype=float)
    return np.asarray(matrices[int(key)], dtype=float)


def compute_algebra_residuals(
    matrices: Mapping[str, Any] | Sequence[Any], laws: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Evaluate typed law specifications against learned or exact matrices.

    Supported specifications are ``idempotent``, ``inverse``, ``commute``, and
    ``composition``.  Operator fields accept human-readable names or indices.
    """

    results: list[dict[str, Any]] = []
    for number, law in enumerate(laws):
        kind = str(law.get("kind", law.get("law", ""))).lower()
        if kind in {"idempotent", "idempotence"}:
            operator = law.get("op", law.get("operator"))
            value = idempotence_residual(_matrix(matrices, operator))
        elif kind in {"inverse", "inverses"}:
            left = law.get("left", law.get("op_a"))
            right = law.get("right", law.get("op_b"))
            value = inverse_residual(_matrix(matrices, left), _matrix(matrices, right))
        elif kind in {"commute", "commutation", "commutative"}:
            left = law.get("left", law.get("op_a"))
            right = law.get("right", law.get("op_b"))
            value = commutator_residual(_matrix(matrices, left), _matrix(matrices, right))
        elif kind in {"composition", "compose"}:
            composed = law.get("composed", law.get("result"))
            left = law.get("left", law.get("op_a"))
            right = law.get("right", law.get("op_b"))
            value = composition_residual(
                _matrix(matrices, composed), _matrix(matrices, left), _matrix(matrices, right)
            )
        else:
            raise ValueError(f"Unsupported algebra law kind: {kind!r}")
        results.append({"index": number, "kind": kind, "residual": float(value), "law": dict(law)})
    values = [item["residual"] for item in results]
    return {
        "count": len(values),
        "mean_residual": float(np.mean(values)) if values else 0.0,
        "max_residual": float(np.max(values)) if values else 0.0,
        "laws": results,
    }


def length_generalization_metrics(
    records: Sequence[Mapping[str, Any]], predictions: Sequence[Any]
) -> dict[str, Any]:
    if len(records) != len(predictions):
        raise ValueError("records and predictions must have equal lengths")
    groups: dict[int, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        length = _metadata(record).get("length", len(record.get("program", []) or []))
        groups[int(length)].append(index)
    return {
        str(length): _subset_metrics(records, predictions, indices)
        for length, indices in sorted(groups.items())
    }


def bootstrap_accuracy_interval(
    gold: Sequence[Any],
    predicted: Sequence[Any],
    *,
    samples: int = 2000,
    seed: int = 17,
    confidence: float = 0.95,
) -> dict[str, float]:
    """Deterministic nonparametric interval for reporting across examples."""

    if len(gold) != len(predicted):
        raise ValueError("gold and predicted must have equal lengths")
    if not gold:
        return {"estimate": 0.0, "lower": 0.0, "upper": 0.0}
    correct = np.asarray([str(a) == str(b) for a, b in zip(gold, predicted)], dtype=float)
    estimate = float(correct.mean())
    if int(samples) < 1:
        return {"estimate": estimate, "lower": estimate, "upper": estimate}
    rng = np.random.default_rng(seed)
    # Resampling a binary correctness vector is exactly Binomial(n, p_hat).
    # This avoids allocating a samples-by-examples index matrix for full runs.
    distribution = rng.binomial(len(correct), estimate, size=int(samples)) / len(correct)
    alpha = (1 - confidence) / 2
    return {
        "estimate": estimate,
        "lower": float(np.quantile(distribution, alpha)),
        "upper": float(np.quantile(distribution, 1 - alpha)),
    }

from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import statistics
from typing import Any, Iterable


SPLITS = ("test_iid", "test_ood_depth")
MODES = ("recurrent", "zero", "shuffle", "no_feedback")
QUERY_TYPES = ("direct", "parity", "codebook")


def read_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return value


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"invalid JSONL object at line {line_number}: {path}")
        records.append(value)
    return records


def _entropy(counts: Iterable[int]) -> float:
    values = [int(value) for value in counts if int(value) > 0]
    total = sum(values)
    if total <= 0:
        return 0.0
    return -sum((value / total) * math.log(value / total) for value in values)


def _mean(values: Iterable[float]) -> float:
    materialized = [float(value) for value in values]
    if not materialized:
        raise ValueError("cannot average an empty sequence")
    return statistics.fmean(materialized)


def _prediction_distribution(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(record["predicted_text"]) for record in records)
    entropy = _entropy(counts.values())
    return {
        "count": len(records),
        "unique_predictions": len(counts),
        "counts": dict(sorted(counts.items())),
        "modal_prediction": counts.most_common(1)[0][0],
        "modal_fraction": counts.most_common(1)[0][1] / len(records),
        "entropy_nats": entropy,
        "effective_prediction_count": math.exp(entropy),
    }


def _trace_summary(evaluation: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for evaluation_key in ("iid", "ood"):
        trace = evaluation[evaluation_key]["trace"]
        result[evaluation_key] = {}
        for mode in ("recurrent", "no_feedback"):
            records = trace[mode]["records"]
            if not records:
                raise RuntimeError(f"empty trace for {evaluation_key}/{mode}")
            keys = (
                "state_mean_norm_by_step",
                "injection_mean_norm_by_step",
                "feedback_mean_norm_by_step",
                "halt_probability_mean_by_step",
            )
            mode_summary: dict[str, Any] = {"batches": len(records)}
            for key in keys:
                width = len(records[0][key])
                if any(len(record[key]) != width for record in records):
                    raise RuntimeError(
                        f"inconsistent trace width for {evaluation_key}/{mode}/{key}"
                    )
                mode_summary[key] = [
                    {
                        "mean": _mean(record[key][step] for record in records),
                        "population_sd": statistics.pstdev(
                            float(record[key][step]) for record in records
                        ),
                        "minimum": min(float(record[key][step]) for record in records),
                        "maximum": max(float(record[key][step]) for record in records),
                    }
                    for step in range(width)
                ]
            result[evaluation_key][mode] = mode_summary
        paired: dict[str, list[float]] = {}
        recurrent_records = trace["recurrent"]["records"]
        no_feedback_records = trace["no_feedback"]["records"]
        if len(recurrent_records) != len(no_feedback_records):
            raise RuntimeError(f"trace batch mismatch for {evaluation_key}")
        for key in (
            "state_mean_norm_by_step",
            "injection_mean_norm_by_step",
            "feedback_mean_norm_by_step",
            "halt_probability_mean_by_step",
        ):
            width = len(recurrent_records[0][key])
            paired[key] = [
                _mean(
                    left[key][step] - right[key][step]
                    for left, right in zip(recurrent_records, no_feedback_records)
                )
                for step in range(width)
            ]
        result[evaluation_key]["mean_recurrent_minus_no_feedback"] = paired
    return result


def analyze_run_artifacts(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir).resolve()
    config = read_json(root / "resolved_config.json")
    gates = read_json(root / "gates.json")
    evaluation = read_json(root / "evaluation.json")
    predictions = read_jsonl(root / "predictions.jsonl")
    training = read_jsonl(root / "training.jsonl")
    if not training:
        raise RuntimeError("training telemetry is empty")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    indexed: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in predictions:
        split = str(record.get("split"))
        mode = str(record.get("mode"))
        example_id = str(record.get("example_id"))
        if split not in SPLITS or mode not in MODES:
            raise RuntimeError(f"unexpected prediction group: {split}/{mode}")
        key = (split, example_id, mode)
        if key in indexed:
            raise RuntimeError(f"duplicate prediction record: {key}")
        indexed[key] = record
        grouped[(split, mode)].append(record)

    counts_by_split = {
        split: int(config["task"]["test_base_problems"])
        * len(QUERY_TYPES)
        if split == "test_iid"
        else int(config["task"]["ood_base_problems"]) * len(QUERY_TYPES)
        for split in SPLITS
    }
    for split in SPLITS:
        expected_ids: set[str] | None = None
        for mode in MODES:
            records = grouped[(split, mode)]
            if len(records) != counts_by_split[split]:
                raise RuntimeError(f"prediction count mismatch for {split}/{mode}")
            identifiers = {str(record["example_id"]) for record in records}
            if expected_ids is None:
                expected_ids = identifiers
            elif identifiers != expected_ids:
                raise RuntimeError(f"prediction identifier mismatch for {split}/{mode}")

    distribution: dict[str, Any] = {}
    agreement: dict[str, Any] = {}
    accuracy: dict[str, Any] = {}
    for split in SPLITS:
        distribution[split] = {}
        accuracy[split] = {}
        ids = sorted(str(record["example_id"]) for record in grouped[(split, "recurrent")])
        for mode in MODES:
            records = grouped[(split, mode)]
            accuracy[split][mode] = {
                "overall": sum(bool(record["correct"]) for record in records)
                / len(records),
                "correct_count": sum(bool(record["correct"]) for record in records),
                "by_query": {
                    query: sum(
                        bool(record["correct"])
                        for record in records
                        if record["query_type"] == query
                    )
                    / sum(record["query_type"] == query for record in records)
                    for query in QUERY_TYPES
                },
            }
            distribution[split][mode] = {
                query: _prediction_distribution(
                    [record for record in records if record["query_type"] == query]
                )
                for query in QUERY_TYPES
            }

        agreement[split] = {}
        pairs = (
            ("recurrent", "zero"),
            ("recurrent", "shuffle"),
            ("recurrent", "no_feedback"),
            ("shuffle", "no_feedback"),
        )
        for left, right in pairs:
            pair_name = f"{left}__{right}"
            same = [
                indexed[(split, identifier, left)]["predicted_token_id"]
                == indexed[(split, identifier, right)]["predicted_token_id"]
                for identifier in ids
            ]
            by_query: dict[str, Any] = {}
            for query in QUERY_TYPES:
                query_ids = [
                    identifier
                    for identifier in ids
                    if indexed[(split, identifier, left)]["query_type"] == query
                ]
                query_same = sum(
                    indexed[(split, identifier, left)]["predicted_token_id"]
                    == indexed[(split, identifier, right)]["predicted_token_id"]
                    for identifier in query_ids
                )
                by_query[query] = {
                    "same_count": query_same,
                    "changed_count": len(query_ids) - query_same,
                    "agreement": query_same / len(query_ids),
                }
            agreement[split][pair_name] = {
                "same_count": sum(same),
                "changed_count": len(same) - sum(same),
                "agreement": sum(same) / len(same),
                "by_query": by_query,
            }

    states = int(config["task"]["states"])
    theoretical_family_chance = {
        "direct": 1.0 / states,
        "parity": 0.5,
        "codebook": 1.0 / states,
    }
    theoretical_overall_chance = _mean(theoretical_family_chance.values())
    iid_majorities = evaluation["iid"]["recurrent"]["majority_baseline_by_query"]
    iid_empirical_majority = _mean(iid_majorities.values())

    target_entropy_by_query: dict[str, float] = {}
    iid_recurrent = grouped[("test_iid", "recurrent")]
    for query in QUERY_TYPES:
        target_counts = Counter(
            int(record["target_token_id"])
            for record in iid_recurrent
            if record["query_type"] == query
        )
        target_entropy_by_query[query] = _entropy(target_counts.values())
    marginal_entropy_baseline = _mean(target_entropy_by_query.values())

    phase_count = 5
    training_phases: list[dict[str, Any]] = []
    maximum_step = int(training[-1]["step"])
    for phase in range(phase_count):
        lower = math.floor(phase * maximum_step / phase_count) + 1
        upper = math.floor((phase + 1) * maximum_step / phase_count)
        records = [record for record in training if lower <= int(record["step"]) <= upper]
        if not records:
            continue
        training_phases.append(
            {
                "step_min": lower,
                "step_max": upper,
                "logged_records": len(records),
                "loss_mean": _mean(record["loss"] for record in records),
                "loss_median": statistics.median(float(record["loss"]) for record in records),
                "gradient_norm_mean": _mean(
                    record["gradient_norm"] for record in records
                ),
            }
        )

    iid_recurrent_accuracy = accuracy["test_iid"]["recurrent"]["overall"]
    deltas = {
        "recurrent_minus_zero": iid_recurrent_accuracy
        - accuracy["test_iid"]["zero"]["overall"],
        "recurrent_minus_shuffle": iid_recurrent_accuracy
        - accuracy["test_iid"]["shuffle"]["overall"],
        "recurrent_minus_no_feedback": iid_recurrent_accuracy
        - accuracy["test_iid"]["no_feedback"]["overall"],
    }
    thresholds = config["gates"]
    signatures = {
        "zero_injection_changes_behavior": deltas["recurrent_minus_zero"]
        >= float(thresholds["zero_gap_min"]),
        "answer_incompatible_shuffle_preserves_accuracy": abs(
            deltas["recurrent_minus_shuffle"]
        )
        <= 1.0 / counts_by_split["test_iid"],
        "no_feedback_preserves_accuracy": abs(
            deltas["recurrent_minus_no_feedback"]
        )
        <= 2.0 / counts_by_split["test_iid"],
        "recurrent_shuffle_prediction_agreement_at_least_95pct": agreement[
            "test_iid"
        ]["recurrent__shuffle"]["agreement"]
        >= 0.95,
        "recurrent_no_feedback_prediction_agreement_at_least_95pct": agreement[
            "test_iid"
        ]["recurrent__no_feedback"]["agreement"]
        >= 0.95,
        "iid_near_theoretical_family_chance": abs(
            iid_recurrent_accuracy - theoretical_overall_chance
        )
        <= 0.02,
    }
    generic_steering_signature = all(signatures.values())

    scientific_failures = [
        gate
        for gate in gates["scientific"]["gates"]
        if gate.get("passed") is False
    ]
    return {
        "schema": "komorebi.neuralese.g1d.static_analysis.v1",
        "source_run": {
            "path": str(root),
            "profile": config["profile"],
            "seed": config["seed"],
            "config_digest": config["config_digest"],
            "claim": gates["claim"],
            "scientific_pass": bool(gates["scientific"]["passed"]),
            "scientific_failure_names": [gate["name"] for gate in scientific_failures],
        },
        "counts": {
            "prediction_records": len(predictions),
            "training_records": len(training),
            "by_split_per_mode": counts_by_split,
        },
        "baselines": {
            "theoretical_family_chance": theoretical_family_chance,
            "theoretical_overall_chance": theoretical_overall_chance,
            "iid_empirical_majority_by_query": iid_majorities,
            "iid_empirical_majority_overall": iid_empirical_majority,
            "iid_target_entropy_nats_by_query": target_entropy_by_query,
            "iid_marginal_entropy_baseline_nats": marginal_entropy_baseline,
        },
        "accuracy": accuracy,
        "iid_causal_deltas": deltas,
        "prediction_distributions": distribution,
        "cross_mode_prediction_agreement": agreement,
        "training_phases": training_phases,
        "trace_aggregate": _trace_summary(evaluation),
        "signatures": signatures,
        "generic_steering_signature": generic_steering_signature,
        "interpretation": (
            "The learned injection changes output formatting or routing, but the saved "
            "behavior is consistent with a largely input-independent steering solution."
            if generic_steering_signature
            else "The predefined generic-steering signature was not fully present."
        ),
    }

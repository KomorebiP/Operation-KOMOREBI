"""Deterministic aggregation for crossed data-seed/model-seed replications.

The neural runner writes one completed run directory per crossed seed cell.
This module deliberately reads only runs whose ``run_metadata.json`` marks
``completed`` as true.  Partial, failed, and interrupted directories are
reported but never mixed into numerical summaries.

The built-in per-split gate is narrowly defined: does a neural accuracy beat
the strongest classical baseline from the same run?  Separately emitted
``EVIDENCE_ADJUDICATION.json`` statuses are preserved verbatim and summarized
as behavioral gate rates.  Neither kind of gate is converted into an evidence
level or an emergence claim here.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Iterable, Mapping, Sequence

from .utils import load_json, save_json, sha256_file


SCHEMA = "osl.micro-emergence.replication-aggregate.v1"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
GATE_STATUSES = ("PASS", "FAIL", "INCOMPLETE")
RENAMING_DIAGNOSTICS = (
    "declared_groups",
    "canonical_accuracy",
    "renamed_accuracy",
    "prediction_consistency",
    "pair_joint_correctness",
    "robustness_gap",
    "pair_groups",
    "triplet_groups",
    "correct_calibration_accuracy",
    "scrambled_accuracy",
    "correct_minus_scrambled_accuracy",
    "correct_vs_scrambled_prediction_change",
    "correct_only_success_rate",
)
COUNTERFACTUAL_DIAGNOSTICS = (
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
)
DIAGNOSTIC_FIELDS = {
    "renaming": RENAMING_DIAGNOSTICS,
    "counterfactual": COUNTERFACTUAL_DIAGNOSTICS,
}
ROLE_CONTRAST_ARMS = (
    "answer_only",
    "role_bind_scrambled",
    "role_bind_augmented",
)
ROLE_CORRECT_ARM = "role_bind_augmented"
ROLE_SCRAMBLED_ARM = "role_bind_scrambled"
ROLE_CONTEXT_ARM = "answer_only"
ROLE_PRIMARY_DELTA = "role_bind_augmented_minus_role_bind_scrambled"
ROLE_CONTEXT_DELTA = "role_bind_augmented_minus_answer_only"
ROLE_CONTROL_CONTEXT_DELTA = "role_bind_scrambled_minus_answer_only"
ROLE_CONTRAST_SPLITS = ("lexical", "heldout_pair", "heldout_triple", "renaming")
ROLE_REQUIRED_RENAMING_DIAGNOSTICS = (
    "renamed_accuracy",
    "prediction_consistency",
    "pair_joint_correctness",
    "correct_minus_scrambled_accuracy",
)
ROLE_PRIMARY_METRICS = (
    "renamed_accuracy_gain_over_scrambled_arm",
    "pair_joint_gain_over_scrambled_arm",
    "correct_calibration_gain_at_test",
    "correct_arm_renamed_accuracy",
    "correct_arm_prediction_consistency",
    "correct_arm_pair_joint_correctness",
    "lexical_accuracy_delta_vs_scrambled",
    "heldout_pair_accuracy_delta_vs_scrambled",
    "heldout_triple_accuracy_delta_vs_scrambled",
    "renaming_accuracy_delta_vs_scrambled",
)
ROLE_POSITIVE_METRICS = (
    "renamed_accuracy_gain_over_scrambled_arm",
    "pair_joint_gain_over_scrambled_arm",
    "correct_calibration_gain_at_test",
)
NON_EVALUATION_SPLITS = {
    "train",
    "renaming_train",
    "renaming_scrambled_train",
    "iid",
    "iid_validation",
    "validation",
    "val",
}


class AggregationError(RuntimeError):
    """Raised when strict aggregation encounters an invalid replication."""


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _integer_seed(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")
    try:
        converted = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{field} must be an integer")
    return converted


def _stats(values: Iterable[float]) -> dict[str, float | int]:
    ordered = [float(value) for value in values]
    if not ordered:
        return {"count": 0, "mean": 0.0, "sd": 0.0, "min": 0.0, "max": 0.0}
    return {
        "count": len(ordered),
        "mean": statistics.fmean(ordered),
        "sd": statistics.stdev(ordered) if len(ordered) > 1 else 0.0,
        "min": min(ordered),
        "max": max(ordered),
    }


def _experiment_identity(experiment_dir: Path) -> tuple[str, str]:
    summary_path = experiment_dir / "training_summary.json"
    arm = ""
    architecture = ""
    if summary_path.is_file():
        summary = load_json(summary_path)
        arm = str(summary.get("arm", ""))
        architecture = str(summary.get("architecture", ""))
    if "__" in experiment_dir.name:
        directory_architecture, directory_arm = experiment_dir.name.split("__", 1)
        architecture = architecture or directory_architecture
        arm = arm or directory_arm
    return architecture or "unspecified", arm or experiment_dir.name


def _strongest_baselines(run_dir: Path) -> dict[str, dict[str, Any]]:
    source = run_dir / "baseline_results.json"
    if not source.is_file():
        return {}
    payload = load_json(source)
    candidates: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for model_name, model in sorted(dict(payload.get("models", {})).items()):
        try:
            splits = model["by_split"]["splits"]
        except (KeyError, TypeError):
            continue
        if not isinstance(splits, Mapping):
            continue
        for split, metrics in sorted(splits.items()):
            if not isinstance(metrics, Mapping):
                continue
            accuracy = _finite_number(metrics.get("accuracy"))
            if accuracy is not None:
                candidates[str(split)].append((str(model_name), accuracy))
    strongest: dict[str, dict[str, Any]] = {}
    for split, rows in sorted(candidates.items()):
        maximum = max(value for _, value in rows)
        strongest[split] = {
            "accuracy": maximum,
            "models": sorted(name for name, value in rows if value == maximum),
        }
    return strongest


def _seed_consistency_issues(run_dir: Path, data_seed: int, model_seed: int) -> list[str]:
    """Cross-check seed labels against portable artifacts when those fields exist."""

    issues: list[str] = []
    checks = (
        (run_dir / "resolved_config.json", ("data_seed",), data_seed, "resolved_config.data_seed"),
        (run_dir / "resolved_config.json", ("model_seed",), model_seed, "resolved_config.model_seed"),
        (run_dir / "manifest.json", ("config", "seed"), data_seed, "manifest.config.seed"),
        (run_dir / "experiment_matrix.json", ("data_seed",), data_seed, "experiment_matrix.data_seed"),
        (run_dir / "experiment_matrix.json", ("model_seed",), model_seed, "experiment_matrix.model_seed"),
    )
    loaded: dict[Path, Mapping[str, Any]] = {}
    for path, keys, expected, label in checks:
        if not path.is_file():
            continue
        if path not in loaded:
            loaded[path] = load_json(path)
        current: Any = loaded[path]
        for key in keys:
            if not isinstance(current, Mapping) or key not in current:
                current = None
                break
            current = current[key]
        if current is None:
            continue
        try:
            observed = _integer_seed(current, label)
        except ValueError:
            issues.append(f"{label} is not an integer")
            continue
        if observed != expected:
            issues.append(f"{label}={observed} does not match run metadata {expected}")
    for summary_path in sorted((run_dir / "experiments").glob("*/training_summary.json")):
        summary = load_json(summary_path)
        if summary.get("model_seed") is None:
            continue
        observed = _integer_seed(summary["model_seed"], "training_summary.model_seed")
        if observed != model_seed:
            issues.append(
                f"{summary_path.parent.name}.model_seed={observed} does not match run metadata {model_seed}"
            )
    return issues


def _normalize_gate_status(value: Any) -> str | None:
    normalized = str(value).upper() if value is not None else ""
    return normalized if normalized in GATE_STATUSES else None


def _gate_items(container: Any, prefix: str = "") -> list[dict[str, Any]]:
    """Extract named statuses from a gates mapping or gates list."""

    rows: list[dict[str, Any]] = []
    if isinstance(container, Mapping):
        for key, value in sorted(container.items(), key=lambda item: str(item[0])):
            name = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, str):
                status = _normalize_gate_status(value)
                if status:
                    rows.append({"gate": name, "status": status})
                continue
            if not isinstance(value, Mapping):
                continue
            status = _normalize_gate_status(value.get("status"))
            if status:
                detail = {
                    str(child_key): child_value
                    for child_key, child_value in value.items()
                    if str(child_key) not in {"name", "gate", "id", "status"}
                }
                rows.append({"gate": name, "status": status, "detail": detail})
            else:
                rows.extend(_gate_items(value, name))
    elif isinstance(container, Sequence) and not isinstance(container, (str, bytes)):
        for index, value in enumerate(container):
            if not isinstance(value, Mapping):
                continue
            name = value.get("name", value.get("gate", value.get("id", f"gate_{index}")))
            status = _normalize_gate_status(value.get("status"))
            if status:
                detail = {
                    str(key): child
                    for key, child in value.items()
                    if str(key) not in {"name", "gate", "id", "status"}
                }
                rows.append({"gate": str(name), "status": status, "detail": detail})
    return rows


def _adjudication_gates(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Read supported explicit-gate containers without treating overall status as a gate."""

    rows: list[dict[str, Any]] = []
    for key in ("gates", "behavioral_gates", "gate_results"):
        if key in payload:
            rows.extend(_gate_items(payload[key]))
    for key in ("behavioral", "adjudication"):
        child = payload.get(key)
        if isinstance(child, Mapping):
            rows.extend(_adjudication_gates(child))
    return rows


def _load_config(path: str | Path | None) -> dict[str, Any]:
    return load_json(path) if path else {}


def _sha256_value(value: Any, field: str) -> str:
    """Return a normalized SHA-256 value or reject malformed provenance."""

    if not isinstance(value, str):
        raise ValueError(f"{field} must be a 64-character hexadecimal SHA-256")
    normalized = value.lower()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{field} must be a 64-character hexadecimal SHA-256")
    return normalized


def _dataset_manifest_descriptor(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Read the portable, model-seed-invariant portion of a dataset manifest."""

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("completed run has no dataset manifest.json")
    try:
        manifest = load_json(manifest_path)
    except Exception as exc:
        raise ValueError(
            "dataset manifest.json could not be read as a JSON object "
            f"({type(exc).__name__})"
        ) from exc
    files = manifest.get("files")
    if not isinstance(files, Mapping) or not files:
        raise ValueError("dataset manifest.json has no non-empty files mapping")

    descriptor: dict[str, dict[str, Any]] = {}
    for split, raw_file in sorted(files.items(), key=lambda item: str(item[0])):
        split_name = str(split)
        if not isinstance(raw_file, Mapping):
            raise ValueError(
                f"dataset manifest file descriptor for {split_name!r} is not an object"
            )
        records = raw_file.get("records")
        if isinstance(records, bool) or not isinstance(records, int) or records < 0:
            raise ValueError(
                f"dataset manifest files.{split_name}.records must be a non-negative integer"
            )
        descriptor[split_name] = {
            "records": records,
            "sha256": _sha256_value(
                raw_file.get("sha256"), f"dataset manifest files.{split_name}.sha256"
            ),
            "semantic_sha256": _sha256_value(
                raw_file.get("semantic_sha256"),
                f"dataset manifest files.{split_name}.semantic_sha256",
            ),
        }
    return descriptor


def _expected_values(
    config: Mapping[str, Any],
    expected_data_seeds: Sequence[int] | None,
    expected_model_seeds: Sequence[int] | None,
) -> dict[str, list[Any]]:
    replication = dict(config.get("replication", {}))
    training = dict(config.get("training", {}))
    dataset = dict(config.get("dataset", {}))
    data_values = (
        list(expected_data_seeds)
        if expected_data_seeds is not None
        else list(replication.get("data_seeds", []))
    )
    model_values = (
        list(expected_model_seeds)
        if expected_model_seeds is not None
        else list(replication.get("model_seeds", []))
    )
    arms = list(replication.get("arms", training.get("arms", [])))
    architectures = list(
        replication.get("architectures", training.get("architectures", ["transformer"]))
    )
    configured_splits = replication.get("splits")
    if configured_splits is None:
        configured_splits = [
            split
            for split in dict(dataset.get("split_sizes", {}))
            if str(split) not in NON_EVALUATION_SPLITS
        ]
    return {
        "data_seeds": sorted({_integer_seed(value, "data_seed") for value in data_values}),
        "model_seeds": sorted({_integer_seed(value, "model_seed") for value in model_values}),
        "arms": sorted({str(value) for value in arms}),
        "architectures": sorted({str(value) for value in architectures}),
        "splits": sorted({str(value) for value in configured_splits}),
    }


def _summarize_rows(rows: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    summaries: list[dict[str, Any]] = []
    metric_names = (
        "n",
        "exact_correct",
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "micro_f1",
        "strongest_baseline_accuracy",
        "baseline_margin",
    )
    for group, members in sorted(grouped.items(), key=lambda item: tuple(str(v) for v in item[0])):
        summary = {key: value for key, value in zip(keys, group)}
        summary["replicates"] = len(members)
        summary["data_seeds"] = sorted({int(row["data_seed"]) for row in members})
        summary["model_seeds"] = sorted({int(row["model_seed"]) for row in members})
        summary["metrics"] = {}
        for metric in metric_names:
            values = [
                value
                for row in members
                if (value := _finite_number(row.get(metric))) is not None
            ]
            if values:
                summary["metrics"][metric] = _stats(values)
        statuses = [str(row.get("baseline_gate_status", "INCOMPLETE")) for row in members]
        counts = {status: statuses.count(status) for status in GATE_STATUSES}
        decided = counts["PASS"] + counts["FAIL"]
        summary["strongest_baseline_gate"] = {
            "definition": "neural split accuracy strictly exceeds the strongest same-run classical baseline",
            "counts": counts,
            "pass_rate_all": counts["PASS"] / len(statuses) if statuses else 0.0,
            "pass_rate_decided": counts["PASS"] / decided if decided else 0.0,
        }
        summaries.append(summary)
    return summaries


def _summarize_explicit_gates(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (str(row["architecture"]), str(row["arm"]), str(row["gate"]))
        grouped[key].append(row)
    summaries: list[dict[str, Any]] = []
    for (architecture, arm, gate), members in sorted(grouped.items()):
        statuses = [str(row["status"]) for row in members]
        counts = {status: statuses.count(status) for status in GATE_STATUSES}
        decided = counts["PASS"] + counts["FAIL"]
        summaries.append(
            {
                "architecture": architecture,
                "arm": arm,
                "gate": gate,
                "replicates": len(members),
                "data_seeds": sorted({int(row["data_seed"]) for row in members}),
                "model_seeds": sorted({int(row["model_seed"]) for row in members}),
                "counts": counts,
                "pass_rate_all": counts["PASS"] / len(members) if members else 0.0,
                "pass_rate_decided": counts["PASS"] / decided if decided else 0.0,
            }
        )
    return summaries


def _extract_diagnostics(evaluation: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    """Extract only preregistered paired and counterfactual diagnostics."""

    behavior = evaluation.get("behavior", {})
    behavior = behavior if isinstance(behavior, Mapping) else {}
    renaming = evaluation.get("renaming", behavior.get("renaming", {}))
    counterfactual = evaluation.get("counterfactual", {})
    sources = {
        "renaming": renaming if isinstance(renaming, Mapping) else {},
        "counterfactual": counterfactual if isinstance(counterfactual, Mapping) else {},
    }
    extracted: dict[str, dict[str, float]] = {}
    for family, fields in DIAGNOSTIC_FIELDS.items():
        extracted[family] = {}
        for field in fields:
            value = _finite_number(sources[family].get(field))
            if value is not None:
                extracted[family][field] = value
    return extracted


def _summarize_diagnostics(
    rows: Sequence[Mapping[str, Any]], keys: Sequence[str]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    summaries: list[dict[str, Any]] = []
    for group, members in sorted(grouped.items(), key=lambda item: tuple(str(v) for v in item[0])):
        summary = {key: value for key, value in zip(keys, group)}
        summary["replicates"] = len(members)
        summary["data_seeds"] = sorted({int(row["data_seed"]) for row in members})
        summary["model_seeds"] = sorted({int(row["model_seed"]) for row in members})
        summary["diagnostics"] = {}
        for family, fields in DIAGNOSTIC_FIELDS.items():
            family_summary: dict[str, Any] = {}
            for field in fields:
                values = [
                    value
                    for row in members
                    if (
                        value := _finite_number(
                            dict(row.get(family, {})).get(field)
                            if isinstance(row.get(family), Mapping)
                            else None
                        )
                    )
                    is not None
                ]
                if values:
                    family_summary[field] = _stats(values)
            summary["diagnostics"][family] = family_summary
        summaries.append(summary)
    return summaries


def _contrast_endpoints(values: Mapping[str, float]) -> dict[str, float]:
    """Return primary and contextual deltas for one matched metric."""

    result = {arm: float(value) for arm, value in values.items()}
    correct = values.get(ROLE_CORRECT_ARM)
    scrambled = values.get(ROLE_SCRAMBLED_ARM)
    answer = values.get(ROLE_CONTEXT_ARM)
    if correct is not None and scrambled is not None:
        result[ROLE_PRIMARY_DELTA] = float(correct - scrambled)
    if correct is not None and answer is not None:
        result[ROLE_CONTEXT_DELTA] = float(correct - answer)
    if scrambled is not None and answer is not None:
        result[ROLE_CONTROL_CONTEXT_DELTA] = float(scrambled - answer)
    return result


def _contrast_primary(contrast: Mapping[str, Any]) -> dict[str, float]:
    """Project one complete three-arm cell onto the frozen H2 endpoints."""

    diagnostics = contrast.get("diagnostics", {})
    renaming = (
        diagnostics.get("renaming", {}) if isinstance(diagnostics, Mapping) else {}
    )
    splits = contrast.get("splits", {})
    splits = splits if isinstance(splits, Mapping) else {}

    def endpoint(field: str, key: str) -> float | None:
        values = renaming.get(field, {}) if isinstance(renaming, Mapping) else {}
        return _finite_number(values.get(key) if isinstance(values, Mapping) else None)

    def split_endpoint(split: str, key: str) -> float | None:
        values = splits.get(split, {})
        return _finite_number(values.get(key) if isinstance(values, Mapping) else None)

    candidates = {
        "renamed_accuracy_gain_over_scrambled_arm": endpoint(
            "renamed_accuracy", ROLE_PRIMARY_DELTA
        ),
        "pair_joint_gain_over_scrambled_arm": endpoint(
            "pair_joint_correctness", ROLE_PRIMARY_DELTA
        ),
        "correct_calibration_gain_at_test": endpoint(
            "correct_minus_scrambled_accuracy", ROLE_CORRECT_ARM
        ),
        "correct_arm_renamed_accuracy": endpoint("renamed_accuracy", ROLE_CORRECT_ARM),
        "correct_arm_prediction_consistency": endpoint(
            "prediction_consistency", ROLE_CORRECT_ARM
        ),
        "correct_arm_pair_joint_correctness": endpoint(
            "pair_joint_correctness", ROLE_CORRECT_ARM
        ),
        "lexical_accuracy_delta_vs_scrambled": split_endpoint(
            "lexical", ROLE_PRIMARY_DELTA
        ),
        "heldout_pair_accuracy_delta_vs_scrambled": split_endpoint(
            "heldout_pair", ROLE_PRIMARY_DELTA
        ),
        "heldout_triple_accuracy_delta_vs_scrambled": split_endpoint(
            "heldout_triple", ROLE_PRIMARY_DELTA
        ),
        "renaming_accuracy_delta_vs_scrambled": split_endpoint(
            "renaming", ROLE_PRIMARY_DELTA
        ),
    }
    return {
        key: value
        for key, value in candidates.items()
        if value is not None
    }


def _endpoint_summary(
    members: Sequence[Mapping[str, Any]],
    container: str,
    family: str,
    field: str | None,
) -> dict[str, Any]:
    endpoints = []
    for row in members:
        parent = row.get(container, {})
        if not isinstance(parent, Mapping):
            continue
        child = parent.get(family, {})
        if not isinstance(child, Mapping):
            continue
        endpoint = child if field is None else child.get(field)
        if isinstance(endpoint, Mapping):
            endpoints.append(endpoint)
    result: dict[str, Any] = {}
    for key in (*ROLE_CONTRAST_ARMS, ROLE_PRIMARY_DELTA, ROLE_CONTEXT_DELTA, ROLE_CONTROL_CONTEXT_DELTA):
        values = [
            value
            for endpoint in endpoints
            if (value := _finite_number(endpoint.get(key))) is not None
        ]
        if values:
            result[key] = _stats(values)
    return result


def _primary_stats(members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for metric in ROLE_PRIMARY_METRICS:
        values = [
            value
            for row in members
            if (
                value := _finite_number(
                    row.get("primary", {}).get(metric)
                    if isinstance(row.get("primary"), Mapping)
                    else None
                )
            )
            is not None
        ]
        if values:
            result[metric] = _stats(values)
    return result


def _contrast_strata(
    members: Sequence[Mapping[str, Any]], key: str
) -> list[dict[str, Any]]:
    grouped: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in members:
        grouped[int(row[key])].append(row)
    return [
        {
            key: value,
            "crossed_cell_count": len(group),
            "data_seeds": sorted({int(row["data_seed"]) for row in group}),
            "model_seeds": sorted({int(row["model_seed"]) for row in group}),
            "primary_metrics": _primary_stats(group),
        }
        for value, group in sorted(grouped.items())
    ]


def _role_binding_contrasts(
    rows: Sequence[Mapping[str, Any]], *, enabled: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build correct-minus-scrambled contrasts within identical seed cells.

    ``role_bind_augmented`` versus ``role_bind_scrambled`` is the primary
    matched calibration-information contrast.  ``answer_only`` deltas are
    retained only as context.  The result can support bounded learned binding
    under this generator and protocol; it is not an emergence adjudication.
    """

    if not enabled:
        return [], [], []
    grouped: dict[tuple[int, int, str], dict[str, list[Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        arm = str(row.get("arm", ""))
        if arm not in ROLE_CONTRAST_ARMS:
            continue
        key = (int(row["data_seed"]), int(row["model_seed"]), str(row["architecture"]))
        grouped[key][arm].append(row)

    contrasts: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for (data_seed, model_seed, architecture), arms in sorted(grouped.items()):
        counts = {arm: len(arms.get(arm, [])) for arm in ROLE_CONTRAST_ARMS}
        if any(counts[arm] != 1 for arm in ROLE_CONTRAST_ARMS):
            issues.append(
                {
                    "data_seed": data_seed,
                    "model_seed": model_seed,
                    "architecture": architecture,
                    "arm_row_counts": counts,
                    "reason": "contrast requires exactly one evaluation for all three central arms",
                }
            )
            continue

        selected = {arm: arms[arm][0] for arm in ROLE_CONTRAST_ARMS}
        contrast: dict[str, Any] = {
            "data_seed": data_seed,
            "model_seed": model_seed,
            "architecture": architecture,
            "runs": {arm: str(selected[arm]["run"]) for arm in ROLE_CONTRAST_ARMS},
            "complete": False,
            "splits": {},
            "diagnostics": {},
            "primary": {},
            "missing_metrics": [],
        }

        for split in ROLE_CONTRAST_SPLITS:
            values: dict[str, float] = {}
            for arm, row in selected.items():
                split_values = row.get("splits", {})
                value = _finite_number(
                    split_values.get(split)
                    if isinstance(split_values, Mapping)
                    else None
                )
                if value is None:
                    contrast["missing_metrics"].append(f"{arm}.split.{split}.accuracy")
                else:
                    values[arm] = value
            if values:
                contrast["splits"][split] = _contrast_endpoints(values)

        for family, fields in DIAGNOSTIC_FIELDS.items():
            family_values: dict[str, Any] = {}
            for field in fields:
                values = {}
                for arm, row in selected.items():
                    source = row.get(family, {})
                    value = _finite_number(
                        source.get(field) if isinstance(source, Mapping) else None
                    )
                    if value is not None:
                        values[arm] = value
                if values:
                    family_values[field] = _contrast_endpoints(values)
            contrast["diagnostics"][family] = family_values

        renaming_values = contrast["diagnostics"].get("renaming", {})
        for field in ROLE_REQUIRED_RENAMING_DIAGNOSTICS:
            endpoint = renaming_values.get(field, {})
            for arm in ROLE_CONTRAST_ARMS:
                if not isinstance(endpoint, Mapping) or arm not in endpoint:
                    contrast["missing_metrics"].append(f"{arm}.renaming.{field}")

        contrast["missing_metrics"] = sorted(set(contrast["missing_metrics"]))
        contrast["primary"] = _contrast_primary(contrast)
        missing_primary = sorted(set(ROLE_PRIMARY_METRICS) - set(contrast["primary"]))
        contrast["missing_metrics"].extend(
            f"primary.{field}" for field in missing_primary
        )
        contrast["missing_metrics"] = sorted(set(contrast["missing_metrics"]))
        contrast["complete"] = not contrast["missing_metrics"]
        if contrast["missing_metrics"]:
            issues.append(
                {
                    "data_seed": data_seed,
                    "model_seed": model_seed,
                    "architecture": architecture,
                    "missing_metrics": list(contrast["missing_metrics"]),
                    "reason": "three-arm learned-binding contrast lacks required endpoints",
                }
            )
        contrasts.append(contrast)

    summaries: list[dict[str, Any]] = []
    by_architecture: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for contrast in contrasts:
        by_architecture[str(contrast["architecture"])].append(contrast)
    for architecture, available in sorted(by_architecture.items()):
        members = [row for row in available if row.get("complete") is True]
        summary: dict[str, Any] = {
            "architecture": architecture,
            "available_seed_cells": len(available),
            "matched_seed_cells": len(members),
            "partial_seed_cells": len(available) - len(members),
            "data_seeds": sorted({int(row["data_seed"]) for row in members}),
            "model_seeds": sorted({int(row["model_seed"]) for row in members}),
            "interpretation": (
                "matched correct-calibration minus scrambled-calibration contrast; "
                "bounded learned binding under the frozen protocol, not emergence"
            ),
            "crossed_seed_note": (
                "Data-seed and model-seed effects are shown separately; crossed cells "
                "are not treated as six independent datasets."
            ),
            "splits": {},
            "diagnostics": {},
            "primary_metrics": _primary_stats(members),
            "strata": {
                "by_data_seed": _contrast_strata(members, "data_seed"),
                "by_model_seed": _contrast_strata(members, "model_seed"),
            },
        }
        for split in ROLE_CONTRAST_SPLITS:
            values = _endpoint_summary(members, "splits", split, None)
            if values:
                summary["splits"][split] = values
        for family, fields in DIAGNOSTIC_FIELDS.items():
            family_summary = {}
            for field in fields:
                values = _endpoint_summary(members, "diagnostics", family, field)
                if values:
                    family_summary[field] = values
            summary["diagnostics"][family] = family_summary
        summaries.append(summary)
    return contrasts, summaries, issues


def _gate_check(
    *,
    observed: float | int | bool | None,
    threshold: float | int | bool,
    passed: bool | None,
    definition: str,
) -> dict[str, Any]:
    return {
        "status": "INCOMPLETE" if passed is None else ("PASS" if passed else "FAIL"),
        "observed": observed,
        "threshold": threshold,
        "definition": definition,
    }


def _learned_binding_gate(
    contrasts: Sequence[Mapping[str, Any]],
    expected: Mapping[str, Sequence[Any]],
    settings: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Adjudicate the frozen, bounded H2 gate over paired crossed-seed cells."""

    configured = bool(settings)
    raw = dict(settings or {})
    thresholds = {
        "minimum_mean_renamed_accuracy_gain_over_scrambled_arm": float(
            raw.get("minimum_mean_renamed_accuracy_gain_over_scrambled_arm", 0.05)
        ),
        "minimum_mean_pair_joint_gain_over_scrambled_arm": float(
            raw.get("minimum_mean_pair_joint_gain_over_scrambled_arm", 0.05)
        ),
        "minimum_mean_correct_calibration_gain_at_test": float(
            raw.get("minimum_mean_correct_calibration_gain_at_test", 0.05)
        ),
        "minimum_positive_seed_cells": int(raw.get("minimum_positive_seed_cells", 5)),
        "require_positive_each_data_seed_mean": bool(
            raw.get("require_positive_each_data_seed_mean", True)
        ),
        "minimum_correct_arm_renamed_accuracy": float(
            raw.get("minimum_correct_arm_renamed_accuracy", 0.60)
        ),
        "minimum_correct_arm_prediction_consistency": float(
            raw.get("minimum_correct_arm_prediction_consistency", 0.80)
        ),
        "minimum_correct_arm_pair_joint_correctness": float(
            raw.get("minimum_correct_arm_pair_joint_correctness", 0.55)
        ),
        "maximum_mean_heldout_pair_accuracy_loss": float(
            raw.get("maximum_mean_heldout_pair_accuracy_loss", 0.05)
        ),
        "maximum_mean_heldout_triple_accuracy_loss": float(
            raw.get("maximum_mean_heldout_triple_accuracy_loss", 0.05)
        ),
    }
    architectures = sorted(
        set(str(value) for value in expected.get("architectures", ()))
        | {str(row.get("architecture", "unspecified")) for row in contrasts}
    )
    expected_pairs = {
        (int(data_seed), int(model_seed))
        for data_seed in expected.get("data_seeds", ())
        for model_seed in expected.get("model_seeds", ())
    }
    expected_data_seeds = sorted(int(value) for value in expected.get("data_seeds", ()))
    architecture_results: list[dict[str, Any]] = []

    for architecture in architectures:
        available = [
            row for row in contrasts if str(row.get("architecture")) == architecture
        ]
        members = [row for row in available if row.get("complete") is True]
        observed_pairs = {
            (int(row["data_seed"]), int(row["model_seed"])) for row in members
        }
        required_pairs = expected_pairs or observed_pairs
        missing_pairs = sorted(required_pairs - observed_pairs)
        primary = _primary_stats(members)

        def mean(metric: str) -> float | None:
            value = primary.get(metric, {})
            return _finite_number(value.get("mean") if isinstance(value, Mapping) else None)

        positive_cells = [
            row
            for row in members
            if all(
                (
                    value := _finite_number(
                        row.get("primary", {}).get(metric)
                        if isinstance(row.get("primary"), Mapping)
                        else None
                    )
                )
                is not None
                and value > 0.0
                for metric in ROLE_POSITIVE_METRICS
            )
        ]
        by_data_seed = _contrast_strata(members, "data_seed")
        by_model_seed = _contrast_strata(members, "model_seed")
        data_seed_positive: list[dict[str, Any]] = []
        for data_seed in sorted(
            set(expected_data_seeds) | {int(row["data_seed"]) for row in members}
        ):
            stratum_members = [row for row in members if int(row["data_seed"]) == data_seed]
            means = {
                metric: _finite_number(_primary_stats(stratum_members).get(metric, {}).get("mean"))
                for metric in ROLE_POSITIVE_METRICS
            }
            positive = bool(stratum_members) and all(
                value is not None and value > 0.0 for value in means.values()
            )
            data_seed_positive.append(
                {
                    "data_seed": data_seed,
                    "crossed_cell_count": len(stratum_members),
                    "primary_means": means,
                    "all_primary_means_positive": positive,
                }
            )

        complete = bool(required_pairs) and not missing_pairs and len(members) == len(required_pairs)
        renamed_gain = mean("renamed_accuracy_gain_over_scrambled_arm")
        pair_joint_gain = mean("pair_joint_gain_over_scrambled_arm")
        calibration_gain = mean("correct_calibration_gain_at_test")
        correct_renamed = mean("correct_arm_renamed_accuracy")
        correct_consistency = mean("correct_arm_prediction_consistency")
        correct_joint = mean("correct_arm_pair_joint_correctness")
        pair_delta = mean("heldout_pair_accuracy_delta_vs_scrambled")
        triple_delta = mean("heldout_triple_accuracy_delta_vs_scrambled")
        pair_loss = None if pair_delta is None else -pair_delta
        triple_loss = None if triple_delta is None else -triple_delta
        every_data_seed_positive = bool(data_seed_positive) and all(
            row["all_primary_means_positive"] for row in data_seed_positive
        )

        checks = {
            "complete_crossed_seed_matrix": _gate_check(
                observed=len(members),
                threshold=len(required_pairs),
                passed=complete if required_pairs else None,
                definition="one complete three-arm contrast for every expected data/model seed cell",
            ),
            "mean_renamed_accuracy_gain_over_scrambled_arm": _gate_check(
                observed=renamed_gain,
                threshold=thresholds[
                    "minimum_mean_renamed_accuracy_gain_over_scrambled_arm"
                ],
                passed=(
                    None
                    if renamed_gain is None
                    else renamed_gain
                    >= thresholds[
                        "minimum_mean_renamed_accuracy_gain_over_scrambled_arm"
                    ]
                ),
                definition="mean role_bind_augmented minus role_bind_scrambled renamed accuracy",
            ),
            "mean_pair_joint_gain_over_scrambled_arm": _gate_check(
                observed=pair_joint_gain,
                threshold=thresholds[
                    "minimum_mean_pair_joint_gain_over_scrambled_arm"
                ],
                passed=(
                    None
                    if pair_joint_gain is None
                    else pair_joint_gain
                    >= thresholds["minimum_mean_pair_joint_gain_over_scrambled_arm"]
                ),
                definition="mean role_bind_augmented minus role_bind_scrambled pair-joint correctness",
            ),
            "mean_correct_calibration_gain_at_test": _gate_check(
                observed=calibration_gain,
                threshold=thresholds["minimum_mean_correct_calibration_gain_at_test"],
                passed=(
                    None
                    if calibration_gain is None
                    else calibration_gain
                    >= thresholds["minimum_mean_correct_calibration_gain_at_test"]
                ),
                definition="mean within-model correct_minus_scrambled_accuracy for the correct-calibration arm",
            ),
            "positive_complete_seed_cells": _gate_check(
                observed=len(positive_cells),
                threshold=thresholds["minimum_positive_seed_cells"],
                passed=len(positive_cells) >= thresholds["minimum_positive_seed_cells"],
                definition="cells where all three primary learned-binding effects are strictly positive",
            ),
            "positive_each_data_seed_mean": _gate_check(
                observed=every_data_seed_positive,
                threshold=thresholds["require_positive_each_data_seed_mean"],
                passed=(
                    True
                    if not thresholds["require_positive_each_data_seed_mean"]
                    else every_data_seed_positive
                ),
                definition="all three primary effects have positive means within every expected data seed",
            ),
            "correct_arm_mean_renamed_accuracy": _gate_check(
                observed=correct_renamed,
                threshold=thresholds["minimum_correct_arm_renamed_accuracy"],
                passed=(
                    None
                    if correct_renamed is None
                    else correct_renamed
                    >= thresholds["minimum_correct_arm_renamed_accuracy"]
                ),
                definition="mean renamed accuracy of role_bind_augmented",
            ),
            "correct_arm_mean_prediction_consistency": _gate_check(
                observed=correct_consistency,
                threshold=thresholds[
                    "minimum_correct_arm_prediction_consistency"
                ],
                passed=(
                    None
                    if correct_consistency is None
                    else correct_consistency
                    >= thresholds["minimum_correct_arm_prediction_consistency"]
                ),
                definition="mean canonical/correct-renamed prediction consistency of role_bind_augmented",
            ),
            "correct_arm_mean_pair_joint_correctness": _gate_check(
                observed=correct_joint,
                threshold=thresholds[
                    "minimum_correct_arm_pair_joint_correctness"
                ],
                passed=(
                    None
                    if correct_joint is None
                    else correct_joint
                    >= thresholds["minimum_correct_arm_pair_joint_correctness"]
                ),
                definition="mean canonical/correct-renamed pair-joint correctness of role_bind_augmented",
            ),
            "mean_heldout_pair_accuracy_loss": _gate_check(
                observed=pair_loss,
                threshold=thresholds["maximum_mean_heldout_pair_accuracy_loss"],
                passed=(
                    None
                    if pair_loss is None
                    else pair_loss
                    <= thresholds["maximum_mean_heldout_pair_accuracy_loss"]
                ),
                definition="role_bind_scrambled minus role_bind_augmented mean heldout-pair accuracy",
            ),
            "mean_heldout_triple_accuracy_loss": _gate_check(
                observed=triple_loss,
                threshold=thresholds["maximum_mean_heldout_triple_accuracy_loss"],
                passed=(
                    None
                    if triple_loss is None
                    else triple_loss
                    <= thresholds["maximum_mean_heldout_triple_accuracy_loss"]
                ),
                definition="role_bind_scrambled minus role_bind_augmented mean heldout-triple accuracy",
            ),
        }
        statuses = [str(value["status"]) for value in checks.values()]
        if not configured or "INCOMPLETE" in statuses:
            status = "INCOMPLETE"
        elif "FAIL" in statuses:
            status = "FAIL"
        else:
            status = "PASS"
        architecture_results.append(
            {
                "architecture": architecture,
                "status": status,
                "expected_crossed_cells": len(required_pairs),
                "complete_crossed_cells": len(members),
                "missing_crossed_cells": [
                    {"data_seed": data_seed, "model_seed": model_seed}
                    for data_seed, model_seed in missing_pairs
                ],
                "positive_complete_cells": len(positive_cells),
                "checks": checks,
                "primary_metrics": primary,
                "data_seed_positive_effects": data_seed_positive,
                "crossed_seed_strata": {
                    "by_data_seed": by_data_seed,
                    "by_model_seed": by_model_seed,
                },
            }
        )

    statuses = [str(row["status"]) for row in architecture_results]
    if not configured or not architecture_results or "INCOMPLETE" in statuses:
        overall = "INCOMPLETE"
    elif "FAIL" in statuses:
        overall = "FAIL"
    else:
        overall = "PASS"
    return {
        "name": "bounded_learned_binding_h2",
        "configured": configured,
        "status": overall,
        "claim_boundary": (
            "PASS supports bounded learned role binding under this frozen generator, "
            "architecture, and seed schedule. It is not evidence of emergence."
        ),
        "analysis_unit": (
            "paired arm differences within crossed data-seed/model-seed cells, with "
            "separate data-seed and model-seed strata; cells are not assumed IID datasets"
        ),
        "thresholds": thresholds,
        "architectures": architecture_results,
    }


def _matrix_completeness(
    rows: Sequence[Mapping[str, Any]], expected: Mapping[str, Sequence[Any]]
) -> dict[str, Any]:
    observed_runs = sorted({(int(row["data_seed"]), int(row["model_seed"])) for row in rows})
    expected_runs = [
        (int(data_seed), int(model_seed))
        for data_seed in expected["data_seeds"]
        for model_seed in expected["model_seeds"]
    ]
    missing_runs = sorted(set(expected_runs) - set(observed_runs))
    expected_cells = {
        (data_seed, model_seed, str(architecture), str(arm), str(split))
        for data_seed, model_seed in expected_runs
        for architecture in expected["architectures"]
        for arm in expected["arms"]
        for split in expected["splits"]
    }
    observed_cells = {
        (
            int(row["data_seed"]),
            int(row["model_seed"]),
            str(row["architecture"]),
            str(row["arm"]),
            str(row["split"]),
        )
        for row in rows
    }
    missing_cells = sorted(expected_cells - observed_cells)
    return {
        "expected_run_count": len(expected_runs),
        "observed_run_count": len(observed_runs),
        "missing_runs": [
            {"data_seed": data_seed, "model_seed": model_seed}
            for data_seed, model_seed in missing_runs
        ],
        "expected_evaluation_cells": len(expected_cells),
        "observed_expected_evaluation_cells": len(expected_cells & observed_cells),
        "missing_evaluation_cells": [
            {
                "data_seed": row[0],
                "model_seed": row[1],
                "architecture": row[2],
                "arm": row[3],
                "split": row[4],
            }
            for row in missing_cells
        ],
        "complete": not missing_runs and not missing_cells if expected_runs else bool(observed_runs),
    }


def aggregate_runs(
    runs_root: str | Path,
    *,
    config: str | Path | None = None,
    expected_data_seeds: Sequence[int] | None = None,
    expected_model_seeds: Sequence[int] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Scan completed run directories and produce a stable aggregate payload."""

    root = Path(runs_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"runs root not found: {root}")
    configuration = _load_config(config)
    config_path = Path(config).resolve() if config is not None else None
    expected_config_sha256 = sha256_file(config_path) if config_path is not None else None
    package_manifest_path = PROJECT_ROOT / "MANIFEST.json"
    current_package_manifest_sha256 = (
        sha256_file(package_manifest_path) if package_manifest_path.is_file() else None
    )
    expected = _expected_values(configuration, expected_data_seeds, expected_model_seeds)
    replication = dict(configuration.get("replication", {}))
    minimum_margin = float(replication.get("baseline_gate_min_margin", 0.0))
    rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    explicit_gates: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    completed_runs: list[dict[str, Any]] = []

    metadata_paths = sorted(root.rglob("run_metadata.json"), key=lambda path: _relative(path, root))
    provenance_candidates: list[dict[str, Any]] = []
    for metadata_path in metadata_paths:
        run_dir = metadata_path.parent
        run_name = _relative(run_dir, root)
        try:
            metadata = load_json(metadata_path)
        except Exception as exc:
            errors.append({"run": run_name, "reason": f"invalid metadata: {type(exc).__name__}: {exc}"})
            continue
        if metadata.get("completed") is not True:
            skipped.append({"run": run_name, "reason": "run_metadata.completed is not true"})
            continue
        try:
            data_seed = _integer_seed(metadata.get("data_seed"), "data_seed")
            model_seed = _integer_seed(metadata.get("model_seed"), "model_seed")
        except ValueError as exc:
            errors.append({"run": run_name, "reason": str(exc)})
            continue
        try:
            seed_issues = _seed_consistency_issues(run_dir, data_seed, model_seed)
        except Exception as exc:
            errors.append(
                {
                    "run": run_name,
                    "reason": f"could not audit seed consistency: {type(exc).__name__}: {exc}",
                }
            )
            continue
        if seed_issues:
            errors.extend({"run": run_name, "reason": issue} for issue in seed_issues)
            continue

        provenance_issues: list[str] = []
        if expected_config_sha256 is not None:
            try:
                observed_config_sha256 = _sha256_value(
                    metadata.get("config_sha256"), "run_metadata.config_sha256"
                )
            except ValueError as exc:
                provenance_issues.append(str(exc))
            else:
                if observed_config_sha256 != expected_config_sha256:
                    provenance_issues.append(
                        "run_metadata.config_sha256 does not match the supplied config "
                        f"({observed_config_sha256} != {expected_config_sha256})"
                    )

        package_manifest_sha256: str | None = None
        try:
            package_manifest_sha256 = _sha256_value(
                metadata.get("package_manifest_sha256"),
                "run_metadata.package_manifest_sha256",
            )
        except ValueError as exc:
            provenance_issues.append(str(exc))

        dataset_descriptor: dict[str, dict[str, Any]] | None = None
        try:
            dataset_descriptor = _dataset_manifest_descriptor(run_dir)
        except Exception as exc:
            provenance_issues.append(
                f"invalid dataset manifest provenance: {type(exc).__name__}: {exc}"
            )

        if provenance_issues:
            errors.extend({"run": run_name, "reason": issue} for issue in provenance_issues)
            continue
        if package_manifest_sha256 is None or dataset_descriptor is None:
            continue
        provenance_candidates.append(
            {
                "run_dir": run_dir,
                "run": run_name,
                "metadata": metadata,
                "data_seed": data_seed,
                "model_seed": model_seed,
                "package_manifest_sha256": package_manifest_sha256,
                "dataset_descriptor": dataset_descriptor,
            }
        )

    invalid_provenance_runs: set[str] = set()
    if current_package_manifest_sha256 is not None:
        for candidate in provenance_candidates:
            if candidate["package_manifest_sha256"] != current_package_manifest_sha256:
                run_name = str(candidate["run"])
                invalid_provenance_runs.add(run_name)
                errors.append(
                    {
                        "run": run_name,
                        "reason": (
                            "run_metadata.package_manifest_sha256 does not match the current "
                            f"package MANIFEST.json ({candidate['package_manifest_sha256']} != "
                            f"{current_package_manifest_sha256})"
                        ),
                    }
                )

    package_candidates = [
        candidate
        for candidate in provenance_candidates
        if candidate["run"] not in invalid_provenance_runs
    ]
    package_hashes = {
        str(candidate["package_manifest_sha256"]) for candidate in package_candidates
    }
    if len(package_hashes) > 1:
        for candidate in package_candidates:
            run_name = str(candidate["run"])
            invalid_provenance_runs.add(run_name)
            errors.append(
                {
                    "run": run_name,
                    "reason": (
                        "run_metadata.package_manifest_sha256 is not uniform across "
                        "completed replication runs"
                    ),
                }
            )

    dataset_candidates = [
        candidate
        for candidate in provenance_candidates
        if candidate["run"] not in invalid_provenance_runs
    ]
    candidates_by_data_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for candidate in dataset_candidates:
        candidates_by_data_seed[int(candidate["data_seed"])].append(candidate)
    for data_seed, candidates in sorted(candidates_by_data_seed.items()):
        descriptor_signatures = {
            json.dumps(
                candidate["dataset_descriptor"],
                sort_keys=True,
                separators=(",", ":"),
            )
            for candidate in candidates
        }
        if len(descriptor_signatures) <= 1:
            continue
        for candidate in candidates:
            run_name = str(candidate["run"])
            invalid_provenance_runs.add(run_name)
            errors.append(
                {
                    "run": run_name,
                    "reason": (
                        "dataset manifest records/sha256/semantic_sha256 descriptors are "
                        f"not identical across model seeds for data_seed={data_seed}"
                    ),
                }
            )

    accepted_candidates = [
        candidate
        for candidate in provenance_candidates
        if candidate["run"] not in invalid_provenance_runs
    ]
    accepted_dataset_descriptors: dict[str, dict[str, dict[str, Any]]] = {}
    for candidate in accepted_candidates:
        accepted_dataset_descriptors.setdefault(
            str(candidate["data_seed"]), candidate["dataset_descriptor"]
        )
    accepted_package_hashes = sorted(
        {str(candidate["package_manifest_sha256"]) for candidate in accepted_candidates}
    )

    for candidate in accepted_candidates:
        run_dir = candidate["run_dir"]
        run_name = str(candidate["run"])
        data_seed = int(candidate["data_seed"])
        model_seed = int(candidate["model_seed"])
        evaluation_paths = sorted(
            (run_dir / "experiments").glob("*/evaluation_results.json"),
            key=lambda path: path.as_posix(),
        )
        if not evaluation_paths:
            errors.append({"run": run_name, "reason": "completed run has no experiment evaluations"})
            continue
        baselines = _strongest_baselines(run_dir)
        run_rows_before = len(rows)
        for evaluation_path in evaluation_paths:
            experiment_dir = evaluation_path.parent
            architecture, arm = _experiment_identity(experiment_dir)
            try:
                evaluation = load_json(evaluation_path)
                split_metrics = evaluation["behavior"]["splits"]
            except Exception as exc:
                errors.append(
                    {
                        "run": run_name,
                        "reason": f"invalid {evaluation_path.name}: {type(exc).__name__}: {exc}",
                    }
                )
                continue
            if not isinstance(split_metrics, Mapping):
                errors.append({"run": run_name, "reason": f"{evaluation_path.name} has no split mapping"})
                continue
            diagnostic_rows.append(
                {
                    "run": run_name,
                    "data_seed": data_seed,
                    "model_seed": model_seed,
                    "architecture": architecture,
                    "arm": arm,
                    "splits": {
                        split: value
                        for split in ROLE_CONTRAST_SPLITS
                        if isinstance(split_metrics.get(split), Mapping)
                        and (
                            value := _finite_number(
                                split_metrics[split].get("accuracy")
                            )
                        )
                        is not None
                    },
                    **_extract_diagnostics(evaluation),
                }
            )
            for split, metrics in sorted(split_metrics.items()):
                if not isinstance(metrics, Mapping):
                    continue
                row: dict[str, Any] = {
                    "run": run_name,
                    "data_seed": data_seed,
                    "model_seed": model_seed,
                    "architecture": architecture,
                    "arm": arm,
                    "split": str(split),
                }
                for metric in (
                    "n",
                    "exact_correct",
                    "accuracy",
                    "macro_precision",
                    "macro_recall",
                    "macro_f1",
                    "micro_f1",
                ):
                    value = _finite_number(metrics.get(metric))
                    if value is not None:
                        row[metric] = value
                baseline = baselines.get(str(split))
                accuracy = _finite_number(row.get("accuracy"))
                if baseline is None or accuracy is None:
                    row["baseline_gate_status"] = "INCOMPLETE"
                else:
                    baseline_accuracy = float(baseline["accuracy"])
                    margin = accuracy - baseline_accuracy
                    row["strongest_baseline_accuracy"] = baseline_accuracy
                    row["strongest_baseline_models"] = list(baseline["models"])
                    row["baseline_margin"] = margin
                    row["baseline_gate_status"] = "PASS" if margin > minimum_margin else "FAIL"
                rows.append(row)

        for adjudication_path in sorted(run_dir.rglob("EVIDENCE_ADJUDICATION.json")):
            try:
                payload = load_json(adjudication_path)
            except Exception as exc:
                errors.append(
                    {
                        "run": run_name,
                        "reason": f"invalid adjudication: {type(exc).__name__}: {exc}",
                    }
                )
                continue
            parent_architecture, parent_arm = _experiment_identity(adjudication_path.parent)
            arm_value = payload.get("arm")
            architecture_value = payload.get("architecture")
            arm = str(arm_value) if arm_value else parent_arm
            architecture = str(architecture_value) if architecture_value else parent_architecture
            if adjudication_path.parent == run_dir and not architecture_value:
                candidates = sorted(
                    path.name.split("__", 1)[0]
                    for path in (run_dir / "experiments").glob(f"*__{arm}")
                    if "__" in path.name and (path / "evaluation_results.json").is_file()
                )
                if len(candidates) == 1:
                    architecture = candidates[0]
            for gate in _adjudication_gates(payload):
                explicit_gates.append(
                    {
                        "run": run_name,
                        "artifact": _relative(adjudication_path, root),
                        "data_seed": data_seed,
                        "model_seed": model_seed,
                        "architecture": architecture,
                        "arm": arm,
                        **gate,
                    }
                )
        completed_runs.append(
            {
                "run": run_name,
                "data_seed": data_seed,
                "model_seed": model_seed,
                "evaluation_rows": len(rows) - run_rows_before,
            }
        )

    rows.sort(
        key=lambda row: (
            int(row["data_seed"]),
            int(row["model_seed"]),
            str(row["architecture"]),
            str(row["arm"]),
            str(row["split"]),
            str(row["run"]),
        )
    )
    explicit_gates.sort(
        key=lambda row: (
            int(row["data_seed"]),
            int(row["model_seed"]),
            str(row["architecture"]),
            str(row["arm"]),
            str(row["gate"]),
            str(row["artifact"]),
        )
    )
    diagnostic_rows.sort(
        key=lambda row: (
            int(row["data_seed"]),
            int(row["model_seed"]),
            str(row["architecture"]),
            str(row["arm"]),
            str(row["run"]),
        )
    )
    completed_runs.sort(key=lambda row: (row["data_seed"], row["model_seed"], row["run"]))
    skipped.sort(key=lambda row: (row["run"], row["reason"]))
    errors.sort(key=lambda row: (row["run"], row["reason"]))

    duplicate_keys: list[dict[str, Any]] = []
    seen: dict[tuple[Any, ...], list[str]] = defaultdict(list)
    for row in rows:
        key = (
            row["data_seed"],
            row["model_seed"],
            row["architecture"],
            row["arm"],
            row["split"],
        )
        seen[key].append(str(row["run"]))
    for key, run_names in sorted(seen.items(), key=lambda item: tuple(str(v) for v in item[0])):
        if len(run_names) > 1:
            duplicate_keys.append(
                {
                    "data_seed": key[0],
                    "model_seed": key[1],
                    "architecture": key[2],
                    "arm": key[3],
                    "split": key[4],
                    "runs": sorted(run_names),
                }
            )

    completeness = _matrix_completeness(rows, expected)
    contrast_enabled = (
        any(arm in expected["arms"] for arm in (ROLE_CORRECT_ARM, ROLE_SCRAMBLED_ARM))
        or any(
            str(row["arm"]) in {ROLE_CORRECT_ARM, ROLE_SCRAMBLED_ARM}
            for row in diagnostic_rows
        )
    )
    role_contrasts, role_contrast_summaries, role_contrast_issues = _role_binding_contrasts(
        diagnostic_rows, enabled=contrast_enabled
    )
    learned_binding_gate = _learned_binding_gate(
        role_contrasts,
        expected,
        replication.get("learned_binding_gate")
        if isinstance(replication.get("learned_binding_gate"), Mapping)
        else None,
    )
    result = {
        "schema": SCHEMA,
        "claim_boundary": (
            "Gate statuses are behavioral replication diagnostics. They are not converted "
            "into an evidence level or a claim of symbolic-language emergence. The primary "
            "role_bind_augmented minus role_bind_scrambled contrast tests bounded learned "
            "binding under the frozen protocol; answer_only deltas are contextual only."
        ),
        "runs_root": root.name,
        "expected": expected,
        "baseline_gate_min_margin": minimum_margin,
        "provenance_audit": {
            "supplied_config_sha256": expected_config_sha256,
            "current_package_manifest_sha256": current_package_manifest_sha256,
            "accepted_package_manifest_sha256": (
                accepted_package_hashes[0] if len(accepted_package_hashes) == 1 else None
            ),
            "accepted_dataset_descriptors_by_data_seed": accepted_dataset_descriptors,
        },
        "completed_runs": completed_runs,
        "skipped_runs": skipped,
        "errors": errors,
        "duplicate_evaluation_cells": duplicate_keys,
        "matrix_completeness": completeness,
        "replicates": rows,
        "diagnostic_replicates": diagnostic_rows,
        "role_binding_contrasts": role_contrasts,
        "role_binding_contrast_issues": role_contrast_issues,
        "learned_binding_h2_gate": learned_binding_gate,
        "explicit_gate_replicates": explicit_gates,
        "summaries": {
            "per_arm_split": _summarize_rows(rows, ("architecture", "arm", "split")),
            "per_arm_split_data_seed": _summarize_rows(
                rows, ("architecture", "arm", "split", "data_seed")
            ),
            "per_arm_split_model_seed": _summarize_rows(
                rows, ("architecture", "arm", "split", "model_seed")
            ),
            "explicit_behavioral_gates": _summarize_explicit_gates(explicit_gates),
            "per_arm_diagnostics": _summarize_diagnostics(
                diagnostic_rows, ("architecture", "arm")
            ),
            "learned_role_binding_contrast": role_contrast_summaries,
            "learned_binding_h2_gate": learned_binding_gate,
        },
    }
    strict_failures = []
    if errors:
        strict_failures.append(f"{len(errors)} invalid completed run artifact(s)")
    if duplicate_keys:
        strict_failures.append(f"{len(duplicate_keys)} duplicate evaluation cell(s)")
    if role_contrast_issues:
        strict_failures.append(f"{len(role_contrast_issues)} incomplete role-binding contrast cell(s)")
    if expected["data_seeds"] and not completeness["complete"]:
        strict_failures.append("expected replication matrix is incomplete")
    if strict and strict_failures:
        raise AggregationError("; ".join(strict_failures))
    return result


def _format_rate(value: Any) -> str:
    return f"{100.0 * float(value):.1f}%"


def _format_stat(summary: Mapping[str, Any], metric: str, field: str = "mean") -> str:
    try:
        return f"{float(summary['metrics'][metric][field]):.4f}"
    except (KeyError, TypeError, ValueError):
        return "NA"


def _format_endpoint(summary: Mapping[str, Any], endpoint: str, field: str = "mean") -> str:
    try:
        return f"{float(summary[endpoint][field]):.4f}"
    except (KeyError, TypeError, ValueError):
        return "NA"


def render_markdown(result: Mapping[str, Any]) -> str:
    """Render a stable human-readable counterpart to the JSON aggregate."""

    completeness = dict(result.get("matrix_completeness", {}))
    lines = [
        "# Micro OSL Confirmatory Replication Aggregate",
        "",
        "## Claim boundary",
        "",
        str(result.get("claim_boundary", "")),
        "",
        "## Replication matrix",
        "",
        f"Completed run directories: **{len(result.get('completed_runs', []))}**",
        "",
        f"Expected crossed seed cells: **{completeness.get('expected_run_count', 0)}**",
        "",
        f"Observed crossed seed cells: **{completeness.get('observed_run_count', 0)}**",
        "",
        f"Matrix complete: **{'YES' if completeness.get('complete') else 'NO'}**",
        "",
        "## Per-arm and per-split results",
        "",
        "SD is descriptive across paired crossed seed cells. Data-seed and model-seed strata are reported separately; the cells are not treated as IID datasets.",
        "",
        "| Architecture | Arm | Split | Replicates | Accuracy mean | SD | Min | Max | Macro F1 mean | Baseline margin mean | Baseline gate pass rate |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in result.get("summaries", {}).get("per_arm_split", []):
        gate = summary.get("strongest_baseline_gate", {})
        lines.append(
            "| {architecture} | {arm} | {split} | {replicates} | {accuracy} | {sd} | {minimum} | {maximum} | {f1} | {margin} | {rate} |".format(
                architecture=summary["architecture"],
                arm=summary["arm"],
                split=summary["split"],
                replicates=summary["replicates"],
                accuracy=_format_stat(summary, "accuracy"),
                sd=_format_stat(summary, "accuracy", "sd"),
                minimum=_format_stat(summary, "accuracy", "min"),
                maximum=_format_stat(summary, "accuracy", "max"),
                f1=_format_stat(summary, "macro_f1"),
                margin=_format_stat(summary, "baseline_margin"),
                rate=_format_rate(gate.get("pass_rate_all", 0.0)),
            )
        )

    lines.extend(
        [
            "",
            "## Bounded learned-binding contrast (not emergence)",
            "",
            "The primary delta is `role_bind_augmented - role_bind_scrambled` within the same data seed, model seed, and architecture. The two role-binding arms have matched format and volume; only calibration correctness differs. `answer_only` deltas are context, not the causal contrast. A pass supports only bounded learned binding under this frozen protocol and does not establish emergence.",
            "",
        ]
    )
    contrast_summaries = result.get("summaries", {}).get(
        "learned_role_binding_contrast", []
    )
    if contrast_summaries:
        lines.extend(
            [
                "### Focused split accuracy",
                "",
                "| Architecture | Split | Cells | Answer-only | Scrambled-train | Correct-train | Correct - scrambled | Correct - answer-only |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for summary in contrast_summaries:
            for split in ROLE_CONTRAST_SPLITS:
                endpoints = summary.get("splits", {}).get(split)
                if not isinstance(endpoints, Mapping):
                    continue
                delta = endpoints.get(ROLE_PRIMARY_DELTA, {})
                metric_cells = delta.get("count", 0) if isinstance(delta, Mapping) else 0
                lines.append(
                    f"| {summary['architecture']} | {split} | {metric_cells} | "
                    f"{_format_endpoint(endpoints, ROLE_CONTEXT_ARM)} | "
                    f"{_format_endpoint(endpoints, ROLE_SCRAMBLED_ARM)} | "
                    f"{_format_endpoint(endpoints, ROLE_CORRECT_ARM)} | "
                    f"{_format_endpoint(endpoints, ROLE_PRIMARY_DELTA)} | "
                    f"{_format_endpoint(endpoints, ROLE_CONTEXT_DELTA)} |"
                )
        lines.extend(
            [
                "",
                "### Renaming and calibration diagnostics",
                "",
                "| Architecture | Diagnostic | Cells | Answer-only | Scrambled-train | Correct-train | Correct - scrambled | Correct - answer-only |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for summary in contrast_summaries:
            for family, fields in DIAGNOSTIC_FIELDS.items():
                if family != "renaming":
                    continue
                family_summary = summary.get("diagnostics", {}).get(family, {})
                for field in fields:
                    endpoints = family_summary.get(field)
                    if not isinstance(endpoints, Mapping):
                        continue
                    delta = endpoints.get(ROLE_PRIMARY_DELTA, {})
                    metric_cells = delta.get("count", 0) if isinstance(delta, Mapping) else 0
                    lines.append(
                        f"| {summary['architecture']} | {field} | {metric_cells} | "
                        f"{_format_endpoint(endpoints, ROLE_CONTEXT_ARM)} | "
                        f"{_format_endpoint(endpoints, ROLE_SCRAMBLED_ARM)} | "
                        f"{_format_endpoint(endpoints, ROLE_CORRECT_ARM)} | "
                        f"{_format_endpoint(endpoints, ROLE_PRIMARY_DELTA)} | "
                        f"{_format_endpoint(endpoints, ROLE_CONTEXT_DELTA)} |"
                    )
        lines.extend(["", "### Crossed-seed strata", ""])
        for summary in contrast_summaries:
            lines.append(f"Architecture `{summary['architecture']}` by data seed:")
            lines.append("")
            lines.append(
                "| Data seed | Model-seed cells | Renamed gain | Pair-joint gain | Test calibration gain |"
            )
            lines.append("|---:|---:|---:|---:|---:|")
            for stratum in summary.get("strata", {}).get("by_data_seed", []):
                primary = stratum.get("primary_metrics", {})
                lines.append(
                    f"| {stratum['data_seed']} | {stratum['crossed_cell_count']} | "
                    f"{_format_endpoint(primary, 'renamed_accuracy_gain_over_scrambled_arm')} | "
                    f"{_format_endpoint(primary, 'pair_joint_gain_over_scrambled_arm')} | "
                    f"{_format_endpoint(primary, 'correct_calibration_gain_at_test')} |"
                )
            lines.append("")
            lines.append(f"Architecture `{summary['architecture']}` by model seed:")
            lines.append("")
            lines.append(
                "| Model seed | Data-seed cells | Renamed gain | Pair-joint gain | Test calibration gain |"
            )
            lines.append("|---:|---:|---:|---:|---:|")
            for stratum in summary.get("strata", {}).get("by_model_seed", []):
                primary = stratum.get("primary_metrics", {})
                lines.append(
                    f"| {stratum['model_seed']} | {stratum['crossed_cell_count']} | "
                    f"{_format_endpoint(primary, 'renamed_accuracy_gain_over_scrambled_arm')} | "
                    f"{_format_endpoint(primary, 'pair_joint_gain_over_scrambled_arm')} | "
                    f"{_format_endpoint(primary, 'correct_calibration_gain_at_test')} |"
                )
    else:
        lines.append("No complete matched three-arm seed cells were available.")

    gate = result.get("learned_binding_h2_gate", {})
    lines.extend(["", "## Bounded learned-binding H2 gate", ""])
    if isinstance(gate, Mapping):
        lines.extend(
            [
                f"Overall status: **{gate.get('status', 'INCOMPLETE')}**",
                "",
                str(gate.get("claim_boundary", "")),
                "",
                str(gate.get("analysis_unit", "")),
                "",
            ]
        )
        for architecture_gate in gate.get("architectures", []):
            lines.append(
                f"Architecture `{architecture_gate['architecture']}`: **{architecture_gate['status']}** "
                f"({architecture_gate['complete_crossed_cells']}/{architecture_gate['expected_crossed_cells']} complete cells)"
            )
            lines.append("")
            lines.append("| Check | Status | Observed | Threshold |")
            lines.append("|---|---|---:|---:|")
            for name, check in architecture_gate.get("checks", {}).items():
                lines.append(
                    f"| {name} | {check.get('status', 'INCOMPLETE')} | "
                    f"{check.get('observed')} | {check.get('threshold')} |"
                )
            lines.append("")
    else:
        lines.append("The learned-binding H2 gate was unavailable.")

    lines.extend(["", "## Explicit behavioral adjudication gates", ""])
    gate_summaries = result.get("summaries", {}).get("explicit_behavioral_gates", [])
    if gate_summaries:
        lines.extend(
            [
                "These statuses are reproduced from `EVIDENCE_ADJUDICATION.json`. They are not an automatic E-level adjudication.",
                "",
                "| Architecture | Arm | Gate | Replicates | Pass | Fail | Incomplete | Pass rate (all) |",
                "|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for gate in gate_summaries:
            counts = gate["counts"]
            lines.append(
                f"| {gate['architecture']} | {gate['arm']} | {gate['gate']} | {gate['replicates']} | "
                f"{counts['PASS']} | {counts['FAIL']} | {counts['INCOMPLETE']} | "
                f"{_format_rate(gate['pass_rate_all'])} |"
            )
    else:
        lines.append("No explicit behavioral gate artifacts were found in completed runs.")

    lines.extend(["", "## Completeness and exclusions", ""])
    missing = completeness.get("missing_runs", [])
    if missing:
        lines.append("Missing crossed seed cells:")
        lines.append("")
        for row in missing:
            lines.append(f"- data seed `{row['data_seed']}`, model seed `{row['model_seed']}`")
    else:
        lines.append("No expected crossed seed cells are missing.")
    skipped = result.get("skipped_runs", [])
    errors = result.get("errors", [])
    duplicates = result.get("duplicate_evaluation_cells", [])
    lines.extend(
        [
            "",
            f"Incomplete run directories excluded: **{len(skipped)}**",
            "",
            f"Invalid completed artifacts: **{len(errors)}**",
            "",
            f"Duplicate evaluation cells: **{len(duplicates)}**",
            "",
        ]
    )
    return "\n".join(lines)


def write_aggregate(result: Mapping[str, Any], output_dir: str | Path) -> dict[str, str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = save_json(output / "REPLICATION_SUMMARY.json", dict(result))
    markdown_path = output / "REPLICATION_REPORT.md"
    markdown_path.write_text(render_markdown(result), encoding="utf-8", newline="\n")
    return {"json": str(json_path.resolve()), "markdown": str(markdown_path.resolve())}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aggregate completed Micro OSL crossed-seed runs")
    subparsers = parser.add_subparsers(dest="command", required=True)
    aggregate = subparsers.add_parser("aggregate")
    aggregate.add_argument("--runs-root", required=True)
    aggregate.add_argument("--output-dir", required=True)
    aggregate.add_argument("--config")
    aggregate.add_argument("--expected-data-seed", action="append", type=int)
    aggregate.add_argument("--expected-model-seed", action="append", type=int)
    aggregate.add_argument("--strict", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = aggregate_runs(
            args.runs_root,
            config=args.config,
            expected_data_seeds=args.expected_data_seed,
            expected_model_seeds=args.expected_model_seed,
            strict=args.strict,
        )
        paths = write_aggregate(result, args.output_dir)
        print(json.dumps({"status": "PASS", **paths}, sort_keys=True))
        return 0
    except (AggregationError, FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

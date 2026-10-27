"""Deterministic, label-blind diagnostics for PR-LASM Block 10.

This module deliberately does not know where the ARC public solution file is.
It can load the already-frozen Block 9 delivery, but a caller must supply the
set of tasks that the independent, post-prediction audit marked as solved.
That separation lets route diagnostics be reused without turning public test
labels into compiler inputs.

The work accounting below reports counters that were actually emitted by the
Block 9 compiler.  Configured limits are retained separately and are never
presented as work performed.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from numbers import Integral, Real
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

try:
    # Use the package-wide canonical contract when the complete Block 10
    # dependency stack is importable.
    from .canonical import (
        canonical_json as _package_canonical_json,
        canonical_value as _package_canonical_value,
        deep_freeze as _package_deep_freeze,
        sha256_record as _package_sha256_record,
    )
except ImportError:  # pragma: no cover - supports isolated audit-file inspection
    _package_canonical_json = None
    _package_canonical_value = None
    _package_deep_freeze = None
    _package_sha256_record = None


SCHEMA_VERSION = 1
NO_PUBLIC_EVALUATION_CLAIM = (
    "Label-blind experiment scaffolding over a frozen Block 9 delivery. "
    "This record does not evaluate public, private, hidden, or official ARC labels."
)

PINNED_BLOCK9_ARTIFACT_SHA256: Mapping[str, str] = MappingProxyType(
    {
        "block9_submission.json": (
            "b403d0979d3414181a19c5d1614af2f9d61b3710a7ac33d985c0145d3476d14e"
        ),
        "block9_validation.json": (
            "d9f18fdde6b07a221975f1d71d105e63c6f0524da63ecce964e7bbed803df66a"
        ),
        "composition_records.json": (
            "44681f977c0c93a2f05bd9c5e5269c10461f1ebff4daee17ba514bb71299f446"
        ),
    }
)

PINNED_BLOCK9_METRICS: Mapping[str, int] = MappingProxyType(
    {
        "exact_outputs": 332,
        "whole_tasks": 301,
        "attempt_1_exact": 203,
        "attempt_2_incremental_exact": 129,
        "total_outputs": 1076,
        "total_tasks": 1000,
    }
)

EXPECTED_BLOCK9_COHORT_COUNTS: Mapping[str, int] = MappingProxyType(
    {"solved": 301, "stranded": 303, "no_transition": 396}
)

_REQUIRED_BASELINE_FILES = tuple(sorted(PINNED_BLOCK9_ARTIFACT_SHA256))


def _canonical_value(value: Any, *, path: str = "$", depth: int = 0) -> Any:
    if depth > 96:
        raise ValueError("canonical value exceeds maximum nesting depth")
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Enum):
        return _canonical_value(value.value, path=path, depth=depth + 1)
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"non-finite number at {path}")
        return number
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"canonical mapping key at {path} must be a string")
            if key in result:
                raise ValueError(f"duplicate canonical key {key!r} at {path}")
            result[key] = _canonical_value(
                item, path=f"{path}.{key}", depth=depth + 1
            )
        return {key: result[key] for key in sorted(result)}
    if isinstance(value, (tuple, list)):
        return [
            _canonical_value(item, path=f"{path}[{index}]", depth=depth + 1)
            for index, item in enumerate(value)
        ]
    if hasattr(value, "to_record") and callable(value.to_record):
        return _canonical_value(value.to_record(), path=path, depth=depth + 1)
    raise TypeError(f"unsupported canonical value {type(value).__name__} at {path}")


def canonical_value(value: Any) -> Any:
    """Return a recursively copied JSON-safe canonical value."""

    if _package_canonical_value is not None:
        return _package_canonical_value(value)
    return _canonical_value(value)


def canonical_json(value: Any) -> str:
    if _package_canonical_json is not None:
        return _package_canonical_json(value)
    return json.dumps(
        canonical_value(value),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_record(value: Any) -> str:
    if _package_sha256_record is not None:
        return _package_sha256_record(value)
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    source = Path(path)
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON number {token!r} is forbidden")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def load_json_strict(path: str | Path) -> Any:
    """Read JSON while rejecting duplicate keys and non-finite constants."""

    return json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=_unique_json_object,
        parse_constant=_reject_json_constant,
    )


def _deep_freeze(value: Any) -> Any:
    if _package_deep_freeze is not None:
        return _package_deep_freeze(value)
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _deep_freeze(item) for key, item in value.items()}
        )
    if isinstance(value, (tuple, list)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    result = int(value)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def _require_task_id(value: Any, label: str = "task_id") -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty and trimmed")
    return value


def _normalized_task_ids(values: Iterable[str], label: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes, bytearray, Mapping)):
        raise TypeError(f"{label} must be an iterable of task identifiers")
    result = tuple(_require_task_id(value, label) for value in values)
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return tuple(sorted(result))


def _validate_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    if any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _verify_embedded_hash(record: Mapping[str, Any], field: str = "content_hash") -> None:
    if field not in record:
        raise ValueError(f"record is missing {field}")
    expected = _validate_digest(record[field], field)
    payload = {key: value for key, value in record.items() if key != field}
    if sha256_record(payload) != expected:
        raise ValueError(f"embedded {field} does not match canonical record content")


def _resolve_block9_results(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve()
    candidates = (source, source / "results", source / "block9" / "results")
    for candidate in candidates:
        if all((candidate / filename).is_file() for filename in _REQUIRED_BASELINE_FILES):
            return candidate
    raise FileNotFoundError(
        "could not locate a Block 9 results directory containing "
        + ", ".join(_REQUIRED_BASELINE_FILES)
    )


@dataclass(frozen=True, slots=True)
class FrozenBlock9Baseline:
    """A hash-bound, deeply immutable view of the delivered Block 9 baseline."""

    results_directory: str
    submission: Mapping[str, Any]
    validation: Mapping[str, Any]
    records: Mapping[str, Any]
    artifact_sha256: Mapping[str, str]
    task_ids: tuple[str, ...]
    baseline_id: str

    @property
    def composition_records(self) -> Mapping[str, Any]:
        return self.records

    @property
    def exact_outputs(self) -> int:
        return int(self.validation["block9"]["exact"])

    @property
    def whole_tasks(self) -> int:
        return int(self.validation["block9"]["whole_tasks"])

    @property
    def total_outputs(self) -> int:
        return int(self.validation["block9"]["total"])

    def to_record(self) -> dict[str, Any]:
        block9 = self.validation["block9"]
        return {
            "schema": "komorebi.lasm_action.frozen_block9_baseline",
            "schema_version": SCHEMA_VERSION,
            "baseline_id": self.baseline_id,
            "artifact_sha256": dict(self.artifact_sha256),
            "task_count": len(self.task_ids),
            "task_set_hash": sha256_record(self.task_ids),
            "metrics": {
                "exact_outputs": int(block9["exact"]),
                "whole_tasks": int(block9["whole_tasks"]),
                "attempt_1_exact": int(block9["attempt_1_exact"]),
                "attempt_2_incremental_exact": int(
                    block9["attempt_2_incremental_exact"]
                ),
                "total_outputs": int(block9["total"]),
                "total_tasks": int(block9["task_total"]),
            },
            "label_access": "none",
        }


def load_frozen_block9_baseline(
    root: str | Path,
    *,
    expected_hashes: Mapping[str, str] | None = None,
    enforce_pinned_metrics: bool = True,
) -> FrozenBlock9Baseline:
    """Load and verify the three artifacts needed for Block 10 ablations.

    ``root`` may be the project root, the ``block9`` directory, or its
    ``results`` directory.  The loader never opens the ARC solutions file.
    Passing an alternate hash contract is useful for clean-extraction tests;
    release code should leave ``expected_hashes`` unset.
    """

    results = _resolve_block9_results(root)
    contract_source = (
        PINNED_BLOCK9_ARTIFACT_SHA256
        if expected_hashes is None
        else expected_hashes
    )
    if not isinstance(contract_source, Mapping):
        raise TypeError("expected_hashes must be a mapping")
    if set(contract_source) != set(_REQUIRED_BASELINE_FILES):
        raise ValueError("expected_hashes must name exactly the three Block 9 artifacts")
    contract = {
        filename: _validate_digest(contract_source[filename], filename)
        for filename in _REQUIRED_BASELINE_FILES
    }
    observed = {
        filename: sha256_file(results / filename)
        for filename in _REQUIRED_BASELINE_FILES
    }
    mismatches = {
        filename: {"expected": contract[filename], "observed": observed[filename]}
        for filename in _REQUIRED_BASELINE_FILES
        if observed[filename] != contract[filename]
    }
    if mismatches:
        raise PermissionError(
            "frozen Block 9 artifact hash mismatch: " + canonical_json(mismatches)
        )

    submission = load_json_strict(results / "block9_submission.json")
    validation = load_json_strict(results / "block9_validation.json")
    records = load_json_strict(results / "composition_records.json")
    if not all(isinstance(value, Mapping) for value in (submission, validation, records)):
        raise TypeError("Block 9 artifacts must contain JSON objects")

    if validation.get("schema") != "komorebi.lasm_recursive_composition_audit":
        raise ValueError("unexpected Block 9 validation schema")
    _verify_embedded_hash(validation)
    if validation.get("release_pass") is not True:
        raise ValueError("Block 9 validation did not pass its release gates")
    if validation.get("compile_errors"):
        raise ValueError("Block 9 validation contains compiler errors")
    if validation.get("lost_exact_outputs"):
        raise ValueError("Block 9 validation contains lost exact outputs")
    if _require_nonnegative_int(
        validation.get("wrong_committed_outputs"), "wrong_committed_outputs"
    ) != 0:
        raise ValueError("Block 9 validation contains a wrong committed output")

    block9 = validation.get("block9")
    if not isinstance(block9, Mapping):
        raise TypeError("Block 9 validation is missing its metric object")
    metrics = {
        "exact_outputs": _require_nonnegative_int(block9.get("exact"), "block9.exact"),
        "whole_tasks": _require_nonnegative_int(
            block9.get("whole_tasks"), "block9.whole_tasks"
        ),
        "attempt_1_exact": _require_nonnegative_int(
            block9.get("attempt_1_exact"), "block9.attempt_1_exact"
        ),
        "attempt_2_incremental_exact": _require_nonnegative_int(
            block9.get("attempt_2_incremental_exact"),
            "block9.attempt_2_incremental_exact",
        ),
        "total_outputs": _require_nonnegative_int(block9.get("total"), "block9.total"),
        "total_tasks": _require_nonnegative_int(
            block9.get("task_total"), "block9.task_total"
        ),
    }
    if metrics["exact_outputs"] != (
        metrics["attempt_1_exact"] + metrics["attempt_2_incremental_exact"]
    ):
        raise ValueError("Block 9 exact count does not equal its attempt decomposition")
    if metrics["exact_outputs"] > metrics["total_outputs"]:
        raise ValueError("Block 9 exact outputs exceed total outputs")
    if metrics["whole_tasks"] > metrics["total_tasks"]:
        raise ValueError("Block 9 whole-task count exceeds total tasks")
    if enforce_pinned_metrics and metrics != dict(PINNED_BLOCK9_METRICS):
        raise ValueError(
            "Block 9 metric contract mismatch: "
            + canonical_json({"expected": PINNED_BLOCK9_METRICS, "observed": metrics})
        )

    submission_ids = _normalized_task_ids(submission.keys(), "submission task IDs")
    record_ids = _normalized_task_ids(records.keys(), "record task IDs")
    if submission_ids != record_ids:
        raise ValueError("Block 9 submission and composition records cover different tasks")
    if len(record_ids) != metrics["total_tasks"]:
        raise ValueError("Block 9 task count does not match the validation record")

    output_count = 0
    for task_id in submission_ids:
        outputs = submission[task_id]
        if isinstance(outputs, (str, bytes, bytearray, Mapping)):
            raise TypeError(f"submission[{task_id!r}] must be an output sequence")
        try:
            output_count += len(outputs)
        except TypeError as error:
            raise TypeError(
                f"submission[{task_id!r}] must be a finite output sequence"
            ) from error
        record = records[task_id]
        if not isinstance(record, Mapping):
            raise TypeError(f"composition record {task_id!r} must be a mapping")
        if record.get("error"):
            raise ValueError(f"composition record {task_id!r} contains an error")
        if not isinstance(record.get("trace"), Mapping):
            raise ValueError(f"composition record {task_id!r} has no trace")
    if output_count != metrics["total_outputs"]:
        raise ValueError("submission output count does not match the validation record")

    identity_payload = {
        "schema": "komorebi.lasm_action.block9_baseline_identity",
        "schema_version": SCHEMA_VERSION,
        "artifact_sha256": observed,
        "metrics": metrics,
        "task_set_hash": sha256_record(record_ids),
    }
    baseline_id = sha256_record(identity_payload)
    return FrozenBlock9Baseline(
        results_directory=str(results),
        submission=_deep_freeze(submission),
        validation=_deep_freeze(validation),
        records=_deep_freeze(records),
        artifact_sha256=_deep_freeze(observed),
        task_ids=record_ids,
        baseline_id=baseline_id,
    )


class CohortKind(str, Enum):
    SOLVED = "solved"
    STRANDED = "stranded"
    NO_TRANSITION = "no_transition"


@dataclass(frozen=True, slots=True)
class CohortPartition:
    """A label-blind diagnostic split once frozen solved IDs are supplied."""

    solved: tuple[str, ...]
    stranded: tuple[str, ...]
    no_transition: tuple[str, ...]
    accepted_transitions: Mapping[str, int]
    partition_id: str

    @property
    def task_count(self) -> int:
        return len(self.solved) + len(self.stranded) + len(self.no_transition)

    @property
    def counts(self) -> dict[str, int]:
        return {
            CohortKind.SOLVED.value: len(self.solved),
            CohortKind.STRANDED.value: len(self.stranded),
            CohortKind.NO_TRANSITION.value: len(self.no_transition),
        }

    @property
    def all_task_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.solved + self.stranded + self.no_transition))

    def ids(self, cohort: CohortKind | str) -> tuple[str, ...]:
        key = CohortKind(cohort)
        if key is CohortKind.SOLVED:
            return self.solved
        if key is CohortKind.STRANDED:
            return self.stranded
        return self.no_transition

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.baseline_cohort_partition",
            "schema_version": SCHEMA_VERSION,
            "classification_rule": {
                "solved": "member of caller-supplied frozen solved-task set",
                "stranded": "not solved and Block 9 accepted at least one certified transition",
                "no_transition": "not solved and Block 9 accepted zero certified transitions",
            },
            "label_access": "external frozen solved-task IDs only; no labels loaded",
            "counts": self.counts,
            "task_ids": {
                "solved": list(self.solved),
                "stranded": list(self.stranded),
                "no_transition": list(self.no_transition),
            },
            "accepted_transitions": dict(self.accepted_transitions),
            "partition_id": self.partition_id,
        }
        return record


def _records_from(value: FrozenBlock9Baseline | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, FrozenBlock9Baseline):
        return value.records
    if not isinstance(value, Mapping):
        raise TypeError("records must be a mapping or FrozenBlock9Baseline")
    return value


def _trace_counter(record: Mapping[str, Any], field: str) -> int:
    trace = record.get("trace")
    if not isinstance(trace, Mapping):
        raise ValueError("composition record is missing a trace mapping")
    if field not in trace:
        raise ValueError(f"composition trace is missing required counter {field!r}")
    return _require_nonnegative_int(trace[field], f"trace.{field}")


def classify_task_cohorts(
    baseline_or_records: FrozenBlock9Baseline | Mapping[str, Any],
    solved_task_ids: Iterable[str],
    *,
    expected_counts: Mapping[str, int] | None = None,
) -> CohortPartition:
    """Split tasks into solved, stranded, and zero-transition cohorts.

    The function never derives correctness.  ``solved_task_ids`` must come from
    a separately frozen, post-prediction audit.
    """

    records = _records_from(baseline_or_records)
    task_ids = _normalized_task_ids(records.keys(), "record task IDs")
    solved = _normalized_task_ids(solved_task_ids, "solved task IDs")
    unknown = sorted(set(solved) - set(task_ids))
    if unknown:
        raise ValueError(f"solved task IDs are absent from the baseline: {unknown!r}")

    solved_set = set(solved)
    accepted: dict[str, int] = {}
    stranded: list[str] = []
    no_transition: list[str] = []
    for task_id in task_ids:
        record = records[task_id]
        if not isinstance(record, Mapping):
            raise TypeError(f"composition record {task_id!r} must be a mapping")
        count = _trace_counter(record, "transitions_accepted")
        accepted[task_id] = count
        if task_id in solved_set:
            continue
        if count > 0:
            stranded.append(task_id)
        else:
            no_transition.append(task_id)

    base = {
        "schema": "komorebi.lasm_action.baseline_cohort_partition",
        "schema_version": SCHEMA_VERSION,
        "solved": list(solved),
        "stranded": stranded,
        "no_transition": no_transition,
        "accepted_transitions": accepted,
    }
    partition = CohortPartition(
        solved=solved,
        stranded=tuple(stranded),
        no_transition=tuple(no_transition),
        accepted_transitions=_deep_freeze(accepted),
        partition_id=sha256_record(base),
    )
    if expected_counts is not None:
        if not isinstance(expected_counts, Mapping):
            raise TypeError("expected_counts must be a mapping")
        required = {kind.value for kind in CohortKind}
        if set(expected_counts) != required:
            raise ValueError("expected_counts must contain solved, stranded, and no_transition")
        normalized = {
            key: _require_nonnegative_int(expected_counts[key], f"expected_counts.{key}")
            for key in sorted(required)
        }
        if partition.counts != normalized:
            raise ValueError(
                "baseline cohort count mismatch: "
                + canonical_json({"expected": normalized, "observed": partition.counts})
            )
    return partition


def classify_frozen_block9_tasks(
    baseline: FrozenBlock9Baseline,
    solved_task_ids: Iterable[str],
) -> CohortPartition:
    """Apply the pinned 301/303/396 Block 9 cohort contract."""

    return classify_task_cohorts(
        baseline,
        solved_task_ids,
        expected_counts=EXPECTED_BLOCK9_COHORT_COUNTS,
    )


@dataclass(frozen=True, slots=True)
class TaskWork:
    task_id: str
    proposals_considered: int
    states_expanded: int
    transitions_accepted: int
    exact_programs: int
    behavior_classes: int
    max_depth_reached: int
    candidate_behaviors: int
    rejection_counts: tuple[tuple[str, int], ...]
    limit_reached: str

    def to_record(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "proposals_considered": self.proposals_considered,
            "states_expanded": self.states_expanded,
            "transitions_accepted": self.transitions_accepted,
            "exact_programs": self.exact_programs,
            "behavior_classes": self.behavior_classes,
            "max_depth_reached": self.max_depth_reached,
            "candidate_behaviors": self.candidate_behaviors,
            "rejection_counts": dict(self.rejection_counts),
            "limit_reached": self.limit_reached,
        }


def task_work_from_record(task_id: str, record: Mapping[str, Any]) -> TaskWork:
    identifier = _require_task_id(task_id)
    if not isinstance(record, Mapping):
        raise TypeError("composition record must be a mapping")
    trace = record.get("trace")
    if not isinstance(trace, Mapping):
        raise ValueError(f"composition record {identifier!r} is missing a trace")
    rejection_source = trace.get("rejection_counts", {})
    if not isinstance(rejection_source, Mapping):
        raise TypeError("trace.rejection_counts must be a mapping")
    rejection_counts: list[tuple[str, int]] = []
    names: list[str] = []
    for name in rejection_source:
        if not isinstance(name, str) or not name or name != name.strip():
            raise ValueError("rejection count names must be nonempty strings")
        names.append(name)
    for name in sorted(names):
        rejection_counts.append(
            (name, _require_nonnegative_int(rejection_source[name], f"rejection_counts.{name}"))
        )
    limit = trace.get("limit_reached", "")
    if not isinstance(limit, str):
        raise TypeError("trace.limit_reached must be a string")
    candidates = record.get("candidates", ())
    if isinstance(candidates, (str, bytes, bytearray, Mapping)):
        raise TypeError("composition candidates must be a finite sequence")
    try:
        candidate_behaviors = len(candidates)
    except TypeError as error:
        raise TypeError("composition candidates must be a finite sequence") from error
    return TaskWork(
        task_id=identifier,
        proposals_considered=_trace_counter(record, "proposals_considered"),
        states_expanded=_trace_counter(record, "states_expanded"),
        transitions_accepted=_trace_counter(record, "transitions_accepted"),
        exact_programs=_trace_counter(record, "exact_programs"),
        behavior_classes=_trace_counter(record, "behavior_classes"),
        max_depth_reached=_trace_counter(record, "max_depth_reached"),
        candidate_behaviors=candidate_behaviors,
        rejection_counts=tuple(rejection_counts),
        limit_reached=limit,
    )


def _histogram(values: Iterable[int]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return {key: result[key] for key in sorted(result, key=int)}


def _aggregate_work(items: Sequence[TaskWork]) -> dict[str, Any]:
    fields = (
        "proposals_considered",
        "states_expanded",
        "transitions_accepted",
        "exact_programs",
        "behavior_classes",
    )
    totals = {
        field: sum(int(getattr(item, field)) for item in items)
        for field in fields
    }
    maxima = {
        field: max((int(getattr(item, field)) for item in items), default=0)
        for field in fields
    }
    rejections: dict[str, int] = {}
    limits: dict[str, int] = {}
    for item in items:
        for name, count in item.rejection_counts:
            rejections[name] = rejections.get(name, 0) + count
        if item.limit_reached:
            limits[item.limit_reached] = limits.get(item.limit_reached, 0) + 1
    return {
        "task_count": len(items),
        "totals": totals,
        "maxima": maxima,
        "tasks_with_proposals": sum(item.proposals_considered > 0 for item in items),
        "tasks_with_expanded_states": sum(item.states_expanded > 0 for item in items),
        "tasks_with_accepted_transitions": sum(
            item.transitions_accepted > 0 for item in items
        ),
        "tasks_with_candidate_behaviors": sum(item.candidate_behaviors > 0 for item in items),
        "tasks_reaching_a_limit": sum(bool(item.limit_reached) for item in items),
        "state_expansion_histogram": _histogram(item.states_expanded for item in items),
        "accepted_transition_histogram": _histogram(
            item.transitions_accepted for item in items
        ),
        "rejection_counts": {key: rejections[key] for key in sorted(rejections)},
        "limit_reasons": {key: limits[key] for key in sorted(limits)},
    }


@dataclass(frozen=True, slots=True)
class WorkAccounting:
    per_task: Mapping[str, TaskWork]
    aggregate: Mapping[str, Any]
    by_cohort: Mapping[str, Any]
    configured_limits: Mapping[str, Any]
    accounting_id: str

    def to_record(self, *, include_per_task: bool = True) -> dict[str, Any]:
        record: dict[str, Any] = {
            "schema": "komorebi.lasm_action.actual_work_accounting",
            "schema_version": SCHEMA_VERSION,
            "accounting_basis": "counters emitted by completed compiler traces",
            "configured_limits_are_not_actual_work": True,
            "aggregate": canonical_value(self.aggregate),
            "by_cohort": canonical_value(self.by_cohort),
            "configured_limits": canonical_value(self.configured_limits),
            "accounting_id": self.accounting_id,
        }
        if include_per_task:
            record["per_task"] = {
                task_id: self.per_task[task_id].to_record()
                for task_id in sorted(self.per_task)
            }
        return record


def account_actual_work(
    baseline_or_records: FrozenBlock9Baseline | Mapping[str, Any],
    *,
    partition: CohortPartition | None = None,
    configured_limits: Mapping[str, Any] | None = None,
) -> WorkAccounting:
    """Aggregate emitted work counters, optionally by diagnostic cohort."""

    records = _records_from(baseline_or_records)
    items = {
        task_id: task_work_from_record(task_id, records[task_id])
        for task_id in sorted(records)
    }
    if partition is not None and tuple(sorted(items)) != partition.all_task_ids:
        raise ValueError("cohort partition and work records cover different task sets")
    by_cohort: dict[str, Any] = {}
    if partition is not None:
        for cohort in CohortKind:
            by_cohort[cohort.value] = _aggregate_work(
                tuple(items[task_id] for task_id in partition.ids(cohort))
            )
    normalized_limits = canonical_value(configured_limits or {})
    aggregate = _aggregate_work(tuple(items.values()))
    identity = {
        "schema": "komorebi.lasm_action.actual_work_accounting_identity",
        "schema_version": SCHEMA_VERSION,
        "per_task": {
            task_id: items[task_id].to_record() for task_id in sorted(items)
        },
        "aggregate": aggregate,
        "by_cohort": by_cohort,
        "configured_limits": normalized_limits,
    }
    return WorkAccounting(
        per_task=MappingProxyType(items),
        aggregate=_deep_freeze(aggregate),
        by_cohort=_deep_freeze(by_cohort),
        configured_limits=_deep_freeze(normalized_limits),
        accounting_id=sha256_record(identity),
    )


def deterministic_validation_record(
    *,
    schema: str,
    payload: Mapping[str, Any],
    gates: Mapping[str, bool],
    source_hashes: Mapping[str, str] | None = None,
    claim_boundary: str = NO_PUBLIC_EVALUATION_CLAIM,
    schema_version: int = SCHEMA_VERSION,
) -> dict[str, Any]:
    """Create a byte-stable validation record with no wall-clock fields."""

    if not isinstance(schema, str) or not schema or schema != schema.strip():
        raise ValueError("schema must be nonempty and trimmed")
    if isinstance(schema_version, bool) or not isinstance(schema_version, Integral):
        raise TypeError("schema_version must be an integer")
    if int(schema_version) <= 0:
        raise ValueError("schema_version must be positive")
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    if not isinstance(gates, Mapping) or not gates:
        raise ValueError("gates must be a nonempty mapping")
    normalized_gates: dict[str, bool] = {}
    for name in sorted(gates):
        if not isinstance(name, str) or not name or name != name.strip():
            raise ValueError("gate names must be nonempty and trimmed")
        if type(gates[name]) is not bool:
            raise TypeError(f"gate {name!r} must be Boolean")
        normalized_gates[name] = gates[name]
    normalized_sources: dict[str, str] = {}
    for name, digest in sorted((source_hashes or {}).items()):
        if not isinstance(name, str) or not name or name != name.strip():
            raise ValueError("source hash names must be nonempty and trimmed")
        normalized_sources[name] = _validate_digest(digest, f"source_hashes.{name}")
    if not isinstance(claim_boundary, str) or not claim_boundary.strip():
        raise ValueError("claim_boundary must be a nonempty string")
    record = {
        "schema": schema,
        "schema_version": int(schema_version),
        "claim_boundary": claim_boundary.strip(),
        "source_hashes": normalized_sources,
        "payload": canonical_value(payload),
        "gates": normalized_gates,
        "pass": all(normalized_gates.values()),
    }
    record["content_hash"] = sha256_record(record)
    return record


def verify_deterministic_validation_record(
    record: Mapping[str, Any],
    *,
    expected_schema: str | None = None,
) -> bool:
    """Raise on any malformed or noncanonical validation certificate."""

    if not isinstance(record, Mapping):
        raise TypeError("validation record must be a mapping")
    version = record.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, Integral) or int(version) <= 0:
        raise ValueError("validation schema_version must be a positive integer")
    schema = record.get("schema")
    if not isinstance(schema, str) or not schema or schema != schema.strip():
        raise ValueError("validation schema must be nonempty and trimmed")
    if expected_schema is not None and record.get("schema") != expected_schema:
        raise ValueError("validation record schema mismatch")
    claim_boundary = record.get("claim_boundary")
    if not isinstance(claim_boundary, str) or not claim_boundary.strip():
        raise ValueError("validation claim_boundary must be nonempty")
    if not isinstance(record.get("payload"), Mapping):
        raise TypeError("validation payload must be a mapping")
    gates = record.get("gates")
    if not isinstance(gates, Mapping) or not gates:
        raise ValueError("validation record has no gates")
    for name, value in gates.items():
        if not isinstance(name, str) or type(value) is not bool:
            raise TypeError("validation gates must map strings to Booleans")
    expected_pass = all(gates.values())
    if record.get("pass") is not expected_pass:
        raise ValueError("validation pass flag does not equal the conjunction of gates")
    source_hashes = record.get("source_hashes")
    if not isinstance(source_hashes, Mapping):
        raise TypeError("validation source_hashes must be a mapping")
    for name, digest in source_hashes.items():
        _validate_digest(digest, f"source_hashes.{name}")
    _verify_embedded_hash(record)
    return True


# Concise aliases used by audit scripts and clean-extraction tests.
load_frozen_block9 = load_frozen_block9_baseline
classify_block9_cohorts = classify_frozen_block9_tasks
actual_work_accounting = account_actual_work
build_validation_record = deterministic_validation_record
verify_validation_record = verify_deterministic_validation_record


__all__ = [
    "CohortKind",
    "CohortPartition",
    "EXPECTED_BLOCK9_COHORT_COUNTS",
    "FrozenBlock9Baseline",
    "NO_PUBLIC_EVALUATION_CLAIM",
    "PINNED_BLOCK9_ARTIFACT_SHA256",
    "PINNED_BLOCK9_METRICS",
    "SCHEMA_VERSION",
    "TaskWork",
    "WorkAccounting",
    "account_actual_work",
    "actual_work_accounting",
    "build_validation_record",
    "canonical_json",
    "canonical_value",
    "classify_block9_cohorts",
    "classify_frozen_block9_tasks",
    "classify_task_cohorts",
    "deterministic_validation_record",
    "load_frozen_block9",
    "load_frozen_block9_baseline",
    "load_json_strict",
    "sha256_file",
    "sha256_record",
    "task_work_from_record",
    "verify_deterministic_validation_record",
    "verify_validation_record",
]

"""Deterministic sampled hypothesis tournament and promotion records.

The tournament is an engineering harness, not an answer selector.  Candidate
generation freezes before a scorer may attach outcomes.  Runtime promotion
records deliberately strip task identities, predictions, and labels.

Author: Komorebi P.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_composition.model import canonical_value, sha256_record, validate_grid


class Stage(str, Enum):
    SMOKE = "smoke"
    VALIDATION = "validation"
    CORPUS = "corpus"


def deterministic_partition(
    task_ids: Iterable[str],
    *,
    salt: str,
    smoke: int,
    validation: int,
    exclusions: Iterable[str] = (),
) -> dict[Stage, tuple[str, ...]]:
    """Partition task identities before any label is inspected."""

    if not isinstance(salt, str) or not salt:
        raise ValueError("salt must be a nonempty string")
    if isinstance(smoke, bool) or not isinstance(smoke, int) or smoke < 0:
        raise ValueError("smoke must be a nonnegative integer")
    if isinstance(validation, bool) or not isinstance(validation, int) or validation < 0:
        raise ValueError("validation must be a nonnegative integer")
    excluded = frozenset(str(value) for value in exclusions)
    unique = {str(value) for value in task_ids}
    ranked = tuple(sorted(
        unique - excluded,
        key=lambda task_id: (
            hashlib.sha256(f"{salt}:{task_id}".encode("utf-8")).hexdigest(),
            task_id,
        ),
    ))
    return {
        Stage.SMOKE: ranked[:smoke],
        Stage.VALIDATION: ranked[smoke:smoke + validation],
        Stage.CORPUS: ranked,
    }


@dataclass(frozen=True, slots=True)
class TaskWork:
    """Actual work and frozen candidate behavior for one lane/task pair."""

    task_id: str
    proposals: int
    executions: int
    candidate_behaviors: int
    prediction_hashes: tuple[str, ...] = ()
    truncated: bool = False
    error: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id:
            raise ValueError("task_id must be a nonempty string")
        for name in ("proposals", "executions", "candidate_behaviors"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.candidate_behaviors != len(self.prediction_hashes):
            raise ValueError("candidate count and prediction hashes disagree")
        if tuple(sorted(set(self.prediction_hashes))) != self.prediction_hashes:
            raise ValueError("prediction hashes must be sorted and unique")

    @property
    def selectable(self) -> bool:
        return not self.truncated and not self.error and self.candidate_behaviors == 1

    def to_record(self) -> dict[str, Any]:
        body = {
            "task_id": self.task_id,
            "proposals": self.proposals,
            "executions": self.executions,
            "candidate_behaviors": self.candidate_behaviors,
            "prediction_hashes": list(self.prediction_hashes),
            "truncated": self.truncated,
            "error": self.error,
            "selectable": self.selectable,
        }
        body["content_hash"] = sha256_record(body)
        return body


@dataclass(frozen=True, slots=True)
class FrozenLaneLedger:
    """Content-addressed, pre-score ledger for one hypothesis lane."""

    lane: str
    stage: Stage
    grammar_hash: str
    sample_hash: str
    source_hashes: tuple[tuple[str, str], ...]
    tasks: tuple[TaskWork, ...]

    def __post_init__(self) -> None:
        if not self.lane or not self.grammar_hash or not self.sample_hash:
            raise ValueError("lane, grammar_hash, and sample_hash are required")
        if tuple(sorted(self.source_hashes)) != self.source_hashes:
            raise ValueError("source_hashes must be key-sorted")
        if tuple(sorted(self.tasks, key=lambda item: item.task_id)) != self.tasks:
            raise ValueError("tasks must be sorted by task_id")
        if len({item.task_id for item in self.tasks}) != len(self.tasks):
            raise ValueError("task identities must be unique within a ledger")

    def to_record(self) -> dict[str, Any]:
        body = {
            "schema": "komorebi.lasm_transfer.frozen_lane_ledger",
            "schema_version": 1,
            "lane": self.lane,
            "stage": self.stage.value,
            "grammar_hash": self.grammar_hash,
            "sample_hash": self.sample_hash,
            "source_hashes": dict(self.source_hashes),
            "tasks": [item.to_record() for item in self.tasks],
            "label_access": "none",
        }
        body["content_hash"] = sha256_record(body)
        return canonical_value(body)


@dataclass(frozen=True, slots=True)
class ScoredActivation:
    task_id: str
    exact: bool
    schema_keys: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id:
            raise ValueError("task_id must be a nonempty string")
        if not isinstance(self.exact, bool):
            raise TypeError("exact must be Boolean")
        object.__setattr__(self, "schema_keys", tuple(self.schema_keys))
        if not self.schema_keys or any(
            not isinstance(value, str) or not value for value in self.schema_keys
        ):
            raise ValueError("schema_keys must contain nonempty strings")
        if tuple(sorted(set(self.schema_keys))) != self.schema_keys:
            raise ValueError("schema_keys must be sorted and unique")


def promotion_record(
    schema_key: str,
    activations: Sequence[ScoredActivation],
    *,
    minimum_exact_tasks: int = 2,
) -> dict[str, Any]:
    """Create a task-free runtime decision from a separate score stream."""

    if not schema_key:
        raise ValueError("schema_key must be nonempty")
    if (
        isinstance(minimum_exact_tasks, bool)
        or not isinstance(minimum_exact_tasks, int)
        or minimum_exact_tasks < 1
    ):
        raise ValueError("minimum_exact_tasks must be a positive integer")
    task_ids = tuple(item.task_id for item in activations)
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("promotion activations must have distinct task IDs")
    relevant = tuple(item for item in activations if schema_key in item.schema_keys)
    exact = sum(item.exact for item in relevant)
    wrong = len(relevant) - exact
    stable = exact >= minimum_exact_tasks and wrong == 0
    body = {
        "schema": "komorebi.lasm_transfer.promotion_record",
        "schema_version": 1,
        "schema_key": schema_key,
        "status": "stable" if stable else "provisional" if exact and not wrong else "rejected",
        "support": exact,
        "incorrect_activations": wrong,
        "minimum_exact_tasks": minimum_exact_tasks,
        "contains_task_ids": False,
        "contains_predictions": False,
        "contains_labels": False,
    }
    body["content_hash"] = sha256_record(body)
    return canonical_value(body)


def quotient_behaviors(
    lane_behaviors: Iterable[tuple[str, Sequence[Any], Mapping[str, Any]]],
) -> tuple[dict[str, Any], ...]:
    """Union candidates by exact raster behavior, retaining all mechanisms."""

    groups: dict[str, dict[str, Any]] = {}
    for lane, predictions, mechanism in lane_behaviors:
        if not isinstance(lane, str) or not lane:
            raise ValueError("candidate lane must be a nonempty string")
        if "lane" in mechanism:
            raise ValueError("mechanism cannot override the reserved lane field")
        if isinstance(predictions, (str, bytes, bytearray, Mapping)):
            raise TypeError("predictions must be a finite sequence of grids")
        normalized_grids = tuple(validate_grid(value) for value in predictions)
        if not normalized_grids:
            raise ValueError("candidate behavior must predict at least one grid")
        normalized = canonical_value(normalized_grids)
        behavior_hash = sha256_record(normalized)
        entry = groups.get(behavior_hash)
        if entry is None:
            entry = {
                "behavior_hash": behavior_hash,
                "test_predictions": normalized,
                "mechanisms": [],
            }
            groups[behavior_hash] = entry
        elif entry["test_predictions"] != normalized:
            raise RuntimeError("behavior hash collision across unequal exact rasters")
        tagged = {**canonical_value(dict(mechanism)), "lane": lane}
        tagged_hash = sha256_record(tagged)
        if all(sha256_record(item) != tagged_hash for item in entry["mechanisms"]):
            entry["mechanisms"].append(tagged)
    result = []
    for key in sorted(groups):
        entry = groups[key]
        entry["mechanisms"] = sorted(
            entry["mechanisms"], key=lambda item: (item["lane"], sha256_record(item))
        )
        entry["content_hash"] = sha256_record(entry)
        result.append(canonical_value(entry))
    return tuple(result)


__all__ = [
    "FrozenLaneLedger",
    "ScoredActivation",
    "Stage",
    "TaskWork",
    "deterministic_partition",
    "promotion_record",
    "quotient_behaviors",
]

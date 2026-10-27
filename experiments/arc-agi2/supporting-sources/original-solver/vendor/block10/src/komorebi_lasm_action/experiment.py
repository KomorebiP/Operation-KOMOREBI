"""Matched, label-blind experiment protocols for PR-LASM Block 10.

The primary design is a complete 2 x 2 x 2 factorial:

* representation: the Block 9 raster quotient or the action-congruent workspace;
* actions: the frozen registry or task-local expanded actions;
* search: the current budget or an explicitly widened budget.

Every cell receives the same task set and replicate salts.  Cell records expose
training-demonstration replay and actual work only.  Public-test evaluation is
intentionally outside this module and must occur after a solver is frozen.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from numbers import Integral, Real
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from .diagnostics import (
    NO_PUBLIC_EVALUATION_CLAIM,
    SCHEMA_VERSION,
    canonical_value,
    deterministic_validation_record,
    sha256_record,
    verify_deterministic_validation_record,
)


DEFAULT_CURRENT_SEARCH_BUDGET: Mapping[str, int | str] = MappingProxyType(
    {
        "max_depth": 2,
        "max_expansions": 8192,
        "max_frontier": 32,
        "max_proposals_per_state": 4096,
        "max_total_cost": 18,
    }
)

DEFAULT_WIDENED_SEARCH_BUDGET: Mapping[str, int | str] = MappingProxyType(
    {
        "max_depth": 4,
        "max_expansions": 32768,
        "max_frontier": 128,
        "max_proposals_per_state": 8192,
        "max_total_cost": 36,
    }
)

DEFAULT_FACTORIAL_METRICS = (
    "training_exact_programs",
    "training_unique_behaviors",
    "tasks_with_candidates",
    "tasks_beyond_root",
    "zero_transition_tasks",
    "proposals_considered",
    "states_expanded",
    "transitions_accepted",
    "executor_calls",
    "capsule_refinements",
    "leakage_witnesses",
)

GAUGE_DESCRIPTOR_SCOPE = "sanitized task content and training demonstrations only"
_FORBIDDEN_EVALUATION_FIELDS = frozenset(
    {
        "gold",
        "gold_outputs",
        "hidden",
        "hidden_labels",
        "official",
        "official_score",
        "private",
        "private_labels",
        "public_exact",
        "public_labels",
        "solutions",
        "test_exact",
        "test_labels",
        "test_outputs",
    }
)


def _require_trimmed(value: Any, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if value != value.strip() or (not allow_empty and not value):
        raise ValueError(f"{label} must be trimmed and nonempty")
    return value


def _task_ids(values: Iterable[str], label: str = "task_ids") -> tuple[str, ...]:
    if isinstance(values, (str, bytes, bytearray, Mapping)):
        raise TypeError(f"{label} must be an iterable of identifiers")
    result = tuple(_require_trimmed(value, label) for value in values)
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    if not result:
        raise ValueError(f"{label} must be nonempty")
    return tuple(sorted(result))


def _strings(values: Iterable[str], label: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes, bytearray, Mapping)):
        raise TypeError(f"{label} must be an iterable of strings")
    result = tuple(_require_trimmed(value, label) for value in values)
    if not result:
        raise ValueError(f"{label} must be nonempty")
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    result = int(value)
    if result <= 0:
        raise ValueError(f"{label} must be positive")
    return result


def _normalized_budget(value: Mapping[str, Any], label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{label} must be a nonempty mapping")
    normalized = canonical_value(value)
    if not isinstance(normalized, dict):
        raise TypeError(f"{label} must canonicalize to an object")
    for key in normalized:
        _require_trimmed(key, f"{label} key")
    return normalized


def _validate_widened_budget(current: Mapping[str, Any], widened: Mapping[str, Any]) -> None:
    """Require a monotone increase on every shared numeric resource control."""

    if set(current) != set(widened):
        raise ValueError("current and widened budgets must name the same controls")
    saw_strict_increase = False
    for key in sorted(set(current).intersection(widened)):
        left = current[key]
        right = widened[key]
        numeric_left = isinstance(left, Real) and not isinstance(left, bool)
        numeric_right = isinstance(right, Real) and not isinstance(right, bool)
        if numeric_left != numeric_right:
            raise TypeError(f"budget field {key!r} changes numeric type across search arms")
        if numeric_left:
            if right < left:
                raise ValueError(f"widened budget decreases numeric field {key!r}")
            saw_strict_increase = saw_strict_increase or right > left
    if not saw_strict_increase:
        raise ValueError("widened budget must strictly increase at least one shared numeric field")


def _assert_no_evaluation_fields(value: Any, *, path: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"record key at {path} must be a string")
            normalized = key.lower().replace("-", "_").replace(".", "_")
            if normalized in _FORBIDDEN_EVALUATION_FIELDS:
                raise ValueError(f"public/hidden evaluation field {key!r} is forbidden at {path}")
            _assert_no_evaluation_fields(item, path=f"{path}.{key}")
    elif isinstance(value, (tuple, list)):
        for index, item in enumerate(value):
            _assert_no_evaluation_fields(item, path=f"{path}[{index}]")


class RepresentationArm(str, Enum):
    OLD = "old"
    NEW = "new"


class ActionArm(str, Enum):
    FROZEN = "frozen"
    EXPANDED = "expanded"


class SearchArm(str, Enum):
    CURRENT = "current"
    WIDENED = "widened"


@dataclass(frozen=True, slots=True)
class FactorialCondition:
    representation: RepresentationArm
    actions: ActionArm
    search: SearchArm

    def __post_init__(self) -> None:
        object.__setattr__(self, "representation", RepresentationArm(self.representation))
        object.__setattr__(self, "actions", ActionArm(self.actions))
        object.__setattr__(self, "search", SearchArm(self.search))

    @property
    def condition_id(self) -> str:
        return (
            f"representation={self.representation.value}__"
            f"actions={self.actions.value}__search={self.search.value}"
        )

    @property
    def representation_contract(self) -> str:
        if self.representation is RepresentationArm.OLD:
            return "Block 9 raster state and residual quotient"
        return "action-congruent semantic workspace with exact grids authoritative"

    @property
    def action_contract(self) -> str:
        if self.actions is ActionArm.FROZEN:
            return "pinned inherited and Block 9 action registry only"
        return "frozen registry plus typed task-local action synthesis"

    def to_record(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "representation": self.representation.value,
            "actions": self.actions.value,
            "search": self.search.value,
            "representation_contract": self.representation_contract,
            "action_contract": self.action_contract,
        }


def factorial_conditions() -> tuple[FactorialCondition, ...]:
    """Return all eight cells in canonical factor order."""

    return tuple(
        FactorialCondition(representation, actions, search)
        for representation in RepresentationArm
        for actions in ActionArm
        for search in SearchArm
    )


@dataclass(frozen=True, slots=True)
class FactorialPlan:
    task_ids: tuple[str, ...]
    conditions: tuple[FactorialCondition, ...]
    current_budget: Mapping[str, Any]
    widened_budget: Mapping[str, Any]
    replicate_salts: tuple[str, ...]
    metrics: tuple[str, ...]
    cohort_partition_id: str
    plan_id: str

    @property
    def task_set_hash(self) -> str:
        return sha256_record(self.task_ids)

    def condition(self, condition_id: str) -> FactorialCondition:
        identifier = _require_trimmed(condition_id, "condition_id")
        for condition in self.conditions:
            if condition.condition_id == identifier:
                return condition
        raise KeyError(f"unknown factorial condition {identifier!r}")

    def budget_for(self, condition: FactorialCondition | str) -> Mapping[str, Any]:
        cell = self.condition(condition) if isinstance(condition, str) else condition
        if cell not in self.conditions:
            raise ValueError("condition is not a member of this factorial plan")
        return self.current_budget if cell.search is SearchArm.CURRENT else self.widened_budget

    def to_record(self) -> dict[str, Any]:
        task_set_hash = self.task_set_hash
        return {
            "schema": "komorebi.lasm_action.matched_factorial_plan",
            "schema_version": SCHEMA_VERSION,
            "design": "complete 2x2x2 factorial",
            "factors": {
                "representation": [arm.value for arm in RepresentationArm],
                "actions": [arm.value for arm in ActionArm],
                "search": [arm.value for arm in SearchArm],
            },
            "task_ids": list(self.task_ids),
            "task_count": len(self.task_ids),
            "task_set_hash": task_set_hash,
            "replicate_salts": list(self.replicate_salts),
            "metrics": list(self.metrics),
            "budgets": {
                SearchArm.CURRENT.value: canonical_value(self.current_budget),
                SearchArm.WIDENED.value: canonical_value(self.widened_budget),
            },
            "cells": [
                {
                    **condition.to_record(),
                    "task_set_hash": task_set_hash,
                    "replicate_salts": list(self.replicate_salts),
                    "budget": canonical_value(self.budget_for(condition)),
                }
                for condition in self.conditions
            ],
            "cohort_partition_id": self.cohort_partition_id,
            "matching_contract": {
                "same_tasks_in_every_cell": True,
                "same_replicate_salts_in_every_cell": True,
                "same_per_task_seed_in_every_cell": True,
                "deterministic_candidate_ordering_required": True,
                "configured_budget_reported_separately_from_actual_work": True,
            },
            "label_access": "training demonstrations only",
            "public_evaluation": "excluded until solver freeze",
            "plan_id": self.plan_id,
        }


def build_matched_factorial_plan(
    task_ids: Iterable[str],
    *,
    current_budget: Mapping[str, Any] | None = None,
    widened_budget: Mapping[str, Any] | None = None,
    replicate_salts: Iterable[str] = ("block10-factorial-r0",),
    metrics: Iterable[str] = DEFAULT_FACTORIAL_METRICS,
    cohort_partition_id: str = "",
) -> FactorialPlan:
    tasks = _task_ids(task_ids)
    current = _normalized_budget(
        DEFAULT_CURRENT_SEARCH_BUDGET if current_budget is None else current_budget,
        "current_budget",
    )
    widened = _normalized_budget(
        DEFAULT_WIDENED_SEARCH_BUDGET if widened_budget is None else widened_budget,
        "widened_budget",
    )
    _validate_widened_budget(current, widened)
    salts = tuple(sorted(_strings(replicate_salts, "replicate_salts")))
    metric_names = _strings(metrics, "metrics")
    partition_id = _require_trimmed(
        cohort_partition_id, "cohort_partition_id", allow_empty=True
    )
    conditions = factorial_conditions()
    identity = {
        "schema": "komorebi.lasm_action.matched_factorial_plan_identity",
        "schema_version": SCHEMA_VERSION,
        "task_ids": tasks,
        "conditions": [condition.to_record() for condition in conditions],
        "current_budget": current,
        "widened_budget": widened,
        "replicate_salts": salts,
        "metrics": metric_names,
        "cohort_partition_id": partition_id,
    }
    return FactorialPlan(
        task_ids=tasks,
        conditions=conditions,
        current_budget=MappingProxyType(current),
        widened_budget=MappingProxyType(widened),
        replicate_salts=salts,
        metrics=metric_names,
        cohort_partition_id=partition_id,
        plan_id=sha256_record(identity),
    )


def matched_task_seed(
    plan: FactorialPlan,
    task_id: str,
    replicate_salt: str,
) -> int:
    """Return the same unsigned 64-bit task seed for every factorial cell."""

    if not isinstance(plan, FactorialPlan):
        raise TypeError("plan must be a FactorialPlan")
    identifier = _require_trimmed(task_id, "task_id")
    if identifier not in plan.task_ids:
        raise ValueError("task_id is not a member of the factorial plan")
    salt = _require_trimmed(replicate_salt, "replicate_salt")
    if salt not in plan.replicate_salts:
        raise ValueError("replicate_salt is not declared by the factorial plan")
    digest = sha256_record(
        {
            "schema": "komorebi.lasm_action.matched_task_seed",
            "schema_version": SCHEMA_VERSION,
            "task_set_hash": plan.task_set_hash,
            "task_id": identifier,
            "replicate_salt": salt,
        }
    )
    return int(digest[:16], 16)


def _finalize_cell_record(record: dict[str, Any]) -> dict[str, Any]:
    record["content_hash"] = sha256_record(record)
    return record


def build_factorial_cell_record(
    plan: FactorialPlan,
    condition: FactorialCondition | str,
    *,
    replicate_salt: str,
    training_metrics: Mapping[str, Any],
    actual_work: Mapping[str, Any],
    run_source_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Record one training-only cell execution after it has completed."""

    if not isinstance(plan, FactorialPlan):
        raise TypeError("plan must be a FactorialPlan")
    cell = plan.condition(condition) if isinstance(condition, str) else condition
    if cell not in plan.conditions:
        raise ValueError("condition is not a member of this factorial plan")
    salt = _require_trimmed(replicate_salt, "replicate_salt")
    if salt not in plan.replicate_salts:
        raise ValueError("replicate_salt is not declared by the factorial plan")
    if not isinstance(training_metrics, Mapping):
        raise TypeError("training_metrics must be a mapping")
    if not isinstance(actual_work, Mapping):
        raise TypeError("actual_work must be a mapping")
    _assert_no_evaluation_fields(training_metrics, path="$.training_metrics")
    _assert_no_evaluation_fields(actual_work, path="$.actual_work")
    sources: dict[str, str] = {}
    for name, digest in sorted((run_source_hashes or {}).items()):
        _require_trimmed(name, "run source name")
        _assert_no_evaluation_fields({name: None}, path="$.run_source_hashes")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise ValueError(f"run source {name!r} must have a lowercase SHA-256 digest")
        sources[name] = digest
    return _finalize_cell_record(
        {
            "schema": "komorebi.lasm_action.factorial_cell_run",
            "schema_version": SCHEMA_VERSION,
            "plan_id": plan.plan_id,
            "condition": cell.to_record(),
            "replicate_salt": salt,
            "task_set_hash": plan.task_set_hash,
            "task_count": len(plan.task_ids),
            "configured_budget": canonical_value(plan.budget_for(cell)),
            "training_metrics": canonical_value(training_metrics),
            "actual_work": canonical_value(actual_work),
            "run_source_hashes": sources,
            "label_access": "training demonstrations only",
            "public_evaluation": "not performed",
        }
    )


def _cell_record_key(record: Mapping[str, Any]) -> tuple[str, str] | None:
    condition = record.get("condition")
    if not isinstance(condition, Mapping):
        return None
    condition_id = condition.get("condition_id")
    salt = record.get("replicate_salt")
    if not isinstance(condition_id, str) or not isinstance(salt, str):
        return None
    return condition_id, salt


def build_factorial_validation_record(
    plan: FactorialPlan,
    cell_records: Sequence[Mapping[str, Any]],
    *,
    source_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Validate matrix completeness and matching without inspecting labels."""

    if not isinstance(plan, FactorialPlan):
        raise TypeError("plan must be a FactorialPlan")
    if isinstance(cell_records, (str, bytes, bytearray, Mapping)):
        raise TypeError("cell_records must be a finite sequence")
    records = tuple(cell_records)
    expected = {
        (condition.condition_id, salt)
        for condition in plan.conditions
        for salt in plan.replicate_salts
    }
    keys: list[tuple[str, str] | None] = []
    hashes: list[str] = []
    valid_embedded_hashes = True
    plan_ids_match = True
    tasks_match = True
    labels_hidden = True
    budgets_match = True
    condition_contracts_match = True
    schemas_valid = True
    training_payloads_present = True
    for record in records:
        if not isinstance(record, Mapping):
            raise TypeError("each factorial cell record must be a mapping")
        schemas_valid &= (
            record.get("schema") == "komorebi.lasm_action.factorial_cell_run"
            and record.get("schema_version") == SCHEMA_VERSION
        )
        training_payloads_present &= (
            isinstance(record.get("training_metrics"), Mapping)
            and isinstance(record.get("actual_work"), Mapping)
        )
        key = _cell_record_key(record)
        keys.append(key)
        content_hash = record.get("content_hash")
        if not isinstance(content_hash, str):
            valid_embedded_hashes = False
            hashes.append(sha256_record(record))
        else:
            payload = {name: value for name, value in record.items() if name != "content_hash"}
            valid_embedded_hashes &= content_hash == sha256_record(payload)
            hashes.append(content_hash)
        plan_ids_match &= record.get("plan_id") == plan.plan_id
        tasks_match &= (
            record.get("task_set_hash") == plan.task_set_hash
            and record.get("task_count") == len(plan.task_ids)
        )
        labels_hidden &= (
            record.get("label_access") == "training demonstrations only"
            and record.get("public_evaluation") == "not performed"
        )
        try:
            _assert_no_evaluation_fields(
                record.get("training_metrics", {}), path="$.training_metrics"
            )
            _assert_no_evaluation_fields(record.get("actual_work", {}), path="$.actual_work")
            _assert_no_evaluation_fields(
                record.get("run_source_hashes", {}), path="$.run_source_hashes"
            )
        except (TypeError, ValueError):
            labels_hidden = False
        if key is None:
            budgets_match = False
            condition_contracts_match = False
        else:
            try:
                declared_condition = plan.condition(key[0])
                expected_budget = canonical_value(plan.budget_for(declared_condition))
            except (KeyError, TypeError, ValueError):
                budgets_match = False
                condition_contracts_match = False
            else:
                budgets_match &= record.get("configured_budget") == expected_budget
                condition_contracts_match &= (
                    record.get("condition") == declared_condition.to_record()
                )
    observed_keys = {key for key in keys if key is not None}
    gates = {
        "complete_2x2x2_matrix": observed_keys == expected,
        "one_record_per_cell_and_replicate": len(keys) == len(set(keys)) == len(expected),
        "embedded_record_hashes_valid": valid_embedded_hashes,
        "cell_schemas_valid": schemas_valid,
        "training_payloads_present": training_payloads_present,
        "factorial_plan_ids_match": plan_ids_match,
        "matched_task_sets": tasks_match,
        "condition_contracts_match": condition_contracts_match,
        "declared_budgets_match": budgets_match,
        "public_labels_unavailable": labels_hidden,
    }
    return deterministic_validation_record(
        schema="komorebi.lasm_action.factorial_validation",
        payload={
            "plan": plan.to_record(),
            "cell_record_hashes": sorted(hashes),
            "expected_cell_replicates": [list(item) for item in sorted(expected)],
            "observed_cell_replicates": [
                list(item) for item in sorted(observed_keys)
            ],
        },
        gates=gates,
        source_hashes=source_hashes,
        claim_boundary=NO_PUBLIC_EVALUATION_CLAIM,
    )


@dataclass(frozen=True, slots=True)
class PrequentialStep:
    position: int
    task_id: str
    prior_task_ids: tuple[str, ...]
    order_hash: str

    @property
    def eligible(self) -> bool:
        return bool(self.prior_task_ids)

    def to_record(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "task_id": self.task_id,
            "prior_task_ids": list(self.prior_task_ids),
            "prior_count": len(self.prior_task_ids),
            "order_hash": self.order_hash,
            "protocol": "freeze prior evidence, predict current, reveal current afterward",
        }


def deterministic_prequential_order(
    task_ids: Iterable[str],
    *,
    salt: str = "block10-prequential-v1:",
) -> tuple[str, ...]:
    tasks = _task_ids(task_ids)
    prefix = _require_trimmed(salt, "salt")
    return tuple(
        sorted(
            tasks,
            key=lambda task_id: (
                hashlib.sha256((prefix + task_id).encode("utf-8")).hexdigest(),
                task_id,
            ),
        )
    )


def build_prequential_steps(
    task_ids: Iterable[str],
    *,
    salt: str = "block10-prequential-v1:",
) -> tuple[PrequentialStep, ...]:
    """Build freeze-before-current steps; no task is included in its own history."""

    order = deterministic_prequential_order(task_ids, salt=salt)
    order_hash = sha256_record({"salt": salt, "order": order})
    return tuple(
        PrequentialStep(
            position=index + 1,
            task_id=task_id,
            prior_task_ids=order[:index],
            order_hash=order_hash,
        )
        for index, task_id in enumerate(order)
    )


def prequential_schedule_record(
    task_ids: Iterable[str],
    *,
    salt: str = "block10-prequential-v1:",
) -> dict[str, Any]:
    steps = build_prequential_steps(task_ids, salt=salt)
    record = {
        "schema": "komorebi.lasm_action.prequential_schedule",
        "schema_version": SCHEMA_VERSION,
        "salt": salt,
        "order_hash": steps[0].order_hash,
        "task_count": len(steps),
        "label_protocol": "current public label remains unavailable until after prediction",
        "steps": [step.to_record() for step in steps],
    }
    record["content_hash"] = sha256_record(record)
    return record


@dataclass(frozen=True, slots=True)
class GaugeFold:
    fold_index: int
    train_task_ids: tuple[str, ...]
    test_task_ids: tuple[str, ...]
    test_gauge_group_ids: tuple[str, ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "fold_index": self.fold_index,
            "train_task_ids": list(self.train_task_ids),
            "test_task_ids": list(self.test_task_ids),
            "test_gauge_group_ids": list(self.test_gauge_group_ids),
        }


@dataclass(frozen=True, slots=True)
class GaugeGroupedFoldPlan:
    folds: tuple[GaugeFold, ...]
    task_to_group: Mapping[str, str]
    groups: Mapping[str, tuple[str, ...]]
    descriptor_scope: str
    salt: str
    plan_id: str

    @property
    def task_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.task_to_group))

    @property
    def fold_count(self) -> int:
        return len(self.folds)

    @property
    def assignment(self) -> Mapping[str, int]:
        return MappingProxyType(
            {
                task_id: fold.fold_index
                for fold in self.folds
                for task_id in fold.test_task_ids
            }
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.gauge_grouped_fold_plan",
            "schema_version": SCHEMA_VERSION,
            "fold_count": self.fold_count,
            "task_count": len(self.task_ids),
            "task_set_hash": sha256_record(self.task_ids),
            "descriptor_scope": self.descriptor_scope,
            "salt": self.salt,
            "task_to_group": dict(self.task_to_group),
            "groups": {
                group_id: list(self.groups[group_id]) for group_id in sorted(self.groups)
            },
            "folds": [fold.to_record() for fold in self.folds],
            "group_isolation_verified": validate_gauge_group_isolation(self),
            "plan_id": self.plan_id,
        }


def _gauge_group_id(descriptor: Any) -> str:
    return sha256_record(
        {
            "schema": "komorebi.lasm_action.gauge_group_descriptor",
            "schema_version": SCHEMA_VERSION,
            "descriptor": canonical_value(descriptor),
        }
    )


def build_gauge_grouped_fold_plan(
    task_to_gauge_descriptor: Mapping[str, Any],
    *,
    fold_count: int = 5,
    salt: str = "block10-gauge-fold-v1:",
    descriptor_scope: str = GAUGE_DESCRIPTOR_SCOPE,
) -> GaugeGroupedFoldPlan:
    """Assign whole gauge-equivalence groups to deterministic balanced folds."""

    if not isinstance(task_to_gauge_descriptor, Mapping) or not task_to_gauge_descriptor:
        raise ValueError("task_to_gauge_descriptor must be a nonempty mapping")
    folds_requested = _positive_int(fold_count, "fold_count")
    if folds_requested < 2:
        raise ValueError("fold_count must be at least two")
    prefix = _require_trimmed(salt, "salt")
    scope = _require_trimmed(descriptor_scope, "descriptor_scope")

    normalized_task_keys = tuple(
        sorted(
            _require_trimmed(task_id, "task_id")
            for task_id in task_to_gauge_descriptor
        )
    )
    task_to_group: dict[str, str] = {}
    grouped: dict[str, list[str]] = {}
    for task_id in normalized_task_keys:
        group_id = _gauge_group_id(task_to_gauge_descriptor[task_id])
        task_to_group[task_id] = group_id
        grouped.setdefault(group_id, []).append(task_id)
    if len(grouped) < folds_requested:
        raise ValueError("fold_count cannot exceed the number of gauge groups")

    group_order = sorted(
        grouped,
        key=lambda group_id: (
            -len(grouped[group_id]),
            hashlib.sha256((prefix + group_id).encode("utf-8")).hexdigest(),
            group_id,
        ),
    )
    fold_groups: list[list[str]] = [[] for _ in range(folds_requested)]
    fold_tasks: list[list[str]] = [[] for _ in range(folds_requested)]
    for group_id in group_order:
        index = min(
            range(folds_requested),
            key=lambda candidate: (
                len(fold_tasks[candidate]),
                len(fold_groups[candidate]),
                candidate,
            ),
        )
        fold_groups[index].append(group_id)
        fold_tasks[index].extend(grouped[group_id])

    all_tasks = tuple(sorted(task_to_group))
    fold_records = tuple(
        GaugeFold(
            fold_index=index,
            train_task_ids=tuple(sorted(set(all_tasks) - set(fold_tasks[index]))),
            test_task_ids=tuple(sorted(fold_tasks[index])),
            test_gauge_group_ids=tuple(sorted(fold_groups[index])),
        )
        for index in range(folds_requested)
    )
    normalized_groups = {
        group_id: tuple(sorted(task_ids)) for group_id, task_ids in grouped.items()
    }
    identity = {
        "schema": "komorebi.lasm_action.gauge_grouped_fold_plan_identity",
        "schema_version": SCHEMA_VERSION,
        "folds": [fold.to_record() for fold in fold_records],
        "task_to_group": task_to_group,
        "groups": normalized_groups,
        "descriptor_scope": scope,
        "salt": prefix,
    }
    plan = GaugeGroupedFoldPlan(
        folds=fold_records,
        task_to_group=MappingProxyType(task_to_group),
        groups=MappingProxyType(normalized_groups),
        descriptor_scope=scope,
        salt=prefix,
        plan_id=sha256_record(identity),
    )
    validate_gauge_group_isolation(plan)
    return plan


def validate_gauge_group_isolation(plan: GaugeGroupedFoldPlan) -> bool:
    """Verify exhaustive task assignment and that no gauge group crosses folds."""

    if not isinstance(plan, GaugeGroupedFoldPlan):
        raise TypeError("plan must be a GaugeGroupedFoldPlan")
    all_tasks = set(plan.task_to_group)
    seen: set[str] = set()
    group_fold: dict[str, int] = {}
    indices = tuple(fold.fold_index for fold in plan.folds)
    if indices != tuple(range(len(plan.folds))):
        raise ValueError("gauge fold indices must be contiguous in canonical order")
    for fold in plan.folds:
        train = set(fold.train_task_ids)
        test = set(fold.test_task_ids)
        if train.intersection(test):
            raise ValueError("gauge fold train and test sets overlap")
        if train.union(test) != all_tasks:
            raise ValueError("gauge fold does not cover the complete task set")
        if seen.intersection(test):
            raise ValueError("a task is assigned to more than one test fold")
        seen.update(test)
        declared_groups = set(fold.test_gauge_group_ids)
        observed_groups = {plan.task_to_group[task_id] for task_id in test}
        if declared_groups != observed_groups:
            raise ValueError("gauge fold group declaration does not match its tasks")
        for group_id in observed_groups:
            previous = group_fold.setdefault(group_id, fold.fold_index)
            if previous != fold.fold_index:
                raise ValueError("a gauge group is split across test folds")
            if set(plan.groups[group_id]) - test:
                raise ValueError("only part of a gauge group appears in a test fold")
    if seen != all_tasks:
        raise ValueError("gauge folds do not assign every task exactly once")
    return True


def gauge_grouped_folds(
    task_to_gauge_descriptor: Mapping[str, Any],
    *,
    fold_count: int = 5,
    salt: str = "block10-gauge-fold-v1:",
    descriptor_scope: str = GAUGE_DESCRIPTOR_SCOPE,
) -> tuple[GaugeFold, ...]:
    return build_gauge_grouped_fold_plan(
        task_to_gauge_descriptor,
        fold_count=fold_count,
        salt=salt,
        descriptor_scope=descriptor_scope,
    ).folds


def gauge_grouped_fold_assignment(
    task_to_gauge_descriptor: Mapping[str, Any],
    *,
    fold_count: int = 5,
    salt: str = "block10-gauge-fold-v1:",
    descriptor_scope: str = GAUGE_DESCRIPTOR_SCOPE,
) -> dict[str, int]:
    plan = build_gauge_grouped_fold_plan(
        task_to_gauge_descriptor,
        fold_count=fold_count,
        salt=salt,
        descriptor_scope=descriptor_scope,
    )
    return dict(plan.assignment)


# Short aliases for audit scripts.
matched_factorial_schema = build_matched_factorial_plan
prequential_order = deterministic_prequential_order
prequential_steps = build_prequential_steps
factorial_validation_record = build_factorial_validation_record


__all__ = [
    "ActionArm",
    "DEFAULT_CURRENT_SEARCH_BUDGET",
    "DEFAULT_FACTORIAL_METRICS",
    "DEFAULT_WIDENED_SEARCH_BUDGET",
    "FactorialCondition",
    "FactorialPlan",
    "GAUGE_DESCRIPTOR_SCOPE",
    "GaugeFold",
    "GaugeGroupedFoldPlan",
    "PrequentialStep",
    "RepresentationArm",
    "SearchArm",
    "build_factorial_cell_record",
    "build_factorial_validation_record",
    "build_gauge_grouped_fold_plan",
    "build_matched_factorial_plan",
    "build_prequential_steps",
    "deterministic_prequential_order",
    "factorial_conditions",
    "factorial_validation_record",
    "gauge_grouped_fold_assignment",
    "gauge_grouped_folds",
    "matched_factorial_schema",
    "matched_task_seed",
    "prequential_order",
    "prequential_schedule_record",
    "prequential_steps",
    "validate_gauge_group_isolation",
    "verify_deterministic_validation_record",
]

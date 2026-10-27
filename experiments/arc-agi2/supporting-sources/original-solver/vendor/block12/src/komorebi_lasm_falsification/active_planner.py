"""Target-blind finite action planner with sealed counterfactual partitions.

The planner receives only an explicitly supplied version space, the action
recommended by each version, and the observation each version predicts for
each legal probe.  It has no environment or hidden-target argument.  A caller
must seal the returned plan before executing the chosen probe, then use the
observed capsule to falsify inconsistent versions.

Author: Komorebi P.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence


PLANNER_SCHEMA_VERSION = 1


def canonical_json(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )


def content_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _entropy(counts: Sequence[int]) -> float:
    total = sum(counts)
    if total <= 1:
        return 0.0
    return -sum(
        (count / total) * math.log2(count / total)
        for count in counts if count
    )


def _goal_entropy(
    version_ids: Sequence[str], goal_by_version: Mapping[str, str]
) -> float:
    counts: dict[str, int] = {}
    for version_id in version_ids:
        goal = goal_by_version[version_id]
        counts[goal] = counts.get(goal, 0) + 1
    return _entropy(tuple(counts.values()))


def _require_ids(version_ids: Sequence[str]) -> tuple[str, ...]:
    frozen = tuple(sorted(version_ids))
    if not frozen:
        raise ValueError("version space cannot be empty")
    if len(frozen) != len(set(frozen)):
        raise ValueError("version IDs must be unique")
    if not all(isinstance(item, str) and item for item in frozen):
        raise TypeError("version IDs must be non-empty strings")
    return frozen


@dataclass(frozen=True, slots=True)
class ProbeEvaluation:
    action: str
    partitions: tuple[tuple[str, tuple[str, ...]], ...]
    goal_information_gain: float
    version_information_gain: float
    worst_partition: int

    def __post_init__(self) -> None:
        if not isinstance(self.action, str) or not self.action:
            raise ValueError("probe action must be non-empty")
        object.__setattr__(self, "partitions", tuple(
            (key, tuple(values)) for key, values in self.partitions
        ))
        if not self.partitions:
            raise ValueError("probe evaluation needs a finite partition")
        flattened = [item for _, values in self.partitions for item in values]
        if len(flattened) != len(set(flattened)):
            raise ValueError("partition cells must be disjoint")
        if self.worst_partition != max(len(values) for _, values in self.partitions):
            raise ValueError("worst-partition metric mismatch")

    @property
    def partition_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.partitions)

    def summary_record(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "goal_information_gain": self.goal_information_gain,
            "version_information_gain": self.version_information_gain,
            "worst_partition": self.worst_partition,
            "partition_count": len(self.partitions),
        }

    def to_record(self) -> dict[str, Any]:
        return {
            **self.summary_record(),
            "partitions": {
                key: list(values) for key, values in self.partitions
            },
        }


@dataclass(frozen=True, slots=True)
class ActiveProbePlan:
    policy: str
    version_ids: tuple[str, ...]
    chosen: ProbeEvaluation
    evaluated: tuple[ProbeEvaluation, ...]

    def __post_init__(self) -> None:
        if self.policy not in {"active", "fixed"}:
            raise ValueError("policy must be active or fixed")
        object.__setattr__(self, "version_ids", _require_ids(self.version_ids))
        object.__setattr__(self, "evaluated", tuple(self.evaluated))
        if not self.evaluated or self.chosen not in self.evaluated:
            raise ValueError("chosen probe must belong to the evaluated set")
        expected = set(self.version_ids)
        for proposal in self.evaluated:
            observed = {
                version_id
                for values in proposal.partition_map.values()
                for version_id in values
            }
            if observed != expected:
                raise ValueError("each probe must partition the complete version space")

    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.block12.active_probe_plan",
            "schema_version": PLANNER_SCHEMA_VERSION,
            "target_blind": True,
            "sealed_before_observation": True,
            "policy": self.policy,
            "version_ids": list(self.version_ids),
            "version_space_hash": content_hash(self.version_ids),
            "chosen_action": self.chosen.action,
            "chosen_partition": self.chosen.to_record(),
            "evaluated_probes": [
                proposal.summary_record()
                for proposal in sorted(self.evaluated, key=lambda item: item.action)
            ],
        }

    @property
    def plan_hash(self) -> str:
        return content_hash(self.semantic_record())

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record(), "plan_hash": self.plan_hash}


def _evaluate_probe(
    action: str,
    version_ids: tuple[str, ...],
    goal_by_version: Mapping[str, str],
    predictions: Mapping[str, object],
) -> ProbeEvaluation:
    if set(predictions) != set(version_ids):
        raise ValueError(f"probe {action!r} predictions do not cover the version space")
    cells: dict[str, list[str]] = {}
    for version_id in version_ids:
        capsule_key = canonical_json(predictions[version_id])
        cells.setdefault(capsule_key, []).append(version_id)
    partitions = tuple(
        (key, tuple(sorted(values))) for key, values in sorted(cells.items())
    )
    total = len(version_ids)
    prior_version_entropy = math.log2(total)
    posterior_version_entropy = sum(
        (len(values) / total) * math.log2(len(values))
        for _, values in partitions
    )
    prior_goal_entropy = _goal_entropy(version_ids, goal_by_version)
    posterior_goal_entropy = sum(
        (len(values) / total) * _goal_entropy(values, goal_by_version)
        for _, values in partitions
    )
    return ProbeEvaluation(
        action=action,
        partitions=partitions,
        goal_information_gain=round(prior_goal_entropy - posterior_goal_entropy, 12),
        version_information_gain=round(
            prior_version_entropy - posterior_version_entropy, 12
        ),
        worst_partition=max(len(values) for _, values in partitions),
    )


def plan_probe(
    *,
    version_ids: Sequence[str],
    goal_by_version: Mapping[str, str],
    predictions_by_action: Mapping[str, Mapping[str, object]],
    policy: str = "active",
    fixed_order: Sequence[str] = (),
) -> ActiveProbePlan:
    """Choose and seal one probe without access to a hidden target.

    Active selection lexicographically maximizes action-congruent information
    gain, then full version information gain, then minimizes worst-case cell
    size.  The fixed control takes the first available action in ``fixed_order``.
    """

    frozen_ids = _require_ids(version_ids)
    if policy not in {"active", "fixed"}:
        raise ValueError("policy must be active or fixed")
    if set(goal_by_version) != set(frozen_ids):
        raise ValueError("goal map must exactly cover the version space")
    if not predictions_by_action:
        raise ValueError("at least one legal probe is required")
    evaluations = tuple(
        _evaluate_probe(action, frozen_ids, goal_by_version, predictions)
        for action, predictions in sorted(predictions_by_action.items())
    )
    if policy == "active":
        chosen = sorted(
            evaluations,
            key=lambda item: (
                -item.goal_information_gain,
                -item.version_information_gain,
                item.worst_partition,
                item.action,
            ),
        )[0]
    else:
        available = {item.action: item for item in evaluations}
        selected = next((item for item in fixed_order if item in available), None)
        if selected is None:
            selected = min(available)
        chosen = available[selected]
    return ActiveProbePlan(policy, frozen_ids, chosen, evaluations)


def falsify_versions(plan: ActiveProbePlan, observed_capsule: object) -> tuple[str, ...]:
    """Return precisely the versions consistent with one observed capsule."""

    if not isinstance(plan, ActiveProbePlan):
        raise TypeError("plan must be an ActiveProbePlan")
    return plan.chosen.partition_map.get(canonical_json(observed_capsule), ())


def unanimous_action(
    version_ids: Sequence[str], goal_by_version: Mapping[str, str]
) -> str | None:
    """Return a safe commit action only under complete version-space agreement."""

    frozen = _require_ids(version_ids)
    if not set(frozen) <= set(goal_by_version):
        raise ValueError("goal map does not cover the supplied versions")
    goals = {goal_by_version[version_id] for version_id in frozen}
    return next(iter(goals)) if len(goals) == 1 else None


def audit_plan(plan: ActiveProbePlan) -> dict[str, Any]:
    record = plan.to_record()
    chosen = plan.chosen
    return {
        "plan_hash_verified": record["plan_hash"] == content_hash(plan.semantic_record()),
        "target_blind": record["target_blind"] is True,
        "sealed_before_observation": record["sealed_before_observation"] is True,
        "complete_partition": set(plan.version_ids) == {
            version_id
            for cell in chosen.partition_map.values()
            for version_id in cell
        },
        "partition_cells_disjoint": len(plan.version_ids) == sum(
            len(cell) for cell in chosen.partition_map.values()
        ),
    }


__all__ = [
    "ActiveProbePlan",
    "ProbeEvaluation",
    "audit_plan",
    "falsify_versions",
    "plan_probe",
    "unanimous_action",
]

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

from .certificate import Certificate, validate_certificate
from .model import ProofField, ValueVector


@dataclass(frozen=True, slots=True)
class TaskRequirement:
    id: str
    required_nodes: frozenset[str] = frozenset()
    required_metadata: frozenset[str] = frozenset()
    probability: float = 1.0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("task id must be nonempty")
        if not np.isfinite(float(self.probability)) or not 0.0 <= self.probability <= 1.0:
            raise ValueError("task probability must be finite and lie in [0, 1]")
        if any(not str(node_id).strip() for node_id in self.required_nodes):
            raise ValueError("required node identifiers must be nonempty")
        if any(not str(key).strip() for key in self.required_metadata):
            raise ValueError("required metadata identifiers must be nonempty")


@dataclass(frozen=True, slots=True)
class Representation:
    name: str
    retained_nodes: frozenset[str]
    retained_metadata: frozenset[str] = frozenset()
    certificate: Certificate | None = None
    profile: "RepresentationProfile | None" = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("representation name must be nonempty")
        if self.certificate is not None and not self.certificate.node_ids.issubset(
            self.retained_nodes
        ):
            raise ValueError("certificate nodes must be retained by the representation")


@dataclass(frozen=True, slots=True)
class CompressionReport:
    verification_complete: bool
    retained_nodes: frozenset[str]
    omitted_nodes: frozenset[str]
    retained_values: ValueVector
    loss_values: ValueVector
    normalized_loss: Mapping[str, float]
    expected_recovery_debt: float
    sufficient_tasks: frozenset[str]
    insufficient_tasks: frozenset[str]


@dataclass(frozen=True, slots=True)
class RepresentationProfile:
    name: str
    verification: float
    discovery: float
    meaning: float
    auditability: float
    bridge: float
    noise: float
    cost: float

    def __post_init__(self) -> None:
        for field_name in (
            "verification",
            "discovery",
            "meaning",
            "auditability",
            "bridge",
            "noise",
            "cost",
        ):
            value = float(getattr(self, field_name))
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{field_name} must be finite and nonnegative")


@dataclass(frozen=True, slots=True)
class GoalWeights:
    verification: float = 0.0
    discovery: float = 0.0
    meaning: float = 0.0
    auditability: float = 0.0
    bridge: float = 0.0
    noise: float = 0.0
    cost: float = 0.0

    def __post_init__(self) -> None:
        for field_name in (
            "verification",
            "discovery",
            "meaning",
            "auditability",
            "bridge",
            "noise",
            "cost",
        ):
            value = float(getattr(self, field_name))
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{field_name} weight must be finite and nonnegative")


def _validated_task_distribution(
    tasks: Iterable[TaskRequirement],
) -> tuple[TaskRequirement, ...]:
    task_tuple = tuple(tasks)
    identifiers = [task.id for task in task_tuple]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("task identifiers must be unique")
    if task_tuple:
        total = float(sum(task.probability for task in task_tuple))
        if not np.isclose(total, 1.0, rtol=0.0, atol=1e-12):
            raise ValueError("task probabilities must sum to 1")
    return task_tuple


def _validated_recovery_cost(
    recovery_cost: Mapping[str, float],
) -> dict[str, float]:
    validated: dict[str, float] = {}
    for node_id, value in recovery_cost.items():
        numeric = float(value)
        if not np.isfinite(numeric) or numeric < 0:
            raise ValueError("recovery costs must be finite and nonnegative")
        validated[str(node_id)] = numeric
    return validated


def retention_projection(
    node_ids: Iterable[str],
    mask: Iterable[str],
) -> frozenset[str]:
    """Apply a pure retention mask to a finite node set."""
    return frozenset(node_ids).intersection(mask)


def retention_meet(*masks: Iterable[str]) -> frozenset[str]:
    """Return the meet of retention masks, with intersection as composition."""
    if not masks:
        raise ValueError("at least one retention mask is required")
    result = frozenset(masks[0])
    for mask in masks[1:]:
        result = result.intersection(mask)
    return result


def retention_join(*masks: Iterable[str]) -> frozenset[str]:
    """Return the join of retention masks."""
    result: set[str] = set()
    for mask in masks:
        result.update(mask)
    return frozenset(result)


def task_sufficient(representation: Representation, task: TaskRequirement) -> bool:
    return (
        task.required_nodes.issubset(representation.retained_nodes)
        and task.required_metadata.issubset(representation.retained_metadata)
    )


def task_signature(
    representation: Representation,
    tasks: Iterable[TaskRequirement],
) -> frozenset[str]:
    return frozenset(task.id for task in tasks if task_sufficient(representation, task))


def recoverability_preorder(
    less_rich: Representation,
    more_rich: Representation,
    tasks: Iterable[TaskRequirement],
) -> bool:
    """Return True when every declared task supported by less_rich is supported by more_rich."""
    task_tuple = tuple(tasks)
    return task_signature(less_rich, task_tuple).issubset(
        task_signature(more_rich, task_tuple)
    )


def recoverability_equivalent(
    left: Representation,
    right: Representation,
    tasks: Iterable[TaskRequirement],
) -> bool:
    task_tuple = tuple(tasks)
    return recoverability_preorder(left, right, task_tuple) and recoverability_preorder(
        right, left, task_tuple
    )


def compression_report(
    field: ProofField,
    representation: Representation,
    *,
    tasks: Sequence[TaskRequirement] = (),
    recovery_cost: Mapping[str, float] | None = None,
) -> CompressionReport:
    unknown = representation.retained_nodes.difference(field.nodes)
    if unknown:
        raise KeyError(sorted(unknown)[0])
    certificate_valid = False
    if representation.certificate is not None:
        certificate_valid = validate_certificate(field, representation.certificate).valid
    retained_values = field.total_values(representation.retained_nodes)
    total_values = field.total_values()
    loss_values = total_values - retained_values
    total_dict = total_values.as_dict()
    loss_dict = loss_values.as_dict()
    normalized = {
        name: (loss_dict[name] / total_dict[name] if total_dict[name] > 0 else 0.0)
        for name in total_dict
    }
    task_tuple = _validated_task_distribution(tasks)
    unknown_task_nodes = set().union(
        *(task.required_nodes for task in task_tuple)
    ).difference(field.nodes) if task_tuple else set()
    if unknown_task_nodes:
        raise KeyError(sorted(unknown_task_nodes)[0])
    if recovery_cost is None:
        recovery_cost = {
            node_id: field.nodes[node_id].costs.recovery for node_id in field.nodes
        }
    validated_recovery_cost = _validated_recovery_cost(recovery_cost)
    sufficient = task_signature(representation, task_tuple)
    task_ids = frozenset(task.id for task in task_tuple)
    debt = 0.0
    for task in task_tuple:
        missing = task.required_nodes.difference(representation.retained_nodes)
        debt += task.probability * sum(
            validated_recovery_cost.get(node_id, 0.0) for node_id in missing
        )
    return CompressionReport(
        verification_complete=certificate_valid,
        retained_nodes=representation.retained_nodes,
        omitted_nodes=frozenset(field.nodes).difference(representation.retained_nodes),
        retained_values=retained_values,
        loss_values=loss_values,
        normalized_loss=normalized,
        expected_recovery_debt=float(debt),
        sufficient_tasks=sufficient,
        insufficient_tasks=task_ids.difference(sufficient),
    )


def compression_debt(
    retained_nodes: Iterable[str],
    tasks: Iterable[TaskRequirement],
    recovery_cost: Mapping[str, float],
) -> float:
    retained = frozenset(retained_nodes)
    task_tuple = _validated_task_distribution(tasks)
    validated_recovery_cost = _validated_recovery_cost(recovery_cost)
    debt = 0.0
    for task in task_tuple:
        debt += task.probability * sum(
            validated_recovery_cost.get(node_id, 0.0)
            for node_id in task.required_nodes.difference(retained)
        )
    return float(debt)


def representation_utility(
    profile: RepresentationProfile,
    weights: GoalWeights,
) -> float:
    return float(
        weights.verification * profile.verification
        + weights.discovery * profile.discovery
        + weights.meaning * profile.meaning
        + weights.auditability * profile.auditability
        + weights.bridge * profile.bridge
        - weights.noise * profile.noise
        - weights.cost * profile.cost
    )


def select_representation(
    profiles: Sequence[RepresentationProfile],
    weights: GoalWeights,
) -> RepresentationProfile:
    if not profiles:
        raise ValueError("at least one representation profile is required")
    return max(
        profiles,
        key=lambda profile: (representation_utility(profile, weights), profile.name),
    )


def pareto_front(
    profiles: Sequence[RepresentationProfile],
) -> tuple[RepresentationProfile, ...]:
    if not profiles:
        return ()
    values = np.array(
        [
            [
                profile.verification,
                profile.discovery,
                profile.meaning,
                profile.auditability,
                profile.bridge,
                -profile.noise,
                -profile.cost,
            ]
            for profile in profiles
        ],
        dtype=float,
    )
    keep = np.ones(len(profiles), dtype=bool)
    for index, row in enumerate(values):
        weakly_better = np.all(values >= row, axis=1)
        strictly_better = np.any(values > row, axis=1)
        if np.any(weakly_better & strictly_better):
            keep[index] = False
    return tuple(profile for profile, retained in zip(profiles, keep) if retained)

from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite
from fractions import Fraction
from typing import Iterable, Mapping

from .model import ProofField


class AlternativeJustificationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Certificate:
    node_ids: frozenset[str]
    justification_ids: frozenset[str]
    targets: frozenset[str]


@dataclass(frozen=True, slots=True)
class CertificateReport:
    valid: bool
    derived_nodes: frozenset[str]
    missing_targets: frozenset[str]
    missing_required_premises: frozenset[str]
    missing_node_references: frozenset[str]
    missing_justification_references: frozenset[str]
    uncertified_justifications: frozenset[str]
    unused_nodes: frozenset[str]


def validate_certificate(
    field: ProofField,
    certificate: Certificate,
    *,
    certified_only: bool = True,
    require_declared_premises: bool = True,
) -> CertificateReport:
    missing_nodes = certificate.node_ids.difference(field.nodes)
    missing_justifications = certificate.justification_ids.difference(
        field.justifications
    )
    uncertified = frozenset(
        justification_id
        for justification_id in certificate.justification_ids
        if justification_id in field.justifications
        and not field.justifications[justification_id].certified
    )
    if missing_nodes or missing_justifications:
        derived = frozenset()
    else:
        derived = field.derive(
            selected_nodes=certificate.node_ids,
            selected_justifications=certificate.justification_ids,
            certified_only=certified_only,
        )
    missing_targets = certificate.targets.difference(derived)
    missing_required_premises = (
        field.premises.difference(certificate.node_ids)
        if require_declared_premises
        else frozenset()
    )
    used_nodes = set(certificate.targets)
    for justification_id in certificate.justification_ids:
        if justification_id in field.justifications:
            justification = field.justifications[justification_id]
            used_nodes.add(justification.conclusion)
            used_nodes.update(justification.premises)
    used_nodes.update(field.premises if require_declared_premises else ())
    unused_nodes = certificate.node_ids.difference(used_nodes)
    valid = not (
        missing_nodes
        or missing_justifications
        or missing_targets
        or missing_required_premises
        or (certified_only and uncertified)
    )
    return CertificateReport(
        valid=valid,
        derived_nodes=derived,
        missing_targets=frozenset(missing_targets),
        missing_required_premises=frozenset(missing_required_premises),
        missing_node_references=frozenset(missing_nodes),
        missing_justification_references=frozenset(missing_justifications),
        uncertified_justifications=uncertified,
        unused_nodes=frozenset(unused_nodes),
    )


def is_and_dag(field: ProofField, targets: Iterable[str] | None = None) -> bool:
    """Check the relevant AND-DAG, stopping expansion at admitted leaves.

    A recorded derivation of a premise already admitted by the field is not
    needed to use that premise. Unrelated ancestors must not create artificial
    proof obligations for the requested target.
    """
    target_set = field.targets if targets is None else frozenset(targets)
    unknown = target_set.difference(field.nodes)
    if unknown:
        raise KeyError(sorted(unknown)[0])
    visited: set[str] = set()
    pending = list(target_set)
    while pending:
        node_id = pending.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        if field.is_admissible_leaf(node_id):
            continue
        incoming = field.incoming(node_id, certified_only=True)
        if len(incoming) != 1:
            return False
        pending.extend(incoming[0].premises)
    return True


def unique_and_dag_certificate(
    field: ProofField,
    targets: Iterable[str] | None = None,
) -> Certificate:
    target_set = field.targets if targets is None else frozenset(targets)
    if not target_set:
        raise ValueError("at least one target is required")
    if not is_and_dag(field, target_set):
        raise AlternativeJustificationError(
            "the relevant certified subfield is not an AND-DAG with one justification per derived node"
        )
    selected_nodes: set[str] = set(field.premises)
    selected_justifications: set[str] = set()
    stack = list(target_set)
    while stack:
        node_id = stack.pop()
        if node_id in selected_nodes:
            continue
        selected_nodes.add(node_id)
        if field.is_admissible_leaf(node_id):
            continue
        justification = field.incoming(node_id, certified_only=True)[0]
        selected_justifications.add(justification.id)
        stack.extend(justification.premises)
    certificate = Certificate(
        frozenset(selected_nodes),
        frozenset(selected_justifications),
        frozenset(target_set),
    )
    report = validate_certificate(field, certificate)
    if not report.valid:
        raise RuntimeError("internal error while constructing the AND-DAG certificate")
    return certificate


def certificate_cost(
    field: ProofField,
    certificate: Certificate,
    *,
    node_cost: Mapping[str, float] | None = None,
    justification_cost: Mapping[str, float] | None = None,
) -> float:
    unknown_nodes = certificate.node_ids.difference(field.nodes)
    unknown_justifications = certificate.justification_ids.difference(
        field.justifications
    )
    if unknown_nodes:
        raise KeyError(sorted(unknown_nodes)[0])
    if unknown_justifications:
        raise KeyError(sorted(unknown_justifications)[0])
    if node_cost is None:
        node_cost = {
            node_id: field.nodes[node_id].costs.storage
            for node_id in field.nodes
        }
    if justification_cost is None:
        justification_cost = {}
    values: list[float] = []
    for node_id in certificate.node_ids:
        value = float(node_cost.get(node_id, 0.0))
        if not isfinite(value) or value < 0:
            raise ValueError("node costs must be finite and nonnegative")
        values.append(value)
    for justification_id in certificate.justification_ids:
        value = float(justification_cost.get(justification_id, 0.0))
        if not isfinite(value) or value < 0:
            raise ValueError("justification costs must be finite and nonnegative")
        values.append(value)
    return float(fsum(values))


def minimum_certificate(
    field: ProofField,
    targets: Iterable[str] | None = None,
    *,
    node_cost: Mapping[str, float] | None = None,
    justification_cost: Mapping[str, float] | None = None,
    max_search_states: int = 250_000,
) -> Certificate:
    """Find an exact minimum-cost certificate by branch and bound.

    The search is exponential in the number of alternative derivations. It is
    intended for finite research examples and validation, not large proof
    assistant libraries. Selection compares exact rational values of the stored
    binary floating-point costs. Public cost summaries are still floats.
    """

    if max_search_states <= 0:
        raise ValueError("max_search_states must be positive")
    target_set = field.targets if targets is None else frozenset(targets)
    if not target_set:
        raise ValueError("at least one target is required")
    unknown = target_set.difference(field.nodes)
    if unknown:
        raise KeyError(sorted(unknown)[0])
    if node_cost is None:
        node_cost = {
            node_id: field.nodes[node_id].costs.storage
            for node_id in field.nodes
        }
    if justification_cost is None:
        justification_cost = {}
    for value in tuple(node_cost.values()) + tuple(justification_cost.values()):
        numeric = float(value)
        if not isfinite(numeric) or numeric < 0:
            raise ValueError("certificate costs must be finite and nonnegative")

    # Binary floats are rational numbers. Exact rational accumulation avoids
    # both tolerance-based pruning and loss of small costs beside a large one.
    # This does not recover a user's intended decimal before float conversion.
    exact_node_cost = {
        node_id: Fraction.from_float(float(node_cost.get(node_id, 0.0)))
        for node_id in field.nodes
    }
    exact_justification_cost = {
        item_id: Fraction.from_float(float(justification_cost.get(item_id, 0.0)))
        for item_id in field.justifications
    }
    best_cost: Fraction | None = None
    best: Certificate | None = None
    states = 0

    def current_cost(nodes: set[str], justifications: set[str]) -> Fraction:
        return sum(
            (exact_node_cost[node_id] for node_id in nodes), Fraction(0)
        ) + sum(
            (exact_justification_cost[item_id] for item_id in justifications),
            Fraction(0),
        )

    def first_missing_dependency(
        nodes: set[str],
        justifications: set[str],
    ) -> str | None:
        derived = field.derive(
            selected_nodes=nodes,
            selected_justifications=justifications,
            certified_only=True,
        )
        pending = [
            node_id
            for node_id in field.topological_order
            if node_id in nodes
            and node_id not in derived
            and not field.is_admissible_leaf(node_id)
        ]
        if pending:
            return pending[0]
        missing_targets = [node_id for node_id in target_set if node_id not in derived]
        return missing_targets[0] if missing_targets else None

    def search(nodes: set[str], justifications: set[str]) -> None:
        nonlocal best, best_cost, states
        states += 1
        if states > max_search_states:
            raise RuntimeError(
                "minimum-certificate search exceeded max_search_states"
            )
        cost = current_cost(nodes, justifications)
        if best_cost is not None and cost >= best_cost:
            return

        report = validate_certificate(
            field,
            Certificate(frozenset(nodes), frozenset(justifications), target_set),
        )
        if report.valid:
            best = Certificate(
                frozenset(nodes),
                frozenset(justifications),
                target_set,
            )
            best_cost = cost
            return

        node_id = first_missing_dependency(nodes, justifications)
        if node_id is None:
            return
        if field.is_admissible_leaf(node_id):
            expanded = set(nodes)
            expanded.add(node_id)
            search(expanded, set(justifications))
            return

        alternatives = field.incoming(node_id, certified_only=True)
        if not alternatives:
            return
        alternatives = tuple(
            sorted(
                alternatives,
                key=lambda item: (
                    exact_justification_cost[item.id]
                    + sum((exact_node_cost[premise] for premise in item.premises), Fraction(0)),
                    item.id,
                ),
            )
        )
        for justification in alternatives:
            expanded_nodes = set(nodes)
            expanded_nodes.add(node_id)
            expanded_nodes.update(justification.premises)
            expanded_justifications = set(justifications)
            expanded_justifications.add(justification.id)
            search(expanded_nodes, expanded_justifications)

    initial_nodes = set(field.premises) | set(target_set)
    search(initial_nodes, set())
    if best is None:
        raise ValueError("no certified certificate derives the requested targets")
    return best

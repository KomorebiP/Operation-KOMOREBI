from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

import sympy as sp

from .forest import PerturbationForest
from .model import DeformationSystem, JSONValue


@dataclass(slots=True)
class FamilyCertificate:
    name: str
    member_node_ids: list[int]
    parameter_name: str
    parameters: dict[int, JSONValue]
    closure_directions: tuple[str, ...]
    invariant_fields: tuple[str, ...]
    relations: tuple[str, ...]
    verified: bool
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "member_node_ids": self.member_node_ids,
            "parameter_name": self.parameter_name,
            "parameters": {str(key): value for key, value in self.parameters.items()},
            "closure_directions": list(self.closure_directions),
            "invariant_fields": list(self.invariant_fields),
            "relations": list(self.relations),
            "verified": self.verified,
            "failures": self.failures,
        }


def certify_family(
    forest: PerturbationForest,
    *,
    name: str,
    predicate: Callable[[Any], bool],
    parameter_map: Callable[[Any], JSONValue],
    closure_directions: Sequence[str] = (),
    invariant_fields: Sequence[str] = (),
    relations: Sequence[str] = (),
) -> FamilyCertificate:
    members = [node for node in forest.nodes.values() if predicate(node.state)]
    failures: list[str] = []
    closure = tuple(closure_directions)
    for node in members:
        available = {direction.name: direction for direction in forest.system.directions(node.state, node.min_depth)}
        for direction_name in closure:
            if direction_name not in available:
                failures.append(f"node {node.id} lacks direction {direction_name}")
                continue
            try:
                child = forest.system.apply(node.state, available[direction_name])
            except Exception as exc:
                failures.append(f"node {node.id} failed under {direction_name}: {exc}")
                continue
            if not predicate(child):
                failures.append(f"node {node.id} leaves the family under {direction_name}")
    parameters = {node.id: parameter_map(node.state) for node in members}
    return FamilyCertificate(
        name=name,
        member_node_ids=sorted(node.id for node in members),
        parameter_name="parameter",
        parameters=parameters,
        closure_directions=closure,
        invariant_fields=tuple(invariant_fields),
        relations=tuple(relations),
        verified=not failures and bool(members),
        failures=failures,
    )


def cluster_by_signature(
    forest: PerturbationForest, fields: Sequence[str]
) -> dict[tuple[JSONValue, ...], list[int]]:
    groups: dict[tuple[JSONValue, ...], list[int]] = {}
    for node in forest.nodes.values():
        signature = tuple(node.invariants.get(field) for field in fields)
        groups.setdefault(signature, []).append(node.id)
    return groups


def infer_constant_coefficient_recurrence(
    values: Sequence[int | Fraction | sp.Rational], max_order: int = 8
) -> list[sp.Rational] | None:
    """Infer an exact recurrence a_n = sum c_j a_{n-j-1}."""
    sequence = [sp.Rational(value) for value in values]
    if len(sequence) < 3:
        return None
    for order in range(1, min(max_order, len(sequence) // 2) + 1):
        rows = []
        rhs = []
        for n in range(order, len(sequence)):
            rows.append([sequence[n - j - 1] for j in range(order)])
            rhs.append(sequence[n])
        matrix = sp.Matrix(rows)
        vector = sp.Matrix(rhs)
        try:
            solution_set = sp.linsolve((matrix, vector))
        except Exception:
            continue
        if solution_set is sp.EmptySet:
            continue
        solutions = list(solution_set)
        if len(solutions) != 1:
            continue
        solution = solutions[0]
        if any(coefficient.free_symbols for coefficient in solution):
            continue
        coefficients = [sp.Rational(coefficient) for coefficient in solution]
        if verify_recurrence(sequence, coefficients):
            return coefficients
    return None


def verify_recurrence(values: Sequence[sp.Rational], coefficients: Sequence[sp.Rational]) -> bool:
    order = len(coefficients)
    if order == 0 or len(values) <= order:
        return False
    for n in range(order, len(values)):
        predicted = sum(coefficients[j] * values[n - j - 1] for j in range(order))
        if sp.simplify(values[n] - predicted) != 0:
            return False
    return True

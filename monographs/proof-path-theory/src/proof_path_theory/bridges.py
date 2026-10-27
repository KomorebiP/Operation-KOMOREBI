from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class RetentionResult:
    retained: tuple[str, ...]
    utility: float
    spent: float


class BridgeGraph:
    """Finite directed graph used for future-reach and bridge-retention models."""

    def __init__(self, nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> None:
        self.nodes = frozenset(nodes)
        if not self.nodes:
            raise ValueError("bridge graph must contain nodes")
        if any(not str(node_id).strip() for node_id in self.nodes):
            raise ValueError("bridge node identifiers must be nonempty")
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in self.nodes}
        for left, right in edges:
            if left not in self.nodes or right not in self.nodes:
                raise ValueError("bridge edge endpoint is not a graph node")
            adjacency[left].add(right)
        self.adjacency = {
            node_id: frozenset(children)
            for node_id, children in adjacency.items()
        }

    def _validate_target_weights(self, target_weights: Mapping[str, float]) -> None:
        unknown = set(target_weights).difference(self.nodes)
        if unknown:
            raise KeyError(sorted(unknown)[0])
        for target, weight in target_weights.items():
            numeric = float(weight)
            if not isfinite(numeric) or numeric < 0:
                raise ValueError(
                    f"target weight for {target} must be finite and nonnegative"
                )

    def reachable(
        self,
        starts: Iterable[str],
        *,
        blocked: Iterable[str] = (),
        include_starts: bool = True,
    ) -> frozenset[str]:
        start_set = set(starts)
        unknown = start_set.difference(self.nodes)
        if unknown:
            raise KeyError(sorted(unknown)[0])
        blocked_set = set(blocked)
        unknown_blocked = blocked_set.difference(self.nodes)
        if unknown_blocked:
            raise KeyError(sorted(unknown_blocked)[0])
        seen: set[str] = set()
        stack = [node_id for node_id in start_set if node_id not in blocked_set]
        while stack:
            node_id = stack.pop()
            if node_id in seen or node_id in blocked_set:
                continue
            seen.add(node_id)
            stack.extend(self.adjacency[node_id].difference(seen, blocked_set))
        if not include_starts:
            seen.difference_update(start_set)
        return frozenset(seen)

    def target_utility(
        self,
        starts: Iterable[str],
        target_weights: Mapping[str, float],
        *,
        blocked: Iterable[str] = (),
    ) -> float:
        self._validate_target_weights(target_weights)
        reachable = self.reachable(starts, blocked=blocked)
        return float(
            sum(
                float(weight)
                for target, weight in target_weights.items()
                if target in reachable
            )
        )

    def dominated_targets(
        self,
        starts: Iterable[str],
        node_id: str,
        targets: Iterable[str],
    ) -> frozenset[str]:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        before = self.reachable(starts)
        after = self.reachable(starts, blocked=(node_id,))
        target_set = set(targets)
        unknown_targets = target_set.difference(self.nodes)
        if unknown_targets:
            raise KeyError(sorted(unknown_targets)[0])
        return frozenset(target_set.intersection(before.difference(after)))

    def bridge_criticality(
        self,
        starts: Iterable[str],
        node_id: str,
        target_weights: Mapping[str, float],
    ) -> float:
        self._validate_target_weights(target_weights)
        dominated = self.dominated_targets(starts, node_id, target_weights)
        return float(sum(float(target_weights[target]) for target in dominated))


def _validated_selection_sets(
    graph: BridgeGraph,
    candidates: Sequence[str],
    mandatory: Iterable[str],
) -> tuple[tuple[str, ...], set[str]]:
    candidate_tuple = tuple(dict.fromkeys(candidates))
    mandatory_set = set(mandatory)
    unknown = set(candidate_tuple).union(mandatory_set).difference(graph.nodes)
    if unknown:
        raise KeyError(sorted(unknown)[0])
    overlap = set(candidate_tuple).intersection(mandatory_set)
    if overlap:
        raise ValueError("candidate and mandatory node sets must be disjoint")
    return candidate_tuple, mandatory_set


def _validated_budget(value: float, *, integral: bool = False) -> float:
    numeric = float(value)
    if not isfinite(numeric) or numeric < 0:
        raise ValueError("budget must be finite and nonnegative")
    if integral and not numeric.is_integer():
        raise ValueError("cardinality budget must be an integer")
    return numeric


def is_monotone_submodular_coverage(
    graph: BridgeGraph,
    candidates: Sequence[str],
    target_weights: Mapping[str, float],
    *,
    mandatory: Iterable[str] = (),
    tolerance: float = 1e-12,
) -> bool:
    """Exhaustively verify monotonicity and diminishing returns on a small instance."""
    candidate_tuple, mandatory_mutable = _validated_selection_sets(
        graph, candidates, mandatory
    )
    mandatory_set = frozenset(mandatory_mutable)
    subsets = [
        frozenset(choice)
        for size in range(len(candidate_tuple) + 1)
        for choice in combinations(candidate_tuple, size)
    ]
    utility = {
        subset: graph.target_utility(mandatory_set | subset, target_weights)
        for subset in subsets
    }
    for left in subsets:
        for right in subsets:
            if not left.issubset(right):
                continue
            if utility[left] > utility[right] + tolerance:
                return False
            for element in set(candidate_tuple).difference(right):
                marginal_left = utility[left | {element}] - utility[left]
                marginal_right = utility[right | {element}] - utility[right]
                if marginal_left + tolerance < marginal_right:
                    return False
    return True


def greedy_cardinality_retention(
    graph: BridgeGraph,
    candidates: Sequence[str],
    target_weights: Mapping[str, float],
    *,
    budget: int,
    mandatory: Iterable[str] = (),
) -> RetentionResult:
    budget_value = int(_validated_budget(budget, integral=True))
    candidate_tuple, mandatory_set = _validated_selection_sets(
        graph, candidates, mandatory
    )
    retained: list[str] = []
    remaining = list(candidate_tuple)
    current = graph.target_utility(mandatory_set, target_weights)
    while remaining and len(retained) < budget_value:
        scored = []
        for node_id in remaining:
            value = graph.target_utility(
                mandatory_set | set(retained) | {node_id},
                target_weights,
            )
            scored.append((value - current, node_id, value))
        gain, node_id, value = min(
            scored,
            key=lambda item: (-item[0], item[1]),
        )
        if gain <= 0:
            break
        retained.append(node_id)
        remaining.remove(node_id)
        current = value
    return RetentionResult(tuple(retained), float(current), float(len(retained)))


def exact_cardinality_retention(
    graph: BridgeGraph,
    candidates: Sequence[str],
    target_weights: Mapping[str, float],
    *,
    budget: int,
    mandatory: Iterable[str] = (),
) -> RetentionResult:
    budget_value = int(_validated_budget(budget, integral=True))
    candidate_tuple, mandatory_set = _validated_selection_sets(
        graph, candidates, mandatory
    )
    best_choice: tuple[str, ...] = ()
    best_value = graph.target_utility(mandatory_set, target_weights)
    for size in range(min(budget_value, len(candidate_tuple)) + 1):
        for choice in combinations(candidate_tuple, size):
            value = graph.target_utility(mandatory_set | set(choice), target_weights)
            if value > best_value + 1e-12 or (
                abs(value - best_value) <= 1e-12 and choice < best_choice
            ):
                best_choice = choice
                best_value = value
    return RetentionResult(best_choice, float(best_value), float(len(best_choice)))


def greedy_cost_retention(
    graph: BridgeGraph,
    candidates: Sequence[str],
    target_weights: Mapping[str, float],
    costs: Mapping[str, float],
    *,
    budget: float,
    mandatory: Iterable[str] = (),
) -> RetentionResult:
    budget_value = _validated_budget(budget)
    candidate_tuple, mandatory_set = _validated_selection_sets(
        graph, candidates, mandatory
    )
    relevant_nodes = set(candidate_tuple).union(mandatory_set)
    validated_costs: dict[str, float] = {}
    for node_id in relevant_nodes:
        cost = float(costs.get(node_id, 0.0))
        if not isfinite(cost) or cost < 0:
            raise ValueError("retention costs must be finite and nonnegative")
        validated_costs[node_id] = cost
    spent = sum(validated_costs[node_id] for node_id in mandatory_set)
    if spent > budget_value + 1e-12:
        raise ValueError("mandatory nodes exceed budget")
    retained: list[str] = []
    remaining = list(candidate_tuple)
    current = graph.target_utility(mandatory_set, target_weights)
    while remaining:
        best: tuple[float, str, float, float] | None = None
        for node_id in remaining:
            cost = validated_costs[node_id]
            if spent + cost > budget_value + 1e-12:
                continue
            value = graph.target_utility(
                mandatory_set | set(retained) | {node_id},
                target_weights,
            )
            gain = value - current
            ratio = float("inf") if cost == 0 and gain > 0 else (gain / cost if cost > 0 else 0.0)
            candidate = (ratio, node_id, gain, value)
            if best is None or ratio > best[0] + 1e-12 or (
                abs(ratio - best[0]) <= 1e-12 and node_id < best[1]
            ):
                best = candidate
        if best is None or best[2] <= 0:
            break
        _, node_id, _, value = best
        retained.append(node_id)
        remaining.remove(node_id)
        spent += validated_costs[node_id]
        current = value
    return RetentionResult(tuple(retained), float(current), float(spent))

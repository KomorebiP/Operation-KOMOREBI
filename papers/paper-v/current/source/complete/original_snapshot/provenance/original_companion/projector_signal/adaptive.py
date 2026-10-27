from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from collections.abc import Mapping, Sequence
import math

import numpy as np

from .filterbanks import haar_analyze, haar_synthesize


@dataclass(frozen=True)
class PruningResult:
    """Exact optimum of an additive cost on a finite binary packet tree."""

    cost: float
    nodes: tuple[str, ...]
    margins: Mapping[str, float]


def enumerate_prunings(max_depth: int, prefix: str = "") -> tuple[tuple[str, ...], ...]:
    """Enumerate every complete pruning below ``prefix``.

    A pruning either stops at the current node or refines both children.  The
    count therefore satisfies a_0=1 and a_{d+1}=1+a_d^2.
    """
    if max_depth < len(prefix):
        raise ValueError("max_depth must be at least the prefix depth")
    if len(prefix) == max_depth:
        return ((prefix,),)
    left = enumerate_prunings(max_depth, prefix + "0")
    right = enumerate_prunings(max_depth, prefix + "1")
    refined = tuple(tuple(sorted(a + b)) for a, b in product(left, right))
    return ((prefix,),) + refined


def is_complete_pruning(nodes: Sequence[str], max_depth: int) -> bool:
    """Return whether ``nodes`` is a complete antichain of the depth tree."""
    selected = set(nodes)
    if not selected or len(selected) != len(tuple(nodes)):
        return False
    if any(len(path) > max_depth or set(path) - {"0", "1"} for path in selected):
        return False
    ordered = sorted(selected, key=len)
    for i, path in enumerate(ordered):
        if any(other.startswith(path) for other in ordered[i + 1 :]):
            return False
    for leaf_number in range(2**max_depth):
        leaf = format(leaf_number, f"0{max_depth}b") if max_depth else ""
        if sum(leaf.startswith(path) for path in selected) != 1:
            return False
    return True


def all_haar_packet_nodes(x: Sequence[complex], max_depth: int) -> dict[str, np.ndarray]:
    """Analyze a signal at every node of the complete Haar packet tree."""
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    root = np.asarray(x)
    if root.ndim != 1 or root.size % (2**max_depth):
        raise ValueError("signal length must be divisible by 2**max_depth")
    nodes: dict[str, np.ndarray] = {"": root.copy()}
    frontier = [""]
    for _ in range(max_depth):
        next_frontier: list[str] = []
        for path in frontier:
            low, high = haar_analyze(nodes[path])
            nodes[path + "0"] = low
            nodes[path + "1"] = high
            next_frontier.extend((path + "0", path + "1"))
        frontier = next_frontier
    return nodes


def synthesize_pruning(
    packet_nodes: Mapping[str, Sequence[complex]],
    pruning: Sequence[str],
    max_depth: int,
) -> np.ndarray:
    """Synthesize a complete mixed-depth Haar packet pruning exactly."""
    selected = set(pruning)
    if not is_complete_pruning(tuple(selected), max_depth):
        raise ValueError("pruning must be a complete antichain")

    def rebuild(path: str) -> np.ndarray:
        if path in selected:
            if path not in packet_nodes:
                raise KeyError(f"missing packet coefficients for {path!r}")
            return np.asarray(packet_nodes[path])
        if len(path) >= max_depth:
            raise ValueError("incomplete pruning")
        return haar_synthesize(rebuild(path + "0"), rebuild(path + "1"))

    return rebuild("")


def pruning_cost(pruning: Sequence[str], costs: Mapping[str, float]) -> float:
    return float(sum(float(costs[path]) for path in pruning))


def best_pruning(
    costs: Mapping[str, float],
    max_depth: int,
    *,
    prefer_stop_on_tie: bool = True,
) -> PruningResult:
    """Compute a globally optimal complete pruning by dynamic programming.

    ``margins[path]`` is ``stop_cost - refined_cost``.  Negative values favor
    stopping; positive values favor refinement.
    """
    margins: dict[str, float] = {}

    def solve(path: str) -> tuple[float, tuple[str, ...]]:
        if path not in costs:
            raise KeyError(f"missing local cost for node {path!r}")
        stop = float(costs[path])
        if len(path) == max_depth:
            return stop, (path,)
        left_cost, left_nodes = solve(path + "0")
        right_cost, right_nodes = solve(path + "1")
        refined = left_cost + right_cost
        margins[path] = stop - refined
        choose_stop = stop < refined or (prefer_stop_on_tie and stop == refined)
        if choose_stop:
            return stop, (path,)
        return refined, tuple(sorted(left_nodes + right_nodes))

    optimum, nodes = solve("")
    return PruningResult(optimum, nodes, margins)


def perturbation_envelope(local_bounds: Mapping[str, float], max_depth: int) -> float:
    """Worst possible cost perturbation over all complete prunings."""

    def envelope(path: str) -> float:
        if path not in local_bounds:
            raise KeyError(f"missing perturbation bound for node {path!r}")
        stop = abs(float(local_bounds[path]))
        if len(path) == max_depth:
            return stop
        return max(stop, envelope(path + "0") + envelope(path + "1"))

    return envelope("")


def optimum_gap(costs: Mapping[str, float], max_depth: int) -> float:
    """Gap between the smallest and second-smallest pruning costs."""
    values = sorted(pruning_cost(pruning, costs) for pruning in enumerate_prunings(max_depth))
    if len(values) < 2:
        return math.inf
    return float(values[1] - values[0])


def stable_by_gap(gap: float, perturbation_bound: float) -> bool:
    """Sufficient deterministic stability criterion from the global gap."""
    return float(gap) > 2.0 * float(perturbation_bound)


def shannon_packet_cost(
    coefficients: Sequence[complex],
    *,
    complexity_penalty: float = 0.0,
    leakage_penalty: float = 0.0,
    zero_tolerance: float = 1e-300,
    reference_energy: float | None = None,
) -> float:
    """Additive information cost for one packet node.

    The coefficients themselves are not discarded.  This is a basis-selection
    cost, so every complete pruning still has exact synthesis.
    """
    values = np.abs(np.asarray(coefficients)) ** 2
    total = float(values.sum())
    scale = total if reference_energy is None else float(reference_energy)
    if total <= zero_tolerance or scale <= zero_tolerance:
        entropy = 0.0
    else:
        probabilities = values[values > zero_tolerance] / scale
        entropy = float(-np.sum(probabilities * np.log(probabilities)))
    return entropy + float(complexity_penalty) + float(leakage_penalty)


def packet_tree_costs(
    packet_nodes: Mapping[str, Sequence[complex]],
    max_depth: int,
    *,
    complexity_per_node: float = 0.0,
    leakage: Mapping[str, float] | None = None,
) -> dict[str, float]:
    """Build local entropy + leakage + complexity costs for every node."""
    leakage = {} if leakage is None else leakage
    root_energy = float(np.sum(np.abs(np.asarray(packet_nodes[""])) ** 2))
    result: dict[str, float] = {}
    for depth in range(max_depth + 1):
        for number in range(2**depth):
            path = format(number, f"0{depth}b") if depth else ""
            if path not in packet_nodes:
                raise KeyError(f"missing packet node {path!r}")
            result[path] = shannon_packet_cost(
                packet_nodes[path],
                complexity_penalty=complexity_per_node,
                leakage_penalty=float(leakage.get(path, 0.0)),
                reference_energy=root_energy,
            )
    return result

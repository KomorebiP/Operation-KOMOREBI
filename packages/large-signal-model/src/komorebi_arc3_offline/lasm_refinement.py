from __future__ import annotations

"""Exact adaptive packet-tree refinement for PR-LASM."""

from dataclasses import dataclass
from math import log
from typing import Callable, Mapping
from types import MappingProxyType
from ._validation import integer, real_array, readonly

import numpy as np

from .types import FloatArray


def haar_pair_analyze(values: FloatArray) -> tuple[FloatArray, FloatArray]:
    array = real_array(values, "packet values", ndim=1)
    if array.size % 2:
        raise ValueError("packet split requires an even one-dimensional vector")
    root2 = np.sqrt(2.0)
    return (array[0::2] + array[1::2]) / root2, (array[0::2] - array[1::2]) / root2


def haar_pair_synthesize(low: FloatArray, high: FloatArray) -> FloatArray:
    low_array = real_array(low, "low packet", ndim=1)
    high_array = real_array(high, "high packet", ndim=1)
    if low_array.shape != high_array.shape:
        raise ValueError("children must have equal shape")
    root2 = np.sqrt(2.0)
    output = np.empty(low_array.size * 2, dtype=np.float64)
    output[0::2] = (low_array + high_array) / root2
    output[1::2] = (low_array - high_array) / root2
    return output


@dataclass(frozen=True)
class PacketTree:
    coefficients: Mapping[str, FloatArray]
    maximum_depth: int

    def __post_init__(self) -> None:
        depth = integer(self.maximum_depth, "maximum_depth")
        if "" not in self.coefficients:
            raise ValueError("packet tree must contain a root")
        root = real_array(self.coefficients[""], "root", ndim=1)
        if depth > root.size.bit_length() - 1 or root.size % (2**depth):
            raise ValueError("vector length is not divisible by the requested depth")
        expected = {format(i, f"0{d}b") if d else "" for d in range(depth + 1) for i in range(2**d)}
        if set(self.coefficients) != expected:
            raise ValueError("packet tree must contain every node through maximum_depth")
        checked = {}
        for path, values in self.coefficients.items():
            array = real_array(values, "packet coefficients", ndim=1)
            if array.shape != (root.size // (2**len(path)),):
                raise ValueError(f"wrong coefficient shape for packet {path!r}")
            checked[path] = readonly(array)
        object.__setattr__(self, "coefficients", MappingProxyType(checked))

    @classmethod
    def analyze(cls, values: FloatArray, maximum_depth: int) -> "PacketTree":
        root = real_array(values, "packet root", ndim=1)
        maximum_depth = integer(maximum_depth, "maximum_depth")
        if maximum_depth > root.size.bit_length() - 1 or root.size % (2**maximum_depth):
            raise ValueError("vector length must be divisible by the complete packet depth")
        packets: dict[str, FloatArray] = {"": root.copy()}
        frontier = [""]
        for _ in range(maximum_depth):
            new_frontier: list[str] = []
            for path in frontier:
                low, high = haar_pair_analyze(packets[path])
                packets[path + "0"] = low
                packets[path + "1"] = high
                new_frontier.extend([path + "0", path + "1"])
            frontier = new_frontier
        return cls(packets, maximum_depth)

    def children(self, path: str) -> tuple[str, str] | None:
        left, right = path + "0", path + "1"
        return (left, right) if left in self.coefficients and right in self.coefficients else None

    def synthesize(self, pruning: Mapping[str, FloatArray] | set[str] | tuple[str, ...]) -> FloatArray:
        paths = list(pruning)
        if not paths or len(paths) != len(set(paths)):
            raise ValueError("a complete pruning must be nonempty and contain no duplicate paths")
        for path in paths:
            if path not in self.coefficients:
                raise ValueError(f"unknown packet path: {path!r}")
        chosen = set(paths)
        if any(path[:k] in chosen for path in paths for k in range(len(path))):
            raise ValueError("selected packet family contains overlapping ancestors and descendants")
        selected = {}
        for path in paths:
            value = pruning[path] if isinstance(pruning, Mapping) else self.coefficients[path]
            array = real_array(value, "selected packet", ndim=1)
            if array.shape != self.coefficients[path].shape:
                raise ValueError(f"wrong coefficient shape for selected packet {path!r}")
            selected[path] = array.copy()
        current = dict(selected)
        # A complete pruning contains exactly enough nodes for every branch to
        # synthesize the root.  Combine deepest siblings until the root appears.
        while "" not in current:
            depths = sorted({len(path) for path in current}, reverse=True)
            combined = False
            for depth in depths:
                parents = sorted({path[:-1] for path in current if len(path) == depth})
                for parent in parents:
                    left, right = parent + "0", parent + "1"
                    if left in current and right in current:
                        current[parent] = haar_pair_synthesize(current.pop(left), current.pop(right))
                        combined = True
                if combined:
                    break
            if not combined:
                raise ValueError("selected nodes are not a complete packet pruning")
        if len(current) != 1:
            raise ValueError("selected packet family contains overlapping ancestors and descendants")
        return current[""]


def shannon_packet_cost(coefficients: FloatArray, complexity: float = 0.0) -> float:
    values = np.asarray(coefficients, dtype=np.float64)
    energy = values * values
    total = float(energy.sum())
    if total <= 1e-18:
        return float(complexity)
    probability = energy / total
    positive = probability[probability > 0]
    entropy = -float(np.sum(positive * np.log(positive)))
    return entropy + float(complexity)


def l1_packet_cost(coefficients: FloatArray, complexity: float = 0.0) -> float:
    """Additive sparsity cost used by the finite best-basis benchmark."""
    return float(np.sum(np.abs(np.asarray(coefficients, dtype=np.float64))) + complexity)


@dataclass(frozen=True)
class BestBasisResult:
    paths: tuple[str, ...]
    total_cost: float
    node_costs: Mapping[str, float]
    decisions: Mapping[str, str]

    def coefficients(self, tree: PacketTree) -> dict[str, FloatArray]:
        return {path: np.asarray(tree.coefficients[path], dtype=np.float64) for path in self.paths}


def best_basis(
    tree: PacketTree,
    *,
    cost: Callable[[FloatArray, float], float] = shannon_packet_cost,
    packet_penalty: float = 0.01,
) -> BestBasisResult:
    """Find the exact minimum-cost complete pruning by bottom-up dynamic programming."""
    if not np.isfinite(packet_penalty):
        raise ValueError("packet_penalty must be finite")
    values: dict[str, float] = {}
    selections: dict[str, tuple[str, ...]] = {}
    decisions: dict[str, str] = {}
    node_costs: dict[str, float] = {}
    for depth in range(tree.maximum_depth, -1, -1):
        for path in sorted(key for key in tree.coefficients if len(key) == depth):
            direct = float(cost(tree.coefficients[path], packet_penalty))
            if not np.isfinite(direct):
                raise ValueError(f"nonfinite packet cost at {path!r}")
            node_costs[path] = direct
            children = tree.children(path)
            if children is None:
                values[path] = direct
                selections[path] = (path,)
                decisions[path] = "leaf"
                continue
            split = values[children[0]] + values[children[1]]
            if direct <= split:
                values[path] = direct
                selections[path] = (path,)
                decisions[path] = "keep"
            else:
                values[path] = split
                selections[path] = selections[children[0]] + selections[children[1]]
                decisions[path] = "split"
    return BestBasisResult(
        paths=tuple(sorted(selections[""], key=lambda value: (len(value), value))),
        total_cost=float(values[""]),
        node_costs=node_costs,
        decisions=decisions,
    )


def pruning_feature_vector(tree: PacketTree, result: BestBasisResult) -> FloatArray:
    """Return invariant statistics for the selected packet basis."""
    features: list[float] = []
    root_energy = max(float(np.sum(tree.coefficients[""] ** 2)), 1e-12)
    for path in result.paths:
        values = tree.coefficients[path]
        features.extend(
            [
                len(path) / max(1, tree.maximum_depth),
                float(np.sum(values**2) / root_energy),
                float(np.mean(np.abs(values))),
                float(np.std(values)),
            ]
        )
    # Fixed-size tail: aggregate by depth, allowing different mixed-depth bases
    # to enter one Bayesian design matrix.
    by_depth = np.zeros((tree.maximum_depth + 1, 3), dtype=np.float64)
    for path in result.paths:
        values = tree.coefficients[path]
        depth = len(path)
        by_depth[depth, 0] += 1.0
        by_depth[depth, 1] += float(np.sum(values**2) / root_energy)
        by_depth[depth, 2] += float(np.mean(np.abs(values)))
    return np.concatenate([by_depth.ravel(), [result.total_cost, len(result.paths)]])


__all__ = [
    "BestBasisResult",
    "PacketTree",
    "best_basis",
    "haar_pair_analyze",
    "haar_pair_synthesize",
    "l1_packet_cost",
    "pruning_feature_vector",
    "shannon_packet_cost",
]

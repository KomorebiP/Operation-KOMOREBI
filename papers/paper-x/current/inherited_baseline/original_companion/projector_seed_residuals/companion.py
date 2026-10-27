from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


def evaluate_polynomial(coefficients: Sequence[int], x: int) -> int:
    total = 0
    for coefficient in coefficients:
        total = total * x + int(coefficient)
    return total


def roots_mod_prime_power(coefficients: Sequence[int], p: int, depth: int) -> list[int]:
    modulus = p**depth
    return [x for x in range(modulus) if evaluate_polynomial(coefficients, x) % modulus == 0]


@dataclass(frozen=True)
class RootForest:
    p: int
    levels: tuple[tuple[int, ...], ...]
    parents: tuple[dict[int, int], ...]


def build_root_forest(coefficients: Sequence[int], p: int, depth: int) -> RootForest:
    if depth < 1:
        raise ValueError("depth must be positive")
    levels = [tuple(roots_mod_prime_power(coefficients, p, m)) for m in range(1, depth + 1)]
    parents: list[dict[int, int]] = []
    for m in range(1, depth):
        modulus = p**m
        parents.append({child: child % modulus for child in levels[m]})
    return RootForest(p, tuple(levels), tuple(parents))


def enumerate_branches(forest: RootForest) -> list[tuple[int, ...]]:
    if not forest.levels or not forest.levels[0]:
        return []
    branches = [(x,) for x in forest.levels[0]]
    for level_index in range(1, len(forest.levels)):
        parent_map = forest.parents[level_index - 1]
        next_branches: list[tuple[int, ...]] = []
        for branch in branches:
            parent = branch[-1]
            for child in forest.levels[level_index]:
                if parent_map[child] == parent:
                    next_branches.append(branch + (child,))
        branches = next_branches
    return branches


def has_nodes_at_every_level(forest: RootForest) -> bool:
    return all(bool(level) for level in forest.levels)


def transition_is_surjective(forest: RootForest, level_index: int) -> bool:
    if not 0 <= level_index < len(forest.parents):
        raise IndexError("invalid transition")
    return set(forest.parents[level_index].values()) == set(forest.levels[level_index])

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any


def branching_entropy(counts: dict[int, int]) -> float:
    """Return limsup proxy max(log count / depth) over observed positive depths."""
    values = [math.log(count) / depth for depth, count in counts.items() if depth > 0 and count > 0]
    return max(values, default=0.0)


def growth_series(counts: dict[int, int], z: complex) -> complex:
    return sum(count * (z**depth) for depth, count in counts.items())


def weighted_partition_function(costs: Iterable[float], s: float) -> float:
    if s < 0:
        raise ValueError("s must be nonnegative")
    return math.fsum(math.exp(-s * float(cost)) for cost in costs)


def geometric_tree_partition(branching: int, step_cost: float, s: float) -> float:
    """Closed partition function sum over all positive path lengths.

    It converges exactly when branching * exp(-s * step_cost) < 1.
    """
    if branching < 0 or step_cost <= 0 or s < 0:
        raise ValueError("invalid parameters")
    ratio = branching * math.exp(-s * step_cost)
    if ratio >= 1:
        return math.inf
    return ratio / (1.0 - ratio)


def propagated_cover_error(
    lipschitz_state: Sequence[float],
    lipschitz_direction: Sequence[float],
    cover_radii: Sequence[float],
    *,
    initial_error: float = 0.0,
) -> float:
    """Compute the recursive endpoint error for sampled direction covers.

    e_{k+1} <= L_k e_k + M_k epsilon_k.
    """
    if not (len(lipschitz_state) == len(lipschitz_direction) == len(cover_radii)):
        raise ValueError("all sequences must have equal length")
    error = float(initial_error)
    for state_lipschitz, direction_lipschitz, radius in zip(
        lipschitz_state, lipschitz_direction, cover_radii
    ):
        if min(state_lipschitz, direction_lipschitz, radius) < 0:
            raise ValueError("Lipschitz constants and cover radii must be nonnegative")
        error = state_lipschitz * error + direction_lipschitz * radius
    return error


def summable_step_tail(step_bounds: Sequence[float], start: int) -> float:
    if start < 0:
        raise ValueError("start must be nonnegative")
    if any(bound < 0 for bound in step_bounds):
        raise ValueError("step bounds must be nonnegative")
    return math.fsum(step_bounds[start:])


def cauchy_residual(states: Sequence[Any], distance: Any) -> float:
    if len(states) < 2:
        return 0.0
    return max(float(distance(states[i], states[j])) for i in range(len(states)) for j in range(i + 1, len(states)))


def exact_walk_endpoint_count(depth: int) -> int:
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    return depth + 1


def exact_walk_raw_count(depth: int) -> int:
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    return 2**depth

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


@dataclass(frozen=True, slots=True)
class RefinementDecision:
    keep: bool
    utility_gain: float
    reason: str


def refinement_decision(
    value_gains: Mapping[str, float],
    *,
    cost_increase: float,
    goal_weights: Mapping[str, float],
    threshold: float = 0.0,
    bridge_override: float | None = None,
) -> RefinementDecision:
    if not np.isfinite(float(cost_increase)) or cost_increase < 0:
        raise ValueError("cost_increase must be finite and nonnegative")
    if not np.isfinite(float(threshold)):
        raise ValueError("threshold must be finite")
    if bridge_override is not None and (
        not np.isfinite(float(bridge_override)) or bridge_override < 0
    ):
        raise ValueError("bridge_override must be finite and nonnegative")
    if any(
        not np.isfinite(float(value)) or float(value) < 0
        for value in value_gains.values()
    ):
        raise ValueError("value gains must be finite and nonnegative")
    if any(
        not np.isfinite(float(value)) or float(value) < 0
        for value in goal_weights.values()
    ):
        raise ValueError("goal weights must be finite and nonnegative")
    utility = sum(
        float(goal_weights.get(name, 0.0)) * float(value)
        for name, value in value_gains.items()
    ) - cost_increase
    if bridge_override is not None and value_gains.get("bridge", 0.0) >= bridge_override:
        return RefinementDecision(True, float(utility), "bridge-retention override")
    if utility > threshold:
        return RefinementDecision(True, float(utility), "positive goal-relative utility")
    return RefinementDecision(False, float(utility), "insufficient goal-relative utility")


def optimal_depth(
    residuals: Sequence[float],
    costs: Sequence[float],
    *,
    residual_weight: float,
    cost_weight: float,
) -> int:
    residual_array = np.asarray(residuals, dtype=float)
    cost_array = np.asarray(costs, dtype=float)
    if residual_array.ndim != 1 or cost_array.ndim != 1:
        raise ValueError("residuals and costs must be one-dimensional")
    if residual_array.shape != cost_array.shape or len(residual_array) == 0:
        raise ValueError("residuals and costs must be nonempty and equal length")
    if not np.all(np.isfinite(residual_array)) or not np.all(np.isfinite(cost_array)):
        raise ValueError("residuals and costs must be finite")
    if np.any(residual_array < 0) or np.any(cost_array < 0):
        raise ValueError("residuals and costs must be nonnegative")
    if np.any(np.diff(cost_array) < 0):
        raise ValueError("cumulative costs must be nondecreasing")
    if np.any(np.diff(residual_array) > 0):
        raise ValueError("residuals must be nonincreasing")
    if (
        not np.isfinite(float(residual_weight))
        or not np.isfinite(float(cost_weight))
        or residual_weight < 0
        or cost_weight < 0
    ):
        raise ValueError("objective weights must be finite and nonnegative")
    objective = residual_weight * residual_array + cost_weight * cost_array
    return int(np.argmin(objective))


def stopping_depth(
    residuals: Sequence[float],
    costs: Sequence[float],
    *,
    residual_tolerance: float,
    marginal_gain_floor: float,
) -> int:
    residual_array = np.asarray(residuals, dtype=float)
    cost_array = np.asarray(costs, dtype=float)
    if residual_array.shape != cost_array.shape or residual_array.ndim != 1:
        raise ValueError("residuals and costs must be equal one-dimensional arrays")
    if len(residual_array) == 0:
        raise ValueError("at least one depth is required")
    if not np.all(np.isfinite(residual_array)) or not np.all(np.isfinite(cost_array)):
        raise ValueError("residuals and costs must be finite")
    if np.any(residual_array < 0) or np.any(cost_array < 0):
        raise ValueError("residuals and costs must be nonnegative")
    if (
        not np.isfinite(float(residual_tolerance))
        or not np.isfinite(float(marginal_gain_floor))
        or residual_tolerance < 0
        or marginal_gain_floor < 0
    ):
        raise ValueError("stopping parameters must be finite and nonnegative")
    if np.any(np.diff(cost_array) < 0):
        raise ValueError("cumulative costs must be nondecreasing")
    if np.any(np.diff(residual_array) > 0):
        raise ValueError("residuals must be nonincreasing")
    for depth, residual in enumerate(residual_array):
        if residual <= residual_tolerance:
            return depth
        if depth > 0:
            gain = residual_array[depth - 1] - residual
            cost_gain = cost_array[depth] - cost_array[depth - 1]
            marginal = gain / cost_gain if cost_gain > 0 else float("inf")
            if marginal < marginal_gain_floor:
                return depth - 1
    return len(residual_array) - 1

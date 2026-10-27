from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Sequence

import numpy as np


class AuditRegime(str, Enum):
    STABLE = "stable"
    CRITICAL = "critical"
    UNSTABLE = "unstable"


@dataclass(frozen=True, slots=True)
class AuditQueueResult:
    backlog: np.ndarray
    audited: np.ndarray
    accepted: np.ndarray
    rejected: np.ndarray

    @property
    def final_backlog(self) -> float:
        return float(self.backlog[-1]) if len(self.backlog) else 0.0


def constant_rate_regime(arrival_rate: float, service_rate: float) -> AuditRegime:
    if not isfinite(float(arrival_rate)) or not isfinite(float(service_rate)):
        raise ValueError("rates must be finite")
    if arrival_rate < 0 or service_rate < 0:
        raise ValueError("rates must be nonnegative")
    if arrival_rate < service_rate:
        return AuditRegime.STABLE
    if arrival_rate > service_rate:
        return AuditRegime.UNSTABLE
    return AuditRegime.CRITICAL


def simulate_audit_queue(
    arrivals: Sequence[float],
    capacity: Sequence[float],
    *,
    initial_backlog: float = 0.0,
    acceptance_rate: float = 0.35,
) -> AuditQueueResult:
    arrivals_array = np.asarray(arrivals, dtype=float)
    capacity_array = np.asarray(capacity, dtype=float)
    if arrivals_array.shape != capacity_array.shape:
        raise ValueError("arrivals and capacity must have the same shape")
    if not np.all(np.isfinite(arrivals_array)) or not np.all(
        np.isfinite(capacity_array)
    ):
        raise ValueError("arrivals and capacity must be finite")
    if arrivals_array.ndim != 1:
        raise ValueError("arrivals and capacity must be one-dimensional")
    if np.any(arrivals_array < 0) or np.any(capacity_array < 0):
        raise ValueError("arrivals and capacity must be nonnegative")
    if not isfinite(float(initial_backlog)) or initial_backlog < 0:
        raise ValueError("initial_backlog must be finite and nonnegative")
    if not isfinite(float(acceptance_rate)) or not 0.0 <= acceptance_rate <= 1.0:
        raise ValueError("acceptance_rate must lie in [0, 1]")

    backlog = np.zeros_like(arrivals_array)
    audited = np.zeros_like(arrivals_array)
    accepted = np.zeros_like(arrivals_array)
    rejected = np.zeros_like(arrivals_array)
    current = float(initial_backlog)
    for index, arrival in enumerate(arrivals_array):
        current += float(arrival)
        audited[index] = min(current, float(capacity_array[index]))
        current -= float(audited[index])
        accepted[index] = acceptance_rate * audited[index]
        rejected[index] = (1.0 - acceptance_rate) * audited[index]
        backlog[index] = current
    return AuditQueueResult(backlog, audited, accepted, rejected)


def audit_priority(
    *,
    error_probability: float,
    consequence: float,
    dependency_reach: float,
    audit_cost: float,
) -> float:
    inputs = (error_probability, consequence, dependency_reach, audit_cost)
    if any(not isfinite(float(value)) for value in inputs):
        raise ValueError("priority inputs must be finite")
    if not 0.0 <= error_probability <= 1.0:
        raise ValueError("error_probability must lie in [0, 1]")
    if consequence < 0 or dependency_reach < 0 or audit_cost < 0:
        raise ValueError("priority inputs must be nonnegative")
    numerator = error_probability * consequence * (1.0 + dependency_reach)
    return float(numerator / audit_cost) if audit_cost > 0 else float("inf")

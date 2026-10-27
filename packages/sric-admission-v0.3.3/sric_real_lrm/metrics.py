from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterable, Mapping, Sequence
import hashlib
import numpy as np


def mean(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=np.float64)
    return float(np.mean(array)) if array.size else float("nan")


def positive_fraction(values: Iterable[float], threshold: float = 0.0) -> float:
    array = np.asarray(list(values), dtype=np.float64)
    return float(np.mean(array > threshold)) if array.size else float("nan")


def max_absolute(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=np.float64)
    return float(np.max(np.abs(array))) if array.size else float("nan")


def grouped_bootstrap_interval(
    values: Sequence[float],
    groups: Sequence[str],
    *,
    replicates: int,
    seed: int,
    alpha: float = 0.05,
    statistic: Callable[[np.ndarray], float] | None = None,
) -> tuple[float, float]:
    if len(values) != len(groups):
        raise ValueError("values and groups must have equal length")
    if not values:
        return float("nan"), float("nan")
    statistic = statistic or (lambda x: float(np.mean(x)))
    grouped: dict[str, list[float]] = defaultdict(list)
    for value, group in zip(values, groups):
        grouped[str(group)].append(float(value))
    group_ids = sorted(grouped)
    group_arrays = {group: np.asarray(grouped[group], dtype=np.float64) for group in group_ids}
    digest = hashlib.sha256(f"{seed}:{','.join(group_ids)}".encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    samples = np.empty(replicates, dtype=np.float64)
    for index in range(replicates):
        selected = rng.choice(group_ids, size=len(group_ids), replace=True)
        concatenated = np.concatenate([group_arrays[group] for group in selected])
        samples[index] = statistic(concatenated)
    return (
        float(np.quantile(samples, alpha / 2)),
        float(np.quantile(samples, 1 - alpha / 2)),
    )


def covariance_from_traces(traces: Iterable[np.ndarray]) -> np.ndarray:
    arrays = [np.asarray(trace, dtype=np.float64) for trace in traces]
    if not arrays:
        raise ValueError("At least one trace is required")
    observations = np.concatenate(arrays, axis=0)
    centered = observations - observations.mean(axis=0, keepdims=True)
    denominator = max(1, observations.shape[0] - 1)
    return centered.T @ centered / denominator


def summarize_effect(
    rows: Sequence[Mapping[str, object]],
    field: str,
    *,
    groups_field: str = "group_id",
    replicates: int,
    seed: int,
) -> dict[str, float | list[float]]:
    values = [float(row[field]) for row in rows]
    groups = [str(row[groups_field]) for row in rows]
    low, high = grouped_bootstrap_interval(values, groups, replicates=replicates, seed=seed)
    return {
        "mean": mean(values),
        "positive_fraction": positive_fraction(values),
        "interval_95": [low, high],
    }

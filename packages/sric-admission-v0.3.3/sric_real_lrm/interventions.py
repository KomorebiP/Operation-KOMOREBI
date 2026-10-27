from __future__ import annotations

import hashlib
from typing import Any
import numpy as np


def _seed(task_id: str, salt: str, base_seed: int) -> int:
    text = f"{base_seed}:{task_id}:{salt}".encode("utf-8")
    return int(hashlib.sha256(text).hexdigest()[:16], 16) % (2**32)


def ensure_trace(trace: Any) -> np.ndarray:
    array = np.asarray(trace, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError(f"Expected a [steps, hidden] trace, got {array.shape}")
    if not np.isfinite(array).all():
        raise ValueError("Trace contains non-finite values")
    return array


def zero_trace(trace: Any) -> np.ndarray:
    return np.zeros_like(ensure_trace(trace))


def derangement(length: int, task_id: str, base_seed: int) -> np.ndarray:
    if length < 2:
        return np.arange(length)
    rng = np.random.default_rng(_seed(task_id, "permutation", base_seed))
    for _ in range(100):
        permutation = rng.permutation(length)
        if np.all(permutation != np.arange(length)):
            return permutation
    return np.roll(np.arange(length), 1)


def permute_trace(trace: Any, task_id: str, base_seed: int) -> np.ndarray:
    array = ensure_trace(trace)
    return array[derangement(array.shape[0], task_id, base_seed)]


def norm_matched_noise(trace: Any, task_id: str, base_seed: int) -> np.ndarray:
    array = ensure_trace(trace)
    rng = np.random.default_rng(_seed(task_id, "norm-noise", base_seed))
    noise = rng.standard_normal(array.shape)
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    noise_norms = np.linalg.norm(noise, axis=1, keepdims=True)
    noise = noise / np.maximum(noise_norms, 1e-12)
    return noise * norms


def covariance_matched_noise(
    trace: Any,
    covariance: Any,
    task_id: str,
    base_seed: int,
) -> np.ndarray:
    array = ensure_trace(trace)
    covariance_array = np.asarray(covariance, dtype=np.float64)
    if covariance_array.shape != (array.shape[1], array.shape[1]):
        raise ValueError("Covariance dimension does not match trace hidden size")
    eigenvalues, eigenvectors = np.linalg.eigh((covariance_array + covariance_array.T) / 2)
    root = eigenvectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0.0))) @ eigenvectors.T
    rng = np.random.default_rng(_seed(task_id, "cov-noise", base_seed))
    noise = rng.standard_normal(array.shape) @ root.T
    target_norms = np.linalg.norm(array, axis=1, keepdims=True)
    noise_norms = np.linalg.norm(noise, axis=1, keepdims=True)
    return noise / np.maximum(noise_norms, 1e-12) * target_norms


def truncate_trace(trace: Any, retained_steps: int) -> np.ndarray:
    array = ensure_trace(trace).copy()
    if retained_steps < 0 or retained_steps > array.shape[0]:
        raise ValueError("retained_steps outside valid range")
    array[retained_steps:] = 0.0
    return array


def patch_step(base_trace: Any, donor_trace: Any, step_index: int) -> np.ndarray:
    base = ensure_trace(base_trace).copy()
    donor = ensure_trace(donor_trace)
    if base.shape != donor.shape:
        raise ValueError("Trace shapes differ")
    if not 0 <= step_index < base.shape[0]:
        raise ValueError("step_index outside valid range")
    base[step_index] = donor[step_index]
    return base

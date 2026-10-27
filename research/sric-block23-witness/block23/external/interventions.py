from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def zero_trace(trace: Array) -> Array:
    return np.zeros_like(np.asarray(trace, float))


def truncate_trace(trace: Array, keep: int) -> Array:
    x = np.asarray(trace, float).copy()
    if keep < 0 or keep > len(x):
        raise ValueError(f"keep must lie in [0,{len(x)}]")
    x[keep:] = 0.0
    return x


def permute_trace(trace: Array, permutation: list[int] | tuple[int, ...]) -> Array:
    x = np.asarray(trace, float)
    p = np.asarray(permutation, dtype=int)
    if sorted(p.tolist()) != list(range(len(x))):
        raise ValueError("permutation must contain each latent-step index exactly once")
    return x[p].copy()


def norm_matched_noise(trace: Array, seed: int) -> Array:
    x = np.asarray(trace, float)
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=x.shape)
    n0 = np.linalg.norm(x, axis=1, keepdims=True)
    nn = np.maximum(np.linalg.norm(noise, axis=1, keepdims=True), 1e-12)
    return noise * (n0 / nn)


def covariance_matched_noise(trace_bank: Array, seed: int) -> Array:
    """Sample one K x D trace with per-step empirical covariance."""
    bank = np.asarray(trace_bank, float)
    if bank.ndim != 3:
        raise ValueError("trace_bank must have shape [tasks, steps, hidden]")
    rng = np.random.default_rng(seed)
    out = np.empty(bank.shape[1:], dtype=float)
    for k in range(bank.shape[1]):
        x = bank[:, k, :]
        mu = np.mean(x, axis=0)
        cov = np.cov(x, rowvar=False) + 1e-6 * np.eye(x.shape[1])
        out[k] = rng.multivariate_normal(mu, cov)
    return out

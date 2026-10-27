from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


Array = np.ndarray


def _matrix(x: Array, name: str) -> Array:
    out = np.asarray(x, dtype=np.float64)
    if out.ndim != 2:
        raise ValueError(f"{name} must be a matrix, got shape {out.shape}")
    if not np.isfinite(out).all():
        raise ValueError(f"{name} contains non-finite values")
    return out


def center(x: Array) -> tuple[Array, Array]:
    x = _matrix(x, "x")
    mean = x.mean(axis=0, keepdims=True)
    return x - mean, mean[0]


def symmetrize(a: Array) -> Array:
    a = _matrix(a, "a")
    if a.shape[0] != a.shape[1]:
        raise ValueError("a must be square")
    return 0.5 * (a + a.T)


def orthonormalize(a: Array, rank: int | None = None, tolerance: float = 1e-10) -> Array:
    a = _matrix(a, "a")
    if rank is None:
        rank = min(a.shape)
    rank = max(1, min(int(rank), a.shape[0], a.shape[1]))
    u, s, _ = np.linalg.svd(a, full_matrices=False)
    if s.size == 0 or s[0] <= 0:
        raise ValueError("cannot orthonormalize a zero matrix")
    keep = int(min(rank, np.count_nonzero(s > tolerance * s[0])))
    if keep < 1:
        raise ValueError("matrix has no numerically stable direction")
    return u[:, :keep]


def top_eigenbasis(a: Array, rank: int) -> tuple[Array, Array]:
    a = symmetrize(a)
    values, vectors = np.linalg.eigh(a)
    order = np.argsort(values)[::-1]
    rank = max(1, min(int(rank), a.shape[0]))
    order = order[:rank]
    return vectors[:, order], values[order]


def psd_sqrt(a: Array, ridge: float = 0.0) -> tuple[Array, Array]:
    a = symmetrize(a)
    values, vectors = np.linalg.eigh(a)
    scale = max(float(np.max(np.abs(values))), 1.0)
    floor = max(float(ridge), np.finfo(np.float64).eps * scale)
    values = np.maximum(values, floor)
    root = (vectors * np.sqrt(values)) @ vectors.T
    inv_root = (vectors * (1.0 / np.sqrt(values))) @ vectors.T
    return symmetrize(root), symmetrize(inv_root)


@dataclass(frozen=True)
class Whitening:
    mean: Array
    to_white: Array
    from_white: Array
    ridge: float

    def states(self, x: Array) -> Array:
        x = _matrix(x, "x")
        return (x - self.mean[None, :]) @ self.to_white.T

    def deltas(self, x: Array) -> Array:
        return _matrix(x, "x") @ self.to_white.T

    def covectors(self, rows: Array) -> Array:
        return _matrix(rows, "rows") @ self.from_white


def fit_whitening(x: Array, ridge_fraction: float = 1e-3) -> Whitening:
    xc, mean = center(x)
    covariance = (xc.T @ xc) / max(1, xc.shape[0] - 1)
    average_variance = max(float(np.trace(covariance) / covariance.shape[0]), 1e-12)
    ridge = float(ridge_fraction) * average_variance
    root, inv_root = psd_sqrt(covariance, ridge=ridge)
    return Whitening(mean=mean, to_white=inv_root, from_white=root, ridge=ridge)


def gram_from_samples(samples: Array, center_samples: bool = True) -> Array:
    samples = _matrix(samples, "samples")
    if center_samples:
        samples, _ = center(samples)
    return symmetrize((samples.T @ samples) / max(1, samples.shape[0] - 1))


def pca_basis(samples: Array, rank: int, center_samples: bool = True) -> tuple[Array, Array]:
    gram = gram_from_samples(samples, center_samples=center_samples)
    return top_eigenbasis(gram, rank)


def predictive_basis(source: Array, future_update: Array, rank: int) -> tuple[Array, Array]:
    source, _ = center(source)
    future_update, _ = center(future_update)
    if source.shape != future_update.shape:
        raise ValueError("source and future_update must have the same shape")
    cross = (source.T @ future_update) / max(1, source.shape[0] - 1)
    u, singular, _ = np.linalg.svd(cross, full_matrices=False)
    rank = max(1, min(int(rank), u.shape[1]))
    return u[:, :rank], singular[:rank]


def persistent_basis(source: Array, future: Array, rank: int, ridge_fraction: float = 1e-3) -> tuple[Array, Array]:
    source, _ = center(source)
    future, _ = center(future)
    if source.shape != future.shape:
        raise ValueError("source and future must have the same shape")
    n = max(1, source.shape[0] - 1)
    covariance = symmetrize((source.T @ source) / n)
    lag = symmetrize((source.T @ future + future.T @ source) / (2.0 * n))
    average_variance = max(float(np.trace(covariance) / covariance.shape[0]), 1e-12)
    _, inv_root = psd_sqrt(covariance, ridge=ridge_fraction * average_variance)
    whitened_lag = symmetrize(inv_root @ lag @ inv_root)
    q, values = top_eigenbasis(whitened_lag, rank)
    directions = inv_root @ q
    return orthonormalize(directions, rank), values


def balanced_basis(write_gram: Array, read_gram: Array, rank: int, ridge_fraction: float = 1e-6) -> tuple[Array, Array]:
    write_gram = symmetrize(write_gram)
    read_gram = symmetrize(read_gram)
    if write_gram.shape != read_gram.shape:
        raise ValueError("write and read Gramians must have the same shape")
    d = write_gram.shape[0]
    scale = max(float(np.trace(write_gram) / d), 1e-12)
    root, _ = psd_sqrt(write_gram, ridge=ridge_fraction * scale)
    hankel = symmetrize(root @ read_gram @ root)
    q, values = top_eigenbasis(hankel, rank)
    directions = root @ q
    return orthonormalize(directions, rank), np.sqrt(np.maximum(values, 0.0))


def projector(basis: Array) -> Array:
    basis = orthonormalize(basis, min(_matrix(basis, "basis").shape))
    return symmetrize(basis @ basis.T)


def consensus_basis(bases: Iterable[Array], rank: int) -> tuple[Array, Array]:
    bases = list(bases)
    if not bases:
        raise ValueError("at least one basis is required")
    first = _matrix(bases[0], "basis")
    aggregate = np.zeros((first.shape[0], first.shape[0]), dtype=np.float64)
    for basis in bases:
        basis = orthonormalize(basis, min(_matrix(basis, "basis").shape))
        if basis.shape[0] != first.shape[0]:
            raise ValueError("all bases must share an ambient dimension")
        aggregate += basis @ basis.T
    aggregate /= len(bases)
    return top_eigenbasis(aggregate, rank)


def overlap(a: Array, b: Array) -> float:
    a = orthonormalize(a, min(_matrix(a, "a").shape))
    b = orthonormalize(b, min(_matrix(b, "b").shape))
    denominator = max(1, min(a.shape[1], b.shape[1]))
    return float(np.linalg.norm(a.T @ b, ord="fro") ** 2 / denominator)


def adjusted_overlap(a: Array, b: Array) -> float:
    a = orthonormalize(a, min(_matrix(a, "a").shape))
    b = orthonormalize(b, min(_matrix(b, "b").shape))
    if a.shape[0] != b.shape[0]:
        raise ValueError("ambient dimensions differ")
    d = a.shape[0]
    raw_sum = float(np.linalg.norm(a.T @ b, ord="fro") ** 2)
    expected = a.shape[1] * b.shape[1] / d
    maximum = min(a.shape[1], b.shape[1])
    denominator = maximum - expected
    return float((raw_sum - expected) / denominator) if denominator > 0 else 0.0


def principal_angles_degrees(a: Array, b: Array) -> list[float]:
    a = orthonormalize(a, min(_matrix(a, "a").shape))
    b = orthonormalize(b, min(_matrix(b, "b").shape))
    singular = np.linalg.svd(a.T @ b, compute_uv=False)
    singular = np.clip(singular, 0.0, 1.0)
    return np.degrees(np.arccos(singular)).tolist()


def random_overlap_null(
    reference: Array,
    comparison_rank: int,
    replicates: int,
    seed: int,
) -> dict[str, float | list[float]]:
    reference = orthonormalize(reference, min(_matrix(reference, "reference").shape))
    d = reference.shape[0]
    comparison_rank = max(1, min(int(comparison_rank), d))
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(int(replicates)):
        random_basis, _ = np.linalg.qr(rng.normal(size=(d, comparison_rank)), mode="reduced")
        values.append(overlap(reference, random_basis))
    array = np.asarray(values)
    return {
        "mean": float(array.mean()),
        "sd": float(array.std(ddof=1)) if len(array) > 1 else 0.0,
        "q95": float(np.quantile(array, 0.95)),
        "values": values,
    }


def overlap_against_null(observed: float, null: dict[str, float | list[float]]) -> dict[str, float]:
    mean = float(null["mean"])
    sd = float(null["sd"])
    values = np.asarray(null["values"], dtype=np.float64)
    z = (observed - mean) / sd if sd > 0 else float("inf")
    p = float((1 + np.count_nonzero(values >= observed)) / (len(values) + 1))
    return {"observed": float(observed), "null_mean": mean, "null_sd": sd, "z": float(z), "p_upper": p}


def pairwise_overlap_matrix(named_bases: dict[str, Array]) -> tuple[list[str], Array]:
    names = list(named_bases)
    matrix = np.eye(len(names), dtype=np.float64)
    for i, left in enumerate(names):
        for j in range(i + 1, len(names)):
            value = overlap(named_bases[left], named_bases[names[j]])
            matrix[i, j] = matrix[j, i] = value
    return names, matrix


def projection_distance_profile(samples: Array, basis: Array) -> Array:
    samples = _matrix(samples, "samples")
    basis = orthonormalize(basis, min(_matrix(basis, "basis").shape))
    residual = samples - (samples @ basis) @ basis.T
    return np.linalg.norm(residual, axis=1)


def distance_function_rms(samples: Array, a: Array, b: Array) -> float:
    da = projection_distance_profile(samples, a)
    db = projection_distance_profile(samples, b)
    return float(np.sqrt(np.mean((da - db) ** 2)))


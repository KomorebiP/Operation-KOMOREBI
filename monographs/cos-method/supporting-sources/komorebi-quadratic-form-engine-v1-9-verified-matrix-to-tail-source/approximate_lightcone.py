from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

Array = np.ndarray


@dataclass(frozen=True)
class LightConeCertificate:
    depth: int
    actual_error_frobenius: float
    certified_error_frobenius: float
    actual_outside_cone_frobenius: float
    certified_outside_cone_frobenius: float
    phasewise_valid: bool


def _phase_slices(widths: Sequence[int]) -> list[slice]:
    widths = [int(w) for w in widths]
    if not widths or any(w <= 0 for w in widths):
        raise ValueError("phase widths must be positive")
    starts = np.cumsum([0] + widths)
    return [slice(int(starts[i]), int(starts[i + 1])) for i in range(len(widths))]


def phase_norm_vector(X: Array, widths: Sequence[int]) -> Array:
    """Return phasewise Frobenius norms of a vector or block vector."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim == 1:
        X = X[:, None]
    slices = _phase_slices(widths)
    if X.shape[0] != slices[-1].stop:
        raise ValueError("X row dimension does not match phase widths")
    return np.array([np.linalg.norm(X[sl], ord="fro") for sl in slices])


def block_transfer_matrix(H: Array, widths: Sequence[int]) -> Array:
    """B[h,g] = ||P_h H P_g||_2."""
    H = np.asarray(H, dtype=np.float64)
    slices = _phase_slices(widths)
    n = slices[-1].stop
    if H.shape != (n, n):
        raise ValueError("H must be square and match phase widths")
    q = len(slices)
    B = np.zeros((q, q), dtype=np.float64)
    for h, sh in enumerate(slices):
        for g, sg in enumerate(slices):
            B[h, g] = np.linalg.norm(H[sh, sg], ord=2)
    return B


def threshold_operator(
    H: Array,
    widths: Sequence[int],
    threshold: float,
    *,
    keep_diagonal: bool = True,
) -> tuple[Array, Array, int]:
    """Symmetrically retain phase blocks whose spectral norm exceeds threshold."""
    H = np.asarray(H, dtype=np.float64)
    slices = _phase_slices(widths)
    B = block_transfer_matrix(H, widths)
    H0 = np.zeros_like(H)
    B0 = np.zeros_like(B)
    retained_directed_off_diagonal = 0
    for h, sh in enumerate(slices):
        for g, sg in enumerate(slices):
            retain = (h == g and keep_diagonal) or B[h, g] >= threshold
            if retain:
                H0[sh, sg] = H[sh, sg]
                B0[h, g] = B[h, g]
                if h != g:
                    retained_directed_off_diagonal += 1
    return H0, B0, retained_directed_off_diagonal


def power_phase_envelope(B: Array, rho0: Array, depth: int) -> Array:
    return np.linalg.matrix_power(np.asarray(B, dtype=np.float64), int(depth)) @ np.asarray(rho0, dtype=np.float64)


def power_difference_envelope(B: Array, B0: Array, rho0: Array, depth: int) -> Array:
    depth = int(depth)
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    if depth == 0:
        return np.zeros_like(np.asarray(rho0, dtype=np.float64))
    return (
        np.linalg.matrix_power(np.asarray(B, dtype=np.float64), depth)
        - np.linalg.matrix_power(np.asarray(B0, dtype=np.float64), depth)
    ) @ np.asarray(rho0, dtype=np.float64)


def polynomial_difference_envelope(
    B: Array,
    B0: Array,
    rho0: Array,
    coefficients: Iterable[float],
) -> Array:
    """Certificate for p(H)-p(H0), p(t)=sum_j a_j t^j."""
    coeff = np.asarray(tuple(coefficients), dtype=np.float64)
    rho0 = np.asarray(rho0, dtype=np.float64)
    out = np.zeros_like(rho0)
    for j, a in enumerate(coeff):
        if j == 0 or a == 0:
            continue
        out += abs(float(a)) * power_difference_envelope(B, B0, rho0, j)
    return out


def apply_polynomial(H: Array, X: Array, coefficients: Iterable[float]) -> Array:
    coeff = np.asarray(tuple(coefficients), dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    Y = coeff[0] * X
    power = X.copy()
    for j in range(1, coeff.size):
        power = H @ power
        Y = Y + coeff[j] * power
    return Y


def certify_depth(
    H: Array,
    H0: Array,
    widths: Sequence[int],
    X: Array,
    depth: int,
    retained_graph_distance: Array,
) -> LightConeCertificate:
    B = block_transfer_matrix(H, widths)
    B0 = block_transfer_matrix(H0, widths)
    rho0 = phase_norm_vector(X, widths)
    Y = np.linalg.matrix_power(H, depth) @ X
    Y0 = np.linalg.matrix_power(H0, depth) @ X
    actual_phase_error = phase_norm_vector(Y - Y0, widths)
    certified_phase_error = power_difference_envelope(B, B0, rho0, depth)
    outside = np.asarray(retained_graph_distance) > int(depth)
    actual_phase_norm = phase_norm_vector(Y, widths)
    return LightConeCertificate(
        depth=int(depth),
        actual_error_frobenius=float(np.linalg.norm(actual_phase_error)),
        certified_error_frobenius=float(np.linalg.norm(certified_phase_error)),
        actual_outside_cone_frobenius=float(np.linalg.norm(actual_phase_norm[outside])),
        certified_outside_cone_frobenius=float(np.linalg.norm(certified_phase_error[outside])),
        phasewise_valid=bool(np.all(actual_phase_error <= certified_phase_error + 1e-12)),
    )

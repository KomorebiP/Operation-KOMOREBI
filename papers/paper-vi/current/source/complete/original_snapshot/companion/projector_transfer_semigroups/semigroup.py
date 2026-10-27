from __future__ import annotations

from collections.abc import Sequence
import numpy as np
from scipy.linalg import expm
from scipy.integrate import quad_vec

from .packets import packet_blocks


def matrix_semigroup(generator: np.ndarray, time: float) -> np.ndarray:
    return expm(time * np.asarray(generator, dtype=float))


def packet_semigroup_blocks(
    generator: np.ndarray,
    time: float,
    projectors: Sequence[np.ndarray],
) -> list[list[np.ndarray]]:
    return packet_blocks(matrix_semigroup(generator, time), projectors)


def feshbach_effective_operator(
    operator: np.ndarray,
    retained_indices: Sequence[int],
    z: complex,
) -> np.ndarray:
    """Exact Schur-Feshbach effective operator z-A on the retained coordinates."""
    a = np.asarray(operator, dtype=complex)
    n = a.shape[0]
    keep = np.array(sorted(set(retained_indices)), dtype=int)
    hidden = np.array([i for i in range(n) if i not in set(keep)], dtype=int)
    app = a[np.ix_(keep, keep)]
    if hidden.size == 0:
        return z * np.eye(len(keep)) - app
    apq = a[np.ix_(keep, hidden)]
    aqp = a[np.ix_(hidden, keep)]
    aqq = a[np.ix_(hidden, hidden)]
    return z * np.eye(len(keep)) - app - apq @ np.linalg.inv(z * np.eye(len(hidden)) - aqq) @ aqp


def projected_resolvent(
    operator: np.ndarray,
    retained_indices: Sequence[int],
    z: complex,
) -> np.ndarray:
    a = np.asarray(operator, dtype=complex)
    keep = np.array(sorted(set(retained_indices)), dtype=int)
    full = np.linalg.inv(z * np.eye(a.shape[0]) - a)
    return full[np.ix_(keep, keep)]


def memory_kernel(operator: np.ndarray, retained_indices: Sequence[int], time: float) -> np.ndarray:
    """K(t)=A_PQ exp(t A_QQ) A_QP."""
    a = np.asarray(operator, dtype=float)
    n = a.shape[0]
    keep_set = set(retained_indices)
    keep = np.array(sorted(keep_set), dtype=int)
    hidden = np.array([i for i in range(n) if i not in keep_set], dtype=int)
    if hidden.size == 0:
        return np.zeros((len(keep), len(keep)))
    apq = a[np.ix_(keep, hidden)]
    aqp = a[np.ix_(hidden, keep)]
    aqq = a[np.ix_(hidden, hidden)]
    return apq @ expm(time * aqq) @ aqp


def memory_kernel_laplace(
    operator: np.ndarray,
    retained_indices: Sequence[int],
    z: float,
) -> np.ndarray:
    if z <= 0:
        raise ValueError("positive Laplace parameter required")
    a = np.asarray(operator, dtype=float)
    n = a.shape[0]
    keep_set = set(retained_indices)
    keep = np.array(sorted(keep_set), dtype=int)
    hidden = np.array([i for i in range(n) if i not in keep_set], dtype=int)
    if hidden.size == 0:
        return np.zeros((len(keep), len(keep)))
    apq = a[np.ix_(keep, hidden)]
    aqp = a[np.ix_(hidden, keep)]
    aqq = a[np.ix_(hidden, hidden)]
    return apq @ np.linalg.inv(z * np.eye(len(hidden)) - aqq) @ aqp


def numerical_memory_laplace(
    operator: np.ndarray,
    retained_indices: Sequence[int],
    z: float,
    upper: float = 80.0,
) -> np.ndarray:
    integrand = lambda t: np.exp(-z * t) * memory_kernel(operator, retained_indices, float(t))
    value, _ = quad_vec(integrand, 0.0, upper, epsabs=1e-11, epsrel=1e-11)
    return np.asarray(value)


def generator_refinement_defect(coarsener: np.ndarray, fine: np.ndarray, coarse: np.ndarray) -> np.ndarray:
    return np.asarray(coarsener) @ np.asarray(fine) - np.asarray(coarse) @ np.asarray(coarsener)


def semigroup_refinement_residual(
    coarsener: np.ndarray,
    fine: np.ndarray,
    coarse: np.ndarray,
    time: float,
) -> np.ndarray:
    return coarsener @ expm(time * fine) - expm(time * coarse) @ coarsener


def duhamel_defect_integral(
    coarsener: np.ndarray,
    fine: np.ndarray,
    coarse: np.ndarray,
    time: float,
) -> np.ndarray:
    defect = generator_refinement_defect(coarsener, fine, coarse)
    integrand = lambda s: expm((time - float(s)) * coarse) @ defect @ expm(float(s) * fine)
    value, _ = quad_vec(integrand, 0.0, time, epsabs=1e-11, epsrel=1e-11)
    return np.asarray(value)

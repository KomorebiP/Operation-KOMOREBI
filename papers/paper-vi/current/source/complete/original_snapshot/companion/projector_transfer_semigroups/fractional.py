from __future__ import annotations

import numpy as np
from scipy.integrate import quad


def _symmetric_eigendecomposition(operator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(operator, dtype=float)
    if np.linalg.norm(a - a.T) > 1e-10:
        raise ValueError("symmetric operator required")
    values, vectors = np.linalg.eigh(a)
    if np.min(values) < -1e-10:
        raise ValueError("positive semidefinite operator required")
    return np.maximum(values, 0.0), vectors


def spectral_fractional_power(operator: np.ndarray, alpha: float) -> np.ndarray:
    if alpha < 0:
        raise ValueError("nonnegative alpha required for semidefinite operators")
    values, vectors = _symmetric_eigendecomposition(operator)
    powered = np.where(values == 0.0, 0.0 if alpha > 0 else 1.0, values**alpha)
    return (vectors * powered) @ vectors.T


def fractional_semigroup(operator: np.ndarray, alpha: float, time: float) -> np.ndarray:
    values, vectors = _symmetric_eigendecomposition(operator)
    factors = np.exp(-float(time) * values**alpha)
    return (vectors * factors) @ vectors.T


def scalar_square_root_subordination(eigenvalue: float, time: float) -> float:
    """Poisson subordination integral for exp(-t sqrt(lambda))."""
    if eigenvalue < 0 or time <= 0:
        raise ValueError("lambda >= 0 and time > 0 required")
    if eigenvalue == 0:
        return 1.0
    constant = time / (2.0 * np.sqrt(np.pi))

    # Substitute s = exp(u) to integrate over the whole real line stably.
    def integrand(u: float) -> float:
        s = np.exp(u)
        return constant * s ** (-0.5) * np.exp(-time * time / (4.0 * s) - eigenvalue * s)

    value, _ = quad(integrand, -30.0, 20.0, epsabs=1e-12, epsrel=1e-12, limit=500)
    return float(value)


def fractional_intertwining_defect(
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    coarsener: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Return C A^alpha - B^alpha C for positive semidefinite matrices.

    ``fine_operator`` is A on the fine space, ``coarse_operator`` is B on
    the coarse space, and ``coarsener`` is the rectangular map C.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    a = np.asarray(fine_operator, dtype=float)
    b = np.asarray(coarse_operator, dtype=float)
    c = np.asarray(coarsener, dtype=float)
    if c.shape != (b.shape[0], a.shape[0]):
        raise ValueError("coarsener shape must be (coarse dimension, fine dimension)")
    return c @ spectral_fractional_power(a, alpha) - spectral_fractional_power(b, alpha) @ c


def generator_intertwining_defect(
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    coarsener: np.ndarray,
) -> np.ndarray:
    """Return the first-order refinement defect C A - B C."""
    a = np.asarray(fine_operator, dtype=float)
    b = np.asarray(coarse_operator, dtype=float)
    c = np.asarray(coarsener, dtype=float)
    if c.shape != (b.shape[0], a.shape[0]):
        raise ValueError("coarsener shape must be (coarse dimension, fine dimension)")
    return c @ a - b @ c


def fractional_holder_bound(
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    coarsener: np.ndarray,
    alpha: float,
) -> float:
    r"""Hölder-type bound for the fractional intertwining defect.

    For positive semidefinite A and B and D = C A - B C,

        ||C A^alpha - B^alpha C||
        <= K_alpha ||C||^(1-alpha) ||D||^alpha,

    where K_alpha = 2^(1-alpha) sin(pi alpha) /
    (pi alpha (1-alpha)).  The spectral norm is used.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    a = np.asarray(fine_operator, dtype=float)
    b = np.asarray(coarse_operator, dtype=float)
    c = np.asarray(coarsener, dtype=float)
    # Validate positivity through the same helper used by the functional calculus.
    _symmetric_eigendecomposition(a)
    _symmetric_eigendecomposition(b)
    d = generator_intertwining_defect(a, b, c)
    c_norm = float(np.linalg.norm(c, 2))
    d_norm = float(np.linalg.norm(d, 2))
    if c_norm == 0.0 or d_norm == 0.0:
        return 0.0
    constant = (
        2.0 ** (1.0 - alpha)
        * np.sin(np.pi * alpha)
        / (np.pi * alpha * (1.0 - alpha))
    )
    return float(constant * c_norm ** (1.0 - alpha) * d_norm**alpha)


def fractional_gap_bound(
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    coarsener: np.ndarray,
    alpha: float,
) -> float:
    r"""Linear defect bound under a common positive spectral gap.

    If A,B >= m I with m>0, then

        ||C A^alpha - B^alpha C|| <= alpha m^(alpha-1) ||C A - B C||.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    a_values, _ = _symmetric_eigendecomposition(fine_operator)
    b_values, _ = _symmetric_eigendecomposition(coarse_operator)
    gap = float(min(np.min(a_values), np.min(b_values)))
    if gap <= 0.0:
        raise ValueError("a strictly positive common spectral gap is required")
    defect = generator_intertwining_defect(fine_operator, coarse_operator, coarsener)
    return float(alpha * gap ** (alpha - 1.0) * np.linalg.norm(defect, 2))


def fractional_semigroup_intertwining_defect(
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    coarsener: np.ndarray,
    alpha: float,
    time: float,
) -> np.ndarray:
    """Return C exp(-t A^alpha) - exp(-t B^alpha) C."""
    if time < 0.0:
        raise ValueError("time must be nonnegative")
    a = np.asarray(fine_operator, dtype=float)
    b = np.asarray(coarse_operator, dtype=float)
    c = np.asarray(coarsener, dtype=float)
    if c.shape != (b.shape[0], a.shape[0]):
        raise ValueError("coarsener shape must be (coarse dimension, fine dimension)")
    return c @ fractional_semigroup(a, alpha, time) - fractional_semigroup(b, alpha, time) @ c


def fractional_semigroup_bound(
    fine_operator: np.ndarray,
    coarse_operator: np.ndarray,
    coarsener: np.ndarray,
    alpha: float,
    time: float,
    *,
    use_gap: bool = False,
) -> float:
    """Duhamel bound for the fractional semigroup refinement defect."""
    if time < 0.0:
        raise ValueError("time must be nonnegative")
    if use_gap:
        a_values, _ = _symmetric_eigendecomposition(fine_operator)
        b_values, _ = _symmetric_eigendecomposition(coarse_operator)
        gap = float(min(np.min(a_values), np.min(b_values)))
        if gap <= 0.0:
            raise ValueError("a strictly positive common spectral gap is required")
        base = fractional_gap_bound(
            fine_operator, coarse_operator, coarsener, alpha
        )
        return float(time * np.exp(-time * gap**alpha) * base)
    base = fractional_holder_bound(
        fine_operator, coarse_operator, coarsener, alpha
    )
    return float(time * base)

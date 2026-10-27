from __future__ import annotations

import numpy as np
from scipy.linalg import expm

Array = np.ndarray


def cycle_laplacian(size: int, spacing: float | None = None) -> Array:
    if size < 3:
        raise ValueError("cycle needs at least three vertices")
    h = (2 * np.pi / size) if spacing is None else spacing
    l = np.zeros((size, size), dtype=float)
    for i in range(size):
        l[i, i] = 2
        l[i, (i - 1) % size] = -1
        l[i, (i + 1) % size] = -1
    return l / h**2


def cycle_eigenvalues(size: int, spacing: float | None = None) -> np.ndarray:
    h = (2 * np.pi / size) if spacing is None else spacing
    k = np.arange(size)
    return 4 * np.sin(np.pi * k / size) ** 2 / h**2


def torus_eigenvalues(side: int, dimension: int = 2, spacing: float | None = None) -> np.ndarray:
    if side < 3 or dimension < 1:
        raise ValueError("invalid torus")
    h = (2 * np.pi / side) if spacing is None else spacing
    one = 4 * np.sin(np.pi * np.arange(side) / side) ** 2 / h**2
    grids = np.meshgrid(*([one] * dimension), indexing="ij")
    values = sum(grids)
    return np.asarray(values).ravel()


def heat_trace(eigenvalues: np.ndarray, tau: np.ndarray | float, normalized: bool = True) -> np.ndarray:
    lam = np.asarray(eigenvalues, dtype=float)
    t = np.atleast_1d(np.asarray(tau, dtype=float))
    values = np.array([np.sum(np.exp(-x * lam)) for x in t])
    if normalized:
        values = values / lam.size
    return values


def spectral_dimension(eigenvalues: np.ndarray, tau: np.ndarray) -> np.ndarray:
    t = np.asarray(tau, dtype=float)
    p = heat_trace(eigenvalues, t, normalized=True)
    return -2 * np.gradient(np.log(p), np.log(t))


def low_mode_error_bound(mode: int, spacing: float) -> tuple[float, float]:
    k = float(mode)
    discrete = 4 * np.sin(k * spacing / 2) ** 2 / spacing**2
    exact_error = k**2 - discrete
    bound = k**4 * spacing**2 / 12
    return float(exact_error), float(bound)


def causal_volume_hamiltonian(size: int, kappa: float = 1.0, center: float | None = None, confinement: float = 0.015) -> Array:
    """Finite volume-state toy Hamiltonian.

    The model is a one-dimensional nearest-neighbor kinetic term plus a confining
    potential.  It is only a controlled transfer-matrix test, not a discretization
    derived from a gravitational path integral.
    """
    if size < 4:
        raise ValueError("size too small")
    c = (size + 1) / 2 if center is None else center
    h = np.zeros((size, size), dtype=float)
    for i in range(size):
        n = i + 1
        h[i, i] = 2 * kappa + confinement * (n - c) ** 2
        if i + 1 < size:
            h[i, i + 1] = h[i + 1, i] = -kappa
    return h


def euclidean_transfer(hamiltonian: Array, tau: float, shift_ground: bool = True) -> Array:
    h = np.asarray(hamiltonian, dtype=float)
    if shift_ground:
        h = h - np.min(np.linalg.eigvalsh(h)) * np.eye(h.shape[0])
    return expm(-tau * h)

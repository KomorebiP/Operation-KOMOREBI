from __future__ import annotations

import numpy as np
import sympy as sp

from .core import matrix_units
from .graphs import cycle_adjacency, path_adjacency


def companion_matrix(coefficients: list[int | float]) -> sp.Matrix:
    """Companion matrix of x^n + c_{n-1}x^(n-1)+...+c_0.

    Coefficients are supplied [c_0,...,c_{n-1}].
    """
    n = len(coefficients)
    if n < 1:
        raise ValueError("at least one coefficient is required")
    c = sp.zeros(n)
    for i in range(n - 1):
        c[i + 1, i] = 1
    for i, value in enumerate(coefficients):
        c[i, n - 1] = -sp.sympify(value)
    return c


def repeated_jordan_operator(block_sizes: list[int], eigenvalue: int = 0) -> sp.Matrix:
    blocks = []
    for size in block_sizes:
        block = sp.eye(size) * eigenvalue
        for i in range(size - 1):
            block[i, i + 1] = 1
        blocks.append(block)
    return sp.diag(*blocks)


def coordinate_projectors(n: int, groups: list[list[int]]) -> list[np.ndarray]:
    projectors = []
    covered: set[int] = set()
    for group in groups:
        p = np.zeros((n, n), dtype=complex)
        for i in group:
            if i in covered or i < 0 or i >= n:
                raise ValueError("groups must be a disjoint partition of coordinates")
            covered.add(i)
            p[i, i] = 1
        projectors.append(p)
    if covered != set(range(n)):
        raise ValueError("groups must cover every coordinate")
    return projectors


def bilateral_shift_matrix(n: int) -> np.ndarray:
    s = np.zeros((n, n), dtype=complex)
    for j in range(n):
        s[(j + 1) % n, j] = 1
    return s


def residue_projectors(n: int, modulus: int) -> list[np.ndarray]:
    if n % modulus:
        raise ValueError("for this finite cyclic model, modulus must divide n")
    groups = [[i for i in range(n) if i % modulus == r] for r in range(modulus)]
    return coordinate_projectors(n, groups)


def full_matrix_orbit_dimension(seed: np.ndarray) -> int:
    seed = np.asarray(seed, dtype=complex).reshape(-1)
    units = matrix_units(seed.size)
    orbit = np.column_stack([u @ seed for u in units])
    return int(np.linalg.matrix_rank(orbit, tol=1e-10))

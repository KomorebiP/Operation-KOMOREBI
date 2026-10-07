from __future__ import annotations

import numpy as np
import sympy as sp


def path_adjacency(n: int) -> sp.Matrix:
    if n < 1:
        raise ValueError("n must be positive")
    a = sp.zeros(n)
    for i in range(n - 1):
        a[i, i + 1] = 1
        a[i + 1, i] = 1
    return a


def cycle_adjacency(n: int) -> sp.Matrix:
    if n < 3:
        raise ValueError("a simple cycle requires n >= 3")
    a = path_adjacency(n)
    a[0, n - 1] = 1
    a[n - 1, 0] = 1
    return a


def symmetric_graph_seed_rank(adjacency: sp.Matrix) -> int:
    """Seed count for a real symmetric adjacency matrix, over the complex field.

    This uses the classical spectral theorem and SymPy's eigenvalue routine,
    not a formally verified eigensolver. Use exact entries for exact checks.
    Complex symmetry alone does not imply diagonalizability.
    """
    if adjacency.rows != adjacency.cols or adjacency != adjacency.T:
        raise ValueError("adjacency matrix must be symmetric")
    if any(entry.is_real is not True for entry in adjacency):
        raise ValueError("the spectral shortcut requires proven-real entries")
    return max(adjacency.eigenvals().values(), default=0)


def endpoint_krylov_determinant_path(n: int) -> sp.Expr:
    a = path_adjacency(n)
    e0 = sp.zeros(n, 1)
    e0[0, 0] = 1
    columns = []
    current = e0
    for _ in range(n):
        columns.append(current)
        current = a * current
    return sp.factor(sp.Matrix.hstack(*columns).det())

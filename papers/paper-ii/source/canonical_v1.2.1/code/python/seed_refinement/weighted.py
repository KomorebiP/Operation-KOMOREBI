from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
from typing import Iterable, Sequence

import numpy as np
import sympy as sp


def _require_prime(prime: int) -> int:
    if isinstance(prime, bool) or not isinstance(prime, Integral) or not sp.isprime(int(prime)):
        raise ValueError("prime must be a prime integer")
    return int(prime)


def _require_depth(depth: int) -> int:
    if isinstance(depth, bool) or not isinstance(depth, Integral) or depth < 1:
        raise ValueError("depth must be a positive integer")
    return int(depth)


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    weight: int
    multiplicity: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.weight, bool) or not isinstance(self.weight, Integral) or self.weight < 1:
            raise ValueError("edge weight must be a positive integer")
        if (
            isinstance(self.multiplicity, bool)
            or not isinstance(self.multiplicity, Integral)
            or self.multiplicity < 1
        ):
            raise ValueError("multiplicity must be a positive integer")


def weighted_adjacency(num_vertices: int, edges: Sequence[Edge], variable: sp.Symbol | None = None) -> sp.Matrix:
    if num_vertices < 1:
        raise ValueError("num_vertices must be positive")
    t = variable or sp.Symbol("t")
    matrix = sp.zeros(num_vertices)
    for edge in edges:
        if not (0 <= edge.source < num_vertices and 0 <= edge.target < num_vertices):
            raise ValueError("edge endpoint out of range")
        matrix[edge.source, edge.target] += edge.multiplicity * t ** edge.weight
    return matrix


def path_zeta(
    num_vertices: int,
    edges: Sequence[Edge],
    starts: Sequence[int],
    targets: Sequence[int],
    variable: sp.Symbol | None = None,
) -> sp.Expr:
    if any(index < 0 or index >= num_vertices for index in (*starts, *targets)):
        raise ValueError("start and target vertices must be in range")
    t = variable or sp.Symbol("t")
    adjacency = weighted_adjacency(num_vertices, edges, t)
    u = sp.zeros(num_vertices, 1)
    v = sp.zeros(num_vertices, 1)
    for index in starts:
        u[index, 0] += 1
    for index in targets:
        v[index, 0] += 1
    return sp.factor((u.T * (sp.eye(num_vertices) - adjacency).inv() * v)[0])


def path_counts(
    num_vertices: int,
    edges: Sequence[Edge],
    starts: Sequence[int],
    targets: Sequence[int],
    max_weight: int,
) -> list[int]:
    if num_vertices < 1:
        raise ValueError("num_vertices must be positive")
    if max_weight < 0:
        raise ValueError("max_weight must be nonnegative")
    if any(index < 0 or index >= num_vertices for index in (*starts, *targets)):
        raise ValueError("start and target vertices must be in range")
    if any(
        edge.source < 0 or edge.source >= num_vertices
        or edge.target < 0 or edge.target >= num_vertices
        for edge in edges
    ):
        raise ValueError("edge endpoint out of range")
    # dp[w,vertex] counts walks ending at vertex with total weight w.
    dp = np.zeros((max_weight + 1, num_vertices), dtype=object)
    for source in starts:
        dp[0, source] += 1
    for weight in range(max_weight + 1):
        for edge in edges:
            if weight + edge.weight <= max_weight:
                dp[weight + edge.weight, edge.target] += dp[weight, edge.source] * edge.multiplicity
    return [int(sum(dp[w, target] for target in targets)) for w in range(max_weight + 1)]


def _matrix_mod(matrix: np.ndarray, modulus: int) -> np.ndarray:
    return np.asarray(matrix, dtype=object) % modulus


def _matmul_mod(a: np.ndarray, b: np.ndarray, modulus: int) -> np.ndarray:
    return (np.asarray(a, dtype=object) @ np.asarray(b, dtype=object)) % modulus


def _identity(size: int) -> np.ndarray:
    return np.eye(size, dtype=object)


def inverse_mod_matrix(matrix: np.ndarray, modulus: int) -> np.ndarray:
    M = sp.Matrix([[int(value) % modulus for value in row] for row in np.asarray(matrix)])
    inv = M.inv_mod(modulus)
    return np.array(inv.tolist(), dtype=object) % modulus


def direct_inverse_mod(diagonal: np.ndarray, transfer: np.ndarray, prime: int, depth: int) -> np.ndarray:
    """Invert ``diagonal + transfer`` modulo a genuine prime power."""
    prime = _require_prime(prime)
    depth = _require_depth(depth)
    modulus = prime**depth
    return inverse_mod_matrix(_matrix_mod(diagonal + transfer, modulus), modulus)


def neumann_inverse_mod(
    diagonal: np.ndarray,
    transfer: np.ndarray,
    prime: int,
    depth: int,
    max_terms: int | None = None,
) -> np.ndarray:
    """Filtered inverse of D+K modulo p^depth.

    The caller must provide a transfer K whose entries are divisible by p.  D must
    be invertible modulo p^depth.  The sum terminates when the next power of
    A=D^{-1}K vanishes modulo p^depth.
    """
    prime = _require_prime(prime)
    depth = _require_depth(depth)
    if max_terms is not None and (
        isinstance(max_terms, bool)
        or not isinstance(max_terms, Integral)
        or max_terms < 1
    ):
        raise ValueError("max_terms must be a positive integer when supplied")
    modulus = prime**depth
    D = _matrix_mod(diagonal, modulus)
    K = _matrix_mod(transfer, modulus)
    if any(int(value) % prime for value in K.flat):
        raise ValueError("transfer must raise the p-adic filtration")
    D_inv = inverse_mod_matrix(D, modulus)
    A = _matmul_mod(D_inv, K, modulus)
    size = D.shape[0]
    total = _identity(size)
    power = _identity(size)
    sign = -1
    limit = max_terms if max_terms is not None else depth * size * 4 + 8
    for _ in range(1, limit + 1):
        power = _matmul_mod(power, A, modulus)
        if not np.any(power % modulus):
            break
        total = (total + sign * power) % modulus
        sign *= -1
    else:
        raise ArithmeticError("filtered Neumann series did not terminate within the safety limit")
    return _matmul_mod(total, D_inv, modulus)


def zeta_coefficients(expr: sp.Expr, variable: sp.Symbol, max_degree: int) -> list[int]:
    series = sp.series(expr, variable, 0, max_degree + 1).removeO().expand()
    return [int(series.coeff(variable, degree)) for degree in range(max_degree + 1)]

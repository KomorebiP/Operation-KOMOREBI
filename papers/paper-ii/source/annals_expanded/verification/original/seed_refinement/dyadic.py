from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Sequence

import numpy as np
import sympy as sp


def valuation(integer: int, prime: int) -> int:
    if prime < 2:
        raise ValueError("prime must be at least two")
    if integer == 0:
        raise ValueError("valuation of zero is not finite")
    value = abs(integer)
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def resultant_weight(f: sp.Poly, g: sp.Poly, prime: int) -> tuple[int, int]:
    if f.gens != g.gens:
        raise ValueError("polynomials must use the same variable")
    resultant = int(sp.resultant(f.as_expr(), g.as_expr(), f.gens[0]))
    return resultant, valuation(resultant, prime)


def delayed_separation_example() -> dict[str, object]:
    """The integral matrix A=[[1,1],[0,-1]] and its rational sign projectors."""
    A = sp.Matrix([[1, 1], [0, -1]])
    I = sp.eye(2)
    plus = sp.simplify((I + A) / 2)
    minus = sp.simplify((I - A) / 2)
    return {
        "matrix": A,
        "plus": plus,
        "minus": minus,
        "scaled_plus": sp.simplify(2 * plus),
        "scaled_minus": sp.simplify(2 * minus),
        "plus_idempotent": sp.simplify(plus * plus - plus) == sp.zeros(2),
        "minus_idempotent": sp.simplify(minus * minus - minus) == sp.zeros(2),
        "orthogonal": sp.simplify(plus * minus) == sp.zeros(2),
    }


@dataclass(frozen=True)
class SmithSolveResult:
    solvable: bool
    solution_count: int
    coordinate_counts: tuple[int, ...]


def smith_diagonal_solve(
    weights: Sequence[int],
    transformed_rhs: Sequence[int],
    prime: int,
    depth: int,
) -> SmithSolveResult:
    """Solve diag(p^s_i) x = b modulo p^depth.

    Each coordinate is independent.  A coordinate is solvable exactly when b_i is
    divisible by p^min(s_i,depth), and then has p^min(s_i,depth) solutions.
    """
    if len(weights) != len(transformed_rhs):
        raise ValueError("weights and right-hand side must have the same length")
    modulus = prime**depth
    counts: list[int] = []
    for s, b in zip(weights, transformed_rhs, strict=True):
        if s < 0:
            raise ValueError("Smith weights must be nonnegative")
        required = prime ** min(s, depth)
        if b % required:
            return SmithSolveResult(False, 0, tuple())
        counts.append(required)
    total = 1
    for count in counts:
        total *= count
    return SmithSolveResult(True, total, tuple(counts))


def odd_prime_sign_projectors(matrix: np.ndarray, prime: int) -> tuple[np.ndarray, np.ndarray]:
    if prime == 2:
        raise ValueError("two is not invertible in the dyadic residue ring")
    inv2 = pow(2, -1, prime)
    A = np.asarray(matrix, dtype=int) % prime
    I = np.eye(A.shape[0], dtype=int)
    return ((I + A) * inv2) % prime, ((I - A) * inv2) % prime

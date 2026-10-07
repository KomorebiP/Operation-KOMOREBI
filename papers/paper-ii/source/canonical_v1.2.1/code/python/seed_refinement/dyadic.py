from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from numbers import Integral
from typing import Sequence

import numpy as np
import sympy as sp


def _require_prime(prime: int) -> int:
    """Return ``prime`` as an ``int`` after checking primality.

    The algorithms in this module are stated over prime-power residue rings.
    Accepting a merely positive modulus would silently change their meaning.
    """
    if isinstance(prime, bool) or not isinstance(prime, Integral) or not sp.isprime(int(prime)):
        raise ValueError("prime must be a prime integer")
    return int(prime)


def _require_positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def valuation(integer: int, prime: int) -> int:
    """Return the exponent of the prime ``prime`` in a nonzero integer."""
    prime = _require_prime(prime)
    if isinstance(integer, bool) or not isinstance(integer, Integral):
        raise ValueError("integer must be an integer")
    if integer == 0:
        raise ValueError("valuation of zero is not finite")
    value = abs(int(integer))
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
    prime = _require_prime(prime)
    depth = _require_positive_integer(depth, "depth")
    modulus = prime**depth
    counts: list[int] = []
    for s, b in zip(weights, transformed_rhs, strict=True):
        if isinstance(s, bool) or not isinstance(s, Integral) or s < 0:
            raise ValueError("Smith weights must be nonnegative")
        if isinstance(b, bool) or not isinstance(b, Integral):
            raise ValueError("right-hand side entries must be integers")
        s = int(s)
        b = int(b)
        required = prime ** min(s, depth)
        if b % required:
            return SmithSolveResult(False, 0, tuple())
        counts.append(required)
    total = 1
    for count in counts:
        total *= count
    return SmithSolveResult(True, total, tuple(counts))


def odd_prime_sign_projectors(matrix: np.ndarray, prime: int) -> tuple[np.ndarray, np.ndarray]:
    """Return the sign projectors of an involution over ``Z / prime Z``.

    The formula ``(I +/- A)/2`` defines projectors only when ``A^2 = I``.
    Accordingly, this routine validates both that ``prime`` is an odd prime and
    that the supplied square integral matrix is an involution modulo ``prime``.
    """
    prime = _require_prime(prime)
    if prime == 2:
        raise ValueError("prime must be odd because two must be invertible")
    inv2 = pow(2, -1, prime)
    raw = np.asarray(matrix)
    if raw.ndim != 2 or raw.shape[0] != raw.shape[1]:
        raise ValueError("matrix must be square")
    if any(isinstance(value, bool) or not isinstance(value, Integral) for value in raw.flat):
        raise ValueError("matrix entries must be integers")
    A = np.asarray(matrix, dtype=object) % prime
    I = np.eye(A.shape[0], dtype=object)
    if np.any((A @ A - I) % prime):
        raise ValueError("matrix must be an involution modulo prime")
    return ((I + A) * inv2) % prime, ((I - A) * inv2) % prime

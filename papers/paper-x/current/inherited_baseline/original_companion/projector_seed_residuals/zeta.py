from __future__ import annotations

from fractions import Fraction
from math import ceil, log
from typing import Iterable, Sequence

import sympy as sp


def smooth_count(q: int, dimension: int, depth: int) -> int:
    """Maps O[[t_1,...,t_d]] -> O/pi^depth with each t_i in the maximal ideal."""
    if q < 2 or dimension < 0 or depth < 1:
        raise ValueError("invalid parameters")
    return q ** (dimension * (depth - 1))


def weighted_count(q: int, weights: Sequence[int], depth: int) -> int:
    """Count coordinates constrained by t_i in pi^{weights[i]} O/pi^depth."""
    if q < 2 or depth < 1 or any(w < 1 for w in weights):
        raise ValueError("invalid parameters")
    exponent = sum(max(depth - int(w), 0) for w in weights)
    return q**exponent


def weighted_zeta_expression(q: int, weights: Sequence[int]) -> sp.Expr:
    """Exact rational generating function sum_{L>=1} count(L) T^L."""
    if q < 2 or any(w < 1 for w in weights):
        raise ValueError("invalid parameters")
    T = sp.Symbol("T")
    if not weights:
        return T / (1 - T)
    ws = sorted(int(w) for w in weights)
    max_w = ws[-1]
    finite = sum(weighted_count(q, ws, L) * T**L for L in range(1, max_w + 1))
    dimension = len(ws)
    total_weight = sum(ws)
    tail_start = max_w + 1
    tail_coefficient = q ** (dimension * tail_start - total_weight)
    tail = tail_coefficient * T**tail_start / (1 - q**dimension * T)
    return sp.factor(sp.together(finite + tail))


def singular_power_count(p: int, exponent: int, depth: int) -> int:
    """Number of x mod p^depth satisfying x^exponent == 0 mod p^depth."""
    if p < 2 or exponent < 1 or depth < 1:
        raise ValueError("invalid parameters")
    required_valuation = ceil(depth / exponent)
    return p ** (depth - required_valuation)


def singular_square_zeta_expression(p: int) -> sp.Expr:
    T = sp.Symbol("T")
    return sp.factor((T + p * T**2) / (1 - p * T**2))


def exact_singular_dimension(exponent: int) -> Fraction:
    if exponent < 1:
        raise ValueError("exponent must be positive")
    return Fraction(exponent - 1, exponent)


def estimated_seed_dimension(counts: Sequence[int], q: int, depths: Sequence[int] | None = None) -> float:
    if q < 2 or not counts:
        raise ValueError("invalid input")
    if depths is None:
        depths = list(range(1, len(counts) + 1))
    if len(depths) != len(counts):
        raise ValueError("depth/count mismatch")
    # Least-squares slope of log_q(count) against depth.
    xs = [float(x) for x in depths]
    ys = [log(max(int(c), 1), q) for c in counts]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys, strict=True)) / denom

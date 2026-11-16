"""Exact sequence families recovered from the Komorebi OEIS 1.0.0 work.

Generic Hurwitz series, recurrence jumps, and classical families already live
in other package domains. These views retain the archive's normalization while
using the existing lazy sequence and recurrence objects.
"""
from __future__ import annotations

from math import comb

from .._number_theory import require_integer
from ..arithmetic.recurrence import LinearRecurrence
from ..exceptions import ValidationError
from .base import Sequence


def _nonnegative(value: int, name: str) -> int:
    integer = require_integer(value, name=name)
    if integer < 0:
        raise ValidationError(f"{name} must be nonnegative")
    return integer


def _spacing(value: int) -> int:
    spacing = require_integer(value, name="spacing")
    if spacing < 1:
        raise ValidationError("spacing must be positive")
    return spacing


def universal_denominator_coefficients(spacing: int, degree: int) -> tuple[int, ...]:
    """Return dense EGF coefficients of D_N(t) through ``degree`` inclusive.

    ``D_N(t) = sum_q (-1)**q * t**(N*q)/(N*q)!``. Entries are the
    coefficients multiplying ``t**j/j!``, not ordinary Taylor coefficients.
    """
    step = _spacing(spacing)
    last = _nonnegative(degree, "degree")
    return tuple((-1) ** (index // step) if index % step == 0 else 0
                 for index in range(last + 1))


def reciprocal_sequence(spacing: int, *, power: int = 1) -> Sequence:
    """Return A_N^[r](n) with D_N(t)^(-r)=sum_n A(n)t^(N*n)/(N*n)!.

    ``N >= 1`` and ``r >= 0`` are exact integers. Power zero is the identity
    sequence ``(1,0,0,...)``. The compressed Hurwitz inversion recurrence
    retains Python integer arithmetic and avoids filling the zero residue lanes.
    """
    step = _spacing(spacing)
    exponent = _nonnegative(power, "power")
    rows = [[1] for _ in range(exponent + 1)]

    def evaluate(index: int) -> int:
        while len(rows[0]) <= index:
            n = len(rows[0])
            rows[0].append(0)
            weights = tuple((-1) ** q * comb(step * n, step * q) for q in range(1, n + 1))
            for r in range(1, exponent + 1):
                rows[r].append(rows[r - 1][n] - sum(
                    weights[q - 1] * rows[r][n - q] for q in range(1, n + 1)))
        return rows[exponent][index]

    return Sequence(evaluate, name=f"reciprocal D_{step} power {exponent}",
                    metadata={"spacing": step, "power": exponent,
                              "normalization": "t^(N*n)/(N*n)!",
                              "source_release": "Komorebi OEIS 1.0.0"})


def reciprocal_coefficients(spacing: int, count: int, *, power: int = 1) -> tuple[int, ...]:
    """Return exactly ``count`` compressed reciprocal coefficients from index zero."""
    total = _nonnegative(count, "count")
    return reciprocal_sequence(spacing, power=power).first(total)


def kbonacci_sequence(order: int) -> Sequence:
    """Return T(n;k), with k-1 initial zeros followed by one, then k-term sums."""
    k = require_integer(order, name="order")
    if k < 2:
        raise ValidationError("order must be at least two")
    recurrence = LinearRecurrence((1,) * k, (0,) * (k - 1) + (1,), name=f"{k}-bonacci")
    return Sequence(recurrence.term, name=recurrence.name,
                    metadata={"recurrence": recurrence, "recurrence_certified": True,
                              "initial_nonzero_index": k - 1})


def kbonacci_closed_form(order: int, index: int) -> int:
    """Return T(n;k) by the archive's finite binomial formula.

    For s=n-(k-1), sum over 0<=r<=floor(s/(k+1)) of
    (-1)^r [2^(s-(k+1)r) C(s-kr,r) - 2^(s-(k+1)r-1) C(s-kr-1,r)],
    with the second term omitted when its exponent would be negative.
    """
    k = require_integer(order, name="order")
    n = _nonnegative(index, "index")
    if k < 2:
        raise ValidationError("order must be at least two")
    if n < k - 1:
        return 0
    s = n - (k - 1)
    total = 0
    for r in range(s // (k + 1) + 1):
        h = s - (k + 1) * r
        first = (1 << h) * comb(s - k * r, r)
        second = (1 << (h - 1)) * comb(s - k * r - 1, r) if h else 0
        total += (-1) ** r * (first - second)
    return total


def fubini_sequence() -> Sequence:
    """Return ordered Bell numbers sum_k k! S(n,k), starting with one."""
    values = [1]

    def evaluate(index: int) -> int:
        while len(values) <= index:
            n = len(values)
            values.append(sum(comb(n, k) * values[n - k] for k in range(1, n + 1)))
        return values[index]

    return Sequence(evaluate, name="Fubini / ordered Bell")


def derangement_sequence() -> Sequence:
    """Return subfactorials D_0=1, D_1=0, D_n=(n-1)(D_(n-1)+D_(n-2))."""
    values = [1, 0]

    def evaluate(index: int) -> int:
        while len(values) <= index:
            n = len(values)
            values.append((n - 1) * (values[-1] + values[-2]))
        return values[index]

    return Sequence(evaluate, name="derangements")


__all__ = ["universal_denominator_coefficients", "reciprocal_sequence", "reciprocal_coefficients",
           "kbonacci_sequence", "kbonacci_closed_form", "fubini_sequence", "derangement_sequence"]

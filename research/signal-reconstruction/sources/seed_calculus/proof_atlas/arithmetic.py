from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product

import sympy as sp


@dataclass(frozen=True)
class ArithmeticCertificate:
    sequence: tuple[sp.Integer, ...]
    recurrence_residuals: tuple[sp.Integer, ...]
    series_residual: sp.Expr
    hypergeometric_residual: sp.Expr
    composition_formula_residuals: tuple[sp.Integer, ...]
    parameter_polynomials: tuple[sp.Expr, ...]


def transfer_secancy_coefficients(N: int, r: sp.Expr, nmax: int) -> tuple[sp.Expr, ...]:
    vals: list[sp.Expr] = [sp.Integer(1)]
    for n in range(1, nmax + 1):
        first = -sum(
            (-1) ** k * sp.binomial(N * n - 1, N * k) * vals[n - k]
            for k in range(1, n)
        )
        second = -r * sum(
            (-1) ** k * sp.binomial(N * n - 1, N * k - 1) * vals[n - k]
            for k in range(1, n + 1)
        )
        vals.append(sp.factor(sp.expand(first + second)))
    return tuple(vals)


def compositions(n: int, m: int) -> tuple[tuple[int, ...], ...]:
    if m == 0:
        return ((),) if n == 0 else ()
    if m == 1:
        return ((n,),) if n >= 1 else ()
    out: list[tuple[int, ...]] = []
    for first in range(1, n - m + 2):
        for rest in compositions(n - first, m - 1):
            out.append((first,) + rest)
    return tuple(out)


def composition_formula_a5r2(n: int) -> sp.Integer:
    if n == 0:
        return sp.Integer(1)
    total = sp.Rational(0)
    for m in range(1, n + 1):
        inner = sum(
            sp.prod(sp.Rational(1, sp.factorial(5 * part)) for part in comp)
            for comp in compositions(n, m)
        )
        total += (-1) ** (n + m) * (m + 1) * inner
    return sp.Integer(sp.factorial(5 * n) * total)


def d5_root_sum(z: sp.Symbol) -> sp.Expr:
    sqrt5 = sp.sqrt(5)
    a = (1 + sqrt5) / 4
    b = sp.sqrt(10 - 2 * sqrt5) / 4
    c = (1 - sqrt5) / 4
    d = sp.sqrt(10 + 2 * sqrt5) / 4
    return sp.simplify(
        (sp.exp(-z) + 2 * sp.exp(a * z) * sp.cos(b * z) + 2 * sp.exp(c * z) * sp.cos(d * z)) / 5
    )


def d5_truncated_series(z: sp.Symbol, nmax: int) -> sp.Expr:
    return sum((-1) ** n * z ** (5 * n) / sp.factorial(5 * n) for n in range(nmax + 1))


@lru_cache(maxsize=None)
def build_certificate(nmax: int = 12) -> ArithmeticCertificate:
    z = sp.symbols("z")
    seq_expr = transfer_secancy_coefficients(5, sp.Integer(2), nmax)
    seq = tuple(sp.Integer(v) for v in seq_expr)

    recurrence_residuals: list[sp.Integer] = []
    for n in range(1, nmax + 1):
        rhs = -sum(
            (-1) ** k * sp.binomial(5 * n - 1, 5 * k) * seq[n - k]
            for k in range(1, n)
        ) - 2 * sum(
            (-1) ** k * sp.binomial(5 * n - 1, 5 * k - 1) * seq[n - k]
            for k in range(1, n + 1)
        )
        recurrence_residuals.append(sp.Integer(sp.simplify(seq[n] - rhs)))

    # Independent coefficient check of D_5(z)^{-2}.  First square D_5,
    # then convolve its block-EGF coefficients with the candidate sequence.
    d2 = []
    for n in range(nmax + 1):
        d2.append(sp.Integer(sum(
            sp.binomial(5 * n, 5 * q) * (-1) ** q * (-1) ** (n - q)
            for q in range(n + 1)
        )))
    inverse_residuals = []
    for n in range(nmax + 1):
        coeff = sum(sp.binomial(5 * n, 5 * k) * d2[k] * seq[n - k] for k in range(n + 1))
        inverse_residuals.append(sp.Integer(sp.simplify(coeff - (1 if n == 0 else 0))))
    series_residual = sp.Integer(max(abs(int(v)) for v in inverse_residuals))

    # Hypergeometric coefficient identity, checked exactly term by term.
    hyper_residuals = []
    for n in range(nmax + 1):
        lhs = sp.Rational((-1) ** n, sp.factorial(5 * n))
        rhs = sp.Rational((-1) ** n, 5 ** (5 * n) * sp.factorial(n))
        for j in range(1, 5):
            rhs /= sp.rf(sp.Rational(j, 5), n)
        hyper_residuals.append(sp.simplify(lhs - rhs))
    hypergeometric_residual = sp.Integer(0) if all(v == 0 for v in hyper_residuals) else sp.Integer(1)

    comp_res = tuple(sp.Integer(seq[n] - composition_formula_a5r2(n)) for n in range(nmax + 1))
    r = sp.symbols("r")
    parameter_polynomials = transfer_secancy_coefficients(5, r, 5)

    assert all(v == 0 for v in recurrence_residuals)
    assert series_residual == 0
    assert hypergeometric_residual == 0
    assert all(v == 0 for v in comp_res)
    assert all(v.is_integer for v in seq)

    return ArithmeticCertificate(
        sequence=seq,
        recurrence_residuals=tuple(recurrence_residuals),
        series_residual=series_residual,
        hypergeometric_residual=hypergeometric_residual,
        composition_formula_residuals=comp_res,
        parameter_polynomials=parameter_polynomials,
    )

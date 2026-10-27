#!/usr/bin/env python3
"""Exact rational Taylor-coefficient controls for continuous hidden-state elimination.

No sampled exponential is treated as exact. The finite assertions compare
coefficients through degree 8, using an independently expanded polynomial
antiderivative for the Volterra convolution. Universal time/space claims are
proved in Lean, not inferred from this finite test. Uses the retained exact
matrix helper and only Python's standard library.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb, factorial
import json
import random
from check_discrete_memory import Mat, blocks

SEED = 20260913
ORDER = 8
ASSERTIONS = 0
NEGATIVE_CONTROLS = 0


def check(condition: bool, label: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    if not condition:
        raise AssertionError(f'{ASSERTIONS}: {label}')


def scale(a: Q, matrix: Mat) -> Mat:
    return Mat(matrix.rows, matrix.cols,
               tuple(tuple(a*x for x in row) for row in matrix.entries))


def polynomial_integral_factor(k: int, j: int) -> Q:
    """Coefficient of t^(k+j+1) in integral_0^t (t-s)^k s^j ds.

    Computed by expanding (t-s)^k and integrating each monomial, not using
    the closed-form beta/factorial identity being tested.
    """
    return sum((Q((-1)**r * comb(k, r), r+j+1) for r in range(k+1)), Q(0))


def convolution(kernel: list[Mat], values: list[Mat], n: int, r: int, c: int) -> Mat:
    """Degree-n coefficient of integral_0^t K(t-s) v(s) ds."""
    out = Mat.zero(r, c)
    for k in range(n):
        j = n-1-k
        out += scale(polynomial_integral_factor(k, j), kernel[k] @ values[j])
    return out


def validate_prefix(A: Mat, B: Mat, G: Mat, D: Mat, claimed: list[Mat]) -> None:
    """Fail-closed exact check; finite data only, no certificate extraction claim."""
    L = blocks(A, B, G, D)
    if len(claimed) != ORDER+1:
        raise ValueError('Incomplete Taylor prefix')
    for n, coefficient in enumerate(claimed):
        if coefficient != scale(Q(1, factorial(n)), L.power(n).sub(0, A.rows, 0, A.rows)):
            raise ValueError(f'Incorrect Taylor coefficient at degree {n}')


def reject(fn) -> None:
    global NEGATIVE_CONTROLS
    try:
        fn()
    except (ValueError, AssertionError):
        NEGATIVE_CONTROLS += 1
    else:
        raise AssertionError('Negative control unexpectedly accepted')


def run() -> dict:
    rng = random.Random(SEED)
    systems = 0

    def rand(r: int, c: int) -> Mat:
        return Mat(r, c, tuple(tuple(Q(rng.randint(-2, 2), rng.randint(1, 3))
                                     for _ in range(c)) for _ in range(r)))

    # Independent antiderivative oracle and the factorial convolution identity.
    for k in range(ORDER+1):
        for j in range(ORDER+1):
            check(polynomial_integral_factor(k, j) ==
                  Q(factorial(k)*factorial(j), factorial(k+j+1)), 'monomial integral')

    for v in range(4):
        for h in range(4):
            for repetition in range(2):
                systems += 1
                A, B, G, D = rand(v, v), rand(v, h), rand(h, v), rand(h, h)
                L = blocks(A, B, G, D)
                powers = [L.power(n) for n in range(ORDER+2)]
                dpowers = [D.power(n) for n in range(ORDER+1)]
                ecoeff = [scale(Q(1, factorial(n)), powers[n].sub(0, v, 0, v))
                         for n in range(ORDER+1)]
                dcoeff = [scale(Q(1, factorial(n)), dpowers[n]) for n in range(ORDER+1)]
                mcoeff = [B @ x @ G for x in dcoeff]
                validate_prefix(A, B, G, D, ecoeff)
                x0 = rand(v+h, 1)
                y0, z0 = x0.sub(0, v, 0, 1), x0.sub(v, v+h, 0, 1)
                y = [scale(Q(1, factorial(n)), (powers[n] @ x0).sub(0, v, 0, 1))
                     for n in range(ORDER+2)]
                z = [scale(Q(1, factorial(n)), (powers[n] @ x0).sub(v, v+h, 0, 1))
                     for n in range(ORDER+2)]
                gy = [G @ x for x in y]
                for n in range(ORDER+1):
                    # Derived hidden formula, including nonzero initial hidden state.
                    check(z[n] == dcoeff[n] @ z0 + convolution(dcoeff, gy, n, h, 1),
                          'hidden elimination coefficient')
                    check(B @ z[n] == B @ dcoeff[n] @ z0 + convolution(mcoeff, y, n, v, 1),
                          'initial forcing plus feedback')
                    check(scale(Q(n+1), y[n+1]) ==
                          A @ y[n] + B @ dcoeff[n] @ z0 + convolution(mcoeff, y, n, v, 1),
                          'visible Volterra derivative coefficient')
                    # Actual prepared response satisfies the operator-valued recurrence.
                    next_e = scale(Q(1, factorial(n)), powers[n+1].sub(0, v, 0, v))
                    check(next_e == A @ ecoeff[n] + convolution(mcoeff, ecoeff, n, v, v),
                          'prepared memory coefficient')
                # Bivariate coefficient of E(s+t)-E(s)E(t), and hidden-return factorization.
                for i in range(5):
                    for j in range(5):
                        lhs = scale(Q(1, factorial(i)*factorial(j)),
                                    powers[i+j].sub(0, v, 0, v)) - ecoeff[i] @ ecoeff[j]
                        rhs = scale(Q(1, factorial(i)*factorial(j)),
                                    powers[i].sub(0, v, v, v+h) @ powers[j].sub(v, v+h, 0, v))
                        check(lhs == rhs, 'continuous semigroup defect coefficient')
                # Finite dimension moment certificate vs prepared derivative prefix.
                moment_pass = all(B @ dpowers[k] @ G == Mat.zero(v, v) for k in range(h))
                generator_pass = all(powers[n].sub(0, v, 0, v) == A.power(n) for n in range(h+2))
                check(moment_pass == generator_pass, 'finite certificates agree')
                if moment_pass:
                    check(all(m == Mat.zero(v, v) for m in mcoeff), 'extended zero moment controls')
                    check(all(ecoeff[n] == scale(Q(1, factorial(n)), A.power(n))
                              for n in range(ORDER+1)), 'extended prepared controls')
                if v and repetition == 0:
                    corrupted = list(ecoeff)
                    corrupted[3] += Mat.eye(v)
                    reject(lambda: validate_prefix(A, B, G, D, corrupted))

    # The exact delayed return example: hidden D^2=0, M(t)=t, first visible term t^3/6.
    A = Mat.of([[0]])
    B, G, D = Mat.of([[1, 0]]), Mat.of([[0], [1]]), Mat.of([[0, 1], [0, 0]])
    L = blocks(A, B, G, D)
    check(D.power(2) == Mat.zero(2, 2), 'nilpotent hidden generator')
    check(B @ G == Mat.zero(1, 1), 'zero immediate feedback')
    check(B @ D @ G == Mat.eye(1), 'nonzero delayed feedback')
    check(scale(Q(1, 6), L.power(3).sub(0, 1, 0, 1)) == Mat.of([[Q(1, 6)]]),
          'third Taylor coefficient')
    for n in range(ORDER+1):
        expected = Mat.eye(1) if n == 1 else Mat.zero(1, 1)
        check(scale(Q(1, factorial(n)), B @ D.power(n) @ G) == expected, 'exact polynomial memory')
    # Removing the hidden transfer keeps both couplings but kills all prepared feedback.
    D = Mat.zero(2, 2)
    L = blocks(A, B, G, D)
    for n in range(ORDER+1):
        check(B @ D.power(n) @ G == Mat.zero(1, 1), 'disconnected return kernel')
        check(L.power(n).sub(0, 1, 0, 1) == A.power(n), 'prepared exact disconnected')
    check(B @ Mat.of([[1], [0]]) == Mat.eye(1), 'hidden initialization still observed')
    reject(lambda: validate_prefix(A, B, G, D, []))
    reject(lambda: scale(Q(1), Mat(-1, 0, ())))
    reject(lambda: blocks(A, Mat.zero(2, 2), G, D))
    return {'passed': True, 'seed': SEED, 'random_systems': systems,
            'visible_dimension_range': [0, 3], 'hidden_dimension_range': [0, 3],
            'taylor_degree': ORDER, 'mixed_time_degrees': [0, 4],
            'exact_assertions': ASSERTIONS, 'negative_controls_rejected': NEGATIVE_CONTROLS,
            'arithmetic': 'fractions.Fraction, no floating point',
            'scope': 'Finite coefficients only; universal exponential/integral results are Lean proofs.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

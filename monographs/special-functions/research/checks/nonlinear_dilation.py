#!/usr/bin/env python3
"""SF-DISCOVERY-001: exact bounded checks, using only Python's standard library.

The run checks formal coefficients through z^61, not entire growth or novelty.
The analytic proofs are in routes/nonlinear_dilation.md. No result files are
written: JSON is emitted to stdout for the integrating run to capture.
"""
from fractions import Fraction as Q
from math import factorial
import json
import platform


def coefficients(q, last=30):
    c = [Q(1)]
    for n in range(1, last + 1):
        c.append(q ** (2 * n) * sum(c[i] * c[n - 1 - i]
                                  for i in range(n)) / (2 * n + 1))
    return c


def picard(q, degree=61):
    # A distinct construction: repeated integration of 1 + P(qz)^2,
    # retaining all degrees, including the even degrees that must vanish.
    p = [Q(0)] * (degree + 1)
    p[1] = Q(1)
    for _ in range((degree + 1) // 2):
        nxt = [Q(0)] * (degree + 1)
        nxt[1] = Q(1)
        scaled = [a * q ** i for i, a in enumerate(p)]
        for j in range(degree):
            nxt[j + 1] += sum(scaled[i] * scaled[j - i]
                              for i in range(j + 1)) / (j + 1)
        p = nxt
    return p


def bernoulli(n):
    # Exact triangular Bernoulli construction; B1 convention is immaterial
    # because the tangent benchmark uses only even indices.
    a = [Q(0)] * (n + 1)
    for m in range(n + 1):
        a[m] = Q(1, m + 1)
        for j in range(m, 0, -1):
            a[j - 1] = j * (a[j - 1] - a[j])
    return a[0]


def tangent_coefficient(n):
    m = 2 * n + 2
    return (-1) ** n * 2 ** m * (2 ** m - 1) * bernoulli(m) / factorial(m)


def polynomials(last=12):
    # Dictionaries exponent -> rational coefficient are exact Q[q] objects.
    out = [{0: Q(1)}]
    for n in range(1, last + 1):
        p = {}
        for i in range(n):
            for a, x in out[i].items():
                for b, y in out[n - 1 - i].items():
                    e = 2 * n + a + b
                    p[e] = p.get(e, Q(0)) + x * y / (2 * n + 1)
        out.append(p)
    return out


def main():
    count = 0

    def check(ok):
        nonlocal count
        assert ok
        count += 1

    poly = polynomials()
    expected = [{0: Q(1)}, {2: Q(1, 3)}, {6: Q(2, 15)},
                {10: Q(1, 63), 12: Q(4, 105)},
                {16: Q(4, 405), 18: Q(2, 567), 20: Q(8, 945)}]
    for actual, target in zip(poly, expected):
        check(actual == target)

    parameters = [Q(0), Q(1, 3), Q(1, 2), Q(3, 4), Q(1)]
    data = []
    for q in parameters:
        c = coefficients(q)
        p = picard(q)
        for j, a in enumerate(p):
            check(a == (c[(j - 1) // 2] if j % 2 else Q(0)))
        for n, a in enumerate(c):
            rhs = Q(1) if n == 0 else q ** (2 * n) * sum(
                c[i] * c[n - 1 - i] for i in range(n))
            check((2 * n + 1) * a == rhs)
            check(a >= 0)
            check(a <= tangent_coefficient(n))
            check(a <= q ** (2 * n) * tangent_coefficient(n))
            check(tangent_coefficient(n) <= Q(1, 2) ** n)
        for n, a in enumerate(poly):
            check(sum(x * q ** e for e, x in a.items()) == c[n])
        if q == 1:
            for n, a in enumerate(c):
                check(a == tangent_coefficient(n))
        if q == 0:
            check(c == [Q(1)] + [Q(0)] * 30)
        if q == Q(1, 2):
            for n, a in enumerate(c):
                check(a == Q(1, 2 ** n * factorial(2 * n + 1)))
        ratio = q ** 2 / 2
        sample_tail = ratio ** 31 / (1 - ratio)
        data.append({"q": str(q), "first_five": [str(a) for a in c[:5]],
                     "f_at_1_degree61": str(sum(c)),
                     "f_at_1_decimal": float(sum(c)),
                     "abs_tail_bound_at_1": str(sample_tail),
                     "abs_tail_bound_at_1_decimal": float(sample_tail)})

    # The tangent recurrence proves t_n <= 2^(-n) by induction. Since
    # c_n(q) <= q^(2n)t_n, |z| <= 1 has a rigorous degree-61 tail bound
    # sum_{n>=31}(q²/2)^n, at most 2^(-30) on q in [0,1].
    tail_bound = Q(1, 2) ** 30
    print(json.dumps({
        "checkpoint": "SF-DISCOVERY-001",
        "route": "nonlinear dilation tangent",
        "status": "passed",
        "python": platform.python_version(),
        "arithmetic": "fractions.Fraction over Q; polynomial dictionary over Q[q]",
        "bounds": {"last_coefficient_n": 30, "degree_z": 61,
                   "symbolic_polynomial_n": 12, "q": [str(q) for q in parameters]},
        "exact_assertions": count,
        "first_polynomials": [{str(e): str(a) for e, a in p.items()} for p in poly[:5]],
        "samples": data,
        "uniform_abs_tail_at_radius1": str(tail_bound),
        "uniform_abs_tail_at_radius1_decimal": float(tail_bound),
        "non_claims": ["No finite computation proves entire extension or growth order.",
                       "No global historical novelty claim.",
                       "No analytic Lean formalization."]
    }, indent=2))


if __name__ == "__main__":
    main()

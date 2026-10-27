#!/usr/bin/env python3
"""Exact finite checks for asymmetric dilation and a finite feedback tap bank.

Only standard-library rational arithmetic is used. Analytic proofs and scope
are recorded in routes/asymmetric_dilation.md; this script proves no novelty.
"""
from fractions import Fraction as Q
import hashlib
import json
import platform
from nonlinear_dilation import coefficients as diagonal_coefficients
from nonlinear_dilation import tangent_coefficient


def coefficients(channels, last=30):
    c = [Q(1)]
    for n in range(1, last + 1):
        c.append(sum(h * sum(q ** (2 * i + 1) * r ** (2 * (n - 1 - i) + 1)
                              * c[i] * c[n - 1 - i] for i in range(n))
                     for h, q, r in channels) / (2 * n + 1))
    return c


def picard(channels, degree=61):
    p = [Q(0)] * (degree + 1)
    p[1] = Q(1)
    for _ in range((degree + 1) // 2):
        nxt = [Q(0)] * (degree + 1)
        nxt[1] = Q(1)
        for h, q, r in channels:
            left = [a * q ** i for i, a in enumerate(p)]
            right = [a * r ** i for i, a in enumerate(p)]
            for j in range(degree):
                nxt[j + 1] += h * sum(left[i] * right[j - i]
                                     for i in range(j + 1)) / (j + 1)
        p = nxt
    return p


def polynomial_coefficients(last=8):
    # Exact Q[q,r] objects: (q exponent, r exponent) -> rational coefficient.
    out = [{(0, 0): Q(1)}]
    for n in range(1, last + 1):
        p = {}
        for i in range(n):
            j = n - 1 - i
            for (a, b), u in out[i].items():
                for (c, d), v in out[j].items():
                    e = (a + c + 2 * i + 1, b + d + 2 * j + 1)
                    p[e] = p.get(e, Q(0)) + u * v / (2 * n + 1)
        out.append(p)
    return out


def main():
    count = 0

    def check(ok):
        nonlocal count
        assert ok
        count += 1

    poly = polynomial_coefficients()
    expected = [{(0, 0): Q(1)}, {(1, 1): Q(1, 3)},
                {(4, 2): Q(1, 15), (2, 4): Q(1, 15)}]
    for p, target in zip(poly, expected):
        check(p == target)
    for p in poly:
        check(p == {(b, a): c for (a, b), c in p.items()})

    pairs = [(Q(1, 2), Q(1, 2)), (Q(1, 3), Q(2, 3)),
             (Q(1, 4), Q(3, 4)), (Q(1, 3), Q(1, 2)),
             (Q(1, 4), Q(1, 3)), (Q(3, 5), Q(4, 5)),
             (Q(0), Q(1, 2))]
    banks = [[(Q(1, 4), Q(1, 4), Q(1, 4)),
              (Q(3, 4), Q(3, 4), Q(3, 4))],
             [(Q(1, 2), Q(1, 3), Q(2, 3)),
              (Q(1, 2), Q(1, 4), Q(3, 4))]]
    samples = []
    for channels in [[(Q(1), q, r)] for q, r in pairs] + banks:
        check(sum(h for h, _, _ in channels) == 1)
        c = coefficients(channels)
        p = picard(channels)
        for j, a in enumerate(p):
            check(a == (c[(j - 1) // 2] if j % 2 else Q(0)))
        swapped = [(h, r, q) for h, q, r in channels]
        other = coefficients(swapped)
        max_delay = max(max(q, r) for _, q, r in channels)
        for n, a in enumerate(c):
            check(a == other[n])
            check(a >= 0)
            check(a <= max_delay ** (2 * n) * tangent_coefficient(n))
            rhs = Q(1) if n == 0 else sum(
                h * sum(q ** (2 * i + 1) * r ** (2 * (n - 1 - i) + 1)
                        * c[i] * c[n - 1 - i] for i in range(n))
                for h, q, r in channels)
            check((2 * n + 1) * a == rhs)
        mu1 = sum(h * q * r for h, q, r in channels)
        mu2 = sum(h * q * r * (q ** 2 + r ** 2) for h, q, r in channels)
        check(c[1] == mu1 / 3)
        check(c[2] == mu1 * mu2 / 15)
        if len(channels) == 1:
            _, q, r = channels[0]
            for n, a in enumerate(poly):
                check(sum(x * q ** u * r ** v for (u, v), x in a.items()) == c[n])
            if q == r:
                diag = diagonal_coefficients(q)
                for n, a in enumerate(c):
                    check(a == diag[n])
            if q + r == 1 and q != r:
                check(c[2] > mu1 ** 2 / 30)
            if q ** 2 + r ** 2 == 1 and q != r:
                # The exceptional-order branch of the nonrescaling proof.
                scaled_diagonal_c3 = Q(11, 1260) * mu1 ** 3
                obstruction = mu1 ** 3 * (1 - 4 * mu1 ** 2) / 1260
                check(c[3] - scaled_diagonal_c3 == obstruction)
                check(obstruction > 0)
        ratio = max_delay ** 2 / 2
        tail = ratio ** 31 / (1 - ratio)
        partial_sum = sum(c)
        samples.append({"channels": [[str(x) for x in channel] for channel in channels],
                        "first_five": [str(a) for a in c[:5]],
                        "f_at_1_decimal": float(partial_sum),
                        "exact_partial_sum_sha256": hashlib.sha256(str(partial_sum).encode()).hexdigest(),
                        "analytic_tail_bound_radius1": str(tail),
                        "analytic_tail_bound_radius1_decimal": float(tail)})
    print(json.dumps({"checkpoint": "SF-DISCOVERY-001",
                      "route": "asymmetric dilation with feedback taps",
                      "status": "passed", "python": platform.python_version(),
                      "arithmetic": "fractions.Fraction over Q; bivariate polynomial dictionary over Q[q,r]",
                      "exact_assertions": count,
                      "bounds": {"last_coefficient_n": 30, "degree_z": 61,
                                 "bivariate_polynomial_n": 8, "pair_count": len(pairs),
                                 "two_channel_bank_count": len(banks)},
                      "first_four_bivariate_polynomials": [
                          {f"{u},{v}": str(a) for (u, v), a in p.items()} for p in poly[:4]],
                      "samples": samples,
                      "non_claims": ["The finite run does not prove entire extension or order.",
                                     "No global priority claim.", "No analytic Lean certificate."]}, indent=2))


if __name__ == "__main__":
    main()

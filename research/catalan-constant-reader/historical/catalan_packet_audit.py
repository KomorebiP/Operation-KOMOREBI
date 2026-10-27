#!/usr/bin/env python3
"""Exact arithmetic audit for Catalan-constant packet constructions.

This script checks three finite claims:
1. Zudilin's recurrence and the closed Wronskian identity.
2. 2-adic valuations of the binomial packet transform over a bounded range.
3. Common divisors of the cleared coefficients for Eskandari's filter.

The finite scans are evidence only; they do not prove a uniform asymptotic bound
or the irrationality of Catalan's constant.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from math import comb, gcd, lcm
from pathlib import Path


def p(n: int) -> int:
    return 20 * n * n - 8 * n + 1


def q(n: int) -> int:
    return (
        3520 * n**6
        + 5632 * n**5
        + 2064 * n**4
        - 384 * n**3
        - 156 * n**2
        + 16 * n
        + 7
    )


def v2_integer(value: int) -> int:
    value = abs(value)
    if value == 0:
        raise ValueError("v2(0) is infinite")
    return (value & -value).bit_length() - 1


def zudilin_sequences(max_n: int) -> tuple[list[Fraction], list[Fraction]]:
    if max_n < 1:
        raise ValueError("max_n must be at least 1")
    u = [Fraction(1), Fraction(7, 4)]
    v = [Fraction(0), Fraction(13, 8)]
    for n in range(1, max_n):
        a_n = (2 * n + 1) ** 2 * (2 * n + 2) ** 2 * p(n)
        c_n = (2 * n - 1) ** 2 * (2 * n) ** 2 * p(n + 1)
        u.append((q(n) * u[n] + c_n * u[n - 1]) / a_n)
        v.append((q(n) * v[n] + c_n * v[n - 1]) / a_n)
    return u[: max_n + 1], v[: max_n + 1]


def t_sequence(max_n: int) -> list[int]:
    """Return T_n = 16^n u_n using exact integer division."""
    if max_n < 1:
        return [1][: max_n + 1]
    values = [1, 28]
    for n in range(1, max_n):
        a_n = (2 * n + 1) ** 2 * (2 * n + 2) ** 2 * p(n)
        c_n = (2 * n - 1) ** 2 * (2 * n) ** 2 * p(n + 1)
        numerator = 16 * q(n) * values[n] + 256 * c_n * values[n - 1]
        next_value, remainder = divmod(numerator, a_n)
        if remainder != 0:
            raise ArithmeticError(f"nonintegral T recurrence at n={n}")
        values.append(next_value)
    return values[: max_n + 1]


def wronskian_audit(u: list[Fraction], v: list[Fraction], bound: int) -> dict:
    failures: list[dict] = []
    for n in range(bound + 1):
        observed = u[n + 1] * v[n] - u[n] * v[n + 1]
        expected = Fraction(
            (-1) ** (n + 1) * p(n + 1),
            2 * (2 * n + 1) ** 2 * (2 * n + 2) ** 2,
        )
        if observed != expected:
            failures.append(
                {"n": n, "observed": str(observed), "expected": str(expected)}
            )
    return {"bound": bound, "failures": failures, "passed": not failures}


def scan_binomial_v2(max_n: int, precision_bits: int = 128) -> dict:
    """Scan S_{n,m}=sum_i binom(m,i)T_{n+i}, n<=max_n, m<=4n.

    The Pascal recurrence is evaluated modulo 2^precision_bits. Any residue equal
    to zero would mean only v2 >= precision_bits. The run is exact when no such
    unresolved residue is encountered at the reported maximum.
    """
    max_m = 4 * max_n
    max_index = 5 * max_n
    modulus = 1 << precision_bits
    mask = modulus - 1
    row = [value & mask for value in t_sequence(max_index)]

    maximum = -1
    argmax = None
    unresolved = 0
    count = 0

    for m in range(max_m + 1):
        n_min = max(1, (m + 3) // 4)
        for n in range(n_min, max_n + 1):
            residue = row[n]
            count += 1
            if residue == 0:
                unresolved += 1
                valuation = precision_bits
            else:
                valuation = (residue & -residue).bit_length() - 1
            if valuation > maximum:
                maximum = valuation
                argmax = [n, m]

        if m < max_m:
            upper = max_index - m
            for n in range(upper):
                row[n] = (row[n] + row[n + 1]) & mask

    return {
        "max_n": max_n,
        "pairs_scanned": count,
        "precision_bits": precision_bits,
        "maximum_v2": maximum,
        "argmax_n_m": argmax,
        "unresolved_residues": unresolved,
        "exact_below_precision": unresolved == 0,
    }


def direct_binomial_v2_crosscheck(max_n: int = 100) -> dict:
    """Independent direct-sum cross-check for a smaller range."""
    values = t_sequence(5 * max_n)
    maximum = -1
    argmax = None
    count = 0
    for n in range(1, max_n + 1):
        for m in range(0, 4 * n + 1):
            total = sum(comb(m, i) * values[n + i] for i in range(m + 1))
            valuation = v2_integer(total)
            count += 1
            if valuation > maximum:
                maximum = valuation
                argmax = [n, m]
    return {
        "max_n": max_n,
        "pairs_scanned": count,
        "maximum_v2": maximum,
        "argmax_n_m": argmax,
    }


def lcm_upto(bound: int) -> int:
    value = 1
    for k in range(1, bound + 1):
        value = lcm(value, k)
    return value


def filtered_cleared_pair(
    n: int, m: int, u: list[Fraction], v: list[Fraction]
) -> tuple[int, int]:
    ell = lcm_upto(2 * (n + m))
    sum_u = 0
    sum_v = Fraction(0)
    for i in range(m + 1):
        coefficient = comb(m, i)
        k = n + i
        scaled_u = u[k] * 16**k
        if scaled_u.denominator != 1:
            raise ArithmeticError(f"16^k u_k is nonintegral at k={k}")
        sum_u += coefficient * scaled_u.numerator
        sum_v += coefficient * (v[k] * 16**k)

    cleared_u = 8 * (-1) ** n * ell**2 * sum_u
    cleared_v_fraction = 8 * (-1) ** n * ell**2 * sum_v
    if cleared_v_fraction.denominator != 1:
        raise ArithmeticError(f"cleared v coefficient is nonintegral at {(n, m)}")
    return cleared_u, cleared_v_fraction.numerator


def trial_factor(value: int) -> dict[str, int]:
    remaining = abs(value)
    factors: dict[str, int] = {}
    prime = 2
    while prime * prime <= remaining:
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        if exponent:
            factors[str(prime)] = exponent
        prime = 3 if prime == 2 else prime + 2
    if remaining > 1:
        factors[str(remaining)] = 1
    return factors


def gcd_table() -> list[dict]:
    pairs = [(20, 66), (30, 100), (50, 166), (70, 232), (100, 332)]
    max_k = max(n + m for n, m in pairs)
    u, v = zudilin_sequences(max_k)
    rows: list[dict] = []
    for n, m in pairs:
        a, b = filtered_cleared_pair(n, m, u, v)
        content = gcd(abs(a), abs(b))
        rows.append(
            {
                "n": n,
                "m": m,
                "gcd": str(content),
                "factorization": trial_factor(content),
                "v2_gcd": v2_integer(content),
                "log_gcd_over_n_plus_m": math.log(content) / (n + m),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-n", type=int, default=2000)
    parser.add_argument("--precision-bits", type=int, default=128)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("catalan_packet_audit_results.json"),
    )
    args = parser.parse_args()

    recurrence_bound = max(200, 101)
    u, v = zudilin_sequences(recurrence_bound + 1)
    result = {
        "scope": {
            "claim": "finite arithmetic audit; not an irrationality proof",
            "arithmetic": "Python arbitrary-precision integers and Fraction rationals",
        },
        "wronskian": wronskian_audit(u, v, recurrence_bound),
        "binomial_v2_scan": scan_binomial_v2(args.scan_n, args.precision_bits),
        "binomial_v2_direct_crosscheck": direct_binomial_v2_crosscheck(100),
        "filtered_gcd_table": gcd_table(),
    }
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

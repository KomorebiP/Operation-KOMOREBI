"""Exact arithmetic-progression Cauchy subminor verification.

Author: Komorebi P. Uses integer arithmetic and exact fractions only.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import factorial, gcd, prod
from pathlib import Path
import json


def cauchy_det(n: int, d: int, e: int, h: int) -> Fraction:
    size = n + 1
    return Fraction(
        (d * e) ** (size * (size - 1) // 2)
        * prod(factorial(k) ** 2 for k in range(1, size)),
        prod(d * i + e * j + h for i in range(size) for j in range(size)),
    )


def det_elimination(n: int, d: int, e: int, h: int) -> Fraction:
    matrix = [[Fraction(1, d * i + e * j + h)
               for j in range(n + 1)] for i in range(n + 1)]
    determinant = Fraction(1)
    for k in range(n + 1):
        pivot = next((i for i in range(k, n + 1) if matrix[i][k]), None)
        assert pivot is not None
        if pivot != k:
            matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
            determinant = -determinant
        value = matrix[k][k]
        determinant *= value
        for i in range(k + 1, n + 1):
            factor = matrix[i][k] / value
            for j in range(k + 1, n + 1):
                matrix[i][j] -= factor * matrix[k][j]
            matrix[i][k] = 0
    return determinant


def factorial_v(k: int, p: int) -> int:
    total = 0
    while k:
        k //= p
        total += k
    return total


def factor(n: int) -> dict[int, int]:
    result = {}
    k = 2
    while k * k <= n:
        while n % k == 0:
            result[k] = result.get(k, 0) + 1
            n //= k
        k += 1
    if n > 1:
        result[n] = result.get(n, 0) + 1
    return result


def numerator_equal_step(n: int, d: int, h: int) -> int:
    g = gcd(d, h)
    reduced = d // g
    size = n + 1
    numerator = 1
    fg = factor(g)
    for p, exponent in factor(reduced).items():
        power = n * size * exponent + 2 * sum(factorial_v(k, p)
                for k in range(1, n + 1)) - size * fg.get(p, 0)
        if power > 0:
            numerator *= p ** power
    return numerator


def audit() -> dict:
    equal = unequal = 0
    for d in range(1, 6):
        for h in range(1, 8):
            for stride in range(1, 5):
                for row in range(4):
                    for col in range(4):
                        step = d * stride
                        shift = h + d * (row + col)
                        for n in range(4):
                            actual = det_elimination(n, step, step, shift)
                            assert actual == cauchy_det(n, step, step, shift)
                            assert actual.numerator == numerator_equal_step(n, step, shift)
                            equal += 1

    for d in range(1, 5):
        for h in range(1, 6):
            for row_step in range(1, 5):
                for col_step in range(1, 5):
                    for row in range(3):
                        for col in range(3):
                            shift = h + d * (row + col)
                            for n in range(4):
                                actual = det_elimination(n, d * row_step, d * col_step, shift)
                                assert actual == cauchy_det(n, d * row_step, d * col_step, shift)
                                assert all(d * row_step * col_step % p == 0
                                           for p in factor(actual.numerator))
                                unequal += 1
    assert cauchy_det(1, 2, 2, 1) == Fraction(4, 45)
    return {
        "author": "Komorebi P.",
        "status": "passed",
        "equal_stride_checks": equal,
        "unequal_stride_checks": unequal,
        "arithmetic_subminor_counterexample": "indices 0,2 in Hilbert matrix give 4/45",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = audit()
    encoded = json.dumps(result, indent=2) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded)
    print(encoded)

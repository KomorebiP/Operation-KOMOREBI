#!/usr/bin/env python3
"""Factorial lanes: independent, exact, standard-library worked example.

This computes a finite example; it does not certify unrelated research claims.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import json
from math import comb, factorial, prod
from pathlib import Path

N, J, P = 10, 4, 5


def step_factorial(start: int, n: int, step: int = N) -> int:
    """(start)_(n;step), including the empty product when n=0."""
    if n < 0 or step <= 0:
        raise ValueError('n must be nonnegative and the step positive')
    return prod(start + step * k for k in range(n))


def lane_products(n: int) -> dict[int, int]:
    return {r: step_factorial(r, n) for r in range(J + 1, J + N + 1)}


def pochhammer(value: Fraction, n: int) -> Fraction:
    return prod((value + k for k in range(n)), start=Fraction(1))


def parameters() -> tuple[Fraction, ...]:
    """The parameter 1 is handled by the built-in n! of 0F9."""
    return tuple(Fraction(r, N) for r in range(J + 1, J + N + 1) if r != N)


def hypergeometric_coefficient(n: int) -> Fraction:
    denominator = Fraction(factorial(J) * N ** (N * n) * factorial(n))
    for alpha in parameters():
        denominator *= pochhammer(alpha, n)
    return 1 / denominator


def unit_tail(n: int) -> Fraction:
    """Coefficient of t^(10n)/(10n)! after removing t^4/4!."""
    return Fraction(1, comb(N * n + J, J))


def reciprocal_coefficients(last: int) -> list[Fraction]:
    """Exact exponential-basis inverse of the normalized residue section."""
    g = [unit_tail(n) for n in range(last + 1)]
    c = [Fraction(1)]
    for n in range(1, last + 1):
        c.append(-sum((comb(N*n, N*k) * g[k] * c[n-k]
                       for k in range(1, n + 1)), Fraction(0)))
    return c


def valuation(value: Fraction | int, prime: int = P) -> int | None:
    """None represents infinity (the valuation of zero)."""
    value = Fraction(value)
    if not value:
        return None
    a, b, exponent = abs(value.numerator), value.denominator, 0
    while a % prime == 0:
        a //= prime
        exponent += 1
    while b % prime == 0:
        b //= prime
        exponent -= 1
    return exponent


def finite_difference(n: int, steps: tuple[int, ...]) -> Fraction:
    """Delta_q1 ... Delta_qs g(n), computed by exact inclusion-exclusion."""
    total = Fraction(0)
    for mask in range(1 << len(steps)):
        degree = mask.bit_count()
        offset = sum(step for i, step in enumerate(steps) if mask & (1 << i))
        total += (-1) ** (len(steps) - degree) * unit_tail(n + offset)
    return total


def check() -> dict[str, int]:
    totals = {'lane_and_hypergeometric': 0, 'reciprocal': 0,
              'prime_unit_and_displacement': 0, 'refinement': 0,
              'boundary_witness': 0}
    alphas = parameters()
    assert len(alphas) == 9 and Fraction(1) not in alphas
    for n in range(7):
        assert factorial(J) * prod(lane_products(n).values()) == factorial(N*n + J)
        assert hypergeometric_coefficient(n) == Fraction(1, factorial(N*n + J))
        assert unit_tail(n) == Fraction(factorial(J) * factorial(N*n), factorial(N*n+J))
        totals['lane_and_hypergeometric'] += 3
    coeffs = reciprocal_coefficients(7)
    for n, coefficient in enumerate(coeffs):
        total = sum((comb(N*n, N*k)*unit_tail(k)*coeffs[n-k]
                     for k in range(n+1)), Fraction(0))
        original = sum((comb(N*n+J, N*q)*coeffs[q]
                        for q in range(n+1)), Fraction(0))
        assert total == original == (1 if n == 0 else 0)
        assert valuation(coefficient) is None or valuation(coefficient) >= 0
        totals['reciprocal'] += 2
    assert coeffs[1] == -Fraction(1, 1001)
    assert coeffs[2] == Fraction(178205, 966966)
    assert [valuation(x) for x in coeffs[:5]] == [0, 0, 1, 0, 1]
    for n in range(16):
        g = unit_tail(n)
        assert valuation(g) == 0
        assert n == 0 or valuation(g - 1) >= 3
        totals['prime_unit_and_displacement'] += 2
    for q in (1, 2, 5, 10):
        for n in range(6):
            # Special four-factor cancellation supplies two extra powers of 5.
            assert valuation(unit_tail(n+q)-unit_tail(n)) >= 3 + valuation(q)
            totals['prime_unit_and_displacement'] += 1
    for steps in ((2,), (2,2), (2,2,2), (2,2,2,2), (2,10), (5,10)):
        for n in range(5):
            value = finite_difference(n, steps)
            lower = len(steps) + sum(valuation(q) for q in steps)
            assert valuation(value) is None or valuation(value) >= lower
            totals['prime_unit_and_displacement'] += 1
    # Both the two-child and the literature's five-child refinements are exact.
    for degree in range(100):
        parent = int(degree % 10 == 4)
        children_20 = int(degree % 20 == 4) + int(degree % 20 == 14)
        children_50 = sum(int(degree % 50 == r) for r in (4, 14, 24, 34, 44))
        assert parent == children_20 == children_50
        totals['refinement'] += 1
    # Outside 0 <= j < 5 the uniform unit conclusion can fail.
    assert valuation(Fraction(1, comb(25, 5))) == -1
    # Omitting the r=10 lane also fails to reconstruct the factorial.
    assert factorial(4)*prod(v for r,v in lane_products(3).items() if r != 10) != factorial(34)
    totals['boundary_witness'] += 2
    return totals


def write_tables(folder: Path, counts: dict[str, int]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    cs = reciprocal_coefficients(7)
    with (folder/'coefficients.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('n', 'degree', 'g_n', 'C_n', 'v5_g_n', 'v5_C_n'))
        for n,c in enumerate(cs):
            writer.writerow((n, 10*n+4, str(unit_tail(n)), str(c),
                             valuation(unit_tail(n)), valuation(c)))
    with (folder/'lane-products.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('lane_start', 'factors_n3', 'product'))
        for r, value in lane_products(3).items():
            writer.writerow((r, ' * '.join(str(r+10*k) for k in range(3)), value))
    (folder/'results.json').write_text(json.dumps({
        'case': {'N': N, 'j': J, 'p': P},
        'finite_assertions': counts, 'total': sum(counts.values()),
        'interpretation': 'Finite exact checks, not a general formal proof.'
    }, indent=2)+'\n', encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional folder for exact CSV and JSON tables')
    args = parser.parse_args()
    counts = check()
    print('FACTORIAL LANES | N=10, j=4, p=5')
    print('34! = 4! * product of ten step-10 lanes (n=3)')
    print('lane products: '+', '.join(f'{r}:{v}' for r, v in lane_products(3).items()))
    cs = reciprocal_coefficients(3)
    for n in range(4):
        print(f'n={n}  g_n={unit_tail(n)}  C_n={cs[n]}  v5(C_n)={valuation(cs[n])}')
    print(f'PASS: {sum(counts.values())} exact finite assertions')
    if args.output:
        write_tables(args.output, counts)
        print(f'Exact tables written to {args.output}')


if __name__ == '__main__':
    main()

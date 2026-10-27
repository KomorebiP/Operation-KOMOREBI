#!/usr/bin/env python3
"""Independent exact-rational checks of the v17 Euler residual identities.

These finite computations corroborate, but do not replace, the Lean proofs.
Uses only Python's standard library. All scientific arithmetic is exact.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from math import comb, factorial, prod
from pathlib import Path
import time


def two_power(e: int) -> Fraction:
    return Fraction(1 << e) if e >= 0 else Fraction(1, 1 << (-e))


def v2_int(n: int) -> int:
    if n == 0:
        raise ValueError("Zero has no finite valuation")
    n = abs(n)
    return (n & -n).bit_length() - 1


def v2(x: Fraction) -> int | None:
    return None if x == 0 else v2_int(x.numerator) - v2_int(x.denominator)


def at_least(x: Fraction, k: int) -> bool:
    val = v2(x)
    return val is None or val >= k


def bernoulli(limit: int) -> list[Fraction]:
    values = [Fraction(1)]
    for n in range(1, limit + 1):
        values.append(-sum((Fraction(comb(n + 1, k)) * values[k]
                            for k in range(n)), Fraction()) / (n + 1))
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-r', type=int, default=32)
    parser.add_argument('--max-offset', type=int, default=24)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.max_r < 1 or args.max_offset < 0:
        parser.error('require max-r>=1 and max-offset>=0')
    if args.output.exists():
        raise FileExistsError(f'Refusing overwrite: {args.output}')
    start = time.monotonic()
    limit = args.max_r + args.max_offset
    B = bernoulli(2 * limit)
    beta = [-two_power(2 * m) * (2 * m - 1) * B[2 * m] / factorial(2 * m)
            for m in range(limit + 1)]
    kappa = [two_power(2 * m) * factorial(2 * m) * beta[m]
             for m in range(limit + 1)]
    E = [Fraction(1)]
    for N in range(1, limit + 1):
        E.append(-sum((Fraction(comb(2 * N, 2 * m)) * E[m]
                       for m in range(N)), Fraction()))
    A = [Fraction(9 ** (n + 1) - 1, 8 * (n + 1) * (2 * n + 1))
         for n in range(limit + 1)]
    checks: Counter[str] = Counter()

    def check(name: str, condition: bool, inputs: object) -> None:
        if not condition:
            raise AssertionError(f'{name}: {inputs!r}')
        checks[name] += 1

    @lru_cache(None)
    def packet(q: int, n: int) -> int:
        return prod((n - i) * (2 * n - 2 * i - 1) for i in range(q))

    @lru_cache(None)
    def J(r: int, n: int) -> Fraction:
        return sum((two_power(3 * q) * beta[r + q] * packet(q, n) * A[n - q]
                    for q in range(n + 1)), Fraction())

    for m in range(1, limit + 1):
        check('beta_digit_valuation', v2(beta[m]) == m.bit_count() - 1, m)
        check('kappa_valuation', v2(kappa[m]) == 4 * m - 1, m)
    for n in range(limit + 1):
        check('source_unit', v2(A[n]) == 0, n)
        reconstructed = sum((kappa[m] * comb(2 * n, 2 * m) * A[n - m]
                             for m in range(n + 1)), Fraction())
        check('independent_euler_reconstruction', reconstructed == E[n], n)
    for r in range(1, args.max_r + 1):
        bound = (r.bit_count() - 1) // 3
        costs = [3 * q + (r + q).bit_count() - r.bit_count()
                 for q in range(bound + 1)]
        mu = min(costs)
        minimizers = [q for q, cost in enumerate(costs) if cost == mu]
        terminal = max(minimizers)
        check('minimum_nonpositive', mu <= 0, r)
        check('last_minimum_bound', terminal <= bound, r)
        for q in range(args.max_offset + 1):
            scalar = two_power(3 * q) * beta[r + q] / beta[r]
            cost = 3 * q + (r + q).bit_count() - r.bit_count()
            check('actual_scalar_carry', v2(scalar) == cost, (r, q))
            check('finite_search_global_bound', cost >= mu and (q <= bound or cost > 0), (r, q))
        for n in range(args.max_offset + 1):
            N = r + n
            h = J(r, n) / beta[r]
            g = two_power(-mu) * h
            error = E[N] - sum((kappa[m] * comb(2 * N, 2 * m) * A[N - m]
                               for m in range(r)), Fraction())
            predicted = kappa[r] * comb(2 * N, 2 * r) * h
            check('whole_euler_error_factorization', error == predicted, (r, N))
            check('normalized_integral_value', at_least(g, 0), (r, n))
            check('normalized_factorization', predicted == kappa[r] * comb(2 * N, 2 * r) * two_power(mu) * g, (r, n))
            check('doubled_binomial_valuation', v2_int(comb(2*N, 2*r)) == v2_int(comb(N, r)), (r, N))
            if g:
                expected_val = 4*r - 1 + v2_int(comb(N, r)) + mu + v2(g)
                check('normalized_whole_tail_valuation', v2(error) == expected_val, (r, N))
            residue = (g.numerator * pow(g.denominator, -1, 2)) % 2
            falling_residue = sum(prod(n-i for i in range(q)) for q in minimizers) % 2
            check('minimizer_residue_value', residue == falling_residue, (r, n))
            if r.bit_count() <= 3:
                check('sparse_row_exactness', v2(error) == 4*r-1+v2_int(comb(N, r)), (r, N))
            if n == 0:
                check('residual_at_zero', h == 1, r)
            else:
                rhs = beta[r] * A[n] + 8*n*(2*n-1)*J(r+1, n-1)
                check('infinite_recursion_integer_specialization', J(r,n) == rhs, (r,n))
            for a in range(min(n, 5) + 1):
                prefix = sum((two_power(3*q)*beta[r+q]*packet(q,n)*A[n-q]
                              for q in range(a)), Fraction())
                rhs = prefix + two_power(3*a)*packet(a,n)*J(r+a,n-a)
                check('block_recursion', J(r,n) == rhs, (r,n,a))
            for Q in range(n+2):
                prefix = sum((two_power(3*q)*beta[r+q]*packet(q,n)*A[n-q]
                              for q in range(min(Q, n+1))), Fraction())
                check('numerator_tail_precision', at_least(J(r,n)-prefix, 3*Q), (r,n,Q))
    report = {
        'status': 'PASS', 'kind': 'finite_exact_rational_corroboration',
        'proof_boundary': 'Universal statements are in Lean. This is not a certificate for all arithmetic inputs.',
        'max_r': args.max_r, 'max_offset': args.max_offset,
        'checks': dict(checks), 'registered_checks': sum(checks.values()),
        'seconds': round(time.monotonic() - start, 6),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic': 'Python integers and fractions.Fraction; no floating-point scientific arithmetic',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

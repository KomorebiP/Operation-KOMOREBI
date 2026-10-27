#!/usr/bin/env python3
"""Exact, independent finite mirrors for Paper IX companion and Fibonacci packets.

Author: Komorebi P.
Pure Python 3.10+. These checks are not extracted Lean code or universal proofs.
Characteristic polynomials are computed by the permutation determinant, with no
matrix division. Modular cases deliberately include composite coefficient rings.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import json
import random
from typing import Sequence

Scalar = int | Q
Matrix = list[list[Scalar]]
ROOT = Path(__file__).resolve().parents[1]


def natural(x: int, name: str) -> int:
    if isinstance(x, bool) or not isinstance(x, int) or x < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return x


def square(a: Sequence[Sequence[Scalar]]) -> int:
    n = len(a)
    if any(len(row) != n for row in a):
        raise ValueError('a square matrix is required')
    if any(isinstance(x, bool) or not isinstance(x, (int, Q)) for row in a for x in row):
        raise ValueError('matrix entries must be exact integers or Fractions')
    return n


def identity(n: int) -> Matrix:
    natural(n, 'dimension')
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a: Matrix, b: Matrix) -> Matrix:
    n = square(a)
    if square(b) != n:
        raise ValueError('matrix dimensions differ')
    return [[sum(a[i][j] * b[j][k] for j in range(n)) for k in range(n)] for i in range(n)]


def power(a: Matrix, n: int) -> Matrix:
    natural(n, 'exponent')
    out = identity(square(a))
    base = [row[:] for row in a]
    while n:
        if n & 1:
            out = mul(out, base)
        base = mul(base, base)
        n //= 2
    return out


def apply(a: Matrix, v: Sequence[Scalar]) -> list[Scalar]:
    n = square(a)
    if len(v) != n:
        raise ValueError('state dimension differs from matrix dimension')
    if any(isinstance(x, bool) or not isinstance(x, (int, Q)) for x in v):
        raise ValueError('state entries must be exact integers or Fractions')
    return [sum(a[i][j] * v[j] for j in range(n)) for i in range(n)]


def states(a: Matrix, v: Sequence[Scalar], last: int) -> list[list[Scalar]]:
    natural(last, 'last index')
    apply(a, v)  # Validate even when last = 0.
    out = [list(v)]
    for _ in range(last):
        out.append(apply(a, out[-1]))
    return out


def convolution(a: list[Scalar], b: list[Scalar]) -> list[Scalar]:
    out: list[Scalar] = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def characteristic(a: Matrix) -> list[Scalar]:
    """Ascending coefficients of det(t I - a), including the empty determinant 1."""
    n = square(a)
    out: list[Scalar] = [0] * (n + 1)
    for perm in permutations(range(n)):
        inv = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        term: list[Scalar] = [(-1) ** inv]
        for i, j in enumerate(perm):
            term = convolution(term, [-a[i][j], int(i == j)])
        for i, x in enumerate(term):
            out[i] += x
    return out


def fib(n: int) -> int:
    natural(n, 'Fibonacci index')
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def lucas(n: int) -> int:
    natural(n, 'Lucas index')
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def sampled_fib(step: int, offset: int, last: int) -> list[int]:
    """Evaluate by the packet recurrence, not by evaluating fib at every address."""
    natural(step, 'step'); natural(offset, 'offset'); natural(last, 'last')
    out = [fib(offset)]
    if last == 0:
        return out
    out.append(fib(step + offset))
    for k in range(last - 1):
        out.append(lucas(step) * out[k + 1] - (-1) ** step * out[k])
    return out


def check_case(a: Matrix, v: list[Scalar], step: int, offset: int, modulus: int | None) -> dict:
    d = square(a)
    last_k = 5
    src = states(a, v, step * (last_k + d) + offset)
    jump = power(a, step)
    coeff = characteristic(jump)
    def eq(x: Scalar, y: Scalar) -> bool:
        return x == y if modulus is None else (x - y) % modulus == 0
    def veq(x: list[Scalar], y: list[Scalar]) -> bool:
        return len(x) == len(y) and all(eq(s, t) for s, t in zip(x, y))
    assert eq(coeff[-1], 1)
    # Check the actual Cayley-Hamilton identity as an independent finite mirror.
    cpows = [power(jump, i) for i in range(d + 1)]
    for i in range(d):
        for j in range(d):
            assert eq(sum(coeff[t] * cpows[t][i][j] for t in range(d + 1)), 0)
    for k in range(last_k + 1):
        pkt = src[step * k + offset]
        formula = apply(power(a, offset), apply(power(jump, k), v))
        assert veq(pkt, formula)
        total = [sum(coeff[t] * src[step * (k + t) + offset][i] for t in range(d + 1))
                 for i in range(d)]
        assert veq(total, [0] * d)
        rhs = [-sum(coeff[t] * src[step * (k + t) + offset][i] for t in range(d)) for i in range(d)]
        assert veq(src[step * (k + d) + offset], rhs)
        if k < last_k:
            assert veq(src[step * (k + 1) + offset], apply(jump, pkt))
    return {'jump_cases': last_k + 1, 'recurrence_cases': last_k + 1,
            'matrix_identity_cases': 1, 'step_cases': last_k}


def run() -> dict:
    rng = random.Random(906)
    counts = {'matrix_systems': 0, 'jump_cases': 0, 'recurrence_cases': 0,
              'matrix_identity_cases': 0, 'step_cases': 0,
              'fibonacci_packet_cases': 0, 'fibonacci_scalar_recurrences': 0,
              'lucas_trace_cases': 0, 'matrix_refinement_cases': 0,
              'invalid_input_rejections': 0}
    domains = ['integer', 'rational', 1, 4, 6, 9, 11]
    for domain in domains:
        for d in range(5):
            for sample in range(8):
                val = lambda: Q(rng.randint(-2, 2), rng.randint(1, 4)) if domain == 'rational' else rng.randint(-2, 2)
                a = [[val() for _ in range(d)] for _ in range(d)]
                v = [val() for _ in range(d)]
                step, offset = sample % 6, (sample * 3) % 7
                results = check_case(a, v, step, offset, domain if isinstance(domain, int) else None)
                counts['matrix_systems'] += 1
                for key, n in results.items(): counts[key] += n
                # Iterated subsequence addressing, also meaningful at zero step.
                m, s, k = sample % 3, sample % 2, 2
                left = apply(power(a, step * (m*k+s) + offset), v)
                right = apply(power(a, (step*m)*k + (step*s+offset)), v)
                assert left == right
                counts['matrix_refinement_cases'] += 1
    companion = [[1, 1], [1, 0]]
    for n in range(81):
        j = power(companion, n)
        assert sum(j[i][i] for i in range(2)) == lucas(n)
        assert j[0][0]*j[1][1] - j[0][1]*j[1][0] == (-1)**n
        assert lucas(n) == 2*fib(n+1) - fib(n)
        counts['lucas_trace_cases'] += 1
    for n in range(21):
        for j in range(17):
            got = sampled_fib(n, j, 32)
            assert got == [fib(n*k+j) for k in range(33)]
            counts['fibonacci_packet_cases'] += 1
            counts['fibonacci_scalar_recurrences'] += 31
    controls = {
        'wrong_even_sign_rejected': fib(5) != 3*fib(3)+fib(1),
        'wrong_jump_matrix_rejected': apply(power(companion, 2), [1,0]) != apply(companion, [1,0]),
        'wrong_jump_trace_rejected': sum(power(companion, 3)[i][i] for i in range(2)) != 3,
        'dimension_not_minimal_order': apply(identity(2), [1,0]) == [1,0],
        'empty_charpoly_is_one': characteristic([]) == [1],
        'singular_nilpotent_supported': characteristic([[0,1],[0,0]]) == [0,0,1],
    }
    assert all(controls.values())
    for call in [lambda: power([[1]], -1), lambda: fib(-1), lambda: lucas(True),
                 lambda: characteristic([[1,2]]), lambda: apply([[1]], []),
                 lambda: sampled_fib(1,-1,2), lambda: sampled_fib(1,0,-1),
                 lambda: states([[1]],[1],True), lambda: characteristic([[0.5]]),
                 lambda: apply([[1]], [True])]:
        try: call()
        except ValueError: counts['invalid_input_rejections'] += 1
        else: raise AssertionError('An invalid input was accepted')
    return {'status': 'PASS', 'seed': 906, 'counts': counts, 'domains': domains,
            'controls': controls, 'example_9_3': sampled_fib(3,2,5),
            'scope': 'Independent exact finite mirrors; not Lean extraction or universal proof.'}


def main() -> None:
    result = run()
    from datetime import datetime, timezone
    out = ROOT / 'verification/sixth_regressions' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True, exist_ok=False)
    (out/'regressions.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

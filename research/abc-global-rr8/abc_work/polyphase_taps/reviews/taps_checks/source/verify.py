#!/usr/bin/env python3
"""Exact finite tests for finite taps on A^n+B^n."""
import hashlib
import itertools
import json
import math
import platform
from fractions import Fraction
from pathlib import Path


def seq(A, B, n):
    return A ** n + B ** n


def evaluate(taps, x):
    return sum(t * x ** j for j, t in enumerate(taps))


def apply(taps, A, B, n, d=1):
    return sum(t * seq(A, B, n + j * d) for j, t in enumerate(taps))


def egcd(a, b):
    r0, r1, u0, u1, v0, v1 = a, b, 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        u0, u1 = u1, u0 - q * u1
        v0, v1 = v1, v0 - q * v1
    return r0, u0, v0


def valuation(n, p):
    assert n != 0
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e


def order(x, p):
    y = 1
    for d in range(1, p):
        y = y * x % p
        if y == 1:
            return d
    raise AssertionError('order not found')


def primes_dividing(n):
    p, out = 2, []
    while p * p <= n:
        if n % p == 0:
            out.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def main():
    root = Path(__file__).resolve().parent
    counts = {'tap_transport': 0, 'gcd_ideal': 0, 'half_order_gcd': 0,
              'vanishing_moments': 0, 'preserving_short_taps': 0,
              'physical_convolution_transport': 0}
    bases = [(A, B) for A in range(2, 9) for B in range(1, A) if math.gcd(A, B) == 1]
    for A, B in bases:
        for n in range(1, 13):
            for d in range(1, 7):
                delta = A ** d - B ** d
                x, y = seq(A, B, n), seq(A, B, n + d)
                g, u, v = egcd(x, y)
                assert g == math.gcd(x, delta)
                assert u * x + v * y == g > 0
                assert abs(u) <= y // g and abs(v) <= x // g
                assert g <= delta
                assert math.gcd(*[seq(A, B, n + j * d) for j in range(6)]) == g
                ann = ((A * B) ** d, -(A ** d + B ** d), 1)
                assert apply(ann, A, B, n, d) == 0
                counts['gcd_ideal'] += 1
                for r in range(1, 5):
                    taps = [math.comb(r, j) * (-B ** d) ** (r - j) for j in range(r + 1)]
                    got = apply(taps, A, B, n, d)
                    assert got == A ** n * delta ** r
                    assert sum(abs(t) for t in taps) == (1 + B ** d) ** r
                    assert got == A ** n * evaluate(taps, A ** d) + B ** n * evaluate(taps, B ** d)
                    counts['tap_transport'] += 1
                    counts['vanishing_moments'] += 1
            assert math.gcd(seq(A, B, n), seq(A, B, 3 * n)) == seq(A, B, n)
        for h in range(1, 7):
            for k in (1, 3, 5, 7):
                n = h * k
                expected = 2 if A % 2 == B % 2 == 1 else 1
                assert math.gcd(seq(A, B, n), seq(A, B, n + h)) == expected
                phase = A ** (n + h) - B ** (n + h) + B ** h * seq(A, B, n)
                assert phase == A ** n * (A ** h + B ** h)
                counts['half_order_gcd'] += 1

    # Physical convention, arbitrary decimation, exact integer amplitude.
    for A, B in ((2, 1), (3, 2), (8, 1)):
        for N in range(1, 5):
            for d in range(1, 5):
                for r in range(1, 5):
                    taps = [math.comb(r, j) * (-B ** d) ** (r - j) for j in range(r + 1)]
                    m = r * d + 2
                    n = N * m - r * d
                    h = {(r - j) * d: t for j, t in enumerate(taps)}
                    y = sum(t * seq(A, B, N * m - k) for k, t in h.items())
                    assert y == apply(taps, A, B, n, d)
                    counts['physical_convolution_transport'] += 1

    # Preserving all exceptional birth depths, exhaustively testing short taps.
    exceptional_samples = []
    for A, B, n in ((8, 1, 3), (8, 1, 5), (7, 2, 1), (17, 1, 3), (2, 1, 18)):
        P = 1
        births = []
        for p in primes_dividing(seq(A, B, n)):
            if p == 2:
                continue
            d = order(A * pow(B, -1, p) % p, p)
            s = valuation(A ** d - B ** d, p)
            if s >= 2:
                P *= p ** s
                births.append([p, d, s])
        assert math.gcd(P, A - B) == 1
        for taps in itertools.product(range(-2, 3), repeat=4):
            D = evaluate(taps, A) - evaluate(taps, B)
            Y = apply(taps, A, B, n)
            assert (Y % P == 0) == (D % P == 0)
            if D == 0:
                assert Y == evaluate(taps, A) * seq(A, B, n)
            elif D % P == 0:
                assert abs(D) >= P * (A - B)
                assert abs(D) <= sum(abs(t) for t in taps) * (A ** 3 + B ** 3)
            counts['preserving_short_taps'] += 1
        assert evaluate((0, P), A) - evaluate((0, P), B) == P * (A - B)
        exceptional_samples.append({'A': A, 'B': B, 'n': n, 'P': P, 'births': births})

    # Explicit birth and primitive-order examples, without factoring large output.
    g, u, v = egcd(seq(8, 1, 3), seq(8, 1, 5))
    assert g == 9 and valuation(g, 3) == 2
    worked = {'A': 8, 'B': 1, 'n': 3, 'd': 2, 's_n': seq(8, 1, 3),
              's_n_plus_d': seq(8, 1, 5), 'u': u, 'v': v, 'nonzero_auxiliary': g}
    p, n = 1093, 182
    assert valuation(pow(2, 364) - 1, p) == 2
    assert math.gcd(seq(2, 1, n), seq(2, 1, n + 364)) == seq(2, 1, n)
    assert math.gcd(seq(2, 1, n), seq(2, 1, n + 182)) == 1
    for r in range(1, 5):
        numerator = 2 ** n * (2 ** 364 - 1) ** r
        assert valuation(numerator, p) == 2 * r
        normalized = Fraction(numerator, p ** r)
        assert valuation(normalized.numerator, p) - valuation(normalized.denominator, p) == r

    data = {'status': 'completed', 'python': platform.python_version(),
            'assertion_tested': 'Exact finite verification of tap formulas, optimal gcd ideal, phase transport, coefficient-preservation conditions, and normalization.',
            'non_claims': ['No ABC proof.', 'No universal existence theorem for low-cost nonzero preserving taps.', 'No floating arithmetic.'],
            'counts': counts, 'worked_bezout': worked, 'exceptional_samples': exceptional_samples,
            'input_hashes': {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                             for name in ('PROOF_NOTE.md', 'verify.py')}}
    (root / 'verification.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()

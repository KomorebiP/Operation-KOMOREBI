#!/usr/bin/env python3
"""Independent finite checks; no imports from the author's implementation."""
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


def val(x, p):
    assert x
    e = 0
    while x % p == 0:
        e += 1
        x //= p
    return e


def primes(limit):
    return [p for p in range(3, limit + 1, 2)
            if all(p % q for q in range(2, math.isqrt(p) + 1))]


def order_ratio(a, b, p):
    a0, b0 = 1, 1
    for d in range(1, p):
        a0, b0 = a0 * a % p, b0 * b % p
        if a0 == b0:
            return d
    raise AssertionError("No order")


def main():
    counts = dict(ideal=0, half_gcd=0, birth=0, finite_difference=0,
                  explicit_kernel_and_degree_zero=0,
                  physical_arbitrary_taps=0, preserving_arbitrary_taps=0)
    bases = [(a, b) for a in range(2, 13) for b in range(1, a)
             if math.gcd(a, b) == 1]
    for a, b in bases:
        for n in range(1, 19):
            x = a ** n + b ** n
            assert math.gcd(x, a * b) == 1
            for d in range(1, 9):
                delta = a ** d - b ** d
                values = [a ** (n + j * d) + b ** (n + j * d)
                          for j in range(8)]
                g = math.gcd(*values)
                assert g == math.gcd(x, delta)
                for j in range(6):
                    assert values[j + 2] == (a ** d + b ** d) * values[j + 1] - (a * b) ** d * values[j]
                assert g <= delta < a ** d
                counts['ideal'] += 1
            assert math.gcd(x, a ** (3 * n) + b ** (3 * n)) == x
        for h in range(1, 9):
            for k in range(1, 16, 2):
                n = h * k
                g = math.gcd(a ** n + b ** n, a ** (n + h) + b ** (n + h))
                assert g == (2 if a % 2 == b % 2 == 1 else 1)
                assert a ** (n + h) - b ** (n + h) + b ** h * (a ** n + b ** n) == a ** n * (a ** h + b ** h)
                counts['half_gcd'] += 1
        for p in primes(43):
            if a * b % p == 0:
                continue
            d = order_ratio(a, b, p)
            if d % 2:
                continue
            s = val(a ** d - b ** d, p)
            h = d // 2
            assert (a ** h + b ** h) % (p ** s) == 0
            for k in (1, 3, p):
                n = h * k
                x, y = a ** n + b ** n, a ** (n + d) + b ** (n + d)
                assert val(x, p) == s + val(n, p)
                assert val(math.gcd(x, y), p) == s
                counts['birth'] += 1
                for r in range(1, 5):
                    tap = [math.comb(r, j) * (-b ** d) ** (r - j)
                           for j in range(r + 1)]
                    got = sum(t * (a ** (n + j * d) + b ** (n + j * d)) for j, t in enumerate(tap))
                    assert got == a ** n * (a ** d - b ** d) ** r
                    assert val(got, p) == r * s
                    normalized = Fraction(got, p ** r)
                    assert val(normalized.numerator, p) - val(normalized.denominator, p) == r * (s - 1)
                    counts['finite_difference'] += 1

    for a, b in ((2, 1), (5, 3), (7, 2)):
        for N in range(1, 5):
            for d in range(1, 5):
                r, m = 3, 3 * d + 2
                n = N * m - r * d
                assert n >= 1
                for tap in itertools.product((-1, 0, 1), repeat=4):
                    physical = sum(t * (a ** (N * m - (r - j) * d) + b ** (N * m - (r - j) * d)) for j, t in enumerate(tap))
                    forward = sum(t * (a ** (n + j * d) + b ** (n + j * d)) for j, t in enumerate(tap))
                    modes = a ** n * sum(t * (a ** d) ** j for j, t in enumerate(tap)) + b ** n * sum(t * (b ** d) ** j for j, t in enumerate(tap))
                    assert physical == forward == modes
                    counts['physical_arbitrary_taps'] += 1

    for a, b in ((2, 1), (3, 1), (3, 2)):
        for n in (1, 2, 3):
            tap = [a * b, -(a + b), 1]
            assert sum(t * (a ** (n + j) + b ** (n + j)) for j, t in enumerate(tap)) == 0
            tap[0] += 1
            assert sum(t * (a ** (n + j) + b ** (n + j)) for j, t in enumerate(tap)) == a ** n + b ** n
            for t in (-2, 0, 3):
                assert t * (a ** n + b ** n) == a ** n * t + b ** n * t
            counts['explicit_kernel_and_degree_zero'] += 1

    examples = []
    # Deliberate multi-prime and depth-three cases, supplementing author's P=9/1 samples.
    for a, b, n, P in ((8, 1, 3, 9), (26, 1, 3, 27),
                       (224, 1, 1, 225), (223, 2, 1, 225),
                       (1224, 1, 1, 1225), (2, 1, 18, 1)):
        assert math.gcd(a, b) == math.gcd(P, a - b) == 1
        assert (a ** n + b ** n) % P == 0
        nonzero_preserving = 0
        for tap in itertools.product(range(-2, 3), repeat=4):
            ta = sum(t * a ** j for j, t in enumerate(tap))
            tb = sum(t * b ** j for j, t in enumerate(tap))
            difference = ta - tb
            output = sum(t * (a ** (n + j) + b ** (n + j)) for j, t in enumerate(tap))
            assert (output % P == 0) == (difference % P == 0)
            assert difference % (a - b) == 0
            if difference == 0:
                assert output == ta * (a ** n + b ** n)
            elif difference % P == 0:
                nonzero_preserving += 1
                assert abs(difference) >= P * (a - b)
                assert abs(difference) <= sum(abs(t) for t in tap) * (a ** 3 + b ** 3)
            counts['preserving_arbitrary_taps'] += 1
        assert P * a - P * b == P * (a - b)
        examples.append(dict(A=a, B=b, n=n, P=P, nonzero_preserving=nonzero_preserving))

    root = Path(__file__).resolve().parent
    data = dict(status='passed', arithmetic='exact integers and Fraction', counts=counts,
                source_hashes={name: hashlib.sha256((root / 'source' / name).read_bytes()).hexdigest()
                               for name in ('PROOF_NOTE.md', 'verify.py')},
                examples=examples,
                limitations='Finite tests are consistency checks; ideal/minimum and valuation universality are established by the proof audit.')
    (root / 'independent_results.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()

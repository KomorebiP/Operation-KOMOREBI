#!/usr/bin/env python3
"""Exact finite checks for the full-radical route, not a universal proof."""
import hashlib
import json
import math
import platform
from fractions import Fraction
from pathlib import Path


def radical(n):
    out, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            out *= p
            while n % p == 0:
                n //= p
        p += 1
    return out * n


def is_prime(n):
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


def is_squarefree(n):
    return radical(n) == n


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def b_one(n):
    """Integer exponent t=1 checks telescoping, not series convergence."""
    out, p = 1, 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e == 1:
            return 0
        if e >= 2:
            out *= p ** (e - 1) - p ** (e - 2)
        p += 1
    return 0 if n > 1 else out


def main():
    root = Path(__file__).resolve().parent
    assertion_counts = {}
    checked = 0
    for n in range(1, 3001):
        assert sum(b_one(d) for d in divisors(n)) == n // radical(n)
        checked += 1
    assertion_counts['integer_telescoping_1_to_3000'] = checked

    checked = 0
    hits = 0
    for H in (20, 50, 100, 200):
        for h in range(H // 2 + 1, H + 1):
            if not is_squarefree(h):
                continue
            for Q in range(1, 301):
                if math.gcd(h, Q) != 1:
                    continue
                c = 1 + h * Q
                rq, rc = radical(Q), radical(c)
                R = h * rq * rc
                U = c // rc
                # epsilon = 1/10. Both exact integer forms must agree.
                bad = c ** 10 > R ** 11
                assert bad == (U ** 11 > (h * rq) ** 11 * c)
                if bad:
                    # U^11 > H^12 Q r(Q)^11 / 2^12.
                    assert (2 ** 12) * U ** 11 > H ** 12 * Q * rq ** 11
                    hits += 1
                # Exact sufficient endpoint Q <= H^(1/10).
                if Q ** 10 <= H:
                    assert not bad
                checked += 1
    assertion_counts['quality_equivalence_and_threshold_pairs'] = checked
    assertion_counts['quality_1_10_exceptions_in_tested_pairs'] = hits

    checked = 0
    witnessed = []
    for k in range(2, 9):
        for Q in range(1, 201):
            for u in range(2, 81):
                c = u ** k
                if (c - 1) % Q:
                    continue
                h = (c - 1) // Q
                # Trial primality is restricted to h<=100000 for bounded cost.
                if h > 100000 or math.gcd(h, Q) != 1 or not is_prime(h):
                    continue
                assert h * Q <= (Q + 1) ** k - 1
                if len(witnessed) < 8:
                    witnessed.append({'k': k, 'Q': Q, 'u': u, 'h': h})
                checked += 1
    assertion_counts['perfect_power_witnesses_Q_200_k_8_u_80_h_100000'] = checked

    eps = Fraction(1, 10)
    gamma = eps / (1 + eps)
    A, t = Fraction(1, 2), Fraction(99, 100)
    E = 1 + A - t * (1 + gamma * (1 + A))
    assert E == Fraction(3, 8)

    result = {
        'status': 'completed',
        'interpretation': 'Exact finite consistency checks; no ABC proof and no test of asymptotic constants.',
        'python': platform.python_version(),
        'assertion_counts': assertion_counts,
        'perfect_power_sample_witnesses': witnessed,
        'explicit_exponent': str(E),
        'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'proof_sha256': hashlib.sha256((root / 'PROOF.md').read_bytes()).hexdigest(),
    }
    (root / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

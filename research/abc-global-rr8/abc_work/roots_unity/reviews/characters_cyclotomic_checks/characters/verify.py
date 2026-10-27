#!/usr/bin/env python3
"""Exact finite tests of conductor, depth, and joint-contact formulas."""
import hashlib
import json
import math
import platform
from fractions import Fraction
from pathlib import Path


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def mobius(n):
    sign, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            sign *= -1
            if n % p == 0:
                return 0
        p += 1
    return -sign if n > 1 else sign


def ramanujan(q, t):
    return sum(d * mobius(q // d) for d in divisors(math.gcd(q, t)))


def valuation(n, p):
    assert n != 0
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def order_brute(x, q):
    assert math.gcd(x, q) == 1
    y = 1
    for d in range(1, q + 1):
        y = y * x % q
        if y == 1:
            return d
    raise AssertionError('order not found')


def is_contact(A, B, n, q):
    return (pow(A, n, q) + pow(B, n, q)) % q == 0


def main():
    root = Path(__file__).resolve().parent
    counts = {}
    k = 0
    for q in range(1, 101):
        for t in range(-100, 201):
            assert sum(ramanujan(d, t) for d in divisors(q)) == q * (t % q == 0)
            k += 1
    counts['general_conductor_identity_q_1_100_t_minus100_200'] = k

    k = 0
    for p in (3, 5, 7, 11):
        for e in range(1, 5):
            q = p ** e
            # Every residue is tested, including t=0.
            for t in range(q):
                expected = q * (t % q == 0) - (q // p) * (t % (q // p) == 0)
                assert ramanujan(q, t) == expected
                k += 1
    counts['prime_power_conductor_shell_all_residues'] = k

    order_cases, contact_cases, mean_cases = 0, 0, 0
    for A in range(2, 11):
        for B in range(1, A):
            if math.gcd(A, B) != 1:
                continue
            for p in (3, 5, 7, 11, 13):
                if A * B % p == 0:
                    continue
                d = order_brute(A * pow(B, -1, p) % p, p)
                s = valuation(A ** d - B ** d, p)
                for e in range(1, 4):
                    q = p ** e
                    de = d * p ** max(0, e - s)
                    assert order_brute(A * pow(B, -1, q) % q, q) == de
                    order_cases += 1
                    for n in range(1, 2 * de + 1):
                        predicted = d % 2 == 0 and n % de == de // 2
                        assert is_contact(A, B, n, q) == predicted
                        contact_cases += 1
                L = max(2, s)
                # The mean contract uses L=s or 2, not an unbounded average.
                dL = d * p ** max(0, L - s)
                observed = Fraction(sum(sum(is_contact(A, B, n, p ** e)
                                             for e in range(2, L + 1))
                                        for n in range(1, dL + 1)), dL)
                if d % 2 == 0:
                    predicted = (Fraction(s - 1) + sum((Fraction(1, p ** j)
                                                        for j in range(1, L - s + 1)), Fraction(0))) / d
                else:
                    predicted = Fraction(0)
                assert observed == predicted
                mean_cases += 1
    counts['order_lifting_base_A_2_10_B_lt_A_p_3_5_7_11_13_e_1_3'] = order_cases
    counts['exponent_contact_checks_two_complete_periods_each'] = contact_cases
    counts['exact_truncated_local_mean_checks'] = mean_cases

    # Joint projectors: complete periods for specified small base/prime/depth data.
    joint_cases, joint_parameters = 0, 0
    for A, B in ((2, 1), (3, 1), (5, 2), (224, 1)):
        for p, r in ((3, 5), (3, 7), (3, 11), (5, 7)):
            if math.gcd(A * B, p * r) != 1:
                continue
            dp = order_brute(A * pow(B, -1, p) % p, p)
            dr = order_brute(A * pow(B, -1, r) % r, r)
            sp, sr = valuation(A ** dp - B ** dp, p), valuation(A ** dr - B ** dr, r)
            for ep in (1, 2):
                for er in (1, 2):
                    qp = dp * p ** max(0, ep - sp)
                    qr = dr * r ** max(0, er - sr)
                    D = math.lcm(qp, qr)
                    compatible = dp % 2 == 0 and dr % 2 == 0 and valuation(qp, 2) == valuation(qr, 2)
                    for n in range(1, 2 * D + 1):
                        observed = is_contact(A, B, n, p ** ep) and is_contact(A, B, n, r ** er)
                        assert observed == (compatible and n % D == D // 2)
                        joint_cases += 1
                    joint_parameters += 1
    counts['joint_contact_parameter_cases'] = joint_parameters
    counts['joint_contact_integer_checks_two_complete_periods'] = joint_cases

    p, A, B, N = 1093, 2, 1, 728
    d = order_brute(A, p)
    assert d == 364
    assert valuation(A ** d - 1, p) == 2
    contacts = [n for n in range(1, N + 1) if is_contact(A, B, n, p * p)]
    assert contacts == [182, 546]
    for n in contacts:
        assert not is_contact(A, B, n, p ** 3)
    naive_bound = Fraction(N, d * p) + 1
    assert len(contacts) > naive_bound

    # Arbitrary-depth construction, finitely checked at L=1..8.
    plateaus = []
    for p in (3, 5, 7, 11):
        for L in range(1, 9):
            A = p ** L - 1
            assert order_brute(A % p, p) == 2
            assert valuation(A * A - 1, p) == L
            for n in range(1, 101):
                assert is_contact(A, 1, n, p ** L) == (n % 2 == 1)
            plateaus.append([p, L])
    counts['arbitrary_depth_construction_parameter_cases'] = len(plateaus)

    data = {
        'status': 'completed',
        'assertion_tested': 'Finite exact checks of displayed projector, order, contact, and mean identities; explicit counterexample to depth-rarity bound.',
        'non_claims': ['No ABC proof.', 'No universal bound on weighted exceptional birth depths.', 'No floating Fourier approximation or independent-prime assumption.'],
        'python': platform.python_version(),
        'counts': counts,
        'depth_rarity_counterexample': {'A': 2, 'B': 1, 'p': 1093, 'e': 2, 'd': d, 's': 2, 'N': N,
                                       'actual_contact_exponents': contacts, 'proposed_upper_bound': str(naive_bound)},
        'input_hashes': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ('PROOF_NOTE.md', 'verify.py')},
    }
    (root / 'verification.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Exact finite checks for radical-ceiling counting theorems.
No third-party packages. Uses deterministic Miller–Rabin for 64-bit integers.
"""
import json
import math
from pathlib import Path


def primes_upto(n):
    if n < 2:
        return []
    sieve = bytearray(b'\x01') * (n + 1)
    sieve[0:2] = b'\x00\x00'
    for p in range(2, math.isqrt(n) + 1):
        if sieve[p]:
            sieve[p * p:n + 1:p] = b'\x00' * ((n - p * p) // p + 1)
    return [p for p in range(2, n + 1) if sieve[p]]


def factor(n):
    assert n >= 1
    rem = n
    out = {}
    for p in primes_upto(math.isqrt(n) + 1):
        if p * p > rem:
            break
        if rem % p == 0:
            ex = 0
            while rem % p == 0:
                rem //= p
                ex += 1
            out[p] = ex
    if rem > 1:
        out[rem] = out.get(rem, 0) + 1
    return out


def radical(n):
    v = 1
    for p in factor(n):
        v *= p
    return v


def is_prime64(n):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def bounded_radical_values(X, Y):
    """Return (n, rad n), n>1, rad n<=Y, with no duplicate n."""
    pp = primes_upto(Y)
    result = []
    def recur(start, product, d):
        if product > 1:
            result.append((product, d))
        for j in range(start, len(pp)):
            p = pp[j]
            if d * p > Y:
                break
            v = product * p
            while v <= X:
                recur(j + 1, v, d * p)
                v *= p
    recur(0, 1, 1)
    assert len(result) == len(set(n for n, _ in result))
    return result


def classification(Q, H):
    K = Q // radical(Q)
    all_output_candidates = bounded_radical_values(1 + H * Q, K)
    candidates = []
    for c, rc in all_output_candidates:
        if (c - 1) % Q:
            continue
        h = (c - 1) // Q
        if not 2 <= h <= H or math.gcd(h, Q) != 1:
            continue
        candidates.append({'h': h, 'c': c, 'rad_c': rc, 'is_prime': is_prime64(h)})
    candidates.sort(key=lambda v: v['h'])
    hits = [v for v in candidates if v['is_prime']]
    for v in hits:
        assert v['c'] > radical(Q * v['h'] * v['c'])
        assert v['rad_c'] <= K
    return {'Q': Q, 'H': H, 'U_Q': K,
            'output_candidates': len(all_output_candidates),
            'congruence_candidates': len(candidates),
            'prime_multiplier_hits': hits,
            'candidate_multipliers': [v['h'] for v in candidates]}


def brute_checks(limit=300):
    tests = 0
    for a in range(1, limit+1):
        for b in range(1, limit+1):
            if math.gcd(a, b) != 1:
                continue
            c = a + b
            ra, rb, rc = radical(a), radical(b), radical(c)
            ua, ub = a // ra, b // rb
            lhs = c > ra*rb*rc
            rhs_exact = rc*ra*rb < ra*ua + rb*ub
            assert lhs == rhs_exact
            # delta = 1/2 and 1/3 as exact integer inequalities.
            if (ua+ub)**2 <= c:
                assert c <= (ra*rb*rc)**2
            if (ua+ub)**3 <= c:
                assert c**2 <= (ra*rb*rc)**3
            # For epsilon=1/2, gamma=1/3.
            if c**2 > (ra*rb*rc)**3:
                assert (ua+ub)**3 > c
            tests += 1
    return tests


def offset_checks(limit_h=200, max_a=30, max_q=90):
    tests = 0
    for a in range(1, max_a+1):
        ra = radical(a)
        for Q in range(2, max_q+1):
            if math.gcd(a,Q) != 1:
                continue
            rQ = radical(Q); K = Q//rQ
            for h in primes_upto(limit_h):
                if math.gcd(h,a*Q) != 1 or h*rQ < a:
                    continue
                c = a+h*Q
                left = c > ra*h*rQ*radical(c)
                right = ra*radical(c) <= K
                assert left == right, (a,Q,h,c,left,right)
                tests += 1
    return tests


def example_factors():
    examples=[(4,2,9),(9,7,64),(16,3,49),(16,5,81),
              (243,5,1216),(243,241,58564),(243,643,156250)]
    return [{'Q':Q,'h':h,'c':c,'factors':factor(c),'quality_ratio':str(c)+'/'+str(radical(h*Q*c))}
            for Q,h,c in examples]


def main():
    proof_checks = {'two_sided_primitive_triples': brute_checks(300),
                    'fixed_offset_exact_ceiling': offset_checks()}
    enumeration = [classification(Q,H) for Q,H in
                   [(4,1000000),(8,1000000),(9,1000000),(16,1000000),
                    (243,1000000),(243,1000000000)]]
    assert [h['h'] for h in enumeration[0]['prime_multiplier_hits']] == []
    assert [h['h'] for h in enumeration[1]['prime_multiplier_hits']] == []
    assert [h['h'] for h in enumeration[2]['prime_multiplier_hits']] == [7]
    assert [h['h'] for h in enumeration[3]['prime_multiplier_hits']] == [3,5]
    assert [h['h'] for h in enumeration[-1]['prime_multiplier_hits']] == [5,241,643]
    results = {'claim':'finite arithmetic checks only; proofs in PROOF_NOTE.md',
               'checks':proof_checks,'enumerations':enumeration,
               'examples':example_factors()}
    dest=Path(__file__).with_name('RESULTS.json')
    dest.write_text(json.dumps(results,indent=2,sort_keys=True,default=str)+'\n')
    print(json.dumps({'checks': proof_checks, 'samples':[
        {k:v for k,v in e.items() if k in ('Q','H','U_Q','output_candidates','congruence_candidates','prime_multiplier_hits')}
        for e in enumeration]},indent=2))

if __name__ == '__main__':
    main()

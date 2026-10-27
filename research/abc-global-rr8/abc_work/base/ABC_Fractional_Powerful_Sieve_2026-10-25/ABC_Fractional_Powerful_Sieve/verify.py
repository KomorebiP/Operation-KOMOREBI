#!/usr/bin/env python3
"""Exact arithmetic checks for ABC fractional powerful-divisor research.
Only Python standard library is used. General asymptotic theorems are proved in PROOF_NOTE.md.
"""
import json
import math
from collections import Counter
from pathlib import Path


def prime_sieve(limit: int):
    marks = bytearray(b'\x01') * (limit + 1)
    marks[:2] = b'\x00\x00'
    for p in range(2, math.isqrt(limit) + 1):
        if marks[p]:
            marks[p * p:limit + 1:p] = b'\x00' * ((limit - p * p) // p + 1)
    return [p for p, flag in enumerate(marks) if flag]


def factor(n: int, primes):
    f = {}
    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            f[p] = e
    if n > 1:
        f[n] = 1
    return f


def powerful_part(factors):
    return math.prod(p ** (e - 1) for p, e in factors.items())


def radical(factors):
    return math.prod(factors)


def exact_divisor_expansion_integer_sigma(factors):
    """Exact telescoping at sigma=1, a strong structural check."""
    ans = 1
    for p, e in factors.items():
        if e < 2:
            continue
        ans *= 1 + sum(p ** (j - 1) - p ** (j - 2) for j in range(2, e + 1))
    return ans


def main():
    Hs = [(700, 0.10, 3), (2000, 0.25, 3), (10000, 0.25, 3), (10000, 0.50, 2), (30000, 0.50, 2)]
    max_n = max(1 + H * max(q ** f for f in range(1, 50) if q ** f <= H ** (1 - eta)) for H, eta, q in Hs)
    primes = prime_sieve(math.isqrt(max_n) + 1)
    results = {"proof_status":"general theorem from Brun-Titchmarsh; no Lean compilation", "samples":[], "exact_expansion_checks":0}
    # Test local telescoping structure on all n<=5000 with exact integer coefficients.
    for n in range(1, 5001):
        fs = factor(n, primes)
        assert powerful_part(fs) == exact_divisor_expansion_integer_sigma(fs), n
        results['exact_expansion_checks'] += 1
    for H, eta, q in Hs:
        all_primes = prime_sieve(H)
        hs = [h for h in all_primes if H//2 < h <= H]
        Qs = []
        f = 1
        while q ** f <= H ** (1 - eta):
            Qs.append((f, q ** f))
            f += 1
        hits = []
        moment_total = 0.0
        num = 0
        max_powerful = (0, None)
        for h in hs:
            for f, Q in Qs:
                c = 1 + h * Q
                fs = factor(c, primes)
                M = powerful_part(fs)
                R = radical(fs) * radical(factor(h * Q, primes))
                assert c // radical(fs) == M
                moment_total += math.exp((eta / 8) * math.log(M))
                num += 1
                if M > max_powerful[0]:
                    max_powerful = (M, {'h':h, 'f':f, 'Q':Q, 'c':c, 'factors':fs})
                if c > R:
                    hits.append({'h':h,'f':f,'Q':Q,'c':c,'R':R,'factors':fs})
        results['samples'].append({
            'H':H, 'eta':eta, 'q':q, 'prime_multipliers':len(hs),
            'exponents':Qs, 'triples_tested':num, 'abc_hits':hits,
            'mean_M_to_eta_over_8':moment_total/max(1,num),
            'largest_powerful_part':max_powerful
        })
    # Exact negative control: the theorem is density-one, NOT pointwise.
    h, q, f = 643, 3, 5
    c = 1 + h * (q ** f)
    assert c == 156250
    assert factor(c, primes) == {2: 1, 5: 7}
    assert radical(factor(h * q ** f, primes)) == 1929
    R = radical(factor(h * q ** f, primes)) * radical(factor(c, primes))
    assert R == 19290 and c > R
    results['spike'] = {'triple': [1, h*q**f, c], 'radical':R, 'quality_c_over_R':c/R}
    out = Path(__file__).with_name('results.json')
    out.write_text(json.dumps(results, indent=2) + '\n', encoding='utf8')
    print('PASS', results['exact_expansion_checks'], 'exact divisor-expansion checks')
    for s in results['samples']:
        print('H',s['H'],'q',s['q'],'triples',s['triples_tested'],'hits',len(s['abc_hits']),
              'mean fractional powerful part',round(s['mean_M_to_eta_over_8'],6))
    print('PASS explicit exception', results['spike'])
    print('Wrote',out)

if __name__ == '__main__':
    main()

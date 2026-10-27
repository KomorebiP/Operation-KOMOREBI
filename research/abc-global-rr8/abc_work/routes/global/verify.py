#!/usr/bin/env python3
"""Exact finite checks of the pure-power lifting identities, not ABC itself.

Run: python3 verify.py
Domain: coprime 1<=B<A<=10, 1<=n<=12. No random sampling or early exits.
"""
from pathlib import Path
from math import gcd, prod
import hashlib
import json
import platform
import time


def factor(n):
    out = {}
    d = 2
    while d*d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def val(n, p):
    ans = 0
    while n % p == 0:
        ans += 1
        n //= p
    return ans


def order(A, B, p):
    d = p-1
    for ell in factor(p-1):
        while d % ell == 0 and pow(A, d//ell, p) == pow(B, d//ell, p):
            d //= ell
    return d


def direct_order(A, B, p):
    a = b = 1
    for d in range(1, p):
        a = a*A % p
        b = b*B % p
        if a == b:
            return d
    raise AssertionError('order not found')


def birth_depth(A, B, d, p, cap):
    e = 0
    while e <= cap and pow(A, d, p**(e+1)) == pow(B, d, p**(e+1)):
        e += 1
    assert e <= cap, 'valuation did not terminate inside proved finite bound'
    return e


def main():
    start = time.monotonic()
    script = Path(__file__)
    hash_before = hashlib.sha256(script.read_bytes()).hexdigest()
    pairs = points = prime_contacts = independent_order_checks = prime_exponent_checks = binary_exponent_checks = 0
    exceptional_contacts = []
    for A in range(2, 11):
        for B in range(1, A):
            if gcd(A, B) != 1:
                continue
            pairs += 1
            for n in range(1, 13):
                points += 1
                c = A**n + B**n
                fs = factor(c)
                assert prod(p**e for p,e in fs.items()) == c
                W = G = ordinary = Wprim = 1
                for p,e in fs.items():
                    if p == 2:
                        continue
                    prime_contacts += 1
                    d = order(A, B, p)
                    if p <= 1000:
                        assert d == direct_order(A, B, p)
                        independent_order_checks += 1
                    assert (p-1) % d == 0 and d % 2 == 0
                    assert (2*n) % d == 0 and (2*n//d) % 2 == 1
                    ep = birth_depth(A, B, d, p, e+1)
                    assert e == ep + val(n, p)
                    W *= p**(ep-1)
                    if d == 2*n:
                        Wprim *= p**(ep-1)
                        assert p >= 2*n+1
                    G *= p**val(n, p)
                    if ep == 1:
                        ordinary *= p**(e-1)
                    else:
                        exceptional_contacts.append([A,B,n,p,e,ep,d])
                B2 = 2**max(fs.get(2,0)-1,0)
                if (A+B) % 2 == 1 or n % 2 == 0:
                    assert B2 == 1
                else:
                    assert B2 == 2**(val(A+B,2)-1)
                assert B2 <= A
                U = c//prod(fs)
                assert U == B2*W*G
                assert n % G == 0 and n % ordinary == 0
                if n in (3,5,7,11):
                    ab = A+B
                    Uab = ab//prod(factor(ab))
                    assert U == Uab*(n if ab%n==0 else 1)*Wprim
                    prime_exponent_checks += 1
                if n in (2,4,8):
                    assert B2 == G == 1 and U == W == Wprim
                    binary_exponent_checks += 1
    p=1093
    d=order(2,1,p)
    ep=birth_depth(2,1,d,p,5)
    n=182
    c=2**n+1
    assert d==364 and ep==2 and val(c,p)==2 and n%p!=0
    hash_after=hashlib.sha256(script.read_bytes()).hexdigest()
    assert hash_before==hash_after
    result={
        'status':'completed',
        'outcome':'exact finite assertions verified in stated range',
        'assertion_tested':'valuation identity, exact powerful-part factorization, G_n|n, ordinary part|n, and 2-adic branch formulas',
        'domain':{'A':[2,10],'B':'1<=B<A, gcd(A,B)=1','n':[1,12],'exhaustive':True},
        'pairs':pairs,'points':points,'odd_prime_contacts':prime_contacts,
        'independent_naive_order_checks':independent_order_checks,
        'prime_exponent_identity_checks':prime_exponent_checks,
        'power_of_two_exponent_identity_checks':binary_exponent_checks,
        'exceptional_contacts':exceptional_contacts,
        'negative_control':{'base':2,'p':p,'n':n,'order':d,'birth_depth':ep,'output_valuation':2,'p_divides_n':False},
        'software':{'python':platform.python_version(),'platform':platform.platform()},
        'script_sha256_before':hash_before,'script_sha256_after':hash_after,
        'runtime_seconds':time.monotonic()-start,
        'non_claims':['not a proof of ABC','not a distribution theorem for exceptional primes','not Lean compiled']
    }
    Path('verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='exceptional_contacts'},indent=2))


if __name__=='__main__':
    main()

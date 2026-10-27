#!/usr/bin/env python3
"""Independent exact checks supplementing, not proving, the reviewed claims.

No imports from route verifiers. Polynomial coefficients are ascending.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from math import gcd, lcm
from pathlib import Path
import hashlib
import json


def trim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def monic_div(a, b):
    a, b = trim(a), trim(b)
    assert b[-1] == 1
    q = [0] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and a != [0]:
        j, c = len(a) - len(b), a[-1]
        q[j] += c
        for i, x in enumerate(b):
            a[i+j] -= c*x
        a = trim(a)
    return trim(q), trim(a)


@lru_cache(None)
def cyclotomic(n):
    f = [-1] + [0]*(n-1) + [1]
    for d in range(1, n):
        if n % d == 0:
            f, remainder = monic_div(f, cyclotomic(d))
            assert remainder == [0]
    return tuple(f)


def reduction(a, n):
    return monic_div(a, cyclotomic(n))[1]


def v(x, p):
    assert x != 0
    out = 0
    while x % p == 0:
        x //= p
        out += 1
    return out


def order(x, m):
    assert gcd(x, m) == 1
    y = x % m
    d = 1
    while y != 1:
        y = y*x % m
        d += 1
    return d


def contact(a, b, n, m):
    return (pow(a, n, m) + pow(b, n, m)) % m == 0


def factor(x):
    out = {}
    p = 2
    while p*p <= x:
        if x % p == 0:
            out[p] = v(x, p)
            x //= p**out[p]
        p += 1
    if x > 1:
        out[x] = 1
    return out


def determinant(a):
    a = [list(r) for r in a]
    size = len(a)
    if size == 0:
        return 1
    previous, sign = 1, 1
    for k in range(size-1):
        if a[k][k] == 0:
            pivot = next((i for i in range(k+1, size) if a[i][k]), None)
            if pivot is None:
                return 0
            a[k], a[pivot] = a[pivot], a[k]
            sign *= -1
        for i in range(k+1, size):
            for j in range(k+1, size):
                numerator = a[i][j]*a[k][k] - a[i][k]*a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator // previous
        previous = a[k][k]
        for i in range(k+1, size):
            a[i][k] = 0
    return sign*a[-1][-1]


def resultant(f, g):
    f, g = trim(f), trim(g)
    m, n = len(f)-1, len(g)-1
    if n == 0:
        return g[0]**m
    rows = []
    for i in range(n):
        rows.append([0]*i + list(reversed(f)) + [0]*(n-1-i))
    for i in range(m):
        rows.append([0]*i + list(reversed(g)) + [0]*(m-1-i))
    return determinant(rows)


def eval_homogeneous(f, a, b):
    degree = len(f)-1
    return sum(c*a**i*b**(degree-i) for i, c in enumerate(f))


def formal_excluded(n, omitted):
    # A - t*zeta**j, with A,t algebraically independent.
    f = {(0, 0, 0): 1}
    for j in range(n):
        if j == omitted:
            continue
        g = defaultdict(int)
        for (a, t, z), c in f.items():
            g[a+1, t, z] += c
            g[a, t+1, (z+j) % n] -= c
        f = g
    return f


def main():
    counts = defaultdict(int)
    # Character sums are evaluated in Z[X]/Phi_q rather than via Mobius sums.
    for q in range(1, 41):
        for t in range(q):
            full, primitive = [0]*q, [0]*q
            for j in range(q):
                full[j*t % q] += 1
                if gcd(j, q) == 1:
                    primitive[j*t % q] += 1
            assert reduction(full, q) == [q if t == 0 else 0]
            for p in (3, 5, 7):
                e = 0
                z = q
                while z % p == 0:
                    z //= p
                    e += 1
                if e and z == 1:
                    shell = q*(t % q == 0) - (q//p)*(t % (q//p) == 0)
                    assert reduction(primitive, q) == [shell]
            counts['exact_cyclotomic_character_residues_q_1_40'] += 1

    # Formal cleared resolvent identity, including n=1 and every mode.
    for n in range(1, 10):
        for k in range(n):
            coefficients = defaultdict(lambda: [0]*n)
            for j in range(n):
                for (a, t, z), c in formal_excluded(n, j).items():
                    coefficients[a, t][(z-k*j) % n] += c
            for (a, t), f in coefficients.items():
                expected = n if (a, t) == (n-1-k, k) else 0
                assert reduction(f, n) == [expected]
            counts['formal_resolvent_modes_n_1_9'] += 1

    # Means beyond the birth plateau; author mean grid only uses L=max(2,s).
    for a in range(2, 9):
        for b in range(1, a):
            if gcd(a, b) != 1:
                continue
            for p in (3, 5, 7):
                if a*b % p == 0:
                    continue
                d = order(a*pow(b, -1, p) % p, p)
                s = v(a**d-b**d, p)
                if d % 2:
                    continue
                for L in range(max(2, s), max(2, s)+3):
                    period = d*p**max(0, L-s)
                    observed = sum((sum(contact(a,b,n,p**e) for e in range(2,L+1))
                                    for n in range(1,period+1)), 0)
                    rhs = (Fraction(s-1)+sum((Fraction(1,p**j) for j in range(1,L-s+1)), Fraction()))/d
                    assert Fraction(observed, period) == rhs
                    for sigma in (1, 2):
                        moment = Fraction(sum(p**(sigma*min(max(v(a**n+b**n,p)-1,0), L-1))
                                              for n in range(1, period+1)), period)
                        predicted = 1 + sum((Fraction(p**(sigma*(e-1))-p**(sigma*(e-2)),
                                                      d*p**max(0,e-s)) for e in range(2,L+1)), Fraction())
                        assert moment == predicted
                        counts['truncated_moment_checks_sigma_1_2'] += 1
                    counts['local_mean_checks_three_L_values'] += 1

    # Full Sylvester determinant and homogeneous B>1 scaling.
    for n in range(1, 9):
        h = cyclotomic(2*n)
        candidates = ([1], [-2,1]) if n > 1 else ([1], [-2])
        for seed in range(3):
            candidates += ([((i+seed) % 3)-1 for i in range(n)],)
        for q in candidates:
            q = trim(q)
            if q == [0]:
                continue
            R = resultant(h,q)
            if R == 0:
                continue
            assert abs(R) <= sum(map(abs,q))**(len(h)-1)
            counts['sylvester_resultant_height_checks'] += 1
            for a in range(2,9):
                for b in range(1,a):
                    if gcd(a,b) != 1:
                        continue
                    # Homogenize q to total degree n-1, exactly as in note.
                    P = sum(c*a**i*b**(n-1-i) for i,c in enumerate(q))
                    packet = 1
                    for p,e in factor(a**n+b**n).items():
                        if p==2 or order(a*pow(b,-1,p)%p,p) != 2*n:
                            continue
                        canceled = e if P==0 else min(e,v(P,p))
                        assert canceled <= v(R,p)
                        packet *= p**canceled
                        counts['homogeneous_primitive_resultant_contacts'] += 1
                    assert abs(R) % packet == 0
    assert resultant([1,0,1],[-7,1]) == 50
    assert resultant([1,0,1],[1,1]) == 2
    for n in (2,4,8,16):
        assert abs(resultant(cyclotomic(2*n),[-2,1])) == 2**n+1
        counts['moving_conductor_resultant_checks'] += 1
    data={'status':'passed','proof_status':'finite consistency checks only',
          'counts':dict(counts),
          'method':'exact integer polynomial reduction, formal cleared resolvents, rational means, and independent Sylvester determinants',
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (Path(__file__).parent/'independent_results.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))


if __name__ == '__main__':
    main()

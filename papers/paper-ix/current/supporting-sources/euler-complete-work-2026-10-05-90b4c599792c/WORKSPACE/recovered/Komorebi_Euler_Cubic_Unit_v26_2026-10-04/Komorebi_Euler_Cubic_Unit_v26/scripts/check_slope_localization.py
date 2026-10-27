#!/usr/bin/env python3
"""Exact finite corroboration of the v21 local slope theorems.

These are synthetic polynomial tests, not numerical Euler-family certificates.
The actual Euler-specific scope is proved in the Lean source. No external
Python packages are used. Output refuses overwrite.
"""
from __future__ import annotations
import argparse
from collections import Counter
from math import comb, factorial
from pathlib import Path
import json
import time

Poly = list[int]


def trim(a: Poly) -> Poly:
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def add(a: Poly, b: Poly) -> Poly:
    out = [0] * max(len(a), len(b))
    for i, x in enumerate(a): out[i] += x
    for i, x in enumerate(b): out[i] += x
    return trim(out)


def scale(a: Poly, c: int) -> Poly:
    return trim([c * x for x in a])


def mul(a: Poly, b: Poly) -> Poly:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): out[i+j] += x*y
    return trim(out)


def at(a: Poly, x: int, modulus: int | None = None) -> int:
    z = 0
    for c in reversed(a):
        z = z*x+c
        if modulus is not None: z %= modulus
    return z


def deriv(a: Poly) -> Poly:
    return [i*a[i] for i in range(1, len(a))] or [0]


def affine_binomial(a: Poly, center: int, step: int) -> Poly:
    """Direct binomial expansion, independent of product chart construction."""
    out = [0] * len(a)
    for n, c in enumerate(a):
        for i in range(n+1):
            out[i] += c*comb(n, i)*center**(n-i)*step**i
    return trim(out)


def v2(n: int) -> int:
    if n == 0:
        raise ValueError('v2(0) must not be assigned a finite value')
    n = abs(n)
    return (n & -n).bit_length()-1


def residue(a: Poly, modulus: int = 2) -> Poly:
    return trim([x % modulus for x in a])


def divide_exact(a: Poly, exponent: int) -> Poly:
    if exponent < 0:
        raise ValueError('negative content exponent')
    d = 1 << exponent
    if any(x % d for x in a):
        raise AssertionError('nonintegral coefficient division')
    return trim([x//d for x in a])


def packet(j: int) -> Poly:
    out = [1]
    for ell in range(j):
        out = mul(out, mul([-ell, 1], [-2*ell-1, 2]))
    return out


def skeleton_chart(j: int, i: int, k: int) -> Poly:
    s = 1 << k
    out = [1]
    for ell in range(j):
        out = mul(out, mul([i-ell, s], [2*i-2*ell-1, 2*s]))
    return out


def lift_affine(a: Poly, bits: int) -> int:
    """Unique residue lift for a polynomial with complete affine reduction."""
    if len(residue(a)) != 2 or residue(a)[1] != 1:
        raise ValueError('not an affine-unit reduction')
    root = 0
    for p in range(1, bits+1):
        mod = 1 << p
        choices = [root, root + (1 << (p-1))]
        roots = [x for x in choices if at(a, x, mod) == 0]
        if len(roots) != 1:
            raise AssertionError('nonunique lift')
        root = roots[0]
    if at(deriv(a), root, 2) != 1:
        raise AssertionError('derivative is not odd')
    return root


def audit(max_j: int) -> dict[str, object]:
    if not 2 <= max_j <= 64:
        raise ValueError('--max-j must lie between 2 and 64')
    counts: Counter[str] = Counter()
    lifts = 0
    t0 = time.monotonic()
    for j in range(2, max_j+1):
        global_p = packet(j)
        for i in range(j):
            k = max(i, j-1-i).bit_length()
            d = v2(factorial(i)) + v2(factorial(j-1-i))
            t = k+d
            pc = skeleton_chart(j, i, k)
            assert pc == affine_binomial(global_p, i, 1 << k)
            assert residue(divide_exact(pc, t)) == [0, 1]
            counts['exact_skeleton_charts'] += 1
            # A genuinely nonconstant global analytic unit, U(x-j)=1+2(x-j)+4(x-j)^2.
            z = i-j
            uc = [1+2*z+4*z*z, (2+8*z)*(1 << k), 4*(1 << (2*k))]
            sc = mul(pc, uc)
            assert residue(divide_exact(sc, t)) == [0, 1]
            counts['nonconstant_upper_unit_charts'] += 1
            # Root-containing lower center: V(i+2^kY)=2^k(w+Y+2^(k+1)Y^2).
            for w in range(4):
                lc = [((1 << k)*w), 1 << k, 1 << (2*k+1)]
                for delta in sorted({0, max(0, d-1), d, d+1, t+1}):
                    g = add(sc, scale(lc, 1 << delta))
                    c = k+min(d, delta)
                    f = divide_exact(g, c)
                    expected = [w % 2, 1] if delta < d else ([0, 1] if delta > d else [w % 2])
                    assert residue(f) == expected
                    counts['root_containing_full_coefficient_cases'] += 1
                    if delta != d and lifts < 300:
                        alpha = lift_affine(f, 8)
                        assert at(g, alpha, 1 << (c+8)) == 0
                        assert v2(at(deriv(g), alpha)) == c
                        lifts += 1
            # Shallow lower value, with exact center content s<k and odd unit w.
            for s in sorted({0, k-1}):
                for w in (1, 3):
                    lc = [(1 << s)*w, 1 << k, 1 << (2*k+1)]
                    for delta in sorted({0, max(0, t-s-1), t-s, t-s+1}):
                        g = add(sc, scale(lc, 1 << delta))
                        c = min(t, delta+s)
                        f = divide_exact(g, c)
                        expected = [1] if delta+s<t else ([1,1] if delta+s==t else [0,1])
                        assert residue(f) == expected
                        counts['shallow_lower_full_coefficient_cases'] += 1
    counts['simple_root_modular_lifts_8_bits'] = lifts
    # Candidate cardinality and parity uniqueness with both one- and two-root lower functions.
    for j in range(2, 65):
        ds = []
        ks = []
        for i in range(j):
            ks.append(max(i, j-1-i).bit_length())
            ds.append(v2(factorial(i))+v2(factorial(j-1-i)))
        for constant in range(8):
            for quadratic in (1,2):
                v = [constant,1,quadratic]
                aligned = [i for i in range(j) if at(v,i) % (1 << ks[i]) == 0]
                assert len(aligned) <= 2
                assert len({i % 2 for i in aligned}) == len(aligned)
                counts['aligned_candidate_cardinality_cases'] += 1
                for delta in set(ds):
                    cand = [i for i in aligned if ds[i]==delta and at(v,i) % (1 << (ks[i]+1)) == 0]
                    assert len(cand)<=2
                    counts['slope_candidate_cardinality_cases'] += 1
    # Coefficient precision after affine substitution is P+ki, not merely a pointwise estimate.
    errors = [[1,-2,3,4,-5,6], [0,7,0,-3,4,0,1], [5]]
    for e in errors:
        for P in (1,4,8):
            for k in range(1,5):
                for a in range(5):
                    child = affine_binomial(scale(e, 1 << P), a, 1 << k)
                    for n,c in enumerate(child):
                        assert c % (1 << (P+k*n)) == 0
                    counts['affine_full_coefficient_error_bounds'] += 1
    # Negative control: no generic assertion of simplicity at equal slopes.
    p2 = packet(2)
    v = add([0,0,1], scale(p2,-1))
    g = add(p2,v)
    assert g == [0,0,1] and residue(v) == [0,1]
    assert at(g,0)==at(deriv(g),0)==0
    assert at(v,0) % 4 == 0  # extra alignment survives; this is the allowed candidate, not ruled out.
    counts['exact_double_root_negative_control'] += 1
    # Independent actual integer carry example; no giant Euler number is evaluated.
    r=(1 << 63)-17
    bound=(r.bit_count()-1)//3
    costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
    recurrent=[0]
    for q in range(1,bound+1): recurrent.append(recurrent[-1]+4-v2(r+q))
    assert costs==recurrent
    mu=min(costs); minima=[q for q,c in enumerate(costs) if c==mu]
    assert (bound,mu,minima)==(20,-10,[17])
    lower=[3*q+(16).bit_count()-(16-q).bit_count() for q in range(17)]
    assert min(lower)==0 and [q for q,c in enumerate(lower) if c==0]==[0,1]
    slopes=[v2(factorial(i))+v2(factorial(16-i)) for i in range(17)]
    assert min(slopes)==11 and max(slopes)==15
    counts['actual_carry_example_checks'] += 4
    return {'schema':'komorebi.euler.v21.slope-localization-audit.v1',
            'status':'PASS', 'max_j_full_polynomial_checks':max_j,
            'counts':dict(counts), 'registered_checks':sum(counts.values()),
            'actual_carry_example':{'r':r,'terminal_index':17,'minimum':-10,'distance':10},
            'seconds':round(time.monotonic()-t0,6),
            'scope':'Exact finite implementation corroboration. Synthetic polynomials are not Euler-family certificates. Modular root lifts are finite residues, not exact root claims; universal conclusions come from the Lean proofs.'}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--max-j',type=int,default=32)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists(): raise FileExistsError(f'Refusing overwrite: {args.output}')
    result=audit(args.max_j)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()

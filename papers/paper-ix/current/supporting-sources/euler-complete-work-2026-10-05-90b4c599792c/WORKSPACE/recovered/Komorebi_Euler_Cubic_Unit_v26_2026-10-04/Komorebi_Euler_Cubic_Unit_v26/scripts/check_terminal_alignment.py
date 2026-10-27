#!/usr/bin/env python3
"""Finite exact-arithmetic checks for the terminal-wall Lean construction.

Uses Python 3.10+ standard library. These tests corroborate the Lean theorems;
they do not establish their universal quantifiers. Output files are never replaced.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from math import comb, factorial, prod
from pathlib import Path
import time


def v2(n: int) -> int:
    if n == 0:
        raise ValueError('Zero has no finite integer valuation')
    n = abs(n)
    return (n & -n).bit_length() - 1


def rat_v2(x: Fraction) -> int | None:
    return None if not x else v2(x.numerator) - v2(x.denominator)


def pow2(e: int) -> Fraction:
    return Fraction(1 << e) if e >= 0 else Fraction(1, 1 << (-e))


def bernoulli(limit: int) -> list[Fraction]:
    b = [Fraction(1)]
    for n in range(1, limit + 1):
        b.append(-sum((comb(n + 1, k) * b[k] for k in range(n)), Fraction()) / (n + 1))
    return b


def direct_costs(r: int, bound: int) -> list[int]:
    # Independent valuation recurrence, without calling bit_count in the loop.
    vals = [0]
    for q in range(1, bound + 1):
        vals.append(vals[-1] + 4 - v2(r + q))
    return vals


def descriptor(r: int) -> tuple[int, int, int, int, int, int, tuple[int, ...]]:
    bound = (r.bit_count() - 1) // 3
    costs = [3*q + (r+q).bit_count() - r.bit_count() for q in range(bound + 1)]
    mu = min(costs)
    mins = tuple(q for q, c in enumerate(costs) if c == mu)
    j = mins[-1]
    L = v2(r + j)
    b = (r + j) >> L
    if j:
        lower = [3*q + (j-1).bit_count() - (j-q-1).bit_count() for q in range(j)]
        E = min(lower)
        origin = 3*j + 1 + (j-1).bit_count() - E
        delta = L - origin
    else:
        E = delta = 0
    return j, mu, L, b, E, delta, mins


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--max-r', type=int, default=65536)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    if args.max_r < 1:
        ap.error('--max-r must be positive')
    if args.output.exists():
        raise FileExistsError(f'Refusing existing output: {args.output}')
    start = time.monotonic()
    counts: Counter[str] = Counter()
    examples: list[dict[str, object]] = []

    def check(name: str, ok: bool, inputs: object) -> None:
        if not ok:
            raise AssertionError(f'{name}: {inputs!r}')
        counts[name] += 1

    for L in range(13):
        for n in range(1 << L):
            check('digit_complement', ((1 << L) - 1 - n).bit_count() + n.bit_count() == L, (L,n))
            for b in (1,3,10,31):
                check('digit_append', ((b << L) + n).bit_count() == b.bit_count() + n.bit_count(), (L,n,b))

    def check_depth(r: int, retain: bool=False) -> None:
        j, mu, L, b, E, delta, mins = descriptor(r)
        bound = (r.bit_count() - 1) // 3
        vals = direct_costs(r, max(bound + 12, 2*j+4))
        check('minimum_independent_scan', min(vals) == mu and tuple(q for q,c in enumerate(vals) if c==mu)==mins, r)
        check('canonical_factorization', b*(1 << L)==r+j and b%2==1 and j<(1 << L), r)
        check('all_scanned_costs', all(c==3*q+(r+q).bit_count()-r.bit_count() for q,c in enumerate(vals)), r)
        shifted = direct_costs(r+j, bound+12)
        check('shifted_cost_cocycle', all(shifted[q]==3*q+(r+j+q).bit_count()-(r+j).bit_count() for q in range(len(shifted))),r)
        check('shifted_minimum_zero', min(shifted)==0 and all(c>0 for c in shifted[1:]), r)
        if not j:
            return
        lower = vals[:j]
        expected = [3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        check('lower_cost_independence', lower==expected and E==min(lower),r)
        check('wall_distance_nonnegative',delta>=0,r)
        check('minimum_normalization',mu==E-delta,r)
        check('binary_complexity',r.bit_count()==b.bit_count()+3*j-E+delta,r)
        expected_mins = (j,) if delta else tuple(q for q,c in enumerate(lower) if c==E)+(j,)
        check('complete_wall_minimizers',mins==expected_mins,r)
        if j>=2:
            values = [sum(prod(x-i for i in range(q)) for q,c in enumerate(lower) if c==E)%2 for x in (0,1)]
            expected_values = [(int(E==0)+int(lower[1]==E)*x)%2 for x in (0,1)]
            check('lower_binary_values',values==expected_values,r)
            check('pointwise_unit_iff', (values==[1,1]) == (E==0 and lower[1]!=E),r)
        if retain:
            examples.append({'r':str(r),'j':j,'mu':mu,'L':L,'b':str(b),'E':E,'delta':delta,'minimizers':mins})

    for r in range(1,args.max_r+1):
        check_depth(r)
    for j in (1,2,3,5,17,33,65,129,145,258,514):
        e=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        origin=3*j+1+(j-1).bit_count()-min(e)
        for delta in (0,1,3,17):
            for b in (1,3,17,(1<<90)+3):
                check_depth((b << (origin+delta))-j,retain=(delta==0 and b==1))
    check_depth((1<<64)-17,True)
    check('last_not_first_guard', descriptor((1<<64)-17)[0]==17 and direct_costs((1<<64)-17,1)[1]==0, '2^64-17')
    check('actual_254_descriptor', descriptor(254)==(2,0,8,1,0,0,(0,2)),254)

    # Rational values use nonnegative offsets ONLY. No negative source argument
    # or derivative is approximated by a terminating integer-row value formula.
    rs=list(range(1,33))+[47,63,127,254]
    limit=max(rs)+8
    B=bernoulli(2*limit)
    beta=[-pow2(2*m)*(2*m-1)*B[2*m]/factorial(2*m) for m in range(limit+1)]
    kappa=[pow2(2*m)*factorial(2*m)*beta[m] for m in range(limit+1)]
    source=[Fraction(9**(n+1)-1,8*(n+1)*(2*n+1)) for n in range(limit+1)]
    euler=[1]
    for n in range(1,limit+1):
        euler.append(-sum(comb(2*n,2*m)*euler[m] for m in range(n)))

    @lru_cache(None)
    def P(q: int,n: int) -> int:
        return prod((n-i)*(2*n-2*i-1) for i in range(q))

    @lru_cache(None)
    def H(r: int,n: int) -> Fraction:
        if n<0:
            raise ValueError('Finite evaluation is valid only at nonnegative integer offsets')
        return sum((pow2(3*q)*beta[r+q]/beta[r]*P(q,n)*source[n-q] for q in range(n+1)),Fraction())

    for r in rs:
        j,mu,L,b,E,delta,mins=descriptor(r)
        if not j:
            continue
        for x in range(j,9):
            if r+x>limit:
                continue
            V=pow2(-E)*sum((pow2(3*q)*beta[r+q]/beta[r]*P(q,x)*source[x-q] for q in range(j)),Fraction())
            U=pow2(-mu+3*j)*beta[r+j]/beta[r]*H(r+j,x-j)
            g=pow2(-mu)*H(r,x)
            check('rational_wall_factorization',g==P(j,x)*U+pow2(delta)*V,(r,x))
            check('rational_upper_unit',rat_v2(U)==0,(r,x))
            check('rational_lower_integral',not V or rat_v2(V)>=0,(r,x))
            N=r+x
            error=Fraction(euler[N])-sum((kappa[m]*comb(2*N,2*m)*source[N-m] for m in range(r)),Fraction())
            check('independent_euler_wall_error',error==kappa[r]*comb(2*N,2*r)*pow2(mu)*g,(r,x))
            if delta==0 and j>=2 and E==0:
                e1=3+(j-1).bit_count()-(j-2).bit_count()
                if e1!=E:
                    check('equality_wall_exact_row',rat_v2(error)==4*r-1+v2(comb(N,r)),(r,N))
    report={'status':'PASS','scope':'Finite exact tests corroborate the universal Lean proofs; no numerical extrapolation.',
            'max_r':args.max_r,'counts':dict(counts),'registered_checks':sum(counts.values()),
            'seconds':round(time.monotonic()-start,6),'examples':examples,
            'arithmetic':'Python integers and fractions.Fraction; float only for time metadata',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out:
        json.dump(report,out,indent=2);out.write('\n')
    print(json.dumps({k:v for k,v in report.items() if k!='examples'},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())

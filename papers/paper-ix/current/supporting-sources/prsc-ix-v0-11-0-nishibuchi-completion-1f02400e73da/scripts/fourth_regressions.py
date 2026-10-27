#!/usr/bin/env python3
"""Independent exact-rational mirrors for the fourth block, not extracted Lean code.
Author: Komorebi P. No third-party packages or network required.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, inf
from pathlib import Path
import json, random, time
from typing import Callable, Sequence

ROOT=Path(__file__).resolve().parents[1]

def require_nat(*values: int) -> None:
    if any(isinstance(n,bool) or not isinstance(n,int) or n<0 for n in values):
        raise ValueError('Indices, orders and steps must be natural numbers')

def is_prime(p: int) -> bool:
    return p>=2 and all(p%d for d in range(2,int(p**0.5)+1))

def valuation(x: Q | int, p: int) -> int | float:
    if not is_prime(p): raise ValueError('Valuation base must be prime')
    x=Q(x)
    if x==0: return inf
    a=abs(x.numerator);b=x.denominator;v=0
    while a%p==0:a//=p;v+=1
    while b%p==0:b//=p;v-=1
    return v

def coefficients(values: Sequence[Q | int]) -> list[Q]:
    if not values: raise ValueError('At least one sample is required')
    row=list(map(Q,values));ans=[]
    while row:
        ans.append(row[0]);row=[b-a for a,b in zip(row,row[1:])]
    return ans

def eval_newton(c: Sequence[Q | int], n: int) -> Q:
    require_nat(n)
    return sum((Q(c[r])*comb(n,r) for r in range(min(len(c),n+1))),Q(0))

def difference(f: Callable[[int],Q | int], n: int, s: int, h: int=1) -> Q:
    require_nat(n,s,h)
    # Local table is independent of the coefficient-shift and geometric multiplier formulae.
    row=[Q(f(n+j*h)) for j in range(s+1)]
    for _ in range(s):row=[b-a for a,b in zip(row,row[1:])]
    return row[0]

def sample_difference(values: Sequence[Q | int], n: int, s: int) -> Q:
    require_nat(n,s)
    if not values or n+s>=len(values): raise ValueError('Forward stencil exceeds supplied samples')
    return difference(lambda j:values[j],n,s)

def weighted_bound(c: Sequence[Q | int], n: int, s: int, p: int) -> int | float:
    require_nat(n,s)
    if not is_prime(p): raise ValueError('Prime required')
    if any(valuation(Q(x),p)<0 for x in c): raise ValueError('Coefficients must be p-integral')
    return min((valuation(Q(c[s+j]),p)+valuation(comb(n,j),p)
                for j in range(n+1) if s+j<len(c)),default=inf)

def unit_mode(u: Q | int,n: int,s: int,p: int,step_multiple: int=1) -> Q:
    require_nat(n,s,step_multiple)
    if not is_prime(p) or valuation(Q(u),p)!=0:raise ValueError('Prime and p-adic unit required')
    return difference(lambda k:Q(u)**k,n,s,step_multiple*(p-1))

def run() -> dict:
    start=time.monotonic();rng=random.Random(904704)
    counts=dict(sample_arrays=0,reconstructed_values=0,in_range_differences=0,
        interpolants=0,arbitrary_interpolant_differences=0,weighted_cases=0,
        zero_weighted_differences=0,unit_cases=0,finite_mode_cases=0,
        rejected_out_of_range_stencils=0,rejected_nonunit_inputs=0)
    for N in range(21):
      for _ in range(9):
        values=[Q(rng.randint(-200,200),rng.randint(1,11)) for _ in range(N+1)]
        c=coefficients(values);counts['sample_arrays']+=1
        for n in range(N+1):
          assert eval_newton(c,n)==values[n];counts['reconstructed_values']+=1
          for s in range(N-n+1):
            exact=sample_difference(values,n,s)
            shifted=sum((c[s+j]*comb(n,j) for j in range(n+1)),Q(0))
            assert exact==shifted==difference(lambda k:eval_newton(c,k),n,s)
            counts['in_range_differences']+=1
        try:sample_difference(values,N,1)
        except ValueError:counts['rejected_out_of_range_stencils']+=1
        else:raise AssertionError('Unprovided sample was silently inferred')
    for N in range(13):
      for _ in range(8):
        c=[Q(rng.randint(-30,30),rng.randint(1,9)) for _ in range(N+1)]
        assert coefficients([eval_newton(c,n) for n in range(N+1)])==c
        counts['interpolants']+=1
        for n in [0,1,N,N+3,2*N+1]:
          for s in [0,1,N,N+1,N+3]:
            exact=difference(lambda k:eval_newton(c,k),n,s)
            shifted=sum((c[s+j]*comb(n,j) for j in range(n+1) if s+j<=N),Q(0))
            assert exact==shifted
            if s>N:assert exact==0
            counts['arbitrary_interpolant_differences']+=1
    for p in [2,3,5,7,11]:
      denominators=[d for d in range(1,14) if d%p]
      for _ in range(180):
        N=rng.randrange(0,11);n=rng.randrange(0,13);s=rng.randrange(0,14)
        c=[Q(rng.randint(-8,8)*p**rng.randrange(0,6),rng.choice(denominators)) for _ in range(N+1)]
        actual=difference(lambda k:eval_newton(c,k),n,s);bound=weighted_bound(c,n,s,p)
        assert valuation(actual,p)>=bound
        counts['weighted_cases']+=1;counts['zero_weighted_differences']+=actual==0
      for a in [a for a in range(1,13) if a%p]:
        u=Q(a,rng.choice(denominators))
        for n in [0,1,4]:
          for s in range(7):
            mult=rng.randrange(0,4);h=mult*(p-1)
            exact=unit_mode(u,n,s,p,mult)
            assert exact==u**n*(u**h-1)**s
            assert valuation(exact,p)>=s
            counts['unit_cases']+=1
      for _ in range(70):
        count=rng.randrange(0,6);n=rng.randrange(0,5);s=rng.randrange(0,6)
        u=[Q(rng.choice([a for a in range(1,10) if a%p]),rng.choice(denominators)) for _ in range(count)]
        a=[Q(rng.randint(-9,9),rng.choice(denominators)) for _ in range(count)]
        exact=difference(lambda k:sum((ai*ui**k for ai,ui in zip(a,u)),Q(0)),n,s,p-1)
        assert exact==sum((ai*ui**n*(ui**(p-1)-1)**s for ai,ui in zip(a,u)),Q(0))
        assert valuation(exact,p)>=s
        counts['finite_mode_cases']+=1
      for u in [Q(p),Q(1,p),Q(0)]:
        try:unit_mode(u,0,1,p)
        except ValueError:counts['rejected_nonunit_inputs']+=1
        else:raise AssertionError('Nonunit was admitted')
    assert difference(lambda n:Q(n),0,1)!=difference(lambda n:Q(0),0,1)
    c=[0,81,3,3,81];assert weighted_bound(c,3,1,3)==2
    assert difference(lambda k:eval_newton(c,k),3,1)==180
    assert valuation(180,3)==2
    assert valuation(unit_mode(2,0,2,5),5)==2
    assert difference(lambda k:Q(3)**k,0,1,2)==8
    assert valuation(8,3)==0
    result={'status':'PASS','seed':904704,'counts':counts,
      'examples':{'weighted_difference':180,'weighted_minimum':2,'weighted_actual_valuation':2,
      'unit_difference':225,'unit_actual_valuation':2,'nonunit_difference':8},
      'seconds':round(time.monotonic()-start,4),
      'boundary':'Independent exact-rational mirrors, not executions extracted from Lean. Zero valuation is infinity internally. No GPU or historical numerical suite run.'}
    return result

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional new result file; no recorded evidence is overwritten by default')
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end='')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

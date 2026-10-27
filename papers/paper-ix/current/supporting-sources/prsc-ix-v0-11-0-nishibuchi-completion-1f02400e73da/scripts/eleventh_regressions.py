#!/usr/bin/env python3
"""Independent exact-rational checks. These are not extracted Lean executables."""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, factorial, lcm
from functools import lru_cache
import argparse, hashlib, json, time
from pathlib import Path

@lru_cache(maxsize=None)
def coefficients(N:int,j:int,end:int)->tuple[F,...]:
    if N<1 or not 0<=j<N or end<0: raise ValueError('invalid coefficient parameters')
    a=[F(1)]
    for n in range(1,end+1):
        a.append(-sum((F(comb(N*n+j,N*q))*a[q] for q in range(n)),F(0))/comb(N*n+j,N*n))
    return tuple(a)

def valuation(p:int,x:F)->int|None:
    if p<2: raise ValueError('base must be at least two')
    if x==0: return None
    a,b=abs(x.numerator),x.denominator;v=0
    while a%p==0: a//=p;v+=1
    while b%p==0: b//=p;v-=1
    return v

def precision(p:int,x:F,e:int)->bool:
    v=valuation(p,x)
    return v is None or v>=e

def delta(a:tuple[F,...],u:int,k:int,n:int)->F:
    return sum(((-1)**(k-i)*comb(k,i)*a[n+i*u] for i in range(k+1)),F(0))

def run()->dict:
    counts=dict(dyadic_coefficients=0,dyadic_higher_normalized=0,dyadic_higher_unnormalized=0,
                dyadic_periods=0,source_factorizations=0,source_reciprocal_rows=0,
                divisor_periods=0,divisor_families=0,degree_shift_identities=0,
                binomial_precision_cases=0)
    examples=[]
    for j in range(4):
        a=coefficients(4,j,96);b=tuple(factorial(j)*x for x in a)
        for n,x in enumerate(a):
            assert precision(2,x,0) and precision(2,b[n],0)
            counts['dyadic_coefficients']+=1
            g=[F(1),F(1,4*n+1),F(1,(4*n+1)*(2*n+1)),F(3,(4*n+1)*(2*n+1)*(4*n+3))][j]
            assert g==F(1,comb(4*n+j,4*n));counts['source_factorizations']+=1
        for n in range(25):
            product=sum((comb(4*n,4*q)*a[q]/comb(4*(n-q)+j,4*(n-q)) for q in range(n+1)),F(0))
            assert product==int(n==0);counts['source_reciprocal_rows']+=1
            for k in range(13):
                for u in range(5):
                    if n+k*u>96:continue
                    assert precision(2,delta(a,u,k,n),min(k,n));counts['dyadic_higher_normalized']+=1
                    assert precision(2,delta(b,u,k,n),min(k,n));counts['dyadic_higher_unnormalized']+=1
        for r in range(1,8):
            for n in range(r,25):
                assert precision(2,b[n+2**(r-1)]-b[n],r);counts['dyadic_periods']+=1
                assert 4*(n+2**(r-1))==4*n+2**(r+1);counts['degree_shift_identities']+=1
        examples.append({'j':j,'E4':str(b[1]),'E8':str(b[2]),'first_difference_v2':valuation(2,b[1]-b[0])})
    for p in [2,3,5,7]:
        for m in range(1,p):
            if (p-1)%m:continue
            N=m*p;q=lcm(2,p-1)
            for j in range(N):
                counts['divisor_families']+=1
                end=7+(q//m)*p
                a=tuple(factorial(j)*x for x in coefficients(N,j,end))
                for r in [1,2]:
                    shift=(q//m)*p**(r-1)
                    for n in range(r,8):
                        assert precision(p,a[n+shift]-a[n],r);counts['divisor_periods']+=1
                        assert N*(n+shift)==N*n+q*p**r;counts['degree_shift_identities']+=1
        for s in range(4):
            for k in range(1,p**s+1):
                assert comb(p**s,k)*p**k % p**(s+1)==0
                counts['binomial_precision_cases']+=1
    # Retained controls: extra uniform precision and a wrong degree displacement fail.
    a=coefficients(4,1,2)
    assert a[1]-a[0]==F(-6,5) and valuation(2,a[1]-a[0])==1
    assert not precision(2,a[1]-a[0],2)
    assert 4*(3+2**(3-1))!=4*3+2**3
    assert factorial(3)*coefficients(4,3,0)[0]!=1
    math={'counts':counts,'examples':examples,'retained_invalid_controls':3,'status':'PASS'}
    math['mathematical_sha256']=hashlib.sha256(json.dumps(math,sort_keys=True).encode()).hexdigest()
    return math

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);args=ap.parse_args()
    t=time.monotonic();result=run();result['seconds']=time.monotonic()-t
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text)

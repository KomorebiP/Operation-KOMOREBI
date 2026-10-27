#!/usr/bin/env python3
"""Independent exact-rational first-block regression mirrors, not extracted Lean code.
Author: Komorebi P.  No nonstandard dependencies, network, or floating-point arithmetic.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, factorial, prod
from random import Random
import argparse
import json
from pathlib import Path


def triangular(T: list[list[int]], b: list[int|Q]) -> list[Q]:
    if len(T)!=len(b) or any(len(row)!=len(b) for row in T): raise ValueError('Square dimension mismatch')
    a=[]
    for n,row in enumerate(T):
        if row[n]==0: raise ValueError('Zero diagonal')
        a.append((Q(b[n])-sum(Q(row[q])*a[q] for q in range(n)))/row[n])
    return a

def euler(N: int,j: int,depth: int) -> list[Q]:
    if N<1 or not 0<=j<N or depth<0: raise ValueError('Invalid packet parameters')
    T=[[comb(N*n+j,N*q) if q<=n else 0 for q in range(depth+1)] for n in range(depth+1)]
    return triangular(T,[1]+[0]*depth)

def convolution(h: list[Q],a: list[Q]) -> list[Q]:
    if len(h)!=len(a): raise ValueError('Dimension mismatch')
    return [sum(Q(comb(n,r))*h[r]*a[n-r] for r in range(n+1)) for n in range(len(h))]

def egf_inverse(h: list[Q]) -> list[Q]:
    if not h or h[0]!=1: raise ValueError('Unit constant must be one')
    k=[Q(1)]
    for n in range(1,len(h)):
        k.append(-sum(Q(comb(n,r))*h[r]*k[n-r] for r in range(1,n+1)))
    return k

def select(a: list[Q],N: int,j: int) -> list[Q]:
    if N<1: raise ValueError('Positive modulus required')
    return [x if n%N==j else Q(0) for n,x in enumerate(a)]

def vp(q: Q,p: int) -> int:
    if not q: raise ValueError('Finite valuation routine excludes zero')
    a,b=abs(q.numerator),q.denominator;v=0
    while a%p==0: a//=p;v+=1
    while b%p==0: b//=p;v-=1
    return v

def run() -> dict:
    rng=Random(90609);counts={}
    checks=0
    # Generic finite lower-triangular integer systems; integral right-hand sides.
    for size in range(1,11):
        for _ in range(12):
            T=[[rng.randint(-7,7) if j<=i else 0 for j in range(size)] for i in range(size)]
            for i in range(size): T[i][i]=rng.choice([-7,-3,-1,1,2,5])
            b=[rng.randint(-9,9) for _ in range(size)];a=triangular(T,b)
            for n in range(size):
                assert sum(T[n][q]*a[q] for q in range(n+1))==b[n]
                assert (prod(T[r][r] for r in range(n+1))*a[n]).denominator==1
            checks+=1
    counts['triangular_systems']=checks
    checks=0;rows=0
    for N in range(1,10):
        for j in range(N):
            a=euler(N,j,10);D=1
            for n in range(11):
                if n: D*=comb(N*n+j,N*n)
                assert (D*a[n]).denominator==1
                assert sum(Q(comb(N*n+j,N*q))*a[q] for q in range(n+1))==(1 if n==0 else 0)
                assert sum(a[q]/factorial(N*q)*Q(factorial(j),factorial(N*(n-q)+j)) for q in range(n+1))==(1 if n==0 else 0)
                # Original t-variable source has support at N*n+j.
                rows+=1
            checks+=1
    counts['congruential_parameter_pairs']=checks;counts['congruential_rows']=rows
    checks=0
    for _ in range(120):
        size=rng.randint(1,14);N=rng.randint(1,7)
        h=[Q(1)]+[Q(rng.randint(-8,8),rng.randint(1,6)) for _ in range(size-1)]
        a=[Q(rng.randint(-9,9),rng.randint(1,7)) for _ in range(size)]
        k=egf_inverse(h)
        assert convolution(k,convolution(h,a))==a
        assert convolution(h,convolution(k,a))==a
        transported=lambda j,x:convolution(h,select(convolution(k,x),N,j))
        packets=[transported(j,a) for j in range(N)]
        assert [sum(x[n] for x in packets) for n in range(size)]==a
        for j in range(N):
            assert transported(j,packets[j])==packets[j]
            for i in range(N):
                if i!=j: assert transported(i,packets[j])==[Q(0)]*size
        checks+=1
    counts['egf_coordinate_systems']=checks
    checks=0
    for N in range(1,10):
        for scale in range(1,6):
            M=N*scale;a=[Q(rng.randint(-10,10)) for _ in range(40)]
            assert [sum(select(a,N,j)[n] for j in range(N)) for n in range(len(a))]==a
            for j in range(N):
                parts=[select(a,M,r) for r in range(M) if r%N==j]
                assert [sum(x[n] for x in parts) for n in range(len(a))]==select(a,N,j)
            checks+=1
    counts['residue_refinement_cases']=checks
    checks=0
    for _ in range(240):
        p=rng.choice([2,3,5,7]);n=rng.randrange(18);L=rng.randrange(10)
        weights=[None if rng.randrange(5)==0 else rng.randrange(12) for _ in range(n+1)]
        c=[rng.randint(-8,8) for _ in range(n+1)];S=[rng.randint(-8,8) for _ in range(n+1)]
        terms=[0 if weights[r] is None else comb(n,r)*c[r]*p**weights[r]*S[n-r] for r in range(n+1)]
        retained=sum(terms[r] for r in range(n+1) if weights[r] is not None and weights[r]<L)
        assert (sum(terms)-retained)%p**L==0
        checks+=1
    counts['filtered_finite_tail_cases']=checks
    checks=0
    for p in [2,3,5,7,11,13]:
        for m in range(1,5):
            for n in range(11):
                for q in range(n+1):
                    for j in range(p):
                        assert (comb(m*p*n+j,m*p*q)-comb(m*n,m*q))%p==0
                        checks+=1
                for j in range(p):
                    assert comb(m*p*n+j,m*p*n)%p==1
                    assert factorial(j)%p!=0
    counts['lucas_row_cases']=checks
    a=euler(6,3,2)
    assert a[1]==Q(-1,84) and a[2]==Q(703,5460)
    delta=a[2]-a[1]
    assert delta==Q(64,455) and vp(delta,3)==0
    assert factorial(3)*delta==Q(384,455) and vp(factorial(3)*delta,3)==1
    assert vp(Q(factorial(3)),3)==1
    counts['normalization_counterexample']=1
    invalid=0
    for thunk in [lambda:euler(0,0,1),lambda:euler(3,3,2),lambda:euler(3,-1,2),lambda:euler(3,0,-1),
                  lambda:triangular([[0]],[1]),lambda:egf_inverse([Q(2)]),lambda:vp(Q(0),3),lambda:select([Q(1)],0,0)]:
        try: thunk()
        except ValueError: invalid+=1
        else: raise AssertionError('Invalid control accepted')
    counts['invalid_input_controls_rejected']=invalid
    return {'status':'EXACT_RATIONAL_REGRESSIONS_PASS','seed':90609,'counts':counts,
            'arithmetic':'Python integers and fractions.Fraction; no floating-point comparisons',
            'boundary':'Independent mirrors; not extracted Lean code, not the original historical numerical suite.'}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=run();text=json.dumps(result,indent=2)+'\n'
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text,end='');return 0
if __name__=='__main__': raise SystemExit(main())

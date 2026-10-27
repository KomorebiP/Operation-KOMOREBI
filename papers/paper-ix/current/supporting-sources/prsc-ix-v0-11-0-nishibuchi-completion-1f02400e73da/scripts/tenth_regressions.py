#!/usr/bin/env python3
"""Independent exact-arithmetic checks; not extracted Lean code or universal proofs.
Author: Komorebi P. Python 3.10+, standard library only.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, factorial, isqrt
from pathlib import Path
import argparse, hashlib, json, random, time


def natural(x: int, name: str = 'index') -> int:
    if isinstance(x, bool) or not isinstance(x, int) or x < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return x


def prime(p: int) -> int:
    natural(p, 'prime')
    if p < 2 or any(p % d == 0 for d in range(2, isqrt(p)+1)):
        raise ValueError('base must be prime')
    return p


def parameters(p: int, m: int, j: int) -> tuple[int, int]:
    prime(p); natural(m, 'm'); natural(j, 'residue')
    if not m or (p-1) % m or j >= m*p:
        raise ValueError('require m>0, m|(p-1), and 0<=j<m*p')
    return m*p, (p-1)//m


def valuation(x: Q | int, p: int) -> int | None:
    prime(p); q=Q(x)
    if not q: return None
    a,b=abs(q.numerator),q.denominator; v=0
    while a%p==0: a//=p; v+=1
    while b%p==0: b//=p; v-=1
    return v


def precision(x: Q | int, p: int, bound: int) -> bool:
    v=valuation(x,p)
    return v is None or v>=bound


def coefficients(N: int, j: int, rows: int) -> list[Q]:
    natural(N,'modulus');natural(j,'residue');natural(rows,'rows')
    if not N or j>=N: raise ValueError('require N>0 and j<N')
    c=[Q(1)]
    for n in range(1,rows+1):
        c.append(-sum((comb(N*n+j,N*q)*c[q] for q in range(n)),Q(0))/comb(N*n+j,N*n))
    return c


def reciprocal_coefficients(N: int, j: int, rows: int) -> list[Q]:
    """An independent ordinary-series reciprocal of j!/(N*n+j)!.
    Multiplication here is ordinary convolution, not the triangular binomial loop.
    """
    natural(rows)
    kernel=[Q(factorial(j),factorial(N*n+j)) for n in range(rows+1)]
    b=[Q(1)]
    for n in range(1,rows+1):
        b.append(-sum((kernel[r]*b[n-r] for r in range(1,n+1)),Q(0)))
    return [b[n]*factorial(N*n) for n in range(rows+1)]


def difference(values: list[Q], h: int, k: int, n: int) -> Q:
    natural(h,'step');natural(k,'order');natural(n,'row')
    if n+k*h>=len(values): raise ValueError('incomplete forward stencil')
    return sum(((-1)**(k-i)*comb(k,i)*values[n+i*h] for i in range(k+1)),Q(0))


def theta(f: list[Q]) -> list[Q]:
    return [Q(i)*f[i]+(i+1)*(f[i+1] if i+1<len(f) else Q(0)) for i in range(len(f))]


def theta_defect(f: list[Q], p: int) -> list[Q]:
    prime(p); a=list(f); b=None
    for r in range(1,p*p+1):
        a=theta(a)
        if r==p: b=list(a)
    assert b is not None
    return [(x-y)/p for x,y in zip(a,b)]


def weighted(f: list[Q], p: int) -> bool:
    return all(precision(x,p,-(d//p)) for d,x in enumerate(f))


def convolution(a: list[Q], b: list[Q], D: int) -> list[Q]:
    return [sum((a[i]*b[d-i] for i in range(d+1)),Q(0)) for d in range(D+1)]


def picard(q: list[Q], c: int, iterations: int) -> list[Q]:
    natural(c,'pivot');natural(iterations)
    if not c or q[0]: raise ValueError('require c>0 and q(0)=0')
    D=len(q)-1;y=[Q(0)]*(D+1)
    for _ in range(iterations):
        yq=convolution(y,q,D);yy=convolution(y,y,D)
        y=[(c*q[d]+yq[d]-yy[d])/(d+c) for d in range(D+1)]
    return y


def fixedpoint(q: list[Q], c: int) -> list[Q]:
    if c<=0 or q[0]: raise ValueError('require c>0 and q(0)=0')
    D=len(q)-1;y=[Q(0)]*(D+1)
    for d in range(1,D+1):
        y[d]=(c*q[d]+sum((y[i]*q[d-i]-y[i]*y[d-i] for i in range(1,d)),Q(0)))/(d+c)
    return y


def run() -> dict:
    start=time.monotonic(); rng=random.Random(91010)
    counts=dict(families=0,higher_residue_families=0,integral_coefficients=0,
                normalized_bounds=0,unnormalized_bounds=0,reciprocal_identity_rows=0,
                higher_residue_bound_pairs=0,theta_stability_checks=0,
                frobenius_square_checks=0,picard_prefix_checks=0)
    records=[]
    for p in [2,3,5,7,11]:
        for m in range(1,p):
            if (p-1)%m:continue
            for j in range(m*p):
                N,h=parameters(p,m,j);cs=coefficients(N,j,12);es=[factorial(j)*x for x in cs]
                alternate=reciprocal_coefficients(N,j,4)
                assert cs[:5]==alternate,(p,m,j,'reciprocal')
                counts['reciprocal_identity_rows']+=5
                counts['families']+=1;counts['higher_residue_families']+=int(j>=p)
                for v in es:
                    assert precision(v,p,0),(p,m,j,'integrality')
                    counts['integral_coefficients']+=1
                loss=valuation(factorial(j),p);assert loss is not None
                cases=0
                for n in range(5):
                    for k in range(5):
                        for u in [0,1,2]:
                            if n+k*u*h>12: continue
                            d=difference(cs,u*h,k,n);e=factorial(j)*d; b=min(k,m*n)
                            assert precision(e,p,b),(p,m,j,n,k,u,'unnormalized')
                            assert precision(d,p,b-loss),(p,m,j,n,k,u,'normalized')
                            counts['unnormalized_bounds']+=1;counts['normalized_bounds']+=1
                            counts['higher_residue_bound_pairs']+=int(j>=p);cases+=1
                records.append(dict(p=p,m=m,j=j,cases=cases))
    for p in [2,3,5,7,11]:
        for a in range(41):
            assert (a**(p*p)-a**p)%(p*p)==0
            counts['frobenius_square_checks']+=1
    for p in [2,3,5]:
        for _ in range(12):
            f=[Q(rng.randrange(-7,8),p**(d//p)) for d in range(16)]
            for s in range(3):
                assert weighted(f,p),(p,s,'theta stability')
                counts['theta_stability_checks']+=1;f=theta_defect(f,p)
    for c in [1,2,4,5,7]:
        for _ in range(4):
            q=[Q(0)]+[Q(rng.randrange(-3,4),rng.randrange(1,6)) for _ in range(8)]
            actual=fixedpoint(q,c)
            for r in range(9):
                approx=picard(q,c,r)
                assert approx[:r+1]==actual[:r+1],(c,r,'Picard prefix')
                counts['picard_prefix_checks']+=1
    c3=coefficients(6,3,3);c4=coefficients(6,4,3)
    e3=6*difference(c3,1,2,1);e4=24*difference(c4,1,2,1)
    assert e3==Q(-1464768,8645) and valuation(e3,3)==2
    assert e4==Q(-102745512,2377375) and valuation(e4,3)==2
    # Preserve the old counterexample, now explained by the corrected normalization.
    assert valuation(difference(c3,1,1,1),3)==0
    assert (2**81-2**9)%81==54
    mathematical=dict(status='EXACT_FINITE_CHECKS_PASS',counts=counts,families=records,
      examples={'p3_m2_j3_second':str(e3),'p3_m2_j4_second':str(e4),
                'second_valuations':[2,2],'normalized_no_loss_still_false':True},
      scope='Independent exact finite Python mirrors, not extracted Lean code or universal proof.')
    canonical=json.dumps(mathematical,sort_keys=True,separators=(',',':')).encode()
    return dict(**mathematical,mathematical_sha256=hashlib.sha256(canonical).hexdigest(),
                seconds=round(time.monotonic()-start,3))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); result=run()
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='families'},indent=2))

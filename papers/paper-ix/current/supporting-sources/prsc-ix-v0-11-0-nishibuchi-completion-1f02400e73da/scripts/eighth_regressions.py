#!/usr/bin/env python3
"""Independent exact arithmetic mirrors for the eighth block; not extracted Lean code.
Author: Komorebi P. Python 3.10+, standard library only.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, factorial
from functools import lru_cache
from pathlib import Path
from datetime import datetime, timezone
import json
import random

ROOT = Path(__file__).resolve().parents[1]

def natural(n: int, name: str) -> int:
    if type(n) is not int or n < 0:
        raise ValueError(f'{name} must be a natural integer')
    return n

def prime(p: int) -> int:
    natural(p, 'p')
    if p < 2 or any(p % d == 0 for d in range(2, int(p**0.5)+1)):
        raise ValueError('p must be prime')
    return p

def valuation(x: Q | int, p: int) -> int | None:
    prime(p)
    x=Q(x)
    if not x:return None
    def v(n: int) -> int:
        k=0
        while n % p == 0:n//=p;k+=1
        return k
    return v(abs(x.numerator))-v(x.denominator)

def precision(x: Q | int, p: int, s: int) -> bool:
    v=valuation(x,p)
    return v is None or v >= s

def difference(f, h: int, k: int, n: int) -> Q:
    for a,name in [(h,'h'),(k,'k'),(n,'n')]:natural(a,name)
    return sum(((-1)**(k-a)*comb(k,a)*Q(f(n+a*h)) for a in range(k+1)),Q(0))

def coefficients(N: int, j: int, last: int) -> list[Q]:
    natural(N,'N');natural(j,'j');natural(last,'last')
    if N == 0 or j >= N:raise ValueError('require N>0 and 0<=j<N')
    c=[Q(1)]
    for n in range(1,last+1):
        c.append(-sum((comb(N*n+j,N*q)*c[q] for q in range(n)),Q(0))/comb(N*n+j,N*n))
    return c

def hurwitz(f, g, d: int) -> Q:
    natural(d,'d')
    return sum((comb(d,k)*Q(f(k))*Q(g(d-k)) for k in range(d+1)),Q(0))

def reciprocal(f: list[Q], last: int) -> list[Q]:
    natural(last,'last')
    if not f or f[0] != 1:raise ValueError('constant coefficient must be one')
    out=[]
    for n in range(last+1):
        out.append(Q(int(n==0))-sum((comb(n,k)*out[k]*(f[n-k] if n-k < len(f) else 0)
                                    for k in range(n)),Q(0)))
    return out

def defect(f, p: int, s: int, d: int, normalized: bool = False) -> Q:
    prime(p);natural(s,'s');natural(d,'d')
    v=difference(f,p*(p-1),s,d+p*s)
    return v/(p**s) if normalized else v

def middle(f,g,p: int,q: int,d: int) -> Q:
    prime(p);natural(q,'q');natural(d,'d')
    return sum((Q(comb(q,k),p)*hurwitz(lambda a:f(a+k),lambda a:g(a+q-k),d)
                for k in range(1,q)),Q(0))

def run() -> dict:
    rng=random.Random(908)
    counts={k:0 for k in ['parameter_residue_families','rational_window_bounds',
                         'unnormalized_window_bounds','kernel_defect_bounds',
                         'inverse_defect_bounds','frobenius_product_identities',
                         'inverse_closure_cases','euler_commutator_identities',
                         'multiple_step_telescopes','invalid_input_rejections']}
    # Literal original recurrence, including p=2, all residues in the standard window.
    for p in [2,3,5,7,11]:
        for m in range(1,p):
            if (p-1)%m:continue
            N=m*p;h=(p-1)//m
            for j in range(p):
                counts['parameter_residue_families']+=1
                last=max(3+6*h,(2*p+3*p*p)//N+1)
                cs=coefficients(N,j,last)
                def value(r):return cs[r]
                def packed(d):return cs[d//N] if d%N==0 else Q(0)
                def kernel(d):return Q(1,comb(d+j,d)) if d%N==0 else Q(0)
                for u in [1,2]:
                    for k in range(4):
                        for n in range(4):
                            x=difference(value,u*h,k,n);bound=min(k,m*n)
                            assert precision(x,p,bound),(p,m,j,n,k,u,x)
                            counts['rational_window_bounds']+=1
                            assert precision(factorial(j)*x,p,bound)
                            counts['unnormalized_window_bounds']+=1
                for s in range(4):
                    for d in range(2*p+1):
                        assert precision(defect(kernel,p,s,d),p,s),(p,m,j,s,d,'kernel')
                        counts['kernel_defect_bounds']+=1
                        assert precision(defect(packed,p,s,d),p,s),(p,m,j,s,d,'inverse')
                        counts['inverse_defect_bounds']+=1
    # Full characteristic-zero product formula, on actual finite polynomial EGFs.
    for p in [2,3,5]:
        for _ in range(5):
            fs=[Q(rng.randrange(-4,5),rng.choice([1,2,3])) for _ in range(9)]
            gs=[Q(rng.randrange(-4,5),rng.choice([1,2,5])) for _ in range(8)]
            f=lambda d:fs[d] if d<len(fs) else Q(0)
            g=lambda d:gs[d] if d<len(gs) else Q(0)
            fg=lambda d:hurwitz(f,g,d)
            Bf=lambda d:defect(f,p,1,d,True)
            Bg=lambda d:defect(g,p,1,d,True)
            for d in range(5):
                lhs=defect(fg,p,1,d,True)
                rhs=hurwitz(Bf,g,d)+hurwitz(f,Bg,d)+middle(f,g,p,p*p,d)-middle(f,g,p,p,d)
                assert lhs==rhs
                counts['frobenius_product_identities']+=1
            # Every polynomial of degree <p has zero defect and is a flat source.
            fsmall=[Q(1)]+[Q(rng.randrange(-3,4)) for _ in range(p-1)]
            rec=reciprocal(fsmall,3*p*p+5)
            for s in range(4):
                for d in range(6):
                    assert precision(defect(lambda a:rec[a],p,s,d),p,s)
                    counts['inverse_closure_cases']+=1
            for c in [0,1,p,p+1]:
                E=lambda d:(d+c)*f(d)
                for s in range(3):
                    for d in range(4):
                        dg=lambda a:defect(f,p,s,a)
                        corr=p*p*dg(d+p*p)-p*dg(d+p)
                        assert defect(E,p,s+1,d)==(d+c)*defect(f,p,s+1,d)+(s+1)*corr
                        counts['euler_commutator_identities']+=1
    for h in range(5):
        for u in range(6):
            f=lambda n:Q(n**4-3*n**2+7)
            for n in range(5):
                assert f(n+u*h)-f(n)==sum(difference(f,h,1,n+a*h) for a in range(u))
                counts['multiple_step_telescopes']+=1
    cs=coefficients(6,2,3)
    delta=difference(lambda n:cs[n],1,2,1)
    controls={
        'actual_window_sharp_power':delta==Q(-949959,1235) and valuation(delta,3)==2,
        'extra_power_fails':not precision(delta,3,3),
        'nonunit_normalized_residue_fails_integrality':valuation(coefficients(6,3,1)[1],3)==-1,
        'zero_precision_preserved':precision(0,3,100),
        'cubic_defect_not_derivation':defect(lambda d:Q(factorial(3) if d==3 else 0),3,1,0,True)==-2,
        'composite_middle_not_integral':valuation(Q(comb(4,2),4),2)==-1,
        'singular_pivot_not_unit':valuation(3,3)==1,
    }
    assert all(controls.values())
    invalid=[lambda:prime(1),lambda:prime(9),lambda:prime(True),
             lambda:coefficients(0,0,2),lambda:coefficients(6,6,2),
             lambda:coefficients(6,0,-1),lambda:reciprocal([0,1],2),
             lambda:difference(lambda n:n,1,-1,0),lambda:defect(lambda n:n,4,1,0),
             lambda:defect(lambda n:n,3,1,-1)]
    for f in invalid:
        try:f()
        except ValueError:counts['invalid_input_rejections']+=1
        else:raise AssertionError('invalid input accepted')
    return {'status':'PASS','seed':908,'counts':counts,'controls':controls,
            'scope':'Exact finite Python mirrors, not Lean extraction. Full higher-power theorem checked formally only in the standard window; all-residue item 7.5 remains pending.',
            'example':{'C6_2':list(map(str,cs)),'second_difference':str(delta),'v3':valuation(delta,3)}}

def main() -> None:
    data=run()
    out=ROOT/'verification/eighth_regressions'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True,exist_ok=False)
    (out/'regressions.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
if __name__=='__main__':main()

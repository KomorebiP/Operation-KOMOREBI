#!/usr/bin/env python3
"""Independent exact finite mirrors for the seventh block. Author: Komorebi P.
No results here are counted as universal proofs or as execution extracted from Lean.
"""
from __future__ import annotations
from datetime import datetime, timezone
from fractions import Fraction
from math import comb, gcd
from pathlib import Path
import json, random
ROOT=Path(__file__).resolve().parents[1]

def natural(n: int) -> None:
    if isinstance(n,bool) or not isinstance(n,int) or n<0: raise ValueError('Expected natural integer')

def prime(p: int) -> bool:
    natural(p)
    return p>=2 and all(p%d for d in range(2,int(p**0.5)+1))

def require_prime(p: int) -> None:
    if not prime(p): raise ValueError('Prime modulus required')

def convolution(f: list[int],g: list[int],n:int,p:int) -> int:
    require_prime(p); natural(n)
    if n>=len(f) or n>=len(g): raise ValueError('Complete convolution row required')
    return sum(comb(n,k)*f[k]*g[n-k] for k in range(n+1))%p

def reciprocal(g: list[int],p:int) -> list[int]:
    require_prime(p)
    if not g or g[0]%p!=1: raise ValueError('Constant coefficient must be one')
    out=[1]
    for n in range(1,len(g)):
        out.append(-sum(comb(n,k)*out[k]*g[n-k] for k in range(n))%p)
    return out

def reduced(p:int,m:int,count:int) -> list[int]:
    require_prime(p); natural(m);natural(count)
    if m==0: raise ValueError('Positive packet width required')
    out=[1]
    for n in range(1,count+1):
        out.append(-sum(comb(m*n,m*q)*out[q] for q in range(n))%p)
    return out

def period(p:int,m:int) -> int:
    require_prime(p);natural(m)
    if m==0 or (p-1)%m: raise ValueError('Width must divide p-1')
    return (p-1)//m

def normalized_coefficients(N:int,j:int,count:int) -> list[Fraction]:
    natural(N);natural(j);natural(count)
    if N==0 or j>=N: raise ValueError('Canonical residue and positive modulus required')
    out=[Fraction(1)]
    for n in range(1,count+1):
        out.append(-sum((comb(N*n+j,N*q)*out[q] for q in range(n)),Fraction(0))/comb(N*n+j,N*n))
    return out

def reduce_fraction(x:Fraction,p:int) -> int:
    require_prime(p)
    x=Fraction(x)
    if x.denominator%p==0: raise ValueError('Nonintegral rational has no residue')
    return x.numerator*pow(x.denominator,-1,p)%p

def valuation(x:Fraction,p:int) -> int|None:
    require_prime(p);x=Fraction(x)
    if not x:return None # infinity, not zero
    a,b=abs(x.numerator),x.denominator;v=0
    while a%p==0:a//=p;v+=1
    while b%p==0:b//=p;v-=1
    return v

def difference(f:list,h:int,k:int,n:int):
    for x in [h,k,n]:natural(x)
    if n+h*k>=len(f):raise ValueError('Incomplete forward stencil')
    return sum((-1)**(k-i)*comb(k,i)*f[n+h*i] for i in range(k+1))

def defect_value(p:int,L:int,k:int,f,d:int):
    return sum((-1)**(k-i)*comb(k,i)*f(d+p*k+L*i) for i in range(k+1))

def run() -> dict:
    rng=random.Random(907)
    counts={k:0 for k in ['reciprocal_rows','higher_leibniz_rows','inverse_prime_shift_rows',
             'section_parameter_pairs','support_rows','residual_identification_rows','period_rows',
             'standard_window_rational_rows','standard_window_differences','mod_p_higher_differences',
             'dwork_extraction_interfaces','finite_global_test_cases','invalid_input_rejections']}
    for p in [2,3,5,7,11,13]:
        for _ in range(8):
            tail=[rng.randrange(p) for _ in range(p-1)]
            g=[1]+[tail[(i-1)%(p-1)] for i in range(1,101)]
            f=reciprocal(g,p)
            for n in range(101):
                assert convolution(f,g,n,p)==int(n==0);counts['reciprocal_rows']+=1
            for n in range(101-p):
                assert f[n+p]==f[n+1];counts['inverse_prime_shift_rows']+=1
            a=[rng.randrange(p) for _ in range(51)];b=[rng.randrange(p) for _ in range(51)]
            for n in range(18):
                for r in [1,2,p]:
                    left=convolution(a,b,n+r,p)
                    right=sum(comb(r,i)*convolution(a[i:],b[r-i:],n,p) for i in range(r+1))%p
                    assert left==right;counts['higher_leibniz_rows']+=1
    for p in [2,3,5,7,11,13,17,19]:
        for m in range(1,p):
            if (p-1)%m:continue
            h=period(p,m);maxrow=24+4*h
            seq=reduced(p,m,maxrow)
            g=[int(d%m==0) for d in range(m*(h+8)+1)]
            f=reciprocal(g,p)
            counts['section_parameter_pairs']+=1
            for d,v in enumerate(f):
                if d%m:assert v==0
                else:assert v==seq[d//m];counts['residual_identification_rows']+=1
                counts['support_rows']+=1
            for n in range(1,25):
                for u in range(5):
                    assert seq[n+u*h]==seq[n];counts['period_rows']+=1
            for n in range(1,6):
                for k in range(1,5):
                    assert difference(seq,h,k,n)%p==0;counts['mod_p_higher_differences']+=1
            # independently compute the rational family, not just a modulo-p recurrence
            for j in sorted({0,p//2,p-1}):
                cs=normalized_coefficients(m*p,j,2*h+6)
                for n,c in enumerate(cs):
                    assert reduce_fraction(c,p)==seq[n];counts['standard_window_rational_rows']+=1
                for n in range(1,7):
                    for u in [1,2]:
                        assert reduce_fraction(cs[n+u*h]-cs[n],p)==0
                        counts['standard_window_differences']+=1
            # Algebraic extraction interface, with arbitrary coefficients NOT claimed flat.
            e=lambda q:q**4-3*q+7
            packed=lambda d:e(d//(m*p)) if d%(m*p)==0 else 0
            for n in range(5):
                for k in range(min(m*n,4)+1):
                    left=defect_value(p,p*(p-1),k,packed,m*p*n-p*k)
                    right=sum((-1)**(k-i)*comb(k,i)*e(n+h*i) for i in range(k+1))
                    assert left==right;counts['dwork_extraction_interfaces']+=1
    # Finite tests of the STILL PENDING global theorem. Never counted as a proof.
    from math import factorial
    for p in [3,5,7]:
        for m in range(1,p):
            if (p-1)%m:continue
            h=(p-1)//m;N=m*p
            for j in range(N):
                cs=normalized_coefficients(N,j,3+6*h)
                es=[factorial(j)*x for x in cs]
                for n in range(4):
                    for k in range(4):
                        for u in [1,2]:
                            v=valuation(difference(es,u*h,k,n),p)
                            assert v is None or v>=min(k,m*n)
                            counts['finite_global_test_cases']+=1
    cs=normalized_coefficients(6,0,2)
    controls={
      'positive_tail_required':reduced(3,2,1)==[1,2],
      'divisor_hypothesis_required':reduced(5,3,3)[2]!=reduced(5,3,3)[3],
      'one_power_is_not_two':cs[2]-cs[1]==924 and valuation(cs[2]-cs[1],3)==1,
      'zero_precision_is_infinite':valuation(Fraction(0),3) is None,
      'p2_included':reduced(2,1,6)==[1]*7,
      'nonstandard_coefficient_nonintegral':valuation(normalized_coefficients(6,3,1)[1],3)==-1,
      'nondivisor_sequence':reduced(5,3,3)==[1,4,4,2],
    }
    assert all(controls.values())
    for call in [lambda:period(9,2),lambda:period(5,3),lambda:period(5,0),
                 lambda:reciprocal([0,1],3),lambda:reciprocal([],3),
                 lambda:difference([1],1,1,0),lambda:normalized_coefficients(0,0,1),
                 lambda:normalized_coefficients(6,6,1),lambda:reduce_fraction(Fraction(1,3),3),
                 lambda:reduced(5,True,3),lambda:period(5,-1)]:
        try:call()
        except ValueError:counts['invalid_input_rejections']+=1
        else:raise AssertionError('Invalid input accepted')
    return {'status':'PASS','seed':907,'counts':counts,'controls':controls,
            'scope':'Independent exact finite mirrors. Not Lean extraction. Global finite-difference tests do not promote item 7.5.',
            'exact_examples':{'C_6_0_first':str(cs[1]),'C_6_0_second':str(cs[2]),'difference':924,'v3':1}}

def main() -> None:
    result=run();out=ROOT/'verification/seventh_regressions'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True,exist_ok=False);(out/'regressions.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

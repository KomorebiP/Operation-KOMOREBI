#!/usr/bin/env python3
"""Exact Block47 Cartier and hypergeometric checks; Python standard library only."""
from collections import defaultdict, Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse, json, platform


def mul_poly(a,b):
    c=defaultdict(int)
    for u,cu in a.items():
        for v,cv in b.items():
            c[tuple(x+y for x,y in zip(u,v))]+=cu*cv
    return {u:c for u,c in c.items() if c}


def prime_val(x,p=7):
    assert x
    out=0
    while x%p==0:
        x//=p; out+=1
    return out


def field(q):
    if q==7:
        return (lambda a,b:(a+b)%7,lambda a,b:(a*b)%7,lambda a:a%7)
    assert q==49
    # F_49=F_7[u]/(u^2-3); a+7b encodes a+b*u.
    def add(x,y):return (x%7+y%7)%7+7*((x//7+y//7)%7)
    def mul(x,y):
        a,b,c,d=x%7,x//7,y%7,y//7
        return (a*c+3*b*d)%7+7*((a*d+b*c)%7)
    return add,mul,lambda a:a%7


def point_count(A,B,q):
    add,mul,integer=field(q)
    roots=Counter(mul(y,y) for y in range(q))
    count=2 # monic, degree six: two smooth rational points at infinity
    for x in range(q):
        x2=mul(x,x);x3=mul(x2,x);x6=mul(x3,x3)
        value=add(add(x6,mul(integer(10*B),x3)),add(mul(integer(12*A),x),integer(5*B*B)))
        count+=roots[value]
    return count


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    sextic={(6,0,0):1,(3,0,1):10,(1,1,0):12,(0,0,2):5}
    cube=mul_poly(mul_poly(sextic,sextic),sextic)
    coeffs={i:{(a,b):v for (x,a,b),v in cube.items() if x==i} for i in (6,5,13,12)}
    assert coeffs=={6:{(0,4):1575},5:{(2,1):4320},13:{(1,0):36},12:{(0,2):315}}
    # Independent dense univariate expansion for each of the 49 specializations.
    good=[];bad=[]
    for A in range(7):
      for B in range(7):
        f=[5*B*B,12*A,0,10*B,0,0,1]
        ff=[sum(f[i]*f[j] for i in range(7) for j in range(7) if i+j==n) for n in range(13)]
        fff=[sum(ff[i]*f[j] for i in range(13) for j in range(7) if i+j==n)%7 for n in range(19)]
        assert (fff[6],fff[5],fff[13],fff[12])==(0,A*A*B%7,A,0)
        if (A**3+B**5)%7==0:
            bad.append([A,B]);continue
        n1=point_count(A,B,7);n2=point_count(A,B,49)
        s1=8-n1;s2=50-n2
        assert (s1*s1-s2)%2==0
        e2=(s1*s1-s2)//2
        # chi(T)=T4-s1*T3+e2*T2-7*s1*T+49.
        assert s1%7==0 and e2%7==(-A**3*B)%7
        matrix_rank=2 if A*B%7 else (1 if A else 0)
        good.append({'A':A,'B':B,'C':(A**3+B**5)%7,'cartier_rank':matrix_rank,'stable_rank':2 if matrix_rank==2 else 0,'N7':n1,'N49':n2,'chi':[1,-s1,e2,-7*s1,49]})
    # Exact hypergeometric coefficients and seven-lane recurrence checks.
    coeff=[Fraction(1)]
    for n in range(350):
        coeff.append(coeff[-1]*Fraction((15*n+8)*(15*n-2),45*(n+1)*(5*n+7)))
    assert coeff[1]==Fraction(-16,315)
    assert all(coeff)
    for n in range(1,len(coeff)):
        assert 45*n*(5*n+2)*coeff[n]==(15*n-7)*(15*n-17)*coeff[n-1]
    minima=[];val=0
    for j in range(100000):
        val+=prime_val(15*j+8)+prime_val(15*j-2)-prime_val(j+1)-prime_val(5*j+7)
        if not minima or val<minima[-1][1]:minima.append([j+1,val])
        if j+1<len(coeff):assert val==prime_val(coeff[j+1].numerator)-prime_val(coeff[j+1].denominator)
    assert minima==[[1,-1],[1030,-2],[3431,-3]]
    # Universal parameter construction in quotient rings with both parameter and complement units.
    checks=0
    from math import gcd
    for modulus in [7,49,343,11,121,25,27]:
      for t in range(modulus):
        if gcd(t*(1-t),modulus)!=1:continue
        A=pow(t,28,modulus)*pow(1-t,30,modulus)%modulus
        B=-pow(t,17,modulus)*pow(1-t,18,modulus)%modulus
        C=pow(t,12,modulus)*pow(1-t,13,modulus)%modulus
        assert (pow(A,3,modulus)+pow(B,5,modulus)-pow(C,7,modulus))%modulus==0
        assert (pow(B,5,modulus)+t*pow(A,3,modulus))%modulus==0
        assert gcd(A*B*C,modulus)==1
        checks+=1
    result={'status':'PASS','script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'python':platform.python_version(),'domain':'Z[A,B,X], Q exact fractions, F7 and F49=F7[u]/(u²-3)','symbolic_coefficients':{str(i):[[a,b,v] for (a,b),v in d.items()] for i,d in coeffs.items()},'specializations_checked':49,'good_reduction_specializations':len(good),'singular_specializations':bad,'cartier_rank_counts':dict(Counter(x['cartier_rank'] for x in good)),'good_specializations':good,'period_coefficients_checked':len(coeff),'coefficient_valuation_scan_bound':100000,'first_new_minima_v7':minima,'universal_parameter_checks':checks,'scope':'Exact identities plus finite checks. No modular candidate elimination; no residual irreducibility theorem; no global primitive solution exclusion.'}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('good_specializations','singular_specializations')},indent=2))

if __name__=='__main__':main()

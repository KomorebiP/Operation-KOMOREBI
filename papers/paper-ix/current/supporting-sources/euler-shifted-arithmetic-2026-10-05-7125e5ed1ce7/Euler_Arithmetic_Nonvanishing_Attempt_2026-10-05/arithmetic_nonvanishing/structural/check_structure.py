#!/usr/bin/env python3
"""Exact finite corroboration; universal statements have separate proofs."""
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import json
import sys

def bernoullis(n):
    b=[F(1)]
    for m in range(1,n+1):
        b.append(-sum(F(comb(m+1,k))*b[k] for k in range(m))/(m+1))
    return b

def eulers(n):
    e=[1]
    for m in range(1,n+1):
        e.append(-sum(comb(2*m,2*k)*e[k] for k in range(m)))
    return e

def fall(x,n):
    z=1
    for k in range(n):z*=x-k
    return z

def skeleton(x,n):
    z=1
    for k in range(n):z*=(x-k)*(2*x-2*k-1)
    return z

def source(n):
    return F(9**(n+1)-1,8*(n+1)*(2*n+1))

def trim(p):
    while len(p)>1 and not p[-1]:p.pop()
    return p

def add(p,q):
    return trim([(p[i] if i<len(p) else 0)+(q[i] if i<len(q) else 0)
                 for i in range(max(len(p),len(q)))])

def mul(p,q):
    out=[F(0)]*(len(p)+len(q)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(q):out[i+j]+=a*b
    return trim(out)

def det(a):
    a=[[F(v) for v in row] for row in a]
    ans=F(1)
    for i in range(len(a)):
        k=next(k for k in range(i,len(a)) if a[k][i])
        if k!=i:a[k],a[i]=a[i],a[k];ans=-ans
        pivot=a[i][i];ans*=pivot
        for k in range(i+1,len(a)):
            scale=a[k][i]/pivot
            for j in range(i+1,len(a)):a[k][j]-=scale*a[i][j]
            a[k][i]=0
    return ans

def fmod(q,p):
    q=F(q)
    assert q.denominator%2
    return q.numerator*pow(q.denominator,-1,1<<p)%(1<<p)

def main(out):
    b=bernoullis(82);e=eulers(40)
    beta=[F(1)]+[-F(2**(2*m)*(2*m-1),factorial(2*m))*b[2*m]
                for m in range(1,41)]
    counts={"volkenborn_values":0,"source_free_values":0,
            "original_reconstruction":0,"finite_resummation":0,
            "orthogonality_pairs":0,"hankel_determinants":0}
    for n in range(31):
        moment=sum(F(comb(2*n+1,k))*4**k*b[k] for k in range(2*n+2))
        assert -moment/(2*n+1)==e[n]
        counts['volkenborn_values']+=1
        sf=2-F(1,2*n+1)+sum(4**m*beta[m]*fall(2*n,2*m-1)/(2*m-1)
                            for m in range(1,n+1))
        assert sf==e[n];counts['source_free_values']+=1
        reconstruction=sum(8**m*beta[m]*skeleton(n,m)*source(n-m)
                           for m in range(n+1))
        assert reconstruction==e[n];counts['original_reconstruction']+=1
        for r in range(1,min(n,24)+1):
            d=(n+1)*(2*n+1)
            q=1+d*sum(8**m*beta[m]*F(1,9**m)*skeleton(n,m-1)
                       for m in range(1,r))
            rr=1+d*sum(8**m*beta[m]*skeleton(n,m-1) for m in range(1,r))
            h=sum(8**k*beta[r+k]/beta[r]*skeleton(n-r,k)*source(n-r-k)
                  for k in range(n-r+1))
            assert 8*d*e[n]-9**(n+1)*q+rr==8**(r+1)*beta[r]*d*skeleton(n,r)*h
            counts['finite_resummation']+=1
    # Complete coefficient reductions: the proved omitted m>=2 bound is >=4.
    low=[F(1),F(2)-F(8,3),F(-4),F(8)]
    assert [fmod(v,4) for v in low]==[1,10,12,8]
    assert [fmod((i+1)*low[i+1],3) for i in range(3)]==[2,0,0]
    assert [fmod((i+2)*(i+1)*low[i+2],4) for i in range(2)]==[8,0]
    p=[[F(1)],[F(0),F(1)]]
    for n in range(1,12):p.append(add([F(0)]+p[n],[n*n*c for c in p[n-1]]))
    def L(pol):return sum(c*e[k//2] for k,c in enumerate(pol) if k%2==0)
    for n in range(13):
        for m in range(13):
            assert L(mul(p[n],p[m]))==((-1)**n*factorial(n)**2 if n==m else 0)
            counts['orthogonality_pairs']+=1
    hd=[]
    for d in range(7):
        observed=det([[e[i+j] for j in range(d+1)] for i in range(d+1)])
        expected=1
        for j in range(d+1):expected*=factorial(2*j)**2
        assert observed==expected
        hd.append(str(expected));counts['hankel_determinants']+=1
    ratios=[(F(e[n])-source(n))/F(e[n+1]+e[n]) for n in [1,2]]
    assert ratios==[F(-2,3),F(2,105)] and ratios[0]!=ratios[1]
    result={"status":"passed","base_checkpoint":"Euler-coupled-stationarity-20261005",
            "arithmetic":"exact integer and fractions.Fraction",
            "counts":counts,"coefficient_mod16":[1,10,12,8],
            "hankel_determinants_d0_to6":hd,
            "failed_dictionary_ratios":[str(x) for x in ratios],
            "nonclaims":["No universal residual simplicity proof.",
                          "No stationary critical-value nonvanishing theorem.",
                          "No bounded measure representation of Euler power moments.",
                          "No transfer of Hankel nonvanishing to the actual residual."]}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'STRUCTURE_CHECKS.json')

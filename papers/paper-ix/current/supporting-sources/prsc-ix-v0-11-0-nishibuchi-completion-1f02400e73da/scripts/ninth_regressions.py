#!/usr/bin/env python3
"""Independent exact finite mirrors for the singular-Amice block; not Lean extraction.
Author: Komorebi P.  Uses only the Python standard library.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import json,math,random,time,argparse


def prime(p: int) -> bool:
    return isinstance(p,int) and not isinstance(p,bool) and p>=2 and all(p%d for d in range(2,math.isqrt(p)+1))


def vp(x: int|Q, p: int) -> int|None:
    if not prime(p): raise ValueError('prime required')
    x=Q(x)
    if x==0: return None
    a,b=abs(x.numerator),x.denominator
    v=0
    while a%p==0: a//=p;v+=1
    while b%p==0: b//=p;v-=1
    return v


def weighted(f: list[Q],p: int) -> bool:
    if not prime(p): raise ValueError('prime required')
    return all(vp(x,p) is None or vp(x,p)>=-(d//p) for d,x in enumerate(f))


def mul(f:list[Q],g:list[Q],D:int)->list[Q]:
    if D<0: raise ValueError('nonnegative degree required')
    out=[Q(0)]*(D+1)
    for i,x in enumerate(f[:D+1]):
        if not x: continue
        for j,y in enumerate(g[:D-i+1]):
            if y: out[i+j]+=x*y
    return out


def reciprocal(f:list[Q],D:int)->list[Q]:
    if D<0 or not f or f[0]==0: raise ValueError('nonzero constant and nonnegative degree required')
    b=[1/Q(f[0])]
    for d in range(1,D+1):
        b.append(-sum((Q(f[i])*b[d-i] for i in range(1,min(d,len(f)-1)+1)),Q(0))/f[0])
    return b


def signed_stirling(D:int)->list[list[int]]:
    if D<0: raise ValueError('nonnegative degree required')
    rows=[[1]]
    for d in range(D):
        r=[0]*(d+2)
        for k,x in enumerate(rows[-1]): r[k]-=d*x;r[k+1]+=x
        rows.append(r)
    return rows


def section_pullback(N:int,c:int,D:int)->list[Q]:
    if N<=0 or not 0<=c<N or D<0: raise ValueError('canonical positive-modulus address required')
    return [Q(sum(row[k] for k in range(c,d+1,N)),math.factorial(d)) for d,row in enumerate(signed_stirling(D))]


def compose_log_stirling(f:list[Q],D:int)->list[Q]:
    out=[]
    for d,row in enumerate(signed_stirling(D)):
        out.append(sum((Q(row[k]*math.factorial(k),math.factorial(d))*f[k] for k in range(min(d+1,len(f))) if row[k] and f[k]),Q(0)))
    return out


def log_series(D:int)->list[Q]:
    return [Q(0)]+[Q((-1)**(d+1),d) for d in range(1,D+1)]


def compose_log_direct(f:list[Q],D:int)->list[Q]:
    lg=log_series(D);power=[Q(1)]+[Q(0)]*D;out=[Q(0)]*(D+1)
    for k in range(min(len(f),D+1)):
        for d in range(D+1): out[d]+=f[k]*power[d]
        power=mul(power,lg,D)
    return out


def ratio_t(N:int,c:int,D:int)->list[Q]:
    if N<=0 or not 1<=c<N or D<0: raise ValueError('positive canonical ratio address required')
    a=lambda j:[Q(1,math.factorial(d+j)) if d%N==0 else Q(0) for d in range(D+1)]
    return mul(a(c-1),reciprocal(a(c),D),D)


def euler_log(f:list[Q],D:int)->list[Q]:
    deriv=[(d+1)*f[d+1] if d+1<len(f) else Q(0) for d in range(D+1)]
    return mul(mul(log_series(D),[Q(1),Q(1)],D),deriv,D)


def singular_case(p:int,m:int,a:int,D:int)->dict:
    if not prime(p) or m<=0 or (p-1)%m or not 1<=a<m or D<0: raise ValueError('invalid singular parameters')
    N=m*p;c=a*p
    H=section_pullback(N,c,D+c+1)
    U=[math.factorial(c)*H[d+c] for d in range(D+2)]
    assert U[0]==1
    inv=reciprocal(U,D)
    direct=compose_log_stirling(ratio_t(N,c,D),D)
    lu=[Q((-1)**d,d+1) for d in range(D+1)]
    leading=[c*x for x in mul([Q(1),Q(1)],lu,D)]
    term=mul(euler_log(U,D),inv,D)
    reconstructed=[leading[d]+term[d] for d in range(D+1)]
    assert reconstructed==direct
    assert weighted(H,p) and weighted(U,p) and weighted(inv,p) and weighted(direct,p)
    assert direct[0]==c
    assert all(q==0 for q in direct[1:min(N,D+1)])
    return {'p':p,'m':m,'a':a,'degree':D,'coefficient_checks':D+1,'nonzero_coefficients':sum(q!=0 for q in direct)}


def run()->dict:
    counts={'cyclic_numerator_checks':0,'section_weight_checks':0,'direct_log_composition_cases':0,
            'singular_families':0,'singular_ratio_coefficient_checks':0,'weighted_closure_cases':0}
    for p in (2,3,5,7):
        D=3*p*p;rows=signed_stirling(D)
        for N in range(1,p*(p-1)+1):
            if p*(p-1)%N: continue
            for d,row in enumerate(rows):
                e=vp(math.factorial(d//p),p)
                for c in range(N):
                    numerator=sum(row[k] for k in range(c,d+1,N))
                    assert numerator%(p**e)==0
                    counts['cyclic_numerator_checks']+=1
                    q=Q(numerator,math.factorial(d))
                    assert vp(q,p) is None or vp(q,p)>=-(d//p)
                    counts['section_weight_checks']+=1
    for N in (1,2,3,4,6,8):
        for c in range(N):
            f=[Q(1,math.factorial(d)) if d%N==c else Q(0) for d in range(13)]
            assert compose_log_direct(f,12)==section_pullback(N,c,12)
            counts['direct_log_composition_cases']+=1
    families=[]
    for p in (3,5,7):
        for m in range(1,p):
            if (p-1)%m: continue
            for a in range(1,m):
                D=min(2*m*p,64)
                result=singular_case(p,m,a,D);families.append(result)
                counts['singular_families']+=1
                counts['singular_ratio_coefficient_checks']+=D+1
    rng=random.Random(9072026)
    for p in (2,3,5,7):
        D=18
        for _ in range(30):
            f=[Q(1)]+[Q(rng.randrange(-20,21),p**(d//p)) for d in range(1,D+2)]
            g=[Q(1)]+[Q(rng.randrange(-20,21),p**(d//p)) for d in range(1,D+2)]
            assert weighted(mul(f,g,D),p)
            inv=reciprocal(f,D)
            assert mul(f,inv,D)==[Q(1)]+[Q(0)]*D
            assert weighted(inv,p)
            assert weighted([(d+1)*f[d+1] for d in range(D+1)],p)
            assert weighted(euler_log(f,D),p)
            counts['weighted_closure_cases']+=1
    q=compose_log_stirling(ratio_t(6,3,6),6)[6]
    assert q==Q(1,10080) and vp(q,3)==-2
    bad=section_pullback(4,1,9)[9]
    assert vp(bad,3)<-3  # Violating N | p(p-1) can invalidate the section estimate.
    assert section_pullback(3,0,3)[3]==Q(1,6) and vp(Q(1,6),3)==-1
    assert not weighted([Q(1,3)],3)
    assert vp(Q(0),3) is None
    return {'status':'EXACT_FINITE_REGRESSIONS_PASS','counts':counts,'families':families,
      'sharp_singular_example':{'p':3,'N':6,'c':3,'d':6,'coefficient':str(q),'valuation':-2,'weight_floor':2},
      'invalid_modulus_example':{'p':3,'N':4,'c':1,'d':9,'coefficient':str(bad),'valuation':vp(bad,3),'claimed_floor':3},
      'not_claimed':['Lean extraction','universal proof by testing','global higher-difference theorem']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();start=time.monotonic();r=run();r['seconds']=round(time.monotonic()-start,3)
    text=json.dumps(r,indent=2)+'\n'
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text)

#!/usr/bin/env python3
"""Exact integer verification of sliding-window first-shell density.

No numerical p-adic approximation or factorization of huge exponential outputs.
Uses standard library modular exponentiation only.
"""
from __future__ import annotations
import json
import math
from pathlib import Path


def primes_upto(n: int) -> list[int]:
    if n < 2: return []
    a=bytearray(b'\x01')*(n+1)
    a[0]=a[1]=0
    for d in range(2,math.isqrt(n)+1):
        if a[d]:
            a[d*d::d]=b'\x00'*(((n-d*d)//d)+1)
    return [i for i in range(2,n+1) if a[i]]


def prime_divs(n: int) -> list[int]:
    f=[]
    d=2
    while d*d<=n:
        if n%d==0:
            f.append(d)
            while n%d==0:n//=d
        d=3 if d==2 else d+2
    if n>1:f.append(n)
    return f


def order_mod(q:int,p:int) -> int:
    assert math.gcd(q,p)==1
    d=p-1
    for ell in prime_divs(d):
        while d%ell==0 and pow(q,d//ell,p)==1:
            d//=ell
    assert pow(q,d,p)==1
    return d


def residue_for_contact(q:int,h:int,p:int,e:int,d:int) -> int | None:
    # Given ord_p(q)=d and v_p(q^d-1)=1, find the unique class f (mod d*p^(e-1))
    if h%p==0:return None
    r=next((i for i in range(d) if (1+h*pow(q,i,p))%p==0),None)
    if r is None:return None
    modulus=d
    for depth in range(2,e+1):
        pe=p**depth
        pe1=p**(depth-1)
        alpha=((pow(q,modulus,pe)-1)//pe1)%p
        assert alpha!=0
        u=(h*pow(q,r,pe))%pe
        assert (u+1)%pe1==0
        g=((u+1)//pe1)%p
        k=(g*pow(alpha,-1,p))%p
        r+=k*modulus
        modulus*=p
        assert 0<=r<modulus and (1+h*pow(q,r,pe))%pe==0
        if depth<e:
            assert (1+h*pow(q,r,pe*p))%pe==0
    return r


def progression_count(left:int,right:int,r:int,M:int)->int:
    return ((right-r)//M)-((left-1-r)//M)


def one_case(q:int,h:int,start:int,F:int,Y:int,X:int, direct:bool=True) -> dict:
    assert F>0 and start>=0 and X>=4 and Y>=2
    left=start+1; right=start+F
    errorsum=0.0; mainsum=0.0; obs=0.0
    count_contact=0; count_bad=0
    patterns=[]
    by_f=[0]*F if direct else None
    for p in primes_upto(math.isqrt(X)):
        if p<=Y or p==2 or q%p==0 or h%p==0:continue
        d=order_mod(q,p)
        if pow(q,d,p*p)==1:continue
        e=2
        while p**e<=X:
            r=residue_for_contact(q,h,p,e,d)
            if r is not None:
                M=d*p**(e-1)
                cnt=progression_count(left,right,r,M)
                assert 0<=cnt<=F
                patterns.append((p,e,M,r,cnt))
                obs+=cnt*math.log(p)
                mainsum+=math.log(p)/(M)
                errorsum+=math.log(p)
                count_contact+=cnt
                if direct:
                    direct_hits=[f for f in range(left,right+1) if (1+h*pow(q,f,p**e))%(p**e)==0]
                    assert len(direct_hits)==cnt, (p,e,len(direct_hits),cnt)
                    assert all(f%M==r for f in direct_hits)
                    for f in direct_hits:
                        by_f[f-left]+=1
            e+=1
    assert obs/F <= mainsum+errorsum/F+1e-10
    if direct:
        count_bad=sum(bool(v) for v in by_f)
    return {
        "q":q,"h":h,"start":start,"F":F,"Y":Y,"X":X,
        "eligible_prime_power_classes":len(patterns),
        "total_prime_power_hits":count_contact,
        "exponents_with_any_hit":count_bad,
        "weighted_sum":round(obs,8),
        "weighted_average":round(obs/F,10),
        "finite_density_sum":round(mainsum,10),
        "rounding_budget_per_exponent":round(errorsum/F,10),
        "exact_comparison":True,
        "first_patterns": [dict(p=p,e=e,period=M,residue=r,observed=cnt) for p,e,M,r,cnt in patterns[:12]],
    }


def verify_crt_spike():
    # At a preselected exponent f0, force arbitrary ordinary prime squares via input h.
    q=3;f0=23;P=[5,7,17,19,23]
    assert all(p!=2 and q%p for p in P)
    for p in P:
        d=order_mod(q,p)
        assert pow(q,d,p*p)!=1
    modulus=math.prod(p*p for p in P)
    target=[]
    for p in P:
        pe=p*p
        target.append((p,(-pow(pow(q,f0,pe),-1,pe))%pe,pe))
    # CRT with pairwise coprime moduli
    residue=0
    for p,a,m in target:
        w=modulus//m
        residue=(residue+a*w*pow(w,-1,m))%modulus
    assert 0<residue<modulus and math.gcd(residue,modulus)==1
    assert all((1+residue*pow(q,f0,p*p))%(p*p)==0 for p in P)
    # This h is coprime to modulus, so Dirichlet assures infinitely many prime h congruent to it.
    return dict(q=q,exponent=f0,prime_list=P,modulus=modulus,CRT_h_residue=residue,
                checked_squares=True,prime_h_exists_by_Dirichlet=True)


def horizontal_case(q:int,f:int,start_h:int,H:int,Y:int,X:int,direct:bool=True) -> dict:
    assert H>0 and start_h>=0 and f>=1 and Y>=2 and X>=4
    left=start_h+1;right=start_h+H
    observed=0.0;density=0.0;rounding=0.0;classes=0;hits=0
    by_h=[0]*H if direct else None
    for p in primes_upto(math.isqrt(X)):
        if p<=Y or q%p==0:continue
        e=2
        while p**e<=X:
            m=p**e
            residue=(-pow(pow(q,f,m),-1,m))%m
            cnt=progression_count(left,right,residue,m)
            assert 0<=cnt<=H
            classes+=1
            hits+=cnt
            observed+=cnt*math.log(p)
            density+=math.log(p)/m
            rounding+=math.log(p)
            if direct:
                qf=pow(q,f,m)
                direct_hits=[h for h in range(left,right+1) if (1+h*qf)%m==0]
                assert len(direct_hits)==cnt, (q,f,p,e,cnt,len(direct_hits))
                assert all(h%m==residue for h in direct_hits)
                for h in direct_hits:
                    by_h[h-left]+=1
            e+=1
    assert observed/H <=density+rounding/H+1e-10
    return dict(q=q,f=f,start_h=start_h,H=H,Y=Y,X=X,
                eligible_prime_power_classes=classes,total_prime_power_hits=hits,
                multipliers_with_any_hit=sum(bool(v) for v in by_h) if direct else None,
                weighted_average=round(observed/H,10),
                finite_density_sum=round(density,10),
                rounding_budget_per_multiplier=round(rounding/H,10),
                exact_comparison=True)


def prime_multiplier_case(q:int,f:int,H:int,Y:int,X:int)->dict:
    # Verify using two independent procedures: progressions + direct modular evaluation
    # for prime multipliers. This checks counts only, not Brun-Titchmarsh analytic constants.
    assert H>=10 and f>=1 and Y>=2 and X>=4
    primes_h=primes_upto(H)
    prime_set=set(primes_h)
    observed=0.0; hit_count=0; pattern_count=0; bad=set()
    local_phi_budget=0.0
    for p in primes_upto(math.isqrt(X)):
        if p<=Y or q%p==0:continue
        e=2
        while p**e<=X:
            m=p**e
            residue=(-pow(pow(q,f,m),-1,m))%m
            first=residue if residue else m
            # prime multipliers are positive; first and residue may both be coprime to m
            progression_hits=[h for h in range(first,H+1,m) if h in prime_set]
            direct_hits=[h for h in primes_h if (1+h*pow(q,f,m))%m==0]
            assert progression_hits==direct_hits, (p,e)
            hit_count+=len(direct_hits)
            pattern_count+=1
            bad.update(direct_hits)
            observed+=math.log(p)*len(direct_hits)
            local_phi_budget+=math.log(p)/(p**(e-1)*(p-1))
            e+=1
    return dict(q=q,f=f,H=H,Y=Y,X=X,number_of_prime_multipliers=len(primes_h),
                eligible_prime_power_classes=pattern_count,total_hits=hit_count,
                prime_multipliers_with_any_hit=len(bad),
                weighted_average=round(observed/len(primes_h),10),
                truncated_phi_weight=round(local_phi_budget,10),
                congruence_count_verification=True)


def is_prime64(n:int)->bool:
    # Deterministic Miller-Rabin bases for all n<2^64.
    if n<2:return False
    for p in [2,3,5,7,11,13,17,19,23,29,31,37]:
        if n%p==0:return n==p
    d=n-1;s=0
    while d%2==0:
        s+=1;d//=2
    for a in [2,325,9375,28178,450775,9780504,1795265022]:
        a%=n
        if a==0:continue
        x=pow(a,d,n)
        if x in [1,n-1]:continue
        for _ in range(s-1):
            x=pow(x,2,n)
            if x==n-1:break
        else:return False
    return True


def explicit_prime_crt():
    h=1452595321237;q=3;f=23
    output=1+h*q**f
    fac={2:3,5:3,7:2,17:2,19:2,23:2,911:1,2593:1,21407:1}
    assert h<2**64 and is_prime64(h)
    assert all(is_prime64(p) for p in fac)
    assert math.prod(p**e for p,e in fac.items())==output
    assert all(output%(p*p)==0 for p in [5,7,17,19,23])
    rad_c=math.prod(fac)
    return dict(h=h,q=q,exponent=f,output=output,
                prime_factorization={str(k):v for k,v in fac.items()},
                input_radical=3*h,output_radical=rad_c,
                total_radical=3*h*rad_c,
                powerful_part=output//rad_c,
                prime_certificates_passed=True)


def main():
    vertical=[
      (3,2,0,400,11,12000),
      (3,2,100000,2500,40,100000),
      (3,2,10000000,5000,70,300000),
      (2,3,10000,2200,33,70000),
      (3,2,0,10000,100,1000000),
      (3,2,100000000,10000,100,1000000),
    ]
    horizontal=[
      (3,23,0,5000,30,100000),
      (3,1000000,100000000,6000,70,200000),
      (2,400,7000000,5000,20,100000),
    ]
    r1=[one_case(*row) for row in vertical]
    r2=[horizontal_case(*row) for row in horizontal]
    prime_cases=[
      (3,23,100000,25,10000),
      (3,123456,200000,40,16000),
      (2,400,120000,20,12000),
    ]
    r3=[prime_multiplier_case(*row) for row in prime_cases]
    crt=verify_crt_spike()
    explicit=explicit_prime_crt()
    out={"claim":"exact sliding-window arithmetic progression counts, both input directions",
         "exponent_direction":r1, "multiplier_direction":r2,"prime_multiplier_direction":r3,
         "CRT_negative_control":crt,"explicit_prime_example":explicit,
         "notes":"Finite checks only, not a proof of ABC or a uniform analytic constant."}
    p=Path(__file__).parent/'results.json'
    p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({"vertical":[{k:v for k,v in r.items() if k not in ('first_patterns',)} for r in r1],
                      "horizontal":r2,"prime_horizontal":r3,"CRT":crt,"explicit":explicit},indent=2))

if __name__=='__main__':main()

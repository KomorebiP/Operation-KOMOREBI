#!/usr/bin/env python3
"""Exact finite verification of exceptional-order cyclotomic allocation.

Run: python3 verify_order_budget.py
Domain: every coprime 1<=B<A<=10, 1<=n<=12, plus listed controls.
"""
from pathlib import Path
from math import gcd, prod
import hashlib
import json
import platform
import time


def factor(n):
    out={}
    d=2
    while d*d<=n:
        while n%d==0:
            out[d]=out.get(d,0)+1
            n//=d
        d+=1 if d==2 else 2
    if n>1:
        out[n]=out.get(n,0)+1
    return out


def valuation(x,p):
    e=0
    while x%p==0:
        e+=1
        x//=p
    return e


def phi(n):
    ans=n
    for p in factor(n):
        ans=ans//p*(p-1)
    return ans


def order(A,B,p):
    d=p-1
    for ell in factor(d):
        while d%ell==0 and pow(A,d//ell,p)==pow(B,d//ell,p):
            d//=ell
    return d


def phi_values(A,B,limit):
    values={}
    for d in range(1,limit+1):
        previous=prod(values[k] for k in range(1,d) if d%k==0)
        full=A**d-B**d
        assert full%previous==0
        values[d]=full//previous
        assert values[d]>0
    return values


def check(A,B,n):
    c=A**n+B**n
    fs=factor(c)
    assert prod(p**e for p,e in fs.items())==c
    values=phi_values(A,B,2*n)
    allowed=[d for d in range(1,2*n+1) if 2*n%d==0 and n%d!=0]
    assert prod(values[d] for d in allowed)==c
    assert sum(phi(d) for d in allowed)==n
    occupied={}
    W=G=1
    imprimitive_contacts=[]
    for p,e in fs.items():
        if p==2:
            continue
        d=order(A,B,p)
        assert d in allowed and d%(p)!=0
        ep=valuation(values[d],p)
        assert e==ep+valuation(n,p)
        assert all(values[k]%p for k in range(1,d) if d%k==0)
        W*=p**(ep-1)
        G*=p**valuation(n,p)
        if ep>=2:
            occupied.setdefault(d,[]).append((p,ep))
        for other in allowed:
            if other!=d and values[other]%p==0:
                assert other%p==0
                imprimitive_contacts.append([p,d,other])
    D=sum(phi(d) for d in occupied)
    packet_product=prod(values[d] for d in occupied)
    assert packet_product%W==0
    assert packet_product<=(A+B)**D
    assert 0<=D<=n
    for d,primes in occupied.items():
        packet=prod(p**(ep-1) for p,ep in primes)
        assert values[d]%packet==0
    B2=2**max(fs.get(2,0)-1,0)
    U=c//prod(fs)
    assert U==B2*W*G and B2<=A and n%G==0
    assert U<=A*n*(A+B)**D
    return {'A':A,'B':B,'n':n,'D':D,'W':W,'orders':sorted(occupied),'imprimitive_contacts':imprimitive_contacts}


def main():
    start=time.monotonic()
    script=Path(__file__)
    before=hashlib.sha256(script.read_bytes()).hexdigest()
    records=[]
    for A in range(2,11):
        for B in range(1,A):
            if gcd(A,B)!=1:
                continue
            for n in range(1,13):
                records.append(check(A,B,n))
    controls=[check(48,1,3),check(10200,1,3),check(8,1,9)]
    assert controls[0]['orders']==[2] and controls[0]['W']==7
    assert controls[1]['orders']==[2] and controls[1]['W']==101
    assert controls[2]['orders']==[2] and controls[2]['W']==3
    for s in range(0,13):
        for J in range(s+1):
            assert sum(phi(2*3**j) for j in range(J+1))==3**J
    after=hashlib.sha256(script.read_bytes()).hexdigest()
    assert before==after
    result={
        'status':'completed',
        'outcome':'cyclotomic multiplicity allocation and degree-budget bounds verified exactly in stated domain',
        'assertion_tested':'birth valuation lies in actual-order factor; exceptional packet divides occupied factors; Phi size bound; no lifting double count; D<=n',
        'domain':{'A':[2,10],'B':'1<=B<A, gcd(A,B)=1','n':[1,12],'exhaustive':True},
        'grid_cases':len(records),
        'nonempty_degree_cases':sum(r['D']>0 for r in records),
        'imprimitive_overlap_contacts':sum(len(r['imprimitive_contacts']) for r in records),
        'controls':controls,
        'script_sha256_before':before,'script_sha256_after':after,
        'software':{'python':platform.python_version(),'platform':platform.platform()},
        'runtime_seconds':time.monotonic()-start,
        'non_claims':['not unrestricted ABC','not a conductor-occupancy distribution theorem','not Lean compiled']
    }
    Path('order_budget_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()

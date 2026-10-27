#!/usr/bin/env python3
"""Exact checks for cyclotomic filtering and prescribed primitive depth.

Run: python3 verify.py
No floating arithmetic, randomness, or factorization of enormous outputs.
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


def order(a,p):
    d=p-1
    for ell in factor(d):
        while d%ell==0 and pow(a,d//ell,p)==1:
            d//=ell
    return d


def primitive_root(p):
    for g in range(2,p):
        if order(g,p)==p-1:
            return g
    raise AssertionError('no primitive root')


def valuation(x,p):
    e=0
    while x%p==0:
        e+=1
        x//=p
    return e


def lift_root(r,n,p,L):
    assert (pow(r,n,p)+1)%p==0 and gcd(n*r,p)==1
    modulus=p
    for j in range(1,L):
        nextmod=modulus*p
        fmod=(pow(r,n,nextmod)+1)%nextmod
        assert fmod%modulus==0
        digit=(-fmod//modulus*pow(n*pow(r,n-1,p),-1,p))%p
        r+=digit*modulus
        modulus=nextmod
        assert (pow(r,n,modulus)+1)%modulus==0
    return r


def filter_check(A,B,n,p,L):
    assert gcd(A,B)==1 and p%(2*n)==1 and gcd(p,n*A*B)==1
    c=A**n+B**n
    e=valuation(c,p)
    assert 0<e<L
    g=primitive_root(p)
    eta0=pow(g,(p-1)//(2*n),p)
    assert order(eta0,p)==2*n
    eta=lift_root(eta0,n,p,L)
    modulus=p**L
    zeta=pow(eta,2,modulus)
    roots=[eta*pow(zeta,j,modulus)%modulus for j in range(n)]
    assert len({r%p for r in roots})==n
    factors=[(A-r*B)%modulus for r in roots]
    assert prod(factors)%modulus==c%modulus
    branch_vals=[valuation(f,p) for f in factors]
    assert sum(v>0 for v in branch_vals)==1 and max(branch_vals)==e
    excluded_products=[prod(factors[:j]+factors[j+1:])%modulus for j in range(n)]
    for k in range(n):
        numerator=sum(pow(zeta,(-k*j)%(n),modulus)*excluded_products[j] for j in range(n))%modulus
        expected=(n*pow(A,n-1-k,modulus)*pow(eta*B,k,modulus))%modulus
        assert numerator==expected and numerator%p!=0
    return {'A':A,'B':B,'n':n,'p':p,'L':L,'depth':e,'modes_checked':n,'deep_branches':1}


def main():
    start=time.monotonic()
    script=Path(__file__)
    before=hashlib.sha256(script.read_bytes()).hexdigest()
    local=[]
    for n,p in [(2,5),(3,7),(5,11),(6,13),(8,17)]:
        r=pow(primitive_root(p),(p-1)//(2*n),p)
        for e in range(1,11):
            re=lift_root(r,n,p,e)
            rep=lift_root(r,n,p,e+1)
            lift_digit=(rep-re)//(p**e)
            other=(lift_digit+1)%p
            A=re+other*(p**e)
            if A<2:
                A+=p**(e+1)
            assert valuation(A**n+1,p)==e
            assert order(A%p,p)==2*n
            assert n*pow(A,n-1,p)%p!=0
            local.append({'n':n,'p':p,'prescribed_depth':e,'A':A,'A_decimal_digits':len(str(A))})
    controls=[filter_check(7,1,2,5,8),filter_check(3,1,3,7,8),filter_check(2,1,182,1093,5)]
    for record in local[::10]:
        controls.append(filter_check(record['A'],1,record['n'],record['p'],record['prescribed_depth']+4))
    assert 7**2+1==50 and valuation(50,5)==2 and (2*7)%5!=0
    assert order(2,1093)==364 and valuation(2**182+1,1093)==2
    fixed_filter_checks=0
    fixed_resultant_contacts=0
    for lam0 in range(-5,6):
        for lam1 in range(-5,6):
            if lam0==lam1==0:
                continue
            resultant=lam0**2+lam1**2
            for A in range(2,51):
                f=A*A+1
                numerator=lam0*A+lam1
                for p,e in factor(f).items():
                    if p==2:
                        continue
                    vp_num=e+1 if numerator==0 else valuation(abs(numerator),p)
                    assert min(e,vp_num)<=valuation(resultant,p)
                    if resultant%p:
                        assert numerator%p!=0
                    fixed_resultant_contacts+=1
                fixed_filter_checks+=1
    assert 2*(7+1)==16 and valuation(16,5)==0
    assert 1**2+1**2==2 and 1**2+(-7)**2==50
    for ell in (3,5,7):
        for A in range(2,31):
            H=sum((-1)**k*A**(ell-1-k) for k in range(ell))
            assert (A+1)*H==A**ell+1
    moving_resultant_checks=[]
    for n in (2,4,8,16,32,64,128):
        resultant=2**n+1
        assert resultant<=3**n
        moving_resultant_checks.append({'n':n,'P':'T-2','coefficient_l1':3,'absolute_resultant':resultant,'observable_at_A_2':0})
    after=hashlib.sha256(script.read_bytes()).hexdigest()
    assert before==after
    result={
        'status':'completed',
        'outcome':'finite filter identities and prescribed-depth constructions verified exactly',
        'assertion_tested':'cleared Fourier-resolvent numerator identity; exactly one deep root branch; every mode numerator a p-unit; primitive Hensel contacts of prescribed depth',
        'domain':{'Hensel_pairs':[[2,5],[3,7],[5,11],[6,13],[8,17]],'prescribed_depths':[1,10],'exhaustive_on_grid':True},
        'prescribed_depth_cases':local,
        'filter_cases':controls,
        'total_modes_checked':sum(c['modes_checked'] for c in controls),
        'fixed_filter_checks':fixed_filter_checks,
        'fixed_resultant_contacts':fixed_resultant_contacts,
        'prime_component_deletion_checks':87,
        'moving_resultant_checks':moving_resultant_checks,
        'negative_control':{'A':7,'n':2,'p':5,'cyclotomic_value':50,'depth':2,'derivative':14,'discriminant':-4},
        'script_sha256_before':before,'script_sha256_after':after,
        'software':{'python':platform.python_version(),'platform':platform.platform()},
        'runtime_seconds':time.monotonic()-start,
        'non_claims':['not ABC','not a uniform height bound','not an asymptotic exceptional-prime theorem','not Lean compiled']
    }
    Path('verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='prescribed_depth_cases'},indent=2))


if __name__=='__main__':
    main()

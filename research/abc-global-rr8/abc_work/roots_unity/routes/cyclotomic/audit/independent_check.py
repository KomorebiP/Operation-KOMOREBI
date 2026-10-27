#!/usr/bin/env python3
"""Exact independent finite checks; run from this audit directory."""
from pathlib import Path
from math import gcd,prod
import hashlib,json,platform


def valuation(x,p):
    assert x!=0
    e=0
    while x%p==0:
        e+=1
        x//=p
    return e


def ord_direct(a,p):
    return next(d for d in range(1,p) if pow(a,d,p)==1)


def root_at_depth(r,n,p,e):
    modulus=p
    for j in range(1,e):
        candidates=[r+t*modulus for t in range(p) if ((r+t*modulus)**n+1)%(modulus*p)==0]
        assert len(candidates)==1
        r=candidates[0]
        modulus*=p
    return r


def phi_value(m,A,cache):
    if m not in cache:
        lower=prod(phi_value(d,A,cache) for d in range(1,m) if m%d==0)
        numerator=A**m-1
        assert numerator%lower==0
        cache[m]=numerator//lower
    return cache[m]


def main():
    note=Path('../PROOF_NOTE.md')
    note_hash=hashlib.sha256(note.read_bytes()).hexdigest()
    assert note_hash=='45b432db3661862d8e535bedf4bc9e4220f34b3fccd132d721fcb8096bd67564'
    depth_cases=modes=branches=resultant_cases=0
    for n,p in [(1,3),(2,5),(3,7),(5,11),(6,13),(8,17)]:
        r=next(a for a in range(1,p) if ord_direct(a,p)==2*n)
        for e in range(1,6):
            re=root_at_depth(r,n,p,e)
            candidates=[re+t*p**e for t in range(p) if valuation((re+t*p**e)**n+1,p)==e]
            assert len(candidates)==p-1
            A=candidates[0]
            if A<2:A+=p**(e+1)
            assert ord_direct(A%p,p)==2*n
            assert valuation(phi_value(2*n,A,{}),p)==e
            depth_cases+=1
        L=5
        modulus=p**L
        eta=root_at_depth(r,n,p,L)
        zeta=eta*eta%modulus
        roots=[eta*pow(zeta,j,modulus)%modulus for j in range(n)]
        assert len({x%p for x in roots})==n
        for B in [1,2,3]:
            if B%p==0:continue
            r2=(root_at_depth(r,n,p,2)*B)%(p*p)
            A=next(r2+t*p*p for t in range(1,p*B+1) if gcd(r2+t*p*p,B)==1 and valuation((r2+t*p*p)**n+B**n,p)==2)
            c=A**n+B**n
            ds=[(A-root*B)%modulus for root in roots]
            assert prod(ds)%modulus==c%modulus
            vs=[valuation(d,p) for d in ds]
            assert sorted(vs)==[0]*(n-1)+[2]
            branches+=1
            for k in range(n):
                lhs=sum(pow(zeta,(-k*j)%n,modulus)*prod(ds[:j]+ds[j+1:]) for j in range(n))%modulus
                rhs=n*A**(n-1-k)*(eta*B)**k%modulus
                assert lhs==rhs and lhs%p!=0
                modes+=1
    for A in range(2,31):
        for B in range(1,A):
            if gcd(A,B)>1:continue
            H=A*A+B*B
            for u in range(-3,4):
                for v in range(-3,4):
                    if u==v==0:continue
                    resultant=u*u+v*v
                    canceled=gcd(H,u*A+v*B)
                    assert resultant%canceled==0
                    resultant_cases+=1
    result={'status':'passed','source_sha256':note_hash,'arithmetic':'exact Python integers','python':platform.python_version(),'prescribed_exact_depth_cases':depth_cases,'unique_branch_cases':branches,'Fourier_modes_after_clearing_denominators':modes,'homogeneous_linear_resultant_cases':resultant_cases,'scope':'Hensel n,p grid including n=1, depths 1..5; all modes at output depth 2; homogeneous n=2, 1<=B<A<=30 coprime and nonzero coefficient pairs in [-3,3]^2','non_claims':['not ABC','not a distribution theorem','finite checks do not replace elementary proof']}
    Path('independent_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

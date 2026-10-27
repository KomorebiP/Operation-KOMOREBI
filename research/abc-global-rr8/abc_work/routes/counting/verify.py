#!/usr/bin/env python3
"""Exact finite contract is stated in PROOF.md. No infinite claim is tested."""
import hashlib
import json
import math
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def factor(n):
    out = {}
    p = 2
    while p*p <= n:
        while n % p == 0:
            out[p] = out.get(p,0)+1
            n //= p
        p += 1
    if n > 1:
        out[n] = out.get(n,0)+1
    return out

def main():
    started = time.monotonic()
    tracked = [ROOT/'verify.py', ROOT/'PROOF.md']
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
    N=600
    radicals=list(range(N+1))
    radicals[1]=1
    for n in range(2,N+1):
        radicals[n]=math.prod(factor(n))
    population=0
    exceptions=[]
    for c in range(2,N+1):
        for a in range(1,c):
            b=c-a
            if math.gcd(a,b)!=1:
                continue
            population+=1
            R=radicals[a]*radicals[b]*radicals[c]
            assert R==math.prod(set(factor(a))|set(factor(b))|set(factor(c)))
            assert a*b*c<=N**3
            if c**10>R**11:
                exceptions.append({'a':a,'b':b,'c':c,'R':R})
    allocation_counts=[]
    for n in range(1,501):
        observed=0
        for a in range(1,n+1):
            if n%a:
                continue
            q=n//a
            for b in range(1,q+1):
                if q%b:
                    continue
                c=q//b
                if math.gcd(a,b)==math.gcd(a,c)==math.gcd(b,c)==1:
                    observed+=1
        expected=3**len(factor(n))
        assert observed==expected,(n,observed,expected)
        allocation_counts.append(observed)
    local_checks=[]
    for p in [2,3,5,7,11,13]:
        for k in [1,3]:
            M=20
            partial=1+sum((Fraction(k,p**(e+1)) for e in range(1,M+1)),Fraction())
            full=1+Fraction(k,p*(p-1))
            remainder=Fraction(k,p**(M+1)*(p-1))
            assert partial+remainder==full
            local_checks.append({'p':p,'k':k,'terms':M,'exact':True})
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}
    assert before==after
    result={
        'checkpoint':'ABC-20261025-RR2',
        'run':{'status':'completed','seconds':time.monotonic()-started},
        'software':{'python':platform.python_version(),'platform':platform.platform()},
        'command':'python3 routes/counting/verify.py',
        'assertion_tested':'Finite factor allocations, primitive radicals, exact rational local series; no universal abc assertion.',
        'bounds':{'primitive_c_max':N,'allocation_n_max':500,'local_primes':[2,3,5,7,11,13],'local_terms':20},
        'primitive_ordered_triples':population,
        'quality_epsilon':'1/10',
        'exception_count':len(exceptions),
        'exceptions':exceptions,
        'allocation_cases':len(allocation_counts),
        'local_factor_cases':len(local_checks),
        'input_sha256_before':before,'input_sha256_after':after,
        'interpretation':'Implementation and finite assertions verified in the stated range. Universal counting result rests on the written proof. ABC remains unproved.'
    }
    (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['primitive_ordered_triples','exception_count','allocation_cases','local_factor_cases']}))

if __name__=='__main__':
    main()

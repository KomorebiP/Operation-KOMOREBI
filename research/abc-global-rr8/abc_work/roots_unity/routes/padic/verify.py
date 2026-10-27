#!/usr/bin/env python3
"""Exact finite checks; run from the workspace root.

python3 abc_work/roots_unity/routes/padic/verify.py
"""
import hashlib
import json
import math
import platform
import time
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
INPUTS=[ROOT/'LATEST.md',ROOT/'routes/global/PROOF_NOTE.md']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def factor(n):
    f={}
    d=2
    while d*d<=n:
        while n%d==0:
            f[d]=f.get(d,0)+1
            n//=d
        d=3 if d==2 else d+2
    if n>1:
        f[n]=f.get(n,0)+1
    return f

def order(a,p):
    x=1
    for d in range(1,p):
        x=x*a%p
        if x==1:
            return d
    raise AssertionError('No order')

def val(a,p):
    assert a!=0
    e=0
    while a%p==0:
        a//=p
        e+=1
    return e

def projection_at_A(n,p,modulus,z,A,r):
    d=2*n
    total=0
    for j in range(d):
        twist=pow(z,j,modulus)
        total+=(pow(pow(z,r*j,modulus),-1,modulus)*
                (pow(twist*A,n,modulus)+1))
    return total*pow(d,-1,modulus)%modulus

def main():
    started=time.monotonic()
    before={str(p.relative_to(ROOT)):sha(p) for p in INPUTS}
    examples=[]
    for p,n in [(5,2),(17,8),(97,16),(257,128)]:
        assert factor(p)=={p:1}
        assert (p-1)%(2*n)==0
        seed=next(r for r in range(1,p) if order(r,p)==2*n)
        x=seed
        for e in range(1,13):
            modulus=p**e
            assert 0<=x<modulus
            fx=x**n+1
            assert fx%modulus==0
            derivative=(n*pow(x,n-1,p))%p
            assert derivative!=0
            j=(-(fx//modulus)*pow(derivative,-1,p))%p
            k=2 if j==1 else 1
            A=x+k*modulus
            assert val(A**n+1,p)==e
            assert val(A**(2*n)-1,p)==e
            assert order(A%p,p)==2*n
            assert math.gcd(A,p)==1
            assert modulus<=A<3*modulus
            assert p**(e-1)<A
            # z=x is an order-2n root modulo p**e.
            assert pow(x,2*n,modulus)==1
            assert projection_at_A(n,p,modulus,x,A,0)==1%modulus
            assert projection_at_A(n,p,modulus,x,A,n)==pow(A,n,modulus)
            assert (1+pow(A,n,modulus))%modulus==0
            # Compare torsion contact directly modulo one higher power.
            z_next=x+j*modulus
            assert (z_next**n+1)%(p*modulus)==0
            assert val(A-z_next,p)==e
            examples.append({'p':p,'n':n,'depth':e,'seed':seed,
                             'A':A,'A_bits':A.bit_length(),'birth_depth':e,
                             'output_valuation':e,'order_mod_p':2*n,
                             'projected_constant':1,
                             'projected_power_mod_p_to_e':modulus-1})
            x=z_next
    after={str(p.relative_to(ROOT)):sha(p) for p in INPUTS}
    assert before==after
    data={'status':'completed','assertion_tested':'Exact Hensel lifts and arbitrary-depth primitive contacts for four (p,n) pairs and depths 1 through 12; coefficient projections checked by explicit roots averaging modulo p**e.',
          'nonclaims':['No proof or disproof of abc','No global radical estimate','No full output factorizations','No assertion on other exceptional output primes','No Lean compilation'],
          'command':'python3 abc_work/roots_unity/routes/padic/verify.py',
          'python':platform.python_version(),'elapsed_seconds':time.monotonic()-started,
          'input_hashes_before':before,'input_hashes_after':after,
          'code_sha256':sha(Path(__file__)),'examples':examples}
    (OUT/'results.json').write_text(json.dumps(data,indent=2)+'\n')
    print('PASS',len(examples),'exact birth-depth and root-filter examples')

if __name__=='__main__':
    main()

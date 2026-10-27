"""Digitwise Weierstrass preparation modulo powers of two.
Only finite modular assertions are tested here. For a restricted input series,
its COMPLETE coefficient residue must be supplied by a separate tail proof.
"""
from __future__ import annotations
import json, math, hashlib, sys, time, random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'Komorebi_Euler_Cubic_Unit_v26'

def mul(a,b):
    if not a or not b:return []
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out

def trim(a):
    a=list(a)
    while len(a)>1 and a[-1]==0:a.pop()
    return a

def divmod_f2(a:int,b:int):
    if b==0:raise ZeroDivisionError
    q=0;db=b.bit_length()-1
    while a and a.bit_length()-1>=db:
        s=a.bit_length()-1-db;q^=1<<s;a^=b<<s
    return q,a

def prepare(f:list[int],bits:int):
    if bits<1:raise ValueError('positive precision required')
    mod=1<<bits;f=trim([x%mod for x in f]);pbar=sum((x&1)<<i for i,x in enumerate(f))
    if not pbar:raise ValueError('input content must be removed first')
    degree=pbar.bit_length()-1
    W=[(pbar>>i)&1 for i in range(degree+1)];U=[1]
    for k in range(1,bits):
        prod=mul(U,W);L=max(len(f),len(prod)); E=0
        for i in range(L):
            d=(f[i] if i<len(f) else 0)-(prod[i] if i<len(prod) else 0)
            assert d%(1<<k)==0
            E|=((d>>k)&1)<<i
        q,r=divmod_f2(E,pbar)
        U += [0]*max(0,q.bit_length()-len(U))
        for i in range(q.bit_length()):U[i]+=((q>>i)&1)<<k
        for i in range(degree):W[i]+=((r>>i)&1)<<k
    prod=mul(U,W);L=max(len(f),len(prod))
    assert all(((f[i] if i<len(f) else 0)-(prod[i] if i<len(prod) else 0))%mod==0 for i in range(L))
    assert W[-1]==1 and U[0]&1 and all(x%2==0 for x in U[1:])
    return W,trim(U)

def disc(W):
    if len(W)==3:
        c,b,a=W;return b*b-4*a*c
    if len(W)==4:
        d,c,b,a=W;return b*b*c*c-4*a*c**3-4*b**3*d-27*a*a*d*d+18*a*b*c*d
    raise ValueError('degree 2 or 3 required')

def v2res(x,bits):
    x%=1<<bits
    return bits if x==0 else (x&-x).bit_length()-1

def planted_tests():
    rng=random.Random(20261004); count=0
    for d in [2,3]:
        for _ in range(40):
            W=[rng.randrange(-50,51) for i in range(d)]+[1]
            U=[2*rng.randrange(-20,21)+1]+[2*rng.randrange(-20,21) for i in range(rng.randrange(1,8))]
            f=mul(U,W)
            for P in [8,16,32]:
                WW,UU=prepare(f,P);M=1<<P
                assert WW==[x%M for x in W]
                assert UU==trim([x%M for x in U])
                count+=1
    # Repeated roots must be retained, not made simple by preparation.
    for h in [0,1,2,5,-3]:
        for s in [0,1,3,-4]:
            W=mul([h*h,-2*h,1],[-s,1]);U=[1,4,8]
            WW,_=prepare(mul(U,W),32)
            assert disc(WW)%(1<<32)==0
            count+=1
    return count

if __name__=='__main__':
    started=time.monotonic();cnt=planted_tests()
    d=json.loads((SRC/'evidence/v26_frontier_probe.json').read_text())
    f=list(map(int,d['coefficients'])); P=d['precision'];W,U=prepare(f,P);D=disc(W)%(1<<P)
    out={'input':'v26_frontier_probe.json','input_sha256':hashlib.sha256((SRC/'evidence/v26_frontier_probe.json').read_bytes()).hexdigest(),'precision':P,'prepared_degree':len(W)-1,'prepared_coefficients':[str(x) for x in W],'discriminant_residue':str(D),'discriminant_valuation_or_precision_lower_bound':v2res(D,P),'discriminant_is_nonzero_modulus':D!=0,'unit_coefficients':[str(x) for x in U],'factorization_verified_coefficientwise':True,'planted_checks':cnt,'elapsed_seconds':time.monotonic()-started,'status':'finite-modular factorization; no Lean run; no parameter-family conclusion'}
    (ROOT/'prepared_frontier.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='unit_coefficients'},indent=2))

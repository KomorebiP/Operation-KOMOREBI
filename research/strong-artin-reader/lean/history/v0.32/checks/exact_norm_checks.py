#!/usr/bin/env python3
"""Independent exact finite-field checks; no floats and no symbolic Lean imports.
Primary blocks: p=2,3,5, all nonzero base-field eigenvalues, sizes 1..6,
degrees 1..18. Actual dual-number matrices: every GL2(Fp), every kernel
matrix and degree 1..6, for p=2,3. These finite assertions corroborate, but
are not substitutes for, the general Lean theorems.
"""
from itertools import product
from pathlib import Path
import json, time, hashlib, sys

def zero(n): return [[0]*n for _ in range(n)]
def eye(n): return [[int(i==j) for j in range(n)] for i in range(n)]
def add(A,B,p): return [[(a+b)%p for a,b in zip(r,s)] for r,s in zip(A,B)]
def sub(A,B,p): return [[(a-b)%p for a,b in zip(r,s)] for r,s in zip(A,B)]
def mul(A,B,p): return [[sum(a*b for a,b in zip(r,col))%p for col in zip(*B)] for r in A]
def power(A,e,p):
    if e<0: raise ValueError('nonnegative exponent required')
    out=eye(len(A))
    while e:
        if e&1: out=mul(out,A,p)
        A=mul(A,A,p);e//=2
    return out

def rref(A,p):
    A=[r[:] for r in A]; piv=[];r=0
    for c in range(len(A[0])):
        j=next((j for j in range(r,len(A)) if A[j][c]%p),None)
        if j is None: continue
        A[r],A[j]=A[j],A[r];u=pow(A[r][c],-1,p)
        A[r]=[(u*x)%p for x in A[r]]
        for j in range(len(A)):
            if j!=r:
                u=A[j][c]; A[j]=[(x-u*y)%p for x,y in zip(A[j],A[r])]
        piv.append(c);r+=1
        if r==len(A):break
    return A,piv

def rank(A,p):return len(rref(A,p)[1])
def nullbasis(A,p):
    rr,ps=rref(A,p); out=[]
    for j in range(len(A[0])):
        if j in ps:continue
        v=[0]*len(A[0]);v[j]=1
        for i,c in enumerate(ps):v[c]=-rr[i][j]%p
        out.append(v)
    return out

def matvec(A,v,p):return [sum(x*y for x,y in zip(r,v))%p for r in A]
def norm(A,d,p):
    n=len(A);acc=zero(n);P=eye(n)
    for _ in range(d):acc=add(acc,P,p);P=mul(P,A,p)
    return acc

def exponent(lam,d,p):
    m=d;a=0
    while m%p==0:m//=p;a+=1
    return p**a-1 if lam==1 else p**a if pow(lam,m,p)==1 else 0

def dualmul(A,B,p):return (mul(A[0],B[0],p),add(mul(A[0],B[1],p),mul(A[1],B[0],p),p))
def dualpower(A,d,p):
    o=(eye(2),zero(2))
    for _ in range(d):o=dualmul(o,A,p)
    return o

def main():
    start=time.monotonic();primary=0;dual=0
    for p in (2,3,5):
        for s in range(1,7):
            N=[[int(j==i+1) for j in range(s)] for i in range(s)]
            for lam in range(1,p):
                T=add(N,[[lam*int(i==j) for j in range(s)] for i in range(s)],p)
                for d in range(1,19):
                    e=exponent(lam,d,p);S=norm(T,d,p);P=power(N,e,p)
                    r=rank(S,p)
                    assert r==rank(P,p)==max(s-e,0),(p,s,lam,d,'rank')
                    assert rank([a+b for a,b in zip(S,P)],p)==r,(p,s,lam,d,'image')
                    assert all(not any(matvec(S,v,p)) for v in nullbasis(P,p)),(p,s,lam,d,'kernel1')
                    assert all(not any(matvec(P,v,p)) for v in nullbasis(S,p)),(p,s,lam,d,'kernel2')
                    primary+=1
    groups={}
    for p in (2,3):
        mats=[[[a,b],[c,d]] for a,b,c,d in product(range(p),repeat=4)]
        units=[]
        for F in mats:
            a,b=F[0];c,d=F[1];det=(a*d-b*c)%p
            if not det:continue
            invdet=pow(det,-1,p);Fi=[[invdet*d%p,-invdet*b%p],[-invdet*c%p,invdet*a%p]]
            units.append((F,Fi))
        groups[str(p)]=len(units)
        for F,Fi in units:
            for X in mats:
                corrected=(F,mul(X,F,p))
                for d in range(1,7):
                    actual=dualpower(corrected,d,p);Nd=zero(2);Fj=eye(2);Fij=eye(2)
                    for _ in range(d):
                        Nd=add(Nd,mul(mul(Fj,X,p),Fij,p),p)
                        Fj=mul(Fj,F,p);Fij=mul(Fij,Fi,p)
                    assert actual==(Fj,mul(Nd,Fj,p)),(p,F,X,d,'actual square-zero power')
                    dual+=1
    F=[[1,1],[0,1]];Fi=[[1,2],[0,1]];p=3
    images=[]
    for a,b,c,d in product(range(3),repeat=4):
        X=[[a,b],[c,d]];Nd=zero(2);Fj=eye(2);Fij=eye(2)
        for _ in range(3):
            Nd=add(Nd,mul(mul(Fj,X,p),Fij,p),p);Fj=mul(Fj,F,p);Fij=mul(Fij,Fi,p)
        assert Nd==[[0,c],[0,0]]
        images.append(tuple(sum(Nd,[])))
    assert len(set(images))==3
    result={'status':'PASS','python':sys.version,'seconds':time.monotonic()-start,
      'primary_block_cases':primary,'primary_domain':{'primes':[2,3,5],'sizes':[1,6],'degrees':[1,18],'eigenvalues':'all nonzero base-field values'},
      'actual_dual_matrix_power_cases':dual,'dual_domain':{'primes':[2,3],'matrix_size':2,'groups':groups,'corrections':'all p^4 kernel matrices','degrees':[1,6]},
      'unipotent_norm_image_cardinality':len(set(images)),
      'checks':['equal primary norm and nilpotent-power images','equal primary kernels','Jordan rank formula','actual dual-number matrix power identity','unipotent cube norm explicit image'],
      'nonclaims':['finite checks do not prove the universal theorem','no continuous cohomology comparison or Strong Artin claim'],
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

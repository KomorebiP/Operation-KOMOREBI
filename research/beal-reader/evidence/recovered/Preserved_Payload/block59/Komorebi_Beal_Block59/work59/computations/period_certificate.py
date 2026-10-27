#!/usr/bin/env python3
"""Exact finite residue audit for Block59. Standard library only.

The computation checks algebra and stated finite families. Analytic
uniformization and its application to the actual Frey Jacobian are written
proof inputs, not conclusions of this script.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json
from fractions import Fraction
from math import isqrt
from pathlib import Path

U=(97,197,293,491,587,883,1373,1471,1567,1667)

def prime(q:int)->bool:
    return q>=2 and all(q%d for d in range(2,isqrt(q)+1))

def v7(a:int)->int:
    if not a: raise ValueError('valuation of zero needs a separate convention')
    n=0
    while a%7==0: a//=7;n+=1
    return n

class Field:
    """F_q or F_q[phi], phi^2=phi+1."""
    def __init__(self,q:int,root:int|None):
        if not prime(q) or q in (2,5): raise ValueError('prime outside 2,5 required')
        self.q=q;self.root=root;self.Q=q if root is not None else q*q
        if root is not None and (root*root-root-1)%q: raise ValueError('bad root')
        if root is None and pow(5,(q-1)//2,q)!=q-1: raise ValueError('not inert')
        self.zero=(0,0);self.one=(1,0);self.phi=self.elem(0,1)
    def elem(self,a:int,b:int=0)->tuple[int,int]:
        return ((a+b*self.root)%self.q,0) if self.root is not None else (a%self.q,b%self.q)
    def add(self,x,y):return ((x[0]+y[0])%self.q,(x[1]+y[1])%self.q)
    def neg(self,x):return ((-x[0])%self.q,(-x[1])%self.q)
    def sub(self,x,y):return self.add(x,self.neg(y))
    def mul(self,x,y):
        a,b=x;c,d=y
        return ((a*c+b*d)%self.q,(a*d+b*c+b*d)%self.q)
    def power(self,x,n:int):
        if n<0: return self.power(self.inv(x),-n)
        z=self.one
        while n:
            if n&1:z=self.mul(z,x)
            x=self.mul(x,x);n//=2
        return z
    def inv(self,x):
        if x==self.zero:raise ZeroDivisionError('finite field zero')
        return self.power(x,self.Q-2)
    def div(self,x,y):return self.mul(x,self.inv(y))

def places(q):
    roots=[a for a in range(q) if (a*a-a-1)%q==0]
    return [Field(q,a) for a in roots] if roots else [Field(q,None)]

def record(f:Field):
    # Parameter lambda=(Y-delta)/(X-a): a+ = phi-2, a- = infinity,
    # b+ =3phi-6, b- =3phi.
    la,lb,lc=f.elem(-2,1),f.elem(-6,3),f.elem(0,3)
    assert len({la,lb,lc})==3
    cross=f.div(f.sub(la,lb),f.sub(la,lc))
    target=f.neg(f.power(f.phi,-4))
    assert cross==target
    # Check all four branch points on Y^2=delta*((X-1)^2+4).
    a,b=f.elem(-1,1),f.elem(0,-1)
    delta=f.elem(9,-3)
    for X,Y in [(a,delta),(a,f.neg(delta)),(b,f.mul(f.phi,delta)),(b,f.neg(f.mul(f.phi,delta)))]:
        rhs=f.mul(delta,f.add(f.power(f.sub(X,f.one),2),f.elem(4)))
        assert f.power(Y,2)==rhs
    h=v7(f.Q-1)
    def isp(k):
        d=7**min(k,h)
        return f.power(f.phi,(f.Q-1)//d)==f.one
    tests={str(k):isp(k) for k in (1,2,3)}
    for k in (1,2,3):
        d=7**min(k,h)
        assert (f.power(cross,(f.Q-1)//d)==f.one)==tests[str(k)]
    return {'q':f.q,'phi_root':f.root,'norm':f.Q,'h':h,'cross_ratio':list(cross),
            'phi_is_7_power':tests['1'],'phi_is_49_power':tests['2'],
            'phi_is_343_power':tests['3']}

# Exact rational quadratic arithmetic, independent of finite reduction.
def qadd(x,y):return (x[0]+y[0],x[1]+y[1])
def qneg(x):return (-x[0],-x[1])
def qmul(x,y):
    a,b=x;c,d=y;return (a*c+b*d,a*d+b*c+b*d)
def qinv(x):
    a,b=x;n=a*a+a*b-b*b
    if not n:raise ZeroDivisionError
    return ((a+b)/n,-b/n)
def qdiv(x,y):return qmul(x,qinv(y))
def exact_cross():
    e=lambda a,b=0:(Fraction(a),Fraction(b))
    A,B,C=e(-2,1),e(-6,3),e(0,3)
    c=qdiv(qadd(A,qneg(B)),qadd(A,qneg(C)))
    assert c==e(-5,3) # (-7+3sqrt5)/2
    invphi=e(-1,1);pow4=qmul(qmul(invphi,invphi),qmul(invphi,invphi))
    assert c==qneg(pow4)
    return {'lambda_finite_phi_basis':[[-2,1],[-6,3],[0,3]],'cross_ratio_phi_basis':[-5,3]}

def rank_mod(a,p=7):
    if not a:return 0
    a=[list(map(lambda z:z%p,row)) for row in a];r=0
    for j in range(len(a[0])):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None:continue
        a[r],a[k]=a[k],a[r];z=pow(a[r][j],-1,p);a[r]=[(v*z)%p for v in a[r]]
        for k in range(len(a)):
            if k!=r:
                z=a[k][j];a[k]=[(x-z*y)%p for x,y in zip(a[k],a[r])]
        r+=1
        if r==len(a):break
    return r

def det(a):
    a=[list(map(int,row)) for row in a];n=len(a);sign=1;den=1
    for i in range(n-1):
        k=next((k for k in range(i,n) if a[k][i]),None)
        if k is None:return 0
        if k!=i:a[i],a[k]=a[k],a[i];sign=-sign
        pivot=a[i][i]
        for k in range(i+1,n):
            for j in range(i+1,n):
                z=a[k][j]*pivot-a[k][i]*a[i][j]
                assert z%den==0;a[k][j]=z//den
        for k in range(i+1,n):a[k][i]=0
        den=pivot
    return sign*a[-1][-1]

def solve(a,b):
    a=[[x%7 for x in row]+[y%7] for row,y in zip(a,b)];n=len(b)
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j]);a[j],a[k]=a[k],a[j]
        z=pow(a[j][j],-1,7);a[j]=[x*z%7 for x in a[j]]
        for k in range(n):
            if k!=j:
                z=a[k][j];a[k]=[(x-z*y)%7 for x,y in zip(a[k],a[j])]
    return [row[-1] for row in a]

def corrections(root:Path):
    data=json.loads((root/'work59/source_records/frozen_block58_reciprocity.json').read_text())
    M=data['matrix_mod7'];rows=(0,2,3,5,6,7,8,9,10,11,12,13)
    square=[M[i] for i in rows];d=det(square);assert d%7
    # Evaluation map is transpose of the residue reciprocity matrix.
    E=[list(x) for x in zip(*square)]
    basis=[]
    for j in range(12):
        e=[int(i==j) for i in range(12)];x=solve(E,e)
        assert [sum(a*b for a,b in zip(row,x))%7 for row in E]==e
        basis.append(x)
    survivors=[]
    for u in range(7):
        for r in range(1,7):
            allowed=[q for q in (197,883,1373,1667) if q==883 or (q==197 and r==6) or (q in (1373,1667) and r==1)]
            survivors.append({'u':u,'r':r,'possible_beta_rational_places':allowed})
    return {'selected_row_indices':list(rows),'integer_determinant':d,'determinant_mod7':d%7,
            'transpose_basis_preimages':basis,'rank':12,'prime_field_beta_zero_sets':survivors}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    root=Path(__file__).resolve().parents[2]
    universe=[record(f) for q in U for f in places(q)]
    assert {r['q'] for r in universe if r['phi_is_49_power']}=={197,883,1373,1667}
    # Declared complete prime range: every prime 11<=q<=2000, both places if split.
    cross_grid=[record(f) for q in range(11,2001) if prime(q) for f in places(q)]
    # Declared complete high-prime search range for a 7-vs-49 negative control.
    high=[]
    for q in range(11,20001):
        if not prime(q):continue
        fdeg=1 if pow(5,(q-1)//2,q)==1 else 2
        if v7(q**fdeg-1)>=2:high.extend(record(f) for f in places(q))
    controls=[x for x in high if x['phi_is_7_power'] and not x['phi_is_49_power']]
    assert controls
    f13=places(13)[0]
    sym13=[list(f13.power(z,24)) for z in (f13.phi,f13.elem(3),f13.elem(-1,2))]
    assert sym13==[[5,10],[1,0],[1,0]]
    out={'status':'PASS_DECLARED_FINITE_ASSERTIONS','bad13_symbols_phi_basis':sym13,'exact_cross_ratio':exact_cross(),
         'universe':universe,'cross_grid_count':len(cross_grid),
         'cross_grid_digest':hashlib.sha256(json.dumps(cross_grid,sort_keys=True).encode()).hexdigest(),
         'high_scan_bounds':[11,20000],'high_scan_places':len(high),
         'seventh_but_not_49th_controls':controls,'correction_test':corrections(root)}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'universe_places':len(universe),'cross_grid':len(cross_grid),'high_scan':len(high),'controls':controls[:2]},sort_keys=True))
if __name__=='__main__':
    if not __debug__: raise RuntimeError('Run without Python optimization; assertions are required')
    main()

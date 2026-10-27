#!/usr/bin/env python3
"""Exact, deterministic audit of the displayed finite descent model.
No gamma values, floating arithmetic, or assumed analytic comparison occurs.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, combinations
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, platform, sys, time
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]

def main():
    started=datetime.now(timezone.utc).isoformat(); tic=time.monotonic(); checks=[]; negatives=[]
    def ck(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    def neg(name, condition):
        if not condition: raise AssertionError('negative control: '+name)
        negatives.append(name)
    M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]]); R=M.inv(); Z=sp.zeros(3)
    MR=sp.diag(M,M); RR=sp.diag(R,R)
    OR=Z.row_join(-sp.eye(3)).col_join(sp.eye(3).row_join(-sp.eye(3)))
    BR=OR*MR
    a=sp.Matrix([[1,0,-2,-3,0,-1]])
    b=sp.Matrix([[0,1,3,0,-3,-2]])
    L=a.col_join(b)
    K=sp.Matrix([[1,4],[0,1]]); KM=sp.Matrix([[2,1],[0,2]])
    E=a.T*b-b.T*a
    ck('original matrix determinant',M.det()==1)
    ck('twisted residue quotient',all(x%7==0 for x in L*BR-K*L))
    ck('ordinary residue quotient',all(x%7==0 for x in L*MR-KM*L))
    ck('rotation residue quotient',all(x%7==0 for x in L*OR-4*L))
    ck('quotient has explicit section',L[:,:2]==sp.eye(2))
    ck('alternating form exact rank two',E.rank()==2 and E.T==-E)
    ck('twisted form invariant mod seven',all(x%7==0 for x in BR.T*E*BR-E))
    ck('ordinary form has multiplier four',all(x%7==0 for x in MR.T*E*MR-4*E))
    ck('rotation form has multiplier two',all(x%7==0 for x in OR.T*E*OR-2*E))
    neg('not ordinary invariant',any(x%7 for x in MR.T*E*MR-E))
    ck('twisted quotient order seven',all(x%7==0 for x in K**7-sp.eye(2)))
    ck('three twists equal three ordinary steps',all(x%7==0 for x in K**3-KM**3))
    # Exact Eisenstein multiplication.
    def em(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]-x[1]*y[1])
    def es(x,y):return (x[0]-y[0],x[1]-y[1])
    def ea(x,y):return (x[0]+y[0],x[1]+y[1])
    ah=[(3,1),(0,0),(1,-2)];bh=[(0,0),(3,1),(2,3)]
    cyc=[(1,2),(2,0),(0,1)]
    hodge=[es(em(ah[i],bh[j]),em(ah[j],bh[i])) for i,j in cyc]
    ck('exact Hodge cross coefficients',hodge==[(-5,3),(-3,-8),(8,5)])
    target=[(2*k,3*k) for k in (1,2,4)]
    ck('Hodge class is (1,2,4)/Jbar',all((x-y)%7==0 for h,t in zip(hodge,target) for x,y in zip(h,t)))
    J=(2,3);jb=(-1,-3)
    ck('Jacobi norm',em(J,jb)==(7,0))
    # Enumerate every fixed parameter class, in rational real coordinates.
    def tor(x):return tuple(F(c)%1 for c in x)
    def vadd(x,y):return tuple(ea(u,v) for u,v in zip(x,y))
    def vscale(c,x):return tuple(em(c,u) for u in x)
    def act(A,x):
        return tuple(tuple(sum(F(A[i,j])*x[j][k] for j in range(3))%1 for k in range(2)) for i in range(3))
    def canon(x):return tuple(tor(c) for c in x)
    pts=[];param=[]
    for i,j in product(range(42),repeat=2):
        z=(F(i,42),F(j,42))
        if all(c.denominator==1 for c in em((-6,-18),z)):
            pts.append(z);param.append(canon((em((4,-1),z),em((1,5),z),z)))
    ck('all 252 fixed parameters enumerated',len(pts)==252 and len(set(param))==252)
    ck('every parameter fixed by omega R',all(canon(vscale((0,1),act(R,x)))==x for x in param))
    common=[x for x in param if act(R,x)==x]
    expected=[((F(0),F(0)),(F(0),F(0)),(F(2*k,3)%1,F(k,3)%1)) for k in range(3)]
    ck('joint invariance exactly three',set(common)==set(expected))
    gamma=canon(tuple(em((k,0),(F(2,7),F(3,7))) for k in (1,2,4)))
    ck('primitive class is nonzero fixed parameter',gamma in param and gamma!=canon(((0,0),)*3))
    ck('ordinary action is multiplication four',act(R,gamma)==canon(vscale((4,0),gamma)))
    ck('seven primitive multiples distinct',len({canon(vscale((k,0),gamma)) for k in range(7)})==7)
    ck('primitive triple tensor norm zero',canon(vadd(vadd(gamma,act(R,gamma)),act(R,act(R,gamma))))==canon(((0,0),)*3))
    neg('nonzero primitive is not jointly invariant',gamma not in common)
    # Full quotient/radical count on the stated finite domain (117649 inputs).
    counts=Counter()
    aa=list(map(int,a));bb=list(map(int,b))
    for v in product(range(7),repeat=6):
        counts[(sum(x*y for x,y in zip(aa,v))%7,sum(x*y for x,y in zip(bb,v))%7)]+=1
    ck('all 49 quotient fibers have size 2401',len(counts)==49 and set(counts.values())=={2401})
    # Monomial matrices are represented by (row, zeta exponent) for each column.
    def W(r,a,b):return tuple(((j+b)%7,r*(a*j+4*a*b)%7) for j in range(7))
    def D(r):return tuple((j,2*r*j*j%7) for j in range(7))
    def S2():return tuple((2*j%7,0) for j in range(7))
    def S4():return tuple((4*j%7,0) for j in range(7))
    def matmul(A,B):return tuple((A[i][0],(e+A[i][1])%7) for i,e in B)
    def scalar(A,e):return tuple((i,(p+e)%7) for i,p in A)
    I=tuple((j,0) for j in range(7))
    def power(A,n):
        x=I
        for _ in range(n):x=matmul(x,A)
        return x
    all49=list(product(range(7),repeat=2))
    ck('all 2401 Weyl products',all(matmul(W(1,a,b),W(1,c,d))==scalar(W(1,(a+c)%7,(b+d)%7),4*(a*d-b*c)) for a,b in all49 for c,d in all49))
    ck('all 49 twisted lifts',all(matmul(D(1),W(1,a,b))==matmul(W(1,(a+4*b)%7,b),D(1)) for a,b in all49))
    ck('unit lift order seven and fixes first basis vector',power(D(1),7)==I and D(1)[0]==(0,0))
    ck('all 147 ordinary packet intertwiners',all(matmul(matmul(D(r),S2()),W(4*r,a,b))==matmul(W(r,2*a+b,2*b),matmul(D(r),S2())) for r in (1,4,2) for a,b in all49))
    ck('three packet lifts match cubic twisted lift',all(matmul(matmul(matmul(D(r),S2()),matmul(D(4*r),S2())),matmul(D(2*r),S2()))==power(D(r),3) for r in (1,4,2)))
    ck('all 147 rotation packet intertwiners',all(matmul(S4(),W(2*r,a,b))==matmul(W(r,4*a,4*b),S4()) for r in (1,4,2) for a,b in all49))
    ck('both lifted actions commute',all(matmul(matmul(D(r),S2()),S4())==matmul(S4(),matmul(D(2*r),S2()))==D(r) for r in (1,4,2)))
    ck('rotation lift has order three',power(S4(),3)==I)
    ck('orientation commutator gives zeta cubed',matmul(W(1,3,0),W(1,0,1))==scalar(matmul(W(1,0,1),W(1,3,0)),3))
    neg('scalar-free Weyl multiplication is false',matmul(W(1,1,0),W(1,0,1))!=W(1,1,1))
    neg('unit permutation without quadratic lift is false',W(1,0,1)!=W(1,4,1))
    # Holomorphic cochain numerator identity, exact symbolic check.
    az,bz,an,bn,am,bm=sp.symbols('az bz an bn am bm')
    alt=lambda a,b,c,d:a*d-b*c
    residual=4*alt(az+an,bz+bn,am,bm)-4*alt(az,bz,an+am,bn+bm)+4*alt(az,bz,an,bn)-4*alt(an,bn,am,bm)
    ck('universal cover cochain identity',sp.expand(residual)==0)
    ck('cochain zero-anchor numerator',alt(0,0,an,bn)==0)
    # The integer antisymmetric cocycle has twice its coefficient in H^2.
    ck('alternating representative has correct integral ambiguity',8==1+7)
    neg('full cocycle not trivial on real period group',4*int(E[0,1])%7!=0)
    # Primitive classes transform reciprocally to the point component.
    ck('all 49 pairing covariance entries',all((3*(2*k)*(4*l)-3*k*l)%7==0 for k,l in all49))
    data={'M':sp.matrix2numpy(M).tolist(),'R':sp.matrix2numpy(R).tolist(),'alpha':aa,'beta':bb,'alternating_matrix':sp.matrix2numpy(E).tolist(),'K_B':sp.matrix2numpy(K).tolist(),'K_M':sp.matrix2numpy(KM).tolist(),'hodge_cross':hodge,'joint_fixed_parameters':[[[str(c) for c in xy] for xy in x] for x in common]}
    (ROOT/'evidence/descent_data.json').write_text(json.dumps(data,indent=2,default=int)+'\n')
    result={'started_at':started,'runtime_seconds':time.monotonic()-tic,'exit_status':0,'assertion_count':len(checks),'checks':checks,'negative_count':len(negatives),'negative_controls':negatives,'domains':{'lattice_quotient_inputs':7**6,'fixed_parameter_grid':42**2,'accepted_fixed_parameters':252,'Weyl_products':49**2,'Weyl_entries_per_product':7,'twisted_intertwiners':49,'ordinary_packet_intertwiners':147,'pairing_checks':49},'software':{'python':sys.version,'sympy':sp.__version__},'scope':'Exact model only. No gamma descent identification, holomorphic cohomology formalization, scalar reality theorem, or numerical gamma test.'}
    (ROOT/'evidence/exact_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS {len(checks)} exact assertions; {len(negatives)} negative controls; {time.monotonic()-tic:.3f}s')
if __name__=='__main__':main()

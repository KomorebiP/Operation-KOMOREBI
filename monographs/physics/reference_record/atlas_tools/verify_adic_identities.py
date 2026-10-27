#!/usr/bin/env python3
"""Small exact editorial assertions; no archived scripts executed, no Lean run."""
from __future__ import annotations
import argparse
from fractions import Fraction
from math import factorial
from pathlib import Path
import json
import sympy as s


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', default='evidence/adic/identity_checks_final/results.json')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    checks=[]
    def add(name, ok, detail):
        checks.append({'name':name,'status':'passed' if ok else 'failed','detail':detail})
    projectors=True;ranks=True;nesting=True
    for p in (2,3):
        H=3;n=p**H
        E=[s.Matrix(n,n,lambda x,y:s.Rational(1,p**(H-r)) if (x-y)%p**r==0 else 0) for r in range(H+1)]
        D=[E[0]]+[E[r]-E[r-1] for r in range(1,H+1)]
        for r in range(H+1):
            ranks &= s.trace(D[r])==(1 if r==0 else (p-1)*p**(r-1))
            projectors &= D[r]*D[r]==D[r]
            for t in range(H+1):
                nesting &= E[r]*E[t]==E[min(r,t)]
                projectors &= D[r]*D[t]==(D[r] if r==t else s.zeros(n))
    add('exact rational averaging and detail projector algebra',bool(projectors and nesting),{'p':[2,3],'H':3,'largest_matrix':27})
    add('detail ranks from exact traces',bool(ranks),{'rank0':1,'rank_r':'(p-1)*p^(r-1)'})
    gram=True
    for p in (2,3,5):
        B=s.Matrix(3*p,3,lambda x,y:int(x%3==y))
        gram &= B.T*B==p*s.eye(3)
    add('normalized incidence Gram identity',bool(gram),{'p':[2,3,5],'coarse_dimension':3,'identity':'B^T B=p I; I=B/sqrt(p)'})
    phase=True;missing_wrong=False;count=0
    for a,b in ((2,3),(3,5),(4,9)):
        N=a*b
        for n in range(N):
            for k in range(N):
                ka=k*pow(b,-1,a)%a;kb=k*pow(a,-1,b)%b
                phase &= (b*ka*(n%a)+a*kb*(n%b)-k*n)%N==0
                missing_wrong |= (b*(k%a)*(n%a)+a*(k%b)*(n%b)-k*n)%N != 0
                count+=1
    add('CRT dual output Fourier phase congruence',phase,{'moduli':[[2,3],[3,5],[4,9]],'all_basis_pairs':count,'arithmetic':'integer congruences'})
    add('same input and output CRT map negative control detected',missing_wrong,{'meaning':'omitting dual inverses fails at some enumerated pair'})
    shift_ok=True
    for p in (2,3,5):
        n=3;N=n*p;B=s.Matrix(N,n,lambda x,y:int(x%n==y))
        def shift(m): return s.Matrix(m,m,lambda x,y:int(x==(y+1)%m))
        shift_ok &= shift(N)*B==B*shift(n)
    add('cyclic shift exact incidence intertwining',bool(shift_ok),{'p':[2,3,5],'n':3,'normalized_factor_cancels':True})
    z,l=s.symbols('z l')
    H=s.Matrix([[1,l,0],[l,2,1],[0,1,3]])
    R=z*s.eye(3)-H
    d=(z-2)*(z-3)-1
    sigma=l*l*(z-3)/d
    cc=(R.inv()[0,0])
    add('rank one Schur resolvent identity',s.cancel(cc-1/(z-1-sigma))==0,{'matrix':[[1,'l',0],['l',2,1],[0,1,3]],'detail_exclusion':'(z-2)(z-3)-1 nonzero','full_exclusion':'det(z I-H) nonzero'})
    sigma_direct=(H.extract([0],[1,2])*(z*s.eye(2)-H.extract([1,2],[1,2])).inv()*H.extract([1,2],[0]))[0,0]
    add('rank one self energy quadratic coupling',s.cancel(sigma_direct-sigma)==0 and s.Poly(s.cancel(sigma_direct/l**2),l).degree()==0,{'self_energy':'l^2 (z-3)/((z-2)(z-3)-1)','uniform_bound_requires':'distance from detail spectrum'})
    add('Schur determinant factorization',s.cancel(R.det()-d*(z-1-sigma))==0,{'regular_domain':True,'cleared_identity_polynomial':True})
    M=s.Matrix([[5,1,0,1],[1,6,2,0],[0,2,7,1],[1,0,1,8]])
    def schur(A,keep):
        drop=[i for i in range(A.rows) if i not in keep]
        return A.extract(keep,keep)-A.extract(keep,drop)*A.extract(drop,drop).inv()*A.extract(drop,keep)
    direct=schur(M,[0]);step=schur(schur(M,[0,1,2]),[0])
    add('nested Schur elimination transitivity',direct==step,{'matrix':[[int(v) for v in row] for row in M.tolist()],'first_eliminate':[3],'second_eliminate':[1,2],'exact_value':str(direct[0,0])})
    grover=[]
    for p in (2,3):
        d0=3;d1=d0+p
        G=s.Rational(2,d1)*s.ones(d1)-s.eye(d1)
        leakage=sum(G[j,0]**2 for j in range(d0,d1))
        grover.append({'p':p,'old_degree':d0,'new_degree':d1,'squared_leakage':str(leakage),'formula':str(s.Rational(4*p,d1*d1))})
    add('Grover depth extension nonzero leakage negative control',all(s.Rational(x['squared_leakage'])==s.Rational(x['formula'])>0 for x in grover),grover)
    factorial_ok=True;num=0
    for N in range(2,8):
        for j in range(N):
            for q in range(9):
                prod=Fraction(factorial(j)*N**(N*q)*factorial(q))
                for r in range(1,N+1):
                    if j+r==N:continue
                    for k in range(q):prod*=Fraction(j+r,N)+k
                factorial_ok &= prod==factorial(N*q+j);num+=1
    add('factorial lane exact rational coefficient factorization',factorial_ok,{'N_min':2,'N_max':7,'all_j':True,'q_min':0,'q_max':8,'coefficient_instances':num})
    A=s.diag(s.Matrix([[1,1],[1,2]]),s.Matrix([[3,0],[0,4]]))
    P=s.diag(1,1,0,0);Q=s.eye(4)-P
    poly=s.eye(4)+A+A**2/2+A**3/6
    B=A.copy();B[0,2]=B[2,0]=1
    polyB=s.eye(4)+B+B**2/2+B**3/6
    add('stable packet polynomial preserves reducing block',Q*poly*P==s.zeros(4),{'degree':3,'arithmetic':'rational','packet_rank':2})
    add('off diagonal packet coupling negative control detected',Q*polyB*P!=s.zeros(4),{'coupling':1,'degree':3,'leakage_matrix':str(Q*polyB*P)})
    result={'schema':'physics.adic.exact-checks.v1','contract':'finite exact rational and symbolic identities plus negative controls, not universal proof by testing','fresh_lean_compile':False,'archive_scripts_executed':False,'checks':checks,'counts':{'passed':sum(x['status']=='passed' for x in checks),'failed':sum(x['status']=='failed' for x in checks)}}
    out=root/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts']))
    raise SystemExit(0 if not result['counts']['failed'] else 1)


if __name__=='__main__':main()

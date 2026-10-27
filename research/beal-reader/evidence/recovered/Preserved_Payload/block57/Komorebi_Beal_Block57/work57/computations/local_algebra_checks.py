#!/usr/bin/env python3
"""Exact finite algebra controls for the written Block57 local lemma.
These tests do not replace the universal proof or certify Frey geometry.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path


def need(ok,msg):
    if not ok:raise ValueError(msg)

def add(x,y):return (x[0]+y[0],x[1]+y[1])
def neg(x):return (-x[0],-x[1])
def sub(x,y):return add(x,neg(y))
def mul(x,y):
    a,b=x;c,d=y
    return (a*c+b*d,a*d+b*c+b*d)
def scale(a,x):return (a*x[0],a*x[1])
def mod(x,m):return (x[0]%m,x[1]%m)
def v7(a):
    if a==0:return None
    v=0
    while a%7==0:a//=7;v+=1
    return v
def valuation(x):
    vs=[v7(a) for a in x if a]
    return min(vs) if vs else None

def power(x,e,M):
    out=(1,0)
    while e:
        if e&1:out=mod(mul(out,x),M)
        x=mod(mul(x,x),M);e//=2
    return out

def mm(A,B):return [[add(mul(A[i][0],B[0][j]),mul(A[i][1],B[1][j])) for j in range(2)] for i in range(2)]
def mat_scale(q,A):return [[scale(q,x) for x in row] for row in A]
def determinant(A):return sub(mul(A[0][0],A[1][1]),mul(A[0][1],A[1][0]))
def trace(A):return add(A[0][0],A[1][1])
def Z(x):return (x,0)


def main(output):
    trace_tests=0;accepted=0;separated=0;nonrational_units=0;sharp=0;orders=0
    norms=[11,19,31,169,491,1373**2]
    for n in range(1,7):
        m=n//2+1;M=7**n;free=7**(n-m)
        for a,b in itertools.product(range(free),repeat=2):
            u=(7**m*a,7**m*b);eta=add((1,0),u);inverse=sub((1,0),u)
            need(mod(mul(eta,inverse),M)==(1,0),'square-zero inverse failure')
            j=valuation(u)
            k=0 if j is None else n-j
            need(power(eta,7**k,M)==(1,0),'predicted principal order fails')
            if k:need(power(eta,7**(k-1),M)!=(1,0),'order not exact')
            orders+=1;nonrational_units+=bool(b)
            for Q in norms:
                h=v7(Q-1)
                error=sub(add(scale(Q,eta),inverse),(Q+1,0))
                factor=mul(sub(eta,(1,0)),sub(scale(Q,eta),(1,0)))
                need(mod(mul(error,eta),M)==mod(factor,M),'quadratic factor identity failed')
                condition=mod(error,M)==(0,0)
                predicted=(j is None or j+h>=n)
                need(condition==predicted,'toric Frobenius precision equivalence failed')
                trace_tests+=1
                if condition:
                    accepted+=1;need(k<=h,'local Frobenius order exceeds 7^h')
                    if h==0:
                        separated+=1;need(mod(eta,M)==(1,0),'separated character was nontrivial')
                    if k and k==h:sharp+=1
    # Entire principal residue family mod343 (not just half precision), at every
    # separated norm residue Q mod49. Checks the stronger unit-factor argument.
    full_principal_tests=0
    for a,b in itertools.product(range(49),repeat=2):
        eta=(1+7*a,7*b);M=343
        for Q in range(1,49):
            if Q%7 in (0,1):continue
            factor=mul(sub(eta,(1,0)),sub(scale(Q,eta),(1,0)))
            need((mod(factor,M)==(0,0))==(a==b==0),'separated root uniqueness failed')
            full_principal_tests+=1
    # Same-basis exact toric matrices; no division or floating-point operations.
    mats=0;nonrational_mats=0
    units=[(a,b) for a in range(1,4) for b in range(3) if (a,b)!=(0,0)]
    for n,t,Q,u in itertools.product(range(1,7),range(1,4),(11,19,31),units):
        y=scale(7**n,u);b=(2,1);mu=(7**t,0);one=(1,0)
        N=[[neg(mul(mu,y)),mu],[neg(mul(mu,mul(y,y))),mul(mu,y)]]
        # P diag(Q,1) P^-1, where P=[[1,b],[y,1+yb]] has determinant1.
        p=scale(Q-1,add(one,mul(y,b)));r=scale(-(Q-1),b)
        F=[[add(one,p),r],[mul(y,p),add(one,mul(y,r))]]
        zero=[[(0,0),(0,0)],[(0,0),(0,0)]]
        need(mm(N,N)==zero,'N not nilpotent')
        need(mm(F,N)==mat_scale(Q,N) and mm(N,F)==N,'toric identities failed')
        need(trace(F)==(Q+1,0) and determinant(F)==(Q,0),'toric trace/determinant failed')
        need(mod(N[1][0],7**n)==(0,0) and mod(F[1][0],7**n)==(0,0),'wrong lattice depth')
        need(mod(F[1][1],7**n)==(1,0) and mod(N[1][1],7**n)==(0,0),'separated diagonals not trivial')
        mats+=1;nonrational_mats+=any(v[1] for row in F+N for v in row)
    # Sharp negative control: h=1 does NOT force full local triviality.
    n=3;Q=29
    N=[[Z(-343),Z(7)],[Z(-16807),Z(343)]]
    F=[[Z(-20),Z(1)],[Z(-1029),Z(50)]]
    need(mm(N,N)==[[Z(0),Z(0)],[Z(0),Z(0)]],'control N^2')
    need(mm(F,N)==mat_scale(Q,N) and mm(N,F)==N,'control toric identities')
    need(trace(F)==Z(30) and determinant(F)==Z(29),'control trace/determinant')
    need(valuation(N[1][0])==5 and valuation(F[1][0])==3,'control lower-depth valuations')
    need(valuation(sub(F[1][1],Z(1)))==2,'control global half precision')
    etaF=pow(50,-1,343)
    need(etaF==295 and pow(etaF,7,343)==1 and etaF!=1,'control nontrivial order')
    need((-343)%343==0 and 343%343==0,'control should be inertia-trivial')
    # Algebraic norms show the six generators are primes of the stated norms.
    norm_controls=[]
    for (a,b),q in [((3,1),11),((4,-1),11),((4,1),19),((5,-1),19),((5,2),31),((7,-2),31)]:
        need(a*a+a*b-b*b==q,'incorrect ideal generator norm')
        norm_controls.append({'phi_coefficients':[a,b],'norm':q})
    result={'schema':'komorebi.beal.block57.algebra.v1','status':'PASS',
       'arithmetic':'exact Z[phi], phi^2=phi+1, residue rings modulo powers of seven',
       'half_precision_depths':[1,2,3,4,5,6],'norms_tested':norms,
       'principal_units_tested':orders,'nonrational_principal_units':nonrational_units,
       'trace_condition_tests':trace_tests,'toric_trace_congruences_accepted':accepted,
       'separated_accepted_cases':separated,'sharp_positive_local_orders':sharp,
       'all_principal_mod343_separated_tests':full_principal_tests,
       'same_basis_exact_matrix_cases':mats,'nonrational_matrix_cases':nonrational_mats,
       'principal_prime_norm_controls':norm_controls,
       'h1_nontrivial_local_control':{'n':3,'Q':29,'N':[[-343,7],[-16807,343]],
         'F':[[-20,1],[-1029,50]],'eta_F_mod343':etaF,'eta_inertia_trivial':True,
         'meaning':'Exact local model, not a global Frey realization. h=0 may not be replaced by h>=0.'},
       'nonclaims':['Finite matrix tests do not prove the universal lemma','No arithmetic solution or Lean proof']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','trace_condition_tests','all_principal_mod343_separated_tests','same_basis_exact_matrix_cases','nonrational_matrix_cases')},sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    main(ap.parse_args().output)

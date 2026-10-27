#!/usr/bin/env python3
"""Deterministic finite controls, not universal proofs or a verified Python implementation."""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import combinations
import json, random
from hilbert_certificate import (Matrix,add,scale,transpose,inverse,construct,evaluate,norm_sq,
                                column_basis,positive_semidefinite,run_document)

checks=0; negatives=0

def check(p:bool)->None:
    global checks
    checks+=1
    if not p: raise AssertionError(f'Assertion {checks} failed.')

def reject(f)->None:
    global negatives
    try:f()
    except (ValueError,TypeError,KeyError,ArithmeticError):negatives+=1;return
    raise AssertionError('Invalid control accepted.')

def determinant(a:Matrix)->Q:
    r=[list(row) for row in a.rows]; ans=Q(1)
    for k in range(a.ncols):
        p=next((i for i in range(k,len(r)) if r[i][k]),None)
        if p is None:return Q(0)
        if p!=k:r[p],r[k]=r[k],r[p];ans=-ans
        pivot=r[k][k];ans*=pivot
        for i in range(k+1,len(r)):
            f=r[i][k]/pivot
            for j in range(k+1,len(r)):r[i][j]-=f*r[k][j]
    return ans

def principal_minor_psd(a:Matrix)->bool:
    return all(determinant(Matrix(tuple(tuple(a.rows[i][j] for j in ix) for i in ix),len(ix)))>=0
      for k in range(a.nrows+1) for ix in combinations(range(a.nrows),k))

rng=random.Random(20260913)
systems=0; vectors=0
for n in range(7):
 for trial in range(6):
    r=rng.randrange(n+1); h=rng.randrange(n-r+1); d=n-r-h
    s=Matrix.eye(n)
    for _ in range(2*n):
        if n<2:break
        i,j=rng.sample(range(n),2); t=Matrix.eye(n)
        rows=[list(row) for row in t.rows]; rows[i][j]=Q(rng.choice([-2,-1,1,2]));s=Matrix(tuple(map(tuple,rows)),n)@s
    sinv=inverse(s)
    base=Matrix(tuple(tuple(row[j] for j in range(r)) for row in s.rows),r)
    a=Matrix(tuple(row+((row[0] if r else Q(0)),) for row in base.rows),r+1)
    dr=sinv.rows[n-d:] if d else ()
    delta=Matrix(dr+((dr[0],) if d else ()),n)
    cert=construct(a,delta)
    systems+=1
    pr,pk,po,pi=(cert[k] for k in ('realized_projector','kernel_projector','obstruction_projector','inconsistency_projector'))
    for p in (pr,pk,po,pi):
        check(p@p==p);check(transpose(p)==p)
    for p,q in ((pr,po),(pr,pi),(po,pi)):
        check(p@q==Matrix.zero(n,n));check(q@p==Matrix.zero(n,n))
    check(add(add(pr,po),pi)==Matrix.eye(n))
    check(delta@pr==Matrix.zero(delta.nrows,n));check(delta@po==Matrix.zero(delta.nrows,n))
    check(cert['ranks']=={'realized':r,'obstruction':h,'inconsistency':d})
    check(positive_semidefinite(cert['psd_witness']))
    if n<=4:check(principal_minor_psd(cert['psd_witness']))
    new_basis=Matrix(tuple(tuple(row[j] for j in range(r+h)) for row in s.rows),r+h)
    refined=construct(new_basis,delta)
    check(refined['inconsistency_projector']==pi)
    for _ in range(8):
        v=Matrix.parse([[rng.randint(-4,4)] for _ in range(n)],1)
        e=evaluate(cert,v); e1=evaluate(refined,v);vectors+=1
        check(e['error_squared']==e['obstruction_squared']+e['inconsistency_squared'])
        check(e['error_squared']<=e['bound_squared'])
        for p,q in ((e['realized'],e['obstruction']),(e['realized'],e['inconsistency']),(e['obstruction'],e['inconsistency'])):
            check((transpose(p)@q)==Matrix.zero(1,1))
        check(norm_sq(v)==norm_sq(e['realized'])+e['obstruction_squared']+e['inconsistency_squared'])
        w=Matrix.parse([[rng.randint(-4,4)] for _ in range(n)],1)
        for p in (pr,po,pi):check(norm_sq(p@add(v,w,Q(-1)))<=norm_sq(add(v,w,Q(-1))))
        shift=pr@w
        check(po@add(v,shift)==po@v)
        check(pi@add(v,pk@w)==pi@v)
        gain=add(e1['realized'],e['realized'],Q(-1))
        check(e['error_squared']==e1['error_squared']+norm_sq(gain))
        check(e['obstruction_squared']==e1['obstruction_squared']+norm_sq(gain))
        # Arbitrary global candidates obey the stronger Pythagorean identity.
        z=Matrix.parse([[rng.randint(-3,3)] for _ in range(a.ncols)],1)
        check(norm_sq(add(v,a@z,Q(-1)))==e['error_squared']+norm_sq(add(e['realized'],a@z,Q(-1))))
    if d:
        reject(lambda:construct(a,delta,Q(10**9)))
    check(construct(a,delta,cert['sigma_squared']/2)['sigma_squared']==cert['sigma_squared']/2)

# Audit PSD by an independent all-principal-minors criterion.
psd_cases=0
for n in range(5):
 for _ in range(20):
    m=Matrix.parse([[rng.randint(-2,2) for _ in range(n)] for _ in range(n)],n)
    sym=add(m,transpose(m));check(positive_semidefinite(sym)==principal_minor_psd(sym));psd_cases+=1

sample={'schema_version':1,'coefficient_domain':'Q','local_dimension':3,'global_dimension':1,
        'residual_dimension':1,'A':[[1],[0],[0]],'delta':[[0,0,2]],'local_vector':[3,4,5]}
out=run_document(sample)
check(out['evaluation']['error_squared']=='41');check(out['evaluation']['bound_squared']=='41')
check(out['evaluation']['obstruction_squared']=='16');check(out['evaluation']['inconsistency_squared']=='25')
check(out['certificate']['sigma_squared']=='4')
for s in (Q(1),Q(1,2),Q(1,1000)):
    c=construct(Matrix.zero(1,1),Matrix.parse([[s]],1),s*s)
    e=evaluate(c,Matrix.parse([[1]],1));check(e['error_squared']==1);check(e['bound_squared']==1)
check(run_document({**sample,'local_vector':[3,4,0]})['evaluation']['residual_squared']=='0')
check(run_document({**sample,'local_vector':[3,4,0]})['evaluation']['error_squared']=='16')
for patch in ({'schema_version':2},{'coefficient_domain':'R'},{'local_dimension':-1},
 {'local_dimension':17},{'local_dimension':True},{'global_dimension':2},{'residual_dimension':2},
 {'local_vector':[1,2]},{'local_vector':[1.0,2,3]},{'A':[[1],[True],[0]]},
 {'delta':[[1,0,2]]},{'delta':[[0,2]]},{'sigma_squared':0},{'sigma_squared':-1},
 {'sigma_squared':5}):
    reject(lambda patch=patch:run_document({**sample,**patch}))
reject(lambda:inverse(Matrix.zero(2,2)))
reject(lambda:evaluate(construct(Matrix.zero(1,1),Matrix.eye(1)),Matrix.zero(2,1)))
print(json.dumps({'passed':True,'seed':20260913,'systems':systems,'local_dimensions':[0,6],
  'vectors':vectors,'exact_assertions':checks,'negative_controls_rejected':negatives,
  'independent_psd_comparisons':psd_cases,'arithmetic':'fractions.Fraction',
  'boundary':'Finite Euclidean rational controls; Python and JSON parsing are not formally verified.'},indent=2))

#!/usr/bin/env python3
"""Deterministic exact-rational controls for minimum-norm reconstruction.

Finite tests do not prove the universal Lean statements or the Python parser.
Uses a second rank-factorization construction, and SymPy pinv on a small subset.
"""
from __future__ import annotations
import copy,json,random
from fractions import Fraction as Q
from pathlib import Path
from observable_model import Matrix
from hilbert_certificate import (transpose,add,scale,inverse,column_basis,kernel_basis,
    projector_from_basis,norm_sq,positive_semidefinite)
from reconstruction_certificate import construct,evaluate,run_document,validate_reconstruction

COUNT=0;NEG=0;INDEPENDENT=0

def check(b:bool,message:str)->None:
    global COUNT
    COUNT+=1
    if not b:raise AssertionError(message)

def reject(f)->None:
    global NEG
    try:f()
    except (ValueError,TypeError,KeyError,ArithmeticError):NEG+=1;return
    raise AssertionError('Invalid input was accepted.')

def random_matrix(rng,n,g):
    return Matrix(tuple(tuple(Q(rng.randint(-3,3)) for _ in range(g)) for _ in range(n)),g)

def independent_inverse(a):
    """Full-rank factorization A=F*C; independently invert both factors."""
    f=column_basis(a);ft=transpose(f)
    fleft=inverse(ft@f)@ft
    c=fleft@a;ct=transpose(c)
    return ct@inverse(c@ct)@fleft

def main():
    global INDEPENDENT
    rng=random.Random(20260913);systems=0;vectors=0
    for n in range(7):
      for gdim in range(7):
        a=random_matrix(rng,n,gdim)
        if (n+gdim)%4==0:a=Matrix.zero(n,gdim)
        elif gdim>1 and (n+gdim)%2==0:
            a=Matrix(tuple(row[:-1]+(row[0],) for row in a.rows),gdim)
        c=construct(a);systems+=1
        b,pr,ps,pk=(c[k] for k in ['recovery','image_projector','identifiable_projector','source_kernel_projector'])
        check(b==independent_inverse(a),'Independent rank-factorization mismatch.');INDEPENDENT+=1
        if 0<n<=4 and 0<gdim<=4:
            import sympy as sp
            sa=sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in a.rows])
            sb=sa.pinv()
            qb=Matrix(tuple(tuple(Q(int(sb[i,j].p),int(sb[i,j].q)) for j in range(n)) for i in range(gdim)),n)
            check(b==qb,'SymPy exact pseudoinverse mismatch.');INDEPENDENT+=1
        for val,msg in [(a@b@a==a,'ABA'),(b@a@b==b,'BAB'),(pr@pr==pr,'P image'),
                        (ps@ps==ps,'P source'),(pk@pk==pk,'P kernel'),
                        (transpose(pr)==pr,'selfadjoint image'),(transpose(ps)==ps,'selfadjoint source'),
                        (a@pk==Matrix.zero(n,gdim),'kernel killed'),
                        (b@add(Matrix.eye(n),pr,Q(-1))==Matrix.zero(gdim,n),'residual killed'),
                        (positive_semidefinite(c['source_psd_witness']),'PSD source')]:check(val,msg)
        # A compatibility test that need not detect the whole nonrealizable complement.
        kd=kernel_basis(transpose(a));dd=transpose(kd)
        d=Matrix(dd.rows[:len(dd.rows)//2],n)
        check(d@a==Matrix.zero(d.nrows,gdim),'chain')
        compatible=projector_from_basis(kernel_basis(d))
        obs=add(compatible,pr,Q(-1));inc=add(Matrix.eye(n),compatible,Q(-1))
        check(b@obs==Matrix.zero(gdim,n),'obstruction ignored')
        check(b@inc==Matrix.zero(gdim,n),'inconsistency ignored')
        for _ in range(7):
            v=random_matrix(rng,n,1);x=random_matrix(rng,gdim,1);e=random_matrix(rng,n,1)
            rec=b@v;k=pk@x;candidate=add(rec,k);err=add(v,a@rec,Q(-1));vectors+=1
            check(norm_sq(candidate)==norm_sq(rec)+norm_sq(k),'source Pythagoras')
            check(a@candidate==a@rec,'same best image')
            check(norm_sq(rec)<=norm_sq(candidate),'minimum norm')
            check(norm_sq(add(v,a@x,Q(-1)))==norm_sq(err)+norm_sq(a@add(x,rec,Q(-1))), 'fitting Pythagoras')
            check(norm_sq(add(b@add(a@x,e),x,Q(-1)))==norm_sq(b@e)+norm_sq(pk@x),'noise and ambiguity')
            check(norm_sq(b@e)<=norm_sq(e)/c['alpha_squared'],'source noise bound')
            check(norm_sq(b@e)<=norm_sq(pr@e)/c['alpha_squared'],'projected noise bound')
            check(norm_sq(rec)<=norm_sq(v)/c['alpha_squared'],'source norm bound')
            check(b@add(v,obs@e)==rec,'obstruction noise ignored')
            check(b@add(v,inc@e)==rec,'inconsistency noise ignored')
            ev=evaluate(c,v,x)
            check(ev['candidate']['source_error_squared']<=ev['candidate']['source_error_bound_squared'],'candidate bound')
            check(norm_sq(add(v,a@x,Q(-1)))==norm_sq(obs@v)+norm_sq(inc@v)+norm_sq(a@add(x,rec,Q(-1))),'three-term error')
        if n and gdim:
            badrows=[list(row) for row in b.rows];badrows[0][0]+=1
            reject(lambda:validate_reconstruction(a,Matrix(tuple(tuple(row) for row in badrows),n),c['alpha_squared']))
    path=Path(__file__).resolve().parents[1]/'examples/reconstruction_input.json'
    doc=json.loads(path.read_text());out=run_document(doc)
    check(out['evaluation']['minimum_norm_source']==[['3/2'],['3/2']],'document source')
    check(out['evaluation']['source_norm_squared']=='9/2','document source norm')
    check(out['evaluation']['candidate']['source_error_squared']=='9/2','candidate ambiguity')
    check(out['local_globalization']['error_squared']=='41','document local error')
    for field,value in [('alpha_squared',0),('alpha_squared',-1),('alpha_squared',3),
                        ('sigma_squared',0),('sigma_squared',5),('global_dimension',17),
                        ('global_dimension',True),('local_dimension',-1),('local_vector',[3,4]),
                        ('candidate_source',[3]),('A',[[1],[0],[0]]),('delta',[[1,0,2]]),
                        ('schema_version',True),('coefficient_domain','R'),('local_vector',[3.1,4,5])]:
        bad=copy.deepcopy(doc);bad[field]=value
        reject(lambda bad=bad:run_document(bad))
    for key in ['A','local_dimension','local_vector']:
        bad=copy.deepcopy(doc);del bad[key];reject(lambda bad=bad:run_document(bad))
    for value in [None,[],0,'bad']:reject(lambda value=value:run_document(value))
    for cval in [Q(1,10),Q(1,100),Q(1,1000)]:
        a=Matrix(((cval,),),1);cert=construct(a,cval*cval);b=cert['recovery']
        check(b@a==Matrix.eye(1),'scalar inverse')
        check(norm_sq(b@a)==1,'small data unit source')
    report={'passed':True,'exact_assertions':COUNT,'systems':systems,'vectors':vectors,
            'independent_comparisons':INDEPENDENT,'negative_controls_rejected':NEG,
            'seed':20260913,'arithmetic':'fractions.Fraction','dimensions':[0,6],
            'crosschecks':'49 independent full-rank factorizations; 16 SymPy exact pseudoinverses',
            'scope':'finite exact tests of known rational Euclidean models, not verification of Python or a universal theorem'}
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Finite exact-rational controls for the regularization block.

Seed 20260913; source/data dimensions 0..5; lambda=1/4,1,4; known matrices.
Universal mathematics is proved separately in Lean. Augmented least squares shares
helpers; SymPy uses a separate exact inverse implementation on a small subset.
"""
from __future__ import annotations
import copy,json,random
from fractions import Fraction as Q
from pathlib import Path
from observable_model import Matrix
from hilbert_certificate import (transpose,add,scale,inverse,norm_sq,
    positive_semidefinite,kernel_basis,projector_from_basis)
from reconstruction_certificate import construct as pinv_construct
from tikhonov_certificate import construct,validate,evaluate,objective,run_document,coefficient

COUNT=NEG=ALT=SYM=0

def check(b:bool,msg:str)->None:
    global COUNT
    COUNT+=1
    if not b: raise AssertionError(msg)

def reject(f)->None:
    global NEG
    try:f()
    except (ValueError,TypeError,KeyError,ArithmeticError):NEG+=1;return
    raise AssertionError('Invalid certificate/input accepted.')

def mat(rng,n,g)->Matrix:
    return Matrix(tuple(tuple(Q(rng.randint(-3,3)) for _ in range(g)) for _ in range(n)),g)

def upper(a:Matrix)->Q:
    row=max((sum(map(abs,r),Q(0)) for r in a.rows),default=Q(0))
    col=max((sum((abs(a.rows[i][j]) for i in range(a.nrows)),Q(0)) for j in range(a.ncols)),default=Q(0))
    return max(row,col)

def operator_bound(a:Matrix,k:Q)->bool:
    return positive_semidefinite(add(scale(Matrix.eye(a.ncols),k*k),transpose(a)@a,Q(-1)))

def main():
    global ALT,SYM
    rng=random.Random(20260913);systems=vectors=0
    for n in range(6):
      for gdim in range(6):
        a=mat(rng,n,gdim)
        if (n+gdim)%4==0:a=Matrix.zero(n,gdim)
        elif gdim>1 and (n+gdim)%2==0:a=Matrix(tuple(r[:-1]+(r[0],) for r in a.rows),gdim)
        pk=projector_from_basis(kernel_basis(a));p=add(Matrix.eye(gdim),pk,Q(-1))
        dag=pinv_construct(a); alpha2=dag['alpha_squared']
        for root in [Q(1,2),Q(1),Q(2)]:
          lam=root*root;c=construct(a,lam);r,b,normal=(c[k] for k in ['inverse','recovery','normal']);systems+=1
          check(normal@r==Matrix.eye(gdim),'left inverse')
          check(r@normal==Matrix.eye(gdim),'right inverse')
          check(b==r@transpose(a),'true solution')
          check(operator_bound(r,Q(1)/lam),'inverse norm')
          check(operator_bound(b,Q(1)/(2*root)),'sharp noise norm')
          check(operator_bound(a@b,Q(1)),'fitted contraction')
          check(operator_bound(b@a,Q(1)),'source filter contraction')
          check(pk@b==Matrix.zero(gdim,n),'no artificial kernel component')
          check(b@add(Matrix.eye(n),a@dag['recovery'],Q(-1))==Matrix.zero(gdim,n),'ignore image orthogonal')
          check(add(b@a,scale(r,lam))==Matrix.eye(gdim),'filter decomposition')
          # Alternative construction: least squares on [A; sqrt(lambda) I].
          aug=Matrix(a.rows+scale(Matrix.eye(gdim),root).rows,gdim)
          ap=pinv_construct(aug)['recovery']
          alt=Matrix(tuple(row[:n] for row in ap.rows),n)
          check(alt==b,'augmented least squares');ALT+=1
          if 0<n<=3 and 0<gdim<=3 and root==1:
            import sympy as sp
            sa=sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in a.rows])
            sr=(sa.T*sa+sp.eye(gdim)).inv()*sa.T
            sb=Matrix(tuple(tuple(Q(int(sr[i,j].p),int(sr[i,j].q)) for j in range(n)) for i in range(gdim)),n)
            check(sb==b,'separate SymPy inverse');SYM+=1
          other=mat(rng,n,gdim) if root!=1 else Matrix.zero(n,gdim)
          oc=construct(other,lam);s,d=oc['inverse'],oc['recovery']
          check(add(r,s,Q(-1))==r@add(oc['normal'],normal,Q(-1))@s,'resolvent operator identity')
          delta=add(a,other,Q(-1));eta=upper(delta);ma,mc=upper(a),upper(other)
          ub=eta/lam+(ma+mc)*eta*mc/(lam*lam)
          check(operator_bound(add(b,d,Q(-1)),ub),'rank-change fixed-lambda sensitivity')
          mu=lam+1;rm=construct(a,mu)['inverse']
          check(add(r,rm,Q(-1))==scale(r@rm,mu-lam),'parameter identity')
          check(operator_bound(add(r,rm,Q(-1)),abs(mu-lam)/(lam*mu)),'parameter norm')
          for _ in range(4):
            v=mat(rng,n,1);g=mat(rng,gdim,1);e=mat(rng,n,1);h=mat(rng,gdim,1);x=b@v;vectors+=1
            out=evaluate(c,v,g,g,e)
            check(objective(a,lam,v,x)<=objective(a,lam,v,g),'minimum objective')
            check(objective(a,lam,v,add(x,h))==objective(a,lam,v,x)+norm_sq(a@h)+lam*norm_sq(h),'increment')
            check(4*lam*norm_sq(x)<=norm_sq(v),'sharp squared')
            check(norm_sq(a@x)<=norm_sq(v),'fitted bound')
            check(norm_sq(add(a@x,v,Q(-1)))<=norm_sq(v),'residual contraction')
            check(add(b@(a@g),g,Q(-1))==scale(r@g,-lam),'bias identity')
            check(add(b@add(a@g,e),g,Q(-1))==add(scale(r@g,-lam),b@e),'noise/bias identity')
            pg=p@g;bias=add(b@(a@pg),pg,Q(-1))
            check(norm_sq(bias)<=(lam/(alpha2+lam))**2*norm_sq(pg),'conditioned identifiable bias')
            source=transpose(a)@a@g;sbias=add(b@(a@source),source,Q(-1))
            check(norm_sq(sbias)<=lam*lam*norm_sq(g),'source-condition bias rate')
            check(norm_sq(add(b@add(a@g,e),g,Q(-1)))==norm_sq(add(bias,b@e))+norm_sq(pk@g),'kernel Pythagoras')
            normal_res=add(normal@g,transpose(a)@v,Q(-1))
            check(norm_sq(add(g,x,Q(-1)))<=norm_sq(normal_res)/(lam*lam),'computed-solver certificate')
            check(lam*norm_sq(add(g,x,Q(-1)))<=out['candidate']['objective_gap'],'strong objective growth')
          if gdim and n:
            corrupt=add(b,Matrix(tuple(tuple(Q(i==0 and j==0) for j in range(n)) for i in range(gdim)),n))
            reject(lambda:validate(a,lam,r,corrupt))
    # Universal-bound specializations and intentional cancellation of bias by noise.
    for rr in [Q(1,2**k) for k in range(9)]:
        a=Matrix(((rr,),),1);c=construct(a,rr*rr);b=c['recovery']
        check(b.rows[0][0]==Q(1)/(2*rr),'matched scalar formula')
        check(4*rr*rr*b.rows[0][0]**2==1,'sharpness attained')
        check((b@Matrix(((2*rr,),),1)).rows[0][0]==1,'small data fixed response')
        check((b@(a@Matrix(((Q(1),),),1))).rows[0][0]==Q(1,2),'half-source boundary')
    one=Matrix(((Q(1),),),1);b=construct(one,Q(1))['recovery']
    bias=add(b@one,one,Q(-1));noise=b@one
    check(norm_sq(add(bias,noise))==0 and norm_sq(bias)+norm_sq(noise)==Q(1,2),'bias and noise are not orthogonal')
    doc=json.loads((Path(__file__).resolve().parents[1]/'examples/tikhonov_input.json').read_text())
    result=run_document(doc)
    check(result['evaluation']['regularized_source']==[['1'],['1']],'example recovery')
    check(result['globalization']['total_fit_error_squared']=='42','example fit')
    check(result['evaluation']['objective']=='44','example objective')
    for value in [0,-1,True,0.5,'nan','1/0','1e999999','9'*300,None]:
      bad=copy.deepcopy(doc);bad['lambda']=value;reject(lambda bad=bad:run_document(bad))
    for key,value in [('global_dimension',17),('local_dimension',True),('local_vector',[1]),
        ('candidate_source',[1]),('coefficient_domain','R'),('schema_version',True),
        ('A',[[1,2]]),('delta',[[1,0,0]]),('unrecognized','ignored'),('noise',[1]),
        ('true_source',[1]),('sigma_squared',0),('lambda',{'value':1})]:
      bad=copy.deepcopy(doc);bad[key]=value;reject(lambda bad=bad:run_document(bad))
    bad=copy.deepcopy(doc);del bad['noise'];reject(lambda:run_document(bad))
    for val in [True,1.0,'0.1','nan','1e9','1/0','1/'+'2'*300]:reject(lambda val=val:coefficient(val))
    reject(lambda:construct(Matrix.zero(0,0),Q(0)))
    print(json.dumps({'passed':True,'assertions':COUNT,'systems':systems,'vectors':vectors,
        'negative_controls_rejected':NEG,'augmented_least_squares_comparisons':ALT,
        'sympy_inverse_comparisons':SYM,'seed':20260913,'dimension_range':[0,5],
        'lambda_values':['1/4','1','4'],'extra_scalar_examples':9,
        'domain':'Q; standard Euclidean metrics; no floating arithmetic'},indent=2))
if __name__=='__main__':main()

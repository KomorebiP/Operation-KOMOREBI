#!/usr/bin/env python3
"""Exact finite controls for block 11. No finite run certifies a limit theorem.

Known rational Euclidean matrices, dimensions 0..4, deterministic seed 20260913.
Positive square schedules, dual push-through, kernel retention, and finite noise/
solver budgets. Generic infinite-dimensional conclusions are separate Lean proofs.
"""
from __future__ import annotations
import json, random
from fractions import Fraction as Q
from observable_model import Matrix
from hilbert_certificate import transpose, add, scale, norm_sq, kernel_basis, projector_from_basis, positive_semidefinite
from tikhonov_certificate import construct, validate
from reconstruction_certificate import construct as pinv

COUNT = 0
NEG = 0

def check(p: bool, label: str) -> None:
    global COUNT
    COUNT += 1
    if not p: raise AssertionError(label)

def reject(fn) -> None:
    global NEG
    try: fn()
    except (ValueError, TypeError, ZeroDivisionError): NEG += 1; return
    raise AssertionError('corrupted certificate accepted')

def random_matrix(rng, n: int, m: int) -> Matrix:
    return Matrix(tuple(tuple(Q(rng.randint(-2, 2)) for _ in range(m)) for _ in range(n)), m)

def main() -> None:
    rng = random.Random(20260913)
    systems = vectors = 0
    for n in range(5):
      for d in range(5):
        a = random_matrix(rng,n,d)
        if (n+d)%4==0: a = Matrix.zero(n,d)
        elif d>1 and (n+d)%3==0: a = Matrix(tuple(r[:-1]+(r[0],) for r in a.rows),d)
        at=transpose(a); q=at@a
        p=add(Matrix.eye(d),projector_from_basis(kernel_basis(a)),Q(-1))
        dag=pinv(a);pv=a@dag['recovery']; alpha2=dag['alpha_squared']
        g=random_matrix(rng,d,1); w=random_matrix(rng,d,1)
        en=random_matrix(rng,n,1); h=random_matrix(rng,d,1)
        for k in [1,2,4,8]:
          s=Q(1,k);lam=s*s
          c=construct(a,lam);b=c['recovery'];r=c['inverse'];normal=c['normal']
          bd=construct(at,lam)['recovery'];systems+=1
          check(a@b==bd@at,'actual dual push-through')
          err=add(b@a,p,Q(-1))
          check(positive_semidefinite(add(Matrix.eye(d),transpose(err)@err,Q(-1))),'source error contraction')
          bound=lam/(alpha2+lam)
          check(positive_semidefinite(add(scale(Matrix.eye(d),bound**2),transpose(err)@err,Q(-1))),'closed-range uniform rate')
          check(norm_sq(add(b@(a@(q@w)),q@w,Q(-1))) <= lam*lam*norm_sq(w),'source condition rate')
          e=scale(en,s*s); vectors+=1
          x=b@add(a@g,e); pg=p@g;pk=add(g,pg,Q(-1))
          check(norm_sq(add(x,g,Q(-1)))==norm_sq(add(x,pg,Q(-1)))+norm_sq(pk),'limiting kernel energy retained')
          check(norm_sq(b@e)<=norm_sq(e)/(4*lam),'noise sqrt-lambda budget squared')
          check(norm_sq(a@(b@e))<=norm_sq(e),'fitted noise needs no sqrt scaling')
          candidate=add(x,scale(h,s*s)); res=add(normal@candidate,at@add(a@g,e),Q(-1))
          check(norm_sq(add(candidate,x,Q(-1)))<=norm_sq(res)/(lam*lam),'actual normal residual solver budget')
          check(pv@(a@b)==a@b,'fitted data lie in actual finite range')
          if n and d:
            corrupt=add(b,Matrix(tuple(tuple(Q(1) if i==0 and j==0 else Q(0) for j in range(n)) for i in range(d)),n))
            reject(lambda:validate(a,lam,r,corrupt))
    # Finite sections of the fixed diagonal 1/(j+1) operator on l2.
    # These finite values illustrate, but do not prove, its infinite limit behavior.
    for n in [2,4,8,16,32]:
      lam=Q(1,n*n)
      # A unit vector at index n has filter bias 1/2 at this lambda.
      bias=lam/(Q(1,n*n)+lam)
      check(bias==Q(1,2),'moving unit vector defeats uniform inference')
      # A much deeper coordinate has bias close to one.
      deep=lam/(Q(1,(n*n)**2)+lam)
      check(deep==Q(n*n,n*n+1),'worst direction approaches norm one')
      # Fixed first coordinate improves as lambda shrinks.
      check(lam/(1+lam)==Q(1,n*n+1),'fixed coordinate bias shrinks')
    # Data in a kernel direction remains outside identifiable-source recovery.
    a=Matrix(((Q(1),Q(0)),),2);g=Matrix(((Q(3),),(Q(4),)),1)
    for k in [1,2,4,8,16]:
      c=construct(a,Q(1,k*k));err=add(c['recovery']@(a@g),g,Q(-1))
      check(norm_sq(err)==Q(16)+Q(9,(k*k+1)**2),'exact error tends to kernel squared norm 16')
    print(json.dumps({'passed':True,'assertions':COUNT,'systems':systems,'vectors':vectors,
      'negative_controls_rejected':NEG,'seed':20260913,'source_target_dimensions':'0..4',
      'schedule_denominators':[1,2,4,8],'arithmetic':'fractions.Fraction',
      'non_claim':'Finite tests are not proof of any infinite limit, nor verified Python.'},indent=2))

if __name__=='__main__':main()

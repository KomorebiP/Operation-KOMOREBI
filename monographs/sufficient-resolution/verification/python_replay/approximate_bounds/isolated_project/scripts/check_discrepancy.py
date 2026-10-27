#!/usr/bin/env python3
"""Deterministic finite controls; no finite computation proves a convergence limit."""
from __future__ import annotations
from fractions import Fraction as Q
import json,random
from observable_model import Matrix
from hilbert_certificate import transpose,add,scale,norm_sq
from reconstruction_certificate import construct as pinv
from tikhonov_certificate import construct as tikh
from discrepancy_certificate import select,validate,run_document
COUNT=NEG=0

def check(test,label):
    global COUNT
    COUNT+=1
    if not test:raise AssertionError(label)

def reject(fn):
    global NEG
    try:fn()
    except (ValueError,TypeError,RuntimeError,ZeroDivisionError):NEG+=1;return
    raise AssertionError('Invalid certificate/input was accepted')

def mat(rng,n,d):
    return Matrix(tuple(tuple(Q(rng.randint(-2,2)) for _ in range(d)) for _ in range(n)),d)

def main():
    rng=random.Random(20260914);cases=positive=small=0;max_evals=0
    for n in range(5):
      for d in range(5):
        a=mat(rng,n,d)
        if (n+d)%4==0:a=Matrix.zero(n,d)
        elif d>1 and (n+d)%3==0:a=Matrix(tuple(row[:-1]+(row[0],) for row in a.rows),d)
        g=mat(rng,d,1);noise_direction=mat(rng,n,1)
        norm1=sum((abs(row[0]) for row in noise_direction.rows),Q(0))
        p=pinv(a)['recovery']@a;pg=p@g
        for k in [2,4,8]:
          eta=Q(1,k);e=scale(noise_direction,eta/(1+norm1));v=add(a@g,e)
          c=select(a,v,eta);x=c['source'];cases+=1
          positive+=c['lambda'] is not None;small+=c['lambda'] is None
          max_evals=max(max_evals,c['evaluations'])
          check(norm_sq(e)<=eta**2,'true noise allowance')
          check(c['feasible_residual_squared']<=eta**2,'actual feasibility witness')
          check(norm_sq(x)<=norm_sq(pg),'source norm domination')
          check(norm_sq(add(a@x,a@g,Q(-1)))<=9*eta**2,'true data residual')
          check(p@x==x,'selected source remains identifiable')
          err=add(x,g,Q(-1));ident=add(x,pg,Q(-1));kernel=add(g,pg,Q(-1))
          check(norm_sq(err)==norm_sq(ident)+norm_sq(kernel),'source ambiguity retained')
          if c['lambda'] is not None:
            c2=tikh(a,c['lambda']);check(c2['recovery']@v==x,'validated full-inverse comparison (shared helpers)')
            check(Q(9,4)*eta**2<=c['residual_squared']<=4*eta**2,'strict numerical discrepancy band')
            for first,second in zip(sorted(c['trace'],key=lambda q:q['lambda']),sorted(c['trace'],key=lambda q:q['lambda'])[1:]):
              check(first['residual_squared']<=second['residual_squared'],'residual monotonicity on search trace')
          else:check(norm_sq(v)<=4*eta**2,'small-data condition')
          if d:
            corrupt=add(x,Matrix(tuple((Q(1) if j==0 else Q(0),) for j in range(d)),1))
            reject(lambda:validate(a,v,eta,Q(2),corrupt,c['lambda']))
    # Actual scalar root formula, not a floating root finder.
    for v in [Q(1),Q(2),Q(5)]:
      for ratio in [Q(1,4),Q(1,2),Q(3,4)]:
        rho=v*ratio;lam=rho/(v-rho);a=Matrix.eye(1);x=tikh(a,lam)['recovery']@Matrix(((v,),),1)
        check(x.rows[0][0]==v-rho,'scalar exact source')
        check(norm_sq(add(x,Matrix(((v,),),1),Q(-1)))==rho**2,'scalar exact discrepancy')
    # Underestimated noise in an unattainable direction is rejected.
    reject(lambda:select(Matrix.zero(1,1),Matrix(((Q(1),),),1),Q(1,4)))
    base={'schema_version':1,'coefficient_domain':'Q','global_dimension':1,'local_dimension':1,
          'A':[[1]],'local_vector':[4],'noise_allowance':'1/8'}
    serialized=json.dumps(run_document(base))
    check(json.loads(serialized)['certificate']['branch']=='positive_parameter','JSON output roundtrip')
    for field,bad in [('noise_allowance',0),('noise_allowance',-1),('noise_allowance',0.1),
                      ('upper_multiplier',1),('lower_multiplier',2),('max_steps',True),('max_steps',0),
                      ('max_steps',1),('global_dimension',2),('local_vector',[1,2]),('junk',1)]:
        reject(lambda f=field,b=bad:run_document(dict(base,**{f:b})))
    print(json.dumps({'passed':True,'assertions':COUNT,'systems':cases,'positive_parameter_cases':positive,
       'small_data_cases':small,'negative_controls_rejected':NEG,'largest_search_evaluations':max_evals,
       'seed':20260914,'dimensions':'0..4','noise_allowance_denominators':[2,4,8],
       'arithmetic':'fractions.Fraction','non_claim':'Finite tests are not universal proofs, limit proofs, or formally verified code.'},indent=2))
if __name__=='__main__':main()

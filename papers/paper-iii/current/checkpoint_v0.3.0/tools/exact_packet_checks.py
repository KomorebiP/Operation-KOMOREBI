#!/usr/bin/env python3
"""Independent rational examples and adverse controls for Paper III Section 16.
All arithmetic below is Fraction or exact F2 arithmetic. These bounded checks are
not substituted for Lean proofs. No imports from the production proof project.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
from collections import Counter
from pathlib import Path
import argparse, hashlib, json, random, time

Matrix = tuple[tuple[F, ...], ...]
Vector = tuple[F, ...]

def eye(n:int)->Matrix:
    return tuple(tuple(F(i==j) for j in range(n)) for i in range(n))
def zero(n:int)->Matrix:
    return tuple(tuple(F(0) for _ in range(n)) for _ in range(n))
def mm(a:Matrix,b:Matrix)->Matrix:
    n=len(a)
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(n)),F(0)) for j in range(n)) for i in range(n))
def mv(a:Matrix,x:Vector)->Vector:
    return tuple(sum((v*w for v,w in zip(row,x)),F(0)) for row in a)
def addv(xs:tuple[Vector,...],n:int)->Vector:
    return tuple(sum((x[i] for x in xs),F(0)) for i in range(n))
def addm(xs:tuple[Matrix,...],n:int)->Matrix:
    return tuple(tuple(sum((a[i][j] for a in xs),F(0)) for j in range(n)) for i in range(n))
def inv(a:Matrix)->Matrix:
    n=len(a);r=[list(row)+list(eye(n)[i]) for i,row in enumerate(a)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if r[i][j]),None)
        if pivot is None:raise ValueError('singular matrix')
        r[j],r[pivot]=r[pivot],r[j]
        q=r[j][j];r[j]=[x/q for x in r[j]]
        for i in range(n):
            if i!=j:
                c=r[i][j];r[i]=[x-c*y for x,y in zip(r[i],r[j])]
    return tuple(tuple(row[n:]) for row in r)
def basis(n:int,seed:int)->Matrix:
    rng=random.Random(seed);a=[list(x) for x in eye(n)]
    for _ in range(2*n+1):
        if n<2:break
        i,j=rng.sample(range(n),2);c=rng.choice([-2,-1,1,2])
        a[i]=[x+c*y for x,y in zip(a[i],a[j])]
    return tuple(tuple(x) for x in a)
def packets(n:int,seed:int,grouped:bool=False)->tuple[Matrix,...]:
    b=basis(n,seed);bi=inv(b)
    blocks=[list(range(n))] if grouped else [[i] for i in range(n)]
    result=[]
    for block in blocks:
        d=tuple(tuple(F(i==j and i in block) for j in range(n)) for i in range(n))
        result.append(mm(mm(b,d),bi))
    return tuple(result)
def analyze(ps:tuple[Matrix,...],x:Vector)->tuple[Vector,...]:return tuple(mv(p,x) for p in ps)
def nonlinear(x:Vector)->Vector:
    n=len(x)
    return tuple(x[i]*x[(i+1)%n]+x[i]+F(i+1,3) for i in range(n))
def following(x:Vector)->Vector:return tuple(x[i]**2-x[(i+1)%len(x)] for i in range(len(x)))
def coord(ps,qs,f,z):return analyze(qs,f(addv(z,len(ps[0]) if ps else 0)))
def serialize(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,(list,tuple)):return [serialize(v) for v in x]
    if isinstance(x,dict):return {k:serialize(v) for k,v in x.items()}
    return x

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    counts=Counter();total=0;families=[];start=time.monotonic()
    def check(condition:bool,group:str,detail:str=''):
        nonlocal total
        total+=1;counts[group]+=1
        if not condition:raise AssertionError(f'{group}: {detail}')
    report={'schema':'paper-iii.exact-packet-checks/1','status':'RUNNING','scope':'Bounded exact examples, not universal proof',
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
      for n in range(1,5):
        for seed in range(6):
          ps=packets(n,seed);qs=packets(n,seed+71);rs=packets(n,seed+137)
          pp=packets(n,seed+11,True)+(zero(n),);qq=packets(n,seed+113)
          families.append({'dimension':n,'seed':seed,'P':ps,'basis':basis(n,seed)})
          check(addm(ps,n)==eye(n),'projector_axioms','complete')
          for i,p in enumerate(ps):
            check(mm(p,p)==p,'projector_axioms','idempotent')
            for j,q in enumerate(ps):
              if i!=j:check(mm(p,q)==zero(n),'projector_axioms','orthogonal')
          for raw in product((-1,0,1),repeat=n):
            x=tuple(map(F,raw));z=analyze(ps,x)
            check(addv(z,n)==x,'analysis_synthesis','ambient')
            check(analyze(ps,addv(z,n))==z,'analysis_synthesis','tuple')
            y=coord(ps,qs,nonlinear,z)
            check(addv(y,n)==nonlinear(x),'arbitrary_nonlinear_reconstruction')
            check(coord(qs,rs,following,y)==coord(ps,rs,lambda v:following(nonlinear(v)),z),'composition')
            zprime=analyze(pp,x)
            change_in=analyze(ps,addv(zprime,n))
            changed=analyze(qq,addv(coord(ps,qs,nonlinear,change_in),n))
            check(coord(pp,qq,nonlinear,zprime)==changed,'change_of_coordinates')
            # An independently chosen legal tuple, not a tuple obtained by one analysis call.
            legal=tuple(mv(p,tuple(F(raw[(k+i)%n]+i,2) for k in range(n))) for i,p in enumerate(ps))
            check(analyze(ps,addv(legal,n))==legal,'all_legal_tuple_reconstruction')
            # A genuinely nonlinear bijective shear, with its explicit inverse.
            def shear(v):return v if n<2 else (v[0],v[1]+v[0]**2,*v[2:])
            def unshear(v):return v if n<2 else (v[0],v[1]-v[0]**2,*v[2:])
            check(coord(qs,ps,unshear,coord(ps,qs,shear,z))==z,'transported_inverse')
            def cycle(v):return v if n<2 else (v[1],v[0],*v[2:])
            xn=x;zn=z
            for step in range(7):
                check(zn==analyze(ps,xn),'iterate_conjugacy')
                check((xn==x)==(zn==z),'return_times')
                xn=cycle(xn);zn=coord(ps,ps,cycle,zn)
      check(analyze((),())==(),'zero_module_empty_family')
      check(addv((),0)==(),'zero_module_empty_family')
      p=((F(1),F(0)),(F(0),F(0)));x=(F(3),F(5))
      check(mm(p,p)==p and p!=zero(2),'missing_completeness_control')
      check(addv(analyze((p,),x),2)!=x,'missing_completeness_control')
      # In F2, three identity maps sum to identity and are idempotent, but not orthogonal.
      check(sum([1,1,1])%2==1,'missing_orthogonality_control')
      tuple_in=(1,0,0);tuple_out=tuple(sum(tuple_in)%2 for _ in range(3))
      check(tuple_out!=tuple_in,'missing_orthogonality_control')
      mixed=lambda v:(v[0]*v[1],v[0]**2+v[1])
      x=(F(2),F(3));exact=mixed(x);diagonal=(mixed((x[0],F(0)))[0],mixed((F(0),x[1]))[1])
      check(exact==(F(6),F(7)) and exact!=diagonal,'cross_packet_interaction_control')
      report.update(status='PASS',checks=total,groups=dict(counts),families=serialize(families),
        adverse_examples={'missing_completeness':{'input':serialize((F(3),F(5))),'reconstruction':serialize((F(3),F(0)))},
         'missing_orthogonality_F2':{'idempotents':[1,1,1],'sum_mod2':1,'input':tuple_in,'analysis_after_synthesis':tuple_out},
         'mixed_quadratic':{'input':serialize(x),'exact':serialize(exact),'diagonal_restriction':serialize(diagonal)}})
    except Exception as exc:
      report.update(status='FAIL',checks_attempted=total,groups=dict(counts),error=repr(exc))
    report['elapsed_seconds']=time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report.get(k) for k in ('status','checks','groups','error','elapsed_seconds')}))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

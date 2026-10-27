#!/usr/bin/env python3
"""Exact independent finite checks; universal reductions are in PROOF.md."""
from fractions import Fraction as F
from collections import defaultdict
from itertools import product
from pathlib import Path
from datetime import datetime,timezone
import json,time,sys,sympy as sp
ROOT=Path(__file__).resolve().parents[1]
def main():
 start=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();checks=[]
 def ck(n,b):
  if not bool(b):raise AssertionError(n)
  checks.append(n)
 def pt(a,b=0,c=0):return F(a)%1,F(b)%1,F(c)
 def clean(d):return {k:v for k,v in d.items() if v}
 def add(*terms):
  d=defaultdict(int)
  for coef,ds in terms:
   for p,v in ds.items():d[p]+=coef*v
  return clean(d)
 def push(n,d):
  o=defaultdict(int)
  for (a,b,c),v in d.items():o[pt(n*a,n*b,n*c)]+=v
  return clean(o)
 def trans(d,c):return {pt(a,b,s-c):v for (a,b,s),v in d.items()}
 def charges(d):
  o=defaultdict(int)
  for (a,b,c),v in d.items():o[(a,b,c%1)]+=v
  return clean(o)
 D={pt(0):4,**{pt(F(i,5)):-1 for i in range(1,5)}}
 P=defaultdict(int)
 for (a,b,c),v in D.items():
  for x,y in product(range(2),repeat=2):P[pt((a+x)/2,(b+y)/2,c/2)]+=v
 P=clean(P)
 delta=add((2,D),(-1,P),(-1,trans(P,F(1,2))))
 ck('original kernel has 40 support points',len(delta)==40)
 ck('origin and half orbit charges',charges(delta)[pt(0)]==4 and charges(delta)[pt(0,0,F(1,2))]==-4)
 norm_records=[]
 for n in range(1,25):
  observed=push(n,delta)
  if n%5==0:pred={};class_pred={}
  elif n%2:
   pred=add((2,D),(-1,P),(-1,trans(P,F(n,2))));class_pred=charges(delta)
  else:
   pred=add((-2,D),(-4,trans(D,F(n,2))));class_pred=charges(add((-6,D)))
  ck(f'full divisor norm n={n}',observed==pred)
  ck(f'translation class norm n={n}',charges(observed)==class_pred)
  norm_records.append({'n':n,'support':len(observed),'class':('zero' if n%5==0 else 'same' if n%2 else '-6 theta')})
 primitive=add((6,D),(1,delta));R=add((4,D),(-1,P))
 ck('primitive distribution component is nontrivial',charges(primitive)[pt(0)]==28 and charges(primitive)[pt(0,0,F(1,2))]==-4)
 ck('primitive doubled norm is a boundary',push(2,primitive)==add((4,D),(-4,trans(D,1))))
 ck('norm one rational factor',push(2,R)=={})
 ck('norm one factor is not constant',R!={})
 Q=sp.Matrix([[1,-6],[0,0]]);ck('norm projector idempotent',Q*Q==Q)
 ck('primitive integral basis vector killed',Q*sp.Matrix([6,1])==sp.zeros(2,1))
 ck('two charge matrix injective',sp.Matrix([[4,4],[0,-4]]).det()==-16)
 def mat(n):return sp.zeros(2) if n%5==0 else Q if n%2==0 else sp.eye(2)
 ck('complete residue-ten semigroup',all(mat(a*b)==mat(a)*mat(b) for a,b in product(range(10),repeat=2)))
 a,b,c,d,u,v,w=sp.symbols('a b c d u v w',nonzero=True)
 ck('pointwise kernel decomposition',sp.cancel(u**2/(v*w)-(u**4/v)**2/u**6*v/w)==0)
 W=[a*b/(c*d),a*c/(b*d),a*d/(b*c)]
 ck('three signed channels reconstruct norm-one factor',sp.cancel(sp.prod(W)-a**4/(a*b*c*d))==0)
 ck('Hadamard fourth power reconstruction',sp.cancel(a*b*c*d*sp.prod(W)-a**4)==0)
 ck('bare norm forgets component: negative control',Q*sp.Matrix([6,1])!=sp.Matrix([6,1]))
 ck('smoothing norm not identity: negative control',mat(5)!=sp.eye(2))
 out={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'python':sys.version.split()[0],'sympy':sp.__version__,'count':len(checks),'checks':checks,'norms':norm_records,'scope':'Finite exact divisor/polynomial checks; no gamma arithmetic identity.'}
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS:',len(checks),'exact checks.')
if __name__=='__main__':main()

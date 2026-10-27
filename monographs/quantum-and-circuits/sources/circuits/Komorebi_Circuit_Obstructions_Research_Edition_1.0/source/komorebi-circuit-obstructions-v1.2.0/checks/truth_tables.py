"""Exact finite truth-table profiles. Internal research code, not a stable public API."""
from itertools import combinations
from time import perf_counter

def monomials(n):
 return [sum(1<<i for i in s) for d in range(n+1) for s in combinations(range(n),d)]
def affine_masks(n):
 return [sum((((s&x).bit_count()&1)^b)<<x for x in range(1<<n)) for s in range(1<<n) for b in (0,1)]
def profile(f,n,features=None):
 if f==0:return 0,0
 if features is None:
  mons=monomials(n);features=[sum((x&s==s)<<j for j,s in enumerate(mons)) for x in range(1<<n)]
 pos=[x for x in range(1<<n) if f>>x&1];neg=[x for x in range(1<<n) if not f>>x&1]
 D=0; alpha=None
 for d in range(n+1):
  from math import comb
  D+=comb(n,d);mask=(1<<D)-1;basis={}
  def reduce(v):
   while v:
    p=v.bit_length()-1
    if p not in basis:return v
    v^=basis[p]
   return 0
  for x in neg:
   v=reduce(features[x]&mask)
   if v:basis[v.bit_length()-1]=v
  if alpha is None and len(basis)<D:alpha=d
  if all(reduce(features[x]&mask) for x in pos):return alpha,d
 raise AssertionError

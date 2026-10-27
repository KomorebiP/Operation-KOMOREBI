#!/usr/bin/env python3
"""Orthogonal bounded rank checks and hand-computable primitive benchmarks."""
from __future__ import annotations
import argparse
import importlib.util
import itertools
import json
from pathlib import Path
import sys

def plain_rank(a,p):
 a=[[int(x)%p for x in row] for row in a];rows=len(a);cols=len(a[0]);r=0
 for c in range(cols):
  pivot=next((k for k in range(r,rows) if a[k][c]),None)
  if pivot is None:continue
  a[r],a[pivot]=a[pivot],a[r];iv=pow(a[r][c],-1,p)
  a[r]=[(v*iv)%p for v in a[r]]
  for k in range(r+1,rows):
   q=a[k][c];a[k]=[(x-q*y)%p for x,y in zip(a[k],a[r])]
  r+=1
  if r==rows:break
 return r

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 spec=importlib.util.spec_from_file_location('paper_xii_original_finite',a.source);mod=importlib.util.module_from_spec(spec)
 sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 count=0
 for p in (2,3,5,7):
  for entries in itertools.product(range(p),repeat=4):
   matrix=mod.np.array(entries,dtype=int).reshape((2,2));expected=plain_rank(matrix.tolist(),p)
   actual=mod.rank_mod(matrix,p)
   assert actual==expected,(p,entries,actual,expected);count+=1
  for n in range(1,6):
   assert mod.rank_mod(mod.np.eye(n,dtype=int),p)==n
   assert mod.rank_mod(mod.np.zeros((n,n),dtype=int),p)==0
   assert mod.np.array_equal(mod.matrix_inverse_mod(mod.np.eye(n,dtype=int),p),mod.np.eye(n,dtype=int))
   count+=3
  for n in range(2,6):
   j=mod.jordan_block(n,0,p)
   assert mod.rank_mod(j,p)==n-1
   assert mod.np.array_equal(mod.matrix_power_mod(j,n,p),mod.np.zeros((n,n),dtype=int));count+=2
 assert mod.cyclic_convolution((1,1),(1,1),2)==(0,0);count+=1
 report={'status':'PASS','assertion_count':count,'rank_comparisons':sum(p**4 for p in (2,3,5,7)),
  'coefficient_domain':'Exact prime-field arithmetic in plain Python integers compared with original NumPy modular elimination.',
  'bounds':{'fields':[2,3,5,7],'exhaustive_2x2_matrices':True,'identity_zero_inverse_dimension':[1,5],'nilpotent_jordan_dimension':[2,5]},
  'independence_limit':'Separate implementation using forward elimination and Python lists; shares the standard Gaussian-elimination method, not a theorem prover.',
  'non_claims':['No general theorem is inferred; benchmarks audit these implementation primitives only.']}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0
if __name__=='__main__':sys.exit(main())

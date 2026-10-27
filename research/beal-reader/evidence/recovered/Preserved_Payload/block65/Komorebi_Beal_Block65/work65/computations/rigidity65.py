#!/usr/bin/env python3
"""Exact finite algebra checks for the written coefficient-rigidity proof.
These tests do not prove Kummer theory, Chebotarev or their arithmetic application.
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def add(x,y):return (x%7+y%7)%7+7*((x//7+y//7)%7)
def neg(x):return (-x%7)%7+7*((-(x//7))%7)
def mul(x,y):
 a,b=x%7,x//7;c,d=y%7,y//7
 return (a*c+5*b*d)%7+7*((a*d+b*c)%7)
def power(x,n):
 r=1
 while n:
  if n&1:r=mul(r,x)
  x=mul(x,x);n//=2
 return r
def need(b,m):
 if not b:raise AssertionError(m)
def compatible(u,r,b,x,y,z):
 mid=mul(b,add(mul(r,y),z));edge=mul(b,mul(u,x))
 plus=add(mid,edge);minus=add(mid,neg(edge))
 return plus==minus or power(plus,7)==minus

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 total=first=0;accepted=[]
 for u,r,b in itertools.product(range(1,49),repeat=3):
  total+=1
  if not compatible(u,r,b,1,0,1):continue
  first+=1
  if compatible(u,r,b,1,1,0):accepted.append([u,r,b])
 expected=[[u,r,b] for u in range(7,49,7) for r in range(1,7) for b in range(1,7)]
 need(accepted==expected,'Two-probe classification differs')
 full=0
 for u,r,b in accepted:
  for x,y,z in itertools.product(range(7),repeat=3):
   need(compatible(u,r,b,x,y,z),'Failed full paired identity');full+=1
 # T acts by 3 on the Kummer coordinates and by inverse(3)=5 on beta.
 # (T-5)/(3-5) is the projection onto the former block.
 projections=0
 for xyz in itertools.product(range(7),repeat=3):
  for b in range(49):
   v=list(xyz)+[b];tv=[mul(3,x) for x in xyz]+[mul(5,b)]
   p=[mul(3,add(t,neg(mul(5,x)))) for x,t in zip(v,tv)]
   need(p==list(xyz)+[0],'Eigenprojection identity');projections+=1
 need(compatible(1,1,7,1,0,0),'Lost one-place negative control')
 need(not compatible(1,1,7,1,0,1),'Missing independent-probe obstruction')
 out={'schema':'beal.block65.rigidity_algebra.v1','status':'PASS_FINITE_ALGEBRA',
  'triples_tested':total,'first_probe_survivors':first,'two_probe_survivors':len(accepted),
  'accepted_triples':accepted,'full_coordinate_tests':full,'eigenprojection_vectors':projections,
  'normalized_alpha_directions':[[u,r,1] for u in range(7,49,7) for r in range(1,7)],
  'one_place_control':{'u':1,'r':1,'beta':7,'coordinates':[1,0,0],'products':[7,42],
    'reason':'A single conjugate pair does not force normalized coefficient descent.'},
  'scope':'Finite coefficient algebra only; the group-theoretic independence and Frobenius realization are written proof steps.'}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],total,first,len(accepted),full,projections)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Separate coefficient-field checker. theta^2=theta+1, not w^2=5.
Imports no primary arithmetic. Enumerates all nonzero triples and rechecks projections.
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def plus(a,b):return ((a[0]+b[0])%7,(a[1]+b[1])%7)
def times(a,b):
 x,y=a;u,v=b
 return ((x*u+y*v)%7,(x*v+y*u+y*v)%7)
def negative(a):return((-a[0])%7,(-a[1])%7)
def conjugate(a):return((a[0]+a[1])%7,(-a[1])%7)
def code(a):return (a[0]+4*a[1])%7+7*(4*a[1]%7)
def fromw(x):return((x%7-x//7)%7,2*(x//7)%7)
def need(b,m):
 if not b:raise AssertionError(m)
def pair(u,r,b,x,y,z):
 t=times(b,plus(times(r,(y,0)),(z,0)));e=times(b,times(u,(x,0)))
 a=plus(t,e);c=plus(t,negative(e))
 return a==c or conjugate(a)==c

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 rec=json.loads(args.certificate.read_text());F=list(itertools.product(range(7),repeat=2));nonzero=[v for v in F if v!=(0,0)]
 accepted=[];first=0;full=0
 for u,r,b in itertools.product(nonzero,repeat=3):
  if not pair(u,r,b,1,0,1):continue
  first+=1
  if pair(u,r,b,1,1,0):accepted.append([code(u),code(r),code(b)])
 need(sorted(accepted)==sorted(rec['accepted_triples']),'Changed rigidity classification')
 need(len(accepted)==rec['two_probe_survivors']==216 and first==rec['first_probe_survivors']==1728,'Wrong finite totals')
 for row in accepted:
  u,r,b=map(fromw,row)
  for x,y,z in itertools.product(range(7),repeat=3):
   need(pair(u,r,b,x,y,z),'Conjugacy control failed');full+=1
 need(full==rec['full_coordinate_tests']==74088,'Coordinate coverage mismatch')
 count=0
 for xyz in itertools.product(range(7),repeat=3):
  for b in F:
   v=[(x,0) for x in xyz]+[b];tv=[times((3,0),z) for z in v[:3]]+[times((5,0),b)]
   p=[times((3,0),plus(t,negative(times((5,0),z)))) for z,t in zip(v,tv)]
   need(p==v[:3]+[(0,0)],'Projection mismatch');count+=1
 need(count==rec['eigenprojection_vectors']==16807,'Projection coverage mismatch')
 need(rec['normalized_alpha_directions']==[[u,r,1] for u in range(7,49,7) for r in range(1,7)],'Wrong normalized directions')
 out={'schema':'beal.block65.independent_rigidity.v1','status':'PASS_INDEPENDENT_ALGEBRA',
  'triples':48**3,'first_probe':first,'accepted':len(accepted),'full_coordinate_tests':full,
  'eigenprojection_vectors':count,'primary_arithmetic_imports':False,'field_basis':'theta^2=theta+1',
  'scope':'Finite algebra, not an independent review of arithmetic proof or Chebotarev application.'}
 args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Exact Q(phi) Frobenius identities; finite checks supplement, not replace, the proof."""
from __future__ import annotations
import argparse,json
from itertools import product
from pathlib import Path

Z=(0,0);ONE=(1,0)
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def sub(a,b):return add(a,neg(b))
def mul(a,b):return (a[0]*b[0]+a[1]*b[1],a[0]*b[1]+a[1]*b[0]+a[1]*b[1])
def scale(a,n):return (a[0]*n,a[1]*n)
def invunit(a):
 n=a[0]*a[0]+a[0]*a[1]-a[1]*a[1]
 if abs(n)!=1:raise ValueError('Only exact global units are accepted')
 return ((a[0]+a[1])//n,-a[1]//n)
def divides(a,n):return a[0]%n==0 and a[1]%n==0
def vp(n):
 n=abs(n);v=0
 if not n:raise ValueError('Finite valuation expected')
 while n%7==0:n//=7;v+=1
 return v

def imul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def times(a,n):return [[n*x for x in r] for r in a]
def need(ok,msg):
 if not ok:raise AssertionError(msg)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
 count=nonrat=depth2=tight=0
 units=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1)]
 for n in range(1,5):
  N=7**n
  for Q in [29,71,491,197**2,883**2,1373**2,1667**2]:
   h=vp(Q-1);bound=min(h,n)
   for D in product(range(-4,5),repeat=2):
    for c in units:
     z=sub(scale(D,Q-1),scale(mul(D,D),N));b=mul(z,invunit(c))
     a=sub((Q,0),scale(D,N));d=add(ONE,scale(D,N));low=scale(c,N)
     need(add(a,d)==(Q+1,0),'Wrong trace')
     need(sub(mul(a,d),mul(b,low))==(Q,0),'Wrong determinant')
     need(divides(b,7**bound),'Off-diagonal precision failed')
     need(divides(sub(a,ONE),7**bound) and divides(sub(d,ONE),7**bound),'Scalar precision failed')
     need(divides(sub(d,ONE),N),'Diagonal correction not trivial')
     count+=1;nonrat+=int(any(x[1] for x in [a,b,low,d]));depth2+=int(n==2)
     tight+=int(not divides(b,7**(bound+1)))
 # Dropping full eta precision is false even with trivial natural residual inertia.
 F=[[22,3],[49,8]];N=[[-147,63],[-343,147]]
 need(F[0][0]+F[1][1]==30 and F[0][0]*F[1][1]-F[0][1]*F[1][0]==29,'Control polynomial failed')
 need(imul(N,N)==[[0,0],[0,0]] and imul(F,N)==times(N,29) and imul(N,F)==N,'Control toric identities failed')
 need(all(x%7==0 for row in N for x in row),'Natural inertia control failed')
 need(F[1][0]%343==49 and F[0][1]%7!=0 and F[1][1]%49!=1,'Control does not distinguish hypotheses')
 out={'schema':'beal.block61.local.v1','status':'PASS_EXACT_LOCAL_ALGEBRA',
 'counts':{'matrix_instances':count,'nonrational_instances':nonrat,'depth_two_instances':depth2,'tight_upper_entry_bound':tight},
 'ranges':{'n':[1,2,3,4],'Q':[29,71,491,197**2,883**2,1373**2,1667**2],'D_coefficients':[-4,4],'units':units},
 'negative_control':{'F':F,'N':N,'natural_inertia_mod7':'identity','beta_unramified_Frobenius_nonzero':True,
 'natural_residual_Frobenius_nontrivial':True,'eta_mod49_trivial':False,
 'interpretation':'Local control against dropping eta_n=1; not an actual global Frey representation'},
 'not_a_Lean_certificate':True}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(out['status']);print(out['counts'])
if __name__=='__main__':main()

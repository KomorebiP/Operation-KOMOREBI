#!/usr/bin/env python3
"""Finite chi^-1 conductor extension using inherited actual trace correction sets.
All conductor primes are included. Primary: discrete logs and affine elimination.
The coefficient scalar u is restricted only when the new 83 theorem is invoked.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,math
from pathlib import Path
W=(43,113,127,197,337,463,547,883,1373,1667)
GEN={29:(0,0,0,1,-1,-1),43:(-1,-1,-1,-1,-1,1),71:(0,1,-1,-1,1,-1),
211:(-2,-2,-2,-2,1,-1),239:(-2,-2,0,-1,-2,1),491:(0,1,-2,2,0,2)}
TESTS=(71,29,491,43,211,239)
ADD=[[((x%7+y%7)%7)+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
MUL=[[((x%7*(y%7)+5*(x//7)*(y//7))%7)+7*((x%7*(y//7)+(x//7)*(y%7))%7) for y in range(49)] for x in range(49)]
NEG=[(-(x%7))%7+7*((-(x//7))%7) for x in range(49)]
def need(ok,msg):
 if not ok:raise AssertionError(msg)
def dot(a,b):
 x=0
 for u,v in zip(a,b):x=ADD[x][MUL[u][v]]
 return x
def prime(q):return q>=2 and all(q%d for d in range(2,math.isqrt(q)+1))
def primitive(q):
 factors=[d for d in range(2,q) if (q-1)%d==0 and prime(d)]
 return next(g for g in range(2,q) if all(pow(g,(q-1)//d,q)!=1 for d in factors))
def ev(a,x,q):
 r=0
 for v in reversed(a):r=(r*x+v)%q
 return r
def column(q):
 need(prime(q) and q%7==1 and q%5 in (2,3),'Not in the inert chi-invariant conductor regime')
 g=primitive(q);z=pow(g,(q-1)//7,q);logs={pow(g,j,q):j%7 for j in range(q-1)}
 need(len(logs)==q-1 and z!=1,'Invalid primitive generator')
 rows={};symbols={}
 for ell,a in GEN.items():
  if ell==q:continue  # no unramified Frobenius at a conductor prime
  vv=[ev(a,pow(z,b,q),q) for b in range(1,7)];need(all(vv),'Nonunit at a conductor factor')
  ll=[logs[v] for v in vv];rows[str(ell)]=-sum(b*v for b,v in enumerate(ll,1))%7
  symbols[str(ell)]={'values':vv,'logs_mod7':ll}
 l3,l5=2*logs[3]%7,logs[5]%7
 ratio=(-l5*pow(l3,-1,7))%7 if l3 else ('all' if l5==0 else 'none')
 return {'q':q,'primitive':g,'root':z,'rows':rows,'symbols':symbols,'kummer':[0,l3,l5],'ratio':ratio}
def affine_add(state,row,rhs):
 a=list(row)
 for p,b,c in state:
  t=a[p]
  if t:a=[(x-t*y)%7 for x,y in zip(a,b)];rhs=ADD[rhs][NEG[MUL[t][c]]]
 p=next((i for i,x in enumerate(a) if x),None)
 if p is None:return state if rhs==0 else None
 t=pow(a[p],-1,7);a=[x*t%7 for x in a];rhs=MUL[t][rhs]
 return state+[(p,a,rhs)]
def affine_points(state,n):
 free=[j for j in range(n) if j not in [p for p,a,b in state]]
 for ff in itertools.product(range(49),repeat=len(free)):
  x=[0]*n
  for j,v in zip(free,ff):x[j]=v
  for p,a,b in reversed(state):x[p]=ADD[b][NEG[dot(a,x)]]
  if any(x):yield x
def allowed(data,ell,u,r,b):
 v=MUL[2 if ell==43 else 1][b]
 pp=[MUL[dot(row,[u,r,1])][v] for row in data['kummer_rows'][str(ell)]]
 good=all(x in data['good_trace_sets'][str(ell)] for x in pp)
 bad=all(x==0 for x in pp) and (not any(row[0] for row in data['kummer_rows'][str(ell)]) or v==0)
 return good or bad
def sieve(conductor,columns,data,nonzero):
 answers=[];stages=[]
 for r in range(1,7):
  cc=[q for q in conductor if columns[q]['ratio'] in (r,'all')]
  order=[71,29,491]+([] if 43 in cc else [43])+[211,239]
  rr={ell:[columns[q]['rows'][str(ell)] for q in cc] for ell in order}
  counts=[0]*len(order)
  for u in range(1 if nonzero else 0,49):
   states=[[]]
   for j,ell in enumerate(order):
    vals=[0] if ell==71 else [b for b in range(49) if allowed(data,ell,u,r,b)]
    states=[v for state in states for b in vals if (v:=affine_add(state,rr[ell],b)) is not None]
    counts[j]+=sum(49**(len(cc)-len(s))-(1 if all(b==0 for p,a,b in s) else 0) for s in states)
    if not states:break
   for state in states:
    for x in affine_points(state,len(cc)):
     answers.append({'alpha':[u,r,1],'columns':cc,'inertia':x,'values':{str(ell):dot(rr[ell],x) for ell in order}})
  stages.append({'ratio':r,'columns':cc,'tests':order,'counts':counts})
 return {'conductor':list(conductor),'unit_coefficient_nonzero':nonzero,'stages':stages,'survivors':answers,'count':len(answers)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 data=json.loads(a.fixture.read_text());cc={q:column(q) for q in sorted(W+(617,))}
 strict=sieve(W,cc,data,True);old=sieve(W,cc,data,False);outside=sieve(sorted(W+(617,)),cc,data,True)
 need(strict['count']==0 and old['count']==3 and outside['count']==2,'Changed finite conductor conclusion')
 need(all(z['alpha'][0]==0 for z in old['survivors']),'Old-system control not isolated by the new theorem')
 out={'schema':'beal.block63.conductor.v1','status':'PASS_EXACT_FINITE_SIEVE','columns':[cc[q] for q in sorted(cc)],
      'inherited_fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),
      'strict':strict,'without_unit_restriction':old,'outside_617_control':outside,
      'nonclaim':'Survivors are necessary algebraic tuples, not Frey realizations or integer solutions.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])
if __name__=='__main__':main()

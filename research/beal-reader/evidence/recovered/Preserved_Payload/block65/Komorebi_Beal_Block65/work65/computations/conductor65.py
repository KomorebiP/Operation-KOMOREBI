#!/usr/bin/env python3
"""Block65 exact prime-field conductor systems after the proved coefficient-rigidity reduction.
All conductor primes are included. Primary: discrete logs and affine elimination.
The explicit B65 coefficient theorem restricts u to nonzero trace-zero elements and beta inertia to F7.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,math
from pathlib import Path
W=(43,113,127,197,337,463,547,883,1373,1667)
BASE=tuple(sorted(W+(617,)))
EXPANDED=tuple(sorted(BASE+(953,)))
CONTROL=tuple(sorted(EXPANDED+(743,)))
GEN={29:(0,0,0,1,-1,-1),43:(-1,-1,-1,-1,-1,1),71:(0,1,-1,-1,1,-1),
211:(-2,-2,-2,-2,1,-1),239:(-2,-2,0,-1,-2,1),491:(0,1,-2,2,0,2),281:(-2,-2,-1,-2,0,1)}
GEN[379]=(-2,-2,-1,1,-2,-2)
TESTS=(71,29,491,43,211,239,281,379)
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
def allowed(data,ell,u,r,b,joint=False):
 v=MUL[2 if ell==43 else 1][b]
 pp=[MUL[dot(row,[u,r,1])][v] for row in data['kummer_rows'][str(ell)]]
 good=(any(all(x in pair for x in pp) for pair in data['paired_trace_sets'][str(ell)]) if joint else all(x in data['good_trace_sets'][str(ell)] for x in pp))
 bad=all(x==0 for x in pp) and (not any(row[0] for row in data['kummer_rows'][str(ell)]) or v==0)
 return good or bad



def primefield_points(state,n):
 free=[j for j in range(n) if j not in [p for p,a,b in state]]
 for vv in itertools.product(range(7),repeat=len(free)):
  x=[0]*n
  for j,b in zip(free,vv):x[j]=b
  for p,a,b in reversed(state):x[p]=(b-sum(i*j for i,j in zip(a,x)))%7
  if any(x):yield x

def sieve(conductor,columns,data):
 answers=[];stages=[]
 for r in range(1,7):
  cc=[q for q in conductor if columns[q]['ratio'] in (r,'all')]
  order=[71,29,491]+([] if 43 in cc else [43])+[211,239,281,379]
  rr={ell:[columns[q]['rows'][str(ell)] for q in cc] for ell in order};ns=[0]*len(order)
  for v in range(1,7):
   u=7*v;states=[[]]
   for j,ell in enumerate(order):
    bs=[0] if ell in (71,29) else [b for b in range(7) if allowed(data,ell,u,r,b,True)]
    states=[nxt for state in states for b in bs if (nxt:=affine_add(state,rr[ell],b)) is not None]
    ns[j]+=sum(7**(len(cc)-len(st))-(1 if all(b==0 for _,_,b in st) else 0) for st in states)
    if not states:break
   for st in states:
    for x in primefield_points(st,len(cc)):
     answers.append({'alpha':[u,r,1],'columns':cc,'inertia':x,
        'values':{str(ell):dot(rr[ell],x) for ell in order}})
  stages.append({'ratio':r,'columns':cc,'tests':order,'counts':ns})
 canon=lambda x:json.dumps(x,sort_keys=True)
 return {'conductor':list(conductor),'stages':stages,'survivors':sorted(answers,key=canon),'count':len(answers)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True)
 ap.add_argument('--counts',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args();data=json.loads(a.fixture.read_text());pc=json.loads(a.counts.read_text())
 need(pc['status']=='PASS_FINITE_COUNTS' and len(pc['primes'])==1,'Bad count input')
 p=pc['primes'][0];need(p['q']==379,'Wrong count prime')
 data['good_trace_sets']['379']=p['trace_defect_set']
 data['paired_trace_sets']['379']=[list(z) for z in sorted({tuple(row['defect_roots']) for row in p['rows'] if row['residual_pass']})]
 root=next(z for z in range(2,379) if pow(z,7,379)==1 and ev(GEN[379],z,379)==0)
 def lg(x):return next(i for i in range(7) if pow(root,i,379)==pow(x%379,54,379))
 ph=[x for x in range(379) if (x*x-x-1)%379==0]
 data['kummer_rows']['379']=[[lg(x),lg(3),lg(2*x-1)] for x in ph]
 universe=[q for q in range(11,2001) if prime(q) and q%7==1 and q%5 in(2,3)]
 cc={q:column(q) for q in universe}
 exceptional=[673,1163,1723,1933]
 exclusion=[q for q in universe if q not in exceptional]
 small=sorted(set(CONTROL)|{q for q in universe if q<=1000})
 cases={'retained13':sieve(CONTROL,cc,data),'extended21_exclusion':sieve(exclusion,cc,data),
        'small17_boundary':sieve(small,cc,data),'complete25_boundary':sieve(universe,cc,data)}
 need([z['count'] for z in cases.values()]==[0,0,10,112],'Unexpected finite classification')
 targets=[]
 for z in data['inherited_coupled_survivors']:
  b=dot([cc[q]['rows']['379'] for q in z['columns']],z['inertia'])
  ps=[MUL[dot(k,z['alpha'])][b] for k in data['kummer_rows']['379']]
  good=any(all(x in pair for x in ps) for pair in data['paired_trace_sets']['379']);bad=not any(ps)
  targets.append({'alpha':z['alpha'],'columns':z['columns'],'inertia':z['inertia'],
       'beta379':b,'products':ps,'good_possible':good,'bad_possible':bad})
 need(len(targets)==2 and all(not t['good_possible'] and not t['bad_possible'] for t in targets),'Retained tuple survives')
 # A concrete surviving system outside the declared exclusion.
 witness=next(z for z in cases['small17_boundary']['survivors'] if z['alpha']==[7,6,1])
 out={'schema':'beal.block65.conductor.v1','status':'PASS_FINITE_CONDUCTOR',
  'columns':[cc[q] for q in universe],'generators':{str(k):list(v) for k,v in GEN.items()},
  'test379_root':root,'phi379_roots':ph,'kummer379':data['kummer_rows']['379'],
  'kummer_rows':data['kummer_rows'],'good_trace_sets':data['good_trace_sets'],
  'paired_trace_sets':data['paired_trace_sets'],'universe_bound':2000,'universe':universe,
  'necessary_escape_set_in_universe':exceptional,'cases':cases,
  'retained547743_targets':targets,'larger_conductor_witness':witness,
  'coefficient_reduction':'Conditional B65 coefficient-rigidity theorem, not an experimental field restriction.',
  'nonclaims':['No bound on actual conductor','112 tuples are necessary-system survivors, not representations']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(out['status'],{k:v['count'] for k,v in cases.items()})
if __name__=='__main__':main()

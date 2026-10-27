#!/usr/bin/env python3
"""Finite chi^-1 conductor extension using inherited actual trace correction sets.
All conductor primes are included. Primary: discrete logs and affine elimination.
The coefficient scalar u is restricted only when the new 83 theorem is invoked.
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
def allowed(data,ell,u,r,b,joint=False):
 v=MUL[2 if ell==43 else 1][b]
 pp=[MUL[dot(row,[u,r,1])][v] for row in data['kummer_rows'][str(ell)]]
 good=(any(all(x in pair for x in pp) for pair in data['paired_trace_sets'][str(ell)]) if joint else all(x in data['good_trace_sets'][str(ell)] for x in pp))
 bad=all(x==0 for x in pp) and (not any(row[0] for row in data['kummer_rows'][str(ell)]) or v==0)
 return good or bad

def sieve(conductor,columns,data,include281=True,joint=False):
 answers=[];stages=[]
 for r in range(1,7):
  cc=[q for q in conductor if columns[q]['ratio'] in (r,'all')]
  order=[71,29,491]+([] if 43 in cc else [43])+[211,239]+([281] if include281 else [])
  rr={ell:[columns[q]['rows'][str(ell)] for q in cc] for ell in order}
  counts=[0]*len(order)
  for u in range(1,49):
   states=[[]]
   for j,ell in enumerate(order):
    vals=[0] if ell in (71,29) else [b for b in range(49) if allowed(data,ell,u,r,b,joint)]
    states=[v for state in states for b in vals if (v:=affine_add(state,rr[ell],b)) is not None]
    counts[j]+=sum(49**(len(cc)-len(s))-(1 if all(b==0 for p,a,b in s) else 0) for s in states)
    if not states:break
   for state in states:
    for x in affine_points(state,len(cc)):
     answers.append({'alpha':[u,r,1],'columns':cc,'inertia':x,
        'values':{str(ell):dot(rr[ell],x) for ell in order}})
  stages.append({'ratio':r,'columns':cc,'tests':order,'counts':counts})
 return {'conductor':list(conductor),'joint_good_polynomial':joint,'includes281':include281,
         'stages':stages,'survivors':answers,'count':len(answers)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True)
 ap.add_argument('--counts',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args();data=json.loads(a.fixture.read_text());pc=json.loads(a.counts.read_text())
 need(pc['status']=='PASS_FINITE_COUNTS' and len(pc['primes'])==1,'Bad new count input')
 p=pc['primes'][0];need(p['q']==281,'Wrong test prime')
 data['good_trace_sets']['281']=p['trace_defect_set']
 data['paired_trace_sets']['281']=[list(t) for t in sorted({tuple(z['defect_roots']) for z in p['rows'] if z['residual_pass']})]
 # Compute test-root and natural symbols rather than identifying the two sqrt5 fields.
 coeff=GEN[281];root=next(z for z in range(2,281) if pow(z,7,281)==1 and ev(coeff,z,281)==0)
 def klog(v):return next(j for j in range(7) if pow(root,j,281)==pow(v%281,40,281))
 phis=[v for v in range(281) if (v*v-v-1)%281==0]
 data['kummer_rows']['281']=[[klog(x),klog(3),klog(2*x-1)] for x in phis]
 cc={q:column(q) for q in CONTROL}
 cases={
  'base_before281':sieve(BASE,cc,data,False,False),
  'expanded_before281':sieve(EXPANDED,cc,data,False,False),
  'expanded_exclusion':sieve(EXPANDED,cc,data,True,False),
  'outside743_uncoupled':sieve(CONTROL,cc,data,True,False),
  'outside743_coupled':sieve(CONTROL,cc,data,True,True)}
 need([cases[k]['count'] for k in cases]==[2,16,0,6,2],'Changed finite conductor conclusion')
 targets=[]
 for z in cases['base_before281']['survivors']:
  b=dot([cc[q]['rows']['281'] for q in z['columns']],z['inertia'])
  pp=[MUL[dot(k,z['alpha'])][b] for k in data['kummer_rows']['281']]
  targets.append({'alpha':z['alpha'],'beta281':b,'products':pp,
                  'good_possible':all(x in data['good_trace_sets']['281'] for x in pp),
                  'bad_possible':all(x==0 for x in pp)})
 need(all(not x['good_possible'] and not x['bad_possible'] for x in targets),'617 target survived')
 # Concrete failure of independent choice from different actual good polynomials.
 mixed=[]
 for z in cases['outside743_uncoupled']['survivors']:
  if any(z['alpha']==v['alpha'] and z['inertia']==v['inertia'] for v in cases['outside743_coupled']['survivors']):continue
  for ell in [491,211,239,281]:
   b=z['values'][str(ell)];pp=[MUL[dot(k,z['alpha'])][b] for k in data['kummer_rows'][str(ell)]]
   if allowed(data,ell,*z['alpha'][:2],b,False) and not allowed(data,ell,*z['alpha'][:2],b,True):
    mixed.append({'alpha':z['alpha'],'inertia':z['inertia'],'columns':z['columns'],'prime':ell,'products':pp});break
 need(len(mixed)==4,'Joint-polynomial strengthening not validated')
 out={'schema':'beal.block64.conductor.v1','status':'PASS_EXACT_CONDUCTOR_TESTS',
      'columns':[cc[q] for q in sorted(cc)],'test281_generator':list(coeff),'test281_root':root,
      'phi281_roots':phis,'kummer281':data['kummer_rows']['281'],
      'good_trace_sets':data['good_trace_sets'],'paired_trace_sets':data['paired_trace_sets'],
      'cases':cases,'target617_evaluations':targets,'mixed_polynomial_controls':mixed,
      'nonclaims':['Surviving tuples are not global representations','The complete conductor is stipulated',
         'Affine cardinalities are exact symbolic counts, not independent tests of every hypothetical solution']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(out['status'],{k:v['count'] for k,v in cases.items()})
if __name__=='__main__':main()

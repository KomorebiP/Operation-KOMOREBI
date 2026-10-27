#!/usr/bin/env python3
"""Independent 94-tuple refinement and fixture audit. Imports no primary arithmetic.
Reconstructs correction pairs by trace/norm enumeration in theta^2=theta+1.
Uses independently computed twisted columns and recomputes base residue symbols.
"""
from __future__ import annotations
import argparse,hashlib,json,collections
from pathlib import Path

def check(ok,msg):
 if not ok:raise AssertionError(msg)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def ident(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def add(x,y):return ((x[0]+y[0])%7,(x[1]+y[1])%7)
def mul(x,y):
 a,b=x;c,d=y
 return ((a*c+b*d)%7,(a*d+b*c+b*d)%7)
def power(x,n):
 a=(1,0)
 for bit in bin(n)[2:]:
  a=mul(a,a)
  if bit=='1':a=mul(a,x)
 return a
def wcode(x):return (x[0]+4*x[1])%7+7*(4*x[1]%7)
def poly_eval(cs,x,p):return sum(c*pow(x,j,p) for j,c in enumerate(cs))%p

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sieve',type=Path,required=True);ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--spec',type=Path,required=True);ap.add_argument('--counts-dir',type=Path,required=True);ap.add_argument('--columns',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 d=json.loads(a.fixture.read_text());spec=json.loads(a.spec.read_text());source=json.loads(a.sieve.read_text());cols=json.loads(a.columns.read_text());certificate=json.loads(a.certificate.read_text())
 check(cols['status']=='PASS_SEPARATE_COLUMN_AUDIT','Unverified separate columns');rows_byq={r['q']:r for r in cols['rows']}
 initial=source['expanded28']['survivors'];check(len(initial)==94,'Changed inherited candidate count');remaining=initial[:];stages=[];total_evaluations=0
 for q in spec['test_order']:
  cs=spec['generators'][str(q)];root=[z for z in range(2,q) if pow(z,7,q)==1 and poly_eval(cs,z,q)==0];check(len(root)==1,'Bad test generator');root=root[0]
  def log(x):
   y=pow(x%q,(q-1)//7,q)
   return next(i for i in range(7) if pow(root,i,q)==y)
  phis=[x for x in range(q) if (x*x-x-1)%q==0];check(len(phis)==2,'Non-split new test')
  kr=[[log(x),log(3),log(2*x-1)] for x in phis];check(kr==d['kummer_rows'][str(q)],'Changed natural Kummer rows')
  rec=json.loads((a.counts_dir/f'count_{q}.json').read_text())['primes'][0];allpairs=set();root_checks=0
  for entry in rec['rows']:
   if not entry['residual_pass']:continue
   P=entry['twisted_polynomial'];S=-P[3];B=P[2];t=S-2*(q+1);n=B-2*q-(q+1)*S+(q+1)**2
   check(t%7==0 and n%49==0,'Nonintegral correction trace/norm')
   pair=[]
   for c in range(7):
    for e in range(7):
     root_checks+=1
     if (2*c+e-t//7)%7==0 and (c*c+c*e-e*e-n//49)%7==0:pair.append(wcode((c,e)))
   check(pair,'Empty correction root set');check(sorted(pair)==entry['defect_roots'],'Wrong individual correction pair');allpairs.add(tuple(sorted(pair)))
  pairs=[list(t) for t in sorted(allpairs)];check(pairs==d['paired_trace_sets'][str(q)],'Changed common polynomial pairs')
  passing=[];cases=[]
  for s in remaining:
   beta=sum(t*rows_byq[p]['rows'][str(q)] for p,t in zip(s['columns'],s['inertia']))%7
   v=s['alpha'][0]//7;r=s['alpha'][1];u=((-v)%7,2*v%7)
   products=[]
   for x,y,z in kr:
    value=add(mul((x,0),u),((y*r+z)%7,0));products.append(wcode(mul((beta,0),value)))
   good=[i for i,pair in enumerate(pairs) if set(products)<=set(pair)];bad=set(products)=={0};ok=bool(good) or bad
   total_evaluations+=1
   cases.append({'id':ident(s),'beta_value':beta,'products':products,'good_pair_indices':good,'bad_allowed':bad,'survives':ok})
   if ok:passing.append(s)
  stages.append({'q':q,'before':len(remaining),'after':len(passing),'cases':cases});remaining=passing
 check(stages==certificate['stages'],'Changed stage cases or candidate refinement')
 check(remaining==certificate['survivors'] and len(remaining)==certificate['survivor_count'],'Changed complete survivor list')
 spectrum=dict(sorted(collections.Counter(str(sum(t!=0 for t in s['inertia'])) for s in remaining).items()))
 check(spectrum==certificate['support_histogram'],'Changed support bound')
 check(certificate['minimum_support']==min((sum(t!=0 for t in s['inertia']) for s in remaining),default=None),'Changed minimum support bound')
 check(certificate['ratio_histogram']==dict(sorted(collections.Counter(str(s['alpha'][1]) for s in remaining).items())),'Changed ratio summary')
 result={'schema':'beal.block69.separate_refinement.v1','status':'PASS_INDEPENDENT_REFINEMENT','primary_arithmetic_imports':False,'candidate_test_evaluations':total_evaluations,'stages':stages,'survivor_count':len(remaining),'survivors':remaining,'support_histogram':spectrum,'normalization':'coefficient theta^2=theta+1; output w=2theta-1','scope':'Refinement of the independently replayed complete Block68 94-tuple cover; not a new global representation construction.'}
 a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS_SEPARATE_REFINEMENT',len(remaining))
if __name__=='__main__':main()

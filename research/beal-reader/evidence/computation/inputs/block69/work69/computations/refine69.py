#!/usr/bin/env python3
"""Refine all 94 frozen necessary tuples, retaining every allowed conductor column."""
from __future__ import annotations
import argparse,json,hashlib,collections
from pathlib import Path

def need(ok,msg):
 if not ok:raise AssertionError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def ident(x):return hashlib.sha256(canonical(x).encode()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--sieve',type=Path,required=True);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--columns',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 frozen=json.loads(a.sieve.read_text());d=json.loads(a.fixture.read_text());spec=json.loads(a.spec.read_text());cols=json.loads(a.columns.read_text());byq={x['q']:x for x in cols['columns']}
 start=frozen['expanded28']['survivors'];need(len(start)==94 and frozen['expanded28']['count']==94,'Changed frozen 94-candidate cover');need(len({ident(x) for x in start})==94,'Repeated input tuple')
 left=start[:];stages=[]
 for q in spec['test_order']:
  rows=d['kummer_rows'][str(q)];pairs=d['paired_trace_sets'][str(q)];passed=[];cases=[]
  for s in left:
   need(q not in s['columns'],'Ramified test used without a branch split');v=s['alpha'][0]//7;r=s['alpha'][1]
   b=sum(byq[c]['rows'][str(q)]*t for c,t in zip(s['columns'],s['inertia']))%7
   products=[b*(kr[1]*r+kr[2])%7+7*(b*kr[0]*v%7) for kr in rows]
   good=[i for i,pp in enumerate(pairs) if all(z in pp for z in products)];bad=all(x==0 for x in products);ok=bool(good) or bad
   cases.append({'id':ident(s),'beta_value':b,'products':products,'good_pair_indices':good,'bad_allowed':bad,'survives':ok})
   if ok:passed.append(s)
  stages.append({'q':q,'before':len(left),'after':len(passed),'cases':cases});left=passed
 result={'schema':'beal.block69.refinement.v1','status':'PASS_FINITE_REFINEMENT','input_count':94,'stages':stages,'survivor_count':len(left),'survivors':left,
  'support_histogram':dict(sorted(collections.Counter(str(sum(bool(t) for t in s['inertia'])) for s in left).items())),
  'ratio_histogram':dict(sorted(collections.Counter(str(s['alpha'][1]) for s in left).items())),
  'input_id_sha256':hashlib.sha256('\n'.join(ident(x) for x in start).encode()).hexdigest(),
  'minimum_support':min((sum(bool(t) for t in s['inertia']) for s in left),default=None),
  'scope':'Actual depth one, complete rational beta ramification <=2000, all inherited hypotheses. Surviving tuples are not representations.'}
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS_REFINEMENT',[(x['q'],x['after']) for x in stages],result['support_histogram'])
if __name__=='__main__':main()

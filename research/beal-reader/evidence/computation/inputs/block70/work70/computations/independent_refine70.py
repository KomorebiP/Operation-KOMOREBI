#!/usr/bin/env python3
"""Audit the complete refinement using the independently computed per-prime verdicts."""
from pathlib import Path
import argparse,json,hashlib

def need(x,m):
 if not x:raise AssertionError(m)
def key(s):return hashlib.sha256(json.dumps(s,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--sieve',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--counts-dir',type=Path,required=True);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 load=lambda p:json.loads(p.read_text());src=load(a.sieve);spec=load(a.spec);cert=load(a.certificate);tuples=src['survivors']
 need(len(tuples)==18 and src['survivor_count']==18,'Changed complete predecessor cover')
 ids=[key(x) for x in tuples];alive=set(ids);stages=[];stats=[]
 for p0 in spec['test_order']:
  z=load(a.counts_dir/f'independent_targeted_{p0}.json');need(z['status']=='PASS_SEPARATE_TARGET_AUDIT','No independent arithmetic acceptance')
  need(z['q']==p0 and [v['id'] for v in z['cases']]==ids,'Incomplete independent case set')
  cases=[v for v in z['cases'] if v['id'] in alive];before=len(alive);alive.intersection_update(z['survivors'])
  stages.append({'q':p0,'before':before,'after':len(alive),'cases':cases});stats.append({k:z[k] for k in ['q','admissible_pairs','degree_one_counts','degree_two_counts','smoothness_checks','coefficient_root_checks']})
 surviving=[x for x in tuples if key(x) in alive]
 need(stages==cert['stages'],'Changed stage cases')
 need(surviving==cert['survivors'] and cert['survivor_count']==len(surviving),'Changed complete survivor list')
 h={};rh={};sets=[]
 for x in surviving:
  support={q for q,t in zip(x['columns'],x['inertia']) if t};sets.append(support);s=str(len(support));h[s]=h.get(s,0)+1;r=str(x['alpha'][1]);rh[r]=rh.get(r,0)+1
 need(h==cert['support_histogram'] and rh==cert['ratio_histogram'],'Changed support or ratio spectrum')
 minimum=min(map(len,sets),default=None);forced=sorted(set.intersection(*sets)) if sets else None
 need(cert['minimum_support']==minimum,'Changed minimum support bound');need(cert['forced_support']==forced,'Changed forced ramification set')
 out={'schema':'beal.block70.independent_refinement.v1','status':'PASS_INDEPENDENT_FINITE_REFINEMENT','input_count':18,'stages':stages,'survivor_count':len(surviving),'survivors':surviving,'minimum_support':minimum,'forced_support':forced,'support_histogram':h,'ratio_histogram':rh,'statistics':stats,'primary_arithmetic_imports':False}
 a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS_INDEPENDENT_FINITE_REFINEMENT',len(surviving),flush=True)
if __name__=='__main__':main()

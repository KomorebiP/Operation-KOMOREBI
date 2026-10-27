#!/usr/bin/env python3
"""Combine checked target-specific tests on the complete frozen 18-tuple cover."""
from pathlib import Path
import argparse,collections,hashlib,json

def ident(s):return hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--sieve',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--counts-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 frozen=json.loads(a.sieve.read_text());spec=json.loads(a.spec.read_text());start=frozen['survivors'];assert frozen['survivor_count']==18 and len(start)==18
 ids=[ident(s) for s in start];assert len(set(ids))==18
 left=start[:];stages=[];coverage=[]
 for q in spec['test_order']:
  d=json.loads((a.counts_dir/f'targeted_{q}.json').read_text());assert d['status']=='PASS_TARGETED_FINITE_COUNTS'
  rec=d['record'];assert rec['q']==q and [c['id'] for c in rec['cases']]==ids
  byid={c['id']:c for c in rec['cases']};cases=[byid[ident(s)] for s in left];after=[s for s in left if byid[ident(s)]['survives']]
  stages.append({'q':q,'before':len(left),'after':len(after),'cases':cases});left=after
  coverage.append({k:rec[k] for k in ['q','admissible_pairs','degree_one_counts','degree_two_counts','skip_reasons','unattained_targets']})
 supports=[{q for q,t in zip(s['columns'],s['inertia']) if t} for s in left]
 out={'schema':'beal.block70.refinement.v1','status':'PASS_COMPLETE_FINITE_REFINEMENT','input_count':18,'test_order':spec['test_order'],'stages':stages,'survivor_count':len(left),'survivors':left,
 'support_histogram':dict(sorted(collections.Counter(str(len(s)) for s in supports).items())),
 'ratio_histogram':dict(sorted(collections.Counter(str(s['alpha'][1]) for s in left).items())),
 'minimum_support':min(map(len,supports),default=None),'forced_support':sorted(set.intersection(*supports)) if supports else None,
 'coverage':coverage,'scope':'Depth one and COMPLETE rational beta ramification at primes <=2000, conditional on the inherited Frey, representation, and cohomology hypotheses. This refines a complete frozen cover. Passing local traces do not construct a global representation.'}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('PASS_REFINEMENT',[(s['q'],s['after']) for s in stages],out['support_histogram'],out['forced_support'],flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Build new test fixture from declared integral prime generators and fresh curve counts."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

def need(ok,msg):
 if not ok:raise AssertionError(msg)
def ev(cs,x,q):
 z=0
 for a in reversed(cs):z=(z*x+a)%q
 return z

def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--counts-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 base=json.loads(a.base.read_text());spec=json.loads(a.spec.read_text());d=json.loads(a.base.read_text());dig={}
 for q in spec['test_order']:
  k=str(q);path=a.counts_dir/f'count_{q}.json';doc=json.loads(path.read_text());need(doc['status']=='PASS_FINITE_COUNTS','Invalid count input');rec=doc['primes'][0]
  need(rec['q']==q and rec['f']==1,'Expected split test prime');cs=spec['generators'][k]
  roots=[x for x in range(2,q) if pow(x,7,q)==1 and ev(cs,x,q)==0];need(len(roots)==1,'Invalid test-prime generator root');z=roots[0]
  powers={pow(z,i,q):i for i in range(7)}
  def symbol(x):return powers[pow(x%q,(q-1)//7,q)]
  phi=[x for x in range(q) if (x*x-x-1)%q==0];need(len(phi)==2,'Expected two base-field places')
  d['generators'][k]=cs;d['kummer_rows'][k]=[[symbol(x),symbol(3),symbol(2*x-1)] for x in phi]
  d['paired_trace_sets'][k]=[list(t) for t in sorted({tuple(row['defect_roots']) for row in rec['rows'] if row['residual_pass']})]
  d['test_order'].append(q);dig[k]=hashlib.sha256(path.read_bytes()).hexdigest()
 d['block69_new_counts_sha256']=dig;d['block69_base_sha256']=hashlib.sha256(a.base.read_bytes()).hexdigest()
 a.output.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n');print('PASS_FIXTURE',spec['test_order'])
if __name__=='__main__':main()

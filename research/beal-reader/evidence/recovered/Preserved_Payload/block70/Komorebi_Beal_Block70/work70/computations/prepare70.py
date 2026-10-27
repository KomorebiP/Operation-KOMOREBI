#!/usr/bin/env python3
"""Prepare normalization-only fixture; no claimed point-count values are inserted."""
from pathlib import Path
import argparse,json

def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 d=json.loads(a.base.read_text());s=json.loads(a.spec.read_text())
 for q in s['test_order']:
  assert q not in d['test_order']
  cs=s['generators'][str(q)];roots=[z for z in range(2,q) if pow(z,7,q)==1 and sum(c*pow(z,i,q) for i,c in enumerate(cs))%q==0]
  assert len(roots)==1;z=roots[0];log={pow(z,i,q):i for i in range(7)}
  def symbol(x):return log[pow(x%q,(q-1)//7,q)]
  phis=[x for x in range(q) if (x*x-x-1)%q==0];assert len(phis)==2
  d['test_order'].append(q);d['generators'][str(q)]=cs;d['kummer_rows'][str(q)]=[[symbol(x),symbol(3),symbol(2*x-1)] for x in phis]
 d['block70_new_tests']=s['test_order'];d['block70_count_boundary']='No new correction-pair union is claimed in this normalization fixture. The new counts are target-specific existence/exclusion certificates.'
 a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()

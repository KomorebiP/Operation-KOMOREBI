#!/usr/bin/env python3
"""Primary-only failed-route audit: inert tests whose rational correction set is saturated.
These results are not used to exclude a tuple and are not claimed independently audited.
"""
import argparse,json
from pathlib import Path
import count68

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();count68.PRIMES=(113,127,197);out=[]
 for q in count68.PRIMES:
  r=count68.run_prime(q);pairs=sorted({tuple(t['defect_roots']) for t in r['rows'] if t['residual_pass']})
  assert pairs==[(i,) for i in range(7)]
  out.append({'q':q,'admissible_pairs':r['admissible_pairs'],'defect_pairs':[list(t) for t in pairs]})
 a.output.write_text(json.dumps({'status':'PASS_EXPLORATORY_ONLY','route':'Inert auxiliary trace-product sets permit every F7 product; no extra exclusion follows at this precision. Ramified test places would require separate handling.','independent_implementation':False,'results':out},sort_keys=True,indent=2)+'\n')
 print('EXPLORATORY_SATURATION_CONFIRMED')
if __name__=='__main__':main()

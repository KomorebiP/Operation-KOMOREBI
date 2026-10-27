#!/usr/bin/env python3
"""Read-only trial-jet check against frozen original-index coefficient records.
The inherited coefficient construction certifies the omitted tail. This script
checks the inequalities only; it never labels a zero residue an exact zero.
"""
from pathlib import Path
import argparse, json, math, time

def ev(p,x,mod):
    s=0
    for a in reversed(p): s=(s*x+a)%mod
    return s

def jet(p,k): return [math.comb(i,k)*p[i] for i in range(k,len(p))]
def valuation(z,precision):
    z %= 1<<precision
    return precision if not z else (z&-z).bit_length()-1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--records',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    start=time.monotonic(); records=[]
    for b in [3,7,11,15]:
        rec=json.loads((args.records/f'v25_actual_{b}.json').read_text())['records'][0]
        p=rec['precision']; mod=1<<p; f=list(map(int,rec['coefficients'])); x=6
        v0=valuation(ev(f,x,mod),p)
        v1=valuation(ev(jet(f,1),x,mod),p)
        v2=valuation(ev(jet(f,2),x,mod),p)
        assert max(v0,v1,v2)<p, 'insufficient precision for a required nonzero jet'
        slope_margin=2*v2>v1
        value_margin=min(v2+v1,3*v2)>v0
        mismatch=2*v0!=2+3*v1
        passed=slope_margin and value_margin and mismatch
        assert passed == (b in [7,15])
        assert (v0,v1)==(rec['v_C'],rec['v_A']), 'trial norms do not match inflection norms'
        records.append({'B':b,'trial_y':x,'local_coefficient_precision':p,
          'v_value':v0,'v_slope':v1,'v_half_second':v2,
          'slope_error_valuation_lower_bound':2*v2,
          'value_error_valuation_lower_bound':min(v2+v1,3*v2),
          'slope_margin':slope_margin,'value_margin':value_margin,'norm_mismatch':mismatch,
          'decision':'no critical zero on this fixed core' if passed else 'inconclusive, not a repeated-root finding'})
    report={'status':'PASS','scope':'four fixed multiplier records, no parameter-family claim',
            'seconds':time.monotonic()-start,'records':records}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()

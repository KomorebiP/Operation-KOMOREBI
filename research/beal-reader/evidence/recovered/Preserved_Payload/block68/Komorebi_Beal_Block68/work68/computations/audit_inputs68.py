#!/usr/bin/env python3
"""Check the extension of frozen tests against new complete quartics independently."""
from __future__ import annotations
import argparse,json,hashlib,math
from pathlib import Path

def require(ok,msg):
    if not ok:raise AssertionError(msg)
def evaluate(cs,z,p):return sum(c*pow(z,j,p) for j,c in enumerate(cs))%p

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--extended',type=Path,required=True);p.add_argument('--counts',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    base=json.loads(a.base.read_text());d=json.loads(a.extended.read_text());counts=json.loads(a.counts.read_text());new=[701,911,1009]
    require(d['test_order']==base['test_order']+new,'Wrong test coverage')
    for key in ('inherited_universe','inherited_columns','source_leaves','coefficient_encoding','claimed_previous_final_count'):require(d[key]==base[key],'Changed frozen input')
    for key in ('generators','kummer_rows','paired_trace_sets'):
        for k,v in base[key].items():require(d[key][k]==v,'Changed old test data')
    require(d['base_fixture_sha256']==hashlib.sha256(a.base.read_bytes()).hexdigest(),'Wrong base provenance')
    require(d['new_counts_sha256']==hashlib.sha256(a.counts.read_bytes()).hexdigest(),'Wrong count provenance')
    stats=[]
    for rec in counts['primes']:
        q=rec['q'];require(q in new,'Unexpected test prime');key=str(q);cs=d['generators'][key]
        roots=[z for z in range(2,q) if pow(z,7,q)==1 and evaluate(cs,z,q)==0];require(len(roots)==1,'Bad test-prime root')
        z=roots[0]
        def symbol(x):return next(j for j in range(7) if pow(z,j,q)==pow(x%q,(q-1)//7,q))
        phi=[x for x in range(q) if (x*x-x-1)%q==0]
        expected=[[symbol(x),symbol(3),symbol(2*x-1)] for x in phi]
        require(d['kummer_rows'][key]==expected,'Changed compatible natural row')
        pairs=set()
        for row in rec['rows']:
            if not row['residual_pass']:continue
            P=row['twisted_polynomial'];S=-P[3];C=P[2]
            st=S-2*(q+1);nn=C-2*q-(q+1)*S+(q+1)**2
            require(st%7==0 and nn%49==0,'Nonintegral correction trace/norm')
            ts=st//7%7;ns=nn//49%7
            pair=tuple(sorted(a+7*b for a in range(7) for b in range(7) if 2*a%7==ts and (a*a-5*b*b)%7==ns))
            require(len(pair) in (1,2),'Wrong correction root count');pairs.add(pair)
        require(d['paired_trace_sets'][key]==[list(p) for p in sorted(pairs)],'Invented or missing actual polynomial pair')
        stats.append({'q':q,'compatible_root':z,'kummer_rows':expected,'common_pairs':len(pairs),'residual_pairs':rec['residual_pairs'],'all_pairs':rec['admissible_pairs']})
    out={'status':'PASS_INPUT_AND_POLYNOMIAL_AUDIT','schema':'beal.block68.input-audit.v1','prime_statistics':stats,'method':'Direct symbol alignment and independent 49-element trace/norm root enumeration'}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])
if __name__=='__main__':main()

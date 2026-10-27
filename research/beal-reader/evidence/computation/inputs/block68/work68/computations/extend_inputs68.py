#!/usr/bin/env python3
"""Assemble the new actual-polynomial tests. No exploratory counts are inputs."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
GEN={701:[-2,-2,-1,-1,2,2],911:[-2,-2,-1,0,1,-2],1009:[-2,-2,0,-1,1,2]}
def need(x,msg):
    if not x:raise ValueError(msg)
def ev(cs,x,p):
    v=0
    for c in reversed(cs):v=(v*x+c)%p
    return v

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--counts',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=json.loads(a.fixture.read_text());c=json.loads(a.counts.read_text());need(c['status']=='PASS_FINITE_COUNTS','Bad new count source')
    need([z['q'] for z in c['primes']]==list(GEN),'Wrong new test primes')
    for rec in c['primes']:
        q=rec['q'];k=str(q);cs=GEN[q]
        roots=[r for r in range(2,q) if pow(r,7,q)==1 and ev(cs,r,q)==0];need(len(roots)==1,'Wrong cyclotomic root')
        root=roots[0];powers={pow(root,i,q):i for i in range(7)}
        def symbol(x):return powers[pow(x%q,(q-1)//7,q)]
        ph=[r for r in range(q) if (r*r-r-1)%q==0];need(len(ph)==2,'Nonsplit new test prime')
        d['generators'][k]=cs;d['kummer_rows'][k]=[[symbol(x),symbol(3),symbol(2*x-1)] for x in ph]
        d['paired_trace_sets'][k]=[list(x) for x in sorted({tuple(z['defect_roots']) for z in rec['rows'] if z['residual_pass']})]
        d['test_order'].append(q)
    d['new_counts_sha256']=hashlib.sha256(a.counts.read_bytes()).hexdigest();d['base_fixture_sha256']=hashlib.sha256(a.fixture.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    for q in GEN:print(q,d['kummer_rows'][str(q)],d['paired_trace_sets'][str(q)])
if __name__=='__main__':main()

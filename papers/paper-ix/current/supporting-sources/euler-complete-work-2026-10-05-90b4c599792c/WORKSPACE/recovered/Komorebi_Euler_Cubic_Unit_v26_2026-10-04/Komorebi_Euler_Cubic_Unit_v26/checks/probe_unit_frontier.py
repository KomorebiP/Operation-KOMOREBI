#!/usr/bin/env python3
"""Named stress test: does the new cubic unit criterion decide B=17659?
A false test predicate means inconclusive, not a mathematical counterexample.
"""
from pathlib import Path
import argparse,json,time,hashlib
import check_critical_value as base
from check_cubic_unit import jet,lift,v2

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ns=ap.parse_args()
    if ns.output.exists():raise FileExistsError(ns.output)
    start=time.monotonic();B=17659;P=224;r=B*(1<<640)-161
    G,mu,j=base.residual(r,P)
    if (mu,j)!=(-154,161):raise AssertionError('wrong actual terminal')
    L=base.local(G,90,7,P);content=min(base.v2(x,P) for x in L)
    if content!=162:raise AssertionError('wrong full cubic normalization')
    F=[x>>content for x in L];p=P-content;M=1<<p
    if not (F[3]%2 and all(x%4==0 for x in F[4:])):raise AssertionError('not cubic class')
    rho=lift(F,p);A=base.ev(jet(F,1),rho,M);C=base.ev(F,rho,M);v=base.ev(jet(F,3),rho,M)
    D=(4*A**3+27*v*C*C)%M
    # Strong all-degree Euler bound leaves only coefficients 4 and 5 relevant
    # to a scale up to 16. Do not infer an arbitrary infinite scale from a finite list.
    tail=min(base.v2(x,p) for x in F[4:]);sigma_order=min(tail-2,2)
    va,vc,vd=v2(A),v2(C),v2(D)
    passes=vd is not None and va is not None and 2*vd<8+2*sigma_order+7*va
    out={'status':'completed','B':B,'global_precision':P,'precision':p,'content':content,
         'r':str(r),'j':j,'mu':mu,'ball':[90,7],
         'v_A':va,'v_C':vc,'v_D':vd,'tail_scale_valuation_used':sigma_order,
         'inflection_residue':str(rho),'A_residue':str(A),'C_residue':str(C),'v_residue':str(v),'D_residue':str(D),
         'coefficients':list(map(str,F)),
         'criterion_passes':passes,'interpretation':'no critical zero certified' if passes else 'inconclusive: no exact zero asserted',
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'seconds':time.monotonic()-start}
    ns.output.write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k not in ['coefficients','r']})
if __name__=='__main__':main()

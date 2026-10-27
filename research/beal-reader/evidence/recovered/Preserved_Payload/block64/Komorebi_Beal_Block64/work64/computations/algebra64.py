#!/usr/bin/env python3
"""Exact paired-product algebra and the redundant13 local-value control.
Finite checks supplement the written proof. No primary/independent code imports.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def add(x,y):return ((x[0]+y[0])%7,(x[1]+y[1])%7)
def neg(x):return (-x[0]%7,-x[1]%7)
def mul(x,y):return ((x[0]*y[0]+5*x[1]*y[1])%7,(x[0]*y[1]+x[1]*y[0])%7)
def conj(x):return (x[0],-x[1]%7)
def need(b,s):
    if not b:raise AssertionError(s)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    field=[(i,j) for i in range(7) for j in range(7)];count=0;distinct=0;compatible=0
    for c in field:
        for u in field:
            for b in field:
                z=mul(b,c);d=mul(b,u);p=add(z,d);q=add(z,neg(d))
                relation=conj(p)==q
                split=(z[1]==0 and d[0]==0)
                need(relation==split,'Paired trace/conjugation equivalence')
                if p!=q:
                    distinct+=1
                    if relation:
                        need(p[1]!=0 and mul(p,q)[1]==0,'Distinct conjugates lost quadratic invariants')
                        compatible+=1
                count+=1
    # Exact Z[phi] identity; phi^2=phi+1, no base/coefficient identification.
    def zmul(x,y):return (x[0]*y[0]+x[1]*y[1],x[0]*y[1]+x[1]*y[0]+x[1]*y[1])
    need(zmul((9,-3),(1,1))==(6,3),'Conjugate twist identity')
    for b in field:
        # gamma(Frob13^2)=(1+chi(13)^(-1))*gamma(Frob13)=0.
        need(add(b,mul((6,0),b))==(0,0),'The inert13 value is not automatic')
    # A pair drawn from two different actual polynomials is not a legitimate pair.
    p=(1,4);q=(3,3)  # codes29 and24 from the discarded outside743 candidate.
    choices=[{(0,0)},{(6,0)},{(3,1),(3,6)},{(1,3),(1,4)},{(3,3),(3,4)}]
    union=set().union(*choices)
    need(p in union and q in union,'Union control malformed')
    need(not any(p in x and q in x for x in choices),'Mixed-polynomial control accepted')
    out={'schema':'beal.block64.algebra.v1','status':'PASS_EXACT_ALGEBRA',
         'coefficient_triples':count,'distinct_product_pairs':distinct,'conjugate_distinct_cases':compatible,
         'automatic13_cocycle_values':49,'twist_identity':{'delta':[9,-3],'conjugate_delta':[6,3],'ratio_phi_squared':[1,1]},
         'mixed_polynomial_pair_codes':[29,24],
         'nonclaim':'This checks finite algebra, not the actual geometric identification or global realizability.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])
if __name__=='__main__':main()

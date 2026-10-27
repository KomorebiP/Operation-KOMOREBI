from __future__ import annotations
from math import comb, ceil
import json
from pathlib import Path
from prime_power_cartier_compiler import vp_int, carry_count_add

PRIMES=(2,3,5,7,11,13)
RMAX=20
checks=0
edge_checks=0
for p in PRIMES:
    for q in range(1,60):
        for k in range(0,80):
            v=vp_int(comb(q+k-1,k),p)
            c=carry_count_add(k,q-1,p)
            if v!=c:
                raise AssertionError(('Kummer mismatch',p,q,k,v,c))
            checks+=1
    # Also audit the active-edge inequality over a range of synthetic defect valuations h.
    for r in range(1,RMAX+1):
        for h in range(0,5):
            K=(r-1)//(h+1)
            L=K+ceil((K+1)/(p-1))
            for ell in range(1,L+1):
                q=ceil((ell+1)/p)
                for k in range(K+1):
                    via_bin=k*(1+h)+vp_int(comb(q+k-1,k),p) < r
                    via_carry=k*(1+h)+carry_count_add(k,q-1,p) < r
                    if via_bin!=via_carry:
                        raise AssertionError(('edge mismatch',p,r,h,ell,q,k))
                    edge_checks+=1
result={'schema':'komorebi-kummer-carry-correction-graph-verification-v1','primes':list(PRIMES),'q_max':59,'k_max':79,'r_max':RMAX,'kummer_checks':checks,'edge_checks':edge_checks,'failures':0,'claim_boundary':'Finite exact audit of the classical Kummer carry identity in the specific binomial family used by the correction graph. The mathematical equality is a classical input, not proved by enumeration.'}
Path(__file__).with_name('kummer_carry_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))

from __future__ import annotations
from random import Random
import json
from pathlib import Path
from math import ceil, comb
from prime_power_cartier_compiler import frobenius_defect, vp_poly, vp_int, ppow, trim

SEED=2026091704
PRIMES=(2,3,5,7)
SAMPLES=20
RMAX=6
rng=Random(SEED)
checks=0
for p in PRIMES:
    for _ in range(SAMPLES):
        deg=rng.randint(0,4)
        b0=rng.choice([x for x in range(1,2*p+1) if x%p])
        B=trim([b0]+[rng.randint(-p**3,p**3) for _ in range(deg)])
        E=frobenius_defect(B,p)
        h=vp_poly(E,p)
        if h>10**8:
            continue
        powers=[ppow(E,k) for k in range(RMAX)]
        power_v=[vp_poly(P,p) for P in powers]
        for k in range(RMAX):
            if power_v[k] != k*h:
                raise AssertionError(('power content',p,B,E,h,k,power_v[k]))
        for r in range(1,RMAX+1):
            L=(r-1)+(r+p-2)//(p-1)
            for ell in range(1,L+1):
                q=ceil((ell+1)/p)
                for k in range(r):
                    expected=k*(1+h)+vp_int(comb(q+k-1,k),p)
                    scalar=comb(q+k-1,k)*(p**k)
                    actual=vp_int(scalar,p)+power_v[k]
                    if actual!=expected:
                        raise AssertionError((p,B,E,h,r,ell,q,k,actual,expected))
                    checks+=1
result={'schema':'komorebi-branch-valuation-verification-v1','seed':SEED,'primes':list(PRIMES),'samples_per_prime':SAMPLES,'max_r':RMAX,'checks':checks,'failures':0,'claim_boundary':'Exact integer checks of the branch-content valuation formula. The universal proof uses F_p[z] being an integral domain after factoring the exact p-content of E_B.'}
Path(__file__).with_name('branch_valuation_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))

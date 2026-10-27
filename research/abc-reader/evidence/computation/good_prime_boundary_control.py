#!/usr/bin/env python3
"""Exact named boundary check: rank 2 at p=5=3r-1.

For p>=5, s<=3, v_p(k)<=k/p gives
v_p((2p)^k/k^s) >= k-3*k/p >= 2*k/5.
After K=3N, every omitted moment term is 0 modulo p^N.
All moments here are p-integral, so this also certifies their determinant
modulo p^N. This justifies the finite truncation for the named p-adic values.
"""
from pathlib import Path
import json,sys

def valuation(n,p):
    assert n!=0
    h=0
    while n%p==0:n//=p;h+=1
    return h

output=Path(sys.argv[1]);rows=[]
for p in (5,7):
    for N in (6,8,12,16):
        modulus=p**N;K=3*N;raw=[];depleted=[]
        for s in (1,2,3):
            total=0;unit_total=0
            for k in range(1,K+1):
                h=valuation(k,p);u=k//p**h
                exp=k-s*h
                assert exp>=0
                term=pow(p,exp,modulus)*pow(2,k,modulus)*pow(pow(u,s,modulus),-1,modulus)
                total=(total+term)%modulus
                if h==0:unit_total=(unit_total+term)%modulus
            raw.append(total);depleted.append(unit_total)
        raw_det=(raw[0]*raw[2]-raw[1]**2)%modulus
        depleted_det=(depleted[0]*depleted[2]-depleted[1]**2)%modulus
        actual=valuation(raw_det,p);unit_actual=valuation(depleted_det,p)
        assert actual==(4 if p==5 else 3)
        assert unit_actual==3
        rows.append({'rank':2,'p':p,'t':2*p,'precision':N,'K':K,
                     'raw_determinant_residue':raw_det,'raw_valuation':actual,
                     'depleted_determinant_residue':depleted_det,'depleted_valuation':unit_actual})
report={'status':'PASS','rows':rows,'tail_bound':'For p>=5, v_p(k)<=k/p and s<=3 imply k-s*v_p(k)>=2k/5. K=3N leaves all omitted moment terms with valuation>N. All moments are p-integral here.','interpretation':'The strict good-prime hypothesis p>3r-1 cannot be weakened to p>=3r-1: raw rank 2 at p=5,t=10 has valuation 4 rather than 3. Its depleted value still has valuation 3.','non_claims':['This named boundary case is not an abc result','No global arithmetic realization or height bound supplied']}
output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

"""Finite checks of the exact undepletion continuity obstruction.
The infinite limit is proved in ATTEMPT_AND_BOUNDARY.md, not by these samples.
"""
from __future__ import annotations
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'Komorebi_Euler_Cubic_Unit_v26/checks'))
import check_critical_value as b
P=40;M=1<<P;r0=3
actual=b.fmod(2*b.B[2*r0],P)
depleted=b.fmod(2*(1-2**(2*r0-1))*b.B[2*r0],P)
rows=[]
for h in [4,8,12,16,24,36]:
    v=b.twoB(2*(r0+2**h),P)
    va=b.v2((v-actual)%M,P);vd=b.v2((v-depleted)%M,P)
    assert va==5 and vd==h+2
    rows.append({'h':h,'residue_mod_2_40':str(v),'v2_distance_to_original':va,'v2_distance_to_depleted':vd})
R=17659*(1<<640)-161
bound=(R.bit_count()-1)//3
cost=lambda r,q:3*q+(r+q).bit_count()-r.bit_count()
assert bound==215 and min(cost(R,q) for q in range(161))==-1
old=[cost(R,q) for q in range(216)]
assert min(old)==-154 and max(q for q,z in enumerate(old) if z==-154)==161
for h in [0,1,20,200,1000]:
    rr=R+(1<<(658+h))
    assert rr.bit_count()==647 and (rr.bit_count()-1)//3==215
    assert [cost(rr,q) for q in range(216)]==old
out={'precision':40,'base_index':3,'raw_bernoulli_limit_samples':rows,
     'terminal161_spectral_head':{'mu':-154,'head_valuation':154,'lower_prefix_scalar_minimum':153,
          'lower_positive_dilated_bound':155,'upper_dilated_bound':322},
     'sparse_index_carry_checks_h':[0,1,20,200,1000],
     'status':'bounded exact/modular corroboration of written limit and carry arguments'}
(ROOT/'continuity_results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

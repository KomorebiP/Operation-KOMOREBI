#!/usr/bin/env python3
"""Independent finite checks for the new arithmetic nonvanishing attempts.

No full packet reconstruction is repeated here. The separately replayed
discriminator uses the immutable audited packet engine. This script directly
checks terminal selection, a Newton stationary lift in the stored model,
normalization/precision, and the exhaustive finite carry equivalence.
"""
from pathlib import Path
from fractions import Fraction
import json, sys, hashlib, platform, time

ROOT = Path(__file__).resolve().parents[2]

def val(n):
    return (abs(n)&-abs(n)).bit_length()-1 if n else None

def ev(p,z,m):
    return sum(a*pow(z,i,m) for i,a in enumerate(p))%m

def run():
    start=time.monotonic()
    rec=json.loads((ROOT/'arithmetic_nonvanishing/root/unit_filter_run/results.json').read_text())
    rep=json.loads((ROOT/'arithmetic_nonvanishing/review/replayed_unit_filter.json').read_text())
    assert rec==rep
    r=int(rec['r']); T=int(rec['T']); B=int(rec['B'])
    assert r==(B<<640)-161 and B==17659+(T<<18)
    # Outside this range lambda is positive, while lambda(0)=0.
    end=(r.bit_count()-1)//3
    lam=[3*q+(r+q).bit_count()-r.bit_count() for q in range(end+1)]
    mu=min(lam); j=max(q for q,x in enumerate(lam) if x==mu)
    assert (mu,j)==(-154,161)
    mod=1<<96
    model=json.loads((ROOT/'Euler_Coupled_Stationarity_2026-10-05/coupled/parameter_geometry/model_coefficients.json').read_text())
    # Extend the arrays before combining potentially different lengths.
    h0=list(map(int,model['H0']));h1=list(map(int,model['H1']))
    H=[(h0[i] if i<len(h0) else 0)+T*(h1[i] if i<len(h1) else 0) for i in range(max(len(h0),len(h1)))]
    assert all(i*a%2==0 for i,a in enumerate(H))
    J=[i*a//2 for i,a in enumerate(H) if i]
    DJ=[i*a for i,a in enumerate(J) if i]
    z=0
    # Independent Newton iteration, not the candidate's joint bit lift.
    for _ in range(8):
        z=(z-ev(J,z,mod)*pow(ev(DJ,z,mod),-1,mod))%mod
    assert ev(J,z,mod)==0
    assert z==int(rec['stationary_Z_mod2_96'])
    model_K=ev(H,z,mod)*pow(B,-1,mod)%mod
    raw=int(rec['actual_value_record']['raw_residue'])
    assert raw%(1<<178)==0
    actual_K=(raw>>178)%mod
    assert model_K==actual_K==15*(1<<91)
    assert val(raw)-178==91 and ((raw>>269)&31)==15
    assert int(rec['actual_parameter_exponent_E'])==2*r-25>142
    assert 178+2*141>320
    # Independent carry formulation: minimize over later integers directly.
    count=0
    for M in (1,2,3,6,12):
        for b in range(1,2048,2):
            bound=max(1,(b.bit_count()-1)//M+1)
            direct=all(M*(n-b)+n.bit_count()>b.bit_count() for n in range(b+1,b+bound+1))
            prefix=True
            for t in range(b.bit_length()+1):
                if ((b>>t)&1)==0:
                    lower=b&((1<<t)-1)
                    prefix &= lower.bit_count()<=M*((1<<t)-lower)
            assert direct==prefix
            count+=1
    return {'status':'PASS','independent_terminal':{'mu':mu,'j':j,'q_max':end},
        'newton_stationary_model_bits':96,'actual_normalized_value_bits':142,
        'exact_actual_valuation':91,'unit_mod32':15,'carry_cases':count,
        'full_discriminator_replay_equal':True,
        'nonclaims':['No actual double root constructed.','No nonvanishing theorem established.','Actual packet reconstruction replay relies on the immutable audited engine.'],
        'python':platform.python_version(),'runtime_seconds':time.monotonic()-start}

if __name__=='__main__':
    out=run()
    Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

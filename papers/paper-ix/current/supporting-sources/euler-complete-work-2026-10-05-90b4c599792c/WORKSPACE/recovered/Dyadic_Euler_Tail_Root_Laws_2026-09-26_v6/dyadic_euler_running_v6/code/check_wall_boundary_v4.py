#!/usr/bin/env python3
"""Exact checks at and before the shifted walls, where the minimum is not unique."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import hashlib, json, platform, sys, time
import dyadic_modular as d
from check_completion_v4 import original_normalized_tail

BASE=Path(__file__).resolve().parent

def run():
    started=datetime.now(timezone.utc).isoformat();begin=time.perf_counter()
    counts={'regular_prewall_minima':0,'regular_boundary_certificates':0,
            'irregular_prewall_and_boundary_certificates':0,'independent_original_tails':0}
    records=[]
    for j in range(1,33):
        e=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        if any(z<=0 for z in e[1:]):continue
        Lj=d.wall_threshold(j)
        for L in range(j.bit_length(),Lj):
            r=(1<<L)-j
            assert d.minimum(r)==(0,[0]),(j,L)
            counts['regular_prewall_minima']+=1
        r=(1<<Lj)-j
        dat=d.tail_polynomial(r,24)
        assert dat['mu']==0 and dat['minima']==[0,j]
        atlas=d.root_atlas(dat)
        assert not any(z['kind'].startswith('unresolved') for z in atlas)
        assert sum(z['kind']=='simple_root' for z in atlas)==int(j==1)
        if j>1:assert all(z['kind']=='constant' and z['value']==0 for z in atlas)
        assert sum((Fraction(1,1<<z['k']) for z in atlas),Fraction(0))==1
        for x in range(16):
            assert original_normalized_tail(r,x,24)==d.evaluate(dat['coefficients'],x,1<<24)
            counts['independent_original_tails']+=1
        records.append({'j':j,'L':Lj,'delta':0,'r':r,'mu':0,'atlas':atlas})
        counts['regular_boundary_certificates']+=len(atlas)
    j=17;Lj=d.wall_threshold(j)
    for L in range(j.bit_length(),Lj+1):
        r=(1<<L)-j
        dat=d.tail_polynomial(r,24)
        assert dat['mu']==0 and dat['minima']==([0,1] if L<Lj else [0,1,17])
        atlas=d.root_atlas(dat)
        assert not any(z['kind'].startswith('unresolved') for z in atlas)
        roots=[z for z in atlas if z['kind']=='simple_root']
        assert len(roots)==1 and roots[0]['root_mod']%2==1
        assert sum((Fraction(1,1<<z['k']) for z in atlas),Fraction(0))==1
        for x in range(16):
            assert original_normalized_tail(r,x,24)==d.evaluate(dat['coefficients'],x,1<<24)
            counts['independent_original_tails']+=1
        records.append({'j':j,'L':L,'delta':L-Lj,'r':r,'mu':0,'atlas':atlas})
        counts['irregular_prewall_and_boundary_certificates']+=len(atlas)
    result={'status':'PASS','counts':counts,'records':records,
            'runtime_seconds':time.perf_counter()-begin,
            'scope':'Pre-wall carry minima and complete coefficientwise boundary classifications for all wall labels j<=32; no all-arbitrary-r root assertion.'}
    out=BASE/'RESULTS_BOUNDARY_04.json';out.write_text(json.dumps(result,indent=2)+'\n')
    h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    mf={
        'schema_version':1,'claim_id':'DYADIC-TAIL-V4-BOUNDARY-CLOSURE',
        'repository':{'commit':'not a git checkout; input hashes supplied','dirty':True},
        'command':f'{sys.executable} {Path(__file__).name}',
        'environment':{'software':[sys.version,platform.platform()],'hardware':platform.machine()},
        'mathematics':{'assertion_tested':result['scope'],
            'coefficient_domain':'Exact integer residues and rational coverage weights.',
            'conventions':'r=2^L-j; valid L requires 2^L>j; delta=L-L_j may be zero or negative.',
            'inputs':[{'path':p.name,'sha256':h(p)} for p in [BASE/'dyadic_modular.py',BASE/'check_completion_v4.py',BASE/'check_dyadic_tail.py',Path(__file__)]],
            'bounds':{'j_max':32,'coefficient_precision_bits':24,'independent_offsets':list(range(16)),
                      'j17_L_range':[5,53]},
            'non_claims':['No Lean run.','Finite precision zeros are not exact roots without a simple-root certificate.']},
        'randomness':{'used':False,'generator':'none','seed':None},
        'run':{'started_at':started,'runtime_seconds':result['runtime_seconds'],'exit_status':0},
        'outputs':[{'path':out.name,'sha256':h(out)}],
        'checks':[{'name':k,'count':v,'status':'PASS'} for k,v in counts.items()],
        'result':'PASS: finite assertions verified. Universal regular pre-wall/boundary statements have separate proofs in COMPLETION_04.md.',
        'residual_risks':['Not proof-assistant checked.','Version-1 rather than bounded-runner provenance.']}
    (BASE/'MANIFEST_BOUNDARY_04.json').write_text(json.dumps(mf,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','counts','runtime_seconds')},indent=2))

if __name__=='__main__':run()

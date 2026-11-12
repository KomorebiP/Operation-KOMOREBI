"""Author: Komorebi P. Exact regression and negative-control suite.
No external solver or floating-point acceptance criterion is used.
"""
from __future__ import annotations
import sys,random,json,time,copy
from pathlib import Path
from fractions import Fraction as F
from real_algebraic import trim,mul,add,scale,sub,gcd
from cauer_ladders import find_cauer
from endpoint_extract import find_endpoint_cauer
from recursive_modules import synthesize
from algebraic_witness import verify_algebraic_circuit
from sparse_q3_templates import find_sparse_q3

def coef_rational(P,Q):
    g=gcd(P,Q)
    if len(g)>1:raise ValueError('Fixture target unexpectedly canceled')
    return {'P':list(map(str,trim(P))),'Q':list(map(str,trim(Q)))}

def rc_ladder(n,seed):
    rng=random.Random(seed)
    P=[F(rng.randint(1,5))];Q=[F(1)]
    for i in range(n):
        r=F(rng.randint(1,5));c=F(rng.randint(1,5))
        D=add(Q,mul([F(0),c],P));P=add(scale(D,r),P);Q=D
    return coef_rational(P,Q)

def add_module(P,Q,a,u,kind='RC'):
    P=list(map(F,P));Q=list(map(F,Q));k=[F(u)] if kind=='RC' else [F(0),F(u)]
    h=[F(a),F(1)]
    return coef_rational(add(mul(P,h),mul(k,Q)),mul(Q,h))

def reciprocal(P,Q):return coef_rational(list(map(F,Q)),list(map(F,P)))

def shunt_series_L(P,Q,g,l):
    P=list(map(F,P));Q=list(map(F,Q));w=add(P,mul([F(0),F(l)],Q));d=add(Q,scale(w,F(g)))
    return coef_rational(w,d)

def main():
    t=time.perf_counter();stats={'cauer':0,'endpoint_irreducible_cubic':0,'series_modules':0,
        'parallel_modules':0,'nested_endpoint':0,'sparse_bridges':0,'negative_controls':0}
    # Cauer targets are generated from physical positive ladder component values,
    # but the *synthesizer* receives only their rational P/Q coefficients.
    for n in range(1,9):
        for seed in range(1,5):
            data=rc_ladder(n,101*n+seed)
            z=find_cauer(data['P'],data['Q']);assert z['status']=='CERTIFIED_MINIMUM',(n,seed)
            assert z['verification']['actual_storage']==n
            stats['cauer']+=1
            # Check reciprocal and frequency-inverted orientations.
            if n<=4:
                r=reciprocal(data['P'],data['Q']);zz=find_cauer(r['P'],r['Q'])
                assert zz['status']=='CERTIFIED_MINIMUM',(n,seed,'recip')
                stats['cauer']+=1
    hard=json.loads((Path(__file__).parents[1]/'examples/hard_coupled_q3.json').read_text())
    ep=find_endpoint_cauer(hard['P'],hard['Q']);assert ep['status']=='CERTIFIED_MINIMUM'
    assert ep['verification']['actual_storage']==3
    stats['endpoint_irreducible_cubic']+=1
    # Confirm that a known positive witness is correctly bound to its actual target.
    w=verify_algebraic_circuit(hard['known_exact_witness'],hard,3)
    assert w['status']=='PASS';stats['negative_controls']+=1
    # The original restricted module-only route cannot deflate this irreducible cubic.
    for a in (5,7,9):
        d=add_module(hard['P'],hard['Q'],a,1,'RC');z=synthesize(d['P'],d['Q'])
        assert z['status']=='CERTIFIED_MINIMUM',('series',a,z)
        assert z['verification']['actual_storage']==4
        stats['series_modules']+=1
    d=add_module(hard['P'],hard['Q'],5,1,'RC')
    d=add_module(d['P'],d['Q'],11,2,'RL')
    z=synthesize(d['P'],d['Q']);assert z['status']=='CERTIFIED_MINIMUM',z
    assert z['verification']['actual_storage']==5
    stats['series_modules']+=1
    for a in (4,5,7):
        y=reciprocal(hard['P'],hard['Q'])
        y=add_module(y['P'],y['Q'],a,1,'RC')
        d=reciprocal(y['P'],y['Q'])
        z=synthesize(d['P'],d['Q'])
        assert z['status']=='CERTIFIED_MINIMUM',('parallel',a,z)
        assert z['verification']['actual_storage']==4
        stats['parallel_modules']+=1
    d=shunt_series_L(hard['P'],hard['Q'],F(2),F(3))
    z=synthesize(d['P'],d['Q'])
    assert z['status']=='CERTIFIED_MINIMUM',('nested',z)
    assert z['verification']['actual_storage']==4
    stats['nested_endpoint']+=1
    d2=shunt_series_L(d['P'],d['Q'],F(3),F(2))
    z=synthesize(d2['P'],d2['Q'])
    assert z['status']=='CERTIFIED_MINIMUM',('nested_double',z)
    assert z['verification']['actual_storage']==5
    stats['nested_endpoint']+=1
    # The two seven-component templates are recovered using numerical proposal
    # but are accepted ONLY after exact independent graph verification.
    for filename in ('sparse_bridge_A.json','sparse_bridge_B.json'):
        item=json.loads((Path(__file__).parents[1]/'examples'/filename).read_text())
        rr=find_sparse_q3(item['P'],item['Q'])
        assert rr['status']=='CERTIFIED_MINIMUM',filename
        assert rr['verification']['actual_storage']==3
        stats['sparse_bridges']+=1
        bad=copy.deepcopy(rr['certificate'])
        old=F(bad['branches'][0]['coefficient'][0]);bad['branches'][0]['coefficient'][0]=str(old+F(1,100))
        try:verify_algebraic_circuit(bad,item,3)
        except ValueError:stats['negative_controls']+=1
        else:raise AssertionError('Altered sparse bridge witness was accepted')
    # An example known to need 5 physical reactive elements despite degree 2.
    # It must never be mislabeled minimum 2 by these restricted charts.
    hughes={'P':['2/3','1/2','1'],'Q':['3/2','1/3','1']}
    assert synthesize(hughes['P'],hughes['Q'])['status']=='UNKNOWN'
    stats['negative_controls']+=1
    # Corrupt target binding: exact nodal verifier must reject wrong polynomial.
    corrupt=copy.deepcopy(ep['certificate']);corrupt['target']['P'][0]=str(F(corrupt['target']['P'][0])+1)
    try:verify_algebraic_circuit(corrupt,hard,3)
    except ValueError:stats['negative_controls']+=1
    else:raise AssertionError('Corrupted target was not rejected')
    # Non-positive-real example cannot receive a positive physical witness.
    assert synthesize(['-1','1'],['1','1'])['status']=='UNKNOWN'
    stats['negative_controls']+=1
    # Deliberately strict cutoff is UNKNOWN, never inferred UNSAT.
    assert synthesize(hard['P'],hard['Q'],max_degree=2)['status']=='UNKNOWN'
    stats['negative_controls']+=1
    return {'status':'PASS','statistics':stats,'total_assertion_groups':sum(stats.values()),
            'seconds':time.perf_counter()-t,
            'claim_scope':'Exact witnesses in restricted sufficient templates; UNKNOWN never means impossible'}

if __name__=='__main__':
    r=main();print(json.dumps(r,indent=2))
    (Path(__file__).parents[1]/'results/test_next.json').write_text(json.dumps(r,indent=2))

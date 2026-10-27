#!/usr/bin/env python3
"""Audit the new resolution bound and exact Haar valuation laws.

No random inputs. Assertions use exact integers and Fraction.
"""
from __future__ import annotations
import argparse, json, time
from fractions import Fraction as F
from pathlib import Path
from math import comb
import dyadic_modular as d
from certificates_v5 import (derivative, resultant, squarefree_certificate,
    validate_atlas, survival, mean_valuation, distribution_record, regular_scales, regular_mean)


def run() -> dict:
    start=time.perf_counter();counts={}
    def count(s,n=1):counts[s]=counts.get(s,0)+n
    # Verify the independent resultant construction on split integer polynomials.
    for roots in ([0],[0,1],[0,2],[0,1,2],[0,1,2,4],[1,3,9,27,81]):
        f=[1]
        for x in roots:
            out=[0]*(len(f)+1)
            for k,c in enumerate(f):out[k]-=x*c;out[k+1]+=c
            f=out
        expected=1
        for i,a in enumerate(roots):
            for j,b in enumerate(roots):
                if i!=j:expected*=a-b
        assert resultant(f,derivative(f))==expected
        count('resultant_integer_benchmarks')
    fixtures=[]
    for s in range(1,9):
        bits=4*s+6;w=[0,-(1<<s),1]
        cert=squarefree_certificate(w,bits)
        assert cert['status']=='squarefree' and cert['resultant_valuation']==2*s
        dat={'precision':bits,'coefficients':[z%(1<<bits) for z in w]}
        atlas=d.root_atlas(dat,max_depth=cert['depth_bound'])
        count('polynomial_fixture_leaf_certificates',validate_atlas(dat,atlas))
        assert sum(a['kind']=='simple_root' for a in atlas)==2
        assert max(a['k'] for a in atlas)<=cert['depth_bound']
        fixtures.append({'s':s,'certificate':cert,'max_actual_depth':max(a['k'] for a in atlas)})
        count('separated_root_fixture_cases')
    for w in ([1,0,1],[-1,0,1],[-17,0,1],[1,1,1]):
        bits=24;cert=squarefree_certificate(w,bits)
        assert cert['status']=='squarefree'
        atlas=d.root_atlas({'precision':bits,'coefficients':[z%(1<<bits) for z in w]},max_depth=cert['depth_bound'])
        validate_atlas({'precision':bits,'coefficients':[z%(1<<bits) for z in w]},atlas)
        count('nonsplit_or_quadratic_fixture_cases')
    # A zero resultant is deliberately inconclusive. Do not promote finite zeros.
    repeated=[0,0,1];cert=squarefree_certificate(repeated,24)
    assert cert['status']=='inconclusive_resultant'
    singular=d.root_atlas({'precision':24,'coefficients':repeated})
    assert any(a['kind'].startswith('unresolved') for a in singular)
    count('repeated_root_safety_cases')
    records=[]
    depths=[15,31,63,127,254,255,510,511,1021,2045,4093,8189,16381,
            (1<<24)-3,(1<<40)-7,int('1010111111111111',2)]
    depths += [(1<<(17+delta))-5 for delta in range(1,8)]
    for r in depths:
        dat=d.tail_polynomial(r,32);fac=d.weierstrass_mod(dat)
        cert=squarefree_certificate(fac['W'],32)
        if cert['status']=='squarefree':
            bits=max(32,cert['sufficient_precision'])
            if bits>32:
                assert bits<=96,('audit cap',r,bits)
                dat=d.tail_polynomial(r,bits);fac=d.weierstrass_mod(dat)
                newer=squarefree_certificate(fac['W'],bits)
                assert newer['resultant_valuation']==cert['resultant_valuation']
                cert=newer
            atlas=d.root_atlas({**dat,'coefficients':fac['W']},max_depth=cert['depth_bound'])
            count('squarefree_Euler_leaf_certificates',validate_atlas({**dat,'coefficients':fac['W']},atlas))
            assert max(a['k'] for a in atlas)<=cert['depth_bound']
            count('squarefree_Euler_cases')
        elif cert['status']=='unit_polynomial':
            atlas=d.root_atlas(dat)
        else:
            raise AssertionError(('Unresolved squarefreeness in selected audit range',r,cert))
        records.append({'r':r,'mu':dat['mu'],'degree':fac['degree'],'certificate':cert,
                        'max_actual_depth':max(a['k'] for a in atlas),
                        'distribution':distribution_record(atlas,16)})
        # Compare the exact Haar law with complete residue counts at every h<=12.
        H=12;mod=1<<H
        histogram=[0]*(H+1)
        for x in range(mod):
            value=d.evaluate(dat['coefficients'],x,mod)
            histogram[H if value==0 else int(d.v2(value))]+=1
        count('exhaustive_residue_evaluations',mod)
        for h in range(H+1):
            measured=F(sum(histogram[h:]),mod)
            assert measured==survival(atlas,h),(r,h,measured,survival(atlas,h))
            count('exact_survival_thresholds')
        h0=records[-1]['distribution']['eventual_survival_onset']
        K=F(records[-1]['distribution']['eventual_survival_constant'])
        for h in range(h0,h0+16):
            assert survival(atlas,h)==K/(1<<h)
            count('eventual_geometric_law_checks')
    # Regular-wall mean formulas follow from its exact separating-ball theorem.
    regular=[]
    for j in range(1,129):
        ej=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        scales=regular_scales(j)
        assert sum((F(t+1,1<<k) for i,di,k,t in scales),F(0))==j
        count('skeleton_valuation_mean_identities')
        if any(z<=0 for z in ej[1:]):continue
        if j<=16:
            for delta in range(1,max(t for i,di,k,t in scales)+2):
                r=(1<<(d.wall_threshold(j)+delta))-j
                data=d.tail_polynomial(r,32)
                atlas=d.root_atlas(data)
                assert mean_valuation(atlas)==regular_mean(j,delta)
                regular.append({'j':j,'delta':delta,'mean':str(mean_valuation(atlas))})
                count('regular_wall_mean_checks')
    # Capped linear-factor means give the binomial integral s2(r) without independence.
    H=10;mod=1<<H
    for r in range(1,33):
        total=0
        factorial_val=r-r.bit_count()
        for x in range(mod):
            total+=sum(min(H,int(d.v2(x+i))) if x+i else H for i in range(1,r+1))-factorial_val
        assert F(total,mod)==F(r.bit_count())-F(r,mod)
        count('factorwise_capped_binomial_mean_checks')
    five=[]
    for delta in range(1,8):
        r=(1<<(17+delta))-5;dat=d.tail_polynomial(r,40);atlas=d.root_atlas(dat)
        mean=mean_valuation(atlas)
        gap=r.bit_count()+dat['mu']+mean
        assert gap==16+mean
        if delta>=6:assert gap==21
        five.append({'delta':delta,'r':r,'mu':dat['mu'],'distribution':distribution_record(atlas,16),
                     'mean_precision_excess_over_uniform':str(gap)})
    saturated=[]
    for j in range(1,17):
        delta=max(1,max(t for i,di,k,t in regular_scales(j)))
        L=d.wall_threshold(j)+delta;r=(1<<L)-j;dat=d.tail_polynomial(r,40)
        atlas=d.root_atlas(dat)
        actual=4*r-1+dat['mu']+r.bit_count()+mean_valuation(atlas)
        assert actual==4*(r+j)
        saturated.append({'j':j,'L':L,'r':r,'expected_valuation':str(actual)})
        count('saturated_mean_wall_identities')
    return {'status':'PASS','counts':counts,'squarefree_cases':records,
            'fixture_cases':fixtures,'regular_mean_cases':regular,'five_root_distributions':five,
            'saturated_wall_mean_cases':saturated,'runtime_seconds':time.perf_counter()-start,
            'non_claims':['No universal squarefreeness statement.','Haar expectations are not an independence assumption or a guarantee at every individual integer row.','Only capped frequencies are identified with residue sampling; no untruncated empirical average convergence theorem is asserted.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=run();a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','counts','runtime_seconds')},indent=2))

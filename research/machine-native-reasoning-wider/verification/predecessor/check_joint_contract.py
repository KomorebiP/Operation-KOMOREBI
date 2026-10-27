#!/usr/bin/env python3
"""Exact rational finite witnesses for legal and stochastic quotient composition.
Tests current-state fibre constancy and whole report/action/coarse-history laws.
No claim about learning, real-world authorization, or formal proof verification.
"""
from fractions import Fraction as F
from collections import defaultdict
import itertools,json
from pathlib import Path

states=list(itertools.product((0,1),repeat=3))
coarse=list(itertools.product((0,1),repeat=2))
pi=lambda x:x[:2]
acts=('hold','flip','repair')

def legal(x):
    b,s,n=x
    return ('hold','flip','repair') if b==0 else ('hold','flip')

def step(x,a):
    b,s,n=x
    assert a in legal(x)
    if a=='flip': b=1-b
    if a=='repair': b=0
    return (b,s,n)

def instrument(x,a):
    y=step(x,a)
    # A supplied fair-noise reported display, independent of the nuisance bit.
    report_correct=y[0]^y[1]
    return {(y,report_correct):F(3,4), (y,1-report_correct):F(1,4)}

# Check all fibres, all enabled actions, and normalization.
fine_joint={}
coarse_joint={}
for x in states:
    for a in legal(x):
        fine_joint[(x,a)]=instrument(x,a)
        coarse_distribution=defaultdict(F)
        for (xnext,o),prob in instrument(x,a).items():
            coarse_distribution[(pi(xnext),o)]+=prob
        assert sum(coarse_distribution.values())==1
        key=(pi(x),a)
        if key in coarse_joint: assert dict(coarse_distribution)==coarse_joint[key]
        else: coarse_joint[key]=dict(coarse_distribution)
for x in states:
    assert legal(x)==legal((x[0],x[1],1-x[2]))

# Independently enumerate full paths, with a policy that sees ONLY previous reports.
def policy(reports):
    if not reports: return 'hold'
    return 'flip' if reports[-1]==0 else 'hold'

fine={(x,(),()):F(1,8) for x in states}
coarse_paths={(z,(),()):F(1,4) for z in coarse}
counts=[]
for t in range(5):
    fine_obs=defaultdict(F)
    coarse_obs=defaultdict(F)
    for (x,acts0,obs),mass in fine.items(): fine_obs[(pi(x),acts0,obs)]+=mass
    for (z,acts0,obs),mass in coarse_paths.items(): coarse_obs[(z,acts0,obs)]+=mass
    assert dict(fine_obs)==dict(coarse_obs), {'horizon':t}
    counts.append(len(fine_obs))
    if t==4:break
    newfine=defaultdict(F)
    for (x,aa,oo),mass in fine.items():
        a=policy(oo)
        assert a in legal(x)
        for (xp,o),p in fine_joint[(x,a)].items(): newfine[(xp,aa+(a,),oo+(o,))]+=mass*p
    fine=dict(newfine)
    newcoarse=defaultdict(F)
    for (z,aa,oo),mass in coarse_paths.items():
        a=policy(oo)
        for (zp,o),p in coarse_joint[(z,a)].items(): newcoarse[(zp,aa+(a,),oo+(o,))]+=mass*p
    coarse_paths=dict(newcoarse)

# The standard marginal-only counterexample: same coarse successor and report
# marginal, different joint law inside a current coarse fibre.
paired={
 'x0':{(0,0):F(1,2),(1,1):F(1,2)},
 'x1':{(0,1):F(1,2),(1,0):F(1,2)}
}
for mode in ('successor','report'):
 projected=[]
 for lab,dist in paired.items():
    marginal=defaultdict(F)
    for (newz,o),p in dist.items(): marginal[newz if mode=='successor' else o]+=p
    projected.append(dict(marginal))
 assert projected[0]==projected[1]
assert paired['x0']!=paired['x1']

out={
 'case':'8-state to 4-state quotient, nuisance bit removed',
 'source_states':8,'coarse_states':4,'actions':list(acts),
 'verified_fibre_law_contracts':len(coarse_joint),
 'horizons_tested':[0,1,2,3,4],
 'distinct_joint_coarse_histories':counts,
 'history_laws_identical':True,
 'marginal_only_counterexample':True,
 'arithmetic':'fractions.Fraction, exact rationals',
 'assurance':'finite reference checks, not general theorem/kernel/learned-world evidence',
 'passed':True
}
p=Path(__file__).resolve().parents[1]/'verification'/'joint_contract_exact_checks.json'
p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

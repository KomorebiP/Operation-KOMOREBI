#!/usr/bin/env python3
"""Exact complete-path checks for the legal/stochastic quotient.

Paths retain every state, not only the terminal state. Fine and coarse rows
are constructed separately. Policies depend on the report history and the
initially declared scenario, never on the path's hidden current state.
"""
from __future__ import annotations
from fractions import Fraction as F
from collections import defaultdict
from itertools import product
from pathlib import Path
import json

X=tuple(product((0,1),repeat=3)); Z=tuple(product((0,1),repeat=2))
def project(x):return x[:2]
def label(x):return x[0]^x[1]
def enabled(x):return frozenset(('hold','flip','repair')) if x[0]==0 else frozenset(('hold','flip'))

def fine_row(x,a):
    if a not in enabled(x):raise ValueError('disabled fine action')
    b,s,n=x
    if a=='flip':b=1-b
    nxt=(b,s,n);o=b^s
    return {(nxt,o):F(3,4),(nxt,1-o):F(1,4)}

def coarse_row(z,a):
    if a not in enabled(z):raise ValueError('disabled coarse action')
    # Independently specified coarse transition, not a projection of fine_row.
    nxt=(1-z[0],z[1]) if a=='flip' else z
    return {(nxt,o): F(3,4) if o==nxt[0]^nxt[1] else F(1,4) for o in (0,1)}

def policy(mode,reports):
    if mode=='adaptive':return {'flip' if reports and reports[-1]==0 else 'hold':F(1)}
    if mode=='randomized':
        return {'hold':F(1,3),'flip':F(2,3)} if len(reports)%2==0 else {'hold':F(2,3),'flip':F(1,3)}
    if mode=='known_target':return {'hold':F(1,2),'repair':F(1,2)}
    raise ValueError('unknown policy')

def push_prior(prior):
    out=defaultdict(F)
    for x,p in prior.items():out[project(x)]+=p
    return dict(out)

def state_history_law(paths,projection):
    out=defaultdict(F)
    for (ss,aa,oo),mass in paths.items():out[(tuple(projection(s) for s in ss),aa,oo)]+=mass
    return dict(out)

def posterior_groups(paths,projection):
    out=defaultdict(lambda:defaultdict(F))
    for (ss,aa,oo),mass in paths.items():out[(aa,oo)][projection(ss[-1])]+=mass
    return {h:dict(row) for h,row in out.items()}

def next_paths(paths,row,mode):
    out=defaultdict(F)
    for (ss,aa,oo),mass in paths.items():
        probabilities=policy(mode,oo)
        assert sum(probabilities.values())==1
        for a,p_a in probabilities.items():
            assert p_a>=0 and a in enabled(ss[-1])
            for (xp,o),p in row(ss[-1],a).items():
                assert p>=0
                out[(ss+(xp,),aa+(a,),oo+(o,))]+=mass*p_a*p
    return dict(out)

def main():
    fibre_rows=0
    for z in Z:
        fibre=[x for x in X if project(x)==z]
        assert len({enabled(x) for x in fibre})==1
        assert len({label(x) for x in fibre})==1
        for a in enabled(z):
            for x in fibre:
                projected=defaultdict(F)
                for (xp,o),p in fine_row(x,a).items():projected[(project(xp),o)]+=p
                assert dict(projected)==coarse_row(z,a)
            fibre_rows+=1
    scenarios=[('adaptive',{x:F(1,8) for x in X}),
               ('randomized',{x:F(1,8) for x in X}),
               ('known_target',{x:F(1,4) for x in X if x[0]==0}),
               ('randomized',{x:F(i+1,36) for i,x in enumerate(X)})]
    records=[];posterior_checks=0;full_path_records=0
    for mode,prior in scenarios:
        fine={( (x,),(),()):p for x,p in prior.items()}
        coarse={((z,),(),()):p for z,p in push_prior(prior).items()}
        horizons=[]
        for t in range(5):
            f=state_history_law(fine,project);c=state_history_law(coarse,lambda z:z)
            assert f==c and sum(f.values())==1
            assert state_history_law(fine,label)==state_history_law(coarse,label)
            full_path_records+=len(f)
            fg=posterior_groups(fine,project);cg=posterior_groups(coarse,lambda z:z)
            assert fg==cg
            for history,values in fg.items():
                mass=sum(values.values());assert mass>0
                assert {z:p/mass for z,p in values.items()}=={z:p/mass for z,p in cg[history].items()}
                legal=set.intersection(*(set(enabled(z)) for z in values))
                fine_support={ss[-1] for (ss,aa,oo),p in fine.items() if (aa,oo)==history and p>0}
                assert legal==set.intersection(*(set(enabled(x)) for x in fine_support))
                assert set(policy(mode,history[1]))<=legal
                posterior_checks+=1
            horizons.append({'horizon':t,'complete_projected_paths':len(f),'report_histories':len(fg)})
            if t<4:
                fine=next_paths(fine,fine_row,mode);coarse=next_paths(coarse,coarse_row,mode)
        records.append({'policy':mode,'initial_support':len(prior),'horizons':horizons})
    # Equal marginals, unequal joint rows.
    diagonal={(0,0):F(1,2),(1,1):F(1,2)}
    anti={(0,1):F(1,2),(1,0):F(1,2)}
    for i in (0,1):
        def marginal(d):
            m=defaultdict(F)
            for key,p in d.items():m[key[i]]+=p
            return dict(m)
        assert marginal(diagonal)==marginal(anti)
    assert diagonal!=anti
    # The exact coverage gap in the predecessor: terminal equality need not
    # preserve the intervening state/label path.
    left={(0,1,0):F(1)};right={(0,0,0):F(1)}
    assert {path[-1]:p for path,p in left.items()}=={path[-1]:p for path,p in right.items()}
    assert left!=right
    # Action and label collisions invalidate the relevant fibre clauses.
    assert enabled((0,0,0))!=enabled((1,1,0))
    assert label((0,0,0))!=label((0,1,0))
    result={'status':'PASS','verified_fibre_state_action_rows':fibre_rows,
            'scenarios':records,'complete_path_records_compared':full_path_records,
            'positive_history_posterior_and_action_checks':posterior_checks,
            'negative_controls':4,'arithmetic':'exact fractions.Fraction',
            'corrected_predecessor_boundary':'the old script compared terminal coarse state plus action/report words, not complete state paths',
            'scope':'four explicitly declared scenarios through horizon four; not general theorem certification'}
    out=Path(__file__).resolve().parents[1]/'verification'/'joint_contract_exact_checks.json'
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

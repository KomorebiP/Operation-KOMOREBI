#!/usr/bin/env python3
"""Exact finite checks for quotient transport and conservative support envelopes."""
from __future__ import annotations
from itertools import product
from fractions import Fraction
from pathlib import Path
import json, random
from finite_games import Game, regions, pre, pull, image, all_subsets, exact_quotient

COUNTS = {"exhaustive_two_state_games": 0, "accepted_exact_quotients": 0,
          "constructed_larger_quotients": 0, "conservative_envelopes": 0,
          "predecessor_identities": 0, "negative_controls": 0}

def check_exact(g, q, pi):
    for b in all_subsets(q.n):
        for fc, cc in ((g.running, q.running), (g.ending, q.ending)):
            assert pre(fc, pull(pi, b)) == pull(pi, pre(cc, b))
            COUNTS["predecessor_identities"] += 1
    ft, fl, fr = regions(g)
    qt, ql, qr = regions(q)
    for k in range(max(len(ft), len(qt))):
        assert ft[min(k,len(ft)-1)] == pull(pi,qt[min(k,len(qt)-1)])
    for k in range(max(len(fl), len(ql))):
        assert fl[min(k,len(fl)-1)] == pull(pi,ql[min(k,len(ql)-1)])
    assert fr == {x:qr[pi[x]] for x in ft[-1]}
    # Check the actual lifted positional witnesses, not just set equality.
    for z in ql[-1]:
        a = next(a for a,p in enumerate(q.running[z]) if p is not None and p <= ql[-1])
        for x in pull(pi, frozenset([z])):
            assert g.running[x][a] <= fl[-1]
    for z,k in qr.items():
        if k:
            a = next(a for a,p in enumerate(q.ending[z])
                     if p is not None and all(qr.get(y,q.n+1)<k for y in p))
            for x in pull(pi,frozenset([z])):
                assert all(fr.get(y,g.n+1)<k for y in g.ending[x][a])

def random_lift(rng, q, pi):
    n=len(pi); fibers=[list(pull(pi,frozenset([z]))) for z in range(q.n)]
    cats=[]
    for cat in (q.running,q.ending):
        rows=[]
        for x in range(n):
            row=[]
            for post in cat[pi[x]]:
                if post is None: row.append(None);continue
                chosen=set()
                for z in post:
                    f=fibers[z]
                    chosen.add(rng.choice(f))
                    chosen.update(y for y in f if rng.randrange(2))
                row.append(frozenset(chosen))
            rows.append(tuple(row))
        cats.append(tuple(rows))
    return Game(n,pull(pi,q.safe),pull(pi,q.goal),*cats)

def main():
    opts=(None,)+tuple(s for s in all_subsets(2) if s)
    for values in product(opts,repeat=4):
        for status in product(range(3),repeat=2):
            safe=frozenset(i for i,s in enumerate(status) if s>=1)
            goal=frozenset(i for i,s in enumerate(status) if s==2)
            g=Game(2,safe,goal,((values[0],),(values[1],)),((values[2],),(values[3],)))
            COUNTS['exhaustive_two_state_games']+=1
            for pi in ((0,0),(0,1)):
                q=exact_quotient(g,pi)
                if q is not None:
                    check_exact(g,q,pi);COUNTS['accepted_exact_quotients']+=1
    rng=random.Random(102223)
    for _ in range(3000):
        m=rng.choice((2,3)); pi=tuple(list(range(m))+[rng.randrange(m) for _ in range(rng.randrange(1,3))])
        statuses=[rng.randrange(3) for _ in range(m)]
        safe=frozenset(i for i,s in enumerate(statuses) if s>=1)
        goal=frozenset(i for i,s in enumerate(statuses) if s==2)
        subsets=tuple(s for s in all_subsets(m) if s)
        cats=[]
        for mode in range(2):
            cats.append(tuple(tuple(None if rng.randrange(4)==0 else rng.choice(subsets)
                                    for a in range(2)) for x in range(m)))
        q=Game(m,safe,goal,*cats);g=random_lift(rng,q,pi)
        check_exact(g,q,pi);COUNTS['constructed_larger_quotients']+=1
        # Adverse envelope: discard actions or add possible successors.
        ec=[]
        for cat in cats:
            ec.append(tuple(tuple(None if p is None or rng.randrange(5)==0
                                   else p | rng.choice(subsets) for p in row) for row in cat))
        env=Game(m,safe,goal,*ec)
        ft,fl,fr=regions(g);et,el,er=regions(env)
        assert pull(pi,et[-1]) <= ft[-1]
        assert pull(pi,el[-1]) <= fl[-1]
        assert all(fr[x]<=er[pi[x]] for x in pull(pi,et[-1]))
        COUNTS['conservative_envelopes']+=1
    # A malformed enabled dead end must not count as a vacuous winning action.
    try: Game(1,frozenset([0]),frozenset(),((frozenset(),),),((None,),))
    except ValueError: COUNTS['negative_controls']+=1
    else: raise AssertionError('empty enabled post accepted')
    # Goal/safety collisions and action-availability collisions invalidate quotients.
    bad=Game(2,frozenset([0]),frozenset(),((frozenset([0]),),(frozenset([1]),)),((None,),(None,)))
    assert exact_quotient(bad,(0,0)) is None;COUNTS['negative_controls']+=1
    bad=Game(2,frozenset([0,1]),frozenset(),((None,),(frozenset([1]),)),((None,),(None,)))
    assert exact_quotient(bad,(0,0)) is None;COUNTS['negative_controls']+=1
    # Tiny stochastic error can destroy a sure ending at state 0.
    nominal=Game(3,frozenset([0,1]),frozenset([1]),
                 ((frozenset([0]),),(frozenset([1]),),(None,)),
                 ((frozenset([1]),),(frozenset([1]),),(None,)))
    perturbed=Game(3,nominal.safe,nominal.goal,nominal.running,
                  ((frozenset([1,2]),),(frozenset([1]),),(None,)))
    nt,nl,_=regions(nominal);pt,pl,_=regions(perturbed)
    assert 0 in nt[-1] and 0 in nl[-1] and 0 not in pt[-1] and 0 not in pl[-1]
    epsilons=[]
    for d in (2,10,100,1000,1000000):
        e=Fraction(1,d)
        tv=(abs(1-(1-e))+abs(e))/2
        assert tv==e
        epsilons.append(str(e))
    COUNTS['negative_controls']+=1
    result={'status':'PASS','counts':COUNTS,'seed':102223,
            'support_counterexample_epsilons':epsilons,
            'scope':'finite exact reference checks of stated quotients and enclosures; not Lean certification'}
    out=Path(__file__).resolve().parents[1]/'verification'/'control_transport.json'
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

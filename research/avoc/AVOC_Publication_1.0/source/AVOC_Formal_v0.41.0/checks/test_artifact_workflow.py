#!/usr/bin/env python3
"""Exact finite tests of reported-outcome Bayes and the staged workflow.

These checks are independent rational arithmetic, not a refinement proof of the
filesystem adapter. General mathematical claims are proved in the Lean modules.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib, json, sys, time

ROOT = Path(__file__).resolve().parents[1]
RD = ROOT / 'results/v0.17.0'


def predict(b, channel):
    return tuple(sum(b[w] * channel[w][o] for w in range(2)) for o in range(3))


def posterior(b, likelihood):
    mass = sum(x*y for x,y in zip(b,likelihood))
    return tuple(x*y/mass for x,y in zip(b,likelihood)) if mass else b


def report_channel(channel, mask):
    return tuple(tuple(sum(row[o] for o in range(3) if mask[o] == d)
                       for d in (False, True)) for row in channel)


def l1(a,b):
    return sum(abs(x-y) for x,y in zip(a,b))


def channel_checks():
    rows = [tuple(F(x,4) for x in (a,b,4-a-b)) for a in range(5) for b in range(5-a)]
    count = zero = 0
    for p,(row0,row1),mask in product([F(i,4) for i in range(5)], product(rows,repeat=2), product((False,True),repeat=3)):
        b,c = (1-p,p),(p,1-p)
        e,g = (row0,row1),(row1,row0)
        pe,pg = predict(b,e),predict(c,g)
        be=[posterior(b,(e[0][o],e[1][o])) for o in range(3)]
        cg=[posterior(c,(g[0][o],g[1][o])) for o in range(3)]
        joint=sum(abs(b[w]*e[w][o]-c[w]*g[w][o]) for w in range(2) for o in range(3))
        assert joint <= l1(b,c) + max(l1(e[w],g[w]) for w in range(2))
        assert l1(pe,pg) <= joint
        assert sum(pe[o]*l1(be[o],cg[o]) for o in range(3)) <= 2*joint
        ec=report_channel(e,mask)
        pc=tuple(sum(b[w]*ec[w][d] for w in range(2)) for d in range(2))
        bc=[posterior(b,(ec[0][d],ec[1][d])) for d in range(2)]
        for d in range(2):
            assert pc[d] == sum(pe[o] for o in range(3) if mask[o]==bool(d))
            for w in range(2):
                assert pc[d]*bc[d][w] == sum(pe[o]*be[o][w] for o in range(3) if mask[o]==bool(d))
            zero += pc[d] == 0
        # Arbitrary continuation of the reported posterior, not a raw-aware policy.
        v=[F(2)*bc[d][1] - F(d) for d in range(2)]
        assert sum(pc[d]*v[d] for d in range(2)) == sum(pe[o]*v[int(mask[o])] for o in range(3))
        count+=1
    return dict(comparisons=count,zero_predictive_report_entries=zero)


@dataclass(frozen=True)
class State:
    belief: F
    completed: bool = False
    generation: int = 0
    pending: tuple[int,bool] | None = None
    checked: int | None = None
    budget: int = 3
    spent: int = 0
    halted: bool = False


def actions(s):
    if s.halted: return ('stop',)
    out=['stop']
    if s.budget:
        if not s.completed: out += ['register-valid','register-invalid']
        if s.pending is not None: out += ['verify']
        if s.pending is not None and s.checked == s.pending[0] and s.pending[1]: out += ['admit']
    return tuple(out)


def safe(s,total):
    return (F(0)<=s.belief<=F(1) and s.budget>=0 and s.spent>=0 and s.budget+s.spent==total
        and (s.pending is None or (s.pending[0]<s.generation and not s.completed))
        and (s.checked is None or (s.pending is not None and s.pending==(s.checked,True))))


def report_prob(s,a,e):
    if a!='verify': return (F(1),F(0))
    good = s.pending is not None and s.pending[1]
    q = ((1-s.belief)*e[0][0]+s.belief*e[1][0]) if good else F(0)
    return (1-q,q)


def transition(s,a,d,e):
    if a not in actions(s):raise ValueError('inadmissible action')
    if a=='stop':return replace(s,halted=True)
    z=replace(s,budget=s.budget-1,spent=s.spent+1)
    if a.startswith('register'):
        return replace(z,generation=s.generation+1,pending=(s.generation,a=='register-valid'),checked=None)
    if a=='admit':return replace(z,completed=True,pending=None,checked=None)
    good = s.pending is not None and s.pending[1]
    l=(e[0][0],e[1][0]) if good else (F(0),F(0))
    if not d:l=tuple(1-x for x in l)
    bnew=posterior((1-s.belief,s.belief),l)[1]
    return replace(z,belief=bnew,checked=s.pending[0] if d and good else None)


def reward(s,a):return F(0) if a=='stop' else F(7) if a=='admit' else F(-1)


def control_checks():
    channels=[((F(1,4),F(1,2),F(1,4)),(F(3,4),F(1,4),F(0))),
              ((F(0),F(1),F(0)),(F(1),F(0),F(0))),
              ((F(1,2),F(1,2),F(0)),(F(1,2),F(0),F(1,2)))]
    seen_states=branches=tree_choices=0
    witnesses=[]
    for e,p,budget in product(channels,[F(i,4) for i in range(5)],[2,3,4]):
        init=State(p,budget=budget)
        frontier={init};allstates={init}
        for depth in range(4):
            nxt=set()
            for s in frontier:
                assert safe(s,budget)
                for a in actions(s):
                    assert sum(report_prob(s,a,e))==1
                    for d in (False,True):
                        t=transition(s,a,d,e);assert safe(t,budget);branches+=1
                        if a.startswith('register') or a=='verify':assert t.completed==s.completed
                        if a=='verify' and not d:assert t.pending==s.pending and t.checked is None
                        if a=='admit':assert t.pending is None and t.checked is None and 'admit' not in actions(t)
                        if a!='verify':assert t.belief==s.belief
                        nxt.add(t)
            frontier=nxt-allstates;allstates |= nxt
        seen_states+=len(allstates)
        @lru_cache(None)
        def value(n,s):
            if n==0:return F(0)
            return max(reward(s,a)+sum(prob*value(n-1,transition(s,a,d,e)) for d,prob in enumerate(report_prob(s,a,e))) for a in actions(s))
        @lru_cache(None)
        def trees(n,s):
            nonlocal tree_choices
            if n==0:return (F(0),)
            out=[]
            for a in actions(s):
                pr=report_prob(s,a,e)
                v0=trees(n-1,transition(s,a,False,e));v1=trees(n-1,transition(s,a,True,e))
                for x,y in product(v0,v1):
                    out.append(reward(s,a)+pr[0]*x+pr[1]*y);tree_choices+=1
            return tuple(out)
        for n in range(4):assert max(trees(n,init))==value(n,init)
        if e==channels[0] and p==F(1,2) and budget==3:
            reg=transition(init,'register-valid',False,e)
            failed=transition(reg,'verify',False,e)
            passed=transition(reg,'verify',True,e)
            assert failed.belief==F(1,4) and passed.belief==F(3,4)
            assert value(1,init)==0 and value(2,reg)==F(5,2) and value(3,init)==F(3,2)
            assert value(1,failed)==0 and value(1,passed)==7
            done=transition(passed,'admit',False,e)
            assert done.spent==3 and done.completed
            witnesses.append(dict(initial_V3=str(value(3,init)),registered_V2=str(value(2,reg)),reject_posterior=str(failed.belief),accept_posterior=str(passed.belief),total_success_spend=done.spent))
    return dict(configurations=45,reachable_state_instances=seen_states,transition_checks=branches,
                enumerated_adaptive_tree_values=tree_choices,witnesses=witnesses)


def main():
    t=time.monotonic();c=channel_checks();w=control_checks()
    paths=['checks/test_artifact_workflow.py']+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'AVOC').glob('ArtifactWorkflow*.lean'))]+['AVOC/FilteredObservation.lean']
    result=dict(status='PASS',arithmetic='fractions.Fraction; exact',channel=c,workflow=w,
                seconds=round(time.monotonic()-t,3),scope='Finite reported-outcome comparisons and independent small controller; not empirical LLM evidence or filesystem refinement.',
                source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
    RD.mkdir(parents=True,exist_ok=True);(RD/'workflow_regression.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

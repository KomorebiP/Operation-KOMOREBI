#!/usr/bin/env python3
"""Finite exact reference checks for machine-theory Core 8.3.

This is a Python exhaustive-state model check, NOT Lean certification.
All action successors are nonempty finite sets and nondeterminism is demonic.
Independent policy enumeration is used to check two fixed-point calculations.
"""
from __future__ import annotations
from itertools import product
import json
import random
from pathlib import Path


def subs(mask: int, of: int) -> bool:
    return (mask & ~of) == 0


def attractor(n, S, G, end):
    assert subs(G, S)
    T = G
    levels = [G]
    while True:
        more = 0
        for z in range(n):
            if S >> z & 1 and any(succ and subs(succ, T) for succ in end[z]):
                more |= 1 << z
        new = T | more
        if new == T:
            break
        T = new
        levels.append(T)
    return T, levels


def viable(n, T, run):
    L = T
    levels = [L]
    while True:
        new = 0
        for z in range(n):
            if L >> z & 1 and any(succ and subs(succ, L) for succ in run[z]):
                new |= 1 << z
        if new == L:
            break
        L = new
        levels.append(L)
    return L, levels


def all_policies(cat):
    """Enumerate every positional policy with None for missing actions."""
    return product(*[row if row else (None,) for row in cat])


def reaches_goal_under_policy(n, S, G, policy, z):
    # Non-goal frontier: if the n-step frontier is nonempty, some
    # branch has length n without reaching G; a finite positional
    # winning policy cannot have a reachable non-goal cycle.
    frontier = (1 << z) & ~G
    if frontier == 0:
        return bool((1 << z) & G)
    for _ in range(n):
        nxt = 0
        for v in range(n):
            if not (frontier >> v & 1):
                continue
            if not (S >> v & 1) or policy[v] is None or policy[v] == 0:
                return False
            nxt |= policy[v]
        if nxt & ~S:
            return False
        frontier = nxt & ~G
        if frontier == 0:
            return True
    return False


def brute_ending(n, S, G, end):
    win = G
    for policy in all_policies(end):
        for z in range(n):
            if reaches_goal_under_policy(n, S, G, policy, z):
                win |= 1 << z
    return win


def stays_in_safe_ending_region(n, S, target, policy, z):
    reached = 0
    pending = 1 << z
    while pending:
        if pending & ~(S & target):
            return False
        new = pending & ~reached
        if not new:
            break
        reached |= new
        pending = 0
        for v in range(n):
            if new >> v & 1:
                if policy[v] is None or policy[v] == 0:
                    return False
                pending |= policy[v]
    return True


def brute_joint(n, S, endwin, run):
    joint = 0
    for policy in all_policies(run):
        for z in range(n):
            if stays_in_safe_ending_region(n, S, endwin, policy, z):
                joint |= 1 << z
    return joint


def test_one(n, S, G, run, end):
    # The stated safe-hold premise is implemented literally.
    end = [tuple(sorted(set(cat) | ({1 << z} if G >> z & 1 else set()))) for z, cat in enumerate(end)]
    T, tlevels = attractor(n, S, G, end)
    L, llevels = viable(n, T, run)
    Talt = brute_ending(n, S, G, end)
    Lalt = brute_joint(n, S, Talt, run)
    if T != Talt or L != Lalt:
        raise AssertionError({'n':n,'S':S,'G':G,'run':run,'end':end,
                              'T':T,'Talt':Talt,'L':L,'Lalt':Lalt})
    assert len(tlevels) <= n+1
    assert len(llevels) <= n+1
    # Full rank witness: a winning ending action decreases rank on ALL its successors.
    rank = {}
    for k, layer in enumerate(tlevels):
        for z in range(n):
            if layer >> z & 1 and z not in rank:
                rank[z] = k
    for z, k in rank.items():
        if k == 0:
            assert G >> z & 1
            continue
        assert any(succ and all(rank.get(v, n+1) < k for v in range(n) if succ >> v & 1) for succ in end[z])
    return T,L


def main():
    counts = {'exhaustive_n2':0,'random_n3':0,'random_n4':0}
    distributions = {}
    # Exhaust ALL two-state systems with one optional running and ending
    # action at each state, including every safe/goal subset.
    n=2
    opts=tuple(range(1<<n))
    for slots in product(opts,repeat=2*n):
        run=[(slots[z],) if slots[z] else () for z in range(n)]
        end=[(slots[n+z],) if slots[n+z] else () for z in range(n)]
        for statuses in product(range(3),repeat=n):
            S=sum((1<<z) for z,s in enumerate(statuses) if s in (1,2))
            G=sum((1<<z) for z,s in enumerate(statuses) if s==2)
            T,L=test_one(n,S,G,run,end)
            counts['exhaustive_n2']+=1
            distributions[(T,L)]=distributions.get((T,L),0)+1
    rng=random.Random(834227)
    for n,repeat,key in [(3,4000,'random_n3'),(4,2000,'random_n4')]:
        masks=list(range(1,1<<n))
        for _ in range(repeat):
            states=[rng.choice((0,1,2)) for _ in range(n)]
            S=sum((1<<z) for z,s in enumerate(states) if s>=1)
            G=sum((1<<z) for z,s in enumerate(states) if s==2)
            run=[]; end=[]
            for _z in range(n):
                ar=rng.randrange(3); ae=rng.randrange(3)
                run.append(tuple(rng.sample(masks,ar)))
                end.append(tuple(rng.sample(masks,ae)))
            test_one(n,S,G,run,end)
            counts[key]+=1
    # Counterexamples with 3 states. z0 safe forever but not endable;
    # z1 can end immediately but its only running successor is z0;
    # z2 is goal and has a safe hold.
    S=0b111; G=0b100
    run=[(0b001,), (0b001,), (0b100,)]
    end=[(),(0b100,),(0b100,)]
    T,L=test_one(3,S,G,run,end)
    assert T==0b110 and L==0b100, (T,L)
    # Target that seems superficially safe but cannot be ended: n=1.
    assert test_one(1,1,0,[(1,)],[()]) == (0,0)
    results={
      'purpose':'Core 8.3 fixed point versus explicit positional-policy enumeration',
      'assurance':'finite exact checks only; not Lean theorem proving or an independent mathematical proof',
      'counts':counts,
      'total_checked_cases':sum(counts.values())+2,
      'two_state_winning_pair_distribution':{f'{t}:{l}':v for (t,l),v in sorted(distributions.items())},
      'counterexample':{'S':S,'G':G,'T':T,'L':L,'meaning':'state 1 can end now but cannot run without losing ending capability'},
      'verified_properties':['least sure-ending attractor equals exhaustive positional ending-policy outcome',
                             'greatest safe-running invariant equals exhaustive positional running-policy outcome',
                             'every positive-rank ending state has an action with all successors at lower first-entry rank'],
      'passed':True,
      'seed_n3_n4':834227
    }
    out=Path(__file__).resolve().parents[1]/'verification'/'core83_exact_checks.json'
    out.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':
    main()

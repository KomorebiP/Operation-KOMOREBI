#!/usr/bin/env python3
"""Bounded exact checks of certificate revision and vector-resource contracts."""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product, combinations
from pathlib import Path
import json
from revision_contract import *

ROOT = Path(__file__).resolve().parents[1]
GROUPS = []
N = 0

def require(condition: bool) -> None:
    global N
    N += 1
    if not condition:
        raise AssertionError('Finite revision assertion failed.')

def rejected(call) -> None:
    try:
        call()
    except (ValueError, KeyError, TypeError, IndexError):
        require(True)
    else:
        require(False)

def group(name, domain, f):
    global N
    before = N
    f()
    GROUPS.append({'name': name, 'domain': domain, 'assertions': N-before})


def exact_check(view, witness):
    if witness != view:
        raise ValueError('Witness does not equal the specified finite local value.')


def dag_cases():
    for n in range(1, 5):
        edges = list(combinations(range(n), 2))
        for mask in range(1 << len(edges)):
            parents = [[] for _ in range(n)]
            for j, (a, b) in enumerate(edges):
                if mask >> j & 1:
                    parents[b].append(str(a))
            specs = tuple(Obligation(str(i), (f'x{i}',), tuple(parents[i])) for i in range(n))
            state = {f'x{i}': 0 for i in range(n)}
            certs = {}; checks = {str(i): exact_check for i in range(n)}
            for s in specs:
                certs[s.name] = issue(s, state, {k: state[k] for k in s.dependencies}, certs, exact_check)
            for changed_bits in range(1 << n):
                changed = {f'x{i}' for i in range(n) if changed_bits >> i & 1}
                revised = {k: int(k in changed) for k in state}
                closure = invalidation_closure(specs, changed)
                # Independently propagate forward along raw adjacency, not registry order.
                direct = {str(i) for i in range(n) if f'x{i}' in changed}
                reach = set(direct)
                while True:
                    extra = {str(b) for a, b in edges if (mask >> edges.index((a, b)) & 1) and str(a) in reach}
                    new = reach | extra
                    if new == reach:
                        break
                    reach = new
                require(closure == frozenset(reach))
                results = check_bundle(specs, revised, certs, checks)
                for s in specs:
                    require((results[s.name]['status'] == 'VALID') == (s.name not in closure))
                # Removing all stale evidence never creates a valid descendant.
                reduced = {k: c for k, c in certs.items() if k not in closure}
                results = check_bundle(specs, revised, reduced, checks)
                for s in specs:
                    require((results[s.name]['status'] == 'VALID') == (s.name not in closure))


def topology_errors():
    rejected(lambda: topological_order((Obligation('a',(),('a',)),)))
    rejected(lambda: topological_order((Obligation('a',(),('b',)), Obligation('b',(),('a',)))))
    rejected(lambda: topological_order((Obligation('a',(),('missing',)),)))
    rejected(lambda: topological_order((Obligation('a',()), Obligation('a',()))))
    rejected(lambda: topological_order((Obligation('',()),)))
    rejected(lambda: topological_order((Obligation('a',('x','x')),)))
    require(topological_order((Obligation('b',(),('a',)), Obligation('a',()))) == ('a','b'))


def binding_errors():
    specs = (Obligation('a', ('x','y')), Obligation('b', ('x',), ('a',)))
    state = {'x':0,'y':1}; checks={'a':exact_check,'b':exact_check}
    a=issue(specs[0],state,state,{},exact_check)
    b=issue(specs[1],state,{'x':0},{'a':a},exact_check)
    certs={'a':a,'b':b}
    for wrong in [replace(a, bindings=()), replace(a, bindings=a.bindings[:1]),
                  replace(a, witness=canonical({'x':0,'y':0})),
                  replace(a, bindings=a.bindings + (('unrequested',canonical(1)),))]:
        out=check_bundle(specs,state,{'a':wrong,'b':b},checks)
        require(out['a']['status']=='REJECTED')
        require(out['b']['status']=='BLOCKED')
    out=check_bundle(specs,{'x':0},certs,checks)
    require(out['a']['status']=='STALE' and out['b']['status']=='BLOCKED')
    out=check_bundle(specs,state,{'a':a,'b':replace(b,parent_seals=(('a','0'*64),))},checks)
    require(out['b']['status']=='BLOCKED')
    rejected(lambda: issue(specs[1],state,{'x':0},{},exact_check))


def serialization():
    require(canonical({'b':1,'a':[2,3]})==canonical({'a':(2,3),'b':1}))
    require(canonical(True)!=canonical(1))
    require(canonical('1')!=canonical(1))
    for obj in (1.0, float('nan'), float('inf'), {1:'bad'}, Q(1,2), object()):
        rejected(lambda obj=obj: canonical(obj))
    c=Certificate('a',(('x',canonical(1)),),(),canonical({'accepted':True}))
    require(c.seal()==replace(c).seal())
    require(c.seal()!=replace(c,witness=canonical({'accepted':False})).seal())


def explicit_incomplete_contract():
    # Successful negative control: declared dependencies are not self-authenticating.
    spec=Obligation('claim',('visible',));before={'visible':0,'hidden':0}
    c=issue(spec,before,{'visible':0},{},exact_check)
    after={'visible':0,'hidden':1}
    out=check_bundle((spec,),after,{'claim':c},{'claim':exact_check})
    require(out['claim']['status']=='VALID')
    require(after['visible']!=after['hidden'])
    require(invalidation_closure((spec,),{'hidden'})==frozenset())


def vector_dominance():
    prices=tuple(product((Q(0),Q(1,2),Q(1)),repeat=3))
    for delta in product(range(-2,3),repeat=3):
        # Contains every basis vector, so this finite test is an exact discriminator
        # for the specified vector; the general proof is separate.
        require(all(priced_saving(delta,w)>=0 for w in prices)==all(x>=0 for x in delta))
        for j in range(3):
            basis=tuple(int(i==j) for i in range(3))
            require(priced_saving(delta,basis)==delta[j])


def workload_sums():
    for setup in product(range(3),repeat=2):
        for row1 in product(range(-1,2),repeat=2):
            for row2 in product(range(-1,2),repeat=2):
                for counts in product(range(3),repeat=2):
                    actual=net_saving(setup,(row1,row2),counts)
                    expanded=[tuple(Q(-v) for v in setup)]
                    expanded += [tuple(map(Q,row1))]*counts[0]+[tuple(map(Q,row2))]*counts[1]
                    expected=tuple(sum(v[j] for v in expanded) for j in range(2))
                    require(actual==expected)


def convex_prices():
    vertices=((Q(1),Q(0)),(Q(0),Q(2)),(Q(1),Q(1)))
    for delta in product(range(-3,4),repeat=2):
        lo=price_polytope_margin(delta,vertices)
        require(lo==min(priced_saving(delta,w) for w in vertices))
        for a in range(5):
            for b in range(5-a):
                c=4-a-b
                w=tuple((a*vertices[0][j]+b*vertices[1][j]+c*vertices[2][j])/4 for j in range(2))
                require(priced_saving(delta,w)>=lo)


def scalar_break_even():
    for setup in range(11):
        for numerator in range(1,11):
            for denominator in range(1,6):
                gain=Q(numerator,denominator)
                first=int(Q(setup)/gain)+1
                require(first*gain-setup>0)
                require((first-1)*gain-setup<=0)


def cost_controls():
    delta=(Q(1552),Q(1552),Q(-1868))
    require(priced_saving(delta,(1,1,1))==1236)
    require(priced_saving(delta,(0,0,1))==-1868)
    require(priced_saving(delta,(1,0,1))==-316)
    # A setup charge is not hidden by a per-use positive margin.
    require(net_saving((0,0,2000),(delta,),[1])==(Q(1552),Q(1552),Q(-3868)))
    require(priced_saving(net_saving((0,0,2000),(delta,),[1]),(1,1,1))==-764)
    require(priced_saving(net_saving((0,0,2000),(delta,),[2]),(1,1,1))==472)
    for call in (
        lambda: net_saving((),(),()), lambda: net_saving((-1,),((1,),),(1,)),
        lambda: net_saving((0,),((1,2),),(1,)), lambda: net_saving((0,),((1,),),(-1,)),
        lambda: net_saving((0,),((1,),),(True,)),lambda: priced_saving((1,),(-1,)),
        lambda: price_polytope_margin((1,),()),
    ):
        rejected(call)


def main():
    group('declared_dependency_invalidation','Every forward-labelled DAG on one through four nodes; every changed-input subset; independent reachability and deleted-evidence comparison.',dag_cases)
    group('dependency_topology_negative_controls','Self-loop, two-node cycle, missing parent, duplicate names/dependencies and reverse input order.',topology_errors)
    group('binding_and_evidence_negative_controls','Missing fields, changed witness, extra binding, missing input and incorrect parent seal.',binding_errors)
    group('exact_snapshot_and_content_identifiers','Canonical JSON, bool/integer distinction, unsupported inexact values, content changes.',serialization)
    group('undeclared_dependency_counterexample','One intentionally incomplete registry. Passing its stated check does not establish the unrepresented claim.',explicit_incomplete_contract)
    group('nonnegative_price_duality','All three-dimensional integer savings vectors in [-2,2]^3; prices in {0,1/2,1}^3 and basis-vector separators.',vector_dominance)
    group('additive_workload_accounting','Two-dimensional setup in {0,1,2}^2, two saving types in {-1,0,1}^2, counts in {0,1,2}^2; expanded event sums.',workload_sums)
    group('finite_price_polytope_extrema','Two-dimensional savings [-3,3]^2; three price vertices; every quarter-grid barycentric combination.',convex_prices)
    group('strict_scalar_repayment_threshold','Setup 0..10, positive gains p/q with p=1..10 and q=1..5.',scalar_break_even)
    group('weighted_model_prices_and_invalid_budgets','Recorded weighted-search deltas, separate price regimes, explicit setup, and malformed vectors.',cost_controls)
    report={'status':'PASS','groups':GROUPS,'assertions':N,
            'non_claims':['No independent proof kernel or origin authentication.','Declared dependencies need independent semantic justification.','Event counts do not identify universal hardware exchange rates.']}
    (ROOT/'validation/revision_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(GROUPS)} groups and {N:,} exact assertions.')
if __name__=='__main__':main()

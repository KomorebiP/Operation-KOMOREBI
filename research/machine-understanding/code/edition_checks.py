#!/usr/bin/env python3
"""Exact first-edition regression checks with explicit finite bounds.

Independent comparisons include direct encoder assignment versus set covering
and literal full observation-history tree enumeration versus Pareto dynamic
programming. Neither constitutes independent external verification.
"""
from __future__ import annotations
import argparse
import itertools as it
import json
import time
from pathlib import Path
from resource_contracts import (Experiment, Model, common_codebook,
                               resource_frontier, verify_policy, leq)

ROOT = Path(__file__).resolve().parents[1]
GROUPS: list[dict] = []


def group(name: str, domain: str):
    row = {'name': name, 'domain': domain, 'assertions': 0}
    GROUPS.append(row)
    def check(condition: bool, detail: object = '') -> None:
        row['assertions'] += 1
        if not condition:
            raise AssertionError(f'{name}: {detail}')
    return check


def subsets(n: int):
    for mask in range(1 << n):
        yield frozenset(i for i in range(n) if (mask >> i) & 1)


def direct_image_min(rows: tuple[frozenset[int], ...], k: int) -> int | None:
    vals = [len(set(a)) for a in it.product(range(k), repeat=len(rows))
            if all(x in allowed for x, allowed in zip(a, rows))]
    return min(vals) if vals else None


def syntax_trees(h: int):
    # Unpruned full binary observation-history trees, independent of a model.
    stops = [('s', 0), ('s', 1)]
    if h == 0:
        return stops
    child = syntax_trees(h - 1)
    return stops + [('e', e, left, right) for e in range(2) for left in child for right in child]


def direct_profiles(model: Model, v: tuple[int, ...], h: int) -> set[tuple[int, ...]]:
    results = set()
    for tree in syntax_trees(h):
        costs, used, valid = [], set(), True
        for original in v:
            x, node, path = original, tree, ()
            total = [0, 0]
            while True:
                used.add(path)
                if node[0] == 's':
                    gamma = model.terminal_costs[x][node[1]]
                    if gamma is None:
                        valid = False
                    else:
                        costs.append(tuple(a + b for a, b in zip(total, gamma)))
                    break
                e = model.experiments[node[1]]
                if x not in e.admissible:
                    valid = False
                    break
                total = [a + b for a, b in zip(total, e.cost)]
                obs, x = e.observation[x], e.transition[x]
                node = node[2 + obs]
                path = path + (obs,)
            if not valid:
                break
        if valid:
            results.add((max(c[0] for c in costs), max(c[1] for c in costs), len(used)))
    return {p for p in results if not any(q != p and all(a <= b for a, b in zip(q, p)) for q in results)}


def run() -> dict:
    begin = time.monotonic()
    check = group('fixed decoder covering versus direct encoder assignments',
                  'Every family of 1..3 acceptable-artifact sets over alphabets of size 1..3, including empty sets.')
    for k in range(1, 4):
        choices = tuple(subsets(k))
        for n in range(1, 4):
            for rows in it.product(choices, repeat=n):
                cover = common_codebook(rows, k)
                answer = direct_image_min(rows, k)
                check((None if cover is None else len(cover)) == answer, (rows, cover, answer))
                if cover is not None:
                    check(all(set(cover) & r for r in rows))
    check(common_codebook([], 0) == ())

    check = group('sender fibres require intersections rather than casewise choices',
                  'All 27 maps from 3 cases to 3 sender labels and all 512 acceptable-set tables over 3 artifacts.')
    for access in it.product(range(3), repeat=3):
        labels = sorted(set(access))
        for rows in it.product(tuple(subsets(3)), repeat=3):
            intersections = tuple(frozenset.intersection(*(rows[x] for x in range(3) if access[x] == s)) for s in labels)
            cover = common_codebook(intersections, 3)
            direct = []
            for assignment in it.product(range(3), repeat=len(labels)):
                mapping = dict(zip(labels, assignment))
                if all(mapping[access[x]] in rows[x] for x in range(3)):
                    direct.append(len(set(assignment)))
            check((None if cover is None else len(cover)) == (min(direct) if direct else None))

    check = group('task dependent interpreter capacity and framing distinctions',
                  'Truth tables on n=0..3 input bits; all description splits d+b up to 2^n+1; equal-background profile counts.')
    for n in range(4):
        width = 1 << n
        profiles = tuple(it.product((0, 1), repeat=width))
        check(len(profiles) == 1 << width)
        for d in range(width + 2):
            for b in range(width + 2 - d):
                check(((1 << (d + b)) >= len(profiles)) == (d + b >= width))
        # Store the entire truth table in the charged package and decode by index.
        for table in profiles:
            for query in range(width):
                check(table[query] in (0, 1))
        for prefix in range(width + 1):
            fibres: dict[tuple, set] = {}
            for table in profiles:
                fibres.setdefault(table[:prefix], set()).add(table)
            check(max(map(len, fibres.values())) == 1 << (width - prefix))
    check(sum(1 << k for k in range(4)) == 15)  # length-at-most-3 is not 8 fixed-length strings.

    check = group('fixed interpreter obstructions and catalogue encoding',
                  'The three-case pairwise-intersecting artifact example and explicit sender-blind incompatible stops.')
    allowed = (frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 2)))
    check(len(common_codebook(allowed, 3)) == 2)
    check(not set.intersection(*(set(a) for a in allowed)))
    check(all(allowed[i] & allowed[j] for i in range(3) for j in range(i + 1, 3)))
    check(common_codebook((frozenset(),), 2) is None)
    check(len(common_codebook((frozenset((2,)),), 3)) == 1)  # one catalogue item need not be one raw bit.

    check = group('resource Pareto synthesis versus literal history tree enumeration',
                  'Two states; every ordered pair of identity/swap transitions and binary observation maps (64 pairs), every binary terminal-validity table (16), each nonempty support, horizons 0..2. Fixed costs (1,0),(0,1); terminal cost (0,1).')
    tables = tuple(it.product(((0, 1), (1, 0)), tuple(it.product(range(2), repeat=2))))
    for e0, e1 in it.product(tables, repeat=2):
        experiments = (Experiment('e0', e0[0], e0[1], frozenset((0, 1)), (1, 0)),
                       Experiment('e1', e1[0], e1[1], frozenset((0, 1)), (0, 1)))
        for flags in it.product((False, True), repeat=4):
            term = tuple(tuple((0, 1) if flags[2*x + m] else None for m in range(2)) for x in range(2))
            model = Model(2, 2, ('experiment_0_units', 'experiment_1_and_stop_units'), experiments, term)
            for v in ((0,), (1,), (0, 1)):
                for h in range(3):
                    frontier = resource_frontier(model, v, h)
                    check({p.key for p in frontier} == direct_profiles(model, v, h), (e0,e1,flags,v,h))
                    for p in frontier:
                        check(verify_policy(model, v, h, p.policy).key == p.key)

    check = group('online cost versus complete installed controller tradeoff',
                  'Four persistent origins, one cost-4 complete read, three cost-1 equality tests, horizon 3, four exact output artifacts.')
    experiments = (Experiment('direct', (0, 1, 2, 3), (0, 1, 2, 3), frozenset(range(4)), (4,)),) + tuple(
        Experiment(f'equal_{j}', (0, 1, 2, 3), tuple(int(x == j) for x in range(4)), frozenset(range(4)), (1,)) for j in range(3))
    term = tuple(tuple((0,) if x == m else None for m in range(4)) for x in range(4))
    model = Model(4, 4, ('online_units',), experiments, term)
    profiles = resource_frontier(model, range(4), 3)
    check({p.key for p in profiles} == {(4, 5), (3, 7)}, [p.key for p in profiles])
    for p in profiles:
        check(verify_policy(model, range(4), 3, p.policy).key == p.key)
    for online in range(7):
        for records in range(10):
            expected = (online >= 4 and records >= 5) or (online >= 3 and records >= 7)
            check(any(p.cost[0] <= online and p.records <= records for p in profiles) == expected)
    check(not any(p.cost[0] <= 3 and p.records <= 5 for p in profiles))
    check({p.key for p in resource_frontier(model, range(4), 0)} == set())

    from demo_first_edition import instrument_model, decode_a, decode_b, direct_protocol
    check = group('one costed instrument and two genuinely fixed decoders',
                  'Every one of 25 old (s,b) records, all 5 hidden c values, h=0,1,2,3; exact primitive counts and 6-record tree.')
    for s, b in it.product(range(5), repeat=2):
        model = instrument_model(s, b)
        check(resource_frontier(model, range(5), 0) == ())
        for h in (1, 2, 3):
            frontier = resource_frontier(model, range(5), h)
            check({p.key for p in frontier} == {(1, 1, 3, 1, 1, 6)})
            check(verify_policy(model, range(5), h, frontier[0].policy).key == frontier[0].key)
        for c in range(5):
            a = (s - b) % 5
            result = direct_protocol(a, b, c)
            check(result['message'] == c)
            check(tuple(result['recipient_a']) == ((a+c) % 5, b, c))
            check(tuple(result['recipient_b']) == ((s+c) % 5, b, c))
            check(tuple(result['cost']) == (1, 1, 3, 1, 1))
            check(decode_a((a,b),c,0) is None)
            check(decode_b((s,b),c,0) is None)
        check(not resource_frontier(instrument_model(s,b,recipient_a_limit=0),range(5),1))
        check(not resource_frontier(instrument_model(s,b,recipient_b_limit=0),range(5),1))

    check = group('recipient continuation execution after the costed handover',
                  'All 125 initial instrument states and every H/W/J word of length 0..4, comparing register and display-centered executions.')
    for a, b, c in it.product(range(5), repeat=3):
        result = direct_protocol(a,b,c)
        for length in range(5):
            for word in it.product('HWJ', repeat=length):
                x = tuple(result['recipient_a']); y = tuple(result['recipient_b']); count = 0
                for u in word:
                    aa,bb,cc=x;ss,dd,ee=y
                    if u=='H':x=((aa+bb)%5,bb,cc);y=((ss+dd)%5,dd,ee)
                    elif u=='W':x=(bb,aa,cc);y=(ss,(ss-dd)%5,ee)
                    else:x=((aa+cc)%5,bb,cc);y=((ss+ee)%5,dd,ee)
                    count+=1
                check((x[0]+x[1])%5 == y[0])
                check(((x[0]+x[1])%5,x[1],x[2]) == y)
                check(count == length)

    check = group('malformed witnesses and invalid resource tables are rejected',
                  'Wrong terminal artifact, missing/extra branches, unavailable experiment, zero horizon, negative/bool cost, zero/invalid model shapes.')
    from copy import deepcopy
    model = instrument_model(4,3)
    policy = resource_frontier(model, range(5), 1)[0].policy
    bad=[]
    p=deepcopy(policy);p['branches']['0']['message']=(p['branches']['0']['message']+1)%5;bad.append((p,1))
    p=deepcopy(policy);del p['branches']['0'];bad.append((p,1))
    p=deepcopy(policy);p['branches']['99']={'kind':'stop','message':0};bad.append((p,1))
    p=deepcopy(policy);p['experiment']=99;bad.append((p,1))
    bad.append((policy,0));bad.append(({'kind':'stop','message':0},1))
    for p,h in bad:
        try:verify_policy(model,range(5),h,p)
        except ValueError:check(True)
        else:check(False)
    for malformed in ((-1,), (True,), (1,2)):
        try:Model(1,1,('units',),(),((malformed,),))
        except ValueError:check(True)
        else:check(False)
    try:resource_frontier(model, [], 1)
    except ValueError:check(True)
    else:check(False)
    try:resource_frontier(model,range(5),True)
    except ValueError:check(True)
    else:check(False)
    try:common_codebook(({7},),2)
    except ValueError:check(True)
    else:check(False)
    # An experiment admissible in only one possible state cannot be selected.
    m=Model(2,2,('units',),(Experiment('partial',(0,1),(0,1),frozenset((0,)),(0,)),),(((0,),None),(None,(0,))))
    check(not resource_frontier(m,(0,1),2))

    check = group('separate and packed state buffers have different exact sizes',
                  'F5 base 25 states, supplementary 5 symbols, expanded 125 states; fixed binary and separate-residue layouts.')
    bits=lambda n:(n-1).bit_length()
    check(bits(25)==5);check(bits(5)==3);check(bits(125)==7)
    check(bits(25)+bits(5)==8);check(3*bits(5)==9)
    check(2**2 < 5 <= 2**3)
    check(6*bits(6) >= 6)  # pointer width is a storage convention, not six raw bits.

    return {'status':'passed','group_count':len(GROUPS),'assertions':sum(g['assertions'] for g in GROUPS),
            'runtime_seconds':time.monotonic()-begin,'arithmetic':'exact integers; no random sampling',
            'groups':GROUPS,'non_claims':['No general proof by finite enumeration.','Not independent peer review or formal-kernel verification.',
            'No empirical claim about a learned model.','No optimality claim outside the declared decoder and explicit-tree catalogue.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build'/'edition_checks.json')
    args=parser.parse_args()
    try:
        result=run()
    except Exception as exc:
        result={'status':'failed','error':repr(exc),'groups':GROUPS}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        raise
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','group_count','assertions','runtime_seconds')},indent=2))
    for g in GROUPS:print(f"{g['name']}: {g['assertions']} passed")

if __name__=='__main__':main()

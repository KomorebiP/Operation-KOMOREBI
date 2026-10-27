#!/usr/bin/env python3
"""Finite proof-field checker and an independent model-enumeration oracle.

The lower-level rules can be cyclic. Unknown addresses and Boolean addresses
are rejected. This is a finite Python check, not a proof of a parser or producer.
"""
from __future__ import annotations
from itertools import product
from pathlib import Path
import json

class Rejected(ValueError):pass

def subsets(n):
    return [frozenset(i for i in range(n) if mask & 1<<i) for mask in range(1<<n)]

def replay(n,rules,seeds,trace,strict=False):
    known=set(seeds)
    for address in trace:
        if type(address) is not int or not 0<=address<len(rules):raise Rejected('bad rule address')
        premises,conclusion=rules[address]
        if not premises<=known:raise Rejected('missing premise')
        if strict and conclusion in known:raise Rejected('repeated conclusion')
        known.add(conclusion)
    return frozenset(known)

def produce(n,rules,seeds):
    known=set(seeds); trace=[]
    while True:
        old=len(known)
        for j,(premises,conclusion) in enumerate(rules):
            if premises<=known and conclusion not in known:
                known.add(conclusion);trace.append(j)
        if len(known)==old:return frozenset(known),tuple(trace)
        if len(trace)>n:raise AssertionError('strict insertion bound failed')

def is_closed(rules,known):
    return all(not premises<=known or conclusion in known for premises,conclusion in rules)

def check_closure(n,rules,seeds,trace,reported):
    try:
        got=replay(n,rules,seeds,trace,True)
    except Rejected:return False
    return got==reported and is_closed(rules,reported)

def main():
    counts={'two_node_fields':0,'protected_requests':0,'model_sets_enumerated':0,
            'strict_traces':0,'replay_append_checks':0,'mutated_claims':0,
            'negative_controls':0,'three_node_rule_lists':0}
    for n,mode in [(2,'all'),(3,'two_rows')]:
        ss=subsets(n); all_rules=tuple((p,c) for p in ss for c in range(n))
        if mode=='all':
            families=(tuple(all_rules[j] for j in range(len(all_rules)) if mask & 1<<j)
                      for mask in range(1<<len(all_rules)))
        else:
            families=(tuple(all_rules[j] for j in js)
                      for size in range(3) for js in product(range(len(all_rules)),repeat=size))
        for rules in families:
            if n==3:counts['three_node_rule_lists']+=1
            for seeds in ss:
                closure,trace=produce(n,rules,seeds)
                models=[b for b in ss if seeds<=b and is_closed(rules,b)]
                counts['model_sets_enumerated']+=len(ss)
                oracle=frozenset.intersection(*models)
                assert closure==oracle and len(trace)<=n-len(seeds)
                assert check_closure(n,rules,seeds,trace,closure)
                counts['strict_traces']+=1
                if n==2:counts['two_node_fields']+=1
                for cut in range(len(trace)+1):
                    first=replay(n,rules,seeds,trace[:cut])
                    assert replay(n,rules,first,trace[cut:])==closure
                    counts['replay_append_checks']+=1
                for node in range(n):
                    altered=closure ^ frozenset([node])
                    assert not check_closure(n,rules,seeds,trace,altered)
                    counts['mutated_claims']+=1
                for forbidden in ss:
                    feasible=any(not b & forbidden for b in models)
                    assert feasible==(not closure & forbidden)
                    if not feasible:
                        target=next(iter(closure & forbidden))
                        assert target in replay(n,rules,seeds,trace)
                    counts['protected_requests']+=1
    # Distinct failure mechanisms from the four-node worked example.
    rules=((frozenset([0]),1),(frozenset([1]),2));seeds=frozenset([0])
    assert replay(4,rules,seeds,(0,))==frozenset([0,1])
    assert not check_closure(4,rules,seeds,(0,),frozenset([0,1]))
    assert is_closed(rules,frozenset(range(4)))
    assert not check_closure(4,rules,seeds,(0,1),frozenset(range(4)))
    counts['negative_controls']+=2
    for trace in [(True,),(-1,),(2,),('0',),(1,)]:
        try:replay(4,rules,seeds,trace)
        except Rejected:counts['negative_controls']+=1
        else:raise AssertionError(('invalid trace accepted',trace))
    assert replay(4,rules,seeds,(0,0))==frozenset([0,1])
    try:replay(4,rules,seeds,(0,0),True)
    except Rejected:counts['negative_controls']+=1
    else:raise AssertionError('strict duplicate accepted')
    # No circular self-justification without a seed.
    cyc=((frozenset([0]),1),(frozenset([1]),0))
    assert produce(2,cyc,frozenset())[0]==frozenset();counts['negative_controls']+=1
    result={'status':'PASS','counts':counts,
            'scope':'all rule subsets on two nodes; ordered rule lists of length at most two on three nodes, all seed/forbidden subsets; separate four-node and malformed-input controls',
            'oracle':'enumerate every seeded closed model and intersect them; independent of the forward producer',
            'assurance':'same-project finite Python reference checks, not a new kernel proof or universal parser verification'}
    out=Path(__file__).resolve().parents[1]/'verification'/'proof_fields.json'
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

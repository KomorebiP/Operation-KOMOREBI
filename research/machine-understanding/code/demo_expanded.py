#!/usr/bin/env python3
"""Reproduce the finite acquisition, Bayesian, and recipient examples.

No empirical data or trained models are used. Defaults to printing a JSON
record. Pass --output PATH to save the same record for a reproducible review.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
from understanding import (Experiment, acquisition, channel, chromatic_number,
                           explanation_graph, policy_trace, posterior,
                           reconstruct_channel, compose, color_graph)


def build_record() -> dict:
    states = list(product(range(5), repeat=3))
    idx = {x: j for j, x in enumerate(states)}
    transforms = [lambda a,b,c: ((a+b)%5,b,c),
                  lambda a,b,c: (b,a,c),
                  lambda a,b,c: ((a+c)%5,b,c)]
    experiments = []
    for name, fn, cost in zip(('H','W','J'), transforms, (1,1,2)):
        nxt = [fn(*x) for x in states]
        experiments.append(Experiment(name, tuple(idx[x] for x in nxt),
                           tuple((x[0]+x[1])%5 for x in nxt), F(cost)))
    initial = frozenset(idx[(3,4,c)] for c in range(5))
    target = tuple(((a+b)%5,b,c) for a,b,c in states)
    cost, witness = acquisition(target, experiments, initial, 2)
    assert cost == 2 and witness['name'] == 'J'
    traces = []
    for x in sorted(initial):
        final, paid, depth = policy_trace(x, witness, experiments)
        assert paid == 2 and depth == 1
        traces.append({'before': states[x], 'after': states[final],
                       'record': target[final], 'cost': str(paid)})

    likelihood = channel([[F(3,4) if c==y else F(1,16)
                           for y in range(5)] for c in range(5)])
    parity = channel([[int(z == y%2) for z in range(2)] for y in range(5)])
    coarse = compose(likelihood, parity)
    rows = []
    for n in range(4):
        fine = posterior([F(1,5)]*5, [likelihood[c][2]**n for c in range(5)])
        even = posterior([F(1,5)]*5, [coarse[c][0]**n for c in range(5)])
        assert fine is not None and even is not None
        assert fine[2] == F(12**n,12**n+4)
        rows.append({'fresh_report_count': n, 'full_symbol_c2': str(fine[2]),
                     'even_only_c2': str(even[2])})
    raw = channel([[likelihood[c][y]*flag for y in range(5)
                    for flag in (F(1,3),F(2,3))] for c in range(5)])
    drop_flag = channel([[int(z==j//2) for z in range(5)] for j in range(10)])
    assert reconstruct_channel(raw,drop_flag) is not None
    assert reconstruct_channel(likelihood,parity) is None

    bits = list(product(range(2),repeat=2))
    sender = [a^b for a,b in bits]
    backgrounds = [[a for a,b in bits], [b for a,b in bits]]
    demands = [[b for a,b in bits], [a for a,b in bits]]
    vertices,edges = explanation_graph(sender,backgrounds,demands)
    colors = color_graph(len(vertices),edges,2)
    assert colors is not None and chromatic_number(len(vertices),edges)==2
    assert len(set(sender)) < len(bits)
    decoded = [{'state': [a,b], 'artifact': a^b,
                'first_recipient_recovers_b': a^(a^b),
                'second_recipient_recovers_a': b^(a^b)} for a,b in bits]
    return {'status':'passed', 'arithmetic':'integers and fractions.Fraction',
            'acquisition': {'initial_base_record':[2,4], 'optimal_cost':str(cost),
                            'first_experiment':witness['name'],'traces':traces},
            'noisy_instrument': {'posterior_rows':rows,
                                'ancillary_flag_is_sufficient':True,
                                'parity_is_sufficient':False},
            'shared_explanation': {'message_symbols':2,'source_identifies_full_state':False,
                                   'recipient_decodings':decoded},
            'scope':'Fixed analytical constructions; not a general optimizer for noisy joint inquiry and communication.'}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    text=json.dumps(build_record(),indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    print(text,end='')

if __name__=='__main__':
    main()

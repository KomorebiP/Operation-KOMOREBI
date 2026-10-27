#!/usr/bin/env python3
"""Costed, exact instrument handover with fixed recipient programs.

The five online units are physical diagnostic calls, source modular arithmetic,
transmitted payload bits, A's modular arithmetic, and B's modular arithmetic.
They are not timings. The physical laws, interface and recipient programs are
supplied. The diagnostic protocol is fixed before the hidden c is chosen.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
from resource_contracts import Model, Experiment, resource_frontier, verify_policy
ROOT=Path(__file__).resolve().parents[1]
UNITS=('diagnostic_calls','source_modular_ops','broadcast_bits','recipient_A_modular_ops','recipient_B_modular_ops')


def residue(x):
    if type(x) is not int or not 0<=x<5:raise ValueError('Expected a residue 0..4.')
    return x


def decode_a(background, message, limit=1):
    """One installed decoder, unchanged across all 125 cases."""
    if type(limit) is not int or limit<0:raise ValueError('Nonnegative integer limit required.')
    a,b=map(residue,background);m=residue(message)
    if limit<1:return None
    return ((a+m)%5,b,m)


def decode_b(background, message, limit=1):
    if type(limit) is not int or limit<0:raise ValueError('Nonnegative integer limit required.')
    s,b=map(residue,background);m=residue(message)
    if limit<1:return None
    return ((s+m)%5,b,m)


def direct_protocol(a,b,c):
    a,b,c=map(residue,(a,b,c));s=(a+b)%5
    # Physical J plus its exact returned readout is one supplied diagnostic call.
    physical_after=((a+c)%5,b,c);new_display=(physical_after[0]+b)%5
    message=(new_display-s)%5  # one source modular subtraction
    recipient_a=decode_a((a,b),message)
    recipient_b=decode_b((s,b),message)
    return {'before':[a,b,c],'old_sender_record':[s,b],'after':list(physical_after),
            'private_report':new_display,'message':message,'fixed_length_payload':format(message,'03b'),
            'recipient_a':list(recipient_a),'recipient_b':list(recipient_b),'cost':[1,1,3,1,1]}


def instrument_model(s,b,recipient_a_limit=1,recipient_b_limit=1):
    s,b=map(residue,(s,b));a=(s-b)%5
    # 0..4 encode (before,c); 5..9 encode (after J,c). Origin remains available
    # to the formal target evaluator, not as extra information for the sender.
    transition=tuple(c+5 for c in range(5))+tuple(range(5,10))
    observation=tuple((s+c)%5 for c in range(5))*2
    experiment=Experiment('J_with_exact_report_and_encode',transition,observation,frozenset(range(5)),(1,1,0,0,0))
    rows=[]
    for phase in (0,1):
        for c in range(5):
            row=[]
            for m in range(5):
                out_a=decode_a((a,b),m,recipient_a_limit)
                out_b=decode_b((s,b),m,recipient_b_limit)
                valid=phase==1 and out_a==((a+c)%5,b,c) and out_b==((s+c)%5,b,c)
                row.append((0,0,3,1,1) if valid else None)
            rows.append(tuple(row))
    return Model(10,5,UNITS,(experiment,),tuple(rows))


def demo():
    model=instrument_model(4,3)
    front=resource_frontier(model,range(5),1)
    verified=verify_policy(model,range(5),1,front[0].policy)
    hashes={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in (ROOT/'code'/'resource_contracts.py',ROOT/'code'/'demo_first_edition.py')}
    cases=[direct_protocol(a,b,c) for a,b,c in product(range(5),repeat=3)]
    return {'status':'passed','units':UNITS,'old_record_example':[4,3],
            'cost':verified.cost,'controller_records':verified.records,'policy':verified.policy,
            'records_visited_per_execution':2,'case_count':len(cases),'cases':cases,
            'installed_source_files':hashes,
            'policy_canonical_json_bytes':len(json.dumps(verified.policy,sort_keys=True,separators=(',',':')).encode()),
            'scope':'All 125 analytical cases, fixed programs, exact diagnostic. Code bytes are recorded, not minimized. Controller record count is for one old-record fibre. No sensor-learning or neural-mechanism claim.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build'/'first_edition_demo.json')
    args=parser.parse_args();result=demo();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','units','cost','controller_records','case_count','policy_canonical_json_bytes')},indent=2))

if __name__=='__main__':main()

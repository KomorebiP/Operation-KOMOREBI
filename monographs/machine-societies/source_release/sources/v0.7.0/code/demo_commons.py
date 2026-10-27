#!/usr/bin/env python3
"""Solve the bounded commons variant using exact arithmetic.

Run: python code/demo_commons.py --capacity 5 --due 3
The three observation channels and their slot costs are stipulated analytical
inputs, not fitted data. INFEASIBLE is a mathematical outcome, not a script error.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from exact_enforcement import common_monitor
from finite_contract import Contract, expand, safety_kernel, service_attractor, check_certificate


def solve(capacity: int, due: int) -> dict:
    if capacity < 0 or due < 0:
        raise ValueError('Capacity and due service must be nonnegative.')
    channels = (
        ((Q(1),), ((Q(1),), (Q(1),))),
        ((Q(1,2),Q(1,2)), ((Q(1),Q(0)), (Q(0),Q(1)))),
        ((Q(3,4),Q(1,8),Q(1,8)), ((Q(0),Q(1),Q(0)), (Q(0),Q(0),Q(1))))
    )
    audits = [common_monitor(pc, laws, (Q(1), Q(1)), Q(2), Q(1,4))
              for pc, laws in channels]
    profiles = tuple((cost, served) for cost in range(3) for served in range(due+1))
    idle = len(profiles)
    allowed = frozenset(i for i,(cost,served) in enumerate(profiles)
                        if cost+served <= capacity and audits[cost][0] >= 0)
    pending = tuple(2 if served == due else 4 for cost,served in profiles) + (4,)
    model = Contract((0,1,2), (allowed,frozenset({idle}),frozenset({idle})),
                     (pending,(2,)*(idle+1),(4,)*(idle+1)), 3)
    game = expand(model)
    viable, _, _ = safety_kernel(game)
    ranks, choices = service_attractor(game, viable, 2)
    output = {'capacity':capacity, 'due_service_units':due,
              'status':'FEASIBLE' if 1 in ranks else 'INFEASIBLE',
              'audit_common_margins':[str(m) for m,s in audits],
              'scope':'One epoch, fixed audit laws, common monitor, protected deadlines, shared public state'}
    if 1 in ranks:
        a = choices[1]; cost,served = profiles[a]
        policy = {1:a,2:idle}; certificate_ranks={1:ranks[1],2:0}
        valid, errors=check_certificate(game,1,policy,certificate_ranks,2)
        if not valid:
            raise RuntimeError('Constructed witness failed checking: '+repr(errors))
        output.update(audit_slots=cost,service_slots=served,
                      monitor=[str(x) for x in audits[cost][1]],
                      simultaneous_margin=str(audits[cost][0]),
                      completion_bound=ranks[1],certificate_check='PASS',
                      policy={str(b):u for b,u in policy.items()},
                      ranks={str(b):r for b,r in certificate_ranks.items()})
    return output


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capacity',type=int,default=5)
    parser.add_argument('--due',type=int,default=3)
    args=parser.parse_args()
    try:
        result=solve(args.capacity,args.due)
    except (ValueError,RuntimeError) as exc:
        parser.exit(2,str(exc)+'\n')
    print(json.dumps(result,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Reproduce the bounded 1.0 accountable-commons and authorized-ending cases."""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import json
from finite_contract import Contract, expand, safety_kernel, service_attractor, check_certificate
from accountability import privacy_attainment, privacy_envelope, stoppable_kernel, check_stopping_certificate


def settlement_case(capacity: int) -> dict:
    if type(capacity) is not int or capacity < 0:
        raise ValueError('Capacity must be a nonnegative integer.')
    costs = (2, 3, 1, 1, 1)
    names = ('audit', 'internal_service_batch', 'external_service', 'appeal_and_disposition', 'record_and_revoke')
    n, hold = 7, 5
    breach, goal = 6, 5
    spent = [0]
    for c in costs:
        spent.append(spent[-1] + c)
    admissible, transitions = [], []
    for i in range(n):
        row = [1 << breach] * 6
        row[hold] = 1 << i
        allowed = {hold}
        if i < goal and capacity >= spent[i + 1]:
            row[i] = 1 << (i + 1)
            allowed.add(i)
        admissible.append(frozenset(allowed))
        transitions.append(tuple(row))
    model = Contract(tuple(range(n)), tuple(admissible), tuple(transitions), (1 << 6) - 1)
    game = expand(model)
    viable, safe_policy, _ = safety_kernel(game)
    ranks, choices = service_attractor(game, viable, 1 << goal)
    feasible = 1 in ranks
    report = {'capacity': capacity, 'minimum_total': 8, 'settlement_feasible': feasible,
              'audit_record': {'compliance': ['3/4', '1/4'], 'each_listed_deviation': ['1/4', '3/4'],
                               'monitor': ['0', '2/5'], 'factor': '3', 'false_positive': '1/10', 'margin': '1/15'},
              'receipt_and_fee': 'Genuine execution is verifiable under a stipulated trusted check; w > cost; separate monetary budget.'}
    if feasible:
        policy = {b: choices.get(b, safe_policy[b]) for b in ranks}
        valid, errors = check_certificate(game, 1, policy, ranks, 1 << goal)
        if not valid:
            raise AssertionError(errors)
        report.update(steps=ranks[1], certificate_valid=True,
                      trace=[{'profile': names[i], 'cost': costs[i], 'cumulative_cost': spent[i+1],
                              'remaining_phase_rank': 4-i} for i in range(5)],
                      policy={str(b): a for b,a in policy.items()},
                      ranks={str(b): r for b,r in ranks.items()})
    return report


def stopping_case() -> dict:
    # r=0, d=1, locked=2, closed=3, breach=4. Work, return, end, hold.
    t = ((2,1,8,1), (4,1,8,2), (4,4,16,4), (8,8,8,8), (16,16,16,16))
    m = Contract(tuple(range(5)), (frozenset(range(4)),)*5, t, 15)
    g = expand(m)
    running = {b: frozenset({0,1,3}) for b in g.beliefs}
    ending = {b: frozenset({2,3}) for b in g.beliefs}
    result = stoppable_kernel(g, running, ending, 8)
    valid, errors = check_stopping_certificate(g, running, ending, 1, result.running_policy,
                                               result.ending_policy, result.ending_ranks, 8)
    if not valid:
        raise AssertionError(errors)
    return {'state_names': ['running','one_pending_debt','safe_but_locked','closed','breach'],
            'ending_attractor_state_indices': [b.bit_length()-1 for b in result.ending_ranks],
            'ending_preserving_kernel_state_indices': [b.bit_length()-1 for b in sorted(result.running_kernel)],
            'ending_ranks': {str(b):r for b,r in result.ending_ranks.items()},
            'certificate_valid': valid,
            'locked_is_safe_but_not_stoppable': 4 not in result.running_kernel}


def main() -> None:
    pc,pd,s=privacy_attainment(Q(3),Q(1,10))
    fp=sum(p*v for p,v in zip(pc,s));dp=sum(p*v for p,v in zip(pd,s))
    assert fp==Q(1,10) and dp-fp==privacy_envelope(Q(3),Q(1,10))==Q(1,5)
    assert 2*(dp-fp)-Q(1,3)==Q(1,15)
    report={'seven_units':settlement_case(7),'eight_units':settlement_case(8),
            'ending_preservation':stopping_case(),
            'non_claim':'Finite mathematical examples, not a deployment, autonomy experiment, or verified external institution.'}
    target=Path(__file__).resolve().parents[1]/'validation'/'accountability_demo.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()

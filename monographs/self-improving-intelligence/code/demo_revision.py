#!/usr/bin/env python3
"""Replay applicability on the actual inherited equation and repair constructions.

The dependency registry and its local checker implementations are supplied.
This is a finite reference demonstration, not an agent self-editing its verifier.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import hashlib
import json

from revision_contract import Obligation, issue, check_bundle, canonical, net_saving, priced_saving
from meta_synthesis import SEMANTICS, LearnedNormalizer, verify_quotient, to_tuple
from synthesized_pruning import grammar, certify_rule
from weighted_repair_pruning import paired_repair_problem, checked_greedy_weights, verify_weights, ordered_weighted_search
from repair_calculus import Problem, Experiment, Repair, check_tree, tree_to_dict, tree_from_dict

ROOT = Path(__file__).resolve().parents[1]


def problem_record(p: Problem) -> dict:
    return {'n': p.n, 'experiments': [
        {'name': e.name, 'cost': str(e.cost), 'transitions': e.transitions} for e in p.experiments],
        'repairs': [{'name': r.name, 'cost': str(r.cost), 'good': sorted(r.good)} for r in p.repairs]}


def read_problem(s: dict) -> Problem:
    return Problem(s['n'], tuple(Experiment(e['name'], Q(e['cost']),
        tuple(None if x is None else tuple(x) for x in e['transitions'])) for e in s['experiments']),
        tuple(Repair(r['name'], Q(r['cost']), frozenset(r['good'])) for r in s['repairs']))


SPECS = (
    Obligation('equations', ('arithmetic', 'proof_implementation', 'equation_library')),
    Obligation('quotient', ('arithmetic', 'grammar', 'equation_library', 'quotient_record'), ('equations',)),
    Obligation('capacity_rule', ('rule', 'rule_implementation'), ('quotient',)),
    Obligation('repair_weights', ('problem', 'weights')),
    Obligation('controller', ('problem', 'weights', 'horizon', 'tree'), ('repair_weights',)),
    Obligation('cost_assessment', ('cost_ledger', 'prices'), ('controller',)),
)


def callbacks() -> dict:
    proof_code = (ROOT/'code/meta_synthesis.py').read_text()
    rule_code = (ROOT/'code/synthesized_pruning.py').read_text()
    def equations(s, w):
        if s['arithmetic'] != SEMANTICS or s['proof_implementation'] != proof_code:
            raise ValueError('The installed arithmetic proof implementation is not this contract.')
        LearnedNormalizer(s['equation_library'])
        if w != {'claim': 'checked_equation_library'}:
            raise ValueError('Incorrect equation claim.')
    def quotient(s, w):
        if s['arithmetic'] != SEMANTICS:
            raise ValueError('Changed arithmetic.')
        indices = verify_quotient(tuple(to_tuple(p) for p in s['grammar']),
                                  s['equation_library'], s['quotient_record'])
        if w != {'retained': len(indices)}:
            raise ValueError('Incorrect quotient witness.')
    def rule(s, w):
        if s['rule_implementation'] != rule_code:
            raise ValueError('Changed rule checker.')
        cert = certify_rule(s['rule'])
        if w != {'theorem': cert['theorem']}:
            raise ValueError('Wrong rule theorem identifier.')
    def weights(s, w):
        vals, report = verify_weights(read_problem(s['problem']), tuple(Q(v) for v in s['weights']))
        if w != {'total': str(sum(vals, Q(0)))}:
            raise ValueError('Incorrect weight total.')
    def controller(s, w):
        p = read_problem(s['problem'])
        work, size = check_tree(p, range(p.n), tree_from_dict(s['tree']), s['horizon'])
        if w != {'work': str(work), 'storage': size}:
            raise ValueError('Incorrect controller witness.')
    def cost(s, w):
        d = s['cost_ledger']
        delta = net_saving(d['setup'], d['savings'], d['multiplicities'])
        score = priced_saving(delta, s['prices'])
        if w != {'priced_margin': str(score), 'strictly_positive': score > 0}:
            raise ValueError('Incorrect conditional resource assessment.')
    return dict(zip((x.name for x in SPECS), (equations, quotient, rule, weights, controller, cost)))


def prepare():
    lib = json.loads((ROOT/'validation/learned_equations.json').read_text())
    quo = json.loads((ROOT/'validation/synthesis_quotient.json').read_text())
    p = paired_repair_problem(16)
    weights, wr = checked_greedy_weights(p)
    full, fr = ordered_weighted_search(p, 4, weights, False)
    stream, sr = ordered_weighted_search(p, 4, weights, True)
    if full != stream or stream is None:
        raise AssertionError('The common diagnostic controller changed.')
    # Unlike resource types stay separate. These are event deltas, not CPU time.
    units = ('model-record reads', 'rational additions', 'capacity comparisons')
    savings = [fr['counters'][k] - sr['counters'][k]
               for k in ('search_model_reads', 'weight_additions', 'capacity_comparisons')]
    state = {
        'arithmetic': SEMANTICS,
        'proof_implementation': (ROOT/'code/meta_synthesis.py').read_text(),
        'equation_library': lib, 'grammar': grammar(), 'quotient_record': quo,
        'rule': ('>', ('max', ('a',), ('b',)), ('c',)),
        'rule_implementation': (ROOT/'code/synthesized_pruning.py').read_text(),
        'problem': problem_record(p), 'weights': list(map(str, weights)), 'horizon': 4,
        'tree': tree_to_dict(stream),
        'cost_ledger': {'units': units, 'setup': ['0', '0', '0'], 'savings': [list(map(str, savings))],
                        'multiplicities': [1],
                        'boundary': 'Conditional weighted-search execution difference only. Shared setup and validation cancel. Certificate-management work and learned-library preparation are not included.'},
        'prices': ['1', '1', '1'],
    }
    work, size = check_tree(p, range(p.n), stream, 4)
    witnesses = {
        'equations': {'claim': 'checked_equation_library'}, 'quotient': {'retained': quo['retained_candidates']},
        'capacity_rule': {'theorem': 'prefix_capacity_v1'},
        'repair_weights': {'total': str(sum(weights, Q(0)))},
        'controller': {'work': str(work), 'storage': size},
        'cost_assessment': {'priced_margin': str(sum(savings)), 'strictly_positive': sum(savings) > 0},
    }
    certs = {}
    checks = callbacks()
    for s in SPECS:
        certs[s.name] = issue(s, state, witnesses[s.name], certs, checks[s.name])
    return state, certs, checks, {'full': fr, 'streaming': sr, 'weight_constructor': wr,
                               'resource_units': units, 'net_saving': list(map(str, savings))}


def run_demo() -> dict:
    state, certs, checks, raw = prepare()
    baseline = check_bundle(SPECS, state, certs, checks)
    if not all(v['status'] == 'VALID' for v in baseline.values()):
        raise AssertionError(baseline)
    cases = []
    for key, replacement in (
        ('arithmetic', 'bounded-word-arithmetic'),
        ('grammar', tuple(reversed(state['grammar']))),
        ('rule', ('>', ('a',), ('c',))),
        ('horizon', 3),
        ('prices', ['0', '0', '1']),
    ):
        changed = dict(state); changed[key] = replacement
        result = check_bundle(SPECS, changed, certs, checks)
        cases.append({'changed_component': key, 'statuses': result})
    # Same name and old weights do not confer validity on a larger repair language.
    broad = deepcopy(state)
    broad['problem']['repairs'].append({'name': 'universal', 'cost': '1',
                                        'good': list(range(broad['problem']['n']))})
    before = check_bundle(SPECS, broad, certs, checks)
    try:
        verify_weights(read_problem(broad['problem']), tuple(Q(v) for v in broad['weights']))
        raise AssertionError('The stale dual weights were accepted.')
    except ValueError:
        pass
    p = read_problem(broad['problem']); fresh_w, _ = checked_greedy_weights(p)
    tree, report = ordered_weighted_search(p, 0, fresh_w)
    if tree is None:
        raise AssertionError('The universal repair was not found.')
    broad['weights'] = list(map(str, fresh_w)); broad['horizon'] = 0; broad['tree'] = tree_to_dict(tree)
    fresh = dict(certs)
    for name, witness in [('repair_weights', {'total': str(sum(fresh_w, Q(0)))}),
                          ('controller', report['witness'])]:
        spec = next(s for s in SPECS if s.name == name)
        fresh[name] = issue(spec, broad, witness, fresh, checks[name])
    after = check_bundle(SPECS, broad, fresh, checks)
    # Old cost evidence is explicitly NOT reissued for a different controller.
    if after['controller']['status'] != 'VALID' or after['cost_assessment']['status'] != 'BLOCKED':
        raise AssertionError('Controller replacement leaked into a stale cost claim.')
    # Price-only edit leaves semantic certificates valid. Recompute, do not relabel.
    priced = dict(state); priced['prices'] = ['0', '0', '1']
    delta = net_saving(priced['cost_ledger']['setup'], priced['cost_ledger']['savings'], [1])
    revised_margin = priced_saving(delta, priced['prices'])
    cost_spec = SPECS[-1]
    new_cost = dict(certs)
    new_cost['cost_assessment'] = issue(cost_spec, priced,
        {'priced_margin': str(revised_margin), 'strictly_positive': revised_margin > 0}, certs, checks['cost_assessment'])
    priced_status = check_bundle(SPECS, priced, new_cost, checks)
    if revised_margin >= 0 or not all(v['status'] == 'VALID' for v in priced_status.values()):
        raise AssertionError('Negative but valid resource conclusion was concealed.')
    return {'status': 'PASS', 'baseline': baseline, 'revision_cases': cases,
            'repair_extension': {'before_recheck': before, 'after_recheck': after,
                                  'replacement_work': report['witness'], 'old_cost_claim_reused': False},
            'price_revision': {'margin': str(revised_margin), 'statuses': priced_status},
            'measured_weighted_search': raw,
            'certificate_seals': {k: c.seal() for k, c in certs.items()},
            'boundary': 'Declared dependency equality plus replayed project-local checks. Dependency completeness and primitive proof soundness are assumptions. This does not make the certificate manager a learned or independently verified system.'}


if __name__ == '__main__':
    result = run_demo()
    (ROOT/'validation/revision_demonstration.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: certificate invalidation, checked repair replacement, and separate resource revaluation.')
    print('Event savings:', result['measured_weighted_search']['net_saving'])
    print('Replacement:', result['repair_extension']['replacement_work'])

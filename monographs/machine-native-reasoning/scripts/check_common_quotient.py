#!/usr/bin/env python3
"""Exhaustive exact F_2^2 regression for Core 2.4.

Two candidate models, two actions, all 16^4 operator families, and all four
linear scalar readouts. Independent state-pair reachability runs to exhaustion,
not to an arbitrarily selected word horizon. This finite checker is not the
proof of the general field-linear theorem.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path


def span(generators: set[int]) -> frozenset[int]:
    result = {0}
    for g in generators:
        result.update(x ^ g for x in tuple(result))
    return frozenset(result)


def closure(ref: tuple[tuple[int, ...], ...], other: tuple[tuple[int, ...], ...]):
    e = span({ref[a][v] ^ other[a][v] for a in range(2) for v in (1, 2)})
    stages = [e]
    while True:
        f = span(set(e) | {ref[a][v] for a in range(2) for v in e})
        if f == e:
            break
        stages.append(f)
        e = f
    assert len(stages) - 1 <= 2
    return e, stages


def paired_reachable(ref, other, switched: bool):
    # Initial states range over the whole vector space. The model index is
    # fixed in the first calculation, and can switch at every action in the second.
    seen = {(v, v) for v in range(4)}
    pending = list(seen)
    choices = (ref, other) if switched else (other,)
    while pending:
        x, y = pending.pop()
        for candidate in choices:
            for a in range(2):
                successor = (candidate[a][x], ref[a][y])
                if successor not in seen:
                    seen.add(successor)
                    pending.append(successor)
    return seen


def run() -> dict:
    matrices = [(0, a, b, a ^ b) for a in range(4) for b in range(4)]
    families = decisions = positive = 0
    dimensions = {0: 0, 1: 0, 2: 0}
    rounds = {0: 0, 1: 0, 2: 0}
    immediate_only_counterexamples = 0
    for r0, r1, t0, t1 in itertools.product(matrices, repeat=4):
        ref, other = (r0, r1), (t0, t1)
        e, stages = closure(ref, other)
        e_reverse, _ = closure(other, ref)
        assert e == e_reverse, 'reference dependence'
        fixed = paired_reachable(ref, other, False)
        switched = paired_reachable(ref, other, True)
        assert span({x ^ y for x, y in fixed}) == e, 'fixed-word discrepancy mismatch'
        assert span({x ^ y for x, y in switched}) == e, 'switching mismatch'
        representatives = [min(v ^ d for d in e) for v in range(4)]
        for candidate in (ref, other):
            for a in range(2):
                for v in range(4):
                    assert representatives[candidate[a][v]] == representatives[ref[a][representatives[v]]]
        for q in range(4):
            output = tuple((q & v).bit_count() % 2 for v in range(4))
            invisible = all(output[d] == 0 for d in e)
            fixed_agreement = all(output[x] == output[y] for x, y in fixed)
            switch_agreement = all(output[x] == output[y] for x, y in switched)
            quotient_readout = all(output[v] == output[representatives[v]] for v in range(4))
            assert invisible == fixed_agreement == switch_agreement == quotient_readout
            immediate = all(output[d] == 0 for d in stages[0])
            immediate_only_counterexamples += int(immediate and not invisible)
            positive += int(invisible)
            decisions += 1
        families += 1
        dimensions[len(e).bit_length() - 1] += 1
        rounds[len(stages) - 1] += 1
    assert families == 65536 and decisions == 262144
    assert immediate_only_counterexamples > 0
    return {
        'schema': 'komorebi.core24.exact_finite.v1', 'status': 'PASS',
        'field': 'F_2', 'dimension': 2, 'actions': 2, 'candidates': 2,
        'exhaustive_operator_families': families, 'readout_contracts': decisions,
        'admissible_readout_contracts': positive,
        'discrepancy_dimension_histogram': dimensions,
        'strict_closure_round_histogram': rounds,
        'immediate_invisibility_insufficient_cases': immediate_only_counterexamples,
        'checked': ['fixed-candidate paired-state reachability to exhaustion',
                    'arbitrary-switching paired-state reachability to exhaustion',
                    'independent invariant-subspace closure', 'canonical coset updates',
                    'readout factorization', 'reference independence', 'dimension bound'],
        'scope': 'Exact exhaustive finite regression, not a replacement for general Lean proofs.'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Exact independent finite regression for Reviewed Core 3.2.

The signatures below are computed by world-set intersections and target images.
The occupancy implementation instead uses attained (cell,target) pairs. Neither
implementation imports Lean output. The exhaustive domain is every canonical
partition of 0..n-1, n <= 5, every map into a three-element target alphabet, and
every candidate subset and union-of-cells event. Canonical partition labels
remove only label permutations, not any unlabelled partition. This finite test
does not establish the universal theorem or any variable-length memory bound.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
INPUTS = [Path(__file__), ROOT / 'source/core_v0.2.tex',
          ROOT / 'MachineTheory/Correction.lean', ROOT / 'release/NEXT_CORE32_SPEC.md']


def partition_maps(n):
    """Restricted-growth strings enumerate every set partition once."""
    if n == 0:
        yield ()
        return
    def rec(xs, greatest):
        if len(xs) == n:
            yield tuple(xs)
        else:
            for k in range(greatest + 2):
                yield from rec(xs + [k], max(greatest, k))
    yield from rec([0], 0)


def image_bits(worlds, target):
    ans = 0
    for w, y in enumerate(target):
        if worlds & (1 << w):
            ans |= 1 << y
    return ans


def signatures(cell, target, event_worlds=None):
    n = len(cell)
    m = max(cell, default=-1) + 1
    events = (tuple(sum(1 << w for w in range(n) if j & (1 << cell[w]))
                    for j in range(1 << m)) if event_worlds is None else tuple(event_worlds))
    return [tuple(image_bits(v & e, target) for e in events) for v in range(1 << n)], events


def occupancy_records(cell, target):
    pairs = tuple(sorted(set(zip(cell, target))))
    where = {p: k for k, p in enumerate(pairs)}
    records = []
    for v in range(1 << len(cell)):
        occupied = 0
        for w, pair in enumerate(zip(cell, target)):
            if v & (1 << w):
                occupied |= 1 << where[pair]
        records.append(occupied)
    return records, pairs


def occupied_target(bits, pairs):
    ans = 0
    for k, (_, y) in enumerate(pairs):
        if bits & (1 << k):
            ans |= 1 << y
    return ans


def occupancy_step(bits, pairs, cell_selection):
    return sum(1 << k for k, (i, _) in enumerate(pairs)
               if (bits & (1 << k)) and (cell_selection & (1 << i)))


def check_family(cell, target, count):
    sigs, events = signatures(cell, target)
    occs, pairs = occupancy_records(cell, target)
    r = len(pairs)
    sig_to_occ, occ_to_sig = {}, {}
    for v, (sig, occ) in enumerate(zip(sigs, occs)):
        assert sig_to_occ.setdefault(sig, occ) == occ
        assert occ_to_sig.setdefault(occ, sig) == sig
        count['signature_occupancy_classification_candidates'] += 1
        assert occupied_target(occ, pairs) == image_bits(v, target)
        count['current_readout'] += 1
        for j, e in enumerate(events):
            step = occupancy_step(occ, pairs, j)
            assert step == occs[v & e]
            assert occupied_target(step, pairs) == sig[j]
            count['event_update'] += 1
            count['event_readout'] += 1
    assert set(occs) == set(range(1 << r))
    assert len(set(sigs)) == 1 << r
    count['realization_and_exact_count_families'] += 1
    for s in range(1 << r):
        # Full preimage, not a chosen representative: it must realize exactly s.
        preimage = sum(1 << w for w in range(len(cell))
                       if s & (1 << pairs.index((cell[w], target[w]))))
        assert occs[preimage] == s
        count['full_preimage_realizations'] += 1
    assert sigs[0] == tuple(0 for _ in events)
    assert occs[0] == 0
    count['empty_candidate'] += 1
    return {'worlds': len(cell), 'cells': max(cell, default=-1) + 1,
            'attained_pairs': r, 'signatures': len(set(sigs))}


def boundary_checks(count):
    checks = {}
    checks['empty_worlds'] = check_family((), (), count)
    checks['one_cell_constant_target'] = check_family((0, 0, 0), (1, 1, 1), count)
    checks['multiple_targets_per_cell_and_repeated_targets'] = check_family((0, 0, 1, 1), (0, 1, 0, 1), count)
    assert checks['one_cell_constant_target']['signatures'] == 2
    assert checks['multiple_targets_per_cell_and_repeated_targets']['attained_pairs'] == 4
    # Target value 2 is unused: no phantom (cell,2) pair is retained.
    occs, pairs = occupancy_records((0, 0, 1), (0, 1, 0))
    assert all(y != 2 for _, y in pairs) and len(pairs) == 3
    checks['unattained_target_value'] = {'unused_value': 2, 'attained_pairs': len(pairs)}

    # Same old occupancy, but a newly admitted event splits its sole cell.
    cell, target = (0, 0), (0, 0)
    occs, _ = occupancy_records(cell, target)
    split_sig, _ = signatures(cell, target, event_worlds=(0, 1, 3))
    assert occs[1] == occs[2] and split_sig[1] != split_sig[2]
    checks['splitting_cell_invalidates_sufficiency'] = {'worlds': 2, 'candidates': [1, 2], 'extra_event': 1}
    # Keeping only empty and total evidence is an intersection-closed family,
    # but it loses the singleton events needed to attain the old lower bound.
    cell, target = (0, 1), (0, 0)
    occs, _ = occupancy_records(cell, target)
    weak_sig, _ = signatures(cell, target, event_worlds=(0, 3))
    assert occs[1] != occs[2] and weak_sig[1] == weak_sig[2]
    assert len(set(weak_sig)) == 2 < 4
    checks['missing_singleton_events_loses_lower_bound'] = {'signatures': 2, 'old_occupancies': 4}

    worlds = tuple(itertools.product(range(2), repeat=3))
    cell = tuple(2*b+s for b, s, nuisance in worlds)
    target = tuple(b for b, s, nuisance in worlds)
    sensor = check_family(cell, target, count)
    assert sensor == {'worlds': 8, 'cells': 4, 'attained_pairs': 4, 'signatures': 16}
    v = sum(1 << worlds.index(w) for w in [(0,0,0), (1,1,0)])
    w = sum(1 << worlds.index(w) for w in [(0,1,0), (1,0,0)])
    calibration = sum(1 << k for k, (_, s, _) in enumerate(worlds) if s == 0)
    assert image_bits(v, target) == image_bits(w, target) == 3
    assert image_bits(v & calibration, target) == 1
    assert image_bits(w & calibration, target) == 2
    checks['four_cell_eight_world_sensor'] = sensor | {'candidate_bits': 8, 'occupancy_bits': 4,
                                                     'too_few_bit_capacity': 8,
                                                     'current_target_set_loses_correction': True}

    # Independent small exhaustive injection rejection for r=1,2,3.
    rejected = 0
    for r in (1, 2, 3):
        states, codes = 1 << r, 1 << (r-1)
        for encoding in itertools.product(range(codes), repeat=states):
            assert len(set(encoding)) < states
            rejected += 1
    assert rejected == 65553
    checks['too_few_bits_exhaustive_encodings'] = {'r': [1,2,3], 'b': [0,1,2],
                                                'rejected_assignments': rejected}
    # Source sensor sequential update, including contradiction. This finite
    # check supplements rather than replaces the generic Lean list theorem.
    sigs, events = signatures(cell, target)
    occs, pairs = occupancy_records(cell, target)
    seqs = 0
    for v in range(1 << 8):
        for js in itertools.product(range(16), repeat=2):
            actual, kept = v, occs[v]
            for j in js:
                actual &= events[j]
                kept = occupancy_step(kept, pairs, j)
            assert occupied_target(kept, pairs) == image_bits(actual, target)
            seqs += 1
    checks['sensor_two_event_sequences'] = seqs
    return checks


def pin_inputs():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', '--output', dest='out', type=Path, required=True)
    args = ap.parse_args()
    before = pin_inputs()
    started = time.monotonic()
    count = {k: 0 for k in ['signature_occupancy_classification_candidates', 'current_readout',
             'event_update', 'event_readout', 'realization_and_exact_count_families',
             'full_preimage_realizations', 'empty_candidate']}
    bell = [1,1,2,5,15,52]
    levels=[]
    for n in range(6):
        parts = list(partition_maps(n))
        assert len(parts) == bell[n]
        families = 0
        for c in parts:
            for t in itertools.product(range(3), repeat=n):
                check_family(c, t, count)
                families += 1
        assert families == bell[n] * 3**n
        levels.append({'worlds': n, 'partitions': len(parts), 'target_maps_per_partition': 3**n,
                       'families': families})
    boundaries = boundary_checks(count)
    after = pin_inputs()
    assert before == after
    result={'status':'PASS','assertion_tested':'In the explicitly enumerated finite population, direct future-filter target signatures and attained cell-target occupancy have exactly the same fibres; every occupancy occurs; signature count is 2^r; occupancy readout/update agrees with direct world filtering.',
            'scope':'Finite exact regression, not a universal proof, novelty claim, or variable-length/average-bit/runtime lower bound.',
            'domain':{'world_sizes':[0,1,2,3,4,5], 'target_alphabet':[0,1,2],
                      'partitions':'all canonical restricted-growth partitions',
                      'candidates':'all subsets including empty', 'events':'exactly all unions of partition cells'},
            'levels':levels,'checks':count,'boundary_controls':boundaries,
            'inputs_before':before,'inputs_after':after,'software':{'python':sys.version,'platform':platform.platform()},
            'command_template':'python3 scripts/core32_exact.py --out OUTPUT'}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'families':sum(x['families'] for x in levels),
                      'checks':count,'boundary_controls':len(boundaries),'seconds':time.monotonic()-started}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())

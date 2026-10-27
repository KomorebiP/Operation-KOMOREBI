#!/usr/bin/env python3
"""Complete finite prefixes of the two new irregular wall families j=33,49."""
from __future__ import annotations
import argparse, json, time
from fractions import Fraction
from pathlib import Path
import dyadic_modular as d
from check_completion_v4 import original_normalized_tail, predicted_capped
from certificates_v5 import validate_atlas, mean_valuation, distribution_record, regular_scales


def run(j: int) -> dict:
    if j not in (33, 49):
        raise ValueError('This audit contract permits j=33 or 49 only')
    start = time.perf_counter()
    threshold = max(t for i, di, k, t in regular_scales(j))
    L0 = d.wall_threshold(j)
    precision = max(64, threshold + 12)
    records, counts = [], {}
    def count(s, n=1): counts[s] = counts.get(s, 0) + n
    for delta in range(1, threshold + 1):
        r = (1 << (L0 + delta)) - j
        data = d.tail_polynomial(r, precision)
        atlas = d.root_atlas(data)
        count('whole_ball_certificates', validate_atlas(data, atlas))
        # Independently reconstruct the minimal coefficient precision each leaf needs.
        low_precision = 1 + max(a.get('content', a.get('value', 0)) for a in atlas)
        low = d.tail_polynomial(r, low_precision)
        assert d.trim([a % (1 << low_precision) for a in data['coefficients']]) == low['coefficients']
        validate_atlas(low, atlas)
        count('coefficient_precision_compatibility')
        for x in list(range(13)) + [j - 1, j, j + 1]:
            bits = min(32, precision)
            value = original_normalized_tail(r, x, bits)
            assert value == d.evaluate(data['coefficients'], x, 1 << bits)
            count('original_unfactored_tails')
        for x in range(128):
            value = d.evaluate(data['coefficients'], x, 1 << precision)
            actual = precision if not value else int(d.v2(value))
            assert actual == predicted_capped(atlas, x, precision)
            count('atlas_value_checks')
        root_count = sum(a['kind'] == 'simple_root' for a in atlas)
        if delta == threshold:
            assert root_count == j
            assert mean_valuation(atlas) == j
            assert 4*r - 1 + data['mu'] + r.bit_count() + mean_valuation(atlas) == 4*(r+j)
            count('saturated_mean_identity')
        records.append({'j': j, 'delta': delta, 'wall_L': L0,
                        'r': r, 'precision': precision, 'mu': data['mu'],
                        'minima': data['minima'], 'roots': root_count,
                        'atlas': atlas, 'distribution': distribution_record(atlas, 20)})
        count('positive_wall_distances')
    # Pre-wall and equality scales: their residual-polynomial proofs cover all scales.
    prewall = []
    for L in range(j.bit_length(), L0 + 1):
        r = (1 << L) - j
        mu, indices = d.minimum(r)
        expected = ([1] if j == 33 else [0, 1]) + ([j] if L == L0 else [])
        assert indices == expected, (j,L,indices,expected)
        count('prewall_minimum_checks')
    for L in (j.bit_length(), L0 - 1, L0):
        r = (1 << L) - j
        data = d.tail_polynomial(r, precision)
        atlas = d.root_atlas(data)
        count('boundary_whole_ball_certificates', validate_atlas(data, atlas))
        assert sum(a['kind'] == 'simple_root' for a in atlas) == 1
        prewall.append({'L':L, 'r':r, 'atlas':atlas})
    return {'status':'PASS', 'j':j, 'L_j':L0, 'eventual_threshold':threshold,
            'counts':counts, 'records':records, 'boundary_examples':prewall,
            'runtime_seconds':time.perf_counter()-start,
            'claim_boundary':'Finite coefficient certificates cover all exceptional positive distances. The proved general separation theorem covers larger distances. Prewall root count has a separate residual-polynomial proof. No claim about arbitrary depths outside these wall families.'}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--j',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=run(a.j);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','j','L_j','eventual_threshold','counts','runtime_seconds')},indent=2))
    print('ROOT_COUNTS', [r['roots'] for r in result['records']])

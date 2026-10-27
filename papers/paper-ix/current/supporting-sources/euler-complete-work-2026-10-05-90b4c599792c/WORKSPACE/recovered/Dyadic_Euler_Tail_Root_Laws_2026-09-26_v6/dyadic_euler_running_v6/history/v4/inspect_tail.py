#!/usr/bin/env python3
"""Inspect the exact modular polynomial and certified balls for an Euler tail.

Examples:
  python inspect_tail.py --wall 5 --delta 6 --precision 32 --offset 8
  python inspect_tail.py --r 510 --precision 32

Zero residues are reported as lower bounds, not exact zero valuations.
"""
from __future__ import annotations
import argparse
import json
from dyadic_modular import evaluate, minimum, root_atlas, tail_polynomial, v2, wall_threshold, weierstrass_mod


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--r', type=int, help='first omitted depth, r=M+1')
    group.add_argument('--wall', type=int, help='positive shifted-wall label j')
    parser.add_argument('--delta', type=int, help='positive distance past the specified wall')
    parser.add_argument('--precision', type=int, default=32, help='coefficient precision in binary digits (1..256)')
    parser.add_argument('--offset', type=int, help='optional nonnegative integer x=N-r at which to evaluate')
    args = parser.parse_args()
    if not 1 <= args.precision <= 256:
        parser.error('precision must be between 1 and 256')
    if args.wall is not None:
        if args.wall < 1 or args.delta is None or args.delta < 1:
            parser.error('--wall requires a positive label and a positive --delta')
        r = (1 << (wall_threshold(args.wall) + args.delta)) - args.wall
    else:
        if args.r is None or args.r < 1:
            parser.error('r must be positive')
        if args.delta is not None:
            parser.error('--delta is only used with --wall')
        r = args.r
    if args.offset is not None and args.offset < 0:
        parser.error('--offset must be nonnegative for an integer Euler tail')
    data = tail_polynomial(r, args.precision)
    atlas = root_atlas(data)
    prep = weierstrass_mod(data)
    result = {
        'r': r,
        'last_retained_depth_M': r - 1,
        'precision_bits': args.precision,
        'mu': data['mu'],
        'minimum_layers': data['minima'],
        'degree': prep['degree'],
        'W_coefficients_low_to_high_mod_2P': prep['W'],
        'atlas_complete': not any(a['kind'].startswith('unresolved') for a in atlas),
        'atlas': atlas,
        'interpretation': 'Root residues approximate unique dyadic roots only on leaves certified simple_root. Unresolved leaves make no root assertion.'
    }
    if args.offset is not None:
        x = args.offset
        N = r + x
        residue = evaluate(data['coefficients'], x, 1 << args.precision)
        prefix = 4*r - 1 + r.bit_count() + x.bit_count() - N.bit_count() + data['mu']
        result['evaluation'] = {
            'x': x, 'half_index_N': N, 'Euler_index_2N': 2*N,
            'normalized_residue': residue,
            'valuation_relation': '>=' if residue == 0 else '=',
            'tail_valuation': prefix + (args.precision if residue == 0 else int(v2(residue))),
            'normalization': 'tail = kappa_r * binom(2N,2r) * 2^mu * G_r(x)'
        }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

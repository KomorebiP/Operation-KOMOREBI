#!/usr/bin/env python3
"""Exact bounded check of the written valuation-stratum equivalence."""
import argparse
import json
from pathlib import Path


def main(output):
    checked = 0
    allowed = 0
    for sector in ('A', 'B', 'C', 'unit'):
        sizes = range(1, 43) if sector != 'unit' else [0]
        for r in sizes:
            m, n = {'A': (r, 0), 'B': (0, r),
                    'C': (-r, -r), 'unit': (0, 0)}[sector]
            solutions = []
            # Every possible h with r <= 42 lies in [-34,48], by the
            # written minimum-of-weighted-valuations argument.
            for h in range(-60, 61):
                vals = (35*h+12*m+28*n, 21*h+7*m+17*n,
                        15*h+5*m+12*n)
                if min(vals) == 0:
                    solutions.append((h, vals))
            expected = []
            if sector == 'A' and r % 3 == 0:
                expected = [(-r//3, (r//3, 0, 0))]
            elif sector == 'B' and r % 5 == 0:
                expected = [(-4*r//5, (0, r//5, 0))]
            elif sector == 'C' and r % 7 == 0:
                expected = [(8*r//7, (0, 0, r//7))]
            elif sector == 'unit':
                expected = [(0, (0, 0, 0))]
            assert solutions == expected, (sector, r, solutions, expected)
            checked += 1
            allowed += bool(solutions)
    result = {
        'status': 'PASS_EXACT_BOUNDED_VALUATION_CHECK',
        'domain': 'Z', 'sectors_checked': checked,
        'sectors_with_primitive_scaling': allowed,
        'bounds': {'valuation_size_max': 42, 'scaling_min': -60,
                   'scaling_max': 60},
        'non_claims': ['No integer Beal solution is constructed or excluded.',
                      'Universal validity depends on notes/primitive_scaling.md.']}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    main(p.parse_args().output)

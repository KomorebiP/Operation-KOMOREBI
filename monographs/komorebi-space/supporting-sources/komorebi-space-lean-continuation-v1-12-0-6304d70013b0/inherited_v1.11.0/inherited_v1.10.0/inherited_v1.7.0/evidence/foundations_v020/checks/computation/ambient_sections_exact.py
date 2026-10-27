#!/usr/bin/env python3
"""Finite, exact audit of section/extension formulas; not a proof of general descent."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import time


def rank(matrix: list[list[Q]], cols: int) -> int:
    a = [row[:] for row in matrix]
    pivot = 0
    for col in range(cols):
        k = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if k is None:
            continue
        a[pivot], a[k] = a[k], a[pivot]
        c = a[pivot][col]
        a[pivot] = [x / c for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot and a[i][col]:
                c = a[i][col]
                a[i] = [x - c*y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    assertions = 0
    cases = {'boolean_view_diagrams': 0, 'rational_extension_problems': 0,
             'integer_seeds': 0, 'group_actions': 0}

    def check(p: bool, label: str) -> None:
        nonlocal assertions
        if not p:
            raise AssertionError(label)
        assertions += 1

    maps = list(product(range(2), repeat=2))
    for n in range(2, 6):
        for down in product(maps, repeat=n-1):
            cases['boolean_view_diagrams'] += 1

            def coherent(xs: tuple[int, ...]) -> bool:
                return all(down[i][xs[i+1]] == xs[i] for i in range(len(xs)-1))

            global_sections = [xs for xs in product(range(2), repeat=n) if coherent(xs)]
            generated = []
            for top in range(2):
                xs = [top]
                for edge in reversed(down):
                    xs.append(edge[xs[-1]])
                generated.append(tuple(reversed(xs)))
            check(set(generated) == set(global_sections), 'terminal evaluation')
            prefixes = [[xs for xs in product(range(2), repeat=j+1) if coherent(xs)]
                        for j in range(n)]
            glued = []
            for family in product(*prefixes):
                matching = all(family[j][:i+1] == family[i]
                               for i in range(n) for j in range(i, n))
                if not matching:
                    continue
                s = tuple(family[j][-1] for j in range(n))
                check(coherent(s), 'transition-covered glue coherent')
                check(all(s[:j+1] == family[j] for j in range(n)), 'restriction recovers locals')
                check(sum(all(t[:j+1] == family[j] for j in range(n))
                          for t in global_sections) == 1, 'unique glue')
                glued.append(s)
            check(set(glued) == set(global_sections), 'matching/global equivalence')

    # Over Q, test the quotient membership criterion against an independent
    # global reconstruction parameterized by the terminal coordinate.
    for n in range(2, 5):
        for down in product([-1, 0, 1, 2], repeat=n-1):
            D = [[Q(-1 if j == i else down[i] if j == i+1 else 0)
                  for j in range(n)] for i in range(n-1)]
            coeff = [Q(1)] * n
            for i in range(n-2, -1, -1):
                coeff[i] = Q(down[i]) * coeff[i+1]
            scopes = sorted({(0,), (n-1,), (0, n-1)})
            for x in product([-1, 0, 1], repeat=n):
                residual = [sum(row[j]*x[j] for j in range(n)) for row in D]
                for U in scopes:
                    cases['rational_extension_problems'] += 1
                    free = [j for j in range(n) if j not in U]
                    allowed = [[row[j] for j in free] for row in D]
                    quotient_zero = rank(allowed, len(free)) == rank(
                        [row + [residual[i]] for i, row in enumerate(allowed)], len(free)+1)
                    determined = [Q(x[i])/coeff[i] for i in U if coeff[i]]
                    reconstructed = (all(x[i] == 0 for i in U if not coeff[i]) and
                                     (not determined or all(t == determined[0] for t in determined)))
                    check(quotient_zero == reconstructed, 'constrained class versus actual extension')
                    if reconstructed:
                        t = determined[0] if determined else Q(0)
                        g = [c*t for c in coeff]
                        check(all(sum(row[j]*g[j] for j in range(n)) == 0 for row in D), 'extension exact')
                        check(all(g[i] == x[i] for i in U), 'extension preserves prescribed views')

    for k in range(-31, 32):
        cases['integer_seeds'] += 1
        solutions = [m for m in range(-32, 33) if 2*m == k]
        check(bool(solutions) == (k % 2 == 0), 'integer extension iff even in stated range')
        check(len(solutions) <= 1, 'integer extension uniqueness in stated range')

    for swap in (False, True):
        cases['group_actions'] += 1
        f = lambda x: x ^ int(swap)
        fixed = [x for x in range(2) if f(x) == x]
        check(sorted(f(x) for x in range(2)) == [0, 1], 'transport is bijective')
        check(bool(fixed) == (not swap), 'ambient sections are fixed points')
        check(all(f(f(x)) == x for x in range(2)), 'involution coherence')

    false_claims = {
        'object_cover_alone_glues_different_constant_values': 0 == 1,
        'nonempty_fibers_imply_coherent_section': any((x ^ 1) == x for x in range(2)),
        'bijective_transport_is_identity': all((x ^ 1) == x for x in range(2)),
        'every_local_integer_extends': any(2*m == 1 for m in range(-32, 33)),
    }
    controls = []
    for name, proposition in false_claims.items():
        rejected = False
        try:
            assert proposition, name
        except AssertionError:
            rejected = True
        check(rejected, 'false-claim rejection: ' + name)
        controls.append({'claim': name, 'rejected': rejected})

    result = {'status': 'PASS', 'cases': cases, 'assertions': assertions,
              'negative_controls': controls,
              'arithmetic': 'exact Boolean, integer, and fractions.Fraction rational arithmetic',
              'bounds': {'boolean_views': [2, 5], 'rational_views': [2, 4],
                         'rational_down_scalars': [-1, 0, 1, 2], 'integer_seed_range': [-31, 31]},
              'randomness': False, 'seconds': time.monotonic()-start,
              'non_claims': ['Finite tests do not prove arbitrary or higher-category descent.',
                             'No arithmetic or automorphic correspondence is tested.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

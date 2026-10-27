#!/usr/bin/env python3
"""Exact regression for v0.7.0. Finite tests, not proof of the categorical theorems.

Domains: integral cochain complexes, rational/integer identities, ranks over F_p.
No random sampling. No floating-point tolerances. The arity/label/word bounds are
recorded in output. The proof of the general results is in the LaTeX manuscript.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Sequence

from check_models import tokenise, events_and_predecessors, ideal_graph

Matrix = list[list[int]]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def identity(n: int) -> Matrix:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mm(a: Matrix, b: Matrix) -> Matrix:
    require(bool(a) and bool(b), 'nonempty matrix dimensions required')
    require(len(a[0]) == len(b), 'matrix dimensions mismatch')
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def det(a: Matrix) -> int:
    """Bareiss elimination, with exact divisibility checked at each update."""
    n = len(a)
    if n == 0:
        return 1
    require(all(len(r) == n for r in a), 'determinant needs a square matrix')
    if n == 1:
        return a[0][0]
    b = [row[:] for row in a]
    sign, previous = 1, 1
    for k in range(n - 1):
        if b[k][k] == 0:
            pivot = next((i for i in range(k + 1, n) if b[i][k]), None)
            if pivot is None:
                return 0
            b[k], b[pivot] = b[pivot], b[k]
            sign *= -1
        pivot_value = b[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = b[i][j] * pivot_value - b[i][k] * b[k][j]
                require(numerator % previous == 0, 'Bareiss division was not exact')
                b[i][j] = numerator // previous
            b[i][k] = 0
        previous = pivot_value
    return sign * b[-1][-1]


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    x, y = abs(a), abs(b)
    r0, r1, s0, s1, t0, t1 = x, y, 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
    return r0, s0 * (-1 if a < 0 else 1), t0 * (-1 if b < 0 else 1)


def row_gcd_change(a: Sequence[int]) -> Matrix:
    n = len(a)
    require(n > 0 and any(a), 'gcd normal form excludes the all-zero row')
    u, row = identity(n), list(a)
    for j in range(1, n):
        left, right = row[0], row[j]
        if left == right == 0:
            continue
        g, s, t = extended_gcd(left, right)
        e = identity(n)
        e[0][0], e[j][0] = s, t
        e[0][j], e[j][j] = -right // g, left // g
        u = mm(u, e)
        row = mm([row], e)[0]
    if row[0] < 0:
        e = identity(n)
        e[0][0] = -1
        u = mm(u, e)
    return u


def wedge(u: Matrix, k: int) -> Matrix:
    indices = list(itertools.combinations(range(len(u)), k))
    return [[det([[u[i][j] for j in cols] for i in rows])
             for cols in indices] for rows in indices]


def koszul_differentials(a: Sequence[int]) -> dict[int, Matrix]:
    """D[k] is d^{-k}: K^{-k} -> K^{-k+1}, basis by ordered k-subsets."""
    n = len(a)
    out = {}
    for k in range(1, n + 1):
        source = list(itertools.combinations(range(n), k))
        target = list(itertools.combinations(range(n), k - 1))
        row = {v: i for i, v in enumerate(target)}
        d = [[0] * len(source) for _ in target]
        for col, subset in enumerate(source):
            for position, index in enumerate(subset):
                reduced = subset[:position] + subset[position + 1:]
                d[row[reduced]][col] += (-1) ** position * a[index]
        out[k] = d
    return out


def rank_mod(a: Matrix, p: int) -> int:
    b = [[x % p for x in row] for row in a]
    m, n = len(b), len(b[0])
    rank = 0
    for j in range(n):
        pivot = next((i for i in range(rank, m) if b[i][j]), None)
        if pivot is None:
            continue
        b[rank], b[pivot] = b[pivot], b[rank]
        inv = pow(b[rank][j], -1, p)
        b[rank] = [(v * inv) % p for v in b[rank]]
        for i in range(m):
            if i != rank and b[i][j]:
                c = b[i][j]
                b[i] = [(x - c * y) % p for x, y in zip(b[i], b[rank])]
        rank += 1
        if rank == m:
            break
    return rank


def check_koszul_vector(a: tuple[int, ...]) -> dict[str, int]:
    n = len(a)
    g = math.gcd(*a)
    u = row_gcd_change(a)
    require(abs(det(u)) == 1, f'unimodularity: {a}')
    target = [g] + [0] * (n - 1)
    require(mm([list(a)], u)[0] == target, f'gcd row: {a}')
    d, reduced = koszul_differentials(a), koszul_differentials(target)
    w = {k: wedge(u, k) for k in range(n + 1)}
    for k in range(n + 1):
        require(abs(det(w[k])) == 1, f'exterior map invertibility: {a}, {k}')
    for k in range(1, n + 1):
        require(mm(d[k], w[k]) == mm(w[k - 1], reduced[k]),
                f'exterior chain map: {a}, degree {-k}')
    for k in range(2, n + 1):
        require(all(x == 0 for row in mm(d[k - 1], d[k]) for x in row),
                f'd squared: {a}, degree {-k}')
    field_checks = 0
    for p in (2, 3, 5, 7):
        ranks = {k: rank_mod(v, p) for k, v in d.items()}
        for k in range(n + 1):
            h = math.comb(n, k) - ranks.get(k, 0) - ranks.get(k + 1, 0)
            expected = math.comb(n, k) if all(x % p == 0 for x in a) else 0
            require(h == expected, f'field homology: {a}, p={p}, degree={-k}')
            field_checks += 1
    return {'chain_map_checks': n, 'd_squared_checks': max(0, n - 1),
            'field_homology_dimensions': field_checks}


def prime_divisors(n: int) -> set[int]:
    require(n > 0, 'prime support function expects a positive integer')
    out, p = set(), 2
    while p * p <= n:
        if n % p == 0:
            out.add(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        out.add(n)
    return out


def remove_primes(n: int, primes: set[int]) -> int:
    for p in sorted(primes):
        while n % p == 0:
            n //= p
    return n


def transitive_predecessors(events, pred):
    out = {e: set(pred[e]) for e in events}
    changed = True
    while changed:
        changed = False
        for e in events:
            old = len(out[e])
            for f in tuple(out[e]):
                out[e].update(out[f])
            changed |= len(out[e]) != old
    return {e: frozenset(v) for e, v in out.items()}


def check_scalar_diagrams(max_length: int) -> dict[str, int]:
    totals = dict(words=0, ideals=0, cover_arrows=0, independent_squares=0,
                  eligible_contexts=0, localized_inverse_checks=0,
                  ideal_pair_excision_checks=0)
    alphabet = (6, 10, 15, 7, 11, 13, 1)
    for n in range(max_length + 1):
        for letters in itertools.product('TC', repeat=n):
            tokens = tokenise(''.join(letters))
            events, pred = events_and_predecessors(tokens)
            predecessors = transitive_predecessors(events, pred)
            ideals, arrows = ideal_graph(events, pred)
            labels = {e: alphabet[(e[0] + 2 * e[1]) % len(alphabet)] for e in events}
            incomparable = {frozenset((e, f)) for e, f in itertools.combinations(events, 2)
                            if e not in predecessors[f] and f not in predecessors[e]}
            removed = set()
            for pair in incomparable:
                e, f = sorted(pair)
                removed |= prime_divisors(math.gcd(labels[e], labels[f]))
            products = {i: math.prod(labels[e] for e in i) for i in ideals}
            seen_pairs = set()
            for i, j in arrows:
                e, = j - i
                require(products[j] == labels[e] * products[i], 'strict scalar composition')
            for i in ideals:
                enabled = [e for e in events if e not in i and predecessors[e] <= i]
                for e, f in itertools.combinations(enabled, 2):
                    require(i | {e, f} in ideals, 'missing diamond terminal')
                    require(products[i] * labels[e] * labels[f] == products[i | {e, f}],
                            'diamond scalar map')
                    require(prime_divisors(math.gcd(labels[e], labels[f])) <= removed,
                            'square support missing from quotient')
                    seen_pairs.add(frozenset((e, f)))
                    totals['independent_squares'] += 1
            require(seen_pairs == incomparable, 'not every incomparable pair occurs in a square')
            for e in events:
                minimal = predecessors[e]
                require(minimal in ideals, 'predecessors are not an ideal')
                residual_order = remove_primes(labels[e], removed)
                for i in ideals:
                    if e not in i and minimal <= i:
                        totals['eligible_contexts'] += 1
                        require(i | {e} in ideals, 'event is not enabled in eligible context')
                        extra = i - minimal
                        require(all(frozenset((e, f)) in incomparable for f in extra),
                                'eligible context adds a dependent event')
                        multiplier = math.prod(labels[f] for f in extra)
                        require(math.gcd(multiplier, residual_order) == 1,
                                'localized context map not invertible')
                        if residual_order > 1:
                            inverse = pow(multiplier % residual_order, -1, residual_order)
                            require((multiplier * inverse) % residual_order == 1,
                                    'wrong context-map inverse')
                            totals['localized_inverse_checks'] += 1
            # Independent combinatorial checks needed by the grid-pasting proof.
            if n <= 6:
                for i in ideals:
                    for j in ideals:
                        require(i | j in ideals and i & j in ideals, 'ideal lattice closure')
                        for e in i - j:
                            for f in j - i:
                                require(frozenset((e, f)) in incomparable,
                                        'exclusive ideal parts not independent')
                        totals['ideal_pair_excision_checks'] += 1
            totals['words'] += 1
            totals['ideals'] += len(ideals)
            totals['cover_arrows'] += len(arrows)
    return totals


def named_boundaries() -> dict:
    require(math.gcd(6, 10, 15) == 1, 'triple residual counterexample')
    require([math.gcd(a, b) for a, b in ((6, 10), (6, 15), (10, 15))] == [2, 3, 5],
            'pair residual counterexample')
    require([remove_primes(x, {2}) for x in (6, 10, 60)] == [3, 5, 15],
            '6/10 localization example')
    for p in (2, 3, 5, 7, 11, 13):
        image = {(p * x) % (p * p) for x in range(p)}
        require(len(image) == p, 'Z/p injection into Z/p^2')
        require((p * 1) % (p * p) != 0, 'nonsplit exponent distinction')
    all_zero = koszul_differentials((0, 0))
    require(all(x == 0 for matrix in all_zero.values() for row in matrix for x in row),
            'all-zero cube differential')
    return {
        'six_ten_after_inverting_2': [3, 5, 15],
        'six_ten_fifteen_pair_gcds': [2, 3, 5],
        'six_ten_fifteen_joint_gcd': 1,
        'nonsplit_prime_chains_checked': [2, 3, 5, 7, 11, 13],
        'excluded_all_zero_pair_free_cohomology_ranks': [1, 2, 1],
    }


def kron(a: Matrix, b: Matrix) -> Matrix:
    return [[a[i][j] * b[u][v]
             for j in range(len(a[0])) for v in range(len(b[0]))]
            for i in range(len(a)) for u in range(len(b))]


def two_by_two_data(a: Matrix) -> tuple[bool, set[int]]:
    g = math.gcd(*(x for row in a for x in row))
    determinant = det(a)
    if g == 0:
        return True, set()
    if determinant == 0:
        return True, prime_divisors(g)
    require(abs(determinant) % (g * g) == 0, 'invalid 2x2 Smith divisibility')
    return False, prime_divisors(g) | prime_divisors(abs(determinant) // g)


def check_matrix_pairs() -> dict:
    cases = {
        'identity': [[1, 0], [0, 1]],
        'zero': [[0, 0], [0, 0]],
        'torsion_2': [[2, 0], [0, 1]],
        'torsion_3': [[3, 0], [0, 1]],
        'torsion_6': [[6, 0], [0, 1]],
        'free_and_2': [[0, 0], [0, 2]],
        'triangular_6': [[2, 1], [0, 3]],
        'mixed_det_minus_2': [[1, 2], [3, 4]],
        'rank_one': [[0, 1], [0, 0]],
        'torsion_5': [[5, 0], [0, 1]],
        'torsion_7': [[7, 0], [0, 1]],
    }
    fields, counts = (2, 3, 5, 7, 11), {'pairs': 0, 'collapse_pairs': 0,
                                              'finite_field_degree_checks': 0}
    for name_a, a in cases.items():
        free_a, primes_a = two_by_two_data(a)
        for name_b, b in cases.items():
            free_b, primes_b = two_by_two_data(b)
            collapse = free_a and free_b
            counts['collapse_pairs'] += int(collapse)
            if not free_a and not free_b:
                support = primes_a & primes_b
            elif free_a and not free_b:
                support = primes_b
            elif not free_a and free_b:
                support = primes_a
            else:
                support = set()  # Free cohomology, not a finite-prime support claim.
            left, right = kron(a, identity(2)), kron(identity(2), b)
            d1 = [x + y for x, y in zip(left, right)]
            d2 = [[-x for x in row] for row in right] + left
            require(all(x == 0 for row in mm(d1, d2) for x in row),
                    f'matrix tensor differential: {name_a}, {name_b}')
            for p in fields:
                r1, r2 = rank_mod(d1, p), rank_mod(d2, p)
                actual = [4 - r1, 8 - r1 - r2, 4 - r2]
                ca, cb = 2 - rank_mod(a, p), 2 - rank_mod(b, p)
                expected = [ca * cb, 2 * ca * cb, ca * cb]
                require(actual == expected, f'field tensor homology: {name_a}, {name_b}, {p}')
                require(any(actual) == (collapse or p in support),
                        f'matrix interaction support: {name_a}, {name_b}, {p}')
                counts['finite_field_degree_checks'] += 3
            counts['pairs'] += 1
    return {'matrices': cases, 'finite_fields': list(fields), **counts,
            'scope': 'all ordered pairs of this explicit 11-matrix set, not all integer matrices'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-length', type=int, default=8)
    parser.add_argument('--max-label', type=int, default=6)
    parser.add_argument('--max-arity', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not (0 <= args.max_length <= 10 and 1 <= args.max_label <= 20
            and 1 <= args.max_arity <= 5):
        parser.error('bounds: word length 0..10, labels 1..20, arity 1..5')
    start = time.perf_counter()
    totals = dict(vectors=0, chain_map_checks=0, d_squared_checks=0,
                  field_homology_dimensions=0)
    for n in range(1, args.max_arity + 1):
        for a in itertools.product(range(1, args.max_label + 1), repeat=n):
            result = check_koszul_vector(a)
            totals['vectors'] += 1
            for key, value in result.items():
                totals[key] += value
    signed_cases = ((0, 2), (-2, 4), (0, -3, 6), (-6, 10, 15), (0, 0, 5), (7,))
    for a in signed_cases:
        check_koszul_vector(a)
    diagrams = check_scalar_diagrams(args.max_length)
    named = named_boundaries()
    matrix_pairs = check_matrix_pairs()
    script = Path(__file__)
    report = {
        'status': 'PASS',
        'evidence': 'exact finite regression; general results require written proofs',
        'python': platform.python_version(),
        'platform': platform.platform(),
        'argv': sys.argv,
        'coefficient_convention': 'integral cochain Koszul complex; K^{-k}=exterior^k; d degree +1',
        'bounds': {'positive_labels': [1, args.max_label], 'arity': [1, args.max_arity],
                   'word_length': [0, args.max_length], 'ideal_pair_checks_max_length': 6,
                   'finite_fields': [2, 3, 5, 7]},
        'deterministic': True,
        'random_seed': None,
        'skipped_primary_cases': 0,
        'integral_chain_checks': totals,
        'additional_signed_or_zero_nonzero_vectors': [list(x) for x in signed_cases],
        'scalar_event_diagrams': diagrams,
        'named_boundary_cases': named,
        'integral_matrix_pairs': matrix_pairs,
        'elapsed_seconds': time.perf_counter() - start,
        'input_sha256': {str(script.name): hashlib.sha256(script.read_bytes()).hexdigest(),
                         'check_models.py': hashlib.sha256(script.with_name('check_models.py').read_bytes()).hexdigest()},
        'nonclaims': ['No Lean certification', 'No exhaustive category-theoretic verification',
                      'No general arithmetic globalization', 'No Langlands reciprocity proof',
                      'No historical novelty claim'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

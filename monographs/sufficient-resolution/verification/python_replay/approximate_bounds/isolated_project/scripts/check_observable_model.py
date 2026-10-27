#!/usr/bin/env python3
"""Bounded exact controls for finite observable-state construction.

Compares sparse row-closure against explicit all-word observation tables using
a separate forward-elimination rank routine.  Tests are evidence about the
implementation, not the proof of the universal Lean theorems.
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
import json
import random
from observable_model import Matrix, Model, minimize, validate_certificate, word_operator

checks = 0
systems = 0
failures_rejected = 0
records = []


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def independent_rank(rows: list[list[Q]], ncols: int) -> int:
    """Forward elimination only, independent from the solver's RREF/provenance code."""
    a = [list(row) for row in rows]
    pivot_row = 0
    for col in range(ncols):
        pivot = None
        for j in range(pivot_row, len(a)):
            if a[j][col] != 0:
                pivot = j
                break
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        divisor = a[pivot_row][col]
        for j in range(pivot_row + 1, len(a)):
            factor = a[j][col] / divisor
            for k in range(col, ncols):
                a[j][k] -= factor * a[pivot_row][k]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row


def words(m: int, depth: int):
    for n in range(depth + 1):
        yield from product(range(m), repeat=n)


def observation_rows(ops: tuple[Matrix, ...], obs: Matrix, depth: int) -> list[list[Q]]:
    rows = []
    for w in words(len(ops), depth):
        rows.extend([list(row) for row in (obs @ word_operator(ops, w, obs.ncols)).rows])
    return rows


def run_case(name: str, ops: tuple[Matrix, ...], obs: Matrix, expected: int | None = None) -> Model:
    global checks, systems
    systems += 1
    model = minimize(ops, obs)
    identities = validate_certificate(ops, obs, model)
    checks += identities
    n = obs.ncols
    initial = independent_rank([list(row) for row in obs.rows], n)
    bound = n - initial
    check(model.horizon_bound == bound, name + ': horizon')
    check(len(model.rank_history) - 1 <= bound, name + ': termination budget')
    if expected is not None:
        check(model.compression.nrows == expected, name + ': expected minimum')
    # Check each realized refinement against a separately generated word table.
    for d, rank in enumerate(model.rank_history):
        brute_rows = observation_rows(ops, obs, d)
        check(independent_rank(brute_rows, n) == rank, name + ': depth rank')
    brute_rows = observation_rows(ops, obs, bound)
    brute_rank = independent_rank(brute_rows, n)
    check(brute_rank == model.compression.nrows, name + ': full horizon rank')
    check(independent_rank(brute_rows + [list(row) for row in model.compression.rows], n) == brute_rank,
          name + ': generated rowspace matches table')
    # Exact whole-map fidelity checks, not random state samples.
    for w in words(len(ops), min(bound + 2, 4)):
        reduced = word_operator(model.dynamics, w, model.compression.nrows)
        original = word_operator(ops, w, n)
        check(model.compression @ original == reduced @ model.compression, name + ': word intertwining')
        check(model.output @ reduced @ model.compression == obs @ original, name + ': word observation')
    encoded = json.loads(json.dumps(model.json()))
    restored = Model.parse(encoded)
    check(restored == model, name + ': JSON exact round trip')
    checks += validate_certificate(ops, obs, restored)
    records.append({'name': name, 'dimension': n, 'alphabet_size': len(ops),
                    'output_dimension': obs.nrows, 'minimum_dimension': model.compression.nrows,
                    'bound': bound, 'strict_refinements': len(model.rank_history) - 1,
                    'certificate_generation_depth': model.generation_depth,
                    'identities': identities})
    return model


def rejects(fn, label: str) -> None:
    global failures_rejected
    try:
        fn()
    except (ValueError, TypeError, RuntimeError):
        failures_rejected += 1
    else:
        raise AssertionError('Negative control accepted: ' + label)


def main() -> None:
    a = Matrix.parse([[0,1,0],[0,0,0],[0,0,1]], 3)
    b = Matrix.parse([[0,0,0],[1,0,0],[0,0,1]], 3)
    o = Matrix.parse([[1,0,0]], 3)
    lean_model = run_case('lean_two_noncommuting_operations', (a,b), o, 2)
    check(lean_model.compression == Matrix.parse([[1,0,0],[0,1,0]], 3), 'Lean concrete compression match')
    check(a @ b != b @ a, 'Noncommuting control')
    # Sharp chains: the final direction first appears at depth n-1.
    for n in range(1, 7):
        shift = Matrix.parse([[int(j == i+1) for j in range(n)] for i in range(n)], n)
        obs = Matrix.parse([[int(j == 0) for j in range(n)]], n)
        model = run_case('sharp_shift_' + str(n), (shift,), obs, n)
        check(model.generation_depth == n - 1, 'Sharp depth')
        check(model.rank_history == tuple(range(1,n+1)), 'Sharp rank ladder')
    run_case('zero_state_zero_output', (), Matrix.zero(0,0), 0)
    run_case('zero_state_nonempty_alphabet', (Matrix.zero(0,0),), Matrix.zero(1,0), 0)
    run_case('empty_alphabet', (), Matrix.parse([[1,2,0],[2,4,0]],3), 1)
    run_case('zero_observation', (a,b), Matrix.zero(1,3), 0)
    run_case('zero_output_space', (a,b), Matrix.zero(0,3), 0)
    run_case('full_observation', (a,b), Matrix.eye(3), 3)
    run_case('duplicate_operations', (a,a), o, 2)
    run_case('rational_dependent_observation', (a,b), Matrix.parse([['1/2',0,0],[1,0,0]],3), 2)
    rng = random.Random(20260913)
    for n in range(1,6):
        for sample in range(3):
            ops = tuple(Matrix.parse([[rng.randint(-2,2) for _ in range(n)] for _ in range(n)],n)
                        for _ in range(2))
            obs = Matrix.parse([[rng.randint(-2,2) for _ in range(n)] for _ in range(1 + sample % 2)],n)
            run_case(f'random_{n}_{sample}',ops,obs)
    # Whole-certificate negative controls. Each corrupted identity is tested separately.
    rejects(lambda: validate_certificate((a,b),o,replace(lean_model, output=Matrix.zero(1,2))), 'output')
    rejects(lambda: validate_certificate((a,b),o,replace(lean_model, lift=Matrix.zero(3,2))), 'surjectivity')
    rejects(lambda: validate_certificate((a,b),o,replace(lean_model,
            dynamics=(Matrix.zero(2,2),lean_model.dynamics[1]))), 'dynamics')
    rejects(lambda: validate_certificate((a,b),o,replace(lean_model, provenance=({},{}))), 'generation')
    rejects(lambda: validate_certificate((a,b),o,replace(lean_model, generation_depth=0)), 'depth')
    rejects(lambda: Matrix.parse([[0.1]],1), 'floating input')
    rejects(lambda: minimize((Matrix.eye(2),),o), 'operator shape')
    rejects(lambda: minimize((a,b),o,max_dimension=2), 'dimension resource limit')
    rejects(lambda: minimize((a,b),o,max_certificate_terms=0), 'certificate resource limit')
    rejects(lambda: Model.parse({'schema_version':2}), 'unknown JSON schema')
    print(json.dumps({'passed':True,'systems':systems,'exact_assertions':checks,
                      'negative_controls_rejected':failures_rejected,'seed':20260913,
                      'bounds':{'fine_dimension':'0..6','alphabet_size':'0..2',
                                'output_dimension':'0..3','word_fidelity_max_depth':4,
                                'horizon_tables_max_depth':5},
                      'records':records},indent=2))


if __name__ == '__main__':
    main()

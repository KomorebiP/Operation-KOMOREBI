#!/usr/bin/env python3
"""Independently check exact browser certificates using Fraction and minor ranks.

Run: python -B tools/audit_recovery_lab.py [--output result.json]
Requires Node.js on PATH, or --node /path/to/node. No third-party dependencies.
"""
import argparse
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from math import lcm
from pathlib import Path
import random
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def determinant(a):
    size = len(a)
    result = 0
    for perm in permutations(range(size)):
        inversions = sum(perm[i] > perm[j] for i in range(size) for j in range(i+1, size))
        value = -1 if inversions % 2 else 1
        for row, column in enumerate(perm):
            value *= a[row][column]
        result += value
    return result


def rank_by_minors(matrix):
    if not matrix:
        return 0
    integers = []
    for row in matrix:
        scale = lcm(*(v.denominator for v in row))
        integers.append([int(v*scale) for v in row])
    for size in range(min(len(matrix), len(matrix[0])), 0, -1):
        for rows in combinations(integers, size):
            for cols in combinations(range(len(matrix[0])), size):
                if determinant([[row[c] for c in cols] for row in rows]):
                    return size
    return 0


def states():
    def state(R, F, enabled=None, t=1):
        n = len(R[0])
        return dict(v=1, n=n, R=[[str(v) for v in row] for row in R],
                    F=[[str(v) for v in row] for row in F],
                    enabled=enabled if enabled is not None else [True]*len(R),
                    x=list(range(n)), t=t, question=len(F)-1)

    # Exhaustive, including zero rows and rank changes. 5^4 + 3^6 = 1,354.
    for values in product(range(-2, 3), repeat=4):
        yield state([values[:2]], [values[2:]])
    for values in product(range(-1, 2), repeat=6):
        yield state([values[:2], values[2:4]], [values[4:]])
    rng = random.Random(20261103)
    for i in range(250):
        n, m, k = rng.randint(2, 4), rng.randint(1, 4), rng.randint(1, 3)
        limit = 99 if i % 11 == 0 else 9
        entry = lambda: str(Fraction(rng.randint(-limit, limit), rng.randint(1, limit)))
        R = [[entry() for _ in range(n)] for _ in range(m)]
        F = [[entry() for _ in range(n)] for _ in range(k)]
        if i % 3 == 0:
            R[-1] = R[0].copy()
        if i % 7 == 0:
            F[0] = R[0].copy()
        yield state(R, F, [rng.choice([True, False]) for _ in range(m)], rng.randint(-4, 4))


def audit(node=None):
    executable = node or shutil.which('node')
    if not executable:
        raise RuntimeError('Node.js is required for the independent browser-model audit.')
    cases = list(states())
    script = """import fs from 'node:fs';
import {analyzeRecovery,repairExperiment} from './website/assets/recovery-lab-core.mjs';
const states=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(states.map(s=>({result:analyzeRecovery(s),repaired:analyzeRecovery(repairExperiment(s))}))));"""
    run = subprocess.run([executable, '--input-type=module', '-e', script], cwd=ROOT,
                         input=json.dumps(cases), text=True, encoding='utf-8', capture_output=True, timeout=45, check=True)
    records = json.loads(run.stdout)
    if len(records) != len(cases):
        raise AssertionError('Browser result count differs from the generated case count.')
    dot = lambda a, b: sum((x*y for x, y in zip(a, b)), Fraction(0))
    parse = lambda rows: [[Fraction(v) for v in row] for row in rows]
    checked_rules = checked_witnesses = 0
    for index, (case, record) in enumerate(zip(cases, records)):
        r, repaired = record['result'], record['repaired']
        R, F = parse(case['R']), parse(case['F'])
        A = [row for row, enabled in zip(R, case['enabled']) if enabled]
        rank = rank_by_minors(A)
        assert r['rank'] == rank, (index, 'rank')
        assert r['nullity'] == case['n']-rank, (index, 'nullity')
        kernel = parse(r['kernel'])
        assert len(kernel) == r['nullity'] and rank_by_minors(kernel) == len(kernel), (index, 'kernel basis')
        assert all(dot(row, w) == 0 for row in A for w in kernel), (index, 'kernel equations')
        reduced, transform = parse(r['rref']), parse(r['transform'])
        for i, row in enumerate(reduced):
            assert [sum((transform[i][k]*A[k][j] for k in range(len(A))), Fraction(0))
                    for j in range(case['n'])] == row, (index, 'row-operation identity')
        expected_recoverable = 0
        for f, question in zip(F, r['questions']):
            expected = rank_by_minors(A+[f]) == rank
            assert question['recoverable'] == expected, (index, 'recoverability')
            expected_recoverable += expected
            if expected:
                weights = [Fraction(v) for v in question['weights']]
                assert all(weights[i] == 0 for i, enabled in enumerate(case['enabled']) if not enabled)
                assert [sum((weights[i]*R[i][j] for i in range(len(R))), Fraction(0))
                        for j in range(case['n'])] == f, (index, 'F = GR')
                checked_rules += 1
            else:
                w = [Fraction(v) for v in question['witness']]
                assert all(dot(row, w) == 0 for row in A), (index, 'Rw = 0')
                assert dot(f, w) != 0 and str(dot(f, w)) == question['change'], (index, 'Fw != 0')
                checked_witnesses += 1
        assert r['recoverable'] == expected_recoverable
        expected_extra = rank_by_minors(A+F)-rank
        assert r['repair']['additional'] == expected_extra, (index, 'minimal repair')
        assert repaired['recoverable'] == len(F), (index, 'repair sufficiency')
        assert len(repaired['state']['R']) == max(1,rank+expected_extra), (index, 'repair size')
        motion = r['motion']
        assert motion['summary'] == motion['movedSummary'], (index, 'collision summaries')
        x, moved, direction = [[Fraction(v) for v in motion[key]] for key in ('x','moved','direction')]
        assert all(b == a+case['t']*w for a, b, w in zip(x, moved, direction)), (index, 'motion')
        assert [str(dot(f,x)) for f in F] == motion['answers']
        assert [str(dot(f,moved)) for f in F] == motion['movedAnswers']
    return dict(status='passed',cases=len(cases),exhaustive_cases=1354,seeded_rational_cases=250,
                seed=20261103,recovery_rules=checked_rules,obstruction_witnesses=checked_witnesses,
                independent_oracle='Python Fraction arithmetic; rank from determinants of minors, not row reduction',
                assertion_tested='Exact recovery rules, obstruction witnesses, kernel bases, row-operation identities, collisions and minimal sufficient repairs for every generated case',
                non_claim='Finite software validation; no new manuscript proof review or Lean execution')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.node)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))

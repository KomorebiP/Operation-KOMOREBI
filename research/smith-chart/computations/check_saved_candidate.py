"""Check recorded decimal candidate values at exact rational frequencies.

Only the saved decimals are tested; nearby real parameter values are not excluded.
"""
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent
FIT = ROOT / 'verification/five-node-fit-003.json'
FIT_SHA256 = 'f393c245f5b396527d5af5553609f9b7642390b77fe12e5364a9ecd80c3cf7cd'
P = (450, 1385, 2477, 2200, 1142, 335, 75)
D = (150, 795, 1375, 1720, 1250, 445, 25)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def polynomial(coefficients, s):
    value = Q(0)
    for coefficient in coefficients:
        value = value * s + coefficient
    return value


def solve(matrix, rhs):
    # Exact Gauss-Jordan elimination with row pivoting.
    rows = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for column in range(len(rhs)):
        pivot = next((i for i in range(column, len(rhs)) if rows[i][column]), None)
        if pivot is None:
            raise ValueError('Singular exact nodal matrix')
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for i in range(len(rhs)):
            if i == column:
                continue
            multiple = rows[i][column]
            rows[i] = [x - multiple * y for x, y in zip(rows[i], rows[column])]
    return [row[-1] for row in rows]


def candidate_impedance(s, edges, reactives, conductances, values):
    admittances = list(conductances)
    for (kind, index), value in zip(reactives, values):
        admittances[index] += value * (s if kind == 'C' else 1 / s)
    matrix = [[Q(0) for _ in range(4)] for _ in range(4)]
    for (u, v), admittance in zip(edges, admittances):
        for node, sign in ((u, 1), (v, -1)):
            if node == 0:
                continue
            for other, other_sign in ((u, 1), (v, -1)):
                if other != 0:
                    matrix[node - 1][other - 1] += sign * other_sign * admittance
    return solve(matrix, [Q(1), Q(0), Q(0), Q(0)])[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='Optional new JSON receipt; never overwritten')
    args = parser.parse_args()
    source, raw_fit = Path(__file__).read_bytes(), FIT.read_bytes()
    if sha(raw_fit) != FIT_SHA256:
        raise RuntimeError('Recorded fit differs from the pinned input')
    fit = json.loads(raw_fit, parse_float=str)
    best = min(fit['results'], key=lambda row: Q(row['training_error']))
    if fit['candidate_id'] != 142 or best['start'] != 37:
        raise RuntimeError('Unexpected saved candidate')
    conductances = [Q(value) for value in best['conductances']]
    values = [Q(value) for value in best['reactive_admittance_parameters']]
    if len(conductances) != 10 or len(values) != 6 or min(conductances + values) <= 0:
        raise RuntimeError('Invalid candidate parameters')
    results = []
    for s in (Q(1, 10), Q(1), Q(10)):
        target = polynomial(P, s) / polynomial(D, s)
        candidate = candidate_impedance(s, fit['edges'], fit['reactives'], conductances, values)
        difference = candidate - target
        if difference == 0:
            raise AssertionError('Expected a nonzero witness for the saved decimal parameters')
        scaled = abs(difference) / (1 + abs(target))
        results.append({'s': str(s), 'difference_numerator': str(difference.numerator),
                        'difference_denominator': str(difference.denominator),
                        'scaled_absolute_error_approx': float(scaled)})
    if Path(__file__).read_bytes() != source or sha(FIT.read_bytes()) != FIT_SHA256:
        raise RuntimeError('An input changed during the exact check')
    receipt = {'status': 'PASS', 'python': platform.python_version(), 'script_sha256': sha(source),
               'fit_receipt_sha256': FIT_SHA256, 'candidate_id': 142, 'start': best['start'],
               'parameter_interpretation': 'Each recorded decimal is an exact rational number.',
               'method': 'Fraction-valued grounded nodal matrix and exact Gauss-Jordan elimination.',
               'results': results,
               'scope': 'The recorded decimal fit is not an exact realization at these points; nearby real values and other networks are not excluded.'}
    text = json.dumps(receipt, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as out:
            out.write(text)
    print(text, end='')


if __name__ == '__main__':
    main()

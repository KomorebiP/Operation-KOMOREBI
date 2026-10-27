"""Independent reviewer checks for the Block 19 finite computation.

Uses a separate list-of-rows matrix implementation for arithmetic benchmarks,
exhaustive F2 idempotents, and a coefficient-level Newton identity. The main
experiment itself is replayed independently by its separate bounded manifest.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import exact_summands as predecessor

ROOT = Path(__file__).resolve().parents[1]


def multiply(a, b):
    cols = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in cols] for row in a]


def flatten(a):
    return tuple(x for row in a for x in row)


def poly_mul(a, b):
    out = [0] * (len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def poly_sub(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0)-(b[i] if i < len(b) else 0) for i in range(n)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    source = ROOT/'checks/exact_families.py'
    helpers = ROOT/'checks/exact_summands.py'
    original = ROOT/'checks/families_run/exact_families.json'
    replay = ROOT/'checks/families_independent_run/exact_families.json'
    assert original.read_bytes() == replay.read_bytes()
    report = json.loads(replay.read_text())
    assert report['source_sha256'] == sha256(source.read_bytes()).hexdigest()
    assert report['predecessor_helpers_sha256'] == sha256(helpers.read_bytes()).hexdigest()
    expected = [('C2', r, p, k) for r, p, k in product((3, 4, 5), (2, 3), (1, 2, 3))]
    expected += [('Klein4', r, 2, k) for r, k in product((3, 4, 5), (1, 2, 3))]
    expected += [('S3', r, p, k) for r, p, k in product((3, 4), (2, 3, 5), (1, 2, 3))]
    expected += [('C4', r, 2, k) for r, k in product((3, 4), (1, 2))]
    actual = [(r['family'], r['summands'], r['p'], r['k']) for r in report['constructed_cases']]
    assert len(set(actual)) == len(actual) == 49
    assert actual == expected
    assert sum(2*r for _, r, _, _ in expected) == 370
    assert report['totals']['constructed_family_lifts'] == 98
    assert report['totals']['constructed_projectors'] == 370
    assert report['totals']['constructed_newton_iterations'] == 324+162+270+70 == 826
    assert report['totals']['total_newton_iterations'] == 826+8*4+2*4 == 866
    helper_checks = 0
    for n, variant in product((0, 1, 2, 3, 4, 8), range(5)):
        a = [[Fraction((i+2)*(j+3)+variant-7, 2+variant) for j in range(n)] for i in range(n)]
        b = [[Fraction((i-j)*(variant+3)+1, 3+variant) for j in range(n)] for i in range(n)]
        assert flatten(multiply(a, b)) == predecessor.mul(flatten(a), flatten(b), n)
        helper_checks += 1
    idempotents = []
    for entries in product((0, 1), repeat=4):
        a = [list(entries[:2]), list(entries[2:])]
        squared = multiply(a, a)
        if all((squared[i][j]-a[i][j]) % 2 == 0 for i, j in product(range(2), repeat=2)):
            idempotents.append(a)
    assert len(idempotents) == 8
    assert sum(a not in ([[0, 0], [0, 0]], [[1, 0], [0, 1]]) for a in idempotents) == 6
    # Equality as coefficient lists checks the polynomial identity independently
    # of the production matrix evaluation and its matrix multiplication helper.
    correction, defect = [0, 0, 3, -2], [0, -1, 1]
    lhs = poly_sub(poly_mul(correction, correction), correction)
    rhs = poly_mul(poly_mul(defect, defect), [-3, -4, 4])
    assert lhs == rhs == [0, 0, -3, 2, 9, -12, 4]
    # Necessary loss of one 2-adic digit: every lift of the prescribed entry
    # 2 modulo 4 violates the scalar commutation equation modulo 8.
    candidates = [x for x in range(8) if x % 4 == 2]
    assert candidates == [2, 6] and all(2*x % 8 == 4 for x in candidates)
    out = {
        'verdict': 'PASS: independently replayed and reviewed finite assertion',
        'source_sha256': sha256(source.read_bytes()).hexdigest(),
        'helpers_sha256': sha256(helpers.read_bytes()).hexdigest(),
        'identical_result_sha256': sha256(replay.read_bytes()).hexdigest(),
        'all_parameter_cases_match': len(expected),
        'independent_rational_matrix_products': helper_checks,
        'independent_F2_matrices_enumerated': 16,
        'independent_F2_idempotents': len(idempotents),
        'newton_defect_polynomial_coefficients': lhs,
        'independent_precision_obstruction_entries': candidates,
        'non_claims': ['These checks do not establish universal projector lifting or arithmetic compatibility.']
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()

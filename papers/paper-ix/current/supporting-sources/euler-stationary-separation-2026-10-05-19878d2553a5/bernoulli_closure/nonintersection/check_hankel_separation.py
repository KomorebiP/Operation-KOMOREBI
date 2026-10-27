"""Exact finite checks of the actual Bernoulli Hankel separation theorem.

No parameter digits or Euler critical values are computed. The independent
Bernoulli recurrence supplies all moments; Jacobi formulas are then checked
against those moments rather than used to generate them.
"""
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import json
import sys


def v_int(n):
    if not n:
        raise ValueError('valuation of zero')
    n = abs(n)
    return (n & -n).bit_length() - 1


def val(x):
    x = F(x)
    return None if not x else v_int(x.numerator) - v_int(x.denominator)


def bernoulli(N):
    b = [F(1)]
    for n in range(1, N + 1):
        b.append(-sum(comb(n + 1, j) * b[j] for j in range(n)) / F(n + 1))
    return b


def add(a, b):
    out = [F(0)] * max(len(a), len(b))
    for i, t in enumerate(a):
        out[i] += t
    for i, t in enumerate(b):
        out[i] += t
    return out


def scale(a, c):
    return [F(c) * t for t in a]


def mul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, s in enumerate(a):
        for j, t in enumerate(b):
            out[i + j] += s * t
    return out


def det(matrix):
    a = [list(map(F, row)) for row in matrix]
    out = F(1)
    for k in range(len(a)):
        if not a[k][k]:
            pivot = next((j for j in range(k + 1, len(a)) if a[j][k]), None)
            if pivot is None:
                return F(0)
            a[k], a[pivot] = a[pivot], a[k]
            out = -out
        pivot = a[k][k]
        out *= pivot
        for i in range(k + 1, len(a)):
            ratio = a[i][k] / pivot
            for j in range(k + 1, len(a)):
                a[i][j] -= ratio * a[k][j]
    return out


def rho(n):
    return F(-n ** 4, 4 * n * n - 1)


def expected(m):
    return 2 * m * (m - 1) + 4 * sum(v_int(factorial(k)) for k in range(m))


def main():
    result = Path(sys.argv[1])
    b = bernoulli(112)
    D = [(2 - 4 ** n) * b[2 * n] for n in range(57)]
    actual = [2 * b[2 * n] for n in range(57)]
    assert D[0] == 1 and D[1] == F(-1, 3)
    polys = [[F(1)], [F(1, 3), F(1)]]
    for n in range(1, 8):
        bn = rho(2 * n) + rho(2 * n + 1)
        an = rho(2 * n) * rho(2 * n - 1)
        polys.append(add(mul([-bn, F(1)], polys[n]), scale(polys[n-1], -an)))
    def moment(p, shift=0):
        return sum(t * D[shift + k] for k, t in enumerate(p))
    orthogonality = 0
    for n, p in enumerate(polys):
        cn = F(4 ** n * factorial(n) ** 2)
        assert all(t == 0 or val(t) >= 0 for t in p)
        for j in range(n):
            assert moment([F(0)] * j + p) == 0
            orthogonality += 1
        norm = moment(mul(p, p))
        assert val(norm / cn ** 2) == 0
    depleted = []
    for x in range(9):
        for m in range(1, 9):
            value = det([[D[x + i + j] for j in range(m)] for i in range(m)])
            assert val(value) == expected(m)
            depleted.append({'x': x, 'm': m, 'valuation': val(value)})
    transferred = []
    for r in range(1, 41):
        for m in range(1, 9):
            bound = 4 * (m - 1) + 4 * v_int(factorial(m - 1))
            if 2 * r - 1 <= bound:
                continue
            value = det([[actual[r + i + j] for j in range(m)] for i in range(m)])
            assert val(value) == expected(m)
            transferred.append({'r': r, 'm': m, 'valuation': val(value),
                                'entry_precision_margin': 2 * r - 1 - bound})
    boundary = []
    for r, target in [(1, 1), (2, 3), (3, 4)]:
        value = actual[r] * actual[r + 2] - actual[r + 1] ** 2
        assert val(value) == target
        boundary.append({'r': r, 'm': 2, 'determinant': str(value),
                         'valuation': val(value), 'depleted_valuation': 4})
    payload = {
        'status': 'passed', 'arithmetic': 'exact rational Fraction',
        'orthogonality_checks': orthogonality,
        'unit_norm_checks': len(polys),
        'depleted_checks': len(depleted), 'actual_transfer_checks': len(transferred),
        'depleted_records': depleted, 'actual_records': transferred,
        'boundary_records': boundary,
        'non_claims': ['No proof by finite enumeration', 'No computation of Phi',
                       'No terminal161 closure', 'No new parameter digits']
    }
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({k: payload[k] for k in ['status', 'orthogonality_checks',
          'unit_norm_checks', 'depleted_checks', 'actual_transfer_checks']}))


if __name__ == '__main__':
    main()

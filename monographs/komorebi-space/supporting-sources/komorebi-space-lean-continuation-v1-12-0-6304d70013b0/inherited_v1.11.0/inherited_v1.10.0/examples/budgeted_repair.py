#!/usr/bin/env python3
"""Exact rational protected quadratic repair, with its actual kernel metric.

Run with no arguments for three reproducible examples. --input accepts a JSON
object with keys d, p, f, alpha and optional measured_residual. Use integers or
fraction strings, not JSON floating-point numbers. A nonorthogonal nullspace
basis is handled with its Gram matrix. This is exact tested Python, not a
universally Lean-verified implementation.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from typing import Any, Sequence

Rational = int | str | F
Vector = list[F]
Matrix = list[Vector]

def rational(x: Rational) -> F:
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise TypeError('Use an integer or fraction string, not a float or bool')
    try:
        return F(x)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f'Invalid rational: {x!r}') from exc

def vector(xs: Sequence[Rational]) -> Vector:
    if isinstance(xs, (str, bytes)):
        raise TypeError('A vector must be a sequence of rational entries')
    return [rational(x) for x in xs]

def matrix(xs: Sequence[Sequence[Rational]], n: int | None = None) -> Matrix:
    if isinstance(xs, (str, bytes)):
        raise TypeError('A matrix must be a sequence of rows')
    out = [vector(row) for row in xs]
    width = n if n is not None else (len(out[0]) if out else 0)
    if any(len(row) != width for row in out):
        raise ValueError('Matrix rows must have the declared common length')
    return out

def dot(a: Vector, b: Vector) -> F:
    if len(a) != len(b):
        raise ValueError('Dot-product dimensions differ')
    return sum((x*y for x, y in zip(a, b)), F(0))

def mv(a: Matrix, x: Vector) -> Vector:
    return [dot(row, x) for row in a]

def transpose(a: Matrix) -> Matrix:
    return [list(col) for col in zip(*a)] if a else []

def mm(a: Matrix, b: Matrix) -> Matrix:
    bt = transpose(b)
    if a and len(a[0]) != len(b):
        raise ValueError('Matrix-product dimensions differ')
    return [[dot(row, col) for col in bt] for row in a]

def sub(a: Vector, b: Vector) -> Vector:
    if len(a) != len(b):
        raise ValueError('Vector dimensions differ')
    return [x-y for x, y in zip(a, b)]

def norm2(a: Vector) -> F:
    return dot(a, a)

def rref(a: Matrix, width: int | None = None) -> tuple[Matrix, list[int]]:
    """Gauss--Jordan elimination with exact arithmetic and explicit pivots."""
    b = [row[:] for row in a]
    n = width if width is not None else (len(b[0]) if b else 0)
    if any(len(row) != n for row in b):
        raise ValueError('RREF row length mismatch')
    pivots: list[int] = []
    i = 0
    for j in range(n):
        pivot = next((k for k in range(i, len(b)) if b[k][j]), None)
        if pivot is None:
            continue
        b[i], b[pivot] = b[pivot], b[i]
        scale = b[i][j]
        b[i] = [x/scale for x in b[i]]
        for k in range(len(b)):
            if k != i and b[k][j]:
                factor = b[k][j]
                b[k] = [x-factor*y for x, y in zip(b[k], b[i])]
        pivots.append(j)
        i += 1
        if i == len(b):
            break
    return b, pivots

def kernel_basis(p: Matrix, n: int) -> Matrix:
    """Return an n-by-k matrix whose columns form a rational kernel basis."""
    rr, pivots = rref(p, n)
    free = [j for j in range(n) if j not in pivots]
    columns: Matrix = []
    for j in free:
        x = [F(0) for _ in range(n)]
        x[j] = F(1)
        for i, pivot in enumerate(pivots):
            x[pivot] = -rr[i][j]
        columns.append(x)
    return [[columns[j][i] for j in range(len(columns))] for i in range(n)]

def solve_square(a: Matrix, b: Vector) -> Vector:
    n = len(a)
    if len(b) != n or any(len(row) != n for row in a):
        raise ValueError('Expected a square matrix and matching right side')
    if n == 0:
        return []
    rr, pivots = rref([row+[rhs] for row, rhs in zip(a, b)], n+1)
    if pivots != list(range(n)):
        raise ValueError('System does not have a unique solution')
    return [rr[i][-1] for i in range(n)]

def budget_certificate(r: Vector, a: Vector, v: Vector, alpha: F) -> dict[str, Any]:
    """Encode WR07's exact unnormalized dual witness without rounding square roots.

    When v != 0, z = v/sqrt(witness_norm_squared) is the unit witness.
    Its actual restricted adjoint is alpha*a by the certified normal equation.
    All norm data remain squared rationals. A zero residual uses z = 0.
    """
    energy, residual2 = norm2(a), norm2(v)
    identity = dot(r, v)-alpha*energy-residual2
    if identity:
        raise ArithmeticError('Budget dual equality failed')
    return {'witness_numerator': v, 'witness_norm_squared': residual2,
            'normalization': 'zero witness' if residual2 == 0 else 'divide numerator by square root of witness_norm_squared',
            'budget_norm_squared': energy,
            'restricted_adjoint_numerator': [alpha*x for x in a],
            'optimal_residual_squared': residual2,
            'dual_equality_residual': identity,
            'scope': 'Optimal at the returned correction budget for this fixed model and target data; WR07.'}

def regularize(t: Sequence[Sequence[Rational]], r: Sequence[Rational],
               alpha: Rational) -> dict[str, Any]:
    """Regularize T a = r in standard Euclidean coordinates."""
    tt = matrix(t)
    if not tt or not tt[0]:
        raise ValueError('The forward matrix must have positive dimensions')
    n = len(tt[0])
    rr = vector(r)
    if len(rr) != len(tt):
        raise ValueError('Residual-data dimension mismatch')
    aa = rational(alpha)
    if aa <= 0:
        raise ValueError('alpha must be strictly positive')
    normal = mm(transpose(tt), tt)
    for i in range(n):
        normal[i][i] += aa
    a = solve_square(normal, mv(transpose(tt), rr))
    v = sub(rr, mv(tt, a))
    return {'correction': a, 'fit_residual': v, 'alpha': aa,
            'correction_norm_squared': norm2(a), 'residual_norm_squared': norm2(v),
            'normal_residual': sub(mv(transpose(tt), v), [aa*x for x in a]),
            'objective': norm2(v)+aa*norm2(a),
            'budget_certificate': budget_certificate(rr, a, v, aa)}

def protected_regularize(d: Sequence[Sequence[Rational]],
                         p: Sequence[Sequence[Rational]],
                         f: Sequence[Rational], alpha: Rational,
                         measured_residual: Sequence[Rational] | None = None) -> dict[str, Any]:
    """Minimize ||D a - r||^2 + alpha ||a||^2 subject to P a = 0.

    By default r = D f. With measured_residual, the fit residual uses that data,
    while true_candidate_residual still reports D(f-a) for the supplied model.
    """
    ff = vector(f)
    n = len(ff)
    if n == 0:
        raise ValueError('The ambient candidate must have positive dimension')
    dd, pp = matrix(d, n), matrix(p, n)
    if not dd:
        raise ValueError('At least one residual coordinate is required')
    aa = rational(alpha)
    if aa <= 0:
        raise ValueError('alpha must be strictly positive')
    r = mv(dd, ff) if measured_residual is None else vector(measured_residual)
    if len(r) != len(dd):
        raise ValueError('Measured residual dimension mismatch')
    basis = kernel_basis(pp, n)
    k = len(basis[0])
    if k:
        gram = mm(transpose(basis), basis)
        s = mm(dd, basis)
        ss = mm(transpose(s), s)
        normal = [[ss[i][j]+aa*gram[i][j] for j in range(k)] for i in range(k)]
        coordinates = solve_square(normal, mv(transpose(s), r))
        a = mv(basis, coordinates)
        residual = sub(r, mv(dd, a))
        normal_residual = sub(mv(transpose(s), residual),
                              [aa*x for x in mv(gram, coordinates)])
    else:
        gram, coordinates, normal_residual = [], [], []
        a, residual = [F(0)]*n, r[:]
    candidate = sub(ff, a)
    before, after = mv(pp, ff), mv(pp, candidate)
    if before != after or any(normal_residual):
        raise ArithmeticError('Internal preservation/normal-equation certificate failed')
    return {'alpha': aa, 'kernel_dimension': k, 'kernel_basis': basis, 'kernel_gram': gram,
            'coordinates': coordinates, 'correction': a, 'candidate': candidate,
            'target_residual': r, 'fit_residual': residual,
            'true_candidate_residual': mv(dd, candidate),
            'protected_before': before, 'protected_after': after,
            'normal_coordinate_residual': normal_residual,
            'correction_norm_squared': norm2(a), 'residual_norm_squared': norm2(residual),
            'objective': norm2(residual)+aa*norm2(a),
            'budget_certificate': budget_certificate(r, a, residual, aa)}

def diagonal_enclosure(m: int, cutoff: int) -> dict[str, Any]:
    """Rational enclosures for the actual infinite regularized escape energies."""
    if isinstance(m, bool) or isinstance(cutoff, bool) or not isinstance(m, int) or not isinstance(cutoff, int):
        raise TypeError('m and cutoff must be integers')
    if m < 1 or cutoff < m:
        raise ValueError('Require 1 <= m <= cutoff')
    a = sum((F(m**4, (m*m+n*n)**2) for n in range(1, cutoff+1)), F(0))
    b = sum((F(n*n, (m*m+n*n)**2) for n in range(1, cutoff+1)), F(0))
    return {'m': m, 'cutoff': cutoff, 'alpha': F(1, m*m),
            'energy_interval': [a, a+F(m**4, 3*cutoff**3)],
            'residual_square_interval': [b, b+F(1, cutoff)],
            'scope': 'Infinite-tail inequalities proved in WR10. Finite sums do not replace that proof.'}

def jsonable(obj: Any) -> Any:
    if isinstance(obj, F):
        return str(obj)
    if isinstance(obj, dict):
        return {key: jsonable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(value) for value in obj]
    return obj

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='JSON problem (defaults to demonstrations)')
    args = parser.parse_args()
    try:
        if args.input:
            problem = json.loads(args.input.read_text())
            if not isinstance(problem, dict):
                raise ValueError('Input JSON must be an object')
            unknown = set(problem)-{'d', 'p', 'f', 'alpha', 'measured_residual'}
            if unknown:
                raise ValueError(f'Unknown keys: {sorted(unknown)}')
            result = protected_regularize(**problem)
        else:
            result = {
                'scope': 'Exact rational finite examples. Not a universal Python-to-Lean refinement.',
                'protected_first_coordinate': protected_regularize([[1,1]], [[1,0]], [1,0], 1),
                'nonorthogonal_kernel_basis': protected_regularize([[1,0]], [[1,-1]], [1,0], 1),
                'fully_protected': protected_regularize([[1,1]], [[1,0],[0,1]], [1,0], 1),
                'dual_witness_example': regularize([[1,0],[0,'1/2']], [1,1], 1),
                'infinite_tail_enclosure': diagonal_enclosure(4,32)}
        print(json.dumps(jsonable(result), indent=2))
        return 0
    except (ValueError, TypeError, OSError, ArithmeticError) as exc:
        parser.exit(2, f'Input or arithmetic error: {exc}\n')

if __name__ == '__main__':
    raise SystemExit(main())

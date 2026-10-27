#!/usr/bin/env python3
"""Exact rational finite-matrix evaluation of approximate-sufficiency bounds.

Uses the induced infinity norm (maximum absolute row sum). The executable is
not extracted from Lean or formally verified; the general analytic theorem is
separate. Only whole-map norm bounds, never sample fits, are used as inputs.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import json
from pathlib import Path
from typing import Iterable, Sequence


def rational(x: object) -> F:
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise ValueError('Use exact integers or rational strings, not floats/bools')
    if isinstance(x, str) and len(x) > 256:
        raise ValueError('Rational input exceeds 256 characters')
    try:
        q = F(x)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('Invalid rational input') from exc
    if max(q.numerator.bit_length(), q.denominator.bit_length()) > 1024:
        raise ValueError('Rational input exceeds 1024-bit cap')
    return q


@dataclass(frozen=True)
class Matrix:
    rows: tuple[tuple[F, ...], ...]
    cols: int

    def __post_init__(self) -> None:
        if self.cols < 0 or any(len(row) != self.cols for row in self.rows):
            raise ValueError('Invalid matrix shape')

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), self.cols

    @staticmethod
    def zero(n: int, m: int) -> Matrix:
        return Matrix(tuple(tuple(F(0) for _ in range(m)) for _ in range(n)), m)

    @staticmethod
    def identity(n: int) -> Matrix:
        return Matrix(tuple(tuple(F(i == j) for j in range(n)) for i in range(n)), n)

    @staticmethod
    def parse(data: object, n: int, m: int) -> Matrix:
        if not isinstance(data, list) or len(data) != n:
            raise ValueError('Matrix row count mismatch')
        if any(not isinstance(row, list) or len(row) != m for row in data):
            raise ValueError('Matrix column count mismatch')
        return Matrix(tuple(tuple(rational(x) for x in row) for row in data), m)

    def __add__(self, other: Matrix) -> Matrix:
        if self.shape != other.shape:
            raise ValueError('Addition shape mismatch')
        return Matrix(tuple(tuple(x + y for x, y in zip(a, b))
                            for a, b in zip(self.rows, other.rows)), self.cols)

    def __sub__(self, other: Matrix) -> Matrix:
        return self + other.scale(F(-1))

    def __matmul__(self, other: Matrix) -> Matrix:
        if self.cols != len(other.rows):
            raise ValueError('Composition shape mismatch')
        return Matrix(tuple(tuple(sum((row[k] * other.rows[k][j]
                        for k in range(self.cols)), F(0))
                        for j in range(other.cols)) for row in self.rows), other.cols)

    def scale(self, c: F) -> Matrix:
        return Matrix(tuple(tuple(c*x for x in row) for row in self.rows), self.cols)

    def norm(self) -> F:
        return max((sum((abs(x) for x in row), F(0)) for row in self.rows), default=F(0))

    def json(self) -> list[list[str]]:
        return [[str(x) for x in row] for row in self.rows]


@dataclass(frozen=True)
class Model:
    q: Matrix
    T: tuple[Matrix, ...]
    U: tuple[Matrix, ...]
    O: Matrix
    V: Matrix

    def __post_init__(self) -> None:
        z, x = self.q.shape
        y, ox = self.O.shape
        if ox != x or self.V.shape != (y, z) or len(self.T) != len(self.U):
            raise ValueError('Model dimensions or alphabets disagree')
        if any(t.shape != (x, x) for t in self.T) or any(u.shape != (z, z) for u in self.U):
            raise ValueError('Operation dimensions disagree')

    def step_errors(self) -> tuple[Matrix, ...]:
        return tuple(self.q @ t - u @ self.q for t, u in zip(self.T, self.U))

    def automatic_bounds(self) -> tuple[tuple[F, ...], tuple[F, ...], tuple[F, ...], F]:
        return (tuple(t.norm() for t in self.T), tuple(u.norm() for u in self.U),
                tuple(d.norm() for d in self.step_errors()), (self.O - self.V @ self.q).norm())


def word(ops: Sequence[Matrix], letters: Sequence[int], dim: int) -> Matrix:
    result = Matrix.identity(dim)
    for i in letters:
        if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(ops):
            raise ValueError('Word index outside operation alphabet')
        result = ops[i] @ result
    return result


def envelope(a: Sequence[F], b: Sequence[F], eps: Sequence[F], letters: Sequence[int]) -> tuple[F, F, F]:
    fine, coarse, error = F(1), F(1), F(0)
    for i in letters:
        error = b[i] * error + eps[i] * fine
        fine *= a[i]
        coarse *= b[i]
    return fine, coarse, error


def validate_bounds(model: Model, a: Sequence[F], b: Sequence[F], eps: Sequence[F], eta: F) -> None:
    if any(len(v) != len(model.T) for v in (a, b, eps)):
        raise ValueError('Envelope length mismatch')
    if any(c < 0 for v in (a, b, eps) for c in v) or eta < 0:
        raise ValueError('Norm bounds must be nonnegative')
    actual = model.automatic_bounds()
    if any(c > bound for v, supplied in zip(actual[:3], (a, b, eps)) for c, bound in zip(v, supplied)):
        raise ValueError('Supplied bound underestimates a whole-map norm')
    if actual[3] > eta:
        raise ValueError('Supplied readout bound is too small')


def evaluate(model: Model, letters: Sequence[int]) -> dict[str, object]:
    z, x = model.q.shape
    tw, uw = word(model.T, letters, x), word(model.U, letters, z)
    a, b, eps, eta = model.automatic_bounds()
    fine, coarse, error_bound = envelope(a, b, eps, letters)
    error = model.q @ tw - uw @ model.q
    output = model.O @ tw - model.V @ uw @ model.q
    output_bound = eta * fine + model.V.norm() * error_bound
    if error.norm() > error_bound or output.norm() > output_bound:
        raise ArithmeticError('Exact norm inequality failed')
    return {'word': list(letters), 'fine_gain': str(fine), 'coarse_gain': str(coarse),
            'state_error_norm': str(error.norm()), 'state_error_bound': str(error_bound),
            'output_error_norm': str(output.norm()), 'output_error_bound': str(output_bound)}


def load(data: dict[str, object]) -> tuple[Model, list[list[int]]]:
    dims = data.get('dimensions')
    if not isinstance(dims, list) or len(dims) != 3:
        raise ValueError('dimensions must be [fine, reduced, output]')
    if any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= 8 for x in dims):
        raise ValueError('Dimensions must be integers in 0..8')
    x, z, y = dims
    T, U = data.get('T'), data.get('U')
    if not isinstance(T, list) or not isinstance(U, list) or len(T) != len(U) or len(T) > 4:
        raise ValueError('Matching alphabets of size 0..4 are required')
    model = Model(Matrix.parse(data.get('q'), z, x), tuple(Matrix.parse(t, x, x) for t in T),
                  tuple(Matrix.parse(u, z, z) for u in U), Matrix.parse(data.get('O'), y, x),
                  Matrix.parse(data.get('V'), y, z))
    words = data.get('words', [[]])
    if not isinstance(words, list) or len(words) > 500 or any(not isinstance(w, list) or len(w) > 64 for w in words):
        raise ValueError('At most 500 words, each of length at most 64, are allowed')
    for w in words:
        if any(isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(T) for i in w):
            raise ValueError('Invalid operation index')
    return model, words


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.input.stat().st_size > 1_000_000:
        p.error('Input exceeds 1 MB cap')
    try:
        data = json.loads(args.input.read_text())
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object')
        model, words = load(data)
        a, b, eps, eta = model.automatic_bounds()
        result = {'schema_version': 1, 'arithmetic': 'exact rational', 'norm': 'induced infinity norm',
                  'step_true_norms': list(map(str, a)), 'step_reduced_norms': list(map(str, b)),
                  'step_error_norms': list(map(str, eps)), 'readout_error_norm': str(eta),
                  'words': [evaluate(model, w) for w in words],
                  'boundary': 'Finite exact Python checks. Not Lean-verified executable code or inference from sampled data.'}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    except (ValueError, KeyError, ArithmeticError) as exc:
        p.error(str(exc))
    print(json.dumps({'passed': True, 'words': len(words), 'output': str(args.output)}))

if __name__ == '__main__':
    main()

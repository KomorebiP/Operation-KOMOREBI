#!/usr/bin/env python3
"""Exact protected linear repair over Q, with directly checkable certificates.

Solve A y = 0 and P y = P x. A feasible certificate includes one particular
answer and a basis for all invisible exact changes. An obstructed certificate
contains rows lambda, mu with lambda A = mu P and lambda A x = 1.

This is field-linear elimination, not an integer solver or a nearest-point
algorithm. Only exact integers, Fraction objects, and rational strings are
accepted. Floats and booleans are rejected. No external packages are required.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Literal, Sequence, TypeAlias
import argparse
import json
import sys

Q = Fraction
Scalar: TypeAlias = int | str | Fraction
Vector: TypeAlias = tuple[Fraction, ...]
Matrix: TypeAlias = tuple[Vector, ...]


def rational(x: Scalar) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, str, Fraction)):
        raise TypeError("Use an integer or a rational string such as '1/2', not a float or bool.")
    try:
        return Q(x)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"Invalid rational value: {x!r}") from exc


def _matrix(rows: Sequence[Sequence[Scalar]], n: int) -> Matrix:
    result = tuple(tuple(rational(v) for v in row) for row in rows)
    if any(len(row) != n for row in result):
        raise ValueError(f"Every row must have {n} entries, matching the candidate dimension.")
    return result


def _mv(a: Matrix, x: Vector) -> Vector:
    return tuple(sum((v * w for v, w in zip(row, x)), Q(0)) for row in a)


def _left(x: Vector, a: Matrix, n: int) -> Vector:
    return tuple(sum((x[i] * a[i][j] for i in range(len(a))), Q(0)) for j in range(n))


def _reduce(a: Matrix, n: int) -> tuple[Matrix, tuple[int, ...], Matrix]:
    """Return R, pivot columns, and E with R = E A. The matrix E is invertible."""
    m = len(a)
    r = [list(row) for row in a]
    e = [[Q(i == j) for j in range(m)] for i in range(m)]
    pivots: list[int] = []
    row = 0
    for col in range(n):
        pivot = next((i for i in range(row, m) if r[i][col]), None)
        if pivot is None:
            continue
        r[row], r[pivot] = r[pivot], r[row]
        e[row], e[pivot] = e[pivot], e[row]
        scale = r[row][col]
        r[row] = [v / scale for v in r[row]]
        e[row] = [v / scale for v in e[row]]
        for i in range(m):
            if i != row and r[i][col]:
                scale = r[i][col]
                r[i] = [v - scale * w for v, w in zip(r[i], r[row])]
                e[i] = [v - scale * w for v, w in zip(e[i], e[row])]
        pivots.append(col)
        row += 1
        if row == m:
            break
    return tuple(map(tuple, r)), tuple(pivots), tuple(map(tuple, e))


@dataclass(frozen=True)
class Certificate:
    status: Literal["feasible", "obstructed"]
    answer: Vector = ()
    ambiguity_basis: tuple[Vector, ...] = ()  # Basis vectors, not rows of an operator.
    residual_witness: Vector = ()
    protected_witness: Vector = ()

    def to_dict(self) -> dict:
        if self.status == "feasible":
            return {"status": self.status, "answer": list(map(str, self.answer)),
                    "ambiguity_basis": [list(map(str, b)) for b in self.ambiguity_basis],
                    "ambiguity_dimension": len(self.ambiguity_basis),
                    "selection": "Gaussian particular answer, not necessarily nearest"}
        return {"status": self.status,
                "lambda": list(map(str, self.residual_witness)),
                "mu": list(map(str, self.protected_witness)),
                "equations": "lambda A = mu P; lambda A x = 1"}


def solve_protected(A: Sequence[Sequence[Scalar]], P: Sequence[Sequence[Scalar]],
                    x: Sequence[Scalar]) -> Certificate:
    """Return a complete affine answer description or a normalized obstruction."""
    xx = tuple(rational(v) for v in x)
    n = len(xx)
    aa, pp = _matrix(A, n), _matrix(P, n)
    t = aa + pp
    b = (Q(0),) * len(aa) + _mv(pp, xx)
    reduced, pivots, transform = _reduce(t, n)
    rhs = _mv(transform, b)
    for i in range(len(t)):
        if not any(reduced[i]) and rhs[i]:
            w = tuple(v / rhs[i] for v in transform[i])
            return Certificate("obstructed", residual_witness=tuple(-v for v in w[:len(aa)]),
                               protected_witness=w[len(aa):])
    answer = [Q(0)] * n
    for row, col in enumerate(pivots):
        answer[col] = rhs[row]
    basis = []
    for free in (j for j in range(n) if j not in pivots):
        v = [Q(0)] * n
        v[free] = Q(1)
        for row, col in enumerate(pivots):
            v[col] = -reduced[row][free]
        basis.append(tuple(v))
    return Certificate("feasible", answer=tuple(answer), ambiguity_basis=tuple(basis))


def verify_certificate(A: Sequence[Sequence[Scalar]], P: Sequence[Sequence[Scalar]],
                       x: Sequence[Scalar], certificate: Certificate) -> bool:
    """Verify equations directly; verify completeness of the basis by rank.

    Negative certificate verification is just exact multiplication. Positive
    basis completeness additionally uses elimination for its rank calculation.
    The test suite cross-checks ranks using an independent minor/determinant
    oracle. This function is not a Lean-verified refinement.
    """
    xx = tuple(rational(v) for v in x)
    n = len(xx)
    aa, pp = _matrix(A, n), _matrix(P, n)
    c = certificate
    if c.status == "obstructed":
        la, mu = c.residual_witness, c.protected_witness
        if len(la) != len(aa) or len(mu) != len(pp):
            return False
        return (_left(la, aa, n) == _left(mu, pp, n)
                and sum((v * w for v, w in zip(la, _mv(aa, xx))), Q(0)) == 1)
    if c.status != "feasible" or len(c.answer) != n:
        return False
    if any(_mv(aa, c.answer)) or _mv(pp, c.answer) != _mv(pp, xx):
        return False
    if any(len(v) != n or any(_mv(aa + pp, v)) for v in c.ambiguity_basis):
        return False
    expected_dim = n - len(_reduce(aa + pp, n)[1])
    actual_rank = len(_reduce(tuple(c.ambiguity_basis), n)[1])
    return len(c.ambiguity_basis) == expected_dim == actual_rank


def _demo() -> list[dict]:
    A, x = [[1, -1, 0]], [2, 0, 5]
    problems = [("unique", [[1, 0, 0], [0, 0, 1]]),
                ("ambiguous", [[0, 0, 1]]),
                ("obstructed", [[1, 0, 0], [0, 1, 0]])]
    out = []
    for name, P in problems:
        c = solve_protected(A, P, x)
        if not verify_certificate(A, P, x, c):
            raise RuntimeError(f"Internal verification failed for demo {name}")
        out.append({"name": name, "A": A, "P": P, "x": x, "certificate": c.to_dict()})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="JSON object with exact A, P, and x entries")
    parser.add_argument("--demo", action="store_true", help="Run the monograph's three preservation problems")
    args = parser.parse_args()
    try:
        if args.demo:
            if args.input:
                parser.error("Use either --demo or an input file, not both.")
            result = _demo()
        else:
            if args.input is None:
                parser.error("Supply an input JSON file or use --demo.")
            data = json.loads(args.input.read_text(encoding="utf-8"))
            c = solve_protected(data["A"], data["P"], data["x"])
            if not verify_certificate(data["A"], data["P"], data["x"], c):
                raise RuntimeError("Certificate failed independent equation verification.")
            result = c.to_dict()
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        print(f"protected_repair: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

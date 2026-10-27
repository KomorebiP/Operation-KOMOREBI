"""Exact finite GF(2) feasibility, ambiguity, and observation gain.

All outputs derive from the declared linear compatibility and protected data.
An inconsistency witness certifies nonexistence for the specified finite
linear system, not the unprovability of a general theorem or proof search.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
from numbers import Integral


@dataclass(frozen=True)
class AffineRealizationReport:
    feasible: bool
    rank: int
    ambiguity_dimension: int | None
    realization_count: int
    solution: tuple[int, ...] | None
    ambiguity_basis: tuple[tuple[int, ...], ...]
    obstruction_witness: tuple[int, ...] | None
    observation_gain_bits: int | None
    remaining_ambiguity_bits: int | None


def _dimension(n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 0:
        raise ValueError("dimension must be a nonnegative integer")
    return int(n)


def _bits(values: Sequence[int], length: int, label: str) -> list[int]:
    values = list(values)
    if len(values) != length or any(not isinstance(v, Integral) or v not in (0, 1) for v in values):
        raise ValueError(f"{label} requires binary integer entries and the declared length")
    return [int(v) for v in values]


def _validate_matrix(rows: Sequence[Sequence[int]], n: int) -> list[list[int]]:
    n = _dimension(n)
    return [_bits(row, n, "GF(2) row") for row in rows]


def _rref(rows: Sequence[Sequence[int]], n: int, rhs: Sequence[int] | None = None):
    """Reduced row echelon form, tracking combinations of input equations."""
    m = len(rows)
    if rhs is not None and (len(rhs) != m or any(t not in (0, 1) for t in rhs)):
        raise ValueError("right hand side must be a GF(2) vector")
    a = [list(row) + ([rhs[i]] if rhs is not None else []) for i, row in enumerate(rows)]
    operations = [[int(i == j) for j in range(m)] for i in range(m)]
    pivots: list[int] = []
    pivot_row = 0
    for col in range(n):
        pivot = next((i for i in range(pivot_row, m) if a[i][col]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        operations[pivot_row], operations[pivot] = operations[pivot], operations[pivot_row]
        for row in range(m):
            if row != pivot_row and a[row][col]:
                a[row] = [x ^ y for x, y in zip(a[row], a[pivot_row])]
                operations[row] = [x ^ y for x, y in zip(operations[row], operations[pivot_row])]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == m:
            break
    return a, pivots, operations


def _rank(rows: Sequence[Sequence[int]], n: int) -> int:
    return len(_rref(rows, n)[1])


def analyze_affine_realizations(
    *,
    dimension: int,
    compatibility: Sequence[Sequence[int]],
    protected: Sequence[Sequence[int]],
    candidate: Sequence[int],
    observation: Sequence[Sequence[int]] = (),
) -> AffineRealizationReport:
    """Analyze {y : Ay=0, Py=Px} over GF(2) without enumerating solutions.

    `observation` gives optional rows Q. With uniform sampling on a nonempty
    affine realization fiber, observing Qy gives rank(Q|ker[A;P]) bits.
    The count of completions per possible observed value is uniform.
    """
    n = _dimension(dimension)
    a = _validate_matrix(compatibility, n)
    p = _validate_matrix(protected, n)
    q = _validate_matrix(observation, n)
    x = _bits(candidate, n, "candidate")
    equations = a + p
    rhs = [0] * len(a) + [sum(i & j for i, j in zip(row, x)) % 2 for row in p]
    reduced, pivots, operations = _rref(equations, n, rhs)
    rank = len(pivots)
    obstruction = next(
        (tuple(operations[i]) for i, row in enumerate(reduced)
         if not any(row[:n]) and row[n] == 1),
        None,
    )
    if obstruction is not None:
        return AffineRealizationReport(
            feasible=False, rank=rank, ambiguity_dimension=None,
            realization_count=0, solution=None, ambiguity_basis=(),
            obstruction_witness=obstruction, observation_gain_bits=None,
            remaining_ambiguity_bits=None,
        )
    # Every pivot equation gives its pivot coordinate in terms of free variables.
    solution = [0] * n
    for i, col in enumerate(pivots):
        solution[col] = reduced[i][n]
    free = [col for col in range(n) if col not in pivots]
    basis: list[tuple[int, ...]] = []
    for col in free:
        vector = [0] * n
        vector[col] = 1
        for i, pivot_col in enumerate(pivots):
            vector[pivot_col] = reduced[i][col]
        basis.append(tuple(vector))
    # Q restricted to the nullspace is a matrix with columns Q*basis[j].
    q_on_h = [
        [sum(a & b for a, b in zip(row, vector)) % 2 for vector in basis]
        for row in q
    ]
    gain = _rank(q_on_h, len(basis))
    return AffineRealizationReport(
        feasible=True, rank=rank, ambiguity_dimension=len(basis),
        realization_count=1 << len(basis), solution=tuple(solution),
        ambiguity_basis=tuple(basis), obstruction_witness=None,
        observation_gain_bits=gain, remaining_ambiguity_bits=len(basis) - gain,
    )


def check_obstruction_witness(
    *,
    dimension: int,
    compatibility: Sequence[Sequence[int]],
    protected: Sequence[Sequence[int]],
    candidate: Sequence[int],
    witness: Sequence[int],
) -> bool:
    """Check a GF(2) linear combination: lambda*[A;P]=0, lambda*b=1."""
    dimension = _dimension(dimension)
    a = _validate_matrix(compatibility, dimension)
    p = _validate_matrix(protected, dimension)
    x = _bits(candidate, dimension, "candidate")
    equations = a + p
    try:
        lam = _bits(witness, len(equations), "witness")
    except ValueError:
        return False
    rhs = [0] * len(a) + [sum(i & j for i, j in zip(row, x)) % 2 for row in p]
    return (
        all(sum(lam[i] * row[col] for i, row in enumerate(equations)) % 2 == 0
            for col in range(dimension))
        and sum(u * v for u, v in zip(lam, rhs)) % 2 == 1
    )

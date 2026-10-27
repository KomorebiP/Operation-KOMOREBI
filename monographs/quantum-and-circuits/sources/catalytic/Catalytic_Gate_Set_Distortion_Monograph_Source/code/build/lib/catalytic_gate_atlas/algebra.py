"""Exact algebraic primitives for catalytic gate-set experiments.

Matrices over GF(2) are represented as tuples of integer row bitmasks.  A
permutation of ``range(N)`` is represented as a tuple ``p`` with ``p[x]`` the
image of ``x``.  The module intentionally avoids NumPy so that every search
state is immutable, hashable, and exact.
"""
from __future__ import annotations

from typing import Iterable, Sequence, Tuple

GF2Matrix = Tuple[int, ...]
Permutation = Tuple[int, ...]


def gf2_identity(size: int) -> GF2Matrix:
    if size < 0:
        raise ValueError("size must be nonnegative")
    return tuple(1 << i for i in range(size))


def gf2_mul(left: GF2Matrix, right: GF2Matrix, size: int | None = None) -> GF2Matrix:
    """Return ``left * right`` over GF(2), using row-bit matrices."""
    if size is None:
        size = len(left)
    if len(left) != size or len(right) != size:
        raise ValueError("matrix dimensions do not match")
    output: list[int] = []
    mask = (1 << size) - 1
    for row in left:
        row &= mask
        value = 0
        bits = row
        while bits:
            lsb = bits & -bits
            index = lsb.bit_length() - 1
            value ^= right[index]
            bits ^= lsb
        output.append(value & mask)
    return tuple(output)


def gf2_transpose(matrix: GF2Matrix) -> GF2Matrix:
    size = len(matrix)
    rows = [0] * size
    for i, row in enumerate(matrix):
        for j in range(size):
            if (row >> j) & 1:
                rows[j] |= 1 << i
    return tuple(rows)


def gf2_is_identity(matrix: GF2Matrix) -> bool:
    return matrix == gf2_identity(len(matrix))


def gf2_rank(rows: Iterable[int], width: int | None = None) -> int:
    work = [int(row) for row in rows if row]
    if not work:
        return 0
    if width is None:
        width = max(row.bit_length() for row in work)
    rank = 0
    for col in reversed(range(width)):
        pivot = next((k for k in range(rank, len(work)) if (work[k] >> col) & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for k in range(len(work)):
            if k != rank and ((work[k] >> col) & 1):
                work[k] ^= work[rank]
        rank += 1
        if rank == len(work):
            break
    return rank


def gf2_matrix_to_rows(matrix: GF2Matrix) -> list[list[int]]:
    size = len(matrix)
    return [[(matrix[i] >> j) & 1 for j in range(size)] for i in range(size)]


def gf2_rows_to_matrix(rows: Sequence[Sequence[int]]) -> GF2Matrix:
    size = len(rows)
    if any(len(row) != size for row in rows):
        raise ValueError("matrix must be square")
    output = []
    for row in rows:
        value = 0
        for j, entry in enumerate(row):
            if int(entry) & 1:
                value |= 1 << j
        output.append(value)
    return tuple(output)


def perm_identity(size: int) -> Permutation:
    return tuple(range(size))


def perm_compose(left: Permutation, right: Permutation) -> Permutation:
    """Return ``left after right``."""
    if len(left) != len(right):
        raise ValueError("permutation dimensions do not match")
    return tuple(left[right[i]] for i in range(len(right)))


def perm_inverse(permutation: Permutation) -> Permutation:
    inverse = [0] * len(permutation)
    for i, image in enumerate(permutation):
        inverse[image] = i
    return tuple(inverse)


def dense_matmul_mod(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]], modulus: int) -> list[list[int]]:
    if modulus <= 1:
        raise ValueError("modulus must exceed one")
    n = len(left)
    if n == 0 or len(right) != n or any(len(row) != n for row in left) or any(len(row) != n for row in right):
        raise ValueError("matrices must be nonempty and square")
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            coefficient = left[i][k] % modulus
            if coefficient:
                for j in range(n):
                    out[i][j] = (out[i][j] + coefficient * right[k][j]) % modulus
    return out


def dense_identity(size: int) -> list[list[int]]:
    return [[1 if i == j else 0 for j in range(size)] for i in range(size)]


def dense_row_add(matrix: list[list[int]], source: int, target: int, coefficient: int, modulus: int) -> None:
    if source == target:
        raise ValueError("source and target must be distinct")
    row_source = matrix[source]
    row_target = matrix[target]
    for j in range(len(matrix)):
        row_target[j] = (row_target[j] + coefficient * row_source[j]) % modulus

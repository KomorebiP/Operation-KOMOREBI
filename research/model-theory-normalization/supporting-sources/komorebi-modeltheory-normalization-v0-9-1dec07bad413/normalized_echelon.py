"""Canonical tail reduction for the v0.6 integer-preimage solver.

This is a separately audited Python port, not verified extraction from Lean.
The verified algorithms live in EchelonNormalize and NormalizedDiscovery.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Any, Sequence
from integer_echelon import IntegerEchelon


def normalize_rows(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    """Row-Hermite convention: positive pivots, 0 <= H[i,j] < H[j,j] for i<j.

    Rows are processed from bottom to top. Within one row, reduce from left
    to right, so later operations cannot change earlier reduced columns.
    """
    out = [list(row) for row in rows]
    d = len(out)
    if any(len(row) != d or any(type(x) is not int for x in row) for row in out):
        raise ValueError('a square integer matrix is required')
    if any(out[i][i] <= 0 or any(out[i][:i]) for i in range(d)):
        raise ValueError('positive-pivot upper triangular input is required')
    for i in range(d-1, -1, -1):
        for j in range(i+1, d):
            quotient = out[i][j] // out[j][j]
            for k in range(j, d):
                out[i][k] -= quotient * out[j][k]
    return out


@dataclass
class NormalizedEchelon(IntegerEchelon):
    max_checkpoint_bits: int = 0
    normalization_divisions: int = 0
    max_checkpoint_value: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        self._checkpoint()

    def _checkpoint(self) -> None:
        d, m = self.dimension, self.modulus
        if any(m % self.rows[i][i] for i in range(d)):
            raise ArithmeticError('a pivot failed to divide the modulus')
        if any(not (0 <= x <= m) for row in self.rows for x in row):
            raise ArithmeticError('stored coefficient bound violated')
        if any(not (0 <= self.rows[i][j] < self.rows[j][j])
               for i in range(d) for j in range(i+1, d)):
            raise ArithmeticError('tail reduction failed')
        self.max_checkpoint_bits = max(self.max_checkpoint_bits,
            max((x.bit_length() for row in self.rows for x in row), default=0))
        self.max_checkpoint_value = max(self.max_checkpoint_value,
            max((x for row in self.rows for x in row), default=0))

    def insert(self, vector: Sequence[int]) -> None:
        super().insert(vector)
        # max_integer_bits inherited from the old code also records transient,
        # pre-normalization basis values. It is not the persistent-cache bound.
        self.rows = normalize_rows(self.rows)
        self.normalization_divisions += self.dimension*(self.dimension-1)//2
        self._checkpoint()

    def key(self) -> tuple[int, int, tuple[tuple[int, ...], ...]]:
        """Exact key relative to the same modulus, dimension and ambient columns."""
        return self.modulus, self.dimension, tuple(map(tuple, self.rows))


def discover_normalized(source: dict[str, Any], *, candidate_cap: int | None = None
                        ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from discover import validate_spec, rowmul
    p, r, d, m = validate_spec(source)
    bound = len(source['observations'])+len(source['actions'])*r*d
    cap = bound if candidate_cap is None else candidate_cap
    if type(cap) is not int or cap < 0:
        raise ValueError('candidate_cap must be a nonnegative integer')
    todo = deque(([], j, list(row)) for j, row in enumerate(source['observations']))
    basis = NormalizedEchelon(m, d)
    accepted: list[dict[str, Any]] = []
    decisions = 0
    while todo:
        if decisions >= cap:
            raise RuntimeError('pending work at candidate cap: unresolved')
        word, j, row = todo.popleft()
        decisions += 1
        if not basis.contains(row):
            accepted.append({'word': word, 'observation': j})
            basis.insert(row)
            for a, matrix in enumerate(source['actions']):
                todo.append(([a]+word, j, rowmul(row, matrix, m)))
    return accepted, {
        'accepted': len(accepted), 'decisions': decisions, 'stored_rows': d,
        'gcd_updates': basis.gcd_updates,
        'membership_pivots': basis.membership_pivots,
        'normalization_divisions': basis.normalization_divisions,
        'max_checkpoint_bits': basis.max_checkpoint_bits,
        'max_pre_normalization_bits': basis.max_integer_bits,
        'maximum_word_length': max((len(t['word']) for t in accepted), default=0),
        'final_basis': basis.rows,
    }

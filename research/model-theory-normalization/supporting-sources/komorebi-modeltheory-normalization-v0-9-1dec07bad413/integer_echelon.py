"""Exact incremental integer-preimage echelon backend.

This is a Python port, not extracted/verified code. Its Lean counterpart is
EchelonCore/EchelonInsert/EchelonModular/EchelonDiscovery. No Smith solver,
source-state enumeration, coefficient-tuple enumeration, or certificate adviser
is used here. Integer sizes are monitored, not assumed constant-cost.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Sequence


def bezout(q: int, a: int) -> tuple[int, int, int]:
    """Return positive g and s,t with s*q+t*a=g; q must be positive."""
    if type(q) is not int or q <= 0 or type(a) is not int:
        raise ValueError("positive integer pivot and integer candidate required")
    old_r, r, old_s, s, old_t, t = q, abs(a), 1, 0, 0, 1
    while r:
        k = old_r // r
        old_r, r = r, old_r-k*r
        old_s, s = s, old_s-k*s
        old_t, t = t, old_t-k*t
    return old_r, old_s, old_t if a >= 0 else -old_t


@dataclass
class IntegerEchelon:
    modulus: int
    dimension: int
    rows: list[list[int]] = field(init=False)
    insertions: int = 0
    gcd_updates: int = 0
    membership_pivots: int = 0
    max_integer_bits: int = 0

    def __post_init__(self) -> None:
        if type(self.modulus) is not int or self.modulus < 1:
            raise ValueError("positive integer modulus required")
        if type(self.dimension) is not int or self.dimension < 0:
            raise ValueError("nonnegative integer dimension required")
        self.rows = [[self.modulus if i == j else 0 for j in range(self.dimension)]
                     for i in range(self.dimension)]
        self._record_bits()

    def _vector(self, v: Sequence[int]) -> list[int]:
        if len(v) != self.dimension or any(type(x) is not int for x in v):
            raise ValueError("integer vector of the declared dimension required")
        return list(v)

    def _record_bits(self) -> None:
        self.max_integer_bits = max(self.max_integer_bits,
            max((abs(x).bit_length() for r in self.rows for x in r), default=0))

    def coordinates(self, v: Sequence[int]) -> list[int] | None:
        """Solve in the integer preimage lattice, using at most d divisions."""
        residual = self._vector(v)
        coefficients: list[int] = []
        for j, row in enumerate(self.rows):
            self.membership_pivots += 1
            c, rem = divmod(residual[j], row[j])
            if rem:
                return None
            coefficients.append(c)
            for k in range(j, self.dimension):
                residual[k] -= c*row[k]
        if any(residual):
            raise ArithmeticError("triangular solve invariant violated")
        return coefficients

    def contains(self, v: Sequence[int]) -> bool:
        return self.coordinates(v) is not None

    def insert(self, v: Sequence[int]) -> None:
        """Exact join with one row; one determinant-one update per column."""
        residual = self._vector(v)
        for j in range(self.dimension):
            old = self.rows[j][:]
            q, a = old[j], residual[j]
            g, s, t = bezout(q, a)
            Q, A = q//g, a//g
            if s*Q+t*A != 1:
                raise ArithmeticError("invalid Bezout determinant")
            new = [s*u+t*v for u, v in zip(old, residual)]
            rem = [-A*u+Q*v for u, v in zip(old, residual)]
            if new[j] != g or any(new[:j]) or any(rem[:j+1]):
                raise ArithmeticError("triangular insertion invariant violated")
            self.rows[j] = new
            residual = rem
            self.gcd_updates += 1
            self._record_bits()
        if any(residual):
            raise ArithmeticError("nonzero final residual")
        self.insertions += 1


def discover_echelon(source: dict[str, Any], *, candidate_cap: int | None = None
                     ) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Same FIFO policy as the retained discovery source; Python port boundary applies."""
    # Reuse only source validation and ordinary row multiplication, not Smith.
    from discover import validate_spec, rowmul
    p, r, d, m = validate_spec(source)
    bound = len(source['observations']) + len(source['actions'])*r*d
    cap = bound if candidate_cap is None else candidate_cap
    if type(cap) is not int or cap < 0:
        raise ValueError("candidate_cap must be a nonnegative integer")
    todo = deque(([],j,list(row)) for j,row in enumerate(source['observations']))
    basis = IntegerEchelon(m,d)
    accepted: list[dict[str, Any]] = []
    decisions = 0
    while todo:
        if decisions >= cap:
            raise RuntimeError("pending work at candidate cap: unresolved")
        word, j, row = todo.popleft()
        decisions += 1
        if not basis.contains(row):
            accepted.append({'word':word, 'observation':j})
            basis.insert(row)
            for a, matrix in enumerate(source['actions']):
                todo.append(([a]+word,j,rowmul(row,matrix,m)))
    stats = {'accepted':len(accepted), 'decisions':decisions,
             'stored_rows':d, 'gcd_updates':basis.gcd_updates,
             'membership_pivots':basis.membership_pivots,
             'max_integer_bits':basis.max_integer_bits,
             'maximum_word_length':max((len(x['word']) for x in accepted),default=0)}
    return accepted, stats

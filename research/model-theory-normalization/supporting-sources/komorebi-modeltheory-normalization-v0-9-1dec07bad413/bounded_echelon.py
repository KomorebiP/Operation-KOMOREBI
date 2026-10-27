"""Separately tested port of the v0.8 bounded-coefficient lattice solver.

The Lean definitions are the verified implementation. This Python port and its
instrumentation are not verified extraction. Integer arithmetic is exact.
"""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class ArithmeticLog:
    peaks: dict[str, int] = field(default_factory=dict)
    counts: Counter = field(default_factory=Counter)

    def record(self, phase: str, *values: int) -> None:
        self.peaks[phase] = max(self.peaks.get(phase, 0), *(abs(v) for v in values), 0)

    def row(self, phase: str, values: Sequence[int]) -> None:
        self.record(phase, *values)


def bounded_bezout(q: int, a: int, log: ArithmeticLog | None = None) -> tuple[int, int, int]:
    """The stack form of Lean's euclidCoeff, followed by the signed-input map."""
    if type(q) is not int or q <= 0 or type(a) is not int:
        raise ValueError('positive integer pivot and integer candidate required')
    log = ArithmeticLog() if log is None else log
    x, y = q, abs(a)
    stack: list[int] = []
    start_steps = log.counts['euclid_divisions']
    while y:
        quotient, rem = divmod(x, y)
        log.record('euclid', x, y, quotient, rem)
        log.counts['euclid_divisions'] += 1
        stack.append(quotient)
        x, y = y, rem
    g, s, t = x, 1, 0
    log.record('euclid', g, s, t)
    for quotient in reversed(stack):
        product = quotient * t
        new_t = s - product
        log.record('euclid', product, new_t, s, t)
        log.counts['euclid_products'] += 1
        s, t = t, new_t
    if a < 0:
        t = -t
    assert q * s + a * t == g
    assert abs(s) <= max(1, abs(a)) and abs(t) <= q
    # b < 2^b.bit_length(), including b=0 and its zero recursion count.
    assert log.counts['euclid_divisions'] - start_steps <= 2 * abs(a).bit_length()
    return g, s, t


@dataclass
class BoundedEchelon:
    modulus: int
    dimension: int
    rows: list[list[int]] = field(init=False)
    log: ArithmeticLog = field(default_factory=ArithmeticLog)
    checkpoints: int = 0
    insertions: int = 0

    def __post_init__(self) -> None:
        if type(self.modulus) is not int or self.modulus < 1:
            raise ValueError('modulus must be a positive integer')
        if type(self.dimension) is not int or self.dimension < 0:
            raise ValueError('dimension must be nonnegative')
        self.rows = [[self.modulus if i == j else 0 for j in range(self.dimension)]
                     for i in range(self.dimension)]
        self._checkpoint()

    def _vector(self, v: Sequence[int]) -> list[int]:
        if len(v) != self.dimension or any(type(x) is not int for x in v):
            raise ValueError('an integer vector of the declared dimension is required')
        return list(v)

    def _checkpoint(self) -> None:
        m, d = self.modulus, self.dimension
        for i in range(d):
            assert self.rows[i][i] > 0 and m % self.rows[i][i] == 0
            assert all(x == 0 for x in self.rows[i][:i])
            assert all(0 <= self.rows[i][j] < self.rows[j][j] for j in range(i+1, d))
            assert all(0 <= x <= m for x in self.rows[i])
            self.log.row('stored', self.rows[i])
        self.checkpoints += 1

    def coordinates(self, vector: Sequence[int]) -> list[int] | None:
        v = self._vector(vector)
        out: list[int] = []
        for i, row in enumerate(self.rows):
            c, rem = divmod(v[i], row[i])
            self.log.row('membership', v)
            self.log.record('membership', row[i], c, rem)
            self.log.counts['membership_pivots'] += 1
            if rem:
                return None
            out.append(c)
            v[i] = 0
            for j in range(i+1, self.dimension):
                product = c * row[j]
                self.log.record('membership', product, v[j]-product)
                self.log.counts['membership_products'] += 1
                v[j] -= product
        assert not any(v)
        return out

    def contains(self, vector: Sequence[int]) -> bool:
        return self.coordinates(vector) is not None

    def insert(self, vector: Sequence[int]) -> None:
        v = self._vector(vector)
        d, m = self.dimension, self.modulus
        for i in range(d):
            old = self.rows[i][:]
            q, a = old[i], v[i]
            g, s, t = bounded_bezout(q, a, self.log)
            Q, A = q//g, a//g
            self.log.row('insertion', v)
            self.log.record('insertion', q, a, g, s, t, Q, A)
            self.log.counts['insert_levels'] += 1
            new = [0]*d
            new[i] = g
            v[i] = 0
            for j in range(i+1, d):
                sb, tv, ab, qv = s*old[j], t*v[j], -A*old[j], Q*v[j]
                new[j], v[j] = sb+tv, ab+qv
                self.log.record('insertion', sb, tv, ab, qv, new[j], v[j])
                self.log.counts['insertion_products'] += 4
            self.rows[i] = new
        assert not any(v)
        # Same bottom-up, column-pivot convention as Lean.normalize.
        for i in range(d-1, -1, -1):
            for j in range(i+1, d):
                c, rem = divmod(self.rows[i][j], self.rows[j][j])
                self.log.record('normalization', self.rows[i][j], self.rows[j][j], c, rem)
                self.log.counts['normalization_pivots'] += 1
                self.rows[i][j] = rem
                for k in range(j+1, d):
                    product = c*self.rows[j][k]
                    self.rows[i][k] -= product
                    self.log.record('normalization', product, self.rows[i][k])
                    self.log.counts['normalization_products'] += 1
        self.insertions += 1
        self._checkpoint()

    def key(self) -> tuple[int, int, tuple[tuple[int, ...], ...]]:
        return self.modulus, self.dimension, tuple(map(tuple, self.rows))


def discover_bounded(source: dict[str, Any], *, candidate_cap: int | None = None
                     ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from discover import validate_spec
    p, r, d, m = validate_spec(source)
    cap = len(source['observations']) + len(source['actions'])*r*d if candidate_cap is None else candidate_cap
    if type(cap) is not int or cap < 0:
        raise ValueError('candidate cap must be a nonnegative integer')
    basis = BoundedEchelon(m, d)
    todo = deque(([], j, list(row)) for j, row in enumerate(source['observations']))
    accepted: list[dict[str, Any]] = []
    decisions = 0
    while todo:
        if decisions >= cap:
            raise RuntimeError('candidate cap reached with pending work: unresolved')
        word, j, row = todo.popleft()
        decisions += 1
        if basis.contains(row):
            continue
        accepted.append({'word': word, 'observation': j})
        basis.insert(row)
        for a, matrix in enumerate(source['actions']):
            # Ring operations are reduced after each addition; no unbounded dot accumulator.
            nxt = []
            for col in range(d):
                acc = 0
                for i in range(d):
                    product = row[i]*matrix[i][col]
                    raw = acc+product
                    basis.log.record('source_row', product, raw)
                    basis.log.counts['source_products'] += 1
                    acc = raw % m
                nxt.append(acc)
            todo.append(([a]+word, j, nxt))
    C = m*(2*m*(m+1))**d
    phases = ['membership', 'insertion', 'normalization', 'euclid']
    peak = max((basis.log.peaks.get(k, 0) for k in phases), default=0)
    assert peak <= C
    bits = (m-1).bit_length()  # least b with m <= 2^b, including m=1.
    budget = bits + (2*bits+2)*d + 1
    assert peak.bit_length() <= budget
    return accepted, {'accepted': len(accepted), 'decisions': decisions,
                     'final_basis': basis.rows, 'phase_peaks': basis.log.peaks,
                     'phase_bits': {k: v.bit_length() for k,v in basis.log.peaks.items()},
                     'counts': dict(basis.log.counts),
                     'arithmetic_peak': peak, 'proved_cap': C,
                     'proved_bit_budget': budget}

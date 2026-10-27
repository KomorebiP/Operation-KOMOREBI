from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Hashable, Iterable, Mapping, Sequence

import sympy as sp


@dataclass(frozen=True)
class LocalSpineRecord:
    prime: int
    frobenius_polynomials: tuple[tuple[int, ...], ...]
    weights: tuple[int, ...]
    determinant_label: str
    local_packet_labels: tuple[str, ...]


def spine_is_compatible(records: Sequence[LocalSpineRecord]) -> bool:
    if not records:
        return True
    reference = records[0]
    return all(
        record.frobenius_polynomials == reference.frobenius_polynomials
        and record.weights == reference.weights
        and record.determinant_label == reference.determinant_label
        and record.local_packet_labels == reference.local_packet_labels
        for record in records[1:]
    )


def select_frobenius_separators(trace_rows: Sequence[Sequence[int | Fraction]], constituent_count: int) -> list[int]:
    """Greedily choose trace rows until the constituent columns have full rank."""
    chosen: list[int] = []
    current: list[list[sp.Rational]] = []
    rank = 0
    for index, row in enumerate(trace_rows):
        candidate = current + [[sp.Rational(x) for x in row]]
        candidate_rank = sp.Matrix(candidate).rank()
        if candidate_rank > rank:
            chosen.append(index)
            current = candidate
            rank = candidate_rank
            if rank == constituent_count:
                return chosen
    raise ValueError("trace rows do not separate all constituents")


def recover_multiplicities(
    trace_matrix: Sequence[Sequence[int | Fraction]],
    observed_traces: Sequence[int | Fraction],
    capacities: Sequence[int] | None = None,
) -> tuple[int, ...]:
    matrix = sp.Matrix([[sp.Rational(x) for x in row] for row in trace_matrix])
    observed = sp.Matrix([sp.Rational(x) for x in observed_traces])
    if matrix.rows != observed.rows:
        raise ValueError("trace dimensions do not match")
    solutions = sp.linsolve((matrix, observed))
    if solutions is sp.EmptySet or not solutions:
        raise ValueError("no multiplicity solution")
    values = next(iter(solutions))
    if any(value.free_symbols for value in values):
        raise ValueError("multiplicities are not uniquely determined")
    out: list[int] = []
    for value in values:
        if value.q != 1 or value < 0:
            raise ValueError("multiplicities must be nonnegative integers")
        out.append(int(value))
    if capacities is not None:
        if len(capacities) != len(out):
            raise ValueError("capacity mismatch")
        if any(value > capacity for value, capacity in zip(out, capacities, strict=True)):
            raise ValueError("multiplicity exceeds carrier capacity")
    return tuple(out)

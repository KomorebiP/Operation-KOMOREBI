"""Linear transvection examples, including the universal six-row atom."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .algebra import dense_identity, dense_row_add


@dataclass(frozen=True)
class RowGate:
    source: int
    target: int
    coefficient: int = 1


def canonical_six_target(modulus: int) -> list[list[int]]:
    if modulus <= 1:
        raise ValueError("modulus must exceed one")
    matrix = dense_identity(6)
    additions = {
        1: {0: 1},
        3: {1: 1, 2: 1},
        4: {0: 1, 1: 1, 2: 1},
        5: {0: 1, 1: 1, 2: 1},
    }
    for target, entries in additions.items():
        for source, coefficient in entries.items():
            matrix[target][source] = coefficient % modulus
    return matrix


def canonical_ambient_word(modulus: int) -> list[RowGate]:
    return [
        RowGate(2, 1, 1),
        RowGate(1, 3, 1),
        RowGate(0, 1, 1),
        RowGate(1, 4, 1),
        RowGate(1, 5, 1),
        RowGate(2, 1, -1 % modulus),
    ]


def canonical_restricted_word(modulus: int) -> list[RowGate]:
    return [
        RowGate(0, 1, 1),
        RowGate(1, 2, 1),
        RowGate(0, 3, -1 % modulus),
        RowGate(2, 3, 1),
        RowGate(2, 4, 1),
        RowGate(2, 5, 1),
        RowGate(1, 2, -1 % modulus),
    ]


def apply_row_word(size: int, word: Sequence[RowGate], modulus: int) -> list[list[int]]:
    matrix = dense_identity(size)
    for gate in word:
        dense_row_add(matrix, gate.source, gate.target, gate.coefficient, modulus)
    return matrix


def verify_canonical_atom(modulus: int) -> dict[str, object]:
    target = canonical_six_target(modulus)
    ambient = apply_row_word(6, canonical_ambient_word(modulus), modulus)
    restricted = apply_row_word(6, canonical_restricted_word(modulus), modulus)
    return {
        "modulus": modulus,
        "ambient_word_length": 6,
        "restricted_word_length": 7,
        "ambient_matches": ambient == target,
        "restricted_matches": restricted == target,
    }


def snapshot_target(u: int, phases: Sequence[int], modulus: int = 2) -> list[list[int]]:
    """Construct the connected snapshot family A(u; phases).

    Coordinates are ``x_0,...,x_{u-1},p,q,t_0,...,t_{v-1}``.
    Output ``t_j`` receives ``q+p+x_0+...+x_{phases[j]-1}``.
    """
    if u < 1:
        raise ValueError("u must be positive")
    if not phases:
        raise ValueError("at least one phase is required")
    if sorted(phases) != list(phases) or len(set(phases)) != len(phases):
        raise ValueError("phases must be strictly increasing")
    if phases[0] < 0 or phases[-1] > u:
        raise ValueError("phase out of range")
    v = len(phases)
    p, q = u, u + 1
    size = u + v + 2
    matrix = dense_identity(size)
    for i in range(u):
        matrix[p][i] = 1 % modulus
    for j, phase in enumerate(phases):
        target = u + 2 + j
        matrix[target][p] = 1 % modulus
        matrix[target][q] = 1 % modulus
        for i in range(phase):
            matrix[target][i] = 1 % modulus
    return matrix


def snapshot_ambient_word(u: int, phases: Sequence[int], modulus: int = 2) -> list[RowGate]:
    p, q = u, u + 1
    word: list[RowGate] = [RowGate(q, p, 1)]
    phase_to_outputs: dict[int, list[int]] = {}
    for j, phase in enumerate(phases):
        phase_to_outputs.setdefault(phase, []).append(u + 2 + j)
    for target in phase_to_outputs.get(0, []):
        word.append(RowGate(p, target, 1))
    for i in range(u):
        word.append(RowGate(i, p, 1))
        for target in phase_to_outputs.get(i + 1, []):
            word.append(RowGate(p, target, 1))
    word.append(RowGate(q, p, -1 % modulus))
    return word

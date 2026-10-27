from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

import numpy as np

N_STATES = 8
N_OPERATORS = 2

# States are r^k f^b with index 4*b+k. Operators act by left multiplication.
_D4_R = np.array([4 * (i // 4) + ((i % 4 + 1) % 4) for i in range(N_STATES)], dtype=np.int64)
_D4_F = np.array([4 * (1 - i // 4) + ((-(i % 4)) % 4) for i in range(N_STATES)], dtype=np.int64)
_C8_A = np.array([(i + 1) % N_STATES for i in range(N_STATES)], dtype=np.int64)
_C8_B = np.array([(i + 3) % N_STATES for i in range(N_STATES)], dtype=np.int64)
_MIXED_A = _C8_A.copy()
_MIXED_B = np.array([i ^ 1 for i in range(N_STATES)], dtype=np.int64)

D4_RELATIONS: Mapping[str, tuple[int, ...]] = {
    "r4": (0, 0, 0, 0),
    "f2": (1, 1),
    "frfr": (1, 0, 1, 0),
}

D4_EQUIVALENT_PATHS: Mapping[str, tuple[tuple[int, ...], tuple[int, ...]]] = {
    "identity_r4": ((), (0, 0, 0, 0)),
    "identity_f2": ((), (1, 1)),
    "r_inverse": ((0, 0, 0), (1, 0, 1)),
    "rf_rewrite": ((0, 1), (1, 0, 0, 0)),
}


@dataclass(frozen=True)
class AlgebraAudit:
    family: str
    valid_permutations: bool
    relation_results: dict[str, bool]
    digest: str


def canonical_maps(family: str) -> np.ndarray:
    family = family.lower()
    if family == "d4":
        return np.stack((_D4_R, _D4_F), axis=0)
    if family == "c8":
        return np.stack((_C8_A, _C8_B), axis=0)
    if family == "mixed_cycle":
        return np.stack((_MIXED_A, _MIXED_B), axis=0)
    raise ValueError(f"Unknown fixed algebra family: {family}")


def apply_word(maps: np.ndarray, start: np.ndarray, word: np.ndarray) -> np.ndarray:
    """Apply per-example slot maps to integer states.

    maps: (batch, slots, states), start: (batch,), word: (batch, length)
    """
    current = np.asarray(start, dtype=np.int64).copy()
    rows = np.arange(current.shape[0])
    for t in range(word.shape[1]):
        selected = maps[rows, word[:, t]]
        current = selected[rows, current]
    return current


def compose_single(maps: np.ndarray, word: tuple[int, ...]) -> np.ndarray:
    current = np.arange(maps.shape[-1], dtype=np.int64)
    for operator in word:
        current = maps[operator, current]
    return current


def audit_algebra(family: str = "d4") -> AlgebraAudit:
    maps = canonical_maps(family)
    expected = np.arange(N_STATES)
    valid = all(np.array_equal(np.sort(row), expected) for row in maps)
    relation_results: dict[str, bool] = {}
    if family == "d4":
        for name, word in D4_RELATIONS.items():
            relation_results[name] = bool(np.array_equal(compose_single(maps, word), expected))
    payload = maps.tobytes() + family.encode("utf-8")
    return AlgebraAudit(
        family=family,
        valid_permutations=valid,
        relation_results=relation_results,
        digest=hashlib.sha256(payload).hexdigest(),
    )


def conjugate_maps(canonical: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Conjugate fixed maps by per-example state permutations.

    canonical has shape (operators, states). phi has shape (batch, states) and
    maps canonical labels to observed labels.
    """
    inverse = np.argsort(phi, axis=1)
    batch = phi.shape[0]
    output = np.empty((batch, canonical.shape[0], canonical.shape[1]), dtype=np.int64)
    for operator in range(canonical.shape[0]):
        canonical_target = canonical[operator][inverse]
        output[:, operator] = np.take_along_axis(phi, canonical_target, axis=1)
    return output

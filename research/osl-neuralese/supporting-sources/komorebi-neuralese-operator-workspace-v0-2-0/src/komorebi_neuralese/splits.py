from __future__ import annotations

import hashlib
import itertools
import math
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .algebra import N_STATES


# This value is part of the experimental protocol. Changing it creates a new
# coordinate partition and must therefore be treated as a protocol revision.
COORDINATE_SPLIT_NAMESPACE = "komorebi-neuralese/operator-map-split/v1"
COORDINATE_SPLITS = ("train", "dev", "test")
COORDINATE_SPLIT_COUNTS: Mapping[str, int] = MappingProxyType(
    {
        "train": 24_192,
        "dev": 8_064,
        "test": 8_064,
    }
)

_SPLIT_CODES = {name: code for code, name in enumerate(COORDINATE_SPLITS)}


@dataclass(frozen=True)
class CoordinateSplitAudit:
    """Exhaustive audit of the frozen partition of the finite space S_8."""

    namespace: str
    total_maps: int
    expected_counts: dict[str, int]
    observed_counts: dict[str, int]
    pairwise_intersections: dict[str, int]
    unique_fingerprints: bool
    disjoint: bool
    complete: bool
    digest: str

    @property
    def passed(self) -> bool:
        return bool(
            self.unique_fingerprints
            and self.disjoint
            and self.complete
            and self.observed_counts == self.expected_counts
        )


@dataclass(frozen=True)
class _PartitionTable:
    assignments: dict[bytes, int]
    permutations: tuple[np.ndarray, np.ndarray, np.ndarray]
    fingerprints: tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]
    digest: str


def _validated_map_bytes(mapping: np.ndarray) -> bytes:
    array = np.asarray(mapping)
    if array.shape != (N_STATES,):
        raise ValueError(f"operator mapping must have shape ({N_STATES},)")
    if not np.issubdtype(array.dtype, np.integer):
        raise ValueError("operator mapping must contain integers")
    array64 = np.asarray(array, dtype=np.int64)
    if not np.array_equal(np.sort(array64), np.arange(N_STATES, dtype=np.int64)):
        raise ValueError(f"operator mapping must be a permutation of 0..{N_STATES - 1}")
    # Values are in 0..7, so this one-byte encoding is independent of machine
    # endianness and NumPy dtype width.
    return bytes(int(value) for value in array64)


def _fingerprint_bytes(encoded_map: bytes) -> bytes:
    payload = COORDINATE_SPLIT_NAMESPACE.encode("utf-8") + b"\x00" + encoded_map
    return hashlib.sha256(payload).digest()


def map_fingerprint(mapping: np.ndarray) -> str:
    """Return the stable, namespace-bound SHA-256 fingerprint of one map."""

    return _fingerprint_bytes(_validated_map_bytes(mapping)).hex()


@lru_cache(maxsize=1)
def _partition_table() -> _PartitionTable:
    """Build the exact 60/20/20 hash-rank partition of all 8! maps."""

    ranked: list[tuple[bytes, bytes]] = []
    for permutation in itertools.permutations(range(N_STATES)):
        encoded = bytes(permutation)
        ranked.append((_fingerprint_bytes(encoded), encoded))
    ranked.sort()

    boundaries = (
        COORDINATE_SPLIT_COUNTS["train"],
        COORDINATE_SPLIT_COUNTS["train"] + COORDINATE_SPLIT_COUNTS["dev"],
        len(ranked),
    )
    assignments: dict[bytes, int] = {}
    split_maps: list[list[tuple[int, ...]]] = [[], [], []]
    split_fingerprints: list[list[str]] = [[], [], []]
    lower = 0
    for code, upper in enumerate(boundaries):
        for fingerprint, encoded in ranked[lower:upper]:
            assignments[encoded] = code
            split_maps[code].append(tuple(encoded))
            split_fingerprints[code].append(fingerprint.hex())
        lower = upper

    arrays: list[np.ndarray] = []
    for maps in split_maps:
        array = np.asarray(maps, dtype=np.int64)
        array.setflags(write=False)
        arrays.append(array)

    manifest = b"".join(
        fingerprint + bytes((assignments[encoded],)) + encoded
        for fingerprint, encoded in ranked
    )
    return _PartitionTable(
        assignments=assignments,
        permutations=(arrays[0], arrays[1], arrays[2]),
        fingerprints=(
            tuple(split_fingerprints[0]),
            tuple(split_fingerprints[1]),
            tuple(split_fingerprints[2]),
        ),
        digest=hashlib.sha256(manifest).hexdigest(),
    )


def validate_coordinate_split(split: str | None) -> str | None:
    if split is None:
        return None
    if not isinstance(split, str):
        raise ValueError(f"coordinate_split must be one of {COORDINATE_SPLITS} or None")
    normalized = split.lower()
    if normalized not in _SPLIT_CODES:
        raise ValueError(f"coordinate_split must be one of {COORDINATE_SPLITS} or None")
    return normalized


def map_split(mapping: np.ndarray) -> str:
    """Return train, dev, or test for one valid eight-state operator map."""

    encoded = _validated_map_bytes(mapping)
    code = _partition_table().assignments[encoded]
    return COORDINATE_SPLITS[code]


def map_splits(maps: np.ndarray) -> np.ndarray | str:
    """Vectorized-shape split labels for maps stored along the last axis."""

    array = np.asarray(maps)
    if array.ndim == 1:
        return map_split(array)
    if array.ndim < 2 or array.shape[-1] != N_STATES:
        raise ValueError(f"maps must have final dimension {N_STATES}")
    flat = array.reshape(-1, N_STATES)
    labels = np.asarray([map_split(mapping) for mapping in flat], dtype="<U5")
    return labels.reshape(array.shape[:-1])


def maps_all_in_split(maps: np.ndarray, split: str) -> np.ndarray | bool:
    """Test whether every operator in each map collection is in ``split``.

    A one-dimensional input is treated as a single map. A two-dimensional
    ``(operators, states)`` input returns one bool. Inputs with leading batch
    dimensions return a bool array over those leading dimensions.
    """

    normalized = validate_coordinate_split(split)
    assert normalized is not None
    labels = map_splits(maps)
    if isinstance(labels, str):
        return labels == normalized
    matches = labels == normalized
    if matches.ndim == 1:
        return bool(np.all(matches))
    return np.all(matches, axis=-1)


def permutations_in_split(split: str) -> np.ndarray:
    """Return a read-only enumeration of all maps assigned to ``split``."""

    normalized = validate_coordinate_split(split)
    assert normalized is not None
    return _partition_table().permutations[_SPLIT_CODES[normalized]]


def audit_coordinate_splits() -> CoordinateSplitAudit:
    """Exhaustively verify the frozen finite partition, including disjointness."""

    table = _partition_table()
    sets = {
        split: set(table.fingerprints[_SPLIT_CODES[split]])
        for split in COORDINATE_SPLITS
    }
    intersections = {
        "train_dev": len(sets["train"] & sets["dev"]),
        "train_test": len(sets["train"] & sets["test"]),
        "dev_test": len(sets["dev"] & sets["test"]),
    }
    observed = {split: len(sets[split]) for split in COORDINATE_SPLITS}
    total_maps = sum(observed.values())
    union = set().union(*sets.values())
    return CoordinateSplitAudit(
        namespace=COORDINATE_SPLIT_NAMESPACE,
        total_maps=total_maps,
        expected_counts=dict(COORDINATE_SPLIT_COUNTS),
        observed_counts=observed,
        pairwise_intersections=intersections,
        unique_fingerprints=len(union) == total_maps,
        disjoint=all(count == 0 for count in intersections.values()),
        complete=len(union) == math.factorial(N_STATES),
        digest=table.digest,
    )


# An explicit name for protocol/audit callers that want to emphasize that this
# is a complete finite enumeration rather than a statistical spot check.
enumerate_coordinate_split_audit = audit_coordinate_splits


__all__ = [
    "COORDINATE_SPLIT_COUNTS",
    "COORDINATE_SPLIT_NAMESPACE",
    "COORDINATE_SPLITS",
    "CoordinateSplitAudit",
    "audit_coordinate_splits",
    "enumerate_coordinate_split_audit",
    "map_fingerprint",
    "map_split",
    "map_splits",
    "maps_all_in_split",
    "permutations_in_split",
    "validate_coordinate_split",
]

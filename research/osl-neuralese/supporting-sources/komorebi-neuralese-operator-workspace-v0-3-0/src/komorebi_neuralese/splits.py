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
WORD_PRODUCT_SCOPES = ("none", "terminal", "prefixes", "contiguous")
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
    rank_codes: np.ndarray
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
    # ``itertools.permutations(range(8))`` is lexicographic, so its position is
    # exactly the permutation's Lehmer rank.  Keeping the split code indexed by
    # that rank lets ``map_splits`` classify whole arrays without a Python loop
    # or repeated validation/hash-table work.  The frozen fingerprint-based
    # partition itself is unchanged.
    rank_codes = np.fromiter(
        (assignments[bytes(permutation)] for permutation in itertools.permutations(range(N_STATES))),
        dtype=np.int8,
        count=math.factorial(N_STATES),
    )
    rank_codes.setflags(write=False)
    return _PartitionTable(
        assignments=assignments,
        permutations=(arrays[0], arrays[1], arrays[2]),
        fingerprints=(
            tuple(split_fingerprints[0]),
            tuple(split_fingerprints[1]),
            tuple(split_fingerprints[2]),
        ),
        rank_codes=rank_codes,
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


def validate_word_product_scope(scope: str) -> str:
    """Validate how a sampled word's exact products are split-confined.

    ``terminal`` checks only the complete word, ``prefixes`` checks every
    nonempty prefix, and ``contiguous`` checks every nonempty contiguous
    subword.  The last option is the strict training boundary: no transformation
    traversed by a terminal-loss computation can equal a held-out primitive map.
    """

    if not isinstance(scope, str):
        raise ValueError(f"word_product_scope must be one of {WORD_PRODUCT_SCOPES}")
    normalized = scope.lower()
    if normalized not in WORD_PRODUCT_SCOPES:
        raise ValueError(f"word_product_scope must be one of {WORD_PRODUCT_SCOPES}")
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
    if not np.issubdtype(array.dtype, np.integer):
        raise ValueError("operator mappings must contain integers")
    flat = np.asarray(array, dtype=np.int64).reshape(-1, N_STATES)
    expected = np.broadcast_to(np.arange(N_STATES, dtype=np.int64), flat.shape)
    if not np.array_equal(np.sort(flat, axis=1), expected):
        raise ValueError(f"every operator mapping must be a permutation of 0..{N_STATES - 1}")

    # Vectorized Lehmer ranks.  For position i, count smaller values to its
    # right and multiply by (7-i)!.  N_STATES is frozen at eight here, making
    # this both small and substantially faster than one dictionary lookup plus
    # validation per map in strict inner-loop audits.
    ranks = np.zeros(flat.shape[0], dtype=np.int64)
    for position in range(N_STATES - 1):
        smaller_to_right = np.sum(
            flat[:, position + 1 :] < flat[:, position, None], axis=1, dtype=np.int64
        )
        ranks += smaller_to_right * math.factorial(N_STATES - 1 - position)
    codes = _partition_table().rank_codes[ranks]
    labels = np.asarray(COORDINATE_SPLITS, dtype="<U5")[codes]
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


def word_product_maps(
    maps: np.ndarray,
    words: np.ndarray,
    scope: str = "contiguous",
) -> np.ndarray:
    """Compose the exact maps selected by a batch of anonymous words.

    Returns shape ``(batch, products, states)``.  Products are nonempty and are
    ordered deterministically.  For ``contiguous``, intervals are ordered by
    start position and then exclusive end position.  An empty word therefore
    has zero products and satisfies every split constraint vacuously.
    """

    normalized_scope = validate_word_product_scope(scope)
    map_array = np.asarray(maps)
    word_array = np.asarray(words)
    if map_array.ndim != 3 or map_array.shape[-1] != N_STATES:
        raise ValueError(f"maps must have shape (batch, slots, {N_STATES})")
    if word_array.ndim != 2 or word_array.shape[0] != map_array.shape[0]:
        raise ValueError("words must have shape (batch, length)")
    if not np.issubdtype(map_array.dtype, np.integer):
        raise ValueError("maps must contain integers")
    if not np.issubdtype(word_array.dtype, np.integer):
        raise ValueError("words must contain integers")
    batch, slots, states = map_array.shape
    expected = np.broadcast_to(np.arange(states, dtype=np.int64), map_array.shape)
    if not np.array_equal(np.sort(map_array.astype(np.int64, copy=False), axis=-1), expected):
        raise ValueError(f"every primitive map must be a permutation of 0..{states - 1}")
    if word_array.size and (np.any(word_array < 0) or np.any(word_array >= slots)):
        raise ValueError("word slot index out of range")
    length = word_array.shape[1]
    if normalized_scope == "none" or length == 0:
        return np.empty((batch, 0, states), dtype=np.int64)

    rows = np.arange(batch)
    if normalized_scope == "terminal":
        starts = (0,)
        retained_ends = {length}
    elif normalized_scope == "prefixes":
        starts = (0,)
        retained_ends = set(range(1, length + 1))
    else:
        starts = tuple(range(length))
        retained_ends = None

    collected: list[np.ndarray] = []
    for start in starts:
        current = np.broadcast_to(np.arange(states, dtype=np.int64), (batch, states)).copy()
        for position in range(start, length):
            selected = map_array[rows, word_array[:, position]]
            current = np.take_along_axis(selected, current, axis=1)
            end = position + 1
            if retained_ends is None or end in retained_ends:
                collected.append(current.copy())
    return np.stack(collected, axis=1)


def word_products_all_in_split(
    maps: np.ndarray,
    words: np.ndarray,
    split: str,
    scope: str = "contiguous",
) -> np.ndarray:
    """Return one acceptance decision per word under an exact split boundary."""

    normalized_split = validate_coordinate_split(split)
    assert normalized_split is not None
    products = word_product_maps(maps, words, scope=scope)
    if products.shape[1] == 0:
        return np.ones(products.shape[0], dtype=np.bool_)
    labels = map_splits(products)
    assert isinstance(labels, np.ndarray)
    return np.all(labels == normalized_split, axis=1)


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
    "WORD_PRODUCT_SCOPES",
    "CoordinateSplitAudit",
    "audit_coordinate_splits",
    "enumerate_coordinate_split_audit",
    "map_fingerprint",
    "map_split",
    "map_splits",
    "maps_all_in_split",
    "permutations_in_split",
    "validate_coordinate_split",
    "validate_word_product_scope",
    "word_product_maps",
    "word_products_all_in_split",
]

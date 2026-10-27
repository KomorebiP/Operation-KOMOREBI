from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese import map_fingerprint as exported_map_fingerprint
from komorebi_neuralese import map_split as exported_map_split
from komorebi_neuralese.algebra import N_STATES, canonical_maps, conjugate_maps
from komorebi_neuralese.data import EpisodeGenerator, map_fingerprint, map_split, maps_all_in_split
from komorebi_neuralese.splits import (
    COORDINATE_SPLIT_COUNTS,
    COORDINATE_SPLIT_NAMESPACE,
    COORDINATE_SPLITS,
    audit_coordinate_splits,
    map_splits,
    permutations_in_split,
)


def _assert_batches_equal(first, second) -> None:
    for field in (
        "tables",
        "maps",
        "op_slots",
        "canonical_ops",
        "start",
        "target",
        "intermediates",
        "canonical_to_slot",
        "phi",
    ):
        assert torch.equal(getattr(first, field), getattr(second, field)), field
    assert first.family == second.family
    assert first.coordinate_split == second.coordinate_split


def _legacy_d4_episode(seed: int, batch_size: int, length: int) -> dict[str, np.ndarray]:
    """Independent transcription of the v0.1 unrestricted sampling path."""

    rng = np.random.default_rng(seed)
    phi = np.argsort(rng.random((batch_size, N_STATES)), axis=1).astype(np.int64)
    canonical_batch_maps = conjugate_maps(canonical_maps("d4"), phi)
    swap = rng.integers(0, 2, size=batch_size, dtype=np.int64)
    slot_maps = np.empty_like(canonical_batch_maps)
    slot_maps[:, 0] = np.where(swap[:, None].astype(bool), canonical_batch_maps[:, 1], canonical_batch_maps[:, 0])
    slot_maps[:, 1] = np.where(swap[:, None].astype(bool), canonical_batch_maps[:, 0], canonical_batch_maps[:, 1])
    canonical_to_slot = np.stack((swap, 1 - swap), axis=1)
    canonical_ops = rng.integers(0, 2, size=(batch_size, length), dtype=np.int64)
    op_slots = np.take_along_axis(canonical_to_slot, canonical_ops, axis=1)
    start = rng.integers(0, N_STATES, size=batch_size, dtype=np.int64)
    current = start.copy()
    intermediates = np.empty((batch_size, length), dtype=np.int64)
    rows = np.arange(batch_size)
    for step in range(length):
        selected = slot_maps[rows, op_slots[:, step]]
        current = selected[rows, current]
        intermediates[:, step] = current
    return {
        "maps": slot_maps,
        "phi": phi,
        "canonical_to_slot": canonical_to_slot,
        "canonical_ops": canonical_ops,
        "op_slots": op_slots,
        "start": start,
        "target": current,
        "intermediates": intermediates,
    }


def test_frozen_hash_partition_has_exact_counts_and_no_overlap() -> None:
    audit = audit_coordinate_splits()
    assert COORDINATE_SPLIT_NAMESPACE == "komorebi-neuralese/operator-map-split/v1"
    assert dict(COORDINATE_SPLIT_COUNTS) == {"train": 24_192, "dev": 8_064, "test": 8_064}
    assert audit.observed_counts == dict(COORDINATE_SPLIT_COUNTS)
    assert audit.total_maps == 40_320
    assert audit.pairwise_intersections == {"train_dev": 0, "train_test": 0, "dev_test": 0}
    assert audit.unique_fingerprints
    assert audit.disjoint
    assert audit.complete
    assert audit.passed
    assert audit.digest == "3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340"


def test_fingerprint_and_split_are_stable_and_exported() -> None:
    identity = np.arange(N_STATES, dtype=np.int64)
    expected = "492987c4a77e025324278e3ae0558cb909ef8007530463966106a0d67effa970"
    assert map_fingerprint(identity) == expected
    assert exported_map_fingerprint(identity) == expected
    assert map_split(identity) == "train"
    assert exported_map_split(identity) == "train"


def test_split_enumerations_are_read_only_and_individually_correct() -> None:
    for split in COORDINATE_SPLITS:
        maps = permutations_in_split(split)
        assert maps.shape == (COORDINATE_SPLIT_COUNTS[split], N_STATES)
        assert not maps.flags.writeable
        assert np.all(map_splits(maps[:32]) == split)


@pytest.mark.parametrize("family", ("d4", "c8", "mixed", "mixed_cycle", "random"))
@pytest.mark.parametrize("split", COORDINATE_SPLITS)
def test_episode_generator_requires_both_base_operators_in_split(family: str, split: str) -> None:
    batch = EpisodeGenerator(117, coordinate_split=split).sample(24, 5, family=family)
    membership = maps_all_in_split(batch.maps.numpy(), split)
    assert isinstance(membership, np.ndarray)
    assert membership.shape == (24,)
    assert np.all(membership)
    assert batch.coordinate_split == split
    assert batch.to("cpu").coordinate_split == split


def test_per_call_split_override_is_supported() -> None:
    batch = EpisodeGenerator(211).sample(32, 4, family="d4", coordinate_split="dev")
    assert np.all(maps_all_in_split(batch.maps.numpy(), "dev"))
    assert batch.coordinate_split == "dev"


def test_split_sampling_is_deterministic() -> None:
    first = EpisodeGenerator(313, coordinate_split="test").sample(48, 7, family="c8")
    second = EpisodeGenerator(313, coordinate_split="test").sample(48, 7, family="c8")
    _assert_batches_equal(first, second)


def test_default_none_preserves_the_legacy_unrestricted_stream() -> None:
    seed = 419
    batch_size = 37
    length = 6
    expected = _legacy_d4_episode(seed, batch_size, length)
    observed = EpisodeGenerator(seed, coordinate_split=None).sample(batch_size, length, family="d4")
    assert observed.coordinate_split is None
    for field, array in expected.items():
        assert torch.equal(getattr(observed, field), torch.from_numpy(array)), field


def test_invalid_maps_and_split_names_fail_closed() -> None:
    with pytest.raises(ValueError):
        map_split(np.arange(N_STATES - 1))
    with pytest.raises(ValueError):
        map_split(np.zeros(N_STATES, dtype=np.int64))
    with pytest.raises(ValueError):
        map_split(np.arange(N_STATES, dtype=np.float64))
    with pytest.raises(ValueError):
        EpisodeGenerator(1, coordinate_split="validation")
    with pytest.raises(ValueError):
        EpisodeGenerator(1).sample(2, 1, coordinate_split="validation")

from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import torch

from .algebra import N_OPERATORS, N_STATES, canonical_maps, conjugate_maps
from .splits import (
    COORDINATE_SPLIT_NAMESPACE,
    audit_coordinate_splits,
    map_fingerprint,
    map_split,
    maps_all_in_split,
    permutations_in_split,
    validate_coordinate_split,
)


def _fixed_family_name(family: str) -> str:
    normalized = family.lower()
    if normalized == "mixed":
        return "mixed_cycle"
    return normalized


@lru_cache(maxsize=None)
def _eligible_coordinate_permutations(family: str, split: str) -> np.ndarray:
    """Enumerate coordinate changes whose two exposed maps share a split."""

    fixed_family = _fixed_family_name(family)
    if fixed_family == "random":
        raise ValueError("random operators do not use a fixed coordinate orbit")
    normalized_split = validate_coordinate_split(split)
    assert normalized_split is not None
    all_phi = np.asarray(tuple(itertools.permutations(range(N_STATES))), dtype=np.int64)
    maps = conjugate_maps(canonical_maps(fixed_family), all_phi)
    eligible = all_phi[maps_all_in_split(maps, normalized_split)]
    if eligible.shape[0] == 0:
        raise RuntimeError(f"no {fixed_family} coordinate realizations belong to split {normalized_split}")
    eligible.setflags(write=False)
    return eligible


@dataclass
class EpisodeBatch:
    tables: torch.Tensor
    maps: torch.Tensor
    op_slots: torch.Tensor
    canonical_ops: torch.Tensor
    start: torch.Tensor
    target: torch.Tensor
    intermediates: torch.Tensor
    canonical_to_slot: torch.Tensor
    phi: torch.Tensor
    family: str
    coordinate_split: str | None = None

    def to(self, device: torch.device | str) -> "EpisodeBatch":
        return EpisodeBatch(
            tables=self.tables.to(device),
            maps=self.maps.to(device),
            op_slots=self.op_slots.to(device),
            canonical_ops=self.canonical_ops.to(device),
            start=self.start.to(device),
            target=self.target.to(device),
            intermediates=self.intermediates.to(device),
            canonical_to_slot=self.canonical_to_slot.to(device),
            phi=self.phi.to(device),
            family=self.family,
            coordinate_split=self.coordinate_split,
        )


class EpisodeGenerator:
    """Generate independently conjugated finite-operator episodes."""

    def __init__(self, seed: int, coordinate_split: str | None = None):
        self.seed = int(seed)
        self.coordinate_split = validate_coordinate_split(coordinate_split)
        self.rng = np.random.default_rng(self.seed)
        self.eye = np.eye(N_STATES, dtype=np.float32)

    def _permutations(self, batch_size: int) -> np.ndarray:
        return np.argsort(self.rng.random((batch_size, N_STATES)), axis=1).astype(np.int64)

    def _canonical_batch_maps(
        self,
        batch_size: int,
        family: str,
        coordinate_split: str | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        fixed_family = _fixed_family_name(family)
        if coordinate_split is not None:
            normalized_split = validate_coordinate_split(coordinate_split)
            assert normalized_split is not None
            if fixed_family == "random":
                phi = self._permutations(batch_size)
                pool = permutations_in_split(normalized_split)
                first = pool[self.rng.integers(0, pool.shape[0], size=batch_size)]
                second = pool[self.rng.integers(0, pool.shape[0], size=batch_size)]
                return np.stack((first, second), axis=1), phi

            pool = _eligible_coordinate_permutations(fixed_family, normalized_split)
            indices = self.rng.integers(0, pool.shape[0], size=batch_size)
            phi = np.asarray(pool[indices], dtype=np.int64)
            maps = conjugate_maps(canonical_maps(fixed_family), phi)
            return maps, phi

        phi = self._permutations(batch_size)
        if fixed_family == "random":
            maps = np.stack((self._permutations(batch_size), self._permutations(batch_size)), axis=1)
            return maps, phi
        return conjugate_maps(canonical_maps(fixed_family), phi), phi

    def sample(
        self,
        batch_size: int,
        length: int,
        family: str = "d4",
        canonical_word: tuple[int, ...] | None = None,
        starts: np.ndarray | None = None,
        coordinate_split: str | None = None,
    ) -> EpisodeBatch:
        if batch_size < 1 or length < 0:
            raise ValueError("batch_size must be positive and length must be nonnegative")
        if canonical_word is not None and len(canonical_word) != length:
            raise ValueError("canonical_word length mismatch")

        effective_split = self.coordinate_split if coordinate_split is None else validate_coordinate_split(coordinate_split)
        canonical_batch_maps, phi = self._canonical_batch_maps(batch_size, family, effective_split)
        swap = self.rng.integers(0, 2, size=batch_size, dtype=np.int64)
        slot_maps = np.empty_like(canonical_batch_maps)
        slot_maps[:, 0] = np.where(swap[:, None].astype(bool), canonical_batch_maps[:, 1], canonical_batch_maps[:, 0])
        slot_maps[:, 1] = np.where(swap[:, None].astype(bool), canonical_batch_maps[:, 0], canonical_batch_maps[:, 1])
        canonical_to_slot = np.stack((swap, 1 - swap), axis=1)

        if canonical_word is None:
            canonical_ops = self.rng.integers(0, N_OPERATORS, size=(batch_size, length), dtype=np.int64)
        else:
            canonical_ops = np.broadcast_to(np.asarray(canonical_word, dtype=np.int64), (batch_size, length)).copy()
        if length:
            op_slots = np.take_along_axis(canonical_to_slot, canonical_ops, axis=1)
        else:
            op_slots = np.empty((batch_size, 0), dtype=np.int64)

        if starts is None:
            start = self.rng.integers(0, N_STATES, size=batch_size, dtype=np.int64)
        else:
            start = np.asarray(starts, dtype=np.int64).copy()
            if start.shape != (batch_size,):
                raise ValueError("starts must have shape (batch_size,)")

        current = start.copy()
        intermediates = np.empty((batch_size, length), dtype=np.int64)
        rows = np.arange(batch_size)
        for t in range(length):
            selected = slot_maps[rows, op_slots[:, t]]
            current = selected[rows, current]
            intermediates[:, t] = current

        tables = self.eye[slot_maps]
        return EpisodeBatch(
            tables=torch.from_numpy(tables),
            maps=torch.from_numpy(slot_maps),
            op_slots=torch.from_numpy(op_slots),
            canonical_ops=torch.from_numpy(canonical_ops),
            start=torch.from_numpy(start),
            target=torch.from_numpy(current),
            intermediates=torch.from_numpy(intermediates),
            canonical_to_slot=torch.from_numpy(canonical_to_slot),
            phi=torch.from_numpy(phi),
            family=family,
            coordinate_split=effective_split,
        )

    @staticmethod
    def slots_for_word(canonical_to_slot: torch.Tensor, word: tuple[int, ...]) -> torch.Tensor:
        if not word:
            return torch.empty((canonical_to_slot.shape[0], 0), dtype=torch.long, device=canonical_to_slot.device)
        word_tensor = torch.tensor(word, dtype=torch.long, device=canonical_to_slot.device)
        expanded = word_tensor.unsqueeze(0).expand(canonical_to_slot.shape[0], -1)
        return torch.gather(canonical_to_slot, 1, expanded)

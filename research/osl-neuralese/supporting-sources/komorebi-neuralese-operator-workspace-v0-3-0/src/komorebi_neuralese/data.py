from __future__ import annotations

import hashlib
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
    map_splits,
    maps_all_in_split,
    permutations_in_split,
    validate_coordinate_split,
    validate_word_product_scope,
    word_product_maps,
    word_products_all_in_split,
)


DIRECT_CONDITIONED_SAMPLER_NAMESPACE = (
    "komorebi-neuralese/fixed-family-direct-conditioned-word-sampler/v1"
)
CONDITIONED_SAMPLER_BACKENDS = ("cached_exact_v1", "rejection_v1", "auto_v1")
# The Stage-A training boundary has at most 12,504 * 2**4 candidate pairs.
# Keeping a conservative cap makes the generalized fixed-family path useful at
# ordinary evaluation lengths without permitting accidental exponential
# allocation for long words.
_MAX_DIRECT_CONDITIONING_PAIRS = 2_000_000


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


@lru_cache(maxsize=None)
def _fixed_coordinate_permutation_pool(family: str, split: str | None) -> np.ndarray:
    """Return the exact uniform coordinate pool used by a fixed family."""

    fixed_family = _fixed_family_name(family)
    if fixed_family == "random":
        raise ValueError("random operators do not have a finite fixed-family coordinate pool")
    if split is not None:
        return _eligible_coordinate_permutations(fixed_family, split)
    pool = np.asarray(tuple(itertools.permutations(range(N_STATES))), dtype=np.int64)
    pool.setflags(write=False)
    return pool


@dataclass(frozen=True)
class _DirectConditionedSupport:
    """Finite support of the exact conditional (coordinate, word) law."""

    phi_indices: np.ndarray
    words: np.ndarray
    candidate_pairs: int
    accepted_pairs: int
    acceptance_probability: float
    digest: str


def _candidate_words(length: int, canonical_word: tuple[int, ...] | None) -> np.ndarray:
    if length == 0:
        words = np.empty((1, 0), dtype=np.int64)
    elif canonical_word is not None:
        words = np.asarray((canonical_word,), dtype=np.int64)
    else:
        words = np.asarray(
            tuple(itertools.product(range(N_OPERATORS), repeat=length)), dtype=np.int64
        ).reshape(-1, length)
    words.setflags(write=False)
    return words


@lru_cache(maxsize=None)
def _direct_conditioned_support(
    family: str,
    coordinate_split: str | None,
    word_product_split: str,
    scope: str,
    length: int,
    canonical_word: tuple[int, ...] | None,
) -> _DirectConditionedSupport | None:
    """Enumerate a fixed family's exact accepted coordinate/word support.

    Before conditioning, the fixed-family generator samples a coordinate
    permutation uniformly and a canonical operator word uniformly.  Rejection
    therefore induces the uniform law on the accepted pair set.  Sampling one
    index uniformly from the support below is exactly that conditional law,
    without replaying rejected candidates in every minibatch.

    ``None`` requests the legacy rejection path.  It is returned for random
    operator families and supports that would exceed the frozen safety cap.
    """

    fixed_family = _fixed_family_name(family)
    if fixed_family == "random":
        return None
    normalized_scope = validate_word_product_scope(scope)
    normalized_word_split = validate_coordinate_split(word_product_split)
    assert normalized_word_split is not None
    normalized_coordinate_split = validate_coordinate_split(coordinate_split)
    phi_pool = _fixed_coordinate_permutation_pool(
        fixed_family, normalized_coordinate_split
    )
    words = _candidate_words(length, canonical_word)
    candidate_pairs = int(phi_pool.shape[0] * words.shape[0])
    if candidate_pairs > _MAX_DIRECT_CONDITIONING_PAIRS:
        return None

    canonical = canonical_maps(fixed_family)
    # A word has very few distinct products in the finite Stage-A families.
    # Classify each conjugated product once, then reuse that membership vector
    # across all words containing it.
    product_membership: dict[bytes, np.ndarray] = {}
    accepted_phi: list[np.ndarray] = []
    accepted_words: list[np.ndarray] = []
    for word in words:
        products = word_product_maps(
            canonical[None, :, :], word.reshape(1, -1), scope=normalized_scope
        )[0]
        valid = np.ones(phi_pool.shape[0], dtype=np.bool_)
        for product in products:
            key = bytes(int(value) for value in product)
            membership = product_membership.get(key)
            if membership is None:
                observed = conjugate_maps(product[None, :], phi_pool)[:, 0, :]
                labels = map_splits(observed)
                assert isinstance(labels, np.ndarray)
                membership = labels == normalized_word_split
                membership.setflags(write=False)
                product_membership[key] = membership
            valid &= membership
            if not np.any(valid):
                break
        indices = np.flatnonzero(valid).astype(np.int32, copy=False)
        if indices.size:
            accepted_phi.append(indices)
            accepted_words.append(np.broadcast_to(word, (indices.size, length)).copy())

    if not accepted_phi:
        raise RuntimeError(
            "the exact fixed-family conditioning support is empty; "
            f"family={family!r}, length={length}, coordinate_split={coordinate_split!r}, "
            f"word_product_split={word_product_split!r}, scope={scope!r}"
        )
    phi_indices = np.concatenate(accepted_phi)
    accepted_word_array = np.concatenate(accepted_words, axis=0).astype(np.int8, copy=False)
    phi_indices.setflags(write=False)
    accepted_word_array.setflags(write=False)
    digest_payload = (
        DIRECT_CONDITIONED_SAMPLER_NAMESPACE.encode("utf-8")
        + b"\x00"
        + fixed_family.encode("utf-8")
        + b"\x00"
        + str(normalized_coordinate_split).encode("utf-8")
        + b"\x00"
        + normalized_word_split.encode("utf-8")
        + b"\x00"
        + normalized_scope.encode("utf-8")
        + b"\x00"
        + np.asarray((length, candidate_pairs), dtype="<i8").tobytes()
        + phi_indices.astype("<i4", copy=False).tobytes()
        + accepted_word_array.tobytes()
    )
    accepted_pairs = int(phi_indices.shape[0])
    return _DirectConditionedSupport(
        phi_indices=phi_indices,
        words=accepted_word_array,
        candidate_pairs=candidate_pairs,
        accepted_pairs=accepted_pairs,
        acceptance_probability=accepted_pairs / candidate_pairs,
        digest=hashlib.sha256(digest_payload).hexdigest(),
    )


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
    word_product_split: str | None = None
    word_product_scope: str = "none"
    sampling_candidates: int = 0
    sampling_rejections: int = 0
    sampling_method: str = "unconditioned"
    conditioned_sampler_backend: str | None = None
    rejection_equivalent_candidate_pairs: int | None = None
    rejection_equivalent_accepted_pairs: int | None = None
    rejection_equivalent_acceptance_probability: float | None = None
    conditioning_support_digest: str | None = None

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
            word_product_split=self.word_product_split,
            word_product_scope=self.word_product_scope,
            sampling_candidates=self.sampling_candidates,
            sampling_rejections=self.sampling_rejections,
            sampling_method=self.sampling_method,
            conditioned_sampler_backend=self.conditioned_sampler_backend,
            rejection_equivalent_candidate_pairs=self.rejection_equivalent_candidate_pairs,
            rejection_equivalent_accepted_pairs=self.rejection_equivalent_accepted_pairs,
            rejection_equivalent_acceptance_probability=(
                self.rejection_equivalent_acceptance_probability
            ),
            conditioning_support_digest=self.conditioning_support_digest,
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

    def _sample_once(
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
        if canonical_word is not None and any(
            not isinstance(operator, (int, np.integer))
            or operator < 0
            or operator >= N_OPERATORS
            for operator in canonical_word
        ):
            raise ValueError(f"canonical_word entries must be integers in 0..{N_OPERATORS - 1}")

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
            sampling_candidates=batch_size,
            sampling_method="unconditioned",
            conditioned_sampler_backend=None,
        )

    def _sample_direct_conditioned(
        self,
        batch_size: int,
        length: int,
        family: str,
        starts: np.ndarray | None,
        coordinate_split: str | None,
        word_product_split: str,
        scope: str,
        support: _DirectConditionedSupport,
        conditioned_sampler_backend: str,
    ) -> EpisodeBatch:
        """Draw directly and uniformly from an exact finite conditional support."""

        fixed_family = _fixed_family_name(family)
        phi_pool = _fixed_coordinate_permutation_pool(fixed_family, coordinate_split)
        support_rows = self.rng.integers(0, support.accepted_pairs, size=batch_size)
        phi = np.asarray(phi_pool[support.phi_indices[support_rows]], dtype=np.int64)
        canonical_batch_maps = conjugate_maps(canonical_maps(fixed_family), phi)

        # Slot relabeling and starts are independent of the split-conditioning
        # event, so sampling them after the accepted pair preserves their exact
        # Bernoulli/uniform laws.
        swap = self.rng.integers(0, 2, size=batch_size, dtype=np.int64)
        slot_maps = np.empty_like(canonical_batch_maps)
        slot_maps[:, 0] = np.where(
            swap[:, None].astype(bool), canonical_batch_maps[:, 1], canonical_batch_maps[:, 0]
        )
        slot_maps[:, 1] = np.where(
            swap[:, None].astype(bool), canonical_batch_maps[:, 0], canonical_batch_maps[:, 1]
        )
        canonical_to_slot = np.stack((swap, 1 - swap), axis=1)
        canonical_ops = np.asarray(support.words[support_rows], dtype=np.int64)
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
        for step in range(length):
            selected = slot_maps[rows, op_slots[:, step]]
            current = selected[rows, current]
            intermediates[:, step] = current

        return EpisodeBatch(
            tables=torch.from_numpy(self.eye[slot_maps]),
            maps=torch.from_numpy(slot_maps),
            op_slots=torch.from_numpy(op_slots),
            canonical_ops=torch.from_numpy(canonical_ops),
            start=torch.from_numpy(start),
            target=torch.from_numpy(current),
            intermediates=torch.from_numpy(intermediates),
            canonical_to_slot=torch.from_numpy(canonical_to_slot),
            phi=torch.from_numpy(phi),
            family=family,
            coordinate_split=coordinate_split,
            word_product_split=word_product_split,
            word_product_scope=scope,
            # These counters describe actual direct draws.  The exact
            # rejection-equivalent population/probability is recorded
            # separately below; no fictional rejected examples are counted.
            sampling_candidates=batch_size,
            sampling_rejections=0,
            sampling_method="direct_conditioned_uniform",
            conditioned_sampler_backend=conditioned_sampler_backend,
            rejection_equivalent_candidate_pairs=support.candidate_pairs,
            rejection_equivalent_accepted_pairs=support.accepted_pairs,
            rejection_equivalent_acceptance_probability=support.acceptance_probability,
            conditioning_support_digest=support.digest,
        )

    def sample(
        self,
        batch_size: int,
        length: int,
        family: str = "d4",
        canonical_word: tuple[int, ...] | None = None,
        starts: np.ndarray | None = None,
        coordinate_split: str | None = None,
        word_product_scope: str = "none",
        word_product_split: str | None = None,
        conditioned_sampler_backend: str = "auto_v1",
    ) -> EpisodeBatch:
        """Sample an episode batch, optionally confining exact word products.

        ``coordinate_split`` confines the two exposed primitive maps.  It does
        not, by itself, constrain maps produced by their compositions.
        ``word_product_scope='contiguous'`` additionally requires every
        nonempty contiguous subword product to belong to ``word_product_split``.
        If the latter is omitted, it inherits ``coordinate_split``.  Fixed
        families with tractable finite support are sampled directly from the
        exact conditional law; larger/random supports use deterministic
        rejection.  Both paths are strict and fail-closed.
        """

        if batch_size < 1 or length < 0:
            raise ValueError("batch_size must be positive and length must be nonnegative")
        if canonical_word is not None and len(canonical_word) != length:
            raise ValueError("canonical_word length mismatch")
        if canonical_word is not None and any(
            not isinstance(operator, (int, np.integer))
            or operator < 0
            or operator >= N_OPERATORS
            for operator in canonical_word
        ):
            raise ValueError(f"canonical_word entries must be integers in 0..{N_OPERATORS - 1}")
        scope = validate_word_product_scope(word_product_scope)
        if conditioned_sampler_backend not in CONDITIONED_SAMPLER_BACKENDS:
            raise ValueError(
                "conditioned_sampler_backend must be one of "
                f"{CONDITIONED_SAMPLER_BACKENDS}"
            )
        effective_split = self.coordinate_split if coordinate_split is None else validate_coordinate_split(coordinate_split)
        effective_word_split = validate_coordinate_split(word_product_split)
        if scope != "none" and effective_word_split is None:
            effective_word_split = effective_split
        if scope != "none" and effective_word_split is None:
            raise ValueError(
                "a non-'none' word_product_scope requires word_product_split or coordinate_split"
            )
        if scope == "none" and word_product_split is not None:
            raise ValueError("word_product_split requires a non-'none' word_product_scope")

        # Preserve the historical RNG stream byte-for-byte when no composition
        # boundary is requested.
        if scope == "none":
            return self._sample_once(
                batch_size,
                length,
                family=family,
                canonical_word=canonical_word,
                starts=starts,
                coordinate_split=coordinate_split,
            )

        support = None
        if conditioned_sampler_backend != "rejection_v1":
            support = _direct_conditioned_support(
                _fixed_family_name(family),
                effective_split,
                effective_word_split,
                scope,
                length,
                canonical_word,
            )
        if support is not None:
            assert effective_word_split is not None
            return self._sample_direct_conditioned(
                batch_size=batch_size,
                length=length,
                family=family,
                starts=starts,
                coordinate_split=effective_split,
                word_product_split=effective_word_split,
                scope=scope,
                support=support,
                conditioned_sampler_backend=conditioned_sampler_backend,
            )
        if conditioned_sampler_backend == "cached_exact_v1":
            raise RuntimeError(
                "cached_exact_v1 has no tractable exact support for this request; "
                "select rejection_v1 explicitly"
            )

        requested_starts: np.ndarray | None = None
        pending_positions: np.ndarray | None = None
        if starts is not None:
            requested_starts = np.asarray(starts, dtype=np.int64).copy()
            if requested_starts.shape != (batch_size,):
                raise ValueError("starts must have shape (batch_size,)")
            pending_positions = np.arange(batch_size, dtype=np.int64)

        accepted_chunks: list[EpisodeBatch] = []
        accepted_positions: list[np.ndarray] = []
        accepted = 0
        candidates = 0
        maximum_candidates = max(1024, 1024 * batch_size)
        while accepted < batch_size:
            if pending_positions is None:
                candidate_size = batch_size - accepted
                candidate_starts = None
            else:
                candidate_size = int(pending_positions.shape[0])
                candidate_starts = requested_starts[pending_positions]
            candidate = self._sample_once(
                candidate_size,
                length,
                family=family,
                canonical_word=canonical_word,
                starts=candidate_starts,
                coordinate_split=coordinate_split,
            )
            candidates += candidate_size
            keep_numpy = word_products_all_in_split(
                candidate.maps.numpy(),
                candidate.op_slots.numpy(),
                effective_word_split,
                scope=scope,
            )
            keep_indices = np.flatnonzero(keep_numpy)
            if keep_indices.size:
                index = torch.from_numpy(keep_indices.copy())
                accepted_chunks.append(
                    EpisodeBatch(
                        tables=candidate.tables[index],
                        maps=candidate.maps[index],
                        op_slots=candidate.op_slots[index],
                        canonical_ops=candidate.canonical_ops[index],
                        start=candidate.start[index],
                        target=candidate.target[index],
                        intermediates=candidate.intermediates[index],
                        canonical_to_slot=candidate.canonical_to_slot[index],
                        phi=candidate.phi[index],
                        family=candidate.family,
                        coordinate_split=candidate.coordinate_split,
                    )
                )
                accepted += int(keep_indices.size)
                if pending_positions is not None:
                    accepted_positions.append(pending_positions[keep_numpy])
            if pending_positions is not None:
                pending_positions = pending_positions[~keep_numpy]
            if candidates >= maximum_candidates and accepted < batch_size:
                raise RuntimeError(
                    "word-product split rejection exceeded the fail-closed candidate limit; "
                    f"accepted {accepted}/{batch_size} for family={family!r}, length={length}, "
                    f"split={effective_word_split!r}, scope={scope!r}"
                )

        def concatenate(field: str) -> torch.Tensor:
            return torch.cat([getattr(chunk, field) for chunk in accepted_chunks], dim=0)

        output = EpisodeBatch(
            tables=concatenate("tables"),
            maps=concatenate("maps"),
            op_slots=concatenate("op_slots"),
            canonical_ops=concatenate("canonical_ops"),
            start=concatenate("start"),
            target=concatenate("target"),
            intermediates=concatenate("intermediates"),
            canonical_to_slot=concatenate("canonical_to_slot"),
            phi=concatenate("phi"),
            family=family,
            coordinate_split=effective_split,
            word_product_split=effective_word_split,
            word_product_scope=scope,
            sampling_candidates=candidates,
            sampling_rejections=candidates - batch_size,
            sampling_method="deterministic_rejection",
            conditioned_sampler_backend=conditioned_sampler_backend,
        )
        if accepted_positions:
            positions = np.concatenate(accepted_positions)
            order = torch.from_numpy(np.argsort(positions).astype(np.int64, copy=False))
            output = EpisodeBatch(
                tables=output.tables[order],
                maps=output.maps[order],
                op_slots=output.op_slots[order],
                canonical_ops=output.canonical_ops[order],
                start=output.start[order],
                target=output.target[order],
                intermediates=output.intermediates[order],
                canonical_to_slot=output.canonical_to_slot[order],
                phi=output.phi[order],
                family=output.family,
                coordinate_split=output.coordinate_split,
                word_product_split=output.word_product_split,
                word_product_scope=output.word_product_scope,
                sampling_candidates=output.sampling_candidates,
                sampling_rejections=output.sampling_rejections,
                sampling_method=output.sampling_method,
                conditioned_sampler_backend=output.conditioned_sampler_backend,
                rejection_equivalent_candidate_pairs=(
                    output.rejection_equivalent_candidate_pairs
                ),
                rejection_equivalent_accepted_pairs=(
                    output.rejection_equivalent_accepted_pairs
                ),
                rejection_equivalent_acceptance_probability=(
                    output.rejection_equivalent_acceptance_probability
                ),
                conditioning_support_digest=output.conditioning_support_digest,
            )
        return output

    @staticmethod
    def slots_for_word(canonical_to_slot: torch.Tensor, word: tuple[int, ...]) -> torch.Tensor:
        if not word:
            return torch.empty((canonical_to_slot.shape[0], 0), dtype=torch.long, device=canonical_to_slot.device)
        word_tensor = torch.tensor(word, dtype=torch.long, device=canonical_to_slot.device)
        expanded = word_tensor.unsqueeze(0).expand(canonical_to_slot.shape[0], -1)
        return torch.gather(canonical_to_slot, 1, expanded)

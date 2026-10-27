from __future__ import annotations

import itertools
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import N_OPERATORS, canonical_maps, conjugate_maps
from komorebi_neuralese.data import (
    DIRECT_CONDITIONED_SAMPLER_NAMESPACE,
    EpisodeGenerator,
    _direct_conditioned_support,
    _eligible_coordinate_permutations,
)
from komorebi_neuralese.models import build_model
from komorebi_neuralese.splits import word_products_all_in_split
from komorebi_neuralese.train import (
    TRAIN_LENGTH_SCHEDULE_NAMESPACE,
    TrainConfig,
    _training_length_schedule,
    train_arm,
)


def _independent_accepted_pairs(length: int) -> tuple[np.ndarray, np.ndarray]:
    """Exhaust the legacy proposal law and retain exactly its accepted pairs."""

    phi_pool = _eligible_coordinate_permutations("d4", "train")
    maps = conjugate_maps(canonical_maps("d4"), phi_pool)
    accepted_phi: list[np.ndarray] = []
    accepted_words: list[np.ndarray] = []
    for word_tuple in itertools.product(range(N_OPERATORS), repeat=length):
        word = np.asarray(word_tuple, dtype=np.int64)
        words = np.broadcast_to(word, (phi_pool.shape[0], length))
        keep = word_products_all_in_split(maps, words, "train", scope="contiguous")
        indices = np.flatnonzero(keep).astype(np.int32, copy=False)
        if indices.size:
            accepted_phi.append(indices)
            accepted_words.append(np.broadcast_to(word, (indices.size, length)).copy())
    return np.concatenate(accepted_phi), np.concatenate(accepted_words, axis=0)


@pytest.mark.parametrize("length", (1, 2, 3, 4))
def test_direct_support_exactly_equals_exhaustive_rejection_support(length: int) -> None:
    support = _direct_conditioned_support(
        "d4", "train", "train", "contiguous", length, None
    )
    assert support is not None
    expected_phi, expected_words = _independent_accepted_pairs(length)
    assert np.array_equal(support.phi_indices, expected_phi)
    assert np.array_equal(support.words, expected_words)
    assert support.candidate_pairs == 12_504 * (2**length)
    assert support.accepted_pairs == expected_phi.shape[0]
    assert support.acceptance_probability == pytest.approx(
        expected_phi.shape[0] / support.candidate_pairs, abs=0.0
    )


def test_direct_sampler_is_exact_uniform_index_sampling_from_conditional_support() -> None:
    seed = 1301
    batch_size = 4096
    length = 4
    support = _direct_conditioned_support(
        "d4", "train", "train", "contiguous", length, None
    )
    assert support is not None
    phi_pool = _eligible_coordinate_permutations("d4", "train")

    # Replay the documented direct law independently: one uniform support-row
    # draw, followed by independent slot-swap and start draws.
    reference_rng = np.random.default_rng(seed)
    support_rows = reference_rng.integers(0, support.accepted_pairs, size=batch_size)
    expected_phi = phi_pool[support.phi_indices[support_rows]]
    expected_words = support.words[support_rows].astype(np.int64)
    expected_swap = reference_rng.integers(0, 2, size=batch_size, dtype=np.int64)
    expected_starts = reference_rng.integers(0, 8, size=batch_size, dtype=np.int64)

    observed = EpisodeGenerator(seed, coordinate_split="train").sample(
        batch_size,
        length,
        family="d4",
        word_product_scope="contiguous",
    )
    assert np.array_equal(observed.phi.numpy(), expected_phi)
    assert np.array_equal(observed.canonical_ops.numpy(), expected_words)
    assert np.array_equal(observed.canonical_to_slot[:, 0].numpy(), expected_swap)
    assert np.array_equal(observed.start.numpy(), expected_starts)


def test_direct_sampler_is_strict_deterministic_and_auditable() -> None:
    first = EpisodeGenerator(1403, coordinate_split="train").sample(
        8192, 4, family="d4", word_product_scope="contiguous"
    )
    second = EpisodeGenerator(1403, coordinate_split="train").sample(
        8192, 4, family="d4", word_product_scope="contiguous"
    )
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
    assert np.all(
        word_products_all_in_split(
            first.maps.numpy(), first.op_slots.numpy(), "train", scope="contiguous"
        )
    )
    assert first.sampling_method == "direct_conditioned_uniform"
    assert first.conditioned_sampler_backend == "auto_v1"
    assert first.sampling_candidates == 8192
    assert first.sampling_rejections == 0
    assert first.rejection_equivalent_candidate_pairs == 200_064
    assert first.rejection_equivalent_accepted_pairs == 45_680
    assert first.rejection_equivalent_acceptance_probability == pytest.approx(
        45_680 / 200_064
    )
    assert len(first.conditioning_support_digest or "") == 64
    assert first.conditioning_support_digest == second.conditioning_support_digest
    assert DIRECT_CONDITIONED_SAMPLER_NAMESPACE.endswith("/v1")


def test_requested_starts_and_fixed_word_preserve_direct_conditioning_semantics() -> None:
    starts = np.arange(513, dtype=np.int64) % 8
    word = (1, 0, 1, 0)
    batch = EpisodeGenerator(1507, coordinate_split="train").sample(
        starts.shape[0],
        len(word),
        family="d4",
        canonical_word=word,
        starts=starts,
        word_product_scope="contiguous",
    )
    assert batch.sampling_method == "direct_conditioned_uniform"
    assert np.array_equal(batch.start.numpy(), starts)
    assert np.array_equal(
        batch.canonical_ops.numpy(), np.broadcast_to(word, (starts.shape[0], len(word)))
    )
    assert np.all(
        word_products_all_in_split(
            batch.maps.numpy(), batch.op_slots.numpy(), "train", scope="contiguous"
        )
    )


def test_random_family_retains_fail_closed_rejection_fallback() -> None:
    batch = EpisodeGenerator(1601, coordinate_split="train").sample(
        256, 4, family="random", word_product_scope="contiguous"
    )
    assert batch.sampling_method == "deterministic_rejection"
    assert batch.conditioned_sampler_backend == "auto_v1"
    assert batch.rejection_equivalent_candidate_pairs is None
    assert batch.rejection_equivalent_accepted_pairs is None
    assert batch.rejection_equivalent_acceptance_probability is None
    assert batch.conditioning_support_digest is None
    assert batch.sampling_candidates >= 256
    assert batch.sampling_rejections == batch.sampling_candidates - 256
    assert np.all(
        word_products_all_in_split(
            batch.maps.numpy(), batch.op_slots.numpy(), "train", scope="contiguous"
        )
    )


def test_conditioning_support_is_cached() -> None:
    _direct_conditioned_support.cache_clear()
    EpisodeGenerator(1709, coordinate_split="train").sample(
        32, 4, family="d4", word_product_scope="contiguous"
    )
    after_cold = _direct_conditioned_support.cache_info()
    EpisodeGenerator(1711, coordinate_split="train").sample(
        32, 4, family="d4", word_product_scope="contiguous"
    )
    after_warm = _direct_conditioned_support.cache_info()
    assert after_cold.misses == 1
    assert after_warm.misses == 1
    assert after_warm.hits == after_cold.hits + 1


def test_cold_support_construction_consumes_no_episode_rng() -> None:
    seed = 1801
    _direct_conditioned_support.cache_clear()
    generator = EpisodeGenerator(seed, coordinate_split="train")
    _direct_conditioned_support("d4", "train", "train", "contiguous", 4, None)
    observed = generator.rng.random(16)
    expected = np.random.default_rng(seed).random(16)
    assert np.array_equal(observed, expected)


def test_length_schedule_is_independent_of_direct_or_rejection_sampler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import komorebi_neuralese.data as data_module

    config = TrainConfig(
        model_name="linear_hyper_hard",
        regime="terminal",
        seed=1907,
        steps=24,
        batch_size=8,
        train_min_length=1,
        train_max_length=4,
        max_eval_length=8,
        learning_rate=8e-4,
        composition_weight=0.0,
        device="cpu",
    )
    torch.manual_seed(11)
    direct = train_arm(build_model("linear_hyper_hard", max_length=8), config)

    monkeypatch.setattr(data_module, "_direct_conditioned_support", lambda *args: None)
    torch.manual_seed(11)
    rejection = train_arm(
        build_model("linear_hyper_hard", max_length=8),
        replace(config, conditioned_sampler_backend="rejection_v1"),
    )

    assert direct.sampling_audit["sampling_methods"] == ["direct_conditioned_uniform"]
    assert rejection.sampling_audit["sampling_methods"] == ["deterministic_rejection"]
    assert direct.sampling_audit["length_schedule"] == rejection.sampling_audit["length_schedule"]
    receipt = direct.sampling_audit["length_schedule"]
    assert receipt["namespace"] == TRAIN_LENGTH_SCHEDULE_NAMESPACE
    assert receipt["independent_of_episode_sampler"] is True
    assert sum(receipt["counts"].values()) == config.steps

    schedule, replay = _training_length_schedule(
        config.seed, config.train_min_length, config.train_max_length, config.steps
    )
    assert replay == receipt
    assert all(config.train_min_length <= int(value) <= config.train_max_length for value in schedule)


def test_cached_exact_backend_fails_closed_when_support_is_not_tractable() -> None:
    with pytest.raises(RuntimeError, match="cached_exact_v1 has no tractable exact support"):
        EpisodeGenerator(2003, coordinate_split="train").sample(
            8,
            4,
            family="random",
            word_product_scope="contiguous",
            conditioned_sampler_backend="cached_exact_v1",
        )
    with pytest.raises(ValueError, match="conditioned_sampler_backend"):
        EpisodeGenerator(2005, coordinate_split="train").sample(
            8,
            4,
            family="d4",
            word_product_scope="contiguous",
            conditioned_sampler_backend="unknown",
        )

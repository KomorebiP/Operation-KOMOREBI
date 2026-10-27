from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.composition_training import (
    anonymous_multiscale_composition_loss,
    enumerate_action_words,
    finite_transition_map,
    group_words_by_demonstrated_action,
    induced_action,
    multiscale_composition_consistency_loss,
    oriented_projective_chordal_loss,
    rollout_word_endpoints,
    spd_metric_from_factor,
)


def _idempotent_system() -> torch.Tensor:
    # These are anonymous table slots, not named algebra generators.
    return torch.tensor(
        [
            [1, 1, 2],
            [0, 2, 2],
        ],
        dtype=torch.long,
    )


def _identity_swap_system() -> torch.Tensor:
    return torch.tensor([[0, 1], [1, 0]], dtype=torch.long)


def _word_bank() -> tuple[tuple[int, ...], ...]:
    return ((), (0,), (1,), (1, 1), (0, 1), (0, 1, 1, 0), (1, 0, 0, 0))


def _group_partition(classes: object) -> set[frozenset[int]]:
    return {frozenset(item.word_indices) for item in classes}  # type: ignore[attr-defined]


def test_words_are_grouped_by_induced_table_action_not_named_relations() -> None:
    action_table = _idempotent_system()
    words = ((), (0,), (0, 0), (1,), (1, 1), (0, 1), (0, 1, 0), (1, 0))
    classes = group_words_by_demonstrated_action(action_table, words)
    partition = _group_partition(classes)
    assert frozenset({1, 2}) in partition  # slot 0 is idempotent
    assert frozenset({3, 4}) in partition  # slot 1 is independently idempotent
    assert frozenset({5, 6}) in partition  # a longer table-derived composition
    assert induced_action(action_table, (0, 1)).tolist() == [2, 2, 2]


def test_operator_slot_relabeling_does_not_change_equivalence_partition() -> None:
    table = _idempotent_system()
    words = ((), (0,), (0, 0), (1,), (1, 1), (0, 1), (1, 0), (0, 1, 0))
    original = group_words_by_demonstrated_action(table, words)
    relabeled_table = table.flip(0)
    relabeled_words = tuple(tuple(1 - action for action in word) for word in words)
    relabeled = group_words_by_demonstrated_action(relabeled_table, relabeled_words)
    assert _group_partition(original) == _group_partition(relabeled)


def test_partial_demonstrations_control_observational_equivalence() -> None:
    table = torch.tensor([[0, 0, 2], [0, 1, 1]], dtype=torch.long)
    words = ((0,), (1,))
    partial = group_words_by_demonstrated_action(table, words, observed_states=[0])
    full = group_words_by_demonstrated_action(table, words)
    assert len(partial) == 1
    assert len(full) == 2


def test_dense_episode_tables_convert_only_when_deterministic() -> None:
    transition_map = _identity_swap_system()
    dense = torch.nn.functional.one_hot(transition_map, num_classes=2).to(torch.float64)
    assert torch.equal(finite_transition_map(dense), transition_map)
    dense[0, 0] = torch.tensor([0.5, 0.5], dtype=torch.float64)
    with pytest.raises(ValueError, match="deterministic one-hot"):
        finite_transition_map(dense)


def test_oriented_projective_loss_has_the_required_gauge_semantics() -> None:
    state = torch.tensor([[1.5, -0.5]], dtype=torch.float64)
    assert oriented_projective_chordal_loss(state, 7.0 * state).item() == pytest.approx(0.0)
    assert oriented_projective_chordal_loss(state, -state).item() == pytest.approx(2.0)
    zero = torch.zeros_like(state)
    assert oriented_projective_chordal_loss(zero, zero).item() == pytest.approx(1.0)


def test_loss_is_invariant_to_positive_gauge_and_coordinate_transport() -> None:
    generator = torch.Generator().manual_seed(41)
    words = _word_bank()
    endpoints = torch.randn(len(words), 2, 3, generator=generator, dtype=torch.float64)
    factor = torch.tensor(
        [[1.3, 0.0, 0.0], [0.2, 0.9, 0.0], [-0.1, 0.3, 1.1]],
        dtype=torch.float64,
    )
    metric = spd_metric_from_factor(factor, diagonal_floor=0.2)
    options = dict(
        metric=metric,
        scales=(1, 2, 4),
        separation_weight=0.3,
        separation_margin=0.8,
    )
    original = multiscale_composition_consistency_loss(
        endpoints,
        _identity_swap_system(),
        words,
        **options,
    )

    positive_gauge = torch.rand(len(words), 2, 1, generator=generator, dtype=torch.float64) + 0.2
    gauged = multiscale_composition_consistency_loss(
        endpoints * positive_gauge,
        _identity_swap_system(),
        words,
        **options,
    )
    assert torch.allclose(original.loss, gauged.loss, atol=1e-12, rtol=1e-12)

    coordinate_change = torch.tensor(
        [[1.1, 0.3, -0.2], [0.0, 0.8, 0.4], [0.2, -0.1, 1.4]],
        dtype=torch.float64,
    )
    inverse = torch.linalg.inv(coordinate_change)
    transported_metric = inverse.transpose(0, 1) @ metric @ inverse
    transported_endpoints = endpoints @ coordinate_change.transpose(0, 1)
    transported = multiscale_composition_consistency_loss(
        transported_endpoints,
        _identity_swap_system(),
        words,
        metric=transported_metric,
        scales=(1, 2, 4),
        separation_weight=0.3,
        separation_margin=0.8,
    )
    assert torch.allclose(original.loss, transported.loss, atol=1e-12, rtol=1e-12)
    assert torch.allclose(original.consistency_loss, transported.consistency_loss, atol=1e-12, rtol=1e-12)


def test_pairs_are_binned_once_across_multiple_word_scales() -> None:
    words = _word_bank()
    endpoints = torch.randn(len(words), 2, 3, generator=torch.Generator().manual_seed(7))
    result = multiscale_composition_consistency_loss(
        endpoints,
        _identity_swap_system(),
        words,
        scales=(1, 2, 4),
    )
    assert [(item.scale, item.pair_count) for item in result.per_scale] == [(1, 1), (2, 3), (4, 5)]
    assert result.equivalent_pair_count == 9


def test_exact_positive_ray_action_endpoints_have_zero_consistency() -> None:
    table = _identity_swap_system()
    words = _word_bank()
    semantic = torch.eye(2, dtype=torch.float64)
    endpoints = []
    for index, word in enumerate(words):
        action = induced_action(table, word)
        endpoints.append((index + 1.0) * semantic[action])
    result = multiscale_composition_consistency_loss(
        torch.stack(endpoints),
        table,
        words,
        scales=(1, 2, 4),
    )
    assert result.consistency_loss.item() == pytest.approx(0.0, abs=1e-12)


def test_optional_separation_term_detects_collapsed_action_classes() -> None:
    words = ((), (0,), (1,), (1, 1))
    collapsed = torch.ones(len(words), 2, 3, dtype=torch.float64)
    without_separation = multiscale_composition_consistency_loss(
        collapsed,
        _identity_swap_system(),
        words,
        scales=(1, 2),
    )
    with_separation = multiscale_composition_consistency_loss(
        collapsed,
        _identity_swap_system(),
        words,
        scales=(1, 2),
        separation_weight=1.0,
        separation_margin=0.7,
    )
    assert without_separation.loss.item() == pytest.approx(0.0)
    assert with_separation.separation_loss.item() == pytest.approx(0.7)
    assert with_separation.loss.item() == pytest.approx(0.7)
    assert with_separation.separation_pair_count > 0


def test_shared_prefix_rollout_is_correct_and_loss_backpropagates() -> None:
    table = _identity_swap_system()
    words = enumerate_action_words(2, 3)
    initial = torch.tensor([[1.0, 0.1], [0.2, 1.0]], dtype=torch.float64, requires_grad=True)
    codes = torch.tensor(
        [
            [[1.02, 0.03], [-0.02, 0.97]],
            [[0.04, 0.94], [1.07, -0.01]],
        ],
        dtype=torch.float64,
        requires_grad=True,
    )

    calls = 0

    def step(hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        nonlocal calls
        calls += 1
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    endpoints, normalized = rollout_word_endpoints(initial, codes, words, step)
    assert endpoints.shape == (15, 2, 2)
    assert normalized == words
    assert calls == 14  # once for every nonempty prefix, not once per word per depth

    result = anonymous_multiscale_composition_loss(
        initial,
        codes,
        table,
        words,
        lambda hidden, code: torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1),
        scales=(1, 2, 3),
        separation_weight=0.2,
    )
    result.loss.backward()
    assert result.loss.requires_grad
    assert codes.grad is not None and bool(torch.isfinite(codes.grad).all())
    assert initial.grad is not None and bool(torch.isfinite(initial.grad).all())
    assert float(codes.grad.abs().sum()) > 0


def test_invalid_words_scales_and_metrics_fail_closed() -> None:
    table = _identity_swap_system()
    endpoints = torch.ones(2, 2, 2)
    with pytest.raises(ValueError, match="unique"):
        multiscale_composition_consistency_loss(endpoints, table, [(), ()])
    with pytest.raises(ValueError, match="cover"):
        multiscale_composition_consistency_loss(endpoints, table, [(), (1, 1)], scales=(1,))
    with pytest.raises(ValueError, match="positive definite"):
        oriented_projective_chordal_loss(
            torch.ones(2),
            torch.ones(2),
            torch.tensor([[1.0, 0.0], [0.0, -1.0]]),
        )

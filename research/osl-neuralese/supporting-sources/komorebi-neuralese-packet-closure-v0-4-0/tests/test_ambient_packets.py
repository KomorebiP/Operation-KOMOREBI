from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.ambient_packets import (
    SuffixSplit,
    build_constraint_split,
    build_continuation_constraints,
    continuation_margins,
    enumerate_suffixes,
    normalize_oriented_rays,
    oriented_projective_distance,
    oriented_projective_normalize,
    split_suffixes_for_validation,
    suffix_transition_signature,
    summarize_packet_erosion,
    validate_suffix_split,
)


def _permutation_system() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    decoder = torch.eye(3, dtype=torch.float64)
    transitions = torch.tensor(
        [
            [1, 2, 0],
            [0, 2, 1],
        ],
        dtype=torch.long,
    )
    operators = torch.zeros(2, 3, 3, dtype=torch.float64)
    for action in range(2):
        for source in range(3):
            operators[action, transitions[action, source], source] = 1.0
    return decoder, operators, transitions


def _delayed_failure_system() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    decoder = torch.eye(2, dtype=torch.float64)
    operators = torch.tensor([[[1.0, 0.0], [0.9, 1.0]]], dtype=torch.float64)
    transitions = torch.tensor([[0, 1]], dtype=torch.long)
    return decoder, operators, transitions


def test_oriented_normalization_preserves_sign_and_positive_scale() -> None:
    states = torch.tensor([[3.0, 4.0], [-3.0, -4.0]], dtype=torch.float64)
    normalized = oriented_projective_normalize(states)
    scaled = oriented_projective_normalize(7.25 * states)
    assert torch.allclose(normalized, scaled)
    assert torch.allclose(normalized[0], -normalized[1])
    distance = oriented_projective_distance(states[:1], states[1:])
    assert torch.allclose(distance, torch.tensor([math.pi], dtype=torch.float64), atol=1e-12, rtol=0)


def test_zero_and_nonfinite_states_are_explicitly_invalid() -> None:
    states = torch.tensor([[0.0, 0.0], [float("nan"), 1.0], [1.0, 0.0]])
    batch = normalize_oriented_rays(states)
    assert batch.valid.tolist() == [False, False, True]
    assert torch.equal(batch.representatives[:2], torch.zeros(2, 2))
    with pytest.raises(ValueError, match="cannot normalize 2"):
        oriented_projective_normalize(states)
    permissive = oriented_projective_normalize(states, zero_policy="zeros")
    assert torch.equal(permissive[:2], torch.zeros(2, 2))


def test_metric_normalization_rejects_non_spd_metrics() -> None:
    state = torch.tensor([1.0, 2.0], dtype=torch.float64)
    with pytest.raises(ValueError, match="symmetric"):
        oriented_projective_normalize(state, torch.tensor([[1.0, 2.0], [0.0, 1.0]]))
    with pytest.raises(ValueError, match="positive definite"):
        oriented_projective_normalize(state, torch.tensor([[1.0, 0.0], [0.0, -1.0]]))


def test_constraint_builder_matches_exact_permutation_execution() -> None:
    decoder, operators, transitions = _permutation_system()
    suffixes = enumerate_suffixes(2, 3)
    constraints = build_continuation_constraints(
        decoder,
        operators,
        transitions,
        source_state=0,
        suffixes=suffixes,
    )
    assert constraints.constraint_count == len(suffixes) * 2
    assert constraints.horizon == 3
    state = torch.tensor([[1.0, 0.0, 0.0]], dtype=torch.float64)
    result = continuation_margins(state, constraints)
    assert result.inside.item()
    assert float(result.minimum_margin) == pytest.approx(1.0 / math.sqrt(2.0))
    assert bool(result.valid_constraints.all())


def test_continuation_margin_is_scale_and_coordinate_invariant() -> None:
    normals = torch.tensor([[1.0, -1.0]], dtype=torch.float64)
    states = torch.tensor([[2.0, 0.0], [20.0, 0.0]], dtype=torch.float64)
    metric = torch.tensor([[4.0, 0.0], [0.0, 1.0]], dtype=torch.float64)
    original = continuation_margins(states, normals, metric)
    assert torch.allclose(original.minimum_margin[0], original.minimum_margin[1])

    transform = torch.tensor([[2.0, 1.0], [0.0, 0.5]], dtype=torch.float64)
    inverse = torch.linalg.inv(transform)
    transformed_states = states @ transform.transpose(0, 1)
    transformed_normals = normals @ inverse
    transformed_metric = inverse.transpose(0, 1) @ metric @ inverse
    transformed = continuation_margins(transformed_states, transformed_normals, transformed_metric)
    assert torch.allclose(original.minimum_margin, transformed.minimum_margin, atol=1e-12, rtol=1e-12)


def test_degenerate_constraints_are_flagged_and_never_pass() -> None:
    states = torch.tensor([[1.0, 0.0], [0.0, 0.0]], dtype=torch.float64)
    normals = torch.tensor([[0.0, 0.0], [1.0, -1.0]], dtype=torch.float64)
    result = continuation_margins(states, normals)
    assert result.valid_constraints.tolist() == [False, True]
    assert torch.isneginf(result.signed_margins[0, 0])
    assert not result.inside[0]
    assert torch.isnan(result.minimum_margin[1])
    assert result.active_constraint[1].item() == -1
    assert not result.inside[1]


def test_transition_equivalent_suffixes_stay_on_one_side_of_split() -> None:
    _, _, transitions = _permutation_system()
    suffixes = enumerate_suffixes(2, 4)
    key = lambda word: suffix_transition_signature(transitions, word)
    split = split_suffixes_for_validation(
        suffixes,
        heldout_fraction=0.35,
        seed=19,
        equivalence_key=key,
    )
    construction_keys = {key(word) for word in split.construction}
    heldout_keys = {key(word) for word in split.heldout}
    assert construction_keys.isdisjoint(heldout_keys)
    assert () in split.construction
    assert split.heldout
    validate_suffix_split(split, equivalence_key=key)


def test_validate_suffix_split_rejects_exact_and_equivalence_leakage() -> None:
    exact_leak = SuffixSplit(
        construction=((), (0,)),
        heldout=((0,),),
        construction_group_keys=((), (0,)),
        heldout_group_keys=((0,),),
        seed=0,
    )
    with pytest.raises(ValueError, match="suffix leakage"):
        validate_suffix_split(exact_leak)

    equivalent_leak = SuffixSplit(
        construction=((0,),),
        heldout=((1,),),
        construction_group_keys=("same",),
        heldout_group_keys=("same",),
        seed=0,
    )
    with pytest.raises(ValueError, match="equivalence-group leakage"):
        validate_suffix_split(equivalent_leak, equivalence_key=lambda _: "same")


def test_heldout_constraints_are_not_used_to_define_construction_packet() -> None:
    decoder, operators, transitions = _delayed_failure_system()
    split = SuffixSplit(
        construction=((), (0,)),
        heldout=((0, 0),),
        construction_group_keys=((), (0,)),
        heldout_group_keys=((0, 0),),
        seed=0,
    )
    constraints = build_constraint_split(decoder, operators, transitions, 0, split)
    state = torch.tensor([[1.0, 0.0]], dtype=torch.float64)
    construction_result = continuation_margins(state, constraints.construction)
    heldout_result = continuation_margins(state, constraints.heldout)
    assert construction_result.inside.item()
    assert not heldout_result.inside.item()
    assert float(heldout_result.minimum_margin) < 0.0


def test_packet_erosion_summary_detects_first_delayed_failure() -> None:
    decoder, operators, transitions = _delayed_failure_system()
    by_depth = {
        depth: build_continuation_constraints(
            decoder,
            operators,
            transitions,
            0,
            max_depth=depth,
        )
        for depth in range(4)
    }
    state = torch.tensor([[1.0, 0.0]], dtype=torch.float64)
    summary = summarize_packet_erosion(state, by_depth)
    assert summary.depths == (0, 1, 2, 3)
    assert summary.inside_by_depth.tolist() == [[True, True, False, False]]
    assert summary.first_failure_depth.tolist() == [2]
    assert summary.conditional_retention_fraction.tolist() == [1.0, 1.0, 0.0, 0.0]
    assert summary.monotonicity_violations == 0
    assert torch.all(summary.minimum_margin_by_depth[:, 1:] <= summary.minimum_margin_by_depth[:, :-1])


def test_packet_erosion_summary_keeps_invalid_states_out_of_rates() -> None:
    decoder, operators, transitions = _delayed_failure_system()
    constraints = {0: build_continuation_constraints(decoder, operators, transitions, 0, max_depth=0)}
    states = torch.tensor([[1.0, 0.0], [0.0, 0.0]], dtype=torch.float64)
    summary = summarize_packet_erosion(states, constraints)
    assert summary.valid_states.tolist() == [True, False]
    assert summary.first_failure_depth.tolist() == [-1, -2]
    assert summary.survival_fraction.tolist() == [1.0]


def test_constraint_builder_rejects_duplicate_or_out_of_alphabet_suffixes() -> None:
    decoder, operators, transitions = _permutation_system()
    with pytest.raises(ValueError, match="unique"):
        build_continuation_constraints(
            decoder,
            operators,
            transitions,
            0,
            suffixes=[(0,), (0,)],
        )
    with pytest.raises(ValueError, match="outside"):
        build_continuation_constraints(
            decoder,
            operators,
            transitions,
            0,
            suffixes=[(2,)],
        )
    with pytest.raises(TypeError, match="must be integers"):
        build_continuation_constraints(
            decoder,
            operators,
            transitions,
            0,
            suffixes=[(0.5,)],
        )

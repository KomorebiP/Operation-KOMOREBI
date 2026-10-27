from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import canonical_maps
from komorebi_neuralese.packet_training import (
    RelationGroupedSuffixPlan,
    audit_heldout_packet,
    construction_packet_margin_loss,
    make_relation_grouped_suffix_plan,
    relation_groups,
)


def _transition_tuple() -> tuple[tuple[int, ...], ...]:
    return ((1, 2, 0), (0, 2, 1))


def _manual_plan() -> RelationGroupedSuffixPlan:
    return RelationGroupedSuffixPlan(
        canonical_transitions=_transition_tuple(),
        construction=((), (0,)),
        heldout=((1,),),
        seed=17,
        heldout_fraction=1.0 / 3.0,
    )


def _system(
    *,
    batch: int = 2,
    dtype: torch.dtype = torch.float64,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    transitions = torch.tensor(_transition_tuple(), dtype=torch.long)
    operators = torch.zeros(2, 3, 3, dtype=dtype)
    for action in range(2):
        for source in range(3):
            operators[action, transitions[action, source], source] = 1.0
    operators = operators.unsqueeze(0).expand(batch, -1, -1, -1).clone()
    maps = transitions.unsqueeze(0).expand(batch, -1, -1).clone()
    canonical_to_slot = torch.arange(2, dtype=torch.long).unsqueeze(0).expand(batch, -1).clone()
    decoder = torch.eye(3, dtype=dtype)
    metric = torch.diag(torch.tensor([4.0, 1.0, 0.25], dtype=dtype))
    return operators, decoder, metric, maps, canonical_to_slot


def test_relation_grouped_plan_is_deterministic_and_does_not_touch_global_rng() -> None:
    transitions = torch.from_numpy(canonical_maps("d4")).long()
    torch.manual_seed(90210)
    random.seed(90210)
    torch_state = torch.random.get_rng_state().clone()
    python_state = random.getstate()

    first = make_relation_grouped_suffix_plan(
        transitions,
        max_depth=4,
        heldout_fraction=0.35,
        seed=31,
    )
    second = make_relation_grouped_suffix_plan(
        transitions.clone(),
        max_depth=4,
        heldout_fraction=0.35,
        seed=31,
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert torch.equal(torch_state, torch.random.get_rng_state())
    assert python_state == random.getstate()
    assert set(first.construction).isdisjoint(first.heldout)
    assert set(first.construction_group_signatures).isdisjoint(first.heldout_group_signatures)


def test_all_d4_identity_relations_are_kept_with_empty_construction_word() -> None:
    transitions = torch.from_numpy(canonical_maps("d4")).long()
    plan = make_relation_grouped_suffix_plan(
        transitions,
        max_depth=4,
        heldout_fraction=0.40,
        seed=7,
    )
    identity_words = ((), (0, 0, 0, 0), (1, 1), (1, 0, 1, 0))
    assert all(word in plan.construction for word in identity_words)
    assert len(set(relation_groups(plan, identity_words))) == 1

    side_by_group: dict[tuple[int, ...], set[str]] = {}
    for side, words in (("construction", plan.construction), ("heldout", plan.heldout)):
        for signature in relation_groups(plan, words):
            side_by_group.setdefault(signature, set()).add(side)
    assert all(len(sides) == 1 for sides in side_by_group.values())


def test_manual_plan_rejects_relation_equivalent_audit_leakage() -> None:
    with pytest.raises(ValueError, match="relation-group leakage"):
        RelationGroupedSuffixPlan(
            canonical_transitions=_transition_tuple(),
            construction=((),),
            heldout=((0, 0, 0),),
            seed=0,
            heldout_fraction=0.5,
        )


def test_metric_packet_margin_is_positive_and_invariant_to_hidden_scale() -> None:
    plan = _manual_plan()
    operators, decoder, metric, maps, canonical_to_slot = _system(batch=2)
    hidden = torch.tensor([[1.0, 0.0, 0.0], [13.0, 0.0, 0.0]], dtype=torch.float64)
    sources = torch.zeros(2, dtype=torch.long)

    result = construction_packet_margin_loss(
        hidden,
        operators,
        decoder,
        metric,
        maps,
        canonical_to_slot,
        sources,
        plan,
        required_margin=0.1,
        temperature=0.05,
        reduction="none",
    )

    assert result.loss.shape == (2,)
    assert torch.equal(result.per_example_loss[0], result.per_example_loss[1])
    assert torch.equal(
        result.evaluation.suffix_minimum_margin[0],
        result.evaluation.suffix_minimum_margin[1],
    )
    assert bool((result.evaluation.minimum_margin > 0).all())
    assert result.evaluation.target_states.tolist() == [[0, 1], [0, 1]]


def test_packet_loss_is_differentiable_through_state_operator_decoder_and_metric() -> None:
    plan = _manual_plan()
    operators, decoder, metric, maps, canonical_to_slot = _system(batch=1)
    hidden = torch.tensor([[0.2, 1.0, 0.1]], dtype=torch.float64, requires_grad=True)
    operators.requires_grad_()
    decoder.requires_grad_()
    metric.requires_grad_()
    sources = torch.zeros(1, dtype=torch.long)

    result = construction_packet_margin_loss(
        hidden,
        operators,
        decoder,
        metric,
        maps,
        canonical_to_slot,
        sources,
        plan,
        required_margin=0.25,
        temperature=0.08,
    )
    result.loss.backward()

    for tensor in (hidden, operators, decoder, metric):
        assert tensor.grad is not None
        assert bool(torch.isfinite(tensor.grad).all())
    assert float(hidden.grad.norm()) > 0.0
    assert float(operators.grad[:, 0].norm()) > 0.0

    improved_hidden = (hidden.detach() - 0.05 * hidden.grad).requires_grad_(False)
    improved = construction_packet_margin_loss(
        improved_hidden,
        operators.detach(),
        decoder.detach(),
        metric.detach(),
        maps,
        canonical_to_slot,
        sources,
        plan,
        required_margin=0.25,
        temperature=0.08,
    )
    assert float(improved.loss) < float(result.loss.detach())


def test_heldout_suffix_is_absent_from_training_graph_and_audit_is_detached() -> None:
    plan = _manual_plan()
    operators, decoder, metric, maps, canonical_to_slot = _system(batch=1)
    operators.requires_grad_()
    hidden = torch.tensor([[0.7, 0.2, 0.1]], dtype=torch.float64, requires_grad=True)
    sources = torch.zeros(1, dtype=torch.long)

    training = construction_packet_margin_loss(
        hidden,
        operators,
        decoder,
        metric,
        maps,
        canonical_to_slot,
        sources,
        plan,
    )
    training.loss.backward()

    # Only action 0 occurs in construction. Action 1 occurs exclusively in the
    # held-out word, so an exact zero gradient is a direct leakage test.
    assert float(operators.grad[:, 0].abs().sum()) > 0.0
    assert torch.equal(operators.grad[:, 1], torch.zeros_like(operators.grad[:, 1]))
    gradient_before_audit = operators.grad.clone()

    audit = audit_heldout_packet(
        hidden,
        operators,
        decoder,
        metric,
        maps,
        canonical_to_slot,
        sources,
        plan,
    )
    assert audit.evaluation.suffixes == plan.heldout
    assert not audit.evaluation.class_margins.requires_grad
    assert not audit.inside.requires_grad
    assert torch.equal(operators.grad, gradient_before_audit)


def test_cpu_loss_and_gradients_are_bitwise_deterministic() -> None:
    plan = _manual_plan()
    base_operators, base_decoder, metric, maps, canonical_to_slot = _system(batch=2)
    base_hidden = torch.tensor(
        [[0.7, 0.2, 0.1], [0.1, 0.8, 0.3]],
        dtype=torch.float64,
    )
    sources = torch.tensor([0, 1], dtype=torch.long)

    outputs: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]] = []
    for _ in range(2):
        hidden = base_hidden.clone().requires_grad_()
        operators = base_operators.clone().requires_grad_()
        decoder = base_decoder.clone().requires_grad_()
        result = construction_packet_margin_loss(
            hidden,
            operators,
            decoder,
            metric,
            maps,
            canonical_to_slot,
            sources,
            plan,
            required_margin=0.2,
            temperature=0.07,
        )
        result.loss.backward()
        outputs.append(
            (
                result.loss.detach().clone(),
                hidden.grad.clone(),
                operators.grad.clone(),
                decoder.grad.clone(),
            )
        )

    assert all(torch.equal(left, right) for left, right in zip(outputs[0], outputs[1], strict=True))


def test_slot_permutation_preserves_targets_and_margins() -> None:
    plan = _manual_plan()
    operators, decoder, metric, maps, canonical_to_slot = _system(batch=1)
    hidden = torch.tensor([[1.0, 0.0, 0.0]], dtype=torch.float64)
    sources = torch.zeros(1, dtype=torch.long)
    baseline = construction_packet_margin_loss(
        hidden,
        operators,
        decoder,
        metric,
        maps,
        canonical_to_slot,
        sources,
        plan,
    )

    swapped_operators = operators[:, [1, 0]]
    swapped_maps = maps[:, [1, 0]]
    swapped_slots = torch.tensor([[1, 0]], dtype=torch.long)
    swapped = construction_packet_margin_loss(
        hidden,
        swapped_operators,
        decoder,
        metric,
        swapped_maps,
        swapped_slots,
        sources,
        plan,
    )
    assert torch.equal(baseline.loss, swapped.loss)
    assert torch.equal(baseline.evaluation.target_states, swapped.evaluation.target_states)
    assert torch.equal(baseline.evaluation.class_margins, swapped.evaluation.class_margins)


def test_invalid_metric_and_invalid_slot_map_fail_closed() -> None:
    plan = _manual_plan()
    operators, decoder, metric, maps, canonical_to_slot = _system(batch=1)
    hidden = torch.tensor([[1.0, 0.0, 0.0]], dtype=torch.float64)
    sources = torch.zeros(1, dtype=torch.long)

    non_spd = metric.clone()
    non_spd[2, 2] = -1.0
    with pytest.raises(ValueError, match="positive definite"):
        construction_packet_margin_loss(
            hidden,
            operators,
            decoder,
            non_spd,
            maps,
            canonical_to_slot,
            sources,
            plan,
        )

    with pytest.raises(ValueError, match="permutation"):
        construction_packet_margin_loss(
            hidden,
            operators,
            decoder,
            metric,
            maps,
            torch.zeros_like(canonical_to_slot),
            sources,
            plan,
        )


def test_degenerate_decoder_contrast_is_flagged_with_finite_gradient() -> None:
    plan = _manual_plan()
    operators, decoder, metric, maps, canonical_to_slot = _system(batch=1)
    decoder = decoder.clone()
    decoder[1] = decoder[0]
    decoder.requires_grad_()
    hidden = torch.tensor([[0.8, 0.1, 0.1]], dtype=torch.float64, requires_grad=True)
    sources = torch.zeros(1, dtype=torch.long)

    result = construction_packet_margin_loss(
        hidden,
        operators,
        decoder,
        metric,
        maps,
        canonical_to_slot,
        sources,
        plan,
    )
    assert bool(result.evaluation.degenerate_decoder_contrasts.any())
    result.loss.backward()
    assert bool(torch.isfinite(decoder.grad).all())
    assert bool(torch.isfinite(hidden.grad).all())


def test_numpy_transition_source_produces_same_plan_after_tensor_conversion() -> None:
    maps = canonical_maps("d4")
    plan_64 = make_relation_grouped_suffix_plan(torch.from_numpy(maps), max_depth=3, seed=5)
    plan_32 = make_relation_grouped_suffix_plan(torch.from_numpy(maps.astype(np.int32)), max_depth=3, seed=5)
    assert plan_64 == plan_32

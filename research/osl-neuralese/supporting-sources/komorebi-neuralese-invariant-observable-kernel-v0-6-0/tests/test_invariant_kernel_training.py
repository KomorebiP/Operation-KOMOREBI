import json
import math
from dataclasses import replace

import numpy as np
import pytest
import torch

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.flatness_training import relation_cell_bank
from komorebi_neuralese.invariant_kernel_models import (
    LearnedFrameBlockIsometricOperatorRNN,
)
from komorebi_neuralese.invariant_kernel_training import (
    INVARIANT_KERNEL_ARMS,
    PRIMARY_INVARIANT_KERNEL_ARMS,
    InvariantKernelTrainConfig,
    LearnedIntertwinerPolarRNN,
    LinearPolarTableOperatorRNN,
    auxiliary_schedule_multiplier,
    build_relation_context_plan,
    build_invariant_kernel_model,
    compute_invariant_kernel_losses,
    invariant_kernel_checkpoint_metadata,
    invariant_kernel_training_contract,
    learned_intertwiner_losses,
    mean_relation_product_loss,
    regular_simplex_chart,
    train_invariant_kernel_arm,
    train_paired_invariant_kernel_panel,
)
from komorebi_neuralese.packet_closure_train import (
    make_v04_construction_bank,
    sample_v04_terminal_batch,
    state_dict_digest,
)
from komorebi_neuralese.packet_models import PolarIsometricTableOperatorRNN


def _tiny_config(seed: int = 211) -> InvariantKernelTrainConfig:
    return InvariantKernelTrainConfig(
        seed=seed,
        steps=1,
        batch_size=8,
        warmup_steps=1,
        auxiliary_delay_steps=0,
        auxiliary_ramp_end_step=1,
        checkpoints=1,
    )


def test_six_arm_registry_is_frozen_and_mechanisms_are_isolated():
    assert PRIMARY_INVARIANT_KERNEL_ARMS == (
        "polar_supervised",
        "polar_cr",
        "polar_exact",
        "learned_intertwiner",
        "hard_kernel_supervised",
        "hard_kernel_semantic_flat",
    )
    assert tuple(INVARIANT_KERNEL_ARMS) == PRIMARY_INVARIANT_KERNEL_ARMS
    assert INVARIANT_KERNEL_ARMS["polar_cr"].legacy_cr
    assert INVARIANT_KERNEL_ARMS["polar_exact"].exact_flatness
    assert INVARIANT_KERNEL_ARMS["learned_intertwiner"].learned_intertwiner
    assert INVARIANT_KERNEL_ARMS["hard_kernel_semantic_flat"].semantic_flatness


def test_regular_simplex_chart_is_rank_seven_centered_helmert_frame():
    chart = regular_simplex_chart(dtype=torch.float64)
    centering = torch.eye(8, dtype=torch.float64) - torch.ones(8, 8) / 8
    assert chart.shape == (7, 8)
    assert torch.linalg.matrix_rank(chart).item() == 7
    assert torch.allclose(chart @ chart.T, torch.eye(7, dtype=torch.float64), atol=1e-12)
    assert torch.allclose(chart.T @ chart, centering, atol=1e-12)
    assert torch.allclose(chart.sum(dim=1), torch.zeros(7, dtype=torch.float64), atol=1e-12)


def test_learned_intertwiner_is_row_orthonormal_and_does_not_construct_model():
    config = _tiny_config()
    model = build_invariant_kernel_model(config, "learned_intertwiner")
    assert isinstance(model, LearnedIntertwinerPolarRNN)
    batch = EpisodeGenerator(701).sample(3, 3, family="d4")
    with torch.no_grad():
        codes_before = model.encode_operators(batch.tables).clone()
        logits_before = model(batch.tables, batch.op_slots, batch.start).clone()
        model.observer_raw.normal_(mean=0.0, std=1.0)
        codes_after = model.encode_operators(batch.tables)
        logits_after = model(batch.tables, batch.op_slots, batch.start)
        observer = model.observer_matrix()
    assert observer.shape == (7, 12)
    assert torch.allclose(observer @ observer.T, torch.eye(7), atol=2e-6)
    assert torch.equal(codes_before, codes_after)
    assert torch.equal(logits_before, logits_after)
    parameter_names = {name for name, _ in model.named_parameters()}
    assert "observer_raw" in parameter_names
    assert not any("semantic_operator_head" in name for name in parameter_names)
    assert not any("centered_readout_head" in name for name in parameter_names)


def test_learned_observer_starts_on_instantaneous_centered_readout_row_space():
    torch.manual_seed(707)
    model = LearnedIntertwinerPolarRNN()
    observer = model.observer_matrix()
    projector = observer.T @ observer
    kernel = torch.eye(12) - projector
    centered = model.centered_decoder()
    relative_residual = torch.linalg.matrix_norm(
        centered @ kernel, ord="fro"
    ) / torch.linalg.matrix_norm(centered, ord="fro")
    assert relative_residual.item() < 2e-6
    assert torch.allclose(observer @ observer.T, torch.eye(7), atol=2e-6)
    assert "_registered_anchor_coordinates" not in model.state_dict()


def test_linear_polar_rollout_matches_legacy_on_natural_isometric_trajectories():
    torch.manual_seed(719)
    legacy = PolarIsometricTableOperatorRNN()
    torch.manual_seed(719)
    linear = LinearPolarTableOperatorRNN()
    assert state_dict_digest(legacy) == state_dict_digest(linear)
    batch = EpisodeGenerator(720).sample(16, 8, family="d4")
    legacy_trace = legacy.run(batch.tables, batch.op_slots, batch.start)
    linear_trace = linear.run(batch.tables, batch.op_slots, batch.start)
    assert torch.equal(legacy_trace.operator_codes, linear_trace.operator_codes)
    assert len(legacy_trace.hidden) == len(linear_trace.hidden)
    for legacy_hidden, linear_hidden in zip(legacy_trace.hidden, linear_trace.hidden):
        assert torch.allclose(legacy_hidden, linear_hidden, atol=3e-6, rtol=3e-6)
    assert torch.allclose(legacy_trace.logits, linear_trace.logits, atol=3e-6, rtol=3e-6)
    assert torch.allclose(
        legacy_trace.radial_norms,
        linear_trace.radial_norms,
        atol=3e-6,
        rtol=3e-6,
    )


def test_exact_invariant_Q_injection_is_centered_logit_invariant_in_real_rollout():
    """Catch hidden projective normalization that matrix-only audits bypass."""

    model = build_invariant_kernel_model(_tiny_config(), "learned_intertwiner")
    assert isinstance(model, LearnedIntertwinerPolarRNN)
    with torch.no_grad():
        # Register Pi as the first seven coordinates.
        model.observer_raw.zero_()
        model.observer_raw[:, :7].copy_(torch.eye(7))
        # Every visible permutation table has eight unit entries, so this
        # bias-free encoder emits I_12 for every table before polar retraction.
        model.operator_encoder.weight.zero_()
        for diagonal in range(12):
            model.operator_encoder.weight[diagonal * 12 + diagonal].fill_(1.0 / 8.0)
        model.state_embedding.weight.zero_()
        model.state_embedding.weight[0, 0] = 1.0
        model.decoder.weight.zero_()
        model.decoder.weight[:, :7].copy_(regular_simplex_chart().T)

    batch = EpisodeGenerator(711).sample(1, 5, family="d4")
    natural = model.run(batch.tables, batch.op_slots, torch.zeros(1, dtype=torch.long))
    codes = natural.operator_codes
    assert codes is not None
    identity = torch.eye(12).expand_as(codes)
    assert torch.allclose(codes, identity, atol=2e-6)
    assert torch.allclose(natural.hidden[-1], natural.hidden[0], atol=2e-6)

    base_hidden = natural.hidden[0]
    q_injection = torch.zeros_like(base_hidden)
    q_injection[:, 7] = 0.75
    q_projector = torch.eye(12) - model.observer_projector()
    assert torch.allclose(q_injection @ model.observer_matrix().T, torch.zeros(1, 7))
    assert torch.allclose(q_injection @ q_projector, q_injection, atol=2e-6)

    base = model.continue_from_hidden(base_hidden, codes, batch.op_slots)
    injected = model.continue_from_hidden(base_hidden + q_injection, codes, batch.op_slots)
    centering = torch.eye(8) - torch.ones(8, 8) / 8
    base_centered = base.logits @ centering
    injected_centered = injected.logits @ centering
    assert torch.allclose(base_centered, injected_centered, atol=2e-6)
    assert torch.allclose(injected.hidden[-1] - base.hidden[-1], q_injection, atol=2e-6)
    # Radial receipts observe the larger norm but do not feed it back into h.
    assert injected.radial_norms[0, -1] > base.radial_norms[0, -1]


def test_intertwiner_C_and_T_are_induced_and_losses_reach_observer_and_recurrence():
    config = _tiny_config()
    model = build_invariant_kernel_model(config, "learned_intertwiner")
    assert isinstance(model, LearnedIntertwinerPolarRNN)
    batch = EpisodeGenerator(702).sample(1, 2, family="d4")
    codes = model.encode_operators(batch.tables)[0]
    pairs = relation_cell_bank(batch.maps[0]).cells
    losses = learned_intertwiner_losses(model, codes.unsqueeze(0), (pairs,))
    observer = model.observer_matrix()
    induced_t = observer @ codes @ observer.T
    induced_c = model.centered_decoder() @ observer.T
    assert torch.equal(induced_t, model.induced_semantic_operators(codes))
    assert torch.equal(induced_c, model.induced_centered_readout())
    assert losses.observer_orthogonality.item() < 1e-12
    projector = observer.T @ observer
    kernel = torch.eye(12) - projector
    anchors = model.state_anchors().T
    observed_anchors = observer @ anchors
    centering = torch.eye(8) - torch.ones(8, 8) / 8
    manual_geometry = (
        (observed_anchors.T @ observed_anchors - centering).square().sum() / 7
    )
    centered_decoder = model.centered_decoder()
    manual_readout = (
        (centered_decoder @ kernel).square().sum()
        / (centered_decoder.square().sum().detach() + 1e-4)
    )
    manual_intertwining = (
        (observer.unsqueeze(0) @ codes @ kernel).square().sum(dim=(-2, -1))
        + (kernel @ codes @ observer.T.unsqueeze(0)).square().sum(dim=(-2, -1))
    ).mean() / 14
    assert torch.allclose(losses.anchor_geometry, manual_geometry)
    assert torch.allclose(losses.centered_readout, manual_readout, atol=1e-6)
    assert torch.allclose(losses.intertwining, manual_intertwining, atol=1e-6)
    total = (
        losses.anchor_geometry
        + losses.centered_readout
        + losses.intertwining
        + losses.semantic_relation
    )
    model.zero_grad(set_to_none=True)
    total.backward()
    assert model.observer_raw.grad is not None
    assert torch.isfinite(model.observer_raw.grad).all()
    assert model.observer_raw.grad.abs().sum().item() > 0.0
    assert model.operator_encoder.weight.grad is not None
    assert torch.isfinite(model.operator_encoder.weight.grad).all()
    assert model.operator_encoder.weight.grad.abs().sum().item() > 0.0


def test_anchor_geometry_is_invariant_to_observer_quotient_basis():
    torch.manual_seed(709)
    model = LearnedIntertwinerPolarRNN()
    batch = EpisodeGenerator(710).sample(1, 2, family="d4")
    codes = model.encode_operators(batch.tables)[0]
    pairs = relation_cell_bank(batch.maps[0]).cells
    original = learned_intertwiner_losses(
        model, codes.unsqueeze(0), (pairs,)
    ).anchor_geometry.detach()

    with torch.no_grad():
        observer = model.observer_matrix()
        rotation, _ = torch.linalg.qr(torch.randn(7, 7))
        model.observer_raw.copy_(rotation @ observer)

    rotated = learned_intertwiner_losses(
        model, codes.unsqueeze(0), (pairs,)
    ).anchor_geometry.detach()
    assert torch.allclose(original, rotated, atol=2e-6, rtol=2e-6)


def test_eight_context_intertwiner_losses_equal_manual_context_mean_and_reach_last_code():
    config = _tiny_config(seed=713)
    model = build_invariant_kernel_model(config, "learned_intertwiner")
    assert isinstance(model, LearnedIntertwinerPolarRNN)
    batch = sample_v04_terminal_batch(EpisodeGenerator(714), 8, 3).batch
    plan = build_relation_context_plan(batch, config.auxiliary_contexts)
    pairs_by_context = tuple(bank.cells for bank in plan.banks)
    codes = model.encode_operators(batch.tables[:8])
    codes.retain_grad()

    joint = learned_intertwiner_losses(model, codes, pairs_by_context)
    singles = [
        learned_intertwiner_losses(
            model,
            codes[index : index + 1],
            (pairs_by_context[index],),
        )
        for index in range(8)
    ]
    assert torch.allclose(
        joint.intertwining,
        torch.stack([loss.intertwining for loss in singles]).mean(),
        atol=1e-7,
        rtol=1e-6,
    )
    assert torch.allclose(
        joint.semantic_relation,
        torch.stack([loss.semantic_relation for loss in singles]).mean(),
        atol=1e-7,
        rtol=1e-6,
    )
    joint_context_loss = joint.intertwining + joint.semantic_relation
    model.zero_grad(set_to_none=True)
    joint_context_loss.backward()
    assert codes.grad is not None
    assert torch.isfinite(codes.grad).all()
    assert codes.grad[7].abs().sum().item() > 0.0


def test_multicontext_relation_loss_is_invariant_to_paired_prefix_permutation():
    config = _tiny_config(seed=715)
    model = build_invariant_kernel_model(config, "polar_exact")
    batch = sample_v04_terminal_batch(EpisodeGenerator(716), 8, 3).batch
    plan = build_relation_context_plan(batch, 8)
    pairs = tuple(bank.cells for bank in plan.banks)
    codes = model.encode_operators(batch.tables)
    original = mean_relation_product_loss(codes, pairs)

    permutation = torch.tensor([7, 2, 5, 0, 6, 1, 4, 3])
    permuted_maps = batch.maps.index_select(0, permutation)
    permuted_tables = batch.tables.index_select(0, permutation)
    permuted_batch = replace(
        batch,
        maps=permuted_maps,
        tables=permuted_tables,
    )
    permuted_plan = build_relation_context_plan(permuted_batch, 8)
    permuted_pairs = tuple(bank.cells for bank in permuted_plan.banks)
    permuted_codes = model.encode_operators(permuted_tables)
    observed = mean_relation_product_loss(permuted_codes, permuted_pairs)
    assert torch.allclose(original, observed, atol=1e-7, rtol=1e-6)


def test_ninth_context_is_outside_the_registered_auxiliary_prefix():
    config = replace(_tiny_config(seed=717), batch_size=9)
    model = build_invariant_kernel_model(config, "polar_exact")
    batch = sample_v04_terminal_batch(EpisodeGenerator(718), 9, 3).batch
    donor = sample_v04_terminal_batch(EpisodeGenerator(719), 9, 3).batch
    changed_tables = batch.tables.clone()
    changed_maps = batch.maps.clone()
    changed_tables[8] = donor.tables[8]
    changed_maps[8] = donor.maps[8]
    changed = replace(batch, tables=changed_tables, maps=changed_maps)
    construction = make_v04_construction_bank(4)
    original = compute_invariant_kernel_losses(
        model, batch, construction, "polar_exact", config, step=0
    )
    modified = compute_invariant_kernel_losses(
        model, changed, construction, "polar_exact", config, step=0
    )
    assert torch.equal(original.exact_flatness, modified.exact_flatness)
    assert original.relation_context_indices == tuple(range(8))
    assert modified.relation_context_indices == tuple(range(8))


def test_every_selected_context_uses_its_own_visible_relation_bank():
    batch = sample_v04_terminal_batch(EpisodeGenerator(720), 8, 3).batch
    plan = build_relation_context_plan(batch, 8)
    expected = tuple(relation_cell_bank(batch.maps[index]) for index in range(8))
    assert plan.indices == tuple(range(8))
    assert tuple(bank.fingerprint for bank in plan.banks) == tuple(
        bank.fingerprint for bank in expected
    )
    assert tuple(bank.cells for bank in plan.banks) == tuple(
        bank.cells for bank in expected
    )
    assert len({bank.cells for bank in plan.banks}) > 1


def test_hard_kernel_uses_7_plus_1_plus_4_and_frozen_dormant_ambient_encoder():
    config = _tiny_config()
    supervised = build_invariant_kernel_model(config, "hard_kernel_supervised")
    semantic = build_invariant_kernel_model(config, "hard_kernel_semantic_flat")
    assert isinstance(supervised, LearnedFrameBlockIsometricOperatorRNN)
    assert isinstance(semantic, LearnedFrameBlockIsometricOperatorRNN)
    assert state_dict_digest(supervised) == state_dict_digest(semantic)
    assert supervised.semantic_dim == 7
    assert supervised.common_logit_dim == 1
    assert supervised.ambient_dim == 4
    assert not supervised.ambient_operator_encoder.weight.requires_grad

    batch = EpisodeGenerator(703).sample(2, 2, family="d4")
    bundle = supervised.encode_operator_bundle(batch.tables)
    assert bundle.semantic_blocks.shape[-2:] == (7, 7)
    assert bundle.common_blocks.shape[-2:] == (1, 1)
    assert bundle.ambient_blocks.shape[-2:] == (4, 4)
    with torch.no_grad():
        supervised.semantic_state_embedding.weight.copy_(regular_simplex_chart().T)
        anchors = supervised.state_anchors()
    assert torch.allclose(anchors @ anchors.T, torch.eye(8), atol=2e-6)
    assert torch.linalg.matrix_rank(anchors).item() == 8
    assert torch.allclose(
        anchors @ supervised.ambient_frame().to(dtype=anchors.dtype),
        torch.zeros(8, 4),
        atol=2e-6,
    )
    expected_common = torch.full((8, 1), 1.0 / math.sqrt(8))
    assert torch.allclose(
        anchors @ supervised.common_logit_frame().to(dtype=anchors.dtype),
        expected_common,
        atol=2e-6,
    )
    before = supervised.ambient_operator_encoder.weight.detach().clone()
    construction = make_v04_construction_bank(4)
    losses = compute_invariant_kernel_losses(
        supervised,
        sample_v04_terminal_batch(EpisodeGenerator(704), 8, 2).batch,
        construction,
        "hard_kernel_supervised",
        config,
        step=0,
    )
    losses.total.backward()
    assert supervised.ambient_operator_encoder.weight.grad is None
    assert torch.equal(before, supervised.ambient_operator_encoder.weight)


def test_auxiliary_schedule_boundaries_are_frozen_and_independent_of_base_warmup():
    defaults = InvariantKernelTrainConfig(seed=211, steps=1, batch_size=8)
    assert defaults.auxiliary_contexts == 8
    assert defaults.base_config().auxiliary_contexts == 8
    assert defaults.auxiliary_delay_steps == 800
    assert defaults.auxiliary_ramp_end_step == 1600
    assert auxiliary_schedule_multiplier(0, 800, 1600) == 0.0
    assert auxiliary_schedule_multiplier(798, 800, 1600) == 0.0
    assert auxiliary_schedule_multiplier(799, 800, 1600) == 0.0
    assert math.isclose(auxiliary_schedule_multiplier(800, 800, 1600), 1.0 / 800.0)
    assert math.isclose(auxiliary_schedule_multiplier(1598, 800, 1600), 799.0 / 800.0)
    assert auxiliary_schedule_multiplier(1599, 800, 1600) == 1.0
    assert auxiliary_schedule_multiplier(2000, 800, 1600) == 1.0


@pytest.mark.parametrize(
    ("delay", "ramp", "message"),
    [
        (-1, 800, "nonnegative"),
        (400, 400, "greater"),
        (401, 400, "greater"),
    ],
)
def test_invalid_auxiliary_schedules_fail_closed(delay, ramp, message):
    config = InvariantKernelTrainConfig(
        seed=211,
        steps=1,
        batch_size=8,
        auxiliary_delay_steps=delay,
        auxiliary_ramp_end_step=ramp,
    )
    with pytest.raises(ValueError, match=message):
        config.validate()


def test_registered_auxiliary_context_count_cannot_be_silently_truncated():
    config = InvariantKernelTrainConfig(seed=211, steps=1, batch_size=7)
    with pytest.raises(ValueError, match="cannot exceed batch_size"):
        config.validate()

    batch = EpisodeGenerator(706).sample(7, 2, family="d4")
    with pytest.raises(ValueError, match="exceeds batch rows"):
        build_relation_context_plan(batch, 8)


def test_all_auxiliaries_use_staged_multiplier_and_relation_bank_is_complete():
    config = InvariantKernelTrainConfig(
        seed=211,
        steps=1,
        batch_size=8,
        warmup_steps=10,
        auxiliary_delay_steps=0,
        auxiliary_ramp_end_step=10,
        checkpoints=1,
    )
    model = build_invariant_kernel_model(config, "learned_intertwiner")
    batch = sample_v04_terminal_batch(EpisodeGenerator(705), 8, 3).batch
    losses = compute_invariant_kernel_losses(
        model,
        batch,
        make_v04_construction_bank(4),
        "learned_intertwiner",
        config,
        step=0,
    )
    assert math.isclose(losses.base.warmup, 0.1)
    assert math.isclose(losses.auxiliary_multiplier, 0.1)
    assert losses.auxiliary_delay_steps == 0
    assert losses.auxiliary_ramp_end_step == 10
    assert losses.relation_context_indices == tuple(range(8))
    assert losses.relation_cell_indices == tuple(range(9))
    assert losses.relation_cells_per_context == 9
    assert losses.relation_cells_total == 72
    weighted_auxiliary = (
        config.weights.observer_anchor_geometry * losses.observer_anchor_geometry
        + config.weights.observer_centered_readout * losses.observer_centered_readout
        + config.weights.observer_intertwining * losses.observer_intertwining
        + config.weights.observer_semantic_relation * losses.observer_semantic_relation
    )
    expected = losses.base.total + losses.auxiliary_multiplier * weighted_auxiliary
    assert torch.allclose(losses.total, expected)


def test_one_step_panel_is_paired_within_architecture_and_across_streams():
    torch.set_num_threads(1)
    panel = train_paired_invariant_kernel_panel(_tiny_config())
    assert tuple(panel) == PRIMARY_INVARIANT_KERNEL_ARMS
    for attribute in (
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
        "terminal_proposal_count",
        "terminal_candidates_accepted",
        "terminal_candidates_rejected",
        "terminal_identity_rejections",
        "terminal_r2_rejections",
        "construction_digest",
        "construction_words",
    ):
        assert len({getattr(result, attribute) for result in panel.values()}) == 1
    polar = [panel[name] for name in PRIMARY_INVARIANT_KERNEL_ARMS[:4]]
    hard = [panel[name] for name in PRIMARY_INVARIANT_KERNEL_ARMS[4:]]
    assert len({result.core_initial_state_digest for result in polar}) == 1
    assert len({result.initial_state_digest for result in hard}) == 1
    assert all(np.isfinite(result.final_loss) for result in panel.values())
    assert all(result.config.auxiliary_contexts == 8 for result in panel.values())
    assert all(
        result.config.base_config().auxiliary_contexts == 8
        for result in panel.values()
    )
    assert all(result.ambient_initial_digest is None for result in polar)
    assert all(
        result.ambient_initial_digest == result.ambient_final_digest
        and result.ambient_initial_digest is not None
        for result in hard
    )
    schedule_row = panel["learned_intertwiner"].trajectory[0]
    assert schedule_row["base_warmup"] == 1.0
    assert schedule_row["auxiliary_multiplier"] == 1.0
    assert schedule_row["auxiliary_delay_steps"] == 0
    assert schedule_row["auxiliary_ramp_end_step"] == 1
    assert schedule_row["relation_context_indices"] == list(range(8))
    assert schedule_row["relation_cells_per_context"] == 9
    assert schedule_row["relation_cells_total"] == 72


def test_checkpoint_metadata_is_training_only_and_marks_explicit_pressure():
    result = train_paired_invariant_kernel_panel(
        _tiny_config(),
        arm_names=("learned_intertwiner",),
    )["learned_intertwiner"]
    metadata = invariant_kernel_checkpoint_metadata(result)
    encoded = json.dumps(metadata, sort_keys=True, allow_nan=False)
    assert "heldout" not in encoded.lower()
    assert metadata["claim_boundary"] == {
        "explicit_pressure_only": True,
        "spontaneous_emergence": False,
        "anchor_geometry_is_supervised": True,
        "observer_constructs_recurrence": False,
        "learned_intertwiner_projective_normalization": False,
        "ambient_fiber_is_useful_memory": False,
    }
    contract = invariant_kernel_training_contract(result.config)
    assert contract["learned_intertwiner"]["observer_rank"] == 7
    assert contract["learned_intertwiner"]["centered_null_rank"] == 5
    assert "centered-readout rowspace only" in contract["learned_intertwiner"][
        "observer_initialization"
    ]
    assert "anchor_geometry" in contract["learned_intertwiner"]["loss_normalization"]
    assert contract["hard_kernel"]["split"] == [7, 1, 4]
    assert metadata["auxiliary_schedule"]["delay_steps"] == 0
    assert metadata["auxiliary_schedule"]["ramp_end_step"] == 1
    assert metadata["relation_exposure"] == {
        "selection": "first_n_accepted_rows_without_replacement",
        "contexts_per_step": 8,
        "cells_per_context": 9,
        "cells_per_step_total": 72,
        "aggregation": "mean_over_contexts_and_cells_not_sum",
        "shared_across_arms": True,
    }
    assert contract["relation_exposure"] == metadata["relation_exposure"]
    assert contract["auxiliary_schedule"]["base_warmup_is_independent"]
    assert "explicit" in contract["claim_boundary"]


def test_repeated_training_is_byte_deterministic_excluding_elapsed_time():
    config = _tiny_config(seed=223)
    first = train_invariant_kernel_arm("learned_intertwiner", config)
    second = train_invariant_kernel_arm("learned_intertwiner", config)
    assert first.initial_state_digest == second.initial_state_digest
    assert first.core_initial_state_digest == second.core_initial_state_digest
    assert first.final_state_digest == second.final_state_digest
    assert first.episode_stream_digest == second.episode_stream_digest
    assert first.terminal_proposal_stream_digest == second.terminal_proposal_stream_digest
    assert first.relation_schedule_digest == second.relation_schedule_digest
    assert first.trajectory == second.trajectory


@pytest.mark.parametrize("bad_rank", [6, 8])
def test_observer_rank_is_not_tunable_posthoc(bad_rank):
    with pytest.raises(ValueError, match="observer_dim"):
        LearnedIntertwinerPolarRNN(observer_dim=bad_rank)

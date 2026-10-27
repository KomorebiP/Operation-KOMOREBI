import math

import numpy as np
import torch

from komorebi_neuralese.algebra import canonical_maps
from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.flatness_eval import (
    ExactCompiledPolarRNN,
    QuotientCurvedPolarOracle,
)
from komorebi_neuralese.flatness_training import (
    PACKET_DELAY_STEPS,
    PACKET_DENOMINATOR_FLOOR,
    PACKET_HOLONOMY_POWERS,
    PACKET_RAMP_END_STEP,
    FlatnessTrainConfig,
    _packet_ramp_multiplier,
    build_flatness_model,
    compute_flatness_losses,
    relation_cell_bank,
    relation_flatness_losses,
    train_paired_flatness_panel,
    word_signature,
)
from komorebi_neuralese.packet_closure_train import (
    make_v04_construction_bank,
    sample_v04_terminal_batch,
)


def test_relation_cell_bank_is_relation_complete_and_shuffled_is_false():
    maps = canonical_maps("d4")
    bank = relation_cell_bank(maps)
    assert len(bank.normal_forms) == 8
    assert len(bank.cells) == 9
    assert len(bank.shuffled_cells) == 9
    assert all(
        word_signature(maps, left) == word_signature(maps, right)
        for left, right in bank.cells
    )
    assert all(
        word_signature(maps, left) != word_signature(maps, right)
        for left, right in bank.shuffled_cells
    )
    assert sorted(right for _, right in bank.cells) == sorted(
        right for _, right in bank.shuffled_cells
    )


def test_cell_bank_is_conjugacy_invariant_but_slot_sensitive():
    batch = EpisodeGenerator(91).sample(4, 0, family="d4")
    for index in range(4):
        bank = relation_cell_bank(batch.maps[index])
        assert len(bank.cells) == 9
        assert all(
            word_signature(batch.maps[index], left)
            == word_signature(batch.maps[index], right)
            for left, right in bank.cells
        )


def test_exact_and_quotient_curved_oracles_separate_targets():
    batch = EpisodeGenerator(92).sample(1, 0, family="d4")
    pairs = relation_cell_bank(batch.maps[0]).cells
    probes = ((), (0,), (1,), (0, 1, 0, 1))
    exact_model = ExactCompiledPolarRNN()
    exact_codes = exact_model.encode_operator_bundle(batch.tables).matrices[0]
    exact_loss, packet_loss = relation_flatness_losses(
        exact_model, exact_codes, pairs, probes
    )
    assert float(exact_loss) <= 1e-12
    assert float(packet_loss) <= 1e-12

    curved_model = QuotientCurvedPolarOracle()
    curved_codes = curved_model.encode_operator_bundle(batch.tables).matrices[0]
    curved_exact, curved_packet = relation_flatness_losses(
        curved_model, curved_codes, pairs, probes
    )
    assert float(curved_exact) > 1e-3
    assert float(curved_packet) <= 1e-12


def test_v2_defaults_and_packet_ramp_are_frozen():
    config = FlatnessTrainConfig(seed=59, steps=1, batch_size=8)
    assert config.relation_cells_per_step == 9
    assert config.probes_per_step == 8
    assert config.exact_weight == 0.30
    assert config.packet_weight == 0.05
    assert PACKET_HOLONOMY_POWERS == (1, 2, 4, 8, 16)
    assert PACKET_DENOMINATOR_FLOOR == 1e-4
    assert _packet_ramp_multiplier(PACKET_DELAY_STEPS - 1) == 0.0
    assert math.isclose(
        _packet_ramp_multiplier(PACKET_DELAY_STEPS),
        1.0 / (PACKET_RAMP_END_STEP - PACKET_DELAY_STEPS),
    )
    assert _packet_ramp_multiplier(PACKET_RAMP_END_STEP - 1) == 1.0


def test_compute_uses_every_cell_and_every_bfs_suffix():
    config = FlatnessTrainConfig(seed=59, steps=1, batch_size=8)
    model = build_flatness_model(config, "polar_packet_flat")
    batch = sample_v04_terminal_batch(EpisodeGenerator(93), 8, 2).batch
    construction = make_v04_construction_bank(config.base_config().auxiliary_max_depth)
    losses = compute_flatness_losses(
        model,
        batch,
        construction,
        "polar_packet_flat",
        config,
        step=PACKET_DELAY_STEPS,
    )
    assert losses.cell_indices == tuple(range(9))
    assert losses.probe_indices == tuple(range(8))
    assert math.isclose(
        losses.packet_ramp,
        1.0 / (PACKET_RAMP_END_STEP - PACKET_DELAY_STEPS),
    )


def test_packet_observer_is_frozen_but_holonomy_receives_gradient():
    config = FlatnessTrainConfig(seed=59, steps=1, batch_size=8)
    model = build_flatness_model(config, "polar_packet_flat")
    batch = EpisodeGenerator(94).sample(1, 0, family="d4")
    bank = relation_cell_bank(batch.maps[0])
    codes = model.encode_operator_bundle(batch.tables).matrices[0]
    _, packet = relation_flatness_losses(
        model,
        codes,
        bank.cells,
        bank.normal_forms,
    )
    model.zero_grad(set_to_none=True)
    packet.backward()
    assert model.state_embedding.weight.grad is None
    assert model.decoder.weight.grad is None
    encoder_gradient = model.operator_encoder.weight.grad
    assert encoder_gradient is not None
    assert bool(torch.isfinite(encoder_gradient).all())
    assert float(encoder_gradient.abs().sum()) > 0.0


def test_multiscale_packet_loss_exposes_repeated_small_rotation():
    config = FlatnessTrainConfig(seed=59, steps=1, batch_size=8)
    model = build_flatness_model(config, "polar_packet_flat")
    with torch.no_grad():
        model.state_embedding.weight.zero_()
        model.state_embedding.weight[:, :8].copy_(torch.eye(8))
        model.decoder.weight.zero_()
        model.decoder.weight[:, :8].copy_(torch.eye(8))
    identity = torch.eye(12)
    rotation = identity.clone()
    angle = 0.02
    rotation[0, 0] = math.cos(angle)
    rotation[0, 1] = -math.sin(angle)
    rotation[1, 0] = math.sin(angle)
    rotation[1, 1] = math.cos(angle)
    codes = torch.stack((identity, rotation))
    pair = (((1,), ()),)
    _, single = relation_flatness_losses(
        model,
        codes,
        pair,
        ((),),
        powers=(1,),
    )
    _, multiscale = relation_flatness_losses(
        model,
        codes,
        pair,
        ((),),
    )
    assert float(single) > 0.0
    assert float(multiscale) > float(single) * 10.0


def test_one_step_panel_is_paired_and_finite():
    torch.set_num_threads(1)
    config = FlatnessTrainConfig(
        seed=59,
        steps=1,
        batch_size=8,
        warmup_steps=1,
        checkpoints=1,
    )
    panel = train_paired_flatness_panel(config)
    assert len({row.initial_state_digest for row in panel.values()}) == 1
    assert len({row.episode_stream_digest for row in panel.values()}) == 1
    assert len({row.terminal_proposal_stream_digest for row in panel.values()}) == 1
    assert all(np.isfinite(row.final_loss) for row in panel.values())
    positive = {
        row.relation_schedule_digest
        for row in panel.values()
        if not row.arm.shuffled_equivalence
    }
    shuffled = panel["polar_shuffled_packet"].relation_schedule_digest
    assert len(positive) == 1
    assert shuffled not in positive

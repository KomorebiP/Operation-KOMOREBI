from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import N_STATES
from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.invariant_kernel_models import (
    AMBIENT_DIM,
    CENTERED_NULL_DIM,
    COMMON_LOGIT_DIM,
    HIDDEN_DIM,
    OBSERVABLE_DIM,
    SEMANTIC_DIM,
    ExactInvariantKernelOperatorRNN,
    LearnedFrameBlockIsometricOperatorRNN,
    QuotientCurvedInvariantKernelOperatorRNN,
)
from komorebi_neuralese.models import RecurrentOperatorModel


def _learned(seed: int = 11, gauge_seed: int = 607) -> LearnedFrameBlockIsometricOperatorRNN:
    torch.manual_seed(seed)
    return LearnedFrameBlockIsometricOperatorRNN(gauge_seed=gauge_seed)


def test_fixed_gauge_is_deterministic_persistent_and_not_trainable() -> None:
    torch.manual_seed(1)
    before = torch.random.get_rng_state().clone()
    first = LearnedFrameBlockIsometricOperatorRNN(gauge_seed=19)
    # Model parameter initialization consumes the global RNG, but construction
    # of W itself uses a local generator.  Replaying the parameter draws with a
    # different gauge seed must therefore leave the global state identical.
    after_first = torch.random.get_rng_state().clone()
    torch.random.set_rng_state(before)
    second = LearnedFrameBlockIsometricOperatorRNN(gauge_seed=23)
    after_second = torch.random.get_rng_state().clone()

    third = LearnedFrameBlockIsometricOperatorRNN(gauge_seed=19)
    parameter_names = dict(first.named_parameters())

    assert torch.equal(after_first, after_second)
    assert torch.equal(first.gauge_matrix(), third.gauge_matrix())
    assert not torch.equal(first.gauge_matrix(), second.gauge_matrix())
    assert "_gauge" in first.state_dict()
    assert "_gauge" not in parameter_names
    assert first.gauge_matrix().shape == (HIDDEN_DIM, HIDDEN_DIM)
    assert torch.allclose(
        first.gauge_matrix().T @ first.gauge_matrix(),
        torch.eye(HIDDEN_DIM, dtype=first.gauge_matrix().dtype),
        atol=2e-12,
        rtol=2e-12,
    )
    assert float(torch.linalg.det(first.gauge_matrix())) > 0.0


def test_public_frames_and_projectors_form_an_exact_seven_plus_one_plus_four_split() -> None:
    model = _learned()
    identity = torch.eye(HIDDEN_DIM, dtype=model.gauge_matrix().dtype)

    assert SEMANTIC_DIM == OBSERVABLE_DIM == 7
    assert COMMON_LOGIT_DIM == 1
    assert AMBIENT_DIM == 4
    assert CENTERED_NULL_DIM == 5
    assert model.S.shape == (HIDDEN_DIM, OBSERVABLE_DIM)
    assert model.L.shape == (HIDDEN_DIM, COMMON_LOGIT_DIM)
    assert model.K.shape == (HIDDEN_DIM, AMBIENT_DIM)
    assert model.U.shape == (HIDDEN_DIM, OBSERVABLE_DIM)
    assert model.V.shape == (HIDDEN_DIM, AMBIENT_DIM)
    assert torch.equal(model.semantic_frame(), model.U)
    assert torch.equal(model.ambient_frame(), model.V)
    assert torch.allclose(
        model.S.T @ model.K,
        torch.zeros(OBSERVABLE_DIM, AMBIENT_DIM, dtype=model.S.dtype),
        atol=2e-12,
    )
    assert torch.allclose(model.P @ model.P, model.P, atol=2e-6, rtol=2e-6)
    assert torch.allclose(model.Q @ model.Q, model.Q, atol=2e-6, rtol=2e-6)
    assert torch.allclose(model.P + model.Q, identity, atol=2e-6, rtol=2e-6)
    assert torch.allclose(torch.trace(model.P_S), torch.tensor(7.0, dtype=model.P_S.dtype))
    assert torch.allclose(torch.trace(model.P_L), torch.tensor(1.0, dtype=model.P_L.dtype))
    assert torch.allclose(torch.trace(model.P_K), torch.tensor(4.0, dtype=model.P_K.dtype))
    assert torch.allclose(torch.trace(model.Q), torch.tensor(5.0, dtype=model.Q.dtype))


def test_embeddings_decoder_and_operators_obey_the_kernel_contract() -> None:
    model = _learned(13)
    batch = EpisodeGenerator(17).sample(23, 4, family="random")
    bundle = model.encode_operator_bundle(batch.tables)
    audit = model.audit_invariant_kernel(bundle.matrices)

    assert bundle.matrices.shape == (23, 2, HIDDEN_DIM, HIDDEN_DIM)
    assert bundle.semantic_blocks.shape == (23, 2, SEMANTIC_DIM, SEMANTIC_DIM)
    assert bundle.common_blocks.shape == (23, 2, COMMON_LOGIT_DIM, COMMON_LOGIT_DIM)
    assert bundle.ambient_blocks.shape == (23, 2, AMBIENT_DIM, AMBIENT_DIM)
    assert torch.equal(bundle.common_blocks, torch.ones_like(bundle.common_blocks))
    assert torch.equal(bundle.gauge, model.gauge_matrix().to(bundle.gauge.dtype))
    assert model.effective_state_embedding().shape == (N_STATES, HIDDEN_DIM)
    assert model.effective_decoder_weight().shape == (N_STATES, HIDDEN_DIM)
    assert audit.passed, audit.as_dict()
    assert audit.pmq_residual < 5e-5
    assert audit.qmp_residual < 5e-5
    assert audit.null_cross_residual < 5e-5
    assert audit.embedding_kernel_residual < 5e-5
    assert audit.embedding_common_residual < 5e-5
    assert audit.embedding_norm_residual < 5e-5
    assert audit.decoder_kernel_residual < 5e-5
    assert audit.common_logit_residual < 5e-5


def test_hard_anchors_have_fixed_common_component_unit_norm_and_zero_k_component() -> None:
    model = _learned(19)
    anchors = model.effective_state_embedding()
    common = anchors @ model.L.to(anchors.dtype)
    ambient = anchors @ model.K.to(anchors.dtype)

    assert torch.allclose(
        common,
        torch.full_like(common, 1.0 / N_STATES**0.5),
        atol=2e-6,
        rtol=2e-6,
    )
    assert torch.allclose(ambient, torch.zeros_like(ambient), atol=2e-6, rtol=2e-6)
    assert torch.allclose(
        torch.linalg.vector_norm(anchors, dim=-1),
        torch.ones(N_STATES),
        atol=2e-6,
        rtol=2e-6,
    )


def test_common_line_is_exactly_a_softmax_invariant_logit_shift() -> None:
    model = _learned(21)
    generator = torch.Generator().manual_seed(23)
    hidden = torch.randn(19, HIDDEN_DIM, generator=generator)
    common_coordinates = torch.randn(19, 1, generator=generator)
    common_perturbation = common_coordinates @ model.L.T.to(common_coordinates.dtype)

    baseline = model.decode_hidden(hidden)
    shifted = model.decode_hidden(hidden + common_perturbation)
    difference = shifted - baseline

    assert torch.allclose(
        difference,
        common_coordinates.expand(-1, N_STATES),
        atol=2e-6,
        rtol=2e-6,
    )
    assert torch.allclose(
        F.softmax(baseline, dim=-1),
        F.softmax(shifted, dim=-1),
        atol=2e-6,
        rtol=2e-6,
    )
    centered_decoder = model.centered_effective_decoder_weight()
    assert torch.allclose(
        centered_decoder @ model.P_centered_null.to(centered_decoder.dtype),
        torch.zeros_like(centered_decoder),
        atol=2e-6,
        rtol=2e-6,
    )


def test_ambient_encoder_is_frozen_and_terminal_gradients_are_semantic_only() -> None:
    model = _learned(29)
    batch = EpisodeGenerator(31).sample(32, 4, family="d4")
    logits = model(batch.tables, batch.op_slots, batch.start)
    F.cross_entropy(logits, batch.target).backward()

    assert model.semantic_state_embedding.weight.requires_grad
    assert model.semantic_decoder.weight.requires_grad
    assert model.semantic_operator_encoder.weight.requires_grad
    assert not model.ambient_operator_encoder.weight.requires_grad
    assert model.ambient_operator_encoder.weight.grad is None
    for parameter in (
        model.semantic_state_embedding.weight,
        model.semantic_decoder.weight,
        model.semantic_operator_encoder.weight,
    ):
        assert parameter.grad is not None
        assert torch.isfinite(parameter.grad).all()
        assert float(parameter.grad.norm()) > 0.0


def test_model_satisfies_recurrent_interface_and_intervention_continuation() -> None:
    model = _learned(37)
    batch = EpisodeGenerator(41).sample(14, 7, family="c8")
    prefix = model.run(batch.tables, batch.op_slots[:, :3], batch.start)
    codes = prefix.operator_codes
    assert codes is not None

    continuation = model.continue_from_hidden(
        prefix.hidden[-1],
        codes.flip(1),
        batch.op_slots[:, 3:],
    )

    assert isinstance(model, RecurrentOperatorModel)
    assert prefix.logits.shape == (14, N_STATES)
    assert len(prefix.hidden) == 4
    assert continuation.logits.shape == (14, N_STATES)
    assert len(continuation.hidden) == 5
    assert continuation.operator_codes is not None
    assert torch.isfinite(continuation.logits).all()


def test_exact_compiled_control_solves_randomly_conjugated_long_words() -> None:
    model = ExactInvariantKernelOperatorRNN(gauge_seed=43)
    batch = EpisodeGenerator(47).sample(128, 64, family="d4")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    audit = model.audit_invariant_kernel(trace.operator_codes)

    assert torch.equal(trace.logits.argmax(dim=-1), batch.target)
    assert audit.passed, audit.as_dict()
    anchors = model.effective_state_embedding()
    assert torch.allclose(
        anchors @ anchors.T,
        torch.eye(N_STATES),
        atol=2e-6,
        rtol=2e-6,
    )
    assert not any(parameter.requires_grad for parameter in model.parameters())


def test_exact_control_retains_native_float64_geometry() -> None:
    model = ExactInvariantKernelOperatorRNN(gauge_seed=49).double()
    batch = EpisodeGenerator(51).sample(16, 16, family="random")
    codes = model.encode_operators(batch.tables.double())
    audit = model.audit_invariant_kernel(codes)

    assert audit.passed, audit.as_dict()
    assert audit.frame_orthogonality_residual < 5e-11
    assert audit.operator_orthogonality_residual < 5e-11


def test_ambient_perturbations_are_invisible_and_remain_isolated_under_continuation() -> None:
    model = QuotientCurvedInvariantKernelOperatorRNN(gauge_seed=53)
    batch = EpisodeGenerator(59).sample(48, 11, family="d4")
    prefix = model.run(batch.tables, batch.op_slots[:, :5], batch.start)
    assert prefix.operator_codes is not None
    suffix = batch.op_slots[:, 5:]

    generator = torch.Generator().manual_seed(61)
    ambient_coordinates = torch.randn(48, AMBIENT_DIM, generator=generator)
    ambient_perturbation = ambient_coordinates @ model.K.T.to(ambient_coordinates.dtype)
    baseline = model.continue_from_hidden(prefix.hidden[-1], prefix.operator_codes, suffix)
    perturbed = model.continue_from_hidden(
        prefix.hidden[-1] + 17.0 * ambient_perturbation,
        prefix.operator_codes,
        suffix,
    )

    assert torch.allclose(baseline.logits, perturbed.logits, atol=2e-5, rtol=2e-5)
    assert torch.equal(baseline.logits.argmax(dim=-1), batch.target)


def test_quotient_curved_control_separates_semantic_from_full_space_flatness() -> None:
    exact = ExactInvariantKernelOperatorRNN(gauge_seed=67)
    curved = QuotientCurvedInvariantKernelOperatorRNN(gauge_seed=67)
    batch = EpisodeGenerator(71).sample(
        64,
        2,
        family="d4",
        canonical_word=(1, 1),
    )
    exact_codes = exact.encode_operators(batch.tables)
    curved_codes = curved.encode_operators(batch.tables)
    rows = torch.arange(batch.start.shape[0])
    first = curved_codes[rows, batch.op_slots[:, 0]]
    second = curved_codes[rows, batch.op_slots[:, 1]]
    holonomy = second @ first
    identity = torch.eye(HIDDEN_DIM).expand_as(holonomy)
    p_s = curved.P_S.to(holonomy.dtype)
    p_k = curved.P_K.to(holonomy.dtype)
    semantic_residual = p_s @ (holonomy - identity) @ p_s
    ambient_residual = p_k @ (holonomy - identity) @ p_k

    exact_trace = exact.run(batch.tables, batch.op_slots, batch.start)
    curved_trace = curved.run(batch.tables, batch.op_slots, batch.start)

    assert torch.equal(exact_trace.logits.argmax(dim=-1), batch.target)
    assert torch.equal(curved_trace.logits.argmax(dim=-1), batch.target)
    assert torch.allclose(exact_trace.logits, curved_trace.logits, atol=2e-5, rtol=2e-5)
    assert float(torch.linalg.matrix_norm(semantic_residual, ord="fro", dim=(-2, -1)).max()) < 2e-5
    assert float(torch.linalg.matrix_norm(ambient_residual, ord="fro", dim=(-2, -1)).min()) > 0.1


def test_state_dict_round_trip_preserves_sealed_gauge_and_behavior() -> None:
    source = _learned(73, gauge_seed=79)
    restored = _learned(83, gauge_seed=89)
    restored.load_state_dict(copy.deepcopy(source.state_dict()))
    batch = EpisodeGenerator(97).sample(12, 5, family="mixed_cycle")

    assert torch.equal(source.gauge_matrix(), restored.gauge_matrix())
    assert restored.gauge_seed == source.gauge_seed == 79
    assert torch.equal(
        source(batch.tables, batch.op_slots, batch.start),
        restored(batch.tables, batch.op_slots, batch.start),
    )
    assert not restored.ambient_operator_encoder.weight.requires_grad


def test_audit_fails_closed_for_leakage_and_nonfinite_codes() -> None:
    model = _learned(101)
    batch = EpisodeGenerator(103).sample(4, 1, family="random")
    codes = model.encode_operators(batch.tables)
    leaking_direction = torch.outer(model.S[:, 0], model.K[:, 0]).to(codes.dtype)
    leaking = codes + 0.1 * leaking_direction
    nonfinite = codes.clone()
    nonfinite[0, 0, 0, 0] = float("nan")

    leakage_audit = model.audit_invariant_kernel(leaking)
    nonfinite_audit = model.audit_invariant_kernel(nonfinite)

    assert not leakage_audit.passed
    assert leakage_audit.pmq_residual > 0.05
    assert not nonfinite_audit.passed
    assert not nonfinite_audit.all_finite


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"hidden_dim": 11}, "hidden_dim == 12"),
        ({"semantic_dim": 6}, "semantic_dim == 7"),
        ({"gauge_seed": True}, "gauge_seed"),
        ({"normalization_eps": 0.0}, "normalization_eps"),
    ],
)
def test_invalid_configuration_fails_closed(
    kwargs: dict[str, int | float | bool], message: str
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        LearnedFrameBlockIsometricOperatorRNN(**kwargs)

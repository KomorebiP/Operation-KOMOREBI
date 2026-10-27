from __future__ import annotations

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
from komorebi_neuralese.models import RecurrentOperatorModel, parameter_count
from komorebi_neuralese.packet_models import (
    PolarIsometricTableOperatorRNN,
    ProjectiveLinearTableOperatorRNN,
    ProjectiveResidualOperatorRNN,
)


def _model(seed: int = 1, hidden_dim: int = 8) -> ProjectiveResidualOperatorRNN:
    torch.manual_seed(seed)
    return ProjectiveResidualOperatorRNN(
        hidden_dim=hidden_dim,
        encoder_width=24,
        residual_cap=4.0,
    )


def test_projective_residual_model_has_compatible_trace_shapes() -> None:
    model = _model()
    batch = EpisodeGenerator(3).sample(11, 5, family="d4")
    trace = model.run(batch.tables, batch.op_slots, batch.start)

    assert isinstance(model, RecurrentOperatorModel)
    assert trace.logits.shape == (11, N_STATES)
    assert trace.operator_matrices.shape == (11, 2, 8, 8)
    assert trace.raw_operator_matrices is not None
    assert trace.raw_operator_matrices.shape == (11, 2, 8, 8)
    assert trace.residual_operator_matrices is not None
    assert trace.selected_operator_matrices.shape == (11, 5, 8, 8)
    assert trace.hidden_tensor.shape == (11, 6, 8)
    assert trace.pre_normalized_hidden_tensor.shape == (11, 5, 8)
    assert trace.radial_norms.shape == (11, 5)
    assert trace.log_radial_increments.shape == (11, 5)
    assert torch.isfinite(trace.logits).all()


def test_every_recurrent_state_is_a_unit_oriented_ray_representative() -> None:
    model = _model(5)
    batch = EpisodeGenerator(7).sample(32, 12, family="random")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    norms = torch.einsum(
        "bti,ij,btj->bt",
        trace.hidden_tensor,
        trace.metric,
        trace.hidden_tensor,
    ).sqrt()
    assert torch.allclose(norms, torch.ones_like(norms), atol=2e-6, rtol=2e-6)
    assert torch.all(trace.radial_norms > 0)


def test_trace_retains_the_discarded_radial_dynamics_exactly() -> None:
    model = _model(11)
    batch = EpisodeGenerator(13).sample(16, 4, family="mixed_cycle")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    raw = trace.pre_normalized_hidden_tensor
    reconstructed = raw / trace.radial_norms.unsqueeze(-1)
    assert torch.allclose(reconstructed, trace.hidden_tensor[:, 1:], atol=2e-6, rtol=2e-6)


def test_learned_metric_is_spd_unit_determinant_and_exposed_in_trace() -> None:
    model = _model(14, hidden_dim=6)
    with torch.no_grad():
        model.metric_log_diagonal.copy_(torch.linspace(-0.7, 0.8, 6))
        model.metric_strict_lower.copy_(
            torch.linspace(-0.5, 0.5, model.metric_strict_lower.numel())
        )
    metric = model.invariant_metric()
    batch = EpisodeGenerator(15).sample(7, 2, family="d4")
    trace = model.run(batch.tables, batch.op_slots, batch.start)

    assert torch.all(torch.linalg.eigvalsh(metric) > 0)
    assert torch.allclose(torch.linalg.det(metric), torch.tensor(1.0), atol=2e-5, rtol=2e-5)
    assert torch.allclose(trace.metric, metric)


def test_default_ambient_width_leaves_four_dimensions_beyond_eight_anchors() -> None:
    model = ProjectiveResidualOperatorRNN()
    assert model.hidden_dim == 12
    assert model.anchor_matrix().shape == (12, 8)


def test_direct_linear_table_model_has_expected_compact_parameter_count() -> None:
    model = ProjectiveLinearTableOperatorRNN()
    # 64*144 encoder + 8*12 anchors + 8*12 decoder + 78 metric coordinates.
    assert parameter_count(model) == 9_486
    assert model.hidden_dim == 12
    assert model.operator_encoder.bias is None


def test_direct_linear_table_model_uses_same_projective_trace_contract() -> None:
    torch.manual_seed(16)
    model = ProjectiveLinearTableOperatorRNN(hidden_dim=12)
    batch = EpisodeGenerator(18).sample(13, 6, family="d4")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    metric_norms = torch.einsum(
        "bti,ij,btj->bt",
        trace.hidden_tensor,
        trace.metric,
        trace.hidden_tensor,
    ).sqrt()

    assert trace.operator_matrices.shape == (13, 2, 12, 12)
    assert trace.selected_operator_matrices.shape == (13, 6, 12, 12)
    assert trace.hidden_tensor.shape == (13, 7, 12)
    assert trace.raw_operator_matrices is not None
    assert trace.residual_operator_matrices is None
    assert torch.allclose(metric_norms, torch.ones_like(metric_norms), atol=2e-6, rtol=2e-6)


def test_direct_linear_table_terminal_loss_reaches_encoder_and_metric() -> None:
    torch.manual_seed(20)
    model = ProjectiveLinearTableOperatorRNN(hidden_dim=12)
    batch = EpisodeGenerator(22).sample(32, 4, family="d4")
    result = model.terminal_task(batch.tables, batch.op_slots, batch.start, batch.target)
    result.loss.backward()
    assert model.operator_encoder.weight.grad is not None
    assert float(model.operator_encoder.weight.grad.norm()) > 0
    assert model.metric_log_diagonal.grad is not None
    assert float(model.metric_log_diagonal.grad.norm()) > 0


def test_polar_control_uses_fixed_identity_metric_and_orthogonal_codes() -> None:
    torch.manual_seed(24)
    model = PolarIsometricTableOperatorRNN()
    batch = EpisodeGenerator(26).sample(31, 3, family="random")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    identity = torch.eye(12).expand(31, 2, 12, 12)
    gram = trace.operator_matrices.transpose(-1, -2) @ trace.operator_matrices

    assert torch.equal(trace.metric, torch.eye(12))
    assert torch.allclose(gram, identity, atol=3e-5, rtol=3e-5)
    determinants = torch.linalg.det(trace.operator_matrices)
    assert torch.allclose(determinants.abs(), torch.ones_like(determinants), atol=3e-5, rtol=3e-5)
    assert torch.allclose(
        trace.radial_norms,
        torch.ones_like(trace.radial_norms),
        atol=3e-5,
        rtol=3e-5,
    )
    assert not model.metric_log_diagonal.requires_grad
    assert not model.metric_strict_lower.requires_grad


def test_polar_retraction_keeps_both_orientation_components() -> None:
    positive = torch.diag(torch.linspace(0.5, 1.5, 12))
    negative = positive.clone()
    negative[-1, -1] *= -1
    polar = PolarIsometricTableOperatorRNN.polar_retraction(
        torch.stack((positive, negative))
    )
    determinants = torch.linalg.det(polar)
    assert torch.allclose(determinants, torch.tensor([1.0, -1.0]), atol=2e-6, rtol=2e-6)


def test_polar_control_trace_preserves_raw_and_patched_operator_apis() -> None:
    torch.manual_seed(28)
    model = PolarIsometricTableOperatorRNN()
    batch = EpisodeGenerator(30).sample(9, 5, family="d4")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    assert trace.raw_operator_matrices is not None
    assert trace.raw_operator_matrices.shape == (9, 2, 12, 12)
    assert trace.residual_operator_matrices is None

    patched = trace.operator_matrices.flip(1)
    continuation = model.continue_from_hidden(
        trace.hidden[2],
        patched,
        batch.op_slots[:, 2:],
    )
    assert continuation.operator_matrices is patched
    assert continuation.selected_operator_matrices.shape == (9, 3, 12, 12)
    assert torch.isfinite(continuation.logits).all()


def test_polar_control_terminal_gradient_reaches_raw_table_encoder() -> None:
    torch.manual_seed(32)
    model = PolarIsometricTableOperatorRNN()
    batch = EpisodeGenerator(34).sample(24, 4, family="d4")
    result = model.terminal_task(batch.tables, batch.op_slots, batch.start, batch.target)
    result.loss.backward()
    gradient = model.operator_encoder.weight.grad
    assert gradient is not None
    assert torch.isfinite(gradient).all()
    assert float(gradient.norm()) > 0


def test_polar_control_rejects_noncanonical_width() -> None:
    with pytest.raises(ValueError, match="hidden_dim == 12"):
        PolarIsometricTableOperatorRNN(hidden_dim=8)


def test_projective_step_ignores_positive_radial_rescaling() -> None:
    model = _model(17, hidden_dim=6)
    generator = torch.Generator().manual_seed(19)
    hidden = torch.randn(9, 6, generator=generator)
    matrices = torch.randn(9, 6, 6, generator=generator)
    reference = model.step_hidden(hidden, matrices)
    rescaled = model.step_hidden(7.0 * hidden, 3.0 * matrices)
    assert torch.allclose(reference, rescaled, atol=2e-6, rtol=2e-6)


def test_residual_hypernetwork_is_smoothly_bounded_not_a_table_executor() -> None:
    # A hidden dimension different from the state count makes direct insertion
    # of the 8x8 semantic permutation tables structurally impossible.
    model = _model(23, hidden_dim=5)
    batch = EpisodeGenerator(29).sample(64, 0, family="random")
    bundle = model.encode_operator_bundle(batch.tables)
    residual_norm = torch.linalg.vector_norm(
        bundle.residuals.flatten(start_dim=-2), dim=-1
    )
    identity = torch.eye(5).reshape(1, 1, 5, 5)

    assert bundle.matrices.shape == (64, 2, 5, 5)
    assert bool(torch.all(residual_norm < model.residual_cap))
    assert torch.allclose(bundle.matrices, identity + bundle.residuals)
    assert bundle.matrices.shape[-2:] != batch.tables.shape[-2:]
    assert not torch.equal(bundle.matrices[0, 0], bundle.matrices[0, 1])


def test_terminal_only_objective_backpropagates_through_all_learned_parts() -> None:
    model = _model(31)
    batch = EpisodeGenerator(37).sample(48, 4, family="d4")
    result = model.terminal_task(
        batch.tables,
        batch.op_slots,
        batch.start,
        batch.target,
    )
    expected = F.cross_entropy(result.trace.logits, batch.target)
    assert torch.allclose(result.loss, expected)
    assert result.accuracy.ndim == 0
    result.loss.backward()

    assert model.state_embedding.weight.grad is not None
    assert model.operator_head.weight.grad is not None
    assert model.decoder.weight.grad is not None
    assert model.metric_log_diagonal.grad is not None
    assert model.metric_strict_lower.grad is not None
    assert float(model.state_embedding.weight.grad.norm()) > 0
    assert float(model.operator_head.weight.grad.norm()) > 0
    assert float(model.decoder.weight.grad.norm()) > 0
    assert float(model.metric_log_diagonal.grad.norm()) > 0
    assert float(model.metric_strict_lower.grad.norm()) > 0
    trunk_gradient = sum(
        float(parameter.grad.norm())
        for parameter in model.operator_trunk.parameters()
        if parameter.grad is not None
    )
    assert trunk_gradient > 0


def test_continuation_canonicalizes_the_donor_scale_and_exposes_selected_codes() -> None:
    model = _model(41)
    batch = EpisodeGenerator(43).sample(10, 7, family="c8")
    prefix = model.run(batch.tables, batch.op_slots[:, :3], batch.start)
    suffix_slots = batch.op_slots[:, 3:]
    direct = model.continue_from_hidden(
        prefix.hidden[-1],
        prefix.operator_matrices,
        suffix_slots,
    )
    rescaled = model.continue_from_hidden(
        23.0 * prefix.hidden[-1],
        prefix.operator_matrices,
        suffix_slots,
    )

    assert torch.allclose(direct.logits, rescaled.logits, atol=2e-6, rtol=2e-6)
    assert direct.selected_operator_matrices.shape == (10, 4, 8, 8)
    assert direct.raw_operator_matrices is None
    assert direct.residual_operator_matrices is not None


def test_empty_word_has_well_typed_empty_auxiliary_trajectories() -> None:
    model = _model(47, hidden_dim=7)
    batch = EpisodeGenerator(53).sample(6, 0, family="d4")
    trace = model.run(batch.tables, batch.op_slots, batch.start)
    assert trace.hidden_tensor.shape == (6, 1, 7)
    assert trace.pre_normalized_hidden_tensor.shape == (6, 0, 7)
    assert trace.selected_operator_matrices.shape == (6, 0, 7, 7)
    assert trace.radial_norms.shape == (6, 0)
    assert trace.log_radial_increments.shape == (6, 0)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"hidden_dim": 1}, "hidden_dim"),
        ({"encoder_width": 0}, "encoder_width"),
        ({"residual_cap": 0.0}, "residual_cap"),
        ({"normalization_eps": 0.0}, "normalization_eps"),
        ({"metric_log_diagonal_cap": 0.0}, "metric_log_diagonal_cap"),
        ({"metric_offdiagonal_cap": 0.0}, "metric_offdiagonal_cap"),
    ],
)
def test_invalid_model_configuration_fails_closed(
    kwargs: dict[str, int | float], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        ProjectiveResidualOperatorRNN(**kwargs)


def test_invalid_operator_indices_fail_closed() -> None:
    model = _model(59)
    batch = EpisodeGenerator(61).sample(4, 2, family="d4")
    bad_slots = batch.op_slots.clone()
    bad_slots[0, 0] = 2
    with pytest.raises(IndexError, match="out-of-range"):
        model.run(batch.tables, bad_slots, batch.start)

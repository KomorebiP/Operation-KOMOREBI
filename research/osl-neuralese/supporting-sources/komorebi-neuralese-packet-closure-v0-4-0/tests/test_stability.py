from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.models import LinearHyperOperatorRNN
from komorebi_neuralese.projective import normalize_ray, projective_tangent_jacobian
from komorebi_neuralese.stability import (
    anchor_basis,
    anchor_closed_codes,
    anchor_metric,
    future_observability,
    metric_polar_codes,
    conformal_metric_defect,
    normalized_anchor_defect,
    normalized_metric_defect,
    projective_anchor_defect,
    switched_feshbach_analysis,
)


def test_centered_decoder_rank_is_not_inflated_by_float32_roundoff() -> None:
    from komorebi_neuralese.stability import centered_decoder

    decoder = torch.randn(8, 8, generator=torch.Generator().manual_seed(2), dtype=torch.float32)
    centered = centered_decoder(decoder)
    singular = torch.linalg.svdvals(centered)
    assert int((singular > singular[0] * 1e-6).sum()) == 7


def test_projective_defects_ignore_positive_operator_scale() -> None:
    model = _well_conditioned_model(4)
    batch = EpisodeGenerator(5).sample(32, 0, family="d4")
    basis = anchor_basis(model)
    exact = anchor_closed_codes(model, batch.tables)
    scaled = 0.125 * exact
    anchor_error, fitted = projective_anchor_defect(scaled, batch.tables, basis)
    conformal_error, scale = conformal_metric_defect(scaled, anchor_metric(model))
    assert float(anchor_error.max().detach()) < 2e-5
    assert float(conformal_error.max().detach()) < 2e-5
    assert torch.all(fitted > 0)
    assert torch.all(scale > 0)
from komorebi_neuralese.stable_models import (
    AnchorClosedOperatorRNN,
    NormalizedRawOperatorRNN,
    ProjectiveLinearHyperOperatorRNN,
    SemanticChartClosedOperatorRNN,
)


def _well_conditioned_model(seed: int = 1) -> LinearHyperOperatorRNN:
    torch.manual_seed(seed)
    model = LinearHyperOperatorRNN(hidden_dim=8)
    with torch.no_grad():
        orthogonal, _ = torch.linalg.qr(torch.randn(8, 8))
        model.state_embedding.weight.copy_(orthogonal.transpose(0, 1))
        model.decoder.weight.copy_(orthogonal.transpose(0, 1))
    return model


def test_anchor_closed_codes_execute_visible_table() -> None:
    model = _well_conditioned_model()
    batch = EpisodeGenerator(3).sample(64, 0, family="d4")
    codes = anchor_closed_codes(model, batch.tables)
    basis = anchor_basis(model)
    defect = normalized_anchor_defect(codes, batch.tables, basis)
    assert float(defect.max().detach()) < 1e-5
    source = model.initial_hidden(torch.arange(8).repeat(8))
    rows = torch.arange(64)
    target_state = batch.maps[rows, torch.zeros(64, dtype=torch.long), torch.arange(8).repeat(8)]
    observed = torch.bmm(codes[:, 0], source.unsqueeze(-1)).squeeze(-1)
    expected = model.initial_hidden(target_state)
    assert torch.allclose(observed, expected, atol=2e-5, rtol=2e-5)


def test_anchor_metric_makes_closed_codes_isometric() -> None:
    model = _well_conditioned_model(5)
    batch = EpisodeGenerator(7).sample(128, 0, family="random")
    codes = anchor_closed_codes(model, batch.tables)
    defect = normalized_metric_defect(codes, anchor_metric(model))
    assert float(defect.max().detach()) < 2e-5


def test_normalization_preserves_finite_linear_predictions() -> None:
    model = _well_conditioned_model(11)
    normalized = NormalizedRawOperatorRNN(model)
    batch = EpisodeGenerator(13).sample(128, 32, family="d4")
    raw = model.run(batch.tables, batch.op_slots, batch.start)
    projective = normalized.run(batch.tables, batch.op_slots, batch.start)
    assert torch.equal(raw.logits.argmax(dim=1), projective.logits.argmax(dim=1))
    assert torch.allclose(projective.hidden[-1].norm(dim=1), torch.ones(128), atol=1e-6, rtol=1e-6)


def test_projective_tangent_jacobian_annihilates_radial_direction() -> None:
    generator = torch.Generator().manual_seed(17)
    metric = torch.eye(5)
    state = normalize_ray(torch.randn(5, generator=generator), metric)
    operator = torch.randn(5, 5, generator=generator)
    jacobian, endpoint = projective_tangent_jacobian(operator, state, metric)
    assert torch.allclose(jacobian @ state, torch.zeros(5), atol=2e-6, rtol=2e-6)
    assert torch.allclose(endpoint @ metric @ endpoint, torch.tensor(1.0), atol=2e-6, rtol=2e-6)


def test_future_observability_distinguishes_fixed_null_from_delayed_visibility() -> None:
    decoder = torch.tensor([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
    identity_codes = torch.eye(3).reshape(1, 1, 3, 3)
    null_result = future_observability(decoder, identity_codes, max_depth=3, episode_limit=None)
    assert null_result.rank == 1
    assert null_result.null_dimension == 2

    shift = torch.tensor([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    visible_codes = torch.stack((torch.eye(3), shift)).reshape(1, 2, 3, 3)
    full_result = future_observability(decoder, visible_codes, max_depth=2, episode_limit=None)
    assert full_result.rank == 3
    assert full_result.null_dimension == 0


def test_metric_polar_projection_is_isometric() -> None:
    generator = torch.Generator().manual_seed(19)
    codes = torch.randn(32, 2, 4, 4, generator=generator)
    factor = torch.randn(4, 4, generator=generator)
    metric = factor.transpose(0, 1) @ factor + 0.5 * torch.eye(4)
    projected = metric_polar_codes(codes, metric)
    defect = normalized_metric_defect(projected, metric)
    assert float(defect.max()) < 2e-5


def _switched_return_system(with_return: bool) -> torch.Tensor:
    operators = torch.zeros(2, 4, 4)
    operators[:, 0, 0] = 1.0
    operators[0, 1, 0] = 1.0
    operators[0, 2, 1] = 1.0
    operators[1, 3, 2] = 1.0
    if with_return:
        operators[1, 0, 3] = 1.0
    return operators


def test_switched_feshbach_detects_delayed_cross_generator_return() -> None:
    retained = torch.eye(4)[:, :1]
    nuisance = torch.eye(4)[:, 1:]
    closed = switched_feshbach_analysis(_switched_return_system(False), retained, nuisance)
    returning = switched_feshbach_analysis(_switched_return_system(True), retained, nuisance)
    assert closed.closed_at_tolerance
    assert closed.mixed_return_rank == 0
    assert not returning.closed_at_tolerance
    assert returning.mixed_return_rank >= 1


def test_anchor_closed_wrapper_remains_exact_at_depth_128() -> None:
    model = _well_conditioned_model(23)
    closed = AnchorClosedOperatorRNN(model)
    batch = EpisodeGenerator(29).sample(256, 128, family="random")
    trace = closed.run(batch.tables, batch.op_slots, batch.start)
    assert torch.equal(trace.logits.argmax(dim=1), batch.target)
    assert torch.isfinite(trace.hidden[-1]).all()


def test_semantic_chart_is_euclidean_and_exact() -> None:
    model = _well_conditioned_model(31)
    closed = SemanticChartClosedOperatorRNN(model)
    batch = EpisodeGenerator(37).sample(256, 256, family="random")
    trace = closed.run(batch.tables, batch.op_slots, batch.start)
    assert torch.equal(trace.logits.argmax(dim=1), batch.target)
    assert torch.allclose(trace.hidden[-1].norm(dim=1), torch.ones(256), atol=0, rtol=0)
    assert torch.equal(closed.invariant_metric, torch.eye(8))


def test_projective_model_is_checkpoint_shape_compatible() -> None:
    raw = _well_conditioned_model(41)
    projective = ProjectiveLinearHyperOperatorRNN(hidden_dim=8)
    projective.load_state_dict(raw.state_dict(), strict=True)
    batch = EpisodeGenerator(43).sample(64, 4, family="d4")
    trace = projective.run(batch.tables, batch.op_slots, batch.start)
    assert torch.allclose(trace.hidden[-1].norm(dim=1), torch.ones(64), atol=1e-6, rtol=1e-6)

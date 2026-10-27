from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.stability_training import (
    anchor_gram_conditioning_loss,
    feshbach_block_diagnostics,
    feshbach_return_diagnostics,
    g_orthogonal_anchor_projector,
    metric_condition_diagnostics,
    metric_conditioning_regularizer,
    scale_free_conformal_defect,
    switched_projective_tangent_gain_hinge,
)


DTYPE = torch.float64


def _spd(dimension: int, seed: int = 1) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    factor = torch.randn(dimension, dimension, generator=generator, dtype=DTYPE)
    return factor @ factor.transpose(0, 1) + 0.7 * torch.eye(dimension, dtype=DTYPE)


def _coordinate_change(dimension: int, seed: int = 2) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    candidate = torch.randn(dimension, dimension, generator=generator, dtype=DTYPE)
    return candidate + 2.5 * torch.eye(dimension, dtype=DTYPE)


def _g_orthogonal_operator(metric: torch.Tensor, angle: float = 0.4) -> torch.Tensor:
    dimension = metric.shape[0]
    rotation = torch.eye(dimension, dtype=metric.dtype)
    cosine = torch.cos(torch.tensor(angle, dtype=metric.dtype))
    sine = torch.sin(torch.tensor(angle, dtype=metric.dtype))
    rotation[:2, :2] = torch.stack(
        (torch.stack((cosine, -sine)), torch.stack((sine, cosine)))
    )
    chart = torch.linalg.cholesky(metric).transpose(0, 1)
    return torch.linalg.solve(chart, rotation @ chart)


def test_exact_g_isometry_has_zero_scale_free_conformal_defect() -> None:
    metric = _spd(5, 3)
    operator = _g_orthogonal_operator(metric)
    result = scale_free_conformal_defect(operator, metric)

    assert float(result.loss) < 1e-25
    assert torch.allclose(
        operator.transpose(0, 1) @ metric @ operator,
        metric,
        atol=2e-12,
        rtol=2e-12,
    )


def test_nonnormal_shear_has_positive_conformal_defect() -> None:
    operator = torch.tensor([[1.0, 7.0], [0.0, 1.0]], dtype=DTYPE)
    result = scale_free_conformal_defect(operator, torch.eye(2, dtype=DTYPE))
    assert float(result.defect) > 0.5


def test_conformal_defect_is_operator_scale_invariant_and_coordinate_covariant() -> None:
    metric = _spd(4, 5)
    generator = torch.Generator().manual_seed(7)
    operators = torch.randn(3, 4, 4, generator=generator, dtype=DTYPE)
    scales = torch.tensor([0.07, 3.0, 41.0], dtype=DTYPE)[:, None, None]
    reference = scale_free_conformal_defect(operators, metric, reduction="none")
    rescaled = scale_free_conformal_defect(scales * operators, 11.0 * metric, reduction="none")

    coordinates = _coordinate_change(4, 11)
    inverse = torch.linalg.inv(coordinates)
    transformed_operators = coordinates @ operators @ inverse
    transformed_metric = inverse.transpose(0, 1) @ metric @ inverse
    transformed = scale_free_conformal_defect(
        transformed_operators, transformed_metric, reduction="none"
    )

    assert torch.allclose(reference.defect, rescaled.defect, atol=2e-12, rtol=2e-12)
    assert torch.allclose(reference.defect, transformed.defect, atol=2e-11, rtol=2e-11)


def test_metric_barrier_is_scale_free_and_flags_a_near_zero_direction() -> None:
    identity = torch.eye(4, dtype=DTYPE)
    healthy = metric_conditioning_regularizer(identity)
    ill = torch.diag(torch.tensor([1e-8, 1.0, 2.0, 3.0], dtype=DTYPE))
    ill_result = metric_conditioning_regularizer(ill)
    rescaled = metric_conditioning_regularizer(29.0 * ill)
    diagnostics = metric_condition_diagnostics(ill)

    assert float(healthy.loss) == 0.0
    assert float(ill_result.near_zero_loss) > 0.0
    assert float(ill_result.condition_hinge_loss) > 0.0
    assert torch.allclose(ill_result.loss, rescaled.loss, atol=2e-12, rtol=2e-12)
    assert float(diagnostics.condition_number) > 1e8
    assert bool(diagnostics.positive_definite)


def test_anchor_gram_conditioning_is_zero_for_a_g_orthonormal_frame() -> None:
    metric = _spd(6, 13)
    chart = torch.linalg.cholesky(metric).transpose(0, 1)
    anchors = torch.linalg.inv(chart.transpose(0, 1))
    result = anchor_gram_conditioning_loss(anchors, metric)

    assert torch.allclose(result.gram, torch.eye(6, dtype=DTYPE), atol=2e-12, rtol=2e-12)
    assert float(result.loss) < 1e-25
    assert int(result.numerical_rank) == 6


def test_anchor_gram_loss_is_coordinate_covariant() -> None:
    metric = _spd(4, 17)
    generator = torch.Generator().manual_seed(19)
    anchors = torch.randn(6, 4, generator=generator, dtype=DTYPE)
    reference = anchor_gram_conditioning_loss(anchors, metric)
    coordinates = _coordinate_change(4, 23)
    inverse = torch.linalg.inv(coordinates)
    transformed_anchors = anchors @ coordinates.transpose(0, 1)
    transformed_metric = inverse.transpose(0, 1) @ metric @ inverse
    transformed = anchor_gram_conditioning_loss(transformed_anchors, transformed_metric)

    assert torch.allclose(
        reference.active_eigenvalues,
        transformed.active_eigenvalues,
        atol=2e-10,
        rtol=2e-10,
    )
    assert torch.allclose(reference.loss, transformed.loss, atol=2e-10, rtol=2e-10)


def test_eight_anchors_in_twelve_dimensions_are_conditioned_without_erasing_q() -> None:
    dimension = 12
    anchors = torch.eye(dimension, dtype=DTYPE)[:8]
    metric = torch.eye(dimension, dtype=DTYPE)
    conditioning = anchor_gram_conditioning_loss(anchors, metric)
    plane = g_orthogonal_anchor_projector(anchors, metric)

    assert conditioning.active_eigenvalues.shape == (8,)
    assert int(conditioning.numerical_rank) == 8
    assert float(conditioning.loss) == 0.0
    assert plane.rank == 8
    assert torch.allclose(
        plane.complement_effective_trace, torch.tensor(4.0, dtype=DTYPE)
    )


def test_g_isometric_word_has_unit_prefix_tangent_gain() -> None:
    metric = _spd(4, 29)
    first = _g_orthogonal_operator(metric, 0.2)
    second = _g_orthogonal_operator(metric, -0.7)
    words = torch.stack((first, second, first, second)).unsqueeze(0)
    state = torch.tensor([[1.0, -0.4, 0.2, 0.7]], dtype=DTYPE)
    result = switched_projective_tangent_gain_hinge(
        words,
        state,
        metric,
        maximum_gain=1.0 + 1e-10,
    )

    assert torch.allclose(result.prefix_gains, torch.ones_like(result.prefix_gains), atol=2e-11, rtol=2e-11)
    assert float(result.loss) == 0.0


def test_nonnormal_word_triggers_switched_tangent_gain_hinge() -> None:
    operator = torch.tensor([[0.5, 3.0], [0.0, 0.5]], dtype=DTYPE)
    _, _, right_vectors_h = torch.linalg.svd(operator)
    state = right_vectors_h[-1].unsqueeze(0)
    result = switched_projective_tangent_gain_hinge(
        operator.reshape(1, 1, 2, 2),
        state,
        torch.eye(2, dtype=DTYPE),
        maximum_gain=1.1,
    )

    assert float(result.maximum_prefix_gain) > 5.0
    assert float(result.loss) > 0.0


def test_switched_gain_is_scale_invariant_and_coordinate_covariant() -> None:
    metric = _spd(3, 31)
    generator = torch.Generator().manual_seed(37)
    words = torch.randn(2, 4, 3, 3, generator=generator, dtype=DTYPE)
    states = torch.randn(2, 3, generator=generator, dtype=DTYPE)
    reference = switched_projective_tangent_gain_hinge(
        words, states, metric, maximum_gain=1.3, reduction="none"
    )
    scales = torch.tensor([0.2, 4.0, 0.07, 12.0], dtype=DTYPE)[None, :, None, None]
    rescaled = switched_projective_tangent_gain_hinge(
        words * scales,
        9.0 * states,
        5.0 * metric,
        maximum_gain=1.3,
        reduction="none",
    )
    coordinates = _coordinate_change(3, 41)
    inverse = torch.linalg.inv(coordinates)
    transformed_words = coordinates @ words @ inverse
    transformed_states = states @ coordinates.transpose(0, 1)
    transformed_metric = inverse.transpose(0, 1) @ metric @ inverse
    transformed = switched_projective_tangent_gain_hinge(
        transformed_words,
        transformed_states,
        transformed_metric,
        maximum_gain=1.3,
        reduction="none",
    )

    assert torch.allclose(reference.prefix_log_gains, rescaled.prefix_log_gains, atol=2e-11, rtol=2e-11)
    assert torch.allclose(reference.prefix_log_gains, transformed.prefix_log_gains, atol=2e-10, rtol=2e-10)
    assert torch.allclose(reference.per_word_loss, transformed.per_word_loss, atol=2e-10, rtol=2e-10)


def test_all_training_losses_have_finite_gradients() -> None:
    generator = torch.Generator().manual_seed(43)
    raw_metric = torch.randn(4, 4, generator=generator, dtype=DTYPE, requires_grad=True)
    metric = raw_metric @ raw_metric.transpose(0, 1) + 0.5 * torch.eye(4, dtype=DTYPE)
    anchors = torch.randn(5, 4, generator=generator, dtype=DTYPE, requires_grad=True)
    operators = torch.randn(2, 3, 4, 4, generator=generator, dtype=DTYPE, requires_grad=True)
    states = torch.randn(2, 4, generator=generator, dtype=DTYPE, requires_grad=True)

    anchor_loss = anchor_gram_conditioning_loss(anchors, metric).loss
    conformal_loss = scale_free_conformal_defect(operators, metric).loss
    gain_loss = switched_projective_tangent_gain_hinge(
        operators,
        states,
        metric,
        maximum_gain=0.5,
        near_zero_weight=0.1,
    ).loss
    metric_loss = metric_conditioning_regularizer(
        metric, maximum_condition=1.0
    ).loss
    total = anchor_loss + conformal_loss + gain_loss + metric_loss
    total.backward()

    for tensor in (raw_metric, anchors, operators, states):
        assert tensor.grad is not None
        assert torch.isfinite(tensor.grad).all()


def test_spanning_eight_dimensional_anchor_plane_exposes_q_zero_vacuity() -> None:
    dimension = 8
    metric = torch.eye(dimension, dtype=DTYPE)
    plane = g_orthogonal_anchor_projector(torch.eye(dimension, dtype=DTYPE), metric)
    generator = torch.Generator().manual_seed(47)
    operator = torch.randn(dimension, dimension, generator=generator, dtype=DTYPE)
    blocks = feshbach_block_diagnostics(operator, plane, metric)
    returned = feshbach_return_diagnostics(operator, operator, operator, plane, metric)

    assert plane.rank == dimension
    assert torch.allclose(plane.projector, torch.eye(dimension, dtype=DTYPE))
    assert torch.allclose(plane.complement, torch.zeros_like(plane.complement))
    assert float(plane.complement_effective_trace) == 0.0
    assert float(blocks.p_to_q_energy) == 0.0
    assert float(blocks.q_to_p_energy) == 0.0
    assert float(blocks.q_to_q_energy) == 0.0
    assert float(returned.return_energy) == 0.0


def test_rank_four_plane_in_dimension_twelve_has_real_complement_and_return() -> None:
    dimension = 12
    metric = torch.eye(dimension, dtype=DTYPE)
    anchors = torch.eye(dimension, dtype=DTYPE)[:4]
    plane = g_orthogonal_anchor_projector(anchors, metric)
    departure = torch.zeros(dimension, dimension, dtype=DTYPE)
    interior = torch.zeros_like(departure)
    returning = torch.zeros_like(departure)
    departure[4, 0] = 2.0
    interior[5, 4] = 3.0
    returning[1, 5] = 5.0

    returned = feshbach_return_diagnostics(
        returning, interior, departure, plane, metric
    )
    blocks = feshbach_block_diagnostics(departure, plane, metric)

    assert plane.rank == 4
    assert torch.allclose(plane.effective_trace, torch.tensor(4.0, dtype=DTYPE))
    assert torch.allclose(
        plane.complement_effective_trace, torch.tensor(8.0, dtype=DTYPE)
    )
    assert torch.allclose(returned.return_operator[1, 0], torch.tensor(30.0, dtype=DTYPE))
    assert torch.count_nonzero(returned.return_operator) == 1
    assert torch.allclose(returned.submultiplicative_fraction, torch.tensor(1.0, dtype=DTYPE))
    assert torch.allclose(blocks.p_to_q_fraction, torch.tensor(1.0, dtype=DTYPE))


def test_projector_and_feshbach_energies_are_coordinate_covariant() -> None:
    dimension = 5
    metric = _spd(dimension, 53)
    generator = torch.Generator().manual_seed(59)
    anchors = torch.randn(3, dimension, generator=generator, dtype=DTYPE)
    operator = torch.randn(dimension, dimension, generator=generator, dtype=DTYPE)
    plane = g_orthogonal_anchor_projector(anchors, metric)
    blocks = feshbach_block_diagnostics(operator, plane, metric)

    coordinates = _coordinate_change(dimension, 61)
    inverse = torch.linalg.inv(coordinates)
    transformed_anchors = anchors @ coordinates.transpose(0, 1)
    transformed_metric = inverse.transpose(0, 1) @ metric @ inverse
    transformed_operator = coordinates @ operator @ inverse
    transformed_plane = g_orthogonal_anchor_projector(
        transformed_anchors, transformed_metric
    )
    transformed_blocks = feshbach_block_diagnostics(
        transformed_operator, transformed_plane, transformed_metric
    )

    assert torch.allclose(
        transformed_plane.projector,
        coordinates @ plane.projector @ inverse,
        atol=2e-10,
        rtol=2e-10,
    )
    for left, right in (
        (blocks.p_to_q_fraction, transformed_blocks.p_to_q_fraction),
        (blocks.q_to_p_fraction, transformed_blocks.q_to_p_fraction),
        (blocks.q_to_q_fraction, transformed_blocks.q_to_q_fraction),
    ):
        assert torch.allclose(left, right, atol=2e-10, rtol=2e-10)

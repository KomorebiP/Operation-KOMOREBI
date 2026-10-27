from __future__ import annotations

import math
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.switched_stability import (
    margin_to_amplification_risk,
    nonnormal_switched_counterexample,
    normalized_decoder_margin,
    normalized_projective_jacobian,
    normalized_projective_map,
    projective_sequence_jacobian,
    relation_loop_repeated_drift,
    verify_projective_jacobian_finite_difference,
)


def _spd_metric(dimension: int, seed: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    factor = torch.randn(dimension, dimension, generator=generator, dtype=torch.float64)
    return factor.transpose(0, 1) @ factor + 0.75 * torch.eye(dimension, dtype=torch.float64)


def test_normalized_projective_map_is_scale_safe_and_metric_unit() -> None:
    generator = torch.Generator().manual_seed(1101)
    operator = torch.randn(4, 4, generator=generator, dtype=torch.float64)
    state = torch.randn(4, generator=generator, dtype=torch.float64)
    metric = _spd_metric(4, 103)
    ordinary = normalized_projective_map(operator, state, metric)
    huge = normalized_projective_map(1e200 * operator, 1e150 * state, metric)
    assert torch.allclose(ordinary, huge, atol=2e-14, rtol=2e-14)
    assert torch.allclose(ordinary @ metric @ ordinary, torch.tensor(1.0, dtype=torch.float64), atol=2e-14)


def test_projective_jacobian_annihilates_radial_direction_and_is_tangent() -> None:
    generator = torch.Generator().manual_seed(107)
    operator = torch.randn(5, 5, generator=generator, dtype=torch.float64)
    state = torch.randn(5, generator=generator, dtype=torch.float64)
    metric = _spd_metric(5, 109)
    unit = state / torch.sqrt(state @ metric @ state)
    jacobian, endpoint = normalized_projective_jacobian(operator, unit, metric)
    assert torch.linalg.vector_norm(jacobian @ unit) < 2e-13
    assert torch.linalg.vector_norm(endpoint @ metric @ jacobian) < 2e-13


def test_sequence_jacobian_matches_autograd_and_reports_worst_gain() -> None:
    generator = torch.Generator().manual_seed(113)
    operators = torch.randn(4, 3, 3, generator=generator, dtype=torch.float64)
    state = torch.randn(3, generator=generator, dtype=torch.float64)
    state = state / torch.linalg.vector_norm(state)
    result = projective_sequence_jacobian(operators, state)

    def switched(candidate: torch.Tensor) -> torch.Tensor:
        current = candidate
        for operator in operators:
            current = normalized_projective_map(operator, current)
        return current

    automatic = torch.autograd.functional.jacobian(switched, state)
    assert result.jacobian_product is not None
    assert torch.allclose(result.jacobian_product, automatic, atol=2e-12, rtol=2e-12)
    direct_gain = float(torch.linalg.svdvals(automatic)[0])
    assert math.isclose(result.worst_singular_amplification, direct_gain, rel_tol=2e-12, abs_tol=2e-12)
    assert len(result.prefix_worst_singular_amplifications) == 4
    assert len(result.step_worst_singular_amplifications) == 4


def test_margin_to_amplification_certificate_changes_at_boundary() -> None:
    decoder = torch.tensor([[1.0, 0.0], [0.0, 1.0]], dtype=torch.float64)
    state = torch.tensor([1.0, 0.0], dtype=torch.float64)
    margin = normalized_decoder_margin(decoder, state, target=0)
    assert math.isclose(margin, 1 / math.sqrt(2), rel_tol=1e-14)
    safe = margin_to_amplification_risk(margin, worst_singular_amplification=2.0, input_radius=0.25)
    unsafe = margin_to_amplification_risk(margin, worst_singular_amplification=3.0, input_radius=0.25)
    assert safe.certified_safe
    assert safe.remaining_margin_lower_bound > 0
    assert not unsafe.certified_safe
    assert unsafe.remaining_margin_lower_bound < 0


def test_relation_loop_drift_detects_repeated_small_holonomy() -> None:
    epsilon = 0.01
    angle = math.pi / 2 + epsilon / 4
    rotation = torch.tensor(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]],
        dtype=torch.float64,
    )
    loop = rotation.repeat(4, 1, 1)
    result = relation_loop_repeated_drift(loop, torch.tensor([1.0, 0.0], dtype=torch.float64), repeats=6)
    expected = tuple((index + 1) * epsilon for index in range(6))
    assert torch.allclose(torch.tensor(result.drift_radians), torch.tensor(expected), atol=2e-13, rtol=2e-13)
    assert result.terminal_drift_radians > result.drift_radians[0]


def test_nonnormal_switching_defeats_individual_spectral_radius_check() -> None:
    result = nonnormal_switched_counterexample()
    assert result.is_counterexample
    assert max(result.individual_spectral_radii) == 0.5
    assert result.period_spectral_radius > 1.45
    assert result.period_operator_norm > result.period_spectral_radius
    assert result.projective_worst_amplification > 30.0


def test_five_point_verification_remains_accurate_under_huge_operator_scale() -> None:
    generator = torch.Generator().manual_seed(127)
    operator = 1e200 * torch.randn(4, 4, generator=generator, dtype=torch.float64)
    state = torch.randn(4, generator=generator, dtype=torch.float64)
    metric = _spd_metric(4, 131)
    result = verify_projective_jacobian_finite_difference(operator, state, metric)
    assert result.passed
    assert result.relative_frobenius_error < 2e-8
    assert result.max_absolute_error < 2e-8
    assert torch.isfinite(result.finite_difference_jacobian).all()

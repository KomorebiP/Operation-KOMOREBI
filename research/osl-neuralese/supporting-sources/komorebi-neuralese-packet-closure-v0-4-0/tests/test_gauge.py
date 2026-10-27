from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.gauge import (
    cocycle_diagnostic,
    column_permutation_matrix,
    compose_monomial_cocycle,
    decompose_operator_gauge,
    gauge_rescaling_diagnostic,
    loop_scale_diagnostic,
    rescale_anchor_basis,
    semantic_coordinates,
    transform_state_scales_under_anchor_gauge,
)


DTYPE = torch.float64


def _basis(seed: int, dimension: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    orthogonal, _ = torch.linalg.qr(torch.randn(dimension, dimension, generator=generator, dtype=DTYPE))
    scales = torch.linspace(0.8, 1.4, dimension, dtype=DTYPE)
    return orthogonal @ torch.diag(scales)


def _ambient_operators(
    basis: torch.Tensor,
    permutations: torch.Tensor,
    scales: torch.Tensor,
) -> torch.Tensor:
    semantic = permutations @ torch.diag_embed(scales)
    return basis @ semantic @ torch.linalg.inv(basis)


def test_column_permutation_matrix_uses_source_to_target_convention() -> None:
    mapping = torch.tensor([[1, 2, 0], [2, 1, 0]])
    matrix = column_permutation_matrix(mapping, dtype=DTYPE)
    sources = torch.eye(3, dtype=DTYPE).expand(2, -1, -1)
    observed = matrix @ sources
    for episode in range(2):
        for source in range(3):
            assert int(observed[episode, :, source].argmax()) == int(mapping[episode, source])

    with pytest.raises(ValueError, match="finite integers"):
        column_permutation_matrix(torch.tensor([1.9, 0.0, 2.0]), dtype=DTYPE)


def test_exact_statewise_monomial_action_is_recovered() -> None:
    basis = _basis(3, 4)
    maps = torch.tensor([[1, 2, 3, 0], [0, 3, 2, 1]])
    permutations = column_permutation_matrix(maps, dtype=DTYPE)
    scales = torch.tensor([[0.5, 1.0, 2.0, 4.0], [1.25, 0.75, 3.0, 1.5]], dtype=DTYPE)
    operators = _ambient_operators(basis, permutations, scales)

    fit = decompose_operator_gauge(basis, operators, maps)

    assert torch.all(fit.projectively_valid)
    assert torch.allclose(fit.state_scales, scales, atol=2e-12, rtol=2e-12)
    assert torch.allclose(fit.semantic_leakage, torch.zeros_like(fit.semantic_leakage), atol=3e-12)
    assert torch.allclose(fit.ambient_skeleton, operators, atol=3e-12, rtol=3e-12)
    assert float(fit.statewise_relative_residual.max()) < 2e-12
    assert float(fit.global_relative_residual.min()) > 0.25


def test_leakage_reconstructs_operator_and_statewise_fit_dominates_global_fit() -> None:
    basis = _basis(5, 4)
    mapping = torch.tensor([1, 2, 3, 0])
    permutation = column_permutation_matrix(mapping, dtype=DTYPE)
    scales = torch.tensor([0.8, 1.1, 1.7, 2.3], dtype=DTYPE)
    leakage = torch.tensor(
        [
            [0.04, -0.02, 0.01, 0.0],
            [0.0, 0.03, -0.01, 0.02],
            [0.02, 0.0, -0.04, 0.01],
            [-0.01, 0.01, 0.0, 0.02],
        ],
        dtype=DTYPE,
    )
    leakage[mapping, torch.arange(4)] = 0.0
    semantic = permutation @ torch.diag(scales) + leakage
    operator = basis @ semantic @ torch.linalg.inv(basis)

    fit = decompose_operator_gauge(basis, operator, permutation)

    assert torch.allclose(fit.semantic_operator, fit.monomial_skeleton + fit.semantic_leakage)
    assert torch.allclose(operator, fit.ambient_skeleton + fit.ambient_leakage)
    assert torch.allclose(fit.semantic_leakage, leakage, atol=2e-12, rtol=2e-12)
    assert float(fit.statewise_relative_residual) < float(fit.global_relative_residual)


def test_nonpositive_target_coefficient_is_reported_and_constrained() -> None:
    basis = torch.eye(3, dtype=DTYPE)
    mapping = torch.tensor([1, 2, 0])
    permutation = column_permutation_matrix(mapping, dtype=DTYPE)
    semantic = permutation @ torch.diag(torch.tensor([1.0, -2.0, 3.0], dtype=DTYPE))

    fit = decompose_operator_gauge(
        basis,
        semantic,
        permutation,
        minimum_positive_scale=1e-5,
    )

    assert fit.projectively_valid.tolist() == [True, False, True]
    assert fit.raw_state_scales.tolist() == [1.0, -2.0, 3.0]
    assert fit.state_scales.tolist() == [1.0, 1e-5, 3.0]


def test_positive_anchor_rescaling_preserves_ambient_skeleton_and_leakage() -> None:
    basis = _basis(7, 4)
    maps = torch.tensor([[1, 2, 3, 0], [2, 3, 0, 1]])
    permutations = column_permutation_matrix(maps, dtype=DTYPE)
    scales = torch.tensor([[0.7, 1.3, 2.1, 0.9], [1.8, 0.6, 1.1, 2.4]], dtype=DTYPE)
    operators = _ambient_operators(basis, permutations, scales)
    operators = operators + 0.002 * torch.eye(4, dtype=DTYPE)
    representative_scaling = torch.tensor([0.2, 3.0, 1.7, 0.6], dtype=DTYPE)

    diagnostic = gauge_rescaling_diagnostic(
        basis,
        operators,
        maps,
        representative_scaling,
    )

    assert not diagnostic.all_projectively_valid
    assert float(diagnostic.scale_covariance_relative_error.max()) < 2e-12
    assert float(diagnostic.ambient_skeleton_relative_error.max()) < 3e-12
    assert float(diagnostic.ambient_leakage_relative_error.max()) < 3e-12


def test_scale_cocycle_is_exact_for_monomial_generators() -> None:
    basis = _basis(11, 4)
    maps = torch.tensor([[1, 2, 3, 0], [0, 3, 2, 1]])
    permutations = column_permutation_matrix(maps, dtype=DTYPE)
    scales = torch.tensor([[0.5, 1.2, 2.0, 0.8], [1.1, 0.9, 1.4, 2.5]], dtype=DTYPE)
    operators = _ambient_operators(basis, permutations, scales)
    word = (0, 1, 0, 0, 1, 1, 0)

    semantic_product, expected_scales = compose_monomial_cocycle(permutations, scales, word)
    diagnostic = cocycle_diagnostic(basis, operators, maps, word)

    assert diagnostic.all_projectively_valid
    assert torch.allclose(diagnostic.semantic_product, semantic_product)
    assert torch.allclose(diagnostic.predicted_state_scales, expected_scales, atol=3e-12, rtol=3e-12)
    assert torch.allclose(diagnostic.fitted_state_scales, expected_scales, atol=3e-12, rtol=3e-12)
    assert float(diagnostic.scale_relative_error) < 3e-12
    assert float(diagnostic.predicted_monomial_relative_residual) < 3e-12
    assert float(diagnostic.fitted_monomial_relative_residual) < 3e-12


def test_loop_diagnostic_separates_statewise_gauge_from_global_scalar() -> None:
    basis = _basis(13, 3)
    mapping = torch.tensor([[1, 0, 2]])
    permutations = column_permutation_matrix(mapping, dtype=DTYPE)
    generator_scales = torch.tensor([[2.0, 3.0, 5.0]], dtype=DTYPE)
    operators = _ambient_operators(basis, permutations, generator_scales)

    loop = loop_scale_diagnostic(basis, operators, mapping, (0, 0), repeats=7)

    assert loop.semantic_identity
    assert loop.projectively_valid
    assert torch.allclose(loop.fitted_state_scales, torch.tensor([6.0, 6.0, 25.0], dtype=DTYPE))
    assert float(loop.statewise_relative_residual) < 2e-12
    assert float(loop.repeated_statewise_relative_residual) < 2e-12
    assert float(loop.global_relative_residual) > 0.4
    assert torch.allclose(loop.repeated_state_scales, loop.fitted_state_scales**7)
    assert torch.allclose(loop.repeated_log_scale_spread, 7 * loop.log_scale_spread)


def test_repeated_loop_diagnostic_fits_full_power_when_leakage_returns() -> None:
    basis = torch.eye(2, dtype=DTYPE)
    mapping = torch.tensor([[0, 1]])
    operator = torch.tensor([[[2.0, 0.2], [0.1, 1.0]]], dtype=DTYPE)

    loop = loop_scale_diagnostic(basis, operator, mapping, (0,), repeats=3)
    powered = torch.linalg.matrix_power(operator[0], 3)

    assert not loop.projectively_valid
    assert torch.allclose(loop.repeated_state_scales, torch.diagonal(powered))
    assert not torch.allclose(loop.repeated_state_scales, loop.fitted_state_scales**3)
    expected_spread = torch.diagonal(powered).log().max() - torch.diagonal(powered).log().min()
    assert torch.allclose(loop.repeated_log_scale_spread, expected_spread)


def test_closed_loop_scales_are_invariant_under_anchor_gauge_rescaling() -> None:
    basis = _basis(17, 3)
    mapping = torch.tensor([[1, 0, 2]])
    permutations = column_permutation_matrix(mapping, dtype=DTYPE)
    scales = torch.tensor([[2.0, 3.0, 5.0]], dtype=DTYPE)
    operators = _ambient_operators(basis, permutations, scales)
    representative_scaling = torch.tensor([0.1, 4.0, 1.7], dtype=DTYPE)

    transformed = transform_state_scales_under_anchor_gauge(
        scales,
        permutations,
        representative_scaling,
    )
    expected = scales * representative_scaling / representative_scaling[mapping]
    assert torch.allclose(transformed, expected)

    original_loop = loop_scale_diagnostic(basis, operators, mapping, (0, 0), repeats=5)
    rescaled_loop = loop_scale_diagnostic(
        rescale_anchor_basis(basis, representative_scaling),
        operators,
        mapping,
        (0, 0),
        repeats=5,
    )
    assert torch.allclose(
        original_loop.fitted_state_scales,
        rescaled_loop.fitted_state_scales,
        atol=2e-12,
        rtol=2e-12,
    )
    assert torch.allclose(
        original_loop.repeated_log_scale_spread,
        rescaled_loop.repeated_log_scale_spread,
        atol=2e-12,
        rtol=2e-12,
    )


def test_active_floor_preserves_raw_covariance_but_not_clamped_skeleton() -> None:
    basis = torch.eye(2, dtype=DTYPE)
    mapping = torch.tensor([1, 0])
    permutation = column_permutation_matrix(mapping, dtype=DTYPE)
    operator = permutation @ torch.diag(torch.tensor([1e-6, 2.0], dtype=DTYPE))

    diagnostic = gauge_rescaling_diagnostic(
        basis,
        operator,
        permutation,
        torch.tensor([10.0, 0.1], dtype=DTYPE),
        minimum_positive_scale=1e-3,
    )

    assert float(diagnostic.scale_covariance_relative_error) < 1e-14
    assert float(diagnostic.ambient_skeleton_relative_error) > 1e-5
    assert not diagnostic.all_projectively_valid


def test_positive_even_loop_does_not_hide_negative_generator_scale() -> None:
    basis = torch.eye(2, dtype=DTYPE)
    mapping = torch.tensor([[1, 0]])
    permutation = column_permutation_matrix(mapping, dtype=DTYPE)
    operator = -permutation

    loop = loop_scale_diagnostic(basis, operator, mapping, (0, 0))

    assert torch.all(loop.fitted_state_scales > 0)
    assert not loop.projectively_valid


def test_semantic_coordinates_reject_singular_anchor_basis() -> None:
    singular = torch.tensor([[1.0, 0.0], [2.0, 0.0]], dtype=DTYPE)
    with pytest.raises(ValueError, match="invertible"):
        semantic_coordinates(singular, torch.eye(2, dtype=DTYPE))

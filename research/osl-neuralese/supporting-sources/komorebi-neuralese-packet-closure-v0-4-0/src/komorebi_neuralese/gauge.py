from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import torch


@dataclass(frozen=True)
class GaugeDecomposition:
    """Monomial-plus-leakage decomposition in an anchor chart.

    The permutation convention is column acting: ``P[:, i]`` is the one-hot
    target of source state ``i``.  Consequently the projectively exact model
    is ``P @ diag(lambda)`` and ``lambda[i]`` is the positive scale attached
    to source state ``i``.

    Semantic-coordinate residuals depend on the normalization chosen for the
    anchor columns.  The reconstructed ambient skeleton and ambient leakage do
    not when the positivity floor is inactive.
    """

    semantic_operator: torch.Tensor
    permutation: torch.Tensor
    raw_state_scales: torch.Tensor
    state_scales: torch.Tensor
    projectively_valid: torch.Tensor
    monomial_skeleton: torch.Tensor
    semantic_leakage: torch.Tensor
    ambient_skeleton: torch.Tensor
    ambient_leakage: torch.Tensor
    global_scale: torch.Tensor
    global_skeleton: torch.Tensor
    statewise_relative_residual: torch.Tensor
    global_relative_residual: torch.Tensor
    ambient_statewise_relative_residual: torch.Tensor
    ambient_global_relative_residual: torch.Tensor


@dataclass(frozen=True)
class CocycleDiagnostic:
    """Agreement between generator gauges and a directly fitted word gauge."""

    word: tuple[int, ...]
    semantic_product: torch.Tensor
    predicted_state_scales: torch.Tensor
    fitted_state_scales: torch.Tensor
    all_projectively_valid: bool
    scale_relative_error: torch.Tensor
    log_scale_rms_error: torch.Tensor
    log_scale_max_error: torch.Tensor
    predicted_monomial_relative_residual: torch.Tensor
    fitted_monomial_relative_residual: torch.Tensor


@dataclass(frozen=True)
class LoopScaleDiagnostic:
    """Projective closure and scale accumulation for a semantic loop."""

    word: tuple[int, ...]
    repeats: int
    semantic_identity: bool
    fitted_state_scales: torch.Tensor
    cocycle_predicted_scales: torch.Tensor
    repeated_state_scales: torch.Tensor
    projectively_valid: bool
    statewise_relative_residual: torch.Tensor
    repeated_statewise_relative_residual: torch.Tensor
    global_relative_residual: torch.Tensor
    global_scale: torch.Tensor
    mean_log_scale: torch.Tensor
    log_scale_spread: torch.Tensor
    repeated_log_scale_spread: torch.Tensor
    cocycle_scale_relative_error: torch.Tensor


@dataclass(frozen=True)
class GaugeRescalingDiagnostic:
    """Covariance of a statewise gauge fit under positive anchor rescaling."""

    predicted_rescaled_scales: torch.Tensor
    fitted_rescaled_scales: torch.Tensor
    scale_covariance_relative_error: torch.Tensor
    ambient_skeleton_relative_error: torch.Tensor
    ambient_leakage_relative_error: torch.Tensor
    all_projectively_valid: bool


def _check_anchor_basis(anchor_basis: torch.Tensor) -> int:
    if anchor_basis.ndim != 2 or anchor_basis.shape[0] != anchor_basis.shape[1]:
        raise ValueError("anchor_basis must be a square matrix with anchors in columns")
    if not anchor_basis.is_floating_point():
        raise TypeError("anchor_basis must have a real floating dtype")
    if not torch.isfinite(anchor_basis).all():
        raise ValueError("anchor_basis must be finite")
    try:
        torch.linalg.inv(anchor_basis)
    except RuntimeError as error:
        raise ValueError("anchor_basis must be invertible") from error
    return anchor_basis.shape[0]


def _check_operators(operators: torch.Tensor, dimension: int) -> None:
    if operators.ndim < 2 or operators.shape[-2:] != (dimension, dimension):
        raise ValueError("operators must have shape (..., dimension, dimension)")
    if not operators.is_floating_point():
        raise TypeError("operators must have a real floating dtype")
    if not torch.isfinite(operators).all():
        raise ValueError("operators must be finite")


def column_permutation_matrix(
    source_to_target: torch.Tensor,
    *,
    dtype: torch.dtype | None = None,
    device: torch.device | None = None,
) -> torch.Tensor:
    """Convert maps ``source -> target`` to column-acting permutation matrices."""

    if source_to_target.ndim < 1:
        raise ValueError("source_to_target must have shape (..., dimension)")
    raw_mapping = source_to_target.to(device=device)
    if torch.is_complex(raw_mapping):
        if torch.any(raw_mapping.imag != 0):
            raise ValueError("source_to_target entries must be real integers")
        raw_mapping = raw_mapping.real
    if raw_mapping.is_floating_point():
        if not torch.isfinite(raw_mapping).all() or torch.any(raw_mapping != raw_mapping.round()):
            raise ValueError("source_to_target entries must be finite integers")
        raw_mapping = raw_mapping.round()
    mapping = raw_mapping.to(dtype=torch.long)
    dimension = mapping.shape[-1]
    expected = torch.arange(dimension, device=mapping.device)
    if not torch.equal(torch.sort(mapping, dim=-1).values, expected.expand_as(mapping)):
        raise ValueError("each source_to_target row must be a permutation")
    result_dtype = dtype if dtype is not None else torch.get_default_dtype()
    matrix = torch.zeros(
        *mapping.shape[:-1], dimension, dimension, dtype=result_dtype, device=mapping.device
    )
    source = expected.expand_as(mapping)
    matrix.scatter_(-2, mapping.unsqueeze(-2), torch.ones_like(source, dtype=result_dtype).unsqueeze(-2))
    return matrix


def _coerce_permutations(
    permutations: torch.Tensor,
    leading_shape: torch.Size,
    dimension: int,
    *,
    dtype: torch.dtype,
    device: torch.device,
    tolerance: float,
) -> torch.Tensor:
    matrix_shape = tuple(leading_shape) + (dimension, dimension)
    map_shape = tuple(leading_shape) + (dimension,)
    if tuple(permutations.shape) == map_shape:
        matrix = column_permutation_matrix(permutations, dtype=dtype, device=device)
    elif tuple(permutations.shape) == matrix_shape:
        raw_matrix = permutations.to(device=device)
        if torch.is_complex(raw_matrix):
            if torch.any(raw_matrix.imag.abs() > tolerance):
                raise ValueError("permutation matrices must be real")
            raw_matrix = raw_matrix.real
        if raw_matrix.is_floating_point() and not torch.isfinite(raw_matrix).all():
            raise ValueError("permutation matrices must be finite")
        matrix = raw_matrix.to(dtype=dtype)
    else:
        raise ValueError(
            "permutations must be source-to-target maps with shape "
            f"{map_shape} or matrices with shape {matrix_shape}"
        )

    ones = torch.ones(*leading_shape, dimension, dtype=dtype, device=device)
    entries_valid = torch.all((matrix - matrix.round()).abs() <= tolerance)
    nonnegative = torch.all(matrix >= -tolerance)
    row_valid = torch.allclose(matrix.sum(dim=-1), ones, atol=tolerance, rtol=0.0)
    column_valid = torch.allclose(matrix.sum(dim=-2), ones, atol=tolerance, rtol=0.0)
    if not bool(entries_valid and nonnegative and row_valid and column_valid):
        raise ValueError("permutation matrices must be one-hot with unit row and column sums")
    return matrix


def _positive_floor(reference: torch.Tensor, minimum: float | None) -> float:
    value = float(torch.finfo(reference.dtype).tiny if minimum is None else minimum)
    if value <= 0 or not bool(torch.isfinite(reference.new_tensor(value))):
        raise ValueError("minimum_positive_scale must be strictly positive")
    return value


def _relative_frobenius(residual: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
    numerator = torch.linalg.matrix_norm(residual, ord="fro", dim=(-2, -1))
    denominator = torch.linalg.matrix_norm(reference, ord="fro", dim=(-2, -1))
    tiny = torch.finfo(reference.dtype).tiny
    return numerator / denominator.clamp_min(tiny)


def semantic_coordinates(anchor_basis: torch.Tensor, operators: torch.Tensor) -> torch.Tensor:
    """Return ``B^{-1} M B`` for one operator or any leading batch shape."""

    dimension = _check_anchor_basis(anchor_basis)
    _check_operators(operators, dimension)
    if anchor_basis.device != operators.device:
        raise ValueError("anchor_basis and operators must be on the same device")
    if anchor_basis.dtype != operators.dtype:
        raise ValueError("anchor_basis and operators must have the same dtype")
    inverse = torch.linalg.inv(anchor_basis)
    return inverse @ operators @ anchor_basis


def fit_positive_state_scales(
    semantic_operator: torch.Tensor,
    permutations: torch.Tensor,
    *,
    minimum_positive_scale: float | None = None,
    permutation_tolerance: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Fit ``A ~= P diag(lambda)`` with strictly positive statewise scales.

    Returns the constrained scales, the unconstrained target coefficients,
    and a Boolean mask recording where the positivity floor was inactive.
    """

    if semantic_operator.ndim < 2:
        raise ValueError("semantic_operator must have shape (..., dimension, dimension)")
    dimension = semantic_operator.shape[-1]
    _check_operators(semantic_operator, dimension)
    permutation = _coerce_permutations(
        permutations,
        semantic_operator.shape[:-2],
        dimension,
        dtype=semantic_operator.dtype,
        device=semantic_operator.device,
        tolerance=permutation_tolerance,
    )
    raw = torch.diagonal(permutation.transpose(-1, -2) @ semantic_operator, dim1=-2, dim2=-1)
    floor = _positive_floor(semantic_operator, minimum_positive_scale)
    valid = raw >= floor
    return raw.clamp_min(floor), raw, valid


def decompose_operator_gauge(
    anchor_basis: torch.Tensor,
    operators: torch.Tensor,
    permutations: torch.Tensor,
    *,
    minimum_positive_scale: float | None = None,
    permutation_tolerance: float = 1e-6,
    projective_validity_tolerance: float = 1e-6,
) -> GaugeDecomposition:
    """Decompose operators into a positive monomial skeleton and leakage.

    ``projectively_valid[..., i]`` requires both an unclamped positive target
    coefficient and columnwise leakage no larger than
    ``projective_validity_tolerance``.  It therefore asserts positive-ray
    action on anchor ``i`` to the declared tolerance, not merely a positive
    sign in the intended coordinate.
    """

    if projective_validity_tolerance < 0:
        raise ValueError("projective_validity_tolerance must be nonnegative")

    semantic = semantic_coordinates(anchor_basis, operators)
    dimension = semantic.shape[-1]
    permutation = _coerce_permutations(
        permutations,
        semantic.shape[:-2],
        dimension,
        dtype=semantic.dtype,
        device=semantic.device,
        tolerance=permutation_tolerance,
    )
    scales, raw_scales, constraint_inactive = fit_positive_state_scales(
        semantic,
        permutation,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
    )
    state_diagonal = torch.diag_embed(scales)
    monomial = permutation @ state_diagonal
    semantic_leakage = semantic - monomial
    tiny = torch.finfo(semantic.dtype).tiny
    column_reference = torch.linalg.vector_norm(semantic, dim=-2).clamp_min(tiny)
    column_leakage = torch.linalg.vector_norm(semantic_leakage, dim=-2) / column_reference
    valid = constraint_inactive & (column_leakage <= projective_validity_tolerance)

    raw_global = raw_scales.mean(dim=-1)
    floor = _positive_floor(semantic, minimum_positive_scale)
    global_scale = raw_global.clamp_min(floor)
    global_skeleton = permutation * global_scale[..., None, None]

    inverse = torch.linalg.inv(anchor_basis)
    ambient_skeleton = anchor_basis @ monomial @ inverse
    ambient_leakage = operators - ambient_skeleton
    ambient_global = anchor_basis @ global_skeleton @ inverse

    return GaugeDecomposition(
        semantic_operator=semantic,
        permutation=permutation,
        raw_state_scales=raw_scales,
        state_scales=scales,
        projectively_valid=valid,
        monomial_skeleton=monomial,
        semantic_leakage=semantic_leakage,
        ambient_skeleton=ambient_skeleton,
        ambient_leakage=ambient_leakage,
        global_scale=global_scale,
        global_skeleton=global_skeleton,
        statewise_relative_residual=_relative_frobenius(semantic_leakage, semantic),
        global_relative_residual=_relative_frobenius(semantic - global_skeleton, semantic),
        ambient_statewise_relative_residual=_relative_frobenius(ambient_leakage, operators),
        ambient_global_relative_residual=_relative_frobenius(operators - ambient_global, operators),
    )


def word_product(matrices: torch.Tensor, word: Sequence[int]) -> torch.Tensor:
    """Compose matrices in execution order: ``(a, b)`` returns ``M_b M_a``."""

    if matrices.ndim != 3 or matrices.shape[-2] != matrices.shape[-1]:
        raise ValueError("matrices must have shape (operators, dimension, dimension)")
    result = torch.eye(matrices.shape[-1], dtype=matrices.dtype, device=matrices.device)
    for slot in word:
        index = int(slot)
        if index < 0 or index >= matrices.shape[0]:
            raise IndexError(f"operator index {index} is out of range")
        result = matrices[index] @ result
    return result


def compose_monomial_cocycle(
    permutations: torch.Tensor,
    state_scales: torch.Tensor,
    word: Sequence[int],
    *,
    permutation_tolerance: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Compose source-indexed positive scales using the monomial cocycle law."""

    if state_scales.ndim != 2:
        raise ValueError("state_scales must have shape (operators, dimension)")
    if torch.any(state_scales <= 0) or not torch.isfinite(state_scales).all():
        raise ValueError("state_scales must be strictly positive")
    operator_count, dimension = state_scales.shape
    permutation = _coerce_permutations(
        permutations,
        torch.Size((operator_count,)),
        dimension,
        dtype=state_scales.dtype,
        device=state_scales.device,
        tolerance=permutation_tolerance,
    )
    skeletons = permutation @ torch.diag_embed(state_scales)
    semantic_product = word_product(permutation, word)
    skeleton_product = word_product(skeletons, word)
    cumulative_scales = torch.diagonal(
        semantic_product.transpose(-1, -2) @ skeleton_product, dim1=-2, dim2=-1
    )
    return semantic_product, cumulative_scales


def cocycle_diagnostic(
    anchor_basis: torch.Tensor,
    operators: torch.Tensor,
    permutations: torch.Tensor,
    word: Sequence[int],
    *,
    minimum_positive_scale: float | None = None,
    permutation_tolerance: float = 1e-6,
    projective_validity_tolerance: float = 1e-6,
) -> CocycleDiagnostic:
    """Compare composed generator scales with a direct fit of the full word."""

    if operators.ndim != 3:
        raise ValueError("operators must have shape (operators, dimension, dimension)")
    generator_fit = decompose_operator_gauge(
        anchor_basis,
        operators,
        permutations,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    semantic_product, predicted_scales = compose_monomial_cocycle(
        generator_fit.permutation,
        generator_fit.state_scales,
        word,
        permutation_tolerance=permutation_tolerance,
    )
    composite = word_product(operators, word)
    direct_fit = decompose_operator_gauge(
        anchor_basis,
        composite,
        semantic_product,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    fitted_scales = direct_fit.state_scales
    floor = _positive_floor(fitted_scales, minimum_positive_scale)
    log_error = fitted_scales.clamp_min(floor).log() - predicted_scales.clamp_min(floor).log()
    scale_denominator = torch.linalg.vector_norm(fitted_scales).clamp_min(floor)

    predicted = semantic_product @ torch.diag(predicted_scales)
    predicted_residual = predicted - direct_fit.semantic_operator
    return CocycleDiagnostic(
        word=tuple(int(slot) for slot in word),
        semantic_product=semantic_product,
        predicted_state_scales=predicted_scales,
        fitted_state_scales=fitted_scales,
        all_projectively_valid=bool(
            torch.all(generator_fit.projectively_valid) and torch.all(direct_fit.projectively_valid)
        ),
        scale_relative_error=torch.linalg.vector_norm(fitted_scales - predicted_scales)
        / scale_denominator,
        log_scale_rms_error=log_error.square().mean().sqrt(),
        log_scale_max_error=log_error.abs().max(),
        predicted_monomial_relative_residual=_relative_frobenius(
            predicted_residual, direct_fit.semantic_operator
        ),
        fitted_monomial_relative_residual=direct_fit.statewise_relative_residual,
    )


def loop_scale_diagnostic(
    anchor_basis: torch.Tensor,
    operators: torch.Tensor,
    permutations: torch.Tensor,
    word: Sequence[int],
    *,
    repeats: int = 1,
    require_semantic_identity: bool = True,
    minimum_positive_scale: float | None = None,
    permutation_tolerance: float = 1e-6,
    projective_validity_tolerance: float = 1e-6,
) -> LoopScaleDiagnostic:
    """Diagnose state-dependent scale and leakage accumulated around a loop."""

    if repeats < 1:
        raise ValueError("repeats must be at least one")
    cocycle = cocycle_diagnostic(
        anchor_basis,
        operators,
        permutations,
        word,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    identity = torch.eye(
        cocycle.semantic_product.shape[-1],
        dtype=cocycle.semantic_product.dtype,
        device=cocycle.semantic_product.device,
    )
    semantic_identity = torch.allclose(
        cocycle.semantic_product, identity, atol=permutation_tolerance, rtol=0.0
    )
    if require_semantic_identity and not semantic_identity:
        raise ValueError("word is not a semantic loop")

    composite = word_product(operators, word)
    direct_fit = decompose_operator_gauge(
        anchor_basis,
        composite,
        cocycle.semantic_product,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    floor = _positive_floor(direct_fit.state_scales, minimum_positive_scale)
    log_scales = direct_fit.state_scales.clamp_min(floor).log()
    spread = log_scales.max() - log_scales.min()

    repeated_composite = torch.linalg.matrix_power(composite, repeats)
    repeated_semantic_product = torch.linalg.matrix_power(cocycle.semantic_product, repeats)
    repeated_fit = decompose_operator_gauge(
        anchor_basis,
        repeated_composite,
        repeated_semantic_product,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    repeated_log_scales = repeated_fit.state_scales.clamp_min(floor).log()
    return LoopScaleDiagnostic(
        word=tuple(int(slot) for slot in word),
        repeats=repeats,
        semantic_identity=semantic_identity,
        fitted_state_scales=direct_fit.state_scales,
        cocycle_predicted_scales=cocycle.predicted_state_scales,
        repeated_state_scales=repeated_fit.state_scales,
        projectively_valid=bool(
            cocycle.all_projectively_valid
            and torch.all(direct_fit.projectively_valid)
            and torch.all(repeated_fit.projectively_valid)
        ),
        statewise_relative_residual=direct_fit.statewise_relative_residual,
        repeated_statewise_relative_residual=repeated_fit.statewise_relative_residual,
        global_relative_residual=direct_fit.global_relative_residual,
        global_scale=direct_fit.global_scale,
        mean_log_scale=log_scales.mean(),
        log_scale_spread=spread,
        repeated_log_scale_spread=repeated_log_scales.max() - repeated_log_scales.min(),
        cocycle_scale_relative_error=cocycle.scale_relative_error,
    )


def rescale_anchor_basis(anchor_basis: torch.Tensor, positive_scaling: torch.Tensor) -> torch.Tensor:
    """Choose different positive representatives for the same anchor rays."""

    dimension = _check_anchor_basis(anchor_basis)
    if positive_scaling.shape != (dimension,):
        raise ValueError(f"positive_scaling must have shape ({dimension},)")
    raw_scaling = positive_scaling.to(device=anchor_basis.device)
    if torch.is_complex(raw_scaling):
        if torch.any(raw_scaling.imag != 0):
            raise ValueError("positive_scaling must be real and strictly positive")
        raw_scaling = raw_scaling.real
    scaling = raw_scaling.to(dtype=anchor_basis.dtype)
    if torch.any(scaling <= 0) or not torch.isfinite(scaling).all():
        raise ValueError("positive_scaling must be real and strictly positive")
    return anchor_basis @ torch.diag(scaling)


def transform_state_scales_under_anchor_gauge(
    state_scales: torch.Tensor,
    permutations: torch.Tensor,
    positive_scaling: torch.Tensor,
    *,
    permutation_tolerance: float = 1e-6,
) -> torch.Tensor:
    """Apply ``lambda'_i=lambda_i d_i/d_{p(i)}`` for ``B' = B diag(d)``."""

    dimension = state_scales.shape[-1]
    leading = state_scales.shape[:-1]
    raw_scaling = positive_scaling.to(device=state_scales.device)
    if torch.is_complex(raw_scaling):
        if torch.any(raw_scaling.imag != 0):
            raise ValueError("positive_scaling must be a strictly positive dimension-vector")
        raw_scaling = raw_scaling.real
    scaling = raw_scaling.to(dtype=state_scales.dtype)
    if (
        scaling.shape != (dimension,)
        or torch.any(scaling <= 0)
        or not torch.isfinite(scaling).all()
    ):
        raise ValueError("positive_scaling must be a strictly positive dimension-vector")
    permutation = _coerce_permutations(
        permutations,
        leading,
        dimension,
        dtype=state_scales.dtype,
        device=state_scales.device,
        tolerance=permutation_tolerance,
    )
    target_scaling = (permutation.transpose(-1, -2) @ scaling.unsqueeze(-1)).squeeze(-1)
    return state_scales * scaling / target_scaling


def gauge_rescaling_diagnostic(
    anchor_basis: torch.Tensor,
    operators: torch.Tensor,
    permutations: torch.Tensor,
    positive_scaling: torch.Tensor,
    *,
    minimum_positive_scale: float | None = None,
    permutation_tolerance: float = 1e-6,
    projective_validity_tolerance: float = 1e-6,
) -> GaugeRescalingDiagnostic:
    """Check covariance and ambient invariance under ``B -> B diag(d)``."""

    original = decompose_operator_gauge(
        anchor_basis,
        operators,
        permutations,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    rescaled_basis = rescale_anchor_basis(anchor_basis, positive_scaling)
    rescaled = decompose_operator_gauge(
        rescaled_basis,
        operators,
        permutations,
        minimum_positive_scale=minimum_positive_scale,
        permutation_tolerance=permutation_tolerance,
        projective_validity_tolerance=projective_validity_tolerance,
    )
    predicted = transform_state_scales_under_anchor_gauge(
        original.raw_state_scales,
        original.permutation,
        positive_scaling,
        permutation_tolerance=permutation_tolerance,
    )
    floor = _positive_floor(predicted, minimum_positive_scale)
    scale_error = torch.linalg.vector_norm(rescaled.raw_state_scales - predicted, dim=-1)
    scale_reference = torch.linalg.vector_norm(predicted, dim=-1).clamp_min(floor)
    return GaugeRescalingDiagnostic(
        predicted_rescaled_scales=predicted,
        fitted_rescaled_scales=rescaled.raw_state_scales,
        scale_covariance_relative_error=scale_error / scale_reference,
        ambient_skeleton_relative_error=_relative_frobenius(
            rescaled.ambient_skeleton - original.ambient_skeleton,
            original.ambient_skeleton,
        ),
        ambient_leakage_relative_error=_relative_frobenius(
            rescaled.ambient_leakage - original.ambient_leakage,
            operators,
        ),
        all_projectively_valid=bool(
            torch.all(original.projectively_valid) and torch.all(rescaled.projectively_valid)
        ),
    )

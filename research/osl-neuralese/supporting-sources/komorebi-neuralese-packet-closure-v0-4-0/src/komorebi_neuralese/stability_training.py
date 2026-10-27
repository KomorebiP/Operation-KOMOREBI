"""Coordinate-aware training losses for ambient packet closure.

The losses in this module control geometry that per-step projective
normalization does not control by itself.  They are deliberately expressed in
an explicit positive-definite metric ``G``:

* anchor conditioning prevents the learned state anchors from collapsing;
* conformal defect measures angular distortion while quotienting harmless
  scalar operator gain;
* switched tangent gain controls products of normalized-map Jacobians rather
  than generator spectral radii;
* exact ``G``-orthogonal anchor projectors expose whether an alleged ambient
  complement actually exists; and
* Feshbach blocks identify departure from, motion within, and return to the
  anchor plane.

All operator conventions use column states.  If coordinates change by
``x' = C x``, operators and metrics must transform as
``M' = C M C^-1`` and ``G' = C^-T G C^-1``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch


@dataclass(frozen=True)
class MetricConditionDiagnostics:
    """Spectral diagnostics for one metric or a batch of metrics."""

    eigenvalues: torch.Tensor
    relative_eigenvalues: torch.Tensor
    minimum_eigenvalue: torch.Tensor
    maximum_eigenvalue: torch.Tensor
    minimum_relative_eigenvalue: torch.Tensor
    condition_number: torch.Tensor
    log_condition_number: torch.Tensor
    determinant: torch.Tensor
    positive_definite: torch.Tensor


@dataclass(frozen=True)
class MetricConditioningResult:
    """Scale-free metric barrier and condition-number hinge."""

    loss: torch.Tensor
    near_zero_loss: torch.Tensor
    condition_hinge_loss: torch.Tensor
    diagnostics: MetricConditionDiagnostics


@dataclass(frozen=True)
class AnchorGramConditioningResult:
    """Conditioning loss for the metric Gram matrix of state anchors."""

    loss: torch.Tensor
    per_example_loss: torch.Tensor
    isotropy_loss: torch.Tensor
    near_zero_loss: torch.Tensor
    gram: torch.Tensor
    active_eigenvalues: torch.Tensor
    relative_eigenvalues: torch.Tensor
    condition_number: torch.Tensor
    numerical_rank: torch.Tensor


@dataclass(frozen=True)
class ConformalDefectResult:
    """Scale-free ``G``-conformal defect with an optional zero-map barrier."""

    loss: torch.Tensor
    per_operator_loss: torch.Tensor
    defect: torch.Tensor
    near_zero_loss: torch.Tensor
    metric_frobenius_norm: torch.Tensor
    normalized_right_gram: torch.Tensor


@dataclass(frozen=True)
class SwitchedTangentGainResult:
    """Differentiable prefix gains for supplied switched operator words."""

    loss: torch.Tensor
    per_word_loss: torch.Tensor
    prefix_log_gains: torch.Tensor
    prefix_gains: torch.Tensor
    maximum_prefix_log_gain: torch.Tensor
    maximum_prefix_gain: torch.Tensor
    terminal_log_gain: torch.Tensor
    terminal_gain: torch.Tensor
    endpoint: torch.Tensor
    operator_metric_frobenius_norms: torch.Tensor
    near_zero_loss: torch.Tensor


@dataclass(frozen=True)
class AnchorPlaneProjector:
    """Exact ``G``-orthogonal projector onto a supplied anchor span."""

    projector: torch.Tensor
    complement: torch.Tensor
    gram: torch.Tensor
    rank: int
    ambient_dimension: int
    anchor_count: int
    effective_trace: torch.Tensor
    complement_effective_trace: torch.Tensor
    idempotence_error: torch.Tensor
    metric_self_adjoint_error: torch.Tensor


@dataclass(frozen=True)
class FeshbachBlockDiagnostics:
    """Metric-normalized block energies for an operator decomposition."""

    p_to_p: torch.Tensor
    p_to_q: torch.Tensor
    q_to_p: torch.Tensor
    q_to_q: torch.Tensor
    total_energy: torch.Tensor
    p_to_p_energy: torch.Tensor
    p_to_q_energy: torch.Tensor
    q_to_p_energy: torch.Tensor
    q_to_q_energy: torch.Tensor
    p_to_p_fraction: torch.Tensor
    p_to_q_fraction: torch.Tensor
    q_to_p_fraction: torch.Tensor
    q_to_q_fraction: torch.Tensor


@dataclass(frozen=True)
class FeshbachReturnDiagnostics:
    """The return channel ``U_g D_v V_h`` through the anchor complement."""

    u_g: torch.Tensor
    d_v: torch.Tensor
    v_h: torch.Tensor
    return_operator: torch.Tensor
    full_product: torch.Tensor
    return_energy: torch.Tensor
    full_product_energy: torch.Tensor
    full_product_fraction: torch.Tensor
    submultiplicative_fraction: torch.Tensor


def _validate_floating_matrix(tensor: torch.Tensor, name: str) -> int:
    if not isinstance(tensor, torch.Tensor):
        raise TypeError(f"{name} must be a torch.Tensor")
    if tensor.ndim < 2 or tensor.shape[-1] != tensor.shape[-2] or tensor.shape[-1] < 1:
        raise ValueError(f"{name} must end in a nonempty square matrix")
    if not tensor.is_floating_point():
        raise TypeError(f"{name} must have a floating dtype")
    if not bool(torch.isfinite(tensor.detach()).all()):
        raise ValueError(f"{name} must contain only finite values")
    return int(tensor.shape[-1])


def _checked_spd_metric(
    metric: torch.Tensor,
    dimension: int,
    reference: torch.Tensor,
) -> torch.Tensor:
    if not isinstance(metric, torch.Tensor):
        raise TypeError("metric must be a torch.Tensor")
    if metric.ndim < 2 or metric.shape[-2:] != (dimension, dimension):
        raise ValueError("metric must end in (dimension, dimension)")
    if not metric.is_floating_point():
        raise TypeError("metric must have a floating dtype")
    candidate = metric.to(dtype=reference.dtype, device=reference.device)
    detached = candidate.detach()
    if not bool(torch.isfinite(detached).all()):
        raise ValueError("metric must contain only finite values")
    tolerance = 64.0 * torch.finfo(candidate.dtype).eps * dimension
    if not torch.allclose(
        detached,
        detached.transpose(-1, -2),
        atol=tolerance,
        rtol=tolerance,
    ):
        raise ValueError("metric must be symmetric")
    _, info = torch.linalg.cholesky_ex(detached)
    if bool((info != 0).any()):
        raise ValueError("metric must be positive definite")
    return candidate


def _reduce(values: torch.Tensor, reduction: str) -> torch.Tensor:
    if reduction == "none":
        return values
    if reduction == "mean":
        return values.mean()
    if reduction == "sum":
        return values.sum()
    raise ValueError("reduction must be 'none', 'mean', or 'sum'")


def _matrix_metric_chart(metric: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Return ``R, R^-1`` with ``G = R.T @ R``."""

    lower = torch.linalg.cholesky(metric)
    chart = lower.transpose(-1, -2)
    identity = torch.eye(metric.shape[-1], dtype=metric.dtype, device=metric.device)
    inverse = torch.linalg.solve(chart, identity)
    return chart, inverse


def _expand_metric_for_matrices(metric: torch.Tensor, matrices: torch.Tensor) -> torch.Tensor:
    expanded = metric
    while expanded.ndim < matrices.ndim:
        expanded = expanded.unsqueeze(-3)
    try:
        return expanded.expand(matrices.shape[:-2] + matrices.shape[-2:])
    except RuntimeError as error:
        raise ValueError("metric leading dimensions do not broadcast over matrices") from error


def _metric_frobenius_squared(matrices: torch.Tensor, metric: torch.Tensor) -> torch.Tensor:
    expanded_metric = _expand_metric_for_matrices(metric, matrices)
    chart, inverse_chart = _matrix_metric_chart(expanded_metric)
    whitened = chart @ matrices @ inverse_chart
    return whitened.square().sum(dim=(-2, -1))


def metric_condition_diagnostics(
    metric: torch.Tensor,
    *,
    eps: float = 1e-12,
) -> MetricConditionDiagnostics:
    """Report metric conditioning without silently declaring a nullspace.

    Unlike losses that require an SPD metric, this diagnostic remains total
    for a symmetric metric with nonpositive eigenvalues: its condition number
    is then reported as infinity and ``positive_definite`` is false.
    """

    dimension = _validate_floating_matrix(metric, "metric")
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    detached = metric.detach()
    tolerance = 64.0 * torch.finfo(metric.dtype).eps * dimension
    if not torch.allclose(
        detached,
        detached.transpose(-1, -2),
        atol=tolerance,
        rtol=tolerance,
    ):
        raise ValueError("metric must be symmetric")
    eigenvalues = torch.linalg.eigvalsh(0.5 * (metric + metric.transpose(-1, -2)))
    scale = eigenvalues.abs().mean(dim=-1, keepdim=True).clamp_min(eps)
    relative = eigenvalues / scale
    minimum = eigenvalues[..., 0]
    maximum = eigenvalues[..., -1]
    positive = minimum > 0
    safe_minimum = minimum.clamp_min(eps * scale.squeeze(-1))
    raw_condition = maximum / safe_minimum
    infinity = torch.full_like(raw_condition, torch.inf)
    condition = torch.where(positive, raw_condition, infinity)
    log_condition = torch.where(positive, condition.log(), infinity)
    return MetricConditionDiagnostics(
        eigenvalues=eigenvalues,
        relative_eigenvalues=relative,
        minimum_eigenvalue=minimum,
        maximum_eigenvalue=maximum,
        minimum_relative_eigenvalue=relative[..., 0],
        condition_number=condition,
        log_condition_number=log_condition,
        determinant=torch.linalg.det(metric),
        positive_definite=positive,
    )


def metric_conditioning_regularizer(
    metric: torch.Tensor,
    *,
    relative_eigenvalue_floor: float = 0.02,
    maximum_condition: float = 100.0,
    condition_weight: float = 1.0,
    reduction: str = "mean",
    eps: float = 1e-12,
) -> MetricConditioningResult:
    """Penalize near-zero relative metric eigenvalues and excessive condition.

    Both terms are invariant to positive global rescaling of ``metric``.
    """

    if not 0.0 < relative_eigenvalue_floor < 1.0:
        raise ValueError("relative_eigenvalue_floor must lie in (0, 1)")
    if maximum_condition < 1.0 or not math.isfinite(maximum_condition):
        raise ValueError("maximum_condition must be finite and at least one")
    if condition_weight < 0.0 or not math.isfinite(condition_weight):
        raise ValueError("condition_weight must be finite and nonnegative")
    diagnostics = metric_condition_diagnostics(metric, eps=eps)
    relative_minimum = diagnostics.minimum_relative_eigenvalue
    near_zero_per = (
        torch.relu(relative_eigenvalue_floor - relative_minimum)
        / relative_eigenvalue_floor
    ).square()
    # Clamp only for the differentiable loss. The un-clamped diagnostic still
    # fails closed with infinity for a non-SPD metric.
    safe_condition = diagnostics.maximum_eigenvalue.clamp_min(eps) / (
        diagnostics.minimum_eigenvalue.clamp_min(eps)
    )
    condition_per = torch.relu(
        safe_condition.log() - math.log(maximum_condition)
    ).square()
    per_metric = near_zero_per + float(condition_weight) * condition_per
    return MetricConditioningResult(
        loss=_reduce(per_metric, reduction),
        near_zero_loss=_reduce(near_zero_per, reduction),
        condition_hinge_loss=_reduce(condition_per, reduction),
        diagnostics=diagnostics,
    )


def anchor_gram_conditioning_loss(
    anchors: torch.Tensor,
    metric: torch.Tensor,
    *,
    relative_eigenvalue_floor: float = 0.02,
    near_zero_weight: float = 1.0,
    reduction: str = "mean",
    eps: float = 1e-12,
) -> AnchorGramConditioningResult:
    """Make the anchor frame well-conditioned in the learned metric.

    ``anchors`` has shape ``(..., anchor_count, dimension)``.  The nonzero
    spectrum of ``A G A.T`` is coordinate invariant and is normalized by its
    mean, so this loss is also insensitive to a global positive rescaling of
    either anchors or metric.  Both an undercomplete independent frame
    (notably eight anchors in a 12-dimensional ambient space) and an
    overcomplete tight frame are supported.
    """

    if not isinstance(anchors, torch.Tensor) or anchors.ndim < 2:
        raise TypeError("anchors must be a torch.Tensor with at least two dimensions")
    if not anchors.is_floating_point():
        raise TypeError("anchors must have a floating dtype")
    if not bool(torch.isfinite(anchors.detach()).all()):
        raise ValueError("anchors must contain only finite values")
    dimension = int(anchors.shape[-1])
    anchor_count = int(anchors.shape[-2])
    checked_metric = _checked_spd_metric(metric, dimension, anchors)
    if not 0.0 < relative_eigenvalue_floor < 1.0:
        raise ValueError("relative_eigenvalue_floor must lie in (0, 1)")
    if near_zero_weight < 0.0 or not math.isfinite(near_zero_weight):
        raise ValueError("near_zero_weight must be finite and nonnegative")
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")

    gram = anchors @ checked_metric @ anchors.transpose(-1, -2)
    gram = 0.5 * (gram + gram.transpose(-1, -2))
    eigenvalues = torch.linalg.eigvalsh(gram)
    active_count = min(anchor_count, dimension)
    active = eigenvalues[..., -active_count:]
    mean = active.mean(dim=-1, keepdim=True).clamp_min(eps)
    relative = active / mean
    safe_relative = relative.clamp_min(eps)
    centered_log = safe_relative.log() - safe_relative.log().mean(
        dim=-1, keepdim=True
    )
    isotropy_per = centered_log.square().mean(dim=-1)
    near_zero_per = (
        torch.relu(relative_eigenvalue_floor - relative)
        / relative_eigenvalue_floor
    ).square().mean(dim=-1)
    per_example = isotropy_per + float(near_zero_weight) * near_zero_per
    tolerance = max(anchor_count, dimension) * torch.finfo(anchors.dtype).eps
    numerical_rank = (active > active[..., -1:].clamp_min(eps) * tolerance).sum(dim=-1)
    condition = active[..., -1] / active[..., 0].clamp_min(eps * mean.squeeze(-1))
    return AnchorGramConditioningResult(
        loss=_reduce(per_example, reduction),
        per_example_loss=per_example,
        isotropy_loss=_reduce(isotropy_per, reduction),
        near_zero_loss=_reduce(near_zero_per, reduction),
        gram=gram,
        active_eigenvalues=active,
        relative_eigenvalues=relative,
        condition_number=condition,
        numerical_rank=numerical_rank,
    )


def scale_free_conformal_defect(
    operators: torch.Tensor,
    metric: torch.Tensor,
    *,
    minimum_metric_frobenius_norm: float = 0.10,
    near_zero_weight: float = 0.0,
    reduction: str = "mean",
    eps: float = 1e-12,
) -> ConformalDefectResult:
    """Measure ``M.T G M = alpha G`` up to harmless operator scale.

    More precisely, each operator is moved into a metric-orthonormal chart and
    divided by its metric Frobenius norm.  Its right Gram matrix should then be
    ``I / dimension``.  The defect is exactly invariant to any nonzero scalar
    multiplying an operator (away from the explicit numerical zero barrier).
    """

    dimension = _validate_floating_matrix(operators, "operators")
    checked_metric = _checked_spd_metric(metric, dimension, operators)
    if minimum_metric_frobenius_norm <= 0.0 or not math.isfinite(
        minimum_metric_frobenius_norm
    ):
        raise ValueError("minimum_metric_frobenius_norm must be finite and positive")
    if near_zero_weight < 0.0 or not math.isfinite(near_zero_weight):
        raise ValueError("near_zero_weight must be finite and nonnegative")
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")

    expanded_metric = _expand_metric_for_matrices(checked_metric, operators)
    chart, inverse_chart = _matrix_metric_chart(expanded_metric)
    whitened = chart @ operators @ inverse_chart
    norms = torch.linalg.vector_norm(whitened, dim=(-2, -1))
    normalized = whitened / norms.clamp_min(eps)[..., None, None]
    right_gram = normalized.transpose(-1, -2) @ normalized
    identity = torch.eye(dimension, dtype=operators.dtype, device=operators.device)
    defect = dimension * (
        right_gram - identity / dimension
    ).square().sum(dim=(-2, -1))
    near_zero = (
        torch.relu(minimum_metric_frobenius_norm - norms)
        / minimum_metric_frobenius_norm
    ).square()
    per_operator = defect + float(near_zero_weight) * near_zero
    return ConformalDefectResult(
        loss=_reduce(per_operator, reduction),
        per_operator_loss=per_operator,
        defect=defect,
        near_zero_loss=near_zero,
        metric_frobenius_norm=norms,
        normalized_right_gram=right_gram,
    )


def switched_projective_tangent_gain_hinge(
    operator_words: torch.Tensor,
    initial_states: torch.Tensor,
    metric: torch.Tensor,
    *,
    maximum_gain: float = 2.0,
    minimum_metric_frobenius_norm: float = 0.10,
    near_zero_weight: float = 0.0,
    reduction: str = "mean",
    eps: float = 1e-12,
) -> SwitchedTangentGainResult:
    """Penalize transient projective tangent gain along supplied words.

    ``operator_words`` has shape ``(..., steps, d, d)`` and
    ``initial_states`` has broadcast-compatible shape ``(..., d)``.  A hinge
    is applied to the *maximum prefix log gain*, so amplification cannot be
    hidden by later contraction.  Products are renormalized in their metric
    Frobenius norm while a differentiable log scale is accumulated.
    """

    dimension = _validate_floating_matrix(operator_words, "operator_words")
    if operator_words.ndim < 3 or operator_words.shape[-3] < 1:
        raise ValueError("operator_words must contain at least one step")
    if not isinstance(initial_states, torch.Tensor) or initial_states.ndim < 1:
        raise TypeError("initial_states must be a torch.Tensor")
    if not initial_states.is_floating_point() or initial_states.shape[-1] != dimension:
        raise ValueError("initial_states must be floating and end in the operator dimension")
    if not bool(torch.isfinite(initial_states.detach()).all()):
        raise ValueError("initial_states must contain only finite values")
    if maximum_gain <= 0.0 or not math.isfinite(maximum_gain):
        raise ValueError("maximum_gain must be finite and positive")
    if minimum_metric_frobenius_norm <= 0.0 or not math.isfinite(
        minimum_metric_frobenius_norm
    ):
        raise ValueError("minimum_metric_frobenius_norm must be finite and positive")
    if near_zero_weight < 0.0 or not math.isfinite(near_zero_weight):
        raise ValueError("near_zero_weight must be finite and nonnegative")
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")

    checked_metric = _checked_spd_metric(metric, dimension, operator_words)
    try:
        batch_shape = torch.broadcast_shapes(
            operator_words.shape[:-3],
            initial_states.shape[:-1],
            checked_metric.shape[:-2],
        )
    except RuntimeError as error:
        raise ValueError("operator, state, and metric batches are not broadcast-compatible") from error
    steps = int(operator_words.shape[-3])
    operators = operator_words.expand(batch_shape + (steps, dimension, dimension))
    states = initial_states.to(
        dtype=operator_words.dtype, device=operator_words.device
    ).expand(batch_shape + (dimension,))
    expanded_metric = checked_metric.expand(batch_shape + (dimension, dimension))
    chart, inverse_chart = _matrix_metric_chart(expanded_metric)

    def vector_norm(vector: torch.Tensor) -> torch.Tensor:
        squared = (
            vector.unsqueeze(-2) @ expanded_metric @ vector.unsqueeze(-1)
        ).squeeze(-1).squeeze(-1)
        return squared.clamp_min(0.0).sqrt()

    state_norm = vector_norm(states)
    current = states / state_norm.clamp_min(eps).unsqueeze(-1)
    identity = torch.eye(
        dimension, dtype=operator_words.dtype, device=operator_words.device
    ).expand(batch_shape + (dimension, dimension))
    mantissa = identity
    accumulated_log_scale = torch.zeros(
        batch_shape, dtype=operator_words.dtype, device=operator_words.device
    )
    prefix_logs: list[torch.Tensor] = []
    operator_norms: list[torch.Tensor] = []

    for operator in operators.unbind(dim=-3):
        whitened_operator = chart @ operator @ inverse_chart
        operator_norm = torch.linalg.vector_norm(whitened_operator, dim=(-2, -1))
        operator_norms.append(operator_norm)
        scaled_operator = operator / operator_norm.clamp_min(eps)[..., None, None]
        raw_endpoint = (scaled_operator @ current.unsqueeze(-1)).squeeze(-1)
        radius = vector_norm(raw_endpoint)
        endpoint = raw_endpoint / radius.clamp_min(eps).unsqueeze(-1)
        endpoint_covector = (
            expanded_metric @ endpoint.unsqueeze(-1)
        ).squeeze(-1)
        projector = identity - endpoint.unsqueeze(-1) @ endpoint_covector.unsqueeze(-2)
        jacobian = projector @ scaled_operator / radius.clamp_min(eps)[..., None, None]

        candidate = jacobian @ mantissa
        candidate_whitened = chart @ candidate @ inverse_chart
        candidate_scale = torch.linalg.vector_norm(
            candidate_whitened, dim=(-2, -1)
        )
        mantissa = candidate / candidate_scale.clamp_min(eps)[..., None, None]
        accumulated_log_scale = accumulated_log_scale + candidate_scale.clamp_min(eps).log()
        whitened_mantissa = chart @ mantissa @ inverse_chart
        largest_singular = torch.linalg.svdvals(whitened_mantissa)[..., 0]
        prefix_logs.append(
            accumulated_log_scale + largest_singular.clamp_min(eps).log()
        )
        current = endpoint

    prefix_log_gains = torch.stack(prefix_logs, dim=-1)
    maximum_prefix_log_gain = prefix_log_gains.max(dim=-1).values
    log_threshold = math.log(maximum_gain)
    gain_hinge = torch.relu(maximum_prefix_log_gain - log_threshold).square()
    norms = torch.stack(operator_norms, dim=-1)
    near_zero_per_step = (
        torch.relu(minimum_metric_frobenius_norm - norms)
        / minimum_metric_frobenius_norm
    ).square()
    near_zero = near_zero_per_step.mean(dim=-1)
    per_word = gain_hinge + float(near_zero_weight) * near_zero
    max_log_value = math.log(torch.finfo(operator_words.dtype).max)
    prefix_gains = torch.exp(prefix_log_gains.clamp(max=max_log_value))
    maximum_prefix_gain = torch.exp(maximum_prefix_log_gain.clamp(max=max_log_value))
    terminal_log_gain = prefix_log_gains[..., -1]
    terminal_gain = torch.exp(terminal_log_gain.clamp(max=max_log_value))
    return SwitchedTangentGainResult(
        loss=_reduce(per_word, reduction),
        per_word_loss=per_word,
        prefix_log_gains=prefix_log_gains,
        prefix_gains=prefix_gains,
        maximum_prefix_log_gain=maximum_prefix_log_gain,
        maximum_prefix_gain=maximum_prefix_gain,
        terminal_log_gain=terminal_log_gain,
        terminal_gain=terminal_gain,
        endpoint=current,
        operator_metric_frobenius_norms=norms,
        near_zero_loss=near_zero,
    )


def g_orthogonal_anchor_projector(
    anchors: torch.Tensor,
    metric: torch.Tensor,
    *,
    rank_tolerance: float | None = None,
) -> AnchorPlaneProjector:
    """Construct ``P=B(B.T G B)^-1 B.T G`` exactly.

    Anchors are supplied as rows with shape ``(anchor_count, dimension)``;
    thus ``B = anchors.T``.  The anchors must be linearly independent.  The
    explicit rank and effective trace make the ``Q=0`` spanning-anchor case
    visible instead of allowing a vacuous complement claim.
    """

    if not isinstance(anchors, torch.Tensor) or anchors.ndim != 2:
        raise TypeError("anchors must be a rank-two torch.Tensor")
    if not anchors.is_floating_point() or anchors.shape[0] < 1 or anchors.shape[1] < 1:
        raise ValueError("anchors must be a nonempty floating matrix")
    if not bool(torch.isfinite(anchors.detach()).all()):
        raise ValueError("anchors must contain only finite values")
    dimension = int(anchors.shape[1])
    anchor_count = int(anchors.shape[0])
    if anchor_count > dimension:
        raise ValueError("an exact anchor basis cannot contain more vectors than dimension")
    checked_metric = _checked_spd_metric(metric, dimension, anchors)
    gram = anchors @ checked_metric @ anchors.transpose(-1, -2)
    gram = 0.5 * (gram + gram.transpose(-1, -2))
    if rank_tolerance is None:
        rank_tolerance = max(anchor_count, dimension) * torch.finfo(anchors.dtype).eps
    if rank_tolerance <= 0.0 or not math.isfinite(rank_tolerance):
        raise ValueError("rank_tolerance must be finite and positive")
    singular_values = torch.linalg.svdvals(gram.detach())
    threshold = float(rank_tolerance) * singular_values.max()
    rank = int((singular_values > threshold).sum().item())
    if rank != anchor_count:
        raise ValueError("anchors must be linearly independent in the supplied metric")
    right = anchors @ checked_metric
    solved = torch.linalg.solve(gram, right)
    projector = anchors.transpose(0, 1) @ solved
    identity = torch.eye(dimension, dtype=anchors.dtype, device=anchors.device)
    complement = identity - projector
    idempotence = torch.linalg.matrix_norm(projector @ projector - projector, ord="fro")
    self_adjoint = torch.linalg.matrix_norm(
        projector.transpose(0, 1) @ checked_metric - checked_metric @ projector,
        ord="fro",
    )
    return AnchorPlaneProjector(
        projector=projector,
        complement=complement,
        gram=gram,
        rank=rank,
        ambient_dimension=dimension,
        anchor_count=anchor_count,
        effective_trace=torch.trace(projector),
        complement_effective_trace=torch.trace(complement),
        idempotence_error=idempotence,
        metric_self_adjoint_error=self_adjoint,
    )


def feshbach_block_diagnostics(
    operators: torch.Tensor,
    anchor_plane: AnchorPlaneProjector,
    metric: torch.Tensor,
    *,
    eps: float = 1e-12,
) -> FeshbachBlockDiagnostics:
    """Decompose supplied operators into exact ``P/Q`` Feshbach blocks."""

    dimension = _validate_floating_matrix(operators, "operators")
    if dimension != anchor_plane.ambient_dimension:
        raise ValueError("operator and anchor-plane dimensions do not match")
    checked_metric = _checked_spd_metric(metric, dimension, operators)
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    p = anchor_plane.projector.to(dtype=operators.dtype, device=operators.device)
    q = anchor_plane.complement.to(dtype=operators.dtype, device=operators.device)
    p_to_p = p @ operators @ p
    p_to_q = q @ operators @ p
    q_to_p = p @ operators @ q
    q_to_q = q @ operators @ q
    total_energy = _metric_frobenius_squared(operators, checked_metric)
    energies = tuple(
        _metric_frobenius_squared(block, checked_metric)
        for block in (p_to_p, p_to_q, q_to_p, q_to_q)
    )
    denominator = total_energy.clamp_min(eps)
    return FeshbachBlockDiagnostics(
        p_to_p=p_to_p,
        p_to_q=p_to_q,
        q_to_p=q_to_p,
        q_to_q=q_to_q,
        total_energy=total_energy,
        p_to_p_energy=energies[0],
        p_to_q_energy=energies[1],
        q_to_p_energy=energies[2],
        q_to_q_energy=energies[3],
        p_to_p_fraction=energies[0] / denominator,
        p_to_q_fraction=energies[1] / denominator,
        q_to_p_fraction=energies[2] / denominator,
        q_to_q_fraction=energies[3] / denominator,
    )


def feshbach_return_diagnostics(
    return_operator_g: torch.Tensor,
    complement_product_v: torch.Tensor,
    departure_operator_h: torch.Tensor,
    anchor_plane: AnchorPlaneProjector,
    metric: torch.Tensor,
    *,
    eps: float = 1e-12,
) -> FeshbachReturnDiagnostics:
    """Measure the exact complement-mediated return ``U_g D_v V_h``.

    ``V_h = Q M_h P`` departs the anchor plane, ``D_v = Q M_v Q``
    propagates inside its complement, and ``U_g = P M_g Q`` returns.  Leading
    operator dimensions may batch supplied generators or word products.
    """

    dimension = _validate_floating_matrix(return_operator_g, "return_operator_g")
    for tensor, name in (
        (complement_product_v, "complement_product_v"),
        (departure_operator_h, "departure_operator_h"),
    ):
        other_dimension = _validate_floating_matrix(tensor, name)
        if other_dimension != dimension:
            raise ValueError("all return-channel operators must have the same dimension")
    if dimension != anchor_plane.ambient_dimension:
        raise ValueError("operators and anchor-plane dimensions do not match")
    checked_metric = _checked_spd_metric(metric, dimension, return_operator_g)
    if eps <= 0.0 or not math.isfinite(eps):
        raise ValueError("eps must be finite and positive")
    p = anchor_plane.projector.to(
        dtype=return_operator_g.dtype, device=return_operator_g.device
    )
    q = anchor_plane.complement.to(
        dtype=return_operator_g.dtype, device=return_operator_g.device
    )
    u_g = p @ return_operator_g @ q
    d_v = q @ complement_product_v @ q
    v_h = q @ departure_operator_h @ p
    return_operator = u_g @ d_v @ v_h
    full_product = return_operator_g @ complement_product_v @ departure_operator_h
    return_energy = _metric_frobenius_squared(return_operator, checked_metric)
    full_energy = _metric_frobenius_squared(full_product, checked_metric)
    u_energy = _metric_frobenius_squared(u_g, checked_metric)
    d_energy = _metric_frobenius_squared(d_v, checked_metric)
    v_energy = _metric_frobenius_squared(v_h, checked_metric)
    return FeshbachReturnDiagnostics(
        u_g=u_g,
        d_v=d_v,
        v_h=v_h,
        return_operator=return_operator,
        full_product=full_product,
        return_energy=return_energy,
        full_product_energy=full_energy,
        full_product_fraction=return_energy / full_energy.clamp_min(eps),
        submultiplicative_fraction=return_energy
        / (u_energy * d_energy * v_energy).clamp_min(eps),
    )


__all__ = [
    "AnchorGramConditioningResult",
    "AnchorPlaneProjector",
    "ConformalDefectResult",
    "FeshbachBlockDiagnostics",
    "FeshbachReturnDiagnostics",
    "MetricConditionDiagnostics",
    "MetricConditioningResult",
    "SwitchedTangentGainResult",
    "anchor_gram_conditioning_loss",
    "feshbach_block_diagnostics",
    "feshbach_return_diagnostics",
    "g_orthogonal_anchor_projector",
    "metric_condition_diagnostics",
    "metric_conditioning_regularizer",
    "scale_free_conformal_defect",
    "switched_projective_tangent_gain_hinge",
]

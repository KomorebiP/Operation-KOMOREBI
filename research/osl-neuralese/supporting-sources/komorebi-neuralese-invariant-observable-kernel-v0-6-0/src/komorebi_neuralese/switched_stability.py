"""Finite-horizon stability diagnostics for switched projective dynamics.

The routines in this module deliberately distinguish raw linear stability
from stability on the positive-ray quotient.  A raw operator may expand or
contract every representative of a ray without changing its projective
action.  Conversely, individually Schur-stable nonnormal operators can have
an unstable switched product.  The relevant local quantity is therefore the
Jacobian of the normalized map and its ordered products along a trajectory.

All public routines operate on a single ambient state.  This keeps the
geometry explicit and makes the diagnostics suitable for independent audit.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import torch


@dataclass(frozen=True)
class SequenceJacobianResult:
    """Ordered projective Jacobian product along a switched trajectory.

    ``jacobian_mantissa`` and ``jacobian_log_scale`` always represent the
    product as ``exp(jacobian_log_scale) * jacobian_mantissa`` (apart from the
    exactly-zero case).  ``jacobian_product`` is supplied when that product is
    representable in the working floating-point dtype and is otherwise
    ``None``.  This avoids silently overflowing a long-horizon audit.
    """

    endpoint: torch.Tensor
    jacobian_product: torch.Tensor | None
    jacobian_mantissa: torch.Tensor
    jacobian_log_scale: float
    worst_singular_amplification: float
    log_worst_singular_amplification: float
    step_worst_singular_amplifications: tuple[float, ...]
    prefix_worst_singular_amplifications: tuple[float, ...]
    prefix_log_worst_singular_amplifications: tuple[float, ...]


@dataclass(frozen=True)
class MarginAmplificationRisk:
    """Conservative first-order packet-boundary risk certificate."""

    margin: float
    worst_singular_amplification: float
    input_radius: float
    propagated_radius_bound: float
    remaining_margin_lower_bound: float
    risk_ratio: float
    certified_safe: bool


@dataclass(frozen=True)
class RelationLoopDriftResult:
    """Positive-projective drift after repeated execution of one loop."""

    initial_state: torch.Tensor
    cycle_states: torch.Tensor
    drift_radians: tuple[float, ...]
    terminal_drift_radians: float
    max_drift_radians: float


@dataclass(frozen=True)
class NonnormalSwitchedCounterexample:
    """A pair of stable generators with an unstable switched product."""

    operators: torch.Tensor
    individual_spectral_radii: tuple[float, float]
    period_product: torch.Tensor
    period_spectral_radius: float
    period_operator_norm: float
    projective_probe_state: torch.Tensor
    projective_worst_amplification: float
    is_counterexample: bool


@dataclass(frozen=True)
class FiniteDifferenceVerification:
    """Analytic-versus-five-point projective Jacobian comparison."""

    analytic_jacobian: torch.Tensor
    finite_difference_jacobian: torch.Tensor
    endpoint: torch.Tensor
    step_size: float
    max_absolute_error: float
    relative_frobenius_error: float
    passed: bool


def _validate_square_operator(operator: torch.Tensor) -> int:
    if operator.ndim != 2 or operator.shape[0] != operator.shape[1]:
        raise ValueError("operator must be a square rank-two tensor")
    if not operator.is_floating_point():
        raise TypeError("operator must have a floating-point dtype")
    return operator.shape[0]


def _coerce_metric(
    metric: torch.Tensor | None,
    dimension: int,
    reference: torch.Tensor,
) -> torch.Tensor | None:
    if metric is None:
        return None
    if metric.shape != (dimension, dimension):
        raise ValueError("metric shape must match the ambient dimension")
    metric = metric.to(dtype=reference.dtype, device=reference.device)
    metric = (metric + metric.transpose(0, 1)) / 2
    eigenvalues = torch.linalg.eigvalsh(metric)
    if not bool(torch.isfinite(eigenvalues).all()) or float(eigenvalues.min().detach()) <= 0:
        raise ValueError("metric must be finite and positive definite")
    return metric


def _metric_factors(metric: torch.Tensor | None, reference: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    dimension = reference.shape[-1]
    if metric is None:
        identity = torch.eye(dimension, dtype=reference.dtype, device=reference.device)
        return identity, identity
    eigenvalues, eigenvectors = torch.linalg.eigh(metric)
    square_root = (eigenvectors * eigenvalues.sqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
    inverse_square_root = (
        eigenvectors * eigenvalues.rsqrt().unsqueeze(0)
    ) @ eigenvectors.transpose(0, 1)
    return square_root, inverse_square_root


def _safe_metric_norm(vector: torch.Tensor, metric: torch.Tensor | None) -> torch.Tensor:
    if metric is None:
        return torch.linalg.vector_norm(vector)
    square_root, _ = _metric_factors(metric, vector)
    return torch.linalg.vector_norm(square_root @ vector)


def _unit_state(state: torch.Tensor, metric: torch.Tensor | None) -> torch.Tensor:
    if state.ndim != 1:
        raise ValueError("state must be a rank-one tensor")
    norm = _safe_metric_norm(state, metric)
    threshold = torch.finfo(state.dtype).tiny**0.5
    if not bool(torch.isfinite(norm)) or float(norm.detach()) <= threshold:
        raise ValueError("projective state must have a finite nonzero norm")
    return state / norm


def _scale_safe_operator(operator: torch.Tensor) -> torch.Tensor:
    """Remove a harmless positive scalar before applying an operator.

    This makes the projective map invariant in practice even for matrices
    multiplied by extremely large or small positive constants.
    """

    scale = operator.abs().max()
    threshold = torch.finfo(operator.dtype).tiny
    if not bool(torch.isfinite(scale)) or float(scale.detach()) <= threshold:
        raise ValueError("operator must contain a finite nonzero entry")
    return operator / scale


def normalized_projective_map(
    operator: torch.Tensor,
    state: torch.Tensor,
    metric: torch.Tensor | None = None,
) -> torch.Tensor:
    """Apply ``operator`` and return the unit representative of its ray.

    Positive rescaling of either the input state or the operator leaves the
    result unchanged up to floating-point roundoff.  The matrix is first
    rescaled by its largest entry to avoid overflow that has no projective
    meaning.
    """

    dimension = _validate_square_operator(operator)
    if state.shape != (dimension,):
        raise ValueError("state shape must match the operator dimension")
    if state.dtype != operator.dtype or state.device != operator.device:
        state = state.to(dtype=operator.dtype, device=operator.device)
    metric = _coerce_metric(metric, dimension, operator)
    unit = _unit_state(state, metric)
    raw_endpoint = _scale_safe_operator(operator) @ unit
    return _unit_state(raw_endpoint, metric)


def normalized_projective_jacobian(
    operator: torch.Tensor,
    state: torch.Tensor,
    metric: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Jacobian of ``x -> normalize_G(M x)`` at the unit ray representative.

    The returned Jacobian acts on ambient perturbations and annihilates the
    radial direction.  It maps the input tangent hyperplane into the tangent
    hyperplane at the returned endpoint.
    """

    dimension = _validate_square_operator(operator)
    if state.shape != (dimension,):
        raise ValueError("state shape must match the operator dimension")
    if state.dtype != operator.dtype or state.device != operator.device:
        state = state.to(dtype=operator.dtype, device=operator.device)
    metric = _coerce_metric(metric, dimension, operator)
    unit = _unit_state(state, metric)
    scaled_operator = _scale_safe_operator(operator)
    raw_endpoint = scaled_operator @ unit
    endpoint_scale = _safe_metric_norm(raw_endpoint, metric)
    threshold = torch.finfo(operator.dtype).tiny**0.5
    if not bool(torch.isfinite(endpoint_scale)) or float(endpoint_scale.detach()) <= threshold:
        raise ValueError("operator maps the state to an undefined projective point")
    endpoint = raw_endpoint / endpoint_scale
    identity = torch.eye(dimension, dtype=operator.dtype, device=operator.device)
    if metric is None:
        endpoint_covector = endpoint
    else:
        endpoint_covector = metric @ endpoint
    output_tangent_projector = identity - endpoint.unsqueeze(1) @ endpoint_covector.unsqueeze(0)
    jacobian = output_tangent_projector @ scaled_operator / endpoint_scale
    return jacobian, endpoint


def _metric_operator_norm(operator: torch.Tensor, metric: torch.Tensor | None) -> torch.Tensor:
    square_root, inverse_square_root = _metric_factors(metric, operator.new_zeros(operator.shape[-1]))
    whitened = square_root @ operator @ inverse_square_root
    return torch.linalg.svdvals(whitened)[0]


def _stable_log_metric_operator_norm(operator: torch.Tensor, metric: torch.Tensor | None) -> float:
    entry_scale = operator.abs().max()
    if float(entry_scale) == 0.0:
        return -math.inf
    normalized = operator / entry_scale
    singular = _metric_operator_norm(normalized, metric)
    if float(singular) == 0.0:
        return -math.inf
    return float(torch.log(entry_scale) + torch.log(singular))


def _materialize_scaled_product(
    mantissa: torch.Tensor,
    log_scale: float,
) -> torch.Tensor | None:
    if log_scale == -math.inf:
        return torch.zeros_like(mantissa)
    finfo = torch.finfo(mantissa.dtype)
    largest = float(mantissa.abs().max())
    if largest == 0.0:
        return torch.zeros_like(mantissa)
    upper = math.log(finfo.max / largest)
    lower = math.log(finfo.tiny / largest)
    if log_scale > upper or log_scale < lower:
        return None
    return mantissa * math.exp(log_scale)


def projective_sequence_jacobian(
    operators: torch.Tensor | Iterable[torch.Tensor],
    state: torch.Tensor,
    metric: torch.Tensor | None = None,
) -> SequenceJacobianResult:
    """Compose normalized-map Jacobians in the actual switching order.

    For a sequence ``[M0, M1, ...]``, the ambient action is
    ``... M1 M0 h`` and the derivative product follows the same order.
    Renormalizing the product after every multiplication provides a stable
    mantissa/log representation for long switched trajectories.
    """

    if isinstance(operators, torch.Tensor):
        if operators.ndim != 3:
            raise ValueError("operators must have shape (steps, dim, dim)")
        sequence = tuple(operators[index] for index in range(operators.shape[0]))
    else:
        sequence = tuple(operators)
    if not sequence:
        if state.ndim != 1 or not state.is_floating_point():
            raise ValueError("state must be a floating-point rank-one tensor")
        dimension = state.shape[0]
        metric = _coerce_metric(metric, dimension, state)
        endpoint = _unit_state(state, metric)
        identity = torch.eye(dimension, dtype=state.dtype, device=state.device)
        return SequenceJacobianResult(
            endpoint=endpoint,
            jacobian_product=identity,
            jacobian_mantissa=identity / math.sqrt(dimension),
            jacobian_log_scale=0.5 * math.log(dimension),
            worst_singular_amplification=1.0,
            log_worst_singular_amplification=0.0,
            step_worst_singular_amplifications=(),
            prefix_worst_singular_amplifications=(),
            prefix_log_worst_singular_amplifications=(),
        )

    dimension = _validate_square_operator(sequence[0])
    reference = sequence[0]
    if state.shape != (dimension,):
        raise ValueError("state shape must match the operator dimension")
    state = state.to(dtype=reference.dtype, device=reference.device)
    metric = _coerce_metric(metric, dimension, reference)
    endpoint = _unit_state(state, metric)

    mantissa = torch.eye(dimension, dtype=reference.dtype, device=reference.device)
    log_scale = 0.0
    step_amplifications: list[float] = []
    prefix_amplifications: list[float] = []
    prefix_log_amplifications: list[float] = []

    for operator in sequence:
        if operator.shape != (dimension, dimension):
            raise ValueError("all operators must have the same square shape")
        operator = operator.to(dtype=reference.dtype, device=reference.device)
        jacobian, endpoint = normalized_projective_jacobian(operator, endpoint, metric)
        step_amplifications.append(float(_metric_operator_norm(jacobian, metric)))

        candidate = jacobian @ mantissa
        candidate_scale = torch.linalg.matrix_norm(candidate, ord="fro")
        if float(candidate_scale) == 0.0:
            mantissa = torch.zeros_like(candidate)
            log_scale = -math.inf
            prefix_log = -math.inf
            prefix_amplification = 0.0
        else:
            mantissa = candidate / candidate_scale
            if log_scale != -math.inf:
                log_scale += float(torch.log(candidate_scale))
            normalized_log_norm = _stable_log_metric_operator_norm(mantissa, metric)
            prefix_log = log_scale + normalized_log_norm
            max_log = math.log(torch.finfo(reference.dtype).max)
            prefix_amplification = math.exp(prefix_log) if prefix_log <= max_log else math.inf
        prefix_log_amplifications.append(prefix_log)
        prefix_amplifications.append(prefix_amplification)

    final_log = prefix_log_amplifications[-1]
    final_amplification = prefix_amplifications[-1]
    product = _materialize_scaled_product(mantissa, log_scale)
    return SequenceJacobianResult(
        endpoint=endpoint,
        jacobian_product=product,
        jacobian_mantissa=mantissa,
        jacobian_log_scale=log_scale,
        worst_singular_amplification=final_amplification,
        log_worst_singular_amplification=final_log,
        step_worst_singular_amplifications=tuple(step_amplifications),
        prefix_worst_singular_amplifications=tuple(prefix_amplifications),
        prefix_log_worst_singular_amplifications=tuple(prefix_log_amplifications),
    )


def normalized_decoder_margin(
    decoder_weight: torch.Tensor,
    state: torch.Tensor,
    target: int,
    metric: torch.Tensor | None = None,
) -> float:
    """Scale-invariant distance to the nearest homogeneous decision plane."""

    if decoder_weight.ndim != 2:
        raise ValueError("decoder_weight must have shape (classes, dim)")
    classes, dimension = decoder_weight.shape
    if not 0 <= target < classes:
        raise ValueError("target must index a decoder row")
    if state.shape != (dimension,):
        raise ValueError("state shape must match decoder width")
    state = state.to(dtype=decoder_weight.dtype, device=decoder_weight.device)
    metric = _coerce_metric(metric, dimension, decoder_weight)
    unit = _unit_state(state, metric)
    contrasts = decoder_weight[target].unsqueeze(0) - decoder_weight
    mask = torch.arange(classes, device=decoder_weight.device) != target
    contrasts = contrasts[mask]
    if metric is None:
        dual_norms = torch.linalg.vector_norm(contrasts, dim=1)
    else:
        inverse_metric = torch.linalg.inv(metric)
        dual_norms = torch.einsum("bi,ij,bj->b", contrasts, inverse_metric, contrasts).clamp_min(0).sqrt()
    if bool((dual_norms <= torch.finfo(decoder_weight.dtype).tiny**0.5).any()):
        raise ValueError("decoder contains indistinguishable class hyperplanes")
    signed_distances = (contrasts @ unit) / dual_norms
    return float(signed_distances.min())


def margin_to_amplification_risk(
    margin: float,
    worst_singular_amplification: float,
    input_radius: float,
) -> MarginAmplificationRisk:
    """Combine a normalized margin with a first-order switched gain bound."""

    if not math.isfinite(margin):
        raise ValueError("margin must be finite")
    if worst_singular_amplification < 0 or math.isnan(worst_singular_amplification):
        raise ValueError("amplification must be nonnegative")
    if input_radius < 0 or not math.isfinite(input_radius):
        raise ValueError("input_radius must be finite and nonnegative")
    propagated = worst_singular_amplification * input_radius
    remaining = margin - propagated
    if margin <= 0:
        ratio = math.inf
    elif propagated == 0:
        ratio = 0.0
    else:
        ratio = propagated / margin
    return MarginAmplificationRisk(
        margin=margin,
        worst_singular_amplification=worst_singular_amplification,
        input_radius=input_radius,
        propagated_radius_bound=propagated,
        remaining_margin_lower_bound=remaining,
        risk_ratio=ratio,
        certified_safe=remaining > 0,
    )


def _stable_projective_angle(
    left: torch.Tensor,
    right: torch.Tensor,
    metric: torch.Tensor | None,
) -> float:
    left = _unit_state(left, metric)
    right = _unit_state(right, metric)
    if metric is None:
        cosine = torch.dot(left, right)
    else:
        cosine = left @ metric @ right
    cosine = cosine.clamp(-1.0, 1.0)
    residual = right - cosine * left
    sine = _safe_metric_norm(residual, metric)
    return float(torch.atan2(sine, cosine))


def relation_loop_repeated_drift(
    loop_operators: torch.Tensor | Iterable[torch.Tensor],
    state: torch.Tensor,
    repeats: int,
    metric: torch.Tensor | None = None,
) -> RelationLoopDriftResult:
    """Measure accumulated ray drift after one relation loop is repeated."""

    if repeats < 1:
        raise ValueError("repeats must be positive")
    if isinstance(loop_operators, torch.Tensor):
        if loop_operators.ndim != 3:
            raise ValueError("loop_operators must have shape (steps, dim, dim)")
        sequence = tuple(loop_operators[index] for index in range(loop_operators.shape[0]))
    else:
        sequence = tuple(loop_operators)
    if not sequence:
        raise ValueError("relation loop must contain at least one operator")
    dimension = _validate_square_operator(sequence[0])
    reference = sequence[0]
    if state.shape != (dimension,):
        raise ValueError("state shape must match the operator dimension")
    metric = _coerce_metric(metric, dimension, reference)
    initial = _unit_state(state.to(dtype=reference.dtype, device=reference.device), metric)
    current = initial
    states: list[torch.Tensor] = []
    drifts: list[float] = []
    for _ in range(repeats):
        for operator in sequence:
            current = normalized_projective_map(operator, current, metric)
        states.append(current)
        drifts.append(_stable_projective_angle(initial, current, metric))
    return RelationLoopDriftResult(
        initial_state=initial,
        cycle_states=torch.stack(states),
        drift_radians=tuple(drifts),
        terminal_drift_radians=drifts[-1],
        max_drift_radians=max(drifts),
    )


def nonnormal_switched_counterexample(
    contraction: float = 0.5,
    shear: float = 1.0,
    dtype: torch.dtype = torch.float64,
) -> NonnormalSwitchedCounterexample:
    """Construct a classic two-generator switched-stability counterexample.

    Both triangular generators have spectral radius ``contraction``.  Their
    alternating product can nevertheless have spectral radius greater than
    one.  The smallest right-singular direction of the period product also
    exposes large projective tangent amplification.
    """

    if not 0 < contraction < 1:
        raise ValueError("contraction must lie strictly between zero and one")
    if shear <= 0 or not math.isfinite(shear):
        raise ValueError("shear must be finite and positive")
    first = torch.tensor([[contraction, shear], [0.0, contraction]], dtype=dtype)
    second = torch.tensor([[contraction, 0.0], [shear, contraction]], dtype=dtype)
    operators = torch.stack((first, second))
    radii = tuple(float(torch.linalg.eigvals(operator).abs().max()) for operator in operators)
    period = second @ first
    period_radius = float(torch.linalg.eigvals(period).abs().max())
    period_norm = float(torch.linalg.svdvals(period)[0])
    _, _, right_h = torch.linalg.svd(period)
    probe = right_h[-1]
    projective = projective_sequence_jacobian(operators, probe)
    is_counterexample = max(radii) < 1.0 and period_radius > 1.0
    return NonnormalSwitchedCounterexample(
        operators=operators,
        individual_spectral_radii=(radii[0], radii[1]),
        period_product=period,
        period_spectral_radius=period_radius,
        period_operator_norm=period_norm,
        projective_probe_state=probe,
        projective_worst_amplification=projective.worst_singular_amplification,
        is_counterexample=is_counterexample,
    )


def verify_projective_jacobian_finite_difference(
    operator: torch.Tensor,
    state: torch.Tensor,
    metric: torch.Tensor | None = None,
    step_size: float | None = None,
    relative_tolerance: float = 2e-8,
) -> FiniteDifferenceVerification:
    """Verify the analytic Jacobian using a stable five-point stencil.

    Inputs are promoted to float64 for the audit.  Operator scale is removed
    inside ``normalized_projective_map``, so a harmless factor such as
    ``1e200`` cannot overflow the finite-difference evaluations.
    """

    dimension = _validate_square_operator(operator)
    if state.shape != (dimension,):
        raise ValueError("state shape must match the operator dimension")
    operator64 = operator.detach().to(dtype=torch.float64)
    state64 = state.detach().to(dtype=torch.float64, device=operator64.device)
    metric64 = None if metric is None else metric.detach().to(dtype=torch.float64, device=operator64.device)
    metric64 = _coerce_metric(metric64, dimension, operator64)
    unit = _unit_state(state64, metric64)
    analytic, endpoint = normalized_projective_jacobian(operator64, unit, metric64)
    if step_size is None:
        step_size = float(torch.finfo(torch.float64).eps ** (1.0 / 5.0))
    if step_size <= 0 or not math.isfinite(step_size):
        raise ValueError("step_size must be finite and positive")

    columns: list[torch.Tensor] = []
    identity = torch.eye(dimension, dtype=torch.float64, device=operator64.device)
    for index in range(dimension):
        direction = identity[:, index]
        minus_two = normalized_projective_map(operator64, unit - 2 * step_size * direction, metric64)
        minus_one = normalized_projective_map(operator64, unit - step_size * direction, metric64)
        plus_one = normalized_projective_map(operator64, unit + step_size * direction, metric64)
        plus_two = normalized_projective_map(operator64, unit + 2 * step_size * direction, metric64)
        derivative = (minus_two - 8 * minus_one + 8 * plus_one - plus_two) / (12 * step_size)
        columns.append(derivative)
    finite_difference = torch.stack(columns, dim=1)
    residual = finite_difference - analytic
    max_absolute = float(residual.abs().max())
    denominator = torch.linalg.matrix_norm(analytic, ord="fro").clamp_min(torch.finfo(torch.float64).tiny)
    relative = float(torch.linalg.matrix_norm(residual, ord="fro") / denominator)
    return FiniteDifferenceVerification(
        analytic_jacobian=analytic,
        finite_difference_jacobian=finite_difference,
        endpoint=endpoint,
        step_size=step_size,
        max_absolute_error=max_absolute,
        relative_frobenius_error=relative,
        passed=relative <= relative_tolerance,
    )

"""Differentiable delayed-return control for projective recurrent operators.

The construction deliberately uses *soft* observability filters.  ``P`` denotes
directions that are more strongly observed in a local context and ``Q = I-P``
denotes the complementary, more weakly observed component.  Neither object is
claimed to be an exact projector or the projector onto an exact nullspace.

Geometry is handled through an ambient-to-Euclidean chart ``y = C x``.  A
positive-definite metric may be supplied instead; a differentiable Cholesky
chart is then constructed such that ``G = C.T @ C``.  Consequently the return
energy is invariant under a change of ambient coordinates when the metric or
chart and observation covectors are transformed with those coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import torch


@dataclass(frozen=True)
class SoftObservabilitySplit:
    """A strictly soft local observability split.

    ``observed`` and ``weakly_observed`` are ambient-space endomorphisms.  The
    corresponding ``*_chart`` tensors are self-adjoint contractions in the
    Euclidean chart.  A positive ``floor`` keeps both filters full rank, so the
    weak component must not be interpreted as an asserted latent nullspace.
    Leading dimensions may index examples, states, or contexts.
    """

    observed: torch.Tensor
    weakly_observed: torch.Tensor
    observed_chart: torch.Tensor
    weakly_observed_chart: torch.Tensor
    gramian_chart: torch.Tensor
    chart: torch.Tensor
    inverse_chart: torch.Tensor
    metric: torch.Tensor
    floor: float


@dataclass(frozen=True)
class ReturnEnergy:
    """Energy carried from a soft ``Q`` component into a later soft ``P``."""

    raw: torch.Tensor
    propagated_weak: torch.Tensor
    fraction: torch.Tensor


@dataclass(frozen=True)
class DelayedReturnResult:
    """Differentiable aggregate and its unreduced per-delay diagnostics."""

    loss: torch.Tensor
    per_delay: torch.Tensor
    raw_per_delay: torch.Tensor
    propagated_weak_per_delay: torch.Tensor
    delays: tuple[int, ...]
    delay_weights: torch.Tensor


def _as_geometry_tensor(value: torch.Tensor, reference: torch.Tensor, name: str) -> torch.Tensor:
    if not isinstance(value, torch.Tensor):
        raise TypeError(f"{name} must be a torch.Tensor")
    if not torch.is_floating_point(value):
        raise TypeError(f"{name} must have a floating dtype")
    return value.to(dtype=reference.dtype, device=reference.device)


def _resolve_chart(
    observation_jacobian: torch.Tensor,
    metric: torch.Tensor | None,
    chart: torch.Tensor | None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    dimension = observation_jacobian.shape[-1]

    supplied_metric: torch.Tensor | None = None
    if metric is not None:
        supplied_metric = _as_geometry_tensor(metric, observation_jacobian, "metric")
        if supplied_metric.shape[-2:] != (dimension, dimension):
            raise ValueError("metric must end in (dimension, dimension)")
        if not torch.allclose(
            supplied_metric.detach(),
            supplied_metric.detach().transpose(-1, -2),
            atol=1e-7,
            rtol=1e-6,
        ):
            raise ValueError("metric must be symmetric")

    if chart is None:
        if supplied_metric is None:
            chart_tensor = torch.eye(
                dimension,
                dtype=observation_jacobian.dtype,
                device=observation_jacobian.device,
            )
        else:
            try:
                # If G = L L^T, then C = L^T obeys G = C^T C.
                chart_tensor = torch.linalg.cholesky(supplied_metric).transpose(-1, -2)
            except RuntimeError as error:
                raise ValueError("metric must be positive definite") from error
    else:
        chart_tensor = _as_geometry_tensor(chart, observation_jacobian, "chart")
        if chart_tensor.shape[-2:] != (dimension, dimension):
            raise ValueError("chart must end in (dimension, dimension)")
        try:
            # This both validates invertibility and produces the inverse needed below.
            inverse_chart = torch.linalg.inv(chart_tensor)
        except RuntimeError as error:
            raise ValueError("chart must be invertible") from error
        induced_metric = chart_tensor.transpose(-1, -2) @ chart_tensor
        if supplied_metric is not None and not torch.allclose(
            induced_metric.detach(), supplied_metric.detach(), atol=1e-7, rtol=1e-5
        ):
            raise ValueError("metric and chart must satisfy metric = chart.T @ chart")
        return chart_tensor, inverse_chart, induced_metric

    try:
        inverse_chart = torch.linalg.inv(chart_tensor)
    except RuntimeError as error:
        raise ValueError("chart derived from metric must be invertible") from error
    induced_metric = chart_tensor.transpose(-1, -2) @ chart_tensor
    return chart_tensor, inverse_chart, induced_metric


def soft_observability_split(
    observation_jacobian: torch.Tensor,
    *,
    metric: torch.Tensor | None = None,
    chart: torch.Tensor | None = None,
    observation_weights: torch.Tensor | None = None,
    threshold: float | torch.Tensor = 1.0,
    floor: float = 1e-4,
) -> SoftObservabilitySplit:
    """Construct a differentiable, context-dependent soft observability split.

    Args:
        observation_jacobian: Local observation or continuation Jacobian with
            shape ``(..., observations, dimension)``.  Leading dimensions can
            represent states or contexts, and no rank assumption is made.
        metric: Optional SPD ambient metric ``G``.  It is converted to a chart
            ``C`` satisfying ``G = C.T @ C``.
        chart: Optional invertible ambient-to-Euclidean chart ``y = C x``.  If
            both ``metric`` and ``chart`` are given, they must be compatible.
        observation_weights: Optional nonnegative row weights with shape
            broadcastable to ``observation_jacobian.shape[:-1]``.
        threshold: Positive soft transition scale for the observability
            Gramian.  This is not a singular-value cutoff.
        floor: Strictly positive spectral floor below one half.  It prevents
            either side of the split from becoming an exact nullspace.

    The chart-space filter is

    ``P = floor I + (1 - 2 floor) H (H + threshold I)^(-1)``,

    where ``H`` is the weighted local observability Gramian.  ``Q = I-P``.
    This rational spectral filter is smooth away from the required positive
    threshold and supports both rank-deficient and full-rank Jacobians.
    """

    if not isinstance(observation_jacobian, torch.Tensor):
        raise TypeError("observation_jacobian must be a torch.Tensor")
    if observation_jacobian.ndim < 2:
        raise ValueError("observation_jacobian must have at least two dimensions")
    if not torch.is_floating_point(observation_jacobian):
        raise TypeError("observation_jacobian must have a floating dtype")
    if observation_jacobian.shape[-2] < 1 or observation_jacobian.shape[-1] < 1:
        raise ValueError("observation_jacobian dimensions must be nonempty")
    if not 0.0 < float(floor) < 0.5:
        raise ValueError("floor must lie strictly between zero and one half")

    threshold_tensor = torch.as_tensor(
        threshold,
        dtype=observation_jacobian.dtype,
        device=observation_jacobian.device,
    )
    if bool(torch.any(threshold_tensor.detach() <= 0)):
        raise ValueError("threshold must be strictly positive")

    chart_tensor, inverse_chart, induced_metric = _resolve_chart(
        observation_jacobian, metric, chart
    )
    jacobian_chart = observation_jacobian @ inverse_chart

    if observation_weights is None:
        weighted_jacobian = jacobian_chart
    else:
        weights = _as_geometry_tensor(
            observation_weights, observation_jacobian, "observation_weights"
        )
        if bool(torch.any(weights.detach() < 0)):
            raise ValueError("observation_weights must be nonnegative")
        try:
            weighted_jacobian = jacobian_chart * weights.unsqueeze(-1)
        except RuntimeError as error:
            raise ValueError(
                "observation_weights must broadcast over observation rows"
            ) from error

    gramian = jacobian_chart.transpose(-1, -2) @ weighted_jacobian
    # Guard against insignificant asymmetric roundoff before the SPD solve.
    gramian = 0.5 * (gramian + gramian.transpose(-1, -2))
    dimension = gramian.shape[-1]
    identity = torch.eye(dimension, dtype=gramian.dtype, device=gramian.device)
    regularized = gramian + threshold_tensor[..., None, None] * identity
    response = torch.linalg.solve(regularized, gramian)
    response = 0.5 * (response + response.transpose(-1, -2))

    observed_chart = float(floor) * identity + (1.0 - 2.0 * float(floor)) * response
    weak_chart = identity - observed_chart
    observed = inverse_chart @ observed_chart @ chart_tensor
    weakly_observed = inverse_chart @ weak_chart @ chart_tensor

    return SoftObservabilitySplit(
        observed=observed,
        weakly_observed=weakly_observed,
        observed_chart=observed_chart,
        weakly_observed_chart=weak_chart,
        gramian_chart=gramian,
        chart=chart_tensor,
        inverse_chart=inverse_chart,
        metric=induced_metric,
        floor=float(floor),
    )


def ordered_prefix_products(operators: torch.Tensor) -> torch.Tensor:
    """Return products ``M[t] ... M[1] M[0]`` for every prefix.

    ``operators`` must have shape ``(..., steps, dimension, dimension)``.  The
    implementation avoids in-place writes so gradients flow through all prefix
    products.
    """

    if not isinstance(operators, torch.Tensor):
        raise TypeError("operators must be a torch.Tensor")
    if operators.ndim < 3:
        raise ValueError("operators must have shape (..., steps, dimension, dimension)")
    if operators.shape[-1] != operators.shape[-2]:
        raise ValueError("operators must be square")
    if operators.shape[-3] < 1:
        raise ValueError("operators must contain at least one step")

    products: list[torch.Tensor] = []
    current: torch.Tensor | None = None
    for operator in operators.unbind(dim=-3):
        current = operator if current is None else operator @ current
        products.append(current)
    return torch.stack(products, dim=-3)


def q_to_p_return_energy(
    product: torch.Tensor,
    start_split: SoftObservabilitySplit,
    end_split: SoftObservabilitySplit,
    *,
    eps: float = 1e-12,
) -> ReturnEnergy:
    """Measure product-level return from start ``Q`` into end ``P``.

    The calculation is performed in the supplied charts:

    ``||P_end C_end A C_start^-1 Q_start||_F^2``.

    The reported fraction divides this by the energy of the propagated soft-Q
    component before applying ``P_end``.  It is therefore invariant to a global
    nonzero rescaling of the product as well as covariant coordinate changes.
    """

    if not isinstance(product, torch.Tensor):
        raise TypeError("product must be a torch.Tensor")
    dimension = start_split.observed.shape[-1]
    if product.shape[-2:] != (dimension, dimension):
        raise ValueError("product and start split dimensions do not match")
    if end_split.observed.shape[-2:] != (dimension, dimension):
        raise ValueError("start and end split dimensions do not match")
    if eps <= 0:
        raise ValueError("eps must be strictly positive")

    product_chart = end_split.chart @ product @ start_split.inverse_chart
    propagated_weak = product_chart @ start_split.weakly_observed_chart
    returned = end_split.observed_chart @ propagated_weak
    raw_energy = returned.square().sum(dim=(-2, -1))
    propagated_energy = propagated_weak.square().sum(dim=(-2, -1))
    fraction = raw_energy / propagated_energy.clamp_min(eps)
    return ReturnEnergy(
        raw=raw_energy,
        propagated_weak=propagated_energy,
        fraction=fraction,
    )


def delayed_return_regularizer(
    operators: torch.Tensor,
    start_split: SoftObservabilitySplit,
    *,
    end_splits: SoftObservabilitySplit | Sequence[SoftObservabilitySplit] | None = None,
    delays: Sequence[int] | None = None,
    minimum_delay: int = 2,
    delay_weights: torch.Tensor | Sequence[float] | None = None,
    normalized: bool = True,
    reduction: str = "mean",
    eps: float = 1e-12,
) -> DelayedReturnResult:
    """Penalize soft-Q to soft-P return across recurrent prefix products.

    ``end_splits`` may be a single shared context or one split per recurrent
    step, enabling state-dependent observability.  Delays are one-indexed:
    delay ``k`` evaluates ``M[k-1] ... M[0]``.  By default the immediate step is
    excluded and every delay from two onward is penalized.

    ``normalized=True`` uses the scale-free return fraction.  ``False`` uses
    raw chart-metric energy; both remain coordinate-covariant when geometry is
    transformed consistently.  The returned per-delay tensors remain attached
    to autograd regardless of reduction.
    """

    products = ordered_prefix_products(operators)
    step_count = int(products.shape[-3])

    if delays is None:
        selected_delays = tuple(range(int(minimum_delay), step_count + 1))
    else:
        selected_delays = tuple(int(delay) for delay in delays)
    if not selected_delays:
        raise ValueError("no delayed products were selected")
    if len(set(selected_delays)) != len(selected_delays):
        raise ValueError("delays must not contain duplicates")
    if any(delay < 1 or delay > step_count for delay in selected_delays):
        raise ValueError("each delay must lie between one and the number of steps")

    if end_splits is None:
        split_sequence: Sequence[SoftObservabilitySplit] | None = None
        shared_end = start_split
    elif isinstance(end_splits, SoftObservabilitySplit):
        split_sequence = None
        shared_end = end_splits
    else:
        split_sequence = tuple(end_splits)
        if len(split_sequence) != step_count:
            raise ValueError("a sequence of end_splits must contain one split per step")
        shared_end = start_split  # Not used, but keeps the branch total.

    fractions: list[torch.Tensor] = []
    raw_energies: list[torch.Tensor] = []
    propagated_energies: list[torch.Tensor] = []
    for delay in selected_delays:
        end_split = shared_end if split_sequence is None else split_sequence[delay - 1]
        energy = q_to_p_return_energy(
            products[..., delay - 1, :, :],
            start_split,
            end_split,
            eps=eps,
        )
        fractions.append(energy.fraction)
        raw_energies.append(energy.raw)
        propagated_energies.append(energy.propagated_weak)

    per_delay_fraction = torch.stack(fractions, dim=-1)
    raw_per_delay = torch.stack(raw_energies, dim=-1)
    propagated_per_delay = torch.stack(propagated_energies, dim=-1)
    selected_energy = per_delay_fraction if normalized else raw_per_delay

    if delay_weights is None:
        weights = torch.ones(
            len(selected_delays), dtype=selected_energy.dtype, device=selected_energy.device
        )
    else:
        weights = torch.as_tensor(
            delay_weights, dtype=selected_energy.dtype, device=selected_energy.device
        )
        if weights.ndim != 1 or weights.numel() != len(selected_delays):
            raise ValueError("delay_weights must have one entry per selected delay")
        if bool(torch.any(weights.detach() < 0)) or not bool(torch.any(weights.detach() > 0)):
            raise ValueError("delay_weights must be nonnegative with at least one positive entry")

    per_example = (selected_energy * weights).sum(dim=-1) / weights.sum()
    if reduction == "none":
        loss = per_example
    elif reduction == "mean":
        loss = per_example.mean()
    elif reduction == "sum":
        loss = per_example.sum()
    else:
        raise ValueError("reduction must be 'none', 'mean', or 'sum'")

    return DelayedReturnResult(
        loss=loss,
        per_delay=per_delay_fraction,
        raw_per_delay=raw_per_delay,
        propagated_weak_per_delay=propagated_per_delay,
        delays=selected_delays,
        delay_weights=weights,
    )

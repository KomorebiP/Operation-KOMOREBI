"""Array-based diagnostics for recursive resolution closure experiments.

The functions in this module deliberately know nothing about the prototype
agent.  Experiments may pass recorded NumPy arrays or zero/one-argument
callables that produce those arrays.  No diagnostic is presented as a test for
phenomenal consciousness; these are falsifiable measurements of the proposed
functional signature.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import numpy as np


ArraySource = np.ndarray | Sequence[Any] | Callable[..., Any]


def _materialize(source: ArraySource, inputs: Any = None) -> np.ndarray:
    """Evaluate an optional callable and return its value as an array."""

    if callable(source):
        value = source() if inputs is None else source(inputs)
    else:
        value = source
    array = np.asarray(value)
    if array.size == 0:
        raise ValueError("diagnostic inputs must not be empty")
    return array


def _finite_float(source: ArraySource, inputs: Any = None) -> np.ndarray:
    array = np.asarray(_materialize(source, inputs), dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError("diagnostic inputs must be finite")
    return array


def _normalize_axis(axis: int, ndim: int) -> int:
    """Normalize an axis without depending on NumPy's private namespace."""

    value = int(axis)
    if value < 0:
        value += ndim
    if value < 0 or value >= ndim:
        raise ValueError(f"axis {axis} is out of bounds for an array of dimension {ndim}")
    return value


def broadcast_reach(
    baseline_or_changes: ArraySource,
    intervened: ArraySource | None = None,
    *,
    consumer_axis: int = -1,
    threshold: float = 0.0,
    weights: ArraySource | None = None,
    inputs: Any = None,
) -> float:
    """Return the fraction of consumers changed by an intervention.

    ``baseline_or_changes`` may be an already computed consumer-change array.
    When ``intervened`` is supplied, absolute paired differences are computed
    first.  Dimensions other than ``consumer_axis`` are treated as repeated
    observations: boolean changes are combined with ``any`` and numeric changes
    by root-mean-square magnitude.
    """

    if threshold < 0 or not np.isfinite(threshold):
        raise ValueError("threshold must be finite and nonnegative")
    first = _materialize(baseline_or_changes, inputs)
    if intervened is None:
        changes = first
    else:
        second = _materialize(intervened, inputs)
        try:
            changes = np.asarray(second, dtype=np.float64) - np.asarray(
                first, dtype=np.float64
            )
        except ValueError as exc:
            raise ValueError("baseline and intervened traces must broadcast") from exc
    if changes.ndim == 0:
        changes = changes.reshape(1)
    axis = _normalize_axis(consumer_axis, changes.ndim)
    moved = np.moveaxis(changes, axis, -1)
    if moved.dtype == np.bool_:
        affected = np.any(moved.reshape(-1, moved.shape[-1]), axis=0)
    else:
        numeric = np.asarray(moved, dtype=np.float64)
        if not np.all(np.isfinite(numeric)):
            raise ValueError("consumer changes must be finite")
        magnitude = np.sqrt(np.mean(np.square(numeric.reshape(-1, numeric.shape[-1])), axis=0))
        affected = magnitude > threshold
    if weights is None:
        return float(np.mean(affected))
    consumer_weights = _finite_float(weights).reshape(-1)
    if consumer_weights.size != affected.size:
        raise ValueError("weights must have one entry per consumer")
    if np.any(consumer_weights < 0) or float(np.sum(consumer_weights)) <= 0:
        raise ValueError("weights must be nonnegative with positive total")
    return float(np.average(affected, weights=consumer_weights))


def temporal_persistence_auc(
    baseline_or_persistence: ArraySource,
    intervened: ArraySource | None = None,
    *,
    times: ArraySource | None = None,
    time_axis: int = 0,
    normalize: bool = True,
    inputs: Any = None,
) -> float:
    """Measure temporal depth as normalized area under an effect curve.

    With two traces the effect at each time is their RMS difference.  With one
    input, a one-dimensional array is treated as the persistence curve and a
    higher-dimensional array is reduced to an RMS curve.  Normalization divides
    by the initial nonzero effect (or the peak if the initial effect is zero),
    clips the curve to ``[0, 1]``, and divides the integral by elapsed time.
    """

    first = _finite_float(baseline_or_persistence, inputs)
    if intervened is None:
        effect = np.abs(first)
    else:
        second = _finite_float(intervened, inputs)
        try:
            effect = np.abs(second - first)
        except ValueError as exc:
            raise ValueError("baseline and intervened traces must broadcast") from exc
    if effect.ndim == 0:
        effect = effect.reshape(1)
    axis = _normalize_axis(time_axis, effect.ndim)
    moved = np.moveaxis(effect, axis, 0)
    if moved.ndim == 1:
        curve = moved
    else:
        curve = np.sqrt(np.mean(np.square(moved.reshape(moved.shape[0], -1)), axis=1))
    if normalize:
        reference = float(curve[0])
        if reference <= np.finfo(np.float64).eps:
            reference = float(np.max(curve))
        curve = np.zeros_like(curve) if reference <= 0 else np.clip(curve / reference, 0.0, 1.0)
    if times is None:
        coordinates = np.arange(curve.size, dtype=np.float64)
    else:
        coordinates = _finite_float(times).reshape(-1)
        if coordinates.size != curve.size:
            raise ValueError("times must have one entry per time point")
        if np.any(np.diff(coordinates) <= 0):
            raise ValueError("times must be strictly increasing")
    if curve.size == 1:
        return float(curve[0])
    duration = float(coordinates[-1] - coordinates[0])
    return float(np.trapezoid(curve, coordinates) / duration)


def effective_rank(
    data: ArraySource,
    *,
    sample_axis: int = 0,
    center: bool = True,
    normalized: bool = True,
    spectrum: bool = False,
    rtol: float | None = None,
    inputs: Any = None,
) -> float:
    """Return entropy effective rank as a differentiation score.

    Sample data are flattened into samples by features and their squared
    singular values form the spectrum.  Set ``spectrum=True`` to provide a
    nonnegative eigenspectrum directly.  The normalized result lies in
    ``[0, 1]`` and divides by the maximum observable rank.
    """

    array = _finite_float(data, inputs)
    if rtol is not None and (rtol < 0 or not np.isfinite(rtol)):
        raise ValueError("rtol must be finite and nonnegative")
    if spectrum:
        values = array.reshape(-1)
        if np.any(values < 0):
            raise ValueError("a supplied spectrum must be nonnegative")
        maximum_rank = values.size
    else:
        if array.ndim == 0:
            array = array.reshape(1, 1)
        axis = _normalize_axis(sample_axis, array.ndim)
        samples = np.moveaxis(array, axis, 0).reshape(array.shape[axis], -1)
        if center:
            samples = samples - np.mean(samples, axis=0, keepdims=True)
        singular_values = np.linalg.svd(samples, compute_uv=False)
        values = np.square(singular_values)
        maximum_rank = min(samples.shape[1], samples.shape[0] - int(center))
    if maximum_rank <= 0 or values.size == 0 or float(np.max(values)) <= 0:
        return 0.0
    tolerance = (
        np.finfo(np.float64).eps * max(1, values.size)
        if rtol is None
        else float(rtol)
    )
    values = values[values > tolerance * float(np.max(values))]
    if values.size == 0:
        return 0.0
    probabilities = values / np.sum(values)
    entropy = -float(np.sum(probabilities * np.log(probabilities)))
    rank = float(np.exp(entropy))
    return float(np.clip(rank / maximum_rank, 0.0, 1.0)) if normalized else rank


def brier_score(
    confidence: ArraySource,
    outcomes: ArraySource,
    *,
    inputs: Any = None,
) -> float:
    """Return the mean binary Brier score for confidence in correctness."""

    probabilities = _finite_float(confidence, inputs)
    truth = _finite_float(outcomes)
    try:
        probabilities, truth = np.broadcast_arrays(probabilities, truth)
    except ValueError as exc:
        raise ValueError("confidence and outcomes must broadcast") from exc
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("confidence values must lie in [0, 1]")
    if np.any(~(np.isclose(truth, 0.0) | np.isclose(truth, 1.0))):
        raise ValueError("outcomes must be binary")
    return float(np.mean(np.square(probabilities - truth)))


def metacognitive_calibration(
    confidence: ArraySource,
    outcomes: ArraySource,
    *,
    inputs: Any = None,
) -> float:
    """Transform the Brier loss into a bounded score, ``1 - Brier``."""

    return float(np.clip(1.0 - brier_score(confidence, outcomes, inputs=inputs), 0.0, 1.0))


def self_location_prediction_score(
    predicted: ArraySource,
    actual: ArraySource,
    *,
    mode: str = "auto",
    scale: float | None = None,
    inputs: Any = None,
) -> float:
    """Score prediction of the system's own state or causal location.

    Categorical predictions may be labels or class scores/probabilities.  A
    continuous prediction is scored by ``1 / (1 + RMSE / scale)``; by default
    ``scale`` is the standard deviation of the target, with safe fallbacks for
    constant targets.
    """

    estimate = _materialize(predicted, inputs)
    target = _materialize(actual)
    if mode not in {"auto", "categorical", "continuous"}:
        raise ValueError("mode must be 'auto', 'categorical', or 'continuous'")
    categorical = mode == "categorical"
    if mode == "auto":
        categorical = (
            estimate.ndim == target.ndim + 1
            and estimate.shape[:-1] == target.shape
            and np.issubdtype(target.dtype, np.integer)
        ) or (
            estimate.shape == target.shape
            and (estimate.dtype.kind in "biu" or target.dtype.kind in "biu")
        )
    if categorical:
        if estimate.ndim == target.ndim + 1 and estimate.shape[:-1] == target.shape:
            estimate = np.argmax(estimate, axis=-1)
        if estimate.shape != target.shape:
            raise ValueError("categorical predictions and targets have incompatible shapes")
        return float(np.mean(estimate == target))
    estimate = np.asarray(estimate, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if estimate.shape != target.shape:
        raise ValueError("continuous predictions and targets must have equal shapes")
    if not np.all(np.isfinite(estimate)) or not np.all(np.isfinite(target)):
        raise ValueError("predictions and targets must be finite")
    error = float(np.sqrt(np.mean(np.square(estimate - target))))
    if scale is None:
        denominator = float(np.std(target))
        if denominator <= np.finfo(np.float64).eps:
            denominator = float(np.sqrt(np.mean(np.square(target))))
        if denominator <= np.finfo(np.float64).eps:
            denominator = 1.0
    else:
        denominator = float(scale)
        if denominator <= 0 or not np.isfinite(denominator):
            raise ValueError("scale must be finite and positive")
    return float(1.0 / (1.0 + error / denominator))


def episodic_binding_accuracy(
    predicted: ArraySource,
    actual: ArraySource,
    *,
    sample_axis: int = 0,
    atol: float = 0.0,
    inputs: Any = None,
) -> float:
    """Return the fraction of episodes whose complete binding is correct.

    For multi-component bindings, an episode is correct only when every
    component matches.  Floating values use ``atol`` with zero relative
    tolerance; symbolic and integer values use exact equality.
    """

    estimate = _materialize(predicted, inputs)
    target = _materialize(actual)
    if estimate.shape != target.shape:
        raise ValueError("predicted and actual bindings must have equal shapes")
    if atol < 0 or not np.isfinite(atol):
        raise ValueError("atol must be finite and nonnegative")
    if estimate.ndim == 0:
        estimate = estimate.reshape(1)
        target = target.reshape(1)
    axis = _normalize_axis(sample_axis, estimate.ndim)
    estimate = np.moveaxis(estimate, axis, 0)
    target = np.moveaxis(target, axis, 0)
    if np.issubdtype(estimate.dtype, np.number) and np.issubdtype(target.dtype, np.number):
        matches = np.isclose(estimate, target, atol=atol, rtol=0.0)
    else:
        matches = estimate == target
    per_episode = matches.reshape(matches.shape[0], -1).all(axis=1)
    return float(np.mean(per_episode))


def _apply_projector(projector: Any, probes: np.ndarray) -> np.ndarray:
    if callable(projector):
        result = np.asarray(projector(probes), dtype=np.float64)
    else:
        matrix = np.asarray(projector, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("projector matrices must be square")
        if probes.shape[-1] != matrix.shape[1]:
            raise ValueError("probe dimension does not match projector dimension")
        result = np.einsum("...j,ij->...i", probes, matrix)
    if result.shape != probes.shape or not np.all(np.isfinite(result)):
        raise ValueError("a projector must return a finite array with probe shape")
    return result


def nested_projector_residual(
    projectors: Sequence[Any],
    *,
    probes: ArraySource | None = None,
    aggregate: str = "max",
) -> float:
    """Measure idempotence and ordered nesting residuals.

    Projectors are ordered coarse to fine.  The residual checks ``P_i^2=P_i``
    and, for ``i < j``, both ``P_i P_j=P_i`` and ``P_j P_i=P_i``.  Matrix
    projectors are probed on the identity basis by default.  Callable
    projectors require explicit probes.
    """

    operators = tuple(projectors)
    if not operators:
        raise ValueError("at least one projector is required")
    if aggregate not in {"max", "rms"}:
        raise ValueError("aggregate must be 'max' or 'rms'")
    if probes is None:
        if any(callable(operator) for operator in operators):
            raise ValueError("callable projectors require probes")
        first = np.asarray(operators[0])
        if first.ndim != 2 or first.shape[0] != first.shape[1]:
            raise ValueError("projector matrices must be square")
        probe_array = np.eye(first.shape[0], dtype=np.float64)
    else:
        probe_array = _finite_float(probes)
        if probe_array.ndim == 1:
            probe_array = probe_array[None, :]
    images = [_apply_projector(operator, probe_array) for operator in operators]
    residuals: list[float] = []
    epsilon = np.finfo(np.float64).eps

    def relative(delta: np.ndarray, reference: np.ndarray) -> float:
        return float(np.linalg.norm(delta) / max(float(np.linalg.norm(reference)), epsilon))

    for index, operator in enumerate(operators):
        image = images[index]
        residuals.append(relative(_apply_projector(operator, image) - image, image))
    for coarse_index, coarse in enumerate(operators):
        coarse_image = images[coarse_index]
        for fine_index in range(coarse_index + 1, len(operators)):
            fine = operators[fine_index]
            residuals.append(relative(_apply_projector(coarse, images[fine_index]) - coarse_image, coarse_image))
            residuals.append(relative(_apply_projector(fine, coarse_image) - coarse_image, coarse_image))
    values = np.asarray(residuals, dtype=np.float64)
    return float(np.max(values) if aggregate == "max" else np.sqrt(np.mean(np.square(values))))


def projector_consistency(residual: float) -> float:
    """Convert a nonnegative projector residual into a bounded score."""

    value = float(residual)
    if value < 0 or not np.isfinite(value):
        raise ValueError("residual must be finite and nonnegative")
    return float(1.0 / (1.0 + value))


def causal_adjacency(
    baseline_trace: ArraySource,
    intervention_traces: ArraySource,
    *,
    source_nodes: Sequence[int] | None = None,
    threshold: float = 0.0,
    relative: bool = False,
    time_axis: int = 0,
    node_axis: int = 1,
    include_self: bool = True,
    return_effects: bool = False,
    inputs: Any = None,
) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """Infer a directed causal adjacency matrix from paired traces.

    The baseline has shape ``(time, nodes, ...)`` by default.  Intervention
    traces add a leading intervention axis.  Row ``k`` is the trace paired with
    an intervention at ``source_nodes[k]``.  An edge ``i -> j`` is present when
    the RMS change of consumer ``j`` exceeds ``threshold``.
    """

    if threshold < 0 or not np.isfinite(threshold):
        raise ValueError("threshold must be finite and nonnegative")
    baseline = _finite_float(baseline_trace, inputs)
    interventions = _finite_float(intervention_traces, inputs)
    if baseline.ndim < 2 or interventions.ndim != baseline.ndim + 1:
        raise ValueError("interventions must add one leading axis to the baseline shape")
    t_axis = _normalize_axis(time_axis, baseline.ndim)
    n_axis = _normalize_axis(node_axis, baseline.ndim)
    if t_axis == n_axis:
        raise ValueError("time_axis and node_axis must differ")
    baseline = np.moveaxis(baseline, (t_axis, n_axis), (0, 1))
    interventions = np.moveaxis(interventions, (t_axis + 1, n_axis + 1), (1, 2))
    if interventions.shape[1:] != baseline.shape:
        raise ValueError("each intervention trace must match the baseline shape")
    source_count = interventions.shape[0]
    node_count = baseline.shape[1]
    if source_nodes is None:
        if source_count != node_count:
            raise ValueError("one intervention per node is required when source_nodes is omitted")
        sources = np.arange(node_count, dtype=int)
    else:
        sources = np.asarray(source_nodes, dtype=int).reshape(-1)
        if sources.size != source_count:
            raise ValueError("source_nodes must match the number of interventions")
        if np.any((sources < 0) | (sources >= node_count)) or np.unique(sources).size != sources.size:
            raise ValueError("source_nodes must be unique valid node indices")
    delta = interventions - baseline[None, ...]
    reduction_axes = (1,) + tuple(range(3, delta.ndim))
    paired_effects = np.sqrt(np.mean(np.square(delta), axis=reduction_axes))
    if relative:
        baseline_scale = np.sqrt(np.mean(np.square(baseline), axis=(0,) + tuple(range(2, baseline.ndim))))
        paired_effects = paired_effects / np.maximum(baseline_scale[None, :], np.finfo(np.float64).eps)
    effects = np.zeros((node_count, node_count), dtype=np.float64)
    effects[sources, :] = paired_effects
    adjacency = effects > threshold
    if not include_self:
        np.fill_diagonal(adjacency, False)
    return (adjacency, effects) if return_effects else adjacency


def is_strongly_connected(adjacency: ArraySource, *, threshold: float = 0.0) -> bool:
    """Return whether every node can reach every other directed node."""

    if threshold < 0 or not np.isfinite(threshold):
        raise ValueError("threshold must be finite and nonnegative")
    matrix = _finite_float(adjacency)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("adjacency must be a square matrix")
    edges = matrix > threshold
    reachability = edges.copy()
    np.fill_diagonal(reachability, True)
    for intermediate in range(matrix.shape[0]):
        reachability |= reachability[:, intermediate, None] & reachability[None, intermediate, :]
    return bool(np.all(reachability))


PROFILE_FIELDS = (
    "broadcast_reach",
    "temporal_persistence",
    "differentiation",
    "metacognitive_calibration",
    "self_location",
    "episodic_binding",
    "projector_consistency",
)


@dataclass(frozen=True)
class DiagnosticProfile:
    """Seven bounded diagnostics plus the irreducible causal-closure gate."""

    broadcast_reach: float
    temporal_persistence: float
    differentiation: float
    metacognitive_calibration: float
    self_location: float
    episodic_binding: float
    projector_consistency: float
    strongly_connected: bool

    def __post_init__(self) -> None:
        for name in PROFILE_FIELDS:
            value = float(getattr(self, name))
            if not np.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
            object.__setattr__(self, name, value)
        object.__setattr__(self, "strongly_connected", bool(self.strongly_connected))

    def components(self) -> dict[str, float]:
        """Return the seven scalar components in canonical order."""

        return {name: float(getattr(self, name)) for name in PROFILE_FIELDS}

    def as_dict(self) -> dict[str, float | bool]:
        result: dict[str, float | bool] = self.components()
        result["strongly_connected"] = self.strongly_connected
        return result


@dataclass(frozen=True)
class ConjunctiveSignature:
    """Conservative minimum-ratio order parameter and its audit trail."""

    omega: float
    passes: bool
    bottleneck: str
    ratios: Mapping[str, float]
    profile: DiagnosticProfile

    def as_dict(self) -> dict[str, Any]:
        return {
            "omega": float(self.omega),
            "passes": bool(self.passes),
            "bottleneck": self.bottleneck,
            "ratios": {key: float(value) for key, value in self.ratios.items()},
            "profile": self.profile.as_dict(),
        }


def conjunctive_signature(
    profile: DiagnosticProfile,
    thresholds: float | Mapping[str, float] = 0.5,
) -> ConjunctiveSignature:
    """Compute ``Omega = 1[SCC] min_i(profile_i / threshold_i)``.

    A scalar threshold applies to every component.  A mapping must contain all
    canonical profile fields.  ``passes`` is true exactly when causal closure
    holds and every component reaches its threshold.
    """

    if not isinstance(profile, DiagnosticProfile):
        raise TypeError("profile must be a DiagnosticProfile")
    if isinstance(thresholds, Mapping):
        missing = set(PROFILE_FIELDS) - set(thresholds)
        extra = set(thresholds) - set(PROFILE_FIELDS)
        if missing or extra:
            raise ValueError(f"threshold keys mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
        threshold_map = {name: float(thresholds[name]) for name in PROFILE_FIELDS}
    else:
        threshold_map = {name: float(thresholds) for name in PROFILE_FIELDS}
    if any(not np.isfinite(value) or value <= 0 for value in threshold_map.values()):
        raise ValueError("all thresholds must be finite and positive")
    components = profile.components()
    ratios = {name: components[name] / threshold_map[name] for name in PROFILE_FIELDS}
    if profile.strongly_connected:
        bottleneck = min(ratios, key=ratios.get)
        omega = float(ratios[bottleneck])
    else:
        bottleneck = "causal_closure"
        omega = 0.0
    return ConjunctiveSignature(
        omega=omega,
        passes=bool(profile.strongly_connected and omega >= 1.0),
        bottleneck=bottleneck,
        ratios=ratios,
        profile=profile,
    )


__all__ = [
    "ConjunctiveSignature",
    "DiagnosticProfile",
    "PROFILE_FIELDS",
    "brier_score",
    "broadcast_reach",
    "causal_adjacency",
    "conjunctive_signature",
    "effective_rank",
    "episodic_binding_accuracy",
    "is_strongly_connected",
    "metacognitive_calibration",
    "nested_projector_residual",
    "projector_consistency",
    "self_location_prediction_score",
    "temporal_persistence_auc",
]

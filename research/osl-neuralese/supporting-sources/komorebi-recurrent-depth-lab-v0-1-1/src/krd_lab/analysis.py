"""Dependency-light analysis for finite recurrent trajectories.

The routines in this module deliberately distinguish exact algebraic checks
from empirical estimates. A certificate marked ``rigorous`` uses a supplied
operator norm. A certificate marked ``empirical`` is diagnostic evidence only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

import numpy as np


Array = np.ndarray


def _states_2d(states: Array | Sequence[Array]) -> Array:
    value = np.asarray(states)
    if value.ndim < 2:
        raise ValueError("states must have shape (steps, ...state dimensions)")
    if value.shape[0] < 2:
        raise ValueError("at least two states are required")
    if not np.all(np.isfinite(value)):
        raise ValueError("states contain non-finite values")
    return value.reshape(value.shape[0], -1).astype(np.float64, copy=False)


@dataclass(frozen=True)
class PCAResult:
    coordinates: Array
    components: Array
    mean: Array
    explained_variance_ratio: Array
    reconstruction_residual: float
    effective_rank: int


def pca_reduce(states: Array | Sequence[Array], rank: int = 12) -> PCAResult:
    """Return a finite PCA chart of a trajectory."""

    x = _states_2d(states)
    mean = x.mean(axis=0)
    centered = x - mean
    _, singular, vh = np.linalg.svd(centered, full_matrices=False)
    if rank < 1:
        raise ValueError("rank must be positive")
    cutoff = np.finfo(float).eps * max(centered.shape) * (singular[0] if singular.size else 0.0)
    effective_rank = int(np.count_nonzero(singular > cutoff))
    retained = max(1, min(int(rank), max(effective_rank, 1), vh.shape[0]))
    components = vh[:retained]
    coordinates = centered @ components.T
    reconstructed = coordinates @ components + mean
    centered_norm = float(np.linalg.norm(centered))
    residual = (
        0.0
        if centered_norm <= np.finfo(float).eps
        else float(np.linalg.norm(x - reconstructed) / centered_norm)
    )
    energy = singular**2
    if float(energy.sum()) == 0.0:
        ratio = np.zeros(retained, dtype=float)
    else:
        ratio = energy[:retained] / energy.sum()
    return PCAResult(coordinates, components, mean, ratio, residual, effective_rank)


@dataclass(frozen=True)
class AffineDMDResult:
    operator: Array
    offset: Array
    eigenvalues: Array
    one_step_residual: float
    spectral_radius: float
    condition_number: float
    samples: int
    augmented_effective_rank: int
    augmented_dimension: int
    fully_excited: bool

    def to_json(self) -> dict:
        payload = asdict(self)
        payload["operator"] = self.operator.tolist()
        payload["offset"] = self.offset.tolist()
        payload["eigenvalues"] = [[float(v.real), float(v.imag)] for v in self.eigenvalues]
        return payload


def affine_dmd(states: Array | Sequence[Array], rcond: float = 1e-12) -> AffineDMDResult:
    """Fit ``s[i+1] = A s[i] + b`` by least squares.

    The fit is exact for noiseless affine dynamics when the snapshot matrix has
    sufficient rank. For learned trajectories it is an empirical local model.
    """

    x = _states_2d(states)
    source = x[:-1].T
    target = x[1:].T
    augmented = np.vstack([source, np.ones((1, source.shape[1]))])
    singular_values = np.linalg.svd(augmented, compute_uv=False)
    cutoff = rcond * singular_values[0] if singular_values.size else 0.0
    effective_rank = int(np.count_nonzero(singular_values > cutoff))
    fitted = target @ np.linalg.pinv(augmented, rcond=rcond)
    operator = fitted[:, :-1]
    offset = fitted[:, -1]
    predicted = operator @ source + offset[:, None]
    denominator = max(float(np.linalg.norm(target)), np.finfo(float).eps)
    residual = float(np.linalg.norm(target - predicted) / denominator)
    eigenvalues = np.linalg.eigvals(operator)
    return AffineDMDResult(
        operator=operator,
        offset=offset,
        eigenvalues=eigenvalues,
        one_step_residual=residual,
        spectral_radius=float(np.max(np.abs(eigenvalues))),
        condition_number=float(np.linalg.cond(augmented)),
        samples=source.shape[1],
        augmented_effective_rank=effective_rank,
        augmented_dimension=augmented.shape[0],
        fully_excited=effective_rank == augmented.shape[0],
    )


@dataclass(frozen=True)
class LinearFitResult:
    """Minimum-norm finite operator fit on column-oriented snapshots."""

    operator: Array
    singular_values: Array
    effective_rank: int
    feature_dimension: int
    condition_number: float
    relative_residual: float
    fully_excited: bool

    def to_json(self) -> dict:
        payload = asdict(self)
        payload["operator"] = self.operator.tolist()
        payload["singular_values"] = self.singular_values.tolist()
        return payload


def linear_operator_fit(
    source_features: Array,
    target_features: Array,
    *,
    rtol: float | None = None,
) -> LinearFitResult:
    """Fit ``target = K @ source`` and report the actually excited rank.

    Both arrays use the convention ``(features, snapshot_pairs)``.  The
    returned operator is meaningful only on the span excited by ``source``;
    ``fully_excited`` makes that limitation explicit.
    """

    source = np.asarray(source_features, dtype=float)
    target = np.asarray(target_features, dtype=float)
    if source.ndim != 2 or target.ndim != 2 or source.shape != target.shape:
        raise ValueError("source and target must be equal 2D feature-by-snapshot arrays")
    if source.shape[1] < 1 or not np.all(np.isfinite(source)) or not np.all(np.isfinite(target)):
        raise ValueError("snapshots must be nonempty and finite")
    u, singular, vh = np.linalg.svd(source, full_matrices=False)
    relative_cutoff = (
        np.finfo(float).eps * max(source.shape) if rtol is None else float(rtol)
    )
    if relative_cutoff < 0:
        raise ValueError("rtol must be nonnegative")
    threshold = relative_cutoff * singular[0] if singular.size and singular[0] > 0 else 0.0
    rank = int(np.count_nonzero(singular > threshold))
    if rank == 0:
        operator = np.zeros((target.shape[0], source.shape[0]), dtype=float)
        condition = float("inf")
    else:
        ur = u[:, :rank]
        sr = singular[:rank]
        vr = vh[:rank].T
        operator = (target @ vr / sr[None, :]) @ ur.T
        condition = float(sr[0] / sr[-1])
    predicted = operator @ source
    denominator = max(float(np.linalg.norm(target)), np.finfo(float).eps)
    residual = float(np.linalg.norm(target - predicted) / denominator)
    return LinearFitResult(
        operator=operator,
        singular_values=singular,
        effective_rank=rank,
        feature_dimension=source.shape[0],
        condition_number=condition,
        relative_residual=residual,
        fully_excited=rank == source.shape[0],
    )


def classify_eigenvalues(
    eigenvalues: Iterable[complex],
    *,
    radial_tolerance: float = 0.03,
    angular_tolerance: float = 0.05,
) -> list[dict[str, float | str]]:
    """Classify candidate recurrent modes without claiming causal meaning."""

    output: list[dict[str, float | str]] = []
    for raw in eigenvalues:
        value = complex(raw)
        magnitude = abs(value)
        angle = float(np.angle(value))
        if magnitude < 1.0 - radial_tolerance:
            label = "contracting"
        elif magnitude > 1.0 + radial_tolerance:
            label = "expanding"
        elif abs(angle) > angular_tolerance:
            label = "unit_or_near_unit_orbit"
        else:
            label = "neutral_or_drift_candidate"
        output.append(
            {
                "real": float(value.real),
                "imag": float(value.imag),
                "magnitude": float(magnitude),
                "angle": angle,
                "label": label,
            }
        )
    return output


@dataclass(frozen=True)
class SliderResult:
    detected: bool
    mean_step_norm: float
    acceleration_ratio: float
    direction_stability: float


def detect_slider(states: Array | Sequence[Array], tolerance: float = 1e-8) -> SliderResult:
    """Detect approximately constant nonzero drift in a trajectory."""

    x = _states_2d(states)
    velocity = np.diff(x, axis=0)
    speed = np.linalg.norm(velocity, axis=1)
    mean_speed = float(speed.mean())
    if velocity.shape[0] < 2:
        acceleration_ratio = float("inf")
    else:
        acceleration = np.diff(velocity, axis=0)
        acceleration_ratio = float(
            np.linalg.norm(acceleration) / max(np.linalg.norm(velocity[:-1]), np.finfo(float).eps)
        )
    valid = speed > tolerance
    if int(valid.sum()) < 2:
        direction_stability = 0.0
    else:
        directions = velocity[valid] / speed[valid, None]
        reference = directions.mean(axis=0)
        norm = float(np.linalg.norm(reference))
        direction_stability = 0.0 if norm == 0 else float(np.mean(directions @ (reference / norm)))
    detected = mean_speed > tolerance and acceleration_ratio < 1e-6 and direction_stability > 0.999
    return SliderResult(detected, mean_speed, acceleration_ratio, direction_stability)


def coordinate_projectors(dimension: int, groups: Sequence[Sequence[int]]) -> tuple[Array, ...]:
    """Construct exact orthogonal coordinate packets from a partition."""

    if dimension < 1:
        raise ValueError("dimension must be positive")
    flattened = [int(index) for group in groups for index in group]
    if sorted(flattened) != list(range(dimension)):
        raise ValueError("groups must partition every coordinate exactly once")
    projectors: list[Array] = []
    for group in groups:
        projector = np.zeros((dimension, dimension), dtype=float)
        for index in group:
            projector[int(index), int(index)] = 1.0
        projectors.append(projector)
    return tuple(projectors)


def _block_multiply(left: list[list[Array]], right: list[list[Array]]) -> list[list[Array]]:
    count = len(left)
    result: list[list[Array]] = []
    for row in range(count):
        output_row: list[Array] = []
        for column in range(count):
            total = np.zeros_like(left[0][0])
            for middle in range(count):
                total = total + left[row][middle] @ right[middle][column]
            output_row.append(total)
        result.append(output_row)
    return result


def _reconstruct_blocks(blocks: Sequence[Sequence[Array]]) -> Array:
    total = np.zeros_like(np.asarray(blocks[0][0]))
    for row in blocks:
        for block in row:
            total = total + np.asarray(block)
    return total


@dataclass(frozen=True)
class BlockTransportCertificate:
    valid: bool
    packet_idempotence_residual: float
    packet_annihilation_residual: float
    packet_completeness_residual: float
    one_step_reconstruction_residual: float
    path_power_residual: float
    exponent: int

    def to_json(self) -> dict:
        return asdict(self)


def block_transport_certificate(
    operator: Array,
    projectors: Sequence[Array],
    *,
    exponent: int = 5,
    tolerance: float = 1e-10,
) -> BlockTransportCertificate:
    """Check finite packet reconstruction and the recurrent path-power law."""

    matrix = np.asarray(operator, dtype=float)
    packets = tuple(np.asarray(projector, dtype=float) for projector in projectors)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    if exponent < 1:
        raise ValueError("exponent must be positive")
    if any(packet.shape != matrix.shape for packet in packets):
        raise ValueError("all projectors must match the operator")
    identity = np.eye(matrix.shape[0])
    idempotence = max(float(np.linalg.norm(packet @ packet - packet)) for packet in packets)
    annihilation = max(
        [float(np.linalg.norm(left @ right)) for i, left in enumerate(packets) for j, right in enumerate(packets) if i != j]
        or [0.0]
    )
    completeness = float(np.linalg.norm(sum(packets, np.zeros_like(matrix)) - identity))
    blocks = [[target @ matrix @ source for source in packets] for target in packets]
    one_step = float(np.linalg.norm(_reconstruct_blocks(blocks) - matrix))
    powered_blocks = blocks
    for _ in range(1, exponent):
        powered_blocks = _block_multiply(powered_blocks, blocks)
    path_residual = float(np.linalg.norm(_reconstruct_blocks(powered_blocks) - np.linalg.matrix_power(matrix, exponent)))
    valid = max(idempotence, annihilation, completeness, one_step, path_residual) <= tolerance
    return BlockTransportCertificate(valid, idempotence, annihilation, completeness, one_step, path_residual, exponent)


@dataclass(frozen=True)
class ContractionCertificate:
    status: str
    kappa: float
    last_step_norm: float
    fixed_point_error_bound: float | None
    observed_final_error: float | None
    bound_holds: bool | None

    def to_json(self) -> dict:
        return asdict(self)


def contraction_certificate(
    states: Array | Sequence[Array],
    *,
    operator: Array | None = None,
    kappa: float | None = None,
    fixed_point: Array | None = None,
) -> ContractionCertificate:
    """Return a rigorous bound only when a certified contraction is supplied."""

    x = _states_2d(states)
    if operator is not None and kappa is not None:
        raise ValueError("provide operator or kappa, not both")
    if operator is not None:
        kappa_value = float(np.linalg.norm(np.asarray(operator, dtype=float), ord=2))
        status = "conditional_on_supplied_linear_operator"
    elif kappa is not None:
        kappa_value = float(kappa)
        status = "conditional_on_supplied_contraction_constant"
    else:
        ratios = np.linalg.norm(np.diff(x, axis=0)[1:], axis=1) / np.maximum(
            np.linalg.norm(np.diff(x, axis=0)[:-1], axis=1), np.finfo(float).eps
        )
        kappa_value = float(np.max(ratios)) if ratios.size else float("nan")
        status = "empirical_only"
    last_step = float(np.linalg.norm(x[-1] - x[-2]))
    has_supplied_certificate = operator is not None or kappa is not None
    bound = (
        kappa_value * last_step / (1.0 - kappa_value)
        if has_supplied_certificate and 0.0 <= kappa_value < 1.0
        else None
    )
    observed = None
    holds = None
    if fixed_point is not None:
        target = np.asarray(fixed_point, dtype=float).reshape(-1)
        if target.shape != x[-1].shape:
            raise ValueError("fixed point shape does not match state shape")
        observed = float(np.linalg.norm(x[-1] - target))
        holds = None if bound is None else bool(observed <= bound + 1e-12)
    return ContractionCertificate(status, kappa_value, last_step, bound, observed, holds)


@dataclass(frozen=True)
class PathIndependenceResult:
    initial_pairwise_max: float
    final_pairwise_max: float
    tail_centroid_pairwise_max: float
    normalized_final_dispersion: float
    seeds: int

    def to_json(self) -> dict:
        return asdict(self)


def _pairwise_max(rows: Array) -> float:
    if rows.shape[0] < 2:
        return 0.0
    return max(float(np.linalg.norm(rows[i] - rows[j])) for i in range(rows.shape[0]) for j in range(i))


def path_independence(trajectories: Sequence[Array], tail: int = 8) -> PathIndependenceResult:
    """Measure agreement across initial states without declaring a proof of descent."""

    if len(trajectories) < 2:
        raise ValueError("at least two trajectories are required")
    if tail < 1:
        raise ValueError("tail must be positive")
    values = [_states_2d(trajectory) for trajectory in trajectories]
    dimension = values[0].shape[1]
    if any(value.shape[1] != dimension for value in values):
        raise ValueError("all trajectories must have one state dimension")
    initials = np.vstack([value[0] for value in values])
    finals = np.vstack([value[-1] for value in values])
    centroids = np.vstack([value[-min(tail, value.shape[0]) :].mean(axis=0) for value in values])
    initial_spread = _pairwise_max(initials)
    scale = max(initial_spread, np.finfo(float).eps)
    return PathIndependenceResult(
        initial_pairwise_max=initial_spread,
        final_pairwise_max=_pairwise_max(finals),
        tail_centroid_pairwise_max=_pairwise_max(centroids),
        normalized_final_dispersion=_pairwise_max(finals) / scale,
        seeds=len(values),
    )


def modulo_cache_profile(step_count: int, modulus: int) -> dict:
    """Describe the exact residue-address quotient used by a cyclic cache."""

    if step_count < 0 or modulus < 1:
        raise ValueError("step_count must be nonnegative and modulus positive")
    lanes = {str(residue): [] for residue in range(modulus)}
    for step in range(step_count):
        lanes[str(step % modulus)].append(step)
    retained = {residue: (steps[-1] if steps else None) for residue, steps in lanes.items()}
    collision_count = sum(max(0, len(steps) - 1) for steps in lanes.values())
    return {
        "step_count": step_count,
        "modulus": modulus,
        "lanes": lanes,
        "retained_last_step": retained,
        "collision_count": collision_count,
        "lossless": collision_count == 0,
    }


def last_write_selector(step_count: int, modulus: int) -> Array:
    """Return the exact final-state selector for modulo-``k`` overwriting.

    This is deliberately not a residue-class sum or average.  Row ``r`` has a
    single one at the most recent step whose cache address is ``r``.
    """

    if step_count < 0 or modulus < 1:
        raise ValueError("step_count must be nonnegative and modulus positive")
    selector = np.zeros((modulus, step_count), dtype=float)
    for residue in range(min(modulus, step_count)):
        final_step = residue + modulus * ((step_count - 1 - residue) // modulus)
        selector[residue, final_step] = 1.0
    return selector

"""Online, persistent causal self-boundary learning for RRCT.

The component in this module owns its prospective handle commitments, binds
them to subsequently realized anonymous process streams, and accepts an
outcome only through an explicit reveal call.  It never receives source-family
labels, hidden routes, evaluator projectors, condition truth, or an executed
perturbation vector.

Completed transitions are retained in a bounded rolling evidence window.  A
fixed-seed, per-update max-statistic randomization null and two disjoint
evidence halves define the first replicated handle-by-source mode.  Exactly
one pair must survive or the fit is null.  For every higher ordered mode, a
cross-fitted reduced-rank randomization bootstrap carries the proposal fold's
fitted lower modes into each reassigned confirmation outcome and asks whether
another mode is required.  The observed longitudinal history is conditioned
on rather than recursively regenerated.  This is one-step composite-null
inference under the stated single-route, additive, stable-effect, and weak-
dependence assumptions; it is not an exact finite-sample Fisher test, a full
dynamic null, or sequence-wide online error control.

This is a bounded functional causal-modeling component.  It does not create or
measure phenomenal consciousness, subjective awareness, sentience, valence,
or moral status.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
SNAPSHOT_SCHEMA = "rrct.online_causal_self_boundary.v4"
COMMITMENT_SCHEMA = "rrct.causal_handle_commitment.v1"
TRANSITION_SCHEMA = "rrct.bound_causal_transition.v1"
OUTCOME_SCHEMA = "rrct.causal_outcome.v1"
ACCESS_SNAPSHOT_SCHEMA = "rrct.online_causal_access_readout.v1"
ACCESS_MEMORY_SNAPSHOT_SCHEMA = "rrct.online_causal_access_memory.v1"
DIRECT_ACCESS_SNAPSHOT_SCHEMA = "rrct.direct_causal_access.v1"
HIGHER_MODE_NULLS = frozenset(
    {
        "cross_fitted_reduced_rank_randomization_bootstrap",
        "global_sharp_null",
    }
)


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise ValueError(f"{name} must be an integer")
    parsed = int(value)
    if parsed < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return parsed


def _optional_integer(
    value: Any, name: str, *, minimum: int = 0
) -> int | None:
    if value is None:
        return None
    return _integer(value, name, minimum=minimum)


def _finite_float(value: Any, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(f"{name} must be a finite real scalar")
    parsed = float(value)
    if not np.isfinite(parsed):
        raise ValueError(f"{name} must be a finite real scalar")
    return parsed


def _array(value: ArrayLike, shape: tuple[int, ...], name: str) -> FloatArray:
    result = np.asarray(value, dtype=np.float64)
    if result.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


def _readonly(value: ArrayLike) -> FloatArray:
    result = np.asarray(value, dtype=np.float64).copy()
    result.setflags(write=False)
    return result


def _update_digest(digest: Any, value: Any) -> None:
    if isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        digest.update(b"array\0")
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(json.dumps(array.shape).encode("ascii"))
        digest.update(array.tobytes(order="C"))
        return
    if isinstance(value, Mapping):
        digest.update(b"mapping\0")
        for key in sorted(value, key=str):
            _update_digest(digest, str(key))
            _update_digest(digest, value[key])
        return
    if isinstance(value, (tuple, list)):
        digest.update(b"sequence\0")
        for item in value:
            _update_digest(digest, item)
        return
    if isinstance(value, np.generic):
        value = value.item()
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest.update(encoded.encode("utf-8"))


def _digest(value: Any) -> str:
    result = hashlib.sha256()
    _update_digest(result, value)
    return result.hexdigest()


def _sha256_text(value: Any, name: str) -> str:
    """Validate the canonical lowercase representation of a SHA-256 digest."""

    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest") from exc
    if value != value.lower():
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _matrix_rank(value: FloatArray) -> int:
    """Return a deterministic numerical rank for snapshot invariants."""

    singular = np.linalg.svd(value, compute_uv=False)
    if singular.size == 0:
        return 0
    tolerance = (
        max(value.shape)
        * np.finfo(np.float64).eps
        * max(float(singular[0]), 1.0)
        * 64.0
    )
    return int(np.count_nonzero(singular > tolerance))


def _validate_projector(value: FloatArray, rank: int, name: str) -> None:
    """Require a symmetric idempotent orthogonal projector of exact rank."""

    tolerance = 1e-9
    if not np.allclose(value, value.T, rtol=0.0, atol=tolerance):
        raise ValueError(f"snapshot {name} is not symmetric")
    if not np.allclose(value @ value, value, rtol=0.0, atol=tolerance):
        raise ValueError(f"snapshot {name} is not idempotent")
    if _matrix_rank(value) != rank:
        raise ValueError(f"snapshot {name} rank does not match state.rank")


def _monte_carlo_order(
    permutations: int,
    quantile: float,
    *,
    permutations_name: str = "permutations",
) -> int:
    """Return the finite-Monte-Carlo critical order (one based).

    With ``B`` null draws, a strict observed-statistic comparison against
    order ``ceil((B + 1) * (1 - alpha))`` implements the usual add-one
    randomization rule.  The requested tail is unresolved when that order is
    larger than ``B``; interpolation between draws must not silently pretend
    otherwise.
    """

    count = _integer(permutations, permutations_name, minimum=1)
    requested = _finite_float(quantile, "quantile")
    if not 0.0 < requested < 1.0:
        raise ValueError("quantile must lie in (0, 1)")
    # nextafter preserves exact integer boundaries such as 100 * .99 while
    # leaving genuinely non-integral products on the same side of the ceiling.
    product = np.nextafter((count + 1) * requested, -np.inf)
    order = int(np.ceil(product))
    if order > count:
        alpha = 1.0 - requested
        raise ValueError(
            f"{permutations_name}={count} cannot resolve alpha={alpha:.12g}; "
            f"the requested finite Monte Carlo order is {order}"
        )
    return max(1, order)


def _monte_carlo_threshold(maxima: ArrayLike, quantile: float) -> float:
    """Select a finite max-statistic order without quantile interpolation."""

    values = np.asarray(maxima, dtype=np.float64)
    if values.ndim != 1 or len(values) == 0 or not np.all(np.isfinite(values)):
        raise ValueError("maxima must be a non-empty finite one-dimensional array")
    order = _monte_carlo_order(len(values), quantile)
    return float(np.partition(values, order - 1)[order - 1])


@dataclass(frozen=True)
class CausalBoundaryConfig:
    """Frozen dimensions and online fit/revision constants."""

    observation_dim: int
    process_dim: int
    source_count: int
    handle_count: int
    evidence_capacity: int = 480
    minimum_samples: int = 480
    fit_interval: int = 40
    structural_confirmation_interval: int | None = None
    commitment_block_size: int = 40
    ridge: float = 0.50
    null_permutations: int = 128
    half_null_permutations: int = 128
    null_quantile: float = 0.99
    higher_mode_null: str = (
        "cross_fitted_reduced_rank_randomization_bootstrap"
    )
    revision_confirmations: int = 2
    revocation_confirmations: int = 2
    confidence_decay: float = 0.65
    seed: int = 0

    def __post_init__(self) -> None:
        confirmation_interval = (
            self.fit_interval
            if self.structural_confirmation_interval is None
            else self.structural_confirmation_interval
        )
        object.__setattr__(
            self,
            "structural_confirmation_interval",
            _integer(
                confirmation_interval,
                "structural_confirmation_interval",
                minimum=1,
            ),
        )
        for name in (
            "observation_dim",
            "process_dim",
            "source_count",
            "handle_count",
            "evidence_capacity",
            "minimum_samples",
            "fit_interval",
            "structural_confirmation_interval",
            "commitment_block_size",
            "null_permutations",
            "half_null_permutations",
            "revision_confirmations",
            "revocation_confirmations",
        ):
            object.__setattr__(self, name, _integer(getattr(self, name), name, minimum=1))
        object.__setattr__(self, "seed", _integer(self.seed, "seed", minimum=0))
        if self.minimum_samples > self.evidence_capacity:
            raise ValueError("minimum_samples cannot exceed evidence_capacity")
        if self.minimum_samples < 8:
            raise ValueError("minimum_samples must be at least eight")
        if self.commitment_block_size % 2:
            raise ValueError("commitment_block_size must be even")
        ridge = _finite_float(self.ridge, "ridge")
        quantile = _finite_float(self.null_quantile, "null_quantile")
        decay = _finite_float(self.confidence_decay, "confidence_decay")
        if ridge <= 0.0:
            raise ValueError("ridge must be positive")
        if not 0.5 < quantile < 1.0:
            raise ValueError("null_quantile must lie in (0.5, 1)")
        if not 0.0 < decay < 1.0:
            raise ValueError("confidence_decay must lie in (0, 1)")
        if (
            not isinstance(self.higher_mode_null, str)
            or self.higher_mode_null not in HIGHER_MODE_NULLS
        ):
            raise ValueError(
                "higher_mode_null must be one of "
                f"{sorted(HIGHER_MODE_NULLS)!r}"
            )
        for name in (
            "evidence_capacity",
            "minimum_samples",
            "fit_interval",
            "structural_confirmation_interval",
        ):
            if getattr(self, name) % self.commitment_block_size:
                raise ValueError(
                    f"{name} must be a multiple of commitment_block_size"
                )
        if self.structural_confirmation_interval % self.fit_interval:
            raise ValueError(
                "structural_confirmation_interval must be a multiple of fit_interval"
            )
        nuisance_columns = (
            1
            + self.observation_dim
            + self.source_count * self.process_dim
            + self.handle_count
        )
        for name in ("evidence_capacity", "minimum_samples"):
            block_count = getattr(self, name) // self.commitment_block_size
            if block_count < 2 or block_count % 2:
                raise ValueError(
                    f"{name} must contain a positive even number of commitment blocks"
                )
            if (
                self.higher_mode_null
                == "cross_fitted_reduced_rank_randomization_bootstrap"
                and block_count % 4
            ):
                raise ValueError(
                    f"{name} must contain a multiple of four commitment blocks "
                    "for disjoint proposal and confirmation folds"
                )
            if (
                self.higher_mode_null
                == "cross_fitted_reduced_rank_randomization_bootstrap"
                and (block_count // 4) * self.commitment_block_size
                <= nuisance_columns
            ):
                raise ValueError(
                    "each conditional-rank confirmation fold must contain "
                    f"more rows than the {nuisance_columns} nuisance columns"
                )
        if self.minimum_samples // 2 <= nuisance_columns:
            raise ValueError(
                "each minimum-sample evidence half must contain more rows than "
                f"the {nuisance_columns} nuisance-design columns"
            )
        for name in ("null_permutations", "half_null_permutations"):
            _monte_carlo_order(
                getattr(self, name),
                quantile,
                permutations_name=name,
            )
        object.__setattr__(self, "ridge", ridge)
        object.__setattr__(self, "null_quantile", quantile)
        object.__setattr__(self, "confidence_decay", decay)


@dataclass(frozen=True)
class CausalHandleCommitment:
    """Agent-generated prospective anonymous handle values."""

    time: int
    nonce: int
    handles: FloatArray
    digest: str


@dataclass(frozen=True)
class BoundCausalTransition:
    """Receipt binding a prior commitment to current state and source bank."""

    time: int
    commitment_digest: str
    transition_digest: str


@dataclass(frozen=True)
class CausalBoundaryState:
    """Persistent learned boundary state, without evaluator metadata."""

    selected_handle_index: int | None
    selected_source_index: int | None
    rank: int
    internal_projector: FloatArray
    sensory_projector: FloatArray
    effect_operator: FloatArray
    confidence: float
    uncertainty: float
    change_alarm: float
    evidence_count: int
    fit_count: int
    age: int
    epoch: int
    model_digest: str

    @property
    def active(self) -> bool:
        return bool(
            self.selected_handle_index is not None
            and self.selected_source_index is not None
            and self.rank > 0
        )

    @property
    def structural_signature(self) -> tuple[bool, int | None, int | None, int]:
        """Return the identity whose changes require sequential confirmation."""

        return (
            self.active,
            self.selected_handle_index,
            self.selected_source_index,
            self.rank,
        )


@dataclass(frozen=True)
class CausalBoundaryUpdateReceipt:
    """Prequential receipt for one revealed transition."""

    commitment_digest: str
    transition_digest: str
    outcome_digest: str
    reveal_time: int
    model_digest_before: str
    model_digest_after: str
    evidence_count: int
    fit_performed: bool
    acquired: bool
    revised: bool
    revoked: bool
    rank_changed: bool
    structural_event: str
    updates_frozen: bool
    prequential_alignment: float
    confidence_before: float
    previous_handle_index: int | None
    previous_source_index: int | None
    previous_rank: int
    fit_handle_index: int | None
    fit_source_index: int | None
    fit_rank: int
    fit_confidence: float
    selected_handle_index: int | None
    selected_source_index: int | None
    rank: int
    confidence: float
    change_alarm: float
    candidate_handle_index: int | None
    candidate_source_index: int | None
    candidate_rank: int
    candidate_streak: int
    candidate_last_evidence_count: int | None
    candidate_renewed: bool
    null_streak: int
    null_last_evidence_count: int | None
    null_renewed: bool
    epoch: int


@dataclass(frozen=True)
class _Evidence:
    observation: FloatArray
    process_bank: FloatArray
    handles: FloatArray
    next_observation: FloatArray
    commitment_time: int
    commitment_nonce: int
    commitment_digest: str
    transition_digest: str
    reveal_time: int
    outcome_digest: str


@dataclass(frozen=True)
class _PendingTransition:
    time: int
    observation: FloatArray
    process_bank: FloatArray
    commitment: CausalHandleCommitment
    transition_digest: str


@dataclass(frozen=True)
class _FitResult:
    selected_handle_index: int | None
    selected_source_index: int | None
    rank: int
    internal_projector: FloatArray
    sensory_projector: FloatArray
    effect_operator: FloatArray
    confidence: float
    ambiguous: bool


@dataclass(frozen=True)
class CausalAccessPrediction:
    """One pre-update readout attempt from post-workspace/self features."""

    pair: tuple[int, int] | None
    class_index: int | None
    confidence: float
    margin: float
    distance: float
    update_count: int


def _ridge_coefficients(
    design: FloatArray, targets: FloatArray, ridge: float
) -> FloatArray:
    penalty = float(ridge) * np.eye(design.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.1 * float(ridge)
    return np.asarray(
        np.linalg.solve(
        design.T @ design + penalty, design.T @ targets
        ),
        dtype=np.float64,
    )


def _ridge_residuals(design: FloatArray, targets: FloatArray, ridge: float) -> FloatArray:
    coefficients = _ridge_coefficients(design, targets, ridge)
    return np.asarray(targets - design @ coefficients, dtype=np.float64)


def _raw_designs(
    observation: FloatArray,
    bank: FloatArray,
    handles: FloatArray,
    config: CausalBoundaryConfig,
) -> tuple[FloatArray, FloatArray]:
    """Return nuisance and handle-by-source designs before residualization."""

    count = len(observation)
    nuisance = np.column_stack(
        (
            np.ones(count, dtype=np.float64),
            observation,
            bank.reshape(count, config.source_count * config.process_dim),
            handles,
        )
    )
    raw_interactions = (
        handles[:, :, None, None] * bank[:, None, :, :]
    ).reshape(
        count,
        config.handle_count * config.source_count * config.process_dim,
    )
    return (
        np.asarray(nuisance, dtype=np.float64),
        np.asarray(
            raw_interactions.reshape(
                count,
                config.handle_count,
                config.source_count,
                config.process_dim,
            ),
            dtype=np.float64,
        ),
    )


def _residual_problem(
    observation: FloatArray,
    bank: FloatArray,
    handles: FloatArray,
    next_observation: FloatArray,
    config: CausalBoundaryConfig,
) -> tuple[FloatArray, FloatArray]:
    count = len(observation)
    nuisance, raw_interactions = _raw_designs(
        observation, bank, handles, config
    )
    # Outcome and interaction columns share exactly the same nuisance design.
    # Solving their ridge system together avoids a duplicate factorization
    # without changing the residual problem being recomputed for each draw.
    residuals = _ridge_residuals(
        nuisance,
        np.column_stack((next_observation, raw_interactions.reshape(count, -1))),
        config.ridge,
    )
    outcome = residuals[:, : config.observation_dim]
    residual_interactions = residuals[:, config.observation_dim :].reshape(
        count,
        config.handle_count,
        config.source_count,
        config.process_dim,
    )
    return outcome, residual_interactions


def _operators(
    interactions: FloatArray,
    outcome: FloatArray,
    config: CausalBoundaryConfig,
) -> tuple[FloatArray, FloatArray]:
    shape = (
        config.handle_count,
        config.source_count,
        config.process_dim,
        config.observation_dim,
    )
    effects = np.empty(shape, dtype=np.float64)
    inverses = np.empty(
        (
            config.handle_count,
            config.source_count,
            config.process_dim,
            config.process_dim,
        ),
        dtype=np.float64,
    )
    penalty = config.ridge * np.eye(config.process_dim, dtype=np.float64)
    for handle_index in range(config.handle_count):
        for source_index in range(config.source_count):
            values = interactions[:, handle_index, source_index]
            inverse = np.linalg.inv(values.T @ values + penalty)
            inverses[handle_index, source_index] = inverse
            effects[handle_index, source_index] = inverse @ values.T @ outcome
    return effects, inverses


def _commitment_block_groups(
    commitment_nonces: ArrayLike,
    block_size: int,
) -> list[NDArray[np.int64]]:
    """Return row indices for complete prospective commitment blocks."""

    nonces = np.asarray(commitment_nonces)
    if nonces.ndim != 1 or not np.issubdtype(nonces.dtype, np.integer):
        raise ValueError("commitment_nonces must be a one-dimensional integer array")
    size = _integer(block_size, "block_size", minimum=2)
    if len(nonces) == 0 or len(np.unique(nonces)) != len(nonces):
        raise ValueError("commitment nonces must be non-empty and unique")
    groups: list[NDArray[np.int64]] = []
    block_ids = np.unique(nonces // size)
    for block_id in np.sort(block_ids):
        indices = np.flatnonzero(nonces // size == block_id)
        expected = np.arange(block_id * size, (block_id + 1) * size)
        ordered = indices[np.argsort(nonces[indices])]
        if len(ordered) != size or not np.array_equal(nonces[ordered], expected):
            raise ValueError("inference requires complete prospective commitment blocks")
        groups.append(np.asarray(ordered, dtype=np.int64))
    return groups


def _rerandomized_handles(
    handles: FloatArray,
    commitment_nonces: ArrayLike,
    block_size: int,
    rng: np.random.Generator,
) -> FloatArray:
    """Independently rerandomize each handle column inside each full block."""

    values = np.asarray(handles, dtype=np.float64)
    if values.ndim != 2 or not np.all(np.isfinite(values)):
        raise ValueError("handles must be a finite two-dimensional array")
    groups = _commitment_block_groups(commitment_nonces, block_size)
    randomized = values.copy()
    for indices in groups:
        for handle_index in range(values.shape[1]):
            order = rng.permutation(len(indices))
            randomized[indices, handle_index] = values[
                indices[order], handle_index
            ]
    return randomized


def _replicated_directional_mode(
    full_value: float,
    half_value_a: float,
    half_value_b: float,
    full_threshold: float,
    half_threshold_a: float,
    half_threshold_b: float,
) -> bool:
    """Require a positive effect in the full fit and both held-apart halves."""

    return bool(
        full_value > full_threshold
        and half_value_a > half_threshold_a
        and half_value_b > half_threshold_b
    )


def _paired_mode_confidence(
    full_value: float,
    half_value_a: float,
    half_value_b: float,
    full_threshold: float,
    half_threshold_a: float,
    half_threshold_b: float,
) -> float:
    """Return the limiting normalized margin from correctly paired splits.

    This is an evidence-support score, not a posterior probability.  It is
    positive exactly when all three directional comparisons are strictly
    above their own thresholds.
    """

    comparisons = (
        (float(full_value), float(full_threshold)),
        (float(half_value_a), float(half_threshold_a)),
        (float(half_value_b), float(half_threshold_b)),
    )
    margins = [
        (statistic - threshold) / (abs(statistic) + 1e-12)
        for statistic, threshold in comparisons
    ]
    return float(np.clip(min(margins), 0.0, 1.0))


def _familywise_threshold(
    observation: FloatArray,
    bank: FloatArray,
    handles: FloatArray,
    next_observation: FloatArray,
    commitment_nonces: NDArray[np.int64],
    config: CausalBoundaryConfig,
    *,
    permutations: int,
    salt: int,
) -> FloatArray:
    """Calibrate ordered modes against max-pair block-randomization nulls.

    Every draw independently rerandomizes each prospective handle column
    within its commitment block.  Because handles are nuisance variables as
    well as constituents of the candidate interactions, the entire residual
    problem is recomputed for every draw.  For ordered singular mode ``k``, the
    statistic is the maximum ``k``-th singular value over all candidate pairs.
    For mode one this is a max-pair screen under the global sharp null of no
    handle-mediated interaction.  For higher modes it is deliberately an
    operational threshold, not a conditional reduced-rank null: rerandomizing
    all handles also destroys any admitted lower mode.  Sequential admission
    stops at the first failed mode, but no composite-rank, strong pairwise, or
    across-update error-control claim follows.
    """

    count = _integer(permutations, "permutations", minimum=1)
    _monte_carlo_order(count, config.null_quantile)
    groups = _commitment_block_groups(
        commitment_nonces, config.commitment_block_size
    )
    if not groups:
        raise ValueError("at least one complete commitment block is required")
    # The schedule is fixed by frozen configuration and prospective nonces. It
    # never depends on realized handle values, outcomes, or observed effects.
    seed = np.random.SeedSequence(
        [
            config.seed,
            int(salt),
            len(observation),
            config.handle_count,
            config.source_count,
            int(commitment_nonces[groups[0][0]]),
            int(commitment_nonces[groups[-1][-1]]),
        ]
    )
    rng = np.random.default_rng(seed)
    mode_count = min(config.process_dim, config.observation_dim)
    maxima = np.empty((count, mode_count), dtype=np.float64)
    for permutation_index in range(len(maxima)):
        randomized_handles = _rerandomized_handles(
            handles,
            commitment_nonces,
            config.commitment_block_size,
            rng,
        )
        null_outcome, null_interactions = _residual_problem(
            observation,
            bank,
            randomized_handles,
            next_observation,
            config,
        )
        null_effects, _ = _operators(null_interactions, null_outcome, config)
        null_singular_values = np.linalg.svd(
            null_effects, compute_uv=False
        )
        maxima[permutation_index] = np.max(
            null_singular_values, axis=(0, 1)
        )
    return np.asarray(
        [
            _monte_carlo_threshold(maxima[:, mode_index], config.null_quantile)
            for mode_index in range(mode_count)
        ],
        dtype=np.float64,
    )


def _reduced_rank_ridge_fit(
    interactions: FloatArray,
    outcome: FloatArray,
    ridge: float,
    rank: int,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Fit the penalized least-squares surface with a rank constraint.

    If ``G = X.T @ X + ridge * I = L @ L.T`` and ``B`` is the unconstrained
    ridge coefficient, truncating the SVD of ``L.T @ B`` gives the exact
    minimizer of the penalized objective subject to ``rank(B) <= rank``.
    The squared ordered singular values are the successive improvements in
    that objective.  The Cholesky factor avoids explicitly forming a square
    root and inverse square root of an ill-conditioned Gram matrix.
    """

    values = np.asarray(interactions, dtype=np.float64)
    targets = np.asarray(outcome, dtype=np.float64)
    if values.ndim != 2 or targets.ndim != 2 or len(values) != len(targets):
        raise ValueError("reduced-rank inputs must be aligned matrices")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(targets)):
        raise ValueError("reduced-rank inputs must be finite")
    requested_rank = _integer(rank, "rank", minimum=0)
    maximum_rank = min(values.shape[1], targets.shape[1])
    if requested_rank > maximum_rank:
        raise ValueError("rank exceeds the reduced-rank problem dimension")
    penalty = _finite_float(ridge, "ridge")
    if penalty <= 0.0:
        raise ValueError("ridge must be positive")
    gram = values.T @ values + penalty * np.eye(values.shape[1])
    try:
        root = np.linalg.cholesky(gram)
        coefficient = np.linalg.solve(gram, values.T @ targets)
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "reduced-rank Gram matrix is not positive definite"
        ) from exc
    weighted = root.T @ coefficient
    left, singular, right = np.linalg.svd(weighted, full_matrices=False)
    if requested_rank == 0:
        restricted = np.zeros_like(coefficient)
    else:
        truncated = (
            (left[:, :requested_rank] * singular[:requested_rank])
            @ right[:requested_rank]
        )
        restricted = np.linalg.solve(root.T, truncated)
    return (
        np.asarray(restricted, dtype=np.float64),
        np.asarray(singular, dtype=np.float64),
        np.asarray(coefficient, dtype=np.float64),
    )


def _rank_increment_statistic(
    interactions: FloatArray,
    outcome: FloatArray,
    ridge: float,
    null_rank: int,
) -> float:
    """Return the penalized improvement from rank ``r`` to ``r + 1``."""

    rank = _integer(null_rank, "null_rank", minimum=0)
    _, singular, _ = _reduced_rank_ridge_fit(
        interactions, outcome, ridge, rank
    )
    if rank >= len(singular):
        raise ValueError("null_rank leaves no additional mode to test")
    return float(singular[rank] ** 2)


def _partition_inference_evidence(
    evidence: list[_Evidence], config: CausalBoundaryConfig
) -> tuple[list[_Evidence], list[_Evidence], list[_Evidence]]:
    """Split the newest usable complete blocks into disjoint 1/2, 1/4, 1/4."""

    aligned = _aligned_complete_evidence(evidence, config)
    block_count = len(aligned) // config.commitment_block_size
    usable_blocks = block_count - block_count % 4
    if usable_blocks < 4:
        raise ValueError(
            "conditional rank inference requires four complete blocks"
        )
    aligned = aligned[-usable_blocks * config.commitment_block_size :]
    block_count = usable_blocks
    confirmation_blocks = block_count // 4
    proposal_blocks = block_count - 2 * confirmation_blocks
    proposal_end = proposal_blocks * config.commitment_block_size
    confirmation_a_end = (
        proposal_end + confirmation_blocks * config.commitment_block_size
    )
    proposal = aligned[:proposal_end]
    confirmation_a = aligned[proposal_end:confirmation_a_end]
    confirmation_b = aligned[confirmation_a_end:]
    nonces = [
        {item.commitment_nonce for item in fold}
        for fold in (proposal, confirmation_a, confirmation_b)
    ]
    if nonces[0] & nonces[1] or nonces[0] & nonces[2] or nonces[1] & nonces[2]:
        raise ValueError("conditional rank inference folds overlap")
    return proposal, confirmation_a, confirmation_b


def _evidence_arrays(
    evidence: list[_Evidence],
) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]]:
    return (
        np.stack([item.observation for item in evidence]),
        np.stack([item.process_bank for item in evidence]),
        np.stack([item.handles for item in evidence]),
        np.stack([item.next_observation for item in evidence]),
        np.asarray([item.commitment_nonce for item in evidence], dtype=np.int64),
    )


def _proposal_rank_null_surface(
    observation: FloatArray,
    bank: FloatArray,
    handles: FloatArray,
    next_observation: FloatArray,
    config: CausalBoundaryConfig,
    *,
    selected_pair: tuple[int, int],
    null_rank: int,
) -> tuple[FloatArray, FloatArray]:
    """Estimate the lower-rank effect and nuisance surface on proposal rows."""

    handle_index, source_index = selected_pair
    outcome, interactions = _residual_problem(
        observation, bank, handles, next_observation, config
    )
    restricted, singular, _ = _reduced_rank_ridge_fit(
        interactions[:, handle_index, source_index],
        outcome,
        config.ridge,
        null_rank,
    )
    if null_rank:
        tolerance = (
            max(restricted.shape)
            * np.finfo(np.float64).eps
            * max(float(singular[0]), 1.0)
            * 64.0
        )
        if singular[null_rank - 1] <= tolerance:
            raise ValueError("proposal lower-rank surface is numerically deficient")
    nuisance, raw_interactions = _raw_designs(
        observation, bank, handles, config
    )
    remainder = (
        next_observation
        - raw_interactions[:, handle_index, source_index] @ restricted
    )
    nuisance_coefficient = _ridge_coefficients(
        nuisance, remainder, config.ridge
    )
    return restricted, nuisance_coefficient


def _null_preserving_outcome(
    observation: FloatArray,
    bank: FloatArray,
    handles: FloatArray,
    residual: FloatArray,
    restricted_effect: FloatArray,
    nuisance_coefficient: FloatArray,
    config: CausalBoundaryConfig,
    *,
    selected_pair: tuple[int, int],
) -> FloatArray:
    """Move a fitted lower-rank surface with a reassigned handle design."""

    handle_index, source_index = selected_pair
    nuisance, raw_interactions = _raw_designs(
        observation, bank, handles, config
    )
    return np.asarray(
        nuisance @ nuisance_coefficient
        + raw_interactions[:, handle_index, source_index] @ restricted_effect
        + residual,
        dtype=np.float64,
    )


def _pair_sharp_null_randomization_test(
    observation: FloatArray,
    bank: FloatArray,
    handles: FloatArray,
    next_observation: FloatArray,
    commitment_nonces: NDArray[np.int64],
    config: CausalBoundaryConfig,
    *,
    selected_pair: tuple[int, int],
    permutations: int,
    salt: int,
) -> tuple[float, float, float]:
    """Test one proposal-selected pair under the no-interaction sharp null."""

    count = _integer(permutations, "permutations", minimum=1)
    _monte_carlo_order(count, config.null_quantile)
    handle_index, source_index = selected_pair
    outcome, interactions = _residual_problem(
        observation, bank, handles, next_observation, config
    )
    observed = _rank_increment_statistic(
        interactions[:, handle_index, source_index], outcome, config.ridge, 0
    )
    groups = _commitment_block_groups(
        commitment_nonces, config.commitment_block_size
    )
    seed = np.random.SeedSequence(
        [
            config.seed,
            int(salt),
            len(observation),
            handle_index,
            source_index,
            int(commitment_nonces[groups[0][0]]),
            int(commitment_nonces[groups[-1][-1]]),
        ]
    )
    rng = np.random.default_rng(seed)
    null_statistics = np.empty(count, dtype=np.float64)
    for draw in range(count):
        randomized = _rerandomized_handles(
            handles, commitment_nonces, config.commitment_block_size, rng
        )
        null_outcome, null_interactions = _residual_problem(
            observation, bank, randomized, next_observation, config
        )
        null_statistics[draw] = _rank_increment_statistic(
            null_interactions[:, handle_index, source_index],
            null_outcome,
            config.ridge,
            0,
        )
    threshold = _monte_carlo_threshold(null_statistics, config.null_quantile)
    p_value = float(
        (1 + np.count_nonzero(null_statistics >= observed)) / (count + 1)
    )
    return float(observed), float(threshold), p_value


def _conditional_rank_randomization_test(
    proposal: tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]],
    confirmation: tuple[FloatArray, FloatArray, FloatArray, FloatArray, NDArray[np.int64]],
    config: CausalBoundaryConfig,
    *,
    selected_pair: tuple[int, int],
    null_rank: int,
    permutations: int,
    salt: int,
) -> tuple[float, float, float]:
    """Test one incremental mode while preserving proposal-fitted lower modes.

    The lower-rank effect and nuisance coefficients are fitted only on the
    disjoint proposal fold.  Each confirmation-fold handle reassignment moves
    that fitted surface with the reassigned design while retaining the
    confirmation row residual.  Because a composite null must be estimated,
    the add-one Monte Carlo value is asymptotic/bootstrap calibrated rather
    than an exact finite-sample Fisher p-value.
    """

    rank = _integer(null_rank, "null_rank", minimum=1)
    count = _integer(permutations, "permutations", minimum=1)
    _monte_carlo_order(count, config.null_quantile)
    proposal_observation, proposal_bank, proposal_handles, proposal_next, _ = proposal
    observation, bank, handles, next_observation, commitment_nonces = confirmation
    handle_index, source_index = selected_pair
    restricted, nuisance_coefficient = _proposal_rank_null_surface(
        proposal_observation,
        proposal_bank,
        proposal_handles,
        proposal_next,
        config,
        selected_pair=selected_pair,
        null_rank=rank,
    )
    outcome, interactions = _residual_problem(
        observation, bank, handles, next_observation, config
    )
    observed = _rank_increment_statistic(
        interactions[:, handle_index, source_index],
        outcome,
        config.ridge,
        rank,
    )
    nuisance, raw_interactions = _raw_designs(
        observation, bank, handles, config
    )
    residual = (
        next_observation
        - nuisance @ nuisance_coefficient
        - raw_interactions[:, handle_index, source_index] @ restricted
    )
    groups = _commitment_block_groups(
        commitment_nonces, config.commitment_block_size
    )
    seed = np.random.SeedSequence(
        [
            config.seed,
            int(salt),
            len(observation),
            handle_index,
            source_index,
            rank,
            int(commitment_nonces[groups[0][0]]),
            int(commitment_nonces[groups[-1][-1]]),
        ]
    )
    rng = np.random.default_rng(seed)
    null_statistics = np.empty(count, dtype=np.float64)
    for draw in range(count):
        randomized = _rerandomized_handles(
            handles, commitment_nonces, config.commitment_block_size, rng
        )
        pseudo_outcome = _null_preserving_outcome(
            observation,
            bank,
            randomized,
            residual,
            restricted,
            nuisance_coefficient,
            config,
            selected_pair=selected_pair,
        )
        null_outcome, null_interactions = _residual_problem(
            observation, bank, randomized, pseudo_outcome, config
        )
        null_statistics[draw] = _rank_increment_statistic(
            null_interactions[:, handle_index, source_index],
            null_outcome,
            config.ridge,
            rank,
        )
    threshold = _monte_carlo_threshold(null_statistics, config.null_quantile)
    p_value = float(
        (1 + np.count_nonzero(null_statistics >= observed)) / (count + 1)
    )
    return float(observed), float(threshold), p_value


def _paired_confirmation_confidence(
    value_a: float,
    value_b: float,
    threshold_a: float,
    threshold_b: float,
) -> float:
    margins = (
        (float(value_a) - float(threshold_a)) / (abs(float(value_a)) + 1e-12),
        (float(value_b) - float(threshold_b)) / (abs(float(value_b)) + 1e-12),
    )
    return float(np.clip(min(margins), 0.0, 1.0))


def _null_fit(config: CausalBoundaryConfig, *, ambiguous: bool = False) -> _FitResult:
    return _FitResult(
        selected_handle_index=None,
        selected_source_index=None,
        rank=0,
        internal_projector=_readonly(
            np.zeros((config.process_dim, config.process_dim))
        ),
        sensory_projector=_readonly(
            np.zeros((config.observation_dim, config.observation_dim))
        ),
        effect_operator=_readonly(
            np.zeros((config.process_dim, config.observation_dim))
        ),
        confidence=0.0,
        ambiguous=bool(ambiguous),
    )


def _aligned_complete_evidence(
    evidence: list[_Evidence], config: CausalBoundaryConfig
) -> list[_Evidence]:
    """Keep a newest even set of complete nonce-defined commitment blocks."""

    grouped: dict[int, dict[int, _Evidence] | None] = {}
    size = config.commitment_block_size
    for item in evidence:
        block_id = item.commitment_nonce // size
        block = grouped.setdefault(block_id, {})
        if block is None or item.commitment_nonce in block:
            grouped[block_id] = None
        else:
            block[item.commitment_nonce] = item
    complete: list[list[_Evidence]] = []
    for block_id in sorted(grouped):
        block = grouped[block_id]
        expected = range(block_id * size, (block_id + 1) * size)
        if block is not None and all(nonce in block for nonce in expected):
            complete.append([block[nonce] for nonce in expected])
    # The ordinary configured path always has an even number of complete
    # blocks.  If an interrupted commitment left a hole, fail closed by using
    # only the newest even set rather than creating a partial half-block.
    if len(complete) % 2:
        complete = complete[1:]
    return [item for block in complete for item in block]


def _fit_window_global_sharp_null(
    evidence: list[_Evidence], config: CausalBoundaryConfig
) -> _FitResult:
    evidence = _aligned_complete_evidence(evidence, config)
    if len(evidence) < config.minimum_samples:
        return _null_fit(config)
    observation = np.stack([item.observation for item in evidence])
    bank = np.stack([item.process_bank for item in evidence])
    handles = np.stack([item.handles for item in evidence])
    next_observation = np.stack([item.next_observation for item in evidence])
    commitment_nonces = np.asarray(
        [item.commitment_nonce for item in evidence], dtype=np.int64
    )
    outcome, interactions = _residual_problem(
        observation, bank, handles, next_observation, config
    )
    effects, _ = _operators(interactions, outcome, config)
    full_threshold = _familywise_threshold(
        observation,
        bank,
        handles,
        next_observation,
        commitment_nonces,
        config,
        permutations=config.null_permutations,
        salt=101,
    )

    midpoint = len(evidence) // 2
    outcome_a, interactions_a = _residual_problem(
        observation[:midpoint],
        bank[:midpoint],
        handles[:midpoint],
        next_observation[:midpoint],
        config,
    )
    outcome_b, interactions_b = _residual_problem(
        observation[midpoint:],
        bank[midpoint:],
        handles[midpoint:],
        next_observation[midpoint:],
        config,
    )
    effects_a, _ = _operators(interactions_a, outcome_a, config)
    effects_b, _ = _operators(interactions_b, outcome_b, config)
    threshold_a = _familywise_threshold(
        observation[:midpoint],
        bank[:midpoint],
        handles[:midpoint],
        next_observation[:midpoint],
        commitment_nonces[:midpoint],
        config,
        permutations=config.half_null_permutations,
        salt=103,
    )
    threshold_b = _familywise_threshold(
        observation[midpoint:],
        bank[midpoint:],
        handles[midpoint:],
        next_observation[midpoint:],
        commitment_nonces[midpoint:],
        config,
        permutations=config.half_null_permutations,
        salt=107,
    )

    mode_count = min(config.process_dim, config.observation_dim)
    masks = np.zeros(
        (config.handle_count, config.source_count, mode_count), dtype=bool
    )
    left_vectors: dict[tuple[int, int], FloatArray] = {}
    right_vectors: dict[tuple[int, int], FloatArray] = {}
    singular_values: dict[tuple[int, int], FloatArray] = {}
    replicated_confidences: dict[tuple[int, int], list[float]] = {}
    for handle_index in range(config.handle_count):
        for source_index in range(config.source_count):
            left, singular, right = np.linalg.svd(
                effects[handle_index, source_index], full_matrices=False
            )
            key = (handle_index, source_index)
            left_vectors[key] = left
            right_vectors[key] = right
            singular_values[key] = singular
            confidences: list[float] = []
            prior_modes_accepted = True
            for mode_index in range(mode_count):
                direction_left = left[:, mode_index]
                direction_right = right[mode_index]
                value_a = float(
                    direction_left
                    @ effects_a[handle_index, source_index]
                    @ direction_right
                )
                value_b = float(
                    direction_left
                    @ effects_b[handle_index, source_index]
                    @ direction_right
                )
                accepted = bool(
                    prior_modes_accepted
                    and _replicated_directional_mode(
                        float(singular[mode_index]),
                        value_a,
                        value_b,
                        float(full_threshold[mode_index]),
                        float(threshold_a[mode_index]),
                        float(threshold_b[mode_index]),
                    )
                )
                prior_modes_accepted = accepted
                masks[handle_index, source_index, mode_index] = accepted
                if accepted:
                    # Pair each statistic with the threshold from the same
                    # evidence split.  v0.29 instead subtracted the largest
                    # threshold from the smallest statistic, which could
                    # assign zero confidence to a mode that passed all three
                    # of its actual comparisons.
                    confidences.append(
                        _paired_mode_confidence(
                            float(singular[mode_index]),
                            value_a,
                            value_b,
                            float(full_threshold[mode_index]),
                            float(threshold_a[mode_index]),
                            float(threshold_b[mode_index]),
                        )
                    )
            replicated_confidences[key] = confidences

    pair_ranks = np.sum(masks, axis=2)
    selected_pairs = np.argwhere(pair_ranks > 0)
    if len(selected_pairs) != 1:
        return _null_fit(config, ambiguous=bool(len(selected_pairs) > 1))

    handle_index = int(selected_pairs[0, 0])
    source_index = int(selected_pairs[0, 1])
    key = (handle_index, source_index)
    selected_modes = np.flatnonzero(masks[handle_index, source_index])
    internal_basis = left_vectors[key][:, selected_modes]
    sensory_basis = right_vectors[key][selected_modes].T
    internal_projector = internal_basis @ internal_basis.T
    sensory_projector = sensory_basis @ sensory_basis.T
    truncated_effect = (
        internal_projector
        @ effects[handle_index, source_index]
        @ sensory_projector
    )
    confidence = float(
        np.clip(min(replicated_confidences[key]), 0.0, 1.0)
    )
    return _FitResult(
        selected_handle_index=handle_index,
        selected_source_index=source_index,
        rank=int(len(selected_modes)),
        internal_projector=_readonly(internal_projector),
        sensory_projector=_readonly(sensory_projector),
        effect_operator=_readonly(truncated_effect),
        confidence=confidence,
        ambiguous=False,
    )


def _fit_window_cross_fitted_reduced_rank(
    evidence: list[_Evidence], config: CausalBoundaryConfig
) -> _FitResult:
    """Select a pair, then test added modes on two untouched block folds."""

    aligned = _aligned_complete_evidence(evidence, config)
    if len(aligned) < config.minimum_samples:
        return _null_fit(config)
    try:
        proposal_rows, confirmation_a_rows, confirmation_b_rows = (
            _partition_inference_evidence(aligned, config)
        )
    except ValueError:
        return _null_fit(config)
    proposal = _evidence_arrays(proposal_rows)
    confirmation_a = _evidence_arrays(confirmation_a_rows)
    confirmation_b = _evidence_arrays(confirmation_b_rows)
    (
        proposal_observation,
        proposal_bank,
        proposal_handles,
        proposal_next,
        proposal_nonces,
    ) = proposal
    proposal_outcome, proposal_interactions = _residual_problem(
        proposal_observation,
        proposal_bank,
        proposal_handles,
        proposal_next,
        config,
    )
    proposal_effects, _ = _operators(
        proposal_interactions, proposal_outcome, config
    )
    proposal_threshold = _familywise_threshold(
        proposal_observation,
        proposal_bank,
        proposal_handles,
        proposal_next,
        proposal_nonces,
        config,
        permutations=config.null_permutations,
        salt=31_101,
    )
    first_mode = np.linalg.svd(proposal_effects, compute_uv=False)[..., 0]
    selected_pairs = np.argwhere(first_mode > proposal_threshold[0])
    if len(selected_pairs) != 1:
        return _null_fit(config, ambiguous=bool(len(selected_pairs) > 1))
    handle_index = int(selected_pairs[0, 0])
    source_index = int(selected_pairs[0, 1])
    selected_pair = (handle_index, source_index)
    first_a = _pair_sharp_null_randomization_test(
        *confirmation_a[:4],
        confirmation_a[4],
        config,
        selected_pair=selected_pair,
        permutations=config.half_null_permutations,
        salt=31_103,
    )
    first_b = _pair_sharp_null_randomization_test(
        *confirmation_b[:4],
        confirmation_b[4],
        config,
        selected_pair=selected_pair,
        permutations=config.half_null_permutations,
        salt=31_107,
    )
    if first_a[0] <= first_a[1] or first_b[0] <= first_b[1]:
        return _null_fit(config)
    confidence_parts = [
        _paired_confirmation_confidence(
            first_a[0], first_b[0], first_a[1], first_b[1]
        )
    ]
    admitted_rank = 1
    maximum_rank = min(config.process_dim, config.observation_dim)
    while admitted_rank < maximum_rank:
        try:
            mode_a = _conditional_rank_randomization_test(
                proposal,
                confirmation_a,
                config,
                selected_pair=selected_pair,
                null_rank=admitted_rank,
                permutations=config.half_null_permutations,
                salt=31_200 + 10 * admitted_rank + 1,
            )
            mode_b = _conditional_rank_randomization_test(
                proposal,
                confirmation_b,
                config,
                selected_pair=selected_pair,
                null_rank=admitted_rank,
                permutations=config.half_null_permutations,
                salt=31_200 + 10 * admitted_rank + 3,
            )
        except ValueError as exc:
            if "numerically deficient" not in str(exc):
                raise
            break
        if mode_a[0] <= mode_a[1] or mode_b[0] <= mode_b[1]:
            break
        confidence_parts.append(
            _paired_confirmation_confidence(
                mode_a[0], mode_b[0], mode_a[1], mode_b[1]
            )
        )
        admitted_rank += 1

    full_observation, full_bank, full_handles, full_next, _ = _evidence_arrays(
        aligned
    )
    full_outcome, full_interactions = _residual_problem(
        full_observation, full_bank, full_handles, full_next, config
    )
    restricted_effect, _, _ = _reduced_rank_ridge_fit(
        full_interactions[:, handle_index, source_index],
        full_outcome,
        config.ridge,
        admitted_rank,
    )
    left, singular, right = np.linalg.svd(
        restricted_effect, full_matrices=False
    )
    tolerance = (
        max(restricted_effect.shape)
        * np.finfo(np.float64).eps
        * max(float(singular[0]), 1.0)
        * 64.0
    )
    if np.count_nonzero(singular > tolerance) != admitted_rank:
        return _null_fit(config)
    internal_basis = left[:, :admitted_rank]
    sensory_basis = right[:admitted_rank].T
    internal_projector = internal_basis @ internal_basis.T
    sensory_projector = sensory_basis @ sensory_basis.T
    confidence = float(np.clip(min(confidence_parts), 0.0, 1.0))
    return _FitResult(
        selected_handle_index=handle_index,
        selected_source_index=source_index,
        rank=admitted_rank,
        internal_projector=_readonly(internal_projector),
        sensory_projector=_readonly(sensory_projector),
        effect_operator=_readonly(restricted_effect),
        confidence=confidence,
        ambiguous=False,
    )


def _fit_window(
    evidence: list[_Evidence], config: CausalBoundaryConfig
) -> _FitResult:
    if config.higher_mode_null == "global_sharp_null":
        return _fit_window_global_sharp_null(evidence, config)
    if (
        config.higher_mode_null
        == "cross_fitted_reduced_rank_randomization_bootstrap"
    ):
        return _fit_window_cross_fitted_reduced_rank(evidence, config)
    raise RuntimeError("unsupported higher-mode null configuration")


class OnlineCausalSelfBoundary:
    """Own, learn, retain, and revise one anonymous causal self-boundary."""

    def __init__(self, config: CausalBoundaryConfig) -> None:
        if not isinstance(config, CausalBoundaryConfig):
            raise TypeError("config must be a CausalBoundaryConfig")
        self.config = config
        self._evidence: list[_Evidence] = []
        self._pending_commitment: CausalHandleCommitment | None = None
        self._pending_transition: _PendingTransition | None = None
        self._commit_count = 0
        self._completed_count = 0
        self._fit_count = 0
        self._updates_frozen = False
        self._candidate_signature: tuple[int, int, int] | None = None
        self._candidate_streak = 0
        self._candidate_last_evidence_count: int | None = None
        self._miss_streak = 0
        self._miss_last_evidence_count: int | None = None
        self._last_receipt: CausalBoundaryUpdateReceipt | None = None
        self._interrupted_transitions = 0
        self._state = self._initial_state()

    @property
    def descriptor_dim(self) -> int:
        return (
            self.config.observation_dim
            + self.config.process_dim
            + self.config.handle_count
            + self.config.source_count
            + 5
        )

    @property
    def updates_frozen(self) -> bool:
        return self._updates_frozen

    @property
    def state(self) -> CausalBoundaryState:
        return self._copy_state(self._state)

    @property
    def last_receipt(self) -> CausalBoundaryUpdateReceipt | None:
        return copy.deepcopy(self._last_receipt)

    @property
    def has_pending(self) -> bool:
        return self._pending_commitment is not None or self._pending_transition is not None

    @property
    def has_pending_commitment(self) -> bool:
        """Whether an emitted commitment still requires a source binding."""

        return self._pending_commitment is not None

    @property
    def has_bound_transition(self) -> bool:
        """Whether the next observation must reveal a bound transition."""

        return self._pending_transition is not None

    @property
    def interrupted_transitions(self) -> int:
        """Count explicit resets/loads that interrupted pending causal work."""

        return self._interrupted_transitions

    @property
    def pending_commitment(self) -> CausalHandleCommitment | None:
        """Return a read-only copy of the commitment awaiting a binding."""

        if self._pending_commitment is None:
            return None
        return self._copy_commitment(self._pending_commitment)

    @property
    def pending_transition_digest(self) -> str | None:
        """Return the digest of the transition awaiting its exact outcome."""

        if self._pending_transition is None:
            return None
        return self._pending_transition.transition_digest

    @property
    def bound_process_bank(self) -> FloatArray | None:
        """Return a read-only copy of the anonymous bank awaiting reveal."""

        if self._pending_transition is None:
            return None
        return _readonly(self._pending_transition.process_bank)

    @property
    def bound_handles(self) -> FloatArray | None:
        """Return a read-only copy of the handles paired with the bound bank."""

        if self._pending_transition is None:
            return None
        return _readonly(self._pending_transition.commitment.handles)

    def _initial_state(self, *, epoch: int = 0, alarm: float = 0.0) -> CausalBoundaryState:
        state = CausalBoundaryState(
            selected_handle_index=None,
            selected_source_index=None,
            rank=0,
            internal_projector=_readonly(
                np.zeros((self.config.process_dim, self.config.process_dim))
            ),
            sensory_projector=_readonly(
                np.zeros((self.config.observation_dim, self.config.observation_dim))
            ),
            effect_operator=_readonly(
                np.zeros((self.config.process_dim, self.config.observation_dim))
            ),
            confidence=0.0,
            uncertainty=1.0,
            change_alarm=float(alarm),
            evidence_count=self._completed_count,
            fit_count=self._fit_count,
            age=0,
            epoch=int(epoch),
            model_digest="",
        )
        return replace(state, model_digest=self._state_digest(state))

    @staticmethod
    def _copy_state(state: CausalBoundaryState) -> CausalBoundaryState:
        return replace(
            state,
            internal_projector=_readonly(state.internal_projector),
            sensory_projector=_readonly(state.sensory_projector),
            effect_operator=_readonly(state.effect_operator),
        )

    @staticmethod
    def _copy_commitment(
        commitment: CausalHandleCommitment,
    ) -> CausalHandleCommitment:
        return replace(commitment, handles=_readonly(commitment.handles))

    def __deepcopy__(self, memo: dict[int, Any]) -> "OnlineCausalSelfBoundary":
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        clone = type(self)(self.config)
        memo[id(self)] = clone
        clone.load_snapshot(self.snapshot())
        return clone

    @staticmethod
    def _state_payload(state: CausalBoundaryState) -> dict[str, Any]:
        return {
            "selected_handle_index": state.selected_handle_index,
            "selected_source_index": state.selected_source_index,
            "rank": state.rank,
            "internal_projector": state.internal_projector,
            "sensory_projector": state.sensory_projector,
            "effect_operator": state.effect_operator,
            "confidence": state.confidence,
            "uncertainty": state.uncertainty,
            "change_alarm": state.change_alarm,
            "evidence_count": state.evidence_count,
            "fit_count": state.fit_count,
            "age": state.age,
            "epoch": state.epoch,
        }

    def _state_digest(self, state: CausalBoundaryState) -> str:
        return _digest(self._state_payload(state))

    def _replace_state(self, **changes: Any) -> None:
        candidate = replace(self._state, **changes, model_digest="")
        self._state = replace(candidate, model_digest=self._state_digest(candidate))

    def _handle_block(self, block_index: int) -> FloatArray:
        rng = np.random.default_rng(
            np.random.SeedSequence([self.config.seed, 29_001, int(block_index)])
        )
        block = np.empty(
            (self.config.commitment_block_size, self.config.handle_count),
            dtype=np.float64,
        )
        base = np.concatenate(
            (
                np.zeros(self.config.commitment_block_size // 2),
                np.ones(self.config.commitment_block_size // 2),
            )
        )
        for handle_index in range(self.config.handle_count):
            block[:, handle_index] = base[rng.permutation(len(base))]
        return block

    def commit_handles(self, *, time: int) -> CausalHandleCommitment:
        """Generate and commit anonymous handle values before source realization."""

        timestamp = _integer(time, "time", minimum=0)
        if self.has_pending:
            raise RuntimeError("a causal commitment or transition is already pending")
        nonce = self._commit_count
        block_index, row_index = divmod(nonce, self.config.commitment_block_size)
        handles = _readonly(self._handle_block(block_index)[row_index])
        payload = {
            "schema": COMMITMENT_SCHEMA,
            "time": timestamp,
            "nonce": nonce,
            "handles": handles,
        }
        commitment = CausalHandleCommitment(
            time=timestamp,
            nonce=nonce,
            handles=handles,
            digest=_digest(payload),
        )
        self._pending_commitment = commitment
        self._commit_count += 1
        return self._copy_commitment(commitment)

    def validate_pending_commitment(
        self, commitment: CausalHandleCommitment
    ) -> CausalHandleCommitment:
        """Return the private committed value only after complete equality.

        The public receipt is immutable, but callers can construct a different
        dataclass instance that retains a valid digest.  Comparing every field
        prevents a forged handle array from reaching the broadcast path while
        the private learner binds the original committed handles.
        """

        if not isinstance(commitment, CausalHandleCommitment):
            raise TypeError("commitment must be a CausalHandleCommitment")
        pending = self._pending_commitment
        if pending is None or self._pending_transition is not None:
            raise RuntimeError("no unbound causal handle commitment is pending")
        matches = bool(
            commitment.time == pending.time
            and commitment.nonce == pending.nonce
            and commitment.digest == pending.digest
            and np.array_equal(commitment.handles, pending.handles)
        )
        if not matches:
            raise ValueError("commitment does not match the pending commitment")
        expected = _digest(
            {
                "schema": COMMITMENT_SCHEMA,
                "time": pending.time,
                "nonce": pending.nonce,
                "handles": pending.handles,
            }
        )
        if pending.digest != expected:
            raise RuntimeError("the pending causal commitment failed integrity validation")
        return self._copy_commitment(pending)

    def bind_sources(
        self,
        observation: ArrayLike,
        process_bank: ArrayLike,
        *,
        commitment_digest: str,
        time: int,
    ) -> BoundCausalTransition:
        """Bind a committed handle vector to the now-realized anonymous bank."""

        timestamp = _integer(time, "time", minimum=0)
        if self._pending_commitment is None or self._pending_transition is not None:
            raise RuntimeError("no unbound causal handle commitment is pending")
        commitment = self._pending_commitment
        if not isinstance(commitment_digest, str) or commitment_digest != commitment.digest:
            raise ValueError("commitment digest does not match the pending commitment")
        if timestamp != commitment.time:
            raise ValueError("source binding time must equal commitment time")
        current = _readonly(
            _array(
                observation,
                (self.config.observation_dim,),
                "observation",
            )
        )
        bank = _readonly(
            _array(
                process_bank,
                (self.config.source_count, self.config.process_dim),
                "process_bank",
            )
        )
        payload = {
            "schema": TRANSITION_SCHEMA,
            "time": timestamp,
            "commitment_digest": commitment.digest,
            "observation": current,
            "process_bank": bank,
        }
        transition_digest = _digest(payload)
        self._pending_transition = _PendingTransition(
            time=timestamp,
            observation=current,
            process_bank=bank,
            commitment=commitment,
            transition_digest=transition_digest,
        )
        self._pending_commitment = None
        return BoundCausalTransition(
            time=timestamp,
            commitment_digest=commitment.digest,
            transition_digest=transition_digest,
        )

    def _prequential_alignment(
        self, transition: _PendingTransition, next_observation: FloatArray
    ) -> float:
        state = self._state
        if not state.active:
            return 0.0
        handle = transition.commitment.handles[state.selected_handle_index]
        source = transition.process_bank[state.selected_source_index]
        signal = handle * source @ state.internal_projector
        predicted = signal @ state.effect_operator
        observed = (
            next_observation - transition.observation
        ) @ state.sensory_projector
        denominator = float(np.linalg.norm(predicted) * np.linalg.norm(observed))
        if denominator <= 1e-12:
            return 0.0
        return float(np.clip(np.dot(predicted, observed) / denominator, -1.0, 1.0))

    def _should_fit(self) -> bool:
        return bool(
            not self._updates_frozen
            and self._completed_count >= self.config.minimum_samples
            and (
                self._completed_count - self.config.minimum_samples
            )
            % self.config.fit_interval
            == 0
        )

    def _accept_fit(self, fit: _FitResult, *, revision: bool) -> None:
        epoch = self._state.epoch + (1 if revision or not self._state.active else 0)
        state = CausalBoundaryState(
            selected_handle_index=fit.selected_handle_index,
            selected_source_index=fit.selected_source_index,
            rank=fit.rank,
            internal_projector=_readonly(fit.internal_projector),
            sensory_projector=_readonly(fit.sensory_projector),
            effect_operator=_readonly(fit.effect_operator),
            confidence=float(fit.confidence),
            uncertainty=float(1.0 - fit.confidence),
            change_alarm=1.0 if revision else 0.0,
            evidence_count=self._completed_count,
            fit_count=self._fit_count,
            age=0 if revision or not self._state.active else self._state.age,
            epoch=epoch,
            model_digest="",
        )
        self._state = replace(state, model_digest=self._state_digest(state))
        self._candidate_signature = None
        self._candidate_streak = 0
        self._candidate_last_evidence_count = None
        self._miss_streak = 0
        self._miss_last_evidence_count = None

    def _confirmation_due(self, last_evidence_count: int | None) -> bool:
        return bool(
            last_evidence_count is None
            or self._completed_count - last_evidence_count
            >= self.config.structural_confirmation_interval
        )

    def _update_candidate(self, signature: tuple[int, int, int]) -> bool:
        """Start or renew a structural proposal using prospectively new rows."""

        if signature != self._candidate_signature:
            self._candidate_signature = signature
            self._candidate_streak = 1
            self._candidate_last_evidence_count = self._completed_count
            return True
        if self._confirmation_due(self._candidate_last_evidence_count):
            self._candidate_streak += 1
            self._candidate_last_evidence_count = self._completed_count
            return True
        return False

    def _apply_fit(
        self, fit: _FitResult
    ) -> tuple[bool, bool, bool, bool, str, bool, bool]:
        revised = False
        revoked = False
        acquired = False
        rank_changed = False
        structural_event = "none"
        candidate_renewed = False
        null_renewed = False
        if fit.selected_handle_index is None or fit.selected_source_index is None:
            self._candidate_signature = None
            self._candidate_streak = 0
            self._candidate_last_evidence_count = None
            if self._state.active and self._confirmation_due(
                self._miss_last_evidence_count
            ):
                self._miss_streak += 1
                self._miss_last_evidence_count = self._completed_count
                null_renewed = True
            if self._state.active and self._miss_streak >= self.config.revocation_confirmations:
                epoch = self._state.epoch + 1
                self._state = self._initial_state(epoch=epoch, alarm=1.0)
                self._miss_streak = 0
                self._miss_last_evidence_count = None
                revoked = True
                structural_event = "revocation"
            elif self._state.active:
                confidence = max(
                    np.finfo(np.float64).tiny,
                    self._state.confidence * self.config.confidence_decay,
                )
                self._replace_state(
                    confidence=confidence,
                    uncertainty=1.0 - confidence,
                    change_alarm=min(1.0, self._state.change_alarm + 0.35),
                    fit_count=self._fit_count,
                    evidence_count=self._completed_count,
                )
                structural_event = "null_candidate"
            else:
                self._miss_streak = 0
                self._miss_last_evidence_count = None
                self._replace_state(
                    fit_count=self._fit_count,
                    evidence_count=self._completed_count,
                )
                structural_event = "null_fit"
            return (
                revised,
                revoked,
                acquired,
                rank_changed,
                structural_event,
                candidate_renewed,
                null_renewed,
            )

        signature = (
            fit.selected_handle_index,
            fit.selected_source_index,
            fit.rank,
        )
        current_signature = (
            self._state.selected_handle_index,
            self._state.selected_source_index,
            self._state.rank,
        )
        if not self._state.active:
            self._miss_streak = 0
            self._miss_last_evidence_count = None
            candidate_renewed = self._update_candidate(signature)
            self._replace_state(
                fit_count=self._fit_count,
                evidence_count=self._completed_count,
            )
            if self._candidate_streak >= self.config.revision_confirmations:
                self._accept_fit(fit, revision=False)
                acquired = True
                structural_event = "acquisition"
            else:
                structural_event = "acquisition_candidate"
        elif signature == current_signature:
            self._accept_fit(fit, revision=False)
            structural_event = "parameter_refresh"
        else:
            self._miss_streak = 0
            self._miss_last_evidence_count = None
            candidate_renewed = self._update_candidate(signature)
            confidence = max(
                np.finfo(np.float64).tiny,
                self._state.confidence * self.config.confidence_decay,
            )
            self._replace_state(
                confidence=confidence,
                uncertainty=1.0 - confidence,
                change_alarm=min(1.0, self._state.change_alarm + 0.45),
                fit_count=self._fit_count,
                evidence_count=self._completed_count,
            )
            if self._candidate_streak >= self.config.revision_confirmations:
                prior_pair = current_signature[:2]
                next_pair = signature[:2]
                self._accept_fit(fit, revision=True)
                revised = True
                rank_changed = bool(
                    prior_pair == next_pair
                    and current_signature[2] != signature[2]
                )
                structural_event = (
                    "rank_revision" if rank_changed else "pair_revision"
                )
            else:
                structural_event = "structural_candidate"
        return (
            revised,
            revoked,
            acquired,
            rank_changed,
            structural_event,
            candidate_renewed,
            null_renewed,
        )

    def reveal_outcome(
        self,
        next_observation: ArrayLike,
        *,
        transition_digest: str,
        time: int,
    ) -> CausalBoundaryUpdateReceipt:
        """Score and retain exactly one actually revealed next observation."""

        timestamp = _integer(time, "time", minimum=0)
        if self._pending_transition is None:
            raise RuntimeError("no bound causal transition is pending")
        transition = self._pending_transition
        if not isinstance(transition_digest, str) or transition_digest != transition.transition_digest:
            raise ValueError("transition digest does not match the pending transition")
        if timestamp <= transition.time:
            raise ValueError("outcome time must follow commitment and binding time")
        outcome = _readonly(
            _array(
                next_observation,
                (self.config.observation_dim,),
                "next_observation",
            )
        )
        prior_state = self._state
        before = prior_state.model_digest
        alignment = self._prequential_alignment(transition, outcome)
        outcome_digest = _digest(
            {
                "schema": OUTCOME_SCHEMA,
                "transition_digest": transition.transition_digest,
                "reveal_time": timestamp,
                "next_observation": outcome,
            }
        )
        # A fit is part of the reveal transaction.  Retain exact references to
        # the immutable pre-state so any numerical or inference exception can
        # restore the bound transition for a safe retry instead of consuming
        # half a causal record.
        rollback = (
            self._evidence.copy(),
            self._pending_transition,
            self._completed_count,
            self._fit_count,
            self._state,
            self._candidate_signature,
            self._candidate_streak,
            self._candidate_last_evidence_count,
            self._miss_streak,
            self._miss_last_evidence_count,
            self._last_receipt,
        )
        try:
            self._evidence.append(
                _Evidence(
                    observation=transition.observation,
                    process_bank=transition.process_bank,
                    handles=transition.commitment.handles,
                    next_observation=outcome,
                    commitment_time=transition.commitment.time,
                    commitment_nonce=transition.commitment.nonce,
                    commitment_digest=transition.commitment.digest,
                    transition_digest=transition.transition_digest,
                    reveal_time=timestamp,
                    outcome_digest=outcome_digest,
                )
            )
            if len(self._evidence) > self.config.evidence_capacity:
                self._evidence.pop(0)
            self._pending_transition = None
            self._completed_count += 1
            self._replace_state(
                evidence_count=self._completed_count,
                age=self._state.age + 1,
                change_alarm=float(
                    np.clip(
                        0.97 * self._state.change_alarm
                        + (
                            0.03
                            if self._state.active and alignment < 0.0
                            else 0.0
                        ),
                        0.0,
                        1.0,
                    )
                ),
            )
            fit_performed = self._should_fit()
            revised = False
            revoked = False
            acquired = False
            rank_changed = False
            structural_event = "none"
            candidate_renewed = False
            null_renewed = False
            fit: _FitResult | None = None
            if fit_performed:
                self._fit_count += 1
                window = self._evidence[-self.config.evidence_capacity :]
                fit = _fit_window(window, self.config)
                (
                    revised,
                    revoked,
                    acquired,
                    rank_changed,
                    structural_event,
                    candidate_renewed,
                    null_renewed,
                ) = self._apply_fit(fit)
            candidate = self._candidate_signature
            receipt = CausalBoundaryUpdateReceipt(
                commitment_digest=transition.commitment.digest,
                transition_digest=transition.transition_digest,
                outcome_digest=outcome_digest,
                reveal_time=timestamp,
                model_digest_before=before,
                model_digest_after=self._state.model_digest,
                evidence_count=self._completed_count,
                fit_performed=fit_performed,
                acquired=acquired,
                revised=revised,
                revoked=revoked,
                rank_changed=rank_changed,
                structural_event=structural_event,
                updates_frozen=self._updates_frozen,
                prequential_alignment=alignment,
                confidence_before=prior_state.confidence,
                previous_handle_index=prior_state.selected_handle_index,
                previous_source_index=prior_state.selected_source_index,
                previous_rank=prior_state.rank,
                fit_handle_index=(
                    None if fit is None else fit.selected_handle_index
                ),
                fit_source_index=(
                    None if fit is None else fit.selected_source_index
                ),
                fit_rank=(0 if fit is None else fit.rank),
                fit_confidence=(0.0 if fit is None else fit.confidence),
                selected_handle_index=self._state.selected_handle_index,
                selected_source_index=self._state.selected_source_index,
                rank=self._state.rank,
                confidence=self._state.confidence,
                change_alarm=self._state.change_alarm,
                candidate_handle_index=(None if candidate is None else candidate[0]),
                candidate_source_index=(None if candidate is None else candidate[1]),
                candidate_rank=(0 if candidate is None else candidate[2]),
                candidate_streak=self._candidate_streak,
                candidate_last_evidence_count=(
                    self._candidate_last_evidence_count
                ),
                candidate_renewed=candidate_renewed,
                null_streak=self._miss_streak,
                null_last_evidence_count=self._miss_last_evidence_count,
                null_renewed=null_renewed,
                epoch=self._state.epoch,
            )
            self._last_receipt = receipt
        except Exception:
            (
                self._evidence,
                self._pending_transition,
                self._completed_count,
                self._fit_count,
                self._state,
                self._candidate_signature,
                self._candidate_streak,
                self._candidate_last_evidence_count,
                self._miss_streak,
                self._miss_last_evidence_count,
                self._last_receipt,
            ) = rollback
            raise
        return copy.deepcopy(receipt)

    def candidate_signal(
        self, process_bank: ArrayLike, handles: ArrayLike
    ) -> FloatArray:
        bank = _array(
            process_bank,
            (self.config.source_count, self.config.process_dim),
            "process_bank",
        )
        gates = _array(handles, (self.config.handle_count,), "handles")
        state = self._state
        if not state.active:
            return np.zeros(self.config.process_dim, dtype=np.float64)
        return np.asarray(
            (
                gates[state.selected_handle_index]
                * bank[state.selected_source_index]
            )
            @ state.internal_projector,
            dtype=np.float64,
        )

    def descriptor(
        self,
        observation: ArrayLike,
        process_bank: ArrayLike | None = None,
        handles: ArrayLike | None = None,
    ) -> FloatArray:
        """Return a fixed-width, bounded globally broadcastable representation."""

        current = _array(
            observation,
            (self.config.observation_dim,),
            "observation",
        )
        if (process_bank is None) != (handles is None):
            raise ValueError("process_bank and handles must be supplied together")
        if process_bank is None:
            signal = np.zeros(self.config.process_dim, dtype=np.float64)
        else:
            signal = self.candidate_signal(process_bank, handles)
        sensory = self._state.sensory_projector @ current
        handle_identity = np.zeros(self.config.handle_count, dtype=np.float64)
        source_identity = np.zeros(self.config.source_count, dtype=np.float64)
        if self._state.active:
            handle_identity[self._state.selected_handle_index] = 1.0
            source_identity[self._state.selected_source_index] = 1.0
        max_rank = max(1, min(self.config.process_dim, self.config.observation_dim))
        telemetry = np.asarray(
            [
                self._state.confidence,
                self._state.uncertainty,
                self._state.change_alarm,
                self._state.rank / max_rank,
                np.tanh(self._state.age / max(self.config.fit_interval, 1)),
            ],
            dtype=np.float64,
        )
        return np.asarray(
            np.clip(
                np.concatenate(
                    (
                        np.tanh(sensory),
                        np.tanh(signal),
                        handle_identity,
                        source_identity,
                        telemetry,
                    )
                ),
                -1.0,
                1.0,
            ),
            dtype=np.float64,
        )

    def freeze(self) -> None:
        self._updates_frozen = True

    def unfreeze(self) -> None:
        self._updates_frozen = False

    def reset_pending(self) -> None:
        """Discard incomplete work and explicitly record a broken chain."""

        if self.has_pending:
            self._interrupted_transitions += 1
        self._pending_commitment = None
        self._pending_transition = None

    def record_interruption(self, count: int = 1) -> None:
        """Record a caller-level replacement of an incomplete causal chain."""

        self._interrupted_transitions += _integer(
            count, "interruption_count", minimum=1
        )

    def clear_model(self, *, retain_evidence: bool = False) -> None:
        """Explicitly erase learned boundary state; this is never implicit."""

        self.reset_pending()
        if not retain_evidence:
            self._evidence = []
            self._completed_count = 0
        self._fit_count = 0
        self._candidate_signature = None
        self._candidate_streak = 0
        self._candidate_last_evidence_count = None
        self._miss_streak = 0
        self._miss_last_evidence_count = None
        self._last_receipt = None
        self._state = self._initial_state(epoch=self._state.epoch + 1)

    def snapshot(self) -> dict[str, Any]:
        """Return a complete, digest-protected continuation snapshot."""

        state_payload = {
            **self._state_payload(self._state),
            "model_digest": self._state.model_digest,
        }
        evidence_payload = [
            {
                "observation": item.observation.copy(),
                "process_bank": item.process_bank.copy(),
                "handles": item.handles.copy(),
                "next_observation": item.next_observation.copy(),
                "commitment_time": item.commitment_time,
                "commitment_nonce": item.commitment_nonce,
                "commitment_digest": item.commitment_digest,
                "transition_digest": item.transition_digest,
                "reveal_time": item.reveal_time,
                "outcome_digest": item.outcome_digest,
            }
            for item in self._evidence
        ]
        commitment_payload = None
        if self._pending_commitment is not None:
            commitment_payload = {
                "time": self._pending_commitment.time,
                "nonce": self._pending_commitment.nonce,
                "handles": self._pending_commitment.handles.copy(),
                "digest": self._pending_commitment.digest,
            }
        transition_payload = None
        if self._pending_transition is not None:
            transition_payload = {
                "time": self._pending_transition.time,
                "observation": self._pending_transition.observation.copy(),
                "process_bank": self._pending_transition.process_bank.copy(),
                "commitment": {
                    "time": self._pending_transition.commitment.time,
                    "nonce": self._pending_transition.commitment.nonce,
                    "handles": self._pending_transition.commitment.handles.copy(),
                    "digest": self._pending_transition.commitment.digest,
                },
                "transition_digest": self._pending_transition.transition_digest,
            }
        receipt_payload = asdict(self._last_receipt) if self._last_receipt else None
        payload: dict[str, Any] = {
            "schema": SNAPSHOT_SCHEMA,
            "config": asdict(self.config),
            "state": state_payload,
            "evidence": evidence_payload,
            "pending_commitment": commitment_payload,
            "pending_transition": transition_payload,
            "commit_count": self._commit_count,
            "completed_count": self._completed_count,
            "fit_count": self._fit_count,
            "updates_frozen": self._updates_frozen,
            "candidate_signature": self._candidate_signature,
            "candidate_streak": self._candidate_streak,
            "candidate_last_evidence_count": self._candidate_last_evidence_count,
            "miss_streak": self._miss_streak,
            "miss_last_evidence_count": self._miss_last_evidence_count,
            "last_receipt": receipt_payload,
            "interrupted_transitions": self._interrupted_transitions,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)

    def _load_commitment(self, value: Mapping[str, Any]) -> CausalHandleCommitment:
        if not isinstance(value, Mapping):
            raise ValueError("snapshot commitment must be a mapping")
        commitment = CausalHandleCommitment(
            time=_integer(value["time"], "commitment.time", minimum=0),
            nonce=_integer(value["nonce"], "commitment.nonce", minimum=0),
            handles=_readonly(
                _array(
                    value["handles"],
                    (self.config.handle_count,),
                    "commitment.handles",
                )
            ),
            digest=_sha256_text(value["digest"], "commitment.digest"),
        )
        expected = _digest(
            {
                "schema": COMMITMENT_SCHEMA,
                "time": commitment.time,
                "nonce": commitment.nonce,
                "handles": commitment.handles,
            }
        )
        if commitment.digest != expected:
            raise ValueError("snapshot commitment digest mismatch")
        block_index, row_index = divmod(
            commitment.nonce, self.config.commitment_block_size
        )
        expected_handles = self._handle_block(block_index)[row_index]
        if not np.array_equal(commitment.handles, expected_handles):
            raise ValueError("snapshot commitment does not match the owned schedule")
        return commitment

    def load_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        """Validate and atomically load an exact continuation snapshot."""

        if not isinstance(snapshot, Mapping):
            raise TypeError("causal boundary snapshot must be a mapping")
        payload = copy.deepcopy(dict(snapshot))
        observed_digest = payload.pop("digest", None)
        if not isinstance(observed_digest, str) or observed_digest != _digest(payload):
            raise ValueError("causal boundary snapshot digest mismatch")
        if payload.get("schema") != SNAPSHOT_SCHEMA:
            raise ValueError("unsupported causal boundary snapshot schema")
        if payload.get("config") != asdict(self.config):
            raise ValueError("causal boundary snapshot config does not match")
        replacing_pending = self.has_pending

        raw_state = payload["state"]
        if not isinstance(raw_state, Mapping):
            raise ValueError("snapshot state must be a mapping")
        state = CausalBoundaryState(
            selected_handle_index=_optional_integer(
                raw_state["selected_handle_index"],
                "state.selected_handle_index",
            ),
            selected_source_index=_optional_integer(
                raw_state["selected_source_index"],
                "state.selected_source_index",
            ),
            rank=_integer(raw_state["rank"], "state.rank", minimum=0),
            internal_projector=_readonly(
                _array(
                    raw_state["internal_projector"],
                    (self.config.process_dim, self.config.process_dim),
                    "state.internal_projector",
                )
            ),
            sensory_projector=_readonly(
                _array(
                    raw_state["sensory_projector"],
                    (self.config.observation_dim, self.config.observation_dim),
                    "state.sensory_projector",
                )
            ),
            effect_operator=_readonly(
                _array(
                    raw_state["effect_operator"],
                    (self.config.process_dim, self.config.observation_dim),
                    "state.effect_operator",
                )
            ),
            confidence=_finite_float(raw_state["confidence"], "state.confidence"),
            uncertainty=_finite_float(raw_state["uncertainty"], "state.uncertainty"),
            change_alarm=_finite_float(raw_state["change_alarm"], "state.change_alarm"),
            evidence_count=_integer(raw_state["evidence_count"], "state.evidence_count"),
            fit_count=_integer(raw_state["fit_count"], "state.fit_count"),
            age=_integer(raw_state["age"], "state.age"),
            epoch=_integer(raw_state["epoch"], "state.epoch"),
            model_digest=_sha256_text(
                raw_state["model_digest"], "state.model_digest"
            ),
        )
        if state.model_digest != self._state_digest(state):
            raise ValueError("snapshot model digest mismatch")
        for index_name, index_value, limit in (
            ("selected_handle_index", state.selected_handle_index, self.config.handle_count),
            ("selected_source_index", state.selected_source_index, self.config.source_count),
        ):
            if index_value is not None and not 0 <= int(index_value) < limit:
                raise ValueError(f"snapshot {index_name} is out of bounds")
        if not 0.0 <= state.confidence <= 1.0 or not 0.0 <= state.uncertainty <= 1.0:
            raise ValueError("snapshot confidence values are out of bounds")
        if not 0.0 <= state.change_alarm <= 1.0:
            raise ValueError("snapshot change alarm is out of bounds")
        if not np.isclose(
            state.confidence + state.uncertainty,
            1.0,
            rtol=0.0,
            atol=1e-12,
        ):
            raise ValueError("snapshot confidence and uncertainty must sum to one")
        has_handle = state.selected_handle_index is not None
        has_source = state.selected_source_index is not None
        if has_handle != has_source:
            raise ValueError("snapshot selected pair must be wholly active or null")
        maximum_rank = min(self.config.process_dim, self.config.observation_dim)
        if has_handle:
            if not 1 <= state.rank <= maximum_rank:
                raise ValueError("snapshot active state rank is out of bounds")
            if state.confidence <= 0.0:
                raise ValueError("snapshot active state confidence must be positive")
            _validate_projector(
                state.internal_projector,
                state.rank,
                "internal_projector",
            )
            _validate_projector(
                state.sensory_projector,
                state.rank,
                "sensory_projector",
            )
            if _matrix_rank(state.effect_operator) != state.rank:
                raise ValueError(
                    "snapshot effect_operator rank does not match state.rank"
                )
            containment_tolerance = 1e-9 * max(
                1.0, float(np.linalg.norm(state.effect_operator))
            )
            if not np.allclose(
                state.internal_projector @ state.effect_operator,
                state.effect_operator,
                rtol=0.0,
                atol=containment_tolerance,
            ):
                raise ValueError(
                    "snapshot effect_operator escapes the internal projector"
                )
            if not np.allclose(
                state.effect_operator @ state.sensory_projector,
                state.effect_operator,
                rtol=0.0,
                atol=containment_tolerance,
            ):
                raise ValueError(
                    "snapshot effect_operator escapes the sensory projector"
                )
        else:
            if state.rank != 0:
                raise ValueError("snapshot null state must have rank zero")
            if state.confidence != 0.0 or state.uncertainty != 1.0:
                raise ValueError(
                    "snapshot null state must have zero confidence and full uncertainty"
                )
            if any(
                np.count_nonzero(value)
                for value in (
                    state.internal_projector,
                    state.sensory_projector,
                    state.effect_operator,
                )
            ):
                raise ValueError("snapshot null state operators must be exactly zero")

        evidence: list[_Evidence] = []
        raw_evidence = payload["evidence"]
        if not isinstance(raw_evidence, (tuple, list)):
            raise ValueError("snapshot evidence must be a sequence")
        for raw in raw_evidence:
            if not isinstance(raw, Mapping):
                raise ValueError("snapshot evidence entries must be mappings")
            item = _Evidence(
                    observation=_readonly(
                        _array(
                            raw["observation"],
                            (self.config.observation_dim,),
                            "evidence.observation",
                        )
                    ),
                    process_bank=_readonly(
                        _array(
                            raw["process_bank"],
                            (self.config.source_count, self.config.process_dim),
                            "evidence.process_bank",
                        )
                    ),
                    handles=_readonly(
                        _array(
                            raw["handles"],
                            (self.config.handle_count,),
                            "evidence.handles",
                        )
                    ),
                    next_observation=_readonly(
                        _array(
                            raw["next_observation"],
                            (self.config.observation_dim,),
                            "evidence.next_observation",
                        )
                    ),
                    commitment_time=_integer(
                        raw["commitment_time"],
                        "evidence.commitment_time",
                    ),
                    commitment_nonce=_integer(
                        raw["commitment_nonce"],
                        "evidence.commitment_nonce",
                    ),
                    commitment_digest=_sha256_text(
                        raw["commitment_digest"],
                        "evidence.commitment_digest",
                    ),
                    transition_digest=_sha256_text(
                        raw["transition_digest"],
                        "evidence.transition_digest",
                    ),
                    reveal_time=_integer(
                        raw["reveal_time"], "evidence.reveal_time"
                    ),
                    outcome_digest=_sha256_text(
                        raw["outcome_digest"], "evidence.outcome_digest"
                    ),
                )
            block_index, row_index = divmod(
                item.commitment_nonce,
                self.config.commitment_block_size,
            )
            if not np.array_equal(
                item.handles,
                self._handle_block(block_index)[row_index],
            ):
                raise ValueError(
                    "snapshot evidence handles do not match the owned schedule"
                )
            expected_commitment = _digest(
                {
                    "schema": COMMITMENT_SCHEMA,
                    "time": item.commitment_time,
                    "nonce": item.commitment_nonce,
                    "handles": item.handles,
                }
            )
            if item.commitment_digest != expected_commitment:
                raise ValueError("snapshot evidence commitment digest mismatch")
            expected_transition = _digest(
                {
                    "schema": TRANSITION_SCHEMA,
                    "time": item.commitment_time,
                    "commitment_digest": item.commitment_digest,
                    "observation": item.observation,
                    "process_bank": item.process_bank,
                }
            )
            if item.transition_digest != expected_transition:
                raise ValueError("snapshot evidence transition digest mismatch")
            if item.reveal_time <= item.commitment_time:
                raise ValueError(
                    "snapshot evidence reveal must follow its commitment"
                )
            expected_outcome = _digest(
                {
                    "schema": OUTCOME_SCHEMA,
                    "transition_digest": item.transition_digest,
                    "reveal_time": item.reveal_time,
                    "next_observation": item.next_observation,
                }
            )
            if item.outcome_digest != expected_outcome:
                raise ValueError("snapshot evidence outcome digest mismatch")
            evidence.append(item)
        if len(evidence) > self.config.evidence_capacity:
            raise ValueError("snapshot evidence exceeds configured capacity")
        evidence_nonces = [item.commitment_nonce for item in evidence]
        if any(
            later <= earlier
            for earlier, later in zip(evidence_nonces, evidence_nonces[1:])
        ):
            raise ValueError(
                "snapshot evidence commitment nonces must be strictly increasing"
            )

        pending_commitment = None
        if payload["pending_commitment"] is not None:
            pending_commitment = self._load_commitment(payload["pending_commitment"])
        pending_transition = None
        if payload["pending_transition"] is not None:
            raw = payload["pending_transition"]
            if not isinstance(raw, Mapping):
                raise ValueError("snapshot pending_transition must be a mapping")
            commitment = self._load_commitment(raw["commitment"])
            pending_transition = _PendingTransition(
                time=_integer(raw["time"], "pending_transition.time", minimum=0),
                observation=_readonly(
                    _array(
                        raw["observation"],
                        (self.config.observation_dim,),
                        "pending_transition.observation",
                    )
                ),
                process_bank=_readonly(
                    _array(
                        raw["process_bank"],
                        (self.config.source_count, self.config.process_dim),
                        "pending_transition.process_bank",
                    )
                ),
                commitment=commitment,
                transition_digest=_sha256_text(
                    raw["transition_digest"],
                    "pending_transition.transition_digest",
                ),
            )
            if pending_transition.time != commitment.time:
                raise ValueError(
                    "snapshot transition time must equal commitment time"
                )
            expected_transition = _digest(
                {
                    "schema": TRANSITION_SCHEMA,
                    "time": pending_transition.time,
                    "commitment_digest": commitment.digest,
                    "observation": pending_transition.observation,
                    "process_bank": pending_transition.process_bank,
                }
            )
            if pending_transition.transition_digest != expected_transition:
                raise ValueError("snapshot transition digest mismatch")
        if pending_commitment is not None and pending_transition is not None:
            raise ValueError("snapshot cannot contain two pending causal stages")

        candidate_signature = payload["candidate_signature"]
        if candidate_signature is not None:
            if (
                not isinstance(candidate_signature, (tuple, list))
                or len(candidate_signature) != 3
            ):
                raise ValueError("snapshot candidate_signature must have length three")
            candidate_signature = (
                _integer(candidate_signature[0], "candidate_signature.handle"),
                _integer(candidate_signature[1], "candidate_signature.source"),
                _integer(candidate_signature[2], "candidate_signature.rank", minimum=1),
            )
            if (
                candidate_signature[0] >= self.config.handle_count
                or candidate_signature[1] >= self.config.source_count
            ):
                raise ValueError("snapshot candidate_signature pair is out of bounds")
            if candidate_signature[2] > min(
                self.config.process_dim, self.config.observation_dim
            ):
                raise ValueError("snapshot candidate_signature rank is out of bounds")
        candidate_last_evidence_count = _optional_integer(
            payload["candidate_last_evidence_count"],
            "candidate_last_evidence_count",
        )
        miss_last_evidence_count = _optional_integer(
            payload["miss_last_evidence_count"],
            "miss_last_evidence_count",
        )
        last_receipt = None
        if payload["last_receipt"] is not None:
            raw_receipt = payload["last_receipt"]
            if not isinstance(raw_receipt, Mapping):
                raise ValueError("snapshot last_receipt must be a mapping")
            for boolean_name in (
                "fit_performed",
                "acquired",
                "revised",
                "revoked",
                "rank_changed",
                "candidate_renewed",
                "null_renewed",
                "updates_frozen",
            ):
                if not isinstance(raw_receipt[boolean_name], (bool, np.bool_)):
                    raise ValueError(
                        f"last_receipt.{boolean_name} must be boolean"
                    )
            last_receipt = CausalBoundaryUpdateReceipt(
                commitment_digest=_sha256_text(
                    raw_receipt["commitment_digest"],
                    "last_receipt.commitment_digest",
                ),
                transition_digest=_sha256_text(
                    raw_receipt["transition_digest"],
                    "last_receipt.transition_digest",
                ),
                outcome_digest=_sha256_text(
                    raw_receipt["outcome_digest"],
                    "last_receipt.outcome_digest",
                ),
                reveal_time=_integer(
                    raw_receipt["reveal_time"], "last_receipt.reveal_time"
                ),
                model_digest_before=_sha256_text(
                    raw_receipt["model_digest_before"],
                    "last_receipt.model_digest_before",
                ),
                model_digest_after=_sha256_text(
                    raw_receipt["model_digest_after"],
                    "last_receipt.model_digest_after",
                ),
                evidence_count=_integer(
                    raw_receipt["evidence_count"],
                    "last_receipt.evidence_count",
                ),
                fit_performed=bool(raw_receipt["fit_performed"]),
                acquired=bool(raw_receipt["acquired"]),
                revised=bool(raw_receipt["revised"]),
                revoked=bool(raw_receipt["revoked"]),
                rank_changed=bool(raw_receipt["rank_changed"]),
                structural_event=str(raw_receipt["structural_event"]),
                updates_frozen=bool(raw_receipt["updates_frozen"]),
                prequential_alignment=_finite_float(
                    raw_receipt["prequential_alignment"],
                    "last_receipt.prequential_alignment",
                ),
                confidence_before=_finite_float(
                    raw_receipt["confidence_before"],
                    "last_receipt.confidence_before",
                ),
                previous_handle_index=_optional_integer(
                    raw_receipt["previous_handle_index"],
                    "last_receipt.previous_handle_index",
                ),
                previous_source_index=_optional_integer(
                    raw_receipt["previous_source_index"],
                    "last_receipt.previous_source_index",
                ),
                previous_rank=_integer(
                    raw_receipt["previous_rank"], "last_receipt.previous_rank"
                ),
                fit_handle_index=_optional_integer(
                    raw_receipt["fit_handle_index"],
                    "last_receipt.fit_handle_index",
                ),
                fit_source_index=_optional_integer(
                    raw_receipt["fit_source_index"],
                    "last_receipt.fit_source_index",
                ),
                fit_rank=_integer(
                    raw_receipt["fit_rank"], "last_receipt.fit_rank"
                ),
                fit_confidence=_finite_float(
                    raw_receipt["fit_confidence"],
                    "last_receipt.fit_confidence",
                ),
                selected_handle_index=_optional_integer(
                    raw_receipt["selected_handle_index"],
                    "last_receipt.selected_handle_index",
                ),
                selected_source_index=_optional_integer(
                    raw_receipt["selected_source_index"],
                    "last_receipt.selected_source_index",
                ),
                rank=_integer(raw_receipt["rank"], "last_receipt.rank"),
                confidence=_finite_float(
                    raw_receipt["confidence"], "last_receipt.confidence"
                ),
                change_alarm=_finite_float(
                    raw_receipt["change_alarm"], "last_receipt.change_alarm"
                ),
                candidate_handle_index=_optional_integer(
                    raw_receipt["candidate_handle_index"],
                    "last_receipt.candidate_handle_index",
                ),
                candidate_source_index=_optional_integer(
                    raw_receipt["candidate_source_index"],
                    "last_receipt.candidate_source_index",
                ),
                candidate_rank=_integer(
                    raw_receipt["candidate_rank"], "last_receipt.candidate_rank"
                ),
                candidate_streak=_integer(
                    raw_receipt["candidate_streak"],
                    "last_receipt.candidate_streak",
                ),
                candidate_last_evidence_count=_optional_integer(
                    raw_receipt["candidate_last_evidence_count"],
                    "last_receipt.candidate_last_evidence_count",
                ),
                candidate_renewed=bool(raw_receipt["candidate_renewed"]),
                null_streak=_integer(
                    raw_receipt["null_streak"],
                    "last_receipt.null_streak",
                ),
                null_last_evidence_count=_optional_integer(
                    raw_receipt["null_last_evidence_count"],
                    "last_receipt.null_last_evidence_count",
                ),
                null_renewed=bool(raw_receipt["null_renewed"]),
                epoch=_integer(raw_receipt["epoch"], "last_receipt.epoch"),
            )
            allowed_events = {
                "none",
                "acquisition_candidate",
                "acquisition",
                "parameter_refresh",
                "null_candidate",
                "null_fit",
                "revocation",
                "structural_candidate",
                "rank_revision",
                "pair_revision",
            }
            if last_receipt.structural_event not in allowed_events:
                raise ValueError("last_receipt.structural_event is invalid")
            if last_receipt.acquired != (
                last_receipt.structural_event == "acquisition"
            ):
                raise ValueError("last_receipt acquisition flag is inconsistent")
            if last_receipt.revised != (
                last_receipt.structural_event in {"rank_revision", "pair_revision"}
            ):
                raise ValueError("last_receipt revision flag is inconsistent")
            if last_receipt.revoked != (
                last_receipt.structural_event == "revocation"
            ):
                raise ValueError("last_receipt revocation flag is inconsistent")
            if last_receipt.rank_changed != (
                last_receipt.structural_event == "rank_revision"
            ):
                raise ValueError("last_receipt rank-change flag is inconsistent")
            if last_receipt.fit_performed == (
                last_receipt.structural_event == "none"
            ):
                raise ValueError("last_receipt structural event violates fit status")

        completed_count = _integer(
            payload["completed_count"], "completed_count", minimum=0
        )
        fit_count = _integer(payload["fit_count"], "fit_count", minimum=0)
        commit_count = _integer(payload["commit_count"], "commit_count")
        candidate_streak = _integer(
            payload["candidate_streak"], "candidate_streak"
        )
        miss_streak = _integer(payload["miss_streak"], "miss_streak")
        if state.evidence_count != completed_count or state.fit_count != fit_count:
            raise ValueError("snapshot state counters do not match agent counters")
        if completed_count > commit_count:
            raise ValueError("snapshot completed_count exceeds commit_count")
        if fit_count > completed_count:
            raise ValueError("snapshot fit_count exceeds completed_count")
        expected_evidence_count = min(
            completed_count, self.config.evidence_capacity
        )
        if len(evidence) != expected_evidence_count:
            raise ValueError(
                "snapshot retained evidence count does not match completed_count"
            )
        if any(nonce >= commit_count for nonce in evidence_nonces):
            raise ValueError("snapshot evidence nonce is not below commit_count")
        pending = pending_commitment
        if pending_transition is not None:
            pending = pending_transition.commitment
        if pending is not None:
            if commit_count == 0 or pending.nonce != commit_count - 1:
                raise ValueError(
                    "snapshot pending commitment must own the latest nonce"
                )
            if evidence_nonces and evidence_nonces[-1] >= pending.nonce:
                raise ValueError(
                    "snapshot pending nonce must follow retained evidence"
                )
        if candidate_signature is None:
            if candidate_streak != 0 or candidate_last_evidence_count is not None:
                raise ValueError(
                    "snapshot candidate state requires a candidate_signature"
                )
        else:
            if not 1 <= candidate_streak < self.config.revision_confirmations:
                raise ValueError(
                    "snapshot candidate_streak is outside the unconfirmed range"
                )
            if (
                candidate_last_evidence_count is None
                or candidate_last_evidence_count > completed_count
            ):
                raise ValueError(
                    "snapshot candidate renewal counter is missing or in the future"
                )
        if candidate_signature is not None:
            current_signature = (
                state.selected_handle_index,
                state.selected_source_index,
                state.rank,
            )
            if state.active and candidate_signature == current_signature:
                raise ValueError(
                    "snapshot candidate_signature duplicates the accepted structure"
                )
            if miss_streak != 0:
                raise ValueError(
                    "snapshot structural candidate cannot coexist with null misses"
                )
        if state.active and miss_streak >= self.config.revocation_confirmations:
            raise ValueError(
                "snapshot active state exceeds the revocation miss threshold"
            )
        if miss_streak == 0:
            if miss_last_evidence_count is not None:
                raise ValueError(
                    "snapshot null renewal counter requires a null streak"
                )
        elif (
            not state.active
            or miss_last_evidence_count is None
            or miss_last_evidence_count > completed_count
        ):
            raise ValueError("snapshot null candidate state is inconsistent")
        updates_frozen = payload["updates_frozen"]
        if not isinstance(updates_frozen, (bool, np.bool_)):
            raise ValueError("snapshot updates_frozen must be boolean")
        interrupted_transitions = _integer(
            payload["interrupted_transitions"],
            "interrupted_transitions",
        )
        if last_receipt is not None:
            if not evidence:
                raise ValueError("snapshot last_receipt has no retained evidence")
            last_evidence = evidence[-1]
            if (
                last_receipt.commitment_digest
                != last_evidence.commitment_digest
                or last_receipt.transition_digest
                != last_evidence.transition_digest
                or last_receipt.outcome_digest != last_evidence.outcome_digest
                or last_receipt.reveal_time != last_evidence.reveal_time
            ):
                raise ValueError(
                    "snapshot last_receipt does not match the latest evidence"
                )
            if last_receipt.evidence_count != completed_count:
                raise ValueError(
                    "snapshot last_receipt evidence counter does not match"
                )
            scheduled_fit = bool(
                completed_count >= self.config.minimum_samples
                and (
                    completed_count - self.config.minimum_samples
                )
                % self.config.fit_interval
                == 0
            )
            expected_fit = bool(
                scheduled_fit and not last_receipt.updates_frozen
            )
            if last_receipt.fit_performed != expected_fit:
                raise ValueError(
                    "snapshot last_receipt fit flag violates the update schedule"
                )
            if (
                sum(
                    int(flag)
                    for flag in (
                        last_receipt.acquired,
                        last_receipt.revised,
                        last_receipt.revoked,
                    )
                )
                > 1
            ) or (
                (
                    last_receipt.acquired
                    or last_receipt.revised
                    or last_receipt.revoked
                )
                and not last_receipt.fit_performed
            ):
                raise ValueError(
                    "snapshot last_receipt revision flags are inconsistent"
                )
            if not -1.0 <= last_receipt.prequential_alignment <= 1.0:
                raise ValueError(
                    "snapshot last_receipt alignment is out of bounds"
                )
            if not 0.0 <= last_receipt.confidence_before <= 1.0:
                raise ValueError(
                    "snapshot last_receipt prior confidence is out of bounds"
                )
            previous_has_handle = last_receipt.previous_handle_index is not None
            previous_has_source = last_receipt.previous_source_index is not None
            if previous_has_handle != previous_has_source:
                raise ValueError(
                    "snapshot last_receipt previous pair is incomplete"
                )
            if previous_has_handle != (last_receipt.previous_rank > 0):
                raise ValueError(
                    "snapshot last_receipt previous rank is inconsistent"
                )
            fit_has_handle = last_receipt.fit_handle_index is not None
            fit_has_source = last_receipt.fit_source_index is not None
            if fit_has_handle != fit_has_source:
                raise ValueError("snapshot last_receipt fit pair is incomplete")
            if fit_has_handle != (last_receipt.fit_rank > 0):
                raise ValueError("snapshot last_receipt fit rank is inconsistent")
            if not 0.0 <= last_receipt.fit_confidence <= 1.0:
                raise ValueError(
                    "snapshot last_receipt fit confidence is out of bounds"
                )
            if not last_receipt.fit_performed and (
                fit_has_handle
                or last_receipt.fit_rank != 0
                or last_receipt.fit_confidence != 0.0
            ):
                raise ValueError(
                    "snapshot last_receipt has a fit proposal without a fit"
                )
            if last_receipt.fit_performed and fit_has_handle:
                if last_receipt.fit_confidence <= 0.0:
                    raise ValueError(
                        "snapshot last_receipt active fit confidence must be positive"
                    )
            receipt_candidate = None
            if (
                last_receipt.candidate_handle_index is not None
                or last_receipt.candidate_source_index is not None
                or last_receipt.candidate_rank != 0
            ):
                if (
                    last_receipt.candidate_handle_index is None
                    or last_receipt.candidate_source_index is None
                    or last_receipt.candidate_rank <= 0
                ):
                    raise ValueError(
                        "snapshot last_receipt candidate signature is incomplete"
                    )
                receipt_candidate = (
                    last_receipt.candidate_handle_index,
                    last_receipt.candidate_source_index,
                    last_receipt.candidate_rank,
                )
            if (
                receipt_candidate != candidate_signature
                or last_receipt.candidate_streak != candidate_streak
                or last_receipt.candidate_last_evidence_count
                != candidate_last_evidence_count
            ):
                raise ValueError(
                    "snapshot last_receipt candidate does not match pending state"
                )
            if (
                last_receipt.null_streak != miss_streak
                or last_receipt.null_last_evidence_count
                != miss_last_evidence_count
            ):
                raise ValueError(
                    "snapshot last_receipt null candidate does not match pending state"
                )
            if last_receipt.candidate_renewed and last_receipt.null_renewed:
                raise ValueError(
                    "snapshot last_receipt cannot renew two structural decisions"
                )
            if (
                last_receipt.candidate_renewed
                or last_receipt.null_renewed
            ) and not last_receipt.fit_performed:
                raise ValueError(
                    "snapshot last_receipt renewal requires a performed fit"
                )
            if last_receipt.candidate_renewed and last_receipt.fit_rank <= 0:
                raise ValueError(
                    "snapshot last_receipt candidate renewal requires a non-null fit"
                )
            if last_receipt.null_renewed and last_receipt.fit_rank != 0:
                raise ValueError(
                    "snapshot last_receipt null renewal requires a null fit"
                )
            if (
                last_receipt.structural_event
                in {"acquisition", "rank_revision", "pair_revision"}
                and not last_receipt.candidate_renewed
            ):
                raise ValueError(
                    "snapshot committed structural change lacks renewed evidence"
                )
            if (
                last_receipt.structural_event == "revocation"
                and not last_receipt.null_renewed
            ):
                raise ValueError(
                    "snapshot revocation lacks renewed null evidence"
                )
            receipt_state = (
                last_receipt.selected_handle_index,
                last_receipt.selected_source_index,
                last_receipt.rank,
                last_receipt.confidence,
                last_receipt.change_alarm,
                last_receipt.epoch,
                last_receipt.model_digest_after,
            )
            current_state = (
                state.selected_handle_index,
                state.selected_source_index,
                state.rank,
                state.confidence,
                state.change_alarm,
                state.epoch,
                state.model_digest,
            )
            if receipt_state != current_state:
                raise ValueError(
                    "snapshot last_receipt does not describe the current state"
                )
        self._state = self._copy_state(state)
        self._evidence = evidence
        self._pending_commitment = pending_commitment
        self._pending_transition = pending_transition
        self._commit_count = commit_count
        self._completed_count = completed_count
        self._fit_count = fit_count
        self._updates_frozen = bool(updates_frozen)
        self._candidate_signature = candidate_signature
        self._candidate_streak = candidate_streak
        self._candidate_last_evidence_count = candidate_last_evidence_count
        self._miss_streak = miss_streak
        self._miss_last_evidence_count = miss_last_evidence_count
        self._last_receipt = last_receipt
        self._interrupted_transitions = max(
            interrupted_transitions,
            self._interrupted_transitions,
        ) + int(replacing_pending)


class DirectCausalAccessReadout:
    """Label-free transport for a workspace-selected causal candidate.

    This object deliberately performs no classification and accepts no target
    labels.  Its presence in the agent preserves the same snapshot/reset API
    as the learned access readouts while making the absence of supervised
    access updates auditable.  The agent itself copies the currently selected
    private candidate into the public-pair field only after the causal
    proposal wins workspace access.  A downstream consequence-grounded gate
    must still decide whether that candidate is authorized for action.
    """

    def __init__(
        self,
        feature_dim: int,
        handle_count: int,
        source_count: int,
    ) -> None:
        self.feature_dim = _integer(feature_dim, "feature_dim", minimum=1)
        self.handle_count = _integer(handle_count, "handle_count", minimum=1)
        self.source_count = _integer(source_count, "source_count", minimum=1)
        self._update_count = 0

    @property
    def update_count(self) -> int:
        return 0

    def predict(self, features: ArrayLike) -> CausalAccessPrediction:
        _array(features, (self.feature_dim,), "access_features")
        return CausalAccessPrediction(
            pair=None,
            class_index=None,
            confidence=0.0,
            margin=0.0,
            distance=float("inf"),
            update_count=0,
        )

    def update(
        self,
        features: ArrayLike,
        attempted_pair: tuple[int, int] | None,
    ) -> None:
        _array(features, (self.feature_dim,), "access_features")
        del attempted_pair
        raise RuntimeError(
            "direct causal access is label-free and cannot receive targets"
        )

    def reset(self) -> None:
        self._update_count = 0

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": DIRECT_ACCESS_SNAPSHOT_SCHEMA,
            "feature_dim": self.feature_dim,
            "handle_count": self.handle_count,
            "source_count": self.source_count,
            "strategy": "direct_workspace_candidate",
            "uses_class_labels": False,
            "update_count": 0,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)

    def load_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        if not isinstance(snapshot, Mapping):
            raise TypeError("direct causal access snapshot must be a mapping")
        payload = copy.deepcopy(dict(snapshot))
        observed_digest = payload.pop("digest", None)
        if not isinstance(observed_digest, str) or observed_digest != _digest(payload):
            raise ValueError("direct causal access snapshot digest mismatch")
        expected = {
            "schema": DIRECT_ACCESS_SNAPSHOT_SCHEMA,
            "feature_dim": self.feature_dim,
            "handle_count": self.handle_count,
            "source_count": self.source_count,
            "strategy": "direct_workspace_candidate",
            "uses_class_labels": False,
            "update_count": 0,
        }
        if payload != expected:
            raise ValueError("direct causal access snapshot configuration mismatch")
        self._update_count = 0

    def __deepcopy__(
        self, memo: dict[int, Any]
    ) -> "DirectCausalAccessReadout":
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        clone = type(self)(
            self.feature_dim,
            self.handle_count,
            self.source_count,
        )
        memo[id(self)] = clone
        return clone


class OnlineCausalAccessReadout:
    """Bounded prequential access readout for an attempted boundary broadcast.

    Inference consumes only post-workspace and post-self-model features.  The
    readout then receives the boundary module's own attempted pair (or null)
    as a self-supervised target.  Evaluator routes and source-family metadata
    are neither accepted nor retained.
    """

    def __init__(
        self,
        feature_dim: int,
        handle_count: int,
        source_count: int,
        *,
        learning_rate: float = 0.25,
        minimum_class_updates: int = 2,
        maximum_distance: float = 0.55,
        minimum_margin: float = 1e-4,
    ) -> None:
        self.feature_dim = _integer(feature_dim, "feature_dim", minimum=1)
        self.handle_count = _integer(handle_count, "handle_count", minimum=1)
        self.source_count = _integer(source_count, "source_count", minimum=1)
        self.learning_rate = _finite_float(learning_rate, "learning_rate")
        self.minimum_class_updates = _integer(
            minimum_class_updates, "minimum_class_updates", minimum=1
        )
        self.maximum_distance = _finite_float(
            maximum_distance, "maximum_distance"
        )
        self.minimum_margin = _finite_float(minimum_margin, "minimum_margin")
        if not 0.0 < self.learning_rate <= 1.0:
            raise ValueError("learning_rate must lie in (0, 1]")
        if self.maximum_distance <= 0.0:
            raise ValueError("maximum_distance must be positive")
        if self.minimum_margin < 0.0:
            raise ValueError("minimum_margin must be nonnegative")
        self.class_count = self.handle_count * self.source_count + 1
        self.null_class = self.class_count - 1
        self._centroids = np.zeros(
            (self.class_count, self.feature_dim), dtype=np.float64
        )
        self._class_updates = np.zeros(self.class_count, dtype=np.int64)
        self._update_count = 0

    @property
    def update_count(self) -> int:
        return self._update_count

    def _features(self, value: ArrayLike) -> FloatArray:
        features = _array(value, (self.feature_dim,), "access_features")
        return np.asarray(np.tanh(features), dtype=np.float64)

    def _pair_class(self, pair: tuple[int, int] | None) -> int:
        if pair is None:
            return self.null_class
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("attempted_pair must be a two-integer tuple or None")
        handle = _integer(pair[0], "attempted_pair.handle")
        source = _integer(pair[1], "attempted_pair.source")
        if handle >= self.handle_count or source >= self.source_count:
            raise ValueError("attempted_pair is out of bounds")
        return handle * self.source_count + source

    def _class_pair(self, class_index: int) -> tuple[int, int] | None:
        if class_index == self.null_class:
            return None
        return divmod(class_index, self.source_count)

    def predict(self, features: ArrayLike) -> CausalAccessPrediction:
        """Predict before the current attempted broadcast is used as a target."""

        bounded = self._features(features)
        eligible = self._class_updates >= self.minimum_class_updates
        if not np.any(eligible):
            return CausalAccessPrediction(
                pair=None,
                class_index=None,
                confidence=0.0,
                margin=0.0,
                distance=float("inf"),
                update_count=self._update_count,
            )
        distances = np.full(self.class_count, np.inf, dtype=np.float64)
        differences = self._centroids[eligible] - bounded[None, :]
        distances[eligible] = np.mean(differences * differences, axis=1)
        order = np.argsort(distances, kind="stable")
        best = int(order[0])
        best_distance = float(distances[best])
        finite = order[np.isfinite(distances[order])]
        if len(finite) > 1:
            second_distance = float(distances[int(finite[1])])
            margin = second_distance - best_distance
        else:
            margin = 1.0
        confidence = float(np.clip(np.exp(-4.0 * best_distance), 0.0, 1.0))
        usable = bool(
            best_distance <= self.maximum_distance
            and margin >= self.minimum_margin
        )
        pair = self._class_pair(best) if usable else None
        return CausalAccessPrediction(
            pair=pair,
            class_index=best if usable else None,
            confidence=confidence if usable else 0.0,
            margin=float(margin if np.isfinite(margin) else 0.0),
            distance=best_distance,
            update_count=self._update_count,
        )

    def update(
        self,
        features: ArrayLike,
        attempted_pair: tuple[int, int] | None,
    ) -> None:
        """Learn only after a prequential access prediction has been made."""

        bounded = self._features(features)
        class_index = self._pair_class(attempted_pair)
        count = int(self._class_updates[class_index])
        rate = 1.0 if count == 0 else self.learning_rate
        centroid = (
            (1.0 - rate) * self._centroids[class_index]
            + rate * bounded
        )
        self._centroids[class_index] = np.clip(centroid, -1.0, 1.0)
        self._class_updates[class_index] += 1
        self._update_count += 1

    def reset(self) -> None:
        self._centroids.fill(0.0)
        self._class_updates.fill(0)
        self._update_count = 0

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": ACCESS_SNAPSHOT_SCHEMA,
            "feature_dim": self.feature_dim,
            "handle_count": self.handle_count,
            "source_count": self.source_count,
            "learning_rate": self.learning_rate,
            "minimum_class_updates": self.minimum_class_updates,
            "maximum_distance": self.maximum_distance,
            "minimum_margin": self.minimum_margin,
            "centroids": self._centroids.copy(),
            "class_updates": self._class_updates.copy(),
            "update_count": self._update_count,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)

    def load_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        if not isinstance(snapshot, Mapping):
            raise TypeError("causal access snapshot must be a mapping")
        payload = copy.deepcopy(dict(snapshot))
        observed_digest = payload.pop("digest", None)
        if not isinstance(observed_digest, str) or observed_digest != _digest(payload):
            raise ValueError("causal access snapshot digest mismatch")
        expected_configuration = {
            "schema": ACCESS_SNAPSHOT_SCHEMA,
            "feature_dim": self.feature_dim,
            "handle_count": self.handle_count,
            "source_count": self.source_count,
            "learning_rate": self.learning_rate,
            "minimum_class_updates": self.minimum_class_updates,
            "maximum_distance": self.maximum_distance,
            "minimum_margin": self.minimum_margin,
        }
        for name, expected in expected_configuration.items():
            if payload.get(name) != expected:
                raise ValueError(
                    f"causal access snapshot {name} does not match"
                )
        centroids = _array(
            payload["centroids"],
            (self.class_count, self.feature_dim),
            "access.centroids",
        )
        if np.max(np.abs(centroids), initial=0.0) > 1.0:
            raise ValueError("causal access centroids are out of bounds")
        raw_updates = np.asarray(payload["class_updates"])
        if raw_updates.shape != (self.class_count,) or raw_updates.dtype.kind not in "iu":
            raise ValueError("causal access class_updates must be integer-valued")
        if np.any(raw_updates < 0):
            raise ValueError("causal access class_updates must be nonnegative")
        class_updates = np.asarray(raw_updates, dtype=np.int64)
        update_count = _integer(payload["update_count"], "access.update_count")
        if int(np.sum(class_updates)) != update_count:
            raise ValueError("causal access update counter does not match")
        self._centroids = np.asarray(centroids, dtype=np.float64).copy()
        self._class_updates = class_updates.copy()
        self._update_count = update_count

    def __deepcopy__(self, memo: dict[int, Any]) -> "OnlineCausalAccessReadout":
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        clone = type(self)(
            self.feature_dim,
            self.handle_count,
            self.source_count,
            learning_rate=self.learning_rate,
            minimum_class_updates=self.minimum_class_updates,
            maximum_distance=self.maximum_distance,
            minimum_margin=self.minimum_margin,
        )
        memo[id(self)] = clone
        clone.load_snapshot(self.snapshot())
        return clone


class OnlineCausalAccessMemoryReadout:
    """Bounded prequential nearest-memory decoder for attempted broadcasts.

    The historical centroid readout compresses every class into one moving
    prototype.  That representation is brittle when the same attempted pair
    reaches the workspace through several recurrent contexts.  This readout
    retains a bounded set of class-conditional feature exemplars and predicts
    from the mean distance to the nearest ``neighbors`` exemplars.

    ``strategy="fifo"`` keeps the most recent examples.  ``strategy="prototype"``
    fills a bounded prototype set and then moves the nearest prototype toward
    each new example.  Prediction always precedes the current self-supervised
    target update, preserving the same prequential information boundary as the
    original decoder.
    """

    def __init__(
        self,
        feature_dim: int,
        handle_count: int,
        source_count: int,
        *,
        memory_capacity: int = 64,
        neighbors: int = 1,
        strategy: str = "fifo",
        prototype_learning_rate: float = 0.25,
        minimum_class_updates: int = 2,
        maximum_distance: float = 0.55,
        minimum_margin: float = 1e-4,
    ) -> None:
        self.feature_dim = _integer(feature_dim, "feature_dim", minimum=1)
        self.handle_count = _integer(handle_count, "handle_count", minimum=1)
        self.source_count = _integer(source_count, "source_count", minimum=1)
        self.memory_capacity = _integer(
            memory_capacity, "memory_capacity", minimum=1
        )
        self.neighbors = _integer(neighbors, "neighbors", minimum=1)
        if self.neighbors > self.memory_capacity:
            raise ValueError("neighbors cannot exceed memory_capacity")
        if strategy not in {"fifo", "prototype"}:
            raise ValueError("strategy must be 'fifo' or 'prototype'")
        self.strategy = str(strategy)
        self.prototype_learning_rate = _finite_float(
            prototype_learning_rate, "prototype_learning_rate"
        )
        if not 0.0 < self.prototype_learning_rate <= 1.0:
            raise ValueError("prototype_learning_rate must lie in (0, 1]")
        self.minimum_class_updates = _integer(
            minimum_class_updates, "minimum_class_updates", minimum=1
        )
        self.maximum_distance = _finite_float(
            maximum_distance, "maximum_distance"
        )
        self.minimum_margin = _finite_float(minimum_margin, "minimum_margin")
        if self.maximum_distance <= 0.0:
            raise ValueError("maximum_distance must be positive")
        if self.minimum_margin < 0.0:
            raise ValueError("minimum_margin must be nonnegative")
        self.class_count = self.handle_count * self.source_count + 1
        self.null_class = self.class_count - 1
        self._memories: list[list[FloatArray]] = [
            [] for _ in range(self.class_count)
        ]
        self._class_updates = np.zeros(self.class_count, dtype=np.int64)
        self._update_count = 0

    @property
    def update_count(self) -> int:
        return self._update_count

    def _features(self, value: ArrayLike) -> FloatArray:
        features = _array(value, (self.feature_dim,), "access_features")
        return np.asarray(np.tanh(features), dtype=np.float64)

    def _pair_class(self, pair: tuple[int, int] | None) -> int:
        if pair is None:
            return self.null_class
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("attempted_pair must be a two-integer tuple or None")
        handle = _integer(pair[0], "attempted_pair.handle")
        source = _integer(pair[1], "attempted_pair.source")
        if handle >= self.handle_count or source >= self.source_count:
            raise ValueError("attempted_pair is out of bounds")
        return handle * self.source_count + source

    def _class_pair(self, class_index: int) -> tuple[int, int] | None:
        if class_index == self.null_class:
            return None
        return divmod(class_index, self.source_count)

    def predict(self, features: ArrayLike) -> CausalAccessPrediction:
        """Predict before the current attempted broadcast becomes evidence."""

        bounded = self._features(features)
        distances = np.full(self.class_count, np.inf, dtype=np.float64)
        for class_index, memory in enumerate(self._memories):
            if (
                self._class_updates[class_index]
                < self.minimum_class_updates
                or not memory
            ):
                continue
            exemplars = np.stack(memory)
            sample_distances = np.mean(
                (exemplars - bounded[None, :]) ** 2, axis=1
            )
            count = min(self.neighbors, len(sample_distances))
            nearest = np.partition(sample_distances, count - 1)[:count]
            distances[class_index] = float(np.mean(nearest))
        if not np.any(np.isfinite(distances)):
            return CausalAccessPrediction(
                pair=None,
                class_index=None,
                confidence=0.0,
                margin=0.0,
                distance=float("inf"),
                update_count=self._update_count,
            )
        order = np.argsort(distances, kind="stable")
        best = int(order[0])
        best_distance = float(distances[best])
        finite = order[np.isfinite(distances[order])]
        margin = (
            float(distances[int(finite[1])] - best_distance)
            if len(finite) > 1
            else 1.0
        )
        confidence = float(np.clip(np.exp(-4.0 * best_distance), 0.0, 1.0))
        usable = bool(
            best_distance <= self.maximum_distance
            and margin >= self.minimum_margin
        )
        return CausalAccessPrediction(
            pair=self._class_pair(best) if usable else None,
            class_index=best if usable else None,
            confidence=confidence if usable else 0.0,
            margin=float(margin if np.isfinite(margin) else 0.0),
            distance=best_distance,
            update_count=self._update_count,
        )

    def update(
        self,
        features: ArrayLike,
        attempted_pair: tuple[int, int] | None,
    ) -> None:
        """Add the current self-supervised target after prediction."""

        bounded = self._features(features)
        class_index = self._pair_class(attempted_pair)
        memory = self._memories[class_index]
        if len(memory) < self.memory_capacity:
            memory.append(bounded.copy())
        elif self.strategy == "fifo":
            del memory[0]
            memory.append(bounded.copy())
        else:
            exemplars = np.stack(memory)
            distances = np.mean(
                (exemplars - bounded[None, :]) ** 2, axis=1
            )
            nearest = int(np.argmin(distances))
            rate = self.prototype_learning_rate
            memory[nearest] = np.clip(
                (1.0 - rate) * memory[nearest] + rate * bounded,
                -1.0,
                1.0,
            )
        self._class_updates[class_index] += 1
        self._update_count += 1

    def reset(self) -> None:
        self._memories = [[] for _ in range(self.class_count)]
        self._class_updates.fill(0)
        self._update_count = 0

    def snapshot(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": ACCESS_MEMORY_SNAPSHOT_SCHEMA,
            "feature_dim": self.feature_dim,
            "handle_count": self.handle_count,
            "source_count": self.source_count,
            "memory_capacity": self.memory_capacity,
            "neighbors": self.neighbors,
            "strategy": self.strategy,
            "prototype_learning_rate": self.prototype_learning_rate,
            "minimum_class_updates": self.minimum_class_updates,
            "maximum_distance": self.maximum_distance,
            "minimum_margin": self.minimum_margin,
            "memories": tuple(
                np.stack(memory)
                if memory
                else np.zeros((0, self.feature_dim), dtype=np.float64)
                for memory in self._memories
            ),
            "class_updates": self._class_updates.copy(),
            "update_count": self._update_count,
        }
        payload["digest"] = _digest(payload)
        return copy.deepcopy(payload)

    def load_snapshot(self, snapshot: Mapping[str, Any]) -> None:
        if not isinstance(snapshot, Mapping):
            raise TypeError("causal access memory snapshot must be a mapping")
        payload = copy.deepcopy(dict(snapshot))
        observed_digest = payload.pop("digest", None)
        if not isinstance(observed_digest, str) or observed_digest != _digest(payload):
            raise ValueError("causal access memory snapshot digest mismatch")
        expected = {
            "schema": ACCESS_MEMORY_SNAPSHOT_SCHEMA,
            "feature_dim": self.feature_dim,
            "handle_count": self.handle_count,
            "source_count": self.source_count,
            "memory_capacity": self.memory_capacity,
            "neighbors": self.neighbors,
            "strategy": self.strategy,
            "prototype_learning_rate": self.prototype_learning_rate,
            "minimum_class_updates": self.minimum_class_updates,
            "maximum_distance": self.maximum_distance,
            "minimum_margin": self.minimum_margin,
        }
        for name, value in expected.items():
            if payload.get(name) != value:
                raise ValueError(
                    f"causal access memory snapshot {name} does not match"
                )
        raw_memories = payload.get("memories")
        if not isinstance(raw_memories, (tuple, list)) or len(raw_memories) != self.class_count:
            raise ValueError("causal access memories have invalid class count")
        memories: list[list[FloatArray]] = []
        for class_index, raw_memory in enumerate(raw_memories):
            array = np.asarray(raw_memory, dtype=np.float64)
            if (
                array.ndim != 2
                or array.shape[1:] != (self.feature_dim,)
                or len(array) > self.memory_capacity
                or not np.all(np.isfinite(array))
                or np.max(np.abs(array), initial=0.0) > 1.0
            ):
                raise ValueError(
                    f"causal access memory class {class_index} is invalid"
                )
            memories.append([row.copy() for row in array])
        raw_updates = np.asarray(payload.get("class_updates"))
        if raw_updates.shape != (self.class_count,) or raw_updates.dtype.kind not in "iu":
            raise ValueError("causal access class_updates must be integer-valued")
        if np.any(raw_updates < 0):
            raise ValueError("causal access class_updates must be nonnegative")
        updates = np.asarray(raw_updates, dtype=np.int64)
        update_count = _integer(payload.get("update_count"), "access.update_count")
        if int(np.sum(updates)) != update_count:
            raise ValueError("causal access update counter does not match")
        for class_index, memory in enumerate(memories):
            expected_size = min(int(updates[class_index]), self.memory_capacity)
            if len(memory) != expected_size:
                raise ValueError(
                    "causal access memory size does not match class updates"
                )
        self._memories = memories
        self._class_updates = updates.copy()
        self._update_count = update_count

    def __deepcopy__(
        self, memo: dict[int, Any]
    ) -> "OnlineCausalAccessMemoryReadout":
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        clone = type(self)(
            self.feature_dim,
            self.handle_count,
            self.source_count,
            memory_capacity=self.memory_capacity,
            neighbors=self.neighbors,
            strategy=self.strategy,
            prototype_learning_rate=self.prototype_learning_rate,
            minimum_class_updates=self.minimum_class_updates,
            maximum_distance=self.maximum_distance,
            minimum_margin=self.minimum_margin,
        )
        memo[id(self)] = clone
        clone.load_snapshot(self.snapshot())
        return clone


__all__ = [
    "BoundCausalTransition",
    "CausalAccessPrediction",
    "CausalBoundaryConfig",
    "CausalBoundaryState",
    "CausalBoundaryUpdateReceipt",
    "CausalHandleCommitment",
    "DirectCausalAccessReadout",
    "OnlineCausalAccessMemoryReadout",
    "OnlineCausalAccessReadout",
    "OnlineCausalSelfBoundary",
]

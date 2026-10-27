"""RRCT v0.28 discovery of intervention provenance.

The estimator in this section is deliberately independent of the synthetic
world used by the development experiment.  It receives a mixed sensory
transition, an unlabeled bank of candidate internal processes, and a bank of
source-independent controllability handles.  It is not given the process or
handle that generated the effective intervention.

Provenance is operationalized as a replicated handle-by-process interaction:
after current sensory state, every raw candidate process, and every raw handle
have been accounted for, an effective pair must retain a reproducible effect
on the next sensory state.  Significance is familywise across every candidate
pair and singular mode.  Hidden source identities, interface projectors, and
rank are evaluation-only.

This is a bounded functional causal-identification mechanism.  It is not a
test of phenomenal consciousness, subjective awareness, sentience, valence,
or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import _agent_from_snapshots
from .discovered_agent_interface_experiment import _internal_interface
from .discovered_self_boundary_experiment import _native_observation, _orthogonal_mixing
from .instrumental_agency_experiment import _other_direction, _remap_matrix
from .sensorimotor_closure_experiment import _train_bundle


V028_INTERNAL_DIM = 8
V028_SENSOR_DIM = 12
V028_REGRESSION_RIDGE = 0.50
V028_NULL_PERMUTATIONS = 128
V028_HALF_NULL_PERMUTATIONS = 96
V028_NULL_QUANTILE = 0.99
V028_DEVELOPMENT_SEEDS = (5401, 5407, 5413, 5419)
V028_PILOT_SEEDS = (5381, 5387, 5393, 5399)
V028_SOURCE_KINDS = (
    "true_private",
    "delayed_echo",
    "policy_correlated",
    "independent",
    "exogenous_causal",
    "other_disturbance",
)
V028_GATEABLE_SOURCE_KINDS = V028_SOURCE_KINDS[:4]
V028_SOURCE_COUNT = len(V028_SOURCE_KINDS)
V028_HANDLE_COUNT = len(V028_GATEABLE_SOURCE_KINDS)
V028_CALIBRATION_EPISODES = 16
V028_CALIBRATION_STEPS = 60
V028_EVALUATION_EPISODES = 12
V028_EVALUATION_STEPS = 30
V028_SOURCE_AMPLITUDE = 0.95
V028_BASE_ACTION_SCALE = 0.24
V028_POLICY_SOURCE_NOISE = 0.32
V028_PRIVATE_COUPLING = 2.00
V028_EXOGENOUS_COUPLING = 2.40
V028_OTHER_SOURCE_COUPLING = 0.56
V028_TAKEOVER_AMPLITUDE = 0.50
V028_BOOTSTRAP_SEED = 20_261_028
V028_BOOTSTRAP_RESAMPLES = 4_000


def _validate_discovery_arrays(
    sensor: np.ndarray,
    process_bank: np.ndarray,
    handles: np.ndarray,
    next_sensor: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(sensor, dtype=np.float64)
    bank = np.asarray(process_bank, dtype=np.float64)
    gates = np.asarray(handles, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    if y.ndim != 2 or y.shape[1] != V028_SENSOR_DIM:
        raise ValueError("sensor must have shape (samples, 12)")
    if bank.ndim != 3 or bank.shape[0] != len(y) or bank.shape[2] != V028_INTERNAL_DIM:
        raise ValueError("process_bank must have shape (samples, sources, 8)")
    if bank.shape[1] < 1:
        raise ValueError("process_bank must contain at least one source")
    if gates.ndim != 2 or gates.shape[0] != len(y) or gates.shape[1] < 1:
        raise ValueError("handles must have shape (samples, handles)")
    if nxt.shape != y.shape:
        raise ValueError("next_sensor must have the same shape as sensor")
    if len(y) < 8:
        raise ValueError("at least eight samples are required")
    if not all(np.all(np.isfinite(value)) for value in (y, bank, gates, nxt)):
        raise ValueError("discovery arrays must contain only finite values")
    return y, bank, gates, nxt


def _ridge_residuals(design: np.ndarray, targets: np.ndarray) -> np.ndarray:
    x = np.asarray(design, dtype=np.float64)
    t = np.asarray(targets, dtype=np.float64)
    penalty = V028_REGRESSION_RIDGE * np.eye(x.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.05
    coefficients = np.linalg.solve(x.T @ x + penalty, x.T @ t)
    return t - x @ coefficients


def _residualized_problem(
    sensor: np.ndarray,
    process_bank: np.ndarray,
    handles: np.ndarray,
    next_sensor: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    sample_count, source_count, _ = process_bank.shape
    handle_count = handles.shape[1]
    nuisance = np.column_stack(
        (
            np.ones(sample_count, dtype=np.float64),
            sensor,
            process_bank.reshape(sample_count, source_count * V028_INTERNAL_DIM),
            handles,
        )
    )
    interactions = (
        handles[:, :, None, None] * process_bank[:, None, :, :]
    ).reshape(sample_count, handle_count * source_count * V028_INTERNAL_DIM)
    outcome_residual = _ridge_residuals(nuisance, next_sensor)
    interaction_residual = _ridge_residuals(nuisance, interactions).reshape(
        sample_count, handle_count, source_count, V028_INTERNAL_DIM
    )
    return outcome_residual, interaction_residual


def _effect_operator(interaction: np.ndarray, outcome: np.ndarray) -> np.ndarray:
    z = np.asarray(interaction, dtype=np.float64)
    r = np.asarray(outcome, dtype=np.float64)
    penalty = V028_REGRESSION_RIDGE * np.eye(V028_INTERNAL_DIM, dtype=np.float64)
    return np.linalg.solve(z.T @ z + penalty, z.T @ r)


def _effect_bank(interactions: np.ndarray, outcome: np.ndarray) -> np.ndarray:
    handle_count, source_count = interactions.shape[1:3]
    effects = np.empty(
        (handle_count, source_count, V028_INTERNAL_DIM, V028_SENSOR_DIM),
        dtype=np.float64,
    )
    for handle_index in range(handle_count):
        for source_index in range(source_count):
            effects[handle_index, source_index] = _effect_operator(
                interactions[:, handle_index, source_index], outcome
            )
    return effects


def _familywise_threshold(
    interactions: np.ndarray,
    outcome: np.ndarray,
    *,
    seed: int,
    permutations: int,
) -> float:
    if int(permutations) < 1:
        raise ValueError("permutations must be positive")
    rng = np.random.default_rng(int(seed))
    maxima = np.empty(int(permutations), dtype=np.float64)
    for permutation_index in range(len(maxima)):
        # Break the prospective instrument/outcome alignment while preserving
        # the dynamically predictable structure of the sensory residual.
        permuted = interactions[rng.permutation(len(interactions))]
        effects = _effect_bank(permuted, outcome)
        maximum = 0.0
        for effect in effects.reshape(-1, V028_INTERNAL_DIM, V028_SENSOR_DIM):
            maximum = max(
                maximum,
                float(np.linalg.svd(effect, compute_uv=False)[0]),
            )
        maxima[permutation_index] = maximum
    return float(np.quantile(maxima, V028_NULL_QUANTILE))


@dataclass(frozen=True)
class DiscoveredInterventionProvenance:
    """A fail-closed provenance choice and its complete discovery diagnostics."""

    selected_handle_index: int | None
    selected_source_index: int | None
    rank: int
    internal_projector: np.ndarray
    sensory_projector: np.ndarray
    singular_values: np.ndarray
    familywise_null_threshold: float
    half_a_threshold: float
    half_b_threshold: float
    half_a_directional: np.ndarray
    half_b_directional: np.ndarray
    replicated_mask: np.ndarray
    pair_ranks: np.ndarray
    ambiguous: bool

    def candidate_signal(
        self,
        process_bank: np.ndarray,
        handles: np.ndarray,
    ) -> np.ndarray:
        """Produce the learned gated intervention signal without hidden truth.

        A failed or ambiguous model returns an all-zero signal.  This makes the
        downstream behavior fail closed rather than silently choosing a pair.
        """

        bank = np.asarray(process_bank, dtype=np.float64)
        gates = np.asarray(handles, dtype=np.float64)
        if bank.ndim != 3 or bank.shape[2] != V028_INTERNAL_DIM:
            raise ValueError("process_bank must have shape (samples, sources, 8)")
        if gates.ndim != 2 or gates.shape[0] != bank.shape[0]:
            raise ValueError("handles must have shape (samples, handles)")
        if self.selected_source_index is None or self.selected_handle_index is None:
            return np.zeros((len(bank), V028_INTERNAL_DIM), dtype=np.float64)
        if not 0 <= self.selected_source_index < bank.shape[1]:
            raise ValueError("learned source index is absent from process_bank")
        if not 0 <= self.selected_handle_index < gates.shape[1]:
            raise ValueError("learned handle index is absent from handles")
        gated = (
            gates[:, self.selected_handle_index, None]
            * bank[:, self.selected_source_index, :]
        )
        return gated @ self.internal_projector


def discover_intervention_provenance(
    sensor: np.ndarray,
    process_bank: np.ndarray,
    handles: np.ndarray,
    next_sensor: np.ndarray,
    *,
    seed: int,
    permutations: int = V028_NULL_PERMUTATIONS,
    half_permutations: int = V028_HALF_NULL_PERMUTATIONS,
) -> DiscoveredInterventionProvenance:
    """Discover one replicated handle/process causal interface without labels.

    Modes must exceed a familywise max-singular temporal-permutation threshold
    on the full sample and reproduce directionally in both disjoint halves.
    The estimator returns no interface if zero or multiple candidate pairs
    retain replicated modes.
    """

    y, bank, gates, nxt = _validate_discovery_arrays(
        sensor, process_bank, handles, next_sensor
    )
    outcome, interactions = _residualized_problem(y, bank, gates, nxt)
    effects = _effect_bank(interactions, outcome)
    handle_count, source_count = effects.shape[:2]
    mode_count = min(V028_INTERNAL_DIM, V028_SENSOR_DIM)

    singular = np.empty((handle_count, source_count, mode_count), dtype=np.float64)
    left_vectors = np.empty(
        (handle_count, source_count, V028_INTERNAL_DIM, mode_count),
        dtype=np.float64,
    )
    right_vectors = np.empty(
        (handle_count, source_count, mode_count, V028_SENSOR_DIM),
        dtype=np.float64,
    )
    for handle_index in range(handle_count):
        for source_index in range(source_count):
            left, values, right = np.linalg.svd(
                effects[handle_index, source_index], full_matrices=False
            )
            singular[handle_index, source_index] = values
            left_vectors[handle_index, source_index] = left
            right_vectors[handle_index, source_index] = right

    threshold = _familywise_threshold(
        interactions, outcome, seed=int(seed), permutations=int(permutations)
    )
    midpoint = len(y) // 2
    outcome_a, interactions_a = _residualized_problem(
        y[:midpoint], bank[:midpoint], gates[:midpoint], nxt[:midpoint]
    )
    outcome_b, interactions_b = _residualized_problem(
        y[midpoint:], bank[midpoint:], gates[midpoint:], nxt[midpoint:]
    )
    effects_a = _effect_bank(interactions_a, outcome_a)
    effects_b = _effect_bank(interactions_b, outcome_b)
    threshold_a = _familywise_threshold(
        interactions_a,
        outcome_a,
        seed=int(seed) + 1,
        permutations=int(half_permutations),
    )
    threshold_b = _familywise_threshold(
        interactions_b,
        outcome_b,
        seed=int(seed) + 2,
        permutations=int(half_permutations),
    )

    directional_a = np.empty_like(singular)
    directional_b = np.empty_like(singular)
    replicated = np.zeros_like(singular, dtype=bool)
    for handle_index in range(handle_count):
        for source_index in range(source_count):
            for mode_index in range(mode_count):
                left = left_vectors[handle_index, source_index, :, mode_index]
                right = right_vectors[handle_index, source_index, mode_index]
                value_a = float(
                    abs(left @ effects_a[handle_index, source_index] @ right)
                )
                value_b = float(
                    abs(left @ effects_b[handle_index, source_index] @ right)
                )
                directional_a[handle_index, source_index, mode_index] = value_a
                directional_b[handle_index, source_index, mode_index] = value_b
                replicated[handle_index, source_index, mode_index] = bool(
                    singular[handle_index, source_index, mode_index] > threshold
                    and value_a > threshold_a
                    and value_b > threshold_b
                )

    pair_ranks = np.sum(replicated, axis=2, dtype=np.int64)
    selected_pairs = np.argwhere(pair_ranks > 0)
    ambiguous = bool(len(selected_pairs) > 1)
    if len(selected_pairs) == 1:
        selected_handle = int(selected_pairs[0, 0])
        selected_source = int(selected_pairs[0, 1])
        selected_modes = np.flatnonzero(replicated[selected_handle, selected_source])
        internal_basis = left_vectors[selected_handle, selected_source][:, selected_modes]
        sensory_basis = right_vectors[selected_handle, selected_source][selected_modes].T
        internal_projector = internal_basis @ internal_basis.T
        sensory_projector = sensory_basis @ sensory_basis.T
        rank = int(len(selected_modes))
    else:
        selected_handle = None
        selected_source = None
        rank = 0
        internal_projector = np.zeros(
            (V028_INTERNAL_DIM, V028_INTERNAL_DIM), dtype=np.float64
        )
        sensory_projector = np.zeros(
            (V028_SENSOR_DIM, V028_SENSOR_DIM), dtype=np.float64
        )

    return DiscoveredInterventionProvenance(
        selected_handle_index=selected_handle,
        selected_source_index=selected_source,
        rank=rank,
        internal_projector=internal_projector,
        sensory_projector=sensory_projector,
        singular_values=singular,
        familywise_null_threshold=threshold,
        half_a_threshold=threshold_a,
        half_b_threshold=threshold_b,
        half_a_directional=directional_a,
        half_b_directional=directional_b,
        replicated_mask=replicated,
        pair_ranks=pair_ranks,
        ambiguous=ambiguous,
    )


@dataclass(frozen=True)
class _HiddenProvenanceRoute:
    """Evaluator-only source and handle permutation for one seed."""

    source_order: tuple[str, ...]
    handle_order: tuple[str, ...]
    true_source_index: int
    true_handle_index: int

    def source_index(self, kind: str) -> int:
        return self.source_order.index(str(kind))

    def handle_index(self, kind: str) -> int:
        return self.handle_order.index(str(kind))


@dataclass(frozen=True)
class _FunctionalInterface:
    handle_index: int | None
    source_index: int | None
    internal_projector: np.ndarray
    sensory_projector: np.ndarray

    def candidate_signal(
        self, process_bank: np.ndarray, handles: np.ndarray
    ) -> np.ndarray:
        bank = np.asarray(process_bank, dtype=np.float64)
        gates = np.asarray(handles, dtype=np.float64)
        if self.handle_index is None or self.source_index is None:
            return np.zeros((len(bank), V028_INTERNAL_DIM), dtype=np.float64)
        return (
            gates[:, self.handle_index, None] * bank[:, self.source_index]
        ) @ self.internal_projector


def _seed_ordinal(seed: int) -> int:
    value = int(seed)
    if value in V028_DEVELOPMENT_SEEDS:
        return V028_DEVELOPMENT_SEEDS.index(value)
    if value in V028_PILOT_SEEDS:
        return V028_PILOT_SEEDS.index(value)
    return abs(value) % 4


def _hidden_provenance_route(seed: int) -> _HiddenProvenanceRoute:
    """Create balanced but hidden evaluator truth without exposing it to discovery."""

    ordinal = _seed_ordinal(seed)
    official_source_slots = (2, 5, 1, 4)
    pilot_source_slots = (0, 3, 5, 2)
    official_handle_slots = (1, 3, 0, 2)
    pilot_handle_slots = (2, 0, 3, 1)
    if int(seed) in V028_DEVELOPMENT_SEEDS:
        true_source_index = official_source_slots[ordinal]
        true_handle_index = official_handle_slots[ordinal]
    else:
        true_source_index = pilot_source_slots[ordinal]
        true_handle_index = pilot_handle_slots[ordinal]
    rng = np.random.default_rng(int(seed) + 28_041)
    source_order: list[str | None] = [None] * V028_SOURCE_COUNT
    source_order[true_source_index] = "true_private"
    remaining_source_slots = [i for i, value in enumerate(source_order) if value is None]
    remaining_source_kinds = list(V028_SOURCE_KINDS[1:])
    rng.shuffle(remaining_source_kinds)
    for index, kind in zip(remaining_source_slots, remaining_source_kinds):
        source_order[index] = kind
    handle_order: list[str | None] = [None] * V028_HANDLE_COUNT
    handle_order[true_handle_index] = "true_private"
    remaining_handle_slots = [i for i, value in enumerate(handle_order) if value is None]
    remaining_handle_kinds = list(V028_GATEABLE_SOURCE_KINDS[1:])
    rng.shuffle(remaining_handle_kinds)
    for index, kind in zip(remaining_handle_slots, remaining_handle_kinds):
        handle_order[index] = kind
    return _HiddenProvenanceRoute(
        source_order=tuple(str(value) for value in source_order),
        handle_order=tuple(str(value) for value in handle_order),
        true_source_index=true_source_index,
        true_handle_index=true_handle_index,
    )


def _bounded_source(rng: np.random.Generator) -> np.ndarray:
    value = rng.normal(size=V028_INTERNAL_DIM)
    return V028_SOURCE_AMPLITUDE * value / (np.linalg.norm(value) + 1e-12)


def _balanced_handles(
    rng: np.random.Generator, steps: int, *, active_handle: int | None
) -> np.ndarray:
    if int(steps) % 2:
        raise ValueError("balanced provenance episodes require an even step count")
    result = np.zeros((int(steps), V028_HANDLE_COUNT), dtype=np.float64)
    for handle_index in range(V028_HANDLE_COUNT):
        values = np.concatenate(
            (
                np.zeros(int(steps) // 2, dtype=np.float64),
                np.ones(int(steps) // 2, dtype=np.float64),
            )
        )
        result[:, handle_index] = values[rng.permutation(int(steps))]
    if active_handle is not None:
        if not 0 <= int(active_handle) < V028_HANDLE_COUNT:
            raise ValueError("active handle is outside the anonymous handle bank")
        keep = result[:, int(active_handle)].copy()
        result.fill(0.0)
        result[:, int(active_handle)] = keep
    return result


def _episode_stream(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    sensory_mixing: np.ndarray,
    internal_basis: np.ndarray,
    internal_complement: np.ndarray,
    route: _HiddenProvenanceRoute,
    *,
    steps: int,
    episode: int,
    condition: str,
    active_handle: int | None,
) -> dict[str, Any]:
    offsets = {
        "calibration": 0,
        "self_remap": 101,
        "other_takeover": 211,
        "true_route_lesion": 101,
        "decoy_stream_lesion": 101,
    }
    if condition not in offsets:
        raise ValueError(f"unknown provenance condition: {condition}")
    rng = np.random.default_rng(
        int(seed) + 28_000_000 + 317 * int(episode) + offsets[condition]
    )
    calibration = condition == "calibration"
    handles = _balanced_handles(
        rng, int(steps), active_handle=None if calibration else active_handle
    )
    if not calibration and active_handle is None:
        handles.fill(0.0)
    commitment_digest = hashlib.sha256(handles.tobytes(order="C")).hexdigest()
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    position = rng.uniform(-1.0, 1.0, size=2)
    other_position = rng.uniform(-1.0, 1.0, size=2)
    goal = rng.uniform(-1.0, 1.0, size=2)
    nuisance = rng.normal(0.0, 0.8, size=8)
    last_action = np.zeros(2, dtype=np.float64)
    previous_action = np.zeros(2, dtype=np.float64)
    previous_true = _bounded_source(rng)
    sensor_now = sensory_mixing @ np.concatenate(
        (position, other_position, nuisance)
    )
    remap = _remap_matrix(episode)
    sensor_rows: list[np.ndarray] = []
    bank_rows: list[np.ndarray] = []
    next_rows: list[np.ndarray] = []
    source_norm_errors: list[float] = []

    for step in range(int(steps)):
        observation = _native_observation(
            position, goal, last_action, step, int(steps) + 2
        )
        focal_result = focal.step(observation, source=f"v028_{condition}_focal")
        other_result = other.step(observation, source=f"v028_{condition}_other")
        base_action = V028_BASE_ACTION_SCALE * focal_result.action
        true_source = _bounded_source(rng)
        delayed_source = previous_true.copy()
        policy_latent = np.concatenate(
            (
                1.9 * np.asarray(focal_result.action, dtype=np.float64)
                + 0.7 * previous_action,
                rng.normal(0.0, V028_POLICY_SOURCE_NOISE, size=6),
            )
        )
        policy_source = (
            internal_basis @ policy_latent[:2]
            + internal_complement @ policy_latent[2:]
        )
        policy_source = (
            V028_SOURCE_AMPLITUDE
            * policy_source
            / (np.linalg.norm(policy_source) + 1e-12)
        )
        latent_sources = {
            "true_private": true_source,
            "delayed_echo": delayed_source,
            "policy_correlated": policy_source,
            "independent": _bounded_source(rng),
            "exogenous_causal": _bounded_source(rng),
            "other_disturbance": _bounded_source(rng),
        }
        if condition == "decoy_stream_lesion":
            latent_sources["delayed_echo"] = np.zeros(
                V028_INTERNAL_DIM, dtype=np.float64
            )
        observed_bank = np.stack(
            [latent_sources[kind] for kind in route.source_order]
        )
        if condition != "decoy_stream_lesion":
            source_norm_errors.extend(
                abs(np.linalg.norm(value) - V028_SOURCE_AMPLITUDE)
                for value in latent_sources.values()
            )

        true_gate = handles[step, route.true_handle_index]
        private_motor = internal_basis.T @ (true_gate * true_source)
        external_motor = internal_basis.T @ latent_sources["exogenous_causal"]
        other_motor = internal_basis.T @ latent_sources["other_disturbance"]
        if condition == "calibration":
            private_drive = private_motor
            focal_drive = base_action
        elif condition in {"self_remap", "decoy_stream_lesion"}:
            private_drive = remap @ private_motor
            focal_drive = base_action
        elif condition == "other_takeover":
            private_drive = np.zeros(2, dtype=np.float64)
            focal_drive = V028_TAKEOVER_AMPLITUDE * _other_direction(other_result)
        else:
            private_drive = np.zeros(2, dtype=np.float64)
            focal_drive = base_action
        executed = np.clip(focal_drive + private_drive, -1.0, 1.0)
        focal.register_executed_action(executed)
        other.register_executed_action(other_result.action)

        previous_sensor = sensor_now.copy()
        position = (
            0.91 * position
            + focal_drive
            + V028_PRIVATE_COUPLING * private_drive
            + V028_EXOGENOUS_COUPLING * external_motor
            + rng.normal(0.0, 0.025, size=2)
        )
        other_position = (
            0.82 * other_position
            + 0.70 * other_result.action
            + V028_OTHER_SOURCE_COUPLING * other_motor
            + rng.normal(0.0, 0.08, size=2)
        )
        nuisance = 0.72 * nuisance + rng.normal(0.0, 0.28, size=8)
        last_action = executed.copy()
        sensor_now = sensory_mixing @ np.concatenate(
            (position, other_position, nuisance)
        )
        sensor_rows.append(previous_sensor)
        bank_rows.append(observed_bank)
        next_rows.append(sensor_now.copy())
        previous_true = true_source
        previous_action = focal_result.action.copy()

    return {
        "sensor": np.stack(sensor_rows),
        "process_bank": np.stack(bank_rows),
        "handles": handles,
        "next_sensor": np.stack(next_rows),
        "receipt": {
            "condition": condition,
            "episode": int(episode),
            "gate_commitment_digest": commitment_digest,
            "commitment_precedes_source_realization": True,
            "all_handle_values_binary": bool(
                np.all((handles == 0.0) | (handles == 1.0))
            ),
            "all_handles_balanced": bool(
                not calibration or np.all(np.sum(handles, axis=0) == int(steps) // 2)
            ),
            "maximum_source_norm_error": float(max(source_norm_errors, default=0.0)),
            "echo_reset_within_episode": True,
        },
    }


def _subspace_overlap(projector: np.ndarray, truth: np.ndarray) -> float:
    return float(np.trace(np.asarray(projector) @ np.asarray(truth)) / 2.0)


def _conditional_interaction_score(
    sensor: np.ndarray,
    process_bank: np.ndarray,
    handles: np.ndarray,
    next_sensor: np.ndarray,
    interface: _FunctionalInterface,
) -> float:
    if (
        interface.handle_index is None
        or interface.source_index is None
        or np.linalg.matrix_rank(interface.internal_projector) == 0
        or np.linalg.matrix_rank(interface.sensory_projector) == 0
    ):
        return 0.0
    y = np.asarray(sensor, dtype=np.float64)
    bank = np.asarray(process_bank, dtype=np.float64)
    gates = np.asarray(handles, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    target = nxt @ interface.sensory_projector
    signal = interface.candidate_signal(bank, gates)
    base = np.column_stack(
        (
            np.ones(len(y), dtype=np.float64),
            y,
            bank.reshape(len(y), -1),
            gates,
        )
    )
    penalty0 = V028_REGRESSION_RIDGE * np.eye(base.shape[1], dtype=np.float64)
    penalty0[0, 0] = 0.05
    coefficients0 = np.linalg.solve(
        base.T @ base + penalty0, base.T @ target
    )
    error0 = float(np.mean(np.square(target - base @ coefficients0)))
    enriched = np.column_stack((base, signal))
    penalty1 = V028_REGRESSION_RIDGE * np.eye(
        enriched.shape[1], dtype=np.float64
    )
    penalty1[0, 0] = 0.05
    coefficients1 = np.linalg.solve(
        enriched.T @ enriched + penalty1, enriched.T @ target
    )
    error1 = float(np.mean(np.square(target - enriched @ coefficients1)))
    return float(np.clip((error0 - error1) / (error0 + 1e-12), 0.0, 1.0))


def _as_interface(
    model: DiscoveredInterventionProvenance,
) -> _FunctionalInterface:
    return _FunctionalInterface(
        handle_index=model.selected_handle_index,
        source_index=model.selected_source_index,
        internal_projector=model.internal_projector,
        sensory_projector=model.sensory_projector,
    )


def _passive_interface(
    sensor: np.ndarray,
    process_bank: np.ndarray,
    next_sensor: np.ndarray,
    *,
    handle_index: int | None,
) -> tuple[_FunctionalInterface, np.ndarray]:
    y = np.asarray(sensor, dtype=np.float64)
    bank = np.asarray(process_bank, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    design = np.column_stack((np.ones(len(y)), y, bank.reshape(len(y), -1)))
    penalty = V028_REGRESSION_RIDGE * np.eye(design.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.05
    coefficients = np.linalg.solve(
        design.T @ design + penalty, design.T @ nxt
    )[-V028_SOURCE_COUNT * V028_INTERNAL_DIM :]
    effects = coefficients.reshape(
        V028_SOURCE_COUNT, V028_INTERNAL_DIM, V028_SENSOR_DIM
    )
    strengths = np.asarray(
        [np.linalg.svd(effect, compute_uv=False)[0] for effect in effects]
    )
    source_index = int(np.argmax(strengths))
    left, _, right = np.linalg.svd(effects[source_index], full_matrices=False)
    return (
        _FunctionalInterface(
            handle_index=handle_index,
            source_index=source_index,
            internal_projector=left[:, :2] @ left[:, :2].T,
            sensory_projector=right[:2].T @ right[:2],
        ),
        strengths,
    )


def _pca_interface(
    process_bank: np.ndarray,
    sensor: np.ndarray,
    next_sensor: np.ndarray,
    *,
    handle_index: int | None,
) -> _FunctionalInterface:
    bank = np.asarray(process_bank, dtype=np.float64)
    source_strengths: list[float] = []
    source_bases: list[np.ndarray] = []
    for source_index in range(bank.shape[1]):
        _, values, right = np.linalg.svd(
            bank[:, source_index] - bank[:, source_index].mean(axis=0),
            full_matrices=False,
        )
        source_strengths.append(float(np.sum(np.square(values[:2]))))
        source_bases.append(right[:2].T)
    source_index = int(np.argmax(source_strengths))
    internal_basis = source_bases[source_index]
    delta = np.asarray(next_sensor) - np.asarray(sensor)
    _, _, right = np.linalg.svd(delta - delta.mean(axis=0), full_matrices=False)
    sensory_basis = right[:2].T
    return _FunctionalInterface(
        handle_index=handle_index,
        source_index=source_index,
        internal_projector=internal_basis @ internal_basis.T,
        sensory_projector=sensory_basis @ sensory_basis.T,
    )


def _pair_strengths(model: DiscoveredInterventionProvenance) -> np.ndarray:
    directional_minimum = np.minimum(
        np.minimum(model.singular_values, model.half_a_directional),
        model.half_b_directional,
    )
    return np.max(directional_minimum, axis=2)


def _learner_null_seed(handles: np.ndarray, label: str) -> int:
    """Derive a public null RNG seed without exposing the hidden world seed."""

    gates = np.asarray(handles, dtype=np.float64)
    digest = hashlib.sha256()
    digest.update(b"rrct.v028.provenance-null.v1\0")
    digest.update(str(label).encode("utf-8"))
    digest.update(gates.shape[0].to_bytes(8, "little", signed=False))
    digest.update(gates.shape[1].to_bytes(8, "little", signed=False))
    digest.update(gates.tobytes(order="C"))
    return int.from_bytes(digest.digest()[:8], "little", signed=False)


def _run_intervention_provenance_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    predictor, forecaster, *_ = _train_bundle(seed)
    sensory_mixing = _orthogonal_mixing(seed + 2_528)
    internal_basis, internal_complement = _internal_interface(seed + 2_628)
    true_internal = internal_basis @ internal_basis.T
    true_sensory_basis = sensory_mixing[:, :2]
    true_sensory = true_sensory_basis @ true_sensory_basis.T
    route = _hidden_provenance_route(seed)

    calibration_parts: list[dict[str, Any]] = []
    for episode in range(V028_CALIBRATION_EPISODES):
        calibration_parts.append(
            _episode_stream(
                seed + 5 * episode,
                predictor,
                forecaster,
                sensory_mixing,
                internal_basis,
                internal_complement,
                route,
                steps=V028_CALIBRATION_STEPS,
                episode=episode,
                condition="calibration",
                active_handle=None,
            )
        )
    sensor = np.concatenate([part["sensor"] for part in calibration_parts])
    bank = np.concatenate([part["process_bank"] for part in calibration_parts])
    handles = np.concatenate([part["handles"] for part in calibration_parts])
    next_sensor = np.concatenate(
        [part["next_sensor"] for part in calibration_parts]
    )
    learned_null_seed = _learner_null_seed(handles, "learned")
    learned = discover_intervention_provenance(
        sensor, bank, handles, next_sensor, seed=learned_null_seed
    )
    rng = np.random.default_rng(seed + 28_200)
    shuffled_handles = handles.copy()
    for episode in range(V028_CALIBRATION_EPISODES):
        start = episode * V028_CALIBRATION_STEPS
        stop = start + V028_CALIBRATION_STEPS
        for handle_index in range(V028_HANDLE_COUNT):
            shuffled_handles[start:stop, handle_index] = handles[
                start:stop, handle_index
            ][rng.permutation(V028_CALIBRATION_STEPS)]
    shuffled_null_seed = _learner_null_seed(shuffled_handles, "shuffled")
    shuffled = discover_intervention_provenance(
        sensor,
        bank,
        shuffled_handles,
        next_sensor,
        seed=shuffled_null_seed,
    )
    passive, passive_strengths = _passive_interface(
        sensor,
        bank,
        next_sensor,
        handle_index=learned.selected_handle_index,
    )
    pca = _pca_interface(
        bank, sensor, next_sensor, handle_index=learned.selected_handle_index
    )
    oracle = _FunctionalInterface(
        handle_index=route.true_handle_index,
        source_index=route.true_source_index,
        internal_projector=true_internal,
        sensory_projector=true_sensory,
    )
    delayed = _FunctionalInterface(
        handle_index=learned.selected_handle_index,
        source_index=route.source_index("delayed_echo"),
        internal_projector=true_internal,
        sensory_projector=true_sensory,
    )
    exogenous = _FunctionalInterface(
        handle_index=learned.selected_handle_index,
        source_index=route.source_index("exogenous_causal"),
        internal_projector=true_internal,
        sensory_projector=true_sensory,
    )
    deranged = _FunctionalInterface(
        handle_index=learned.selected_handle_index,
        source_index=route.source_index("independent"),
        internal_projector=true_internal,
        sensory_projector=true_sensory,
    )
    interfaces = {
        "learned": _as_interface(learned),
        "oracle": oracle,
        "shuffled": _as_interface(shuffled),
        "passive": passive,
        "pca": pca,
        "delayed": delayed,
        "exogenous": exogenous,
        "deranged": deranged,
    }

    rows: list[dict[str, Any]] = []
    evaluation_receipts: list[dict[str, Any]] = []
    evaluation_parts: dict[str, list[dict[str, Any]]] = {
        condition: []
        for condition in (
            "self_remap",
            "other_takeover",
            "true_route_lesion",
            "decoy_stream_lesion",
        )
    }
    for episode in range(V028_EVALUATION_EPISODES):
        for condition in evaluation_parts:
            part = _episode_stream(
                seed + 9_000 + 7 * episode,
                predictor,
                forecaster,
                sensory_mixing,
                internal_basis,
                internal_complement,
                route,
                steps=V028_EVALUATION_STEPS,
                episode=episode,
                condition=condition,
                active_handle=learned.selected_handle_index,
            )
            evaluation_parts[condition].append(part)
            evaluation_receipts.append(part["receipt"])

    for condition, parts in evaluation_parts.items():
        condition_sensor = np.concatenate([part["sensor"] for part in parts])
        condition_bank = np.concatenate(
            [part["process_bank"] for part in parts]
        )
        condition_handles = np.concatenate([part["handles"] for part in parts])
        condition_next = np.concatenate(
            [part["next_sensor"] for part in parts]
        )
        row: dict[str, Any] = {
            "seed": seed,
            "condition": condition,
            "episode_count": V028_EVALUATION_EPISODES,
            "transition_count": len(condition_sensor),
        }
        for name, interface in interfaces.items():
            row[f"{name}_score"] = _conditional_interaction_score(
                condition_sensor,
                condition_bank,
                condition_handles,
                condition_next,
                interface,
            )
        rows.append(row)

    def mean(condition: str, key: str) -> float:
        return float(
            np.mean([row[key] for row in rows if row["condition"] == condition])
        )

    strengths = _pair_strengths(learned)
    true_strength = float(
        strengths[route.true_handle_index, route.true_source_index]
    )
    false_strengths = strengths.copy()
    false_strengths[route.true_handle_index, route.true_source_index] = -np.inf
    best_false_strength = float(np.max(false_strengths))
    replicated_count = int(np.sum(learned.replicated_mask))
    true_replicated_count = int(
        np.sum(
            learned.replicated_mask[
                route.true_handle_index, route.true_source_index
            ]
        )
    )
    false_mass = float(
        (replicated_count - true_replicated_count) / max(replicated_count, 1)
    )
    passive_source = int(passive.source_index)
    pca_source = int(pca.source_index)
    calibration_receipts = [part["receipt"] for part in calibration_parts]
    all_receipts = calibration_receipts + evaluation_receipts
    integrity = bool(
        all(receipt["commitment_precedes_source_realization"] for receipt in all_receipts)
        and all(receipt["all_handle_values_binary"] for receipt in all_receipts)
        and all(receipt["all_handles_balanced"] for receipt in calibration_receipts)
        and max(
            receipt["maximum_source_norm_error"] for receipt in all_receipts
        )
        < 1e-10
        and len(set(route.source_order)) == V028_SOURCE_COUNT
        and len(set(route.handle_order)) == V028_HANDLE_COUNT
    )
    summary = {
        "seed": seed,
        "selected_pair_correct": bool(
            learned.selected_handle_index == route.true_handle_index
            and learned.selected_source_index == route.true_source_index
        ),
        "selected_handle_index": learned.selected_handle_index,
        "selected_source_index": learned.selected_source_index,
        "true_handle_index": route.true_handle_index,
        "true_source_index": route.true_source_index,
        "discovered_rank": int(learned.rank),
        "internal_overlap": _subspace_overlap(
            learned.internal_projector, true_internal
        ),
        "sensory_overlap": _subspace_overlap(
            learned.sensory_projector, true_sensory
        ),
        "shuffled_rank": int(shuffled.rank),
        "shuffled_internal_overlap": _subspace_overlap(
            shuffled.internal_projector, true_internal
        ),
        "shuffled_sensory_overlap": _subspace_overlap(
            shuffled.sensory_projector, true_sensory
        ),
        "pca_internal_overlap": _subspace_overlap(
            pca.internal_projector, true_internal
        ),
        "pca_sensory_overlap": _subspace_overlap(
            pca.sensory_projector, true_sensory
        ),
        "false_pair_mass": false_mass,
        "true_pair_strength": true_strength,
        "best_false_pair_strength": best_false_strength,
        "true_false_strength_margin": true_strength - best_false_strength,
        "correct_lag_strength_margin": true_strength
        - float(np.max(strengths[:, route.source_index("delayed_echo")])),
        "exogenous_false_mass": float(
            np.sum(
                learned.replicated_mask[
                    :, route.source_index("exogenous_causal")
                ]
            )
            / max(replicated_count, 1)
        ),
        "delayed_false_mass": float(
            np.sum(
                learned.replicated_mask[:, route.source_index("delayed_echo")]
            )
            / max(replicated_count, 1)
        ),
        "policy_false_mass": float(
            np.sum(
                learned.replicated_mask[
                    :, route.source_index("policy_correlated")
                ]
            )
            / max(replicated_count, 1)
        ),
        "passive_selected_true": passive_source == route.true_source_index,
        "passive_selected_exogenous": passive_source
        == route.source_index("exogenous_causal"),
        "pca_selected_true": pca_source == route.true_source_index,
        "self_remap_learned": mean("self_remap", "learned_score"),
        "other_takeover_learned": mean("other_takeover", "learned_score"),
        "learned_self_other_separation": mean("self_remap", "learned_score")
        - mean("other_takeover", "learned_score"),
        "self_remap_oracle": mean("self_remap", "oracle_score"),
        "oracle_gap": mean("self_remap", "oracle_score")
        - mean("self_remap", "learned_score"),
        "self_remap_shuffled": mean("self_remap", "shuffled_score"),
        "self_remap_passive": mean("self_remap", "passive_score"),
        "self_remap_pca": mean("self_remap", "pca_score"),
        "self_remap_delayed": mean("self_remap", "delayed_score"),
        "self_remap_exogenous": mean("self_remap", "exogenous_score"),
        "self_remap_deranged": mean("self_remap", "deranged_score"),
        "true_route_lesion_learned": mean(
            "true_route_lesion", "learned_score"
        ),
        "decoy_stream_lesion_learned": mean(
            "decoy_stream_lesion", "learned_score"
        ),
        "lesion_selectivity": mean("decoy_stream_lesion", "learned_score")
        - mean("true_route_lesion", "learned_score"),
        "decoy_stream_retention_gap": abs(
            mean("decoy_stream_lesion", "learned_score")
            - mean("self_remap", "learned_score")
        ),
        "integrity": integrity,
    }
    return {
        "seed": seed,
        "seed_summary": summary,
        "rows": rows,
        "discovery_receipt": {
            "seed": seed,
            "selected_handle_index": learned.selected_handle_index,
            "selected_source_index": learned.selected_source_index,
            "selected_rank": int(learned.rank),
            "candidate_handle_count": V028_HANDLE_COUNT,
            "candidate_source_count": V028_SOURCE_COUNT,
            "singular_values": learned.singular_values.tolist(),
            "familywise_null_threshold": float(
                learned.familywise_null_threshold
            ),
            "half_a_threshold": float(learned.half_a_threshold),
            "half_b_threshold": float(learned.half_b_threshold),
            "half_a_directional": learned.half_a_directional.tolist(),
            "half_b_directional": learned.half_b_directional.tolist(),
            "replicated_mask": learned.replicated_mask.astype(int).tolist(),
            "pair_ranks": learned.pair_ranks.tolist(),
            "learner_null_seed": learned_null_seed,
            "shuffled_null_seed": shuffled_null_seed,
            "source_order_evaluator_only": list(route.source_order),
            "handle_order_evaluator_only": list(route.handle_order),
            "passive_source_strengths": passive_strengths.tolist(),
            "prospective_gate_commitments_supplied": True,
            "executed_perturbation_vector_supplied": False,
            "true_source_or_handle_supplied": False,
            "source_family_labels_supplied": False,
            "hidden_route_or_projector_supplied": False,
            "actuator_or_body_coordinates_supplied": False,
            "rank_supplied": False,
            "condition_truth_supplied": False,
            "pca_or_oracle_hint_supplied": False,
            "calibration_commitment_digests": [
                receipt["gate_commitment_digest"]
                for receipt in calibration_receipts
            ],
        },
    }


def run_intervention_provenance_seed(seed: int) -> dict[str, Any]:
    """Run exactly one frozen v0.28 official seed."""

    if int(seed) not in V028_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of the frozen v0.28 official set")
    return _run_intervention_provenance_seed(int(seed))


def run_intervention_provenance_pilot_seed(seed: int) -> dict[str, Any]:
    """Run a declared nonofficial seed before the pre-outcome freeze."""

    if int(seed) not in V028_PILOT_SEEDS:
        raise ValueError("seed is not part of the declared v0.28 pilot set")
    return _run_intervention_provenance_seed(int(seed))


def _bootstrap_interval(values: Sequence[float], salt: int) -> tuple[float, float]:
    data = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V028_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V028_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for index in range(len(draws)):
        draws[index] = float(
            np.mean(data[rng.integers(0, len(data), size=len(data))])
        )
    return (
        float(np.quantile(draws, 0.025)),
        float(np.quantile(draws, 0.975)),
    )


def aggregate_intervention_provenance_results(
    parts: Sequence[Mapping[str, Any]], output: str | Path
) -> dict[str, Any]:
    """Aggregate the four untouched official seeds and evaluate frozen gates."""

    by_seed = {int(part["seed"]): part for part in parts}
    if tuple(sorted(by_seed)) != tuple(sorted(V028_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly the frozen v0.28 seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")
    seed_rows = [by_seed[seed]["seed_summary"] for seed in V028_DEVELOPMENT_SEEDS]
    rows = [row for seed in V028_DEVELOPMENT_SEEDS for row in by_seed[seed]["rows"]]
    receipts = [
        by_seed[seed]["discovery_receipt"] for seed in V028_DEVELOPMENT_SEEDS
    ]
    excluded = {
        "seed",
        "selected_handle_index",
        "selected_source_index",
        "true_handle_index",
        "true_source_index",
        "discovered_rank",
        "shuffled_rank",
        "integrity",
        "selected_pair_correct",
        "passive_selected_true",
        "passive_selected_exogenous",
        "pca_selected_true",
    }
    numeric_fields = [
        key
        for key, value in seed_rows[0].items()
        if key not in excluded and isinstance(value, (int, float, np.floating))
    ]
    values = {
        key: [float(row[key]) for row in seed_rows] for key in numeric_fields
    }
    means = {key: float(np.mean(value)) for key, value in values.items()}
    intervals = {
        key: _bootstrap_interval(value, index)
        for index, (key, value) in enumerate(values.items())
    }
    privilege_integrity = all(
        receipt["prospective_gate_commitments_supplied"]
        and not receipt["executed_perturbation_vector_supplied"]
        and not receipt["true_source_or_handle_supplied"]
        and not receipt["source_family_labels_supplied"]
        and not receipt["hidden_route_or_projector_supplied"]
        and not receipt["actuator_or_body_coordinates_supplied"]
        and not receipt["rank_supplied"]
        and not receipt["condition_truth_supplied"]
        and not receipt["pca_or_oracle_hint_supplied"]
        for receipt in receipts
    )
    true_handles = [int(row["true_handle_index"]) for row in seed_rows]
    true_sources = [int(row["true_source_index"]) for row in seed_rows]
    gates = {
        "unique_provenance_pair_recovered": all(
            bool(row["selected_pair_correct"]) for row in seed_rows
        ),
        "rank_discovered_correctly": all(
            int(row["discovered_rank"]) == 2 for row in seed_rows
        ),
        "hidden_internal_interface_recovered": intervals["internal_overlap"][0]
        > 0.97,
        "hidden_sensory_interface_recovered": intervals["sensory_overlap"][0]
        > 0.97,
        "false_provenance_mass_bounded": intervals["false_pair_mass"][1]
        < 0.10,
        "true_pair_beats_all_decoys": intervals[
            "true_false_strength_margin"
        ][0]
        > 1.00,
        "exogenous_cause_not_misattributed": intervals[
            "exogenous_false_mass"
        ][1]
        < 0.10,
        "echo_and_policy_not_misattributed": intervals["delayed_false_mass"][1]
        < 0.10
        and intervals["policy_false_mass"][1] < 0.10
        and intervals["correct_lag_strength_margin"][0] > 1.00,
        "gate_shuffle_destroys_provenance": all(
            int(row["shuffled_rank"]) == 0 for row in seed_rows
        )
        and intervals["shuffled_internal_overlap"][1] < 0.15
        and intervals["shuffled_sensory_overlap"][1] < 0.15,
        "passive_association_prefers_exogenous": all(
            bool(row["passive_selected_exogenous"])
            and not bool(row["passive_selected_true"])
            for row in seed_rows
        )
        and intervals["self_remap_passive"][1] < 0.08,
        "variance_pca_not_functional": intervals["self_remap_pca"][1] < 0.08,
        "remap_uses_discovered_provenance": intervals["self_remap_learned"][0]
        > 0.18,
        "takeover_rejected": intervals["other_takeover_learned"][1] < 0.08,
        "functional_self_other_separation": intervals[
            "learned_self_other_separation"
        ][0]
        > 0.17,
        "near_oracle_function": intervals["oracle_gap"][1] < 0.05,
        "route_and_stream_lesions_selective": intervals[
            "true_route_lesion_learned"
        ][1]
        < 0.05
        and intervals["decoy_stream_lesion_learned"][0] > 0.18
        and intervals["lesion_selectivity"][0] > 0.16
        and intervals["decoy_stream_retention_gap"][1] < 0.05,
        "strong_wrong_sources_not_functional": intervals[
            "self_remap_delayed"
        ][1]
        < 0.08
        and intervals["self_remap_exogenous"][1] < 0.08
        and intervals["self_remap_deranged"][1] < 0.08
        and intervals["self_remap_shuffled"][1] < 0.08,
        "discovery_has_no_privileged_provenance": privilege_integrity,
        "permutations_and_integrity_hold": len(set(true_handles)) == 4
        and len(set(true_sources)) == 4
        and all(bool(row["integrity"]) for row in seed_rows),
    }
    result = {
        "schema": "rrct.v028.intervention_provenance.v1",
        "seeds": list(V028_DEVELOPMENT_SEEDS),
        "means": means,
        "bootstrap_95": {key: list(value) for key, value in intervals.items()},
        "selected_pairs": [
            [row["selected_handle_index"], row["selected_source_index"]]
            for row in seed_rows
        ],
        "true_pairs": [
            [row["true_handle_index"], row["true_source_index"]]
            for row in seed_rows
        ],
        "discovered_ranks": [int(row["discovered_rank"]) for row in seed_rows],
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_boundary": (
            "Active discovery of one controllable intervention source and its "
            "paired internal/sensory interface from anonymous commitments and "
            "source streams in a bounded synthetic scene; not evidence of "
            "phenomenal consciousness or subjective awareness."
        ),
    }
    with (destination / "intervention_provenance_seed_summaries.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(seed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(seed_rows)
    with (destination / "intervention_provenance_rows.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    flat_receipts: list[dict[str, Any]] = []
    for receipt in receipts:
        flat = dict(receipt)
        for key, value in list(flat.items()):
            if isinstance(value, (list, tuple, dict)):
                flat[key] = json.dumps(value, sort_keys=True)
        flat_receipts.append(flat)
    with (destination / "discovery_receipts.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat_receipts[0].keys()))
        writer.writeheader()
        writer.writerows(flat_receipts)
    summary_path = destination / "intervention_provenance_summary.json"
    summary_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    hashes: dict[str, str] = {}
    for path in sorted(destination.iterdir()):
        if path.is_file():
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (destination / "artifact_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


__all__ = [
    "V028_BOOTSTRAP_RESAMPLES",
    "V028_BOOTSTRAP_SEED",
    "V028_DEVELOPMENT_SEEDS",
    "V028_HALF_NULL_PERMUTATIONS",
    "V028_INTERNAL_DIM",
    "V028_NULL_PERMUTATIONS",
    "V028_NULL_QUANTILE",
    "V028_PILOT_SEEDS",
    "V028_REGRESSION_RIDGE",
    "V028_SENSOR_DIM",
    "DiscoveredInterventionProvenance",
    "aggregate_intervention_provenance_results",
    "discover_intervention_provenance",
    "run_intervention_provenance_pilot_seed",
    "run_intervention_provenance_seed",
]

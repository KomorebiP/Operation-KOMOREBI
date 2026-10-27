"""Development benchmark for bounded adaptive RRCT feedback.

This module tests a narrow functional hypothesis: feedback aligned to current
internal load can support externally measured delayed binding better than a
fixed feedback dose.  The study is exploratory.  It does not measure or imply
consciousness, sentience, valence, desire, or moral status.

The runner deliberately keeps outcome labels outside the agent.  A shared
label-free predictor and observation forecaster are trained once per seed,
then copied into every arm.  Arm-specific latent-factor probes are fitted on a
separate upstream split.  Predictor, forecaster, probe, and core parameters
are frozen throughout calibration and held-out evaluation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ._version import __version__
from ._release_provenance import V0_10_DEV2_SOURCE_HASHES
from .agent import RRCTAgent, StepResult
from .environment import BindingEpisode, task_names
from .feedback import FeedbackTelemetry, compute_feedback_telemetry
from .learning import LatentFactorProbe


DEVELOPMENT_SEEDS = (3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067)
FIXED_GAINS: dict[str, float] = {
    "fixed_low": 0.25,
    "fixed_mid": 0.65,
    "fixed_high": 1.05,
}
ARM_ORDER = (
    "fixed_low",
    "fixed_mid",
    "fixed_high",
    "adaptive_aligned",
    "adaptive_shuffled",
    "adaptive_no_self",
)
STATIC_ARMS = tuple(FIXED_GAINS)
REGIMES = ("low", "high", "load_up", "load_down")
SHIFTED_REGIMES = ("load_up", "load_down")
DEFAULT_SEQUENCE_LENGTH = 12
DEFAULT_BOOTSTRAP_SEED = 20260821
DEFAULT_BOOTSTRAP_RESAMPLES = 20_000
DEFAULT_SCHEDULE_SEED = 20260820
FROZEN_OFFICIAL_VERSION = "0.10.0-dev1"


@dataclass(frozen=True)
class LoadEpisode:
    """One fixed-length delayed-binding episode with an explicit load trace."""

    episode: BindingEpisode
    regime: str
    load_profile: tuple[float, ...]
    split: str
    split_index: int
    digest: str


@dataclass
class SplitRun:
    """Representations and audit records from one arm on one split."""

    features: np.ndarray
    factors: np.ndarray
    schedules: tuple[tuple[tuple[float, float], ...], ...]
    telemetry_rows: list[dict[str, Any]]
    episode_records: list[dict[str, Any]]
    frozen_audit: dict[str, Any]


def _exact_integer(value: Any, name: str, *, minimum: int = 1) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise ValueError(f"{name} must be an integer")
    parsed = int(value)
    if parsed < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return parsed


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object_digest(value: Any) -> str:
    return hashlib.sha256(pickle.dumps(value, protocol=5)).hexdigest()


def _episode_digest(
    episode: BindingEpisode,
    *,
    regime: str,
    load_profile: Sequence[float],
    split: str,
) -> str:
    if not split:
        raise ValueError("split must be nonempty")
    payload = (
        "rrct.v010.load_episode.v1",
        regime,
        tuple(float(value) for value in load_profile),
        int(episode.context),
        int(episode.object_cue),
        int(episode.actuator_map),
        np.ascontiguousarray(episode.observations, dtype=np.float64).tobytes(),
    )
    return _object_digest(payload)


def _split_digest(episodes: Sequence[LoadEpisode]) -> str:
    return _object_digest(
        (
            "rrct.v010.split.v1",
            tuple(item.digest for item in episodes),
        )
    )


def _load_profile(regime: str, sequence_length: int) -> np.ndarray:
    if regime not in REGIMES:
        raise ValueError(f"unknown load regime: {regime}")
    low = 0.18
    high = 0.92
    if regime == "low":
        return np.full(sequence_length, low, dtype=np.float64)
    if regime == "high":
        return np.full(sequence_length, high, dtype=np.float64)
    midpoint = sequence_length // 2
    if regime == "load_up":
        return np.concatenate(
            (
                np.full(midpoint, low, dtype=np.float64),
                np.full(sequence_length - midpoint, high, dtype=np.float64),
            )
        )
    return np.concatenate(
        (
            np.full(midpoint, high, dtype=np.float64),
            np.full(sequence_length - midpoint, low, dtype=np.float64),
        )
    )


def _latent_combinations() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (context, object_cue, actuator)
        for context in (-1, 1)
        for object_cue in (-1, 1)
        for actuator in (-1, 1)
    )


def _episode_design(
    count: int,
    *,
    rng: np.random.Generator,
) -> list[tuple[str, tuple[int, int, int]]]:
    """Return balanced prefixes of repeated 4-by-8 regime/factor blocks."""

    latents = _latent_combinations()
    design: list[tuple[str, tuple[int, int, int]]] = []
    block = 0
    while len(design) < count:
        factor_order = rng.permutation(len(latents))
        regime_offset = int(rng.integers(0, len(REGIMES)))
        for phase in range(len(REGIMES)):
            for position, factor_index in enumerate(factor_order):
                regime = REGIMES[
                    (position + phase + regime_offset + block) % len(REGIMES)
                ]
                design.append((regime, latents[int(factor_index)]))
                if len(design) == count:
                    return design
        block += 1
    return design


def _build_observations(
    context: int,
    object_cue: int,
    actuator: int,
    *,
    episode_marker: int,
    profile: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create a fixed-length observation sequence using the existing layout."""

    sequence_length = int(profile.size)
    observations = np.zeros((sequence_length, 12), dtype=np.float64)
    observations[0, 0] = context
    observations[0, 3] = 1.0
    observations[1, 1] = object_cue
    observations[1, 4] = 1.0
    observations[-1, 2] = actuator
    observations[-1, 5] = 1.0
    observations[:, 6] = np.linspace(0.0, 1.0, sequence_length)
    observations[-1, 7] = 1.0
    observations[:, 8] = rng.uniform(-1.0, 1.0, size=sequence_length)

    # The load manipulation is label-independent.  It changes the number and
    # amplitude of nuisance trajectories without changing the three factors.
    independent = rng.normal(0.0, 1.0, size=(sequence_length, 3))
    carrier_phase = rng.uniform(-np.pi, np.pi, size=3)
    carrier_rate = rng.uniform(0.7, 2.4, size=3)
    grid = np.linspace(0.0, 2.0 * np.pi, sequence_length)[:, None]
    carriers = np.sin(grid * carrier_rate[None, :] + carrier_phase[None, :])
    distractor_scale = 0.18 + 0.82 * profile[:, None]
    observations[:, 9:12] = distractor_scale * (
        0.72 * independent + 0.28 * carriers
    )

    noise_scale = 0.012 + 0.038 * profile[:, None]
    noisy_columns = np.r_[6, 8:12]
    observations[:, noisy_columns] += rng.normal(
        0.0,
        noise_scale,
        size=(sequence_length, len(noisy_columns)),
    )
    # The marker indexes an independently advanced RNG stream, never a label.
    if episode_marker < 0:  # pragma: no cover - construction guard
        raise ValueError("episode_marker must be nonnegative")
    return observations


def _make_load_split(
    count: int,
    *,
    seed: int,
    split: str,
    sequence_length: int,
) -> list[LoadEpisode]:
    count = _exact_integer(count, f"{split}_episode_count", minimum=8)
    sequence_length = _exact_integer(sequence_length, "sequence_length", minimum=6)
    rng = np.random.default_rng(seed)
    design = _episode_design(count, rng=rng)
    episodes: list[LoadEpisode] = []
    for index, (regime, factors) in enumerate(design):
        profile = _load_profile(regime, sequence_length)
        context, object_cue, actuator = factors
        observations = _build_observations(
            context,
            object_cue,
            actuator,
            episode_marker=index,
            profile=profile,
            rng=rng,
        )
        episode = BindingEpisode(
            observations=observations,
            context=context,
            object_cue=object_cue,
            actuator_map=actuator,
            episode_id=index,
        )
        digest = _episode_digest(
            episode,
            regime=regime,
            load_profile=profile,
            split=split,
        )
        episodes.append(
            LoadEpisode(
                episode=episode,
                regime=regime,
                load_profile=tuple(float(value) for value in profile),
                split=split,
                split_index=index,
                digest=digest,
            )
        )
    return episodes


def _make_agent(
    seed: int,
    *,
    arm: str,
    predictor_snapshot: Mapping[str, Any],
    forecaster_snapshot: Mapping[str, Any],
) -> RRCTAgent:
    if arm not in ARM_ORDER:
        raise ValueError(f"unknown arm: {arm}")
    if arm in FIXED_GAINS:
        gain = FIXED_GAINS[arm]
        feedback_mode = "fixed"
        ablations: tuple[str, ...] = ()
    else:
        gain = FIXED_GAINS["fixed_mid"]
        feedback_mode = "manual" if arm == "adaptive_shuffled" else "adaptive"
        ablations = ()
    agent = RRCTAgent(
        12,
        action_dim=2,
        projector_ranks=(3, 6, 9, 12),
        n_specialists=8,
        specialist_dim=16,
        workspace_dim=16,
        workspace_capacity=4,
        self_dim=12,
        memory_capacity=64,
        memory_top_k=4,
        seed=seed,
        recurrent_gain=gain,
        closure_gain=gain,
        self_feedback_gain=0.0 if arm == "adaptive_no_self" else 1.0,
        action_feedback_gain=1.0,
        self_model_mode="frozen",
        feedback_mode=feedback_mode,
        feedback_minimum_gain=0.15,
        feedback_maximum_gain=1.20,
        feedback_adaptation_rate=0.35,
        feedback_maximum_step=0.12,
        feedback_deadband=0.02,
        ablations=ablations,
    )
    agent.load_predictor_snapshot(predictor_snapshot, freeze=True)
    agent.load_observation_forecaster_snapshot(forecaster_snapshot, freeze=True)
    agent.freeze_self_model()
    return agent


def _train_shared_predictors(
    seed: int,
    episodes: Sequence[LoadEpisode],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    gain = FIXED_GAINS["fixed_mid"]
    agent = RRCTAgent(
        12,
        action_dim=2,
        projector_ranks=(3, 6, 9, 12),
        n_specialists=8,
        specialist_dim=16,
        workspace_dim=16,
        workspace_capacity=4,
        self_dim=12,
        memory_capacity=64,
        memory_top_k=4,
        seed=seed,
        recurrent_gain=gain,
        closure_gain=gain,
        self_feedback_gain=1.0,
        action_feedback_gain=1.0,
        self_model_mode="train",
        feedback_mode="fixed",
    )
    for item in episodes:
        agent.reset()
        for observation in item.episode.observations:
            agent.step(observation, source="v010_predictor_training")
    agent.freeze_self_model()
    predictor = agent.predictor_snapshot()
    forecaster = agent.observation_forecaster_snapshot()
    receipt = {
        "seed": int(seed),
        "episode_count": len(episodes),
        "step_count": int(sum(len(item.episode.observations) for item in episodes)),
        "predictor_learning_steps": int(predictor["learning_steps"]),
        "forecaster_learning_steps": int(forecaster["learning_steps"]),
        "predictor_digest": _object_digest(predictor),
        "forecaster_digest": _object_digest(forecaster),
        "training_split_digest": _split_digest(episodes),
    }
    return predictor, forecaster, receipt


def _derangement(count: int, *, seed: int) -> tuple[int, ...]:
    count = _exact_integer(count, "schedule count", minimum=2)
    rng = np.random.default_rng(seed)
    identity = np.arange(count, dtype=int)
    for _ in range(10_000):
        candidate = rng.permutation(count)
        if np.all(candidate != identity):
            return tuple(int(value) for value in candidate)
    # This deterministic cyclic fallback is also a derangement.
    shift = 1 + int(seed) % (count - 1)
    return tuple(int(value) for value in np.roll(identity, shift))


def _regime_derangement(
    episodes: Sequence[LoadEpisode], *, seed: int
) -> tuple[int, ...]:
    """Match every target to a distinct source from another load regime."""

    count = _exact_integer(len(episodes), "schedule count", minimum=2)
    rng = np.random.default_rng(seed)
    candidate_orders = {
        target: tuple(
            int(source)
            for source in rng.permutation(count)
            if episodes[int(source)].regime != episodes[target].regime
        )
        for target in range(count)
    }
    if any(not order for order in candidate_orders.values()):
        raise ValueError("load regimes do not admit a cross-regime schedule control")
    source_to_target: dict[int, int] = {}

    def assign(target: int, seen: set[int]) -> bool:
        for source in candidate_orders[target]:
            if source in seen:
                continue
            seen.add(source)
            previous_target = source_to_target.get(source)
            if previous_target is None or assign(previous_target, seen):
                source_to_target[source] = target
                return True
        return False

    target_order = tuple(int(value) for value in rng.permutation(count))
    for target in target_order:
        if not assign(target, set()):
            raise ValueError("load regimes do not admit a cross-regime schedule control")
    permutation = [-1] * count
    for source, target in source_to_target.items():
        permutation[target] = source
    if (
        sorted(permutation) != list(range(count))
        or any(source == target for target, source in enumerate(permutation))
        or any(
            episodes[source].regime == episodes[target].regime
            for target, source in enumerate(permutation)
        )
    ):
        raise RuntimeError("cross-regime schedule matching failed its audit")
    return tuple(permutation)


def _telemetry_dict(telemetry: FeedbackTelemetry) -> dict[str, float]:
    return {key: float(value) for key, value in asdict(telemetry).items()}


def _run_split(
    agent: RRCTAgent,
    episodes: Sequence[LoadEpisode],
    *,
    seed: int,
    arm: str,
    split: str,
    manual_schedules: Sequence[Sequence[tuple[float, float]]] | None = None,
    schedule_sources: Sequence[int] | None = None,
) -> SplitRun:
    if (manual_schedules is None) != (schedule_sources is None):
        raise ValueError("manual schedules and sources must be supplied together")
    if arm == "adaptive_shuffled":
        if manual_schedules is None or len(manual_schedules) != len(episodes):
            raise ValueError("the shuffled arm requires one manual schedule per episode")
        if schedule_sources is None or len(schedule_sources) != len(episodes):
            raise ValueError("the shuffled arm requires one source per episode")
        if any(
            isinstance(source, (bool, np.bool_))
            or not isinstance(source, (int, np.integer))
            or not 0 <= int(source) < len(episodes)
            for source in schedule_sources
        ):
            raise ValueError("schedule source indices must address this split")
    elif manual_schedules is not None:
        raise ValueError("manual schedules are valid only for the shuffled arm")

    self_updates_before = int(agent.self_learning_updates)
    forecaster_updates_before = int(agent.observation_forecaster.learning_steps)
    features: list[np.ndarray] = []
    factors: list[tuple[int, int, int]] = []
    schedules: list[tuple[tuple[float, float], ...]] = []
    telemetry_rows: list[dict[str, Any]] = []
    episode_records: list[dict[str, Any]] = []

    for episode_index, item in enumerate(episodes):
        agent.reset()
        previous_workspace = np.zeros(agent.workspace_dim, dtype=np.float64)
        schedule: list[tuple[float, float]] = []
        episode_telemetry: list[FeedbackTelemetry] = []
        final: StepResult | None = None
        source_index = (
            int(schedule_sources[episode_index])
            if schedule_sources is not None
            else episode_index
        )
        source_hash = episodes[source_index].digest if schedule_sources is not None else item.digest
        for step_index, observation in enumerate(item.episode.observations):
            if manual_schedules is not None:
                manual_schedule = manual_schedules[episode_index]
                if len(manual_schedule) != len(item.episode.observations):
                    raise ValueError("manual schedule length does not match the episode")
                requested_recurrent, requested_closure = manual_schedule[step_index]
                agent.set_active_feedback(requested_recurrent, requested_closure)
            applied_recurrent = float(agent.current_recurrent_gain)
            applied_closure = float(agent.current_closure_gain)
            final = agent.step(
                observation,
                source=f"v010_{split}_{item.regime}_{arm}",
            )
            telemetry = compute_feedback_telemetry(
                specialist_states=final.specialist_states,
                specialist_salience=final.specialist_salience,
                workspace=final.workspace,
                prediction_error=final.prediction_error,
                previous_workspace=previous_workspace,
                workspace_proposal_states=final.workspace_proposal_states,
                workspace_weights=final.workspace_weights,
            )
            if arm in {"adaptive_aligned", "adaptive_no_self"}:
                record = agent.last_feedback_control
                if record is None:
                    raise RuntimeError("adaptive feedback failed to record an update")
                recorded = np.asarray(
                    tuple(asdict(record.telemetry).values()), dtype=np.float64
                )
                independently_computed = np.asarray(
                    tuple(asdict(telemetry).values()), dtype=np.float64
                )
                if not np.allclose(recorded, independently_computed, atol=1e-14, rtol=1e-14):
                    raise RuntimeError("adaptive feedback telemetry audit failed")
                if (
                    final.feedback_telemetry != record.telemetry
                    or final.applied_recurrent_gain != applied_recurrent
                    or final.applied_closure_gain != applied_closure
                    or final.next_recurrent_gain != agent.current_recurrent_gain
                    or final.next_closure_gain != agent.current_closure_gain
                ):
                    raise RuntimeError("adaptive StepResult dose audit failed")
            next_recurrent = float(agent.current_recurrent_gain)
            next_closure = float(agent.current_closure_gain)
            telemetry_values = _telemetry_dict(telemetry)
            throughput_proxy = float(
                telemetry.differentiation
                * (1.0 - telemetry.redundancy)
                * (1.0 - telemetry.saturation)
                * telemetry.salience_entropy
            )
            telemetry_rows.append(
                {
                    "seed": int(seed),
                    "split": split,
                    "arm": arm,
                    "episode_index": episode_index,
                    "episode_hash": item.digest,
                    "regime": item.regime,
                    "step": step_index,
                    "load": float(item.load_profile[step_index]),
                    "applied_recurrent_gain": applied_recurrent,
                    "applied_closure_gain": applied_closure,
                    "next_recurrent_gain": next_recurrent,
                    "next_closure_gain": next_closure,
                    "schedule_source_episode_index": source_index,
                    "schedule_source_episode_hash": source_hash,
                    **telemetry_values,
                    "bounded_integrated_throughput_proxy": throughput_proxy,
                    "workspace_norm": float(np.linalg.norm(final.workspace)),
                    "self_state_norm": float(np.linalg.norm(final.self_state)),
                    "prediction_error_norm": float(final.error_norm),
                    "selected_specialist_count": len(final.selected_specialists),
                    "resolution_level": int(final.resolution_level),
                    "next_resolution_level": int(final.next_resolution_level),
                }
            )
            schedule.append((applied_recurrent, applied_closure))
            episode_telemetry.append(telemetry)
            previous_workspace = final.workspace.copy()
        if final is None:  # pragma: no cover - fixed positive length
            raise RuntimeError("episode produced no steps")
        schedules.append(tuple(schedule))
        features.append(final.feature_vector())
        factors.append(
            (
                item.episode.context,
                item.episode.object_cue,
                item.episode.actuator_map,
            )
        )
        recurrent_values = np.asarray([pair[0] for pair in schedule], dtype=np.float64)
        closure_values = np.asarray([pair[1] for pair in schedule], dtype=np.float64)
        episode_records.append(
            {
                "seed": int(seed),
                "split": split,
                "arm": arm,
                "episode_index": episode_index,
                "episode_hash": item.digest,
                "regime": item.regime,
                "context": int(item.episode.context),
                "object": int(item.episode.object_cue),
                "actuator": int(item.episode.actuator_map),
                "schedule_source_episode_index": source_index,
                "schedule_source_episode_hash": source_hash,
                "mean_recurrent_gain": float(np.mean(recurrent_values)),
                "minimum_recurrent_gain": float(np.min(recurrent_values)),
                "maximum_recurrent_gain": float(np.max(recurrent_values)),
                "mean_closure_gain": float(np.mean(closure_values)),
                "minimum_closure_gain": float(np.min(closure_values)),
                "maximum_closure_gain": float(np.max(closure_values)),
                "mean_load": float(np.mean(item.load_profile)),
                "mean_demand": float(np.mean([value.demand for value in episode_telemetry])),
                "mean_congestion": float(
                    np.mean([value.congestion for value in episode_telemetry])
                ),
                "final_prediction_error_norm": float(final.error_norm),
            }
        )

    self_updates_after = int(agent.self_learning_updates)
    forecaster_updates_after = int(agent.observation_forecaster.learning_steps)
    frozen_audit = {
        "seed": int(seed),
        "arm": arm,
        "split": split,
        "self_model_mode": agent.self_model_mode,
        "self_updates_before": self_updates_before,
        "self_updates_after": self_updates_after,
        "self_update_delta": self_updates_after - self_updates_before,
        "forecaster_updates_before": forecaster_updates_before,
        "forecaster_updates_after": forecaster_updates_after,
        "forecaster_update_delta": forecaster_updates_after - forecaster_updates_before,
        "frozen": bool(
            agent.self_model_mode == "frozen"
            and not agent.self_model.training
            and not agent.observation_forecaster.training
            and self_updates_after == self_updates_before
            and forecaster_updates_after == forecaster_updates_before
        ),
    }
    if not frozen_audit["frozen"]:
        raise RuntimeError(f"learning changed during frozen {split} scoring for {arm}")
    return SplitRun(
        features=np.asarray(features, dtype=np.float64),
        factors=np.asarray(factors, dtype=int),
        schedules=tuple(schedules),
        telemetry_rows=telemetry_rows,
        episode_records=episode_records,
        frozen_audit=frozen_audit,
    )


def _task_label(factors: Sequence[int], task: str) -> int:
    context, object_cue, actuator = (int(value) for value in factors)
    if task == "product":
        signed = context * object_cue * actuator
    elif task == "majority":
        signed = context + object_cue + actuator
    elif task == "context_object":
        signed = context * object_cue
    elif task == "object_actuator":
        signed = object_cue * actuator
    else:  # pragma: no cover - task_names defines the supported set
        raise ValueError(f"unknown task: {task}")
    return int(signed > 0)


def _prediction_rows(
    run: SplitRun,
    probe: LatentFactorProbe,
) -> list[dict[str, Any]]:
    probabilities = probe.predict_proba(run.features)
    decoded = np.where(probabilities >= 0.5, 1, -1).astype(int)
    rows: list[dict[str, Any]] = []
    tasks = task_names()
    for index, base in enumerate(run.episode_records):
        truth_factors = run.factors[index]
        predicted_factors = decoded[index]
        row = dict(base)
        row.update(
            {
                "probability_context_positive": float(probabilities[index, 0]),
                "probability_object_positive": float(probabilities[index, 1]),
                "probability_actuator_positive": float(probabilities[index, 2]),
                "predicted_context": int(predicted_factors[0]),
                "predicted_object": int(predicted_factors[1]),
                "predicted_actuator": int(predicted_factors[2]),
                "binding_correct": int(np.array_equal(predicted_factors, truth_factors)),
            }
        )
        correct_values: list[int] = []
        for task in tasks:
            truth = _task_label(truth_factors, task)
            prediction = _task_label(predicted_factors, task)
            correct = int(truth == prediction)
            row[f"truth_{task}"] = truth
            row[f"prediction_{task}"] = prediction
            row[f"correct_{task}"] = correct
            correct_values.append(correct)
        row["mean_task_correct"] = float(np.mean(correct_values))
        rows.append(row)
    return rows


def _summarize_predictions(
    rows: Sequence[Mapping[str, Any]],
    *,
    seed: int,
    arm: str,
    split: str,
) -> dict[str, Any]:
    selected = [
        row for row in rows if int(row["seed"]) == seed and row["arm"] == arm and row["split"] == split
    ]
    if not selected:
        raise ValueError(f"no prediction rows for seed={seed}, arm={arm}, split={split}")
    tasks = task_names()
    task_accuracy = {
        task: float(np.mean([float(row[f"correct_{task}"]) for row in selected]))
        for task in tasks
    }
    factor_accuracy = {
        "context": float(
            np.mean([int(row["predicted_context"]) == int(row["context"]) for row in selected])
        ),
        "object": float(
            np.mean([int(row["predicted_object"]) == int(row["object"]) for row in selected])
        ),
        "actuator": float(
            np.mean([int(row["predicted_actuator"]) == int(row["actuator"]) for row in selected])
        ),
    }
    regime_accuracy = {
        regime: float(
            np.mean(
                [
                    float(row["mean_task_correct"])
                    for row in selected
                    if row["regime"] == regime
                ]
            )
        )
        for regime in REGIMES
    }
    recurrent = np.asarray(
        [float(row["mean_recurrent_gain"]) for row in selected], dtype=np.float64
    )
    closure = np.asarray(
        [float(row["mean_closure_gain"]) for row in selected], dtype=np.float64
    )
    return {
        "seed": int(seed),
        "arm": arm,
        "split": split,
        "episode_count": len(selected),
        "mean_task_accuracy": float(np.mean(list(task_accuracy.values()))),
        "task_accuracy": task_accuracy,
        "factor_accuracy": factor_accuracy,
        "binding_accuracy": float(
            np.mean([float(row["binding_correct"]) for row in selected])
        ),
        "regime_accuracy": regime_accuracy,
        "shifted_regime_accuracy": float(
            np.mean([regime_accuracy[regime] for regime in SHIFTED_REGIMES])
        ),
        "mean_recurrent_gain": float(np.mean(recurrent)),
        "minimum_episode_mean_recurrent_gain": float(np.min(recurrent)),
        "maximum_episode_mean_recurrent_gain": float(np.max(recurrent)),
        "mean_closure_gain": float(np.mean(closure)),
    }


def _bootstrap_mean(
    values: Sequence[float],
    *,
    resamples: int,
    seed: int,
) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError("bootstrap values must be a nonempty finite vector")
    resamples = _exact_integer(resamples, "bootstrap_resamples")
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, vector.size, size=(resamples, vector.size))
    means = np.mean(vector[draws], axis=1)
    lower, upper = np.quantile(means, (0.025, 0.975))
    return {
        "mean": float(np.mean(vector)),
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
        "seed_count": int(vector.size),
        "strictly_positive_seeds": int(np.sum(vector > 0.0)),
        "values": [float(value) for value in vector],
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path.name}")
    fieldnames: list[str] = []
    known: set[str] = set()
    for row in rows:
        for key in row:
            if key not in known:
                known.add(key)
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            serialized = {
                key: (
                    json.dumps(value, sort_keys=True, separators=(",", ":"))
                    if isinstance(value, (dict, list, tuple))
                    else value
                )
                for key, value in row.items()
            }
            writer.writerow(serialized)


def _source_hashes() -> dict[str, str]:
    project_root = Path(__file__).resolve().parents[2]
    relative_paths = (
        "src/rrct/adaptive_feedback_experiment.py",
        "src/rrct/__init__.py",
        "src/rrct/agent.py",
        "src/rrct/components.py",
        "src/rrct/dynamics.py",
        "src/rrct/feedback.py",
        "src/rrct/environment.py",
        "src/rrct/learning.py",
        "src/rrct/_version.py",
        "tests/test_v10_adaptive_feedback.py",
        "tests/test_v10_adaptive_feedback_experiment.py",
        "pyproject.toml",
    )
    release_manifest_relative = "src/rrct/_release_provenance.py"
    live_paths = {
        relative: project_root / relative
        for relative in (*relative_paths, release_manifest_relative)
    }
    if all(path.is_file() for path in live_paths.values()):
        return {
            relative: _sha256_file(path) for relative, path in live_paths.items()
        }

    # A wheel intentionally omits project-level tests and pyproject.toml.  Use
    # the hashes embedded at release time so an installed runner can still
    # produce a complete, explicit source receipt.  A partial source checkout
    # remains an error rather than silently claiming the release manifest.
    if (project_root / "src" / "rrct").is_dir():
        missing = sorted(
            relative for relative, path in live_paths.items() if not path.is_file()
        )
        raise FileNotFoundError(
            "incomplete source checkout; missing provenance inputs: "
            + ", ".join(missing)
        )
    if set(V0_10_DEV2_SOURCE_HASHES) != set(relative_paths):
        raise RuntimeError("installed release source manifest is incomplete")
    package_root = Path(__file__).resolve().parent
    runtime_mismatches: list[str] = []
    for relative in relative_paths:
        if not relative.startswith("src/rrct/"):
            continue
        installed_path = package_root / Path(relative).name
        observed = _sha256_file(installed_path)
        if observed != V0_10_DEV2_SOURCE_HASHES[relative]:
            runtime_mismatches.append(relative)
    if runtime_mismatches:
        raise RuntimeError(
            "installed runtime modules do not match the embedded release manifest: "
            + ", ".join(runtime_mismatches)
        )
    source_hashes = dict(V0_10_DEV2_SOURCE_HASHES)
    source_hashes[release_manifest_relative] = _sha256_file(
        package_root / "_release_provenance.py"
    )
    return source_hashes


def _source_provenance_mode() -> str:
    project_root = Path(__file__).resolve().parents[2]
    if (project_root / "src" / "rrct").is_dir():
        return "source_checkout"
    return "installed_distribution"


def _plot_results(
    path: Path,
    *,
    seed_summaries: Sequence[Mapping[str, Any]],
    telemetry_rows: Sequence[Mapping[str, Any]],
    contrasts: Sequence[Mapping[str, Any]],
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional figure dependency
        raise RuntimeError("matplotlib is required to create the development plot") from exc

    display_arms = (*ARM_ORDER, "calibration_best_static")
    labels = {
        "fixed_low": "Fixed 0.25",
        "fixed_mid": "Fixed 0.65",
        "fixed_high": "Fixed 1.05",
        "adaptive_aligned": "Adaptive aligned",
        "adaptive_shuffled": "Adaptive shuffled",
        "adaptive_no_self": "Adaptive no self",
        "calibration_best_static": "Best static",
    }
    colors = {
        "fixed_low": "#6B7280",
        "fixed_mid": "#9CA3AF",
        "fixed_high": "#D1D5DB",
        "adaptive_aligned": "#0F766E",
        "adaptive_shuffled": "#D97706",
        "adaptive_no_self": "#7C3AED",
        "calibration_best_static": "#1F2937",
    }
    figure, axes = plt.subplots(2, 2, figsize=(13.0, 8.2))

    means = []
    errors = []
    for arm in display_arms:
        values = np.asarray(
            [
                float(row["mean_task_accuracy"])
                for row in seed_summaries
                if row["arm"] == arm
            ],
            dtype=np.float64,
        )
        means.append(float(np.mean(values)))
        errors.append(
            float(np.std(values, ddof=1) / np.sqrt(values.size))
            if values.size > 1
            else 0.0
        )
    positions = np.arange(len(display_arms))
    axes[0, 0].bar(
        positions,
        means,
        yerr=errors,
        color=[colors[arm] for arm in display_arms],
        capsize=3,
    )
    axes[0, 0].set_xticks(positions, [labels[arm] for arm in display_arms], rotation=28, ha="right")
    axes[0, 0].set_ylabel("Held-out mean task accuracy")
    axes[0, 0].set_ylim(0.0, 1.0)
    axes[0, 0].set_title("External delayed-binding outcome")

    regime_positions = np.arange(len(REGIMES))
    for arm in ("fixed_low", "fixed_mid", "fixed_high", "adaptive_aligned", "adaptive_shuffled", "adaptive_no_self"):
        values = []
        for regime in REGIMES:
            values.append(
                float(
                    np.mean(
                        [
                            float(row["regime_accuracy"][regime])
                            for row in seed_summaries
                            if row["arm"] == arm
                        ]
                    )
                )
            )
        axes[0, 1].plot(
            regime_positions,
            values,
            marker="o",
            linewidth=2.0 if arm == "adaptive_aligned" else 1.1,
            color=colors[arm],
            label=labels[arm],
        )
    axes[0, 1].set_xticks(regime_positions, [name.replace("_", " ") for name in REGIMES])
    axes[0, 1].set_ylim(0.0, 1.0)
    axes[0, 1].set_ylabel("Mean task accuracy")
    axes[0, 1].set_title("Performance across load regimes")
    axes[0, 1].legend(frameon=False, fontsize=8, ncol=2)

    for arm in ("adaptive_aligned", "adaptive_shuffled", "adaptive_no_self"):
        arm_rows = [
            row
            for row in telemetry_rows
            if row["split"] == "evaluation" and row["arm"] == arm
        ]
        step_values = sorted({int(row["step"]) for row in arm_rows})
        mean_gain = [
            float(
                np.mean(
                    [
                        float(row["applied_recurrent_gain"])
                        for row in arm_rows
                        if int(row["step"]) == step
                    ]
                )
            )
            for step in step_values
        ]
        axes[1, 0].plot(
            step_values,
            mean_gain,
            linewidth=2.2 if arm == "adaptive_aligned" else 1.4,
            color=colors[arm],
            label=labels[arm],
        )
    axes[1, 0].axhline(FIXED_GAINS["fixed_mid"], color="#9CA3AF", linestyle=":", linewidth=1.0)
    axes[1, 0].set_xlabel("Step")
    axes[1, 0].set_ylabel("Applied recurrent gain")
    axes[1, 0].set_title("Frozen evaluation feedback schedules")
    axes[1, 0].legend(frameon=False, fontsize=8)

    contrast_positions = np.arange(len(contrasts))
    contrast_means = np.asarray([float(row["mean"]) for row in contrasts])
    lower = contrast_means - np.asarray([float(row["ci95_lower"]) for row in contrasts])
    upper = np.asarray([float(row["ci95_upper"]) for row in contrasts]) - contrast_means
    axes[1, 1].errorbar(
        contrast_means,
        contrast_positions,
        xerr=np.vstack((lower, upper)),
        fmt="o",
        color="#0F766E",
        ecolor="#5EEAD4",
        capsize=4,
    )
    axes[1, 1].axvline(0.0, color="#111827", linewidth=1.0)
    axes[1, 1].set_yticks(
        contrast_positions,
        [str(row["display_name"]) for row in contrasts],
    )
    axes[1, 1].set_xlabel("Paired accuracy contrast")
    axes[1, 1].set_title("Complete-seed bootstrap intervals")

    for axis in axes.ravel():
        axis.grid(alpha=0.18)
        axis.spines[["top", "right"]].set_visible(False)
    figure.suptitle("RRCT v0.10 adaptive feedback development", fontsize=15)
    figure.tight_layout()
    figure.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(figure)


def _prepare_output(path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            raise FileExistsError(f"output destination is not a directory: {path}")
        if any(path.iterdir()):
            raise FileExistsError(f"refusing nonempty output destination: {path}")
    else:
        path.mkdir(parents=True, exist_ok=False)


def run_adaptive_feedback_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = DEVELOPMENT_SEEDS,
    predictor_episode_count: int = 64,
    probe_episode_count: int = 64,
    calibration_episode_count: int = 32,
    evaluation_episode_count: int = 64,
    sequence_length: int = DEFAULT_SEQUENCE_LENGTH,
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
    schedule_seed: int = DEFAULT_SCHEDULE_SEED,
) -> dict[str, Any]:
    """Run the exploratory adaptive-feedback benchmark and write its evidence."""

    output_path = Path(output).expanduser().resolve()
    seed_values = tuple(_exact_integer(seed, "seed", minimum=0) for seed in seeds)
    if not seed_values or len(set(seed_values)) != len(seed_values):
        raise ValueError("seeds must be a nonempty sequence of unique integers")
    counts = {
        "predictor": _exact_integer(predictor_episode_count, "predictor_episode_count", minimum=8),
        "probe": _exact_integer(probe_episode_count, "probe_episode_count", minimum=8),
        "calibration": _exact_integer(calibration_episode_count, "calibration_episode_count", minimum=8),
        "evaluation": _exact_integer(evaluation_episode_count, "evaluation_episode_count", minimum=8),
    }
    sequence_length = _exact_integer(sequence_length, "sequence_length", minimum=6)
    bootstrap_resamples = _exact_integer(bootstrap_resamples, "bootstrap_resamples")
    bootstrap_seed = _exact_integer(bootstrap_seed, "bootstrap_seed", minimum=0)
    schedule_seed = _exact_integer(schedule_seed, "schedule_seed", minimum=0)
    _prepare_output(output_path)

    all_telemetry_rows: list[dict[str, Any]] = []
    all_prediction_rows: list[dict[str, Any]] = []
    frozen_audits: list[dict[str, Any]] = []
    predictor_receipts: list[dict[str, Any]] = []
    probe_audits: list[dict[str, Any]] = []
    shared_snapshot_load_audits: list[dict[str, Any]] = []
    schedule_provenance: list[dict[str, Any]] = []
    split_records: list[dict[str, Any]] = []
    calibration_selections: list[dict[str, Any]] = []
    evaluation_summaries: list[dict[str, Any]] = []

    split_offsets = {
        "predictor": 101,
        "probe": 211,
        "calibration": 307,
        "evaluation": 401,
    }
    for seed_index, seed in enumerate(seed_values):
        split_episodes = {
            split: _make_load_split(
                count,
                seed=seed * 10_007 + offset,
                split=split,
                sequence_length=sequence_length,
            )
            for split, count in counts.items()
            for offset in (split_offsets[split],)
        }
        digest_sets = {
            split: {item.digest for item in episodes}
            for split, episodes in split_episodes.items()
        }
        no_overlap = all(
            digest_sets[left].isdisjoint(digest_sets[right])
            for left_index, left in enumerate(split_episodes)
            for right in tuple(split_episodes)[left_index + 1 :]
        )
        if not no_overlap:
            raise RuntimeError("episode hashes overlap across declared splits")
        split_records.append(
            {
                "seed": seed,
                "split_digests": {
                    split: _split_digest(episodes)
                    for split, episodes in split_episodes.items()
                },
                "episode_counts": {split: len(episodes) for split, episodes in split_episodes.items()},
                "episode_hashes_disjoint": True,
            }
        )

        predictor_snapshot, forecaster_snapshot, predictor_receipt = _train_shared_predictors(
            seed, split_episodes["predictor"]
        )
        predictor_receipts.append(predictor_receipt)
        agents = {
            arm: _make_agent(
                seed,
                arm=arm,
                predictor_snapshot=predictor_snapshot,
                forecaster_snapshot=forecaster_snapshot,
            )
            for arm in ARM_ORDER
        }
        for arm, agent in agents.items():
            loaded_predictor_digest = _object_digest(agent.predictor_snapshot())
            loaded_forecaster_digest = _object_digest(
                agent.observation_forecaster_snapshot()
            )
            load_audit = {
                "seed": seed,
                "arm": arm,
                "expected_predictor_digest": predictor_receipt["predictor_digest"],
                "loaded_predictor_digest": loaded_predictor_digest,
                "expected_forecaster_digest": predictor_receipt["forecaster_digest"],
                "loaded_forecaster_digest": loaded_forecaster_digest,
                "exact_shared_snapshot_match": bool(
                    loaded_predictor_digest == predictor_receipt["predictor_digest"]
                    and loaded_forecaster_digest
                    == predictor_receipt["forecaster_digest"]
                ),
            }
            if not load_audit["exact_shared_snapshot_match"]:
                raise RuntimeError("an arm failed to load the shared predictor snapshots")
            shared_snapshot_load_audits.append(load_audit)
        probes: dict[str, LatentFactorProbe] = {}
        probe_fit_digests: dict[str, str] = {}

        def run_split_for_all(split: str) -> dict[str, SplitRun]:
            episodes = split_episodes[split]
            split_runs: dict[str, SplitRun] = {}
            # The aligned schedule must be committed before its cross-episode
            # permutation is constructed for the manual negative control.
            split_runs["adaptive_aligned"] = _run_split(
                agents["adaptive_aligned"],
                episodes,
                seed=seed,
                arm="adaptive_aligned",
                split=split,
            )
            permutation_seed = (
                schedule_seed
                + 1_000_003 * (seed_index + 1)
                + 97 * (tuple(split_episodes).index(split) + 1)
            )
            permutation = _regime_derangement(episodes, seed=permutation_seed)
            aligned_schedules = split_runs["adaptive_aligned"].schedules
            shuffled_schedules = tuple(aligned_schedules[index] for index in permutation)
            source_episode_hashes = [item.digest for item in episodes]
            target_source_hashes = [episodes[index].digest for index in permutation]
            source_schedule_digests = [
                _object_digest(schedule) for schedule in aligned_schedules
            ]
            target_schedule_digests = [
                _object_digest(schedule) for schedule in shuffled_schedules
            ]
            permutation_digest = _object_digest(
                (
                    "rrct.v010.schedule_permutation.v2",
                    seed,
                    split,
                    permutation_seed,
                    permutation,
                    tuple(source_episode_hashes),
                    tuple(target_source_hashes),
                    tuple(source_schedule_digests),
                    tuple(target_schedule_digests),
                )
            )
            schedule_provenance.append(
                {
                    "seed": seed,
                    "split": split,
                    "permutation_seed": permutation_seed,
                    "permutation": list(permutation),
                    "permutation_digest": permutation_digest,
                    "is_bijection": sorted(permutation) == list(range(len(episodes))),
                    "has_no_fixed_points": all(index != source for index, source in enumerate(permutation)),
                    "all_source_regimes_differ": all(
                        episodes[index].regime != episodes[source].regime
                        for index, source in enumerate(permutation)
                    ),
                    "source_episode_hashes": source_episode_hashes,
                    "target_to_source_episode_hashes": target_source_hashes,
                    "source_schedule_digests": source_schedule_digests,
                    "target_schedule_digests": target_schedule_digests,
                    "schedule_multiset_preserved": sorted(source_schedule_digests)
                    == sorted(target_schedule_digests),
                }
            )
            for arm in (*STATIC_ARMS, "adaptive_no_self"):
                split_runs[arm] = _run_split(
                    agents[arm],
                    episodes,
                    seed=seed,
                    arm=arm,
                    split=split,
                )
            split_runs["adaptive_shuffled"] = _run_split(
                agents["adaptive_shuffled"],
                episodes,
                seed=seed,
                arm="adaptive_shuffled",
                split=split,
                manual_schedules=shuffled_schedules,
                schedule_sources=permutation,
            )
            return split_runs

        probe_runs = run_split_for_all("probe")
        for arm in ARM_ORDER:
            run = probe_runs[arm]
            probes[arm] = LatentFactorProbe(alpha=0.02).fit(run.features, run.factors)
            probe_fit_digests[arm] = _object_digest(probes[arm])
            all_telemetry_rows.extend(run.telemetry_rows)
            frozen_audits.append(run.frozen_audit)
            all_prediction_rows.extend(_prediction_rows(run, probes[arm]))

        calibration_runs = run_split_for_all("calibration")
        for arm in ARM_ORDER:
            run = calibration_runs[arm]
            all_telemetry_rows.extend(run.telemetry_rows)
            frozen_audits.append(run.frozen_audit)
            all_prediction_rows.extend(_prediction_rows(run, probes[arm]))
            current_probe_digest = _object_digest(probes[arm])
            probe_audits.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "split": "calibration",
                    "fit_digest": probe_fit_digests[arm],
                    "post_scoring_digest": current_probe_digest,
                    "unchanged": current_probe_digest == probe_fit_digests[arm],
                }
            )
            if current_probe_digest != probe_fit_digests[arm]:
                raise RuntimeError("latent-factor probe changed during calibration")
        calibration_static = {
            arm: _summarize_predictions(
                all_prediction_rows,
                seed=seed,
                arm=arm,
                split="calibration",
            )
            for arm in STATIC_ARMS
        }
        selected_static = max(
            STATIC_ARMS,
            key=lambda arm: (
                calibration_static[arm]["mean_task_accuracy"],
                -STATIC_ARMS.index(arm),
            ),
        )
        calibration_selections.append(
            {
                "seed": seed,
                "selected_arm": selected_static,
                "selected_gain": FIXED_GAINS[selected_static],
                "tie_break_order": list(STATIC_ARMS),
                "static_mean_task_accuracy": {
                    arm: calibration_static[arm]["mean_task_accuracy"]
                    for arm in STATIC_ARMS
                },
            }
        )

        evaluation_runs = run_split_for_all("evaluation")
        for arm in ARM_ORDER:
            run = evaluation_runs[arm]
            all_telemetry_rows.extend(run.telemetry_rows)
            frozen_audits.append(run.frozen_audit)
            all_prediction_rows.extend(_prediction_rows(run, probes[arm]))
            current_probe_digest = _object_digest(probes[arm])
            probe_audits.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "split": "evaluation",
                    "fit_digest": probe_fit_digests[arm],
                    "post_scoring_digest": current_probe_digest,
                    "unchanged": current_probe_digest == probe_fit_digests[arm],
                }
            )
            if current_probe_digest != probe_fit_digests[arm]:
                raise RuntimeError("latent-factor probe changed during evaluation")
            evaluation_summaries.append(
                _summarize_predictions(
                    all_prediction_rows,
                    seed=seed,
                    arm=arm,
                    split="evaluation",
                )
            )
        selected_summary = next(
            summary
            for summary in evaluation_summaries
            if summary["seed"] == seed and summary["arm"] == selected_static
        )
        best_static_summary = pickle.loads(pickle.dumps(selected_summary, protocol=5))
        best_static_summary["arm"] = "calibration_best_static"
        best_static_summary["selected_source_arm"] = selected_static
        best_static_summary["selected_gain"] = FIXED_GAINS[selected_static]
        evaluation_summaries.append(best_static_summary)

    summary_lookup = {
        (int(row["seed"]), str(row["arm"])): row for row in evaluation_summaries
    }

    def contrast_values(
        left: str,
        right: str,
        *,
        metric: str = "mean_task_accuracy",
    ) -> list[float]:
        return [
            float(summary_lookup[(seed, left)][metric])
            - float(summary_lookup[(seed, right)][metric])
            for seed in seed_values
        ]

    contrast_specs = (
        (
            "adaptive_vs_best_static",
            "Adaptive aligned vs best static",
            "adaptive_aligned",
            "calibration_best_static",
            "mean_task_accuracy",
        ),
        (
            "adaptive_vs_shuffled",
            "Adaptive aligned vs shuffled",
            "adaptive_aligned",
            "adaptive_shuffled",
            "mean_task_accuracy",
        ),
        (
            "adaptive_vs_no_self",
            "Adaptive aligned vs no self",
            "adaptive_aligned",
            "adaptive_no_self",
            "mean_task_accuracy",
        ),
        (
            "adaptive_vs_best_static_shifted",
            "Adaptive vs best static, shifted",
            "adaptive_aligned",
            "calibration_best_static",
            "shifted_regime_accuracy",
        ),
    )
    contrasts: list[dict[str, Any]] = []
    for contrast_index, (name, display_name, left, right, metric) in enumerate(contrast_specs):
        result = _bootstrap_mean(
            contrast_values(left, right, metric=metric),
            resamples=bootstrap_resamples,
            seed=bootstrap_seed + contrast_index,
        )
        result.update(
            {
                "name": name,
                "display_name": display_name,
                "left_arm": left,
                "right_arm": right,
                "metric": metric,
            }
        )
        contrasts.append(result)
    contrast_lookup = {row["name"]: row for row in contrasts}

    expected_telemetry_rows = (
        len(seed_values)
        * len(ARM_ORDER)
        * (counts["probe"] + counts["calibration"] + counts["evaluation"])
        * sequence_length
    )
    expected_prediction_rows = (
        len(seed_values)
        * len(ARM_ORDER)
        * (counts["probe"] + counts["calibration"] + counts["evaluation"])
    )
    telemetry_keys = [
        (
            int(row["seed"]),
            str(row["split"]),
            str(row["arm"]),
            int(row["episode_index"]),
            int(row["step"]),
        )
        for row in all_telemetry_rows
    ]
    prediction_keys = [
        (
            int(row["seed"]),
            str(row["split"]),
            str(row["arm"]),
            int(row["episode_index"]),
        )
        for row in all_prediction_rows
    ]

    def numeric_rows_are_finite(rows: Sequence[Mapping[str, Any]]) -> bool:
        return all(
            np.isfinite(float(value))
            for row in rows
            for value in row.values()
            if isinstance(value, (int, float, np.integer, np.floating))
            and not isinstance(value, (bool, np.bool_))
        )

    link_groups: dict[tuple[int, str, str, int], list[Mapping[str, Any]]] = {}
    for row in all_telemetry_rows:
        if row["arm"] not in {
            *STATIC_ARMS,
            "adaptive_aligned",
            "adaptive_no_self",
        }:
            continue
        key = (
            int(row["seed"]),
            str(row["split"]),
            str(row["arm"]),
            int(row["episode_index"]),
        )
        link_groups.setdefault(key, []).append(row)
    next_step_links_valid = True
    for rows in link_groups.values():
        ordered = sorted(rows, key=lambda row: int(row["step"]))
        if len(ordered) != sequence_length:
            next_step_links_valid = False
            break
        for current_row, next_row in zip(ordered, ordered[1:]):
            if (
                float(current_row["next_recurrent_gain"])
                != float(next_row["applied_recurrent_gain"])
                or float(current_row["next_closure_gain"])
                != float(next_row["applied_closure_gain"])
            ):
                next_step_links_valid = False
                break
        if not next_step_links_valid:
            break

    telemetry_coordinate_names = tuple(FeedbackTelemetry.__dataclass_fields__)
    telemetry_bounded = all(
        0.0 <= float(row[name]) <= 1.0
        for row in all_telemetry_rows
        for name in telemetry_coordinate_names
    )
    gains_bounded = all(
        0.15 <= float(row[name]) <= 1.20
        for row in all_telemetry_rows
        for name in (
            "applied_recurrent_gain",
            "applied_closure_gain",
            "next_recurrent_gain",
            "next_closure_gain",
        )
    )
    control_diagnostics: list[dict[str, Any]] = []
    for seed in seed_values:
        for arm in ARM_ORDER:
            rows = [
                row
                for row in all_telemetry_rows
                if int(row["seed"]) == seed
                and row["split"] == "evaluation"
                and row["arm"] == arm
            ]
            recurrent = np.asarray(
                [float(row["applied_recurrent_gain"]) for row in rows]
            )
            closure = np.asarray(
                [float(row["applied_closure_gain"]) for row in rows]
            )
            control = np.asarray([float(row["control_signal"]) for row in rows])
            next_recurrent = np.asarray(
                [float(row["next_recurrent_gain"]) for row in rows]
            )

            def correlation(left: np.ndarray, right: np.ndarray) -> float | None:
                if (
                    left.size < 2
                    or float(np.std(left)) <= np.finfo(np.float64).eps
                    or float(np.std(right)) <= np.finfo(np.float64).eps
                ):
                    return None
                return float(np.corrcoef(left, right)[0, 1])

            control_diagnostics.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "evaluation_step_count": len(rows),
                    "recurrent_gain_range": float(np.ptp(recurrent)),
                    "closure_gain_range": float(np.ptp(closure)),
                    "control_to_next_recurrent_correlation": correlation(
                        control, next_recurrent
                    ),
                    "mean_bounded_integrated_throughput_proxy": float(
                        np.mean(
                            [
                                float(row["bounded_integrated_throughput_proxy"])
                                for row in rows
                            ]
                        )
                    ),
                }
            )

    official_parameter_design = bool(
        seed_values == DEVELOPMENT_SEEDS
        and counts
        == {"predictor": 64, "probe": 64, "calibration": 32, "evaluation": 64}
        and sequence_length == DEFAULT_SEQUENCE_LENGTH
        and bootstrap_resamples == DEFAULT_BOOTSTRAP_RESAMPLES
        and bootstrap_seed == DEFAULT_BOOTSTRAP_SEED
        and schedule_seed == DEFAULT_SCHEDULE_SEED
    )
    official_design = bool(
        official_parameter_design and __version__ == FROZEN_OFFICIAL_VERSION
    )
    integrity = {
        "official_development_design": official_design,
        "official_development_parameters": official_parameter_design,
        "split_hashes_disjoint": all(
            record["episode_hashes_disjoint"] for record in split_records
        ),
        "shared_predictor_snapshots_exact": all(
            record["exact_shared_snapshot_match"]
            for record in shared_snapshot_load_audits
        ),
        "probes_unchanged_after_fit": all(
            record["unchanged"] for record in probe_audits
        ),
        "telemetry_row_count_exact": len(all_telemetry_rows)
        == expected_telemetry_rows,
        "prediction_row_count_exact": len(all_prediction_rows)
        == expected_prediction_rows,
        "telemetry_rows_unique": len(set(telemetry_keys)) == len(telemetry_keys),
        "prediction_rows_unique": len(set(prediction_keys)) == len(prediction_keys),
        "all_numeric_rows_finite": numeric_rows_are_finite(all_telemetry_rows)
        and numeric_rows_are_finite(all_prediction_rows),
        "all_telemetry_coordinates_bounded": telemetry_bounded,
        "all_gains_bounded": gains_bounded,
        "all_next_step_links_valid": next_step_links_valid,
    }
    technical_integrity = bool(
        all(
            value
            for name, value in integrity.items()
            if name
            not in {
                "official_development_design",
                "official_development_parameters",
            }
        )
    )

    all_frozen = all(
        audit["frozen"]
        for audit in frozen_audits
        if audit["split"] in {"calibration", "evaluation"}
    )
    all_schedule_controls_valid = all(
        record["is_bijection"]
        and record["has_no_fixed_points"]
        and record["all_source_regimes_differ"]
        and record["schedule_multiset_preserved"]
        for record in schedule_provenance
    )
    minimum_wins = int(math.ceil(0.75 * len(seed_values)))
    gate_specification = {
        "status": "pre-outcome development gates declared in source before the substantive run",
        "minimum_mean_accuracy_gain": 0.02,
        "bootstrap_confidence": 0.95,
        "bootstrap_unit": "complete seed",
        "minimum_seed_win_fraction": 0.75,
        "minimum_seed_wins": minimum_wins,
        "shifted_regime_contrast_threshold": 0.0,
        "all_calibration_and_evaluation_learning_deltas_must_equal_zero": True,
        "shuffled_schedule_must_be_a_derangement_and_preserve_schedule_multiset": True,
        "gate_verdicts_require_the_exact_official_design": True,
    }
    best = contrast_lookup["adaptive_vs_best_static"]
    shuffled = contrast_lookup["adaptive_vs_shuffled"]
    shifted = contrast_lookup["adaptive_vs_best_static_shifted"]
    gate_results = {
        "adaptive_beats_best_static": bool(
            best["mean"] >= 0.02
            and best["ci95_lower"] > 0.0
            and best["strictly_positive_seeds"] >= minimum_wins
        ),
        "adaptive_beats_shuffled": bool(
            shuffled["mean"] >= 0.02
            and shuffled["ci95_lower"] > 0.0
            and shuffled["strictly_positive_seeds"] >= minimum_wins
        ),
        "adaptive_improves_shifted_load": bool(
            shifted["mean"] > 0.0 and shifted["ci95_lower"] > 0.0
        ),
        "all_learning_frozen": bool(all_frozen),
        "all_shuffled_schedule_controls_valid": bool(all_schedule_controls_valid),
        "all_integrity_checks_pass": technical_integrity,
        "official_development_design": official_design,
        "official_development_parameters": official_parameter_design,
    }
    gate_results["all_primary_gates_pass"] = bool(
        all(gate_results.values()) and official_design
    )

    telemetry_path = output_path / "adaptive_feedback_telemetry.csv"
    predictions_path = output_path / "adaptive_feedback_episode_predictions.csv"
    seed_summary_path = output_path / "adaptive_feedback_seed_summaries.csv"
    contrast_path = output_path / "adaptive_feedback_bootstrap_contrasts.csv"
    plot_path = output_path / "adaptive_feedback_development.png"
    _write_csv(telemetry_path, all_telemetry_rows)
    _write_csv(predictions_path, all_prediction_rows)
    flattened_seed_summaries = [
        {
            "seed": row["seed"],
            "arm": row["arm"],
            "selected_source_arm": row.get("selected_source_arm", ""),
            "selected_gain": row.get("selected_gain", ""),
            "episode_count": row["episode_count"],
            "mean_task_accuracy": row["mean_task_accuracy"],
            **{f"accuracy_{task}": row["task_accuracy"][task] for task in task_names()},
            **{f"factor_accuracy_{name}": value for name, value in row["factor_accuracy"].items()},
            "binding_accuracy": row["binding_accuracy"],
            **{f"regime_accuracy_{name}": value for name, value in row["regime_accuracy"].items()},
            "shifted_regime_accuracy": row["shifted_regime_accuracy"],
            "mean_recurrent_gain": row["mean_recurrent_gain"],
            "minimum_episode_mean_recurrent_gain": row["minimum_episode_mean_recurrent_gain"],
            "maximum_episode_mean_recurrent_gain": row["maximum_episode_mean_recurrent_gain"],
            "mean_closure_gain": row["mean_closure_gain"],
        }
        for row in evaluation_summaries
    ]
    _write_csv(seed_summary_path, flattened_seed_summaries)
    _write_csv(contrast_path, contrasts)
    _plot_results(
        plot_path,
        seed_summaries=evaluation_summaries,
        telemetry_rows=all_telemetry_rows,
        contrasts=contrasts,
    )

    source_hashes = _source_hashes()
    source_provenance_mode = _source_provenance_mode()
    summary: dict[str, Any] = {
        "schema": "rrct.adaptive_feedback_development.v0.10",
        "version": __version__,
        "status": "exploratory development only",
        "interpretation_boundary": (
            "This benchmark tests bounded functional feedback regulation and "
            "external delayed-binding accuracy. It does not create, detect, "
            "measure, or establish consciousness, sentience, valence, desire, "
            "phenomenal awareness, or moral status."
        ),
        "hypothesis": (
            "State-aligned bounded feedback improves held-out external delayed-"
            "binding performance under changing nuisance load relative to fixed "
            "gain and cross-episode schedule controls."
        ),
        "adaptive_no_self_definition": (
            "The self model remains present, but its explicit self-to-workspace "
            "feedback path is set to zero."
        ),
        "probe_definition": (
            "Each arm uses an independently fitted decoder with identical model "
            "class and capacity. This measures arm-specific representational "
            "decodability, not performance through one common decoder."
        ),
        "shuffled_control_definition": (
            "This is an offline, label-free, transductive negative control. Each "
            "target episode receives the complete aligned schedule of a distinct "
            "held-out episode from a different load regime. It preserves the exact "
            "schedule multiset but is not a deployable online policy."
        ),
        "parameters": {
            "seeds": list(seed_values),
            "fixed_gains": FIXED_GAINS,
            "arms": list(ARM_ORDER),
            "regimes": list(REGIMES),
            "sequence_length": sequence_length,
            "split_episode_counts": counts,
            "bootstrap_resamples": bootstrap_resamples,
            "bootstrap_seed": bootstrap_seed,
            "schedule_seed": schedule_seed,
        },
        "split_records": split_records,
        "predictor_receipts": predictor_receipts,
        "probe_immutability_audits": probe_audits,
        "shared_snapshot_load_audits": shared_snapshot_load_audits,
        "calibration_selections": calibration_selections,
        "schedule_permutation_provenance": schedule_provenance,
        "frozen_learning_audits": frozen_audits,
        "seed_summaries": evaluation_summaries,
        "bootstrap_contrasts": contrasts,
        "control_diagnostics": control_diagnostics,
        "integrity": integrity,
        "gate_specification": gate_specification,
        "gate_results": gate_results,
        "row_counts": {
            "telemetry": len(all_telemetry_rows),
            "episode_predictions": len(all_prediction_rows),
            "seed_summaries": len(evaluation_summaries),
            "bootstrap_contrasts": len(contrasts),
        },
        "source_hashes": source_hashes,
        "source_provenance_mode": source_provenance_mode,
        "limitations": [
            "The study is exploratory and its source-encoded gates are not an externally timestamped preregistration.",
            "Eight complete seeds still provide low-resolution seed-level uncertainty intervals.",
            "The bounded integrated-throughput value is an internal functional proxy and is not a consciousness metric.",
            "Bayesian causal-transfer evidence is deliberately disabled under adaptive feedback until active gains enter that feature schema.",
            "Artifact writes are fail-closed against overwrite but are not transactionally atomic across the entire directory.",
            "Installed-distribution runs validate packaged runtime modules against an embedded release manifest; omitted project-level tests and pyproject are covered by the separately checksummed source-and-evidence archive.",
        ],
        "artifacts": [
            telemetry_path.name,
            predictions_path.name,
            seed_summary_path.name,
            contrast_path.name,
            plot_path.name,
            "adaptive_feedback_summary.json",
            "artifact_sha256.json",
            "SHA256SUMS.txt",
        ],
    }
    summary_path = output_path / "adaptive_feedback_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    artifact_paths = (
        telemetry_path,
        predictions_path,
        seed_summary_path,
        contrast_path,
        plot_path,
        summary_path,
    )
    artifact_hashes = {path.name: _sha256_file(path) for path in artifact_paths}
    checksum_path = output_path / "SHA256SUMS.txt"
    checksum_path.write_text(
        "\n".join(
            f"{digest}  {name}" for name, digest in sorted(artifact_hashes.items())
        )
        + "\n",
        encoding="utf-8",
    )
    artifact_hashes[checksum_path.name] = _sha256_file(checksum_path)
    (output_path / "artifact_sha256.json").write_text(
        json.dumps(artifact_hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def _parse_seeds(value: str) -> tuple[int, ...]:
    try:
        seeds = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seeds must be comma-separated integers") from exc
    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return seeds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the RRCT v0.10 adaptive-feedback development benchmark."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seeds", type=_parse_seeds, default=DEVELOPMENT_SEEDS)
    parser.add_argument("--predictor-episodes", type=int, default=64)
    parser.add_argument("--probe-episodes", type=int, default=64)
    parser.add_argument("--calibration-episodes", type=int, default=32)
    parser.add_argument("--evaluation-episodes", type=int, default=64)
    parser.add_argument("--sequence-length", type=int, default=DEFAULT_SEQUENCE_LENGTH)
    parser.add_argument("--bootstrap-resamples", type=int, default=DEFAULT_BOOTSTRAP_RESAMPLES)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    parser.add_argument("--schedule-seed", type=int, default=DEFAULT_SCHEDULE_SEED)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_adaptive_feedback_experiment(
        args.output,
        seeds=args.seeds,
        predictor_episode_count=args.predictor_episodes,
        probe_episode_count=args.probe_episodes,
        calibration_episode_count=args.calibration_episodes,
        evaluation_episode_count=args.evaluation_episodes,
        sequence_length=args.sequence_length,
        bootstrap_resamples=args.bootstrap_resamples,
        bootstrap_seed=args.bootstrap_seed,
        schedule_seed=args.schedule_seed,
    )
    print(json.dumps(summary["gate_results"], sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

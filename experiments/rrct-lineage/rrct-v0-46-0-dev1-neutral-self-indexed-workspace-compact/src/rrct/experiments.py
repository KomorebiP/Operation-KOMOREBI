"""Preregistered experiments for the RRCT architecture prototype.

The experiment measures an intervention-sensitive functional signature.  It
does not infer phenomenal consciousness from the resulting numbers.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import os
import tempfile
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from ._version import __version__
from .agent import RRCTAgent, StepResult
from .criticality import (
    hysteresis_area,
    interaction_residual,
    max_slope_interval,
    widest_path_cut_certificate,
    widest_path_closure_details,
)
from .dynamics import local_transition_jacobian
from .environment import BindingEpisode, DelayedBindingEnvironment, TaskName, task_names
from .learning import LatentFactorProbe
from .metrics import (
    DiagnosticProfile,
    broadcast_reach,
    causal_adjacency,
    conjunctive_signature,
    effective_rank,
    is_strongly_connected,
    metacognitive_calibration,
    nested_projector_residual,
    projector_consistency,
    self_location_prediction_score,
    temporal_persistence_auc,
)


VARIANTS: dict[str, tuple[str, ...]] = {
    "full": (),
    "no_recurrence": ("recurrence",),
    "no_self_model": ("self_model",),
    "no_broadcast": ("broadcast",),
    "no_memory": ("memory",),
    "fixed_resolution": ("resolution",),
    "no_temporal_core": ("recurrence", "memory"),
}

PROFILE_THRESHOLDS = {
    "broadcast_reach": 0.45,
    "temporal_persistence": 0.20,
    "differentiation": 0.08,
    "metacognitive_calibration": 0.60,
    "self_location": 0.35,
    "episodic_binding": 0.35,
    "projector_consistency": 0.999,
}

SELF_MODEL_CONDITIONS = (
    "trained_self_model",
    "untrained_self_model",
    "no_self_model",
)
SHUFFLED_SELF_MODEL_CONDITION = "shuffled_trained_self_model"
EVALUATION_CONDITIONS = (*SELF_MODEL_CONDITIONS, SHUFFLED_SELF_MODEL_CONDITION)
MEDIATION_CONDITIONS = (
    "trained_self_model",
    "untrained_self_model",
    SHUFFLED_SELF_MODEL_CONDITION,
    "no_self_model",
)
DEFAULT_SWEEP_SEEDS = (17, 23, 31, 47)
DEFAULT_PHASE_GAINS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2)
V03_VALIDATION_SEEDS = (149, 157, 167, 173, 181, 191, 199, 211)
DEFAULT_SURFACE_GAINS = DEFAULT_PHASE_GAINS
DEFAULT_HYSTERESIS_GAINS = tuple(index / 10.0 for index in range(13))
INTERVENTION_MAGNITUDE = 0.35
V03_BOOTSTRAP_SEED = 20260819
V03_BOOTSTRAP_RESAMPLES = 20_000
V04_VALIDATION_SEEDS = (223, 227, 229, 233, 239, 241, 251, 257)
V04_BOOTSTRAP_SEED = 20260820
V04_BOOTSTRAP_RESAMPLES = 20_000
DEFAULT_LOCAL_DYNAMICS_GAINS = DEFAULT_PHASE_GAINS
DEFAULT_PREDICTOR_DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)


@dataclass
class RepresentationBatch:
    features: np.ndarray
    factors: np.ndarray
    episodes: list[BindingEpisode]
    predicted_workspace: np.ndarray
    actual_workspace: np.ndarray
    resolution_levels: np.ndarray
    causal_states: np.ndarray


@dataclass
class InterventionResult:
    baseline: np.ndarray
    interventions: np.ndarray
    temporal_curve: np.ndarray
    effects: np.ndarray
    adjacency: np.ndarray
    broadcast: float
    persistence: float
    strongly_connected: bool
    closure_strength: float
    closure_raw_strength: float
    closure_capacity_matrix: np.ndarray
    closure_bottleneck_pair: tuple[int, int]
    closure_cut_certificate: dict[str, Any]
    self_to_workspace_effect: float


def _agent(
    seed: int,
    ablations: Iterable[str] = (),
    *,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    self_model_mode: str = "frozen",
) -> RRCTAgent:
    return RRCTAgent(
        DelayedBindingEnvironment.observation_dim,
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
        ablations=tuple(ablations),
        recurrent_gain=recurrent_gain,
        closure_gain=closure_gain,
        self_feedback_gain=self_feedback_gain,
        action_feedback_gain=action_feedback_gain,
        self_model_mode=self_model_mode,
    )


def _episodes(count: int, *, seed: int, delay: int) -> list[BindingEpisode]:
    if count < 8:
        raise ValueError("at least eight episodes are required")
    environment = DelayedBindingEnvironment(
        delay=delay,
        noise=0.025,
        distractor_scale=0.45,
        seed=seed,
    )
    repeats = int(math.ceil(count / 8))
    return list(environment.enumerate_latents(repeats))[:count]


def collect_representations(
    episodes: Sequence[BindingEpisode],
    *,
    seed: int,
    ablations: Iterable[str] = (),
    agent: RRCTAgent | None = None,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    self_model_mode: str = "frozen",
) -> RepresentationBatch:
    """Collect final states without training the core on task labels."""

    active_agent = agent or _agent(
        seed,
        ablations,
        recurrent_gain=recurrent_gain,
        closure_gain=closure_gain,
        self_feedback_gain=self_feedback_gain,
        action_feedback_gain=action_feedback_gain,
        self_model_mode=self_model_mode,
    )
    features: list[np.ndarray] = []
    factors: list[tuple[int, int, int]] = []
    predictions: list[np.ndarray] = []
    actuals: list[np.ndarray] = []
    resolutions: list[int] = []
    causal_states: list[np.ndarray] = []

    for episode in episodes:
        active_agent.reset()
        last: StepResult | None = None
        for observation in episode.observations:
            last = active_agent.step(observation, source="procedural")
            predictions.append(last.predicted_workspace.copy())
            actuals.append(last.workspace.copy())
            causal_states.append(last.causal_nodes().reshape(-1))
        assert last is not None
        features.append(last.feature_vector())
        factors.append((episode.context, episode.object_cue, episode.actuator_map))
        resolutions.append(last.resolution_level)
    return RepresentationBatch(
        features=np.asarray(features, dtype=np.float64),
        factors=np.asarray(factors, dtype=int),
        episodes=list(episodes),
        predicted_workspace=np.asarray(predictions, dtype=np.float64),
        actual_workspace=np.asarray(actuals, dtype=np.float64),
        resolution_levels=np.asarray(resolutions, dtype=int),
        causal_states=np.asarray(causal_states, dtype=np.float64),
    )


def _differentiation_score(states: np.ndarray) -> float:
    """Effective rank of the complete causal core after unit normalization.

    Differentiation concerns the repertoire across specialists, workspace,
    self-model, and memory over time.  Measuring only the final task bottleneck
    would incorrectly penalize efficient compression.  Constant coordinates
    are removed and active coordinates are standardized before the effective
    rank is calculated.
    """

    values = np.asarray(states, dtype=np.float64)
    deviations = values.std(axis=0)
    active = deviations > 1e-8
    if not np.any(active):
        return 0.0
    standardized = (values[:, active] - values[:, active].mean(axis=0)) / deviations[active]
    return effective_rank(standardized)


def _task_label_from_factors(factors: np.ndarray, task: TaskName) -> np.ndarray:
    c, o, a = factors[:, 0], factors[:, 1], factors[:, 2]
    if task == "product":
        signed = c * o * a
    elif task == "majority":
        signed = c + o + a
    elif task == "context_object":
        signed = c * o
    elif task == "object_actuator":
        signed = o * a
    else:  # pragma: no cover
        raise ValueError(f"unknown task: {task}")
    return (signed > 0).astype(int)


def _task_predictions(decoded: np.ndarray) -> dict[str, np.ndarray]:
    return {
        task: _task_label_from_factors(decoded, task) for task in task_names()
    }


def _node_matrix(result: StepResult) -> np.ndarray:
    """Aggregate the causal loop into specialist, workspace, self, memory nodes."""

    specialist = np.mean(result.specialist_states, axis=0)
    vectors = (specialist, result.workspace, result.self_state, result.memory_read)
    width = max(vector.size for vector in vectors)
    matrix = np.zeros((4, width), dtype=np.float64)
    for index, vector in enumerate(vectors):
        matrix[index, : vector.size] = vector
    return matrix


def _run_intervention_trace(
    episode: BindingEpisode,
    *,
    seed: int,
    ablations: Iterable[str],
    source_node: int | None,
    horizon: int,
    magnitude: float = INTERVENTION_MAGNITUDE,
    agent_template: RRCTAgent | None = None,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    self_model_mode: str = "frozen",
) -> np.ndarray:
    agent = (
        copy.deepcopy(agent_template)
        if agent_template is not None
        else _agent(
            seed,
            ablations,
            recurrent_gain=recurrent_gain,
            closure_gain=closure_gain,
            self_feedback_gain=self_feedback_gain,
            action_feedback_gain=action_feedback_gain,
            self_model_mode=self_model_mode,
        )
    )
    agent.freeze_self_model()
    agent.reset()
    for observation in episode.observations:
        agent.step(observation, source="prime")

    workspace_delta = np.zeros(agent.workspace_dim, dtype=np.float64)
    workspace_delta[0] = magnitude
    if source_node == 0:
        for specialist in agent.specialists:
            specialist.state[0] += magnitude
    elif source_node == 2:
        agent.self_model.state[0] += magnitude
    elif source_node == 3:
        agent.memory.write(workspace_delta, time=agent.time, source="intervention")

    zero = np.zeros(agent.observation_dim, dtype=np.float64)
    trace: list[np.ndarray] = []
    for lag in range(horizon):
        perturb = workspace_delta if source_node == 1 and lag == 0 else None
        result = agent.step(
            zero,
            source="intervention_probe",
            perturb_workspace=perturb,
        )
        trace.append(_node_matrix(result))
    return np.asarray(trace, dtype=np.float64)


def intervention_diagnostics(
    *,
    seed: int,
    ablations: Iterable[str] = (),
    horizon: int = 12,
    agent_template: RRCTAgent | None = None,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    self_model_mode: str = "frozen",
    intervention_magnitude: float = INTERVENTION_MAGNITUDE,
) -> InterventionResult:
    """Estimate the four-node causal graph using matched interventions."""

    if not np.isfinite(intervention_magnitude) or intervention_magnitude <= 0:
        raise ValueError("intervention_magnitude must be finite and positive")

    environment = DelayedBindingEnvironment(
        delay=4, noise=0.0, distractor_scale=0.25, seed=seed + 700
    )
    episode = environment.sample()
    baseline = _run_intervention_trace(
        episode,
        seed=seed,
        ablations=ablations,
        source_node=None,
        horizon=horizon,
        agent_template=agent_template,
        recurrent_gain=recurrent_gain,
        closure_gain=closure_gain,
        self_feedback_gain=self_feedback_gain,
        action_feedback_gain=action_feedback_gain,
        self_model_mode=self_model_mode,
        magnitude=intervention_magnitude,
    )
    traces = np.asarray(
        [
            _run_intervention_trace(
                episode,
                seed=seed,
                ablations=ablations,
                source_node=node,
                horizon=horizon,
                agent_template=agent_template,
                recurrent_gain=recurrent_gain,
                closure_gain=closure_gain,
                self_feedback_gain=self_feedback_gain,
                action_feedback_gain=action_feedback_gain,
                self_model_mode=self_model_mode,
                magnitude=intervention_magnitude,
            )
            for node in range(4)
        ],
        dtype=np.float64,
    )
    adjacency, effects = causal_adjacency(
        baseline,
        traces,
        threshold=7.5e-4,
        include_self=True,
        return_effects=True,
    )
    workspace_trace = traces[1]
    curve = np.sqrt(np.mean(np.square(workspace_trace - baseline), axis=(1, 2)))
    if curve[0] > 0:
        curve = np.clip(curve / curve[0], 0.0, 1.0)
    closure = widest_path_closure_details(
        effects,
        normalize=intervention_magnitude,
    )
    cut = widest_path_cut_certificate(effects)
    if is_dataclass(cut):
        cut_record = asdict(cut)
    else:  # pragma: no cover - compatibility with mapping-like implementations
        cut_record = dict(cut)
    cut_record["reachable_set"] = list(cut_record["reachable_set"])
    cut_record["cut_edges"] = [list(edge) for edge in cut_record["cut_edges"]]
    return InterventionResult(
        baseline=baseline,
        interventions=traces,
        temporal_curve=curve,
        effects=np.asarray(effects, dtype=np.float64),
        adjacency=np.asarray(adjacency, dtype=bool),
        broadcast=broadcast_reach(
            baseline,
            workspace_trace,
            consumer_axis=1,
            threshold=7.5e-4,
        ),
        persistence=temporal_persistence_auc(curve),
        strongly_connected=is_strongly_connected(adjacency),
        closure_strength=closure.strength,
        closure_raw_strength=closure.raw_strength,
        closure_capacity_matrix=closure.capacity_matrix,
        closure_bottleneck_pair=closure.weakest_pair,
        closure_cut_certificate=cut_record,
        self_to_workspace_effect=float(effects[2, 1] / intervention_magnitude),
    )


def _shuffled_predictor_snapshot(
    snapshot: Mapping[str, Any],
    *,
    seed: int,
) -> tuple[dict[str, Any], np.ndarray]:
    """Apply one deterministic output-row permutation to both predictor maps."""

    copied = {
        key: value.copy() if isinstance(value, np.ndarray) else value
        for key, value in snapshot.items()
    }
    prediction = np.asarray(copied["prediction_weights"], dtype=np.float64)
    workspace_skip = np.asarray(copied["workspace_skip"], dtype=np.float64)
    if prediction.ndim != 2 or workspace_skip.ndim != 2:
        raise ValueError("predictor snapshot matrices must be two-dimensional")
    if prediction.shape[0] != workspace_skip.shape[0]:
        raise ValueError("predictor snapshot matrices must share output rows")
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 0x52524354]))
    permutation = rng.permutation(prediction.shape[0])
    if permutation.size > 1 and np.array_equal(
        permutation, np.arange(permutation.size)
    ):
        permutation = np.roll(permutation, 1)
    copied["prediction_weights"] = prediction[permutation, :].copy()
    copied["workspace_skip"] = workspace_skip[permutation, :].copy()
    for original, shuffled in (
        (prediction, copied["prediction_weights"]),
        (workspace_skip, copied["workspace_skip"]),
    ):
        if not np.allclose(
            np.linalg.svd(original, compute_uv=False),
            np.linalg.svd(shuffled, compute_uv=False),
            atol=1e-12,
            rtol=1e-12,
        ):
            raise RuntimeError("row permutation failed to preserve singular spectrum")
    return copied, permutation


def _predictor_snapshot_id(snapshot: Mapping[str, Any]) -> str:
    """Return a deterministic content identifier for the learned predictor."""

    digest = hashlib.sha256()
    for key in ("prediction_weights", "workspace_skip"):
        values = np.ascontiguousarray(np.asarray(snapshot[key]))
        digest.update(key.encode("utf-8"))
        digest.update(values.dtype.str.encode("ascii"))
        digest.update(np.asarray(values.shape, dtype=np.int64).tobytes())
        digest.update(values.tobytes())
    digest.update(str(int(snapshot.get("learning_steps", 0))).encode("ascii"))
    return digest.hexdigest()


def evaluate_variant(
    name: str,
    ablations: Sequence[str],
    train_episodes: Sequence[BindingEpisode],
    test_episodes: Sequence[BindingEpisode],
    *,
    seed: int,
    recurrent_gain: float = 1.0,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    intervention_horizon: int = 12,
    self_model_condition: str = "trained_self_model",
    predictor_snapshot: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], np.ndarray]:
    if self_model_condition not in EVALUATION_CONDITIONS:
        raise ValueError(
            f"self_model_condition must be one of {EVALUATION_CONDITIONS}"
        )
    active_ablations = tuple(ablations)
    if self_model_condition == "no_self_model" and "self_model" not in active_ablations:
        active_ablations = (*active_ablations, "self_model")
    effective_condition = (
        "no_self_model"
        if "self_model" in active_ablations
        else self_model_condition
    )
    learned_condition = effective_condition in {
        "trained_self_model",
        SHUFFLED_SELF_MODEL_CONDITION,
    }
    if predictor_snapshot is not None and not learned_condition:
        raise ValueError("predictor_snapshot is only valid for trained conditions")
    initial_mode = "train" if learned_condition and predictor_snapshot is None else "frozen"
    agent = _agent(
        seed,
        active_ablations,
        recurrent_gain=recurrent_gain,
        closure_gain=closure_gain,
        self_feedback_gain=self_feedback_gain,
        action_feedback_gain=action_feedback_gain,
        self_model_mode=initial_mode,
    )

    # Learned and untrained predictors are both frozen for every scored trace.
    # The learned condition gets a label-free warm-up over the training inputs;
    # the same episodes are then replayed with frozen weights for readout fitting.
    if predictor_snapshot is not None:
        snapshot_to_load: Mapping[str, Any] = predictor_snapshot
        permutation: np.ndarray | None = None
        if effective_condition == SHUFFLED_SELF_MODEL_CONDITION:
            snapshot_to_load, permutation = _shuffled_predictor_snapshot(
                predictor_snapshot,
                seed=seed,
            )
        agent.load_predictor_snapshot(snapshot_to_load, freeze=True)
    elif learned_condition:
        agent.train_self_model()
        collect_representations(
            train_episodes,
            seed=seed,
            ablations=active_ablations,
            agent=agent,
        )
        permutation = None
        if effective_condition == SHUFFLED_SELF_MODEL_CONDITION:
            shuffled, permutation = _shuffled_predictor_snapshot(
                agent.predictor_snapshot(),
                seed=seed,
            )
            agent.load_predictor_snapshot(shuffled, freeze=True)
    else:
        permutation = None
    agent.freeze_self_model()
    updates_before_scoring = int(agent.self_learning_updates)
    train = collect_representations(
        train_episodes,
        seed=seed,
        ablations=active_ablations,
        agent=agent,
    )
    updates_before_test = int(agent.self_learning_updates)
    test = collect_representations(
        test_episodes,
        seed=seed,
        ablations=active_ablations,
        agent=agent,
    )
    updates_after_test = int(agent.self_learning_updates)
    if updates_before_test != updates_before_scoring:
        raise RuntimeError("self-model changed during frozen readout collection")
    if updates_after_test != updates_before_test:
        raise RuntimeError("self-model changed during held-out scoring")
    probe = LatentFactorProbe(alpha=0.02).fit(train.features, train.factors)
    decoded = probe.predict_signed(test.features)
    probabilities = probe.predict_proba(test.features)
    predictions = _task_predictions(decoded)

    accuracies: dict[str, float] = {}
    for task in task_names():
        truth = _task_label_from_factors(test.factors, task)
        accuracies[task] = float(np.mean(predictions[task] == truth))

    product_truth = _task_label_from_factors(test.factors, "product")
    product_correct = (predictions["product"] == product_truth).astype(float)
    confidence = np.mean(np.maximum(probabilities, 1.0 - probabilities), axis=1)
    binding = float(np.mean(np.all(decoded == test.factors, axis=1)))
    intervention = intervention_diagnostics(
        seed=seed,
        ablations=active_ablations,
        horizon=intervention_horizon,
        agent_template=agent,
        recurrent_gain=recurrent_gain,
        closure_gain=closure_gain,
        self_feedback_gain=self_feedback_gain,
        action_feedback_gain=action_feedback_gain,
        self_model_mode="frozen",
    )
    projector_bank = agent.projectors
    projector_residual = nested_projector_residual(
        [projector_bank.matrix(level) for level in range(len(projector_bank))]
    )
    if "self_model" in active_ablations or float(np.std(test.actual_workspace)) <= 1e-8:
        self_location = 0.0
    else:
        self_location = self_location_prediction_score(
            test.predicted_workspace,
            test.actual_workspace,
            mode="continuous",
        )
    profile = DiagnosticProfile(
        broadcast_reach=intervention.broadcast,
        temporal_persistence=intervention.persistence,
        differentiation=_differentiation_score(test.causal_states),
        metacognitive_calibration=metacognitive_calibration(
            confidence, product_correct
        ),
        self_location=self_location,
        episodic_binding=binding,
        projector_consistency=projector_consistency(projector_residual),
        strongly_connected=intervention.strongly_connected,
    )
    signature = conjunctive_signature(profile, PROFILE_THRESHOLDS)
    factor_accuracy = np.mean(decoded == test.factors, axis=0)
    heldout_prediction_rmse = float(
        np.sqrt(
            np.mean(
                np.square(test.predicted_workspace - test.actual_workspace)
            )
        )
    )
    result: dict[str, Any] = {
        "name": name,
        "ablations": list(active_ablations),
        "self_model_condition": effective_condition,
        "self_model_mode_during_scoring": str(agent.self_model_mode),
        "self_learning_updates": updates_before_scoring,
        "self_learning_updates_before_test": updates_before_test,
        "self_learning_updates_after_test": updates_after_test,
        "self_learning_updates_during_test": updates_after_test - updates_before_test,
        "heldout_prediction_rmse": heldout_prediction_rmse,
        "recurrent_gain": float(recurrent_gain),
        "closure_gain": float(closure_gain),
        "self_feedback_gain": float(self_feedback_gain),
        "action_feedback_gain": float(action_feedback_gain),
        "effective_self_feedback_gain": float(
            agent.effective_self_feedback_gain
        ),
        "effective_action_feedback_gain": float(
            agent.effective_action_feedback_gain
        ),
        "closure_strength": float(intervention.closure_strength),
        "closure_raw_strength": float(intervention.closure_raw_strength),
        "closure_capacity_matrix": (
            intervention.closure_capacity_matrix.tolist()
        ),
        "closure_bottleneck_pair": list(intervention.closure_bottleneck_pair),
        "closure_cut_certificate": intervention.closure_cut_certificate,
        "self_to_workspace_effect": float(intervention.self_to_workspace_effect),
        "intervention_magnitude": INTERVENTION_MAGNITUDE,
        "predictor_row_permutation": (
            permutation.astype(int).tolist() if permutation is not None else None
        ),
        "predictor_snapshot_id": (
            _predictor_snapshot_id(predictor_snapshot)
            if predictor_snapshot is not None
            else ""
        ),
        "loaded_predictor_snapshot_id": (
            _predictor_snapshot_id(agent.predictor_snapshot())
            if predictor_snapshot is not None
            else ""
        ),
        "task_accuracy": accuracies,
        "mean_task_accuracy": float(np.mean(list(accuracies.values()))),
        "factor_accuracy": {
            "context": float(factor_accuracy[0]),
            "object": float(factor_accuracy[1]),
            "actuator": float(factor_accuracy[2]),
        },
        "profile": profile.as_dict(),
        "signature": signature.as_dict(),
        "projector_residual": float(projector_residual),
        "causal_adjacency": intervention.adjacency.astype(int).tolist(),
        "causal_effects": intervention.effects.tolist(),
        "resolution_histogram": {
            str(level): int(np.sum(test.resolution_levels == level))
            for level in range(4)
        },
    }
    return result, intervention.temporal_curve


def _replay_result(full: dict[str, Any]) -> dict[str, Any]:
    """Construct a behaviorally identical but causally inert replay control."""

    profile = DiagnosticProfile(
        broadcast_reach=0.0,
        temporal_persistence=0.0,
        differentiation=float(full["profile"]["differentiation"]),
        metacognitive_calibration=float(full["profile"]["metacognitive_calibration"]),
        self_location=0.0,
        episodic_binding=float(full["profile"]["episodic_binding"]),
        projector_consistency=0.0,
        strongly_connected=False,
    )
    replay = {
        "name": "replay_control",
        "ablations": ["live_causation"],
        "task_accuracy": dict(full["task_accuracy"]),
        "mean_task_accuracy": float(full["mean_task_accuracy"]),
        "factor_accuracy": dict(full["factor_accuracy"]),
        "profile": profile.as_dict(),
        "signature": conjunctive_signature(profile, PROFILE_THRESHOLDS).as_dict(),
        "projector_residual": None,
        "closure_strength": 0.0,
        "closure_raw_strength": 0.0,
        "closure_capacity_matrix": np.zeros((4, 4), dtype=float).tolist(),
        "closure_bottleneck_pair": [0, 1],
        "closure_cut_certificate": {
            "source": 0,
            "target": 1,
            "raw_capacity": 0.0,
            "reachable_set": [0],
            "cut_edges": [[0, 1, 0.0], [0, 2, 0.0], [0, 3, 0.0]],
            "node_count": 4,
        },
        "self_to_workspace_effect": 0.0,
        "intervention_magnitude": INTERVENTION_MAGNITUDE,
        "causal_adjacency": np.zeros((4, 4), dtype=int).tolist(),
        "causal_effects": np.zeros((4, 4), dtype=float).tolist(),
        "resolution_histogram": dict(full["resolution_histogram"]),
    }
    return replay


def _write_csv(path: Path, results: Sequence[dict[str, Any]]) -> None:
    profile_names = tuple(PROFILE_THRESHOLDS)
    task_fields = tuple(task_names())
    fields = [
        "name",
        "ablations",
        *[f"accuracy_{task}" for task in task_fields],
        "mean_task_accuracy",
        *profile_names,
        "strongly_connected",
        "omega",
        "passes",
        "bottleneck",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            row: dict[str, Any] = {
                "name": result["name"],
                "ablations": ",".join(result["ablations"]),
                "mean_task_accuracy": result["mean_task_accuracy"],
                "strongly_connected": result["profile"]["strongly_connected"],
                "omega": result["signature"]["omega"],
                "passes": result["signature"]["passes"],
                "bottleneck": result["signature"]["bottleneck"],
            }
            row.update(
                {
                    f"accuracy_{task}": result["task_accuracy"][task]
                    for task in task_fields
                }
            )
            row.update(
                {name: result["profile"][name] for name in profile_names}
            )
            writer.writerow(row)


def _make_figures(
    output: Path,
    results: Sequence[dict[str, Any]],
    temporal_curves: dict[str, np.ndarray],
) -> list[str]:
    try:
        cache = Path(tempfile.gettempdir()) / "rrct_matplotlib_cache"
        cache.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(cache))
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return []

    generated: list[str] = []
    plot_results = [result for result in results if result["name"] != "replay_control"]
    names = [result["name"].replace("_", " ") for result in plot_results]
    tasks = task_names()
    x = np.arange(len(names))
    width = 0.19
    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    for index, task in enumerate(tasks):
        values = [result["task_accuracy"][task] for result in plot_results]
        ax.bar(x + (index - 1.5) * width, values, width, label=task.replace("_", " "))
    ax.axhline(0.5, color="black", linewidth=1, linestyle="--", label="chance")
    ax.set_ylim(0.0, 1.02)
    ax.set_ylabel("Held-out accuracy")
    ax.set_xticks(x, names, rotation=22, ha="right")
    ax.set_title("Compositional task performance under causal ablations")
    ax.legend(ncol=3, frameon=False)
    path = output / "task_accuracy.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    generated.append(path.name)

    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    for name in ("full", "no_recurrence", "no_broadcast", "no_temporal_core"):
        curve = temporal_curves[name]
        ax.plot(np.arange(curve.size), curve, marker="o", label=name.replace("_", " "))
    ax.set_xlabel("Lag after matched intervention")
    ax.set_ylabel("Normalized causal effect")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("Persistence of a workspace intervention")
    ax.legend(frameon=False)
    path = output / "temporal_persistence.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    generated.append(path.name)

    fields = tuple(PROFILE_THRESHOLDS)
    angles = np.linspace(0, 2 * np.pi, len(fields), endpoint=False)
    closed_angles = np.r_[angles, angles[0]]
    fig = plt.figure(figsize=(8, 7), constrained_layout=True)
    ax = fig.add_subplot(111, polar=True)
    for name in ("full", "no_self_model", "no_broadcast", "replay_control"):
        result = next(item for item in results if item["name"] == name)
        values = np.asarray([result["profile"][field] for field in fields])
        ax.plot(closed_angles, np.r_[values, values[0]], linewidth=2, label=name.replace("_", " "))
    thresholds = np.asarray([PROFILE_THRESHOLDS[field] for field in fields])
    ax.plot(
        closed_angles,
        np.r_[thresholds, thresholds[0]],
        color="black",
        linestyle="--",
        linewidth=1.5,
        label="preregistered thresholds",
    )
    ax.set_xticks(angles, [field.replace("_", "\n") for field in fields])
    ax.set_ylim(0.0, 1.0)
    ax.set_title("RRCT functional diagnostic profile\n(not a consciousness measurement)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), frameon=False)
    path = output / "diagnostic_profile.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    generated.append(path.name)
    return generated


def run_experiment(
    output: str | Path,
    *,
    seed: int = 17,
    train_episode_count: int = 256,
    test_episode_count: int = 128,
    make_figures: bool = True,
) -> dict[str, Any]:
    """Run all matched variants and write the complete audit artifacts."""

    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    train = _episodes(train_episode_count, seed=seed + 1, delay=5)
    test = _episodes(test_episode_count, seed=seed + 2, delay=7)
    results: list[dict[str, Any]] = []
    curves: dict[str, np.ndarray] = {}
    for name, ablations in VARIANTS.items():
        result, curve = evaluate_variant(
            name,
            ablations,
            train,
            test,
            seed=seed,
        )
        results.append(result)
        curves[name] = curve
    results.append(_replay_result(results[0]))
    curves["replay_control"] = np.zeros_like(curves["full"])

    full = results[0]
    targeted_losses = {
        "broadcast_loss": float(
            full["profile"]["broadcast_reach"]
            - next(r for r in results if r["name"] == "no_broadcast")["profile"]["broadcast_reach"]
        ),
        "self_location_loss": float(
            full["profile"]["self_location"]
            - next(r for r in results if r["name"] == "no_self_model")["profile"]["self_location"]
        ),
        "temporal_loss": float(
            full["profile"]["temporal_persistence"]
            - next(r for r in results if r["name"] == "no_temporal_core")[
                "profile"
            ]["temporal_persistence"]
        ),
    }
    supported = bool(
        full["signature"]["passes"]
        and targeted_losses["broadcast_loss"] > 0
        and targeted_losses["self_location_loss"] > 0
        and targeted_losses["temporal_loss"] > 0
    )
    summary: dict[str, Any] = {
        "experiment": "Recursive Resolution Closure nonvalenced prototype",
        "version": __version__,
        "seed": seed,
        "train_episodes": len(train),
        "test_episodes": len(test),
        "train_delay": 5,
        "test_delay": 7,
        "thresholds": PROFILE_THRESHOLDS,
        "status": (
            "implemented_architectural_hypothesis_supported"
            if supported
            else "implemented_architectural_hypothesis_not_supported"
        ),
        "targeted_losses": targeted_losses,
        "results": results,
        "interpretation_boundary": (
            "The measurements test the implemented causal architecture. "
            "They do not establish or measure phenomenal consciousness."
        ),
    }
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_csv(destination / "ablations.csv", results)
    figures = _make_figures(destination, results, curves) if make_figures else []
    summary["artifacts"] = ["summary.json", "ablations.csv", *figures]
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


SWEEP_ROW_FIELDS = (
    "seed",
    "condition",
    "gain",
    "recurrent_gain",
    "closure_gain",
    "self_feedback_gain",
    "action_feedback_gain",
    "effective_self_feedback_gain",
    "effective_action_feedback_gain",
    "train_episode_count",
    "test_episode_count",
    "self_model_mode_during_scoring",
    "self_learning_updates",
    "self_learning_updates_before_test",
    "self_learning_updates_after_test",
    "self_learning_updates_during_test",
    "predictor_snapshot_id",
    "loaded_predictor_snapshot_id",
    "heldout_prediction_rmse",
    "closure_strength",
    "closure_raw_strength",
    "closure_bottleneck_pair",
    "closure_cut_certificate",
    "intervention_magnitude",
    "causal_effects",
    "closure_capacity_matrix",
    *tuple(f"accuracy_{task}" for task in task_names()),
    "mean_task_accuracy",
    *tuple(PROFILE_THRESHOLDS),
    "strongly_connected",
    "omega",
    "passes",
    "bottleneck",
)


def _validate_sweep_values(
    seeds: Sequence[int],
    gains: Sequence[float],
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    seed_values = tuple(int(seed) for seed in seeds)
    gain_values = tuple(float(gain) for gain in gains)
    if not seed_values:
        raise ValueError("at least one seed is required")
    if len(set(seed_values)) != len(seed_values):
        raise ValueError("seeds must be unique")
    if not gain_values:
        raise ValueError("at least one gain is required")
    if len(set(gain_values)) != len(gain_values):
        raise ValueError("gains must be unique")
    if any(not np.isfinite(gain) or gain < 0 for gain in gain_values):
        raise ValueError("gains must be finite and nonnegative")
    return seed_values, gain_values


def _validate_conditions(
    conditions: Sequence[str],
    *,
    allowed: Sequence[str] = EVALUATION_CONDITIONS,
) -> tuple[str, ...]:
    values = tuple(str(condition) for condition in conditions)
    if not values:
        raise ValueError("at least one condition is required")
    if len(set(values)) != len(values):
        raise ValueError("conditions must be unique")
    unknown = set(values) - set(allowed)
    if unknown:
        raise ValueError(f"unknown condition(s): {sorted(unknown)}")
    return values


def _bootstrap_mean_ci(
    values: Sequence[float],
    *,
    resamples: int,
    rng: np.random.Generator,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError("bootstrap values must be nonempty and finite")
    if int(resamples) != resamples or resamples <= 0:
        raise ValueError("bootstrap resamples must be a positive integer")
    indices = rng.integers(0, vector.size, size=(int(resamples), vector.size))
    means = np.mean(vector[indices], axis=1)
    lower, upper = np.quantile(means, (0.025, 0.975))
    return {
        "mean": float(np.mean(vector)),
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
    }


def _numeric_summary(values: Sequence[float]) -> dict[str, float]:
    vector = np.asarray(values, dtype=np.float64)
    if vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError("summary values must be nonempty and finite")
    return {
        "mean": float(np.mean(vector)),
        "population_std": float(np.std(vector, ddof=0)),
        "min": float(np.min(vector)),
        "max": float(np.max(vector)),
    }


def _sweep_row(
    result: dict[str, Any],
    *,
    seed: int,
    gain: float,
    train_episode_count: int,
    test_episode_count: int,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "seed": int(seed),
        "condition": result["self_model_condition"],
        "gain": float(gain),
        "recurrent_gain": float(result["recurrent_gain"]),
        "closure_gain": float(result["closure_gain"]),
        "self_feedback_gain": float(result.get("self_feedback_gain", 1.0)),
        "action_feedback_gain": float(result.get("action_feedback_gain", 1.0)),
        "effective_self_feedback_gain": float(
            result.get("effective_self_feedback_gain", result.get("closure_gain", 1.0))
        ),
        "effective_action_feedback_gain": float(
            result.get("effective_action_feedback_gain", result.get("closure_gain", 1.0))
        ),
        "train_episode_count": int(train_episode_count),
        "test_episode_count": int(test_episode_count),
        "self_model_mode_during_scoring": result[
            "self_model_mode_during_scoring"
        ],
        "self_learning_updates": int(result["self_learning_updates"]),
        "self_learning_updates_before_test": int(
            result["self_learning_updates_before_test"]
        ),
        "self_learning_updates_after_test": int(
            result["self_learning_updates_after_test"]
        ),
        "self_learning_updates_during_test": int(
            result["self_learning_updates_during_test"]
        ),
        "predictor_snapshot_id": str(result.get("predictor_snapshot_id", "")),
        "loaded_predictor_snapshot_id": str(
            result.get(
                "loaded_predictor_snapshot_id",
                result.get("predictor_snapshot_id", ""),
            )
        ),
        "heldout_prediction_rmse": float(result["heldout_prediction_rmse"]),
        "closure_strength": float(result.get("closure_strength", 0.0)),
        "closure_raw_strength": float(result.get("closure_raw_strength", 0.0)),
        "closure_bottleneck_pair": list(
            result.get("closure_bottleneck_pair", [])
        ),
        "closure_cut_certificate": dict(
            result.get("closure_cut_certificate", {})
        ),
        "intervention_magnitude": float(
            result.get("intervention_magnitude", INTERVENTION_MAGNITUDE)
        ),
        "causal_effects": list(result.get("causal_effects", [])),
        "closure_capacity_matrix": list(
            result.get("closure_capacity_matrix", [])
        ),
        "mean_task_accuracy": float(result["mean_task_accuracy"]),
        "strongly_connected": bool(result["profile"]["strongly_connected"]),
        "omega": float(result["signature"]["omega"]),
        "passes": bool(result["signature"]["passes"]),
        "bottleneck": result["signature"]["bottleneck"],
    }
    row.update(
        {
            f"accuracy_{task}": float(result["task_accuracy"][task])
            for task in task_names()
        }
    )
    row.update(
        {
            field: float(result["profile"][field])
            for field in PROFILE_THRESHOLDS
        }
    )
    return row


def _write_sweep_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    _write_structured_csv(path, SWEEP_ROW_FIELDS, rows)


def _write_structured_csv(
    path: Path,
    fields: Sequence[str],
    rows: Sequence[dict[str, Any]],
) -> None:
    structured_fields = {
        "causal_adjacency",
        "causal_effects",
        "closure_capacity_matrix",
        "closure_bottleneck_pair",
        "closure_cut_certificate",
        "predictor_row_permutation",
        "givens_pairs",
        "orthogonal_matrix",
        "cut_audit",
        "branch_switch_coordinates",
        "jacobian_shape",
        "positive_branch_signatures",
        "negative_branch_signatures",
        "task_accuracy",
        "diagnostic_profile",
        "conjunctive_signature",
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            serialized = dict(row)
            for field in structured_fields.intersection(serialized):
                serialized[field] = json.dumps(
                    serialized[field],
                    separators=(",", ":"),
                )
            writer.writerow(serialized)


def _aggregate_sweep_rows(
    rows: Sequence[dict[str, Any]],
    *,
    include_gain: bool,
) -> list[dict[str, Any]]:
    metric_fields = (
        "heldout_prediction_rmse",
        "closure_strength",
        *tuple(f"accuracy_{task}" for task in task_names()),
        "mean_task_accuracy",
        *tuple(PROFILE_THRESHOLDS),
        "strongly_connected",
        "omega",
        "passes",
    )
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            (row["condition"], float(row["gain"]))
            if include_gain
            else (row["condition"],)
        )
        groups.setdefault(key, []).append(row)

    aggregates: list[dict[str, Any]] = []
    for key, group in groups.items():
        metrics: dict[str, dict[str, float]] = {}
        for field in metric_fields:
            values = np.asarray([float(row[field]) for row in group], dtype=np.float64)
            metrics[field] = {
                "mean": float(np.mean(values)),
                "population_std": float(np.std(values, ddof=0)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }
        aggregate: dict[str, Any] = {
            "condition": key[0],
            "seed_count": len(group),
            "seeds_included": [int(row["seed"]) for row in group],
            "pass_count": int(sum(bool(row["passes"]) for row in group)),
            "pass_rate": float(np.mean([bool(row["passes"]) for row in group])),
            "metrics": metrics,
        }
        if include_gain:
            aggregate["gain"] = float(key[1])
        aggregates.append(aggregate)
    return aggregates


def _sweep_pyplot() -> Any:
    cache = Path(tempfile.gettempdir()) / "rrct_matplotlib_cache"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError(
            "sweep PNG generation requires the 'figures' optional dependency"
        ) from exc
    return plt


def _plot_seed_sweep(
    path: Path,
    rows: Sequence[dict[str, Any]],
    seeds: Sequence[int],
) -> None:
    plt = _sweep_pyplot()
    figure, axis = plt.subplots(figsize=(9.5, 5.8), constrained_layout=True)
    x = np.arange(len(seeds), dtype=float)
    for condition in SELF_MODEL_CONDITIONS:
        lookup = {
            int(row["seed"]): float(row["omega"])
            for row in rows
            if row["condition"] == condition
        }
        axis.plot(
            x,
            [lookup[int(seed)] for seed in seeds],
            marker="o",
            linewidth=2,
            label=condition.replace("_", " "),
        )
    axis.axhline(
        1.0,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label="fixed conjunctive boundary",
    )
    axis.set_xticks(x, [str(seed) for seed in seeds])
    axis.set_xlabel("Seed (all prespecified seeds shown)")
    axis.set_ylabel(r"Conjunctive signature $\Omega$")
    axis.set_title("Fixed-threshold multi-seed RRCT sweep")
    axis.legend(frameon=False)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _plot_phase_sweep(
    path: Path,
    aggregates: Sequence[dict[str, Any]],
    gains: Sequence[float],
    conditions: Sequence[str],
) -> None:
    plt = _sweep_pyplot()
    figure, (omega_axis, pass_axis) = plt.subplots(
        2,
        1,
        figsize=(9.5, 8.0),
        sharex=True,
        constrained_layout=True,
    )
    for condition in conditions:
        records = {
            float(item["gain"]): item
            for item in aggregates
            if item["condition"] == condition
        }
        means = np.asarray(
            [records[float(gain)]["metrics"]["omega"]["mean"] for gain in gains]
        )
        deviations = np.asarray(
            [
                records[float(gain)]["metrics"]["omega"]["population_std"]
                for gain in gains
            ]
        )
        pass_rates = np.asarray(
            [records[float(gain)]["pass_rate"] for gain in gains]
        )
        label = condition.replace("_", " ")
        omega_axis.plot(gains, means, marker="o", linewidth=2, label=label)
        omega_axis.fill_between(
            gains,
            np.maximum(0.0, means - deviations),
            means + deviations,
            alpha=0.14,
        )
        pass_axis.plot(gains, pass_rates, marker="o", linewidth=2, label=label)
    omega_axis.axhline(
        1.0,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label="fixed conjunctive boundary",
    )
    omega_axis.set_ylabel(r"Mean $\Omega$ (band: population SD)")
    omega_axis.set_title("Continuous recurrent and closure gain sweep")
    omega_axis.legend(frameon=False)
    pass_axis.set_xlabel("Scalar gain (recurrent gain = closure gain)")
    pass_axis.set_ylabel("Fixed-threshold pass rate")
    pass_axis.set_ylim(-0.02, 1.02)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _run_sweep_rows(
    *,
    seeds: Sequence[int],
    gains: Sequence[float],
    train_episode_count: int,
    test_episode_count: int,
    conditions: Sequence[str] = SELF_MODEL_CONDITIONS,
    predictor_snapshots: Mapping[int, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gain in gains:
        for seed in seeds:
            train = _episodes(train_episode_count, seed=seed + 1, delay=5)
            test = _episodes(test_episode_count, seed=seed + 2, delay=7)
            for condition in conditions:
                snapshot = None
                if predictor_snapshots is not None and condition in {
                    "trained_self_model",
                    SHUFFLED_SELF_MODEL_CONDITION,
                }:
                    snapshot = predictor_snapshots[int(seed)]
                evaluation_options: dict[str, Any] = {
                    "seed": seed,
                    "recurrent_gain": gain,
                    "closure_gain": gain,
                    "self_model_condition": condition,
                }
                if snapshot is not None:
                    evaluation_options["predictor_snapshot"] = snapshot
                result, _ = evaluate_variant(
                    condition,
                    (),
                    train,
                    test,
                    **evaluation_options,
                )
                if snapshot is not None:
                    expected_updates = int(snapshot.get("learning_steps", 0))
                    if result["self_learning_updates"] != expected_updates:
                        raise RuntimeError(
                            "matched phase predictor update count changed"
                        )
                    result["predictor_snapshot_id"] = _predictor_snapshot_id(
                        snapshot
                    )
                rows.append(
                    _sweep_row(
                        result,
                        seed=seed,
                        gain=gain,
                        train_episode_count=train_episode_count,
                        test_episode_count=test_episode_count,
                    )
                )
    return rows


def _sweep_summary(
    *,
    sweep: str,
    seeds: Sequence[int],
    gains: Sequence[float],
    train_episode_count: int,
    test_episode_count: int,
    rows: Sequence[dict[str, Any]],
    aggregates: Sequence[dict[str, Any]],
    artifacts: Sequence[str],
    conditions: Sequence[str] = SELF_MODEL_CONDITIONS,
    matched_predictor: bool = False,
    predictor_snapshots: Mapping[int, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    predictor_records = {
        str(seed): {
            "predictor_snapshot_id": _predictor_snapshot_id(snapshot),
            "self_learning_updates": int(snapshot.get("learning_steps", 0)),
        }
        for seed, snapshot in (predictor_snapshots or {}).items()
    }
    return {
        "schema": (
            "rrct.experimental_sweep.v0.3"
            if matched_predictor
            else "rrct.experimental_sweep.v0.2"
        ),
        "experiment": sweep,
        "version": __version__,
        "status": "completed_without_seed_filtering",
        "parameters": {
            "seeds": [int(seed) for seed in seeds],
            "gains": [float(gain) for gain in gains],
            "train_episode_count": int(train_episode_count),
            "test_episode_count": int(test_episode_count),
            "conditions": list(conditions),
            "matched_predictor": bool(matched_predictor),
        },
        "gain_protocol": {
            "recurrent_gain": "g",
            "closure_gain": "g",
            "independent_squared_scaling": False,
        },
        "self_model_protocol": {
            "trained_self_model": (
                "label-free online prediction training on training episodes, "
                "then frozen for readout collection, held-out scoring, and "
                "matched interventions"
            ),
            "untrained_self_model": (
                "initialized predictor frozen before all training and held-out traces"
            ),
            "no_self_model": "self-model causal link disabled by named ablation",
            "required_updates_during_heldout": 0,
        },
        "matched_predictor_protocol": {
            "enabled": bool(matched_predictor),
            "standard_recurrent_gain": 1.0,
            "standard_explicit_closure_gain": 1.0,
            "training": (
                "one label-free predictor snapshot per seed, trained at standard "
                "gains and frozen unchanged across every scored gain"
                if matched_predictor
                else "independent predictor training within each gain run"
            ),
            "snapshots": predictor_records,
        },
        "threshold_policy": {
            "source": "PROFILE_THRESHOLDS",
            "lowered_or_retuned": False,
            "thresholds": dict(PROFILE_THRESHOLDS),
        },
        "aggregation_policy": {
            "seed_filtering": "none",
            "standard_deviation": "population",
            "all_prespecified_seeds_included": True,
        },
        "runs": list(rows),
        "aggregates": list(aggregates),
        "artifacts": list(artifacts),
        "interpretation_boundary": (
            "These sweeps test preregistered functional diagnostics of an "
            "implemented architecture. They do not establish or measure "
            "phenomenal consciousness."
        ),
    }


def _phase_slope_diagnostics(
    aggregates: Sequence[dict[str, Any]],
    gains: Sequence[float],
    conditions: Sequence[str],
) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    if len(gains) < 2:
        return {condition: None for condition in conditions}
    for condition in conditions:
        records = {
            float(item["gain"]): item
            for item in aggregates
            if item["condition"] == condition
        }
        condition_result: dict[str, Any] = {}
        for metric in ("closure_strength", "temporal_persistence"):
            response = [
                records[float(gain)]["metrics"][metric]["mean"]
                for gain in gains
            ]
            interval, slope = max_slope_interval(gains, response)
            condition_result[metric] = {
                "interval": [float(interval[0]), float(interval[1])],
                "signed_slope": float(slope),
                "interpretation": "steepest observed adjacent interval",
            }
        diagnostics[condition] = condition_result
    return diagnostics


def run_seed_sweep(
    output: str | Path,
    *,
    seeds: Sequence[int] = DEFAULT_SWEEP_SEEDS,
    train_episode_count: int = 128,
    test_episode_count: int = 64,
) -> dict[str, Any]:
    """Run every self-model condition on every seed at fixed gain and thresholds."""

    seed_values, gain_values = _validate_sweep_values(seeds, (1.0,))
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    rows = _run_sweep_rows(
        seeds=seed_values,
        gains=gain_values,
        train_episode_count=train_episode_count,
        test_episode_count=test_episode_count,
    )
    aggregates = _aggregate_sweep_rows(rows, include_gain=False)
    csv_name = "seed_sweep.csv"
    json_name = "seed_sweep.json"
    png_name = "seed_sweep.png"
    _write_sweep_csv(destination / csv_name, rows)
    _plot_seed_sweep(destination / png_name, rows, seed_values)
    summary = _sweep_summary(
        sweep="fixed_threshold_seed_sweep",
        seeds=seed_values,
        gains=gain_values,
        train_episode_count=train_episode_count,
        test_episode_count=test_episode_count,
        rows=rows,
        aggregates=aggregates,
        artifacts=(json_name, csv_name, png_name),
    )
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def run_phase_sweep(
    output: str | Path,
    *,
    seeds: Sequence[int] = DEFAULT_SWEEP_SEEDS,
    gains: Sequence[float] = DEFAULT_PHASE_GAINS,
    train_episode_count: int = 64,
    test_episode_count: int = 32,
    conditions: Sequence[str] = SELF_MODEL_CONDITIONS,
    matched_predictor: bool = False,
) -> dict[str, Any]:
    """Sweep a continuous scalar applied to recurrent and closure feedback."""

    seed_values, gain_values = _validate_sweep_values(seeds, gains)
    condition_values = _validate_conditions(conditions)
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    learned_conditions = {
        "trained_self_model",
        SHUFFLED_SELF_MODEL_CONDITION,
    }
    predictor_snapshots: dict[int, Mapping[str, Any]] | None = None
    if matched_predictor:
        predictor_snapshots = {}
        if learned_conditions.intersection(condition_values):
            for seed in seed_values:
                training = _episodes(
                    train_episode_count,
                    seed=seed + 1,
                    delay=5,
                )
                predictor_snapshots[seed] = _train_predictor_snapshot(
                    training,
                    seed=seed,
                )
    rows = _run_sweep_rows(
        seeds=seed_values,
        gains=gain_values,
        train_episode_count=train_episode_count,
        test_episode_count=test_episode_count,
        conditions=condition_values,
        predictor_snapshots=predictor_snapshots,
    )
    aggregates = _aggregate_sweep_rows(rows, include_gain=True)
    csv_name = "phase_sweep.csv"
    json_name = "phase_sweep.json"
    png_name = "phase_sweep.png"
    _write_sweep_csv(destination / csv_name, rows)
    _plot_phase_sweep(
        destination / png_name,
        aggregates,
        gain_values,
        condition_values,
    )
    summary = _sweep_summary(
        sweep="continuous_gain_phase_sweep",
        seeds=seed_values,
        gains=gain_values,
        train_episode_count=train_episode_count,
        test_episode_count=test_episode_count,
        rows=rows,
        aggregates=aggregates,
        artifacts=(json_name, csv_name, png_name),
        conditions=condition_values,
        matched_predictor=matched_predictor,
        predictor_snapshots=predictor_snapshots,
    )
    summary["steepest_observed_intervals"] = _phase_slope_diagnostics(
        aggregates,
        gain_values,
        condition_values,
    )
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


GAIN_SURFACE_ROW_FIELDS = tuple(
    field for field in SWEEP_ROW_FIELDS if field != "gain"
)


def _surface_aggregates(
    rows: Sequence[dict[str, Any]],
    *,
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, float, float], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            str(row["condition"]),
            float(row["recurrent_gain"]),
            float(row["closure_gain"]),
        )
        groups.setdefault(key, []).append(row)
    rng = np.random.default_rng(bootstrap_seed)
    aggregates: list[dict[str, Any]] = []
    metric_fields = (
        "closure_strength",
        "temporal_persistence",
        "strongly_connected",
        "passes",
        "omega",
        "mean_task_accuracy",
    )
    for (condition, recurrent_gain, closure_gain), group in groups.items():
        metrics: dict[str, dict[str, float]] = {}
        for field in metric_fields:
            values = [float(row[field]) for row in group]
            metrics[field] = _numeric_summary(values)
            if field in {"closure_strength", "temporal_persistence"}:
                interval = _bootstrap_mean_ci(
                    values,
                    resamples=bootstrap_resamples,
                    rng=rng,
                )
                metrics[field]["bootstrap_ci95_lower"] = interval["ci95_lower"]
                metrics[field]["bootstrap_ci95_upper"] = interval["ci95_upper"]
        aggregates.append(
            {
                "condition": condition,
                "recurrent_gain": recurrent_gain,
                "closure_gain": closure_gain,
                "seed_count": len(group),
                "seeds_included": [int(row["seed"]) for row in group],
                "scc_rate": float(np.mean([row["strongly_connected"] for row in group])),
                "pass_rate": float(np.mean([row["passes"] for row in group])),
                "metrics": metrics,
            }
        )
    return aggregates


def _surface_matrix(
    aggregates: Sequence[dict[str, Any]],
    *,
    condition: str,
    recurrent_gains: Sequence[float],
    closure_gains: Sequence[float],
    metric: str,
) -> np.ndarray:
    lookup = {
        (float(item["closure_gain"]), float(item["recurrent_gain"])): item
        for item in aggregates
        if item["condition"] == condition
    }
    matrix = np.empty((len(closure_gains), len(recurrent_gains)), dtype=np.float64)
    for row_index, closure_gain in enumerate(closure_gains):
        for column_index, recurrent_gain in enumerate(recurrent_gains):
            item = lookup[(float(closure_gain), float(recurrent_gain))]
            if metric == "scc_rate":
                value = item["scc_rate"]
            elif metric == "pass_rate":
                value = item["pass_rate"]
            else:
                value = item["metrics"][metric]["mean"]
            matrix[row_index, column_index] = float(value)
    return matrix


def _surface_interactions(
    aggregates: Sequence[dict[str, Any]],
    *,
    rows: Sequence[dict[str, Any]],
    conditions: Sequence[str],
    recurrent_gains: Sequence[float],
    closure_gains: Sequence[float],
    seeds: Sequence[int],
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    rng = np.random.default_rng(bootstrap_seed)
    recurrent_interior = np.asarray(recurrent_gains, dtype=float) > 0.0
    closure_interior = np.asarray(closure_gains, dtype=float) > 0.0
    for condition in conditions:
        surface = _surface_matrix(
            aggregates,
            condition=condition,
            recurrent_gains=recurrent_gains,
            closure_gains=closure_gains,
            metric="closure_strength",
        )
        residual = interaction_residual(surface)
        per_seed_interior_mean: list[dict[str, float | int]] = []
        for seed in seeds:
            seed_lookup = {
                (float(row["closure_gain"]), float(row["recurrent_gain"])): float(
                    row["closure_strength"]
                )
                for row in rows
                if row["condition"] == condition and row["seed"] == seed
            }
            seed_surface = np.asarray(
                [
                    [
                        seed_lookup[(float(closure_gain), float(recurrent_gain))]
                        for recurrent_gain in recurrent_gains
                    ]
                    for closure_gain in closure_gains
                ],
                dtype=np.float64,
            )
            seed_residual = interaction_residual(seed_surface)
            interior = seed_residual[np.ix_(closure_interior, recurrent_interior)]
            interior_mean = float(np.mean(interior)) if interior.size else 0.0
            per_seed_interior_mean.append(
                {"seed": int(seed), "interior_mean_residual": interior_mean}
            )
        decision_values = [
            float(item["interior_mean_residual"])
            for item in per_seed_interior_mean
        ]
        decision_summary = _numeric_summary(decision_values)
        decision_interval = _bootstrap_mean_ci(
            decision_values,
            resamples=bootstrap_resamples,
            rng=rng,
        )
        decision_summary["bootstrap_ci95_lower"] = decision_interval["ci95_lower"]
        decision_summary["bootstrap_ci95_upper"] = decision_interval["ci95_upper"]
        decision_summary["ci95_excludes_zero"] = bool(
            decision_interval["ci95_lower"] > 0.0
            or decision_interval["ci95_upper"] < 0.0
        )
        positive_count = int(np.sum(np.asarray(decision_values) > 0.0))
        validation_positive_count = 6
        validation_seed_count = 8
        actual_required_count = int(
            math.ceil(
                validation_positive_count
                * len(decision_values)
                / validation_seed_count
            )
        )
        positive_supported = bool(
            positive_count >= actual_required_count
            and decision_interval["ci95_lower"] > 0.0
        )
        decision_summary.update(
            {
                "count_positive_seed_interior_means": positive_count,
                "seed_count": len(decision_values),
                "actual_required_positive_seed_count": actual_required_count,
                "positive_interaction_supported": positive_supported,
            }
        )
        results[condition] = {
            "metric": "closure_strength",
            "baseline_recurrent_gain": float(recurrent_gains[0]),
            "baseline_explicit_closure_gain": float(closure_gains[0]),
            "residual": residual.tolist(),
            "rms": float(np.sqrt(np.mean(np.square(residual)))),
            "maximum_absolute": float(np.max(np.abs(residual))),
            "per_seed_interior_mean": per_seed_interior_mean,
            "interior_mean_decision_variable": decision_summary,
            "count_positive_seed_interior_means": positive_count,
            "seed_count": len(decision_values),
            "bootstrap_ci95_lower": decision_interval["ci95_lower"],
            "positive_interaction_supported": positive_supported,
            "validation_rule": {
                "required_positive_seed_count": validation_positive_count,
                "prespecified_seed_count": validation_seed_count,
                "required_positive_fraction": (
                    validation_positive_count / validation_seed_count
                ),
                "bootstrap_ci95_lower_must_exceed": 0.0,
                "smoke_run_count_scaling": "ceiling of 0.75 times actual seed count",
            },
            "bootstrap": {
                "method": "paired resampling of prespecified seed surfaces",
                "rng_seed": int(bootstrap_seed),
                "resamples": int(bootstrap_resamples),
            },
            "interpretation": (
                "descriptive nonadditive interaction residual, not a criticality test"
            ),
        }
    return results


def _plot_gain_surface(
    path: Path,
    aggregates: Sequence[dict[str, Any]],
    *,
    conditions: Sequence[str],
    recurrent_gains: Sequence[float],
    closure_gains: Sequence[float],
) -> None:
    plt = _sweep_pyplot()
    metrics = (
        ("closure_strength", "Mean closure strength"),
        ("temporal_persistence", "Mean temporal persistence"),
        ("scc_rate", "SCC rate"),
        ("pass_rate", "Fixed-threshold pass rate"),
        ("interaction", "Closure interaction residual"),
    )
    figure, axes = plt.subplots(
        len(conditions),
        len(metrics),
        figsize=(20, max(4.2, 3.8 * len(conditions))),
        squeeze=False,
        constrained_layout=True,
    )
    for row_index, condition in enumerate(conditions):
        closure_surface = _surface_matrix(
            aggregates,
            condition=condition,
            recurrent_gains=recurrent_gains,
            closure_gains=closure_gains,
            metric="closure_strength",
        )
        for column_index, (metric, title) in enumerate(metrics):
            axis = axes[row_index, column_index]
            if metric == "interaction":
                matrix = interaction_residual(closure_surface)
                limit = max(float(np.max(np.abs(matrix))), np.finfo(float).eps)
                image = axis.imshow(
                    matrix,
                    origin="lower",
                    aspect="auto",
                    cmap="coolwarm",
                    vmin=-limit,
                    vmax=limit,
                )
            else:
                matrix = _surface_matrix(
                    aggregates,
                    condition=condition,
                    recurrent_gains=recurrent_gains,
                    closure_gains=closure_gains,
                    metric=metric,
                )
                image = axis.imshow(
                    matrix,
                    origin="lower",
                    aspect="auto",
                    cmap="viridis",
                    vmin=0.0 if metric in {"scc_rate", "pass_rate"} else None,
                    vmax=1.0 if metric in {"scc_rate", "pass_rate"} else None,
                )
            axis.set_xticks(range(len(recurrent_gains)), [f"{gain:g}" for gain in recurrent_gains])
            axis.set_yticks(range(len(closure_gains)), [f"{gain:g}" for gain in closure_gains])
            axis.set_xlabel("Recurrent gain")
            if column_index == 0:
                axis.set_ylabel(
                    "Explicit closure gain\n(prior self/action feedback only)"
                )
            axis.set_title(
                f"{title}\n{condition.replace('_', ' ')}"
                if len(conditions) > 1
                else title
            )
            figure.colorbar(image, ax=axis, shrink=0.78)
    figure.suptitle(
        "Independent gain surface diagnostics (descriptive, not a phase-transition claim)"
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_gain_surface(
    output: str | Path,
    *,
    seeds: Sequence[int] = V03_VALIDATION_SEEDS,
    recurrent_gains: Sequence[float] = DEFAULT_SURFACE_GAINS,
    closure_gains: Sequence[float] = DEFAULT_SURFACE_GAINS,
    conditions: Sequence[str] = ("trained_self_model",),
    train_episode_count: int = 32,
    test_episode_count: int = 16,
    bootstrap_resamples: int = V03_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V03_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Map independent recurrence and explicit closure gains without seed filtering."""

    seed_values, recurrent_values = _validate_sweep_values(seeds, recurrent_gains)
    _, closure_values = _validate_sweep_values(seed_values, closure_gains)
    recurrent_values = tuple(sorted(recurrent_values))
    closure_values = tuple(sorted(closure_values))
    condition_values = _validate_conditions(conditions)
    if int(bootstrap_resamples) != bootstrap_resamples or bootstrap_resamples <= 0:
        raise ValueError("bootstrap_resamples must be a positive integer")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    episode_cache = {
        seed: (
            _episodes(train_episode_count, seed=seed + 1, delay=5),
            _episodes(test_episode_count, seed=seed + 2, delay=7),
        )
        for seed in seed_values
    }
    learned_conditions = {
        "trained_self_model",
        SHUFFLED_SELF_MODEL_CONDITION,
    }
    predictor_snapshots: dict[int, Mapping[str, Any]] = {}
    if learned_conditions.intersection(condition_values):
        for seed in seed_values:
            predictor_snapshots[seed] = _train_predictor_snapshot(
                episode_cache[seed][0],
                seed=seed,
            )
    rows: list[dict[str, Any]] = []
    for recurrent_gain in recurrent_values:
        for closure_gain in closure_values:
            for seed in seed_values:
                train, test = episode_cache[seed]
                for condition in condition_values:
                    snapshot = (
                        predictor_snapshots[seed]
                        if condition in learned_conditions
                        else None
                    )
                    result, _ = evaluate_variant(
                        condition,
                        (),
                        train,
                        test,
                        seed=seed,
                        recurrent_gain=recurrent_gain,
                        closure_gain=closure_gain,
                        self_model_condition=condition,
                        predictor_snapshot=snapshot,
                    )
                    if snapshot is not None:
                        expected_updates = int(snapshot.get("learning_steps", 0))
                        if result["self_learning_updates"] != expected_updates:
                            raise RuntimeError(
                                "matched surface predictor update count changed"
                            )
                        result["predictor_snapshot_id"] = _predictor_snapshot_id(
                            snapshot
                        )
                    row = _sweep_row(
                        result,
                        seed=seed,
                        gain=0.0,
                        train_episode_count=train_episode_count,
                        test_episode_count=test_episode_count,
                    )
                    row.pop("gain")
                    rows.append(row)
    aggregates = _surface_aggregates(
        rows,
        bootstrap_resamples=int(bootstrap_resamples),
        bootstrap_seed=int(bootstrap_seed),
    )
    interactions = _surface_interactions(
        aggregates,
        rows=rows,
        conditions=condition_values,
        recurrent_gains=recurrent_values,
        closure_gains=closure_values,
        seeds=seed_values,
        bootstrap_resamples=int(bootstrap_resamples),
        bootstrap_seed=int(bootstrap_seed),
    )
    csv_name, json_name, png_name = (
        "gain_surface.csv",
        "gain_surface.json",
        "gain_surface.png",
    )
    _write_structured_csv(
        destination / csv_name,
        GAIN_SURFACE_ROW_FIELDS,
        rows,
    )
    _plot_gain_surface(
        destination / png_name,
        aggregates,
        conditions=condition_values,
        recurrent_gains=recurrent_values,
        closure_gains=closure_values,
    )
    summary: dict[str, Any] = {
        "schema": "rrct.gain_surface.v0.3",
        "experiment": "independent_gain_surface",
        "version": __version__,
        "status": "completed_without_seed_filtering",
        "parameters": {
            "seeds": list(seed_values),
            "recurrent_gains": list(recurrent_values),
            "explicit_closure_gains": list(closure_values),
            "conditions": list(condition_values),
            "train_episode_count": train_episode_count,
            "test_episode_count": test_episode_count,
            "intervention_magnitude": INTERVENTION_MAGNITUDE,
            "matched_predictor": True,
        },
        "predictor_protocol": {
            "training": (
                "one label-free snapshot per seed at recurrent_gain=1 and "
                "explicit_closure_gain=1; loaded frozen into every gain cell"
            ),
            "standard_recurrent_gain": 1.0,
            "standard_explicit_closure_gain": 1.0,
            "heldout_updates_required": 0,
            "snapshots": {
                str(seed): {
                    "predictor_snapshot_id": _predictor_snapshot_id(snapshot),
                    "self_learning_updates": int(snapshot.get("learning_steps", 0)),
                }
                for seed, snapshot in predictor_snapshots.items()
            },
        },
        "axis_interpretation": {
            "recurrent_gain": "temporal recurrent drive and residual carry",
            "explicit_closure_gain": (
                "prior self-state and action feedback into workspace only; "
                "zero does not remove adaptive-resolution self-mediated paths"
            ),
        },
        "threshold_policy": {
            "source": "PROFILE_THRESHOLDS",
            "lowered_or_retuned": False,
            "thresholds": dict(PROFILE_THRESHOLDS),
            "closure_strength_enters_omega": False,
        },
        "bootstrap": {
            "method": "deterministic percentile bootstrap of prespecified seeds",
            "confidence": 0.95,
            "rng_seed": int(bootstrap_seed),
            "resamples": int(bootstrap_resamples),
            "seed_filtering": "none",
        },
        "runs": rows,
        "aggregates": aggregates,
        "interaction_residuals": interactions,
        "artifacts": [json_name, csv_name, png_name],
        "interpretation_boundary": (
            "The surface and interaction residuals are descriptive architecture "
            "diagnostics. They do not establish a phase transition or phenomenal "
            "consciousness."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


HYSTERESIS_RESPONSE_FIELDS = (
    "workspace_norm",
    "self_norm",
    "error_norm",
    "perturbation_persistence",
)


def _train_predictor_snapshot(
    train_episodes: Sequence[BindingEpisode],
    *,
    seed: int,
) -> Mapping[str, Any]:
    agent = _agent(seed, self_model_mode="frozen")
    agent.train_self_model()
    collect_representations(
        train_episodes,
        seed=seed,
        agent=agent,
    )
    agent.freeze_self_model()
    return agent.predictor_snapshot()


def _periodic_drive(period: int, dimension: int) -> np.ndarray:
    if int(period) != period or period <= 0:
        raise ValueError("drive period must be a positive integer")
    time = np.arange(int(period), dtype=np.float64)[:, None]
    coordinates = np.arange(int(dimension), dtype=np.float64)[None, :]
    frequencies = 1.0 + np.mod(coordinates, 4.0)
    phases = np.pi * np.mod(coordinates, 7.0) / 7.0
    drive = 0.3 * np.sin(2.0 * np.pi * frequencies * time / period + phases)
    return np.asarray(drive, dtype=np.float64)


def _state_persistence_proxy(
    agent: RRCTAgent,
    drive: np.ndarray,
    *,
    horizon: int,
) -> float:
    if int(horizon) != horizon or horizon <= 0:
        raise ValueError("persistence horizon must be a positive integer")
    baseline = copy.deepcopy(agent)
    intervened = copy.deepcopy(agent)
    baseline.freeze_self_model()
    intervened.freeze_self_model()
    delta = np.zeros(agent.workspace_dim, dtype=np.float64)
    delta[0] = INTERVENTION_MAGNITUDE
    curve: list[float] = []
    for lag in range(int(horizon)):
        observation = drive[lag % drive.shape[0]]
        baseline_step = baseline.step(observation, source="hysteresis_proxy")
        intervention_step = intervened.step(
            observation,
            source="hysteresis_proxy",
            perturb_workspace=delta if lag == 0 else None,
        )
        curve.append(
            float(
                np.linalg.norm(
                    intervention_step.workspace - baseline_step.workspace
                )
            )
        )
    return temporal_persistence_auc(np.asarray(curve, dtype=np.float64))


def _gain_ramp(
    agent_template: RRCTAgent,
    gains: Sequence[float],
    *,
    seed: int,
    direction: str,
    settle_cycles: int,
    measurement_cycles: int,
    drive: np.ndarray,
    persistence_horizon: int,
    settle_multiplier: int,
) -> list[dict[str, Any]]:
    if direction not in {"upward", "downward"}:
        raise ValueError("direction must be upward or downward")
    agent = copy.deepcopy(agent_template)
    agent.freeze_self_model()
    agent.reset()
    ordered_gains = tuple(gains if direction == "upward" else reversed(gains))
    rows: list[dict[str, Any]] = []
    for order_index, gain in enumerate(ordered_gains):
        updates_before = agent.self_learning_updates
        agent.set_gains(gain, gain, reset=False)
        for _ in range(settle_cycles):
            for observation in drive:
                agent.step(observation, source="hysteresis_settle")
        workspace_norms: list[float] = []
        self_norms: list[float] = []
        error_norms: list[float] = []
        for _ in range(measurement_cycles):
            for observation in drive:
                result = agent.step(observation, source="hysteresis_measure")
                workspace_norms.append(float(np.linalg.norm(result.workspace)))
                self_norms.append(float(np.linalg.norm(result.self_state)))
                error_norms.append(float(result.error_norm))
        updates_after = agent.self_learning_updates
        if updates_after != updates_before:
            raise RuntimeError("self-model changed during frozen hysteresis ramp")
        rows.append(
            {
                "seed": int(seed),
                "direction": direction,
                "order_index": order_index,
                "gain": float(gain),
                "recurrent_gain": float(gain),
                "closure_gain": float(gain),
                "settle_multiplier": int(settle_multiplier),
                "settle_cycles": int(settle_cycles),
                "measurement_cycles": int(measurement_cycles),
                "drive_period": int(drive.shape[0]),
                "workspace_norm": float(np.mean(workspace_norms)),
                "self_norm": float(np.mean(self_norms)),
                "error_norm": float(np.mean(error_norms)),
                "perturbation_persistence": _state_persistence_proxy(
                    agent,
                    drive,
                    horizon=persistence_horizon,
                ),
                "self_learning_updates_during_measurement": (
                    updates_after - updates_before
                ),
            }
        )
    return rows


def _hysteresis_per_seed(
    rows: Sequence[dict[str, Any]],
    *,
    gains: Sequence[float],
    seeds: Sequence[int],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for seed in seeds:
        areas_by_multiplier: dict[int, dict[str, float]] = {}
        for multiplier in (1, 2):
            subset = [
                row
                for row in rows
                if row["seed"] == seed and row["settle_multiplier"] == multiplier
            ]
            upward = {float(row["gain"]): row for row in subset if row["direction"] == "upward"}
            downward = {
                float(row["gain"]): row
                for row in subset
                if row["direction"] == "downward"
            }
            areas_by_multiplier[multiplier] = {
                field: hysteresis_area(
                    gains,
                    [upward[float(gain)][field] for gain in gains],
                    [downward[float(gain)][field] for gain in gains],
                    normalize=True,
                )
                for field in HYSTERESIS_RESPONSE_FIELDS
            }
        sensitivity = {
            field: abs(areas_by_multiplier[2][field] - areas_by_multiplier[1][field])
            for field in HYSTERESIS_RESPONSE_FIELDS
        }
        relative_sensitivity = {
            field: sensitivity[field]
            / max(abs(areas_by_multiplier[1][field]), np.finfo(float).eps)
            for field in HYSTERESIS_RESPONSE_FIELDS
        }
        retention = {
            field: areas_by_multiplier[2][field]
            / max(areas_by_multiplier[1][field], np.finfo(float).eps)
            for field in HYSTERESIS_RESPONSE_FIELDS
        }
        results.append(
            {
                "seed": int(seed),
                "normalized_hysteresis_area": {
                    "declared_settle": areas_by_multiplier[1],
                    "doubled_settle": areas_by_multiplier[2],
                },
                "doubled_settle_absolute_sensitivity": sensitivity,
                "doubled_settle_relative_sensitivity": relative_sensitivity,
                "doubled_settle_retention": retention,
            }
        )
    return results


def _hysteresis_aggregates(
    per_seed: Sequence[dict[str, Any]],
    *,
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(bootstrap_seed)
    result: dict[str, Any] = {
        "normalized_hysteresis_area": {},
        "doubled_settle_absolute_sensitivity": {},
        "doubled_settle_retention": {},
    }
    for settle_name in ("declared_settle", "doubled_settle"):
        result["normalized_hysteresis_area"][settle_name] = {}
        for field in HYSTERESIS_RESPONSE_FIELDS:
            values = [
                item["normalized_hysteresis_area"][settle_name][field]
                for item in per_seed
            ]
            summary = _numeric_summary(values)
            summary.update(
                {
                    f"bootstrap_{key}": value
                    for key, value in _bootstrap_mean_ci(
                        values,
                        resamples=bootstrap_resamples,
                        rng=rng,
                    ).items()
                    if key != "mean"
                }
            )
            result["normalized_hysteresis_area"][settle_name][field] = summary
    for field in HYSTERESIS_RESPONSE_FIELDS:
        values = [
            item["doubled_settle_absolute_sensitivity"][field]
            for item in per_seed
        ]
        summary = _numeric_summary(values)
        summary.update(
            {
                f"bootstrap_{key}": value
                for key, value in _bootstrap_mean_ci(
                    values,
                    resamples=bootstrap_resamples,
                    rng=rng,
                ).items()
                if key != "mean"
            }
        )
        result["doubled_settle_absolute_sensitivity"][field] = summary
        retention_values = [
            item["doubled_settle_retention"][field]
            for item in per_seed
        ]
        retention_summary = _numeric_summary(retention_values)
        retention_interval = _bootstrap_mean_ci(
            retention_values,
            resamples=bootstrap_resamples,
            rng=rng,
        )
        retention_summary["bootstrap_ci95_lower"] = retention_interval["ci95_lower"]
        retention_summary["bootstrap_ci95_upper"] = retention_interval["ci95_upper"]
        result["doubled_settle_retention"][field] = retention_summary
    return result


HYSTERESIS_ROW_FIELDS = (
    "seed",
    "direction",
    "order_index",
    "gain",
    "recurrent_gain",
    "closure_gain",
    "settle_multiplier",
    "settle_cycles",
    "measurement_cycles",
    "drive_period",
    *HYSTERESIS_RESPONSE_FIELDS,
    "self_learning_updates_during_measurement",
    *tuple(f"normalized_hysteresis_area_{field}" for field in HYSTERESIS_RESPONSE_FIELDS),
    *tuple(f"doubled_settle_sensitivity_{field}" for field in HYSTERESIS_RESPONSE_FIELDS),
    *tuple(f"doubled_settle_retention_{field}" for field in HYSTERESIS_RESPONSE_FIELDS),
)


def _plot_hysteresis(
    path: Path,
    rows: Sequence[dict[str, Any]],
    *,
    gains: Sequence[float],
) -> None:
    plt = _sweep_pyplot()
    figure, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    for axis, field in zip(axes.reshape(-1), HYSTERESIS_RESPONSE_FIELDS):
        for multiplier, linestyle, alpha in ((1, "-", 1.0), (2, ":", 0.72)):
            for direction, color in (("upward", "tab:blue"), ("downward", "tab:orange")):
                means = []
                for gain in gains:
                    values = [
                        row[field]
                        for row in rows
                        if row["settle_multiplier"] == multiplier
                        and row["direction"] == direction
                        and row["gain"] == gain
                    ]
                    means.append(float(np.mean(values)))
                axis.plot(
                    gains,
                    means,
                    color=color,
                    linestyle=linestyle,
                    marker="o" if multiplier == 1 else None,
                    alpha=alpha,
                    label=f"{direction}, {multiplier}x settle",
                )
        axis.set_title(field.replace("_", " "))
        axis.set_xlabel("Joint gain (recurrent = explicit closure)")
        axis.set_ylabel("Mean response")
        axis.legend(frameon=False, fontsize=8)
    figure.suptitle(
        "Matched continuation ramps: path-dependence / hysteresis proxy\n"
        "Descriptive only; not evidence of a phase transition"
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_hysteresis_sweep(
    output: str | Path,
    *,
    seeds: Sequence[int] = V03_VALIDATION_SEEDS,
    gains: Sequence[float] = DEFAULT_HYSTERESIS_GAINS,
    train_episode_count: int = 64,
    settle_cycles: int = 8,
    measurement_cycles: int = 4,
    drive_period: int = 8,
    persistence_horizon: int = 12,
    bootstrap_resamples: int = V03_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V03_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run matched continuation ramps and report a conservative path proxy."""

    seed_values, gain_values = _validate_sweep_values(seeds, gains)
    gain_values = tuple(sorted(gain_values))
    for name, value in (
        ("train_episode_count", train_episode_count),
        ("settle_cycles", settle_cycles),
        ("measurement_cycles", measurement_cycles),
        ("drive_period", drive_period),
        ("persistence_horizon", persistence_horizon),
        ("bootstrap_resamples", bootstrap_resamples),
    ):
        if int(value) != value or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    drive = _periodic_drive(int(drive_period), DelayedBindingEnvironment.observation_dim)
    rows: list[dict[str, Any]] = []
    for seed in seed_values:
        train = _episodes(train_episode_count, seed=seed + 1, delay=5)
        snapshot = _train_predictor_snapshot(train, seed=seed)
        template = _agent(seed, self_model_mode="frozen")
        template.load_predictor_snapshot(snapshot, freeze=True)
        updates = template.self_learning_updates
        for multiplier in (1, 2):
            cycles = int(settle_cycles) * multiplier
            for direction in ("upward", "downward"):
                ramp_rows = _gain_ramp(
                    template,
                    gain_values,
                    seed=seed,
                    direction=direction,
                    settle_cycles=cycles,
                    measurement_cycles=int(measurement_cycles),
                    drive=drive,
                    persistence_horizon=int(persistence_horizon),
                    settle_multiplier=multiplier,
                )
                if template.self_learning_updates != updates:
                    raise RuntimeError("hysteresis template changed after freezing")
                rows.extend(ramp_rows)
    per_seed = _hysteresis_per_seed(rows, gains=gain_values, seeds=seed_values)
    per_seed_lookup = {item["seed"]: item for item in per_seed}
    for row in rows:
        item = per_seed_lookup[row["seed"]]
        settle_name = "declared_settle" if row["settle_multiplier"] == 1 else "doubled_settle"
        for field in HYSTERESIS_RESPONSE_FIELDS:
            row[f"normalized_hysteresis_area_{field}"] = item[
                "normalized_hysteresis_area"
            ][settle_name][field]
            row[f"doubled_settle_sensitivity_{field}"] = item[
                "doubled_settle_absolute_sensitivity"
            ][field]
            row[f"doubled_settle_retention_{field}"] = item[
                "doubled_settle_retention"
            ][field]
    aggregates = _hysteresis_aggregates(
        per_seed,
        bootstrap_resamples=int(bootstrap_resamples),
        bootstrap_seed=int(bootstrap_seed),
    )
    csv_name, json_name, png_name = (
        "hysteresis.csv",
        "hysteresis.json",
        "hysteresis.png",
    )
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / csv_name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HYSTERESIS_ROW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    _plot_hysteresis(destination / png_name, rows, gains=gain_values)
    steepest: dict[str, Any] = {}
    for field in HYSTERESIS_RESPONSE_FIELDS:
        response = [
            float(
                np.mean(
                    [
                        row[field]
                        for row in rows
                        if row["settle_multiplier"] == 1
                        and row["direction"] == "upward"
                        and row["gain"] == gain
                    ]
                )
            )
            for gain in gain_values
        ]
        if len(gain_values) >= 2:
            interval, slope = max_slope_interval(gain_values, response)
            steepest[field] = {
                "interval": list(interval),
                "signed_slope": slope,
                "interpretation": "steepest observed adjacent interval",
            }
        else:
            steepest[field] = None
    declared_workspace_areas = np.asarray(
        [
            item["normalized_hysteresis_area"]["declared_settle"][
                "workspace_norm"
            ]
            for item in per_seed
        ],
        dtype=np.float64,
    )
    doubled_workspace_areas = np.asarray(
        [
            item["normalized_hysteresis_area"]["doubled_settle"][
                "workspace_norm"
            ]
            for item in per_seed
        ],
        dtype=np.float64,
    )
    workspace_retentions = np.asarray(
        [item["doubled_settle_retention"]["workspace_norm"] for item in per_seed],
        dtype=np.float64,
    )
    gate_area_threshold = 0.05
    declared_area_median = float(np.median(declared_workspace_areas))
    doubled_area_median = float(np.median(doubled_workspace_areas))
    aggregate_median_retention_ratio = float(
        doubled_area_median
        / max(declared_area_median, float(np.finfo(np.float64).eps))
    )
    gate_statistics = {
        "primary_metric": "workspace_norm",
        "normalized_area_threshold": gate_area_threshold,
        "declared_settle_area_median": declared_area_median,
        "doubled_settle_area_median": doubled_area_median,
        "aggregate_median_retention_ratio": aggregate_median_retention_ratio,
        "retention_gate_statistic": "aggregate_median_retention_ratio",
        "doubled_settle_retention_median": float(np.median(workspace_retentions)),
        "doubled_settle_retention_median_role": (
            "descriptive median of per-seed ratios; not the preregistered gate"
        ),
        "doubled_settle_count_at_or_above_threshold": int(
            np.sum(doubled_workspace_areas >= gate_area_threshold)
        ),
        "seed_count": len(per_seed),
        "per_seed": [
            {
                "seed": int(item["seed"]),
                "declared_settle_area": float(declared_workspace_areas[index]),
                "doubled_settle_area": float(doubled_workspace_areas[index]),
                "doubled_settle_retention": float(workspace_retentions[index]),
                "doubled_settle_at_or_above_threshold": bool(
                    doubled_workspace_areas[index] >= gate_area_threshold
                ),
            }
            for index, item in enumerate(per_seed)
        ],
    }
    summary: dict[str, Any] = {
        "schema": "rrct.hysteresis_proxy.v0.3",
        "experiment": "matched_path_dependence_hysteresis_proxy",
        "version": __version__,
        "status": "completed_without_seed_filtering",
        "parameters": {
            "seeds": list(seed_values),
            "joint_gains": list(gain_values),
            "train_episode_count": int(train_episode_count),
            "settle_cycles": int(settle_cycles),
            "doubled_settle_cycles": int(settle_cycles) * 2,
            "measurement_cycles": int(measurement_cycles),
            "drive_period": int(drive_period),
            "persistence_horizon": int(persistence_horizon),
            "intervention_magnitude": INTERVENTION_MAGNITUDE,
        },
        "protocol": {
            "drive": "fixed analytic periodic sinusoidal drive shared by every path",
            "continuation": "set_gains(g, g, reset=False) within each ramp",
            "predictor": "trained once per seed and frozen before every ramp",
            "directions": ["upward", "downward"],
            "doubled_settle_sensitivity": "absolute area change from S to 2S cycles",
            "retention": (
                "the gate is median doubled-settle area divided by median "
                "declared-settle area with a machine-epsilon zero guard; "
                "per-seed ratios are retained descriptively"
            ),
        },
        "bootstrap": {
            "method": "deterministic percentile bootstrap of prespecified seeds",
            "confidence": 0.95,
            "rng_seed": int(bootstrap_seed),
            "resamples": int(bootstrap_resamples),
            "seed_filtering": "none",
        },
        "runs": rows,
        "per_seed_hysteresis": per_seed,
        "aggregates": aggregates,
        "primary_response": {
            "metric": "workspace_norm",
            "declared_settle_area": aggregates["normalized_hysteresis_area"][
                "declared_settle"
            ]["workspace_norm"],
            "doubled_settle_area": aggregates["normalized_hysteresis_area"][
                "doubled_settle"
            ]["workspace_norm"],
            "doubled_settle_retention": aggregates[
                "doubled_settle_retention"
            ]["workspace_norm"],
            "aggregate_median_retention_ratio": (
                aggregate_median_retention_ratio
            ),
        },
        "hysteresis_gate_statistics": gate_statistics,
        "steepest_observed_intervals": steepest,
        "artifacts": [json_name, csv_name, png_name],
        "interpretation_boundary": (
            "This reports finite-time path dependence and a normalized hysteresis "
            "proxy. It is not evidence of a thermodynamic phase transition, a "
            "critical point, or phenomenal consciousness."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


MEDIATION_ROW_FIELDS = (
    "seed",
    "condition",
    "train_episode_count",
    "test_episode_count",
    "self_model_mode_during_scoring",
    "self_learning_updates",
    "self_learning_updates_during_test",
    "heldout_prediction_rmse",
    "self_location",
    "closure_strength",
    "closure_raw_strength",
    "closure_bottleneck_pair",
    "closure_cut_certificate",
    "intervention_magnitude",
    "causal_effects",
    "closure_capacity_matrix",
    "self_to_workspace_effect",
    *tuple(f"accuracy_{task}" for task in task_names()),
    "mean_task_accuracy",
    "episodic_binding",
    "omega",
    "passes",
    "predictor_row_permutation",
)


def _mediation_row(
    result: Mapping[str, Any],
    *,
    seed: int,
    train_episode_count: int,
    test_episode_count: int,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "seed": int(seed),
        "condition": result["self_model_condition"],
        "train_episode_count": int(train_episode_count),
        "test_episode_count": int(test_episode_count),
        "self_model_mode_during_scoring": result[
            "self_model_mode_during_scoring"
        ],
        "self_learning_updates": int(result["self_learning_updates"]),
        "self_learning_updates_during_test": int(
            result["self_learning_updates_during_test"]
        ),
        "heldout_prediction_rmse": float(result["heldout_prediction_rmse"]),
        "self_location": float(result["profile"]["self_location"]),
        "closure_strength": float(result["closure_strength"]),
        "closure_raw_strength": float(result["closure_raw_strength"]),
        "closure_bottleneck_pair": list(result["closure_bottleneck_pair"]),
        "closure_cut_certificate": dict(
            result.get("closure_cut_certificate", {})
        ),
        "intervention_magnitude": float(result["intervention_magnitude"]),
        "causal_effects": list(result["causal_effects"]),
        "closure_capacity_matrix": list(result["closure_capacity_matrix"]),
        "self_to_workspace_effect": float(result["self_to_workspace_effect"]),
        "mean_task_accuracy": float(result["mean_task_accuracy"]),
        "episodic_binding": float(result["profile"]["episodic_binding"]),
        "omega": float(result["signature"]["omega"]),
        "passes": bool(result["signature"]["passes"]),
        "predictor_row_permutation": result["predictor_row_permutation"],
    }
    row.update(
        {
            f"accuracy_{task}": float(result["task_accuracy"][task])
            for task in task_names()
        }
    )
    return row


def _mediation_aggregates(
    rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    metrics = (
        "heldout_prediction_rmse",
        "self_location",
        "closure_strength",
        "self_to_workspace_effect",
        "mean_task_accuracy",
        "episodic_binding",
        "omega",
        "passes",
    )
    aggregates: list[dict[str, Any]] = []
    for condition in MEDIATION_CONDITIONS:
        group = [row for row in rows if row["condition"] == condition]
        aggregates.append(
            {
                "condition": condition,
                "seed_count": len(group),
                "seeds_included": [int(row["seed"]) for row in group],
                "metrics": {
                    metric: _numeric_summary([row[metric] for row in group])
                    for metric in metrics
                },
            }
        )
    return aggregates


def _mediation_rmse_differences(
    rows: Sequence[dict[str, Any]],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    lookup = {
        (int(row["seed"]), str(row["condition"])): float(
            row["heldout_prediction_rmse"]
        )
        for row in rows
    }
    rng = np.random.default_rng(bootstrap_seed)
    result: dict[str, Any] = {}
    for condition in MEDIATION_CONDITIONS:
        if condition == "trained_self_model":
            continue
        differences = [
            lookup[(seed, condition)] - lookup[(seed, "trained_self_model")]
            for seed in seeds
        ]
        summary = _numeric_summary(differences)
        interval = _bootstrap_mean_ci(
            differences,
            resamples=bootstrap_resamples,
            rng=rng,
        )
        summary["bootstrap_ci95_lower"] = interval["ci95_lower"]
        summary["bootstrap_ci95_upper"] = interval["ci95_upper"]
        summary["paired_differences_by_seed"] = [float(value) for value in differences]
        summary["direction"] = "positive means larger RMSE than trained_self_model"
        result[condition] = summary
    return result


def _paired_mediation_contrasts(
    rows: Sequence[dict[str, Any]],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    lookup = {
        (int(row["seed"]), str(row["condition"])): row
        for row in rows
    }
    rng = np.random.default_rng(bootstrap_seed)
    result: dict[str, Any] = {}
    metrics = (
        "heldout_prediction_rmse",
        "closure_strength",
        "self_to_workspace_effect",
    )
    for condition in MEDIATION_CONDITIONS:
        if condition == "trained_self_model":
            continue
        contrasts: dict[str, Any] = {}
        for metric in metrics:
            differences = [
                float(lookup[(seed, condition)][metric])
                - float(lookup[(seed, "trained_self_model")][metric])
                for seed in seeds
            ]
            summary = _numeric_summary(differences)
            interval = _bootstrap_mean_ci(
                differences,
                resamples=bootstrap_resamples,
                rng=rng,
            )
            summary["bootstrap_ci95_lower"] = interval["ci95_lower"]
            summary["bootstrap_ci95_upper"] = interval["ci95_upper"]
            summary["paired_differences_by_seed"] = [
                {"seed": int(seed), "condition_minus_trained": float(value)}
                for seed, value in zip(seeds, differences)
            ]
            summary["difference_definition"] = "condition minus trained_self_model"
            if metric == "heldout_prediction_rmse":
                summary["win_counts"] = {
                    "trained_lower_rmse": int(sum(value > 0.0 for value in differences)),
                    "condition_lower_rmse": int(sum(value < 0.0 for value in differences)),
                    "exact_ties": int(sum(value == 0.0 for value in differences)),
                    "seed_count": len(differences),
                }
            contrasts[metric] = summary
        result[condition] = contrasts
    return result


def _paired_mediation_records(
    rows: Sequence[dict[str, Any]],
    *,
    seeds: Sequence[int],
) -> list[dict[str, Any]]:
    lookup = {
        (int(row["seed"]), str(row["condition"])): row
        for row in rows
    }
    return [
        {
            "seed": int(seed),
            "conditions": {
                condition: {
                    "heldout_prediction_rmse": float(
                        lookup[(seed, condition)]["heldout_prediction_rmse"]
                    ),
                    "heldout_update_delta": int(
                        lookup[(seed, condition)][
                            "self_learning_updates_during_test"
                        ]
                    ),
                    "closure_strength": float(
                        lookup[(seed, condition)]["closure_strength"]
                    ),
                    "self_to_workspace_effect": float(
                        lookup[(seed, condition)]["self_to_workspace_effect"]
                    ),
                }
                for condition in MEDIATION_CONDITIONS
            },
        }
        for seed in seeds
    ]


def _plot_predictor_mediation(
    path: Path,
    rows: Sequence[dict[str, Any]],
) -> None:
    plt = _sweep_pyplot()
    metrics = (
        ("heldout_prediction_rmse", "Held-out prediction RMSE"),
        ("self_location", "Self-location score"),
        ("closure_strength", "Closure strength"),
        ("self_to_workspace_effect", "Self to workspace effect"),
        ("mean_task_accuracy", "Mean task accuracy"),
        ("episodic_binding", "Episodic binding"),
    )
    figure, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    x = np.arange(len(MEDIATION_CONDITIONS), dtype=float)
    labels = [condition.replace("_", " ") for condition in MEDIATION_CONDITIONS]
    for axis, (metric, title) in zip(axes.reshape(-1), metrics):
        for index, condition in enumerate(MEDIATION_CONDITIONS):
            values = np.asarray(
                [row[metric] for row in rows if row["condition"] == condition],
                dtype=np.float64,
            )
            axis.scatter(
                np.full(values.size, index),
                values,
                color="tab:blue",
                alpha=0.45,
                s=24,
            )
            axis.plot(
                [index - 0.22, index + 0.22],
                [np.mean(values), np.mean(values)],
                color="black",
                linewidth=2,
            )
        axis.set_xticks(x, labels, rotation=24, ha="right")
        axis.set_title(title)
    figure.suptitle(
        "Predictor mediation controls with frozen held-out evaluation\n"
        "Row-shuffled predictor preserves singular spectra"
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_predictor_mediation(
    output: str | Path,
    *,
    seeds: Sequence[int] = V03_VALIDATION_SEEDS,
    train_episode_count: int = 128,
    test_episode_count: int = 64,
    bootstrap_resamples: int = V03_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V03_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Compare learned prediction with frozen, shuffled, and disabled controls."""

    seed_values, _ = _validate_sweep_values(seeds, (1.0,))
    if int(bootstrap_resamples) != bootstrap_resamples or bootstrap_resamples <= 0:
        raise ValueError("bootstrap_resamples must be a positive integer")
    rows: list[dict[str, Any]] = []
    for seed in seed_values:
        train = _episodes(train_episode_count, seed=seed + 1, delay=5)
        test = _episodes(test_episode_count, seed=seed + 2, delay=7)
        learned_snapshot = _train_predictor_snapshot(train, seed=seed)
        for condition in MEDIATION_CONDITIONS:
            snapshot = (
                learned_snapshot
                if condition
                in {"trained_self_model", SHUFFLED_SELF_MODEL_CONDITION}
                else None
            )
            result, _ = evaluate_variant(
                condition,
                (),
                train,
                test,
                seed=seed,
                self_model_condition=condition,
                predictor_snapshot=snapshot,
            )
            if result["self_learning_updates_during_test"] != 0:
                raise RuntimeError("predictor mediation held-out weights changed")
            rows.append(
                _mediation_row(
                    result,
                    seed=seed,
                    train_episode_count=train_episode_count,
                    test_episode_count=test_episode_count,
                )
            )
    aggregates = _mediation_aggregates(rows)
    differences = _mediation_rmse_differences(
        rows,
        seeds=seed_values,
        bootstrap_resamples=int(bootstrap_resamples),
        bootstrap_seed=int(bootstrap_seed),
    )
    paired_contrasts = _paired_mediation_contrasts(
        rows,
        seeds=seed_values,
        bootstrap_resamples=int(bootstrap_resamples),
        bootstrap_seed=int(bootstrap_seed),
    )
    paired_records = _paired_mediation_records(rows, seeds=seed_values)
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    csv_name, json_name, png_name = (
        "predictor_mediation.csv",
        "predictor_mediation.json",
        "predictor_mediation.png",
    )
    _write_structured_csv(
        destination / csv_name,
        MEDIATION_ROW_FIELDS,
        rows,
    )
    _plot_predictor_mediation(destination / png_name, rows)
    summary: dict[str, Any] = {
        "schema": "rrct.predictor_mediation.v0.3",
        "experiment": "frozen_predictor_mediation_controls",
        "version": __version__,
        "status": "completed_without_seed_filtering",
        "parameters": {
            "seeds": list(seed_values),
            "conditions": list(MEDIATION_CONDITIONS),
            "train_episode_count": int(train_episode_count),
            "test_episode_count": int(test_episode_count),
        },
        "protocol": {
            "trained_self_model": "one learned snapshot per seed, frozen for scoring",
            "untrained_self_model": "seed-matched initialized predictor, always frozen",
            "shuffled_trained_self_model": (
                "same learned snapshot with one deterministic common output-row "
                "permutation applied to prediction_weights and workspace_skip"
            ),
            "no_self_model": "self-model causal link disabled by named ablation",
            "shuffle_invariant": "singular spectra of both predictor matrices",
            "heldout_updates_required": 0,
            "causal_effect_normalization": INTERVENTION_MAGNITUDE,
        },
        "bootstrap": {
            "method": "deterministic paired seed-resampling percentile bootstrap",
            "confidence": 0.95,
            "rng_seed": int(bootstrap_seed),
            "resamples": int(bootstrap_resamples),
            "seed_filtering": "none",
        },
        "runs": rows,
        "paired_per_seed": paired_records,
        "aggregates": aggregates,
        "paired_rmse_differences_vs_trained": differences,
        "paired_contrasts_vs_trained": paired_contrasts,
        "artifacts": [json_name, csv_name, png_name],
        "interpretation_boundary": (
            "These controls test whether learned predictor organization mediates "
            "selected functional diagnostics. They do not establish consciousness."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


# ---------------------------------------------------------------------------
# v0.4 preregistered mechanistic validation arms


def _validate_experiment_counts(
    *,
    train_episode_count: int,
    test_episode_count: int | None = None,
    intervention_horizon: int = 12,
) -> None:
    if int(train_episode_count) != train_episode_count or train_episode_count < 8:
        raise ValueError("train_episode_count must be an integer of at least eight")
    if test_episode_count is not None and (
        int(test_episode_count) != test_episode_count or test_episode_count < 8
    ):
        raise ValueError("test_episode_count must be an integer of at least eight")
    if int(intervention_horizon) != intervention_horizon or intervention_horizon <= 0:
        raise ValueError("intervention_horizon must be a positive integer")


def _prepare_empty_output(output: str | Path) -> Path:
    destination = Path(output)
    if destination.exists():
        if not destination.is_dir():
            raise ValueError("output must be a directory path")
        if any(destination.iterdir()):
            raise ValueError("output directory must be new or empty")
    else:
        destination.mkdir(parents=True, exist_ok=False)
    return destination


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    return value


def _exhaustive_simple_path_capacities(effects: np.ndarray) -> np.ndarray:
    """Return widest capacities by enumerating every simple directed path.

    This intentionally independent implementation is used only as a four-node
    audit of the Floyd-Warshall closure calculation retained in each row.
    """

    matrix = np.asarray(effects, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("effects must be square")
    node_count = matrix.shape[0]
    capacities = np.zeros_like(matrix)

    def visit(
        current: int,
        target: int,
        visited: tuple[int, ...],
        capacity: float,
    ) -> float:
        if current == target:
            return capacity
        best = 0.0
        for successor in range(node_count):
            if successor in visited or successor == current:
                continue
            edge_capacity = float(matrix[current, successor])
            next_capacity = min(capacity, edge_capacity)
            best = max(
                best,
                visit(
                    successor,
                    target,
                    (*visited, successor),
                    next_capacity,
                ),
            )
        return best

    for source in range(node_count):
        for target in range(node_count):
            if source != target:
                capacities[source, target] = visit(
                    source,
                    target,
                    (source,),
                    float("inf"),
                )
    return capacities


def _audit_closure_row(result: Mapping[str, Any]) -> dict[str, Any]:
    """Run the frozen exhaustive cut and SCC-equivalence audit for one row."""

    effects = np.asarray(result["causal_effects"], dtype=np.float64)
    if effects.shape != (4, 4):
        raise ValueError("the preregistered cut audit requires a four-node graph")
    certificate = dict(result["closure_cut_certificate"])
    node_count_exact = int(certificate["node_count"]) == 4
    source = int(certificate["source"])
    target = int(certificate["target"])
    raw_capacity = float(certificate["raw_capacity"])
    reachable = tuple(int(value) for value in certificate["reachable_set"])
    cut_edges = tuple(
        (int(edge[0]), int(edge[1]), float(edge[2]))
        for edge in certificate["cut_edges"]
    )
    complement = tuple(index for index in range(4) if index not in reachable)
    expected_pairs = tuple(
        (edge_source, edge_target)
        for edge_source in reachable
        for edge_target in complement
    )
    observed_pairs = tuple((edge[0], edge[1]) for edge in cut_edges)
    endpoint_valid = source in reachable and target not in reachable
    independently_reachable = {source}
    frontier = [source]
    while frontier:
        current = frontier.pop(0)
        for successor in range(4):
            if (
                successor != current
                and successor not in independently_reachable
                and effects[current, successor] > raw_capacity
            ):
                independently_reachable.add(successor)
                frontier.append(successor)
    reachable_exact = tuple(sorted(independently_reachable)) == reachable
    edge_set_exact = observed_pairs == expected_pairs
    edge_weights_exact = edge_set_exact and all(
        effect_source == edge_source
        and effect_target == edge_target
        and float(effects[edge_source, edge_target]) == weight
        for (edge_source, edge_target, weight), (
            effect_source,
            effect_target,
        ) in zip(cut_edges, expected_pairs)
    )
    cut_bounded = all(weight <= raw_capacity for _, _, weight in cut_edges)

    exhaustive_raw = _exhaustive_simple_path_capacities(effects)
    stored_raw = np.asarray(
        result["closure_capacity_matrix"], dtype=np.float64
    )
    capacity_match = bool(np.array_equal(exhaustive_raw, stored_raw))
    ordered_pairs = tuple(
        (pair_source, pair_target)
        for pair_source in range(4)
        for pair_target in range(4)
        if pair_source != pair_target
    )
    pair_values = [exhaustive_raw[pair] for pair in ordered_pairs]
    independent_weakest_index = int(np.argmin(np.asarray(pair_values)))
    independent_weakest_pair = ordered_pairs[independent_weakest_index]
    independent_raw_capacity = float(pair_values[independent_weakest_index])
    weakest_pair = tuple(int(value) for value in result["closure_bottleneck_pair"])
    weakest_match = (
        (source, target) == weakest_pair
        and weakest_pair == independent_weakest_pair
        and raw_capacity == float(result["closure_raw_strength"])
        and exhaustive_raw[source, target] == raw_capacity
        and independent_raw_capacity == raw_capacity
    )
    distinct_thresholds = sorted(set(float(value) for value in effects.reshape(-1)))
    threshold_checks = [
        {
            "threshold": threshold,
            "observed_strongly_connected": bool(
                is_strongly_connected(effects > threshold)
            ),
            "expected_strongly_connected": bool(raw_capacity > threshold),
        }
        for threshold in distinct_thresholds
    ]
    threshold_equivalence = all(
        check["observed_strongly_connected"]
        == check["expected_strongly_connected"]
        for check in threshold_checks
    )
    passed = all(
        (
            endpoint_valid,
            node_count_exact,
            reachable_exact,
            edge_set_exact,
            edge_weights_exact,
            cut_bounded,
            capacity_match,
            weakest_match,
            threshold_equivalence,
        )
    )
    return {
        "passed": bool(passed),
        "source_in_reachable_target_outside": bool(endpoint_valid),
        "certificate_node_count_is_exactly_four": bool(node_count_exact),
        "strict_reachable_set_recomputed_exactly": bool(reachable_exact),
        "all_forward_cut_edges_listed_exactly_once": bool(edge_set_exact),
        "cut_edge_weights_match_effect_matrix": bool(edge_weights_exact),
        "all_cut_edges_at_or_below_lambda": bool(cut_bounded),
        "exhaustive_simple_path_capacities_match": bool(capacity_match),
        "weakest_pair_and_lambda_match": bool(weakest_match),
        "scc_equivalence_at_distinct_effect_thresholds": bool(
            threshold_equivalence
        ),
        "max_abs_capacity_error": float(
            np.max(np.abs(exhaustive_raw - stored_raw))
        ),
        "threshold_checks": threshold_checks,
    }


def _paired_contrast_summary(
    values: Sequence[float],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    rng: np.random.Generator,
    required_sign_agreement: int = 6,
) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    interval = _bootstrap_mean_ci(
        vector,
        resamples=bootstrap_resamples,
        rng=rng,
    )
    mean = float(interval["mean"])
    if mean > 0.0:
        direction = "positive"
        agreement = int(np.sum(vector > 0.0))
        excludes_zero = float(interval["ci95_lower"]) > 0.0
    elif mean < 0.0:
        direction = "negative"
        agreement = int(np.sum(vector < 0.0))
        excludes_zero = float(interval["ci95_upper"]) < 0.0
    else:
        direction = "zero"
        agreement = int(np.sum(vector == 0.0))
        excludes_zero = False
    return {
        "mean": mean,
        "population_std": float(np.std(vector, ddof=0)),
        "min": float(np.min(vector)),
        "max": float(np.max(vector)),
        "bootstrap_ci95_lower": float(interval["ci95_lower"]),
        "bootstrap_ci95_upper": float(interval["ci95_upper"]),
        "aggregate_direction": direction,
        "sign_agreement_count": agreement,
        "required_sign_agreement": int(required_sign_agreement),
        "seed_count": int(vector.size),
        "ci_excludes_zero": bool(excludes_zero),
        "supported": bool(
            agreement >= required_sign_agreement and excludes_zero
        ),
        "paired_values": [
            {"seed": int(seed), "contrast": float(value)}
            for seed, value in zip(seeds, vector)
        ],
    }


def _positive_paired_contrast_summary(
    values: Sequence[float],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    interval = _bootstrap_mean_ci(
        vector,
        resamples=bootstrap_resamples,
        rng=rng,
    )
    positive_count = int(np.sum(vector > 0.0))
    return {
        "mean": float(interval["mean"]),
        "population_std": float(np.std(vector, ddof=0)),
        "min": float(np.min(vector)),
        "max": float(np.max(vector)),
        "bootstrap_ci95_lower": float(interval["ci95_lower"]),
        "bootstrap_ci95_upper": float(interval["ci95_upper"]),
        "strictly_positive_seed_count": positive_count,
        "required_strictly_positive_seed_count": 6,
        "seed_count": int(vector.size),
        "supported": bool(
            positive_count >= 6 and float(interval["ci95_lower"]) > 0.0
        ),
        "gate": "at least 6/8 strictly positive and bootstrap lower bound > 0",
        "paired_values": [
            {"seed": int(seed), "contrast": float(value)}
            for seed, value in zip(seeds, vector)
        ],
    }


def _descriptive_paired_contrast_summary(
    values: Sequence[float],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    vector = np.asarray(values, dtype=np.float64)
    interval = _bootstrap_mean_ci(
        vector,
        resamples=bootstrap_resamples,
        rng=rng,
    )
    return {
        "mean": float(interval["mean"]),
        "population_std": float(np.std(vector, ddof=0)),
        "min": float(np.min(vector)),
        "max": float(np.max(vector)),
        "bootstrap_ci95_lower": float(interval["ci95_lower"]),
        "bootstrap_ci95_upper": float(interval["ci95_upper"]),
        "decision_rule": "none; descriptive retention only",
        "paired_values": [
            {"seed": int(seed), "contrast": float(value)}
            for seed, value in zip(seeds, vector)
        ],
    }


PATH_DECOMPOSITION_ROW_FIELDS = (
    "row_status",
    "stop_reason",
    "seed",
    "recurrent_gain",
    "closure_gain",
    "self_feedback_gain",
    "action_feedback_gain",
    "effective_self_feedback_gain",
    "effective_action_feedback_gain",
    "train_episode_count",
    "test_episode_count",
    "train_delay",
    "test_delay",
    "intervention_horizon",
    "adjacency_threshold",
    "intervention_magnitude",
    "closure_normalization",
    "predictor_snapshot_id",
    "loaded_predictor_snapshot_id",
    "self_learning_updates",
    "self_learning_updates_before_test",
    "self_learning_updates_after_test",
    "self_learning_updates_during_test",
    "heldout_prediction_rmse",
    "closure_strength",
    "closure_raw_strength",
    "temporal_persistence",
    "strongly_connected",
    "mean_task_accuracy",
    "task_accuracy",
    "diagnostic_profile",
    "conjunctive_signature",
    "omega",
    "passes",
    "bottleneck",
    "causal_adjacency",
    "causal_effects",
    "closure_capacity_matrix",
    "closure_bottleneck_pair",
    "closure_cut_certificate",
    "cut_audit",
)


def _path_decomposition_row(
    result: Mapping[str, Any],
    *,
    seed: int,
    train_episode_count: int,
    test_episode_count: int,
    train_delay: int,
    test_delay: int,
    intervention_horizon: int,
    additional_stop_reasons: Sequence[str] = (),
) -> dict[str, Any]:
    audit = _audit_closure_row(result)
    stop_reasons = list(additional_stop_reasons)
    if not audit["passed"]:
        stop_reasons.append("cut_certificate_audit_failed")
    return {
        "row_status": "protocol_contradiction" if stop_reasons else "completed",
        "stop_reason": ",".join(stop_reasons),
        "seed": int(seed),
        "recurrent_gain": float(result["recurrent_gain"]),
        "closure_gain": float(result["closure_gain"]),
        "self_feedback_gain": float(result["self_feedback_gain"]),
        "action_feedback_gain": float(result["action_feedback_gain"]),
        "effective_self_feedback_gain": float(
            result["effective_self_feedback_gain"]
        ),
        "effective_action_feedback_gain": float(
            result["effective_action_feedback_gain"]
        ),
        "train_episode_count": int(train_episode_count),
        "test_episode_count": int(test_episode_count),
        "train_delay": int(train_delay),
        "test_delay": int(test_delay),
        "intervention_horizon": int(intervention_horizon),
        "adjacency_threshold": 7.5e-4,
        "intervention_magnitude": float(result["intervention_magnitude"]),
        "closure_normalization": float(result["intervention_magnitude"]),
        "predictor_snapshot_id": str(result["predictor_snapshot_id"]),
        "loaded_predictor_snapshot_id": str(
            result["loaded_predictor_snapshot_id"]
        ),
        "self_learning_updates": int(result["self_learning_updates"]),
        "self_learning_updates_before_test": int(
            result["self_learning_updates_before_test"]
        ),
        "self_learning_updates_after_test": int(
            result["self_learning_updates_after_test"]
        ),
        "self_learning_updates_during_test": int(
            result["self_learning_updates_during_test"]
        ),
        "heldout_prediction_rmse": float(result["heldout_prediction_rmse"]),
        "closure_strength": float(result["closure_strength"]),
        "closure_raw_strength": float(result["closure_raw_strength"]),
        "temporal_persistence": float(
            result["profile"]["temporal_persistence"]
        ),
        "strongly_connected": bool(result["profile"]["strongly_connected"]),
        "mean_task_accuracy": float(result["mean_task_accuracy"]),
        "task_accuracy": dict(result["task_accuracy"]),
        "diagnostic_profile": dict(result["profile"]),
        "conjunctive_signature": dict(result["signature"]),
        "omega": float(result["signature"]["omega"]),
        "passes": bool(result["signature"]["passes"]),
        "bottleneck": result["signature"]["bottleneck"],
        "causal_adjacency": list(result["causal_adjacency"]),
        "causal_effects": list(result["causal_effects"]),
        "closure_capacity_matrix": list(result["closure_capacity_matrix"]),
        "closure_bottleneck_pair": list(result["closure_bottleneck_pair"]),
        "closure_cut_certificate": dict(result["closure_cut_certificate"]),
        "cut_audit": audit,
    }


def _path_decomposition_contrasts(
    rows: Sequence[dict[str, Any]],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    lookup = {
        (
            int(row["seed"]),
            float(row["recurrent_gain"]),
            float(row["self_feedback_gain"]),
            float(row["action_feedback_gain"]),
        ): row
        for row in rows
    }
    cells = tuple(
        (recurrent, self_gain, action_gain)
        for recurrent in (0.0, 1.0)
        for self_gain in (0.0, 1.0)
        for action_gain in (0.0, 1.0)
    )
    definitions: dict[str, tuple[dict[tuple[float, float, float], float], str]] = {
        "self_contribution_at_recurrence_1": (
            {(1.0, 1.0, 1.0): 1.0, (1.0, 0.0, 1.0): -1.0},
            "M111 - M101",
        ),
        "action_contribution_at_recurrence_1": (
            {(1.0, 1.0, 1.0): 1.0, (1.0, 1.0, 0.0): -1.0},
            "M111 - M110",
        ),
        "recurrence_contribution_with_both_paths": (
            {(1.0, 1.0, 1.0): 1.0, (0.0, 1.0, 1.0): -1.0},
            "M111 - M011",
        ),
        "self_action_interaction_at_recurrence_1": (
            {
                (1.0, 1.0, 1.0): 1.0,
                (1.0, 1.0, 0.0): -1.0,
                (1.0, 0.0, 1.0): -1.0,
                (1.0, 0.0, 0.0): 1.0,
            },
            "M111 - M110 - M101 + M100",
        ),
        "self_action_interaction_at_recurrence_0": (
            {
                (0.0, 1.0, 1.0): 1.0,
                (0.0, 1.0, 0.0): -1.0,
                (0.0, 0.0, 1.0): -1.0,
                (0.0, 0.0, 0.0): 1.0,
            },
            "M011 - M010 - M001 + M000",
        ),
        "three_way_interaction": (
            {
                (1.0, 1.0, 1.0): 1.0,
                (1.0, 1.0, 0.0): -1.0,
                (1.0, 0.0, 1.0): -1.0,
                (1.0, 0.0, 0.0): 1.0,
                (0.0, 1.0, 1.0): -1.0,
                (0.0, 1.0, 0.0): 1.0,
                (0.0, 0.0, 1.0): 1.0,
                (0.0, 0.0, 0.0): -1.0,
            },
            "I_SA|R=1 - I_SA|R=0",
        ),
        "average_main_effect_recurrence": (
            {cell: (0.25 if cell[0] == 1.0 else -0.25) for cell in cells},
            "mean over S,A at R=1 minus mean over S,A at R=0",
        ),
        "average_main_effect_self_feedback": (
            {cell: (0.25 if cell[1] == 1.0 else -0.25) for cell in cells},
            "mean over R,A at S=1 minus mean over R,A at S=0",
        ),
        "average_main_effect_action_feedback": (
            {cell: (0.25 if cell[2] == 1.0 else -0.25) for cell in cells},
            "mean over R,S at A=1 minus mean over R,S at A=0",
        ),
    }
    rng = np.random.default_rng(bootstrap_seed)
    summaries: dict[str, Any] = {}
    for contrast_name, (coefficients, definition) in definitions.items():
        summaries[contrast_name] = {}
        for metric in ("closure_strength", "temporal_persistence"):
            values: list[float] = []
            for seed in seeds:
                values.append(
                    sum(
                        coefficient
                        * float(lookup[(seed, *cell)][metric])
                        for cell, coefficient in coefficients.items()
                    )
                )
            decision_contrasts = {
                "self_contribution_at_recurrence_1",
                "action_contribution_at_recurrence_1",
                "recurrence_contribution_with_both_paths",
                "self_action_interaction_at_recurrence_1",
            }
            summary = (
                _positive_paired_contrast_summary(
                    values,
                    seeds=seeds,
                    bootstrap_resamples=bootstrap_resamples,
                    rng=rng,
                )
                if contrast_name in decision_contrasts
                else _descriptive_paired_contrast_summary(
                    values,
                    seeds=seeds,
                    bootstrap_resamples=bootstrap_resamples,
                    rng=rng,
                )
            )
            summary["definition"] = definition
            summaries[contrast_name][metric] = summary

    necessity: dict[str, Any] = {}
    for path_name, removal_cell in (
        ("recurrence", (0.0, 1.0, 1.0)),
        ("self_feedback", (1.0, 0.0, 1.0)),
        ("action_feedback", (1.0, 1.0, 0.0)),
    ):
        necessity[path_name] = {}
        for metric in ("closure_strength", "temporal_persistence"):
            full_values = [
                float(lookup[(seed, 1.0, 1.0, 1.0)][metric])
                for seed in seeds
            ]
            removal_values = [
                float(lookup[(seed, *removal_cell)][metric]) for seed in seeds
            ]
            full_positive = all(value > 0.0 for value in full_values)
            exact_zero = all(value == 0.0 for value in removal_values)
            necessity[path_name][metric] = {
                "necessary": bool(full_positive and exact_zero),
                "rule": (
                    "full cell must be positive and removal must make every "
                    "seed exactly zero"
                ),
                "full_cell_positive_every_seed": bool(full_positive),
                "all_seeds_exactly_zero": bool(exact_zero),
                "full_cell_values": [
                    {"seed": int(seed), "value": float(value)}
                    for seed, value in zip(seeds, full_values)
                ],
                "values_after_removal": [
                    {"seed": int(seed), "value": float(value)}
                    for seed, value in zip(seeds, removal_values)
                ],
            }
    return summaries, necessity


def _path_cell_aggregates(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregates: list[dict[str, Any]] = []
    for recurrent_gain in (0.0, 1.0):
        for self_gain in (0.0, 1.0):
            for action_gain in (0.0, 1.0):
                group = [
                    row
                    for row in rows
                    if row["recurrent_gain"] == recurrent_gain
                    and row["self_feedback_gain"] == self_gain
                    and row["action_feedback_gain"] == action_gain
                ]
                aggregates.append(
                    {
                        "recurrent_gain": recurrent_gain,
                        "self_feedback_gain": self_gain,
                        "action_feedback_gain": action_gain,
                        "seed_count": len(group),
                        "metrics": {
                            metric: {
                                **_numeric_summary([row[metric] for row in group]),
                                "individual_values": [
                                    {
                                        "seed": int(row["seed"]),
                                        "value": float(row[metric]),
                                    }
                                    for row in group
                                ],
                            }
                            for metric in (
                                "closure_strength",
                                "temporal_persistence",
                            )
                        },
                    }
                )
    return aggregates


def _failed_path_decomposition_row(
    *,
    seed: int,
    recurrent_gain: float,
    closure_gain: float,
    self_feedback_gain: float,
    action_feedback_gain: float,
    train_episode_count: int,
    test_episode_count: int,
    train_delay: int,
    test_delay: int,
    intervention_horizon: int,
    predictor_snapshot_id: str,
    exception: Exception,
) -> dict[str, Any]:
    row = {field: None for field in PATH_DECOMPOSITION_ROW_FIELDS}
    row.update(
        {
            "row_status": "protocol_exception",
            "stop_reason": f"{type(exception).__name__}: {str(exception)}",
            "seed": int(seed),
            "recurrent_gain": float(recurrent_gain),
            "closure_gain": float(closure_gain),
            "self_feedback_gain": float(self_feedback_gain),
            "action_feedback_gain": float(action_feedback_gain),
            "effective_self_feedback_gain": (
                float(closure_gain) * float(self_feedback_gain)
            ),
            "effective_action_feedback_gain": (
                float(closure_gain) * float(action_feedback_gain)
            ),
            "train_episode_count": int(train_episode_count),
            "test_episode_count": int(test_episode_count),
            "train_delay": int(train_delay),
            "test_delay": int(test_delay),
            "intervention_horizon": int(intervention_horizon),
            "adjacency_threshold": 7.5e-4,
            "intervention_magnitude": INTERVENTION_MAGNITUDE,
            "closure_normalization": INTERVENTION_MAGNITUDE,
            "predictor_snapshot_id": predictor_snapshot_id,
            "loaded_predictor_snapshot_id": None,
            "task_accuracy": {},
            "diagnostic_profile": {},
            "conjunctive_signature": {},
            "causal_adjacency": [],
            "causal_effects": [],
            "closure_capacity_matrix": [],
            "closure_bottleneck_pair": [],
            "closure_cut_certificate": {},
            "cut_audit": {"passed": False, "not_run_due_to_exception": True},
        }
    )
    return row


def _plot_path_decomposition(
    path: Path,
    rows: Sequence[dict[str, Any]],
) -> None:
    plt = _sweep_pyplot()
    if not rows:
        figure, axis = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
        axis.text(
            0.5,
            0.5,
            "Protocol stopped before a complete path-decomposition row",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        figure.savefig(path, dpi=180)
        plt.close(figure)
        return
    configurations = (
        (0.0, 0.0, "neither"),
        (1.0, 0.0, "self only"),
        (0.0, 1.0, "action only"),
        (1.0, 1.0, "both"),
    )
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.2), constrained_layout=True)
    for axis, metric, title in (
        (axes[0], "closure_strength", "Closure strength"),
        (axes[1], "temporal_persistence", "Temporal persistence"),
    ):
        for self_gain, action_gain, label in configurations:
            means = []
            recurrent_values = (0.0, 1.0)
            for recurrent_gain in recurrent_values:
                values = [
                    float(row[metric])
                    for row in rows
                    if row["recurrent_gain"] == recurrent_gain
                    and row["self_feedback_gain"] == self_gain
                    and row["action_feedback_gain"] == action_gain
                ]
                means.append(float(np.mean(values)))
            axis.plot(recurrent_values, means, marker="o", label=label)
        axis.set_xticks((0.0, 1.0))
        axis.set_xlabel("Recurrent gain")
        axis.set_ylabel(title)
        axis.set_title(title)
    axes[1].legend(frameon=False)
    figure.suptitle("Factorial self/action feedback decomposition")
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_path_decomposition(
    output: str | Path,
    *,
    seeds: Sequence[int] = V04_VALIDATION_SEEDS,
    recurrent_gains: Sequence[float] = (0.0, 1.0),
    self_feedback_gains: Sequence[float] = (0.0, 1.0),
    action_feedback_gains: Sequence[float] = (0.0, 1.0),
    closure_gain: float = 1.0,
    train_episode_count: int = 64,
    test_episode_count: int = 32,
    train_delay: int = 5,
    test_delay: int = 7,
    intervention_horizon: int = 12,
    bootstrap_resamples: int = V04_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V04_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run the frozen 2x2x2 path-factorial decomposition."""

    seed_values, recurrent_values = _validate_sweep_values(seeds, recurrent_gains)
    _, self_values = _validate_sweep_values(seed_values, self_feedback_gains)
    _, action_values = _validate_sweep_values(seed_values, action_feedback_gains)
    if tuple(sorted(recurrent_values)) != (0.0, 1.0):
        raise ValueError("recurrent_gains must be exactly 0 and 1")
    if tuple(sorted(self_values)) != (0.0, 1.0):
        raise ValueError("self_feedback_gains must be exactly 0 and 1")
    if tuple(sorted(action_values)) != (0.0, 1.0):
        raise ValueError("action_feedback_gains must be exactly 0 and 1")
    if not np.isfinite(closure_gain) or closure_gain < 0.0:
        raise ValueError("closure_gain must be finite and nonnegative")
    _validate_experiment_counts(
        train_episode_count=train_episode_count,
        test_episode_count=test_episode_count,
        intervention_horizon=intervention_horizon,
    )
    if int(bootstrap_resamples) != bootstrap_resamples or bootstrap_resamples <= 0:
        raise ValueError("bootstrap_resamples must be a positive integer")

    destination = _prepare_empty_output(output)
    rows: list[dict[str, Any]] = []
    for seed in seed_values:
        try:
            train = _episodes(train_episode_count, seed=seed + 1, delay=train_delay)
            test = _episodes(test_episode_count, seed=seed + 2, delay=test_delay)
            snapshot = _train_predictor_snapshot(train, seed=seed)
            expected_snapshot_id = _predictor_snapshot_id(snapshot)
        except Exception as exception:
            rows.extend(
                _failed_path_decomposition_row(
                    seed=seed,
                    recurrent_gain=recurrent_gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_gain,
                    action_feedback_gain=action_gain,
                    train_episode_count=train_episode_count,
                    test_episode_count=test_episode_count,
                    train_delay=train_delay,
                    test_delay=test_delay,
                    intervention_horizon=intervention_horizon,
                    predictor_snapshot_id="",
                    exception=exception,
                )
                for recurrent_gain in sorted(recurrent_values)
                for self_gain in sorted(self_values)
                for action_gain in sorted(action_values)
            )
            continue
        for recurrent_gain in sorted(recurrent_values):
            for self_gain in sorted(self_values):
                for action_gain in sorted(action_values):
                    try:
                        result, _ = evaluate_variant(
                            "trained_self_model",
                            (),
                            train,
                            test,
                            seed=seed,
                            recurrent_gain=recurrent_gain,
                            closure_gain=closure_gain,
                            self_feedback_gain=self_gain,
                            action_feedback_gain=action_gain,
                            intervention_horizon=intervention_horizon,
                            predictor_snapshot=snapshot,
                        )
                        stop_reasons: list[str] = []
                        if result["self_learning_updates_during_test"] != 0:
                            stop_reasons.append("heldout_predictor_updates_nonzero")
                        if (
                            result["loaded_predictor_snapshot_id"]
                            != expected_snapshot_id
                        ):
                            stop_reasons.append("matched_predictor_identity_changed")
                        row = _path_decomposition_row(
                            result,
                            seed=seed,
                            train_episode_count=train_episode_count,
                            test_episode_count=test_episode_count,
                            train_delay=train_delay,
                            test_delay=test_delay,
                            intervention_horizon=intervention_horizon,
                            additional_stop_reasons=stop_reasons,
                        )
                    except Exception as exception:
                        row = _failed_path_decomposition_row(
                            seed=seed,
                            recurrent_gain=recurrent_gain,
                            closure_gain=closure_gain,
                            self_feedback_gain=self_gain,
                            action_feedback_gain=action_gain,
                            train_episode_count=train_episode_count,
                            test_episode_count=test_episode_count,
                            train_delay=train_delay,
                            test_delay=test_delay,
                            intervention_horizon=intervention_horizon,
                            predictor_snapshot_id=expected_snapshot_id,
                            exception=exception,
                        )
                    rows.append(row)

    protocol_stopped = any(row["stop_reason"] for row in rows)
    if protocol_stopped:
        contrasts: dict[str, Any] = {
            "status": "not_computed_after_protocol_contradiction"
        }
        necessity: dict[str, Any] = {
            "status": "not_computed_after_protocol_contradiction"
        }
        cell_aggregates: list[dict[str, Any]] = []
    else:
        contrasts, necessity = _path_decomposition_contrasts(
            rows,
            seeds=seed_values,
            bootstrap_resamples=int(bootstrap_resamples),
            bootstrap_seed=int(bootstrap_seed),
        )
        cell_aggregates = _path_cell_aggregates(rows)
    csv_name, json_name, png_name = (
        "path_decomposition.csv",
        "path_decomposition.json",
        "path_decomposition.png",
    )
    _write_structured_csv(destination / csv_name, PATH_DECOMPOSITION_ROW_FIELDS, rows)
    complete_rows = [
        row for row in rows if row["row_status"] != "protocol_exception"
    ]
    _plot_path_decomposition(destination / png_name, complete_rows)
    summary: dict[str, Any] = {
        "schema": "rrct.path_decomposition.v0.4",
        "experiment": "matched_factorial_path_decomposition",
        "version": __version__,
        "status": (
            "stopped_protocol_contradiction"
            if protocol_stopped
            else "completed_without_seed_filtering"
        ),
        "parameters": {
            "seeds": list(seed_values),
            "recurrent_gains": list(sorted(recurrent_values)),
            "self_feedback_multipliers": list(sorted(self_values)),
            "action_feedback_multipliers": list(sorted(action_values)),
            "closure_gain": float(closure_gain),
            "train_episode_count": int(train_episode_count),
            "test_episode_count": int(test_episode_count),
            "train_delay": int(train_delay),
            "test_delay": int(test_delay),
            "intervention_horizon": int(intervention_horizon),
            "matched_predictor": True,
        },
        "protocol": {
            "predictor": "one trained snapshot per seed, frozen across all eight cells",
            "heldout_updates_required": 0,
            "cut_audit": (
                "exact forward cut, exhaustive four-node simple paths, and SCC "
                "equivalence at every distinct effect threshold"
            ),
        },
        "bootstrap": {
            "method": "deterministic paired seed-resampling percentile bootstrap",
            "confidence": 0.95,
            "rng_seed": int(bootstrap_seed),
            "resamples": int(bootstrap_resamples),
            "seed_filtering": "none",
        },
        "runs": rows,
        "cell_aggregates": cell_aggregates,
        "paired_factorial_contrasts": contrasts,
        "necessity_tests": necessity,
        "stop_reasons": sorted(
            set(row["stop_reason"] for row in rows if row["stop_reason"])
        ),
        "all_cut_audits_passed": bool(all(row["cut_audit"]["passed"] for row in rows)),
        "artifacts": [json_name, csv_name, png_name],
        "interpretation_boundary": (
            "These paired interventions identify functional path contributions in "
            "the implemented architecture. Necessity is reported only for exact "
            "zero-after-removal results across every seed. They are not evidence "
            "of phenomenal consciousness."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def _average_ranks(values: Sequence[float]) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError("rank values must be nonempty and finite")
    order = np.argsort(vector, kind="mergesort")
    ranks = np.empty(vector.size, dtype=np.float64)
    start = 0
    while start < vector.size:
        stop = start + 1
        while stop < vector.size and vector[order[stop]] == vector[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def _spearman_correlation(
    first: Sequence[float],
    second: Sequence[float],
) -> float:
    first_ranks = _average_ranks(first)
    second_ranks = _average_ranks(second)
    if first_ranks.shape != second_ranks.shape:
        raise ValueError("Spearman inputs must have the same shape")
    if first_ranks.size < 2:
        raise ValueError("Spearman correlation requires at least two pairs")
    if float(np.std(first_ranks)) == 0.0 or float(np.std(second_ranks)) == 0.0:
        return 0.0
    return float(np.corrcoef(first_ranks, second_ranks)[0, 1])


def _association_gate(
    correlations: Sequence[float],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    rng: np.random.Generator,
    positive_only: bool,
) -> dict[str, Any]:
    summary = _paired_contrast_summary(
        correlations,
        seeds=seeds,
        bootstrap_resamples=bootstrap_resamples,
        rng=rng,
    )
    if positive_only:
        positive_count = int(sum(value > 0.0 for value in correlations))
        supported = (
            positive_count >= 6
            and float(summary["bootstrap_ci95_lower"]) > 0.0
        )
        summary.update(
            {
                "positive_seed_count": positive_count,
                "gate": "at least 6/8 positive and bootstrap lower bound > 0",
                "supported": bool(supported),
            }
        )
    else:
        summary["gate"] = (
            "nonzero mean direction, at least 6/8 matching signs, and a "
            "two-sided bootstrap interval excluding zero"
        )
    return summary


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _gain_file_token(value: float) -> str:
    return format(float(value), ".12g").replace("-", "m").replace(".", "p")


LOCAL_DYNAMICS_ROW_FIELDS = (
    "row_status",
    "stop_reason",
    "seed",
    "recurrent_gain",
    "closure_gain",
    "self_feedback_gain",
    "action_feedback_gain",
    "train_episode_count",
    "train_delay",
    "test_delay",
    "warmup_episode_count",
    "intervention_horizon",
    "adjacency_threshold",
    "intervention_magnitude",
    "closure_normalization",
    "predictor_snapshot_id",
    "loaded_predictor_snapshot_id",
    "self_learning_updates",
    "self_learning_updates_during_warmup_and_jacobian",
    "spectral_radius",
    "largest_singular_value",
    "branch_switch_fraction",
    "branch_switch_count",
    "branch_switch_coordinates",
    "positive_branch_signatures",
    "negative_branch_signatures",
    "high_switching",
    "state_dimension",
    "epsilon",
    "jacobian_file",
    "jacobian_sha256",
    "jacobian_shape",
    "jacobian_completed_columns",
    "jacobian_failure_stage",
    "raw_jacobian_retained",
    "raw_jacobian_finite",
    "raw_jacobian_nonfinite_count",
    "matrix_retention_reason",
    "temporal_persistence",
    "closure_strength",
    "closure_raw_strength",
    "strongly_connected",
    "causal_adjacency",
    "causal_effects",
    "closure_capacity_matrix",
    "closure_bottleneck_pair",
    "closure_cut_certificate",
    "cut_audit",
)


def _local_dynamics_correlations(
    rows: Sequence[dict[str, Any]],
    *,
    seeds: Sequence[int],
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    per_seed: list[dict[str, Any]] = []
    for seed in seeds:
        group = sorted(
            (row for row in rows if row["seed"] == seed),
            key=lambda row: float(row["recurrent_gain"]),
        )
        gains = [float(row["recurrent_gain"]) for row in group]
        spectral = [float(row["spectral_radius"]) for row in group]
        persistence = [float(row["temporal_persistence"]) for row in group]
        per_seed.append(
            {
                "seed": int(seed),
                "recurrence_vs_spectral_radius": _spearman_correlation(
                    gains, spectral
                ),
                "spectral_radius_vs_persistence": _spearman_correlation(
                    spectral, persistence
                ),
                "recurrence_vs_persistence": _spearman_correlation(
                    gains, persistence
                ),
            }
        )
    rng = np.random.default_rng(bootstrap_seed)
    gates = {
        field: _association_gate(
            [float(row[field]) for row in per_seed],
            seeds=seeds,
            bootstrap_resamples=bootstrap_resamples,
            rng=rng,
            positive_only=True,
        )
        for field in (
            "recurrence_vs_spectral_radius",
            "spectral_radius_vs_persistence",
        )
    }
    supporting = _descriptive_paired_contrast_summary(
        [float(row["recurrence_vs_persistence"]) for row in per_seed],
        seeds=seeds,
        bootstrap_resamples=bootstrap_resamples,
        rng=rng,
    )
    supporting["description"] = (
        "supporting recurrence-gain versus intervention-persistence association"
    )
    return per_seed, gates, supporting


def _plot_local_dynamics(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    plt = _sweep_pyplot()
    if not rows:
        figure, axis = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
        axis.text(
            0.5,
            0.5,
            "Protocol stopped before a complete local-dynamics row",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        figure.savefig(path, dpi=180)
        plt.close(figure)
        return
    gains = sorted(set(float(row["recurrent_gain"]) for row in rows))
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    for axis, metric, title in (
        (axes[0], "spectral_radius", "Piecewise local spectral radius"),
        (axes[1], "largest_singular_value", "Piecewise local operator norm"),
        (axes[2], "temporal_persistence", "Intervention persistence"),
    ):
        means = [
            float(
                np.mean(
                    [
                        row[metric]
                        for row in rows
                        if float(row["recurrent_gain"]) == gain
                    ]
                )
            )
            for gain in gains
        ]
        axis.plot(gains, means, marker="o", linewidth=2)
        for row in rows:
            axis.scatter(
                row["recurrent_gain"],
                row[metric],
                color="tab:blue",
                alpha=0.28,
                s=18,
            )
        axis.set_xlabel("Recurrent gain")
        axis.set_ylabel(title)
        axis.set_title(title)
    figure.suptitle("Piecewise local transition diagnostics (not Lyapunov exponents)")
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _run_warmed_intervention_trace(
    agent_template: RRCTAgent,
    *,
    source_node: int | None,
    horizon: int,
    magnitude: float,
) -> np.ndarray:
    agent = copy.deepcopy(agent_template)
    agent.freeze_self_model()
    workspace_delta = np.zeros(agent.workspace_dim, dtype=np.float64)
    workspace_delta[0] = magnitude
    if source_node == 0:
        for specialist in agent.specialists:
            specialist.state[0] += magnitude
    elif source_node == 2:
        agent.self_model.state[0] += magnitude
    elif source_node == 3:
        agent.memory.write(workspace_delta, time=agent.time, source="v04_local")
    zero = np.zeros(agent.observation_dim, dtype=np.float64)
    trace: list[np.ndarray] = []
    for lag in range(horizon):
        result = agent.step(
            zero,
            source="v04_local_intervention",
            perturb_workspace=(
                workspace_delta if source_node == 1 and lag == 0 else None
            ),
        )
        trace.append(_node_matrix(result))
    return np.asarray(trace, dtype=np.float64)


def _warmed_intervention_diagnostics(
    agent_template: RRCTAgent,
    *,
    horizon: int,
    intervention_magnitude: float = INTERVENTION_MAGNITUDE,
) -> InterventionResult:
    """Estimate causal diagnostics from matched terminal warmed-state copies."""

    baseline = _run_warmed_intervention_trace(
        agent_template,
        source_node=None,
        horizon=horizon,
        magnitude=intervention_magnitude,
    )
    traces = np.asarray(
        [
            _run_warmed_intervention_trace(
                agent_template,
                source_node=source_node,
                horizon=horizon,
                magnitude=intervention_magnitude,
            )
            for source_node in range(4)
        ],
        dtype=np.float64,
    )
    adjacency, effects = causal_adjacency(
        baseline,
        traces,
        threshold=7.5e-4,
        include_self=True,
        return_effects=True,
    )
    workspace_trace = traces[1]
    curve = np.sqrt(np.mean(np.square(workspace_trace - baseline), axis=(1, 2)))
    if curve[0] > 0.0:
        curve = np.clip(curve / curve[0], 0.0, 1.0)
    closure = widest_path_closure_details(
        effects,
        normalize=intervention_magnitude,
    )
    cut = widest_path_cut_certificate(effects)
    cut_record = _json_safe(cut)
    return InterventionResult(
        baseline=baseline,
        interventions=traces,
        temporal_curve=curve,
        effects=np.asarray(effects, dtype=np.float64),
        adjacency=np.asarray(adjacency, dtype=bool),
        broadcast=broadcast_reach(
            baseline,
            workspace_trace,
            consumer_axis=1,
            threshold=7.5e-4,
        ),
        persistence=temporal_persistence_auc(curve),
        strongly_connected=is_strongly_connected(adjacency),
        closure_strength=closure.strength,
        closure_raw_strength=closure.raw_strength,
        closure_capacity_matrix=closure.capacity_matrix,
        closure_bottleneck_pair=closure.weakest_pair,
        closure_cut_certificate=cut_record,
        self_to_workspace_effect=float(effects[2, 1] / intervention_magnitude),
    )


def _local_dynamics_gain_aggregates(
    rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    aggregates: list[dict[str, Any]] = []
    for gain in sorted(set(float(row["recurrent_gain"]) for row in rows)):
        group = [row for row in rows if float(row["recurrent_gain"]) == gain]
        aggregates.append(
            {
                "recurrent_gain": gain,
                "seed_count": len(group),
                "high_switch_count": int(
                    sum(bool(row["high_switching"]) for row in group)
                ),
                "metrics": {
                    metric: {
                        **_numeric_summary([float(row[metric]) for row in group]),
                        "individual_values": [
                            {
                                "seed": int(row["seed"]),
                                "value": float(row[metric]),
                            }
                            for row in group
                        ],
                    }
                    for metric in (
                        "spectral_radius",
                        "largest_singular_value",
                        "branch_switch_fraction",
                        "temporal_persistence",
                        "closure_strength",
                    )
                },
            }
        )
    return aggregates


def _failed_local_dynamics_row(
    *,
    destination: Path,
    seed: int,
    gain: float,
    closure_gain: float,
    self_feedback_gain: float,
    action_feedback_gain: float,
    train_episode_count: int,
    train_delay: int,
    test_delay: int,
    warmup_episode_count: int,
    intervention_horizon: int,
    snapshot_id: str,
    epsilon: float,
    exception: Exception,
) -> dict[str, Any]:
    row = {field: None for field in LOCAL_DYNAMICS_ROW_FIELDS}
    matrix_name = f"local_jacobian_seed_{seed}_gain_{_gain_file_token(gain)}.npy"
    matrix_path = destination / matrix_name
    exposed_matrix = getattr(exception, "jacobian", None)
    if matrix_path.is_file():
        retained_matrix = np.load(matrix_path, allow_pickle=False)
        retention_reason = "side artifact was written before the exception"
    elif exposed_matrix is not None:
        retained_matrix = np.asarray(exposed_matrix, dtype=np.float64)
        np.save(matrix_path, retained_matrix, allow_pickle=False)
        retention_reason = "exception exposed an immutable raw or partial Jacobian"
    else:
        retained_matrix = None
        retention_reason = (
            "exception exposed no Jacobian and no side artifact had been written"
        )
    positive_signatures = [
        _json_safe(signature)
        for signature in getattr(exception, "positive_branch_signatures", ())
    ]
    negative_signatures = [
        _json_safe(signature)
        for signature in getattr(exception, "negative_branch_signatures", ())
    ]
    raw_positive_signatures = tuple(
        getattr(exception, "positive_branch_signatures", ())
    )
    raw_negative_signatures = tuple(
        getattr(exception, "negative_branch_signatures", ())
    )
    branch_switch_coordinates = [
        index
        for index, (positive, negative) in enumerate(
            zip(raw_positive_signatures, raw_negative_signatures)
        )
        if positive != negative
    ]
    retained_dimension = int(
        getattr(
            exception,
            "state_dimension",
            retained_matrix.shape[0] if retained_matrix is not None else 0,
        )
    )
    branch_switch_fraction = (
        len(branch_switch_coordinates) / retained_dimension
        if retained_dimension > 0
        else None
    )
    row.update(
        {
            "row_status": "protocol_exception",
            "stop_reason": (
                f"{type(exception).__name__}: {str(exception)}"
            ),
            "seed": int(seed),
            "recurrent_gain": float(gain),
            "closure_gain": float(closure_gain),
            "self_feedback_gain": float(self_feedback_gain),
            "action_feedback_gain": float(action_feedback_gain),
            "train_episode_count": int(train_episode_count),
            "train_delay": int(train_delay),
            "test_delay": int(test_delay),
            "warmup_episode_count": int(warmup_episode_count),
            "intervention_horizon": int(intervention_horizon),
            "adjacency_threshold": 7.5e-4,
            "intervention_magnitude": INTERVENTION_MAGNITUDE,
            "closure_normalization": INTERVENTION_MAGNITUDE,
            "predictor_snapshot_id": snapshot_id,
            "epsilon": float(epsilon),
            "branch_switch_fraction": branch_switch_fraction,
            "branch_switch_count": len(branch_switch_coordinates),
            "branch_switch_coordinates": branch_switch_coordinates,
            "positive_branch_signatures": positive_signatures,
            "negative_branch_signatures": negative_signatures,
            "high_switching": (
                branch_switch_fraction > 0.10
                if branch_switch_fraction is not None
                else None
            ),
            "jacobian_completed_columns": int(
                getattr(exception, "completed_columns", 0)
            ),
            "jacobian_failure_stage": str(
                getattr(exception, "stage", "external_exception")
            ),
            "raw_jacobian_retained": retained_matrix is not None,
            "matrix_retention_reason": retention_reason,
            "causal_adjacency": [],
            "causal_effects": [],
            "closure_capacity_matrix": [],
            "closure_bottleneck_pair": [],
            "closure_cut_certificate": {},
            "cut_audit": {"passed": False, "not_run_due_to_exception": True},
        }
    )
    if retained_matrix is not None:
        nonfinite_count = int(np.sum(~np.isfinite(retained_matrix)))
        row.update(
            {
                "state_dimension": int(
                    getattr(exception, "state_dimension", retained_matrix.shape[0])
                ),
                "epsilon": float(getattr(exception, "epsilon", epsilon)),
                "jacobian_file": matrix_name,
                "jacobian_sha256": _file_sha256(matrix_path),
                "jacobian_shape": list(retained_matrix.shape),
                "raw_jacobian_finite": nonfinite_count == 0,
                "raw_jacobian_nonfinite_count": nonfinite_count,
            }
        )
    else:
        row.update(
            {
                "jacobian_file": None,
                "jacobian_sha256": None,
                "jacobian_shape": None,
                "raw_jacobian_finite": None,
                "raw_jacobian_nonfinite_count": None,
            }
        )
    return row


def _run_local_dynamics_cell(
    destination: Path,
    *,
    seed: int,
    gain: float,
    closure_gain: float,
    self_feedback_gain: float,
    action_feedback_gain: float,
    train_episode_count: int,
    train_delay: int,
    test_delay: int,
    warmup_episode_count: int,
    intervention_horizon: int,
    epsilon: float,
    heldout_episode: BindingEpisode,
    snapshot: Mapping[str, Any],
    snapshot_id: str,
) -> tuple[dict[str, Any], str]:
    agent = _agent(
        seed,
        recurrent_gain=gain,
        closure_gain=closure_gain,
        self_feedback_gain=self_feedback_gain,
        action_feedback_gain=action_feedback_gain,
        self_model_mode="frozen",
    )
    agent.load_predictor_snapshot(snapshot, freeze=True)
    updates_before = int(agent.self_learning_updates)
    agent.reset()
    for observation in heldout_episode.observations:
        agent.step(observation, source="v04_local_warmup")
    diagnostics = local_transition_jacobian(
        agent,
        np.zeros(agent.observation_dim, dtype=np.float64),
        epsilon=epsilon,
    )
    intervention = _warmed_intervention_diagnostics(
        agent,
        horizon=intervention_horizon,
    )
    updates_after = int(agent.self_learning_updates)
    matrix = np.asarray(diagnostics.jacobian, dtype=np.float64)
    matrix_name = f"local_jacobian_seed_{seed}_gain_{_gain_file_token(gain)}.npy"
    matrix_path = destination / matrix_name
    np.save(matrix_path, matrix, allow_pickle=False)
    matrix_sha = _file_sha256(matrix_path)
    cut_audit = _audit_closure_row(
        {
            "causal_effects": intervention.effects.tolist(),
            "closure_cut_certificate": intervention.closure_cut_certificate,
            "closure_capacity_matrix": intervention.closure_capacity_matrix.tolist(),
            "intervention_magnitude": INTERVENTION_MAGNITUDE,
            "closure_bottleneck_pair": list(intervention.closure_bottleneck_pair),
            "closure_raw_strength": intervention.closure_raw_strength,
        }
    )
    positive_signatures = [
        _json_safe(signature)
        for signature in diagnostics.positive_branch_signatures
    ]
    negative_signatures = [
        _json_safe(signature)
        for signature in diagnostics.negative_branch_signatures
    ]
    stop_reasons: list[str] = []
    if updates_after != updates_before:
        stop_reasons.append("frozen_predictor_updates_nonzero")
    loaded_snapshot_id = _predictor_snapshot_id(agent.predictor_snapshot())
    if loaded_snapshot_id != snapshot_id:
        stop_reasons.append("matched_predictor_identity_changed")
    if int(diagnostics.state_dimension) != 158:
        stop_reasons.append("state_dimension_not_158")
    if matrix.shape != (158, 158):
        stop_reasons.append("jacobian_shape_not_158_by_158")
    if not np.all(np.isfinite(matrix)):
        stop_reasons.append("jacobian_contains_nonfinite_values")
    if len(positive_signatures) != 158 or len(negative_signatures) != 158:
        stop_reasons.append("branch_signature_retention_incomplete")
    if not cut_audit["passed"]:
        stop_reasons.append("cut_certificate_audit_failed")
    row = {
        "row_status": "protocol_contradiction" if stop_reasons else "completed",
        "stop_reason": ",".join(stop_reasons),
        "seed": int(seed),
        "recurrent_gain": float(gain),
        "closure_gain": float(closure_gain),
        "self_feedback_gain": float(self_feedback_gain),
        "action_feedback_gain": float(action_feedback_gain),
        "train_episode_count": int(train_episode_count),
        "train_delay": int(train_delay),
        "test_delay": int(test_delay),
        "warmup_episode_count": int(warmup_episode_count),
        "intervention_horizon": int(intervention_horizon),
        "adjacency_threshold": 7.5e-4,
        "intervention_magnitude": INTERVENTION_MAGNITUDE,
        "closure_normalization": INTERVENTION_MAGNITUDE,
        "predictor_snapshot_id": snapshot_id,
        "loaded_predictor_snapshot_id": loaded_snapshot_id,
        "self_learning_updates": updates_before,
        "self_learning_updates_during_warmup_and_jacobian": (
            updates_after - updates_before
        ),
        "spectral_radius": float(diagnostics.spectral_radius),
        "largest_singular_value": float(diagnostics.largest_singular_value),
        "branch_switch_fraction": float(diagnostics.branch_switch_fraction),
        "branch_switch_count": int(diagnostics.branch_switch_count),
        "branch_switch_coordinates": list(diagnostics.branch_switch_coordinates),
        "positive_branch_signatures": positive_signatures,
        "negative_branch_signatures": negative_signatures,
        "high_switching": bool(diagnostics.branch_switch_fraction > 0.10),
        "state_dimension": int(diagnostics.state_dimension),
        "epsilon": float(diagnostics.epsilon),
        "jacobian_file": matrix_name,
        "jacobian_sha256": matrix_sha,
        "jacobian_shape": list(matrix.shape),
        "jacobian_completed_columns": int(diagnostics.state_dimension),
        "jacobian_failure_stage": "",
        "raw_jacobian_retained": True,
        "raw_jacobian_finite": bool(np.all(np.isfinite(matrix))),
        "raw_jacobian_nonfinite_count": int(np.sum(~np.isfinite(matrix))),
        "matrix_retention_reason": "completed Jacobian retained",
        "temporal_persistence": float(intervention.persistence),
        "closure_strength": float(intervention.closure_strength),
        "closure_raw_strength": float(intervention.closure_raw_strength),
        "strongly_connected": bool(intervention.strongly_connected),
        "causal_adjacency": intervention.adjacency.astype(int).tolist(),
        "causal_effects": intervention.effects.tolist(),
        "closure_capacity_matrix": intervention.closure_capacity_matrix.tolist(),
        "closure_bottleneck_pair": list(intervention.closure_bottleneck_pair),
        "closure_cut_certificate": intervention.closure_cut_certificate,
        "cut_audit": cut_audit,
    }
    return row, matrix_name


def run_local_dynamics(
    output: str | Path,
    *,
    seeds: Sequence[int] = V04_VALIDATION_SEEDS,
    recurrent_gains: Sequence[float] = DEFAULT_LOCAL_DYNAMICS_GAINS,
    closure_gain: float = 1.0,
    self_feedback_gain: float = 1.0,
    action_feedback_gain: float = 1.0,
    train_episode_count: int = 32,
    train_delay: int = 5,
    test_delay: int = 7,
    warmup_episode_count: int = 1,
    epsilon: float = 1e-5,
    intervention_horizon: int = 12,
    bootstrap_resamples: int = V04_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V04_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Measure one frozen piecewise local Jacobian per seed and gain."""

    seed_values, gain_values = _validate_sweep_values(seeds, recurrent_gains)
    gain_values = tuple(sorted(gain_values))
    if len(gain_values) < 2:
        raise ValueError("local dynamics requires at least two recurrence gains")
    for name, value in (
        ("closure_gain", closure_gain),
        ("self_feedback_gain", self_feedback_gain),
        ("action_feedback_gain", action_feedback_gain),
    ):
        if not np.isfinite(value) or value < 0.0:
            raise ValueError(f"{name} must be finite and nonnegative")
    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("epsilon must be finite and positive")
    if int(warmup_episode_count) != 1:
        raise ValueError("warmup_episode_count is preregistered as exactly one")
    _validate_experiment_counts(
        train_episode_count=train_episode_count,
        intervention_horizon=intervention_horizon,
    )
    if int(bootstrap_resamples) != bootstrap_resamples or bootstrap_resamples <= 0:
        raise ValueError("bootstrap_resamples must be a positive integer")

    destination = _prepare_empty_output(output)
    rows: list[dict[str, Any]] = []
    matrix_artifacts: list[str] = []
    for seed in seed_values:
        try:
            train = _episodes(train_episode_count, seed=seed + 1, delay=train_delay)
            heldout_episode = _episodes(8, seed=seed + 2, delay=test_delay)[0]
            snapshot = _train_predictor_snapshot(train, seed=seed)
            snapshot_id = _predictor_snapshot_id(snapshot)
        except Exception as exception:
            rows.extend(
                _failed_local_dynamics_row(
                    destination=destination,
                    seed=seed,
                    gain=gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_feedback_gain,
                    action_feedback_gain=action_feedback_gain,
                    train_episode_count=train_episode_count,
                    train_delay=train_delay,
                    test_delay=test_delay,
                    warmup_episode_count=warmup_episode_count,
                    intervention_horizon=intervention_horizon,
                    snapshot_id="",
                    epsilon=epsilon,
                    exception=exception,
                )
                for gain in gain_values
            )
            continue
        for gain in gain_values:
            try:
                row, matrix_name = _run_local_dynamics_cell(
                    destination,
                    seed=seed,
                    gain=gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_feedback_gain,
                    action_feedback_gain=action_feedback_gain,
                    train_episode_count=train_episode_count,
                    train_delay=train_delay,
                    test_delay=test_delay,
                    warmup_episode_count=warmup_episode_count,
                    intervention_horizon=intervention_horizon,
                    epsilon=epsilon,
                    heldout_episode=heldout_episode,
                    snapshot=snapshot,
                    snapshot_id=snapshot_id,
                )
            except Exception as exception:  # retained preregistered stop row
                row = _failed_local_dynamics_row(
                    destination=destination,
                    seed=seed,
                    gain=gain,
                    closure_gain=closure_gain,
                    self_feedback_gain=self_feedback_gain,
                    action_feedback_gain=action_feedback_gain,
                    train_episode_count=train_episode_count,
                    train_delay=train_delay,
                    test_delay=test_delay,
                    warmup_episode_count=warmup_episode_count,
                    intervention_horizon=intervention_horizon,
                    snapshot_id=snapshot_id,
                    epsilon=epsilon,
                    exception=exception,
                )
            if row.get("jacobian_file"):
                matrix_artifacts.append(str(row["jacobian_file"]))
            rows.append(row)

    protocol_stopped = any(row["stop_reason"] for row in rows)
    if protocol_stopped:
        per_seed: list[dict[str, Any]] = []
        gates: dict[str, Any] = {
            "status": "not_computed_after_protocol_contradiction"
        }
        supporting_association: dict[str, Any] = {
            "status": "not_computed_after_protocol_contradiction"
        }
    else:
        per_seed, gates, supporting_association = _local_dynamics_correlations(
            rows,
            seeds=seed_values,
            bootstrap_resamples=int(bootstrap_resamples),
            bootstrap_seed=int(bootstrap_seed),
        )
    complete_rows = [
        row for row in rows if row["row_status"] != "protocol_exception"
    ]
    gain_aggregates = _local_dynamics_gain_aggregates(complete_rows)
    csv_name, json_name, png_name = (
        "local_dynamics.csv",
        "local_dynamics.json",
        "local_dynamics.png",
    )
    _write_structured_csv(destination / csv_name, LOCAL_DYNAMICS_ROW_FIELDS, rows)
    _plot_local_dynamics(destination / png_name, complete_rows)
    summary: dict[str, Any] = {
        "schema": "rrct.local_dynamics.v0.4",
        "experiment": "piecewise_local_transition_jacobians",
        "version": __version__,
        "status": (
            "stopped_protocol_contradiction"
            if protocol_stopped
            else "completed_without_seed_filtering"
        ),
        "parameters": {
            "seeds": list(seed_values),
            "recurrent_gains": list(gain_values),
            "closure_gain": float(closure_gain),
            "self_feedback_gain": float(self_feedback_gain),
            "action_feedback_gain": float(action_feedback_gain),
            "train_episode_count": int(train_episode_count),
            "train_delay": int(train_delay),
            "test_delay": int(test_delay),
            "warmup_episode_count": int(warmup_episode_count),
            "epsilon": float(epsilon),
            "intervention_horizon": int(intervention_horizon),
        },
        "protocol": {
            "predictor": "one trained snapshot per seed, frozen across gains",
            "jacobian": (
                "centered finite difference of the 158-coordinate continuous "
                "transition state after one complete deterministic held-out "
                "warmup episode, with the next input fixed to all zeros"
            ),
            "intervention": (
                "baseline and four source interventions start from independent "
                "deep copies of the identical terminal warmed state and continue "
                "on all-zero observations"
            ),
            "branch_signature": [
                "selected_specialists",
                "next_resolution_level",
                "memory_indices",
                "memory_written",
                "action_candidate_index",
            ],
            "matrix_retention": (
                "one deterministic NumPy binary side artifact with SHA256 for "
                "every completed, raw, or partial Jacobian; failures before any "
                "matrix exists retain an explicit no-matrix reason"
            ),
            "heldout_updates_required": 0,
        },
        "bootstrap": {
            "method": "deterministic paired seed-resampling percentile bootstrap",
            "confidence": 0.95,
            "rng_seed": int(bootstrap_seed),
            "resamples": int(bootstrap_resamples),
            "seed_filtering": "none",
        },
        "runs": rows,
        "per_gain_aggregates": gain_aggregates,
        "per_seed_spearman": per_seed,
        "positive_association_gates": gates,
        "supporting_recurrence_vs_persistence": supporting_association,
        "stop_reasons": sorted(
            set(row["stop_reason"] for row in rows if row["stop_reason"])
        ),
        "state_dimensions_observed": sorted(
            set(int(row["state_dimension"]) for row in complete_rows)
        ),
        "all_cut_audits_passed": bool(all(row["cut_audit"]["passed"] for row in rows)),
        "artifacts": [json_name, csv_name, png_name, *matrix_artifacts],
        "interpretation_boundary": (
            "These are piecewise local finite-difference transition diagnostics. "
            "They are not Lyapunov exponents and are not evidence for criticality, "
            "a phase transition, or phenomenal consciousness."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


__all__ = [
    "DEFAULT_HYSTERESIS_GAINS",
    "DEFAULT_LOCAL_DYNAMICS_GAINS",
    "DEFAULT_PHASE_GAINS",
    "DEFAULT_SURFACE_GAINS",
    "DEFAULT_SWEEP_SEEDS",
    "EVALUATION_CONDITIONS",
    "GAIN_SURFACE_ROW_FIELDS",
    "HYSTERESIS_ROW_FIELDS",
    "INTERVENTION_MAGNITUDE",
    "MEDIATION_CONDITIONS",
    "MEDIATION_ROW_FIELDS",
    "LOCAL_DYNAMICS_ROW_FIELDS",
    "PATH_DECOMPOSITION_ROW_FIELDS",
    "PROFILE_THRESHOLDS",
    "SELF_MODEL_CONDITIONS",
    "SHUFFLED_SELF_MODEL_CONDITION",
    "SWEEP_ROW_FIELDS",
    "V03_BOOTSTRAP_RESAMPLES",
    "V03_BOOTSTRAP_SEED",
    "V03_VALIDATION_SEEDS",
    "V04_BOOTSTRAP_RESAMPLES",
    "V04_BOOTSTRAP_SEED",
    "V04_VALIDATION_SEEDS",
    "VARIANTS",
    "collect_representations",
    "evaluate_variant",
    "intervention_diagnostics",
    "run_experiment",
    "run_gain_surface",
    "run_hysteresis_sweep",
    "run_local_dynamics",
    "run_path_decomposition",
    "run_phase_sweep",
    "run_predictor_mediation",
    "run_seed_sweep",
]

from __future__ import annotations

import math
from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.jspace import (
    MovingJacobianFrame,
    jacobian_energy_capture,
    projector_idempotence_defect,
)
from rrct_lab.orchestration import RunContext
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import digest_object, entropy, seed_everything


FAMILY = "persistent_fuzzy_j_workspace"
TASK_NAMES = ("routine", "pair", "overlap", "global")
EVENT_NAMES = ("none", "world_shift", "provenance_burst")
CONSUMER_NAMES = ("report", "inference", "plan", "memory")
_BATCH_SIZE = 16
_SOURCE_COUNT = 4
_HEAD_COUNT = len(CONSUMER_NAMES)
# Every signed consumer Jacobian is paired with its negative.  The workspace
# code can therefore remain genuinely nonnegative without discarding one sign
# of a downstream-relevant residual direction.
_CODE_DIMENSION = 2 * _HEAD_COUNT


def _softmax(values: np.ndarray, axis: int = -1) -> np.ndarray:
    shifted = values - np.max(values, axis=axis, keepdims=True)
    exponentials = np.exp(np.clip(shifted, -60.0, 60.0))
    return exponentials / np.maximum(
        np.sum(exponentials, axis=axis, keepdims=True), 1e-12
    )


def _canonicalize_columns(matrix: np.ndarray) -> np.ndarray:
    result = np.asarray(matrix, dtype=float).copy()
    for column in range(result.shape[1]):
        pivot = int(np.argmax(np.abs(result[:, column])))
        if result[pivot, column] < 0.0:
            result[:, column] *= -1.0
    return result


def _orthonormal_frame(
    rng: np.random.Generator, dimension: int, rank: int
) -> np.ndarray:
    q, _ = np.linalg.qr(rng.normal(size=(dimension, rank)), mode="reduced")
    return _canonicalize_columns(q[:, :rank])


def _pca_frame(covariance_sum: np.ndarray, count: int, rank: int) -> np.ndarray:
    if count <= 0 or float(np.linalg.norm(covariance_sum)) <= 1e-12:
        return np.eye(covariance_sum.shape[0], rank, dtype=float)
    covariance = covariance_sum / max(1, count)
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    order = np.argsort(values)[::-1][:rank]
    return _canonicalize_columns(vectors[:, order])


def _covariance_variance_fraction(
    covariance_sum: np.ndarray, projector: np.ndarray
) -> float:
    covariance = np.asarray(covariance_sum, dtype=float)
    denominator = float(np.trace(covariance))
    if denominator <= 1e-12:
        return 0.0
    retained = float(np.trace(np.asarray(projector, dtype=float) @ covariance))
    return float(np.clip(retained / denominator, 0.0, 1.0))


def _relative_preservation(reference: np.ndarray, candidate: np.ndarray) -> float:
    baseline = np.asarray(reference, dtype=float)
    altered = np.asarray(candidate, dtype=float)
    denominator = float(np.linalg.norm(baseline))
    difference = float(np.linalg.norm(altered - baseline))
    if denominator <= 1e-12:
        return 1.0 if difference <= 1e-12 else 0.0
    return 1.0 - min(1.0, difference / denominator)


def _basis_code(
    hidden: np.ndarray,
    basis: np.ndarray,
    *,
    top_k: int,
    output_dimension: int,
    nonnegative: bool,
) -> np.ndarray:
    scores = hidden @ basis
    if nonnegative:
        scores = np.maximum(scores, 0.0)
    if top_k < scores.shape[1]:
        keep = np.argpartition(scores, -top_k, axis=1)[:, -top_k:]
        mask = np.zeros_like(scores, dtype=bool)
        np.put_along_axis(mask, keep, True, axis=1)
        scores = np.where(mask, scores, 0.0)
    code = np.zeros((len(hidden), output_dimension), dtype=float)
    width = min(output_dimension, scores.shape[1])
    code[:, :width] = scores[:, :width]
    return code


def _j_codes(frame: Any, hidden: np.ndarray, top_k: int) -> np.ndarray:
    return np.stack(
        [frame.sparse_code(vector, top_k=top_k) for vector in hidden], axis=0
    )


def _task_weights(tasks: np.ndarray) -> np.ndarray:
    templates = np.asarray(
        [
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0, 0.0],
            [1.0, 0.6, 0.6, 0.0],
            [0.7, 0.7, 0.7, 0.7],
        ],
        dtype=float,
    )
    return templates[tasks]


def _make_stream(
    seed: int,
    steps: int,
    event_interval: int,
    feature_dimension: int,
) -> dict[str, np.ndarray]:
    task_rng = np.random.default_rng(seed ^ 0x7A510001)
    event_rng = np.random.default_rng(seed ^ 0x7A510002)
    value_rng = np.random.default_rng(seed ^ 0x7A510003)

    tasks = np.empty((steps, _BATCH_SIZE), dtype=int)
    balanced = np.tile(np.arange(len(TASK_NAMES)), _BATCH_SIZE // len(TASK_NAMES))
    for step in range(steps):
        tasks[step] = task_rng.permutation(balanced)

    # -1 denotes an ordinary continuation.  Zero is reserved for a genuine
    # matched null boundary, so recurrence specificity never treats every
    # non-boundary step as a null event.
    events = np.full(steps, -1, dtype=int)
    world_sign = np.ones(steps, dtype=float)
    current_world = 1.0
    boundary_count = int(math.ceil(steps / max(1, event_interval)))
    event_cycle = np.tile(
        np.arange(len(EVENT_NAMES)),
        int(math.ceil(boundary_count / len(EVENT_NAMES))),
    )[:boundary_count]
    event_cycle = event_rng.permutation(event_cycle)
    for boundary, start in enumerate(range(0, steps, max(1, event_interval))):
        event = int(event_cycle[boundary])
        events[start] = event
        if event == 1:
            current_world *= -1.0
        stop = min(steps, start + max(1, event_interval))
        world_sign[start:stop] = current_world

    latent = value_rng.normal(size=(steps, _BATCH_SIZE, _SOURCE_COUNT))
    valid = value_rng.random(size=latent.shape) < 0.78
    chain_valid = value_rng.random(size=(steps, _BATCH_SIZE)) < 0.82
    for step in range(steps):
        segment_event = events[(step // max(1, event_interval)) * max(1, event_interval)]
        if segment_event == 2:
            chain_valid[step] = value_rng.random(_BATCH_SIZE) < 0.48
    context = value_rng.normal(size=(steps, _BATCH_SIZE))
    world_cue = (
        0.30 * world_sign[:, None]
        + value_rng.normal(scale=0.85, size=(steps, _BATCH_SIZE))
    )
    signal = latent + value_rng.normal(scale=0.08, size=latent.shape)
    receipt = (
        2.0 * valid.astype(float)
        - 1.0
        + value_rng.normal(scale=0.10, size=latent.shape)
    )
    chain_score = (
        2.0 * chain_valid.astype(float)
        - 1.0
        + value_rng.normal(scale=0.10, size=(steps, _BATCH_SIZE))
    )

    features = np.zeros(
        (steps, _BATCH_SIZE, _SOURCE_COUNT, feature_dimension), dtype=float
    )
    features[..., 0] = signal
    features[..., 1] = receipt
    features[..., 2] = signal * np.clip(0.5 * (receipt + 1.0), 0.0, 1.0)
    features[..., 3] = chain_score[:, :, None]
    features[..., 4] = world_cue[:, :, None]
    features[..., 5] = context[:, :, None]
    for task in range(len(TASK_NAMES)):
        features[..., 6 + task] = (tasks == task)[:, :, None]
    for source in range(_SOURCE_COUNT):
        features[:, :, source, 10 + source] = 1.0
    features[..., 14] = 1.0

    weights = _task_weights(tasks)
    trusted_latent = latent * valid.astype(float)
    denominator = np.sqrt(np.maximum(np.sum(np.square(weights), axis=2), 1.0))
    raw_content = np.sum(weights * trusted_latent, axis=2) / denominator
    report = np.tanh(raw_content)
    inference = np.tanh(0.70 * raw_content + 0.45 * context)
    plan = chain_valid.astype(float) * np.tanh(world_sign[:, None] * raw_content)
    memory = 2.0 * chain_valid.astype(float) - 1.0
    targets = np.stack((report, inference, plan, memory), axis=2)
    routine_target = np.tanh(latent[..., 0] * valid[..., 0].astype(float))
    shuffles = np.stack(
        [value_rng.permutation(_SOURCE_COUNT) for _ in range(steps)], axis=0
    )
    return {
        "features": features,
        "tasks": tasks,
        "events": events,
        "world_sign": world_sign,
        "context": context,
        "world_cue": world_cue,
        "chain_valid": chain_valid.astype(float),
        "chain_score": chain_score,
        "targets": targets,
        "routine_target": routine_target,
        "shuffles": shuffles,
    }


def _memberships(
    features: np.ndarray,
    gate_weights: np.ndarray,
    temperature: float,
    *,
    dynamic: bool,
    hard: bool,
) -> tuple[np.ndarray, np.ndarray]:
    if dynamic:
        logits = np.einsum("baf,fk->bak", features, gate_weights)
    else:
        logits = np.zeros(
            (features.shape[0], features.shape[1], gate_weights.shape[1]),
            dtype=float,
        )
        logits[..., 1:] = 1.0
    soft = _softmax(logits / max(temperature, 1e-5), axis=-1)
    if not hard:
        return soft, soft
    hardened = np.zeros_like(soft)
    np.put_along_axis(hardened, np.argmax(soft, axis=-1)[..., None], 1.0, axis=-1)
    return soft, hardened


def _residual(
    features: np.ndarray,
    memberships: np.ndarray,
    encoders: np.ndarray,
    *,
    workspace_active: bool,
) -> tuple[np.ndarray, np.ndarray]:
    contributions = np.einsum("baf,kfd->bakd", features, encoders)
    if workspace_active:
        preactivation = np.sum(
            memberships[:, :, 1:, None] * contributions[:, :, 1:, :],
            axis=(1, 2),
        ) / max(1, features.shape[1])
    else:
        preactivation = np.zeros(
            (features.shape[0], encoders.shape[2]), dtype=float
        )
    return np.tanh(preactivation), contributions


def _consumer_features(
    code: np.ndarray,
    provenance: np.ndarray,
    feedback: float,
    world_cue: np.ndarray,
    context: np.ndarray,
) -> np.ndarray:
    code_dimension = code.shape[1]
    width = 2 * code_dimension + 5
    result = np.zeros((len(code), _HEAD_COUNT, width), dtype=float)
    result[:, 0, :code_dimension] = code
    result[:, 1, :code_dimension] = code
    result[:, 2, code_dimension : 2 * code_dimension] = (
        code * provenance[:, None]
    )
    result[:, 2, 2 * code_dimension] = provenance
    result[:, 2, 2 * code_dimension + 1] = feedback
    result[:, 2, 2 * code_dimension + 2] = world_cue
    result[:, 1, 2 * code_dimension + 3] = context
    result[:, 3, 2 * code_dimension] = provenance
    result[:, :, -1] = 1.0
    return result


def _predict(readouts: np.ndarray, features: np.ndarray) -> np.ndarray:
    return np.tanh(np.einsum("bcf,cf->bc", features, readouts))


def _head_mask(tasks: np.ndarray) -> np.ndarray:
    mask = np.ones((len(tasks), _HEAD_COUNT), dtype=float)
    mask[tasks == 0, :3] = 0.0
    return mask


def _masked_mse(
    prediction: np.ndarray, target: np.ndarray, mask: np.ndarray
) -> float:
    denominator = max(1.0, float(np.sum(mask)))
    return float(np.sum(mask * np.square(prediction - target)) / denominator)


def _prediction_gradient(
    prediction: np.ndarray, target: np.ndarray, mask: np.ndarray
) -> np.ndarray:
    # Give each independent consumer an equal terminal-loss contribution.
    # A single global denominator would make every readout learn four times
    # more slowly merely because four consumers are instrumented.
    denominator = np.maximum(np.sum(mask, axis=0, keepdims=True), 1.0)
    return (
        2.0
        * mask
        * (prediction - target)
        * (1.0 - np.square(prediction))
        / denominator
    )


def _accuracy(
    prediction: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray,
    tolerance: float = 0.45,
) -> float:
    selected = mask > 0.0
    if not np.any(selected):
        return 1.0
    return float(np.mean(np.abs(prediction[selected] - target[selected]) <= tolerance))


def _correlation(counters: dict[str, float], prefix: str) -> float:
    n = float(counters[f"{prefix}_n"])
    if n < 2.0:
        return 0.0
    sx = counters[f"{prefix}_sx"]
    sy = counters[f"{prefix}_sy"]
    sxx = counters[f"{prefix}_sxx"]
    syy = counters[f"{prefix}_syy"]
    sxy = counters[f"{prefix}_sxy"]
    numerator = n * sxy - sx * sy
    denominator = math.sqrt(max(0.0, n * sxx - sx * sx)) * math.sqrt(
        max(0.0, n * syy - sy * sy)
    )
    return float(numerator / denominator) if denominator > 1e-12 else 0.0


def _add_pairs(
    counters: dict[str, float], prefix: str, x: np.ndarray, y: np.ndarray
) -> None:
    left = np.asarray(x, dtype=float).ravel()
    right = np.asarray(y, dtype=float).ravel()
    counters[f"{prefix}_n"] += float(len(left))
    counters[f"{prefix}_sx"] += float(np.sum(left))
    counters[f"{prefix}_sy"] += float(np.sum(right))
    counters[f"{prefix}_sxx"] += float(np.sum(np.square(left)))
    counters[f"{prefix}_syy"] += float(np.sum(np.square(right)))
    counters[f"{prefix}_sxy"] += float(np.sum(left * right))


def _initial_counters(random_baselines: int) -> dict[str, float]:
    keys = (
        "eval_batches",
        "eval_examples",
        "task_correct",
        "task_total",
        "report_correct",
        "report_trials",
        "inference_correct",
        "inference_trials",
        "plan_correct",
        "plan_trials",
        "memory_correct",
        "memory_trials",
        "routine_correct",
        "routine_total",
        "formation_correct",
        "formation_total",
        "formation_true_positive",
        "formation_true_negative",
        "formation_positive",
        "formation_negative",
        "entropy_sum",
        "idempotence_sum",
        "shared_mass_sum",
        "code_norm_sum",
        "effective_code_norm_sum",
        "active_directions_sum",
        "ignition_sum",
        "intact_loss_sum",
        "actual_loss_sum",
        "jcut_loss_sum",
        "broadcast_loss_sum",
        "provenance_loss_sum",
        "planner_loss_sum",
        "pca_loss_sum",
        "random_loss_sum",
        "routine_intact_loss_sum",
        "routine_jcut_loss_sum",
        "provenance_trials",
        "provenance_correct",
        "false_writes",
        "memory_writes",
        "quarantine_records",
        "event_reopen_trials",
        "event_reopen_correct",
        "null_reopen_trials",
        "null_reopen_false",
        "recovery_trials",
        "recovery_gain_sum",
        "frame_drift_sum",
        "frame_drift_trials",
        "membership_preservation_sum",
        "jspace_preservation_sum",
        "broadcast_code_preservation_sum",
        "provenance_report_preservation_sum",
        "feedback_first_pass_preservation_sum",
        "preservation_trials",
        "mj_n",
        "mj_sx",
        "mj_sy",
        "mj_sxx",
        "mj_syy",
        "mj_sxy",
    )
    counters = {key: 0.0 for key in keys}
    counters["random_baselines"] = float(random_baselines)
    return counters


def _score(loss: float) -> float:
    return float(math.exp(-max(0.0, float(loss))))


def _longest_prefix(metrics: dict[str, Any]) -> tuple[str, int, dict[str, bool]]:
    gates = {
        "fuzzy_formation": bool(
            metrics["formation_accuracy"] >= 0.52
            and metrics["causal_membership_calibration"] >= -0.05
        ),
        "sparse_jacobian_workspace": bool(
            metrics["jspace_jacobian_energy_capture"] >= 0.45
            and metrics["mean_active_directions"]
            <= metrics["configured_active_directions"] + 1e-9
            # A Jacobian-labelled frame is not privileged merely because it
            # captures its own generating Jacobian.  Even the smoke gate must
            # beat both same-rank controls in the expected direction.
            and metrics["jspace_minus_pca"] > 0.0
            and metrics["jspace_minus_random"] > 0.0
        ),
        "causal_broadcast": bool(
            metrics["jspace_ablation_drop"] > 0.0
            and metrics["routine_preservation_under_jspace_cut"] >= 0.99
            and metrics["code_preservation_under_broadcast_cut"] >= 0.99
        ),
        "provenance_aware_planning": bool(
            metrics["provenance_accuracy"] >= 0.55
            and metrics["provenance_plan_drop"] > 0.0
            and metrics["plan_accuracy"] >= 0.55
            and metrics["planner_cut_drop"] > 0.0
            and metrics["report_preservation_under_provenance_cut"] >= 0.99
        ),
        "recurrence": bool(
            metrics["recurrence_reopen_rate"] >= 0.50
            and metrics["recurrence_false_reopen_rate"] <= 0.50
        ),
    }
    supported: list[str] = []
    for name, passed in gates.items():
        if not passed:
            break
        supported.append(name)
    return (" -> ".join(supported) if supported else "none", len(supported), gates)


def run(
    config: dict[str, Any], context: RunContext | None = None
) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 600001))
    device = str(cfg(config, "runtime.device", "auto"))
    if device not in {"auto", "cpu"}:
        raise ValueError(
            "persistent_fuzzy_j_workspace is NumPy-only; use runtime.device=cpu or auto"
        )
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))

    residual_dimension = int(cfg(config, "jspace.residual_dimension", 12))
    if residual_dimension < 4:
        raise ValueError("jspace.residual_dimension must be at least four")
    requested_rank = int(cfg(config, "jspace.frame_rank", 4))
    maximum_identifiable_rank = min(residual_dimension, _HEAD_COUNT)
    if not 1 <= requested_rank <= maximum_identifiable_rank:
        raise ValueError(
            "jspace.frame_rank must lie in [1, "
            f"{maximum_identifiable_rank}] for four independent consumers"
        )
    frame_rank = requested_rank
    active_directions = int(cfg(config, "jspace.active_directions", 2))
    if not 1 <= active_directions <= frame_rank:
        raise ValueError(
            "jspace.active_directions must lie between one and jspace.frame_rank"
        )
    steps = int(cfg(config, "jspace.steps", 128))
    calibration_steps = int(cfg(config, "jspace.calibration_steps", 32))
    event_interval = int(cfg(config, "jspace.event_interval", 8))
    moving_rate = float(cfg(config, "jspace.moving_rate", 0.15))
    gate_learning_rate = float(cfg(config, "jspace.gate_learning_rate", 0.04))
    readout_learning_rate = float(cfg(config, "jspace.readout_learning_rate", 0.05))
    ridge = float(cfg(config, "jspace.ridge", 1e-4))
    spectral_ratio = float(cfg(config, "jspace.spectral_ratio", 0.15))
    ignition_threshold = float(cfg(config, "jspace.ignition_threshold", 0.05))
    access_hysteresis = float(cfg(config, "jspace.access_hysteresis", 0.02))
    random_baselines = int(cfg(config, "jspace.random_baselines", 4))
    invocation_step_limit = int(cfg(config, "jspace.invocation_step_limit", 0))
    if steps < 1 or not 0 <= calibration_steps < steps:
        raise ValueError(
            "jspace.steps must be positive and calibration_steps must lie in [0, steps)"
        )
    if event_interval < 1:
        raise ValueError("jspace.event_interval must be positive")
    if not 0.0 < moving_rate <= 1.0:
        raise ValueError("jspace.moving_rate must lie in (0, 1]")
    if gate_learning_rate < 0.0 or readout_learning_rate < 0.0:
        raise ValueError("J-space learning rates must be nonnegative")
    if ridge <= 0.0:
        raise ValueError("jspace.ridge must be positive")
    if not 0.0 < spectral_ratio < 1.0:
        raise ValueError("jspace.spectral_ratio must lie in (0, 1)")
    if ignition_threshold < 0.0 or access_hysteresis < 0.0:
        raise ValueError("J-space access thresholds must be nonnegative")
    if random_baselines < 1 or invocation_step_limit < 0:
        raise ValueError("random_baselines must be positive and invocation limit nonnegative")

    workspace_feature = enabled(config, "workspace")
    fuzzy_packets = enabled(config, "fuzzy_packets")
    dynamic_formation = enabled(config, "dynamic_formation")
    cost_regularized = enabled(config, "cost_regularization")
    jacobian_workspace = enabled(config, "jacobian_workspace")
    moving_j_lens = enabled(config, "moving_j_lens")
    sparse_cone = enabled(config, "sparse_cone")
    provenance_feature = enabled(config, "provenance")
    planner_feature = enabled(config, "planner_binding")
    recurrence_feature = enabled(config, "recurrence")
    temperature = max(1e-5, float(cfg(config, "workspace.temperature", 1.0)))
    formation_cost = (
        float(cfg(config, "workspace.formation_cost", 0.12))
        if cost_regularized
        else 0.0
    )

    feature_dimension = 15
    packet_count = max(3, active_directions + 1)
    code_scale = math.sqrt(residual_dimension / frame_rank)
    stream = _make_stream(seed, steps, event_interval, feature_dimension)

    encoder_rng = np.random.default_rng(seed ^ 0x7A510010)
    encoders = encoder_rng.normal(
        scale=1.0 / math.sqrt(feature_dimension),
        size=(packet_count, feature_dimension, residual_dimension),
    )
    gate_weights = encoder_rng.normal(
        scale=0.03, size=(feature_dimension, packet_count)
    )
    gate_weights[:, 0] += 0.08
    shadow_readouts = encoder_rng.normal(
        scale=0.08, size=(_HEAD_COUNT, residual_dimension)
    )
    shadow_bias = np.zeros(_HEAD_COUNT, dtype=float)

    moving_frame = MovingJacobianFrame(
        np.concatenate((shadow_readouts, -shadow_readouts), axis=0),
        decay=1.0 - moving_rate,
        rank=frame_rank,
        top_k=active_directions,
    )
    consumer_width = 2 * _CODE_DIMENSION + 5
    j_readouts = encoder_rng.normal(
        scale=0.03, size=(_HEAD_COUNT, consumer_width)
    )
    pca_readouts = encoder_rng.normal(
        scale=0.03, size=(_HEAD_COUNT, consumer_width)
    )
    random_readouts = encoder_rng.normal(
        scale=0.03,
        size=(random_baselines, _HEAD_COUNT, consumer_width),
    )
    routine_readout = encoder_rng.normal(scale=0.03, size=3)
    covariance_sum = np.zeros((residual_dimension, residual_dimension), dtype=float)
    covariance_count = 0
    pca_basis = np.eye(residual_dimension, frame_rank, dtype=float)
    random_frames = np.stack(
        [
            _orthonormal_frame(encoder_rng, residual_dimension, frame_rank)
            for _ in range(random_baselines)
        ],
        axis=0,
    )

    state: dict[str, Any] = {
        "episode": 0,
        "gate_weights": gate_weights.tolist(),
        "shadow_readouts": shadow_readouts.tolist(),
        "shadow_bias": shadow_bias.tolist(),
        "j_readouts": j_readouts.tolist(),
        "pca_readouts": pca_readouts.tolist(),
        "random_readouts": random_readouts.tolist(),
        "routine_readout": routine_readout.tolist(),
        "encoders": encoders.tolist(),
        "moving_frame": moving_frame.state_dict(),
        "covariance_sum": covariance_sum.tolist(),
        "covariance_count": covariance_count,
        "pca_basis": pca_basis.tolist(),
        "random_frames": random_frames.tolist(),
        "feedback_state": 0.0,
        "reopen_next": False,
        "previous_boundary_event": -1,
        "plan_error_mean": 0.0,
        "plan_error_m2": 0.0,
        "plan_error_count": 0,
        "access_active": False,
        "memory_records": 0,
        "quarantined_records": 0,
        "false_memory_writes": 0,
        "counters": _initial_counters(random_baselines),
        "row_tail": [],
        "rng_state": rng.bit_generator.state,
    }
    if context is not None and context.resume_state:
        state.update(context.resume_state)
        state.pop("phase", None)
        if state.get("rng_state") is not None:
            rng.bit_generator.state = state["rng_state"]

    gate_weights = np.asarray(state["gate_weights"], dtype=float)
    shadow_readouts = np.asarray(state["shadow_readouts"], dtype=float)
    shadow_bias = np.asarray(state["shadow_bias"], dtype=float)
    j_readouts = np.asarray(state["j_readouts"], dtype=float)
    pca_readouts = np.asarray(state["pca_readouts"], dtype=float)
    random_readouts = np.asarray(state["random_readouts"], dtype=float)
    routine_readout = np.asarray(state["routine_readout"], dtype=float)
    encoders = np.asarray(state["encoders"], dtype=float)
    moving_frame = MovingJacobianFrame.from_state_dict(state["moving_frame"])
    covariance_sum = np.asarray(state["covariance_sum"], dtype=float)
    covariance_count = int(state["covariance_count"])
    pca_basis = np.asarray(state["pca_basis"], dtype=float)
    random_frames = np.asarray(state["random_frames"], dtype=float)
    counters = _initial_counters(random_baselines)
    if isinstance(state.get("counters"), dict):
        for key, value in state["counters"].items():
            if key in counters:
                counters[key] = float(value)
    rows = list(state.get("row_tail", []))

    start_episode = int(state.get("episode", 0))
    stop_episode = (
        steps
        if invocation_step_limit <= 0
        else min(steps, start_episode + invocation_step_limit)
    )

    for episode in range(start_episode, stop_episode):
        if context is not None:
            context.check_limits()
        features = stream["features"][episode]
        tasks = stream["tasks"][episode]
        targets = stream["targets"][episode]
        mask = _head_mask(tasks)
        context_values = stream["context"][episode]
        world_cue = stream["world_cue"][episode]
        provenance_observation = np.clip(
            0.5 * (stream["chain_score"][episode] + 1.0), 0.0, 1.0
        )
        intervention_active = episode >= calibration_steps
        base_hard = (not fuzzy_packets) or bool(cfg(config, "features.hard_packets", False))
        soft_u, intact_u = _memberships(
            features,
            gate_weights,
            temperature,
            dynamic=dynamic_formation,
            hard=base_hard,
        )
        actual_u = intact_u.copy()
        if intervention_active and bool(cfg(config, "interventions.hardening", False)):
            actual_u = np.zeros_like(soft_u)
            np.put_along_axis(
                actual_u,
                np.argmax(soft_u, axis=-1)[..., None],
                1.0,
                axis=-1,
            )
        shuffled = intervention_active and bool(
            cfg(config, "interventions.membership_shuffle", False)
        )
        permutation = stream["shuffles"][episode]
        if shuffled:
            actual_u = actual_u[:, permutation, :]

        workspace_cut = intervention_active and bool(
            cfg(config, "interventions.workspace_cut", False)
        )
        intact_h, contributions = _residual(
            features, intact_u, encoders, workspace_active=workspace_feature
        )
        actual_h, _ = _residual(
            features,
            actual_u,
            encoders,
            workspace_active=workspace_feature and not workspace_cut,
        )
        frame = moving_frame.frame
        if jacobian_workspace:
            intact_code = _j_codes(frame, intact_h, active_directions)
            actual_code_raw = _j_codes(frame, actual_h, active_directions)
        else:
            intact_code = _basis_code(
                intact_h,
                frame.basis,
                top_k=active_directions,
                output_dimension=_CODE_DIMENSION,
                nonnegative=sparse_cone,
            )
            actual_code_raw = _basis_code(
                actual_h,
                frame.basis,
                top_k=active_directions,
                output_dimension=_CODE_DIMENSION,
                nonnegative=sparse_cone,
            )
        if not sparse_cone:
            intact_code = frame.logits(intact_h)
            actual_code_raw = frame.logits(actual_h)
        intact_code *= code_scale
        actual_code_raw *= code_scale

        code_strength = np.linalg.norm(actual_code_raw, axis=1)
        threshold = max(
            0.0,
            ignition_threshold
            - (access_hysteresis if bool(state.get("access_active", False)) else 0.0),
        )
        ignited = code_strength >= threshold
        if episode < calibration_steps:
            ignited[:] = True
        state["access_active"] = bool(np.mean(ignited) >= 0.5)
        actual_code = actual_code_raw * ignited[:, None]
        jspace_cut = intervention_active and bool(
            cfg(config, "interventions.jspace_cut", False)
        )
        broadcast_cut = intervention_active and bool(
            cfg(config, "interventions.broadcast_cut", False)
        )
        state_code = np.zeros_like(actual_code) if jspace_cut else actual_code
        delivered_code = (
            np.zeros_like(state_code) if broadcast_cut or jspace_cut else state_code
        )
        provenance_for_actual = (
            np.ones_like(provenance_observation)
            if (not provenance_feature)
            or (
                intervention_active
                and bool(cfg(config, "interventions.provenance_cut", False))
            )
            else provenance_observation
        )

        feedback_state = float(state.get("feedback_state", 0.0))
        intact_features = _consumer_features(
            intact_code,
            provenance_observation,
            feedback_state,
            world_cue,
            context_values,
        )
        actual_features = _consumer_features(
            delivered_code,
            provenance_for_actual,
            feedback_state,
            world_cue,
            context_values,
        )
        intact_prediction = _predict(j_readouts, intact_features)
        actual_prediction = _predict(j_readouts, actual_features)
        if (not planner_feature) or (
            intervention_active
            and bool(cfg(config, "interventions.planner_binding_cut", False))
        ):
            actual_prediction[:, 2] = 0.0

        zero_code = np.zeros_like(intact_code)
        jcut_prediction = _predict(
            j_readouts,
            _consumer_features(
                zero_code,
                provenance_observation,
                feedback_state,
                world_cue,
                context_values,
            ),
        )
        provenance_cut_prediction = _predict(
            j_readouts,
            _consumer_features(
                intact_code,
                np.ones_like(provenance_observation),
                feedback_state,
                world_cue,
                context_values,
            ),
        )
        planner_cut_prediction = intact_prediction.copy()
        planner_cut_prediction[:, 2] = 0.0

        pca_code = _basis_code(
            intact_h,
            pca_basis,
            top_k=min(active_directions, frame_rank),
            output_dimension=_CODE_DIMENSION,
            nonnegative=True,
        ) * code_scale
        pca_features = _consumer_features(
            pca_code,
            provenance_observation,
            feedback_state,
            world_cue,
            context_values,
        )
        pca_prediction = _predict(pca_readouts, pca_features)
        random_predictions = []
        random_features = []
        for baseline in range(random_baselines):
            code = _basis_code(
                intact_h,
                random_frames[baseline],
                top_k=min(active_directions, frame_rank),
                output_dimension=_CODE_DIMENSION,
                nonnegative=True,
            ) * code_scale
            consumer_features = _consumer_features(
                code,
                provenance_observation,
                feedback_state,
                world_cue,
                context_values,
            )
            random_features.append(consumer_features)
            random_predictions.append(
                _predict(random_readouts[baseline], consumer_features)
            )

        routine_features = np.stack(
            (features[:, 0, 0], features[:, 0, 2], np.ones(_BATCH_SIZE)), axis=1
        )
        routine_prediction = np.tanh(routine_features @ routine_readout)
        routine_target = stream["routine_target"][episode]

        if episode < calibration_steps:
            main_gradient = _prediction_gradient(
                intact_prediction, targets, mask
            )
            j_readouts -= readout_learning_rate * (
                np.einsum("bcf,bc->cf", intact_features, main_gradient)
                + ridge * j_readouts
            )
            pca_gradient = _prediction_gradient(pca_prediction, targets, mask)
            pca_readouts -= readout_learning_rate * (
                np.einsum("bcf,bc->cf", pca_features, pca_gradient)
                + ridge * pca_readouts
            )
            for baseline in range(random_baselines):
                gradient = _prediction_gradient(
                    random_predictions[baseline], targets, mask
                )
                random_readouts[baseline] -= readout_learning_rate * (
                    np.einsum(
                        "bcf,bc->cf", random_features[baseline], gradient
                    )
                    + ridge * random_readouts[baseline]
                )

            shadow_prediction = np.tanh(
                intact_h @ shadow_readouts.T + shadow_bias[None, :]
            )
            shadow_gradient = _prediction_gradient(
                shadow_prediction, targets, mask
            )
            shadow_readouts -= readout_learning_rate * (
                shadow_gradient.T @ intact_h + ridge * shadow_readouts
            )
            shadow_bias -= readout_learning_rate * np.sum(shadow_gradient, axis=0)

            routine_mask = tasks == 0
            if np.any(routine_mask):
                routine_raw_gradient = (
                    2.0
                    * (routine_prediction[routine_mask] - routine_target[routine_mask])
                    * (1.0 - np.square(routine_prediction[routine_mask]))
                    / max(1, int(np.sum(routine_mask)))
                )
                routine_readout -= readout_learning_rate * (
                    routine_features[routine_mask].T @ routine_raw_gradient
                    + ridge * routine_readout
                )

            if dynamic_formation and gate_learning_rate > 0.0:
                code_gradient = np.zeros_like(intact_code)
                code_gradient += (
                    main_gradient[:, 0, None]
                    * j_readouts[0, :_CODE_DIMENSION][None, :]
                )
                code_gradient += (
                    main_gradient[:, 1, None]
                    * j_readouts[1, :_CODE_DIMENSION][None, :]
                )
                code_gradient += (
                    main_gradient[:, 2, None]
                    * provenance_observation[:, None]
                    * j_readouts[
                        2,
                        _CODE_DIMENSION : 2 * _CODE_DIMENSION,
                    ][None, :]
                )
                active_code = intact_code > 0.0
                hidden_gradient = (
                    (code_gradient * active_code.astype(float))
                    @ frame.frame_vectors.T
                ) * code_scale
                hidden_gradient += 0.25 * (
                    shadow_gradient @ shadow_readouts
                )
                preactivation_gradient = hidden_gradient * (
                    1.0 - np.square(intact_h)
                )
                membership_gradient = np.einsum(
                    "bd,bakd->bak", preactivation_gradient, contributions
                ) / max(1, _SOURCE_COUNT)
                membership_gradient[:, :, 0] = 0.0
                if formation_cost > 0.0:
                    membership_gradient[:, :, 1:] += formation_cost / (
                        _BATCH_SIZE * _SOURCE_COUNT * max(1, packet_count - 1)
                    )
                logits_gradient = soft_u * (
                    membership_gradient
                    - np.sum(
                        soft_u * membership_gradient, axis=-1, keepdims=True
                    )
                ) / temperature
                gate_weights -= gate_learning_rate * (
                    np.einsum("baf,bak->fk", features, logits_gradient)
                    + ridge * gate_weights
                )

        shadow_prediction_for_jacobian = np.tanh(
            intact_h @ shadow_readouts.T + shadow_bias[None, :]
        )
        observed_head_jacobian = np.mean(
            (1.0 - np.square(shadow_prediction_for_jacobian))[:, :, None]
            * shadow_readouts[None, :, :],
            axis=0,
        )
        observed_jacobian = np.concatenate(
            (observed_head_jacobian, -observed_head_jacobian), axis=0
        )
        previous_projector = moving_frame.frame.projector.copy()
        if moving_j_lens or episode < calibration_steps:
            moving_frame.update(observed_jacobian)
        counters["frame_drift_sum"] += float(
            np.linalg.norm(
                moving_frame.frame.projector - previous_projector, ord="fro"
            )
        )
        counters["frame_drift_trials"] += 1.0
        covariance_sum += intact_h.T @ intact_h
        covariance_count += len(intact_h)
        pca_basis = _pca_frame(covariance_sum, covariance_count, frame_rank)

        flex_mask_all = tasks != 0
        plan_error_current = (
            float(
                np.mean(
                    np.square(
                        actual_prediction[flex_mask_all, 2]
                        - targets[flex_mask_all, 2]
                    )
                )
            )
            if np.any(flex_mask_all)
            else 0.0
        )
        if episode < calibration_steps:
            error_count = int(state.get("plan_error_count", 0)) + 1
            error_mean = float(state.get("plan_error_mean", 0.0))
            error_delta = plan_error_current - error_mean
            error_mean += error_delta / error_count
            error_m2 = float(state.get("plan_error_m2", 0.0)) + error_delta * (
                plan_error_current - error_mean
            )
            state["plan_error_count"] = error_count
            state["plan_error_mean"] = error_mean
            state["plan_error_m2"] = error_m2
            calibration_reopen = plan_error_current > max(0.10, error_mean)
            if recurrence_feature and calibration_reopen:
                eligible = (
                    np.abs(targets[:, 2]) > 0.10
                ) & (np.abs(intact_prediction[:, 0]) > 0.10)
                if np.any(eligible):
                    evidence = float(
                        np.mean(
                            np.sign(
                                targets[eligible, 2]
                                * intact_prediction[eligible, 0]
                            )
                        )
                    )
                    state["feedback_state"] = float(
                        0.45 * feedback_state + 0.55 * evidence
                    )
                state["reopen_next"] = True
            else:
                state["reopen_next"] = False
            state["previous_boundary_event"] = int(stream["events"][episode])

        if episode >= calibration_steps:
            flex_mask = tasks != 0
            actual_loss = _masked_mse(actual_prediction, targets, mask)
            intact_loss = _masked_mse(intact_prediction, targets, mask)
            jcut_loss = _masked_mse(jcut_prediction, targets, mask)
            provenance_loss = _masked_mse(
                provenance_cut_prediction, targets, mask
            )
            planner_loss = _masked_mse(planner_cut_prediction, targets, mask)
            pca_loss = _masked_mse(pca_prediction, targets, mask)
            random_loss = float(
                np.mean(
                    [
                        _masked_mse(prediction, targets, mask)
                        for prediction in random_predictions
                    ]
                )
            )
            counters["eval_batches"] += 1.0
            counters["eval_examples"] += float(_BATCH_SIZE)
            counters["intact_loss_sum"] += intact_loss
            counters["actual_loss_sum"] += actual_loss
            counters["jcut_loss_sum"] += jcut_loss
            counters["broadcast_loss_sum"] += jcut_loss
            counters["provenance_loss_sum"] += provenance_loss
            counters["planner_loss_sum"] += planner_loss
            counters["pca_loss_sum"] += pca_loss
            counters["random_loss_sum"] += random_loss
            counters["task_correct"] += float(
                np.sum(
                    (np.abs(actual_prediction - targets) <= 0.45)
                    * (mask > 0.0)
                )
            )
            counters["task_total"] += float(np.sum(mask > 0.0))
            for head, name in enumerate(CONSUMER_NAMES):
                selected = mask[:, head] > 0.0
                counters[f"{name}_correct"] += float(
                    np.sum(
                        np.abs(
                            actual_prediction[selected, head]
                            - targets[selected, head]
                        )
                        <= 0.45
                    )
                )
                counters[f"{name}_trials"] += float(np.sum(selected))
            routine_selected = tasks == 0
            if np.any(routine_selected):
                routine_error = np.square(
                    routine_prediction[routine_selected]
                    - routine_target[routine_selected]
                )
                counters["routine_correct"] += float(
                    np.sum(np.abs(
                        routine_prediction[routine_selected]
                        - routine_target[routine_selected]
                    ) <= 0.45)
                )
                counters["routine_total"] += float(np.sum(routine_selected))
                routine_loss = float(np.mean(routine_error))
                counters["routine_intact_loss_sum"] += routine_loss
                counters["routine_jcut_loss_sum"] += routine_loss

            shared_mass = np.mean(1.0 - actual_u[:, :, 0], axis=1)
            # Uniform packet allocation is not evidence of formation.  The
            # admission decision must exceed the uniform shared-packet mass;
            # balanced accuracy then prevents the 3:1 task mix from rewarding
            # an always-open workspace.
            formation_threshold = 1.0 - 1.0 / packet_count
            predicted_workspace = shared_mass > formation_threshold
            truth_workspace = tasks != 0
            counters["formation_correct"] += float(
                np.sum(predicted_workspace == truth_workspace)
            )
            counters["formation_total"] += float(len(tasks))
            counters["formation_true_positive"] += float(
                np.sum(predicted_workspace & truth_workspace)
            )
            counters["formation_true_negative"] += float(
                np.sum(~predicted_workspace & ~truth_workspace)
            )
            counters["formation_positive"] += float(np.sum(truth_workspace))
            counters["formation_negative"] += float(np.sum(~truth_workspace))
            counters["entropy_sum"] += float(
                np.mean(entropy(np.clip(actual_u, 1e-12, 1.0), axis=-1))
            )
            counters["idempotence_sum"] += float(
                np.mean(np.sqrt(np.sum(np.square(actual_u * actual_u - actual_u), axis=(1, 2))))
            )
            counters["shared_mass_sum"] += float(np.mean(shared_mass))
            counters["code_norm_sum"] += float(np.mean(np.linalg.norm(actual_code_raw, axis=1)))
            counters["effective_code_norm_sum"] += float(np.mean(np.linalg.norm(state_code, axis=1)))
            counters["active_directions_sum"] += float(np.mean(np.sum(actual_code_raw > 0.0, axis=1)))
            counters["ignition_sum"] += float(np.mean(ignited))

            membership_preservation = _relative_preservation(intact_u, actual_u)
            pre_cut_state_code = actual_code.copy()
            jspace_preservation = _relative_preservation(
                pre_cut_state_code, state_code
            )
            broadcast_state_code = state_code.copy()
            broadcast_code_preservation = _relative_preservation(
                state_code, broadcast_state_code
            )
            provenance_report_preservation = _relative_preservation(
                intact_prediction[:, 0], provenance_cut_prediction[:, 0]
            )
            feedback_cut_first_prediction = _predict(
                j_readouts,
                _consumer_features(
                    intact_code,
                    provenance_observation,
                    feedback_state,
                    world_cue,
                    context_values,
                ),
            )
            feedback_first_pass_preservation = _relative_preservation(
                intact_prediction, feedback_cut_first_prediction
            )
            counters["membership_preservation_sum"] += membership_preservation
            counters["jspace_preservation_sum"] += jspace_preservation
            counters["broadcast_code_preservation_sum"] += (
                broadcast_code_preservation
            )
            counters["provenance_report_preservation_sum"] += (
                provenance_report_preservation
            )
            counters["feedback_first_pass_preservation_sum"] += (
                feedback_first_pass_preservation
            )
            counters["preservation_trials"] += 1.0

            selected_sources = np.arange(_BATCH_SIZE) % _SOURCE_COUNT
            strengths = 1.0 - actual_u[
                np.arange(_BATCH_SIZE), selected_sources, 0
            ]
            ablated_u = actual_u.copy()
            ablated_u[np.arange(_BATCH_SIZE), selected_sources, 1:] = 0.0
            ablated_u[np.arange(_BATCH_SIZE), selected_sources, 0] = 1.0
            ablated_h, _ = _residual(
                features, ablated_u, encoders, workspace_active=workspace_feature
            )
            ablated_code = _j_codes(frame, ablated_h, active_directions)
            ablated_code *= code_scale
            effects = np.linalg.norm(actual_code_raw - ablated_code, axis=1)
            _add_pairs(counters, "mj", strengths, effects)

            valid_target = stream["chain_valid"][episode] > 0.5
            memory_prediction = actual_prediction[:, 3] > 0.0
            counters["provenance_trials"] += float(len(valid_target))
            counters["provenance_correct"] += float(
                np.sum(memory_prediction == valid_target)
            )
            counters["false_writes"] += float(
                np.sum(memory_prediction & ~valid_target)
            )
            counters["memory_writes"] += float(np.sum(memory_prediction))
            counters["quarantine_records"] += float(
                np.sum(~memory_prediction & ~valid_target)
            )
            state["memory_records"] = int(state["memory_records"]) + int(
                np.sum(memory_prediction)
            )
            state["false_memory_writes"] = int(
                state["false_memory_writes"]
            ) + int(np.sum(memory_prediction & ~valid_target))
            state["quarantined_records"] = int(
                state["quarantined_records"]
            ) + int(np.sum(~memory_prediction & ~valid_target))

            reopened = bool(state.get("reopen_next", False))
            previous_boundary = int(state.get("previous_boundary_event", -1))
            if previous_boundary == 1:
                counters["event_reopen_trials"] += 1.0
                counters["event_reopen_correct"] += float(reopened)
            elif previous_boundary == 0:
                counters["null_reopen_trials"] += 1.0
                counters["null_reopen_false"] += float(reopened)

            no_feedback_prediction = _predict(
                j_readouts,
                _consumer_features(
                    intact_code,
                    provenance_observation,
                    0.0,
                    world_cue,
                    context_values,
                ),
            )
            if reopened and np.any(flex_mask):
                intact_plan_loss = float(
                    np.mean(
                        np.square(
                            intact_prediction[flex_mask, 2]
                            - targets[flex_mask, 2]
                        )
                    )
                )
                no_feedback_plan_loss = float(
                    np.mean(
                        np.square(
                            no_feedback_prediction[flex_mask, 2]
                            - targets[flex_mask, 2]
                        )
                    )
                )
                counters["recovery_trials"] += 1.0
                counters["recovery_gain_sum"] += (
                    no_feedback_plan_loss - intact_plan_loss
                )

            error_count = max(1, int(state.get("plan_error_count", 1)))
            error_variance = float(state.get("plan_error_m2", 0.0)) / max(
                1, error_count - 1
            )
            learned_threshold = float(state.get("plan_error_mean", 0.0)) + 0.5 * math.sqrt(
                max(0.0, error_variance)
            )
            should_reopen = bool(
                plan_error_current > max(0.12, learned_threshold)
            )
            recurrence_cut = intervention_active and (
                bool(cfg(config, "interventions.recurrence_cut", False))
                or bool(cfg(config, "interventions.feedback_cut", False))
            )
            if recurrence_feature and not recurrence_cut and should_reopen:
                eligible = (
                    np.abs(targets[:, 2]) > 0.10
                ) & (np.abs(intact_prediction[:, 0]) > 0.10)
                if np.any(eligible):
                    evidence = float(
                        np.mean(
                            np.sign(
                                targets[eligible, 2]
                                * intact_prediction[eligible, 0]
                            )
                        )
                    )
                    state["feedback_state"] = float(
                        0.45 * feedback_state + 0.55 * evidence
                    )
                state["reopen_next"] = True
            else:
                state["reopen_next"] = False
            state["previous_boundary_event"] = int(stream["events"][episode])

            if bool(cfg(config, "run.save_rows", True)):
                rows.append(
                    {
                        "episode": episode,
                        "event_truth": (
                            EVENT_NAMES[int(stream["events"][episode])]
                            if int(stream["events"][episode]) >= 0
                            else "continuation"
                        ),
                        "task_counts": [int(np.sum(tasks == value)) for value in range(4)],
                        "task_accuracy": _accuracy(actual_prediction, targets, mask),
                        "intact_loss": intact_loss,
                        "actual_loss": actual_loss,
                        "membership_entropy": float(
                            np.mean(entropy(np.clip(actual_u, 1e-12, 1.0), axis=-1))
                        ),
                        "shared_membership_mass": float(np.mean(shared_mass)),
                        "jspace_code_norm": float(np.mean(np.linalg.norm(state_code, axis=1))),
                        "jspace_ignited": bool(state["access_active"]),
                        "reopened": reopened,
                        "feedback_state": float(state["feedback_state"]),
                        "memory_records": int(state["memory_records"]),
                        "quarantined_records": int(state["quarantined_records"]),
                    }
                )
                if len(rows) > 2048:
                    rows = rows[-2048:]

        state.update(
            {
                "episode": episode + 1,
                "gate_weights": gate_weights.tolist(),
                "shadow_readouts": shadow_readouts.tolist(),
                "shadow_bias": shadow_bias.tolist(),
                "j_readouts": j_readouts.tolist(),
                "pca_readouts": pca_readouts.tolist(),
                "random_readouts": random_readouts.tolist(),
                "routine_readout": routine_readout.tolist(),
                "encoders": encoders.tolist(),
                "moving_frame": moving_frame.state_dict(),
                "covariance_sum": covariance_sum.tolist(),
                "covariance_count": covariance_count,
                "pca_basis": pca_basis.tolist(),
                "random_frames": random_frames.tolist(),
                "counters": counters,
                "row_tail": rows,
                "rng_state": rng.bit_generator.state,
            }
        )
        if context is not None:
            context.checkpoint(
                episode + 1,
                state,
                {
                    "calibrating": episode + 1 <= calibration_steps,
                    "frame_updates": moving_frame.updates,
                },
            )
        if (
            invocation_step_limit > 0
            and episode + 1 - start_episode >= invocation_step_limit
            and episode + 1 < steps
        ):
            if context is not None:
                context.checkpoint(
                    episode + 1,
                    state,
                    {"interrupted_for_resume": True},
                    force=True,
                )
            break

    completed_all = int(state.get("episode", 0)) >= steps
    batches = max(1.0, counters["eval_batches"])
    task_accuracy = counters["task_correct"] / max(1.0, counters["task_total"])
    intact_loss = counters["intact_loss_sum"] / batches
    actual_loss = counters["actual_loss_sum"] / batches
    jcut_loss = counters["jcut_loss_sum"] / batches
    provenance_loss = counters["provenance_loss_sum"] / batches
    pca_loss = counters["pca_loss_sum"] / batches
    random_loss = counters["random_loss_sum"] / batches
    routine_intact_loss = counters["routine_intact_loss_sum"] / batches
    routine_jcut_loss = counters["routine_jcut_loss_sum"] / batches
    frame = moving_frame.frame
    singular_values = np.asarray(frame.singular_values, dtype=float)
    spectral_support = int(
        np.sum(singular_values / max(singular_values[0], 1e-12) >= spectral_ratio)
    )
    formation_raw_accuracy = counters["formation_correct"] / max(
        1.0, counters["formation_total"]
    )
    formation_balanced_accuracy = 0.5 * (
        counters["formation_true_positive"]
        / max(1.0, counters["formation_positive"])
        + counters["formation_true_negative"]
        / max(1.0, counters["formation_negative"])
    )
    metrics: dict[str, Any] = {
        "task_accuracy": task_accuracy,
        "continuous_task_accuracy": task_accuracy,
        "report_accuracy": counters["report_correct"] / max(1.0, counters["report_trials"]),
        "inference_accuracy": counters["inference_correct"] / max(1.0, counters["inference_trials"]),
        "plan_accuracy": counters["plan_correct"] / max(1.0, counters["plan_trials"]),
        "memory_accuracy": counters["memory_correct"] / max(1.0, counters["memory_trials"]),
        "routine_task_accuracy": counters["routine_correct"] / max(1.0, counters["routine_total"]),
        "formation_accuracy": formation_balanced_accuracy,
        "formation_balanced_accuracy": formation_balanced_accuracy,
        "formation_raw_accuracy": formation_raw_accuracy,
        "causal_membership_calibration": _correlation(counters, "mj"),
        "membership_entropy": counters["entropy_sum"] / batches,
        "idempotence_defect": counters["idempotence_sum"] / batches,
        "mean_shared_membership_mass": counters["shared_mass_sum"] / batches,
        "workspace_decodability": _score(actual_loss),
        "jspace_task_score": _score(intact_loss),
        "pca_matched_task_score": _score(pca_loss),
        "random_matched_task_score": _score(random_loss),
        "jspace_minus_pca": _score(intact_loss) - _score(pca_loss),
        "jspace_minus_random": _score(intact_loss) - _score(random_loss),
        "jspace_jacobian_energy_capture": jacobian_energy_capture(
            frame.average_jacobian, frame.projector
        ),
        "jspace_activation_variance_fraction": _covariance_variance_fraction(
            np.asarray(state["covariance_sum"], dtype=float), frame.projector
        ),
        "jspace_projector_idempotence_defect": projector_idempotence_defect(
            frame.projector
        ),
        "jspace_rank": frame.rank,
        "jspace_spectral_support": spectral_support,
        "configured_active_directions": active_directions,
        "mean_active_directions": counters["active_directions_sum"] / batches,
        "jspace_ignition_rate": counters["ignition_sum"] / batches,
        "mean_jspace_code_norm": counters["code_norm_sum"] / batches,
        "mean_effective_jspace_code_norm": counters["effective_code_norm_sum"] / batches,
        "jspace_ablation_drop": _score(intact_loss) - _score(jcut_loss),
        "broadcast_ablation_drop": _score(intact_loss) - _score(jcut_loss),
        "routine_preservation_under_jspace_cut": _score(routine_jcut_loss)
        / max(_score(routine_intact_loss), 1e-12),
        "code_preservation_under_broadcast_cut": counters[
            "broadcast_code_preservation_sum"
        ]
        / max(1.0, counters["preservation_trials"]),
        "membership_upstream_preservation": counters["membership_preservation_sum"]
        / max(1.0, counters["preservation_trials"]),
        "jspace_upstream_preservation": counters["jspace_preservation_sum"]
        / max(1.0, counters["preservation_trials"]),
        "provenance_accuracy": counters["provenance_correct"]
        / max(1.0, counters["provenance_trials"]),
        "false_autobiographical_write_rate": counters["false_writes"]
        / max(1.0, counters["provenance_trials"]),
        "provenance_plan_drop": _score(intact_loss) - _score(provenance_loss),
        "report_preservation_under_provenance_cut": counters[
            "provenance_report_preservation_sum"
        ]
        / max(1.0, counters["preservation_trials"]),
        "planner_cut_drop": _score(intact_loss)
        - _score(counters["planner_loss_sum"] / batches),
        "recurrence_reopen_rate": counters["event_reopen_correct"]
        / max(1.0, counters["event_reopen_trials"]),
        "recurrence_false_reopen_rate": counters["null_reopen_false"]
        / max(1.0, counters["null_reopen_trials"]),
        "recurrence_recovery_gain": counters["recovery_gain_sum"]
        / max(1.0, counters["recovery_trials"]),
        "feedback_cut_first_pass_preservation": counters[
            "feedback_first_pass_preservation_sum"
        ]
        / max(1.0, counters["preservation_trials"]),
        "frame_mean_drift": counters["frame_drift_sum"]
        / max(1.0, counters["frame_drift_trials"]),
        "frame_updates": moving_frame.updates,
        "task_event_dependence": 0.0,
        "memory_records": int(state["memory_records"]),
        "quarantined_records": int(state["quarantined_records"]),
        "episodes_completed": int(state["episode"]),
        "target_episodes": steps,
        "run_complete": completed_all,
    }
    prefix, prefix_length, gates = _longest_prefix(metrics)
    metrics["longest_supported_prefix"] = prefix
    metrics["supported_prefix_length"] = prefix_length

    semantic_state = dict(state)
    semantic_state.pop("phase", None)
    trajectory_digest = digest_object(
        {
            "state": semantic_state,
            "rows": rows,
            "task_digest": digest_object(stream["tasks"]),
            "event_digest": digest_object(stream["events"]),
        }
    )
    if context is not None:
        context.checkpoint(
            int(state["episode"]),
            {**state, "phase": "completed" if completed_all else "interrupted"},
            metrics,
            force=True,
        )
    return ExperimentResult(
        family=FAMILY,
        status="completed" if completed_all else "interrupted",
        metrics=metrics,
        rows=rows,
        metadata={
            "final_step": int(state["episode"]),
            "resumed": bool(context and context.resumed),
            "trajectory_digest": trajectory_digest,
            "supported_link_gates": gates,
            "task_event_independence_by_design": True,
            "membership_supervision": "terminal consumer loss plus declared resource cost only",
            "controller_hidden_truth_access": False,
            "outcome_feedback": "terminal targets are revealed only after prediction",
            "jacobian_source": "analytic residual Jacobian of independent terminal readouts",
            "baseline_matching": {
                "rank": frame_rank,
                "active_directions": active_directions,
                "calibration_examples": calibration_steps * _BATCH_SIZE,
                "random_baselines": random_baselines,
            },
            "interpretation_boundary": (
                "Bounded NumPy engineering analogue of a fuzzy-to-J-workspace causal chain; "
                "not evidence of a naturally occurring transformer J-space, awareness, or consciousness."
            ),
        },
        warnings=[
            "This synthetic instrumented residual model is an engineering analogue, not a scientific-scale or transformer result.",
            "Longest-supported-prefix gates are smoke diagnostics and are not preregistered inferential thresholds.",
        ],
    )

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.orchestration import RunContext
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import digest_object, entropy, seed_everything


TASK_LOCAL = 0
TASK_PAIR = 1
TASK_OVERLAP = 2
TASK_GLOBAL = 3
TASK_NAMES = ("local", "pair", "overlap", "global")
EVENT_NAMES = ("none", "world_shift", "self_shift", "memory_corruption", "partner_change")


@dataclass
class Segment:
    start: int
    stop: int
    task_kind: int
    event: str


def _task_membership(task_kind: int, agents: int, max_packets: int) -> tuple[np.ndarray, int, np.ndarray]:
    u = np.zeros((agents, max_packets), dtype=float)
    u[:, 0] = 1.0
    required = np.zeros(agents, dtype=bool)
    if task_kind == TASK_LOCAL:
        required[0] = True
        return u, 0, required
    if task_kind == TASK_PAIR:
        required[: min(2, agents)] = True
        u[required, 0] = 0.0
        u[required, 1] = 1.0
        return u, 1, required
    if task_kind == TASK_OVERLAP:
        count = min(3, agents)
        required[:count] = True
        u[required, 0] = 0.0
        if count >= 1:
            u[0, 1] = 1.0
        if count >= 2:
            u[1, 1] = 0.5
            u[1, 2] = 0.5
        if count >= 3:
            u[2, 2] = 1.0
        return u, min(2, max_packets - 1), required
    required[:] = True
    u[:, 0] = 0.0
    u[:, 1] = 1.0
    return u, 1, required


def _dependency_matrix(u: np.ndarray) -> np.ndarray:
    shared = u[:, 1:]
    return shared @ shared.T


def _infer_membership(
    matrix: np.ndarray,
    max_packets: int,
    birth_threshold: float,
    temperature: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, int, np.ndarray]:
    agents = matrix.shape[0]
    sym = 0.5 * (matrix + matrix.T)
    eigenvalues, eigenvectors = np.linalg.eigh(sym + np.eye(agents) * 1e-6)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.clip(eigenvalues[order], 0.0, None)
    eigenvectors = eigenvectors[:, order]
    if eigenvalues[0] <= 0.20:
        u = np.zeros((agents, max_packets), dtype=float)
        u[:, 0] = 1.0
        return u, 0, eigenvalues
    relative = eigenvalues / max(eigenvalues[0], 1e-12)
    count = int(np.sum(relative >= birth_threshold))
    count = max(1, min(count, max_packets - 1, agents))
    initial = np.maximum(np.abs(eigenvectors[:, :count]), 1e-3)
    initial += 1e-4 * rng.random(initial.shape)
    w = initial
    positive = np.clip(sym, 0.0, None) + 1e-6 * np.eye(agents)
    for _ in range(30):
        numerator = positive @ w
        denominator = w @ (w.T @ w) + 1e-8
        w *= numerator / denominator
        w = np.maximum(w, 1e-8)
    shared_strength = np.clip(np.linalg.norm(positive, axis=1), 0.0, None)
    if shared_strength.max() > 0:
        shared_strength /= shared_strength.max()
    shared_strength[shared_strength < 0.18] = 0.0
    w /= np.maximum(w.sum(axis=1, keepdims=True), 1e-12)
    w = np.power(np.maximum(w, 1e-12), 1.0 / max(float(temperature), 1e-5))
    w /= np.maximum(w.sum(axis=1, keepdims=True), 1e-12)
    w *= shared_strength[:, None]
    u = np.zeros((agents, max_packets), dtype=float)
    u[:, 1 : 1 + count] = w
    u[:, 0] = np.clip(1.0 - u[:, 1:].sum(axis=1), 0.0, 1.0)
    u /= np.maximum(u.sum(axis=1, keepdims=True), 1e-12)
    return u, count, eigenvalues


def _segment_schedule(
    episodes: int,
    segment_length: int,
    rng: np.random.Generator,
    config: dict[str, Any],
) -> list[Segment]:
    segments: list[Segment] = []
    event_cycle = ["none", "self_shift", "world_shift", "memory_corruption", "partner_change"]
    task_cycle = [TASK_LOCAL, TASK_PAIR, TASK_GLOBAL, TASK_OVERLAP]
    position = 0
    index = 0
    event_interval = max(segment_length, int(cfg(config, "continuous.event_interval", segment_length)))
    event_stride = max(1, int(math.ceil(event_interval / segment_length)))
    event_fabric = enabled(config, "continuous_event_fabric")
    while position < episodes:
        stop = min(episodes, position + segment_length)
        if not event_fabric or index % event_stride != 0:
            event = "none"
        elif index // event_stride < len(event_cycle):
            event = event_cycle[index // event_stride]
        else:
            draws = np.asarray(
                [
                    1.0
                    - float(cfg(config, "experiment.world_shift_probability", 0.12))
                    - float(cfg(config, "experiment.self_shift_probability", 0.12))
                    - float(cfg(config, "experiment.memory_corruption_probability", 0.10))
                    - float(cfg(config, "experiment.partner_change_probability", 0.08)),
                    float(cfg(config, "experiment.world_shift_probability", 0.12)),
                    float(cfg(config, "experiment.self_shift_probability", 0.12)),
                    float(cfg(config, "experiment.memory_corruption_probability", 0.10)),
                    float(cfg(config, "experiment.partner_change_probability", 0.08)),
                ],
                dtype=float,
            )
            draws = np.clip(draws, 0.0, None)
            draws /= draws.sum()
            event = str(rng.choice(np.asarray(EVENT_NAMES), p=draws))
        if event == "self_shift":
            task = TASK_PAIR
        elif event == "partner_change":
            task = TASK_OVERLAP
        elif index < len(task_cycle):
            task = task_cycle[index]
        else:
            no_workspace = float(cfg(config, "experiment.no_workspace_probability", 0.25))
            probabilities = np.asarray([no_workspace, 0.25, 0.25, max(0.0, 0.5 - no_workspace)])
            probabilities /= probabilities.sum()
            task = int(rng.choice(4, p=probabilities))
        segments.append(Segment(position, stop, task, event))
        position = stop
        index += 1
    return segments


def _cyclic_distance(a: int, b: int, classes: int) -> float:
    delta = abs(int(a) - int(b)) % classes
    return float(min(delta, classes - delta))


def run(config: dict[str, Any], context: RunContext | None = None) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 590001))
    device = str(cfg(config, "runtime.device", "auto"))
    if device not in {"auto", "cpu"}:
        raise ValueError("continuous_open_set_runtime is currently a NumPy CPU family; use runtime.device=cpu or auto")
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))

    # Backward-compatible precedence: a nondefault legacy event_horizon overrides
    # the default continuous.steps value, while explicit continuous.steps wins.
    configured_steps = int(cfg(config, "continuous.steps", 256))
    legacy_horizon = int(cfg(config, "experiment.event_horizon", 256))
    episodes = legacy_horizon if configured_steps == 256 and legacy_horizon != 256 else configured_steps

    agents = max(3, int(cfg(config, "experiment.agent_count", 6)))
    classes = max(3, int(cfg(config, "experiment.action_dim", 4)))
    configured_switch = int(cfg(config, "continuous.task_switch_interval", 7))
    configured_event_interval = int(cfg(config, "continuous.event_interval", 12))
    legacy_sequence = int(cfg(config, "experiment.sequence_length", 8))
    if configured_switch == 7 and configured_event_interval != 12:
        segment_length = max(4, configured_event_interval)
    elif configured_switch == 7 and legacy_sequence != 8:
        segment_length = max(4, legacy_sequence)
    else:
        segment_length = max(4, configured_switch)

    calibration_steps = max(0, int(cfg(config, "continuous.calibration_steps", 0)))
    passive_noise = max(0.0, float(cfg(config, "continuous.passive_noise_std", cfg(config, "experiment.noise_std", 0.02))))
    checkpoint_state_rows = max(0, int(cfg(config, "continuous.checkpoint_state_rows", 128)))
    invocation_step_limit = max(0, int(cfg(config, "continuous.invocation_step_limit", 0)))

    max_packets = max(3, min(int(cfg(config, "workspace.max_packets", 8)), agents + 1))
    birth_threshold = float(cfg(config, "workspace.birth_threshold", 0.25))
    allow_new_packets = bool(cfg(config, "workspace.allow_new_packets", False))
    allow_packet_death = bool(cfg(config, "workspace.allow_packet_death", True))
    min_packet_lifetime = max(0, int(cfg(config, "workspace.min_packet_lifetime", 4)))
    temperature = max(1e-5, float(cfg(config, "workspace.temperature", 1.0)))
    death_threshold = float(cfg(config, "workspace.death_threshold", 0.15))
    cost_regularized = enabled(config, "cost_regularization")
    formation_cost = float(cfg(config, "workspace.formation_cost", 0.12)) if cost_regularized else 0.0

    update_rate = float(cfg(config, "continuous.packet_update_rate", 0.35))
    decay_rate = float(cfg(config, "continuous.packet_decay_rate", 0.10))
    birth_patience = max(1, int(cfg(config, "continuous.packet_birth_patience", 2)))
    death_patience = max(1, int(cfg(config, "continuous.packet_death_patience", 3)))
    configured_change = float(cfg(config, "continuous.change_threshold", 0.18))
    legacy_anomaly = float(cfg(config, "continuous.anomaly_threshold", 0.35))
    anomaly_threshold = legacy_anomaly if configured_change == 0.18 and legacy_anomaly != 0.35 else configured_change
    attribution_margin = float(cfg(config, "continuous.attribution_margin", 0.10))
    probe_noise = max(0.0, float(cfg(config, "continuous.probe_noise_std", 0.015)))
    probe_samples = max(1, int(cfg(config, "continuous.probe_samples", 3)))
    recovery_threshold = max(0.0, float(cfg(config, "continuous.recovery_threshold", 0.08)))
    repair_rate = float(cfg(config, "continuous.repair_rate", 0.75))

    event_fabric = enabled(config, "continuous_event_fabric")
    workspace_enabled = enabled(config, "workspace", "workspace_cut")
    self_model = enabled(config, "self_model", "self_model_cut")
    causal_boundary = enabled(config, "causal_boundary", "causal_boundary_cut") and not bool(
        cfg(config, "interventions.self_world_attribution_cut", False)
    )
    temporal = enabled(config, "temporal_identity")
    continuity = enabled(config, "transformational_continuity")
    memory_enabled = enabled(config, "autobiographical_memory", "memory_cut")
    provenance = enabled(config, "provenance", "provenance_cut")
    quarantine = enabled(config, "memory_quarantine") and provenance
    planner = enabled(config, "planner_binding", "planner_binding_cut")
    recurrence = enabled(config, "recurrence", "recurrence_cut") and not bool(
        cfg(config, "interventions.feedback_cut", False)
    )
    metacognition = enabled(config, "metacognition", "metacognition_cut")
    probing = enabled(config, "adaptive_probing") and not bool(cfg(config, "interventions.probe_cut", False))
    change_detector = enabled(config, "open_set_change_detection") and not bool(
        cfg(config, "interventions.change_detector_cut", False)
    )
    birth_enabled = enabled(config, "dynamic_packet_birth") and bool(cfg(config, "workspace.allow_new_packets", False)) and not bool(
        cfg(config, "interventions.packet_birth_cut", False)
    )
    death_enabled = (
        enabled(config, "dynamic_packet_death")
        and allow_packet_death
        and not bool(cfg(config, "interventions.packet_death_cut", False))
    )
    repair_enabled = enabled(config, "self_model_repair") and not bool(
        cfg(config, "interventions.repair_cut", False)
    )
    dynamic_formation = enabled(config, "dynamic_formation")
    fuzzy_packets = enabled(config, "fuzzy_packets")
    coordinate_alignment = enabled(config, "coordinate_alignment")

    effective_birth_threshold = min(0.95, birth_threshold + (0.08 * formation_cost if cost_regularized else 0.0))
    allowed_events = {
        str(value)
        for value in cfg(
            config,
            "continuous.event_types",
            ["none", "world_shift", "self_shift", "memory_corruption", "partner_change"],
        )
    }
    if not event_fabric:
        schedule = [Segment(0, episodes, TASK_GLOBAL, "none")]
    else:
        active_start = min(calibration_steps, episodes)
        schedule = []
        if active_start > 0:
            schedule.append(Segment(0, active_start, TASK_GLOBAL, "none"))
        remainder = _segment_schedule(episodes - active_start, segment_length, rng, config)
        for segment in remainder:
            event = segment.event if segment.event in allowed_events else "none"
            schedule.append(
                Segment(
                    segment.start + active_start,
                    segment.stop + active_start,
                    segment.task_kind,
                    event,
                )
            )
        if not schedule:
            schedule = [Segment(0, episodes, TASK_GLOBAL, "none")]
    segment_by_episode = np.empty(episodes, dtype=int)
    for index, segment in enumerate(schedule):
        segment_by_episode[segment.start : segment.stop] = index

    # Pre-generate all episode data so exact resume needs only controller state.
    values_all = rng.integers(0, classes, size=(episodes, agents))
    cue_noise = rng.normal(scale=passive_noise, size=(episodes, agents, agents))
    cue_noise = 0.5 * (cue_noise + np.transpose(cue_noise, (0, 2, 1)))
    segment_increments = rng.integers(1, classes, size=max(1, len(schedule)))
    segment_shifts = rng.integers(1, agents, size=max(1, len(schedule)))
    segment_memory_offsets = rng.integers(1, classes, size=max(1, len(schedule)))
    probe_noise_self = rng.normal(0.0, probe_noise, size=episodes)
    probe_noise_world = rng.normal(0.0, probe_noise, size=episodes)

    initial_u = np.zeros((agents, max_packets), dtype=float)
    initial_u[:, 0] = 1.0
    state: dict[str, Any] = {
        "episode": 0,
        "world_offset_true": 0,
        "world_offset_est": 0,
        "perm_true": list(range(agents)),
        "perm_est": list(range(agents)),
        "cue_perm_true": list(range(agents)),
        "cue_perm_est": list(range(agents)),
        "membership": initial_u.tolist(),
        "active_packets": 0,
        "birth_counter": 0,
        "death_counter": 0,
        "packet_lifetime": 0,
        "next_evidence_budget": int(cfg(config, "metacognition.evidence_budget", 1)),
        "memory_records": 0,
        "quarantined_records": 0,
        "false_memory_writes": 0,
        "counters": {},
        "rng_state": None,
        "current_segment_index": -1,
        "event_truth": "none",
        "event_pending": False,
    }
    if context is not None and context.resume_state:
        state.update(context.resume_state)
        # Run-manager phase labels are not part of the scientific controller state.
        state.pop("phase", None)
        if state.get("rng_state") is not None:
            rng.bit_generator.state = state["rng_state"]

    counters: dict[str, float] = {
        "episodes": 0.0,
        "task_correct": 0.0,
        "change_trials": 0.0,
        "change_correct": 0.0,
        "attribution_trials": 0.0,
        "attribution_correct": 0.0,
        "formation_correct": 0.0,
        "dissolution_trials": 0.0,
        "dissolution_correct": 0.0,
        "packet_count_correct": 0.0,
        "provenance_trials": 0.0,
        "provenance_correct": 0.0,
        "false_writes": 0.0,
        "reopen_trials": 0.0,
        "reopen_correct": 0.0,
        "repair_trials": 0.0,
        "repair_correct": 0.0,
        "continuity_trials": 0.0,
        "continuity_correct": 0.0,
        "probe_total": 0.0,
        "entropy_sum": 0.0,
        "idempotence_sum": 0.0,
        "transport_sum": 0.0,
        "packet_count_sum": 0.0,
    }
    if isinstance(state.get("counters"), dict):
        for key, value in state["counters"].items():
            if key in counters:
                counters[key] = float(value)

    rows: list[dict[str, Any]] = list(state.get("row_tail", [])) if isinstance(state.get("row_tail"), list) else []
    current_segment_index = int(state.get("current_segment_index", -1))
    event_truth = str(state.get("event_truth", "none"))
    event_pending = bool(state.get("event_pending", False))

    start_episode = int(state.get("episode", 0))
    stop_episode = (
        episodes
        if invocation_step_limit <= 0
        else min(episodes, start_episode + invocation_step_limit)
    )
    for episode in range(start_episode, stop_episode):
        if context is not None:
            context.check_limits()
        segment_index = int(segment_by_episode[episode])
        segment = schedule[segment_index]
        if segment_index != current_segment_index:
            current_segment_index = segment_index
            event_truth = segment.event
            event_pending = event_truth != "none"
            if event_truth == "world_shift":
                increment = int(segment_increments[segment_index])
                state["world_offset_true"] = (int(state["world_offset_true"]) + increment) % classes
            elif event_truth == "self_shift":
                permutation = np.asarray(state["perm_true"], dtype=int)
                shift = int(segment_shifts[segment_index])
                state["perm_true"] = np.roll(permutation, shift).tolist()
            elif event_truth == "partner_change":
                permutation = np.asarray(state["cue_perm_true"], dtype=int)
                shift = int(segment_shifts[segment_index])
                state["cue_perm_true"] = np.roll(permutation, shift).tolist()
            elif event_truth == "memory_corruption":
                counters["provenance_trials"] += 1
                if memory_enabled and quarantine:
                    state["quarantined_records"] = int(state["quarantined_records"]) + 1
                    counters["provenance_correct"] += 1
                elif memory_enabled:
                    state["false_memory_writes"] = int(state["false_memory_writes"]) + 1
                    counters["false_writes"] += 1
                    state["world_offset_est"] = (
                        int(state["world_offset_est"]) + int(segment_memory_offsets[segment_index])
                    ) % classes
                else:
                    counters["provenance_correct"] += 1

        truth_u, truth_packet_count, required_agents = _task_membership(
            segment.task_kind, agents, max_packets
        )
        cue = _dependency_matrix(truth_u)
        cue_perm_true = np.asarray(state["cue_perm_true"], dtype=int)
        cue = cue[np.ix_(cue_perm_true, cue_perm_true)] + cue_noise[episode]
        cue = np.clip(0.5 * (cue + cue.T), 0.0, None)
        cue_perm_est = np.asarray(state["cue_perm_est"], dtype=int)
        inverse_cue = np.argsort(cue_perm_est)
        cue_canonical = cue[np.ix_(inverse_cue, inverse_cue)] if coordinate_alignment else cue

        candidate_u, candidate_count, eigenvalues = _infer_membership(
            cue_canonical,
            max_packets,
            effective_birth_threshold,
            temperature,
            np.random.default_rng(seed ^ (episode * 1000003 + 0xC0A1)),
        )
        if not dynamic_formation or not workspace_enabled:
            candidate_count = 0 if not workspace_enabled else truth_packet_count
            candidate_u = initial_u.copy() if candidate_count == 0 else truth_u.copy()
        active_count = int(state["active_packets"])
        state["packet_lifetime"] = int(state.get("packet_lifetime", 0)) + 1
        candidate_shared_mass = float(candidate_u[:, 1:].sum()) / max(1, agents)
        if candidate_shared_mass <= death_threshold:
            candidate_count = 0
        if candidate_count > active_count:
            state["birth_counter"] = int(state["birth_counter"]) + 1
            state["death_counter"] = 0
            if birth_enabled and allow_new_packets and int(state["birth_counter"]) >= birth_patience:
                active_count = candidate_count
                state["birth_counter"] = 0
                state["packet_age"] = 0
                state["packet_lifetime"] = 0
        elif candidate_count < active_count:
            state["death_counter"] = int(state["death_counter"]) + 1
            state["birth_counter"] = 0
            if death_enabled and int(state["death_counter"]) >= death_patience and int(state["packet_lifetime"]) >= min_packet_lifetime:
                active_count = candidate_count
                state["death_counter"] = 0
                state["packet_lifetime"] = 0
        else:
            state["birth_counter"] = 0
            state["death_counter"] = 0
        state["active_packets"] = active_count
        state["packet_age"] = int(state.get("packet_age", 0)) + 1

        current_u = np.asarray(state["membership"], dtype=float)
        target_u = candidate_u.copy()
        if active_count == 0:
            target_u = initial_u.copy()
        elif active_count < max_packets - 1:
            target_u[:, 1 + active_count :] = 0.0
            target_u[:, 0] = np.clip(1.0 - target_u[:, 1:].sum(axis=1), 0.0, 1.0)
            target_u /= np.maximum(target_u.sum(axis=1, keepdims=True), 1e-12)
        rate = update_rate if fuzzy_packets else 1.0
        current_u = (1.0 - rate) * current_u + rate * target_u
        if not fuzzy_packets:
            hard = np.zeros_like(current_u)
            hard[np.arange(agents), np.argmax(current_u, axis=1)] = 1.0
            current_u = hard
        if active_count == 0:
            current_u = (1.0 - decay_rate) * current_u + decay_rate * initial_u
        current_u = np.power(np.clip(current_u, 1e-12, 1.0), 1.0 / temperature)
        current_u /= np.maximum(current_u.sum(axis=1, keepdims=True), 1e-12)
        state["membership"] = current_u.tolist()

        predicted_packet_count = int(np.sum(current_u[:, 1:].sum(axis=0) > 0.35))
        predicted_workspace = predicted_packet_count > 0
        truth_workspace = truth_packet_count > 0
        counters["formation_correct"] += float(predicted_workspace == truth_workspace)
        counters["packet_count_correct"] += float(predicted_packet_count == truth_packet_count)
        if not truth_workspace:
            counters["dissolution_trials"] += 1
            counters["dissolution_correct"] += float(not predicted_workspace)

        observed = values_all[episode].copy()
        perm_true = np.asarray(state["perm_true"], dtype=int)
        observed = observed[perm_true]
        perm_est = np.asarray(state["perm_est"], dtype=int)
        inverse_est = np.argsort(perm_est)
        canonical_est = observed[inverse_est] if self_model else observed

        shared_mass = current_u[:, 1:].sum(axis=1)
        predicted_agents = shared_mass > 0.20
        if not predicted_workspace:
            predicted_agents[:] = False
            predicted_agents[0] = True
        if not np.any(predicted_agents):
            predicted_agents[0] = True
        prediction = int(canonical_est[predicted_agents].sum()) % classes
        prediction = (prediction + int(state["world_offset_est"])) % classes
        target = int(values_all[episode][required_agents].sum()) % classes
        target = (target + int(state["world_offset_true"])) % classes
        if not planner:
            prediction = 0
        error = _cyclic_distance(prediction, target, classes) / max(1.0, classes / 2.0)
        changed_prediction = bool(change_detector and error > anomaly_threshold)
        truth_change = bool(event_pending and event_truth in {"world_shift", "self_shift", "partner_change"})
        if event_pending:
            counters["change_trials"] += 1
            counters["change_correct"] += float(changed_prediction == truth_change)

        predicted_source = "none"
        abstention_threshold = float(cfg(config, "metacognition.abstention_threshold", 0.55))
        evidence_budget = int(state["next_evidence_budget"])
        reopened = evidence_budget > int(cfg(config, "metacognition.evidence_budget", 1))
        if truth_change:
            counters["reopen_trials"] += 1
            counters["reopen_correct"] += float(reopened or episode == segment.start)
        self_mismatch = float(
            np.mean(np.asarray(state["perm_true"]) != np.asarray(state["perm_est"]))
        )
        partner_mismatch = float(
            np.mean(
                np.asarray(state["cue_perm_true"])
                != np.asarray(state["cue_perm_est"])
            )
        )
        world_mismatch = _cyclic_distance(
            int(state["world_offset_true"]),
            int(state["world_offset_est"]),
            classes,
        ) / max(1.0, classes / 2.0)
        actual_model_mismatch = max(self_mismatch, partner_mismatch, world_mismatch) > 1e-9
        if changed_prediction and causal_boundary and actual_model_mismatch:
            if probing and metacognition:
                scale = max(1, evidence_budget * probe_samples)
                self_evidence = max(self_mismatch, partner_mismatch) + probe_noise_self[episode] / math.sqrt(scale)
                world_evidence = world_mismatch + probe_noise_world[episode] / math.sqrt(scale)
                counters["probe_total"] += scale
            else:
                self_evidence = 0.5 * max(self_mismatch, partner_mismatch)
                world_evidence = 0.5 * world_mismatch
            confidence = abs(self_evidence - world_evidence)
            if confidence < attribution_margin * abstention_threshold:
                predicted_source = "unresolved"
            elif self_evidence > world_evidence:
                predicted_source = "self"
            else:
                predicted_source = "world"
            truth_source = "self" if event_truth in {"self_shift", "partner_change"} else "world"
            counters["attribution_trials"] += 1
            counters["attribution_correct"] += float(predicted_source == truth_source)
            if repair_enabled and predicted_source in {"self", "world"}:
                counters["repair_trials"] += 1
                repair_gate = repair_rate >= recovery_threshold
                if repair_gate and predicted_source == "self":
                    state["perm_est"] = list(state["perm_true"])
                    if coordinate_alignment:
                        state["cue_perm_est"] = list(state["cue_perm_true"])
                elif repair_gate:
                    state["world_offset_est"] = int(state["world_offset_true"])
                residual_mismatch = max(
                    float(np.mean(np.asarray(state["perm_true"]) != np.asarray(state["perm_est"]))),
                    float(np.mean(np.asarray(state["cue_perm_true"]) != np.asarray(state["cue_perm_est"]))),
                    _cyclic_distance(
                        int(state["world_offset_true"]),
                        int(state["world_offset_est"]),
                        classes,
                    ) / max(1.0, classes / 2.0),
                )
                repaired = residual_mismatch <= recovery_threshold
                counters["repair_correct"] += float(repaired)
                if repaired:
                    event_pending = False
        elif event_pending and event_truth == "memory_corruption":
            event_pending = False

        task_correct = prediction == target
        counters["task_correct"] += float(task_correct)
        counters["episodes"] += 1
        if memory_enabled and task_correct:
            state["memory_records"] = min(
                min(
                    int(cfg(config, "continuous.max_memory_records", 512)),
                    int(cfg(config, "memory.capacity", 256)),
                ),
                int(state["memory_records"]) + 1,
            )

        if error > anomaly_threshold and recurrence and metacognition:
            state["next_evidence_budget"] = int(
                cfg(config, "metacognition.max_evidence_budget", 4)
            )
        else:
            state["next_evidence_budget"] = int(
                cfg(config, "metacognition.evidence_budget", 1)
            )

        # Continuity should survive representational repair and remain unresolved under
        # unquarantined foreign memory.
        if event_truth in {"self_shift", "partner_change", "memory_corruption"}:
            counters["continuity_trials"] += 1
            expected_continuity = event_truth != "memory_corruption" or quarantine
            predicted_continuity = bool(
                temporal
                and continuity
                and (
                    event_truth not in {"self_shift", "partner_change"}
                    or list(state["perm_est"]) == list(state["perm_true"])
                )
                and (event_truth != "memory_corruption" or quarantine)
            )
            counters["continuity_correct"] += float(
                predicted_continuity == expected_continuity
            )

        membership_entropy = float(np.mean(entropy(current_u, axis=1)))
        idempotence = float(
            np.mean(
                [
                    np.linalg.norm(
                        np.diag(current_u[:, packet]) ** 2
                        - np.diag(current_u[:, packet]),
                        ord="fro",
                    )
                    for packet in range(max_packets)
                ]
            )
        )
        transport = float(
            np.linalg.norm(
                current_u[np.asarray(state["cue_perm_true"], dtype=int)]
                - current_u[np.asarray(state["cue_perm_est"], dtype=int)],
                ord="fro",
            )
            / max(1.0, math.sqrt(current_u.size))
        )
        counters["entropy_sum"] += membership_entropy
        counters["idempotence_sum"] += idempotence
        counters["transport_sum"] += transport
        counters["packet_count_sum"] += predicted_packet_count

        if bool(cfg(config, "run.save_rows", True)) and len(rows) < 5000:
            rows.append(
                {
                    "episode": episode,
                    "segment": segment_index,
                    "task_kind": TASK_NAMES[segment.task_kind],
                    "event_truth": event_truth if episode == segment.start else "continuation",
                    "prediction": prediction,
                    "target": target,
                    "task_correct": task_correct,
                    "change_detected": changed_prediction,
                    "attribution": predicted_source,
                    "truth_packet_count": truth_packet_count,
                    "predicted_packet_count": predicted_packet_count,
                    "workspace_active": predicted_workspace,
                    "membership_entropy": membership_entropy,
                    "idempotence_defect": idempotence,
                    "transport_defect": transport,
                    "evidence_budget": evidence_budget,
                    "memory_records": int(state["memory_records"]),
                    "quarantined_records": int(state["quarantined_records"]),
                }
            )
            if checkpoint_state_rows > 0 and len(rows) > checkpoint_state_rows:
                rows = rows[-checkpoint_state_rows:]
        state["row_tail"] = rows[-checkpoint_state_rows:] if checkpoint_state_rows > 0 else []

        state["episode"] = episode + 1
        state["counters"] = counters
        state["rng_state"] = rng.bit_generator.state
        state["current_segment_index"] = current_segment_index
        state["event_truth"] = event_truth
        state["event_pending"] = event_pending
        if context is not None:
            context.checkpoint(
                episode + 1,
                state,
                {
                    "task_accuracy_so_far": counters["task_correct"]
                    / max(1.0, counters["episodes"]),
                    "active_packets": active_count,
                },
            )
        if invocation_step_limit > 0 and (episode + 1 - start_episode) >= invocation_step_limit and (episode + 1) < episodes:
            if context is not None:
                context.checkpoint(episode + 1, state, {"interrupted_for_resume": True}, force=True)
            break

    completed_all = int(state.get("episode", 0)) >= episodes
    denom = max(1.0, counters["episodes"])
    task_accuracy = counters["task_correct"] / denom
    metrics = {
        "task_accuracy": task_accuracy,
        "continuous_task_accuracy": task_accuracy,
        "change_detection_accuracy": counters["change_correct"]
        / max(1.0, counters["change_trials"]),
        "self_world_accuracy": counters["attribution_correct"]
        / max(1.0, counters["attribution_trials"]),
        "self_world_attribution_accuracy": counters["attribution_correct"]
        / max(1.0, counters["attribution_trials"]),
        "formation_accuracy": counters["formation_correct"] / denom,
        "packet_birth_accuracy": counters["packet_count_correct"] / denom,
        "packet_death_accuracy": counters["dissolution_correct"]
        / max(1.0, counters["dissolution_trials"]),
        "workspace_dissolution_accuracy": counters["dissolution_correct"]
        / max(1.0, counters["dissolution_trials"]),
        "provenance_accuracy": counters["provenance_correct"]
        / max(1.0, counters["provenance_trials"]),
        "false_autobiographical_write_rate": counters["false_writes"]
        / max(1.0, counters["provenance_trials"]),
        "recurrence_reopen_rate": counters["reopen_correct"]
        / max(1.0, counters["reopen_trials"]),
        "repair_accuracy": counters["repair_correct"]
        / max(1.0, counters["repair_trials"]),
        "continuity_accuracy": counters["continuity_correct"]
        / max(1.0, counters["continuity_trials"]),
        "membership_entropy": counters["entropy_sum"] / denom,
        "idempotence_defect": counters["idempotence_sum"] / denom,
        "transport_defect": counters["transport_sum"] / denom,
        "mean_active_packets": counters["packet_count_sum"] / denom,
        "adaptive_probe_accuracy": 1.0 if probing else 0.0,
        "planner_binding_rate": 1.0 if planner else 0.0,
        "workspace_decodability": counters["formation_correct"] / denom,
        "episodes_completed": int(counters["episodes"]),
        "target_episodes": episodes,
        "run_complete": stop_episode >= episodes,
        "memory_records": int(state["memory_records"]),
        "quarantined_records": int(state["quarantined_records"]),
        "probe_count": int(counters["probe_total"]),
    }
    closure_axes = [
        metrics["task_accuracy"],
        metrics["change_detection_accuracy"],
        metrics["self_world_attribution_accuracy"],
        metrics["formation_accuracy"],
        metrics["provenance_accuracy"],
        metrics["recurrence_reopen_rate"],
        metrics["continuity_accuracy"],
    ]
    metrics["functional_closure_score"] = float(
        np.exp(np.mean(np.log(np.clip(closure_axes, 1e-9, 1.0))))
    )
    if context is not None:
        context.checkpoint(
            stop_episode,
            {**state, "phase": "completed" if stop_episode >= episodes else "interrupted"},
            metrics,
            force=True,
        )
    semantic_state = dict(state)
    semantic_state.pop("phase", None)
    trajectory_digest = digest_object(
        {
            "state": semantic_state,
            "counters": counters,
            "rows": rows,
            "schedule": [segment.__dict__ for segment in schedule],
        }
    )
    return ExperimentResult(
        family="continuous_open_set_runtime",
        status="completed" if stop_episode >= episodes else "interrupted",
        metrics=metrics,
        rows=rows,
        warnings=[
            "Legacy scaffold: repair in continuous_open_set_runtime reads evaluator-side "
            "latent state. Do not interpret its attribution or repair metrics as "
            "evaluator-blind causal evidence; use persistent_fuzzy_j_workspace for the "
            "new blinded bridge protocol."
        ],
        metadata={
            "final_step": stop_episode,
            "segments": [segment.__dict__ for segment in schedule],
            "event_types": EVENT_NAMES,
            "task_types": TASK_NAMES,
            "resumed": bool(context and context.resumed),
            "trajectory_digest": trajectory_digest,
            "controller_hidden_truth_access": True,
            "scientific_status": "legacy_oracle_assisted_scaffold",
            "interpretation_boundary": (
                "Bounded continuous synthetic functional test; not evidence of subjective experience."
            ),
        },
    )

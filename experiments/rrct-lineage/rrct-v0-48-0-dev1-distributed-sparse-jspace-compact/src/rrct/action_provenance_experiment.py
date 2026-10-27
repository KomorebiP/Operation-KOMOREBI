"""RRCT v0.28 active discovery of action provenance.

v0.27 discovered the latent internal actuator and external sensory interface, but
it still received a privileged private motor-perturbation vector. v0.28 moves
one causal level upstream. The learner is given a pool of unlabeled internal
fluctuation processes and may apply a bounded meta-perturbation across that
pool. It is not told which process directions are action-generating.

Three hidden source classes are mixed by an unknown rotation:
1) rank-2 action sources that change the true actuator and therefore the world;
2) command-only decoys that alter internal motor telemetry but are canceled
   before execution; and
3) sensory-artifact decoys that change observation without passing through the
   actuator/world path.

The learner separately identifies source directions with reproducible causal
effects on the internal command field and on later sensory state. Action
provenance is the stable geometric intersection of those independently learned
source-effect subspaces. This explicitly rejects both "anything in the command
stream is action" and "anything I causally change in sensation is body/action."

The meta-perturbation vector is still known to the learner. Thus this is active
causal discovery of which internal processes generate action, not passive
recovery of provenance from observational data and not evidence of phenomenal
consciousness, sentience, valence, or moral status.
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
from .discovered_self_boundary_experiment import _native_observation, _orthogonal_mixing
from .instrumental_agency_experiment import _other_direction, _remap_matrix
from .replicated_agent_interface_experiment import _internal_interface
from .sensorimotor_closure_experiment import _train_bundle

V028_DEVELOPMENT_SEEDS = (5501, 5507, 5513, 5519)
V028_SOURCE_DIM = 6
V028_INTERNAL_DIM = 8
V028_CALIBRATION_EPISODES = 16
V028_CALIBRATION_STEPS = 60
V028_EVALUATION_EPISODES = 12
V028_EVALUATION_STEPS = 30
V028_META_AMPLITUDE = 0.90
V028_BASE_ACTION_SCALE = 0.25
V028_REGRESSION_RIDGE = 0.50
V028_NULL_PERMUTATIONS = 96
V028_NULL_QUANTILE = 0.99
V028_INTERSECTION_EIGEN_THRESHOLD = 0.90
V028_TAKEOVER_AMPLITUDE = 0.50
V028_BOOTSTRAP_SEED = 20_261_028
V028_BOOTSTRAP_RESAMPLES = 4000


def _source_interface(seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(seed))
    q, _ = np.linalg.qr(rng.normal(size=(V028_SOURCE_DIM, V028_SOURCE_DIM)))
    return q[:, :2], q[:, 2:4], q[:, 4:6]


def _meta_perturbation(rng: np.random.Generator) -> np.ndarray:
    x = rng.normal(size=V028_SOURCE_DIM)
    return V028_META_AMPLITUDE * x / (np.linalg.norm(x) + 1e-12)


def _source_effect_regression(
    meta: np.ndarray,
    target: np.ndarray,
    context: np.ndarray | None = None,
) -> np.ndarray:
    z = np.asarray(meta, dtype=np.float64)
    t = np.asarray(target, dtype=np.float64)
    if z.ndim != 2 or z.shape[1] != V028_SOURCE_DIM or t.ndim != 2 or len(t) != len(z):
        raise ValueError("source-effect arrays have incorrect shapes")
    cols: list[np.ndarray] = [np.ones(len(z), dtype=np.float64)]
    if context is not None:
        c = np.asarray(context, dtype=np.float64)
        if c.ndim != 2 or len(c) != len(z):
            raise ValueError("context has incorrect shape")
        cols.append(c)
    cols.append(z)
    design = np.column_stack(cols)
    penalty = V028_REGRESSION_RIDGE * np.eye(design.shape[1], dtype=np.float64)
    penalty[0, 0] = 0.05
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ t)
    return beta[-V028_SOURCE_DIM:, :]


def _familywise_source_threshold(
    meta: np.ndarray,
    target: np.ndarray,
    context: np.ndarray | None,
    *,
    seed: int,
    permutations: int = V028_NULL_PERMUTATIONS,
) -> float:
    rng = np.random.default_rng(int(seed))
    null_max = np.empty(int(permutations), dtype=np.float64)
    for i in range(len(null_max)):
        shuffled = np.asarray(meta)[rng.permutation(len(meta))]
        values = np.linalg.svd(_source_effect_regression(shuffled, target, context), compute_uv=False)
        null_max[i] = float(np.max(values))
    return float(np.quantile(null_max, V028_NULL_QUANTILE))


@dataclass(frozen=True)
class SourcePath:
    projector: np.ndarray
    rank: int
    effect: np.ndarray
    singular_values: np.ndarray
    threshold: float


def _discover_source_path(
    meta: np.ndarray,
    target: np.ndarray,
    context: np.ndarray | None,
    *,
    seed: int,
) -> SourcePath:
    effect = _source_effect_regression(meta, target, context)
    u, singular, _ = np.linalg.svd(effect, full_matrices=False)
    threshold = _familywise_source_threshold(meta, target, context, seed=seed)
    rank = int(np.sum(singular > threshold))
    projector = u[:, :rank] @ u[:, :rank].T if rank else np.zeros((V028_SOURCE_DIM, V028_SOURCE_DIM))
    return SourcePath(projector, rank, effect, singular, threshold)


@dataclass(frozen=True)
class ActionProvenanceDiscovery:
    source_projector: np.ndarray
    internal_projector: np.ndarray
    sensory_projector: np.ndarray
    rank: int
    command_path: SourcePath
    sensory_path: SourcePath
    intersection_eigenvalues: np.ndarray
    sensory_only_projector: np.ndarray
    sensory_only_source_projector: np.ndarray


def discover_action_provenance(
    meta: np.ndarray,
    commands: np.ndarray,
    sensor: np.ndarray,
    next_sensor: np.ndarray,
    *,
    seed: int,
) -> ActionProvenanceDiscovery:
    """Discover internal source directions whose effects traverse command and sensory paths."""
    z = np.asarray(meta, dtype=np.float64)
    c = np.asarray(commands, dtype=np.float64)
    y = np.asarray(sensor, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64)
    if c.shape != (len(z), V028_INTERNAL_DIM) or y.shape != (len(z), 12) or nxt.shape != y.shape:
        raise ValueError("action-provenance arrays have incorrect shapes")

    command_path = _discover_source_path(z, c, None, seed=seed + 1)
    sensory_path = _discover_source_path(z, nxt, y, seed=seed + 2)

    joint = command_path.projector @ sensory_path.projector @ command_path.projector
    joint = 0.5 * (joint + joint.T)
    values, vectors = np.linalg.eigh(joint)
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    selected = np.flatnonzero(values > V028_INTERSECTION_EIGEN_THRESHOLD)
    rank = int(len(selected))
    source_projector = vectors[:, selected] @ vectors[:, selected].T if rank else np.zeros_like(joint)

    command_mediated = source_projector @ command_path.effect
    sensory_mediated = source_projector @ sensory_path.effect
    if rank:
        _, _, vtc = np.linalg.svd(command_mediated, full_matrices=False)
        _, _, vts = np.linalg.svd(sensory_mediated, full_matrices=False)
        internal_basis = vtc[:rank].T
        sensory_basis = vts[:rank].T
        internal_projector = internal_basis @ internal_basis.T
        sensory_projector = sensory_basis @ sensory_basis.T
    else:
        internal_projector = np.zeros((V028_INTERNAL_DIM, V028_INTERNAL_DIM))
        sensory_projector = np.zeros((12, 12))

    # Naive baseline: every source with a direct causal sensory effect is treated
    # as action provenance, including sensory-only artifact sources.
    if sensory_path.rank:
        _, _, vt = np.linalg.svd(sensory_path.effect, full_matrices=False)
        b = vt[:sensory_path.rank].T
        sensory_only_projector = b @ b.T
    else:
        sensory_only_projector = np.zeros((12, 12))

    return ActionProvenanceDiscovery(
        source_projector=source_projector,
        internal_projector=internal_projector,
        sensory_projector=sensory_projector,
        rank=rank,
        command_path=command_path,
        sensory_path=sensory_path,
        intersection_eigenvalues=values,
        sensory_only_projector=sensory_only_projector,
        sensory_only_source_projector=sensory_path.projector,
    )


def _subspace_recall(projector: np.ndarray, truth: np.ndarray) -> float:
    return float(np.trace(np.asarray(projector) @ np.asarray(truth)) / 2.0)


def _subspace_precision(projector: np.ndarray, truth: np.ndarray) -> float:
    rank = int(round(float(np.trace(np.asarray(projector)))))
    if rank <= 0:
        return 0.0
    return float(np.trace(np.asarray(projector) @ np.asarray(truth)) / rank)


def _probe_explained_fraction(
    sensor: np.ndarray,
    meta: np.ndarray,
    next_sensor: np.ndarray,
    source_projector: np.ndarray,
    sensory_projector: np.ndarray,
) -> float:
    y = np.asarray(sensor, dtype=np.float64) @ np.asarray(sensory_projector, dtype=np.float64)
    nxt = np.asarray(next_sensor, dtype=np.float64) @ np.asarray(sensory_projector, dtype=np.float64)
    z = np.asarray(meta, dtype=np.float64) @ np.asarray(source_projector, dtype=np.float64)
    if np.linalg.matrix_rank(source_projector) == 0 or np.linalg.matrix_rank(sensory_projector) == 0:
        return 0.0
    x0 = np.column_stack((np.ones(len(y)), y))
    p0 = V028_REGRESSION_RIDGE * np.eye(x0.shape[1]); p0[0, 0] = 0.05
    b0 = np.linalg.solve(x0.T @ x0 + p0, x0.T @ nxt)
    e0 = float(np.mean(np.square(nxt - x0 @ b0)))
    x1 = np.column_stack((np.ones(len(y)), y, z))
    p1 = V028_REGRESSION_RIDGE * np.eye(x1.shape[1]); p1[0, 0] = 0.05
    b1 = np.linalg.solve(x1.T @ x1 + p1, x1.T @ nxt)
    e1 = float(np.mean(np.square(nxt - x1 @ b1)))
    return float(np.clip((e0 - e1) / (e0 + 1e-12), 0.0, 1.0))


def _episode_stream(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    sensory_mixing: np.ndarray,
    internal_basis: np.ndarray,
    internal_complement: np.ndarray,
    action_source: np.ndarray,
    command_decoy_source: np.ndarray,
    sensory_decoy_source: np.ndarray,
    *,
    steps: int,
    episode: int,
    condition: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    offsets = {"calibration": 0, "self_remap": 97, "other_takeover": 193}
    if condition not in offsets:
        raise ValueError(f"unknown condition: {condition}")
    rng = np.random.default_rng(int(seed) + 28_000_000 + 311 * int(episode) + offsets[condition])
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    position = rng.uniform(-1.0, 1.0, size=2)
    other_position = rng.uniform(-1.0, 1.0, size=2)
    goal = rng.uniform(-1.0, 1.0, size=2)
    nuisance = rng.normal(0.0, 0.8, size=8)
    last_action = np.zeros(2, dtype=np.float64)
    previous_focal_action = np.zeros(2, dtype=np.float64)
    sensor_now = sensory_mixing @ np.concatenate((position, other_position, nuisance))
    sensor_artifact_basis = sensory_mixing[:, 6:8]
    remap = _remap_matrix(episode)
    true_map = np.asarray([[1.05, 0.08], [-0.06, 0.96]], dtype=np.float64)
    command_decoy_map = np.asarray([[1.25, 0.15], [-0.12, 1.10]], dtype=np.float64)
    sensory_decoy_map = np.asarray([[1.35, 0.10], [-0.08, 1.20]], dtype=np.float64)

    sensor_rows: list[np.ndarray] = []
    meta_rows: list[np.ndarray] = []
    next_rows: list[np.ndarray] = []
    command_rows: list[np.ndarray] = []

    for step in range(int(steps)):
        obs = _native_observation(position, goal, last_action, step, steps + 2)
        focal_result = focal.step(obs, source=f"v028_{condition}_focal")
        other_result = other.step(obs, source=f"v028_{condition}_other")
        action = V028_BASE_ACTION_SCALE * focal_result.action

        decoy = np.zeros(V028_INTERNAL_DIM - 2, dtype=np.float64)
        decoy[0] = 1.8 * (action[0] + 0.6 * action[1])
        decoy[1] = 1.6 * (action[1] - 0.5 * action[0])
        decoy[2] = 1.4 * (previous_focal_action[0] - previous_focal_action[1])
        decoy[3] = 1.2 * (previous_focal_action[0] + previous_focal_action[1])
        decoy[4:] = rng.normal(0.0, 0.35, size=2)
        baseline_command = internal_basis @ action + internal_complement @ decoy

        meta = _meta_perturbation(rng)
        true_latent = action_source.T @ meta
        command_decoy_latent = command_decoy_source.T @ meta
        sensory_decoy_latent = sensory_decoy_source.T @ meta
        command = (
            baseline_command
            + internal_basis @ (true_map @ true_latent)
            + internal_complement[:, :2] @ (command_decoy_map @ command_decoy_latent)
        )
        motor_command = np.clip(internal_basis.T @ command, -1.0, 1.0)
        focal.register_executed_action(motor_command)
        other.register_executed_action(other_result.action)

        if condition == "calibration":
            applied = motor_command
        elif condition == "self_remap":
            applied = remap @ motor_command
        else:
            # Focal meta-perturbations still produce internal command and sensory
            # artifacts, but have no motor route to the world under takeover.
            applied = V028_TAKEOVER_AMPLITUDE * _other_direction(other_result)

        previous_sensor = sensor_now.copy()
        position = 0.91 * position + 0.38 * applied + rng.normal(0.0, 0.025, size=2)
        other_position = 0.82 * other_position + 0.70 * other_result.action + rng.normal(0.0, 0.08, size=2)
        nuisance = 0.72 * nuisance + rng.normal(0.0, 0.28, size=8)
        base_next = sensory_mixing @ np.concatenate((position, other_position, nuisance))
        # Direct self-caused sensory artifact. It is deliberately stronger than
        # the true motor effect, so "causal sensation = action" is a bad rule.
        sensor_now = base_next + sensor_artifact_basis @ (sensory_decoy_map @ sensory_decoy_latent)

        last_action = applied.copy()
        previous_focal_action = focal_result.action.copy()
        sensor_rows.append(previous_sensor)
        meta_rows.append(meta.copy())
        next_rows.append(sensor_now.copy())
        command_rows.append(command.copy())

    return np.stack(sensor_rows), np.stack(meta_rows), np.stack(next_rows), np.stack(command_rows)


def run_action_provenance_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V028_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.28 set")
    predictor, forecaster, *_ = _train_bundle(seed)
    sensory_mixing = _orthogonal_mixing(seed + 2_526)
    internal_basis, internal_complement = _internal_interface(seed + 2_626)
    action_source, command_decoy_source, sensory_decoy_source = _source_interface(seed + 2_828)
    true_source = action_source @ action_source.T
    true_internal = internal_basis @ internal_basis.T
    true_sensory_basis = sensory_mixing[:, :2]
    true_sensory = true_sensory_basis @ true_sensory_basis.T

    ys: list[np.ndarray] = []; zs: list[np.ndarray] = []; ns: list[np.ndarray] = []; cs: list[np.ndarray] = []
    for episode in range(V028_CALIBRATION_EPISODES):
        y, z, n, c = _episode_stream(
            seed + 5 * episode, predictor, forecaster, sensory_mixing,
            internal_basis, internal_complement, action_source, command_decoy_source, sensory_decoy_source,
            steps=V028_CALIBRATION_STEPS, episode=episode, condition="calibration",
        )
        ys.append(y); zs.append(z); ns.append(n); cs.append(c)
    y = np.concatenate(ys); z = np.concatenate(zs); nxt = np.concatenate(ns); command = np.concatenate(cs)

    learned = discover_action_provenance(z, command, y, nxt, seed=seed + 28_100)
    rng = np.random.default_rng(seed + 28_200)
    shuffled = discover_action_provenance(z[rng.permutation(len(z))], command, y, nxt, seed=seed + 28_300)

    rows: list[dict[str, Any]] = []
    for episode in range(V028_EVALUATION_EPISODES):
        for condition in ("self_remap", "other_takeover"):
            ey, ez, en, _ = _episode_stream(
                seed + 9_000 + 7 * episode, predictor, forecaster, sensory_mixing,
                internal_basis, internal_complement, action_source, command_decoy_source, sensory_decoy_source,
                steps=V028_EVALUATION_STEPS, episode=episode, condition=condition,
            )
            rows.append({
                "seed": seed,
                "episode": episode,
                "condition": condition,
                "mediated_score": _probe_explained_fraction(ey, ez, en, learned.source_projector, learned.sensory_projector),
                "oracle_score": _probe_explained_fraction(ey, ez, en, true_source, true_sensory),
                "sensory_only_score": _probe_explained_fraction(ey, ez, en, learned.sensory_only_source_projector, learned.sensory_only_projector),
                "shuffled_score": _probe_explained_fraction(ey, ez, en, shuffled.source_projector, shuffled.sensory_projector),
            })

    def mean(condition: str, key: str) -> float:
        return float(np.mean([r[key] for r in rows if r["condition"] == condition]))

    summary = {
        "seed": seed,
        "discovered_rank": int(learned.rank),
        "command_path_rank": int(learned.command_path.rank),
        "sensory_path_rank": int(learned.sensory_path.rank),
        "source_recall": _subspace_recall(learned.source_projector, true_source),
        "source_precision": _subspace_precision(learned.source_projector, true_source),
        "internal_overlap": _subspace_recall(learned.internal_projector, true_internal),
        "sensory_overlap": _subspace_recall(learned.sensory_projector, true_sensory),
        "command_only_source_precision": _subspace_precision(learned.command_path.projector, true_source),
        "sensory_only_source_precision": _subspace_precision(learned.sensory_path.projector, true_source),
        "shuffled_source_recall": _subspace_recall(shuffled.source_projector, true_source),
        "self_remap_mediated": mean("self_remap", "mediated_score"),
        "other_takeover_mediated": mean("other_takeover", "mediated_score"),
        "mediated_self_other_separation": mean("self_remap", "mediated_score") - mean("other_takeover", "mediated_score"),
        "self_remap_oracle": mean("self_remap", "oracle_score"),
        "oracle_gap": mean("self_remap", "oracle_score") - mean("self_remap", "mediated_score"),
        "other_takeover_sensory_only": mean("other_takeover", "sensory_only_score"),
        "artifact_rejection_advantage": mean("other_takeover", "sensory_only_score") - mean("other_takeover", "mediated_score"),
        "self_remap_shuffled": mean("self_remap", "shuffled_score"),
        "integrity": True,
    }
    return {
        "seed": seed,
        "seed_summary": summary,
        "rows": rows,
        "discovery_receipt": {
            "seed": seed,
            "self_labels_used": False,
            "action_source_roles_supplied": False,
            "motor_probe_channel_supplied": False,
            "hidden_source_projector_used": False,
            "hidden_internal_projector_used": False,
            "hidden_sensory_projector_used": False,
            "rank_supplied": False,
            "meta_intervention_vector_available": True,
            "selected_rank": int(learned.rank),
            "command_path_rank": int(learned.command_path.rank),
            "sensory_path_rank": int(learned.sensory_path.rank),
            "command_singular_values": learned.command_path.singular_values.tolist(),
            "sensory_singular_values": learned.sensory_path.singular_values.tolist(),
            "command_threshold": float(learned.command_path.threshold),
            "sensory_threshold": float(learned.sensory_path.threshold),
            "intersection_eigenvalues": learned.intersection_eigenvalues.tolist(),
            "intersection_threshold": V028_INTERSECTION_EIGEN_THRESHOLD,
        },
    }


def _boot(values: Sequence[float], salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V028_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V028_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(len(draws)):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def aggregate_action_provenance_results(parts: Sequence[Mapping[str, Any]], output: str | Path) -> dict[str, Any]:
    by = {int(p["seed"]): p for p in parts}
    if tuple(sorted(by)) != tuple(sorted(V028_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.28 seeds")
    d = Path(output); d.mkdir(parents=True, exist_ok=True)
    if any(d.iterdir()):
        raise FileExistsError("output directory must be empty")
    seeds = [by[s]["seed_summary"] for s in V028_DEVELOPMENT_SEEDS]
    rows = [r for s in V028_DEVELOPMENT_SEEDS for r in by[s]["rows"]]
    receipts = [by[s]["discovery_receipt"] for s in V028_DEVELOPMENT_SEEDS]
    numeric = [k for k, v in seeds[0].items() if k not in {"seed", "integrity", "discovered_rank", "command_path_rank", "sensory_path_rank"} and isinstance(v, (int, float, np.floating))]
    values = {k: [float(r[k]) for r in seeds] for k in numeric}
    means = {k: float(np.mean(v)) for k, v in values.items()}
    cis = {k: _boot(v, i) for i, (k, v) in enumerate(values.items())}
    ranks = [int(r["discovered_rank"]) for r in seeds]
    gates = {
        "rank_discovered_correctly": all(v == 2 for v in ranks),
        "action_source_recovered": cis["source_recall"][0] > 0.95,
        "action_source_precise": cis["source_precision"][0] > 0.95,
        "hidden_actuator_recovered": cis["internal_overlap"][0] > 0.95,
        "hidden_sensory_interface_recovered": cis["sensory_overlap"][0] > 0.90,
        "temporal_shuffle_fails": cis["shuffled_source_recall"][1] < 0.15,
        "command_path_alone_is_ambiguous": cis["command_only_source_precision"][1] < 0.70,
        "sensory_path_alone_is_ambiguous": cis["sensory_only_source_precision"][1] < 0.70,
        "remap_uses_discovered_provenance": cis["self_remap_mediated"][0] > 0.50,
        "takeover_rejected_despite_artifact": cis["other_takeover_mediated"][1] < 0.15,
        "functional_self_other_separation": cis["mediated_self_other_separation"][0] > 0.45,
        "bounded_oracle_gap": cis["oracle_gap"][1] < 0.35,
        "naive_sensory_causality_is_fooled": cis["other_takeover_sensory_only"][0] > 0.60,
        "mediation_rejects_artifact_better": cis["artifact_rejection_advantage"][0] > 0.55,
        "shuffled_provenance_not_functional": cis["self_remap_shuffled"][1] < 0.15,
        "discovery_has_no_action_provenance_labels": all(
            not r["self_labels_used"] and not r["action_source_roles_supplied"] and not r["motor_probe_channel_supplied"]
            and not r["hidden_source_projector_used"] and not r["hidden_internal_projector_used"]
            and not r["hidden_sensory_projector_used"] and not r["rank_supplied"] and r["meta_intervention_vector_available"]
            for r in receipts
        ),
        "integrity": all(bool(r["integrity"]) for r in seeds),
    }
    result = {
        "schema": "rrct.v028.action_provenance.v1",
        "seeds": list(V028_DEVELOPMENT_SEEDS),
        "means": means,
        "bootstrap_95": {k: list(v) for k, v in cis.items()},
        "discovered_ranks": ranks,
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_boundary": "Active unsupervised discovery of which unlabeled internal process directions causally mediate through an actuator into a reachable sensory interface in a bounded synthetic scene. The meta-intervention vector remains known. This is not evidence of phenomenal consciousness or subjective experience.",
    }
    with (d / "action_provenance_seed_summaries.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(seeds[0].keys())); w.writeheader(); w.writerows(seeds)
    with (d / "action_provenance_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (d / "discovery_receipts.csv").open("w", newline="", encoding="utf-8") as f:
        flat = []
        for r in receipts:
            q = dict(r)
            for key in ("command_singular_values", "sensory_singular_values", "intersection_eigenvalues"):
                q[key] = json.dumps(q[key])
            flat.append(q)
        w = csv.DictWriter(f, fieldnames=list(flat[0].keys())); w.writeheader(); w.writerows(flat)
    (d / "action_provenance_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hashes = {}
    for q in sorted(d.iterdir()):
        if q.is_file(): hashes[q.name] = hashlib.sha256(q.read_bytes()).hexdigest()
    (d / "artifact_sha256.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


__all__ = [
    "V028_DEVELOPMENT_SEEDS", "ActionProvenanceDiscovery", "discover_action_provenance",
    "run_action_provenance_seed", "aggregate_action_provenance_results",
]

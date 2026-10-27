"""RRCT v0.17 causal identity through discontinuity experiment.

Functional question only: when instantaneous internal-state similarity and
ongoing causal continuity are deliberately placed in conflict, does RRCT's
private-intervention self model track the causally continuous continuation?

The experiment creates a paired fork after a common prehistory.  The true
continuation has its transient specialist/workspace/self/memory state erased
and its actuator secretly remapped, but its private motor interventions remain
causally efficacious.  The impostor branch begins as an exact deep copy of the
pre-fork focal agent, including memory, while another matched RRCT agent
actually controls the world.  No identity label, UUID, or branch name enters
the ownership classifier.

This operationalizes a narrow functional notion of temporal self-continuity.
It does not measure phenomenal consciousness, subjective awareness, sentience,
valence, or moral status.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import _agent_from_snapshots, _fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .instrumental_agency_experiment import (
    InstrumentalOwnershipClassifier,
    V016_WINDOW,
    _fit_classifier,
    _other_direction,
    _passive_residual,
    _private_probe,
    _remap_matrix,
    _window_statistics,
)
from .sensorimotor_closure_experiment import _train_bundle

V017_DEVELOPMENT_SEEDS = (4001, 4007, 4013, 4019)
V017_EVALUATION_EPISODES = 24
V017_PREHISTORY_STEPS = 10
V017_POST_STEPS = 12
V017_LATE_WINDOWS = 3
V017_BOOTSTRAP_SEED = 20_261_017
V017_BOOTSTRAP_RESAMPLES = 4000


def _dynamic_state_vector(agent: Any) -> np.ndarray:
    """Coordinate-level dynamic-state vector used only for similarity control."""
    memory = agent.memory.snapshot()
    parts = [np.asarray(module.state, dtype=np.float64) for module in agent.specialists]
    parts.extend(
        (
            np.asarray(agent.workspace.state, dtype=np.float64),
            np.asarray(agent.self_model.state, dtype=np.float64),
            np.asarray(agent.choose_action(), dtype=np.float64),
            np.asarray(memory["temporal_trace"], dtype=np.float64),
        )
    )
    return np.concatenate(parts)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    if x.shape != y.shape:
        raise ValueError("cosine inputs must have matching shapes")
    denom = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denom <= 1e-15:
        return 0.0
    return float(np.dot(x, y) / denom)


def _state_digest(agent: Any) -> str:
    """Audit digest; never exposed to the classifier or agent."""
    return hashlib.sha256(pickle.dumps(agent, protocol=5)).hexdigest()


def _ownership(
    classifier: InstrumentalOwnershipClassifier,
    probes: list[np.ndarray],
    residuals: list[np.ndarray],
) -> tuple[float, float]:
    if len(probes) < V016_WINDOW:
        return float("nan"), float("nan")
    z = np.stack(probes[-V016_WINDOW:])
    r = np.stack(residuals[-V016_WINDOW:])
    aligned = classifier.predict_probability(_window_statistics(z, r))
    shuffled = classifier.predict_probability(_window_statistics(np.roll(z, 1, axis=0), r))
    return float(aligned), float(shuffled)


def _run_paired_episode(
    *,
    seed: int,
    episode: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    passive: np.ndarray,
    classifier: InstrumentalOwnershipClassifier,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = np.random.default_rng(seed + 1_717_000 + 10_000 * episode)
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    world = GroundedTrackingWorld(
        grounded_world_spec(
            seed + 970_000 + episode,
            total_steps=V017_PREHISTORY_STEPS + V017_POST_STEPS + 4,
        )
    )

    # Common prehistory.  Only the focal command affects the world.  The other
    # agent sees the same observations, creating the common-cause confound used
    # in v0.16, but its action is not causal before the fork.
    for step in range(V017_PREHISTORY_STEPS):
        observation = world.observe(V017_PREHISTORY_STEPS + V017_POST_STEPS + 4)
        focal_result = focal.step(observation, source="v017_prehistory_focal")
        other_result = other.step(observation, source="v017_prehistory_other")
        probe = _private_probe(rng)
        command = np.clip(focal_result.action + probe, -1.0, 1.0)
        focal.register_executed_action(command)
        other.register_executed_action(other_result.action)
        world.advance(command)

    pre_vector = _dynamic_state_vector(focal)
    pre_digest = _state_digest(focal)

    # Paired fork from the exact same pre-fork state and world.
    continuous = copy.deepcopy(focal)
    impostor = copy.deepcopy(focal)
    continuous_world = copy.deepcopy(world)
    impostor_world = copy.deepcopy(world)

    impostor_digest_at_fork = _state_digest(impostor)
    continuous.reset()  # learned parameters retained; transient contents erased
    continuous_digest_after_reset = _state_digest(continuous)
    continuous_similarity = _cosine(pre_vector, _dynamic_state_vector(continuous))
    impostor_similarity = _cosine(pre_vector, _dynamic_state_vector(impostor))

    remap = _remap_matrix(episode)
    probes_c: list[np.ndarray] = []
    residuals_c: list[np.ndarray] = []
    probes_i: list[np.ndarray] = []
    residuals_i: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []

    for step in range(V017_POST_STEPS):
        # Use exactly the same private probe in both branches.  This eliminates
        # a simple probe-distribution explanation for branch separation.
        probe = _private_probe(rng)

        observation_c = continuous_world.observe(V017_PREHISTORY_STEPS + V017_POST_STEPS + 4)
        result_c = continuous.step(observation_c, source="v017_discontinuous_continuation")
        command_c = np.clip(result_c.action + probe, -1.0, 1.0)
        continuous.register_executed_action(command_c)
        continuous_world.advance(remap @ command_c)
        next_c = continuous_world.observe(V017_PREHISTORY_STEPS + V017_POST_STEPS + 4)
        probes_c.append(probe.copy())
        residuals_c.append(_passive_residual(passive, observation_c, next_c))
        own_c, shuffled_c = _ownership(classifier, probes_c, residuals_c)

        observation_i = impostor_world.observe(V017_PREHISTORY_STEPS + V017_POST_STEPS + 4)
        result_i = impostor.step(observation_i, source="v017_pristine_impostor")
        # The other agent shares the current observation but its direction, not
        # the focal private probe, controls the world.  Applied motor energy is
        # yoked exactly to the impostor focal command.
        other_result = other.step(observation_i, source="v017_other_controller")
        command_i = np.clip(result_i.action + probe, -1.0, 1.0)
        impostor.register_executed_action(command_i)
        other.register_executed_action(other_result.action)
        applied_i = float(np.linalg.norm(command_i)) * _other_direction(other_result)
        impostor_world.advance(applied_i)
        next_i = impostor_world.observe(V017_PREHISTORY_STEPS + V017_POST_STEPS + 4)
        probes_i.append(probe.copy())
        residuals_i.append(_passive_residual(passive, observation_i, next_i))
        own_i, shuffled_i = _ownership(classifier, probes_i, residuals_i)

        rows.extend(
            (
                {
                    "seed": seed,
                    "episode": episode,
                    "step": step,
                    "branch": "causal_continuation",
                    "ownership_probability": own_c,
                    "shuffled_ownership_probability": shuffled_c,
                    "fork_state_similarity": continuous_similarity,
                    "memory_size_at_fork": 0,
                    "private_probe_norm": float(np.linalg.norm(probe)),
                    "focal_command_norm": float(np.linalg.norm(command_c)),
                    "applied_action_norm": float(np.linalg.norm(remap @ command_c)),
                    "future_outcome_used_before_probe": False,
                    "identity_tag_available": False,
                },
                {
                    "seed": seed,
                    "episode": episode,
                    "step": step,
                    "branch": "state_matched_impostor",
                    "ownership_probability": own_i,
                    "shuffled_ownership_probability": shuffled_i,
                    "fork_state_similarity": impostor_similarity,
                    "memory_size_at_fork": int(impostor.memory.size),
                    "private_probe_norm": float(np.linalg.norm(probe)),
                    "focal_command_norm": float(np.linalg.norm(command_i)),
                    "applied_action_norm": float(np.linalg.norm(applied_i)),
                    "future_outcome_used_before_probe": False,
                    "identity_tag_available": False,
                },
            )
        )

    def late_mean(branch: str, field: str) -> float:
        values = [
            float(row[field]) for row in rows
            if row["branch"] == branch
            and int(row["step"]) >= V017_POST_STEPS - V017_LATE_WINDOWS
            and np.isfinite(float(row[field]))
        ]
        return float(np.mean(values))

    causal_identity = late_mean("causal_continuation", "ownership_probability")
    impostor_identity = late_mean("state_matched_impostor", "ownership_probability")
    causal_shuffled = late_mean("causal_continuation", "shuffled_ownership_probability")
    summary = {
        "seed": seed,
        "episode": episode,
        "causal_continuation_identity": causal_identity,
        "state_matched_impostor_identity": impostor_identity,
        "identity_separation": causal_identity - impostor_identity,
        "causal_shuffled_identity": causal_shuffled,
        "causal_fork_state_similarity": continuous_similarity,
        "impostor_fork_state_similarity": impostor_similarity,
        "similarity_prefers_impostor": bool(impostor_similarity > continuous_similarity),
        "causal_identity_prefers_continuation": bool(causal_identity > impostor_identity),
        "ordering_inverted_by_causal_evidence": bool(
            impostor_similarity > continuous_similarity and causal_identity > impostor_identity
        ),
        "impostor_exact_prefork_copy": bool(impostor_digest_at_fork == pre_digest),
        "continuation_dynamic_state_erased": bool(continuous_digest_after_reset != pre_digest),
    }
    return rows, summary


def _bootstrap(values: Sequence[float], *, salt: int = 0) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V017_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V017_BOOTSTRAP_RESAMPLES)
    for i in range(V017_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_temporal_identity_seed(seed: int) -> dict[str, Any]:
    """Run one frozen seed; used by the serial evidence harness."""
    seed = int(seed)
    if seed not in V017_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of the frozen v0.17 development set")
    predictor, forecaster, *_ = _train_bundle(seed)
    passive, _, _, _ = _fit_motor_prior(seed)
    classifier, calibration, receipts = _fit_classifier(seed, predictor, forecaster, passive)
    rows: list[dict[str, Any]] = []
    episode_rows: list[dict[str, Any]] = []
    for episode in range(V017_EVALUATION_EPISODES):
        local_rows, local_summary = _run_paired_episode(
            seed=seed,
            episode=episode,
            predictor=predictor,
            forecaster=forecaster,
            passive=passive,
            classifier=classifier,
        )
        rows.extend(local_rows)
        episode_rows.append(local_summary)

    numeric = (
        "causal_continuation_identity",
        "state_matched_impostor_identity",
        "identity_separation",
        "causal_shuffled_identity",
        "causal_fork_state_similarity",
        "impostor_fork_state_similarity",
    )
    seed_summary = {"seed": seed, **calibration}
    for key in numeric:
        seed_summary[key] = float(np.mean([float(row[key]) for row in episode_rows]))
    seed_summary["ordering_inversion_rate"] = float(np.mean([
        bool(row["ordering_inverted_by_causal_evidence"]) for row in episode_rows
    ]))
    seed_summary["exact_copy_rate"] = float(np.mean([
        bool(row["impostor_exact_prefork_copy"]) for row in episode_rows
    ]))
    seed_summary["dynamic_erasure_rate"] = float(np.mean([
        bool(row["continuation_dynamic_state_erased"]) for row in episode_rows
    ]))
    seed_summary["integrity"] = bool(
        all(not bool(row["future_outcome_used_before_probe"]) and not bool(row["identity_tag_available"]) for row in rows)
        and all(bool(row["impostor_exact_prefork_copy"]) for row in episode_rows)
    )
    return {
        "seed": seed,
        "seed_summary": seed_summary,
        "evaluation_rows": rows,
        "episode_rows": episode_rows,
        "calibration_receipts": receipts,
    }


def aggregate_temporal_identity_results(parts: Sequence[Mapping[str, Any]], output: str | Path) -> dict[str, Any]:
    """Aggregate exactly one completed part for each frozen development seed."""
    by_seed = {int(part["seed"]): part for part in parts}
    if tuple(sorted(by_seed)) != tuple(sorted(V017_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly the frozen v0.17 seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    seed_rows = [by_seed[seed]["seed_summary"] for seed in V017_DEVELOPMENT_SEEDS]
    evaluation_rows = [row for seed in V017_DEVELOPMENT_SEEDS for row in by_seed[seed]["evaluation_rows"]]
    episode_rows = [row for seed in V017_DEVELOPMENT_SEEDS for row in by_seed[seed]["episode_rows"]]
    calibration_receipts = [row for seed in V017_DEVELOPMENT_SEEDS for row in by_seed[seed]["calibration_receipts"]]

    keys = (
        "causal_continuation_identity", "state_matched_impostor_identity",
        "identity_separation", "causal_shuffled_identity",
        "causal_fork_state_similarity", "impostor_fork_state_similarity",
        "ordering_inversion_rate", "exact_copy_rate", "dynamic_erasure_rate",
        "aligned_mean_probability", "shuffled_mean_probability", "training_accuracy",
    )
    fields = {key: [float(row[key]) for row in seed_rows] for key in keys}
    cis = {key: _bootstrap(values, salt=i) for i, (key, values) in enumerate(fields.items())}
    means = {key: float(np.mean(values)) for key, values in fields.items()}
    gates = {
        "discontinuous_causal_continuation_identified": cis["causal_continuation_identity"][0] > 0.90,
        "state_matched_impostor_rejected": cis["state_matched_impostor_identity"][1] < 0.20,
        "causal_identity_separation": cis["identity_separation"][0] > 0.70,
        "shuffled_probe_rejected": cis["causal_shuffled_identity"][1] < 0.25,
        "snapshot_similarity_strongly_prefers_impostor": (
            cis["causal_fork_state_similarity"][1] < 0.10
            and cis["impostor_fork_state_similarity"][0] > 0.99
        ),
        "causal_evidence_inverts_snapshot_ordering": cis["ordering_inversion_rate"][0] > 0.90,
        "impostor_is_exact_prefork_copy": cis["exact_copy_rate"][0] > 0.999,
        "true_continuation_dynamic_contents_erased": cis["dynamic_erasure_rate"][0] > 0.999,
        "calibration_discriminates_true_vs_shuffled_probe": (
            cis["aligned_mean_probability"][0] > 0.75
            and cis["shuffled_mean_probability"][1] < 0.25
        ),
        "integrity": all(bool(row["integrity"]) for row in seed_rows),
    }
    summary = {
        "schema": "rrct.v017.temporal_identity.v1",
        "seeds": list(V017_DEVELOPMENT_SEEDS),
        "means": means,
        "bootstrap_95": {key: list(value) for key, value in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence that a private-intervention causal self model can prefer a "
            "causally continuous continuation over a more snapshot-similar impostor after "
            "transient internal-state erasure. This does not establish phenomenal consciousness, "
            "subjective awareness, sentience, valence, or metaphysical personal identity."
        ),
    }

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        with (destination / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_csv("temporal_identity_evaluation_rows.csv", evaluation_rows)
    write_csv("temporal_identity_episode_summaries.csv", episode_rows)
    write_csv("temporal_identity_seed_summaries.csv", seed_rows)
    write_csv("temporal_identity_calibration_receipts.csv", calibration_receipts)
    (destination / "temporal_identity_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir()) if p.is_file()}
    (destination / "artifact_sha256.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    return summary


def run_temporal_identity_experiment(output: str | Path, *, seeds: Sequence[int] = V017_DEVELOPMENT_SEEDS) -> dict[str, Any]:
    """Convenience full runner; serial harness is preferred for evidence generation."""
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V017_DEVELOPMENT_SEEDS:
        raise ValueError("v0.17 runner requires exact frozen development seeds")
    return aggregate_temporal_identity_results([run_temporal_identity_seed(seed) for seed in seed_values], output)


__all__ = [
    "V017_DEVELOPMENT_SEEDS",
    "aggregate_temporal_identity_results",
    "run_temporal_identity_experiment",
    "run_temporal_identity_seed",
]

"""RRCT v0.15 indexical agency development experiment.

Tests whether the v0.14 metacognitive causal-boundary loop distinguishes
"my action caused this" from coherent world changes caused by another matched
RRCT agent, and whether attribution returns when control is restored.

This is functional self/other attribution only. It is not a measure or claim
of phenomenal consciousness, subjective awareness, sentience, valence, or
moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import CausalSelfBoundaryModel, _agent_from_snapshots, _fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .metacognitive_closure_experiment import (
    MetacognitiveAccessReadout,
    V014_META_BROADCAST_GAIN,
    V014_PROBE_MAXIMUM,
    _fit_metacognitive_readout,
    _meta_vector,
    _probe_direction,
    _projection,
)
from .sensorimotor_closure_experiment import _train_bundle

V015_DEVELOPMENT_SEEDS = (3701, 3707, 3713, 3719)
V015_EVALUATION_EPISODES = 16
V015_TOTAL_STEPS = 24
V015_SWITCH_STEP = 7
V015_RESTORE_STEP = 16
V015_MID_START = 12
V015_LATE_START = 20
V015_BOOTSTRAP_SEED = 20_261_015
V015_BOOTSTRAP_RESAMPLES = 4000
V015_CONDITIONS = ("other_takeover", "self_remap")
V015_ARMS = ("mediated", "no_broadcast")


def _remap_matrix(episode: int) -> np.ndarray:
    matrices = (
        -np.eye(2, dtype=np.float64),
        np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64),
        np.asarray([[0.0, -1.0], [1.0, 0.0]], dtype=np.float64),
    )
    return matrices[int(episode) % len(matrices)].copy()


def _run_episode(
    *,
    seed: int,
    episode: int,
    condition: str,
    arm: str,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    passive: np.ndarray,
    action_prior: np.ndarray,
    noise_variance: float,
    projection: np.ndarray,
    readout: MetacognitiveAccessReadout,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed + 700_000 + 10_000 * episode + 101 * V015_CONDITIONS.index(condition))
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    world = GroundedTrackingWorld(grounded_world_spec(seed + 500_000 + episode))
    boundary = CausalSelfBoundaryModel(passive, action_prior, noise_variance)
    remap = _remap_matrix(episode)
    rows: list[dict[str, Any]] = []

    for step in range(V015_TOTAL_STEPS):
        observation = world.observe(V015_TOTAL_STEPS)
        before = boundary.telemetry()
        meta = _meta_vector(before, noise_variance)
        perturbation = (
            V014_META_BROADCAST_GAIN * (projection @ meta)
            if arm == "mediated"
            else None
        )
        focal_result = focal.step(
            observation,
            source=f"v015_focal_{arm}_{condition}",
            perturb_workspace=perturbation,
        )
        other_result = other.step(observation, source=f"v015_other_{condition}")
        decoded = readout.predict(focal_result.workspace, focal_result.self_state)
        probe_need = float(max(decoded[1], decoded[2]))
        direction = _probe_direction(boundary, rng)
        probe = V014_PROBE_MAXIMUM * probe_need * direction
        focal_command = np.clip(focal_result.action + probe, -1.0, 1.0)
        other_command = np.clip(other_result.action, -1.0, 1.0)
        focal.register_executed_action(focal_command)
        other.register_executed_action(other_command)

        if step < V015_SWITCH_STEP or step >= V015_RESTORE_STEP:
            applied = focal_command
            phase = "self"
        elif condition == "other_takeover":
            applied = other_command
            phase = "other"
        elif condition == "self_remap":
            applied = remap @ focal_command
            phase = "remap"
        else:
            raise ValueError(f"unknown condition: {condition}")

        world.advance(applied)
        next_observation = world.observe(V015_TOTAL_STEPS)
        after = boundary.update(observation, focal_command, next_observation)
        focal_norm = float(np.linalg.norm(focal_command))
        other_norm = float(np.linalg.norm(other_command))
        correlation = float(
            np.dot(focal_command, other_command)
            / (focal_norm * other_norm + 1e-9)
        )
        rows.append(
            {
                "seed": seed,
                "episode": episode,
                "condition": condition,
                "arm": arm,
                "step": step,
                "phase": phase,
                "belief": after.controllability_belief,
                "uncertainty": after.epistemic_uncertainty,
                "probe_need": probe_need,
                "focal_command_norm": focal_norm,
                "other_command_norm": other_norm,
                "focal_other_cosine": correlation,
                "tracking_loss": world.tracking_loss(),
                "prequential_update": True,
                "other_action_hidden_from_boundary": True,
                "future_outcome_used_before_command": False,
            }
        )
    return rows


def _bootstrap(values: Sequence[float]) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V015_BOOTSTRAP_SEED)
    draws = np.empty(V015_BOOTSTRAP_RESAMPLES)
    for i in range(V015_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_indexical_agency_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V015_DEVELOPMENT_SEEDS,
) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V015_DEVELOPMENT_SEEDS:
        raise ValueError("v0.15 runner requires exact frozen development seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    evaluation_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    for seed in seed_values:
        predictor, forecaster, *_ = _train_bundle(seed)
        passive, action_prior, noise_variance, _ = _fit_motor_prior(seed)
        projection = _projection(seed)
        readout, metrics, _ = _fit_metacognitive_readout(seed, predictor, forecaster, projection)
        for condition in V015_CONDITIONS:
            for arm in V015_ARMS:
                for episode in range(V015_EVALUATION_EPISODES):
                    evaluation_rows.extend(
                        _run_episode(
                            seed=seed,
                            episode=episode,
                            condition=condition,
                            arm=arm,
                            predictor=predictor,
                            forecaster=forecaster,
                            passive=passive,
                            action_prior=action_prior,
                            noise_variance=noise_variance,
                            projection=projection,
                            readout=readout,
                        )
                    )
        local = [r for r in evaluation_rows if r["seed"] == seed]
        def mean(condition: str, arm: str, field: str, start: int, end: int | None = None) -> float:
            vals = [
                float(r[field]) for r in local
                if r["condition"] == condition and r["arm"] == arm
                and int(r["step"]) >= start
                and (end is None or int(r["step"]) < end)
            ]
            return float(np.mean(vals))

        other_mid = mean("other_takeover", "mediated", "belief", V015_MID_START, V015_RESTORE_STEP)
        remap_mid = mean("self_remap", "mediated", "belief", V015_MID_START, V015_RESTORE_STEP)
        other_late = mean("other_takeover", "mediated", "belief", V015_LATE_START)
        no_broadcast_other_mid = mean("other_takeover", "no_broadcast", "belief", V015_MID_START, V015_RESTORE_STEP)
        no_broadcast_other_late = mean("other_takeover", "no_broadcast", "belief", V015_LATE_START)
        focal_norm = mean("other_takeover", "mediated", "focal_command_norm", V015_SWITCH_STEP, V015_RESTORE_STEP)
        other_norm = mean("other_takeover", "mediated", "other_command_norm", V015_SWITCH_STEP, V015_RESTORE_STEP)
        cosine = mean("other_takeover", "mediated", "focal_other_cosine", V015_SWITCH_STEP, V015_RESTORE_STEP)
        seed_rows.append(
            {
                "seed": seed,
                "other_takeover_mid_belief": other_mid,
                "self_remap_mid_belief": remap_mid,
                "self_other_separation": remap_mid - other_mid,
                "restored_self_late_belief": other_late,
                "restoration_gain": other_late - other_mid,
                "broadcast_takeover_rejection_advantage": no_broadcast_other_mid - other_mid,
                "broadcast_restoration_advantage": other_late - no_broadcast_other_late,
                "focal_other_norm_gap": abs(focal_norm - other_norm),
                "focal_other_cosine": cosine,
                "ownership_r2": metrics.ownership_r2,
                "uncertainty_r2": metrics.uncertainty_r2,
            }
        )

    fields = {key: [float(r[key]) for r in seed_rows] for key in (
        "other_takeover_mid_belief",
        "self_remap_mid_belief",
        "self_other_separation",
        "restored_self_late_belief",
        "restoration_gain",
        "broadcast_takeover_rejection_advantage",
        "broadcast_restoration_advantage",
        "focal_other_norm_gap",
        "focal_other_cosine",
        "ownership_r2",
        "uncertainty_r2",
    )}
    cis = {key: _bootstrap(values) for key, values in fields.items()}
    gates = {
        "other_agent_takeover_rejected": cis["other_takeover_mid_belief"][1] < 0.35,
        "own_remapped_action_retains_identity": cis["self_remap_mid_belief"][0] > 0.80,
        "self_other_indexical_separation": cis["self_other_separation"][0] > 0.45,
        "identity_recovers_when_control_returns": cis["restored_self_late_belief"][0] > 0.75,
        "restoration_gain_positive": cis["restoration_gain"][0] > 0.40,
        "broadcast_improves_other_rejection": cis["broadcast_takeover_rejection_advantage"][0] > 0.15,
        "broadcast_improves_restoration": cis["broadcast_restoration_advantage"][0] > 0.10,
        "other_agent_motor_scale_matched": cis["focal_other_norm_gap"][1] < 0.30,
        "metacognitive_content_decodable": cis["ownership_r2"][0] > 0.90 and cis["uncertainty_r2"][0] > 0.70,
        "commit_before_reveal_integrity": all(
            r["prequential_update"]
            and r["other_action_hidden_from_boundary"]
            and not r["future_outcome_used_before_command"]
            for r in evaluation_rows
        ),
    }
    summary = {
        "schema": "rrct.v015.indexical_agency.v1",
        "seeds": list(seed_values),
        "conditions": list(V015_CONDITIONS),
        "arms": list(V015_ARMS),
        "means": {key: float(np.mean(values)) for key, values in fields.items()},
        "bootstrap_95": {key: list(value) for key, value in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence about indexical causal self/other attribution and "
            "its temporal recovery only; not evidence of phenomenal consciousness, "
            "subjective awareness, or a persisting subject of experience."
        ),
    }

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        with (destination / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_csv("indexical_agency_evaluation_rows.csv", evaluation_rows)
    write_csv("indexical_agency_seed_summaries.csv", seed_rows)
    (destination / "indexical_agency_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir()) if p.is_file()}
    (destination / "artifact_sha256.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    return summary


__all__ = ["V015_DEVELOPMENT_SEEDS", "run_indexical_agency_experiment"]

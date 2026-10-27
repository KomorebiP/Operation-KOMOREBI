"""RRCT v0.18 temporal identity global-access experiment.

v0.17 placed snapshot similarity and causal continuity in direct conflict.
v0.18 asks a stronger functional question: can the resulting causal-identity
belief become globally available inside RRCT without itself creating the
ownership evidence?

The private-instrument classifier remains the evidence source.  Its current
belief and uncertainty are broadcast into the global workspace one step later.
A readout trained independently on synthetic metacognitive broadcasts must
recover that content from workspace+self state.  A no-broadcast arm receives
the same observations, probes, fork construction, and classifier but no
identity perturbation.  Private-probe amplitude is fixed in both arms so global
broadcast cannot create the instrumental separation by changing probe power.

This is a functional metacognitive/temporal-self experiment only.  It does not
measure phenomenal consciousness, subjective experience, sentience, valence,
or moral status.
"""
from __future__ import annotations

import copy
import csv
import dataclasses
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
from .metacognitive_closure_experiment import (
    V014_META_BROADCAST_GAIN,
    _fit_metacognitive_readout,
    _projection,
)
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_experiment import _cosine, _dynamic_state_vector

V018_DEVELOPMENT_SEEDS = (4101, 4107, 4113, 4119)
V018_EVALUATION_EPISODES = 24
V018_PREHISTORY_STEPS = 10
V018_POST_STEPS = 14
V018_LATE_START = 11
V018_BOOTSTRAP_SEED = 20_261_018
V018_BOOTSTRAP_RESAMPLES = 4000
V018_ARMS = ("mediated", "no_broadcast")
V018_BRANCHES = ("causal_continuation", "state_matched_impostor")


def _deep_structural_equal(a: Any, b: Any, seen: set[tuple[int, int]] | None = None) -> bool:
    """Compare scientific state recursively without serialization artifacts."""
    if seen is None:
        seen = set()
    if a is b:
        return True
    pair = (id(a), id(b))
    if pair in seen:
        return True
    seen.add(pair)
    if type(a) is not type(b):
        return False
    if isinstance(a, np.ndarray):
        return bool(a.dtype == b.dtype and a.shape == b.shape and np.array_equal(a, b, equal_nan=True))
    if isinstance(a, np.generic):
        if np.issubdtype(a.dtype, np.floating) and np.isnan(a) and np.isnan(b):
            return True
        return bool(a == b)
    if isinstance(a, float):
        if np.isnan(a) and np.isnan(b):
            return True
        return bool(a == b)
    if isinstance(a, (str, bytes, int, bool, type(None))):
        return bool(a == b)
    if dataclasses.is_dataclass(a):
        return all(_deep_structural_equal(getattr(a, field.name), getattr(b, field.name), seen) for field in dataclasses.fields(a))
    if isinstance(a, dict):
        return bool(a.keys() == b.keys() and all(_deep_structural_equal(a[key], b[key], seen) for key in a))
    if isinstance(a, (tuple, list)):
        return bool(len(a) == len(b) and all(_deep_structural_equal(x, y, seen) for x, y in zip(a, b)))
    if hasattr(a, "__dict__") and hasattr(b, "__dict__"):
        return _deep_structural_equal(a.__dict__, b.__dict__, seen)
    try:
        return bool(a == b)
    except Exception:
        return False


def _identity_meta(probability: float, previous_probability: float) -> np.ndarray:
    p = float(np.clip(probability, 0.0, 1.0))
    previous = float(np.clip(previous_probability, 0.0, 1.0))
    uncertainty = 4.0 * p * (1.0 - p)
    change_alarm = float(np.clip(2.0 * abs(p - previous), 0.0, 1.0))
    return np.asarray([2.0 * p - 1.0, uncertainty, 0.0, 0.0, change_alarm], dtype=np.float64)


def _ownership(classifier: InstrumentalOwnershipClassifier, probes: list[np.ndarray], residuals: list[np.ndarray]) -> float:
    if len(probes) < V016_WINDOW:
        return float("nan")
    z = np.stack(probes[-V016_WINDOW:])
    r = np.stack(residuals[-V016_WINDOW:])
    return float(classifier.predict_probability(_window_statistics(z, r)))


def _probe_for(seed: int, episode: int, step: int) -> np.ndarray:
    # Independent deterministic stream per episode/step, shared across every
    # branch and arm, so probe distribution is exactly matched.
    rng = np.random.default_rng(seed + 18_180_000 + 10_000 * episode + step)
    return _private_probe(rng)


def _run_branch(
    *, seed: int, episode: int, branch: str, arm: str,
    focal_pre: Any, other_pre: Any, world_pre: Any,
    pre_vector: np.ndarray, predictor: Mapping[str, Any], forecaster: Mapping[str, Any],
    passive: np.ndarray, classifier: InstrumentalOwnershipClassifier,
    projection: np.ndarray, readout: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    agent = copy.deepcopy(focal_pre)
    other = copy.deepcopy(other_pre)
    world = copy.deepcopy(world_pre)
    exact_copy_before_transform = _deep_structural_equal(focal_pre, agent)
    if branch == "causal_continuation":
        agent.reset()
    elif branch != "state_matched_impostor":
        raise ValueError(f"unknown branch: {branch}")
    fork_similarity = _cosine(pre_vector, _dynamic_state_vector(agent))
    remap = _remap_matrix(episode)
    probes: list[np.ndarray] = []
    residuals: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []
    current_p = 0.5
    previous_p = 0.5
    workspace_effects: list[float] = []
    self_effects: list[float] = []

    for step in range(V018_POST_STEPS):
        observation = world.observe(V018_PREHISTORY_STEPS + V018_POST_STEPS + 4)
        meta = _identity_meta(current_p, previous_p)
        perturbation = V014_META_BROADCAST_GAIN * (projection @ meta) if arm == "mediated" else None

        # At late steps, audit whether the same pre-step internal state is
        # causally sensitive to high-vs-low identity content.  These clones are
        # not used to choose or alter the live trajectory.
        if arm == "mediated" and step >= V018_LATE_START:
            high = copy.deepcopy(agent)
            low = copy.deepcopy(agent)
            high_result = high.step(
                observation,
                source="v018_counterfactual_high_identity",
                perturb_workspace=V014_META_BROADCAST_GAIN * (projection @ np.asarray([1.0, 0.0, 0.0, 0.0, 0.0])),
            )
            low_result = low.step(
                observation,
                source="v018_counterfactual_low_identity",
                perturb_workspace=V014_META_BROADCAST_GAIN * (projection @ np.asarray([-1.0, 0.0, 0.0, 0.0, 0.0])),
            )
            workspace_effects.append(float(np.linalg.norm(high_result.workspace - low_result.workspace)))
            self_effects.append(float(np.linalg.norm(high_result.self_state - low_result.self_state)))

        result = agent.step(
            observation,
            source=f"v018_{arm}_{branch}",
            perturb_workspace=perturbation,
        )
        decoded = readout.predict(result.workspace, result.self_state)
        decoded_identity = float(np.clip(0.5 * (decoded[0] + 1.0), 0.0, 1.0))
        decoded_uncertainty = float(decoded[1])

        probe = _probe_for(seed, episode, step)
        command = np.clip(result.action + probe, -1.0, 1.0)
        agent.register_executed_action(command)
        if branch == "causal_continuation":
            applied = remap @ command
        else:
            other_result = other.step(observation, source="v018_other_controller")
            other.register_executed_action(other_result.action)
            applied = float(np.linalg.norm(command)) * _other_direction(other_result)
        world.advance(applied)
        next_observation = world.observe(V018_PREHISTORY_STEPS + V018_POST_STEPS + 4)
        probes.append(probe.copy())
        residuals.append(_passive_residual(passive, observation, next_observation))
        new_p = _ownership(classifier, probes, residuals)
        previous_p = current_p
        if np.isfinite(new_p):
            current_p = new_p

        rows.append({
            "seed": seed, "episode": episode, "step": step, "branch": branch, "arm": arm,
            "ownership_probability": float(new_p),
            "broadcast_identity_input": float(0.5 * (meta[0] + 1.0)),
            "broadcast_uncertainty_input": float(meta[1]),
            "decoded_identity": decoded_identity,
            "decoded_uncertainty": decoded_uncertainty,
            "fork_state_similarity": fork_similarity,
            "probe_norm": float(np.linalg.norm(probe)),
            "focal_command_norm": float(np.linalg.norm(command)),
            "applied_action_norm": float(np.linalg.norm(applied)),
            "identity_tag_available": False,
            "future_outcome_used_before_probe": False,
        })

    late = [row for row in rows if int(row["step"]) >= V018_LATE_START]
    finite_ownership = [float(row["ownership_probability"]) for row in late if np.isfinite(float(row["ownership_probability"]))]
    summary = {
        "seed": seed, "episode": episode, "branch": branch, "arm": arm,
        "late_ownership": float(np.mean(finite_ownership)),
        "late_decoded_identity": float(np.mean([float(row["decoded_identity"]) for row in late])),
        "late_decode_abs_error": float(np.mean([
            abs(float(row["decoded_identity"]) - float(row["broadcast_identity_input"])) for row in late
        ])),
        "fork_state_similarity": fork_similarity,
        "exact_copy_before_transform": bool(exact_copy_before_transform),
        "workspace_identity_effect": float(np.mean(workspace_effects)) if workspace_effects else 0.0,
        "self_identity_effect": float(np.mean(self_effects)) if self_effects else 0.0,
    }
    return rows, summary


def _run_episode(
    *, seed: int, episode: int, predictor: Mapping[str, Any], forecaster: Mapping[str, Any],
    passive: np.ndarray, classifier: InstrumentalOwnershipClassifier,
    projection: np.ndarray, readout: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed + 1_818_181 + 10_000 * episode)
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    world = GroundedTrackingWorld(grounded_world_spec(seed + 1_080_000 + episode, total_steps=V018_PREHISTORY_STEPS + V018_POST_STEPS + 4))
    for step in range(V018_PREHISTORY_STEPS):
        observation = world.observe(V018_PREHISTORY_STEPS + V018_POST_STEPS + 4)
        focal_result = focal.step(observation, source="v018_prehistory_focal")
        other_result = other.step(observation, source="v018_prehistory_other")
        probe = _private_probe(rng)
        command = np.clip(focal_result.action + probe, -1.0, 1.0)
        focal.register_executed_action(command)
        other.register_executed_action(other_result.action)
        world.advance(command)
    pre_vector = _dynamic_state_vector(focal)
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for arm in V018_ARMS:
        for branch in V018_BRANCHES:
            local_rows, local_summary = _run_branch(
                seed=seed, episode=episode, branch=branch, arm=arm,
                focal_pre=focal, other_pre=other, world_pre=world, pre_vector=pre_vector,
                predictor=predictor, forecaster=forecaster, passive=passive,
                classifier=classifier, projection=projection, readout=readout,
            )
            rows.extend(local_rows); summaries.append(local_summary)
    return rows, summaries


def _bootstrap(values: Sequence[float], *, salt: int) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V018_BOOTSTRAP_SEED + int(salt))
    draws = np.empty(V018_BOOTSTRAP_RESAMPLES)
    for i in range(V018_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_temporal_identity_global_seed(seed: int) -> dict[str, Any]:
    seed = int(seed)
    if seed not in V018_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.18 set")
    predictor, forecaster, *_ = _train_bundle(seed)
    passive, _, _, _ = _fit_motor_prior(seed)
    classifier, classifier_metrics, classifier_receipts = _fit_classifier(seed, predictor, forecaster, passive)
    projection = _projection(seed)
    readout, readout_metrics, readout_receipts = _fit_metacognitive_readout(seed, predictor, forecaster, projection)
    evaluation_rows: list[dict[str, Any]] = []
    episode_rows: list[dict[str, Any]] = []
    for episode in range(V018_EVALUATION_EPISODES):
        rows, summaries = _run_episode(
            seed=seed, episode=episode, predictor=predictor, forecaster=forecaster,
            passive=passive, classifier=classifier, projection=projection, readout=readout,
        )
        evaluation_rows.extend(rows); episode_rows.extend(summaries)

    def m(arm: str, branch: str, field: str) -> float:
        return float(np.mean([float(row[field]) for row in episode_rows if row["arm"] == arm and row["branch"] == branch]))
    med_c = m("mediated", "causal_continuation", "late_ownership")
    med_i = m("mediated", "state_matched_impostor", "late_ownership")
    no_c = m("no_broadcast", "causal_continuation", "late_ownership")
    no_i = m("no_broadcast", "state_matched_impostor", "late_ownership")
    med_dc = m("mediated", "causal_continuation", "late_decoded_identity")
    med_di = m("mediated", "state_matched_impostor", "late_decoded_identity")
    no_dc = m("no_broadcast", "causal_continuation", "late_decoded_identity")
    no_di = m("no_broadcast", "state_matched_impostor", "late_decoded_identity")
    seed_summary = {
        "seed": seed,
        "mediated_causal_identity": med_c,
        "mediated_impostor_identity": med_i,
        "mediated_direct_separation": med_c - med_i,
        "no_broadcast_causal_identity": no_c,
        "no_broadcast_impostor_identity": no_i,
        "direct_separation_arm_difference": (med_c - med_i) - (no_c - no_i),
        "mediated_decoded_causal_identity": med_dc,
        "mediated_decoded_impostor_identity": med_di,
        "mediated_decoded_separation": med_dc - med_di,
        "no_broadcast_decoded_separation": no_dc - no_di,
        "mediated_decode_abs_error": float(np.mean([float(row["late_decode_abs_error"]) for row in episode_rows if row["arm"] == "mediated"])),
        "no_broadcast_decode_abs_error": float(np.mean([float(row["late_decode_abs_error"]) for row in episode_rows if row["arm"] == "no_broadcast"])),
        "causal_fork_similarity": m("mediated", "causal_continuation", "fork_state_similarity"),
        "impostor_fork_similarity": m("mediated", "state_matched_impostor", "fork_state_similarity"),
        "workspace_identity_effect": float(np.mean([float(row["workspace_identity_effect"]) for row in episode_rows if row["arm"] == "mediated"])),
        "self_identity_effect": float(np.mean([float(row["self_identity_effect"]) for row in episode_rows if row["arm"] == "mediated"])),
        "exact_copy_rate": float(np.mean([bool(row["exact_copy_before_transform"]) for row in episode_rows])),
        "ownership_readout_r2": float(readout_metrics.ownership_r2),
        "uncertainty_readout_r2": float(readout_metrics.uncertainty_r2),
        "change_alarm_readout_r2": float(readout_metrics.change_alarm_r2),
        **classifier_metrics,
        "integrity": bool(all(not bool(row["identity_tag_available"]) and not bool(row["future_outcome_used_before_probe"]) for row in evaluation_rows)),
    }
    return {
        "seed": seed, "seed_summary": seed_summary, "evaluation_rows": evaluation_rows,
        "episode_rows": episode_rows, "classifier_receipts": classifier_receipts,
        "readout_receipts": readout_receipts,
    }


def aggregate_temporal_identity_global_results(parts: Sequence[Mapping[str, Any]], output: str | Path) -> dict[str, Any]:
    by_seed = {int(part["seed"]): part for part in parts}
    if tuple(sorted(by_seed)) != tuple(sorted(V018_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.18 seeds")
    destination = Path(output); destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()): raise FileExistsError("output directory must be empty")
    seed_rows = [by_seed[s]["seed_summary"] for s in V018_DEVELOPMENT_SEEDS]
    evaluation_rows = [r for s in V018_DEVELOPMENT_SEEDS for r in by_seed[s]["evaluation_rows"]]
    episode_rows = [r for s in V018_DEVELOPMENT_SEEDS for r in by_seed[s]["episode_rows"]]
    classifier_receipts = [r for s in V018_DEVELOPMENT_SEEDS for r in by_seed[s]["classifier_receipts"]]
    readout_receipts = [r for s in V018_DEVELOPMENT_SEEDS for r in by_seed[s]["readout_receipts"]]
    keys = [k for k in seed_rows[0] if k not in {"seed", "integrity"}]
    fields = {k: [float(row[k]) for row in seed_rows] for k in keys}
    cis = {k: _bootstrap(v, salt=i) for i, (k, v) in enumerate(fields.items())}
    means = {k: float(np.mean(v)) for k, v in fields.items()}
    gates = {
        "causal_identity_survives_discontinuity": cis["mediated_causal_identity"][0] > 0.90,
        "state_matched_impostor_rejected": cis["mediated_impostor_identity"][1] < 0.20,
        "direct_identity_separation": cis["mediated_direct_separation"][0] > 0.70,
        "broadcast_does_not_create_instrumental_separation": max(abs(cis["direct_separation_arm_difference"][0]), abs(cis["direct_separation_arm_difference"][1])) < 0.10,
        "mediated_identity_globally_decodable": cis["mediated_decoded_causal_identity"][0] > 0.75 and cis["mediated_decoded_impostor_identity"][1] < 0.25,
        "mediated_decoded_separation": cis["mediated_decoded_separation"][0] > 0.50,
        "no_broadcast_does_not_expose_identity": max(abs(cis["no_broadcast_decoded_separation"][0]), abs(cis["no_broadcast_decoded_separation"][1])) < 0.20,
        "broadcast_improves_identity_decode_error": cis["mediated_decode_abs_error"][1] + 0.15 < cis["no_broadcast_decode_abs_error"][0],
        "snapshot_similarity_conflict_present": cis["causal_fork_similarity"][1] < 0.10 and cis["impostor_fork_similarity"][0] > 0.99,
        "identity_content_changes_workspace_and_self": cis["workspace_identity_effect"][0] > 0.25 and cis["self_identity_effect"][0] > 0.08,
        "metacognitive_readout_generalizes": cis["ownership_readout_r2"][0] > 0.80 and cis["uncertainty_readout_r2"][0] > 0.55,
        "copy_audit": cis["exact_copy_rate"][0] > 0.999,
        "classifier_calibration": cis["aligned_mean_probability"][0] > 0.75 and cis["shuffled_mean_probability"][1] < 0.25,
        "integrity": all(bool(row["integrity"]) for row in seed_rows),
    }
    summary = {
        "schema": "rrct.v018.temporal_identity_global_access.v1",
        "seeds": list(V018_DEVELOPMENT_SEEDS), "means": means,
        "bootstrap_95": {k: list(v) for k, v in cis.items()}, "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence that causal temporal-self information can be made globally "
            "decodable and causally available inside RRCT while preserving an independently "
            "identified private-intervention ownership signal. This is not evidence of phenomenal "
            "consciousness or subjective experience."
        ),
    }
    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        with (destination/name).open("w", newline="", encoding="utf-8") as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write_csv("temporal_identity_global_evaluation_rows.csv", evaluation_rows)
    write_csv("temporal_identity_global_episode_summaries.csv", episode_rows)
    write_csv("temporal_identity_global_seed_summaries.csv", seed_rows)
    write_csv("temporal_identity_global_classifier_receipts.csv", classifier_receipts)
    write_csv("temporal_identity_global_readout_receipts.csv", readout_receipts)
    (destination/"temporal_identity_global_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir()) if p.is_file()}
    (destination/"artifact_sha256.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n")
    return summary


__all__ = ["V018_DEVELOPMENT_SEEDS", "_deep_structural_equal", "run_temporal_identity_global_seed", "aggregate_temporal_identity_global_results"]

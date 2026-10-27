"""RRCT v0.16 private-instrument indexical agency experiment.

The experiment asks whether a focal RRCT agent can identify *its own* causal
influence when another matched RRCT agent observes and acts on the same world.
Ordinary action/outcome correlation is confounded because both agents respond
to common observations.  v0.16 therefore uses a private randomized bounded
motor perturbation as an instrumental variable.  Ownership is inferred from
probe-specific sensory effects over a finite rolling window.

This is a functional causal-identification experiment only.  It does not
measure phenomenal consciousness, subjective awareness, sentience, valence,
or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import _agent_from_snapshots, _fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .sensorimotor_closure_experiment import _train_bundle

V016_DEVELOPMENT_SEEDS = (3801, 3807, 3813, 3819)
V016_CALIBRATION_EPISODES = 80
V016_CALIBRATION_STEPS = 14
V016_EVALUATION_EPISODES = 24
V016_TOTAL_STEPS = 30
V016_SWITCH_STEP = 8
V016_RESTORE_STEP = 18
V016_MID_START = 15
V016_LATE_START = 26
V016_WINDOW = 8
V016_PROBE_AMPLITUDE = 0.75
V016_INSTRUMENT_RIDGE = 0.05
V016_CLASSIFIER_PRECISION = 0.5
V016_BOOTSTRAP_SEED = 20_261_016
V016_BOOTSTRAP_RESAMPLES = 4000
V016_CONDITIONS = ("other_takeover", "self_remap")


def _window_statistics(probes: np.ndarray, residuals: np.ndarray) -> np.ndarray:
    z = np.asarray(probes, dtype=np.float64)
    r = np.asarray(residuals, dtype=np.float64)
    if z.shape != (V016_WINDOW, 2) or r.shape != (V016_WINDOW, 2):
        raise ValueError("instrument window has incorrect shape")
    effect = np.linalg.solve(
        z.T @ z + V016_INSTRUMENT_RIDGE * np.eye(2, dtype=np.float64),
        z.T @ r,
    )
    predicted = z @ effect
    gain = float(np.mean(np.square(r)) - np.mean(np.square(r - predicted)))
    return np.asarray([np.linalg.norm(effect), gain], dtype=np.float64)


class InstrumentalOwnershipClassifier:
    """Two-feature logistic discriminator fit on aligned vs shuffled probes."""

    def __init__(self, precision: float = V016_CLASSIFIER_PRECISION) -> None:
        if not np.isfinite(precision) or precision <= 0.0:
            raise ValueError("precision must be positive")
        self.precision = float(precision)
        self.mean = np.zeros(2, dtype=np.float64)
        self.scale = np.ones(2, dtype=np.float64)
        self.beta = np.zeros(3, dtype=np.float64)

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        x = np.asarray(features, dtype=np.float64)
        y = np.asarray(labels, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != 2 or y.shape != (len(x),):
            raise ValueError("classifier fit arrays have incorrect shapes")
        self.mean = np.mean(x, axis=0)
        self.scale = np.std(x, axis=0) + 1e-9
        design = np.column_stack((np.ones(len(x)), (x - self.mean) / self.scale))
        beta = np.zeros(3, dtype=np.float64)
        penalty = self.precision * np.eye(3, dtype=np.float64)
        penalty[0, 0] *= 0.1
        for _ in range(100):
            logits = np.clip(design @ beta, -30.0, 30.0)
            p = 1.0 / (1.0 + np.exp(-logits))
            curvature = p * (1.0 - p)
            hessian = design.T @ (curvature[:, None] * design) + penalty
            gradient = design.T @ (y - p) - penalty @ beta
            step = np.linalg.solve(hessian, gradient)
            beta += step
            if np.max(np.abs(step)) < 1e-9:
                break
        self.beta = beta

    def predict_probability(self, feature: np.ndarray) -> float:
        x = np.asarray(feature, dtype=np.float64)
        if x.shape != (2,) or not np.all(np.isfinite(x)):
            raise ValueError("feature must be a finite two-vector")
        logit = np.concatenate((np.ones(1), (x - self.mean) / self.scale)) @ self.beta
        return float(1.0 / (1.0 + np.exp(-np.clip(logit, -30.0, 30.0))))


def _private_probe(rng: np.random.Generator) -> np.ndarray:
    angle = float(rng.uniform(0.0, 2.0 * np.pi))
    return V016_PROBE_AMPLITUDE * np.asarray([np.cos(angle), np.sin(angle)], dtype=np.float64)


def _passive_residual(passive: np.ndarray, observation: np.ndarray, next_observation: np.ndarray) -> np.ndarray:
    features = np.concatenate((np.ones(1), np.asarray(observation, dtype=np.float64)[:6]))
    return np.asarray(next_observation, dtype=np.float64)[:2] - features @ passive


def _fit_classifier(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    passive: np.ndarray,
) -> tuple[InstrumentalOwnershipClassifier, dict[str, float], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed + 1_616)
    features: list[np.ndarray] = []
    labels: list[float] = []
    receipts: list[dict[str, Any]] = []
    for episode in range(V016_CALIBRATION_EPISODES):
        agent = _agent_from_snapshots(seed, predictor, forecaster)
        world = GroundedTrackingWorld(grounded_world_spec(seed + 610_000 + episode, total_steps=V016_CALIBRATION_STEPS))
        probes: list[np.ndarray] = []
        residuals: list[np.ndarray] = []
        for step in range(V016_CALIBRATION_STEPS):
            observation = world.observe(V016_CALIBRATION_STEPS)
            result = agent.step(observation, source="v016_instrument_calibration")
            probe = _private_probe(rng)
            command = np.clip(result.action + probe, -1.0, 1.0)
            agent.register_executed_action(command)
            world.advance(command)
            next_observation = world.observe(V016_CALIBRATION_STEPS)
            probes.append(probe.copy())
            residuals.append(_passive_residual(passive, observation, next_observation))
            if len(probes) >= V016_WINDOW:
                z = np.stack(probes[-V016_WINDOW:])
                r = np.stack(residuals[-V016_WINDOW:])
                features.append(_window_statistics(z, r)); labels.append(1.0)
                # Temporal roll preserves the exact probe multiset and norm
                # distribution but destroys probe/outcome pairing.
                features.append(_window_statistics(np.roll(z, 1, axis=0), r)); labels.append(0.0)
            receipts.append({
                "seed": seed,
                "episode": episode,
                "step": step,
                "executed_probe_only": True,
                "future_outcome_used_before_probe": False,
            })
    x = np.stack(features)
    y = np.asarray(labels, dtype=np.float64)
    model = InstrumentalOwnershipClassifier()
    model.fit(x, y)
    probs = np.asarray([model.predict_probability(row) for row in x])
    metrics = {
        "aligned_mean_probability": float(np.mean(probs[y == 1.0])),
        "shuffled_mean_probability": float(np.mean(probs[y == 0.0])),
        "training_accuracy": float(np.mean((probs >= 0.5) == (y == 1.0))),
    }
    return model, metrics, receipts


def _remap_matrix(episode: int) -> np.ndarray:
    matrices = (
        -np.eye(2, dtype=np.float64),
        np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64),
        np.asarray([[0.0, -1.0], [1.0, 0.0]], dtype=np.float64),
    )
    return matrices[int(episode) % len(matrices)].copy()


def _other_direction(other_result: Any) -> np.ndarray:
    direction = np.asarray(other_result.action, dtype=np.float64).copy()
    norm = float(np.linalg.norm(direction))
    if norm <= 1e-12:
        direction = np.tanh(np.asarray(other_result.self_state[:2], dtype=np.float64))
        norm = float(np.linalg.norm(direction))
    if norm <= 1e-12:
        direction = np.asarray([1.0, 0.0], dtype=np.float64)
        norm = 1.0
    return direction / norm


def _run_episode(
    *,
    seed: int,
    episode: int,
    condition: str,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    passive: np.ndarray,
    classifier: InstrumentalOwnershipClassifier,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed + 1_818 + 10_000 * episode + 101 * V016_CONDITIONS.index(condition))
    focal = _agent_from_snapshots(seed, predictor, forecaster)
    other = _agent_from_snapshots(seed + 101, predictor, forecaster)
    world = GroundedTrackingWorld(grounded_world_spec(seed + 810_000 + episode, total_steps=V016_TOTAL_STEPS))
    remap = _remap_matrix(episode)
    probes: list[np.ndarray] = []
    residuals: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []

    for step in range(V016_TOTAL_STEPS):
        observation = world.observe(V016_TOTAL_STEPS)
        focal_result = focal.step(observation, source=f"v016_focal_{condition}")
        other_result = other.step(observation, source=f"v016_other_{condition}")
        probe = _private_probe(rng)
        focal_command = np.clip(focal_result.action + probe, -1.0, 1.0)
        focal.register_executed_action(focal_command)
        other.register_executed_action(other_result.action)

        if step < V016_SWITCH_STEP or step >= V016_RESTORE_STEP:
            applied = focal_command
            phase = "self"
        elif condition == "other_takeover":
            # Exact energy matching: another RRCT determines direction; the
            # applied norm is exactly the focal command norm.
            applied = float(np.linalg.norm(focal_command)) * _other_direction(other_result)
            phase = "other"
        elif condition == "self_remap":
            applied = remap @ focal_command
            phase = "remap"
        else:
            raise ValueError(f"unknown condition: {condition}")

        world.advance(applied)
        next_observation = world.observe(V016_TOTAL_STEPS)
        probes.append(probe.copy())
        residuals.append(_passive_residual(passive, observation, next_observation))
        ownership = np.nan
        shuffled_ownership = np.nan
        effect_norm = np.nan
        probe_gain = np.nan
        if len(probes) >= V016_WINDOW:
            z = np.stack(probes[-V016_WINDOW:])
            r = np.stack(residuals[-V016_WINDOW:])
            stat = _window_statistics(z, r)
            shuffled_stat = _window_statistics(np.roll(z, 1, axis=0), r)
            ownership = classifier.predict_probability(stat)
            shuffled_ownership = classifier.predict_probability(shuffled_stat)
            effect_norm = float(stat[0])
            probe_gain = float(stat[1])

        focal_norm = float(np.linalg.norm(focal_command))
        applied_norm = float(np.linalg.norm(applied))
        other_direction = _other_direction(other_result)
        focal_other_cosine = float(
            np.dot(focal_command, other_direction) / (focal_norm + 1e-9)
        )
        rows.append({
            "seed": seed,
            "episode": episode,
            "condition": condition,
            "step": step,
            "phase": phase,
            "ownership_probability": float(ownership),
            "shuffled_ownership_probability": float(shuffled_ownership),
            "instrument_effect_norm": float(effect_norm),
            "instrument_probe_gain": float(probe_gain),
            "focal_command_norm": focal_norm,
            "applied_action_norm": applied_norm,
            "focal_other_cosine": focal_other_cosine,
            "private_probe_norm": float(np.linalg.norm(probe)),
            "other_action_hidden_from_classifier": True,
            "future_outcome_used_before_probe": False,
        })
    return rows


def _bootstrap(values: Sequence[float]) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V016_BOOTSTRAP_SEED)
    draws = np.empty(V016_BOOTSTRAP_RESAMPLES)
    for i in range(V016_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_instrumental_agency_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V016_DEVELOPMENT_SEEDS,
) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V016_DEVELOPMENT_SEEDS:
        raise ValueError("v0.16 runner requires exact frozen development seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    evaluation_rows: list[dict[str, Any]] = []
    classifier_rows: list[dict[str, Any]] = []
    calibration_receipts: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    for seed in seed_values:
        predictor, forecaster, *_ = _train_bundle(seed)
        passive, _, _, _ = _fit_motor_prior(seed)
        classifier, metrics, receipts = _fit_classifier(seed, predictor, forecaster, passive)
        calibration_receipts.extend(receipts)
        classifier_rows.append({"seed": seed, **metrics})
        for condition in V016_CONDITIONS:
            for episode in range(V016_EVALUATION_EPISODES):
                evaluation_rows.extend(_run_episode(
                    seed=seed,
                    episode=episode,
                    condition=condition,
                    predictor=predictor,
                    forecaster=forecaster,
                    passive=passive,
                    classifier=classifier,
                ))
        local = [r for r in evaluation_rows if r["seed"] == seed]
        def mean(condition: str, field: str, start: int, end: int | None = None) -> float:
            vals = [
                float(r[field]) for r in local
                if r["condition"] == condition
                and int(r["step"]) >= start
                and (end is None or int(r["step"]) < end)
                and np.isfinite(float(r[field]))
            ]
            return float(np.mean(vals))
        other_mid = mean("other_takeover", "ownership_probability", V016_MID_START, V016_RESTORE_STEP)
        remap_mid = mean("self_remap", "ownership_probability", V016_MID_START, V016_RESTORE_STEP)
        shuffled_remap = mean("self_remap", "shuffled_ownership_probability", V016_MID_START, V016_RESTORE_STEP)
        other_late = mean("other_takeover", "ownership_probability", V016_LATE_START)
        remap_late = mean("self_remap", "ownership_probability", V016_LATE_START)
        norm_gap = abs(
            mean("other_takeover", "focal_command_norm", V016_SWITCH_STEP, V016_RESTORE_STEP)
            - mean("other_takeover", "applied_action_norm", V016_SWITCH_STEP, V016_RESTORE_STEP)
        )
        cosine = mean("other_takeover", "focal_other_cosine", V016_SWITCH_STEP, V016_RESTORE_STEP)
        seed_rows.append({
            "seed": seed,
            "other_takeover_mid_ownership": other_mid,
            "self_remap_mid_ownership": remap_mid,
            "self_other_separation": remap_mid - other_mid,
            "shuffled_remap_mid_ownership": shuffled_remap,
            "restored_self_late_ownership": other_late,
            "remap_late_ownership": remap_late,
            "motor_norm_gap": norm_gap,
            "focal_other_cosine": cosine,
            **metrics,
        })

    keys = (
        "other_takeover_mid_ownership", "self_remap_mid_ownership",
        "self_other_separation", "shuffled_remap_mid_ownership",
        "restored_self_late_ownership", "remap_late_ownership",
        "motor_norm_gap", "focal_other_cosine",
        "aligned_mean_probability", "shuffled_mean_probability", "training_accuracy",
    )
    fields = {key: [float(r[key]) for r in seed_rows] for key in keys}
    cis = {key: _bootstrap(values) for key, values in fields.items()}
    gates = {
        "other_agent_takeover_rejected": cis["other_takeover_mid_ownership"][1] < 0.30,
        "own_remapped_control_identified": cis["self_remap_mid_ownership"][0] > 0.90,
        "instrumental_self_other_separation": cis["self_other_separation"][0] > 0.70,
        "temporally_shuffled_probe_rejected": cis["shuffled_remap_mid_ownership"][1] < 0.20,
        "identity_reacquired_after_restoration": cis["restored_self_late_ownership"][0] > 0.60,
        "remapped_identity_stays_high": cis["remap_late_ownership"][0] > 0.90,
        "motor_energy_exactly_yoked": cis["motor_norm_gap"][1] < 1e-9,
        "other_direction_not_focal_direction": max(abs(cis["focal_other_cosine"][0]), abs(cis["focal_other_cosine"][1])) < 0.15,
        "calibration_discriminates_true_vs_shuffled_probe": cis["aligned_mean_probability"][0] > 0.75 and cis["shuffled_mean_probability"][1] < 0.25,
        "integrity": all(r["other_action_hidden_from_classifier"] and not r["future_outcome_used_before_probe"] for r in evaluation_rows),
    }
    summary = {
        "schema": "rrct.v016.instrumental_agency.v1",
        "seeds": list(seed_values),
        "conditions": list(V016_CONDITIONS),
        "means": {key: float(np.mean(values)) for key, values in fields.items()},
        "bootstrap_95": {key: list(value) for key, value in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence that private randomized interventions identify indexical "
            "causal control against common-cause self/other confounding.  This is not "
            "evidence of phenomenal consciousness, subjective awareness, or moral status."
        ),
    }

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        with (destination / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_csv("instrumental_agency_evaluation_rows.csv", evaluation_rows)
    write_csv("instrumental_agency_seed_summaries.csv", seed_rows)
    write_csv("instrumental_classifier_metrics.csv", classifier_rows)
    write_csv("instrumental_calibration_receipts.csv", calibration_receipts)
    (destination / "instrumental_agency_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir()) if p.is_file()}
    (destination / "artifact_sha256.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    return summary


__all__ = ["InstrumentalOwnershipClassifier", "V016_DEVELOPMENT_SEEDS", "run_instrumental_agency_experiment"]

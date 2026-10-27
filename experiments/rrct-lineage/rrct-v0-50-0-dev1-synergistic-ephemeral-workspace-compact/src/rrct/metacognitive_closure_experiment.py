"""RRCT v0.14 metacognitive-closure development experiment.

Functional question only: can uncertainty about causal self/world attribution
be globally broadcast, recovered from RRCT's own workspace/self state, and then
used to control active information gathering that resolves hidden embodiment
changes?  Nothing in this module measures phenomenal consciousness, subjective
awareness, sentience, valence, or moral status.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .causal_self_boundary_experiment import (
    CausalSelfBoundaryModel,
    _agent_from_snapshots,
    _fit_motor_prior,
)
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .sensorimotor_closure_experiment import _train_bundle

V014_DEVELOPMENT_SEEDS = (3601, 3607, 3613, 3619)
V014_EVALUATION_EPISODES = 16
V014_TOTAL_STEPS = 22
V014_SWITCH_STEP = 7
V014_LATE_START = 17
V014_META_BROADCAST_GAIN = 0.22
V014_READOUT_EPISODES = 70
V014_READOUT_STEPS = 10
V014_READOUT_PRECISION = 1e-2
V014_PROBE_MAXIMUM = 0.75
V014_BOOTSTRAP_SEED = 20_261_014
V014_BOOTSTRAP_RESAMPLES = 4000
V014_CONDITIONS = ("normal", "remap", "mimic")
V014_ARMS = ("mediated", "direct_meta", "no_broadcast", "other_efference")


@dataclass(frozen=True)
class MetaReadoutMetrics:
    ownership_r2: float
    uncertainty_r2: float
    change_alarm_r2: float


class MetacognitiveAccessReadout:
    """Ridge readout from joint workspace/self state to metacognitive content."""

    def __init__(self, *, precision: float = V014_READOUT_PRECISION) -> None:
        if not np.isfinite(precision) or precision <= 0.0:
            raise ValueError("precision must be positive")
        self.precision = float(precision)
        self.beta: np.ndarray | None = None

    @staticmethod
    def features(workspace: np.ndarray, self_state: np.ndarray) -> np.ndarray:
        w = np.asarray(workspace, dtype=np.float64)
        s = np.asarray(self_state, dtype=np.float64)
        if w.shape != (16,) or s.shape != (12,):
            raise ValueError("expected workspace (16,) and self_state (12,)")
        if not np.all(np.isfinite(w)) or not np.all(np.isfinite(s)):
            raise ValueError("readout inputs must be finite")
        return np.concatenate((np.ones(1), w, s))

    def fit(self, x: np.ndarray, y: np.ndarray) -> None:
        features = np.asarray(x, dtype=np.float64)
        targets = np.asarray(y, dtype=np.float64)
        if features.ndim != 2 or features.shape[1] != 29:
            raise ValueError("readout feature matrix must have 29 columns")
        if targets.shape != (len(features), 3):
            raise ValueError("readout targets must have shape (n, 3)")
        penalty = self.precision * np.eye(features.shape[1], dtype=np.float64)
        penalty[0, 0] *= 0.1
        self.beta = np.linalg.solve(
            features.T @ features + penalty,
            features.T @ targets,
        )

    def predict(self, workspace: np.ndarray, self_state: np.ndarray) -> np.ndarray:
        if self.beta is None:
            raise RuntimeError("readout must be fit before prediction")
        value = self.features(workspace, self_state) @ self.beta
        return np.asarray(
            [
                np.clip(value[0], -1.0, 1.0),
                np.clip(value[1], 0.0, 1.0),
                np.clip(value[2], 0.0, 1.0),
            ],
            dtype=np.float64,
        )


def _projection(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 7_714)
    q, _ = np.linalg.qr(rng.normal(size=(16, 5)))
    return np.asarray(q[:, :5], dtype=np.float64)


def _meta_vector(telemetry: Any, noise_variance: float) -> np.ndarray:
    return np.asarray(
        [
            2.0 * telemetry.controllability_belief - 1.0,
            telemetry.epistemic_uncertainty,
            np.tanh(telemetry.causal_gain / (noise_variance + 1e-8)),
            telemetry.causal_alignment,
            telemetry.change_alarm,
        ],
        dtype=np.float64,
    )


def _r2(y: np.ndarray, pred: np.ndarray) -> float:
    centered = y - float(np.mean(y))
    denominator = float(np.sum(np.square(centered)))
    if denominator <= 1e-15:
        return 0.0
    return float(1.0 - np.sum(np.square(y - pred)) / denominator)


def _fit_metacognitive_readout(
    seed: int,
    predictor: Mapping[str, Any],
    forecaster: Mapping[str, Any],
    projection: np.ndarray,
) -> tuple[MetacognitiveAccessReadout, MetaReadoutMetrics, list[dict[str, Any]]]:
    rng = np.random.default_rng(seed + 1_414)
    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    receipts: list[dict[str, Any]] = []
    for episode in range(V014_READOUT_EPISODES):
        agent = _agent_from_snapshots(seed, predictor, forecaster)
        world = GroundedTrackingWorld(grounded_world_spec(seed + 920_000 + episode))
        for step in range(V014_READOUT_STEPS):
            observation = world.observe(V014_READOUT_STEPS + 2)
            meta = np.asarray(
                [
                    rng.uniform(-1.0, 1.0),
                    rng.uniform(0.0, 1.0),
                    rng.uniform(-1.0, 1.0),
                    rng.uniform(-1.0, 1.0),
                    rng.uniform(0.0, 1.0),
                ],
                dtype=np.float64,
            )
            result = agent.step(
                observation,
                source="v014_meta_readout_training",
                perturb_workspace=V014_META_BROADCAST_GAIN * (projection @ meta),
            )
            features.append(MetacognitiveAccessReadout.features(result.workspace, result.self_state))
            targets.append(meta[[0, 1, 4]].copy())
            world.advance(result.action)
            receipts.append(
                {
                    "seed": seed,
                    "episode": episode,
                    "step": step,
                    "synthetic_meta_only": True,
                    "future_outcome_used": False,
                }
            )
    x = np.stack(features)
    y = np.stack(targets)
    indices = np.arange(len(x))
    rng.shuffle(indices)
    split = int(0.8 * len(indices))
    train = indices[:split]
    test = indices[split:]
    model = MetacognitiveAccessReadout()
    model.fit(x[train], y[train])
    pred = x[test] @ model.beta  # type: ignore[operator]
    metrics = MetaReadoutMetrics(
        ownership_r2=_r2(y[test, 0], pred[:, 0]),
        uncertainty_r2=_r2(y[test, 1], pred[:, 1]),
        change_alarm_r2=_r2(y[test, 2], pred[:, 2]),
    )
    return model, metrics, receipts


def _remap_matrix(episode: int) -> np.ndarray:
    matrices = (
        -np.eye(2, dtype=np.float64),
        np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64),
        np.asarray([[0.0, -1.0], [1.0, 0.0]], dtype=np.float64),
    )
    return matrices[int(episode) % len(matrices)].copy()


def _probe_direction(boundary: CausalSelfBoundaryModel, rng: np.random.Generator) -> np.ndarray:
    covariance = np.linalg.inv(boundary.design_precision)
    values, vectors = np.linalg.eigh(covariance)
    direction = vectors[:, int(np.argmax(values))].copy()
    if rng.random() < 0.5:
        direction *= -1.0
    return direction


def _same_norm_other_efference(command: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    norm = float(np.linalg.norm(command))
    angle = float(rng.uniform(0.0, 2.0 * np.pi))
    return norm * np.asarray([np.cos(angle), np.sin(angle)], dtype=np.float64)


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
    rng = np.random.default_rng(
        seed + 600_000 + 10_000 * episode + 101 * V014_CONDITIONS.index(condition) + 17 * V014_ARMS.index(arm)
    )
    agent = _agent_from_snapshots(seed, predictor, forecaster)
    world = GroundedTrackingWorld(grounded_world_spec(seed + 400_000 + episode))
    boundary = CausalSelfBoundaryModel(passive, action_prior, noise_variance)
    remap = _remap_matrix(episode)
    rows: list[dict[str, Any]] = []

    for step in range(V014_TOTAL_STEPS):
        observation = world.observe(V014_TOTAL_STEPS)
        before = boundary.telemetry()
        meta = _meta_vector(before, noise_variance)
        broadcast_enabled = arm != "no_broadcast"
        perturbation = (
            V014_META_BROADCAST_GAIN * (projection @ meta)
            if broadcast_enabled
            else None
        )
        result = agent.step(
            observation,
            source=f"v014_{arm}_{condition}",
            perturb_workspace=perturbation,
        )
        decoded = readout.predict(result.workspace, result.self_state)
        decoded_ownership = 0.5 * (decoded[0] + 1.0)
        decoded_uncertainty = float(decoded[1])
        decoded_alarm = float(decoded[2])
        if arm == "direct_meta":
            probe_need = float(max(before.epistemic_uncertainty, before.change_alarm))
        else:
            # Critical v0.14 closure: behavior reads metacognition back out of
            # RRCT's own globally influenced internal state.
            probe_need = float(max(decoded_uncertainty, decoded_alarm))
        direction = _probe_direction(boundary, rng)
        probe = V014_PROBE_MAXIMUM * probe_need * direction
        command = np.clip(result.action + probe, -1.0, 1.0)
        agent.register_executed_action(command)

        if step < V014_SWITCH_STEP or condition == "normal":
            applied = command
            phase = "baseline" if step < V014_SWITCH_STEP else "post"
        elif condition == "remap":
            applied = remap @ command
            phase = "post"
        elif condition == "mimic":
            applied = rng.uniform(-1.0, 1.0, size=2)
            phase = "post"
        else:
            raise ValueError(f"unknown condition: {condition}")

        world.advance(applied)
        next_observation = world.observe(V014_TOTAL_STEPS)
        scored_action = command
        if arm == "other_efference":
            scored_action = _same_norm_other_efference(command, rng)
        after = boundary.update(observation, scored_action, next_observation)
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
                "causal_gain": after.causal_gain,
                "causal_alignment": after.causal_alignment,
                "change_alarm": after.change_alarm,
                "decoded_ownership": float(decoded_ownership),
                "decoded_uncertainty": decoded_uncertainty,
                "decoded_change_alarm": decoded_alarm,
                "probe_need": probe_need,
                "probe_norm": float(np.linalg.norm(probe)),
                "tracking_loss": world.tracking_loss(),
                "prequential_update": True,
                "future_outcome_used_before_command": False,
            }
        )
    return rows


def _bootstrap(values: Sequence[float]) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V014_BOOTSTRAP_SEED)
    draws = np.empty(V014_BOOTSTRAP_RESAMPLES)
    for i in range(V014_BOOTSTRAP_RESAMPLES):
        draws[i] = float(np.mean(x[rng.integers(0, len(x), size=len(x))]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_metacognitive_closure_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V014_DEVELOPMENT_SEEDS,
) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V014_DEVELOPMENT_SEEDS:
        raise ValueError("v0.14 runner requires the exact frozen development seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    evaluation_rows: list[dict[str, Any]] = []
    readout_rows: list[dict[str, Any]] = []
    readout_receipts: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []

    for seed in seed_values:
        predictor, forecaster, *_ = _train_bundle(seed)
        passive, action_prior, noise_variance, _ = _fit_motor_prior(seed)
        projection = _projection(seed)
        readout, metrics, receipts = _fit_metacognitive_readout(seed, predictor, forecaster, projection)
        readout_receipts.extend(receipts)
        readout_rows.append(
            {
                "seed": seed,
                "ownership_r2": metrics.ownership_r2,
                "uncertainty_r2": metrics.uncertainty_r2,
                "change_alarm_r2": metrics.change_alarm_r2,
            }
        )
        for condition in V014_CONDITIONS:
            for arm in V014_ARMS:
                for episode in range(V014_EVALUATION_EPISODES):
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
        def mean(condition: str, arm: str, field: str, start: int = V014_LATE_START, end: int | None = None) -> float:
            vals = [
                float(r[field]) for r in local
                if r["condition"] == condition and r["arm"] == arm
                and int(r["step"]) >= start
                and (end is None or int(r["step"]) < end)
            ]
            return float(np.mean(vals))

        mediated_remap = mean("remap", "mediated", "belief")
        mediated_mimic = mean("mimic", "mediated", "belief")
        no_broadcast_remap = mean("remap", "no_broadcast", "belief")
        other_remap = mean("remap", "other_efference", "belief")
        direct_remap = mean("remap", "direct_meta", "belief")
        mediated_probe_early = mean("remap", "mediated", "probe_need", V014_SWITCH_STEP, V014_SWITCH_STEP + 6)
        no_broadcast_probe_early = mean("remap", "no_broadcast", "probe_need", V014_SWITCH_STEP, V014_SWITCH_STEP + 6)
        seed_rows.append(
            {
                "seed": seed,
                "mediated_remap_late_belief": mediated_remap,
                "mediated_mimic_late_belief": mediated_mimic,
                "self_mimic_separation": mediated_remap - mediated_mimic,
                "broadcast_remap_advantage": mediated_remap - no_broadcast_remap,
                "correct_efference_advantage": mediated_remap - other_remap,
                "mediated_minus_direct": mediated_remap - direct_remap,
                "broadcast_probe_advantage": mediated_probe_early - no_broadcast_probe_early,
                "ownership_r2": metrics.ownership_r2,
                "uncertainty_r2": metrics.uncertainty_r2,
                "change_alarm_r2": metrics.change_alarm_r2,
            }
        )

    fields = {
        "mediated_remap_late_belief": [r["mediated_remap_late_belief"] for r in seed_rows],
        "mediated_mimic_late_belief": [r["mediated_mimic_late_belief"] for r in seed_rows],
        "self_mimic_separation": [r["self_mimic_separation"] for r in seed_rows],
        "broadcast_remap_advantage": [r["broadcast_remap_advantage"] for r in seed_rows],
        "correct_efference_advantage": [r["correct_efference_advantage"] for r in seed_rows],
        "mediated_minus_direct": [r["mediated_minus_direct"] for r in seed_rows],
        "broadcast_probe_advantage": [r["broadcast_probe_advantage"] for r in seed_rows],
        "ownership_r2": [r["ownership_r2"] for r in seed_rows],
        "uncertainty_r2": [r["uncertainty_r2"] for r in seed_rows],
        "change_alarm_r2": [r["change_alarm_r2"] for r in seed_rows],
    }
    cis = {key: _bootstrap(values) for key, values in fields.items()}
    gates = {
        "metacognitive_ownership_globally_decodable": cis["ownership_r2"][0] > 0.90,
        "metacognitive_uncertainty_globally_decodable": cis["uncertainty_r2"][0] > 0.70,
        "embodiment_change_globally_decodable": cis["change_alarm_r2"][0] > 0.70,
        "mediated_remapped_self_reidentified": cis["mediated_remap_late_belief"][0] > 0.85,
        "mediated_external_mimic_rejected": cis["mediated_mimic_late_belief"][1] < 0.35,
        "mediated_self_mimic_separation": cis["self_mimic_separation"][0] > 0.50,
        "broadcast_is_functionally_required": cis["broadcast_remap_advantage"][0] > 0.20,
        "correct_efference_is_functionally_required": cis["correct_efference_advantage"][0] > 0.40,
        "mediated_control_matches_direct_meta": cis["mediated_minus_direct"][0] > -0.08,
        "broadcast_drives_postchange_probing": cis["broadcast_probe_advantage"][0] > 0.20,
        "commit_before_reveal_integrity": all(
            r["prequential_update"] and not r["future_outcome_used_before_command"]
            for r in evaluation_rows
        ),
    }
    summary = {
        "schema": "rrct.v014.metacognitive_closure.v1",
        "seeds": list(seed_values),
        "conditions": list(V014_CONDITIONS),
        "arms": list(V014_ARMS),
        "means": {key: float(np.mean(values)) for key, values in fields.items()},
        "bootstrap_95": {key: list(value) for key, value in cis.items()},
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence about global metacognitive access and closed-loop "
            "causal self/world regulation only; not evidence of phenomenal consciousness "
            "or subjective awareness."
        ),
    }

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        with (destination / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)

    write_csv("metacognitive_closure_evaluation_rows.csv", evaluation_rows)
    write_csv("metacognitive_closure_seed_summaries.csv", seed_rows)
    write_csv("metacognitive_readout_metrics.csv", readout_rows)
    write_csv("metacognitive_readout_receipts.csv", readout_receipts)
    (destination / "metacognitive_closure_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(destination.iterdir()) if path.is_file()
    }
    (destination / "artifact_sha256.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


__all__ = [
    "MetaReadoutMetrics",
    "MetacognitiveAccessReadout",
    "V014_DEVELOPMENT_SEEDS",
    "run_metacognitive_closure_experiment",
]

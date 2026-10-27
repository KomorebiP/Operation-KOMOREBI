"""RRCT v0.13 causal self-boundary development experiment.

This experiment tests a bounded functional mechanism: whether a recurrent
agent can infer which sensory changes remain contingently controlled by its
own motor commands, revise that inference after hidden embodiment remapping,
and reject externally generated motion with matched action scale.

The quantities here are *not* measures of consciousness, awareness,
sentience, phenomenal experience, valence, or moral status.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .agent import RRCTAgent
from .experiments import _agent
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .sensorimotor_closure_experiment import _train_bundle

V013_DEVELOPMENT_SEEDS = (3501, 3507, 3513, 3519)
V013_CALIBRATION_EPISODES = 100
V013_EVALUATION_EPISODES = 48
V013_TOTAL_STEPS = 22
V013_SWITCH_STEP = 7
V013_LATE_START = 17
V013_PRIOR_STRENGTH = 0.5
V013_FORGETTING = 0.94
V013_PROBE_MAXIMUM = 0.75
V013_META_BROADCAST_GAIN = 0.18
V013_BOOTSTRAP_SEED = 20_261_013
V013_BOOTSTRAP_RESAMPLES = 4000
V013_CONDITIONS = ("normal", "invert", "swap", "rot90", "mimic")


def _sigmoid(value: float) -> float:
    return float(1.0 / (1.0 + np.exp(-np.clip(value, -12.0, 12.0))))


@dataclass(frozen=True)
class BoundaryTelemetry:
    controllability_belief: float
    epistemic_uncertainty: float
    causal_gain: float
    causal_alignment: float
    change_alarm: float


class CausalSelfBoundaryModel:
    """Prequential adaptive action-to-sensory causal comparator.

    A frozen passive model predicts the next two position channels from the
    current sensory state.  A two-by-two action-effect map predicts the
    additional innovation attributable to the agent's motor command.  The
    action map is updated only *after* the current transition has been scored.
    """

    def __init__(
        self,
        passive_coefficients: np.ndarray,
        action_prior: np.ndarray,
        noise_variance: float,
        *,
        prior_strength: float = V013_PRIOR_STRENGTH,
        forgetting: float = V013_FORGETTING,
    ) -> None:
        passive = np.asarray(passive_coefficients, dtype=np.float64)
        action = np.asarray(action_prior, dtype=np.float64)
        if passive.shape != (7, 2) or action.shape != (2, 2):
            raise ValueError("boundary model coefficients have incorrect shapes")
        if not np.all(np.isfinite(passive)) or not np.all(np.isfinite(action)):
            raise ValueError("boundary model coefficients must be finite")
        if not np.isfinite(noise_variance) or noise_variance <= 0.0:
            raise ValueError("noise_variance must be positive")
        if not 0.0 < forgetting <= 1.0 or prior_strength <= 0.0:
            raise ValueError("invalid boundary adaptation parameters")
        self.passive_coefficients = passive.copy()
        self.action_prior = action.copy()
        self.noise_variance = float(noise_variance)
        self.prior_strength = float(prior_strength)
        self.forgetting = float(forgetting)
        self.reset()

    def reset(self) -> None:
        self.design_precision = self.prior_strength * np.eye(2, dtype=np.float64)
        self.effect_target = self.prior_strength * self.action_prior.copy()
        self.log_odds = 2.0
        self.last_gain = 0.0
        self.last_alignment = 0.0
        self.change_alarm = 0.0
        self.observation_count = 0

    @property
    def action_effect(self) -> np.ndarray:
        return np.linalg.solve(self.design_precision, self.effect_target)

    @property
    def belief(self) -> float:
        return _sigmoid(self.log_odds)

    @property
    def uncertainty(self) -> float:
        probability = self.belief
        hypothesis_ambiguity = 4.0 * probability * (1.0 - probability)
        design_uncertainty = min(
            1.0,
            float(np.trace(np.linalg.inv(self.design_precision))) / 4.0,
        )
        return float(np.clip(0.7 * hypothesis_ambiguity + 0.3 * design_uncertainty, 0.0, 1.0))

    def telemetry(self) -> BoundaryTelemetry:
        return BoundaryTelemetry(
            controllability_belief=self.belief,
            epistemic_uncertainty=self.uncertainty,
            causal_gain=self.last_gain,
            causal_alignment=self.last_alignment,
            change_alarm=float(self.change_alarm),
        )

    def probe(self, rng: np.random.Generator) -> tuple[np.ndarray, float]:
        covariance = np.linalg.inv(self.design_precision)
        values, vectors = np.linalg.eigh(covariance)
        direction = vectors[:, int(np.argmax(values))].copy()
        if rng.random() < 0.5:
            direction *= -1.0
        need = float(np.clip(max(self.uncertainty, self.change_alarm), 0.0, 1.0))
        return V013_PROBE_MAXIMUM * need * direction, need

    def update(
        self,
        observation: np.ndarray,
        action: np.ndarray,
        next_observation: np.ndarray,
    ) -> BoundaryTelemetry:
        obs = np.asarray(observation, dtype=np.float64)
        command = np.asarray(action, dtype=np.float64)
        nxt = np.asarray(next_observation, dtype=np.float64)
        if obs.shape != (12,) or nxt.shape != (12,) or command.shape != (2,):
            raise ValueError("boundary update received incorrect shapes")
        features = np.concatenate((np.ones(1, dtype=np.float64), obs[:6]))
        observed = nxt[:2]
        passive_prediction = features @ self.passive_coefficients
        effect = self.action_effect
        action_prediction = passive_prediction + command @ effect
        passive_error = float(np.mean(np.square(observed - passive_prediction)))
        action_error = float(np.mean(np.square(observed - action_prediction)))
        gain = passive_error - action_error
        innovation = observed - passive_prediction
        predicted_innovation = command @ effect
        denominator = float(np.linalg.norm(innovation) * np.linalg.norm(predicted_innovation))
        alignment = (
            float(np.dot(innovation, predicted_innovation) / denominator)
            if denominator > 1e-12
            else 0.0
        )

        normalized_surprise = action_error / (self.noise_variance + 1e-8)
        if (
            self.belief > 0.75
            and gain < -0.5 * self.noise_variance
            and normalized_surprise > 2.0
        ):
            # A previously trusted body model has abruptly stopped matching.
            # Loosen the embodiment map without declaring the world "not-self".
            self.design_precision = 0.35 * self.design_precision + 0.15 * np.eye(2)
            self.effect_target = 0.35 * self.effect_target
            self.log_odds *= 0.2
            self.change_alarm = 1.0
        else:
            self.change_alarm *= 0.75

        evidence = float(
            np.clip(gain / (2.0 * self.noise_variance + 1e-8), -1.5, 1.5)
        )
        self.log_odds = 0.90 * self.log_odds + evidence

        # Prequential integrity: update only after scoring this transition.
        residual = observed - passive_prediction
        self.design_precision = (
            self.forgetting * self.design_precision
            + np.outer(command, command)
            + 0.01 * np.eye(2)
        )
        self.effect_target = self.forgetting * self.effect_target + np.outer(command, residual)
        self.last_gain = float(gain)
        self.last_alignment = float(alignment)
        self.observation_count += 1
        return self.telemetry()


def _fit_motor_prior(seed: int) -> tuple[np.ndarray, np.ndarray, float, list[dict[str, Any]]]:
    rng = np.random.default_rng(seed + 991)
    sensory_rows: list[np.ndarray] = []
    action_rows: list[np.ndarray] = []
    target_rows: list[np.ndarray] = []
    receipts: list[dict[str, Any]] = []
    for episode in range(V013_CALIBRATION_EPISODES):
        world = GroundedTrackingWorld(grounded_world_spec(seed + 100_000 + episode))
        for step in range(9):
            observation = world.observe(10)
            # Bounded developmental motor babbling.  Only executed transitions
            # are used; no unchosen candidate outcome is observed.
            command = rng.uniform(-1.0, 1.0, size=2)
            world.advance(command)
            next_observation = world.observe(10)
            sensory_rows.append(np.concatenate((np.ones(1), observation[:6])))
            action_rows.append(command.copy())
            target_rows.append(next_observation[:2].copy())
            receipts.append(
                {
                    "seed": seed,
                    "calibration_episode": episode,
                    "step": step,
                    "executed_action_only": True,
                    "world_digest": world.spec.digest(),
                }
            )
    x = np.asarray(sensory_rows, dtype=np.float64)
    a = np.asarray(action_rows, dtype=np.float64)
    y = np.asarray(target_rows, dtype=np.float64)
    design = np.column_stack((x, a))
    penalty = 1e-3 * np.eye(design.shape[1], dtype=np.float64)
    penalty[0, 0] = 1e-5
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    residual = y - design @ beta
    noise_variance = float(np.mean(np.square(residual)))
    return beta[:7].copy(), beta[7:].copy(), noise_variance, receipts


def _condition_matrix(condition: str) -> np.ndarray:
    if condition == "normal":
        return np.eye(2, dtype=np.float64)
    if condition == "invert":
        return -np.eye(2, dtype=np.float64)
    if condition == "swap":
        return np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64)
    if condition == "rot90":
        return np.asarray([[0.0, -1.0], [1.0, 0.0]], dtype=np.float64)
    if condition == "mimic":
        return np.zeros((2, 2), dtype=np.float64)
    raise ValueError(f"unknown condition: {condition}")


def _meta_projection(seed: int, workspace_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 7_777)
    matrix = rng.normal(size=(workspace_dim, 4))
    q, _ = np.linalg.qr(matrix)
    return np.asarray(q[:, :4], dtype=np.float64)


def _meta_vector(telemetry: BoundaryTelemetry, noise_variance: float) -> np.ndarray:
    return np.asarray(
        [
            2.0 * telemetry.controllability_belief - 1.0,
            telemetry.epistemic_uncertainty,
            np.tanh(telemetry.causal_gain / (noise_variance + 1e-8)),
            telemetry.causal_alignment,
        ],
        dtype=np.float64,
    )


def _bootstrap_interval(values: Sequence[float]) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V013_BOOTSTRAP_SEED)
    draws = np.empty(V013_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for index in range(V013_BOOTSTRAP_RESAMPLES):
        sample = rng.integers(0, len(x), size=len(x))
        draws[index] = float(np.mean(x[sample]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _agent_from_snapshots(seed: int, predictor: Mapping[str, Any], forecaster: Mapping[str, Any]) -> RRCTAgent:
    agent = _agent(seed, self_model_mode="frozen")
    agent.load_predictor_snapshot(predictor, freeze=True)
    agent.load_observation_forecaster_snapshot(forecaster, freeze=True)
    agent.reset()
    agent.freeze_self_model()
    return agent


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
    meta_projection: np.ndarray,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed + 500_000 + 10_000 * episode + 101 * V013_CONDITIONS.index(condition))
    agent = _agent_from_snapshots(seed, predictor, forecaster)
    world = GroundedTrackingWorld(grounded_world_spec(seed + 300_000 + episode))
    boundary = CausalSelfBoundaryModel(passive, action_prior, noise_variance)
    control_matrix = _condition_matrix(condition)
    rows: list[dict[str, Any]] = []

    for step in range(V013_TOTAL_STEPS):
        observation = world.observe(V013_TOTAL_STEPS)
        before = boundary.telemetry()
        meta = _meta_vector(before, noise_variance)
        use_broadcast = arm != "no_broadcast"
        perturbation = (
            V013_META_BROADCAST_GAIN * (meta_projection @ meta)
            if use_broadcast
            else None
        )
        result = agent.step(
            observation,
            source=f"v013_{arm}_{condition}",
            perturb_workspace=perturbation,
        )
        if arm == "passive":
            probe = np.zeros(2, dtype=np.float64)
            probe_need = 0.0
        else:
            probe, probe_need = boundary.probe(rng)
        command = np.clip(result.action + probe, -1.0, 1.0)
        agent.register_executed_action(command)

        if step < V013_SWITCH_STEP or condition == "normal":
            applied_action = command
            phase = "baseline" if step < V013_SWITCH_STEP else "post"
        elif condition == "mimic":
            # Same bounded marginal action scale, but independent of the
            # current agent command.  This is the matched non-owned motion arm.
            applied_action = rng.uniform(-1.0, 1.0, size=2)
            phase = "post"
        else:
            applied_action = control_matrix @ command
            phase = "post"

        world.advance(applied_action)
        next_observation = world.observe(V013_TOTAL_STEPS)
        scored_action = command.copy()
        if arm == "shuffled_efference":
            scored_action = np.asarray([command[1], -command[0]], dtype=np.float64)
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
                "probe_need": float(probe_need),
                "probe_norm": float(np.linalg.norm(probe)),
                "command_norm": float(np.linalg.norm(command)),
                "applied_action_norm": float(np.linalg.norm(applied_action)),
                "tracking_loss": world.tracking_loss(),
                "workspace_norm": float(np.linalg.norm(result.workspace)),
                "self_state_norm": float(np.linalg.norm(result.self_state)),
                "memory_written": bool(result.memory_written),
                "prequential_update": True,
                "future_outcome_used_before_command": False,
            }
        )
    return rows


def run_causal_self_boundary_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V013_DEVELOPMENT_SEEDS,
) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V013_DEVELOPMENT_SEEDS:
        raise ValueError("v0.13 runner requires the exact frozen development seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    evaluation_rows: list[dict[str, Any]] = []
    calibration_receipts: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    integration_rows: list[dict[str, Any]] = []

    for seed in seed_values:
        predictor, forecaster, *_ = _train_bundle(seed)
        passive, action_prior, noise_variance, receipts = _fit_motor_prior(seed)
        calibration_receipts.extend(receipts)
        projection = _meta_projection(seed, 16)

        # Matched causal availability audit from identical states.  This only
        # establishes downstream access to the boundary signal, not awareness.
        audit_agent = _agent_from_snapshots(seed, predictor, forecaster)
        audit_world = GroundedTrackingWorld(grounded_world_spec(seed + 880_000))
        audit_observation = audit_world.observe(V013_TOTAL_STEPS)
        audit_boundary = CausalSelfBoundaryModel(passive, action_prior, noise_variance)
        meta = _meta_vector(audit_boundary.telemetry(), noise_variance)
        with_meta = copy.deepcopy(audit_agent).step(
            audit_observation,
            source="v013_meta_audit_on",
            perturb_workspace=V013_META_BROADCAST_GAIN * (projection @ meta),
        )
        without_meta = copy.deepcopy(audit_agent).step(
            audit_observation,
            source="v013_meta_audit_off",
        )
        integration_rows.append(
            {
                "seed": seed,
                "workspace_effect": float(np.linalg.norm(with_meta.workspace - without_meta.workspace)),
                "self_state_effect": float(np.linalg.norm(with_meta.self_state - without_meta.self_state)),
                "action_effect": float(np.linalg.norm(with_meta.action - without_meta.action)),
                "resolution_changed": bool(with_meta.next_resolution_level != without_meta.next_resolution_level),
            }
        )

        for condition in V013_CONDITIONS:
            for arm in ("adaptive", "passive", "shuffled_efference", "no_broadcast"):
                for episode in range(V013_EVALUATION_EPISODES):
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
                            meta_projection=projection,
                        )
                    )

        rows_seed = [row for row in evaluation_rows if row["seed"] == seed]
        def late_mean(condition: str, arm: str, field: str) -> float:
            values = [
                float(row[field]) for row in rows_seed
                if row["condition"] == condition
                and row["arm"] == arm
                and int(row["step"]) >= V013_LATE_START
            ]
            return float(np.mean(values))

        remap_conditions = ("invert", "swap", "rot90")
        adaptive_remap = float(np.mean([late_mean(c, "adaptive", "belief") for c in remap_conditions]))
        passive_remap = float(np.mean([late_mean(c, "passive", "belief") for c in remap_conditions]))
        shuffled_remap = float(np.mean([late_mean(c, "shuffled_efference", "belief") for c in remap_conditions]))
        mimic = late_mean("mimic", "adaptive", "belief")
        normal = late_mean("normal", "adaptive", "belief")
        adaptive_uncertainty = float(np.mean([late_mean(c, "adaptive", "uncertainty") for c in remap_conditions]))
        passive_uncertainty = float(np.mean([late_mean(c, "passive", "uncertainty") for c in remap_conditions]))
        seed_rows.append(
            {
                "seed": seed,
                "adaptive_normal_late_belief": normal,
                "adaptive_remap_late_belief": adaptive_remap,
                "adaptive_mimic_late_belief": mimic,
                "self_mimic_separation": adaptive_remap - mimic,
                "active_passive_remap_advantage": adaptive_remap - passive_remap,
                "active_shuffled_remap_advantage": adaptive_remap - shuffled_remap,
                "adaptive_remap_late_uncertainty": adaptive_uncertainty,
                "passive_remap_late_uncertainty": passive_uncertainty,
                "uncertainty_reduction_vs_passive": passive_uncertainty - adaptive_uncertainty,
            }
        )

    separations = [row["self_mimic_separation"] for row in seed_rows]
    active_passive = [row["active_passive_remap_advantage"] for row in seed_rows]
    active_shuffled = [row["active_shuffled_remap_advantage"] for row in seed_rows]
    abs_remap = [row["adaptive_remap_late_belief"] for row in seed_rows]
    mimic_values = [row["adaptive_mimic_late_belief"] for row in seed_rows]
    uncertainty_reduction = [row["uncertainty_reduction_vs_passive"] for row in seed_rows]

    separation_ci = _bootstrap_interval(separations)
    active_passive_ci = _bootstrap_interval(active_passive)
    active_shuffled_ci = _bootstrap_interval(active_shuffled)
    remap_ci = _bootstrap_interval(abs_remap)
    mimic_ci = _bootstrap_interval(mimic_values)
    uncertainty_ci = _bootstrap_interval(uncertainty_reduction)

    gates = {
        "self_vs_mimic_separation_positive": separation_ci[0] > 0.25,
        "remapped_self_reidentified": remap_ci[0] > 0.80,
        "external_mimic_rejected": mimic_ci[1] < 0.40,
        "active_probe_beats_passive": active_passive_ci[0] > 0.05,
        "aligned_efference_beats_shuffled": active_shuffled_ci[0] > 0.10,
        "active_probe_reduces_uncertainty": uncertainty_ci[0] > 0.10,
        "commit_before_reveal_integrity": all(
            row["prequential_update"] and not row["future_outcome_used_before_command"]
            for row in evaluation_rows
        ),
        "metacognitive_signal_reaches_self_state": min(
            row["self_state_effect"] for row in integration_rows
        ) > 1e-6,
    }

    summary = {
        "schema": "rrct.v013.causal_self_boundary.v1",
        "seeds": list(seed_values),
        "conditions": list(V013_CONDITIONS),
        "evaluation_episodes_per_condition_arm_seed": V013_EVALUATION_EPISODES,
        "switch_step": V013_SWITCH_STEP,
        "late_start": V013_LATE_START,
        "means": {
            "adaptive_remap_late_belief": float(np.mean(abs_remap)),
            "adaptive_mimic_late_belief": float(np.mean(mimic_values)),
            "self_mimic_separation": float(np.mean(separations)),
            "active_passive_remap_advantage": float(np.mean(active_passive)),
            "active_shuffled_remap_advantage": float(np.mean(active_shuffled)),
            "uncertainty_reduction_vs_passive": float(np.mean(uncertainty_reduction)),
        },
        "bootstrap_95": {
            "adaptive_remap_late_belief": list(remap_ci),
            "adaptive_mimic_late_belief": list(mimic_ci),
            "self_mimic_separation": list(separation_ci),
            "active_passive_remap_advantage": list(active_passive_ci),
            "active_shuffled_remap_advantage": list(active_shuffled_ci),
            "uncertainty_reduction_vs_passive": list(uncertainty_ci),
        },
        "gates": gates,
        "all_primary_gates_pass": bool(all(gates.values())),
        "interpretation_limit": (
            "Functional evidence about causal self/world discrimination, adaptive embodiment, "
            "metacognitive access, and active information gathering only; not evidence of "
            "phenomenal consciousness or subjective awareness."
        ),
    }

    def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)

    write_csv(destination / "causal_self_boundary_evaluation_rows.csv", evaluation_rows)
    write_csv(destination / "causal_self_boundary_seed_summaries.csv", seed_rows)
    write_csv(destination / "causal_self_boundary_calibration_receipts.csv", calibration_receipts)
    write_csv(destination / "causal_self_boundary_integration_audit.csv", integration_rows)
    (destination / "causal_self_boundary_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifact_hashes = {}
    for path in sorted(destination.iterdir()):
        if path.is_file():
            artifact_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (destination / "artifact_sha256.json").write_text(
        json.dumps(artifact_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


__all__ = [
    "BoundaryTelemetry",
    "CausalSelfBoundaryModel",
    "V013_DEVELOPMENT_SEEDS",
    "run_causal_self_boundary_experiment",
]

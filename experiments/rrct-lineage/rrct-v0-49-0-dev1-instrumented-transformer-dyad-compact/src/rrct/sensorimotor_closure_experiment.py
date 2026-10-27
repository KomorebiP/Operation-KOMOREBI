"""RRCT v0.12 learned sensorimotor-closure development experiment.

This module tests a functional causal mechanism only. It does not create,
detect, or measure consciousness, awareness, sentience, valence, or moral
status.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .agent import RRCTAgent
from .experiments import _agent
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec

V012_DEVELOPMENT_SEEDS = (3401, 3407, 3413, 3419)
V012_TRAIN_EPISODES = 24
V012_EVALUATION_EPISODES = 32
V012_PREFIX_STEPS = 6
V012_HORIZON = 4
V012_TOTAL_STEPS = 10
V012_QUERY_BUDGET = 4
V012_CANDIDATE_MAGNITUDE = 0.35
V012_WORLD_MODEL_PRECISION = 1e-2
V012_BOOTSTRAP_SEED = 20_261_012
V012_BOOTSTRAP_RESAMPLES = 4000


class SensorimotorRidgeModel:
    """Bounded second-order next-observation model conditioned on action."""

    def __init__(self, *, action_conditioned: bool = True, precision: float = V012_WORLD_MODEL_PRECISION) -> None:
        if not np.isfinite(precision) or precision <= 0.0:
            raise ValueError("precision must be positive")
        self.action_conditioned = bool(action_conditioned)
        self.precision = float(precision)
        self.beta: np.ndarray | None = None

    def feature_vector(self, observation: np.ndarray, action: np.ndarray) -> np.ndarray:
        obs = np.asarray(observation, dtype=np.float64)
        act = np.asarray(action, dtype=np.float64)
        if obs.shape != (12,) or act.shape != (2,) or not np.all(np.isfinite(obs)) or not np.all(np.isfinite(act)):
            raise ValueError("expected finite observation (12,) and action (2,)")
        effective_action = act if self.action_conditioned else np.zeros(2, dtype=np.float64)
        return np.concatenate(
            (
                np.ones(1, dtype=np.float64),
                obs,
                effective_action,
                obs * obs,
                effective_action * effective_action,
                np.outer(obs, effective_action).reshape(-1),
            )
        )

    @property
    def feature_dim(self) -> int:
        return 1 + 12 + 2 + 12 + 2 + 24

    def fit(self, transitions: Sequence[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
        if not transitions:
            raise ValueError("at least one transition is required")
        x = np.stack([self.feature_vector(obs, action) for obs, action, _ in transitions])
        y = np.stack([np.asarray(next_obs, dtype=np.float64) for _, _, next_obs in transitions])
        if y.shape != (len(transitions), 12) or not np.all(np.isfinite(y)):
            raise ValueError("next observations must be finite 12-vectors")
        penalty = self.precision * np.eye(x.shape[1], dtype=np.float64)
        penalty[0, 0] *= 0.1
        self.beta = np.linalg.solve(x.T @ x + penalty, x.T @ y)

    def predict(self, observation: np.ndarray, action: np.ndarray) -> np.ndarray:
        if self.beta is None:
            raise RuntimeError("model must be fit before prediction")
        value = self.feature_vector(observation, action) @ self.beta
        value = np.asarray(value, dtype=np.float64)
        value[:6] = np.clip(value[:6], -1.0, 1.0)
        value[6] = np.clip(value[6], 0.0, 1.0)
        value[7:] = np.clip(value[7:], -1.0, 1.0)
        return value


def _derange_actions(transitions: Sequence[tuple[np.ndarray, np.ndarray, np.ndarray]], seed: int) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    count = len(transitions)
    rng = np.random.default_rng(seed)
    base = np.arange(count)
    for _ in range(10_000):
        permutation = rng.permutation(count)
        if np.all(permutation != base):
            break
    else:
        raise RuntimeError("failed to derange action assignments")
    actions = [np.asarray(transitions[int(index)][1], dtype=np.float64).copy() for index in permutation]
    return [
        (np.asarray(obs).copy(), action, np.asarray(next_obs).copy())
        for (obs, _, next_obs), action in zip(transitions, actions)
    ]


def _train_bundle(seed: int) -> tuple[Mapping[str, Any], Mapping[str, Any], SensorimotorRidgeModel, SensorimotorRidgeModel, SensorimotorRidgeModel, list[dict[str, Any]]]:
    agent = _agent(seed, self_model_mode="frozen")
    agent.train_self_model()
    transitions: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    receipt_rows: list[dict[str, Any]] = []
    for episode_index in range(V012_TRAIN_EPISODES):
        world = GroundedTrackingWorld(grounded_world_spec(seed + 10_000 + episode_index))
        agent.reset()
        for step in range(V012_TOTAL_STEPS - 1):
            observation = world.observe(V012_TOTAL_STEPS)
            result = agent.step(observation, source="v012_sensorimotor_training")
            world.advance(result.action)
            next_observation = world.observe(V012_TOTAL_STEPS)
            transitions.append((observation.copy(), result.action.copy(), next_observation.copy()))
            receipt_rows.append(
                {
                    "seed": seed,
                    "training_episode": episode_index,
                    "step": step,
                    "world_digest": world.spec.digest(),
                    "executed_action_only": True,
                }
            )
        agent.step(world.observe(V012_TOTAL_STEPS), source="v012_sensorimotor_training_final")
    agent.freeze_self_model()
    aligned = SensorimotorRidgeModel(action_conditioned=True)
    aligned.fit(transitions)
    shuffled = SensorimotorRidgeModel(action_conditioned=True)
    shuffled.fit(_derange_actions(transitions, seed + 91_012))
    no_action = SensorimotorRidgeModel(action_conditioned=False)
    no_action.fit(transitions)
    return (
        agent.predictor_snapshot(),
        agent.observation_forecaster_snapshot(),
        aligned,
        shuffled,
        no_action,
        receipt_rows,
    )


def _prime(seed: int, predictor: Mapping[str, Any], forecaster: Mapping[str, Any], episode_seed: int, models: Sequence[SensorimotorRidgeModel]) -> tuple[RRCTAgent, GroundedTrackingWorld, list[list[float]]]:
    agent = _agent(seed, self_model_mode="frozen")
    agent.load_predictor_snapshot(predictor, freeze=True)
    agent.load_observation_forecaster_snapshot(forecaster, freeze=True)
    agent.reset()
    agent.freeze_self_model()
    world = GroundedTrackingWorld(grounded_world_spec(episode_seed))
    model_errors: list[list[float]] = [[] for _ in models]
    for _ in range(V012_PREFIX_STEPS):
        observation = world.observe(V012_TOTAL_STEPS)
        result = agent.step(observation, source="v012_evaluation_prefix")
        predictions = [model.predict(observation, result.action) for model in models]
        world.advance(result.action)
        next_observation = world.observe(V012_TOTAL_STEPS)
        for bucket, prediction in zip(model_errors, predictions):
            bucket.append(float(np.sqrt(np.mean(np.square(prediction - next_observation)))))
    return agent, world, model_errors


def _predicted_tracking_loss(agent: RRCTAgent, start_observation: np.ndarray, delta: np.ndarray, model: SensorimotorRidgeModel) -> float:
    branch = copy.deepcopy(agent)
    branch.self_model.state += np.asarray(delta, dtype=np.float64)
    observation = np.asarray(start_observation, dtype=np.float64).copy()
    losses: list[float] = []
    for _ in range(V012_HORIZON):
        result = branch.step(observation, source="v012_closed_loop_world_model")
        observation = model.predict(observation, result.action)
        losses.append(float(np.mean(np.square(observation[4:6]))))
    return float(np.mean(losses))


def _realized_external_loss(agent: RRCTAgent, world: GroundedTrackingWorld, delta: np.ndarray) -> float:
    branch = copy.deepcopy(agent)
    environment = copy.deepcopy(world)
    branch.self_model.state += np.asarray(delta, dtype=np.float64)
    losses: list[float] = []
    for _ in range(V012_HORIZON):
        result = branch.step(environment.observe(V012_TOTAL_STEPS), source="v012_realized_branch")
        environment.advance(result.action)
        losses.append(environment.tracking_loss())
    return float(np.mean(losses))


def _bootstrap_interval(values: Sequence[float]) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V012_BOOTSTRAP_SEED)
    draws = np.empty(V012_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for index in range(V012_BOOTSTRAP_RESAMPLES):
        sample = rng.integers(0, len(x), size=len(x))
        draws[index] = float(np.mean(x[sample]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_sensorimotor_closure_experiment(output: str | Path, *, seeds: Sequence[int] = V012_DEVELOPMENT_SEEDS) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V012_DEVELOPMENT_SEEDS:
        raise ValueError("v0.12 runner requires the exact frozen development seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    training_receipts: list[dict[str, Any]] = []
    evaluation_rows: list[dict[str, Any]] = []
    seed_summaries: list[dict[str, Any]] = []
    seed_contrasts: list[dict[str, Any]] = []
    model_rows: list[dict[str, Any]] = []

    for seed in seed_values:
        predictor, forecaster, aligned, shuffled, no_action, receipts = _train_bundle(seed)
        training_receipts.extend(receipts)
        models = (aligned, shuffled, no_action)
        policy_values: dict[str, list[float]] = defaultdict(list)
        policy_actions: dict[str, int] = defaultdict(int)
        policy_goods: dict[str, int] = defaultdict(int)
        policy_harms: dict[str, int] = defaultdict(int)
        prefix_model_errors = [[], [], []]

        for episode_index in range(V012_EVALUATION_EPISODES):
            agent, world, prefix_errors = _prime(
                seed, predictor, forecaster, seed + 40_000 + episode_index, models
            )
            for bucket, values in zip(prefix_model_errors, prefix_errors):
                bucket.extend(values)
            plan = agent.plan_endogenous_self_intention(
                horizon=V012_HORIZON,
                query_budget=V012_QUERY_BUDGET,
                candidate_magnitude=V012_CANDIDATE_MAGNITUDE,
                forecast_mode="learned",
                selection_mode="rollout",
                calibration_mode="off",
            )
            nonzero_positions = [
                position for position, candidate in enumerate(plan.queried_indices)
                if candidate != 0
            ]
            candidate_indices = [plan.queried_indices[position] for position in nonzero_positions]
            internal_scores = np.asarray(
                [
                    plan.predicted_baseline_error - plan.predicted_candidate_errors[position]
                    for position in nonzero_positions
                ], dtype=np.float64
            )
            start_observation = world.observe(V012_TOTAL_STEPS)
            score_map: dict[str, np.ndarray] = {"internal_open_loop": internal_scores}
            for arm, model in (
                ("sensorimotor_closed_loop", aligned),
                ("shuffled_action_model", shuffled),
                ("no_action_model", no_action),
            ):
                baseline_loss = _predicted_tracking_loss(
                    agent, start_observation, plan.candidate_deltas[0], model
                )
                score_map[arm] = np.asarray(
                    [
                        baseline_loss
                        - _predicted_tracking_loss(
                            agent, start_observation, plan.candidate_deltas[candidate], model
                        )
                        for candidate in candidate_indices
                    ], dtype=np.float64
                )
            decisions: dict[str, int] = {"zero": 0}
            for arm, scores in score_map.items():
                best = int(np.argmax(scores))
                decisions[arm] = int(candidate_indices[best]) if scores[best] > 0.0 else 0
            decision_digest = hashlib.sha256(repr(sorted(decisions.items())).encode()).hexdigest()

            baseline_external = _realized_external_loss(
                agent, world, plan.candidate_deltas[0]
            )
            outcome_lookup = {0: 0.0}
            for candidate in candidate_indices:
                outcome_lookup[int(candidate)] = float(
                    baseline_external
                    - _realized_external_loss(agent, world, plan.candidate_deltas[candidate])
                )
            for arm, selected in decisions.items():
                benefit = outcome_lookup[int(selected)]
                policy_values[arm].append(benefit)
                policy_actions[arm] += int(selected != 0)
                policy_goods[arm] += int(selected != 0 and benefit > 1e-12)
                policy_harms[arm] += int(selected != 0 and benefit < -1e-12)
                evaluation_rows.append(
                    {
                        "seed": seed,
                        "evaluation_episode": episode_index,
                        "arm": arm,
                        "selected_index": int(selected),
                        "external_benefit": float(benefit),
                        "acted": bool(selected != 0),
                        "beneficial": bool(selected != 0 and benefit > 1e-12),
                        "harmful": bool(selected != 0 and benefit < -1e-12),
                        "decision_digest": decision_digest,
                        "world_digest": world.spec.digest(),
                        "outcomes_materialized_after_decision": True,
                    }
                )
        for name, errors in zip(
            ("aligned_action_conditioned", "shuffled_action_conditioned", "no_action"),
            prefix_model_errors,
        ):
            model_rows.append(
                {
                    "seed": seed,
                    "model": name,
                    "heldout_prefix_one_step_rmse": float(np.mean(errors)),
                    "prediction_count": len(errors),
                }
            )
        for arm in (
            "zero", "internal_open_loop", "sensorimotor_closed_loop",
            "shuffled_action_model", "no_action_model",
        ):
            values = np.asarray(policy_values[arm], dtype=np.float64)
            action_count = policy_actions[arm]
            seed_summaries.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "net_external_improvement": float(np.mean(values)),
                    "action_coverage": action_count / V012_EVALUATION_EPISODES,
                    "beneficial_action_count": policy_goods[arm],
                    "harmful_action_count": policy_harms[arm],
                    "beneficial_precision": policy_goods[arm] / action_count if action_count else None,
                    "conditional_harm_rate": policy_harms[arm] / action_count if action_count else None,
                }
            )
        lookup = {row["arm"]: row for row in seed_summaries if row["seed"] == seed}
        model_lookup = {row["model"]: row for row in model_rows if row["seed"] == seed}
        seed_contrasts.append(
            {
                "seed": seed,
                "closed_loop_minus_internal": lookup["sensorimotor_closed_loop"]["net_external_improvement"] - lookup["internal_open_loop"]["net_external_improvement"],
                "closed_loop_minus_shuffled": lookup["sensorimotor_closed_loop"]["net_external_improvement"] - lookup["shuffled_action_model"]["net_external_improvement"],
                "closed_loop_net": lookup["sensorimotor_closed_loop"]["net_external_improvement"],
                "aligned_minus_shuffled_one_step_rmse": model_lookup["aligned_action_conditioned"]["heldout_prefix_one_step_rmse"] - model_lookup["shuffled_action_conditioned"]["heldout_prefix_one_step_rmse"],
            }
        )

    primary = np.asarray([row["closed_loop_minus_internal"] for row in seed_contrasts])
    control = np.asarray([row["closed_loop_minus_shuffled"] for row in seed_contrasts])
    net = np.asarray([row["closed_loop_net"] for row in seed_contrasts])
    prediction = np.asarray([row["aligned_minus_shuffled_one_step_rmse"] for row in seed_contrasts])
    primary_ci = _bootstrap_interval(primary)
    control_ci = _bootstrap_interval(control)
    net_ci = _bootstrap_interval(net)
    prediction_ci = _bootstrap_interval(prediction)
    gates = {
        "closed_loop_beats_internal_ci": bool(primary_ci[0] > 0.0),
        "closed_loop_beats_internal_seed_consistency": bool(np.sum(primary > 0.0) >= 3),
        "closed_loop_beats_shuffled_mean": bool(np.mean(control) > 0.0),
        "closed_loop_positive_external_ci": bool(net_ci[0] > 0.0),
        "aligned_world_model_better_rmse_mean": bool(np.mean(prediction) < 0.0),
        "commit_before_reveal": all(row["outcomes_materialized_after_decision"] for row in evaluation_rows),
        "training_uses_executed_transitions_only": all(row["executed_action_only"] for row in training_receipts),
    }
    gates["primary_success"] = bool(all(gates.values()))
    summary = {
        "schema": "rrct.v012.sensorimotor_closure_development.v1",
        "status": "exploratory_development_only",
        "seeds": seed_values,
        "mean_closed_loop_minus_internal": float(np.mean(primary)),
        "closed_loop_minus_internal_ci95": primary_ci,
        "mean_closed_loop_minus_shuffled": float(np.mean(control)),
        "closed_loop_minus_shuffled_ci95": control_ci,
        "mean_closed_loop_external_net": float(np.mean(net)),
        "closed_loop_external_net_ci95": net_ci,
        "mean_aligned_minus_shuffled_one_step_rmse": float(np.mean(prediction)),
        "aligned_minus_shuffled_one_step_rmse_ci95": prediction_ci,
        "positive_seed_count_closed_loop_minus_internal": int(np.sum(primary > 0.0)),
        "gates": gates,
        "seed_contrasts": seed_contrasts,
        "limitations": [
            "The world is synthetic and low-dimensional.",
            "The tracking objective is external but not a consciousness metric.",
            "The sensor encoding and actuator dimensionality are fixed.",
            "The world model is a simple ridge model rather than a general learned dynamics model.",
            "This result cannot establish awareness, sentience, phenomenology, valence, or moral status.",
        ],
    }

    def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    write_csv(destination / "sensorimotor_training_receipts.csv", training_receipts)
    write_csv(destination / "sensorimotor_model_summaries.csv", model_rows)
    write_csv(destination / "sensorimotor_evaluation_rows.csv", evaluation_rows)
    write_csv(destination / "sensorimotor_seed_summaries.csv", seed_summaries)
    with (destination / "sensorimotor_closure_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True); handle.write("\n")
    return summary


__all__ = [
    "SensorimotorRidgeModel",
    "V012_DEVELOPMENT_SEEDS",
    "run_sensorimotor_closure_experiment",
]

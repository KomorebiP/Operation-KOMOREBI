"""Development-only externally grounded causal-control experiment for RRCT v0.11.

The benchmark is deliberately nonvalenced. Agent actions causally move a
world state, changed world states become subsequent observations, and the
measured outcome is external tracking error. No quantity here is a measure of
consciousness, sentience, subjective experience, or moral status.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .agent import RRCTAgent
from .experiments import _agent

V011_DEVELOPMENT_SEEDS = (3301, 3307, 3313, 3319)
V011_PREDICTOR_EPISODES = 24
V011_TRANSFER_EPISODES = 24
V011_EVALUATION_EPISODES = 32
V011_PREFIX_STEPS = 6
V011_HORIZON = 4
V011_TOTAL_STEPS = 10
V011_QUERY_BUDGET = 4
V011_CANDIDATE_MAGNITUDE = 0.35
V011_RIDGE_PRIOR_PRECISION = 1.0
V011_BOOTSTRAP_SEED = 20_261_011
V011_BOOTSTRAP_RESAMPLES = 4000


@dataclass(frozen=True)
class GroundedWorldSpec:
    goal: np.ndarray
    initial_position: np.ndarray
    disturbances: np.ndarray

    def digest(self) -> str:
        h = hashlib.sha256()
        for value in (self.goal, self.initial_position, self.disturbances):
            arr = np.ascontiguousarray(value, dtype=np.float64)
            h.update(repr((str(arr.dtype), tuple(arr.shape))).encode())
            h.update(arr.tobytes())
        return h.hexdigest()


class GroundedTrackingWorld:
    """Two-dimensional world whose next sensory state depends on RRCT action."""

    observation_dim = 12

    def __init__(self, spec: GroundedWorldSpec, *, action_coupling: float = 0.42) -> None:
        if not np.isfinite(action_coupling) or action_coupling < 0.0:
            raise ValueError("action_coupling must be finite and nonnegative")
        self.spec = spec
        self.action_coupling = float(action_coupling)
        self.position = np.asarray(spec.initial_position, dtype=np.float64).copy()
        self.last_action = np.zeros(2, dtype=np.float64)
        self.time = 0

    def observe(self, total_steps: int) -> np.ndarray:
        if total_steps < 2:
            raise ValueError("total_steps must be at least two")
        goal = np.asarray(self.spec.goal, dtype=np.float64)
        error = goal - self.position
        x = np.zeros(self.observation_dim, dtype=np.float64)
        x[0:2] = np.tanh(self.position / 1.5)
        x[2:4] = np.tanh(goal / 1.5)
        x[4:6] = np.tanh(error / 2.0)
        x[6] = min(self.time, total_steps - 1) / float(total_steps - 1)
        x[7] = 1.0 if self.time >= total_steps - 2 else 0.0
        x[8:10] = self.last_action
        x[10] = np.tanh(np.linalg.norm(error) / 2.0)
        x[11] = 1.0
        return x

    def advance(self, action: np.ndarray) -> None:
        values = np.asarray(action, dtype=np.float64)
        if values.shape != (2,) or not np.all(np.isfinite(values)):
            raise ValueError("action must be a finite two-vector")
        bounded = np.clip(values, -1.0, 1.0)
        disturbance = np.asarray(
            self.spec.disturbances[min(self.time, len(self.spec.disturbances) - 1)],
            dtype=np.float64,
        )
        self.position = np.clip(
            0.92 * self.position + self.action_coupling * bounded + disturbance,
            -2.5,
            2.5,
        )
        self.last_action = bounded.copy()
        self.time += 1

    def tracking_loss(self) -> float:
        return float(np.mean(np.square(self.position - self.spec.goal)))


def grounded_world_spec(seed: int, total_steps: int = V011_TOTAL_STEPS) -> GroundedWorldSpec:
    rng = np.random.default_rng(int(seed))
    goal = rng.uniform(-1.25, 1.25, size=2)
    initial = rng.uniform(-1.5, 1.5, size=2)
    disturbances = rng.normal(0.0, 0.035, size=(total_steps + 2, 2))
    phase = rng.uniform(-1.0, 1.0, size=(1, 2))
    frequencies = np.asarray([[0.7, 1.1]], dtype=np.float64)
    disturbances += 0.025 * np.sin(
        np.arange(total_steps + 2)[:, None] * frequencies + phase
    )
    return GroundedWorldSpec(goal, initial, disturbances)


class WeightedRidgeTransfer:
    """Deterministic ridge model over bounded precommit causal features."""

    def __init__(self, feature_dim: int, prior_precision: float = 1.0) -> None:
        if feature_dim <= 0:
            raise ValueError("feature_dim must be positive")
        if not np.isfinite(prior_precision) or prior_precision <= 0.0:
            raise ValueError("prior_precision must be positive")
        self.feature_dim = int(feature_dim)
        self.prior_precision = float(prior_precision)
        self.beta = np.zeros(self.feature_dim + 1, dtype=np.float64)

    def fit(self, features: np.ndarray, targets: np.ndarray, weights: np.ndarray) -> None:
        x = np.asarray(features, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64)
        w = np.asarray(weights, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != self.feature_dim:
            raise ValueError("features have the wrong shape")
        if y.shape != (len(x),) or w.shape != (len(x),):
            raise ValueError("targets and weights must match features")
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(w)):
            raise ValueError("fit arrays must be finite")
        if np.any(w <= 0.0):
            raise ValueError("weights must be positive")
        design = np.column_stack((np.ones(len(x), dtype=np.float64), x))
        penalty = self.prior_precision * np.eye(design.shape[1], dtype=np.float64)
        penalty[0, 0] *= 0.1
        precision = design.T @ (w[:, None] * design) + penalty
        target = design.T @ (w * y)
        self.beta = np.linalg.solve(precision, target)

    def predict(self, features: np.ndarray) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim == 1:
            x = x[None, :]
        if x.ndim != 2 or x.shape[1] != self.feature_dim or not np.all(np.isfinite(x)):
            raise ValueError("features have the wrong shape or contain nonfinite values")
        return np.column_stack((np.ones(len(x), dtype=np.float64), x)) @ self.beta


class WeightedLogisticHurdle:
    """Weighted logistic sign model used only as a secondary selector."""

    def __init__(self, feature_dim: int, prior_precision: float = 1.0) -> None:
        self.feature_dim = int(feature_dim)
        self.prior_precision = float(prior_precision)
        self.beta = np.zeros(self.feature_dim + 1, dtype=np.float64)

    def fit(self, features: np.ndarray, labels: np.ndarray, weights: np.ndarray) -> None:
        x = np.asarray(features, dtype=np.float64)
        y = np.asarray(labels, dtype=np.float64)
        w = np.asarray(weights, dtype=np.float64)
        design = np.column_stack((np.ones(len(x), dtype=np.float64), x))
        beta = self.beta.copy()
        penalty = self.prior_precision * np.eye(design.shape[1], dtype=np.float64)
        penalty[0, 0] *= 0.1
        for _ in range(100):
            logits = np.clip(design @ beta, -35.0, 35.0)
            probabilities = 1.0 / (1.0 + np.exp(-logits))
            curvature = w * probabilities * (1.0 - probabilities)
            hessian = design.T @ (curvature[:, None] * design) + penalty
            gradient = design.T @ (w * (y - probabilities)) - penalty @ beta
            step = np.linalg.solve(hessian, gradient)
            next_beta = beta + step
            if np.max(np.abs(step)) < 1e-9:
                beta = next_beta
                break
            beta = next_beta
        self.beta = beta

    def predict_probability(self, features: np.ndarray) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim == 1:
            x = x[None, :]
        logits = np.column_stack((np.ones(len(x), dtype=np.float64), x)) @ self.beta
        return 1.0 / (1.0 + np.exp(-np.clip(logits, -35.0, 35.0)))


def _train_predictors(seed: int) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    agent = _agent(seed, self_model_mode="frozen")
    agent.train_self_model()
    for episode_index in range(V011_PREDICTOR_EPISODES):
        world = GroundedTrackingWorld(
            grounded_world_spec(seed + 10_000 + episode_index)
        )
        agent.reset()
        for _ in range(V011_TOTAL_STEPS):
            result = agent.step(
                world.observe(V011_TOTAL_STEPS), source="v011_grounded_predictor_training"
            )
            world.advance(result.action)
    agent.freeze_self_model()
    return agent.predictor_snapshot(), agent.observation_forecaster_snapshot()


def _prime(seed: int, predictor: Mapping[str, Any], forecaster: Mapping[str, Any], episode_seed: int) -> tuple[RRCTAgent, GroundedTrackingWorld]:
    agent = _agent(seed, self_model_mode="frozen")
    agent.load_predictor_snapshot(predictor, freeze=True)
    agent.load_observation_forecaster_snapshot(forecaster, freeze=True)
    agent.reset()
    agent.freeze_self_model()
    world = GroundedTrackingWorld(grounded_world_spec(episode_seed))
    for _ in range(V011_PREFIX_STEPS):
        result = agent.step(world.observe(V011_TOTAL_STEPS), source="v011_grounded_prefix")
        world.advance(result.action)
    return agent, world


def _external_rollout(agent: RRCTAgent, world: GroundedTrackingWorld, delta: np.ndarray) -> float:
    trial = copy.deepcopy(agent)
    branch = copy.deepcopy(world)
    trial.self_model.state += np.asarray(delta, dtype=np.float64)
    losses: list[float] = []
    for _ in range(V011_HORIZON):
        result = trial.step(
            branch.observe(V011_TOTAL_STEPS), source="v011_grounded_counterfactual"
        )
        branch.advance(result.action)
        losses.append(branch.tracking_loss())
    return float(np.mean(losses))


def _derangement(count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.arange(count)
    for _ in range(10_000):
        candidate = rng.permutation(count)
        if np.all(candidate != base):
            return candidate
    raise RuntimeError("failed to construct derangement")


def _bootstrap_interval(values: Sequence[float]) -> tuple[float, float]:
    x = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(V011_BOOTSTRAP_SEED)
    draws = np.empty(V011_BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for index in range(V011_BOOTSTRAP_RESAMPLES):
        sample = rng.integers(0, len(x), size=len(x))
        draws[index] = np.mean(x[sample])
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def run_grounded_control_experiment(output: str | Path, *, seeds: Sequence[int] = V011_DEVELOPMENT_SEEDS) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if seed_values != V011_DEVELOPMENT_SEEDS:
        raise ValueError("v0.11 development runner requires the exact frozen seed tuple")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError("output directory must be empty")

    training_rows: list[dict[str, Any]] = []
    evaluation_rows: list[dict[str, Any]] = []
    seed_summaries: list[dict[str, Any]] = []
    seed_contrasts: list[dict[str, Any]] = []

    for seed in seed_values:
        predictor, forecaster = _train_predictors(seed)
        feature_groups: list[np.ndarray] = []
        benefit_groups: list[np.ndarray] = []
        for episode_index in range(V011_TRANSFER_EPISODES):
            agent, world = _prime(seed, predictor, forecaster, seed + 20_000 + episode_index)
            plan = agent.plan_endogenous_self_intention(
                horizon=V011_HORIZON,
                query_budget=25,
                candidate_magnitude=V011_CANDIDATE_MAGNITUDE,
                forecast_mode="learned",
                selection_mode="rollout",
                calibration_mode="off",
            )
            precommit_digest = agent._endogenous_state_digest()
            baseline = _external_rollout(agent, world, plan.candidate_deltas[0])
            features: list[np.ndarray] = []
            benefits: list[float] = []
            for position, candidate_index in enumerate(plan.queried_indices):
                if candidate_index == 0:
                    continue
                external_loss = _external_rollout(
                    agent, world, plan.candidate_deltas[candidate_index]
                )
                benefit = baseline - external_loss
                features.append(np.asarray(plan.bayesian_features[position]).copy())
                benefits.append(float(benefit))
                training_rows.append(
                    {
                        "seed": seed,
                        "transfer_episode": episode_index,
                        "candidate_index": int(candidate_index),
                        "external_benefit": float(benefit),
                        "positive": bool(benefit > 1e-12),
                        "weight": 1.0 / 24.0,
                        "world_digest": world.spec.digest(),
                        "planning_nonmutating": precommit_digest == agent._endogenous_state_digest(),
                    }
                )
            feature_groups.append(np.stack(features))
            benefit_groups.append(np.asarray(benefits, dtype=np.float64))

        feature_matrix = np.concatenate(feature_groups, axis=0)
        benefit_vector = np.concatenate(benefit_groups, axis=0)
        weights = np.full(len(benefit_vector), 1.0 / 24.0, dtype=np.float64)
        aligned = WeightedRidgeTransfer(feature_matrix.shape[1], V011_RIDGE_PRIOR_PRECISION)
        aligned.fit(feature_matrix, benefit_vector, weights)
        permutation = _derangement(V011_TRANSFER_EPISODES, seed + 90_011)
        permuted_targets = np.concatenate(
            [benefit_groups[int(index)] for index in permutation], axis=0
        )
        permuted = WeightedRidgeTransfer(feature_matrix.shape[1], V011_RIDGE_PRIOR_PRECISION)
        permuted.fit(feature_matrix, permuted_targets, weights)
        hurdle = WeightedLogisticHurdle(feature_matrix.shape[1], V011_RIDGE_PRIOR_PRECISION)
        hurdle.fit(feature_matrix, (benefit_vector > 1e-12).astype(np.float64), weights)
        positive_values = benefit_vector[benefit_vector > 1e-12]
        nonpositive_values = -benefit_vector[benefit_vector <= 1e-12]
        positive_mean = float(np.mean(positive_values)) if len(positive_values) else 0.0
        downside_mean = float(np.mean(nonpositive_values)) if len(nonpositive_values) else 0.0

        policy_values: dict[str, list[float]] = defaultdict(list)
        policy_actions: dict[str, int] = defaultdict(int)
        policy_harms: dict[str, int] = defaultdict(int)
        policy_goods: dict[str, int] = defaultdict(int)
        opportunities = 0
        for episode_index in range(V011_EVALUATION_EPISODES):
            agent, world = _prime(seed, predictor, forecaster, seed + 40_000 + episode_index)
            plan = agent.plan_endogenous_self_intention(
                horizon=V011_HORIZON,
                query_budget=V011_QUERY_BUDGET,
                candidate_magnitude=V011_CANDIDATE_MAGNITUDE,
                forecast_mode="learned",
                selection_mode="rollout",
                calibration_mode="off",
            )
            positions = [i for i, candidate in enumerate(plan.queried_indices) if candidate != 0]
            candidate_indices = [plan.queried_indices[i] for i in positions]
            x = np.stack([plan.bayesian_features[i] for i in positions])
            rollout_scores = np.asarray(
                [
                    plan.predicted_baseline_error - plan.predicted_candidate_errors[i]
                    for i in positions
                ],
                dtype=np.float64,
            )
            aligned_scores = aligned.predict(x)
            permuted_scores = permuted.predict(x)
            probabilities = hurdle.predict_probability(x)
            hurdle_scores = probabilities * positive_mean - (1.0 - probabilities) * downside_mean
            score_map = {
                "internal_rollout": rollout_scores,
                "grounded_ridge": aligned_scores,
                "permuted_ridge": permuted_scores,
                "grounded_hurdle": hurdle_scores,
            }
            # Every policy decision is fixed before any held-out candidate outcome is computed.
            decisions: dict[str, int] = {"zero": 0}
            for arm, scores in score_map.items():
                position = int(np.argmax(scores))
                decisions[arm] = int(candidate_indices[position]) if scores[position] > 0.0 else 0
            decision_digest = hashlib.sha256(repr(sorted(decisions.items())).encode()).hexdigest()

            baseline = _external_rollout(agent, world, plan.candidate_deltas[0])
            outcome_by_candidate = {0: 0.0}
            for candidate_index in candidate_indices:
                outcome_by_candidate[int(candidate_index)] = float(
                    baseline - _external_rollout(agent, world, plan.candidate_deltas[candidate_index])
                )
            opportunities += int(max(outcome_by_candidate.values()) > 1e-12)
            for arm, selected in decisions.items():
                benefit = outcome_by_candidate[int(selected)]
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
                        "queried_opportunity": bool(max(outcome_by_candidate.values()) > 1e-12),
                        "decision_digest": decision_digest,
                        "world_digest": world.spec.digest(),
                        "outcomes_materialized_after_decision": True,
                    }
                )

        for arm in ("zero", "internal_rollout", "grounded_ridge", "permuted_ridge", "grounded_hurdle"):
            values = np.asarray(policy_values[arm], dtype=np.float64)
            action_count = policy_actions[arm]
            seed_summaries.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "net_external_improvement": float(np.mean(values)),
                    "action_coverage": action_count / V011_EVALUATION_EPISODES,
                    "beneficial_action_count": policy_goods[arm],
                    "harmful_action_count": policy_harms[arm],
                    "beneficial_precision": policy_goods[arm] / action_count if action_count else None,
                    "conditional_harm_rate": policy_harms[arm] / action_count if action_count else None,
                    "queried_opportunity_count": opportunities,
                }
            )
        summary_lookup = {
            row["arm"]: row for row in seed_summaries if row["seed"] == seed
        }
        seed_contrasts.append(
            {
                "seed": seed,
                "grounded_minus_internal": summary_lookup["grounded_ridge"]["net_external_improvement"] - summary_lookup["internal_rollout"]["net_external_improvement"],
                "grounded_minus_permuted": summary_lookup["grounded_ridge"]["net_external_improvement"] - summary_lookup["permuted_ridge"]["net_external_improvement"],
                "grounded_net": summary_lookup["grounded_ridge"]["net_external_improvement"],
                "hurdle_minus_internal": summary_lookup["grounded_hurdle"]["net_external_improvement"] - summary_lookup["internal_rollout"]["net_external_improvement"],
                "training_positive_rate": float(np.mean(benefit_vector > 1e-12)),
                "permutation": tuple(int(v) for v in permutation),
            }
        )

    primary = np.asarray([row["grounded_minus_internal"] for row in seed_contrasts])
    control = np.asarray([row["grounded_minus_permuted"] for row in seed_contrasts])
    net = np.asarray([row["grounded_net"] for row in seed_contrasts])
    primary_ci = _bootstrap_interval(primary)
    control_ci = _bootstrap_interval(control)
    net_ci = _bootstrap_interval(net)
    gates = {
        "grounded_beats_internal_mean": bool(np.mean(primary) > 0.0),
        "grounded_beats_internal_ci": bool(primary_ci[0] > 0.0),
        "grounded_beats_internal_seed_consistency": bool(np.sum(primary > 0.0) >= 3),
        "grounded_beats_permuted_mean": bool(np.mean(control) > 0.0),
        "grounded_beats_permuted_ci": bool(control_ci[0] > 0.0),
        "grounded_positive_external_net": bool(np.mean(net) > 0.0),
        "grounded_positive_external_ci": bool(net_ci[0] > 0.0),
        "commit_before_reveal": all(row["outcomes_materialized_after_decision"] for row in evaluation_rows),
        "training_planning_nonmutating": all(row["planning_nonmutating"] for row in training_rows),
    }
    gates["primary_success"] = bool(
        gates["grounded_beats_internal_ci"]
        and gates["grounded_beats_internal_seed_consistency"]
        and gates["grounded_beats_permuted_mean"]
        and gates["grounded_positive_external_ci"]
        and gates["commit_before_reveal"]
        and gates["training_planning_nonmutating"]
    )
    summary = {
        "schema": "rrct.v011.grounded_control_development.v1",
        "status": "exploratory_development_only",
        "seeds": seed_values,
        "protocol": {
            "predictor_episodes": V011_PREDICTOR_EPISODES,
            "transfer_episodes": V011_TRANSFER_EPISODES,
            "evaluation_episodes": V011_EVALUATION_EPISODES,
            "prefix_steps": V011_PREFIX_STEPS,
            "horizon": V011_HORIZON,
            "query_budget": V011_QUERY_BUDGET,
            "candidate_magnitude": V011_CANDIDATE_MAGNITUDE,
            "ridge_prior_precision": V011_RIDGE_PRIOR_PRECISION,
            "fractional_candidate_weight": 1.0 / 24.0,
        },
        "mean_grounded_minus_internal": float(np.mean(primary)),
        "grounded_minus_internal_ci95": primary_ci,
        "mean_grounded_minus_permuted": float(np.mean(control)),
        "grounded_minus_permuted_ci95": control_ci,
        "mean_grounded_external_net": float(np.mean(net)),
        "grounded_external_net_ci95": net_ci,
        "positive_seed_count_grounded_minus_internal": int(np.sum(primary > 0.0)),
        "gates": gates,
        "seed_contrasts": seed_contrasts,
        "limitations": [
            "The benchmark is synthetic and low-dimensional.",
            "The external objective is tracking error, not a consciousness metric.",
            "Counterfactual training still has privileged access to multiple cloned branches.",
            "This study does not establish awareness, sentience, phenomenology, or moral status.",
        ],
    }

    def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        keys = list(rows[0])
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(destination / "grounded_transfer_training_rows.csv", training_rows)
    write_csv(destination / "grounded_control_evaluation_rows.csv", evaluation_rows)
    write_csv(destination / "grounded_control_seed_summaries.csv", seed_summaries)
    with (destination / "grounded_control_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return summary


__all__ = [
    "GroundedTrackingWorld",
    "GroundedWorldSpec",
    "V011_DEVELOPMENT_SEEDS",
    "WeightedLogisticHurdle",
    "WeightedRidgeTransfer",
    "grounded_world_spec",
    "run_grounded_control_experiment",
]

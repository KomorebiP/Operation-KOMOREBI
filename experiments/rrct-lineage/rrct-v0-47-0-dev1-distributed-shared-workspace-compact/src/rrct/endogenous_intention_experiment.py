"""Development-only benchmark for endogenous nonvalenced self-regulation."""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from ._version import __version__
from .agent import RRCTAgent
from .experiments import _agent, _bootstrap_mean_ci, _episodes, _train_predictor_snapshot


V07_DEVELOPMENT_SEEDS = (1801, 1811, 1823, 1831)
V07_BOOTSTRAP_SEED = 20_260_824
V07_BOOTSTRAP_RESAMPLES = 2_000


def _prime(agent: RRCTAgent, observations: np.ndarray) -> None:
    agent.reset()
    agent.freeze_self_model()
    for observation in observations:
        agent.step(observation, source="v07_prime")


def _candidate_errors(
    template: RRCTAgent,
    candidates: np.ndarray,
    future: np.ndarray,
) -> np.ndarray:
    values: list[float] = []
    for delta in candidates:
        trial = copy.deepcopy(template)
        trial.self_model.state += delta
        steps = [trial.step(x, source="v07_offline_evaluator") for x in future]
        values.append(float(np.mean([step.error_norm for step in steps])))
    return np.asarray(values, dtype=np.float64)


def _rank_correlation(x: np.ndarray, y: np.ndarray) -> float:
    if np.all(x == x[0]) or np.all(y == y[0]):
        return 0.0
    def ranks(values: np.ndarray) -> np.ndarray:
        order = np.argsort(values, kind="stable")
        result = np.empty(len(values), dtype=np.float64)
        index = 0
        while index < len(values):
            end = index + 1
            while end < len(values) and values[order[end]] == values[order[index]]:
                end += 1
            result[order[index:end]] = 0.5 * (index + end - 1)
            index = end
        return result
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def _plot(path: Path, seed_rows: list[dict[str, float | int]]) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    labels = [str(row["seed"]) for row in seed_rows]
    x = np.arange(len(labels))
    width = 0.25
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
    axes[0].bar(x - width, [row["selected_improvement"] for row in seed_rows], width, label="endogenous")
    axes[0].bar(x, [row["random_improvement"] for row in seed_rows], width, label="budget random")
    axes[0].bar(x + width, [row["deranged_improvement"] for row in seed_rows], width, label="actuation deranged")
    axes[0].axhline(0.0, color="black", linewidth=0.8)
    axes[0].set_ylabel("mean unseen error reduction")
    axes[0].set_xticks(x, labels)
    axes[0].set_xlabel("development seed")
    axes[0].legend()
    axes[1].bar(x, [row["selection_advantage"] for row in seed_rows], color="#4979a8")
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].set_ylabel("selected reduction minus pool mean")
    axes[1].set_xticks(x, labels)
    axes[1].set_xlabel("development seed")
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
    fig.suptitle("Endogenous prediction-error regulation on unseen continuations")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return True


def run_endogenous_intention_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V07_DEVELOPMENT_SEEDS,
    train_episode_count: int = 64,
    probe_count: int = 8,
    train_delay: int = 5,
    test_delay: int = 7,
    horizon: int = 4,
    query_budget: int = 4,
    candidate_magnitude: float = 0.35,
    bootstrap_resamples: int = V07_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V07_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    seed_values = tuple(int(seed) for seed in seeds)
    if len(seed_values) < 2 or len(set(seed_values)) != len(seed_values):
        raise ValueError("at least two unique seeds are required")
    if set(seed_values) - set(V07_DEVELOPMENT_SEEDS):
        raise ValueError("development runner refuses non-development seeds")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError(f"output directory must be empty: {destination}")
    rows: list[dict[str, Any]] = []
    for seed in seed_values:
        snapshot = _train_predictor_snapshot(
            _episodes(train_episode_count, seed=seed + 10_000, delay=train_delay),
            seed=seed,
        )
        planning = _episodes(probe_count, seed=seed + 20_000, delay=test_delay)
        evaluation = _episodes(probe_count, seed=seed + 30_000, delay=test_delay)
        for probe, (planning_episode, evaluation_episode) in enumerate(zip(planning, evaluation)):
            agent = _agent(seed, self_model_mode="frozen")
            agent.load_predictor_snapshot(snapshot, freeze=True)
            observations = np.asarray(planning_episode.observations, dtype=np.float64)
            future = np.asarray(evaluation_episode.observations[-horizon:], dtype=np.float64)
            _prime(agent, observations[:-horizon])
            before = agent._endogenous_state_digest()
            plan = agent.plan_endogenous_self_intention(
                horizon=horizon,
                query_budget=query_budget,
                candidate_magnitude=candidate_magnitude,
            )
            planning_nonmutating = agent._endogenous_state_digest() == before
            errors = _candidate_errors(agent, plan.candidate_deltas, future)
            baseline_error = float(errors[0])
            reductions = baseline_error - errors
            selected = int(plan.selected_index)
            rng = np.random.default_rng(np.random.SeedSequence((seed, probe, 0x5637524E)))
            random_index = int(plan.queried_indices[int(rng.integers(0, len(plan.queried_indices)))])
            selected_position = plan.queried_indices.index(selected)
            deranged_index = int(plan.queried_indices[(selected_position + 1) % len(plan.queried_indices)])
            queried_realized_errors = errors[np.asarray(plan.queried_indices, dtype=int)]
            correlation = _rank_correlation(
                np.asarray(plan.predicted_candidate_errors), queried_realized_errors
            )
            receipt = agent.commit_endogenous_self_intention(plan)
            result = agent.evaluate_committed_intention(receipt, future)
            rows.append({
                "seed": seed,
                "probe": probe,
                "latent_factors": [planning_episode.context, planning_episode.object_cue, planning_episode.actuator_map],
                "candidate_count": int(plan.candidate_deltas.shape[0]),
                "queried_count": len(plan.queried_indices),
                "queried_indices": list(plan.queried_indices),
                "selected_index": selected,
                "random_index": random_index,
                "deranged_index": deranged_index,
                "candidate_deltas": plan.candidate_deltas.tolist(),
                "proxy_scores": plan.proxy_scores.tolist(),
                "predicted_candidate_errors": list(plan.predicted_candidate_errors),
                "realized_candidate_errors": errors.tolist(),
                "baseline_error": baseline_error,
                "selected_improvement": float(reductions[selected]),
                "random_improvement": float(reductions[random_index]),
                "deranged_improvement": float(reductions[deranged_index]),
                "pool_mean_improvement": float(np.mean(reductions)),
                "selection_advantage": float(reductions[selected] - np.mean(reductions)),
                "queried_prediction_realization_spearman": correlation,
                "forecast_observations": plan.forecast_observations.tolist(),
                "evaluation_observations": future.tolist(),
                "planning_nonmutating": planning_nonmutating,
                "commit_digest_matches": receipt.precommit_state_digest == plan.state_digest,
                "realized_api_matches_offline": bool(np.isclose(result.realized_selected_error, errors[selected], atol=1e-12, rtol=1e-12)),
                "predictor_updates_during_evaluation": int(agent.self_learning_updates - snapshot.get("learning_steps", 0)),
            })
    seed_rows: list[dict[str, float | int]] = []
    for seed in seed_values:
        group = [row for row in rows if row["seed"] == seed]
        seed_rows.append({
            "seed": seed,
            "selected_improvement": float(np.mean([row["selected_improvement"] for row in group])),
            "random_improvement": float(np.mean([row["random_improvement"] for row in group])),
            "deranged_improvement": float(np.mean([row["deranged_improvement"] for row in group])),
            "selection_advantage": float(np.mean([row["selection_advantage"] for row in group])),
            "correlation": float(np.mean([row["queried_prediction_realization_spearman"] for row in group])),
        })
    rng = np.random.default_rng(bootstrap_seed)
    metrics = {}
    for field in ("selected_improvement", "selection_advantage", "correlation"):
        values = [float(row[field]) for row in seed_rows]
        metrics[field] = {
            **_bootstrap_mean_ci(values, resamples=bootstrap_resamples, rng=rng),
            "positive_seed_count": int(np.count_nonzero(np.asarray(values) > 0.0)),
        }
    for name, left, right in (
        ("selected_minus_random", "selected_improvement", "random_improvement"),
        ("selected_minus_deranged", "selected_improvement", "deranged_improvement"),
    ):
        values = [float(row[left]) - float(row[right]) for row in seed_rows]
        metrics[name] = {
            **_bootstrap_mean_ci(values, resamples=bootstrap_resamples, rng=rng),
            "positive_seed_count": int(np.count_nonzero(np.asarray(values) > 0.0)),
        }
    csv_fields = [key for key in rows[0] if key not in {"candidate_deltas", "proxy_scores", "predicted_candidate_errors", "realized_candidate_errors", "forecast_observations", "evaluation_observations", "latent_factors", "queried_indices"}]
    with (destination / "endogenous_intention_rows.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows([{key: row[key] for key in csv_fields} for row in rows])
    figure_created = _plot(destination / "endogenous_intention.png", seed_rows)
    integrity = {
        "all_rows_retained": len(rows) == len(seed_values) * probe_count,
        "all_plans_nonmutating": all(row["planning_nonmutating"] for row in rows),
        "all_commit_digests_match": all(row["commit_digest_matches"] for row in rows),
        "all_api_evaluations_match_offline": all(row["realized_api_matches_offline"] for row in rows),
        "all_query_budgets_exact": all(row["queried_count"] == query_budget < row["candidate_count"] for row in rows),
        "no_predictor_updates": all(row["predictor_updates_during_evaluation"] == 0 for row in rows),
    }
    summary = {
        "version": __version__,
        "status": "completed_development_only" if all(integrity.values()) else "integrity_failure",
        "confirmatory_claim_allowed": False,
        "parameters": {"seeds": list(seed_values), "train_episode_count": train_episode_count, "probe_count": probe_count, "horizon": horizon, "query_budget": query_budget, "candidate_count": 25, "candidate_magnitude": candidate_magnitude},
        "integrity": integrity,
        "metrics": metrics,
        "seed_summaries": seed_rows,
        "rows": rows,
        "artifacts": ["endogenous_intention_summary.json", "endogenous_intention_rows.csv"] + (["endogenous_intention.png"] if figure_created else []),
        "interpretation_boundary": "This development experiment tests endogenous nonvalenced regulation of an internal workspace-prediction residual. It does not establish autonomous desire, consciousness, sentience, or subjective experience.",
    }
    (destination / "endogenous_intention_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return summary


__all__ = ["V07_DEVELOPMENT_SEEDS", "run_endogenous_intention_experiment"]

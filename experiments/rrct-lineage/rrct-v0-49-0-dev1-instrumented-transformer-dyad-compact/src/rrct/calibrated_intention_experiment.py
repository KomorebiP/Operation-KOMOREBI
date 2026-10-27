"""Development benchmark for learned forecasting and calibrated intentions."""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ._version import __version__
from .agent import RRCTAgent
from .experiments import (
    _agent,
    _bootstrap_mean_ci,
    _episodes,
    collect_representations,
)


V08_DEVELOPMENT_SEEDS = (2003, 2011, 2017, 2027)
V08_BOOTSTRAP_SEED = 20_260_826
V08_BOOTSTRAP_RESAMPLES = 2_000
FORECAST_MODES = ("decay", "learned")
ARM_NAMES = (
    "decay_uncalibrated",
    "decay_calibrated",
    "learned_uncalibrated",
    "learned_calibrated",
)


def _train_snapshots(
    *,
    seed: int,
    train_episode_count: int,
    train_delay: int,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    trainer = _agent(seed, self_model_mode="frozen")
    trainer.train_self_model()
    collect_representations(
        _episodes(train_episode_count, seed=seed + 10_000, delay=train_delay),
        seed=seed,
        agent=trainer,
    )
    trainer.freeze_self_model()
    return trainer.predictor_snapshot(), trainer.observation_forecaster_snapshot()


def _prime_agent(
    *,
    seed: int,
    predictor_snapshot: Mapping[str, Any],
    forecaster_snapshot: Mapping[str, Any],
    prefix: np.ndarray,
    calibration_snapshot: Mapping[str, Any] | None = None,
) -> RRCTAgent:
    agent = _agent(seed, self_model_mode="frozen")
    agent.load_predictor_snapshot(predictor_snapshot, freeze=True)
    agent.load_observation_forecaster_snapshot(forecaster_snapshot, freeze=True)
    agent.reset()
    agent.freeze_self_model()
    for observation in prefix:
        agent.step(observation, source="v08_same_episode_prefix")
    if calibration_snapshot is not None:
        agent.load_intention_calibration_snapshot(calibration_snapshot)
    return agent


def _candidate_errors(
    template: RRCTAgent,
    candidates: np.ndarray,
    future: np.ndarray,
) -> np.ndarray:
    errors: list[float] = []
    for delta in candidates:
        trial = copy.deepcopy(template)
        trial.self_model.state += np.asarray(delta, dtype=np.float64)
        steps = tuple(
            trial.step(observation, source="v08_offline_candidate")
            for observation in future
        )
        errors.append(float(np.mean([step.error_norm for step in steps])))
    return np.asarray(errors, dtype=np.float64)


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1)
        start = end
    return ranks


def _rank_correlation(left: np.ndarray, right: np.ndarray) -> float:
    if np.all(left == left[0]) or np.all(right == right[0]):
        return 0.0
    return float(np.corrcoef(_average_ranks(left), _average_ranks(right))[0, 1])


def _build_calibration_bank(
    *,
    seed: int,
    forecast_mode: str,
    episodes: Sequence[Any],
    predictor_snapshot: Mapping[str, Any],
    forecaster_snapshot: Mapping[str, Any],
    horizon: int,
    query_budget: int,
    candidate_magnitude: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bank: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    for episode_index, episode in enumerate(episodes):
        observations = np.asarray(episode.observations, dtype=np.float64)
        prefix = observations[:-horizon]
        hidden = observations[-horizon:]
        agent = _prime_agent(
            seed=seed,
            predictor_snapshot=predictor_snapshot,
            forecaster_snapshot=forecaster_snapshot,
            prefix=prefix,
            calibration_snapshot=bank,
        )
        before = agent.snapshot()
        plan = agent.plan_endogenous_self_intention(
            horizon=horizon,
            query_budget=query_budget,
            candidate_magnitude=candidate_magnitude,
            forecast_mode=forecast_mode,
            calibration_mode="explore",
        )
        record = agent.record_shadow_intention_calibration(plan, hidden)
        after = agent.snapshot()
        bank = agent.intention_calibration_snapshot()
        rows.append(
            {
                "seed": seed,
                "forecast_mode": forecast_mode,
                "calibration_episode": episode_index,
                "sequence_id": record.sequence_id,
                "calibration_key": record.calibration_key,
                "predicted_improvement": record.predicted_improvement,
                "realized_improvement": record.realized_improvement,
                "optimism": record.optimism,
                "selected_index": record.selected_index,
                "selected_delta_norm": record.selected_delta_norm,
                "outcome_source": record.outcome_source,
                "same_episode_suffix": bool(
                    np.array_equal(
                        np.concatenate((prefix, hidden), axis=0), observations
                    )
                ),
                "shadow_core_nonmutating": bool(
                    before["time"] == after["time"]
                    and before["resolution_level"] == after["resolution_level"]
                    and np.array_equal(before["workspace"], after["workspace"])
                    and np.array_equal(before["self_state"], after["self_state"])
                    and np.array_equal(before["last_action"], after["last_action"])
                ),
            }
        )
    if bank is None:
        raise RuntimeError("calibration bank was not created")
    return bank, rows


def _plot(
    path: Path,
    seed_summaries: list[dict[str, Any]],
) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    seeds = sorted({int(row["seed"]) for row in seed_summaries})
    lookup = {(int(row["seed"]), str(row["arm"])): row for row in seed_summaries}
    x = np.arange(len(seeds), dtype=np.float64)
    figure, axes = plt.subplots(1, 3, figsize=(15.2, 5.2))
    width = 0.18
    colors = ("#7a7a7a", "#b8b8b8", "#2f6f9f", "#79a9cf")
    for index, arm in enumerate(ARM_NAMES):
        offset = (index - 1.5) * width
        axes[0].bar(
            x + offset,
            [lookup[(seed, arm)]["selected_improvement"] for seed in seeds],
            width,
            label=arm.replace("_", " "),
            color=colors[index],
        )
    axes[0].axhline(0.0, color="black", linewidth=0.8)
    axes[0].set_title("Realized internal error reduction")
    axes[0].set_ylabel("mean reduction vs zero intervention")
    axes[0].set_xticks(x, [str(seed) for seed in seeds])

    axes[1].bar(
        x - width / 2,
        [lookup[(seed, "decay_uncalibrated")]["forecast_rmse"] for seed in seeds],
        width,
        label="fixed decay",
        color="#7a7a7a",
    )
    axes[1].bar(
        x + width / 2,
        [lookup[(seed, "learned_uncalibrated")]["forecast_rmse"] for seed in seeds],
        width,
        label="learned AR(1)",
        color="#2f6f9f",
    )
    axes[1].set_title("Literal hidden-suffix forecast")
    axes[1].set_ylabel("observation RMSE")
    axes[1].set_xticks(x, [str(seed) for seed in seeds])

    for index, arm in enumerate(ARM_NAMES):
        offset = (index - 1.5) * width
        axes[2].bar(
            x + offset,
            [lookup[(seed, arm)]["nonzero_rate"] for seed in seeds],
            width,
            color=colors[index],
        )
    axes[2].set_title("Gate behavior")
    axes[2].set_ylabel("nonzero intervention rate")
    axes[2].set_ylim(0.0, 1.0)
    axes[2].set_xticks(x, [str(seed) for seed in seeds])
    axes[2].text(
        0.02,
        0.96,
        "both calibrated arms = 0 on every seed",
        transform=axes[2].transAxes,
        ha="left",
        va="top",
        fontsize=9,
    )

    for axis in axes:
        axis.set_xlabel("development seed")
        axis.grid(axis="y", alpha=0.25)
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8)
    figure.suptitle("RRCT v0.8 learned forecasting × prospective calibration")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return True


def run_calibrated_intention_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V08_DEVELOPMENT_SEEDS,
    train_episode_count: int = 64,
    calibration_episode_count: int = 32,
    evaluation_episode_count: int = 32,
    train_delay: int = 5,
    test_delay: int = 7,
    horizon: int = 4,
    query_budget: int = 4,
    candidate_magnitude: float = 0.35,
    calibration_alpha: float = 0.05,
    calibration_min_samples: int = 19,
    bootstrap_resamples: int = V08_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V08_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run the development-only learned-forecast × calibration factorial."""

    seed_values = tuple(int(seed) for seed in seeds)
    if len(seed_values) < 2 or len(set(seed_values)) != len(seed_values):
        raise ValueError("at least two unique development seeds are required")
    if set(seed_values) - set(V08_DEVELOPMENT_SEEDS):
        raise ValueError("runner refuses seeds outside the development set")
    if calibration_episode_count < calibration_min_samples:
        raise ValueError("calibration episodes must meet calibration_min_samples")
    if train_episode_count < 8 or evaluation_episode_count < 8:
        raise ValueError("training and evaluation require at least eight episodes")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError(f"output directory must be empty: {destination}")

    rows: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    bank_summaries: list[dict[str, Any]] = []
    for seed in seed_values:
        predictor_snapshot, forecaster_snapshot = _train_snapshots(
            seed=seed,
            train_episode_count=train_episode_count,
            train_delay=train_delay,
        )
        calibration_episodes = _episodes(
            calibration_episode_count,
            seed=seed + 20_000,
            delay=test_delay,
        )
        banks: dict[str, dict[str, Any]] = {}
        for forecast_mode in FORECAST_MODES:
            bank, bank_rows = _build_calibration_bank(
                seed=seed,
                forecast_mode=forecast_mode,
                episodes=calibration_episodes,
                predictor_snapshot=predictor_snapshot,
                forecaster_snapshot=forecaster_snapshot,
                horizon=horizon,
                query_budget=query_budget,
                candidate_magnitude=candidate_magnitude,
            )
            banks[forecast_mode] = bank
            calibration_rows.extend(bank_rows)
            optimism = tuple(float(item["optimism"]) for item in bank["records"])
            ready, threshold = RRCTAgent._conformal_optimism_threshold(
                optimism,
                alpha=calibration_alpha,
                minimum_records=calibration_min_samples,
            )
            bank_summaries.append(
                {
                    "seed": seed,
                    "forecast_mode": forecast_mode,
                    "count": int(bank["count"]),
                    "ready": ready,
                    "threshold": threshold,
                    "optimism_mean": float(np.mean(optimism)),
                    "optimism_min": float(np.min(optimism)),
                    "optimism_max": float(np.max(optimism)),
                    "digest": str(bank["digest"]),
                }
            )

        evaluation_episodes = _episodes(
            evaluation_episode_count,
            seed=seed + 30_000,
            delay=test_delay,
        )
        for episode_index, episode in enumerate(evaluation_episodes):
            observations = np.asarray(episode.observations, dtype=np.float64)
            prefix = observations[:-horizon]
            hidden = observations[-horizon:]
            for forecast_mode in FORECAST_MODES:
                for calibrated in (False, True):
                    arm = f"{forecast_mode}_{'calibrated' if calibrated else 'uncalibrated'}"
                    agent = _prime_agent(
                        seed=seed,
                        predictor_snapshot=predictor_snapshot,
                        forecaster_snapshot=forecaster_snapshot,
                        prefix=prefix,
                        calibration_snapshot=(banks[forecast_mode] if calibrated else None),
                    )
                    before_digest = agent._endogenous_state_digest()
                    plan = agent.plan_endogenous_self_intention(
                        horizon=horizon,
                        query_budget=query_budget,
                        candidate_magnitude=candidate_magnitude,
                        forecast_mode=forecast_mode,
                        calibration_mode=("conservative" if calibrated else "off"),
                        calibration_alpha=calibration_alpha,
                        calibration_min_samples=calibration_min_samples,
                    )
                    planning_nonmutating = before_digest == agent._endogenous_state_digest()
                    errors = _candidate_errors(agent, plan.candidate_deltas, hidden)
                    baseline_error = float(errors[0])
                    reductions = baseline_error - errors
                    selected_index = int(plan.selected_index)
                    raw_index = int(plan.raw_selected_index)
                    nonzero_indices = np.arange(1, errors.size, dtype=int)
                    oracle_index = int(np.argmax(reductions))
                    best_nonzero_index = int(
                        nonzero_indices[np.argmax(reductions[nonzero_indices])]
                    )
                    rng = np.random.default_rng(
                        np.random.SeedSequence(
                            (seed, episode_index, 1 if forecast_mode == "learned" else 0)
                        )
                    )
                    random_index = int(
                        plan.queried_indices[
                            int(rng.integers(0, len(plan.queried_indices)))
                        ]
                    )
                    queried_errors = errors[
                        np.asarray(plan.queried_indices, dtype=int)
                    ]
                    forecast_rmse = float(
                        np.sqrt(np.mean(np.square(plan.forecast_observations - hidden)))
                    )
                    threshold = plan.uncertainty_threshold
                    coverage = (
                        None
                        if not calibrated or raw_index == 0 or threshold is None
                        else bool(
                            reductions[raw_index]
                            + 1e-15
                            >= plan.raw_predicted_improvement - threshold
                        )
                    )
                    receipt = agent.commit_endogenous_self_intention(plan)
                    result = agent.evaluate_committed_intention(receipt, hidden)
                    realized_workspace = np.stack(
                        [step.workspace for step in result.realized_steps]
                    )
                    realized_actions = np.stack(
                        [step.action for step in result.realized_steps]
                    )
                    rows.append(
                        {
                            "seed": seed,
                            "evaluation_episode": episode_index,
                            "arm": arm,
                            "forecast_mode": forecast_mode,
                            "calibrated": calibrated,
                            "latent_context": int(episode.context),
                            "latent_object": int(episode.object_cue),
                            "latent_actuator": int(episode.actuator_map),
                            "same_episode_suffix": bool(
                                np.array_equal(
                                    np.concatenate((prefix, hidden), axis=0),
                                    observations,
                                )
                            ),
                            "planning_nonmutating": planning_nonmutating,
                            "calibration_count": plan.calibration_count,
                            "calibration_ready": plan.calibration_ready,
                            "calibration_threshold": threshold,
                            "conservative_lower_bound": plan.conservative_lower_bound,
                            "abstained": plan.abstained,
                            "abstention_reason": plan.abstention_reason,
                            "raw_selected_index": raw_index,
                            "selected_index": selected_index,
                            "oracle_index": oracle_index,
                            "best_nonzero_index": best_nonzero_index,
                            "random_index": random_index,
                            "raw_predicted_improvement": plan.raw_predicted_improvement,
                            "predicted_improvement": plan.predicted_improvement,
                            "baseline_error": baseline_error,
                            "selected_improvement": float(reductions[selected_index]),
                            "raw_improvement": float(reductions[raw_index]),
                            "oracle_improvement": float(reductions[oracle_index]),
                            "best_nonzero_improvement": float(
                                reductions[best_nonzero_index]
                            ),
                            "random_improvement": float(reductions[random_index]),
                            "pool_mean_improvement": float(np.mean(reductions)),
                            "selection_advantage": float(
                                reductions[selected_index] - np.mean(reductions)
                            ),
                            "oracle_regret": float(
                                reductions[oracle_index] - reductions[selected_index]
                            ),
                            "harm": bool(reductions[selected_index] < -1e-12),
                            "nonzero": selected_index != 0,
                            "beneficial_nonzero": bool(
                                selected_index != 0
                                and reductions[selected_index] > 1e-12
                            ),
                            "opportunity": bool(
                                reductions[best_nonzero_index] > 1e-12
                            ),
                            "coverage": coverage,
                            "forecast_rmse": forecast_rmse,
                            "forecast_mae": float(
                                np.mean(np.abs(plan.forecast_observations - hidden))
                            ),
                            "queried_prediction_realization_spearman": _rank_correlation(
                                np.asarray(plan.predicted_candidate_errors),
                                queried_errors,
                            ),
                            "workspace_variance": float(np.var(realized_workspace)),
                            "action_variance": float(np.var(realized_actions)),
                            "api_matches_offline": bool(
                                np.isclose(
                                    result.realized_selected_error,
                                    errors[selected_index],
                                    atol=1e-12,
                                    rtol=1e-12,
                                )
                            ),
                            "self_predictor_updates": int(
                                agent.self_learning_updates
                                - int(predictor_snapshot["learning_steps"])
                            ),
                            "observation_forecaster_updates": int(
                                agent.observation_forecaster.learning_steps
                                - int(forecaster_snapshot["learning_steps"])
                            ),
                            "forecast_observations": plan.forecast_observations.tolist(),
                            "hidden_observations": hidden.tolist(),
                            "candidate_errors": errors.tolist(),
                            "predicted_queried_errors": list(
                                plan.predicted_candidate_errors
                            ),
                            "queried_indices": list(plan.queried_indices),
                        }
                    )

    seed_summaries: list[dict[str, Any]] = []
    for seed in seed_values:
        for arm in ARM_NAMES:
            group = [row for row in rows if row["seed"] == seed and row["arm"] == arm]
            opportunities = [row for row in group if row["opportunity"]]
            covered = [row for row in group if row["coverage"] is not None]
            seed_summaries.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "forecast_rmse": float(np.mean([row["forecast_rmse"] for row in group])),
                    "selected_improvement": float(
                        np.mean([row["selected_improvement"] for row in group])
                    ),
                    "raw_improvement": float(
                        np.mean([row["raw_improvement"] for row in group])
                    ),
                    "selection_advantage": float(
                        np.mean([row["selection_advantage"] for row in group])
                    ),
                    "oracle_regret": float(
                        np.mean([row["oracle_regret"] for row in group])
                    ),
                    "harm_rate": float(np.mean([row["harm"] for row in group])),
                    "nonzero_rate": float(np.mean([row["nonzero"] for row in group])),
                    "beneficial_action_rate": float(
                        np.mean([row["beneficial_nonzero"] for row in group])
                    ),
                    "opportunity_rate": float(
                        np.mean([row["opportunity"] for row in group])
                    ),
                    "opportunity_recall": (
                        float(
                            np.mean(
                                [row["beneficial_nonzero"] for row in opportunities]
                            )
                        )
                        if opportunities
                        else None
                    ),
                    "coverage_rate": (
                        float(np.mean([row["coverage"] for row in covered]))
                        if covered
                        else None
                    ),
                    "workspace_variance": float(
                        np.mean([row["workspace_variance"] for row in group])
                    ),
                    "rank_correlation": float(
                        np.mean(
                            [
                                row["queried_prediction_realization_spearman"]
                                for row in group
                            ]
                        )
                    ),
                }
            )

    rng = np.random.default_rng(bootstrap_seed)
    aggregate_metrics: dict[str, dict[str, dict[str, float]]] = {}
    numeric_fields = (
        "forecast_rmse",
        "selected_improvement",
        "raw_improvement",
        "selection_advantage",
        "oracle_regret",
        "harm_rate",
        "nonzero_rate",
        "beneficial_action_rate",
        "opportunity_rate",
        "workspace_variance",
        "rank_correlation",
    )
    for arm in ARM_NAMES:
        group = [row for row in seed_summaries if row["arm"] == arm]
        aggregate_metrics[arm] = {
            field: _bootstrap_mean_ci(
                [float(row[field]) for row in group],
                resamples=bootstrap_resamples,
                rng=rng,
            )
            for field in numeric_fields
        }

    seed_lookup = {
        (int(row["seed"]), str(row["arm"])): row for row in seed_summaries
    }
    contrasts: dict[str, dict[str, float]] = {}
    contrast_specs = {
        "learned_minus_decay_forecast_rmse": (
            "learned_uncalibrated",
            "decay_uncalibrated",
            "forecast_rmse",
        ),
        "learned_minus_decay_uncalibrated_improvement": (
            "learned_uncalibrated",
            "decay_uncalibrated",
            "selected_improvement",
        ),
        "decay_calibration_effect": (
            "decay_calibrated",
            "decay_uncalibrated",
            "selected_improvement",
        ),
        "learned_calibration_effect": (
            "learned_calibrated",
            "learned_uncalibrated",
            "selected_improvement",
        ),
        "learned_calibrated_minus_decay_uncalibrated": (
            "learned_calibrated",
            "decay_uncalibrated",
            "selected_improvement",
        ),
    }
    for name, (left, right, field) in contrast_specs.items():
        values = [
            float(seed_lookup[(seed, left)][field])
            - float(seed_lookup[(seed, right)][field])
            for seed in seed_values
        ]
        contrasts[name] = {
            **_bootstrap_mean_ci(
                values, resamples=bootstrap_resamples, rng=rng
            ),
            "positive_seed_count": int(
                np.count_nonzero(np.asarray(values, dtype=np.float64) > 0.0)
            ),
            "negative_seed_count": int(
                np.count_nonzero(np.asarray(values, dtype=np.float64) < 0.0)
            ),
        }

    raw_pairs_match = True
    for seed in seed_values:
        for episode_index in range(evaluation_episode_count):
            for forecast_mode in FORECAST_MODES:
                pair = [
                    row
                    for row in rows
                    if row["seed"] == seed
                    and row["evaluation_episode"] == episode_index
                    and row["forecast_mode"] == forecast_mode
                ]
                raw_pairs_match = raw_pairs_match and len(pair) == 2 and bool(
                    pair[0]["raw_selected_index"] == pair[1]["raw_selected_index"]
                    and pair[0]["raw_predicted_improvement"]
                    == pair[1]["raw_predicted_improvement"]
                    and pair[0]["forecast_observations"]
                    == pair[1]["forecast_observations"]
                    and pair[0]["candidate_errors"] == pair[1]["candidate_errors"]
                )

    integrity = {
        "all_evaluation_rows_retained": len(rows)
        == len(seed_values) * evaluation_episode_count * len(ARM_NAMES),
        "all_calibration_rows_retained": len(calibration_rows)
        == len(seed_values) * calibration_episode_count * len(FORECAST_MODES),
        "all_calibration_banks_ready": all(row["ready"] for row in bank_summaries),
        "all_calibration_records_shadow_labeled": all(
            row["outcome_source"] == "shadow" for row in calibration_rows
        ),
        "all_shadow_calibration_core_nonmutating": all(
            row["shadow_core_nonmutating"] for row in calibration_rows
        ),
        "all_suffixes_from_same_episode": all(
            row["same_episode_suffix"] for row in calibration_rows
        )
        and all(row["same_episode_suffix"] for row in rows),
        "all_plans_nonmutating": all(row["planning_nonmutating"] for row in rows),
        "all_api_evaluations_match_offline": all(
            row["api_matches_offline"] for row in rows
        ),
        "no_predictor_updates_during_evaluation": all(
            row["self_predictor_updates"] == 0
            and row["observation_forecaster_updates"] == 0
            for row in rows
        ),
        "calibration_changes_only_gate_not_raw_plan": raw_pairs_match,
    }

    scalar_csv_fields = [
        key
        for key in rows[0]
        if key
        not in {
            "forecast_observations",
            "hidden_observations",
            "candidate_errors",
            "predicted_queried_errors",
            "queried_indices",
        }
    ]
    with (destination / "calibrated_intention_rows.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=scalar_csv_fields)
        writer.writeheader()
        writer.writerows(
            [{field: row[field] for field in scalar_csv_fields} for row in rows]
        )
    with (destination / "calibration_records.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(calibration_rows[0]))
        writer.writeheader()
        writer.writerows(calibration_rows)
    figure_created = _plot(
        destination / "calibrated_intention.png", seed_summaries
    )
    summary = {
        "version": __version__,
        "experiment": "v0.8_learned_forecast_by_conformal_intention_gate",
        "status": (
            "completed_development_only"
            if all(integrity.values())
            else "integrity_failure"
        ),
        "confirmatory_claim_allowed": False,
        "parameters": {
            "seeds": list(seed_values),
            "train_episode_count": train_episode_count,
            "calibration_episode_count": calibration_episode_count,
            "evaluation_episode_count": evaluation_episode_count,
            "train_delay": train_delay,
            "test_delay": test_delay,
            "horizon": horizon,
            "query_budget": query_budget,
            "candidate_count": 25,
            "candidate_magnitude": candidate_magnitude,
            "calibration_alpha": calibration_alpha,
            "calibration_min_samples": calibration_min_samples,
            "calibration_residual": (
                "maximum signed forecast optimism across queried nonzero "
                "candidates per calibration episode"
            ),
            "future_protocol": "literal withheld suffix of the same episode",
        },
        "integrity": integrity,
        "calibration_banks": bank_summaries,
        "arm_metrics": aggregate_metrics,
        "contrasts": contrasts,
        "seed_summaries": seed_summaries,
        "rows": rows,
        "calibration_rows": calibration_rows,
        "artifacts": [
            "calibrated_intention_summary.json",
            "calibrated_intention_rows.csv",
            "calibration_records.csv",
        ]
        + (["calibrated_intention.png"] if figure_created else []),
        "interpretation_boundary": (
            "This development experiment measures learned observation forecasting "
            "and a one-sided split-conformal gate for bounded interventions that "
            "regulate an internal workspace-prediction residual under fixed future "
            "observations. It does not establish consciousness, sentience, desire, "
            "subjective uncertainty, external-task benefit, or interactive-world causality."
        ),
    }
    (destination / "calibrated_intention_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


__all__ = ["V08_DEVELOPMENT_SEEDS", "run_calibrated_intention_experiment"]

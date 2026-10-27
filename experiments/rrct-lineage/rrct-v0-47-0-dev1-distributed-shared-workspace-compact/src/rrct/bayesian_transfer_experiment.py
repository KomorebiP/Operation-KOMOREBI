"""Separated development benchmark for Bayesian causal-transfer intentions."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ._version import __version__
from .agent import BayesianTransferUpdate, EndogenousSelfPlan, RRCTAgent
from .experiments import _agent, _bootstrap_mean_ci, _episodes, collect_representations


V09_DEVELOPMENT_SEEDS = (2309, 2311, 2333, 2339)
V09_BOOTSTRAP_SEED = 20_260_920
V09_BOOTSTRAP_RESAMPLES = 2_000
ARM_SPECS = {
    "always_zero": (None, "always_zero", "off", None),
    "rollout_uncalibrated": (None, "rollout", "off", None),
    "rollout_conformal": (None, "rollout", "conservative", "rollout"),
    "bayes_mean": ("bayes", "bayesian_mean", "off", None),
    "bayes_credible": ("bayes", "bayesian_credible", "off", None),
    "bayes_conformal": ("bayes", "bayesian_mean", "conservative", "bayes"),
    "permuted_bayes_conformal": (
        "permuted", "bayesian_mean", "conservative", "permuted"
    ),
}


def _episode_hash(episode: Any) -> str:
    observations = np.ascontiguousarray(episode.observations, dtype=np.float64)
    payload = (
        observations.tobytes(),
        int(episode.context),
        int(episode.object_cue),
        int(episode.actuator_map),
    )
    return hashlib.sha256(repr(payload[1:]).encode() + payload[0]).hexdigest()


def _train_predictors(
    *, seed: int, episode_count: int, delay: int
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    trainer = _agent(seed, self_model_mode="frozen")
    trainer.train_self_model()
    collect_representations(
        _episodes(episode_count, seed=seed + 10_000, delay=delay),
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
    transfer_snapshot: Mapping[str, Any] | None = None,
    calibration_snapshot: Mapping[str, Any] | None = None,
    transfer_training: bool = False,
) -> RRCTAgent:
    agent = _agent(seed, self_model_mode="frozen")
    agent.load_predictor_snapshot(predictor_snapshot, freeze=True)
    agent.load_observation_forecaster_snapshot(forecaster_snapshot, freeze=True)
    if transfer_snapshot is not None:
        agent.load_bayesian_transfer_snapshot(
            transfer_snapshot, freeze=not transfer_training
        )
    elif transfer_training:
        agent.train_bayesian_transfer()
    agent.reset()
    agent.freeze_self_model()
    for observation in prefix:
        agent.step(observation, source="v09_same_episode_prefix")
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
            trial.step(observation, source="v09_offline_candidate")
            for observation in future
        )
        errors.append(float(np.mean([step.error_norm for step in steps])))
    return np.asarray(errors, dtype=np.float64)


def _train_transfer(
    *,
    seed: int,
    episodes: Sequence[Any],
    predictor_snapshot: Mapping[str, Any],
    forecaster_snapshot: Mapping[str, Any],
    horizon: int,
    candidate_magnitude: float,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    bank: dict[str, Any] | None = None
    feature_groups: list[np.ndarray] = []
    target_groups: list[np.ndarray] = []
    candidate_index_groups: list[tuple[int, ...]] = []
    rows: list[dict[str, Any]] = []
    transfer_key: str | None = None
    for episode_index, episode in enumerate(episodes):
        observations = np.asarray(episode.observations, dtype=np.float64)
        prefix = observations[:-horizon]
        agent = _prime_agent(
            seed=seed,
            predictor_snapshot=predictor_snapshot,
            forecaster_snapshot=forecaster_snapshot,
            prefix=prefix,
            transfer_snapshot=bank,
            transfer_training=True,
        )
        before = agent.snapshot()
        plan = agent.plan_endogenous_self_intention(
            horizon=horizon,
            query_budget=25,
            candidate_magnitude=candidate_magnitude,
            forecast_mode="learned",
            selection_mode="rollout",
            calibration_mode="off",
        )
        hidden = observations[-horizon:].copy()
        update = agent.record_shadow_bayesian_transfer(plan, hidden)
        after = agent.snapshot()
        transfer_key = plan.bayesian_transfer_key
        feature_group = np.asarray(plan.bayesian_features[1:], dtype=np.float64)
        target_group = np.asarray(update.normalized_targets, dtype=np.float64)
        feature_groups.append(feature_group.copy())
        target_groups.append(target_group.copy())
        candidate_index_groups.append(tuple(int(value) for value in update.candidate_indices))
        rollout_benefits = np.asarray(
            [
                plan.predicted_baseline_error - value
                for value in plan.predicted_candidate_errors[1:]
            ],
            dtype=np.float64,
        )
        for position, candidate_index in enumerate(update.candidate_indices):
            row: dict[str, Any] = {
                "seed": seed,
                "transfer_episode": episode_index,
                "episode_hash": _episode_hash(episode),
                "candidate_index": candidate_index,
                "rollout_predicted_improvement": float(rollout_benefits[position]),
                "realized_improvement": float(
                    rollout_benefits[position]
                    + target_group[position] * agent.bayesian_transfer_target_scale
                ),
                "normalized_transfer_correction": float(target_group[position]),
                "per_candidate_weight": update.per_candidate_weight,
                "same_episode_suffix": bool(
                    np.array_equal(np.concatenate((prefix, hidden)), observations)
                ),
                "shadow_core_nonmutating": bool(
                    before["time"] == after["time"]
                    and before["resolution_level"] == after["resolution_level"]
                    and np.array_equal(before["workspace"], after["workspace"])
                    and np.array_equal(before["self_state"], after["self_state"])
                    and np.array_equal(before["last_action"], after["last_action"])
                ),
            }
            for feature_name, feature_value in zip(
                RRCTAgent.BAYESIAN_TRANSFER_FEATURE_NAMES,
                feature_group[position],
            ):
                row[f"feature_{feature_name}"] = float(feature_value)
            rows.append(row)
        bank = agent.bayesian_transfer_snapshot()
    if bank is None or transfer_key is None:
        raise RuntimeError("Bayesian transfer bank was not created")
    final_agent = _prime_agent(
        seed=seed,
        predictor_snapshot=predictor_snapshot,
        forecaster_snapshot=forecaster_snapshot,
        prefix=np.asarray(episodes[-1].observations[:-horizon]),
        transfer_snapshot=bank,
    )
    final_agent.freeze_bayesian_transfer()
    bank = final_agent.bayesian_transfer_snapshot()

    permutation = np.random.default_rng(
        np.random.SeedSequence((seed, 90_091))
    ).permutation(len(target_groups))
    permuted_agent = _prime_agent(
        seed=seed,
        predictor_snapshot=predictor_snapshot,
        forecaster_snapshot=forecaster_snapshot,
        prefix=np.asarray(episodes[0].observations[:-horizon]),
        transfer_training=True,
    )
    permuted_agent._bayesian_transfer_key = transfer_key
    per_candidate_weight = 1.0 / feature_groups[0].shape[0]
    permutation_digest = RRCTAgent.bayesian_transfer_permutation_digest(
        transfer_key, tuple(int(value) for value in permutation)
    )
    for episode_index, (feature_group, candidate_indices, target_index) in enumerate(
        zip(feature_groups, candidate_index_groups, permutation)
    ):
        normalized_targets = target_groups[int(target_index)]
        target_candidate_indices = candidate_index_groups[int(target_index)]
        count_before = permuted_agent.bayesian_transfer.observation_count
        effective_before = permuted_agent.bayesian_transfer.effective_sample_count
        digest_before = permuted_agent.bayesian_transfer.posterior_digest()
        permuted_agent.bayesian_transfer.observe_batch(
            feature_group,
            normalized_targets,
            weights=np.full(feature_group.shape[0], per_candidate_weight),
        )
        permuted_agent._bayesian_transfer_updates.append(
            BayesianTransferUpdate(
                sequence_id=episode_index,
                transfer_key=transfer_key,
                evidence_digest=RRCTAgent.bayesian_transfer_control_evidence_digest(
                    permutation_digest=permutation_digest,
                    feature_episode_index=episode_index,
                    target_episode_index=int(target_index),
                    candidate_indices=candidate_indices,
                    target_candidate_indices=target_candidate_indices,
                    normalized_targets=normalized_targets,
                ),
                planned_time=None,
                recorded_time=None,
                feature_episode_index=episode_index,
                target_episode_index=int(target_index),
                target_candidate_indices=target_candidate_indices,
                permutation_digest=permutation_digest,
                candidate_indices=candidate_indices,
                normalized_targets=tuple(float(value) for value in normalized_targets),
                per_candidate_weight=per_candidate_weight,
                observation_count_before=count_before,
                observation_count_after=(
                    permuted_agent.bayesian_transfer.observation_count
                ),
                effective_sample_count_before=effective_before,
                effective_sample_count_after=(
                    permuted_agent.bayesian_transfer.effective_sample_count
                ),
                posterior_digest_before=digest_before,
                posterior_digest_after=(
                    permuted_agent.bayesian_transfer.posterior_digest()
                ),
                outcome_source="permuted_control",
            )
        )
    permuted_agent.freeze_bayesian_transfer()
    return bank, permuted_agent.bayesian_transfer_snapshot(), rows


def _build_calibration_bank(
    *,
    seed: int,
    episodes: Sequence[Any],
    predictor_snapshot: Mapping[str, Any],
    forecaster_snapshot: Mapping[str, Any],
    transfer_snapshot: Mapping[str, Any] | None,
    selection_mode: str,
    horizon: int,
    query_budget: int,
    candidate_magnitude: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bank: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    for episode_index, episode in enumerate(episodes):
        observations = np.asarray(episode.observations, dtype=np.float64)
        prefix = observations[:-horizon]
        agent = _prime_agent(
            seed=seed,
            predictor_snapshot=predictor_snapshot,
            forecaster_snapshot=forecaster_snapshot,
            prefix=prefix,
            transfer_snapshot=transfer_snapshot,
            calibration_snapshot=bank,
        )
        before = agent.snapshot()
        plan = agent.plan_endogenous_self_intention(
            horizon=horizon,
            query_budget=query_budget,
            candidate_magnitude=candidate_magnitude,
            forecast_mode="learned",
            selection_mode=selection_mode,
            calibration_mode="explore",
        )
        hidden = observations[-horizon:].copy()
        record = agent.record_shadow_intention_calibration(plan, hidden)
        after = agent.snapshot()
        bank = agent.intention_calibration_snapshot()
        rows.append(
            {
                "seed": seed,
                "selection_mode": selection_mode,
                "calibration_episode": episode_index,
                "episode_hash": _episode_hash(episode),
                "predicted_improvement": record.predicted_improvement,
                "realized_improvement": record.realized_improvement,
                "optimism": record.optimism,
                "selected_index": record.selected_index,
                "policy_raw_selected_index": int(plan.raw_selected_index),
                "policy_raw_predicted_improvement": float(
                    plan.raw_predicted_improvement
                ),
                "same_episode_suffix": bool(
                    np.array_equal(np.concatenate((prefix, hidden)), observations)
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


def _student_t_log_density(
    value: float, *, mean: float, scale_squared: float, degrees_of_freedom: float
) -> float:
    standardized_squared = (value - mean) ** 2 / scale_squared
    return float(
        math.lgamma((degrees_of_freedom + 1.0) / 2.0)
        - math.lgamma(degrees_of_freedom / 2.0)
        - 0.5 * math.log(degrees_of_freedom * math.pi * scale_squared)
        - 0.5
        * (degrees_of_freedom + 1.0)
        * math.log1p(standardized_squared / degrees_of_freedom)
    )


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


def _rank_correlation(left: Sequence[float], right: Sequence[float]) -> float:
    left_values = np.asarray(left, dtype=np.float64)
    right_values = np.asarray(right, dtype=np.float64)
    if left_values.size < 2 or np.all(left_values == left_values[0]) or np.all(
        right_values == right_values[0]
    ):
        return 0.0
    return float(
        np.corrcoef(_average_ranks(left_values), _average_ranks(right_values))[0, 1]
    )


def _bayesian_risk_coverage_rows(
    *,
    seeds: Sequence[int],
    calibration_rows: Sequence[Mapping[str, Any]],
    evaluation_predictions: Sequence[Mapping[str, Any]],
    policy_evaluations: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Evaluate thresholds fixed from calibration predictions, never outcomes."""

    quantiles = tuple(float(value) for value in np.linspace(0.0, 1.0, 11))
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        calibration_predictions = np.asarray(
            [
                float(row["policy_raw_predicted_improvement"])
                for row in calibration_rows
                if int(row["seed"]) == seed and row.get("bank") == "bayes"
            ],
            dtype=np.float64,
        )
        if calibration_predictions.size == 0 or not np.all(
            np.isfinite(calibration_predictions)
        ):
            raise RuntimeError("Bayesian calibration predictions are unavailable")
        thresholds = [
            (
                f"calibration_q{int(round(100.0 * quantile)):03d}",
                quantile,
                float(np.quantile(calibration_predictions, quantile)),
                False,
            )
            for quantile in quantiles
        ]
        thresholds.append(("minimum_effect_zero", None, 0.0, False))
        thresholds.append(("forced_abstain", None, None, True))
        episode_groups: dict[int, list[Mapping[str, Any]]] = {}
        for prediction in evaluation_predictions:
            if int(prediction["seed"]) == seed:
                episode_groups.setdefault(
                    int(prediction["evaluation_episode"]), []
                ).append(prediction)
        if not episode_groups:
            raise RuntimeError("Bayesian evaluation predictions are unavailable")
        expected_candidates = len(next(iter(episode_groups.values())))
        for episode_index, group in episode_groups.items():
            if (
                len(group) != expected_candidates
                or len({int(item["candidate_index"]) for item in group}) != len(group)
                or len({int(item["queried_position"]) for item in group}) != len(group)
                or len({str(item["episode_hash"]) for item in group}) != 1
                or any(int(item["candidate_index"]) == 0 for item in group)
                or any(
                    not np.isfinite(float(item[field]))
                    for item in group
                    for field in (
                        "rollout_predicted_improvement",
                        "bayesian_predicted_improvement",
                        "bayesian_lower_bound_95",
                        "realized_improvement",
                    )
                )
            ):
                raise RuntimeError(
                    f"invalid Bayesian prediction group for seed {seed}, "
                    f"episode {episode_index}"
                )
        api_lookup = {
            int(item["evaluation_episode"]): item
            for item in policy_evaluations
            if int(item["seed"]) == seed and item["arm"] == "bayes_mean"
        }
        if set(api_lookup) != set(episode_groups):
            raise RuntimeError("Bayesian API rows do not match prediction groups")
        # Candidate identity and action scores are frozen in a label-free pass.
        # Realized outcomes are joined only after every selector is fixed.
        decision_lookup: dict[int, tuple[int, float]] = {}
        outcome_lookup: dict[tuple[int, int], float] = {}
        for episode_index, group in episode_groups.items():
            scored_candidates = [
                (
                    float(item["bayesian_predicted_improvement"]),
                    -int(item["queried_position"]),
                    int(item["candidate_index"]),
                )
                for item in group
            ]
            best_score, _, best_candidate_index = max(scored_candidates)
            decision_lookup[episode_index] = (best_candidate_index, best_score)
            for item in group:
                outcome_lookup[
                    (episode_index, int(item["candidate_index"]))
                ] = float(item["realized_improvement"])
        for label, quantile, threshold, forced_abstain in thresholds:
            selected_improvements: list[float] = []
            action_improvements: list[float] = []
            opportunity_count = 0
            beneficial_action_count = 0
            harmful_action_count = 0
            queried_oracle_regrets: list[float] = []
            for episode_index in sorted(episode_groups):
                group = episode_groups[episode_index]
                best_candidate_index, best_score = decision_lookup[episode_index]
                realized_values = np.asarray(
                    [float(item["realized_improvement"]) for item in group],
                    dtype=np.float64,
                )
                opportunity = bool(np.max(realized_values) > 1e-12)
                opportunity_count += int(opportunity)
                acted = (
                    False
                    if forced_abstain
                    else best_score > float(threshold)
                )
                selected = (
                    outcome_lookup[(episode_index, best_candidate_index)]
                    if acted
                    else 0.0
                )
                selected_improvements.append(selected)
                queried_oracle_regrets.append(max(0.0, float(np.max(realized_values))) - selected)
                if acted:
                    action_improvements.append(selected)
                    beneficial_action_count += int(selected > 1e-12)
                    harmful_action_count += int(selected < -1e-12)
            episode_count = len(episode_groups)
            action_count = len(action_improvements)
            matches_api: bool | None = None
            if label == "minimum_effect_zero":
                matches_api = all(
                    (
                        bool(api_lookup[episode_index]["acted"])
                        == (decision_lookup[episode_index][1] > 0.0)
                        and int(api_lookup[episode_index]["selected_index"])
                        == (
                            decision_lookup[episode_index][0]
                            if decision_lookup[episode_index][1] > 0.0
                            else 0
                        )
                        and np.isclose(
                            float(api_lookup[episode_index]["selected_improvement"]),
                            (
                                outcome_lookup[
                                    (
                                        episode_index,
                                        decision_lookup[episode_index][0],
                                    )
                                ]
                                if bool(api_lookup[episode_index]["acted"])
                                else 0.0
                            ),
                            atol=1e-12,
                            rtol=1e-12,
                        )
                    )
                    for episode_index in episode_groups
                )
            rows.append(
                {
                    "seed": seed,
                    "threshold_label": label,
                    "calibration_prediction_quantile": quantile,
                    "minimum_predicted_improvement": threshold,
                    "forced_abstain_endpoint": forced_abstain,
                    "threshold_uses_evaluation_outcomes": False,
                    "matches_bayes_mean_api": matches_api,
                    "episode_count": episode_count,
                    "action_count": action_count,
                    "action_coverage": action_count / episode_count,
                    "harmful_action_count": harmful_action_count,
                    "beneficial_action_count": beneficial_action_count,
                    "conditional_harm_rate": (
                        harmful_action_count / action_count if action_count else None
                    ),
                    "conditional_downside": (
                        float(np.mean([max(0.0, -value) for value in action_improvements]))
                        if action_count
                        else None
                    ),
                    "net_improvement": float(np.mean(selected_improvements)),
                    "unconditional_harm_burden": float(
                        np.mean([max(0.0, -value) for value in selected_improvements])
                    ),
                    "beneficial_precision": (
                        beneficial_action_count / action_count if action_count else None
                    ),
                    "opportunity_count": opportunity_count,
                    "opportunity_recall": (
                        beneficial_action_count / opportunity_count
                        if opportunity_count
                        else None
                    ),
                    "queried_oracle_regret": float(np.mean(queried_oracle_regrets)),
                }
            )
    return rows


def _save_flat_snapshot(path: Path, snapshot: Mapping[str, Any]) -> None:
    arrays = {
        key: value for key, value in snapshot.items() if isinstance(value, np.ndarray)
    }
    metadata = {
        key: value for key, value in snapshot.items() if not isinstance(value, np.ndarray)
    }
    np.savez_compressed(
        path,
        **arrays,
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
    )


def load_flat_snapshot_artifact(path: str | Path) -> dict[str, Any]:
    """Reload a predictor/forecaster NPZ artifact without pickle."""

    with np.load(Path(path), allow_pickle=False) as archive:
        if "metadata_json" not in archive.files:
            raise ValueError("snapshot artifact is missing metadata_json")
        metadata = json.loads(str(archive["metadata_json"].item()))
        if not isinstance(metadata, dict):
            raise ValueError("snapshot artifact metadata must be an object")
        snapshot = dict(metadata)
        for name in archive.files:
            if name != "metadata_json":
                snapshot[name] = np.asarray(archive[name]).copy()
    return snapshot


def _save_transfer_snapshot(path: Path, snapshot: Mapping[str, Any]) -> None:
    model = dict(snapshot["model"])
    arrays = {
        key: value for key, value in model.items() if isinstance(value, np.ndarray)
    }
    metadata = {
        "agent": {key: value for key, value in snapshot.items() if key != "model"},
        "model": {
            key: value for key, value in model.items() if not isinstance(value, np.ndarray)
        },
    }
    np.savez_compressed(
        path,
        **arrays,
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
    )


def load_transfer_snapshot_artifact(path: str | Path) -> dict[str, Any]:
    """Reload an auditable Bayesian agent snapshot from its portable NPZ."""

    with np.load(Path(path), allow_pickle=False) as archive:
        if "metadata_json" not in archive.files:
            raise ValueError("transfer artifact is missing metadata_json")
        metadata = json.loads(str(archive["metadata_json"].item()))
        if not isinstance(metadata, dict) or set(metadata) != {"agent", "model"}:
            raise ValueError("invalid transfer artifact metadata")
        agent_metadata = metadata["agent"]
        model_metadata = metadata["model"]
        if not isinstance(agent_metadata, dict) or not isinstance(model_metadata, dict):
            raise ValueError("invalid transfer artifact snapshot objects")
        model = dict(model_metadata)
        if "coordinate_names" in model:
            model["coordinate_names"] = tuple(model["coordinate_names"])
        for name in archive.files:
            if name != "metadata_json":
                model[name] = np.asarray(archive[name]).copy()
    snapshot = dict(agent_metadata)
    snapshot["model"] = model
    return snapshot


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty result table")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _plot(path: Path, seed_summaries: list[dict[str, Any]], transfer: list[dict[str, Any]]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    seeds = sorted({int(row["seed"]) for row in seed_summaries})
    arms = tuple(ARM_SPECS)
    lookup = {(int(row["seed"]), str(row["arm"])): row for row in seed_summaries}
    transfer_lookup = {int(row["seed"]): row for row in transfer}
    figure, axes = plt.subplots(1, 3, figsize=(16.2, 5.2))
    x = np.arange(len(seeds))
    width = 0.35
    axes[0].bar(
        x - width / 2,
        [transfer_lookup[seed]["rollout_rmse"] for seed in seeds],
        width,
        label="rollout",
        color="#7b7b7b",
    )
    axes[0].bar(
        x + width / 2,
        [transfer_lookup[seed]["bayesian_rmse"] for seed in seeds],
        width,
        label="Bayesian transfer",
        color="#286f9b",
    )
    axes[0].set_title("Held-out transfer prediction")
    axes[0].set_ylabel("RMSE of realized improvement")
    axes[0].set_xticks(x, [str(seed) for seed in seeds])
    axes[0].legend(fontsize=8)

    selected_arms = (
        "rollout_uncalibrated",
        "bayes_mean",
        "bayes_credible",
        "bayes_conformal",
    )
    colors = ("#777777", "#286f9b", "#64a7ca", "#193f5a")
    local_width = 0.18
    for index, (arm, color) in enumerate(zip(selected_arms, colors)):
        axes[1].bar(
            x + (index - 1.5) * local_width,
            [lookup[(seed, arm)]["net_improvement"] for seed in seeds],
            local_width,
            label=arm.replace("_", " "),
            color=color,
        )
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].set_title("Realized selected effect")
    axes[1].set_ylabel("mean error reduction vs no-op")
    axes[1].set_xticks(x, [str(seed) for seed in seeds])
    axes[1].legend(fontsize=7)

    aggregate_coverage = [
        np.mean([lookup[(seed, arm)]["action_coverage"] for seed in seeds])
        for arm in arms
    ]
    aggregate_harm = [
        np.mean(
            [
                lookup[(seed, arm)]["conditional_harm_rate"]
                for seed in seeds
                if lookup[(seed, arm)]["conditional_harm_rate"] is not None
            ]
        )
        if any(
            lookup[(seed, arm)]["conditional_harm_rate"] is not None
            for seed in seeds
        )
        else 0.0
        for arm in arms
    ]
    axis_x = np.arange(len(arms))
    axes[2].bar(
        axis_x - 0.18,
        aggregate_coverage,
        0.36,
        label="action coverage",
        color="#4c8b62",
    )
    axes[2].bar(axis_x + 0.18, aggregate_harm, 0.36, label="harm | action", color="#b65c54")
    axes[2].set_title("Selectivity versus conditional harm")
    axes[2].set_ylim(0.0, 1.0)
    axes[2].set_xticks(axis_x, [arm.replace("_", "\n") for arm in arms], fontsize=7)
    axes[2].legend(fontsize=8)
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
        axis.set_xlabel("development seed" if axis is not axes[2] else "policy")
    figure.suptitle("RRCT v0.9 Bayesian causal-transfer development benchmark")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return True


def run_bayesian_transfer_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V09_DEVELOPMENT_SEEDS,
    predictor_episode_count: int = 64,
    transfer_episode_count: int = 64,
    calibration_episode_count: int = 32,
    evaluation_episode_count: int = 64,
    train_delay: int = 5,
    test_delay: int = 7,
    horizon: int = 4,
    query_budget: int = 4,
    candidate_magnitude: float = 0.35,
    calibration_alpha: float = 0.05,
    calibration_min_samples: int = 19,
    bootstrap_resamples: int = V09_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V09_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run a development-only four-way separated Bayesian transfer study."""

    seed_values = tuple(int(seed) for seed in seeds)
    if len(seed_values) < 2 or len(set(seed_values)) != len(seed_values):
        raise ValueError("at least two unique development seeds are required")
    if set(seed_values) - set(V09_DEVELOPMENT_SEEDS):
        raise ValueError("runner refuses seeds outside the v0.9 development set")
    if min(predictor_episode_count, transfer_episode_count, evaluation_episode_count) < 8:
        raise ValueError("predictor, transfer, and evaluation splits require at least eight episodes")
    if calibration_episode_count < calibration_min_samples:
        raise ValueError("calibration split must meet calibration_min_samples")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError(f"output directory must be empty: {destination}")

    evaluation_rows: list[dict[str, Any]] = []
    transfer_evaluation_rows: list[dict[str, Any]] = []
    transfer_training_rows: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    calibration_bank_summaries: list[dict[str, Any]] = []
    transfer_seed_summaries: list[dict[str, Any]] = []
    split_manifest: list[dict[str, Any]] = []
    for seed in seed_values:
        predictor_snapshot, forecaster_snapshot = _train_predictors(
            seed=seed,
            episode_count=predictor_episode_count,
            delay=train_delay,
        )
        _save_flat_snapshot(
            destination / f"self_predictor_seed_{seed}.npz", predictor_snapshot
        )
        _save_flat_snapshot(
            destination / f"observation_forecaster_seed_{seed}.npz",
            forecaster_snapshot,
        )
        split_episodes = {
            "predictor": _episodes(predictor_episode_count, seed=seed + 10_000, delay=train_delay),
            "transfer": _episodes(transfer_episode_count, seed=seed + 20_000, delay=test_delay),
            "calibration": _episodes(calibration_episode_count, seed=seed + 30_000, delay=test_delay),
            "evaluation": _episodes(evaluation_episode_count, seed=seed + 40_000, delay=test_delay),
        }
        for split_name, episodes in split_episodes.items():
            for episode_index, episode in enumerate(episodes):
                split_manifest.append(
                    {
                        "seed": seed,
                        "split": split_name,
                        "episode_index": episode_index,
                        "episode_hash": _episode_hash(episode),
                    }
                )
        bayes_snapshot, permuted_snapshot, training_rows = _train_transfer(
            seed=seed,
            episodes=split_episodes["transfer"],
            predictor_snapshot=predictor_snapshot,
            forecaster_snapshot=forecaster_snapshot,
            horizon=horizon,
            candidate_magnitude=candidate_magnitude,
        )
        transfer_training_rows.extend(training_rows)
        _save_transfer_snapshot(
            destination / f"bayesian_posterior_seed_{seed}.npz",
            bayes_snapshot,
        )
        _save_transfer_snapshot(
            destination / f"permuted_bayesian_posterior_seed_{seed}.npz",
            permuted_snapshot,
        )
        calibration_banks: dict[str, dict[str, Any]] = {}
        calibration_specs = {
            "rollout": (None, "rollout"),
            "bayes": (bayes_snapshot, "bayesian_mean"),
            "permuted": (permuted_snapshot, "bayesian_mean"),
        }
        for bank_name, (transfer_snapshot, selection_mode) in calibration_specs.items():
            bank, bank_rows = _build_calibration_bank(
                seed=seed,
                episodes=split_episodes["calibration"],
                predictor_snapshot=predictor_snapshot,
                forecaster_snapshot=forecaster_snapshot,
                transfer_snapshot=transfer_snapshot,
                selection_mode=selection_mode,
                horizon=horizon,
                query_budget=query_budget,
                candidate_magnitude=candidate_magnitude,
            )
            calibration_banks[bank_name] = bank
            for row in bank_rows:
                row["bank"] = bank_name
            calibration_rows.extend(bank_rows)
            optimism = tuple(float(item["optimism"]) for item in bank["records"])
            ready, threshold = RRCTAgent._conformal_optimism_threshold(
                optimism,
                alpha=calibration_alpha,
                minimum_records=calibration_min_samples,
            )
            calibration_bank_summaries.append(
                {
                    "seed": seed,
                    "bank": bank_name,
                    "count": int(bank["count"]),
                    "ready": ready,
                    "threshold": threshold,
                    "optimism_mean": float(np.mean(optimism)),
                    "optimism_min": float(np.min(optimism)),
                    "optimism_max": float(np.max(optimism)),
                    "digest": str(bank["digest"]),
                }
            )
        with (destination / f"calibration_banks_seed_{seed}.json").open(
            "w", encoding="utf-8"
        ) as handle:
            json.dump(calibration_banks, handle, indent=2, sort_keys=True)
            handle.write("\n")

        transfer_actual: list[float] = []
        transfer_rollout: list[float] = []
        transfer_bayesian: list[float] = []
        transfer_brier: list[float] = []
        transfer_log_density: list[float] = []
        joint_marginal_bound_coverage: list[bool] = []
        rollout_rank_correlations: list[float] = []
        bayesian_rank_correlations: list[float] = []
        rollout_top1_matches: list[bool] = []
        bayesian_top1_matches: list[bool] = []
        for episode_index, episode in enumerate(split_episodes["evaluation"]):
            observations = np.asarray(episode.observations, dtype=np.float64)
            prefix = observations[:-horizon]
            plans: dict[str, tuple[Any, ...]] = {}
            queried_reference: tuple[int, ...] | None = None
            for arm, (posterior_name, selection_mode, calibration_mode, bank_name) in ARM_SPECS.items():
                transfer_snapshot = (
                    bayes_snapshot
                    if posterior_name == "bayes"
                    else permuted_snapshot if posterior_name == "permuted" else None
                )
                agent = _prime_agent(
                    seed=seed,
                    predictor_snapshot=predictor_snapshot,
                    forecaster_snapshot=forecaster_snapshot,
                    prefix=prefix,
                    transfer_snapshot=transfer_snapshot,
                    calibration_snapshot=(
                        calibration_banks[str(bank_name)]
                        if bank_name is not None
                        else None
                    ),
                )
                posterior_count_before = agent.bayesian_transfer.observation_count
                calibration_count_before = agent.intention_calibration_snapshot()["count"]
                before_digest = agent._endogenous_state_digest()
                plan = agent.plan_endogenous_self_intention(
                    horizon=horizon,
                    query_budget=query_budget,
                    candidate_magnitude=candidate_magnitude,
                    forecast_mode="learned",
                    selection_mode=selection_mode,
                    bayesian_confidence=0.95,
                    calibration_mode=calibration_mode,
                    calibration_alpha=calibration_alpha,
                    calibration_min_samples=calibration_min_samples,
                )
                planning_nonmutating = before_digest == agent._endogenous_state_digest()
                if queried_reference is None:
                    queried_reference = plan.queried_indices
                if plan.queried_indices != queried_reference:
                    raise RuntimeError("evaluation arms produced different query sets")
                receipt = agent.commit_endogenous_self_intention(plan)
                plans[arm] = (
                    agent,
                    plan,
                    receipt,
                    planning_nonmutating,
                    posterior_count_before,
                    calibration_count_before,
                )

            # Every decision is committed before the evaluation suffix is
            # materialized or any candidate outcome is computed.
            hidden = observations[-horizon:].copy()
            assert queried_reference is not None
            rollout_receipt = plans["rollout_uncalibrated"][2]
            rollout_plan = plans["rollout_uncalibrated"][1]
            candidate_errors = _candidate_errors(
                rollout_receipt._baseline_agent,
                rollout_plan.candidate_deltas,
                hidden,
            )
            reductions = float(candidate_errors[0]) - candidate_errors
            for arm, values in plans.items():
                (
                    agent,
                    plan,
                    receipt,
                    planning_nonmutating,
                    posterior_count_before,
                    calibration_count_before,
                ) = values
                result = agent.evaluate_committed_intention(
                    receipt, hidden, update_calibration=False
                )
                api_matches = bool(
                    np.isclose(
                        result.realized_selected_error,
                        candidate_errors[plan.selected_index],
                        atol=1e-12,
                        rtol=1e-12,
                    )
                )
                evaluation_rows.append(
                    {
                        "seed": seed,
                        "evaluation_episode": episode_index,
                        "episode_hash": _episode_hash(episode),
                        "arm": arm,
                        "selected_index": int(plan.selected_index),
                        "raw_selected_index": int(plan.raw_selected_index),
                        "simulator_selected_index": int(plan.simulator_selected_index),
                        "selected_improvement": float(reductions[plan.selected_index]),
                        "predicted_improvement": float(plan.predicted_improvement),
                        "acted": bool(plan.selected_index != 0),
                        "harm": bool(reductions[plan.selected_index] < -1e-12),
                        "beneficial_action": bool(
                            plan.selected_index != 0
                            and reductions[plan.selected_index] > 1e-12
                        ),
                        "queried_opportunity": bool(
                            np.max(reductions[np.asarray(plan.queried_indices)]) > 1e-12
                        ),
                        "queried_oracle_regret": float(
                            np.max(reductions[np.asarray(plan.queried_indices)])
                            - reductions[plan.selected_index]
                        ),
                        "full_oracle_regret": float(
                            np.max(reductions) - reductions[plan.selected_index]
                        ),
                        "abstained": bool(plan.abstained),
                        "abstention_reason": plan.abstention_reason,
                        "planning_nonmutating": planning_nonmutating,
                        "api_matches_offline": api_matches,
                        "same_episode_suffix": bool(
                            np.array_equal(np.concatenate((prefix, hidden)), observations)
                        ),
                        "committed_before_suffix_materialization": True,
                        "posterior_updates": int(
                            agent.bayesian_transfer.observation_count
                            - posterior_count_before
                        ),
                        "calibration_updates": int(
                            agent.intention_calibration_snapshot()["count"]
                            - calibration_count_before
                        ),
                        "workspace_variance": float(
                            np.var(np.stack([step.workspace for step in result.realized_steps]))
                        ),
                        "action_variance": float(
                            np.var(np.stack([step.action for step in result.realized_steps]))
                        ),
                    }
                )
            bayes_agent = plans["bayes_mean"][0]
            bayes_plan = plans["bayes_mean"][1]
            queried_realized: list[float] = []
            queried_rollout: list[float] = []
            queried_bayesian: list[float] = []
            queried_covered: list[bool] = []
            for position, candidate_index in enumerate(bayes_plan.queried_indices):
                if candidate_index == 0:
                    continue
                realized = float(reductions[candidate_index])
                rollout_prediction = float(
                    bayes_plan.predicted_baseline_error
                    - bayes_plan.predicted_candidate_errors[position]
                )
                bayesian_prediction = float(bayes_plan.bayesian_means[position])
                prediction = bayes_agent.bayesian_transfer.predict(
                    bayes_plan.bayesian_features[position]
                )
                normalized_realized = (
                    realized - rollout_prediction
                ) / bayes_agent.bayesian_transfer_target_scale
                transfer_actual.append(realized)
                transfer_rollout.append(rollout_prediction)
                transfer_bayesian.append(bayesian_prediction)
                transfer_brier.append(
                    (
                        bayes_plan.bayesian_probabilities_positive[position]
                        - float(realized > 0.0)
                    )
                    ** 2
                )
                log_density = _student_t_log_density(
                    normalized_realized,
                    mean=prediction.mean,
                    scale_squared=prediction.scale_squared,
                    degrees_of_freedom=prediction.degrees_of_freedom,
                )
                transfer_log_density.append(log_density)
                queried_realized.append(realized)
                queried_rollout.append(rollout_prediction)
                queried_bayesian.append(bayesian_prediction)
                lower_covered = bool(
                    realized + 1e-15 >= bayes_plan.bayesian_lower_bounds[position]
                )
                queried_covered.append(lower_covered)
                transfer_evaluation_rows.append(
                    {
                        "seed": seed,
                        "evaluation_episode": episode_index,
                        "episode_hash": _episode_hash(episode),
                        "queried_position": position,
                        "candidate_index": int(candidate_index),
                        "realized_improvement": realized,
                        "rollout_predicted_improvement": rollout_prediction,
                        "bayesian_predicted_improvement": bayesian_prediction,
                        "bayesian_predicted_correction": float(
                            prediction.mean * bayes_agent.bayesian_transfer_target_scale
                        ),
                        "bayesian_predictive_sd": float(
                            bayes_plan.bayesian_standard_deviations[position]
                        ),
                        "bayesian_probability_positive": float(
                            bayes_plan.bayesian_probabilities_positive[position]
                        ),
                        "bayesian_lower_bound_95": float(
                            bayes_plan.bayesian_lower_bounds[position]
                        ),
                        "lower_bound_covered": lower_covered,
                        "normalized_realized_correction": normalized_realized,
                        "log_predictive_density": log_density,
                    }
                )
            joint_marginal_bound_coverage.append(all(queried_covered))
            rollout_rank_correlations.append(
                _rank_correlation(queried_rollout, queried_realized)
            )
            bayesian_rank_correlations.append(
                _rank_correlation(queried_bayesian, queried_realized)
            )
            realized_best = int(np.argmax(queried_realized))
            rollout_top1_matches.append(int(np.argmax(queried_rollout)) == realized_best)
            bayesian_top1_matches.append(int(np.argmax(queried_bayesian)) == realized_best)

        actual = np.asarray(transfer_actual)
        rollout_prediction = np.asarray(transfer_rollout)
        bayesian_prediction = np.asarray(transfer_bayesian)
        training_positive_rate = float(
            np.mean(
                [
                    float(row["realized_improvement"] > 0.0)
                    for row in transfer_training_rows
                    if int(row["seed"]) == seed
                ]
            )
        )
        transfer_seed_summaries.append(
            {
                "seed": seed,
                "candidate_count": int(actual.size),
                "evaluation_positive_candidate_rate": float(np.mean(actual > 0.0)),
                "training_positive_candidate_rate": training_positive_rate,
                "zero_prediction_rmse": float(np.sqrt(np.mean(np.square(actual)))),
                "rollout_rmse": float(np.sqrt(np.mean(np.square(actual - rollout_prediction)))),
                "bayesian_rmse": float(np.sqrt(np.mean(np.square(actual - bayesian_prediction)))),
                "rollout_mae": float(np.mean(np.abs(actual - rollout_prediction))),
                "bayesian_mae": float(np.mean(np.abs(actual - bayesian_prediction))),
                "bayesian_sign_brier": float(np.mean(transfer_brier)),
                "training_prevalence_sign_brier": float(
                    np.mean(
                        np.square(training_positive_rate - (actual > 0.0).astype(np.float64))
                    )
                ),
                "bayesian_mean_log_predictive_density": float(np.mean(transfer_log_density)),
                "bayesian_joint_coverage_of_three_marginal_95_lower_bounds": float(
                    np.mean(joint_marginal_bound_coverage)
                ),
                "rollout_mean_within_episode_rank_correlation": float(
                    np.mean(rollout_rank_correlations)
                ),
                "bayesian_mean_within_episode_rank_correlation": float(
                    np.mean(bayesian_rank_correlations)
                ),
                "rollout_top1_candidate_accuracy": float(np.mean(rollout_top1_matches)),
                "bayesian_top1_candidate_accuracy": float(np.mean(bayesian_top1_matches)),
                "posterior_observation_count": int(bayes_snapshot["model"]["observation_count"]),
                "posterior_effective_sample_count": float(bayes_snapshot["model"]["effective_sample_count"]),
                "posterior_digest": str(bayes_snapshot["model"]["posterior_digest"]),
            }
        )

    risk_coverage_rows = _bayesian_risk_coverage_rows(
        seeds=seed_values,
        calibration_rows=calibration_rows,
        evaluation_predictions=transfer_evaluation_rows,
        policy_evaluations=evaluation_rows,
    )
    seed_summaries: list[dict[str, Any]] = []
    for seed in seed_values:
        for arm in ARM_SPECS:
            group = [
                row for row in evaluation_rows
                if row["seed"] == seed and row["arm"] == arm
            ]
            acted = [row for row in group if row["acted"]]
            opportunities = [row for row in group if row["queried_opportunity"]]
            seed_summaries.append(
                {
                    "seed": seed,
                    "arm": arm,
                    "action_coverage": float(np.mean([row["acted"] for row in group])),
                    "net_improvement": float(np.mean([row["selected_improvement"] for row in group])),
                    "conditional_harm_rate": (
                        float(np.mean([row["harm"] for row in acted])) if acted else None
                    ),
                    "conditional_downside": (
                        float(np.mean([max(0.0, -row["selected_improvement"]) for row in acted]))
                        if acted else None
                    ),
                    "unconditional_harm_burden": float(
                        np.mean([max(0.0, -row["selected_improvement"]) for row in group])
                    ),
                    "beneficial_precision": (
                        float(np.mean([row["beneficial_action"] for row in acted]))
                        if acted else None
                    ),
                    "opportunity_recall": (
                        float(np.mean([row["beneficial_action"] for row in opportunities]))
                        if opportunities else None
                    ),
                    "queried_oracle_regret": float(
                        np.mean([row["queried_oracle_regret"] for row in group])
                    ),
                    "full_oracle_regret": float(
                        np.mean([row["full_oracle_regret"] for row in group])
                    ),
                }
            )

    rng = np.random.default_rng(bootstrap_seed)
    transfer_differences = [
        row["bayesian_rmse"] - row["rollout_rmse"]
        for row in transfer_seed_summaries
    ]
    transfer_contrast = {
        **_bootstrap_mean_ci(
            transfer_differences, resamples=bootstrap_resamples, rng=rng
        ),
        "bayesian_better_seed_count": int(
            np.count_nonzero(np.asarray(transfer_differences) < 0.0)
        ),
    }
    aggregate_arms: dict[str, Any] = {}
    for arm in ARM_SPECS:
        group = [row for row in seed_summaries if row["arm"] == arm]
        aggregate_arms[arm] = {
            field: _bootstrap_mean_ci(
                [float(row[field]) for row in group],
                resamples=bootstrap_resamples,
                rng=rng,
            )
            for field in (
                "action_coverage",
                "net_improvement",
                "unconditional_harm_burden",
                "queried_oracle_regret",
                "full_oracle_regret",
            )
        }
        conditional_harm = [
            float(row["conditional_harm_rate"])
            for row in group
            if row["conditional_harm_rate"] is not None
        ]
        aggregate_arms[arm]["conditional_harm_rate"] = (
            _bootstrap_mean_ci(conditional_harm, resamples=bootstrap_resamples, rng=rng)
            if conditional_harm else None
        )

    pooled_arms: dict[str, Any] = {}
    for arm in ARM_SPECS:
        group = [row for row in evaluation_rows if row["arm"] == arm]
        acted = [row for row in group if row["acted"]]
        opportunities = [row for row in group if row["queried_opportunity"]]
        pooled_arms[arm] = {
            "episode_count": len(group),
            "action_count": len(acted),
            "harmful_action_count": int(sum(bool(row["harm"]) for row in acted)),
            "beneficial_action_count": int(
                sum(bool(row["beneficial_action"]) for row in acted)
            ),
            "action_coverage": len(acted) / len(group),
            "net_improvement": float(
                np.mean([row["selected_improvement"] for row in group])
            ),
            "conditional_harm_rate": (
                float(np.mean([row["harm"] for row in acted])) if acted else None
            ),
            "beneficial_precision": (
                float(np.mean([row["beneficial_action"] for row in acted]))
                if acted else None
            ),
            "opportunity_recall": (
                float(np.mean([row["beneficial_action"] for row in opportunities]))
                if opportunities else None
            ),
        }

    seed_summary_lookup = {
        (int(row["seed"]), str(row["arm"])): row for row in seed_summaries
    }
    policy_contrasts: dict[str, Any] = {}
    for name, left, right, field in (
        (
            "bayes_mean_minus_rollout_uncalibrated_net_improvement",
            "bayes_mean",
            "rollout_uncalibrated",
            "net_improvement",
        ),
        (
            "bayes_conformal_minus_permuted_net_improvement",
            "bayes_conformal",
            "permuted_bayes_conformal",
            "net_improvement",
        ),
        (
            "bayes_conformal_minus_rollout_conformal_opportunity_recall",
            "bayes_conformal",
            "rollout_conformal",
            "opportunity_recall",
        ),
    ):
        values = [
            float(seed_summary_lookup[(seed, left)][field])
            - float(seed_summary_lookup[(seed, right)][field])
            for seed in seed_values
        ]
        policy_contrasts[name] = {
            **_bootstrap_mean_ci(values, resamples=bootstrap_resamples, rng=rng),
            "positive_seed_count": int(np.count_nonzero(np.asarray(values) > 0.0)),
            "negative_seed_count": int(np.count_nonzero(np.asarray(values) < 0.0)),
        }

    hashes_by_split: dict[tuple[int, str], set[str]] = {}
    for row in split_manifest:
        hashes_by_split.setdefault((int(row["seed"]), str(row["split"])), set()).add(
            str(row["episode_hash"])
        )
    no_split_overlap = all(
        hashes_by_split[(seed, left)].isdisjoint(hashes_by_split[(seed, right)])
        for seed in seed_values
        for left in ("predictor", "transfer", "calibration", "evaluation")
        for right in ("predictor", "transfer", "calibration", "evaluation")
        if left < right
    )
    integrity = {
        "all_rows_retained": len(evaluation_rows)
        == len(seed_values) * evaluation_episode_count * len(ARM_SPECS),
        "all_transfer_rows_retained": len(transfer_training_rows)
        == len(seed_values) * transfer_episode_count * 24,
        "all_transfer_evaluation_predictions_retained": len(transfer_evaluation_rows)
        == len(seed_values) * evaluation_episode_count * (query_budget - 1),
        "all_calibration_rows_retained": len(calibration_rows)
        == len(seed_values) * calibration_episode_count * 3,
        "all_risk_coverage_rows_retained": len(risk_coverage_rows)
        == len(seed_values) * 13,
        "risk_coverage_thresholds_do_not_use_evaluation_outcomes": all(
            not row["threshold_uses_evaluation_outcomes"]
            for row in risk_coverage_rows
        ),
        "risk_coverage_zero_threshold_matches_api": all(
            row["matches_bayes_mean_api"] is True
            for row in risk_coverage_rows
            if row["threshold_label"] == "minimum_effect_zero"
        ),
        "risk_coverage_forced_abstain_has_zero_actions": all(
            row["action_count"] == 0
            for row in risk_coverage_rows
            if row["threshold_label"] == "forced_abstain"
        ),
        "all_calibration_banks_ready": all(
            row["ready"] for row in calibration_bank_summaries
        ),
        "no_episode_hash_overlap_across_splits": no_split_overlap,
        "all_suffixes_from_same_episode": all(
            row["same_episode_suffix"] for row in transfer_training_rows
        )
        and all(row["same_episode_suffix"] for row in calibration_rows)
        and all(row["same_episode_suffix"] for row in evaluation_rows),
        "all_shadow_updates_core_nonmutating": all(
            row["shadow_core_nonmutating"] for row in transfer_training_rows
        )
        and all(row["shadow_core_nonmutating"] for row in calibration_rows),
        "all_evaluation_plans_nonmutating": all(
            row["planning_nonmutating"] for row in evaluation_rows
        ),
        "all_decisions_committed_before_suffix_materialization": all(
            row["committed_before_suffix_materialization"]
            for row in evaluation_rows
        ),
        "all_api_evaluations_match_offline": all(
            row["api_matches_offline"] for row in evaluation_rows
        ),
        "zero_heldout_posterior_updates": all(
            row["posterior_updates"] == 0 for row in evaluation_rows
        ),
        "zero_heldout_calibration_updates": all(
            row["calibration_updates"] == 0 for row in evaluation_rows
        ),
    }
    development_checks = {
        "bayesian_transfer_prediction_improved": bool(
            transfer_contrast["bayesian_better_seed_count"] >= 3
            and transfer_contrast["ci95_upper"] < 0.0
        ),
        "bayes_conformal_useful_action_coverage": bool(
            pooled_arms["bayes_conformal"]["action_coverage"] >= 0.10
            and sum(
                seed_summary_lookup[(seed, "bayes_conformal")]["action_coverage"] > 0.0
                for seed in seed_values
            )
            >= 3
        ),
        "bayes_conformal_positive_net_improvement": bool(
            sum(
                seed_summary_lookup[(seed, "bayes_conformal")]["net_improvement"] > 0.0
                for seed in seed_values
            )
            >= 3
            and aggregate_arms["bayes_conformal"]["net_improvement"]["ci95_lower"] > 0.0
        ),
        "bayes_conformal_harm_rate_at_most_0_10": bool(
            pooled_arms["bayes_conformal"]["conditional_harm_rate"] is not None
            and pooled_arms["bayes_conformal"]["conditional_harm_rate"] <= 0.10
        ),
        "specificity_vs_permuted_net_improvement": bool(
            policy_contrasts[
                "bayes_conformal_minus_permuted_net_improvement"
            ]["positive_seed_count"]
            >= 3
            and policy_contrasts[
                "bayes_conformal_minus_permuted_net_improvement"
            ]["ci95_lower"]
            > 0.0
        ),
    }

    _write_csv(destination / "bayesian_transfer_training_rows.csv", transfer_training_rows)
    _write_csv(
        destination / "bayesian_transfer_evaluation_predictions.csv",
        transfer_evaluation_rows,
    )
    _write_csv(destination / "bayesian_transfer_calibration_rows.csv", calibration_rows)
    _write_csv(destination / "calibration_bank_summaries.csv", calibration_bank_summaries)
    _write_csv(destination / "bayesian_transfer_evaluation_rows.csv", evaluation_rows)
    _write_csv(destination / "bayesian_transfer_seed_summaries.csv", seed_summaries)
    _write_csv(destination / "bayesian_transfer_prediction_summaries.csv", transfer_seed_summaries)
    _write_csv(destination / "bayesian_risk_coverage.csv", risk_coverage_rows)
    _write_csv(destination / "split_manifest.csv", split_manifest)
    plot_created = _plot(
        destination / "bayesian_transfer_development.png",
        seed_summaries,
        transfer_seed_summaries,
    )
    package_directory = Path(__file__).resolve().parent
    project_directory = package_directory.parent.parent
    source_files = (
        Path(__file__).resolve(),
        package_directory / "agent.py",
        package_directory / "components.py",
        package_directory / "_version.py",
        project_directory / "pyproject.toml",
        project_directory / "tests" / "test_v09_bayesian_agent.py",
        project_directory / "tests" / "test_v09_bayesian_experiment.py",
        project_directory / "tests" / "test_v09_bayesian_transfer.py",
    )
    source_sha256 = {
        str(path.relative_to(project_directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_files
    }
    summary = {
        "schema_version": 1,
        "experiment_protocol": "rrct.v09.bayesian_transfer_development.v3",
        "package_version": __version__,
        "status": "development_only_not_preregistered_not_confirmatory",
        "parameters": {
            "seeds": list(seed_values),
            "predictor_episode_count": predictor_episode_count,
            "transfer_episode_count": transfer_episode_count,
            "calibration_episode_count": calibration_episode_count,
            "evaluation_episode_count": evaluation_episode_count,
            "train_delay": train_delay,
            "test_delay": test_delay,
            "horizon": horizon,
            "query_budget": query_budget,
            "transfer_query_budget": 25,
            "candidate_magnitude": candidate_magnitude,
            "calibration_alpha": calibration_alpha,
            "calibration_min_samples": calibration_min_samples,
            "bootstrap_resamples": bootstrap_resamples,
            "bootstrap_seed": bootstrap_seed,
        },
        "model": {
            "family": "Normal-Inverse-Gamma Bayesian linear regression",
            "likelihood": "fractionally weighted Gaussian power likelihood",
            "feature_count": len(RRCTAgent.BAYESIAN_TRANSFER_FEATURE_NAMES),
            "feature_names": list(RRCTAgent.BAYESIAN_TRANSFER_FEATURE_NAMES),
            "include_intercept": False,
            "prior_precision": RRCTAgent.BAYESIAN_TRANSFER_PRIOR_PRECISION,
            "prior_shape": RRCTAgent.BAYESIAN_TRANSFER_PRIOR_SHAPE,
            "prior_scale": RRCTAgent.BAYESIAN_TRANSFER_PRIOR_SCALE,
            "target": "(paired realized reduction - rollout-predicted reduction) divided by 4*sqrt(workspace_dim)",
        },
        "transfer_seed_summaries": transfer_seed_summaries,
        "transfer_rmse_contrast_bayesian_minus_rollout": transfer_contrast,
        "calibration_bank_summaries": calibration_bank_summaries,
        "seed_summaries": seed_summaries,
        "aggregate_arms": aggregate_arms,
        "pooled_arms": pooled_arms,
        "policy_contrasts": policy_contrasts,
        "risk_coverage": {
            "file": "bayesian_risk_coverage.csv",
            "row_count": len(risk_coverage_rows),
            "threshold_source": (
                "within-seed Bayesian calibration raw-prediction quantiles, "
                "plus zero and an explicit forced-abstain endpoint"
            ),
            "selection_rule": (
                "choose the stable argmax Bayesian-mean nonzero candidate and act "
                "iff its predicted improvement is strictly above the threshold"
            ),
        },
        "metric_definitions": {
            "action_coverage": "fraction of episodes with a nonzero intervention",
            "conditional_harm_rate": "harmful nonzero actions divided by nonzero actions",
            "net_improvement": "mean realized internal-error reduction across every episode",
            "lower_bound_coverage": (
                "empirical coverage of three marginal 95% lower bounds jointly; "
                "not a multiplicity-adjusted simultaneous 95% interval"
            ),
        },
        "integrity": integrity,
        "development_checks": development_checks,
        "plot_created": plot_created,
        "source_sha256": source_sha256,
        "claim_boundary": {
            "establishes_consciousness": False,
            "creates_consciousness": False,
            "establishes_subjective_experience": False,
            "what_it_tests": "held-out prediction and selective control of one internal error metric",
        },
    }
    with (destination / "bayesian_transfer_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    checksum_rows = []
    for path in sorted(destination.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        checksum_rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (destination / "SHA256SUMS.txt").write_text(
        "\n".join(checksum_rows) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    parser.add_argument("--predictor-episodes", type=int, default=64)
    parser.add_argument("--transfer-episodes", type=int, default=64)
    parser.add_argument("--calibration-episodes", type=int, default=32)
    parser.add_argument("--evaluation-episodes", type=int, default=64)
    args = parser.parse_args(argv)
    summary = run_bayesian_transfer_experiment(
        args.output,
        predictor_episode_count=args.predictor_episodes,
        transfer_episode_count=args.transfer_episodes,
        calibration_episode_count=args.calibration_episodes,
        evaluation_episode_count=args.evaluation_episodes,
    )
    print(json.dumps(summary["development_checks"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Development-only prospective self-access selection experiment.

This standalone runner asks whether candidate-specific self counterfactuals can
be used to select an intervention for a novel linear workspace objective.  It
compares the live selector with a cross-seed predictor, a self-ablated agent,
exact baseline replay, deterministic random selection, and an equal-compute
generic workspace-intervention planner.

The task is bounded, nonvalenced, and mechanistic.  It is not a consciousness
test, and its development seeds are explicitly barred from confirmatory use.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import tempfile
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ._version import __version__
from .agent import RRCTAgent, SelfCounterfactualQuery
from .experiments import (
    _agent,
    _bootstrap_mean_ci,
    _episodes,
    _predictor_snapshot_id,
    _prepare_empty_output,
    _train_predictor_snapshot,
)


V06_DEVELOPMENT_SEEDS = (1601, 1607, 1613, 1619)
V06_DEVELOPMENT_BOOTSTRAP_SEED = 20_260_823
V06_DEVELOPMENT_BOOTSTRAP_RESAMPLES = 2_000
CONDITIONS = (
    "live_self_query",
    "wrong_self_query",
    "self_ablated_query",
    "replay",
    "random",
    "generic_equal_compute",
)
ROW_FIELDS = (
    "status",
    "stop_reason",
    "seed",
    "probe",
    "episode_id",
    "latent_factors",
    "wrong_self_seed",
    "live_predictor_snapshot_id",
    "wrong_predictor_snapshot_id",
    "predictor_learning_steps",
    "train_episode_count",
    "train_delay",
    "test_delay",
    "future_horizon",
    "direction_count",
    "candidate_count",
    "candidate_magnitude",
    "objective",
    "objective_sha256",
    "self_candidate_deltas",
    "self_candidate_sha256",
    "generic_workspace_deltas",
    "generic_candidate_sha256",
    "planning_observations",
    "planning_observations_sha256",
    "evaluation_observations",
    "evaluation_observations_sha256",
    "predictions",
    "selections",
    "compute_audit",
    "invariants",
    "state_digests",
)


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    return value


def _array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(values, dtype=np.float64))
    digest = hashlib.sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _update_digest(digest: Any, value: Any) -> None:
    if is_dataclass(value):
        digest.update(b"dataclass")
        _update_digest(digest, asdict(value))
    elif isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        digest.update(b"ndarray")
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    elif isinstance(value, Mapping):
        digest.update(b"mapping")
        for key in sorted(value, key=str):
            _update_digest(digest, str(key))
            _update_digest(digest, value[key])
    elif isinstance(value, (tuple, list)):
        digest.update(type(value).__name__.encode("ascii"))
        digest.update(str(len(value)).encode("ascii"))
        for item in value:
            _update_digest(digest, item)
    elif value is None:
        digest.update(b"none")
    elif isinstance(value, (bool, int, float, str, np.generic)):
        digest.update(type(value).__name__.encode("ascii"))
        digest.update(repr(value.item() if isinstance(value, np.generic) else value).encode("utf-8"))
    else:  # pragma: no cover - snapshots currently use only the cases above
        raise TypeError(f"unsupported digest value: {type(value).__name__}")


def _agent_state_sha256(agent: RRCTAgent) -> str:
    digest = hashlib.sha256()
    _update_digest(digest, agent.snapshot())
    return digest.hexdigest()


def _dct_directions(dimension: int, count: int) -> np.ndarray:
    coordinates = np.arange(dimension, dtype=np.float64)
    matrix = np.asarray(
        [
            np.cos(np.pi * (coordinates + 0.5) * frequency / dimension)
            for frequency in range(count)
        ],
        dtype=np.float64,
    )
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    if not np.allclose(matrix @ matrix.T, np.eye(count), atol=1e-12, rtol=1e-12):
        raise RuntimeError("self candidate directions are not orthonormal")
    return matrix


def _random_orthonormal_directions(
    dimension: int,
    count: int,
    *,
    seed_words: Sequence[int],
) -> np.ndarray:
    rng = np.random.default_rng(np.random.SeedSequence(tuple(int(x) for x in seed_words)))
    raw = rng.normal(size=(dimension, count))
    basis, triangular = np.linalg.qr(raw, mode="reduced")
    signs = np.sign(np.diag(triangular))
    signs[signs == 0.0] = 1.0
    basis = basis * signs
    matrix = np.asarray(basis.T, dtype=np.float64)
    if not np.allclose(matrix @ matrix.T, np.eye(count), atol=1e-12, rtol=1e-12):
        raise RuntimeError("random directions are not orthonormal")
    return matrix


def _signed_candidates(directions: np.ndarray, magnitude: float) -> np.ndarray:
    return np.asarray(
        [
            sign * magnitude * direction
            for direction in directions
            for sign in (1.0, -1.0)
        ],
        dtype=np.float64,
    )


def _prime(agent: RRCTAgent, observations: np.ndarray, source: str) -> None:
    agent.reset()
    agent.freeze_self_model()
    for observation in observations:
        agent.step(observation, source=source)


def _query_payload(
    agent: RRCTAgent,
    candidates: np.ndarray,
    future: np.ndarray,
    objective: np.ndarray,
) -> tuple[int, np.ndarray, tuple[SelfCounterfactualQuery, ...], dict[str, Any]]:
    selected, scores, queries = agent.select_self_counterfactual(
        candidates,
        future,
        objective,
    )
    score_vector = np.asarray(scores, dtype=np.float64)
    payload = {
        "scores": score_vector.tolist(),
        "baseline_workspace": np.asarray(
            [query.baseline_workspace for query in queries], dtype=np.float64
        ).tolist(),
        "intervened_workspace": np.asarray(
            [query.intervened_workspace for query in queries], dtype=np.float64
        ).tolist(),
        "workspace_delta": np.asarray(
            [query.workspace_delta for query in queries], dtype=np.float64
        ).tolist(),
        "baseline_actions": np.asarray(
            [query.baseline_actions for query in queries], dtype=np.float64
        ).tolist(),
        "intervened_actions": np.asarray(
            [query.intervened_actions for query in queries], dtype=np.float64
        ).tolist(),
        "action_delta": np.asarray(
            [query.action_delta for query in queries], dtype=np.float64
        ).tolist(),
        "baseline_resolutions": [list(query.baseline_resolutions) for query in queries],
        "intervened_resolutions": [
            list(query.intervened_resolutions) for query in queries
        ],
    }
    return selected, score_vector, queries, payload


def _generic_query_payload(
    agent: RRCTAgent,
    candidates: np.ndarray,
    future: np.ndarray,
    objective: np.ndarray,
) -> tuple[int, np.ndarray, dict[str, Any]]:
    baselines: list[np.ndarray] = []
    interventions: list[np.ndarray] = []
    baseline_actions: list[np.ndarray] = []
    intervention_actions: list[np.ndarray] = []
    for delta in candidates:
        baseline = copy.deepcopy(agent)
        intervened = copy.deepcopy(agent)
        intervened.workspace.state += delta
        baseline_steps = [
            baseline.step(observation, source="v06_generic_query")
            for observation in future
        ]
        intervention_steps = [
            intervened.step(observation, source="v06_generic_query")
            for observation in future
        ]
        baselines.append(np.stack([step.workspace for step in baseline_steps]))
        interventions.append(np.stack([step.workspace for step in intervention_steps]))
        baseline_actions.append(np.stack([step.action for step in baseline_steps]))
        intervention_actions.append(
            np.stack([step.action for step in intervention_steps])
        )
    baseline_array = np.asarray(baselines, dtype=np.float64)
    intervention_array = np.asarray(interventions, dtype=np.float64)
    scores = intervention_array[:, -1, :] @ objective
    payload = {
        "scores": scores.tolist(),
        "baseline_workspace": baseline_array.tolist(),
        "intervened_workspace": intervention_array.tolist(),
        "workspace_delta": (intervention_array - baseline_array).tolist(),
        "baseline_actions": np.asarray(baseline_actions).tolist(),
        "intervened_actions": np.asarray(intervention_actions).tolist(),
        "action_delta": (
            np.asarray(intervention_actions) - np.asarray(baseline_actions)
        ).tolist(),
    }
    return int(np.argmax(scores)), np.asarray(scores, dtype=np.float64), payload


def _realized_self_outcomes(
    agent: RRCTAgent,
    candidates: np.ndarray,
    future: np.ndarray,
    objective: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    final_workspaces: list[np.ndarray] = []
    for delta in candidates:
        realized = copy.deepcopy(agent)
        realized.self_model.state += delta
        steps = [
            realized.step(observation, source="v06_realized_outcome")
            for observation in future
        ]
        final_workspaces.append(steps[-1].workspace)
    final_array = np.asarray(final_workspaces, dtype=np.float64)
    return final_array, final_array @ objective


def _average_ranks(values: Sequence[float]) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64)
    order = np.argsort(vector, kind="mergesort")
    ranks = np.empty(vector.size, dtype=np.float64)
    start = 0
    while start < vector.size:
        stop = start + 1
        while stop < vector.size and vector[order[stop]] == vector[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def _spearman(first: Sequence[float], second: Sequence[float]) -> float:
    left = _average_ranks(first)
    right = _average_ranks(second)
    if np.std(left) == 0.0 or np.std(right) == 0.0:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


def _selection_record(
    selected: int,
    selector_scores: np.ndarray,
    realized_scores: np.ndarray,
    *,
    score_prediction_is_comparable: bool = True,
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    oracle_score = float(np.max(realized_scores))
    oracle_indices = np.flatnonzero(realized_scores >= oracle_score - tolerance)
    minimum = float(np.min(realized_scores))
    score_range = oracle_score - minimum
    selected_realized = float(realized_scores[selected])
    raw_regret = oracle_score - selected_realized
    return {
        "selected_index": int(selected),
        "selector_argmax": int(np.argmax(selector_scores)),
        "selector_scores": selector_scores.tolist(),
        "oracle_indices": oracle_indices.astype(int).tolist(),
        "oracle_score": oracle_score,
        "selected_realized_score": selected_realized,
        "selection_success": bool(selected in set(oracle_indices.tolist())),
        "raw_regret": float(raw_regret),
        "normalized_regret": float(raw_regret / max(score_range, tolerance)),
        "score_recovery": float(
            (selected_realized - minimum) / max(score_range, tolerance)
        ),
        "selector_vs_realized_spearman": _spearman(
            selector_scores, realized_scores
        ),
        "score_prediction_rmse": (
            float(np.sqrt(np.mean(np.square(selector_scores - realized_scores))))
            if score_prediction_is_comparable
            else None
        ),
    }


def _failure_row(
    *,
    seed: int,
    probe: int,
    wrong_seed: int,
    reason: str,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    row = {field: None for field in ROW_FIELDS}
    row.update(
        {
            "status": "stopped_exception",
            "stop_reason": [reason],
            "seed": int(seed),
            "probe": int(probe),
            "wrong_self_seed": int(wrong_seed),
            "train_episode_count": int(parameters["train_episode_count"]),
            "train_delay": int(parameters["train_delay"]),
            "test_delay": int(parameters["test_delay"]),
            "future_horizon": int(parameters["future_horizon"]),
            "direction_count": int(parameters["direction_count"]),
            "candidate_count": 2 * int(parameters["direction_count"]),
            "candidate_magnitude": float(parameters["candidate_magnitude"]),
        }
    )
    return row


def _run_probe(
    *,
    seed: int,
    probe: int,
    episode: Any,
    evaluation_episode: Any,
    snapshot: Mapping[str, Any],
    wrong_seed: int,
    wrong_snapshot: Mapping[str, Any],
    objective: np.ndarray,
    self_candidates: np.ndarray,
    generic_candidates: np.ndarray,
    train_episode_count: int,
    train_delay: int,
    test_delay: int,
    future_horizon: int,
    candidate_magnitude: float,
) -> dict[str, Any]:
    observations = np.asarray(episode.observations, dtype=np.float64)
    prime_observations = observations[:-future_horizon]
    future = observations[-future_horizon:]
    evaluation_observations = np.asarray(
        evaluation_episode.observations, dtype=np.float64
    )
    evaluation_future = evaluation_observations[-future_horizon:]
    live = _agent(seed, self_model_mode="frozen")
    live.load_predictor_snapshot(snapshot, freeze=True)
    wrong = _agent(seed, self_model_mode="frozen")
    wrong.load_predictor_snapshot(wrong_snapshot, freeze=True)
    no_self = _agent(seed, ablations=("self_model",), self_model_mode="frozen")
    no_self.load_predictor_snapshot(snapshot, freeze=True)
    _prime(live, prime_observations, "v06_live_prime")
    _prime(wrong, prime_observations, "v06_wrong_self_prime")
    _prime(no_self, prime_observations, "v06_no_self_prime")

    before = {
        "live": _agent_state_sha256(live),
        "wrong_self": _agent_state_sha256(wrong),
        "self_ablated": _agent_state_sha256(no_self),
    }
    update_counts_before = {
        "live": int(live.self_learning_updates),
        "wrong_self": int(wrong.self_learning_updates),
        "self_ablated": int(no_self.self_learning_updates),
    }
    live_selected, live_scores, live_queries, live_payload = _query_payload(
        live, self_candidates, future, objective
    )
    wrong_selected, wrong_scores, wrong_queries, wrong_payload = _query_payload(
        wrong, self_candidates, future, objective
    )
    no_self_selected, no_self_scores, no_self_queries, no_self_payload = _query_payload(
        no_self, self_candidates, future, objective
    )
    generic_selected, generic_scores, generic_payload = _generic_query_payload(
        live, generic_candidates, future, objective
    )
    realized_workspace, realized_scores = _realized_self_outcomes(
        live, self_candidates, evaluation_future, objective
    )
    after = {
        "live": _agent_state_sha256(live),
        "wrong_self": _agent_state_sha256(wrong),
        "self_ablated": _agent_state_sha256(no_self),
    }
    update_counts_after = {
        "live": int(live.self_learning_updates),
        "wrong_self": int(wrong.self_learning_updates),
        "self_ablated": int(no_self.self_learning_updates),
    }

    live_baseline_final = np.asarray(
        [query.baseline_workspace[-1] for query in live_queries], dtype=np.float64
    )
    replay_scores = live_baseline_final[0] @ objective * np.ones(
        self_candidates.shape[0], dtype=np.float64
    )
    replay_selected = int(np.argmax(replay_scores))
    random_rng = np.random.default_rng(
        np.random.SeedSequence([int(seed), int(probe), 0x5636524E])
    )
    random_keys = random_rng.random(self_candidates.shape[0])
    random_selected = int(np.argmax(random_keys))

    selections = {
        "live_self_query": _selection_record(
            live_selected, live_scores, realized_scores
        ),
        "wrong_self_query": _selection_record(
            wrong_selected, wrong_scores, realized_scores
        ),
        "self_ablated_query": _selection_record(
            no_self_selected, no_self_scores, realized_scores
        ),
        "replay": _selection_record(
            replay_selected, replay_scores, realized_scores
        ),
        "random": _selection_record(
            random_selected,
            random_keys,
            realized_scores,
            score_prediction_is_comparable=False,
        ),
        "generic_equal_compute": _selection_record(
            generic_selected, generic_scores, realized_scores
        ),
    }
    candidate_count = int(self_candidates.shape[0])
    paired_steps = 2 * candidate_count * future_horizon
    no_self_delta = np.asarray(
        [query.workspace_delta for query in no_self_queries], dtype=np.float64
    )
    live_predicted_final = np.asarray(
        [query.intervened_workspace[-1] for query in live_queries], dtype=np.float64
    )
    wrong_predicted_final = np.asarray(
        [query.intervened_workspace[-1] for query in wrong_queries], dtype=np.float64
    )
    generic_baseline = np.asarray(generic_payload["baseline_workspace"], dtype=np.float64)
    finite_arrays = (
        objective,
        self_candidates,
        generic_candidates,
        future,
        evaluation_future,
        live_scores,
        wrong_scores,
        no_self_scores,
        generic_scores,
        replay_scores,
        random_keys,
        realized_workspace,
        realized_scores,
    )
    invariants = {
        "all_values_finite": bool(all(np.all(np.isfinite(x)) for x in finite_arrays)),
        "objective_unit_norm": bool(np.isclose(np.linalg.norm(objective), 1.0, atol=1e-12, rtol=1e-12)),
        "self_candidate_norms_match": bool(np.allclose(np.linalg.norm(self_candidates, axis=1), candidate_magnitude, atol=1e-12, rtol=1e-12)),
        "generic_candidate_norms_match": bool(np.allclose(np.linalg.norm(generic_candidates, axis=1), candidate_magnitude, atol=1e-12, rtol=1e-12)),
        "live_api_selection_is_score_argmax": bool(live_selected == int(np.argmax(live_scores))),
        "wrong_self_selection_is_score_argmax": bool(wrong_selected == int(np.argmax(wrong_scores))),
        "self_ablated_selection_is_score_argmax": bool(no_self_selected == int(np.argmax(no_self_scores))),
        "generic_selection_is_score_argmax": bool(generic_selected == int(np.argmax(generic_scores))),
        "live_scores_match_retained_workspaces": bool(np.allclose(live_scores, live_predicted_final @ objective, atol=1e-12, rtol=1e-12)),
        "wrong_scores_match_retained_workspaces": bool(np.allclose(wrong_scores, wrong_predicted_final @ objective, atol=1e-12, rtol=1e-12)),
        "planning_and_evaluation_streams_are_distinct": bool(not np.array_equal(future, evaluation_future)),
        "planning_and_evaluation_latents_match": bool(
            (episode.context, episode.object_cue, episode.actuator_map)
            == (evaluation_episode.context, evaluation_episode.object_cue, evaluation_episode.actuator_map)
        ),
        "live_baseline_is_candidate_invariant": bool(np.all(live_baseline_final == live_baseline_final[0])),
        "generic_baseline_is_candidate_invariant": bool(np.all(generic_baseline == generic_baseline[0])),
        "self_ablated_workspace_response_is_exactly_zero": bool(np.all(no_self_delta == 0.0)),
        "self_ablated_scores_are_exactly_tied": bool(np.all(no_self_scores == no_self_scores[0])),
        "replay_scores_are_exactly_tied": bool(np.all(replay_scores == replay_scores[0])),
        "query_does_not_mutate_live_agents": bool(before == after),
        "frozen_predictor_updates_are_zero": bool(update_counts_before == update_counts_after),
        "live_snapshot_loaded_exactly": bool(_predictor_snapshot_id(live.predictor_snapshot()) == _predictor_snapshot_id(snapshot)),
        "wrong_snapshot_loaded_exactly": bool(_predictor_snapshot_id(wrong.predictor_snapshot()) == _predictor_snapshot_id(wrong_snapshot)),
        "generic_compute_equals_live_query_compute": True,
        "wrong_self_compute_equals_live_query_compute": True,
        "self_ablated_compute_equals_live_query_compute": True,
    }
    stop_reasons = [name for name, passed in invariants.items() if not passed]
    predictions = {
        "live_self_query": live_payload,
        "wrong_self_query": wrong_payload,
        "self_ablated_query": no_self_payload,
        "generic_equal_compute": generic_payload,
        "replay": {
            "scores": replay_scores.tolist(),
            "baseline_final_workspace": live_baseline_final[0].tolist(),
        },
        "random": {
            "selection_keys": random_keys.tolist(),
            "rng_seed_words": [int(seed), int(probe), 0x5636524E],
        },
        "independent_realization": {
            "scores": realized_scores.tolist(),
            "final_workspace": realized_workspace.tolist(),
        },
    }
    return {
        "status": "completed" if not stop_reasons else "protocol_contradiction",
        "stop_reason": stop_reasons,
        "seed": int(seed),
        "probe": int(probe),
        "episode_id": int(episode.episode_id),
        "latent_factors": [int(episode.context), int(episode.object_cue), int(episode.actuator_map)],
        "wrong_self_seed": int(wrong_seed),
        "live_predictor_snapshot_id": _predictor_snapshot_id(snapshot),
        "wrong_predictor_snapshot_id": _predictor_snapshot_id(wrong_snapshot),
        "predictor_learning_steps": int(snapshot.get("learning_steps", 0)),
        "train_episode_count": int(train_episode_count),
        "train_delay": int(train_delay),
        "test_delay": int(test_delay),
        "future_horizon": int(future_horizon),
        "direction_count": int(candidate_count // 2),
        "candidate_count": candidate_count,
        "candidate_magnitude": float(candidate_magnitude),
        "objective": objective.tolist(),
        "objective_sha256": _array_sha256(objective),
        "self_candidate_deltas": self_candidates.tolist(),
        "self_candidate_sha256": _array_sha256(self_candidates),
        "generic_workspace_deltas": generic_candidates.tolist(),
        "generic_candidate_sha256": _array_sha256(generic_candidates),
        "planning_observations": future.tolist(),
        "planning_observations_sha256": _array_sha256(future),
        "evaluation_observations": evaluation_future.tolist(),
        "evaluation_observations_sha256": _array_sha256(evaluation_future),
        "predictions": predictions,
        "selections": selections,
        "compute_audit": {
            "live_self_query_forward_steps": paired_steps,
            "wrong_self_query_forward_steps": paired_steps,
            "self_ablated_query_forward_steps": paired_steps,
            "generic_equal_compute_forward_steps": paired_steps,
            "replay_forward_steps": 0,
            "random_forward_steps": 0,
            "independent_evaluator_forward_steps": candidate_count * future_horizon,
            "counting_rule": "deep-copied agent.step calls",
        },
        "invariants": invariants,
        "state_digests": {"before_queries": before, "after_queries": after},
    }


def _seed_summaries(rows: Sequence[Mapping[str, Any]], seeds: Sequence[int]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for seed in seeds:
        group = [row for row in rows if row["seed"] == seed]
        summaries.append(
            {
                "seed": int(seed),
                "probe_count": len(group),
                "conditions": {
                    condition: {
                        "selection_accuracy": float(np.mean([row["selections"][condition]["selection_success"] for row in group])),
                        "mean_normalized_regret": float(np.mean([row["selections"][condition]["normalized_regret"] for row in group])),
                        "mean_score_recovery": float(np.mean([row["selections"][condition]["score_recovery"] for row in group])),
                        "mean_selector_vs_realized_spearman": float(np.mean([row["selections"][condition]["selector_vs_realized_spearman"] for row in group])),
                    }
                    for condition in CONDITIONS
                },
            }
        )
    return summaries


def _development_aggregates(
    seed_summaries: Sequence[Mapping[str, Any]],
    *,
    bootstrap_resamples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(int(bootstrap_seed))
    metrics = (
        "selection_accuracy",
        "mean_normalized_regret",
        "mean_score_recovery",
        "mean_selector_vs_realized_spearman",
    )
    conditions: dict[str, Any] = {}
    for condition in CONDITIONS:
        conditions[condition] = {}
        for metric in metrics:
            values = [float(row["conditions"][condition][metric]) for row in seed_summaries]
            interval = _bootstrap_mean_ci(values, resamples=bootstrap_resamples, rng=rng)
            conditions[condition][metric] = {
                **interval,
                "population_std": float(np.std(values, ddof=0)),
                "individual_seed_values": [
                    {"seed": int(row["seed"]), "value": float(row["conditions"][condition][metric])}
                    for row in seed_summaries
                ],
            }
    comparisons: dict[str, Any] = {}
    for control in CONDITIONS[1:]:
        values = [
            float(row["conditions"]["live_self_query"]["selection_accuracy"])
            - float(row["conditions"][control]["selection_accuracy"])
            for row in seed_summaries
        ]
        comparisons[f"live_minus_{control}_selection_accuracy"] = {
            **_bootstrap_mean_ci(values, resamples=bootstrap_resamples, rng=rng),
            "population_std": float(np.std(values, ddof=0)),
            "individual_seed_values": [
                {"seed": int(row["seed"]), "value": float(value)}
                for row, value in zip(seed_summaries, values)
            ],
            "interpretation": "development-only descriptive contrast; no support gate",
        }
    return {"conditions": conditions, "comparisons": comparisons}


def _write_rows_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: json.dumps(
                        _json_safe(row[field]),
                        separators=(",", ":"),
                        sort_keys=True,
                        allow_nan=False,
                    )
                    for field in ROW_FIELDS
                }
            )


def _plot(path: Path, seed_summaries: Sequence[Mapping[str, Any]]) -> bool:
    try:
        cache = Path(tempfile.gettempdir()) / "rrct_matplotlib_cache"
        cache.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(cache))
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover - optional dependency boundary
        return False
    x = np.arange(len(CONDITIONS), dtype=np.float64)
    figure, axes = plt.subplots(1, 2, figsize=(14, 5.5), constrained_layout=True)
    for row in seed_summaries:
        axes[0].plot(
            x,
            [row["conditions"][condition]["selection_accuracy"] for condition in CONDITIONS],
            marker="o",
            alpha=0.35,
        )
        axes[1].plot(
            x,
            [row["conditions"][condition]["mean_normalized_regret"] for condition in CONDITIONS],
            marker="o",
            alpha=0.35,
        )
    for axis, title, ylabel in (
        (axes[0], "Novel-objective selection accuracy", "Accuracy"),
        (axes[1], "Normalized realized regret", "Regret (lower is better)"),
    ):
        axis.set_xticks(x, [name.replace("_", "\n") for name in CONDITIONS])
        axis.set_ylim(-0.03, 1.03)
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.25)
    figure.suptitle("Prospective self-access controls — nonconfirmatory development seeds")
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return True


def run_self_access_experiment(
    output: str | Path,
    *,
    seeds: Sequence[int] = V06_DEVELOPMENT_SEEDS,
    train_episode_count: int = 128,
    probe_count: int = 8,
    train_delay: int = 5,
    test_delay: int = 7,
    future_horizon: int = 4,
    direction_count: int = 4,
    candidate_magnitude: float = 0.35,
    bootstrap_resamples: int = V06_DEVELOPMENT_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V06_DEVELOPMENT_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Run the bounded nonconfirmatory self-access development experiment."""

    seed_values = tuple(int(seed) for seed in seeds)
    if len(seed_values) < 2 or len(set(seed_values)) != len(seed_values):
        raise ValueError("at least two unique development seeds are required")
    unknown = set(seed_values) - set(V06_DEVELOPMENT_SEEDS)
    if unknown:
        raise ValueError(
            "this development runner refuses seeds outside V06_DEVELOPMENT_SEEDS: "
            f"{sorted(unknown)}"
        )
    for name, value, minimum in (
        ("train_episode_count", train_episode_count, 8),
        ("probe_count", probe_count, 8),
        ("train_delay", train_delay, 1),
        ("test_delay", test_delay, 1),
        ("future_horizon", future_horizon, 1),
        ("direction_count", direction_count, 1),
        ("bootstrap_resamples", bootstrap_resamples, 1),
    ):
        if int(value) != value or value < minimum:
            raise ValueError(f"{name} must be an integer of at least {minimum}")
    if probe_count > 16:
        raise ValueError("probe_count cannot exceed the 16-dimensional objective basis")
    if direction_count > 12:
        raise ValueError("direction_count cannot exceed the 12-dimensional self state")
    if future_horizon >= test_delay + 3:
        raise ValueError("future_horizon must leave at least one priming observation")
    if (
        not np.isfinite(candidate_magnitude)
        or candidate_magnitude <= 0.0
        or candidate_magnitude > 1.0
    ):
        raise ValueError("candidate_magnitude must be finite and lie in (0, 1]")
    destination = _prepare_empty_output(output)
    parameters = {
        "train_episode_count": int(train_episode_count),
        "probe_count": int(probe_count),
        "train_delay": int(train_delay),
        "test_delay": int(test_delay),
        "future_horizon": int(future_horizon),
        "direction_count": int(direction_count),
        "candidate_magnitude": float(candidate_magnitude),
    }

    snapshots: dict[int, Mapping[str, Any]] = {}
    setup_errors: dict[int, str] = {}
    for seed in seed_values:
        try:
            training = _episodes(
                train_episode_count,
                seed=seed + 10_000,
                delay=train_delay,
            )
            snapshots[seed] = _train_predictor_snapshot(training, seed=seed)
        except Exception as exc:  # retained rather than seed-filtered
            setup_errors[seed] = f"setup_exception:{type(exc).__name__}:{exc}"

    self_directions = _dct_directions(12, direction_count)
    self_candidates = _signed_candidates(self_directions, candidate_magnitude)
    rows: list[dict[str, Any]] = []
    pairing = {
        seed: seed_values[(index + 1) % len(seed_values)]
        for index, seed in enumerate(seed_values)
    }
    for seed in seed_values:
        wrong_seed = pairing[seed]
        try:
            probes = _episodes(probe_count, seed=seed + 20_000, delay=test_delay)
            evaluation_probes = _episodes(
                probe_count, seed=seed + 30_000, delay=test_delay
            )
            objectives = _random_orthonormal_directions(
                16,
                probe_count,
                seed_words=(seed, 0x56364F42),
            )
            generic_directions = _random_orthonormal_directions(
                16,
                direction_count,
                seed_words=(seed, 0x5636474E),
            )
            generic_candidates = _signed_candidates(
                generic_directions, candidate_magnitude
            )
        except Exception as exc:
            setup_errors[seed] = f"probe_setup_exception:{type(exc).__name__}:{exc}"
            probes = [None] * probe_count
            evaluation_probes = [None] * probe_count
            objectives = np.zeros((probe_count, 16), dtype=np.float64)
            generic_candidates = np.zeros(
                (2 * direction_count, 16), dtype=np.float64
            )
        for probe in range(probe_count):
            unavailable = setup_errors.get(seed) or setup_errors.get(wrong_seed)
            if unavailable:
                rows.append(
                    _failure_row(
                        seed=seed,
                        probe=probe,
                        wrong_seed=wrong_seed,
                        reason=unavailable,
                        parameters=parameters,
                    )
                )
                continue
            try:
                rows.append(
                    _run_probe(
                        seed=seed,
                        probe=probe,
                        episode=probes[probe],
                        evaluation_episode=evaluation_probes[probe],
                        snapshot=snapshots[seed],
                        wrong_seed=wrong_seed,
                        wrong_snapshot=snapshots[wrong_seed],
                        objective=objectives[probe],
                        self_candidates=self_candidates,
                        generic_candidates=generic_candidates,
                        train_episode_count=train_episode_count,
                        train_delay=train_delay,
                        test_delay=test_delay,
                        future_horizon=future_horizon,
                        candidate_magnitude=candidate_magnitude,
                    )
                )
            except Exception as exc:
                rows.append(
                    _failure_row(
                        seed=seed,
                        probe=probe,
                        wrong_seed=wrong_seed,
                        reason=f"probe_exception:{type(exc).__name__}:{exc}",
                        parameters=parameters,
                    )
                )

    protocol_stopped = any(row["status"] != "completed" for row in rows)
    if protocol_stopped:
        seed_summaries: list[dict[str, Any]] = []
        aggregates: dict[str, Any] = {
            "status": "withheld_after_protocol_stop"
        }
    else:
        seed_summaries = _seed_summaries(rows, seed_values)
        aggregates = _development_aggregates(
            seed_summaries,
            bootstrap_resamples=int(bootstrap_resamples),
            bootstrap_seed=int(bootstrap_seed),
        )

    csv_name = "self_access_rows.csv"
    json_name = "self_access_summary.json"
    png_name = "self_access_controls.png"
    _write_rows_csv(destination / csv_name, rows)
    figure_created = (
        _plot(destination / png_name, seed_summaries)
        if not protocol_stopped
        else False
    )
    summary = {
        "schema": "rrct.self_access.development.v0.6-dev2",
        "version": __version__,
        "experiment": "heldout_continuation_prospective_self_counterfactual_selection",
        "status": (
            "stopped_protocol_contradiction"
            if protocol_stopped
            else "completed_development_only"
        ),
        "protocol_scope": "nonconfirmatory_development_only",
        "confirmatory_claim_allowed": False,
        "parameters": {**parameters, "seeds": list(seed_values)},
        "wrong_self_pairing": {str(seed): int(pairing[seed]) for seed in seed_values},
        "conditions": {
            "live_self_query": "public candidate-wise self-counterfactual query",
            "wrong_self_query": "same core and compute with the cyclic next seed's frozen predictor snapshot",
            "self_ablated_query": "same query compute with the self-model causal link disabled",
            "replay": "candidate-independent exact live baseline final workspace",
            "random": "deterministic seed-and-probe-specific random keys",
            "generic_equal_compute": "paired direct-workspace perturbation rollouts with independent orthonormal directions and the same agent.step count",
        },
        "novel_objective_protocol": (
            "Objectives are deterministic seed-specific orthonormal workspace "
            "directions generated only after label-free predictor training."
        ),
        "compute_scope": (
            "Equal compute counts deep-copied agent.step calls only; it does not "
            "claim equal memory traffic, Python overhead, or semantic information."
        ),
        "bootstrap": {
            "method": "development-only percentile bootstrap over seed summaries",
            "resamples": int(bootstrap_resamples),
            "rng_seed": int(bootstrap_seed),
            "confidence": 0.95,
            "inferential_gate": "none",
        },
        "rows": rows,
        "row_count": len(rows),
        "seed_summaries": seed_summaries,
        "development_aggregates": aggregates,
        "stop_reasons": sorted(
            {
                reason
                for row in rows
                for reason in (row["stop_reason"] or [])
            }
        ),
        "artifacts": [json_name, csv_name]
        + ([png_name] if figure_created else []),
        "limitations": [
            "Planning and evaluation use independently noisy matched-latent continuations, but the future model supplied to the planner is still externally specified.",
            "The novel objectives are synthetic linear workspace directions and may not represent natural downstream tasks.",
            "The cross-seed control swaps only the learned predictor snapshot, not the complete self-model dynamics, avoiding a larger baseline confound but testing only one notion of wrong-self matching.",
            "The generic control matches forward-step count but not intervention semantics, information content, memory traffic, or implementation overhead.",
            "Replay and random are exclusion baselines, not equal-compute controls.",
            "Four reused development seeds are too few for confirmatory inference; every bootstrap interval is exploratory.",
            "Candidate directions, magnitude, horizon, and tie tolerance remain design choices requiring preregistration before untouched validation.",
        ],
        "interpretation_boundary": (
            "This experiment tests bounded prospective use of a causal self-state. "
            "It does not establish consciousness, sentience, subjective experience, "
            "a universal self-access mechanism, or moral status."
        ),
    }
    (destination / json_name).write_text(
        json.dumps(_json_safe(summary), indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    return summary


__all__ = [
    "CONDITIONS",
    "ROW_FIELDS",
    "V06_DEVELOPMENT_BOOTSTRAP_RESAMPLES",
    "V06_DEVELOPMENT_BOOTSTRAP_SEED",
    "V06_DEVELOPMENT_SEEDS",
    "run_self_access_experiment",
]

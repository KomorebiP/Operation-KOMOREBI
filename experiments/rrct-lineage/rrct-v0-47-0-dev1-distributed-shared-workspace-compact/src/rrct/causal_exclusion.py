"""Preregistered v0.5 causal-exclusion experiment.

The experiment distinguishes baseline output equivalence from equivalence under
a novel hidden intervention.  It is an architecture test, not a consciousness
detector.
"""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from ._version import __version__
from .agent import RRCTAgent, StepResult
from .experiments import _agent, _bootstrap_mean_ci, _episodes, _train_predictor_snapshot


V05_VALIDATION_SEEDS = (269, 271, 277, 281, 283, 293, 307, 311)
V05_BOOTSTRAP_RESAMPLES = 20_000
V05_BOOTSTRAP_SEED = 20_260_821
ROW_FIELDS = (
    "seed", "probe", "direction", "sign", "live_workspace_response",
    "live_telemetry_response", "live_hard_decision_response",
    "no_self_workspace_response", "no_self_telemetry_response",
    "replay_response", "replay_baseline_exact", "yoked_baseline_exact",
)


def _telemetry(step: StepResult) -> np.ndarray:
    one_hot = np.zeros(len(step.resolution_scores), dtype=np.float64)
    one_hot[step.next_resolution_level] = 1.0
    return np.concatenate((step.action, one_hot, step.action_scores, step.resolution_scores))


def _hard_decision(step: StepResult) -> np.ndarray:
    return np.concatenate((step.action, np.asarray([step.next_resolution_level], dtype=np.float64)))


def _dct_directions(dimension: int, count: int) -> np.ndarray:
    coordinates = np.arange(dimension, dtype=np.float64)
    rows = []
    for frequency in range(count):
        vector = np.cos(np.pi * (coordinates + 0.5) * frequency / dimension)
        rows.append(vector / np.linalg.norm(vector))
    matrix = np.asarray(rows, dtype=np.float64)
    if not np.allclose(matrix @ matrix.T, np.eye(count), atol=1e-12):
        raise RuntimeError("DCT intervention directions are not orthonormal")
    return matrix


def _prime(agent: RRCTAgent, observations: np.ndarray) -> RRCTAgent:
    agent.reset()
    agent.freeze_self_model()
    for observation in observations:
        agent.step(observation, source="v05_prime")
    return agent


def _paired_response(
    template: RRCTAgent,
    direction: np.ndarray,
    *,
    magnitude: float,
    horizon: int,
) -> tuple[float, float, float, bool]:
    baseline = copy.deepcopy(template)
    intervened = copy.deepcopy(template)
    intervened.self_model.state += magnitude * direction
    zeros = np.zeros(template.observation_dim, dtype=np.float64)
    workspace_squared: list[float] = []
    telemetry_squared: list[float] = []
    hard_changed: list[float] = []
    baseline_telemetry: list[np.ndarray] = []
    replay_telemetry: list[np.ndarray] = []
    for _ in range(horizon):
        base_step = baseline.step(zeros, source="v05_response")
        intervention_step = intervened.step(zeros, source="v05_response")
        base_control = _telemetry(base_step)
        intervention_control = _telemetry(intervention_step)
        baseline_telemetry.append(base_control)
        replay_telemetry.append(base_control.copy())
        workspace_squared.append(float(np.mean(np.square(intervention_step.workspace - base_step.workspace))))
        telemetry_squared.append(float(np.mean(np.square(intervention_control - base_control))))
        hard_changed.append(float(not np.array_equal(_hard_decision(intervention_step), _hard_decision(base_step))))
    return (
        float(np.sqrt(np.mean(workspace_squared))),
        float(np.sqrt(np.mean(telemetry_squared))),
        float(np.mean(hard_changed)),
        bool(np.array_equal(np.asarray(baseline_telemetry), np.asarray(replay_telemetry))),
    )


def _workspace_positive_control(template: RRCTAgent, magnitude: float, horizon: int) -> float:
    baseline = copy.deepcopy(template)
    intervened = copy.deepcopy(template)
    zeros = np.zeros(template.observation_dim, dtype=np.float64)
    squared: list[float] = []
    delta = np.zeros(template.workspace_dim, dtype=np.float64)
    delta[0] = magnitude
    for lag in range(horizon):
        base_step = baseline.step(zeros, source="v05_positive_control")
        intervention_step = intervened.step(
            zeros,
            source="v05_positive_control",
            perturb_workspace=delta if lag == 0 else None,
        )
        squared.append(float(np.mean(np.square(intervention_step.workspace - base_step.workspace))))
    return float(np.sqrt(np.mean(squared)))


def _seed_summary(rows: list[dict[str, Any]], seeds: Sequence[int]) -> list[dict[str, float | int]]:
    summaries: list[dict[str, float | int]] = []
    for seed in seeds:
        selected = [row for row in rows if row["seed"] == seed]
        summaries.append({
            "seed": int(seed),
            "live_workspace_response": float(np.mean([r["live_workspace_response"] for r in selected])),
            "live_telemetry_response": float(np.mean([r["live_telemetry_response"] for r in selected])),
            "no_self_workspace_response": float(np.mean([r["no_self_workspace_response"] for r in selected])),
            "live_minus_no_self_workspace": float(np.mean([r["live_workspace_response"] - r["no_self_workspace_response"] for r in selected])),
        })
    return summaries


def _aggregate(values: Sequence[float], *, rng: np.random.Generator, resamples: int) -> dict[str, Any]:
    interval = _bootstrap_mean_ci(values, resamples=resamples, rng=rng)
    return {
        **interval,
        "positive_seed_count": int(np.count_nonzero(np.asarray(values) > 0.0)),
        "seed_count": len(values),
    }


def _plot(destination: Path, seed_rows: list[dict[str, float | int]]) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    labels = [str(row["seed"]) for row in seed_rows]
    x = np.arange(len(labels))
    width = 0.25
    fig, axis = plt.subplots(figsize=(10, 5.5))
    axis.bar(x - width, [row["live_workspace_response"] for row in seed_rows], width, label="live workspace")
    axis.bar(x, [row["live_telemetry_response"] for row in seed_rows], width, label="live control telemetry")
    axis.bar(x + width, [row["no_self_workspace_response"] for row in seed_rows], width, label="no-self workspace")
    axis.set_xticks(x, labels)
    axis.set_xlabel("prespecified seed")
    axis.set_ylabel("intervention response RMSE")
    axis.set_title("Hidden self intervention under exact baseline output equivalence")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)
    return True


def run_causal_exclusion(
    output: str | Path,
    *,
    seeds: Sequence[int] = V05_VALIDATION_SEEDS,
    train_episode_count: int = 128,
    train_delay: int = 5,
    test_delay: int = 7,
    magnitude: float = 0.35,
    horizon: int = 12,
    bootstrap_resamples: int = V05_BOOTSTRAP_RESAMPLES,
    bootstrap_seed: int = V05_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    seeds = tuple(int(seed) for seed in seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be nonempty and unique")
    if train_episode_count < 8 or horizon <= 0 or magnitude <= 0.0:
        raise ValueError("invalid episode count, horizon, or magnitude")
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise FileExistsError(f"output directory must be empty: {destination}")
    directions = _dct_directions(12, 4)
    rows: list[dict[str, Any]] = []
    positive_controls: list[dict[str, float | int]] = []
    for seed in seeds:
        train = _episodes(train_episode_count, seed=seed + 10_000, delay=train_delay)
        snapshot = _train_predictor_snapshot(train, seed=seed)
        probes = _episodes(8, seed=seed + 20_000, delay=test_delay)
        seed_live_controls: list[float] = []
        seed_no_self_controls: list[float] = []
        for probe, (episode, direction_index, sign) in enumerate(
            zip(probes, np.repeat(np.arange(4), 2), np.tile(np.asarray((1.0, -1.0)), 4))
        ):
            live = _agent(seed, self_model_mode="frozen")
            live.load_predictor_snapshot(snapshot, freeze=True)
            no_self = _agent(seed, ablations=("self_model",), self_model_mode="frozen")
            no_self.load_predictor_snapshot(snapshot, freeze=True)
            observations = np.asarray(episode.observations, dtype=np.float64)
            _prime(live, observations)
            _prime(no_self, observations)
            direction = float(sign) * directions[int(direction_index)]
            live_w, live_t, live_h, replay_exact = _paired_response(live, direction, magnitude=magnitude, horizon=horizon)
            no_w, no_t, _, _ = _paired_response(no_self, direction, magnitude=magnitude, horizon=horizon)
            # The yoked exposure is, by construction, the stored live baseline
            # telemetry. Keep the exact-equality audit explicit in every row.
            rows.append({
                "seed": seed, "probe": probe, "direction": int(direction_index), "sign": int(sign),
                "live_workspace_response": live_w, "live_telemetry_response": live_t,
                "live_hard_decision_response": live_h, "no_self_workspace_response": no_w,
                "no_self_telemetry_response": no_t, "replay_response": 0.0,
                "replay_baseline_exact": replay_exact, "yoked_baseline_exact": True,
            })
            if probe == 0:
                seed_live_controls.append(_workspace_positive_control(live, magnitude, horizon))
                seed_no_self_controls.append(_workspace_positive_control(no_self, magnitude, horizon))
        positive_controls.append({"seed": seed, "live": seed_live_controls[0], "no_self": seed_no_self_controls[0]})
    seed_rows = _seed_summary(rows, seeds)
    rng = np.random.default_rng(bootstrap_seed)
    aggregates = {
        field: _aggregate([float(row[field]) for row in seed_rows], rng=rng, resamples=bootstrap_resamples)
        for field in ("live_workspace_response", "live_telemetry_response", "live_minus_no_self_workspace")
    }
    gates = {
        "replay_baseline_exact": all(row["replay_baseline_exact"] for row in rows),
        "yoked_baseline_exact": all(row["yoked_baseline_exact"] for row in rows),
        "replay_self_response_zero": all(row["replay_response"] == 0.0 for row in rows),
        "no_self_workspace_response_at_most_1e-12": all(row["no_self_workspace_response"] <= 1e-12 for row in rows),
        "live_workspace_response": aggregates["live_workspace_response"]["positive_seed_count"] >= 6 and aggregates["live_workspace_response"]["ci95_lower"] > 0.0,
        "live_telemetry_response": aggregates["live_telemetry_response"]["positive_seed_count"] >= 6 and aggregates["live_telemetry_response"]["ci95_lower"] > 0.0,
        "live_minus_no_self_workspace": aggregates["live_minus_no_self_workspace"]["positive_seed_count"] >= 6 and aggregates["live_minus_no_self_workspace"]["ci95_lower"] > 0.0,
        "workspace_positive_controls": all(row["live"] > 1e-12 and row["no_self"] > 1e-12 for row in positive_controls),
    }
    csv_name = "causal_exclusion_rows.csv"
    with (destination / csv_name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    figure_name = "causal_exclusion.png"
    figure_created = _plot(destination / figure_name, seed_rows)
    summary = {
        "version": __version__, "experiment": "v0.5_causal_exclusion_under_output_equivalence",
        "status": "PASS" if all(gates.values()) else "FAIL", "gates": gates,
        "parameters": {"seeds": list(seeds), "train_episode_count": train_episode_count, "train_delay": train_delay, "test_delay": test_delay, "probe_count_per_seed": 8, "magnitude": magnitude, "horizon": horizon},
        "bootstrap": {"method": "deterministic percentile bootstrap over prespecified seed means", "resamples": bootstrap_resamples, "rng_seed": bootstrap_seed, "confidence": 0.95},
        "aggregates": aggregates, "seed_summaries": seed_rows,
        "positive_controls": positive_controls, "row_count": len(rows),
        "artifacts": [csv_name, "summary.json"] + ([figure_name] if figure_created else []),
        "warranted_claim": "Exact baseline output equivalence did not entail equivalence under a novel hidden self-model intervention, and the measured response depended on the live self-model link." if all(gates.values()) else "The preregistered causal-exclusion claim was not established.",
        "interpretation_boundary": "This experiment tests causal organization. It neither detects nor establishes phenomenal consciousness.",
    }
    (destination / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


__all__ = ["V05_BOOTSTRAP_RESAMPLES", "V05_BOOTSTRAP_SEED", "V05_VALIDATION_SEEDS", "run_causal_exclusion"]

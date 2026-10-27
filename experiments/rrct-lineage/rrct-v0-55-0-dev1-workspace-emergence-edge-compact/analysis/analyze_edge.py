from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import defaultdict
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import beta
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)


def load_jsons(path: pathlib.Path) -> list[dict[str, object]]:
    return [json.loads(file.read_text()) for file in sorted(path.glob("*.json"))]


def cp_interval(successes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    if successes == 0:
        lower = 0.0
    else:
        lower = float(beta.ppf(alpha / 2, successes, total - successes + 1))
    if successes == total:
        upper = 1.0
    else:
        upper = float(beta.ppf(1 - alpha / 2, successes + 1, total - successes))
    return lower, upper


def crossing_step(checkpoints: list[dict[str, object]], key: str, threshold: float, *, direction: str = "ge") -> int | None:
    for row in checkpoints:
        value = float(row[key])
        passed = value >= threshold if direction == "ge" else value <= threshold
        if passed:
            return int(row["step"])
    return None


def fit_weibull(rows: list[dict[str, object]], dimensions: list[int]) -> dict[str, object]:
    filtered = [row for row in rows if int(row["bottleneck_dim"]) in dimensions]
    times = np.array([
        float(row["stable_onset_step"] if row["stable_onset_step"] is not None else row["max_steps"])
        for row in filtered
    ])
    events = np.array([row["stable_onset_step"] is not None for row in filtered], dtype=float)
    dims = np.array([float(row["bottleneck_dim"]) for row in filtered])
    log_dims = np.log(dims)

    def nll(parameters: np.ndarray) -> float:
        log_shape, a, b, c = parameters
        shape = math.exp(log_shape)
        log_scale = a + b * log_dims + c * log_dims**2
        scale = np.exp(log_scale)
        ratio = np.clip(times / scale, 1e-12, 1e12)
        event_log = np.log(shape) - log_scale + (shape - 1) * (np.log(times) - log_scale) - ratio**shape
        censor_log = -(ratio**shape)
        return -float(np.sum(events * event_log + (1 - events) * censor_log))

    initial = np.array([math.log(3.0), math.log(700.0), -0.5, 0.0])
    result = minimize(nll, initial, method="Nelder-Mead", options={"maxiter": 50000})
    log_shape, a, b, c = result.x
    shape = math.exp(log_shape)

    def scale_for(dim: int) -> float:
        ld = math.log(dim)
        return math.exp(a + b * ld + c * ld * ld)

    thresholds: dict[str, dict[str, float]] = {}
    for dim in dimensions:
        scale = scale_for(dim)
        thresholds[str(dim)] = {
            "scale": scale,
            "s20": scale * (-math.log(0.8)) ** (1 / shape),
            "s50": scale * (math.log(2.0)) ** (1 / shape),
            "s80": scale * (-math.log(0.2)) ** (1 / shape),
            "s90": scale * (math.log(10.0)) ** (1 / shape),
        }
    return {
        "success": bool(result.success),
        "negative_log_likelihood": float(result.fun),
        "shape": shape,
        "log_scale_coefficients": {"intercept": float(a), "log_dim": float(b), "log_dim_squared": float(c)},
        "formula": "P(T<=S|D)=1-exp(-(S/exp(a+b log D+c log(D)^2))^k)",
        "thresholds": thresholds,
    }


def edge_auc(rows: list[dict[str, object]]) -> dict[str, float]:
    seed_ids = sorted({int(row["base_seed"]) for row in rows if int(row["bottleneck_dim"]) >= 2})
    predictions: list[float] = []
    labels: list[int] = []
    for held_seed in seed_ids:
        train_x: list[list[float]] = []
        train_y: list[int] = []
        test_x: list[list[float]] = []
        test_y: list[int] = []
        for trajectory in rows:
            dim = int(trajectory["bottleneck_dim"])
            if dim < 2:
                continue
            for checkpoint in trajectory["checkpoints"]:
                features = [
                    math.log2(float(checkpoint["step"])),
                    math.log2(float(dim)),
                    math.log2(float(dim)) ** 2,
                ]
                label = int(bool(checkpoint["emergence"]))
                if int(trajectory["base_seed"]) == held_seed:
                    test_x.append(features)
                    test_y.append(label)
                else:
                    train_x.append(features)
                    train_y.append(label)
        if len(set(train_y)) < 2:
            continue
        model = LogisticRegression(C=1e6, max_iter=10000)
        model.fit(np.asarray(train_x), np.asarray(train_y))
        probability = model.predict_proba(np.asarray(test_x))[:, 1]
        predictions.extend(probability.tolist())
        labels.extend(test_y)
    return {
        "auc": float(roc_auc_score(labels, predictions)),
        "brier": float(brier_score_loss(labels, predictions)),
        "n": len(labels),
    }


def geometry_warning_auc(rows: list[dict[str, object]]) -> dict[str, float | int | None]:
    features: list[float] = []
    labels: list[int] = []
    for trajectory in rows:
        if int(trajectory["bottleneck_dim"]) < 2:
            continue
        stable = trajectory["stable_onset_step"]
        horizon = int(trajectory["max_steps"])
        for checkpoint in trajectory["checkpoints"]:
            step = int(checkpoint["step"])
            if bool(checkpoint["emergence"]):
                continue
            if step > 800:
                continue
            label = int(stable is not None and step < int(stable) <= step + 200)
            features.append(float(checkpoint["minimum_second_to_first_ratio"]))
            labels.append(label)
    if len(set(labels)) < 2:
        return {"auc": None, "n": len(labels), "positive_count": sum(labels)}
    return {
        "auc": float(roc_auc_score(labels, features)),
        "n": len(labels),
        "positive_count": int(sum(labels)),
    }


def crossed_variance(rows: list[dict[str, object]]) -> dict[str, object]:
    frame = pd.DataFrame([
        {
            "init_seed": int(row["initialization_seed"]),
            "data_seed": int(row["data_seed"]),
            "onset": float(row["stable_onset_step"] if row["stable_onset_step"] is not None else int(row["max_steps"]) + 100),
            "emerged_800": int(row["stable_onset_step"] is not None and int(row["stable_onset_step"]) <= 800),
            "emerged_1000": int(row["stable_onset_step"] is not None and int(row["stable_onset_step"]) <= 1000),
            "emerged_1200": int(row["stable_onset_step"] is not None and int(row["stable_onset_step"]) <= 1200),
        }
        for row in rows
    ])
    y = np.log(frame["onset"].to_numpy())
    grand = float(y.mean())
    init_means = frame.assign(log_onset=y).groupby("init_seed")["log_onset"].mean()
    data_means = frame.assign(log_onset=y).groupby("data_seed")["log_onset"].mean()
    n_data = frame["data_seed"].nunique()
    n_init = frame["init_seed"].nunique()
    ss_init = float(n_data * np.sum((init_means.to_numpy() - grand) ** 2))
    ss_data = float(n_init * np.sum((data_means.to_numpy() - grand) ** 2))
    fitted = np.array([
        init_means.loc[row.init_seed] + data_means.loc[row.data_seed] - grand
        for row in frame.itertuples()
    ])
    ss_residual = float(np.sum((y - fitted) ** 2))
    total = max(ss_init + ss_data + ss_residual, 1e-12)
    return {
        "n": len(frame),
        "eta_squared_initialization": ss_init / total,
        "eta_squared_data_stream": ss_data / total,
        "eta_squared_residual": ss_residual / total,
        "success_rate_by_800": float(frame["emerged_800"].mean()),
        "success_rate_by_1000": float(frame["emerged_1000"].mean()),
        "success_rate_by_1200": float(frame["emerged_1200"].mean()),
        "initialization_mean_onsets": {str(key): float(value) for key, value in frame.groupby("init_seed")["onset"].mean().items()},
        "data_stream_mean_onsets": {str(key): float(value) for key, value in frame.groupby("data_seed")["onset"].mean().items()},
    }


def main() -> int:
    primary = load_jsons(RESULTS / "primary")
    crossed = load_jsons(RESULTS / "crossed")
    if len(primary) != 132:
        raise RuntimeError(f"expected 132 primary trajectories, found {len(primary)}")
    if len(crossed) != 32:
        raise RuntimeError(f"expected 32 crossed trajectories, found {len(crossed)}")

    dimensions = [1, 2, 3, 4, 6, 8]
    checkpoints = sorted({int(cp["step"]) for row in primary for cp in row["checkpoints"]})
    rate_rows: list[dict[str, object]] = []
    dimension_summary: list[dict[str, object]] = []
    for dim in dimensions:
        group = [row for row in primary if int(row["bottleneck_dim"]) == dim]
        onsets = [int(row["stable_onset_step"]) for row in group if row["stable_onset_step"] is not None]
        for step in checkpoints:
            eligible = [row for row in group if int(row["max_steps"]) >= step]
            if not eligible:
                continue
            successes = sum(row["stable_onset_step"] is not None and int(row["stable_onset_step"]) <= step for row in eligible)
            lower, upper = cp_interval(successes, len(eligible))
            rate_rows.append({
                "bottleneck_dim": dim,
                "step": step,
                "successes": successes,
                "n": len(eligible),
                "rate": successes / len(eligible),
                "ci95_lower": lower,
                "ci95_upper": upper,
            })
        dimension_summary.append({
            "bottleneck_dim": dim,
            "hidden_width": int(group[0]["hidden_width"]),
            "parameter_count": int(group[0]["parameter_count"]),
            "n": len(group),
            "event_count": len(onsets),
            "final_rate": len(onsets) / len(group),
            "empirical_median_onset": None if len(onsets) < math.ceil(len(group) / 2) else float(np.median(onsets)),
            "mean_first_hit": None if not any(row["first_hit_step"] is not None for row in group) else float(np.mean([row["first_hit_step"] for row in group if row["first_hit_step"] is not None])),
            "trajectories_with_more_than_one_relapse": sum(int(row["relapse_count_after_first_hit"]) > 1 for row in group),
            "mean_train_seconds": float(np.mean([row["train_seconds"] for row in group])),
        })

    weibull = fit_weibull(primary, [2, 3, 4, 6, 8])
    discrimination = edge_auc(primary)
    geometry = geometry_warning_auc(primary)
    crossed_analysis = crossed_variance(crossed)

    synchrony_flags: list[bool] = []
    synchrony_spreads: list[int] = []
    for row in primary:
        if row["stable_onset_step"] is None:
            continue
        checkpoint_rows = row["checkpoints"]
        crossings = [
            crossing_step(checkpoint_rows, "action_accuracy", 0.98),
            crossing_step(checkpoint_rows, "probe_accuracy", 0.95),
            crossing_step(checkpoint_rows, "patch_accuracy", 0.95),
        ]
        if all(value is not None for value in crossings):
            spread = max(crossings) - min(crossings)
            synchrony_spreads.append(int(spread))
            synchrony_flags.append(spread <= 150)

    emerged_checkpoints_by_dim: dict[int, list[float]] = defaultdict(list)
    for row in primary:
        dim = int(row["bottleneck_dim"])
        for checkpoint in row["checkpoints"]:
            if checkpoint["emergence"]:
                emerged_checkpoints_by_dim[dim].append(float(checkpoint["cut_accuracy"]))

    def rate_by(dim: int, step: int) -> float:
        group = [row for row in primary if int(row["bottleneck_dim"]) == dim]
        return sum(row["stable_onset_step"] is not None and int(row["stable_onset_step"]) <= step for row in group) / len(group)

    medians = {int(item["bottleneck_dim"]): item["empirical_median_onset"] for item in dimension_summary}
    parameter_deviation = max(abs(int(item["parameter_count"]) - 2480) / 2480 for item in dimension_summary)
    hit_rows = [row for row in primary if row["first_hit_step"] is not None]
    multi_relapse_rate = (sum(int(row["relapse_count_after_first_hit"]) > 1 for row in hit_rows) / len(hit_rows)) if hit_rows else 0.0
    endpoints = {
        "E01_parameter_match": parameter_deviation <= 0.05,
        "E02_dim1_no_edge": rate_by(1, 2400) <= 1 / 12,
        "E03_dim2_eventual": rate_by(2, 1400) >= 18 / 24,
        "E04_dim3_eventual": rate_by(3, 1000) >= 20 / 24,
        "E05_dim4_eventual": rate_by(4, 800) >= 20 / 24,
        "E06_overcomplete_eventual": max(rate_by(6, 800), rate_by(8, 800)) >= 20 / 24,
        "E07_dimension_acceleration": medians[2] is not None and medians[4] is not None and float(medians[4]) <= 0.8 * float(medians[2]),
        "E08_sustained_behavior": multi_relapse_rate < 0.10,
        "E09_cut_specificity": all(np.mean(values) <= 0.10 for dim, values in emerged_checkpoints_by_dim.items() if dim >= 2 and values),
        "E10_causal_synchrony": bool(synchrony_flags) and np.mean(synchrony_flags) >= 0.90,
        "E11_edge_model_discrimination": discrimination["auc"] >= 0.85,
        "E12_geometry_warning": geometry["auc"] is not None and float(geometry["auc"]) >= 0.80,
        "E13_crossed_variance": all(math.isfinite(float(crossed_analysis[key])) for key in ("eta_squared_initialization", "eta_squared_data_stream", "eta_squared_residual")),
        "E14_all_receipts": all(
            row.get("uses_intermediate_workspace_labels_for_training") is False
            and row.get("valence_model_present") is False
            and float(row.get("self_preservation_reward", 1.0)) == 0.0
            for row in primary + crossed
        ),
    }

    analysis = {
        "schema": "rrct.v055.workspace_emergence_edge.analysis.v1",
        "status": "V055_EDGE_ENDPOINTS_MET" if all(endpoints.values()) else "V055_EDGE_ENDPOINTS_PARTIALLY_MET",
        "endpoint_count": len(endpoints),
        "endpoints_passed": sum(endpoints.values()),
        "all_endpoints_met": all(endpoints.values()),
        "endpoints": endpoints,
        "primary_trajectory_count": len(primary),
        "crossed_trajectory_count": len(crossed),
        "dimension_summary": dimension_summary,
        "empirical_rates": rate_rows,
        "weibull_edge_model": weibull,
        "edge_discrimination": discrimination,
        "geometry_warning": geometry,
        "crossed_variance": crossed_analysis,
        "causal_synchrony": {
            "n": len(synchrony_flags),
            "rate_within_150_updates": float(np.mean(synchrony_flags)) if synchrony_flags else None,
            "median_spread": float(np.median(synchrony_spreads)) if synchrony_spreads else None,
            "maximum_spread": max(synchrony_spreads) if synchrony_spreads else None,
        },
        "multi_relapse_rate": multi_relapse_rate,
        "claim_boundary": "Parameter-matched, dense-checkpoint edge map for workspace semantics inside a supplied synthetic hierarchy. Not spontaneous hierarchy formation or awareness evidence.",
    }
    (RESULTS / "EDGE_ANALYSIS.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    pd.DataFrame(rate_rows).to_csv(RESULTS / "EDGE_RATES.csv", index=False)
    pd.DataFrame(dimension_summary).to_csv(RESULTS / "DIMENSION_SUMMARY.csv", index=False)

    # Figure 1: empirical CDFs.
    fig, ax = plt.subplots(figsize=(12, 7.5))
    rates = pd.DataFrame(rate_rows)
    for dim in dimensions:
        subset = rates[rates["bottleneck_dim"] == dim]
        ax.step(subset["step"], subset["rate"], where="post", label=f"D={dim}")
    ax.set_title("Stable Workspace-Onset Probability Along Continuous Training Trajectories")
    ax.set_xlabel("Terminal-only training updates")
    ax.set_ylabel("Fraction of seeds with stable onset")
    ax.set_ylim(-0.02, 1.05)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.savefig(FIGURES / "01_stable_onset_cdf.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: onset threshold vs dimension.
    fig, ax = plt.subplots(figsize=(10, 7))
    dims_fit = [2, 3, 4, 6, 8]
    s50 = [weibull["thresholds"][str(dim)]["s50"] for dim in dims_fit]
    s90 = [weibull["thresholds"][str(dim)]["s90"] for dim in dims_fit]
    ax.plot(dims_fit, s50, marker="o", label="fitted 50% onset")
    ax.plot(dims_fit, s90, marker="o", label="fitted 90% onset")
    ax.set_title("Parameter-Matched Emergence Frontier by Bottleneck Dimension")
    ax.set_xlabel("Bottleneck dimension")
    ax.set_ylabel("Training updates")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.savefig(FIGURES / "02_dimension_frontier.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Figure 3: order parameter trajectories.
    fig, ax = plt.subplots(figsize=(12, 7.5))
    for dim in dimensions:
        grouped: dict[int, list[float]] = defaultdict(list)
        for row in primary:
            if int(row["bottleneck_dim"]) != dim:
                continue
            for checkpoint in row["checkpoints"]:
                grouped[int(checkpoint["step"])].append(float(checkpoint["order_parameter"]))
        steps = sorted(grouped)
        means = [np.mean(grouped[step]) for step in steps]
        ax.plot(steps, means, marker=".", label=f"D={dim}")
    ax.set_title("Continuous Workspace Order Parameter")
    ax.set_xlabel("Training updates")
    ax.set_ylabel("min(task, probe, patch, 1-cut)")
    ax.set_ylim(0, 1.03)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.savefig(FIGURES / "03_order_parameter.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Figure 4: latent geometry warning.
    geometry_rows = []
    for row in primary:
        if int(row["bottleneck_dim"]) < 2:
            continue
        for checkpoint in row["checkpoints"]:
            if int(checkpoint["step"]) <= 800:
                geometry_rows.append({
                    "ratio": float(checkpoint["minimum_second_to_first_ratio"]),
                    "margin": float(checkpoint["emergence_margin"]),
                    "emergence": bool(checkpoint["emergence"]),
                    "dim": int(row["bottleneck_dim"]),
                })
    frame = pd.DataFrame(geometry_rows)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(frame["ratio"], frame["margin"], s=12, alpha=0.22)
    ax.axhline(0.0, linewidth=1.2)
    ax.set_title("Latent Rank Geometry and Emergence Margin")
    ax.set_xlabel("Minimum second / first singular-value ratio")
    ax.set_ylabel("Minimum frozen-threshold margin")
    ax.grid(alpha=0.2)
    fig.savefig(FIGURES / "04_geometry_warning.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Figure 5: crossed variance decomposition.
    labels = ["Initialization", "Data stream", "Residual"]
    values = [
        crossed_analysis["eta_squared_initialization"],
        crossed_analysis["eta_squared_data_stream"],
        crossed_analysis["eta_squared_residual"],
    ]
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.bar(labels, values)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Fraction of log-onset variation")
    ax.set_title("D=2 Crossed Diagnostic: What Drives Seed Variability?")
    ax.grid(axis="y", alpha=0.2)
    for index, value in enumerate(values):
        ax.text(index, value + 0.02, f"{value:.3f}", ha="center")
    fig.savefig(FIGURES / "05_crossed_variance.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps({
        "status": analysis["status"],
        "endpoints": f"{analysis['endpoints_passed']}/{analysis['endpoint_count']}",
        "edge_auc": discrimination["auc"],
        "geometry_auc": geometry["auc"],
        "weibull_shape": weibull["shape"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

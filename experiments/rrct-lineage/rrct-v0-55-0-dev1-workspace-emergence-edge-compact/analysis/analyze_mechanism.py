from __future__ import annotations

import json
import math
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.metrics import roc_auc_score, roc_curve

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)


def load(path: pathlib.Path) -> list[dict[str, object]]:
    return [json.loads(file.read_text()) for file in sorted(path.glob("*.json"))]


primary = load(RESULTS / "primary")
crossed = load(RESULTS / "crossed")
tail = load(RESULTS / "posthoc_d2_tail")
overcomplete = load(RESULTS / "overcomplete")
main_analysis = json.loads((RESULTS / "EDGE_ANALYSIS.json").read_text())

# Complete D=2 tail and all dimension summaries.
primary_by_dim: dict[int, list[dict[str, object]]] = {}
for dim in [1, 2, 3, 4, 6, 8]:
    primary_by_dim[dim] = [row for row in primary if int(row["bottleneck_dim"]) == dim]
primary_by_dim[2] = tail
extension_by_dim = {
    dim: [row for row in overcomplete if int(row["bottleneck_dim"]) == dim]
    for dim in [10, 12, 14, 16, 20]
}

all_dimension_rows: list[dict[str, object]] = []
for dim, rows in {**primary_by_dim, **extension_by_dim}.items():
    onsets = sorted(int(row["stable_onset_step"]) for row in rows if row["stable_onset_step"] is not None)
    all_dimension_rows.append({
        "bottleneck_dim": dim,
        "hidden_width": int(rows[0]["hidden_width"]),
        "parameter_count": int(rows[0]["parameter_count"]),
        "n": len(rows),
        "event_count": len(onsets),
        "median_onset": None if not onsets else float(np.median(onsets)),
        "mean_onset": None if not onsets else float(np.mean(onsets)),
        "p90_onset": None if not onsets else float(np.quantile(onsets, 0.9)),
        "onset_cv": None if len(onsets) < 2 else float(np.std(onsets, ddof=1) / np.mean(onsets)),
        "rate_by_400": sum(value <= 400 for value in onsets) / len(rows),
        "rate_by_800": sum(value <= 800 for value in onsets) / len(rows),
        "rate_by_1400": sum(value <= 1400 for value in onsets) / len(rows),
        "maximum_onset": None if not onsets else max(onsets),
    })
all_dimension_rows.sort(key=lambda item: int(item["bottleneck_dim"]))

# Rank opening and semantic-locking stages for the primary matched sweep.
rank_threshold = 0.5
two_stage_rows: list[dict[str, object]] = []
for dim in [2, 3, 4, 6, 8]:
    rows = primary_by_dim[dim]
    rank_steps: list[int] = []
    lock_lags: list[int] = []
    onset_steps: list[int] = []
    for row in rows:
        onset = row["stable_onset_step"]
        if onset is None:
            continue
        rank_step = next(
            (
                int(checkpoint["step"])
                for checkpoint in row["checkpoints"]
                if float(checkpoint["minimum_second_to_first_ratio"]) >= rank_threshold
            ),
            None,
        )
        if rank_step is None:
            continue
        rank_steps.append(rank_step)
        onset_steps.append(int(onset))
        lock_lags.append(int(onset) - rank_step)
    two_stage_rows.append({
        "bottleneck_dim": dim,
        "rank_opening_median": float(np.median(rank_steps)),
        "stable_onset_median": float(np.median(onset_steps)),
        "locking_delay_median": float(np.median(lock_lags)),
        "locking_delay_mean": float(np.mean(lock_lags)),
        "n": len(lock_lags),
    })

# Precursor threshold for onset within 200 steps.
y: list[int] = []
x: list[float] = []
for row in primary:
    if int(row["bottleneck_dim"]) < 2:
        continue
    onset = row["stable_onset_step"]
    for checkpoint in row["checkpoints"]:
        step = int(checkpoint["step"])
        if bool(checkpoint["emergence"]) or step > 800:
            continue
        y.append(int(onset is not None and step < int(onset) <= step + 200))
        x.append(float(checkpoint["minimum_second_to_first_ratio"]))
fpr, tpr, thresholds = roc_curve(y, x)
index = int(np.argmax(tpr - fpr))
rank_precursor = {
    "auc": float(roc_auc_score(y, x)),
    "youden_threshold": float(thresholds[index]),
    "sensitivity": float(tpr[index]),
    "false_positive_rate": float(fpr[index]),
    "n": len(y),
    "positive_count": int(sum(y)),
}

# Fit low-dimensional acceleration formulas to primary empirical medians.
primary_formula_data = [row for row in all_dimension_rows if int(row["bottleneck_dim"]) in [2, 3, 4, 6, 8]]
d_primary = np.asarray([row["bottleneck_dim"] for row in primary_formula_data], dtype=float)
t_primary = np.asarray([row["median_onset"] for row in primary_formula_data], dtype=float)


def asymptotic_formula(dim, floor, amplitude, exponent):
    return floor + amplitude * np.asarray(dim) ** (-exponent)


primary_parameters, _ = curve_fit(
    asymptotic_formula,
    d_primary,
    t_primary,
    p0=[175.0, 1000.0, 2.0],
    bounds=([0.0, 0.0, 0.01], [2000.0, 100000.0, 10.0]),
    maxfev=100000,
)
primary_prediction = asymptotic_formula(d_primary, *primary_parameters)
primary_formula = {
    "formula": "T50(D)=T_inf+A*D^(-alpha)",
    "T_inf": float(primary_parameters[0]),
    "A": float(primary_parameters[1]),
    "alpha": float(primary_parameters[2]),
    "rmse_updates": float(np.sqrt(np.mean((primary_prediction - t_primary) ** 2))),
}

# Fit a descriptive two-pressure formula across the full D/H sweep.
full_formula_data = [row for row in all_dimension_rows if int(row["bottleneck_dim"]) >= 2]
d_full = np.asarray([row["bottleneck_dim"] for row in full_formula_data], dtype=float)
h_full = np.asarray([row["hidden_width"] for row in full_formula_data], dtype=float)
t_full = np.asarray([row["median_onset"] for row in full_formula_data], dtype=float)


def goldilocks_formula(inputs, floor, amplitude, exponent, congestion, congestion_exponent):
    dim, hidden = inputs
    return (
        floor
        + amplitude * dim ** (-exponent)
        + congestion * (dim / hidden) ** congestion_exponent
    )


goldilocks_parameters, _ = curve_fit(
    goldilocks_formula,
    (d_full, h_full),
    t_full,
    p0=[200.0, 1500.0, 2.5, 0.02, 5.0],
    bounds=([0, 0, 0.01, 0, 0.01], [2000, 100000, 10, 100000, 10]),
    maxfev=100000,
)
goldilocks_prediction = goldilocks_formula((d_full, h_full), *goldilocks_parameters)
goldilocks = {
    "formula": "T50(D,H)=T0+A*D^(-alpha)+B*(D/H)^beta",
    "T0": float(goldilocks_parameters[0]),
    "A": float(goldilocks_parameters[1]),
    "alpha": float(goldilocks_parameters[2]),
    "B": float(goldilocks_parameters[3]),
    "beta": float(goldilocks_parameters[4]),
    "rmse_updates": float(np.sqrt(np.mean((goldilocks_prediction - t_full) ** 2))),
    "interpretation": "The first term penalizes insufficient representational slack; the final term penalizes a workspace too wide for its hidden transformation width. This is a post-outcome architecture-specific fit, not a universal law.",
}

# Extension endpoints.
extension_parameters_ok = max(
    abs(int(row["parameter_count"]) - 2480) / 2480 for row in all_dimension_rows if int(row["bottleneck_dim"]) >= 10
) <= 0.08
summary_by_dim = {int(row["bottleneck_dim"]): row for row in all_dimension_rows}
extension_endpoints = {
    "X01_parameter_match": extension_parameters_ok,
    "X02_dim10_continuity": summary_by_dim[10]["rate_by_800"] >= 9 / 12,
    "X03_high_dim_reversal": any(
        summary_by_dim[dim]["rate_by_800"] < 9 / 12
        or float(summary_by_dim[dim]["median_onset"]) > 200
        for dim in [12, 14, 16, 20]
    ),
    "X04_no_valence_or_labels": all(
        row.get("uses_intermediate_workspace_labels_for_training") is False
        and row.get("valence_model_present") is False
        and float(row.get("self_preservation_reward", 1.0)) == 0.0
        for row in overcomplete
    ),
}

mechanism = {
    "schema": "rrct.v055.workspace_emergence_mechanism.analysis.v1",
    "status": "V055_EDGE_MECHANISM_AND_OVERCOMPLETE_EXTENSION_COMPLETED",
    "primary_status": main_analysis["status"],
    "primary_endpoints": f"{main_analysis['endpoints_passed']}/{main_analysis['endpoint_count']}",
    "overcomplete_extension_endpoints": extension_endpoints,
    "overcomplete_extension_passed": sum(extension_endpoints.values()),
    "overcomplete_extension_total": len(extension_endpoints),
    "trajectory_counts": {
        "primary": len(primary),
        "crossed": len(crossed),
        "posthoc_d2_tail": len(tail),
        "prospective_overcomplete_extension": len(overcomplete),
        "total": len(primary) + len(crossed) + len(tail) + len(overcomplete),
    },
    "dimension_summary": all_dimension_rows,
    "two_stage_transition": {
        "rank_opening_threshold": rank_threshold,
        "rows": two_stage_rows,
        "rank_precursor": rank_precursor,
        "interpretation": "A second latent direction opens before task/probe/patch semantics causally lock. Increasing D shortens both the rank-opening time and the later locking delay.",
    },
    "low_dimension_formula": primary_formula,
    "goldilocks_formula": goldilocks,
    "crossed_variance": main_analysis["crossed_variance"],
    "d2_complete_tail": {
        "median": summary_by_dim[2]["median_onset"],
        "p90": summary_by_dim[2]["p90_onset"],
        "maximum": summary_by_dim[2]["maximum_onset"],
        "coefficient_of_variation": summary_by_dim[2]["onset_cv"],
    },
    "strongest_interpretation": "The edge is a two-sided Goldilocks frontier: D=1 lacks sufficient smooth state dimension; D=2 is sufficient but has a long optimization tail; D=4-12 gives robust representational slack; very large D combined with very narrow hidden transformations sharply slows stable causal locking.",
    "claim_boundary": "All formulas are descriptive for one supplied synthetic hierarchy. The study does not establish spontaneous hierarchy formation, a universal neural scaling law, or awareness.",
}
(RESULTS / "EDGE_MECHANISM_ANALYSIS.json").write_text(
    json.dumps(mechanism, indent=2, sort_keys=True) + "\n"
)
pd.DataFrame(all_dimension_rows).to_csv(RESULTS / "FULL_DIMENSION_EDGE.csv", index=False)
pd.DataFrame(two_stage_rows).to_csv(RESULTS / "TWO_STAGE_TRANSITION.csv", index=False)

# Figure 6: complete dimension edge with p90.
frame = pd.DataFrame(all_dimension_rows)
fig, ax = plt.subplots(figsize=(12, 7.5))
ax.plot(frame["bottleneck_dim"], frame["median_onset"], marker="o", label="median stable onset")
ax.plot(frame["bottleneck_dim"], frame["p90_onset"], marker="o", label="90th percentile onset")
ax.set_title("The Full Parameter-Matched Edge: Too Narrow, Goldilocks Plateau, Then Congestion")
ax.set_xlabel("Workspace bottleneck dimension D")
ax.set_ylabel("Training updates to stable causal workspace")
ax.grid(alpha=0.2)
ax.legend()
fig.savefig(FIGURES / "06_full_goldilocks_edge.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Figure 7: two-stage transition.
stage = pd.DataFrame(two_stage_rows)
fig, ax = plt.subplots(figsize=(11, 7))
ax.plot(stage["bottleneck_dim"], stage["rank_opening_median"], marker="o", label="second latent direction opens")
ax.plot(stage["bottleneck_dim"], stage["stable_onset_median"], marker="o", label="full causal workspace locks")
ax.fill_between(
    stage["bottleneck_dim"].to_numpy(),
    stage["rank_opening_median"].to_numpy(),
    stage["stable_onset_median"].to_numpy(),
    alpha=0.15,
    label="semantic/causal locking interval",
)
ax.set_title("Workspace Emergence Is a Two-Stage Transition")
ax.set_xlabel("Bottleneck dimension")
ax.set_ylabel("Training updates")
ax.grid(alpha=0.2)
ax.legend()
fig.savefig(FIGURES / "07_two_stage_transition.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Figure 8: crossed onset matrix.
cross_frame = pd.DataFrame([
    {
        "init": str(row["initialization_seed"]),
        "data": str(row["data_seed"]),
        "onset": row["stable_onset_step"] if row["stable_onset_step"] is not None else 1500,
    }
    for row in crossed
])
pivot = cross_frame.pivot(index="init", columns="data", values="onset")
fig, ax = plt.subplots(figsize=(9, 7))
image = ax.imshow(pivot.to_numpy(), aspect="auto")
ax.set_title("D=2 Onset Depends on Initialization × Data-Order Interaction")
ax.set_xlabel("Data-stream seed")
ax.set_ylabel("Initialization seed")
ax.set_xticks(np.arange(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
ax.set_yticks(np.arange(len(pivot.index)))
ax.set_yticklabels(pivot.index)
for row_index in range(pivot.shape[0]):
    for col_index in range(pivot.shape[1]):
        ax.text(col_index, row_index, int(pivot.iloc[row_index, col_index]), ha="center", va="center", fontsize=8)
fig.colorbar(image, ax=ax, label="Stable onset updates; 1500 = censored at 1400")
fig.savefig(FIGURES / "08_crossed_onset_matrix.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Figure 9: formula calibration across the full edge.
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(t_full, goldilocks_prediction, s=70)
minimum = min(float(t_full.min()), float(goldilocks_prediction.min()))
maximum = max(float(t_full.max()), float(goldilocks_prediction.max()))
ax.plot([minimum, maximum], [minimum, maximum], linewidth=1.3)
for dim, actual, predicted in zip(d_full, t_full, goldilocks_prediction):
    ax.annotate(f"D={int(dim)}", (actual, predicted), xytext=(5, 4), textcoords="offset points")
ax.set_title("Post-Outcome Two-Pressure Formula Calibration")
ax.set_xlabel("Observed median onset")
ax.set_ylabel("Formula-predicted median onset")
ax.grid(alpha=0.2)
fig.savefig(FIGURES / "09_goldilocks_formula_calibration.png", dpi=220, bbox_inches="tight")
plt.close(fig)

print(json.dumps({
    "status": mechanism["status"],
    "primary_endpoints": mechanism["primary_endpoints"],
    "extension_endpoints": f"{mechanism['overcomplete_extension_passed']}/{mechanism['overcomplete_extension_total']}",
    "rank_precursor_auc": rank_precursor["auc"],
    "rank_precursor_threshold": rank_precursor["youden_threshold"],
    "goldilocks_rmse": goldilocks["rmse_updates"],
}, indent=2))

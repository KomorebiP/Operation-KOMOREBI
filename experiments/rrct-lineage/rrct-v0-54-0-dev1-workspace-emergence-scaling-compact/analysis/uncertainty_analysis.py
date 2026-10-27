from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
frame = pd.read_csv(ROOT / "holdout_results/HOLDOUT_POINTS.csv")
rows: list[dict[str, float | int]] = []
for (dim, hidden, steps), group in frame.groupby(
    ["bottleneck_dim", "hidden_width", "steps"]
):
    successes = int(group.emergence.sum())
    n = int(len(group))
    lower = 0.0 if successes == 0 else float(beta.ppf(0.025, successes, n - successes + 1))
    upper = 1.0 if successes == n else float(beta.ppf(0.975, successes + 1, n - successes))
    rows.append(
        {
            "bottleneck_dim": int(dim),
            "hidden_width": int(hidden),
            "steps": int(steps),
            "successes": successes,
            "n": n,
            "observed_rate": successes / n,
            "clopper_pearson_95_lower": lower,
            "clopper_pearson_95_upper": upper,
            "mean_action_accuracy": float(group.action_accuracy.mean()),
            "mean_probe_accuracy": float(group.probe_accuracy.mean()),
            "mean_patch_accuracy": float(group.patch_accuracy.mean()),
            "mean_cut_accuracy": float(group.cut_accuracy.mean()),
        }
    )
payload = {
    "schema": "rrct.v054.uncertainty_analysis.v1",
    "interpretation": (
        "Exact binomial intervals are broad because each frozen configuration has four seeds. "
        "The logistic scaling surface should be treated as an ordering and interpolation device, "
        "not a precise universal probability law."
    ),
    "configurations": rows,
}
(ROOT / "holdout_results/UNCERTAINTY_ANALYSIS.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

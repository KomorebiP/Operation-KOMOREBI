from __future__ import annotations

"""Create concise JSON and Markdown summaries of the fitted Bayesian model."""

import argparse
import json
from pathlib import Path
from typing import Any


def beta_mean(value: dict[str, float]) -> float:
    return float(value["alpha"]) / max(1e-12, float(value["alpha"]) + float(value["beta"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    calibration = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    family_rows = []
    for family, prior in calibration["family_priors"].items():
        if family == "__unknown__":
            continue
        family_rows.append({
            "family": family,
            "posterior_mean": beta_mean(prior),
            "alpha": float(prior["alpha"]),
            "beta": float(prior["beta"]),
            "effective_count": float(prior["alpha"]) + float(prior["beta"]) - 2.0,
        })
    family_rows.sort(key=lambda row: (-row["posterior_mean"], -row["effective_count"], row["family"]))

    regression = calibration.get("regression") or {}
    coefficient_rows = []
    for name, coefficient in zip(regression.get("feature_names", []), regression.get("coefficient_mean", []), strict=False):
        coefficient_rows.append({"feature": name, "coefficient": float(coefficient)})
    coefficient_rows.sort(key=lambda row: (-abs(row["coefficient"]), row["feature"]))

    summary: dict[str, Any] = {
        "model_version": calibration.get("model_version"),
        "training_metadata": calibration.get("training_metadata"),
        "calibration_evaluation": report.get("calibration_evaluation"),
        "parameter_holdout_evaluation": report.get("locked_training_holdout_evaluation"),
        "family_reliability": family_rows,
        "largest_standardized_regression_coefficients": coefficient_rows[:25],
        "regression_feature_count": len(regression.get("feature_names", [])),
        "regression_posterior_shape": regression.get("posterior_shape"),
        "regression_posterior_scale": regression.get("posterior_scale"),
    }
    Path(args.json_output).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    calibration_eval = summary["calibration_evaluation"] or {}
    holdout_eval = summary["parameter_holdout_evaluation"] or {}
    lines = [
        "# Bayesian PR-LASM calibration summary",
        "",
        f"**Model:** `{summary['model_version']}`",
        "",
        "## Partition results",
        "",
        "| Partition | Tasks | Whole tasks exact | Outputs exact | Output rate |",
        "|---|---:|---:|---:|---:|",
        f"| Calibration | {calibration_eval.get('tasks')} | {calibration_eval.get('whole_tasks_correct')} | {calibration_eval.get('outputs_correct')}/{calibration_eval.get('outputs_total')} | {float(calibration_eval.get('score') or 0):.4%} |",
        f"| Parameter holdout | {holdout_eval.get('tasks')} | {holdout_eval.get('whole_tasks_correct')} | {holdout_eval.get('outputs_correct')}/{holdout_eval.get('outputs_total')} | {float(holdout_eval.get('score') or 0):.4%} |",
        "",
        "## Highest family reliability posterior means",
        "",
        "| Family | Mean | Effective candidate records |",
        "|---|---:|---:|",
    ]
    for row in family_rows[:20]:
        lines.append(f"| `{row['family']}` | {row['posterior_mean']:.4f} | {row['effective_count']:.1f} |")
    lines.extend([
        "",
        "## Largest standardized reliability coefficients",
        "",
        "| Feature | Coefficient |",
        "|---|---:|",
    ])
    for row in coefficient_rows[:20]:
        lines.append(f"| `{row['feature']}` | {row['coefficient']:.5f} |")
    lines.extend([
        "",
        "The parameter holdout is excluded from the fitted calibration file. It is a machine-level parameter holdout, not a claim that the tasks were historically unseen by all earlier project versions.",
        "",
    ])
    Path(args.markdown_output).write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

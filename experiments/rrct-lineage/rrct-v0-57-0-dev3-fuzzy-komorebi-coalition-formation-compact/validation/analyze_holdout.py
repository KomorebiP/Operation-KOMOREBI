from __future__ import annotations

import csv
import json
import pathlib
import statistics
import sys
from collections import defaultdict

import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import fuzzy_komorebi as fk


def mean(values: list[float]) -> float:
    return float(statistics.mean(values))


def maximum(values: list[float]) -> float:
    return float(max(values))


def minimum(values: list[float]) -> float:
    return float(min(values))


seed_receipt = json.loads((ROOT / "validation/HOLDOUT_SEED_SELECTION.json").read_text())
seeds = [int(value) for value in seed_receipt["holdout_seeds"]]
rows: list[dict[str, object]] = []
by_variant: dict[str, list[dict[str, object]]] = defaultdict(list)
for seed in seeds:
    for variant in ("fuzzy", "hard", "direct", "crystal"):
        path = ROOT / f"results/holdout/{variant}_{seed}.json"
        payload = json.loads(path.read_text())
        rows.append(payload)
        by_variant[variant].append(payload)

fuzzy = [row["result"] for row in by_variant["fuzzy"]]
hard = [row["result"] for row in by_variant["hard"]]
direct = [row["result"] for row in by_variant["direct"]]
crystal = [row["result"] for row in by_variant["crystal"]]

summary: dict[str, object] = {
    "schema": "rrct.v057.holdout_summary.v1",
    "version": "0.57.0.dev3",
    "holdout_seeds": seeds,
    "seed_count": len(seeds),
    "models_trained": len(rows),
}

for variant, variant_rows in by_variant.items():
    results = [row["result"] for row in variant_rows]
    summary[variant] = {
        "mean_mse": mean([float(r["mse"]) for r in results]),
        "max_mse": maximum([float(r["mse"]) for r in results]),
        "mean_strict_accuracy": mean([float(r["strict_accuracy"]) for r in results]),
        "mean_crisp_mse": mean([float(r["crisp_mse"]) for r in results]),
        "mean_familiar_blend_mse": mean([float(r["familiar_blend_mse"]) for r in results]),
        "mean_diffuse_mse": mean([float(r["diffuse_mse"]) for r in results]),
        "mean_novel_blend_mse": mean([float(r["novel_blend_mse"]) for r in results]),
        "max_novel_blend_mse": maximum([float(r["novel_blend_mse"]) for r in results]),
        "mean_novel_blend_strict_accuracy": mean(
            [float(r["novel_blend_strict_accuracy"]) for r in results]
        ),
    }

fuzzy_summary = summary["fuzzy"]
hard_summary = summary["hard"]
direct_summary = summary["direct"]
crystal_summary = summary["crystal"]
assert isinstance(fuzzy_summary, dict)
assert isinstance(hard_summary, dict)
assert isinstance(direct_summary, dict)
assert isinstance(crystal_summary, dict)

entropy_separation = [
    float(r["novel_blend_membership_entropy"]) - float(r["crisp_membership_entropy"])
    for r in fuzzy
]
idempotence_separation = [
    float(r["novel_blend_idempotence_defect"]) - float(r["crisp_idempotence_defect"])
    for r in fuzzy
]
correlations = [float(r["idempotence_target_correlation"]) for r in fuzzy]
causal_correlations = [
    float(r["causal_membership"]["membership_effect_correlation"]) for r in fuzzy
]
top_effects = [
    float(r["causal_membership"]["top_quartile_ablation_effect"]) for r in fuzzy
]
partition_errors = [
    float(r["packet_diagnostics"]["maximum_partition_error"]) for r in fuzzy
]
reconstruction_errors = [
    float(r["packet_diagnostics"]["maximum_block_reconstruction_relative_error"])
    for r in fuzzy
]
transport_errors = [
    float(r["packet_diagnostics"]["maximum_permutation_transport_error"]) for r in fuzzy
]
min_eigenvalues = [
    float(r["packet_diagnostics"]["minimum_packet_eigenvalue"]) for r in fuzzy
]

fuzzy_novel = float(fuzzy_summary["mean_novel_blend_mse"])
hard_novel = float(hard_summary["mean_novel_blend_mse"])
direct_mse = float(direct_summary["mean_mse"])
fuzzy_mse = float(fuzzy_summary["mean_mse"])
oracle_hard_novel = mean([float(r["oracle_hard_novel_blend_mse"]) for r in fuzzy])
oracle_hard_crisp = mean([float(r["oracle_hard_crisp_mse"]) for r in fuzzy])
crispified_novel = mean(
    [float(r["predicted_crispification_novel_blend_mse"]) for r in fuzzy]
)

crisp_entropy_drop: list[float] = []
final_fuzzy_minus_crisp: list[float] = []
for row in by_variant["fuzzy"]:
    curve = row["curve"]
    start = curve.get("100") or curve.get(100)
    final = curve.get("2000") or curve.get(2000)
    if start is None or final is None:
        raise RuntimeError("frozen fuzzy trajectory lacks step 100 or step 2000")
    crisp_entropy_drop.append(float(start["crisp_entropy"]) - float(final["crisp_entropy"]))
    final_fuzzy_minus_crisp.append(
        float(final["fuzzy_entropy"]) - float(final["crisp_entropy"])
    )

endpoints = {
    "fuzzy_mean_mse_at_most_0_0012": fuzzy_mse <= 0.0012,
    "fuzzy_max_mse_at_most_0_002": float(fuzzy_summary["max_mse"]) <= 0.002,
    "fuzzy_mean_midblend_mse_at_most_0_002": fuzzy_novel <= 0.002,
    "fuzzy_max_midblend_mse_at_most_0_004": float(fuzzy_summary["max_novel_blend_mse"]) <= 0.004,
    "fuzzy_crisp_mse_at_most_0_0002": float(fuzzy_summary["mean_crisp_mse"]) <= 0.0002,
    "fuzzy_beats_oracle_crispification_by_12_5x": fuzzy_novel <= 0.08 * oracle_hard_novel,
    "hardening_causes_at_least_30x_midblend_error": crispified_novel >= 30.0 * fuzzy_novel,
    "learned_hard_model_at_least_20x_worse": hard_novel >= 20.0 * fuzzy_novel,
    "direct_edge_mean_mse_at_most_0_001": direct_mse <= 0.001,
    "direct_edge_is_competitive": direct_mse <= 1.10 * fuzzy_mse,
    "fuzzy_within_3x_direct_edge": fuzzy_mse <= 3.0 * direct_mse,
    "entropy_separates_crisp_and_overlap": mean(entropy_separation) >= 0.45 and minimum(entropy_separation) >= 0.35,
    "idempotence_defect_separates_crisp_and_overlap": mean(idempotence_separation) >= 0.25 and minimum(idempotence_separation) >= 0.20,
    "idempotence_tracks_target_fuzziness": mean(correlations) >= 0.85 and minimum(correlations) >= 0.80,
    "membership_strength_is_causally_calibrated": mean(causal_correlations) >= 0.45 and minimum(causal_correlations) >= 0.40,
    "high_membership_ablation_is_material": mean(top_effects) >= 0.02 and minimum(top_effects) >= 0.015,
    "fuzzy_packet_partition_certified": maximum(partition_errors) <= 1e-5,
    "fuzzy_transfer_blocks_reconstruct": maximum(reconstruction_errors) <= 1e-5,
    "fuzzy_packets_transport_covariantly": maximum(transport_errors) <= 1e-6,
    "fuzzy_packets_are_positive": minimum(min_eigenvalues) >= -1e-6,
    "oracle_hard_is_exact_only_on_crisp_tasks": oracle_hard_crisp <= 1e-7 and oracle_hard_novel >= 0.02,
    "training_sharpens_crisp_but_retains_fuzzy_state": mean(crisp_entropy_drop) >= 0.10 and mean(final_fuzzy_minus_crisp) >= 0.40,
}

summary.update(
    {
        "fuzzy_diagnostics": {
            "mean_entropy_separation": mean(entropy_separation),
            "minimum_entropy_separation": minimum(entropy_separation),
            "mean_idempotence_separation": mean(idempotence_separation),
            "minimum_idempotence_separation": minimum(idempotence_separation),
            "mean_idempotence_target_correlation": mean(correlations),
            "minimum_idempotence_target_correlation": minimum(correlations),
            "mean_causal_membership_correlation": mean(causal_correlations),
            "minimum_causal_membership_correlation": minimum(causal_correlations),
            "mean_top_quartile_ablation_effect": mean(top_effects),
            "minimum_top_quartile_ablation_effect": minimum(top_effects),
            "maximum_partition_error": maximum(partition_errors),
            "maximum_block_reconstruction_error": maximum(reconstruction_errors),
            "maximum_transport_error": maximum(transport_errors),
            "minimum_packet_eigenvalue": minimum(min_eigenvalues),
            "mean_crisp_entropy_drop_100_to_2000": mean(crisp_entropy_drop),
            "mean_final_fuzzy_minus_crisp_entropy": mean(final_fuzzy_minus_crisp),
            "oracle_hard_crisp_mse": oracle_hard_crisp,
            "oracle_hard_novel_blend_mse": oracle_hard_novel,
            "predicted_crispification_novel_blend_mse": crispified_novel,
            "fuzzy_to_oracle_hard_novel_ratio": fuzzy_novel / oracle_hard_novel,
            "crispification_to_fuzzy_novel_ratio": crispified_novel / fuzzy_novel,
            "learned_hard_to_fuzzy_novel_ratio": hard_novel / fuzzy_novel,
            "fuzzy_to_direct_mse_ratio": fuzzy_mse / direct_mse,
        },
        "crystallization_exploratory": {
            "mean_mse": float(crystal_summary["mean_mse"]),
            "mean_novel_blend_mse": float(crystal_summary["mean_novel_blend_mse"]),
            "mean_crisp_idempotence_defect": mean(
                [float(r["crisp_idempotence_defect"]) for r in crystal]
            ),
            "mean_novel_idempotence_defect": mean(
                [float(r["novel_blend_idempotence_defect"]) for r in crystal]
            ),
            "interpretation": "Exploratory uniform idempotence pressure; not a frozen endpoint.",
        },
        "endpoints": endpoints,
        "endpoint_count": len(endpoints),
        "passed_endpoint_count": sum(bool(value) for value in endpoints.values()),
        "all_endpoints_met": all(endpoints.values()),
        "status": "V057_FROZEN_ENDPOINTS_MET" if all(endpoints.values()) else "V057_FROZEN_ENDPOINTS_NOT_MET",
        "claim_boundary": "Bounded terminal-action test of fuzzy packet and edge matrices. No biological-brain, functional-awareness, consciousness, sentience, or valence claim.",
    }
)

# CSV: one row per trained model.
csv_path = ROOT / "results/HOLDOUT_MODELS.csv"
fieldnames = [
    "variant", "seed", "mse", "strict_accuracy", "crisp_mse",
    "familiar_blend_mse", "diffuse_mse", "novel_blend_mse",
    "novel_blend_strict_accuracy", "elapsed_seconds",
]
with csv_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        result = row["result"]
        writer.writerow(
            {
                "variant": row["variant"],
                "seed": row["seed"],
                "mse": result["mse"],
                "strict_accuracy": result["strict_accuracy"],
                "crisp_mse": result["crisp_mse"],
                "familiar_blend_mse": result["familiar_blend_mse"],
                "diffuse_mse": result["diffuse_mse"],
                "novel_blend_mse": result["novel_blend_mse"],
                "novel_blend_strict_accuracy": result["novel_blend_strict_accuracy"],
                "elapsed_seconds": row["elapsed_seconds"],
            }
        )

fk.write_json(ROOT / "results/HOLDOUT_SUMMARY.json", summary)
fk.write_json(
    ROOT / "results/HOLDOUT_ANALYSIS.json",
    {
        "schema": "rrct.v057.holdout_analysis.v1",
        "summary": summary,
        "models": rows,
    },
)

report = f"""# RRCT v0.57 Fuzzy Komorebi Coalition Formation Report

## Status

`{summary['status']}`

Frozen endpoints: **{summary['passed_endpoint_count']} of {summary['endpoint_count']} passed**.

## Primary result

The terminally trained fuzzy packet model achieved mean MSE **{fuzzy_mse:.6g}** and held-out central-blend MSE **{fuzzy_novel:.6g}**. The oracle hard projection of the same true task memberships had central-blend MSE **{oracle_hard_novel:.6g}**, while hardening the learned fuzzy memberships produced MSE **{crispified_novel:.6g}**.

The direct-edge model achieved mean MSE **{direct_mse:.6g}**. It is therefore a competitive and slightly stronger predictive baseline; the frozen result supports graded relational structure and structured packet diagnostics, not unique predictive superiority of the packet factorization.

## Fuzzy geometry

- Mean entropy separation, overlap minus crisp: **{mean(entropy_separation):.6f}**
- Mean idempotence-defect separation: **{mean(idempotence_separation):.6f}**
- Mean idempotence-to-target correlation: **{mean(correlations):.6f}**
- Mean membership-to-ablation correlation: **{mean(causal_correlations):.6f}**
- Maximum packet partition error: **{maximum(partition_errors):.3e}**
- Maximum fuzzy block reconstruction error: **{maximum(reconstruction_errors):.3e}**
- Maximum permutation transport error: **{maximum(transport_errors):.3e}**

## Interpretation

Within this synthetic task family, fuzzy matrix entries are causally meaningful. Crisp tasks induce relatively sharper packet geometry, whereas overlap tasks retain non-idempotent memberships. Forcing hard assignments destroys the graded cases while preserving the exact crisp oracle cases.

The experiment does not establish that fuzzy Komorebi matrices are uniquely optimal, that the brain implements these matrices, or that the tested system is aware or conscious.
"""
(ROOT / "RESULT_REPORT.md").write_text(report, encoding="utf-8")
print(json.dumps({"status": summary["status"], "passed": summary["passed_endpoint_count"], "total": summary["endpoint_count"], "endpoints": endpoints}, indent=2, sort_keys=True))

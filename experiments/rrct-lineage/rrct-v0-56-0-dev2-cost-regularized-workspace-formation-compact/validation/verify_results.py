#!/usr/bin/env python3
"""Verify the canonical v0.56 result cells and aggregate analysis."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Any

import numpy as np
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import workspace_formation as wf  # noqa: E402

LAMBDAS = (0.0, 0.01, 0.03, 0.05, 0.08, 0.12, 0.16, 0.20, 0.22, 0.24, 0.26, 0.30, 0.40)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def mean(key: str) -> float:
        return float(np.mean([float(row[key]) for row in rows]))

    return {
        "seed_count": len(rows),
        "mean_task_accuracy": mean("task_accuracy"),
        "minimum_task_accuracy": min(float(row["task_accuracy"]) for row in rows),
        "mean_route_accuracy": mean("route_accuracy"),
        "minimum_route_accuracy": min(float(row["route_accuracy"]) for row in rows),
        "mean_cost": mean("mean_cost"),
        "mean_oracle_cost": mean("oracle_cost"),
        "mean_excess_cost": mean("excess_cost"),
        "maximum_absolute_excess_cost": max(abs(float(row["excess_cost"])) for row in rows),
        "mean_shuffled_cue_task_accuracy": mean("shuffled_cue_task_accuracy") if "shuffled_cue_task_accuracy" in rows[0] else None,
        "mean_shuffled_cue_route_accuracy": mean("shuffled_cue_route_accuracy") if "shuffled_cue_route_accuracy" in rows[0] else None,
        "mean_dissolution_accuracy": mean("dissolution_accuracy") if "dissolution_accuracy" in rows[0] else None,
        "mean_graph_switch_accuracy": mean("graph_switch_accuracy") if "graph_switch_accuracy" in rows[0] else None,
        "mean_route_patch_change_rate": mean("route_patch_change_rate") if "route_patch_change_rate" in rows[0] else None,
        "route_by_task": np.mean(np.asarray([row["route_by_task"] for row in rows], dtype=float), axis=0).tolist(),
        "accuracy_by_task": (
            np.mean(np.asarray([row["accuracy_by_task"] for row in rows], dtype=float), axis=0).tolist()
            if "accuracy_by_task" in rows[0]
            else None
        ),
    }


def close(a: Any, b: Any, tolerance: float = 1e-12) -> bool:
    if a is None or b is None:
        return a is b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y, tolerance) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance
    return a == b


def main() -> int:
    result_root = ROOT / "results"
    receipt = json.loads((ROOT / "validation/HOLDOUT_SEED_SELECTION.json").read_text(encoding="utf-8"))
    analysis = json.loads((result_root / "ANALYSIS.json").read_text(encoding="utf-8"))
    manifest = json.loads((result_root / "RESULT_SHA256.json").read_text(encoding="utf-8"))

    expected_names = {"ANALYSIS.json", "COST_EDGE.csv"}
    expected_names.update(f"primary_seed_{seed}.json" for seed in receipt["primary_seeds"])
    expected_names.update(f"naive_seed_{seed}.json" for seed in receipt["edge_seeds"])
    expected_names.update(
        f"edge_l{lambda_cost:.2f}_seed_{seed}.json"
        for lambda_cost in LAMBDAS
        for seed in receipt["edge_seeds"]
    )

    checks: dict[str, bool] = {}
    checks["analysis_status"] = analysis.get("status") == "V056_CONFIRMATION_ENDPOINTS_MET"
    checks["all_endpoints"] = bool(analysis.get("all_endpoints_met"))
    checks["endpoint_count"] = analysis.get("endpoint_count") == 23 and len(analysis.get("endpoints", {})) == 23
    checks["all_endpoint_values"] = all(bool(value) for value in analysis.get("endpoints", {}).values())
    checks["primary_seed_binding"] = analysis.get("primary_seeds") == receipt["primary_seeds"]
    checks["edge_seed_binding"] = analysis.get("edge_seeds") == receipt["edge_seeds"]
    checks["result_file_set"] = set(manifest.get("files", {})) == expected_names
    checks["manifest_file_count"] = manifest.get("file_count") == len(expected_names)

    for name, metadata in manifest.get("files", {}).items():
        path = result_root / name
        checks[f"present::{name}"] = path.is_file()
        checks[f"size::{name}"] = bool(path.is_file() and path.stat().st_size == metadata["size_bytes"])
        checks[f"sha256::{name}"] = bool(path.is_file() and sha256(path) == metadata["sha256"])

    primary_rows = [
        json.loads((result_root / f"primary_seed_{seed}.json").read_text(encoding="utf-8"))
        for seed in receipt["primary_seeds"]
    ]
    primary_recomputed = aggregate(primary_rows)
    checks["primary_aggregate_recomputed"] = close(primary_recomputed, analysis["primary"])
    checks["primary_lambda"] = all(abs(float(row["lambda_cost"]) - 0.12) <= 1e-15 for row in primary_rows)
    checks["no_task_index"] = all(not bool(row["router_uses_task_ids"]) for row in primary_rows)
    checks["no_valence"] = all(not bool(row["valence_model_present"]) for row in primary_rows)
    checks["no_self_preservation"] = all(float(row["self_preservation_reward"]) == 0.0 for row in primary_rows)

    edge_recomputed = []
    for lambda_cost in LAMBDAS:
        rows = [
            json.loads((result_root / f"edge_l{lambda_cost:.2f}_seed_{seed}.json").read_text(encoding="utf-8"))
            for seed in receipt["edge_seeds"]
        ]
        aggregate_row = aggregate(rows)
        aggregate_row["lambda_cost"] = lambda_cost
        edge_recomputed.append(aggregate_row)
    checks["edge_aggregate_recomputed"] = close(edge_recomputed, analysis["cost_edge"])

    naive_rows = [
        json.loads((result_root / f"naive_seed_{seed}.json").read_text(encoding="utf-8"))
        for seed in receipt["edge_seeds"]
    ]
    checks["naive_aggregate_recomputed"] = close(aggregate(naive_rows), analysis["naive_expected_loss_control"])

    sample = wf.sample_batch(120000, torch.Generator().manual_seed(560562), 0.0)
    losses = wf.route_losses(sample["routes"], sample["target"])
    break_even: dict[str, float | None] = {}
    for task in range(6):
        if task == 0:
            value = None
        else:
            mask = sample["task_ids"] == task
            value = float((losses[mask, 0] - losses[mask, task]).mean()) / float(
                wf.ROUTE_COSTS[task] - wf.ROUTE_COSTS[0]
            )
        break_even[wf.TASK_NAMES[task]] = value
    checks["break_even_recomputed"] = close(break_even, analysis["break_even_lambda"])
    checks["goldilocks_band"] = analysis.get("goldilocks_cost_band") == [0.03, 0.22]
    checks["first_underformation"] = abs(float(analysis["first_underformation"]["lambda_cost"]) - 0.24) <= 1e-15

    payload = {
        "schema": "rrct.v056.result_verification.v1",
        "status": "V056_RESULTS_VERIFIED" if all(checks.values()) else "V056_RESULTS_FAILED",
        "analysis_sha256": sha256(result_root / "ANALYSIS.json"),
        "result_manifest_sha256": sha256(result_root / "RESULT_SHA256.json"),
        "expected_result_files": len(expected_names),
        "checks_passed": sum(bool(value) for value in checks.values()),
        "check_count": len(checks),
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

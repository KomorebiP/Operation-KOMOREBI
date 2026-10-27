#!/usr/bin/env python3
"""Execute the sealed RRCT v0.49 trained-transformer holdout."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(root: Path) -> dict[str, Any]:
    path = root / "validation/V0_49_PREOUTCOME_FREEZE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    failed: list[str] = []
    for item in payload["files"]:
        candidate = root / item["relative_path"]
        if (
            not candidate.is_file()
            or candidate.stat().st_size != item["size_bytes"]
            or sha256(candidate) != item["sha256"]
        ):
            failed.append(item["relative_path"])
    companion = path.with_suffix(path.suffix + ".sha256")
    companion_matches = (
        companion.is_file()
        and companion.read_text(encoding="utf-8").split()[0] == sha256(path)
    )
    result = {
        "manifest_sha256": sha256(path),
        "file_count": len(payload["files"]),
        "failed_files": failed,
        "companion_matches": companion_matches,
        "all_checks_pass": not failed and companion_matches,
    }
    if not result["all_checks_pass"]:
        raise RuntimeError(f"v0.49 source freeze failed: {result}")
    return result


def compact_summary(full: dict[str, Any]) -> dict[str, Any]:
    analyses = []
    for item in full["analyses"]:
        late = item["late_workspace"]
        analyses.append(
            {
                "seed": item["seed"],
                "training_step": item["training_step"],
                "model_sha256": item["model_sha256"],
                "base_min_accuracy": item["base_min_accuracy"],
                "h1": item["stage_metrics"]["h1"],
                "h2": item["stage_metrics"]["h2"],
                "h3": item["stage_metrics"]["h3"],
                "late_workspace": {
                    "rank": late["rank"],
                    "row_rank_a": late["row_rank_a"],
                    "row_rank_b": late["row_rank_b"],
                    "alignment_r2": late["alignment_r2"],
                    "variance_fraction_a": late["variance_fraction_a"],
                    "variance_fraction_b": late["variance_fraction_b"],
                    "j_probes_a": late["j_probes_a"],
                    "j_probes_b": late["j_probes_b"],
                    "pca_probes_a": late["pca_probes_a"],
                    "pca_probes_b": late["pca_probes_b"],
                    "random_probes_a": late["random_probes_a"],
                    "random_probes_b": late["random_probes_b"],
                    "direct_ablation_shared_mean": late[
                        "direct_ablation_shared_mean"
                    ],
                    "direct_ablation_private_mean": late[
                        "direct_ablation_private_mean"
                    ],
                    "two_round_recovery_shared_mean": late[
                        "two_round_recovery_shared_mean"
                    ],
                    "two_round_recovery_private_mean": late[
                        "two_round_recovery_private_mean"
                    ],
                    "patch_both_a": late["patch_both_a"],
                    "patch_both_b": late["patch_both_b"],
                    "a_only_to_b_round1": late["a_only_to_b_round1"],
                    "a_only_back_to_a_round2": late[
                        "a_only_back_to_a_round2"
                    ],
                    "b_only_to_a_round1": late["b_only_to_a_round1"],
                    "b_only_back_to_b_round2": late[
                        "b_only_back_to_b_round2"
                    ],
                    "message_only_joint_accuracy": late[
                        "message_only_joint_accuracy"
                    ],
                },
            }
        )
    payload = {
        key: value
        for key, value in full.items()
        if key not in {"analyses", "digest"}
    }
    payload["analyses"] = analyses
    unsigned = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    payload["digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
    return payload


def write_rows(path: Path, summary: dict[str, Any]) -> None:
    fields = [
        "seed",
        "training_step",
        "base_min_accuracy",
        "h1_jscore_mean",
        "h1_alignment_r2",
        "h1_ablation_shared_mean",
        "h3_jscore_min",
        "h3_alignment_r2",
        "h3_variance_a",
        "h3_variance_b",
        "late_alignment_r2",
        "late_j_private_a",
        "late_j_private_b",
        "late_pca_private_a",
        "late_pca_private_b",
        "direct_ablation_shared_mean",
        "two_round_recovery_shared_mean",
        "message_only_joint_accuracy",
        "a_to_b_report",
        "b_to_a_report",
        "a_return_persistence",
        "b_return_persistence",
        "model_sha256",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in summary["analyses"]:
            h1 = item["stage_metrics"]["h1"]
            h3 = item["stage_metrics"]["h3"]
            late = item["late_workspace"]
            writer.writerow(
                {
                    "seed": item["seed"],
                    "training_step": item["training_step"],
                    "base_min_accuracy": item["base_min_accuracy"],
                    "h1_jscore_mean": sum(
                        [
                            h1["jscore_a"]["factor_a"],
                            h1["jscore_a"]["factor_b"],
                            h1["jscore_b"]["factor_a"],
                            h1["jscore_b"]["factor_b"],
                        ]
                    )
                    / 4.0,
                    "h1_alignment_r2": h1["alignment_r2"],
                    "h1_ablation_shared_mean": h1[
                        "ablation_shared_mean"
                    ],
                    "h3_jscore_min": min(
                        h3["jscore_a"].values()
                        | h3["jscore_b"].values()
                        if False
                        else [
                            h3["jscore_a"]["factor_a"],
                            h3["jscore_a"]["factor_b"],
                            h3["jscore_b"]["factor_a"],
                            h3["jscore_b"]["factor_b"],
                        ]
                    ),
                    "h3_alignment_r2": h3["alignment_r2"],
                    "h3_variance_a": h3["variance_fraction_a"],
                    "h3_variance_b": h3["variance_fraction_b"],
                    "late_alignment_r2": late["alignment_r2"],
                    "late_j_private_a": late["j_probes_a"]["private"],
                    "late_j_private_b": late["j_probes_b"]["private"],
                    "late_pca_private_a": late["pca_probes_a"]["private"],
                    "late_pca_private_b": late["pca_probes_b"]["private"],
                    "direct_ablation_shared_mean": late[
                        "direct_ablation_shared_mean"
                    ],
                    "two_round_recovery_shared_mean": late[
                        "two_round_recovery_shared_mean"
                    ],
                    "message_only_joint_accuracy": late[
                        "message_only_joint_accuracy"
                    ],
                    "a_to_b_report": late["a_only_to_b_round1"]["a"],
                    "b_to_a_report": late["b_only_to_a_round1"]["b"],
                    "a_return_persistence": late[
                        "a_only_back_to_a_round2"
                    ]["a"],
                    "b_return_persistence": late[
                        "b_only_back_to_b_round2"
                    ]["b"],
                    "model_sha256": item["model_sha256"],
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    import torch
    from rrct.instrumented_transformer_dyad import (
        TransformerDyadConfig,
        run_transformer_dyad_holdout,
    )

    freeze = verify_freeze(root)
    seed_receipt = json.loads(
        (root / "validation/V0_49_HOLDOUT_SEED_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    output = args.output or (
        root
        / "validation/v0.49.0_instrumented_transformer_dyad/results"
    )
    output.mkdir(parents=True, exist_ok=True)
    weights = output / "weights"
    full = run_transformer_dyad_holdout(
        seed_receipt["selected_seeds"],
        TransformerDyadConfig(),
        weights_directory=str(weights),
    )
    full_path = output / "instrumented_transformer_dyad_analysis.json"
    full_path.write_text(json.dumps(full, indent=2, sort_keys=True) + "\n")
    compact = compact_summary(full)
    compact_path = output / "V0_49_FROZEN_SUMMARY.json"
    compact_path.write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")
    rows_path = output / "instrumented_transformer_dyad_rows.csv"
    write_rows(rows_path, full)
    receipt = {
        "schema": "rrct.v049.holdout_execution_receipt.v1",
        "version": "0.49.0.dev1",
        "executed_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "source_freeze": freeze,
        "seeds": seed_receipt["selected_seeds"],
        "scientific_status": full["scientific_status"],
        "all_endpoints_met": full["all_endpoints_met"],
        "endpoint_pass_count": full["endpoint_pass_count"],
        "endpoint_count": full["endpoint_count"],
        "analysis_sha256": sha256(full_path),
        "summary_sha256": sha256(compact_path),
        "rows_sha256": sha256(rows_path),
        "weight_sha256": {
            path.name: sha256(path) for path in sorted(weights.glob("*.pt"))
        },
        "python": platform.python_version(),
        "torch": torch.__version__,
        "platform": platform.platform(),
    }
    unsigned = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if full["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

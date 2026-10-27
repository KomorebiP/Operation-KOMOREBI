#!/usr/bin/env python3
"""Execute the sealed RRCT v0.50 synergistic-workspace holdout."""
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
    path = root / "validation/V0_50_PREOUTCOME_FREEZE.json"
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
    companion_matches = bool(
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
        raise RuntimeError(f"v0.50 source freeze failed: {result}")
    return result


def compact_summary(full: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": "rrct.v050.synergistic_ephemeral_workspace.summary.v1",
        "version": full["version"],
        "status": full["status"],
        "seeds": full["seeds"],
        "sequence_case_count_per_seed": full["sequence_case_count_per_seed"],
        "matched_mode_count": full["matched_mode_count"],
        "aggregate": full["aggregate"],
        "endpoints": full["endpoints"],
        "all_endpoints_met": full["all_endpoints_met"],
        "claim_boundary": full["claim_boundary"],
        "seed_summaries": [
            {
                "seed": item["seed"],
                "digest": item["digest"],
                "agent_a_training": item["agent_a_training"],
                "agent_b_training": item["agent_b_training"],
                "synergy": item["synergy"],
                "modes": item["modes"],
                "max_nonpersistent_control_accuracy": item[
                    "max_nonpersistent_control_accuracy"
                ],
                "causal_patch": item["causal_patch"],
                "active_workspace_reports": item["active_workspace_reports"],
                "post_dissolution": item["post_dissolution"],
                "private_routine_accuracy": item["private_routine_accuracy"],
                "endpoints": item["endpoints"],
            }
            for item in full["seed_results"]
        ],
    }
    unsigned = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
    return payload


def write_mode_table(path: Path, full: dict[str, Any]) -> None:
    fields = [
        "seed",
        "mode",
        "task_accuracy",
        "agent_a_report_accuracy",
        "agent_b_report_accuracy",
        "private_a_accuracy",
        "private_b_accuracy",
        "persistent_joint_state",
        "jointly_writable",
        "physically_centralized",
        "workspace_erased_after_action",
        "pair_autobiography_present",
        "receipt_digest",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in full["seed_results"]:
            for mode, metrics in result["modes"].items():
                writer.writerow(
                    {
                        "seed": result["seed"],
                        "mode": mode,
                        "task_accuracy": metrics["task_accuracy"],
                        "agent_a_report_accuracy": metrics[
                            "agent_a_report_accuracy"
                        ],
                        "agent_b_report_accuracy": metrics[
                            "agent_b_report_accuracy"
                        ],
                        "private_a_accuracy": metrics["private_a_accuracy"],
                        "private_b_accuracy": metrics["private_b_accuracy"],
                        "persistent_joint_state": metrics[
                            "persistent_joint_state"
                        ],
                        "jointly_writable": metrics["jointly_writable"],
                        "physically_centralized": metrics[
                            "physically_centralized"
                        ],
                        "workspace_erased_after_action": metrics[
                            "workspace_erased_after_action"
                        ],
                        "pair_autobiography_present": metrics[
                            "pair_autobiography_present"
                        ],
                        "receipt_digest": metrics["digest"],
                    }
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    import torch
    from rrct.synergistic_ephemeral_workspace import (
        SynergisticWorkspaceConfig,
        run_synergistic_holdout,
    )

    freeze = verify_freeze(root)
    seed_receipt = json.loads(
        (root / "validation/V0_50_HOLDOUT_SEED_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    output = args.output or (
        root / "validation/v0.50.0_synergistic_ephemeral_workspace/results"
    )
    output.mkdir(parents=True, exist_ok=True)
    weights = output / "weights"
    full = run_synergistic_holdout(
        seed_receipt["selected_seeds"],
        SynergisticWorkspaceConfig(),
        model_directory=weights,
    )
    analysis_path = output / "synergistic_ephemeral_workspace_analysis.json"
    analysis_path.write_text(json.dumps(full, indent=2, sort_keys=True) + "\n")
    compact = compact_summary(full)
    summary_path = output / "V0_50_FROZEN_SUMMARY.json"
    summary_path.write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")
    table_path = output / "synergistic_ephemeral_workspace_modes.csv"
    write_mode_table(table_path, full)
    model_files = sorted(weights.glob("*.pt"))
    receipt = {
        "schema": "rrct.v050.holdout_execution_receipt.v1",
        "version": "0.50.0.dev1",
        "executed_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "source_freeze": freeze,
        "seeds": seed_receipt["selected_seeds"],
        "scientific_status": full["status"],
        "all_endpoints_met": full["all_endpoints_met"],
        "endpoint_pass_count": sum(full["endpoints"].values()),
        "endpoint_count": len(full["endpoints"]),
        "analysis_sha256": sha256(analysis_path),
        "summary_sha256": sha256(summary_path),
        "mode_table_sha256": sha256(table_path),
        "model_sha256": {path.name: sha256(path) for path in model_files},
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

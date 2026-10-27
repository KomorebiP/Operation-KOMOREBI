#!/usr/bin/env python3
"""Verify packaged RRCT v0.50 evidence without retraining."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from rrct.synergistic_ephemeral_workspace import synergy_receipt

    result = root / "validation/v0.50.0_synergistic_ephemeral_workspace/results"
    receipt = json.loads((result / "HOLDOUT_EXECUTION_RECEIPT.json").read_text())
    summary = json.loads((result / "V0_50_FROZEN_SUMMARY.json").read_text())
    analysis_path = result / "synergistic_ephemeral_workspace_analysis.json"
    table_path = result / "synergistic_ephemeral_workspace_modes.csv"
    exact_synergy = synergy_receipt()
    checks = {
        "scientific_status": receipt["scientific_status"]
        == "V050_FROZEN_ENDPOINTS_MET",
        "all_endpoints_met": bool(
            summary["all_endpoints_met"] and receipt["all_endpoints_met"]
        ),
        "endpoint_count": bool(
            len(summary["endpoints"]) == 23
            and sum(summary["endpoints"].values()) == 23
            and receipt["endpoint_count"] == 23
            and receipt["endpoint_pass_count"] == 23
        ),
        "analysis_sha256": sha256(analysis_path) == receipt["analysis_sha256"],
        "summary_sha256": sha256(result / "V0_50_FROZEN_SUMMARY.json")
        == receipt["summary_sha256"],
        "mode_table_sha256": sha256(table_path) == receipt["mode_table_sha256"],
        "exact_synergy": bool(
            exact_synergy.synergy_lower_bound_bits == 4.0
            and exact_synergy.bayes_accuracy_a_history == 1.0 / 16.0
            and exact_synergy.bayes_accuracy_b_history == 1.0 / 16.0
            and exact_synergy.bayes_accuracy_joint_history == 1.0
        ),
        "full_workspace": summary["aggregate"]["modes"]["full_workspace"][
            "task_accuracy"
        ]
        == 1.0,
        "recurrent_message_workspace": summary["aggregate"]["modes"][
            "recurrent_message_workspace"
        ]["task_accuracy"]
        == 1.0,
        "nonpersistent_controls_fail": summary["aggregate"][
            "mean_max_nonpersistent_control_accuracy"
        ]
        <= 0.18,
    }
    for name, digest in receipt["model_sha256"].items():
        path = result / "weights" / name
        checks[f"model::{name}"] = path.is_file() and sha256(path) == digest

    freeze = root / "validation/V0_50_PREOUTCOME_FREEZE.json"
    freeze_payload = json.loads(freeze.read_text())
    freeze_failed: list[str] = []
    for item in freeze_payload["files"]:
        path = root / item["relative_path"]
        if (
            not path.is_file()
            or path.stat().st_size != item["size_bytes"]
            or sha256(path) != item["sha256"]
        ):
            freeze_failed.append(item["relative_path"])
    companion = freeze.with_suffix(freeze.suffix + ".sha256")
    checks["source_freeze"] = bool(
        not freeze_failed
        and companion.is_file()
        and companion.read_text().split()[0] == sha256(freeze)
    )
    payload = {
        "schema": "rrct.v050.result_verification.v1",
        "status": (
            "V050_RESULTS_VERIFIED"
            if all(checks.values())
            else "V050_RESULTS_VERIFICATION_FAILED"
        ),
        "checks": checks,
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "freeze_failed_files": freeze_failed,
        "all_checks_pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify the v0.47 seal and execute the frozen distributed-workspace cohort."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from rrct.distributed_shared_workspace_experiment import (
    run_distributed_shared_workspace_benchmark,
    write_distributed_workspace_results,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(root: Path) -> str:
    path = root / "validation/V0_47_PREOUTCOME_FREEZE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    failed = []
    for entry in payload["files"]:
        candidate = root / entry["relative_path"]
        if (
            not candidate.is_file()
            or candidate.stat().st_size != entry["size_bytes"]
            or sha256(candidate) != entry["sha256"]
        ):
            failed.append(entry["relative_path"])
    if failed:
        raise RuntimeError(f"v0.47 pre-outcome freeze mismatch: {failed}")
    companion = path.with_suffix(path.suffix + ".sha256")
    expected = companion.read_text(encoding="utf-8").split()[0]
    actual = sha256(path)
    if expected != actual:
        raise RuntimeError("v0.47 freeze companion digest mismatch")
    return actual


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    freeze_sha = verify_freeze(root)
    seed_path = root / "validation/V0_47_HOLDOUT_SEED_SELECTION.json"
    seed_receipt = json.loads(seed_path.read_text(encoding="utf-8"))
    seeds = tuple(int(value) for value in seed_receipt["holdout_seeds"])
    output = root / "validation/v0.47.0_distributed_shared_workspace/results"
    output.mkdir(parents=True, exist_ok=True)
    result = run_distributed_shared_workspace_benchmark(
        seeds,
        trials_per_mode=96,
        cohort="frozen_holdout",
    )
    hashes = write_distributed_workspace_results(result, output)
    compact = {
        "schema": "rrct.v047.frozen_holdout_summary.v1",
        "version": "0.47.0.dev1",
        "status": (
            "V047_FROZEN_ENDPOINTS_MET"
            if result["all_endpoints_met"]
            else "V047_FROZEN_ENDPOINTS_NOT_MET"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "holdout_seed_selection_sha256": sha256(seed_path),
        "holdout_seeds": list(seeds),
        "unique_world_case_count": result["unique_world_case_count"],
        "matched_decision_count": result["matched_decision_count"],
        "endpoint_count": len(result["endpoints"]),
        "endpoints": result["endpoints"],
        "all_endpoints_met": result["all_endpoints_met"],
        "discovery_summary": result["discovery_summary"],
        "patch_summary": result["patch_summary"],
        "provenance_summary": result["provenance_summary"],
        "feedback_summary": result["feedback_summary"],
        "partner_summary": result["partner_summary"],
        "mode_summaries": result["mode_summaries"],
        "claim_boundary": result["claim_boundary"],
    }
    summary_path = output / "V0_47_FROZEN_SUMMARY.json"
    summary_path.write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "schema": "rrct.v047.holdout_execution_receipt.v1",
        "version": "0.47.0.dev1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "preoutcome_freeze_sha256": freeze_sha,
        "seed_selection_sha256": sha256(seed_path),
        "analysis_sha256": hashes["distributed_shared_workspace_analysis.json"],
        "compact_summary_sha256": hashes["distributed_shared_workspace_summary.json"],
        "decision_csv_sha256": hashes["distributed_shared_workspace_rows.csv"],
        "human_report_sha256": hashes["DISTRIBUTED_SHARED_WORKSPACE_REPORT.md"],
        "frozen_summary_sha256": sha256(summary_path),
        "all_endpoints_met": compact["all_endpoints_met"],
        "outcomes_hidden_until_runtime_commitment": True,
        "uses_evaluator_labels": False,
    }
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.with_suffix(receipt_path.suffix + ".sha256").write_text(
        f"{sha256(receipt_path)}  {receipt_path.name}\n", encoding="utf-8"
    )
    print(json.dumps(compact, indent=2, sort_keys=True))
    return 0 if compact["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify the v0.46 source seal and execute the frozen neutral-workspace cohort."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from rrct.jspace_self_indexed_workspace_experiment import (
    run_neutral_workspace_benchmark,
    write_neutral_workspace_results,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(root: Path) -> str:
    path = root / "validation/V0_46_PREOUTCOME_FREEZE.json"
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
        raise RuntimeError(f"v0.46 pre-outcome freeze mismatch: {failed}")
    companion = path.with_suffix(path.suffix + ".sha256")
    expected = companion.read_text(encoding="utf-8").split()[0]
    actual = sha256(path)
    if expected != actual:
        raise RuntimeError("v0.46 freeze companion digest mismatch")
    return actual


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    freeze_sha = verify_freeze(root)
    seed_path = root / "validation/V0_46_HOLDOUT_SEED_SELECTION.json"
    seed_receipt = json.loads(seed_path.read_text(encoding="utf-8"))
    seeds = tuple(int(value) for value in seed_receipt["holdout_seeds"])
    output = root / "validation/v0.46.0_neutral_self_indexed_workspace/results"
    output.mkdir(parents=True, exist_ok=True)
    result = run_neutral_workspace_benchmark(
        seeds,
        trials_per_scenario=16,
        cohort="frozen_holdout",
    )
    hashes = write_neutral_workspace_results(result, output)
    summary = {
        "schema": "rrct.v046.frozen_holdout_summary.v1",
        "version": "0.46.0.dev1",
        "status": (
            "V046_FROZEN_ENDPOINTS_MET"
            if result["all_endpoints_met"]
            else "V046_FROZEN_ENDPOINTS_NOT_MET"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "holdout_seed_selection_sha256": sha256(seed_path),
        "holdout_seeds": list(seeds),
        "unique_world_case_count": result["unique_world_case_count"],
        "matched_decision_count": result["decision_count"],
        "endpoint_count": len(result["endpoints"]),
        "endpoints": result["endpoints"],
        "all_endpoints_met": result["all_endpoints_met"],
        "discovery_summary": result["discovery_summary"],
        "swap_summary": result["swap_summary"],
        "ablation_summary": result["ablation_summary"],
        "mode_summaries": result["mode_summaries"],
        "claim_boundary": result["claim_boundary"],
    }
    summary_path = output / "V0_46_FROZEN_SUMMARY.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    receipt = {
        "schema": "rrct.v046.holdout_execution_receipt.v1",
        "version": "0.46.0.dev1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "seed_selection_sha256": sha256(seed_path),
        "analysis_sha256": hashes["neutral_self_indexed_workspace_analysis.json"],
        "compact_summary_sha256": hashes["neutral_self_indexed_workspace_summary.json"],
        "decision_csv_sha256": hashes["neutral_self_indexed_workspace_rows.csv"],
        "human_report_sha256": hashes["NEUTRAL_SELF_INDEXED_WORKSPACE_REPORT.md"],
        "frozen_summary_sha256": sha256(summary_path),
        "all_endpoints_met": summary["all_endpoints_met"],
        "outcomes_hidden_until_runtime_commitment": True,
        "uses_evaluator_labels": False,
    }
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    receipt_path.with_suffix(receipt_path.suffix + ".sha256").write_text(
        f"{sha256(receipt_path)}  {receipt_path.name}\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

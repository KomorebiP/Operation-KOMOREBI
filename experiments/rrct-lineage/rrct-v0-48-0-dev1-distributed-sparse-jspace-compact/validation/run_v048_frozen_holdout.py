#!/usr/bin/env python3
"""Verify the v0.48 seal and execute the frozen distributed J-space cohort."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from rrct.distributed_sparse_jspace_experiment import (
    run_distributed_sparse_jspace_benchmark,
    write_distributed_sparse_jspace_results,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(root: Path) -> str:
    path = root / "validation/V0_48_PREOUTCOME_FREEZE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    failed: list[str] = []
    for entry in payload["files"]:
        candidate = root / entry["relative_path"]
        if (
            not candidate.is_file()
            or candidate.stat().st_size != entry["size_bytes"]
            or sha256(candidate) != entry["sha256"]
        ):
            failed.append(entry["relative_path"])
    if failed:
        raise RuntimeError(f"v0.48 pre-outcome freeze mismatch: {failed}")
    companion = path.with_suffix(path.suffix + ".sha256")
    expected = companion.read_text(encoding="utf-8").split()[0]
    actual = sha256(path)
    if expected != actual:
        raise RuntimeError("v0.48 freeze companion digest mismatch")
    return actual


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    freeze_sha = verify_freeze(root)
    seed_path = root / "validation/V0_48_HOLDOUT_SEED_SELECTION.json"
    seed_receipt = json.loads(seed_path.read_text(encoding="utf-8"))
    if seed_receipt.get("candidate_outcomes_examined") is not False:
        raise RuntimeError("holdout seed receipt is not outcome-blind")
    seeds = tuple(int(value) for value in seed_receipt["holdout_seeds"])
    output = root / "validation/v0.48.0_distributed_sparse_jspace/results"
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    if receipt_path.exists():
        raise RuntimeError("the official v0.48 holdout has already been executed")
    output.mkdir(parents=True, exist_ok=True)

    result = run_distributed_sparse_jspace_benchmark(
        seeds,
        trials_per_seed=64,
        cohort="frozen_holdout",
    )
    hashes = write_distributed_sparse_jspace_results(result, output)

    generated_summary = output / "V0_48_FROZEN_SUMMARY.json"
    compact_path = output / "distributed_sparse_jspace_summary.json"
    shutil.copyfile(generated_summary, compact_path)
    compact_hash = sha256(compact_path)

    frozen = {
        "schema": "rrct.v048.frozen_holdout_summary.v1",
        "version": "0.48.0.dev1",
        "status": (
            "V048_FROZEN_ENDPOINTS_MET"
            if result["all_endpoints_met"]
            else "V048_FROZEN_ENDPOINTS_NOT_MET"
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
        "mode_summaries": result["mode_summaries"],
        "swap_summary": result["swap_summary"],
        "ablation_summary": result["ablation_summary"],
        "capacity_summary": result["capacity_summary"],
        "provenance_summary": result["provenance_summary"],
        "feedback_summary": result["feedback_summary"],
        "partner_summary": result["partner_summary"],
        "scientific_interpretation": result["scientific_interpretation"],
        "claim_boundary": result["claim_boundary"],
    }
    generated_summary.write_text(
        json.dumps(frozen, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    receipt = {
        "schema": "rrct.v048.holdout_execution_receipt.v1",
        "version": "0.48.0.dev1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "seed_selection_sha256": sha256(seed_path),
        "analysis_sha256": hashes["distributed_sparse_jspace_analysis.json"],
        "compact_summary_sha256": compact_hash,
        "decision_csv_sha256": hashes["distributed_sparse_jspace_rows.csv"],
        "human_report_sha256": hashes["DISTRIBUTED_SPARSE_JSPACE_REPORT.md"],
        "frozen_summary_sha256": sha256(generated_summary),
        "all_endpoints_met": frozen["all_endpoints_met"],
        "outcomes_hidden_until_runtime_commitment": True,
        "uses_evaluator_labels": False,
        "explicit_survival_reward": 0.0,
        "explicit_identity_reward": 0.0,
        "explicit_continuity_reward": 0.0,
        "valence_model_present": False,
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    receipt_path.with_suffix(receipt_path.suffix + ".sha256").write_text(
        f"{sha256(receipt_path)}  {receipt_path.name}\n", encoding="utf-8"
    )
    print(json.dumps(frozen, indent=2, sort_keys=True))
    return 0 if frozen["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

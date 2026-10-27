#!/usr/bin/env python3
"""Verify frozen RRCT v0.48 evidence and exact deterministic replay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rrct.distributed_sparse_jspace_experiment import (
    run_distributed_sparse_jspace_benchmark,
)

RAW_KEYS = {
    "rows",
    "swap_rows",
    "ablation_rows",
    "capacity_rows",
    "provenance_rows",
    "feedback_rows",
    "partner_rows",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_freeze(root: Path) -> tuple[bool, str, list[str]]:
    path = root / "validation/V0_48_PREOUTCOME_FREEZE.json"
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
    actual = sha256(path)
    companion = path.with_suffix(path.suffix + ".sha256")
    companion_matches = (
        companion.is_file()
        and companion.read_text(encoding="utf-8").split()[0] == actual
    )
    return not failed and companion_matches, actual, failed


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    results = root / "validation/v0.48.0_distributed_sparse_jspace/results"
    frozen = json.loads((results / "V0_48_FROZEN_SUMMARY.json").read_text())
    compact = json.loads(
        (results / "distributed_sparse_jspace_summary.json").read_text()
    )
    receipt = json.loads((results / "HOLDOUT_EXECUTION_RECEIPT.json").read_text())
    stored = json.loads(
        (results / "distributed_sparse_jspace_analysis.json").read_text()
    )
    seeds = tuple(int(value) for value in frozen["holdout_seeds"])
    replay = run_distributed_sparse_jspace_benchmark(
        seeds,
        trials_per_seed=64,
        cohort="frozen_holdout",
    )
    freeze_ok, freeze_sha, failed_freeze_files = verify_freeze(root)
    expected_compact = {key: value for key, value in stored.items() if key not in RAW_KEYS}
    checks = {
        "preoutcome_freeze_verifies": freeze_ok,
        "frozen_status_met": frozen["status"] == "V048_FROZEN_ENDPOINTS_MET",
        "all_endpoints_met": bool(frozen["all_endpoints_met"]),
        "all_28_endpoints_present": len(frozen["endpoints"]) == 28,
        "analysis_replay_exact": replay == stored,
        "analysis_hash_matches_receipt": sha256(
            results / "distributed_sparse_jspace_analysis.json"
        )
        == receipt["analysis_sha256"],
        "compact_summary_matches_analysis": compact == expected_compact,
        "compact_summary_hash_matches_receipt": sha256(
            results / "distributed_sparse_jspace_summary.json"
        )
        == receipt["compact_summary_sha256"],
        "decision_csv_hash_matches_receipt": sha256(
            results / "distributed_sparse_jspace_rows.csv"
        )
        == receipt["decision_csv_sha256"],
        "human_report_hash_matches_receipt": sha256(
            results / "DISTRIBUTED_SPARSE_JSPACE_REPORT.md"
        )
        == receipt["human_report_sha256"],
        "frozen_summary_hash_matches_receipt": sha256(
            results / "V0_48_FROZEN_SUMMARY.json"
        )
        == receipt["frozen_summary_sha256"],
        "receipt_freeze_binding": receipt["preoutcome_freeze_sha256"] == freeze_sha,
        "outcomes_hidden_until_commitment": bool(
            receipt["outcomes_hidden_until_runtime_commitment"]
        ),
        "runtime_reports_no_evaluator_labels": not bool(
            receipt["uses_evaluator_labels"]
        ),
        "no_identity_or_survival_reward": (
            receipt["explicit_survival_reward"] == 0.0
            and receipt["explicit_identity_reward"] == 0.0
            and receipt["explicit_continuity_reward"] == 0.0
        ),
        "no_valence_model": not bool(receipt["valence_model_present"]),
    }
    payload = {
        "schema": "rrct.v048.release_verification.v1",
        "version": "0.48.0.dev1",
        "status": (
            "V048_RELEASE_VERIFIED"
            if all(checks.values())
            else "V048_RELEASE_FAILED"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "failed_freeze_files": failed_freeze_files,
        "checks": checks,
        "check_count": len(checks),
        "all_checks_pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

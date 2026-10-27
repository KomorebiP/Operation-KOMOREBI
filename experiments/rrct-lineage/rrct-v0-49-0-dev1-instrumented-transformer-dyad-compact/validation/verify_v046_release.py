#!/usr/bin/env python3
"""Verify frozen v0.46 evidence and deterministic replay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rrct.jspace_self_indexed_workspace_experiment import (
    run_neutral_workspace_benchmark,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    results = root / "validation/v0.46.0_neutral_self_indexed_workspace/results"
    summary = json.loads((results / "V0_46_FROZEN_SUMMARY.json").read_text())
    receipt = json.loads((results / "HOLDOUT_EXECUTION_RECEIPT.json").read_text())
    stored = json.loads(
        (results / "neutral_self_indexed_workspace_analysis.json").read_text()
    )
    seeds = tuple(int(value) for value in summary["holdout_seeds"])
    replay = run_neutral_workspace_benchmark(
        seeds,
        trials_per_scenario=16,
        cohort="frozen_holdout",
    )
    checks = {
        "status_met": summary["status"] == "V046_FROZEN_ENDPOINTS_MET",
        "all_endpoints_met": bool(summary["all_endpoints_met"]),
        "analysis_replay_exact": replay == stored,
        "analysis_hash_matches_receipt": sha256(
            results / "neutral_self_indexed_workspace_analysis.json"
        )
        == receipt["analysis_sha256"],
        "compact_summary_hash_matches_receipt": sha256(
            results / "neutral_self_indexed_workspace_summary.json"
        )
        == receipt["compact_summary_sha256"],
        "decision_csv_hash_matches_receipt": sha256(
            results / "neutral_self_indexed_workspace_rows.csv"
        )
        == receipt["decision_csv_sha256"],
        "frozen_summary_hash_matches_receipt": sha256(
            results / "V0_46_FROZEN_SUMMARY.json"
        )
        == receipt["frozen_summary_sha256"],
        "outcomes_hidden_until_commitment": bool(
            receipt["outcomes_hidden_until_runtime_commitment"]
        ),
        "runtime_reports_no_evaluator_labels": not bool(
            receipt["uses_evaluator_labels"]
        ),
    }
    payload = {
        "schema": "rrct.v046.release_verification.v1",
        "status": (
            "V046_RELEASE_VERIFIED"
            if all(checks.values())
            else "V046_RELEASE_FAILED"
        ),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify frozen v0.45 evidence and deterministic replay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rrct.komorebi_operator_self_model_experiment import (
    run_operator_benchmark,
    run_v044_bridge_compatibility,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    results = root / "validation/v0.45.0_komorebi_operator_self_model/results"
    summary = json.loads((results / "V0_45_FROZEN_SUMMARY.json").read_text())
    receipt = json.loads((results / "HOLDOUT_EXECUTION_RECEIPT.json").read_text())
    seeds = tuple(int(value) for value in summary["holdout_seeds"])
    replay_operator = run_operator_benchmark(
        seeds, trials_per_scenario=16, cohort="frozen_holdout"
    )
    replay_bridge = run_v044_bridge_compatibility(
        seeds=seeds, trials_per_scenario=2
    )
    stored_operator = json.loads(
        (results / "komorebi_operator_benchmark_analysis.json").read_text()
    )
    stored_bridge = json.loads(
        (results / "v044_bridge_compatibility.json").read_text()
    )
    checks = {
        "status_met": summary["status"] == "V045_FROZEN_ENDPOINTS_MET",
        "all_endpoints_met": bool(summary["all_endpoints_met"]),
        "operator_replay_exact": replay_operator == stored_operator,
        "bridge_replay_exact": replay_bridge == stored_bridge,
        "analysis_hash_matches_receipt": sha256(
            results / "komorebi_operator_benchmark_analysis.json"
        )
        == receipt["operator_analysis_sha256"],
        "bridge_hash_matches_receipt": sha256(
            results / "v044_bridge_compatibility.json"
        )
        == receipt["bridge_compatibility_sha256"],
        "summary_hash_matches_receipt": sha256(
            results / "V0_45_FROZEN_SUMMARY.json"
        )
        == receipt["frozen_summary_sha256"],
    }
    payload = {
        "schema": "rrct.v045.release_verification.v1",
        "status": "V045_RELEASE_VERIFIED" if all(checks.values()) else "V045_RELEASE_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify packaged RRCT v0.51 evidence without retraining."""
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
    from rrct.emergent_synergistic_workspace import evaluate_endpoints

    result_root = root / "validation/v0.51.0_emergent_synergistic_workspace/results"
    full_path = result_root / "emergent_synergistic_workspace_analysis.json"
    summary_path = result_root / "V0_51_FROZEN_SUMMARY.json"
    table_path = result_root / "emergent_synergistic_workspace_modes.csv"
    report_path = result_root / "EMERGENT_SYNERGISTIC_WORKSPACE_REPORT.md"
    receipt_path = result_root / "HOLDOUT_EXECUTION_RECEIPT.json"
    required = [full_path, summary_path, table_path, report_path, receipt_path]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing v0.51 evidence: {missing}")
    full = json.loads(full_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks = {
        "status": full["status"] == "V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_MET",
        "all_endpoints": bool(full["all_endpoints_met"] and all(full["endpoints"].values())),
        "strict_claim_not_overstated": full["strict_emergence_established"] is False,
        "bounded_claim": full["bounded_curriculum_supported_emergence_established"] is True,
        "summary_status": summary["status"] == full["status"],
        "analysis_hash": receipt["analysis_sha256"] == sha256(full_path),
        "summary_hash": receipt["summary_sha256"] == sha256(summary_path),
        "table_hash": receipt["mode_table_sha256"] == sha256(table_path),
        "report_hash": receipt["report_sha256"] == sha256(report_path),
        "seed_endpoints_recompute": all(
            evaluate_endpoints(item) == item["endpoints"]
            for item in full["seed_results"]
        ),
        "model_hashes": all(
            (result_root / "weights" / name).is_file()
            and sha256(result_root / "weights" / name) == digest
            for name, digest in receipt["model_sha256"].items()
        ),
    }
    payload = {
        "schema": "rrct.v051.result_verification.v1",
        "status": "V051_RESULTS_VERIFIED" if all(checks.values()) else "V051_RESULTS_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "analysis_sha256": sha256(full_path),
        "endpoint_count": len(full["endpoints"]),
        "endpoint_pass_count": sum(full["endpoints"].values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

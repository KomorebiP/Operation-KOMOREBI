#!/usr/bin/env python3
"""Verify the v0.45 source seal, execute the frozen cohort, and write evidence."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from rrct.komorebi_operator_self_model_experiment import (
    run_operator_benchmark,
    run_v044_bridge_compatibility,
    write_operator_benchmark_results,
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify_freeze(root: Path) -> str:
    path = root / "validation/V0_45_PREOUTCOME_FREEZE.json"
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
        raise RuntimeError(f"v0.45 pre-outcome freeze mismatch: {failed}")
    return sha256(path)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    freeze_sha = verify_freeze(root)
    seed_receipt = json.loads(
        (root / "validation/V0_45_HOLDOUT_SEED_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    seeds = tuple(int(value) for value in seed_receipt["holdout_seeds"])
    output = root / "validation/v0.45.0_komorebi_operator_self_model/results"
    output.mkdir(parents=True, exist_ok=True)

    operator = run_operator_benchmark(
        seeds,
        trials_per_scenario=16,
        cohort="frozen_holdout",
    )
    hashes = write_operator_benchmark_results(operator, output)
    compatibility = run_v044_bridge_compatibility(
        seeds=seeds,
        trials_per_scenario=2,
    )
    compatibility_path = output / "v044_bridge_compatibility.json"
    compatibility_path.write_text(
        json.dumps(compatibility, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    combined_endpoints = {
        **{f"operator::{key}": value for key, value in operator["endpoints"].items()},
        **{
            f"bridge::{key}": value
            for key, value in compatibility["endpoints"].items()
        },
    }
    combined = {
        "schema": "rrct.v045.komorebi_operator_holdout_summary.v1",
        "status": (
            "V045_FROZEN_ENDPOINTS_MET"
            if all(combined_endpoints.values())
            else "V045_FROZEN_ENDPOINTS_NOT_MET"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "holdout_seeds": list(seeds),
        "operator_decision_count": len(operator["rows"]),
        "bridge_decision_count": len(compatibility["rows"]),
        "operator_mode_summaries": operator["mode_summaries"],
        "bridge_summaries": compatibility["summaries"],
        "endpoints": combined_endpoints,
        "all_endpoints_met": all(combined_endpoints.values()),
        "claim_boundary": operator["claim_boundary"],
    }
    summary_path = output / "V0_45_FROZEN_SUMMARY.json"
    summary_path.write_text(
        json.dumps(combined, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema": "rrct.v045.holdout_execution_receipt.v1",
        "executed_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "preoutcome_freeze_sha256": freeze_sha,
        "seed_selection_sha256": sha256(
            root / "validation/V0_45_HOLDOUT_SEED_SELECTION.json"
        ),
        "operator_analysis_sha256": hashes[
            "komorebi_operator_benchmark_analysis.json"
        ],
        "operator_summary_sha256": hashes[
            "komorebi_operator_benchmark_summary.json"
        ],
        "bridge_compatibility_sha256": sha256(compatibility_path),
        "frozen_summary_sha256": sha256(summary_path),
        "all_endpoints_met": combined["all_endpoints_met"],
        "outcomes_hidden_until_runtime_commitment": True,
    }
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(combined, indent=2, sort_keys=True))
    return 0 if combined["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

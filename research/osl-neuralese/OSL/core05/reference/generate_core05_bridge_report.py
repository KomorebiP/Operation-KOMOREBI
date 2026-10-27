#!/usr/bin/env python3
"""Verify the finite Discovery Bridge fixtures under OSL-Core 0.5."""

from __future__ import annotations

import json
from pathlib import Path

from generate_core05_evidence import ROOT, run_source
from osl_model import digest


def main() -> int:
    records = []
    for path in sorted((ROOT / "bridge_examples").glob("*.osl")):
        summary, _trace = run_source(path)
        records.append(summary)
    payload = {
        "schema": "osl.core05.discovery-bridge-suite.v1",
        "language_version": "OSL-Core 0.5",
        "evidence_profile": "v0.5-semantic-independence",
        "program_count": len(records),
        "accepted_count": sum(bool(record["runtime_accepted"]) for record in records),
        "receipt_count": sum(int(record["receipt_count"]) for record in records),
        "base_independent_verified_count": sum(
            bool(record["base_independent_checks_pass"]) for record in records
        ),
        "semantic_independence_verified_count": sum(
            bool(record["semantic_independence_pass"]) for record in records
        ),
        "supplementary_replay_verified_count": sum(
            bool(record["supplementary_replay_pass"]) for record in records
        ),
        "records": records,
        "all_checks_pass": bool(records and all(record["passed"] for record in records)),
        "claim_boundary": (
            "The bridge demonstrates finite admitted, quarantined, and rejected "
            "candidate handling. It does not prove open-world discovery or semantic truth."
        ),
    }
    payload["suite_digest"] = digest(payload)
    (ROOT / "CORE05_DISCOVERY_BRIDGE_REPORT.json").write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "program_count": payload["program_count"],
        "receipt_count": payload["receipt_count"],
        "all_checks_pass": payload["all_checks_pass"],
    }, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify the three OSL Discovery Bridge programs under Core 0.4."""
from __future__ import annotations

import json
from pathlib import Path

from osl_core import OSLError, OSLRuntime, OSLStaticError
from osl_kernel import KernelVerifier
from osl_model import digest


EXPECTED_FILES = {
    "ambiguous_quarantine.osl",
    "flip_both_admission.osl",
    "inconsistent_rejection.osl",
}
EXPECTED_RECEIPT_COUNT = 71


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    records = []
    for path in sorted((root / "bridge_examples").glob("*.osl")):
        source = path.read_text(encoding="utf-8")
        runtime = OSLRuntime()
        error = None
        try:
            runtime.run_text(source, filename=path.name)
        except (OSLError, OSLStaticError) as exc:
            error = str(exc)
        kernel = KernelVerifier().verify(
            runtime.audit_log,
            runtime.state.snapshot(),
            source=source,
        )
        terminal = runtime.audit_log[-1]
        record = {
            "file": path.name,
            "source_digest": digest(source),
            "runtime_accepted": error is None,
            "runtime_error": error,
            "terminal_kind": terminal.get("kind"),
            "terminal_phase": terminal.get("phase"),
            "receipt_count": len(runtime.audit_log),
            "receipt_head": terminal.get("digest"),
            "kernel_checks_pass": kernel.get("all_checks_pass"),
            "independent_checks_pass": kernel.get("independent_checks_pass"),
            "supplementary_replay_pass": bool(
                kernel.get("supplementary_same_runtime_replay", {}).get("performed")
                and kernel.get("supplementary_same_runtime_replay", {}).get("receipt_match")
                and kernel.get("supplementary_same_runtime_replay", {}).get("final_state_match")
            ),
            "kernel_verification_digest": kernel.get("verification_digest"),
        }
        record["record_digest"] = digest(record)
        records.append(record)
    payload = {
        "schema": "osl.core04.discovery-bridge-suite.v1",
        "language_version": "OSL-Core 0.4",
        "evidence_profile": "v0.4-native",
        "program_count": len(records),
        "accepted_count": sum(record["runtime_accepted"] for record in records),
        "verified_count": sum(record["kernel_checks_pass"] for record in records),
        "independent_verified_count": sum(
            record["independent_checks_pass"] for record in records
        ),
        "supplementary_replay_verified_count": sum(
            record["supplementary_replay_pass"] for record in records
        ),
        "receipt_count": sum(record["receipt_count"] for record in records),
        "records": records,
        "all_checks_pass": bool(
            len(records) == 3
            and {record["file"] for record in records} == EXPECTED_FILES
            and sum(record["receipt_count"] for record in records)
            == EXPECTED_RECEIPT_COUNT
            and all(record["runtime_accepted"] for record in records)
            and all(record["kernel_checks_pass"] for record in records)
            and all(record["independent_checks_pass"] for record in records)
            and all(record["supplementary_replay_pass"] for record in records)
        ),
    }
    payload["verification_status"] = (
        "V04_NATIVE_VERIFIED" if payload["all_checks_pass"] else "NOT_VERIFIED"
    )
    payload["suite_digest"] = digest(payload)
    (root / "CORE04_DISCOVERY_BRIDGE_REPORT.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

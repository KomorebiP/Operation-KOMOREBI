#!/usr/bin/env python3
"""Run packaged OSL-Core 0.3 examples and paired-trace audits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_noninterference import audit
from osl_core import run_program
from osl_model import digest


def expected_error(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines()[:5]:
        marker = "# EXPECT-ERROR:"
        if line.startswith(marker):
            return line[len(marker) :].strip()
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "examples",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "examples",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = []
    failures = []
    for path in sorted(args.examples.glob("*.osl")):
        expected = expected_error(path)
        result = run_program(path)
        accepted = bool(result["ok"])
        if expected is None:
            passed = accepted
            detail = "accepted" if accepted else result["error"]
        else:
            passed = (not accepted) and expected.lower() in str(result["error"]).lower()
            detail = result["error"]
        record = {
            "file": path.name,
            "expected_error": expected,
            "accepted": accepted,
            "passed": passed,
            "detail": detail,
            "snapshot_digest": result["state"]["snapshot_digest"],
            "static_report_digest": (
                None
                if result["state"].get("static_report") is None
                else result["state"]["static_report"]["report_digest"]
            ),
        }
        records.append(record)
        if not passed:
            failures.append(record)

    audit_specs = [
        (
            "safe_metadata_pair",
            args.examples / "28_safe_metadata_left.osl",
            args.examples / "29_safe_metadata_right.osl",
            True,
        ),
        (
            "leaky_metadata_pair",
            args.examples / "30_leaky_metadata_left.osl",
            args.examples / "31_leaky_metadata_right.osl",
            False,
        ),
    ]
    audit_records = []
    for name, left, right, expected_noninterference in audit_specs:
        result = audit(left, right)
        passed = bool(result.get("ok")) and (
            bool(result.get("noninterference")) == expected_noninterference
        )
        audit_record = {
            "name": name,
            "left": left.name,
            "right": right.name,
            "expected_noninterference": expected_noninterference,
            "observed_noninterference": result.get("noninterference"),
            "difference_count": result.get("difference_count"),
            "passed": passed,
            "audit_digest": result.get("audit_digest"),
        }
        audit_records.append(audit_record)
        if not passed:
            failures.append(audit_record)

    payload = {
        "schema": "osl-core.example-suite.v2",
        "language_version": "0.3",
        "example_count": len(records),
        "passed_count": sum(record["passed"] for record in records),
        "audit_count": len(audit_records),
        "audit_passed_count": sum(record["passed"] for record in audit_records),
        "failed_count": len(failures),
        "records": records,
        "audit_records": audit_records,
    }
    payload["suite_digest"] = digest(payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for record in records:
            status = "PASS" if record["passed"] else "FAIL"
            print(f"{status:4s} {record['file']}: {record['detail']}")
        for record in audit_records:
            status = "PASS" if record["passed"] else "FAIL"
            print(
                f"{status:4s} {record['name']}: expected_noninterference="
                f"{record['expected_noninterference']} observed="
                f"{record['observed_noninterference']}"
            )
        print(
            f"OSL_CORE_EXAMPLES passed={payload['passed_count']}/"
            f"{payload['example_count']} audits={payload['audit_passed_count']}/"
            f"{payload['audit_count']} failed={payload['failed_count']}"
        )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

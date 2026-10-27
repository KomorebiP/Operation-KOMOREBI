#!/usr/bin/env python3
"""Offline integrity and evidence-summary verifier for the Core 0.4 package."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

from osl_model import digest


EXCLUDED_NAMES = {
    "MANIFEST.json",
    "SHA256SUMS",
    "OSL_Core_0.4_Receipt_Hardening_v0.1.0.zip",
}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXPECTED_SCHEMA = "osl.core04.release-manifest.v1"
EXPECTED_RELEASE = "OSL-Core 0.4 Receipt Hardening v0.1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "MANIFEST.json"
    failures: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"all_checks_pass": False, "failures": [str(exc)]}))
        return 1
    if not isinstance(manifest, dict):
        print(json.dumps({
            "all_checks_pass": False,
            "failures": ["manifest_not_object"],
        }))
        return 1

    unsigned = dict(manifest)
    observed_manifest_digest = unsigned.pop("manifest_digest", None)
    if observed_manifest_digest != digest(unsigned):
        failures.append("manifest_digest")

    if manifest.get("schema") != EXPECTED_SCHEMA:
        failures.append("manifest_schema")
    if manifest.get("release") != EXPECTED_RELEASE:
        failures.append("manifest_release")
    records = manifest.get("files")
    if not isinstance(records, list):
        failures.append("manifest_files")
        records = []
    if manifest.get("file_count") != len(records):
        failures.append("manifest_file_count")

    listed_paths: list[str] = []
    seen_paths: set[str] = set()
    root_resolved = root.resolve()
    for record in records:
        if not isinstance(record, dict):
            failures.append("record_type")
            continue
        relative = record.get("path")
        if not isinstance(relative, str) or not relative:
            failures.append("record_path")
            continue
        pure = PurePosixPath(relative)
        if (
            pure.is_absolute()
            or not pure.parts
            or ".." in pure.parts
            or relative != pure.as_posix()
            or "\\" in relative
        ):
            failures.append(f"unsafe_path:{relative}")
            continue
        if relative in seen_paths:
            failures.append(f"duplicate_path:{relative}")
            continue
        seen_paths.add(relative)
        listed_paths.append(relative)
        path = root.joinpath(*pure.parts)
        try:
            path.resolve().relative_to(root_resolved)
        except (OSError, ValueError):
            failures.append(f"escaped_path:{relative}")
            continue
        if path.is_symlink():
            failures.append(f"symlink:{relative}")
            continue
        if not path.is_file():
            failures.append(f"missing:{relative}")
            continue
        if path.stat().st_size != record.get("size_bytes"):
            failures.append(f"size:{relative}")
        expected_sha = record.get("sha256")
        if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            failures.append(f"sha256_format:{relative}")
        elif sha256(path) != expected_sha:
            failures.append(f"sha256:{relative}")

    if listed_paths != sorted(listed_paths):
        failures.append("manifest_path_order")
    expected_paths = [
        path.relative_to(root).as_posix()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.name not in EXCLUDED_NAMES
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
        and path.suffix != ".pyc"
    ]
    if listed_paths != expected_paths:
        missing_from_manifest = sorted(set(expected_paths) - set(listed_paths))
        extra_in_manifest = sorted(set(listed_paths) - set(expected_paths))
        failures.extend(f"unlisted:{path}" for path in missing_from_manifest)
        failures.extend(f"not_packaged:{path}" for path in extra_in_manifest)

    expected_sums = "".join(
        f"{record.get('sha256')}  {record.get('path')}\n"
        for record in records
        if isinstance(record, dict)
    )
    try:
        observed_sums = (root / "SHA256SUMS").read_text(encoding="utf-8")
    except OSError:
        failures.append("missing:SHA256SUMS")
    else:
        if observed_sums != expected_sums:
            failures.append("SHA256SUMS")

    evidence_expectations = {
        "CORE04_CONFORMANCE_REPORT.json": {
            "all_checks_pass": True,
            "evidence_profile": "v0.4-native",
            "verification_status": "V04_NATIVE_VERIFIED",
            "example_count": 66,
            "accepted_count": 42,
            "rejected_count": 24,
            "audit_receipt_count": 1825,
        },
        "CORE04_KERNEL_REPORT.json": {
            "all_checks_pass": True,
            "evidence_profile": "v0.4-native",
            "verification_status": "V04_NATIVE_VERIFIED",
            "program_count": 66,
            "verified_program_count": 66,
            "independent_verified_program_count": 66,
            "supplementary_replay_verified_count": 66,
            "audit_receipt_count": 1825,
        },
        "ADVERSARIAL_MUTATION_REPORT.json": {
            "all_checks_pass": True,
            "case_count": 24,
            "passed_count": 24,
        },
        "CORE04_DISCOVERY_BRIDGE_REPORT.json": {
            "all_checks_pass": True,
            "evidence_profile": "v0.4-native",
            "verification_status": "V04_NATIVE_VERIFIED",
            "program_count": 3,
            "accepted_count": 3,
            "verified_count": 3,
            "independent_verified_count": 3,
            "supplementary_replay_verified_count": 3,
            "receipt_count": 71,
        },
        "TEST_REPORT.json": {
            "all_checks_pass": True,
            "pytest_passed": 93,
            "pytest_failed": 0,
            "pytest_skipped": 0,
            "pytest_xfailed": 0,
            "pytest_xpassed": 0,
            "pytest_deselected": 0,
            "pytest_errors": 0,
            "syntax_failure_count": 0,
        },
    }
    for filename, expected in evidence_expectations.items():
        try:
            report = json.loads((root / filename).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            failures.append(f"evidence:{filename}")
            continue
        if not isinstance(report, dict):
            failures.append(f"evidence:{filename}:not_object")
            continue
        for key, value in expected.items():
            if report.get(key) != value:
                failures.append(f"evidence:{filename}:{key}")

    result = {
        "schema": "osl.core04.offline-verification.v1",
        "checked_file_count": len(records),
        "failure_count": len(failures),
        "failures": failures,
        "all_checks_pass": not failures,
        "claim_boundary": (
            "This verifies packaged bytes and declared finite reports; it does "
            "not authenticate the package signer or prove the interpreter."
        ),
    }
    result["verification_digest"] = digest(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

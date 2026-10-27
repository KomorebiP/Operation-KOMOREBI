#!/usr/bin/env python3
"""Generate the complete OSL-Core 0.3 evidence bundle deterministically."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from osl_core import OSLRuntime, OSLError, OSLStaticError
from osl_formal_kernel import explore_kernel
from osl_information_flow import analyze_information_flow
from osl_kernel import verify_directory
from osl_metacore import build_report as build_metacore_report
from osl_model import digest
from osl_parser import parse_and_check, parse_program
from osl_session_verify import verify_session_protocol
from verify_trace import verify_directory as verify_trace_directory


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _expected_error(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines()[:5]:
        marker = "# EXPECT-ERROR:"
        if line.startswith(marker):
            return line[len(marker):].strip()
    return None


def example_report(example_dir: Path) -> dict[str, Any]:
    from audit_noninterference import audit

    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for path in sorted(example_dir.glob("*.osl")):
        expected = _expected_error(path)
        runtime = OSLRuntime()
        error: str | None = None
        try:
            runtime.run_file(path)
        except (OSLError, OSLStaticError) as exc:
            error = str(exc)
        accepted = error is None
        passed = accepted if expected is None else (not accepted and expected.lower() in str(error).lower())
        record = {
            "file": path.name,
            "expected_error": expected,
            "accepted": accepted,
            "passed": passed,
            "detail": "accepted" if accepted else error,
            "semantic_digest": runtime.state.semantic_digest(),
            "snapshot_digest": runtime.state.snapshot()["snapshot_digest"],
            "audit_chain_tip": runtime.audit_log[-1]["digest"] if runtime.audit_log else "0" * 64,
            "audit_receipt_count": len(runtime.audit_log),
            "static_report_digest": None if runtime.state.static_report is None else runtime.state.static_report["report_digest"],
        }
        records.append(record)
        if not passed:
            failures.append(record)

    audit_specs = [
        ("safe_metadata_pair", example_dir / "28_safe_metadata_left.osl", example_dir / "29_safe_metadata_right.osl", True),
        ("leaky_metadata_pair", example_dir / "30_leaky_metadata_left.osl", example_dir / "31_leaky_metadata_right.osl", False),
    ]
    audit_records: list[dict[str, Any]] = []
    for name, left, right, expected in audit_specs:
        result = audit(left, right)
        passed = bool(result.get("ok")) and bool(result.get("noninterference")) == expected
        record = {
            "name": name,
            "left": left.name,
            "right": right.name,
            "expected_noninterference": expected,
            "observed_noninterference": result.get("noninterference"),
            "difference_count": result.get("difference_count"),
            "passed": passed,
            "audit_digest": result.get("audit_digest"),
        }
        audit_records.append(record)
        if not passed:
            failures.append(record)

    payload: dict[str, Any] = {
        "schema": "osl-core.example-suite.v3",
        "language_version": "0.3",
        "example_count": len(records),
        "accepted_count": sum(record["accepted"] for record in records),
        "expected_rejection_count": sum(not record["accepted"] for record in records),
        "passed_count": sum(record["passed"] for record in records),
        "audit_count": len(audit_records),
        "audit_passed_count": sum(record["passed"] for record in audit_records),
        "failed_count": len(failures),
        "records": records,
        "audit_records": audit_records,
    }
    payload["suite_digest"] = digest(payload)
    return payload


def information_flow_report(example_dir: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in sorted(example_dir.glob("*.osl")):
        statements = parse_program(path.read_text(encoding="utf-8"))
        report = analyze_information_flow(statements)
        records.append({"file": path.name, **asdict(report)})
    explicit = sorted(record["file"] for record in records if record["explicit_leak_count"])
    expected = ["30_leaky_metadata_left.osl", "31_leaky_metadata_right.osl"]
    payload: dict[str, Any] = {
        "schema": "osl.core.information-flow-suite.v1",
        "language_version": "OSL-Core 0.3",
        "program_count": len(records),
        "explicit_leak_programs": explicit,
        "expected_explicit_leak_programs": expected,
        "unexpected_explicit_leak_programs": sorted(set(explicit) - set(expected)),
        "missing_expected_leak_programs": sorted(set(expected) - set(explicit)),
        "records": records,
        "claim_boundary": "Static explicit-dependency analysis for the finite secret-to-metadata grammar only; timing, implicit control flow, semantic steganography, latent vectors, and external tools remain outside the certificate.",
    }
    payload["all_checks_pass"] = not payload["unexpected_explicit_leak_programs"] and not payload["missing_expected_leak_programs"]
    payload["suite_digest"] = digest(payload)
    return payload


def session_report(example_dir: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in sorted(example_dir.glob("*.osl")):
        if _expected_error(path) is not None:
            continue
        runtime = OSLRuntime()
        runtime.run_file(path)
        for name, protocol in sorted(runtime.state.sessions.items()):
            report = verify_session_protocol(protocol)
            record = {"file": path.name, **asdict(report)}
            record["verification_declared"] = bool(protocol.verification is not None)
            record["legacy_order_monitor_only"] = not record["verification_declared"]
            records.append(record)
    declared = [record for record in records if record["verification_declared"]]
    legacy = [record for record in records if record["legacy_order_monitor_only"]]
    payload: dict[str, Any] = {
        "schema": "osl.core.session-verification-suite.v1",
        "language_version": "OSL-Core 0.3",
        "session_count": len(records),
        "declared_verified_session_count": len(declared),
        "declared_verified_session_pass_count": sum(record["all_checks_pass"] for record in declared),
        "legacy_order_monitor_session_count": len(legacy),
        "records": records,
        "claim_boundary": "Formal graph verification is claimed only for protocols that explicitly declared terminal states and executed verify_session. Older accepted examples remain order monitors, not liveness certificates. Asynchronous queues, recursive protocols, scheduler fairness, and general multiparty liveness are not established.",
    }
    payload["all_checks_pass"] = bool(declared and all(record["all_checks_pass"] for record in declared))
    payload["suite_digest"] = digest(payload)
    return payload


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    examples = root / "examples"
    outputs: dict[str, dict[str, Any]] = {
        "EXAMPLE_RESULTS.json": example_report(examples),
        "COMPACT_CLOSURE_CERTIFICATE.json": explore_kernel(),
        "FINITE_METACORE_CERTIFICATE.json": build_metacore_report(),
        "INDEPENDENT_KERNEL_REPORT.json": verify_directory(examples),
        "TRACE_VERIFICATION.json": verify_trace_directory(examples),
        "INFORMATION_FLOW_REPORT.json": information_flow_report(examples),
        "SESSION_VERIFICATION_REPORT.json": session_report(examples),
    }
    for name, payload in outputs.items():
        _write(root / name, payload)

    index: dict[str, Any] = {
        "schema": "osl.core.v03-certificate-index.v1",
        "language_version": "OSL-Core 0.3",
        "artifacts": {
            name: {
                "sha256": sha256(root / name),
                "size_bytes": (root / name).stat().st_size,
                "all_checks_pass": payload.get("all_checks_pass", payload.get("aggregate", {}).get("all_checks_pass", payload.get("failed_count") == 0)),
            }
            for name, payload in sorted(outputs.items())
        },
        "claim_boundary": "The index binds several complementary finite certificates. Their conjunction is stronger than example testing, but it is not a proof-assistant verification of arbitrary OSL programs or the Python implementation itself.",
    }
    index["all_checks_pass"] = all(item["all_checks_pass"] for item in index["artifacts"].values())
    index["index_digest"] = digest(index)
    _write(root / "V03_CERTIFICATE_INDEX.json", index)
    print(json.dumps(index, indent=2, sort_keys=True))
    return 0 if index["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

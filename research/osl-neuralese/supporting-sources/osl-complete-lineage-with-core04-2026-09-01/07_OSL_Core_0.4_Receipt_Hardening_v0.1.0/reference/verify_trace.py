#!/usr/bin/env python3
"""Replay and verify source-to-receipt trace correspondence for OSL-Core 0.4."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

try:  # pragma: no cover
    from .osl_core import OSLRuntime, run_program
    from .osl_invariants import check_runtime_state, verify_audit_log
    from .osl_model import OSLError, OSLStaticError, digest
    from .osl_parser import parse_program
except ImportError:  # pragma: no cover
    from osl_core import OSLRuntime, run_program  # type: ignore
    from osl_invariants import check_runtime_state, verify_audit_log  # type: ignore
    from osl_model import OSLError, OSLStaticError, digest  # type: ignore
    from osl_parser import parse_program  # type: ignore


def _run_runtime(path: Path) -> tuple[OSLRuntime, bool, str | None]:
    runtime = OSLRuntime()
    try:
        runtime.run_file(path)
    except (OSLError, OSLStaticError) as exc:
        return runtime, False, str(exc)
    return runtime, True, None


def verify_program_trace(path: Path) -> dict[str, Any]:
    first_runtime, first_ok, first_error = _run_runtime(path)
    second_runtime, second_ok, second_error = _run_runtime(path)
    receipts = first_runtime.audit_log
    failures: list[str] = []

    chain = verify_audit_log(receipts)
    if not chain["all_checks_pass"]:
        failures.extend(f"chain:{item}" for item in chain["failed_checks"])

    if first_ok != second_ok or first_error != second_error:
        failures.append("replay_status")
    if first_runtime.state.snapshot() != second_runtime.state.snapshot():
        failures.append("replay_state")
    if first_runtime.audit_log != second_runtime.audit_log:
        failures.append("replay_receipts")

    invariant_report = check_runtime_state(
        first_runtime.state, audit_log=first_runtime.audit_log
    )
    if not invariant_report["all_checks_pass"]:
        failures.extend(f"invariant:{item}" for item in invariant_report["failures"])

    try:
        statements = parse_program(path.read_text(encoding="utf-8"))
    except Exception:
        statements = ()
    boundaries = [
        receipt
        for receipt in receipts
        if receipt.get("kind") in {"statement_commit", "statement_reject"}
    ]
    for index, boundary in enumerate(boundaries):
        if index > 0:
            previous = boundaries[index - 1]
            if boundary.get("before_semantic_digest") != previous.get(
                "after_semantic_digest"
            ):
                failures.append(f"statement_continuity:{index}")
        line_number = int(boundary.get("line_number", -1))
        matching = [statement for statement in statements if statement.line_number == line_number]
        if len(matching) != 1:
            failures.append(f"statement_line:{line_number}")
        else:
            statement = matching[0]
            if boundary.get("statement_kind") != statement.kind:
                failures.append(f"statement_kind:{line_number}")
            if boundary.get("source_digest") != digest(statement.source):
                failures.append(f"statement_source:{line_number}")

    terminal_kinds = [receipt.get("kind") for receipt in receipts[-3:]]
    if first_ok and "program_complete" not in terminal_kinds:
        failures.append("missing_program_complete")
    if not first_ok and statements and not any(
        receipt.get("kind") in {"statement_reject", "program_reject"}
        for receipt in receipts
    ):
        # Static rejection legitimately has no source-statement boundary receipt.
        if receipts:
            failures.append("missing_rejection_receipt")

    payload: dict[str, Any] = {
        "schema": "osl.core.program-trace-verification.v1",
        "file": path.name,
        "accepted": first_ok,
        "error": first_error,
        "statement_count": len(statements),
        "boundary_receipt_count": len(boundaries),
        "audit_receipt_count": len(receipts),
        "audit_chain_tip": chain["chain_tip"],
        "semantic_digest": first_runtime.state.semantic_digest(),
        "invariant_report_digest": invariant_report["report_digest"],
        "deterministic_replay": first_runtime.audit_log == second_runtime.audit_log,
        "failure_count": len(failures),
        "failures": failures,
        "all_checks_pass": not failures,
    }
    payload["verification_digest"] = digest(payload)
    return payload


def verify_directory(directory: Path) -> dict[str, Any]:
    records = [verify_program_trace(path) for path in sorted(directory.glob("*.osl"))]
    payload: dict[str, Any] = {
        "schema": "osl.core.trace-suite-verification.v1",
        "language": "OSL-Core 0.4",
        "program_count": len(records),
        "passed_count": sum(bool(record["all_checks_pass"]) for record in records),
        "failed_count": sum(not bool(record["all_checks_pass"]) for record in records),
        "records": records,
        "all_checks_pass": all(bool(record["all_checks_pass"]) for record in records),
        "claim_boundary": (
            "Deterministic replay and receipt correspondence for the packaged finite "
            "programs. This is not a universal proof for arbitrary external effects or "
            "untrusted neural attestations."
        ),
    }
    payload["suite_digest"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = verify_directory(args.path) if args.path.is_dir() else verify_program_trace(args.path)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

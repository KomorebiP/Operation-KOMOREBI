#!/usr/bin/env python3
"""Generate deterministic source-bound OSL-Core 0.4 conformance evidence.

The generator executes the frozen 66-program corpus, checks each observed
outcome against its ``# EXPECT-ERROR:`` marker, and independently verifies the
resulting terminal receipt trace against the exact source text.  It writes a
compact conformance report, the complete strict-kernel reports, and a
self-contained JSONL trace bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from osl_core import OSLError, OSLRuntime, OSLStaticError
from osl_kernel import KernelVerifier
from osl_model import digest


EXPECTED_EXAMPLE_COUNT = 66
TERMINAL_KINDS = {"program_complete", "program_reject"}
ZERO_DIGEST = "0" * 64


def canonical_json(value: Any) -> str:
    """Return the canonical JSON representation used for JSONL evidence."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    rendered = "".join(canonical_json(record) + "\n" for record in records)
    path.write_text(rendered, encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected_error(source: str) -> str | None:
    marker = "# EXPECT-ERROR:"
    for line in source.splitlines()[:5]:
        if line.startswith(marker):
            return line[len(marker) :].strip()
    return None


def _terminal_metadata(
    receipts: list[dict[str, Any]], error: Exception | None
) -> dict[str, Any]:
    terminals = [receipt for receipt in receipts if receipt.get("kind") in TERMINAL_KINDS]
    terminal = terminals[-1] if terminals else None
    terminal_kind = None if terminal is None else str(terminal.get("kind"))

    if terminal is not None and terminal.get("phase") is not None:
        phase = str(terminal["phase"])
    elif terminal_kind == "program_complete":
        phase = "complete"
    elif isinstance(error, OSLStaticError):
        phase = "static"
    elif terminal is not None and terminal.get("failed_line") is None:
        phase = "finalization"
    elif terminal_kind == "program_reject":
        phase = "runtime"
    else:
        phase = "missing"

    terminal_is_last = bool(
        terminal is not None
        and receipts
        and receipts[-1].get("kind") in TERMINAL_KINDS
        and receipts[-1].get("digest") == terminal.get("digest")
    )
    return {
        "terminal_kind": terminal_kind,
        "terminal_phase": phase,
        "terminal_count": len(terminals),
        "terminal_is_last": terminal_is_last,
        "terminal_index": None if terminal is None else terminal.get("index"),
        "terminal_step": None if terminal is None else terminal.get("step"),
        "terminal_digest": None if terminal is None else terminal.get("digest"),
        "audit_receipt_count": len(receipts),
        "audit_head_digest": receipts[-1].get("digest") if receipts else ZERO_DIGEST,
    }


def _outcome_matches(expected_error: str | None, error: Exception | None) -> bool:
    if expected_error is None:
        return error is None
    return error is not None and expected_error.lower() in str(error).lower()


def _terminal_matches(error: Exception | None, terminal: dict[str, Any]) -> bool:
    expected_kind = "program_complete" if error is None else "program_reject"
    return bool(
        terminal["terminal_count"] == 1
        and terminal["terminal_is_last"]
        and terminal["terminal_kind"] == expected_kind
    )


def _run_program(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    expected_error = _expected_error(source)
    runtime = OSLRuntime()
    error: Exception | None = None
    try:
        runtime.run_text(source, filename=path.name)
    except (OSLError, OSLStaticError) as exc:
        error = exc

    receipts = runtime.audit_log
    final_state = runtime.state.snapshot()
    terminal = _terminal_metadata(receipts, error)
    outcome_pass = _outcome_matches(expected_error, error)
    terminal_pass = _terminal_matches(error, terminal)
    kernel_report = KernelVerifier().verify(receipts, final_state, source=source)
    kernel_pass = bool(kernel_report.get("all_checks_pass"))
    source_digest = digest(source)

    conformance_record: dict[str, Any] = {
        "file": path.name,
        "source_digest": source_digest,
        "expected_error": expected_error,
        "runtime_accepted": error is None,
        "runtime_error_type": None if error is None else type(error).__name__,
        "runtime_error": None if error is None else str(error),
        "expected_outcome_matches": outcome_pass,
        "terminal_matches_outcome": terminal_pass,
        **terminal,
        "semantic_digest": runtime.state.semantic_digest(),
        "snapshot_digest": final_state.get("snapshot_digest"),
        "static_report_digest": (
            None
            if runtime.state.static_report is None
            else runtime.state.static_report.get("report_digest")
        ),
        "kernel_verification_digest": kernel_report.get("verification_digest"),
        "kernel_checks_pass": kernel_pass,
    }
    conformance_record["passed"] = bool(outcome_pass and terminal_pass and kernel_pass)
    conformance_record["evidence_profile"] = "v0.4-native"
    conformance_record["verification_status"] = (
        "V04_NATIVE_VERIFIED" if conformance_record["passed"] else "NOT_VERIFIED"
    )
    conformance_record["record_digest"] = digest(conformance_record)

    kernel_record: dict[str, Any] = {
        "file": path.name,
        "source_digest": source_digest,
        "expected_error": expected_error,
        "runtime_accepted": error is None,
        "runtime_error": None if error is None else str(error),
        **terminal,
        "kernel_report": kernel_report,
        "all_checks_pass": kernel_pass,
        "evidence_profile": "v0.4-native",
        "verification_status": (
            "V04_NATIVE_VERIFIED" if kernel_pass else "NOT_VERIFIED"
        ),
    }
    kernel_record["record_digest"] = digest(kernel_record)

    trace_record: dict[str, Any] = {
        "schema": "osl.core04.source-bound-trace.v1",
        "language_version": "OSL-Core 0.4",
        "file": path.name,
        "source": source,
        "source_digest": source_digest,
        "expected_error": expected_error,
        "runtime_accepted": error is None,
        "runtime_error_type": None if error is None else type(error).__name__,
        "runtime_error": None if error is None else str(error),
        **terminal,
        "receipts": receipts,
        "final_state": final_state,
        "kernel_verification_digest": kernel_report.get("verification_digest"),
        "kernel_checks_pass": kernel_pass,
        "evidence_profile": "v0.4-native",
        "verification_status": (
            "V04_NATIVE_VERIFIED" if kernel_pass else "NOT_VERIFIED"
        ),
    }
    trace_record["record_digest"] = digest(trace_record)

    return {
        "conformance": conformance_record,
        "kernel": kernel_record,
        "trace": trace_record,
    }


def _phase_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(record["terminal_phase"]) for record in records).items()))


def generate(example_dir: Path, output_dir: Path) -> dict[str, Any]:
    paths = sorted(example_dir.glob("*.osl"), key=lambda path: path.name)
    results = [_run_program(path) for path in paths]
    conformance_records = [result["conformance"] for result in results]
    kernel_records = [result["kernel"] for result in results]
    trace_records = [result["trace"] for result in results]

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "CORE04_TRACE_BUNDLE.jsonl"
    _write_jsonl(trace_path, trace_records)
    trace_sha256 = _sha256(trace_path)
    source_set = [
        {"file": record["file"], "source_digest": record["source_digest"]}
        for record in conformance_records
    ]

    exact_corpus = len(paths) == EXPECTED_EXAMPLE_COUNT
    conformance_report: dict[str, Any] = {
        "schema": "osl.core04.conformance-suite.v1",
        "language_version": "OSL-Core 0.4",
        "evidence_profile": "v0.4-native",
        "expected_example_count": EXPECTED_EXAMPLE_COUNT,
        "example_count": len(conformance_records),
        "accepted_count": sum(record["runtime_accepted"] for record in conformance_records),
        "rejected_count": sum(not record["runtime_accepted"] for record in conformance_records),
        "expected_error_count": sum(record["expected_error"] is not None for record in conformance_records),
        "expected_outcome_match_count": sum(record["expected_outcome_matches"] for record in conformance_records),
        "terminal_receipt_count": sum(record["terminal_count"] for record in conformance_records),
        "terminal_match_count": sum(record["terminal_matches_outcome"] for record in conformance_records),
        "terminal_phase_counts": _phase_counts(conformance_records),
        "audit_receipt_count": sum(record["audit_receipt_count"] for record in conformance_records),
        "passed_count": sum(record["passed"] for record in conformance_records),
        "failed_count": sum(not record["passed"] for record in conformance_records),
        "source_set_digest": digest(source_set),
        "trace_bundle_file": trace_path.name,
        "trace_bundle_sha256": trace_sha256,
        "records": conformance_records,
        "claim_boundary": (
            "Conformance is established only for the frozen 66-program OSL-Core "
            "corpus and its declared expected rejections."
        ),
    }
    conformance_report["all_checks_pass"] = bool(
        exact_corpus and conformance_records and all(record["passed"] for record in conformance_records)
    )
    conformance_report["verification_status"] = (
        "V04_NATIVE_VERIFIED"
        if conformance_report["all_checks_pass"]
        else "NOT_VERIFIED"
    )
    conformance_report["suite_digest"] = digest(conformance_report)

    counter_totals: Counter[str] = Counter()
    for record in kernel_records:
        counters = record["kernel_report"].get("counters", {})
        if isinstance(counters, dict):
            for name, value in counters.items():
                if isinstance(value, int) and not isinstance(value, bool):
                    counter_totals[str(name)] += value

    kernel_report: dict[str, Any] = {
        "schema": "osl.core04.strict-kernel-suite.v1",
        "language_version": "OSL-Core 0.4",
        "evidence_profile": "v0.4-native",
        "expected_program_count": EXPECTED_EXAMPLE_COUNT,
        "program_count": len(kernel_records),
        "verified_program_count": sum(record["all_checks_pass"] for record in kernel_records),
        "independent_verified_program_count": sum(
            bool(record["kernel_report"].get("independent_checks_pass"))
            for record in kernel_records
        ),
        "supplementary_replay_verified_count": sum(
            bool(
                record["kernel_report"]
                .get("supplementary_same_runtime_replay", {})
                .get("performed")
                and record["kernel_report"]
                .get("supplementary_same_runtime_replay", {})
                .get("receipt_match")
                and record["kernel_report"]
                .get("supplementary_same_runtime_replay", {})
                .get("final_state_match")
            )
            for record in kernel_records
        ),
        "failed_program_count": sum(not record["all_checks_pass"] for record in kernel_records),
        "runtime_accepted_count": sum(record["runtime_accepted"] for record in kernel_records),
        "runtime_rejected_count": sum(not record["runtime_accepted"] for record in kernel_records),
        "terminal_receipt_count": sum(record["terminal_count"] for record in kernel_records),
        "terminal_phase_counts": _phase_counts(kernel_records),
        "audit_receipt_count": sum(record["audit_receipt_count"] for record in kernel_records),
        "counter_totals": dict(sorted(counter_totals.items())),
        "source_set_digest": digest(source_set),
        "trace_bundle_file": trace_path.name,
        "trace_bundle_sha256": trace_sha256,
        "records": kernel_records,
        "claim_boundary": (
            "The strict kernel independently replays protected module, identity, "
            "packet, proof, memory, capability, and action tables, plus transaction "
            "lifecycle and protected rollback/secret-commitment state, for the "
            "packaged corpus. A separately labeled same-runtime replay "
            "binds delegated interpreter semantics; numerical algebra and complete "
            "session-graph refinement are not independently reconstructed and "
            "retain their named finite verifiers. This is not principal "
            "authentication or a proof of the Python implementation."
        ),
    }
    kernel_report["all_checks_pass"] = bool(
        exact_corpus
        and kernel_records
        and all(record["all_checks_pass"] for record in kernel_records)
        and kernel_report["independent_verified_program_count"]
        == EXPECTED_EXAMPLE_COUNT
        and kernel_report["supplementary_replay_verified_count"]
        == EXPECTED_EXAMPLE_COUNT
    )
    kernel_report["verification_status"] = (
        "V04_NATIVE_VERIFIED" if kernel_report["all_checks_pass"] else "NOT_VERIFIED"
    )
    kernel_report["suite_digest"] = digest(kernel_report)

    conformance_path = output_dir / "CORE04_CONFORMANCE_REPORT.json"
    kernel_path = output_dir / "CORE04_KERNEL_REPORT.json"
    _write_json(conformance_path, conformance_report)
    _write_json(kernel_path, kernel_report)

    summary: dict[str, Any] = {
        "schema": "osl.core04.evidence-generation.v1",
        "language_version": "OSL-Core 0.4",
        "example_count": len(paths),
        "conformance_pass": conformance_report["all_checks_pass"],
        "kernel_pass": kernel_report["all_checks_pass"],
        "artifacts": {
            conformance_path.name: _sha256(conformance_path),
            kernel_path.name: _sha256(kernel_path),
            trace_path.name: trace_sha256,
        },
    }
    summary["all_checks_pass"] = bool(
        summary["conformance_pass"] and summary["kernel_pass"]
    )
    summary["generation_digest"] = digest(summary)
    return summary


def main(argv: Iterable[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Generate deterministic OSL-Core 0.4 conformance evidence."
    )
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=root / "examples",
        help="Directory containing the frozen .osl corpus.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root,
        help="Destination directory for the three Core 0.4 evidence artifacts.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    summary = generate(args.examples_dir.resolve(), args.output_dir.resolve())
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0 if summary["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

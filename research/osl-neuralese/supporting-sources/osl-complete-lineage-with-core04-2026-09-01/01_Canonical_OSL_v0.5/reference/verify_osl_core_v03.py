#!/usr/bin/env python3
"""Unified finite verification for OSL-Core 0.3.

This script combines four deliberately distinct evidence layers:

1. source-program conformance and paired public-projection audits;
2. deterministic source-to-receipt replay checks;
3. an independent receipt/proof kernel over emitted traces;
4. two exhaustive finite transition models.

The result is a finite mechanized certificate.  It is not a proof-assistant
verification of the complete Python implementation and is not a universal
security proof for unbounded programs or external effects.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

try:  # pragma: no cover - package/script dual use
    from .audit_noninterference import audit
    from .osl_core import run_program
    from .osl_formal_kernel import explore_kernel
    from .osl_information_flow import analyze_information_flow
    from .osl_kernel import verify_directory as verify_kernel_directory
    from .osl_metacore import build_report as build_metacore_report
    from .osl_model import digest
    from .osl_parser import parse_and_check
    from .verify_trace import verify_directory as verify_trace_directory
except ImportError:  # pragma: no cover
    from audit_noninterference import audit  # type: ignore
    from osl_core import run_program  # type: ignore
    from osl_formal_kernel import explore_kernel  # type: ignore
    from osl_information_flow import analyze_information_flow  # type: ignore
    from osl_kernel import verify_directory as verify_kernel_directory  # type: ignore
    from osl_metacore import build_report as build_metacore_report  # type: ignore
    from osl_model import digest  # type: ignore
    from osl_parser import parse_and_check  # type: ignore
    from verify_trace import verify_directory as verify_trace_directory  # type: ignore


def expected_error(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines()[:5]:
        marker = "# EXPECT-ERROR:"
        if line.startswith(marker):
            return line[len(marker) :].strip()
    return None


def conformance_report(examples: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in sorted(examples.glob("*.osl")):
        expected = expected_error(path)
        result = run_program(path)
        accepted = bool(result["ok"])
        if expected is None:
            passed = accepted
        else:
            passed = (not accepted) and expected.lower() in str(result["error"]).lower()
        records.append(
            {
                "file": path.name,
                "expected_error": expected,
                "accepted": accepted,
                "passed": passed,
                "detail": "accepted" if accepted else result["error"],
                "snapshot_digest": result["state"]["snapshot_digest"],
                "audit_receipt_count": int(result.get("audit", {}).get("receipt_count", 0)),
                "audit_chain_tip": result.get("audit", {}).get("head_digest"),
            }
        )

    audit_specs = (
        (
            "safe_metadata_pair",
            examples / "28_safe_metadata_left.osl",
            examples / "29_safe_metadata_right.osl",
            True,
        ),
        (
            "leaky_metadata_pair",
            examples / "30_leaky_metadata_left.osl",
            examples / "31_leaky_metadata_right.osl",
            False,
        ),
    )
    audits: list[dict[str, Any]] = []
    for name, left, right, expected_noninterference in audit_specs:
        result = audit(left, right)
        passed = bool(result.get("ok")) and (
            bool(result.get("noninterference")) == expected_noninterference
        )
        audits.append(
            {
                "name": name,
                "left": left.name,
                "right": right.name,
                "expected_noninterference": expected_noninterference,
                "observed_noninterference": result.get("noninterference"),
                "difference_count": result.get("difference_count"),
                "passed": passed,
                "audit_digest": result.get("audit_digest"),
            }
        )

    safe_statements, _ = parse_and_check(
        (examples / "28_safe_metadata_left.osl").read_text(encoding="utf-8")
    )
    leaky_statements, _ = parse_and_check(
        (examples / "30_leaky_metadata_left.osl").read_text(encoding="utf-8")
    )
    safe_flow = analyze_information_flow(safe_statements)
    leaky_flow = analyze_information_flow(leaky_statements)

    payload: dict[str, Any] = {
        "schema": "osl.core.v03-conformance.v1",
        "language": "OSL-Core 0.3",
        "program_count": len(records),
        "accepted_program_count": sum(record["accepted"] for record in records),
        "expected_rejection_count": sum(not record["accepted"] for record in records),
        "passed_program_count": sum(record["passed"] for record in records),
        "audit_count": len(audits),
        "passed_audit_count": sum(item["passed"] for item in audits),
        "static_information_flow": {
            "safe_noninterference": safe_flow.noninterference_in_supported_fragment,
            "safe_report_digest": safe_flow.report_digest,
            "leak_detected": not leaky_flow.noninterference_in_supported_fragment,
            "leaky_path_count": leaky_flow.explicit_leak_count,
            "leaky_report_digest": leaky_flow.report_digest,
        },
        "records": records,
        "audits": audits,
        "all_checks_pass": all(record["passed"] for record in records)
        and all(item["passed"] for item in audits)
        and safe_flow.noninterference_in_supported_fragment
        and not leaky_flow.noninterference_in_supported_fragment,
    }
    payload["report_digest"] = digest(payload)
    return payload


def build_unified_report(root: Path) -> dict[str, Any]:
    examples = root / "examples"
    conformance = conformance_report(examples)
    trace = verify_trace_directory(examples)
    receipt_kernel = verify_kernel_directory(examples)
    abstract_kernel = explore_kernel()
    metacore = build_metacore_report()

    checks = {
        "program_conformance": bool(conformance["all_checks_pass"]),
        "trace_replay_and_boundaries": bool(trace["all_checks_pass"]),
        "independent_receipt_kernel": bool(receipt_kernel["all_checks_pass"]),
        "abstract_kernel_fixpoint": bool(abstract_kernel["all_checks_pass"]),
        "decomposed_metacore_fixpoints": bool(
            metacore["aggregate"]["all_checks_pass"]
        ),
    }
    payload: dict[str, Any] = {
        "schema": "osl.core.v03-unified-verification.v1",
        "language": "OSL-Core 0.3",
        "checks": checks,
        "summary": {
            "source_program_count": conformance["program_count"],
            "source_programs_matching_specification": conformance[
                "passed_program_count"
            ],
            "accepted_program_count": conformance["accepted_program_count"],
            "expected_rejection_count": conformance["expected_rejection_count"],
            "paired_audit_count": conformance["audit_count"],
            "trace_verified_program_count": trace["passed_count"],
            "independent_kernel_verified_program_count": receipt_kernel[
                "verified_program_count"
            ],
            "independent_kernel_receipt_count": receipt_kernel["receipt_count"],
            "independent_kernel_proof_count": receipt_kernel["proof_count"],
            "abstract_kernel_reachable_states": abstract_kernel[
                "reachable_state_count"
            ],
            "abstract_kernel_transition_count": abstract_kernel["transition_count"],
            "metacore_reachable_states": metacore["aggregate"][
                "reachable_state_count"
            ],
            "metacore_transition_attempt_count": metacore["aggregate"][
                "transition_attempt_count"
            ],
            "total_finite_states_explored": abstract_kernel[
                "reachable_state_count"
            ]
            + metacore["aggregate"]["reachable_state_count"],
            "total_finite_transition_checks": abstract_kernel["transition_count"]
            + metacore["aggregate"]["transition_attempt_count"],
        },
        "certificate_digests": {
            "conformance": conformance["report_digest"],
            "trace": trace["suite_digest"],
            "receipt_kernel": receipt_kernel["suite_digest"],
            "abstract_kernel": abstract_kernel["certificate_digest"],
            "abstract_kernel_state_graph": abstract_kernel["state_graph_digest"],
            "decomposed_metacore": metacore["report_digest"],
        },
        "all_checks_pass": all(checks.values()),
        "claim_boundary": (
            "Finite evidence for the packaged OSL-Core 0.3 source language, "
            "receipt semantics, and two abstract transition models. The Python "
            "implementation, external effects, untrusted neural attestations, "
            "unbounded recursive protocols, and general information-flow security "
            "are not proved by this certificate."
        ),
        "layers": {
            "conformance": conformance,
            "trace": trace,
            "receipt_kernel": receipt_kernel,
            "abstract_kernel": abstract_kernel,
            "decomposed_metacore": metacore,
        },
    }
    payload["verification_digest"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = build_unified_report(args.root)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

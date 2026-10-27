#!/usr/bin/env python3
"""Generate deterministic Core 0.5 conformance and semantic evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from osl_core import OSLError, OSLRuntime, OSLStaticError
from osl_kernel import KernelVerifier
from osl_model import canonical_json, digest
from osl_semantic_kernel import verify_semantic_independence


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def expected_rejection(source: str) -> bool:
    return any(line.startswith("# EXPECT-ERROR:") for line in source.splitlines())


def run_source(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    runtime = OSLRuntime()
    runtime_error: str | None = None
    runtime_error_type: str | None = None
    try:
        runtime.run_text(source, filename=str(path.relative_to(ROOT)))
    except (OSLError, OSLStaticError) as exc:
        runtime_error = str(exc)
        runtime_error_type = type(exc).__name__

    final_state = runtime.state.snapshot()
    base_report = KernelVerifier().verify(runtime.audit_log, final_state, source=source)
    semantic_report = verify_semantic_independence(source, runtime.audit_log, final_state)
    expected_reject = expected_rejection(source)
    runtime_accepted = runtime_error is None
    expected_match = runtime_accepted is (not expected_reject)
    terminal = runtime.audit_log[-1] if runtime.audit_log else {}
    passed = bool(
        expected_match
        and base_report.get("all_checks_pass") is True
        and base_report.get("independent_checks_pass") is True
        and semantic_report.get("independent_checks_pass") is True
        and terminal.get("kind") in {"program_complete", "program_reject"}
    )

    summary = {
        "file": str(path.relative_to(ROOT)),
        "source_digest": digest(source),
        "expected_rejection": expected_reject,
        "runtime_accepted": runtime_accepted,
        "runtime_error_type": runtime_error_type,
        "runtime_error": runtime_error,
        "expected_outcome_match": expected_match,
        "receipt_count": len(runtime.audit_log),
        "terminal_kind": terminal.get("kind"),
        "terminal_phase": terminal.get("phase"),
        "terminal_digest": terminal.get("digest"),
        "base_independent_checks_pass": base_report.get("independent_checks_pass") is True,
        "supplementary_replay_pass": bool(
            base_report.get("supplementary_same_runtime_replay", {}).get("receipt_match")
            and base_report.get("supplementary_same_runtime_replay", {}).get("final_state_match")
        ),
        "semantic_independence_checks": semantic_report.get("checks", {}),
        "semantic_independence_pass": semantic_report.get("independent_checks_pass") is True,
        "base_verification_digest": base_report.get("verification_digest"),
        "semantic_suite_digest": semantic_report.get("suite_digest"),
        "passed": passed,
    }
    summary["record_digest"] = digest(summary)

    trace = {
        "schema": "osl.core05.source-bound-trace.v1",
        "language_version": "OSL-Core 0.5",
        "evidence_profile": "v0.5-semantic-independence",
        "file": str(path.relative_to(ROOT)),
        "source": source,
        "source_digest": digest(source),
        "runtime_accepted": runtime_accepted,
        "runtime_error_type": runtime_error_type,
        "runtime_error": runtime_error,
        "receipts": runtime.audit_log,
        "final_state": final_state,
        "base_kernel_report": base_report,
        "semantic_independence_report": semantic_report,
        "verification_status": "V05_SEMANTIC_INDEPENDENCE_VERIFIED" if passed else "NOT_VERIFIED",
    }
    trace["record_digest"] = digest(trace)
    return summary, trace


def generate(paths: list[Path], output_dir: Path) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for path in paths:
        summary, trace = run_source(path)
        summaries.append(summary)
        traces.append(trace)

    phases = Counter(str(record.get("terminal_phase")) for record in summaries)
    receipt_count = sum(int(record["receipt_count"]) for record in summaries)
    accepted = sum(bool(record["runtime_accepted"]) for record in summaries)
    passed = sum(bool(record["passed"]) for record in summaries)
    suite = {
        "schema": "osl.core05.conformance-suite.v1",
        "language_version": "OSL-Core 0.5",
        "receipt_schema": "osl.core.receipt.v2",
        "evidence_profile": "v0.5-semantic-independence",
        "program_count": len(summaries),
        "accepted_count": accepted,
        "rejected_count": len(summaries) - accepted,
        "receipt_count": receipt_count,
        "terminal_phase_counts": dict(sorted(phases.items())),
        "base_independent_verified_count": sum(
            bool(record["base_independent_checks_pass"]) for record in summaries
        ),
        "semantic_independence_verified_count": sum(
            bool(record["semantic_independence_pass"]) for record in summaries
        ),
        "supplementary_replay_verified_count": sum(
            bool(record["supplementary_replay_pass"]) for record in summaries
        ),
        "passed_count": passed,
        "failed_count": len(summaries) - passed,
        "records": summaries,
        "all_checks_pass": bool(summaries and passed == len(summaries)),
        "claim_boundary": (
            "Finite corpus evidence. Independent semantic modules cover numerical "
            "operators, contracts, sessions, metadata-facing state, and audit "
            "intrinsics in addition to the protected-state kernel. General assertion "
            "truth, full cross-domain transaction digests, and all rejection causes "
            "are not yet independently decided."
        ),
    }
    suite["suite_digest"] = digest(suite)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "CORE05_CONFORMANCE_REPORT.json", suite)
    trace_path = output_dir / "CORE05_TRACE_BUNDLE.jsonl"
    trace_path.write_text(
        "".join(canonical_json(record) + "\n" for record in traces),
        encoding="utf-8",
    )

    component_counts = Counter()
    for trace in traces:
        checks = trace["semantic_independence_report"].get("checks", {})
        for name, ok in checks.items():
            if ok:
                component_counts[name] += 1
    semantic_summary = {
        "schema": "osl.core05.semantic-suite-summary.v1",
        "language_version": "OSL-Core 0.5",
        "program_count": len(traces),
        "component_verified_counts": dict(sorted(component_counts.items())),
        "semantic_independence_verified_count": sum(
            trace["semantic_independence_report"].get("independent_checks_pass") is True
            for trace in traces
        ),
        "trace_bundle_file": trace_path.name,
        "trace_bundle_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "all_checks_pass": suite["all_checks_pass"],
        "remaining_delegated_semantics": (
            traces[0]["semantic_independence_report"]["remaining_delegated_semantics"]
            if traces
            else []
        ),
    }
    semantic_summary["suite_digest"] = digest(semantic_summary)
    write_json(output_dir / "CORE05_SEMANTIC_REPORT.json", semantic_summary)
    return suite


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", type=Path, default=ROOT / "examples")
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--bridge", action="store_true")
    args = parser.parse_args()
    paths = sorted(args.examples.glob("*.osl"))
    result = generate(paths, args.output)
    print(canonical_json({
        "program_count": result["program_count"],
        "passed_count": result["passed_count"],
        "receipt_count": result["receipt_count"],
        "all_checks_pass": result["all_checks_pass"],
    }))
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

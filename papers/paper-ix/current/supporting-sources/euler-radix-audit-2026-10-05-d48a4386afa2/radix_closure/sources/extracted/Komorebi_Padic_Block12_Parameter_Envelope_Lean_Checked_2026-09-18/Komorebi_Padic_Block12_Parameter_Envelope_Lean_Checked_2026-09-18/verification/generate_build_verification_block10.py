#!/usr/bin/env python3
"""Assemble the durable Block 10 verification receipt from completed evidence."""
from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    source = load("results/static_source_audit_block10.json")
    axioms = load("results/axiom_audit_block10.json")
    controls = load("results/kernel_controls_block10.json")
    vectors = load("results/lean_vector_replay_block10.json")
    radix = load("results/radix_compiler_audit.json")
    suffix = load("results/suffix_window_audit.json")
    boundary = load("results/final_fiber_boundary_audit.json")
    complexity = load("results/compiler_complexity_audit.json")
    closed = load("results/representative_budget_closed_form_audit.json")

    build_log = (ROOT / "logs/lake_build_clean_block10.log").read_text(encoding="utf-8")
    jobs_match = re.search(r"Build completed successfully \((\d+) jobs\)\.", build_log)
    jobs = int(jobs_match.group(1)) if jobs_match else None
    build_time = (ROOT / "logs/lake_build_clean_block10.time").read_text(encoding="utf-8")
    elapsed_match = re.search(r"elapsed_seconds=([0-9.]+)", build_time)
    rss_match = re.search(r"max_rss_kb=(\d+)", build_time)

    oleans = sorted((ROOT / "compiled_rc2").rglob("*.olean"))
    ileans = sorted((ROOT / "compiled_rc2").rglob("*.ilean"))
    compiled = len(oleans) + len(ileans)
    finite_total = (
        int(radix["total_checks"])
        + int(suffix["total_recorded_checks"])
        + int(boundary["total_recorded_checks_and_cases"])
        + int(complexity["total_recorded_checks_and_cases"])
        + int(closed["total_recorded_checks_and_cases"])
    )

    required_statuses = [
        source.get("status"), axioms.get("status"), controls.get("status"),
        vectors.get("status"), radix.get("status"), suffix.get("status"),
        boundary.get("status"), complexity.get("status"), closed.get("status"),
    ]
    passed = (
        all(status == "PASS" for status in required_statuses)
        and jobs == 1160
        and compiled == 34
        and vectors.get("example_count") == 5918
        and source.get("block10_theorem_count") == 152
        and not source.get("changed_predecessor_theorem_statements")
        and not source.get("missing_predecessor_theorems")
        and not axioms.get("unexpected_axioms")
    )

    report = {
        "schema": "komorebi-padic-block10-build-verification-v1",
        "status": "PASS" if passed else "FAIL",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "authoritative_predecessor": "Komorebi_Padic_COMPLETE_2026-09-18_Block09_Complexity_Certificate_Lean_Checked.zip",
        "toolchain": {
            "lean": "Lean 4.34.0-rc2",
            "lean_commit": "6a10ac8c22beadecabdbb0919c2b50214762f91d",
            "lake": "5.0.0-src+6a10ac8",
            "mathlib_revision": "aeb72f1e9981b6d35b426b16dca7759be3e7ba06",
            "stable_4_34_0_mathlib_5ed296_status": "NOT_CHECKED",
        },
        "runtime_archive": {
            "path": "/mnt/data/lean_compact_runtime/Komorebi_Portable_Lean_4.34.0-rc2_Compact.tar.xz",
            "sha256": "f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7",
            "hash_verified": True,
            "extraction_succeeded": True,
            "standalone_xz_test": "INCONCLUSIVE_TIMEOUT",
        },
        "clean_build": {
            "status": "PASS" if jobs == 1160 else "FAIL",
            "warning_as_error": True,
            "jobs": jobs,
            "elapsed_seconds": float(elapsed_match.group(1)) if elapsed_match else None,
            "max_rss_kb": int(rss_match.group(1)) if rss_match else None,
            "log": "logs/lake_build_clean_block10.log",
            "time_receipt": "logs/lake_build_clean_block10.time",
        },
        "lean": {
            "production_files": source["lean_file_count"],
            "module_count": source["module_count"],
            "theorems": source["block10_theorem_count"],
            "definitions": source["declaration_counts"]["def"],
            "structures": source["declaration_counts"]["structure"],
            "predecessor_theorems": source["predecessor_theorem_count"],
            "new_theorems": len(source["added_theorems"]),
            "changed_predecessor_theorem_statements": len(source["changed_predecessor_theorem_statements"]),
            "compiled_olean_ilean_artifacts": compiled,
            "olean_count": len(oleans),
            "ilean_count": len(ileans),
            "native_decide_files": vectors["file_count"],
            "native_decide_examples": vectors["example_count"],
            "axiom_audit_status": axioms["status"],
            "axiom_audit_theorems": axioms["theorem_count"],
            "observed_axioms": axioms["observed_axioms"],
            "unexpected_axioms": axioms["unexpected_axioms"],
            "negative_controls": controls["status"],
            "placeholder_or_local_axiom_violations": source["placeholder_or_axiom_violations"],
        },
        "computation": {
            "block05_radix": int(radix["total_checks"]),
            "block06_suffix": int(suffix["total_recorded_checks"]),
            "block08_boundary": int(boundary["total_recorded_checks_and_cases"]),
            "block09_complexity": int(complexity["total_recorded_checks_and_cases"]),
            "block10_closed_form": int(closed["total_recorded_checks_and_cases"]),
            "combined_exact_checks_and_cases": finite_total,
            "failure_count": (
                len(radix.get("failures", []))
                + int(suffix.get("failure_count", 0))
                + int(boundary.get("failure_count", 0))
                + int(complexity.get("failure_count", 0))
                + int(closed.get("failure_count", 0))
            ),
        },
        "evidence_sha256": {
            rel: sha256(ROOT / rel)
            for rel in [
                "lean/KomorebiPadic/RepresentativeBudgetClosedForm.lean",
                "results/static_source_audit_block10.json",
                "results/axiom_audit_block10.json",
                "results/kernel_controls_block10.json",
                "results/lean_vector_replay_block10.json",
                "results/representative_budget_closed_form_audit.json",
                "logs/lake_build_clean_block10.log",
            ]
        },
        "inconclusive_or_corrected_attempts": [
            {
                "kind": "environment_timeout",
                "description": "Standalone xz integrity testing exceeded the outer command window. The archive SHA-256 matched exactly, and a separate extraction plus Lean build succeeded; the timed-out xz test itself is not counted as a pass.",
            },
            {
                "kind": "source_integration_error",
                "description": "An early edit placed a root import after declarations, and Lean rejected it as an invalid import command. The import was moved into the import block; theorem statements were unchanged.",
            },
            {
                "kind": "aggregate_vector_timeout",
                "description": "The first aggregate Block 10 vector replay exceeded its outer command window after nine successful files. All 45 constituent vector files were subsequently rerun in bounded batches and passed with individual receipts.",
            },
            {
                "kind": "initial_vector_batch_timeout",
                "description": "The first closed-form vector batch stopped after 14 of 17 files under its aggregate execution window. Files 15--17 were rerun separately and passed; the incomplete batch was not treated as a pass.",
            },
        ],
        "proof_boundary": {
            "universal_proof": "Lean kernel checking of the exact all-natural closed form and prime-base compiler bound.",
            "finite_evidence": "Python exact-integer audits and native_decide vectors over the recorded finite domains.",
            "nonclaims": [
                "No stable Lean 4.34.0 plus mathlib 5ed296 compatibility claim.",
                "No end-to-end compiler theorem for composite bases.",
                "No asymptotic optimality or tightness claim for the compiler envelope.",
                "No novelty or priority claim.",
            ],
        },
    }
    output = ROOT / "results" / "BUILD_VERIFICATION_BLOCK10.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "jobs": jobs,
        "compiled": compiled,
        "native_decide": vectors["example_count"],
        "finite_total": finite_total,
        "theorems": source["block10_theorem_count"],
    }, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

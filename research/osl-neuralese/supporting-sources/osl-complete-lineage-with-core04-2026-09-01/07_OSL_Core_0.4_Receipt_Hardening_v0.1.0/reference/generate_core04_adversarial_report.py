#!/usr/bin/env python3
"""Run the fixed 24-case Core 0.4 adversarial gate."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from osl_model import digest


CASES = (
    "tests/test_core04_lifecycle.py::test_empty_trace_is_not_a_valid_empty_program",
    "tests/test_core04_lifecycle.py::test_missing_terminal_is_rejected_after_full_chain_rehash",
    "tests/test_core04_lifecycle.py::test_double_terminal_is_rejected_after_full_chain_rehash",
    "tests/test_core04_lifecycle.py::test_terminal_must_be_last_even_when_the_chain_is_rehashed",
    "tests/test_core04_lifecycle.py::test_receipts_are_bound_to_the_exact_source",
    "tests/test_core04_lifecycle.py::test_terminal_semantic_digest_is_not_a_decorative_field",
    "tests/test_core04_capability.py::test_kernel_rejects_fully_rehashed_trace_missing_grant",
    "tests/test_core04_capability.py::test_kernel_rejects_fully_rehashed_forged_grant_digest",
    "tests/test_core04_capability.py::test_kernel_rejects_fully_rehashed_execution_after_revoke",
    "tests/test_core04_capability.py::test_kernel_rejects_fully_rehashed_expired_execution",
    "tests/test_core04_capability.py::test_kernel_rejects_fully_rehashed_duplicate_execute",
    "tests/test_core04_capability.py::test_kernel_rejects_fully_rehashed_duplicate_feedback",
    "tests/test_core04_capability.py::test_kernel_rejects_exact_final_capability_mismatch",
    "tests/test_core04_proof.py::test_kernel_rejects_rehashed_false_primitive_access_proof",
    "tests/test_core04_proof.py::test_kernel_rejects_duplicate_construction_that_resets_linear_proof",
    "tests/test_core04_proof.py::test_capability_proof_does_not_revive_after_identical_regrant",
    "tests/test_core04_proof.py::test_kernel_rejects_missing_proof_in_final_snapshot",
    "tests/test_core04_proof.py::test_kernel_rejects_trace_without_terminal_receipt",
    "tests/test_core04_provenance.py::test_rejects_fully_rehashed_observe_constructor_forgery",
    "tests/test_core04_provenance.py::test_rejects_fully_rehashed_communicated_field_forgery",
    "tests/test_core04_provenance.py::test_rejects_fully_rehashed_memory_record_mismatch",
    "tests/test_core04_provenance.py::test_rejects_fully_rehashed_admission_with_bogus_proof_digests",
    "tests/test_core04_provenance.py::test_rejects_fully_rehashed_unknown_receipt_kind",
    "tests/test_core04_provenance.py::test_communication_cannot_launder_a_quarantined_packet",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(
        value
        for value in (str(root / "reference"), env.get("PYTHONPATH", ""))
        if value
    )
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        *CASES,
    ]
    proc = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (proc.stdout + proc.stderr).strip()
    match = re.search(r"(\d+) passed", output)
    passed = int(match.group(1)) if match else 0
    payload = {
        "schema": "osl.core04.adversarial-suite.v1",
        "language_version": "OSL-Core 0.4",
        "case_count": len(CASES),
        "passed_count": passed,
        "failed_count": len(CASES) - passed,
        "cases": list(CASES),
        "case_set_digest": digest(CASES),
        "pytest_exit_code": proc.returncode,
        "pytest_output_tail": (
            f"{passed} passed" if match else (output.splitlines()[-1] if output else "")
        ),
        "all_checks_pass": proc.returncode == 0 and passed == len(CASES),
        "claim_boundary": (
            "These are fixed regression witnesses, not exhaustive security testing."
        ),
    }
    payload["report_digest"] = digest(payload)
    path = root / "ADVERSARIAL_MUTATION_REPORT.json"
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

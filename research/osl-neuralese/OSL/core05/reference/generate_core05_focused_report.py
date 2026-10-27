#!/usr/bin/env python3
"""Run the fixed Core 0.5 semantic-independence focused gate."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from osl_model import digest


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "tests/test_core05_semantic_numeric.py",
    "tests/test_core05_semantic_contracts.py",
    "tests/test_core05_semantic_sessions.py",
    "tests/test_core05_semantic_meta.py",
    "tests/test_core05_semantic_intrinsics.py",
    "tests/test_core05_semantic_kernel.py",
    "tests/test_core05_language_hardening.py",
]
EXPECTED = {
    "numeric": 16,
    "contracts": 16,
    "sessions": 11,
    "metadata": 6,
    "intrinsics": 3,
    "integration": 4,
    "language_hardening": 19,
}


def main() -> int:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(ROOT / "reference"), env.get("PYTHONPATH", "")) if item
    )
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *FILES]
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    output = (proc.stdout + proc.stderr).strip()
    match = re.search(r"(\d+) passed", output)
    passed = int(match.group(1)) if match else 0
    expected_count = sum(EXPECTED.values())
    payload = {
        "schema": "osl.core05.focused-test-suite.v1",
        "language_version": "OSL-Core 0.5",
        "files": FILES,
        "category_case_counts": EXPECTED,
        "case_count": expected_count,
        "passed_count": passed,
        "failed_count": 0 if proc.returncode == 0 else max(1, expected_count - passed),
        "pytest_exit_code": proc.returncode,
        "all_checks_pass": proc.returncode == 0 and passed == expected_count,
        "claim_boundary": (
            "The fixed gate combines positive reconstruction, fail-closed malformed "
            "input, fully rehashed semantic mutation, rollback, and language-hardening "
            "tests. It is not exhaustive adversarial testing."
        ),
    }
    payload["report_digest"] = digest(payload)
    (ROOT / "CORE05_FOCUSED_REPORT.json").write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "case_count": expected_count,
        "passed_count": passed,
        "all_checks_pass": payload["all_checks_pass"],
    }, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

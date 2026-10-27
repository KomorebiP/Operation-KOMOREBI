#!/usr/bin/env python3
"""Run deterministic OSL-Core 0.5 tests and emit a compact report."""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from osl_model import digest


EXCLUDED_LEGACY_WRITERS = {
    "build_core04_archive.py",
    "build_core04_manifest.py",
    "generate_core04_adversarial_report.py",
    "generate_core04_bridge_report.py",
    "generate_core04_evidence.py",
    "verify_core04_package.py",
}


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
        "tests",
    ]
    proc = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
    output = (proc.stdout + proc.stderr).strip()
    match = re.search(r"(\d+) passed", output)
    passed = int(match.group(1)) if match else 0
    outcome_counts = {
        "pytest_failed": int((re.search(r"(\d+) failed", output) or [0, 0])[1]),
        "pytest_skipped": int((re.search(r"(\d+) skipped", output) or [0, 0])[1]),
        "pytest_xfailed": int((re.search(r"(\d+) xfailed", output) or [0, 0])[1]),
        "pytest_xpassed": int((re.search(r"(\d+) xpassed", output) or [0, 0])[1]),
        "pytest_deselected": int((re.search(r"(\d+) deselected", output) or [0, 0])[1]),
        "pytest_errors": int((re.search(r"(\d+) errors?", output) or [0, 0])[1]),
    }

    source_files = sorted(
        path
        for path in (root / "reference").glob("*.py")
        if path.name not in EXCLUDED_LEGACY_WRITERS
    ) + sorted((root / "tests").glob("*.py"))
    syntax_failures: list[str] = []
    for path in source_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            syntax_failures.append(f"{path.relative_to(root).as_posix()}:{exc.lineno}")

    payload = {
        "schema": "osl.core.test-report.v2",
        "language_version": "OSL-Core 0.5",
        "pytest_command": command[1:],
        "pytest_exit_code": proc.returncode,
        "pytest_passed": passed,
        **outcome_counts,
        # Do not persist pytest's wall-clock duration; the certificate must be
        # byte-reproducible across otherwise identical runs.
        "pytest_output_tail": f"{passed} passed" if match else (output.splitlines()[-1] if output else ""),
        "python_source_count": len(source_files),
        "syntax_failure_count": len(syntax_failures),
        "syntax_failures": syntax_failures,
        "all_checks_pass": bool(
            proc.returncode == 0
            and passed == 168
            and not any(outcome_counts.values())
            and not syntax_failures
        ),
    }
    payload["report_digest"] = digest(payload)
    (root / "TEST_REPORT.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

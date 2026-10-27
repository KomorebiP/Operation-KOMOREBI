#!/usr/bin/env python3
"""Run deterministic OSL-Core 0.3 tests and emit a compact report."""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from osl_model import digest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(root / "reference")
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

    source_files = sorted((root / "reference").glob("*.py")) + sorted((root / "tests").glob("*.py"))
    syntax_failures: list[str] = []
    for path in source_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            syntax_failures.append(f"{path.relative_to(root).as_posix()}:{exc.lineno}")

    payload = {
        "schema": "osl.core.test-report.v1",
        "language_version": "OSL-Core 0.3",
        "pytest_command": command[1:],
        "pytest_exit_code": proc.returncode,
        "pytest_passed": passed,
        # Do not persist pytest's wall-clock duration; the certificate must be
        # byte-reproducible across otherwise identical runs.
        "pytest_output_tail": f"{passed} passed" if match else (output.splitlines()[-1] if output else ""),
        "python_source_count": len(source_files),
        "syntax_failure_count": len(syntax_failures),
        "syntax_failures": syntax_failures,
        "all_checks_pass": proc.returncode == 0 and passed == 61 and not syntax_failures,
    }
    payload["report_digest"] = digest(payload)
    (root / "TEST_REPORT.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

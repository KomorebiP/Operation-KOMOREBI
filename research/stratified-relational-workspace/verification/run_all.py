#!/usr/bin/env python3
"""Run every deterministic mathematical regression check."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SCRIPTS = [
    "core_geometry.py",
    "case_studies.py",
    "decomposition_robustness.py",
    "specification_identifiability.py",
]


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    completed: list[dict[str, object]] = []
    for script in SCRIPTS:
        proc = subprocess.run(
            [sys.executable, str(HERE / script)],
            cwd=HERE,
            text=True,
            capture_output=True,
        )
        completed.append(
            {
                "script": script,
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            }
        )
        if proc.returncode != 0:
            (RESULTS / "summary.json").write_text(
                json.dumps({"all_checks_passed": False, "runs": completed}, indent=2) + "\n",
                encoding="utf-8",
            )
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            raise SystemExit(proc.returncode)

    summary = {"all_checks_passed": True, "runs": completed}
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"all_checks_passed": True, "scripts": SCRIPTS}, indent=2))


if __name__ == "__main__":
    main()

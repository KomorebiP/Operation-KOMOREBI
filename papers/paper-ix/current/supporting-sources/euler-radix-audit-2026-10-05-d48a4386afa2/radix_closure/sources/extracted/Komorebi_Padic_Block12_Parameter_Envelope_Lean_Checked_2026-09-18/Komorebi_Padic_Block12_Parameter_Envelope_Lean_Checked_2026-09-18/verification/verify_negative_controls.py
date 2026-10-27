#!/usr/bin/env python3
"""Run Block 09 Lean negative controls with explicit timeouts."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cases = [
        ("false_theorem", root / "verification" / "RejectFalse.lean", root / "logs" / "reject_false_block09.log"),
        ("sorry_placeholder", root / "verification" / "RejectSorry.lean", root / "logs" / "reject_sorry_block09.log"),
    ]
    records: list[dict[str, object]] = []
    passed = True
    env = dict(os.environ)
    env["TERM"] = "dumb"
    for name, source, log in cases:
        try:
            result = subprocess.run(
                ["lake", "env", "lean", "-DwarningAsError=true", str(source)],
                cwd=root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=120,
                check=False,
            )
            log.write_text(result.stdout, encoding="utf-8")
            ok = result.returncode != 0
            records.append({"name": name, "source": str(source.relative_to(root)), "exit_code": result.returncode, "timed_out": False, "passed": ok})
            passed = passed and ok
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or ""
            if isinstance(output, bytes):
                output = output.decode(errors="replace")
            log.write_text(output + "\nTIMEOUT\n", encoding="utf-8")
            records.append({"name": name, "source": str(source.relative_to(root)), "exit_code": None, "timed_out": True, "passed": False})
            passed = False
    report = {"schema": "komorebi-padic-block09-negative-controls-v1", "status": "PASS" if passed else "FAIL", "records": records}
    (root / "results" / "kernel_controls_block09.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

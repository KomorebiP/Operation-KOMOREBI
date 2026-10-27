#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    subprocess.run([sys.executable, "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT, check=True)
    smoke = ROOT / "results" / "smoke"
    required = [
        smoke / "PREREGISTRATION.json",
        smoke / "AGGREGATE_RESULTS.json",
        smoke / "GATE_RESULTS.json",
        smoke / "RUN_COMPLETE.json",
        smoke / "REPORT.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing smoke artifacts: {missing}")
    completion = json.loads((smoke / "RUN_COMPLETE.json").read_text(encoding="utf-8"))
    if completion.get("profile") != "smoke":
        raise SystemExit("Smoke completion profile mismatch")
    sums = ROOT / "SHA256SUMS.txt"
    if sums.exists():
        for line in sums.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            expected, relative = line.split("  ", 1)
            path = ROOT / relative
            observed = hashlib.sha256(path.read_bytes()).hexdigest()
            if observed != expected:
                raise SystemExit(f"Checksum mismatch: {relative}")
    print("PACKAGE_VERIFY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

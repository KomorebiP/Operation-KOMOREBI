#!/usr/bin/env python3
"""Re-run the Block 37 proof gates in the pinned Lean project."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification" / "block37" / "local_run"
OUT.mkdir(parents=True, exist_ok=True)

CHECKS = [
    ("full_build", ["lake", "-Kjobs=4", "--wfail", "build", "KomorebiPhysics"], False),
    ("source_warning_as_error", ["lake", "env", "lean", "-DwarningAsError=true", "KomorebiPhysics/Relativistic3DOctreeEuclideanCoding.lean"], False),
    ("api", ["lake", "env", "lean", "-DwarningAsError=true", "verification/block37/CheckBlock37API.lean"], False),
    ("axioms", ["lake", "env", "lean", "verification/block37/AuditBlock37.lean"], False),
    ("negative_mass", ["lake", "env", "lean", "-DwarningAsError=true", "negative_controls/block37/WrongBitVectorMass.lean"], True),
    ("negative_uniqueness", ["lake", "env", "lean", "-DwarningAsError=true", "negative_controls/block37/WrongBinaryUniqueness.lean"], True),
    ("negative_octant", ["lake", "env", "lean", "-DwarningAsError=true", "negative_controls/block37/WrongOctantBit.lean"], True),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    records = []
    ok = True
    for label, argv, expected_failure in CHECKS:
        log = OUT / f"{label}.log"
        started = time.time()
        proc = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log.write_bytes(proc.stdout)
        passed = (proc.returncode != 0) if expected_failure else (proc.returncode == 0)
        ok &= passed
        records.append({
            "label": label,
            "argv": argv,
            "returncode": proc.returncode,
            "expected_failure": expected_failure,
            "passed": passed,
            "elapsed_seconds": time.time() - started,
            "log": str(log.relative_to(ROOT)),
            "log_sha256": sha256(log),
        })
        print(f"{label}: {'PASS' if passed else 'FAIL'} (rc={proc.returncode})", flush=True)
        if not passed:
            break
    report = {
        "schema": "komorebi.physics.block37.local-verifier.v1",
        "status": "PASS" if ok else "FAIL",
        "checks": records,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

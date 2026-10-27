#!/usr/bin/env python3
"""Run the Block 38 modular cumulative proof gates."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification" / "block38" / "local_run"
OUT.mkdir(parents=True, exist_ok=True)

CHECKS = [
    ("module_build", ["lake", "build", "KomorebiPhysics.Relativistic3DBinaryLebesgue"], False),
    ("source_warning_as_error", ["lake", "env", "lean", "-DwarningAsError=true",
        "KomorebiPhysics/Relativistic3DBinaryLebesgue.lean"], False),
    ("api", ["lake", "env", "lean", "-DwarningAsError=true",
        "verification/block38/CheckBlock38API.lean"], False),
    ("axioms", ["lake", "env", "lean", "verification/block38/AuditBlock38.lean"], False),
    ("negative_half_cdf", ["lake", "env", "lean",
        "negative_controls/block38/FalseHalfCDF.lean"], True),
    ("negative_three_bit_mass", ["lake", "env", "lean",
        "negative_controls/block38/FalseThreeBitMass.lean"], True),
    ("negative_cube_mass", ["lake", "env", "lean",
        "negative_controls/block38/FalseCubeMass.lean"], True),
]

FORBIDDEN = {
    "sorry": re.compile(r"(?m)^\s*sorry\b|\bsorryAx\b"),
    "admit": re.compile(r"(?m)^\s*admit\b"),
    "custom_axiom": re.compile(r"(?m)^\s*axiom\b"),
    "native_decide": re.compile(r"\bnative_decide\b"),
    "unsafe": re.compile(r"(?m)^\s*unsafe\b"),
}


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
        proc = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
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

    source = ROOT / "KomorebiPhysics" / "Relativistic3DBinaryLebesgue.lean"
    text = source.read_text()
    trust_hits = {name: len(list(pattern.finditer(text))) for name, pattern in FORBIDDEN.items()}
    trust_pass = all(v == 0 for v in trust_hits.values())
    ok &= trust_pass

    parent_file = ROOT / "verification" / "block38" / "parent_preservation.json"
    parent = json.loads(parent_file.read_text()) if parent_file.exists() else {"all_identical": False}
    ok &= bool(parent.get("all_identical"))

    report = {
        "schema": "komorebi.physics.block38.local-verifier.v1",
        "status": "PASS" if ok else "FAIL",
        "verification_mode": "modular cumulative verification against frozen checked v0.37 parent",
        "checks": records,
        "source_trust_scan": {"passed": trust_pass, "hits": trust_hits},
        "parent_preservation": parent,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

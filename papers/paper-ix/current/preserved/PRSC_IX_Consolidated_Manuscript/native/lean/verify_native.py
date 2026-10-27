#!/usr/bin/env python3
"""Replay the standalone affine obstruction theorem with fresh local outputs.

Usage: python verify_native.py --kit /path/to/portable/kit --output /new/directory
The portable kit supplies Lean and Mathlib. No precompiled project artifact is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_MAIN = {
    "reduction", "digitMap", "Obstruction", "obstruction", "obstruction_finite",
    "obstruction_zero_iff_correction", "obstruction_representative_independent",
    "reduction_zero_iff", "affine_residual_transport",
    "affine_lift_iff_obstruction_zero", "residual_exists", "same_residue_iff",
    "finite_affine_obstruction",
}
EXPECTED_CONTROLS = {
    "identity_unobstructed", "zero_map_residual_nonzero",
    "singular_lower_solution", "singular_no_lift",
}

NEGATIVE_SOURCES = {
    "NegativeUnconditionalLift.lean": '''import FiniteAffineObstruction
open Komorebi.NativeAffine
example : obstruction 2 (0 : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ)) (fun _ => 1) = 0 := by
  rw [obstruction_zero_iff_correction]
  exact ⟨0, rfl⟩
''',
    "NegativePrecisionUpgrade.lean": '''import FiniteAffineObstruction
example : (4 : ℤ) ∣ 2 := by
  exact dvd_refl 2
''',
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def axiom_audit(log: str, expected: set[str]) -> dict:
    records = {}
    pattern = r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]"
    for name, content in re.findall(pattern, log, flags=re.S):
        records[name] = [a.strip() for a in content.split(",") if a.strip()]
    for name in re.findall(r"'([^']+)' does not depend on any axioms", log):
        records[name] = []
    actual = {name.rsplit(".", 1)[-1] for name in records}
    unexpected = sorted({a for axioms in records.values() for a in axioms} - ALLOWED_AXIOMS)
    return {"pass": actual == expected and not unexpected,
            "expected_count": len(expected), "actual_count": len(records),
            "missing": sorted(expected - actual), "unexpected_axioms": unexpected,
            "records": records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    kit = args.kit.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error("--output must be a new directory to exclude stale artifacts")
    output.mkdir(parents=True)
    sources = output / "sources"
    compiled = output / "compiled"
    sources.mkdir()
    compiled.mkdir()
    rows = []
    inputs = ["FiniteAffineObstruction.lean", "AffineObstructionControls.lean"]
    for name in inputs:
        shutil.copyfile(ROOT / name, sources / name)
    for name, source in NEGATIVE_SOURCES.items():
        (sources / name).write_text(source, encoding="utf-8")

    def run(name: str, negative: bool, expected: set[str] | None = None) -> dict:
        proof = sources / name
        command = [sys.executable, str(ROOT / "check_low_memory.py"), "--kit", str(kit),
                   "--threads", "1", "--timeout", "240", "--import-dir", str(compiled)]
        if not negative:
            command += ["--output", str(compiled / (proof.stem + ".olean"))]
        command.append(str(proof))
        started = time.monotonic()
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding="utf-8", errors="replace", timeout=400)
        log_path = output / (proof.stem + ".log")
        log_path.write_text(result.stdout, encoding="utf-8")
        if negative:
            # Reject missing imports, startup failures, and timeouts as false successes.
            good = (result.returncode == 1 and "error:" in result.stdout
                    and "type mismatch" in result.stdout.lower()
                    and "does not exist" not in result.stdout)
            audit = None
        else:
            audit = axiom_audit(result.stdout, expected or set())
            good = result.returncode == 0 and audit["pass"]
        row = {"source": name, "source_sha256": sha256(proof), "command": command,
               "exit_code": result.returncode, "expected_rejection": negative,
               "pass": good, "elapsed_seconds": round(time.monotonic() - started, 3),
               "log": log_path.name, "axiom_audit": audit}
        rows.append(row)
        print(f"{name}: {'PASS' if good else 'FAIL'}", flush=True)
        return row

    first = run(inputs[0], False, EXPECTED_MAIN)
    if first["pass"]:
        run(inputs[1], False, EXPECTED_CONTROLS)
        for name in NEGATIVE_SOURCES:
            run(name, True)
    complete = len(rows) == 4 and all(row["pass"] for row in rows)
    report = {
        "schema": "komorebi-native-affine-replay-v1", "pass": complete,
        "scope": "Finite affine integer-linear systems, positive modulus p, L >= 0; not arbitrary nonlinear native towers",
        "kit": str(kit), "threads_per_compile": 1, "warning_as_error": True,
        "allowed_axioms": sorted(ALLOWED_AXIOMS), "fresh_local_compilation": True,
        "results": rows,
        "verifier_sha256": sha256(Path(__file__)),
        "runner_sha256": sha256(ROOT / "check_low_memory.py"),
    }
    (output / "native_affine_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())

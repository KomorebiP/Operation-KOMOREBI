#!/usr/bin/env python3
"""Replay the scoped generator release with the external pinned Linux/WSL Lean kit.

Creates a NEW work directory, preserves the distributed baseline archive, performs
no downloads, and records accepted runs separately from expected mutant failures.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
MODULE = "KomorebiPhysics.Relativistic3DGeneratorBridge"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True,
                        help="New directory; existing directories are rejected")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--timeout", type=int, default=1200,
                        help="Maximum seconds for each gate")
    parser.add_argument("--prepare-only", action="store_true",
                        help="Verify inputs and attach pins; do NOT compile")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    manifest = json.loads((HERE / "GENERATOR_MANIFEST.json").read_text())
    baseline = (args.baseline or HERE.parent / manifest["baseline_archive"]).resolve()
    kit, work = args.kit.resolve(), args.work_dir.resolve()
    if work.exists():
        raise ValueError(f"Refusing to overwrite existing work directory: {work}")
    if digest(baseline) != manifest["baseline_sha256"]:
        raise ValueError("Baseline archive SHA-256 mismatch")
    for rel, expected in manifest["files"].items():
        if digest(HERE / rel) != expected:
            raise ValueError(f"Source SHA-256 mismatch: {rel}")
    env = os.environ.copy()
    env["PATH"] = str(kit / "toolchain/bin") + os.pathsep + env.get("PATH", "")
    for var in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME"):
        env.pop(var, None)
    version = subprocess.check_output([str(kit / "toolchain/bin/lean"), "--version"],
                                      env=env, text=True, timeout=60).strip()
    if manifest["lean_commit"] not in version:
        raise ValueError(f"Compiler pin mismatch: {version}")
    mathlib = kit / "workspace/.lake/packages/mathlib"
    rev = subprocess.check_output(["git", "-C", str(mathlib), "rev-parse", "HEAD"],
                                  text=True, timeout=60).strip()
    if rev != manifest["mathlib_commit"]:
        raise ValueError("Mathlib revision mismatch")
    work.mkdir(parents=True)
    with zipfile.ZipFile(baseline) as z:
        for item in z.infolist():
            candidate = (work / item.filename).resolve()
            if not candidate.is_relative_to(work):
                raise ValueError(f"Unsafe archive path: {item.filename}")
            if ((item.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError(f"Archive symlink not permitted: {item.filename}")
        z.extractall(work)
    project = work / baseline.stem
    if not (project / "lakefile.toml").is_file():
        raise FileNotFoundError("Expected baseline project root was not found")
    for rel in manifest["files"]:
        target = project / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / rel, target)
    evidence = work / "verification"
    evidence.mkdir()
    records: list[dict] = []
    summary = {"status": "RUNNING", "lean": version, "mathlib": rev,
               "source_manifest_sha256": digest(HERE / "GENERATOR_MANIFEST.json"),
               "baseline_sha256": digest(baseline), "gates": records}

    def save() -> None:
        (evidence / "RESULT.json").write_text(json.dumps(summary, indent=2) + "\n")

    def run(label: str, command: list[str], rejection: bool = False) -> None:
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        t = time.monotonic()
        log = evidence / (label + ".log")
        with log.open("w") as f:
            process = subprocess.Popen(command, cwd=project, env=env, stdout=f,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            timed_out = False
            try:
                rc = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                rc = process.returncode
        text = log.read_text(errors="replace")
        ok = (rc == 0) if not rejection else (
            rc != 0 and "error:" in text and "Unknown identifier" not in text
            and "object file" not in text)
        ok = ok and not timed_out
        records.append({"gate": label, "argv": command, "started_utc": started,
                        "seconds": round(time.monotonic() - t, 3), "returncode": rc,
                        "expected_rejection": rejection, "timeout": timed_out,
                        "pass": ok, "log": log.name, "log_sha256": digest(log)})
        save()
        print(f"{label}: {'PASS' if ok else 'FAIL'} (exit {rc})", flush=True)
        if not ok:
            raise RuntimeError(f"Gate failed: {label}; see {log}")

    try:
        run("attach_pinned_dependencies", ["bash", str(kit / "run.sh"), "attach", str(project)])
        if args.prepare_only:
            summary["status"] = "PREPARED_ONLY_NOT_COMPILED"
            save()
            return 0
        run("baseline_operator", ["lake", "build", "KomorebiPhysics.Relativistic3DWeightedDiracDomain"])
        run("generator_build", ["lake", "build", MODULE])
        lean = ["lake", "env", "lean", "-j1", "-DwarningAsError=true"]
        run("generator_strict", lean + ["KomorebiPhysics/Relativistic3DGeneratorBridge.lean"])
        for label, name in [("api", "CheckGeneratorBridge.lean"),
                            ("axioms", "AuditGeneratorBridge.lean"),
                            ("positive_smoke", "PositiveGeneratorSmoke.lean"),
                            ("baseline_api", "CheckBlock49API.lean"),
                            ("baseline_axioms", "AuditBlock49.lean")]:
            run(label, lean + [name])
        for mutant in ["WrongSign", "MissingDomain", "MissingImaginaryUnit", "Placeholder"]:
            run("negative_" + mutant, lean + [f"NegativeGenerator{mutant}.lean"], rejection=True)
        run("kernel_replay", ["lake", "env", "leanchecker", "-v", MODULE])
        fresh = evidence / "FreshGeneratorBridge.lean"
        shutil.copy2(project / "KomorebiPhysics/Relativistic3DGeneratorBridge.lean", fresh)
        run("fresh_path_strict", lean + [str(fresh)])
        axioms = []
        for m in re.finditer(r"'([^']+)' depends on axioms: \[(.*?)\]",
                             (evidence / "axioms.log").read_text(), re.S):
            deps = [s.strip() for s in m[2].split(",") if s.strip()]
            if not set(deps) <= ALLOWED:
                raise ValueError(f"Unexpected axiom dependencies for {m[1]}: {deps}")
            axioms.append({"name": m[1], "axioms": deps})
        expected = {d["name"] for d in manifest["declarations"]}
        if {d["name"] for d in axioms} != expected:
            raise ValueError("Axiom audit does not cover every named declaration")
        summary["axiom_audit"] = axioms
        summary["status"] = "PASS_SCOPED_GENERATOR"
        summary["trust_boundary"] = ("Exact target sources checked against pinned compiled dependencies. "
            "No compiler rebuild, no full library-from-source audit, no formal centered resolvent/rate theorem.")
        save()
        return 0
    except Exception as exc:
        summary["status"] = "FAIL"
        summary["failure"] = str(exc)
        save()
        raise

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Replay failed: {exc}", file=sys.stderr)
        raise SystemExit(1)

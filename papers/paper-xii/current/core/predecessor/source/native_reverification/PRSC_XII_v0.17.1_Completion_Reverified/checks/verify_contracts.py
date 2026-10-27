#!/usr/bin/env python3
"""Replay the exact manuscript contracts after a successful cumulative project build."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
NAMES = [f"PaperXII.ManuscriptContractReplay.{n}" for n in
         ("claim31_contract", "claim33_contract", "exact_closed_kernel")]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("portable_kit", type=Path)
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()
    report = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Three direct contract tests; not additions to the production theorem census"}
    output = ROOT / "CONTRACT_REPLAY.json"
    src = ROOT / "checks/ManuscriptContractReplay.lean"
    log = ROOT / "checks/ManuscriptContractReplay.log"
    try:
        full = json.loads((ROOT / "verification.json").read_text())
        if full["status"] != "PASS":
            raise ValueError("A complete successful cumulative replay is required first")
        kit = args.portable_kit.resolve()
        lean = kit / "toolchain/bin/lean"
        if sha(lean) != full["compiler_sha256"]:
            raise ValueError("Compiler hash differs from the cumulative replay")
        for path, digest in full["source_hashes_after"].items():
            if sha(ROOT / "lean" / path) != digest:
                raise ValueError(f"Production source changed: {path}")
        for item in full["modules"]:
            if sha(ROOT / item["olean_path"]) != item["olean_sha256"]:
                raise ValueError(f"Compiled dependency changed: {item['module']}")
        env = os.environ.copy()
        env["MALLOC_ARENA_MAX"] = "2"
        ws = kit / "workspace"
        env["LEAN_PATH"] = os.pathsep.join(str(p) for p in
            [ROOT / "build", ws / ".lake/build/lib/lean",
             *sorted((ws / ".lake/packages").glob("*/.lake/build/lib/lean"))])
        argv = [str(lean), "-j1", "-DwarningAsError=true", str(src)]
        report.update(argv=argv, cwd=str(ROOT / "lean"),
            compiler_sha256=sha(lean), source_sha256_before=sha(src),
            production_module_count=full["module_count"],
            lean_version=full["lean_version"], mathlib_commit=full["mathlib_commit"],
            timeout_seconds=args.timeout, threads=1, lean_path=env["LEAN_PATH"])
        output.write_text(json.dumps(report, indent=2) + "\n")
        start = time.monotonic()
        proc = subprocess.Popen(argv, cwd=ROOT / "lean", env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        timed_out = False
        try:
            text, _ = proc.communicate(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGKILL)
            text, _ = proc.communicate()
        log.write_text(text)
        report.update(exit_code=proc.returncode, timed_out=timed_out,
            seconds=round(time.monotonic()-start, 3), log=str(log.relative_to(ROOT)),
            log_sha256=sha(log), source_sha256_after=sha(src))
        if proc.returncode != 0 or timed_out:
            raise RuntimeError("Contract compilation did not pass; inspect the preserved log")
        audits = []
        for name in NAMES:
            match = re.search(re.escape("'" + name + "'") + r" depends on axioms:\s*\[([^\]]*)\]", text)
            if match:
                axioms = [a.strip() for a in match.group(1).split(",") if a.strip()]
            elif "'" + name + "' does not depend on any axioms" in text:
                axioms = []
            else:
                raise ValueError(f"Missing axiom output for {name}")
            if set(axioms) - ALLOWED:
                raise ValueError(f"Forbidden axiom in {name}: {axioms}")
            audits.append({"name": name, "axioms": axioms})
        if report["source_sha256_before"] != report["source_sha256_after"]:
            raise ValueError("Contract source changed during execution")
        report.update(status="PASS", audits=audits, finished_utc=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        report.update(status="FAIL", error=str(error), finished_utc=datetime.now(timezone.utc).isoformat())
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())

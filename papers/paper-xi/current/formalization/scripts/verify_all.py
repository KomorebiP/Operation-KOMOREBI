#!/usr/bin/env python3
"""Run source compilation, owning-module axiom audits and negative controls.

Dependencies must be prepared first with bootstrap.py. This command performs
no dependency downloads. Its child scripts preserve exact commands, source
hashes, output hashes and separate selected/terminal/interface counts.
The redundant same-kernel leanchecker pass is an explicit optional extra.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from replay import ROOT, stamp, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--out")
    parser.add_argument("--lean-bin")
    parser.add_argument("--synchronous", action="store_true",
                        help="Use synchronous Lean source elaboration to reduce memory pressure")
    parser.add_argument("--kernel-replay", action="store_true",
                        help="Also run the official same-kernel checker after the required gates")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
    relative = args.out or ("runs/" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    out = (ROOT / relative).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        parser.error("--out must be a new directory inside this project")
    out.mkdir(parents=True)
    relative = str(out.relative_to(ROOT))
    replay = relative + "/source_build"
    lean_args = ["--lean-bin", args.lean_bin] if args.lean_bin else []
    steps = [
        ("source_build", "replay.py", ["--out", replay, "--jobs", str(args.jobs)]
         + (["--synchronous"] if args.synchronous else [])),
        ("axioms_selected", "axiom_audit.py", ["--replay", replay, "--scope", "selected", "--out", relative + "/axioms_selected"]),
        ("axioms_terminal", "axiom_audit.py", ["--replay", replay, "--scope", "terminal", "--out", relative + "/axioms_terminal"]),
        ("axioms_interface", "axiom_audit.py", ["--replay", replay, "--scope", "new_interface", "--out", relative + "/axioms_interface"]),
        ("audit_controls", "audit_controls.py", ["--replay", replay, "--out", relative + "/audit_controls"]),
    ]
    if args.kernel_replay:
        steps.append(("kernel_replay", "kernel_replay.py", ["--replay", replay,
                      "--out", relative + "/kernel_replay", "--jobs", str(args.jobs)]))
    report = {"status": "RUNNING", "started_at": stamp(), "steps": []}
    write_json(out / "RUN_SUMMARY.json", report)
    start = time.monotonic()
    for name, script, arguments in steps:
        command = [sys.executable, str(ROOT / "scripts" / script), *arguments, *lean_args]
        print(f"Starting {name}", flush=True)
        t = time.monotonic()
        result = subprocess.run(command, cwd=ROOT)
        report["steps"].append({"name": name, "command": command,
                                "exit_code": result.returncode, "seconds": time.monotonic() - t})
        write_json(out / "RUN_SUMMARY.json", report)
        if result.returncode != 0:
            report.update(status="FAIL", failed_step=name, completed_at=stamp(),
                          seconds=time.monotonic() - start)
            write_json(out / "RUN_SUMMARY.json", report)
            print(json.dumps(report, indent=2))
            return result.returncode
    report.update(status="PASS", completed_at=stamp(), seconds=time.monotonic() - start)
    write_json(out / "RUN_SUMMARY.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

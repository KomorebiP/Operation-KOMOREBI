#!/usr/bin/env python3
"""Replay Block 48's Lean check without depending on the original cwd.

The optional runtime argument relocates the already installed pinned runtime;
this script never downloads or installs anything. The JSON result is execution
and axiom-audit evidence, not an assertion that external arithmetic is formal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    project = here.parent.parent
    runtime = (args.runtime or project / "runtime" /
               "Komorebi_Portable_Lean_4.34.0-rc2").resolve()
    source = here / "BealBlock48LocalAlgebra.lean"
    command = ["bash", str(runtime / "run.sh"), "lake", "-d",
               str(runtime / "workspace"), "env", "lean", "-j", "1",
               "-DwarningAsError=true", str(source)]
    print(json.dumps({"command": command}), flush=True)
    started = time.monotonic()
    run = subprocess.run(command, text=True, capture_output=True, timeout=100)
    print(run.stdout, end="", flush=True)
    print(run.stderr, end="", file=sys.stderr, flush=True)
    expected = re.findall(r"^theorem\s+(\w+)", source.read_text(), re.M)
    reports = re.findall(
        r"'KomorebiBeal\.Block48\.(\w+)' depends on axioms: \[([^]]*)\]",
        run.stdout, re.S)
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    axioms = {name: [a.strip() for a in names.split(",") if a.strip()]
              for name, names in reports}
    complete = len(reports) == len(expected) and set(axioms) == set(expected)
    permitted = all(set(names) <= allowed for names in axioms.values())
    passed = run.returncode == 0 and complete and permitted
    result = {
        "status": "passed" if passed else "failed",
        "command": command,
        "runtime_seconds": time.monotonic() - started,
        "compiler_exit_status": run.returncode,
        "source": str(source.relative_to(project)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "public_theorems": len(expected),
        "private_helpers": len(re.findall(r"^private theorem\s+", source.read_text(), re.M)),
        "axiom_audit_complete": complete,
        "only_standard_axioms": permitted,
        "axioms": axioms,
        "non_claim": "External curve, database, modular, and Fontaine-Laffaille arithmetic bridges are not formalized."
    }
    if args.result:
        args.result.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "public_theorems": len(expected),
                      "only_standard_axioms": permitted}), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

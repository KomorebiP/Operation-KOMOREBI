#!/usr/bin/env python3
"""Exercise two negative controls for the owning-module axiom audit.

The first control places public and private nonstandard axioms outside a safe
catalogue entry in the same module. The audit must detect both. The second requests an absent
catalogue name from a real selected module. Neither control modifies Paper XI.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from axiom_audit import generate
from replay import ROOT, locate_bin, runtime_environment, sha, stamp, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", default="evidence/replay")
    parser.add_argument("--out", default="evidence/axiom_controls")
    parser.add_argument("--lean-bin")
    args = parser.parse_args()
    replay = (ROOT / args.replay).resolve()
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        parser.error("--out must be a new directory inside this project")
    out.mkdir(parents=True)
    objects = out / "objects"
    objects.mkdir()
    bin_dir = locate_bin(args.lean_bin)
    env = runtime_environment(bin_dir, replay / "objects")
    env["LEAN_PATH"] = str(objects) + os.pathsep + env["LEAN_PATH"]
    source = out / "AxiomAuditControl.lean"
    source.write_text("namespace AxiomAuditControl\n"
                      "axiom uncataloguedSentinel : True\n"
                      "private axiom privateSentinel : True\n"
                      "theorem safeCatalogueEntry : True := True.intro\n"
                      "end AxiomAuditControl\n")
    command = [str(bin_dir / "lean"), "-j1", "-o", str(objects / "AxiomAuditControl.olean"), source.name]
    with (out / "CONTROL_BUILD.log").open("w") as f:
        subprocess.run(command, cwd=out, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
    controls = [
        ("uncatalogued_axiom", ["AxiomAuditControl"], ["AxiomAuditControl"],
         [{"name": "AxiomAuditControl.safeCatalogueEntry", "module": "AxiomAuditControl"}],
         "Nonstandard axioms found"),
        ("missing_catalogue_name", ["PaperXI.AtomicMultiset"], ["PaperXI.AtomicMultiset"],
         [{"name": "PaperXI.AtomicMultiset.DeliberatelyAbsentAuditName", "module": "PaperXI.AtomicMultiset"}],
         "Catalogue name is absent"),
    ]
    report = {"status": "RUNNING", "started_at": stamp(),
              "control_source_sha256": sha(source), "control_compile_command": command,
              "controls": [], "scope": "Audit harness only; no Paper XI source is edited."}
    for name, imports, owners, catalogue, expected in controls:
        audit = out / (name + ".lean")
        audit.write_text(generate(imports, owners, catalogue))
        command = [str(bin_dir / "lean"), "-j1", "-DwarningAsError=true", str(audit)]
        log = out / (name + ".log")
        t = time.monotonic()
        with log.open("w") as f:
            p = subprocess.run(command, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=180)
        text = log.read_text()
        passed = p.returncode != 0 and expected in text
        sentinel_checks = {}
        if name == "uncatalogued_axiom":
            events = [json.loads(line) for line in text.splitlines() if line.startswith('{"')]
            owned = [row for row in events if row.get("event") == "owned_constant"]
            public = [row for row in owned if row["name"] == "AxiomAuditControl.uncataloguedSentinel"]
            private = [row for row in owned if row["name"].startswith("_private.")
                       and row["name"].endswith(".AxiomAuditControl.privateSentinel")]
            safe = [row for row in owned if row["name"] == "AxiomAuditControl.safeCatalogueEntry"]
            sentinel_checks = {
                "public_uncatalogued_axiom_detected": len(public) == 1 and public[0]["name"] in public[0]["forbidden_axioms"],
                "private_uncatalogued_axiom_detected": len(private) == 1 and private[0]["name"] in private[0]["forbidden_axioms"],
                "catalogued_theorem_has_no_axioms": len(safe) == 1 and safe[0]["axioms"] == [],
                "observed_private_sentinel_names": [row["name"] for row in private],
            }
            passed = passed and all(sentinel_checks[key] for key in [
                "public_uncatalogued_axiom_detected", "private_uncatalogued_axiom_detected",
                "catalogued_theorem_has_no_axioms"])
        report["controls"].append({"name": name, "status": "PASS" if passed else "FAIL",
            "expected_outcome": "Lean audit exits nonzero with the specified rejection reason",
            "expected_error_text": expected, "exit_code": p.returncode,
            "command": command, "seconds": time.monotonic() - t,
            "sentinel_checks": sentinel_checks,
            "audit_source_sha256": sha(audit), "log_sha256": sha(log)})
    report["status"] = "PASS" if all(x["status"] == "PASS" for x in report["controls"]) else "FAIL"
    report["completed_at"] = stamp()
    write_json(out / "RESULT.json", report)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

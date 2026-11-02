#!/usr/bin/env python3
"""Replay SF-LEAN-B09 using a pinned, already populated Lean/Mathlib environment.

No installation or network access is performed. The work directory must be new
and outside the release. Native Windows and Linux toolchains are supported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
PREFIX = "Komorebi.SpecialFunctions.Coupled.Scales."


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--mathlib", type=Path, required=True)
    parser.add_argument("--packages", type=Path, help="Default: MATHLIB/.lake/packages")
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--git", default="git")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    kit, mathlib, work = args.toolchain.resolve(), args.mathlib.resolve(), args.work.resolve()
    packages = (args.packages or mathlib / ".lake/packages").resolve()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if work == ROOT or ROOT in work.parents:
        parser.error("--work must be outside the release")
    if work.exists():
        parser.error("--work must be a new directory, preserving earlier receipts")
    work.mkdir(parents=True)
    build = work / "build"
    build.mkdir()
    exe = ".exe" if os.name == "nt" else ""
    lean = kit / "bin" / ("lean" + exe)
    checker = kit / "bin" / ("leanchecker" + exe)
    env = dict(os.environ)
    for key in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME"):
        env.pop(key, None)
    env["PATH"] = str(kit / "bin") + os.pathsep + env.get("PATH", "")
    libs = [build, mathlib / ".lake/build/lib/lean"] + [
        p / ".lake/build/lib/lean" for p in sorted(packages.iterdir()) if p.is_dir()]
    env["LEAN_PATH"] = os.pathsep.join(map(str, libs))
    base = [str(lean), "-j1", "-DwarningAsError=true"]
    report = {
        "schema": 1, "block": "SF-LEAN-B09", "status": "running",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(), "python": sys.version,
        "scope": "Explicit lower logarithmic power comparison for all R>=2, positive canonical coefficients and uniform growth-ratio lower bounds, via seed/shift/descent induction. Upper bounds and liminf/limsup type identification remain open.",
        "kernel_scope": "Same-kernel replay of CoupledFormal, CoupledAnalytic, CoupledEntire, CoupledUniqueness, CoupledGermInverse, CoupledRescaling, CoupledCharacteristic, CoupledPositiveReal and CoupledLowerGrowth against cached imports; imported Mathlib is not freshly replayed.",
        "steps": [], "inputs": {},
    }
    receipt = work / "receipt.json"

    def save() -> None:
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    def run(name: str, argv: list[str], *, cwd: Path = build,
            expected: int = 0, diagnostic: str | None = None) -> str:
        started = time.monotonic()
        try:
            proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                                  encoding="utf-8", errors="replace", timeout=args.timeout)
            output = proc.stdout + proc.stderr
            rc, timed_out = proc.returncode, False
        except subprocess.TimeoutExpired as exc:
            output = str(exc)
            rc, timed_out = None, True
        log = work / (name + ".log")
        log.write_text(output, encoding="utf-8")
        passed = not timed_out and rc == expected and (diagnostic is None or diagnostic in output)
        report["steps"].append({
            "name": name, "argv": argv, "cwd": str(cwd), "exit_code": rc,
            "expected_exit_code": expected, "required_diagnostic": diagnostic,
            "timed_out": timed_out, "seconds": round(time.monotonic() - started, 3),
            "passed": passed, "log": log.name, "log_sha256": sha(log),
        })
        save()
        print(("PASS " if passed else "FAIL ") + name, flush=True)
        if not passed:
            raise RuntimeError(name + ": " + output[-4000:])
        return output

    def audit(output: str, wanted: list[str], label: str) -> None:
        names = re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)", output)
        groups = re.findall(r"depends on axioms:\s*\[([^]]*)\]", output, flags=re.S)
        axioms = {x.strip() for group in groups for x in group.split(",") if x.strip()}
        if set(names) != set(wanted) or len(names) != len(wanted) or axioms - ALLOWED:
            raise RuntimeError("Axiom audit mismatch: " + label)
        report[label] = {"names": names, "count": len(names), "axioms": sorted(axioms)}
        save()

    try:
        production = ROOT / "lean/CoupledLowerGrowth.lean"
        maps = {}
        for block, source in (("Block01", "CoupledFormal"), ("Block02", "CoupledAnalytic"), ("Block03", "CoupledEntire"), ("Block04", "CoupledUniqueness"), ("Block05", "CoupledGermInverse"), ("Block06", "CoupledRescaling"), ("Block07", "CoupledCharacteristic"), ("Block08", "CoupledPositiveReal"), ("Block09", "CoupledLowerGrowth")):
            mapping = json.loads((ROOT / "formalization" / block / "declarations.json").read_text())
            path = ROOT / "lean" / (source + ".lean")
            if sha(path) != mapping["sha256"]:
                raise RuntimeError("Source/map digest mismatch: " + source)
            names = [r["name"] for r in mapping["declarations"]]
            if len(names) != len(set(names)) or len(names) != mapping["count"]:
                raise RuntimeError("Duplicate or incorrect declaration count: " + source)
            if block == "Block09":
                parsed = [PREFIX + n for n in re.findall(r"^theorem\s+(\w+)", path.read_text(encoding="utf-8"), re.M)]
                if parsed != names:
                    raise RuntimeError("New declaration map is not exactly the source theorem list")
            maps[source] = names
            for name in (source + ".lean", source + "Audit.lean"):
                shutil.copyfile(ROOT / "lean" / name, build / name)
        scrub = re.sub(r"/\-.*?\-/|--[^\n]*", "", production.read_text(encoding="utf-8"), flags=re.S)
        if re.search(r"\b(sorry|admit|axiom|native_decide|unsafe)\b", scrub):
            raise RuntimeError("Forbidden construct in production source")
        controls = json.loads((ROOT / "lean/lower_growth_controls/manifest.json").read_text())
        inputs = [ROOT / "tools/verify_coupled_lower_growth.py", ROOT / "lean/dependency_pins.json",
                  ROOT / "formalization/Block01/declarations.json", ROOT / "formalization/Block02/declarations.json",
                  ROOT / "formalization/Block03/declarations.json", ROOT / "formalization/Block04/declarations.json", ROOT / "formalization/Block05/declarations.json", ROOT / "formalization/Block06/declarations.json", ROOT / "formalization/Block07/declarations.json", ROOT / "formalization/Block08/declarations.json", ROOT / "formalization/Block09/declarations.json",
                  ROOT / "lean/lower_growth_controls/manifest.json"]
        inputs += [ROOT / "lean" / (n + suffix) for n in maps for suffix in (".lean", "Audit.lean")]
        inputs += [ROOT / "lean/lower_growth_controls" / row["file"] for row in controls]
        report["inputs"] = {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}
        report["toolchain"] = {"lean_sha256": sha(lean), "leanchecker_sha256": sha(checker)}
        version = run("version", [str(lean), "--version"], diagnostic="4.34.0-rc2")
        report["toolchain"]["version"] = version.strip()
        pins = json.loads((ROOT / "lean/dependency_pins.json").read_text())["packages"]
        for pin in pins:
            path = mathlib if pin["name"] == "mathlib" else packages / pin["name"]
            out = run("pin-" + pin["name"], [args.git, "rev-parse", "HEAD"], cwd=path)
            if out.strip() != pin["rev"]:
                raise RuntimeError("Wrong dependency revision: " + pin["name"])
        for source, names in maps.items():
            run("compile-" + source, base + ["-o", source + ".olean", source + ".lean"])
            output = run("audit-" + source, base + [source + "Audit.lean"])
            audit(output, names, source + "_audit")
            report.setdefault("objects", {})[source + ".olean"] = sha(build / (source + ".olean"))
        for source in maps:
            run("kernel-" + source, [str(checker), "--verbose", source], diagnostic="replaying " + source)
        for row in controls:
            name = "control-" + Path(row["file"]).stem
            shutil.copyfile(ROOT / "lean/lower_growth_controls" / row["file"], build / (name + ".lean"))
            run(name, base + [name + ".lean"], expected=row.get("expected_exit_code", 1), diagnostic=row["diagnostic"])
        # Evidence is only valid for the exact inputs present at the end of replay.
        if any(sha(ROOT / name) != digest for name, digest in report["inputs"].items()):
            raise RuntimeError("An input changed during verification")
        report["status"] = "passed"
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        print(str(exc), file=sys.stderr)
    finally:
        save()
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

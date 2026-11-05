#!/usr/bin/env python3
"""Replay SF-LEAN-B19 using a pinned, already populated Lean/Mathlib environment.

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
    parser.add_argument("--dependency-build", type=Path,
                        help="Reuse Block18 and earlier objects only with a matching successful --dependency-receipt")
    parser.add_argument("--dependency-receipt", type=Path)
    args = parser.parse_args()
    kit, mathlib, work = args.toolchain.resolve(), args.mathlib.resolve(), args.work.resolve()
    packages = (args.packages or mathlib / ".lake/packages").resolve()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if (args.dependency_build is None) != (args.dependency_receipt is None):
        parser.error("--dependency-build and --dependency-receipt must be supplied together")
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
        "schema": 1, "block": "SF-LEAN-B19", "status": "running",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(), "python": sys.version,
        "scope": "Source-bound imperative operational model, universal array/ladder/fold/dictionary refinement, totality/determinism and parameterized raw conversion/error front end. Source binder/template and Python primitives remain an explicit trusted boundary; no verified-compiler or CPython implementation claim.",
        "kernel_scope": ("Fresh compile, exact axiom audits and same-kernel replay of CoupledPythonSource and CoupledPythonRefinement. Eighteen coupled dependencies are inherited after recursive receipt, source, object and compiler hash checks. Mathlib is cached."
                         if args.dependency_build else
                         "Fresh compile, axiom audit and same-kernel replay of all twenty coupled modules against cached Mathlib imports; Mathlib is not freshly replayed."),
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
        production = ROOT / "lean/CoupledPythonRefinement.lean"
        maps = {}
        for block, source in (("Block01", "CoupledFormal"), ("Block02", "CoupledAnalytic"), ("Block03", "CoupledEntire"), ("Block04", "CoupledUniqueness"), ("Block05", "CoupledGermInverse"), ("Block06", "CoupledRescaling"), ("Block07", "CoupledCharacteristic"), ("Block08", "CoupledPositiveReal"), ("Block09", "CoupledLowerGrowth"), ("Block10", "CoupledUpperGrowth"), ("Block11", "CoupledGrowthTypes"), ("Block12", "CoupledTypeProportions"), ("Block13", "CoupledScalarReduction"), ("Block14", "CoupledOperator"), ("Block15", "CoupledEvaluation"), ("Block16", "CoupledNormalization"), ("Block17", "CoupledGuardedMajorant"), ("Block18", "CoupledEvaluationResult"), ("Block19Source", "CoupledPythonSource"), ("Block19", "CoupledPythonRefinement")):
            mapping_path = (ROOT / "formalization/Block19/source_declarations.json" if block == "Block19Source" else ROOT / "formalization" / block / "declarations.json")
            mapping = json.loads(mapping_path.read_text())
            path = ROOT / "lean" / (source + ".lean")
            if sha(path) != mapping["sha256"]:
                raise RuntimeError("Source/map digest mismatch: " + source)
            names = [r["name"] for r in mapping["declarations"]]
            if len(names) != len(set(names)) or len(names) != mapping["count"]:
                raise RuntimeError("Duplicate or incorrect declaration count: " + source)
            if block.startswith("Block19"):
                parsed = [PREFIX + "Python." + n for n in re.findall(r"^theorem\s+(\w+)", path.read_text(encoding="utf-8"), re.M)]
                if parsed != names:
                    raise RuntimeError("New declaration map is not exactly the source theorem list")
            maps[source] = names
            for name in (source + ".lean", source + "Audit.lean"):
                shutil.copyfile(ROOT / "lean" / name, build / name)
        for checked_source in (production, ROOT / "lean/CoupledPythonSource.lean"):
            scrub = re.sub(r"/\-.*?\-/|--[^\n]*", "", checked_source.read_text(encoding="utf-8"), flags=re.S)
            if re.search(r"\b(sorry|admit|axiom|native_decide|unsafe)\b", scrub):
                raise RuntimeError("Forbidden construct in production source: " + checked_source.name)
        controls = json.loads((ROOT / "lean/python_refinement_controls/manifest.json").read_text())
        inputs = [ROOT / "tools/verify_coupled_python_refinement.py", ROOT / "lean/dependency_pins.json",
                  ROOT / "formalization/Block01/declarations.json", ROOT / "formalization/Block02/declarations.json",
                  ROOT / "formalization/Block03/declarations.json", ROOT / "formalization/Block04/declarations.json", ROOT / "formalization/Block05/declarations.json", ROOT / "formalization/Block06/declarations.json", ROOT / "formalization/Block07/declarations.json", ROOT / "formalization/Block08/declarations.json", ROOT / "formalization/Block09/declarations.json", ROOT / "formalization/Block10/declarations.json", ROOT / "formalization/Block11/declarations.json", ROOT / "formalization/Block12/declarations.json", ROOT / "formalization/Block13/declarations.json", ROOT / "formalization/Block14/declarations.json", ROOT / "formalization/Block15/declarations.json", ROOT / "formalization/Block16/declarations.json", ROOT / "formalization/Block17/declarations.json", ROOT / "formalization/Block18/declarations.json", ROOT / "formalization/Block19/declarations.json", ROOT / "formalization/Block19/source_declarations.json",
                  ROOT / "lean/python_refinement_controls/manifest.json"]
        inputs += [ROOT / name for name in ("research/coupled_lab.py", "research/family_lab.py", "tools/bind_python_source.py", "tools/check_python_source_binding.py", "tools/python_refinement/source_patterns.json", "tools/python_refinement/CoupledPythonSource.template")]
        inputs += [ROOT / "lean" / (n + suffix) for n in maps for suffix in (".lean", "Audit.lean")]
        inputs += [ROOT / "lean/python_refinement_controls" / row["file"] for row in controls]
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
        inherited_objects = {}
        if args.dependency_build:
            prior_path = args.dependency_receipt.resolve()
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            receipt_chain = {}
            def collect_receipt(path):
                path = path.resolve()
                if str(path) in receipt_chain:
                    raise RuntimeError("Cyclic dependency receipt chain")
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("status") != "passed" or not data.get("steps") or not all(step.get("passed") is True for step in data["steps"]):
                    raise RuntimeError("Unsuccessful dependency receipt")
                if any(data["toolchain"][key] != report["toolchain"][key] for key in ("lean_sha256", "leanchecker_sha256")):
                    raise RuntimeError("Different compiler/checker in dependency chain")
                receipt_chain[str(path)] = sha(path)
                objects = {}
                inherited = data.get("inherited_dependencies")
                if inherited:
                    parent = Path(inherited["receipt"])
                    if sha(parent) != inherited["receipt_sha256"]:
                        raise RuntimeError("Dependency parent receipt hash changed")
                    objects.update(collect_receipt(parent))
                for name, digest in data.get("objects", {}).items():
                    if name in objects and objects[name] != digest:
                        raise RuntimeError("Inconsistent object revisions in dependency chain")
                    objects[name] = digest
                return objects
            if prior.get("block") != "SF-LEAN-B18":
                raise RuntimeError("A successful Block18 dependency receipt is required")
            prior_objects = collect_receipt(prior_path)
            for source in maps:
                if source in ("CoupledPythonSource", "CoupledPythonRefinement"):
                    continue
                for suffix in (".lean", "Audit.lean"):
                    key = "lean/" + source + suffix
                    if report["inputs"][key] != prior["inputs"][key]:
                        raise RuntimeError("Dependency source changed: " + key)
                obj = args.dependency_build.resolve() / (source + ".olean")
                digest = sha(obj)
                if digest != prior_objects[obj.name]:
                    raise RuntimeError("Dependency object changed: " + source)
                inherited_objects[str(obj)] = digest
                shutil.copyfile(obj, build / obj.name)
                if sha(build / obj.name) != digest:
                    raise RuntimeError("Dependency object copy changed: " + source)
            report["inherited_dependencies"] = {
                "receipt": str(prior_path), "receipt_sha256": sha(prior_path),
                "objects": inherited_objects, "receipt_chain": receipt_chain,
                "freshly_compiled_or_replayed": False,
            }
            report["inputs"]["@dependency-receipt"] = sha(prior_path)
            save()
        fresh_maps = {source: names for source, names in maps.items()
                      if not args.dependency_build or source in ("CoupledPythonSource", "CoupledPythonRefinement")}
        run("source-binding", [sys.executable, str(ROOT / "tools/bind_python_source.py"), "--output", str(work / "binding.json")])
        run("binding-mutation-controls", [sys.executable, str(ROOT / "tools/check_python_source_binding.py"), "--output", str(work / "binding-controls.json")])
        report["binding_sha256"] = sha(work / "binding.json")
        report["binding_controls_sha256"] = sha(work / "binding-controls.json")
        for source, names in fresh_maps.items():
            run("compile-" + source, base + ["-o", source + ".olean", source + ".lean"])
            output = run("audit-" + source, base + [source + "Audit.lean"])
            audit(output, names, source + "_audit")
            report.setdefault("objects", {})[source + ".olean"] = sha(build / (source + ".olean"))
        for source in fresh_maps:
            run("kernel-" + source, [str(checker), "--verbose", source], diagnostic="replaying " + source)
        for row in controls:
            name = "control-" + Path(row["file"]).stem
            shutil.copyfile(ROOT / "lean/python_refinement_controls" / row["file"], build / (name + ".lean"))
            run(name, base + [name + ".lean"], expected=row.get("expected_exit_code", 1), diagnostic=row["diagnostic"])
        # Evidence is only valid for the exact inputs present at the end of replay.
        if any(sha(ROOT / name) != digest for name, digest in report["inputs"].items()
               if not name.startswith("@")):
            raise RuntimeError("An input changed during verification")
        if args.dependency_build:
            if any(sha(Path(name)) != digest for name, digest in receipt_chain.items()):
                raise RuntimeError("Dependency receipt chain changed during verification")
            if sha(args.dependency_receipt) != report["inputs"]["@dependency-receipt"]:
                raise RuntimeError("Dependency receipt changed during verification")
            if any(sha(Path(name)) != digest or sha(build / Path(name).name) != digest
                   for name, digest in inherited_objects.items()):
                raise RuntimeError("An inherited object changed during verification")
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

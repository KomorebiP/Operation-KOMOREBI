#!/usr/bin/env python3
"""Fail-closed clean cumulative source replay of the unchanged 1.7.0 library.

Use --static-only --label NAME to inventory without a Lean claim, or
--runtime /path/to/portable-runtime --label NAME for compilation and controls.
Each run uses a new source snapshot and empty build directory. No network or
package installation occurs. Every source, script, log and receipt is retained.
External pinned package caches and the official Lean kernel remain trusted.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from common import ALLOWED_AXIOMS, ROOT_MODULE, graph, sha, write_json

HOME = Path(__file__).resolve().parents[1]
PROJECT = HOME / "project"
VERSION = "4.34.0-rc2"
COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"
CONTROLS = {"formal": {"positive": 1, "negative": 6, "policy": 1},
            "extension": {"positive": 1, "negative": 4, "policy": 1}}


def tree_hashes(root: Path) -> dict:
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runtime", type=Path)
    ap.add_argument("--label", required=True)
    ap.add_argument("--static-only", action="store_true")
    ap.add_argument("--path-adapter", type=Path,
                    help="Explicit portable-runtime executable-location adapter, if needed")
    ap.add_argument("--timeout", type=int, default=300,
                    help="Per compiler invocation timeout in seconds")
    ap.add_argument("--audit-timeout", type=int, default=1800)
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.label):
        ap.error("Use a simple letters/digits/underscore/hyphen label")
    if not args.static_only and args.runtime is None:
        ap.error("--runtime is required unless --static-only")
    if args.timeout <= 0 or args.audit_timeout <= 0:
        ap.error("Timeouts must be positive")
    runroot = HOME / "runs" / args.label
    if runroot.exists():
        ap.error("Refusing to overwrite an existing attempt; use a new label")
    runroot.mkdir(parents=True)
    logs = runroot / "logs"
    logs.mkdir()
    workspace = runroot / "source"
    build = runroot / "build"
    build.mkdir()
    rep = {"schema": "komorebi-space-combined-replay-v1", "label": args.label,
           "status": "RUNNING", "lean_executed": False,
           "scope": "All unchanged v1.7.0 core and regularization modules together",
           "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "compile_policy": {"threads": 1, "warningAsError": True, "autoImplicit": False},
           "clean_project_build": True, "commands": [], "dependencies": [],
           "trust_boundary": ["Official Lean compiler/kernel and standard permitted axioms.",
                              "Pinned external compiled package caches are reused, not rebuilt.",
                              "No machine-checked translation of prose or Python refinement."]}

    def save() -> None:
        write_json(runroot / "receipt.json", rep)

    child = None

    def interrupt(signum, frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
        raise KeyboardInterrupt(f"Received signal {signum}")

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, interrupt)

    def execute(label, argv, env, *, negative=False, marker=None):
        nonlocal child
        argv = list(map(str, argv))
        log = logs / (label + ".log")
        started = time.monotonic()
        timed_out = False
        with log.open("w") as stream:
            child = subprocess.Popen(argv, cwd=workspace, env=env,
                                     stdout=stream, stderr=subprocess.STDOUT,
                                     start_new_session=True)
            try:
                code = child.wait(timeout=args.audit_timeout if label == "axiom_export" else args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
                code = 124
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
        child = None
        output = log.read_text(errors="replace")
        lower = output.lower()
        passed = code == 0 and not timed_out
        if negative:
            forbidden_errors = ("unknown module", "unknown identifier", "unknown constant",
                                "object file", "failed to load", "no such file", "not found",
                                "cannot execute", "segmentation fault", "stack overflow")
            # A killed compiler, broken environment or missing symbol is not a rejection control.
            passed = (code > 0 and not timed_out and "error" in lower
                      and not any(s in lower for s in forbidden_errors)
                      and (marker is None or marker in output))
        record = {"label": label, "argv": argv, "exit_code": code,
                  "expected_rejection": negative, "required_marker": marker,
                  "timeout": timed_out, "passed": passed,
                  "seconds": round(time.monotonic() - started, 3),
                  "log": str(log.relative_to(runroot)), "log_sha256": sha(log)}
        rep["commands"].append(record)
        save()
        print(label, "PASS" if passed else "FAIL", code, flush=True)
        if not passed:
            raise RuntimeError(f"{label} failed; retained log {log}")
        return output

    try:
        save()
        inventory = json.loads((HOME / "inventory.json").read_text())
        before = tree_hashes(PROJECT)
        if before != inventory["project_file_sha256"]:
            raise ValueError("Project differs from assembled archive-bound inventory")
        if inventory["control_counts"] != CONTROLS:
            raise ValueError("Inventory has unexpected control counts")
        rep["inventory_sha256"] = sha(HOME / "inventory.json")
        rep["source_archive_sha256"] = inventory["source_archive_sha256"]
        rep["project_file_sha256"] = before
        helpers_before = tree_hashes(HOME / "scripts")
        rep["verifier_input_sha256"] = helpers_before
        shutil.copytree(PROJECT, workspace)
        shutil.copyfile(HOME / "scripts/ExportAudit.lean", workspace / "ExportAudit.lean")
        info = graph(workspace)
        for key in ("source_sha256", "compile_order", "production_modules", "compile_targets"):
            if info[key] != inventory[key]:
                raise ValueError(f"Snapshot graph differs from assembly: {key}")
        if (workspace / "wanted_modules.txt").read_text().splitlines() != info["compile_order"]:
            raise ValueError("Audit module list differs from complete source graph")
        rep.update({key: info[key] for key in ("compile_order", "compile_targets", "production_modules",
                                             "entrypoints", "explicit_theorem_lemma_count", "source_sha256")})
        for scope, counts in CONTROLS.items():
            for kind, count in counts.items():
                if len(list((workspace / "tests" / scope / kind).glob("*.lean"))) != count:
                    raise ValueError(f"Missing control: {scope}/{kind}")
        save()
        if args.static_only:
            rep["status"] = "STATIC_CHECKS_PASS_NOT_LEAN_VERIFIED"
            rep["reason"] = "Requested static mode. Compiler, axiom audit and rejection controls were not run."
        else:
            runtime = args.runtime.resolve()
            lean = runtime / "toolchain/bin/lean"
            packages = runtime / "workspace/.lake/packages"
            rep["runtime"] = str(runtime)
            if not lean.is_file():
                raise FileNotFoundError(f"Missing pinned Lean executable: {lean}")
            pins = json.loads((workspace / "pinned-dependencies.json").read_text())["packages"]
            named_cache_paths = {pin["name"]: packages / pin["name"] / ".lake/build/lib/lean"
                                 for pin in pins}
            if not named_cache_paths["mathlib"].is_dir():
                raise FileNotFoundError("Missing pinned mathlib cache")
            expected_cache_paths = [p for p in named_cache_paths.values() if p.is_dir()]
            rep["dependency_cache_directories"] = {name: {"path": str(path), "exists": path.is_dir()}
                                                    for name, path in named_cache_paths.items()}
            env = dict(os.environ)
            for key in ("LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME"):
                env.pop(key, None)
            # Discard inherited Lean search paths and never include historical project objects.
            env["LEAN_PATH"] = os.pathsep.join(map(str, [build] + expected_cache_paths))
            env["PATH"] = str(runtime / "toolchain/bin") + os.pathsep + env.get("PATH", "")
            env["KS_COMBINED_AUDIT"] = str(runroot / "axioms.json")
            if args.path_adapter:
                adapter = args.path_adapter.resolve()
                if not adapter.is_file() or any(c.isspace() for c in str(adapter)):
                    raise ValueError("Path adapter must be an existing file at a whitespace-free path")
                env["LD_PRELOAD"] = str(adapter) + ((":" + env["LD_PRELOAD"]) if env.get("LD_PRELOAD") else "")
                rep["executable_path_adapter"] = {"path": str(adapter), "sha256": sha(adapter)}
            rep["environment"] = {"LEAN_PATH": env["LEAN_PATH"]}
            if env.get("LD_PRELOAD"):
                rep["environment"]["LD_PRELOAD"] = env["LD_PRELOAD"]
            rep["lean_binary_sha256"] = sha(lean)
            rep["lean_executed"] = True
            version = execute("lean_version", [lean, "--version"], env).strip()
            if VERSION not in version or COMMIT not in version:
                raise ValueError(f"Unexpected Lean version/commit: {version}")
            rep["lean_version"] = version
            for pin in pins:
                actual = execute("pin_" + pin["name"],
                                 ["git", "-C", packages / pin["name"], "rev-parse", "HEAD"], env).strip()
                if actual != pin["rev"]:
                    raise ValueError(f"Dependency mismatch: {pin['name']}")
                execute("clean_" + pin["name"],
                        ["git", "-C", packages / pin["name"], "diff", "--exit-code", "HEAD", "--"], env)
                rep["dependencies"].append({"name": pin["name"], "expected": pin["rev"], "actual": actual})
            flags = [lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
            for mod in info["compile_order"]:
                rel = Path(mod.replace(".", "/"))
                out = build / rel.with_suffix(".olean")
                out.parent.mkdir(parents=True, exist_ok=True)
                execute("compile_" + mod, flags + ["-o", out, workspace / rel.with_suffix(".lean")], env)
            rep["object_sha256"] = tree_hashes(build)
            execute("axiom_export", flags + [workspace / "ExportAudit.lean"], env)
            audit = json.loads((runroot / "axioms.json").read_text())
            rows = audit["declarations"]
            if not rows or audit["unexpected"] or audit["count"] != len(rows):
                raise ValueError("Empty, inconsistent, or rejected axiom export")
            if len({row["name"] for row in rows}) != len(rows):
                raise ValueError("Duplicate declaration names in export")
            audited = {row["module"] for row in rows}
            expected_modules = set(info["compile_order"]) - set(info["entrypoints"])
            if expected_modules - audited:
                raise ValueError(f"Axiom export omitted modules: {expected_modules - audited}")
            if audited - set(info["compile_order"]):
                raise ValueError("Axiom export includes outside-scope modules")
            for row in rows:
                if row["unsafe"] or set(row["axioms"]) - ALLOWED_AXIOMS:
                    raise ValueError(f"Unapproved axiom/unsafe declaration: {row['name']}")
            rep["axiom_declarations"] = len(rows)
            rep["axiom_union"] = sorted({a for row in rows for a in row["axioms"]})
            rep["axiom_report_sha256"] = sha(runroot / "axioms.json")
            ordered = sorted(rows, key=lambda row: (row["module"], row["name"]))
            write_json(runroot / "declarations_sorted.json", ordered)
            for scope in CONTROLS:
                for kind in ("positive", "negative", "policy"):
                    for path in sorted((workspace / "tests" / scope / kind).glob("*.lean")):
                        marker = None
                        if kind == "policy":
                            marker = ("AXIOM_POLICY_REJECTION" if scope == "formal"
                                      else "custom axiom rejected by the extension policy")
                        elif kind == "negative" and path.stem == "Placeholder":
                            marker = "sorry"
                        execute(f"{scope}_{kind}_{path.stem}", flags + [path], env,
                                negative=kind != "positive", marker=marker)
            if graph(workspace)["source_sha256"] != info["source_sha256"]:
                raise ValueError("Compiled source snapshot changed during replay")
            rep["status"] = "PASS"
        if tree_hashes(PROJECT) != before or tree_hashes(HOME / "scripts") != helpers_before:
            raise ValueError("Project or verifier inputs changed during run")
        if sha(HOME / "inventory.json") != rep["inventory_sha256"]:
            raise ValueError("Inventory changed during run")
        rep["source_unchanged_during_run"] = True
    except KeyboardInterrupt as exc:
        rep["status"] = "INTERRUPTED"
        rep["failure"] = str(exc)
    except Exception as exc:
        rep["status"] = "FAIL"
        rep["failure"] = f"{type(exc).__name__}: {exc}"
        print(rep["failure"], file=sys.stderr, flush=True)
    finally:
        rep["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print("FINAL", rep["status"], flush=True)
    return 0 if rep["status"] in ("PASS", "STATIC_CHECKS_PASS_NOT_LEAN_VERIFIED") else 1


if __name__ == "__main__":
    raise SystemExit(main())

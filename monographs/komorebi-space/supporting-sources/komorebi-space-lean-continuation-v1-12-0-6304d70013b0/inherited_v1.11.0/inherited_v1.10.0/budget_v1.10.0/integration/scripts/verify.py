#!/usr/bin/env python3
"""Clean cumulative replay from a frozen source assembly, with immutable attempts.

All project modules are compiled anew, single-threaded, with warnings as errors
and autoImplicit disabled. Only external pinned dependency caches are reused.
The audit covers all project declarations and types of all new declarations.
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
# Load the reviewed helper source directly, never a timestamp-cached .pyc.
_common_path = Path(__file__).resolve().with_name("common.py")
_common_ns = {"__file__": str(_common_path), "__name__": "_ks_reviewed_common"}
exec(compile(_common_path.read_bytes(), str(_common_path), "exec"), _common_ns)
ALLOWED_AXIOMS = _common_ns["ALLOWED_AXIOMS"]
graph = _common_ns["graph"]
sha = _common_ns["sha"]
tree_hashes = _common_ns["tree_hashes"]
runtime_hashes = _common_ns["runtime_hashes"]
write_json = _common_ns["write_json"]

HOME = Path(__file__).resolve().parents[1]
VERSION = "4.34.0-rc2"
COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"
BAD_REJECTION = ("unknown module", "unknown identifier", "unknown constant", "object file",
                 "failed to load", "no such file", "not found", "cannot execute",
                 "segmentation fault", "stack overflow", "maximum recursion depth",
                 "maximum number of heartbeats", "out of memory", "failed to synthesize")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assembly", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--path-adapter", type=Path)
    p.add_argument("--label", required=True)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--audit-timeout", type=int, default=1800)
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", a.label): p.error("Unsafe label")
    if a.timeout <= 0 or a.audit_timeout <= 0: p.error("Timeouts must be positive")
    assembly, runtime = a.assembly.resolve(), a.runtime.resolve()
    run = HOME / "runs" / a.label
    if run.exists(): p.error("Refusing to overwrite any attempt")
    run.mkdir(parents=True)
    logs, source, build = run / "logs", run / "source", run / "build"
    logs.mkdir(); build.mkdir()
    receipt = {"schema": "komorebi-space-budget-clean-replay-v1", "label": a.label,
               "status": "RUNNING", "lean_executed": False, "clean_project_build": True,
               "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "commands": [], "compile_policy": {"threads": 1, "warningAsError": True, "autoImplicit": False},
               "trust_boundary": ["Lean compiler/kernel and standard permitted axioms.",
                                  "Pinned external compiled caches are trusted and not rebuilt from source.",
                                  "Local source/control/kernel translation is reviewed separately from prose.",
                                  "Endpoint hashes cannot detect transient changes restored before recheck."],
               "timeouts_seconds": {"command": a.timeout, "audit": a.audit_timeout}}
    child = None
    def save(): write_json(run / "receipt.json", receipt)
    def interrupt(signum, frame):
        if child is not None and child.poll() is None: os.killpg(child.pid, signal.SIGKILL)
        raise KeyboardInterrupt(f"Signal {signum}")
    signal.signal(signal.SIGINT, interrupt); signal.signal(signal.SIGTERM, interrupt)
    def execute(label, argv, env, negative=False, markers=None):
        nonlocal child
        argv = list(map(str, argv)); markers = markers or []
        log = logs / (label + ".log")
        started, timed = time.monotonic(), False
        with log.open("x") as out:
            child = subprocess.Popen(argv, cwd=source, env=env, stdout=out,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            try: code = child.wait(timeout=a.audit_timeout if label == "axiom_export" else a.timeout)
            except subprocess.TimeoutExpired:
                timed = True; os.killpg(child.pid, signal.SIGKILL); child.wait(); code = 124
            finally:
                if child.poll() is None: os.killpg(child.pid, signal.SIGKILL); child.wait()
        child = None
        text = log.read_text(errors="replace")
        passed = code == 0 and not timed
        if negative:
            passed = (code == 1 and not timed and "error:" in text.lower()
                      and not any(s in text.lower() for s in BAD_REJECTION)
                      and all(s in text for s in markers))
        receipt["commands"].append({"label": label, "argv": argv, "cwd": str(source),
                                    "exit_code": code, "passed": passed, "timeout": timed,
                                    "expected_rejection": negative, "required_markers": markers,
                                    "seconds": round(time.monotonic()-started,3),
                                    "log": f"logs/{label}.log", "log_sha256": sha(log)})
        save(); print(label, "PASS" if passed else "FAIL", code, flush=True)
        if not passed: raise RuntimeError(f"{label} failed, retained log: {log}")
        return text
    try:
        save()
        invpath = assembly / "inventory.json"
        inv = json.loads(invpath.read_text())
        if inv["schema"] != "komorebi-space-budget-assembly-v1": raise ValueError("Wrong assembly schema")
        receipt["assembly_path"] = str(assembly)
        receipt["inventory_sha256"] = sha(invpath)
        input_hashes = tree_hashes(assembly / "source")
        if input_hashes != inv["project_file_sha256"]: raise ValueError("Assembly bytes changed")
        helpers = tree_hashes(HOME / "scripts")
        if helpers != inv["helpers_sha256"]: raise ValueError("Assembly used different helper revisions")
        receipt["verifier_input_sha256"] = helpers
        if sha(assembly / "source/ExportAudit.lean") != helpers["ExportAudit.lean"]:
            raise ValueError("Snapshot exporter differs from reviewed helper")
        shutil.copytree(assembly / "source", source)
        info = graph(source)
        for key in ("compile_order", "source_sha256", "compile_targets", "production_modules", "entrypoints"):
            if info[key] != inv[key]: raise ValueError(f"Snapshot graph differs: {key}")
            receipt[key] = info[key]
        receipt["explicit_theorem_lemma_count"] = info["explicit_theorem_lemma_count"]
        if (source / "wanted_modules.txt").read_text().splitlines() != info["compile_order"]:
            raise ValueError("Audit target list does not equal full graph")
        if (source / "new_modules.txt").read_text().splitlines() != inv["new_modules"]:
            raise ValueError("New module list differs")
        if json.loads((source / "control_manifest.json").read_text())["controls"] != inv["controls"]:
            raise ValueError("Control manifest differs")
        actual_controls = {p.relative_to(source).as_posix() for p in (source / "tests").rglob("*.lean")}
        if actual_controls != {c["path"] for c in inv["controls"]}: raise ValueError("Control inventory incomplete")
        receipt["new_modules"] = inv["new_modules"]
        receipt["controls"] = inv["controls"]
        receipt["source_snapshot_sha256"] = tree_hashes(source)
        if receipt["source_snapshot_sha256"] != input_hashes: raise ValueError("Incomplete source copy")
        if tree_hashes(build): raise ValueError("Project build was not empty initially")
        receipt["initial_project_objects"] = {}
        lean = runtime / "toolchain/bin/lean"
        pins = json.loads((source / "pinned-dependencies.json").read_text())["packages"]
        packages = runtime / "workspace/.lake/packages"
        caches = {pin["name"]: packages / pin["name"] / ".lake/build/lib/lean" for pin in pins}
        if not caches["mathlib"].is_dir(): raise ValueError("Missing mathlib cache")
        env = dict(os.environ)
        for key in ("LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME", "LD_PRELOAD", "LD_LIBRARY_PATH"):
            env.pop(key, None)
        env["LEAN_PATH"] = os.pathsep.join(map(str, [build] + [p for p in caches.values() if p.is_dir()]))
        env["PATH"] = str(runtime / "toolchain/bin") + os.pathsep + env.get("PATH", "")
        env["KS_COMBINED_AUDIT"] = str(run / "axioms.json")
        if a.path_adapter:
            adapter = a.path_adapter.resolve()
            if not adapter.is_file() or any(c.isspace() for c in str(adapter)): raise ValueError("Invalid adapter")
            env["LD_PRELOAD"] = str(adapter)
            receipt["executable_path_adapter"] = {"path": str(adapter), "sha256": sha(adapter)}
        receipt["environment"] = {k: env[k] for k in ("LEAN_PATH", "LD_PRELOAD") if k in env}
        receipt["dependency_cache_directories"] = {k: {"path": str(v), "exists": v.is_dir()} for k,v in caches.items()}
        receipt["runtime"] = str(runtime); receipt["lean_binary_sha256"] = sha(lean)
        runtime_scopes = ["toolchain/bin", "toolchain/lib"] + [p.relative_to(runtime).as_posix() for p in caches.values() if p.is_dir()]
        print("Hashing trusted runtime/cache inputs before replay", flush=True)
        runtime_before = runtime_hashes(runtime, runtime_scopes)
        write_json(run / "runtime_snapshot.json", runtime_before)
        receipt["runtime_snapshot_sha256"] = sha(run / "runtime_snapshot.json")
        receipt["runtime_file_count"] = len(runtime_before["file_sha256"])
        receipt["runtime_scopes"] = runtime_scopes
        receipt["lean_executed"] = True
        version = execute("lean_version", [lean, "--version"], env).strip()
        if VERSION not in version or COMMIT not in version: raise ValueError("Unexpected Lean version/commit")
        receipt["lean_version"] = version; receipt["dependencies"] = []
        for pin in pins:
            actual = execute("pin_" + pin["name"], ["git", "-C", packages / pin["name"], "rev-parse", "HEAD"], env).strip()
            if actual != pin["rev"]: raise ValueError(f"Dependency revision mismatch: {pin['name']}")
            execute("clean_" + pin["name"], ["git", "-C", packages / pin["name"], "diff", "--exit-code", "HEAD", "--"], env)
            receipt["dependencies"].append({"name": pin["name"], "expected": pin["rev"], "actual": actual})
        flags = [lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
        for mod in info["compile_order"]:
            rel = Path(mod.replace(".", "/")); out = build / rel.with_suffix(".olean")
            out.parent.mkdir(parents=True, exist_ok=True)
            execute("compile_" + mod, flags + ["-o", out, source / rel.with_suffix(".lean")], env)
        objects = tree_hashes(build)
        if set(objects) != {m.replace(".", "/") + ".olean" for m in info["compile_order"]}:
            raise ValueError("Unexpected/missing compiled objects")
        receipt["postcompile_object_sha256"] = objects; save()
        execute("axiom_export", flags + [source / "ExportAudit.lean"], env)
        audit = json.loads((run / "axioms.json").read_text()); rows = audit["declarations"]
        if not rows or audit["unexpected"] or len(rows) != audit["count"]:
            raise ValueError("Empty/inconsistent/rejected axiom report")
        if len({r["name"] for r in rows}) != len(rows): raise ValueError("Duplicate exported names")
        audited = {r["module"] for r in rows}
        if not set(info["compile_order"]) - set(info["entrypoints"]) <= audited <= set(info["compile_order"]):
            raise ValueError("Axiom report omits production modules or includes outside modules")
        for row in rows:
            if row["unsafe"] or set(row["axioms"]) - ALLOWED_AXIOMS: raise ValueError(f"Unapproved declaration: {row['name']}")
            if row["module"] in inv["new_modules"] and (not row["type"] or "⋯" in row["type"]):
                raise ValueError(f"Missing new declaration type: {row['name']}")
        receipt["axiom_declarations"] = len(rows)
        receipt["new_axiom_declarations"] = sum(r["module"] in inv["new_modules"] for r in rows)
        receipt["axiom_union"] = sorted({ax for r in rows for ax in r["axioms"]})
        receipt["axiom_report_sha256"] = sha(run / "axioms.json")
        write_json(run / "declarations_sorted.json", sorted(rows, key=lambda r: (r["module"],r["name"])))
        write_json(run / "new_declarations.json", sorted([r for r in rows if r["module"] in inv["new_modules"]],key=lambda r:r["name"]))
        for c in inv["controls"]:
            path = source / c["path"]
            label = "control_" + c["path"].removeprefix("tests/").removesuffix(".lean").replace("/", "_")
            execute(label, flags + [path], env, negative=c["kind"] != "positive", markers=c["required_markers"])
        for pin in pins:
            actual = execute("terminal_pin_" + pin["name"], ["git", "-C", packages / pin["name"], "rev-parse", "HEAD"], env).strip()
            if actual != pin["rev"]: raise ValueError(f"Terminal dependency revision mismatch: {pin['name']}")
            execute("terminal_clean_" + pin["name"], ["git", "-C", packages / pin["name"], "diff", "--exit-code", "HEAD", "--"], env)
        print("Hashing trusted runtime/cache inputs after replay", flush=True)
        if runtime_hashes(runtime, runtime_scopes) != runtime_before:
            raise ValueError("Trusted runtime/cache bytes or symlink targets changed")
        if sha(run / "runtime_snapshot.json") != receipt["runtime_snapshot_sha256"]:
            raise ValueError("Runtime snapshot record changed")
        receipt["runtime_unchanged_during_run"] = True
        if tree_hashes(source) != input_hashes or tree_hashes(assembly / "source") != input_hashes:
            raise ValueError("Source/control snapshot or original assembly changed")
        if tree_hashes(HOME / "scripts") != helpers: raise ValueError("Verifier helpers changed")
        if sha(invpath) != receipt["inventory_sha256"]: raise ValueError("Inventory changed")
        if tree_hashes(build) != objects: raise ValueError("Objects changed during audit/controls")
        if sha(lean) != receipt["lean_binary_sha256"]: raise ValueError("Compiler binary changed")
        if a.path_adapter and sha(a.path_adapter.resolve()) != receipt["executable_path_adapter"]["sha256"]:
            raise ValueError("Path adapter changed")
        # Closed-form command inventory, independently checked again by postflight.py.
        expected = ["lean_version"]
        for pin in pins: expected.extend(["pin_"+pin["name"], "clean_"+pin["name"]])
        expected.extend("compile_"+m for m in info["compile_order"]); expected.append("axiom_export")
        expected.extend("control_"+c["path"].removeprefix("tests/").removesuffix(".lean").replace("/","_") for c in inv["controls"])
        for pin in pins: expected.extend(["terminal_pin_"+pin["name"], "terminal_clean_"+pin["name"]])
        if [c["label"] for c in receipt["commands"]] != expected or len(set(expected)) != len(expected):
            raise ValueError("Missing/extra/duplicate commands")
        receipt["object_sha256"] = objects
        receipt["source_unchanged_during_run"] = True
        receipt["helpers_unchanged_during_run"] = True
        receipt["objects_unchanged_after_compile"] = True
        receipt["exact_command_labels"] = expected
        receipt["status"] = "PASS"
    except KeyboardInterrupt as exc: receipt.update(status="INTERRUPTED", failure=str(exc))
    except Exception as exc:
        receipt.update(status="FAIL", failure=f"{type(exc).__name__}: {exc}")
        print(receipt["failure"], file=sys.stderr, flush=True)
    finally:
        receipt["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(); save()
    print("FINAL", receipt["status"], flush=True)
    return 0 if receipt["status"] == "PASS" else 1

if __name__ == "__main__": raise SystemExit(main())

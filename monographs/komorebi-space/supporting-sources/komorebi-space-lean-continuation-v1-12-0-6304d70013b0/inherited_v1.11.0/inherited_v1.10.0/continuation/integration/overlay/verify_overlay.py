#!/usr/bin/env python3
"""Fresh WR overlay replay over a hash-validated accepted clean cumulative base.

This is deliberately INCREMENTAL: inherited object files are copied from the
accepted base, new modules and a combined root are compiled from source, and the
whole resulting environment receives a fresh axiom audit and all controls.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOME / "scripts"))
from common import ALLOWED_AXIOMS, ROOT_MODULE, graph, sha, write_json
from verify import CONTROLS, VERSION, COMMIT, tree_hashes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", type=Path, required=True, help="Completed base run directory")
    ap.add_argument("--overlay", type=Path, required=True)
    ap.add_argument("--base-postflight", type=Path, required=True,
                    help="Independent terminal snapshot and complete-command validation receipt")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--path-adapter", type=Path)
    ap.add_argument("--label", required=True)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--audit-timeout", type=int, default=1800)
    args = ap.parse_args()
    if not args.label or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.label):
        ap.error("Use an alphanumeric label")
    base, overlay, runtime = args.base.resolve(), args.overlay.resolve(), args.runtime.resolve()
    runroot = HOME / "runs" / args.label
    if runroot.exists():
        ap.error("Existing labels are immutable")
    runroot.mkdir(parents=True)
    logs = runroot / "logs"
    logs.mkdir()
    work, build = runroot / "source", runroot / "build"
    rep = {"schema": "komorebi-space-incremental-overlay-v1", "status": "RUNNING",
           "label": args.label, "lean_executed": False, "clean_project_build": False,
           "scope": "New WR modules compiled over accepted clean cumulative objects; fresh full axiom audit",
           "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "commands": [], "base_receipt_path": str(base / "receipt.json"),
           "trust_boundary": ["The accepted base's unchanged compiled project objects are reused.",
                              "Official Lean kernel/compiler and pinned external caches remain trusted.",
                              "No universal verification of Python or prose translation."]}

    def save():
        write_json(runroot / "receipt.json", rep)

    child = None

    def interrupt(signum, frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
        raise KeyboardInterrupt(f"Signal {signum}")

    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)

    def execute(label, argv, env, negative=False, marker=None):
        nonlocal child
        log, start = logs / (label + ".log"), time.monotonic()
        timed = False
        with log.open("w") as stream:
            child = subprocess.Popen(list(map(str, argv)), cwd=work, env=env,
                                     stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = child.wait(timeout=args.audit_timeout if label == "axiom_export" else args.timeout)
            except subprocess.TimeoutExpired:
                timed = True
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
                code = 124
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
        child = None
        output = log.read_text(errors="replace")
        passed = code == 0 and not timed
        if negative:
            bad = ("unknown module", "unknown identifier", "unknown constant", "object file",
                   "failed to load", "no such file", "not found", "cannot execute",
                   "segmentation fault", "stack overflow")
            passed = (code > 0 and not timed and "error" in output.lower()
                      and not any(x in output.lower() for x in bad)
                      and (marker is None or marker in output))
        rep["commands"].append({"label": label, "argv": list(map(str, argv)), "exit_code": code,
                                "passed": passed, "expected_rejection": negative, "required_marker": marker,
                                "timeout": timed, "seconds": round(time.monotonic() - start, 3),
                                "log": str(log.relative_to(runroot)), "log_sha256": sha(log)})
        save()
        print(label, "PASS" if passed else "FAIL", code, flush=True)
        if not passed:
            raise RuntimeError(f"{label} failed; see {log}")
        return output

    try:
        save()
        previous = json.loads((base / "receipt.json").read_text())
        if (previous.get("schema") != "komorebi-space-combined-replay-v1"
                or previous.get("status") != "PASS" or not previous.get("clean_project_build")
                or not previous.get("lean_executed")):
            raise ValueError("Base is not an accepted completed clean cumulative replay")
        if not previous.get("source_unchanged_during_run") or not previous.get("axiom_declarations"):
            raise ValueError("Base lacks source-preservation or axiom-audit evidence")
        rep["base_receipt_sha256"] = sha(base / "receipt.json")
        inventory = json.loads((HOME / "inventory.json").read_text())
        if sha(HOME / "inventory.json") != previous["inventory_sha256"]:
            raise ValueError("Base inventory identity differs from current frozen assembly")
        for key in ("source_sha256", "compile_order", "compile_targets", "production_modules", "project_file_sha256"):
            if previous[key] != inventory[key]:
                raise ValueError(f"Base receipt has unexpected graph/source scope: {key}")
        base_graph = graph(base / "source")
        for key in ("source_sha256", "compile_order", "compile_targets", "production_modules"):
            if base_graph[key] != inventory[key]:
                raise ValueError(f"Base actual graph differs from archive inventory: {key}")
        base_pins = json.loads((base / "source/pinned-dependencies.json").read_text())["packages"]
        expected_labels = ["lean_version"]
        for pin in base_pins:
            expected_labels.extend(["pin_" + pin["name"], "clean_" + pin["name"]])
        expected_labels.extend("compile_" + mod for mod in inventory["compile_order"])
        expected_labels.append("axiom_export")
        for scope, counts in CONTROLS.items():
            for kind, count in counts.items():
                controls = sorted((base / "source/tests" / scope / kind).glob("*.lean"))
                if len(controls) != count:
                    raise ValueError("Incomplete base control inventory")
                expected_labels.extend(f"{scope}_{kind}_{p.stem}" for p in controls)
        labels = [command["label"] for command in previous["commands"]]
        if labels != expected_labels or len(labels) != len(set(labels)):
            raise ValueError("Base commands are missing, duplicated, extra, or in an unexpected order")
        postflight_path = args.base_postflight.resolve()
        postflight = json.loads(postflight_path.read_text())
        if (postflight.get("schema") != "komorebi-space-base-postflight-v1"
                or postflight.get("status") != "PASS"
                or postflight.get("base_receipt_sha256") != rep["base_receipt_sha256"]):
            raise ValueError("Independent base postflight is missing, rejected, or bound to a different receipt")
        if postflight["inventory_sha256"] != previous["inventory_sha256"] or postflight["exact_command_labels"] != expected_labels:
            raise ValueError("Independent postflight covers different inputs or commands")
        if postflight["source_snapshot_sha256"] != tree_hashes(base / "source"):
            raise ValueError("Base complete source/control snapshot differs from postflight")
        if postflight["object_sha256"] != tree_hashes(base / "build"):
            raise ValueError("Base object snapshot differs from postflight")
        rep["base_postflight_path"] = str(postflight_path)
        rep["base_postflight_sha256"] = sha(postflight_path)
        rep["base_axiom_report_sha256"] = sha(base / "axioms.json")
        if rep["base_axiom_report_sha256"] != previous["axiom_report_sha256"]:
            raise ValueError("Base axiom report hash mismatch")
        for command in previous["commands"]:
            if not command["passed"] or sha(base / command["log"]) != command["log_sha256"]:
                raise ValueError(f"Base command evidence invalid: {command['label']}")
        for rel, digest in previous["project_file_sha256"].items():
            if sha(base / "source" / rel) != digest:
                raise ValueError(f"Base source snapshot changed: {rel}")
        if tree_hashes(base / "build") != previous["object_sha256"]:
            raise ValueError("Base compiled object inventory changed")
        current_inputs = {"overlay": tree_hashes(overlay), "helpers": tree_hashes(HOME / "scripts"),
                          "this_script": sha(Path(__file__))}
        rep["input_sha256"] = current_inputs
        modules = sorted((overlay / "KomorebiSpace").rglob("*.lean"))
        if not modules:
            raise ValueError("No new production modules supplied")
        new_names = [".".join(p.relative_to(overlay).with_suffix("").parts) for p in modules]
        new_controls = {kind: sorted((overlay / "tests" / kind).glob("*.lean"))
                        for kind in ("positive", "negative", "policy")}
        if not new_controls["positive"] or not new_controls["negative"]:
            raise ValueError("New overlay needs positive and negative control files")
        shutil.copytree(base / "source", work)
        shutil.copytree(base / "build", build)
        for path in modules:
            rel = path.relative_to(overlay)
            if (work / rel).exists():
                raise ValueError(f"Overlay cannot overwrite an inherited production module: {rel}")
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, work / rel)
        for kind, paths in new_controls.items():
            for path in paths:
                dest = work / "tests" / "new" / kind / path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
        root = work / f"{ROOT_MODULE}.lean"
        root.write_text(root.read_text() + "".join(f"import {name}\n" for name in sorted(new_names)))
        info = graph(work)
        (work / "wanted_modules.txt").write_text("\n".join(info["compile_order"]) + "\n")
        (work / "new_modules.txt").write_text("\n".join(sorted(new_names)) + "\n")
        exporter = (HOME / "scripts/ExportAudit.lean").read_text()
        old = '  let wantedTypes := '
        if exporter.count(old) != 1:
            raise ValueError("Unexpected exporter template")
        exporter = exporter.replace(old, '  let newModules := ((← IO.FS.readFile "new_modules.txt").splitOn "\\n").toArray\n' + old)
        old_condition = '((extensionModule || closureModule) && kind == "theorem")'
        if exporter.count(old_condition) != 1:
            raise ValueError("Unexpected exporter type-selection template")
        exporter = exporter.replace(old_condition,
                                     '((extensionModule || closureModule || newModules.contains modName.toString) && kind == "theorem")')
        (work / "ExportAudit.lean").write_text(exporter)
        snapshot_hashes = tree_hashes(work)
        rep["source_snapshot_sha256"] = snapshot_hashes
        rep["source_sha256"] = info["source_sha256"]
        rep["production_modules"] = info["production_modules"]
        rep["complete_module_order"] = info["compile_order"]
        compile_order = [m for m in info["compile_order"] if m in new_names or m == ROOT_MODULE]
        rep["compiled_from_source"] = compile_order
        rep["reused_base_modules"] = [m for m in previous["compile_order"] if m != ROOT_MODULE]
        rep["reused_base_object_sha256"] = previous["object_sha256"]
        rep["control_counts"] = dict(CONTROLS, new={kind: len(paths) for kind, paths in new_controls.items()})
        lean = runtime / "toolchain/bin/lean"
        if sha(lean) != previous["lean_binary_sha256"]:
            raise ValueError("Compiler differs from accepted base")
        rep["runtime"] = str(runtime)
        rep["lean_binary_sha256"] = sha(lean)
        rep["dependencies"] = []
        pins = json.loads((work / "pinned-dependencies.json").read_text())["packages"]
        packages = runtime / "workspace/.lake/packages"
        caches = [packages / pin["name"] / ".lake/build/lib/lean" for pin in pins]
        env = dict(os.environ)
        for key in ("LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME"):
            env.pop(key, None)
        env["PATH"] = str(runtime / "toolchain/bin") + os.pathsep + env.get("PATH", "")
        env["LEAN_PATH"] = os.pathsep.join(map(str, [build] + [p for p in caches if p.is_dir()]))
        env["KS_COMBINED_AUDIT"] = str(runroot / "axioms.json")
        if args.path_adapter:
            adapter = args.path_adapter.resolve()
            if sha(adapter) != previous.get("executable_path_adapter", {}).get("sha256"):
                raise ValueError("Path adapter differs from accepted base")
            env["LD_PRELOAD"] = str(adapter) + ((":" + env["LD_PRELOAD"]) if env.get("LD_PRELOAD") else "")
        rep["environment"] = {key: env[key] for key in ("LEAN_PATH", "LD_PRELOAD") if key in env}
        rep["lean_executed"] = True
        version = execute("lean_version", [lean, "--version"], env).strip()
        if VERSION not in version or COMMIT not in version:
            raise ValueError("Wrong compiler version")
        rep["lean_version"] = version
        for pin in pins:
            actual = execute("pin_" + pin["name"], ["git", "-C", packages / pin["name"], "rev-parse", "HEAD"], env).strip()
            if actual != pin["rev"]:
                raise ValueError("Wrong dependency revision")
            execute("clean_" + pin["name"], ["git", "-C", packages / pin["name"], "diff", "--exit-code", "HEAD", "--"], env)
            rep["dependencies"].append({"name": pin["name"], "expected": pin["rev"], "actual": actual})
        flags = [lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
        for mod in compile_order:
            rel = Path(mod.replace(".", "/"))
            out = build / rel.with_suffix(".olean")
            out.parent.mkdir(parents=True, exist_ok=True)
            execute("compile_" + mod, flags + ["-o", out, work / rel.with_suffix(".lean")], env)
        compiled_objects = tree_hashes(build)
        if set(compiled_objects) != {m.replace(".", "/") + ".olean" for m in info["compile_order"]}:
            raise ValueError("Object tree differs from exact complete module inventory")
        for rel, digest in previous["object_sha256"].items():
            if rel != ROOT_MODULE + ".olean" and compiled_objects.get(rel) != digest:
                raise ValueError(f"Inherited compiled object changed before full audit: {rel}")
        rep["postcompile_object_sha256"] = compiled_objects
        execute("axiom_export", flags + [work / "ExportAudit.lean"], env)
        audit = json.loads((runroot / "axioms.json").read_text())
        rows = audit["declarations"]
        if not rows or audit["unexpected"] or len(rows) != audit["count"]:
            raise ValueError("Failed or incomplete cumulative axiom export")
        if len({r["name"] for r in rows}) != len(rows):
            raise ValueError("Duplicate exported declaration names")
        actual_modules = {r["module"] for r in rows}
        if set(info["compile_order"]) - set(info["entrypoints"]) - actual_modules:
            raise ValueError("Axiom report misses production modules")
        if actual_modules - set(info["compile_order"]):
            raise ValueError("Axiom report contains outside-scope declarations")
        for row in rows:
            if row["unsafe"] or set(row["axioms"]) - ALLOWED_AXIOMS:
                raise ValueError(f"Rejected axiom dependency: {row['name']}")
        rep["axiom_declarations"] = len(rows)
        rep["new_axiom_declarations"] = sum(r["module"] in new_names for r in rows)
        rep["axiom_union"] = sorted({a for row in rows for a in row["axioms"]})
        rep["axiom_report_sha256"] = sha(runroot / "axioms.json")
        write_json(runroot / "declarations_sorted.json", sorted(rows, key=lambda r: (r["module"], r["name"])))
        for scope, counts in rep["control_counts"].items():
            for kind, count in counts.items():
                paths = sorted((work / "tests" / scope / kind).glob("*.lean"))
                if len(paths) != count:
                    raise ValueError(f"Changed control inventory: {scope}/{kind}")
                for path in paths:
                    marker = None
                    if kind == "policy":
                        if scope == "formal":
                            marker = "AXIOM_POLICY_REJECTION"
                        elif scope == "extension":
                            marker = "custom axiom rejected by the extension policy"
                    if kind == "negative" and path.stem == "Placeholder":
                        marker = "sorry"
                    execute(f"{scope}_{kind}_{path.stem}", flags + [path], env,
                            negative=kind != "positive", marker=marker)
        if snapshot_hashes != tree_hashes(work):
            raise ValueError("Source/control/exporter snapshot changed during replay")
        if current_inputs != {"overlay": tree_hashes(overlay), "helpers": tree_hashes(HOME / "scripts"),
                              "this_script": sha(Path(__file__))}:
            raise ValueError("Overlay or verifier inputs changed during replay")
        if sha(base / "receipt.json") != rep["base_receipt_sha256"] or tree_hashes(base / "build") != previous["object_sha256"]:
            raise ValueError("Accepted baseline evidence changed during overlay replay")
        if sha(postflight_path) != rep["base_postflight_sha256"]:
            raise ValueError("Independent base postflight changed during overlay replay")
        if postflight["source_snapshot_sha256"] != tree_hashes(base / "source"):
            raise ValueError("Base source/control snapshot changed during overlay replay")
        if compiled_objects != tree_hashes(build):
            raise ValueError("Compiled objects changed between compilation, full audit, and controls")
        rep["object_sha256"] = compiled_objects
        rep["source_unchanged_during_run"] = True
        rep["status"] = "PASS"
    except KeyboardInterrupt as exc:
        rep["status"], rep["failure"] = "INTERRUPTED", str(exc)
    except Exception as exc:
        rep["status"], rep["failure"] = "FAIL", f"{type(exc).__name__}: {exc}"
        print(rep["failure"], flush=True)
    finally:
        rep["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print("FINAL", rep["status"], flush=True)
    return 0 if rep["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

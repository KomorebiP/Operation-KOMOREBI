#!/usr/bin/env python3
"""Fresh, sequential verification of the complete publication Lean source tree.

Only Python's standard library is required. Install the pinned Lean/Lake and
prepare the locked external dependency caches before running this command.
No existing project object files are used. Every attempt has a new directory.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

VERSION = "4.34.0-rc2"
COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
ENTRYPOINTS = {"KomorebiSpace", "KomorebiSpaceRegularization",
               "KomorebiSpaceCombined", "KomorebiSpaceDiagonal"}
BAD_REJECTION = ("unknown module", "unknown identifier", "unknown constant", "object file",
                 "failed to load", "no such file", "not found", "cannot execute",
                 "segmentation fault", "stack overflow", "maximum recursion depth",
                 "maximum number of heartbeats", "out of memory", "failed to synthesize")


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def strip_comments(text):
    """Preserve Lean strings and newlines; erase nested block and line comments."""
    result, index, depth, in_string = [], 0, 0, False
    while index < len(text):
        pair = text[index:index + 2]
        if depth:
            if pair in ("/-", "-/"):
                depth += 1 if pair == "/-" else -1
                result.extend("  "); index += 2
            else:
                result.append("\n" if text[index] == "\n" else " "); index += 1
        elif in_string:
            result.append(text[index])
            if text[index] == "\\" and index + 1 < len(text):
                index += 1; result.append(text[index])
            elif text[index] == '"':
                in_string = False
            index += 1
        elif pair == "/-":
            depth = 1; result.extend("  "); index += 2
        elif pair == "--":
            end = text.find("\n", index)
            if end < 0:
                end = len(text)
            result.extend(" " * (end - index)); index = end
        else:
            in_string = text[index] == '"'
            result.append(text[index]); index += 1
    if depth or in_string:
        raise ValueError("Unterminated Lean comment or string")
    return "".join(result)


def source_files(publication):
    project = publication / "lean"
    paths = list((project / "KomorebiSpace").rglob("*.lean"))
    paths += list(project.glob("KomorebiSpace*.lean"))
    paths += [project / n for n in ("lean-toolchain", "lakefile.toml", "lake-manifest.json")]
    paths += [p for p in (publication / "verification/runner").rglob("*")
              if p.is_file() and "__pycache__" not in p.parts]
    if any(p.is_symlink() for p in paths):
        raise ValueError("Symlinked project/runner inputs are not accepted")
    return sorted(paths)


def source_hashes(publication):
    return {p.relative_to(publication).as_posix(): sha(p) for p in source_files(publication)}


def graph(project):
    files = sorted((project / "KomorebiSpace").rglob("*.lean"))
    files += sorted(project.glob("KomorebiSpace*.lean"))
    modules = {".".join(p.relative_to(project).with_suffix("").parts): p for p in files}
    roots = {m for m in modules if "." not in m}
    if roots != ENTRYPOINTS:
        raise ValueError(f"Unexpected entrypoint set: {sorted(roots)}")
    imports, theorem_count = {}, 0
    for module, path in sorted(modules.items()):
        text = strip_comments(path.read_text(encoding="utf-8"))
        if re.search(r"\b(?:sorry|admit|axiom|native_decide|unsafe)\b", text):
            raise ValueError(f"Forbidden production token in {module}")
        if re.search(r"\bset_option\s+(?:autoImplicit\s+true|warningAsError\s+false)\b", text):
            raise ValueError(f"Production weakens compiler policy: {module}")
        local = []
        for line in text.splitlines():
            if re.match(r"^\s*import\s+", line):
                local += [dep for dep in line.split()[1:] if dep.startswith("KomorebiSpace")]
        imports[module] = sorted(set(local))
        if set(local) - modules.keys():
            raise ValueError(f"Missing local imports in {module}")
        theorem_count += len(re.findall(r"\b(?:theorem|lemma)\s+[\w'.]+", text))
    order, active, done = [], set(), set()
    def visit(module):
        if module in done:
            return
        if module in active:
            raise ValueError(f"Import cycle at {module}")
        active.add(module)
        for dependency in imports[module]:
            visit(dependency)
        active.remove(module); done.add(module); order.append(module)
    for root in sorted(roots):
        visit(root)
    if done != modules.keys():
        raise ValueError(f"Project modules unreachable from entrypoints: {sorted(modules.keys() - done)}")
    return {"compile_order": order, "entrypoints": sorted(roots), "local_imports": imports,
            "production_modules": len(modules) - len(roots), "compile_targets": len(modules),
            "explicit_theorem_lemma_count": theorem_count}


def runtime_hashes(scopes):
    """Bind trusted installed bytes, not their authenticity or build provenance."""
    files, links, resolved = {}, {}, {}
    for label, path in sorted(scopes.items()):
        path = Path(path).resolve()
        members = [path] if path.is_file() else sorted(path.rglob("*"))
        for member in members:
            relative = "." if member == path else member.relative_to(path).as_posix()
            key = label + "/" + relative
            if member.is_symlink():
                if not member.is_file():
                    raise ValueError(f"Unsupported runtime directory/broken symlink: {member}")
                links[key] = os.readlink(member)
            if member.is_file():
                target = str(member.resolve())
                if target not in resolved:
                    resolved[target] = sha(member)
                files[key] = resolved[target]
    return {"scopes": {k: str(Path(v).resolve()) for k, v in scopes.items()},
            "file_sha256": files, "symlink_targets": links}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True, help="New directory outside the publication")
    parser.add_argument("--timeout", type=int, default=300, help="Seconds per compiler/control command")
    parser.add_argument("--audit-timeout", type=int, default=1800)
    parser.add_argument("--plan-only", action="store_true", help="Snapshot/static validation only; no Lean verdict")
    args = parser.parse_args()
    publication, output = args.publication.resolve(), args.output.resolve()
    if output == publication or publication in output.parents:
        parser.error("Output must be outside the publication input tree")
    if output.exists():
        parser.error("Refusing to overwrite an existing attempt directory")
    if args.timeout <= 0 or args.audit_timeout <= 0:
        parser.error("Timeouts must be positive")
    output.mkdir(parents=True); (output / "logs").mkdir(); (output / "build").mkdir()
    receipt = {"schema": "komorebi-publication-integrated-replay-v1", "status": "RUNNING",
               "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "commands": [], "controls": [], "lean_executed": False,
               "compile_policy": {"threads": 1, "warningAsError": True, "autoImplicit": False},
               "trust_boundary": ["Lean kernel/compiler and the three permitted standard axioms.",
                   "Installed external dependency caches are trusted, byte-bound at endpoints, and not rebuilt or authenticated.",
                   "Statement correspondence and source review are separate from compiler acceptance.",
                   "Endpoint identity does not detect transient changes restored before the final snapshot."],
               "timeouts_seconds": {"command": args.timeout, "audit": args.audit_timeout}}
    def save():
        write_json(output / "receipt.json", receipt)
    def execute(label, argv, cwd, env, timeout=None):
        log = output / "logs" / (label + ".log")
        started, timed_out = time.monotonic(), False
        with log.open("x", encoding="utf-8") as stream:
            options = {"start_new_session": True} if os.name == "posix" else {}
            child = subprocess.Popen([str(v) for v in argv], cwd=cwd, env=env,
                                     stdout=stream, stderr=subprocess.STDOUT, **options)
            try:
                code = child.wait(timeout=timeout or args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "posix":
                    os.killpg(child.pid, signal.SIGKILL)
                else:
                    child.kill()
                child.wait(); code = 124
            except BaseException:
                if child.poll() is None:
                    if os.name == "posix":
                        os.killpg(child.pid, signal.SIGKILL)
                    else:
                        child.kill()
                    child.wait()
                raise
        text = log.read_text(encoding="utf-8", errors="replace")
        command = {"label": label, "argv": list(map(str, argv)), "cwd": str(cwd),
                   "exit_code": code, "timeout": timed_out, "seconds": round(time.monotonic()-started, 3),
                   "log": log.relative_to(output).as_posix(), "log_sha256": sha(log)}
        receipt["commands"].append(command); save()
        print(label, "exit", code, flush=True)
        return command, text
    def require(label, argv, cwd, env, timeout=None):
        result, text = execute(label, argv, cwd, env, timeout)
        if result["exit_code"] != 0 or result["timeout"]:
            raise RuntimeError(f"{label} failed; inspect {result['log']}")
        return text
    try:
        save()
        before = source_hashes(publication)
        receipt["publication_path"] = str(publication)
        receipt["input_sha256"] = before
        snapshot = output / "snapshot"
        for relative in before:
            target = snapshot / relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(publication / relative, target)
        if source_hashes(snapshot) != before:
            raise ValueError("Source snapshot differs from inputs")
        project, runner = snapshot / "lean", snapshot / "verification/runner"
        info = graph(project); receipt.update(info)
        manifest = json.loads((runner / "control_manifest.json").read_text(encoding="utf-8"))
        controls = manifest["controls"]
        actual_controls = {p.relative_to(runner).as_posix() for p in (runner / "controls").rglob("*.lean")}
        if actual_controls != {c["path"] for c in controls} or len({c["id"] for c in controls}) != len(controls):
            raise ValueError("Missing, duplicate, or unregistered control")
        for control in controls:
            if sha(runner / control["path"]) != control["sha256"]:
                raise ValueError(f"Control bytes differ from manifest: {control['id']}")
        receipt["control_manifest_sha256"] = sha(runner / "control_manifest.json")
        receipt["control_specifications"] = controls
        if args.plan_only:
            receipt.update(status="STATIC_VALIDATION_ONLY", lean_executed=False)
            return 0
        original_project = publication / "lean"
        inherited_env = dict(os.environ)
        probe = "import json,os,shutil;print(json.dumps({'lean':shutil.which('lean'),'PATH':os.environ.get('PATH'),'LEAN_SYSROOT':os.environ.get('LEAN_SYSROOT')}))"
        runtime = json.loads(require("lake_environment", ["lake", "env", sys.executable, "-c", probe], original_project, inherited_env))
        lean = Path(runtime["lean"]).resolve()
        environment = dict(inherited_env)
        environment["PATH"] = runtime["PATH"]
        if runtime["LEAN_SYSROOT"]:
            environment["LEAN_SYSROOT"] = runtime["LEAN_SYSROOT"]
        receipt["lean_executed"] = True
        version = require("lean_version", [lean, "--version"], project, environment).strip()
        if VERSION not in version or COMMIT not in version:
            raise ValueError("Unexpected compiler version/commit")
        receipt["lean_version"] = version
        prefix = Path(require("lean_prefix", [lean, "--print-prefix"], project, environment).strip())
        pins = json.loads((project / "lake-manifest.json").read_text(encoding="utf-8"))["packages"]
        packages = original_project / ".lake/packages"
        caches, scopes = [], {"lean_bin": prefix / "bin", "lean_lib": prefix / "lib"}
        receipt["dependencies"] = []
        for pin in pins:
            package = packages / pin["name"]
            revision = require("pin_" + pin["name"], ["git", "-C", package, "rev-parse", "HEAD"], project, environment).strip()
            if revision != pin["rev"]:
                raise ValueError(f"Dependency revision mismatch: {pin['name']}")
            require("clean_" + pin["name"], ["git", "-C", package, "diff", "--exit-code", "HEAD", "--"], project, environment)
            cache = package / ".lake/build/lib/lean"
            if cache.is_dir():
                caches.append(cache.resolve()); scopes["dependency_" + pin["name"]] = cache
            receipt["dependencies"].append({"name": pin["name"], "expected_revision": pin["rev"], "actual_revision": revision, "cache_exists": cache.is_dir()})
        if not (packages / "mathlib/.lake/build/lib/lean").is_dir():
            raise ValueError("Missing pinned mathlib cache; run lake exe cache get first")
        for index, adapter in enumerate(environment.get("LD_PRELOAD", "").split(":")):
            if adapter:
                if not Path(adapter).is_file():
                    raise ValueError("LD_PRELOAD entries must be explicit existing files for provenance")
                scopes["inherited_preload_" + str(index)] = Path(adapter)
        environment["LEAN_PATH"] = os.pathsep.join(map(str, [output / "build"] + caches))
        environment.pop("LEAN_SRC_PATH", None)
        receipt["effective_environment"] = {k: environment[k] for k in ("PATH", "LEAN_PATH", "LEAN_SYSROOT", "LD_PRELOAD", "LD_LIBRARY_PATH") if k in environment}
        print("Hashing installed compiler and dependency cache bytes", flush=True)
        runtime_before = runtime_hashes(scopes)
        write_json(output / "runtime_snapshot.json", runtime_before)
        receipt["runtime_snapshot_sha256"] = sha(output / "runtime_snapshot.json")
        flags = [lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
        for module in info["compile_order"]:
            relative = Path(module.replace(".", "/"))
            destination = output / "build" / relative.with_suffix(".olean")
            destination.parent.mkdir(parents=True, exist_ok=True)
            require("compile_" + module, flags + ["-o", destination, project / relative.with_suffix(".lean")], project, environment)
        objects = {p.relative_to(output / "build").as_posix(): sha(p) for p in (output / "build").rglob("*.olean")}
        if set(objects) != {m.replace(".", "/") + ".olean" for m in info["compile_order"]}:
            raise ValueError("Project object inventory differs from compile targets")
        receipt["fresh_object_sha256"] = objects
        audit_source = output / "Inventory.lean"
        audit_source.write_text("".join("import " + m + "\n" for m in info["entrypoints"]) + (runner / "Inventory.lean").read_text(encoding="utf-8"), encoding="utf-8")
        module_file = output / "wanted_modules.txt"
        module_file.write_text("\n".join(info["compile_order"]) + "\n", encoding="utf-8")
        environment["KOMOREBI_AUDIT_MODULES"] = str(module_file)
        environment["KOMOREBI_AUDIT_OUTPUT"] = str(output / "declarations.json")
        receipt["generated_audit_sha256"] = sha(audit_source)
        require("declaration_inventory", flags + [audit_source], project, environment, args.audit_timeout)
        inventory = json.loads((output / "declarations.json").read_text(encoding="utf-8"))
        rows = inventory["declarations"]
        if not rows or len(rows) != inventory["count"] or inventory["rejected"] or len({r["name"] for r in rows}) != len(rows):
            raise ValueError("Empty, duplicate, inconsistent, or rejected declaration inventory")
        audited = {r["module"] for r in rows}
        if not set(info["compile_order"]) - ENTRYPOINTS <= audited <= set(info["compile_order"]):
            raise ValueError("Declaration provenance omits project modules or includes dependencies")
        if any(r["unsafe"] or r["axiom_declaration"] or set(r["axioms"]) - ALLOWED for r in rows):
            raise ValueError("Forbidden axiom or unsafe declaration")
        receipt["exported_declarations"] = len(rows)
        receipt["axiom_union"] = sorted({ax for row in rows for ax in row["axioms"]})
        receipt["declarations_sha256"] = sha(output / "declarations.json")
        for control in controls:
            command, text = execute("control_" + control["id"], flags + [runner / control["path"]], project, environment)
            missing = [marker for marker in control["required_markers"] if marker not in text]
            infrastructure_error = any(token in text.lower() for token in BAD_REJECTION)
            groups = re.findall(r"depends on axioms: \[([^\]]*)\]", text)
            foreign = sorted({a.strip() for group in groups for a in group.split(",") if a.strip()} - ALLOWED)
            compiled = command["exit_code"] == 0 and not command["timeout"]
            rejected = command["exit_code"] == 1 and not command["timeout"] and "error:" in text.lower() and not infrastructure_error
            expected, stage = control["expected"], control["policy_stage"]
            passed = not missing and ((expected == "accept" and compiled)
                or (expected == "elaboration_reject" and rejected)
                or (expected == "policy_reject" and stage == "embedded" and rejected)
                or (expected == "policy_reject" and stage == "external_axiom_check" and compiled and bool(groups) and bool(foreign)))
            receipt["controls"].append({"id": control["id"], "expected": expected, "policy_stage": stage,
                "compiler_exit_code": command["exit_code"], "compiler_success": compiled,
                "policy_verdict": ("reject" if passed else "unexpected") if expected == "policy_reject" else "not_applicable",
                "missing_markers": missing, "infrastructure_error": infrastructure_error,
                "foreign_axioms": foreign, "passed": bool(passed)})
            save()
            if not passed:
                raise RuntimeError(f"Unexpected control outcome: {control['id']}")
        for pin in pins:
            package = packages / pin["name"]
            revision = require("terminal_pin_" + pin["name"], ["git", "-C", package, "rev-parse", "HEAD"], project, environment).strip()
            if revision != pin["rev"]:
                raise ValueError(f"Dependency revision changed: {pin['name']}")
            require("terminal_clean_" + pin["name"], ["git", "-C", package, "diff", "--exit-code", "HEAD", "--"], project, environment)
        print("Checking endpoint source, object, and runtime identity", flush=True)
        if source_hashes(publication) != before or source_hashes(snapshot) != before:
            raise ValueError("Project sources, controls, or verifier changed during the run")
        if runtime_hashes(scopes) != runtime_before:
            raise ValueError("Compiler or dependency cache bytes changed during the run")
        if objects != {p.relative_to(output / "build").as_posix(): sha(p) for p in (output / "build").rglob("*.olean")}:
            raise ValueError("Fresh project objects changed after compilation")
        receipt.update(status="PASS", source_unchanged=True, runtime_unchanged=True,
                       objects_unchanged=True, control_counts=dict(collections.Counter(c["expected"] for c in controls)))
    except KeyboardInterrupt:
        receipt.update(status="INTERRUPTED", failure="KeyboardInterrupt; no passing replay claimed")
    except Exception as error:
        receipt.update(status="FAIL", failure=f"{type(error).__name__}: {error}")
        print(receipt["failure"], file=sys.stderr, flush=True)
    finally:
        receipt["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(); save()
    print("FINAL", receipt["status"], flush=True)
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

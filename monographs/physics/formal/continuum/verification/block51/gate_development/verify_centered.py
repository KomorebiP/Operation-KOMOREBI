#!/usr/bin/env python3
"""Fresh, scoped Lean verification of the centered Dirac extension.

No downloads, no overwrites, and no pre-existing local project objects are used.
The external pinned compiler/dependency cache is reused and checked against its
shipped manifest (mutable Git index metadata is explicitly excluded).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import time

LEAN_COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"
MATHLIB_COMMIT = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
RUNTIME_MANIFEST_SHA = "3d038009d119676dd1e61146556da63379bccbf2ae89fac6e33f1efa147e8f05"
GENERATOR_SHA = "ee721cc3ab78f500bab87c1edb358be8b30a0892e7047c9e9cb5aa31a6d51499"
NEW_MODULES = [
    "KomorebiPhysics.Relativistic3DCenteredConvergence",
    "KomorebiPhysics.Relativistic3DModalPerturbation",
    "KomorebiPhysics.Relativistic3DCenteredRates",
    "KomorebiPhysics.Relativistic3DCenteredResolvent",
]
ROOT_MODULES = ["KomorebiPhysics.Relativistic3DGeneratorBridge", *NEW_MODULES]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
MODULE_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*\Z")
BAD_DIAGNOSTIC = re.compile(
    r"unknown module prefix|object file .*does not exist|failed to import|"
    r"unknown identifier|unknown constant|unknown namespace|"
    r"failed to locate application|stack overflow|out of memory|"
    r"maximum recursion depth|maximum number of heartbeats|unexpected token|"
    r"ambiguous identifier|ambiguous term|multiple interpretations|"
    r"segmentation fault|(?:^|\n)killed(?:\s|$)", re.I)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def relative(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and p.parts and all(x not in ("", ".", "..") for x in p.parts)
            and "\\" not in name and str(p) == name, "Unsafe relative path: " + name)
    return p


def regular(path):
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))


def lean_path(module):
    require(MODULE_RE.fullmatch(module), "Unsupported module name: " + module)
    return module.replace(".", "/") + ".lean"


def strip_comments(text, strings=False):
    """Preserve line breaks while removing nested Lean comments and optional strings."""
    out, i, depth, quoted = [], 0, 0, False
    while i < len(text):
        if depth:
            if text.startswith("/-", i): depth += 1; out.extend("  "); i += 2
            elif text.startswith("-/", i): depth -= 1; out.extend("  "); i += 2
            else: out.append("\n" if text[i] == "\n" else " "); i += 1
        elif quoted:
            if text[i] == "\\" and i + 1 < len(text):
                out.extend("  " if strings else text[i:i + 2]); i += 2
            else:
                c = text[i]; out.append(" " if strings and c != "\n" else c); i += 1
                if c == '"': quoted = False
        elif text.startswith("/-", i): depth = 1; out.extend("  "); i += 2
        elif text.startswith("--", i):
            j = text.find("\n", i)
            if j < 0: j = len(text)
            out.extend(" " * (j - i)); i = j
        elif text[i] == '"':
            quoted = True; out.append(" " if strings else '"'); i += 1
        else: out.append(text[i]); i += 1
    require(depth == 0 and not quoted, "Unterminated Lean comment or string")
    return "".join(out)


def imports(path):
    result = []
    for m in re.finditer(r"^\s*(?:(?:public|private)\s+)?import\s+([^\n]+)",
                         strip_comments(path.read_text()), re.M):
        for name in m[1].split():
            require(MODULE_RE.fullmatch(name), "Unsupported import syntax in " + str(path))
            result.append(name)
    return result


def local_closure(project, roots):
    order, active, seen, external, graph = [], set(), set(), set(), {}
    def visit(mod):
        if mod in seen: return
        require(mod not in active, "Local import cycle: " + mod)
        path = project / lean_path(mod)
        regular(path)
        active.add(mod)
        graph[mod] = imports(path)
        for dep in graph[mod]:
            if (project / lean_path(dep)).is_file(): visit(dep)
            else: external.add(dep)
        active.remove(mod); seen.add(mod); order.append(mod)
    for mod in roots: visit(mod)
    return order, graph, sorted(external)


def source_screen(path):
    code = strip_comments(path.read_text(), strings=True)
    bad = re.findall(r"\b(?:sorry|admit|axiom|unsafe|native_decide|implemented_by|extern)\b", code)
    require(not bad, "Forbidden active source token(s) in " + str(path) + ": " + str(bad))
    require(not re.search(r"set_option\s+(?:debug\.skipKernelTC|debug\.skipKernel|kernel\.)", code),
            "Forbidden kernel option in " + str(path))


def audit_source(modules):
    names = ", ".join("`" + m for m in modules)
    return "\n".join("import " + m for m in modules) + "\nimport Lean\n\n" + r'''open Lean Elab Command
run_cmd do
  let env ← getEnv
  let modules : Array Name := #[MODULE_NAMES]
  let allowed : Array Name := #[`propext, `Classical.choice, `Quot.sound]
  let mut count : Nat := 0
  for (name, ci) in env.constants.toList do
    let some idx := env.getModuleIdxFor? name | continue
    let mod := env.allImportedModuleNames[idx.toNat]!
    if modules.contains mod then
      let axioms ← collectAxioms name
      if ci.isUnsafe || ci.isPartial then
        throwError "AUDIT_UNSAFE_OR_PARTIAL {name}"
      for ax in axioms do
        unless allowed.contains ax do
          throwError "AUDIT_FORBIDDEN_AXIOM {name}: {ax}"
      let row := Json.mkObj [
        ("name", Json.str name.toString),
        ("module", Json.str mod.toString),
        ("is_theorem", Json.bool ci.isTheorem),
        ("axioms", Json.arr (axioms.map fun n => Json.str n.toString))]
      logInfo m!"AUDIT_JSON|{row.compress}"
      count := count + 1
  logInfo m!"AUDIT_COUNT|{count}"
'''.replace("MODULE_NAMES", names)


def parse_audit(text, modules):
    rows = [json.loads(line.split("AUDIT_JSON|", 1)[1]) for line in text.splitlines()
            if "AUDIT_JSON|" in line]
    counts = re.findall(r"AUDIT_COUNT\|(\d+)", text)
    require(len(counts) == 1 and int(counts[0]) == len(rows) and rows,
            "Incomplete declaration audit output")
    require(len({r["name"] for r in rows}) == len(rows), "Duplicate audit declaration")
    require({r["module"] for r in rows} == set(modules), "Audit module coverage differs")
    require(all(set(r["axioms"]) <= ALLOWED_AXIOMS for r in rows), "Forbidden audited axiom")
    return sorted(rows, key=lambda r: r["name"])


def runtime_inventory(kit, manifest, destination):
    started = utc(); records = []; excluded = []; mismatches = []
    for entry in manifest["files"]:
        rel = str(relative(entry["path"])); path = kit / rel
        if re.fullmatch(r"workspace/\.lake/packages/[^/]+/\.git/index", rel):
            regular(path)
            excluded.append({"path": rel, "expected_sha256": entry["sha256"],
                             "actual_sha256": sha(path), "reason": "Mutable Git index metadata"})
            continue
        if "symlink" in entry:
            actual = {"path": rel, "symlink": os.readlink(path) if path.is_symlink() else None}
            if actual["symlink"] != entry["symlink"]: mismatches.append(actual)
        else:
            regular(path); before = path.stat()
            actual = {"path": rel, "bytes": before.st_size, "sha256": sha(path)}
            after = path.stat()
            require((before.st_size, before.st_mtime_ns, before.st_ino) ==
                    (after.st_size, after.st_mtime_ns, after.st_ino), "Runtime changed during hash: " + rel)
            if actual["bytes"] != entry["bytes"] or actual["sha256"] != entry["sha256"]:
                mismatches.append(actual)
        records.append(actual)
    write(destination, {"schema": "komorebi.physics.runtime-endpoint.v1", "started_utc": started,
        "finished_utc": utc(), "records": records, "excluded_metadata": excluded,
        "mismatches": mismatches, "scope": "Declared runtime files, excluding mutable dependency Git indexes."})
    require(not mismatches, "Declared compiler/source/cache runtime mismatch; see " + str(destination))
    return records


def external_cache_paths(kit, packages, manifest, required_modules):
    """Use existing search directories and prove all direct imports resolve there.

    A pinned package may be source-only and unused by these targets. Its absent
    build directory is recorded, never fabricated. Actual transitive imports are
    subsequently checked by the fresh Lean compilations.
    """
    directories, missing, paths = [], [], []
    for item in packages:
        require(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", item["name"]), "Unsafe dependency name")
        path = kit / "workspace/.lake/packages" / item["name"] / ".lake/build/lib/lean"
        row = {"dependency": item["name"], "path": str(path), "present": path.is_dir()}
        directories.append(row)
        if path.is_dir(): paths.append(path)
        else: missing.append(row)
    toolchain = kit / "toolchain/lib/lean"
    require(toolchain.is_dir(), "Toolchain proof library missing")
    paths.append(toolchain)
    declared = {row["path"]: row for row in manifest["files"]}
    resolutions = []
    for module in sorted(set(required_modules)):
        object_name = lean_path(module)[:-5] + ".olean"
        candidates = [path / object_name for path in paths if (path / object_name).is_file()]
        require(candidates, "Direct external import has no pinned cached object: " + module)
        path = candidates[0]
        regular(path)
        rel = path.relative_to(kit).as_posix()
        expected = declared.get(rel)
        require(expected is not None and "sha256" in expected,
                "Direct external import is outside the pinned runtime manifest: " + module)
        digest = sha(path)
        require(digest == expected["sha256"] and path.stat().st_size == expected["bytes"],
                "Direct external cached object differs: " + module)
        resolutions.append({"module": module, "path": rel, "bytes": path.stat().st_size,
                            "sha256": digest, "search_precedence": paths.index(path.parent)
                            if path.parent in paths else next(i for i, root in enumerate(paths)
                                                           if path.is_relative_to(root))})
    return paths, {"dependency_build_directories": directories,
                   "missing_dependency_build_directories": missing,
                   "direct_import_resolutions": resolutions,
                   "scope": "Every direct production, control and auditor external import resolves to an authenticated cached object. Missing unused build directories are not created. Fresh compilation checks transitive imports."}


class Runner:
    def __init__(self, out, env, cwd, timeout):
        self.out, self.env, self.cwd, self.timeout = out, env, cwd, timeout
        self.records = []

    def command(self, label, argv, expected="accept", pattern=None, env=None):
        require(re.fullmatch(r"[A-Za-z0-9_.-]+", label), "Unsafe gate label")
        require(label not in {x["label"] for x in self.records}, "Duplicate gate label")
        log = self.out / "logs" / (label + ".log"); log.parent.mkdir(exist_ok=True)
        started, t = utc(), time.monotonic(); timed_out = False; interrupted = False
        with log.open("x") as f:
            proc = subprocess.Popen(argv, cwd=self.cwd, env=env or self.env, stdout=f,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            try: rc = proc.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True; os.killpg(proc.pid, signal.SIGKILL); proc.wait(); rc = proc.returncode
            except KeyboardInterrupt:
                interrupted = True
                if proc.poll() is None: os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(); rc = proc.returncode
        output = log.read_text(errors="replace")
        if expected == "accept": ok = rc == 0 and not timed_out and not interrupted
        else:
            require(expected in ("elaboration_reject", "policy_reject"), "Unknown expectation")
            ok = rc != 0 and not timed_out and not interrupted and "error" in output.lower() and bool(pattern)
            ok = ok and re.search(pattern, output, re.S) is not None and not BAD_DIAGNOSTIC.search(output)
            if expected == "policy_reject": ok = ok and "AUDIT_FORBIDDEN_AXIOM" in output
        record = {"label": label, "argv": argv, "cwd": str(self.cwd), "expected": expected,
                  "required_diagnostic_regex": pattern, "started_utc": started, "finished_utc": utc(),
                  "seconds": round(time.monotonic() - t, 6), "exit_code": rc, "timeout": timed_out,
                  "interrupted": interrupted,
                  "passed": bool(ok), "log": log.relative_to(self.out).as_posix(), "log_sha256": sha(log)}
        self.records.append(record); write(self.out / "commands.json", self.records)
        print(label + ": " + ("PASS" if ok else "FAIL"), flush=True)
        require(ok, "Failed gate " + label + "; see " + str(log))
        return output


def verify(args):
    project, kit, controls_file, out = args.project.resolve(strict=True), args.runtime.resolve(strict=True), \
        args.controls.resolve(strict=True), args.out_dir.resolve()
    require(not out.exists(), "Refusing existing output directory: " + str(out))
    require(not out.is_relative_to(project) and not out.is_relative_to(kit), "Output must be outside inputs")
    out.mkdir(parents=True)
    receipt = {"schema": "komorebi.physics.centered-gate.v1", "status": "RUNNING", "started_utc": utc()}
    runner = None
    try:
        regular(controls_file)
        controls = json.loads(controls_file.read_text())
        require(controls.get("schema") == "komorebi.physics.centered-controls.v1", "Unknown controls schema")
        cs = controls["controls"]
        require(cs and len({c["id"] for c in cs}) == len(cs), "Empty or duplicate controls")
        require(all(re.fullmatch(r"[A-Za-z0-9_]+", c["id"]) for c in cs), "Unsafe control id")
        require(any(c["kind"] == "positive" for c in cs), "No positive controls")
        require(any(c["kind"] == "elaboration_reject" for c in cs), "No elaboration rejection controls")
        require(any(c["kind"] == "policy_reject" for c in cs), "No axiom-policy control")
        order, graph, external = local_closure(project, ROOT_MODULES)
        snap = out / "snapshot"; obj = out / "objects"; control_obj = out / "control_objects"
        snap.mkdir(); obj.mkdir(); control_obj.mkdir()
        inputs = {}
        def copy(source, name):
            relative(name); regular(source); target = snap / name
            require(not target.exists(), "Snapshot collision: " + name)
            target.parent.mkdir(parents=True, exist_ok=True); before = sha(source); shutil.copy2(source, target)
            require(sha(target) == before == sha(source), "Source changed during snapshot: " + str(source))
            inputs[str(source)] = {"snapshot": name, "sha256": before, "bytes": target.stat().st_size}
        for mod in order:
            path = project / lean_path(mod); source_screen(path); copy(path, lean_path(mod))
        for name in ("lakefile.toml", "lake-manifest.json", "lean-toolchain"):
            copy(project / name, name)
        copy(controls_file, "CONTROL_MANIFEST.json")
        control_modules = set()
        for c in cs:
            require(c["kind"] in ("positive", "elaboration_reject", "policy_reject"), "Unknown control kind")
            name = str(relative(c["path"])); require(name.endswith(".lean"), "Non-Lean control")
            require(name.startswith(("positive_controls/", "negative_controls/")), "Control must be isolated")
            module = name[:-5].replace("/", "."); lean_path(module)
            require(module not in order and module not in control_modules, "Control module collision")
            control_modules.add(module); copy(controls_file.parent / name, name)
            if c["kind"] != "positive":
                require(isinstance(c.get("expected_regex"), str) and c["expected_regex"], "Missing diagnostic contract")
                re.compile(c["expected_regex"])
        copy(Path(__file__).resolve(), "runner/verify_centered.py")
        require(sha(snap / lean_path(ROOT_MODULES[0])) == GENERATOR_SHA, "Preserved generator source differs")
        write(out / "source_inputs.json", inputs); write(out / "import_graph.json", graph)
        manifest_path = kit / "verification/file-manifest.json"; regular(manifest_path)
        require(sha(manifest_path) == RUNTIME_MANIFEST_SHA, "Unexpected runtime manifest")
        runtime_manifest = json.loads(manifest_path.read_text())
        runtime_dir = out / "runtime"; runtime_dir.mkdir()
        shutil.copy2(manifest_path, runtime_dir / "shipped_manifest.json")
        runtime_before = runtime_inventory(kit, runtime_manifest, runtime_dir / "before.json")
        package_manifest = json.loads((snap / "lake-manifest.json").read_text())
        packages = package_manifest["packages"]
        require({p["name"]: p["rev"] for p in packages}.get("mathlib") == MATHLIB_COMMIT, "Mathlib pin differs")
        package_paths = [kit / "workspace/.lake/packages" / p["name"] for p in packages]
        required_external = set(external) | {"Lean"}
        for c in cs:
            for module in imports(snap / c["path"]):
                if module not in order and module not in control_modules:
                    require(not (project / lean_path(module)).is_file(),
                            "Control imports local module outside the production closure: " + module)
                    required_external.add(module)
        lib_paths, cache_resolution = external_cache_paths(kit, packages, runtime_manifest, required_external)
        write(runtime_dir / "cache_resolution.json", cache_resolution)
        receipt["missing_dependency_build_directories"] = cache_resolution["missing_dependency_build_directories"]
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("LEAN_") or key in ("LAKE_HOME", "LD_PRELOAD"): env.pop(key)
        env["PATH"] = str(kit / "toolchain/bin") + os.pathsep + env.get("PATH", "")
        env["LD_PRELOAD"] = str(kit / "compat/app_path.so")
        env["LEAN_PATH"] = os.pathsep.join(map(str, [obj, *lib_paths]))
        env["LEAN_NUM_THREADS"] = "1"
        receipt["effective_environment"] = {k: env[k] for k in ("PATH", "LD_PRELOAD", "LEAN_PATH", "LEAN_NUM_THREADS")}
        runner = Runner(out, env, snap, args.timeout)
        lean = str(kit / "toolchain/bin/lean"); checker = str(kit / "toolchain/bin/leanchecker")
        version = runner.command("lean_version", [lean, "--version"])
        require(LEAN_COMMIT in version, "Compiler commit differs")
        dependency_revisions = {}
        for item, path in zip(packages, package_paths):
            rev = runner.command("pin_" + item["name"], ["git", "-C", str(path), "rev-parse", "HEAD"]).strip()
            require(rev == item["rev"], "Dependency revision mismatch: " + item["name"])
            dependency_revisions[item["name"]] = rev
        for i, mod in enumerate(order):
            output = obj / (mod.replace(".", "/") + ".olean"); output.parent.mkdir(parents=True, exist_ok=True)
            require(not output.exists(), "Refusing cached local object")
            argv = [lean, "-j1"]
            if mod in ROOT_MODULES: argv.append("-DwarningAsError=true")
            argv += ["-o", str(output), lean_path(mod)]
            runner.command(f"compile_{i:03d}_" + mod.replace(".", "_"), argv)
            regular(output); require(output.stat().st_size > 0, "Empty compiled object")
        production_objects = {p.relative_to(obj).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
                              for p in sorted(obj.rglob("*")) if p.is_file()}
        write(out / "production_objects.json", production_objects)
        audit = snap / "AuditCentered.lean"; audit.write_text(audit_source(ROOT_MODULES))
        audited = parse_audit(runner.command("declaration_axiom_audit",
                            [lean, "-j1", "-DwarningAsError=true", audit.name]), ROOT_MODULES)
        write(out / "declarations.json", audited)
        generated_audits = {audit.relative_to(snap).as_posix(): sha(audit)}
        for mod in ROOT_MODULES:
            runner.command("kernel_" + mod.split(".")[-1], [checker, "-v", mod])
        counts = {"positive": 0, "elaboration_reject": 0, "policy_reject": 0}
        for c in cs:
            label = "control_" + c["id"]; kind = c["kind"]; counts[kind] += 1
            if kind == "policy_reject":
                module = c["path"][:-5].replace("/", ".")
                output = control_obj / (module.replace(".", "/") + ".olean")
                output.parent.mkdir(parents=True, exist_ok=True)
                runner.command(label + "_compile", [lean, "-j1", "-DwarningAsError=true", "-o", str(output), c["path"]])
                audit_file = snap / ("PolicyAudit_" + c["id"] + ".lean")
                audit_file.write_text(audit_source([module]))
                generated_audits[audit_file.relative_to(snap).as_posix()] = sha(audit_file)
                ctrl_env = env | {"LEAN_PATH": str(control_obj) + os.pathsep + env["LEAN_PATH"]}
                runner.command(label + "_audit", [lean, "-j1", "-DwarningAsError=true", audit_file.name],
                               "policy_reject", c["expected_regex"], ctrl_env)
            else:
                runner.command(label, [lean, "-j1", "-DwarningAsError=true", c["path"]],
                               "accept" if kind == "positive" else "elaboration_reject", c.get("expected_regex"))
        control_objects = {p.relative_to(control_obj).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
                           for p in sorted(control_obj.rglob("*")) if p.is_file()}
        write(out / "control_objects.json", control_objects)
        runtime_after = runtime_inventory(kit, runtime_manifest, runtime_dir / "after.json")
        require(runtime_before == runtime_after, "Relevant runtime endpoints differ")
        for original, record in inputs.items():
            require(sha(Path(original)) == record["sha256"] == sha(snap / record["snapshot"]),
                    "Source input changed during verification: " + original)
        objects_after = {p.relative_to(obj).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
                         for p in sorted(obj.rglob("*")) if p.is_file()}
        require(objects_after == production_objects, "Production objects changed after compilation")
        for name, digest in generated_audits.items():
            require(sha(snap / name) == digest, "Generated auditor changed during verification")
        for command in runner.records:
            require(sha(out / command["log"]) == command["log_sha256"], "Command log changed")
        receipt.update({"status": "PASS_SCOPED_CENTERED_EXTENSION", "finished_utc": utc(),
            "root_modules": ROOT_MODULES, "new_modules": NEW_MODULES, "compile_order": order,
            "local_targets": len(order), "direct_external_imports": external,
            "source_input_count": len(inputs), "source_inputs_sha256": sha(out / "source_inputs.json"),
            "source_sha256": {r["snapshot"]: r["sha256"] for r in inputs.values()},
            "generated_audit_sha256": generated_audits,
            "declarations": len(audited), "new_declarations": sum(r["module"] in NEW_MODULES for r in audited),
            "declarations_sha256": sha(out / "declarations.json"), "control_counts": counts,
            "controls_manifest_sha256": sha(controls_file), "commands": len(runner.records),
            "commands_sha256": sha(out / "commands.json"), "dependency_revisions": dependency_revisions,
            "control_objects_sha256": sha(out / "control_objects.json"),
            "lean_version": version.strip(), "production_objects_sha256": sha(out / "production_objects.json"),
            "runner_sha256": sha(Path(__file__)), "runtime_manifest_sha256": RUNTIME_MANIFEST_SHA,
            "cache_resolution_sha256": sha(runtime_dir / "cache_resolution.json"),
            "runtime_before_sha256": sha(runtime_dir / "before.json"),
            "runtime_after_sha256": sha(runtime_dir / "after.json"),
            "source_unchanged": True, "objects_unchanged": True, "relevant_runtime_unchanged": True,
            "trust_boundary": "Fresh local import closure compiled from exact sources; pinned compiled external dependencies reused. Module leanchecker replay uses the same Lean kernel and imported environment. Mutable dependency Git indexes are excluded from runtime source/cache identity. Not a compiler or Mathlib rebuild, independent kernel, full historical physics certification, finite-grid theorem, interacting physics or cosmological validation."})
        write(out / "receipt.json", receipt); print(json.dumps(receipt, indent=2)); return 0
    except BaseException as error:
        receipt.update({"status": "FAIL", "finished_utc": utc(), "failure": type(error).__name__ + ": " + str(error),
                        "commands_completed": len(runner.records) if runner else 0})
        write(out / "receipt.json", receipt)
        print(json.dumps(receipt, indent=2), file=sys.stderr)
        if isinstance(error, KeyboardInterrupt): return 130
        return 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--controls", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--timeout", type=int, default=600)
    args = p.parse_args()
    require(args.timeout > 0, "Timeout must be positive")
    return verify(args)


if __name__ == "__main__":
    raise SystemExit(main())

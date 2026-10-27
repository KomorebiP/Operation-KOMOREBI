#!/usr/bin/env python3
"""Read-only binding check for the assembled physics continuum publication.

This checks the accepted evidence and copied bytes; it does not run Lean again.
Optional JSON output must be outside the publication tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ACCEPTED_RECEIPT_SHA = "f530e4bb0c55204fe3d7d55c9cf71c60781f5db949541bfc9b3c649241799d11"
BASELINE_SHA = "c754c2c11ba5c347045ccbdd63714946869651538c67094d458222a274f61839"
FROZEN_REVIEW_SHA = "fb302695cd421f2fa0836913bd923621f16dc4cf8c5c8ff37db8e4a6a97d193c"
RUNNER_SHA = "2ae5b2e524b3a7527b4a762bc6914296dc06e90ee11056fba6eaaf6c7a1eaa26"
ROOT_MODULES = ["KomorebiPhysics.Relativistic3DGeneratorBridge",
    "KomorebiPhysics.Relativistic3DCenteredConvergence",
    "KomorebiPhysics.Relativistic3DModalPerturbation",
    "KomorebiPhysics.Relativistic3DCenteredRates",
    "KomorebiPhysics.Relativistic3DCenteredResolvent"]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
BAD_DIAGNOSTIC = re.compile(
    r"unknown module prefix|object file .*does not exist|failed to import|"
    r"unknown identifier|unknown constant|unknown namespace|"
    r"failed to locate application|stack overflow|out of memory|"
    r"maximum recursion depth|maximum number of heartbeats|unexpected token|"
    r"ambiguous identifier|ambiguous term|multiple interpretations|"
    r"segmentation fault|(?:^|\n)killed(?:\s|$)", re.I)


def require(ok, message):
    if not ok: raise RuntimeError(message)


def rel(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and p.parts and all(x not in ("", ".", "..") for x in p.parts)
            and "\\" not in name and str(p) == name, "Unsafe relative path: " + name)
    return p


def regular(path):
    require(path.is_file() and not path.is_symlink(), "Expected regular file: " + str(path))


def sha(path):
    regular(path); h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def read(path, expected=None):
    if expected is not None: require(sha(path) == expected, "Hash mismatch: " + str(path))
    else: regular(path)
    return json.loads(path.read_text())


def bind(path, digest, size=None):
    require(sha(path) == digest, "Hash mismatch: " + str(path))
    if size is not None: require(path.stat().st_size == size, "Byte-size mismatch: " + str(path))


def exact_files(root, entries):
    actual = set()
    for p in root.rglob("*"):
        require(not p.is_symlink(), "Symlink in evidence: " + str(p))
        if p.is_file(): actual.add(p.relative_to(root).as_posix())
    require(actual == set(entries), "Exact evidence file set differs: " + str(root))
    for name, row in entries.items(): bind(root / str(rel(name)), row["sha256"], row["bytes"])


def strip_comments(text):
    out, i, depth, quoted = [], 0, 0, False
    while i < len(text):
        if depth:
            if text.startswith("/-", i): depth += 1; out.extend("  "); i += 2
            elif text.startswith("-/", i): depth -= 1; out.extend("  "); i += 2
            else: out.append("\n" if text[i] == "\n" else " "); i += 1
        elif quoted:
            if text[i] == "\\" and i + 1 < len(text): out.extend(text[i:i + 2]); i += 2
            else:
                c = text[i]; out.append(c); i += 1
                if c == '"': quoted = False
        elif text.startswith("/-", i): depth = 1; out.extend("  "); i += 2
        elif text.startswith("--", i):
            j = text.find("\n", i)
            if j < 0: j = len(text)
            out.extend(" " * (j - i)); i = j
        elif text[i] == '"': quoted = True; out.append('"'); i += 1
        else: out.append(text[i]); i += 1
    require(depth == 0 and not quoted, "Unterminated source comment or string")
    return "".join(out)


def imports(path):
    return [name for m in re.finditer(r"^\s*(?:(?:public|private)\s+)?import\s+([^\n]+)",
                                    strip_comments(path.read_text()), re.M) for name in m[1].split()]


def module_path(module):
    require(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*", module),
            "Unsupported module name")
    return module.replace(".", "/") + ".lean"


def validate(formal, gate, baseline_file, frozen_file, receipt_sha=ACCEPTED_RECEIPT_SHA):
    receipt = read(gate / "receipt.json", receipt_sha)
    require(receipt["status"] == "PASS_SCOPED_CENTERED_EXTENSION", "Gate does not pass")
    require(receipt["root_modules"] == ROOT_MODULES and receipt["new_modules"] == ROOT_MODULES[1:],
            "Accepted module scope differs")
    require(receipt["runner_sha256"] == RUNNER_SHA, "Accepted runner differs")
    require(all(receipt[x] is True for x in ("source_unchanged", "objects_unchanged", "relevant_runtime_unchanged")),
            "Gate did not preserve its required inputs")
    inputs = read(gate / "source_inputs.json", receipt["source_inputs_sha256"])
    require(len(inputs) == receipt["source_input_count"], "Source-input count differs")
    paths = [x["snapshot"] for x in inputs.values()]
    require(len(paths) == len(set(paths)), "Duplicate snapshot source path")
    source_map = {r["snapshot"]: r["sha256"] for r in inputs.values()}
    require(source_map == receipt["source_sha256"], "Receipt source map differs")
    original_control = [p for p, row in inputs.items() if row["snapshot"] == "CONTROL_MANIFEST.json"]
    require(len(original_control) == 1, "No unique original project anchor")
    original_project = PurePosixPath(original_control[0]).parent
    snapshot_entries = {}
    relocated = 0
    for original, row in inputs.items():
        name = str(rel(row["snapshot"])); path = gate / "snapshot" / name
        bind(path, row["sha256"], row["bytes"]); snapshot_entries[name] = row
        if name == "runner/verify_centered.py":
            require(row["sha256"] == RUNNER_SHA, "Snapshot runner differs")
        else:
            require(PurePosixPath(original) == original_project / name,
                    "Original project path and snapshot path disagree: " + name)
            bind(formal / name, row["sha256"], row["bytes"]); relocated += 1
    for name, digest in receipt["generated_audit_sha256"].items():
        path = gate / "snapshot" / str(rel(name)); bind(path, digest)
        snapshot_entries[name] = {"bytes": path.stat().st_size, "sha256": digest}
    exact_files(gate / "snapshot", snapshot_entries)

    baseline = read(baseline_file, BASELINE_SHA)
    require(baseline["schema"] == "komorebi.physics.preserved-mathematical-inputs.v1", "Baseline schema differs")
    require(len(baseline["files"]) == 912, "Baseline preservation scope differs")
    for name, digest in baseline["files"].items(): bind(formal / str(rel(name)), digest)
    frozen = read(frozen_file, FROZEN_REVIEW_SHA)
    require(frozen["status"] == "PASS_SEMANTIC_SOURCE_REVIEW", "Frozen source review does not pass")
    require({x["module"] for x in frozen["source_files"]} == set(ROOT_MODULES[1:]), "Frozen modules differ")
    for row in frozen["source_files"]:
        name = str(rel(row["path"])); bind(formal / name, row["sha256"], row["bytes"])
        require(source_map.get(name) == row["sha256"], "Frozen source not bound to gate: " + name)

    controls = read(gate / "snapshot/CONTROL_MANIFEST.json", receipt["controls_manifest_sha256"])
    require(controls["schema"] == "komorebi.physics.centered-controls.v1", "Control schema differs")
    cs = controls["controls"]
    require(len({c["id"] for c in cs}) == len(cs), "Duplicate controls")
    counts = {k: sum(c["kind"] == k for c in cs) for k in ("positive", "elaboration_reject", "policy_reject")}
    require(counts == receipt["control_counts"], "Control counts differ")
    declarations = read(gate / "declarations.json", receipt["declarations_sha256"])
    require(len(declarations) == receipt["declarations"], "Declaration count differs")
    require(len({r["name"] for r in declarations}) == len(declarations), "Duplicate audited declaration")
    require({r["module"] for r in declarations} == set(ROOT_MODULES), "Audited modules differ")
    require(sum(r["module"] in ROOT_MODULES[1:] for r in declarations) == receipt["new_declarations"],
            "New declaration count differs")
    require(all(set(r["axioms"]) <= ALLOWED_AXIOMS for r in declarations), "Forbidden declaration axiom")

    objects = read(gate / "production_objects.json", receipt["production_objects_sha256"])
    exact_files(gate / "objects", objects)
    control_objects = read(gate / "control_objects.json", receipt["control_objects_sha256"])
    exact_files(gate / "control_objects", control_objects)
    order = receipt["compile_order"]
    require(len(order) == receipt["local_targets"] == len(set(order)), "Compilation order differs")
    graph = read(gate / "import_graph.json")
    require(set(graph) == set(order), "Import graph and compile order differ")
    for module in order:
        name = module_path(module)
        require(graph[module] == imports(gate / "snapshot" / name), "Import graph differs from source: " + module)
        require(name[:-5] + ".olean" in objects, "Compiled module object absent: " + module)
        for dependency in graph[module]:
            if dependency in order:
                require(order.index(dependency) < order.index(module), "Local import compiled out of order")

    commands = read(gate / "commands.json", receipt["commands_sha256"])
    require(len(commands) == receipt["commands"], "Command count differs")
    require(len({c["label"] for c in commands}) == len(commands), "Duplicate command label")
    by_label = {c["label"]: c for c in commands}
    package_data = read(gate / "snapshot/lake-manifest.json")
    expected_labels = ["lean_version"] + ["pin_" + p["name"] for p in package_data["packages"]]
    expected_labels += [f"compile_{i:03d}_" + m.replace(".", "_") for i, m in enumerate(order)]
    expected_labels += ["declaration_axiom_audit"] + ["kernel_" + m.split(".")[-1] for m in ROOT_MODULES]
    for c in cs:
        expected_labels += (["control_" + c["id"] + "_compile", "control_" + c["id"] + "_audit"]
                            if c["kind"] == "policy_reject" else ["control_" + c["id"]])
    require([c["label"] for c in commands] == expected_labels, "Exact command order differs")
    log_entries = {}
    for c in commands:
        require(c["passed"] is True and c["timeout"] is False and c.get("interrupted") is False,
                "Unaccepted command in passing receipt")
        name = str(rel(c["log"])); path = gate / name; bind(path, c["log_sha256"])
        require(name.startswith("logs/"), "Command log outside log tree")
        log_entries[name[5:]] = {"bytes": path.stat().st_size, "sha256": c["log_sha256"]}
        output = path.read_text(errors="strict")
        if c["expected"] == "accept": require(c["exit_code"] == 0, "Accepted command exit differs")
        else:
            require(c["expected"] in ("elaboration_reject", "policy_reject"), "Unknown command expectation")
            require(c["exit_code"] != 0 and "error" in output.lower(), "Rejected command lacks error")
            require(c["required_diagnostic_regex"] and re.search(c["required_diagnostic_regex"], output, re.S),
                    "Required rejection diagnostic absent")
            require(not BAD_DIAGNOSTIC.search(output), "Rejected command has a disqualifying diagnostic")
            if c["expected"] == "policy_reject":
                require("AUDIT_FORBIDDEN_AXIOM" in output, "Policy rejection has no forbidden axiom")
    exact_files(gate / "logs", log_entries)
    old_snapshot = PurePosixPath(by_label["declaration_axiom_audit"]["cwd"])
    old_gate = old_snapshot.parent
    lean = by_label["lean_version"]["argv"][0]
    for i, module in enumerate(order):
        c = by_label[f"compile_{i:03d}_" + module.replace(".", "_")]
        argv = [lean, "-j1"] + (["-DwarningAsError=true"] if module in ROOT_MODULES else [])
        argv += ["-o", str(old_gate / "objects" / (module.replace(".", "/") + ".olean")), module_path(module)]
        require(c["argv"] == argv and c["cwd"] == str(old_snapshot), "Source/object compile binding differs")
    for module in ROOT_MODULES:
        c = by_label["kernel_" + module.split(".")[-1]]
        require(PurePosixPath(c["argv"][0]).name == "leanchecker" and c["argv"][1:] == ["-v", module],
                "Kernel replay target differs")
    for c in cs:
        if c["kind"] == "policy_reject":
            compile_row = by_label["control_" + c["id"] + "_compile"]
            module = c["path"][:-5].replace("/", ".")
            require(compile_row["argv"] == [lean, "-j1", "-DwarningAsError=true", "-o",
                    str(old_gate / "control_objects" / (module.replace(".", "/") + ".olean")), c["path"]],
                    "Policy compilation binding differs")
            row = by_label["control_" + c["id"] + "_audit"]
            require(row["argv"] == [lean, "-j1", "-DwarningAsError=true", "PolicyAudit_" + c["id"] + ".lean"],
                    "Policy auditor command differs")
        else:
            row = by_label["control_" + c["id"]]
            require(row["argv"] == [lean, "-j1", "-DwarningAsError=true", c["path"]], "Control source binding differs")
        expected = "accept" if c["kind"] == "positive" else c["kind"]
        require(row["expected"] == expected and row["required_diagnostic_regex"] == c.get("expected_regex"),
                "Control manifest and executed contract differ")
    audit_log = (gate / by_label["declaration_axiom_audit"]["log"]).read_text()
    logged = [json.loads(x.split("AUDIT_JSON|", 1)[1]) for x in audit_log.splitlines() if "AUDIT_JSON|" in x]
    require(sorted(logged, key=lambda r: r["name"]) == declarations, "Declaration inventory differs from raw audit")
    require(re.findall(r"AUDIT_COUNT\|(\d+)", audit_log) == [str(len(declarations))], "Raw audit count differs")

    runtime = gate / "runtime"
    shipped = read(runtime / "shipped_manifest.json", receipt["runtime_manifest_sha256"])
    before = read(runtime / "before.json", receipt["runtime_before_sha256"])
    after = read(runtime / "after.json", receipt["runtime_after_sha256"])
    require(not before["mismatches"] and not after["mismatches"], "Runtime mismatch recorded")
    require(before["records"] == after["records"], "Declared runtime endpoints differ")
    expected_runtime, excluded = [], set()
    for row in shipped["files"]:
        if re.fullmatch(r"workspace/\.lake/packages/[^/]+/\.git/index", row["path"]): excluded.add(row["path"])
        else: expected_runtime.append(row)
    require(before["records"] == expected_runtime, "Runtime endpoint differs from shipped non-index rows")
    require(len(excluded) == 9, "Runtime exclusion boundary differs")
    require({x["path"] for x in before["excluded_metadata"]} == excluded ==
            {x["path"] for x in after["excluded_metadata"]}, "Runtime metadata exclusions differ")
    cache = read(runtime / "cache_resolution.json", receipt["cache_resolution_sha256"])
    require(cache["missing_dependency_build_directories"] == receipt["missing_dependency_build_directories"],
            "Missing cache directory record differs")
    require([x["dependency"] for x in cache["missing_dependency_build_directories"]] == ["Cli"],
            "Unexpected omitted dependency cache")
    runtime_map = {r["path"]: r for r in expected_runtime}
    for row in cache["direct_import_resolutions"]:
        target = runtime_map.get(row["path"])
        require(target and target.get("sha256") == row["sha256"] and target.get("bytes") == row["bytes"],
                "Direct cached import is not bound to runtime evidence")
    required_external = {"Lean"}
    for deps in graph.values(): required_external.update(m for m in deps if m not in graph)
    for c in cs: required_external.update(m for m in imports(gate / "snapshot" / c["path"]) if m not in graph)
    require({x["module"] for x in cache["direct_import_resolutions"]} == required_external,
            "Direct import resolution coverage differs")
    expected_pins = {x["name"]: x["rev"] for x in package_data["packages"]}
    require(receipt["dependency_revisions"] == expected_pins and len(expected_pins) == 9, "Dependency pins differ")
    for name, pin in expected_pins.items():
        require((gate / by_label["pin_" + name]["log"]).read_text().strip() == pin, "Raw dependency pin differs")
    return {"schema": "komorebi.physics.publication-source-binding.v1", "status": "PASS_SOURCE_EVIDENCE_BINDING",
        "accepted_gate_receipt_sha256": receipt_sha, "baseline_record_sha256": BASELINE_SHA,
        "frozen_source_review_sha256": FROZEN_REVIEW_SHA, "runner_sha256": RUNNER_SHA,
        "preserved_mathematical_files": len(baseline["files"]), "frozen_new_modules": len(frozen["source_files"]),
        "snapshot_source_inputs": len(inputs), "relocated_project_inputs": relocated,
        "fresh_compiled_targets": len(order), "compiled_object_files": len(objects),
        "audited_environment_constants": len(declarations), "new_environment_constants": receipt["new_declarations"],
        "commands_bound": len(commands), "controls_reclassified": len(cs), "control_counts": counts,
        "runtime_nonindex_rows_bound": len(expected_runtime), "runtime_git_indexes_explicitly_excluded": len(excluded),
        "direct_external_imports_bound": len(required_external), "dependency_pins_bound": len(expected_pins),
        "scope": "Read-only copied-source and accepted evidence binding. No new Lean execution or live runtime rehash; no empirical physics validation."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--formal", default="formal/continuum", help="Relative to publication root")
    p.add_argument("--gate", default="verification/block51/current", help="Relative to formal root")
    p.add_argument("--baseline", default="verification/block51/BASELINE_MATHEMATICAL_INPUTS.json", help="Relative to formal root")
    p.add_argument("--frozen", default="verification/block51/FROZEN_SOURCE_REVIEW.json", help="Relative to formal root")
    p.add_argument("--output", type=Path, help="Optional new JSON file outside publication root")
    args = p.parse_args(); root = args.root.resolve(strict=True)
    formal = root / str(rel(args.formal)); gate = formal / str(rel(args.gate))
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(root) and not output.exists(), "Output must be new and outside publication")
    try:
        result = validate(formal, gate, formal / str(rel(args.baseline)), formal / str(rel(args.frozen)))
        result["validator_sha256"] = sha(Path(__file__).resolve())
        code = 0
    except Exception as error:
        result = {"status": "FAIL_SOURCE_EVIDENCE_BINDING", "failure": type(error).__name__ + ": " + str(error)}
        code = 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x") as f: f.write(text)
    print(text, end=""); return code


if __name__ == "__main__": raise SystemExit(main())

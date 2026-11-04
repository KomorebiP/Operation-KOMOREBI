#!/usr/bin/env python3
"""Replay one pinned Lean companion in an isolated, fresh build directory.

Dependencies must already be available through the portable runtime or the
project's .lake/packages directory. This command never updates dependencies.
Each run keeps its diagnostics, exact source hashes, and checked axiom lists.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
LEAN_COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"
MATHLIB_COMMIT = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
FORBIDDEN_DIAGNOSTICS = (
    "unknown identifier", "unknown constant", "unknown module prefix", "object file",
    "failed to synthesize", "unexpected token", "no such file",
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_child(root, relative):
    child = (root / relative).resolve()
    if not child.is_relative_to(root) or not child.is_file():
        raise ValueError("Missing or escaping companion file: " + relative)
    return child


def inventory_names(config):
    names = [row["name"] for row in config["declarations"]]
    if not names or len(names) != len(set(names)):
        raise ValueError("Declaration inventory must be nonempty and unique")
    return names


def lean_code(text):
    """Remove nested comments and quoted strings while retaining line breaks."""
    output, index, depth = [], 0, 0
    while index < len(text):
        pair = text[index:index + 2]
        if depth:
            if pair == "/-":
                depth += 1
                index += 2
            elif pair == "-/":
                depth -= 1
                index += 2
            else:
                output.append("\n" if text[index] == "\n" else " ")
                index += 1
        elif pair == "/-":
            depth = 1
            output.append(" ")
            index += 2
        elif pair == "--":
            while index < len(text) and text[index] != "\n":
                index += 1
        elif text[index] == '"':
            output.append(" ")
            index += 1
            while index < len(text) and text[index] != '"':
                if text[index] == "\\":
                    index += 2
                else:
                    output.append("\n" if text[index] == "\n" else " ")
                    index += 1
            index += 1
        else:
            output.append(text[index])
            index += 1
    if depth:
        raise ValueError("Unclosed Lean comment")
    return "".join(output)


def explicit_declarations(project, relative):
    text = lean_code(safe_child(project, relative).read_text())
    if re.search(r"\b(?:sorry|admit|sorryAx|native_decide|axiom|unsafe|private|opaque)\b", text):
        raise ValueError("Disallowed admission, axiom, or unaudited declaration form: " + relative)
    if re.search(r"(?m)^\s*(?:example|instance|macro|syntax|elab|run_cmd|initialize|mutual)\b|^\s*#", text):
        raise ValueError("Unsupported declaration or command in audited source: " + relative)
    namespaces = re.findall(r"(?m)^namespace\s+(\S+)\s*$", text)
    declarations = re.findall(
        r"(?m)^(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|protected)\s+)?"
        r"(def|theorem|lemma|abbrev)\s+([A-Za-z_][A-Za-z_0-9'.]*)", text)
    if declarations and len(namespaces) != 1:
        raise ValueError("Expected one fully qualified module namespace: " + relative)
    return [{"name": namespaces[0] + "." + name, "kind": kind, "source": relative}
            for kind, name in declarations]


def source_inventory(project, config):
    """Check every explicit production declaration against the reviewed list.

    These companions deliberately use one full namespace per module and only
    top-level def/theorem/lemma declarations, with no namespace abbreviations.
    Compiler output, rather than this parser, decides proof acceptance.
    """
    found = {}
    for relative in config["production"]:
        for row in explicit_declarations(project, relative):
            full = row["name"]
            if full in found:
                raise ValueError("Duplicate source declaration: " + full)
            found[full] = {"kind": row["kind"], "source": relative}
    expected = {row["name"]: {"kind": row["kind"], "source": row["source"]}
                for row in config["declarations"]}
    if found != expected:
        raise ValueError("Production declaration inventory differs from source: "
                         + repr({"missing": sorted(set(found) - set(expected)),
                                 "extra": sorted(set(expected) - set(found)),
                                 "metadata": [n for n in set(found) & set(expected)
                                              if found[n] != expected[n]]}))
    root_path = config["library"] + ".lean"
    root_lines = [line.strip() for line in lean_code(safe_child(project, root_path).read_text()).splitlines()
                  if line.strip()]
    expected_imports = {"import " + p.removesuffix(".lean").replace("/", ".")
                        for p in config["production"] if p != root_path}
    if set(root_lines) != expected_imports or len(root_lines) != len(expected_imports):
        raise ValueError("Root must import exactly the inventoried production modules and contain no declarations")


def diagnostics_match(text, required=None, forbidden=(), expected_errors=None):
    return ((required is None or required.lower() in text.lower())
            and not any(item.lower() in text.lower() for item in forbidden)
            and (expected_errors is None
                 or len(re.findall(r"(?m)^.*:\d+:\d+: error(?:\([^\n)]*\))?:", text)) == expected_errors))


def parse_axioms(text):
    pattern = r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)"
    return [{"name": match[1],
             "axioms": [a.strip() for a in (match[2] or "").split(",") if a.strip()]}
            for match in re.finditer(pattern, text)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    project, output = args.project.resolve(), args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Use a new or empty evidence directory")
    output.mkdir(parents=True, exist_ok=True)
    config = json.loads((project / "verification.json").read_text())
    report = {"schema": 1, "status": "RUNNING", "started_utc": now(),
              "project": config["library"], "scope": config["scope"], "checks": []}
    env = os.environ.copy()
    for key in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME", "LD_PRELOAD"):
        env.pop(key, None)
    env["LEAN_NUM_THREADS"] = "1"
    runtime = args.runtime.resolve() if args.runtime else None
    if runtime:
        env["PATH"] = str(runtime / "toolchain/bin") + os.pathsep + env.get("PATH", "")

    def save():
        (output / "run.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(name, command, cwd, expected=0, required=None, forbidden=(), expected_errors=None):
        start = time.monotonic()
        try:
            process = subprocess.run(command, cwd=cwd, env=env, text=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     timeout=args.timeout)
            text, code = process.stdout, process.returncode
        except subprocess.TimeoutExpired as error:
            text = error.stdout or ""
            if isinstance(text, bytes):
                text = text.decode(errors="replace")
            (output / (name + ".log")).write_text(text)
            report["checks"].append({"name": name, "passed": False, "timeout": args.timeout})
            save()
            raise RuntimeError(name + " timed out") from error
        log = output / (name + ".log")
        log.write_text(text)
        passed = code == expected and diagnostics_match(text, required, forbidden, expected_errors)
        report["checks"].append({"name": name, "command": command,
                                 "exit_code": code, "expected_exit_code": expected,
                                 "passed": passed, "seconds": time.monotonic() - start,
                                 "log": log.name, "log_sha256": sha256(log)})
        save()
        print(("PASS " if passed else "FAIL ") + name, flush=True)
        if not passed:
            raise RuntimeError(name + ": inspect " + str(log))
        return text

    save()
    try:
        source_inventory(project, config)
        names = inventory_names(config)
        support_sources = config.get("support_sources", [])
        support_declarations = []
        if support_sources:
            bindings = json.loads((project / "CLAIM_MAP.json").read_text())["reused_prerequisites"]
            if (len(bindings) != len(support_sources)
                    or {row["copy"] for row in bindings} != set(support_sources)):
                raise ValueError("Retained prerequisite bindings differ from selected sources")
            for binding in bindings:
                if sha256(safe_child(project, binding["copy"])) != binding["sha256"]:
                    raise ValueError("Retained prerequisite bytes changed: " + binding["copy"])
                support_declarations.extend(explicit_declarations(project, binding["copy"]))
            report["retained_prerequisites"] = bindings
        source_paths = sorted({"lakefile.toml", "lake-manifest.json", "lean-toolchain",
                               "verification.json", "CLAIM_MAP.json", config["library"] + ".lean",
                               *config["production"],
                               *support_sources,
                               *[row["path"] for row in config["positive_controls"]],
                               *[row["path"] for row in config["negative_controls"]]})
        report["source_sha256"] = {p: sha256(safe_child(project, p)) for p in source_paths}
        report["verifier_sha256"] = sha256(Path(__file__))
        report["source_identity_note"] = "Hashes bind the exact checked inputs; no inference from a file count."
        with tempfile.TemporaryDirectory(prefix="komorebi-lean-") as directory:
            work = Path(directory) / "project"
            work.mkdir()
            for relative in source_paths:
                target = work / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(project / relative, target)
            report["compiler"] = run("compiler", ["lean", "--version"], work,
                                     required=LEAN_COMMIT).strip()
            if "4.34.0-rc2" not in report["compiler"]:
                raise RuntimeError("Unexpected Lean toolchain")
            run("lake", ["lake", "--version"], work, required="4.34.0-rc2")
            manifest = json.loads((work / "lake-manifest.json").read_text())
            dependencies = manifest["packages"]
            mathlib = next(row for row in dependencies if row["name"] == "mathlib")
            if mathlib["rev"] != MATHLIB_COMMIT:
                raise RuntimeError("Unexpected Mathlib pin")
            package_root = (runtime / "workspace/.lake/packages" if runtime
                            else project / ".lake/packages")
            if runtime and ((work / "lean-toolchain").read_bytes()
                            != (runtime / "workspace/lean-toolchain").read_bytes()):
                raise RuntimeError("Portable toolchain pin differs from the project")
            report["dependencies"] = []
            for dependency in dependencies:
                folder = package_root / dependency["name"]
                head = run("pin_" + dependency["name"],
                           ["git", "rev-parse", "HEAD"], folder).strip()
                tracked = run("clean_" + dependency["name"],
                              ["git", "status", "--porcelain", "--untracked-files=no"], folder)
                if head != dependency["rev"] or tracked.strip():
                    raise RuntimeError("Dirty or mismatched dependency: " + dependency["name"])
                report["dependencies"].append({"name": dependency["name"], "revision": head,
                                               "tracked_clean": True})
            (work / ".lake").mkdir()
            (work / ".lake/packages").symlink_to(package_root, target_is_directory=True)
            run("strict_build", ["lake", "build"], work,
                forbidden=("declaration uses `sorry`", "warning:"))
            audit = "import " + config["library"] + "\n\n"
            audit += "".join("#print axioms " + name + "\n" for name in names)
            (work / "AxiomAudit.lean").write_text(audit)
            text = run("production_axioms", ["lake", "env", "lean", "-j1",
                       "-DwarningAsError=true", "AxiomAudit.lean"], work)
            rows = parse_axioms(text)
            if len(rows) != len(names) or {row["name"] for row in rows} != set(names):
                raise RuntimeError("Compiler axiom inventory differs from exact source inventory")
            if any(set(row["axioms"]) - ALLOWED_AXIOMS for row in rows):
                raise RuntimeError("Unapproved axiom dependency")
            report["axioms"] = rows
            if support_declarations:
                support_names = [row["name"] for row in support_declarations]
                if len(set(support_names)) != len(support_names) or set(support_names) & set(names):
                    raise RuntimeError("Duplicate retained prerequisite declaration")
                audit = "import " + config["library"] + "\n"
                audit += "".join("#print axioms " + name + "\n" for name in support_names)
                (work / "PrerequisiteAxiomAudit.lean").write_text(audit)
                text = run("retained_prerequisite_axioms", ["lake", "env", "lean", "-j1",
                           "-DwarningAsError=true", "PrerequisiteAxiomAudit.lean"], work)
                support_rows = parse_axioms(text)
                if (len(support_rows) != len(support_names)
                        or {row["name"] for row in support_rows} != set(support_names)
                        or any(set(row["axioms"]) - ALLOWED_AXIOMS for row in support_rows)):
                    raise RuntimeError("Retained prerequisite axiom audit failed")
                report["retained_prerequisite_axioms"] = support_rows
            run("project_kernel_replay", ["lake", "env", "leanchecker", "--verbose",
                                           config["library"]], work)
            control_declarations = []
            control_imports = []
            for control in config["positive_controls"]:
                declarations = explicit_declarations(project, control["path"])
                if not declarations:
                    raise RuntimeError("Positive control has no named declarations: " + control["path"])
                control_declarations.extend(declarations)
                control_imports.append(control["path"].removesuffix(".lean").replace("/", "."))
                compiled = work / ".lake/build/lib/lean" / Path(control["path"]).with_suffix(".olean")
                compiled.parent.mkdir(parents=True, exist_ok=True)
                run(Path(control["path"]).stem, ["lake", "env", "lean", "-j1",
                    "-DwarningAsError=true", "-o", str(compiled), control["path"]], work,
                    forbidden=("declaration uses `sorry`", "warning:"))
            control_names = [row["name"] for row in control_declarations]
            if len(set(control_names)) != len(control_names):
                raise RuntimeError("Duplicate positive-control declaration")
            audit = "".join("import " + name + "\n" for name in control_imports)
            audit += "".join("#print axioms " + name + "\n" for name in control_names)
            (work / "ControlAxiomAudit.lean").write_text(audit)
            text = run("positive_control_axioms", ["lake", "env", "lean", "-j1",
                       "-DwarningAsError=true", "ControlAxiomAudit.lean"], work)
            control_rows = parse_axioms(text)
            if (len(control_rows) != len(control_names)
                    or {row["name"] for row in control_rows} != set(control_names)
                    or any(set(row["axioms"]) - ALLOWED_AXIOMS for row in control_rows)):
                raise RuntimeError("Positive-control axiom audit failed")
            report["positive_control_axioms"] = control_rows
            for control in config["negative_controls"]:
                run(Path(control["path"]).stem, ["lake", "env", "lean", "-j1",
                    "-DwarningAsError=true", control["path"]], work, expected=1,
                    required=control["diagnostic"], forbidden=FORBIDDEN_DIAGNOSTICS,
                    expected_errors=1)
            for relative, digest in report["source_sha256"].items():
                if sha256(work / relative) != digest or sha256(project / relative) != digest:
                    raise RuntimeError("Source changed during replay: " + relative)
            report.update(status="PASS", finished_utc=now(),
                          theorem_count=sum(row["kind"] in ("theorem", "lemma")
                                            for row in config["declarations"]),
                          audited_declarations=len(names),
                          axiom_union=sorted({a for row in rows for a in row["axioms"]}),
                          negative_controls_rejected=len(config["negative_controls"]),
                          kernel_scope="Fresh project modules replayed using the same Lean kernel against pinned imported environments. This is not an independent kernel or a rebuild of all Mathlib.")
    except Exception as error:
        report.update(status="FAIL", finished_utc=now(), error=str(error))
        print("FAILED: " + str(error), flush=True)
    finally:
        save()
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

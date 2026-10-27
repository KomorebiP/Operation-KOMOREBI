#!/usr/bin/env python3
"""Freshly compile immutable Paper XI sources with bounded parallel processes.

Run from any directory after bootstrapping the pinned dependencies. Every run
requires a new output directory. Selected sources and additions are counted
separately, and a failed addition does not prevent independent selected sources
from being checked. By default no Paper XI object is reused. An explicit resume
authenticates source and artifact hashes from an earlier replay receipt.
The optional terminal-revision mode permits only an explicitly fingerprinted
change to a failed terminal; every successful source and object stays fixed.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LEAN_VERSION = "4.34.0-rc2"
LEAN_COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"
MATHLIB_COMMIT = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
TERMINAL_MODULE = "PaperXI.ActualMonomialLocalGlobal"
INTERFACE_MODULE = "PaperXI.SingleCandidateComparison"
TERMINAL_SOURCE = "PaperXI/ActualMonomialLocalGlobal.lean"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path: Path, value: object) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temp.replace(path)


def without_comments(source: str) -> str:
    """Remove nested Lean comments, preserving strings, offsets and newlines."""
    result = []
    i = depth = 0
    string = False
    while i < len(source):
        if depth:
            if source.startswith("/-", i):
                depth += 1; result.extend("  "); i += 2
            elif source.startswith("-/", i):
                depth -= 1; result.extend("  "); i += 2
            else:
                result.append("\n" if source[i] == "\n" else " "); i += 1
        elif string:
            result.append(source[i])
            if source[i] == "\\" and i + 1 < len(source):
                i += 1; result.append(source[i])
            elif source[i] == '"':
                string = False
            i += 1
        elif source.startswith("/-", i):
            depth = 1; result.extend("  "); i += 2
        elif source.startswith("--", i):
            while i < len(source) and source[i] != "\n":
                result.append(" "); i += 1
        else:
            if source[i] == '"':
                string = True
            result.append(source[i]); i += 1
    if depth:
        raise ValueError("Unclosed Lean block comment")
    return "".join(result)


def imports(path: Path) -> list[str]:
    stripped = without_comments(path.read_text())
    result = []
    for line in stripped.splitlines():
        match = re.match(r"^\s*(?:(?:public|private|meta)\s+)*import\s+(.+)$", line)
        if match:
            result.extend(match.group(1).split())
    return result


def _relative_file(root: Path, relative: str) -> Path:
    """Accept a canonical, nonsymlinked project-relative file path."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise RuntimeError("Resume contains an invalid relative path")
    part = Path(relative)
    if part.is_absolute() or part.as_posix() != relative or any(
            item in {".", ".."} for item in part.parts):
        raise RuntimeError(f"Resume contains an unsafe relative path: {relative}")
    path = root / part
    if path.resolve() != path or not path.is_file():
        raise RuntimeError(f"Resume file missing, noncanonical or symlinked: {relative}")
    return path


def _read_receipt(path: Path) -> tuple[dict, str]:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError(f"Duplicate JSON key in resume evidence: {key}")
            result[key] = value
        return result
    data = path.read_bytes()
    result = json.loads(data, object_pairs_hook=unique)
    if not isinstance(result, dict):
        raise RuntimeError("Resume evidence is not a JSON object")
    return result, hashlib.sha256(data).hexdigest()


def _module_rows(receipt: dict, groups: dict[str, str]) -> dict[str, dict]:
    rows = receipt.get("modules")
    if not isinstance(rows, list):
        raise RuntimeError("Resume module result list missing")
    by_name = {row.get("module"): row for row in rows}
    if len(by_name) != len(rows) or set(by_name) != set(groups):
        raise RuntimeError("Resume module population is missing, duplicated or changed")
    for name, row in by_name.items():
        if row.get("group") != groups[name]:
            raise RuntimeError(f"Resume module group mismatch: {name}")
    return by_name


def _source_transition(previous: dict, current_hashes: dict[str, str],
                       revision: dict | None, groups: dict[str, str]) -> dict | None:
    old = previous.get("source_hashes_after")
    if not isinstance(old, dict) or set(old) != set(current_hashes):
        raise RuntimeError("Resume source population changed")
    changed = {path for path in old if old[path] != current_hashes[path]}
    if revision is None:
        if changed:
            raise RuntimeError("Resume source fingerprints changed without an explicit terminal revision")
        return None
    if changed != {TERMINAL_SOURCE}:
        raise RuntimeError("Terminal revision must change exactly the terminal source")
    for key in ["old_sha256", "new_sha256"]:
        if not isinstance(revision.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", revision[key]):
            raise RuntimeError("Terminal revision requires two lowercase SHA-256 fingerprints")
    if (revision.get("module") != TERMINAL_MODULE
            or revision.get("source_path") != TERMINAL_SOURCE
            or revision["old_sha256"] != old[TERMINAL_SOURCE]
            or revision["new_sha256"] != current_hashes[TERMINAL_SOURCE]):
        raise RuntimeError("Terminal revision fingerprints or source identity do not match")
    if (len(groups) != 425 or sum(group == "selected" for group in groups.values()) != 423
            or groups.get(TERMINAL_MODULE) != "terminal"
            or groups.get(INTERFACE_MODULE) != "new_interface"):
        raise RuntimeError("Terminal revision requires the exact 423 + terminal + interface population")
    rows = _module_rows(previous, groups)
    terminal = rows[TERMINAL_MODULE]
    if (previous.get("status") != "PARTIAL_OR_FAIL" or terminal.get("status") != "FAIL"
            or type(terminal.get("exit_code")) is not int or terminal["exit_code"] == 0
            or terminal.get("source_sha256") != revision["old_sha256"]
            or terminal.get("source_path") != TERMINAL_SOURCE
            or terminal.get("source_unchanged") is not True):
        raise RuntimeError("Terminal revision requires a finalized failed terminal at the declared old hash")
    if {name for name, row in rows.items() if row.get("status") == "PASS"} != set(groups) - {TERMINAL_MODULE}:
        raise RuntimeError("Terminal revision requires all 423 selected modules and the interface to have passed")
    return {"module": TERMINAL_MODULE, "source_path": TERMINAL_SOURCE,
            "old_sha256": revision["old_sha256"], "new_sha256": revision["new_sha256"],
            "previous_status": "FAIL", "invalidated_modules": [TERMINAL_MODULE],
            "previous_terminal_artifacts_reused": False,
            "previous_terminal_artifacts": terminal.get("artifacts", {}),
            "requires_fresh_compilation": True}


def authenticate_resume(root: Path, previous: Path, current: dict,
                        groups: dict[str, str], dependency_map: dict[str, set[str]],
                        terminal_revision: tuple[str, str] | None = None) -> dict:
    """Read-only authentication plan; no old receipt or object is modified.

    All ancestor receipts are hash-linked to a fresh origin. Old origins that
    predate manifest recording remain explicitly marked as unrecorded; the
    terminal-revision mode requires the immediate predecessor's exact manifest.
    """
    root, previous = root.resolve(), previous.resolve()
    if not previous.is_relative_to(root):
        raise RuntimeError("Resume directory must be inside the project")
    current_hashes = current["source_hashes_before"]
    expected_paths = {str(Path(*name.split(".")).with_suffix(".lean")) for name in groups}
    if set(current_hashes) != expected_paths or set(dependency_map) != set(groups):
        raise RuntimeError("Current resume source/dependency population mismatch")
    for path, fingerprint in current_hashes.items():
        if sha(_relative_file(root, path)) != fingerprint:
            raise RuntimeError(f"Current resume source changed: {path}")
    manifest = _relative_file(root, "lake-manifest.json")
    if sha(manifest) != current.get("lake_manifest_sha256"):
        raise RuntimeError("Current dependency manifest changed")
    revision = None if terminal_revision is None else {
        "module": TERMINAL_MODULE, "source_path": TERMINAL_SOURCE,
        "old_sha256": terminal_revision[0], "new_sha256": terminal_revision[1]}
    nodes, seen = [], set()
    path = _relative_file(root, str((previous / "RESULT.json").relative_to(root)))
    expected_digest = None
    while True:
        if path in seen:
            raise RuntimeError("Resume result lineage contains a cycle")
        seen.add(path)
        record, digest = _read_receipt(path)
        if expected_digest is not None and digest != expected_digest:
            raise RuntimeError("Resume ancestor result fingerprint mismatch")
        if record.get("status") not in {"PASS", "PARTIAL_OR_FAIL"} or not record.get("completed_at"):
            raise RuntimeError("Cannot resume an unfinished or invalid replay")
        if (record.get("all_sources_unchanged") is not True
                or record.get("source_hashes_before") != record.get("source_hashes_after")
                or set(record.get("source_hashes_before", {})) != set(current_hashes)):
            raise RuntimeError("Resume ancestor has changed or unfinalized source hashes")
        for key in ["lean_version", "lean_binary_sha256", "mathlib_commit"]:
            if record.get(key) != current.get(key):
                raise RuntimeError(f"Resume runtime mismatch: {key}")
        recorded_manifest = record.get("lake_manifest_sha256")
        if recorded_manifest is not None and recorded_manifest != current["lake_manifest_sha256"]:
            raise RuntimeError("Resume dependency manifest mismatch")
        if (record.get("runtime_inputs_unchanged", True) is not True
                or record.get("lake_manifest_sha256_after", recorded_manifest) != recorded_manifest
                or record.get("lean_binary_sha256_after", record["lean_binary_sha256"]) != record["lean_binary_sha256"]):
            raise RuntimeError("Resume predecessor runtime or manifest changed during its execution")
        if recorded_manifest is None and (record.get("resume") or (not nodes and revision is not None)):
            raise RuntimeError("Terminal revision or intermediate replay lacks a dependency manifest fingerprint")
        rows = _module_rows(record, groups)
        passed = {name for name, row in rows.items() if row.get("status") == "PASS"}
        graph_path = _relative_file(root, str((path.parent / "DEPENDENCY_GRAPH.json").relative_to(root)))
        graph, graph_digest = _read_receipt(graph_path)
        if record.get("dependency_graph_sha256", graph_digest) != graph_digest or set(graph) != set(groups):
            raise RuntimeError("Resume dependency graph fingerprint or population mismatch")
        artifact_suffixes = {}
        for name in passed:
            row = rows[name]
            source = str(Path(*name.split(".")).with_suffix(".lean"))
            if (type(row.get("exit_code")) is not int or row["exit_code"] != 0 or row.get("source_unchanged") is not True
                    or row.get("source_path") != source
                    or row.get("source_sha256") != record["source_hashes_after"][source]
                    or row["source_sha256"] != current_hashes[source]):
                raise RuntimeError(f"Resume successful source receipt mismatch: {name}")
            if (set(graph[name]) != dependency_map[name]
                    or not dependency_map[name] <= passed
                    or {imp for imp in imports(root / source) if imp in groups} != dependency_map[name]):
                raise RuntimeError(f"Resume successful import/dependency closure mismatch: {name}")
            artifacts = row.get("artifacts")
            base = str((path.parent / "objects" / Path(*name.split("."))).relative_to(root))
            if not isinstance(artifacts, dict) or base + ".olean" not in artifacts:
                raise RuntimeError(f"Resume primary object or artifacts missing: {name}")
            suffixes = {}
            for relative, fingerprint in artifacts.items():
                if not relative.startswith(base + ".") or sha(_relative_file(root, relative)) != fingerprint:
                    raise RuntimeError(f"Resume object path or fingerprint mismatch: {name}")
                suffixes[relative[len(base):]] = fingerprint
            artifact_suffixes[name] = suffixes
        nodes.append({"path": path, "sha256": digest, "record": record, "rows": rows,
                      "passed": passed, "artifacts": artifact_suffixes,
                      "graph_sha256": graph_digest})
        parent = record.get("resume")
        if not parent:
            if record.get("paperxi_objects_reused") is not False or any("resumed_from" in rows[n] for n in passed):
                raise RuntimeError("Resume lineage does not terminate at a fresh recorded origin")
            break
        expected_digest = parent.get("result_sha256")
        if not isinstance(expected_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
            raise RuntimeError("Resume ancestor result hash missing")
        path = _relative_file(root, parent.get("result_path"))
    latest = nodes[0]
    revision_record = _source_transition(latest["record"], current_hashes, revision, groups)
    for child, parent in zip(nodes, nodes[1:]):
        child_record, parent_record = child["record"], parent["record"]
        link = child_record["resume"]
        _source_transition(parent_record, child_record["source_hashes_before"],
                           link.get("terminal_revision"), groups)
        inherited = {name for name in child["passed"] if "resumed_from" in child["rows"][name]}
        if (inherited != parent["passed"]
                or child_record.get("paperxi_objects_reused") != bool(inherited)
                or link.get("authenticated_modules") != len(inherited)
                or link.get("authenticated_selected_modules") != sum(groups[n] == "selected" for n in inherited)
                or link.get("earlier_report_reused_paperxi_objects") != parent_record.get("paperxi_objects_reused")):
            raise RuntimeError("Resume inherited-module population or fresh-origin lineage mismatch")
        for name in inherited:
            row, old = child["rows"][name], parent["rows"][name]
            origin = row["resumed_from"]
            if (origin.get("result_path") != str(parent["path"].relative_to(root))
                    or origin.get("result_sha256") != parent["sha256"]
                    or origin.get("original_artifacts") != old["artifacts"]
                    or child["artifacts"][name] != parent["artifacts"][name]
                    or {k: v for k, v in row.items() if k not in {"artifacts", "resumed_from"}}
                       != {k: v for k, v in old.items() if k not in {"artifacts", "resumed_from"}}):
                raise RuntimeError(f"Resume inherited object/source lineage mismatch: {name}")
    lineage = [{"result_path": str(node["path"].relative_to(root)),
                "result_sha256": node["sha256"], "status": node["record"]["status"],
                "started_at": node["record"].get("started_at"),
                "completed_at": node["record"]["completed_at"],
                "elapsed_seconds": node["record"].get("elapsed_seconds"),
                "successful_modules": len(node["passed"]),
                "successful_selected_modules": sum(groups[n] == "selected" for n in node["passed"]),
                "inherited_modules": sum("resumed_from" in node["rows"][n] for n in node["passed"]),
                "dependency_graph_sha256": node["graph_sha256"],
                "lake_manifest_sha256": node["record"].get("lake_manifest_sha256"),
                "terminal_revision": node["record"].get("resume", {}).get("terminal_revision")}
               for node in reversed(nodes)]
    metadata = {"schema_version": 2, "mode": "terminal_revision" if revision_record else "unchanged_sources",
                "result_path": str(latest["path"].relative_to(root)), "result_sha256": latest["sha256"],
                "authenticated_modules": len(latest["passed"]),
                "authenticated_selected_modules": sum(groups[n] == "selected" for n in latest["passed"]),
                "earlier_report_reused_paperxi_objects": latest["record"]["paperxi_objects_reused"],
                "terminal_revision": revision_record, "lineage": lineage,
                "lineage_scope": "All authenticated ancestors, oldest first; the current run is a separate result.",
                "fresh_origin_result_path": lineage[0]["result_path"],
                "fresh_origin_result_sha256": lineage[0]["result_sha256"],
                "ancestors_without_recorded_manifest": [item["result_path"] for item in lineage
                                                        if item["lake_manifest_sha256"] is None],
                "note": "Only authenticated successful current-session objects are reused; the explicitly revised failed terminal is invalidated and compiled afresh."}
    return {"rows": [latest["rows"][name] for name in sorted(latest["passed"])],
            "resume": metadata}


def runtime_environment(bin_dir: Path, objects: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    dependencies = sorted((ROOT / ".lake/packages").glob("*/.lake/build/lib/lean"))
    env["LEAN_PATH"] = os.pathsep.join(str(p) for p in [objects, *dependencies])
    env["MATHLIB_CACHE_DIR"] = str(ROOT / ".runtime/mathlib_cache")
    return env


def locate_bin(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    portable = ROOT / ".runtime/lean-4.34.0-rc2-linux/bin"
    if portable.is_dir():
        return portable
    found = shutil.which("lean")
    if not found:
        raise RuntimeError("Pinned Lean runtime unavailable; run bootstrap.py first")
    return Path(found).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="evidence/replay")
    parser.add_argument("--lean-bin")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--resume", help="Earlier replay directory whose successful objects may be authenticated and reused")
    parser.add_argument("--terminal-revision", nargs=2, metavar=("OLD_SHA256", "NEW_SHA256"),
                        help="Explicit failed-terminal-only source revision when resuming a finalized failed run")
    parser.add_argument("--selected-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
    if args.terminal_revision:
        if not args.resume or args.selected_only:
            parser.error("--terminal-revision requires --resume and the complete source population")
        if (any(not re.fullmatch(r"[0-9a-f]{64}", value) for value in args.terminal_revision)
                or args.terminal_revision[0] == args.terminal_revision[1]):
            parser.error("--terminal-revision requires distinct lowercase old and new SHA-256 fingerprints")
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        parser.error("--out must be a new directory inside this project")
    out.mkdir(parents=True)
    objects = out / "objects"
    (objects / "PaperXI").mkdir(parents=True)
    logs = out / "compile_logs"
    logs.mkdir()
    bin_dir = locate_bin(args.lean_bin)
    lean = bin_dir / "lean"
    env = runtime_environment(bin_dir, objects)
    version = subprocess.check_output([str(lean), "--version"], env=env, text=True).strip()
    if LEAN_VERSION not in version or LEAN_COMMIT not in version:
        raise RuntimeError(f"Lean pin mismatch: {version}")
    mathlib = ROOT / ".lake/packages/mathlib"
    commit = subprocess.check_output(["git", "-C", str(mathlib), "rev-parse", "HEAD"], text=True).strip()
    if commit != MATHLIB_COMMIT:
        raise RuntimeError(f"Mathlib pin mismatch: {commit}")
    catalog = json.loads((ROOT / "catalogues/SOURCE_CATALOG.json").read_text())["modules"]
    declarations = json.loads((ROOT / "catalogues/DECLARATION_CATALOG.json").read_text())
    if len(catalog) != 423 or len(declarations) != 4342:
        raise RuntimeError("Release source/declaration population mismatch")
    sources = {name: ROOT / Path(*name.split(".")).with_suffix(".lean") for name in catalog}
    groups = {name: "selected" for name in catalog}
    if not args.selected_only:
        for name, group in [("PaperXI.ActualMonomialLocalGlobal", "terminal"),
                            ("PaperXI.SingleCandidateComparison", "new_interface")]:
            path = ROOT / Path(*name.split(".")).with_suffix(".lean")
            if path.exists():
                sources[name] = path
                groups[name] = group
    before = {str(p.relative_to(ROOT)): sha(p) for p in sources.values()}
    for name, record in catalog.items():
        if before[str(sources[name].relative_to(ROOT))] != record["sha256"]:
            raise RuntimeError(f"Selected source hash mismatch: {name}")
    dependency_map = {}
    for name, path in sources.items():
        actual_imports = imports(path)
        if name in catalog and actual_imports != catalog[name]["imports"]:
            raise RuntimeError(f"Import catalogue mismatch: {name}")
        missing = [imp for imp in actual_imports if imp.startswith("PaperXI.") and imp not in sources]
        if missing:
            raise RuntimeError(f"Missing project imports in {name}: {missing}")
        dependency_map[name] = {imp for imp in actual_imports if imp in sources}
    report = {
        "status": "RUNNING", "started_at": stamp(), "argv": sys.argv,
        "working_directory": str(ROOT), "lean_version": version,
        "lean_binary_sha256": sha(lean), "mathlib_commit": commit,
        "jobs": args.jobs, "threads_per_lean_process": 1,
        "per_module_timeout_seconds": args.timeout, "compile_heartbeats": 3000000,
        "selected_source_count": len(catalog), "catalogued_name_count": len(declarations),
        "selected_sources_match_catalogue": True, "paperxi_objects_reused": False,
        "script_sha256": sha(Path(__file__)),
        "lake_manifest_sha256": sha(ROOT / "lake-manifest.json"),
        "external_mathlib_rebuilt": False,
        "source_hashes_before": before, "modules": [], "aggregates": [],
        "checks": ["All 423 selected source hashes match the retained catalogue.",
                   "Actual imports match the catalogue and the selected dependency graph closes."]
    }
    write_json(out / "DEPENDENCY_GRAPH.json", {k: sorted(v) for k, v in dependency_map.items()})
    report["dependency_graph_sha256"] = sha(out / "DEPENDENCY_GRAPH.json")
    shutil.copy2(Path(__file__), out / "REPLAY_SCRIPT_EXECUTED.py")
    report["executed_script_snapshot"] = str((out / "REPLAY_SCRIPT_EXECUTED.py").relative_to(ROOT))
    write_json(out / "RESULT.json", report)
    start = time.monotonic()

    def compile_one(name: str, path: Path, group: str) -> dict:
        output = objects / Path(*name.split("."))
        output.parent.mkdir(parents=True, exist_ok=True)
        log = logs / (name + ".log")
        command = [str(lean), "-j1", "-DmaxHeartbeats=3000000", "-o",
                   str(output.with_suffix(".olean")), "-i",
                   str(output.with_suffix(".ilean")), str(path.relative_to(ROOT))]
        began = stamp()
        t = time.monotonic()
        with log.open("w") as f:
            try:
                process = subprocess.run(command, cwd=ROOT, env=env, stdout=f,
                                         stderr=subprocess.STDOUT, timeout=args.timeout)
                code = process.returncode
                status = "PASS" if code == 0 else "FAIL"
            except subprocess.TimeoutExpired:
                code = None
                status = "TIMEOUT"
        text = log.read_text(errors="replace")
        artifacts = {str(p.relative_to(ROOT)): sha(p)
                     for p in sorted(output.parent.glob(output.name + ".*")) if p.is_file()}
        unchanged = before.get(str(path.relative_to(ROOT)), sha(path)) == sha(path)
        if not unchanged:
            status = "INPUTS_CHANGED"
        if code == 0 and not output.with_suffix(".olean").is_file():
            status = "RESULT_MISSING"
        return {
            "module": name, "group": group, "status": status, "exit_code": code,
            "started_at": began, "seconds": time.monotonic() - t, "command": command,
            "source_path": str(path.relative_to(ROOT)), "source_sha256": sha(path),
            "source_unchanged": unchanged, "log_path": str(log.relative_to(ROOT)),
            "log_sha256": sha(log), "warning_lines": len(re.findall(r"\bwarning:", text)),
            "artifacts": artifacts,
        }

    pending = set(sources)
    passed, failed = set(), set()
    if args.resume:
        previous = (ROOT / args.resume).resolve()
        if not previous.is_relative_to(ROOT) or previous == out:
            raise RuntimeError("Resume directory must be a different directory within the project")
        try:
            plan = authenticate_resume(ROOT, previous, report, groups, dependency_map,
                                       tuple(args.terminal_revision) if args.terminal_revision else None)
        except Exception as exc:
            report.update(status="RESUME_REJECTED", completed_at=stamp(), resume_error=str(exc))
            write_json(out / "RESULT.json", report)
            raise
        for row in plan["rows"]:
            name = row["module"]
            new_artifacts = {}
            for relative_path, fingerprint in row["artifacts"].items():
                original = _relative_file(ROOT, relative_path)
                target = objects / original.relative_to(previous / "objects")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
                if sha(target) != fingerprint:
                    raise RuntimeError(f"Resume copy mismatch: {relative_path}")
                new_artifacts[str(target.relative_to(ROOT))] = fingerprint
            carried = dict(row)
            carried["artifacts"] = new_artifacts
            carried["resumed_from"] = {"result_path": plan["resume"]["result_path"],
                                      "result_sha256": plan["resume"]["result_sha256"],
                                      "original_artifacts": row["artifacts"]}
            report["modules"].append(carried)
            pending.remove(name)
            passed.add(name)
        for ancestor in plan["resume"]["lineage"]:
            if sha(_relative_file(ROOT, ancestor["result_path"])) != ancestor["result_sha256"]:
                raise RuntimeError("Resume ancestor receipt changed during authentication/copy")
        if sha(ROOT / "lake-manifest.json") != report["lake_manifest_sha256"] or sha(lean) != report["lean_binary_sha256"]:
            raise RuntimeError("Resume runtime or dependency manifest changed during authentication/copy")
        report["paperxi_objects_reused"] = bool(passed)
        report["resume"] = plan["resume"]
        write_json(out / "RESULT.json", report)
        print(f"Authenticated and copied {len(passed)} completed modules from {args.resume}; {len(pending)} remain.", flush=True)
    running = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        while pending or running:
            ready = sorted(n for n in pending if dependency_map[n] <= passed)
            for name in ready[:args.jobs - len(running)]:
                pending.remove(name)
                running[pool.submit(compile_one, name, sources[name], groups[name])] = name
            if not running:
                for name in sorted(pending):
                    report["modules"].append({"module": name, "group": groups[name],
                        "status": "BLOCKED", "unavailable_dependencies": sorted(dependency_map[name] - passed)})
                break
            done, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in done:
                name = running.pop(future)
                try:
                    row = future.result()
                except Exception as exc:
                    row = {"module": name, "group": groups[name], "status": "LAUNCH_FAILED", "error": repr(exc)}
                report["modules"].append(row)
                if row["status"] == "PASS":
                    passed.add(name)
                else:
                    failed.add(name)
                report["elapsed_seconds"] = time.monotonic() - start
                write_json(out / "RESULT.json", report)
                print(f'{len(report["modules"]):03d}/{len(sources)} {name}: {row["status"]} '
                      f'({row.get("seconds", 0):.2f}s)', flush=True)
    selected_ok = all(n in passed for n in catalog)
    aggregates = [("PaperXI", "selected")] if selected_ok else []
    if "PaperXI.ActualMonomialLocalGlobal" in passed:
        aggregates.append(("PaperXITerminal", "terminal"))
    if "PaperXI.SingleCandidateComparison" in passed:
        aggregates.append(("PaperXIAdditions", "new_interface"))
    for name, group in aggregates:
        row = compile_one(name, ROOT / (name + ".lean"), group)
        report["aggregates"].append(row)
        print(f'Aggregate {name}: {row["status"]}', flush=True)
    after = {str(p.relative_to(ROOT)): sha(p) for p in sources.values()}
    manifest_after, lean_after = sha(ROOT / "lake-manifest.json"), sha(lean)
    runtime_inputs_unchanged = (manifest_after == report["lake_manifest_sha256"]
                               and lean_after == report["lean_binary_sha256"])
    report.update(source_hashes_after=after, all_sources_unchanged=before == after,
                  lake_manifest_sha256_after=manifest_after, lean_binary_sha256_after=lean_after,
                  runtime_inputs_unchanged=runtime_inputs_unchanged,
                  selected_status="PASS" if selected_ok else "FAIL",
                  selected_modules_passed=sum(n in passed for n in catalog),
                  terminal_status="PASS" if "PaperXI.ActualMonomialLocalGlobal" in passed else "NOT_PASSED",
                  new_interface_status="PASS" if "PaperXI.SingleCandidateComparison" in passed else "NOT_PASSED",
                  elapsed_seconds=time.monotonic() - start, completed_at=stamp())
    report["status"] = "PASS" if len(passed) == len(sources) and before == after and runtime_inputs_unchanged and all(
        row["status"] == "PASS" for row in report["aggregates"]) else "PARTIAL_OR_FAIL"
    write_json(out / "RESULT.json", report)
    print(json.dumps({k: report[k] for k in ["status", "selected_status", "selected_modules_passed",
          "terminal_status", "new_interface_status", "all_sources_unchanged", "elapsed_seconds"]}), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

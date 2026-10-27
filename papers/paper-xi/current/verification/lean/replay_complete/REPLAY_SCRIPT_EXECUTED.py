#!/usr/bin/env python3
"""Freshly compile immutable Paper XI sources with bounded parallel processes.

Run from any directory after bootstrapping the pinned dependencies. Every run
requires a new output directory. Selected sources and additions are counted
separately, and a failed addition does not prevent independent selected sources
from being checked. By default no Paper XI object is reused. An explicit resume
authenticates source and artifact hashes from an earlier replay receipt.
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
    parser.add_argument("--selected-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
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
    write_json(out / "RESULT.json", report)
    write_json(out / "DEPENDENCY_GRAPH.json", {k: sorted(v) for k, v in dependency_map.items()})
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
        previous_path = previous / "RESULT.json"
        previous_report = json.loads(previous_path.read_text())
        if previous_report["status"] == "RUNNING":
            raise RuntimeError("Cannot resume an unfinished replay")
        for key in ["lean_version", "lean_binary_sha256", "mathlib_commit"]:
            if previous_report[key] != report[key]:
                raise RuntimeError(f"Resume runtime mismatch: {key}")
        if previous_report["source_hashes_before"] != before or previous_report["source_hashes_after"] != before:
            raise RuntimeError("Resume source population or fingerprints changed")
        previous_passed = {row["module"]: row for row in previous_report["modules"]
                           if row["status"] == "PASS"}
        if not set(previous_passed) <= set(sources):
            raise RuntimeError("Resume contains an unknown successful module")
        for name, row in previous_passed.items():
            if row["group"] != groups[name] or not dependency_map[name] <= set(previous_passed):
                raise RuntimeError(f"Resume successful dependency closure mismatch: {name}")
            if row["source_sha256"] != before[str(sources[name].relative_to(ROOT))]:
                raise RuntimeError(f"Resume source receipt mismatch: {name}")
            new_artifacts = {}
            if not row["artifacts"]:
                raise RuntimeError(f"Resume artifacts missing: {name}")
            for relative_path, fingerprint in row["artifacts"].items():
                original = (ROOT / relative_path).resolve()
                if not original.is_relative_to(previous / "objects") or sha(original) != fingerprint:
                    raise RuntimeError(f"Resume object mismatch: {relative_path}")
                target = objects / original.relative_to(previous / "objects")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
                if sha(target) != fingerprint:
                    raise RuntimeError(f"Resume copy mismatch: {relative_path}")
                new_artifacts[str(target.relative_to(ROOT))] = fingerprint
            expected = objects / Path(*name.split(".")).with_suffix(".olean")
            if str(expected.relative_to(ROOT)) not in new_artifacts:
                raise RuntimeError(f"Resume primary object missing: {name}")
            carried = dict(row)
            carried["artifacts"] = new_artifacts
            carried["resumed_from"] = {"result_path": str(previous_path.relative_to(ROOT)),
                                      "result_sha256": sha(previous_path),
                                      "original_artifacts": row["artifacts"]}
            report["modules"].append(carried)
            pending.remove(name)
            passed.add(name)
        report["paperxi_objects_reused"] = bool(passed)
        report["resume"] = {"result_path": str(previous_path.relative_to(ROOT)),
                            "result_sha256": sha(previous_path),
                            "authenticated_modules": len(passed),
                            "authenticated_selected_modules": sum(n in catalog for n in passed),
                            "earlier_report_reused_paperxi_objects": previous_report["paperxi_objects_reused"],
                            "note": "These objects were successfully compiled in the authenticated earlier replay; earlier failed or blocked modules are compiled afresh here."}
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
    report.update(source_hashes_after=after, all_sources_unchanged=before == after,
                  selected_status="PASS" if selected_ok else "FAIL",
                  selected_modules_passed=sum(n in passed for n in catalog),
                  terminal_status="PASS" if "PaperXI.ActualMonomialLocalGlobal" in passed else "NOT_PASSED",
                  new_interface_status="PASS" if "PaperXI.SingleCandidateComparison" in passed else "NOT_PASSED",
                  elapsed_seconds=time.monotonic() - start, completed_at=stamp())
    report["status"] = "PASS" if len(passed) == len(sources) and before == after and all(
        row["status"] == "PASS" for row in report["aggregates"]) else "PARTIAL_OR_FAIL"
    write_json(out / "RESULT.json", report)
    print(json.dumps({k: report[k] for k in ["status", "selected_status", "selected_modules_passed",
          "terminal_status", "new_interface_status", "all_sources_unchanged", "elapsed_seconds"]}), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

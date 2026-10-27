#!/usr/bin/env python3
"""Coordinate the documented reader builders; never invoke Lean or figure generators.

With no --execute, print the proposed commands only. Groups may be run in
separate invocations against one report directory. Existing final artifacts are
measured, but only the selected groups are rebuilt. No component map is edited.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
GROUPS = ("i_iv", "v_viii", "ix_x", "xi_xii")
CHAPTER_GROUP = {ch: group for group, chapters in (
    ("i_iv", ("I", "II", "III", "IV")),
    ("v_viii", ("V", "VI", "VII", "VIII")),
    ("ix_x", ("IX", "X")),
    ("xi_xii", ("XI", "XII")),
) for ch in chapters}
DIAGNOSTICS = {
    "missing_glyph": re.compile(r"Missing character:|does not contain (?:requested )?glyph", re.I),
    "overfull": re.compile(r"Overfull \\[hv]box"),
    "unresolved": re.compile(r"undefined references|undefined citations|(?:Reference|Citation).*undefined|Rerun to get cross-references right|Label\(s\) may have changed", re.I | re.S),
    "font_shape": re.compile(r"Font shape .*undefined|Some font shapes were not available|Font.*substitut", re.I | re.S),
    "tex_error": re.compile(r"^! |LaTeX Error:|Package .* Error:|Emergency stop|Fatal error occurred"),
}


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def role_of(entry: dict) -> str:
    role = entry.get("role")
    if role:
        return {"visual": "visual_guide", "lean": "lean_guide"}.get(role, role)
    name = entry["baseline_filename"]
    if "Visual" in name:
        return "visual_guide"
    if "Lean" in name:
        return "lean_guide"
    return "traditional"


def paths_for(entry: dict, xi_output: Path) -> tuple[Path, Path, Path]:
    chapter, group, role = entry["paper"], CHAPTER_GROUP[entry["paper"]], role_of(entry)
    if group in ("i_iv", "v_viii"):
        component = ROOT / entry["output_pdf"]
        return component, component, component.with_suffix(".log")
    if group == "ix_x":
        name = entry["baseline_filename"]
        raw = ROOT / "source_ix_xii" / chapter / "compiled" / Path(name).stem / name
        component = ROOT / "source_ix_xii" / chapter / "publication/pdfs" / name
        return raw, component, raw.with_suffix(".log")
    stem = f"Paper_{chapter}_" + {"traditional": "Traditional", "visual_guide": "Visual_Guide", "lean_guide": "Lean_Guide"}[role] + "_Final"
    raw = xi_output / chapter / ("build" if chapter == "XI" else "") / role / (stem + ".pdf")
    component = xi_output / chapter / entry["baseline_filename"]
    return raw, component, raw.with_suffix(".log")


def scan_log(path: Path) -> dict:
    findings = {key: [] for key in DIAGNOSTICS}
    if not path.exists():
        return {"log": relative(path), "exists": False, "findings": findings, "warning_count": None}
    lines = path.read_text(errors="replace").splitlines()
    for number, line in enumerate(lines):
        # TeX often wraps a warning's font or label details onto the next line.
        context = "\n".join(lines[number:min(len(lines), number + 4)])
        for key, pattern in DIAGNOSTICS.items():
            matched = pattern.search(line)
            if key == "font_shape":
                matched = pattern.search(context) if "Font Warning:" in line else None
            if key == "unresolved" and re.search(r"(?:Reference|Citation)", line):
                matched = pattern.search(context)
            if matched:
                findings[key].append({"log_line": number + 1, "message": line, "context": context})
    return {"log": relative(path), "exists": True, "findings": findings,
            "warning_count": sum("Warning:" in line for line in lines)}


def pdf_record(path: Path) -> dict:
    if not path.is_file():
        return {"path": relative(path), "exists": False}
    import fitz
    with fitz.open(path) as document:
        pages = len(document)
    return {"path": relative(path), "exists": True, "pages": pages,
            "sha256": sha(path), "bytes": path.stat().st_size,
            "mtime_ns": path.stat().st_mtime_ns}


def group_commands(args: argparse.Namespace, xi_output: Path) -> dict[str, list[str]]:
    return {
        "i_iv": [sys.executable, str(ROOT / "source_i_iv/rebuild_all.py")],
        "v_viii": [sys.executable, str(ROOT / "source_v_viii/build_all.py"), "--jobs", str(args.v_viii_jobs)],
        "ix_x": [sys.executable, str(ROOT / "source_ix_xii/typeset_ix_x.py")],
        "xi_xii": [sys.executable, str(ROOT / "source_ix_xii/rebuild_xi_xii.py"), "--output", str(xi_output)],
    }


def run_group(group: str, command: list[str], report_dir: Path) -> dict:
    started = time.time_ns()
    log = report_dir / f"{group}.driver.log"
    print(f"START {group}: {relative(log)}", flush=True)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TZ="UTC")
    with log.open("w") as stream:
        proc = subprocess.run(command, cwd=ROOT, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    record = {"group": group, "command": command, "cwd": str(ROOT),
              "started_utc": dt.datetime.fromtimestamp(started / 1e9, dt.timezone.utc).isoformat(),
              "started_ns": started, "returncode": proc.returncode,
              "seconds": round((time.time_ns() - started) / 1e9, 3), "driver_log": relative(log),
              "lean_execution": "not_run", "scientific_figure_generation": "not_run"}
    write_json(report_dir / f"{group}.driver.json", record)
    print(f"DONE {group}: exit {proc.returncode}; {record['seconds']} s", flush=True)
    return record


def aggregate(report_dir: Path, xi_output: Path) -> dict:
    metadata = json.loads((ROOT / "component_builds.json").read_text())["components"]
    entries = [entry for entry in metadata if entry.get("build_kind") != "preserved_pdf"]
    if len(entries) != 36:
        raise ValueError(f"Expected 36 source reader components, found {len(entries)}")
    drivers = {group: json.loads((report_dir / f"{group}.driver.json").read_text())
               for group in GROUPS if (report_dir / f"{group}.driver.json").exists()}
    expected_file = report_dir / "KNOWN_VII_MATH_FONT_WARNINGS.json"
    expected_fonts = json.loads(expected_file.read_text())["allowed_contexts"] if expected_file.exists() else []
    components = []
    for entry in entries:
        group = CHAPTER_GROUP[entry["paper"]]
        raw, output, log = paths_for(entry, xi_output)
        raw_pdf, component_pdf = pdf_record(raw), pdf_record(output)
        driver = drivers.get(group)
        diagnostics = scan_log(log)
        fresh = bool(driver and raw_pdf.get("exists") and raw_pdf["mtime_ns"] >= driver["started_ns"])
        font_findings = diagnostics["findings"]["font_shape"]
        known_fonts = (entry["paper"] == "VII" and role_of(entry) == "traditional"
                       and len(expected_fonts) == 4
                       and [item["context"] for item in font_findings] == [item["context"] for item in expected_fonts])
        if known_fonts:
            for item in font_findings:
                item["known_nonfatal"] = True
            diagnostics["known_exception"] = {
                "reason": "Root-reviewed preexisting Latin Modern Math bold fallback: exact same three shapes, locations, and fallback contexts, plus their final summary. Mathematical fonts deliberately unchanged.",
                "record": relative(expected_file), "individual_shape_warnings": 3, "summary_warnings": 1}
        actionable = {key: [item for item in items if not item.get("known_nonfatal")]
                      for key, items in diagnostics["findings"].items()}
        diagnostics_pass = diagnostics["exists"] and not any(actionable.values())
        components.append({"paper": entry["paper"], "role": role_of(entry), "group": group,
                           "baseline_filename": entry["baseline_filename"],
                           "baseline_pages": entry.get("baseline_pages"), "previous_pages": entry.get("pages"),
                           "raw_pdf": raw_pdf, "component_pdf": component_pdf,
                           "output_pdf": relative(output), "pages": component_pdf.get("pages"),
                           "sha256": component_pdf.get("sha256"), "raw_fresh_for_recorded_run": fresh,
                           "group_driver_returncode": driver.get("returncode") if driver else None,
                           "diagnostics": diagnostics, "diagnostics_pass": diagnostics_pass,
                           "build_pass": bool(fresh and component_pdf.get("exists") and driver and driver["returncode"] == 0)})
    totals = {key: sum(len(row["diagnostics"]["findings"][key]) for row in components) for key in DIAGNOSTICS}
    actionable_totals = {key: sum(sum(not item.get("known_nonfatal") for item in row["diagnostics"]["findings"][key])
                                  for row in components) for key in DIAGNOSTICS}
    navigation_path = ROOT / "source_i_iv/navigation_updates.json"
    navigation = json.loads(navigation_path.read_text()) if navigation_path.exists() else None
    if navigation is not None:
        write_json(report_dir / "i_iv_navigation_updates.json", navigation)
    report = {"schema": "komorebi.prose-rebuild/1", "root": str(ROOT),
              "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "scope": "36 current reader PDFs only; inherited Lean and scientific figure evidence is not rerun",
              "drivers": drivers, "components": components, "diagnostic_counts": totals,
              "actionable_diagnostic_counts": actionable_totals,
              "rebuilt_components": sum(row["build_pass"] for row in components),
              "components_passing_diagnostics": sum(row["diagnostics_pass"] for row in components),
              "all_36_built": all(row["build_pass"] for row in components),
              "all_diagnostics_clear": not any(totals.values()),
              "all_actionable_diagnostics_clear": not any(actionable_totals.values()),
              "root_component_map_changed_by_orchestrator": False,
              "navigation_journal": relative(report_dir / "i_iv_navigation_updates.json") if navigation else None}
    write_json(report_dir / "REBUILD_ALL_COMPONENTS.json", report)
    updates = [{"paper": row["paper"], "role": row["role"], "baseline_filename": row["baseline_filename"],
                "output_pdf": row["output_pdf"], "pages": row["pages"], "sha256": row["sha256"],
                "build_kind": "source_retypeset", "raw_pdf": row["raw_pdf"],
                "build_pass": row["build_pass"], "diagnostics_pass": row["diagnostics_pass"],
                "diagnostics": row["diagnostics"]} for row in components]
    write_json(report_dir / "raw_component_updates.json", {
        "status": "SEALED" if report["all_36_built"] and report["all_actionable_diagnostics_clear"] else "INCOMPLETE",
        "scope": "Fresh source-reader component PDFs before collected-monograph assembly; component map unchanged",
        "components": updates})
    table = ["| Chapter | Role | Baseline filename | Raw pages | Component pages | Build | Diagnostics |", "|---|---|---|---:|---:|---|---|"]
    for row in components:
        diagnostic_label = "known math fallback" if row["diagnostics"].get("known_exception") else ("clear" if row["diagnostics_pass"] else "inspect")
        table.append(f"| {row['paper']} | {row['role']} | {row['baseline_filename']} | {row['raw_pdf'].get('pages', '—')} | {row.get('pages', '—')} | {'PASS' if row['build_pass'] else 'PENDING/FAIL'} | {diagnostic_label} |")
    (report_dir / "REBUILD_ALL_COMPONENTS.md").write_text(
        "# Current reader rebuild\n\n" + f"Fresh components: {report['rebuilt_components']}/36. Raw diagnostic counts: {totals}. Actionable diagnostic counts: {actionable_totals}.\n\n" + "\n".join(table) + "\n\nThe only permitted warning exception is the exact preexisting VII traditional Latin Modern Math bold fallback: three individual warnings and their summary. III text-font shape warnings must be zero. The JSON record contains exact paths, page counts, SHA-256 values, and diagnostic context. No Lean or scientific figure generation was run.\n")
    print(json.dumps({key: report[key] for key in ("rebuilt_components", "components_passing_diagnostics", "diagnostic_counts", "all_36_built")}), flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run selected documented drivers after the coordinator's authorization.")
    parser.add_argument("--collect-only", action="store_true", help="Refresh records from an existing authorized run without compilation.")
    parser.add_argument("--groups", nargs="+", choices=GROUPS, default=list(GROUPS))
    parser.add_argument("--groups-jobs", type=int, default=2)
    parser.add_argument("--v-viii-jobs", type=int, default=2)
    parser.add_argument("--report-dir", type=Path, default=Path("editorial/prose_review/build_run"))
    parser.add_argument("--xi-output", type=Path, default=Path("source_ix_xii/prose_rebuild_xi_xii"))
    args = parser.parse_args()
    report_dir = (ROOT / args.report_dir).resolve()
    xi_output = (ROOT / args.xi_output).resolve()
    commands = group_commands(args, xi_output)
    if not args.execute and not args.collect_only:
        print(json.dumps({"status": "PLAN_ONLY", "groups": {group: commands[group] for group in args.groups}, "report_dir": str(report_dir)}, indent=2))
        return 0
    report_dir.mkdir(parents=True, exist_ok=True)
    if args.execute:
        if "xi_xii" in args.groups and xi_output.exists() and any(xi_output.iterdir()):
            parser.error("XI/XII output must be new or empty; choose --xi-output for a rerun.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.groups_jobs)) as pool:
            futures = [pool.submit(run_group, group, commands[group], report_dir) for group in args.groups]
            for future in concurrent.futures.as_completed(futures):
                future.result()
    report = aggregate(report_dir, xi_output)
    requested = [row for row in report["components"] if row["group"] in args.groups]
    return 0 if all(row["build_pass"] and row["diagnostics_pass"] for row in requested) else 1


if __name__ == "__main__":
    raise SystemExit(main())

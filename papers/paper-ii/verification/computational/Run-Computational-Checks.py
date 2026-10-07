#!/usr/bin/env python3
"""Rerun the existing Paper II finite checks without modifying either source tree.

Usage: python Run-Computational-Checks.py --release-root PATH --visual-root PATH
       --output-dir NEW_DIRECTORY
Requires the release Python dependencies, pytest, and SymPy 1.14.0.
This runner does not run Lean, build a paper, install packages, or add tests.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inventory(root):
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob("*"))
            if p.is_file() and not any(x in p.parts for x in ("__pycache__", ".pytest_cache", ".lake"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--visual-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--command-timeout", type=int, default=240)
    args = parser.parse_args()
    release, visual, output = (p.resolve() for p in (args.release_root, args.visual_root, args.output_dir))
    if output.exists():
        raise SystemExit("Output directory must be new; prior evidence will not be overwritten.")
    if any(output == p or output.is_relative_to(p) for p in (release, visual)):
        raise SystemExit("Output directory must be outside source trees.")
    output.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    before = {"release": inventory(release), "visual": inventory(visual)}
    commands = []
    selected_env = {"PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg", "SOURCE_DATE_EPOCH": "1788393600",
                    "PYTHONPATH": str(release / "code/python"), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                    "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                    "NUMEXPR_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1", "BLIS_NUM_THREADS": "1"}
    env = os.environ.copy()
    env.update(selected_env)
    versions = {"Python": platform.python_version()}
    for name in ("numpy", "sympy", "matplotlib", "pytest", "setuptools", "wheel", "build", "PyMuPDF", "pypdf"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    package_pins = {}
    for line in (release / "code/python/requirements.lock").read_text().splitlines():
        if "==" in line and not line.startswith("#"):
            name, pinned = line.split("==", 1)
            try:
                actual = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                actual = None
            package_pins[name] = {"pinned": pinned, "actual": actual, "matches": pinned == actual}

    def run(name, argv, cwd):
        t0 = time.monotonic()
        start = datetime.now(timezone.utc).isoformat()
        timed_out = False
        with (output / f"{name}.stdout.txt").open("wb") as stdout, (output / f"{name}.stderr.txt").open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = process.wait(timeout=args.command_timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
        rec = {"name": name, "argv": [str(a) for a in argv], "cwd": str(cwd), "started_at": start,
               "runtime_seconds": round(time.monotonic() - t0, 6), "exit_code": code, "timed_out": timed_out,
               "stdout": f"{name}.stdout.txt", "stderr": f"{name}.stderr.txt"}
        commands.append(rec)
        print(f"{name}: exit={code}, runtime={rec['runtime_seconds']}s", flush=True)
        return code

    integrity = {"manifest_sha256": digest(release / "SHA256SUMS.txt"), "entries": []}
    for line in (release / "SHA256SUMS.txt").read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        p = release / name
        exists = p.is_file()
        actual = digest(p) if exists else None
        integrity["entries"].append({"path": name, "expected_sha256": expected, "actual_sha256": actual,
                                     "status": "missing" if not exists else "match" if actual == expected else "mismatch"})
    integrity["entry_count"] = len(integrity["entries"])
    integrity["counts"] = {k: sum(e["status"] == k for e in integrity["entries"]) for k in ("match", "missing", "mismatch")}
    (output / "release_integrity.json").write_text(json.dumps(integrity, indent=2) + "\n")

    with tempfile.TemporaryDirectory(prefix="paperII-computation-") as tmp_name:
        tmp = Path(tmp_name)
        env["MPLCONFIGDIR"] = str(tmp / "mplconfig")
        selected_env["MPLCONFIGDIR"] = "temporary isolated directory (deleted after run)"
        run("pytest", [sys.executable, "-m", "pytest", "-q", "-W", "error", "-p", "no:cacheprovider",
                       "--import-mode=importlib", "--junitxml", str(output / "pytest.xml"),
                       str(release / "code/python/tests")], tmp)
        run("release_regeneration", [sys.executable, str(release / "code/python/run_all.py"),
                                    "--output-root", str(output / "generated_release"),
                                    "--compare-release-root", str(release)], tmp)
        copied_visual = tmp / "visual_appendix"
        (copied_visual / "source").mkdir(parents=True)
        (copied_visual / "checks").mkdir()
        for p in (visual / "source").glob("*.py"):
            shutil.copy2(p, copied_visual / "source" / p.name)
        shutil.copy2(visual / "checks/verify_examples.py", copied_visual / "checks/verify_examples.py")
        run("exact_visual_examples", [sys.executable, str(copied_visual / "checks/verify_examples.py")], copied_visual)
        exact_path = copied_visual / "checks/EXACT_CHECKS.json"
        if exact_path.exists():
            shutil.copy2(exact_path, output / "EXACT_CHECKS.json")
        run("visual_graphics_regeneration", [sys.executable, str(copied_visual / "source/generate_graphics.py")], copied_visual)
        fresh_plates = {p.name: digest(p) for p in sorted((copied_visual / "graphics").glob("*.tex"))}
        shipped_plates = {p.name: digest(p) for p in sorted((visual / "graphics").glob("*.tex"))}
        plates = {"fresh_count": len(fresh_plates), "shipped_count": len(shipped_plates),
                  "all_byte_identical": fresh_plates == shipped_plates,
                  "entries": [{"name": name, "shipped_sha256": shipped_plates.get(name),
                               "regenerated_sha256": fresh_plates.get(name),
                               "byte_identical": fresh_plates.get(name) == shipped_plates.get(name)}
                              for name in sorted(set(fresh_plates) | set(shipped_plates))]}
        (output / "tikz_comparison.json").write_text(json.dumps(plates, indent=2) + "\n")

    after = {"release": inventory(release), "visual": inventory(visual)}
    hash_record = {"before": before, "after": after, "unchanged": before == after,
                   "counts": {k: len(v) for k, v in before.items()},
                   "excluded": ["__pycache__", ".pytest_cache", ".lake"]}
    (output / "source_hashes.json").write_text(json.dumps(hash_record, indent=2) + "\n")
    pytest_counts = {}
    if (output / "pytest.xml").exists():
        suites = ET.parse(output / "pytest.xml").getroot()
        pytest_counts = {k: sum(int(s.get(k, "0")) for s in suites.iter("testsuite"))
                         for k in ("tests", "errors", "failures", "skipped")}
    exact = json.loads((output / "EXACT_CHECKS.json").read_text()) if (output / "EXACT_CHECKS.json").exists() else {}
    saved_exact = json.loads((visual / "checks/EXACT_CHECKS.json").read_text())
    semantic_keys = ("status", "scope", "check_count", "sympy_version", "model_sha256", "checks")
    exact_comparison = all(exact.get(k) == saved_exact.get(k) for k in semantic_keys)
    all_pass = (all(c["exit_code"] == 0 for c in commands) and hash_record["unchanged"]
                and integrity["counts"]["missing"] == 0 and integrity["counts"]["mismatch"] == 0
                and plates["all_byte_identical"] and exact_comparison)
    figures = sorted((output / "generated_release/paper/figures").glob("*"))
    report = {"status": "PASS" if all_pass else "FAIL", "started_at": started,
              "runtime_seconds": round(time.monotonic() - begin, 6),
              "python_executable": sys.executable, "source_roots": {"release": str(release), "visual": str(visual)},
              "environment": {"software": versions, "platform": platform.platform(), "machine": platform.machine(),
                              "selected_variables": selected_env, "release_pin_comparison": package_pins},
              "limits": {"per_command_wall_seconds": args.command_timeout, "numerical_threads": 1,
                         "thread_limits_are_cooperative": True}, "commands": commands,
              "pytest": pytest_counts, "exact_visual_check_count": exact.get("check_count"),
              "exact_visual_all_pass": all(c["passed"] for c in exact.get("checks", [])) and bool(exact),
              "exact_visual_saved_record_semantically_identical": exact_comparison,
              "exact_comparison_ignored_field": "timestamp_utc",
              "tikz": {k: v for k, v in plates.items() if k != "entries"},
              "release_integrity": {k: v for k, v in integrity.items() if k != "entries"},
              "source_hash_counts": hash_record["counts"], "source_trees_unchanged": hash_record["unchanged"],
              "regenerated_figure_counts": {suffix: sum(p.suffix == suffix for p in figures) for suffix in (".png", ".pdf")},
              "record_comparison": {"relative_tolerance": 1e-12, "absolute_tolerance": 1e-14,
                                    "nonfloating_values": "exact", "summary_rows": 9},
              "interpretation": "Existing finite assertions and documented release record comparison reproduced; no new proof claims.",
              "non_claims": ["No fresh Lean compiler or kernel replay", "No claim that all general theorems follow from finite tests",
                             "No independent audit of every computational implementation", "No fresh wheel installation or package build",
                             "Release figures are regenerated and presence-checked, not byte-compared to shipped PDF/PNG files"],
              "artifact_hashes": {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*")) if p.is_file()}}
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [f"Paper II bounded computational verification: {report['status']}",
             f"Python tests: {pytest_counts}", f"Exact visual named checks: {exact.get('check_count')}",
             f"Exact saved-record agreement (timestamp excluded): {exact_comparison}",
             f"TikZ regeneration: {plates['fresh_count']}/{plates['shipped_count']} byte-identical={plates['all_byte_identical']}",
             f"Release checksums: {integrity['counts']} ({integrity['entry_count']} entries)",
             f"Source hashes unchanged: {hash_record['unchanged']}; counts={hash_record['counts']}",
             f"Generated figure artifacts: {report['regenerated_figure_counts']}",
             "Release JSON and all nine CSV summary rows compared by the existing checker.",
             "Floating tolerances: relative 1e-12, absolute 1e-14; nonfloating values exact.",
             "No source fixes or dependency installation were made.",
             "No fresh Lean build, kernel replay, wheel build, or universal proof claim.",
             "Environment is recorded exactly and differs from some release pins."]
    (output / "SUMMARY.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

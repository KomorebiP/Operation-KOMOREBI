#!/usr/bin/env python3
"""Replay Paper VI's documented bounded suites without modifying their sources.

Runs in a disposable package copy. Only new contracts, logs, manifests and
results are copied to the chosen new evidence directory. No Lean process runs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = "verification/closeout_2026-10-20/finite"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {p.relative_to(path).as_posix(): digest(p)
            for p in sorted(path.rglob("*")) if p.is_file()}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def software():
    result = [{"name": "Python", "version": platform.python_version()}]
    for name in ("numpy", "scipy", "sympy", "mpmath", "matplotlib", "pytest"):
        result.append({"name": name, "version": importlib.metadata.version(name)})
    return result


def guide_contract(stage, suite, versions):
    guide = stage / "editable/visual_guide"
    previous = json.loads((guide / "checks/runs" / suite / "manifest.json").read_text())
    prefix = "editable/visual_guide/"
    inputs = [prefix + p for p in previous["execution_artifacts"]]
    mathematics = previous["mathematics"]
    mathematics["inputs"] = [prefix + p for p in mathematics["inputs"]]
    return {"claim_id": previous["claim_id"] + "_RELEASE_REPLAY_20261020",
            "mathematics": mathematics, "execution_artifacts": inputs,
            "software": versions, "randomness": previous["randomness"]}


def interpreted_counts(suite, folder):
    result_file = folder / "result.json"
    if not result_file.is_file():
        return {"status": "RESULT_MISSING"}
    result = json.loads(result_file.read_text())
    fields = ("status", "checks_passed", "false_controls_rejected", "pytest_cases",
              "pytest_failures", "pytest_errors", "pytest_skipped", "verifier_test_methods",
              "verifier_corruption_controls", "verifier_positive_controls", "checks_reported",
              "groups", "numeric_output_fields", "identical_numeric_values",
              "figure_pairs", "relative_tolerance", "absolute_tolerance", "plate_count",
              "byte_identical_count", "source_files_verified_unchanged",
              "downloads_files_verified_unchanged", "scope", "overlap")
    answer = {k: result[k] for k in fields if k in result}
    if suite == "monograph_figure_models":
        answer["checks_passed"] = result.get("checks_passed")
    answer["count_type"] = {
        "source_integrity": "file hashes and archive CRC/extraction checks",
        "static_pytest_verifier": "pytest cases and separately counted verifier control methods",
        "original_sympy_exact": "exact/symbolic assertions and separately counted false controls",
        "independent_exact_rational": "independently coded Fraction assertions; overlaps SymPy examples",
        "numerical_companion": "floating output fields and regenerated figure pairs",
        "annals_numerical": "mixed floating comparisons, Boolean/integer checks and source hygiene",
        "strengthened_baseline": "mixed floating comparisons, Boolean/integer checks and source hygiene",
        "strengthened_expanded": "mixed floating comparisons, Boolean/integer checks and source hygiene",
        "monograph_figure_models": "exact Fraction pedagogic assertions",
        "guide_extensions_exact": "exact finite assertions and separately counted false controls",
        "guide_plates": "regenerated TeX geometry files, with byte equality separately reported",
    }[suite]
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="New evidence directory, relative to the package root")
    parser.add_argument("--dependency-path", action="append", default=[],
                        help="Optional local directory containing installed dependencies")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    output.relative_to(ROOT)
    if output.exists():
        raise SystemExit("Refusing to overwrite existing evidence: " + str(output))
    if sys.flags.optimize:
        raise SystemExit("Unoptimized Python is required for the original assertions")
    env = os.environ.copy()
    if args.dependency_path:
        dependencies = [str(Path(p).resolve()) for p in args.dependency_path]
        sys.path[:0] = dependencies
        env["PYTHONPATH"] = os.pathsep.join(dependencies + [env.get("PYTHONPATH", "")])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MPLBACKEND"] = "Agg"
    versions = software()
    before = {folder: tree(ROOT / folder) for folder in ("source", "downloads")}
    started = datetime.now(timezone.utc).isoformat()
    relative_output = output.relative_to(ROOT).as_posix()
    records = []
    with tempfile.TemporaryDirectory(prefix="paper-vi-release-finite-") as temporary:
        stage = Path(temporary) / "package"
        shutil.copytree(ROOT, stage, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".lake"))
        stage_output = stage / relative_output
        stage_output.mkdir(parents=True)
        spec = importlib.util.spec_from_file_location(
            "paper_vi_documented_launcher", stage / "verification/monograph_checks/launch_runs.py")
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        suites = list(launcher.SUITES) + ["guide_extensions_exact", "guide_plates"]
        runner = stage / "verification/monograph_checks/tools/run_experiment.py"
        validator = stage / "verification/monograph_checks/tools/validate_manifest.py"
        for suite in suites:
            out = relative_output + "/runs/" + suite
            if suite in launcher.SUITES:
                contract = launcher.contract(suite)
                results = launcher.results(suite, out)
                command = [sys.executable, "-B", "verification/monograph_checks/run_suite.py",
                           "--suite", suite, "--out", out]
            else:
                kind = "extensions_exact" if suite == "guide_extensions_exact" else "plates"
                contract = guide_contract(stage, kind, versions)
                script = "check_extensions.py" if kind == "extensions_exact" else "regenerate_plates.py"
                destination = out + "/result.json" if kind == "extensions_exact" else out
                command = [sys.executable, "-B", "editable/visual_guide/checks/" + script,
                           "--output", destination]
                results = [out + "/result.json"]
                if kind == "plates":
                    results += [out + "/graphics/" + p.name
                                for p in sorted((stage / "editable/visual_guide/graphics").glob("*.tex"))]
            contract["claim_id"] += "_CURRENT_RELEASE_REPLAY"
            contract["execution_artifacts"] = sorted(set(contract["execution_artifacts"] + [
                "scripts/replay_finite.py", "verification/monograph_checks/launch_runs.py",
                "verification/monograph_checks/tools/run_experiment.py",
                "verification/monograph_checks/tools/validate_manifest.py"]))
            contract_path = stage_output / "contracts" / (suite + ".json")
            write(contract_path, contract)
            argv = [sys.executable, "-B", str(runner), "--root", str(stage),
                    "--contract", str(contract_path), "--output", out,
                    "--timeout", "300", "--max-output-bytes", "4194304",
                    "--max-memory-bytes", "8589934592", "--max-cpu-seconds", "240",
                    "--max-cores", "1", "--max-threads", "1"]
            for name in contract["execution_artifacts"]:
                argv += ["--input", name]
            for name in results:
                argv += ["--result", name]
            argv += ["--"] + command
            log = stage_output / "launcher_logs" / (suite + ".log")
            log.parent.mkdir(parents=True, exist_ok=True)
            completed = subprocess.run(argv, cwd=stage, env=env, text=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            log.write_text(completed.stdout, encoding="utf-8")
            manifest = stage / out / "manifest.json"
            validation = subprocess.run([sys.executable, "-B", str(validator), str(manifest),
                                         "--root", str(stage)], cwd=stage, env=env, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (stage_output / "launcher_logs" / (suite + "_validation.log")).write_text(
                validation.stdout, encoding="utf-8")
            data = json.loads(manifest.read_text()) if manifest.is_file() else {}
            record = {"suite": suite, "execution_exit": completed.returncode,
                      "manifest_validation_exit": validation.returncode,
                      "run_status": data.get("run", {}).get("status", "NO_MANIFEST"),
                      "manifest": out + "/manifest.json",
                      "counts": interpreted_counts(suite, stage / out)}
            records.append(record)
            print(json.dumps({k: record[k] for k in ("suite", "execution_exit",
                              "manifest_validation_exit", "run_status")}), flush=True)
        after = {folder: tree(ROOT / folder) for folder in ("source", "downloads")}
        preserved = before == after
        write(stage_output / "SOURCE_PRESERVATION.json", {
            "status": "PASS" if preserved else "INPUTS_CHANGED",
            "hashes_before": before, "hashes_after": after,
            "source_files": len(before["source"]), "downloads_files": len(before["downloads"])})
        success = preserved and all(r["execution_exit"] == 0 and
            r["manifest_validation_exit"] == 0 and r["run_status"] == "completed" for r in records)
        summary = {"schema": "komorebi.paper_vi.release-finite-replay/1",
                   "status": "PASS_STATED_FINITE_SCOPE" if success else "INCOMPLETE_OR_FAILED",
                   "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
                   "execution": "Disposable full package copy; original source and downloads read-only",
                   "script_sha256": digest(Path(__file__)), "software": versions,
                   "hardware": platform.platform(), "runs": records,
                   "all_original_source_and_download_bytes_preserved": preserved,
                   "no_lean_process_ran": True,
                   "interpretation": "Existing implemented finite assertions reproduced; numerical branches remain conditional on their source tolerances and dependencies.",
                   "inherited_lean": {"fresh_replay": False,
                       "record": "source/complete/original_snapshot/verification/verification_status.json",
                       "scoped_results": 33, "supporting_targets": 341,
                       "production_modules": 47, "namespace_declarations": 782,
                       "open_conjectures_excluded": 3},
                   "non_claims": ["No fresh Lean compilation or transitive axiom audit.",
                       "No universal analytic theorem follows from these finite examples.",
                       "Overlapping assertion totals and mixed counting conventions are not summed.",
                       "Floating numerical output comparison is separate from exact geometry-byte comparison.",
                       "Historical verification receipts are preserved unchanged and remain historical."]}
        write(stage_output / "FINITE_REPLAY.json", summary)
        shutil.copytree(stage_output, output)
    # Validate the preserved relative paths against the actual delivered inputs.
    final_validator = ROOT / "verification/monograph_checks/tools/validate_manifest.py"
    validation_results = []
    for record in records:
        check = subprocess.run([sys.executable, "-B", str(final_validator),
                                str(ROOT / record["manifest"]), "--root", str(ROOT)],
                               cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        validation_results.append({"suite": record["suite"], "exit_status": check.returncode})
        (output / "launcher_logs" / (record["suite"] + "_delivered_validation.log")).write_text(
            check.stdout, encoding="utf-8")
    write(output / "DELIVERED_MANIFEST_VALIDATION.json", validation_results)
    print(json.dumps({"status": summary["status"], "evidence": str(output),
                      "delivered_validation_passed": all(r["exit_status"] == 0 for r in validation_results)}), flush=True)
    return 0 if success and all(r["exit_status"] == 0 for r in validation_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

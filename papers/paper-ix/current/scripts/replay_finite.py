#!/usr/bin/env python3
"""Replay the nine documented Paper IX arithmetic and metadata gates.

Original scientific inputs remain unchanged. All work runs in a disposable
package copy; new evidence alone is retained. No Lean compiler is launched.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = "verification/2026-10-20/finite"
ARITHMETIC = "preserved/threshold_free/computation/"
FORMAL = "preserved/PRSC_IX_Consolidated_Manuscript"
SCRIPTS = {
    "delta_boundary": "evidence/delta_boundary_checks.py",
    "metric_tables": "evidence/metric_table_checks.py",
    "formal_source_reconciliation": "sources/lean/audit_sources.py",
    "dyadic_512": ARITHMETIC + "check_dyadic_differences.py",
    "factorial_extension": ARITHMETIC + "check_factorial_extension.py",
    "factorial_frontier": ARITHMETIC + "check_factorial_frontier.py",
    "visual_figures": "sources/generate_figures.py",
    "worked_examples": "tools/worked_examples.py",
    "reconstructed_figures": "tools/reconstructed_figures.py",
}
TEMPLATES = {
    "delta_boundary": "evidence/delta_boundary_run/manifest.json",
    "metric_tables": "evidence/metric_table_run/manifest.json",
    "formal_source_reconciliation": "sources/lean/audit/static_bound_release_run/manifest.json",
    "dyadic_512": ARITHMETIC + "run512/manifest.json",
    "factorial_extension": ARITHMETIC + "paired96/manifest.json",
    "factorial_frontier": ARITHMETIC + "supplemental96/manifest.json",
    "visual_figures": "verification/2026-10-10/portable_replay/visual_figures/figures/figure_manifest.json",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {p.relative_to(path).as_posix(): digest(p)
            for p in sorted(path.rglob("*")) if p.is_file()}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def expressions(path):
    text = path.read_text()
    result = []
    for item in ast.walk(ast.parse(text)):
        if isinstance(item, (ast.For, ast.comprehension)):
            result.append({"line": getattr(item, "lineno", None),
                           "iterator": ast.get_source_segment(text, item.iter) or ast.unparse(item.iter)})
        elif isinstance(item, ast.Assert):
            result.append({"line": item.lineno, "assertion": ast.unparse(item.test)})
    return result


def contract(stage, name, versions):
    script = SCRIPTS[name]
    inputs = [script, "scripts/replay_finite.py", "replay_checks.py",
              ARITHMETIC + "run_experiment.py", ARITHMETIC + "validate_manifest.py"]
    if name == "metric_tables":
        inputs.append(SCRIPTS["delta_boundary"])
    if name in ("factorial_extension", "factorial_frontier"):
        inputs.append(SCRIPTS["dyadic_512"])
    if name == "formal_source_reconciliation":
        inputs += [p.relative_to(stage).as_posix() for p in sorted((stage / FORMAL).rglob("*")) if p.is_file()]
    if name in TEMPLATES:
        template = json.loads((stage / TEMPLATES[name]).read_text())
        mathematics = template["mathematics"]
        inputs.append(TEMPLATES[name])
    else:
        mathematics = {
            "assertion_tested": ("Eight exact finite worked examples agree with independent coefficient inversion, normalization, sign, Newton and lifting witnesses."
                if name == "worked_examples" else
                "Exact finite examples behind the fourteen reconstructed historical panels agree with the implemented selectors, periods, root filter, local kernels, affine windows, Fibonacci jump and CRT calculations."),
            "coefficient_domain": "Exact rational arithmetic using fractions.Fraction and exact integers",
            "conventions": "Actual normalized reciprocal definitions and explicitly named finite examples; v_p(0) is represented by None.",
            "inputs": [script],
            "bounds": {},
            "non_claims": ["No universal theorem, analytic convergence result or new Lean proof follows from these examples.",
                           "Illustrative reconstructions are not recovered original artwork."]}
    if name == "factorial_extension":
        # The historical shared template mentions four addresses; this particular
        # implemented checker iterates addresses zero, one and two only.
        mathematics["inputs"] = ["Addresses j=0,1,2; actual N=4 reciprocal coefficients through row96; homogeneous steps1..16 and address-two mixed multisets through order5."]
    mathematics["bounds"]["executed_source_expressions"] = expressions(stage / script)
    mathematics["non_claims"] += ["The new run reproduces existing implemented assertions; historical compiler acceptance remains inherited.",
                                  "Overlapping test families and mixed count types are not added as independent theorem coverage."]
    return {"claim_id": "PAPER_IX_RELEASE_20261020_" + name.upper(),
            "mathematics": mathematics, "execution_artifacts": sorted(set(inputs)),
            "software": versions, "randomness": {"used": False, "generator": "", "seed": None}}


def command(name, out):
    result = out + "/result.json"
    script = SCRIPTS[name]
    extra = {
        "delta_boundary": [result], "metric_tables": [result],
        "formal_source_reconciliation": ["--source", FORMAL, "--output", out],
        "dyadic_512": ["--bound", "512", "--precision", "4096", "--order", "128",
                       "--rational-bound", "16", "--output", result],
        "factorial_extension": ["--bound", "96", "--precision", "1024", "--output", result],
        "factorial_frontier": ["--bound", "96", "--precision", "1024", "--mixed-order", "5", "--output", result],
        "worked_examples": ["--output", result], "reconstructed_figures": ["--output", result],
        "visual_figures": ["--visual-only", "--output", out],
    }[name]
    if name == "visual_figures":
        script = "scripts/replay_finite.py"
    return [sys.executable, "-B", script] + extra


def visual_only(output):
    output = (ROOT / output).resolve()
    with tempfile.TemporaryDirectory(prefix="paper-ix-visual-model-") as temp:
        stage = Path(temp)
        (stage / "sources").mkdir()
        shutil.copy2(ROOT / SCRIPTS["visual_figures"], stage / "sources/generate_figures.py")
        done = subprocess.run([sys.executable, "-B", str(stage / "sources/generate_figures.py")],
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        print(done.stdout, end="")
        if done.returncode:
            return done.returncode
        shutil.copytree(stage / "figures", output / "figures")
    data = json.loads((output / "figures/exact_figure_data.json").read_text())
    old_data = json.loads((ROOT / "figures/exact_figure_data.json").read_text())
    same_data = data == old_data
    new_files = sorted((output / "figures").glob("*.pdf"))
    row = {"status": "PASS" if same_data else "FINITE_DATA_CHANGED",
           "assertions": data["total_assertions"], "assertion_counts": data["assertion_counts"],
           "vector_figures": len(new_files), "exact_figure_data_equal_to_preserved": same_data,
           "figure_byte_comparisons": [{"file": p.name, "regenerated_sha256": digest(p),
               "preserved_sha256": digest(ROOT / "figures" / p.name),
               "byte_identical": p.read_bytes() == (ROOT / "figures" / p.name).read_bytes()}
               for p in new_files],
           "scope": "Exact finite plotted data equality is checked separately from rendering byte comparisons; no universal analytic claim."}
    write(output / "result.json", row)
    return 0 if same_data else 1


def counts(name, folder):
    data = json.loads((folder / ("PROVENANCE_AUDIT.json" if name == "formal_source_reconciliation" else "result.json")).read_text())
    keep = ("status", "passed", "regression_passed", "counts", "family_assertions", "additional_definition_checks",
            "additional_cancellation_control", "total_checks", "coefficient_assertions", "boundary_assertions",
            "frontiers", "source_hash_comparisons", "recorded_log_hash_comparisons", "manuscript_source_links",
            "declaration_source_version_rows", "canonical_source_files", "parser_regression", "assertions",
            "vector_figures", "exact_figure_data_equal_to_preserved")
    answer = {k: data[k] for k in keep if k in data}
    if name == "factorial_extension":
        answer["address_counts"] = [{k: r[k] for k in ("j", "homogeneous_exact_checks", "j2_floor_checks", "j2_floor_equalities")}
                                    for r in data["address_results"]]
    if name == "factorial_frontier":
        answer["address_counts"] = [{k: v for k, v in r.items() if k in ("j", "mixed_lower_bound_checks", "unit_step_exact_checks", "j2_double_slope_checks")}
                                    for r in data["family_results"]]
        answer["candidate_failures_are_retained"] = True
    if name == "formal_source_reconciliation":
        answer["fresh_strict_axiom_parser_records"] = data["latest_gate"]["fresh_strict_axiom_parser_records"]
        answer["historical_negative_log_checks"] = len(data["latest_gate"]["negative_control_log_checks"])
        answer["fresh_lean_run"] = data["fresh_lean_run"]
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="New project-relative evidence directory; existing evidence is never overwritten")
    parser.add_argument("--visual-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.visual_only:
        return visual_only(args.output)
    output = (ROOT / args.output).resolve()
    output.relative_to(ROOT)
    if output.exists():
        raise SystemExit("Refusing to overwrite existing evidence: " + str(output))
    if sys.flags.optimize:
        raise SystemExit("Unoptimized Python is required for assertions")
    versions = [{"name": "Python", "version": platform.python_version()}] + [
        {"name": n, "version": importlib.metadata.version(n)} for n in ("numpy", "matplotlib")]
    before = tree(ROOT / "preserved")
    started = datetime.now(timezone.utc).isoformat()
    relative_output = output.relative_to(ROOT).as_posix()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", MPLBACKEND="Agg")
    records = []
    with tempfile.TemporaryDirectory(prefix="paper-ix-finite-release-") as temp:
        stage = Path(temp) / "package"
        shutil.copytree(ROOT, stage, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".lake"))
        stage_output = stage / relative_output
        for name in SCRIPTS:
            out = relative_output + "/runs/" + name
            c = contract(stage, name, versions)
            cpath = stage_output / "contracts" / (name + ".json")
            write(cpath, c)
            result_name = "PROVENANCE_AUDIT.json" if name == "formal_source_reconciliation" else "result.json"
            results = [out + "/" + result_name]
            if name == "formal_source_reconciliation":
                results += [out + "/STATEMENT_SOURCE_LINKS.json", out + "/parser_regression.log",
                            out + "/evidence_replay.log", out + "/reconciled/EVIDENCE_INDEX.json",
                            out + "/reconciled/DECLARATIONS.csv"]
            if name == "visual_figures":
                results += [out + "/figures/exact_figure_data.json", out + "/figures/figure_manifest.json"]
                results += [out + "/figures/" + p.name for p in sorted((stage / "figures").glob("*.pdf"))]
            argv = [sys.executable, "-B", str(stage / ARITHMETIC / "run_experiment.py"),
                    "--root", str(stage), "--contract", str(cpath), "--output", out,
                    "--timeout", "300", "--max-output-bytes", "4194304",
                    "--max-memory-bytes", "4294967296", "--max-cpu-seconds", "240",
                    "--max-cores", "1", "--max-threads", "1"]
            for item in c["execution_artifacts"]:
                argv += ["--input", item]
            for item in results:
                argv += ["--result", item]
            argv += ["--"] + command(name, out)
            completed = subprocess.run(argv, cwd=stage, env=env, text=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            log = stage_output / "launcher_logs" / (name + ".log")
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(completed.stdout, encoding="utf-8")
            manifest = stage / out / "manifest.json"
            validated = subprocess.run([sys.executable, "-B", str(stage / ARITHMETIC / "validate_manifest.py"),
                str(manifest), "--root", str(stage)], cwd=stage, env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (log.parent / (name + "_validation.log")).write_text(validated.stdout, encoding="utf-8")
            data = json.loads(manifest.read_text()) if manifest.is_file() else {}
            record = {"suite": name, "execution_exit": completed.returncode,
                "manifest_validation_exit": validated.returncode,
                "run_status": data.get("run", {}).get("status", "NO_MANIFEST"),
                "manifest": out + "/manifest.json"}
            try:
                record["counts"] = counts(name, stage / out)
            except (FileNotFoundError, KeyError, json.JSONDecodeError) as error:
                record["result_interpretation_error"] = str(error)
            records.append(record)
            print(json.dumps({k: record[k] for k in ("suite", "execution_exit", "manifest_validation_exit", "run_status")}), flush=True)
        after = tree(ROOT / "preserved")
        same = before == after
        write(stage_output / "SOURCE_PRESERVATION.json", {"status": "PASS" if same else "INPUTS_CHANGED",
              "preserved_file_count": len(before), "hashes_before": before, "hashes_after": after})
        passed = same and all(r["execution_exit"] == 0 and r["manifest_validation_exit"] == 0 and
            r["run_status"] == "completed" and "result_interpretation_error" not in r for r in records)
        summary = {"schema": "komorebi.paper_ix.release-finite-replay/1",
            "status": "PASS_STATED_FINITE_SCOPE" if passed else "INCOMPLETE_OR_FAILED",
            "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "script_sha256": digest(Path(__file__)), "software": versions, "hardware": platform.platform(),
            "execution": "Disposable full package copy, unchanged mathematical sources, fresh bounded v2 manifests",
            "runs": records, "preserved_sources_unchanged": same, "fresh_lean_execution": False,
            "non_claims": ["Finite exact arithmetic does not prove universal congruence, lifting, all-rank or analytic-radius assertions.",
                "Formal source/log reconciliation is fresh Python evidence; compiler acceptance and adverse compiler outcomes remain inherited.",
                "Four legacy affine log fingerprints do not acquire missing historical digests.",
                "Arithmetic families and their counts overlap and are not added as independent theorem counts.",
                "Exact plotted data comparisons are separate from visual layout and PDF byte comparisons."]}
        write(stage_output / "FINITE_REPLAY.json", summary)
        shutil.copytree(stage_output, output)
    validations = []
    for record in records:
        validated = subprocess.run([sys.executable, "-B", str(ROOT / ARITHMETIC / "validate_manifest.py"),
            str(ROOT / record["manifest"]), "--root", str(ROOT)], cwd=ROOT, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        validations.append({"suite": record["suite"], "exit_status": validated.returncode})
        (output / "launcher_logs" / (record["suite"] + "_delivered_validation.log")).write_text(validated.stdout, encoding="utf-8")
    write(output / "DELIVERED_MANIFEST_VALIDATION.json", validations)
    good = passed and all(v["exit_status"] == 0 for v in validations)
    print(json.dumps({"status": summary["status"], "delivered_manifests_validated": good,
                      "evidence": str(output)}), flush=True)
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())

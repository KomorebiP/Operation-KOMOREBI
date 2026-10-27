#!/usr/bin/env python3
"""Execute the finite release suite, retaining full reports and source snapshots.

For resource limits and provenance, invoke through the computation-audit runner
as specified in RELEASE_CHECKS.md. Passing this suite is finite evidence only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


CHECKS = (
    "nonlinear_dilation", "asymmetric_dilation", "complex_depth", "orbit_zeta",
    "arithmetic_polynomials", "dilation_type", "arithmetic_inverse",
    "multi_prime_sieve", "spectral_continuation", "family_lab_checks",
)
PROOFS = (
    "routes/nonlinear_dilation.md", "routes/asymmetric_dilation.md",
    "routes/complex_depth.md", "routes/orbit_zeta.md",
    "routes/arithmetic_polynomials.md", "new_results/dilation_type.md",
    "new_results/arithmetic_inverse.md", "new_results/multi_prime_sieve.md",
    "new_results/spectral_continuation.md", "new_results/sequence_polyphase.md",
)
SNAPSHOT_INPUTS = tuple("checks/" + name + ".py" for name in CHECKS) + (
    "family_lab.py", "TARGET_CONTRACT.json", *PROOFS,
)
CLI_OUTPUT = {"dilation_type", "arithmetic_inverse", "multi_prime_sieve"}
LOCATION_OUTPUT = {
    "arithmetic_polynomials": "arithmetic_polynomial_checks.json",
    "spectral_continuation": "spectral_continuation_checks.json",
    "family_lab_checks": "family_lab_checks.json",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def dependency_record(package):
    package_root = Path(package.__file__).resolve().parent
    files = [{"path": str(path.relative_to(package_root)), "sha256": sha256(path)}
             for path in sorted(package_root.rglob("*.py"))]
    payload = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {"name": package.__name__, "version": package.__version__,
            "source_directory": str(package_root), "python_source_files": files,
            "python_source_tree_sha256": hashlib.sha256(payload).hexdigest()}


def arithmetic_counts(report):
    """Executed assertion statements, derived from the inspected finite loops."""
    cases, degrees = report["parameter_cases"], report["checked_degrees"][1]
    pencils = report["hankel_exceptional_strengths"]
    return {
        "positive_norm_groups": cases,
        "orthogonality_residuals": report["orthogonality_tests"],
        "recurrence_intervals": cases * degrees,
        "positive_norm_ratios": cases * degrees,
        "hankel_root_location_groups": len(pencils),
        "hankel_determinant_residuals": sum(len(p["lambda_roots"]) for p in pencils),
        "sieve_margin_bounds": len(report["sieve_margin_bounds"]),
        "depth_transports": report["depth_transport_cases"],
        "tau_positivity_groups": report["tau_identity_cases"],
        "tau_identity_residuals": report["tau_identity_cases"],
        "uvarov_formulas": report["uvarov_formula_cases"],
        "endpoint_recovery_bounds": len(report["mass_recovery"]),
        "prime_flow_derivative_residual": 1,
    }


def count_report(name, report):
    exact = report.get("exact_assertions", report.get(
        "exact_checks", report.get("exact_assertion_count", 0)))
    supplemental, operational = {}, {}
    numerical = {}
    if name == "arithmetic_polynomials":
        exact = 0
        numerical = arithmetic_counts(report)
    elif name == "complex_depth":
        numerical = {"complex_direct_newton_tail_comparisons":
                     len(report["complex_examples"])}
    elif name == "arithmetic_inverse":
        models = report["finite_prony_models"]
        atoms = sum(row["atoms"] for row in models)
        # The source checks these three conditions inside each atom loop, but
        # its own exact_checks counter increments only for the outer checks.
        supplemental = {"exact_square_root_helpers": atoms,
                        "integral_inverse_power_helpers": atoms,
                        "exact_integer_root_helpers": atoms}
        if exact != 5 * len(models) + 4:
            raise ValueError("inverse principal count disagrees with finite model rows")
        peeling, compact = (report["negative_depth_peeling_examples"],
                            report["compact_instability_examples"])
        numerical = {
            "peeling_slope_and_amplitude_bounds": 2 * len(peeling),
            "nearest_integer_recovery": sum(row["atom_index"] == 1 and
                                             float(row["t"]) == 500 for row in peeling),
            "compact_instability_envelopes": sum(len(row["examples"]) for row in compact),
            "zero_depth_mass_anchors": sum(
                float(example["s"][0]) == 0 and float(example["s"][1]) == 0
                for row in compact for example in row["examples"]),
        }
        if sum(numerical.values()) != report["high_precision_checks"]:
            raise ValueError("inverse numerical rows disagree with reported count")
    elif name == "multi_prime_sieve":
        exact = report["counts"]["exact_rational_assertions"]
        numerical = {"instrumented_numerical_assertions":
                     report["counts"]["numerical_assertions"]}
        operational = {"negative_detector_iteration_guards":
                       sum(row["m"] for row in report["negative_atom_detectors"])}
    elif name == "spectral_continuation":
        numerical = {
            "known_N2_N4_continuation_benchmarks": len(report["known_benchmark_cases"]),
            "derivative_at_zero_benchmarks": len(report["derivative_zero_checks"]),
            "N3_N5_precision_comparisons": len(report["N3_N5_values"]),
            "shifted_N2_product_benchmarks": len(report["shifted_N2_product_benchmarks"]),
        }
    if name != "arithmetic_polynomials" and exact <= 0:
        raise ValueError(f"{name} did not report a positive exact count")
    categories = report.get("assertion_counts", report.get(
        "assertion_categories", report.get("exact_assertions_by_category")))
    if categories is not None and sum(categories.values()) != exact:
        raise ValueError(f"{name} exact categories disagree with total")
    return {"reported_principal_exact_assertions": exact,
            "supplemental_exact_helper_assertions": sum(supplemental.values()),
            "supplemental_exact_breakdown": supplemental,
            "actual_exact_assertion_statements": exact + sum(supplemental.values()),
            "numerical_assertion_statements": sum(numerical.values()),
            "numerical_breakdown": numerical,
            "operational_guard_assertions": sum(operational.values()),
            "operational_guard_breakdown": operational}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--dependencies", type=Path, required=True)
    parser.add_argument("--script-timeout", type=float, default=300)
    args = parser.parse_args(argv)
    if sys.flags.optimize:
        raise RuntimeError("Run without -O: assertions must be enabled.")
    root = Path(__file__).resolve().parents[1]
    relative_output = Path(args.output_dir)
    if relative_output.is_absolute() or ".." in relative_output.parts:
        raise ValueError("output directory must be project-relative")
    output = (root / relative_output).resolve()
    if not output.is_relative_to(root) or output == root:
        raise ValueError("output directory must lie below project root")
    if not output.is_dir():
        raise ValueError("the bounded runner must create the fresh output directory")
    if (output / "summary.json").exists() or (output / "snapshot").exists():
        raise FileExistsError("choose a fresh run directory")
    dependencies = args.dependencies.resolve()
    if not dependencies.is_dir():
        raise FileNotFoundError(dependencies)
    sys.path.insert(0, str(dependencies))
    import mpmath
    dependency_before = dependency_record(mpmath)
    contract = json.loads((root / "evidence/release_contract.json").read_text())
    input_before = {name: sha256(root / name) for name in contract["execution_artifacts"]}
    snapshot = output / "snapshot"
    snapshot.mkdir()
    (snapshot / "evidence").mkdir()
    snapshot_records = []
    for name in SNAPSHOT_INPUTS:
        original, destination = root / name, snapshot / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, destination)
        digest = sha256(destination)
        if digest != input_before[name]:
            raise RuntimeError(f"snapshot changed bytes: {name}")
        snapshot_records.append({"source": name, "sha256": digest,
                                 "snapshot": str(destination.relative_to(root)),
                                 "byte_identical": True})

    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(dependencies), str(snapshot / "checks"), str(snapshot)])
    summary = {
        "checkpoint": "SF-DISCOVERY-100", "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "assertions_enabled": True,
        "reports": [], "failures": [], "snapshot_inputs": snapshot_records,
        "dependency_provenance": dependency_before,
        "counting_convention": (
            "Principal exact counts retain each script's counter. The inverse script also "
            "executes three uncounted exact helper assertions per recovered atom; they are "
            "recorded separately and included once in actual exact statements. Numerical "
            "counts count each executed assertion statement once: all(...), compound "
            "positivity, and maximum-residual conditions each count once. Sieve orthogonality "
            "and recurrence counters are subsets of its numerical total. Iteration guards "
            "are operational assertions, excluded from mathematical totals."),
        "non_claims": [
            "Finite computations do not prove universal analytic claims or historical priority.",
            "mpmath comparisons are ordinary high precision, not interval or ball certificates.",
            "Dilation-type decimal samples and inverse rank tables are displays, not assertion counts.",
            "Embedded run_history preserves previous author failures; these are not current release failures.",
            "External mpmath sources are tree-hashed separately and lie outside project-relative runner inputs.",
            "Memory and CPU caps apply per process; they are not aggregate descendant budgets. Thread limits are cooperative.",
        ],
    }
    started = time.perf_counter()
    try:
        for name in CHECKS:
            script = snapshot / "checks" / (name + ".py")
            result_path = output / "reports" / (name + ".json")
            result_path.parent.mkdir(parents=True, exist_ok=True)
            command = [sys.executable, str(script)]
            if name in CLI_OUTPUT:
                command.extend(["--output", str(result_path)])
            script_started = time.perf_counter()
            child = subprocess.run(command, cwd=snapshot, env=environment,
                                   text=True, capture_output=True, timeout=args.script_timeout)
            elapsed = time.perf_counter() - script_started
            log_root = output / "logs"
            log_root.mkdir(exist_ok=True)
            (log_root / (name + ".stdout.txt")).write_text(child.stdout)
            (log_root / (name + ".stderr.txt")).write_text(child.stderr)
            if child.returncode:
                raise RuntimeError(f"{name} exited with status {child.returncode}; full logs retained")
            if len(child.stdout.encode()) + len(child.stderr.encode()) > 4 * 1024 * 1024:
                raise RuntimeError(f"{name} exceeded the 4 MiB per-script report limit")
            stdout_report = json.loads(child.stdout)
            if name in LOCATION_OUTPUT:
                source_result = snapshot / "evidence" / LOCATION_OUTPUT[name]
                shutil.copyfile(source_result, result_path)
            elif name not in CLI_OUTPUT:
                write_json(result_path, stdout_report)
            report = json.loads(result_path.read_text())
            if report["status"].lower() not in {"pass", "passed"}:
                raise RuntimeError(f"{name} reported nonpassing status")
            counts = count_report(name, report)
            expected = contract["expected_assertion_counts"][name]
            if any(counts[key] != value for key, value in expected.items()):
                raise ValueError(f"{name} count differs from the frozen finite contract: {counts}")
            record = {
                "check": name, "status": "passed", "command": command,
                "runtime_seconds": elapsed, "source": "checks/" + name + ".py",
                "source_sha256": sha256(script),
                "result": str(result_path.relative_to(root)),
                "result_sha256": sha256(result_path), **counts,
                "bounds": report.get("bounds", report.get("exact_bounds", report.get("contract", {
                    "parameter_grid": report.get("parameter_grid", report.get("orthogonal_grid")),
                    "precision_decimal_digits": report.get("precision_decimal_digits"),
                }))),
                "preserved_run_history": report.get("run_history", report.get("failure_history", [])),
            }
            summary["reports"].append(record)
            print(json.dumps({key: record[key] for key in (
                "check", "status", "reported_principal_exact_assertions",
                "supplemental_exact_helper_assertions", "numerical_assertion_statements")}), flush=True)
        dependency_after = dependency_record(mpmath)
        if dependency_after != dependency_before:
            raise RuntimeError("external mpmath sources changed during release run")
        summary["status"] = "passed"
    except Exception as error:
        summary["status"] = "failed"
        summary["failures"].append({"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        input_after = {name: sha256(root / name) for name in input_before}
        changed = [name for name in input_before if input_before[name] != input_after[name]]
        if changed:
            summary["status"] = "failed"
            summary["failures"].append({"type": "InputsChanged", "paths": changed})
        snapshot_after = [{**row, "sha256_after": sha256(root / row["snapshot"])}
                          for row in snapshot_records]
        for row in snapshot_after:
            if row["sha256"] != row["sha256_after"]:
                summary["status"] = "failed"
                summary["failures"].append({"type": "SnapshotChanged", "path": row["snapshot"]})
        write_json(output / "input_hashes.json", {
            "original_inputs": [{"path": name, "sha256": input_before[name],
                                 "sha256_after": input_after[name]}
                                for name in input_before],
            "snapshots": snapshot_after, "inputs_unchanged": not changed,
            "external_dependency_source_unchanged": dependency_record(mpmath) == dependency_before,
        })
        for key in ("reported_principal_exact_assertions", "supplemental_exact_helper_assertions",
                    "actual_exact_assertion_statements", "numerical_assertion_statements",
                    "operational_guard_assertions"):
            summary[key] = sum(row[key] for row in summary["reports"])
        summary["runtime_seconds"] = time.perf_counter() - started
        write_json(output / "summary.json", summary)
    print(json.dumps({key: summary[key] for key in (
        "status", "reported_principal_exact_assertions", "supplemental_exact_helper_assertions",
        "actual_exact_assertion_statements", "numerical_assertion_statements",
        "operational_guard_assertions")}), flush=True)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

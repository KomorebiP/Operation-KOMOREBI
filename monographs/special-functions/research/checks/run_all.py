#!/usr/bin/env python3
"""Run the declared finite suite and preserve its separate scientific reports.

Use the computation-audit runner described in checks/README.md for bounded,
hashed provenance. This program does not certify the mathematical proofs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency_record(package):
    package_root = Path(package.__file__).resolve().parent
    files = [{"path": str(path.relative_to(package_root)), "sha256": sha256(path)}
             for path in sorted(package_root.rglob("*.py"))]
    payload = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {"name": package.__name__, "version": package.__version__,
            "source_directory": str(package_root), "python_source_files": files,
            "python_source_tree_sha256": hashlib.sha256(payload).hexdigest()}


def arithmetic_counts(report):
    # Counts of executed assert statements from the inspected loop structure.
    # An all(...) group or max-residual comparison counts as one statement.
    cases = report["parameter_cases"]
    degrees = report["checked_degrees"][1]
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True,
                        help="fresh project-relative scientific-result directory")
    parser.add_argument("--dependencies", type=Path,
                        help="optional directory containing the mpmath package")
    parser.add_argument("--script-timeout", type=float, default=300,
                        help="per-script wall-clock limit in seconds")
    args = parser.parse_args(argv)
    if sys.flags.optimize:
        raise RuntimeError("Run without -O: the finite suite uses assert statements.")

    root = Path(__file__).resolve().parents[1]
    relative_output = Path(args.output_dir)
    if relative_output.is_absolute() or ".." in relative_output.parts:
        raise ValueError("--output-dir must be project-relative")
    output = (root / relative_output).resolve()
    if not output.is_relative_to(root) or output == root:
        raise ValueError("output directory must be below the project root")
    output.mkdir(parents=True, exist_ok=True)
    if (output / "summary.json").exists():
        raise FileExistsError("choose a fresh run directory; summary.json already exists")

    dependency_path = args.dependencies.resolve() if args.dependencies else None
    if dependency_path is not None:
        if not dependency_path.is_dir():
            raise FileNotFoundError(dependency_path)
        sys.path.insert(0, str(dependency_path))
    import mpmath
    dependency_before = dependency_record(mpmath)

    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    search_paths = [str(root / "checks")]
    if dependency_path is not None:
        search_paths.insert(0, str(dependency_path))
    if environment.get("PYTHONPATH"):
        search_paths.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(search_paths)

    reports = []
    exact_total = numerical_total = 0
    for name in ["nonlinear_dilation", "asymmetric_dilation", "complex_depth",
                 "orbit_zeta", "arithmetic_polynomials"]:
        original = root / "checks" / (name + ".py")
        original_hash = sha256(original)
        script = original
        snapshot = None
        if name == "arithmetic_polynomials":
            # This existing script chooses OUT using __file__. An exact source
            # snapshot redirects only its location-dependent report destination.
            script = output / "arithmetic-snapshot" / "checks" / original.name
            if script.exists():
                raise FileExistsError(script)
            script.parent.mkdir(parents=True)
            shutil.copyfile(original, script)
            if sha256(script) != original_hash:
                raise RuntimeError("arithmetic snapshot differs from the pinned source")
            snapshot = {"path": str(script.relative_to(root)), "sha256": sha256(script),
                        "byte_identical_to_original": True}

        command = [sys.executable, str(script)]
        started = time.perf_counter()
        child = subprocess.run(command, cwd=root, env=environment, text=True,
                               capture_output=True, timeout=args.script_timeout)
        elapsed = time.perf_counter() - started
        if child.returncode:
            sys.stderr.write(child.stderr)
            raise RuntimeError(f"{name} exited with status {child.returncode}")
        if len(child.stdout.encode()) + len(child.stderr.encode()) > 4 * 1024 * 1024:
            raise RuntimeError(f"{name} exceeded the aggregate's per-script report limit")
        stdout_report = json.loads(child.stdout)
        if name == "arithmetic_polynomials":
            result_path = (output / "arithmetic-snapshot" / "evidence" /
                           "arithmetic_polynomial_checks.json")
            report = json.loads(result_path.read_text())
            breakdown = arithmetic_counts(report)
            exact, numerical = 0, sum(breakdown.values())
        else:
            result_path = output / (name + ".json")
            if result_path.exists():
                raise FileExistsError(result_path)
            report = stdout_report
            result_path.write_text(json.dumps(report, indent=2) + "\n")
            exact = report.get("exact_assertions", report.get(
                "exact_checks", report.get("exact_assertion_count", 0)))
            if exact <= 0:
                raise RuntimeError(f"{name} did not report a positive exact assertion count")
            numerical = len(report.get("complex_examples", []))
            breakdown = ({"complex_direct_newton_tail_comparisons": numerical}
                         if numerical else {})
        if report["status"].lower() not in {"pass", "passed"}:
            raise RuntimeError(f"{name} did not report a passing status")
        if sha256(original) != original_hash:
            raise RuntimeError(f"{name} input changed while it ran")
        exact_total += exact
        numerical_total += numerical
        reports.append({
            "route": name, "status": "passed", "command": command,
            "runtime_seconds": elapsed, "source": str(original.relative_to(root)),
            "source_sha256": original_hash, "snapshot": snapshot,
            "result_path": str(result_path.relative_to(root)),
            "result_sha256": sha256(result_path), "exact_assertions": exact,
            "numerical_assertion_statements": numerical,
            "numerical_breakdown": breakdown,
            "bounds": report.get("bounds", {
                "prime": [2, 3, 5], "strength": [-1, -0.5, 0, 1, 10],
                "depth": [0, 1, 3, 10], "degree": [0, 6],
                "hankel_order": [1, 4], "decimal_precision": 160}),
        })
        print(json.dumps({"route": name, "status": "passed",
                          "exact_assertions": exact,
                          "numerical_assertion_statements": numerical}), flush=True)

    dependency_after = dependency_record(mpmath)
    if dependency_after != dependency_before:
        raise RuntimeError("mpmath source or version changed during the run")
    summary = {
        "checkpoint": "SF-DISCOVERY-001", "status": "passed",
        "python": platform.python_version(), "assertions_enabled": True,
        "exact_assertions": exact_total,
        "numerical_assertion_statements": numerical_total,
        "route_reports": reports, "dependency_provenance": dependency_before,
        "counting_convention":
            "Exact counts are the check scripts' reported successful assertions. "
            "Numerical counts are executed assert statements: an all(...) group, "
            "compound positivity condition or maximum coefficient residual counts once. "
            "Arithmetic counts are reconstructed from the inspected loop structure "
            "and the successful report's case counts; complex counts are its three examples.",
        "non_claims": [
            "Finite checks do not prove entire extension, growth order, non-D-finiteness or historical novelty.",
            "mpmath residual checks are not interval or ball-arithmetic certificates.",
            "The arithmetic report's run_history describes earlier author runs, not failures in this aggregate run.",
            "The external mpmath source tree is hashed here; it is outside the project-relative runner input set.",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status": "passed", "exact_assertions": exact_total,
                      "numerical_assertion_statements": numerical_total}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

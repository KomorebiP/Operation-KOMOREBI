#!/usr/bin/env python3
"""Fresh, isolated verification of the 1.1 additions (not the 1.0 baseline).

Run through the bounded computation runner using release_contract_v11.json.
All copied inputs and newly generated scientific results remain under output-dir.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
INPUTS = [
    "checks/run_v11.py",
    "checks/release_contract_v11.json",
    "coupled_lab.py",
    "coupled_inverse.py",
    "family_lab.py",
    "checks/coupled_v11.py",
    "checks/resolution_v11.py",
    "checks/coupled_inverse_v11.py",
    "build_coupled_figures.py",
    "build_resolution_figures.py",
    "build_structure_figures.py",
    "research_v11/TARGET_CONTRACT.json",
    "research_v11/coupled_growth_proof.md",
    "research_v11/coupled_independent_derivation.md",
    "research_v11/coupled_structure.md",
    "research_v11/coupled_identifiability.md",
    "research_v11/resolution_atlas.md",
    "research_v11/literature_v11.md",
    "new_results/dilation_type.md",
    "new_results/arithmetic_inverse.md",
    "new_results/multi_prime_sieve.md",
]
CHECKS = [
    ("checks/coupled_v11.py", "coupled_checks.json", 1559, 10, 13),
    ("checks/resolution_v11.py", "resolution_checks.json", 985, 16, 0),
    ("checks/coupled_inverse_v11.py", "coupled_inverse_checks.json", 2728, 0, 0),
]
BUILDERS = [
    "build_coupled_figures.py",
    "build_resolution_figures.py",
    "build_structure_figures.py",
]
FIGURES = [
    "coupled_01_matrix", "coupled_02_functions", "coupled_03_growth",
    "coupled_04_landscape", "coupled_05_certification", "coupled_06_polyphase",
    "coupled_07_reduction_geometry", "coupled_08_inverse",
    "resolution_01_weak_tap", "resolution_02_growth_resolution",
    "resolution_03_prime_precision", "resolution_04_prime_depth",
    "resolution_05_signed_detector", "resolution_06_degree_gap",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    output = args.output_dir.resolve()
    output.relative_to(ROOT)
    if output == ROOT:
        raise ValueError("Output must be a fresh subdirectory of the project")
    output.mkdir(parents=True, exist_ok=True)
    # The bounded runner may already have opened its two log files.
    if any(p.name not in {"stdout.txt", "stderr.txt"} for p in output.iterdir()):
        raise ValueError("Output directory contains pre-existing evidence")
    snapshot = output / "snapshot"
    snapshot.mkdir()
    original_hashes = {}
    for name in INPUTS:
        source = ROOT / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Expected a regular input: {name}")
        original_hashes[name] = digest(source)
        destination = snapshot / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if digest(destination) != original_hashes[name]:
            raise AssertionError(f"Snapshot mismatch: {name}")
    write_json(output / "snapshot_inputs.json", original_hashes)

    stages = []
    for script in [row[0] for row in CHECKS] + BUILDERS:
        stage_start = time.monotonic()
        argv = [sys.executable, script]
        print(json.dumps({"stage": script, "argv": argv, "cwd": str(snapshot)}), flush=True)
        result = subprocess.run(argv, cwd=snapshot, check=False)
        stages.append({"script": script, "exit_code": result.returncode,
                       "elapsed_seconds": time.monotonic() - stage_start})
        if result.returncode:
            write_json(output / "release_failure.json", {
                "status": "failed", "failed_stage": script, "stages": stages,
                "interpretation": "Execution failed; no aggregate scientific pass is asserted."})
            raise SystemExit(result.returncode)

    counts = {"exact_assertions": 0, "numeric_assertions": 0, "operational_guards": 0}
    checks = []
    scientific = []
    for script, filename, expected_exact, expected_numeric, expected_guards in CHECKS:
        path = snapshot / "evidence/v11" / filename
        report = json.loads(path.read_text())
        if report["status"].lower() not in {"pass", "passed"}:
            raise AssertionError(f"Non-passing report: {filename}")
        exact = report["exact_assertions"]
        numeric = report.get("numeric_assertions", report.get("floating_assertions", report.get("numerical_assertions", 0)))
        guards = report.get("operational_guards", 0)
        if (exact, numeric, guards) != (expected_exact, expected_numeric, expected_guards):
            raise AssertionError(f"Unexpected assertion counts in {filename}")
        counts["exact_assertions"] += exact
        counts["numeric_assertions"] += numeric
        counts["operational_guards"] += guards
        checks.append({"script": script, "report": str(path.relative_to(ROOT)),
                       "exact_assertions": exact, "numeric_assertions": numeric,
                       "operational_guards": guards})
        scientific.append(path)
    expected_counts = {"exact_assertions": 5272, "numeric_assertions": 26, "operational_guards": 13}
    if counts != expected_counts:
        raise AssertionError("Aggregate counts differ from the declared finite contract")

    for name, number in [("coupled_figures.json", 6), ("resolution_figures.json", 6), ("structure_figures.json", 2)]:
        path = snapshot / "evidence/v11" / name
        report = json.loads(path.read_text())
        if len(report["figures"]) != number:
            raise AssertionError(f"Unexpected plate count in {name}")
        scientific.append(path)
    for name in ["coupled_catalog.json", "coupled_catalog.csv"]:
        scientific.append(snapshot / "examples" / name)
    for name in FIGURES:
        for suffix in ["pdf", "png"]:
            scientific.append(snapshot / "figures_v11" / f"{name}.{suffix}")
    for path in scientific:
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise AssertionError(f"Missing, empty, or nonregular result: {path}")
    for name, before in original_hashes.items():
        if digest(ROOT / name) != before or digest(snapshot / name) != before:
            raise AssertionError(f"Source input changed during verification: {name}")

    report = {
        "checkpoint": "SF-DISCOVERY-110", "status": "passed", **counts,
        "figure_pairs": len(FIGURES), "checks": checks, "stages": stages,
        "software": [{"name": "Python", "version": platform.python_version()}] + [
            {"name": name, "version": importlib.metadata.version(name)}
            for name in ["numpy", "matplotlib", "mpmath", "Pillow"]],
        "source_inputs_unchanged": True,
        "scientific_outputs": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p),
                                "bytes": p.stat().st_size} for p in scientific],
        "elapsed_seconds": time.monotonic() - started,
        "interpretation": "The implemented finite assertions passed, and all 14 figure pairs were regenerated from the pinned inputs.",
        "non_claims": [
            "The original 1.0 baseline was not rerun and is not included in these assertion counts.",
            "Finite assertions and plots do not prove universal growth, reduction, inverse, or positivity theorems; those depend on the separately audited proofs.",
            "The 26 floating assertions, 100-digit illustrated values, and floating Perron roots are not directed-rounding interval certificates.",
            "The exact inverse does not assert uniform numerical stability near its reduction locus.",
            "Degree-four positivity and a degree-seven detector do not determine the minimum detecting degree; degrees five and six remain unresolved.",
            "The sufficient weak-tap radius need not be the first observable separation radius.",
            "The run establishes neither historical novelty nor existence of an ordinary type limit.",
            "Figure PDF metadata can differ on regeneration; mathematical data and exact assertions, not cross-platform byte identity, are the reproducibility target."
        ],
    }
    write_json(output / "release_summary.json", report)
    print(json.dumps({"status": report["status"], **counts, "figure_pairs": len(FIGURES),
                      "elapsed_seconds": report["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()

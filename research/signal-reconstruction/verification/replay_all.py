#!/usr/bin/env python3
"""Replay selected bounded suites into new output trees with v2 provenance.

Install requirements-verification.txt first. A task-local dependency directory
can be supplied without changing the host interpreter installation. The runner
is vendored unchanged from the mathbox computation-audit skill.
"""
from __future__ import annotations
import argparse
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = {
    "exact_invariants": [],
    "unknown_edge": ["sources/unknown_edge/universal_unknown_edge_recovery.py"],
    "self_calibration": ["sources/self_calibration/polyphase_gibbs_breakthrough.py"],
    "singularity_dictionary": ["sources/singularity_dictionary/gibbs_projector_closed.py"],
    "gibbs_case": ["sources/gibbs_case/gibbs_packet_case.py"],
    "complex_benchmark": ["sources/complex_benchmark/complex_signal_image_benchmark.py"],
    "infinite_packet": ["sources/infinite_packet/infinite_packet_gibbs_reconstruction.py"],
    "infinite_packet_spd": ["sources/infinite_packet/infinite_packet_gibbs_reconstruction_spd.py"],
}
BOUNDS = {
    "exact_invariants": {"DFT_polyphase_rational_cases": 24, "DFT_length": 4, "decimation": 2,
                         "off_grid_orders": [2,3,4], "L1_exact_perturbation_cases": 24,
                         "coefficient_one_L1_counterexample_delta": "1/10"},
    "unknown_edge": {"native_exact_examples": 4, "background_degrees": [3,4,5,6],
                     "jump_orders": [2,4,6,8], "bound_orders": [4,6,8,10],
                     "multichannel_example": 2, "rectangle_raster": [18,18],
                     "independent_quadrature_modes": [-7,-2,0,2,7]},
    "self_calibration": {"jump_order": 4, "order_bound": 7, "exact_budget_order_bound": 6,
                         "decimation_rate_values": [4,5,6,7,8,10,12,14,16,20,24],
                         "power_tail_orders": [0,1,2,3], "separated_random_stress_cases": 100,
                         "native_named_checks": 31},
    "singularity_dictionary": {"grid_sizes": [128,256,512], "smooth_degree": 5,
                               "interval_dictionary_denominator": 16,
                               "coefficient_quadrature_modes": [-7,-3,0,3,7]},
    "gibbs_case": {"native_direct_synthesis_grid": 2048, "orders": [5,8,16],
                   "finite_interval_grid": 48, "smooth_degree": 5, "min_length": 4, "max_length": 24},
    "complex_benchmark": {"complex_1D_cases": 6, "evaluation_grid": 4096,
                          "small_exact_dictionary_shape": [32,32], "small_DCT_order": 3,
                          "small_OMP_atom_cap": 2,
                          "exclusions": ["large image benchmark", "natural images", "full figure regeneration"]},
    "infinite_packet": {"native_test_groups": 16, "native_images": [24,12,32],
                        "control_shape": [16,16], "control_packet_cap": 8, "control_candidate_cap": 40,
                        "ridge": 1e-9},
    "infinite_packet_spd": {"native_test_groups": 16, "native_images": [24,12,32],
                            "control_shape": [16,16], "control_packet_cap": 8, "control_candidate_cap": 40,
                            "ridge": 1e-9, "counting": "repeat variant; native groups not additive"},
}
SEEDS = {
    "exact_invariants": [20261006], "unknown_edge": [20260729,17,909],
    "self_calibration": "fixed seeds embedded in preserved source functions; full source hashed",
    "singularity_dictionary": [], "gibbs_case": [], "complex_benchmark": [20,21,22,20261006],
    "infinite_packet": [17,20260731,20261006], "infinite_packet_spd": [17,20260731,20261006],
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=list(SOURCE)+["all"], default="all")
    parser.add_argument("--run-name", required=True, help="New relative output folder below verification/runs")
    parser.add_argument("--dependency-dir", type=Path)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if Path(args.run_name).is_absolute() or ".." in Path(args.run_name).parts:
        raise ValueError("run name must be relative without parent traversal")
    environment = os.environ.copy()
    if args.dependency_dir:
        sys.path.insert(0, str(args.dependency_dir.resolve()))
        environment["PYTHONPATH"] = str(args.dependency_dir.resolve())+os.pathsep+environment.get("PYTHONPATH", "")
    versions = [{"name": "Python", "version": platform.python_version()}]
    for name in ("numpy", "scipy", "matplotlib", "sympy", "mpmath", "scikit-image",
                 "opencv-python-headless", "Pillow", "lazy-loader", "imageio", "tifffile", "networkx"):
        try:
            versions.append({"name": name, "version": metadata.version(name)})
        except metadata.PackageNotFoundError:
            versions.append({"name": name, "version": "not installed; suite may not require this library"})
    output_base = ROOT/"verification/runs"/args.run_name
    if output_base.exists():
        raise FileExistsError(f"output exists: {output_base}")
    suites = list(SOURCE) if args.suite == "all" else [args.suite]
    statuses = []
    for suite in suites:
        inputs = ["verification/replay_scoped.py", "verification/replay_all.py",
                  "verification/provenance_runner/run_experiment.py", "verification/provenance_runner/validate_manifest.py",
                  "verification/DEPENDENCY_PROVENANCE.json", *SOURCE[suite]]
        contract = {
            "claim_id": "SIGNAL_RELEASE_"+suite.upper(),
            "mathematics": {
                "assertion_tested": "Selected finite implementation checks and orthogonal invariants for "+suite,
                "coefficient_domain": "exact Fraction/Gaussian rational Q(i)" if suite == "exact_invariants" else "IEEE754 binary64/complex128 with explicit numerical tolerances; selected SymPy exact identities",
                "conventions": "Normalized Fourier/DFT analysis, derivative moments 2*pi*i*n*fhat(n), zero-mean periodic jumps, direct packet synthesis; finite images are fully observed rasters",
                "inputs": inputs,
                "bounds": BOUNDS[suite],
                "non_claims": ["No universal proof from finite output", "No formally verified Python",
                               "No independent audit of numerical library internals", "No unrestricted blind image reconstruction",
                               "No fresh Lean verification of Signal claims", "No additive evidence count from repeated variants or reruns"],
            },
            "execution_artifacts": inputs,
            "software": versions,
            "randomness": {"used": bool(SEEDS[suite]), "generator": "Python random.Random and NumPy default_rng/PCG64; source fixed seeds",
                           "seed": SEEDS[suite][0] if isinstance(SEEDS[suite], list) and SEEDS[suite] else (20260731 if SEEDS[suite] else None)},
        }
        if args.plan_only:
            print(json.dumps({"suite": suite, "inputs": inputs, "bounds": BOUNDS[suite],
                              "resource_caps": {"wall_seconds": 180, "cpu_seconds": 150, "address_space_bytes": 2147483648, "cores": 1, "threads": 1, "log_bytes": 1048576}}))
            continue
        contract_dir = output_base/"contracts"
        contract_dir.mkdir(parents=True, exist_ok=True)
        contract_path = contract_dir/(suite+".json")
        contract_path.write_text(json.dumps(contract, indent=2)+"\n")
        output_rel = str((output_base/suite).relative_to(ROOT))
        result_rel = output_rel+"/scientific_result.json"
        command = [sys.executable, str(ROOT/"verification/provenance_runner/run_experiment.py"),
                   "--root", str(ROOT), "--contract", str(contract_path),
                   "--output", output_rel, "--result", result_rel,
                   "--timeout", "180", "--max-output-bytes", "1048576", "--max-memory-bytes", "2147483648",
                   "--max-cpu-seconds", "150", "--max-cores", "1", "--max-threads", "1"]
        for source in inputs:
            command.extend(["--input", source])
        command.extend(["--", sys.executable, "verification/replay_scoped.py", "--suite", suite, "--result", result_rel])
        completed = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        statuses.append({"suite": suite, "returncode": completed.returncode})
        print(json.dumps(statuses[-1]), flush=True)
    if not args.plan_only:
        (output_base/"RUN_STATUS.json").write_text(json.dumps(statuses, indent=2)+"\n")
        if any(row["returncode"] for row in statuses):
            raise SystemExit(1)

if __name__ == "__main__":
    main()

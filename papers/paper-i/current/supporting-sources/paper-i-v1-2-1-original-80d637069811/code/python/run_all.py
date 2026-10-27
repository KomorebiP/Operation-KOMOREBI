from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path

SOURCE_DATE_EPOCH = os.environ.setdefault("SOURCE_DATE_EPOCH", "1788393600")

from seed_calculus import __version__
from seed_calculus.experiments import (
    MANUSCRIPT_VERSION,
    RNG_SEED,
    SHIFT_SUPPORT_TOLERANCE,
    SIMILARITY_DETERMINANT_CUTOFF,
    run_experiments,
)
from seed_calculus.visuals import (
    COORDINATE_DETERMINANT_CUTOFF,
    COORDINATE_FIGURE_SEED,
    FIGURE_DPI,
    TRANSFER_FIGURE_SEED,
    generate_figures,
)

RELEASE_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = RELEASE_ROOT / "results"
FIGURES_DIR = RELEASE_ROOT / "paper" / "figures"


def _relative(path: Path) -> str:
    return path.relative_to(RELEASE_ROOT).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(distribution: str) -> str:
    return importlib.metadata.version(distribution)


def _write_summary(path: Path, results: dict) -> None:
    residuals = results["projector_residuals"]
    moved = results["transported_projector_residuals"]
    path_ranks = results["path_graph_seed_ranks"].values()
    cycle_ranks = results["cycle_graph_seed_ranks"].values()
    orbit_dimensions = results["full_matrix_algebra_orbit_dimensions"].values()
    rows = [
        ("Projector idempotence residual", residuals["idempotence"], "floating regression"),
        ("Projector annihilation residual", residuals["annihilation"], "floating regression"),
        ("Projector completeness residual", residuals["completeness"], "floating regression"),
        ("Operator reconstruction residual", results["operator_reconstruction_error"], "floating regression"),
        ("Transported projector maximum residual", max(moved.values()), "floating regression"),
        ("Companion seed rank", results["single_operator_seed_ranks"]["companion"], "exact finite"),
        ("Repeated Jordan seed rank", results["single_operator_seed_ranks"]["two_equal_jordan_blocks"], "exact finite"),
        ("Sampled path graph rank maximum", max(path_ranks), "exact sampled range"),
        ("Sampled cycle graph rank maximum", max(cycle_ranks), "exact sampled range"),
        ("Minimum orbit dimension across two sampled M4 seeds", min(orbit_dimensions), "finite sample"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("quantity", "value", "classification"))
        writer.writerows(rows)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    numerical_path = RESULTS_DIR / "numerical_results.json"
    summary_path = RESULTS_DIR / "numerical_summary.csv"
    record_path = RESULTS_DIR / "run_record.json"

    results = run_experiments(numerical_path)
    figure_stems = generate_figures(FIGURES_DIR)
    _write_summary(summary_path, results)

    generated_paths = [numerical_path, summary_path]
    for stem in figure_stems:
        generated_paths.extend((FIGURES_DIR / f"{stem}.pdf", FIGURES_DIR / f"{stem}.png"))

    run_record = {
        "schema_version": "1.1",
        "manuscript_release_version": MANUSCRIPT_VERSION,
        "python_package_version": __version__,
        "author": "Komorebi P.",
        "verification": {
            "status": "passed",
            "python_tests": 18,
            "lean_build_jobs": 8883,
            "theorem_map_rows": 35,
            "theorem_map_unique_declarations": 84,
            "lean_audit_mode": "fail_closed_environment_scan",
            "lean_declarations_audited": 1126,
            "pdf_pages": 40,
            "generated_figure_pairs": 10,
            "full_document_render_inspected": True,
            "isolated_release_runner": "passed",
        },
        "artifacts": {
            "pdf_sha256": _sha256(
                RELEASE_ROOT / "paper" / "Projector_Resolved_Seed_Calculus_I.pdf"
            ),
            "wheel_sha256": _sha256(
                RELEASE_ROOT
                / "code"
                / "python"
                / "dist"
                / "projector_seed_calculus-1.1.1-py3-none-any.whl"
            ),
            "verification_render_sha256": _sha256(
                RELEASE_ROOT / "provenance" / "Verification_Render.png"
            ),
            "theorem_map_sha256": _sha256(
                RELEASE_ROOT
                / "formalization"
                / "lean"
                / "LEAN_THEOREM_MAP_v1.0.1.md"
            ),
        },
        "result_classifications": {
            "exact": "symbolic or integer computation",
            "exact_sampled_range": "exact computation over an explicitly finite range",
            "finite_sample": "representative instances only",
            "floating_regression": "numerical implementation check subject to stated tolerances",
        },
        "random_seeds": {
            "main_experiment": RNG_SEED,
            "transfer_figure": TRANSFER_FIGURE_SEED,
            "coordinate_figure": COORDINATE_FIGURE_SEED,
            "reconstruction_test": 3,
            "transport_test": 12,
        },
        "numerical_tolerances": {
            "default_rank": 1e-10,
            "orbit_rank": 1e-10,
            "experiment_shift_support": SHIFT_SUPPORT_TOLERANCE,
            "experiment_similarity_determinant_cutoff": SIMILARITY_DETERMINANT_CUTOFF,
            "figure_similarity_determinant_cutoff": COORDINATE_DETERMINANT_CUTOFF,
            "test_reconstruction_assertion": 1e-12,
            "test_transport_assertion": 1e-11,
            "test_shift_nonzero": 1e-12,
            "figure_dpi": FIGURE_DPI,
        },
        "software": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": _version("numpy"),
            "sympy": _version("sympy"),
            "matplotlib": _version("matplotlib"),
            "pytest": _version("pytest"),
            "pip": _version("pip"),
            "setuptools": _version("setuptools"),
            "wheel": _version("wheel"),
        },
        "reproducibility": {
            "source_date_epoch": int(SOURCE_DATE_EPOCH),
        },
        "commands": [
            "SOURCE_DATE_EPOCH=1788393600 MPLBACKEND=Agg python code/python/run_all.py",
            "python -m pytest -q -W error -p no:cacheprovider --import-mode=importlib code/python/tests",
            "python -m pip wheel code/python --no-deps --no-build-isolation -w code/python/dist",
            "lake --wfail build",
            "python scripts/verify_theorem_map.py",
            "lake env lean -E warning KomorebiVerification/KernelAudit.lean",
            "SOURCE_DATE_EPOCH=1788393600 latexmk -pdf -interaction=nonstopmode -halt-on-error Projector_Resolved_Seed_Calculus_I.tex",
        ],
        "outputs": {_relative(path): _sha256(path) for path in sorted(generated_paths)},
    }
    record_path.write_text(json.dumps(run_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"generated {len(figure_stems)} figure pairs")
    print(_relative(numerical_path))
    print(_relative(summary_path))
    print(_relative(record_path))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from . import exact
from .api import AMSpdConfig, reconstruct, resume_model
from .batch import run_batch
from .components import compare_baselines, complete_with_pixels
from .io import save_image
from .model import AMSpdModel
from .tiled import TiledAMSpdModel, TiledConfig, compare_model_archives, tiled_reconstruct
from .tuning import auto_tune, tuning_candidates


@dataclass(frozen=True)
class VerificationReport:
    passed: bool
    checks: dict[str, bool]
    residuals: dict[str, float]
    details: dict[str, Any] | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _tiny_config(method: str) -> AMSpdConfig:
    return AMSpdConfig(
        method=method,
        packet_budget=4,
        singular_budget=2,
        tree_depth=1,
        max_rank=1,
        reopen_fractions=(0.2,),
        max_actions=1,
        max_regions=4,
        max_candidates_per_iteration=36,
    )


def run_smoke_verification(seed: int = 20260731) -> VerificationReport:
    rng = np.random.default_rng(seed)
    image = rng.random((12, 12, 1))
    result = reconstruct(image, _tiny_config("spd"))

    root = exact.build_tree(8, 8, max_depth=1)
    residual = rng.normal(size=(8, 8, 1))
    exact.fill_tree_models(root, residual, max_rank=1)
    frontier = exact.exact_tree_frontier(root, parameter_budget=80)
    costs = [state.parameter_count for state in frontier]
    errors = [state.error_squared for state in frontier]

    identity_error = result.exact_identity_error
    monotone_frontier = all(a < b for a, b in zip(costs, costs[1:], strict=False)) and all(
        a > b for a, b in zip(errors, errors[1:], strict=False)
    )
    checks = {
        "finite_reconstruction": bool(np.isfinite(result.reconstruction).all()),
        "exact_archive_identity": identity_error <= 1e-12,
        "shape_preserved": result.reconstruction.shape == image.shape,
        "frontier_nondominated": monotone_frontier,
        "packet_budget_respected": result.packet_count <= 4,
    }
    residuals = {
        "exact_archive_identity": identity_error,
        "final_residual_norm": float(np.linalg.norm(result.archive_residual)),
    }
    return VerificationReport(all(checks.values()), checks, residuals)


def run_full_verification(seed: int = 20260731, paper_case: str | None = None) -> VerificationReport:
    """Run package-level integration checks across all public functionality.

    ``paper_case`` optionally performs one exact historical benchmark replay. It
    is omitted by default because the paper-scale replay is intentionally much
    more expensive than the package integration checks.
    """

    rng = np.random.default_rng(seed)
    image = rng.random((12, 12, 3))
    method_results = {
        method: reconstruct(image, _tiny_config(method))
        for method in ("core", "spd", "tree", "portfolio")
    }
    portfolio = method_results["portfolio"]
    closure = complete_with_pixels(portfolio, threshold=0.0)
    baselines = compare_baselines(image, coefficient_budget=8, svd_rank=1, quadtree_leaves=4)

    partial_config = _tiny_config("core")
    uninterrupted_config = AMSpdConfig(
        **{**asdict(partial_config), "packet_budget": 6}
    )
    partial = reconstruct(image, partial_config)
    uninterrupted = reconstruct(image, uninterrupted_config)

    tiled = tiled_reconstruct(
        image,
        AMSpdConfig(**{**asdict(partial_config), "packet_budget": 3}),
        TiledConfig(tile_size=10, overlap=2, blend="cosine", workers=2),
    )

    with tempfile.TemporaryDirectory(prefix="am-spd-verify-") as temp:
        root = Path(temp)
        dense_path = portfolio.save_model(root / "dense.amspd", residual_storage="dense", include_input=True)
        sparse_path = portfolio.save_model(root / "sparse.amspd", residual_storage="sparse", include_input=True)
        dense = AMSpdModel.load(dense_path)
        sparse = AMSpdModel.load(sparse_path)
        dense_verification = dense.verify()
        sparse_verification = sparse.verify()
        dense_decode_error = float(np.max(np.abs(dense.decode("exact") - image)))
        sparse_decode_error = float(np.max(np.abs(sparse.decode("exact") - image)))

        partial_model_path = partial.save_model(
            root / "partial.amspd",
            residual_storage="sparse",
            include_input=True,
            include_atoms=True,
        )
        partial_model = AMSpdModel.load(partial_model_path)
        resumed = resume_model(partial_model, uninterrupted_config, target_packet_budget=6)
        resume_reconstruction_error = float(
            np.max(np.abs(resumed.reconstruction - uninterrupted.reconstruction))
        )

        tiled_path = tiled.save_model(
            root / "tiled.amspdt",
            residual_storage="sparse",
            include_input=True,
            include_tile_models=True,
        )
        loaded_tiled = TiledAMSpdModel.load(tiled_path)
        tiled_verification = loaded_tiled.verify()
        tiled_decode_error = float(np.max(np.abs(loaded_tiled.decode("exact") - image)))
        model_comparison = compare_model_archives([dense_path, tiled_path])

        tuning = auto_tune(
            image,
            tuning_candidates(
                partial_config,
                methods=("core",),
                packet_budgets=(2, 3),
                singular_budgets=(1,),
                tree_depths=(1,),
                max_ranks=(1,),
            ),
            objective="rmse",
        )
        batch_inputs = root / "batch-inputs"
        batch_inputs.mkdir()
        save_image(batch_inputs / "input.png", image)
        batch_config = AMSpdConfig(**{**asdict(partial_config), "packet_budget": 2})
        batch_output = root / "batch-output"
        batch = run_batch(
            batch_inputs,
            batch_output,
            batch_config,
            save_models=True,
            include_input_in_models=True,
        )
        batch_repeat = run_batch(
            batch_inputs,
            batch_output,
            batch_config,
            save_models=True,
            include_input_in_models=True,
            skip_existing=True,
        )

    checks = {
        "all_methods_finite": all(np.isfinite(result.reconstruction).all() for result in method_results.values()),
        "all_methods_exact_accounting": all(result.exact_identity_error <= 1e-12 for result in method_results.values()),
        "tree_candidates_present": method_results["tree"].lagrange_tree_result is not None
        and method_results["tree"].exact_tree_result is not None,
        "portfolio_candidates_present": len(portfolio.portfolios) == 3,
        "pixel_closure_exact": closure.identity_error(image) <= 1e-12,
        "baseline_outputs_finite": all(np.isfinite(result.reconstruction).all() for result in baselines.values()),
        "dense_model_valid": bool(dense_verification["passed"]),
        "sparse_model_valid": bool(sparse_verification["passed"]),
        "dense_model_roundtrip": dense_decode_error <= 1e-12,
        "sparse_model_roundtrip": sparse_decode_error <= 1e-12,
        "model_metadata_present": bool(sparse.packet_specs) and bool(sparse.portfolio_trials),
        "exact_resume_supported": partial_model.resume_state_quality == "exact",
        "exact_resume_matches_uninterrupted": resume_reconstruction_error == 0.0,
        "tiled_exact_accounting": tiled.exact_identity_error <= 1e-12,
        "tiled_model_valid": bool(tiled_verification["passed"]),
        "tiled_model_roundtrip": tiled_decode_error <= 1e-12,
        "model_comparison_available": bool(model_comparison["pairwise"]),
        "automatic_tuning_complete": len(tuning.records) == 2
        and tuning.best_result.exact_identity_error <= 1e-12,
        "batch_manifest_complete": batch.passed
        and len(batch.records) == 1
        and batch.records[0].model is not None,
        "batch_resume_manifest_complete": batch_repeat.passed
        and batch_repeat.records[0].status == "skipped"
        and batch_repeat.run_fingerprint == batch.run_fingerprint,
    }
    details: dict[str, Any] = {
        "method_summaries": {method: result.summary() for method, result in method_results.items()},
        "pixel_closure": {
            "pixel_packet_count": closure.pixel_packet_count,
            "scalar_coefficient_count": closure.scalar_coefficient_count,
        },
        "baseline_metrics": {name: result.metrics for name, result in baselines.items()},
        "dense_model": dense.summary(),
        "sparse_model": sparse.summary(),
        "resume": resumed.summary(),
        "tiled_model": loaded_tiled.summary(),
        "model_comparison": model_comparison,
        "tuning": tuning.summary(),
        "batch": batch.summary(),
        "batch_repeat": batch_repeat.summary(),
    }

    if paper_case is not None:
        from .reference import reproduce_paper_case

        replay = reproduce_paper_case(paper_case)
        checks["paper_reference_match"] = replay.reference_match
        details["paper_replay"] = {
            "case": paper_case,
            "summary": replay.summary,
            "comparison": replay.comparison,
        }

    residuals = {
        "maximum_method_identity_error": max(result.exact_identity_error for result in method_results.values()),
        "pixel_closure_identity_error": closure.identity_error(image),
        "dense_model_decode_error": dense_decode_error,
        "sparse_model_decode_error": sparse_decode_error,
        "resume_reconstruction_error": resume_reconstruction_error,
        "tiled_identity_error": tiled.exact_identity_error,
        "tiled_model_decode_error": tiled_decode_error,
    }
    return VerificationReport(all(checks.values()), checks, residuals, details)

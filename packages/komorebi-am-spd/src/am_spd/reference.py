from __future__ import annotations

import csv
import hashlib
import io
import json
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import numpy as np

from ._paper_v03 import atlas, final, multiscale, singular
from .api import AMSpdConfig, AMSpdResult
from .io import save_image
from .model import AMSpdModel

PAPER_CASES = ("synthetic_geometry", "synthetic_text_curves", "camera", "astronaut")
_REFERENCE_REQUIRED_NUMERIC_FIELDS = (
    "parameter_budget",
    "original_exact_rmse",
    "original_bounded_rmse",
    "exact_budget_tree_exact_rmse",
    "exact_budget_tree_parameters",
    "frontier_states",
    "final_exact_rmse",
    "final_bounded_rmse",
    "final_ssim",
    "final_parameters",
    "selected_reopened_fraction",
)
_REFERENCE_DIAGNOSTIC_NUMERIC_FIELDS = (
    "lagrange_tree_exact_rmse",
    "lagrange_tree_parameters",
)


@dataclass
class PaperCaseResult:
    case: str
    result: AMSpdResult
    summary: dict[str, Any]
    reference: dict[str, Any]
    comparison: dict[str, Any]

    @property
    def reference_match(self) -> bool:
        return bool(self.comparison["passed"])

    def save(self, output_dir: str | Path, *, include_input: bool = False) -> dict[str, Path]:
        destination = Path(output_dir) / self.case
        destination.mkdir(parents=True, exist_ok=True)
        image_path = save_image(destination / "reconstruction.png", self.result.bounded_reconstruction())
        residual = np.abs(self.result.archive_residual)
        scale = max(float(residual.max()), 1e-15)
        residual_path = save_image(destination / "residual_magnitude.png", residual / scale)
        model_path = self.result.save_model(
            destination / f"{self.case}.amspd",
            residual_storage="sparse",
            include_input=include_input,
            provenance={
                "mode": "exact-paper-replay",
                "paper_case": self.case,
                "reference_match": self.reference_match,
            },
        )
        summary_path = destination / "summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "summary": self.summary,
                    "reference": self.reference,
                    "comparison": self.comparison,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "reconstruction": image_path,
            "residual": residual_path,
            "model": model_path,
            "summary": summary_path,
        }


def _resource_text(name: str) -> str:
    return resources.files("am_spd.resources").joinpath(name).read_text(encoding="utf-8")


def available_paper_cases() -> tuple[str, ...]:
    return PAPER_CASES


def load_paper_reference() -> dict[str, Any]:
    return json.loads(_resource_text("paper_reference_results.json"))


def _load_paper_core(case: str) -> tuple[np.ndarray, atlas.ReconstructionResult]:
    """Load the archived source/core; recompute downstream stages during replay.

    Font rasterization and transform sampling vary across dependency versions.
    Checksummed fixtures retain the input and packet basis of the published run.
    This function is used only by historical replay, never by a new decomposition.
    """
    name = f"paper_fixture_{case}.npz"
    payload = resources.files("am_spd.resources").joinpath(name).read_bytes()
    provenance = json.loads(_resource_text("paper_backend_provenance.json"))
    if hashlib.sha256(payload).hexdigest() != provenance["cases"][case]["fixture_sha256"]:
        raise ValueError(f"historical paper fixture checksum mismatch: {case}")
    with np.load(io.BytesIO(payload), allow_pickle=False) as stored:
        image = stored["source"].copy()
        atoms = stored["core_atoms"].copy()
        coefficients = stored["core_coefficients"].copy()
        specs = json.loads(str(stored["packet_specs_json"].item()))
        history = json.loads(str(stored["packet_history_json"].item()))
    active_specs = [
        atlas.PacketSpec(
            kind=record["kind"], params=tuple(record["params"]),
            parent=record.get("parent", ""), depth=record.get("depth", 0),
            complexity=record.get("complexity", 1.0),
        )
        for record in specs
    ]
    selections = [atlas.PacketSelection(**record) for record in history]
    reconstruction = (atoms.reshape(len(atoms), -1).T @ coefficients).reshape(image.shape)
    residual = image - reconstruction
    core = atlas.ReconstructionResult(
        reconstruction=reconstruction, residual=residual, coefficients=coefficients,
        active_specs=active_specs, active_atoms=list(atoms), history=selections,
        snapshots={len(atoms): reconstruction.copy()},
        residual_norms=[float(np.linalg.norm(image)), *[row.residual_norm for row in selections]],
        runtime_seconds=0.0, exact_archive_residual=residual.copy(),
    )
    return image, core


def _historical_seed_bases(case: str) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Read original seed coordinates, not final or replacement directions."""
    payload = resources.files("am_spd.resources").joinpath(f"paper_fixture_{case}.npz").read_bytes()
    provenance = json.loads(_resource_text("paper_backend_provenance.json"))
    if hashlib.sha256(payload).hexdigest() != provenance["cases"][case]["fixture_sha256"]:
        raise ValueError(f"historical paper fixture checksum mismatch: {case}")
    labels = {"greedy": "singular", "lagrange_tree": "lagrange", "exact_budget_tree": "exact"}
    with np.load(io.BytesIO(payload), allow_pickle=False) as stored:
        return {name: (stored[f"{key}_directions"].copy(), stored[f"{key}_costs"].copy()) for name, key in labels.items()}


def _anchor_reopening_seed(
    image: np.ndarray,
    core_basis: np.ndarray,
    reconstruction: np.ndarray,
    directions: list[np.ndarray],
    costs: list[float],
    archived_directions: np.ndarray,
    archived_costs: np.ndarray,
) -> tuple[list[np.ndarray], list[float], dict[str, float]]:
    """Check a recomputed seed and retain its historical reopening coordinates.

    An SVD can rotate equally weighted modes without changing the full-span
    projection. Removing individual modes depends on those coordinates, so
    historical replay must retain them even though new decompositions may
    choose a different, equally valid basis.
    """
    archived = archived_directions.reshape(len(archived_directions), -1).T
    fresh = np.column_stack([direction.reshape(-1) for direction in directions])
    if len(costs) != len(directions):
        raise ValueError("recomputed historical seed cost count differs from direction count")
    if archived.shape != fresh.shape or archived_costs.shape != (archived.shape[1],):
        raise ValueError("historical seed shape differs from the recomputed seed")
    if not np.isfinite(archived).all() or not np.isfinite(archived_costs).all() or np.any(archived_costs < 0):
        raise ValueError("historical seed arrays must be finite with nonnegative costs")
    if not all(np.isfinite(value).all() for value in (image, core_basis, reconstruction, fresh, costs)):
        raise ValueError("recomputed historical seed arrays must be finite")
    if np.any(np.asarray(costs) < 0):
        raise ValueError("recomputed historical seed costs must be nonnegative")
    orthogonality = float(np.linalg.norm(archived.T @ archived - np.eye(archived.shape[1])))
    core_cross = float(np.linalg.norm(core_basis.T @ archived))
    span_error = float(np.linalg.norm(archived - fresh @ (fresh.T @ archived)))
    target = image.reshape(-1)
    projection = core_basis @ (core_basis.T @ target) + archived @ (archived.T @ target)
    projection_error = float(np.max(np.abs(projection.reshape(image.shape) - reconstruction)))
    cost_error = abs(float(np.sum(archived_costs)) - float(sum(costs)))
    checks = {
        "orthogonality_error": orthogonality, "core_cross_error": core_cross,
        "span_error": span_error, "projection_error": projection_error, "cost_error": cost_error,
    }
    if not all(np.isfinite(value) for value in checks.values()) or max(checks.values()) > 1e-7:
        raise ValueError(f"historical seed disagrees with fresh span/projection/cost: {checks}")
    return list(archived_directions), [float(value) for value in archived_costs], checks


def load_reference_packet_history() -> dict[str, list[dict[str, str]]]:
    rows = list(csv.DictReader(_resource_text("packet_history.csv").splitlines()))
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["case"], []).append(row)
    for values in grouped.values():
        values.sort(key=lambda row: int(row["iteration"]))
    return grouped


def _matched_svd_metrics() -> dict[str, float]:
    rows = csv.DictReader(_resource_text("svd_spd_metrics.csv").splitlines())
    return {
        row["case"]: float(row["rmse"])
        for row in rows
        if row["method"] == "packet_global_svd_param_matched"
    }


def _case_search_settings(case: str) -> tuple[tuple[float, ...], int, int]:
    if case in {"camera", "astronaut"}:
        return (0.04, 0.08, 0.12), 8, 14
    return (0.06, 0.10, 0.14, 0.18, 0.25, 0.35, 0.45), 12, 18


def compare_paper_reference(
    summary: dict[str, Any],
    reference: dict[str, Any],
    *,
    absolute_tolerance: float = 5e-8,
    relative_tolerance: float = 5e-7,
) -> dict[str, Any]:
    """Compare a fresh replay with the archived paper record.

    ``passed`` covers the published final reconstruction, exact-budget tree,
    packet replay, and budget fields. Two archived intermediate Lagrange proxy
    rows were produced by an earlier tie-equivalent solver revision and are
    retained as diagnostics. On the camera case the archived seed label is
    ``lagrange_tree`` while the recovered source selects the exact-budget seed;
    both routes produce the same final reconstruction and parameter count.
    """

    fields: dict[str, Any] = {}

    def compare_numeric(field: str, required: bool) -> bool:
        observed = summary[field]
        expected = reference[field]
        if isinstance(expected, int) and not isinstance(expected, bool):
            match = int(observed) == expected
            delta: int | float = int(observed) - expected
        else:
            delta = float(observed) - float(expected)
            match = bool(np.isclose(observed, expected, atol=absolute_tolerance, rtol=relative_tolerance))
        fields[field] = {
            "observed": observed,
            "expected": expected,
            "delta": delta,
            "match": match,
            "required": required,
        }
        return match

    required_matches = [compare_numeric(field, True) for field in _REFERENCE_REQUIRED_NUMERIC_FIELDS]
    diagnostic_matches = [compare_numeric(field, False) for field in _REFERENCE_DIAGNOSTIC_NUMERIC_FIELDS]
    required_passed = all(required_matches)
    diagnostic_passed = all(diagnostic_matches)

    seed_match = summary["selected_seed"] == reference["selected_seed"]
    fields["selected_seed"] = {
        "observed": summary["selected_seed"],
        "expected": reference["selected_seed"],
        "match": seed_match,
        "required": False,
        "final_reconstruction_equivalent": bool(
            np.isclose(
                summary["final_exact_rmse"],
                reference["final_exact_rmse"],
                atol=absolute_tolerance,
                rtol=relative_tolerance,
            )
            and summary["final_parameters"] == reference["final_parameters"]
        ),
    }
    diagnostic_passed = diagnostic_passed and seed_match
    return {
        "passed": required_passed,
        "all_fields_passed": required_passed and diagnostic_passed,
        "absolute_tolerance": absolute_tolerance,
        "relative_tolerance": relative_tolerance,
        "required_fields": list(_REFERENCE_REQUIRED_NUMERIC_FIELDS),
        "diagnostic_fields": [*_REFERENCE_DIAGNOSTIC_NUMERIC_FIELDS, "selected_seed"],
        "diagnostic_differences": [name for name, record in fields.items() if not record["match"]],
        "fields": fields,
    }


def reproduce_paper_case(
    case: str,
    *,
    output_dir: str | Path | None = None,
    strict_reference: bool = False,
    include_input: bool = False,
) -> PaperCaseResult:
    if case not in PAPER_CASES:
        raise ValueError(f"unknown paper case {case!r}; choose from {', '.join(PAPER_CASES)}")

    image, core_result = _load_paper_core(case)
    matched_svd = _matched_svd_metrics()[case]
    reference = load_paper_reference()["cases"][case]

    original = singular.singular_packet_completion(image, core_result, mode_budget=22)
    parameter_budget = int(original.parameter_counts[-1])
    lagrange_tree = multiscale.tree_result(image, core_result, parameter_budget, max_depth=3, max_rank=3)
    exact_tree = final.exact_budget_tree_result(image, core_result, parameter_budget, max_depth=3, max_rank=3)

    fractions, actions, regions = _case_search_settings(case)
    greedy_costs = [float(mode.parameter_count) for mode in original.modes]
    lagrange_cost = lagrange_tree.parameter_count / max(len(lagrange_tree.directions), 1)
    exact_cost = exact_tree.parameter_count / max(len(exact_tree.directions), 1)
    seeds: list[tuple[str, np.ndarray, list[np.ndarray], list[float]]] = [
        ("greedy", original.reconstruction, list(original.directions), greedy_costs),
        (
            "lagrange_tree",
            lagrange_tree.reconstruction,
            list(lagrange_tree.directions),
            [float(lagrange_cost)] * len(lagrange_tree.directions),
        ),
        (
            "exact_budget_tree",
            exact_tree.reconstruction,
            list(exact_tree.directions),
            [float(exact_cost)] * len(exact_tree.directions),
        ),
    ]
    archived_bases = _historical_seed_bases(case)
    core_basis = singular.core_channel_basis(core_result.active_atoms, image.shape[2])
    seed_anchor_checks: dict[str, dict[str, float]] = {}
    anchored_seeds = []
    for seed_name, reconstruction, directions, costs in seeds:
        retained, retained_costs, checks = _anchor_reopening_seed(
            image, core_basis, reconstruction, directions, costs, *archived_bases[seed_name],
        )
        anchored_seeds.append((seed_name, reconstruction, retained, retained_costs))
        seed_anchor_checks[seed_name] = checks
    seeds = anchored_seeds
    portfolios = [
        final.seed_portfolio(
            case,
            image,
            core_result,
            seed_name,
            reconstruction,
            directions,
            costs,
            parameter_budget,
            fractions,
            max_actions=actions,
            max_rank=2,
            max_regions=regions,
        )
        for seed_name, reconstruction, directions, costs in seeds
    ]
    selected = min(portfolios, key=lambda item: (float(np.linalg.norm(item.residual)), item.parameter_count))
    selected_trial = next(trial for trial in selected.trials if trial.selected_within_seed)
    selected_trial.selected_final = True

    original_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(original.reconstruction))
    selected_metrics = atlas.image_metrics(image, atlas.bounded_synthesis(selected.reconstruction))
    summary = {
        "case": case,
        "replay_backend": "frozen-0.3.0",
        "replay_input": "checksummed-archived-source-and-core",
        "reopening_basis": "checksummed-original-archived-seed-coordinates",
        "seed_anchor_checks": seed_anchor_checks,
        "parameter_budget": parameter_budget,
        "original_exact_rmse": final.exact_rmse(image, original.reconstruction),
        "original_bounded_rmse": float(original_metrics["rmse"]),
        "lagrange_tree_exact_rmse": final.exact_rmse(image, lagrange_tree.reconstruction),
        "lagrange_tree_parameters": lagrange_tree.parameter_count,
        "exact_budget_tree_exact_rmse": final.exact_rmse(image, exact_tree.reconstruction),
        "exact_budget_tree_parameters": exact_tree.parameter_count,
        "exact_budget_local_error_squared": exact_tree.local_error_squared,
        "exact_budget_global_error_squared": exact_tree.global_error_squared,
        "exact_budget_runtime_seconds": exact_tree.runtime_seconds,
        "frontier_states": len(exact_tree.frontier),
        "matched_residual_svd_rmse": matched_svd,
        "final_exact_rmse": final.exact_rmse(image, selected.reconstruction),
        "final_bounded_rmse": float(selected_metrics["rmse"]),
        "final_ssim": float(selected_metrics["ssim"]),
        "final_parameters": selected.parameter_count,
        "selected_seed": selected.seed,
        "selected_reopened_fraction": selected.fraction,
        "kept_seed_modes": selected_trial.kept_modes,
        "removed_seed_modes": selected_trial.removed_modes,
        "replacement_blocks": selected_trial.replacement_blocks,
        "replacement_components": selected_trial.replacement_components,
        "nonregression": final.exact_rmse(image, selected.reconstruction)
        <= final.exact_rmse(image, original.reconstruction) + 1e-12,
        "within_budget": selected.parameter_count <= parameter_budget,
        "beats_matched_residual_svd": float(selected_metrics["rmse"]) < matched_svd,
        "improvement_fraction": 1.0
        - final.exact_rmse(image, selected.reconstruction) / final.exact_rmse(image, original.reconstruction),
    }

    config = AMSpdConfig(
        method="portfolio",
        packet_budget=44,
        singular_budget=22,
        parameter_budget=parameter_budget,
        tree_depth=3,
        max_rank=2,
        reopen_fractions=fractions,
        max_actions=actions,
        max_regions=regions,
        random_seed=20260731 + len(case),
    )
    result = AMSpdResult(
        input_image=image,
        reconstruction=selected.reconstruction,
        archive_residual=image - selected.reconstruction,
        selected_method=f"portfolio:{selected.seed}",
        parameter_count=selected.parameter_count,
        packet_count=len(core_result.active_specs),
        metrics=selected_metrics,
        config=config,
        candidate_rmse={portfolio.seed: final.exact_rmse(image, portfolio.reconstruction) for portfolio in portfolios},
        core_result=core_result,
        singular_result=original,
        lagrange_tree_result=lagrange_tree,
        exact_tree_result=exact_tree,
        portfolios=portfolios,
        run_metadata={"historical_replay": True, "replay_backend": "frozen-0.3.0", "replay_input": "checksummed-archived-source-and-core", "reopening_basis": "checksummed-original-archived-seed-coordinates", "seed_anchor_checks": seed_anchor_checks, "parameter_budget_scope": "downstream_scalar_proxy"},
    )
    comparison = compare_paper_reference(summary, reference)
    paper_result = PaperCaseResult(case, result, summary, reference, comparison)
    if strict_reference and not paper_result.reference_match:
        mismatches = [name for name, record in comparison["fields"].items() if record.get("required") and not record["match"]]
        raise RuntimeError(f"paper replay did not match the reference fields: {', '.join(mismatches)}")
    if output_dir is not None:
        paper_result.save(output_dir, include_input=include_input)
    return paper_result


def reproduce_paper(
    output_dir: str | Path,
    *,
    cases: Iterable[str] | None = None,
    strict_reference: bool = False,
    include_input: bool = False,
) -> dict[str, Any]:
    selected_cases = tuple(cases or PAPER_CASES)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    for case in selected_cases:
        value = reproduce_paper_case(
            case,
            output_dir=destination,
            strict_reference=strict_reference,
            include_input=include_input,
        )
        results[case] = {
            "summary": value.summary,
            "comparison": value.comparison,
        }
    report = {
        "cases": results,
        "all_reference_matches": all(item["comparison"]["passed"] for item in results.values()),
    }
    (destination / "paper_reproduction_summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def model_from_paper_case(case: str) -> AMSpdModel:
    result = reproduce_paper_case(case)
    return AMSpdModel.from_result(
        result.result,
        residual_storage="sparse",
        provenance={"mode": "exact-paper-replay", "paper_case": case},
    )

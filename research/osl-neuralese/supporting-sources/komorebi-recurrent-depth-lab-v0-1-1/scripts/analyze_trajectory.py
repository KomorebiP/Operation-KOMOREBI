#!/usr/bin/env python
"""Analyze a captured recurrent trajectory without claiming global closure."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from krd_lab.analysis import (  # noqa: E402
    affine_dmd,
    classify_eigenvalues,
    detect_slider,
    pca_reduce,
)


def _complex_rows(values: np.ndarray) -> list[list[float]]:
    return [[float(value.real), float(value.imag)] for value in values]


def _period_candidates(states: np.ndarray, maximum_period: int = 16) -> dict:
    flattened = states.reshape(states.shape[0], -1).astype(float)
    centered = flattened - flattened.mean(axis=0, keepdims=True)
    motion_rms = float(np.sqrt(np.mean(np.sum(centered**2, axis=1))))
    step_rms = float(np.sqrt(np.mean(np.sum(np.diff(flattened, axis=0) ** 2, axis=1))))
    base_rms = float(np.sqrt(np.mean(np.sum(flattened**2, axis=1))))
    nontrivial = motion_rms > 1e-8 * max(base_rms, 1.0) and step_rms > 0.0
    output = []
    if nontrivial:
        for period in range(2, min(maximum_period, flattened.shape[0] // 2) + 1):
            absolute = float(
                np.sqrt(
                    np.mean(
                        np.sum((flattened[period:] - flattened[:-period]) ** 2, axis=1)
                    )
                )
            )
            output.append(
                {
                    "period": period,
                    "absolute_rms_return": absolute,
                    "return_over_motion_rms": absolute / max(motion_rms, np.finfo(float).eps),
                    "return_over_step_rms": absolute / max(step_rms, np.finfo(float).eps),
                }
            )
        output.sort(key=lambda row: row["return_over_motion_rms"])
    return {
        "nontrivial_motion": nontrivial,
        "motion_rms": motion_rms,
        "step_rms": step_rms,
        "base_rms": base_rms,
        "candidates": output,
    }


def analyze(path: Path, state_key: str, rank: int, late_window: int) -> dict:
    with np.load(path, allow_pickle=False) as payload:
        if state_key not in payload:
            raise KeyError(f"{state_key!r} not present; available: {', '.join(payload.files)}")
        states = np.asarray(payload[state_key], dtype=float)
        positions = np.asarray(payload.get("selected_positions", []), dtype=int)
    if states.ndim < 2 or states.shape[0] < 3 or not np.all(np.isfinite(states)):
        raise ValueError("trajectory must contain at least three finite depth states")
    flattened = states.reshape(states.shape[0], -1)
    pair_count = states.shape[0] - 1
    # Reserve a temporal holdout and enough fit pairs for the affine constant.
    fit_pairs = max(2, int(np.floor(0.7 * pair_count)))
    fit_pairs = min(fit_pairs, pair_count - 1) if pair_count > 2 else pair_count
    maximum_chart_rank = max(1, fit_pairs - 1)
    chart = pca_reduce(
        flattened,
        rank=min(rank, maximum_chart_rank, states.shape[0] - 1, flattened.shape[1]),
    )
    dmd = affine_dmd(chart.coordinates[: fit_pairs + 1])
    held_source = chart.coordinates[fit_pairs:-1].T
    held_target = chart.coordinates[fit_pairs + 1 :].T
    if held_source.shape[1] > 0:
        held_prediction = dmd.operator @ held_source + dmd.offset[:, None]
        heldout_residual = float(
            np.linalg.norm(held_target - held_prediction)
            / max(float(np.linalg.norm(held_target)), np.finfo(float).eps)
        )
    else:
        heldout_residual = None
    stable_fit = (
        chart.effective_rank == chart.coordinates.shape[1]
        and dmd.fully_excited
        and np.isfinite(dmd.condition_number)
        and dmd.condition_number < 1e10
    )
    deltas = np.linalg.norm(np.diff(flattened, axis=0), axis=1)
    state_norms = np.maximum(np.linalg.norm(flattened[1:], axis=1), np.finfo(float).eps)
    normalized_deltas = deltas / state_norms
    late_count = min(late_window, chart.coordinates.shape[0])
    slider = detect_slider(chart.coordinates[-late_count:])
    periods = _period_candidates(flattened[-max(late_window, 6) :])
    reference_distances = np.linalg.norm(flattened - flattened[-1], axis=1)
    return {
        "schema_version": "1.0",
        "input": str(path.resolve()),
        "state_key": state_key,
        "steps": states.shape[0] - 1,
        "selected_positions": positions.tolist(),
        "state_shape_per_depth": list(states.shape[1:]),
        "pca": {
            "rank": chart.coordinates.shape[1],
            "explained_variance_ratio": chart.explained_variance_ratio.tolist(),
            "total_explained_fraction": float(chart.explained_variance_ratio.sum()),
            "reconstruction_residual": chart.reconstruction_residual,
            "effective_rank": chart.effective_rank,
        },
        "affine_dmd_in_pca_chart": {
            "operator": dmd.operator.tolist(),
            "offset": dmd.offset.tolist(),
            "eigenvalues": _complex_rows(dmd.eigenvalues),
            "mode_labels": classify_eigenvalues(dmd.eigenvalues) if stable_fit else [],
            "one_step_residual": dmd.one_step_residual,
            "temporal_heldout_residual": heldout_residual,
            "spectral_radius": dmd.spectral_radius,
            "condition_number": dmd.condition_number,
            "fit_pairs": fit_pairs,
            "heldout_pairs": int(held_source.shape[1]),
            "augmented_effective_rank": dmd.augmented_effective_rank,
            "augmented_dimension": dmd.augmented_dimension,
            "fully_excited": dmd.fully_excited,
            "status": (
                "empirical_finite_chart_only"
                if stable_fit
                else "rank_deficient_or_ill_conditioned_eigenvalue_labels_suppressed"
            ),
        },
        "full_space_metrics": {
            "delta_norms": deltas.tolist(),
            "normalized_delta_norms": normalized_deltas.tolist(),
            "final_reference_distances": reference_distances.tolist(),
            "candidate_periods": periods,
        },
        "late_slider_diagnostic": {
            **asdict(slider),
            "status": "strict_synthetic_threshold_diagnostic_only",
        },
        "claim_boundary": [
            "PCA geometry is visualization, not proof of a periodic orbit.",
            "DMD error is trajectory evidence, not a global Koopman leakage norm.",
            "A single trajectory may be rank deficient and cannot establish reusable packets.",
            "Causal packet claims require held-out perturbation tests.",
        ],
    }


def maybe_plot(path: Path, report: dict, output: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("plotting requires matplotlib") from exc
    with np.load(path, allow_pickle=False) as payload:
        states = np.asarray(payload[report["state_key"]], dtype=float)
    chart = pca_reduce(states.reshape(states.shape[0], -1), rank=3)
    coordinates = chart.coordinates
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    plot_deltas = np.maximum(
        np.asarray(report["full_space_metrics"]["normalized_delta_norms"], dtype=float),
        np.finfo(float).tiny,
    )
    axes[0].plot(np.arange(1, states.shape[0]), plot_deltas)
    axes[0].set(xlabel="recurrence depth", ylabel="normalized step", yscale="log")
    axes[0].grid(alpha=0.25)
    if coordinates.shape[1] >= 2:
        axes[1].plot(coordinates[:, 0], coordinates[:, 1], "o-", markersize=2)
        axes[1].set(xlabel="PC1", ylabel="PC2")
    else:
        axes[1].plot(coordinates[:, 0])
        axes[1].set(xlabel="recurrence depth", ylabel="PC1")
    axes[1].set_title("finite PCA chart (diagnostic only)")
    axes[1].grid(alpha=0.25)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--state-key", choices=["raw_states", "normalized_states", "all_token_sketch"], default="normalized_states")
    parser.add_argument("--rank", type=int, default=12)
    parser.add_argument("--late-window", type=int, default=32)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--plot", type=Path)
    args = parser.parse_args()
    if args.rank < 1 or args.late_window < 3:
        raise ValueError("rank must be at least 1 and late-window at least 3")
    output = args.output or args.input.with_suffix(".analysis.json")
    report = analyze(args.input, args.state_key, args.rank, args.late_window)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.plot:
        maybe_plot(args.input, report, args.plot)
    print(f"Analysis: {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

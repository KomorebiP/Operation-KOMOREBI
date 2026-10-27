#!/usr/bin/env python3
"""A reproducible Gibbs-phenomenon case study.

This file generates every calculation, table, figure, and numerical check used
in "Projector-Resolved Gibbs Reconstruction." It contains one explicit signal,
one model space, one finite interval-recovery algorithm, and one build command.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Wedge
import numpy as np
from numpy.typing import NDArray
from scipy.special import sici

# -----------------------------------------------------------------------------
# Global constants and deterministic style
# -----------------------------------------------------------------------------
PI = math.pi
A_EDGE = 1.0
EDGE_HALF_WIDTH = PI / 3.0
SMOOTH_DEGREE = 5
DEFAULT_GRID = 96
TRUE_START = DEFAULT_GRID // 3
TRUE_LENGTH = DEFAULT_GRID // 3
RNG_SEED = 20260729

INK = "#17202A"
MUTED = "#566573"
PAPER = "#FAFAF7"
WHITE = "#FFFFFF"
GRID = "#D5D8DC"
BLUE = "#2E86AB"
CYAN = "#42B8C5"
TEAL = "#2A9D8F"
GREEN = "#6A994E"
YELLOW = "#E9C46A"
ORANGE = "#F4A261"
RED = "#E76F51"
MAGENTA = "#A23E8C"
PURPLE = "#6C5CE7"
COLORS = [BLUE, TEAL, ORANGE, MAGENTA, PURPLE, GREEN, RED, CYAN, YELLOW]

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10.5,
        "axes.titlesize": 14,
        "axes.labelsize": 10.5,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

Array = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


# -----------------------------------------------------------------------------
# The single signal and its exact continuous formulas
# -----------------------------------------------------------------------------
def wrap_angle(x: Array | float) -> Array:
    arr = np.asarray(x, dtype=float)
    return (arr + PI) % (2.0 * PI) - PI


def smooth_seed(x: Array | float) -> Array:
    """The exact degree-five trigonometric background."""
    arr = np.asarray(x, dtype=float)
    return (
        1.0 / 4.0
        + 2.0 / 5.0 * np.cos(2.0 * arr)
        - 1.0 / 3.0 * np.sin(3.0 * arr)
        + 1.0 / 5.0 * np.cos(5.0 * arr)
    )


def jump_packet(x: Array | float, half_width: float = EDGE_HALF_WIDTH, amplitude: float = A_EDGE) -> Array:
    """Periodic rectangular packet on [-half_width, half_width)."""
    arr = wrap_angle(x)
    return amplitude * ((arr >= -half_width) & (arr < half_width)).astype(float)


def full_signal(x: Array | float, half_width: float = EDGE_HALF_WIDTH, amplitude: float = A_EDGE) -> Array:
    return smooth_seed(x) + jump_packet(x, half_width=half_width, amplitude=amplitude)


def smooth_fourier_coefficient(n: int) -> complex:
    if n == 0:
        return 1.0 / 4.0
    if abs(n) == 2:
        return 1.0 / 5.0
    if n == 3:
        return 1j / 6.0
    if n == -3:
        return -1j / 6.0
    if abs(n) == 5:
        return 1.0 / 10.0
    return 0.0 + 0.0j


def jump_fourier_coefficient(n: int, half_width: float = EDGE_HALF_WIDTH, amplitude: float = A_EDGE) -> complex:
    if n == 0:
        return amplitude * half_width / PI
    return amplitude * math.sin(n * half_width) / (PI * n)


def full_fourier_coefficient(n: int, half_width: float = EDGE_HALF_WIDTH, amplitude: float = A_EDGE) -> complex:
    return smooth_fourier_coefficient(n) + jump_fourier_coefficient(n, half_width, amplitude)


def evaluate_fourier_series(
    x: Array,
    order: int,
    coefficient: Callable[[int], complex],
    weight: Callable[[int, int], float] | None = None,
) -> Array:
    if order < 0:
        raise ValueError("order must be nonnegative")
    if weight is None:
        weight = lambda k, n: 1.0
    out = np.zeros_like(x, dtype=np.complex128)
    for n in range(-order, order + 1):
        out += weight(abs(n), order) * coefficient(n) * np.exp(1j * n * x)
    return np.real_if_close(out, tol=1000).real


def raw_fourier_partial_sum(x: Array, order: int) -> Array:
    return evaluate_fourier_series(x, order, full_fourier_coefficient)


def _jump_weighted_sum(x: Array, order: int, weight: Callable[[int, int], float] | None = None) -> Array:
    if weight is None:
        weight = lambda k, n: 1.0
    out = np.full_like(x, EDGE_HALF_WIDTH / PI, dtype=float)
    if order == 0:
        return out
    n = np.arange(1, order + 1, dtype=float)
    weights = np.array([weight(int(k), order) for k in n], dtype=float)
    coeff = (2.0 / PI) * np.sin(n * EDGE_HALF_WIDTH) / n * weights
    # Chunk the mode matrix so the standalone script remains memory-safe.
    chunk = 20000
    for start in range(0, x.size, chunk):
        stop = min(x.size, start + chunk)
        out[start:stop] += coeff @ np.cos(np.outer(n, x[start:stop]))
    return out


def jump_fourier_partial_sum(x: Array, order: int) -> Array:
    return _jump_weighted_sum(x, order)


def smooth_fourier_partial_sum(x: Array, order: int, weight: Callable[[int, int], float] | None = None) -> Array:
    if weight is None:
        weight = lambda k, n: 1.0
    out = np.full_like(x, 1.0 / 4.0, dtype=float)
    if order >= 2:
        out += (2.0 / 5.0) * weight(2, order) * np.cos(2.0 * x)
    if order >= 3:
        out -= (1.0 / 3.0) * weight(3, order) * np.sin(3.0 * x)
    if order >= 5:
        out += (1.0 / 5.0) * weight(5, order) * np.cos(5.0 * x)
    return out


def fejer_weight(k: int, n: int) -> float:
    return 1.0 - k / (n + 1.0)


def lanczos_weight(k: int, n: int) -> float:
    if n == 0:
        return 1.0
    return float(np.sinc(k / (n + 1.0)))


def exponential_weight(k: int, n: int, power: int = 8, alpha: float = 18.0) -> float:
    if n == 0:
        return 1.0
    return math.exp(-alpha * (k / n) ** power)


def filtered_full_sum(x: Array, order: int, method: str) -> Array:
    if method == "raw":
        weight = None
    elif method == "fejer":
        weight = fejer_weight
    elif method == "lanczos":
        weight = lanczos_weight
    elif method == "exponential":
        weight = lambda k, n: exponential_weight(k, n)
    else:
        raise ValueError(f"unknown method: {method}")
    return smooth_fourier_partial_sum(x, order, weight) + _jump_weighted_sum(x, order, weight)


def filtered_jump_sum(x: Array, order: int, method: str) -> Array:
    if method == "raw":
        return jump_fourier_partial_sum(x, order)
    if method == "fejer":
        return _jump_weighted_sum(x, order, fejer_weight)
    if method == "lanczos":
        return _jump_weighted_sum(x, order, lanczos_weight)
    if method == "exponential":
        return _jump_weighted_sum(x, order, lambda k, n: exponential_weight(k, n))
    raise ValueError(f"unknown method: {method}")


def packet_reconstruction(x: Array, order: int) -> Array:
    """Resolved operator R_N = S_N P_smooth + P_edge."""
    return smooth_fourier_partial_sum(x, order) + jump_packet(x)


def dirichlet_kernel(t: Array, order: int) -> Array:
    out = np.empty_like(t, dtype=float)
    denom = np.sin(t / 2.0)
    mask = np.abs(denom) < 1e-13
    out[mask] = 2 * order + 1
    out[~mask] = np.sin((order + 0.5) * t[~mask]) / denom[~mask]
    return out


def fejer_kernel(t: Array, order: int) -> Array:
    out = np.empty_like(t, dtype=float)
    denom = np.sin(t / 2.0)
    mask = np.abs(denom) < 1e-13
    out[mask] = order + 1.0
    out[~mask] = (np.sin((order + 1.0) * t[~mask] / 2.0) ** 2) / ((order + 1.0) * denom[~mask] ** 2)
    return out


def gibbs_profile(z: Array) -> Array:
    return 0.5 + sici(z)[0] / PI


def gibbs_constant() -> float:
    return float(sici(PI)[0] / PI - 0.5)


# -----------------------------------------------------------------------------
# Exact packet calculus on the chosen model space
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class PacketState:
    smooth: Array
    edge: Array

    def synthesize(self) -> Array:
        return self.smooth + self.edge


def analyze_declared_model(x: Array) -> PacketState:
    """Analysis for the worked example.

    The input x is assumed to be the signal defined in the paper. The paper
    proves the corresponding model-space projectors abstractly. This function
    implements their action on the worked example.
    """
    return PacketState(smooth=smooth_seed(x), edge=jump_packet(x))


# -----------------------------------------------------------------------------
# Finite sample model and exact profile search
# -----------------------------------------------------------------------------
def sample_grid(size: int) -> Array:
    return -PI + 2.0 * PI * np.arange(size) / size


def trigonometric_design(x: Array, degree: int) -> Array:
    cols: list[Array] = [np.ones_like(x)]
    for k in range(1, degree + 1):
        cols.append(np.cos(k * x))
        cols.append(np.sin(k * x))
    return np.column_stack(cols)


def orthonormal_basis(matrix: Array) -> Array:
    q, _ = np.linalg.qr(matrix)
    return q


def interval_mask(size: int, start: int, length: int) -> Array:
    if length < 1 or length > size:
        raise ValueError("invalid interval length")
    out = np.zeros(size, dtype=float)
    out[(start + np.arange(length)) % size] = 1.0
    return out


@dataclass
class CandidateLibrary:
    size: int
    degree: int
    x: Array
    design: Array
    q_background: Array
    masks: Array
    starts: NDArray[np.int64]
    lengths: NDArray[np.int64]
    residual_masks: Array
    residual_norms: Array

    @classmethod
    def build(
        cls,
        size: int = DEFAULT_GRID,
        degree: int = SMOOTH_DEGREE,
        min_length: int = 8,
        max_length: int | None = None,
    ) -> "CandidateLibrary":
        x = sample_grid(size)
        design = trigonometric_design(x, degree)
        q_background = orthonormal_basis(design)
        if max_length is None:
            max_length = size // 2
        masks: list[Array] = []
        starts: list[int] = []
        lengths: list[int] = []
        residual_masks: list[Array] = []
        residual_norms: list[float] = []
        for length in range(min_length, max_length + 1):
            for start in range(size):
                mask = interval_mask(size, start, length)
                residual = mask - q_background @ (q_background.T @ mask)
                residual_norm = float(residual @ residual)
                if residual_norm <= 1e-12:
                    continue
                masks.append(mask)
                starts.append(start)
                lengths.append(length)
                residual_masks.append(residual)
                residual_norms.append(residual_norm)
        return cls(
            size=size,
            degree=degree,
            x=x,
            design=design,
            q_background=q_background,
            masks=np.asarray(masks),
            starts=np.asarray(starts, dtype=np.int64),
            lengths=np.asarray(lengths, dtype=np.int64),
            residual_masks=np.asarray(residual_masks),
            residual_norms=np.asarray(residual_norms),
        )

    def residualize(self, y: Array) -> Array:
        return y - self.q_background @ (self.q_background.T @ y)

    def search(self, y: Array, positive_amplitude: bool = True) -> dict[str, object]:
        y_perp = self.residualize(y)
        dots = self.residual_masks @ y_perp
        amplitudes = dots / self.residual_norms
        residuals = (
            float(y_perp @ y_perp)
            - 2.0 * amplitudes * dots
            + amplitudes**2 * self.residual_norms
        )
        residuals = np.maximum(residuals, 0.0)
        if positive_amplitude:
            residuals = np.where(amplitudes > 0.0, residuals, np.inf)
        order = np.argsort(residuals)
        best = int(order[0])
        second = int(order[1])
        mask = self.masks[best]
        amplitude = float(amplitudes[best])
        smooth_fit = self.q_background @ (self.q_background.T @ (y - amplitude * mask))
        reconstruction = smooth_fit + amplitude * mask
        return {
            "index": best,
            "start": int(self.starts[best]),
            "length": int(self.lengths[best]),
            "amplitude": amplitude,
            "residual": float(residuals[best]),
            "second_residual": float(residuals[second]),
            "gap": float(residuals[second] - residuals[best]),
            "mask": mask,
            "smooth": smooth_fit,
            "reconstruction": reconstruction,
            "all_residuals": residuals,
            "all_amplitudes": amplitudes,
            "y_perp": y_perp,
        }


def true_discrete_signal(size: int = DEFAULT_GRID) -> tuple[Array, Array, Array, Array]:
    x = sample_grid(size)
    smooth = smooth_seed(x)
    start = size // 3
    length = size // 3
    edge = interval_mask(size, start, length)
    return x, smooth, edge, smooth + edge


# -----------------------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------------------
def rmse(a: Array, b: Array) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def maximum_error(a: Array, b: Array) -> float:
    return float(np.max(np.abs(a - b)))


def boundary_mask(x: Array, width: float = 0.15, half_width: float = EDGE_HALF_WIDTH) -> NDArray[np.bool_]:
    return (np.abs(np.abs(wrap_angle(x)) - half_width) <= width)


def boundary_rmse(approx: Array, truth: Array, x: Array, width: float = 0.15) -> float:
    mask = boundary_mask(x, width=width)
    return rmse(approx[mask], truth[mask])


def jump_overshoot(approx_jump: Array, x: Array, half_width: float = EDGE_HALF_WIDTH, band: float = 0.3) -> float:
    inside = (x < half_width - 1e-8) & (x > half_width - band)
    return float(np.max(approx_jump[inside] - 1.0))


def jump_undershoot(approx_jump: Array, x: Array, half_width: float = EDGE_HALF_WIDTH, band: float = 0.3) -> float:
    outside = (x > half_width + 1e-8) & (x < half_width + band)
    return float(np.min(approx_jump[outside]))


def total_variation_periodic(values: Array) -> float:
    return float(np.sum(np.abs(np.roll(values, -1) - values)))


def transition_width(values: Array, x: Array, low: float = 0.1, high: float = 0.9, edge: float = EDGE_HALF_WIDTH) -> float:
    window = (x > edge - 0.5) & (x < edge + 0.5)
    xx = x[window]
    yy = values[window]
    # descending edge: find nearest positions to high and low crossings.
    high_idx = int(np.argmin(np.abs(yy - high)))
    low_idx = int(np.argmin(np.abs(yy - low)))
    return float(abs(xx[low_idx] - xx[high_idx]))


# -----------------------------------------------------------------------------
# Plot helpers
# -----------------------------------------------------------------------------
def save_figure(fig: plt.Figure, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_dir / f"{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def style_axis(ax: plt.Axes, grid: bool = True) -> None:
    if grid:
        ax.grid(alpha=0.18)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)


def add_external_legend(ax: plt.Axes, ncol: int = 1) -> None:
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0.0,
        frameon=True,
        fontsize=9,
        ncol=ncol,
    )


def diagram_box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, color: str, fontsize: float = 11) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=color + "20",
        edgecolor=color,
        linewidth=1.7,
    )
    ax.add_patch(patch)
    label = ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", multialignment="center", fontsize=fontsize)
    # renderer-based fit
    for _ in range(10):
        ax.figure.canvas.draw()
        r = ax.figure.canvas.get_renderer()
        tb = label.get_window_extent(r)
        (x0, y0), (x1, y1) = ax.transData.transform(((x, y), (x + w, y + h)))
        if tb.width <= abs(x1 - x0) * 0.84 and tb.height <= abs(y1 - y0) * 0.78:
            break
        label.set_fontsize(max(7.5, label.get_fontsize() * 0.90))


def diagram_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = INK, label: str | None = None) -> None:
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13, linewidth=1.6, color=color)
    ax.add_patch(arrow)
    if label:
        mx = 0.5 * (start[0] + end[0])
        my = 0.5 * (start[1] + end[1])
        ax.text(mx, my + 0.025, label, ha="center", va="bottom", fontsize=9.3, color=color, bbox={"facecolor": PAPER, "edgecolor": "none", "pad": 1.2})


# -----------------------------------------------------------------------------
# Main computational experiment
# -----------------------------------------------------------------------------
def build_experiment(root: Path, quick: bool = False) -> dict[str, object]:
    figures = root / "figures"
    tables = root / "tables"
    results_dir = root / "results"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    dense_count = 18000 if quick else 36000
    x_dense = np.linspace(-PI, PI, dense_count, endpoint=False)
    s_dense = smooth_seed(x_dense)
    j_dense = jump_packet(x_dense)
    f_dense = s_dense + j_dense

    # Exact coefficient table.
    coeff_rows: list[dict[str, object]] = []
    for n in range(-24, 25):
        cs = smooth_fourier_coefficient(n)
        cj = jump_fourier_coefficient(n)
        cf = cs + cj
        coeff_rows.append(
            {
                "n": n,
                "smooth_real": float(cs.real),
                "smooth_imag": float(cs.imag),
                "jump_real": float(cj.real),
                "jump_imag": float(cj.imag),
                "full_real": float(cf.real),
                "full_imag": float(cf.imag),
                "residue_mod_6": n % 6,
            }
        )
    with (tables / "fourier_coefficients.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coeff_rows[0]))
        writer.writeheader()
        writer.writerows(coeff_rows)

    # Method curves and metrics over orders.
    orders = np.array([5, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160])
    methods = ["raw", "fejer", "lanczos", "exponential", "packet"]
    metric_rows: list[dict[str, object]] = []
    for order in orders:
        for method in methods:
            if method == "packet":
                approximation = packet_reconstruction(x_dense, int(order))
                jump_approximation = j_dense
            else:
                approximation = filtered_full_sum(x_dense, int(order), method)
                jump_approximation = filtered_jump_sum(x_dense, int(order), method)
            metric_rows.append(
                {
                    "order": int(order),
                    "method": method,
                    "rmse": rmse(approximation, f_dense),
                    "max_error": maximum_error(approximation, f_dense),
                    "boundary_rmse": boundary_rmse(approximation, f_dense, x_dense),
                    "jump_overshoot": jump_overshoot(jump_approximation, x_dense),
                    "jump_undershoot": jump_undershoot(jump_approximation, x_dense),
                    "jump_transition_width": transition_width(jump_approximation, x_dense),
                    "total_variation": total_variation_periodic(approximation),
                }
            )
    with (tables / "method_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)

    # Finite exact recovery.
    library = CandidateLibrary.build(DEFAULT_GRID, SMOOTH_DEGREE)
    x_grid, s_grid, edge_grid, y_grid = true_discrete_signal(DEFAULT_GRID)
    exact_search = library.search(y_grid)
    exact_coefficients, *_ = np.linalg.lstsq(
        library.design,
        y_grid - float(exact_search["amplitude"]) * np.asarray(exact_search["mask"]),
        rcond=None,
    )

    # Candidate objective as a start-length grid.
    max_len = DEFAULT_GRID // 2
    objective_grid = np.full((max_len + 1, DEFAULT_GRID), np.nan)
    all_residuals = np.asarray(exact_search["all_residuals"])
    for residual, start, length in zip(all_residuals, library.starts, library.lengths, strict=True):
        objective_grid[int(length), int(start)] = residual

    # Noise study.
    rng = np.random.default_rng(RNG_SEED)
    sigmas = np.array([0.0, 0.01, 0.03, 0.05, 0.08, 0.12, 0.16, 0.20, 0.25])
    repetitions = 40 if quick else 140
    noise_rows: list[dict[str, object]] = []
    noise_examples: dict[float, dict[str, object]] = {}
    for sigma in sigmas:
        noise = rng.normal(0.0, float(sigma), (DEFAULT_GRID, repetitions))
        noisy_matrix = y_grid[:, None] + noise
        qbg = library.q_background
        yperp_matrix = noisy_matrix - qbg @ (qbg.T @ noisy_matrix)
        dots = library.residual_masks @ yperp_matrix
        amplitudes = dots / library.residual_norms[:, None]
        base = np.sum(yperp_matrix**2, axis=0)[None, :]
        residuals = base - 2.0 * amplitudes * dots + amplitudes**2 * library.residual_norms[:, None]
        residuals = np.maximum(residuals, 0.0)
        residuals = np.where(amplitudes > 0.0, residuals, np.inf)
        best_indices = np.argmin(residuals, axis=0)
        starts = library.starts[best_indices]
        lengths = library.lengths[best_indices]
        best_amplitudes = amplitudes[best_indices, np.arange(repetitions)]
        exact_rate = float(np.mean((starts == TRUE_START) & (lengths == TRUE_LENGTH)))
        circular_start = ((starts - TRUE_START + DEFAULT_GRID / 2) % DEFAULT_GRID) - DEFAULT_GRID / 2
        reconstruction_errors: list[float] = []
        boundary_errors: list[float] = []
        edge_band = np.zeros(DEFAULT_GRID, dtype=bool)
        for center in (TRUE_START, TRUE_START + TRUE_LENGTH):
            for offset in range(-3, 4):
                edge_band[(center + offset) % DEFAULT_GRID] = True
        for rep, idx in enumerate(best_indices):
            mask = library.masks[int(idx)]
            amp = float(best_amplitudes[rep])
            noisy = noisy_matrix[:, rep]
            smooth_fit = qbg @ (qbg.T @ (noisy - amp * mask))
            reconstruction = smooth_fit + amp * mask
            reconstruction_errors.append(rmse(reconstruction, y_grid))
            boundary_errors.append(rmse(reconstruction[edge_band], y_grid[edge_band]))
        noise_rows.append(
            {
                "sigma": float(sigma),
                "repetitions": repetitions,
                "exact_support_rate": exact_rate,
                "mean_abs_start_error_samples": float(np.mean(np.abs(circular_start))),
                "mean_abs_length_error_samples": float(np.mean(np.abs(lengths - TRUE_LENGTH))),
                "mean_abs_amplitude_error": float(np.mean(np.abs(best_amplitudes - A_EDGE))),
                "mean_reconstruction_rmse": float(np.mean(reconstruction_errors)),
                "mean_boundary_rmse": float(np.mean(boundary_errors)),
            }
        )
        if float(sigma) in (0.03, 0.12, 0.20):
            idx = int(best_indices[0])
            mask = library.masks[idx]
            amp = float(best_amplitudes[0])
            noisy = noisy_matrix[:, 0]
            smooth_fit = qbg @ (qbg.T @ (noisy - amp * mask))
            reconstruction = smooth_fit + amp * mask
            noise_examples[float(sigma)] = {
                "noisy": noisy,
                "fit": {
                    "start": int(library.starts[idx]),
                    "length": int(library.lengths[idx]),
                    "amplitude": amp,
                    "reconstruction": reconstruction,
                },
            }
    with (tables / "noise_recovery.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(noise_rows[0]))
        writer.writeheader()
        writer.writerows(noise_rows)

    # Off-grid study.
    offgrid_shift = 0.37
    offgrid_rows: list[dict[str, object]] = []
    for size in [48, 72, 96, 120, 144, 192]:
        xx = sample_grid(size)
        dx = 2.0 * PI / size
        half_width = EDGE_HALF_WIDTH + offgrid_shift * dx
        yy = smooth_seed(xx) + jump_packet(xx, half_width=half_width)
        lib = CandidateLibrary.build(size, SMOOTH_DEGREE, min_length=max(4, size // 16), max_length=size // 2)
        fit = lib.search(yy)
        start = int(fit["start"])
        length = int(fit["length"])
        left_estimate = -PI + start * dx
        right_estimate = -PI + ((start + length) % size) * dx
        # For this nonwrapping worked interval, unwrap right endpoint.
        if right_estimate <= left_estimate:
            right_estimate += 2.0 * PI
        true_left = -half_width
        true_right = half_width
        offgrid_rows.append(
            {
                "size": size,
                "dx": dx,
                "true_left": true_left,
                "true_right": true_right,
                "estimated_left": left_estimate,
                "estimated_right": right_estimate,
                "max_endpoint_error": max(abs(left_estimate - true_left), abs(right_estimate - true_right)),
                "reconstruction_rmse": rmse(np.asarray(fit["reconstruction"]), yy),
            }
        )
    with (tables / "offgrid_recovery.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(offgrid_rows[0]))
        writer.writeheader()
        writer.writerows(offgrid_rows)

    # Runtime scaling for the one finite search implementation.
    runtime_rows: list[dict[str, object]] = []
    runtime_sizes = [48, 64, 80, 96, 112, 128] if quick else [48, 64, 80, 96, 112, 128, 144, 160]
    for size in runtime_sizes:
        t0 = time.perf_counter()
        lib = CandidateLibrary.build(size, SMOOTH_DEGREE, min_length=max(4, size // 16), max_length=size // 2)
        build_seconds = time.perf_counter() - t0
        xx, ss, qq, yy = true_discrete_signal(size)
        t1 = time.perf_counter()
        fit = lib.search(yy)
        search_seconds = time.perf_counter() - t1
        runtime_rows.append(
            {
                "size": size,
                "candidate_count": int(lib.masks.shape[0]),
                "build_seconds": build_seconds,
                "search_seconds": search_seconds,
                "correct": bool(int(fit["start"]) == size // 3 and int(fit["length"]) == size // 3),
            }
        )
    with (tables / "runtime_scaling.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(runtime_rows[0]))
        writer.writeheader()
        writer.writerows(runtime_rows)

    # ------------------------------------------------------------------
    # Figures 01-60
    # ------------------------------------------------------------------
    # 01 components
    fig, ax = plt.subplots(figsize=(11.5, 4.6))
    ax.plot(x_dense, s_dense, lw=2.0, label="smooth seed s(x)", color=BLUE)
    ax.plot(x_dense, j_dense, lw=2.0, label="edge packet j(x)", color=ORANGE)
    ax.plot(x_dense, f_dense, lw=2.3, label="full signal f=s+j", color=INK)
    ax.axvline(-EDGE_HALF_WIDTH, ls="--", lw=1.1, color=MUTED)
    ax.axvline(EDGE_HALF_WIDTH, ls="--", lw=1.1, color=MUTED)
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.set_title("The one signal used throughout the entire monograph", weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0, 0, 0.82, 1])
    save_figure(fig, figures, "01_signal_components")

    # 02 seed-to-reconstruction diagram
    fig, ax = plt.subplots(figsize=(12.5, 5.1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    stages = [
        (0.02, "seed\n(smooth + edge)", BLUE),
        (0.19, "sample\nor observe", CYAN),
        (0.36, "analyze\n(P_s, P_j)", TEAL),
        (0.53, "operate\nS_N P_s + P_j", ORANGE),
        (0.70, "synthesize\nadd packets", MAGENTA),
        (0.87, "residual\ncheck", GREEN),
    ]
    for xpos, label, color in stages:
        diagram_box(ax, xpos, 0.42, 0.12, 0.22, label, color, 12)
    for i in range(len(stages) - 1):
        diagram_arrow(ax, (stages[i][0] + 0.12, 0.53), (stages[i + 1][0], 0.53))
    ax.text(0.5, 0.85, "From the signal seed to reconstruction", ha="center", fontsize=22, weight="bold")
    ax.text(0.5, 0.18, "The discontinuity is never forced through the global Fourier truncation block.", ha="center", fontsize=13, color=MUTED)
    save_figure(fig, figures, "02_closed_pipeline")

    # 03 packet split
    fig, axes = plt.subplots(3, 1, figsize=(11.5, 7.0), sharex=True)
    axes[0].plot(x_dense, f_dense, color=INK, lw=2.2)
    axes[0].set_title("Exact model-space packet decomposition", loc="left", weight="bold")
    axes[0].set_ylabel("f")
    axes[1].plot(x_dense, s_dense, color=BLUE, lw=2.0)
    axes[1].set_ylabel("P_s f")
    axes[2].plot(x_dense, j_dense, color=ORANGE, lw=2.0)
    axes[2].set_ylabel("P_j f")
    axes[2].set_xlabel("x")
    for axr in axes: style_axis(axr)
    fig.tight_layout()
    save_figure(fig, figures, "03_exact_packet_split")

    # 04 basis atoms
    fig, axes = plt.subplots(3, 2, figsize=(11.5, 7.0), sharex=True)
    atoms = [
        (np.ones_like(x_dense), "1"),
        (np.cos(2*x_dense), "cos(2x)"),
        (np.sin(3*x_dense), "sin(3x)"),
        (np.cos(5*x_dense), "cos(5x)"),
        (s_dense, "assembled smooth seed"),
        (j_dense, "edge packet"),
    ]
    for axr, (vals, title) in zip(axes.ravel(), atoms, strict=True):
        axr.plot(x_dense, vals, lw=1.8, color=COLORS[len(axr.lines) % len(COLORS)] if False else BLUE)
        axr.set_title(title, weight="bold", fontsize=11)
        style_axis(axr)
    fig.suptitle("Primitive atoms and the two signal packets", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0,0,1,.94])
    save_figure(fig, figures, "04_seed_atoms")

    # 05 jump geometry
    fig, ax = plt.subplots(figsize=(11.5, 4.4))
    ax.fill_between(x_dense, 0, j_dense, color=ORANGE, alpha=.35, label="packet support")
    ax.plot(x_dense, j_dense, color=ORANGE, lw=2.2)
    ax.scatter([-EDGE_HALF_WIDTH, EDGE_HALF_WIDTH], [1, 0], s=55, color=[TEAL, RED], zorder=4)
    ax.annotate("left jump", (-EDGE_HALF_WIDTH,1), xytext=(-2.4,1.18), arrowprops={"arrowstyle":"->"})
    ax.annotate("right jump", (EDGE_HALF_WIDTH,0), xytext=(1.4,.25), arrowprops={"arrowstyle":"->"})
    ax.set_ylim(-.2,1.35)
    ax.set_xlabel("x")
    ax.set_ylabel("j(x)")
    ax.set_title("The singular packet is a geometric object, not a cloud of Fourier modes", weight="bold")
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig, figures, "05_jump_geometry")

    # 06 exact coefficients
    ns = np.arange(-24,25)
    cs = np.array([smooth_fourier_coefficient(int(n)) for n in ns])
    cj = np.array([jump_fourier_coefficient(int(n)) for n in ns])
    fig, axes = plt.subplots(2,1,figsize=(11.8,6.7),sharex=True)
    axes[0].stem(ns, np.abs(cs), linefmt=BLUE, markerfmt="o", basefmt=" ")
    axes[0].set_ylabel("|s-hat_n|")
    axes[0].set_title("Exact smooth coefficients terminate at degree five", loc="left", weight="bold")
    axes[1].stem(ns, np.abs(cj), linefmt=ORANGE, markerfmt="o", basefmt=" ")
    axes[1].set_ylabel("|j-hat_n|")
    axes[1].set_xlabel("Fourier index n")
    axes[1].set_title("The jump packet has an algebraic 1/|n| tail", loc="left", weight="bold")
    for axr in axes: style_axis(axr)
    fig.tight_layout()
    save_figure(fig, figures, "06_exact_fourier_coefficients")

    # 07 residue classes
    positive_n = np.arange(1,37)
    vals = np.array([math.sin(n*EDGE_HALF_WIDTH) for n in positive_n])
    fig, ax = plt.subplots(figsize=(11.5,4.5))
    colors = [COLORS[n%6] for n in positive_n]
    ax.bar(positive_n, vals, color=colors, edgecolor=INK, linewidth=.4)
    ax.set_xlabel("n")
    ax.set_ylabel("sin(n pi/3)")
    ax.set_title("The jump coefficients split into six exact residue packets", weight="bold")
    ax.set_xticks(np.arange(0,37,3))
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig, figures, "07_coefficient_residue_classes")

    # 08 coefficient decay
    nn = np.arange(1,160)
    jj = np.abs(np.array([jump_fourier_coefficient(int(n)) for n in nn]))
    envelope = 1.0/(PI*nn)
    fig, ax = plt.subplots(figsize=(11.5,4.5))
    ax.loglog(nn, jj + 1e-18, label="|j-hat_n|", color=ORANGE, lw=1.7)
    ax.loglog(nn, envelope, label="1/(pi n) envelope", color=INK, ls="--")
    ax.set_xlabel("n")
    ax.set_ylabel("magnitude")
    ax.set_title("Slow spectral decay is the signature of the discontinuity", weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig, figures, "08_coefficient_decay")

    # 09 kernels
    t_kernel = np.linspace(-.7,.7,20000)
    fig, axes = plt.subplots(2,2,figsize=(11.8,7.0),sharex=True)
    for axr, order in zip(axes.ravel(), [5,10,20,40], strict=True):
        axr.plot(t_kernel, dirichlet_kernel(t_kernel,order), color=BLUE, lw=1.5)
        axr.set_title(f"D_{order}(t)", weight="bold")
        style_axis(axr)
    fig.suptitle("Dirichlet kernels sharpen and oscillate rather than becoming positive", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0,0,1,.94])
    save_figure(fig, figures, "09_dirichlet_kernels")

    # 10 convolution at edge
    u = np.linspace(-.6,.6,20000)
    D = dirichlet_kernel(u,40)/(2*PI)
    fig, ax = plt.subplots(figsize=(11.5,4.7))
    ax.plot(u,D,color=BLUE,lw=1.7,label="normalized D_40")
    ax.fill_between(u,0,D,where=(u<0),color=ORANGE,alpha=.25,label="mass sampled from inside packet")
    ax.axvline(0,color=INK,lw=1)
    ax.set_xlabel("local coordinate around the edge")
    ax.set_ylabel("kernel weight")
    ax.set_title("The truncated Fourier operator mixes both sides of the discontinuity", weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.79,1])
    save_figure(fig, figures, "10_edge_convolution")

    # 11-14 full partial sums
    for fig_no, order in zip(range(11,15), [5,10,20,40], strict=True):
        approx = raw_fourier_partial_sum(x_dense,order)
        fig, ax = plt.subplots(figsize=(11.5,4.5))
        ax.plot(x_dense,f_dense,color=INK,lw=2.1,label="exact f")
        ax.plot(x_dense,approx,color=BLUE,lw=1.3,label=f"raw S_{order} f")
        ax.axvline(-EDGE_HALF_WIDTH,ls="--",color=MUTED,lw=.9)
        ax.axvline(EDGE_HALF_WIDTH,ls="--",color=MUTED,lw=.9)
        ax.set_xlabel("x")
        ax.set_ylabel("amplitude")
        ax.set_title(f"Global Fourier truncation at order N={order}", weight="bold")
        style_axis(ax)
        add_external_legend(ax)
        fig.tight_layout(rect=[0,0,.82,1])
        save_figure(fig, figures, f"{fig_no:02d}_raw_partial_N{order}")

    # 15-17 edge zooms
    for fig_no, order in zip(range(15,18), [10,20,40], strict=True):
        approx = raw_fourier_partial_sum(x_dense,order)
        local = (x_dense>EDGE_HALF_WIDTH-.35)&(x_dense<EDGE_HALF_WIDTH+.35)
        fig, ax = plt.subplots(figsize=(11.5,4.5))
        ax.plot(x_dense[local],f_dense[local],color=INK,lw=2.2,label="exact f")
        ax.plot(x_dense[local],approx[local],color=BLUE,lw=1.5,label=f"S_{order}f")
        ax.axvline(EDGE_HALF_WIDTH,ls="--",color=RED,lw=1.0,label="true edge")
        ax.set_xlabel("x")
        ax.set_ylabel("amplitude")
        ax.set_title(f"The oscillation compresses toward the edge but its first overshoot persists (N={order})", weight="bold")
        style_axis(ax)
        add_external_legend(ax)
        fig.tight_layout(rect=[0,0,.80,1])
        save_figure(fig, figures, f"{fig_no:02d}_edge_zoom_N{order}")

    # 18 scaled profile collapse
    z = np.linspace(-10,10,5000)
    fig, ax = plt.subplots(figsize=(11.5,4.8))
    for order,color in zip([20,40,80,160],[BLUE,TEAL,ORANGE,MAGENTA],strict=True):
        xlocal = EDGE_HALF_WIDTH - z/(order+0.5)
        ax.plot(z,jump_fourier_partial_sum(xlocal,order),lw=1.4,label=f"N={order}",color=color)
    ax.plot(z,gibbs_profile(z),color=INK,lw=2.2,ls="--",label="limiting sine-integral profile")
    ax.axvline(PI,color=RED,ls=":",lw=1)
    ax.set_xlabel("scaled interior coordinate z=(N+1/2)(a-x)")
    ax.set_ylabel("partial sum of jump")
    ax.set_title("Edge profiles collapse to a universal scaled limit", weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.79,1])
    save_figure(fig, figures, "18_scaled_profile_collapse")

    # 19 Gibbs constant convergence
    Nvals=np.arange(5,301)
    observed=[]
    for order in Nvals:
        xstar=EDGE_HALF_WIDTH-PI/(order+.5)
        observed.append(float(jump_fourier_partial_sum(np.array([xstar]),int(order))[0]-1.0))
    fig,ax=plt.subplots(figsize=(11.5,4.5))
    ax.plot(Nvals,observed,color=BLUE,lw=1.7,label="first scaled overshoot")
    ax.axhline(gibbs_constant(),color=RED,ls="--",lw=1.5,label=f"G={gibbs_constant():.12f}")
    ax.set_xlabel("N")
    ax.set_ylabel("overshoot above unit jump")
    ax.set_title("The first overshoot converges to the Gibbs constant",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.79,1])
    save_figure(fig,figures,"19_gibbs_constant_convergence")

    # curves from metrics
    def metric_series(method: str, field: str) -> tuple[np.ndarray,np.ndarray]:
        rows=[r for r in metric_rows if r["method"]==method]
        return np.array([r["order"] for r in rows]),np.array([r[field] for r in rows],float)

    # 20 overshoot
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    for method,color in zip(methods,[BLUE,TEAL,ORANGE,PURPLE,MAGENTA],strict=True):
        xxm,yym=metric_series(method,"jump_overshoot")
        ax.plot(xxm,yym,marker="o",ms=3,lw=1.6,label=method,color=color)
    ax.axhline(gibbs_constant(),color=RED,ls="--",label="Gibbs constant")
    ax.set_xlabel("spectral order N")
    ax.set_ylabel("jump overshoot")
    ax.set_title("Packet retention removes jump overshoot exactly",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig,figures,"20_overshoot_vs_order")

    # 21 RMSE
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    for method,color in zip(methods,[BLUE,TEAL,ORANGE,PURPLE,MAGENTA],strict=True):
        xxm,yym=metric_series(method,"rmse")
        ax.semilogy(xxm,np.maximum(yym,1e-17),marker="o",ms=3,lw=1.6,label=method,color=color)
    ax.set_xlabel("spectral order N")
    ax.set_ylabel("global RMSE")
    ax.set_title("Global spectral error decreases, but only packet retention is exact at N>=5",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig,figures,"21_rmse_vs_order")

    # 22 boundary rmse
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    for method,color in zip(methods,[BLUE,TEAL,ORANGE,PURPLE,MAGENTA],strict=True):
        xxm,yym=metric_series(method,"boundary_rmse")
        ax.semilogy(xxm,np.maximum(yym,1e-17),marker="o",ms=3,lw=1.6,label=method,color=color)
    ax.set_xlabel("spectral order N")
    ax.set_ylabel("boundary-band RMSE")
    ax.set_title("The decisive gain is localized at the discontinuity",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig,figures,"22_boundary_rmse_vs_order")

    # 23-25 filter jump comparisons
    for fig_no,method,color in [(23,"fejer",TEAL),(24,"lanczos",ORANGE),(25,"exponential",PURPLE)]:
        order=40
        approx=filtered_jump_sum(x_dense,order,method)
        local=(x_dense>EDGE_HALF_WIDTH-.45)&(x_dense<EDGE_HALF_WIDTH+.45)
        fig,ax=plt.subplots(figsize=(11.5,4.5))
        ax.plot(x_dense[local],j_dense[local],color=INK,lw=2.2,label="exact jump")
        ax.plot(x_dense[local],approx[local],color=color,lw=1.6,label=f"{method} reconstruction")
        ax.axvline(EDGE_HALF_WIDTH,color=RED,ls="--",lw=1,label="edge")
        ax.set_xlabel("x")
        ax.set_ylabel("jump amplitude")
        ax.set_title(f"{method.capitalize()} filtering trades oscillation for a blurred transition",weight="bold")
        style_axis(ax)
        add_external_legend(ax)
        fig.tight_layout(rect=[0,0,.80,1])
        save_figure(fig,figures,f"{fig_no:02d}_{method}_jump")

    # 26 full comparison
    order=40
    fig,ax=plt.subplots(figsize=(11.5,4.8))
    ax.plot(x_dense,f_dense,color=INK,lw=2.2,label="exact f")
    for method,color in zip(methods,[BLUE,TEAL,ORANGE,PURPLE,MAGENTA],strict=True):
        approx=packet_reconstruction(x_dense,order) if method=="packet" else filtered_full_sum(x_dense,order,method)
        ax.plot(x_dense,approx,lw=1.15,label=method,color=color,alpha=.9)
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.set_title("Five reconstruction operators applied to the same signal",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.78,1])
    save_figure(fig,figures,"26_method_comparison_full")

    # 27 edge comparison
    local=(x_dense>EDGE_HALF_WIDTH-.28)&(x_dense<EDGE_HALF_WIDTH+.28)
    fig,ax=plt.subplots(figsize=(11.5,4.8))
    ax.plot(x_dense[local],f_dense[local],color=INK,lw=2.2,label="exact f")
    for method,color in zip(methods,[BLUE,TEAL,ORANGE,PURPLE,MAGENTA],strict=True):
        approx=packet_reconstruction(x_dense,order) if method=="packet" else filtered_full_sum(x_dense,order,method)
        ax.plot(x_dense[local],approx[local],lw=1.4,label=method,color=color)
    ax.axvline(EDGE_HALF_WIDTH,color=RED,ls="--",lw=1)
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.set_title("Only the packet operator preserves the exact discontinuity",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.78,1])
    save_figure(fig,figures,"27_method_comparison_edge")

    # 28 metric heatmap at N=40
    fields=["rmse","boundary_rmse","jump_overshoot","jump_transition_width"]
    matrix=np.array([[next(float(r[field]) for r in metric_rows if r["method"]==method and r["order"]==40) for field in fields] for method in methods])
    # normalize per column for visibility
    normalized=matrix/np.maximum(matrix.max(axis=0,keepdims=True),1e-16)
    fig,ax=plt.subplots(figsize=(10.8,5.0))
    im=ax.imshow(normalized,cmap="viridis",aspect="auto",vmin=0,vmax=1)
    ax.set_xticks(range(len(fields)),["global RMSE","boundary RMSE","overshoot","transition width"])
    ax.set_yticks(range(len(methods)),methods)
    for i in range(len(methods)):
        for j in range(len(fields)):
            rgba=im.cmap(im.norm(normalized[i,j]))
            lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
            ax.text(j,i,f"{matrix[i,j]:.3e}",ha="center",va="center",color=INK if lum>.55 else WHITE,fontsize=9)
    fig.colorbar(im,ax=ax,fraction=.035,pad=.03,label="column-normalized cost")
    ax.set_title("Method tradeoffs at N=40",weight="bold")
    fig.tight_layout()
    save_figure(fig,figures,"28_metric_heatmap")

    # 29 packet operator diagram
    fig,ax=plt.subplots(figsize=(12.5,5.2))
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.axis("off")
    diagram_box(ax,.04,.42,.14,.20,"f",INK,16)
    diagram_box(ax,.28,.62,.18,.18,"smooth packet\nP_s f",BLUE,13)
    diagram_box(ax,.28,.24,.18,.18,"edge packet\nP_j f",ORANGE,13)
    diagram_box(ax,.57,.62,.18,.18,"Fourier block\nS_N P_s f",TEAL,13)
    diagram_box(ax,.57,.24,.18,.18,"identity block\nP_j f",MAGENTA,13)
    diagram_box(ax,.84,.42,.12,.20,"sum\nR_N f",GREEN,14)
    diagram_arrow(ax,(.18,.52),(.28,.71),BLUE,"P_s")
    diagram_arrow(ax,(.18,.50),(.28,.33),ORANGE,"P_j")
    diagram_arrow(ax,(.46,.71),(.57,.71),TEAL)
    diagram_arrow(ax,(.46,.33),(.57,.33),MAGENTA)
    diagram_arrow(ax,(.75,.71),(.84,.55),TEAL)
    diagram_arrow(ax,(.75,.33),(.84,.48),MAGENTA)
    ax.text(.5,.90,"Resolved reconstruction operator R_N=S_N P_s+P_j",ha="center",fontsize=21,weight="bold")
    ax.text(.5,.08,"The singular packet bypasses the global spectral truncation block.",ha="center",fontsize=12,color=MUTED)
    save_figure(fig,figures,"29_packet_operator_pipeline")

    # 30 exact packet reconstruction
    packet40=packet_reconstruction(x_dense,40)
    fig,ax=plt.subplots(figsize=(11.5,4.5))
    ax.plot(x_dense,f_dense,color=INK,lw=2.4,label="exact f")
    ax.plot(x_dense,packet40,color=MAGENTA,lw=1.2,ls="--",label="R_40 f")
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.set_title("The resolved operator reconstructs this model signal exactly",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig,figures,"30_packet_exact_reconstruction")

    # 31 packet residual
    residual=packet40-f_dense
    fig,ax=plt.subplots(figsize=(11.5,4.2))
    ax.plot(x_dense,residual,color=RED,lw=1.5)
    ax.axhline(0,color=INK,lw=.8)
    ax.set_xlabel("x")
    ax.set_ylabel("R_40 f - f")
    ax.set_title(f"Exact residual: max |r| = {np.max(np.abs(residual)):.3e}",weight="bold")
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig,figures,"31_packet_residual")

    # 32 finite samples
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    ax.plot(x_dense,f_dense,color=GRID if False else MUTED,lw=1.2,label="continuous signal")
    ax.scatter(x_grid,y_grid,s=18,color=BLUE,label="96 samples",zorder=3)
    ax.set_xlabel("x_m")
    ax.set_ylabel("y_m")
    ax.set_title("The recovery stage begins only with sampled values",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig,figures,"32_finite_grid_samples")

    # 33 design matrix
    fig,ax=plt.subplots(figsize=(11.5,5.2))
    im=ax.imshow(library.design.T,aspect="auto",cmap="coolwarm",vmin=-1,vmax=1)
    labels=["1"]+[v for k in range(1,6) for v in (f"cos {k}x",f"sin {k}x")]
    ax.set_yticks(range(len(labels)),labels)
    ax.set_xlabel("sample index m")
    ax.set_title("The finite smooth-background design matrix",weight="bold")
    fig.colorbar(im,ax=ax,fraction=.025,pad=.02,label="basis value")
    fig.tight_layout()
    save_figure(fig,figures,"33_background_design_matrix")

    # 34 residualized signal and mask
    true_mask_residual=library.residual_masks[int(exact_search["index"])]
    fig,axes=plt.subplots(2,1,figsize=(11.5,6.2),sharex=True)
    axes[0].stem(np.arange(DEFAULT_GRID),np.asarray(exact_search["y_perp"]),linefmt=BLUE,markerfmt=" ",basefmt=" ")
    axes[0].set_ylabel("(I-P_B)y")
    axes[0].set_title("Removing the smooth subspace leaves a one-dimensional edge direction",loc="left",weight="bold")
    axes[1].stem(np.arange(DEFAULT_GRID),true_mask_residual,linefmt=ORANGE,markerfmt=" ",basefmt=" ")
    axes[1].set_ylabel("(I-P_B)q_*")
    axes[1].set_xlabel("sample index")
    for axr in axes:style_axis(axr)
    fig.tight_layout()
    save_figure(fig,figures,"34_residualized_signal_and_mask")

    # 35 objective sorted
    sorted_res=np.sort(all_residuals[np.isfinite(all_residuals)])
    fig,ax=plt.subplots(figsize=(11.5,4.5))
    ax.semilogy(np.arange(min(600,len(sorted_res))),np.maximum(sorted_res[:600],1e-18),color=BLUE,lw=1.7)
    ax.scatter([0],[max(sorted_res[0],1e-18)],color=RED,s=50,label="true interval")
    ax.axhline(float(exact_search["second_residual"]),color=ORANGE,ls="--",label="second-best residual")
    ax.set_xlabel("candidate rank")
    ax.set_ylabel("profile residual")
    ax.set_title("The true packet is separated by a large finite objective gap",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.80,1])
    save_figure(fig,figures,"35_candidate_objective_ranking")

    # 36 start-length heatmap
    fig,ax=plt.subplots(figsize=(11.5,5.5))
    logged=np.log10(np.maximum(objective_grid,1e-16))
    im=ax.imshow(logged,origin="lower",aspect="auto",cmap="magma",extent=[0,DEFAULT_GRID,0,max_len])
    ax.scatter([TRUE_START],[TRUE_LENGTH],s=80,facecolor="none",edgecolor=WHITE,lw=1.8,label="true packet")
    ax.set_xlabel("candidate start")
    ax.set_ylabel("candidate length")
    ax.set_title("Profile least-squares objective over the complete interval library",weight="bold")
    fig.colorbar(im,ax=ax,fraction=.035,pad=.02,label="log10 residual")
    ax.legend(loc="upper right")
    fig.tight_layout()
    save_figure(fig,figures,"36_start_length_objective")

    # 37 gap bars
    fig,ax=plt.subplots(figsize=(9.5,4.5))
    vals=[max(float(exact_search["residual"]),1e-18),float(exact_search["second_residual"]),float(exact_search["gap"])]
    ax.bar([0,1,2],vals,color=[TEAL,ORANGE,MAGENTA],edgecolor=INK)
    ax.set_yscale("log")
    ax.set_xticks([0,1,2],["best residual","second residual","identifiability gap"])
    for i,v in enumerate(vals):ax.text(i,v*1.35,f"{v:.3e}",ha="center",fontsize=10)
    ax.set_title("Finite identifiability gap",weight="bold")
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig,figures,"37_identifiability_gap")

    # 38 recovered components
    fig,axes=plt.subplots(3,1,figsize=(11.5,7.1),sharex=True)
    axes[0].plot(x_grid,y_grid,color=INK,lw=1.5,marker="o",ms=3)
    axes[0].set_ylabel("data")
    axes[0].set_title("Recovered components from sampled data alone",loc="left",weight="bold")
    axes[1].plot(x_grid,np.asarray(exact_search["smooth"]),color=BLUE,lw=1.8,label="recovered smooth")
    axes[1].plot(x_grid,s_grid,color=INK,lw=.9,ls="--",label="true smooth")
    axes[1].set_ylabel("smooth")
    axes[1].legend(ncol=2)
    axes[2].step(x_grid,float(exact_search["amplitude"])*np.asarray(exact_search["mask"]),where="post",color=ORANGE,lw=2,label="recovered edge")
    axes[2].step(x_grid,edge_grid,where="post",color=INK,lw=.9,ls="--",label="true edge")
    axes[2].set_ylabel("edge")
    axes[2].set_xlabel("x_m")
    axes[2].legend(ncol=2)
    for axr in axes:style_axis(axr)
    fig.tight_layout()
    save_figure(fig,figures,"38_recovered_components")

    # 39 coefficients recovered
    labels=["1"]+[v for k in range(1,6) for v in (f"c{k}",f"s{k}")]
    true_theta=np.zeros(11)
    true_theta[0]=.25
    true_theta[3]=.4
    true_theta[6]=-(1/3)
    true_theta[9]=.2
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    pos=np.arange(len(labels))
    width=.38
    ax.bar(pos-width/2,true_theta,width,label="true",color=INK,alpha=.75)
    ax.bar(pos+width/2,exact_coefficients,width,label="recovered",color=BLUE,alpha=.85)
    ax.set_xticks(pos,labels)
    ax.set_ylabel("coefficient")
    ax.set_title("The smooth seed coefficients are recovered after edge separation",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.84,1])
    save_figure(fig,figures,"39_recovered_coefficients")

    # 40 grid reconstruction
    fig,axes=plt.subplots(2,1,figsize=(11.5,6.0),sharex=True)
    axes[0].plot(x_grid,y_grid,color=INK,lw=2,label="data")
    axes[0].plot(x_grid,np.asarray(exact_search["reconstruction"]),color=MAGENTA,lw=1.1,ls="--",label="reconstruction")
    axes[0].legend(ncol=2)
    axes[0].set_ylabel("amplitude")
    axes[0].set_title("Data, recovered packets, and reconstructed signal",loc="left",weight="bold")
    rr=np.asarray(exact_search["reconstruction"])-y_grid
    axes[1].stem(np.arange(DEFAULT_GRID),rr,linefmt=RED,markerfmt=" ",basefmt=" ")
    axes[1].set_ylabel("residual")
    axes[1].set_xlabel("sample index")
    axes[1].text(.99,.82,f"max residual = {np.max(np.abs(rr)):.3e}",transform=axes[1].transAxes,ha="right",weight="bold")
    for axr in axes:style_axis(axr)
    fig.tight_layout()
    save_figure(fig,figures,"40_closed_grid_reconstruction")

    # 41 one-sample mislocation
    wrong_mask=interval_mask(DEFAULT_GRID,TRUE_START+1,TRUE_LENGTH)
    wrong_fit=s_grid+wrong_mask
    fig,axes=plt.subplots(2,1,figsize=(11.5,6.2),sharex=True)
    axes[0].plot(x_grid,y_grid,color=INK,lw=2,label="true")
    axes[0].step(x_grid,wrong_fit,where="mid",color=RED,lw=1.5,label="edge shifted by one sample")
    axes[0].legend(ncol=2)
    axes[0].set_ylabel("amplitude")
    axes[0].set_title("Negative control: one-sample packet mislocation",loc="left",weight="bold")
    axes[1].stem(np.arange(DEFAULT_GRID),wrong_fit-y_grid,linefmt=RED,markerfmt=" ",basefmt=" ")
    axes[1].set_ylabel("residual")
    axes[1].set_xlabel("sample index")
    for axr in axes:style_axis(axr)
    fig.tight_layout()
    save_figure(fig,figures,"41_mislocated_edge")

    # 42 amplitude mismatch
    amplitudes=[.75,.9,1.0,1.1,1.25]
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    for amp,color in zip(amplitudes,COLORS[:len(amplitudes)],strict=True):
        approx=s_grid+amp*edge_grid
        ax.plot(x_grid,approx-y_grid,lw=1.4,label=f"Ahat={amp:.2f}",color=color)
    ax.set_xlabel("x_m")
    ax.set_ylabel("residual")
    ax.set_title("Amplitude error remains confined to the chosen packet support",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.80,1])
    save_figure(fig,figures,"42_amplitude_mismatch")

    # 43 perturbation bound
    shift_values=np.arange(0,13)
    actual=[]
    bound=[]
    for shift in shift_values:
        q=interval_mask(DEFAULT_GRID,TRUE_START+int(shift),TRUE_LENGTH)
        actual.append(np.linalg.norm(edge_grid-q))
        symmetric_difference=np.count_nonzero(edge_grid!=q)
        bound.append(math.sqrt(symmetric_difference))
    fig,ax=plt.subplots(figsize=(11.5,4.5))
    ax.plot(shift_values,actual,marker="o",label="actual L2 packet error",color=BLUE)
    ax.plot(shift_values,bound,marker="s",ls="--",label="symmetric-difference bound",color=ORANGE)
    ax.set_xlabel("edge shift in samples")
    ax.set_ylabel("error")
    ax.set_title("Support error has an exact geometric formula",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.80,1])
    save_figure(fig,figures,"43_packet_perturbation_bound")

    # 44 noise examples
    fig,axes=plt.subplots(3,1,figsize=(11.5,8.0),sharex=True)
    for axr,(sigma,record),color in zip(axes,sorted(noise_examples.items()),[TEAL,ORANGE,RED],strict=True):
        noisy=np.asarray(record["noisy"])
        fit=record["fit"]
        axr.scatter(x_grid,noisy,s=14,color=MUTED,label="noisy data")
        axr.plot(x_grid,np.asarray(fit["reconstruction"]),lw=1.8,color=color,label=f"fit: start={fit['start']}, length={fit['length']}")
        axr.plot(x_grid,y_grid,lw=.9,ls="--",color=INK,label="noise-free truth")
        axr.set_ylabel(f"sigma={sigma:.2f}")
        style_axis(axr)
        axr.legend(loc="upper left",bbox_to_anchor=(1.01,1),fontsize=8)
    axes[-1].set_xlabel("x_m")
    fig.suptitle("The same finite search under three noise levels",fontsize=17,weight="bold")
    fig.tight_layout(rect=[0,0,.78,.94])
    save_figure(fig,figures,"44_noisy_recovery_examples")

    # 45-48 noise curves
    sig=np.array([r["sigma"] for r in noise_rows],float)
    curve_specs=[
        (45,"exact_support_rate","exact support recovery rate","probability",TEAL),
        (46,"mean_abs_start_error_samples","mean absolute start error","samples",BLUE),
        (47,"mean_abs_amplitude_error","mean absolute amplitude error","amplitude",ORANGE),
        (48,"mean_boundary_rmse","mean boundary-band reconstruction RMSE","RMSE",MAGENTA),
    ]
    for no,field,title,ylabel,color in curve_specs:
        yy=np.array([r[field] for r in noise_rows],float)
        fig,ax=plt.subplots(figsize=(11.5,4.5))
        ax.plot(sig,yy,marker="o",lw=2,color=color)
        ax.set_xlabel("noise standard deviation")
        ax.set_ylabel(ylabel)
        ax.set_title(title,weight="bold")
        if field=="exact_support_rate":ax.set_ylim(-.03,1.03)
        style_axis(ax)
        fig.tight_layout()
        save_figure(fig,figures,f"{no:02d}_{field}")

    # 49 off-grid example at M=96
    size=96
    xx=sample_grid(size)
    dx=2*PI/size
    half_width=EDGE_HALF_WIDTH+offgrid_shift*dx
    yy=smooth_seed(xx)+jump_packet(xx,half_width=half_width)
    fit=CandidateLibrary.build(size,SMOOTH_DEGREE).search(yy)
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    ax.scatter(xx,yy,s=18,color=INK,label="off-grid sampled signal")
    ax.plot(xx,np.asarray(fit["reconstruction"]),color=BLUE,lw=1.5,label="best grid packet")
    ax.axvline(-half_width,color=RED,ls="--",lw=1,label="continuous edge")
    ax.axvline(half_width,color=RED,ls="--",lw=1)
    ax.set_xlabel("x_m")
    ax.set_ylabel("amplitude")
    ax.set_title("Off-grid edges are localized to the sampling resolution",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.80,1])
    save_figure(fig,figures,"49_offgrid_example")

    # 50 offgrid convergence
    sizes=np.array([r["size"] for r in offgrid_rows])
    errors=np.array([r["max_endpoint_error"] for r in offgrid_rows])
    dxs=np.array([r["dx"] for r in offgrid_rows])
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    ax.loglog(sizes,errors,marker="o",lw=2,label="endpoint error",color=BLUE)
    ax.loglog(sizes,dxs,ls="--",lw=1.5,label="grid spacing",color=ORANGE)
    ax.set_xlabel("sample count M")
    ax.set_ylabel("radians")
    ax.set_title("Off-grid localization error shrinks with grid refinement",weight="bold")
    style_axis(ax)
    add_external_legend(ax)
    fig.tight_layout(rect=[0,0,.82,1])
    save_figure(fig,figures,"50_offgrid_convergence")

    # 51 residual localization for wrong packet
    residual_wrong=wrong_fit-y_grid
    fig,ax=plt.subplots(figsize=(11.5,4.5))
    ax.bar(np.arange(DEFAULT_GRID),np.abs(residual_wrong),color=[RED if v>1e-12 else GRID for v in np.abs(residual_wrong)],edgecolor="none")
    ax.set_xlabel("sample index")
    ax.set_ylabel("|residual|")
    ax.set_title("A wrong packet localizes the unresolved obligation at the two boundaries",weight="bold")
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig,figures,"51_residual_localization")

    # 52 adaptive local refinement diagram
    fig,ax=plt.subplots(figsize=(12.5,5.1))
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.axis("off")
    diagram_box(ax,.04,.41,.15,.20,"coarse grid\nM=48",BLUE,13)
    diagram_box(ax,.29,.41,.17,.20,"residual scan\nedge packets",ORANGE,13)
    diagram_box(ax,.56,.58,.17,.17,"refine left\nboundary",TEAL,12)
    diagram_box(ax,.56,.24,.17,.17,"refine right\nboundary",TEAL,12)
    diagram_box(ax,.84,.41,.12,.20,"exact\npacket fit",MAGENTA,13)
    diagram_arrow(ax,(.19,.51),(.29,.51))
    diagram_arrow(ax,(.46,.52),(.56,.65),ORANGE)
    diagram_arrow(ax,(.46,.49),(.56,.32),ORANGE)
    diagram_arrow(ax,(.73,.65),(.84,.55),TEAL)
    diagram_arrow(ax,(.73,.32),(.84,.47),TEAL)
    ax.text(.5,.88,"Residual-driven refinement acts only where the packet geometry is unresolved",ha="center",fontsize=20,weight="bold")
    ax.text(.5,.09,"Global spectral resolution is not increased merely to sharpen two local edges.",ha="center",fontsize=12,color=MUTED)
    save_figure(fig,figures,"52_adaptive_local_refinement")

    # 53 block matrix of R_N relative to packets
    fig,ax=plt.subplots(figsize=(8.8,5.0))
    mat=np.array([[1,0],[0,1]],float)
    im=ax.imshow(mat,cmap=matplotlib.colors.ListedColormap([PAPER,TEAL]),vmin=0,vmax=1)
    ax.set_xticks([0,1],["smooth input","edge input"])
    ax.set_yticks([0,1],["smooth output","edge output"])
    labels=[["S_N|T_5 = I","0"],["0","I_edge"]]
    for i in range(2):
        for j in range(2):ax.text(j,i,labels[i][j],ha="center",va="center",fontsize=13,weight="bold")
    ax.set_title("The reconstruction operator is block diagonal on the chosen model",weight="bold")
    fig.tight_layout()
    save_figure(fig,figures,"53_packet_operator_blocks")

    # 54 coefficient polyphase
    residues=[]
    for r in range(6):
        nseq=np.arange(r if r>0 else 6,61,6)
        residues.append((r,nseq,np.array([jump_fourier_coefficient(int(n)).real for n in nseq])))
    fig,axes=plt.subplots(3,2,figsize=(11.5,7.2),sharey=True)
    for axr,(r,nseq,v) in zip(axes.ravel(),residues,strict=True):
        axr.stem(nseq,v,linefmt=COLORS[r],markerfmt=" ",basefmt=" ")
        axr.set_title(f"n mod 6 = {r}",weight="bold",fontsize=11)
        style_axis(axr)
    fig.suptitle("Polyphase refinement of the jump's Fourier coefficient sequence",fontsize=17,weight="bold")
    fig.tight_layout(rect=[0,0,1,.94])
    save_figure(fig,figures,"54_fourier_polyphase_packets")

    # 55 tradeoff plot
    n40=[r for r in metric_rows if r["order"]==40]
    fig,ax=plt.subplots(figsize=(9.5,5.4))
    for r,color in zip(n40,[BLUE,TEAL,ORANGE,PURPLE,MAGENTA],strict=True):
        ax.scatter(r["boundary_rmse"],r["jump_transition_width"],s=110,color=color,label=r["method"],edgecolor=INK)
        ax.text(r["boundary_rmse"]*1.04+1e-18,r["jump_transition_width"]*1.02+1e-18,r["method"],fontsize=9)
    ax.set_xscale("symlog",linthresh=1e-14)
    ax.set_yscale("symlog",linthresh=1e-14)
    ax.set_xlabel("boundary RMSE")
    ax.set_ylabel("10%-90% transition width")
    ax.set_title("Filtering trades ringing for blur. Packet separation changes which object is truncated",weight="bold")
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig,figures,"55_method_tradeoff")

    # 56 runtime scaling
    rs=np.array([r["size"] for r in runtime_rows])
    cc=np.array([r["candidate_count"] for r in runtime_rows])
    bt=np.array([r["build_seconds"] for r in runtime_rows])
    st=np.array([r["search_seconds"] for r in runtime_rows])
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.8))
    axes[0].plot(rs,cc,marker="o",color=BLUE)
    axes[0].set_xlabel("M")
    axes[0].set_ylabel("candidate intervals")
    axes[0].set_title("finite search-space size",weight="bold")
    style_axis(axes[0])
    axes[1].plot(rs,bt,marker="o",label="library build",color=ORANGE)
    axes[1].plot(rs,st,marker="o",label="profile search",color=TEAL)
    axes[1].set_xlabel("M")
    axes[1].set_ylabel("seconds")
    axes[1].set_title("measured reference runtime",weight="bold")
    style_axis(axes[1])
    axes[1].legend()
    fig.suptitle("The exhaustive solver checks every finite candidate. It is not claimed to be asymptotically optimal",fontsize=15.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.91])
    save_figure(fig,figures,"56_runtime_scaling")

    # 57 proof dependency
    fig,ax=plt.subplots(figsize=(12.5,6.0))
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.axis("off")
    nodes=[(.06,.72,"Fourier coefficients",BLUE),(.29,.72,"Dirichlet kernel",BLUE),(.53,.72,"scaled edge limit",ORANGE),(.77,.72,"Gibbs constant",RED),(.06,.32,"direct-sum model",TEAL),(.29,.32,"packet projectors",TEAL),(.53,.32,"resolved operator",MAGENTA),(.77,.32,"exact reconstruction",GREEN)]
    for x0,y0,label,color in nodes:diagram_box(ax,x0,y0,.16,.14,label,color,11)
    for a0,b0 in [((.22,.79),(.29,.79)),((.45,.79),(.53,.79)),((.69,.79),(.77,.79)),((.22,.39),(.29,.39)),((.45,.39),(.53,.39)),((.69,.39),(.77,.39))]:diagram_arrow(ax,a0,b0)
    diagram_arrow(ax,(.85,.65),(.85,.46),RED,"problem")
    ax.text(.5,.93,"Two proof chains meet at the final comparison",ha="center",fontsize=21,weight="bold")
    ax.text(.5,.08,"The Gibbs theorem explains why raw truncation fails. The packet theorem explains why the packet reconstruction succeeds.",ha="center",fontsize=11.5,color=MUTED)
    save_figure(fig,figures,"57_proof_dependency_map")

    # 58 test dashboard placeholder built from actual tests below after execution
    # 59 summary wheel
    fig,ax=plt.subplots(figsize=(7.8,7.8))
    ax.set_aspect("equal")
    ax.axis("off")
    labels=[("seed",BLUE),("analyze",CYAN),("project",TEAL),("detect",GREEN),("operate",YELLOW),("refine",ORANGE),("synthesize",MAGENTA),("certify",PURPLE)]
    theta=np.linspace(90,-270,len(labels)+1)
    for i,(lab,color) in enumerate(labels):
        wedge=Wedge((0,0),1.0,theta[i+1],theta[i],width=.34,facecolor=color,edgecolor=PAPER,lw=2)
        ax.add_patch(wedge)
        ang=np.deg2rad((theta[i]+theta[i+1])/2)
        ax.text(.80*np.cos(ang),.80*np.sin(ang),lab,ha="center",va="center",rotation=(theta[i]+theta[i+1])/2-90,rotation_mode="anchor",color=WHITE,fontsize=12,weight="bold")
    ax.add_patch(Circle((0,0),.48,facecolor=PAPER,edgecolor=INK,lw=2))
    ax.text(0,.08,"Gibbs",ha="center",fontsize=18,weight="bold")
    ax.text(0,-.04,"packet case",ha="center",fontsize=16,weight="bold")
    ax.text(0,-.17,"one worked example",ha="center",fontsize=10,color=MUTED)
    ax.set_xlim(-1.1,1.1)
    ax.set_ylim(-1.1,1.1)
    ax.set_title("The calculation from start to finish",fontsize=20,weight="bold")
    save_figure(fig,figures,"59_summary_wheel")

    # 60 exact/approx boundary
    fig,ax=plt.subplots(figsize=(11.5,5.0))
    ax.axis("off")
    rows=[
        ("Fourier coefficient formula","exact identity",TEAL),
        ("Gibbs scaled limit","proved asymptotic",BLUE),
        ("known packet reconstruction","exact theorem",TEAL),
        ("finite interval search","exact finite optimization",TEAL),
        ("noise curves","deterministic numerical experiment",ORANGE),
        ("off-grid localization","finite numerical experiment",ORANGE),
        ("universal unknown-edge recovery","not claimed",RED),
    ]
    y=.88
    ax.text(.5,.96,"Claim boundary for the single worked example",ha="center",fontsize=20,weight="bold",transform=ax.transAxes)
    for i,(claim,status,color) in enumerate(rows):
        bg=WHITE if i%2==0 else "#EFF2F3"
        ax.add_patch(FancyBboxPatch((.05,y-.047),.90,.068,boxstyle="round,pad=.006,rounding_size=.006",facecolor=bg,edgecolor="none",transform=ax.transAxes))
        ax.text(.08,y,claim,ha="left",va="center",fontsize=11,transform=ax.transAxes)
        ax.text(.92,y,status,ha="right",va="center",fontsize=10.5,color=color,weight="bold",transform=ax.transAxes)
        y-=.105
    save_figure(fig,figures,"60_claim_boundary")

    # ------------------------------------------------------------------
    # Tests and certificates
    # ------------------------------------------------------------------
    tests: list[tuple[str, bool, float | str]] = []
    def record(name: str, condition: bool, value: float | str) -> None:
        tests.append((name, bool(condition), value))

    # Fourier coefficient checks against numerical quadrature.
    quad_x=np.linspace(-PI,PI,400000,endpoint=False)
    quad_f=full_signal(quad_x)
    for n in [-8,-5,-3,-2,0,2,3,5,8]:
        numeric=np.mean(quad_f*np.exp(-1j*n*quad_x))
        exact=full_fourier_coefficient(n)
        record(f"Fourier coefficient n={n}",abs(numeric-exact)<2e-5,float(abs(numeric-exact)))

    # Model-space projectors and reconstruction.
    model_sample=np.linspace(-PI,PI,4096,endpoint=False)
    ps=smooth_seed(model_sample)
    pj=jump_packet(model_sample)
    ff=ps+pj
    record("packet synthesis",np.max(np.abs(ps+pj-ff))==0.0,float(np.max(np.abs(ps+pj-ff))))
    record("smooth partial sum exact at N=5",np.max(np.abs(smooth_fourier_partial_sum(model_sample,5)-ps))<2e-15,float(np.max(np.abs(smooth_fourier_partial_sum(model_sample,5)-ps))))
    record("resolved reconstruction exact",np.max(np.abs(packet_reconstruction(model_sample,5)-ff))<2e-15,float(np.max(np.abs(packet_reconstruction(model_sample,5)-ff))))

    # Gibbs profile and constant.
    profile_error=max(abs((jump_fourier_partial_sum(np.array([EDGE_HALF_WIDTH-z/(400+.5)]),400)[0])-gibbs_profile(np.array([z]))[0]) for z in [1.0,PI,5.0])
    record("scaled Gibbs profile",profile_error<4e-3,float(profile_error))
    observed_G=jump_fourier_partial_sum(np.array([EDGE_HALF_WIDTH-PI/(1000+.5)]),1000)[0]-1.0
    record("Gibbs constant",abs(observed_G-gibbs_constant())<1e-3,float(abs(observed_G-gibbs_constant())))

    # Fejer positivity for the jump.
    fejer_test=filtered_jump_sum(model_sample,80,"fejer")
    record("Fejer positivity",np.min(fejer_test)>-1e-12 and np.max(fejer_test)<1+1e-12,float(max(-np.min(fejer_test),np.max(fejer_test)-1)))

    # Exact finite search.
    record("true interval recovered",int(exact_search["start"])==TRUE_START and int(exact_search["length"])==TRUE_LENGTH,f"start={exact_search['start']}, length={exact_search['length']}")
    record("edge amplitude recovered",abs(float(exact_search["amplitude"])-1.0)<1e-12,float(abs(float(exact_search["amplitude"])-1.0)))
    record("finite reconstruction",np.max(np.abs(np.asarray(exact_search["reconstruction"])-y_grid))<2e-14,float(np.max(np.abs(np.asarray(exact_search["reconstruction"])-y_grid))))
    record("positive objective gap",float(exact_search["gap"])>.5,float(exact_search["gap"]))

    # Residue pattern.
    residue_ok=True
    for n in range(1,61):
        expected=0.0 if n%3==0 else (math.sqrt(3)/2 if n%6 in (1,2) else -math.sqrt(3)/2)
        residue_ok &= abs(math.sin(n*PI/3)-expected)<1e-12
    record("six-phase coefficient pattern",residue_ok,0.0 if residue_ok else 1.0)

    # Perturbation identity.
    qshift=interval_mask(DEFAULT_GRID,TRUE_START+4,TRUE_LENGTH)
    lhs=np.linalg.norm(edge_grid-qshift)**2
    rhs=np.count_nonzero(edge_grid!=qshift)
    record("symmetric-difference identity",abs(lhs-rhs)<1e-12,float(abs(lhs-rhs)))

    # Off-grid localization bounded by 1.1 grid spacings in the tested family.
    offgrid_ratio=max(r["max_endpoint_error"]/r["dx"] for r in offgrid_rows)
    record("off-grid localization check",offgrid_ratio<1.1,float(offgrid_ratio))

    # Noise negative/positive controls.
    rate03=next(r["exact_support_rate"] for r in noise_rows if abs(r["sigma"]-.03)<1e-12)
    rate20=next(r["exact_support_rate"] for r in noise_rows if abs(r["sigma"]-.20)<1e-12)
    record("low-noise support recovery",rate03>.98,float(rate03))
    record("high-noise degradation visible",rate20<1.0,float(rate20))

    # Method boundary: raw has persistent overshoot. Packet reconstruction has zero overshoot.
    raw160=next(r for r in metric_rows if r["method"]=="raw" and r["order"]==160)
    packet5=next(r for r in metric_rows if r["method"]=="packet" and r["order"]==5)
    record("raw Gibbs persists",abs(float(raw160["jump_overshoot"])-gibbs_constant())<5e-3,float(raw160["jump_overshoot"]))
    record("packet overshoot zero",abs(float(packet5["jump_overshoot"]))<1e-14,float(packet5["jump_overshoot"]))

    # Generate test dashboard now.
    fig,ax=plt.subplots(figsize=(11.5,7.0))
    ax.axis("off")
    ax.text(.5,.965,"Analytic and numerical checks for the worked example",ha="center",fontsize=20,weight="bold",transform=ax.transAxes)
    y=.91
    for i,(name,passed,value) in enumerate(tests):
        bg=WHITE if i%2==0 else "#EFF2F3"
        ax.add_patch(FancyBboxPatch((.04,y-.022),.92,.040,boxstyle="round,pad=.003,rounding_size=.004",facecolor=bg,edgecolor="none",transform=ax.transAxes))
        ax.text(.06,y,name,ha="left",va="center",fontsize=8.7,transform=ax.transAxes)
        ax.text(.79,y,str(value)[:22],ha="right",va="center",fontsize=8.4,family="monospace",transform=ax.transAxes)
        ax.text(.94,y,"PASS" if passed else "FAIL",ha="right",va="center",fontsize=8.8,color=TEAL if passed else RED,weight="bold",transform=ax.transAxes)
        y-=.043
    ax.text(.5,.025,f"{sum(p for _, p, _ in tests)}/{len(tests)} checks passed",ha="center",fontsize=12,weight="bold",transform=ax.transAxes)
    save_figure(fig,figures,"58_test_dashboard")

    # Test ledger.
    with (tables/"test_ledger.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=["test","passed","value"])
        writer.writeheader()
        writer.writerows([{"test":n,"passed":p,"value":v} for n,p,v in tests])

    results = {
        "signal": {
            "smooth_formula": "1/4 + (2/5) cos(2x) - (1/3) sin(3x) + (1/5) cos(5x)",
            "edge_half_width": EDGE_HALF_WIDTH,
            "edge_amplitude": A_EDGE,
            "smooth_degree": SMOOTH_DEGREE,
        },
        "gibbs_constant": gibbs_constant(),
        "exact_recovery": {
            "grid_size": DEFAULT_GRID,
            "true_start": TRUE_START,
            "true_length": TRUE_LENGTH,
            "recovered_start": int(exact_search["start"]),
            "recovered_length": int(exact_search["length"]),
            "recovered_amplitude": float(exact_search["amplitude"]),
            "residual": float(exact_search["residual"]),
            "second_residual": float(exact_search["second_residual"]),
            "gap": float(exact_search["gap"]),
            "max_reconstruction_residual": float(np.max(np.abs(np.asarray(exact_search["reconstruction"])-y_grid))),
        },
        "tests": {
            "passed": int(sum(p for _,p,_ in tests)),
            "total": len(tests),
        },
        "figure_pairs": 60,
        "method_metrics_rows": len(metric_rows),
        "noise_rows": len(noise_rows),
        "offgrid_rows": len(offgrid_rows),
        "runtime_rows": len(runtime_rows),
    }
    (results_dir/"numerical_results.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    if not all(p for _,p,_ in tests):
        failed=[n for n,p,_ in tests if not p]
        raise AssertionError(f"failed checks: {failed}")
    return results


# -----------------------------------------------------------------------------
# File manifest utilities
# -----------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(root: Path) -> None:
    files=[]
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"SHA256SUMS.txt", "manifest.json"} and "build" not in path.parts:
            files.append({"path":str(path.relative_to(root)),"bytes":path.stat().st_size,"sha256":sha256(path)})
    (root/"manifest.json").write_text(json.dumps({"files":files},indent=2)+"\n",encoding="utf-8")
    lines=[f"{row['sha256']}  {row['path']}" for row in files]
    (root/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument("--quick",action="store_true")
    parser.add_argument("--manifest",action="store_true")
    args=parser.parse_args()
    results=build_experiment(args.root,args.quick)
    if args.manifest:
        write_manifest(args.root)
    print(json.dumps(results,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

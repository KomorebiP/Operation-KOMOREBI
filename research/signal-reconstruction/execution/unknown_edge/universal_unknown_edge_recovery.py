from __future__ import annotations

"""Universal unknown-edge recovery in a declared finite-rate packet class.

This single file contains the mathematical model, exact and numerical recovery
algorithms, tests, figures, tables, and machine-readable result records used by
its companion paper.
"""

import argparse
import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment
from scipy.linalg import subspace_angles
import sympy as sp

Array = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]
PI = math.pi
TAU = 2.0 * math.pi

INK = "#17202A"
MUTED = "#566573"
PAPER = "#FAFAF7"
BLUE = "#2E86AB"
TEAL = "#2A9D8F"
ORANGE = "#F4A261"
RED = "#E76F51"
MAGENTA = "#A23E8C"
PURPLE = "#6C5CE7"
GREEN = "#6A994E"
YELLOW = "#E9C46A"
GRID = "#D5D8DC"
WHITE = "#FFFFFF"
PALETTE = [BLUE, TEAL, ORANGE, MAGENTA, PURPLE, GREEN, RED, YELLOW]

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


def wrap_angle(x: NDArray[np.float64] | float) -> NDArray[np.float64] | float:
    return np.mod(x, TAU)


def circular_distance(a: float, b: float) -> float:
    d = abs(a - b) % TAU
    return min(d, TAU - d)


def pairwise_circular_gaps(tau: Array) -> Array:
    t = np.sort(wrap_angle(np.asarray(tau, dtype=float)))
    return np.diff(np.r_[t, t[0] + TAU])


def save_figure(fig: plt.Figure, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight", pad_inches=0.06)
    fig.savefig(out_dir / f"{name}.png", dpi=180, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def diagram_axes(figsize: tuple[float, float] = (12.0, 5.5)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")
    return fig, ax


def draw_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    face: str = WHITE,
    edge: str = INK,
    fontsize: float = 11.0,
) -> FancyBboxPatch:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.6,
    )
    ax.add_patch(patch)
    label = ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        multialignment="center",
        linespacing=1.12,
        fontsize=fontsize,
        zorder=5,
    )
    fig = ax.figure
    for _ in range(12):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        box = label.get_window_extent(renderer=renderer)
        (x0, y0), (x1, y1) = ax.transData.transform(((x, y), (x + width, y + height)))
        aw = abs(x1 - x0) * 0.84
        ah = abs(y1 - y0) * 0.80
        if box.width <= aw and box.height <= ah:
            break
        label.set_fontsize(max(7.5, label.get_fontsize() * 0.90))
    return patch


def draw_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = INK,
    text: str | None = None,
    text_offset: tuple[float, float] = (0.0, 0.0),
    connectionstyle: str = "arc3",
) -> FancyArrowPatch:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.7,
        color=color,
        connectionstyle=connectionstyle,
    )
    ax.add_patch(arrow)
    if text is not None:
        mx = (start[0] + end[0]) / 2 + text_offset[0]
        my = (start[1] + end[1]) / 2 + text_offset[1]
        ax.text(
            mx,
            my,
            text,
            ha="center",
            va="center",
            fontsize=9.3,
            color=color,
            bbox={"boxstyle": "round,pad=0.12", "facecolor": PAPER, "edgecolor": "none"},
        )
    return arrow


# -----------------------------------------------------------------------------
# Exact signal model
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class EdgeModel:
    """Periodic piecewise-constant packet with canonical zero mean."""

    locations: Array
    jumps: Array

    def __post_init__(self) -> None:
        locations = np.asarray(self.locations, dtype=float)
        jumps = np.asarray(self.jumps, dtype=float)
        if locations.ndim != 1 or jumps.ndim != 1 or locations.size != jumps.size:
            raise ValueError("locations and jumps must be one-dimensional and equally sized")
        if locations.size < 2:
            raise ValueError("a nonconstant periodic packet needs at least two jumps")
        locations = np.mod(locations, TAU)
        order = np.argsort(locations)
        locations = locations[order]
        jumps = jumps[order]
        if np.min(pairwise_circular_gaps(locations)) <= 1e-12:
            raise ValueError("jump locations must be distinct")
        if abs(float(np.sum(jumps))) > 1e-9:
            raise ValueError("periodic jump amplitudes must sum to zero")
        if np.min(np.abs(jumps)) <= 1e-12:
            raise ValueError("zero jump amplitudes must be removed from the model")
        object.__setattr__(self, "locations", locations)
        object.__setattr__(self, "jumps", jumps)

    @property
    def order(self) -> int:
        return int(self.locations.size)

    @property
    def min_separation(self) -> float:
        return float(np.min(pairwise_circular_gaps(self.locations)))

    def fourier(self, n: int) -> complex:
        if n == 0:
            return 0.0 + 0.0j
        return complex(np.sum(self.jumps * np.exp(-1j * n * self.locations)) / (2j * PI * n))

    def moments(self, indices: Sequence[int]) -> ComplexArray:
        n = np.asarray(indices, dtype=int)
        return np.asarray(
            [np.sum(self.jumps * np.exp(-1j * int(k) * self.locations)) for k in n],
            dtype=np.complex128,
        )

    def values(self, x: Array) -> Array:
        xw = np.mod(np.asarray(x, dtype=float), TAU)
        tau = self.locations
        a = self.jumps
        lengths = np.diff(np.r_[tau, tau[0] + TAU])
        cumulative = np.cumsum(a)
        base = -float(np.sum(lengths * cumulative) / TAU)
        out = np.full_like(xw, base, dtype=float)
        for location, jump in zip(tau, a, strict=True):
            out += jump * (xw >= location)
        # Correct the branch cut. Jumps after tau[0] were applied, but values below
        # tau[0] must also include the jumps from the previous cycle.
        out[xw < tau[0]] += float(np.sum(a))
        return out

    def segment_values(self) -> tuple[Array, Array]:
        tau = self.locations
        lengths = np.diff(np.r_[tau, tau[0] + TAU])
        cumulative = np.cumsum(self.jumps)
        base = -float(np.sum(lengths * cumulative) / TAU)
        return lengths, base + cumulative


@dataclass(frozen=True)
class BandlimitedBackground:
    degree: int
    coefficients: dict[int, complex]

    def __post_init__(self) -> None:
        if self.degree < 0:
            raise ValueError("degree must be nonnegative")
        coeffs = dict(self.coefficients)
        for n in coeffs:
            if abs(n) > self.degree:
                raise ValueError("coefficient outside declared bandlimit")
        for n in range(1, self.degree + 1):
            if abs(coeffs.get(-n, 0.0) - np.conj(coeffs.get(n, 0.0))) > 1e-10:
                raise ValueError("coefficients must define a real signal")
        if abs(complex(coeffs.get(0, 0.0)).imag) > 1e-10:
            raise ValueError("zero-frequency coefficient must be real")
        object.__setattr__(self, "coefficients", coeffs)

    def fourier(self, n: int) -> complex:
        return complex(self.coefficients.get(int(n), 0.0 + 0.0j))

    def values(self, x: Array) -> Array:
        x = np.asarray(x, dtype=float)
        out = np.zeros_like(x, dtype=np.complex128)
        for n, value in self.coefficients.items():
            out += value * np.exp(1j * n * x)
        return np.real_if_close(out, tol=1000).astype(float)


@dataclass(frozen=True)
class UniversalSignal:
    background: BandlimitedBackground
    edge: EdgeModel

    def fourier(self, n: int) -> complex:
        return self.background.fourier(n) + self.edge.fourier(n)

    def values(self, x: Array) -> Array:
        return self.background.values(x) + self.edge.values(x)


@dataclass
class RecoveryResult:
    order: int
    locations: Array
    jumps: Array
    annihilator_ascending: ComplexArray
    hankel_singular_values: Array
    moment_indices: NDArray[np.int64]
    measured_moments: ComplexArray
    recurrence_residual: float
    amplitude_residual: float
    min_root_separation: float
    hankel_condition: float
    vandermonde_condition: float

    def edge_model(self) -> EdgeModel:
        jumps = np.asarray(np.real(self.jumps), dtype=float)
        jumps -= float(np.mean(jumps))
        # The correction above is at roundoff scale when the periodic condition
        # is satisfied. It keeps the constructor strict in noisy examples.
        return EdgeModel(self.locations, jumps)


def generate_background(degree: int, rng: np.random.Generator, scale: float = 0.35) -> BandlimitedBackground:
    coeffs: dict[int, complex] = {0: float(rng.normal(scale=scale))}
    for n in range(1, degree + 1):
        z = scale * (rng.normal() + 1j * rng.normal()) / math.sqrt(2.0)
        coeffs[n] = z
        coeffs[-n] = np.conj(z)
    return BandlimitedBackground(degree, coeffs)


def generate_edge_model(
    order: int,
    rng: np.random.Generator,
    min_separation: float = 0.28,
    amplitude_scale: float = 1.0,
) -> EdgeModel:
    if order < 2:
        raise ValueError("order must be at least two")
    for _ in range(100000):
        tau = np.sort(rng.uniform(0.0, TAU, order))
        if np.min(pairwise_circular_gaps(tau)) >= min_separation:
            break
    else:
        raise RuntimeError("could not generate separated jump locations")
    jumps = rng.normal(scale=amplitude_scale, size=order)
    jumps -= float(np.mean(jumps))
    while np.min(np.abs(jumps)) < 0.08 * amplitude_scale:
        jumps = rng.normal(scale=amplitude_scale, size=order)
        jumps -= float(np.mean(jumps))
    return EdgeModel(tau, jumps)


def fourier_measurements(signal: UniversalSignal, indices: Sequence[int]) -> dict[int, complex]:
    return {int(n): signal.fourier(int(n)) for n in indices}


def edge_moments_from_fourier(
    measurements: dict[int, complex],
    indices: Sequence[int],
) -> ComplexArray:
    out = []
    for n in indices:
        if n == 0:
            raise ValueError("edge moments use nonzero Fourier indices")
        out.append(2j * PI * n * measurements[int(n)])
    return np.asarray(out, dtype=np.complex128)


def hankel_from_consecutive_moments(moments: ComplexArray, rows: int, cols: int) -> ComplexArray:
    if moments.size < rows + cols - 1:
        raise ValueError("not enough consecutive moments")
    return np.asarray([[moments[i + j] for j in range(cols)] for i in range(rows)], dtype=np.complex128)


def estimate_order_from_hankel(moments: ComplexArray, upper_bound: int, tolerance: float = 1e-10) -> tuple[int, Array]:
    H = hankel_from_consecutive_moments(moments, upper_bound, upper_bound)
    singular = np.linalg.svd(H, compute_uv=False)
    if singular[0] == 0:
        return 0, singular.astype(float)
    order = int(np.sum(singular > tolerance * singular[0]))
    return order, singular.astype(float)


def recover_unknown_edges(
    measurements: dict[int, complex],
    background_degree_bound: int,
    edge_order_bound: int,
    known_order: int | None = None,
    rank_tolerance: float = 1e-10,
    project_roots_to_circle: bool = True,
) -> RecoveryResult:
    """Recover all edge locations and jumps from consecutive high Fourier modes."""
    n0 = int(background_degree_bound) + 1
    moment_indices = np.arange(n0, n0 + 2 * edge_order_bound, dtype=np.int64)
    moments = edge_moments_from_fourier(measurements, moment_indices)
    estimated_order, singular = estimate_order_from_hankel(moments, edge_order_bound, rank_tolerance)
    order = int(known_order if known_order is not None else estimated_order)
    if order < 1 or order > edge_order_bound:
        raise ValueError(f"invalid recovered edge order {order}")

    H = hankel_from_consecutive_moments(moments, order, order)
    b = moments[order : 2 * order]
    q_low = np.linalg.solve(H, -b)
    annihilator = np.r_[q_low, 1.0 + 0.0j]
    roots = np.roots(annihilator[::-1])
    if project_roots_to_circle:
        if np.min(np.abs(roots)) <= 1e-15:
            raise ValueError("annihilator produced a zero root")
        roots = roots / np.abs(roots)
    locations = np.mod(-np.angle(roots), TAU)
    sort_order = np.argsort(locations)
    locations = locations[sort_order]
    roots = roots[sort_order]

    # Use all available high moments for the amplitude solve.
    V = np.asarray(
        [[roots[j] ** int(n) for j in range(order)] for n in moment_indices],
        dtype=np.complex128,
    )
    jumps, _, _, _ = np.linalg.lstsq(V, moments, rcond=None)
    recurrence_values = []
    for start in range(0, moments.size - order):
        recurrence_values.append(np.dot(annihilator, moments[start : start + order + 1]))
    recurrence_residual = float(np.max(np.abs(recurrence_values))) if recurrence_values else 0.0
    amplitude_residual = float(np.linalg.norm(V @ jumps - moments))
    min_sep = float(np.min(pairwise_circular_gaps(locations)))
    hankel_condition = float(np.linalg.cond(H))
    vandermonde_condition = float(np.linalg.cond(V[:order, :]))
    return RecoveryResult(
        order=order,
        locations=locations,
        jumps=jumps,
        annihilator_ascending=annihilator,
        hankel_singular_values=singular,
        moment_indices=moment_indices,
        measured_moments=moments,
        recurrence_residual=recurrence_residual,
        amplitude_residual=amplitude_residual,
        min_root_separation=min_sep,
        hankel_condition=hankel_condition,
        vandermonde_condition=vandermonde_condition,
    )


def match_edge_models(true_edge: EdgeModel, recovered: RecoveryResult) -> dict[str, float | Array]:
    if true_edge.order != recovered.order:
        return {
            "location_error_max": float("inf"),
            "location_error_rmse": float("inf"),
            "jump_error_max": float("inf"),
            "jump_error_rmse": float("inf"),
            "matched_locations": recovered.locations,
            "matched_jumps": recovered.jumps,
        }
    cost = np.asarray(
        [[circular_distance(float(a), float(b)) for b in recovered.locations] for a in true_edge.locations],
        dtype=float,
    )
    rows, cols = linear_sum_assignment(cost)
    matched_locations = recovered.locations[cols]
    matched_jumps = recovered.jumps[cols]
    loc_errors = np.asarray([circular_distance(float(true_edge.locations[r]), float(matched_locations[i])) for i, r in enumerate(rows)])
    jump_errors = np.abs(true_edge.jumps[rows] - matched_jumps)
    return {
        "location_error_max": float(np.max(loc_errors)),
        "location_error_rmse": float(np.sqrt(np.mean(loc_errors**2))),
        "jump_error_max": float(np.max(jump_errors)),
        "jump_error_rmse": float(np.sqrt(np.mean(jump_errors**2))),
        "matched_locations": matched_locations,
        "matched_jumps": matched_jumps,
    }


def reconstruct_background(
    measurements: dict[int, complex],
    recovered_edge: EdgeModel,
    degree: int,
) -> BandlimitedBackground:
    coeffs: dict[int, complex] = {}
    for n in range(-degree, degree + 1):
        coeffs[n] = measurements[n] - recovered_edge.fourier(n)
    # Force the exact real-signal symmetry at roundoff scale.
    coeffs[0] = complex(float(np.real(coeffs[0])), 0.0)
    for n in range(1, degree + 1):
        avg = 0.5 * (coeffs[n] + np.conj(coeffs[-n]))
        coeffs[n] = avg
        coeffs[-n] = np.conj(avg)
    return BandlimitedBackground(degree, coeffs)


def raw_fourier_partial(measurements: dict[int, complex], x: Array, order: int) -> Array:
    out = np.zeros_like(x, dtype=np.complex128)
    for n in range(-order, order + 1):
        out += measurements.get(n, 0.0) * np.exp(1j * n * x)
    return np.real_if_close(out, tol=1000).astype(float)


def packet_resolved_reconstruction(
    measurements: dict[int, complex],
    recovered_edge: EdgeModel,
    x: Array,
    background_degree: int,
) -> Array:
    background = reconstruct_background(measurements, recovered_edge, background_degree)
    return background.values(x) + recovered_edge.values(x)


# -----------------------------------------------------------------------------
# Finite dictionary theorem
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class DictionaryProblem:
    background: Array
    dictionary: Array

    def __post_init__(self) -> None:
        B = np.asarray(self.background, dtype=float)
        D = np.asarray(self.dictionary, dtype=float)
        if B.ndim != 2 or D.ndim != 2 or B.shape[0] != D.shape[0]:
            raise ValueError("background and dictionary must share the observation dimension")
        object.__setattr__(self, "background", B)
        object.__setattr__(self, "dictionary", D)

    @property
    def projector(self) -> Array:
        # Rank-aware numerical orthogonal projection onto range(background).
        # Full-column QR includes arbitrary extra directions when B is dependent.
        B = self.background
        if B.shape[1] == 0:
            return np.zeros((B.shape[0], B.shape[0]), dtype=float)
        u, singular, _ = np.linalg.svd(B, full_matrices=False)
        if singular.size == 0:
            return np.zeros((B.shape[0], B.shape[0]), dtype=float)
        tolerance = np.finfo(float).eps * max(B.shape) * singular[0]
        q = u[:, singular > tolerance]
        return q @ q.T

    @property
    def residual_dictionary(self) -> Array:
        return (np.eye(self.background.shape[0]) - self.projector) @ self.dictionary


def restricted_separation_constant(matrix: Array, sparsity: int) -> float:
    """Exact finite support search for the smallest restricted singular value."""
    A = np.asarray(matrix, dtype=float)
    if sparsity < 1:
        return float("inf")
    best = float("inf")
    max_support = min(sparsity, A.shape[1])
    for size in range(1, max_support + 1):
        for support in combinations(range(A.shape[1]), size):
            # A wide support has a coefficient kernel, even when compact SVD
            # returns only positive row-space singular values.
            if size > A.shape[0]:
                return 0.0
            sigma = np.linalg.svd(A[:, support], compute_uv=False)
            best = min(best, float(sigma[-1]))
    return best


def exhaustive_sparse_recovery(
    problem: DictionaryProblem,
    y: Array,
    sparsity: int,
) -> dict[str, object]:
    A = problem.residual_dictionary
    R = np.eye(problem.background.shape[0]) - problem.projector
    r = R @ np.asarray(y, dtype=float)
    best_residual = float("inf")
    best_alpha = np.zeros(A.shape[1], dtype=float)
    best_support: tuple[int, ...] = ()
    second_residual = float("inf")
    for size in range(0, sparsity + 1):
        for support in combinations(range(A.shape[1]), size):
            alpha = np.zeros(A.shape[1], dtype=float)
            if support:
                coeff, _, _, _ = np.linalg.lstsq(A[:, support], r, rcond=None)
                alpha[list(support)] = coeff
            residual = float(np.linalg.norm(A @ alpha - r))
            if residual < best_residual - 1e-14:
                second_residual = best_residual
                best_residual = residual
                best_alpha = alpha
                best_support = support
            elif residual < second_residual:
                second_residual = residual
    edge = problem.dictionary @ best_alpha
    smooth = problem.projector @ (y - edge)
    return {
        "support": best_support,
        "alpha": best_alpha,
        "edge": edge,
        "smooth": smooth,
        "reconstruction": smooth + edge,
        "residual": best_residual,
        "second_residual": second_residual,
        "gap": second_residual - best_residual,
    }


# -----------------------------------------------------------------------------
# Multi-channel recovery
# -----------------------------------------------------------------------------
def recover_shared_edges_multichannel(
    measurements_by_channel: Sequence[dict[int, complex]],
    background_degree_bound: int,
    edge_order_bound: int,
    known_order: int,
) -> RecoveryResult:
    n0 = background_degree_bound + 1
    moment_indices = np.arange(n0, n0 + 2 * edge_order_bound, dtype=np.int64)
    channel_moments = [edge_moments_from_fourier(m, moment_indices) for m in measurements_by_channel]
    order = known_order
    H_blocks = []
    b_blocks = []
    for moments in channel_moments:
        H_blocks.append(hankel_from_consecutive_moments(moments, order, order))
        b_blocks.append(moments[order : 2 * order])
    H_stack = np.vstack(H_blocks)
    b_stack = np.concatenate(b_blocks)
    q_low, _, _, _ = np.linalg.lstsq(H_stack, -b_stack, rcond=None)
    annihilator = np.r_[q_low, 1.0 + 0.0j]
    roots = np.roots(annihilator[::-1])
    roots = roots / np.abs(roots)
    locations = np.mod(-np.angle(roots), TAU)
    order_idx = np.argsort(locations)
    locations = locations[order_idx]
    roots = roots[order_idx]
    # Aggregate amplitudes only for diagnostics. The location theorem is the key.
    jumps_aggregate = np.zeros(order, dtype=np.complex128)
    residuals = []
    V = np.asarray([[roots[j] ** int(n) for j in range(order)] for n in moment_indices], dtype=np.complex128)
    for moments in channel_moments:
        amp, _, _, _ = np.linalg.lstsq(V, moments, rcond=None)
        jumps_aggregate += amp
        residuals.append(float(np.linalg.norm(V @ amp - moments)))
    rec_residual = 0.0
    for moments in channel_moments:
        for start in range(moments.size - order):
            rec_residual = max(rec_residual, float(abs(np.dot(annihilator, moments[start : start + order + 1]))))
    H_square = H_stack[:order, :]
    return RecoveryResult(
        order=order,
        locations=locations,
        jumps=jumps_aggregate,
        annihilator_ascending=annihilator,
        hankel_singular_values=np.linalg.svd(H_stack, compute_uv=False).astype(float),
        moment_indices=moment_indices,
        measured_moments=np.concatenate(channel_moments),
        recurrence_residual=rec_residual,
        amplitude_residual=max(residuals),
        min_root_separation=float(np.min(pairwise_circular_gaps(locations))),
        hankel_condition=float(np.linalg.cond(H_square)),
        vandermonde_condition=float(np.linalg.cond(V[:order, :])),
    )


# -----------------------------------------------------------------------------
# Piecewise-polynomial recurrence check
# -----------------------------------------------------------------------------
def exponential_polynomial_moments(
    roots: ComplexArray,
    polynomial_coefficients: Sequence[Sequence[complex]],
    indices: Sequence[int],
) -> ComplexArray:
    out = []
    for n in indices:
        value = 0.0 + 0.0j
        for root, coeffs in zip(roots, polynomial_coefficients, strict=True):
            p = sum(complex(c) * (n**r) for r, c in enumerate(coeffs))
            value += p * (root**n)
        out.append(value)
    return np.asarray(out, dtype=np.complex128)


def repeated_root_annihilator(roots: ComplexArray, multiplicity: int) -> ComplexArray:
    poly_desc = np.asarray([1.0 + 0.0j])
    for root in roots:
        for _ in range(multiplicity):
            poly_desc = np.convolve(poly_desc, np.asarray([1.0 + 0.0j, -root], dtype=np.complex128))
    return poly_desc[::-1]


# -----------------------------------------------------------------------------
# Diagnostics and experiments
# -----------------------------------------------------------------------------
def location_error(true_locations: Array, recovered_locations: Array) -> float:
    if true_locations.size != recovered_locations.size:
        return float("inf")
    cost = np.asarray(
        [[circular_distance(float(a), float(b)) for b in recovered_locations] for a in true_locations],
        dtype=float,
    )
    rows, cols = linear_sum_assignment(cost)
    return float(np.max(cost[rows, cols]))


def add_fourier_noise(
    measurements: dict[int, complex],
    indices: Iterable[int],
    sigma: float,
    rng: np.random.Generator,
) -> dict[int, complex]:
    out = dict(measurements)
    for n in indices:
        noise = sigma * (rng.normal() + 1j * rng.normal()) / math.sqrt(2.0)
        out[int(n)] = out[int(n)] + noise
    return out


def exact_symbolic_example() -> dict[str, str]:
    """An exact four-edge roots-of-unity example checked in SymPy."""
    I = sp.I
    roots = [sp.Integer(1), -sp.Integer(1), I, -I]
    jumps = [sp.Integer(2), sp.Integer(-1), sp.Integer(3), sp.Integer(-4)]
    n0 = 3
    moments = [sp.simplify(sum(a * z**n for a, z in zip(jumps, roots, strict=True))) for n in range(n0, n0 + 8)]
    H = sp.Matrix([[moments[i + j] for j in range(4)] for i in range(4)])
    b = sp.Matrix([moments[i + 4] for i in range(4)])
    q = H.LUsolve(-b)
    Q = sp.expand(sum(q[r] * sp.Symbol("z") ** r for r in range(4)) + sp.Symbol("z") ** 4)
    expected = sp.expand((sp.Symbol("z") - 1) * (sp.Symbol("z") + 1) * (sp.Symbol("z") - I) * (sp.Symbol("z") + I))
    return {
        "hankel_determinant": str(sp.simplify(H.det())),
        "annihilator": str(Q),
        "expected": str(expected),
        "difference": str(sp.expand(Q - expected)),
    }


def run_exact_examples() -> tuple[list[dict[str, float | int]], dict[str, object]]:
    rows: list[dict[str, float | int]] = []
    rng = np.random.default_rng(20260729)
    cases = [
        (3, 2, 4, 0.85),
        (4, 4, 6, 0.55),
        (5, 6, 8, 0.42),
        (6, 8, 10, 0.34),
    ]
    representative: dict[str, object] = {}
    for index, (K, L, Lmax, separation) in enumerate(cases):
        edge = generate_edge_model(L, rng, min_separation=separation)
        background = generate_background(K, rng)
        signal = UniversalSignal(background, edge)
        indices = range(-K, K + 2 * Lmax + 2)
        measurements = fourier_measurements(signal, indices)
        result = recover_unknown_edges(measurements, K, Lmax)
        matched = match_edge_models(edge, result)
        recovered_edge = result.edge_model()
        recovered_background = reconstruct_background(measurements, recovered_edge, K)
        x = np.linspace(0.0, TAU, 4096, endpoint=False)
        reconstruction = recovered_background.values(x) + recovered_edge.values(x)
        error = float(np.max(np.abs(reconstruction - signal.values(x))))
        rows.append(
            {
                "case": index + 1,
                "degree": K,
                "true_edges": L,
                "recovered_edges": result.order,
                "location_error": float(matched["location_error_max"]),
                "jump_error": float(matched["jump_error_max"]),
                "reconstruction_error": error,
                "hankel_condition": result.hankel_condition,
                "vandermonde_condition": result.vandermonde_condition,
            }
        )
        if index == 1:
            representative = {
                "edge": edge,
                "background": background,
                "signal": signal,
                "measurements": measurements,
                "result": result,
                "recovered_edge": recovered_edge,
                "recovered_background": recovered_background,
            }
    return rows, representative


def run_noise_experiment() -> list[dict[str, float]]:
    rng = np.random.default_rng(314159)
    sigmas = [0.0, 1e-10, 1e-8, 1e-6, 1e-4, 5e-4, 1e-3]
    separations = [0.22, 0.35, 0.55, 0.80]
    rows: list[dict[str, float]] = []
    K = 4
    L = 4
    Lmax = 6
    trials = 32
    n0 = K + 1
    high_indices = list(range(n0, n0 + 2 * Lmax))
    all_indices = list(range(-K, K + 2 * Lmax + 2))
    for sep in separations:
        for sigma in sigmas:
            loc_errors = []
            rec_errors = []
            successes = 0
            conditions = []
            for _ in range(trials):
                edge = generate_edge_model(L, rng, min_separation=sep)
                background = generate_background(K, rng)
                signal = UniversalSignal(background, edge)
                measurements = fourier_measurements(signal, all_indices)
                noisy = add_fourier_noise(measurements, high_indices, sigma, rng)
                try:
                    result = recover_unknown_edges(noisy, K, Lmax, known_order=L, rank_tolerance=1e-8)
                    loc = location_error(edge.locations, result.locations)
                    loc_errors.append(loc)
                    conditions.append(result.hankel_condition)
                    successes += int(loc < 0.02)
                    # The smooth coefficients are not noised in this controlled study.
                    recovered_edge = result.edge_model()
                    recovered_background = reconstruct_background(noisy, recovered_edge, K)
                    x = np.linspace(0.0, TAU, 2048, endpoint=False)
                    rec_errors.append(float(np.sqrt(np.mean((signal.values(x) - (recovered_background.values(x) + recovered_edge.values(x))) ** 2))))
                except Exception:
                    loc_errors.append(PI)
                    rec_errors.append(1.0)
                    conditions.append(float("inf"))
            finite_conditions = [c for c in conditions if np.isfinite(c)]
            rows.append(
                {
                    "separation": sep,
                    "sigma": sigma,
                    "success_rate": successes / trials,
                    "median_location_error": float(np.median(loc_errors)),
                    "mean_location_error": float(np.mean(loc_errors)),
                    "median_reconstruction_rmse": float(np.median(rec_errors)),
                    "median_hankel_condition": float(np.median(finite_conditions)) if finite_conditions else float("inf"),
                }
            )
    return rows


def run_close_edge_experiment() -> list[dict[str, float]]:
    K = 2
    L = 4
    Lmax = 4
    base = np.asarray([0.4, 2.4, 4.4, 5.6])
    jumps = np.asarray([1.0, -0.8, 0.5, -0.7])
    separations = np.geomspace(0.8, 0.015, 28)
    rows = []
    rng = np.random.default_rng(99)
    background = generate_background(K, rng)
    for delta in separations:
        tau = base.copy()
        tau[1] = tau[0] + delta
        tau = np.sort(np.mod(tau, TAU))
        edge = EdgeModel(tau, jumps)
        signal = UniversalSignal(background, edge)
        indices = list(range(-K, K + 2 * Lmax + 2))
        measurements = fourier_measurements(signal, indices)
        result = recover_unknown_edges(measurements, K, Lmax, known_order=L)
        rows.append(
            {
                "minimum_separation": edge.min_separation,
                "hankel_condition": result.hankel_condition,
                "vandermonde_condition": result.vandermonde_condition,
                "location_error": location_error(edge.locations, result.locations),
            }
        )
    return rows


def run_runtime_experiment() -> list[dict[str, float | int]]:
    rng = np.random.default_rng(404)
    rows = []
    for L in range(2, 13):
        K = 4
        Lmax = L + 2
        sep = min(0.25, 0.8 * TAU / L)
        edge = generate_edge_model(L, rng, min_separation=sep)
        background = generate_background(K, rng)
        signal = UniversalSignal(background, edge)
        indices = list(range(-K, K + 2 * Lmax + 2))
        measurements = fourier_measurements(signal, indices)
        repeats = 40
        start = time.perf_counter()
        for _ in range(repeats):
            recover_unknown_edges(measurements, K, Lmax, known_order=L)
        elapsed = (time.perf_counter() - start) / repeats
        rows.append({"edge_order": L, "seconds": elapsed})
    return rows


def build_dictionary_example() -> tuple[DictionaryProblem, Array, Array, dict[str, object], float]:
    n = 24
    x = np.linspace(0.0, TAU, n, endpoint=False)
    B = np.column_stack([np.ones(n), np.cos(x), np.sin(x), np.cos(2 * x), np.sin(2 * x)])
    atoms = []
    for start in range(0, n, 3):
        mask = np.zeros(n)
        mask[start : min(start + 4, n)] = 1.0
        atoms.append(mask)
    D = np.column_stack(atoms)
    problem = DictionaryProblem(B, D)
    alpha = np.zeros(D.shape[1])
    alpha[1] = 1.2
    alpha[5] = -0.7
    theta = np.asarray([0.2, 0.5, -0.25, 0.1, 0.15])
    y = B @ theta + D @ alpha
    recovered = exhaustive_sparse_recovery(problem, y, sparsity=2)
    gamma = restricted_separation_constant(problem.residual_dictionary, sparsity=4)
    return problem, y, alpha, recovered, gamma


def build_multichannel_example() -> dict[str, object]:
    rng = np.random.default_rng(909)
    locations = np.asarray([0.45, 1.70, 3.05, 4.30])
    jumps1 = np.asarray([1.0, -0.7, 0.4, -0.7])
    jumps2 = np.asarray([0.0, 0.8, -1.1, 0.3])
    # The first edge is invisible in channel 2, but visible in channel 1.
    edge1 = EdgeModel(locations, jumps1)
    # Avoid a zero jump in the constructor by using the moment model directly for channel 2.
    K = 3
    L = 4
    Lmax = 6
    background1 = generate_background(K, rng)
    background2 = generate_background(K, rng)
    indices = list(range(-K, K + 2 * Lmax + 2))
    m1 = {}
    m2 = {}
    for n in indices:
        edge2_fourier = 0.0 if n == 0 else np.sum(jumps2 * np.exp(-1j * n * locations)) / (2j * PI * n)
        m1[n] = background1.fourier(n) + edge1.fourier(n)
        m2[n] = background2.fourier(n) + edge2_fourier
    result = recover_shared_edges_multichannel([m1, m2], K, Lmax, known_order=L)
    return {
        "locations": locations,
        "jumps1": jumps1,
        "jumps2": jumps2,
        "measurements1": m1,
        "measurements2": m2,
        "result": result,
    }



def build_2d_rectangle_example() -> dict[str, object]:
    height = 18
    width = 18
    yy, xx = np.mgrid[0:height, 0:width]
    xn = 2.0 * PI * xx.ravel() / width
    yn = 2.0 * PI * yy.ravel() / height
    background_design = np.column_stack(
        [
            np.ones(height * width),
            np.cos(xn),
            np.sin(xn),
            np.cos(yn),
            np.sin(yn),
            np.cos(xn + yn),
        ]
    )
    q, _ = np.linalg.qr(background_design)
    candidates: list[Array] = []
    metadata: list[tuple[int, int, int, int]] = []
    for rectangle_height in range(3, 8):
        for rectangle_width in range(3, 8):
            for top in range(0, height - rectangle_height + 1):
                for left in range(0, width - rectangle_width + 1):
                    mask = np.zeros((height, width), dtype=float)
                    mask[top : top + rectangle_height, left : left + rectangle_width] = 1.0
                    candidates.append(mask.ravel())
                    metadata.append((top, left, rectangle_height, rectangle_width))
    dictionary = np.column_stack(candidates)
    residual_dictionary = dictionary - q @ (q.T @ dictionary)
    true_metadata = (6, 8, 5, 6)
    true_index = metadata.index(true_metadata)
    amplitude = 1.35
    theta = np.asarray([0.2, 0.42, -0.18, 0.31, 0.12, -0.16])
    smooth = background_design @ theta
    edge = amplitude * dictionary[:, true_index]
    observed = smooth + edge
    residual_observed = observed - q @ (q.T @ observed)
    dots = residual_dictionary.T @ residual_observed
    norms = np.sum(residual_dictionary**2, axis=0)
    amplitudes = dots / norms
    residuals = (
        float(residual_observed @ residual_observed)
        - 2.0 * amplitudes * dots
        + amplitudes**2 * norms
    )
    best = int(np.argmin(residuals))
    recovered_edge = amplitudes[best] * dictionary[:, best]
    recovered_smooth = q @ (q.T @ (observed - recovered_edge))
    reconstruction = recovered_smooth + recovered_edge
    return {
        "height": height,
        "width": width,
        "metadata": metadata,
        "true_metadata": true_metadata,
        "true_index": true_index,
        "best_index": best,
        "best_metadata": metadata[best],
        "amplitude": amplitude,
        "recovered_amplitude": float(amplitudes[best]),
        "smooth": smooth.reshape(height, width),
        "edge": edge.reshape(height, width),
        "observed": observed.reshape(height, width),
        "recovered_edge": recovered_edge.reshape(height, width),
        "recovered_smooth": recovered_smooth.reshape(height, width),
        "reconstruction": reconstruction.reshape(height, width),
        "residual": (reconstruction - observed).reshape(height, width),
        "objective": float(residuals[best]),
        "second_objective": float(np.partition(residuals, 1)[1]),
    }

def run_tests(
    exact_rows: list[dict[str, float | int]],
    representative: dict[str, object],
    dictionary_data: tuple[DictionaryProblem, Array, Array, dict[str, object], float],
    multichannel: dict[str, object],
    rectangle_2d: dict[str, object],
) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        tests.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    symbolic = exact_symbolic_example()
    record("symbolic annihilator", symbolic["difference"] == "0", symbolic["annihilator"])

    edge: EdgeModel = representative["edge"]  # type: ignore[assignment]
    signal: UniversalSignal = representative["signal"]  # type: ignore[assignment]
    measurements: dict[int, complex] = representative["measurements"]  # type: ignore[assignment]
    result: RecoveryResult = representative["result"]  # type: ignore[assignment]
    recovered_edge: EdgeModel = representative["recovered_edge"]  # type: ignore[assignment]
    recovered_background: BandlimitedBackground = representative["recovered_background"]  # type: ignore[assignment]

    n_test = np.arange(5, 17)
    direct = edge.moments(n_test)
    from_fourier = edge_moments_from_fourier(measurements, n_test)
    record("distributional Fourier identity", float(np.max(np.abs(direct - from_fourier))) < 1e-11, f"residual={np.max(np.abs(direct-from_fourier)):.3e}")

    record("unknown order", result.order == edge.order, f"true={edge.order}, recovered={result.order}")
    match = match_edge_models(edge, result)
    record("off-grid locations", float(match["location_error_max"]) < 1e-9, f"error={float(match['location_error_max']):.3e}")
    record("jump amplitudes", float(match["jump_error_max"]) < 1e-8, f"error={float(match['jump_error_max']):.3e}")
    record("annihilating recurrence", result.recurrence_residual < 1e-8, f"residual={result.recurrence_residual:.3e}")
    record("Vandermonde amplitude solve", result.amplitude_residual < 1e-8, f"residual={result.amplitude_residual:.3e}")

    x = np.linspace(0.0, TAU, 8192, endpoint=False)
    reconstruction = recovered_background.values(x) + recovered_edge.values(x)
    error = float(np.max(np.abs(reconstruction - signal.values(x))))
    record("full signal reconstruction", error < 1e-8, f"error={error:.3e}")

    K = signal.background.degree
    raw = raw_fourier_partial(measurements, x, order=K)
    resolved = packet_resolved_reconstruction(measurements, recovered_edge, x, K)
    record("Gibbs-free resolved synthesis", float(np.max(np.abs(resolved - signal.values(x)))) < 1e-8, f"raw_rmse={np.sqrt(np.mean((raw-signal.values(x))**2)):.3e}")

    # Rank factorization and exact rows.
    record("all exact random cases", max(float(row["reconstruction_error"]) for row in exact_rows) < 1e-7, f"cases={len(exact_rows)}")

    problem, y, alpha, recovered, gamma = dictionary_data
    record("finite dictionary support", tuple(np.flatnonzero(alpha)) == tuple(recovered["support"]), f"support={recovered['support']}")
    record("finite dictionary synthesis", float(np.max(np.abs(recovered["reconstruction"] - y))) < 1e-10, f"residual={recovered['residual']:.3e}")
    record("positive restricted separation", gamma > 1e-6, f"gamma4={gamma:.3e}")

    # A deterministic noisy stability check for the finite dictionary theorem.
    rng = np.random.default_rng(17)
    eta = 1e-4 * rng.normal(size=y.size)
    noisy = y + eta
    recovered_noisy = exhaustive_sparse_recovery(problem, noisy, sparsity=2)
    coeff_error = float(np.linalg.norm(recovered_noisy["alpha"] - alpha))
    bound = 2.0 * float(np.linalg.norm(eta)) / gamma
    record("finite dictionary stability", coeff_error <= bound + 1e-10, f"error={coeff_error:.3e}, bound={bound:.3e}")

    multi_result: RecoveryResult = multichannel["result"]  # type: ignore[assignment]
    multi_error = location_error(np.asarray(multichannel["locations"]), multi_result.locations)
    record("shared-edge multichannel recovery", multi_error < 1e-8, f"error={multi_error:.3e}")

    # Piecewise-polynomial repeated-root recurrence.
    roots = np.exp(-1j * np.asarray([0.7, 2.2]))
    coeffs = [[1.0, 0.3], [-0.4, 0.8]]
    indices = np.arange(1, 20)
    moments = exponential_polynomial_moments(roots, coeffs, indices)
    annihilator = repeated_root_annihilator(roots, multiplicity=2)
    residual = max(abs(np.dot(annihilator, moments[i : i + annihilator.size])) for i in range(moments.size - annihilator.size + 1))
    record("piecewise-polynomial confluent recurrence", float(residual) < 1e-9, f"residual={float(residual):.3e}")

    # Concrete impossibility witness: a sub-grid interval missed by all samples.
    sample_x = np.linspace(0.0, 1.0, 8, endpoint=False)
    witness = ((sample_x > 0.13) & (sample_x < 0.20)).astype(float)
    record("finite-sampling impossibility witness", float(np.max(np.abs(witness))) == 0.0, "nonzero interval can lie between sample points")

    # No uniform stability as two opposite jumps collide.
    n = np.arange(1, 13)
    delta1 = 1e-2
    delta2 = 5e-3
    m1 = 1.0 - np.exp(-1j * n * delta1)
    m2 = 1.0 - np.exp(-1j * n * delta2)
    record("collision instability", float(np.linalg.norm(m2)) < float(np.linalg.norm(m1)), "moment norm shrinks with edge separation")

    record(
        "two-dimensional rectangle recovery",
        rectangle_2d["best_metadata"] == rectangle_2d["true_metadata"]
        and abs(float(rectangle_2d["recovered_amplitude"]) - float(rectangle_2d["amplitude"])) < 1e-10
        and float(np.max(np.abs(rectangle_2d["residual"]))) < 1e-10,
        f"true={rectangle_2d['true_metadata']}, recovered={rectangle_2d['best_metadata']}",
    )

    return tests


# -----------------------------------------------------------------------------
# Figure generation
# -----------------------------------------------------------------------------
def generate_figures(
    base: Path,
    exact_rows: list[dict[str, float | int]],
    representative: dict[str, object],
    noise_rows: list[dict[str, float]],
    close_rows: list[dict[str, float]],
    runtime_rows: list[dict[str, float | int]],
    dictionary_data: tuple[DictionaryProblem, Array, Array, dict[str, object], float],
    multichannel: dict[str, object],
    rectangle_2d: dict[str, object],
    tests: list[dict[str, object]],
) -> None:
    out = base / "figures"
    edge: EdgeModel = representative["edge"]  # type: ignore[assignment]
    background: BandlimitedBackground = representative["background"]  # type: ignore[assignment]
    signal: UniversalSignal = representative["signal"]  # type: ignore[assignment]
    measurements: dict[int, complex] = representative["measurements"]  # type: ignore[assignment]
    result: RecoveryResult = representative["result"]  # type: ignore[assignment]
    recovered_edge: EdgeModel = representative["recovered_edge"]  # type: ignore[assignment]
    recovered_background: BandlimitedBackground = representative["recovered_background"]  # type: ignore[assignment]

    # 01 Pipeline.
    fig, ax = diagram_axes((13.0, 5.8))
    stages = [
        ("finite Fourier data", BLUE),
        ("remove the smooth band", TEAL),
        ("form edge moments", GREEN),
        ("build the Hankel packet", ORANGE),
        ("recover the annihilator", MAGENTA),
        ("find edges and jumps", PURPLE),
        ("synthesize without Gibbs", RED),
    ]
    xs = np.linspace(0.02, 0.84, len(stages))
    for i, ((label, color), xpos) in enumerate(zip(stages, xs, strict=True)):
        draw_box(ax, (xpos, 0.42), 0.13, 0.20, label, face=color + "20", edge=color, fontsize=10.5)
        if i + 1 < len(stages):
            draw_arrow(ax, (xpos + 0.13, 0.52), (xs[i + 1] - 0.006, 0.52))
    ax.text(0.5, 0.88, "Unknown-edge recovery as one closed projector-resolved chain", ha="center", fontsize=22, weight="bold")
    ax.text(0.5, 0.12, "The word universal refers to every signal in the declared finite-rate class, not to arbitrary functions without assumptions.", ha="center", color=MUTED, fontsize=11.5)
    save_figure(fig, out, "01_closed_pipeline")

    # 02 Impossibility witness.
    fig, axes = plt.subplots(2, 1, figsize=(12.4, 6.2), sharex=True)
    xx = np.linspace(0.0, 1.0, 1200)
    samples = np.linspace(0.0, 1.0, 8, endpoint=False)
    hidden = ((xx > 0.13) & (xx < 0.20)).astype(float)
    axes[0].plot(xx, np.zeros_like(xx), color=INK, lw=2)
    axes[0].scatter(samples, np.zeros_like(samples), color=BLUE, zorder=4, label="samples")
    axes[0].set_title("Signal A: no edge", loc="left", weight="bold")
    axes[1].plot(xx, hidden, color=RED, lw=2)
    axes[1].scatter(samples, np.zeros_like(samples), color=BLUE, zorder=4, label="the same samples")
    axes[1].set_title("Signal B: a hidden interval between sample points", loc="left", weight="bold")
    for axr in axes:
        axr.set_ylim(-0.15, 1.2)
        axr.grid(alpha=.16)
        axr.legend(loc="upper right")
    axes[-1].set_xlabel("coordinate")
    fig.suptitle("No method can recover arbitrary edges from a noninjective measurement map", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, .94])
    save_figure(fig, out, "02_unrestricted_impossibility")

    # 03 Decomposition ambiguity.
    fig, ax = diagram_axes((12.6, 5.8))
    draw_box(ax, (.06, .55), .22, .18, "observed object\n$f$", face=BLUE+"20", edge=BLUE, fontsize=16)
    draw_box(ax, (.40, .68), .23, .16, "smooth packet\n$s+h$", face=TEAL+"20", edge=TEAL, fontsize=14)
    draw_box(ax, (.40, .32), .23, .16, "edge packet\n$j-h$", face=ORANGE+"20", edge=ORANGE, fontsize=14)
    draw_box(ax, (.76, .50), .18, .20, "same sum\n$(s+h)+(j-h)=f$", face=MAGENTA+"18", edge=MAGENTA, fontsize=13)
    draw_arrow(ax, (.28,.64), (.40,.76), color=TEAL)
    draw_arrow(ax, (.28,.64), (.40,.40), color=ORANGE)
    draw_arrow(ax, (.63,.76), (.76,.62), color=TEAL)
    draw_arrow(ax, (.63,.40), (.76,.57), color=ORANGE)
    ax.text(.5,.13,r"If $h\in\mathcal{S}\cap\mathcal{J}$ is nonzero, the smooth-edge split is not identifiable.",ha="center",fontsize=15)
    ax.text(.5,.08,"A recovery theorem must make the two packets distinguishable after measurement.",ha="center",color=MUTED,fontsize=11)
    save_figure(fig,out,"03_decomposition_ambiguity")

    # 04 Declared model.
    x = np.linspace(0.0, TAU, 4096, endpoint=False)
    fig, axes = plt.subplots(3, 1, figsize=(12.5, 7.0), sharex=True)
    axes[0].plot(x, background.values(x), color=TEAL, lw=2)
    axes[0].set_title("Unknown bandlimited background", loc="left", weight="bold")
    axes[1].plot(x, edge.values(x), color=ORANGE, lw=2)
    for t in edge.locations:
        axes[1].axvline(t, color=RED, lw=.8, alpha=.6)
    axes[1].set_title(f"Unknown piecewise-constant edge packet with {edge.order} off-grid jumps", loc="left", weight="bold")
    axes[2].plot(x, signal.values(x), color=INK, lw=2)
    axes[2].set_title("Observed sum", loc="left", weight="bold")
    for axr in axes:
        axr.grid(alpha=.15)
        axr.set_ylabel("amplitude")
    axes[-1].set_xlabel("periodic coordinate")
    fig.tight_layout()
    save_figure(fig,out,"04_declared_model")

    # 05 Distributional derivative atoms.
    fig, ax = plt.subplots(figsize=(12.4, 5.3))
    ax.plot(x, edge.values(x), color=ORANGE, lw=2.2, label="edge packet")
    y0 = np.min(edge.values(x)) - 0.55
    for i, (t, a) in enumerate(zip(edge.locations, edge.jumps, strict=True)):
        ax.arrow(t, y0, 0, a * .35, width=.008, head_width=.08, head_length=.10, color=PALETTE[i % len(PALETTE)], length_includes_head=True)
        ax.text(t, y0 - .12, rf"$a_{{{i+1}}}$", ha="center", color=PALETTE[i % len(PALETTE)], weight="bold")
    ax.axhline(y0, color=GRID, lw=1)
    ax.set_title(r"The derivative packet is finite: $j'=\sum_\ell a_\ell\delta_{\tau_\ell}$", weight="bold")
    ax.set_xlabel("coordinate")
    ax.set_ylabel("amplitude")
    ax.grid(alpha=.15)
    ax.legend(loc="upper right")
    save_figure(fig,out,"05_distributional_derivative")

    # 06 Fourier separation.
    ns = np.arange(-28, 29)
    coeff = np.asarray([signal.fourier(int(n)) for n in ns])
    fig, ax = plt.subplots(figsize=(12.3, 5.4))
    ax.stem(ns, np.abs(coeff), linefmt=BLUE, markerfmt="o", basefmt=" ")
    ax.axvspan(-background.degree, background.degree, color=TEAL, alpha=.16, label="smooth band")
    ax.axvline(background.degree + 0.5, color=RED, ls="--", lw=1.3)
    ax.axvline(-background.degree - 0.5, color=RED, ls="--", lw=1.3)
    ax.set_yscale("log")
    ax.set_xlabel("Fourier index")
    ax.set_ylabel(r"$|\widehat f(n)|$")
    ax.set_title("Beyond the smooth band, every coefficient belongs to the edge packet", weight="bold")
    ax.grid(alpha=.18, which="both")
    ax.legend(loc="upper right")
    save_figure(fig,out,"06_fourier_packet_separation")

    # 07 Edge moments.
    moment_indices = result.moment_indices
    moments = result.measured_moments
    fig, axes = plt.subplots(2, 1, figsize=(12.2, 6.2), sharex=True)
    axes[0].stem(moment_indices, moments.real, linefmt=BLUE, markerfmt="o", basefmt=" ")
    axes[0].set_ylabel("real part")
    axes[1].stem(moment_indices, moments.imag, linefmt=MAGENTA, markerfmt="o", basefmt=" ")
    axes[1].set_ylabel("imaginary part")
    axes[1].set_xlabel("moment index n")
    for axr in axes:
        axr.grid(alpha=.16)
    fig.suptitle(r"Edge moments $m_n=2\pi i n\widehat f(n)=\sum_\ell a_\ell z_\ell^n$", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0,0,1,.93])
    save_figure(fig,out,"07_edge_moments")

    # 08 Hankel matrix.
    H = hankel_from_consecutive_moments(moments, result.order, result.order)
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.9))
    im0 = axes[0].imshow(H.real, cmap="coolwarm")
    axes[0].set_title("real part")
    im1 = axes[1].imshow(H.imag, cmap="coolwarm")
    axes[1].set_title("imaginary part")
    for axr in axes:
        axr.set_xlabel("column")
        axr.set_ylabel("row")
    fig.colorbar(im0, ax=axes[0], fraction=.046)
    fig.colorbar(im1, ax=axes[1], fraction=.046)
    fig.suptitle("The Hankel packet factors through a Vandermonde matrix and the unknown jumps", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig,out,"08_hankel_packet")

    # 09 Hankel singular values and unknown order.
    fig, ax = plt.subplots(figsize=(10.5, 5.1))
    sv = result.hankel_singular_values
    ax.semilogy(np.arange(1, len(sv)+1), sv, marker="o", color=BLUE, lw=2)
    ax.axvline(result.order + .5, color=RED, ls="--", label=f"rank = {result.order}")
    ax.set_xlabel("singular-value index")
    ax.set_ylabel("singular value")
    ax.set_title("The number of unknown edges is the exact Hankel rank", weight="bold")
    ax.grid(alpha=.18, which="both")
    ax.legend(loc="upper right")
    save_figure(fig,out,"09_unknown_order_rank")

    # 10 Annihilator roots.
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    circle = plt.Circle((0,0),1.0,fill=False,color=GRID,lw=2)
    ax.add_patch(circle)
    roots = np.exp(-1j * result.locations)
    ax.scatter(roots.real, roots.imag, s=90, color=RED, label="recovered roots")
    true_roots = np.exp(-1j * edge.locations)
    ax.scatter(true_roots.real, true_roots.imag, s=180, facecolors="none", edgecolors=INK, linewidths=1.7, label="true roots")
    for i,z in enumerate(roots):
        ax.text(z.real*1.10,z.imag*1.10,str(i+1),ha="center",va="center",weight="bold")
    ax.set_aspect("equal")
    ax.set_xlim(-1.25,1.25)
    ax.set_ylim(-1.25,1.25)
    ax.axhline(0,color=GRID,lw=.8)
    ax.axvline(0,color=GRID,lw=.8)
    ax.set_title("Roots of the annihilating polynomial encode the edge locations", weight="bold")
    ax.legend(loc="lower center", bbox_to_anchor=(.5,-.13), ncol=2)
    save_figure(fig,out,"10_annihilator_roots")

    # 11 Location comparison.
    fig, ax = plt.subplots(figsize=(12.0, 3.9))
    ax.hlines(0.55, 0, TAU, color=GRID, lw=2)
    ax.hlines(0.20, 0, TAU, color=GRID, lw=2)
    ax.scatter(edge.locations, np.full(edge.order,.55), s=90, color=INK, label="true")
    ax.scatter(result.locations, np.full(result.order,.20), s=90, marker="x", color=RED, label="recovered")
    for t in edge.locations:
        ax.plot([t,t],[.20,.55],color=TEAL,lw=1,alpha=.7)
    ax.set_xlim(0,TAU)
    ax.set_yticks([.20,.55],["recovered","true"])
    ax.set_xlabel("periodic coordinate")
    ax.set_title("All off-grid edge locations are recovered from finitely many Fourier moments", weight="bold")
    ax.legend(loc="upper center", ncol=2)
    ax.grid(alpha=.12,axis="x")
    save_figure(fig,out,"11_edge_location_recovery")

    # 12 Jump amplitudes.
    match = match_edge_models(edge,result)
    matched_jumps = np.real(np.asarray(match["matched_jumps"]))
    p = np.arange(edge.order)
    fig, ax = plt.subplots(figsize=(11.0,5.0))
    ax.bar(p-.18,edge.jumps,width=.36,color=TEAL,label="true")
    ax.bar(p+.18,matched_jumps,width=.36,color=ORANGE,label="recovered")
    ax.axhline(0,color=INK,lw=.8)
    ax.set_xticks(p,[f"edge {i+1}" for i in p])
    ax.set_ylabel("jump amplitude")
    ax.set_title("The Vandermonde solve recovers every jump amplitude", weight="bold")
    ax.grid(alpha=.15,axis="y")
    ax.legend(loc="upper right")
    save_figure(fig,out,"12_jump_amplitudes")

    # 13 Recovered packets.
    fig, axes = plt.subplots(3,1,figsize=(12.5,7.0),sharex=True)
    axes[0].plot(x,background.values(x),color=TEAL,lw=2,label="true")
    axes[0].plot(x,recovered_background.values(x),color=RED,lw=1.2,ls="--",label="recovered")
    axes[0].set_title("background packet",loc="left",weight="bold")
    axes[1].plot(x,edge.values(x),color=ORANGE,lw=2,label="true")
    axes[1].plot(x,recovered_edge.values(x),color=PURPLE,lw=1.2,ls="--",label="recovered")
    axes[1].set_title("edge packet",loc="left",weight="bold")
    axes[2].plot(x,signal.values(x),color=INK,lw=2,label="true")
    axes[2].plot(x,recovered_background.values(x)+recovered_edge.values(x),color=RED,lw=1.0,ls="--",label="recovered")
    axes[2].set_title("complete signal",loc="left",weight="bold")
    for axr in axes:
        axr.grid(alpha=.15)
        axr.legend(loc="upper right",ncol=2)
        axr.set_ylabel("amplitude")
    axes[-1].set_xlabel("coordinate")
    fig.tight_layout()
    save_figure(fig,out,"13_recovered_packets")

    # 14 Reconstruction residual.
    reconstructed = recovered_background.values(x)+recovered_edge.values(x)
    residual = reconstructed-signal.values(x)
    fig,ax=plt.subplots(figsize=(12.2,4.5))
    ax.plot(x,residual,color=RED,lw=1.4)
    ax.axhline(0,color=INK,lw=.8)
    ax.set_xlabel("coordinate")
    ax.set_ylabel("residual")
    ax.set_title(f"Complete reconstruction residual, maximum {np.max(np.abs(residual)):.2e}",weight="bold")
    ax.grid(alpha=.16)
    save_figure(fig,out,"14_exact_reconstruction_residual")

    # 15 Raw Fourier versus resolved synthesis.
    order = background.degree + 12
    all_measurements = {n: signal.fourier(n) for n in range(-order,order+1)}
    raw = raw_fourier_partial(all_measurements,x,order)
    resolved = recovered_background.values(x)+recovered_edge.values(x)
    fig,axes=plt.subplots(2,1,figsize=(12.5,6.7),sharex=True)
    axes[0].plot(x,signal.values(x),color=INK,lw=2,label="true")
    axes[0].plot(x,raw,color=BLUE,lw=1.1,label=f"raw Fourier order {order}")
    axes[0].set_title("Raw global truncation",loc="left",weight="bold")
    axes[1].plot(x,signal.values(x),color=INK,lw=2,label="true")
    axes[1].plot(x,resolved,color=RED,lw=1.1,ls="--",label="recovered edge + smooth packet")
    axes[1].set_title("Projector-resolved synthesis",loc="left",weight="bold")
    for axr in axes:
        axr.grid(alpha=.15)
        axr.legend(loc="upper right",ncol=2)
        axr.set_ylabel("amplitude")
    axes[-1].set_xlabel("coordinate")
    fig.suptitle("Unknown edges are first recovered, then synthesized in their native packet",fontsize=17,weight="bold")
    fig.tight_layout(rect=[0,0,1,.94])
    save_figure(fig,out,"15_gibbs_free_synthesis")

    # 16 Edge zoom.
    center=edge.locations[0]
    local=np.abs(((x-center+PI)%TAU)-PI)<.35
    fig,ax=plt.subplots(figsize=(11.5,4.8))
    ax.plot(x[local],signal.values(x)[local],color=INK,lw=2,label="true")
    ax.plot(x[local],raw[local],color=BLUE,lw=1.4,label="raw Fourier")
    ax.plot(x[local],resolved[local],color=RED,lw=1.2,ls="--",label="resolved")
    ax.axvline(center,color=ORANGE,lw=1,ls=":")
    ax.set_xlabel("coordinate")
    ax.set_ylabel("amplitude")
    ax.set_title("Local view: the reconstructed edge has no Fourier ringing",weight="bold")
    ax.grid(alpha=.16)
    ax.legend(loc="best")
    save_figure(fig,out,"16_edge_zoom")

    # 17 Exact cases dashboard.
    fig,axes=plt.subplots(1,3,figsize=(13.0,4.5))
    Ls=[int(r["true_edges"]) for r in exact_rows]
    axes[0].semilogy(Ls,[float(r["location_error"]) for r in exact_rows],marker="o",color=BLUE)
    axes[0].set_title("location error",weight="bold")
    axes[1].semilogy(Ls,[float(r["jump_error"]) for r in exact_rows],marker="o",color=ORANGE)
    axes[1].set_title("jump error",weight="bold")
    axes[2].semilogy(Ls,[float(r["reconstruction_error"]) for r in exact_rows],marker="o",color=RED)
    axes[2].set_title("reconstruction error",weight="bold")
    for axr in axes:
        axr.set_xlabel("number of edges")
        axr.grid(alpha=.17,which="both")
    fig.suptitle("Exact off-grid recovery across several unknown-edge counts",fontsize=16.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig,out,"17_exact_case_dashboard")

    # 18 Finite dictionary theorem.
    problem,y,alpha,recovered,gamma=dictionary_data
    n=np.arange(y.size)
    fig,axes=plt.subplots(3,1,figsize=(12.3,7.0),sharex=True)
    axes[0].plot(n,y,color=INK,lw=2)
    axes[0].set_title("observed discrete signal",loc="left",weight="bold")
    axes[1].stem(n,problem.dictionary@alpha,linefmt=ORANGE,markerfmt="o",basefmt=" ")
    axes[1].set_title("true two-atom edge packet",loc="left",weight="bold")
    axes[2].stem(n,recovered["edge"],linefmt=RED,markerfmt="x",basefmt=" ")
    axes[2].set_title(f"recovered packet, restricted separation $\\gamma_4={gamma:.3f}$",loc="left",weight="bold")
    for axr in axes:
        axr.grid(alpha=.15)
        axr.set_ylabel("value")
    axes[-1].set_xlabel("sample index")
    fig.tight_layout()
    save_figure(fig,out,"18_finite_dictionary_recovery")

    # 19 Secant geometry.
    fig,ax=diagram_axes((12.5,5.6))
    draw_box(ax,(.06,.43),.20,.20,"two candidate\nedge packets",face=ORANGE+"20",edge=ORANGE,fontsize=15)
    draw_box(ax,(.39,.43),.22,.20,"subtract\n" + r"$D(\alpha-\beta)$",face=WHITE,edge=INK,fontsize=14)
    draw_box(ax,(.74,.58),.20,.16,"visible after\n" + r"$R_{\mathcal{S}}$",face=TEAL+"20",edge=TEAL,fontsize=13)
    draw_box(ax,(.74,.25),.20,.16,"lost inside the\nsmooth packet",face=RED+"18",edge=RED,fontsize=13)
    draw_arrow(ax,(.26,.53),(.39,.53))
    draw_arrow(ax,(.61,.55),(.74,.66),color=TEAL,text=r"$RDh\ne0$",text_offset=(0,.04))
    draw_arrow(ax,(.61,.49),(.74,.33),color=RED,text=r"$RDh=0$",text_offset=(0,-.04))
    ax.text(.5,.10,r"Universal $s$-sparse recovery holds exactly when no nonzero $2s$-sparse secant is hidden by the background.",ha="center",fontsize=13.5)
    save_figure(fig,out,"19_residualized_secant_condition")

    # 20 Noise by separation heatmap.
    separations=sorted({r["separation"] for r in noise_rows})
    sigmas=sorted({r["sigma"] for r in noise_rows})
    matrix=np.zeros((len(separations),len(sigmas)))
    for row in noise_rows:
        matrix[separations.index(row["separation"]),sigmas.index(row["sigma"])]=row["success_rate"]
    fig,ax=plt.subplots(figsize=(11.5,5.3))
    im=ax.imshow(matrix,aspect="auto",origin="lower",vmin=0,vmax=1,cmap="viridis")
    ax.set_xticks(range(len(sigmas)),[f"{s:.0e}" for s in sigmas],rotation=35,ha="right")
    ax.set_yticks(range(len(separations)),[f"{s:.2f}" for s in separations])
    ax.set_xlabel("Fourier coefficient noise standard deviation")
    ax.set_ylabel("minimum edge separation")
    ax.set_title("Exact-location success in the controlled noisy experiment",weight="bold")
    for i in range(len(separations)):
        for j in range(len(sigmas)):
            val=matrix[i,j]
            ax.text(j,i,f"{val:.2f}",ha="center",va="center",color=WHITE if val<.6 else INK,fontsize=9)
    fig.colorbar(im,ax=ax,fraction=.035,label="success rate")
    fig.tight_layout()
    save_figure(fig,out,"20_noise_separation_heatmap")

    # 21 Noise location error.
    fig,ax=plt.subplots(figsize=(11.5,5.3))
    for sep,color in zip(separations,PALETTE,strict=False):
        rows=[r for r in noise_rows if r["separation"]==sep]
        ax.loglog([max(r["sigma"],1e-12) for r in rows],[max(r["median_location_error"],1e-14) for r in rows],marker="o",lw=2,color=color,label=f"sep {sep:.2f}")
    ax.set_xlabel("noise standard deviation")
    ax.set_ylabel("median location error")
    ax.set_title("Edge localization is stable only while the Hankel and root packets remain separated",weight="bold")
    ax.grid(alpha=.18,which="both")
    ax.legend(loc="upper left",ncol=2)
    save_figure(fig,out,"21_noise_location_error")

    # 22 Close-edge conditioning.
    fig,axes=plt.subplots(1,2,figsize=(12.8,4.9))
    d=[r["minimum_separation"] for r in close_rows]
    axes[0].loglog(d,[r["hankel_condition"] for r in close_rows],marker="o",color=BLUE)
    axes[0].set_title("Hankel condition number",weight="bold")
    axes[1].loglog(d,[r["vandermonde_condition"] for r in close_rows],marker="o",color=MAGENTA)
    axes[1].set_title("Vandermonde condition number",weight="bold")
    for axr in axes:
        axr.set_xlabel("minimum edge separation")
        axr.grid(alpha=.18,which="both")
        axr.invert_xaxis()
    fig.suptitle("There is no uniform stable recovery theorem as distinct edges collide",fontsize=16.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig,out,"22_collision_conditioning")

    # 23 Collision moment decay.
    deltas=np.geomspace(.8,.002,100)
    nidx=np.arange(1,13)
    norms=[np.linalg.norm(1-np.exp(-1j*nidx*d)) for d in deltas]
    fig,ax=plt.subplots(figsize=(10.8,5.0))
    ax.loglog(deltas,norms,color=RED,lw=2)
    ax.set_xlabel("distance between opposite jumps")
    ax.set_ylabel("norm of measured moment vector")
    ax.set_title("Opposite jumps become invisible as their separation tends to zero",weight="bold")
    ax.grid(alpha=.18,which="both")
    save_figure(fig,out,"23_no_uniform_stability")

    # 24 Multi-channel.
    multi_result:RecoveryResult=multichannel["result"] # type: ignore[assignment]
    loc=np.asarray(multichannel["locations"])
    fig,axes=plt.subplots(2,1,figsize=(11.8,5.8),sharex=True)
    axes[0].bar(np.arange(loc.size),np.asarray(multichannel["jumps1"]),color=TEAL)
    axes[0].set_title("channel 1 jump amplitudes",loc="left",weight="bold")
    axes[1].bar(np.arange(loc.size),np.asarray(multichannel["jumps2"]),color=ORANGE)
    axes[1].set_title("channel 2 jump amplitudes",loc="left",weight="bold")
    axes[1].set_xticks(np.arange(loc.size),[f"edge {i+1}" for i in range(loc.size)])
    for axr in axes:
        axr.axhline(0,color=INK,lw=.8)
        axr.grid(alpha=.15,axis="y")
    fig.suptitle(f"Shared edge locations are recovered jointly, maximum error {location_error(loc,multi_result.locations):.2e}",fontsize=16.2,weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig,out,"24_multichannel_shared_edges")

    # 25 Piecewise-polynomial repeated roots.
    fig,ax=diagram_axes((12.8,5.8))
    draw_box(ax,(.04,.43),.19,.20,"piecewise polynomial\n$u$ of degree $d$",face=BLUE+"20",edge=BLUE,fontsize=14)
    draw_box(ax,(.30,.43),.20,.20,"distributional derivative\n$D^{d+1}u$",face=TEAL+"20",edge=TEAL,fontsize=14)
    draw_box(ax,(.57,.43),.18,.20,"exponential-polynomial\nmoments",face=ORANGE+"20",edge=ORANGE,fontsize=13)
    draw_box(ax,(.82,.43),.14,.20,"repeated-root\nannihilator",face=MAGENTA+"20",edge=MAGENTA,fontsize=13)
    draw_arrow(ax,(.23,.53),(.30,.53))
    draw_arrow(ax,(.50,.53),(.57,.53))
    draw_arrow(ax,(.75,.53),(.82,.53))
    ax.text(.5,.17,r"Each edge location becomes a root of multiplicity at most $d+1$ in the annihilating polynomial.",ha="center",fontsize=14)
    ax.text(.5,.10,"The piecewise-constant theorem is the case d = 0.",ha="center",color=MUTED,fontsize=11)
    save_figure(fig,out,"25_piecewise_polynomial_extension")

    # 26 Root perturbation disks.
    roots=np.exp(-1j*edge.locations)
    fig,ax=plt.subplots(figsize=(6.5,6.5))
    ax.add_patch(plt.Circle((0,0),1,fill=False,color=GRID,lw=2))
    radius=min(.18,edge.min_separation/5)
    for i,z in enumerate(roots):
        ax.add_patch(plt.Circle((z.real,z.imag),radius,fill=False,color=PALETTE[i%len(PALETTE)],lw=1.5))
        ax.scatter([z.real],[z.imag],color=PALETTE[i%len(PALETTE)],s=70)
    ax.set_aspect("equal")
    ax.set_xlim(-1.3,1.3)
    ax.set_ylim(-1.3,1.3)
    ax.axhline(0,color=GRID,lw=.8)
    ax.axvline(0,color=GRID,lw=.8)
    ax.set_title("A computable Rouche certificate isolates one recovered root in each disk",weight="bold")
    save_figure(fig,out,"26_root_stability_disks")

    # 27 Runtime.
    fig,ax=plt.subplots(figsize=(10.8,5.0))
    ax.plot([r["edge_order"] for r in runtime_rows],[1e3*r["seconds"] for r in runtime_rows],marker="o",color=PURPLE,lw=2)
    ax.set_xlabel("number of edges")
    ax.set_ylabel("milliseconds per recovery")
    ax.set_title("Reference Prony implementation cost",weight="bold")
    ax.grid(alpha=.18)
    save_figure(fig,out,"27_runtime_scaling")

    # 28 Measurement count.
    L=np.arange(1,13)
    fig,ax=plt.subplots(figsize=(10.5,5.0))
    ax.plot(L,2*L,marker="o",color=BLUE,lw=2,label="high-frequency edge moments")
    ax.plot(L,2*L+2*4+1,marker="o",color=ORANGE,lw=2,label="including degree-4 low band")
    ax.set_xlabel("number of unknown jumps")
    ax.set_ylabel("complex Fourier coefficients")
    ax.set_title("Finite-rate measurement count grows linearly with the number of edges",weight="bold")
    ax.grid(alpha=.18)
    ax.legend(loc="upper left")
    save_figure(fig,out,"28_measurement_count")

    # 29 Failure by too few moments.
    fig,ax=diagram_axes((12.6,5.4))
    draw_box(ax,(.08,.46),.22,.18,"L unknown edges\n2L degrees in the moment model",face=ORANGE+"20",edge=ORANGE,fontsize=14)
    draw_box(ax,(.41,.61),.22,.16,"2L consecutive moments\nfull Hankel factorization",face=TEAL+"20",edge=TEAL,fontsize=13)
    draw_box(ax,(.41,.26),.22,.16,"fewer moments\nnonunique annihilators",face=RED+"20",edge=RED,fontsize=13)
    draw_box(ax,(.76,.46),.16,.18,"exact roots\nor ambiguity",face=MAGENTA+"20",edge=MAGENTA,fontsize=14)
    draw_arrow(ax,(.30,.55),(.41,.69),color=TEAL)
    draw_arrow(ax,(.30,.55),(.41,.34),color=RED)
    draw_arrow(ax,(.63,.69),(.76,.59),color=TEAL)
    draw_arrow(ax,(.63,.34),(.76,.50),color=RED)
    ax.text(.5,.10,"The theorem uses enough moments to determine the annihilator rather than guessing a preferred edge set.",ha="center",fontsize=12.5)
    save_figure(fig,out,"29_too_few_moments")

    # 30 Unknown bandlimit failure.
    fig,ax=plt.subplots(figsize=(11.5,5.0))
    n=np.arange(1,19)
    edge_m=np.abs(edge.moments(n))
    full_m=np.abs(np.asarray([2j*PI*k*signal.fourier(int(k)) for k in n]))
    ax.semilogy(n,full_m,marker="o",color=BLUE,label="moments formed from full signal")
    ax.semilogy(n,edge_m,marker="o",color=ORANGE,label="true edge moments")
    ax.axvspan(1,background.degree,color=RED,alpha=.12,label="contaminated by smooth modes")
    ax.axvline(background.degree+.5,color=INK,ls="--")
    ax.set_xlabel("moment index")
    ax.set_ylabel("magnitude")
    ax.set_title("The high-frequency start must lie beyond a valid background bandlimit",weight="bold")
    ax.grid(alpha=.18,which="both")
    ax.legend(loc="upper right")
    save_figure(fig,out,"30_bandlimit_boundary")

    # 31 Tests dashboard.
    fig,ax=plt.subplots(figsize=(12.0,7.0))
    ax.axis("off")
    ax.text(.5,.96,"Independent checks in the single-file implementation",ha="center",fontsize=20,weight="bold",transform=ax.transAxes)
    y=.90
    for i,test in enumerate(tests):
        bg=PAPER if i%2==0 else "#EEF2F3"
        ax.add_patch(FancyBboxPatch((.04,y-.025),.92,.042,boxstyle="round,pad=.004,rounding_size=.004",facecolor=bg,edgecolor="none",transform=ax.transAxes))
        ax.text(.06,y,test["name"],ha="left",va="center",fontsize=9.5,transform=ax.transAxes)
        ax.text(.93,y,"PASS" if test["passed"] else "FAIL",ha="right",va="center",fontsize=9.5,weight="bold",color=TEAL if test["passed"] else RED,transform=ax.transAxes)
        y-=.047
    save_figure(fig,out,"31_verification_dashboard")

    # 32 Proof map.
    fig,ax=diagram_axes((13.0,6.2))
    nodes=[
        (.04,.66,.17,.16,"no-free-lunch\nboundary",RED),
        (.25,.66,.17,.16,"residualized\nedge packet",TEAL),
        (.46,.66,.17,.16,"finite dictionary\nsecant theorem",ORANGE),
        (.67,.66,.17,.16,"Fourier moment\nreduction",BLUE),
        (.82,.39,.14,.16,"Hankel rank\nand roots",MAGENTA),
        (.59,.20,.18,.16,"jumps and native\nedge synthesis",PURPLE),
        (.34,.20,.18,.16,"smooth packet\nreconstruction",GREEN),
        (.09,.20,.18,.16,"Gibbs-free\ncomplete signal",RED),
    ]
    for x0,y0,w,h,label,color in nodes:
        draw_box(ax,(x0,y0),w,h,label,face=color+"20",edge=color,fontsize=12)
    arrows=[((.21,.74),(.25,.74)),((.42,.74),(.46,.74)),((.63,.74),(.67,.74)),((.84,.66),(.87,.55)),((.82,.39),(.77,.31)),((.59,.28),(.52,.28)),((.34,.28),(.27,.28))]
    for s,e in arrows:draw_arrow(ax,s,e)
    ax.text(.5,.93,"Proof dependency map",ha="center",fontsize=22,weight="bold")
    ax.text(.5,.08,"The exact theorem and the impossibility theorem belong together. The assumptions are part of the result.",ha="center",fontsize=12,color=MUTED)
    save_figure(fig,out,"32_proof_dependency_map")

    # 33 Status boundary.
    categories=["arbitrary functions\nfinite samples","finite dictionary\nsparse edges","1D off-grid\nfinite-rate edges","piecewise polynomial\nfinite innovation","arbitrary 2D\nunknown curves"]
    status=[0,2,2,1,0]
    labels=["impossible","proved","proved","reduced","not proved"]
    colors=[RED,TEAL,TEAL,ORANGE,RED]
    fig,ax=plt.subplots(figsize=(12.2,4.9))
    ax.bar(np.arange(len(categories)),[1]*len(categories),color=[c+"CC" for c in colors],edgecolor=INK)
    ax.set_xticks(np.arange(len(categories)),categories)
    ax.set_yticks([])
    for i,label in enumerate(labels):ax.text(i,.5,label,ha="center",va="center",color=WHITE,weight="bold",fontsize=12)
    ax.set_ylim(0,1)
    ax.set_title("Exact scope of the universal unknown-edge result",weight="bold")
    ax.spines[["left","right","top","bottom"]].set_visible(False)
    fig.tight_layout()
    save_figure(fig,out,"33_claim_boundary")

    # 34 Summary wheel.
    fig,ax=plt.subplots(figsize=(7.8,7.8))
    ax.set_aspect("equal")
    ax.axis("off")
    labels_w=[("model",BLUE),("project",TEAL),("differentiate",GREEN),("measure",YELLOW),("annihilate",ORANGE),("locate",RED),("synthesize",MAGENTA),("check",PURPLE)]
    theta=np.linspace(90,90-360,len(labels_w)+1)
    from matplotlib.patches import Wedge
    for i,(label,color) in enumerate(labels_w):
        wedge=Wedge((0,0),1.0,theta[i+1],theta[i],width=.34,facecolor=color,edgecolor=PAPER,lw=2)
        ax.add_patch(wedge)
        angle=np.deg2rad((theta[i]+theta[i+1])/2)
        ax.text(.80*np.cos(angle),.80*np.sin(angle),label,ha="center",va="center",rotation=(theta[i]+theta[i+1])/2-90,rotation_mode="anchor",fontsize=12,weight="bold",color=WHITE)
    ax.add_patch(Circle((0,0),.48,facecolor=PAPER,edgecolor=INK,lw=2))
    ax.text(0,.08,"unknown-edge",ha="center",fontsize=16,weight="bold")
    ax.text(0,-.03,"recovery",ha="center",fontsize=21,weight="bold")
    ax.text(0,-.17,"exact within the declared class",ha="center",fontsize=10,color=MUTED)
    ax.set_xlim(-1.12,1.12)
    ax.set_ylim(-1.12,1.12)
    ax.set_title("The closed recovery cycle",fontsize=20,weight="bold",pad=12)
    save_figure(fig,out,"34_summary_wheel")


    # 35 Two-dimensional finite dictionary example.
    fig, axes = plt.subplots(1, 4, figsize=(13.0, 3.8))
    panels = [
        rectangle_2d["observed"],
        rectangle_2d["edge"],
        rectangle_2d["recovered_edge"],
        np.abs(rectangle_2d["residual"]),
    ]
    titles = ["observed image", "true rectangle packet", "recovered packet", "absolute residual"]
    cmaps = ["viridis", "magma", "magma", "magma"]
    for axr, panel, title, cmap in zip(axes, panels, titles, cmaps, strict=True):
        image = axr.imshow(panel, origin="lower", cmap=cmap)
        axr.set_title(title, weight="bold", fontsize=10.5)
        axr.set_xticks([])
        axr.set_yticks([])
        fig.colorbar(image, ax=axr, fraction=.046)
    fig.suptitle(
        f"The finite dictionary theorem is dimension-independent: recovered rectangle {rectangle_2d['best_metadata']}",
        fontsize=15.5,
        weight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, .90])
    save_figure(fig, out, "35_two_dimensional_rectangle")


def write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_all(base: Path) -> dict[str, object]:
    base.mkdir(parents=True, exist_ok=True)
    (base / "figures").mkdir(exist_ok=True)
    (base / "tables").mkdir(exist_ok=True)
    (base / "results").mkdir(exist_ok=True)

    exact_rows, representative = run_exact_examples()
    noise_rows = run_noise_experiment()
    close_rows = run_close_edge_experiment()
    runtime_rows = run_runtime_experiment()
    dictionary_data = build_dictionary_example()
    multichannel = build_multichannel_example()
    rectangle_2d = build_2d_rectangle_example()
    tests = run_tests(exact_rows, representative, dictionary_data, multichannel, rectangle_2d)
    generate_figures(base, exact_rows, representative, noise_rows, close_rows, runtime_rows, dictionary_data, multichannel, rectangle_2d, tests)

    write_csv(base / "tables" / "exact_recovery_cases.csv", exact_rows)
    write_csv(base / "tables" / "noise_and_separation.csv", noise_rows)
    write_csv(base / "tables" / "collision_conditioning.csv", close_rows)
    write_csv(base / "tables" / "runtime_scaling.csv", runtime_rows)
    write_csv(base / "tables" / "test_ledger.csv", tests)

    symbolic = exact_symbolic_example()
    result: RecoveryResult = representative["result"]  # type: ignore[assignment]
    edge: EdgeModel = representative["edge"]  # type: ignore[assignment]
    match = match_edge_models(edge, result)
    problem, y, alpha, recovered, gamma = dictionary_data
    summary: dict[str, object] = {
        "formal_scope": "periodic bandlimited background plus finitely many off-grid piecewise-constant jumps",
        "exact_random_cases": len(exact_rows),
        "maximum_exact_location_error": max(float(r["location_error"]) for r in exact_rows),
        "maximum_exact_jump_error": max(float(r["jump_error"]) for r in exact_rows),
        "maximum_exact_reconstruction_error": max(float(r["reconstruction_error"]) for r in exact_rows),
        "representative_edge_order": edge.order,
        "representative_location_error": float(match["location_error_max"]),
        "representative_jump_error": float(match["jump_error_max"]),
        "representative_hankel_condition": result.hankel_condition,
        "representative_vandermonde_condition": result.vandermonde_condition,
        "finite_dictionary_gamma_4": gamma,
        "finite_dictionary_support": list(recovered["support"]),
        "rectangle_2d_true": list(rectangle_2d["true_metadata"]),
        "rectangle_2d_recovered": list(rectangle_2d["best_metadata"]),
        "symbolic_example": symbolic,
        "tests_passed": sum(bool(t["passed"]) for t in tests),
        "tests_total": len(tests),
        "figure_pairs": len(list((base / "figures").glob("*.pdf"))),
    }
    (base / "results" / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    summary = run_all(args.out)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

"""Self-calibrating polyphase Fourier reconstruction.

One file contains the model, recovery algorithms, theorem-facing numerical
certificates, figures, tables, and test runner used by the companion paper.

The implementation studies periodic signals

    f = s + j

where s has a controlled Fourier tail and j is a piecewise-constant packet
with finitely many unknown jumps. The main algorithm combines decimated Prony
recovery with several offset residue channels. The offset coefficients provide
an internal phase estimate that selects the correct branch of each aliased
node. This removes the need for an externally supplied jump neighborhood in
the declared model.
"""

import argparse
import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares, linear_sum_assignment
from scipy.special import iv
import sympy as sp

ComplexArray = NDArray[np.complex128]
RealArray = NDArray[np.float64]
PI = math.pi
TAU = 2.0 * math.pi

INK = "#17202A"
MUTED = "#566573"
PAPER = "#FAFAF7"
WHITE = "#FFFFFF"
BLUE = "#2E86AB"
TEAL = "#2A9D8F"
ORANGE = "#F4A261"
RED = "#E76F51"
MAGENTA = "#A23E8C"
PURPLE = "#6C5CE7"
GREEN = "#6A994E"
YELLOW = "#E9C46A"
GRID = "#D5D8DC"
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


def wrap_angle(x: RealArray | float) -> RealArray | float:
    return np.mod(x, TAU)


def circular_distance(a: float, b: float) -> float:
    d = abs(a - b) % TAU
    return min(d, TAU - d)


def min_circular_separation(locations: RealArray) -> float:
    tau = np.sort(np.mod(np.asarray(locations, dtype=float), TAU))
    gaps = np.diff(np.r_[tau, tau[0] + TAU])
    return float(np.min(gaps))


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
    for _ in range(14):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        box = label.get_window_extent(renderer=renderer)
        (x0, y0), (x1, y1) = ax.transData.transform(((x, y), (x + width, y + height)))
        available_width = abs(x1 - x0) * 0.84
        available_height = abs(y1 - y0) * 0.80
        if box.width <= available_width and box.height <= available_height:
            break
        label.set_fontsize(max(7.4, label.get_fontsize() * 0.90))
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
            fontsize=9.2,
            color=color,
            bbox={"boxstyle": "round,pad=0.12", "facecolor": PAPER, "edgecolor": "none"},
        )
    return arrow


@dataclass(frozen=True)
class EdgePacket:
    locations: RealArray
    jumps: RealArray

    def __post_init__(self) -> None:
        tau = np.mod(np.asarray(self.locations, dtype=float), TAU)
        amp = np.asarray(self.jumps, dtype=float)
        if tau.ndim != 1 or amp.ndim != 1 or tau.size != amp.size:
            raise ValueError("locations and jumps must have equal one-dimensional shapes")
        if tau.size < 2:
            raise ValueError("a nonconstant periodic packet needs at least two jumps")
        order = np.argsort(tau)
        tau = tau[order]
        amp = amp[order]
        if min_circular_separation(tau) <= 1e-10:
            raise ValueError("jump locations must be distinct")
        if np.min(np.abs(amp)) <= 1e-12:
            raise ValueError("zero jumps must be removed")
        if abs(float(np.sum(amp))) > 1e-10:
            raise ValueError("periodic jump amplitudes must sum to zero")
        object.__setattr__(self, "locations", tau)
        object.__setattr__(self, "jumps", amp)

    @property
    def order(self) -> int:
        return int(self.locations.size)

    @property
    def separation(self) -> float:
        return min_circular_separation(self.locations)

    @property
    def nodes(self) -> ComplexArray:
        return np.exp(-1j * self.locations)

    def moments(self, indices: Sequence[int]) -> ComplexArray:
        n = np.asarray(indices, dtype=int)
        return np.asarray(
            [np.sum(self.jumps * np.exp(-1j * int(k) * self.locations)) for k in n],
            dtype=np.complex128,
        )

    def fourier(self, n: int) -> complex:
        if n == 0:
            return 0.0 + 0.0j
        return complex(self.moments([n])[0] / (2j * PI * n))

    def values(self, x: RealArray) -> RealArray:
        xw = np.mod(np.asarray(x, dtype=float), TAU)
        tau = self.locations
        amp = self.jumps
        lengths = np.diff(np.r_[tau, tau[0] + TAU])
        cumulative = np.cumsum(amp)
        base = -float(np.sum(lengths * cumulative) / TAU)
        out = np.full_like(xw, base)
        for location, jump in zip(tau, amp, strict=True):
            out += jump * (xw >= location)
        return out


class Background:
    def __init__(self, fourier: Callable[[int], complex], label: str, decay_order: float | None = None) -> None:
        self._fourier = fourier
        self.label = label
        self.decay_order = decay_order

    def fourier(self, n: int) -> complex:
        return complex(self._fourier(int(n)))

    def values(self, x: RealArray, order: int = 1024) -> RealArray:
        x = np.asarray(x, dtype=float)
        out = np.zeros_like(x, dtype=np.complex128)
        for n in range(-order, order + 1):
            out += self.fourier(n) * np.exp(1j * n * x)
        return np.real_if_close(out, tol=1000).real


def analytic_background() -> Background:
    def coeff(n: int) -> complex:
        value = 0.35 * iv(abs(n), 0.7)
        if n == 2:
            value += -0.1j
        elif n == -2:
            value += 0.1j
        if abs(n) == 5:
            value += -0.075
        return complex(value)

    return Background(coeff, "analytic Bessel-tail background", decay_order=None)


def power_tail_background(p: int, amplitude: float = 0.2, phase: float = 0.37) -> Background:
    if p < 0:
        raise ValueError("p must be nonnegative")

    def coeff(n: int) -> complex:
        if n == 0:
            return 0.1 + 0.0j
        if n > 0:
            return complex(amplitude * np.exp(-1j * n * phase) / (1 + n) ** (p + 2))
        return np.conj(coeff(-n))

    return Background(coeff, f"power-tail background p={p}", decay_order=float(p + 2))


def bandlimited_background() -> Background:
    coefficients = {
        0: 0.25 + 0.0j,
        2: 0.18 - 0.09j,
        -2: 0.18 + 0.09j,
        4: -0.10 + 0.04j,
        -4: -0.10 - 0.04j,
    }

    def coeff(n: int) -> complex:
        return coefficients.get(n, 0.0 + 0.0j)

    return Background(coeff, "bandlimited control background", decay_order=math.inf)


@dataclass(frozen=True)
class SignalModel:
    background: Background
    edge: EdgePacket

    def fourier(self, n: int) -> complex:
        return self.background.fourier(n) + self.edge.fourier(n)

    def moment(self, n: int) -> complex:
        if n == 0:
            return 0.0 + 0.0j
        return 2j * PI * n * self.fourier(n)

    def values(self, x: RealArray, smooth_order: int = 1024) -> RealArray:
        return self.background.values(x, order=smooth_order) + self.edge.values(x)


@dataclass
class RecoveryResult:
    order: int
    decimation: int
    offsets: int
    aliased_nodes: ComplexArray
    coarse_nodes: ComplexArray
    nodes: ComplexArray
    locations: RealArray
    jumps: RealArray
    singular_values: RealArray
    order_gap: float
    offset_coefficients: ComplexArray
    phase_residuals: RealArray
    validation_score: float
    nonlinear_residual: float


def build_hankel(sequence: ComplexArray, rows: int, cols: int) -> ComplexArray:
    if rows + cols - 1 > sequence.size:
        raise ValueError("not enough samples for requested Hankel matrix")
    return np.asarray([[sequence[i + j] for j in range(cols)] for i in range(rows)], dtype=complex)


def estimate_model_order(sequence: ComplexArray, upper_bound: int) -> tuple[int, RealArray, RealArray]:
    if upper_bound < 1:
        raise ValueError("upper_bound must be positive")
    cols = min(max(upper_bound + 2, sequence.size // 2), sequence.size - 2)
    rows = sequence.size - cols + 1
    H = build_hankel(sequence, rows, cols)
    singular = np.linalg.svd(H, compute_uv=False)
    usable = min(upper_bound, singular.size - 1)
    ratios = singular[:usable] / np.maximum(singular[1 : usable + 1], 1e-30)
    order = int(np.argmax(ratios) + 1)
    return order, singular, ratios


def esprit_nodes(sequence: ComplexArray, order: int) -> tuple[ComplexArray, RealArray]:
    if order < 1:
        raise ValueError("order must be positive")
    cols = min(max(order + 2, sequence.size // 2), sequence.size - 2)
    rows = sequence.size - cols + 1
    H = build_hankel(sequence, rows, cols)
    U, singular, _ = np.linalg.svd(H, full_matrices=False)
    Us = U[:, :order]
    Phi = np.linalg.pinv(Us[:-1, :]) @ Us[1:, :]
    nodes = np.linalg.eigvals(Phi)
    return np.asarray(nodes, dtype=complex), np.asarray(singular, dtype=float)


def solve_exponential_coefficients(sequence: ComplexArray, nodes: ComplexArray) -> ComplexArray:
    q = np.arange(sequence.size)
    V = np.column_stack([node**q for node in nodes])
    coefficients, *_ = np.linalg.lstsq(V, sequence, rcond=None)
    return np.asarray(coefficients, dtype=complex)


def multi_offset_phase(coefficients: ComplexArray) -> tuple[ComplexArray, RealArray]:
    """Estimate one unit-circle phase per column from adjacent offset products."""
    if coefficients.ndim != 2 or coefficients.shape[0] < 2:
        raise ValueError("coefficients must contain at least two offset rows")
    correlations = np.sum(np.conj(coefficients[:-1]) * coefficients[1:], axis=0)
    phases = correlations / np.maximum(np.abs(correlations), 1e-30)
    residuals = np.zeros(coefficients.shape[1], dtype=float)
    for j, phase in enumerate(phases):
        numerator = np.linalg.norm(coefficients[1:, j] - phase * coefficients[:-1, j])
        denominator = max(np.linalg.norm(coefficients[:, j]), 1e-30)
        residuals[j] = float(numerator / denominator)
    return phases, residuals


def single_offset_phase(coefficients: ComplexArray) -> ComplexArray:
    ratio = coefficients[1] / np.where(np.abs(coefficients[0]) > 1e-30, coefficients[0], 1.0)
    return ratio / np.maximum(np.abs(ratio), 1e-30)


def lift_aliased_nodes(aliased: ComplexArray, coarse: ComplexArray, decimation: int) -> ComplexArray:
    lifted: list[complex] = []
    for u, zc in zip(aliased, coarse, strict=True):
        unit_u = u / max(abs(u), 1e-30)
        angles = (np.angle(unit_u) + TAU * np.arange(decimation)) / decimation
        candidates = np.exp(1j * angles)
        lifted.append(complex(candidates[np.argmin(np.abs(candidates - zc))]))
    return np.asarray(lifted, dtype=complex)


def constrained_amplitudes(nodes: ComplexArray, moments: ComplexArray, indices: RealArray) -> RealArray:
    V = np.exp(-1j * np.outer(indices, (-np.angle(nodes)) % TAU))
    # Real jumps with zero sum. Eliminate the final amplitude.
    B = V[:, :-1] - V[:, [-1]]
    A = np.vstack([B.real, B.imag])
    b = np.r_[moments.real, moments.imag]
    first, *_ = np.linalg.lstsq(A, b, rcond=None)
    jumps = np.r_[first, -float(np.sum(first))]
    return np.asarray(jumps, dtype=float)


def match_locations(reference: RealArray, recovered: RealArray) -> tuple[RealArray, RealArray, float]:
    cost = np.asarray(
        [[circular_distance(float(a), float(b)) for b in reference] for a in recovered],
        dtype=float,
    )
    rows, cols = linear_sum_assignment(cost)
    order = np.argsort(cols)
    rows = rows[order]
    cols = cols[order]
    return rows, cols, float(np.max(cost[rows, cols]))


def reorder_result(result: RecoveryResult, reference: EdgePacket) -> RecoveryResult:
    rows, _, _ = match_locations(reference.locations, result.locations)
    return RecoveryResult(
        order=result.order,
        decimation=result.decimation,
        offsets=result.offsets,
        aliased_nodes=result.aliased_nodes[rows],
        coarse_nodes=result.coarse_nodes[rows],
        nodes=result.nodes[rows],
        locations=result.locations[rows],
        jumps=result.jumps[rows],
        singular_values=result.singular_values,
        order_gap=result.order_gap,
        offset_coefficients=result.offset_coefficients[:, rows],
        phase_residuals=result.phase_residuals[rows],
        validation_score=result.validation_score,
        nonlinear_residual=result.nonlinear_residual,
    )


def nonlinear_refine(
    model: SignalModel,
    locations: RealArray,
    fit_indices: RealArray,
    max_nfev: int = 300,
) -> tuple[RealArray, RealArray, float]:
    order = locations.size
    observed = np.asarray([model.moment(int(n)) for n in fit_indices], dtype=complex)

    def unpack(theta: RealArray) -> tuple[RealArray, RealArray]:
        tau = np.mod(theta[:order], TAU)
        first = theta[order:]
        jumps = np.r_[first, -np.sum(first)]
        return tau, jumps

    initial_nodes = np.exp(-1j * locations)
    initial_jumps = constrained_amplitudes(initial_nodes, observed, fit_indices)
    theta0 = np.r_[locations, initial_jumps[:-1]]

    def residual(theta: RealArray) -> RealArray:
        tau, jumps = unpack(theta)
        predicted = np.exp(-1j * np.outer(fit_indices, tau)) @ jumps
        error = predicted - observed
        return np.r_[error.real, error.imag]

    fit = least_squares(residual, theta0, max_nfev=max_nfev, xtol=1e-13, ftol=1e-13, gtol=1e-13)
    tau, jumps = unpack(fit.x)
    sort = np.argsort(tau)
    return tau[sort], jumps[sort], float(np.linalg.norm(residual(fit.x)))


def recover_polyphase(
    model: SignalModel,
    decimation: int,
    samples_per_offset: int = 22,
    offsets: int = 5,
    order_upper_bound: int = 8,
    q0: int = 1,
    known_order: int | None = None,
    refine: bool = True,
) -> RecoveryResult:
    if decimation < 2:
        raise ValueError("decimation must be at least two")
    if offsets < 2:
        raise ValueError("at least two offsets are needed")
    sequences: list[ComplexArray] = []
    all_indices: list[int] = []
    for residue in range(offsets):
        indices = np.asarray([(q0 + q) * decimation + residue for q in range(samples_per_offset)], dtype=int)
        all_indices.extend(int(n) for n in indices)
        sequences.append(np.asarray([model.moment(int(n)) for n in indices], dtype=complex))

    if known_order is None:
        order, singular, ratios = estimate_model_order(sequences[0], order_upper_bound)
        order_gap = float(ratios[order - 1])
    else:
        order = int(known_order)
        _, singular = esprit_nodes(sequences[0], order)
        order_gap = float(singular[order - 1] / max(singular[order], 1e-30)) if singular.size > order else math.inf

    aliased, singular = esprit_nodes(sequences[0], order)
    # A deterministic ordering keeps every offset coefficient aligned with the same node.
    node_order = np.argsort(np.angle(aliased))
    aliased = aliased[node_order]
    coefficient_rows = np.asarray(
        [solve_exponential_coefficients(sequence, aliased) for sequence in sequences],
        dtype=complex,
    )
    coarse, phase_residuals = multi_offset_phase(coefficient_rows)
    lifted = lift_aliased_nodes(aliased, coarse, decimation)
    locations = np.mod(-np.angle(lifted), TAU)

    fit_indices = np.arange(decimation, max(all_indices) + 1, dtype=float)
    observed = np.asarray([model.moment(int(n)) for n in fit_indices], dtype=complex)
    jumps = constrained_amplitudes(lifted, observed, fit_indices)
    nonlinear_residual = float(np.linalg.norm(np.exp(-1j * np.outer(fit_indices, locations)) @ jumps - observed))

    if refine:
        locations, jumps, nonlinear_residual = nonlinear_refine(model, locations, fit_indices)
        lifted = np.exp(-1j * locations)

    validation_score = float(np.max(phase_residuals))
    return RecoveryResult(
        order=order,
        decimation=decimation,
        offsets=offsets,
        aliased_nodes=aliased,
        coarse_nodes=coarse,
        nodes=lifted,
        locations=locations,
        jumps=jumps,
        singular_values=singular,
        order_gap=order_gap,
        offset_coefficients=coefficient_rows,
        phase_residuals=phase_residuals,
        validation_score=validation_score,
        nonlinear_residual=nonlinear_residual,
    )



def principal_root_nodes(aliased: ComplexArray, decimation: int) -> ComplexArray:
    """Return the principal branch of each unit-normalized aliased node.

    This is a deliberately naive baseline. It ignores all offset-channel phase
    information and is expected to fail whenever a true phase lies outside the
    principal branch.
    """
    unit = aliased / np.maximum(np.abs(aliased), 1e-30)
    return np.exp(1j * np.angle(unit) / decimation)


def oracle_lift_nodes(
    aliased: ComplexArray,
    true_nodes: ComplexArray,
    decimation: int,
) -> ComplexArray:
    """Lift aliased nodes using true phases only for benchmark evaluation.

    The oracle is not part of the reconstruction algorithm. It supplies the
    branch neighborhoods assumed by classical local analyses and allows a
    direct test of whether the offset-channel lift attains the same branch.
    """
    unit = aliased / np.maximum(np.abs(aliased), 1e-30)
    target = true_nodes**decimation
    rows, cols = linear_sum_assignment(np.abs(unit[:, None] - target[None, :]))
    lifted = np.zeros_like(unit)
    for row, col in zip(rows, cols, strict=True):
        angles = (np.angle(unit[row]) + TAU * np.arange(decimation)) / decimation
        candidates = np.exp(1j * angles)
        lifted[row] = candidates[np.argmin(np.abs(candidates - true_nodes[col]))]
    return lifted


def node_set_distance(left: ComplexArray, right: ComplexArray) -> float:
    """Maximum optimal matching distance between two finite node sets."""
    rows, cols = linear_sum_assignment(np.abs(left[:, None] - right[None, :]))
    return float(np.max(np.abs(left[rows] - right[cols])))


def random_edge_packet(
    rng: np.random.Generator,
    order: int,
    decimation: int = 10,
    physical_separation: float = 0.45,
    aliased_separation: float = 0.35,
) -> EdgePacket:
    """Generate one separated random periodic edge packet for stress tests."""
    for _ in range(20000):
        locations = np.sort(rng.uniform(0.0, TAU, order))
        if min_circular_separation(locations) < physical_separation:
            continue
        aliased_locations = np.mod(-np.angle(np.exp(-1j * decimation * locations)), TAU)
        if min_circular_separation(aliased_locations) < aliased_separation:
            continue
        first = rng.uniform(-1.0, 1.0, order - 1)
        jumps = np.r_[first, -float(np.sum(first))]
        if np.min(np.abs(jumps)) < 0.18 or np.max(np.abs(jumps)) > 2.5:
            continue
        return EdgePacket(locations, jumps)
    raise RuntimeError("unable to generate a separated random edge packet")

def edge_from_result(result: RecoveryResult) -> EdgePacket:
    jumps = result.jumps.copy()
    jumps -= np.sum(jumps) / jumps.size
    return EdgePacket(result.locations, jumps)


def fourier_partial(model: SignalModel, x: RealArray, order: int) -> RealArray:
    out = np.zeros_like(x, dtype=complex)
    for n in range(-order, order + 1):
        out += model.fourier(n) * np.exp(1j * n * x)
    return np.real_if_close(out, tol=1000).real


def fejer_sum(model: SignalModel, x: RealArray, order: int) -> RealArray:
    out = np.zeros_like(x, dtype=complex)
    for n in range(-order, order + 1):
        weight = 1.0 - abs(n) / (order + 1.0)
        out += weight * model.fourier(n) * np.exp(1j * n * x)
    return np.real_if_close(out, tol=1000).real


def resolved_reconstruction(model: SignalModel, result: RecoveryResult, x: RealArray, smooth_order: int) -> RealArray:
    recovered_edge = edge_from_result(result)
    smooth = np.zeros_like(x, dtype=complex)
    for n in range(-smooth_order, smooth_order + 1):
        smooth_coeff = model.fourier(n) - recovered_edge.fourier(n)
        smooth += smooth_coeff * np.exp(1j * n * x)
    return np.real_if_close(smooth, tol=1000).real + recovered_edge.values(x)


def edge_l1_error(true_edge: EdgePacket, recovered_edge: EdgePacket, grid_size: int = 20000) -> float:
    x = np.linspace(0.0, TAU, grid_size, endpoint=False)
    return float(np.mean(np.abs(true_edge.values(x) - recovered_edge.values(x))) * TAU)


def background_reconstruction_error(
    model: SignalModel,
    result: RecoveryResult,
    smooth_order: int,
    grid_size: int = 4096,
) -> float:
    x = np.linspace(0.0, TAU, grid_size, endpoint=False)
    recovered_edge = edge_from_result(result)
    smooth = np.zeros_like(x, dtype=complex)
    for n in range(-smooth_order, smooth_order + 1):
        smooth_coeff = model.fourier(n) - recovered_edge.fourier(n)
        smooth += smooth_coeff * np.exp(1j * n * x)
    true = model.background.values(x, order=max(2048, smooth_order * 4))
    return float(np.sqrt(np.mean((np.real(smooth) - true) ** 2)))


def add_moment_noise(model: SignalModel, sigma: float, seed: int) -> SignalModel:
    rng = np.random.default_rng(seed)
    cache: dict[int, complex] = {}

    class NoisySignal(SignalModel):
        def moment(self, n: int) -> complex:
            if n not in cache:
                cache[n] = model.moment(n) + sigma * (rng.normal() + 1j * rng.normal()) / math.sqrt(2.0)
            return cache[n]

        def fourier(self, n: int) -> complex:
            if n == 0:
                return model.fourier(0)
            return self.moment(n) / (2j * PI * n)

    return NoisySignal(model.background, model.edge)


def exact_edge() -> EdgePacket:
    return EdgePacket(
        np.asarray([0.42, 1.37, 2.85, 4.62]),
        np.asarray([1.0, -0.65, 0.40, -0.75]),
    )



def run_finite_budget_experiment(edge: EdgePacket) -> dict[str, object]:
    """Exact self-calibration from an explicit finite high-frequency budget.

    The background is bandlimited below the first sampled index. The base
    channel contains 2*Lmax+1 moments, which is enough for exact Hankel rank
    and Prony recovery. The adjacent offset contains Lmax moments, which is
    enough to recover the coefficient progression and therefore the physical
    phases without a supplied branch neighborhood.
    """
    model = SignalModel(bandlimited_background(), edge)
    decimation = 10
    order_upper_bound = 6
    q0 = 1

    base_indices = np.asarray(
        [(q0 + q) * decimation for q in range(2 * order_upper_bound + 1)],
        dtype=int,
    )
    base_sequence = np.asarray(
        [model.moment(int(n)) for n in base_indices],
        dtype=complex,
    )
    H = build_hankel(
        base_sequence,
        order_upper_bound + 1,
        order_upper_bound + 1,
    )
    singular = np.linalg.svd(H, compute_uv=False)
    tolerance = max(float(singular[0]) * 1e-10, 1e-13)
    order = int(np.sum(singular > tolerance))

    aliased, _ = esprit_nodes(base_sequence, order)
    aliased = aliased / np.maximum(np.abs(aliased), 1e-30)
    node_order = np.argsort(np.angle(aliased))
    aliased = aliased[node_order]
    base_coefficients = solve_exponential_coefficients(base_sequence, aliased)

    offset_indices = np.asarray(
        [(q0 + q) * decimation + 1 for q in range(order_upper_bound)],
        dtype=int,
    )
    offset_sequence = np.asarray(
        [model.moment(int(n)) for n in offset_indices],
        dtype=complex,
    )
    offset_coefficients = solve_exponential_coefficients(
        offset_sequence,
        aliased,
    )

    nodes = offset_coefficients / base_coefficients
    nodes = nodes / np.maximum(np.abs(nodes), 1e-30)
    jumps = np.real_if_close(
        base_coefficients / aliased**q0,
        tol=1000,
    ).real
    locations = np.mod(-np.angle(nodes), TAU)
    location_order = np.argsort(locations)
    locations = locations[location_order]
    jumps = jumps[location_order]

    location_error = max(
        circular_distance(a, b)
        for a, b in zip(edge.locations, locations, strict=True)
    )
    jump_error = float(np.max(np.abs(edge.jumps - jumps)))
    return {
        "order_upper_bound": order_upper_bound,
        "true_order": edge.order,
        "recovered_order": order,
        "decimation": decimation,
        "q0": q0,
        "base_indices": base_indices.tolist(),
        "offset_indices": offset_indices.tolist(),
        "high_frequency_sample_count": int(base_indices.size + offset_indices.size),
        "theoretical_budget": int(3 * order_upper_bound + 1),
        "recovered_locations": locations.tolist(),
        "recovered_jumps": jumps.tolist(),
        "location_error": float(location_error),
        "jump_error": jump_error,
        "rank_singular_values": singular.tolist(),
    }

def symbolic_confluent_check() -> dict[str, str]:
    """Exact degree-one exponential-polynomial offset calculation."""
    I = sp.I
    z = [sp.Integer(1), I]
    A = [sp.Integer(2), sp.Integer(-3)]
    B = [sp.Integer(5), sp.Integer(4)]
    N = 3
    q0 = 1
    rows: dict[int, list[sp.Expr]] = {}
    for r in range(3):
        values: list[sp.Expr] = []
        for q in range(8):
            n = (q0 + q) * N + r
            values.append(sp.expand(sum((A[j] * n + B[j]) * z[j] ** n for j in range(2))))
        rows[r] = values

    # The aliased nodes are u_j=z_j^N. Fit c0_j u^q + c1_j q u^q.
    u = [value**N for value in z]
    leading: dict[int, list[sp.Expr]] = {}
    for r in range(3):
        unknowns = sp.symbols(f"c0_0_{r} c1_0_{r} c0_1_{r} c1_1_{r}")
        equations = []
        for q in range(4):
            expression = (
                (unknowns[0] + unknowns[1] * q) * u[0] ** q
                + (unknowns[2] + unknowns[3] * q) * u[1] ** q
                - rows[r][q]
            )
            equations.append(sp.Eq(expression, 0))
        solution = sp.solve(equations, unknowns, dict=True)[0]
        leading[r] = [sp.simplify(solution[unknowns[1]]), sp.simplify(solution[unknowns[3]])]

    ratios = [sp.simplify(leading[1][j] / leading[0][j]) for j in range(2)]
    validation = [sp.simplify(leading[2][j] * leading[0][j] - leading[1][j] ** 2) for j in range(2)]
    return {
        "node_0_ratio": str(ratios[0]),
        "node_1_ratio": str(ratios[1]),
        "validation_0": str(validation[0]),
        "validation_1": str(validation[1]),
    }


def run_rate_experiment(edge: EdgePacket) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    decimations = [4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24]
    for p in range(4):
        model = SignalModel(power_tail_background(p), edge)
        for N in decimations:
            result = recover_polyphase(model, N, samples_per_offset=22, offsets=5, known_order=edge.order, refine=False)
            result = reorder_result(result, edge)
            location_error = float(
                max(circular_distance(a, b) for a, b in zip(edge.locations, result.locations, strict=True))
            )
            rows.append(
                {
                    "p": p,
                    "decimation": N,
                    "location_error": location_error,
                    "validation_score": result.validation_score,
                }
            )
    return rows


def run_noise_experiment(edge: EdgePacket) -> list[dict[str, float]]:
    model = SignalModel(analytic_background(), edge)
    rows: list[dict[str, float]] = []
    for sigma in [1e-10, 1e-8, 1e-6, 1e-5, 1e-4]:
        errors: list[float] = []
        validations: list[float] = []
        order_success = 0
        for seed in range(30):
            noisy = add_moment_noise(model, sigma, seed)
            result = recover_polyphase(noisy, 10, samples_per_offset=22, offsets=6, order_upper_bound=7, refine=False)
            if result.order == edge.order:
                order_success += 1
                result = reorder_result(result, edge)
                errors.append(
                    max(circular_distance(a, b) for a, b in zip(edge.locations, result.locations, strict=True))
                )
                validations.append(result.validation_score)
        rows.append(
            {
                "sigma": sigma,
                "median_location_error": float(np.median(errors)) if errors else math.nan,
                "maximum_location_error": float(np.max(errors)) if errors else math.nan,
                "median_validation": float(np.median(validations)) if validations else math.nan,
                "order_success_rate": order_success / 30.0,
            }
        )
    return rows


def run_offset_averaging_experiment(edge: EdgePacket) -> list[dict[str, float | int]]:
    """Compare one offset ratio with the multi-offset phase estimator.

    This experiment perturbs the recovered offset coefficients directly with
    independent complex noise. It isolates the phase-estimation theorem from
    the separate aliased-node perturbation.
    """
    rows: list[dict[str, float | int]] = []
    rng = np.random.default_rng(17)
    nodes = edge.nodes
    base = edge.jumps * nodes**10
    for R in [2, 3, 4, 6, 8]:
        single_errors: list[float] = []
        multi_errors: list[float] = []
        for _ in range(500):
            coefficients = np.asarray([base * nodes**r for r in range(R)], dtype=complex)
            coefficients += 0.02 * (
                rng.normal(size=coefficients.shape)
                + 1j * rng.normal(size=coefficients.shape)
            ) / math.sqrt(2.0)
            single = single_offset_phase(coefficients)
            multi, _ = multi_offset_phase(coefficients)
            single_errors.append(float(np.max(np.abs(np.angle(single * np.conj(nodes))))))
            multi_errors.append(float(np.max(np.abs(np.angle(multi * np.conj(nodes))))))
        rows.append(
            {
                "offsets": R,
                "single_median": float(np.median(single_errors)),
                "multi_median": float(np.median(multi_errors)),
                "single_q90": float(np.quantile(single_errors, 0.9)),
                "multi_q90": float(np.quantile(multi_errors, 0.9)),
            }
        )
    return rows


def run_collision_experiment() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for delta in [0.80, 0.45, 0.25, 0.14, 0.08, 0.045, 0.025]:
        locations = np.asarray([0.6, 0.6 + delta, 3.2, 4.7])
        jumps = np.asarray([1.0, -1.0, 0.55, -0.55])
        edge = EdgePacket(locations, jumps)
        model = SignalModel(analytic_background(), edge)
        noisy = add_moment_noise(model, 1e-6, seed=44)
        try:
            result = recover_polyphase(noisy, 10, samples_per_offset=24, offsets=6, known_order=4, refine=False)
            _, _, error = match_locations(edge.locations, result.locations)
            singular_ratio = float(result.singular_values[3] / max(result.singular_values[4], 1e-30))
            validation = result.validation_score
        except Exception:
            error = math.nan
            singular_ratio = math.nan
            validation = math.nan
        rows.append(
            {
                "separation": delta,
                "location_error": error,
                "rank_gap": singular_ratio,
                "validation": validation,
            }
        )
    return rows



def run_oracle_equivalence_experiment(edge: EdgePacket) -> list[dict[str, float | int]]:
    """Compare self-calibrated lifting with an oracle and a principal root."""
    rows: list[dict[str, float | int]] = []
    for p in range(4):
        model = SignalModel(power_tail_background(p), edge)
        for decimation in [6, 8, 10, 12, 16, 20, 24]:
            result = recover_polyphase(
                model,
                decimation,
                samples_per_offset=22,
                offsets=5,
                known_order=edge.order,
                refine=False,
            )
            principal = principal_root_nodes(result.aliased_nodes, decimation)
            oracle = oracle_lift_nodes(result.aliased_nodes, edge.nodes, decimation)
            principal_error = match_locations(
                edge.locations,
                np.mod(-np.angle(principal), TAU),
            )[2]
            oracle_error = match_locations(
                edge.locations,
                np.mod(-np.angle(oracle), TAU),
            )[2]
            self_error = match_locations(edge.locations, result.locations)[2]
            rows.append(
                {
                    "p": p,
                    "decimation": decimation,
                    "principal_error": principal_error,
                    "oracle_error": oracle_error,
                    "self_calibrated_error": self_error,
                    "oracle_self_node_distance": node_set_distance(oracle, result.nodes),
                }
            )
    return rows


def run_random_stress_experiment(cases: int = 100) -> list[dict[str, float | int]]:
    """Test unknown-order recovery on a deterministic separated signal family."""
    rng = np.random.default_rng(20260729)
    rows: list[dict[str, float | int]] = []
    for case in range(cases):
        order = int(rng.integers(2, 6))
        edge = random_edge_packet(rng, order)
        p = int(rng.integers(0, 4))
        background = power_tail_background(
            p,
            amplitude=0.12,
            phase=float(rng.uniform(0.0, TAU)),
        )
        model = SignalModel(background, edge)
        result = recover_polyphase(
            model,
            10,
            samples_per_offset=26,
            offsets=6,
            order_upper_bound=7,
            refine=False,
        )
        if result.order == order:
            location_error = match_locations(edge.locations, result.locations)[2]
        else:
            location_error = math.inf
        rows.append(
            {
                "case": case,
                "tail_index": p,
                "true_order": order,
                "recovered_order": result.order,
                "physical_separation": edge.separation,
                "aliased_separation": min_circular_separation(
                    np.mod(-np.angle(edge.nodes**10), TAU)
                ),
                "location_error": location_error,
                "validation_score": result.validation_score,
                "order_gap": result.order_gap,
            }
        )
    return rows

def run_reconstruction_experiment(edge: EdgePacket) -> dict[str, float]:
    model = SignalModel(power_tail_background(2), edge)
    result = recover_polyphase(model, 10, samples_per_offset=24, offsets=6, order_upper_bound=7, refine=True)
    result = reorder_result(result, edge)
    x = np.linspace(0.0, TAU, 8192, endpoint=False)
    truth = model.values(x, smooth_order=4096)
    raw = fourier_partial(model, x, 48)
    fejer = fejer_sum(model, x, 48)
    resolved = resolved_reconstruction(model, result, x, 48)
    edge_rec = edge_from_result(result)
    return {
        "raw_rmse": float(np.sqrt(np.mean((raw - truth) ** 2))),
        "fejer_rmse": float(np.sqrt(np.mean((fejer - truth) ** 2))),
        "resolved_rmse": float(np.sqrt(np.mean((resolved - truth) ** 2))),
        "raw_max": float(np.max(np.abs(raw - truth))),
        "fejer_max": float(np.max(np.abs(fejer - truth))),
        "resolved_max": float(np.max(np.abs(resolved - truth))),
        "edge_l1": edge_l1_error(edge, edge_rec),
        "smooth_rmse": background_reconstruction_error(model, result, 48),
        "location_error": float(
            max(circular_distance(a, b) for a, b in zip(edge.locations, result.locations, strict=True))
        ),
        "jump_error": float(np.max(np.abs(edge.jumps - result.jumps))),
    }


def run_runtime_experiment(edge: EdgePacket) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    model = SignalModel(analytic_background(), edge)
    for Q in [12, 16, 20, 28, 36, 48]:
        values: list[float] = []
        for _ in range(10):
            start = time.perf_counter()
            recover_polyphase(model, 10, samples_per_offset=Q, offsets=6, known_order=edge.order, refine=False)
            values.append(time.perf_counter() - start)
        rows.append({"samples_per_offset": Q, "median_seconds": float(np.median(values))})
    return rows


def run_tests(
    edge: EdgePacket,
    exact_result: RecoveryResult,
    analytic_result: RecoveryResult,
    symbolic: dict[str, str],
    rate_rows: list[dict[str, float | int]],
    noise_rows: list[dict[str, float]],
    offset_rows: list[dict[str, float | int]],
    oracle_rows: list[dict[str, float | int]],
    stress_rows: list[dict[str, float | int]],
    finite_budget: dict[str, object],
    reconstruction: dict[str, float],
) -> list[dict[str, object]]:
    tests: list[tuple[str, bool, str]] = []

    tests.append(("periodic jump sum", abs(float(np.sum(edge.jumps))) < 1e-12, str(np.sum(edge.jumps))))
    tests.append(("unknown order exact", exact_result.order == edge.order, str(exact_result.order)))
    tests.append(("exact location recovery", max(circular_distance(a, b) for a, b in zip(edge.locations, exact_result.locations, strict=True)) < 1e-10, str(exact_result.locations)))
    tests.append(("exact amplitude recovery", float(np.max(np.abs(edge.jumps - exact_result.jumps))) < 1e-9, str(exact_result.jumps)))
    tests.append(("exact offset validation", exact_result.validation_score < 1e-10, str(exact_result.validation_score)))
    tests.append(("analytic unknown order", analytic_result.order == edge.order, str(analytic_result.order)))
    tests.append(("analytic location recovery", max(circular_distance(a, b) for a, b in zip(edge.locations, analytic_result.locations, strict=True)) < 1e-8, str(analytic_result.locations)))
    tests.append(("symbolic confluent ratio node 0", symbolic["node_0_ratio"] == "1", symbolic["node_0_ratio"]))
    tests.append(("symbolic confluent ratio node 1", symbolic["node_1_ratio"] in {"I", "I*1"}, symbolic["node_1_ratio"]))
    tests.append(("symbolic confluent validation", symbolic["validation_0"] == "0" and symbolic["validation_1"] == "0", str(symbolic)))

    for p in range(4):
        group = [row for row in rate_rows if int(row["p"]) == p]
        tail = [float(row["location_error"]) for row in group if int(row["decimation"]) >= 8]
        tests.append((f"rate family p={p}", np.median(tail[-3:]) < np.median(tail[:3]), str(tail)))

    tests.append(("noise order recovery", min(row["order_success_rate"] for row in noise_rows[:4]) >= 0.9, str(noise_rows)))
    tests.append(("noise monotonicity", noise_rows[0]["median_location_error"] < noise_rows[-1]["median_location_error"], str(noise_rows)))
    tests.append(("multi-offset improvement", sum(float(row["multi_median"]) <= float(row["single_median"]) for row in offset_rows) >= 3, str(offset_rows)))
    tests.append(("resolved reconstruction beats raw", reconstruction["resolved_rmse"] < reconstruction["raw_rmse"], str(reconstruction)))
    tests.append(("resolved reconstruction beats Fejer", reconstruction["resolved_rmse"] < reconstruction["fejer_rmse"], str(reconstruction)))
    tests.append(("edge L1 small", reconstruction["edge_l1"] < 3e-5, str(reconstruction["edge_l1"])))
    tests.append(("smooth RMSE small", reconstruction["smooth_rmse"] < 1e-5, str(reconstruction["smooth_rmse"])))
    tests.append(("positive rank gap", analytic_result.order_gap > 10.0, str(analytic_result.order_gap)))

    # Algebraic identities independent of the end-to-end solver.
    nodes = edge.nodes
    N = 9
    u = nodes**N
    base = edge.jumps * u
    coeff = np.asarray([base * nodes**r for r in range(5)])
    phase, residual = multi_offset_phase(coeff)
    tests.append(("multi-offset phase identity", float(np.max(np.abs(phase - nodes))) < 1e-12, str(phase)))
    tests.append(("multi-offset residual identity", float(np.max(residual)) < 1e-12, str(residual)))
    lifted = lift_aliased_nodes(u, phase, N)
    tests.append(("branch lifting identity", float(np.max(np.abs(lifted - nodes))) < 1e-12, str(lifted)))

    # A deliberately wrong principal branch should fail for this example.
    principal = np.exp(1j * np.angle(u) / N)
    principal_error = float(np.max([min(abs(value - z) for z in nodes) for value in principal]))
    tests.append(("principal-root negative control", principal_error > 0.1, str(principal_error)))

    oracle_distance = max(float(row["oracle_self_node_distance"]) for row in oracle_rows)
    tests.append(("oracle-equivalent branch lifting", oracle_distance < 1e-10, str(oracle_distance)))
    principal_median = float(np.median([float(row["principal_error"]) for row in oracle_rows]))
    self_median = float(np.median([float(row["self_calibrated_error"]) for row in oracle_rows]))
    tests.append(("self-calibration beats principal root", self_median < 1e-3 * principal_median, f"{self_median} vs {principal_median}"))
    stress_order_rate = float(np.mean([int(row["true_order"]) == int(row["recovered_order"]) for row in stress_rows]))
    stress_location_rate = float(np.mean([float(row["location_error"]) < 1e-3 for row in stress_rows]))
    tests.append(("random-family order recovery", stress_order_rate >= 0.98, str(stress_order_rate)))
    tests.append(("random-family branch recovery", stress_location_rate >= 0.98, str(stress_location_rate)))
    finite_budget_pass = (
        int(finite_budget["recovered_order"]) == edge.order
        and int(finite_budget["high_frequency_sample_count"]) == int(finite_budget["theoretical_budget"])
        and float(finite_budget["location_error"]) < 1e-10
        and float(finite_budget["jump_error"]) < 1e-10
    )
    tests.append(("explicit finite sample budget", finite_budget_pass, str(finite_budget)))

    return [
        {"name": name, "passed": bool(passed), "detail": detail}
        for name, passed, detail in tests
    ]


def generate_figures(
    base: Path,
    edge: EdgePacket,
    exact_result: RecoveryResult,
    analytic_result: RecoveryResult,
    rate_rows: list[dict[str, float | int]],
    noise_rows: list[dict[str, float]],
    offset_rows: list[dict[str, float | int]],
    collision_rows: list[dict[str, float]],
    runtime_rows: list[dict[str, float | int]],
    oracle_rows: list[dict[str, float | int]],
    stress_rows: list[dict[str, float | int]],
    finite_budget: dict[str, object],
    reconstruction: dict[str, float],
) -> None:
    out = base / "figures"
    out.mkdir(parents=True, exist_ok=True)

    # 01 architecture
    fig, ax = diagram_axes((13.0, 5.6))
    ax.text(0.5, 0.91, "Self-calibrating polyphase Fourier reconstruction", ha="center", fontsize=22, weight="bold")
    stages = [
        ("Fourier data", BLUE),
        ("derivative moments", TEAL),
        ("decimated Hankel rank", GREEN),
        ("aliased nodes", ORANGE),
        ("offset phases", MAGENTA),
        ("branch lifting", PURPLE),
        ("edge-native synthesis", RED),
    ]
    xs = np.linspace(0.02, 0.84, len(stages))
    for i, ((label, color), x0) in enumerate(zip(stages, xs, strict=True)):
        draw_box(ax, (x0, 0.43), 0.13, 0.18, label, face=color + "20", edge=color, fontsize=10.5)
        if i < len(stages) - 1:
            draw_arrow(ax, (x0 + 0.13, 0.52), (xs[i + 1] - 0.005, 0.52))
    ax.text(0.5, 0.18, "Unknown jump count, no externally supplied jump neighborhoods, and a validation residual from unused offsets", ha="center", fontsize=12, color=MUTED)
    save_figure(fig, out, "01_architecture")

    # 02 model signal
    model = SignalModel(analytic_background(), edge)
    x = np.linspace(0.0, TAU, 2048, endpoint=False)
    fig, axes = plt.subplots(3, 1, figsize=(12.5, 7.3), sharex=True)
    axes[0].plot(x, model.background.values(x, 2048), color=BLUE, lw=2)
    axes[0].set_title("Non-bandlimited smooth background", loc="left", weight="bold")
    axes[1].plot(x, edge.values(x), color=ORANGE, lw=2)
    for tau in edge.locations:
        axes[1].axvline(tau, color=RED, lw=0.8, alpha=0.55)
    axes[1].set_title("Unknown piecewise-constant edge packet", loc="left", weight="bold")
    axes[2].plot(x, model.values(x, 2048), color=INK, lw=2)
    axes[2].set_title("Observed signal", loc="left", weight="bold")
    axes[2].set_xlabel("periodic coordinate")
    for a in axes:
        a.grid(alpha=0.16)
        a.set_ylabel("amplitude")
    fig.tight_layout()
    save_figure(fig, out, "02_signal_model")

    # 03 Fourier tail
    ns = np.arange(1, 101)
    smooth_mag = np.asarray([abs(model.background.fourier(int(n))) for n in ns])
    edge_mag = np.asarray([abs(edge.fourier(int(n))) for n in ns])
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    ax.semilogy(ns, smooth_mag, label="smooth background", color=BLUE, lw=2)
    ax.semilogy(ns, edge_mag, label="edge packet", color=ORANGE, lw=2)
    ax.set_title("The jump controls the high-frequency tail", weight="bold")
    ax.set_xlabel("Fourier index")
    ax.set_ylabel("coefficient magnitude")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, out, "03_fourier_tail")

    # 04 derivative moments
    indices = np.arange(1, 100)
    moments = np.asarray([model.moment(int(n)) for n in indices])
    true_moments = edge.moments(indices)
    fig, axes = plt.subplots(2, 1, figsize=(12.0, 6.4), sharex=True)
    axes[0].plot(indices, moments.real, color=BLUE, lw=1.1, label="observed real")
    axes[0].plot(indices, true_moments.real, color=INK, lw=0.9, ls="--", label="edge-only real")
    axes[0].legend(ncol=2)
    axes[0].set_ylabel("real part")
    axes[1].plot(indices, np.abs(moments - true_moments), color=RED, lw=1.4)
    axes[1].set_yscale("log")
    axes[1].set_ylabel("smooth-tail defect")
    axes[1].set_xlabel("moment index")
    for a in axes:
        a.grid(alpha=0.16)
    fig.suptitle("Differentiation turns jumps into an exponential moment sequence", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, .93])
    save_figure(fig, out, "04_derivative_moments")

    # 05 polyphase lattice
    fig, ax = diagram_axes((12.5, 6.0))
    ax.text(0.5, 0.93, "A high-frequency band is reorganized into offset polyphase channels", ha="center", fontsize=20, weight="bold")
    N = 10
    for r in range(6):
        y = 0.78 - r * 0.115
        ax.text(0.06, y, f"r={r}", ha="right", va="center", weight="bold", color=PALETTE[r])
        for q in range(8):
            n = (q + 1) * N + r
            ax.add_patch(Circle((0.11 + q * 0.105, y), 0.023, facecolor=PALETTE[r] + "33", edgecolor=PALETTE[r], lw=1.4))
            ax.text(0.11 + q * 0.105, y - 0.045, str(n), ha="center", fontsize=8)
    ax.text(0.5, 0.08, r"m_{qN+r}=\sum_j (a_jz_j^r)(z_j^N)^q+e_{qN+r}", ha="center", fontsize=16)
    save_figure(fig, out, "05_polyphase_lattice")

    # 06 rank spectrum
    s = analytic_result.singular_values
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.semilogy(np.arange(1, min(13, len(s)) + 1), s[:12], marker="o", color=TEAL, lw=2)
    ax.axvline(edge.order + 0.5, color=RED, ls="--", lw=1.2, label=f"estimated order = {edge.order}")
    ax.set_title("Hankel singular values expose the unknown jump count", weight="bold")
    ax.set_xlabel("singular-value index")
    ax.set_ylabel("singular value")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, out, "06_hankel_rank")

    # 07 aliased unit circle
    N = analytic_result.decimation
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2))
    theta = np.linspace(0, TAU, 400)
    for axr in axes:
        axr.plot(np.cos(theta), np.sin(theta), color=GRID, lw=1.2)
        axr.axhline(0, color=GRID, lw=0.7)
        axr.axvline(0, color=GRID, lw=0.7)
        axr.set_aspect("equal")
        axr.set_xlim(-1.15, 1.15)
        axr.set_ylim(-1.15, 1.15)
    axes[0].scatter(edge.nodes.real, edge.nodes.imag, c=PALETTE[:edge.order], s=85, edgecolor=INK)
    axes[0].set_title("true edge phases $z_j$", weight="bold")
    u = edge.nodes**N
    axes[1].scatter(u.real, u.imag, c=PALETTE[:edge.order], s=85, edgecolor=INK)
    axes[1].set_title(rf"aliased phases $u_j=z_j^{{{N}}}$", weight="bold")
    fig.suptitle("Decimation improves separation but creates branch ambiguity", fontsize=17, weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig, out, "07_alias_geometry")

    # 08 branch candidates
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.plot(np.cos(theta), np.sin(theta), color=GRID)
    u0 = analytic_result.aliased_nodes[0] / abs(analytic_result.aliased_nodes[0])
    candidates = np.exp(1j * (np.angle(u0) + TAU * np.arange(N)) / N)
    ax.scatter(candidates.real, candidates.imag, s=48, color=BLUE, label="$N$ candidate roots")
    zc = analytic_result.coarse_nodes[0]
    zhat = analytic_result.nodes[0]
    ax.scatter([zc.real], [zc.imag], marker="x", s=110, color=MAGENTA, linewidth=2.4, label="offset phase estimate")
    ax.scatter([zhat.real], [zhat.imag], marker="*", s=160, color=ORANGE, edgecolor=INK, label="selected branch")
    ax.set_aspect("equal")
    ax.set_xlim(-1.15,1.15)
    ax.set_ylim(-1.15,1.15)
    ax.set_title("Offset phases select the correct root internally", weight="bold")
    ax.legend(loc="upper right")
    ax.grid(alpha=.12)
    save_figure(fig, out, "08_branch_selection")

    # 09 offset coefficient spirals
    coeff = analytic_result.offset_coefficients
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.5))
    for j, axr in enumerate(axes.ravel()):
        values = coeff[:, j]
        axr.plot(values.real, values.imag, marker="o", color=PALETTE[j], lw=1.8)
        for r, value in enumerate(values):
            axr.text(value.real, value.imag, str(r), fontsize=8)
        axr.set_title(f"node {j+1}, phase residual {analytic_result.phase_residuals[j]:.2e}", weight="bold", fontsize=10.5)
        axr.axhline(0,color=GRID,lw=.7)
        axr.axvline(0,color=GRID,lw=.7)
        axr.set_aspect("equal", adjustable="datalim")
    fig.suptitle("Across offsets, each coefficient follows one geometric phase progression", fontsize=16.5, weight="bold")
    fig.tight_layout(rect=[0,0,1,.94])
    save_figure(fig, out, "09_offset_coefficients")

    # 10 validation bars
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    ax.bar(np.arange(edge.order), analytic_result.phase_residuals, color=PALETTE[:edge.order], edgecolor=INK)
    ax.set_yscale("log")
    ax.set_xticks(np.arange(edge.order), [f"edge {j+1}" for j in range(edge.order)])
    ax.set_ylabel("normalized offset recurrence residual")
    ax.set_title("Unused offsets provide an a posteriori phase certificate", weight="bold")
    ax.grid(alpha=.18, axis="y")
    save_figure(fig, out, "10_validation_residual")

    # 11 exact recovery table visual
    fig, ax = plt.subplots(figsize=(11.0, 4.8))
    ax.axis("off")
    columns = ["edge", "true location", "recovered location", "true jump", "recovered jump"]
    rows = []
    for j in range(edge.order):
        rows.append([
            str(j+1),
            f"{edge.locations[j]:.12f}",
            f"{analytic_result.locations[j]:.12f}",
            f"{edge.jumps[j]:.8f}",
            f"{analytic_result.jumps[j]:.8f}",
        ])
    table = ax.table(cellText=rows, colLabels=columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.65)
    ax.set_title("Recovered edge parameters", weight="bold", pad=18)
    save_figure(fig, out, "11_recovered_parameters")

    # 12 rate curves
    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    for p, color in zip(range(4), PALETTE[:4], strict=True):
        group = [row for row in rate_rows if int(row["p"]) == p]
        Nvals = np.asarray([row["decimation"] for row in group], dtype=float)
        errors = np.asarray([row["location_error"] for row in group], dtype=float)
        ax.loglog(Nvals, errors, marker="o", lw=1.9, color=color, label=f"tail exponent p={p}")
    ax.set_title("Jump-location error improves with smooth-background decay", weight="bold")
    ax.set_xlabel("decimation scale N")
    ax.set_ylabel("maximum circular location error")
    ax.grid(alpha=.2, which="both")
    ax.legend()
    save_figure(fig, out, "12_rate_curves")

    # 13 fitted slopes
    slopes=[]
    for p in range(4):
        group=[row for row in rate_rows if int(row["p"])==p and int(row["decimation"])>=8]
        xx=np.log(np.asarray([row["decimation"] for row in group],float))
        yy=np.log(np.maximum(np.asarray([row["location_error"] for row in group],float),1e-16))
        slopes.append(float(np.polyfit(xx,yy,1)[0]))
    fig, ax=plt.subplots(figsize=(9.5,5.2))
    ax.bar(np.arange(4),[-s for s in slopes],color=PALETTE[:4],edgecolor=INK,label="observed magnitude")
    ax.plot(np.arange(4),np.arange(2,6),marker="o",color=INK,lw=1.5,label="reference p+2")
    ax.set_xticks(np.arange(4),[f"p={p}" for p in range(4)])
    ax.set_ylabel("empirical decay exponent")
    ax.set_title("Observed localization rates track the predicted one-order lifting",weight="bold")
    ax.legend();ax.grid(alpha=.16,axis="y")
    save_figure(fig,out,"13_rate_slopes")

    # 14 noise
    fig, ax=plt.subplots(figsize=(10.0,5.5))
    sig=np.asarray([row["sigma"] for row in noise_rows])
    med=np.asarray([row["median_location_error"] for row in noise_rows])
    mx=np.asarray([row["maximum_location_error"] for row in noise_rows])
    ax.loglog(sig,med,marker="o",color=TEAL,lw=2,label="median")
    ax.loglog(sig,mx,marker="o",color=ORANGE,lw=1.5,label="maximum")
    ax.set_xlabel("moment noise standard deviation")
    ax.set_ylabel("location error")
    ax.set_title("Noise propagates continuously until the branch margin is threatened",weight="bold")
    ax.grid(alpha=.2,which="both");ax.legend()
    save_figure(fig,out,"14_noise_error")

    # 15 order success
    fig, ax=plt.subplots(figsize=(9.5,5.0))
    ax.semilogx(sig,[row["order_success_rate"] for row in noise_rows],marker="o",color=BLUE,lw=2)
    ax.set_ylim(-.03,1.05)
    ax.set_xlabel("moment noise standard deviation")
    ax.set_ylabel("correct order frequency")
    ax.set_title("Unknown jump count is recovered from the Hankel gap",weight="bold")
    ax.grid(alpha=.18)
    save_figure(fig,out,"15_order_success")

    # 16 offset averaging
    fig, ax=plt.subplots(figsize=(10.0,5.5))
    R=np.asarray([row["offsets"] for row in offset_rows])
    single=np.asarray([row["single_median"] for row in offset_rows])
    multi=np.asarray([row["multi_median"] for row in offset_rows])
    ax.semilogy(R,single,marker="o",color=ORANGE,lw=2,label="single ratio")
    ax.semilogy(R,multi,marker="o",color=TEAL,lw=2,label="multi-offset phase fit")
    ax.set_xlabel("number of offset channels")
    ax.set_ylabel("median location error")
    ax.set_title("Several offsets stabilize the internal branch selector",weight="bold")
    ax.grid(alpha=.18);ax.legend()
    save_figure(fig,out,"16_offset_averaging")

    # 17 collision boundary
    fig, axes=plt.subplots(1,2,figsize=(12.0,4.9))
    sep=np.asarray([row["separation"] for row in collision_rows])
    err=np.asarray([row["location_error"] for row in collision_rows])
    gap=np.asarray([row["rank_gap"] for row in collision_rows])
    axes[0].loglog(sep,err,marker="o",color=RED,lw=2)
    axes[0].invert_xaxis();axes[0].set_xlabel("minimum separation");axes[0].set_ylabel("location error")
    axes[0].set_title("near-collision error",weight="bold");axes[0].grid(alpha=.18)
    axes[1].loglog(sep,gap,marker="o",color=PURPLE,lw=2)
    axes[1].invert_xaxis();axes[1].set_xlabel("minimum separation");axes[1].set_ylabel("rank gap")
    axes[1].set_title("Hankel gap collapse",weight="bold");axes[1].grid(alpha=.18)
    fig.suptitle("The method exposes rather than hides the separation barrier",fontsize=16.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig,out,"17_collision_boundary")

    # 18 raw/fejer/resolved
    model2=SignalModel(power_tail_background(2),edge)
    result2=recover_polyphase(model2,10,samples_per_offset=24,offsets=6,order_upper_bound=7,refine=True)
    result2=reorder_result(result2,edge)
    xx=np.linspace(0,TAU,4096,endpoint=False)
    truth=model2.values(xx,4096)
    raw=fourier_partial(model2,xx,48)
    fej=fejer_sum(model2,xx,48)
    res=resolved_reconstruction(model2,result2,xx,48)
    fig,axes=plt.subplots(3,1,figsize=(12.3,8.2),sharex=True)
    for axr,curve,title,color in [
        (axes[0],raw,"raw Fourier partial sum",BLUE),
        (axes[1],fej,"Fejer averaging",TEAL),
        (axes[2],res,"polyphase edge recovery plus native synthesis",MAGENTA),
    ]:
        axr.plot(xx,truth,color=INK,lw=2,label="truth")
        axr.plot(xx,curve,color=color,lw=1.2,label=title)
        for tau in edge.locations: axr.axvline(tau,color=RED,lw=.65,alpha=.45)
        axr.legend(loc="upper right",ncol=2,fontsize=8.8)
        axr.grid(alpha=.15)
        axr.set_ylabel("amplitude")
    axes[-1].set_xlabel("periodic coordinate")
    fig.suptitle("The recovered edge is synthesized directly instead of through a global partial sum",fontsize=16.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.94])
    save_figure(fig,out,"18_reconstruction_comparison")

    # 19 errors
    fig,ax=plt.subplots(figsize=(11.0,5.3))
    ax.plot(xx,np.abs(raw-truth),color=BLUE,lw=1,label="raw Fourier")
    ax.plot(xx,np.abs(fej-truth),color=TEAL,lw=1,label="Fejer")
    ax.plot(xx,np.abs(res-truth),color=MAGENTA,lw=1,label="resolved")
    ax.set_yscale("log")
    ax.set_xlabel("periodic coordinate");ax.set_ylabel("absolute error")
    ax.set_title("Persistent oscillatory edge error is replaced by parameter and smooth-tail error",weight="bold")
    ax.legend();ax.grid(alpha=.18)
    save_figure(fig,out,"19_reconstruction_errors")

    # 20 metric bars
    labels=["raw RMSE","Fejer RMSE","resolved RMSE","edge L1","smooth RMSE"]
    vals=[reconstruction["raw_rmse"],reconstruction["fejer_rmse"],reconstruction["resolved_rmse"],reconstruction["edge_l1"],reconstruction["smooth_rmse"]]
    fig,ax=plt.subplots(figsize=(10.2,5.4))
    ax.bar(np.arange(len(vals)),vals,color=[BLUE,TEAL,MAGENTA,ORANGE,GREEN],edgecolor=INK)
    ax.set_yscale("log");ax.set_xticks(np.arange(len(vals)),labels,rotation=18,ha="right")
    ax.set_ylabel("error");ax.set_title("End-to-end reconstruction metrics",weight="bold");ax.grid(alpha=.18,axis="y")
    save_figure(fig,out,"20_metric_summary")

    # 21 negative principal branch
    u=edge.nodes**10
    principal=np.exp(1j*np.angle(u)/10)
    fig,ax=plt.subplots(figsize=(7.2,7.2))
    ax.plot(np.cos(theta),np.sin(theta),color=GRID)
    ax.scatter(edge.nodes.real,edge.nodes.imag,s=90,c=PALETTE[:edge.order],edgecolor=INK,label="true nodes")
    ax.scatter(principal.real,principal.imag,s=85,marker="x",color=RED,linewidth=2,label="principal roots")
    ax.set_aspect("equal");ax.set_xlim(-1.15,1.15);ax.set_ylim(-1.15,1.15)
    ax.set_title("Taking principal roots is not a valid de-aliasing rule",weight="bold")
    ax.legend();ax.grid(alpha=.12)
    save_figure(fig,out,"21_principal_root_failure")

    # 22 branch margin theorem picture
    fig,ax=diagram_axes((12.0,5.5))
    ax.text(.5,.91,"Branch selection is certified by a geometric margin",ha="center",fontsize=21,weight="bold")
    draw_box(ax,(.08,.45),.20,.20,r"aliased estimate\n$\widehat u\approx z^N$",face=BLUE+"20",edge=BLUE,fontsize=14)
    draw_box(ax,(.40,.45),.20,.20,r"offset estimate\n$\widetilde z\approx z$",face=TEAL+"20",edge=TEAL,fontsize=14)
    draw_box(ax,(.72,.45),.20,.20,r"nearest candidate\n$\widehat z$",face=MAGENTA+"20",edge=MAGENTA,fontsize=14)
    draw_arrow(ax,(.28,.55),(.40,.55),text=r"form $N$ roots",text_offset=(0,.06))
    draw_arrow(ax,(.60,.55),(.72,.55),text="choose within margin",text_offset=(0,.06))
    ax.text(.5,.20,r"coarse phase error + root perturbation $<\sin(\pi/N)$",ha="center",fontsize=15)
    save_figure(fig,out,"22_branch_margin")

    # 23 theorem map
    fig,ax=diagram_axes((13.0,6.0))
    ax.text(.5,.94,"The proof is modular",ha="center",fontsize=22,weight="bold")
    boxes=[
        (.04,.64,.20,.17,"Hankel gap\nrecovers $L$",BLUE),
        (.30,.64,.20,.17,"decimated Prony\nrecovers $u=z^N$",TEAL),
        (.56,.64,.20,.17,"offset phase fit\nrecovers coarse $z$",ORANGE),
        (.82,.64,.14,.17,"branch lift",MAGENTA),
        (.19,.28,.22,.17,"rate transfer\nadds one power of $N$",PURPLE),
        (.50,.28,.22,.17,"edge-native synthesis\nremoves Gibbs ringing",RED),
    ]
    for x0,y0,w,h,label,color in boxes: draw_box(ax,(x0,y0),w,h,label,face=color+"20",edge=color,fontsize=12.5)
    draw_arrow(ax,(.24,.725),(.30,.725));draw_arrow(ax,(.50,.725),(.56,.725));draw_arrow(ax,(.76,.725),(.82,.725))
    draw_arrow(ax,(.66,.64),(.41,.45),connectionstyle="arc3,rad=.12")
    draw_arrow(ax,(.89,.64),(.61,.45),connectionstyle="arc3,rad=-.12")
    ax.text(.5,.10,"Known exponential-analysis tools are used as inputs. The new theorem-facing object is their rate-preserving integration with piecewise-smooth Fourier reconstruction.",ha="center",fontsize=10.8,color=MUTED)
    save_figure(fig,out,"23_theorem_map")

    # 24 literature comparison
    labels=["Gegenbauer","Eckhoff/Batenkov","FRI/Prony","VEXPA","this synthesis"]
    properties=["unknown L","no external localization","non-bandlimited smooth tail","branch certificate","native edge synthesis"]
    matrix=np.asarray([
        [0,0,1,0,1],
        [0,0,1,0,1],
        [0,1,0,0,1],
        [1,1,0,1,0],
        [1,1,1,1,1],
    ],dtype=float)
    fig,ax=plt.subplots(figsize=(10.8,5.8))
    image=ax.imshow(matrix,aspect="auto",cmap=matplotlib.colors.ListedColormap(["#EEF1F2",TEAL]),vmin=0,vmax=1)
    ax.set_xticks(np.arange(len(properties)),properties,rotation=22,ha="right")
    ax.set_yticks(np.arange(len(labels)),labels)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]): ax.text(j,i,"yes" if matrix[i,j] else "-",ha="center",va="center",color=WHITE if matrix[i,j] else MUTED,weight="bold")
    ax.set_title("The contribution is a synthesis of capabilities, not a claim that every ingredient is new",weight="bold")
    fig.tight_layout()
    save_figure(fig,out,"24_literature_position")

    # 25 stability barrier diagram
    fig,ax=diagram_axes((12.0,5.6))
    ax.text(.5,.91,"Why the general Fourier stability barrier is not contradicted",ha="center",fontsize=20,weight="bold")
    draw_box(ax,(.07,.48),.34,.22,"arbitrary analytic or nonperiodic function\nfirst $m$ Fourier coefficients\nstable universal reconstruction",face=RED+"18",edge=RED,fontsize=13)
    draw_box(ax,(.59,.48),.34,.22,"finite-rate edge packet\nFourier-tail decay class\nnonlinear parametric recovery",face=TEAL+"18",edge=TEAL,fontsize=13)
    ax.text(.24,.28,"root-exponential stability barrier",ha="center",color=RED,weight="bold")
    ax.text(.76,.28,"algebraic rates under model assumptions",ha="center",color=TEAL,weight="bold")
    draw_arrow(ax,(.41,.59),(.59,.59),text="different problem class",text_offset=(0,.06))
    save_figure(fig,out,"25_stability_boundary")

    # 26 multi-decimation consensus
    fig,ax=plt.subplots(figsize=(8.0,7.0))
    ax.plot(np.cos(theta),np.sin(theta),color=GRID)
    for Nval,color in [(8,BLUE),(10,TEAL),(13,ORANGE)]:
        result=recover_polyphase(model,Nval,samples_per_offset=20,offsets=5,known_order=edge.order,refine=False)
        ax.scatter(result.nodes.real,result.nodes.imag,s=55,facecolors="none",edgecolors=color,label=f"N={Nval}")
    ax.scatter(edge.nodes.real,edge.nodes.imag,s=90,c=PALETTE[:edge.order],edgecolor=INK,marker="*",label="truth")
    ax.set_aspect("equal");ax.set_xlim(-1.15,1.15);ax.set_ylim(-1.15,1.15);ax.grid(alpha=.12)
    ax.set_title("Independent decimations provide a consensus check",weight="bold");ax.legend()
    save_figure(fig,out,"26_multiscale_consensus")

    # 27 residual heatmap across N/R
    Ns=[6,8,10,12,16]
    Rs=[2,3,4,5,6]
    heat=np.zeros((len(Rs),len(Ns)))
    for i,Rval in enumerate(Rs):
        for j,Nval in enumerate(Ns):
            rr=recover_polyphase(model,Nval,samples_per_offset=20,offsets=Rval,known_order=edge.order,refine=False)
            heat[i,j]=rr.validation_score
    fig,ax=plt.subplots(figsize=(9.5,5.7));im=ax.imshow(np.log10(np.maximum(heat,1e-18)),aspect="auto",cmap="viridis")
    ax.set_xticks(np.arange(len(Ns)),Ns);ax.set_yticks(np.arange(len(Rs)),Rs)
    ax.set_xlabel("decimation N");ax.set_ylabel("offset channels R")
    ax.set_title("Validation residual guides parameter choice",weight="bold")
    cbar=fig.colorbar(im,ax=ax,fraction=.046);cbar.set_label("log10 validation residual")
    save_figure(fig,out,"27_validation_heatmap")

    # 28 amplitude recovery
    fig,ax=plt.subplots(figsize=(9.5,5.2))
    positions=np.arange(edge.order);width=.35
    ax.bar(positions-width/2,edge.jumps,width,label="true",color=INK)
    ax.bar(positions+width/2,analytic_result.jumps,width,label="recovered",color=TEAL)
    ax.axhline(0,color=GRID,lw=.8);ax.set_xticks(positions,[f"edge {j+1}" for j in positions])
    ax.set_ylabel("jump amplitude");ax.set_title("Jump amplitudes are recovered after phase lifting",weight="bold")
    ax.legend();ax.grid(alpha=.15,axis="y")
    save_figure(fig,out,"28_amplitude_recovery")

    # 29 recovered smooth packet
    recovered_edge=edge_from_result(analytic_result)
    smooth_rec=np.zeros_like(x,dtype=complex)
    for n in range(-40,41): smooth_rec += (model.fourier(n)-recovered_edge.fourier(n))*np.exp(1j*n*x)
    fig,ax=plt.subplots(figsize=(11.5,5.2))
    ax.plot(x,model.background.values(x,2048),color=INK,lw=2,label="true smooth packet")
    ax.plot(x,np.real(smooth_rec),color=BLUE,lw=1.2,ls="--",label="recovered from residual Fourier data")
    ax.set_xlabel("periodic coordinate");ax.set_ylabel("amplitude")
    ax.set_title("After edge removal, the remaining Fourier data are smooth",weight="bold")
    ax.legend();ax.grid(alpha=.16)
    save_figure(fig,out,"29_smooth_packet_recovery")

    # 30 edge packet recovery
    fig,ax=plt.subplots(figsize=(11.5,5.2))
    ax.step(x,edge.values(x),where="post",color=INK,lw=2,label="true edge packet")
    ax.step(x,recovered_edge.values(x),where="post",color=ORANGE,lw=1.2,ls="--",label="recovered edge packet")
    ax.set_xlabel("periodic coordinate");ax.set_ylabel("amplitude")
    ax.set_title("The singular packet is reconstructed in its native coordinate",weight="bold")
    ax.legend();ax.grid(alpha=.16)
    save_figure(fig,out,"30_edge_packet_recovery")

    # 31 runtime
    fig,ax=plt.subplots(figsize=(9.5,5.2))
    Q=np.asarray([row["samples_per_offset"] for row in runtime_rows])
    times=np.asarray([row["median_seconds"] for row in runtime_rows])
    ax.plot(Q,times*1000,marker="o",color=PURPLE,lw=2)
    ax.set_xlabel("samples per offset channel");ax.set_ylabel("median runtime (ms)")
    ax.set_title("The finite solver remains small compared with dense global reconstruction",weight="bold")
    ax.grid(alpha=.18)
    save_figure(fig,out,"31_runtime")

    # 32 algorithm pseudocode graph
    fig,ax=diagram_axes((12.5,6.2))
    ax.text(.5,.94,"Executable algorithm",ha="center",fontsize=22,weight="bold")
    steps=[
        (.06,.68,"1\nform $m_n$",BLUE),(.27,.68,"2\nsplit offsets",TEAL),(.48,.68,"3\nestimate rank",GREEN),(.69,.68,"4\nrecover $u_j$",ORANGE),
        (.17,.30,"5\nfit offset coefficients",MAGENTA),(.43,.30,"6\nphase lift",PURPLE),(.69,.30,"7\nrefine and synthesize",RED),
    ]
    for x0,y0,label,color in steps: draw_box(ax,(x0,y0),.17,.16,label,face=color+"20",edge=color,fontsize=12)
    for a,b in [((.23,.76),(.27,.76)),((.44,.76),(.48,.76)),((.65,.76),(.69,.76)),((.78,.68),(.72,.46)),((.69,.38),(.60,.38)),((.43,.38),(.34,.38))]: draw_arrow(ax,a,b)
    ax.text(.5,.10,"Every stage emits a residual or gap that can be checked before the next stage is trusted.",ha="center",fontsize=11.5,color=MUTED)
    save_figure(fig,out,"32_algorithm")

    # 33 certificate dashboard
    metrics={
        "order":float(analytic_result.order),
        "order gap":analytic_result.order_gap,
        "location error":reconstruction["location_error"],
        "jump error":reconstruction["jump_error"],
        "validation":analytic_result.validation_score,
        "resolved RMSE":reconstruction["resolved_rmse"],
    }
    fig,ax=plt.subplots(figsize=(11.0,5.8));ax.axis("off")
    ax.text(.5,.94,"Certificate dashboard",ha="center",fontsize=21,weight="bold",transform=ax.transAxes)
    y=.82
    for i,(name,value) in enumerate(metrics.items()):
        face=WHITE if i%2==0 else "#EEF1F2"
        ax.add_patch(FancyBboxPatch((.10,y-.042),.80,.065,boxstyle="round,pad=.005,rounding_size=.008",facecolor=face,edgecolor="none",transform=ax.transAxes))
        ax.text(.13,y,name,ha="left",va="center",fontsize=12,transform=ax.transAxes)
        ax.text(.87,y,f"{value:.6e}",ha="right",va="center",fontsize=12,family="monospace",transform=ax.transAxes,color=TEAL if value<1e-4 or name=="order" else ORANGE)
        y-=.105
    save_figure(fig,out,"33_certificate_dashboard")

    # 34 scope diagram
    fig,ax=diagram_axes((12.0,5.8))
    ax.text(.5,.92,"What is proved and what remains outside the theorem",ha="center",fontsize=20,weight="bold")
    draw_box(ax,(.06,.46),.40,.26,"proved in the declared class\nunknown finite jump count\nno external localization\nrate-preserving de-aliasing\nGibbs-free native synthesis",face=TEAL+"18",edge=TEAL,fontsize=13)
    draw_box(ax,(.54,.46),.40,.26,"not claimed\narbitrary edge geometry\nseparation-free stability\nunbounded jump count\nmodel-free exponential convergence",face=ORANGE+"18",edge=ORANGE,fontsize=13)
    ax.text(.5,.18,"The advance is a sharper theorem for a structured class, not a denial of the general impossibility results.",ha="center",fontsize=11.5,color=MUTED)
    save_figure(fig,out,"34_scope_boundary")

    # 35 final synthesis
    fig,ax=diagram_axes((13.0,6.0))
    ax.text(.5,.94,"The field-facing result",ha="center",fontsize=23,weight="bold")
    draw_box(ax,(.07,.58),.24,.20,"decimated algebraic recovery\noptimal conditioning",face=BLUE+"18",edge=BLUE,fontsize=13)
    draw_box(ax,(.38,.58),.24,.20,"offset polyphase lifting\ninternal de-aliasing",face=TEAL+"18",edge=TEAL,fontsize=13)
    draw_box(ax,(.69,.58),.24,.20,"projector synthesis\nno Gibbs edge ringing",face=MAGENTA+"18",edge=MAGENTA,fontsize=13)
    draw_arrow(ax,(.31,.68),(.38,.68));draw_arrow(ax,(.62,.68),(.69,.68))
    ax.text(.5,.33,"unknown jump count + no supplied jump neighborhoods + one-order rate lift + explicit certificates",ha="center",fontsize=15,weight="bold")
    ax.text(.5,.15,"The shifted-channel identity is established exponential-analysis machinery. The contribution is the theorem that carries it into self-calibrating piecewise-smooth Fourier reconstruction and preserves the localization rate.",ha="center",fontsize=10.8,color=MUTED,wrap=True)
    save_figure(fig,out,"35_final_synthesis")

    # 36 oracle equivalence
    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    group = [row for row in oracle_rows if int(row["p"]) == 2]
    Nvals = np.asarray([int(row["decimation"]) for row in group])
    principal = np.asarray([float(row["principal_error"]) for row in group])
    oracle = np.asarray([float(row["oracle_error"]) for row in group])
    self_error = np.asarray([float(row["self_calibrated_error"]) for row in group])
    ax.semilogy(Nvals, principal, marker="o", lw=2, color=RED, label="principal root")
    ax.semilogy(Nvals, oracle, marker="o", lw=2.6, color=INK, label="oracle branch")
    ax.semilogy(Nvals, self_error, marker="x", ms=8, lw=1.4, color=TEAL, label="self-calibrated branch")
    ax.set_xlabel("decimation scale N")
    ax.set_ylabel("maximum circular location error")
    ax.set_title("The offset phase recovers the same branch as the oracle", weight="bold")
    ax.grid(alpha=.18, which="both")
    ax.legend()
    save_figure(fig, out, "36_oracle_equivalence")

    # 37 oracle-self distance heatmap
    pvals = sorted({int(row["p"]) for row in oracle_rows})
    nvals = sorted({int(row["decimation"]) for row in oracle_rows})
    matrix = np.zeros((len(pvals), len(nvals)))
    for row in oracle_rows:
        i = pvals.index(int(row["p"]))
        j = nvals.index(int(row["decimation"]))
        matrix[i, j] = max(float(row["oracle_self_node_distance"]), 1e-18)
    fig, ax = plt.subplots(figsize=(11.0, 4.8))
    image = ax.imshow(np.log10(matrix), aspect="auto", cmap="magma", vmin=-18, vmax=-8)
    ax.set_xticks(np.arange(len(nvals)), nvals)
    ax.set_yticks(np.arange(len(pvals)), [f"p={p}" for p in pvals])
    ax.set_xlabel("decimation scale N")
    ax.set_title("Oracle and self-calibrated node sets agree to numerical precision", weight="bold")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i,j]:.1e}", ha="center", va="center", fontsize=8.5, color=WHITE if np.log10(matrix[i,j]) < -12 else INK)
    fig.colorbar(image, ax=ax, fraction=.035, pad=.025, label="log10 node-set distance")
    fig.tight_layout()
    save_figure(fig, out, "37_oracle_distance")

    # 38 random stress error distribution
    finite_errors = np.asarray([float(row["location_error"]) for row in stress_rows if math.isfinite(float(row["location_error"]))])
    fig, ax = plt.subplots(figsize=(10.0, 5.5))
    ax.hist(np.log10(np.maximum(finite_errors, 1e-18)), bins=24, color=TEAL, edgecolor=INK, alpha=.88)
    ax.axvline(-3, color=RED, ls="--", lw=1.5, label="10^-3 success threshold")
    ax.set_xlabel("log10 maximum circular location error")
    ax.set_ylabel("number of cases")
    ax.set_title("One hundred separated random signals with unknown jump count", weight="bold")
    ax.legend()
    ax.grid(alpha=.15, axis="y")
    save_figure(fig, out, "38_random_stress_errors")

    # 39 random order confusion matrix
    orders = [2, 3, 4, 5]
    confusion = np.zeros((len(orders), len(orders)), dtype=int)
    for row in stress_rows:
        t = int(row["true_order"])
        r = int(row["recovered_order"])
        if t in orders and r in orders:
            confusion[orders.index(t), orders.index(r)] += 1
    fig, ax = plt.subplots(figsize=(7.2, 6.1))
    image = ax.imshow(confusion, cmap="viridis")
    ax.set_xticks(np.arange(len(orders)), orders)
    ax.set_yticks(np.arange(len(orders)), orders)
    ax.set_xlabel("recovered jump count")
    ax.set_ylabel("true jump count")
    ax.set_title("Unknown-order recovery across the random stress family", weight="bold")
    for i in range(len(orders)):
        for j in range(len(orders)):
            value = confusion[i, j]
            color = WHITE if value > max(1, confusion.max() / 2) else INK
            ax.text(j, i, str(value), ha="center", va="center", fontsize=13, weight="bold", color=color)
    fig.colorbar(image, ax=ax, fraction=.045, pad=.035, label="cases")
    fig.tight_layout()
    save_figure(fig, out, "39_random_order_confusion")



    # 40 explicit finite sample budget
    base_indices = np.asarray(finite_budget["base_indices"], dtype=int)
    offset_indices = np.asarray(finite_budget["offset_indices"], dtype=int)
    fig, ax = plt.subplots(figsize=(12.0, 4.8))
    ax.scatter(base_indices, np.zeros_like(base_indices), s=70, color=BLUE, label=r"base channel $r=0$")
    ax.scatter(offset_indices, np.ones_like(offset_indices), s=70, color=ORANGE, label=r"adjacent channel $r=1$")
    for n in base_indices:
        ax.vlines(n, -0.08, 0.08, color=BLUE, alpha=0.45)
    for n in offset_indices:
        ax.vlines(n, 0.92, 1.08, color=ORANGE, alpha=0.45)
    ax.set_yticks([0, 1], [r"$2L_{\max}+1$ moments", r"$L_{\max}$ moments"])
    ax.set_xlabel("Fourier derivative-moment index")
    ax.set_title(
        "Exact self-calibration uses an explicit high-frequency budget of "
        + str(finite_budget["high_frequency_sample_count"])
        + " coefficients",
        weight="bold",
    )
    ax.grid(alpha=0.16, axis="x")
    ax.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, -0.16))
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    save_figure(fig, out, "40_finite_sample_budget")

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
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run_all(base: Path) -> dict[str, object]:
    base.mkdir(parents=True, exist_ok=True)
    (base / "results").mkdir(exist_ok=True)
    (base / "tables").mkdir(exist_ok=True)

    edge = exact_edge()
    exact_model = SignalModel(bandlimited_background(), edge)
    analytic_model = SignalModel(analytic_background(), edge)

    exact = reorder_result(
        recover_polyphase(exact_model, 10, samples_per_offset=22, offsets=6, order_upper_bound=7, refine=True),
        edge,
    )
    analytic = reorder_result(
        recover_polyphase(analytic_model, 10, samples_per_offset=22, offsets=6, order_upper_bound=7, refine=True),
        edge,
    )
    symbolic = symbolic_confluent_check()
    rate_rows = run_rate_experiment(edge)
    noise_rows = run_noise_experiment(edge)
    offset_rows = run_offset_averaging_experiment(edge)
    collision_rows = run_collision_experiment()
    runtime_rows = run_runtime_experiment(edge)
    oracle_rows = run_oracle_equivalence_experiment(edge)
    stress_rows = run_random_stress_experiment(100)
    finite_budget = run_finite_budget_experiment(edge)
    reconstruction = run_reconstruction_experiment(edge)

    tests = run_tests(edge, exact, analytic, symbolic, rate_rows, noise_rows, offset_rows, oracle_rows, stress_rows, finite_budget, reconstruction)
    failed = [row for row in tests if not row["passed"]]
    if failed:
        raise AssertionError(f"failed tests: {failed}")

    generate_figures(
        base,
        edge,
        exact,
        analytic,
        rate_rows,
        noise_rows,
        offset_rows,
        collision_rows,
        runtime_rows,
        oracle_rows,
        stress_rows,
        finite_budget,
        reconstruction,
    )

    write_csv(base / "tables" / "rate_experiment.csv", rate_rows)
    write_csv(base / "tables" / "noise_experiment.csv", noise_rows)
    write_csv(base / "tables" / "offset_averaging.csv", offset_rows)
    write_csv(base / "tables" / "collision_experiment.csv", collision_rows)
    write_csv(base / "tables" / "runtime.csv", runtime_rows)
    write_csv(base / "tables" / "oracle_equivalence.csv", oracle_rows)
    write_csv(base / "tables" / "random_stress.csv", stress_rows)
    write_csv(base / "tables" / "finite_budget.csv", [finite_budget])
    write_csv(base / "tables" / "tests.csv", tests)

    result = {
        "title": "Self-Calibrating Polyphase Fourier Reconstruction",
        "jump_count": edge.order,
        "true_locations": edge.locations.tolist(),
        "true_jumps": edge.jumps.tolist(),
        "exact_recovered_locations": exact.locations.tolist(),
        "exact_recovered_jumps": exact.jumps.tolist(),
        "analytic_recovered_locations": analytic.locations.tolist(),
        "analytic_recovered_jumps": analytic.jumps.tolist(),
        "analytic_order_gap": analytic.order_gap,
        "analytic_validation_score": analytic.validation_score,
        "symbolic_confluent_check": symbolic,
        "reconstruction": reconstruction,
        "oracle_equivalence_max_node_distance": max(float(row["oracle_self_node_distance"]) for row in oracle_rows),
        "random_stress_order_success": float(np.mean([int(row["true_order"]) == int(row["recovered_order"]) for row in stress_rows])),
        "random_stress_location_success": float(np.mean([float(row["location_error"]) < 1e-3 for row in stress_rows])),
        "random_stress_median_location_error": float(np.median([float(row["location_error"]) for row in stress_rows])),
        "random_stress_maximum_location_error": float(np.max([float(row["location_error"]) for row in stress_rows])),
        "finite_budget": finite_budget,
        "test_count": len(tests),
        "tests_passed": len(tests),
        "figure_pairs": 40,
    }
    (base / "results" / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


# ============================================================================
# Complex signal and image benchmark extension
# ============================================================================

from scipy.fft import dctn, idctn
from scipy.ndimage import binary_dilation, gaussian_filter
from skimage import data as skdata
from skimage.feature import canny
from skimage.metrics import structural_similarity
from skimage.restoration import denoise_tv_chambolle
from skimage.transform import resize
from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class MethodMetrics:
    rmse: float
    max_error: float
    psnr: float
    ssim: float
    boundary_rmse: float
    edge_iou: float
    ringing_score: float


def rmse(a: RealArray, b: RealArray) -> float:
    return float(np.sqrt(np.mean((np.asarray(a, dtype=float) - np.asarray(b, dtype=float)) ** 2)))


def max_error(a: RealArray, b: RealArray) -> float:
    return float(np.max(np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))))


def psnr(a: RealArray, b: RealArray, data_range: float | None = None) -> float:
    truth = np.asarray(a, dtype=float)
    estimate = np.asarray(b, dtype=float)
    if data_range is None:
        data_range = float(np.max(truth) - np.min(truth))
    data_range = max(float(data_range), 1e-12)
    err = rmse(truth, estimate)
    if err == 0.0:
        return math.inf
    return float(20.0 * np.log10(data_range / err))


def periodic_fourier_coefficients(values: RealArray) -> ComplexArray:
    arr = np.asarray(values, dtype=float)
    return np.asarray(np.fft.fft(arr) / arr.size, dtype=complex)


def numerical_background_from_samples(values: RealArray, label: str) -> Background:
    coeff = periodic_fourier_coefficients(values)
    ngrid = coeff.size

    def get(n: int) -> complex:
        return complex(coeff[n % ngrid])

    return Background(get, label, decay_order=None)


def make_complex_background(kind: str, grid_size: int = 16384) -> Background:
    x = np.linspace(0.0, TAU, grid_size, endpoint=False)
    if kind == "chirp":
        values = 0.32 * np.sin(3.0 * x + 1.8 * np.sin(x)) + 0.18 * np.cos(11.0 * x)
    elif kind == "bursts":
        values = 0.24 * np.sin(4.0 * x)
        values += 0.55 * np.exp(-35.0 * (np.sin((x - 1.15) / 2.0) ** 2)) * np.cos(18.0 * x)
        values += 0.38 * np.exp(-45.0 * (np.sin((x - 4.65) / 2.0) ** 2)) * np.sin(24.0 * x)
    elif kind == "rough":
        values = np.zeros_like(x)
        for k in range(1, 100):
            values += 0.14 * np.cos(k * x + 0.37 * k) / (k + 1.0) ** 1.65
    else:
        raise ValueError(f"unknown complex background: {kind}")
    return numerical_background_from_samples(values, kind)


def make_edge_from_segments(locations: Sequence[float], levels: Sequence[float]) -> EdgePacket:
    tau = np.mod(np.asarray(locations, dtype=float), TAU)
    order = np.argsort(tau)
    tau = tau[order]
    lev = np.asarray(levels, dtype=float)
    if lev.size != tau.size:
        raise ValueError("levels must have one value per interval")
    lev = lev[order]
    jumps = np.roll(lev, -1) - lev
    return EdgePacket(tau, jumps)


def fixed_complex_edges(order: int) -> EdgePacket:
    if order == 4:
        tau = np.array([0.48, 1.72, 3.43, 5.31])
        jumps = np.array([0.8, -1.15, 0.55, -0.20])
    elif order == 6:
        tau = np.array([0.31, 1.08, 2.10, 3.18, 4.47, 5.74])
        jumps = np.array([0.65, -0.90, 0.52, -0.31, 0.70, -0.66])
    elif order == 8:
        tau = np.array([0.22, 0.91, 1.66, 2.44, 3.30, 4.08, 5.02, 5.78])
        jumps = np.array([0.52, -0.74, 0.63, -0.41, 0.58, -0.37, 0.49, -0.70])
    else:
        raise ValueError("supported fixed orders are 4, 6, and 8")
    return EdgePacket(tau, jumps)


def location_and_jump_errors(reference: EdgePacket, result: RecoveryResult) -> tuple[float, float]:
    if result.order != reference.order:
        return math.inf, math.inf
    rows, cols, loc_error = match_locations(reference.locations, result.locations)
    rec_jumps = result.jumps[rows]
    ref_jumps = reference.jumps[cols]
    return float(loc_error), float(np.max(np.abs(rec_jumps - ref_jumps)))


def reconstruct_background_from_edge(model: SignalModel, recovered: RecoveryResult, x: RealArray, order: int) -> RealArray:
    edge = edge_from_result(recovered)
    out = edge.values(x)
    for n in range(-order, order + 1):
        coeff = model.fourier(n) - edge.fourier(n)
        out += np.real(coeff * np.exp(1j * n * x))
    return out


def run_complex_1d_cases() -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    cases: list[tuple[str, Background, EdgePacket, int, int, int]] = [
        ("bandlimited_8_jump", bandlimited_background(), fixed_complex_edges(8), 11, 7, 80),
        ("analytic_6_jump", analytic_background(), fixed_complex_edges(6), 10, 7, 96),
        ("power_tail_6_jump", power_tail_background(3, 0.35, 0.19), fixed_complex_edges(6), 9, 7, 120),
        ("chirp_6_jump", make_complex_background("chirp"), fixed_complex_edges(6), 10, 7, 140),
        ("bursts_6_jump", make_complex_background("bursts"), fixed_complex_edges(6), 10, 7, 160),
        ("rough_4_jump", make_complex_background("rough"), fixed_complex_edges(4), 8, 7, 180),
    ]
    rows: list[dict[str, object]] = []
    details: dict[str, dict[str, object]] = {}
    x = np.linspace(0.0, TAU, 4096, endpoint=False)
    for name, background, edge, decimation, offsets, smooth_order in cases:
        model = SignalModel(background, edge)
        result = recover_polyphase(
            model,
            decimation=decimation,
            samples_per_offset=max(26, 4 * edge.order + 6),
            offsets=offsets,
            order_upper_bound=max(10, edge.order + 2),
            q0=2,
            known_order=None,
            refine=True,
        )
        loc_err, jump_err = location_and_jump_errors(edge, result)
        truth = model.values(x, smooth_order=1024)
        raw = fourier_partial(model, x, smooth_order)
        fejer = fejer_sum(model, x, smooth_order)
        resolved = reconstruct_background_from_edge(model, result, x, smooth_order)
        edge_true = edge.values(x)
        boundary = np.zeros_like(x, dtype=bool)
        for tau in edge.locations:
            boundary |= np.abs(np.angle(np.exp(1j * (x - tau)))) < 0.06
        row = {
            "case": name,
            "scope": "controlled" if name in {"bandlimited_8_jump", "analytic_6_jump", "power_tail_6_jump"} else "stress",
            "true_order": edge.order,
            "recovered_order": result.order,
            "minimum_separation": edge.separation,
            "location_error": loc_err,
            "jump_error": jump_err,
            "raw_rmse": rmse(truth, raw),
            "fejer_rmse": rmse(truth, fejer),
            "resolved_rmse": rmse(truth, resolved),
            "raw_boundary_rmse": rmse(truth[boundary], raw[boundary]),
            "resolved_boundary_rmse": rmse(truth[boundary], resolved[boundary]),
            "order_gap": result.order_gap,
            "phase_residual": result.validation_score,
        }
        rows.append(row)
        details[name] = {
            "model": model,
            "result": result,
            "x": x,
            "truth": truth,
            "raw": raw,
            "fejer": fejer,
            "resolved": resolved,
            "edge_true": edge_true,
            "boundary": boundary,
        }
    return rows, details


def run_1d_noise_sweep() -> list[dict[str, float | int]]:
    edge = fixed_complex_edges(6)
    base_model = SignalModel(analytic_background(), edge)
    sigmas = np.array([0.0, 1e-5, 1e-4, 1e-3, 1e-2, 3e-2, 5e-2, 1e-1, 2e-1])
    rows: list[dict[str, float | int]] = []
    for sigma in sigmas:
        locs: list[float] = []
        jumps: list[float] = []
        success = 0
        orders = 0
        for seed in range(12):
            model = add_moment_noise(base_model, float(sigma), seed + 310)
            result = recover_polyphase(
                model,
                decimation=10,
                samples_per_offset=30,
                offsets=7,
                order_upper_bound=9,
                q0=2,
                known_order=edge.order,
                refine=True,
            )
            loc_err, jump_err = location_and_jump_errors(edge, result)
            orders += int(result.order == edge.order)
            success += int(loc_err < 1e-3 and jump_err < 5e-3)
            locs.append(loc_err)
            jumps.append(jump_err)
        rows.append(
            {
                "sigma": float(sigma),
                "order_accuracy": orders / 12.0,
                "success_rate": success / 12.0,
                "median_location_error": float(np.median(locs)),
                "maximum_location_error": float(np.max(locs)),
                "median_jump_error": float(np.median(jumps)),
            }
        )
    return rows


def run_1d_separation_sweep() -> list[dict[str, float]]:
    deltas = np.geomspace(0.001, 0.9, 20)
    rows: list[dict[str, float]] = []
    background = analytic_background()
    sigma = 1e-3
    for delta in deltas:
        tau = np.array([0.55, 0.55 + delta, 2.55, 4.45])
        jumps = np.array([0.8, -0.8, 0.55, -0.55])
        edge = EdgePacket(tau, jumps)
        base_model = SignalModel(background, edge)
        loc_values: list[float] = []
        jump_values: list[float] = []
        phase_values: list[float] = []
        successes = 0
        for seed in range(8):
            model = add_moment_noise(base_model, sigma, 8100 + seed)
            try:
                result = recover_polyphase(
                    model,
                    decimation=9,
                    samples_per_offset=30,
                    offsets=7,
                    order_upper_bound=7,
                    q0=2,
                    known_order=4,
                    refine=True,
                )
                loc_err, jump_err = location_and_jump_errors(edge, result)
                successes += int(loc_err < 1e-3 and jump_err < 1e-2)
                phase_values.append(float(result.validation_score))
            except Exception:
                loc_err = math.inf
                jump_err = math.inf
                phase_values.append(math.inf)
            loc_values.append(float(loc_err))
            jump_values.append(float(jump_err))
        indices = np.arange(12, 12 + 24)
        V = np.exp(-1j * np.outer(indices, edge.locations))
        smallest = float(np.linalg.svd(V, compute_uv=False)[-1])
        rows.append(
            {
                "separation": float(delta),
                "noise_sigma": sigma,
                "location_error": float(np.median(loc_values)),
                "jump_error": float(np.median(jump_values)),
                "success": successes / 8.0,
                "smallest_vandermonde_singular": smallest,
                "phase_residual": float(np.median(phase_values)),
            }
        )
    return rows


def run_1d_order_sweep() -> list[dict[str, float | int]]:
    rng = np.random.default_rng(1729)
    rows: list[dict[str, float | int]] = []
    for order in range(2, 11):
        successes = 0
        loc_errors: list[float] = []
        time_values: list[float] = []
        for case in range(8):
            try:
                edge = random_edge_packet(
                    rng,
                    order,
                    decimation=13,
                    physical_separation=max(0.20, 4.6 / order * 0.22),
                    aliased_separation=0.16,
                )
            except RuntimeError:
                continue
            model = SignalModel(power_tail_background(4, 0.25, 0.17 + 0.03 * case), edge)
            start = time.perf_counter()
            result = recover_polyphase(
                model,
                decimation=13,
                samples_per_offset=max(30, 4 * order + 8),
                offsets=7,
                order_upper_bound=min(14, order + 3),
                q0=2,
                known_order=order,
                refine=True,
            )
            elapsed = time.perf_counter() - start
            loc_err, _ = location_and_jump_errors(edge, result)
            successes += int(loc_err < 1e-3)
            loc_errors.append(loc_err)
            time_values.append(elapsed)
        rows.append(
            {
                "order": order,
                "cases": len(loc_errors),
                "success_rate": successes / max(len(loc_errors), 1),
                "median_location_error": float(np.median(loc_errors)) if loc_errors else math.inf,
                "median_runtime_seconds": float(np.median(time_values)) if time_values else math.nan,
            }
        )
    return rows


def fourier_reconstruct_2d(image: RealArray, cutoff: int, method: str = "raw") -> RealArray:
    arr = np.asarray(image, dtype=float)
    h, w = arr.shape
    spec = np.fft.fftshift(np.fft.fft2(arr))
    yy, xx = np.mgrid[-h // 2 : h - h // 2, -w // 2 : w - w // 2]
    ax = np.abs(xx)
    ay = np.abs(yy)
    if method == "raw":
        weight = ((ax <= cutoff) & (ay <= cutoff)).astype(float)
    elif method == "fejer":
        wx = np.maximum(0.0, 1.0 - ax / (cutoff + 1.0))
        wy = np.maximum(0.0, 1.0 - ay / (cutoff + 1.0))
        weight = wx * wy
    elif method == "lanczos":
        inside = (ax <= cutoff) & (ay <= cutoff)
        weight = np.zeros_like(arr, dtype=float)
        weight[inside] = np.sinc(xx[inside] / (cutoff + 1.0)) * np.sinc(yy[inside] / (cutoff + 1.0))
    elif method == "exponential":
        radius = np.sqrt((xx / max(cutoff, 1)) ** 2 + (yy / max(cutoff, 1)) ** 2)
        weight = np.exp(-6.0 * radius**8)
    else:
        raise ValueError(f"unknown 2D Fourier method: {method}")
    return np.real(np.fft.ifft2(np.fft.ifftshift(spec * weight)))


def haar2d_forward(image: RealArray, levels: int = 3) -> tuple[RealArray, list[tuple[slice, slice, slice, slice]]]:
    coeff = np.asarray(image, dtype=float).copy()
    h, w = coeff.shape
    layout: list[tuple[slice, slice, slice, slice]] = []
    for _ in range(levels):
        if h % 2 or w % 2:
            raise ValueError("image dimensions must remain even")
        block = coeff[:h, :w]
        even_rows = (block[0::2, :] + block[1::2, :]) / math.sqrt(2.0)
        odd_rows = (block[0::2, :] - block[1::2, :]) / math.sqrt(2.0)
        ll = (even_rows[:, 0::2] + even_rows[:, 1::2]) / math.sqrt(2.0)
        lh = (even_rows[:, 0::2] - even_rows[:, 1::2]) / math.sqrt(2.0)
        hl = (odd_rows[:, 0::2] + odd_rows[:, 1::2]) / math.sqrt(2.0)
        hh = (odd_rows[:, 0::2] - odd_rows[:, 1::2]) / math.sqrt(2.0)
        h2, w2 = h // 2, w // 2
        coeff[:h2, :w2] = ll
        coeff[:h2, w2:w] = lh
        coeff[h2:h, :w2] = hl
        coeff[h2:h, w2:w] = hh
        layout.append((slice(0, h2), slice(0, w2), slice(h2, h), slice(w2, w)))
        h, w = h2, w2
    return coeff, layout


def haar2d_inverse(coefficients: RealArray, levels: int = 3) -> RealArray:
    coeff = np.asarray(coefficients, dtype=float).copy()
    h0, w0 = coeff.shape
    h = h0 // (2 ** (levels - 1))
    w = w0 // (2 ** (levels - 1))
    for _ in range(levels):
        h2, w2 = h // 2, w // 2
        ll = coeff[:h2, :w2].copy()
        lh = coeff[:h2, w2:w].copy()
        hl = coeff[h2:h, :w2].copy()
        hh = coeff[h2:h, w2:w].copy()
        even_left = (ll + lh) / math.sqrt(2.0)
        even_right = (ll - lh) / math.sqrt(2.0)
        odd_left = (hl + hh) / math.sqrt(2.0)
        odd_right = (hl - hh) / math.sqrt(2.0)
        even_rows = np.empty((h2, w), dtype=float)
        odd_rows = np.empty((h2, w), dtype=float)
        even_rows[:, 0::2] = even_left
        even_rows[:, 1::2] = even_right
        odd_rows[:, 0::2] = odd_left
        odd_rows[:, 1::2] = odd_right
        block = np.empty((h, w), dtype=float)
        block[0::2, :] = (even_rows + odd_rows) / math.sqrt(2.0)
        block[1::2, :] = (even_rows - odd_rows) / math.sqrt(2.0)
        coeff[:h, :w] = block
        h = min(h * 2, h0)
        w = min(w * 2, w0)
    return coeff


def haar_threshold_reconstruct(image: RealArray, keep_fraction: float = 0.12, levels: int = 3) -> RealArray:
    coeff, _ = haar2d_forward(image, levels=levels)
    flat = np.abs(coeff).ravel()
    keep = max(1, int(round(keep_fraction * flat.size)))
    threshold = np.partition(flat, -keep)[-keep]
    truncated = np.where(np.abs(coeff) >= threshold, coeff, 0.0)
    return haar2d_inverse(truncated, levels=levels)


def dct_lowpass(image: RealArray, order: int) -> RealArray:
    coeff = dctn(np.asarray(image, dtype=float), type=2, norm="ortho")
    kept = np.zeros_like(coeff)
    kept[:order, :order] = coeff[:order, :order]
    return idctn(kept, type=2, norm="ortho")


def smooth_background_2d(shape: tuple[int, int], seed: int = 0, order: int = 7) -> RealArray:
    rng = np.random.default_rng(seed)
    h, w = shape
    coeff = np.zeros(shape, dtype=float)
    coeff[:order, :order] = rng.normal(scale=1.0, size=(order, order))
    coeff[0, 0] = 0.0
    bg = idctn(coeff, type=2, norm="ortho")
    bg /= max(np.max(np.abs(bg)), 1e-12)
    return 0.30 * bg + 0.45


def rectangle_mask(shape: tuple[int, int], center: tuple[int, int], size: tuple[int, int]) -> RealArray:
    h, w = shape
    cy, cx = center
    sy, sx = size
    y0 = max(0, cy - sy // 2)
    y1 = min(h, y0 + sy)
    x0 = max(0, cx - sx // 2)
    x1 = min(w, x0 + sx)
    mask = np.zeros(shape, dtype=float)
    mask[y0:y1, x0:x1] = 1.0
    return mask


def disk_mask(shape: tuple[int, int], center: tuple[int, int], radius: int) -> RealArray:
    yy, xx = np.mgrid[: shape[0], : shape[1]]
    cy, cx = center
    return (((yy - cy) ** 2 + (xx - cx) ** 2) <= radius**2).astype(float)


def ellipse_mask(shape: tuple[int, int], center: tuple[int, int], radii: tuple[int, int]) -> RealArray:
    yy, xx = np.mgrid[: shape[0], : shape[1]]
    cy, cx = center
    ry, rx = radii
    return ((((yy - cy) / max(ry, 1)) ** 2 + ((xx - cx) / max(rx, 1)) ** 2) <= 1.0).astype(float)


def bar_mask(shape: tuple[int, int], center: tuple[int, int], length: int, thickness: int, orientation: str) -> RealArray:
    if orientation == "horizontal":
        return rectangle_mask(shape, center, (thickness, length))
    if orientation == "vertical":
        return rectangle_mask(shape, center, (length, thickness))
    raise ValueError("orientation must be horizontal or vertical")


def star_mask(shape: tuple[int, int], center: tuple[float, float], r_outer: float, r_inner: float, points: int = 5) -> RealArray:
    h, w = shape
    cy, cx = center
    angles = np.linspace(-math.pi / 2.0, 3.0 * math.pi / 2.0, 2 * points, endpoint=False)
    radii = np.where(np.arange(2 * points) % 2 == 0, r_outer, r_inner)
    vertices = [(cx + r * math.cos(a), cy + r * math.sin(a)) for r, a in zip(radii, angles, strict=True)]
    image = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(image)
    draw.polygon(vertices, fill=255)
    return np.asarray(image, dtype=float) / 255.0


def text_mask(shape: tuple[int, int], text: str = "KOMOREBI") -> RealArray:
    h, w = shape
    image = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=max(12, h // 6))
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, (h - th) / 2), text, font=font, fill=255)
    return np.asarray(image, dtype=float) / 255.0


@dataclass
class GeometryDictionary:
    atoms: RealArray
    names: list[str]
    masks: list[RealArray]
    residual_atoms: RealArray
    norms: RealArray
    normalized: RealArray
    gram: RealArray


def build_geometry_dictionary(shape: tuple[int, int] = (96, 96), smooth_order: int = 6) -> GeometryDictionary:
    masks: list[RealArray] = []
    names: list[str] = []
    centers = [16, 32, 48, 64, 80]
    for cy in centers:
        for cx in centers:
            for size in [(16, 24), (24, 16), (24, 24), (32, 24), (24, 32)]:
                masks.append(rectangle_mask(shape, (cy, cx), size))
                names.append(f"rect_c{cy}_{cx}_s{size[0]}_{size[1]}")
            for radius in [8, 12, 16]:
                masks.append(disk_mask(shape, (cy, cx), radius))
                names.append(f"disk_c{cy}_{cx}_r{radius}")
            for radii in [(8, 16), (16, 8), (12, 18), (18, 12)]:
                masks.append(ellipse_mask(shape, (cy, cx), radii))
                names.append(f"ellipse_c{cy}_{cx}_r{radii[0]}_{radii[1]}")
    for cy in [24, 48, 72]:
        for cx in [24, 48, 72]:
            for orientation in ["horizontal", "vertical"]:
                masks.append(bar_mask(shape, (cy, cx), 56, 5, orientation))
                names.append(f"bar_{orientation}_c{cy}_{cx}")
    atoms = np.column_stack([mask.ravel() for mask in masks])
    residual_list = [(mask - dct_lowpass(mask, smooth_order)).ravel() for mask in masks]
    residual_atoms = np.column_stack(residual_list)
    norms = np.linalg.norm(residual_atoms, axis=0)
    keep = norms > 1e-8
    atoms = atoms[:, keep]
    residual_atoms = residual_atoms[:, keep]
    norms = norms[keep]
    names = [name for name, flag in zip(names, keep, strict=True) if flag]
    masks = [mask for mask, flag in zip(masks, keep, strict=True) if flag]
    normalized = residual_atoms / norms
    gram = normalized.T @ normalized
    return GeometryDictionary(atoms, names, masks, residual_atoms, norms, normalized, gram)


def omp_unknown_order(
    dictionary: GeometryDictionary,
    observed: RealArray,
    smooth_order: int,
    max_atoms: int = 8,
    noise_sigma: float = 0.0,
    improvement_tolerance: float = 0.08,
) -> tuple[list[int], RealArray, RealArray, list[dict[str, float | int]]]:
    y = np.asarray(observed, dtype=float)
    residual_image = y - dct_lowpass(y, smooth_order)
    b = dictionary.normalized.T @ residual_image.ravel()
    selected: list[int] = []
    history: list[dict[str, float | int]] = []
    best_score = math.inf
    best_selected: list[int] = []
    best_beta = np.zeros(0)
    n = y.size
    previous_sse: float | None = None
    previous_selected: list[int] = []
    previous_beta = np.zeros(0)
    for k in range(1, max_atoms + 1):
        active_beta = previous_beta if selected else np.zeros(0)
        corr = b - dictionary.gram[:, selected] @ active_beta if selected else b.copy()
        corr[selected] = 0.0
        new = int(np.argmax(np.abs(corr)))
        if new in selected:
            break
        selected.append(new)
        Gs = dictionary.gram[np.ix_(selected, selected)]
        bs = b[selected]
        beta, *_ = np.linalg.lstsq(Gs, bs, rcond=None)
        fit = dictionary.normalized[:, selected] @ beta
        residual = residual_image.ravel() - fit
        sse = float(np.dot(residual, residual))
        penalty = k * math.log(max(n, 2))
        scale = max(noise_sigma**2, 1e-14)
        bic = n * math.log(sse / n + scale) + penalty
        relative_improvement = math.inf if previous_sse is None else (previous_sse - sse) / max(previous_sse, 1e-30)
        history.append({"atoms": k, "sse": sse, "bic": bic, "relative_improvement": relative_improvement})
        if previous_sse is not None and relative_improvement < improvement_tolerance:
            best_selected = previous_selected.copy()
            best_beta = previous_beta.copy()
            break
        if bic < best_score:
            best_score = bic
            best_selected = selected.copy()
            best_beta = beta.copy()
        previous_sse = sse
        previous_selected = selected.copy()
        previous_beta = beta.copy()
    alpha = np.zeros(dictionary.atoms.shape[1], dtype=float)
    if best_selected:
        alpha[np.asarray(best_selected, dtype=int)] = best_beta / dictionary.norms[np.asarray(best_selected, dtype=int)]
    edge = (dictionary.atoms @ alpha).reshape(y.shape)
    smooth = dct_lowpass(y - edge, smooth_order)
    reconstruction = smooth + edge
    return best_selected, alpha, reconstruction, history


def boundary_mask_from_image(image: RealArray, threshold: float = 0.08, dilation: int = 2) -> NDArray[np.bool_]:
    arr = np.asarray(image, dtype=float)
    gx = np.zeros_like(arr)
    gy = np.zeros_like(arr)
    gx[:, 1:] = np.abs(np.diff(arr, axis=1))
    gy[1:, :] = np.abs(np.diff(arr, axis=0))
    mask = (gx + gy) > threshold
    if dilation > 0:
        mask = binary_dilation(mask, iterations=dilation)
    return np.asarray(mask, dtype=bool)


def edge_iou_score(truth: RealArray, estimate: RealArray) -> float:
    tr = canny(np.asarray(truth, dtype=float), sigma=1.0)
    es = canny(np.asarray(estimate, dtype=float), sigma=1.0)
    tr = binary_dilation(tr, iterations=1)
    es = binary_dilation(es, iterations=1)
    union = np.logical_or(tr, es)
    if not np.any(union):
        return 1.0
    return float(np.sum(np.logical_and(tr, es)) / np.sum(union))


def ringing_score_2d(truth: RealArray, estimate: RealArray, boundary: NDArray[np.bool_]) -> float:
    t = np.asarray(truth, dtype=float)
    e = np.asarray(estimate, dtype=float)
    if not np.any(boundary):
        return 0.0
    local_min = gaussian_filter(t, 1.5) - 0.25
    local_max = gaussian_filter(t, 1.5) + 0.25
    over = np.maximum(e - local_max, 0.0)
    under = np.maximum(local_min - e, 0.0)
    return float(np.max((over + under)[boundary]))


def compute_image_metrics(truth: RealArray, estimate: RealArray, boundary: NDArray[np.bool_]) -> MethodMetrics:
    data_range = float(np.max(truth) - np.min(truth))
    return MethodMetrics(
        rmse=rmse(truth, estimate),
        max_error=max_error(truth, estimate),
        psnr=psnr(truth, estimate, data_range=data_range),
        ssim=float(structural_similarity(truth, estimate, data_range=max(data_range, 1e-12))),
        boundary_rmse=rmse(truth[boundary], estimate[boundary]) if np.any(boundary) else 0.0,
        edge_iou=edge_iou_score(truth, estimate),
        ringing_score=ringing_score_2d(truth, estimate, boundary),
    )


def make_2d_exact_cases(dictionary: GeometryDictionary, shape: tuple[int, int] = (96, 96)) -> dict[str, dict[str, object]]:
    name_to_index = {name: i for i, name in enumerate(dictionary.names)}
    specs = {
        "multi_geometry": [
            ("rect_c32_32_s24_24", 0.85),
            ("disk_c64_64_r12", -0.65),
            ("ellipse_c32_64_r8_16", 0.55),
            ("bar_vertical_c72_24", 0.42),
        ],
        "curved_shapes": [
            ("disk_c32_32_r16", 0.75),
            ("ellipse_c64_32_r12_18", -0.52),
            ("ellipse_c48_80_r18_12", 0.61),
        ],
        "thin_structures": [
            ("bar_horizontal_c24_48", 0.55),
            ("bar_vertical_c48_72", -0.50),
            ("bar_horizontal_c72_24", 0.44),
            ("rect_c48_48_s16_24", 0.35),
        ],
    }
    cases: dict[str, dict[str, object]] = {}
    for seed, (case_name, atoms_spec) in enumerate(specs.items(), start=20):
        background = smooth_background_2d(shape, seed=seed, order=6)
        edge = np.zeros(shape, dtype=float)
        indices: list[int] = []
        amplitudes: list[float] = []
        for atom_name, amplitude in atoms_spec:
            idx = name_to_index[atom_name]
            edge += amplitude * dictionary.masks[idx]
            indices.append(idx)
            amplitudes.append(float(amplitude))
        truth = background + edge
        cases[case_name] = {
            "background": background,
            "edge": edge,
            "truth": truth,
            "support": indices,
            "amplitudes": amplitudes,
        }
    return cases


def benchmark_2d_case(
    case_name: str,
    truth: RealArray,
    dictionary: GeometryDictionary,
    smooth_order: int,
    cutoff: int,
    noise_sigma: float = 0.0,
    seed: int = 0,
) -> tuple[list[dict[str, object]], dict[str, RealArray], list[int], list[dict[str, float | int]]]:
    rng = np.random.default_rng(seed)
    observed_truth = np.asarray(truth, dtype=float)
    if noise_sigma > 0:
        observed_truth = observed_truth + rng.normal(scale=noise_sigma, size=observed_truth.shape)
    raw = fourier_reconstruct_2d(observed_truth, cutoff, "raw")
    fejer = fourier_reconstruct_2d(observed_truth, cutoff, "fejer")
    lanczos = fourier_reconstruct_2d(observed_truth, cutoff, "lanczos")
    wavelet = haar_threshold_reconstruct(raw, keep_fraction=0.18, levels=3)
    tv = denoise_tv_chambolle(raw, weight=0.07, channel_axis=None)
    selected, alpha, resolved, history = omp_unknown_order(
        dictionary,
        raw,
        smooth_order=smooth_order,
        max_atoms=8,
        noise_sigma=max(noise_sigma, 1e-6),
    )
    boundary = boundary_mask_from_image(truth, threshold=0.07, dilation=2)
    methods = {
        "raw_fourier": raw,
        "fejer": fejer,
        "lanczos": lanczos,
        "haar_threshold": wavelet,
        "tv": tv,
        "dictionary_resolved": resolved,
    }
    rows: list[dict[str, object]] = []
    for method_name, estimate in methods.items():
        metric = compute_image_metrics(truth, estimate, boundary)
        rows.append(
            {
                "case": case_name,
                "method": method_name,
                "rmse": metric.rmse,
                "max_error": metric.max_error,
                "psnr": metric.psnr,
                "ssim": metric.ssim,
                "boundary_rmse": metric.boundary_rmse,
                "edge_iou": metric.edge_iou,
                "ringing_score": metric.ringing_score,
                "selected_atoms": len(selected) if method_name == "dictionary_resolved" else 0,
            }
        )
    return rows, methods, selected, history


def run_2d_exact_benchmarks(dictionary: GeometryDictionary) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    cases = make_2d_exact_cases(dictionary)
    rows: list[dict[str, object]] = []
    details: dict[str, dict[str, object]] = {}
    for seed, (name, case) in enumerate(cases.items(), start=100):
        case_rows, methods, selected, history = benchmark_2d_case(
            name,
            np.asarray(case["truth"]),
            dictionary,
            smooth_order=6,
            cutoff=16,
            noise_sigma=0.0,
            seed=seed,
        )
        rows.extend(case_rows)
        details[name] = {**case, "methods": methods, "selected": selected, "history": history}
    return rows, details


def run_2d_noise_sweep(dictionary: GeometryDictionary) -> list[dict[str, float]]:
    case = make_2d_exact_cases(dictionary)["multi_geometry"]
    truth = np.asarray(case["truth"], dtype=float)
    sigmas = [0.0, 0.01, 0.04, 0.08, 0.16, 0.32, 0.40, 0.60, 0.80]
    rows: list[dict[str, float]] = []
    true_support = set(int(i) for i in case["support"])
    for sigma in sigmas:
        rmses: list[float] = []
        support_scores: list[float] = []
        counts: list[int] = []
        for seed in range(10):
            rng = np.random.default_rng(seed + 1000)
            noisy = truth + rng.normal(scale=sigma, size=truth.shape)
            raw = fourier_reconstruct_2d(noisy, 16, "raw")
            selected, _, resolved, _ = omp_unknown_order(
                dictionary,
                raw,
                smooth_order=6,
                max_atoms=8,
                noise_sigma=max(sigma, 1e-6),
            )
            selected_set = set(selected)
            intersection = len(true_support & selected_set)
            union = len(true_support | selected_set)
            support_scores.append(intersection / max(union, 1))
            counts.append(len(selected))
            rmses.append(rmse(truth, resolved))
        rows.append(
            {
                "sigma": float(sigma),
                "median_rmse": float(np.median(rmses)),
                "median_support_iou": float(np.median(support_scores)),
                "median_selected_count": float(np.median(counts)),
            }
        )
    return rows


def run_2d_random_stress(dictionary: GeometryDictionary, cases: int = 40) -> list[dict[str, float | int]]:
    rng = np.random.default_rng(9091)
    rows: list[dict[str, float | int]] = []
    shape = dictionary.masks[0].shape
    for case_id in range(cases):
        k = int(rng.integers(2, 6))
        support = rng.choice(len(dictionary.names), size=k, replace=False)
        amplitudes = rng.uniform(-0.9, 0.9, size=k)
        amplitudes[np.abs(amplitudes) < 0.25] += 0.35 * np.sign(amplitudes[np.abs(amplitudes) < 0.25] + 1e-12)
        background = smooth_background_2d(shape, seed=500 + case_id, order=6)
        edge = sum((float(a) * dictionary.masks[int(i)] for i, a in zip(support, amplitudes, strict=True)), np.zeros(shape))
        truth = background + edge
        raw = fourier_reconstruct_2d(truth, 16, "raw")
        selected, _, resolved, _ = omp_unknown_order(dictionary, raw, smooth_order=6, max_atoms=8, noise_sigma=1e-6)
        true_set = set(int(i) for i in support)
        selected_set = set(selected)
        intersection = len(true_set & selected_set)
        union = len(true_set | selected_set)
        rows.append(
            {
                "case": case_id,
                "true_count": k,
                "selected_count": len(selected),
                "support_iou": intersection / max(union, 1),
                "raw_rmse": rmse(truth, raw),
                "resolved_rmse": rmse(truth, resolved),
            }
        )
    return rows


def make_out_of_model_cases(shape: tuple[int, int] = (96, 96)) -> dict[str, RealArray]:
    background = smooth_background_2d(shape, seed=404, order=6)
    yy, xx = np.mgrid[: shape[0], : shape[1]]
    gradient = 0.18 * xx / shape[1] + 0.12 * yy / shape[0]
    star = background + 0.75 * star_mask(shape, (48.0, 48.0), 30.0, 13.0, points=7)
    text = background + gradient + 0.65 * text_mask(shape, "KOMOREBI")
    rings = background + 0.55 * (((xx - 48) ** 2 + (yy - 48) ** 2 <= 30**2).astype(float))
    rings -= 0.50 * (((xx - 48) ** 2 + (yy - 48) ** 2 <= 19**2).astype(float))
    return {"star_out_of_dictionary": star, "text_over_gradient": text, "nested_rings": rings}


def run_out_of_model_benchmarks(dictionary: GeometryDictionary) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    rows: list[dict[str, object]] = []
    details: dict[str, dict[str, object]] = {}
    for seed, (name, truth) in enumerate(make_out_of_model_cases().items(), start=600):
        case_rows, methods, selected, history = benchmark_2d_case(
            name,
            truth,
            dictionary,
            smooth_order=6,
            cutoff=16,
            noise_sigma=0.0,
            seed=seed,
        )
        rows.extend(case_rows)
        details[name] = {"truth": truth, "methods": methods, "selected": selected, "history": history}
    return rows, details


def natural_images() -> dict[str, RealArray]:
    images = {
        "camera": skdata.camera(),
        "coins": skdata.coins(),
        "moon": skdata.moon(),
        "page": skdata.page(),
    }
    out: dict[str, RealArray] = {}
    for name, image in images.items():
        arr = np.asarray(image, dtype=float)
        arr -= arr.min()
        arr /= max(arr.max(), 1e-12)
        out[name] = resize(arr, (128, 128), anti_aliasing=True, preserve_range=True).astype(float)
    return out


def run_natural_image_benchmarks() -> tuple[list[dict[str, object]], dict[str, dict[str, RealArray]]]:
    rows: list[dict[str, object]] = []
    details: dict[str, dict[str, RealArray]] = {}
    for name, truth in natural_images().items():
        boundary = boundary_mask_from_image(truth, threshold=0.05, dilation=2)
        methods = {
            "raw_fourier": fourier_reconstruct_2d(truth, 22, "raw"),
            "fejer": fourier_reconstruct_2d(truth, 22, "fejer"),
            "lanczos": fourier_reconstruct_2d(truth, 22, "lanczos"),
        }
        methods["haar_threshold"] = haar_threshold_reconstruct(methods["raw_fourier"], keep_fraction=0.22, levels=3)
        methods["tv"] = denoise_tv_chambolle(methods["raw_fourier"], weight=0.055, channel_axis=None)
        for method_name, estimate in methods.items():
            metric = compute_image_metrics(truth, estimate, boundary)
            rows.append(
                {
                    "case": name,
                    "method": method_name,
                    "rmse": metric.rmse,
                    "max_error": metric.max_error,
                    "psnr": metric.psnr,
                    "ssim": metric.ssim,
                    "boundary_rmse": metric.boundary_rmse,
                    "edge_iou": metric.edge_iou,
                    "ringing_score": metric.ringing_score,
                }
            )
        details[name] = {"truth": truth, **methods}
    return rows, details


def make_natural_hybrid_case(dictionary: GeometryDictionary) -> tuple[RealArray, list[int]]:
    shape = dictionary.masks[0].shape
    camera = resize(skdata.camera().astype(float) / 255.0, shape, anti_aliasing=True, preserve_range=True)
    smooth = gaussian_filter(camera, sigma=5.0)
    name_to_index = {name: i for i, name in enumerate(dictionary.names)}
    support_names = ["disk_c32_64_r12", "rect_c64_32_s24_24", "ellipse_c64_64_r8_16"]
    amplitudes = [0.55, -0.45, 0.38]
    support = [name_to_index[n] for n in support_names]
    edge = sum((a * dictionary.masks[i] for a, i in zip(amplitudes, support, strict=True)), np.zeros(shape))
    return smooth + edge, support


def run_natural_hybrid_benchmark(dictionary: GeometryDictionary) -> tuple[list[dict[str, object]], dict[str, object]]:
    truth, support = make_natural_hybrid_case(dictionary)
    rows, methods, selected, history = benchmark_2d_case(
        "natural_background_hybrid",
        truth,
        dictionary,
        smooth_order=10,
        cutoff=18,
        noise_sigma=0.0,
        seed=777,
    )
    return rows, {"truth": truth, "support": support, "methods": methods, "selected": selected, "history": history}


def plot_1d_case(detail: dict[str, object], title: str, out_dir: Path, name: str) -> None:
    x = np.asarray(detail["x"])
    fig, axes = plt.subplots(3, 1, figsize=(12.0, 8.0), sharex=True, gridspec_kw={"height_ratios": [1.4, 1.0, 1.0]})
    axes[0].plot(x, detail["truth"], color=INK, lw=2.0, label="truth")
    axes[0].plot(x, detail["raw"], color=BLUE, lw=1.0, label="raw Fourier")
    axes[0].plot(x, detail["resolved"], color=TEAL, lw=1.1, ls="--", label="resolved")
    axes[0].set_title(title, loc="left", weight="bold")
    axes[0].legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.17))
    axes[0].set_ylabel("signal")
    axes[1].plot(x, np.abs(np.asarray(detail["truth"]) - np.asarray(detail["raw"])), color=BLUE, lw=1.2, label="raw error")
    axes[1].plot(x, np.abs(np.asarray(detail["truth"]) - np.asarray(detail["fejer"])), color=ORANGE, lw=1.2, label="Fejer error")
    axes[1].plot(x, np.abs(np.asarray(detail["truth"]) - np.asarray(detail["resolved"])), color=TEAL, lw=1.2, label="resolved error")
    axes[1].legend(ncol=3)
    axes[1].set_ylabel("absolute error")
    edge = detail["model"].edge
    axes[2].stem(edge.locations, edge.jumps, linefmt=RED, markerfmt="o", basefmt=" ", label="true jumps")
    result = detail["result"]
    axes[2].stem(result.locations, result.jumps, linefmt=TEAL, markerfmt="x", basefmt=" ", label="recovered jumps")
    axes[2].legend(ncol=2)
    axes[2].set_xlabel("periodic coordinate")
    axes[2].set_ylabel("jump amplitude")
    for ax in axes:
        ax.grid(alpha=0.17)
        ax.set_xlim(0.0, TAU)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, out_dir, name)


def plot_sweep(rows: Sequence[dict[str, object]], x_key: str, y_keys: Sequence[str], labels: Sequence[str], title: str, out_dir: Path, name: str, logx: bool = False, logy: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(9.8, 5.7))
    x = np.asarray([float(row[x_key]) for row in rows])
    for index, (key, label) in enumerate(zip(y_keys, labels, strict=True)):
        y = np.asarray([float(row[key]) for row in rows])
        y = np.where(np.isfinite(y), y, np.nan)
        ax.plot(x, y, marker="o", lw=1.8, label=label, color=PALETTE[index % len(PALETTE)])
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(x_key.replace("_", " "))
    ax.set_ylabel("metric")
    ax.set_title(title, weight="bold")
    ax.grid(alpha=0.18, which="both")
    ax.legend(loc="best")
    fig.tight_layout()
    save_figure(fig, out_dir, name)


def plot_image_grid(truth: RealArray, methods: dict[str, RealArray], title: str, out_dir: Path, name: str) -> None:
    order = ["raw_fourier", "fejer", "lanczos", "haar_threshold", "tv", "dictionary_resolved"]
    existing = [method for method in order if method in methods]
    panels = [("truth", truth)] + [(method, methods[method]) for method in existing]
    cols = 4
    rows = int(math.ceil(len(panels) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(12.5, 3.2 * rows))
    axes_arr = np.atleast_1d(axes).ravel()
    vmin = float(min(np.min(panel) for _, panel in panels))
    vmax = float(max(np.max(panel) for _, panel in panels))
    for ax, (label, panel) in zip(axes_arr, panels, strict=False):
        image = ax.imshow(panel, cmap="gray", vmin=vmin, vmax=vmax)
        ax.set_title(label.replace("_", " "), fontsize=10.5, weight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
    for ax in axes_arr[len(panels) :]:
        ax.axis("off")
    fig.suptitle(title, fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, out_dir, name)


def plot_error_grid(truth: RealArray, methods: dict[str, RealArray], title: str, out_dir: Path, name: str) -> None:
    order = ["raw_fourier", "fejer", "lanczos", "haar_threshold", "tv", "dictionary_resolved"]
    existing = [method for method in order if method in methods]
    cols = 3
    rows = int(math.ceil(len(existing) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(12.0, 3.7 * rows))
    axes_arr = np.atleast_1d(axes).ravel()
    errors = [np.abs(truth - methods[m]) for m in existing]
    vmax = float(max(np.max(error) for error in errors))
    for ax, method, error in zip(axes_arr, existing, errors, strict=False):
        im = ax.imshow(error, cmap="magma", vmin=0.0, vmax=vmax)
        ax.set_title(method.replace("_", " "), fontsize=10.5, weight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046)
    for ax in axes_arr[len(existing) :]:
        ax.axis("off")
    fig.suptitle(title, fontsize=16, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_figure(fig, out_dir, name)


def plot_method_summary(rows: Sequence[dict[str, object]], metric: str, title: str, out_dir: Path, name: str) -> None:
    cases = sorted({str(row["case"]) for row in rows})
    methods = sorted({str(row["method"]) for row in rows})
    matrix = np.full((len(cases), len(methods)), np.nan)
    for row in rows:
        matrix[cases.index(str(row["case"])), methods.index(str(row["method"]))] = float(row[metric])
    fig, ax = plt.subplots(figsize=(max(9.0, 1.4 * len(methods)), max(4.2, 0.6 * len(cases))))
    im = ax.imshow(matrix, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(methods)), [m.replace("_", "\n") for m in methods])
    ax.set_yticks(range(len(cases)), [c.replace("_", " ") for c in cases])
    ax.set_title(title, weight="bold")
    for i in range(len(cases)):
        for j in range(len(methods)):
            if np.isfinite(matrix[i, j]):
                color = WHITE if matrix[i, j] > np.nanmedian(matrix) else INK
                ax.text(j, i, f"{matrix[i,j]:.3g}", ha="center", va="center", color=color, fontsize=8.5)
    fig.colorbar(im, ax=ax, fraction=0.025, label=metric.replace("_", " "))
    fig.tight_layout()
    save_figure(fig, out_dir, name)


def plot_dictionary_atoms(dictionary: GeometryDictionary, out_dir: Path) -> None:
    indices = [0, 4, 6, 9, 12, 20, 40, 80, 120, min(160, len(dictionary.masks)-1), min(200, len(dictionary.masks)-1), len(dictionary.masks)-1]
    indices = sorted(set(indices))
    fig, axes = plt.subplots(3, 4, figsize=(10.5, 8.0))
    for ax, idx in zip(axes.ravel(), indices, strict=False):
        ax.imshow(dictionary.masks[idx], cmap="gray", vmin=0, vmax=1)
        ax.set_title(dictionary.names[idx].replace("_", "\n"), fontsize=8.2)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Representative atoms in the finite geometric dictionary", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0,0,1,.95])
    save_figure(fig, out_dir, "16_geometry_dictionary_atoms")


def generate_benchmark_figures(
    out_dir: Path,
    one_d_rows: list[dict[str, object]],
    one_d_details: dict[str, dict[str, object]],
    noise_rows: list[dict[str, float | int]],
    separation_rows: list[dict[str, float]],
    order_rows: list[dict[str, float | int]],
    dictionary: GeometryDictionary,
    two_d_rows: list[dict[str, object]],
    two_d_details: dict[str, dict[str, object]],
    two_d_noise: list[dict[str, float]],
    two_d_random: list[dict[str, float | int]],
    out_model_rows: list[dict[str, object]],
    out_model_details: dict[str, dict[str, object]],
    natural_rows: list[dict[str, object]],
    natural_details: dict[str, dict[str, RealArray]],
    hybrid_rows: list[dict[str, object]],
    hybrid_detail: dict[str, object],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = diagram_axes((12.5, 5.8))
    stages = [
        ("hard 1D signals", "unknown count, noise, collisions", BLUE),
        ("exact 2D dictionary", "rectangles, disks, ellipses, bars", TEAL),
        ("out-of-model geometry", "stars, text, nested curves", ORANGE),
        ("natural images", "exploratory baselines only", MAGENTA),
        ("failure map", "identify the actual boundary", RED),
    ]
    xs = np.linspace(0.03, 0.82, len(stages))
    for i, (label, sub, color) in enumerate(stages):
        draw_box(ax, (xs[i], 0.43), 0.15, 0.22, f"{label}\n{sub}", face=color + "22", edge=color, fontsize=10.5)
        if i + 1 < len(stages):
            draw_arrow(ax, (xs[i] + 0.15, 0.54), (xs[i+1] - 0.005, 0.54), color=INK)
    ax.text(0.5, 0.88, "Complex signal and image benchmark architecture", ha="center", fontsize=22, weight="bold")
    ax.text(0.5, 0.13, "Exact-model tests and exploratory out-of-model tests are reported separately.", ha="center", fontsize=12, color=MUTED)
    save_figure(fig, out_dir, "01_benchmark_architecture")

    for number, case_name in enumerate(["bandlimited_8_jump", "analytic_6_jump", "chirp_6_jump", "bursts_6_jump", "rough_4_jump"], start=2):
        plot_1d_case(one_d_details[case_name], case_name.replace("_", " ").title(), out_dir, f"{number:02d}_{case_name}")

    plot_sweep(noise_rows, "sigma", ["median_location_error", "median_jump_error"], ["location error", "jump error"], "Noise sensitivity of six-jump recovery", out_dir, "07_noise_sweep", logx=True, logy=True)
    plot_sweep(noise_rows, "sigma", ["success_rate"], ["success rate"], "Recovery success versus moment noise", out_dir, "08_noise_success", logx=True)
    plot_sweep(separation_rows, "separation", ["location_error", "smallest_vandermonde_singular"], ["location error", "smallest singular value"], "Collision boundary and conditioning", out_dir, "09_separation_sweep", logx=True, logy=True)
    plot_sweep(order_rows, "order", ["success_rate"], ["success rate"], "Unknown-jump recovery as model order grows", out_dir, "10_order_success")
    plot_sweep(order_rows, "order", ["median_location_error", "median_runtime_seconds"], ["location error", "runtime seconds"], "Accuracy and runtime versus jump count", out_dir, "11_order_accuracy_runtime", logy=True)

    # 1D summary heatmap
    one_methods = ["raw_rmse", "fejer_rmse", "resolved_rmse", "raw_boundary_rmse", "resolved_boundary_rmse"]
    cases = [str(r["case"]) for r in one_d_rows]
    matrix = np.asarray([[float(r[k]) for k in one_methods] for r in one_d_rows])
    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    im = ax.imshow(np.log10(np.maximum(matrix, 1e-16)), aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(one_methods)), [m.replace("_", "\n") for m in one_methods])
    ax.set_yticks(range(len(cases)), [c.replace("_", " ") for c in cases])
    ax.set_title("Log10 error summary across complex one-dimensional cases", weight="bold")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i,j]:.2e}", ha="center", va="center", color=WHITE if j < 2 else INK, fontsize=8.2)
    fig.colorbar(im, ax=ax, fraction=.03, label="log10 error")
    fig.tight_layout()
    save_figure(fig, out_dir, "12_one_dimensional_summary")

    # Phase portrait of recovery errors
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    for index, row in enumerate(one_d_rows):
        ax.scatter(float(row["minimum_separation"]), float(row["location_error"]), s=90, label=str(row["case"]).replace("_", " "), color=PALETTE[index])
    ax.set_yscale("log")
    ax.set_xlabel("minimum edge separation")
    ax.set_ylabel("maximum location error")
    ax.set_title("Complex-case edge localization", weight="bold")
    ax.grid(alpha=.18)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    save_figure(fig, out_dir, "13_complex_case_localization")

    # Recovery count / phase residual
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8))
    names = [str(r["case"]).replace("_", "\n") for r in one_d_rows]
    axes[0].bar(np.arange(len(names)), [int(r["recovered_order"]) for r in one_d_rows], color=PALETTE[:len(names)], edgecolor=INK)
    axes[0].plot(np.arange(len(names)), [int(r["true_order"]) for r in one_d_rows], color=INK, marker="o", label="true order")
    axes[0].set_xticks(np.arange(len(names)), names, fontsize=8)
    axes[0].set_title("Recovered jump count", weight="bold")
    axes[0].legend()
    axes[1].bar(np.arange(len(names)), [float(r["phase_residual"]) for r in one_d_rows], color=PALETTE[:len(names)], edgecolor=INK)
    axes[1].set_yscale("log")
    axes[1].set_xticks(np.arange(len(names)), names, fontsize=8)
    axes[1].set_title("Polyphase phase residual", weight="bold")
    fig.tight_layout()
    save_figure(fig, out_dir, "14_order_and_phase_certificates")

    # Failure boundary schematic
    fig, ax = diagram_axes((12.2, 5.9))
    boxes = [
        (0.04, "well separated\nfinite-rate edges", TEAL),
        (0.25, "close edges\nill-conditioned", ORANGE),
        (0.46, "wrong smooth model\nresidual contamination", YELLOW),
        (0.67, "geometry outside\nfinite dictionary", MAGENTA),
        (0.84, "arbitrary natural image\nno exact theorem", RED),
    ]
    for x0, label, color in boxes:
        draw_box(ax, (x0, .42), .13, .20, label, face=color+"22", edge=color, fontsize=10.5)
    for a, b in zip(boxes[:-1], boxes[1:], strict=True):
        draw_arrow(ax, (a[0]+.13,.52),(b[0]-.005,.52), color=INK)
    ax.text(.5,.86,"The benchmark is designed to find the boundary, not hide it",ha="center",fontsize=21,weight="bold")
    ax.text(.5,.15,"The exact theorem is strongest on the left. The right-hand cases are exploratory and are reported as such.",ha="center",fontsize=11.5,color=MUTED)
    save_figure(fig,out_dir,"15_failure_boundary_map")

    plot_dictionary_atoms(dictionary, out_dir)

    index = 17
    for case_name in ["multi_geometry", "curved_shapes", "thin_structures"]:
        detail = two_d_details[case_name]
        plot_image_grid(np.asarray(detail["truth"]), detail["methods"], case_name.replace("_", " ").title(), out_dir, f"{index:02d}_{case_name}_reconstructions")
        index += 1
        plot_error_grid(np.asarray(detail["truth"]), detail["methods"], case_name.replace("_", " ").title() + " absolute errors", out_dir, f"{index:02d}_{case_name}_errors")
        index += 1

    plot_method_summary(two_d_rows, "rmse", "RMSE across exact geometric image cases", out_dir, f"{index:02d}_exact_geometry_rmse")
    index += 1
    plot_method_summary(two_d_rows, "boundary_rmse", "Boundary-band RMSE across exact geometric cases", out_dir, f"{index:02d}_exact_geometry_boundary_rmse")
    index += 1
    plot_sweep(two_d_noise, "sigma", ["median_rmse", "median_support_iou"], ["resolved RMSE", "support IoU"], "Noise sensitivity of geometric packet recovery", out_dir, f"{index:02d}_two_dimensional_noise", logx=True)
    index += 1

    # 2D random stress distribution
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.5))
    axes[0].hist([float(r["support_iou"]) for r in two_d_random], bins=10, color=TEAL, edgecolor=INK)
    axes[0].set_title("Support IoU", weight="bold")
    axes[1].hist([float(r["raw_rmse"]) for r in two_d_random], bins=10, alpha=.75, label="raw", color=BLUE, edgecolor=INK)
    axes[1].hist([float(r["resolved_rmse"]) for r in two_d_random], bins=10, alpha=.75, label="resolved", color=ORANGE, edgecolor=INK)
    axes[1].set_title("RMSE distribution", weight="bold")
    axes[1].legend()
    axes[2].scatter([int(r["true_count"]) for r in two_d_random], [int(r["selected_count"]) for r in two_d_random], color=MAGENTA, alpha=.8)
    axes[2].plot([1,6],[1,6],color=INK,ls="--")
    axes[2].set_xlabel("true count")
    axes[2].set_ylabel("selected count")
    axes[2].set_title("Model-order selection", weight="bold")
    for ax in axes:
        ax.grid(alpha=.16)
    fig.suptitle("Forty random finite-dictionary image cases", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    save_figure(fig,out_dir,f"{index:02d}_two_dimensional_random_stress")
    index += 1

    for case_name in ["star_out_of_dictionary", "text_over_gradient", "nested_rings"]:
        detail = out_model_details[case_name]
        plot_image_grid(np.asarray(detail["truth"]), detail["methods"], case_name.replace("_", " ").title(), out_dir, f"{index:02d}_{case_name}")
        index += 1

    plot_method_summary(out_model_rows, "rmse", "Out-of-dictionary image RMSE", out_dir, f"{index:02d}_out_of_model_rmse")
    index += 1
    plot_method_summary(out_model_rows, "edge_iou", "Out-of-dictionary edge overlap", out_dir, f"{index:02d}_out_of_model_edge_iou")
    index += 1

    for case_name in ["camera", "coins", "page"]:
        detail = natural_details[case_name]
        methods = {k:v for k,v in detail.items() if k != "truth"}
        plot_image_grid(detail["truth"], methods, f"Natural image: {case_name}", out_dir, f"{index:02d}_natural_{case_name}")
        index += 1
    plot_method_summary(natural_rows, "ssim", "Natural-image SSIM", out_dir, f"{index:02d}_natural_ssim")
    index += 1
    plot_method_summary(natural_rows, "boundary_rmse", "Natural-image boundary RMSE", out_dir, f"{index:02d}_natural_boundary_rmse")
    index += 1

    plot_image_grid(np.asarray(hybrid_detail["truth"]), hybrid_detail["methods"], "Natural-background hybrid with exact geometric packets", out_dir, f"{index:02d}_natural_hybrid")
    index += 1
    plot_error_grid(np.asarray(hybrid_detail["truth"]), hybrid_detail["methods"], "Natural-background hybrid error maps", out_dir, f"{index:02d}_natural_hybrid_errors")
    index += 1
    plot_method_summary(hybrid_rows, "rmse", "Natural-background hybrid RMSE", out_dir, f"{index:02d}_natural_hybrid_rmse")
    index += 1

    # Final scorecard
    exact_resolved = [r for r in two_d_rows if r["method"] == "dictionary_resolved"]
    natural_best = {}
    for case in sorted({str(r["case"]) for r in natural_rows}):
        subset = [r for r in natural_rows if r["case"] == case]
        natural_best[case] = min(subset, key=lambda r: float(r["rmse"]))
    fig, ax = diagram_axes((12.4, 6.4))
    ax.text(.5,.93,"Benchmark scorecard",ha="center",fontsize=23,weight="bold")
    lines = [
        f"1D complex cases with correct recovered count: {sum(int(r['true_order'])==int(r['recovered_order']) for r in one_d_rows)}/{len(one_d_rows)}",
        f"Median resolved/raw 1D RMSE ratio: {np.median([float(r['resolved_rmse'])/max(float(r['raw_rmse']),1e-30) for r in one_d_rows]):.3e}",
        f"Median exact-dictionary 2D resolved RMSE: {np.median([float(r['rmse']) for r in exact_resolved]):.3e}",
        f"Median random 2D support IoU: {np.median([float(r['support_iou']) for r in two_d_random]):.3f}",
        f"Natural images remain exploratory. Best method varies by case.",
    ]
    y=.78
    for i,line in enumerate(lines):
        color=PALETTE[i]
        draw_box(ax,(.12,y-.05),.76,.10,line,face=color+"18",edge=color,fontsize=12)
        y-=.14
    ax.text(.5,.08,"Exact-model success and out-of-model limitations are both part of the result.",ha="center",fontsize=11.5,color=MUTED)
    save_figure(fig,out_dir,f"{index:02d}_final_scorecard")


def validate_benchmark_results(
    one_d_rows: list[dict[str, object]],
    two_d_rows: list[dict[str, object]],
    two_d_random: list[dict[str, float | int]],
    natural_rows: list[dict[str, object]],
    figure_dir: Path,
) -> list[dict[str, object]]:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("all one-dimensional cases produced finite resolved errors", all(np.isfinite(float(r["resolved_rmse"])) for r in one_d_rows), "resolved RMSE finite"))
    controlled_rows = [r for r in one_d_rows if r.get("scope") == "controlled"]
    checks.append(("all controlled one-dimensional cases recovered the declared count", all(int(r["true_order"]) == int(r["recovered_order"]) for r in controlled_rows), "controlled model order"))
    checks.append(("resolved one-dimensional median RMSE beats raw Fourier", np.median([float(r["resolved_rmse"]) for r in one_d_rows]) < np.median([float(r["raw_rmse"]) for r in one_d_rows]), "median RMSE comparison"))
    exact_resolved = [r for r in two_d_rows if r["method"] == "dictionary_resolved"]
    raw = [r for r in two_d_rows if r["method"] == "raw_fourier"]
    checks.append(("all exact image cases have resolved outputs", len(exact_resolved) == 3, "three exact cases"))
    checks.append(("resolved median image RMSE beats raw Fourier", np.median([float(r["rmse"]) for r in exact_resolved]) < np.median([float(r["rmse"]) for r in raw]), "median image RMSE"))
    checks.append(("random image stress produced forty cases", len(two_d_random) == 40, "case count"))
    checks.append(("natural-image benchmark produced four images and five methods", len(natural_rows) == 20, "natural rows"))
    pdfs = sorted(figure_dir.glob("*.pdf"))
    pngs = sorted(figure_dir.glob("*.png"))
    checks.append(("figure pairs are complete", len(pdfs) == len(pngs) and [p.stem for p in pdfs] == [p.stem for p in pngs], f"{len(pdfs)} pairs"))
    checks.append(("every vector figure is nonempty", all(p.stat().st_size > 1000 for p in pdfs), "PDF assets"))
    checks.append(("every raster figure is nonempty", all(p.stat().st_size > 1000 for p in pngs), "PNG assets"))
    rows = [{"check": name, "passed": bool(passed), "detail": detail} for name, passed, detail in checks]
    failures = [row for row in rows if not row["passed"]]
    if failures:
        raise AssertionError(f"benchmark checks failed: {failures}")
    return rows


def run_complex_benchmark(base: Path) -> dict[str, object]:
    base.mkdir(parents=True, exist_ok=True)
    figures = base / "figures"
    tables = base / "tables"
    results_dir = base / "results"
    figures.mkdir(exist_ok=True)
    tables.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)

    one_d_rows, one_d_details = run_complex_1d_cases()
    noise_rows = run_1d_noise_sweep()
    separation_rows = run_1d_separation_sweep()
    order_rows = run_1d_order_sweep()

    dictionary = build_geometry_dictionary()
    two_d_rows, two_d_details = run_2d_exact_benchmarks(dictionary)
    two_d_noise = run_2d_noise_sweep(dictionary)
    two_d_random = run_2d_random_stress(dictionary, cases=40)
    out_model_rows, out_model_details = run_out_of_model_benchmarks(dictionary)
    natural_rows, natural_details = run_natural_image_benchmarks()
    hybrid_rows, hybrid_detail = run_natural_hybrid_benchmark(dictionary)

    generate_benchmark_figures(
        figures,
        one_d_rows,
        one_d_details,
        noise_rows,
        separation_rows,
        order_rows,
        dictionary,
        two_d_rows,
        two_d_details,
        two_d_noise,
        two_d_random,
        out_model_rows,
        out_model_details,
        natural_rows,
        natural_details,
        hybrid_rows,
        hybrid_detail,
    )

    checks = validate_benchmark_results(one_d_rows, two_d_rows, two_d_random, natural_rows, figures)

    write_csv(tables / "one_dimensional_cases.csv", one_d_rows)
    write_csv(tables / "one_dimensional_noise.csv", noise_rows)
    write_csv(tables / "one_dimensional_separation.csv", separation_rows)
    write_csv(tables / "one_dimensional_order.csv", order_rows)
    write_csv(tables / "two_dimensional_exact.csv", two_d_rows)
    write_csv(tables / "two_dimensional_noise.csv", two_d_noise)
    write_csv(tables / "two_dimensional_random.csv", two_d_random)
    write_csv(tables / "out_of_model_images.csv", out_model_rows)
    write_csv(tables / "natural_images.csv", natural_rows)
    write_csv(tables / "natural_hybrid.csv", hybrid_rows)
    write_csv(tables / "checks.csv", checks)

    result = {
        "title": "Complex Signal and Image Gibbs Benchmark",
        "one_dimensional_cases": one_d_rows,
        "one_dimensional_noise": noise_rows,
        "one_dimensional_separation": separation_rows,
        "one_dimensional_order": order_rows,
        "two_dimensional_exact": two_d_rows,
        "two_dimensional_noise": two_d_noise,
        "two_dimensional_random": two_d_random,
        "out_of_model_images": out_model_rows,
        "natural_images": natural_rows,
        "natural_hybrid": hybrid_rows,
        "dictionary_atoms": len(dictionary.names),
        "checks": checks,
        "figure_pairs": len(list(figures.glob("*.pdf"))),
        "median_1d_resolved_raw_ratio": float(np.median([float(r["resolved_rmse"]) / max(float(r["raw_rmse"]), 1e-30) for r in one_d_rows])),
        "median_2d_exact_resolved_raw_ratio": float(
            np.median([float(r["rmse"]) for r in two_d_rows if r["method"] == "dictionary_resolved"])
            / max(np.median([float(r["rmse"]) for r in two_d_rows if r["method"] == "raw_fourier"]), 1e-30)
        ),
        "median_2d_random_support_iou": float(np.median([float(r["support_iou"]) for r in two_d_random])),
    }
    (results_dir / "complex_benchmark_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def complex_benchmark_main() -> None:
    parser = argparse.ArgumentParser(description="Complex signal and image benchmark for projector-resolved Gibbs reconstruction")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = run_complex_benchmark(args.out)
    print(json.dumps({
        "figure_pairs": result["figure_pairs"],
        "dictionary_atoms": result["dictionary_atoms"],
        "median_1d_resolved_raw_ratio": result["median_1d_resolved_raw_ratio"],
        "median_2d_exact_resolved_raw_ratio": result["median_2d_exact_resolved_raw_ratio"],
        "median_2d_random_support_iou": result["median_2d_random_support_iou"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    complex_benchmark_main()

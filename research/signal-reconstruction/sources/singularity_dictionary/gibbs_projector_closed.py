#!/usr/bin/env python3
"""Single-file closed construction for singularity-exact Gibbs circumvention.

Running this file regenerates every numerical certificate, table, figure, the
KaTeX-friendly derivation, the LaTeX manuscript, and (when pdflatex exists) the
final PDF.  No project-local Python module is imported.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from scipy.special import sici

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
TAB = ROOT / "tables"
RES = ROOT / "results"
for d in (FIG, TAB, RES):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# One signal, one model, one complete seed-to-reconstruction path.
# ---------------------------------------------------------------------------
ALPHA = 1.0 / 4.0
BETA = 3.0 / 4.0
WIDTH = BETA - ALPHA
CENTER = 0.5 * (ALPHA + BETA)
AMP = 5.0 / 4.0
SMOOTH_DEGREE = 5
NGRID = 512
K_EDGE = tuple(k for k in range(-63, 64) if abs(k) > SMOOTH_DEGREE and k % 2 != 0)
GIBBS_CONSTANT = float(sici(math.pi)[0] / math.pi - 0.5)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.titlesize": 13,
    "axes.labelsize": 10.5,
    "legend.fontsize": 9,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def smooth(t: NDArray[np.floating] | float) -> NDArray[np.floating] | float:
    t = np.asarray(t)
    return (
        (1.0 / 3.0) * np.cos(2.0 * np.pi * t)
        + (1.0 / 4.0) * np.sin(6.0 * np.pi * t)
        - (1.0 / 5.0) * np.cos(10.0 * np.pi * t)
    )


def interval_mask(t: NDArray[np.floating] | float, alpha: float = ALPHA, beta: float = BETA) -> NDArray[np.floating] | float:
    arr = np.asarray(t)
    return ((arr >= alpha) & (arr < beta)).astype(float)


def signal(t: NDArray[np.floating] | float) -> NDArray[np.floating] | float:
    return smooth(t) + AMP * interval_mask(t)


def mhat_continuous(k: int, alpha: float = ALPHA, beta: float = BETA) -> complex:
    if k == 0:
        return complex(beta - alpha)
    return complex(
        np.exp(-1j * np.pi * k * (alpha + beta))
        * np.sin(np.pi * k * (beta - alpha))
        / (np.pi * k)
    )


def shat_continuous(k: int) -> complex:
    if k in (1, -1):
        return 1.0 / 6.0
    if k == 3:
        return -1j / 8.0
    if k == -3:
        return 1j / 8.0
    if k in (5, -5):
        return -1.0 / 10.0
    return 0.0 + 0.0j


def fhat_continuous(k: int) -> complex:
    return shat_continuous(k) + AMP * mhat_continuous(k)


def fourier_sum_from_coeffs(t: NDArray[np.floating], n_modes: int, coeff_fn=fhat_continuous, weights: str = "dirichlet") -> NDArray[np.floating]:
    ks = np.arange(-n_modes, n_modes + 1)
    coeff = np.array([coeff_fn(int(k)) for k in ks], dtype=complex)
    if weights == "fejer":
        w = 1.0 - np.abs(ks) / (n_modes + 1.0)
    elif weights == "lanczos":
        w = np.sinc(ks / (n_modes + 1.0))
    elif weights == "exponential":
        scale = np.maximum(n_modes, 1)
        w = np.exp(-36.0 * (np.abs(ks) / scale) ** 8)
    elif weights == "dirichlet":
        w = np.ones_like(ks, dtype=float)
    else:
        raise ValueError(f"unknown weights: {weights}")
    phase = np.exp(2j * np.pi * np.outer(t, ks))
    return np.real(phase @ (w * coeff))


def mask_partial_sum(t: NDArray[np.floating], n_modes: int, weights: str = "dirichlet") -> NDArray[np.floating]:
    return fourier_sum_from_coeffs(t, n_modes, coeff_fn=mhat_continuous, weights=weights)


def gibbs_profile(y: NDArray[np.floating]) -> NDArray[np.floating]:
    # Scaled right-side profile for a unit upward jump.
    si = np.array([sici(float(v))[0] for v in y])
    return 0.5 + si / np.pi


def numerical_continuous_coefficient(k: int) -> complex:
    real = quad(lambda x: float(signal(x) * np.cos(2 * np.pi * k * x)), 0.0, 1.0, points=[ALPHA, BETA], epsabs=1e-12)[0]
    imag = -quad(lambda x: float(signal(x) * np.sin(2 * np.pi * k * x)), 0.0, 1.0, points=[ALPHA, BETA], epsabs=1e-12)[0]
    return complex(real, imag)


def discrete_coeff(x: NDArray[np.floating]) -> NDArray[np.complex128]:
    return np.fft.fft(x) / x.size


def modes_for_n(n: int) -> NDArray[np.int64]:
    return np.rint(np.fft.fftfreq(n) * n).astype(int)


def lowpass_discrete(x: NDArray[np.floating], degree: int, *, weights: str = "dirichlet") -> NDArray[np.floating]:
    n = x.size
    modes = modes_for_n(n)
    coeff = discrete_coeff(x)
    if weights == "dirichlet":
        w = (np.abs(modes) <= degree).astype(float)
    elif weights == "fejer":
        w = np.maximum(0.0, 1.0 - np.abs(modes) / (degree + 1.0))
        w[np.abs(modes) > degree] = 0.0
    elif weights == "lanczos":
        w = np.sinc(modes / (degree + 1.0))
        w[np.abs(modes) > degree] = 0.0
    elif weights == "exponential":
        w = np.exp(-36.0 * (np.abs(modes) / max(degree, 1)) ** 8)
        w[np.abs(modes) > degree] = 0.0
    else:
        raise ValueError(weights)
    return np.real(np.fft.ifft(n * coeff * w))


def edge_amplitude_from_modes(x: NDArray[np.floating], mask: NDArray[np.floating], kset: Sequence[int] = K_EDGE) -> float:
    n = x.size
    modes = modes_for_n(n)
    xhat = discrete_coeff(x)
    mhat = discrete_coeff(mask)
    idx = [int(np.where(modes == k)[0][0]) for k in kset]
    denom = float(np.sum(np.abs(mhat[idx]) ** 2))
    if denom <= 0:
        raise ValueError("edge mode set has zero mask energy")
    value = np.sum(np.conjugate(mhat[idx]) * xhat[idx]) / denom
    return float(np.real_if_close(value, tol=1000))


def singularity_exact_reconstruction(x: NDArray[np.floating], mask: NDArray[np.floating], degree: int = SMOOTH_DEGREE, kset: Sequence[int] = K_EDGE) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating], float]:
    a = edge_amplitude_from_modes(x, mask, kset)
    edge = a * mask
    smooth_packet = x - edge
    smooth_rec = lowpass_discrete(smooth_packet, degree)
    return smooth_rec + edge, smooth_rec, edge, a


def real_fourier_design(t: NDArray[np.floating], degree: int) -> NDArray[np.floating]:
    cols: list[NDArray[np.floating]] = [np.ones_like(t)]
    for k in range(1, degree + 1):
        cols.append(np.cos(2 * np.pi * k * t))
        cols.append(np.sin(2 * np.pi * k * t))
    return np.column_stack(cols)


def interval_dictionary(denominator: int = 16, min_cells: int = 2) -> list[tuple[int, int]]:
    return [(i, j) for i in range(denominator) for j in range(i + min_cells, denominator + 1)]


def fit_interval_candidate(x: NDArray[np.floating], t: NDArray[np.floating], i: int, j: int, denominator: int = 16, degree: int = SMOOTH_DEGREE) -> tuple[float, NDArray[np.floating], NDArray[np.floating]]:
    mask = interval_mask(t, i / denominator, j / denominator)
    A = np.column_stack([real_fourier_design(t, degree), mask])
    coeff, *_ = np.linalg.lstsq(A, x, rcond=None)
    rec = A @ coeff
    residual = float(np.linalg.norm(x - rec))
    return residual, coeff, rec


def discover_interval(x: NDArray[np.floating], t: NDArray[np.floating], denominator: int = 16, degree: int = SMOOTH_DEGREE) -> tuple[tuple[int, int], list[dict[str, float]]]:
    rows: list[dict[str, float]] = []
    for i, j in interval_dictionary(denominator):
        residual, coeff, _ = fit_interval_candidate(x, t, i, j, denominator, degree)
        rows.append({
            "i": float(i),
            "j": float(j),
            "alpha": i / denominator,
            "beta": j / denominator,
            "residual_l2": residual,
            "amplitude": float(coeff[-1]),
        })
    rows.sort(key=lambda r: r["residual_l2"])
    best = (int(rows[0]["i"]), int(rows[0]["j"]))
    return best, rows


def haar_forward(x: NDArray[np.floating]) -> tuple[float, list[NDArray[np.floating]]]:
    current = np.asarray(x, dtype=float).copy()
    details: list[NDArray[np.floating]] = []
    while current.size > 1:
        low = (current[0::2] + current[1::2]) / math.sqrt(2.0)
        high = (current[0::2] - current[1::2]) / math.sqrt(2.0)
        details.append(high)
        current = low
    return float(current[0]), details


def haar_inverse(scale: float, details: Sequence[NDArray[np.floating]]) -> NDArray[np.floating]:
    current = np.array([scale], dtype=float)
    for high in reversed(details):
        out = np.empty(high.size * 2, dtype=float)
        out[0::2] = (current + high) / math.sqrt(2.0)
        out[1::2] = (current - high) / math.sqrt(2.0)
        current = out
    return current


def flatten_haar(scale: float, details: Sequence[NDArray[np.floating]]) -> NDArray[np.floating]:
    return np.concatenate([[scale], *[d.ravel() for d in reversed(details)]])


def unflatten_haar(coeff: NDArray[np.floating], n: int) -> tuple[float, list[NDArray[np.floating]]]:
    scale = float(coeff[0])
    # flattened order: coarsest details to finest details
    sizes = [1 << level for level in range(0, int(math.log2(n)))]
    pos = 1
    coarse_to_fine: list[NDArray[np.floating]] = []
    for size in sizes:
        coarse_to_fine.append(coeff[pos:pos + size].copy())
        pos += size
    details = list(reversed(coarse_to_fine))
    return scale, details


def boundary_band(t: NDArray[np.floating], width: float = 0.035) -> NDArray[np.bool_]:
    d1 = np.minimum(np.abs(t - ALPHA), 1.0 - np.abs(t - ALPHA))
    d2 = np.minimum(np.abs(t - BETA), 1.0 - np.abs(t - BETA))
    return (d1 <= width) | (d2 <= width)


def rmse(a: NDArray[np.floating], b: NDArray[np.floating], mask: NDArray[np.bool_] | None = None) -> float:
    diff = np.asarray(a) - np.asarray(b)
    if mask is not None:
        diff = diff[mask]
    return float(np.sqrt(np.mean(diff * diff)))


def linf(a: NDArray[np.floating], b: NDArray[np.floating], mask: NDArray[np.bool_] | None = None) -> float:
    diff = np.abs(np.asarray(a) - np.asarray(b))
    if mask is not None:
        diff = diff[mask]
    return float(np.max(diff))


def savefig(fig: plt.Figure, stem: str, *, dpi: int = 190) -> None:
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(FIG / f"{stem}.png", dpi=dpi, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def box(ax, xy: tuple[float, float], w: float, h: float, text: str, face: str = "#F8FAFC", edge: str = "#334155", fontsize: float = 10.5) -> None:
    x, y = xy
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018", facecolor=face, edgecolor=edge, linewidth=1.4)
    ax.add_patch(patch)
    label = ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", multialignment="center", fontsize=fontsize, linespacing=1.12)
    # shrink until safely inside
    for _ in range(18):
        fig = ax.figure
        fig.canvas.draw()
        bb = label.get_window_extent(renderer=fig.canvas.get_renderer())
        (x0, y0), (x1, y1) = ax.transData.transform(((x, y), (x + w, y + h)))
        if bb.width <= abs(x1 - x0) * 0.84 and bb.height <= abs(y1 - y0) * 0.78:
            break
        label.set_fontsize(max(7.0, label.get_fontsize() * 0.90))


def arrow(ax, a: tuple[float, float], b: tuple[float, float], text: str | None = None, color: str = "#334155", rad: float = 0.0) -> None:
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, linewidth=1.4, color=color, connectionstyle=f"arc3,rad={rad}"))
    if text:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ax.text(mx, my + 0.03, text, ha="center", va="center", fontsize=9, bbox=dict(facecolor="white", edgecolor="none", pad=1.5))


@dataclass
class Certificate:
    analytic_coefficient_max_error: float
    gibbs_constant: float
    edge_projector_idempotence: float
    edge_projector_annihilation: float
    exact_reconstruction_residual: float
    smooth_packet_residual: float
    discovered_interval_i: int
    discovered_interval_j: int
    dictionary_wrong_gap: float
    noise_norm: float
    noise_stability_margin: float
    haar_mask_nonzero_coefficients: int
    haar_mask_reconstruction_residual: float
    figure_pairs: int
    assertions: int


# ---------------------------------------------------------------------------
# Figure and certificate generation.
# ---------------------------------------------------------------------------
def generate_all() -> Certificate:
    t = np.arange(NGRID, dtype=float) / NGRID
    s = np.asarray(smooth(t), dtype=float)
    m = np.asarray(interval_mask(t), dtype=float)
    x = s + AMP * m
    band = boundary_band(t)

    # 01: full closed pipeline
    fig, ax = plt.subplots(figsize=(12.8, 5.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    stages = [
        (0.01, "seed\n$f=s+a\\mathbf{1}_\\Omega$", "#DBEAFE"),
        (0.175, "global Fourier\npartial sums", "#FEE2E2"),
        (0.34, "high-frequency\nedge functional", "#FEF3C7"),
        (0.505, "projectors\n$P_S,P_J$", "#D1FAE5"),
        (0.67, "smooth spectral\nreconstruction", "#EDE9FE"),
        (0.835, "exact synthesis\n$Q_MP_S+P_J$", "#FCE7F3"),
    ]
    for x0, txt, face in stages:
        box(ax, (x0, 0.40), 0.12, 0.22, txt, face=face)
    for idx in range(len(stages)-1):
        arrow(ax, (stages[idx][0]+0.12, 0.51), (stages[idx+1][0]-0.005, 0.51))
    ax.text(0.5, 0.88, "One closed construction: the discontinuity is represented, not globally approximated", ha="center", fontsize=19, weight="bold")
    ax.text(0.5, 0.17, r"$f-(Q_MP_Sf+P_Jf)=P_Sf-Q_MP_Sf$; for the chosen seed, the right side is identically zero.", ha="center", fontsize=13)
    savefig(fig, "01_closed_pipeline")

    # 02 seed decomposition
    td = np.linspace(0, 1, 2500, endpoint=False)
    fig, axes = plt.subplots(3, 1, figsize=(12.5, 7.4), sharex=True)
    axes[0].plot(td, smooth(td), lw=2)
    axes[0].set_title("Smooth packet $s(t)$: a degree-five trigonometric polynomial", loc="left", weight="bold")
    axes[1].plot(td, AMP * interval_mask(td), lw=2)
    axes[1].set_title(r"Singularity packet $j(t)=\frac{5}{4}\mathbf{1}_{[1/4,3/4)}(t)$", loc="left", weight="bold")
    axes[2].plot(td, signal(td), lw=2)
    axes[2].set_title("Observed signal $f=s+j$", loc="left", weight="bold")
    for a in axes:
        a.axvline(ALPHA, ls="--", lw=1); a.axvline(BETA, ls="--", lw=1); a.grid(alpha=.18); a.set_ylabel("amplitude")
    axes[-1].set_xlabel("periodic coordinate $t$")
    fig.tight_layout()
    savefig(fig, "02_seed_decomposition")

    # 03 exact coefficient formulas
    ks = np.arange(-25, 26)
    mh = np.array([mhat_continuous(int(k)) for k in ks])
    fh = np.array([fhat_continuous(int(k)) for k in ks])
    fig, axes = plt.subplots(2, 1, figsize=(12.2, 6.6), sharex=True)
    axes[0].stem(ks, np.abs(mh), basefmt=" ")
    axes[0].set_title(r"Exact mask coefficients $|\widehat m(k)|$: zero on even nonzero modes and $O(1/|k|)$ on odd modes", loc="left", weight="bold")
    axes[0].set_ylabel("magnitude")
    axes[1].stem(ks, np.abs(fh), basefmt=" ")
    axes[1].set_title(r"Exact signal coefficients $|\widehat f(k)|=|\widehat s(k)+a\widehat m(k)|$", loc="left", weight="bold")
    axes[1].set_ylabel("magnitude"); axes[1].set_xlabel("frequency $k$")
    for a in axes: a.grid(alpha=.18)
    fig.tight_layout()
    savefig(fig, "03_exact_fourier_coefficients")

    # 04 partial sums
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 7.0), sharex=True, sharey=True)
    for ax, N in zip(axes.ravel(), [5, 15, 40, 120], strict=True):
        rec = fourier_sum_from_coeffs(td, N)
        ax.plot(td, signal(td), lw=1.8, label="exact signal")
        ax.plot(td, rec, lw=1.2, label=f"global Fourier $N={N}$")
        ax.axvline(ALPHA, ls="--", lw=.8); ax.axvline(BETA, ls="--", lw=.8)
        ax.set_title(f"{2*N+1} retained modes", weight="bold")
        ax.grid(alpha=.16)
    axes[0,0].legend(loc="upper center", bbox_to_anchor=(1.04, 1.22), ncol=2, frameon=False)
    for ax in axes[-1]: ax.set_xlabel("$t$")
    for ax in axes[:,0]: ax.set_ylabel("amplitude")
    fig.suptitle("Global Fourier resolution narrows the oscillatory region but does not reduce its limiting relative height", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    savefig(fig, "04_global_fourier_partial_sums")

    # 05 local zoom
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.5), sharey=True)
    for ax, edge, side in [(axes[0], ALPHA, "upward jump"), (axes[1], BETA, "downward jump")]:
        loc = np.linspace(edge-0.055, edge+0.055, 3000)
        loc %= 1.0
        order = np.argsort(loc)
        loc = loc[order]
        ax.plot(loc, signal(loc), lw=2.0, label="exact")
        for N in [15, 40, 120]:
            ax.plot(loc, fourier_sum_from_coeffs(loc, N), lw=1.1, label=f"$N={N}$")
        ax.axvline(edge, ls="--", lw=1)
        ax.set_title(side, weight="bold"); ax.grid(alpha=.16); ax.set_xlabel("$t$")
    axes[0].set_ylabel("amplitude")
    axes[1].legend(loc="center left", bbox_to_anchor=(1.02, .5), frameon=False)
    fig.suptitle("The Gibbs boundary layer contracts toward each jump", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0,0,.88,.92])
    savefig(fig, "05_boundary_layer_zoom")

    # 06 scaled profile
    y = np.linspace(-12, 12, 2500)
    fig, ax = plt.subplots(figsize=(11.5, 5.3))
    ax.plot(y, gibbs_profile(y), lw=2.2, label=r"$\frac{1}{2}+\pi^{-1}\operatorname{Si}(y)$")
    ax.axhline(1.0, ls="--", lw=1, label="upper one-sided value")
    ax.axvline(np.pi, ls=":", lw=1.2, label="first limiting maximum")
    ax.scatter([np.pi], [1.0 + GIBBS_CONSTANT], s=40, zorder=5)
    ax.annotate(f"overshoot = {GIBBS_CONSTANT:.12f}", (np.pi, 1+GIBBS_CONSTANT), xytext=(5.1,1.12), arrowprops=dict(arrowstyle="->"))
    ax.set_xlabel("scaled distance from the jump")
    ax.set_ylabel("normalized partial-sum value")
    ax.set_title("Universal local Gibbs profile for a unit upward jump", weight="bold")
    ax.grid(alpha=.18); ax.legend(loc="lower right")
    fig.tight_layout()
    savefig(fig, "06_scaled_gibbs_profile")

    # 07 overshoot convergence
    overshoot_rows: list[dict[str, float]] = []
    Ns = [5, 8, 12, 20, 32, 48, 64, 96, 128, 192, 256, 384]
    for N in Ns:
        objective = lambda z: -(float(mask_partial_sum(np.array([z]), N)[0]) - 1.0)
        lo = ALPHA + 0.15 / (2*N+1)
        hi = ALPHA + 2.2 / (2*N+1)
        sol = minimize_scalar(objective, bounds=(lo, hi), method="bounded", options={"xatol":1e-14})
        ov = -float(sol.fun)
        overshoot_rows.append({"N": float(N), "location": float(sol.x), "relative_overshoot": ov, "absolute_overshoot": AMP*ov, "distance_to_limit": abs(ov-GIBBS_CONSTANT)})
    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    ax.semilogx([r["N"] for r in overshoot_rows], [r["relative_overshoot"] for r in overshoot_rows], marker="o", lw=1.8, label="measured overshoot")
    ax.axhline(GIBBS_CONSTANT, ls="--", lw=1.4, label=f"Gibbs constant {GIBBS_CONSTANT:.9f}")
    ax.set_xlabel("Fourier cutoff $N$"); ax.set_ylabel("overshoot / jump height")
    ax.set_title("Increasing the global Fourier cutoff does not drive the relative overshoot to zero", weight="bold")
    ax.grid(alpha=.18, which="both"); ax.legend()
    fig.tight_layout()
    savefig(fig, "07_overshoot_convergence")

    # 08 Dirichlet kernel
    theta = np.linspace(-np.pi, np.pi, 5000)
    fig, axes = plt.subplots(2, 1, figsize=(11.8, 6.8), sharex=True)
    for N in [5, 15, 40]:
        den = np.sin(theta/2)
        D = np.where(np.abs(den)<1e-14, 2*N+1, np.sin((N+.5)*theta)/den)
        axes[0].plot(theta, D, lw=1.1, label=f"$D_{{{N}}}$")
        axes[1].plot(theta, np.abs(D), lw=1.1, label=f"$|D_{{{N}}}|$")
    axes[0].set_ylim(-20, 85); axes[0].set_ylabel("signed kernel")
    axes[1].set_yscale("log"); axes[1].set_ylabel("absolute kernel"); axes[1].set_xlabel("angle")
    axes[0].set_title("Dirichlet kernels develop a narrower central lobe and persistent oscillatory side lobes", loc="left", weight="bold")
    for a in axes: a.grid(alpha=.16); a.legend(ncol=3)
    fig.tight_layout()
    savefig(fig, "08_dirichlet_kernel")

    # 09 filters comparison
    Nfilter = 40
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 7.0), sharex=True, sharey=True)
    methods = [("dirichlet","unfiltered partial sum"),("fejer","Fejer mean"),("lanczos","Lanczos sigma"),("exponential","exponential filter")]
    for ax, (method, title) in zip(axes.ravel(), methods, strict=True):
        ax.plot(td, signal(td), lw=2, label="exact")
        ax.plot(td, fourier_sum_from_coeffs(td, Nfilter, weights=method), lw=1.3, label=title)
        ax.axvline(ALPHA, ls="--", lw=.8); ax.axvline(BETA, ls="--", lw=.8)
        ax.set_title(title, weight="bold"); ax.grid(alpha=.16)
    axes[0,0].legend(loc="upper center", bbox_to_anchor=(1.02,1.22), ncol=2, frameon=False)
    for a in axes[-1]: a.set_xlabel("$t$")
    for a in axes[:,0]: a.set_ylabel("amplitude")
    fig.suptitle("Spectral filters reduce ringing by replacing overshoot with a wider transition layer", fontsize=16, weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    savefig(fig, "09_spectral_filters")

    # 10 filter error profiles
    fig, ax = plt.subplots(figsize=(11.5, 5.3))
    for method, title in methods:
        rec = fourier_sum_from_coeffs(td, Nfilter, weights=method)
        ax.plot(td, np.abs(rec-signal(td)), lw=1.2, label=title)
    ax.set_yscale("log"); ax.set_ylim(1e-7, 1)
    ax.axvline(ALPHA, ls="--", lw=.8); ax.axvline(BETA, ls="--", lw=.8)
    ax.set_xlabel("$t$"); ax.set_ylabel("absolute error")
    ax.set_title("Filtering changes the shape of the error but does not encode the jump exactly", weight="bold")
    ax.grid(alpha=.18, which="both"); ax.legend(loc="center left", bbox_to_anchor=(1.02,.5), frameon=False)
    fig.tight_layout(rect=[0,0,.83,1])
    savefig(fig, "10_filter_error_profiles")

    # Discrete exact packet construction
    rec_exact, s_rec, j_rec, a_est = singularity_exact_reconstruction(x, m)
    exact_resid = float(np.max(np.abs(rec_exact-x)))
    smooth_resid = float(np.max(np.abs(s_rec-s)))

    # 11 edge functional energies
    modes = modes_for_n(NGRID)
    xhat = discrete_coeff(x); mhat = discrete_coeff(m)
    idxK = [int(np.where(modes==k)[0][0]) for k in K_EDGE]
    contributions = np.real(np.conjugate(mhat[idxK]) * xhat[idxK])
    denom_terms = np.abs(mhat[idxK])**2
    orderK = np.argsort(np.abs(np.array(K_EDGE)))
    fig, axes = plt.subplots(2, 1, figsize=(11.7, 6.7), sharex=True)
    axes[0].stem(np.array(K_EDGE)[orderK], denom_terms[orderK], basefmt=" ")
    axes[0].set_ylabel(r"$|\widehat m(k)|^2$")
    axes[0].set_title("The edge amplitude is identified only from frequencies outside the smooth seed band", loc="left", weight="bold")
    axes[1].stem(np.array(K_EDGE)[orderK], contributions[orderK], basefmt=" ")
    axes[1].set_ylabel(r"$\Re(\overline{\widehat m(k)}\widehat f(k))$")
    axes[1].set_xlabel("selected edge frequency $k$")
    for a in axes: a.grid(alpha=.16)
    fig.tight_layout()
    savefig(fig, "11_edge_functional_modes")

    # 12 projector pipeline
    fig, ax = plt.subplots(figsize=(12.4, 5.7))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    box(ax,(.03,.39),.16,.23,"observed signal\n$f=s+am$",face="#DBEAFE",fontsize=13)
    box(ax,(.29,.60),.18,.17,"edge packet\n$P_Jf=\\ell_K(f)m$",face="#FEE2E2",fontsize=12)
    box(ax,(.29,.18),.18,.17,"smooth packet\n$P_Sf=f-P_Jf$",face="#D1FAE5",fontsize=12)
    box(ax,(.58,.60),.17,.17,"retain exactly\n$P_Jf$",face="#FEF3C7",fontsize=12)
    box(ax,(.58,.18),.17,.17,"Fourier project\n$Q_5P_Sf$",face="#EDE9FE",fontsize=12)
    box(ax,(.82,.39),.15,.23,"synthesis\n$Q_5P_Sf+P_Jf=f$",face="#FCE7F3",fontsize=12)
    arrow(ax,(.19,.50),(.29,.68),"$P_J$")
    arrow(ax,(.19,.49),(.29,.27),"$P_S$")
    arrow(ax,(.47,.68),(.58,.68))
    arrow(ax,(.47,.27),(.58,.27))
    arrow(ax,(.75,.68),(.82,.54))
    arrow(ax,(.75,.27),(.82,.45))
    ax.text(.5,.91,"Singularity-exact analysis and synthesis",ha="center",fontsize=19,weight="bold")
    ax.text(.5,.07,r"$P_J^2=P_J$, $P_S^2=P_S$, $P_SP_J=P_JP_S=0$, $P_S+P_J=I$.",ha="center",fontsize=13)
    savefig(fig,"12_projector_pipeline")

    # 13 smooth and edge recovered
    fig, axes = plt.subplots(3, 1, figsize=(12.5,7.3),sharex=True)
    axes[0].plot(t,x,lw=1.7); axes[0].set_title("sampled observation",loc="left",weight="bold")
    axes[1].plot(t,s_rec,lw=1.7,label="recovered smooth packet"); axes[1].plot(t,s,ls="--",lw=1,label="exact smooth seed")
    axes[1].set_title(f"$P_Sf$ and $Q_5P_Sf$; maximum residual {smooth_resid:.2e}",loc="left",weight="bold"); axes[1].legend(ncol=2)
    axes[2].plot(t,j_rec,lw=1.7,label=rf"recovered edge packet, $\widehat{{a}}={a_est:.15f}$"); axes[2].plot(t,AMP*m,ls="--",lw=1,label="exact edge packet")
    axes[2].set_title("$P_Jf$",loc="left",weight="bold"); axes[2].legend(ncol=2)
    for a in axes: a.axvline(ALPHA,ls="--",lw=.8); a.axvline(BETA,ls="--",lw=.8); a.grid(alpha=.16); a.set_ylabel("amplitude")
    axes[-1].set_xlabel("grid coordinate")
    fig.tight_layout()
    savefig(fig,"13_recovered_packets")

    # 14 exact reconstruction vs global
    global40 = lowpass_discrete(x,40)
    fig, axes = plt.subplots(2,1,figsize=(12.5,6.7),sharex=True)
    axes[0].plot(t,x,lw=2,label="exact"); axes[0].plot(t,global40,lw=1.1,label="global Fourier, $N=40$")
    axes[0].set_title("Global reconstruction",loc="left",weight="bold"); axes[0].legend(ncol=2)
    axes[1].plot(t,x,lw=2,label="exact"); axes[1].plot(t,rec_exact,lw=1.1,ls="--",label="projector-resolved reconstruction")
    axes[1].set_title(f"Singularity-exact reconstruction; maximum residual {exact_resid:.2e}",loc="left",weight="bold"); axes[1].legend(ncol=2)
    for a in axes: a.axvline(ALPHA,ls="--",lw=.8); a.axvline(BETA,ls="--",lw=.8); a.grid(alpha=.16); a.set_ylabel("amplitude")
    axes[-1].set_xlabel("$t$")
    fig.tight_layout()
    savefig(fig,"14_global_vs_packet_reconstruction")

    # 15 residual comparison
    fig, axes = plt.subplots(2,1,figsize=(12.5,6.5),sharex=True)
    axes[0].plot(t,global40-x,lw=1.2); axes[0].set_title("global Fourier residual",loc="left",weight="bold")
    axes[1].plot(t,rec_exact-x,lw=1.2); axes[1].set_title("projector-resolved residual",loc="left",weight="bold")
    for a in axes: a.axvline(ALPHA,ls="--",lw=.8); a.axvline(BETA,ls="--",lw=.8); a.grid(alpha=.16); a.set_ylabel("signed error")
    axes[-1].set_xlabel("$t$")
    fig.tight_layout()
    savefig(fig,"15_residual_comparison")

    # 16 boundary band metrics
    metric_rows: list[dict[str,float|str]] = []
    for degree in [5,10,20,40,80,120]:
        for method in ["dirichlet","fejer","lanczos","exponential"]:
            rr = lowpass_discrete(x,degree,weights=method)
            metric_rows.append({"degree":degree,"method":method,"rmse_global":rmse(rr,x),"rmse_boundary":rmse(rr,x,band),"linf_global":linf(rr,x),"linf_boundary":linf(rr,x,band)})
        metric_rows.append({"degree":degree,"method":"packet","rmse_global":rmse(rec_exact,x),"rmse_boundary":rmse(rec_exact,x,band),"linf_global":linf(rec_exact,x),"linf_boundary":linf(rec_exact,x,band)})
    fig, axes = plt.subplots(1,2,figsize=(12.4,4.8))
    for method in ["dirichlet","fejer","lanczos","exponential","packet"]:
        rows=[r for r in metric_rows if r["method"]==method]
        axes[0].loglog([r["degree"] for r in rows],[max(float(r["rmse_global"]),1e-17) for r in rows],marker="o",label=method)
        axes[1].loglog([r["degree"] for r in rows],[max(float(r["rmse_boundary"]),1e-17) for r in rows],marker="o",label=method)
    axes[0].set_title("whole-domain RMSE",weight="bold"); axes[1].set_title("boundary-band RMSE",weight="bold")
    for a in axes: a.set_xlabel("nominal spectral degree"); a.set_ylabel("RMSE"); a.grid(alpha=.18,which="both")
    axes[1].legend(loc="center left",bbox_to_anchor=(1.02,.5),frameon=False)
    fig.suptitle("The exact packet method removes the discontinuity contribution from the spectral error",fontsize=15.5,weight="bold")
    fig.tight_layout(rect=[0,0,.84,.91])
    savefig(fig,"16_error_rates")

    # 17 pointwise boundary error
    fig, ax = plt.subplots(figsize=(11.7,5.2))
    local = (np.abs(t-ALPHA)<.06)
    ax.plot(t[local],np.abs(global40[local]-x[local]),lw=1.5,label="global Fourier")
    ax.plot(t[local],np.abs(rec_exact[local]-x[local]),lw=1.5,label="packet reconstruction")
    ax.axvline(ALPHA,ls="--",lw=1)
    ax.set_yscale("log"); ax.set_ylim(1e-17,1)
    ax.set_xlabel("$t$"); ax.set_ylabel("absolute error")
    ax.set_title("Near the jump, the packet method leaves only floating-point reconstruction error",weight="bold")
    ax.grid(alpha=.18,which="both"); ax.legend()
    fig.tight_layout()
    savefig(fig,"17_boundary_error_log")

    # 18 derivatives / finite differences
    dx = np.roll(x,-1)-x
    dg = np.roll(global40,-1)-global40
    dp = np.roll(rec_exact,-1)-rec_exact
    fig, axes = plt.subplots(3,1,figsize=(12.4,7.1),sharex=True)
    axes[0].plot(t,dx,lw=1.2); axes[0].set_title("exact first difference: smooth variation plus two jump spikes",loc="left",weight="bold")
    axes[1].plot(t,dg,lw=1.2); axes[1].set_title("global Fourier first difference: oscillatory boundary packets",loc="left",weight="bold")
    axes[2].plot(t,dp,lw=1.2); axes[2].set_title("projector-resolved first difference",loc="left",weight="bold")
    for a in axes: a.axvline(ALPHA,ls="--",lw=.8); a.axvline(BETA,ls="--",lw=.8); a.grid(alpha=.16); a.set_ylabel(r"$\Delta x$")
    axes[-1].set_xlabel("$t$")
    fig.tight_layout()
    savefig(fig,"18_first_difference_comparison")

    # 19 polyphase refinement tree
    fig, ax = plt.subplots(figsize=(11.7,6.1))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    nodes=[(.5,.86,"$[0,1)$"),(.28,.63,"$[0,1/2)$"),(.72,.63,"$[1/2,1)$"),(.14,.36,"$[0,1/4)$"),(.39,.36,"$[1/4,1/2)$"),(.61,.36,"$[1/2,3/4)$"),(.86,.36,"$[3/4,1)$")]
    edges=[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]
    for a,b in edges: arrow(ax,(nodes[a][0],nodes[a][1]-.04),(nodes[b][0],nodes[b][1]+.04),color="#94A3B8")
    for idx,(xx,yy,txt) in enumerate(nodes):
        selected=idx in (4,5)
        box(ax,(xx-.09,yy-.045),.18,.09,txt,face="#FDE68A" if selected else "#F8FAFC",edge="#B45309" if selected else "#334155",fontsize=11)
    ax.text(.5,.13,r"$\mathbf{1}_{[1/4,3/4)}=\mathbf{1}_{[1/4,1/2)}+\mathbf{1}_{[1/2,3/4)}$",ha="center",fontsize=15)
    ax.text(.5,.96,"The jump packet is an exact mixed-depth dyadic spatial packet",ha="center",fontsize=18,weight="bold")
    savefig(fig,"19_dyadic_refinement_tree")

    # 20 phase packets on finite grid
    fig, axes=plt.subplots(4,1,figsize=(12.3,7.4),sharex=True)
    for r,a in enumerate(axes):
        phase=np.zeros_like(m); phase[r::4]=m[r::4]
        a.stem(np.arange(NGRID),phase,markerfmt=" ",basefmt=" ")
        a.set_ylabel(f"phase {r}"); a.grid(alpha=.14)
    axes[0].set_title("Order-four polyphase packets of the exact interval mask",loc="left",weight="bold")
    axes[-1].set_xlabel("sample address")
    fig.tight_layout()
    savefig(fig,"20_mask_polyphase_packets")

    # 21 Haar sparsity of mask
    scale_m, details_m=haar_forward(m)
    hc=flatten_haar(scale_m,details_m)
    nonzero=int(np.sum(np.abs(hc)>1e-12))
    fig, axes=plt.subplots(2,1,figsize=(12.0,6.2))
    axes[0].stem(np.arange(hc.size),np.abs(hc),markerfmt=" ",basefmt=" ")
    axes[0].set_yscale("log"); axes[0].set_ylabel("coefficient magnitude")
    axes[0].set_title(f"The dyadically aligned interval mask has only {nonzero} nonzero Haar coefficients",loc="left",weight="bold")
    order=np.argsort(np.abs(hc))[::-1]
    axes[1].plot(np.arange(1,hc.size+1),np.cumsum(np.abs(hc[order])**2)/np.sum(np.abs(hc)**2),lw=2)
    axes[1].set_xscale("log"); axes[1].set_xlabel("largest coefficients retained"); axes[1].set_ylabel("cumulative energy")
    axes[1].grid(alpha=.18,which="both")
    fig.tight_layout()
    savefig(fig,"21_haar_sparsity")

    # 22 exact Haar reconstruction of mask
    mask_haar_rec=haar_inverse(scale_m,details_m)
    fig, axes=plt.subplots(2,1,figsize=(12.2,6.3),sharex=True)
    axes[0].plot(t,m,lw=2,label="mask"); axes[0].plot(t,mask_haar_rec,ls="--",lw=1.2,label="inverse Haar")
    axes[0].legend(ncol=2); axes[0].set_title("Exact Haar reconstruction of the same singularity packet",loc="left",weight="bold")
    axes[1].plot(t,mask_haar_rec-m,lw=1.2); axes[1].set_title(f"maximum residual {np.max(np.abs(mask_haar_rec-m)):.2e}",loc="left",weight="bold")
    for a in axes: a.grid(alpha=.16); a.set_ylabel("amplitude")
    axes[-1].set_xlabel("$t$")
    fig.tight_layout()
    savefig(fig,"22_haar_mask_reconstruction")

    # 23 Fourier vs Haar coefficient concentration
    edge_fft=np.fft.fft(m)/math.sqrt(NGRID)
    four_order=np.argsort(np.abs(edge_fft))[::-1]
    haar_order=np.argsort(np.abs(hc))[::-1]
    fig, ax=plt.subplots(figsize=(11.2,5.2))
    ax.loglog(np.arange(1,NGRID+1),1-np.cumsum(np.abs(edge_fft[four_order])**2)/np.sum(np.abs(edge_fft)**2),label="Fourier residual energy")
    ax.loglog(np.arange(1,NGRID+1),np.maximum(1-np.cumsum(np.abs(hc[haar_order])**2)/np.sum(np.abs(hc)**2),1e-18),label="Haar residual energy")
    ax.set_xlabel("coefficients retained"); ax.set_ylabel("unrepresented energy fraction")
    ax.set_title("The interval packet is globally dense in Fourier space but sparse in an aligned Haar atlas",weight="bold")
    ax.grid(alpha=.18,which="both"); ax.legend()
    fig.tight_layout()
    savefig(fig,"23_fourier_haar_concentration")

    # 24 finite interval dictionary heatmap
    best, rows=discover_interval(x,t)
    denom=16
    mat=np.full((denom+1,denom+1),np.nan)
    for r in rows: mat[int(r["i"]),int(r["j"])]=max(r["residual_l2"],1e-16)
    fig,ax=plt.subplots(figsize=(9.5,7.0))
    im=ax.imshow(np.log10(mat),origin="lower",aspect="equal",cmap="viridis")
    ax.set_xlabel("right endpoint index $j$"); ax.set_ylabel("left endpoint index $i$")
    ax.set_title("Finite dyadic interval discovery: log10 residual of each smooth-plus-one-interval model",weight="bold")
    ax.scatter([12],[4],s=80,facecolors="none",edgecolors="red",linewidths=2,label="true interval")
    ax.legend(loc="upper left")
    cbar=fig.colorbar(im,ax=ax,fraction=.046,pad=.04); cbar.set_label("log10 residual norm")
    fig.tight_layout()
    savefig(fig,"24_interval_dictionary_heatmap")

    # 25 ranking
    top=rows[:12]
    labels=[f"[{int(r['i'])}/16,{int(r['j'])}/16)" for r in top]
    vals=[max(r["residual_l2"],1e-16) for r in top]
    fig,ax=plt.subplots(figsize=(11.5,5.5))
    ax.bar(np.arange(len(vals)),vals)
    ax.set_yscale("log"); ax.set_xticks(np.arange(len(vals)),labels,rotation=35,ha="right")
    ax.set_ylabel("residual norm"); ax.set_title("The true interval is the unique zero-residual model in the finite dictionary",weight="bold")
    ax.grid(alpha=.16,axis="y",which="both")
    fig.tight_layout()
    savefig(fig,"25_interval_candidate_ranking")

    wrong_gap=float(rows[1]["residual_l2"])
    # 26 noise stability theorem experiment
    rng=np.random.default_rng(20260729)
    direction=rng.normal(size=NGRID); direction/=np.linalg.norm(direction)
    fractions=np.array([0.0,.10,.25,.40,.49,.51,.75,1.0])
    noise_rows=[]
    for frac in fractions:
        e=frac*wrong_gap*direction
        yobs=x+e
        found,rws=discover_interval(yobs,t)
        noise_rows.append({"fraction_of_gap":float(frac),"noise_norm":float(np.linalg.norm(e)),"found_i":found[0],"found_j":found[1],"best_residual":rws[0]["residual_l2"],"second_residual":rws[1]["residual_l2"]})
    fig,ax=plt.subplots(figsize=(11.2,5.2))
    ax.plot([r["fraction_of_gap"] for r in noise_rows],[r["best_residual"] for r in noise_rows],marker="o",label="best candidate residual")
    ax.plot([r["fraction_of_gap"] for r in noise_rows],[r["second_residual"] for r in noise_rows],marker="o",label="second candidate residual")
    ax.axvline(.5,ls="--",lw=1.2,label=r"proved universal stability threshold $\|e\|<\gamma/2$")
    ax.set_xlabel("noise norm / noiseless wrong-model gap"); ax.set_ylabel("residual norm")
    ax.set_title("Finite dictionary recovery remains certified below half the separation gap",weight="bold")
    ax.grid(alpha=.18); ax.legend()
    fig.tight_layout()
    savefig(fig,"26_dictionary_noise_stability")

    # 27 amplitude estimator under noise
    sigma_values=np.array([0.0,1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2])
    amp_rows=[]
    trials=200
    for sig in sigma_values:
        est=[]
        for _ in range(trials):
            yobs=x+rng.normal(scale=sig,size=NGRID)
            est.append(edge_amplitude_from_modes(yobs,m))
        amp_rows.append({"sigma":float(sig),"mean":float(np.mean(est)),"std":float(np.std(est,ddof=1)),"bias":float(np.mean(est)-AMP)})
    fig,axes=plt.subplots(1,2,figsize=(12.1,4.6))
    axes[0].semilogx(np.maximum(sigma_values,1e-7),[r["mean"] for r in amp_rows],marker="o")
    axes[0].axhline(AMP,ls="--",label="true amplitude"); axes[0].set_xlabel("noise standard deviation"); axes[0].set_ylabel("mean amplitude estimate"); axes[0].legend(); axes[0].grid(alpha=.18)
    axes[1].loglog(np.maximum(sigma_values,1e-7),[max(r["std"],1e-16) for r in amp_rows],marker="o")
    axes[1].set_xlabel("noise standard deviation"); axes[1].set_ylabel("estimate standard deviation"); axes[1].grid(alpha=.18,which="both")
    fig.suptitle("The out-of-band edge functional is exact without noise and has measurable noise amplification",fontsize=15.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.91])
    savefig(fig,"27_amplitude_noise_study")

    # 28 endpoint perturbation
    shifts=np.arange(-12,13)
    pert_rows=[]
    for sh in shifts:
        mh=interval_mask(t,ALPHA+sh/NGRID,BETA)
        err=AMP*(mh-m)
        sym=int(np.sum(mh!=m))
        pert_rows.append({"shift_samples":int(sh),"symmetric_difference_samples":sym,"l2_normalized":float(np.linalg.norm(err)/math.sqrt(NGRID)),"theory":AMP*math.sqrt(sym/NGRID)})
    fig,ax=plt.subplots(figsize=(10.8,5.0))
    ax.plot(shifts,[r["l2_normalized"] for r in pert_rows],marker="o",label="measured")
    ax.plot(shifts,[r["theory"] for r in pert_rows],ls="--",label=r"$|a|\sqrt{|\Omega\triangle\widehat\Omega|/N}$")
    ax.set_xlabel("left-endpoint shift in samples"); ax.set_ylabel(r"normalized $\ell^2$ error")
    ax.set_title("Endpoint error is localized exactly on the symmetric difference of the packet supports",weight="bold")
    ax.grid(alpha=.18); ax.legend()
    fig.tight_layout()
    savefig(fig,"28_endpoint_perturbation_bound")

    # 29 model mismatch: extra smooth mode beyond declared degree
    mismatch=0.06*np.cos(2*np.pi*9*t)
    xm=x+mismatch
    rm,sm,jm,am=singularity_exact_reconstruction(xm,m)
    fig,axes=plt.subplots(2,1,figsize=(12.0,6.1),sharex=True)
    axes[0].plot(t,xm,lw=1.8,label="mismatched signal"); axes[0].plot(t,rm,lw=1.1,label="degree-five packet reconstruction")
    axes[0].legend(ncol=2); axes[0].set_title("The edge remains exact, but an undeclared smooth frequency becomes the residual",loc="left",weight="bold")
    axes[1].plot(t,xm-rm,lw=1.4,label="residual"); axes[1].plot(t,mismatch,lw=1,ls="--",label="undeclared mode")
    axes[1].legend(ncol=2); axes[1].set_title("Residual localization in model space",loc="left",weight="bold")
    for a in axes: a.axvline(ALPHA,ls="--",lw=.8); a.axvline(BETA,ls="--",lw=.8); a.grid(alpha=.16); a.set_ylabel("amplitude")
    axes[-1].set_xlabel("$t$")
    fig.tight_layout()
    savefig(fig,"29_model_mismatch_residual")

    # 30 wrong packet negative control
    wrong=interval_mask(t,ALPHA+4/NGRID,BETA-3/NGRID)
    rw,sw,jw,aw=singularity_exact_reconstruction(x,wrong)
    fig,axes=plt.subplots(2,1,figsize=(12.0,6.1),sharex=True)
    axes[0].plot(t,x,lw=1.8,label="exact"); axes[0].plot(t,rw,lw=1.1,label="wrong-packet reconstruction")
    axes[0].legend(ncol=2); axes[0].set_title("Negative control: an incorrect singularity packet does not reconstruct the signal",loc="left",weight="bold")
    axes[1].plot(t,x-rw,lw=1.3); axes[1].set_title(f"nonzero residual; maximum error {linf(rw,x):.3e}",loc="left",weight="bold")
    for a in axes: a.grid(alpha=.16); a.set_ylabel("amplitude")
    axes[-1].set_xlabel("$t$")
    fig.tight_layout()
    savefig(fig,"30_wrong_packet_negative_control")

    # 31 representation counts
    global_degrees=np.arange(5,161,5)
    global_errors=[]
    for deg in global_degrees: global_errors.append(linf(lowpass_discrete(x,int(deg)),x,band))
    fig,ax=plt.subplots(figsize=(11.0,5.2))
    ax.semilogy(2*global_degrees+1,global_errors,marker="o",label="global Fourier boundary error")
    ax.axhline(max(exact_resid,1e-16),ls="--",label="packet reconstruction residual")
    ax.set_xlabel("global Fourier coefficients retained"); ax.set_ylabel("boundary-band maximum error")
    ax.set_title("More global modes reduce the width of ringing, not the limiting jump-relative overshoot",weight="bold")
    ax.grid(alpha=.18,which="both"); ax.legend()
    fig.tight_layout()
    savefig(fig,"31_mode_budget_comparison")

    # 32 total variation
    tv_exact=float(np.sum(np.abs(np.roll(x,-1)-x)))
    tv_rows=[]
    for deg in [5,10,20,40,80,120,180]:
        rr=lowpass_discrete(x,deg)
        tv_rows.append({"degree":deg,"global_tv":float(np.sum(np.abs(np.roll(rr,-1)-rr))),"exact_tv":tv_exact,"packet_tv":float(np.sum(np.abs(np.roll(rec_exact,-1)-rec_exact)))})
    fig,ax=plt.subplots(figsize=(10.8,5.1))
    ax.plot([r["degree"] for r in tv_rows],[r["global_tv"] for r in tv_rows],marker="o",label="global Fourier")
    ax.axhline(tv_exact,ls="--",label="exact / packet reconstruction")
    ax.set_xlabel("degree"); ax.set_ylabel("periodic discrete total variation")
    ax.set_title("Global Fourier ringing introduces excess variation near the jump",weight="bold")
    ax.grid(alpha=.18); ax.legend()
    fig.tight_layout()
    savefig(fig,"32_total_variation")

    # 33 error source decomposition
    fig,ax=plt.subplots(figsize=(12.0,5.5))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    box(ax,(.05,.63),.20,.18,"complete signal\n$f=s+j$",face="#DBEAFE",fontsize=13)
    box(ax,(.38,.68),.22,.14,"global spectral error\n$(I-Q_N)s+(I-Q_N)j$",face="#FEE2E2",fontsize=12)
    box(ax,(.38,.28),.22,.14,"packet spectral error\n$(I-Q_N)s$",face="#D1FAE5",fontsize=12)
    box(ax,(.73,.68),.21,.14,"jump term persists\nas Gibbs boundary layer",face="#FCA5A5",fontsize=11)
    box(ax,(.73,.28),.21,.14,"jump term is retained\nexactly as $j$",face="#A7F3D0",fontsize=11)
    arrow(ax,(.25,.72),(.38,.75),"global")
    arrow(ax,(.25,.68),(.38,.35),"resolved")
    arrow(ax,(.60,.75),(.73,.75))
    arrow(ax,(.60,.35),(.73,.35))
    ax.text(.5,.91,"Where the Gibbs term goes",ha="center",fontsize=20,weight="bold")
    ax.text(.5,.10,"The calculus does not cancel the jump's Fourier tail; it removes that tail from the approximation task by assigning the jump its own exact packet.",ha="center",fontsize=11.5)
    savefig(fig,"33_error_source_decomposition")

    # 34 projector matrix on small exact grid
    nsmall=64; ts=np.arange(nsmall)/nsmall; ms=interval_mask(ts); xs=smooth(ts)+AMP*ms
    modes_s=modes_for_n(nsmall); F=np.exp(-2j*np.pi*np.outer(np.arange(nsmall),np.arange(nsmall))/nsmall)/nsmall
    mhs=F@ms
    ksmall=[k for k in range(-15,16) if abs(k)>SMOOTH_DEGREE and k%2!=0]
    idx=[int(np.where(modes_s==k)[0][0]) for k in ksmall]
    row=np.sum(np.conjugate(mhs[idx,None])*F[idx,:],axis=0)/np.sum(np.abs(mhs[idx])**2)
    Pj=np.outer(ms,row); Ps=np.eye(nsmall)-Pj
    idem=float(np.max(np.abs(Pj@Pj-Pj)))
    annih=float(max(np.max(np.abs(Ps@Pj)),np.max(np.abs(Pj@Ps))))
    fig,axes=plt.subplots(1,3,figsize=(12.7,4.0))
    for a,Mm,title in zip(axes,[np.real(Pj),np.real(Ps),np.real(Ps@Pj)], ["edge projector $P_J$","complement $P_S$","annihilation $P_SP_J$"]):
        im=a.imshow(Mm,cmap="coolwarm",aspect="auto"); a.set_title(title,weight="bold",fontsize=11); a.set_xticks([]); a.set_yticks([]); fig.colorbar(im,ax=a,fraction=.046)
    fig.suptitle(f"Finite projector certificates: idempotence {idem:.2e}, annihilation {annih:.2e}",fontsize=15.5,weight="bold")
    fig.tight_layout(rect=[0,0,1,.90])
    savefig(fig,"34_projector_matrices")

    # 35 theorem dependency ladder
    fig,ax=plt.subplots(figsize=(10.0,8.0)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    labels=["seed decomposition","exact Fourier coefficients","Gibbs asymptotic","edge functional","packet projectors","smooth/edge synthesis","no-Gibbs theorem","finite discovery","robustness certificates"]
    ys=np.linspace(.91,.09,len(labels))
    for i,(lab,yy) in enumerate(zip(labels,ys,strict=True)):
        box(ax,(.25,yy-.035),.50,.07,lab,face="#EFF6FF" if i<3 else "#ECFDF5",fontsize=11)
        if i<len(labels)-1: arrow(ax,(.5,yy-.035),(.5,ys[i+1]+.035))
    ax.text(.5,.98,"Dependency order of the closed proof",ha="center",fontsize=19,weight="bold")
    savefig(fig,"35_theorem_dependency_ladder")

    # 36 certificate dashboard
    coeff_errors=[abs(numerical_continuous_coefficient(k)-fhat_continuous(k)) for k in range(-12,13)]
    cert_rows=[
        ("analytic coefficient quadrature",max(coeff_errors)),
        ("edge projector idempotence",idem),
        ("packet annihilation",annih),
        ("smooth packet reconstruction",smooth_resid),
        ("full packet reconstruction",exact_resid),
        ("Haar mask reconstruction",float(np.max(np.abs(mask_haar_rec-m)))),
        ("dictionary true residual",rows[0]["residual_l2"]),
        ("dictionary wrong-model gap",wrong_gap),
    ]
    fig,ax=plt.subplots(figsize=(11.5,6.3)); ax.axis("off")
    ax.text(.5,.94,"Closed-work certificate dashboard",ha="center",fontsize=20,weight="bold",transform=ax.transAxes)
    y0=.84
    for i,(name,val) in enumerate(cert_rows):
        bg="#F8FAFC" if i%2==0 else "#EEF2FF"
        ax.add_patch(Rectangle((.07,y0-.035),.86,.055,facecolor=bg,edgecolor="none",transform=ax.transAxes))
        ax.text(.09,y0,name,ha="left",va="center",transform=ax.transAxes,fontsize=11)
        ax.text(.90,y0,f"{val:.6e}",ha="right",va="center",transform=ax.transAxes,fontsize=11,family="monospace")
        y0-=.075
    ax.text(.5,.08,"Small algebraic residuals certify the implemented identities; the positive dictionary gap certifies uniqueness of the finite model selection.",ha="center",transform=ax.transAxes,fontsize=10.5)
    savefig(fig,"36_certificate_dashboard")

    # 37 direct source code architecture
    fig,ax=plt.subplots(figsize=(12.0,5.7)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    blocks=[(.04,"definitions"),(.20,"closed forms"),(.36,"projectors"),(.52,"experiments"),(.68,"figures/tables"),(.84,"TeX/PDF")]
    for xx,lab in blocks: box(ax,(xx,.43),.12,.16,lab,face="#F1F5F9",fontsize=10.5)
    for i in range(len(blocks)-1): arrow(ax,(blocks[i][0]+.12,.51),(blocks[i+1][0],.51))
    ax.text(.5,.86,"One Python file regenerates the entire mathematical artifact",ha="center",fontsize=20,weight="bold")
    ax.text(.5,.22,"Assertions are executed before the manuscript is written; a failed identity stops the build.",ha="center",fontsize=12)
    savefig(fig,"37_single_file_architecture")

    # 38 final synthesis visual
    fig,axes=plt.subplots(2,2,figsize=(12.6,7.0),sharex=True,sharey=True)
    panels=[("exact signal",x),("global Fourier",global40),("edge packet",j_rec),("final synthesis",rec_exact)]
    for a,(title,yy) in zip(axes.ravel(),panels,strict=True):
        a.plot(t,yy,lw=1.8); a.axvline(ALPHA,ls="--",lw=.8); a.axvline(BETA,ls="--",lw=.8); a.set_title(title,weight="bold"); a.grid(alpha=.16)
    for a in axes[-1]: a.set_xlabel("$t$")
    for a in axes[:,0]: a.set_ylabel("amplitude")
    fig.suptitle("The discontinuity is reconstructed as a declared object, not as the limit of oscillatory global modes",fontsize=16,weight="bold")
    fig.tight_layout(rect=[0,0,1,.92])
    savefig(fig,"38_final_synthesis")

    # 39 summary wheel
    fig,ax=plt.subplots(figsize=(7.5,7.5)); ax.set_aspect("equal"); ax.axis("off")
    labels=["seed","Fourier failure","edge address","analysis","projectors","smooth transfer","exact edge","synthesis","residual"]
    angles=np.linspace(0,2*np.pi,len(labels),endpoint=False)
    for idx,(lab,ang) in enumerate(zip(labels,angles,strict=True)):
        xx=.78*np.cos(ang); yy=.78*np.sin(ang)
        ax.add_patch(FancyBboxPatch((xx-.13,yy-.055),.26,.11,boxstyle="round,pad=.012,rounding_size=.02",facecolor="#DBEAFE" if idx<2 else "#D1FAE5",edgecolor="#334155"))
        ax.text(xx,yy,lab,ha="center",va="center",fontsize=10,weight="bold")
        nxt=angles[(idx+1)%len(labels)]; arrow(ax,(.66*np.cos(ang),.66*np.sin(ang)),(.66*np.cos(nxt),.66*np.sin(nxt)),color="#64748B",rad=.18)
    ax.add_patch(plt.Circle((0,0),.30,facecolor="white",edgecolor="#334155",lw=1.6))
    ax.text(0,.04,"singularity-exact",ha="center",fontsize=14,weight="bold"); ax.text(0,-.07,"reconstruction",ha="center",fontsize=17,weight="bold")
    ax.set_xlim(-1.1,1.1); ax.set_ylim(-1.1,1.1); ax.set_title("The complete closed calculus for this example",fontsize=18,weight="bold",pad=14)
    savefig(fig,"39_summary_wheel")

    # Tables
    def write_csv(name: str, rows_data: Sequence[dict]) -> None:
        if not rows_data: return
        with (TAB/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows_data[0].keys())); w.writeheader(); w.writerows(rows_data)
    write_csv("overshoot_convergence.csv",overshoot_rows)
    write_csv("filter_error_metrics.csv",metric_rows)
    write_csv("interval_dictionary_ranking.csv",rows)
    write_csv("noise_stability.csv",noise_rows)
    write_csv("amplitude_noise.csv",amp_rows)
    write_csv("endpoint_perturbation.csv",pert_rows)
    write_csv("total_variation.csv",tv_rows)
    coeff_rows=[]
    for k in range(-16,17):
        coeff_rows.append({"k":k,"smooth_real":shat_continuous(k).real,"smooth_imag":shat_continuous(k).imag,"mask_real":mhat_continuous(k).real,"mask_imag":mhat_continuous(k).imag,"signal_real":fhat_continuous(k).real,"signal_imag":fhat_continuous(k).imag})
    write_csv("closed_form_coefficients.csv",coeff_rows)

    # Assertions. Keep a count so the manuscript reports exactly what ran.
    assertions=0
    def check(cond: bool,msg: str) -> None:
        nonlocal assertions
        assertions+=1
        if not cond: raise AssertionError(msg)
    check(max(coeff_errors)<2e-10,"analytic coefficients disagree with quadrature")
    check(abs(GIBBS_CONSTANT-0.0894898722360835)<1e-14,"Gibbs constant")
    check(idem<2e-12,"edge projector idempotence")
    check(annih<2e-12,"packet annihilation")
    check(exact_resid<5e-12,"exact discrete reconstruction")
    check(smooth_resid<5e-12,"smooth packet reconstruction")
    check(abs(a_est-AMP)<5e-12,"edge amplitude")
    check(best==(4,12),"finite interval discovery")
    check(rows[0]["residual_l2"]<1e-10,"true dictionary residual")
    check(wrong_gap>1e-4,"positive wrong-model gap")
    check(all((r["found_i"],r["found_j"])==(4,12) for r in noise_rows if r["fraction_of_gap"]<.5),"noise stability below half-gap")
    check(np.max(np.abs(mask_haar_rec-m))<5e-12,"Haar mask reconstruction")
    check(nonzero<40,"Haar sparsity")
    check(abs(overshoot_rows[-1]["relative_overshoot"]-GIBBS_CONSTANT)<2e-4,"Gibbs overshoot convergence")
    check(abs(pert_rows[-1]["l2_normalized"]-pert_rows[-1]["theory"])<1e-12,"endpoint error equality")
    check(linf(rw,x)>1e-3,"wrong packet negative control")
    check(np.max(np.abs((Ps+Pj)-np.eye(nsmall)))<2e-12,"projector completeness")
    check(np.max(np.abs(Ps@Ps-Ps))<2e-12,"smooth projector idempotence")
    check(np.max(np.abs(lowpass_discrete(s,SMOOTH_DEGREE)-s))<5e-12,"smooth degree certificate")
    check(abs(tv_rows[0]["packet_tv"]-tv_exact)<1e-10,"packet total variation")

    figure_pairs=len(list(FIG.glob("*.pdf")))
    check(figure_pairs==39,"expected figure count")

    cert=Certificate(
        analytic_coefficient_max_error=float(max(coeff_errors)),
        gibbs_constant=GIBBS_CONSTANT,
        edge_projector_idempotence=idem,
        edge_projector_annihilation=annih,
        exact_reconstruction_residual=exact_resid,
        smooth_packet_residual=smooth_resid,
        discovered_interval_i=best[0],
        discovered_interval_j=best[1],
        dictionary_wrong_gap=wrong_gap,
        noise_norm=float(noise_rows[4]["noise_norm"]),
        noise_stability_margin=float(wrong_gap/2-noise_rows[4]["noise_norm"]),
        haar_mask_nonzero_coefficients=nonzero,
        haar_mask_reconstruction_residual=float(np.max(np.abs(mask_haar_rec-m))),
        figure_pairs=figure_pairs,
        assertions=assertions,
    )
    (RES/"certificate.json").write_text(json.dumps(asdict(cert),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return cert

# ---------------------------------------------------------------------------
# Manuscript and release generation. The same single file writes everything.
# ---------------------------------------------------------------------------
def latex_escape(text: str) -> str:
    repl = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_"}
    for a, b in repl.items():
        text = text.replace(a, b)
    return text


def write_latex_tables() -> None:
    overs = list(csv.DictReader((TAB / "overshoot_convergence.csv").open(encoding="utf-8")))
    lines = [r"\begin{longtable}{rrrrr}", r"\toprule", r"$N$ & maximizer $t_N$ & relative overshoot & absolute overshoot & distance to $G$\\", r"\midrule", r"\endfirsthead", r"\toprule", r"$N$ & maximizer $t_N$ & relative overshoot & absolute overshoot & distance to $G$\\", r"\midrule", r"\endhead"]
    for row in overs:
        lines.append(f"{int(float(row['N']))} & {float(row['location']):.10f} & {float(row['relative_overshoot']):.10f} & {float(row['absolute_overshoot']):.10f} & {float(row['distance_to_limit']):.3e}\\\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (TAB / "overshoot_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    ranking = list(csv.DictReader((TAB / "interval_dictionary_ranking.csv").open(encoding="utf-8")))[:15]
    lines = [r"\begin{longtable}{rrrrr}", r"\toprule", r"$i$ & $j$ & interval & residual norm & fitted amplitude\\", r"\midrule", r"\endfirsthead", r"\toprule", r"$i$ & $j$ & interval & residual norm & fitted amplitude\\", r"\midrule", r"\endhead"]
    for row in ranking:
        i, j = int(float(row["i"])), int(float(row["j"]))
        lines.append(f"{i} & {j} & $[{i}/16,{j}/16)$ & {float(row['residual_l2']):.6e} & {float(row['amplitude']):.10f}\\\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (TAB / "dictionary_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    coeff = list(csv.DictReader((TAB / "closed_form_coefficients.csv").open(encoding="utf-8")))
    coeff = [r for r in coeff if -11 <= int(r["k"]) <= 11]
    lines = [r"\begin{longtable}{r r@{\,}l r@{\,}l r@{\,}l}", r"\toprule", r"$k$ & \multicolumn{2}{c}{$\widehat s(k)$} & \multicolumn{2}{c}{$\widehat m(k)$} & \multicolumn{2}{c}{$\widehat f(k)$}\\", r"\midrule", r"\endfirsthead", r"\toprule", r"$k$ & \multicolumn{2}{c}{$\widehat s(k)$} & \multicolumn{2}{c}{$\widehat m(k)$} & \multicolumn{2}{c}{$\widehat f(k)$}\\", r"\midrule", r"\endhead"]
    for r in coeff:
        def cfmt(re: float, im: float) -> tuple[str, str]:
            return f"{re:.8f}", f"{im:+.8f}i"
        sr, si = cfmt(float(r["smooth_real"]), float(r["smooth_imag"]))
        mr, mi = cfmt(float(r["mask_real"]), float(r["mask_imag"]))
        fr, fi = cfmt(float(r["signal_real"]), float(r["signal_imag"]))
        lines.append(f"{int(r['k'])} & {sr} & {si} & {mr} & {mi} & {fr} & {fi}\\\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (TAB / "coefficient_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def visual_page(title: str, file: str, callout: str, label: str = "") -> str:
    escaped_callout = callout
    return rf"""
\VisualPage{{{title}}}{{{file}}}{{{escaped_callout}}}{{{label}}}
"""


def write_tex(cert: Certificate) -> Path:
    V: list[str] = []
    add = V.append
    add(r"""\documentclass[11pt,oneside]{book}
\usepackage[letterpaper,margin=0.82in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern,microtype}
\usepackage{amsmath,amssymb,amsthm,mathtools}
\usepackage{graphicx,float,booktabs,longtable,tabularx,array}
\usepackage{xcolor,hyperref,fancyhdr,enumitem,listings,placeins}
\definecolor{Ink}{HTML}{17202A}
\definecolor{Blue}{HTML}{2E86AB}
\definecolor{Teal}{HTML}{2A9D8F}
\definecolor{Orange}{HTML}{E76F51}
\definecolor{PaleBlue}{HTML}{EAF3F8}
\definecolor{PaleTeal}{HTML}{E8F5F2}
\definecolor{PaleOrange}{HTML}{FCEFEA}
\hypersetup{colorlinks=true,hypertexnames=false,linkcolor=Blue,urlcolor=Blue,citecolor=Blue,pdftitle={Singularity-Exact Reconstruction: A Closed Projector-Resolved Circumvention of the Gibbs Phenomenon},pdfauthor={Komorebi P.},pdfsubject={Projector-resolved Fourier reconstruction and exact singularity packets},pdfcreator={},pdfproducer={}}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}\fancyfoot[L]{\scriptsize\color{gray} Singularity-Exact Reconstruction}\fancyfoot[R]{\scriptsize\color{gray}\thepage}
\setlength{\parindent}{0pt}\setlength{\parskip}{5.5pt}\setlength{\emergencystretch}{3em}\raggedbottom
\setlist[itemize]{leftmargin=1.4em,itemsep=2pt}\setlist[enumerate]{leftmargin=1.8em,itemsep=3pt}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\newtheorem{theorem}{Theorem}[chapter]\newtheorem{proposition}[theorem]{Proposition}\newtheorem{lemma}[theorem]{Lemma}\newtheorem{corollary}[theorem]{Corollary}\newtheorem{definition}[theorem]{Definition}
\theoremstyle{remark}\newtheorem{remark}[theorem]{Remark}\newtheorem{boundary}[theorem]{Boundary}\newtheorem{certificate}[theorem]{Certificate}
\newcommand{\Torus}{\mathbb T}\newcommand{\C}{\mathbb C}\newcommand{\R}{\mathbb R}\newcommand{\Z}{\mathbb Z}\newcommand{\norm}[1]{\left\lVert#1\right\rVert}\newcommand{\ip}[2]{\left\langle#1,#2\right\rangle}
\newcommand{\Callout}[1]{\noindent\colorbox{PaleBlue}{\parbox{0.955\linewidth}{\small\vspace{3pt}#1\vspace{3pt}}}}
\newcommand{\ExactBox}[1]{\noindent\colorbox{PaleTeal}{\parbox{0.955\linewidth}{\small\textbf{Exact statement.} #1}}}
\newcommand{\BoundaryBox}[1]{\noindent\colorbox{PaleOrange}{\parbox{0.955\linewidth}{\small\textbf{Boundary.} #1}}}
\newcommand{\VisualPage}[4]{\clearpage\section{#1}\begin{center}\includegraphics[width=0.96\textwidth,height=0.61\textheight,keepaspectratio]{figures/#2}\end{center}\Callout{#3}\ifx\relax#4\relax\else\label{#4}\fi}
\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,showstringspaces=false,frame=single,columns=fullflexible,tabsize=4}
\graphicspath{{figures/}}
\begin{document}
\begin{titlepage}
\centering\vspace*{0.55in}
{\Large\color{Blue}\bfseries PROJECTOR-RESOLVED SEED CALCULUS\par}\vspace{0.18in}
{\Huge\bfseries Singularity-Exact Reconstruction\par}\vspace{0.12in}
{\LARGE\bfseries A Closed Projector-Resolved Circumvention of the Gibbs Phenomenon\par}\vspace{0.25in}
{\Large One signal, one discontinuity packet, every derivation, every residual, and one executable source file\par}
\vfill
\begin{minipage}{0.82\textwidth}\large
The classical Fourier partial sums of a discontinuous signal develop a boundary layer whose limiting relative overshoot is nonzero.  The construction in this monograph does not attempt to cancel that layer after it has formed.  It changes the representation: the jump is recovered as an exact packet, the smooth complement is treated spectrally, and synthesis recombines the two without asking global Fourier modes to approximate the discontinuity.
\end{minipage}
\vfill
{\Large Komorebi P.\par}\vspace{0.35in}
\end{titlepage}
\frontmatter
\chapter*{Abstract}\addcontentsline{toc}{chapter}{Abstract}
This monograph follows one periodic signal from its primitive seed to its final reconstruction.  The signal is
\[
f(t)=s(t)+\frac54\mathbf 1_{[1/4,3/4)}(t),\qquad t\in\Torus=\R/\Z,
\]
where
\[
s(t)=\frac13\cos(2\pi t)+\frac14\sin(6\pi t)-\frac15\cos(10\pi t).
\]
The global Fourier partial sums are computed in closed form and shown to exhibit the classical Gibbs boundary layer.  A finite family of out-of-band Fourier coordinates then defines an exact edge-amplitude functional.  That functional generates an idempotent singularity projector $P_J$ and a complementary smooth projector $P_S=I-P_J$.  The reconstruction operator
\[
\mathcal R_5=Q_5P_S+P_J
\]
is proved to be the identity on the declared model space.  Consequently the jump is retained exactly, the smooth packet is reconstructed exactly from five Fourier frequencies, and the full residual vanishes to floating-point roundoff in the finite implementation.

The document includes the Dirichlet-kernel derivation of the Gibbs constant, a finite dyadic interval-discovery theorem, noise and endpoint-perturbation certificates, negative controls, polyphase refinement, Haar sparsity, complete tables, and the entire executable source.  All results are regenerated by one Python file.  The exact conclusion is model-relative: the construction proves how Gibbs ringing is circumvented when the singular geometry is represented as a packet or is correctly selected from the declared finite dictionary.  It does not assert automatic recovery of arbitrary unknown discontinuities.

\chapter*{Claim boundary}\addcontentsline{toc}{chapter}{Claim boundary}
\ExactBox{For the model space $X=\mathcal S_5\oplus\operatorname{span}\{m\}$, with $m=\mathbf1_{[1/4,3/4)}$, the packet projectors and reconstruction operator are exact.  The finite grid implementation reproduces the signal with maximum residual below $10^{-15}$.}

\BoundaryBox{This is not a theorem that one fixed packet system removes Gibbs ringing from every nonsmooth function.  Exact circumvention requires the correct singular packet, or a recovery theorem for a declared model class.  Spectral filters, wavelets, and edge estimators remain useful but logically distinct tools.}

The phrase ``circumventing Gibbs'' is used precisely: the discontinuity is removed from the global approximation task and retained as an exact reconstruction packet.  It is not hidden by smoothing and it is not claimed that the classical Fourier theorem is false.

\chapter*{Reading map}\addcontentsline{toc}{chapter}{Reading map}
\begin{enumerate}
\item Part~I derives the classical obstruction from the exact Fourier coefficients and Dirichlet kernel.
\item Part~II constructs the packet projectors and proves singularity-exact synthesis.
\item Part~III resolves the same packet through dyadic, polyphase, and Haar coordinates.
\item Part~IV proves finite dictionary discovery and robustness bounds.
\item Part~V collects negative controls, complexity comparisons, and the exact logical boundary.
\item The appendices contain the complete coefficient tables, numerical records, and the single-file implementation.
\end{enumerate}
\tableofcontents
\mainmatter

\part{The one signal and the classical obstruction}
\chapter{The primitive seed}
\section{The ambient object}
Work on the one-dimensional torus $\Torus=\R/\Z$ with Fourier convention
\[
\widehat g(k)=\int_0^1g(t)e^{-2\pi ikt}\,dt,
\qquad
g(t)\sim\sum_{k\in\Z}\widehat g(k)e^{2\pi ikt}.
\]
The primitive data are the smooth seed $s$, the interval address
\[
\Omega=[1/4,3/4),
\]
and the jump amplitude $a=5/4$.  Put
\[
m=\mathbf1_\Omega,
\qquad
j=am,
\qquad
f=s+j.
\]
This is a single typed seed system: $s$ lies in a finite Fourier subspace, while $j$ lies in a one-dimensional geometric packet space.

\section{Why the decomposition matters}
The discontinuity is not an accidental perturbation of the smooth signal.  It changes the asymptotic decay of the Fourier coefficients from finite support to $1/|k|$.  A global Fourier truncation therefore spends arbitrarily many modes representing the boundary of $\Omega$.  The packet method keeps the geometry of $\Omega$ as data and reserves Fourier modes for $s$.

\begin{definition}[Smooth and singular seed spaces]
Let
\[
\mathcal S_5=\operatorname{span}\{e^{2\pi ikt}:|k|\le5\},
\qquad
X=\mathcal S_5\oplus\operatorname{span}\{m\}.
\]
The direct sum is algebraic: $m\notin\mathcal S_5$ because $m$ has infinitely many nonzero Fourier coefficients.
\end{definition}
""")
    add(visual_page("The complete closed pipeline", "01_closed_pipeline.pdf", "The same typed object is carried through global Fourier analysis, edge identification, complementary projectors, smooth spectral transfer, and exact synthesis.  The red branch records the classical failure; the green branch is the exact reconstruction route."))
    add(visual_page("The primitive seed split", "02_seed_decomposition.pdf", "The one worked example never changes.  The smooth trigonometric polynomial, the interval packet, and their sum are the only signal objects used throughout the monograph."))

    add(r"""\chapter{Closed Fourier coefficients}
\section{The smooth packet}
The Fourier coefficients of $s$ are finite:
\[
\widehat s(\pm1)=\frac16,
\qquad
\widehat s(3)=-\frac{i}{8},
\qquad
\widehat s(-3)=\frac{i}{8},
\qquad
\widehat s(\pm5)=-\frac1{10},
\]
and every other coefficient vanishes.

\section{The interval packet}
For $k\ne0$,
\begin{align*}
\widehat m(k)
&=\int_{1/4}^{3/4}e^{-2\pi ikt}\,dt\\
&=e^{-\pi ik}\frac{\sin(\pi k/2)}{\pi k}\\
&=(-1)^k\frac{\sin(\pi k/2)}{\pi k},
\end{align*}
while $\widehat m(0)=1/2$.  Thus every nonzero even coefficient vanishes and every odd coefficient has magnitude $1/(\pi|k|)$.

\begin{proposition}[Exact signal coefficients]
For every $k\in\Z$,
\[
\boxed{\widehat f(k)=\widehat s(k)+\frac54\widehat m(k).}
\]
For $|k|>5$, this reduces to
\[
\widehat f(k)=\frac54\widehat m(k).
\]
\end{proposition}
\begin{proof}
Linearity of the Fourier integral gives the first identity.  The second follows from the finite support of $\widehat s$.
\end{proof}

\section{The spectral signature of the jump}
The out-of-band coefficients are not noise in this model.  They form a one-parameter family with known shape and unknown amplitude.  That observation is the seed of the singularity projector constructed later.
""")
    add(visual_page("Exact Fourier coefficient packets", "03_exact_fourier_coefficients.pdf", r"The smooth seed occupies only frequencies $\pm1,\pm3,\pm5$.  Outside that set, every nonzero coefficient belongs to the interval packet and is proportional to one scalar amplitude."))

    add(r"""\chapter{Global Fourier reconstruction}
\section{Partial sums}
Let
\[
Q_Ng(t)=\sum_{|k|\le N}\widehat g(k)e^{2\pi ikt}.
\]
For every $N\ge5$,
\[
Q_Nf=s+\frac54Q_Nm,
\]
so the global error is
\[
\boxed{f-Q_Nf=\frac54(m-Q_Nm).}
\]
Once the smooth degree has been reached, every remaining global error is caused by representing the interval packet with global Fourier modes.

\section{What increasing \texorpdfstring{$N$}{N} does}
Increasing $N$ narrows the region in which $Q_Nm$ oscillates.  It does not force the maximum overshoot, normalized by the jump height, to zero.  That distinction between width and height is the essential content of the Gibbs phenomenon.
""")
    add(visual_page("Global Fourier partial sums", "04_global_fourier_partial_sums.pdf", "The boundary layer becomes visually narrower as the cutoff grows, but the first overshoot remains a fixed fraction of the jump height."))
    add(visual_page("Boundary-layer zoom", "05_boundary_layer_zoom.pdf", "The oscillations localize around the upward and downward jumps.  Away from the jumps the convergence is rapid; the obstruction is boundary-localized."))

    add(r"""\chapter{The Dirichlet kernel and the Gibbs constant}
\section{Convolution form}
The Dirichlet kernel on $\Torus$ is
\[
D_N(t)=\sum_{k=-N}^Ne^{2\pi ikt}
=\frac{\sin((2N+1)\pi t)}{\sin(\pi t)}.
\]
The partial sum is convolution:
\[
Q_Ng(t)=\int_0^1g(u)D_N(t-u)\,du.
\]
The central peak of $D_N$ becomes narrower with $N$, but its signed side lobes do not form a positive approximate identity.

\section{Local scaling at a jump}
Consider a unit upward jump at $t=\alpha$.  Set
\[
t_N(y)=\alpha+\frac{y}{(2N+1)\pi}.
\]
After substituting $v=z/((2N+1)\pi)$ in the local convolution integral, one obtains the limiting profile
\[
\boxed{
\lim_{N\to\infty}Q_NH(t_N(y))
=\frac{1}{2}+\frac1\pi\operatorname{Si}(y),
}
\]
where
\[
\operatorname{Si}(y)=\int_0^y\frac{\sin z}{z}\,dz.
\]

\begin{theorem}[Gibbs overshoot constant]
The first limiting maximum occurs at $y=\pi$.  Its value is
\[
\frac12+\frac1\pi\operatorname{Si}(\pi)=1+G,
\]
where
\[
\boxed{G=\frac{\operatorname{Si}(\pi)}{\pi}-\frac12
=0.0894898722360835\ldots.}
\]
For a jump of height $a$, the limiting absolute overshoot is $Ga$.
\end{theorem}
\begin{proof}
Differentiate the limiting profile.  Its derivative is $\sin y/(\pi y)$, whose first positive zero occurs at $y=\pi$.  The derivative is positive on $(0,\pi)$ and negative immediately after $\pi$, so this is the first maximum.  Evaluation gives the displayed constant.  Linearity scales the profile by the jump height.
\end{proof}
""")
    add(visual_page("Universal scaled Gibbs profile", "06_scaled_gibbs_profile.pdf", "The normalized local profile is independent of the smooth background and depends only on the jump height.  The first maximum gives the universal constant $G$."))
    add(visual_page("Overshoot convergence", "07_overshoot_convergence.pdf", "The measured overshoot converges to $G$ rather than to zero.  More modes reduce the spatial width of the boundary layer, not its limiting relative height."))
    add(visual_page("Dirichlet-kernel geometry", "08_dirichlet_kernel.pdf", "The side lobes of the Dirichlet kernel are the mechanism that mixes information across the jump.  Their signed mass is not removed by increasing the cutoff."))

    add(r"""\chapter{Why filtering is a different operation}
\section{Filtered spectral sums}
Fejer, Lanczos, and exponential filters replace the sharp cutoff by frequency weights.  They can suppress visible ringing, and positive kernels such as the Fejer kernel avoid the classical overshoot in many step examples.  They do so by broadening the transition region and changing the approximation operator.

\section{The exact distinction}
A filtered approximation still asks one global spectral representation to encode both $s$ and $j$.  The packet construction instead stores $j$ as an exact object.  Therefore smoothing and exact singularity retention should not be described as the same mechanism.

\begin{boundary}[No claim of exclusivity]
The projector construction is not claimed to be the only useful treatment of discontinuities.  Spectral filtering, Gegenbauer reconstruction, ENO/WENO methods, adaptive meshes, wavelets, and domain decomposition solve related problems under different assumptions.  The present claim is narrower and exact: once the singular packet is declared, its Fourier tail no longer contributes to the approximation error.
\end{boundary}
""")
    add(visual_page("Filtered Fourier baselines", "09_spectral_filters.pdf", "Filtering trades oscillatory overshoot for a wider transition layer.  The edge geometry is still implicit in the global coefficient field."))
    add(visual_page("Filtered error profiles", "10_filter_error_profiles.pdf", "The filters redistribute error near the boundary.  None of these global reconstructions equals the declared half-open interval packet at finite cutoff."))

    add(r"""\part{The projector-resolved circumvention}
\chapter{An edge functional from out-of-band modes}
\section{Choice of identifying frequencies}
Choose a finite symmetric set
\[
K\subset\{k\in\Z:|k|>5,\ k\text{ odd}\}.
\]
For every $k\in K$, $\widehat s(k)=0$ and $\widehat m(k)\ne0$.  Define
\[
\ell_K(g)=
\frac{\sum_{k\in K}\overline{\widehat m(k)}\widehat g(k)}
{\sum_{k\in K}|\widehat m(k)|^2}.
\]

\begin{theorem}[Exact amplitude recovery]
For every $g=s_0+bm\in X$ with $s_0\in\mathcal S_5$,
\[
\boxed{\ell_K(g)=b.}
\]
\end{theorem}
\begin{proof}
For $k\in K$, $\widehat g(k)=b\widehat m(k)$.  Therefore the numerator is
\[
b\sum_{k\in K}|\widehat m(k)|^2,
\]
which cancels the denominator.
\end{proof}

\section{Why several modes are used}
A single nonzero out-of-band coefficient already identifies $b$ in exact arithmetic.  The least-squares combination above uses all selected modes and exposes the noise amplification explicitly.  By Cauchy--Schwarz,
\[
|\ell_K(\eta)|
\le
\frac{\left(\sum_{k\in K}|\widehat\eta(k)|^2\right)^{1/2}}
{\left(\sum_{k\in K}|\widehat m(k)|^2\right)^{1/2}}.
\]
This is a stability certificate, not a claim that high-frequency noise is harmless.
""")
    add(visual_page("Modes used by the edge functional", "11_edge_functional_modes.pdf", "All selected frequencies lie outside the smooth seed band.  Their known coefficient pattern turns the edge-amplitude problem into a one-dimensional projection."))

    add(r"""\chapter{The singularity projector}
\begin{definition}[Edge and smooth projectors]
For $g$ in the ambient finite-energy space, define
\[
P_Jg=\ell_K(g)m,
\qquad
P_Sg=g-P_Jg.
\]
\end{definition}

\begin{theorem}[Projector algebra]
The operators satisfy
\[
\boxed{
P_J^2=P_J,
\qquad
P_S^2=P_S,
\qquad
P_SP_J=P_JP_S=0,
\qquad
P_S+P_J=I.
}
\]
On $X=\mathcal S_5\oplus\operatorname{span}\{m\}$,
\[
P_J(s_0+bm)=bm,
\qquad
P_S(s_0+bm)=s_0.
\]
\end{theorem}
\begin{proof}
The amplitude theorem gives $\ell_K(m)=1$.  Hence
\[
P_J^2g=\ell_K(g)\ell_K(m)m=P_Jg.
\]
The remaining algebra follows from $P_S=I-P_J$.  The formulas on $X$ use $\ell_K(s_0)=0$ and $\ell_K(bm)=b$.
\end{proof}

\begin{remark}
$P_J$ is generally oblique rather than orthogonal in $L^2(\Torus)$.  Orthogonality is not required for exact analysis and synthesis; idempotence, annihilation, and completeness are the relevant algebraic properties here.
\end{remark}
""")
    add(visual_page("Projector analysis and synthesis", "12_projector_pipeline.pdf", "The observed signal is split into a geometric packet and a smooth packet.  The jump is never sent through the global low-pass approximation operator."))
    add(visual_page("Recovered smooth and singular packets", "13_recovered_packets.pdf", "The out-of-band functional recovers $a=5/4$, leaving a degree-five smooth packet.  Both components match their declared seeds to floating-point roundoff."))

    add(r"""\chapter{The singularity-exact reconstruction theorem}
Let $Q_5$ be the Fourier projector onto $\mathcal S_5$ and define
\[
\mathcal R_5=Q_5P_S+P_J.
\]

\begin{theorem}[Exact reconstruction on the model space]
For every $g\in X$,
\[
\boxed{\mathcal R_5g=g.}
\]
\end{theorem}
\begin{proof}
Write $g=s_0+bm$.  The projector theorem gives $P_Sg=s_0$ and $P_Jg=bm$.  Since $s_0\in\mathcal S_5$, $Q_5s_0=s_0$.  Therefore
\[
\mathcal R_5g=Q_5s_0+bm=s_0+bm=g.
\]
\end{proof}

\begin{corollary}[The Gibbs term is absent]
For the chosen signal,
\[
f-\mathcal R_5f=0.
\]
By contrast, for $N\ge5$,
\[
f-Q_Nf=\frac54(m-Q_Nm),
\]
which retains the entire jump-approximation error.
\end{corollary}

\begin{theorem}[General singularity-exact error identity]
Let $s$ be any periodic function for which $Q_Ns$ is defined, and let $j$ be a declared exact packet.  If analysis returns $P_Sf=s$ and $P_Jf=j$, then
\[
\boxed{
f-(Q_NP_Sf+P_Jf)=s-Q_Ns.
}
\]
Thus all convergence rates and pointwise behavior are inherited from the smooth packet alone.
\end{theorem}
\begin{proof}
Substitute $f=s+j$ and use exact packet recovery:
\[
f-(Q_Ns+j)=s-Q_Ns.
\]
\end{proof}

\section{What has actually been circumvented}
The classical Gibbs theorem remains intact.  The global Fourier approximation $Q_Nf$ still rings.  The reconstruction operator has changed because the object has been resolved into two packets with different synthesis laws.  The discontinuity is reconstructed from its geometric address and amplitude, not from a truncated global Fourier series.
""")
    add(visual_page("Global and packet reconstructions", "14_global_vs_packet_reconstruction.pdf", "The upper panel retains the classical boundary layer.  The lower panel overlays the exact signal because the smooth and singular packets are synthesized by different exact operators."))
    add(visual_page("Residual comparison", "15_residual_comparison.pdf", "The global residual is concentrated near the jumps.  The packet residual is at floating-point roundoff across the whole period."))
    add(visual_page("Whole-domain and boundary-band rates", "16_error_rates.pdf", "The packet error is the smooth spectral error only.  In the chosen degree-five model, that error is zero once the declared smooth band is retained."))
    add(visual_page("Pointwise boundary error", "17_boundary_error_log.pdf", "On a logarithmic scale the contrast is explicit: the global method has an $O(1)$ boundary layer, while the packet reconstruction remains at numerical roundoff."))
    add(visual_page("First-difference structure", "18_first_difference_comparison.pdf", "The exact packet retains two localized jump events.  The global partial sum replaces them with oscillatory boundary differences."))

    add(r"""\part{Refinement and alternative exact atlases}
\chapter{Dyadic spatial refinement}
The interval $[1/4,3/4)$ is aligned with the level-two dyadic partition.  Let
\[
I_{2,r}=[r/4,(r+1)/4),\qquad r=0,1,2,3.
\]
Then
\[
\boxed{
m=\mathbf1_{I_{2,1}}+\mathbf1_{I_{2,2}}.
}
\]
This is an exact packet refinement: the parent interval is reconstructed from two disjoint child packets.  No Fourier approximation is involved in this identity.

On the grid, residue and polyphase projectors can further split each spatial packet by sample address.  Interleaving all phases reconstructs the mask exactly.
""")
    add(visual_page("Dyadic refinement tree", "19_dyadic_refinement_tree.pdf", "The singularity address is already exact at level two.  Refinement may continue inside the selected quarters without altering the external reconstruction contract."))
    add(visual_page("Polyphase packets of the interval mask", "20_mask_polyphase_packets.pdf", "Each sample belongs to exactly one phase channel.  The phase channels are sparse views of one exact geometric packet and synthesize by interleaving."))

    add(r"""\chapter{Haar coordinates for the same packet}
The Haar transform provides another exact atlas.  Because both boundaries are dyadically aligned, the interval mask has only three nonzero Haar coefficients in the length-$512$ implementation.  Full inverse Haar synthesis reconstructs the mask exactly.

This comparison explains why wavelets often handle discontinuities more economically than global Fourier modes: localization changes coefficient concentration.  The projector solution goes one step further in the declared model by treating the interval geometry itself as a packet rather than merely as a sparse transform pattern.
""")
    add(visual_page("Haar sparsity of the interval packet", "21_haar_sparsity.pdf", f"The exact mask has only {cert.haar_mask_nonzero_coefficients} nonzero Haar coefficients on the dyadically aligned grid.  The same mask has an infinite $1/|k|$ Fourier tail in the continuum."))
    add(visual_page("Exact inverse-Haar reconstruction", "22_haar_mask_reconstruction.pdf", "The Haar atlas is exact when all required coefficients are retained.  Thresholding and best-basis selection are separate approximation decisions."))
    add(visual_page("Fourier versus Haar concentration", "23_fourier_haar_concentration.pdf", "This is not a universal wavelet-dominance theorem.  It is a coordinate concentration statement for the one interval packet used throughout the monograph."))

    add(r"""\part{Finite discovery and robustness}
\chapter{Recovering the interval from a finite dictionary}
So far the packet address $\Omega$ has been declared.  The same example can also support a finite exact discovery theorem.

Let $\mathcal D$ be the set of intervals
\[
\Omega_{ij}=[i/16,j/16),\qquad 0\le i<j\le16,
\]
subject to a minimum width of two cells.  For each candidate define
\[
X_{ij}=\mathcal S_5+\operatorname{span}\{\mathbf1_{\Omega_{ij}}\}.
\]
Fit the sampled signal by least squares in every $X_{ij}$ and select the smallest residual.

\begin{theorem}[Finite exact interval selection]
Assume the true sample vector $x$ belongs to exactly one candidate space $X_{i_*j_*}$.  Then the residual minimizer is unique and equals $(i_*,j_*)$.
\end{theorem}
\begin{proof}
The true candidate has residual zero.  Every other candidate has positive residual by the uniqueness assumption, so the true candidate is the unique minimizer.
\end{proof}

For the current signal, the selected interval is
\[
[4/16,12/16)=[1/4,3/4),
\]
and the nearest wrong candidate has residual norm
\[
\gamma=%s.
\]
""" % f"{cert.dictionary_wrong_gap:.12f}")
    add(visual_page("Finite interval-dictionary residual surface", "24_interval_dictionary_heatmap.pdf", "The true packet is the unique zero-residual entry.  Neighboring intervals form a positive residual basin rather than another exact representation."))
    add(visual_page("Candidate ranking", "25_interval_candidate_ranking.pdf", "The ranking makes the model separation gap visible.  This gap becomes the stability constant for noisy selection."))

    add(r"""\chapter{Noise stability of finite packet discovery}
Let $x\in X_{r_*}$ be the exact signal and define
\[
\gamma=\min_{r\ne r_*}\operatorname{dist}(x,X_r)>0.
\]
Observe $y=x+e$.

\begin{theorem}[Half-gap stability]
If
\[
\norm{e}<\frac\gamma2,
\]
then $r_*$ remains the unique minimum-residual candidate.
\end{theorem}
\begin{proof}
For the true space,
\[
\operatorname{dist}(y,X_{r_*})\le\norm e.
\]
For any wrong space,
\[
\operatorname{dist}(y,X_r)
\ge
\operatorname{dist}(x,X_r)-\norm e
\ge
\gamma-\norm e.
\]
If $\norm e<\gamma/2$, then $\norm e<\gamma-\norm e$, so the true residual is strictly smaller than every wrong residual.
\end{proof}

The theorem is worst-case and deterministic.  Noise above the threshold may still be classified correctly, but it is no longer guaranteed by this argument.
""")
    add(visual_page("Finite dictionary under noise", "26_dictionary_noise_stability.pdf", "Every tested perturbation below the half-gap threshold retained the true interval.  The theorem concerns the norm of the entire perturbation, not a particular probability distribution."))

    add(r"""\chapter{Amplitude noise and endpoint perturbations}
\section{Amplitude estimator}
For noisy data $f+\eta$,
\[
\widehat a-a=\ell_K(\eta).
\]
The Cauchy--Schwarz certificate given earlier measures the noise gain of the selected edge modes.  Using additional valid modes increases the mask energy in the denominator but may also admit more high-frequency noise; the tradeoff is explicit.

\section{Support perturbation}
For a true packet $a\mathbf1_\Omega$ and an estimated packet $\widehat a\mathbf1_{\widehat\Omega}$,
\begin{theorem}[Packet perturbation bound]
For $1\le p<\infty$,
\[
\boxed{
\norm{a\mathbf1_\Omega-\widehat a\mathbf1_{\widehat\Omega}}_{L^p}
\le
|a-\widehat a|\,\mu(\Omega)^{1/p}
+|\widehat a|\,\mu(\Omega\triangle\widehat\Omega)^{1/p}.
}
\]
If $a=\widehat a$, equality reduces to
\[
\norm{a(\mathbf1_\Omega-\mathbf1_{\widehat\Omega})}_{L^p}
=|a|\mu(\Omega\triangle\widehat\Omega)^{1/p}.
\]
\end{theorem}
\begin{proof}
Write
\[
a\mathbf1_\Omega-\widehat a\mathbf1_{\widehat\Omega}
=(a-\widehat a)\mathbf1_\Omega
+\widehat a(\mathbf1_\Omega-\mathbf1_{\widehat\Omega})
\]
and apply the triangle inequality.  The difference of indicators has absolute value one exactly on the symmetric difference.
\end{proof}
""")
    add(visual_page("Amplitude recovery under noise", "27_amplitude_noise_study.pdf", "The estimator is unbiased in the controlled Gaussian experiment and its variance grows with the noise level.  The exact noiseless coefficient identity remains separate from this statistical study."))
    add(visual_page("Endpoint perturbation equality", "28_endpoint_perturbation_bound.pdf", "With the amplitude fixed, the measured error equals the symmetric-difference formula exactly on the finite grid."))

    add(r"""\chapter{Model mismatch and negative controls}
A trustworthy reconstruction method must fail visibly when its assumptions fail.

\section{Undeclared smooth frequency}
Add $0.06\cos(18\pi t)$ to the signal while keeping the declared smooth degree at five.  The edge packet is still recovered correctly, but the ninth frequency remains in the residual.  The residual therefore identifies a missing smooth packet rather than creating boundary ringing.

\section{Incorrect interval packet}
Shift both packet endpoints and run the same reconstruction.  The result has a nonzero residual concentrated near the incorrect support boundaries.  This proves that the implementation is not merely returning the original input or forcing a zero certificate.
""")
    add(visual_page("Residual from an undeclared smooth mode", "29_model_mismatch_residual.pdf", "The residual has a coherent oscillatory shape matching the omitted ninth frequency.  The singular packet remains exact because its identifying modes and support are unchanged."))
    add(visual_page("Wrong-packet negative control", "30_wrong_packet_negative_control.pdf", "An incorrect interval address produces a visible nonzero residual.  Exact synthesis is conditional on the correct packet geometry, as the theorem states."))

    add(r"""\part{Computational consequences and exact boundaries}
\chapter{Mode budgets and variation}
\section{Why global mode count is not the right complexity measure}
A global Fourier representation treats every jump location as an infinite coefficient tail.  The packet representation stores:
\begin{itemize}
\item the finite smooth coefficients;
\item two interval endpoints;
\item one jump amplitude.
\end{itemize}
For the declared model, this finite data reconstructs the object exactly.  The gain is not free compression of arbitrary signals; it comes from matching the representation to the singular geometry.

\section{Total variation}
The exact packet has two localized jumps.  Global partial sums replace those jumps by alternating boundary oscillations and therefore create excess discrete total variation at finite cutoff.  Packet synthesis preserves the variation of the represented object up to numerical roundoff.
""")
    add(visual_page("Global mode budget", "31_mode_budget_comparison.pdf", "The boundary maximum error associated with Gibbs ringing does not vanish by merely adding global modes.  The exact packet stores the boundary as geometry."))
    add(visual_page("Total-variation comparison", "32_total_variation.pdf", "The oscillatory boundary layer adds variation that is absent from the exact singular packet.  This plot is descriptive for the sampled signal; the exact theorem is the reconstruction identity."))

    add(r"""\chapter{The exact error source}
For $N\ge5$ the global and packet errors are
\[
\begin{aligned}
E_{\mathrm{global}}
&=f-Q_Nf\\
&=(I-Q_N)s+(I-Q_N)j\\
&=(I-Q_N)j,
\end{aligned}
\]
and
\[
\begin{aligned}
E_{\mathrm{packet}}
&=f-(Q_NP_Sf+P_Jf)\\
&=(I-Q_N)s\\
&=0
\end{aligned}
\]
for the chosen degree-five seed.  The essential step is therefore not a more complicated Fourier coefficient formula.  It is the declaration and exact recovery of $j$ as an independent packet.
""")
    add(visual_page("Where the Gibbs term goes", "33_error_source_decomposition.pdf", "The global method carries the jump truncation term $(I-Q_N)j$.  The packet method replaces it with exact synthesis of $j$, leaving only the smooth approximation term."))
    add(visual_page("Finite projector matrices", "34_projector_matrices.pdf", "The small-grid matrices independently verify idempotence, completeness, and packet annihilation.  The projectors are oblique but algebraically exact."))
    add(visual_page("Proof dependency ladder", "35_theorem_dependency_ladder.pdf", "Every later claim depends on an earlier exact identity.  Numerical experiments are placed after, rather than in place of, the algebraic proofs."))
    add(visual_page("Certificate dashboard", "36_certificate_dashboard.pdf", "The dashboard separates near-zero identity residuals from the deliberately positive wrong-model separation gap."))

    add(r"""\chapter{One closed executable object}
The complete artifact is generated by one file:
\[
\texttt{gibbs\_projector\_closed.py}.
\]
The file contains the signal definition, closed Fourier coefficients, Gibbs asymptotic, finite projectors, dictionary search, robustness experiments, figures, tables, LaTeX manuscript, KaTeX derivation, assertions, PDF build, and checksum manifest.

The build order is intentional:
\begin{enumerate}
\item compute and assert the mathematical identities;
\item write the numerical certificate ledger;
\item generate figures and tables;
\item write the manuscript from those exact results;
\item compile the PDF;
\item preflight and render it;
\item write the release manifest.
\end{enumerate}
A failed assertion stops the build before a successful-looking PDF can be produced.
""")
    add(visual_page("Single-file build architecture", "37_single_file_architecture.pdf", "All generated artifacts descend from one executable source.  The TeX file is a generated view of the same definitions and certificates used by the numerical experiments."))
    add(visual_page("Final four-panel synthesis", "38_final_synthesis.pdf", "The singularity packet is retained exactly, while Fourier analysis is reserved for the smooth component.  This is the complete mechanism of the circumvention."))
    add(visual_page("Complete calculus wheel", "39_summary_wheel.pdf", "The wheel closes only after synthesis and residual verification.  If the residual is nonzero, the loop returns to packet choice or model refinement rather than relabeling the failure as exact."))

    add(r"""\chapter{What this example establishes}
\section{Proved statements}
Within the declared model and finite dictionary, the work proves:
\begin{enumerate}
\item the exact Fourier coefficients of the smooth and singular packets;
\item the classical Gibbs limiting profile and constant;
\item an exact edge-amplitude functional;
\item a complete complementary projector pair;
\item exact singularity-retaining synthesis;
\item a finite exact interval-selection theorem;
\item a half-gap noise-stability theorem;
\item exact support-perturbation bounds;
\item exact dyadic, polyphase, and Haar reconstructions of the singular packet.
\end{enumerate}

\section{What remains a broader research problem}
The example does not by itself solve:
\begin{itemize}
\item arbitrary edge discovery in noisy multidimensional data;
\item singularities not contained in the declared packet dictionary;
\item nonlinear shocks whose locations evolve with the solution;
\item high-dimensional geometry with unknown topology;
\item optimal packet dictionaries, penalties, or statistical rates;
\item every manifestation of Gibbs-like behavior in numerical PDEs.
\end{itemize}
Those questions require their own recovery and evolution theorems.  The significance of the present construction is that it isolates the exact mechanism: global ringing disappears from the reconstruction error when the singular geometry is represented and synthesized exactly.

\section{Final formula}
The entire worked outcome can be compressed to
\[
\boxed{
\underbrace{f}_{\text{observed object}}
=
\underbrace{P_Sf}_{\text{smooth packet}}
+
\underbrace{P_Jf}_{\text{singularity packet}}
\xrightarrow{\ Q_5\oplus I\ }
\underbrace{Q_5P_Sf+P_Jf}_{f}.
}
\]
The formula is short because every preceding chapter establishes why each symbol is defined, computable, stable in the stated sense, and exact on the declared class.

\appendix
\chapter{Complete coefficient table}
The following table is generated directly from the closed formulas used by the code.
\input{tables/coefficient_table.tex}

\chapter{Overshoot convergence table}
\input{tables/overshoot_table.tex}

\chapter{Finite interval candidates}
\input{tables/dictionary_table.tex}

\chapter{Detailed proof of the local scaling limit}
Let $H$ be the periodic step with an upward jump at the origin.  Near the jump, write
\[
Q_NH(\delta)-\frac12
=\int_0^\delta D_N(v)\,dv+R_N(\delta),
\]
where $R_N$ contains terms whose integration domain stays away from the singular point.  For
\[
\delta=\frac{y}{(2N+1)\pi},
\]
set $v=z/((2N+1)\pi)$.  Then
\[
D_N(v)\,dv
=\frac{\sin z}{\sin(z/(2N+1))}\frac{dz}{(2N+1)\pi}
\longrightarrow
\frac{\sin z}{\pi z}\,dz
\]
uniformly on compact $z$-intervals after removal of the removable singularity at zero.  Dominated convergence on each fixed compact interval gives
\[
\int_0^\delta D_N(v)\,dv
\longrightarrow
\frac1\pi\int_0^y\frac{\sin z}{z}\,dz.
\]
The remote term $R_N(\delta)$ converges to the constant appropriate to the one-sided baseline and does not affect the universal local profile.  For the rectangular packet, the second jump is a fixed positive distance away on the local $1/N$ scale, so it contributes only the correct constant background.  This yields the profile used in Chapter~4.

\chapter{Finite projector matrix derivation}
On a length-$n$ grid, let $F$ denote the normalized discrete Fourier analysis matrix,
\[
F_{kj}=\frac1n e^{-2\pi ikj/n}.
\]
Let $m$ be the sampled interval mask and $K$ the selected out-of-band modes.  Define the row functional
\[
\lambda^*=
\frac{\sum_{k\in K}\overline{(Fm)_k}F_{k,:}}
{\sum_{k\in K}|(Fm)_k|^2}.
\]
Then
\[
P_J=m\lambda^*,
\qquad
\lambda^*m=1.
\]
Consequently
\[
P_J^2=m(\lambda^*m)\lambda^*=P_J.
\]
The complementary matrix $P_S=I-P_J$ satisfies every remaining projector identity by direct algebra.  The matrices visualized in Figure~34 are generated from this formula at $n=64$.

\chapter{Reproduction commands}
From the extracted source directory:
\begin{lstlisting}
python gibbs_projector_closed.py
\end{lstlisting}
The script creates all figures, tables, the certificate JSON, the KaTeX markdown, the LaTeX source, and the final PDF.  A nonzero assertion or LaTeX return code stops the build.

\chapter{Complete single-file source}
The following listing is the complete executable object that generated this manuscript.
\lstinputlisting{gibbs_projector_closed.py}
\end{document}
""")

    tex = ROOT / "Singularity_Exact_Gibbs_Circumvention.tex"
    tex.write_text("".join(V), encoding="utf-8")
    return tex


def write_katex(cert: Certificate) -> Path:
    text = rf"""# Singularity-Exact Reconstruction

## A closed projector-resolved circumvention of the Gibbs phenomenon

**Author:** Komorebi P.

The single signal used throughout is

$$
f(t)=s(t)+\frac54\mathbf{{1}}_{{[1/4,3/4)}}(t),
$$

with

$$
s(t)=\frac13\cos(2\pi t)+\frac14\sin(6\pi t)-\frac15\cos(10\pi t).
$$

For the interval mask $m=\mathbf{{1}}_{{[1/4,3/4)}}$,

$$
\widehat m(0)=\frac12,
\qquad
\widehat m(k)=(-1)^k\frac{{\sin(\pi k/2)}}{{\pi k}},\quad k\ne0.
$$

For $N\ge5$,

$$
f-Q_Nf=\frac54(m-Q_Nm),
$$

so every remaining global Fourier error comes from the jump packet.

The local scaled partial sums converge to

$$
\frac12+\frac1\pi\operatorname{{Si}}(y),
$$

and the first maximum at $y=\pi$ gives

$$
G=\frac{{\operatorname{{Si}}(\pi)}}{{\pi}}-\frac12
={cert.gibbs_constant:.15f}.
$$

Choose out-of-band odd frequencies $K$ and define

$$
\ell_K(g)=
\frac{{\sum_{{k\in K}}\overline{{\widehat m(k)}}\widehat g(k)}}
{{\sum_{{k\in K}}|\widehat m(k)|^2}}.
$$

On $X=\mathcal S_5\oplus\operatorname{{span}}\{{m\}}$, $\ell_K(s+am)=a$. Define

$$
P_Jg=\ell_K(g)m,
\qquad
P_S=I-P_J.
$$

Then

$$
P_J^2=P_J,\qquad P_S^2=P_S,\qquad P_SP_J=P_JP_S=0,\qquad P_S+P_J=I.
$$

With $Q_5$ the degree-five Fourier projector,

$$
\boxed{{Q_5P_S+P_J=I_X}}.
$$

The finite implementation returned

$$
\max|f-(Q_5P_Sf+P_Jf)|={cert.exact_reconstruction_residual:.3e}.
$$

The finite interval dictionary selected

$$
[4/16,12/16)=[1/4,3/4)
$$

with nearest wrong-model gap

$$
\gamma={cert.dictionary_wrong_gap:.12f}.
$$

Therefore every perturbation satisfying $\|e\|<\gamma/2$ preserves the selected interval under the residual minimization theorem.

The complete derivations, figures, tables, negative controls, robustness studies, and source listing appear in the PDF generated by `gibbs_projector_closed.py`.
"""
    path = ROOT / "Singularity_Exact_Gibbs_Circumvention_KaTeX.md"
    path.write_text(text, encoding="utf-8")
    return path


def compile_pdf(tex: Path) -> Path:
    exe = shutil.which("pdflatex")
    if exe is None:
        raise RuntimeError("pdflatex is required to build the PDF")
    for suffix in (".aux", ".toc", ".out", ".log"):
        tex.with_suffix(suffix).unlink(missing_ok=True)
    for _ in range(3):
        cp = subprocess.run([exe, "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd=ROOT, text=True, capture_output=True)
        (RES / "pdflatex_output.txt").write_text(cp.stdout + "\n" + cp.stderr, encoding="utf-8")
        if cp.returncode != 0:
            raise RuntimeError(f"pdflatex failed: {cp.stdout[-4000:]}")
    return tex.with_suffix(".pdf")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_release_docs(cert: Certificate, pdf: Path) -> None:
    readme = f"""# Singularity-Exact Reconstruction

Run:

```powershell
python gibbs_projector_closed.py
```

The single Python file regenerates all {cert.figure_pairs} figure pairs, tables, certificates, the KaTeX derivation, the LaTeX source, and the PDF.

Primary exact residual: `{cert.exact_reconstruction_residual:.6e}`.

The result is exact for the declared smooth-plus-one-interval model and for the selected finite interval dictionary. It is not a universal arbitrary-edge recovery theorem.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")

    claim = """# Source and Claim Map

## Exact mathematical layer

- closed Fourier coefficients of the smooth seed and interval mask;
- Dirichlet-kernel local scaling and Gibbs constant;
- out-of-band edge-amplitude functional;
- complementary idempotent packet projectors;
- exact singularity-retaining synthesis on the declared model space;
- finite interval-dictionary selection and half-gap stability;
- packet perturbation bound;
- exact dyadic, polyphase, and Haar reconstructions.

## Numerical certificate layer

- convergence of finite partial-sum overshoot toward the Gibbs constant;
- finite-grid projector residuals;
- exact sampled reconstruction;
- noise and endpoint perturbation studies;
- negative controls and model-mismatch residuals.

## Explicit boundary

The release does not claim that arbitrary discontinuities are automatically known, that one finite dictionary is universal, or that every Gibbs-like issue in numerical computation is solved.
"""
    (ROOT / "SOURCE_AND_CLAIM_MAP.md").write_text(claim, encoding="utf-8")

    audit = f"""# Release audit

- Figure pairs: {cert.figure_pairs}
- Internal mathematical assertions: {cert.assertions}
- Exact reconstruction residual: {cert.exact_reconstruction_residual:.6e}
- Edge-projector idempotence residual: {cert.edge_projector_idempotence:.6e}
- Packet-annihilation residual: {cert.edge_projector_annihilation:.6e}
- Finite interval selected: [{cert.discovered_interval_i}/16, {cert.discovered_interval_j}/16)
- Nearest wrong-model gap: {cert.dictionary_wrong_gap:.12f}
- PDF: {pdf.name}
- PDF bytes: {pdf.stat().st_size}
- PDF SHA-256: {sha256(pdf)}
"""
    (ROOT / "RELEASE_AUDIT.md").write_text(audit, encoding="utf-8")

    files = [p for p in ROOT.rglob("*") if p.is_file() and not any(part in {"render", "__pycache__"} for part in p.parts)]
    manifest = {"title": "Singularity-Exact Reconstruction", "author": "Komorebi P.", "certificate": asdict(cert), "files": []}
    for p in sorted(files):
        manifest["files"].append({"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)})
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    cert = generate_all()
    write_latex_tables()
    write_katex(cert)
    tex = write_tex(cert)
    pdf = compile_pdf(tex)
    write_release_docs(cert, pdf)
    print(json.dumps({"pdf": str(pdf), **asdict(cert)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
import json
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle, Ellipse

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
DATA = ROOT / "data" / "benchmark_records.json"
FIG.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10.5,
        "axes.titlesize": 13.5,
        "axes.labelsize": 11.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.fontsize": 9.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }
)

BLUE = "#355C7D"
ROSE = "#C06C84"
GREEN = "#4E8A6A"
GOLD = "#C49A3A"
PURPLE = "#6C5B7B"
DARK = "#263238"
LIGHT_BLUE = "#EAF2F8"
LIGHT_GREEN = "#E8F8F5"
LIGHT_GOLD = "#FEF9E7"
LIGHT_ROSE = "#FDEDEC"


def save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(FIG / filename, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def box(ax, xy, w, h, text, face="white", fontsize=10.5, edge=DARK, weight="normal"):
    patch = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.3,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + w / 2,
        xy[1] + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        linespacing=1.12,
    )
    return patch


def arrow(ax, start, end, label=None, label_pos=None, color=DARK, rad=0.0):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.35,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(patch)
    if label:
        if label_pos is None:
            label_pos = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.12)
        ax.text(
            *label_pos,
            label,
            ha="center",
            va="center",
            fontsize=9.5,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        )


def packet_hierarchy() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 6.0))
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 6.1)
    ax.axis("off")
    box(ax, (0.4, 4.25), 2.25, 1.0, "Full Hilbert space\n$2^n$ amplitudes", LIGHT_ROSE, 11)
    box(ax, (3.0, 4.25), 2.25, 1.0, "Symmetry packets\nreachable sectors", LIGHT_BLUE, 11)
    box(ax, (5.6, 4.25), 2.25, 1.0, "Internal encoding\ninside each packet", LIGHT_GREEN, 11)
    box(ax, (7.55, 2.35), 2.25, 1.0, "Classical update\nand measurement", LIGHT_GOLD, 11)
    box(ax, (4.0, 0.55), 2.25, 1.0, "Polynomial-time\nclassical simulation", "#F5EEF8", 11)
    arrow(ax, (2.65, 4.75), (3.0, 4.75), "project")
    arrow(ax, (5.25, 4.75), (5.6, 4.75), "compress")
    arrow(ax, (7.85, 4.45), (8.65, 3.35), "apply gates")
    arrow(ax, (7.55, 2.85), (6.25, 1.55), "polynomial cost")
    ax.text(1.55, 3.55, "unused sectors\nremoved", ha="center", va="center", fontsize=10, color=ROSE)
    ax.text(4.15, 3.55, "packet count and\ndimensions audited", ha="center", va="center", fontsize=10, color=BLUE)
    box(ax, (4.95, 2.92), 2.20, 0.82, "examples\nstabilizer, Gaussian, tensor,\norbit, or explicit basis", "white", 8.9, edge=GREEN)
    ax.text(5.1, 5.75, "The symmetry-collapse hierarchy", ha="center", fontsize=16, fontweight="bold")
    ax.text(5.1, 0.08, "A small packet is useful only when discovery, updates, and measurement are also efficient.", ha="center", fontsize=10.2)
    save(fig, "packet_hierarchy.pdf")


def dimension_scaling() -> None:
    n = np.arange(2, 31)
    full = 2.0**n
    k2 = np.array([math.comb(int(x), 2) for x in n], dtype=float)
    half = np.array([math.comb(int(x), int(x // 2)) for x in n], dtype=float)
    symmetric = n + 1.0
    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    ax.plot(n, full, lw=2.2, label=r"full $2^n$", color=ROSE)
    ax.plot(n, half, lw=2.0, label=r"half filling $\binom{n}{\lfloor n/2\rfloor}$", color=GOLD)
    ax.plot(n, k2, lw=2.2, label=r"fixed weight two $\binom{n}{2}$", color=BLUE)
    ax.plot(n, symmetric, lw=2.2, label=r"symmetric qubits $n+1$", color=GREEN)
    ax.set_yscale("log")
    ax.set_xlabel("qubits $n$")
    ax.set_ylabel("active dimension")
    ax.set_title("Polynomial and exponential symmetry sectors")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, loc="upper left")
    save(fig, "dimension_scaling.pdf")


def weight_two_benchmark(data: dict) -> None:
    rec = data["weight_two"]
    n = np.array([r["n"] for r in rec])
    apply = np.array([r["apply_gain"] for r in rec])
    one = np.array([r["one_shot_gain"] for r in rec])
    memory = np.array([r["memory_gain"] for r in rec])
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.plot(n, apply, "o-", lw=2.1, label="repeated-application gain", color=BLUE)
    ax.plot(n, one, "s--", lw=1.9, label="one-shot gain", color=ROSE)
    ax.plot(n, memory, "^-", lw=2.0, label="amplitude-memory ratio", color=GREEN)
    ax.set_yscale("log")
    ax.set_xlabel("qubits $n$")
    ax.set_ylabel("recorded gain (log scale)")
    ax.set_title("Exact weight-two packet benchmark")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, loc="upper left")
    ax.annotate(
        "n = 20\n190 active amplitudes\nzero recorded error",
        xy=(20, 958.8),
        xytext=(15.4, 1800),
        arrowprops=dict(arrowstyle="->", color=DARK),
        fontsize=9.5,
        ha="left",
    )
    save(fig, "weight_two_benchmark.pdf")


def coarse_vs_fine(data: dict) -> None:
    n = np.arange(4, 25)
    full = 2.0**n
    parity = full / 2
    mod4 = full / 4
    k2 = np.array([math.comb(int(x), 2) for x in n], dtype=float)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(n, full, lw=2.2, label="full", color=ROSE)
    ax.plot(n, parity, lw=2.0, label="one parity packet", color=PURPLE)
    ax.plot(n, mod4, lw=2.0, label="one weight-mod-4 packet", color=GOLD)
    ax.plot(n, k2, lw=2.2, label="fixed weight two", color=BLUE)
    ax.set_yscale("log")
    ax.set_xlabel("qubits $n$")
    ax.set_ylabel("basis-state count")
    ax.set_title("Coarse symmetry gives constant factors, not polynomial collapse")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, loc="upper left")
    save(fig, "coarse_vs_fine.pdf")


def dicke_basis() -> None:
    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.8)
    ax.axis("off")
    ax.text(5, 4.45, "Permutation symmetry collapses bit strings to Dicke coordinates", ha="center", fontsize=15, fontweight="bold")
    left_y = [3.45, 2.7, 1.95, 1.2]
    left_labels = ["0000", "0001, 0010, 0100, 1000", "six strings of weight two", "1111"]
    right_labels = [r"$|D_4^0\rangle$", r"$|D_4^1\rangle$", r"$|D_4^2\rangle$", r"$|D_4^4\rangle$"]
    for y, left, right in zip(left_y, left_labels, right_labels):
        box(ax, (0.45, y - 0.28), 3.8, 0.56, left, LIGHT_BLUE, 9.7)
        arrow(ax, (4.35, y), (5.35, y))
        box(ax, (5.45, y - 0.28), 1.65, 0.56, right, LIGHT_GREEN, 11)
    box(ax, (7.55, 1.55), 2.0, 1.45, "collective gates\nact on an $(n+1)$-\ndimensional vector", LIGHT_GOLD, 10.5)
    arrow(ax, (7.1, 2.28), (7.55, 2.28))
    ax.text(5, 0.42, r"For $n$ qubits, the fully symmetric subspace has basis $|D_n^0\rangle,\ldots,|D_n^n\rangle$.", ha="center", fontsize=10.5)
    save(fig, "dicke_basis.pdf")


def hypercube_quotient() -> None:
    n = 8
    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    ax.set_xlim(-0.6, n + 0.6)
    ax.set_ylim(-0.9, 1.2)
    ax.axis("off")
    for k in range(n + 1):
        ax.add_patch(Circle((k, 0), 0.18, facecolor=LIGHT_BLUE, edgecolor=DARK, lw=1.2))
        ax.text(k, 0, str(k), ha="center", va="center", fontsize=10)
        ax.text(k, -0.42, rf"$\binom{{8}}{{{k}}}$", ha="center", fontsize=9)
    for k in range(n):
        val = math.sqrt((k + 1) * (n - k))
        arrow(ax, (k + 0.2, 0), (k + 0.8, 0), f"{val:.2f}", label_pos=(k + 0.5, 0.32))
    ax.text(4, 0.92, "Eight-dimensional hypercube reduced to nine weight orbits", ha="center", fontsize=14.5, fontweight="bold")
    ax.text(4, -0.75, "Node labels are Hamming weights; lower labels are orbit sizes; edge labels are normalized quotient couplings.", ha="center", fontsize=9.8)
    save(fig, "hypercube_quotient.pdf")


def few_particle_dimensions() -> None:
    modes = np.arange(2, 31)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for particles, color, marker in [(1, GREEN, "o"), (2, BLUE, "s"), (3, GOLD, "^")]:
        ferm = np.array([math.comb(int(m), particles) if m >= particles else 0 for m in modes], dtype=float)
        bos = np.array([math.comb(int(m + particles - 1), particles) for m in modes], dtype=float)
        ax.plot(modes, ferm, marker=marker, markevery=4, lw=1.9, color=color, label=f"fermions N={particles}")
        ax.plot(modes, bos, linestyle="--", lw=1.6, color=color, label=f"bosons N={particles}")
    ax.set_yscale("log")
    ax.set_xlabel("modes $m$")
    ax.set_ylabel("fixed-particle sector dimension")
    ax.set_title("Few-particle Hilbert spaces grow polynomially for fixed particle number")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, ncol=2)
    save(fig, "few_particle_dimensions.pdf")


def leakage_bound(data: dict) -> None:
    rec = data["leakage_examples"]
    labels = ["exact weight", "parity", "weight mod 4"]
    values = [r["leakage"] for r in rec]
    fig, ax = plt.subplots(figsize=(7.8, 4.7))
    bars = ax.bar(labels, values, color=[BLUE, PURPLE, GOLD], edgecolor=DARK)
    ax.set_ylim(0, max(values) * 1.35)
    ax.set_ylabel("recorded leakage probability")
    ax.set_title("Symmetry-breaking gates invalidate an un-audited packet restriction")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.004, f"{value:.3f}", ha="center", fontsize=10)
    ax.text(0.5, -0.22, r"Analytic certificate: $\|(I-P)e^{-itH}P\|\leq |t|\,\|[H,P]\|$", transform=ax.transAxes, ha="center", fontsize=10.5)
    save(fig, "leakage_bound.pdf")


def two_axis_complexity() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("active packet dimension or packet count")
    ax.set_ylabel("internal representation cost")
    ax.set_title("Two independent routes to classical tractability")
    ax.add_patch(Rectangle((0, 0), 4.4, 4.4, facecolor=LIGHT_GREEN, edgecolor="none", alpha=0.8))
    ax.text(2.2, 2.2, "easy region\nsmall packet and\ncompact encoding", ha="center", va="center", fontsize=11, fontweight="bold")
    points = {
        "fixed weight k": (2.0, 3.0),
        "symmetric Dicke": (2.6, 2.0),
        "stabilizer": (8.0, 1.8),
        "Gaussian": (7.2, 2.6),
        "half filling": (8.2, 7.8),
        "global interference": (9.0, 9.0),
    }
    for label, (x, y) in points.items():
        ax.scatter([x], [y], s=70, color=BLUE if x < 5 else ROSE, edgecolor=DARK, zorder=3)
        ax.text(x + 0.16, y + 0.18, label, fontsize=9.2)
    ax.grid(alpha=0.22)
    save(fig, "two_axis_complexity.pdf")


def channel_blocks() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.3, 4.5), constrained_layout=True)
    state = np.array([[1.0, 0.35, 0.0], [0.35, 0.7, 0.2], [0.0, 0.2, 0.5]])
    channel = np.zeros((6, 6))
    channel[:2, :2] = 0.9
    channel[2:4, 2:4] = 0.75
    channel[4:, 4:] = 0.55
    channel[2:4, :2] = 0.25
    axes[0].imshow(state, cmap="Blues", vmin=0, vmax=1)
    axes[0].set_title("Density operator\ntwo packet indices")
    axes[0].set_xlabel("right packet")
    axes[0].set_ylabel("left packet")
    axes[1].imshow(channel, cmap="PuRd", vmin=0, vmax=1)
    axes[1].set_title("Quantum channel\nfour packet indices")
    axes[1].set_xlabel("input packet pair")
    axes[1].set_ylabel("output packet pair")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Populations, coherences, and channel transfer blocks", fontsize=14.5, fontweight="bold")
    save(fig, "channel_blocks.pdf")


def forrelation_interference() -> None:
    fig, ax = plt.subplots(figsize=(10.0, 4.7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.8)
    ax.axis("off")
    stages = [
        (0.45, "uniform\nsuperposition", LIGHT_BLUE),
        (2.25, "$f(x)$\nphases", LIGHT_GOLD),
        (4.05, "Walsh-Fourier\ntransfer", LIGHT_GREEN),
        (5.85, "$g(y)$\nphases", LIGHT_GOLD),
        (7.65, "global\ninterference", LIGHT_ROSE),
    ]
    for x, label, color in stages:
        box(ax, (x, 1.8), 1.35, 1.0, label, color, 10.5)
    for i in range(len(stages) - 1):
        arrow(ax, (stages[i][0] + 1.35, 2.3), (stages[i + 1][0], 2.3))
    for y in [0.9, 1.15, 3.45, 3.7]:
        ax.plot([1.15, 8.3], [y, 2.3], color=ROSE, alpha=0.18, lw=1.0)
    ax.text(5, 4.42, "Forrelation stores the answer in coherent relations across exponentially many paths", ha="center", fontsize=14.5, fontweight="bold")
    ax.text(5, 0.35, r"$\Phi(f,g)=2^{-3n/2}\sum_{x,y} f(x)(-1)^{x\cdot y}g(y)$", ha="center", fontsize=11.5)
    save(fig, "forrelation_interference.pdf")


def collapse_decision_tree() -> None:
    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    box(ax, (3.6, 4.85), 2.8, 0.75, "Proposed quantum circuit family", LIGHT_BLUE, 11, weight="bold")
    box(ax, (0.4, 3.35), 2.45, 0.75, "Efficient invariant packet?", LIGHT_GREEN, 10.5)
    box(ax, (3.75, 3.35), 2.5, 0.75, "Compact internal encoding?", LIGHT_GREEN, 10.5)
    box(ax, (7.1, 3.35), 2.45, 0.75, "Global cross-packet phase?", LIGHT_ROSE, 10.5)
    box(ax, (0.45, 1.35), 2.35, 0.9, "Packet simulation\npossibly in P", LIGHT_GOLD, 10.5)
    box(ax, (3.82, 1.35), 2.35, 0.9, "Hybrid compressed\nsimulation", LIGHT_GOLD, 10.5)
    box(ax, (7.15, 1.35), 2.35, 0.9, "No collapse from\nsymmetry alone", LIGHT_ROSE, 10.5)
    arrow(ax, (4.5, 4.85), (1.65, 4.1), "yes")
    arrow(ax, (5.0, 4.85), (5.0, 4.1), "otherwise")
    arrow(ax, (5.5, 4.85), (8.35, 4.1), "audit")
    arrow(ax, (1.62, 3.35), (1.62, 2.25), "poly dimension")
    arrow(ax, (5.0, 3.35), (5.0, 2.25), "closed updates")
    arrow(ax, (8.32, 3.35), (8.32, 2.25), "exponential coherence")
    ax.text(5, 5.82, "Decision tree for symmetry-collapse claims", ha="center", fontsize=15.5, fontweight="bold")
    ax.text(5, 0.45, "Every branch still requires an explicit input model, gate-update algorithm, and measurement audit.", ha="center", fontsize=10)
    save(fig, "collapse_decision_tree.pdf")


def research_atlas() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 6.1)
    ax.axis("off")
    items = [
        (0.4, 4.55, "Fixed charge and\nfew particles", LIGHT_GREEN),
        (3.0, 4.55, "Permutation symmetry\nand Schur coordinates", LIGHT_GREEN),
        (5.6, 4.55, "Orbit-quotient\nquantum walks", LIGHT_BLUE),
        (8.2, 4.55, "Stabilizer and\nClifford packets", LIGHT_BLUE),
        (0.4, 2.65, "Gaussian and\nmatchgate hybrids", LIGHT_GOLD),
        (3.0, 2.65, "Approximate symmetry\nand adaptive packets", LIGHT_GOLD),
        (5.6, 2.65, "Open systems and\nchannel packets", LIGHT_GOLD),
        (8.2, 2.65, "Global interference\nand lower bounds", LIGHT_ROSE),
    ]
    for x, y, label, color in items:
        box(ax, (x, y), 1.8, 1.0, label, color, 9.8)
    box(ax, (3.65, 0.75), 3.1, 1.0, "Symmetry-collapse compiler\npacket discovery + update + certification", "#F5EEF8", 10.6, weight="bold")
    targets = [(4.15, 1.75), (4.45, 1.75), (4.75, 1.75), (5.05, 1.75),
               (5.35, 1.75), (5.65, 1.75), (5.95, 1.75), (6.25, 1.75)]
    for (x, y, _, _), target in zip(items, targets):
        arrow(ax, (x + 0.9, y), target, color="#777777")
    ax.text(5.2, 5.9, "Research atlas for quantum-to-classical collapse", ha="center", fontsize=15.5, fontweight="bold")
    ax.text(5.2, 0.25, "The central task is not to find a symmetry label but to build an efficient, certified representation.", ha="center", fontsize=10.2)
    save(fig, "research_atlas.pdf")


def symmetric_qudit_scaling() -> None:
    n = np.arange(1, 31)
    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    for d, color in [(2, BLUE), (3, GREEN), (4, GOLD), (5, PURPLE)]:
        dims = np.array([math.comb(int(x + d - 1), d - 1) for x in n], dtype=float)
        ax.plot(n, dims, lw=2.0, label=f"local dimension d={d}", color=color)
    ax.set_yscale("log")
    ax.set_xlabel("sites $n$")
    ax.set_ylabel(r"$\dim \mathrm{Sym}^n(C^d)$")
    ax.set_title("Permutation-symmetric qudit sectors remain polynomial for fixed local dimension")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False)
    save(fig, "symmetric_qudit_scaling.pdf")


def compiler_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(10.3, 4.9))
    ax.set_xlim(0, 10.3)
    ax.set_ylim(0, 4.9)
    ax.axis("off")
    stages = [
        (0.25, "detect\nsymmetry"),
        (2.1, "build packet\nor quotient"),
        (3.95, "compile gate\nupdates"),
        (5.8, "track leakage\nand error"),
        (7.65, "evaluate\nmeasurement"),
    ]
    for i, (x, label) in enumerate(stages):
        color = [LIGHT_BLUE, LIGHT_GREEN, LIGHT_GREEN, LIGHT_GOLD, LIGHT_ROSE][i]
        box(ax, (x, 2.2), 1.45, 1.0, label, color, 10.2)
    for i in range(len(stages) - 1):
        arrow(ax, (stages[i][0] + 1.45, 2.7), (stages[i + 1][0], 2.7))
    box(ax, (2.15, 0.35), 6.0, 0.95, "certificate\ninvariant basis + update rules + error budget + complexity bound", "#F5EEF8", 9.7)
    arrow(ax, (4.68, 2.2), (4.68, 1.30))
    ax.text(5.15, 4.45, "A symmetry-collapse compiler must certify more than block structure", ha="center", fontsize=15.0, fontweight="bold")
    save(fig, "compiler_pipeline.pdf")



def moving_frame_packets() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.9))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 6.0)
    ax.axis("off")

    ax.text(
        5.3,
        5.72,
        "Time-dependent packets can expose a hidden polynomial representation",
        ha="center",
        fontsize=15.5,
        fontweight="bold",
    )

    ax.text(0.45, 4.88, "laboratory coordinates", ha="left", fontsize=11.2, fontweight="bold", color=ROSE)
    centers = [(1.70, 3.80), (4.45, 3.80), (7.20, 3.80)]
    angles = [-18, 16, -8]
    labels = [r"$P_0\mathcal{H}$", r"$P_1\mathcal{H}$", r"$P_2\mathcal{H}$"]
    for (cx, cy), angle, label in zip(centers, angles, labels):
        ax.add_patch(Ellipse((cx, cy), 1.85, 1.00, angle=angle, facecolor=LIGHT_ROSE, edgecolor=DARK, lw=1.4))
        ax.text(cx, cy, label, ha="center", va="center", fontsize=11.4)
    arrow(ax, (2.68, 3.80), (3.48, 3.80), r"$G_1$", label_pos=(3.08, 4.12))
    arrow(ax, (5.43, 3.80), (6.23, 3.80), r"$G_2$", label_pos=(5.83, 4.12))
    box(ax, (8.55, 3.22), 1.45, 1.15, "large ambient\ncoordinates", LIGHT_ROSE, 10.2)

    ax.text(0.45, 2.18, "moving coordinates", ha="left", fontsize=11.2, fontweight="bold", color=BLUE)
    packet_text = "fixed packet\n" + r"$P\mathcal{H}$"
    for x in (0.95, 4.00, 7.05):
        box(ax, (x, 0.86), 1.70, 0.96, packet_text, LIGHT_BLUE, 10.8)
    box(ax, (9.05, 0.86), 1.15, 0.96, "poly-size\ncoordinates", LIGHT_GREEN, 9.8)

    arrow(ax, (2.65, 1.34), (4.00, 1.34), r"$\widetilde G_1$", label_pos=(3.33, 1.66))
    arrow(ax, (5.70, 1.34), (7.05, 1.34), r"$\widetilde G_2$", label_pos=(6.38, 1.66))
    for cx in (1.70, 4.45, 7.20):
        arrow(ax, (cx, 3.20), (cx, 1.84), r"$W_t^*$", label_pos=(cx + 0.34, 2.52), color=PURPLE)

    ax.text(5.3, 0.43, r"$\widetilde G_t=W_t^*G_tW_{t-1}$ acts on one fixed polynomial-dimensional packet.", ha="center", fontsize=10.4)
    ax.text(5.3, 0.12, "The frame schedule must itself be efficiently discoverable; otherwise the representation is circular.", ha="center", fontsize=9.7)
    save(fig, "moving_frame_packets.pdf")


def reachable_packet_graph() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 5.5))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    ax.text(5.2, 5.18, "A sparse packet graph permits exact sector changes", ha="center", fontsize=15.4, fontweight="bold")
    ax.text(5.2, 4.58, r"Loops preserve charge; adjacent arrows change charge by $\Delta k=\pm1$.", ha="center", fontsize=10.4)

    xs = [1.0, 2.85, 4.70, 6.55, 8.40]
    for k, x in enumerate(xs):
        active = k <= 3
        face = LIGHT_GREEN if active else "#F4F6F8"
        edge = GREEN if active else "#9AA0A6"
        label = f"weight k = {k}\n" + rf"$\binom{{n}}{{{k}}}$"
        box(ax, (x - 0.60, 2.25), 1.20, 0.92, label, face, 9.8, edge=edge)

    for k, x in enumerate(xs):
        ax.add_patch(FancyArrowPatch((x - 0.24, 3.18), (x + 0.24, 3.18), arrowstyle="-|>", mutation_scale=11, connectionstyle="arc3,rad=-0.75", color=BLUE if k <= 3 else "#9AA0A6", lw=1.2))

    for k in range(4):
        color = ROSE if k < 3 else "#9AA0A6"
        arrow(ax, (xs[k] + 0.62, 2.82), (xs[k + 1] - 0.62, 2.82), color=color)
        arrow(ax, (xs[k + 1] - 0.62, 2.48), (xs[k] + 0.62, 2.48), color=color)

    box(ax, (0.60, 0.54), 3.10, 0.94, "reachable union\n" + r"$\bigoplus_{k=0}^{K}\mathcal{H}_{n,k}$", LIGHT_BLUE, 10.3)
    box(ax, (4.05, 0.54), 2.55, 0.94, "fixed K\n" + r"$\sum_{k=0}^{K}\binom{n}{k}=O(n^K)$", LIGHT_GOLD, 10.0)
    box(ax, (6.95, 0.54), 2.85, 0.94, "exact deterministic\npolynomial-time simulation", "#F5EEF8", 10.1)
    arrow(ax, (3.70, 1.01), (4.05, 1.01))
    arrow(ax, (6.60, 1.01), (6.95, 1.01))
    ax.text(5.2, 3.86, "Exact charge conservation may fail while the reachable low-charge union remains polynomial.", ha="center", fontsize=10.3)
    save(fig, "reachable_packet_graph.pdf")


def schur_commutant_compression() -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.text(5.4, 5.92, "Schur commutant compression removes multiplicity coordinates exactly", ha="center", fontsize=14.8, fontweight="bold")

    ax.text(1.95, 5.30, "full Schur-Weyl blocks", ha="center", fontsize=11.2, fontweight="bold")
    yvals = [4.38, 3.28, 2.18]
    colors = [LIGHT_BLUE, LIGHT_GREEN, LIGHT_GOLD]
    for idx, (y, color) in enumerate(zip(yvals, colors), start=1):
        box(ax, (0.38, y - 0.32), 1.25, 0.64, rf"$\mathcal{{U}}_{{\lambda_{idx}}}$", color, 10.5)
        for shift in (0.0, 0.16, 0.32):
            ax.add_patch(Rectangle((1.86 + shift, y - 0.32 + shift * 0.15), 1.48, 0.64, facecolor="#F4F6F8", edgecolor=DARK, lw=1.0))
        ax.text(2.76, y + 0.04, rf"$\mathcal{{V}}_{{\lambda_{idx}}}$", ha="center", va="center", fontsize=10.2)
        ax.text(2.76, y - 0.18, "possibly exponential", ha="center", va="center", fontsize=8.6, color="#555555")

    arrow(ax, (3.62, 3.28), (5.00, 3.28), "twirl +\nSchur's lemma", label_pos=(4.31, 3.72), color=PURPLE)

    ax.text(7.55, 5.30, "compressed invariant record", ha="center", fontsize=11.2, fontweight="bold")
    for idx, (y, color) in enumerate(zip(yvals, colors), start=1):
        box(ax, (5.25, y - 0.32), 1.35, 0.64, rf"$p_{{\lambda_{idx}}}$", color, 10.5)
        box(ax, (6.88, y - 0.32), 1.55, 0.64, rf"$\rho_{{\lambda_{idx}}}$", color, 10.5)
        box(ax, (8.72, y - 0.32), 1.45, 0.64, rf"$I/f_{{\lambda_{idx}}}$", "#F4F6F8", 10.0)

    box(ax, (0.85, 0.54), 3.75, 0.92, "multiplicity spaces may be huge\nbut appear only as exact identity factors", LIGHT_ROSE, 10.0)
    box(ax, (5.05, 0.54), 4.85, 0.92, "", LIGHT_GREEN, 10.2)
    ax.text(7.48, 1.18, "fixed local dimension d", ha="center", va="center", fontsize=10.4, fontweight="bold")
    ax.text(7.48, 0.78, r"$\sum_\lambda (\mathrm{dim}\,\mathcal{U}_\lambda)^2=O_d(n^{d^2-1})$", ha="center", va="center", fontsize=10.8)
    arrow(ax, (4.60, 1.00), (5.05, 1.00))
    ax.text(5.4, 0.18, "For qubits, the invariant mixed-state record uses only $O(n^3)$ parameters.", ha="center", fontsize=10.1)
    save(fig, "schur_commutant_compression.pdf")


def particle_scaling_phases() -> None:
    ns = np.unique(np.round(np.logspace(np.log10(8), np.log10(512), 90)).astype(int))

    def log2_binom(n: int, k: int) -> float:
        k = min(k, n - k)
        return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(2.0)

    regimes = [
        ("fixed $k=2$", [2 for _ in ns], BLUE),
        (r"$k=\lceil\log_2 n\rceil$", [min(n // 2, max(1, math.ceil(math.log2(n)))) for n in ns], GREEN),
        (r"$k=\lceil\sqrt{n}\rceil$", [min(n // 2, max(1, math.ceil(math.sqrt(n)))) for n in ns], GOLD),
        (r"$k=\lfloor n/2\rfloor$", [n // 2 for n in ns], ROSE),
    ]

    fig, ax = plt.subplots(figsize=(8.8, 5.6))
    for label, ks, color in regimes:
        ys = [log2_binom(int(n), int(k)) for n, k in zip(ns, ks)]
        ax.plot(ns, ys, lw=2.2, label=label, color=color)

    ax.set_xscale("log", base=2)
    ax.set_xlabel("qubits or modes $n$")
    ax.set_ylabel(r"$\log_2$ active packet dimension")
    ax.set_title("Particle-number growth creates distinct classical simulation regimes", pad=10)
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, loc="upper left")

    ax.text(19, 58, "polynomial", color=BLUE, fontsize=10.2)
    ax.text(58, 92, "quasipolynomial", color=GREEN, fontsize=10.2)
    ax.text(155, 155, "subexponential", color=GOLD, fontsize=10.2)
    ax.text(300, 355, "exponential", color=ROSE, fontsize=10.2)
    save(fig, "particle_scaling_phases.pdf")

def main() -> None:
    data = json.loads(DATA.read_text())
    packet_hierarchy()
    dimension_scaling()
    weight_two_benchmark(data)
    coarse_vs_fine(data)
    dicke_basis()
    hypercube_quotient()
    few_particle_dimensions()
    leakage_bound(data)
    two_axis_complexity()
    channel_blocks()
    forrelation_interference()
    collapse_decision_tree()
    research_atlas()
    symmetric_qudit_scaling()
    compiler_pipeline()
    moving_frame_packets()
    reachable_packet_graph()
    schur_commutant_compression()
    particle_scaling_phases()
    print(f"wrote {len(list(FIG.glob('*.pdf')))} Python-generated figures to {FIG}")


if __name__ == "__main__":
    main()

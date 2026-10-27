from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
import numpy as np
import sympy as sp

from .core import krylov_rank_profile, semisimple_seed_rank, transfer_blocks
from .examples import (
    bilateral_shift_matrix,
    companion_matrix,
    coordinate_projectors,
    repeated_jordan_operator,
    residue_projectors,
)
from .graphs import cycle_adjacency, path_adjacency, symmetric_graph_seed_rank

FIGURE_DPI = 240
TRANSFER_FIGURE_SEED = 23
COORDINATE_FIGURE_SEED = 91
SHIFT_SUPPORT_TOLERANCE = 1e-10
COORDINATE_DETERMINANT_CUTOFF = 1e-6

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Serif"
plt.rcParams["axes.titlelocation"] = "left"

INK = "#1f2933"
SOFT = "#5b6770"
ACCENT = "#8b1e3f"
ACCENT2 = "#2b6cb0"
GOLD = "#b7791f"
GREEN = "#2f855a"
BG = "#f7f5f2"
GRID = "#d9d4cc"
PALE = "#efe8de"
PALE2 = "#edf2f7"


def _save(fig: plt.Figure, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.png", dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _clean_axes(ax, grid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(SOFT)
    ax.spines["bottom"].set_color(SOFT)
    ax.tick_params(colors=SOFT, labelsize=10)
    if grid:
        ax.grid(True, color=GRID, linewidth=0.8, alpha=0.65)
    ax.set_axisbelow(True)


def _panel_title(ax, title, subtitle=None):
    ax.set_title(title, fontsize=13.5, color=INK, fontweight="bold", pad=10)
    if subtitle:
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5, color=SOFT, va="bottom")


def generate_figures(output_dir: str | Path) -> list[str]:
    out = Path(output_dir)
    stems: list[str] = []

    # 1. Seed grammar workflow diagram.
    fig = plt.figure(figsize=(12.6, 3.6), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.text(0.55, 3.62, "Seed calculus workflow", fontsize=15, color=INK, fontweight="bold")
    ax.text(0.55, 3.30, "The paper moves from a seed and an operator grammar to constrained reconstruction.", fontsize=10.2, color=SOFT)
    steps = [
        (0.8, 1.45, 1.35, 0.9, "seed", "chosen generators"),
        (2.55, 1.45, 1.5, 0.9, "address", "indices / packets"),
        (4.5, 1.45, 1.45, 0.9, "operate", "words in the algebra"),
        (6.35, 1.45, 1.45, 0.9, "project", "block or packet view"),
        (8.2, 1.45, 1.6, 0.9, "constrain", "relations / quotient data"),
        (10.3, 1.45, 1.5, 0.9, "complete", "closure or span"),
        (12.2, 1.45, 1.35, 0.9, "reconstruct", "ambient object"),
    ]
    cols = [ACCENT2, ACCENT2, GREEN, GOLD, ACCENT, GREEN, ACCENT]
    for i, (x, y, w, h, title, sub) in enumerate(steps):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.09", facecolor=BG, edgecolor=cols[i], linewidth=1.8)
        ax.add_patch(box)
        ax.text(x + w/2, y + 0.57, title, ha="center", va="center", fontsize=12, color=INK, fontweight="bold")
        ax.text(x + w/2, y + 0.26, sub, ha="center", va="center", fontsize=8.7, color=SOFT)
        if i < len(steps) - 1:
            x2 = steps[i + 1][0]
            arr = FancyArrowPatch((x + w, y + h/2), (x2, y + h/2), arrowstyle="-|>", mutation_scale=13, linewidth=1.5, color=SOFT)
            ax.add_patch(arr)
    ax.text(7.0, 0.55, "formal objects:  (seed, action, relations, packet structure, realization map)", ha="center", fontsize=10, color=SOFT)
    _save(fig, out, "01_seed_operator_grammar")
    stems.append("01_seed_operator_grammar")

    # 2. Transfer block norms.
    rng = np.random.default_rng(TRANSFER_FIGURE_SEED)
    n = 18
    projectors = coordinate_projectors(n, [list(range(0, 5)), list(range(5, 11)), list(range(11, 18))])
    operator = rng.normal(size=(n, n))
    blocks = transfer_blocks(operator, projectors)
    norms = np.array([[np.linalg.norm(block) for block in row] for row in blocks])
    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    im = ax.imshow(norms, cmap="cividis", aspect="equal")
    _panel_title(ax, "Transfer blocks of one sampled operator", "Each cell shows the Frobenius norm of Qβ A Qα.")
    ax.set_xticks(range(3), [r"packet $\alpha=1$", r"packet $\alpha=2$", r"packet $\alpha=3$"])
    ax.set_yticks(range(3), [r"packet $\beta=1$", r"packet $\beta=2$", r"packet $\beta=3$"])
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{norms[i,j]:.1f}", ha="center", va="center", color="white" if norms[i,j] < norms.max()*0.65 else INK, fontsize=11, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    cbar.ax.set_ylabel("block norm", color=SOFT)
    cbar.ax.tick_params(colors=SOFT)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=SOFT)
    _save(fig, out, "02_transfer_block_norms")
    stems.append("02_transfer_block_norms")

    # 3. Krylov rank profiles.
    companion = np.array(companion_matrix([0, 0, 0, 0, 0, 0, 0, 0]), dtype=float)
    repeated = np.array(repeated_jordan_operator([4, 4], eigenvalue=2), dtype=float)
    seed_comp = np.zeros(8); seed_comp[0] = 1
    seed_rep = np.array([0, 0, 0, 1, 0, 0, 0, 1], dtype=float)
    prof1 = np.array(krylov_rank_profile(companion, seed_comp))
    prof2 = np.array(krylov_rank_profile(repeated, seed_rep))
    steps = np.arange(1, 9)
    fig, ax = plt.subplots(figsize=(8.3, 5.2))
    ax.plot(steps, prof1, color=ACCENT2, linewidth=2.2, marker="o", markersize=6, label="cyclic companion operator")
    ax.plot(steps, prof2, color=GOLD, linewidth=2.2, marker="s", markersize=5.5, label="two equal Jordan blocks")
    ax.fill_between(steps, prof1, color=ACCENT2, alpha=0.08)
    ax.fill_between(steps, prof2, color=GOLD, alpha=0.10)
    ax.annotate("reaches full dimension", xy=(8, 8), xytext=(5.2, 7.1), fontsize=9.5, color=ACCENT2, arrowprops=dict(arrowstyle="-|>", color=ACCENT2, lw=1.2))
    ax.annotate("stalls at four dimensions", xy=(5, 4), xytext=(5.2, 3.1), fontsize=9.5, color=GOLD, arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.2))
    ax.set_xlabel("Krylov word length", color=INK)
    ax.set_ylabel("generated span dimension", color=INK)
    _clean_axes(ax, grid=True)
    ax.set_xticks(steps)
    ax.set_yticks(np.arange(1, 9))
    _panel_title(ax, "One seed either spans or stalls", "Different primary structure gives different growth profiles.")
    leg = ax.legend(frameon=False, loc="upper left")
    for t in leg.get_texts():
        t.set_color(SOFT)
    _save(fig, out, "03_cyclic_rank_profiles")
    stems.append("03_cyclic_rank_profiles")

    # 4. Semisimple heatmap.
    ds = np.arange(1, 9)
    ms = np.arange(1, 25)
    grid = np.array([[semisimple_seed_rank([int(d)], [int(m)]) for m in ms] for d in ds])
    fig, ax = plt.subplots(figsize=(9.3, 5.6))
    im = ax.imshow(grid, origin="lower", aspect="auto", cmap="magma")
    _panel_title(ax, r"Semisimple multiplicity law: $\lceil m/d \rceil$", "Rows fix the simple-module dimension d; columns vary the multiplicity m.")
    ax.set_xticks(np.arange(0, len(ms), 2), ms[::2])
    ax.set_yticks(np.arange(len(ds)), ds)
    ax.set_xlabel("multiplicity  m", color=INK)
    ax.set_ylabel("simple-module dimension  d", color=INK)
    # overlay level boundaries for small values
    for level in range(1, 6):
        for d in ds:
            mmax = min(ms[-1], level * d)
            ax.plot([0.5, mmax - 0.5], [d - 0.5, d - 0.5], color="white", alpha=0.12, lw=0.8)
    for d in [1, 2, 4, 8]:
        m = min(24, 2*d)
        ax.text(m-1, d-1, r"$2$", color="white", fontsize=9, ha="center", va="center")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel("minimal seeds", color=SOFT)
    cbar.ax.tick_params(colors=SOFT)
    ax.tick_params(colors=SOFT)
    _save(fig, out, "04_semisimple_seed_rank")
    stems.append("04_semisimple_seed_rank")

    # 5. Path graph seed ranks.
    ns = np.arange(2, 21)
    ranks = np.array([symmetric_graph_seed_rank(path_adjacency(int(n))) for n in ns])
    fig, ax = plt.subplots(figsize=(7.9, 4.8))
    ax.plot(ns, ranks, color=GREEN, marker="o", linewidth=2.1, markersize=5)
    ax.axhline(1, color=SOFT, linestyle=(0, (4, 3)), linewidth=1.1)
    ax.fill_between(ns, 0, ranks, color=GREEN, alpha=0.08)
    ax.text(13.2, 1.06, "constant value = 1", color=GREEN, fontsize=9.6)
    ax.set_xlabel("number of vertices", color=INK)
    ax.set_ylabel("adjacency-algebra seed rank", color=INK)
    ax.set_xticks([2, 5, 10, 15, 20])
    ax.set_yticks([1])
    _clean_axes(ax, grid=True)
    _panel_title(ax, "Path graphs remain cyclic", "The endpoint Krylov certificate supplies one seed for every tested size.")
    _save(fig, out, "05_path_graph_seed_rank")
    stems.append("05_path_graph_seed_rank")

    # 6. Cycle graph seed ranks.
    ns = np.arange(3, 21)
    ranks = np.array([symmetric_graph_seed_rank(cycle_adjacency(int(n))) for n in ns])
    fig, ax = plt.subplots(figsize=(7.9, 4.8))
    ax.plot(ns, ranks, color=ACCENT, marker="o", linewidth=2.1, markersize=5)
    ax.axhline(2, color=SOFT, linestyle=(0, (4, 3)), linewidth=1.1)
    ax.fill_between(ns, 0, ranks, color=ACCENT, alpha=0.08)
    ax.text(13.2, 2.06, "constant value = 2", color=ACCENT, fontsize=9.6)
    ax.set_xlabel("number of vertices", color=INK)
    ax.set_ylabel("adjacency-algebra seed rank", color=INK)
    ax.set_xticks([3, 5, 10, 15, 20])
    ax.set_yticks([1, 2])
    _clean_axes(ax, grid=True)
    _panel_title(ax, "Cycle graphs require two seeds", "Paired eigenspaces force multiplicity two in the generic spectrum.")
    _save(fig, out, "06_cycle_graph_seed_rank")
    stems.append("06_cycle_graph_seed_rank")

    # 7. Finite shift packet transfer.
    shift = bilateral_shift_matrix(24)
    projectors = residue_projectors(24, 6)
    blocks = transfer_blocks(shift, projectors)
    pattern = np.array([[int(np.linalg.norm(block) > SHIFT_SUPPORT_TOLERANCE) for block in row] for row in blocks])
    fig = plt.figure(figsize=(9.3, 4.9))
    ax1 = fig.add_axes([0.08, 0.17, 0.37, 0.70])
    im = ax1.imshow(pattern, cmap="viridis", aspect="equal", vmin=0, vmax=1)
    ax1.set_xticks(range(6), [str(i) for i in range(6)])
    ax1.set_yticks(range(6), [str(i) for i in range(6)])
    ax1.set_xlabel("input residue packet", color=INK)
    ax1.set_ylabel("output residue packet", color=INK)
    ax1.tick_params(colors=SOFT)
    ax1.set_title("Support matrix", fontsize=12.5, color=INK, pad=8, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel("nonzero transfer", color=SOFT)
    cbar.ax.tick_params(colors=SOFT)
    for i in range(6):
        for j in range(6):
            if pattern[i,j]:
                ax1.text(j, i, "1", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax2 = fig.add_axes([0.56, 0.14, 0.36, 0.72])
    ax2.set_xlim(-1.2, 1.2)
    ax2.set_ylim(-1.1, 1.15)
    ax2.axis("off")
    angles = np.linspace(np.pi/2, np.pi/2 - 2*np.pi, 6, endpoint=False)
    pts = np.c_[np.cos(angles), np.sin(angles)]
    for i, (x,y) in enumerate(pts):
        ax2.add_patch(Circle((x,y), 0.12, facecolor=PALE2, edgecolor=ACCENT2, linewidth=1.8))
        ax2.text(x, y, str(i), ha="center", va="center", color=INK, fontweight="bold")
    for i in range(6):
        x0,y0 = pts[i]
        x1,y1 = pts[(i+1)%6]
        ax2.add_patch(FancyArrowPatch((x0,y0), (x1,y1), arrowstyle="-|>", mutation_scale=12, linewidth=1.5, color=ACCENT2, connectionstyle="arc3,rad=0.18"))
    ax2.text(0, 1.02, "Residue packets form one directed cycle", ha="center", fontsize=12.3, color=INK, fontweight="bold")
    ax2.text(0, -1.00, r"$S_1 P_{N,j} = P_{N,j+1} S_1$", ha="center", fontsize=11, color=SOFT)
    fig.suptitle("Periodic shift on 24 coordinates with 6 residue packets", x=0.08, y=0.98, ha="left", fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.08, 0.92, "The nonzero blocks occur exactly on the successor relation j → j+1.", fontsize=9.5, color=SOFT)
    _save(fig, out, "07_shift_packet_transfer")
    stems.append("07_shift_packet_transfer")

    # 8. Elliptic packet transfer.
    multiplication = np.array([[0, 1], [1, 0]], dtype=float)
    fig = plt.figure(figsize=(7.8, 4.8))
    ax1 = fig.add_axes([0.08, 0.16, 0.42, 0.70])
    im = ax1.imshow(multiplication, cmap="viridis", aspect="equal", vmin=0, vmax=1)
    ax1.set_xticks([0,1], ["even", "odd"])
    ax1.set_yticks([0,1], ["even", "odd"])
    ax1.set_xlabel("input packet", color=INK)
    ax1.set_ylabel("output packet", color=INK)
    ax1.tick_params(colors=SOFT)
    for i in range(2):
        for j in range(2):
            ax1.text(j, i, str(int(multiplication[i,j])), ha="center", va="center", color="white" if multiplication[i,j] < 0.5 else INK, fontsize=13, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel("nonzero multiplication block", color=SOFT)
    cbar.ax.tick_params(colors=SOFT)
    ax2 = fig.add_axes([0.58, 0.18, 0.35, 0.68])
    ax2.axis("off")
    ax2.text(0.0, 0.92, r"Coordinate ring", fontsize=12.5, fontweight="bold", color=INK)
    ax2.text(0.0, 0.80, r"$k[x,y]/(y^2-x^3+x)$", fontsize=12, color=SOFT)
    ax2.text(0.0, 0.62, r"even packet: $k[x]$", fontsize=11, color=INK)
    ax2.text(0.0, 0.48, r"odd packet: $y\,k[x]$", fontsize=11, color=INK)
    ax2.text(0.0, 0.28, r"$M_y:$ even $\leftrightarrow$ odd", fontsize=12, color=ACCENT2)
    ax2.text(0.0, 0.14, r"$M_y^2 = M_{x^3-x}$", fontsize=12, color=ACCENT)
    fig.suptitle(r"Packet transfer for multiplication by $y$", x=0.08, y=0.98, ha="left", fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.08, 0.92, "The operator exchanges the parity packets, while the square returns to the even side.", fontsize=9.5, color=SOFT)
    _save(fig, out, "08_elliptic_packet_transfer")
    stems.append("08_elliptic_packet_transfer")

    # 9. Coordinate transport.
    rng = np.random.default_rng(COORDINATE_FIGURE_SEED)
    q = rng.normal(size=(12, 12))
    while abs(np.linalg.det(q)) < COORDINATE_DETERMINANT_CUTOFF:
        q = rng.normal(size=(12, 12))
    base = coordinate_projectors(12, [list(range(0, 4)), list(range(4, 8)), list(range(8, 12))])
    inv = np.linalg.inv(q)
    moved = [q @ p @ inv for p in base]
    gram = np.array([[np.linalg.norm(p @ r) for r in moved] for p in moved])
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    im = ax.imshow(gram, cmap="viridis", aspect="equal")
    _panel_title(ax, "Products of transported projectors", "Large diagonal values and near-zero off-diagonal products certify the transported packet system.")
    ax.set_xticks([0,1,2], [r"$Q_1$", r"$Q_2$", r"$Q_3$"])
    ax.set_yticks([0,1,2], [r"$Q_1$", r"$Q_2$", r"$Q_3$"])
    for i in range(3):
        for j in range(3):
            txt = f"{gram[i,j]:.2g}" if abs(gram[i,j]) < 1e-3 else f"{gram[i,j]:.2f}"
            ax.text(j, i, txt, ha="center", va="center", color="white" if gram[i,j] < gram.max()*0.55 else INK, fontsize=11, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel(r"$\|Q_i Q_j\|$", color=SOFT)
    cbar.ax.tick_params(colors=SOFT)
    ax.tick_params(colors=SOFT)
    for s in ax.spines.values():
        s.set_visible(False)
    _save(fig, out, "09_coordinate_transport")
    stems.append("09_coordinate_transport")

    # 10. Theorem dependency map.
    fig = plt.figure(figsize=(11.8, 4.5), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.text(0.7, 4.42, "Two proof families meet in the worked realizations", fontsize=14.5, color=INK, fontweight="bold")
    ax.text(0.7, 4.12, "This is a structural roadmap for the paper, not an extracted Lean dependency graph.", fontsize=9.7, color=SOFT)
    left_cluster = [(1.2, 2.9, "fixed operator\ngrammar"), (3.15, 2.9, "hulls and\npresentations"), (5.10, 2.9, "generator counts\nand bounds")]
    right_cluster = [(1.2, 1.2, "finite projector\nsystem"), (3.15, 1.2, "analysis and\nsynthesis"), (5.10, 1.2, "blocks and\ntransport")]
    final_node = (8.3, 2.05, "worked\nrealizations")
    for x, y, label in left_cluster:
        ax.add_patch(FancyBboxPatch((x, y), 1.5, 0.9, boxstyle="round,pad=0.03,rounding_size=0.08", facecolor=PALE2, edgecolor=ACCENT2, linewidth=1.5))
        ax.text(x+0.75, y+0.45, label, ha="center", va="center", fontsize=10.2, color=INK)
    for x, y, label in right_cluster:
        ax.add_patch(FancyBboxPatch((x, y), 1.5, 0.9, boxstyle="round,pad=0.03,rounding_size=0.08", facecolor=PALE, edgecolor=GREEN, linewidth=1.5))
        ax.text(x+0.75, y+0.45, label, ha="center", va="center", fontsize=10.2, color=INK)
    ax.add_patch(FancyBboxPatch((final_node[0], final_node[1]), 2.0, 1.05, boxstyle="round,pad=0.04,rounding_size=0.10", facecolor=BG, edgecolor=ACCENT, linewidth=1.8))
    ax.text(final_node[0]+1.0, final_node[1]+0.52, final_node[2], ha="center", va="center", fontsize=11.2, color=INK, fontweight="bold")
    for row in [left_cluster, right_cluster]:
        for (x1, y1, _), (x2, y2, _) in zip(row[:-1], row[1:]):
            ax.add_patch(FancyArrowPatch((x1+1.5, y1+0.45), (x2, y2+0.45), arrowstyle="-|>", mutation_scale=12, linewidth=1.4, color=SOFT))
    for x, y, _ in [left_cluster[-1], right_cluster[-1]]:
        ax.add_patch(FancyArrowPatch((x+1.5, y+0.45), (final_node[0], final_node[1]+0.52), arrowstyle="-|>", mutation_scale=12, linewidth=1.5, color=SOFT))
    ax.text(0.8, 3.95, "generator-theoretic line", color=ACCENT2, fontsize=10, fontweight="bold")
    ax.text(0.8, 0.80, "packet-theoretic line", color=GREEN, fontsize=10, fontweight="bold")
    ax.text(11.3, 2.45, r"coordinate invariance: $P_\alpha \mapsto U P_\alpha U^{-1}$", fontsize=10.4, color=SOFT)
    ax.text(11.3, 2.05, r"realization: $\Phi A = \varphi(A)\Phi$", fontsize=10.4, color=SOFT)
    ax.text(11.3, 1.65, r"transport: $Q_\beta A Q_\alpha$", fontsize=10.4, color=SOFT)
    _save(fig, out, "10_theorem_dependency")
    stems.append("10_theorem_dependency")

    return stems

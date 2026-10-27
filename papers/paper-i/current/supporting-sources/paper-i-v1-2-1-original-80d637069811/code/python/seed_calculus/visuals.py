from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from .core import krylov_rank_profile, semisimple_seed_rank, transfer_blocks
from .examples import bilateral_shift_matrix, companion_matrix, coordinate_projectors, repeated_jordan_operator, residue_projectors
from .graphs import cycle_adjacency, path_adjacency, symmetric_graph_seed_rank

FIGURE_DPI = 220
TRANSFER_FIGURE_SEED = 23
COORDINATE_FIGURE_SEED = 91
SHIFT_SUPPORT_TOLERANCE = 1e-10
COORDINATE_DETERMINANT_CUTOFF = 1e-6

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42


def _save(fig: plt.Figure, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.png", dpi=FIGURE_DPI, bbox_inches="tight")
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def generate_figures(output_dir: str | Path) -> list[str]:
    out = Path(output_dir)
    stems: list[str] = []

    # 1. Fixed seed grammar.
    fig, ax = plt.subplots(figsize=(11.5, 3.8))
    labels = ["seed", "address", "operate", "project", "constrain", "complete", "reconstruct"]
    x = np.arange(len(labels))
    for i in range(len(labels) - 1):
        ax.annotate(
            "",
            xy=(i + 1, 0),
            xytext=(i, 0),
            arrowprops={"arrowstyle": "->", "shrinkA": 9, "shrinkB": 9},
            zorder=2,
        )
    ax.scatter(x, np.zeros_like(x), s=220, zorder=3)
    for i, label in enumerate(labels):
        ax.text(i, 0.24, label, ha="center", va="bottom", fontsize=11)
    ax.set_xlim(-0.6, len(labels) - 0.4)
    ax.set_ylim(-0.8, 0.8)
    ax.axis("off")
    ax.set_title("The fixed production grammar of Paper I", pad=18)
    _save(fig, out, "01_seed_operator_grammar")
    stems.append("01_seed_operator_grammar")

    # 2. Transfer block norms.
    rng = np.random.default_rng(TRANSFER_FIGURE_SEED)
    n = 18
    projectors = coordinate_projectors(n, [list(range(0, 5)), list(range(5, 11)), list(range(11, 18))])
    operator = rng.normal(size=(n, n))
    blocks = transfer_blocks(operator, projectors)
    norms = np.array([[np.linalg.norm(block) for block in row] for row in blocks])
    fig, ax = plt.subplots(figsize=(6.7, 5.4))
    image = ax.imshow(norms, aspect="equal")
    fig.colorbar(image, ax=ax, label="Frobenius norm of embedded block")
    ax.set_xlabel("input packet alpha")
    ax.set_ylabel("output packet beta")
    ax.set_title("Operator resolved into transfer blocks")
    _save(fig, out, "02_transfer_block_norms")
    stems.append("02_transfer_block_norms")

    # 3. Krylov rank profiles.
    companion = np.array(companion_matrix([0, 0, 0, 0, 0, 0, 0, 0]), dtype=float)
    repeated = np.array(repeated_jordan_operator([4, 4], eigenvalue=2), dtype=float)
    seed_comp = np.zeros(8); seed_comp[0] = 1
    seed_rep = np.array([0, 0, 0, 1, 0, 0, 0, 1], dtype=float)
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    steps = np.arange(1, 9)
    ax.plot(steps, krylov_rank_profile(companion, seed_comp), marker="o", label="cyclic companion operator")
    ax.plot(steps, krylov_rank_profile(repeated, seed_rep), marker="s", label="two equal Jordan blocks")
    ax.set_xlabel("Krylov word length")
    ax.set_ylabel("generated span dimension")
    ax.set_title("One seed succeeds or stalls according to the operator module")
    ax.grid(alpha=0.25)
    ax.legend()
    _save(fig, out, "03_cyclic_rank_profiles")
    stems.append("03_cyclic_rank_profiles")

    # 4. Semisimple formula heatmap.
    ds = np.arange(1, 9)
    ms = np.arange(1, 25)
    grid = np.array([[semisimple_seed_rank([int(d)], [int(m)]) for m in ms] for d in ds])
    fig, ax = plt.subplots(figsize=(9.0, 5.5))
    image = ax.imshow(grid, origin="lower", aspect="auto")
    fig.colorbar(image, ax=ax, label="minimal number of seeds")
    ax.set_xticks(np.arange(0, len(ms), 2), ms[::2])
    ax.set_yticks(np.arange(len(ds)), ds)
    ax.set_xlabel("multiplicity m")
    ax.set_ylabel("simple-module dimension d")
    ax.set_title(r"Semisimple multiplicity law: $\lceil m/d\rceil$")
    _save(fig, out, "04_semisimple_seed_rank")
    stems.append("04_semisimple_seed_rank")

    # 5. Path graph seed ranks.
    ns = np.arange(2, 21)
    ranks = [symmetric_graph_seed_rank(path_adjacency(int(n))) for n in ns]
    fig, ax = plt.subplots(figsize=(7.7, 4.6))
    ax.plot(ns, ranks, marker="o")
    ax.set_xlabel("number of vertices")
    ax.set_ylabel("adjacency-algebra seed rank")
    ax.set_yticks([1])
    ax.set_title("Path graphs have one adjacency seed")
    ax.grid(alpha=0.25)
    _save(fig, out, "05_path_graph_seed_rank")
    stems.append("05_path_graph_seed_rank")

    # 6. Cycle graph seed ranks.
    ns = np.arange(3, 21)
    ranks = [symmetric_graph_seed_rank(cycle_adjacency(int(n))) for n in ns]
    fig, ax = plt.subplots(figsize=(7.7, 4.6))
    ax.plot(ns, ranks, marker="o")
    ax.set_xlabel("number of vertices")
    ax.set_ylabel("adjacency-algebra seed rank")
    ax.set_yticks(sorted(set(ranks)))
    ax.set_title("Cycle graphs require two adjacency seeds")
    ax.grid(alpha=0.25)
    _save(fig, out, "06_cycle_graph_seed_rank")
    stems.append("06_cycle_graph_seed_rank")

    # 7. Finite shift polyphase transfer pattern.
    shift = bilateral_shift_matrix(24)
    projectors = residue_projectors(24, 6)
    blocks = transfer_blocks(shift, projectors)
    pattern = np.array(
        [[int(np.linalg.norm(block) > SHIFT_SUPPORT_TOLERANCE) for block in row] for row in blocks]
    )
    fig, ax = plt.subplots(figsize=(6.5, 5.6))
    image = ax.imshow(pattern, aspect="equal", vmin=0, vmax=1)
    fig.colorbar(image, ax=ax, label="nonzero transfer")
    ax.set_xlabel("input residue packet")
    ax.set_ylabel("output residue packet")
    ax.set_title("The shift is a cyclic packet transfer")
    _save(fig, out, "07_shift_packet_transfer")
    stems.append("07_shift_packet_transfer")

    # 8. Elliptic coordinate-ring packet multiplication.
    multiplication = np.array([[0, 1], [1, 0]], dtype=float)
    fig, ax = plt.subplots(figsize=(5.8, 4.9))
    image = ax.imshow(multiplication, aspect="equal", vmin=0, vmax=1)
    fig.colorbar(image, ax=ax, label="nonzero block of multiplication by y")
    ax.set_xticks([0, 1], ["even input", "odd input"])
    ax.set_yticks([0, 1], ["even output", "odd output"])
    ax.set_title(r"Packet transfer for $M_y$ in $k[x,y]/(y^2-x^3+x)$")
    _save(fig, out, "08_elliptic_packet_transfer")
    stems.append("08_elliptic_packet_transfer")

    # 9. Coordinate transport preserves projector laws.
    rng = np.random.default_rng(COORDINATE_FIGURE_SEED)
    q = rng.normal(size=(12, 12))
    while abs(np.linalg.det(q)) < COORDINATE_DETERMINANT_CUTOFF:
        q = rng.normal(size=(12, 12))
    base = coordinate_projectors(12, [list(range(0, 4)), list(range(4, 8)), list(range(8, 12))])
    inv = np.linalg.inv(q)
    moved = [q @ p @ inv for p in base]
    gram = np.array([[np.linalg.norm(p @ r) for r in moved] for p in moved])
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    image = ax.imshow(gram, aspect="equal")
    fig.colorbar(image, ax=ax, label="norm of product")
    ax.set_xlabel("transported packet")
    ax.set_ylabel("transported packet")
    ax.set_title("Idempotence and annihilation survive coordinate transport")
    _save(fig, out, "09_coordinate_transport")
    stems.append("09_coordinate_transport")

    # 10. Paper I theorem dependency layers.
    labels = ["typed grammar", "generated hull", "packet analysis", "transfer algebra", "seed rank", "functoriality", "worked models"]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11.3, 4.0))
    y = np.array([0, 0.4, 0.0, 0.4, 0.0, 0.4, 0.0])
    for i in range(len(labels) - 1):
        ax.annotate(
            "",
            xy=(i + 1, y[i + 1]),
            xytext=(i, y[i]),
            arrowprops={"arrowstyle": "->", "shrinkA": 9, "shrinkB": 9},
            zorder=2,
        )
    ax.scatter(x, y, s=220, zorder=3)
    for i, label in enumerate(labels):
        offset = 0.18 if y[i] > 0 else -0.18
        vertical_alignment = "bottom" if y[i] > 0 else "top"
        ax.text(
            i,
            y[i] + offset,
            label,
            ha="center",
            va=vertical_alignment,
            fontsize=10,
        )
    ax.set_xlim(-0.6, len(labels) - 0.4)
    ax.set_ylim(-0.7, 1.1)
    ax.axis("off")
    ax.set_title("Logical dependency of the foundational paper")
    _save(fig, out, "10_theorem_dependency")
    stems.append("10_theorem_dependency")

    return stems

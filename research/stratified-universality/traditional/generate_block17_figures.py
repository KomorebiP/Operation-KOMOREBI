from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)


def box(ax, xy, text, width=2.65, height=0.76, fontsize=11):
    x, y = xy
    p = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.2,
        facecolor="white",
        edgecolor="black",
    )
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize)
    return p


def arrow(ax, start, end, label=None, label_xy=None):
    a = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, linewidth=1.1)
    ax.add_patch(a)
    if label:
        x, y = label_xy if label_xy else ((start[0]+end[0])/2, (start[1]+end[1])/2)
        ax.text(x, y, label, ha="center", va="center", fontsize=9)

# Semantic diamond
fig, ax = plt.subplots(figsize=(7.2, 5.1))
ax.set_xlim(-4.2, 4.2)
ax.set_ylim(-3.1, 3.0)
ax.axis("off")
box(ax, (0, 2.05), r"$J=X/(N\cap M)$\n joint semantics", width=3.2)
box(ax, (-2.45, 0.15), r"$S=X/N$\n first view")
box(ax, (2.45, 0.15), r"$T=X/M$\n second view")
box(ax, (0, -1.95), r"$C=X/(N+M)$\n common interface", width=3.2)
arrow(ax, (-0.95, 1.67), (-1.95, 0.58))
arrow(ax, (0.95, 1.67), (1.95, 0.58))
arrow(ax, (-1.95, -0.28), (-0.95, -1.56))
arrow(ax, (1.95, -0.28), (0.95, -1.56))
ax.text(0, -2.72, r"$J\cong S\times_C T$", ha="center", va="center", fontsize=12)
fig.tight_layout()
fig.savefig(OUT / "block17_semantic_diamond.pdf", bbox_inches="tight")
plt.close(fig)

# Contract axes
fig, ax = plt.subplots(figsize=(9.0, 5.0))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 6.2)
ax.axis("off")
box(ax, (2.1, 4.65), r"weaker task\ncoarser quotient", width=2.8)
box(ax, (7.9, 4.65), r"stronger task\nmore retained information", width=3.1)
box(ax, (2.1, 1.35), r"restricted doctrine\nlarger optimized defect", width=3.1)
box(ax, (7.9, 1.35), r"enlarged doctrine\nsmaller optimized defect", width=3.1)
arrow(ax, (3.55, 4.65), (6.25, 4.65), r"task strengthening", (4.9, 5.02))
arrow(ax, (3.65, 1.35), (6.25, 1.35), r"admissibility enlargement", (4.95, 1.72))
arrow(ax, (2.1, 4.25), (2.1, 1.78), r"doctrine change", (1.25, 3.02))
arrow(ax, (7.9, 4.25), (7.9, 1.78), r"doctrine change", (8.75, 3.02))
ax.text(5.0, 3.0, "comparison square\nrequires a certified passport", ha="center", va="center", fontsize=11)
ax.plot([3.55, 6.35], [4.25, 1.78], linewidth=0.8, linestyle="--")
ax.plot([6.35, 3.55], [4.25, 1.78], linewidth=0.8, linestyle="--")
fig.tight_layout()
fig.savefig(OUT / "block19_contract_axes.pdf", bbox_inches="tight")
plt.close(fig)

from __future__ import annotations

from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

NAVY = "#17324D"
BLUE = "#3D6C8E"
TEAL = "#2F7A78"
ORANGE = "#B56A2B"
RED = "#9D4B4B"
GREEN = "#4F774F"
GRAY = "#5F6870"
PALE_BLUE = "#E7F0F6"
PALE_TEAL = "#E7F2F1"
PALE_ORANGE = "#F7EADF"
PALE_RED = "#F5E6E6"
PALE_GREEN = "#EAF2EA"
PALE_GRAY = "#F1F3F4"

plt.rcParams.update({
    "font.size": 9.4,
    "axes.titlesize": 12,
    "figure.dpi": 140,
    "savefig.dpi": 220,
    "font.family": "DejaVu Sans",
})


def box(ax, xy, wh, text, fc, ec, fontsize=9.5, lw=1.2):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=NAVY, zorder=3)
    return patch


def arrow(ax, start, end, text=None, color=GRAY, rad=0.0, lw=1.3, style="-|>"):
    patch = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=11,
        linewidth=lw, color=color,
        connectionstyle=f"arc3,rad={rad}", zorder=4,
    )
    ax.add_patch(patch)
    if text:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.024, text, ha="center", va="bottom",
                fontsize=8.2, color=color, zorder=5)
    return patch


# 1. Local Mahler atlas.
fig, ax = plt.subplots(figsize=(11.2, 6.2))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Normalized local Newton-Mahler and complete polyphase atlas", color=NAVY, pad=10)
box(ax, (0.035, 0.58), (0.22, 0.22),
    r"Continuous semantics" + "\n" + r"$f:\mathbb{Z}_p\to\mathbb{Z}_p$",
    PALE_BLUE, BLUE, fontsize=10)
box(ax, (0.295, 0.58), (0.22, 0.22),
    r"Mahler coefficients" + "\n" + r"$c_r=\Delta^r f(0),\quad c_r\to0$",
    PALE_GREEN, GREEN, fontsize=9.6)
box(ax, (0.555, 0.58), (0.19, 0.22),
    r"Clopen branch packet" + "\n" + r"$f_{a,s}(q)=f(p^a q+s)$",
    PALE_TEAL, TEAL, fontsize=9.4)
box(ax, (0.785, 0.58), (0.18, 0.22),
    r"Branch coefficients" + "\n" + r"$d_{s,k}=\sum_r c_r\Theta_{p^a,s}(r,k)$",
    PALE_ORANGE, ORANGE, fontsize=8.8)
arrow(ax, (0.255, 0.69), (0.295, 0.69), text="Mahler transform", color=GREEN)
arrow(ax, (0.515, 0.69), (0.555, 0.69), text="clopen analysis", color=TEAL)
arrow(ax, (0.745, 0.69), (0.785, 0.69), text="finite-window kernel", color=ORANGE)
arrow(ax, (0.875, 0.58), (0.875, 0.42), color=ORANGE)
arrow(ax, (0.64, 0.58), (0.64, 0.42), color=TEAL)
box(ax, (0.24, 0.18), (0.24, 0.18),
    r"Exact synthesis" + "\n" + r"$x=s+p^a q\Rightarrow f(x)=f_{a,s}(q)$",
    PALE_GRAY, GRAY, fontsize=9.4)
box(ax, (0.57, 0.18), (0.25, 0.18),
    r"Nested refinement" + "\n" + r"$(f_{a,s})_{b,t}=f_{a+b,s+p^a t}$",
    PALE_RED, RED, fontsize=9.2)
arrow(ax, (0.64, 0.42), (0.69, 0.36), text="strict coherence", color=RED)
arrow(ax, (0.875, 0.42), (0.79, 0.36), text="coefficient synthesis", color=ORANGE, rad=0.06)
arrow(ax, (0.48, 0.27), (0.57, 0.27), color=NAVY)
arrow(ax, (0.24, 0.27), (0.145, 0.58), text="piecewise on clopen cosets", color=BLUE, rad=-0.10)
ax.text(0.50, 0.065,
        r"The complete $p^a$-branch packet is reversible; one continuous branch is directional and loses the other cosets.",
        ha="center", va="center", color=NAVY, fontsize=10.1, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"local_mahler_atlas.{ext}", bbox_inches="tight")
plt.close(fig)


# 2. Typed bridge ladder.
fig, ax = plt.subplots(figsize=(11.1, 6.1))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("One affine branch has different status in four coefficient doctrines", color=NAVY, pad=10)
levels = [
    (0.76, "Characteristic-zero polynomial chart", r"$A_{M,s}^{(d)}$ invertible over $\mathbb{Q}_p$", PALE_BLUE, BLUE),
    (0.56, "Integral Mahler lattice", r"injective but nonsplit when $p\mid M$", PALE_GREEN, GREEN),
    (0.36, "Residue coefficient module", r"rank $\lfloor d/p^{v_p(M)}\rfloor+1$", PALE_ORANGE, ORANGE),
    (0.16, "Complete neighboring packet", r"split recovery over every declared base ring", PALE_TEAL, TEAL),
]
for y, title, formula, fc, ec in levels:
    box(ax, (0.18, y), (0.64, 0.125), title + "\n" + formula, fc, ec, fontsize=9.7)
for y1, y2 in ((0.76, 0.685), (0.56, 0.485), (0.36, 0.285)):
    arrow(ax, (0.50, y1), (0.50, y2), color=GRAY)
ax.text(0.085, 0.62, r"same integer" + "\n" + r"kernel matrix", ha="center", va="center", color=GRAY, fontsize=9)
ax.text(0.915, 0.62, r"different" + "\n" + r"bridge passport", ha="center", va="center", color=RED, fontsize=9, fontweight="bold")
ax.text(0.50, 0.055,
        r"Local injection, integral splitting, modular rank, and collective recovery are distinct theorem statements.",
        ha="center", va="center", color=NAVY, fontsize=10.1, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"local_channel_ladder.{ext}", bbox_inches="tight")
plt.close(fig)


# 3. Kernel support and prime-power sparsity.
def theta(M: int, s: int, r: int, k: int) -> int:
    return sum((-1) ** (k - j) * comb(k, j) * comb(M * j + s, r) for j in range(k + 1))

M, s, p, d = 4, 2, 2, 24
A = np.array([[theta(M, s, r, k) for r in range(d + 1)] for k in range(d + 1)], dtype=object)
exact_support = np.array([[1 if A[k, r] != 0 else 0 for r in range(d + 1)] for k in range(d + 1)], dtype=float)
mod_support = np.array([[1 if int(A[k, r]) % p else 0 for r in range(d + 1)] for k in range(d + 1)], dtype=float)
fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2), sharey=True)
for ax, data, title in [
    (axes[0], exact_support, r"Exact support of $\Theta_{4,2}(r,k)$"),
    (axes[1], mod_support, r"Residual support modulo $2$"),
]:
    ax.imshow(data, origin="lower", aspect="auto", interpolation="nearest", cmap="Greys")
    ax.set_title(title, color=NAVY)
    ax.set_xlabel("source Mahler degree r")
axes[0].set_ylabel("refined Mahler degree k")
axes[0].text(0.5, -0.18, r"triangular window: $k\leq r\leq4k+2$", transform=axes[0].transAxes,
             ha="center", color=GRAY, fontsize=9.3)
axes[1].text(0.5, -0.18, r"Frobenius window: $r=4k+u$, $0\leq u\leq2$", transform=axes[1].transAxes,
             ha="center", color=TEAL, fontsize=9.3)
fig.suptitle("Affine Mahler transfer: finite triangular support and prime-power residual sparsity", color=NAVY, y=1.02)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"polyphase_kernel_sparsity.{ext}", bbox_inches="tight")
plt.close(fig)


# 4. Precision tree.
fig, ax = plt.subplots(figsize=(11.1, 6.25))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Principal-unit refinement amplifies the certified Mahler slope", color=NAVY, pad=10)
level_y = {0: 0.80, 1: 0.59, 2: 0.38, 3: 0.17}
level_width = {0: 0.15, 1: 0.14, 2: 0.125, 3: 0.095}
centres = {}
for a in range(4):
    count = 2 ** a
    xs = np.linspace(0.50, 0.50, 1) if count == 1 else np.linspace(0.075, 0.925, count)
    centres[a] = list(xs)
    w = level_width[a]
    y = level_y[a]
    for j, cx in enumerate(xs):
        fc, ec = (PALE_GREEN, GREEN) if a < 2 else (PALE_TEAL, TEAL)
        box(ax, (cx - w / 2, y), (w, 0.105),
            f"a={a}, s={j}" + "\n" + rf"slope $L+{a}$", fc, ec, fontsize=7.9 if a == 3 else 8.4)
        if a > 0:
            parent = centres[a - 1][j // 2]
            py = level_y[a - 1]
            arrow(ax, (parent, py), (cx, y + 0.105), color=GRAY, lw=0.85)
ax.text(0.50, 0.055,
        r"If $C^H=I+p^LB$, then $C^{Hp^a}=I+p^{L+a}B_a$ and $v_p(c_{a,s,r})\geq(L+a)r$.",
        ha="center", va="center", color=NAVY, fontsize=9.6, fontweight="bold")
fig.tight_layout(pad=1.0)
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"local_precision_tree.{ext}", bbox_inches="tight")
plt.close(fig)


# 5. Two Mahler languages.
fig, ax = plt.subplots(figsize=(11.1, 5.9))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Two Mahler languages: related applications, different typed objects", color=NAVY, pad=10)
box(ax, (0.05, 0.54), (0.36, 0.27),
    r"Functional-Mahler / Cartier channel" + "\n" + r"$F(z)=R(z)F(z^p)$" + "\n" + r"formal coefficient series over a residue field" + "\n" + r"digit sections of the coefficient index",
    PALE_BLUE, BLUE, fontsize=9.5)
box(ax, (0.59, 0.54), (0.36, 0.27),
    r"Newton-Mahler / local channel" + "\n" + r"$f(x)=\sum_r c_r\binom{x}{r}$" + "\n" + r"continuous function on $\mathbb{Z}_p$" + "\n" + r"affine branches of the input variable",
    PALE_GREEN, GREEN, fontsize=9.5)
arrow(ax, (0.41, 0.68), (0.59, 0.68), color=RED, style="|-|")
ax.text(0.50, 0.735, "no unrestricted equivalence", ha="center", color=RED, fontsize=10, fontweight="bold")
box(ax, (0.30, 0.18), (0.40, 0.18),
    r"A typed bridge requires extra data" + "\n" + r"coefficient lifts, interpolation hypotheses, and preservation laws",
    PALE_ORANGE, ORANGE, fontsize=9.7)
arrow(ax, (0.23, 0.54), (0.42, 0.36), text="chosen lift", color=ORANGE, rad=0.04)
arrow(ax, (0.77, 0.54), (0.58, 0.36), text="chosen coefficient semantics", color=ORANGE, rad=-0.04)
ax.text(0.50, 0.065,
        "Equal terminology does not identify categories, variables, coefficient rings, or normalization targets.",
        ha="center", va="center", color=NAVY, fontsize=10.1, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"two_mahler_languages.{ext}", bbox_inches="tight")
plt.close(fig)

print("Generated Block 08 local Mahler and polyphase figures")

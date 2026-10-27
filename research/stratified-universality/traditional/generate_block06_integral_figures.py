from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

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
    "font.size": 9.5,
    "axes.titlesize": 12,
    "figure.dpi": 140,
    "savefig.dpi": 220,
    "font.family": "DejaVu Sans",
})


def box(ax, xy, wh, text, fc, ec, fontsize=9.5, lw=1.2, z=2):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=NAVY, zorder=z+1)
    return patch


def arrow(ax, start, end, text=None, color=GRAY, rad=0.0, lw=1.3, style="-|>"):
    a = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=11,
        linewidth=lw, color=color,
        connectionstyle=f"arc3,rad={rad}", zorder=4,
    )
    ax.add_patch(a)
    if text:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.025, text, ha="center", va="bottom",
                fontsize=8.5, color=color, zorder=5)
    return a


# Figure 1: saturation and reduction defect.
fig, ax = plt.subplots(figsize=(10.4, 5.5))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Integral saturation and the exact modular reduction defect", color=NAVY, pad=10)

# Ambient rational space.
box(ax, (0.04, 0.12), (0.50, 0.74), "",
    PALE_GRAY, GRAY, fontsize=11)
# Saturated and raw nested.
box(ax, (0.095, 0.22), (0.39, 0.52), "",
    PALE_BLUE, BLUE, fontsize=10)
box(ax, (0.15, 0.33), (0.28, 0.28),
    r"$M_k(a)=\mathrm{span}_{\mathbf{Z}}\mathcal{K}_k(a)$" + "\nraw section lattice",
    PALE_GREEN, GREEN, fontsize=9.5)
ax.text(0.29, 0.815, r"$V_{\mathbf{Q}}(a)$: finite rational section space",
        ha="center", va="center", color=GRAY, fontsize=10.5, fontweight="bold")
ax.text(0.29, 0.685,
        r"$L_k(a)=V_{\mathbf{Q}}(a)\cap\mathbf{Z}^{\mathbf{N}}$" + "\ncanonical saturated lattice",
        ha="center", va="center", color=BLUE, fontsize=9.6, fontweight="bold")
ax.text(0.29, 0.175, r"$C_k(a)=L_k(a)/M_k(a)$ finite",
        ha="center", va="center", color=RED, fontsize=10.5, fontweight="bold")

# Reduction exact sequence right.
box(ax, (0.62, 0.69), (0.31, 0.14),
    r"$C_k(a)[m]$" + "\nghost kernel",
    PALE_RED, RED, fontsize=9.5)
box(ax, (0.58, 0.43), (0.18, 0.14),
    r"$M_k(a)/mM_k(a)$" + "\nraw residues",
    PALE_GREEN, GREEN, fontsize=9)
box(ax, (0.79, 0.43), (0.18, 0.14),
    r"$L_k(a)/mL_k(a)$" + "\nsaturated residues",
    PALE_BLUE, BLUE, fontsize=9)
box(ax, (0.62, 0.17), (0.31, 0.14),
    r"$C_k(a)/mC_k(a)$" + "\nmissing quotient",
    PALE_ORANGE, ORANGE, fontsize=9.5)

arrow(ax, (0.715, 0.69), (0.68, 0.57), color=RED)
arrow(ax, (0.76, 0.50), (0.79, 0.50), text="inclusion mod $m$", color=NAVY)
arrow(ax, (0.88, 0.43), (0.82, 0.31), color=ORANGE)
ax.text(0.775, 0.62, "exact", ha="center", va="center",
        fontsize=9, color=NAVY, fontweight="bold")
ax.text(0.775, 0.365, "exact", ha="center", va="center",
        fontsize=9, color=NAVY, fontweight="bold")

ax.text(0.77, 0.07,
        r"$G_{k,m}\cong C_k(a)[m]$   and   $Q_{k,m}\cong C_k(a)/mC_k(a)$",
        ha="center", va="center", color=NAVY, fontsize=10.2)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"saturation_reduction_defect.{ext}", bbox_inches="tight")
plt.close(fig)


# Figure 2: prime-power tower.
fig, ax = plt.subplots(figsize=(10.6, 6.0))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Compatible prime-power towers: raw residues, semantic images, and completion", color=NAVY, pad=10)

levels = [1, 2, 3, 4]
ys = [0.73, 0.56, 0.39, 0.22]
for r, y in zip(levels, ys):
    box(ax, (0.06, y), (0.25, 0.105),
        rf"$M_k(a)/p^{r}M_k(a)$" + "\nraw module",
        PALE_GREEN, GREEN, fontsize=9)
    box(ax, (0.38, y), (0.25, 0.105),
        rf"$\overline{{M}}_{{k,p^{r}}}(a)$" + "\nsemantic image",
        PALE_TEAL, TEAL, fontsize=9)
    box(ax, (0.70, y), (0.23, 0.105),
        rf"$Q_{{k,p^{r}}}(a)$" + "\nmissing saturation",
        PALE_ORANGE, ORANGE, fontsize=9)
    arrow(ax, (0.31, y + 0.052), (0.38, y + 0.052), color=NAVY)
    arrow(ax, (0.63, y + 0.052), (0.70, y + 0.052), color=ORANGE)

for x in (0.185, 0.505, 0.815):
    for y1, y2 in zip(ys[:-1], ys[1:]):
        arrow(ax, (x, y1 - 0.005), (x, y2 + 0.11), color=GRAY, lw=1.0)

box(ax, (0.06, 0.035), (0.25, 0.105),
    r"$M_{k,p}(a)$" + "\nraw $p$-adic lattice",
    PALE_GREEN, GREEN, fontsize=9.5)
box(ax, (0.38, 0.035), (0.25, 0.105),
    r"$M_{k,p}(a)\subseteq L_{k,p}(a)$" + "\nsemantic inverse limit",
    PALE_TEAL, TEAL, fontsize=9.5)
box(ax, (0.70, 0.035), (0.23, 0.105),
    r"$C_k(a)_{(p)}$" + "\npersistent missing quotient",
    PALE_ORANGE, ORANGE, fontsize=9.5)

for x in (0.185, 0.505, 0.815):
    arrow(ax, (x, 0.22), (x, 0.145), color=NAVY, lw=1.2)

ax.text(0.34, 0.875, r"finite ghosts: $G_{k,p^r}=C_k(a)[p^r]$, inverse limit $0$",
        ha="center", color=RED, fontsize=10)
ax.text(0.81, 0.875, r"$\lim_{\leftarrow r}Q_{k,p^r}=C_k(a)_{(p)}$",
        ha="center", color=ORANGE, fontsize=10, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"prime_power_regular_tower.{ext}", bbox_inches="tight")
plt.close(fig)


# Figure 3: digit-sum effectivity hierarchy.
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.set_xlim(-0.08, 1.08)
ax.set_ylim(-0.1, 1.06)
ax.axis("off")
ax.set_title("Digit-sum orbit: actual sections, integral lifts, and the $p$-adic closure", color=NAVY, pad=10)

# Nested regions.
outer = FancyBboxPatch((0.05, 0.10), 0.90, 0.78,
                       boxstyle="round,pad=0.02,rounding_size=0.03",
                       facecolor=PALE_BLUE, edgecolor=BLUE, linewidth=1.5)
mid = FancyBboxPatch((0.14, 0.20), 0.70, 0.56,
                     boxstyle="round,pad=0.02,rounding_size=0.03",
                     facecolor=PALE_GREEN, edgecolor=GREEN, linewidth=1.5)
ray = FancyBboxPatch((0.25, 0.32), 0.47, 0.29,
                     boxstyle="round,pad=0.02,rounding_size=0.03",
                     facecolor=PALE_ORANGE, edgecolor=ORANGE, linewidth=1.5)
for pch in (outer, mid, ray):
    ax.add_patch(pch)

ax.text(0.50, 0.82, r"$\overline{\mathcal{O}_k(s_k)}^{\,p}=s_k+\mathbf{Z}_p$",
        ha="center", va="center", color=BLUE, fontsize=11, fontweight="bold")
ax.text(0.49, 0.70, r"$M_k(s_k)=\mathbf{Z}s_k\oplus\mathbf{Z}1$",
        ha="center", va="center", color=GREEN, fontsize=10.5, fontweight="bold")
ax.text(0.485, 0.57, r"$\mathcal{O}_k(s_k)=\{s_k+c:c\geq0\}$",
        ha="center", va="center", color=ORANGE, fontsize=10.2, fontweight="bold")

# Points.
ax.plot([0.34, 0.43, 0.52, 0.61], [0.43]*4, "o", color=ORANGE, markersize=6)
ax.text(0.475, 0.365, "actual section offsets $0,1,2,\\ldots$", ha="center", color=ORANGE, fontsize=8.8)
ax.plot([0.22], [0.29], "o", color=GREEN, markersize=8)
ax.text(0.22, 0.245, r"$s_k-1$", ha="center", color=GREEN, fontsize=9)
ax.text(0.22, 0.205, "integral, not an actual section", ha="center", color=GREEN, fontsize=8)
ax.plot([0.84], [0.29], "o", color=BLUE, markersize=8)
ax.text(0.84, 0.245, r"$s_k+\frac{1}{1-p^2}$", ha="center", color=BLUE, fontsize=9)
ax.text(0.84, 0.205, "$p$-adic, nonintegral", ha="center", color=BLUE, fontsize=8)

arrow(ax, (0.62, 0.43), (0.81, 0.30), text="Cauchy limit", color=BLUE, rad=-0.12)
ax.text(0.50, 0.04,
        r"$p$-adic effectivity $\supsetneq$ integral-lattice effectivity $\supsetneq$ actual-section effectivity",
        ha="center", va="center", color=NAVY, fontsize=10.5, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"digit_sum_padic_effectivity.{ext}", bbox_inches="tight")
plt.close(fig)

print("Generated Block 06 integral and prime-power figures")

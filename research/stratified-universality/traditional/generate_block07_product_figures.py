from __future__ import annotations

from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
GEN = ROOT / "generated"

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
            fontsize=fontsize, color=NAVY, zorder=z + 1)
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
                fontsize=8.3, color=color, zorder=5)
    return a


# Figure 1: Euler coordinate atlas.
fig, ax = plt.subplots(figsize=(10.8, 5.8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Canonical Euler coordinates for integral unit series", color=NAVY, pad=10)

box(ax, (0.04, 0.57), (0.25, 0.22),
    r"Exponent coordinates" + "\n" + r"$b=(b_1,b_2,\ldots)\in\mathbf{Z}^{\mathbf{N}}$",
    PALE_GREEN, GREEN, fontsize=10)
box(ax, (0.375, 0.57), (0.25, 0.22),
    r"Integral unit series" + "\n" + r"$A(z)=\prod_{m\geq1}(1-z^m)^{-b_m}$",
    PALE_BLUE, BLUE, fontsize=9.6)
box(ax, (0.71, 0.57), (0.25, 0.22),
    r"Ghost coordinates" + "\n" + r"$c_n=\sum_{d\mid n}d b_d$",
    PALE_TEAL, TEAL, fontsize=10)
box(ax, (0.375, 0.17), (0.25, 0.20),
    r"Coefficient recurrence" + "\n" + r"$n a_n=\sum_{j=1}^n c_j a_{n-j}$",
    PALE_ORANGE, ORANGE, fontsize=9.7)

arrow(ax, (0.29, 0.68), (0.375, 0.68), text="filtered Euler product", color=GREEN)
arrow(ax, (0.625, 0.68), (0.71, 0.68), text=r"$zA'/A$", color=TEAL)
arrow(ax, (0.71, 0.61), (0.625, 0.35), text="coefficient extraction", color=ORANGE, rad=-0.08)
arrow(ax, (0.375, 0.35), (0.29, 0.61), text="triangular recovery", color=BLUE, rad=-0.08)
arrow(ax, (0.835, 0.57), (0.835, 0.37), text="Mobius inversion", color=TEAL)
arrow(ax, (0.50, 0.57), (0.50, 0.37), color=ORANGE)

ax.text(0.50, 0.06,
        r"Finite prefixes are triangular: $(b_1,\ldots,b_N)\leftrightarrow(a_1,\ldots,a_N)\leftrightarrow(c_1,\ldots,c_N)$",
        ha="center", va="center", color=NAVY, fontsize=10.2, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"euler_coordinate_atlas.{ext}", bbox_inches="tight")
plt.close(fig)


# Figure 2: Multiplicative prime-power atlas.
fig, ax = plt.subplots(figsize=(11.1, 6.3))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Multiplicative functions as descent from prime-power local series", color=NAVY, pad=10)

box(ax, (0.035, 0.55), (0.22, 0.24),
    r"Global multiplicative function" + "\n" + r"$f(n)=\prod_{p^e\parallel n}f(p^e)$",
    PALE_BLUE, BLUE, fontsize=9.6)
box(ax, (0.305, 0.55), (0.22, 0.24),
    r"Prime-power seed series" + "\n" + r"$F_{f,p}(T)=\sum_{e\geq0}f(p^e)T^e$",
    PALE_GREEN, GREEN, fontsize=9.5)
box(ax, (0.575, 0.55), (0.18, 0.24),
    r"Local Euler exponents" + "\n" + r"$F_{f,p}=\prod_m(1-T^m)^{-\beta_{p,m}}$",
    PALE_TEAL, TEAL, fontsize=9.1)
box(ax, (0.805, 0.55), (0.16, 0.24),
    r"Local ghosts" + "\n" + r"$\gamma_{p,e}=\sum_{d\mid e}d\beta_{p,d}$",
    PALE_ORANGE, ORANGE, fontsize=9.1)

arrow(ax, (0.255, 0.67), (0.305, 0.67), color=BLUE)
arrow(ax, (0.525, 0.67), (0.575, 0.67), color=GREEN)
arrow(ax, (0.755, 0.67), (0.805, 0.67), color=TEAL)

box(ax, (0.16, 0.18), (0.27, 0.18),
    r"Dirichlet convolution" + "\n" + r"$(f*_{D}g)(p^e)=\sum_{r=0}^e f(p^r)g(p^{e-r})$",
    PALE_GRAY, GRAY, fontsize=9.3)
box(ax, (0.57, 0.18), (0.27, 0.18),
    r"Additive local coordinates" + "\n" + r"$\beta(f*_{D}g)=\beta(f)+\beta(g)$" + "\n" + r"$\gamma(f*_{D}g)=\gamma(f)+\gamma(g)$",
    PALE_RED, RED, fontsize=9.2)
arrow(ax, (0.415, 0.55), (0.30, 0.36), text="local Cauchy product", color=GRAY, rad=0.05)
arrow(ax, (0.66, 0.55), (0.70, 0.36), text="linearizes", color=RED, rad=-0.03)
arrow(ax, (0.43, 0.27), (0.57, 0.27), color=NAVY)

ax.text(0.50, 0.07,
        r"The local charts glue effectively because unique factorization makes every global coefficient depend on finitely many primes.",
        ha="center", va="center", color=NAVY, fontsize=10.1, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"multiplicative_prime_power_atlas.{ext}", bbox_inches="tight")
plt.close(fig)


# Figure 3: divisor ghost bridge.
fig, ax = plt.subplots(figsize=(11.0, 6.0))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("The divisor-ghost bridge between filtered products and multiplicative seeds", color=NAVY, pad=10)

box(ax, (0.04, 0.60), (0.23, 0.20),
    r"Multiplicative exponent" + "\n" + r"$b:\mathbf{N}_{\geq1}\to\mathbf{Z}$",
    PALE_GREEN, GREEN, fontsize=10)
box(ax, (0.38, 0.60), (0.23, 0.20),
    r"Euler product" + "\n" + r"$A_b(z)=\prod_{n\geq1}(1-z^n)^{-b(n)}$",
    PALE_BLUE, BLUE, fontsize=9.5)
box(ax, (0.72, 0.60), (0.23, 0.20),
    r"Multiplicative ghost" + "\n" + r"$c=\mathbf{1}*_{D}(\mathrm{id}\cdot b)$",
    PALE_TEAL, TEAL, fontsize=9.6)

arrow(ax, (0.27, 0.70), (0.38, 0.70), text="fixed Euler basis", color=GREEN)
arrow(ax, (0.61, 0.70), (0.72, 0.70), text=r"$zA_b'/A_b$", color=TEAL)
arrow(ax, (0.835, 0.60), (0.835, 0.40), text="prime-power seeds", color=TEAL)
arrow(ax, (0.72, 0.56), (0.27, 0.56), color=BLUE, rad=-0.20)
ax.text(0.50, 0.485, r"$b(n)=n^{-1}(\mu*_{D}c)(n)$", ha="center", va="center", color=BLUE, fontsize=9.3)

box(ax, (0.075, 0.18), (0.22, 0.16),
    r"$b(n)=1$" + "\n" + r"$c(n)=\sigma_1(n)$" + "\npartitions",
    PALE_ORANGE, ORANGE, fontsize=9.5)
box(ax, (0.39, 0.18), (0.22, 0.16),
    r"$b(n)=n$" + "\n" + r"$c(n)=\sigma_2(n)$" + "\nplane partitions",
    PALE_ORANGE, ORANGE, fontsize=9.5)
box(ax, (0.705, 0.18), (0.22, 0.16),
    r"$b(n)=n^r$" + "\n" + r"$c(n)=\sigma_{r+1}(n)$" + "\npower family",
    PALE_ORANGE, ORANGE, fontsize=9.5)

for x in (0.185, 0.50, 0.815):
    arrow(ax, (x, 0.40), (x, 0.34), color=ORANGE)

ax.text(0.50, 0.07,
        r"This is an exact cross-stratum invariant bridge, not an isomorphism between global Cauchy and Dirichlet convolution.",
        ha="center", va="center", color=RED, fontsize=10.0, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"divisor_ghost_bridge.{ext}", bbox_inches="tight")
plt.close(fig)


# Figure 4: two monoid boundary.
fig, ax = plt.subplots(figsize=(10.8, 5.9))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.set_title("Two index monoids: exact local overlap and the global boundary", color=NAVY, pad=10)

box(ax, (0.05, 0.58), (0.34, 0.24),
    r"Additive index channel" + "\n" + r"$[z^n](A B)=\sum_{i+j=n}a_i b_j$" + "\n" + r"addresses in $(\mathbf{N},+)$",
    PALE_BLUE, BLUE, fontsize=10)
box(ax, (0.61, 0.58), (0.34, 0.24),
    r"Multiplicative index channel" + "\n" + r"$(f*_{D}g)(n)=\sum_{d\mid n}f(d)g(n/d)$" + "\n" + r"addresses in $(\mathbf{N}_{\geq1},\times)$",
    PALE_GREEN, GREEN, fontsize=9.8)
box(ax, (0.35, 0.20), (0.30, 0.20),
    r"Exact valuation overlap at one prime" + "\n" + r"$e=v_p(n)$" + "\n" + r"Dirichlet convolution $\mapsto$ Cauchy convolution in $e$",
    PALE_TEAL, TEAL, fontsize=9.4)

arrow(ax, (0.29, 0.58), (0.42, 0.40), text="local series", color=BLUE, rad=0.05)
arrow(ax, (0.71, 0.58), (0.58, 0.40), text="prime packet", color=GREEN, rad=-0.05)

# crossed non-equivalence arrow.
arrow(ax, (0.39, 0.70), (0.61, 0.70), color=RED, style="|-|")
ax.text(0.50, 0.745, "no unrestricted algebra isomorphism", ha="center", color=RED, fontsize=9.8, fontweight="bold")
ax.text(0.50, 0.08,
        "A valid bridge must name its kernel, transform, essential image, and the information it forgets.",
        ha="center", va="center", color=NAVY, fontsize=10.1, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"two_monoid_boundary.{ext}", bbox_inches="tight")
plt.close(fig)

print("Generated Block 07 filtered-product and multiplicative figures")

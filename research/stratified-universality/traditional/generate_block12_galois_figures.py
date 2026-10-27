from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

BLUE = "#1f4e79"
PALE_BLUE = "#eaf2f8"
GREEN = "#2e6f40"
PALE_GREEN = "#eaf5ec"
ORANGE = "#a65f00"
PALE_ORANGE = "#fff1df"
RED = "#8c2d2d"
PALE_RED = "#faeaea"
GRAY = "#5e6770"
PALE_GRAY = "#f1f3f5"
NAVY = "#18324a"


def box(ax, xy, w, h, text, fc=PALE_BLUE, ec=BLUE, size=10, lw=1.4):
    x, y = xy
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.025", facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=NAVY, wrap=True)
    return p


def arrow(ax, a, b, text=None, color=GRAY, style="-|>", rad=0.0, lw=1.4):
    ar = FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=12, linewidth=lw, color=color, connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(ar)
    if text:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ax.text(mx, my + 0.025, text, ha="center", va="bottom", fontsize=8.5, color=color)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# 1. Subgroup / projector / fixed-field dictionary.
fig, ax = plt.subplots(figsize=(10.5, 5.4))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.5, 0.965, "Finite Galois charts form an order-reversing resolved atlas", ha="center", va="top", fontsize=15, fontweight="bold", color=NAVY)
box(ax, (0.04, 0.58), 0.25, 0.20, "Subgroup chart\n" + r"$H\leq G$", PALE_BLUE, BLUE, 12)
box(ax, (0.375, 0.58), 0.25, 0.20, "Reynolds packet\n" + r"$P_H=|H|^{-1}\sum_{h\in H}U_h$", PALE_GREEN, GREEN, 11)
box(ax, (0.71, 0.58), 0.25, 0.20, "Fixed-object chart\n$L^H$ or $V^H$", PALE_ORANGE, ORANGE, 12)
arrow(ax, (0.29, 0.68), (0.375, 0.68), r"$H\mapsto P_H$", BLUE)
arrow(ax, (0.625, 0.68), (0.71, 0.68), r"$\operatorname{ran}P_H$", GREEN)
arrow(ax, (0.71, 0.61), (0.625, 0.61), "recognition", ORANGE, style="<|-", rad=0.0)
ax.text(0.50, 0.50, r"$H\subseteq J\;\Longrightarrow\;P_H\geq P_J\;\Longrightarrow\;L^H\supseteq L^J$", ha="center", fontsize=11, color=NAVY)
box(ax, (0.08, 0.16), 0.26, 0.18, "Normality\n" + r"$H\triangleleft G$", PALE_GREEN, GREEN, 11)
box(ax, (0.39, 0.16), 0.26, 0.18, "Central compatibility\n$P_HU_g=U_gP_H$", PALE_BLUE, BLUE, 10.5)
box(ax, (0.70, 0.16), 0.22, 0.18, "Quotient symmetry\n$G/H$ on $V^H$", PALE_ORANGE, ORANGE, 10.5)
arrow(ax, (0.34, 0.25), (0.39, 0.25), "equivalent", GREEN)
arrow(ax, (0.65, 0.25), (0.70, 0.25), "compression", BLUE)
ax.text(0.5, 0.055, "Nonnormal subgroups remain conjugate charts connected by mixed corners, not one global quotient chart.", ha="center", fontsize=9.5, color=RED)
save(fig, "galois_subgroup_atlas")

# 2. Nonnormal atlas and Mackey packets.
fig, ax = plt.subplots(figsize=(10.7, 5.8))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.5, 0.965, "Conjugate fixed charts and double-coset transition packets", ha="center", va="top", fontsize=15, fontweight="bold", color=NAVY)
centers = [(0.18, 0.67), (0.50, 0.78), (0.82, 0.67)]
labels = ["$P_H$\n$L^H$", "$P_{gHg^{-1}}$\n$g(L^H)$", "$P_{kHk^{-1}}$\n$k(L^H)$"]
for c, lab in zip(centers, labels):
    box(ax, (c[0]-0.11, c[1]-0.09), 0.22, 0.18, lab, PALE_BLUE, BLUE, 11)
arrow(ax, (0.29, 0.69), (0.39, 0.75), "conjugation", BLUE)
arrow(ax, (0.61, 0.75), (0.71, 0.69), "conjugation", BLUE)
box(ax, (0.08, 0.28), 0.28, 0.17, "Core envelope\n" + r"$\operatorname{Core}_G(H)=\bigcap_g gHg^{-1}$", PALE_GREEN, GREEN, 10)
box(ax, (0.64, 0.28), 0.28, 0.17, "Normal-closure envelope\n" + r"$\operatorname{Ncl}_G(H)=\langle gHg^{-1}\rangle$", PALE_GREEN, GREEN, 10)
box(ax, (0.38, 0.26), 0.24, 0.21, "Mixed transition packets\n$K\\backslash G/H$\nMackey summands", PALE_ORANGE, ORANGE, 11)
for c in centers:
    arrow(ax, (c[0], c[1]-0.09), (0.50, 0.47), color=GRAY, rad=0.05 if c[0] < 0.5 else -0.05)
arrow(ax, (0.38, 0.365), (0.36, 0.365), color=GREEN)
arrow(ax, (0.62, 0.365), (0.64, 0.365), color=GREEN)
ax.text(0.5, 0.12, "$S_3$ model: a transposition subgroup gives three conjugate cubic charts; its core is $1$ and its normal closure is $S_3$.", ha="center", fontsize=9.5, color=NAVY)
ax.text(0.5, 0.055, "Double cosets are exact transition packets. They do not require the subgroup projectors to commute.", ha="center", fontsize=9.2, color=RED)
save(fig, "galois_mackey_packets")

# 3. Linear versus projective descent.
fig, ax = plt.subplots(figsize=(10.8, 5.8))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.5, 0.965, "Linear descent is effective; projective descent has a Brauer obstruction", ha="center", va="top", fontsize=15, fontweight="bold", color=NAVY)
box(ax, (0.04, 0.62), 0.25, 0.18, "Linear cocycle\n" + r"$a_{\sigma\tau}=a_\sigma\,\sigma(a_\tau)$", PALE_BLUE, BLUE, 10.5)
box(ax, (0.38, 0.62), 0.25, 0.18, "Hilbert 90\n" + r"$a_\sigma=B^{-1}\sigma(B)$", PALE_GREEN, GREEN, 11)
box(ax, (0.72, 0.62), 0.24, 0.18, "Global vector packet\n" + r"$W\otimes_KL\cong L^n$", PALE_GREEN, GREEN, 10.5)
arrow(ax, (0.29, 0.71), (0.38, 0.71), color=BLUE)
arrow(ax, (0.63, 0.71), (0.72, 0.71), color=GREEN)
box(ax, (0.04, 0.25), 0.25, 0.18, "Projective cocycle\n" + r"$[\alpha]\in H^1(G,\mathrm{PGL}_n)$", PALE_ORANGE, ORANGE, 10.5)
box(ax, (0.38, 0.25), 0.25, 0.18, "Connecting class\n" + r"$\delta([\alpha])\in\mathrm{Br}(L/K)$", PALE_RED, RED, 10.5)
box(ax, (0.72, 0.30), 0.24, 0.14, r"$\delta=0$: vector descent", PALE_GREEN, GREEN, 10)
box(ax, (0.72, 0.12), 0.24, 0.14, r"$\delta\neq0$: central simple algebra", PALE_RED, RED, 10)
arrow(ax, (0.29, 0.34), (0.38, 0.34), color=ORANGE)
arrow(ax, (0.63, 0.36), (0.72, 0.37), color=GREEN)
arrow(ax, (0.63, 0.31), (0.72, 0.19), color=RED)
ax.text(0.5, 0.055, "C/R example: A = [[0, 1], [-1, 0]] has A conjugate(A) = -I; the scalar defect -1 is the quaternionic class.", ha="center", fontsize=9.3, color=NAVY)
save(fig, "galois_descent_obstruction")

# 4. Ramification details.
fig, ax = plt.subplots(figsize=(10.6, 5.4))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.5, 0.965, "Ramification is a nested projector resolution", ha="center", va="top", fontsize=15, fontweight="bold", color=NAVY)
xs = [0.08, 0.28, 0.48, 0.68, 0.88]
labels = ["$P_0$\n inertia fixed", "$P_1$", "$P_2$", "$P_3$", "$I$"]
radii = [0.085, 0.12, 0.155, 0.19, 0.225]
for x, lab, rad in zip(xs, labels, radii):
    c = Circle((x, 0.60), rad, facecolor=PALE_BLUE if x < 0.88 else PALE_GREEN, edgecolor=BLUE if x < 0.88 else GREEN, linewidth=1.5)
    ax.add_patch(c)
    ax.text(x, 0.60, lab, ha="center", va="center", fontsize=9.5, color=NAVY)
    if x != xs[-1]:
        arrow(ax, (x + rad, 0.60), (xs[xs.index(x)+1] - radii[xs.index(x)+1], 0.60), color=GRAY)
for i, x in enumerate(xs[:-1]):
    ax.text((x + xs[i+1])/2, 0.34, f"$D_{i}=P_{i+1}-P_i$", ha="center", fontsize=9, color=ORANGE)
ax.text(0.5, 0.19, r"$a(V)=\sum_i \frac{|G_i|}{|G_0|}\,\mathrm{Tr}(I-P_i)$", ha="center", fontsize=13, color=NAVY)
ax.text(0.5, 0.08, "The Artin conductor is the weighted unresolved rank; the Swan conductor removes the tame level.", ha="center", fontsize=9.5, color=RED)
save(fig, "galois_ramification_resolution")

# 5. Profinite and Tannakian boundary.
fig, ax = plt.subplots(figsize=(10.8, 5.8))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.5, 0.965, "Finite quotient resolution and the Tannakian symmetry boundary", ha="center", va="top", fontsize=15, fontweight="bold", color=NAVY)
for i, (x, lab) in enumerate([(0.05, "$G/U_1$"), (0.23, "$G/U_2$"), (0.41, "$G/U_3$")]):
    box(ax, (x, 0.64), 0.14, 0.14, lab, PALE_BLUE, BLUE, 11)
    if i < 2:
        arrow(ax, (x + 0.14, 0.71), (x + 0.18, 0.71), color=BLUE)
box(ax, (0.62, 0.64), 0.31, 0.14, "Profinite limit\n" + r"$P_{U_n}\to I$ strongly", PALE_GREEN, GREEN, 11)
arrow(ax, (0.55, 0.71), (0.62, 0.71), color=GREEN)
box(ax, (0.06, 0.22), 0.25, 0.18, "Faithful additive or corner functor\npackets and transfers", PALE_GRAY, GRAY, 10)
box(ax, (0.38, 0.22), 0.25, 0.18, "Faithful exact tensor fiber functor\n" + r"$\omega:\mathcal{C}\to\mathrm{Vect}_k$", PALE_BLUE, BLUE, 10)
box(ax, (0.70, 0.22), 0.24, 0.18, "Reconstructed symmetry\n" + r"$\mathrm{Aut}^{\otimes}(\omega)$", PALE_ORANGE, ORANGE, 10.5)
arrow(ax, (0.31, 0.31), (0.38, 0.31), "extra tensor data", RED)
arrow(ax, (0.63, 0.31), (0.70, 0.31), "Tannaka", ORANGE)
ax.text(0.5, 0.08, "A faithful concrete realization does not by itself reconstruct a group scheme. Exact tensor preservation is the additional gate.", ha="center", fontsize=9.5, color=RED)
save(fig, "galois_profinite_tannakian")

print("generated Block 12 Galois figures")

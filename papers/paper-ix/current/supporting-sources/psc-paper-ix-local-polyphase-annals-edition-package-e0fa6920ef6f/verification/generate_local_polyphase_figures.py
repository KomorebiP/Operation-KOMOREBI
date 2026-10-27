from __future__ import annotations

from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

matplotlib.rcParams.update({
    "font.size": 10,
    "font.family": "serif",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.unicode_minus": True,
})


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT / name, bbox_inches="tight")
    plt.close()


def box(ax, x: float, y: float, text: str, fontsize: float = 11) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        bbox={"boxstyle": "round,pad=.45", "facecolor": "white", "edgecolor": "black"},
    )


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="->",
            mutation_scale=14,
            connectionstyle="arc3,rad=0",
            linewidth=1,
        )
    )


def vp(value: int, prime: int) -> int:
    if value == 0:
        return 10**6
    value = abs(value)
    answer = 0
    while value % prime == 0:
        value //= prime
        answer += 1
    return answer


def zigzag_numbers(nmax: int) -> list[int]:
    values = [0] * (nmax + 1)
    values[0] = 1
    for n in range(nmax):
        total = sum(comb(n, k) * values[k] * values[n - k] for k in range(n + 1))
        if n == 0:
            total += 1
        values[n + 1] = total // 2
    return values


def theta_polyphase(M: int, s: int, r: int, k: int) -> int:
    return sum((-1) ** (k - j) * comb(k, j) * comb(M * j + s, r) for j in range(k + 1))


# Exact local kernel weights
zigzag = zigzag_numbers(24)
depths = np.arange(0, 11)
odd_weights = [0 if m == 0 else 2 * m + vp(zigzag[2 * m + 1], 5) for m in depths]
dyadic_weights = [0 if m == 0 else 4 * m - 1 for m in depths]
plt.figure(figsize=(9.2, 5.4))
plt.plot(depths, odd_weights, marker="o", label="odd prime p equals 5")
plt.plot(depths, dyadic_weights, marker="s", label="dyadic exact depth")
plt.xlabel("transfer depth m")
plt.ylabel("kernel valuation")
plt.title("Odd and dyadic local Euler kernel weights")
plt.legend()
save("20_local_kernel_weight_profiles.pdf")


# Standard window Fourier transfer
plt.figure(figsize=(11.2, 4.7))
ax = plt.gca()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
box(ax, .10, .70, "periodic input\nFourier characters", 12)
box(ax, .36, .70, "choose " + r"$y^m=\chi$" + "\nroot of unity filter", 12)
box(ax, .64, .70, "finite modes\n" + r"$((1+\zeta y)^m)^n$", 12)
box(ax, .90, .70, r"$h$ periodic output" + "\n" + r"$n\geq1$", 12)
arrow(ax, (.20, .70), (.26, .70))
arrow(ax, (.47, .70), (.53, .70))
arrow(ax, (.75, .70), (.80, .70))
box(ax, .27, .28, "unit triangular\nwindow operator", 12)
box(ax, .56, .28, "automorphism\nof " + r"$V_h$", 12)
box(ax, .84, .28, "finite inverse signature\n" + r"$e_{n+h}=e_n$", 12)
arrow(ax, (.38, .28), (.45, .28))
arrow(ax, (.66, .28), (.73, .28))
arrow(ax, (.90, .59), (.84, .39))
ax.text(.5, .045, "The infinite inverse window problem reduces to one finite character calculation.", ha="center", fontsize=12)
save("21_standard_window_fourier_transfer.pdf")


# Odd and dyadic local geometry
plt.figure(figsize=(10.4, 4.8))
ax = plt.gca()
ax.axis("off")
cell_text = [
    ["torsion address", r"$j\;\mathrm{mod}\;(p-1)$", "sign and parity"],
    ["principal units", r"$1+p\mathbb{Z}_p$", r"$1+4\mathbb{Z}_2$"],
    ["base Mahler gain", "one p adic digit", "three binary digits"],
    ["Euler source", "remove one nonunit mode", "already unit normalized"],
    ["Euler kernel depth", r"$2m+v_p(Z_{2m+1})$", r"$4m-1$"],
]
table = ax.table(
    cellText=cell_text,
    colLabels=["coordinate", "odd prime p", "dyadic prime 2"],
    cellLoc="center",
    colLoc="center",
    loc="center",
    colWidths=[.28, .36, .36],
)
table.auto_set_font_size(False)
table.set_fontsize(13)
table.scale(1, 2.05)
ax.set_title("Odd and dyadic local geometries share reconstruction, not integral weights", fontsize=15, pad=12)
ax.text(
    .5,
    .025,
    "Character phase, principal unit depth, source normalization, and kernel valuation must be tracked separately.",
    ha="center",
    fontsize=12,
    transform=ax.transAxes,
)
save("22_odd_dyadic_local_geometry.pdf")


# Mahler polyphase kernel support and Frobenius sparsity
prime = 3
M = 9
address = 4
kmax = 8
rmax = M * (kmax - 1) + address
matrix = np.zeros((rmax + 1, kmax))
for r in range(rmax + 1):
    for k in range(kmax):
        matrix[r, k] = 1 if theta_polyphase(M, address, r, k) % prime != 0 else 0
plt.figure(figsize=(9.4, 6.3))
mesh = plt.pcolormesh(
    np.arange(kmax + 1) - 0.5,
    np.arange(rmax + 2) - 0.5,
    matrix,
    shading="flat",
    cmap="Greys",
    rasterized=False,
)
plt.xlim(-0.5, kmax - 0.5)
plt.ylim(-0.5, rmax + 0.5)
plt.xlabel("refined Mahler depth k")
plt.ylabel("source Mahler index r")
plt.title(r"Frobenius sparse kernel for $M=3^2$, $s=4$ modulo $3$")
plt.text(
    kmax - 0.55,
    rmax - 2,
    "black means nonzero modulo 3",
    ha="right",
    va="top",
    fontsize=10,
    bbox={"facecolor": "white", "edgecolor": "black", "pad": 3},
)
save("23_mahler_polyphase_kernel.pdf")


# Precision amplification tree
levels = np.arange(0, 7)
plt.figure(figsize=(9.4, 5.5))
plt.plot(levels, levels + 1, marker="o", label=r"odd prime step $(p-1)p^a$")
plt.plot(levels, levels + 3, marker="s", label=r"dyadic step $2^{a+1}$")
plt.xlabel("polyphase refinement depth a")
plt.ylabel("guaranteed valuation per Mahler depth")
plt.title("Principal unit precision amplification under prime power refinement")
plt.legend()
save("24_polyphase_precision_tree.pdf")

print("generated five local polyphase figures")

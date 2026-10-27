from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
GEN = ROOT / "generated"
FIG.mkdir(exist_ok=True)
GEN.mkdir(exist_ok=True)
DATA = json.loads((GEN / "block11_nonlinear_tree_validation.json").read_text(encoding="utf-8"))

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
PALE_GREEN = "#EAF2EA"
PALE_GRAY = "#F1F3F4"

plt.rcParams.update({
    "font.size": 9,
    "figure.dpi": 140,
    "savefig.dpi": 220,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def save(fig, stem: str) -> None:
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def box(ax, xy, wh, text, face, edge=NAVY, fontsize=9):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        facecolor=face, edgecolor=edge, linewidth=1.2,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=NAVY)
    return patch


def arrow(ax, start, end, label=None, color=GRAY, rad=0.0):
    arr = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.1, color=color, connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arr)
    if label:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.025, label, ha="center", va="bottom",
                fontsize=7.5, color=color)


# 1. Marked nonlinear atlas.
fig, ax = plt.subplots(figsize=(10.5, 5.0))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
box(
    ax, (0.04, 0.61), (0.20, 0.22),
    "Marked polynomial\nfixed-point system\n$(s,A_2,\\ldots,A_D;R)$",
    PALE_BLUE,
)
box(
    ax, (0.30, 0.61), (0.20, 0.22),
    "Complete packet jets\nand active hypergraph\n$A_{i\\mid j_1,\\ldots,j_m}$",
    PALE_TEAL,
)
box(ax, (0.56, 0.61), (0.18, 0.22),
    "Colored operadic\ntree grammar\nand tree series", PALE_ORANGE)
box(ax, (0.80, 0.61), (0.16, 0.22),
    "Exact packet\nfixed-point\nsystem", PALE_GREEN)
box(ax, (0.33, 0.17), (0.34, 0.20),
    "Unique selected fixed point $u$\nwith convergence / filtration certificate", PALE_GRAY)
arrow(ax, (0.24, 0.72), (0.30, 0.72), "resolve")
arrow(ax, (0.50, 0.72), (0.56, 0.72), "substitute")
arrow(ax, (0.74, 0.72), (0.80, 0.72), "packetize")
arrow(ax, (0.13, 0.61), (0.40, 0.37), "solve", BLUE)
arrow(ax, (0.65, 0.61), (0.58, 0.37), "sum", ORANGE)
arrow(ax, (0.88, 0.61), (0.63, 0.37), "synthesize", GREEN)
arrow(ax, (0.50, 0.37), (0.50, 0.61), "retain system data", RED, rad=0.05)
ax.text(0.5, 0.94, "Normalized atlas for a marked nonlinear system",
        ha="center", va="center", fontsize=13, fontweight="bold", color=NAVY)
ax.text(
    0.5, 0.06,
    "The semantic fixed point alone does not reconstruct the generating system; "
    "the atlas classifies marked systems.",
    ha="center", va="center", fontsize=8.5, color=GRAY,
)
save(fig, "nonlinear_marked_atlas")


# 2. Faà di Bruno compression counts.
rows = [row for row in DATA["term_count_table"] if row["colors"] == 3]
rows.sort(key=lambda row: row["n"])
ns = [row["n"] for row in rows]
raw_counts = [row["raw"] for row in rows]
compressed_counts = [row["compressed"] for row in rows]
fig, ax = plt.subplots(figsize=(8.5, 5.0))
ax.plot(ns, raw_counts, marker="o", linewidth=1.7,
        label="packet-labeled set partitions")
ax.plot(ns, compressed_counts, marker="s", linewidth=1.7,
        label="colored integer-partition profiles")
ax.set_yscale("log")
ax.set_xlabel("derivative order $n$")
ax.set_ylabel("number of symbolic terms (log scale)")
ax.set_title("Exact diagonal packet Faà di Bruno compression for three intermediate packets")
ax.grid(True, which="both", linewidth=0.35, alpha=0.45)
ax.legend(frameon=False)
save(fig, "faa_di_bruno_compression")


# 3. Residue signature for arity set {3,5}, N=12.
N = 12
arities = (3, 5)
period = math.gcd(*(m - 1 for m in arities))
g = math.gcd(N, period)
active = {j for j in range(N) if (j - 1) % g == 0}
fig, ax = plt.subplots(figsize=(7.0, 7.0))
ax.set_aspect("equal")
ax.axis("off")
for j in range(N):
    angle = 2 * math.pi * j / N + math.pi / 2
    x, y = math.cos(angle), math.sin(angle)
    face = PALE_GREEN if j in active else PALE_GRAY
    edge = GREEN if j in active else GRAY
    circ = Circle((x, y), 0.095, facecolor=face, edgecolor=edge, linewidth=1.5)
    ax.add_patch(circ)
    ax.text(x, y, str(j), ha="center", va="center", color=NAVY, fontweight="bold")
ax.text(0, 0.15, "$u=z+u^3+u^5$", ha="center", va="center", fontsize=14, color=NAVY)
ax.text(0, -0.05, "d_A = gcd(2,4) = 2",
        ha="center", va="center", fontsize=11, color=BLUE)
ax.text(0, -0.23, "active packet addresses: j = 1 mod 2",
        ha="center", va="center", fontsize=10, color=GREEN)
ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-1.3, 1.35)
ax.set_title("Finite tree-address signature at packet width $N=12$", color=NAVY, pad=14)
save(fig, "tree_residue_signature")


# 4. Singularity orbit mapping for q=5 and N=6.
q = 5
Nmap = 6
d = q - 1
gmap = math.gcd(d, Nmap)
h = d // gmap
rho = (q - 1) * q ** (-q / (q - 1))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.8))
for axis in (ax1, ax2):
    axis.set_aspect("equal")
    axis.axhline(0, linewidth=0.5, color="#AAAAAA")
    axis.axvline(0, linewidth=0.5, color="#AAAAAA")
    axis.set_xticks([])
    axis.set_yticks([])
for r in range(d):
    angle = 2 * math.pi * r / d
    z = rho * complex(math.cos(angle), math.sin(angle))
    ax1.scatter([z.real], [z.imag], s=65)
    ax1.text(z.real, z.imag + 0.045, f"$\\rho\\zeta_{r}$", ha="center", fontsize=8)
image_points = []
for r in range(d):
    angle = 2 * math.pi * r / d
    z = rho * complex(math.cos(angle), math.sin(angle))
    image_points.append(z ** Nmap)
unique: list[complex] = []
for z in image_points:
    if not any(abs(z - w) < 1e-10 for w in unique):
        unique.append(z)
for idx, z in enumerate(unique):
    ax2.scatter([z.real], [z.imag], s=75)
    ax2.text(z.real, z.imag + 0.006, f"image {idx + 1}", ha="center", fontsize=8)
ax1.set_title(f"source orbit: $q-1={d}$ points")
ax2.set_title(f"packet orbit after $x=z^{Nmap}$: $h={h}$ points")
ax1.set_xlim(-rho * 1.4, rho * 1.4)
ax1.set_ylim(-rho * 1.4, rho * 1.4)
r2 = rho ** Nmap
ax2.set_xlim(-r2 * 1.5, r2 * 1.5)
ax2.set_ylim(-r2 * 1.5, r2 * 1.5)
fig.suptitle("Dominant singularity orbit under arithmetic packetization",
             fontsize=13, color=NAVY)
save(fig, "tree_singularity_orbit")


# 5. Dependency core and exact elimination.
fig, ax = plt.subplots(figsize=(10.0, 4.8))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
box(ax, (0.04, 0.36), (0.13, 0.20), "packet 0\nexplicit", PALE_BLUE)
box(ax, (0.23, 0.36), (0.13, 0.20), "packet 1\nexplicit", PALE_BLUE)
box(ax, (0.43, 0.28), (0.24, 0.36),
    "cyclic SCC\npackets 2,3,4\nnonlinear core", PALE_ORANGE, edge=ORANGE)
box(ax, (0.75, 0.36), (0.16, 0.20), "packet 5\nreconstruct", PALE_GREEN)
arrow(ax, (0.17, 0.46), (0.23, 0.46))
arrow(ax, (0.36, 0.46), (0.43, 0.46))
arrow(ax, (0.67, 0.46), (0.75, 0.46))
arrow(ax, (0.55, 0.64), (0.62, 0.64), color=ORANGE, rad=-0.5)
arrow(ax, (0.62, 0.28), (0.50, 0.28), color=ORANGE, rad=-0.5)
ax.text(0.5, 0.86, "Condensation of the packet dependency hypergraph",
        ha="center", fontsize=13, fontweight="bold", color=NAVY)
ax.text(
    0.5, 0.10,
    "Acyclic singleton packets are substituted exactly; only cyclic SCCs require "
    "a coupled nonlinear solve.",
    ha="center", fontsize=9, color=GRAY,
)
save(fig, "nonlinear_dependency_core")


# LaTeX table: validation.
cat_order = [
    ("faa_profile_counts", "Colored profile counts"),
    ("faa_profile_orbits", "Orbit-size identity"),
    ("faa_exact_values", "Exact compressed Faà di Bruno values"),
    ("tree_fixed_point", "Polynomial fixed-point prefixes"),
    ("tree_support", "Finite tree-address signatures"),
    ("qary_formula", "Fuss-Catalan formulas"),
    ("qary_packets", "Exact q-ary packet systems"),
    ("qary_singularity", "Dominant-orbit combinatorics"),
    ("dependency_core", "Dependency-core reductions"),
]
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Exact finite verification for Block 11.}",
    r"\label{tab:block11-validation}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}Y r@{}}",
    r"\toprule",
    r"Validation class & Exact checks\\",
    r"\midrule",
]
for key, label in cat_order:
    lines.append(f"{label} & {DATA['categories'].get(key, 0):,}\\\\")
lines += [
    r"\midrule",
    f"\\textbf{{Block 11 total}} & \\textbf{{{DATA['checks']:,}}}\\\\",
    f"Cumulative Block 03--11 total & {DATA['cumulative']:,}\\\\",
    f"Failures & {len(DATA['failures'])}\\\\",
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]
(GEN / "block11_validation_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


# LaTeX table: compression counts for M=3.
count_rows = [row for row in DATA["term_count_table"] if row["colors"] == 3 and row["n"] <= 10]
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Raw and compressed diagonal Fa\`a di Bruno term counts for three intermediate packets.}",
    r"\label{tab:block11-faa-counts}",
    r"\small",
    r"\begin{tabular}{rrrr}",
    r"\toprule",
    r"Order $n$ & Raw packet terms & Colored profiles & Compression factor\\",
    r"\midrule",
]
for row in count_rows:
    factor = row["raw"] / row["compressed"]
    lines.append(
        f"{row['n']} & {row['raw']:,} & {row['compressed']:,} & {factor:.1f}\\\\"
    )
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "block11_faa_counts_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


# LaTeX table: marked tree phases.
selected = [
    (2, 5), (3, 4), (3, 5), (4, 4),
    (4, 6), (5, 6), (5, 7), (6, 10),
]
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Exact packet signatures for the marked full $q$-ary tree family $u=z+u^q$.}",
    r"\label{tab:block11-qary-phases}",
    r"\small",
    r"\begin{tabular}{rrrrrr}",
    r"\toprule",
    r"$q$ & $N$ & $g=\gcd(N,q-1)$ & Active packets & Packet orbit & Active addresses\\",
    r"\midrule",
]
for q, N in selected:
    gcd_value = math.gcd(N, q - 1)
    active_addresses = [j for j in range(N) if (j - 1) % gcd_value == 0]
    orbit_size = (q - 1) // gcd_value
    addr = ",".join(map(str, active_addresses))
    lines.append(
        f"{q} & {N} & {gcd_value} & {len(active_addresses)} & "
        f"{orbit_size} & $\\{{{addr}\\}}$\\\\"
    )
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(GEN / "block11_qary_phase_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Generated Block 11 figures and LaTeX tables")

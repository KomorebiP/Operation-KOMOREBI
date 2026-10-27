"""Redraw the rank illustrations without changing their original data ranges.

Run directly or import ``generate`` from the main figure rebuild script.
The two Krylov profiles are checked by exact rational row reduction. Graph
ranks are computed from the real symmetric adjacency spectra, as in the
original illustration. The semisimple table uses exact integer arithmetic.
"""
from fractions import Fraction
import json
from pathlib import Path

import numpy as np
from matplotlib.colors import PowerNorm
from matplotlib.patches import Circle

from common import canvas, clean_axes, footer, save, INK, MUTED, TEAL, GOLD, GRID, HEAT


def rational_rank(columns):
    rows = [[Fraction(value) for value in row] for row in zip(*columns)]
    pivot = 0
    for column in range(len(columns)):
        found = next((r for r in range(pivot, len(rows)) if rows[r][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        divisor = rows[pivot][column]
        rows[pivot] = [value / divisor for value in rows[pivot]]
        for r in range(len(rows)):
            if r != pivot and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[pivot])]
        pivot += 1
    return pivot


def krylov_profile(matrix, vector):
    columns, profile = [], []
    for _ in range(len(vector)):
        columns.append([int(v) for v in vector])
        profile.append(rational_rank(columns))
        vector = matrix @ vector
    return profile


def graph_seed_rank(n, cyclic):
    matrix = np.zeros((n, n))
    for i in range(n - 1):
        matrix[i, i + 1] = matrix[i + 1, i] = 1
    if cyclic:
        matrix[0, -1] = matrix[-1, 0] = 1
    values = np.linalg.eigvalsh(matrix)
    groups = []
    for value in values:
        if groups and abs(value - groups[-1][0]) < 1e-7:
            groups[-1][1] += 1
        else:
            groups.append([value, 1])
    return max(count for _, count in groups)


def draw_krylov(data):
    fig = canvas("One seed can span the space or stall",
                 "Two operators on an eight dimensional space give different Krylov profiles.",
                 height=3.9)
    ax = fig.add_axes([.11, .21, .83, .57])
    steps = np.arange(1, 9)
    ax.plot(steps, data["cyclic"], color=TEAL, linewidth=2.1,
            marker="o", markersize=6, label="Cyclic companion")
    ax.plot(steps, data["repeated"], color=GOLD, linewidth=2.1,
            marker="s", markersize=6, markerfacecolor="white",
            markeredgewidth=1.5, label="Two equal Jordan blocks")
    ax.text(8.25, 8, "rank 8", color=TEAL, fontsize=10.5, va="center")
    ax.text(8.25, 4, "rank 4", color=GOLD, fontsize=10.5, va="center")
    ax.set(xlim=(.7, 9.15), ylim=(.5, 8.65),
           xlabel="Number of Krylov vectors", ylabel="Generated span dimension")
    ax.set_xticks(steps)
    ax.set_yticks(np.arange(1, 9))
    clean_axes(ax)
    ax.legend(loc="upper left", frameon=False, fontsize=10.5,
              labelcolor=INK, handlelength=2.1, borderaxespad=.3)
    footer(fig, r"The vectors are $v, Tv, \ldots, T^{r-1}v$. Both profiles use one fixed seed.")
    save(fig, "03_cyclic_rank_profiles")


def draw_semisimple(data):
    fig = canvas(r"Semisimple seed rank: $\lceil m/d\rceil$",
                 "A simple module of dimension d can supply at most d multiplicity directions per seed.",
                 height=4.3)
    ax = fig.add_axes([.105, .32, .845, .46])
    image = ax.imshow(data, origin="lower", aspect="auto", cmap=HEAT,
                      norm=PowerNorm(gamma=.5, vmin=1, vmax=24), extent=(.5, 24.5, .5, 8.5))
    ax.set_xticks([1, 4, 8, 12, 16, 20, 24])
    ax.set_yticks(np.arange(1, 9))
    ax.set_xlabel("Multiplicity m", labelpad=5)
    ax.set_ylabel("Simple module dimension d", labelpad=6)
    ax.tick_params(labelsize=10, length=0, pad=5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(.5, 25.5, 1), minor=True)
    ax.set_yticks(np.arange(.5, 9.5, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=.4)
    ax.tick_params(which="minor", length=0)
    for d, m in [(1, 24), (2, 16), (4, 12), (8, 8)]:
        value = int(data[d - 1][m - 1])
        ax.text(m, d, str(value), fontsize=10.5, weight="bold",
                color="white" if value >= 10 else INK, ha="center", va="center")
    cbax = fig.add_axes([.31, .13, .47, .035])
    colorbar = fig.colorbar(image, cax=cbax, orientation="horizontal", ticks=[1, 4, 8, 12, 16, 20, 24])
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(labelsize=10, length=2, color=GRID)
    fig.text(.105, .147, "Minimal seeds", color=MUTED, fontsize=10.5, va="center")
    footer(fig, "Example: dimension 4 and multiplicity 12 require 3 seeds. Every cell uses exact integer arithmetic.")
    save(fig, "04_semisimple_seed_rank")


def example_graph(fig, cyclic):
    ax = fig.add_axes([.04, .635, .285, .185])
    if cyclic:
        angles = np.arange(6) * np.pi / 3
        points = np.column_stack((np.cos(angles), np.sin(angles)))
        for i in range(6):
            a, b = points[i], points[(i + 1) % 6]
            ax.plot([a[0], b[0]], [a[1], b[1]], color=MUTED, linewidth=1.3)
        for x, y in points:
            ax.add_patch(Circle((x, y), .11, facecolor=TEAL, edgecolor="white", linewidth=.7))
        ax.text(0, 0, r"$C_6$", fontsize=11, ha="center", va="center", color=TEAL)
        ax.set(xlim=(-1.3, 1.3), ylim=(-1.3, 1.3), aspect="equal")
    else:
        for i in range(5):
            ax.plot([i, i + 1], [0, 0], color=MUTED, linewidth=1.3)
        for i in range(6):
            ax.add_patch(Circle((i, 0), .105, facecolor=GOLD if i == 0 else TEAL,
                               edgecolor="white", linewidth=.7))
        ax.text(0, .34, r"$e_1$", fontsize=10.5, color=GOLD, ha="center", va="bottom")
        ax.text(2.5, -.4, r"$P_6$", fontsize=11, color=TEAL, ha="center", va="top")
        ax.set(xlim=(-.45, 5.45), ylim=(-.62, .68), aspect="equal")
    ax.axis("off")


def draw_graph_rank(ns, ranks, cyclic):
    title = "Two seeds for cycle adjacency" if cyclic else "One seed for path adjacency"
    subtitle = ("The chart shows cycle sizes from 3 to 20. Each has adjacency seed rank 2." if cyclic
                else "The chart shows path sizes from 2 to 20. Each has adjacency seed rank 1.")
    fig = canvas(title, subtitle, height=3.9)
    example_graph(fig, cyclic)
    explanation = ("The largest eigenspace has dimension 2.\nOne seed cannot span that eigenspace." if cyclic
                   else "An endpoint vector generates each path\nunder repeated adjacency action.")
    fig.text(.365, .742, explanation, fontsize=10.5, color=INK, va="center", linespacing=1.45)
    ax = fig.add_axes([.11, .21, .835, .385])
    color = GOLD if cyclic else TEAL
    ax.plot(ns, ranks, color=color, marker="o", linewidth=1.9, markersize=4.4)
    maximum = 3 if cyclic else 2
    ax.set(xlim=(min(ns) - .5, 20.5), ylim=(-.07, maximum + .12),
           xlabel="Number of vertices", ylabel="Adjacency seed rank")
    ax.set_xticks([min(ns), 5, 10, 15, 20])
    ax.set_yticks(np.arange(maximum + 1))
    clean_axes(ax)
    footer(fig, "The plotted finite range illustrates the general result proved in the text.")
    save(fig, "06_cycle_graph_seed_rank" if cyclic else "05_path_graph_seed_rank")


def generate():
    companion = np.zeros((8, 8), dtype=np.int64)
    for i in range(7):
        companion[i + 1, i] = 1
    repeated = np.diag([2] * 8)
    for offset in [0, 4]:
        for i in range(3):
            repeated[offset + i, offset + i + 1] = 1
    seed_companion = np.array([1, 0, 0, 0, 0, 0, 0, 0], dtype=np.int64)
    seed_repeated = np.array([0, 0, 0, 1, 0, 0, 0, 1], dtype=np.int64)
    profiles = {"cyclic": krylov_profile(companion, seed_companion),
                "repeated": krylov_profile(repeated, seed_repeated)}
    assert profiles == {"cyclic": list(range(1, 9)), "repeated": [1, 2, 3, 4, 4, 4, 4, 4]}
    grid = [[(m + d - 1) // d for m in range(1, 25)] for d in range(1, 9)]
    path_sizes = list(range(2, 21))
    cycle_sizes = list(range(3, 21))
    path_ranks = [graph_seed_rank(n, False) for n in path_sizes]
    cycle_ranks = [graph_seed_rank(n, True) for n in cycle_sizes]
    assert path_ranks == [1] * len(path_sizes)
    assert cycle_ranks == [2] * len(cycle_sizes)
    draw_krylov(profiles)
    draw_semisimple(grid)
    draw_graph_rank(path_sizes, path_ranks, False)
    draw_graph_rank(cycle_sizes, cycle_ranks, True)
    data = {"krylov_steps": list(range(1, 9)), "krylov_profiles": profiles,
            "simple_dimensions": list(range(1, 9)), "multiplicities": list(range(1, 25)),
            "semisimple_seed_ranks": grid, "path_sizes": path_sizes, "path_seed_ranks": path_ranks,
            "cycle_sizes": cycle_sizes, "cycle_seed_ranks": cycle_ranks,
            "validation": "Exact rational Krylov ranks and integer semisimple values. Graph spectra computed with NumPy using eigenvalue grouping tolerance 1e-7."}
    (Path(__file__).parent / "figure_data_ranks.json").write_text(json.dumps(data, indent=2) + "\n")
    return ["03_cyclic_rank_profiles", "04_semisimple_seed_rank", "05_path_graph_seed_rank", "06_cycle_graph_seed_rank"]


if __name__ == "__main__":
    print("Regenerated " + ", ".join(generate()))

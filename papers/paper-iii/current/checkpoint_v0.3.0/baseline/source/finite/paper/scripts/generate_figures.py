#!/usr/bin/env python3
"""Generate the deterministic schematic figures for Paper III."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "figures"

NAVY = "#164A76"
TEAL = "#17827B"
ORANGE = "#D9782D"
RED = "#B2473E"
GRAY = "#64727D"
LIGHT = "#EEF3F6"
DARK = "#17232C"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.dpi": 240,
            "text.color": DARK,
        }
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def node(ax: plt.Axes, xy: tuple[float, float], label: str, color: str = NAVY) -> None:
    circle = plt.Circle(xy, 0.09, facecolor="white", edgecolor=color, linewidth=2.5, zorder=3)
    ax.add_patch(circle)
    ax.text(*xy, label, ha="center", va="center", color=color, fontweight="bold", zorder=4)


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str,
    color: str = TEAL,
    dashed: bool = False,
) -> None:
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=20,
        linewidth=2.4,
        linestyle="--" if dashed else "-",
        color=color,
        shrinkA=28,
        shrinkB=28,
        zorder=2,
    )
    ax.add_patch(patch)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.075)
    ax.text(*midpoint, label, ha="center", va="center", color=color, fontweight="bold")


def edge_walk_figure() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.5), constrained_layout=True)
    fig.suptitle("Typed edge words become directed packet walks", fontsize=18, fontweight="bold")

    ax = axes[0]
    ax.set_title("Composable word")
    points = [(0.12, 0.58), (0.37, 0.58), (0.62, 0.58), (0.87, 0.58)]
    for index, point in enumerate(points):
        node(ax, point, rf"$P_{index}$")
    for index in range(3):
        arrow(ax, points[index], points[index + 1], rf"$e_{index + 1}$")
    ax.text(
        0.52,
        0.25,
        r"$L_{e_3}L_{e_2}L_{e_1}$ executes $e_1,e_2,e_3$",
        ha="center",
        va="center",
        color=NAVY,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": LIGHT, "edgecolor": "none"},
    )
    ax.text(0.52, 0.10, "One surviving endpoint block", ha="center", color=GRAY)

    ax = axes[1]
    ax.set_title("Broken interface")
    left = (0.15, 0.62)
    middle = (0.43, 0.62)
    wrong = (0.76, 0.78)
    source = (0.76, 0.43)
    node(ax, left, r"$P_i$")
    node(ax, middle, r"$P_j$")
    node(ax, wrong, r"$P_k$", ORANGE)
    node(ax, source, r"$P_\ell$", RED)
    arrow(ax, left, middle, r"$e$", TEAL)
    arrow(ax, source, wrong, r"$f$", RED, dashed=True)
    ax.text(0.62, 0.61, r"$j\ne\ell$", ha="center", color=RED, fontweight="bold")
    ax.text(
        0.52,
        0.20,
        r"$L_fL_e=0$",
        ha="center",
        fontsize=18,
        color=RED,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "#F8ECEA", "edgecolor": "none"},
    )
    ax.text(0.52, 0.08, "Target-row, source-column convention", ha="center", color=GRAY)

    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.savefig(OUTPUT_DIR / "typed_edge_walks.png", bbox_inches="tight")
    plt.close(fig)


def triangle(ax: plt.Axes, labels: tuple[str, str, str], color: str, prefix: str) -> None:
    points = [(0.20, 0.20), (0.80, 0.20), (0.50, 0.78)]
    for point, label in zip(points, labels, strict=True):
        node(ax, point, label, color)
    arrow(ax, points[0], points[1], rf"${prefix}_{{b\leftarrow a}}$", color)
    arrow(ax, points[1], points[2], rf"${prefix}_{{c\leftarrow b}}$", color)
    arrow(ax, points[2], points[0], rf"${prefix}_{{a\leftarrow c}}$", color)


def transport_figure() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.5), constrained_layout=True)
    fig.suptitle("Canonical transport and chosen connection data", fontsize=18, fontweight="bold")

    triangle(axes[0], ("a", "b", "c"), NAVY, "J")
    axes[0].set_title("Exact coordinate transport")
    axes[0].text(
        0.50,
        0.47,
        r"$J_{a\leftarrow c}J_{c\leftarrow b}J_{b\leftarrow a}=\mathrm{id}$",
        ha="center",
        color=NAVY,
        bbox={"boxstyle": "round,pad=0.38", "facecolor": LIGHT, "edgecolor": "none"},
    )
    axes[0].text(0.50, 0.04, "Forced by analysis-synthesis exactness", ha="center", color=GRAY)

    triangle(axes[1], ("a", "b", "c"), ORANGE, r"\Gamma")
    axes[1].set_title("Noncanonical connection")
    axes[1].text(
        0.50,
        0.47,
        r"$H_{c,b,a}=\Gamma_{a\leftarrow c}\Gamma_{c\leftarrow b}\Gamma_{b\leftarrow a}$",
        ha="center",
        color=ORANGE,
        bbox={"boxstyle": "round,pad=0.38", "facecolor": "#FFF1E7", "edgecolor": "none"},
    )
    axes[1].text(0.50, 0.08, r"Gauge change: $H^G=G_aHG_a^{-1}$", ha="center", color=GRAY)

    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.savefig(OUTPUT_DIR / "transport_vs_connection.png", bbox_inches="tight")
    plt.close(fig)


def obstruction_figure() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.5), constrained_layout=True)
    fig.suptitle("Packet-resolved holonomy obstruction", fontsize=18, fontweight="bold")

    ax = axes[0]
    ax.set_title("Input-output block resolution")
    n = 4
    for row in range(n):
        for column in range(n):
            highlighted = (row, column) == (1, 3)
            face = "#F5B57F" if highlighted else LIGHT
            edge = ORANGE if highlighted else "white"
            ax.add_patch(Rectangle((column, n - 1 - row), 1, 1, facecolor=face, edgecolor=edge, linewidth=2))
            ax.text(
                column + 0.5,
                n - 1 - row + 0.5,
                rf"$\mathrm{{Ob}}^{{{row}{column}}}$",
                ha="center",
                va="center",
                color=DARK,
                fontsize=11,
            )
    ax.set_xlim(-0.8, n + 0.1)
    ax.set_ylim(-0.7, n + 0.2)
    ax.set_aspect("equal")
    ax.set_xticks([index + 0.5 for index in range(n)], [rf"input ${index}$" for index in range(n)], rotation=25)
    ax.set_yticks([n - 0.5 - index for index in range(n)], [rf"output ${index}$" for index in range(n)])
    ax.tick_params(length=0, labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(2.0, -0.55, "Highlighted: packet mixing witness", ha="center", color=ORANGE, fontweight="bold")

    ax = axes[1]
    ax.set_title("Exact reconstruction and detection")
    lines = [
        r"$\mathrm{Ob} = H-\mathrm{id}$",
        r"$\mathrm{Ob}^{\mu\nu}=\Pi_\mu\mathrm{Ob}\Pi_\nu$",
        r"$\mathrm{Ob}=\sum_{\mu,\nu}\mathrm{Ob}^{\mu\nu}$",
    ]
    y_positions = [0.78, 0.52, 0.26]
    colors = [NAVY, TEAL, ORANGE]
    for text, y, color in zip(lines, y_positions, colors, strict=True):
        ax.text(
            0.5,
            y,
            text,
            ha="center",
            va="center",
            fontsize=18,
            color=color,
            bbox={"boxstyle": "round,pad=0.45", "facecolor": LIGHT, "edgecolor": "none"},
        )
    ax.add_patch(FancyArrowPatch((0.5, 0.69), (0.5, 0.61), arrowstyle="-|>", color=GRAY, mutation_scale=15))
    ax.add_patch(FancyArrowPatch((0.5, 0.43), (0.5, 0.35), arrowstyle="-|>", color=GRAY, mutation_scale=15))
    ax.text(0.5, 0.07, "All blocks vanish iff the total obstruction vanishes", ha="center", color=GRAY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    fig.savefig(OUTPUT_DIR / "holonomy_obstruction_blocks.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure()
    edge_walk_figure()
    transport_figure()
    obstruction_figure()


if __name__ == "__main__":
    main()

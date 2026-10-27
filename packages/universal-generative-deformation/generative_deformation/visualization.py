from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon

from .forest import PerturbationForest

INK = "#17202A"
BLUE = "#2E86AB"
TEAL = "#2A9D8F"
ORANGE = "#E69F00"
RED = "#D55E00"
PURPLE = "#7A5195"
SKY = "#56B4E9"
GREEN = "#4C956C"
GRAY = "#6B7280"
LIGHT = "#EEF2F4"
PAPER = "#FCFBF7"
PALETTE = [BLUE, TEAL, ORANGE, PURPLE, RED, GREEN, SKY]


def _apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 12,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
            "axes.edgecolor": "#4B5563",
            "axes.linewidth": 0.8,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "grid.color": "#CBD5E1",
            "grid.alpha": 0.45,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


_apply_style()


def _save(fig: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig.tight_layout()
    except Exception:
        pass
    fig.savefig(path.with_suffix(".png"), dpi=260, bbox_inches="tight", facecolor=PAPER)
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def _panel_label(ax: Any, label: str) -> None:
    ax.text(
        -0.06,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        color=INK,
        va="top",
    )


def _soft_grid(ax: Any, axis: str = "both") -> None:
    ax.grid(True, axis=axis, linewidth=0.7, alpha=0.45)
    ax.spines[["top", "right"]].set_visible(False)


def _node_box(ax: Any, xy: tuple[float, float], text: str, *, color: str = BLUE, width: float = 0.16, height: float = 0.105, fontsize: float = 8.0) -> None:
    x, y = xy
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor="white",
        edgecolor=color,
        linewidth=1.25,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=INK, zorder=4)


def _arrow(ax: Any, start: tuple[float, float], end: tuple[float, float], *, color: str = GRAY, rad: float = 0.0, lw: float = 1.0, alpha: float = 0.85) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=lw,
        color=color,
        alpha=alpha,
        connectionstyle=f"arc3,rad={rad}",
        zorder=2,
    )
    ax.add_patch(arrow)


def plot_three_layer_architecture(path: str | Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.5))

    ax = axes[0]
    ax.set_title("Raw route forest")
    ax.axis("off")
    positions = {"r": (0.5, 0.92), "a": (0.25, 0.66), "b": (0.5, 0.66), "c": (0.75, 0.66), "aa": (0.12, 0.36), "ab": (0.36, 0.36), "ba": (0.46, 0.36), "bb": (0.64, 0.36), "ca": (0.76, 0.36), "cb": (0.91, 0.36)}
    edges = [("r", "a"), ("r", "b"), ("r", "c"), ("a", "aa"), ("a", "ab"), ("b", "ba"), ("b", "bb"), ("c", "ca"), ("c", "cb")]
    for u, v in edges:
        _arrow(ax, positions[u], positions[v], color="#94A3B8", lw=0.9)
    labels = {"r": "$x_0$", "a": "$d_1$", "b": "$d_2$", "c": "$d_3$", "aa": "$d_1a$", "ab": "$d_1b$", "ba": "$d_2a$", "bb": "$d_2b$", "ca": "$d_3a$", "cb": "$d_3b$"}
    for key, xy in positions.items():
        _node_box(ax, xy, labels[key], color=BLUE if len(key) < 2 else TEAL, width=0.13, height=0.09)
    ax.text(0.5, 0.08, "Every path remains distinct, even when endpoints coincide.", ha="center", fontsize=8.5, color=GRAY)
    _panel_label(ax, "A")

    ax = axes[1]
    ax.set_title("Relation quotient")
    ax.axis("off")
    qpos = {"x": (0.5, 0.91), "u": (0.25, 0.63), "v": (0.65, 0.63), "w": (0.5, 0.30)}
    for start, end, rad, color in [("x", "u", 0, BLUE), ("x", "v", 0, BLUE), ("u", "w", -0.12, TEAL), ("v", "w", 0.12, ORANGE), ("w", "u", 0.25, PURPLE)]:
        _arrow(ax, qpos[start], qpos[end], color=color, rad=rad, lw=1.25)
    for key, label, color in [("x", "$[x_0]$", BLUE), ("u", "$[u]$", TEAL), ("v", "$[v]$", ORANGE), ("w", "$[w]$", PURPLE)]:
        _node_box(ax, qpos[key], label, color=color, width=0.16, height=0.10)
    ax.text(0.5, 0.08, "Equivalent routes merge. Cycles and multiple arrows can appear.", ha="center", fontsize=8.5, color=GRAY)
    _panel_label(ax, "B")

    ax = axes[2]
    ax.set_title("Completed boundary")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    intervals = [(0.06, 0.94)]
    for depth in range(5):
        y = 0.88 - 0.14 * depth
        next_intervals = []
        for left, right in intervals:
            gap = 0.18 * (right - left)
            mid = (left + right) / 2
            children = [(left, mid - gap / 2), (mid + gap / 2, right)]
            for child in children:
                ax.plot(child, [y, y], color=BLUE if depth < 3 else TEAL, linewidth=max(1.0, 4.0 - 0.55 * depth), solid_capstyle="round")
            next_intervals.extend(children)
        intervals = next_intervals
    routes = [0.17, 0.56, 0.84]
    for index, x in enumerate(routes):
        ax.scatter([x], [0.16], s=70, color=PALETTE[index], zorder=4)
        ax.plot([x, x], [0.18, 0.32], linestyle="--", linewidth=1.0, color=PALETTE[index])
    ax.text(0.5, 0.08, "Only branches satisfying the declared convergence law add limit objects.", ha="center", fontsize=8.5, color=GRAY)
    _panel_label(ax, "C")

    fig.suptitle("One generative calculus, three noninterchangeable mathematical layers", fontsize=15, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_state_dependent_direction_fibers(path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 6.0))
    ax.set_xlim(-0.4, 10.4)
    ax.set_ylim(-0.7, 5.5)
    ax.axis("off")

    nodes = [
        (1.5, 4.35, "$x_0$", BLUE, 5, "five root directions"),
        (4.95, 2.8, "$x_1$", TEAL, 3, "three regular directions"),
        (8.4, 2.8, "$x_2$", ORANGE, 7, "seven singular directions"),
    ]
    _arrow(ax, (2.1, 4.1), (4.35, 3.05), color=TEAL, lw=1.4)
    _arrow(ax, (2.1, 4.35), (7.75, 3.05), color=ORANGE, lw=1.4, rad=-0.04)
    ax.text(3.25, 3.82, "$d_1\in\mathcal D_{x_0}$", fontsize=9, color=TEAL)
    ax.text(5.25, 4.05, "$d_2\in\mathcal D_{x_0}$", fontsize=9, color=ORANGE)

    for cx, cy, label, color, count, subtitle in nodes:
        ax.add_patch(Circle((cx, cy), 0.43, facecolor="white", edgecolor=color, linewidth=2.0, zorder=4))
        ax.text(cx, cy, label, ha="center", va="center", fontsize=11, color=INK, zorder=5)
        angles = np.linspace(0.0, 2 * np.pi, count, endpoint=False) + 0.13
        for angle in angles:
            start = (cx + 0.47 * math.cos(angle), cy + 0.47 * math.sin(angle))
            end = (cx + 1.08 * math.cos(angle), cy + 1.08 * math.sin(angle))
            _arrow(ax, start, end, color=color, lw=1.05)
        ax.text(cx, cy - 1.25, subtitle, ha="center", color=GRAY, fontsize=8.5)

    ax.text(
        5.2,
        0.55,
        "$\mathcal D_{x_0}$ is queried once at the root.  After a child is created, the calculus queries $\mathcal D_{x_1}$ or $\mathcal D_{x_2}$ anew.",
        ha="center",
        fontsize=10,
        color=INK,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "edgecolor": "#CBD5E1"},
    )
    ax.set_title("The direction space is a bundle over objects, not one fixed menu copied down the tree", fontsize=14, color=INK)
    _save(fig, Path(path))


def plot_operadic_hyperforest(path: str | Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4))
    titles = ["Unary deformation", "Binary interaction", "Nested operadic tree"]
    for ax, title in zip(axes, titles):
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(title)

    ax = axes[0]
    _node_box(ax, (0.50, 0.80), "$x$", color=BLUE)
    _node_box(ax, (0.50, 0.50), "$d$", color=ORANGE, width=0.12)
    _node_box(ax, (0.50, 0.20), "$x\star d$", color=TEAL, width=0.22)
    _arrow(ax, (0.50, 0.74), (0.50, 0.56), color=BLUE)
    _arrow(ax, (0.50, 0.44), (0.50, 0.26), color=TEAL)
    ax.text(0.5, 0.05, "One input gives an ordinary edge.", ha="center", fontsize=8.5, color=GRAY)
    _panel_label(ax, "A")

    ax = axes[1]
    _node_box(ax, (0.28, 0.80), "$x$", color=BLUE)
    _node_box(ax, (0.72, 0.80), "$y$", color=PURPLE)
    ax.add_patch(Circle((0.50, 0.48), 0.075, facecolor=ORANGE, edgecolor=ORANGE, alpha=0.95))
    ax.text(0.50, 0.48, "$\Psi_2$", ha="center", va="center", fontsize=9, color="white")
    _node_box(ax, (0.50, 0.18), "$\Psi_2(x,y)$", color=TEAL, width=0.28)
    _arrow(ax, (0.31, 0.74), (0.46, 0.54), color=BLUE)
    _arrow(ax, (0.69, 0.74), (0.54, 0.54), color=PURPLE)
    _arrow(ax, (0.50, 0.40), (0.50, 0.25), color=TEAL)
    ax.text(0.5, 0.05, "Several inputs meet at one hyperedge.", ha="center", fontsize=8.5, color=GRAY)
    _panel_label(ax, "B")

    ax = axes[2]
    leaves = [(0.14, 0.82, "$a$", BLUE), (0.38, 0.82, "$b$", TEAL), (0.63, 0.82, "$c$", PURPLE), (0.86, 0.82, "$d$", ORANGE)]
    for x, y, label, color in leaves:
        _node_box(ax, (x, y), label, color=color, width=0.11, height=0.085)
    gates = [(0.26, 0.57, "$\Psi_2$", TEAL), (0.74, 0.57, "$\Psi_2$", ORANGE), (0.50, 0.30, "$\Psi_2$", RED)]
    for x, y, label, color in gates:
        ax.add_patch(Circle((x, y), 0.06, facecolor=color, edgecolor=color))
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, color="white")
    for start, end, color in [((0.14, 0.77), (0.23, 0.62), BLUE), ((0.38, 0.77), (0.29, 0.62), TEAL), ((0.63, 0.77), (0.71, 0.62), PURPLE), ((0.86, 0.77), (0.77, 0.62), ORANGE), ((0.26, 0.51), (0.46, 0.35), TEAL), ((0.74, 0.51), (0.54, 0.35), ORANGE)]:
        _arrow(ax, start, end, color=color)
    _node_box(ax, (0.50, 0.10), "$\Psi_2(\Psi_2(a,b),\Psi_2(c,d))$", color=RED, width=0.62, height=0.10, fontsize=7.5)
    _arrow(ax, (0.50, 0.24), (0.50, 0.16), color=RED)
    ax.text(0.5, 0.01, "Repeated interaction creates syntax trees before relations identify them.", ha="center", fontsize=8.2, color=GRAY)
    _panel_label(ax, "C")

    fig.suptitle("Multi-input directions turn the perturbation tree into a free operadic hyperforest", fontsize=14, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_raw_vs_quotient(forest: PerturbationForest, path: str | Path) -> None:
    raw = forest.raw_counts()
    quotient = forest.quotient_counts()
    depths = sorted(set(raw) | set(quotient))
    raw_values = np.array([raw.get(depth, 0) for depth in depths], dtype=float)
    quotient_values = np.array([quotient.get(depth, 0) for depth in depths], dtype=float)
    ratio = np.divide(raw_values, np.maximum(quotient_values, 1.0))

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.5))
    ax = axes[0]
    ax.semilogy(depths, raw_values, marker="o", linewidth=2.0, color=BLUE, label="raw paths")
    ax.semilogy(depths, quotient_values, marker="s", linewidth=2.0, color=TEAL, label="quotient objects")
    ax.fill_between(depths, quotient_values, raw_values, color=SKY, alpha=0.13)
    ax.set_xlabel("perturbation depth")
    ax.set_ylabel("count at exact depth")
    ax.set_title("Route growth versus object growth")
    ax.legend(frameon=False)
    _soft_grid(ax)
    _panel_label(ax, "A")

    ax = axes[1]
    ax.plot(depths, ratio, marker="o", linewidth=2.2, color=ORANGE)
    ax.fill_between(depths, 1, ratio, color=ORANGE, alpha=0.14)
    ax.axhline(1, linewidth=1.0, color=GRAY, linestyle="--")
    ax.set_xlabel("perturbation depth")
    ax.set_ylabel("raw paths per quotient object")
    ax.set_title("Average path multiplicity")
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Relations can compress an exponentially growing route forest into a small object family", fontsize=14, color=INK, y=1.03)
    _save(fig, Path(path))


def plot_integer_quotient_line(forest: PerturbationForest, path: str | Path) -> None:
    max_depth = min(max(forest.raw_counts()), 8)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.3), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    for depth in range(max_depth + 1):
        endpoints = list(range(-depth, depth + 1, 2))
        multiplicities = [math.comb(depth, (depth - endpoint) // 2) for endpoint in endpoints]
        sizes = 25 + 18 * np.log1p(multiplicities)
        ax.scatter(endpoints, [-depth] * len(endpoints), s=sizes, c=np.log1p(multiplicities), cmap="viridis", edgecolors="white", linewidths=0.5, zorder=3)
        for endpoint, mult in zip(endpoints, multiplicities):
            if depth <= 5:
                ax.text(endpoint, -depth + 0.18, str(mult), ha="center", va="bottom", fontsize=6.5, color=INK)
        if depth < max_depth:
            for endpoint in endpoints:
                _arrow(ax, (endpoint, -depth - 0.12), (endpoint - 1, -(depth + 1) + 0.12), color="#B8C4CE", lw=0.55, alpha=0.5)
                _arrow(ax, (endpoint, -depth - 0.12), (endpoint + 1, -(depth + 1) + 0.12), color="#B8C4CE", lw=0.55, alpha=0.5)
    ax.set_xlabel("integer endpoint")
    ax.set_ylabel("negative path depth")
    ax.set_title("Raw paths grouped by endpoint multiplicity")
    ax.set_yticks(range(0, -max_depth - 1, -1))
    ax.set_yticklabels(range(max_depth + 1))
    _soft_grid(ax)
    _panel_label(ax, "A")

    ax = axes[1]
    values = list(range(-max_depth, max_depth + 1))
    ax.scatter(values, [0] * len(values), s=80, color=TEAL, edgecolor="white", linewidth=0.6, zorder=3)
    for value in values:
        ax.text(value, 0.085 if value % 2 == 0 else -0.11, str(value), ha="center", fontsize=7)
        if value < max_depth:
            _arrow(ax, (value + 0.08, 0.01), (value + 0.92, 0.01), color=BLUE, rad=0.22, lw=0.8)
            _arrow(ax, (value + 0.92, -0.025), (value + 0.08, -0.025), color=ORANGE, rad=0.22, lw=0.8)
    ax.set_xlim(-max_depth - 0.8, max_depth + 0.8)
    ax.set_ylim(-0.32, 0.32)
    ax.set_yticks([])
    ax.set_xlabel("relation-reduced endpoint")
    ax.set_title("Quotient graph after all path merges")
    ax.grid(axis="x", alpha=0.35)
    ax.spines[["top", "right", "left"]].set_visible(False)
    _panel_label(ax, "B")
    fig.suptitle("The integer walk separates construction multiplicity from mathematical endpoints", fontsize=14, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_quotient_forest(
    forest: PerturbationForest,
    path: str | Path,
    *,
    max_nodes: int = 80,
    state_label: Any | None = None,
) -> None:
    nodes = sorted(forest.nodes.values(), key=lambda item: (item.min_depth, item.id))[:max_nodes]
    node_ids = {node.id for node in nodes}
    levels: dict[int, list[int]] = defaultdict(list)
    for node in nodes:
        levels[node.min_depth].append(node.id)
    positions: dict[int, tuple[float, float]] = {}
    for depth, ids in levels.items():
        xs = np.linspace(-1, 1, len(ids)) if len(ids) > 1 else [0]
        for x, node_id in zip(xs, ids):
            positions[node_id] = (float(x), -float(depth))
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    for edge in forest.edges.values():
        if edge.source not in node_ids or edge.target not in node_ids:
            continue
        x0, y0 = positions[edge.source]
        x1, y1 = positions[edge.target]
        _arrow(ax, (x0, y0 - 0.05), (x1, y1 + 0.05), color="#A8B4C0", lw=0.6)
    for node in nodes:
        x, y = positions[node.id]
        label = str(forest.system.serialize_state(node.state)) if state_label is None else str(state_label(node.state))
        if len(label) > 22:
            label = label[:19] + "..."
        ax.scatter([x], [y], s=55 + 10 * math.log1p(node.min_depth + 1), color=PALETTE[node.min_depth % len(PALETTE)], edgecolor="white", linewidth=0.5, zorder=3)
        ax.text(x, y + 0.11, label, ha="center", va="bottom", fontsize=6.5)
    ax.set_title("Relation-reduced deformation graph")
    ax.set_xlabel("objects within a depth")
    ax.set_ylabel("negative minimum depth")
    _soft_grid(ax)
    _save(fig, Path(path))


def plot_branch_convergence(values: Sequence[float], path: str | Path) -> None:
    values_arr = np.asarray(values, dtype=float)
    increments = np.abs(np.diff(values_arr))
    tail = np.array([np.sum(increments[index:]) for index in range(len(increments))]) if len(increments) else np.array([])
    fig, axes = plt.subplots(1, 2, figsize=(11.3, 4.4))
    ax = axes[0]
    ax.plot(range(len(values_arr)), values_arr, marker="o", markersize=3.8, linewidth=1.8, color=BLUE)
    ax.axhline(values_arr[-1], linestyle="--", linewidth=1.0, color=TEAL, label="finite-depth limit estimate")
    ax.set_xlabel("branch depth")
    ax.set_ylabel("endpoint value")
    ax.set_title("A selected route approaches a limit")
    ax.legend(frameon=False)
    _soft_grid(ax)
    _panel_label(ax, "A")

    ax = axes[1]
    if len(increments):
        ax.semilogy(range(1, len(values_arr)), increments, marker="o", markersize=3.5, color=ORANGE, label="step size")
        ax.semilogy(range(1, len(values_arr)), tail, linewidth=2.0, color=PURPLE, label="remaining variation bound")
    ax.set_xlabel("branch depth")
    ax.set_ylabel("absolute magnitude")
    ax.set_title("Summable increments certify completion")
    ax.legend(frameon=False)
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Infinite paths become mathematical objects only through a declared convergence certificate", fontsize=14, color=INK, y=1.03)
    _save(fig, Path(path))


def plot_cover_error(levels: Sequence[int], errors: Sequence[float], path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.5))
    ax = axes[0]
    ax.set_aspect("equal")
    circle = Circle((0, 0), 1, facecolor="none", edgecolor="#94A3B8", linewidth=1.0)
    ax.add_patch(circle)
    for ring_index, (count, radius, color) in enumerate([(8, 1.0, BLUE), (16, 0.78, TEAL), (32, 0.56, ORANGE)]):
        angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
        ax.scatter(radius * np.cos(angles), radius * np.sin(angles), s=12 + 3 * ring_index, color=color, label=f"cover with {count} directions")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.axis("off")
    ax.set_title("Finite nets approximate a continuous direction fiber")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.14), ncol=1)
    _panel_label(ax, "A")

    ax = axes[1]
    ax.semilogy(levels, errors, marker="o", linewidth=2.1, color=PURPLE)
    ax.fill_between(levels, errors, min(errors) * 0.7, color=PURPLE, alpha=0.10)
    ax.set_xlabel("direction-cover level")
    ax.set_ylabel("certified endpoint error")
    ax.set_title("Refining the net shrinks the propagated error")
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Continuous direction spaces are represented by convergent covers, not a fictitious finite list", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))


def _draw_binary_tree(ax: Any, depth: int, x0: float, y0: float, width: float, height: float, color: str) -> None:
    levels = {0: [(x0, y0)]}
    for level in range(depth):
        levels[level + 1] = []
        for index, (x, y) in enumerate(levels[level]):
            span = width / (2 ** (level + 1))
            for sign in (-1, 1):
                child = (x + sign * span, y - height / max(depth, 1))
                _arrow(ax, (x, y - 0.01), (child[0], child[1] + 0.01), color=color, lw=0.55, alpha=0.55)
                levels[level + 1].append(child)
    for level_nodes in levels.values():
        ax.scatter([x for x, _ in level_nodes], [y for _, y in level_nodes], s=10, color=color, zorder=3)


def plot_catalan_growth(values: Sequence[int], path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.5))
    ax = axes[0]
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    centers = [0.12, 0.36, 0.62, 0.86]
    for index, center in enumerate(centers, start=1):
        _draw_binary_tree(ax, min(index, 3), center, 0.82, 0.12, 0.42, PALETTE[index - 1])
        ax.text(center, 0.18, f"order {index}", ha="center", fontsize=8)
        if index < len(values):
            ax.text(center, 0.08, f"{values[index]} shapes", ha="center", fontsize=8, color=GRAY)
    ax.set_title("Distinct parenthesized interaction trees")
    _panel_label(ax, "A")

    ax = axes[1]
    orders = np.arange(len(values))
    ax.semilogy(orders, values, marker="o", linewidth=2.1, color=RED)
    ax.fill_between(orders, 1, values, color=RED, alpha=0.10)
    ax.set_xlabel("interaction order")
    ax.set_ylabel("rooted binary tree count")
    ax.set_title("Catalan growth of nonlinear syntax")
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Repeated multi-input perturbations grow by tree shape before algebraic relations are imposed", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_partition_transition(s_values: Sequence[float], z_values: Sequence[float], path: str | Path) -> None:
    finite = np.array([min(value, 1e5) if math.isfinite(value) else 1e5 for value in z_values], dtype=float)
    s = np.asarray(s_values, dtype=float)
    # For the experiment b=3 and unit edge cost, so the exact threshold is log(3).
    threshold = math.log(3.0)
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.semilogy(s, finite, linewidth=2.2, color=BLUE)
    ax.axvline(threshold, linestyle="--", linewidth=1.4, color=RED, label="$s=\log 3$")
    ax.axvspan(s.min(), threshold, color=RED, alpha=0.09, label="divergent branch entropy")
    ax.axvspan(threshold, s.max(), color=TEAL, alpha=0.08, label="convergent weighted forest")
    ax.set_xlabel("inverse complexity weight $s$")
    ax.set_ylabel("weighted path partition function")
    ax.set_title("A branching forest has a sharp complexity threshold")
    ax.legend(frameon=False, ncol=2, loc="upper right")
    _soft_grid(ax)
    _save(fig, Path(path))


def plot_family_complexity(operations: Sequence[int], depths: Sequence[int], labels: Sequence[str], path: str | Path) -> None:
    plot_expression_complexity_clean(operations, depths, labels, labels[:3], path)


def plot_selected_expression_graph(forest: PerturbationForest, selected_labels: Sequence[str], path: str | Path) -> None:
    serialized = {str(forest.system.serialize_state(node.state)): node for node in forest.nodes.values()}
    nodes = [serialized[label] for label in selected_labels if label in serialized]
    node_ids = {node.id for node in nodes}
    levels: dict[int, list[Any]] = defaultdict(list)
    for node in nodes:
        levels[node.min_depth].append(node)
    positions: dict[int, tuple[float, float]] = {}
    for depth, level_nodes in sorted(levels.items()):
        level_nodes.sort(key=lambda node: selected_labels.index(str(forest.system.serialize_state(node.state))))
        xs = np.linspace(0.06, 0.94, len(level_nodes)) if len(level_nodes) > 1 else np.array([0.5])
        for x, node in zip(xs, level_nodes):
            positions[node.id] = (float(x), 0.92 - 0.27 * depth)

    direction_colors = {
        "differentiate": BLUE,
        "reciprocal": PURPLE,
        "log_derivative": ORANGE,
        "square": RED,
        "even_projection": TEAL,
        "odd_projection": GREEN,
        "double_argument": SKY,
    }
    fig, ax = plt.subplots(figsize=(12.4, 6.2))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for edge in forest.edges.values():
        if edge.source in node_ids and edge.target in node_ids:
            x0, y0 = positions[edge.source]
            x1, y1 = positions[edge.target]
            color = direction_colors.get(edge.direction.name, GRAY)
            _arrow(ax, (x0, y0 - 0.045), (x1, y1 + 0.045), color=color, lw=0.9, alpha=0.55)
    for node in nodes:
        x, y = positions[node.id]
        label = str(forest.system.serialize_state(node.state))
        color = TEAL if node.invariants.get("even") else ORANGE if node.invariants.get("odd") else BLUE
        _node_box(ax, (x, y), f"${label.replace('**', '^')}$" if "**" not in label else label, color=color, width=0.145, height=0.085, fontsize=7.1)
    legend_items = [(name.replace("_", " "), color) for name, color in direction_colors.items()]
    for index, (name, color) in enumerate(legend_items):
        x = 0.04 + (index % 4) * 0.24
        y = 0.05 + (index // 4) * 0.05
        ax.plot([x, x + 0.035], [y, y], color=color, linewidth=2.0)
        ax.text(x + 0.045, y, name, va="center", fontsize=7.5, color=INK)
    ax.set_title("Selected quotient descendants of $\cosh x$ with operation types retained on the edges", fontsize=14, color=INK)
    _save(fig, Path(path))


def plot_expression_complexity_clean(operations: Sequence[int], depths: Sequence[int], labels: Sequence[str], selected: Sequence[str], path: str | Path) -> None:
    operations_arr = np.asarray(operations, dtype=float)
    depths_arr = np.asarray(depths, dtype=float)
    jitter = np.zeros_like(depths_arr)
    offsets: dict[int, int] = defaultdict(int)
    for index, depth in enumerate(depths):
        local = offsets[int(depth)]
        offsets[int(depth)] += 1
        jitter[index] = 0.018 * ((local % 13) - 6)
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    scatter = ax.scatter(depths_arr + jitter, operations_arr, c=operations_arr, cmap="viridis", s=30, alpha=0.72, edgecolor="white", linewidth=0.3)
    for x, depth, operation, label in zip(depths_arr + jitter, depths, operations, labels):
        if label in set(selected):
            ax.annotate(label, (x, operation), xytext=(6, 5), textcoords="offset points", fontsize=8, arrowprops={"arrowstyle": "-", "color": GRAY, "lw": 0.6})
    ax.set_xlabel("minimum perturbation depth")
    ax.set_ylabel("symbolic operation count")
    ax.set_title("Route depth and expression complexity are independent coordinates")
    ax.set_xticks(sorted(set(depths)))
    _soft_grid(ax)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("operation count")
    _save(fig, Path(path))


def plot_generative_landscape(path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(13.0, 7.0))
    ax.axis("off")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.02, 1.05)
    # completion boundary
    theta = np.linspace(0, 2 * np.pi, 500)
    ax.plot(np.cos(theta), np.sin(theta), color="#CBD5E1", linewidth=2.0)
    ax.text(0, 1.0, "completed boundary of convergent routes", ha="center", va="bottom", fontsize=10, color=GRAY)
    # layered tree in polar coordinates
    rng = np.random.default_rng(4)
    layers: list[list[tuple[float, float]]] = [[(0.0, 0.0)]]
    branch_counts = [1, 5, 13, 26]
    for depth, count in enumerate(branch_counts[1:], start=1):
        angles = np.linspace(-0.88 * np.pi, 0.88 * np.pi, count) + rng.normal(0, 0.018, count)
        radius = 0.24 * depth
        layers.append([(radius * math.cos(angle), radius * math.sin(angle)) for angle in angles])
    # connect nearest parents
    for depth in range(1, len(layers)):
        for child_index, child in enumerate(layers[depth]):
            parent = layers[depth - 1][int(child_index * len(layers[depth - 1]) / len(layers[depth]))]
            _arrow(ax, parent, child, color="#A9B6C3", lw=0.55, alpha=0.55)
    # merge selected quotient nodes by arcs
    for depth, layer in enumerate(layers):
        for index, xy in enumerate(layer):
            color = PALETTE[(depth + index) % len(PALETTE)]
            size = 55 if depth == 0 else 22
            ax.scatter([xy[0]], [xy[1]], s=size, color=color, edgecolor="white", linewidth=0.4, zorder=3)
    merge_pairs = [(layers[3][3], layers[3][7]), (layers[3][15], layers[3][19]), (layers[2][2], layers[2][8])]
    for left, right in merge_pairs:
        mid = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)
        ax.plot([left[0], mid[0], right[0]], [left[1], mid[1] + 0.05, right[1]], color=RED, linewidth=1.3, linestyle="--")
    # three infinite routes to boundary
    routes = [layers[3][1], layers[3][13], layers[3][-2]]
    boundary_points = [(-0.82, -0.57), (0.25, -0.97), (0.89, 0.45)]
    for start, end, color in zip(routes, boundary_points, [TEAL, PURPLE, ORANGE]):
        _arrow(ax, start, end, color=color, lw=1.8, alpha=0.9)
        ax.scatter([end[0]], [end[1]], s=85, color=color, edgecolor="white", zorder=4)
    ax.text(-0.78, 0.65, "raw path expansion", fontsize=10, color=BLUE, bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": BLUE})
    ax.text(0.50, 0.58, "relation merges", fontsize=10, color=RED, bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": RED})
    ax.text(0.18, -0.72, "certified infinite routes", fontsize=10, color=PURPLE, bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": PURPLE})
    ax.set_title("The universal generative object is a forest of routes, a quotient of objects, and a boundary of limits", fontsize=15, color=INK)
    _save(fig, Path(path))


def plot_exploration_strategies(path: str | Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.7))
    strategy_titles = ["Breadth first", "Lowest cost", "Residual guided"]
    selected_orders = [list(range(15)), [0, 1, 2, 4, 3, 8, 5, 9, 6, 10, 7, 11, 12, 13, 14], [0, 2, 6, 13, 14, 5, 12, 1, 4, 10, 3, 8, 9, 7, 11]]
    positions: dict[int, tuple[float, float]] = {0: (0.5, 0.9)}
    node = 1
    for depth, count in [(1, 2), (2, 4), (3, 8)]:
        xs = np.linspace(0.08, 0.92, count)
        for x in xs:
            positions[node] = (float(x), 0.9 - 0.24 * depth)
            node += 1
    parents = {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4, 10: 4, 11: 5, 12: 5, 13: 6, 14: 6}
    scores = {index: value for index, value in enumerate([0.2, 0.4, 0.9, 0.1, 0.35, 0.75, 0.8, 0.1, 0.2, 0.3, 0.5, 0.4, 0.7, 0.95, 0.85])}
    for panel, (ax, title, order) in enumerate(zip(axes, strategy_titles, selected_orders)):
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        for child, parent in parents.items():
            _arrow(ax, positions[parent], positions[child], color="#C3CDD6", lw=0.55, alpha=0.7)
        rank = {node_id: idx for idx, node_id in enumerate(order)}
        for node_id, xy in positions.items():
            color = mpl.colormaps["viridis"](scores[node_id]) if panel == 2 else PALETTE[rank[node_id] % len(PALETTE)]
            ax.scatter([xy[0]], [xy[1]], s=75, color=color, edgecolor="white", linewidth=0.5, zorder=3)
            ax.text(xy[0], xy[1], str(rank[node_id] + 1), ha="center", va="center", fontsize=6.5, color="white", zorder=4)
        ax.set_title(title)
        ax.text(0.5, 0.03, ["uniform depth coverage", "cheap paths first", "high explanatory gain first"][panel], ha="center", fontsize=8.5, color=GRAY)
        _panel_label(ax, chr(ord("A") + panel))
    fig.suptitle("Finite exploration policies traverse the same infinite object in different orders", fontsize=14, color=INK, y=1.02)
    _save(fig, Path(path))


def _draw_small_graph(ax: Any, center: tuple[float, float], edges: Sequence[tuple[int, int]], *, n: int = 4, radius: float = 0.06, color: str = BLUE) -> None:
    cx, cy = center
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    pts = [(cx + radius * math.cos(angle), cy + radius * math.sin(angle)) for angle in angles]
    for u, v in edges:
        ax.plot([pts[u][0], pts[v][0]], [pts[u][1], pts[v][1]], color="#708090", linewidth=0.9, zorder=1)
    ax.scatter([x for x, _ in pts], [y for _, y in pts], s=22, color=color, edgecolor="white", linewidth=0.4, zorder=2)


def plot_graph_rewrite_atlas(forest: PerturbationForest, path: str | Path) -> None:
    nodes = sorted(forest.nodes.values(), key=lambda node: (int(node.invariants.get("edge_count", 0)), tuple(node.invariants.get("degree_sequence", [])), node.id))
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.2), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    ax.axis("off")
    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(-0.4, 4.6)
    grouped: dict[int, list[Any]] = defaultdict(list)
    for node in nodes:
        grouped[int(node.invariants.get("edge_count", 0))].append(node)
    positions: dict[int, tuple[float, float]] = {}
    for edge_count, group in sorted(grouped.items()):
        ys = np.linspace(0.25, 4.0, len(group)) if len(group) > 1 else [2.1]
        for y, node in zip(ys, group):
            x = float(edge_count)
            positions[node.id] = (x, float(y))
            edges = [tuple(map(int, edge)) for edge in forest.system.serialize_state(node.state)["edges"]]  # type: ignore[index]
            _draw_small_graph(ax, (x, float(y)), edges, radius=0.17, color=PALETTE[edge_count % len(PALETTE)])
            ax.text(x, float(y) - 0.28, f"deg {node.invariants.get('degree_sequence')}", ha="center", fontsize=6.2, color=GRAY)
    for edge in forest.edges.values():
        if edge.source in positions and edge.target in positions and edge.source != edge.target:
            start = positions[edge.source]
            end = positions[edge.target]
            if abs(start[0] - end[0]) <= 1.1:
                _arrow(ax, (start[0] + 0.18 * np.sign(end[0] - start[0]), start[1]), (end[0] - 0.18 * np.sign(end[0] - start[0]), end[1]), color="#CBD5E1", lw=0.35, alpha=0.30)
    ax.set_xticks(range(7))
    ax.set_xlabel("edge count")
    ax.set_title("All unlabelled four-vertex graph classes reached by edge toggles")
    _panel_label(ax, "A")

    ax = axes[1]
    raw = forest.raw_counts()
    quot = forest.quotient_counts()
    depths = sorted(raw)
    ax.semilogy(depths, [raw[d] for d in depths], marker="o", color=BLUE, linewidth=2.0, label="labelled toggle paths")
    ax.semilogy(depths, [quot.get(d, 0) for d in depths], marker="s", color=TEAL, linewidth=2.0, label="unlabelled graph classes")
    ax.set_xlabel("toggle depth")
    ax.set_ylabel("count")
    ax.set_title("Graph isomorphism removes route redundancy")
    ax.legend(frameon=False)
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Graph rewriting: local moves generate a large labelled tree but a small quotient atlas", fontsize=14, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_gaussian_family_atlas(forest: PerturbationForest, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.9))
    ax = axes[0]
    means = np.array([float(node.state[0]) for node in forest.nodes.values()])
    variances = np.array([float(node.state[1]) for node in forest.nodes.values()])
    depths = np.array([node.min_depth for node in forest.nodes.values()])
    scatter = ax.scatter(means, np.log2(variances), c=depths, cmap="viridis", s=60, edgecolor="white", linewidth=0.5)
    for edge in forest.edges.values():
        left = forest.nodes[edge.source].state
        right = forest.nodes[edge.target].state
        ax.plot([float(left[0]), float(right[0])], [math.log2(float(left[1])), math.log2(float(right[1]))], color="#C6D0D9", linewidth=0.45, alpha=0.35)
    ax.set_xlabel("mean $\mu$")
    ax.set_ylabel("$\log_2$ variance")
    ax.set_title("Exact location-scale-convolution lattice")
    _soft_grid(ax)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("minimum depth")
    _panel_label(ax, "A")

    ax = axes[1]
    xs = np.linspace(-5, 5, 500)
    targets = [(Fraction(0), Fraction(1)), (Fraction(1), Fraction(1)), (Fraction(0), Fraction(2)), (Fraction(-1), Fraction(1, 2)), (Fraction(2), Fraction(3))]
    for index, state in enumerate(targets):
        mean, variance = map(float, state)
        density = np.exp(-0.5 * (xs - mean) ** 2 / variance) / math.sqrt(2 * math.pi * variance)
        ax.plot(xs, density, linewidth=2.0, color=PALETTE[index], label=f"$N({mean:g},{variance:g})$")
    ax.set_xlabel("$x$")
    ax.set_ylabel("density")
    ax.set_title("Selected generated probability objects")
    ax.legend(frameon=False, ncol=2)
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Gaussian deformations show how translation, scale, symmetry, and convolution coexist in one grammar", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_elliptic_curve_atlas(forest: PerturbationForest, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0))
    ax = axes[0]
    a_vals = np.array([int(node.state[0]) for node in forest.nodes.values()])
    b_vals = np.array([int(node.state[1]) for node in forest.nodes.values()])
    core = np.array([abs(int(node.invariants["discriminant"])) for node in forest.nodes.values()], dtype=float)
    scatter = ax.scatter(a_vals, b_vals, c=np.log10(core + 1), cmap="plasma", s=65, edgecolor="white", linewidth=0.5)
    a_line = np.linspace(min(a_vals) - 1, -0.02, 300)
    b_line = np.sqrt(np.maximum(-4 * a_line**3 / 27, 0))
    ax.plot(a_line, b_line, color=RED, linestyle="--", linewidth=1.2, label="singular locus")
    ax.plot(a_line, -b_line, color=RED, linestyle="--", linewidth=1.2)
    invalid = [attempt for attempt in forest.invalid_attempts if "discriminant" in str(attempt.get("reason", ""))]
    ax.set_xlabel("coefficient $a$")
    ax.set_ylabel("coefficient $b$")
    ax.set_title(f"Valid coefficient descendants; {len(invalid)} singular attempts audited")
    ax.legend(frameon=False)
    _soft_grid(ax)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("$\log_{10}(|\Delta|+1)$")
    _panel_label(ax, "A")

    ax = axes[1]
    samples = [(-1, 0), (-1, 1), (-2, 1), (1, 1)]
    x = np.linspace(-3.2, 3.2, 900)
    for index, (a, b) in enumerate(samples):
        y2 = x**3 + a * x + b
        mask = y2 >= 0
        y = np.sqrt(np.maximum(y2, 0))
        ax.plot(x[mask], y[mask], color=PALETTE[index], linewidth=1.6, label=f"$(a,b)=({a},{b})$")
        ax.plot(x[mask], -y[mask], color=PALETTE[index], linewidth=1.6)
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-4.0, 4.0)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title("Four nonsingular curves from the coefficient forest")
    ax.legend(frameon=False, loc="upper left")
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Algebraic geometry example: validity removes the discriminant locus without erasing the attempted routes", fontsize=13.2, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_matrix_spectral_orbit(forest: PerturbationForest, path: str | Path) -> None:
    system = forest.system
    root = next(node for node in forest.nodes.values() if node.min_depth == 0).state
    reps = [
        ("root", root),
        ("basis swap", system.apply(root, next(direction for direction in system.directions(root, 0) if direction.name == "swap_basis"))),
        ("45-degree conjugate", system.apply(root, next(direction for direction in system.directions(root, 0) if direction.name == "rotate_45"))),
    ]
    fig = plt.figure(figsize=(13.0, 4.8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 1])
    ax = fig.add_subplot(gs[0])
    ax.axis("off")
    centers = [0.16, 0.50, 0.84]
    vmax = max(abs(float(value)) for _, state in reps for value in state)
    for center, (label, state) in zip(centers, reps):
        a, b, c = map(float, state)
        matrix = np.array([[a, b], [b, c]])
        inset = ax.inset_axes([center - 0.13, 0.33, 0.26, 0.38])
        inset.imshow(matrix, cmap="coolwarm", vmin=-vmax, vmax=vmax)
        for i in range(2):
            for j in range(2):
                inset.text(j, i, f"{matrix[i,j]:.2g}", ha="center", va="center", fontsize=8, color=INK)
        inset.set_xticks([])
        inset.set_yticks([])
        ax.text(center, 0.77, label, ha="center", fontsize=8.5)
        inv = system.invariants(state)
        ax.text(center, 0.23, f"tr={inv['trace']}\ndet={inv['determinant']}", ha="center", fontsize=8, color=GRAY)
    ax.set_title("Different coordinate matrices, one spectral quotient class")
    _panel_label(ax, "A")

    ax = fig.add_subplot(gs[1])
    lows = np.array([float(node.invariants["eigenvalue_low"]) for node in forest.nodes.values()])
    highs = np.array([float(node.invariants["eigenvalue_high"]) for node in forest.nodes.values()])
    depths = np.array([node.min_depth for node in forest.nodes.values()])
    scatter = ax.scatter(lows, highs, c=depths, cmap="viridis", s=70, edgecolor="white", linewidth=0.5)
    ax.plot([min(lows.min(), highs.min()), max(lows.max(), highs.max())], [min(lows.min(), highs.min()), max(lows.max(), highs.max())], linestyle="--", color="#CBD5E1")
    ax.set_xlabel("lower eigenvalue")
    ax.set_ylabel("upper eigenvalue")
    ax.set_title("Spectral object atlas")
    _soft_grid(ax)
    fig.colorbar(scatter, ax=ax, pad=0.02, label="minimum depth")
    _panel_label(ax, "B")

    ax = fig.add_subplot(gs[2])
    raw = forest.raw_counts(); quot = forest.quotient_counts(); depths_list = sorted(raw)
    ax.semilogy(depths_list, [raw[d] for d in depths_list], marker="o", color=BLUE, label="operator paths")
    ax.semilogy(depths_list, [quot.get(d, 0) for d in depths_list], marker="s", color=TEAL, label="spectral classes")
    ax.set_xlabel("depth")
    ax.set_ylabel("count")
    ax.set_title("Conjugation paths collapse")
    ax.legend(frameon=False)
    _soft_grid(ax)
    _panel_label(ax, "C")
    fig.suptitle("Matrix example: quotient by characteristic polynomial separates basis motion from spectral deformation", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_sierpinski_completion(forest: PerturbationForest, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.2))
    depths = [2, 4, min(7, max(forest.raw_counts()))]
    for panel, (ax, depth) in enumerate(zip(axes, depths)):
        states = [forest.nodes[p.node_id].state for p in forest.paths.values() if p.depth == depth]
        coords = np.array([forest.system.cartesian(state) for state in states])
        ax.scatter(coords[:, 0], coords[:, 1], s=max(2, 40 / (depth + 1)), color=PALETTE[panel], alpha=0.75)
        triangle = np.array([[0, 0], [1, 0], [0.5, math.sqrt(3) / 2], [0, 0]])
        ax.plot(triangle[:, 0], triangle[:, 1], color="#94A3B8", linewidth=0.8)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"depth {depth}: {len(states):,} routes")
        _panel_label(ax, chr(ord("A") + panel))
    fig.suptitle("Three contractions at every descendant converge to the Sierpinski boundary object", fontsize=14, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_bloch_orbit(forest: PerturbationForest, path: str | Path) -> None:
    fig = plt.figure(figsize=(11.8, 5.2))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u = np.linspace(0, 2 * np.pi, 36)
    v = np.linspace(0, np.pi, 18)
    x = np.outer(np.cos(u), np.sin(v)); y = np.outer(np.sin(u), np.sin(v)); z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, rstride=3, cstride=3, color="#CBD5E1", linewidth=0.35, alpha=0.55)
    nodes = list(forest.nodes.values())
    coords = np.array([node.state for node in nodes], dtype=float)
    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=85, c=[PALETTE[node.min_depth % len(PALETTE)] for node in nodes], edgecolor="white", linewidth=0.6)
    for edge in forest.edges.values():
        a = np.array(forest.nodes[edge.source].state, dtype=float)
        b = np.array(forest.nodes[edge.target].state, dtype=float)
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color="#94A3B8", linewidth=0.6, alpha=0.45)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("$x$"); ax.set_ylabel("$y$"); ax.set_zlabel("$z$")
    ax.set_title("Quarter-turn orbit on the Bloch sphere")
    _panel_label(ax, "A")

    ax2 = fig.add_subplot(1, 2, 2)
    raw = forest.raw_counts(); quot = forest.quotient_counts(); depths = sorted(raw)
    ax2.semilogy(depths, [raw[d] for d in depths], marker="o", color=BLUE, linewidth=2.0, label="gate words")
    ax2.semilogy(depths, [quot.get(d, 0) for d in depths], marker="s", color=TEAL, linewidth=2.0, label="distinct Bloch states")
    ax2.axhline(6, linestyle="--", color=ORANGE, linewidth=1.0, label="six axial pure states")
    ax2.set_xlabel("gate depth")
    ax2.set_ylabel("count")
    ax2.set_title("Finite orbit closure under repeated gates")
    ax2.legend(frameon=False)
    _soft_grid(ax2)
    _panel_label(ax2, "B")
    fig.suptitle("Quantum realization: infinitely many gate words can generate a finite quotient orbit", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_signal_gallery(forest: PerturbationForest, path: str | Path) -> None:
    nodes = sorted(forest.nodes.values(), key=lambda node: (node.min_depth, node.id))
    selected = []
    seen_families: set[str] = set()
    for node in nodes:
        family = node.first_direction.family if node.first_direction else "seed"
        if family not in seen_families or len(selected) < 2:
            selected.append(node)
            seen_families.add(str(family))
        if len(selected) >= 6:
            break
    fig, axes = plt.subplots(2, 3, figsize=(12.6, 6.2), sharex=True)
    for ax, node in zip(axes.flat, selected):
        values = np.asarray(node.state, dtype=float)
        ax.step(range(len(values)), values, where="mid", linewidth=1.8, color=PALETTE[node.min_depth % len(PALETTE)])
        ax.scatter(range(len(values)), values, s=18, color=PALETTE[node.min_depth % len(PALETTE)])
        title = "seed" if node.first_direction is None else node.first_direction.name.replace("_", " ")
        ax.set_title(title, fontsize=9.5)
        ax.text(0.03, 0.93, f"energy={node.invariants['energy']}", transform=ax.transAxes, fontsize=7.2, va="top", color=GRAY)
        _soft_grid(ax)
    for ax in axes[-1]:
        ax.set_xlabel("sample index")
    for ax in axes[:, 0]:
        ax.set_ylabel("amplitude")
    fig.suptitle("Signal realization: each generated signal is itself queried for translation, symmetry, modulation, differentiation, and smoothing", fontsize=13.2, color=INK, y=1.01)
    _save(fig, Path(path))


def plot_recurrence_atlas(forest: PerturbationForest, path: str | Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.9))
    ax = axes[0]
    a = np.array([node.state[0] for node in forest.nodes.values()], dtype=float)
    b = np.array([node.state[1] for node in forest.nodes.values()], dtype=float)
    radius = np.array([float(node.invariants["spectral_radius"]) for node in forest.nodes.values()])
    scatter = ax.scatter(a, b, c=np.log1p(radius), cmap="magma", s=80, edgecolor="white", linewidth=0.5)
    for node in forest.nodes.values():
        ax.text(node.state[0], node.state[1] + 0.10, f"({node.state[0]},{node.state[1]})", ha="center", fontsize=6)
    ax.set_xlabel("coefficient $a$")
    ax.set_ylabel("coefficient $b$")
    ax.set_title("Second-order recurrence parameter atlas")
    ax.set_xticks(sorted(set(a.astype(int))))
    ax.set_yticks(sorted(set(b.astype(int))))
    _soft_grid(ax)
    fig.colorbar(scatter, ax=ax, pad=0.02, label="$\log(1+\rho)$")
    _panel_label(ax, "A")

    ax = axes[1]
    targets = [(1, 1), (2, -1), (1, -1), (2, 1), (-1, 1)]
    system = forest.system
    for index, state in enumerate(targets):
        if state not in [node.state for node in forest.nodes.values()]:
            continue
        sequence = system.sequence(state, 11)
        ax.plot(range(len(sequence)), sequence, marker="o", markersize=3, linewidth=1.7, color=PALETTE[index], label=f"$(a,b)={state}$")
    ax.axhline(0, color="#94A3B8", linewidth=0.8)
    ax.set_xlabel("index $n$")
    ax.set_ylabel("$u_n$")
    ax.set_title("Distinct sequence families generated by coefficient moves")
    ax.legend(frameon=False, ncol=2)
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("Sequence realization: perturbing recurrence coefficients generates families, not merely isolated terms", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))


def plot_polynomial_root_orbit(forest: PerturbationForest, path: str | Path) -> None:
    import sympy as sp

    candidates = []
    for node in sorted(forest.nodes.values(), key=lambda node: (node.min_depth, -int(node.invariants.get("degree", -1)), node.id)):
        try:
            poly = sp.Poly(node.state, forest.system.x)
            if poly.degree() >= 1 and poly.degree() <= 6:
                candidates.append(node)
        except Exception:
            continue
        if len(candidates) >= 6:
            break
    fig, axes = plt.subplots(2, 3, figsize=(12.4, 7.0))
    for ax, node in zip(axes.flat, candidates):
        roots = np.array([complex(root) for root in sp.nroots(node.state)], dtype=complex)
        ax.scatter(roots.real, roots.imag, s=55, color=PALETTE[node.min_depth % len(PALETTE)], edgecolor="white", linewidth=0.5)
        ax.axhline(0, color="#CBD5E1", linewidth=0.7)
        ax.axvline(0, color="#CBD5E1", linewidth=0.7)
        label = str(sp.expand(node.state))
        if len(label) > 32:
            label = label[:29] + "..."
        ax.set_title(label, fontsize=8.5)
        ax.text(0.03, 0.92, f"depth {node.min_depth}", transform=ax.transAxes, fontsize=7, color=GRAY)
        ax.set_aspect("equal", adjustable="datalim")
        _soft_grid(ax)
    for ax in axes[-1]:
        ax.set_xlabel("real part")
    for ax in axes[:, 0]:
        ax.set_ylabel("imaginary part")
    fig.suptitle("Polynomial realization: operator paths deform coefficients while the root geometry records the object-level effect", fontsize=13.2, color=INK, y=1.01)
    _save(fig, Path(path))


def plot_analytic_function_gallery(forest: PerturbationForest, path: str | Path) -> None:
    import sympy as sp

    x_symbol = forest.system.x
    labels = ["cosh(x)", "sinh(x)", "1/cosh(x)", "tanh(x)", "cosh(x)**2", "tanh(x)**2"]
    mapping = {str(forest.system.serialize_state(node.state)): node for node in forest.nodes.values()}
    fig, axes = plt.subplots(2, 3, figsize=(12.4, 6.5), sharex=True)
    xs = np.linspace(-2.2, 2.2, 600)
    for ax, label, color in zip(axes.flat, labels, PALETTE):
        node = mapping.get(label)
        if node is None:
            ax.axis("off")
            continue
        function = sp.lambdify(x_symbol, node.state, modules=["numpy"])
        with np.errstate(all="ignore"):
            ys = np.asarray(function(xs), dtype=float)
        ys = np.broadcast_to(ys, xs.shape) if ys.ndim == 0 else ys
        ys = np.clip(ys, -8, 8)
        ax.plot(xs, ys, color=color, linewidth=2.0)
        ax.axhline(0, color="#CBD5E1", linewidth=0.7)
        ax.set_ylim(-4.5, 4.5)
        ax.set_title(label.replace("**", "^"), fontsize=9.5)
        route = " -> ".join(forest.shortest_path_labels(node.id)) or "seed"
        if len(route) > 36:
            route = route[:33] + "..."
        ax.text(0.03, 0.93, route, transform=ax.transAxes, fontsize=6.7, va="top", color=GRAY)
        _soft_grid(ax)
    for ax in axes[-1]:
        ax.set_xlabel("$x$")
    for ax in axes[:, 0]:
        ax.set_ylabel("function value")
    fig.suptitle("Analytic realization: one seed produces a structured gallery through exact symbolic directions", fontsize=13.5, color=INK, y=1.01)
    _save(fig, Path(path))


def plot_family_certificate_pipeline(path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(12.4, 5.3))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    stages = [
        (0.08, "candidate\ncluster", BLUE),
        (0.25, "canonical\nparameterization", TEAL),
        (0.42, "closure\nunder directions", ORANGE),
        (0.59, "relations and\nrecurrences", PURPLE),
        (0.76, "invariant and\nreconstruction tests", GREEN),
        (0.93, "certified\ninternal family", RED),
    ]
    for index, (x, label, color) in enumerate(stages):
        _node_box(ax, (x, 0.62), label, color=color, width=0.13, height=0.17, fontsize=8.1)
        if index < len(stages) - 1:
            _arrow(ax, (x + 0.07, 0.62), (stages[index + 1][0] - 0.07, 0.62), color="#94A3B8", lw=1.1)
    failures = [(0.25, "nonidentifiable\nparameters"), (0.42, "closure failure"), (0.59, "false recurrence"), (0.76, "invariant mismatch")]
    for x, label in failures:
        _arrow(ax, (x, 0.53), (x, 0.30), color=RED, lw=1.0)
        ax.text(x, 0.22, label, ha="center", va="center", fontsize=7.5, color=RED, bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": RED})
    ax.text(0.5, 0.05, "The certificate proves closure relative to the declared grammar. It does not by itself prove historical novelty.", ha="center", fontsize=9.5, color=INK)
    ax.set_title("A mathematical family is promoted only after parameter, closure, relation, invariant, and reconstruction checks", fontsize=14, color=INK)
    _save(fig, Path(path))


def plot_example_dashboard(summaries: Mapping[str, Mapping[str, Any]], path: str | Path) -> None:
    labels = list(summaries)
    raw = np.array([float(summaries[label].get("raw_paths", 0)) for label in labels])
    quotient = np.array([float(summaries[label].get("quotient_nodes", 0)) for label in labels])
    invalid = np.array([float(summaries[label].get("invalid_attempts", 0)) for label in labels])
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axes[0]
    width = 0.36
    ax.bar(x - width / 2, raw, width, color=BLUE, label="raw paths")
    ax.bar(x + width / 2, quotient, width, color=TEAL, label="quotient nodes")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([label.replace("_", "\n") for label in labels], rotation=0)
    ax.set_ylabel("count on logarithmic scale")
    ax.set_title("Exploration size across worked domains")
    ax.legend(frameon=False)
    _soft_grid(ax, "y")
    _panel_label(ax, "A")

    ax = axes[1]
    compression = np.divide(raw, np.maximum(quotient, 1))
    scatter = ax.scatter(compression, invalid + 1, s=80 + 18 * np.log1p(raw), c=np.arange(len(labels)), cmap="tab10", edgecolor="white", linewidth=0.6)
    for cx, cy, label in zip(compression, invalid + 1, labels):
        ax.annotate(label.replace("_", " "), (cx, cy), xytext=(5, 4), textcoords="offset points", fontsize=7)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("raw paths per quotient node")
    ax.set_ylabel("invalid attempts + 1")
    ax.set_title("Compression and constraint pressure")
    _soft_grid(ax)
    _panel_label(ax, "B")
    fig.suptitle("The same calculus supports domains with very different branching, quotienting, and validity behavior", fontsize=13.5, color=INK, y=1.02)
    _save(fig, Path(path))

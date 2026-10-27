from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
from matplotlib.lines import Line2D

from .extended_examples import GraphState, MatrixState, ShapeState, _graph_edges
from .forest import PerturbationForest


plt.rcParams.update(
    {
        "font.size": 10.5,
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "legend.fontsize": 9.5,
        "figure.dpi": 140,
        "savefig.dpi": 240,
    }
)


def _save(fig: Any, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(destination.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _diagram_axes(width: float = 12.0, height: float = 6.0) -> tuple[Any, Any]:
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return fig, ax


def _box(ax: Any, x: float, y: float, width: float, height: float, text: str, *, fontsize: float = 10.0) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        fill=False,
        linewidth=1.3,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=fontsize)


def _arrow(ax: Any, start: tuple[float, float], end: tuple[float, float], label: str | None = None, *, curve: float = 0.0) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.1,
        connectionstyle=f"arc3,rad={curve}",
    )
    ax.add_patch(arrow)
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.035, label, ha="center", va="center", fontsize=8.5)


def plot_universal_overview(path: str | Path) -> None:
    fig, ax = _diagram_axes(13.4, 6.4)
    ax.set_title("The complete generative deformation object", pad=16)

    stage_x = [0.025, 0.22, 0.415, 0.61, 0.805]
    width = 0.165
    titles = ["Seed and local fiber", "Raw route forest", "Quotient atlas", "Completed boundary", "Certified families"]
    descriptions = [
        "$x_0$ with its own\nadmissible directions",
        "all finite direction words\nwith route multiplicity",
        "relations merge equivalent\nendpoints, not histories",
        "proved limits of compatible\ninfinite branches",
        "parameters, closure laws,\nrelations, invariants",
    ]
    for x, title, description in zip(stage_x, titles, descriptions):
        patch = FancyBboxPatch(
            (x, 0.19), width, 0.52,
            boxstyle="round,pad=0.012,rounding_size=0.012",
            fill=False, linewidth=1.3,
        )
        ax.add_patch(patch)
        ax.text(x + width / 2, 0.665, title, ha="center", va="center", fontsize=10.5, fontweight="bold")
        ax.text(x + width / 2, 0.285, description, ha="center", va="center", fontsize=9.4)

    transition_labels = ["expand", "quotient", "complete", "certify"]
    for index, label in enumerate(transition_labels):
        left = stage_x[index] + width
        right = stage_x[index + 1]
        _arrow(ax, (left, 0.455), (right, 0.455))
        ax.text((left + right) / 2, 0.765, label, ha="center", fontsize=8.5)

    # Seed direction halo
    center = (stage_x[0] + width / 2, 0.49)
    ax.scatter([center[0]], [center[1]], s=40)
    for angle in np.linspace(0, 2 * math.pi, 7, endpoint=False):
        end = (center[0] + 0.058 * math.cos(angle), center[1] + 0.058 * math.sin(angle))
        ax.plot([center[0], end[0]], [center[1], end[1]], linewidth=0.9)

    # Small route tree
    root = (stage_x[1] + width / 2, 0.58)
    children = [(root[0] - 0.045, 0.50), (root[0], 0.50), (root[0] + 0.045, 0.50)]
    leaves: list[tuple[float, float]] = []
    for child in children:
        ax.plot([root[0], child[0]], [root[1], child[1]], linewidth=0.9)
        for delta in (-0.018, 0.018):
            leaf = (child[0] + delta, 0.40)
            leaves.append(leaf)
            ax.plot([child[0], leaf[0]], [child[1], leaf[1]], linewidth=0.8)
    for point in [root, *children, *leaves]:
        ax.scatter([point[0]], [point[1]], s=23)

    # Quotient diamond
    qx = stage_x[2] + width / 2
    qnodes = [(qx, 0.59), (qx - 0.042, 0.50), (qx + 0.042, 0.50), (qx, 0.40)]
    for start_point, end_point in [(qnodes[0], qnodes[1]), (qnodes[0], qnodes[2]), (qnodes[1], qnodes[3]), (qnodes[2], qnodes[3])]:
        ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], linewidth=0.9)
    for point in qnodes:
        ax.scatter([point[0]], [point[1]], s=30)

    # Completion as nested neighborhoods
    cx = stage_x[3] + width / 2
    for radius in (0.064, 0.045, 0.028, 0.014):
        ax.add_patch(Circle((cx, 0.49), radius, fill=False, linewidth=1.0))
    ax.scatter([cx], [0.49], s=26)

    # Family curve
    fx0 = stage_x[4] + 0.025
    theta = np.linspace(0, 1, 100)
    curve_x = fx0 + 0.115 * theta
    curve_y = 0.405 + 0.19 * theta - 0.11 * theta**2
    ax.plot(curve_x, curve_y, linewidth=1.4)
    for value in (0.05, 0.32, 0.62, 0.92):
        ax.scatter([fx0 + 0.115 * value], [0.405 + 0.19 * value - 0.11 * value**2], s=31)

    ax.text(
        0.5, 0.085,
        "Route data, object identity, convergence data, and family structure remain distinct and auditable.",
        ha="center", fontsize=11,
    )
    _save(fig, path)


def plot_direction_fiber_gallery(path: str | Path) -> None:
    fig, ax = _diagram_axes(13.0, 6.2)
    ax.set_title("Abstract direction fibers depend on the object being deformed", pad=16)
    centers = [(0.14, 0.54), (0.38, 0.54), (0.62, 0.54), (0.86, 0.54)]
    titles = ["analytic object", "matrix", "probability law", "geometry"]
    inner = ["$f(x)=\\cosh x$", "A = [[1, 1], [0, 1]]", "$N(\\mu,\\sigma^2)$", "triangle $K$"]
    directions = [
        ["differentiate", "invert", "project parity", "double argument"],
        ["transpose", "square", "conjugate", "commutator"],
        ["shift", "scale", "convolve", "standardize"],
        ["rotate", "shear", "reflect", "translate"],
    ]
    for center, title, object_text, labels in zip(centers, titles, inner, directions):
        ax.add_patch(Circle(center, 0.075, fill=False, linewidth=1.4))
        ax.text(center[0], center[1], object_text, ha="center", va="center", fontsize=9.5)
        ax.text(center[0], 0.80, title, ha="center", fontsize=11, fontweight="bold")
        angles = np.linspace(math.pi / 6, 11 * math.pi / 6, len(labels), endpoint=False)
        for angle, label in zip(angles, labels):
            endpoint = (center[0] + 0.125 * math.cos(angle), center[1] + 0.20 * math.sin(angle))
            _arrow(ax, (center[0] + 0.06 * math.cos(angle), center[1] + 0.06 * math.sin(angle)), endpoint)
            ax.text(endpoint[0], endpoint[1] + (0.035 if math.sin(angle) >= 0 else -0.04), label, ha="center", fontsize=8)
    ax.text(
        0.5,
        0.12,
        "The phrase every direction is interpreted relative to a declared fiber $\\mathcal{D}_x$, not as a universal list copied to every state.",
        ha="center",
        fontsize=10.5,
    )
    _save(fig, path)


def plot_raw_tree_to_quotient(path: str | Path, depth: int = 4) -> None:
    fig, ax = _diagram_axes(13.2, 7.0)
    ax.set_title("Raw route multiplicity and quotient object identity", pad=16)

    # Left raw binary tree
    x_left0, x_left1 = 0.04, 0.48
    positions: dict[str, tuple[float, float]] = {"": ((x_left0 + x_left1) / 2, 0.86)}
    for level in range(1, depth + 1):
        words = [format(index, f"0{level}b") for index in range(2**level)]
        for index, word in enumerate(words):
            x = x_left0 + (index + 0.5) * (x_left1 - x_left0) / len(words)
            y = 0.86 - level * 0.16
            positions[word] = (x, y)
            parent = word[:-1]
            ax.plot([positions[parent][0], x], [positions[parent][1], y], linewidth=0.65)
    for word, (x, y) in positions.items():
        endpoint = word.count("1") - word.count("0")
        ax.scatter([x], [y], s=20 if word else 38)
        if len(word) == depth:
            ax.text(x, y - 0.035, str(endpoint), ha="center", va="top", fontsize=7)
    ax.text((x_left0 + x_left1) / 2, 0.96, f"raw binary path tree through depth {depth}", ha="center", fontsize=11, fontweight="bold")
    ax.text((x_left0 + x_left1) / 2, 0.12, f"$2^{depth}={2**depth}$ terminal paths", ha="center", fontsize=10)

    _arrow(ax, (0.50, 0.52), (0.60, 0.52), "identify equal endpoints")

    # Right quotient line
    states = list(range(-depth, depth + 1, 2))
    qx0, qx1 = 0.64, 0.96
    y = 0.52
    ax.plot([qx0, qx1], [y, y], linewidth=1.1)
    multiplicities = [math.comb(depth, (state + depth) // 2) for state in states]
    for index, (state, mult) in enumerate(zip(states, multiplicities)):
        x = qx0 + index * (qx1 - qx0) / (len(states) - 1)
        ax.scatter([x], [y], s=45 + 18 * math.log1p(mult))
        ax.text(x, y + 0.07, str(state), ha="center", fontsize=9)
        ax.text(x, y - 0.08, f"{mult} route{'s' if mult != 1 else ''}", ha="center", fontsize=8)
    ax.text((qx0 + qx1) / 2, 0.96, "quotient endpoint atlas", ha="center", fontsize=11, fontweight="bold")
    ax.text((qx0 + qx1) / 2, 0.22, f"{depth + 1} distinct depth-{depth} endpoint classes", ha="center", fontsize=10)
    ax.text(0.5, 0.04, "Path multiplicity survives as metadata after quotienting.", ha="center", fontsize=10.5)
    _save(fig, path)


def plot_continuous_direction_covers(path: str | Path) -> None:
    fig, ax = _diagram_axes(13.0, 6.2)
    ax.set_title("A continuous direction fiber is explored by certified finite covers", pad=16)
    circle_centers = [(0.17, 0.56), (0.42, 0.56), (0.67, 0.56)]
    counts = [4, 8, 16]
    for center, count in zip(circle_centers, counts):
        ax.add_patch(Circle(center, 0.13, fill=False, linewidth=1.2))
        for angle in np.linspace(0, 2 * math.pi, count, endpoint=False):
            x = center[0] + 0.13 * math.cos(angle)
            y = center[1] + 0.13 * math.sin(angle)
            ax.scatter([x], [y], s=22)
            ax.plot([center[0], x], [center[1], y], linewidth=0.45, alpha=0.55)
        ax.text(center[0], 0.78, f"{count}-point cover", ha="center", fontsize=10.5)
        ax.text(center[0], 0.33, f"radius $\\epsilon={math.pi/count:.3f}$", ha="center", fontsize=9)
    _arrow(ax, (0.30, 0.56), (0.34, 0.56), "refine")
    _arrow(ax, (0.55, 0.56), (0.59, 0.56), "refine")

    # Endpoint bound on the right
    levels = np.arange(2, 8)
    errors = 2.0 ** (-levels)
    x0, x1 = 0.81, 0.97
    y0, y1 = 0.30, 0.78
    ax.plot([x0, x0], [y0, y1], linewidth=0.9)
    ax.plot([x0, x1], [y0, y0], linewidth=0.9)
    scaled_x = x0 + (levels - levels.min()) / (levels.max() - levels.min()) * (x1 - x0)
    scaled_y = y0 + (np.log(errors) - np.log(errors.min())) / (np.log(errors.max()) - np.log(errors.min())) * (y1 - y0)
    ax.plot(scaled_x, scaled_y, marker="o")
    ax.text((x0 + x1) / 2, 0.84, "propagated endpoint bound", ha="center", fontsize=10.5)
    ax.text((x0 + x1) / 2, 0.22, "$e_n$ decreases with cover radius", ha="center", fontsize=9)
    ax.text(0.5, 0.10, "The uncountable fiber remains a parameterized object. Finite covers approximate it without redefining it as finite.", ha="center", fontsize=10.5)
    _save(fig, path)


def plot_branch_completion(values: Sequence[float], path: str | Path, *, limit: float | None = None) -> None:
    values_array = np.asarray(values, dtype=float)
    if limit is None:
        limit = float(values_array[-1])
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    depths = np.arange(len(values_array))
    ax.plot(depths, values_array, marker="o", label="partial endpoint")
    ax.axhline(limit, linestyle="--", linewidth=1.2, label="completed limit")
    tails = np.maximum.accumulate(np.abs(values_array[::-1] - limit))[::-1]
    ax.fill_between(depths, limit - tails, limit + tails, alpha=0.16, label="certified tail envelope")
    ax.set_xlabel("branch depth")
    ax.set_ylabel("endpoint coordinate")
    ax.set_title("Completion adds a limit only after a branch is proved Cauchy")
    ax.grid(alpha=0.22)
    ax.legend(loc="upper right")
    _save(fig, path)


def plot_operadic_hyperforest(path: str | Path) -> None:
    fig, ax = _diagram_axes(12.8, 6.6)
    ax.set_title("Unary words and multi-input operation trees belong to one generative syntax", pad=16)

    # Unary word
    ax.text(0.18, 0.86, "unary word", ha="center", fontsize=11, fontweight="bold")
    unary = [(0.18, 0.72), (0.18, 0.56), (0.18, 0.40), (0.18, 0.24)]
    for point in unary:
        ax.scatter([point[0]], [point[1]], s=45)
    for index in range(len(unary) - 1):
        _arrow(ax, unary[index], unary[index + 1], ["$d_1$", "$d_2$", "$d_3$"][index])

    # Binary tree
    ax.text(0.50, 0.86, "binary interaction tree", ha="center", fontsize=11, fontweight="bold")
    leaves = [(0.40, 0.66), (0.50, 0.66), (0.60, 0.66)]
    for index, point in enumerate(leaves):
        ax.scatter([point[0]], [point[1]], s=45)
        ax.text(point[0], point[1] + 0.055, f"$x_{index+1}$", ha="center")
    op1 = (0.45, 0.48)
    op2 = (0.55, 0.30)
    ax.scatter([op1[0], op2[0]], [op1[1], op2[1]], marker="s", s=70)
    _arrow(ax, leaves[0], op1)
    _arrow(ax, leaves[1], op1)
    _arrow(ax, op1, op2)
    _arrow(ax, leaves[2], op2)
    ax.text(op1[0] - 0.04, op1[1], "$\\Psi_2$", ha="right")
    ax.text(op2[0] - 0.04, op2[1], "$\\Psi_2$", ha="right")

    # Relation quotient of two parenthesizations
    ax.text(0.82, 0.86, "relation quotient", ha="center", fontsize=11, fontweight="bold")
    top_a = (0.74, 0.63)
    top_b = (0.90, 0.63)
    merge = (0.82, 0.30)
    _box(ax, top_a[0] - 0.06, top_a[1] - 0.05, 0.12, 0.10, "$(x_1x_2)x_3$", fontsize=9)
    _box(ax, top_b[0] - 0.06, top_b[1] - 0.05, 0.12, 0.10, "$x_1(x_2x_3)$", fontsize=9)
    ax.scatter([merge[0]], [merge[1]], s=60)
    _arrow(ax, top_a, merge, "associativity", curve=-0.12)
    _arrow(ax, top_b, merge, None, curve=0.12)
    ax.text(merge[0], merge[1] - 0.07, "one quotient object", ha="center", fontsize=9)

    ax.text(0.5, 0.08, "The raw hyperforest stores syntax. The quotient stores mathematical identity under declared operadic relations.", ha="center", fontsize=10.5)
    _save(fig, path)


def plot_growth_phase_diagram(path: str | Path) -> None:
    branching = np.linspace(1.05, 12.0, 260)
    inverse_cost = np.linspace(0.05, 4.0, 260)
    grid_b, grid_s = np.meshgrid(branching, inverse_cost)
    ratio = grid_b * np.exp(-grid_s)
    finite = np.where(ratio < 1, ratio / np.maximum(1e-12, 1 - ratio), np.nan)
    values = np.log10(np.clip(finite, 1e-4, 1e4))
    fig, ax = plt.subplots(figsize=(10.2, 6.1))
    image = ax.imshow(
        values,
        origin="lower",
        aspect="auto",
        extent=[branching.min(), branching.max(), inverse_cost.min(), inverse_cost.max()],
    )
    boundary = np.log(branching)
    ax.plot(branching, boundary, linewidth=1.8, label="$s=\\log B$")
    ax.set_xlabel("branching factor $B$")
    ax.set_ylabel("inverse path cost $s$ for unit step cost")
    ax.set_title("Convergence phase diagram for the regular path partition function")
    ax.legend()
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("$\\log_{10} Z$ in the convergent region")
    ax.text(8.3, 1.1, "divergent", fontsize=11)
    ax.text(3.0, 2.7, "convergent", fontsize=11)
    _save(fig, path)


def plot_family_certificate_pipeline(path: str | Path) -> None:
    fig, ax = _diagram_axes(13.0, 5.8)
    ax.set_title("A generated family requires a certificate, not visual resemblance", pad=16)
    x_positions = [0.03, 0.23, 0.43, 0.63, 0.82]
    widths = [0.14, 0.14, 0.14, 0.14, 0.15]
    labels = [
        "generated endpoints\n$\\{x_i\\}$",
        "candidate parameter\n$\\theta_i$",
        "closure actions\n$\\sigma_d$",
        "exact identities\nrecurrences and invariants",
        "family certificate\nverified or rejected",
    ]
    for x, width, label in zip(x_positions, widths, labels):
        _box(ax, x, 0.31, width, 0.36, label, fontsize=10)
    for index, label in enumerate(["organize", "test", "prove", "audit"]):
        _arrow(ax, (x_positions[index] + widths[index], 0.49), (x_positions[index + 1], 0.49), label)
    ax.text(0.50, 0.18, "A failed closure step is retained as evidence against the proposed family.", ha="center", fontsize=10.5)
    _save(fig, path)


def plot_exploration_frontier(path: str | Path) -> None:
    fig, ax = _diagram_axes(12.8, 6.5)
    ax.set_title("Finite exploration is an audited frontier through an infinite forest", pad=16)
    root = (0.50, 0.88)
    levels = {0: [root]}
    for level, count in [(1, 3), (2, 7), (3, 13), (4, 18)]:
        xs = np.linspace(0.08, 0.92, count)
        levels[level] = [(float(x), 0.88 - 0.16 * level) for x in xs]
    rng = np.random.default_rng(11)
    for level in range(4):
        parents = levels[level]
        children = levels[level + 1]
        assignments = np.linspace(0, len(children) - 1, len(parents) + 1, dtype=int)
        for index, parent in enumerate(parents):
            for child in children[assignments[index] : assignments[index + 1] + 1]:
                ax.plot([parent[0], child[0]], [parent[1], child[1]], linewidth=0.55, alpha=0.55)
    frontier_y = 0.88 - 0.16 * 3 + 0.07
    ax.plot([0.04, 0.96], [frontier_y, frontier_y], linestyle="--", linewidth=1.1)
    ax.text(0.96, frontier_y + 0.025, "current frontier", ha="right", fontsize=9)
    for level, points in levels.items():
        for index, point in enumerate(points):
            if level <= 2:
                ax.scatter([point[0]], [point[1]], s=32)
            elif level == 3 and index % 2 == 0:
                ax.scatter([point[0]], [point[1]], s=32)
            else:
                ax.scatter([point[0]], [point[1]], s=32, facecolors="none")
    # collisions to quotient archive
    _box(ax, 0.05, 0.04, 0.26, 0.12, "quotient archive\ncanonical nodes and path multiplicities", fontsize=9.5)
    for point in levels[2][1::2][:3]:
        _arrow(ax, point, (0.18, 0.16), curve=0.08)
    _box(ax, 0.69, 0.04, 0.26, 0.12, "unexplored residual\nparameter cells, deferred paths, failed moves", fontsize=9.5)
    for point in levels[4][::5]:
        _arrow(ax, point, (0.82, 0.16), curve=-0.08)
    ax.text(0.50, 0.02, "Filled nodes were expanded. Open nodes remain part of the declared search residual.", ha="center", fontsize=9.5)
    _save(fig, path)


def _normalized_curve(expression: sp.Expr, symbol: sp.Symbol, grid: np.ndarray) -> np.ndarray:
    function = sp.lambdify(symbol, expression, modules=["numpy"])
    with np.errstate(all="ignore"):
        values = np.asarray(function(grid), dtype=np.complex128)
    if values.ndim == 0:
        values = np.full(grid.shape, values, dtype=np.complex128)
    elif values.shape != grid.shape:
        values = np.broadcast_to(values, grid.shape).astype(np.complex128)
    values = np.real_if_close(values, tol=1_000)
    values = np.asarray(values, dtype=float)
    values[~np.isfinite(values)] = np.nan
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.zeros_like(grid)
    scale = np.nanpercentile(np.abs(finite), 90)
    if scale <= 1e-12:
        scale = 1.0
    normalized = np.clip(values / scale, -1.0, 1.0)
    jump_indices = np.where(np.abs(np.diff(normalized)) > 1.0)[0]
    normalized[jump_indices] = np.nan
    normalized[jump_indices + 1] = np.nan
    return normalized


def plot_polynomial_atlas(expressions: Sequence[sp.Expr], labels: Sequence[str], symbol: sp.Symbol, path: str | Path) -> None:
    grid = np.linspace(-2.2, 2.2, 500)
    fig, ax = plt.subplots(figsize=(10.8, 7.0))
    for index, (expression, label) in enumerate(zip(expressions, labels)):
        offset = len(expressions) - 1 - index
        curve = _normalized_curve(expression, symbol, grid)
        ax.plot(grid, offset + 0.38 * curve, linewidth=1.3)
        ax.axhline(offset, linewidth=0.35, alpha=0.45)
        ax.text(2.28, offset, label, va="center", fontsize=9)
    ax.set_xlim(-2.25, 3.7)
    ax.set_ylim(-0.7, len(expressions) - 0.3)
    ax.set_yticks([])
    ax.set_xlabel("$x$ coordinate; each row is independently normalized")
    ax.set_title("Polynomial deformation atlas: one seed, several operator routes")
    ax.grid(axis="x", alpha=0.18)
    _save(fig, path)


def plot_analytic_atlas(expressions: Sequence[sp.Expr], labels: Sequence[str], symbol: sp.Symbol, path: str | Path) -> None:
    grid = np.linspace(-2.2, 2.2, 700)
    fig, ax = plt.subplots(figsize=(10.8, 7.6))
    for index, (expression, label) in enumerate(zip(expressions, labels)):
        offset = len(expressions) - 1 - index
        curve = _normalized_curve(expression, symbol, grid)
        ax.plot(grid, offset + 0.36 * curve, linewidth=1.3)
        ax.axhline(offset, linewidth=0.35, alpha=0.45)
        ax.text(2.28, offset, label, va="center", fontsize=9)
    ax.set_xlim(-2.25, 3.75)
    ax.set_ylim(-0.7, len(expressions) - 0.3)
    ax.set_yticks([])
    ax.set_xlabel("$x$ coordinate; each function strip is independently normalized")
    ax.set_title("Analytic deformation atlas generated from $\\cosh x$")
    ax.grid(axis="x", alpha=0.18)
    _save(fig, path)


def plot_sequence_atlas(sequences: Sequence[Sequence[int]], labels: Sequence[str], path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(11.0, 7.0))
    length = max(len(sequence) for sequence in sequences)
    x = np.arange(length)
    for index, (sequence, label) in enumerate(zip(sequences, labels)):
        values = np.asarray(sequence, dtype=float)
        scale = max(1.0, np.percentile(np.abs(values), 90))
        offset = len(sequences) - 1 - index
        ax.plot(x[: len(values)], offset + 0.34 * values / scale, marker="o", markersize=3.5, linewidth=1.1)
        ax.axhline(offset, linewidth=0.35, alpha=0.45)
        ax.text(length - 0.6, offset, label, va="center", fontsize=9)
    ax.set_xlim(-0.3, length + 3.2)
    ax.set_ylim(-0.7, len(sequences) - 0.3)
    ax.set_yticks([])
    ax.set_xlabel("sequence index")
    ax.set_title("Integer sequence deformation atlas")
    ax.grid(axis="x", alpha=0.18)
    _save(fig, path)


def plot_gaussian_atlas(forest: PerturbationForest, path: str | Path, *, max_nodes: int = 126) -> None:
    """Plot the Gaussian parameter atlas without obscuring its geometry.

    Each quotient object is a point in the exact parameter half-plane.  A
    minimum-depth spanning forest shows one shortest construction route to each
    displayed object.  Reset edges created by standardization are omitted from
    the background because they all return to the same canonical seed.
    """
    nodes = sorted(forest.nodes.values(), key=lambda node: (node.min_depth, node.id))[:max_nodes]
    node_ids = {node.id for node in nodes}
    node_by_id = {node.id: node for node in nodes}
    positions = {
        node.id: (float(node.state[0]), math.sqrt(float(node.state[1])))
        for node in nodes
    }

    fig, ax = plt.subplots(figsize=(10.8, 6.7))

    # Retain one shortest incoming edge for each non-root quotient object.
    incoming: dict[int, Any] = {}
    for edge in sorted(
        forest.edges.values(),
        key=lambda edge: (edge.first_depth, edge.target, edge.source, edge.direction.name),
    ):
        if edge.source not in node_ids or edge.target not in node_ids:
            continue
        if edge.direction.name == "standardize":
            continue
        source_node = node_by_id[edge.source]
        target_node = node_by_id[edge.target]
        if target_node.min_depth != source_node.min_depth + 1:
            continue
        incoming.setdefault(edge.target, edge)

    for edge in incoming.values():
        start_xy, end_xy = positions[edge.source], positions[edge.target]
        ax.annotate(
            "",
            xy=end_xy,
            xytext=start_xy,
            arrowprops={"arrowstyle": "->", "linewidth": 0.62, "alpha": 0.22, "color": "0.30"},
            zorder=1,
        )

    means = np.asarray([positions[node.id][0] for node in nodes], dtype=float)
    sigmas = np.asarray([positions[node.id][1] for node in nodes], dtype=float)
    depths = np.asarray([node.min_depth for node in nodes], dtype=float)
    sizes = np.asarray([78 if node.min_depth == 0 else max(24, 58 - 6 * node.min_depth) for node in nodes], dtype=float)
    scatter = ax.scatter(
        means,
        sigmas,
        c=depths,
        s=sizes,
        cmap="viridis",
        edgecolors="white",
        linewidths=0.5,
        zorder=3,
    )
    ax.scatter([0], [1], s=210, marker="*", edgecolors="black", linewidths=0.65, zorder=5, label="seed $N(0,1)$")

    callouts = [
        ((0, 1), (1, 1), "shift $+1$", (1.25, 1.08)),
        ((0, 1), (0, math.sqrt(2)), "convolve $N(0,1)$", (0.22, 1.48)),
        ((0, 1), (0, 2), "scale by $2$", (0.22, 2.13)),
    ]
    for source, target, label, text_position in callouts:
        ax.annotate(
            label,
            xy=target,
            xytext=text_position,
            fontsize=8.8,
            arrowprops={"arrowstyle": "-|>", "linewidth": 0.9},
        )

    ax.text(
        -3.75,
        7.65,
        "standardization is a reset edge to $N(0,1)$",
        fontsize=8.7,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "0.65", "alpha": 0.9},
    )

    colorbar = fig.colorbar(scatter, ax=ax, pad=0.018)
    colorbar.set_label("minimum perturbation depth")
    ax.set_xlabel(r"mean $\mu$")
    ax.set_ylabel(r"standard deviation $\sigma$")
    ax.set_title("Gaussian parameter atlas under shift, scale, convolution, reflection, and standardization")
    ax.grid(alpha=0.20)
    ax.legend(loc="upper right")
    _save(fig, path)

def _qubit_label(x: float, y: float, z: float) -> str:
    candidates = [
        ((0, 0, 1), "$|0\\rangle$"),
        ((0, 0, -1), "$|1\\rangle$"),
        ((1, 0, 0), "$|+\\rangle$"),
        ((-1, 0, 0), "$|-\\rangle$"),
        ((0, 1, 0), "$|+i\\rangle$"),
        ((0, -1, 0), "$|-i\\rangle$"),
    ]
    closest = min(candidates, key=lambda item: (x - item[0][0]) ** 2 + (y - item[0][1]) ** 2 + (z - item[0][2]) ** 2)
    return closest[1]


def plot_qubit_atlas(forest: PerturbationForest, path: str | Path) -> None:
    """Show the same finite orbit as geometry and as a quotient Cayley graph."""
    fig = plt.figure(figsize=(12.2, 6.4))
    ax_sphere = fig.add_subplot(1, 2, 1, projection="3d")
    ax_graph = fig.add_subplot(1, 2, 2)

    states = [(0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
    labels = {
        (0, 0, 1): r"$|0\rangle$",
        (0, 0, -1): r"$|1\rangle$",
        (1, 0, 0): r"$|+\rangle$",
        (-1, 0, 0): r"$|-\rangle$",
        (0, 1, 0): r"$|+i\rangle$",
        (0, -1, 0): r"$|-i\rangle$",
    }

    # Left: exact Bloch-sphere realization.
    u = np.linspace(0, 2 * np.pi, 48)
    v = np.linspace(0, np.pi, 25)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax_sphere.plot_wireframe(xs, ys, zs, rstride=4, cstride=4, linewidth=0.35, alpha=0.22)
    for axis_index in range(3):
        segment = np.zeros((2, 3))
        segment[:, axis_index] = (-1.15, 1.15)
        ax_sphere.plot(segment[:, 0], segment[:, 1], segment[:, 2], linewidth=0.7, alpha=0.5)
    for state in states:
        x, y, z = state
        ax_sphere.scatter([x], [y], [z], s=72)
        ax_sphere.text(1.10 * x + 0.03, 1.10 * y + 0.03, 1.10 * z + 0.03, labels[state], fontsize=10)
    ax_sphere.set_xlim(-1.2, 1.2)
    ax_sphere.set_ylim(-1.2, 1.2)
    ax_sphere.set_zlim(-1.2, 1.2)
    ax_sphere.set_box_aspect((1, 1, 1))
    ax_sphere.set_xticks([])
    ax_sphere.set_yticks([])
    ax_sphere.set_zticks([])
    ax_sphere.set_title("six projective Pauli eigenstates")

    # Right: quotient Cayley graph for the two displayed generators.
    layout = {
        (0, 0, 1): (0.0, 1.0),
        (0, 1, 0): (0.86, 0.48),
        (1, 0, 0): (0.86, -0.48),
        (0, 0, -1): (0.0, -1.0),
        (0, -1, 0): (-0.86, -0.48),
        (-1, 0, 0): (-0.86, 0.48),
    }
    system = forest.system
    gate_styles = {
        "H": {"linestyle": "-", "color": "C0", "rad": -0.06},
        "S": {"linestyle": "--", "color": "C1", "rad": 0.10},
    }
    for gate_name, style in gate_styles.items():
        for state in states:
            direction = next(direction for direction in system.directions(state, 0) if direction.name == gate_name)
            target = system.apply(state, direction)
            if target == state:
                continue
            start_point = layout[state]
            end_point = layout[target]
            ax_graph.add_patch(
                FancyArrowPatch(
                    start_point,
                    end_point,
                    arrowstyle="-|>",
                    mutation_scale=9,
                    linewidth=0.9,
                    linestyle=style["linestyle"],
                    color=style["color"],
                    connectionstyle=f"arc3,rad={style['rad']}",
                    alpha=0.62,
                )
            )
    for state, point in layout.items():
        ax_graph.scatter([point[0]], [point[1]], s=84, zorder=4)
        dx = 0.06 if point[0] >= 0 else -0.06
        ax_graph.text(point[0] + dx, point[1] + 0.03, labels[state], ha="left" if point[0] >= 0 else "right", fontsize=10.5)

    handles = [
        Line2D([0], [0], color="C0", linestyle="-", label="$H$ edges"),
        Line2D([0], [0], color="C1", linestyle="--", label="$S$ edges"),
    ]
    ax_graph.legend(handles=handles, loc="lower right")
    ax_graph.text(0, -1.20, f"depth-5 raw routes: {len(forest.paths):,}    quotient states: {len(forest.nodes)}", ha="center", fontsize=9.5)
    ax_graph.set_aspect("equal")
    ax_graph.set_xlim(-1.25, 1.25)
    ax_graph.set_ylim(-1.30, 1.25)
    ax_graph.set_xticks([])
    ax_graph.set_yticks([])
    ax_graph.set_title("relation-reduced gate graph")

    fig.suptitle("Projective qubit orbit under a fixed Clifford gate grammar", fontsize=15)
    fig.subplots_adjust(wspace=0.08, top=0.86)
    _save(fig, path)

def _center_shape(shape: ShapeState) -> np.ndarray:
    points = np.asarray([[float(point[0]), float(point[1])] for point in shape], dtype=float)
    return points - points.mean(axis=0, keepdims=True)


def plot_affine_shape_atlas(shapes: Sequence[ShapeState], labels: Sequence[str], path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(12.0, 5.6))
    slots = np.linspace(0, 10, len(shapes))
    for slot, shape, label in zip(slots, shapes, labels):
        points = _center_shape(shape)
        scale = max(1.0, np.max(np.abs(points)))
        points = points / scale
        points[:, 0] += slot
        polygon = Polygon(points, closed=True, fill=False, linewidth=1.5)
        ax.add_patch(polygon)
        ax.scatter(points[:, 0], points[:, 1], s=28)
        ax.text(slot, -1.45, label, ha="center", fontsize=9)
    ax.set_xlim(-1.1, 11.1)
    ax.set_ylim(-1.8, 1.6)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Affine geometry atlas: each descendant becomes a new source of shape deformations")
    _save(fig, path)


def _matrix_text(state: MatrixState) -> str:
    return f"[{state[0][0]:>3}  {state[0][1]:>3}]\n[{state[1][0]:>3}  {state[1][1]:>3}]"


def plot_matrix_atlas(states: Sequence[MatrixState], labels: Sequence[str], path: str | Path) -> None:
    fig, ax = _diagram_axes(13.0, 6.0)
    ax.set_title("Matrix deformation atlas with exact trace and determinant metadata", pad=16)
    positions = [(0.12, 0.67), (0.34, 0.67), (0.56, 0.67), (0.78, 0.67), (0.34, 0.27), (0.56, 0.27), (0.78, 0.27)]
    for index, (state, label, position) in enumerate(zip(states, labels, positions)):
        x, y = position
        _box(ax, x - 0.08, y - 0.09, 0.16, 0.18, _matrix_text(state), fontsize=12)
        trace = state[0][0] + state[1][1]
        det = state[0][0] * state[1][1] - state[0][1] * state[1][0]
        ax.text(x, y - 0.135, f"{label}\ntr={trace}, det={det}", ha="center", va="top", fontsize=8.5)
    edge_pairs = [(0, 1, "transpose"), (0, 2, "square"), (0, 3, "adjugate"), (1, 4, "symmetrize"), (2, 5, "conjugate"), (3, 6, "commutator")]
    for source, target, label in edge_pairs:
        _arrow(ax, positions[source], positions[target], label, curve=0.10 if target >= 4 else 0.0)
    _save(fig, path)


def _draw_graph(ax: Any, state: GraphState, center: tuple[float, float], radius: float = 0.075) -> None:
    count = len(state)
    angles = np.linspace(math.pi / 2, math.pi / 2 + 2 * math.pi, count, endpoint=False)
    positions = [(center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)) for angle in angles]
    for left, right in _graph_edges(state):
        ax.plot([positions[left][0], positions[right][0]], [positions[left][1], positions[right][1]], linewidth=1.0)
    for point in positions:
        ax.scatter([point[0]], [point[1]], s=35)


def plot_graph_atlas(states: Sequence[GraphState], labels: Sequence[str], path: str | Path) -> None:
    """Render graph rewrites in separated cards so graph and route labels remain legible."""
    fig, ax = _diagram_axes(13.2, 7.4)
    ax.set_title("Graph deformation atlas with quotienting by unlabeled graph isomorphism", pad=16)

    cards = [
        (0.41, 0.73, 0.18, 0.18),
        (0.03, 0.41, 0.19, 0.18), (0.28, 0.41, 0.19, 0.18),
        (0.53, 0.41, 0.19, 0.18), (0.78, 0.41, 0.19, 0.18),
        (0.15, 0.12, 0.20, 0.17), (0.40, 0.12, 0.20, 0.17), (0.65, 0.12, 0.20, 0.17),
    ]
    centers: list[tuple[float, float]] = []
    for state, label, (x, y, width, height) in zip(states, labels, cards):
        patch = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.008,rounding_size=0.01",
            fill=False, linewidth=0.8, alpha=0.55,
        )
        ax.add_patch(patch)
        center = (x + width / 2, y + height * 0.53)
        centers.append(center)
        _draw_graph(ax, state, center, 0.052 if len(state) <= 4 else 0.058)
        ax.text(x + width / 2, y + height - 0.018, label, ha="center", va="top", fontsize=8.5, fontweight="bold")

    root = centers[0]
    operations = ["complement", "line graph", "add leaf", "subdivide"]
    for child_index, operation in enumerate(operations, start=1):
        child = centers[child_index]
        ax.add_patch(
            FancyArrowPatch(
                (root[0], cards[0][1]),
                (child[0], cards[child_index][1] + cards[child_index][3]),
                arrowstyle="-|>", mutation_scale=10, linewidth=0.9,
                connectionstyle=f"arc3,rad={0.05 * (child_index - 2.5)}",
            )
        )
        ax.text((root[0] + child[0]) / 2, 0.655, operation, ha="center", fontsize=8.1)

    lower_ops = [(1, 5, r"$L(\cdot)$"), (2, 6, "complement"), (3, 7, "relabel")]
    for source_index, target_index, operation in lower_ops:
        source = centers[source_index]
        target = centers[target_index]
        ax.add_patch(
            FancyArrowPatch(
                (source[0], cards[source_index][1]),
                (target[0], cards[target_index][1] + cards[target_index][3]),
                arrowstyle="-|>", mutation_scale=9, linewidth=0.8,
                connectionstyle="arc3,rad=0.04",
            )
        )
        ax.text((source[0] + target[0]) / 2, 0.345, operation, ha="center", fontsize=8.0)

    ax.text(
        0.75, 0.075,
        "the final route is relabelled but has the same canonical unlabeled-graph key",
        ha="center", fontsize=8.8,
    )
    ax.text(
        0.5, 0.025,
        "The raw syntax records each rewrite. The quotient key removes vertex-label artifacts.",
        ha="center", fontsize=10.2,
    )
    _save(fig, path)

def _tree_positions(forest: PerturbationForest, x0: float, x1: float, y0: float, y1: float) -> dict[int, tuple[float, float]]:
    levels: dict[int, list[int]] = defaultdict(list)
    for node in forest.nodes.values():
        levels[node.min_depth].append(node.id)
    positions: dict[int, tuple[float, float]] = {}
    maximum = max(levels) if levels else 0
    for depth, ids in levels.items():
        xs = np.linspace(x0, x1, len(ids) + 2)[1:-1]
        y = y1 - (y1 - y0) * depth / max(1, maximum)
        for node_id, x in zip(sorted(ids), xs):
            positions[node_id] = (float(x), float(y))
    return positions


def plot_adic_lift_forest(simple: PerturbationForest, singular: PerturbationForest, path: str | Path) -> None:
    fig, ax = _diagram_axes(13.0, 7.0)
    ax.set_title("Congruence lifting exposes state-dependent branch geometry", pad=16)
    left_positions = _tree_positions(simple, 0.05, 0.45, 0.14, 0.83)
    right_positions = _tree_positions(singular, 0.55, 0.95, 0.14, 0.83)
    for forest, positions in [(simple, left_positions), (singular, right_positions)]:
        for edge in forest.edges.values():
            if edge.source in positions and edge.target in positions:
                start, end = positions[edge.source], positions[edge.target]
                ax.plot([start[0], end[0]], [start[1], end[1]], linewidth=0.8)
        for node in forest.nodes.values():
            if node.id not in positions:
                continue
            x, y = positions[node.id]
            ax.scatter([x], [y], s=35)
            level, residue = node.state
            ax.text(x, y + 0.026, f"{residue} mod {simple.system.prime**level if forest is simple else singular.system.prime**level}", ha="center", fontsize=7)
    ax.text(0.25, 0.92, "$x^2=1$ over powers of 3\nsimple roots lift uniquely", ha="center", fontsize=11, fontweight="bold")
    ax.text(0.75, 0.92, "$x^2=0$ over powers of 2\nsingular roots branch and die", ha="center", fontsize=11, fontweight="bold")
    ax.text(0.5, 0.06, "The direction fiber at one residue is the finite set of valid next digits. Its size is an object property.", ha="center", fontsize=10.5)
    _save(fig, path)


def plot_cross_domain_counts(summaries: Mapping[str, Mapping[str, Any]], path: str | Path) -> None:
    names = list(summaries)
    raw = [int(summaries[name]["raw_paths"]) for name in names]
    quotient = [int(summaries[name]["quotient_nodes"]) for name in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(11.4, 6.2))
    ax.semilogy(x, raw, marker="o", linewidth=1.3, label="raw routes")
    ax.semilogy(x, quotient, marker="s", linewidth=1.3, label="quotient objects")
    for index, (r, q) in enumerate(zip(raw, quotient)):
        ax.plot([index, index], [q, r], linewidth=0.65, alpha=0.45)
    ax.set_xticks(x, names, rotation=28, ha="right")
    ax.set_ylabel("count on logarithmic scale")
    ax.set_title("Route growth and object growth differ across mathematical domains")
    ax.grid(axis="y", which="both", alpha=0.22)
    ax.legend()
    _save(fig, path)


def plot_stability_regimes(path: str | Path) -> None:
    depth = np.arange(0, 18)
    epsilon = 0.01
    regimes = [(0.72, "contractive $L=0.72$"), (1.0, "neutral $L=1$"), (1.16, "expansive $L=1.16$")]
    fig, ax = plt.subplots(figsize=(10.2, 6.0))
    for lipschitz, label in regimes:
        errors = [0.0]
        for _ in depth[1:]:
            errors.append(lipschitz * errors[-1] + epsilon)
        ax.semilogy(depth, np.maximum(errors, 1e-5), marker="o", markersize=3.5, label=label)
    ax.set_xlabel("perturbation depth")
    ax.set_ylabel("propagated endpoint error")
    ax.set_title("Repeated perturbation can contract, accumulate, or amplify local error")
    ax.grid(True, which="both", alpha=0.22)
    ax.legend()
    _save(fig, path)

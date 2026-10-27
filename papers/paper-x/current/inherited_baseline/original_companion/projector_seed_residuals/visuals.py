from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .companion import build_root_forest
from .transport import DirectedGraph, source_components, strongly_connected_components
from .zeta import singular_power_count, smooth_count, weighted_count


def _save(fig: plt.Figure, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / f"{stem}.png", dpi=220, bbox_inches="tight", metadata={})
    fig.savefig(output / f"{stem}.pdf", bbox_inches="tight", metadata={"Author": "Komorebi P.", "Title": stem})
    plt.close(fig)


def _transport_graph() -> DirectedGraph:
    graph = DirectedGraph()
    for vertex in "ABCDEFG":
        graph.add_vertex(vertex)
    for source, target in [("A", "B"), ("B", "A"), ("B", "C"), ("D", "E"), ("E", "D"), ("E", "F")]:
        graph.add_edge(source, target)
    return graph


def make_visuals(output_dir: str | Path, results_path: str | Path | None = None) -> list[str]:
    output = Path(output_dir)
    stems: list[str] = []

    # 1. Residual seed architecture as nested formal neighborhoods.
    fig, ax = plt.subplots(figsize=(8.2, 5.5))
    centers = [(-2.6, 0), (0, 0), (2.6, 0)]
    for index, (cx, cy) in enumerate(centers):
        for radius in (0.35, 0.72, 1.08):
            circle = plt.Circle((cx, cy), radius, fill=False, linewidth=1.4)
            ax.add_patch(circle)
        ax.scatter([cx], [cy], s=75)
        ax.text(cx, cy - 1.38, rf"residual root $\bar\rho_{index}$", ha="center")
    ax.text(0, 1.72, "one special fiber; one formal neighborhood above each root", ha="center", fontsize=13)
    ax.set_xlim(-4.1, 4.1)
    ax.set_ylim(-1.8, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    _save(fig, output, "01_residual_seed_architecture")
    stems.append("01_residual_seed_architecture")

    # 2. Full 3-adic digit forest through four levels.
    p, depth = 3, 4
    fig, ax = plt.subplots(figsize=(10.0, 6.4))
    level_paths: dict[int, list[tuple[int, ...]]] = {}
    for level in range(1, depth + 1):
        paths = [()]
        for _ in range(level):
            paths = [prefix + (digit,) for prefix in paths for digit in range(p)]
        level_paths[level] = paths

    def position(path: tuple[int, ...]) -> float:
        index = 0
        for digit in path:
            index = p * index + digit
        return (index + 0.5) / (p ** len(path))

    for level in range(1, depth + 1):
        y = depth - level
        for path in level_paths[level]:
            x = position(path)
            ax.scatter([x], [y], s=11 if level > 2 else 28)
            if level < depth:
                for digit in range(p):
                    child = path + (digit,)
                    ax.plot([x, position(child)], [y, y - 1], linewidth=0.45, alpha=0.55)
    ax.set_title("Finite 3-adic residual forest: later digits refine but do not cross roots")
    ax.set_xlabel("lexicographic digit address")
    ax.set_yticks(range(depth), [f"depth {depth-i}" for i in range(depth)])
    ax.set_xlim(-0.02, 1.02)
    ax.grid(alpha=0.15)
    _save(fig, output, "02_residual_digit_forest")
    stems.append("02_residual_digit_forest")

    # 3. No-crossing branches from three roots.
    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    levels = np.arange(1, 9)
    for root in range(3):
        for branch in range(5):
            x = root + 0.12 * np.sin((branch + 1) * levels)
            ax.plot(x, levels, linewidth=1.0)
    ax.set_xticks([0, 1, 2], [r"$\bar\rho_0$", r"$\bar\rho_1$", r"$\bar\rho_2$"])
    ax.set_ylabel("congruence depth")
    ax.set_title("Positive-depth perturbations remain above one residual root")
    ax.grid(alpha=0.2)
    _save(fig, output, "03_no_crossing_branches")
    stems.append("03_no_crossing_branches")

    # 4. Inverse-limit digit reconstruction.
    digits = [2, 4, 1, 3, 0, 2]
    residues = []
    total = 0
    for i, digit in enumerate(digits):
        total += digit * 5**i
        residues.append(total)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.step(np.arange(1, len(residues) + 1), residues, where="mid")
    ax.scatter(np.arange(1, len(residues) + 1), residues)
    for depth_index, digit in enumerate(digits, start=1):
        ax.text(depth_index, residues[depth_index - 1], f" digit {digit}", va="bottom", ha="center")
    ax.set_xlabel("depth")
    ax.set_ylabel("compatible residue")
    ax.set_title("Inverse-limit branch reconstructed from stable base-5 digits")
    ax.grid(alpha=0.2)
    _save(fig, output, "04_inverse_limit_digits")
    stems.append("04_inverse_limit_digits")

    # 5. Dyadic delayed separation of +1 and -1.
    depths = np.arange(1, 8)
    plus = [1 % (2**d) for d in depths]
    minus = [(-1) % (2**d) for d in depths]
    fig, ax = plt.subplots(figsize=(8.1, 4.8))
    ax.plot(depths, plus, marker="o", label="+1 branch")
    ax.plot(depths, minus, marker="o", label="-1 branch")
    ax.set_xlabel("2-adic depth")
    ax.set_ylabel("residue representative")
    ax.set_title("Dyadic delayed visibility: the sign packets merge mod 2 and split mod 4")
    ax.legend()
    ax.grid(alpha=0.2)
    _save(fig, output, "05_dyadic_delayed_separation")
    stems.append("05_dyadic_delayed_separation")

    # 6. Smooth and singular branch counts.
    depths = np.arange(1, 13)
    smooth = [smooth_count(3, 2, int(d)) for d in depths]
    singular = [singular_power_count(3, 2, int(d)) for d in depths]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(depths, smooth, marker="o", label="smooth d=2 chart")
    ax.plot(depths, singular, marker="o", label=r"singular $x^2=0$")
    ax.set_yscale("log", base=3)
    ax.set_xlabel("depth")
    ax.set_ylabel("number of finite-depth lifts")
    ax.set_title("Branch growth distinguishes smooth and singular seeds")
    ax.legend()
    ax.grid(alpha=0.2)
    _save(fig, output, "06_smooth_singular_counts")
    stems.append("06_smooth_singular_counts")

    # 7. Weighted dyadic chart count.
    depths = np.arange(1, 13)
    unweighted = [weighted_count(2, [1, 1, 1], int(d)) for d in depths]
    weighted = [weighted_count(2, [1, 2, 4], int(d)) for d in depths]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(depths, unweighted, marker="o", label="weights (1,1,1)")
    ax.plot(depths, weighted, marker="o", label="weights (1,2,4)")
    ax.set_yscale("log", base=2)
    ax.set_xlabel("depth")
    ax.set_ylabel("number of visible coordinate choices")
    ax.set_title("Weighted coordinates delay branch visibility without changing the eventual slope")
    ax.legend()
    ax.grid(alpha=0.2)
    _save(fig, output, "07_weighted_formal_chart")
    stems.append("07_weighted_formal_chart")

    # 8. Fractional seed dimensions for x^e = 0.
    exponents = np.arange(2, 9)
    dimensions = 1 - 1 / exponents
    fig, ax = plt.subplots(figsize=(7.8, 4.7))
    ax.plot(exponents, dimensions, marker="o")
    ax.set_xlabel("singular exponent e")
    ax.set_ylabel("branching dimension")
    ax.set_title(r"Exact singular seed dimension for $x^e=0$: $1-1/e$")
    ax.grid(alpha=0.2)
    _save(fig, output, "08_fractional_seed_dimension")
    stems.append("08_fractional_seed_dimension")

    # 9. Directed transport graph.
    graph = _transport_graph()
    positions = {
        "A": (0, 0.85), "B": (1.1, 0.85), "C": (2.35, 0.85),
        "D": (0, -0.45), "E": (1.1, -0.45), "F": (2.35, -0.45),
        "G": (3.35, 0.2),
    }
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    for vertex, (x, y) in positions.items():
        ax.scatter([x], [y], s=180)
        ax.text(x, y, vertex, ha="center", va="center")
    for source, targets in graph.adjacency.items():
        for target in targets:
            x0, y0 = positions[source]
            x1, y1 = positions[target]
            ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.12"})
    ax.set_title("Directed residual transports: three source components require three initial seeds")
    ax.axis("off")
    _save(fig, output, "09_directed_transport_graph")
    stems.append("09_directed_transport_graph")

    # 10. Condensation graph source components.
    components = strongly_connected_components(graph)
    component_index = {vertex: i for i, component in enumerate(components) for vertex in component}
    source_sets = source_components(graph)
    source_indices = {component_index[next(iter(component))] for component in source_sets}
    # Arrange source components in a left column and their descendants to the right.
    labels = {i: "{" + ",".join(sorted(component)) + "}" for i, component in enumerate(components)}
    label_to_index = {labels[i]: i for i in labels}
    desired = ["{A,B}", "{C}", "{D,E}", "{F}", "{G}"]
    compact_positions = {
        label_to_index["{A,B}"]: (0.0, 0.8),
        label_to_index["{C}"]: (1.7, 0.8),
        label_to_index["{D,E}"]: (0.0, -0.35),
        label_to_index["{F}"]: (1.7, -0.35),
        label_to_index["{G}"]: (0.0, -1.5),
    }
    fig, ax = plt.subplots(figsize=(8.0, 5.1))
    for i, component in enumerate(components):
        x, y = compact_positions[i]
        ax.scatter([x], [y], s=240)
        ax.text(x, y, labels[i], ha="center", va="center")
        if i in source_indices:
            ax.text(x - 0.05, y + 0.36, "source", ha="center")
    edges = set()
    for source, targets in graph.adjacency.items():
        for target in targets:
            i, j = component_index[source], component_index[target]
            if i != j:
                edges.add((i, j))
    for i, j in edges:
        x0, y0 = compact_positions[i]
        x1, y1 = compact_positions[j]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->"})
    ax.set_xlim(-0.7, 2.4)
    ax.set_ylim(-1.95, 1.35)
    ax.set_title("Condensation DAG: minimum seed count equals the number of source SCCs")
    ax.axis("off")
    _save(fig, output, "10_source_scc_condensation")
    stems.append("10_source_scc_condensation")

    # 11. Tangent and obstruction packet dimensions.
    data = np.array([[0, 0, 0], [1, 2, 1]], dtype=float)
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    image = ax.imshow(data, aspect="auto")
    fig.colorbar(image, ax=ax, label="cohomology dimension")
    ax.set_xticks([0, 1, 2], [r"$H^0$", r"$H^1$", r"$H^2$"])
    ax.set_yticks([0, 1], ["packet 0", "packet 1"])
    ax.set_title("Chain projectors split tangent and obstruction cohomology exactly")
    _save(fig, output, "11_tangent_obstruction_packets")
    stems.append("11_tangent_obstruction_packets")

    # 12. Companion forest occupancy for x^2+1.
    primes = [2, 3, 5, 7, 13]
    matrix = np.array([[len(build_root_forest([1, 0, 1], p, 5).levels[d]) for d in range(5)] for p in primes], dtype=float)
    fig, ax = plt.subplots(figsize=(7.5, 4.9))
    image = ax.imshow(matrix, aspect="auto")
    fig.colorbar(image, ax=ax, label="number of roots")
    ax.set_xticks(range(5), [f"depth {d}" for d in range(1, 6)])
    ax.set_yticks(range(len(primes)), [f"p={p}" for p in primes])
    ax.set_title(r"Finite companion forests for $x^2+1=0$")
    _save(fig, output, "12_companion_forest_occupancy")
    stems.append("12_companion_forest_occupancy")

    # 13. Prime-independent system spine.
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    primes = [3, 5, 7, 11]
    for index, p in enumerate(primes):
        ax.scatter([index], [0], s=150)
        ax.text(index, -0.28, f"lambda | {p}", ha="center")
        ax.plot([index, 1.5], [0.08, 1.2], linewidth=1.0)
    ax.scatter([1.5], [1.35], s=230)
    ax.text(1.5, 1.35, "common Frobenius spine", ha="center", va="center")
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(-0.55, 1.8)
    ax.set_title("Local coefficient-prime members glued through one algebraic spine")
    ax.axis("off")
    _save(fig, output, "13_common_system_spine")
    stems.append("13_common_system_spine")

    # 14. Frobenius trace separator matrix.
    trace_matrix = np.array([[1, 1, 1], [1, 2, 3], [2, 1, 0]], dtype=float)
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    image = ax.imshow(trace_matrix, aspect="equal")
    fig.colorbar(image, ax=ax, label="trace value")
    ax.set_xticks([0, 1, 2], ["constituent 1", "constituent 2", "constituent 3"])
    ax.set_yticks([0, 1, 2], [r"$v_1$", r"$v_2$", r"$v_3$"])
    ax.set_title("Finite Frobenius evaluations separate compatible constituents")
    _save(fig, output, "14_frobenius_separator_matrix")
    stems.append("14_frobenius_separator_matrix")

    # 15. Finite occupancy ranks.
    ranks = [3, 2, 1, 0]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.step(np.arange(1, 5), ranks, where="mid")
    ax.scatter(np.arange(1, 5), ranks)
    ax.set_xticks(np.arange(1, 5), ["condition 1", "condition 2", "condition 3", "inconsistent"])
    ax.set_ylabel("joint projector rank")
    ax.set_title("Finite spectral occupancy is an exact nonnegative trace")
    ax.grid(alpha=0.2)
    _save(fig, output, "15_finite_occupancy_ranks")
    stems.append("15_finite_occupancy_ranks")

    # 16. Proof-status matrix.
    labels = [
        "residual partition",
        "no crossing",
        "inverse limit",
        "cohomology packets",
        "transport seed count",
        "seed zeta models",
        "companion compactness",
        "carrier completion",
        "finite occupancy",
        "universal companion existence",
        "universal automorphic occupancy",
    ]
    status = np.array([
        [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],
        [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1],
    ], dtype=float)
    fig, ax = plt.subplots(figsize=(8.2, 6.2))
    ax.imshow(status, aspect="auto")
    ax.set_xticks([0, 1, 2], ["proved here", "classical input", "remaining existence"])
    ax.set_yticks(np.arange(len(labels)), labels)
    for i in range(status.shape[0]):
        for j in range(status.shape[1]):
            if status[i, j]:
                ax.text(j, i, "yes", ha="center", va="center")
    ax.set_title("Proof boundary for universal residual seeds")
    _save(fig, output, "16_proof_status")
    stems.append("16_proof_status")

    return stems

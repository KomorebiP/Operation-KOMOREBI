from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from .dyadic import delayed_separation_example
from .projectors import refinement_incidence, residue_projectors
from .smith_chart import gamma_from_impedance, polyphase_orbit, smith_weight
from .stability import compatible_replication_tower, defect_norm_bound
from .weighted import Edge, path_counts, path_zeta, zeta_coefficients


def _save(fig: plt.Figure, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(output / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def _graph() -> list[Edge]:
    return [
        Edge(0, 0, 2), Edge(0, 1, 1), Edge(1, 1, 3),
        Edge(1, 2, 2), Edge(2, 0, 1), Edge(2, 2, 4),
    ]


def make_visuals(output_dir: str | Path) -> list[str]:
    output = Path(output_dir)
    stems: list[str] = []

    # 1. Nested 2-4-8 packet tree.
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    levels = [2, 4, 8]
    positions: dict[tuple[int, int], tuple[float, float]] = {}
    for level_index, modulus in enumerate(levels):
        y = 2 - level_index
        xs = np.linspace(0, 1, modulus)
        for j, x in enumerate(xs):
            positions[(modulus, j)] = (float(x), float(y))
            ax.scatter([x], [y], s=130)
            ax.text(x, y + 0.13, f"{j} mod {modulus}", ha="center", fontsize=8)
        if level_index:
            parent_modulus = levels[level_index - 1]
            for j, x in enumerate(xs):
                parent = j % parent_modulus
                x0, y0 = positions[(parent_modulus, parent)]
                ax.plot([x0, x], [y0, y], linewidth=1)
    ax.set_title("Exact nested refinement: residue packets 2 -> 4 -> 8")
    ax.axis("off")
    _save(fig, output, "01_nested_dyadic_refinement")
    stems.append("01_nested_dyadic_refinement")

    # 2. Dyadic-odd CRT grid.
    values = np.zeros((3, 8), dtype=int)
    for j in range(24):
        values[j % 3, j % 8] = j
    fig, ax = plt.subplots(figsize=(9.5, 4.7))
    image = ax.imshow(values, aspect="equal")
    fig.colorbar(image, ax=ax, label="residue modulo 24")
    ax.set_xticks(range(8), [f"{j} mod 8" for j in range(8)], rotation=45, ha="right")
    ax.set_yticks(range(3), [f"{j} mod 3" for j in range(3)])
    for i in range(3):
        for j in range(8):
            ax.text(j, i, str(values[i, j]), ha="center", va="center", fontsize=9)
    ax.set_title("Dyadic-odd packet factorization: mod 24 = mod 8 x mod 3")
    _save(fig, output, "02_crt_dyadic_odd_grid")
    stems.append("02_crt_dyadic_odd_grid")

    # 3. Incidence matrix.
    incidence = refinement_incidence(4, 12)
    fig, ax = plt.subplots(figsize=(9.4, 4.2))
    image = ax.imshow(incidence, aspect="auto")
    fig.colorbar(image, ax=ax, label="child belongs to parent")
    ax.set_xlabel("fine residue mod 12")
    ax.set_ylabel("coarse residue mod 4")
    ax.set_title("Exact coarse/fine incidence matrix")
    _save(fig, output, "03_refinement_incidence")
    stems.append("03_refinement_incidence")

    # 4. Weighted transfer graph.
    coordinates = {0: (0.1, 0.35), 1: (0.5, 0.75), 2: (0.86, 0.35)}
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for vertex, (x, y) in coordinates.items():
        ax.scatter([x], [y], s=650)
        ax.text(x, y, str(vertex), ha="center", va="center", fontsize=13)
    for index, edge in enumerate(_graph()):
        x0, y0 = coordinates[edge.source]
        x1, y1 = coordinates[edge.target]
        rad = 0.24 if edge.source == edge.target else (0.10 if index % 2 else -0.10)
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->", "connectionstyle": f"arc3,rad={rad}"})
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        if edge.source == edge.target:
            xm += 0.06
            ym += 0.13
        ax.text(xm, ym, f"w={edge.weight}", fontsize=10)
    ax.set_title("Weighted transfer graph")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.1, 1)
    ax.axis("off")
    _save(fig, output, "04_weighted_transfer_graph")
    stems.append("04_weighted_transfer_graph")

    # 5. Path-zeta coefficients.
    t = sp.Symbol("t")
    zeta = path_zeta(3, _graph(), [0], [2], t)
    coefficients = zeta_coefficients(zeta, t, 36)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.stem(range(len(coefficients)), coefficients)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("total path weight")
    ax.set_ylabel("number of paths")
    ax.set_title("Coefficients of the weighted transfer-zeta function")
    ax.grid(alpha=0.25)
    _save(fig, output, "05_path_zeta_coefficients")
    stems.append("05_path_zeta_coefficients")

    # 6. Filtered inverse depth.
    depths = np.arange(1, 13)
    retained_terms = depths.copy()
    fig, ax = plt.subplots(figsize=(7.8, 4.7))
    ax.plot(depths, retained_terms, marker="o")
    ax.set_xlabel("p-adic precision L")
    ax.set_ylabel("maximum required path weight")
    ax.set_title("Finite weighted inverse: only paths of weight below L contribute")
    ax.grid(alpha=0.25)
    _save(fig, output, "06_filtered_inverse_depth")
    stems.append("06_filtered_inverse_depth")

    # 7. Delayed dyadic separation.
    delayed = delayed_separation_example()
    matrices = [delayed["plus"], delayed["minus"]]
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.9))
    for ax, matrix, title in zip(axes, matrices, [r"$E_+=(I+A)/2$", r"$E_-=(I-A)/2$"]):
        array = np.array(matrix.tolist(), dtype=float)
        ax.imshow(array, aspect="equal")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=13)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title)
    fig.suptitle("Dyadic delayed separation: rational projectors need one extra 2-adic digit")
    _save(fig, output, "07_dyadic_delayed_separation")
    stems.append("07_dyadic_delayed_separation")

    # 8. Odd-prime separation comparison.
    primes = [2, 3, 5, 7, 11]
    weights = [1, 0, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar([str(p) for p in primes], weights)
    ax.set_xlabel("coefficient prime")
    ax.set_ylabel("projector denominator weight")
    ax.set_title("The sign split is weighted only at the dyadic prime")
    _save(fig, output, "08_odd_prime_separation")
    stems.append("08_odd_prime_separation")

    # 9. Refinement defect bound.
    _, C, Tf, Tc = compatible_replication_tower(np.array([0.4, 0.8, 1.3]), 3)
    Tf[0, 0] += 0.09
    actual = []
    bounds = []
    powers = range(1, 13)
    for n in powers:
        a, b = defect_norm_bound(C, Tf, Tc, n)
        actual.append(a)
        bounds.append(b)
    fig, ax = plt.subplots(figsize=(8.2, 4.7))
    ax.plot(list(powers), actual, marker="o", label="actual defect")
    ax.plot(list(powers), bounds, marker="s", label="telescoping bound")
    ax.set_xlabel("operator power")
    ax.set_ylabel("spectral norm")
    ax.set_title("Propagation of a one-step refinement defect")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, output, "09_refinement_defect_bound")
    stems.append("09_refinement_defect_bound")

    # 10. Transfer block sparsity.
    length = 48
    operator = np.zeros((length, length))
    for i in range(length):
        operator[i, i] = 2
        if i + 1 < length:
            operator[i, i + 1] = -1
            operator[i + 1, i] = -0.7
        if i + 5 < length:
            operator[i, i + 5] = 0.18
    ps = residue_projectors(length, 6)
    block_norms = np.array([[np.linalg.norm(ps[i] @ operator @ ps[j]) for j in range(6)] for i in range(6)])
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    image = ax.imshow(block_norms, aspect="equal")
    fig.colorbar(image, ax=ax, label="Frobenius norm")
    ax.set_xlabel("input packet")
    ax.set_ylabel("output packet")
    ax.set_title("Transfer-block sparsity after mod-6 resolution")
    _save(fig, output, "10_transfer_block_sparsity")
    stems.append("10_transfer_block_sparsity")

    # 11. Smith polyphase orbit.
    orders = [2, 4, 8, 16]
    fig, axes = plt.subplots(2, 2, figsize=(9, 8.2))
    for ax, order in zip(axes.ravel(), orders):
        orbit = polyphase_orbit(0.72, order)
        gamma = np.array([gamma_from_impedance(z) for z in orbit])
        theta = np.linspace(0, 2 * np.pi, 500)
        ax.plot(np.cos(theta), np.sin(theta), linewidth=1)
        ax.scatter(gamma.real, gamma.imag, s=40)
        ax.set_aspect("equal")
        ax.set_title(f"N={order}")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Nested polyphase sampling on the Smith reflection disk")
    _save(fig, output, "11_smith_polyphase_orbit")
    stems.append("11_smith_polyphase_orbit")

    # 12. Smith adaptive weight.
    grid = np.linspace(-0.98, 0.98, 300)
    X, Y = np.meshgrid(grid, grid)
    Gamma = X + 1j * Y
    W = np.full_like(X, np.nan, dtype=float)
    mask = np.abs(Gamma) < 0.985
    W[mask] = np.log10(np.array([smith_weight(g) for g in Gamma[mask]]))
    fig, ax = plt.subplots(figsize=(6.7, 5.8))
    image = ax.imshow(W, extent=[-0.98, 0.98, -0.98, 0.98], origin="lower", aspect="equal")
    fig.colorbar(image, ax=ax, label="log10 adaptive weight")
    ax.set_xlabel(r"$\Re\,\Gamma$")
    ax.set_ylabel(r"$\Im\,\Gamma$")
    ax.set_title("Symmetric refinement weight near open and short boundaries")
    _save(fig, output, "12_smith_adaptive_weight")
    stems.append("12_smith_adaptive_weight")

    # 13. Theorem dependency diagram.
    labels = {
        "A": (0.10, 0.78, "packet axioms"),
        "B": (0.34, 0.78, "nested refinement"),
        "C": (0.62, 0.78, "dyadic-odd CRT"),
        "D": (0.10, 0.28, "weighted paths"),
        "E": (0.36, 0.28, "filtered inverse"),
        "F": (0.62, 0.28, "path zeta"),
        "G": (0.84, 0.53, "delayed separation"),
    }
    arrows = [("A", "B"), ("B", "C"), ("D", "E"), ("D", "F"), ("C", "G"), ("E", "G")]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for key, (x, y, text) in labels.items():
        ax.text(x, y, text, ha="center", va="center", bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "black"})
    for source, target in arrows:
        x0, y0, _ = labels[source]
        x1, y1, _ = labels[target]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->"})
    ax.set_title("Proof dependency map for Seed Calculus II")
    ax.set_xlim(0, 0.94)
    ax.set_ylim(0.12, 0.92)
    ax.axis("off")
    _save(fig, output, "13_theorem_dependency")
    stems.append("13_theorem_dependency")

    return stems

"""Exact address and projector figures, plus a fixed numerical stencil example.

The data contracts match canonical_v1.2.1/code/python/seed_refinement/visuals.py.
This module changes presentation only and has no symbolic runtime dependency.
"""
from fractions import Fraction
from pathlib import Path
import json

import numpy as np
from matplotlib.patches import Rectangle

from common import canvas, clean_axes, footer, save, INK, MUTED, TEAL, LIGHT, GRID, HEAT


def _table(ax, values, fill=None, labels=None, font=11.5):
    """Draw a fixed cell grid with high contrast labels and explicit zeros."""
    rows, columns = values.shape
    if labels is None:
        labels = [[str(values[i, j]) for j in range(columns)] for i in range(rows)]
    for i in range(rows):
        for j in range(columns):
            color = LIGHT if fill is None else fill(i, j)
            ax.add_patch(Rectangle((j-.5, i-.5), 1, 1,
                                   facecolor=color, edgecolor="white", linewidth=1.2))
            label_color = "white" if color == TEAL else INK
            if str(labels[i][j]) == "0" and color != TEAL:
                label_color = MUTED
            ax.text(j, i, labels[i][j], ha="center", va="center",
                    color=label_color, fontsize=font)
    ax.set_xlim(-.5, columns-.5)
    ax.set_ylim(rows-.5, -.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, labelsize=10.5, pad=5)


def nested_dyadic():
    fig = canvas("A nested residue hierarchy", "Each child retains its residue address in the coarser level.", 3.9)
    ax = fig.add_axes([.085, .20, .89, .57])
    ax.set_xlim(-.85, 7.55)
    ax.set_ylim(-.27, 2.28)
    orders = {2: [0, 1], 4: [0, 2, 1, 3], 8: [0, 4, 2, 6, 1, 5, 3, 7]}
    positions = {}
    for j, value in enumerate(orders[8]):
        positions[(8, value)] = (float(j), 0.)
    for modulus, next_modulus, y in ((4, 8, 1.), (2, 4, 2.)):
        for j in orders[modulus]:
            children = [positions[(next_modulus, child)][0]
                        for child in orders[next_modulus] if child % modulus == j]
            positions[(modulus, j)] = (float(np.mean(children)), y)
    edges = []
    for parent_modulus, child_modulus in ((2, 4), (4, 8)):
        for child in orders[child_modulus]:
            parent = child % parent_modulus
            x0, y0 = positions[(parent_modulus, parent)]
            x1, y1 = positions[(child_modulus, child)]
            ax.plot([x0, x1], [y0, y1], color=GRID, linewidth=2.2, zorder=1)
            edges.append([parent_modulus, parent, child_modulus, child])
    for modulus, y in ((2, 2.), (4, 1.), (8, 0.)):
        ax.text(-.65, y, f"mod {modulus}", ha="right", va="center", fontsize=10.5, color=MUTED)
        for j in orders[modulus]:
            x, _ = positions[(modulus, j)]
            ax.scatter([x], [y], s=390, facecolor=LIGHT, edgecolor=TEAL,
                       linewidth=1.4, zorder=2)
            ax.text(x, y, str(j), ha="center", va="center", fontsize=11.5, weight="bold", zorder=3)
    ax.axis("off")
    footer(fig, "A child j at level 2N belongs to the parent j mod N.")
    save(fig, "01_nested_dyadic_refinement")
    assert all(child % parent_modulus == parent for parent_modulus, parent, _, child in edges)
    return {"level_orders": orders, "edges": edges, "check": "All 12 edges retain the exact residue parent."}


def crt_grid():
    values = np.zeros((3, 8), dtype=int)
    for j in range(24):
        values[j % 3, j % 8] = j
    fig = canvas("Two coordinates for each residue", r"The mod 24 address is equivalent to its mod 8 and mod 3 addresses.", 3.6)
    ax = fig.add_axes([.14, .27, .825, .43])
    _table(ax, values, font=12)
    ax.set_xticks(range(8))
    ax.set_yticks(range(3))
    ax.set_xlabel("Residue modulo 8", fontsize=10.5, labelpad=8)
    ax.set_ylabel("Residue modulo 3", fontsize=10.5, labelpad=9)
    footer(fig, "Each cell contains the unique residue j modulo 24 with those two addresses.")
    save(fig, "02_crt_dyadic_odd_grid")
    assert sorted(values.ravel()) == list(range(24))
    assert all(values[i, j] % 3 == i and values[i, j] % 8 == j
               for i in range(3) for j in range(8))
    return {"values": values.tolist(), "check": "All 24 cells satisfy both residue equations exactly."}


def incidence_grid():
    values = np.array([[int(child % 4 == parent) for child in range(12)] for parent in range(4)])
    fig = canvas("Exact refinement incidence", r"A fine residue modulo 12 belongs to its residue modulo 4.", 3.65)
    ax = fig.add_axes([.13, .27, .835, .46])
    _table(ax, values, fill=lambda i, j: TEAL if values[i, j] else LIGHT, font=10.5)
    ax.set_xticks(range(12))
    ax.set_yticks(range(4))
    ax.set_xlabel("Fine residue modulo 12", fontsize=10.5, labelpad=8)
    ax.set_ylabel("Coarse residue modulo 4", fontsize=10.5, labelpad=9)
    footer(fig, "Each fine packet has one parent. Each coarse packet contains three children.")
    save(fig, "03_refinement_incidence")
    assert np.all(values.sum(axis=0) == 1)
    assert np.all(values.sum(axis=1) == 3)
    return {"values": values.tolist(), "check": "All 12 child columns have one parent and all four parent rows have three children."}


def rational_projectors():
    F = Fraction
    A = np.array([[F(1), F(1)], [F(0), F(-1)]], dtype=object)
    I = np.array([[F(1), F(0)], [F(0), F(1)]], dtype=object)
    plus, minus = (I+A)/2, (I-A)/2
    fig = canvas("The two rational sign projectors", r"An integral involution separates over the rationals with denominator 2.", 3.9)
    fig.text(.265, .76, r"$E_+=(I+A)/2$", ha="center", va="center", fontsize=13.5, color=TEAL)
    fig.text(.755, .76, r"$E_-=(I-A)/2$", ha="center", va="center", fontsize=13.5, color=TEAL)
    for left, matrix in ((.13, plus), (.62, minus)):
        ax = fig.add_axes([left, .27, .27, .39])
        labels = [[r"$\frac{1}{2}$" if value == F(1, 2) else r"$-\frac{1}{2}$" if value == F(-1, 2) else str(value)
                   for value in row] for row in matrix]
        _table(ax, matrix, labels=labels, font=17)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        # Matrix brackets remain separate from the cells.
        ax.plot([-.61, -.68, -.68, -.61], [-.48, -.48, 1.48, 1.48],
                color=TEAL, linewidth=1.5, clip_on=False)
        ax.plot([1.61, 1.68, 1.68, 1.61], [-.48, -.48, 1.48, 1.48],
                color=TEAL, linewidth=1.5, clip_on=False)
    fig.text(.51, .18, r"$E_+^2=E_+,\quad E_-^2=E_-,\quad E_+E_-=E_-E_+=0$",
             ha="center", va="center", fontsize=10.5)
    footer(fig, r"Here A = [[1, 1], [0, −1]]. Both projectors have exact 2-adic denominator weight one.")
    save(fig, "07_dyadic_delayed_separation")
    Z = np.zeros((2, 2), dtype=int)
    assert np.array_equal(A@A, I)
    assert np.array_equal(plus@plus, plus) and np.array_equal(minus@minus, minus)
    assert np.array_equal(plus@minus, Z) and np.array_equal(minus@plus, Z)
    assert np.array_equal(plus+minus, I)
    return {"A": [[str(v) for v in row] for row in A], "plus": [[str(v) for v in row] for row in plus],
            "minus": [[str(v) for v in row] for row in minus],
            "check": "Fraction arithmetic verifies involution, idempotence, both orthogonal products, and sum identity exactly."}


def prime_weights():
    primes = [2, 3, 5, 7, 11]
    weights = []
    for prime in primes:
        denominator, valuation = 2, 0
        while denominator % prime == 0:
            denominator //= prime
            valuation += 1
        weights.append(valuation)
    fig = canvas("The denominator singles out the prime two", r"The exact local weight of each sign projector is $v_p(2)$.", 3.8)
    ax = fig.add_axes([.13, .25, .83, .49])
    xs = np.arange(len(primes))
    ax.bar(xs, weights, width=.52, color=TEAL)
    ax.scatter(xs[1:], weights[1:], s=30, color=TEAL, zorder=3)
    for x, value in zip(xs, weights):
        ax.text(x, value+.10, str(value), ha="center", va="bottom", fontsize=12, weight="bold", color=TEAL)
    ax.set_xticks(xs, [str(p) for p in primes])
    ax.set_yticks([0, 1])
    ax.set_ylim(-.05, 1.35)
    ax.set_xlabel("Coefficient prime p", fontsize=10.5, labelpad=8)
    ax.set_ylabel("Denominator weight", fontsize=10.5, labelpad=10)
    clean_axes(ax)
    footer(fig, "The denominator 2 is a unit at every odd prime.")
    save(fig, "08_odd_prime_separation")
    assert weights == [1, 0, 0, 0, 0]
    return {"primes": primes, "weights": weights,
            "check": "Integer valuation of denominator 2 gives [1, 0, 0, 0, 0] for the original five primes."}


def stencil_norms():
    length, modulus = 48, 6
    operator = np.zeros((length, length))
    squared_exact = [[Fraction(0) for _ in range(modulus)] for _ in range(modulus)]
    coefficients = [(0, Fraction(2)), (1, Fraction(-1)), (-1, Fraction(-7, 10)), (5, Fraction(9, 50))]
    for row in range(length):
        for displacement, value in coefficients:
            column = row + displacement
            if 0 <= column < length:
                operator[row, column] = float(value)
                squared_exact[row % modulus][column % modulus] += value*value
    block_norms = np.array([[np.linalg.norm(operator[np.ix_(np.arange(i, length, modulus), np.arange(j, length, modulus))])
                            for j in range(modulus)] for i in range(modulus)])
    exact_as_float = np.array([[float(value) for value in row] for row in squared_exact])
    assert np.allclose(block_norms*block_norms, exact_as_float, atol=1e-13, rtol=1e-14)
    fig = canvas("A sparse transfer pattern", "Frobenius norms for the fixed 48 coordinate stencil, resolved modulo 6.", 4.75)
    ax = fig.add_axes([.15, .23, .64, .58])
    image = ax.imshow(block_norms, cmap=HEAT, vmin=0, vmax=float(block_norms.max()), aspect="equal")
    for i in range(modulus):
        for j in range(modulus):
            value = block_norms[i, j]
            label = "0" if value == 0 else f"{value:.2f}"
            color = "white" if value > .60*block_norms.max() else INK
            if value == 0:
                color = MUTED
            ax.text(j, i, label, ha="center", va="center", fontsize=11.5, color=color)
    ax.set_xticks(range(modulus))
    ax.set_yticks(range(modulus))
    ax.set_xticks(np.arange(-.5, modulus, 1), minor=True)
    ax.set_yticks(np.arange(-.5, modulus, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=0, labelsize=10.5, pad=5)
    ax.set_xlabel("Input packet j", fontsize=10.5, labelpad=8)
    ax.set_ylabel("Output packet i", fontsize=10.5, labelpad=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cax = fig.add_axes([.84, .255, .025, .53])
    colorbar = fig.colorbar(image, cax=cax, ticks=[0, 2, 4, 6])
    colorbar.ax.tick_params(labelsize=10, length=3)
    colorbar.outline.set_visible(False)
    fig.text(.84, .83, "Norm", ha="left", va="bottom", fontsize=10.5, color=MUTED)
    footer(fig, "The diagonal preserves a packet. Only the two neighboring phases transfer.\nExact squared norms were checked with rational arithmetic. Displayed norms are rounded.")
    save(fig, "10_transfer_block_sparsity")
    support = (block_norms > 0).astype(int)
    assert all(support[i, j] == int((j-i) % modulus in (0, 1, 5))
               for i in range(modulus) for j in range(modulus))
    return {"length": length, "modulus": modulus, "stencil": [[d, str(v)] for d, v in coefficients],
            "block_norms": block_norms.tolist(), "squared_norms_exact": [[str(v) for v in row] for row in squared_exact],
            "support": support.tolist(),
            "check": "All 36 numerical squared norms agree with exact rational sums. Support is exactly the diagonal and two adjacent phases."}


def generate():
    result = {
        "01_nested_dyadic_refinement": nested_dyadic(),
        "02_crt_dyadic_odd_grid": crt_grid(),
        "03_refinement_incidence": incidence_grid(),
        "07_dyadic_delayed_separation": rational_projectors(),
        "08_odd_prime_separation": prime_weights(),
        "10_transfer_block_sparsity": stencil_norms(),
    }
    (Path(__file__).parent / "matrix_visual_data.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    generate()
    print("All six matrix and address figures generated with their data checks passing.")

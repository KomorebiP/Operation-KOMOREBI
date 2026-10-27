"""Exact data and spacious main figures for the graph and Smith branches.

The numerical models and finite ranges are inherited unchanged from canonical
v1.2.1. The walk coefficients are recomputed with integer dynamic programming.
"""
from pathlib import Path
import json
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MplPath
from matplotlib.colors import Normalize
from common import canvas, save, clean_axes, footer, INK, MUTED, TEAL, GOLD, LIGHT, GRID, HEAT

EDGES = [(0, 0, 2), (0, 1, 1), (1, 1, 3), (1, 2, 2), (2, 0, 1), (2, 2, 4)]


def walk_coefficients(max_weight=36):
    """Count all directed walks, including repeated edges, by total weight."""
    counts = [[0] * 3 for _ in range(max_weight + 1)]
    counts[0][0] = 1
    for weight in range(max_weight + 1):
        for source, target, gain in EDGES:
            if weight + gain <= max_weight:
                counts[weight + gain][target] += counts[weight][source]
    coefficients = [row[2] for row in counts]
    # Q(t) Z(t) = t^3 for the actual graph. Check every plotted coefficient.
    q = [1, 0, -1, -1, -2, 1, 1, 1, 0, -1]
    for weight in range(max_weight + 1):
        assert sum(q[k] * coefficients[weight-k]
                   for k in range(min(weight, len(q)-1) + 1)) == int(weight == 3)
    return coefficients


def arrow(ax, start, end, radius=0, color=TEAL, scale=14, width=1.55):
    ax.add_patch(FancyArrowPatch(start, end, connectionstyle=f"arc3,rad={radius}",
                                arrowstyle="-|>", mutation_scale=scale,
                                linewidth=width, color=color, zorder=2))


def graph_figure():
    fig = canvas("Weighted transfer graph", "Edge weights measure filtration gain. Every edge has multiplicity one.", height=4.0)
    ax = fig.add_axes([.03, .10, .94, .70])
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 2.65)
    ax.set_aspect("equal")
    ax.axis("off")
    positions = {0: (.85, .70), 1: (3.0, 1.43), 2: (5.15, .70)}
    for source, target, gain in EDGES:
        x, y = positions[source]
        if source == target:
            loop = MplPath([(x-.15, y+.18), (x-.70, y+1.0),
                            (x+.70, y+1.0), (x+.15, y+.18)],
                           [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4])
            ax.add_patch(FancyArrowPatch(path=loop, arrowstyle="-|>", mutation_scale=14,
                                        linewidth=1.55, color=TEAL, zorder=2))
            ax.text(x, y+.88, f"w = {gain}", ha="center", va="center", fontsize=11,
                    color=GOLD, bbox=dict(facecolor="white", edgecolor="none", pad=1.5), zorder=5)
            continue
        target_xy = np.array(positions[target])
        start_xy = np.array((x, y))
        direction = (target_xy-start_xy) / np.linalg.norm(target_xy-start_xy)
        radius = -.22 if (source, target) == (2, 0) else -.06
        arrow(ax, start_xy+.23*direction, target_xy-.23*direction, radius)
        if (source, target) == (2, 0):
            lx, ly = 3.0, .15
        else:
            lx, ly = (start_xy + target_xy)/2
            ly += .17
        ax.text(lx, ly, f"w = {gain}", ha="center", va="center", fontsize=11,
                color=GOLD, bbox=dict(facecolor="white", edgecolor="none", pad=1.5), zorder=5)
    for node, (x, y) in positions.items():
        ax.add_patch(Circle((x, y), .22, facecolor=LIGHT, edgecolor=TEAL, linewidth=1.6, zorder=3))
        ax.text(x, y, str(node), ha="center", va="center", weight="bold", fontsize=12.5, zorder=4)
    footer(fig, "The weighted walk series below starts at packet 0 and ends at packet 2.")
    save(fig, "04_weighted_transfer_graph")


def counts_figure(coefficients):
    fig = canvas("Weighted walk counts", "All walks from packet 0 to packet 2, including loops and repeated visits.", height=3.9)
    ax = fig.add_axes([.12, .22, .84, .57])
    markers, stems, baseline = ax.stem(range(len(coefficients)), coefficients, basefmt=" ")
    markers.set_color(TEAL)
    markers.set_markersize(3.5)
    stems.set_color(TEAL)
    stems.set_linewidth(1.05)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("Total walk weight")
    ax.set_ylabel("Number of walks")
    ax.set_xlim(-.6, 36.6)
    ax.set_xticks(range(0, 37, 4))
    ax.set_yticks([0, 1, 10, 100, 1000, 10000, 100000, 1000000])
    ax.set_yticklabels(["0", "1", "10", r"$10^2$", r"$10^3$", r"$10^4$", r"$10^5$", r"$10^6$"])
    ax.set_ylim(-.2, max(coefficients)*1.8)
    clean_axes(ax)
    footer(fig, "Exact integer counts through weight 36. The vertical scale is logarithmic above 1.")
    save(fig, "05_path_zeta_coefficients")


def inverse_figure():
    precision = np.arange(1, 13)
    retained = precision - 1
    fig = canvas("Finite filtration cutoff", "At precision L, only transfer words with total weight less than L contribute.", height=3.9)
    ax = fig.add_axes([.12, .22, .83, .57])
    ax.step(precision, retained, where="mid", color=TEAL, linewidth=1.8)
    ax.scatter(precision, retained, color=TEAL, s=28, zorder=3)
    ax.set_xticks(precision)
    ax.set_yticks(range(0, 12, 2))
    ax.set_xlim(.6, 12.4)
    ax.set_ylim(-.5, 11.6)
    ax.set_xlabel("Precision L")
    ax.set_ylabel("Largest allowed integer weight")
    clean_axes(ax)
    footer(fig, "This is the support cutoff L − 1. It does not count the number of surviving walks.")
    save(fig, "06_filtered_inverse_depth")


def defect_data():
    values = np.array([.4, .8, 1.3])
    coarsen = np.zeros((3, 9))
    for i in range(3):
        coarsen[i, 3*i:3*i+3] = 1/3
    coarse = np.diag(values)
    fine = np.diag(np.repeat(values, 3))
    fine[0, 0] += .09
    one_step = coarsen @ fine - coarse @ coarsen
    delta = float(np.linalg.norm(one_step, 2))
    nc, nf = float(np.linalg.norm(coarse, 2)), float(np.linalg.norm(fine, 2))
    actual, bound, residual = [], [], []
    for n in range(1, 13):
        difference = coarsen @ np.linalg.matrix_power(fine, n) - np.linalg.matrix_power(coarse, n) @ coarsen
        expanded = sum(np.linalg.matrix_power(coarse, n-1-k) @ one_step @ np.linalg.matrix_power(fine, k) for k in range(n))
        a = float(np.linalg.norm(difference, 2))
        b = delta * sum(nc**(n-1-k)*nf**k for k in range(n))
        actual.append(a)
        bound.append(b)
        residual.append(float(np.linalg.norm(difference-expanded, 2)))
        assert a <= b + 1e-12
        assert residual[-1] < 1e-12
    return {"actual": actual, "bound": bound, "one_step_norm": delta,
            "telescoping_residuals": residual, "coarse_values": values.tolist(),
            "children_per_coordinate": 3, "fine_00_perturbation": .09}


def defect_figure(data):
    fig = canvas("Propagation of a refinement defect", "The exact telescoping identity gives a norm bound at each operator power.", height=3.9)
    ax = fig.add_axes([.12, .22, .83, .50])
    powers = range(1, 13)
    ax.plot(powers, data["actual"], marker="o", color=TEAL, markersize=4.5,
            linewidth=1.8, label="Measured defect")
    ax.plot(powers, data["bound"], marker="s", color=GOLD, markersize=4,
            linewidth=1.8, label="Telescoping bound")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, frameon=False,
              borderaxespad=0, columnspacing=2, handlelength=2)
    ax.set_xticks(powers)
    ax.set_xlim(.6, 12.4)
    ax.set_yscale("log")
    ax.set_ylim(min(data["actual"])*.7, max(data["bound"])*1.7)
    ax.set_xlabel("Operator power n")
    ax.set_ylabel("Spectral norm")
    clean_axes(ax)
    footer(fig, "Numerical model: three coarse coordinates, three children each, and a 0.09 perturbation.\nThe vertical axis is logarithmic so both the defect and its bound remain visible.")
    save(fig, "09_refinement_defect_bound")


def orbit_data():
    out = {}
    for order in (2, 4, 8, 16):
        omega = np.exp(2j*np.pi/order)
        gamma_input = np.array([.72*omega**k for k in range(order)])
        impedance = (1+gamma_input)/(1-gamma_input)
        recovered = (impedance-1)/(impedance+1)
        assert np.max(np.abs(recovered-gamma_input)) < 1e-14
        out[order] = recovered
    for order in (4, 8, 16):
        assert np.max(np.abs(out[order][::2]-out[order//2])) < 1e-14
    return out


def orbit_figure(data):
    fig = canvas("Nested polyphase samples", "Reflection coordinates retain their geometry at every dyadic refinement.", height=5.8)
    theta = np.linspace(0, 2*np.pi, 500)
    for index, order in enumerate((2, 4, 8, 16)):
        left = .16 if index % 2 == 0 else .58
        bottom = .55 if index < 2 else .165
        ax = fig.add_axes([left, bottom, .26, .26*6.7/5.8])
        ax.plot(np.cos(theta), np.sin(theta), color=TEAL, linewidth=1.2)
        ax.plot(.72*np.cos(theta), .72*np.sin(theta), color=GRID, linestyle="--", linewidth=.8)
        ax.axhline(0, color=GRID, linewidth=.7)
        ax.axvline(0, color=GRID, linewidth=.7)
        gamma = data[order]
        colors = [TEAL if order == 2 or k % 2 == 0 else GOLD for k in range(order)]
        ax.scatter(gamma.real, gamma.imag, s=28, c=colors, edgecolors="white", linewidth=.65, zorder=3)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.set_aspect("equal")
        ax.set_title(f"N = {order}", fontsize=11.5, color=INK, pad=5)
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
        ax.tick_params(labelsize=10, length=2)
        for spine in ax.spines.values():
            spine.set_visible(False)
        if index >= 2:
            ax.set_xlabel(r"$\mathrm{Re}\,\Gamma$", labelpad=1)
        if index % 2 == 0:
            ax.set_ylabel(r"$\mathrm{Im}\,\Gamma$", labelpad=1)
    footer(fig, "Every sample has |Γ| = 0.72. Gold marks points added at N = 4, 8, or 16.")
    save(fig, "11_smith_polyphase_orbit")


def smith_weight_figure():
    grid = np.linspace(-.98, .98, 300)
    x, y = np.meshgrid(grid, grid)
    gamma = x+1j*y
    mask = np.abs(gamma) < .985
    values = np.full_like(x, np.nan)
    values[mask] = np.log10(1/np.abs(1-gamma[mask])**2 + 1/np.abs(1+gamma[mask])**2)
    assert np.allclose(values, values[:, ::-1], equal_nan=True)
    assert np.allclose(values, values[::-1, :], equal_nan=True)
    fig = canvas("Symmetric Smith refinement weight", "The weight increases near the two boundary points Γ = −1 and Γ = 1.", height=4.8)
    ax = fig.add_axes([.17, .205, .42, .42*6.7/4.8])
    image = ax.imshow(values, extent=[-.98, .98, -.98, .98], origin="lower", aspect="equal",
                      cmap=HEAT, norm=Normalize(vmin=float(np.nanmin(values)), vmax=float(np.nanmax(values))))
    ax.add_patch(Circle((0, 0), .985, fill=False, color=TEAL, linewidth=1.05))
    ax.set_xticks([-1, -.5, 0, .5, 1])
    ax.set_yticks([-1, -.5, 0, .5, 1])
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel(r"$\mathrm{Re}\,\Gamma$")
    ax.set_ylabel(r"$\mathrm{Im}\,\Gamma$")
    ax.tick_params(labelsize=10, length=2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cax = fig.add_axes([.64, .26, .026, .43])
    colorbar = fig.colorbar(image, cax=cax)
    colorbar.set_ticks([.5, 1, 2, 3])
    colorbar.set_label(r"$\log_{10} w(\Gamma)$", labelpad=8, fontsize=11)
    colorbar.ax.tick_params(labelsize=10)
    colorbar.outline.set_visible(False)
    footer(fig, r"$w(\Gamma)=|1-\Gamma|^{-2}+|1+\Gamma|^{-2}$"+"\nThe 300 × 300 grid is shown only where |Γ| < 0.985.")
    save(fig, "12_smith_adaptive_weight")
    return {"grid_size": [300, 300], "grid_limits": [-.98, .98], "mask_radius": .985,
            "minimum_log10_weight": float(np.nanmin(values)), "maximum_log10_weight": float(np.nanmax(values)),
            "sampled_cells": int(mask.sum()), "horizontal_and_vertical_symmetry": True}


def dependency_figure():
    fig = canvas("Distinct proof branches", "Each row identifies its own inputs and the conclusions they support.", height=6.6)
    ax = fig.add_axes([.025, .085, .95, .765])
    ax.set_xlim(0, 6.36)
    ax.set_ylim(0, 8.25)
    ax.axis("off")
    rows = [
        ("Complete packet axioms", "Coordinate coherence", "Naturality and\nrefined transfer blocks"),
        ("Residue selectors\nand finite Fourier table", "Finite Fourier formulas", "Spectral residue\nprojectors"),
        ("Residue selectors\nand coprime moduli", "Dyadic and odd CRT", "Concrete\nrefinement families"),
        ("Quotient, filtration\nand weight certificates", "Pruned finite inverse", "Precision cutoff"),
        ("Finite graph with\npositive edge weights", "Walk enumeration\nand first-edge recurrence", "Determinant rationality\nand recurrence"),
        ("Evaluated Bézout data\nand lattice action", "Integral separation", "Upward closure\nand precision delay"),
        ("Supplied Smith data\nand coordinate fibres", "Finite Smith product", "Solvability\nand fibre cardinality"),
        ("A typed one-step defect", "Telescoping powers", "Polynomial actions\nand resolvents"),
    ]
    widths = [1.98, 1.86, 1.88]
    lefts = [.0, 2.22, 4.34]
    for index, row in enumerate(rows):
        centre_y = 7.70-index*1.0
        for col, text in enumerate(row):
            box = FancyBboxPatch((lefts[col], centre_y-.36), widths[col], .72,
                                 boxstyle="round,pad=.02,rounding_size=.08",
                                 facecolor=LIGHT if col != 1 else "white", edgecolor=GRID if col != 1 else TEAL,
                                 linewidth=.9)
            ax.add_patch(box)
            ax.text(lefts[col]+widths[col]/2, centre_y, text, ha="center", va="center",
                    fontsize=10.5, linespacing=1.22, color=INK)
        for col in (0, 1):
            arrow(ax, (lefts[col]+widths[col]+.035, centre_y), (lefts[col+1]-.035, centre_y), scale=11, width=1.25)
    footer(fig, "The walk series is independent of operator inversion. General Smith and Bézout constructions\nremain upstream inputs to their certificate branches.")
    save(fig, "13_theorem_dependency")


def generate():
    coefficients = walk_coefficients()
    defect = defect_data()
    orbit = orbit_data()
    graph_figure()
    counts_figure(coefficients)
    inverse_figure()
    defect_figure(defect)
    orbit_figure(orbit)
    smith = smith_weight_figure()
    dependency_figure()
    validation = {
        "source": "canonical_v1.2.1/code/python/seed_refinement/visuals.py",
        "edge_source_target_weight": EDGES,
        "walk_scope": "All directed walks from vertex 0 to vertex 2, not simple paths",
        "exact_walk_counts_0_to_36": coefficients,
        "exact_QZ_equals_t_cubed_checked_through_weight": 36,
        "cutoff_depths": list(range(1, 13)),
        "maximum_retained_integer_weight": list(range(12)),
        "defect_model": defect,
        "smith_orders": [2, 4, 8, 16],
        "smith_sample_radius": .72,
        "smith_impedance_roundtrip_and_nested_samples_tolerance": 1e-14,
        "smith_weight_field": smith,
        "dependency_scope": "Distinct branches described by the current traditional paper proof order"
    }
    (Path(__file__).parent / "graph_visuals_validation.json").write_text(json.dumps(validation, indent=2)+"\n")
    return validation

if __name__ == "__main__":
    generate()

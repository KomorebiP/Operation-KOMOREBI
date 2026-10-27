"""Presentation repairs of four inherited Paper VII figures.

The quantum models, charge transitions, sphere samples, and boundary labels
come from the retained upstream generators. This script changes typesetting
and routing, without adding a mathematical assertion. PDF page sizes equal
the retrieved originals, so manuscript image aspect ratios are unchanged.
Run from any directory; --output-directory permits an isolated replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 10})
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import numpy as np

TRADITIONAL = Path(__file__).resolve().parents[1]
PAGE_SIZES = {
    "core/02_bell_seed_probabilities.pdf": (463.89813232421875, 301.26776123046875),
    "strengthened/03_symmetry_selection.pdf": (460.79998779296875, 219.5279998779297),
    "strengthened/06_kato_transport.pdf": (311.8200988769531, 312.12030029296875),
    "strengthened/16_continuum_boundary.pdf": (547.255126953125, 302.68798828125),
}


def figure(name: str) -> plt.Figure:
    w, h = PAGE_SIZES[name]
    return plt.figure(figsize=(w / 72, h / 72))


def save(fig: plt.Figure, name: str, out: Path) -> None:
    target = out / name
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def bell(out: Path) -> dict:
    name = "core/02_bell_seed_probabilities.pdf"
    hadamard = np.array([[1, 1], [1, -1]], dtype=float) / np.sqrt(2)
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=float)
    state = cnot @ np.kron(hadamard, np.eye(2)) @ np.array([1, 0, 0, 0])
    probability = np.abs(state) ** 2
    fig = figure(name)
    ax = fig.add_axes([0.115, 0.15, 0.86, 0.73])
    ax.bar(["00", "01", "10", "11"], probability)
    ax.set_ylim(0, 0.6)
    ax.set_ylabel("probability")
    ax.set_title(r"Bell state generated from the seed $|00\rangle$", pad=10)
    save(fig, name, out)
    return {"probabilities": probability.tolist(), "sum": float(probability.sum()),
            "scope": "Same two-qubit Bell circuit and four basis probabilities; title ket typesetting only."}


def symmetry(out: Path) -> dict:
    name = "strengthened/03_symmetry_selection.pdf"
    fig = figure(name)
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.90])
    ax.set_xlim(-0.45, 3.45)
    ax.set_ylim(-0.10, 1.90)
    ax.axis("off")
    radius = 0.17
    y = 1.16
    for j in range(4):
        ax.add_patch(Circle((j, y), radius, fill=False, linewidth=1.1))
        ax.text(j, y, rf"$P_{j}$", ha="center", va="center")
        ax.text(j, 1.66, f"charge {j}", ha="center", va="center")
    for j in range(3):
        ax.add_patch(FancyArrowPatch((j + radius + 0.02, y),
                                    (j + 1 - radius - 0.02, y),
                                    arrowstyle="->", mutation_scale=12, linewidth=1.1))
        ax.text(j + 0.5, y + 0.24, r"$A_{+1}$", ha="center", va="center", fontsize=9)
    # The wrap arrow ends on P_0 and starts on P_3, rather than in blank space.
    ax.add_patch(FancyArrowPatch((3, y - radius - 0.02), (0, y - radius - 0.02),
                                connectionstyle="arc3,rad=-0.30", arrowstyle="->",
                                mutation_scale=12, linewidth=1.1))
    ax.text(1.5, 0.59, r"$A_{+1}$", ha="center", va="center", fontsize=9)
    ax.text(1.5, 0.13, r"$S A_q S^*=\omega^q A_q$ forces $A_q P_j\subseteq P_{j+q}\mathcal{H}$",
            ha="center", va="center", fontsize=9)
    save(fig, name, out)
    return {"charge_modulus": 4, "transitions": [[j, (j + 1) % 4] for j in range(4)],
            "scope": "Same four cyclic charge-one transfers and same selection-rule formula; routed arrows now terminate on packets."}


def kato(out: Path) -> dict:
    name = "strengthened/06_kato_transport.pdf"
    theta = np.linspace(0.2, 1.1, 150)
    phi = 2.2 * theta
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 25)
    sx = np.outer(np.cos(u), np.sin(v))
    sy = np.outer(np.sin(u), np.sin(v))
    sz = np.outer(np.ones_like(u), np.cos(v))
    fig = figure(name)
    ax = fig.add_axes([0.04, 0.12, 0.82, 0.78], projection="3d")
    ax.plot_wireframe(sx, sy, sz, rstride=4, cstride=4, linewidth=0.25, alpha=0.25)
    ax.plot(x, y, z, linewidth=1.8)
    ax.scatter([x[0], x[-1]], [y[0], y[-1]], [z[0], z[-1]], s=25)
    ax.set_box_aspect((1, 1, 1))
    for dimension in ("x", "y", "z"):
        getattr(ax, f"set_{dimension}lim")(-1.05, 1.05)
        getattr(ax, f"set_{dimension}ticks")([-1, 0, 1])
        getattr(ax, f"set_{dimension}label")(rf"$n_{dimension}$", labelpad=0, fontsize=9)
    ax.tick_params(labelsize=8, pad=1)
    ax.view_init(elev=30, azim=-60)
    fig.text(0.5, 0.97, "A moving rank one packet\non the Bloch sphere", ha="center", va="top", fontsize=10)
    save(fig, name, out)
    coordinates = np.stack([x, y, z], axis=1)
    return {"theta_range": [0.2, 1.1], "phi_multiplier": 2.2, "path_samples": 150,
            "sphere_mesh_shape": [50, 25], "coordinates_sha256": hashlib.sha256(coordinates.tobytes()).hexdigest(),
            "maximum_unit_sphere_residual": float(np.max(np.abs((coordinates ** 2).sum(axis=1) - 1))),
            "real_three_dimensional_axes": True,
            "scope": "Identical theta/phi path and wireframe samples; fewer ticks, equal axis aspect, and contained labels. Retains genuine 3D axes and original viewing direction."}


def boundary(out: Path) -> dict:
    name = "strengthened/16_continuum_boundary.pdf"
    labels = ["finite packet\nidentities", "compatible\nrefinement tower",
              "self adjoint\ncontinuum limit", "reflection positive\nEuclidean limit",
              "local Lorentzian\nfield theory", "Einstein infrared\ncriterion",
              "positive massless\nspin two sector"]
    fig = figure(name)
    ax = fig.add_axes([0.025, 0.025, 0.95, 0.95])
    ax.set_xlim(0, 8.65)
    ax.set_ylim(0, 7.8)
    ax.axis("off")
    width, height, dx, dy = 1.60, 0.70, 1.05, 0.99
    for i, label in enumerate(labels):
        x, y = 0.35 + i * dx, 0.25 + i * dy
        ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.025",
                                   fill=False, linewidth=1.0))
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=8.0)
        if i < len(labels) - 1:
            ax.add_patch(FancyArrowPatch((x + width / 2, y + height + 0.035),
                                        (x + dx + width / 2, y + dy - 0.035),
                                        arrowstyle="->", mutation_scale=10, linewidth=0.9))
    ax.text(4.325, 7.47, "Every step requires a separate theorem", ha="center", va="center", fontsize=10)
    save(fig, name, out)
    return {"labels_in_order": labels, "transitions": [[i, i + 1] for i in range(6)],
            "scope": "Same seven conditional stages and same proof-boundary warning; separated stairs, forward arrows, and an unclipped final box. No convergence or reconstruction claim is promoted."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=TRADITIONAL / "assets")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    out = args.output_directory.resolve()
    models = {"core/02_bell_seed_probabilities.pdf": bell(out),
              "strengthened/03_symmetry_selection.pdf": symmetry(out),
              "strengthened/06_kato_transport.pdf": kato(out),
              "strengthened/16_continuum_boundary.pdf": boundary(out)}
    report = {"status": "PASS", "matplotlib": matplotlib.__version__, "numpy": np.__version__,
              "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "models": models,
              "outputs": [{"path": p, "sha256": hashlib.sha256((out / p).read_bytes()).hexdigest(),
                           "page_size_pt": list(PAGE_SIZES[p])} for p in models]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "figures": len(models)}))


if __name__ == "__main__":
    main()

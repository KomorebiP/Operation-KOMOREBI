from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save(fig: plt.Figure, output_dir: Path, name: str, dpi: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / name, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def saturation_family(output_dir: Path, dpi: int) -> None:
    fig, axes = plt.subplots(4, 4, figsize=(16, 14))
    for a, ax in zip(range(1, 17), axes.flat):
        nu = np.array([0, a, 2 * a, 3 * a])
        depth = np.arange(0, 3 * a + 8)
        semantic = np.array([np.maximum(r - nu, 0).sum() for r in depth])
        defect = np.array([np.minimum(r, nu).sum() for r in depth])
        raw = len(nu) * depth
        ax.step(depth, raw, where="post", label="rho*r")
        ax.step(depth, semantic, where="post", label="S(r)")
        ax.step(depth, defect, where="post", label="D(r)")
        ax.set_title(f"nu=(0,{a},{2*a},{3*a})", fontsize=9)
        ax.set_xlabel("r", fontsize=8)
        ax.set_ylabel("exponent", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Prime-power saturation family grid", fontsize=16)
    fig.tight_layout()
    save(fig, output_dir, "figure_01_prime_power_saturation_family_grid.png", dpi)


def visibility_landscape(output_dir: Path, dpi: int) -> None:
    a_values = np.arange(1, 13)
    r_values = np.arange(0, 49)
    visibility = np.array([
        [sum(max(int(r) - v, 0) for v in (0, int(a), 2 * int(a), 3 * int(a))) for r in r_values]
        for a in a_values
    ])
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    image = ax.imshow(visibility, aspect="auto", origin="lower")
    ax.set_xticks(np.arange(0, len(r_values), 3), r_values[::3])
    ax.set_yticks(np.arange(len(a_values)), a_values)
    ax.set_xlabel("prime-power depth r")
    ax.set_ylabel("profile spacing a")
    ax.set_title("Prime-power visibility landscape")
    fig.colorbar(image, ax=ax, label="semantic image exponent")
    fig.tight_layout()
    save(fig, output_dir, "figure_02_prime_power_visibility_landscape.png", dpi)


def local_channel_family(output_dir: Path, dpi: int) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    degree = np.arange(0, 81)
    valuation = np.arange(0, 6)
    for prime, ax in zip((2, 3, 5, 7), axes.flat):
        compression = np.array([
            [(d + 1) / (math.floor(d / (prime ** t)) + 1) for d in degree]
            for t in valuation
        ])
        image = ax.imshow(compression, aspect="auto", origin="lower")
        ax.set_xticks(np.arange(0, len(degree), 10), degree[::10])
        ax.set_yticks(np.arange(len(valuation)), valuation)
        ax.set_xlabel("d")
        ax.set_ylabel("t = v_p(M)")
        ax.set_title(f"p={prime}")
        fig.colorbar(image, ax=ax)
    fig.suptitle("Local-channel compression factor family", fontsize=16)
    fig.tight_layout()
    save(fig, output_dir, "figure_03_local_channel_compression_family_grid.png", dpi)


def fuss_compression(output_dir: Path, dpi: int) -> None:
    q_values = np.arange(2, 21)
    n_values = np.arange(1, 25)
    compression = np.array([[math.gcd(int(n), int(q - 1)) for n in n_values] for q in q_values])
    fig, ax = plt.subplots(figsize=(13.2, 8.0))
    image = ax.imshow(compression, aspect="auto", origin="lower")
    ax.set_xticks(np.arange(len(n_values)), n_values)
    ax.set_yticks(np.arange(len(q_values)), q_values)
    ax.set_xlabel("packet width N")
    ax.set_ylabel("tree arity q")
    ax.set_title("Fuss-Catalan compression phase: gcd(N,q-1)")
    for i, q in enumerate(q_values):
        for j, n in enumerate(n_values):
            value = int(compression[i, j])
            if value > 1:
                ax.text(j, i, str(value), ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax, label="compression factor")
    fig.tight_layout()
    save(fig, output_dir, "figure_04_fuss_catalan_compression_phase.png", dpi)


def active_address_family(output_dir: Path, dpi: int) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    n_values = np.arange(1, 25)
    j_values = np.arange(0, 24)
    for q, ax in zip((5, 7, 13, 17), axes.flat):
        support = np.zeros((len(n_values), len(j_values)))
        for row, n in enumerate(n_values):
            g = math.gcd(int(n), q - 1)
            for j in range(int(n)):
                if j % g == 1 % g:
                    support[row, j] = 1
        image = ax.imshow(support, aspect="auto", origin="lower", vmin=0, vmax=1)
        ax.set_xticks(np.arange(0, len(j_values), 3), j_values[::3])
        ax.set_yticks(np.arange(0, len(n_values), 4), n_values[::4])
        ax.set_xlabel("address j")
        ax.set_ylabel("packet width N")
        ax.set_title(f"q={q}")
        fig.colorbar(image, ax=ax)
    fig.suptitle("Fuss-Catalan active-address support family", fontsize=16)
    fig.tight_layout()
    save(fig, output_dir, "figure_05_fuss_active_address_family_grid.png", dpi)


def singularity_orbit(output_dir: Path, dpi: int) -> None:
    q_values = np.arange(2, 25)
    n_values = np.arange(1, 25)
    orbit = np.array([[(q - 1) / math.gcd(int(n), int(q - 1)) for n in n_values] for q in q_values])
    fig, ax = plt.subplots(figsize=(13, 8))
    image = ax.imshow(orbit, aspect="auto", origin="lower")
    ax.set_xticks(np.arange(len(n_values)), n_values)
    ax.set_yticks(np.arange(len(q_values)), q_values)
    ax.set_xlabel("packet width N")
    ax.set_ylabel("tree arity q")
    ax.set_title("Dominant singularity-orbit size after packetization")
    for i, q in enumerate(q_values):
        for j, n in enumerate(n_values):
            value = int(orbit[i, j])
            if value <= 6:
                ax.text(j, i, str(value), ha="center", va="center", fontsize=6.8)
    fig.colorbar(image, ax=ax, label="orbit size")
    fig.tight_layout()
    save(fig, output_dir, "figure_06_singularity_orbit_size_phase.png", dpi)


def algebraic_degree(output_dir: Path, dpi: int) -> None:
    n_values = np.arange(1, 25)
    m_values = np.arange(1, 25)
    exponent = np.array([[n / math.gcd(int(n), int(m)) for n in n_values] for m in m_values])
    fig, ax = plt.subplots(figsize=(13, 8))
    image = ax.imshow(exponent, aspect="auto", origin="lower")
    ax.set_xticks(np.arange(len(n_values)), n_values)
    ax.set_yticks(np.arange(len(m_values)), m_values)
    ax.set_xlabel("packet width N")
    ax.set_ylabel("cyclic radical modulus m")
    ax.set_title("Algebraic packet-degree exponent N/gcd(N,m)")
    for i, m in enumerate(m_values):
        for j, n in enumerate(n_values):
            value = int(exponent[i, j])
            if value <= 6 or math.gcd(int(n), int(m)) > 4:
                ax.text(j, i, str(value), ha="center", va="center", fontsize=6.8)
    fig.colorbar(image, ax=ax, label="degree exponent")
    fig.tight_layout()
    save(fig, output_dir, "figure_07_algebraic_packet_degree_phase.png", dpi)


def rational_obstruction_family(output_dir: Path, dpi: int) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for prime, ax in zip((3, 5, 7, 11), axes.flat):
        modulus = prime - 1
        limit = min(2 * modulus, 24)
        a_values = np.arange(0, limit + 1)
        b_values = np.arange(0, limit + 1)
        obstruction = np.array([
            [int(a % modulus != 0) + int(b % modulus != 0) for a in a_values]
            for b in b_values
        ])
        image = ax.imshow(obstruction, aspect="equal", origin="lower", vmin=0, vmax=2)
        step = max(1, len(a_values) // 6)
        ax.set_xticks(np.arange(0, len(a_values), step), a_values[::step])
        ax.set_yticks(np.arange(0, len(b_values), step), b_values[::step])
        ax.set_xlabel("a")
        ax.set_ylabel("b")
        ax.set_title(f"p={prime}")
        fig.colorbar(image, ax=ax)
    fig.suptitle("Rational-collapse obstruction family", fontsize=16)
    fig.tight_layout()
    save(fig, output_dir, "figure_08_rational_collapse_obstruction_family_grid.png", dpi)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the eight refined exact phase figures.")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "refined")
    parser.add_argument("--dpi", type=int, default=220)
    args = parser.parse_args()
    saturation_family(args.output_dir, args.dpi)
    visibility_landscape(args.output_dir, args.dpi)
    local_channel_family(args.output_dir, args.dpi)
    fuss_compression(args.output_dir, args.dpi)
    active_address_family(args.output_dir, args.dpi)
    singularity_orbit(args.output_dir, args.dpi)
    algebraic_degree(args.output_dir, args.dpi)
    rational_obstruction_family(args.output_dir, args.dpi)


if __name__ == "__main__":
    main()

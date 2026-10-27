from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def ticks(start: int, end: int, count: int) -> tuple[np.ndarray, list[str]]:
    positions = np.linspace(0, count - 1, 11)
    labels = np.linspace(start, end, 11, dtype=int)
    return positions, [str(value) for value in labels]


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, dpi: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.png", dpi=dpi, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def generate(domain_size: int, dpi: int, output_dir: Path) -> None:
    if domain_size < 2:
        raise ValueError("domain_size must be at least 2")

    a_values = np.arange(1, domain_size + 1)
    r_values = np.arange(0, domain_size)
    a_grid = a_values[:, None]
    r_grid = r_values[None, :]
    visibility = (
        np.maximum(r_grid, 0)
        + np.maximum(r_grid - a_grid, 0)
        + np.maximum(r_grid - 2 * a_grid, 0)
        + np.maximum(r_grid - 3 * a_grid, 0)
    )

    fig, ax = plt.subplots(figsize=(12, 12))
    image = ax.imshow(visibility, aspect="auto", origin="lower")
    ax.set_xlabel("prime-power depth r")
    ax.set_ylabel("profile spacing a")
    ax.set_title(f"Prime-power visibility landscape on a {domain_size}x{domain_size} domain")
    x_pos, x_lab = ticks(0, domain_size - 1, len(r_values))
    y_pos, y_lab = ticks(1, domain_size, len(a_values))
    ax.set_xticks(x_pos, x_lab)
    ax.set_yticks(y_pos, y_lab)
    fig.colorbar(image, ax=ax, label="semantic image exponent")
    fig.tight_layout()
    save_figure(fig, output_dir, "figure_02_visibility_large_domain", dpi)

    q_values = np.arange(2, domain_size + 2)
    n_values = np.arange(1, domain_size + 1)
    q_minus_one = (q_values - 1)[:, None]
    n_grid = n_values[None, :]
    gcd_grid = np.gcd(q_minus_one, n_grid)

    fig, ax = plt.subplots(figsize=(12, 12))
    image = ax.imshow(gcd_grid, aspect="auto", origin="lower")
    ax.set_xlabel("packet width N")
    ax.set_ylabel("tree arity q")
    ax.set_title(f"Fuss-Catalan compression phase on a {domain_size}x{domain_size} domain")
    x_pos, x_lab = ticks(1, domain_size, len(n_values))
    y_pos, y_lab = ticks(2, domain_size + 1, len(q_values))
    ax.set_xticks(x_pos, x_lab)
    ax.set_yticks(y_pos, y_lab)
    fig.colorbar(image, ax=ax, label="compression factor gcd(N,q-1)")
    fig.tight_layout()
    save_figure(fig, output_dir, "figure_04_fuss_catalan_compression_large_domain", dpi)

    orbit_size = q_minus_one / gcd_grid
    fig, ax = plt.subplots(figsize=(12, 12))
    image = ax.imshow(orbit_size, aspect="auto", origin="lower")
    ax.set_xlabel("packet width N")
    ax.set_ylabel("tree arity q")
    ax.set_title(f"Dominant singularity-orbit size on a {domain_size}x{domain_size} domain")
    ax.set_xticks(x_pos, x_lab)
    ax.set_yticks(y_pos, y_lab)
    fig.colorbar(image, ax=ax, label="orbit size (q-1)/gcd(N,q-1)")
    fig.tight_layout()
    save_figure(fig, output_dir, "figure_06_singularity_orbit_large_domain", dpi)

    m_values = np.arange(1, domain_size + 1)
    m_grid = m_values[:, None]
    degree_exponent = n_grid / np.gcd(m_grid, n_grid)
    fig, ax = plt.subplots(figsize=(12, 12))
    image = ax.imshow(degree_exponent, aspect="auto", origin="lower")
    ax.set_xlabel("packet width N")
    ax.set_ylabel("cyclic radical modulus m")
    ax.set_title(f"Algebraic packet-degree phase on a {domain_size}x{domain_size} domain")
    x_pos, x_lab = ticks(1, domain_size, len(n_values))
    y_pos, y_lab = ticks(1, domain_size, len(m_values))
    ax.set_xticks(x_pos, x_lab)
    ax.set_yticks(y_pos, y_lab)
    fig.colorbar(image, ax=ax, label="degree exponent N/gcd(N,m)")
    fig.tight_layout()
    save_figure(fig, output_dir, "figure_07_algebraic_packet_degree_large_domain", dpi)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain-size", type=int, default=1000)
    parser.add_argument("--dpi", type=int, default=500)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "high_resolution",
    )
    args = parser.parse_args()
    generate(args.domain_size, args.dpi, args.output_dir)


if __name__ == "__main__":
    main()

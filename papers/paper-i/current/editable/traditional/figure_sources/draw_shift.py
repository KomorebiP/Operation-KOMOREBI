"""Exact packet support for the finite periodic shift used in Figure 7."""
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle, FancyArrowPatch
from common import canvas, footer, save, TEAL, INK, MUTED, GRID


def shift_support():
    """Recompute the original 24 coordinate, 6 residue packet model."""
    n, packets = 24, 6
    shift = np.zeros((n, n), dtype=int)
    shift[(np.arange(n) + 1) % n, np.arange(n)] = 1
    indices = [np.arange(j, n, packets) for j in range(packets)]
    support = np.array([
        [int(np.any(shift[np.ix_(out, inp)])) for inp in indices]
        for out in indices
    ])
    expected = np.zeros((packets, packets), dtype=int)
    expected[(np.arange(packets) + 1) % packets, np.arange(packets)] = 1
    assert np.array_equal(support, expected)
    assert np.all(support.sum(axis=0) == 1)
    assert np.all(support.sum(axis=1) == 1)
    return support


def draw_shift():
    support = shift_support()
    fig = canvas(
        "Periodic shift through six residue packets",
        "A finite model on 24 coordinates. Each input packet moves to its successor.",
        height=3.9,
    )
    fig.text(.285, .765, "Transfer support", ha="center", va="bottom",
             fontsize=11, weight="bold", color=INK)
    fig.text(.77, .765, "Successor cycle", ha="center", va="bottom",
             fontsize=11, weight="bold", color=INK)

    ax = fig.add_axes([.09, .205, .39, .51])
    ax.imshow(support, cmap=ListedColormap(["white", TEAL]),
              vmin=0, vmax=1, interpolation="none", aspect="equal")
    ax.set_xticks(range(6), [str(i) for i in range(6)])
    ax.set_yticks(range(6), [str(i) for i in range(6)])
    ax.set_xlabel("Input packet", fontsize=10.5, labelpad=6)
    ax.set_ylabel("Output packet", fontsize=10.5, labelpad=6)
    ax.set_xticks(np.arange(-.5, 6, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 6, 1), minor=True)
    ax.grid(which="minor", color=GRID, linewidth=.6)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(which="major", length=0, labelsize=10, pad=4)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    for i in range(6):
        for j in range(6):
            value = int(support[i, j])
            ax.text(j, i, str(value), ha="center", va="center",
                    fontsize=10, weight="bold" if value else "normal",
                    color="white" if value else MUTED)

    cycle = fig.add_axes([.575, .19, .39, .54])
    cycle.set_xlim(-1.3, 1.3)
    cycle.set_ylim(-1.16, 1.16)
    cycle.set_aspect("equal")
    cycle.axis("off")
    angles = np.pi / 2 - np.arange(6) * np.pi / 3
    points = np.column_stack([.87 * np.cos(angles), .87 * np.sin(angles)])
    radius = .145
    for j in range(6):
        start, end = points[j], points[(j + 1) % 6]
        direction = (end - start) / np.linalg.norm(end - start)
        start_edge = start + direction * (radius + .025)
        end_edge = end - direction * (radius + .025)
        cycle.add_patch(FancyArrowPatch(
            start_edge, end_edge, arrowstyle="-|>", mutation_scale=13,
            linewidth=1.7, color=TEAL, shrinkA=0, shrinkB=0,
        ))
    for j, (x, y) in enumerate(points):
        cycle.add_patch(Circle((x, y), radius, facecolor=TEAL,
                               edgecolor="white", linewidth=.8))
        cycle.text(x, y, str(j), ha="center", va="center",
                   color="white", fontsize=11.5, weight="bold")
    footer(fig, r"$S_1P_{6,j}=P_{6,j+1}S_1$, with packet indices modulo 6. A 1 marks a nonzero block.")
    save(fig, "07_shift_packet_transfer")


if __name__ == "__main__":
    draw_shift()

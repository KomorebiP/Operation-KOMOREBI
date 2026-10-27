"""Numerical illustrations with the original random seeds and partitions.

These sampled matrices illustrate packet coordinates. Their rounded displays
are not exact certificates for the symbolic results in the text.
"""
import json
import numpy as np
from matplotlib.patches import Rectangle
from common import canvas, footer, save, OUT, INK, MUTED, TEAL, GRID, HEAT

def matrix_axes(fig, grid, scientific=False):
    ax = fig.add_axes([.11, .23, .42, .61])
    ax.imshow(grid, cmap=HEAT, vmin=0, vmax=grid.max(), interpolation="none")
    ax.set_xticks(range(3), ["1", "2", "3"])
    ax.set_yticks(range(3), ["1", "2", "3"])
    ax.set_xlabel("Input packet", labelpad=8, fontsize=11)
    ax.set_ylabel("Output packet", labelpad=8, fontsize=11)
    ax.tick_params(length=0, pad=7)
    for s in ax.spines.values():
        s.set_visible(False)
    for i in range(3):
        for j in range(3):
            value = grid[i,j]
            if scientific and i != j:
                mantissa, exponent = f"{value:.1e}".split("e")
                label = rf"${mantissa}\times10^{{{int(exponent)}}}$"
                size = 10
            else:
                label = f"{value:.2f}" if scientific else f"{value:.1f}"
                size = 15
            ax.text(j, i, label, ha="center", va="center", fontsize=size,
                    color="white" if value/grid.max() > .65 else INK,
                    weight="bold" if size == 15 else "normal")
    ax.set_xticks(np.arange(-.5,3,1), minor=True)
    ax.set_yticks(np.arange(-.5,3,1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)
    return ax

def transfer():
    parts = [list(range(5)), list(range(5,11)), list(range(11,18))]
    operator = np.random.default_rng(23).normal(size=(18,18))
    grid = np.array([[np.linalg.norm(operator[np.ix_(a,b)])
                      for b in parts] for a in parts])
    fig = canvas("Transfer blocks of a sampled operator",
                 r"Each entry is $\|P_i A P_j\|_F$. Rows name outputs and columns name inputs.",
                 height=4.3)
    ax = matrix_axes(fig, grid)
    for i in range(3):
        ax.add_patch(Rectangle((i-.48,i-.48), .96,.96, fill=False,
                               edgecolor=TEAL, linewidth=1.2))
    side = fig.add_axes([.61,.27,.36,.49]); side.axis("off")
    side.text(0,1,"Reading a block", color=TEAL, weight="bold", fontsize=11)
    side.text(0,.83,"First select input packet $j$.\nApply the operator $A$.\nThen select output packet $i$.",
              fontsize=10.5, linespacing=1.6, va="top")
    side.text(0,.38,"Diagonal blocks stay in one packet.\nOther blocks transfer between packets.",
              fontsize=10.5, linespacing=1.6, va="top")
    footer(fig,"Packet dimensions: 5, 6 and 7. Values are rounded to one decimal place.")
    save(fig, "02_transfer_block_norms")
    return {"seed":23,"packet_dimensions":[5,6,7],"frobenius_norms":grid.tolist()}

def transport():
    rng = np.random.default_rng(91)
    basis = rng.normal(size=(12,12))
    while abs(np.linalg.det(basis)) < 1e-6:
        basis = rng.normal(size=(12,12))
    inverse = np.linalg.inv(basis)
    projectors = []
    for i in range(3):
        p = np.zeros((12,12)); p[4*i:4*i+4,4*i:4*i+4] = np.eye(4)
        projectors.append(basis @ p @ inverse)
    grid = np.array([[np.linalg.norm(a@b) for b in projectors] for a in projectors])
    residual = max(np.linalg.norm(q@q-q) for q in projectors)
    annihilation = max(grid[i,j] for i in range(3) for j in range(3) if i != j)
    fig = canvas("Projector products after a change of basis",
                 r"Each entry is $\|Q_i Q_j\|_F$ for transported coordinate projectors.",
                 height=4.3)
    matrix_axes(fig, grid, scientific=True)
    side = fig.add_axes([.61,.25,.36,.51]); side.axis("off")
    side.text(0,1,"The exact identities", color=TEAL, weight="bold", fontsize=11)
    side.text(0,.79,r"$Q_i=U P_i U^{-1}$", fontsize=13)
    side.text(0,.58,r"$Q_i^2=Q_i$", fontsize=13)
    side.text(0,.37,r"$Q_i Q_j=0\quad(i\ne j)$", fontsize=13)
    side.text(0,.11,"The diagonal can have large norms.\nSmall off diagonal values are roundoff.",
              fontsize=10.5, linespacing=1.5, va="top")
    footer(fig,"Three packets of dimension 4 in a space of dimension 12. This is a numerical illustration.")
    save(fig,"09_coordinate_transport")
    return {"seed":91,"packet_dimensions":[4,4,4],"product_frobenius_norms":grid.tolist(),
            "max_idempotence_residual":float(residual),
            "max_annihilation_residual":float(annihilation)}

def generate():
    data={"transfer":transfer(),"coordinate_transport":transport()}
    (OUT / "numeric_figure_data.json").write_text(json.dumps(data,indent=2)+"\n")
    return data

if __name__ == "__main__":
    generate()

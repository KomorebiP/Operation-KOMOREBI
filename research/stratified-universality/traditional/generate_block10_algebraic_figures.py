from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
import numpy as np

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

NAVY = '#17324D'
BLUE = '#3D6C8E'
TEAL = '#2F7A78'
ORANGE = '#B56A2B'
RED = '#9D4B4B'
GREEN = '#4F774F'
GRAY = '#5F6870'
PALE_BLUE = '#E7F0F6'
PALE_TEAL = '#E7F2F1'
PALE_ORANGE = '#F7EADF'
PALE_GREEN = '#EAF2EA'
PALE_RED = '#F5E6E6'
PALE_GRAY = '#F1F3F4'

plt.rcParams.update({
    'font.size': 10,
    'figure.dpi': 120,
    'savefig.dpi': 220,
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(FIG / f'{name}.png', bbox_inches='tight', dpi=220)
    plt.close(fig)


def box(ax, xy, w, h, title, body, edge=NAVY, face='white', title_size=11, body_size=8.6):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle='round,pad=0.015,rounding_size=0.025',
        linewidth=1.35, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.72, title, ha='center', va='center',
            fontsize=title_size, fontweight='bold', color=NAVY)
    ax.text(x + w / 2, y + h * 0.34, body.replace('\\n', '\n'), ha='center', va='center',
            fontsize=body_size, color=GRAY, linespacing=1.24)
    return patch


def arrow(ax, p1, p2, label='', color=BLUE, rad=0.0, dy=0.022):
    arr = FancyArrowPatch(
        p1, p2, arrowstyle='-|>', mutation_scale=13,
        linewidth=1.25, color=color,
        connectionstyle=f'arc3,rad={rad}',
    )
    ax.add_patch(arr)
    if label:
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        ax.text(mx, my + dy, label, ha='center', va='bottom', fontsize=8.2, color=color)


def algebraic_branch_atlas() -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.5, 0.95, 'Normalized selected-branch algebraic atlas', ha='center',
            fontsize=15, fontweight='bold', color=NAVY)

    box(ax, (0.035, 0.59), 0.25, 0.23, 'Semantic branch',
        r'$F(z)\in K[[z]]$\nalgebraic and selected', BLUE, PALE_BLUE)
    box(ax, (0.375, 0.59), 0.25, 0.23, 'Polynomial chart',
        r'monic minimal $P_F(z,Y)$\nfinite branch-separating jet', TEAL, PALE_TEAL)
    box(ax, (0.715, 0.59), 0.25, 0.23, 'Finite algebra chart',
        r'$K(z)[Y]/(P_F)$\ndistinguished root class', GREEN, PALE_GREEN)
    box(ax, (0.19, 0.15), 0.28, 0.23, 'Packet polynomial chart',
        r'$N$ residue equations\ncomplete packet branch selector', ORANGE, PALE_ORANGE)
    box(ax, (0.55, 0.15), 0.28, 0.23, 'Directional Ore chart',
        r'algebraic $\to$ D-finite\nbranch data may be forgotten', RED, PALE_RED)

    arrow(ax, (0.285, 0.70), (0.375, 0.70), 'minimal polynomial')
    arrow(ax, (0.625, 0.70), (0.715, 0.70), 'quotient algebra', color=TEAL)
    arrow(ax, (0.715, 0.64), (0.625, 0.64), 'first dependence', color=GREEN, dy=-0.046)
    arrow(ax, (0.16, 0.59), (0.31, 0.38), 'residue analysis', color=ORANGE, rad=0.08)
    arrow(ax, (0.47, 0.265), (0.55, 0.265), 'annihilator', color=RED)
    arrow(ax, (0.69, 0.38), (0.55, 0.59), 'branch + jet', color=RED, rad=0.08)
    arrow(ax, (0.35, 0.15), (0.17, 0.59), 'synthesis', color=ORANGE, rad=0.10)

    ax.text(0.5, 0.055,
            'A polynomial equation alone is not a normalized algebraic object: the selected branch certificate is part of the chart.',
            ha='center', fontsize=9.2, color=GRAY)
    save(fig, 'algebraic_branch_atlas')


def packet_weil_restriction() -> None:
    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.5, 0.95, 'Algebraic packet compiler as finite Weil restriction', ha='center',
            fontsize=14.6, fontweight='bold', color=NAVY)

    box(ax, (0.035, 0.57), 0.20, 0.24, 'Source equation',
        r'$P(z,Y)=0$\n$\deg_Y P=d$', BLUE, PALE_BLUE)
    box(ax, (0.285, 0.57), 0.22, 0.24, 'Address extension',
        r'$x=z^N$\n$K(x)[z]/(z^N-x)$', TEAL, PALE_TEAL)
    box(ax, (0.555, 0.57), 0.20, 0.24, 'Split geometric fiber',
        r'$N$ rotated addresses\n$d$ branches per address', GREEN, PALE_GREEN)
    box(ax, (0.805, 0.57), 0.16, 0.24, 'Packet scheme',
        r'$d^N$ branch tuples\nfinite over $K(x)$', ORANGE, PALE_ORANGE)
    arrow(ax, (0.235, 0.69), (0.285, 0.69), 'base change')
    arrow(ax, (0.505, 0.69), (0.555, 0.69), 'split')
    arrow(ax, (0.755, 0.69), (0.805, 0.69), 'Fourier / basis')

    n = 4
    centers = np.linspace(0.18, 0.82, n)
    for q, cx in enumerate(centers):
        ax.text(cx, 0.38, rf'$z_q$', ha='center', fontsize=10.5, fontweight='bold', color=NAVY)
        for k in range(3):
            cy = 0.29 - 0.065 * k
            ax.add_patch(Circle((cx, cy), 0.022, edgecolor=TEAL, facecolor=PALE_TEAL, linewidth=1.2))
            ax.text(cx, cy, str(k + 1), ha='center', va='center', fontsize=7.5, color=NAVY)
    ax.text(0.5, 0.08,
            r'After splitting, the packet system is the Cartesian product of $N$ degree-$d$ branch fibers; '
            r'the universal geometric degree is $d^N$.',
            ha='center', fontsize=9.4, color=GRAY)
    save(fig, 'algebraic_packet_weil_restriction')


def collision_defect_ledger() -> None:
    fig, ax = plt.subplots(figsize=(10.7, 5.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.5, 0.94, 'Two-stage algebraic branch-collision ledger', ha='center',
            fontsize=14.6, fontweight='bold', color=NAVY)

    box(ax, (0.045, 0.55), 0.24, 0.25, 'Raw branch tuples',
        r'$\mathcal{B}_N$\n$|\mathcal{B}_N|=d^N$', BLUE, PALE_BLUE)
    box(ax, (0.38, 0.55), 0.24, 0.25, 'Distinct packet values',
        r'$\mathcal{C}_{N,j}=\pi_j(\mathcal{B}_N)$\nprojection collisions removed', ORANGE, PALE_ORANGE)
    box(ax, (0.715, 0.55), 0.24, 0.25, 'Selected Galois orbit',
        r'$\Gamma\cdot U_j$\nminimal packet degree', GREEN, PALE_GREEN)
    arrow(ax, (0.285, 0.675), (0.38, 0.675), r'$c^{\mathrm{tuple}}_{N,j}$', color=RED)
    arrow(ax, (0.62, 0.675), (0.715, 0.675), r'$s^{\mathrm{Gal}}_{N,j}$', color=RED)

    ax.text(0.5, 0.35,
            r'$d^N-\deg_{K(x)}U_j='
            r'(d^N-|\mathcal{C}_{N,j}|)+'
            r'(|\mathcal{C}_{N,j}|-|\Gamma\cdot U_j|)$',
            ha='center', va='center', fontsize=15, fontweight='bold', color=NAVY)
    ax.text(0.5, 0.17,
            'Tuple collision is caused by the packet coordinate projection.  Stabilizer loss is caused by descent of the selected value.\n'
            'The two mechanisms are finite, exact, and must not be merged into one unexplained degree drop.',
            ha='center', va='center', fontsize=9.2, color=GRAY, linespacing=1.35)
    save(fig, 'algebraic_collision_defects')


def quadratic_phase() -> None:
    labels = [
        'Catalan parity',
        'generic radical',
        'symmetric radical: even',
        'symmetric radical: odd',
        'rational collapse',
    ]
    values = np.array([
        [2, 4, 4, 0, 0],
        [2, 4, 4, 0, 0],
        [2, 4, 2, 1, 1],
        [2, 4, 1, 1, 2],
        [1, 1, 1, 0, 0],
    ], dtype=float)
    columns = ['source d', 'bound $d^N$', 'packet degree', 'tuple loss', 'stabilizer loss']

    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    im = ax.imshow(values, aspect='auto', cmap='YlGnBu', vmin=0, vmax=4)
    ax.set_xticks(np.arange(len(columns)), labels=columns)
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    ax.set_title('Exact degree and collision phases for marked parity packets',
                 fontsize=13.4, fontweight='bold', color=NAVY, pad=12)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            v = int(values[i, j])
            ax.text(j, i, str(v), ha='center', va='center', fontsize=10,
                    color='white' if v >= 3 else 'black')
    cb = fig.colorbar(im, ax=ax, shrink=0.78)
    cb.set_label('exact integer value')
    ax.text(2.0, 5.15,
            r'Catalan attains the universal $2^2$ bound; $\sqrt{1-z^2}$ exhibits both tuple collision and selected-orbit loss.',
            ha='center', fontsize=9.2, color=GRAY)
    save(fig, 'algebraic_quadratic_phase')


if __name__ == '__main__':
    algebraic_branch_atlas()
    packet_weil_restriction()
    collision_defect_ledger()
    quadratic_phase()
    print('generated Block 10 algebraic figures')

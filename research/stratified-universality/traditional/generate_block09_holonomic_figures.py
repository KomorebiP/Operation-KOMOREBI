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


def box(ax, xy, w, h, title, body, edge=NAVY, face='white', title_size=11, body_size=8.7):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle='round,pad=0.015,rounding_size=0.025',
        linewidth=1.35, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.72, title, ha='center', va='center',
            fontsize=title_size, fontweight='bold', color=NAVY)
    body = body.replace('\\n', '\n')
    ax.text(x + w / 2, y + h * 0.34, body, ha='center', va='center',
            fontsize=body_size, color=GRAY, linespacing=1.25)
    return patch


def arrow(ax, p1, p2, label='', color=BLUE, rad=0.0, dy=0.025):
    arr = FancyArrowPatch(
        p1, p2, arrowstyle='-|>', mutation_scale=13,
        linewidth=1.25, color=color,
        connectionstyle=f'arc3,rad={rad}',
    )
    ax.add_patch(arr)
    if label:
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        ax.text(mx, my + dy, label, ha='center', va='bottom', fontsize=8.3, color=color)


def holonomic_ore_atlas() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 6.0))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.5, 0.95, 'Normalized ordinary-point holonomic atlas', ha='center',
            va='center', fontsize=15, fontweight='bold', color=NAVY)

    box(ax, (0.035, 0.59), 0.25, 0.23,
        'Semantic germ', r'$F(z)=\sum a_nz^n$\nD-finite at an ordinary point',
        edge=BLUE, face=PALE_BLUE)
    box(ax, (0.375, 0.59), 0.25, 0.23,
        'Differential chart', r'monic minimal $L_F$\nordinary jet $J_0(F)$',
        edge=TEAL, face=PALE_TEAL)
    box(ax, (0.715, 0.59), 0.25, 0.23,
        'Derivative module', r'$\operatorname{span}_{K(z)}\{D^jF\}$\ncyclic vector $F$',
        edge=GREEN, face=PALE_GREEN)
    box(ax, (0.20, 0.16), 0.27, 0.23,
        'Tail recurrence chart', r'monic minimal $R_a$\ncutoff $N_a$ + finite prefix',
        edge=ORANGE, face=PALE_ORANGE)
    box(ax, (0.56, 0.16), 0.27, 0.23,
        'Coefficient bridge', r'Ore translation\npolynomial residual certificate',
        edge=RED, face=PALE_GRAY)

    arrow(ax, (0.285, 0.70), (0.375, 0.70), 'minimalize')
    arrow(ax, (0.625, 0.70), (0.715, 0.70), 'cyclic span', color=TEAL)
    arrow(ax, (0.715, 0.64), (0.625, 0.64), 'first dependence', color=GREEN, dy=-0.045)
    arrow(ax, (0.16, 0.59), (0.31, 0.39), 'coefficients', color=ORANGE, rad=0.08)
    arrow(ax, (0.47, 0.275), (0.56, 0.275), 'exact translation', color=RED)
    arrow(ax, (0.695, 0.39), (0.54, 0.59), 'homogenize residual', color=RED, rad=0.08)
    arrow(ax, (0.56, 0.215), (0.47, 0.215), 'recover sequence', color=ORANGE, dy=-0.045)

    ax.text(0.5, 0.055,
            'The operator alone is not a semantic object: the jet or finite prefix is part of the normalized chart.',
            ha='center', fontsize=9.2, color=GRAY)
    save(fig, 'holonomic_ore_atlas')


def holonomic_multisection_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(10.8, 5.9))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.5, 0.95, 'Holonomic multisection: construction, minimization, and defect accounting',
            ha='center', fontsize=14.2, fontweight='bold', color=NAVY)

    box(ax, (0.025, 0.56), 0.21, 0.24, 'Source object',
        r'$F(z)$ or $v_{n+1}=C(n)v_n$\nminimal source order $r$', BLUE, PALE_BLUE)
    box(ax, (0.285, 0.56), 0.22, 0.24, 'Declared constructor',
        r'root filter / $N$-step jump\nproduced operator $Q^{\rm cl}_{N,j}$', TEAL, PALE_TEAL)
    box(ax, (0.555, 0.56), 0.19, 0.24, 'Minimalize',
        r'$Q^{\rm cl}_{N,j}=A_{N,j}L_{N,j}$\nremove construction excess', ORANGE, PALE_ORANGE)
    box(ax, (0.795, 0.56), 0.18, 0.24, 'Packet chart',
        r'$M_{N,j}F$\nminimal order $r_{N,j}$', GREEN, PALE_GREEN)
    arrow(ax, (0.235, 0.68), (0.285, 0.68), 'section')
    arrow(ax, (0.505, 0.68), (0.555, 0.68), 'factor')
    arrow(ax, (0.745, 0.68), (0.795, 0.68), 'certify')

    box(ax, (0.11, 0.14), 0.26, 0.22, 'Orbit aliasing',
        r'rotated source modules overlap\nbefore the address is selected', RED, '#F5E6E6')
    box(ax, (0.63, 0.14), 0.26, 0.22, 'Address cancellation',
        r'character projection removes\npart of the ambient orbit span', RED, '#F5E6E6')
    arrow(ax, (0.395, 0.56), (0.28, 0.36), r'$A_N$', color=RED, rad=0.06)
    arrow(ax, (0.89, 0.56), (0.75, 0.36), r'$C_{N,j}$', color=RED, rad=-0.06)
    ax.text(0.5, 0.25, r'$N r-r_{N,j}=A_N+C_{N,j}$', ha='center', va='center',
            fontsize=15, fontweight='bold', color=NAVY)
    ax.text(0.5, 0.05,
            'The split is exact once the ambient orbit construction is declared; a universal closed formula is not asserted.',
            ha='center', fontsize=9.1, color=GRAY)
    save(fig, 'holonomic_multisection_pipeline')


def holonomic_order_phase() -> None:
    Ns = np.arange(1, 11)
    labels = ['lambda nonintegral', 'lambda positive integer',
              'lambda = -M, active address', 'lambda = -M, zero address']
    data = np.vstack([Ns, np.ones_like(Ns), np.ones_like(Ns), np.zeros_like(Ns)])
    fig, ax = plt.subplots(figsize=(10.3, 5.4))
    im = ax.imshow(data, aspect='auto', cmap='viridis', vmin=0, vmax=10)
    ax.set_xticks(np.arange(len(Ns)), labels=[str(n) for n in Ns])
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    ax.set_xlabel('Packet width $N$')
    ax.set_title('Exact minimal differential order in the binomial-Fuchsian packet family',
                 fontsize=13.2, fontweight='bold', color=NAVY, pad=12)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = int(data[i, j])
            text_color = 'white' if value >= 5 else 'black'
            ax.text(j, i, str(value), ha='center', va='center', fontsize=9, color=text_color)
    cb = fig.colorbar(im, ax=ax, shrink=0.78)
    cb.set_label('minimal differential order')
    ax.text(4.5, 4.10,
            'Tail recurrence order is 1 on infinite packets and 0 on finite-support packets.',
            ha='center', fontsize=9, color=GRAY)
    save(fig, 'holonomic_order_phase')


def holonomic_exponent_packet() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.5, 0.95, 'Fuchsian exponent packet after binomial multisection',
            ha='center', fontsize=14.5, fontweight='bold', color=NAVY)

    points = [(0.15, 0.53, '0', BLUE, PALE_BLUE),
              (0.50, 0.53, r'$\alpha^{-N}$', ORANGE, PALE_ORANGE),
              (0.85, 0.53, r'$\infty$', TEAL, PALE_TEAL)]
    bodies = [
        r'$E_0=\{0,1/N,\ldots,(N-1)/N\}$',
        r'$E_{\alpha^{-N}}=\{0,1,\ldots,N-2,-\lambda\}$',
        r'$E_\infty=\{(\lambda+j+r)/N\}$',
    ]
    for (x, y, label, edge, face), body in zip(points, bodies):
        ax.add_patch(Circle((x, y), 0.075, edgecolor=edge, facecolor=face, linewidth=1.7))
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold', color=NAVY)
        ax.text(x, 0.78, body, ha='center', va='center', fontsize=9.3, color=GRAY)
    arrow(ax, (0.225, 0.53), (0.425, 0.53), color=GRAY)
    arrow(ax, (0.575, 0.53), (0.775, 0.53), color=GRAY)
    ax.text(0.5, 0.33,
            'local eigenvalue ratios are torsion when lambda is rational',
            ha='center', fontsize=11.2, color=NAVY, fontweight='bold')
    ax.text(0.5, 0.20,
            'The N rotated source singularities alias to one finite packet singularity.\n'
            'Finite local eigenvalue torsion does not imply a finite global monodromy group.',
            ha='center', va='center', fontsize=9.2, color=GRAY, linespacing=1.35)
    save(fig, 'holonomic_exponent_packet')


if __name__ == '__main__':
    holonomic_ore_atlas()
    holonomic_multisection_pipeline()
    holonomic_order_phase()
    holonomic_exponent_packet()
    print('generated Block 09 holonomic figures')

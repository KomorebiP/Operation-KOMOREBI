from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

BLUE = '#2E86AB'
TEAL = '#2A9D8F'
ORANGE = '#F4A261'
MAGENTA = '#A23E8C'
RED = '#E76F51'
MUTED = '#566573'
INK = '#17202A'


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(FIG / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def box(ax, x, y, w, h, text, color, fontsize=11):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.02', facecolor=color + '22', edgecolor=color, linewidth=1.8)
    ax.add_patch(patch)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, color=INK)


def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=1.7, color=MUTED))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.03, label, ha='center', fontsize=9, color=MUTED, bbox=dict(facecolor='white', edgecolor='none', alpha=.9))


def main() -> None:
    verification = json.loads((ROOT / 'results' / 'am_spd_final_verification.json').read_text())
    final = json.loads((ROOT / 'results' / 'adaptive_multiscale_spd_final_results.json').read_text())

    names = list(verification['groups'])
    scenarios = [verification['groups'][name]['scenarios'] for name in names]
    fig, ax = plt.subplots(figsize=(11.5, 5.5))
    y = np.arange(len(names))
    ax.barh(y, scenarios, color=[BLUE, TEAL, ORANGE, MAGENTA, RED] * 3)
    ax.set_yticks(y, [name.replace('_', ' ') for name in names])
    ax.set_xscale('log')
    ax.set_xlabel('verified scenarios (log scale)')
    ax.set_title(f"Comprehensive verification: {verification['scenarios_total']:,} scenarios, zero failures", fontsize=15, weight='bold')
    for index, value in enumerate(scenarios):
        ax.text(value * 1.05, index, f'{value:,}', va='center', fontsize=9)
    ax.grid(axis='x', alpha=.18, which='both')
    fig.tight_layout()
    save(fig, '107_verification_dashboard')

    fig, ax = plt.subplots(figsize=(12.0, 6.1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(.5, .94, 'Final AM-SPD architecture', ha='center', fontsize=19, weight='bold')
    box(ax, .03, .64, .17, .16, 'moving geometry\npacket core', BLUE)
    box(ax, .25, .72, .17, .14, 'greedy SPD\nseed', ORANGE)
    box(ax, .25, .50, .17, .14, 'Lagrange tree\nseed', MAGENTA)
    box(ax, .25, .28, .17, .14, 'exact-budget\nPareto tree seed', TEAL)
    box(ax, .49, .53, .18, .18, 'backward budget\nreopening and moving\nlocal block search', BLUE)
    box(ax, .73, .64, .13, .16, 'exact finite\nportfolio choice', TEAL)
    box(ax, .89, .64, .09, .16, 'global\nrefit', ORANGE)
    box(ax, .72, .24, .20, .15, 'exact residual archive\nor complete finite closure', RED)
    arrow(ax, .20, .72, .25, .79)
    arrow(ax, .20, .72, .25, .57)
    arrow(ax, .20, .72, .25, .35)
    arrow(ax, .42, .79, .49, .65)
    arrow(ax, .42, .57, .49, .62)
    arrow(ax, .42, .35, .49, .58)
    arrow(ax, .67, .62, .73, .72)
    arrow(ax, .86, .72, .89, .72)
    arrow(ax, .935, .64, .82, .39, 'store the unresolved part')
    ax.text(.5, .08, 'Geometry selects where to look. Singular packets select what subspace to keep. The residual keeps the accounting exact.', ha='center', fontsize=11.5, color=MUTED)
    save(fig, '108_final_architecture')

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(.5, .94, 'Why the final selector cannot regress', ha='center', fontsize=18, weight='bold')
    box(ax, .04, .64, .18, .15, 'unchanged\ngreedy seed', ORANGE)
    box(ax, .04, .40, .18, .15, 'unchanged\nLagrange tree', MAGENTA)
    box(ax, .04, .16, .18, .15, 'unchanged\nexact-budget tree', TEAL)
    box(ax, .33, .29, .24, .34, 'declared finite portfolio\n\nunchanged seeds\n+ reopened fractions\n+ moving replacements', BLUE)
    box(ax, .69, .40, .25, .16, 'choose the candidate\nwith the smallest exact residual', TEAL)
    for y0 in (.715, .475, .235):
        arrow(ax, .22, y0, .33, .46)
    arrow(ax, .57, .46, .69, .48)
    ax.text(.815, .25, r'$\|R_{\mathrm{final}}\|_F \leq \min_j \|R_{\mathrm{seed},j}\|_F$', ha='center', fontsize=14, color=INK)
    ax.text(.5, .08, 'This guarantee comes from portfolio inclusion. It does not depend on the moving search finding a better replacement.', ha='center', fontsize=11, color=MUTED)
    save(fig, '109_nonregression_proof_map')

    # Final improvement chart with exact values.
    case_names = list(final['cases'])
    improvements = [100 * final['cases'][name]['improvement_fraction'] for name in case_names]
    fig, ax = plt.subplots(figsize=(9.8, 4.8))
    bars = ax.bar([name.replace('_', '\n') for name in case_names], improvements, color=[BLUE, ORANGE, TEAL, MAGENTA])
    ax.set_ylabel('exact RMSE reduction from original SPD (%)')
    ax.set_title(f"Mean reduction {100*final['mean_improvement_fraction']:.1f}%")
    ax.grid(axis='y', alpha=.18)
    for bar, value in zip(bars, improvements, strict=True):
        ax.text(bar.get_x() + bar.get_width()/2, value + 1, f'{value:.1f}%', ha='center', fontsize=10)
    fig.tight_layout()
    save(fig, '110_final_improvement_summary')


if __name__ == '__main__':
    main()

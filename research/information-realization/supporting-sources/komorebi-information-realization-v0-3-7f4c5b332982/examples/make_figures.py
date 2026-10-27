"""Regenerate separate matplotlib figures from the exact worked-example report."""
from fractions import Fraction
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def make_figures():
    data = json.loads((ROOT / 'reports' / 'worked_examples_v03.json').read_text())
    output = ROOT / 'figures'
    output.mkdir(exist_ok=True)
    figures = []
    rows = data['haar_shift']['horizons']
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot([r['horizon'] for r in rows], [r['endpoint_deficit'] for r in rows],
            marker='o', label='Predict only the endpoint')
    ax.plot([r['horizon'] for r in rows], [r['whole_trajectory_deficit'] for r in rows],
            marker='s', label='Predict the entire observed trajectory')
    ax.set(title='One system, two different information demands', xlabel='Prediction horizon',
           ylabel='Additional independent field coordinates')
    ax.set_xticks(range(9))
    ax.set_yticks((0, 1))
    ax.set_ylim(-0.1, 1.4)
    ax.grid(alpha=0.2)
    ax.legend(loc='upper right')
    fig.text(0.5, 0.02, 'Exact GF(5) Haar shift example. Changing the endpoint task is not irreversible data processing.',
             ha='center', fontsize=10)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    for extension in ('png', 'svg'):
        fig.savefig(output / f'endpoint_and_trajectory.{extension}', dpi=180, bbox_inches='tight')
    figures.append(fig)

    rows = data['restricted_partial_budget']['curves']
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot([r['symbols'] for r in rows], [100*float(Fraction(r['state_aware_success'])) for r in rows],
            marker='o', label='Encoder sees observation and task')
    ax.plot([r['symbols'] for r in rows], [100*float(Fraction(r['helper_only_success'])) for r in rows],
            marker='s', label='Encoder sees task only')
    ax.set(title='Equal exact-recovery budgets do not imply equal partial recovery',
           xlabel='Allowed supplemental message symbols', ylabel='Optimal exact-answer probability (%)')
    ax.set_xticks((1, 2, 3))
    ax.set_yticks((40, 60, 80, 100))
    ax.set_ylim(35, 105)
    ax.grid(alpha=0.2)
    ax.legend(loc='lower right')
    ax.annotate('80% versus 73⅓%', xy=(2, 76.5), xytext=(1.55, 57),
                arrowprops={'arrowstyle': '->'})
    fig.text(0.5, 0.02, 'Exact optima under the stated full-support GF(3)² prior. Lines connect discrete alphabet budgets.',
             ha='center', fontsize=10)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    for extension in ('png', 'svg'):
        fig.savefig(output / f'access_restricted_repair.{extension}', dpi=180, bbox_inches='tight')
    figures.append(fig)
    return figures


if __name__ == '__main__':
    for figure in make_figures():
        plt.close(figure)
    print('Wrote two PNG/SVG figure pairs.')

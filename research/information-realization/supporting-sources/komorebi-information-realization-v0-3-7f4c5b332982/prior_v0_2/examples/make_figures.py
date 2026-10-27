"""Optional figures from the checked worked examples. Requires matplotlib.

Run `python examples/worked_examples.py` first, then this script.
Default matplotlib colors are used. Each figure contains one chart.
"""
from fractions import Fraction
from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
ROOT = Path(__file__).resolve().parents[1]


def make_figures():
    data = json.loads((ROOT/'reports'/'worked_examples.json').read_text())
    destination = ROOT/'figures'
    destination.mkdir(exist_ok=True)
    figures = []
    # Discrete message alphabet, not a continuous physical acquisition cost.
    m = list(range(1, 26))
    given = data['dynamics']['budget_curve']
    lookup = {r['alphabet']: float(Fraction(r['success'])) for r in given}
    fig = plt.figure(figsize=(9.5, 5.3))
    ax = fig.add_subplot(111)
    ax.plot(m, [lookup.get(k, 1.0) for k in m], '.-', label='Biased three-bit state', linewidth=1.5)
    ax.plot(m, [min(k/5, 1) for k in m], '.-', label='Residue reconstruction: 5 possibilities', linewidth=1.5)
    ax.plot(m, [min(k/25, 1) for k in m], '.-', label='Signal reconstruction: 25 possibilities', linewidth=1.5)
    ax.set(xlabel='Allowed supplemental message symbols (integer alphabet size)',
           ylabel='Maximum probability of exact task recovery',
           title='Exact recovery under a limited repair budget', xlim=(0.5,25.5), ylim=(-.025,1.065))
    ax.set_xticks([1,2,3,4,5,10,15,20,25])
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(axis='y', alpha=.2)
    fig.text(.5,.01,'State-aware encoder, noiseless message, and the declared priors. Points are exact finite optima.',
             ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    for ext in ('png','svg'):
        fig.savefig(destination/f'repair_budget_curves.{ext}',dpi=180,bbox_inches='tight')
    figures.append(fig)

    rows=data['XOR_synergy']['rows']
    fig=plt.figure(figsize=(8.3,4.8));ax=fig.add_subplot(111)
    x=['No observation','A only','B only','A and B']
    y=[r['task_mutual_information_bits'] for r in rows]
    ax.bar(x,y)
    for i,v in enumerate(y):
        ax.text(i,v+.035,f'{v:g} bit'+('s' if v!=1 else ''),ha='center',fontsize=11)
    ax.set(ylabel='Mutual information with the task (bits)',ylim=(0,1.2),
           title='Two individually uninformative packets can jointly solve the task')
    fig.text(.5,.015,'Task F = A XOR B. Inputs A and B are independent fair bits.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.04,1,1))
    for ext in ('png','svg'):
        fig.savefig(destination/f'xor_joint_information.{ext}',dpi=180,bbox_inches='tight')
    figures.append(fig)

    rows=data['dynamics']['observation_rows']
    fig=plt.figure(figsize=(8.3,4.8));ax=fig.add_subplot(111)
    y=[float(Fraction(r['categorical_residual'])) for r in rows]
    ax.bar(['Observe a','Observe a, b','Observe a, b, c'],y)
    for i,(v,row) in enumerate(zip(y,rows)):
        ax.text(i,v+.016,row['categorical_residual'],ha='center',fontsize=11)
    ax.set(ylabel='Categorical residual V (unhalved Brier risk)',ylim=(0,.62),
           title='Refinement removes an exactly measured prediction residual')
    fig.text(.5,.015,'Full initial-state task under the declared biased prior. Labels are exact rational values.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    for ext in ('png','svg'):
        fig.savefig(destination/f'categorical_residual_refinement.{ext}',dpi=180,bbox_inches='tight')
    figures.append(fig)
    return figures


if __name__=='__main__':
    figures=make_figures()
    for figure in figures:
        plt.close(figure)
    print('Created three single-chart PNG/SVG figure pairs in figures/.')

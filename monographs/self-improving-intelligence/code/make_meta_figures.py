#!/usr/bin/env python3
"""Two mathematical figures from exact reference outputs. No empirical scores."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures'

def save(fig,name):
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight',pad_inches=.14)
    fig.savefig(OUT/f'{name}.png',bbox_inches='tight',pad_inches=.14,dpi=160)
    plt.close(fig)

def main():
    data=json.loads((ROOT/'validation/meta_synthesis_demonstration.json').read_text())
    names=('sum_budget','minimum_trigger','exact_sum','exact_maximum')
    labels=('Sum threshold','Minimum threshold','Sum equality','Maximum equality')
    cases={x['task']:x for x in data['new_task_cases']}
    y0=[cases[n]['parent']['counters']['semantic_node_visits'] for n in names]
    y1=[cases[n]['child']['counters']['semantic_node_visits'] for n in names]
    fig,ax=plt.subplots(figsize=(8.8,4.3))
    ax.bar([i-.18 for i in range(4)],y0,width=.36,label='Original scan')
    ax.bar([i+.18 for i in range(4)],y1,width=.36,label='Learned quotient')
    ax.set_xticks(range(4),labels);ax.set_ylabel('Interpreter-node visits')
    ax.ticklabel_format(axis='y',style='plain');ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper left',frameon=False);ax.set_ylim(0,max(y0)*1.23)
    ax.set_title('Same candidate and counterexample trace',pad=13)
    fig.tight_layout();save(fig,'meta_acquisition_cost')
    fig,ax=plt.subplots(figsize=(8.7,3.5));ax.set(xlim=(-.2,8.6),ylim=(-.2,3.1));ax.axis('off')
    for g in range(4):
        x=.35+2.1*g
        ax.add_patch(Rectangle((x,1),1.6,1.3,fill=False,linewidth=1.2))
        ax.text(x+.8,2.58,f'Repair {g+1}',ha='center',va='center',fontsize=12)
        ax.text(x+.8,1.92,f'Cases {2*g+1}, {2*g+2}',ha='center',va='center',fontsize=11)
        ax.text(x+.8,1.4,'Weights: 1, 0',ha='center',va='center',fontsize=11)
    ax.text(4.2,.43,'Eight hidden cases  •  Four required repair classes',ha='center',fontsize=12)
    ax.text(4.2,-.06,'Total certified weight = 4. A binary tree needs at least four leaves.',ha='center',fontsize=10.5)
    fig.tight_layout();save(fig,'repair_relative_classes')
    print('Generated two analytical vector figures and two previews.')

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Generate figures only from completed audit JSON records."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
FIGURES=ROOT/'figures'
FIGURES.mkdir(exist_ok=True)
plt.rcParams['svg.fonttype']='none'
def read(name):return json.loads((ROOT/'results'/f'{name}.json').read_text())
def save(fig,name):
    fig.tight_layout()
    fig.savefig(FIGURES/(name+'.svg'),metadata={'Date':None})
    fig.savefig(FIGURES/(name+'.png'),dpi=180)
    plt.close(fig)
rows=[read(f'running-{n}') for n in (8192,16384)]
fig,ax=plt.subplots(figsize=(8,4.3))
ax.plot([r['engine']['K'] for r in rows],[100*float(r['accuracy_decision']['ratio_upper']) for r in rows],'o-',label='Directed multiplicative width')
ax.axhline(2,linestyle='--',label='Requested width: 2%')
ax.set(title='K-COS running example: refinement changes the decision',xlabel='Retained COS modes',ylabel='Probability enclosure width (%)',xticks=[8192,16384],ylim=(0,3))
ax.legend();save(fig,'running_refinement')
depths=[100,1000,5000];rows=[read(f'deep-{d}') for d in depths];tight=read('deep-5000-tight')
fig,ax=plt.subplots(figsize=(8,4.5))
ax.plot(depths,[float(r['accuracy_decision']['ratio_upper']) for r in rows],'o-',label='Fixed resolution: 128 modes, 90 interval digits')
ax.scatter([5000],[float(tight['accuracy_decision']['ratio_upper'])],marker='s',label='Adaptive run: relative request 1e-18')
ax.axhline(1e-18,linestyle='--',label='Adaptive accuracy request')
ax.set(title='Independent reference contained in every displayed interval',xlabel='Target tail depth: -log10(p)',ylabel='Upper bound on probability ratio minus one',xscale='log',yscale='log')
ax.legend(fontsize=8);save(fig,'deep_tail_contracts')
print('Generated two SVG and two PNG figures.')

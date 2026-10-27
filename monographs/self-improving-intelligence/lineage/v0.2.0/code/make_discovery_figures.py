#!/usr/bin/env python3
"""Three analytical figures for the v0.2 theory. No generated imagery or training data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
OUT.mkdir(exist_ok=True)

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.12)
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)

def box(ax,x,y,w,h,label,size=11):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.05',fill=False,linewidth=1.1))
    ax.text(x,y,label,ha='center',va='center',fontsize=size,linespacing=1.3)

def arrow(ax,a,b):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','linewidth':1.2})

fig,ax=plt.subplots(figsize=(9.2,4.7))
ax.set(xlim=(0,10.5),ylim=(0,5.3));ax.axis('off')
box(ax,5.25,4.8,6.4,.65,'Unknown case x and unknown sensor convention θ',12)
box(ax,2.5,3.45,4.0,.7,'Ordinary query: o = x ⊕ θ\nCost 1')
box(ax,2.5,1.95,4.3,1.1,'Each report leaves two possibilities\nthat require different repairs.\nRepeating the reading does not help.')
ax.text(2.5,.6,'No certain repair in any finite horizon\nusing only the ordinary query.',ha='center',va='center',fontsize=11)
box(ax,7.9,3.45,4.0,.7,'Reference measurement reports θ\nCost 2')
box(ax,7.9,2.0,4.0,.7,'Ordinary reading then reveals x\nCost 1')
box(ax,7.9,.55,4.0,.7,'Execute repair rₓ\nCost 1')
arrow(ax,(3.5,4.45),(2.5,3.85));arrow(ax,(7,4.45),(7.9,3.85))
arrow(ax,(2.5,3.05),(2.5,2.55));arrow(ax,(7.9,3.05),(7.9,2.4));arrow(ax,(7.9,1.6),(7.9,.95))
save(fig,'uncertain_sensor')

fig,ax=plt.subplots(figsize=(9.2,4.8))
ax.set(xlim=(0,12),ylim=(0,5.8));ax.axis('off')
for y,label in [(5.15,'Check immutable binary scope'),(3.7,'Propose a diagnostic tree'),(2.25,'Verify tree and both lower bounds'),(.75,'Return the optimal frontier')]:
    box(ax,3.5,y,5.6,.72,label,11)
for top,bot in [(4.75,4.1),(3.3,2.65),(1.85,1.15)]:arrow(ax,(3.5,top),(3.5,bot))
box(ax,9.6,3.0,3.5,1.1,'Run the exact parent\nwith costs retained',11)
arrow(ax,(6.35,5.15),(9.6,5.15));arrow(ax,(9.6,5.15),(9.6,3.65))
arrow(ax,(6.35,3.7),(7.75,3.35));arrow(ax,(6.35,2.25),(7.75,2.7))
ax.text(7.55,5.43,'scope fails',ha='center',fontsize=10)
ax.text(7.2,4.28,'no candidate',ha='center',fontsize=10)
ax.text(7.12,1.48,'not certified\noptimal',ha='center',va='center',fontsize=10,linespacing=1.15)
ax.text(9.6,.75,'A failed proposal is not\na proof of infeasibility.',ha='center',va='center',fontsize=11)
save(fig,'certified_compiler')

report=json.loads((ROOT/'validation'/'discovery_demonstration.json').read_text())
rows=report['comparison_rows']
fig,ax=plt.subplots(figsize=(8.5,4.6))
x=[r['n'] for r in rows]
ax.plot(x,[r['parent']['table_reads'] for r in rows],marker='o',label='Exact parent compiler')
ax.plot(x,[r['descendant']['table_reads'] for r in rows],marker='s',label='Certified shortcut compiler')
ax.set_yscale('log')
ax.set_xlabel('Number of possible immutable cases',fontsize=11)
ax.set_ylabel('Transition/report record reads',fontsize=11)
ax.set_xticks(x)
ax.grid(True,axis='y',alpha=.25)
ax.legend(loc='upper left',frameon=False)
ax.margins(x=.06,y=.12)
fig.tight_layout()
save(fig,'compiler_read_cost')
print('Generated three analytical vector figures and three PNG previews.')

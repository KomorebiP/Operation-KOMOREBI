#!/usr/bin/env python3
"""Regenerate the two v0.7 analytical figures. No empirical observations are used."""
from pathlib import Path
from fractions import Fraction as Q
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
META={'Creator':'Operation Komorebi analytical figure script', 'CreationDate':None, 'ModDate':None}

def main():
    # Integer lattice: the rule is exact. Marker shapes and fills distinguish classes.
    fig,ax=plt.subplots(figsize=(7.2,4.0),layout='constrained')
    feasible=[(d,c) for d in range(5) for c in range(7) if c>=d+2]
    failed=[(d,c) for d in range(5) for c in range(7) if c<d+2]
    ax.plot([d for d,c in failed],[c for d,c in failed],linestyle='none',marker='o',
            fillstyle='none',markersize=7,label='No common allocation')
    ax.plot([d for d,c in feasible],[c for d,c in feasible],linestyle='none',marker='s',
            markersize=6,label='Audit and all due work fit')
    ax.plot([0,4],[2,6],linestyle='--',linewidth=1.2,label=r'Boundary $c=d+2$')
    ax.set(xlabel='Protected service units due, d',ylabel='Available execution slots, c',
           xlim=(-.35,4.35),ylim=(-.5,6.55),xticks=range(5),yticks=range(7))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.20),ncol=2,fontsize=8.3,frameon=False)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'joint_service_frontier.pdf',metadata=META)
    plt.close(fig)
    # Exact rational formulas, converted to float only at the plotting boundary.
    grid=[Q(k,240) for k in range(121)]
    rich=[min(6*a,Q(3,2))-1 for a in grid]
    fig,ax=plt.subplots(figsize=(7.2,3.8),layout='constrained')
    ax.plot([float(a) for a in grid],[float(x) for x in rich],linewidth=2,
            label='Three-outcome audit')
    ax.plot([float(a) for a in grid],[-1]*len(grid),linestyle='--',linewidth=1.5,
            label='Mixture-indistinguishable audit')
    ax.axhline(0,linestyle=':',linewidth=.9,label='Weak-deterrence threshold')
    ax.set(xlabel=r'False-positive cap, $\alpha$',ylabel=r'Best common margin, $\Gamma_\alpha$',
           xlim=(0,.5),ylim=(-1.13,.7))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.20),ncol=2,fontsize=8.3,frameon=False)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'joint_enforcement_margin.pdf',metadata=META)
    plt.close(fig)
    print('Generated two exact analytical vector figures.')

if __name__=='__main__': main()

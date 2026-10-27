#!/usr/bin/env python3
"""Render one chart from independently checked bridge data (no simulated measurements)."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt


def main():
    bundle = Path(__file__).resolve().parent
    report = json.loads((bundle / 'verification.json').read_text())
    labels = np.arange(12)
    psi = np.array(report['signal'], dtype=float) / np.sqrt(48)
    decoded = np.array([0.5 if k in report['coprime_modes'] else 0.0 for k in labels])
    fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=180)
    for values, marker, label, linestyle in [
        (psi,'o',r'Signal amplitudes: $c_{12}(n)/\sqrt{48}$','-'),
        (decoded,'s',r'After inverse QFT: $1/2$ on $\{1,5,7,11\}$','--')
    ]:
        xs = np.column_stack((labels, labels, np.full(12,np.nan))).ravel()
        ys = np.column_stack((np.zeros(12), values, np.full(12,np.nan))).ravel()
        ax.plot(xs,ys,marker=marker,markevery=(1,3),markersize=6,
                linewidth=1.4,linestyle=linestyle,label=label)
    ax.set_xlim(-0.5,11.5)
    ax.set_ylim(-0.69,0.72)
    ax.set_xticks(labels)
    ax.set_yticks([-0.6,-0.3,0,0.3,0.6])
    ax.set_xlabel('Basis label: n before the transform, k after it',labelpad=9)
    ax.set_ylabel('Real probability amplitude',labelpad=9)
    ax.set_title('Arithmetic becomes interference',loc='left',fontsize=15,pad=48)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),frameon=False,fontsize=10,borderaxespad=0)
    ax.grid(axis='y',alpha=0.18)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.subplots_adjust(left=0.11,right=0.98,bottom=0.18,top=0.70)
    for extension in ('png','svg','pdf'):
        fig.savefig(bundle/f'arithmetic_interference.{extension}',dpi=400,bbox_inches='tight',pad_inches=0.12)
    return fig

if __name__=='__main__':
    main()

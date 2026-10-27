#!/usr/bin/env python3
"""Regenerate the two v6 plots from retained exact parameter certificates."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def root_count(record: dict, b: int) -> int:
    matches = [cell for cell in record['parameter_certificates']
               if (b-cell['parameter_residue']) % (1 << cell['parameter_exponent']) == 0]
    if len(matches) != 1:
        raise ValueError('The parameter certificates do not form a partition.')
    return matches[0]['root_count']


def main() -> None:
    audit = json.loads((ROOT/'results/UNIFORM_J17_V6.json').read_text())
    out = ROOT/'figures'
    out.mkdir(exist_ok=True)
    exceptional = next(row for row in audit['distances'] if row['delta'] == 11)
    bs = list(range(1,64,2))
    counts = [root_count(exceptional,b) for b in bs]
    fig, ax = plt.subplots(figsize=(10,4.1))
    ax.vlines(bs,0,counts,linewidth=2)
    ax.scatter(bs,counts,s=35,zorder=3)
    ax.set(title='The same carry boundary can have two roots—or none',
           xlabel='Odd multiplier b modulo 64',ylabel='Number of dyadic roots',
           xlim=(-1,65),ylim=(-.18,2.6))
    ax.set_xticks([1,9,17,25,33,41,49,57,63]);ax.set_yticks([0,1,2])
    ax.annotate('b ≡ 1',(1,2),xytext=(5,2.3))
    ax.annotate('b ≡ 41',(41,2),xytext=(43,2.3))
    ax.grid(axis='y',alpha=.2)
    fig.text(.5,.01,'Terminal label j = 17, wall distance δ = 11. Whole-parameter coefficient certificates.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.055,1,1))
    for ext in ('png','pdf'):fig.savefig(out/f'08_multiplier_classes_v6.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)
    ds=[row['delta'] for row in audit['distances']]
    aa=[root_count(row,1) for row in audit['distances']]
    bb=[root_count(row,3) for row in audit['distances']]
    fig,ax=plt.subplots(figsize=(10,4.6))
    ax.step(ds,aa,where='mid',marker='o',label='b ≡ 1 or 41 (mod 64)')
    ax.step(ds,bb,where='mid',linestyle='--',marker='x',label='Other odd multipliers')
    ax.set(title='The label-17 root classification retains the odd multiplier',xlabel='Distance δ past the carry wall',ylabel='Number of dyadic roots',xlim=(-.4,20.4),ylim=(-.6,18))
    ax.set_xticks(range(0,21,2));ax.set_yticks([0,1,2,4,8,12,14,15,17])
    ax.axvline(11,linestyle=':',linewidth=1)
    ax.annotate('Only δ = 11 depends on the multiplier class',xy=(11,2),xytext=(1,6),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.legend(loc='upper left');ax.grid(alpha=.2);fig.tight_layout()
    for ext in ('png','pdf'):fig.savefig(out/f'09_terminal17_stages_v6.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':main()

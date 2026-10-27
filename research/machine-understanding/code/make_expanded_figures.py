#!/usr/bin/env python3
"""Four exact-model figures for v0.5. No generated imagery or empirical data."""
from pathlib import Path
from fractions import Fraction as F
from math import cos, sin, pi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(parents=True,exist_ok=True)

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.14)
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.14)
    plt.close(fig)

def box(ax,x,y,w,h):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.025',fill=False,linewidth=1.2))

def main():
    fig,ax=plt.subplots(figsize=(8.8,4.2));ax.set(xlim=(-1.65,4.1),ylim=(-1.35,1.45));ax.axis('off')
    pts=[(1.1*cos(pi/2+2*pi*i/5),1.1*sin(pi/2+2*pi*i/5)) for i in range(5)]
    closed=pts+[pts[0]]
    ax.plot([x for x,y in closed],[y for x,y in closed],linewidth=1.4)
    ax.plot([x for x,y in pts],[y for x,y in pts],marker='o',linestyle='None',markersize=6)
    for i,((x,y),letter) in enumerate(zip(pts,'ABABC')):
        ax.text(1.26*x,1.23*y,f'{i}: {letter}',ha='center',va='center',fontsize=12)
    ax.text(2.8,.65,'Five recipients\nOne common artifact',ha='center',va='center',fontsize=13)
    ax.text(2.8,-.05,'Each edge alone: 2 symbols\nWhole cycle: 3 symbols',ha='center',va='center',fontsize=11)
    ax.text(2.8,-.75,'Case: message class\nA, B, C are code symbols',ha='center',va='center',fontsize=11)
    save(fig,'audience_cycle')

    fig,ax=plt.subplots(figsize=(9.3,3.9));ax.set(xlim=(0,10),ylim=(0,4.0));ax.axis('off')
    box(ax,5,3.28,6.1,.72)
    ax.text(5,3.28,r'Base record $(s,b)=(4,3)$; $c$ unknown',ha='center',va='center',fontsize=13)
    ax.text(5,2.55,r'Execute $J$, then read: cost = 2',ha='center',va='center',fontsize=12)
    for c,x in enumerate((.95,2.975,5,7.025,9.05)):
        y=(4+c)%5
        ax.annotate('',xy=(x,1.83),xytext=(5,2.27),arrowprops={'arrowstyle':'->','linewidth':1.1})
        box(ax,x,1.24,1.62,1.0)
        ax.text(x,1.48,f'Report {y}',ha='center',va='center',fontsize=11)
        ax.text(x,1.08,f'({y}, 3, {c})',ha='center',va='center',fontsize=12)
    ax.text(5,.29,'All leaf records describe the state after the diagnostic operation.',ha='center',fontsize=11)
    save(fig,'acquisition_branches')

    fig,ax=plt.subplots(figsize=(8.8,4.8));ns=list(range(7))
    full=[F(12**n,12**n+4) for n in ns]
    coarse=[F(14**n,3*14**n+2*3**n) for n in ns]
    ax.plot(ns,[float(v) for v in full],marker='o',label='Full report (ancillary flag may be removed)',linewidth=1.6)
    ax.plot(ns,[float(v) for v in coarse],marker='s',label='Only even parity retained',linewidth=1.6)
    ax.set(xlabel='Number of conditionally independent reports',ylabel='Posterior probability of c = 2',ylim=(0,1.04),xticks=ns)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.19),frameon=False)
    fig.subplots_adjust(bottom=.3,left=.1,right=.98,top=.94)
    save(fig,'noisy_correction')

    fig,ax=plt.subplots(figsize=(8.4,4.5));gs=[F(i,1000) for i in range(1,1001)];d=F(1,100)
    ax.plot([float(g) for g in gs],[float(min(F(1),d/g)) for g in gs],linewidth=1.7)
    ax.set_xscale('log')
    ax.set(xlabel=r'Certified lower bound on evidence probability, $\gamma$',
           ylabel='Certified upper bound on posterior TV error',ylim=(0,1.04))
    ax.text(.055,.75,r'$\delta=1/100$'+'\n'+r'$\min(1,\delta/\gamma)$',transform=ax.transAxes,fontsize=13)
    ax.spines[['top','right']].set_visible(False)
    fig.subplots_adjust(bottom=.2,left=.12,right=.98,top=.94)
    save(fig,'conditioning_bound')
    print('Generated four vector figures and four previews from the stated finite models.')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Regenerate the four v0.6 analytical vector figures, with no sampled agents."""
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT=Path(__file__).resolve().parent
plt.rcParams.update({'font.size':12, 'pdf.fonttype':42, 'ps.fonttype':42})
META={'Creator':'Machine Societies analytical figure generator', 'CreationDate':None, 'ModDate':None}

def save(fig, name):
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight',metadata=META)
    plt.close(fig)

def box(ax,x,y,w,h,text):
    ax.add_patch(Rectangle((x,y),w,h,fill=False,linewidth=1.2))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',linespacing=1.4)

def distributed():
    fig,ax=plt.subplots(figsize=(8.4,4.4))
    ax.set(xlim=(0,10),ylim=(0,5.2));ax.axis('off')
    box(ax,.2,3.1,3.5,1.35,'Replica A\n'+r'$\{(r,A)\}$'+'\nLocally exclusive')
    box(ax,6.3,3.1,3.5,1.35,'Replica B\n'+r'$\{(r,B)\}$'+'\nLocally exclusive')
    ax.annotate('',(6.15,3.8),(3.85,3.8),arrowprops={'arrowstyle':'<->','linestyle':'--'})
    ax.text(5,4.25,'Delayed exchange',ha='center',fontsize=11)
    box(ax,2.35,.55,5.3,1.55,'Both replicas after union merge\n'+r'$\{(r,A),(r,B)\}$'+'\nSame record, violated exclusivity')
    for x in [1.95,8.05]:
        ax.annotate('',(5,2.2),(x,3),arrowprops={'arrowstyle':'->','linestyle':'--'})
    ax.text(5,4.95,'One indivisible resource; two concurrent grants',ha='center',weight='bold')
    save(fig,'distributed_history')

def averaging():
    fig,ax=plt.subplots(figsize=(7.5,4.3))
    ms=list(range(1,13)); eps=[Q(1,2**(m+1)) for m in ms];T=20
    ax.plot(ms,[float(1-(1-e)**T) for e in eps],marker='o',label=r'Coupling bound $1-(1-\varepsilon_m)^{20}$')
    ax.plot(ms,[float(min(Q(1),T*e)) for e in eps],marker='s',linestyle='--',label=r'Linear bound $\min(1,20\varepsilon_m)$')
    ax.set(xlabel='Fast steps between reviews, m',ylabel='Upper bound on institutional path error',ylim=(0,1.05),xticks=ms)
    ax.legend(frameon=False,fontsize=10,loc='upper right')
    ax.set_title(r'Two-state refresh model: $\varepsilon_m=2^{-m-1}$',fontsize=13,pad=12)
    ax.grid(axis='y',alpha=.25)
    fig.tight_layout();save(fig,'review_averaging')

def cascades():
    p=Q(3,4);q=1-p;eta=q*q/(p*p+q*q);ns=list(range(1,32,2))
    action=[eta+(q-eta)*(2*p*q)**((n-1)//2) for n in ns]
    full=[sum(Q(comb(n,j))*p**j*q**(n-j) for j in range((n-1)//2+1)) for n in ns]
    fig,ax=plt.subplots(figsize=(7.5,4.3))
    ax.plot(ns,list(map(float,action)),marker='o',label='Decision-only public history')
    ax.plot(ns,list(map(float,full)),marker='s',label='Majority of independent signals')
    ax.axhline(float(eta),linestyle=':',label=r'Cascade limit $1/10$')
    ax.set(xlabel='Number of sequential participants / signals (odd n)',ylabel='Probability of a wrong decision',ylim=(0,.27),xticks=[1,5,9,13,17,21,25,29])
    ax.legend(frameon=False,fontsize=10,loc='upper right')
    ax.grid(axis='y',alpha=.25);ax.set_title('Exact binary model; private-signal tie convention',fontsize=13,pad=12)
    fig.tight_layout();save(fig,'cascade_evidence')

def roles():
    fig,ax=plt.subplots(figsize=(7.7,4.3));ax.axis('off');ax.set(xlim=(0,10),ylim=(-.5,4.8))
    ly=[3.4,2.1,.8];ry=[3.9,2.7,1.5,.3];neighbors=[[0,1],[1,2],[2,3]]
    for j,ns in enumerate(neighbors):
        for a in ns:ax.plot([2.35,7.6],[ly[j],ry[a]],linewidth=1.3)
    for j,y in enumerate(ly):
        box(ax,.2,y-.28,2.15,.56,f'Role {j+1}')
    for a,y in enumerate(ry):box(ax,7.6,y-.28,2.1,.56,f'Agent {"abcd"[a]}')
    ax.text(1.25,4.5,'Simultaneous roles',ha='center',weight='bold')
    ax.text(8.65,4.5,'Unit-capacity agents',ha='center',weight='bold')
    ax.text(5,-.3,'Every nonempty role set has at least one extra neighbor.',ha='center',fontsize=11)
    save(fig,'resilient_roles')

if __name__=='__main__':
    distributed();averaging();cascades();roles()
    print('Generated 4 vector figures from analytical constructions.')

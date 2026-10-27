#!/usr/bin/env python3
"""Analytical illustrations from declared finite objects, not empirical data.

Each illustration is a separate matplotlib figure. No image-generation model,
external images, hard-coded plot colors, or hidden data files are used.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'

def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight',pad_inches=.15)
    fig.savefig(OUT/f'{name}.png',bbox_inches='tight',pad_inches=.15,dpi=160)
    plt.close(fig)

def box(ax,x,y,w,h,text,fontsize=11):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,
         boxstyle='round,pad=0.05,rounding_size=0.08',fill=False,linewidth=1.15))
    ax.text(x,y,text,ha='center',va='center',fontsize=fontsize)

def arrow(ax,a,b):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.2})

def main():
    fig,ax=plt.subplots(figsize=(9.2,4.4));ax.set(xlim=(0,10),ylim=(0,4.7));ax.axis('off')
    ax.text(.3,4.45,'INNER PROCESS: improve a solver',fontsize=12,weight='bold',va='center')
    box(ax,1.25,3.3,2.0,1.05,'Starting\nsolver')
    box(ax,5,3.3,3.05,1.05,'Investigation and\nrepair procedure')
    box(ax,8.75,3.3,2.0,1.05,'Selected\ndescendant')
    arrow(ax,(2.35,3.3),(3.35,3.3));arrow(ax,(6.65,3.3),(7.65,3.3))
    ax.text(.3,1.95,'OUTER PROCESS: improve the investigation',fontsize=12,weight='bold',va='center')
    box(ax,2.15,.83,3.7,1.05,'Candidate change to\nthe repair procedure')
    box(ax,7.5,.83,4.2,1.05,'Same starting solvers, library,\nbudget, and protected evaluation',10.5)
    arrow(ax,(4.0,.83),(5.25,.83))
    ax.text(5,2.26,'a different object of comparison',fontsize=10,ha='center')
    save(fig,'two_loops')

    fig,ax=plt.subplots(figsize=(9.4,5.05));ax.set(xlim=(0,10),ylim=(0,5.6));ax.axis('off')
    ax.text(2.35,5.15,'Balanced question',ha='center',fontsize=13,weight='bold')
    ax.text(7.65,5.15,'Repair-aligned question',ha='center',fontsize=13,weight='bold')
    box(ax,2.35,4.3,3.65,.7,'Cases {0, 1, 2, 3}')
    box(ax,7.65,4.3,3.65,.7,'Cases {0, 1, 2, 3}')
    box(ax,1.13,2.7,1.7,.85,'{0, 1}\nrepair A')
    box(ax,3.55,2.7,1.7,.85,'{2, 3}\nunresolved')
    box(ax,6.42,2.7,2.03,.85,'{0, 1, 2}\nrepair A')
    box(ax,8.85,2.7,1.7,.85,'{3}\nrepair B')
    arrow(ax,(1.6,3.9),(1.13,3.19));arrow(ax,(3.05,3.9),(3.55,3.19))
    arrow(ax,(6.9,3.9),(6.42,3.19));arrow(ax,(8.4,3.9),(8.85,3.19))
    arrow(ax,(3.55,2.2),(3.55,1.52))
    ax.text(3.55,1.15,'Another question\nis still needed',ha='center',va='center',fontsize=11)
    ax.text(7.65,1.45,'One question suffices\nfor every case',ha='center',va='center',fontsize=11)
    ax.text(5,.25,'Goal: choose one successful repair, not recover every hidden distinction.',ha='center',fontsize=11)
    save(fig,'repair_partition')

    fig,ax=plt.subplots(figsize=(8.8,4.8))
    xs=[2,4,8,16,32]
    ax.plot(xs,xs,marker='o',label='Singleton queries + repair')
    ax.plot(xs,[n.bit_length() for n in xs],marker='s',label='Bit queries + repair')
    ax.set_xscale('log',base=2);ax.set_xticks(xs,labels=[str(n) for n in xs])
    ax.set_xlabel('Number of possible defective cells');ax.set_ylabel('Worst-case execution calls')
    ax.set_ylim(0,34);ax.grid(True,axis='y',alpha=.25)
    ax.legend(loc='upper left',bbox_to_anchor=(0,1.23),frameon=False,ncol=2)
    ax.text(.5,-.22,'Both literal trees store 2n − 1 records. Model acquisition and compilation are separate.',
            transform=ax.transAxes,ha='center',va='center',fontsize=10)
    fig.subplots_adjust(top=.8,bottom=.22)
    save(fig,'diagnostic_cost')
    print('Generated three analytical vector figures and three PNG previews.')

if __name__=='__main__':main()

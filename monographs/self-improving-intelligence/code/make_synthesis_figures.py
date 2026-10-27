#!/usr/bin/env python3
"""Three mathematical figures, using exact-model outputs rather than image generation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'

def save(fig,name):
    OUT.mkdir(exist_ok=True,parents=True)
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.15)
    fig.savefig(OUT/(name+'.png'),dpi=165,bbox_inches='tight',pad_inches=.15)
    plt.close(fig)

def main():
    fig=plt.figure(figsize=(8.8,4.9));ax=fig.add_axes([.09,.16,.61,.78])
    good=[];bad=[]
    for a in range(9):
        for b in range(9-a):
            (good if max(a,b)<=4 else bad).append((a,b))
    ax.scatter(*zip(*good),marker='o',s=42,label='Capacity still possible')
    ax.scatter(*zip(*bad),marker='x',s=46,label='Impossible to complete')
    ax.add_patch(Rectangle((-.17,-.17),4.34,4.34,fill=False,linewidth=1.3))
    ax.plot([0,8],[8,0],linestyle='--',linewidth=1)
    ax.annotate('',xy=(0,5),xytext=(0,0),arrowprops={'arrowstyle':'->','linestyle':':','linewidth':2})
    ax.set(xlim=(-.55,8.4),ylim=(-.45,8.6),xticks=range(9),yticks=range(9),
           xlabel='Read cases reporting zero, a',ylabel='Read cases reporting one, b')
    ax.set_aspect('equal')
    ax.tick_params(labelsize=12)
    ax.xaxis.label.set_size(13);ax.yaxis.label.set_size(13)
    ax.legend(loc='upper left',bbox_to_anchor=(1.01,1.01),frameon=False,fontsize=12)
    fig.text(.72,.60,'Eight possible cases\nChild capacity: four',fontsize=12,va='top')
    fig.text(.72,.38,'Five matching reports\nclose the root before\nits last three rows\nneed to be read.',fontsize=13,va='top',linespacing=1.4)
    save(fig,'prefix_capacity')

    record=json.loads((ROOT/'validation/synthesis_demonstration.json').read_text())
    rows=record['evaluations'];xs=[r['cases'] for r in rows]
    fig=plt.figure(figsize=(8.7,4.6));ax=fig.add_axes([.10,.19,.85,.67])
    ax.plot(xs,[r['full_scan']['table_reads'] for r in rows],marker='o',label='Ordered full-scan compiler')
    ax.plot(xs,[r['lowered']['table_reads'] for r in rows],marker='s',label='Same compiler with synthesized pruning')
    ax.set_xscale('log',base=2);ax.set_yscale('log')
    ax.set(xticks=xs,xticklabels=[str(x) for x in xs],xlabel='Possible hidden cases',ylabel='Compilation model-record reads')
    ax.tick_params(labelsize=12)
    ax.xaxis.label.set_size(13);ax.yaxis.label.set_size(13)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),frameon=False,fontsize=12)
    ax.grid(axis='y',linestyle=':',alpha=.35)
    fig.text(.10,.035,'Predicate comparisons are charged separately. These are not CPU timings.',fontsize=10)
    save(fig,'synthesized_read_cost')

    fig=plt.figure(figsize=(10.8,5.2));ax=fig.add_axes([.01,.10,.98,.88]);ax.axis('off')
    ax.set(xlim=(0,11),ylim=(0,5.0))
    locations=[(1.7,3.9),(5.5,3.9),(9.3,3.9),(9.3,1.4),(5.5,1.4),(1.7,1.4)]
    labels=[('Feature conflict','Same counts, different\nremaining capacity'),
            ('Expose capacity','A supplied feature\nresolves the conflict'),
            ('Compose the rule','Three counterexamples\nwithin 3,960 ASTs'),
            ('Check its scope','Recognized formula\nplus a proved bound'),
            ('Stream the search','Skip only suffixes\nthat cannot rescue a root'),
            ('Check the controller','Reconstruct branches\nand replay every case')]
    for (x,y),(title,body) in zip(locations,labels):
        ax.add_patch(FancyBboxPatch((x-1.45,y-.60),2.90,1.20,boxstyle='round,pad=.07',fill=False,linewidth=1.2))
        ax.text(x,y+.25,title,ha='center',va='center',fontsize=17,fontweight='bold')
        ax.text(x,y-.20,body,ha='center',va='center',fontsize=15,linespacing=1.4)
    arrows=[((3.22,3.9),(3.95,3.9)),((7.03,3.9),(7.75,3.9)),
            ((9.3,3.20),(9.3,2.10)),((7.77,1.4),(7.05,1.4)),((3.97,1.4),(3.25,1.4))]
    for a,b in arrows:
        ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','linewidth':1.5})
    ax.text(5.5,2.54,'Learned artifact: max(a, b) > capacity',ha='center',va='center',fontsize=16)
    fig.text(.5,.015,'Supplied: primitive language, teacher, feature registry, compiler skeleton, and scope proof.',ha='center',fontsize=14)
    save(fig,'rule_synthesis_pipeline')
    print('Generated three analytical vector figures and three previews.')

if __name__=='__main__':main()

"""Three analytical, reproducible Matplotlib figures for the expanded theory."""
from pathlib import Path
from fractions import Fraction
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'


def save(fig,name):
    for suffix in ('pdf','svg','png'):
        kwargs={'dpi':180} if suffix=='png' else {}
        fig.savefig(OUT/f'{name}.{suffix}',bbox_inches='tight',pad_inches=.15,**kwargs)
    plt.close(fig)


def box(ax,x,y,w,h,text,size=12):
    ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,fill=False,linewidth=1.1))
    ax.text(x,y,text,ha='center',va='center',fontsize=size,linespacing=1.45)


def arrow(ax,p,q):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=13,linewidth=1.2))


def main():
    OUT.mkdir(exist_ok=True)
    data=json.loads((ROOT/'data'/'observable_illustrations.json').read_text())
    fig=plt.figure(figsize=(8.8,4.8));ax=fig.add_axes((.12,.17,.84,.72))
    rows=data['noisy_association'][:7]
    ns=[r['reports'] for r in rows]
    ax.plot(ns,[float(Fraction(r['plus'])) for r in rows],marker='o',linewidth=1.7,label='Positive target–convention association')
    ax.plot(ns,[float(Fraction(r['minus'])) for r in rows],marker='s',linestyle='--',linewidth=1.7,label='Negative target–convention association')
    ax.set(xlim=(-.15,6.15),ylim=(-.03,1.03),xticks=ns,yticks=[0,.25,.5,.75,1])
    ax.set_xlabel('Fresh reference reports, each equal to one',fontsize=12)
    ax.set_ylabel('Posterior probability of target bit 1',fontsize=12)
    ax.tick_params(labelsize=10)
    ax.grid(axis='y',linestyle=':',alpha=.45)
    ax.legend(loc='center right',frameon=False,fontsize=10,bbox_to_anchor=(1,.5))
    ax.annotate('Same two marginals',xy=(0,.5),xytext=(.45,.58),fontsize=11,
                arrowprops={'arrowstyle':'->'})
    ax.annotate('3/4',xy=(1,.75),xytext=(1.5,.80),fontsize=11,arrowprops={'arrowstyle':'->'})
    ax.annotate('1/4',xy=(1,.25),xytext=(1.5,.18),fontsize=11,arrowprops={'arrowstyle':'->'})
    fig.text(.54,.96,'Future correction needs the association',ha='center',fontsize=14)
    save(fig,'noisy_association')

    fig=plt.figure(figsize=(8.8,4.7));ax=fig.add_axes((.11,.18,.85,.70))
    k=list(range(6));fixed=[2,1,0,0,0,0];switch=[2,1,1,1,1,1]
    ax.plot(k,fixed,marker='o',linewidth=1.8,label='Either candidate held fixed: A or B')
    ax.plot(k,switch,marker='D',linestyle='--',linewidth=1.4,label='Alternating candidates: a different model')
    ax.set(xlim=(-.15,5.15),ylim=(-.18,2.35),xticks=k,yticks=[0,1,2])
    ax.set_xlabel('Number of executed actions',fontsize=12)
    ax.set_ylabel('Observed output',fontsize=12)
    ax.grid(axis='y',linestyle=':',alpha=.45)
    ax.legend(loc='upper right',frameon=False,fontsize=10)
    ax.annotate('Hidden states differ here:\nA gives (1, 0); B gives (0, 1)',xy=(1,1),xytext=(1.2,1.60),
                fontsize=10,linespacing=1.3,arrowprops={'arrowstyle':'->'})
    ax.annotate('Same fixed-model continuation',xy=(3,0),xytext=(2.55,.32),fontsize=10,
                arrowprops={'arrowstyle':'->'})
    fig.text(.53,.96,'Fixed uncertainty is not arbitrary switching',ha='center',fontsize=14)
    save(fig,'fixed_model_outputs')

    fig=plt.figure(figsize=(9.1,4.4));ax=fig.add_axes((.03,.04,.94,.91));ax.set(xlim=(0,9),ylim=(0,4.5));ax.axis('off')
    ax.text(4.5,4.23,'An unseen difference must remain unseen under continuation',ha='center',fontsize=14)
    ax.text(.2,3.64,'STRUCTURED NO-RETURN',fontsize=10,ha='left')
    box(ax,1.55,2.94,2.65,.83,'Discrepancy in '+r'$\mathrm{span}(e_3)$'+'\n'+r'$Qe_3=0$')
    box(ax,4.55,2.94,2.65,.83,'Every reference action\nkeeps this span invariant')
    box(ax,7.62,2.94,2.32,.83,'Every later output\ndifference is zero')
    arrow(ax,(2.9,2.94),(3.19,2.94));arrow(ax,(5.9,2.94),(6.43,2.94))
    ax.text(.2,2.01,'HIDDEN RETURN',fontsize=10,ha='left')
    box(ax,1.55,1.30,2.65,.83,r'$\mathrm{im}(D)=\mathrm{span}(e_2)$'+'\n'+r'$QD=0$')
    box(ax,4.55,1.30,2.65,.83,r'$Ae_2=e_1$'+'\nThe hidden error moves')
    box(ax,7.62,1.30,2.32,.83,r'$QAD\ne0$'+'\nSecond output differs')
    arrow(ax,(2.9,1.30),(3.19,1.30));arrow(ax,(5.9,1.30),(6.43,1.30))
    ax.text(4.5,.39,r'Check the full propagated discrepancy span $E_\infty$, not only $QD$.',ha='center',fontsize=12)
    save(fig,'hidden_uncertainty')
    print('Generated three analytical figures as PDF, SVG, and PNG from the explicit models.')

if __name__=='__main__':main()

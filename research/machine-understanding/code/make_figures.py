#!/usr/bin/env python3
"""Reproduce four analytical figures. No measurements or generated imagery.
Matplotlib uses its default color cycle; all quantities come from stated models.
"""
from pathlib import Path
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures';OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':12,
                     'mathtext.fontset':'dejavuserif','pdf.fonttype':42,
                     'savefig.bbox':'tight'})

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.12)
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)

def arrow(ax,p,q,label=None,offset=(0,0)):
    ax.annotate('',xy=q,xytext=p,arrowprops={'arrowstyle':'->','lw':1.3,'shrinkA':2,'shrinkB':2})
    if label:
        ax.text((p[0]+q[0])/2+offset[0],(p[1]+q[1])/2+offset[1],label,
                ha='center',va='center',fontsize=12)

def box(ax,x,y,w,h):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,
                              boxstyle='round,pad=0.025,rounding_size=0.06',
                              fill=False,lw=1.2))

fig,ax=plt.subplots(figsize=(9,4.1));ax.set(xlim=(0,9),ylim=(0,4));ax.axis('off')
box(ax,4.5,3.35,3.8,.76)
ax.text(4.5,3.35,r'Complete state $(a,b,c)\in\mathbb{F}_5^3$',ha='center',va='center',fontsize=14)
for x in (1.45,4.5,7.55):arrow(ax,(4.5,2.93),(x,2.18))
for x,title,n,label in [(1.45,'Current display',5,r'$s=a+b$'),(4.5,'All $H/W$ continuations',25,r'$(s,b)$'),(7.55,'Add the $J$ operation',125,r'$(s,b,c)$')]:
    box(ax,x,1.35,2.62,1.62)
    ax.text(x,1.95,title,ha='center',va='center',fontsize=11)
    ax.text(x,1.39,str(n),ha='center',va='center',fontsize=24,fontweight='bold')
    ax.text(x,.92,label,ha='center',va='center',fontsize=15)
ax.text(4.5,.15,'Minimal distinguishable states depend on the permitted future questions.',
        ha='center',va='center',fontsize=11)
save(fig,'representation_scope')

fig,ax=plt.subplots(figsize=(8.6,3.8));ax.set(xlim=(0,8.6),ylim=(0,3.8));ax.axis('off')
for x,y,w in [(1.55,2.95,2),(6.9,2.95,2.5),(1.55,.85,2.3),(6.9,.85,2.5)]:box(ax,x,y,w,.8)
ax.text(1.55,2.95,r'$(a,b)$',ha='center',va='center',fontsize=17)
ax.text(6.9,2.95,r'$(a+b,b)$',ha='center',va='center',fontsize=17)
ax.text(1.55,.85,r'$(a+b,b)$',ha='center',va='center',fontsize=17)
ax.text(6.9,.85,r'$(a+2b,b)$',ha='center',va='center',fontsize=17)
arrow(ax,(2.6,2.95),(5.57,2.95),r'$T(a,b)=(a+b,b)$',offset=(0,.35))
arrow(ax,(2.75,.85),(5.57,.85),r'$T$',offset=(0,-.32))
arrow(ax,(1.55,2.52),(1.55,1.29),r'$H$',offset=(-.45,0))
arrow(ax,(6.9,2.52),(6.9,1.29),r'$\bar H$',offset=(.45,0))
ax.text(4.3,1.88,r'$T\circ H=\bar H\circ T$',ha='center',va='center',fontsize=15)
save(fig,'transport_square')

fig,ax=plt.subplots(figsize=(8.6,4.2))
for L in (F(1,2),F(1),F(3,2)):
    e=F(0);vals=[e]
    for _ in range(8):e=L*e+F(1,100);vals.append(e)
    label={F(1,2):r'$L=1/2$',F(1):r'$L=1$',F(3,2):r'$L=3/2$'}[L]
    ax.plot(range(9),[float(v) for v in vals],marker='o',linewidth=1.7,markersize=4,label=label)
ax.set_xlabel('Number of operations $n$');ax.set_ylabel('State error $e_n$')
ax.set_xticks(range(9));ax.set_ylim(bottom=0)
ax.spines[['top','right']].set_visible(False)
ax.legend(loc='center left',bbox_to_anchor=(1.02,.6),frameon=False)
ax.text(1.05,.94,r'$e_{n+1}=Le_n+0.01$'+'\n'+r'$e_0=0$',transform=ax.transAxes,va='top',fontsize=11)
fig.subplots_adjust(left=.11,right=.68,bottom=.19,top=.95)
save(fig,'error_accumulation')

fig,ax=plt.subplots(figsize=(9,4.3));ax.set(xlim=(0,9),ylim=(0,4.3));ax.axis('off')
box(ax,1.65,3.1,2.35,.92);box(ax,7.0,3.1,2.35,.92)
box(ax,1.65,1.0,2.35,.92);box(ax,7.0,1.0,3.25,1.32)
ax.text(1.65,3.1,r'$V=\{m_0,m_1\}$',ha='center',va='center',fontsize=15)
ax.text(7,3.1,r'$C_1(V)=\{m_1\}$',ha='center',va='center',fontsize=15)
ax.text(1.65,1,r'$\phi[V]=\{n_0,n_1\}$',ha='center',va='center',fontsize=14)
ax.text(7,1.29,r'Source route: $\{n_1\}$',ha='center',va='center',fontsize=13)
ax.text(7,.75,r'Target route: $\{n_0,n_1\}$',ha='center',va='center',fontsize=13)
arrow(ax,(2.88,3.1),(5.76,3.1),'observe $1$',offset=(0,.3))
arrow(ax,(1.65,2.6),(1.65,1.5),r'$\phi$',offset=(-.4,0))
arrow(ax,(7,2.6),(7,1.71),r'$\phi$',offset=(.43,0))
arrow(ax,(2.88,1),(5.32,1),r'observe $*$',offset=(0,-.35))
ax.text(4.5,.08,r'$\eta(0)=\eta(1)=*$: the evidence distinction is lost.',ha='center',fontsize=11)
save(fig,'correction_square')
print('Created four PDF vector figures and four PNG previews in figures/.')

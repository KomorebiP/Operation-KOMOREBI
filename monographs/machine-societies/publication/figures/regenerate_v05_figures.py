"""Three analytical diagrams for the theoretical edition (no empirical data).

Run: python figures/regenerate_v05_figures.py
Requires matplotlib. The permutation convention is composition right to left.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent
META = {'CreationDate': None, 'ModDate': None}

def arrow(ax, start, end, *, dashed=False):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>',
                 mutation_scale=14, linewidth=1.35,
                 linestyle='--' if dashed else '-'))

def box(ax, x, y, text, width=1.5, height=.55):
    ax.add_patch(FancyBboxPatch((x-width/2,y-height/2),width,height,
                 boxstyle='round,pad=0.06',fill=False,linewidth=1.25))
    ax.text(x,y,text,ha='center',va='center',fontsize=12)

def save(fig, name):
    fig.savefig(OUT/name,bbox_inches='tight',pad_inches=.10,metadata=META)
    plt.close(fig)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams['pdf.fonttype']=42
    fig, ax=plt.subplots(figsize=(7.0,3.65))
    ax.set_xlim(0,10);ax.set_ylim(0,5.2);ax.axis('off')
    box(ax,5,4.50,r'$s$')
    box(ax,2.1,2.75,r'$a$');box(ax,7.9,2.75,r'$b$')
    box(ax,5,.85,r'$c$')
    arrow(ax,(4.35,4.15),(2.55,3.10));arrow(ax,(5.65,4.15),(7.45,3.10))
    arrow(ax,(2.60,2.39),(4.38,1.20),dashed=True)
    arrow(ax,(7.40,2.39),(5.62,1.20),dashed=True)
    ax.text(2.42,4.08,'Admissible step',ha='center',fontsize=10)
    ax.text(7.58,4.08,'Admissible step',ha='center',fontsize=10)
    ax.text(1.66,1.32,'Finite amendment\ncontinuation',ha='center',fontsize=9.5,linespacing=1.5)
    ax.text(8.34,1.32,'Finite amendment\ncontinuation',ha='center',fontsize=9.5,linespacing=1.5)
    ax.text(5,.15,'Required: both branches can reach a common state',ha='center',fontsize=10)
    save(fig,'constitutional_confluence.pdf')

    fig, ax=plt.subplots(figsize=(7.2,3.75))
    ax.set_xlim(-.1,10.1);ax.set_ylim(0,5.1);ax.axis('off')
    box(ax,1.15,3.95,r'$A$');box(ax,8.85,3.95,r'$B$');box(ax,5,1.20,r'$C$')
    arrow(ax,(2.03,3.95),(7.97,3.95))
    arrow(ax,(8.22,3.57),(5.61,1.57))
    arrow(ax,(4.39,1.57),(1.78,3.57))
    ax.text(5,4.30,r'$g_{AB}=(12)$',ha='center',fontsize=12)
    ax.text(8.12,2.32,r'$g_{BC}=(23)$',ha='center',fontsize=12)
    ax.text(1.78,2.32,r'$g_{CA}=e$',ha='center',fontsize=12)
    ax.text(5,2.83,'Compose in traversal order',ha='center',fontsize=10)
    ax.text(5,2.28,r'$H=e\,(23)(12)\ne e$',ha='center',fontsize=13)
    ax.text(5,.29,'Every edge is invertible; the round trip is not identity.',ha='center',fontsize=10)
    save(fig,'noncommutative_holonomy.pdf')

    fig, ax=plt.subplots(figsize=(7.2,2.95))
    ax.set_xlim(0,10);ax.set_ylim(0,4);ax.axis('off')
    for x,k in ((1.15,0),(5,1),(8.85,2)):
        box(ax,x,2.60,rf'$w={k}$',width=1.65,height=.64)
        ax.text(x,1.82,r'$\varphi$ true' if k<2 else r'$\varphi$ false',ha='center',fontsize=11)
    ax.plot([2.08,4.06],[2.60,2.60],linewidth=1.6)
    ax.plot([5.94,7.92],[2.60,2.60],linestyle='--',linewidth=1.6)
    ax.text(3.075,3.01,r'Agent $A$: $\sim_A$',ha='center',fontsize=11)
    ax.text(6.925,3.01,r'Agent $B$: $\sim_B$',ha='center',fontsize=11)
    ax.text(5,.89,r'At $w=0$: $K_A\varphi\ \wedge\ K_B\varphi$',ha='center',fontsize=12)
    ax.text(5,.25,r'But $0\sim_A1\sim_B2$, so $C_{\{A,B\}}\varphi$ is false.',ha='center',fontsize=11)
    save(fig,'common_knowledge_chain.pdf')
    print('Generated 3 vector diagrams in', OUT)

if __name__=='__main__':main()

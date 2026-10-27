"""One reproducible vector diagram for the 1.1 ambient proof-field extension."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'figures'
OUT.mkdir(exist_ok=True, parents=True)

fig, ax = plt.subplots(figsize=(8.8, 3.15))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.0)
ax.axis('off')

frame = FancyBboxPatch((0.2,0.15),11.6,3.6,boxstyle='round,pad=0.13',
                       facecolor='white',edgecolor='#6b7280',linestyle='--',linewidth=1.0)
ax.add_patch(frame)

def node(cx,cy,label,edge='#374151'):
    w,h=2.10,.62
    ax.add_patch(FancyBboxPatch((cx-w/2,cy-h/2),w,h,boxstyle='round,pad=0.09',
                                facecolor='white',edgecolor=edge,linewidth=1.5))
    ax.text(cx,cy,label,ha='center',va='center',fontsize=9.2)

def arrow(x0,y0,x1,y1,edge='#374151',dashed=False):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=12,
        connectionstyle='arc3',color=edge,linewidth=1.4,
        linestyle='--' if dashed else '-'))

node(1.65,2.0,'Premise')
node(5.0,2.95,'Certified lemma',edge='#2b6e59')
node(8.5,2.95,'Verified goal',edge='#2b6e59')
node(5.0,1.12,'Uncertified step',edge='#b56a33')
node(8.5,1.12,'Local obstruction',edge='#b56a33')
arrow(2.75,2.25,3.93,2.78,edge='#2b6e59')
arrow(6.1,2.95,7.39,2.95,edge='#2b6e59')
arrow(2.75,1.83,3.93,1.25,edge='#b56a33',dashed=True)
arrow(6.1,1.12,7.39,1.12,edge='#b56a33',dashed=True)
ax.text(8.5,.59,'The goal may still be provable',ha='center',fontsize=8.7,style='italic',color='#374151')
ax.text(0.46,3.48,'Ambient proof field (schematic)',fontsize=10.4,weight='bold',color='#1f2937')
fig.savefig(OUT/'fig_14_ambient_field.pdf',bbox_inches='tight',pad_inches=.18)
fig.savefig(OUT/'fig_14_ambient_field.png',dpi=180,bbox_inches='tight',pad_inches=.18)
plt.close(fig)

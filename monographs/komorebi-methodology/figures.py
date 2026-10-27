"""Publication figures for The Komorebi Methodology — mathematical essay.
Exact vector plots, not synthetic illustrative images.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT=Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
COVER='#282331'
INK='#352C3B'
ACCENT='#70566D'
GOLD='#A98D5E'
MUTED='#68656B'
PALE='#F7F5F7'
RULE='#DCD7DD'
plt.rcParams.update({'font.family':'DejaVu Serif', 'pdf.fonttype':42,'ps.fonttype':42})

fig,ax=plt.subplots(figsize=(7.65,4.3))
fig.patch.set_facecolor('white');ax.set_facecolor('white')
ax.set_xlim(-4.2,4.2);ax.set_ylim(-2.54,2.52);ax.axis('off')
steps=[('QUESTION','Hypotheses'),('REALIZATION','Representation'),('OBSTRUCTION','Residuals'),('RESOLUTION','Corrections'),('CERTIFICATION','Proof and audit'),('MEMORY','Provenance')]
angles=np.deg2rad([90,30,-30,-90,-150,150])
positions=[(3.03*np.cos(t),1.70*np.sin(t)) for t in angles]
for i,((title,sub),(x,y)) in enumerate(zip(steps,positions)):
    bg=PALE if i%2==0 else '#FFFFFF'
    p=FancyBboxPatch((x-1.13,y-.40),2.26,.80,boxstyle='round,pad=.016,rounding_size=.032', facecolor=bg,edgecolor=RULE,linewidth=.8,zorder=4)
    ax.add_patch(p)
    ax.plot([x-.94,x-.55],[y+.28,y+.28],lw=1.2,c=GOLD,zorder=5)
    ax.text(x,y+.09,title,ha='center',va='center',color=INK,fontsize=9.15,fontweight='bold',zorder=6)
    ax.text(x,y-.16,sub,ha='center',va='center',color=MUTED,fontsize=8.8,zorder=6)
for i in range(6):
    j=(i+1)%6
    a=np.array(positions[i]);b=np.array(positions[j]);v=(b-a);v=v/np.linalg.norm(v)
    # Clip to the rectangular nodes, not a fixed circular radius. A fixed
    # radius can reverse arrows between vertically adjacent short boxes.
    half_width, half_height, gap = 1.146, .416, .035
    tx = half_width / abs(v[0]) if abs(v[0]) > 1e-12 else float('inf')
    ty = half_height / abs(v[1]) if abs(v[1]) > 1e-12 else float('inf')
    offset = min(tx, ty) + gap
    start = a + v * offset
    end = b - v * offset
    if float(np.dot(end - start, b - a)) <= 0:
        raise ValueError(f'Cycle arrow {i} would be reversed or degenerate.')
    ar=FancyArrowPatch(start,end,connectionstyle='arc3,rad=-.12',arrowstyle='-|>',mutation_scale=11,lw=1.05,color=GOLD,zorder=2)
    ax.add_patch(ar)
ax.text(0,.16,'THE RESEARCH',fontsize=10.5,ha='center',va='center',color=MUTED)
ax.text(0,-.17,'CYCLE',fontsize=15.2,ha='center',va='center',color=INK)
fig.savefig(OUT/'inquiry_cycle.pdf',bbox_inches='tight',pad_inches=.1)
fig.savefig(OUT/'inquiry_cycle.png',dpi=250,bbox_inches='tight',pad_inches=.1)
plt.close(fig)



# Exact two-step retained/complementary paths. Coordinates in the boxes are data.
def box(ax, xy, w, h, title, value, selected=True):
    x,y=xy
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,
        boxstyle='round,pad=.015,rounding_size=.035',
        facecolor=PALE if selected else 'white',edgecolor=RULE,linewidth=.9,zorder=4))
    ax.text(x,y+.13,title,ha='center',va='center',fontsize=9.4,
        fontweight='bold',color=INK,zorder=5)
    ax.text(x,y-.16,value,ha='center',va='center',fontsize=11,color=INK,zorder=5)

def arrow(ax,a,b,selected=True,dashed=False,rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,
        connectionstyle=f'arc3,rad={rad}',lw=1.6 if selected else 1.05,
        linestyle='--' if dashed else '-',color=ACCENT if selected else MUTED,zorder=2))

fig,ax=plt.subplots(figsize=(8.3,4.0))
ax.set_xlim(-.05,8.35);ax.set_ylim(-.48,3.90);ax.axis('off')
box(ax,(.98,1.83),1.7,.78,'INPUT',r'$(1,2)$')
box(ax,(4.02,2.83),1.95,.78,'RETAINED',r'$(4,6)$')
box(ax,(4.02,.82),1.95,.78,'COMPLEMENT',r'$-1$')
box(ax,(7.34,1.83),1.75,.78,'AFTER TWO',r'$(14,17)$')
arrow(ax,(1.85,2.04),(3.02,2.72));arrow(ax,(1.85,1.61),(3.02,.94))
arrow(ax,(5.02,2.70),(6.44,2.02));arrow(ax,(5.02,.94),(6.44,1.62))
ax.text(2.25,2.57,r'$A$',fontsize=13,color=INK)
ax.text(2.25,1.06,r'$C$',fontsize=13,color=INK)
ax.text(5.70,3.58,r'$A^2(1,2)=(14,18)$',ha='center',fontsize=9.4,color=INK)
ax.text(5.70,.07,r'$BC(1,2)=(0,-1)$',ha='center',fontsize=9.4,color=INK)
ax.text(4.08,-.35,'The reduced model omits the lower path.',ha='center',fontsize=10,color=MUTED)
fig.savefig(OUT/'return_paths.pdf',bbox_inches='tight',pad_inches=.10)
fig.savefig(OUT/'return_paths.png',bbox_inches='tight',pad_inches=.10,dpi=250)
plt.close(fig)

# AND/OR hypergraph: square nodes represent joint-premise justifications.
fig,ax=plt.subplots(figsize=(8.3,4.25))
ax.set_xlim(-.2,8.3);ax.set_ylim(-.48,3.92);ax.axis('off')
coords={'A':(.55,3.15),'B':(.55,.8),'L':(3.4,3.15),'M':(3.4,.8),
        'T':(6.55,3.15),'U':(3.4,1.90)}
def node(name,selected=False,candidate=False):
    x,y=coords[name]
    ax.add_patch(FancyBboxPatch((x-.45,y-.32),.90,.64,
        boxstyle='round,pad=.016,rounding_size=.035',
        facecolor=PALE if selected else 'white',edgecolor=ACCENT if selected else RULE,
        linewidth=1.15 if selected else .9,linestyle='--' if candidate else '-',zorder=4))
    ax.text(x,y,name,ha='center',va='center',fontsize=15,color=INK,zorder=5)
for n in coords: node(n,n in {'A','B','L','T'},n=='U')
# Selected A AND B -> L -> T.
j1=(2.0,3.15)
ax.plot(*j1,marker='s',markersize=6,color=ACCENT,zorder=5)
arrow(ax,(1.02,3.15),(1.90,3.15))
arrow(ax,(.75,1.12),(1.94,3.02),rad=.12)
arrow(ax,(2.1,3.15),(2.91,3.15))
arrow(ax,(3.87,3.15),(6.06,3.15))
# Alternative A -> M, then M AND B -> T. Put the conjunction below/right.
arrow(ax,(.88,2.84),(3.07,1.13),selected=False,rad=-.05)

j2=(5.02,.80)
ax.plot(*j2,marker='s',markersize=5,color=MUTED,zorder=5)
arrow(ax,(3.87,.80),(4.93,.80),selected=False)
# B uses a lower lane, so it cannot be mistaken for an edge from M.
ax.plot([1.02,1.34,4.60],[.8,.12,.12],color=MUTED,lw=1.05,zorder=1)
arrow(ax,(4.60,.12),(4.97,.70),selected=False)
arrow(ax,(5.08,.89),(6.30,2.81),selected=False)
# Uncertified extension M -> U remains dashed and isolated from certificate.
arrow(ax,(3.40,1.14),(3.40,1.55),selected=False,dashed=True)
ax.text(4.05,1.41,'candidate only',ha='left',fontsize=9,color=MUTED)
ax.text(4.9,3.46,'selected certificate',ha='center',fontsize=10,color=ACCENT)
ax.text(4.05,-.29,'Square junction: every incoming premise is required.',ha='center',fontsize=10,color=MUTED)
fig.savefig(OUT/'proof_field.pdf',bbox_inches='tight',pad_inches=.10)
fig.savefig(OUT/'proof_field.png',bbox_inches='tight',pad_inches=.10,dpi=250)
plt.close(fig)
print('Generated three PDF figures and three PNG previews.')

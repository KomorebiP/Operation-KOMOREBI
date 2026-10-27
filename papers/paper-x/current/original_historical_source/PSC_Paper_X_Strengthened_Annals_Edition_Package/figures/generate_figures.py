from __future__ import annotations
import math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)

def box(ax, xy, w, h, text, fs=9, lw=1.1):
    x,y=xy
    p=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02",fill=False,linewidth=lw)
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs)
    return p

def arrow(ax, a, b, lw=1.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=10,linewidth=lw))

# 01 architecture
fig, ax = plt.subplots(figsize=(8.2,3.7))
ax.set_xlim(0,10); ax.set_ylim(0,4); ax.axis("off")
box(ax,(0.2,2.35),2.2,0.8,"residual roots")
box(ax,(3.0,2.35),2.2,0.8,"finite lift levels")
box(ax,(5.8,2.35),2.2,0.8,"complete branches")
box(ax,(7.6,0.55),2.2,0.8,"occupied carrier")
box(ax,(4.4,0.55),2.2,0.8,"common spine")
box(ax,(1.2,0.55),2.2,0.8,"horizontal companions")
arrow(ax,(2.4,2.75),(3.0,2.75)); arrow(ax,(5.2,2.75),(5.8,2.75))
arrow(ax,(1.35,1.35),(1.35,2.35)); arrow(ax,(3.4,0.95),(4.4,0.95)); arrow(ax,(6.6,0.95),(7.6,0.95))
arrow(ax,(6.9,2.35),(6.1,1.35))
ax.text(4.1,3.5,"vertical deformation",ha="center",fontsize=10)
ax.text(3.9,0.15,"horizontal completion",ha="center",fontsize=10)
ax.text(8.7,1.6,"support and\nnonvanishing",ha="center",fontsize=9)
save(fig,"01_architecture.pdf")

# 02 residual forest
fig, ax=plt.subplots(figsize=(8.0,4.8))
ax.set_xlim(-0.5,10.5); ax.set_ylim(-0.3,5.3); ax.axis("off")
roots=[1.5,5.0,8.5]
for r,x in enumerate(roots):
    ax.add_patch(Circle((x,4.7),0.18,fill=False,linewidth=1.2))
    ax.text(x,5.02,rf"$\bar x_{r+1}$",ha="center")
    prev=[x]
    for level in range(1,4):
        curr=[]
        spread=0.55/(level)
        for px in prev:
            for s in (-1,1):
                cx=px+s*spread
                cy=4.7-level*1.05
                curr.append(cx)
                ax.plot([px,cx],[cy+1.05,cy],linewidth=.8)
                ax.add_patch(Circle((cx,cy),0.12,fill=False,linewidth=1.0))
        prev=curr
ax.text(0.0,4.7,"depth 1",va="center")
ax.text(0.0,3.65,"depth 2",va="center")
ax.text(0.0,2.60,"depth 3",va="center")
ax.text(0.0,1.55,"depth 4",va="center")
ax.text(5.0,0.28,"positive depth edges stay above one residual root",ha="center")
save(fig,"02_residual_forest.pdf")

# 03 visibility tree
fig, ax=plt.subplots(figsize=(8.0,4.2))
ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
levels=[4.5,3.3,2.1,0.9]
clusters=[[(1,9)],[(1,4.6),(5.4,9)],[(1,2.7),(2.9,4.6),(5.4,7.0),(7.2,9)],[(1,1.7),(2.0,2.7),(2.9,3.7),(3.9,4.6),(5.4,6.2),(6.4,7.0),(7.2,8.0),(8.2,9)]]
for d,(y,cs) in enumerate(zip(levels,clusters),start=1):
    ax.text(.2,y,rf"depth {d}",va="center")
    for a,b in cs:
        box(ax,(a,y-.25),b-a,.5,"")
for i in range(8):
    ax.text(1.35+i*1.0,0.25,rf"$a_{i+1}$",ha="center")
ax.text(5,4.92,"congruence classes refine as precision increases",ha="center",fontsize=10)
save(fig,"03_visibility_tree.pdf")

# 04 level counts
fig, ax=plt.subplots(figsize=(7.6,4.5))
m=np.arange(1,10)
smooth=3**(2*(m-1))
weighted=2**np.array([max(x-1,0)+max(x-2,0)+max(x-4,0) for x in m])
singular=3**(m-np.ceil(m/2).astype(int))
cross=3**(m-1)*(3+m*(3-1))
ax.plot(m,np.log10(smooth),marker='o',label='smooth dimension two')
ax.plot(m,np.log10(weighted),marker='s',label='weighted chart')
ax.plot(m,np.log10(singular),marker='^',label='square nilpotent')
ax.plot(m,np.log10(cross),marker='d',label='normal crossing')
ax.set_xlabel("precision depth")
ax.set_ylabel("base ten logarithm of level count")
ax.legend(frameon=False)
ax.grid(True,linewidth=.35)
save(fig,"04_level_counts.pdf")

# 05 complex packets
fig, ax=plt.subplots(figsize=(8.2,4.4))
ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
for j,y in enumerate([3.7,2.5,1.3]):
    box(ax,(1.1,y),1.5,.55,rf"$C^{j}$")
    box(ax,(4.25,y),1.5,.55,rf"$P_1C^{j}$")
    box(ax,(7.4,y),1.5,.55,rf"$P_2C^{j}$")
    arrow(ax,(2.6,y+.28),(4.25,y+.28))
    arrow(ax,(5.75,y+.28),(7.4,y+.28))
for x in [1.85,5.0,8.15]:
    arrow(ax,(x,3.7),(x,3.05))
    arrow(ax,(x,2.5),(x,1.85))
ax.text(5,4.72,"chain projectors split the full correction complex",ha="center",fontsize=10)
ax.text(5,.42,r"$H^r(C^\bullet)\cong H^r(P_1C^\bullet)\oplus H^r(P_2C^\bullet)$",ha="center")
save(fig,"05_obstruction_packets.pdf")

# 06 transport condensation
fig, ax=plt.subplots(figsize=(8.2,4.8))
ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis("off")
pos={'A':(1.1,4.5),'B':(2.3,4.5),'C':(4.2,4.5),'D':(1.5,2.1),'E':(2.8,2.1),'F':(5.2,2.1),'G':(8.2,3.2)}
edges=[('A','B'),('B','A'),('B','C'),('D','E'),('E','D'),('E','F'),('F','C'),('G','F')]
for u,v in edges:
    arrow(ax,pos[u],pos[v])
for n,(x,y) in pos.items():
    ax.add_patch(Circle((x,y),.25,fill=False,linewidth=1.2)); ax.text(x,y,n,ha='center',va='center')
for x,y,w,h,label in [(0.55,3.95,2.3,1.1,'source component'),(.9,1.55,2.5,1.1,'source component'),(7.55,2.65,1.3,1.1,'source')]:
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.03',fill=False,linestyle='--',linewidth=.8)
    ax.add_patch(p); ax.text(x+w/2,y-.25,label,ha='center',fontsize=8)
ax.text(5,5.55,"one generator is required in each source component",ha='center',fontsize=10)
save(fig,"06_transport_graph.pdf")

# 07 companion forests
fig, ax=plt.subplots(figsize=(8.2,4.7))
ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis("off")
primes=[2,3,5,7,13]
counts={2:[1,0,0,0],3:[0,0,0,0],5:[2,2,2,2],7:[0,0,0,0],13:[2,2,2,2]}
for i,p in enumerate(primes):
    x=.9+i*2.0
    ax.text(x,5.55,rf"$p={p}$",ha='center')
    for d,c in enumerate(counts[p]):
        y=4.8-d*1.05
        if c==0:
            ax.text(x,y,"empty",ha='center',va='center',fontsize=8)
        elif c==1:
            ax.add_patch(Circle((x,y),.13,fill=False))
        else:
            ax.add_patch(Circle((x-.25,y),.11,fill=False)); ax.add_patch(Circle((x+.25,y),.11,fill=False))
        if d>0 and counts[p][d-1] and c:
            if counts[p][d-1]==1:
                prev=[x]
            else: prev=[x-.25,x+.25]
            cur=[x] if c==1 else [x-.25,x+.25]
            for a,b in zip(prev,cur): ax.plot([a,b],[y+1.05,y],linewidth=.8)
ax.text(5,.35,r"finite roots of $x^2+1$ through four precision levels",ha='center')
save(fig,"07_companion_forests.pdf")

# 08 common spine
fig, ax=plt.subplots(figsize=(8.3,4.2))
ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
box(ax,(3.4,3.7),3.2,.65,"algebraic Frobenius spine")
for x,label in [(1.0,r"$\lambda_1$"),(3.0,r"$\lambda_2$"),(5.0,r"$\lambda_3$"),(7.0,r"$\lambda_4$"),(9.0,r"$\lambda_5$")]:
    box(ax,(x-.55,.75),1.1,.6,label)
    arrow(ax,(5.0,3.7),(x,1.35))
ax.text(5,2.65,"the spine is prescribed before local branches are chosen",ha='center',fontsize=9)
save(fig,"08_common_spine.pdf")

# 09 separator matrix, drawn with vector cells
fig, ax=plt.subplots(figsize=(6.7,4.8))
M=np.array([[1,1,1],[1,2,3],[2,1,0],[3,0,1]],dtype=float)
ax.set_xlim(0,3); ax.set_ylim(0,4); ax.set_aspect('equal')
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        shade = 0.96 - 0.12 * M[i,j]
        ax.add_patch(Rectangle((j,3-i),1,1,facecolor=str(shade),edgecolor='black',linewidth=.7))
        ax.text(j+.5,3-i+.5,str(int(M[i,j])),ha='center',va='center')
ax.set_xticks([.5,1.5,2.5],[r"$W_1$",r"$W_2$",r"$W_3$"])
ax.set_yticks([3.5,2.5,1.5,.5],[r"$v_1$",r"$v_2$",r"$v_3$",r"$v_4$"])
ax.set_xlabel("compatible constituents")
ax.set_ylabel("Frobenius places")
ax.set_title("finite trace separator")
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)
save(fig,"09_frobenius_separator.pdf")

# 10 support components
fig, ax=plt.subplots(figsize=(8.0,4.0))
ax.set_xlim(0,10); ax.set_ylim(0,4); ax.axis("off")
for i,x in enumerate([1.6,4.0,6.4,8.8]):
    ax.add_patch(Circle((x,2.1),.75,fill=False,linewidth=1.2))
    ax.text(x,2.1,rf"$\operatorname{{Spec}}R_{i+1}$",ha='center',va='center')
for x in [1.6,6.4,8.8]:
    ax.add_patch(Circle((x,2.1),.55,fill=False,linewidth=2.6))
ax.text(5,.55,r"thick circles are the occupied components of $\operatorname{Supp}_R(M)$",ha='center')
save(fig,"10_support_components.pdf")

# 11 fitting locus
fig, ax=plt.subplots(figsize=(7.2,4.5))
x=np.linspace(-2,2,400)
y1=x**2
ax.plot(x,y1,linewidth=1.2)
ax.axhline(0,linewidth=.7)
ax.scatter([0],[0],s=28)
ax.text(.12,.18,r"$V(\operatorname{Fitt}_0M)$")
ax.set_xlabel("local coordinate")
ax.set_ylabel("presentation minor")
ax.set_title("occupancy is the vanishing locus of the zeroth Fitting ideal")
ax.grid(True,linewidth=.3)
save(fig,"11_fitting_locus.pdf")

# 12 finite occupancy ranks
fig, ax=plt.subplots(figsize=(7.4,4.3))
conds=np.arange(0,5)
ranks=[5,3,2,1,0]
ax.step(conds,ranks,where='post',linewidth=1.5)
ax.scatter(conds,ranks,s=28)
ax.set_xticks(conds,["none","1","2","3","inconsistent"])
ax.set_xlabel("number of imposed spectral conditions")
ax.set_ylabel("joint packet rank")
ax.set_ylim(-.2,5.5)
ax.grid(True,linewidth=.3)
save(fig,"12_finite_occupancy.pdf")

# 13 tail projections
fig, ax=plt.subplots(figsize=(8.0,4.3))
ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
for n,y in enumerate([4.25,3.25,2.25,1.25],start=1):
    ax.plot([1+n*.35,9],[y,y],linewidth=3.0,solid_capstyle='butt')
    ax.text(.6,y,rf"$\operatorname{{ran}}P_{n}$",va='center')
ax.text(5,.35,r"every finite range is nonzero, but $\bigcap_n\operatorname{ran}P_n=\{0\}$",ha='center')
save(fig,"13_tail_projections.pdf")

# 14 completion dependencies
fig, ax=plt.subplots(figsize=(8.4,5.0))
ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis("off")
box(ax,(.5,4.4),2.1,.75,"vertical branches")
box(ax,(3.0,4.4),2.1,.75,"residual companions")
box(ax,(5.5,4.4),2.1,.75,"common spine")
box(ax,(7.9,4.4),1.6,.75,"carrier")
box(ax,(2.0,2.4),2.3,.75,"compatible system")
box(ax,(5.8,2.4),2.3,.75,"support occupancy")
box(ax,(3.8,.55),2.5,.75,"occupied realization")
for a in [(1.55,4.4),(4.05,4.4),(6.55,4.4)]: arrow(ax,a,(3.15,3.15))
arrow(ax,(8.7,4.4),(6.95,3.15))
arrow(ax,(4.3,2.77),(5.8,2.77))
arrow(ax,(3.15,2.4),(4.7,1.3)); arrow(ax,(6.95,2.4),(5.4,1.3))
ax.text(5,5.65,"the conclusion requires all four input blocks",ha='center',fontsize=10)
save(fig,"14_completion_dependencies.pdf")

print("generated", len(list(OUT.glob('*.pdf'))), "vector figures")

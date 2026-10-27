r"""Exact mathematical diagrams for the LSM theoretical atlas. No empirical data."""
from pathlib import Path
from fractions import Fraction as F
import json
import numpy as np
import matplotlib
matplotlib.use(r'Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Polygon, Ellipse

ROOT=Path(__file__).resolve().parent
OUT=ROOT/r'figures'; OUT.mkdir(exist_ok=True)
INK=r'#253249'; TEAL=r'#146b72'; GOLD=r'#aa7832'; RED=r'#aa5146'; PALE=r'#edf3f4'; GREY=r'#667281'
plt.rcParams.update({r'font.family':r'DejaVu Serif',r'font.size':10,r'mathtext.fontset':r'stix',r'axes.spines.top':False,r'axes.spines.right':False,r'axes.labelcolor':INK,r'text.color':INK,r'xtick.color':GREY,r'ytick.color':GREY,r'axes.edgecolor':r'#aab2bc',r'pdf.fonttype':42,r'savefig.facecolor':r'white'})

def fig(name,w=7.1,h=2.8):
    f,ax=plt.subplots(figsize=(w,h));return f,ax

def save(f,name):
    f.savefig(OUT/(name+r'.pdf'),bbox_inches=r'tight',pad_inches=.13)
    plt.close(f)

def base(ax):ax.set_xlim(0,10);ax.set_ylim(0,4);ax.axis(r'off')
def box(ax,x,y,w,h,label,c=TEAL):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=PALE,edgecolor=c,lw=1.2))
    ax.text(x+w/2,y+h/2,label,ha=r'center',va=r'center',fontsize=11,color=INK)
def arr(ax,p,q,label=r'',color=INK,rad=0):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle=r'-|>',mutation_scale=12,lw=1.2,color=color,connectionstyle=f'arc3,rad={rad}'))
    if label:
        ax.text((p[0]+q[0])/2,(p[1]+q[1])/2+.17,label,ha=r'center',va=r'bottom',fontsize=10,color=color)

# A compact, typed architecture: different contracts share one underlying object.
f,ax=fig(r'00_architecture',h=2.7);base(ax)
box(ax,.1,2.65,2.15,.75,r'Observation $x\in X$')
box(ax,3.9,2.65,2.15,.75,r'Archive $c\in\mathcal{C}$')
box(ax,7.75,2.65,2.15,.75,r'State $z\in Z$')
arr(ax,(2.3,3.05),(3.85,3.05),r'analysis $A$')
arr(ax,(6.1,3.05),(7.7,3.05),r'summary $\gamma S$')
box(ax,.1,.45,2.15,.75,r'Transition $F_u x$')
box(ax,3.9,.45,2.15,.75,r'Realization $A F_u x$')
box(ax,7.75,.45,2.15,.75,r'Prediction $\bar F_u z$')
arr(ax,(1.15,2.55),(1.15,1.3),r'$F_u$',TEAL)
arr(ax,(4.95,2.55),(4.95,1.3),r'$F_{u,A}$',TEAL)
arr(ax,(8.8,2.55),(8.8,1.3),r'$\bar F_u$',TEAL)
arr(ax,(2.3,.85),(3.85,.85),r'$A$')
arr(ax,(6.1,.85),(7.7,.85),r'$\gamma S$')
ax.text(5,-.05,r'Left square: coordinate consistency.   Right square: predictive closure.',ha=r'center',fontsize=10)
save(f,r'00_architecture')

# Redundant coefficient plane and an oblique consistency projector.
f=plt.figure(figsize=(7.1,3.1));ax=f.add_subplot(111,projection=r'3d')
a,b=np.meshgrid(np.linspace(-.7,1.6,10),np.linspace(-.5,1.3,10))
ax.plot_surface(a,b,a+b,alpha=.17,color=TEAL,linewidth=0)
q=np.array([1,.35,1.95]);pq=np.array([1,.35,1.35]);ax.scatter(*q,color=RED,s=34);ax.scatter(*pq,color=TEAL,s=34)
ax.plot(*np.array([q,pq]).T,color=RED,lw=1.7)
ax.text(*q,r'  $c$',color=RED);ax.text(*pq,r'  $\Pi c$',color=TEAL)
ax.set(xlabel=r'$c_1$',ylabel=r'$c_2$',zlabel=r'$c_3$');ax.view_init(22,-58)
ax.set_box_aspect((1,1,1));ax.grid(False);f.subplots_adjust(left=0,right=.95,bottom=.05,top=1)
save(f,r'01_consistency')

f,ax=fig(r'02_transport',h=2.65);base(ax)
for x,y,label in [(.3,2.7,r'$c_a=A_a x$'),(7.1,2.7,r'$c_b=A_b x$'),(.3,.5,r'$F_a c_a$'),(7.1,.5,r'$F_b c_b$')]:box(ax,x,y,2.6,.8,label)
arr(ax,(3,3.1),(7,3.1),r'$T_{ba}=A_bS_a$')
arr(ax,(3,.9),(7,.9),r'$T_{ba}$')
arr(ax,(1.6,2.6),(1.6,1.4),r'$F_a$');arr(ax,(8.4,2.6),(8.4,1.4),r'$F_b$')
ax.text(5,1.95,r'$F_bT_{ba}=T_{ba}F_a$',ha=r'center',fontsize=16,color=TEAL)
save(f,r'02_transport')

L=np.array([[.5,1],[.25,1/3]])
f,(ax1,ax2)=plt.subplots(1,2,figsize=(7.1,2.8),sharex=True,sharey=True)
ys=np.linspace(-1.3,1.3,40)
for ax in [ax1,ax2]:
    ax.axhline(0,color=r'#cad0d7',lw=.7);ax.axvline(0,color=r'#cad0d7',lw=.7)
    ax.set(xlim=(-1.5,1.5),ylim=(-1.5,1.5),xlabel=r'retained coordinate $y$',ylabel=r'unresolved coordinate $w$')
ax1.plot(np.zeros_like(ys),ys,color=TEAL,lw=2)
ax1.scatter([0,0],[0,1],color=[INK,RED],zorder=5,s=36)
ax1.text(.12,1,r'$x^\prime=(0,1)$',fontsize=10);ax1.text(.12,.03,r'$x=(0,0)$',fontsize=10)
ax1.set_title(r'One summary, two states',fontsize=11)
ax2.plot(ys,ys/3,color=TEAL,lw=2);ax2.scatter([0,1],[0,1/3],color=[INK,RED],s=36,zorder=5)
ax2.text(.22,.65,r'$\gamma Lx^\prime=1$',color=RED);ax2.text(-1.4,-1.25,r'$L(\ker\gamma)\not\subseteq\ker\gamma$',fontsize=12)
ax2.set_title(r'Different next summaries',fontsize=11)
f.tight_layout(w_pad=2);save(f,r'03_fibers')

f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,2.6))
a1.set(xlim=(-.2,1.4),ylim=(-.2,1.4),xlabel=r'first observable coefficient',ylabel=r'second observable coefficient')
a1.axhline(0,color=TEAL,lw=2);a1.arrow(0,0,.5,1,head_width=.05,color=GOLD,length_includes_head=True)
a1.text(.65,.85,r'$CL=(1/2,1)$',fontsize=11);a1.text(.5,.08,r'$W_0=\mathrm{span}\{C\}$',fontsize=10)
a1.set_title(r'Pull back the observable',fontsize=11)
a2.axis(r'off');a2.text(.04,.82,r'$W_0=\mathrm{span}\{(1,0)\}$',fontsize=15)
a2.text(.04,.53,r'$W_1=\mathrm{span}\{(1,0),(1/2,1)\}$',fontsize=14,color=TEAL)
a2.text(.04,.22,r'$W_1=\mathbb{R}^{2\,*}=W_*$',fontsize=16)
f.tight_layout();save(f,r'04_refinement')

f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,2.7))
a1.imshow(L,cmap=r'Blues',vmin=0,vmax=1)
for (i,j),v in np.ndenumerate(L):a1.text(j,i,[[r'$1/2$',r'$1$'],[r'$1/4$',r'$1/3$']][i][j],ha=r'center',va=r'center',fontsize=16,color=r'white' if v>.6 else INK)
a1.set_xticks([0,1],[r'input $P_1$',r'input $P_2$']);a1.set_yticks([0,1],[r'output $P_1$',r'output $P_2$']);a1.set_title(r'Linear transfer blocks $P_jLP_i$',fontsize=11)
u=1.;v=np.linspace(0,.4,100);a2.plot(v,2*u*v,color=RED,label=r'mixed term $2uv$',lw=2);a2.plot(v,v*v,color=TEAL,label=r'packet square $v^2$',lw=2)
a2.set(xlabel=r'omitted amplitude $v$ with $u=1$',ylabel=r'contribution to $(u+v)^2$');a2.legend(frameon=False,fontsize=9,loc=r'upper left');a2.set_title(r'Nonlinear influence has a cross term',fontsize=11)
f.tight_layout(w_pad=2.5);save(f,r'05_packets')

f,ax=fig(r'06_return_path',h=2.2);base(ax)
box(ax,.1,1.3,2.25,1.05,'Retained\n$Pe_1=e_1$')
box(ax,3.85,1.3,2.25,1.05,'Unresolved\n$Qe_2=e_2$',GOLD)
box(ax,7.6,1.3,2.25,1.05,'Retained\n$Pe_1=e_1$')
arr(ax,(2.5,1.85),(3.7,1.85),r'$M$',GOLD);arr(ax,(6.25,1.85),(7.45,1.85),r'$L$',GOLD)
ax.text(5,.45,r'Separate compression deletes both arrows. Composition retains their return path.',ha=r'center',fontsize=10)
save(f,r'06_return_path')

# Canonical exact rational trajectory, memory coefficients and exact checks.
LF=[[F(1,2),F(1)],[F(1,4),F(1,3)]]
x=[F(1),F(0)];records=[]
for t in range(13):
    records.append([str(x[0]),str(x[1])]);x=[sum(LF[i][j]*x[j] for j in range(2)) for i in range(2)]
y=[F(row[0]) for row in records]
for t in range(11):assert y[t+2]==F(5,6)*y[t+1]+F(1,12)*y[t]
for t in range(12):
    memory=F(1,2)*y[t]+sum(F(1,4)*F(1,3)**j*y[t-1-j] for j in range(t))
    assert y[t+1]==memory
assert y[:5]==[F(1),F(1,2),F(1,2),F(11,24),F(61,144)]
(OUT/r'exact_example.json').write_text(json.dumps({r'matrix':[[str(x) for x in row] for row in LF],r'initial_state':[r'1',r'0'],r'trajectory':records,r'checked_recurrence_steps':11,r'checked_memory_steps':12,r'probability_data':False},indent=2)+'\n')
f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,2.65))
j=np.arange(8);a1.stem(j,.25*(1/3.)**j,linefmt=TEAL,markerfmt=r'o',basefmt=r' ');a1.set(xlabel=r'lag $j$',ylabel=r'$K_j=(1/4)(1/3)^j$');a1.set_title(r'Exact projected memory kernel',fontsize=11)
t=np.arange(13);a2.plot(t,[float(x) for x in y],r'-o',color=TEAL,ms=4,label=r'exact dynamics / full memory')
a2.plot(t,.5**t,r'--',color=RED,label=r'one-coordinate compression')
a2.set(xlabel=r'step $t$',ylabel=r'resolved output $y_t$');a2.legend(frameon=False,fontsize=8.5);a2.set_title(r'The lost history changes prediction',fontsize=11)
f.tight_layout(w_pad=2);save(f,r'07_memory')

f,ax=fig(r'08_defect',h=2.7)
t=np.arange(21);delta=.02
for rho,col,lab in [(.7,TEAL,r'$\rho=0.7$'),(1,GOLD,r'$\rho=1$'),(1.08,RED,r'$\rho=1.08$')]:
    bound=delta*t if rho==1 else delta*(rho**t-1)/(rho-1)
    ax.plot(t,bound,lw=2,color=col,label=lab)
ax.set(xlabel=r'composition length $T$',ylabel=r'propagated upper bound');ax.legend(frameon=False,loc=r'upper left');ax.text(.98,.02,r'Analytical bounds with $e_0=0$, $\delta_t=0.02$',transform=ax.transAxes,ha=r'right',fontsize=9,color=GREY)
f.tight_layout();save(f,r'08_defect')

f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,2.65))
zm=np.array([[1,.5],[.5,.5]]);zp=np.array([[.5,.5],[.5,11/24]])
a1.scatter(zm[0],zm[1],color=TEAL,s=55);a1.scatter(zp[0],zp[1],color=GOLD,s=45)
for i in range(2):arr(a1,zm[:,i],zp[:,i],color=TEAL)
a1.set(xlim=(.2,1.12),ylim=(.2,.7),xlabel=r'$y_{t-1}$',ylabel=r'$y_t$');a1.set_title(r'Two independent history states',fontsize=11)
a2.axis(r'off');a2.text(.02,.84,r'Input and successor windows',fontsize=16)
a2.text(.02,.49,r'$\det Z_-=1/4$',fontsize=16,color=TEAL)
a2.text(.02,.15,r'$D_2=Z_+Z_-^{-1}$',fontsize=16)
f.tight_layout(w_pad=3);save(f,r'09_identification')

f,ax=fig(r'10_domain',h=2.65);base(ax)
box(ax,.05,1.3,2.2,1,r'$z\in K$'+'\n'+r'$\lambda z=1$')
box(ax,3.8,1.3,2.4,1,r'$B_o z\in C$'+'\nunnormalized')
box(ax,7.75,1.3,2.2,1,r'$z_o\in K$'+'\nposterior')
arr(ax,(2.4,1.8),(3.65,1.8),r'$B_o$')
arr(ax,(6.35,1.8),(7.6,1.8),r'$/(\lambda B_o z)$')
ax.text(5,.45,r'$p_o=\lambda B_o z\geq0,\qquad\sum_o p_o=1$',ha=r'center',fontsize=15,color=TEAL)
ax.text(5,3.25,r'Cone preservation gives positivity. The mass identity gives normalization.',ha=r'center',fontsize=10)
save(f,r'10_domain')

f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,3))
theta=np.linspace(0,2*np.pi,300);a1.fill(np.cos(theta),np.sin(theta),facecolor=PALE,edgecolor=TEAL,lw=1.5)
R=np.array([[3/5,-4/5],[4/5,3/5]]);v=np.array([1.,0]);points=[]
for _ in range(18):points.append(v.copy());v=R@v
points=np.array(points);a1.plot(points[:,0],points[:,1],r'-o',color=GOLD,ms=3,lw=.8)
a1.set(xlabel=r'$x$',ylabel=r'$y$',aspect=r'equal',xlim=(-1.17,1.17),ylim=(-1.17,1.17));a1.set_title(r'Normalized Lorentz slice: a disk',fontsize=11)
a2.axis(r'off');a2.text(.05,.8,r'$m\geq\sqrt{x^2+y^2}$',fontsize=18,color=TEAL)
a2.text(.05,.53,r'$\det J=(m^2-x^2-y^2)/4$',fontsize=17)
a2.text(.05,.2,r'$\lambda_{\pm}(J)=(m\pm\sqrt{x^2+y^2})/2$',fontsize=15)
f.tight_layout(w_pad=2);save(f,r'11_psd')

f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,2.65))
u=np.linspace(-1,1,200);a1.plot(u,u*u,color=TEAL,lw=2,label=r'$u^2$');a1.scatter([0],[0],color=RED,s=42,zorder=5)
a1.axhline(1/3,color=GOLD,lw=1.5,ls=r'--',label=r'$\mathbb{E}[U^2]=1/3$');a1.set(xlabel=r'$u$ under uniform $[-1,1]$',ylabel=r'quadratic contribution');a1.legend(frameon=False,fontsize=9)
a2.axis(r'off');a2.text(.03,.82,r'$\bar K=\mathbb{E}[K(U)]$',fontsize=15)
a2.text(.03,.51,r'$\mathbb{E}[KXK^{\mathsf{T}}]-\bar KX\bar K^{\mathsf{T}}$',fontsize=15,color=TEAL)
a2.text(.03,.2,r'$=\mathrm{Var}(U)\,K_1XK_1^{\mathsf{T}}$',fontsize=15)
f.tight_layout(w_pad=2);save(f,r'12_covariance')

f=plt.figure(figsize=(7.1,3.1));a1=f.add_subplot(121);a2=f.add_subplot(122,projection=r'3d')
u=np.linspace(-1,1,200);a1.fill_between(u,u*u,1,color=PALE);a1.plot(u,u*u,color=TEAL,lw=2);a1.plot([-1,1],[1,1],color=TEAL,lw=1.3);a1.scatter([-.7,.3],[.49,.09],color=GOLD,s=32);a1.set(xlabel=r'first moment $x$',ylabel=r'second moment $y$',ylim=(-.05,1.08));a1.set_title(r'Normalized slice $x^2\leq y\leq1$',fontsize=11)
for m in np.linspace(.18,1,6):a2.plot(np.full_like(u,m),m*u,m*u*u,color=TEAL,lw=.65);a2.plot([m,m],[-m,m],[m,m],color=TEAL,lw=.5)
for v in np.linspace(-1,1,9):
    m=np.linspace(0,1,50);a2.plot(m,m*v,m*v*v,color=TEAL,lw=.5)
a2.set(xlabel=r'$m$',ylabel=r'$x$',zlabel=r'$y$');a2.view_init(22,-57);a2.set_title(r'Homogeneous moment cone',fontsize=11);a2.grid(False)
f.subplots_adjust(left=.08,right=.96,bottom=.17,top=.88,wspace=.28);save(f,r'13_moments')

f,(a1,a2)=plt.subplots(1,2,figsize=(7.1,2.7))
a1.add_patch(Polygon([(1,0),(0,1),(-1,0),(0,-1)],facecolor=PALE,edgecolor=TEAL,lw=1.5))
a1.add_patch(Rectangle((.1,-.16),.24,.28,edgecolor=GOLD,facecolor=r'#e9d8b6',alpha=.8,lw=1.3));a1.scatter([.22],[-.02],color=GOLD,s=30)
a1.set(xlim=(-1.1,1.1),ylim=(-1.1,1.1),aspect=r'equal',xlabel=r'$a$',ylabel=r'$b$');a1.set_title(r'A whole parameter set is certified',fontsize=11)
a2.axis(r'off');a2.text(.02,.85,r'$p_{a,b}(u\mid x,y)$',fontsize=17)
a2.text(.02,.64,r'$=1+axu+byL_2(u)$',fontsize=16)
a2.text(.02,.35,r'$\inf p\geq1-\sup_{(a,b)\in\Theta}(|a|+|b|)$',fontsize=14,color=TEAL)
a2.text(.02,.07,r'Schematic set inclusion, not observed confidence coverage.',fontsize=8.5,color=GREY)
f.tight_layout(w_pad=2);save(f,r'14_uncertainty')

f,ax=fig(r'15_horizons',h=2.75)
t=np.arange(0,51);Delta=1/50;rho=1/4
ax.plot(t,np.minimum(1,t*Delta),color=GOLD,lw=2,label=r'full-record bound $\min(1,T\Delta)$')
ax.plot(t,Delta*(1-(1-rho)**t)/rho,color=TEAL,lw=2,label=r'one-time bound $\Delta[1-(1-\rho)^t]/\rho$')
ax.axhline(Delta/rho,color=TEAL,ls=r':',lw=1)
ax.set(xlabel=r'future length / time $T$',ylabel=r'total variation upper bound',ylim=(0,1.04));ax.legend(frameon=False,fontsize=9,loc=r'upper left');ax.text(.98,.15,r'Analytical illustration: $\Delta=1/50$, $\rho=1/4$, $e_0=0$',transform=ax.transAxes,ha=r'right',fontsize=9,color=GREY)
f.tight_layout();save(f,r'15_horizons')
print(json.dumps({r'figures':len(list(OUT.glob(r'*.pdf'))),r'exact_arithmetic_checks':r'passed',r'empirical_claims':False}))

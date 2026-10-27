#!/usr/bin/env python3
"""Reproducible mathematical plates for the Komorebi Space monograph.

Each chart is its own figure. Numerical curves evaluate the printed formulas.
No generative images, chart themes, or custom chart colors are used. The PDFs
embed fonts, but no font files are included in the publication package.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'source/figures/generated'
OUT.mkdir(exist_ok=True,parents=True)
plt.rcParams.update({'font.family':'serif','font.serif':['STIXGeneral','DejaVu Serif'],
                     'mathtext.fontset':'stix','font.size':11,'axes.labelsize':11,
                     'axes.titlesize':12,'legend.fontsize':10,
                     'pdf.fonttype':42,'ps.fonttype':42,'savefig.dpi':220})
RECORDS=[]

def clean(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out',length=3)
    ax.grid(True,alpha=.18,linewidth=.6)


def save(fig,name,model,parameters):
    fig.canvas.draw()
    for extension in ['pdf','png']:
        fig.savefig(OUT/f'{name}.{extension}',bbox_inches=None if name in {'11_nested_projection_3d','15_protected_geometry'} else 'tight',pad_inches=.13)
    p=OUT/f'{name}.pdf'
    RECORDS.append({'asset':name,'model':model,'parameters':parameters,
                    'pdf_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                    'source':'checks/build_figures.py','rendering':'matplotlib vector PDF; raster preview'})
    plt.close(fig)

# 10: honest axes and one unambiguous mathematical chart.
fig,ax=plt.subplots(figsize=(6.5,3.6))
n=2**np.arange(0,9)
ax.plot(n,np.ones_like(n),marker='s',linewidth=1.8,label=r'Distance to $\ker D$: $1$')
ax.plot(n,1/n,marker='o',linewidth=1.8,label=r'Residual: $1/n$')
ax.set_xscale('log',base=2);ax.set_xticks(n,labels=[str(i) for i in n])
ax.set_ylim(-.02,1.16);ax.set_yticks([0,.25,.5,.75,1])
ax.set_xlabel(r'Basis index $n$ (logarithmic spacing)');ax.set_ylabel('Norm')
ax.legend(loc='upper center',bbox_to_anchor=(.5,1.22),ncol=2,frameon=False)
clean(ax)
save(fig,'10_closed_range_plot',r'De_n=e_n/n on l2; ker D=0',{'n':n.tolist(),'distance':1,'residual':'1/n'})

# 11: genuine 3-D nested projection with a nonzero first and second error.
fig=plt.figure(figsize=(6.6,4.1));ax=fig.add_axes([-.04,.02,.79,.94],projection='3d')
g=np.linspace(-.3,3.2,2);X,Y=np.meshgrid(g,g)
ax.plot_surface(X,Y,np.zeros_like(X),alpha=.14,linewidth=.4)
ax.plot([-.3,3.2],[0,0],[0,0],linewidth=2.3,label=r'$M=\ker D\cap\ker C$')
x=np.array([2.,2.,3.]);local=np.array([2.,2.,0.]);joint=np.array([2.,0.,0.])
ax.plot([x[0],local[0]],[x[1],local[1]],[x[2],local[2]],marker='o',linewidth=2.1,label=r'Local error $u$: length $3$')
ax.plot([local[0],joint[0]],[local[1],joint[1]],[local[2],joint[2]],marker='s',linewidth=2.1,label=r'Matching error $v$: length $2$')
ax.plot([x[0],joint[0]],[x[1],joint[1]],[x[2],joint[2]],'--',linewidth=1.2)
ax.text(2.08,2.08,3.15,r'$x=(2,2,3)$',fontsize=11)
ax.text(2.08,2.2,-.2,r'$P_Lx$',fontsize=11)
ax.text(2.15,-.48,-.1,r'$Px$',fontsize=11)
ax.text(-.35,1.65,.08,r'$L=\ker D$',fontsize=11)
ax.plot([2,2,2],[1.75,1.75,2],[0,.25,.25],linewidth=1)
ax.set_xlim(-.5,3.25);ax.set_ylim(-.5,3.25);ax.set_zlim(-.3,3.65)
ax.set_xticks([0,2]);ax.set_yticks([0,2]);ax.set_zticks([0,3])
ax.set_xlabel(r'$x_1$',labelpad=0);ax.set_ylabel(r'$x_2$',labelpad=0);ax.set_zlabel('')
ax.text2D(.94,.61,r'$x_3$',transform=ax.transAxes,fontsize=11)
ax.set_box_aspect((1.25,1,1.05));ax.view_init(elev=23,azim=-62)
ax.text(2.08,2.08,1.55,r'$u$',fontsize=12)
ax.text(2.05,.9,.05,r'$v$',fontsize=12)
fig.text(.71,.78,'First correction',fontsize=11)
fig.text(.71,.72,r'$u=(0,0,3)$',fontsize=12)
fig.text(.71,.59,'Second correction',fontsize=11)
fig.text(.71,.53,r'$v=(0,2,0)$',fontsize=12)
fig.text(.71,.40,r'$u\perp v$',fontsize=12)
fig.text(.71,.29,r'$\|x-Px\|^2$',fontsize=12)
fig.text(.71,.23,r'$=3^2+2^2=13$',fontsize=12)
save(fig,'11_nested_projection_3d',r'L={x3=0}, M={x2=x3=0}',{'x':[2,2,3],'PLx':[2,2,0],'Px':[2,0,0],'error_squared':13})

# 12a: geometry and 12b: norm are separate figures, paired only by LaTeX.
fig,ax=plt.subplots(figsize=(3.25,3.5))
t=.75;b=2
v=np.array([0.,b]);j=np.array([-t*b,b]);q=np.array([-t*b/(1+t*t),b/(1+t*t)])
z=np.linspace(-.3,2.6,100)
ax.plot(np.zeros_like(z),z,':',linewidth=1.6,label=r'$\ker D_0$')
ax.plot(-t*z,z,linewidth=1.8,label=r'$\ker D_t$')
ax.scatter([v[0],j[0],q[0]],[v[1],j[1],q[1]],s=26,zorder=4)
ax.annotate('',xy=j,xytext=v,arrowprops={'arrowstyle':'->','lw':1.2,'linestyle':'--'})
ax.annotate('',xy=q,xytext=v,arrowprops={'arrowstyle':'->','lw':1.2})
ax.annotate(r'$(0,b)$',xy=v,xytext=(8,10),textcoords='offset points')
ax.annotate(r'$J(0,b)$',xy=j,xytext=(-20,11),textcoords='offset points')
ax.annotate(r'$q_t(0,b)$',xy=q,xytext=(-28,-26),textcoords='offset points')
ax.set_aspect('equal');ax.set_xlim(-2,.65);ax.set_ylim(-.25,2.7)
ax.set_xticks([-2,-1,0]);ax.set_yticks([0,1,2]);ax.set_xlabel(r'$x$');ax.set_ylabel(r'$y$')
ax.set_title(r'$t=3/4,\quad b=2$')
ax.legend(loc='lower left',frameon=False,fontsize=9)
clean(ax)
save(fig,'12a_moving_line_geometry',r'D_t(x,y)=x+t y',{'t':'3/4','b':2,'J':['-3/2',2],'q':['-24/25','32/25']})
fig,ax=plt.subplots(figsize=(3.25,3.5))
t=np.linspace(0,2,401)
ax.plot(t,t,linestyle='--',linewidth=1.5,label=r'Bound $t$')
ax.plot(t,t/np.sqrt(1+t*t),linewidth=2,label=r'Exact $t/\sqrt{1+t^2}$')
ax.set_xlim(0,2.02);ax.set_ylim(0,2.15);ax.set_xticks([0,1,2]);ax.set_yticks([0,.5,1,1.5,2])
ax.set_xlabel(r'$t\geq 0$');ax.set_ylabel(r'$\|q_t-q_0\|$')
ax.legend(loc='upper left',frameon=False,fontsize=9)
clean(ax)
save(fig,'12b_moving_line_norm',r'projector difference norm = abs(t)/sqrt(1+t^2)',{'t_interval':[0,2],'samples':401})

# 15: the protected and unconstrained problems are both visibly exact.
fig,ax=plt.subplots(figsize=(6.35,4.0))
z=np.linspace(-.3,3,100)
ax.plot(z,z,linewidth=1.8,label=r'Exact space $x_1=x_2$')
ax.plot([2,2],[-.3,2.85],':',linewidth=1.4,label=r'Protected slice $x_1=2$')
raw=np.array([2.,0.]);ordinary=np.array([1.,1.]);protected=np.array([2.,2.])
ax.scatter([2,1,2],[0,1,2],s=40,zorder=4)
ax.annotate('',xy=ordinary,xytext=raw,arrowprops={'arrowstyle':'->','lw':1.5})
ax.annotate('',xy=protected,xytext=raw,arrowprops={'arrowstyle':'->','lw':1.5,'linestyle':'--'})
ax.annotate(r'Raw $(2,0)$',xy=raw,xytext=(13,-18),textcoords='offset points')
ax.annotate(r'Nearest $(1,1)$',xy=ordinary,xytext=(-82,0),textcoords='offset points')
ax.annotate(r'Protected $(2,2)$',xy=protected,xytext=(13,4),textcoords='offset points')
ax.plot([1.12,1.24,1.12],[.88,1.,1.12],linewidth=.8)
ax.set_aspect('equal');ax.set_xlim(-.4,3.1);ax.set_ylim(-.35,3.1)
ax.set_xticks([0,1,2,3]);ax.set_yticks([0,1,2,3]);ax.set_xlabel(r'$x_1$');ax.set_ylabel(r'$x_2$')
ax.legend(loc='upper left',frameon=False,fontsize=10)
clean(ax)
save(fig,'15_protected_geometry',r'D=x1-x2; protected first and third coordinates',{'raw':[2,0,5],'ordinary':[1,1,5],'protected':[2,2,5],'squared_errors':[2,4]})

# 16: a discrete support diagram with coordinate and depth clearly separated.
fig,ax=plt.subplots(figsize=(6.7,3.05))
allowed=[(k,N) for N in range(5) for k in range(16) if (k+1)%2**N==0]
recovered=[(k,N) for N in range(5) for k in range(16) if (k+1)%2**N!=0]
ax.plot([a[0] for a in allowed],[a[1] for a in allowed],'s',markersize=10,linestyle='none',label='May survive')
ax.plot([a[0] for a in recovered],[a[1] for a in recovered],'s',markersize=10,linestyle='none',markerfacecolor='none',label='Guaranteed zero')
ax.set_xlim(-.65,15.65);ax.set_ylim(4.5,-.5)
ax.set_xticks(range(16));ax.set_yticks(range(5));ax.tick_params(axis='x',labelsize=9)
ax.set_xlabel(r'Original coordinate $k$');ax.set_ylabel(r'Coarsening depth $N$')
ax.legend(loc='upper center',bbox_to_anchor=(.5,1.19),ncol=2,frameon=False)
ax.spines[['top','right','bottom','left']].set_visible(False)
ax.tick_params(length=0)
save(fig,'16_dyadic_support',r'Q_N support allowed only if 2^N divides k+1',{'depths':list(range(5)),'coordinates':list(range(16))})

# 17: flatness versus measured transport amplification.
fig,ax=plt.subplots(figsize=(6.4,3.7))
n=np.arange(1,9)
ax.plot(n,2.0**n-1,marker='o',linewidth=1.8,label=r'Repair error $2^n-1$')
ax.plot(n,n,linestyle='--',marker='s',linewidth=1.5,label=r'Route length $n$')
ax.plot(n,np.ones_like(n),linestyle=':',linewidth=1.8,label='Measured residual 1')
ax.set_yscale('log',base=2);ax.set_yticks(2**np.arange(9),labels=[str(2**i) for i in range(9)])
ax.set_xticks(n);ax.set_ylim(.85,320)
ax.set_xlabel(r'Number of edges $n$');ax.set_ylabel('Norm or comparison value (log scale)')
ax.legend(loc='upper left',frameon=False);clean(ax)
save(fig,'17_amplification',r'x_i=8*2^i-1; repaired y_i=7*2^i; two orientations measured',{'n':n.tolist(),'edge_residual_norm':1,'repair_error':'2^n-1'})

# 18: stable line motion versus rank-changing diagonal motion.
fig,ax=plt.subplots(figsize=(6.4,3.6))
eps=2.0**(-np.linspace(0,8,401))
ax.plot(eps,np.ones_like(eps),linewidth=1.8,label=r'Rank-changing pair: gap $1$')
ax.plot(eps,eps/np.sqrt(1+eps*eps),linewidth=1.8,label=r'Moving line: gap $\varepsilon/\sqrt{1+\varepsilon^2}$')
ax.plot(eps,eps,'--',linewidth=1.3,label=r'Operator change $\varepsilon$')
ax.set_xscale('log',base=2);ax.set_xlim(1,1/256)
ax.set_xticks([1,1/4,1/16,1/64,1/256],labels=['1','1/4','1/16','1/64','1/256'])
ax.set_ylim(-.02,1.12);ax.set_yticks([0,.25,.5,.75,1])
ax.set_xlabel(r'Operator-change norm $\varepsilon$ (smaller to the right)');ax.set_ylabel('Exact-projector gap')
ax.legend(loc='center right',frameon=False,fontsize=10);clean(ax)
save(fig,'18_rank_loss',r'stable [1,t] versus unstable diag(1,t), each compared to its t=0 operator',{'epsilon_range':['1/256',1],'samples':401})

(ROOT/'data/figure_manifest.json').write_text(json.dumps({'assets':RECORDS,'chart_color_policy':'matplotlib default cycles; no custom palette','font_files_distributed':False},indent=2)+'\n')
print(f'Built {len(RECORDS)} independent mathematical plots, PDF and PNG.')

#!/usr/bin/env python3
"""Six reproducible vector plates for the expanded monograph.
Each plate is one figure with one axes. Values come from explicit formulas.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'source/figures/generated';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':11,
                     'axes.labelsize':11,'legend.fontsize':10,'pdf.fonttype':42,'ps.fonttype':42})
records=[]
def save(fig,name,model):
    path=OUT/f'{name}.pdf'
    fig.savefig(path,bbox_inches='tight',pad_inches=.16,metadata={'Creator':'Komorebi Space 1.3.0 / Matplotlib','CreationDate':None,'ModDate':None})
    fig.savefig(OUT/f'{name}.png',dpi=160,bbox_inches='tight',pad_inches=.16)
    (ROOT/'source/figures'/f'{name}.tex').write_text('\\includegraphics[width=15cm]{figures/generated/'+name+'.pdf}\n')
    records.append({'name':name,'formula':model,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)

fig,ax=plt.subplots(figsize=(8.1,3.1))
ax.set_xlim(-7.3,6.0);ax.set_ylim(-.7,2.0);ax.axis('off')
ax.text(-.1,1.8,r'Initial seed $(7,0)$: every middle value is locally coherent',ha='center',va='top',fontsize=12)
ax.text(-6.0,1.05,'Middle\nvalue $m$',ha='right',va='center')
ax.text(-6.0,0,'Fine\nvalue $n$',ha='right',va='center')
for m in range(-5,6):
    ax.plot([m],[1.0],marker='o' if m%2==0 else 'x',markersize=7,linestyle='None')
    ax.text(m,1.28,str(m),ha='center',va='bottom')
    if m%2==0:
        ax.annotate('',xy=(m,.12),xytext=(m,.86),arrowprops={'arrowstyle':'->','lw':1.0})
        ax.plot([m],[0],marker='s',markersize=5,linestyle='None')
        ax.text(m,-.22,str(m//2),ha='center',va='top')
ax.text(0,-.55,r'An integer preimage exists exactly when $m=2n$.',ha='center')
save(fig,'19_branches','Initial 7; middle m from -5 to 5; fine preimage n=m/2 only for even m.')

fig,ax=plt.subplots(figsize=(7.6,3.6))
n=np.arange(10);raw=np.array([2,0,4,1,6,3,8,2,9,4]);env=np.maximum.accumulate(raw)
ax.plot(n,raw,'o--',label=r'Original witnesses $k_n$',lw=1.2)
ax.step(n,env,where='post',label=r'Monotone envelope $\phi(n)$',lw=1.7)
ax.plot(n,env,'s',ms=4)
ax.set(xlabel='Output level $n$',ylabel='Required input level',xticks=n,yticks=np.arange(0,11,2),ylim=(-.4,10.3))
ax.legend(loc='lower right',frameon=False);ax.grid(axis='y',alpha=.2)
save(fig,'20_schedule','k=[2,0,4,1,6,3,8,2,9,4]; phi(n)=max_{j<=n} k[j].')

fig,ax=plt.subplots(figsize=(7.5,3.6))
ax.set_xlim(-.7,3.25);ax.set_ylim(-.55,1.55)
ax.axhline(0,lw=.8);ax.axvline(0,lw=.8)
ax.plot([0,2,2],[1,1,0],'o-',lw=1.5,label='Change, then repair')
ax.plot([0,0],[1,0],'s--',lw=1.5,label='Repair, then change')
for pos,label,offset in [((0,1),r'$x=(0,1)$',(-.12,.2)),((2,1),r'$S_2x=(2,1)$',(.1,.13)),((2,0),r'$(2,0)$',(.12,-.22)),((0,0),r'$(0,0)$',(-.5,-.22))]:
    ax.text(pos[0]+offset[0],pos[1]+offset[1],label)
ax.annotate('',xy=(2,-.22),xytext=(.1,-.22),arrowprops={'arrowstyle':'<->','lw':.9})
ax.text(1.05,-.43,r'Mismatch $(2,0)$',ha='center')
ax.set_xlabel('Chosen exact coordinate $u$');ax.set_ylabel('Residual coordinate $r$')
ax.set_xticks([0,1,2,3]);ax.set_yticks([0,.5,1]);ax.legend(loc='upper right',bbox_to_anchor=(1.0,-.13),ncol=2,frameon=False)
save(fig,'21_mismatch','d(u,r)=r; section (0,r); shear S_2(u,r)=(u+2r,r); x=(0,1).')

fig,ax=plt.subplots(figsize=(7.4,3.5))
t=np.linspace(0,.95,200)
ax.plot(t,1/(1-t),lw=1.8,label=r'Exact gain $(1-t)^{-1}$')
pts=np.array([0,.25,.5,.75,.9]);ax.plot(pts,1/(1-pts),'o',ms=4)
ax.axvline(1,ls='--',lw=.9)
ax.text(1.018,12,'Excluded endpoint',rotation=90,ha='left',va='center')
ax.set(xlim=(-.03,1.1),ylim=(0,21),xlabel='Relative operator-error budget $t$',ylabel='Residual gain',xticks=[0,.25,.5,.75,1],yticks=[0,1,5,10,15,20])
ax.legend(loc='upper left',frameon=False);ax.grid(axis='y',alpha=.18)
save(fig,'22_gain_budget','D(a,b)=a, changed D_t=(1-t)a; exact gain 1/(1-t), 0<=t<1.')

fig,ax=plt.subplots(figsize=(7.6,3.5))
i=np.arange(5);anchor=np.array([0,.75,.5,.25,0]);mean=anchor-.375
ax.plot(i,anchor,'o-',lw=1.6,label='Anchor zero')
ax.plot(i,mean,'s--',lw=1.6,label='Mean zero')
ax.set(xlabel='Vertex index (4 repeats vertex 0)',ylabel='Signal value',xticks=i,yticks=[-.375,0,.25,.5,.75],ylim=(-.5,.92))
ax.set_yticklabels([r'$-3/8$','$0$',r'$1/4$',r'$1/2$',r'$3/4$'])
ax.legend(loc='upper right',frameon=False);ax.grid(axis='y',alpha=.2)
save(fig,'23_cycle_primitive','Repaired differences (3/4,-1/4,-1/4,-1/4); anchor primitive (0,3/4,1/2,1/4); mean shift -3/8.')

fig,ax=plt.subplots(figsize=(7.7,3.6));ax.axis('off')
pos=[(-1.8,1.0),(1.5,1.0),(-.15,-1.3)]
for i,(x,y) in enumerate(pos):
    ax.plot(x,y,'o',markersize=12)
    ax.text(x,y+.3 if i<2 else y-.35,f'View {i}',ha='center',va='center',fontsize=12)
for a,b in [(0,1),(1,2),(2,0)]:
    x,y=pos[a];u,v=pos[b];dx,dy=u-x,v-y
    ax.annotate('',xy=(u-.08*dx,v-.08*dy),xytext=(x+.08*dx,y+.08*dy),arrowprops={'arrowstyle':'->','lw':1.2})
ax.text(-.15,1.13,r'$I$',ha='center',va='bottom',fontsize=14)
ax.text(.95,-.3,r'$I$',ha='left',fontsize=14)
ax.text(-1.33,-.36,r'$J$',ha='right',fontsize=14)
ax.text(2.2,.6,r'$J(a,b)=(a,-b)$',fontsize=13)
ax.text(2.2,-.05,r'$\mathrm{Fix}(J)=\{(a,0)\}$',fontsize=13)
ax.text(2.2,-.85,'Exact family:\n$(a,0)$ at every view',fontsize=12,linespacing=1.5)
ax.set_xlim(-2.55,5.1);ax.set_ylim(-2.0,1.8)
save(fig,'24_reflection_cycle','Triangle with identity tree edges and reflection J=diag(1,-1) on the closing edge; fixed anchors (a,0).')
(ROOT/'audit/expansion/figures.json').write_text(json.dumps({'status':'PASS','plates':records,'standalone_font_files_distributed':False},indent=2)+'\n')
print(f'Generated {len(records)} vector plates.')

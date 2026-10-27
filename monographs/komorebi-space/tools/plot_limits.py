#!/usr/bin/env python3
"""Six vector plates with one axes per figure and explicit mathematical models."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/figure_reports').mkdir(parents=True,exist_ok=True)
OUT=ROOT/'source/figures/generated';OUT.mkdir(exist_ok=True,parents=True)
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':11,
                     'axes.labelsize':12,'legend.fontsize':10,'pdf.fonttype':42,'ps.fonttype':42})
records=[]
def save(fig,name,model):
    p=OUT/(name+'.pdf')
    fig.savefig(p,bbox_inches='tight',pad_inches=.17,metadata={'Creator':'Komorebi Space / Matplotlib','CreationDate':None,'ModDate':None})
    fig.savefig(OUT/(name+'.png'),dpi=170,bbox_inches='tight',pad_inches=.17)
    (ROOT/'source/figures'/(name+'.tex')).write_text('\\includegraphics[width=15cm]{figures/generated/'+name+'.pdf}\n')
    records.append({'name':name,'model':model,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    plt.close(fig)

n=np.arange(0,21,dtype=float)
fig,ax=plt.subplots(figsize=(7.7,3.7))
ax.plot(n,1/(n+1),'o-',lw=1.5,ms=4,label=r'Residual and exact tail $1/(n+1)$')
ax.plot(n,1/((n+1)*(n+2)),'s--',lw=1.3,ms=3,label=r'One-step movement $1/((n+1)(n+2))$')
ax.set_yscale('log');ax.set(xlabel='Iteration $n$',ylabel='Size (logarithmic scale)',xticks=[0,4,8,12,16,20])
ax.legend(frameon=False,loc='upper right');ax.grid(axis='y',which='major',alpha=.18)
save(fig,'25_summable_path','f_n=(s,1/(n+1)); maximum-norm movement=1/((n+1)(n+2)); exact distance to limit=1/(n+1).')

n=np.arange(0,17);Q=4.0**(-(n//2))*np.where(n%2==0,1.0,2.0)
fig,ax=plt.subplots(figsize=(7.7,3.5))
ax.plot(n,Q,'o-',lw=1.4,ms=4,label=r'Full residual $Q_n$')
ax.plot(n[n%2==0],Q[n%2==0],'s--',ms=4,lw=1.1,label=r'Even steps: $Q_{2k}=4^{-k}$')
ax.set_yscale('log');ax.set(xlabel='Iteration $n$',ylabel='Residual (logarithmic scale)',xticks=np.arange(0,17,2))
ax.legend(frameon=False,loc='upper right');ax.grid(axis='y',alpha=.18)
save(fig,'26_residual_bursts','q_even=2; q_odd=1/8; Q_even=4^-k; Q_odd=2*4^-k; finite plotted n=0..16.')

fig,ax=plt.subplots(figsize=(7.6,3.7))
r=2.0**(-np.arange(0,7))
for a,mark,style in [(-1,'o','-'),(0,'s','--'),(1,'^','-.')]:
    ax.plot(r,a*(1-r),marker=mark,ls=style,lw=1.3,ms=4,label=rf'$a={a}$')
    ax.plot([0],[a],marker=mark,ms=7,ls='None',fillstyle='none')
ax.axvline(0,lw=.7,ls=':')
ax.annotate('Common start',xy=(1,0),xytext=(.62,.42),arrowprops={'arrowstyle':'->','lw':.8})
ax.text(.025,1.04,'Exact limits',ha='left',va='bottom')
ax.set(xlabel='Residual coordinate $r$',ylabel='Unprotected coordinate $u$',xlim=(-.06,1.08),ylim=(-1.18,1.24),xticks=[0,.25,.5,.75,1],yticks=[-1,-.5,0,.5,1])
ax.legend(frameon=False,loc='lower right');ax.grid(axis='y',alpha=.15)
save(fig,'27_path_limits','Paths (s,a*(1-2^-n),2^-n), a=-1,0,1, n=0..6; open endpoint markers are exact limits at r=0.')

N=np.unique(np.rint(np.geomspace(1,128,100)).astype(int))
fig,ax=plt.subplots(figsize=(7.7,3.7))
ax.plot(N,N,'o-',ms=3,lw=1.4,label=r'Squared correction norm $N$')
ax.plot(N,1/N,'--',lw=1.2,label=r'Residual square upper bound $1/N$')
ax.plot(N,1/(N+1),':',lw=1.4,label=r'Residual square lower bound $1/(N+1)$')
ax.fill_between(N,1/(N+1),1/N,alpha=.16)
ax.set_xscale('log',base=2);ax.set_yscale('log')
ax.set(xlabel='Number of exactly repaired coordinates $N$',ylabel='Squared size (logarithmic scale)',xticks=[1,2,4,8,16,32,64,128])
ax.set_xticklabels(['1','2','4','8','16','32','64','128'])
ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.19),ncol=1)
ax.grid(axis='y',alpha=.18)
save(fig,'28_escaping_repair','Squared correction=N; infinite residual square between 1/(N+1) and 1/N. Band is certified inequality, not an evaluated infinite tail.')

fig,ax=plt.subplots(figsize=(7.6,3.65));ax.axis('off')
pos={'A':(0,0),'B':(2.4,1.15),'C':(2.4,-1.15),'D':(5.1,0)}
for label,(x,y) in pos.items():
    ax.text(x,y,label,ha='center',va='center',fontsize=18,
            bbox={'boxstyle':'circle,pad=.34','fill':False,'lw':1.0})
edges=[('A','B',0,(1.88,.28)),('B','A',0,(1.04,1.08)),
       ('A','C',2,(.98,-1.11)),('C','A',5,(1.88,-.28))]
for left,right,cost,(tx,ty) in edges:
    ax.annotate('',xy=pos[right],xytext=pos[left],
                arrowprops={'arrowstyle':'-|>','connectionstyle':'arc3,rad=.19',
                            'shrinkA':23,'shrinkB':23,'lw':1.35})
    ax.text(tx,ty,str(cost),ha='center',va='center',fontsize=14)
ax.text(5.1,-.62,'isolated',ha='center',va='top',fontsize=11)
ax.text(2.5,-1.95,r'$A\to B\to A$ has length two, not length zero.',
        ha='center',va='center',fontsize=12)
ax.set(xlim=(-.55,5.75),ylim=(-2.2,1.9))
save(fig,'29_transport_cost','Free path category with A->B=0, B->A=0, A->C=2, C->A=5, D isolated. Diagram shows generators; shortest path costs are calculated separately.')

fig,ax=plt.subplots(figsize=(7.6,3.4));ax.axis('off')
labels=[r'$0$',r'$e_1$',r'$e_2$',r'$e_1+e_2$'];data=[['0','0','0','0'],['0','0','0','0'],['0','1','0','1'],['0','1','0','1']]
table=ax.table(cellText=data,rowLabels=labels,colLabels=labels,cellLoc='center',rowLoc='center',bbox=[.19,.18,.63,.67])
table.auto_set_font_size(False);table.set_fontsize(14)
for cell in table.get_celld().values():cell.set_linewidth(.5)
ax.text(.5,.98,r'Phase table $c(x,y)=x_2y_1$ in $\mathbf{F}_2$',transform=ax.transAxes,ha='center',va='top',fontsize=13)
ax.text(.5,.03,r'$c(e_1,e_2)=0$  but  $c(e_2,e_1)=1$',transform=ax.transAxes,ha='center',va='bottom',fontsize=13)
save(fig,'30_phase','G=F2^2 ordered [0,e1,e2,e1+e2]; c(x,y)=x2*y1 modulo 2; all 16 table values explicit.')
(ROOT/'build/figure_reports/plot_limits.json').write_text(json.dumps({'status':'PASS','plates':records,'scope':'Vector plots of explicit formulas. One axes per figure. No new formal theorem or AI-generated illustration.'},indent=2)+'\n')
print(f'Generated {len(records)} new vector figures.')

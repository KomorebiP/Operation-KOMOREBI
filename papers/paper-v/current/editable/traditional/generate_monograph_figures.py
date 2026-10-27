#!/usr/bin/env python3
"""Create deterministic exact-model monograph figures. No experimental data are fitted."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent; O=R/'monograph_figures';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'pdf.fonttype':42,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
TEAL='#245D60';GOLD='#BD874A';BLUE='#517C99';GRAY='#6D757C'
models=[]
def save(fig,name,model):
 fig.savefig(O/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None,'Creator':'Paper V exact-model generator'})
 fig.savefig(O/(name+'.png'),bbox_inches='tight',dpi=170)
 plt.close(fig)
 models.append(dict(name=name,model=model,pdf_sha256=hashlib.sha256((O/(name+'.pdf')).read_bytes()).hexdigest()))
# Index labels are exact integers on an infinite bilateral sequence, shown on a finite window.
q=np.arange(-2,3);fig,axs=plt.subplots(1,3,figsize=(11,3.35),sharey=True,layout='constrained')
for ax,D,title in zip(axs,[0,1,2],['Original coordinates','Delay one original sample','Delay one channel step']):
 for r,col in [(0,TEAL),(1,GOLD)]:
  src=2*q+r-D
  ax.scatter(q,np.full(q.shape,r),s=440,color=col,alpha=.12,edgecolor=col)
  for qi,si in zip(q,src):ax.text(qi,r,str(si),ha='center',va='center',color=col,fontweight='bold')
 ax.set(xlim=(-2.55,2.55),ylim=(-.65,1.65),xticks=q,yticks=[0,1],yticklabels=['even output','odd output'],xlabel='coarse address q',title=title)
 ax.grid(axis='x',alpha=.12)
 if D==1:ax.text(0,1.42,r'$y_0[q]=x_1[q-1],\quad y_1[q]=x_0[q]$',ha='center',fontsize=10,color=GRAY)
 elif D==2:ax.text(0,1.42,r'$y_r[q]=x_r[q-1]$',ha='center',fontsize=10,color=GRAY)
 else:ax.text(0,1.42,r'$x_r[q]=x[2q+r]$',ha='center',fontsize=10,color=GRAY)
for r in [0,1]:
 for qi in q:
  si=2*int(qi)+r-1
  assert divmod(si,2)==((int(qi)-1,1) if r==0 else (int(qi),0))
save(fig,'delay_coordinates',{'kind':'exact-integer-address-model','N':2,'coarse_window':[-2,2],'original_delays':[0,1,2],'scope':'Address identity holds bilaterally. Finite plotted window illustrates indices, not truncation or boundary conditions.'})
# Exact finite retained-packet cancellation, with coordinate averaging as a linear approximation.
s=[F(0),F(1,4),F(1,2),F(3,4),F(1),F(3,4),F(1,2),F(1,4)]
j=[F(0)]*3+[F(1)]*3+[F(0)]*2
Qs=[(s[2*(i//2)]+s[2*(i//2)+1])/2 for i in range(8)]
f=[a+b for a,b in zip(s,j)];rec=[a+b for a,b in zip(Qs,j)];err=[a-b for a,b in zip(f,rec)];smootherr=[a-b for a,b in zip(s,Qs)]
assert err==smootherr
fig,axs=plt.subplots(1,2,figsize=(9.5,3.35),layout='constrained');x=np.arange(8)
axs[0].plot(x,list(map(float,f)),marker='o',color=GRAY,label=r'$f=s+j$')
axs[0].plot(x,list(map(float,rec)),marker='s',color=TEAL,label=r'$\widetilde f=Qs+j$');axs[0].legend(frameon=False,loc='upper left');axs[0].set(title='A retained jump is passed through exactly',xlabel='sample address',ylabel='signal value',xticks=x)
axs[1].stem(x,list(map(float,err)),linefmt=TEAL,markerfmt='o',basefmt=' ',label=r'$f-\widetilde f=s-Qs$');axs[1].axhline(0,color=GRAY,lw=.7);axs[1].legend(frameon=False,loc='upper right');axs[1].set(title='Only the smooth approximation error remains',xlabel='sample address',ylabel='signed error',xticks=x,ylim=(-.22,.3));
for ax in axs:ax.grid(alpha=.13)
save(fig,'retained_packet_cancellation',{'kind':'exact-rational-finite-model','smooth':[str(x) for x in s],'jump':[str(x) for x in j],'Q':'Replace each adjacent pair by its average','error':[str(x) for x in err],'scope':'One eight-coordinate identity. It supplies the packet and does not test detection, Fourier rates, or general image recovery.'})
# Exact sufficient contrast interval, not an optimality claim for all detectors.
M=F(1);h=F(1,20);eps=F(1,40);b=M*h+2*eps;amin=F(1);lo=b;hi=amin-b;assert amin>2*b and lo<hi
fig,ax=plt.subplots(figsize=(8.6,2.8),layout='constrained')
ax.axvspan(0,float(lo),color=BLUE,alpha=.16);ax.axvspan(float(lo),float(hi),color=TEAL,alpha=.10);ax.axvspan(float(hi),1.15,color=GOLD,alpha=.15)
ax.plot([0,float(lo)],[.6,.6],color=BLUE,lw=5);ax.plot([float(hi),1.12],[1.2,1.2],color=GOLD,lw=5)
ax.text(float(lo)/2,.31,'smooth /\nnoise cells',ha='center',fontsize=9);ax.text(1.02,.92,'jump cells',ha='center',fontsize=9)
ax.text(.5,.85,'every threshold inside this gap separates the cells',ha='center',color=TEAL,fontsize=10)
for v,lab in [(lo,r'$b_h=1/10$'),(hi,r'$a_{\min}-b_h=9/10$')]:ax.axvline(float(v),color=GRAY,ls='--',lw=.9);ax.text(float(v),1.48,lab,ha='center',fontsize=11)
ax.set(xlim=(-.03,1.18),ylim=(.1,1.8),yticks=[],xlabel='absolute adjacent contrast',title=r'An explicit sufficient threshold interval: $M=1,\ h=1/20,\ \varepsilon=1/40,\ a_{\min}=1$')
save(fig,'jump_contrast_gap',{'kind':'exact-rational-bound-model','M':str(M),'h':str(h),'epsilon':str(eps),'minimum_amplitude':str(amin),'background_bound':str(b),'admissible_threshold_interval':[str(lo),str(hi)],'scope':'Sufficient contrast bounds under the declared one-jump-per-cell and bounded-noise assumptions. This diagram makes no universal detector or optimal-threshold assertion.'})
(O/'FIGURE_MODELS.json').write_text(json.dumps({'schema':'komorebi.paper_v.monograph.exact_figure_models.v1','models':models,'all_assertions_pass':True},indent=2)+'\n')
print('PASS: three exact-model figure pairs')

#!/usr/bin/env python3
"""Generate three explanatory figures from stated finite models.

Fraction arithmetic checks packet composition and Bayesian coarsening exactly.
The Jordan model checks a nilpotent polynomial exactly; sampled exponentials
are plotted illustrations, not extra proof or general numerical certification.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'monograph_figures';O.mkdir(exist_ok=True)
ACCENT='#245D60';INK='#212B34';GRAY='#58646B';GOLD='#B78B44';TEAL='#72A9A3'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelcolor':INK,'text.color':INK,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','pdf.fonttype':42})
def matmul(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def coarse(p):return [p[0]+p[1],p[2]]
def bayes(p,l):
 e=sum(x*y for x,y in zip(p,l));return [x*y/e for x,y in zip(p,l)]
def exact_models():
 A=[[F(1,2),F(1,4),F(1,4)],[F(1,3),F(1,2),F(1,6)],[F(1,6),F(1,4),F(7,12)]]
 B=[[F(1,2),F(1,6),F(1,3)],[F(1,4),F(1,2),F(1,4)],[F(1,4),F(1,3),F(5,12)]]
 count=0
 for a in [A,B]:
  for col in zip(*a):assert sum(col)==1 and all(x>=0 for x in col);count+=1
 C=matmul(B,A)
 for i in range(3):
  for j in range(3):assert C[i][j]==sum(B[i][k]*A[k][j] for k in range(3));count+=1
 products=[B[2][k]*A[k][0] for k in range(3)];assert sum(products)==C[2][0]==F(11,36);count+=1
 p=[F(1,8),F(3,8),F(1,2)];q=[F(3,8),F(1,8),F(1,2)];lc=[F(2),F(2),F(1)];lv=[F(1),F(3),F(1)]
 assert coarse(p)==coarse(q)==[F(1,2),F(1,2)];count+=1
 assert coarse(bayes(p,lc))==coarse(bayes(q,lc))==[F(2,3),F(1,3)];count+=1
 assert coarse(bayes(p,lv))==[F(5,7),F(2,7)];count+=1
 assert coarse(bayes(q,lv))==[F(3,5),F(2,5)];count+=1
 N=[[F(0),F(2)],[F(0),F(0)]];assert matmul(N,N)==[[F(0),F(0)],[F(0),F(0)]];count+=1
 I=[[F(1),F(0)],[F(0),F(1)]]
 for t in [F(0),F(1,4),F(1,2),F(1),F(2),F(3)]:
  P=[[I[i][j]+t*N[i][j] for j in range(2)] for i in range(2)];assert P[0][1]==2*t;count+=1
  for u in [F(0),F(1,3),F(1),F(2)]:
   Q=[[I[i][j]+u*N[i][j] for j in range(2)] for i in range(2)]
   assert matmul(P,Q)==[[I[i][j]+(t+u)*N[i][j] for j in range(2)] for i in range(2)];count+=1
 return {'A':A,'B':B,'products':products,'p':p,'q':q,'constant_likelihood':lc,'varying_likelihood':lv,'exact_assertions':count}
def save(fig,name):
 fig.savefig(O/(name+'.pdf'),bbox_inches='tight',metadata={'Title':name,'Author':'Komorebi P.','CreationDate':None,'ModDate':None});fig.savefig(O/(name+'.png'),dpi=180,bbox_inches='tight');plt.close(fig)
def generate():
 m=exact_models()
 fig,ax=plt.subplots(figsize=(7.1,3.15));vals=[float(x) for x in m['products']];bars=ax.bar(['via state 1','via state 2','via state 3'],vals,color=[ACCENT,TEAL,GOLD],width=.58)
 ax.set_ylim(0,.18);ax.set_ylabel('Contribution to final state 3');ax.set_title('Every intermediate packet contributes',pad=16)
 for b,v in zip(bars,m['products']):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.006,str(v),ha='center',fontsize=13,color=INK)
 ax.text(.98,.96,'Exact sum: 11/36',transform=ax.transAxes,ha='right',va='top',fontsize=12);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);fig.tight_layout();save(fig,'exact_packet_composition')
 fig,axs=plt.subplots(1,3,figsize=(8.1,3.1),sharey=True)
 panels=[('Before conditioning',[coarse(m['p']),coarse(m['q'])]),('Constant by block',[coarse(bayes(m['p'],m['constant_likelihood'])),coarse(bayes(m['q'],m['constant_likelihood']))]),('Varies within block 1',[coarse(bayes(m['p'],m['varying_likelihood'])),coarse(bayes(m['q'],m['varying_likelihood']))])]
 for ax,(title,pair) in zip(axs,panels):
  x=np.arange(2)
  for n,(v,col,lab) in enumerate(zip(pair,[ACCENT,GOLD],['Prior p','Prior q'])):
   bars=ax.bar(x+(n-.5)*.32,[float(z) for z in v],width=.31,color=col,label=lab)
   for b,z in zip(bars,v):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.025,str(z),ha='center',fontsize=10)
  ax.set_xticks(x,['Block 1','Block 2']);ax.set_title(title,fontsize=10,pad=15);ax.set_ylim(0,.88);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
 axs[0].set_ylabel('Coarse posterior mass');axs[1].legend(ncol=2,loc='upper center',bbox_to_anchor=(.5,-.17),frameon=False,fontsize=10);fig.tight_layout();save(fig,'exact_bayesian_coarsening')
 t=np.linspace(0,5,401);fig,ax=plt.subplots(figsize=(7.1,3.15));ax.plot(t,np.exp(-t),color=GRAY,linestyle='--',linewidth=2,label='Exponential decay factor exp(-t)');ax.plot(t,2*t*np.exp(-t),color=ACCENT,linewidth=2.5,label='Coupled memory 2t exp(-t)');ax.set(xlabel='Time t',ylabel='Kernel value',ylim=(0,1.12));ax.set_title('A hidden Jordan block leaves a polynomial factor',pad=15);ax.legend(frameon=False,fontsize=10);ax.grid(alpha=.18);fig.tight_layout();save(fig,'exact_jordan_memory')
 assets={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in O.iterdir() if p.suffix in ['.pdf','.png']}
 (O/'MODELS_AND_GENERATION.json').write_text(json.dumps({'schema':'komorebi.paper_vi.exact_explanatory_figures.v1','exact_assertions':m['exact_assertions'],'models':{'packet':'Two3x3 rational column-stochastic matrices; complete block composition','bayesian':'Two rational priors with identical coarse masses; block-constant and within-block-varying likelihoods','memory':'Nilpotent N^2=0 for hidden generator -I+N; exact polynomial semigroup factor'},'floating_scope':'Only plotting conversion and exponential curve sampling. No universal numerical claim.','assets':assets},indent=2)+'\n')
 print(json.dumps({'status':'PASS','exact_assertions':m['exact_assertions'],'pdf_figures':3,'png_previews':3},indent=2))
if __name__=='__main__':generate()

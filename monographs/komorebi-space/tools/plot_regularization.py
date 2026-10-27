#!/usr/bin/env python3
"""Six vector figures for the bounded-budget extension (one axes per figure)."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/figure_reports').mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':12,
                     'axes.labelsize':12,'legend.fontsize':10.5,'pdf.fonttype':42,'ps.fonttype':42})
spec=importlib.util.spec_from_file_location('budgeted_repair',ROOT/'examples/budgeted_repair.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
figroot=ROOT/'source/figures';records=[]

def save(fig,name,formula):
    path=figroot/(name+'.pdf')
    fig.savefig(path,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)
    (figroot/(name+'.tex')).write_text('\\includegraphics[width=\\linewidth]{figures/'+name+'.pdf}\n')
    records.append({'name':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'formula':formula})

N=np.arange(1,65)
fig,ax=plt.subplots(figsize=(7.5,3.7))
ax.plot(N,N,'-',lw=1.8,label=r'Escaping datum: $m_N^2=N$')
ax.plot(N,np.cumsum(1/N.astype(float)**2),'--',lw=1.8,label=r'Attainable datum: $m_N^2=\sum_{n=1}^{N}n^{-2}$')
ax.axhline(2,ls=':',lw=1,label='Uniform bound for the attainable datum: 2')
ax.set_xscale('log',base=2);ax.set_yscale('log',base=2)
ax.set(xticks=[1,2,4,8,16,32,64],yticks=[1,2,4,8,16,32,64],
       xlabel='Number of exact observation constraints $N$',ylabel='Minimum squared correction norm')
ax.set_xticklabels(['1','2','4','8','16','32','64']);ax.set_yticklabels(['1','2','4','8','16','32','64'])
ax.grid(axis='y',alpha=.16);ax.legend(loc='upper left',frameon=False)
save(fig,'31_nested_energy','N versus sum(n^-2,n<=N), bound 2. Both use T diagonal(1/n), with different fixed data.')

fig,ax=plt.subplots(figsize=(7.5,4.0))
M=math.sqrt(41)/10;theta=np.linspace(0,2*math.pi,600)
x=M*np.cos(theta);y=M/2*np.sin(theta)
ax.fill(x,y,alpha=.10);ax.plot(x,y,lw=1.6,label='Reachable residuals at the fixed budget')
q=np.array([.5,.2]);r=np.array([1.,1.]);v=r-q
s=np.linspace(-.63,.65,100);line=q[:,None]+np.array([.8,-.5])[:,None]*s
ax.plot(line[0],line[1],'--',lw=1.2,label='Supporting line')
ax.annotate('',xy=r,xytext=q,arrowprops={'arrowstyle':'->','lw':1.8})
ax.plot([0,q[0],r[0]],[0,q[1],r[1]],'o',ms=4)
ax.annotate(r'$Ta=(1/2,1/5)$',xy=q,xytext=(.73,-.30),
            arrowprops={'arrowstyle':'-','lw':.7},fontsize=12)
ax.text(1.04,1.02,r'$r=(1,1)$',fontsize=12)
ax.text(.95,.55,r'$v=(1/2,4/5)$',fontsize=12)
ax.text(-.24,-.13,'0',fontsize=11)
ax.set_aspect('equal');ax.set(xlim=(-.85,1.62),ylim=(-.66,1.3),xlabel='Residual coordinate 1',ylabel='Residual coordinate 2')
ax.legend(loc='upper left',frameon=False,fontsize=10)
save(fig,'32_budget_certificate','T=diag(1,1/2), r=(1,1), a=(1/2,2/5), ||a||=sqrt(41)/10. Image ellipse axes M,M/2. Tangent normal v=(1/2,4/5).')

fig,ax=plt.subplots(figsize=(7.5,3.5));x=np.linspace(0,3,400)
f=np.maximum(1-x,0);radius=.05+.1*x
ax.plot(x,f,lw=1.8,label=r'Nominal $\beta(M)=\max(1-M,0)$')
ax.fill_between(x,np.maximum(f-radius,0),f+radius,alpha=.16,label=r'Guaranteed uncertainty band: $\delta+\eta M$')
ax.plot(x,f+radius,'--',lw=1);ax.plot(x,np.maximum(f-radius,0),':',lw=1)
ax.set(xlabel='Correction budget $M$',ylabel='Residual norm',xlim=(0,3),ylim=(0,1.15))
ax.legend(frameon=False,loc='upper right');ax.grid(axis='y',alpha=.14)
save(fig,'33_budget_uncertainty','Scalar nominal T=1,r=1; delta=1/20,eta=1/10; profiles bracketed by beta +/- (delta+eta*M), lower clipped at zero.')

fig,ax=plt.subplots(figsize=(7.5,3.7));s=np.geomspace(.015,8,500)
for alpha,ls,label in [(1/16,'-',r'$\alpha=1/16$'),(1/4,'--',r'$\alpha=1/4$'),(1,':',r'$\alpha=1$')]:
    ax.plot(s,s/(s*s+alpha),ls,lw=1.8,label=label)
    ax.plot([math.sqrt(alpha)],[1/(2*math.sqrt(alpha))],'o',ms=4)
ax.axhline(2,ls=':',lw=.7,alpha=.6);ax.axhline(1,ls=':',lw=.7,alpha=.6);ax.axhline(.5,ls=':',lw=.7,alpha=.6)
ax.set_xscale('log');ax.set(xlabel=r'Singular value $\sigma$',ylabel=r'Noise multiplier $\sigma/(\sigma^2+\alpha)$',ylim=(0,2.2))
ax.legend(frameon=False,loc='upper right');ax.text(.07,2.07,r'Peak value $1/(2\sqrt{\alpha})$',fontsize=11)
save(fig,'34_noise_filter','Three scalar noise response functions sigma/(sigma^2+alpha); alpha=1/16,1/4,1. Points at sharp maximum sigma=sqrt(alpha).')

fig,ax=plt.subplots(figsize=(7.5,3.6));n=np.arange(1,257,dtype=float)
for m,ls in [(4,'-'),(16,'--'),(64,':')]:
    ax.plot(n,m*m/(m*m+n*n),ls,lw=1.9,label=f'$m={m}$')
    ax.plot([m],[.5],'o',ms=4)
ax.axhline(.5,ls=':',lw=.7,alpha=.5)
ax.set_xscale('log',base=2);ax.set(xticks=[1,4,16,64,256],ylim=(0,1.07),
    xlabel='Coordinate index $n$',ylabel=r'Correction coordinate $a_n^{(m)}$')
ax.set_xticklabels(['1','4','16','64','256']);ax.legend(frameon=False,loc='lower left')
save(fig,'35_regularized_escape','Exact coordinate values m^2/(m^2+n^2), m=4,16,64. Marked threshold n=m has coordinate 1/2.')

fig,ax=plt.subplots(figsize=(7.5,3.8));ms=[1,2,4,8,16,32,64];lower=[];upper=[];data=[]
for m in ms:
    enc=b.diagonal_enclosure(m,32*m)
    alo,ahi=enc['energy_interval'];blo,bhi=enc['residual_square_interval']
    lo=math.sqrt(float(alo*blo));hi=math.sqrt(float(ahi*bhi))
    lower.append(lo);upper.append(hi)
    data.append({'m':m,'cutoff':32*m,'plotted_lower_rounded':lo,'plotted_upper_rounded':hi})
mid=(np.array(lower)+np.array(upper))/2
ax.errorbar(ms,mid,yerr=[mid-np.array(lower),np.array(upper)-mid],fmt='o-',capsize=4,lw=1.3,
            label=r'Soft repair: certified interval for $\sqrt{A_mB_m}$')
hlo=np.sqrt(np.array(ms)/(np.array(ms)+1));hhi=np.ones(len(ms));hmid=(hlo+hhi)/2
ax.errorbar(ms,hmid,yerr=[hmid-hlo,hhi-hmid],fmt='s--',capsize=4,lw=1.2,
            label=r'Hard prefix: certified interval, $N=m$')
ax.axhline(math.pi/4,ls=':',lw=1);ax.axhline(1,ls=':',lw=1)
ax.text(66,math.pi/4,r'$\pi/4$',va='center',fontsize=12);ax.text(66,1,'1',va='center',fontsize=12)
ax.set_xscale('log',base=2);ax.set(xticks=ms,xlim=(.85,105),ylim=(.35,1.07),
    xlabel='Scale parameter $m$ (not a shared correction budget)',ylabel='Correction norm times residual norm')
ax.set_xticklabels([str(m) for m in ms]);ax.legend(frameon=False,loc='lower right',fontsize=10)
save(fig,'36_budget_product','Exact rational partial sums with K=32m, the diagonal tail bounds; product enclosures sqrt(Alo*Blo),sqrt(Ahi*Bhi). Hard prefix intervals [sqrt(m/(m+1)),1]. Finite series arithmetic is exact before plotting roundoff.')

report={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),'plates':records,
        'budget_product_data':data,'scope':'Plots of explicit formulas and exact rational finite sums with written infinite-tail bounds. Plot coordinates are rounded for display. No new Lean proof.'}
(ROOT/'build/figure_reports/plot_regularization.json').write_text(json.dumps(report,indent=2)+'\n')
print('Generated',len(records),'regularization figures')

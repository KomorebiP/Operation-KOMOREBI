#!/usr/bin/env python3
"""Four quantitative vector plates. Display rounding is not proof evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':12,
                     'axes.labelsize':12,'legend.fontsize':10.5,'pdf.fonttype':42,'ps.fonttype':42})
figroot=ROOT/'source/figures';records=[]
def save(fig,name,formula):
    path=figroot/(name+'.pdf');fig.savefig(path,bbox_inches='tight',pad_inches=.13);plt.close(fig)
    (figroot/(name+'.tex')).write_text('\\includegraphics[width=\\linewidth]{figures/'+name+'.pdf}\n')
    records.append({'name':name,'formula':formula,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

alpha=np.geomspace(1e-6,1,400);eps=1e-5
fig,ax=plt.subplots(figsize=(7.5,3.8))
ax.loglog(alpha,eps/alpha,'-',lw=1.8,label=r'Correction bound $\varepsilon/\alpha$')
ax.loglog(alpha,eps/(2*np.sqrt(alpha)),'--',lw=1.8,label=r'Fitted-error bound $\varepsilon/(2\sqrt{\alpha})$')
ax.set(xlabel=r'Regularization parameter $\alpha$',ylabel='Certified norm error',xlim=(1e-6,1))
ax.legend(frameon=False,loc='upper right');ax.text(.035,.19,r'$\varepsilon=10^{-5}$',transform=ax.transAxes,fontsize=12)
ax.grid(axis='y',alpha=.15)
save(fig,'37_solver_amplification','Universal bounds eps/alpha and eps/(2 sqrt(alpha)), eps=10^-5. Not observed errors.')

fig,ax=plt.subplots(figsize=(7.5,3.8));t=np.linspace(0,.68,400);j=3*t*t-2*t+1
ax.plot(t,j,lw=1.8,label=r'Protected objective $J(t,t)=3t^2-2t+1$')
ax.axhline(21/32,ls='--',lw=1.4,label=r'Dual lower bound $21/32$')
ax.plot([1/4],[11/16],'o',ms=6);ax.plot([1/3],[2/3],'s',ms=5)
ax.plot([1/4,1/4],[21/32,11/16],':',lw=2)
ax.annotate(r'Proposal: $t=1/4$, $J=11/16$',xy=(1/4,11/16),xytext=(.045,.91),
            arrowprops={'arrowstyle':'->','lw':.7},fontsize=11)
ax.annotate(r'Minimum: $t=1/3$, $J=2/3$',xy=(1/3,2/3),xytext=(.38,.91),
            arrowprops={'arrowstyle':'->','lw':.7},fontsize=11)
ax.set(xlim=(0,.68),ylim=(.62,1.055),xlabel='Allowed correction coordinate $t$',ylabel='Objective or certified lower bound')
ax.legend(frameon=False,loc='upper center',fontsize=10)
save(fig,'38_objective_certificate','D=(1,0),P=(1,-1),f=(1,0),alpha=1. Proposal=(1/4,1/4), optimum=(1/3,1/3), dual=21/32, gap=1/32.')

fig,ax=plt.subplots(figsize=(7.5,3.6));s=np.geomspace(1e-4,1e4,400)
ax.loglog(s,s/4,'-',lw=1.8,label=r'Raw coordinate covector norm $|q_s|=s/4$')
ax.loglog(s,np.ones_like(s)/math.sqrt(32),'--',lw=1.8,label=r'Actual norm $\sqrt{q_s^\mathsf{T}G_s^{-1}q_s}=1/\sqrt{32}$')
ax.set(xlabel=r'Basis scale $s$ for $B_s=s(1,1)^\mathsf{T}$',ylabel='Reported normal-residual norm',xlim=(1e-4,1e4))
ax.legend(frameon=False,loc='upper left',fontsize=10);ax.grid(axis='y',alpha=.15)
save(fig,'39_covector_metric','Same proposal=(1/4,1/4); B_s=s(1,1), G_s=2s^2, q_s=-s/4. Raw norm changes; Gram-corrected norm is constant.')

fig,ax=plt.subplots(figsize=(7.5,3.9));delta=np.geomspace(1e-5,1,600);m=np.ceil(delta**(-2/3));al=1/m**2
bias=np.sqrt(2/m);noise=delta*m/2;solver=.25*delta**(1/3)
ax.loglog(delta,bias,'-',lw=1.4,label=r'Bias bound $\sqrt{2/m}$')
ax.loglog(delta,noise,'--',lw=1.4,label=r'Data term $\delta m/2$')
ax.loglog(delta,solver,':',lw=1.7,label=r'Solver term $\varepsilon/\alpha=(1/4)\delta^{1/3}$')
ax.loglog(delta,bias+noise+solver,'-.',lw=1.7,label='Total certified bound')
ax.set(xlabel=r'Deterministic data error bound $\delta$',ylabel='Norm error contribution',xlim=(1e-5,1))
ax.legend(frameon=False,loc='upper left',fontsize=10);ax.grid(axis='y',alpha=.15)
save(fig,'40_stopping_schedule','Attainable diagonal model: m=ceil(delta^-2/3), alpha=m^-2, kappa=1/4. All curves are bounds, not empirical errors.')
report={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),'plates':records,
        'scope':'Floating-point rendering of explicit formulas whose mathematical proofs and exact finite checks are supplied separately.'}
(ROOT/'audit/certified_repair/figures.json').write_text(json.dumps(report,indent=2)+'\n')
print('Generated',len(records),'certificate plates')

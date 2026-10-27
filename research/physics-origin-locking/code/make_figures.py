"""Reproduce figures from recorded results and explicit analytic formulas."""
from pathlib import Path
import json
import numpy as np
import mpmath as mp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matching import ROOT,D,S,Bcoef
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.labelsize':10,'legend.fontsize':8.5,'figure.figsize':(6.6,3.5)})
def new():
    f=plt.figure();return f,f.add_subplot(111)
def finish(f,n):
    f.tight_layout();f.savefig(OUT/f'{n}.pdf',bbox_inches='tight');f.savefig(OUT/f'{n}.png',dpi=160,bbox_inches='tight');plt.close(f)
mp.mp.dps=55
q=np.linspace(-7e-6,7e-6,401);dd=mp.mpf(str(D));BB=mp.mpf(str(Bcoef(15)))
y=[]
for qq in q:
 ss=mp.mpf(str(qq))**2;FF=(1+ss)**2*mp.log1p(ss)-ss-mp.mpf('1.5')*ss*ss
 val=dd*(-2*ss/S+ss*ss/S**2)+BB*FF
 y.append(float(val/(dd*mp.mpf('1e-12'))))
f,ax=new();ax.plot(q*1e6,y);ax.axhline(0,linestyle=':',linewidth=.8)
ax.set(xlabel=r'Background coordinate $q$ ($10^{-6}$)',ylabel=r'$(V(q)-D)/(10^{-12}D)$',ylim=(-1.4,5))
ax.grid(alpha=.2);finish(f,'near_origin_vacuum')
lo=json.loads((ROOT/'results/origin_locking_audit.json').read_text());cs=np.load(ROOT/'results/conditional_transport_curves.npz')
f,ax=new()
for cr in [1,20,39]:
 a=cs[f'crossing_{cr}_a']*1e-6;tr=cs[f'crossing_{cr}_trace']/D
 ax.loglog(a,tr,label=f'Freeze hypothesis: crossing {cr}')
ax.axhline(4/S,linestyle='--',label='Loss of local stability')
ax.set(xlabel='Cosmological scale factor (present = 1)',ylabel=r'Conditional $(\rho_\chi-3p_\chi)/D$',xlim=(.1,10),ylim=(.005,5e4));ax.grid(alpha=.2);ax.legend();finish(f,'conditional_locking')
f,ax=new();a=np.load(ROOT/'results/origin_stress128.npz');r=json.loads((ROOT/'results/origin_stress128.json').read_text());rho0=r['parameters']['E0']+r['parameters']['rad0']
ax.plot(a['t'],a['a']**3*a['rho']/rho0,label=r'$a^3\rho/\rho_i$')
ax.plot(a['t'],a['pressure_work']/rho0,label='Accumulated pressure work')
ax.plot(a['t'],a['comoving_balance']/rho0,linestyle='--',label='Conserved sum')
ax.set(xlabel=r'Dimensionless time $\tau$',ylabel='Comoving budget / initial total');ax.grid(alpha=.2);ax.legend();finish(f,'expansion_work')
f,ax=new()
for name,label in [('origin_stress64','Cutoff 16, 64 nodes'),('origin_stress128','Cutoff 16, 128 nodes'),('origin_stress128_cut32','Cutoff 32, 128 nodes')]:
 a=np.load(ROOT/'results'/f'{name}.npz');r=json.loads((ROOT/'results'/f'{name}.json').read_text());ax.plot(a['t'],a['mode_density']/r['parameters']['E0'],label=label,linewidth=1.2)
ax.set(xlabel=r'Dimensionless time $\tau$',ylabel=r'Instantaneous $\rho_\chi/E_0$');ax.grid(alpha=.2);ax.legend();finish(f,'expansion_cutoff_failure')
f,ax=new();vr=json.loads((ROOT/'results/verification.json').read_text());rows=next(g['value'] for g in vr['gates'] if g['name']=='modified_model_matching_window')
ax.semilogy([x['depth'] for x in rows],[x['threshold_over_budget'] for x in rows],marker='o',label='Minimum barrier for a central maximum')
ax.axhline(1,linestyle='--',label='Available budget');ax.axhline(.3,linestyle=':',label='Illustrative changed-model barrier')
ax.set(xlabel='Physical species depth',ylabel='Required barrier / reference budget',xticks=range(10,16));ax.grid(alpha=.2);ax.legend();finish(f,'matching_window')
print('Wrote five separate figures from actual arrays and stated formulas.')

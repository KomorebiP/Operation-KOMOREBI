"""Computed Mellin-tail curves and exact pole/zero diagrams for SF-DISCOVERY-100."""
from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parent
deps=root.parents[1]/'special_work'/'verification_dependencies'
if deps.is_dir():sys.path.insert(0,str(deps))
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(root/'checks'))
from spectral_continuation import MellinContinuation
mp.mp.dps=80
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15,'pdf.fonttype':42})
colors=['#075985','#e76f51','#248f83','#8b5cf6']
figdir=root/'figures';figdir.mkdir(exist_ok=True)
record={'checkpoint':'SF-DISCOVERY-100','precision_decimal_digits':80,'method':'Finite root-of-unity exponential sum, log derivative; exact theorem locations for poles and zeros.','qualification':'Floating-point curves are ordinary high precision; structural locations and formulas have separate proofs.','plots':[]}
def save(fig,name):
 for ext in ('pdf','png'):fig.savefig(figdir/(name+'.'+ext),dpi=180,bbox_inches='tight')
 plt.close(fig)
x=np.linspace(0,12,241)
fig,ax=plt.subplots(1,2,figsize=(9.3,3.6),layout='constrained')
for k,N in enumerate((2,3,4,5)):
 calc=MellinContinuation(N,count=1)
 g=[mp.mpf(0) if xx==0 else 1+calc.log_tail_derivative(mp.mpf(str(xx))) for xx in x]
 ax[0].plot(x,[float(v) for v in g],lw=2,color=colors[k],label=f'N = {N}')
 ax[1].semilogy(x[1:],[float(abs(v-1)) for v in g[1:]],lw=2,color=colors[k],label=f'N = {N}')
 record['plots'].append({'N':N,'root_radius_interval':[0,12],'samples':241,'g_at_1':mp.nstr(g[20],40),'g_at_12':mp.nstr(g[-1],40),'exponential_gap':mp.nstr(1-mp.cos(2*mp.pi/N),30)})
ax[0].axhline(1,color='#64748b',ls=':',lw=1)
ax[0].set(xlabel='Root radius x',ylabel=r'$d\log E_{N,1}(x^N)/dx$',title='One exponential dominates the finite sum')
ax[1].set(xlabel='Root radius x',ylabel='Absolute logarithmic-derivative remainder',title='The tail is exponentially small')
for a in ax:a.legend(fontsize=8)
save(fig,'14_spectral_tail')

fig,ax=plt.subplots(2,1,figsize=(8.8,4.6),layout='constrained')
N=3
for i,a in enumerate(ax):
 a.axhline(0,color='#475569',lw=1)
 a.scatter([0,-1,-2,-3,-4],[0]*5,s=70,facecolors='white',edgecolors=colors[0],lw=2,label='zeros at nonpositive integers',zorder=3)
 poles=[1/N] if i==0 else [1/N-k for k in range(5)]
 a.scatter(poles,[0]*len(poles),s=70,color=colors[1],marker='x',lw=2,label='simple poles',zorder=4)
 for p in poles:a.axvline(p,color=colors[1],alpha=.14,lw=1)
 a.set(xlim=(-4.4,.8),ylim=(-.4,.4),yticks=[],xlabel='Real part of s')
 a.legend(loc='upper left',fontsize=8,ncol=2)
 a.set_title('N = 3: unshifted family, one pole' if i==0 else 'N = 3: shift a > 0, pole ladder at 1/3 − k')
 ax[i].text(.6,-.27,'All poles lie on the real axis',ha='right',fontsize=9,color='#475569')
save(fig,'15_spectral_poles')
record['pole_locations']={'N':3,'unshifted':['1/3'],'shifted':['1/3-k for integer k>=0'],'zeros':['-m for integer m>=0'],'residues':'sin(pi/N)/(N*pi)*(1-1/N)_k*a^k/k!'}
record['inputs']={'checks/spectral_continuation.py':hashlib.sha256((root/'checks/spectral_continuation.py').read_bytes()).hexdigest()}
record['outputs']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for name in ('14_spectral_tail','15_spectral_poles') for p in [figdir/(name+'.pdf'),figdir/(name+'.png')]}
(root/'evidence/spectral_figure_record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'figures':2,'status':'created','samples_per_N':241}))

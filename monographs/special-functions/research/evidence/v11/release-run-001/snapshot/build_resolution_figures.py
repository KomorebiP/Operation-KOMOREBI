#!/usr/bin/env python3
"""Six deterministic Matplotlib figures for the quantitative resolution atlas.
Run checks first, then python build_resolution_figures.py. The figures show
proved analytic bounds and labeled floating evaluations, not interval plots.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
try:
    import mpmath as mp
except ImportError:
    dep=Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
    if dep.is_dir():sys.path.insert(0,str(dep))
    import mpmath as mp
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('resolution_checks',ROOT/'checks/resolution_v11.py')
rc=importlib.util.module_from_spec(spec);spec.loader.exec_module(rc)
F=rc.F
FIG=ROOT/'figures_v11';FIG.mkdir(exist_ok=True)
report=json.loads((ROOT/'evidence/v11/resolution_checks.json').read_text())
mp.mp.dps=100
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,'axes.labelsize':11,'legend.fontsize':9,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.17,'grid.linewidth':.7,'pdf.fonttype':42,'savefig.facecolor':'white','figure.facecolor':'white'})
BLUE='#075985';ORANGE='#c65b35';TEAL='#087f75';PURPLE='#7355a5';GREY='#66717e';PALE='#e7eff4'
record={'checkpoint':'SF-DISCOVERY-110','base_checkpoint':'SF-DISCOVERY-100','figures':[],'working_decimal_digits':100,'plotting_convention':'Exact rational and analytic certificates are proved in the atlas. Displayed floating values are not directed-rounding intervals.','preparation_correction':'The lower arithmetic visibility endpoint is absent when its formula is negative. It is not clamped to an allegedly invisible T=0.'}
def save(fig,name,description,extra=None):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight')
    fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight')
    plt.close(fig)
    entry={'name':name,'description':description,'pdf_sha256':hashlib.sha256((FIG/(name+'.pdf')).read_bytes()).hexdigest(),'png_sha256':hashlib.sha256((FIG/(name+'.png')).read_bytes()).hexdigest()}
    if extra:entry.update(extra)
    record['figures'].append(entry)
def coeff(eps,N):
    c=[mp.mpf(1)]
    for n in range(1,N+1):
        scale=(1-eps)*mp.mpf('.25')**(2*n)+eps*mp.mpf('.75')**(2*n)
        c.append(scale*mp.fsum(c[j]*c[n-1-j] for j in range(n))/(2*n+1))
    return c
N=100
base=coeff(mp.mpf(0),N);diag=coeff(mp.mpf(1),N)
radius=np.linspace(0,1,161)
fig,ax=plt.subplots(1,2,figsize=(10.8,4.2),layout='constrained',gridspec_kw={'width_ratios':[1.25,1]})
for eps,color,label in [(mp.mpf('.1'),ORANGE,r'$\varepsilon=10^{-1}$'),(mp.mpf('.001'),TEAL,r'$\varepsilon=10^{-3}$'),(mp.mpf('1e-6'),BLUE,r'$\varepsilon=10^{-6}$')]:
    c=coeff(eps,N)
    dif=[(a-b)/eps for a,b in zip(c,base)]
    y=[float(mp.mpf(str(r))*mp.polyval(list(reversed(dif)),mp.mpf(str(r))**2)) for r in radius]
    ax[0].plot(radius,y,lw=2,color=color,label=label)
bound=[float(mp.fsum(n*diag[n]*mp.mpf(str(r))**(2*n+1) for n in range(1,N+1))+12*(N+1)*(mp.mpf('.75')*mp.mpf(str(r)))**(2*N+3)) for r in radius]
ax[0].plot(radius,bound,'--',color=GREY,lw=1.8,label='Analytic Lipschitz envelope')
ax[0].set(xlabel=r'Observation radius $R\leq1$',ylabel=r'$(F_\varepsilon(R)-F_0(R))/\varepsilon$',title='Tiny taps remain close on a fixed disk')
ax[0].legend(loc='upper left',frameon=False)
values=[.5]+[math.log(2)/math.log(4/3)]*3
bars=ax[1].bar(range(4),values,color=[GREY,BLUE,TEAL,ORANGE],width=.62)
ax[1].set_xticks(range(4),['0',r'$10^{-12}$',r'$10^{-6}$',r'$10^{-1}$'])
ax[1].set(xlabel=r'Fast-channel weight $\varepsilon$',ylabel='Exact entire-function order',title='Every positive tap changes the order',ylim=(0,2.85))
for b,v in zip(bars,values):ax[1].text(b.get_x()+b.get_width()/2,v+.06,f'{v:.4f}',ha='center',fontsize=10)

tail=12*(N+1)*(.75)**(2*N+3)
save(fig,'resolution_01_weak_tap','Compact normalized response and exact discontinuous entire orders.',{'coefficient_last_n':N,'highest_power':2*N+1,'normalised_curve_truncation_upper_at_R1':tail,'roundoff':'100-digit arithmetic, not interval arithmetic'})

fig,ax=plt.subplots(1,2,figsize=(10.8,4.2),layout='constrained')
eps=np.logspace(-12,-1,160)
rr=[rc.weak_tap_radius(float(e))[-1] for e in eps]
ax[0].loglog(eps,rr,color=BLUE,lw=2.4)
for e in [1e-3,1e-6,1e-9,1e-12]:
    R=rc.weak_tap_radius(e)[-1];ax[0].plot(e,R,'o',color=BLUE,ms=5)
ax[0].set(xlabel=r'Fast-channel weight $\varepsilon$',ylabel=r'Sufficient radius for $F_\varepsilon/F_0\geq2$',title='A guaranteed separation radius')
ax[0].text(.04,.08,'Conservative upper bound on the radius\nneeded for this particular separation test.',transform=ax[0].transAxes,fontsize=9,color=GREY)
rho,cminus,cplus,R=rc.weak_tap_radius(1e-6)
x=np.logspace(2,11,240)
ax[1].loglog(x,cminus*x**rho,color=ORANGE,lw=2.3,label=r'Lower bound for $\log F_{10^{-6}}$')
ax[1].loglog(x,cplus*np.sqrt(x),color=BLUE,lw=2.3,label=r'Upper bound for $\log F_0$')
ax[1].axvline(R,color=GREY,ls=':',lw=1.5)
ax[1].set(xlabel='Radius R',ylabel='Bounds on logarithmic growth',title=r'Why the guarantee eventually succeeds')
ax[1].text(.98,.04,r'$R_2\approx1.237\times10^9$ for $\varepsilon=10^{-6}$',transform=ax[1].transAxes,fontsize=9,ha='right',bbox=dict(facecolor='white',edgecolor='none',alpha=.95,pad=2))
ax[1].legend(loc='upper left',frameon=False)
save(fig,'resolution_02_growth_resolution','Explicit type bounds give a conservative sufficient observation radius, not the actual first crossover.')

fig,ax=plt.subplots(1,2,figsize=(10.8,4.2),layout='constrained')
ps=np.geomspace(11,20000,220);lam=-2*np.log1p(-ps**-2);D4=105/math.pi**4
for k,col in enumerate([BLUE,TEAL,ORANGE,PURPLE]):
    y=lam**k*np.exp(5*lam)*D4/(ps**4+1)
    ax[0].loglog(ps,y,lw=2,color=col,label=f'Derivative order {k}')
ax[0].set(xlabel='Excluded prime p (continuous bound shown)',ylabel=r'Upper bound on the disk $|s|\leq5$',title='Large-prime distinctions fall below precision')
ax[0].legend(frameon=False,loc='lower left')
ax[0].text(.98,.98,'Formula applies at primes.\nConnecting curves show its scale.',transform=ax[0].transAxes,ha='right',va='top',fontsize=8,color=GREY)
primes=[101,1009,10007]
for j,p in enumerate(primes):
    upper=F(4,3)/F(p**4+1)/(1-F(1,p*p))**10
    ax[1].bar(j,-math.log10(float(upper)),color=[BLUE,TEAL,ORANGE][j],width=.58)
    ax[1].text(j,-math.log10(float(upper))+.25,f'{float(upper):.2e}',ha='center',fontsize=10)
ax[1].set_xticks(range(3),[str(p) for p in primes]);ax[1].set(xlabel='Excluded prime p',ylabel='Guaranteed decimal suppression',title='Rational certificates for the entire disk',ylim=(0,18))

save(fig,'resolution_03_prime_precision','Exact analytic derivative envelopes and rational integer-depth bounds. No arithmetic series is truncated.')

fig,ax=plt.subplots(1,2,figsize=(10.8,4.2),layout='constrained')
rows=[rc.prime_visibility(p) for p in primes]
y=np.arange(3)
# Ratios make the narrow but large-time threshold brackets legible.
for j,r in enumerate(rows):
    ax[0].hlines(j,r['invisible_until']/r['visible_by'],1,color=[BLUE,TEAL,ORANGE][j],lw=9)
    ax[0].plot([r['invisible_until']/r['visible_by'],1],[j,j],'|',color='black',ms=15)
    ax[0].text(.963,j+.14,f"p={r['p']}: T+={r['visible_by']:.4g}",fontsize=10)
ax[0].set(xlabel=r'Negative depth divided by the sufficient threshold $T_+$',ylabel='',title=r'Where the difference reaches $10^{-6}$',xlim=(.96,1.005),ylim=(-.45,2.5));ax[0].set_yticks([])
ax[0].text(.965,-.30,'Left endpoint: no larger than tolerance\nRight endpoint: at least tolerance',fontsize=9,color=GREY)
heights=[r['log10_cancellation_lower'] for r in rows]
ax[1].bar(range(3),heights,color=[BLUE,TEAL,ORANGE],width=.6)
ax[1].set_yscale('log');ax[1].set_xticks(range(3),[str(p) for p in primes])
ax[1].set(xlabel='Excluded prime p',ylabel=r'Lower bound on $\log_{10}(A_1(-T_+)/D_p(-T_+))$',title='Subtracting full signals costs precision')
for j,v in enumerate(heights):ax[1].text(j,v*1.3,f'{v:,.0f} digits',ha='center',fontsize=9)
ax[1].set_ylim(1000,2e9)
save(fig,'resolution_04_prime_depth','Analytic brackets for the absolute visibility threshold, together with a cancellation lower bound for subtracting full functions. This is not a computational feasibility claim.')

chosen=report['defect_certificates'][11];det=chosen['detector'];delta=1e-12
poly=np.array([v['decimal'] for v in det['poly']])
x=np.linspace(0,1,600);curve=np.polynomial.polynomial.polyval(x,poly)
fig,ax=plt.subplots(1,2,figsize=(10.8,4.2),layout='constrained',gridspec_kw={'width_ratios':[1.1,1]})
ax[0].plot(x,curve,color=PURPLE,lw=2.1,label='Degree 7 detector')
for n in [1,3,5,7]:ax[0].plot(float(rc.node(n)),0,'o',color=BLUE,ms=6)
ax[0].plot(float(rc.node(2)),1,'o',color=ORANGE,ms=7,label='Target negative atom: n=2')
ax[0].axhline(0,color=GREY,lw=.7)
ax[0].set(xlabel='Atomic coordinate x',ylabel='Detector polynomial value',title='Kill four positive shelves, retain the defect')
ax[0].legend(loc='upper right',frameon=False)
ax[0].text(.06,.06,'Zeros: n=1, 3, 5, 7\nExtra factor: (1−x)³',transform=ax[0].transAxes,fontsize=9,color=GREY)
negative=-delta/16;upper=det['upper']['decimal'];tail_bound=upper-negative
vals=[negative,tail_bound,upper]
ax[1].bar(range(3),np.array(vals)/1e-14,color=[ORANGE,BLUE,PURPLE],width=.6)
ax[1].axhline(0,color=GREY,lw=.8);ax[1].set_xticks(range(3),['Target\nnegative mass','Positive tail\nupper bound','Total norm\nupper bound'])
ax[1].set(ylabel=r'Contribution in units of $10^{-14}$',title='A strictly negative exact certificate',ylim=(-7.5,1.6))
for j,v in enumerate(vals):ax[1].text(j,v/1e-14+(.2 if v>0 else -.35),f'{v/1e-14:.4f}',ha='center',fontsize=10)
save(fig,'resolution_05_signed_detector','Exact degree 7 detector for lambda_2=-1-10^-12. The bar chart displays a rigorous tail upper bound, not a truncated estimate of that tail.')

fig,ax=plt.subplots(1,2,figsize=(10.8,4.2),layout='constrained')
rows=report['defect_certificates'];digits=np.arange(1,16)
pos=[r['positive_through_degree'] for r in rows];neg=[r['detector']['degree'] for r in rows]
ax[0].step(digits,pos,where='mid',color=BLUE,lw=2.3,label='Every degree up to this passes')
ax[0].step(digits,neg,where='mid',color=ORANGE,lw=2.3,label='An explicit degree detects the defect')
ax[0].fill_between(digits,pos,neg,step='mid',color=PALE,alpha=.8)
ax[0].set(xlabel=r'Defect precision $k$ in $\delta=10^{-k}$',ylabel='Polynomial degree',title='A rigorously bracketed resolution gap',xlim=(1,15))
ax[0].xaxis.set_major_locator(MaxNLocator(integer=True));ax[0].yaxis.set_major_locator(MaxNLocator(integer=True));ax[0].legend(frameon=False,loc='upper left')
ax[0].text(.98,.05,'The gap is unresolved.\nNeither boundary is claimed optimal.',ha='right',transform=ax[0].transAxes,fontsize=9,color=GREY)
thresholds=[r['delta_threshold']['decimal'] for r in report['low_degree_certificates']]
degree=np.arange(len(thresholds))
ax[1].semilogy(degree,thresholds,'o-',lw=2,color=BLUE,label='Sufficient positivity margin')
ax[1].axhline(1e-12,color=ORANGE,ls='--',label=r'Chosen defect $\delta=10^{-12}$')
ax[1].fill_between(degree,1e-24,thresholds,color=PALE,alpha=.7)
ax[1].set(xlabel='Degree of every tested polynomial',ylabel=r'Safe defect size from interpolation, $12/K_d$',title='An exact bound for all low degrees',ylim=(1e-22,100))
ax[1].xaxis.set_major_locator(MaxNLocator(integer=True));ax[1].legend(frameon=False,loc='lower left')
save(fig,'resolution_06_degree_gap','Every polynomial of degree at most 4 has positive norm for delta=10^-12, yet a degree 7 polynomial has negative norm. Degree 5 or 6 is not decided by these certificates.')
record['input_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),ROOT/'checks/resolution_v11.py',ROOT/'evidence/v11/resolution_checks.json']}
(ROOT/'evidence/v11/resolution_figures.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':'PASS','figures':len(record['figures']),'normalised_weak_tap_tail_bound':tail}))

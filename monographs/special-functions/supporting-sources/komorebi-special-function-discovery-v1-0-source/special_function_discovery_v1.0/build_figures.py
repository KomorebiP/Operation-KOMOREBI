"""Computed figures for SF-DISCOVERY-001. No generated imagery.

Nonlinear curves have a positive-coefficient Cauchy tail bound, independent of
sample agreement. Arithmetic moments use high precision, not certified balls.
"""
from pathlib import Path
from fractions import Fraction
import sys, json, math
deps = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
if deps.is_dir(): sys.path.insert(0, str(deps))
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
mp.mp.dps=90
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
 'axes.spines.right':False,'axes.grid':True,'grid.alpha':.16,'pdf.fonttype':42,
 'figure.facecolor':'white','axes.titleweight':'bold','savefig.facecolor':'white'})
colors=['#075985','#e76f51','#248f83','#8b5cf6']
record={'checkpoint':'SF-DISCOVERY-001','curves':[],'non_claims':['No historical novelty certification.','Arithmetic decimals are ordinary high precision, not ball intervals.']}
def save(fig,name):
 fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight')
 fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight')
 plt.close(fig)
def nonlinear(q,r,last=160):
 q,r=mp.mpf(str(q)),mp.mpf(str(r)); c=[mp.mpf(1)]
 for n in range(1,last+1):
  c.append(mp.fsum(q**(2*i+1)*r**(2*(n-1-i)+1)*c[i]*c[n-1-i] for i in range(n))/(2*n+1))
 return c
def evaluate(c,x):
 y=mp.mpf(str(x)); return y*mp.polyval(list(reversed(c)),y*y)
def cauchy_bound(q,r,R):
 # On |z|<=1, all these coefficients are <= tangent coefficients, and
 # tan(1)<2. For larger radii use M(R)<=R[1+M(vR)^2], v=max(q,r).
 v=max(Fraction(str(q)),Fraction(str(r))); R=Fraction(str(R)); radii=[R]
 while radii[-1]>1: radii.append(radii[-1]*v)
 bound=Fraction(2)
 for radius in reversed(radii[:-1]): bound=radius*(1+bound*bound)
 return bound
fig,ax=plt.subplots(1,2,figsize=(9.3,3.5),layout='constrained')
x=np.linspace(0,1.4,180)
for k,(q,r,label) in enumerate([(.5,.5,'q = r = 1/2'),(.25,.75,'q = 1/4, r = 3/4'),(.75,.75,'q = r = 3/4')]):
 c=nonlinear(q,r); y=[float(evaluate(c,z)) for z in x]
 ax[0].plot(x,y,color=colors[k],lw=2,label=label)
 R=2; b=cauchy_bound(q,r,R)
 ratio=Fraction(7,10)
 tail=b*ratio**323/(1-ratio)
 record['curves'].append({'q':q,'r':r,'last_n':160,'highest_power':321,'R':2,'display_radius':1.4,'Cauchy_M_upper':str(b),'tail_bound':str(tail),'tail_float':float(tail)})
ax[0].plot(x,np.tan(x),'k--',lw=1.5,label='tangent boundary')
ax[0].set(xlabel='Real argument z',ylabel='Normalized function value',title='Two feedback scales change the function')
ax[0].legend(fontsize=8,loc='upper left')
x2=np.linspace(0,3,200)
for k,(q,r,label) in enumerate([(.5,.5,'symmetric: scaled sinh'),(.25,.75,'asymmetric: same order 1')]):
 c=nonlinear(q,r)
 ax[1].plot(x2,[float(evaluate(c,z)) for z in x2],lw=2,color=colors[k],label=label)
 b=cauchy_bound(q,r,4);ratio=Fraction(3,4);tail=b*ratio**323/(1-ratio)
 record['curves'].append({'q':q,'r':r,'last_n':160,'highest_power':321,'R':4,'display_radius':3,'Cauchy_M_upper':str(b),'tail_bound':str(tail),'tail_float':float(tail)})
ax[1].axvline(np.pi/2,color='#64748b',ls=':',label='first tangent pole')
ax[1].set(xlabel='Real argument z',ylabel='Entire continuation',title='Both curves continue past tangent’s pole')
ax[1].legend(fontsize=8,loc='upper left')
save(fig,'01_asymmetric_functions')

q=np.linspace(.08,.94,70);Q,R=np.meshgrid(q,q);lo=np.zeros_like(Q);hi=np.full_like(Q,30.)
for _ in range(75):
 mid=(lo+hi)/2;mask=Q**mid+R**mid>1;lo=np.where(mask,mid,lo);hi=np.where(mask,hi,mid)
rho=(lo+hi)/2
fig,ax=plt.subplots(figsize=(6.8,4.5),layout='constrained')
im=ax.pcolormesh(Q,R,rho,cmap='viridis',shading='auto',vmin=0,vmax=7)
cs=ax.contour(Q,R,rho,levels=[.5,1,2,4],colors='white',linewidths=.9)
ax.clabel(cs,fmt=lambda x:f'order {x:g}',fontsize=9)
ax.plot(q,q,color='#e76f51',ls='--',lw=1.5,label='known one-dilation diagonal')
ax.set(xlabel='Left dilation q',ylabel='Right dilation r',title=r'Exact growth balance: $q^{\rho}+r^{\rho}=1$')
ax.legend(fontsize=8,loc='upper left')
fig.colorbar(im,ax=ax,label='Theoretical entire growth order (numerical root display)')
save(fig,'02_order_atlas')

sys.path.insert(0,str(ROOT/'checks'))
from complex_depth import zeta_ratio
fig,ax=plt.subplots(1,2,figsize=(9.3,3.6),layout='constrained')
s=np.linspace(-4,12,150)
for k,mod in enumerate([1,2,6,30]):
 zeta_values=[zeta_ratio(4+2*j,mod)-1 for j in range(76)]
 vals=[]
 for t in s:
  tt=mp.mpf(str(t)); b=mp.mpf(1); summands=[]
  for j in range(76):
   summands.append((-1)**j*b*zeta_values[j]);b*= (2*tt-j)/(j+1)
  vals.append(float(mp.fsum(summands)))
 ax[0].semilogy(s,vals,color=colors[k],lw=2,label=f'conductor Q = {mod}')
ax[0].set(xlabel='Real depth s',ylabel='Arithmetic function A(s)',title='Complex-depth family on the real line')
ax[0].legend(fontsize=8)
n=np.array([2,3,5,6,7,10,11,13,14,15,17,19,21,22,23,26,29,30],dtype=float)
lam=-2*np.log1p(-n**-2);w=n**-4
ax[1].scatter(lam,w,color=colors[0],s=35)
for ni,li,wi in zip(n[:4],lam[:4],w[:4]): ax[1].annotate(f'n={int(ni)}',(li,wi),xytext=(4,4),textcoords='offset points',fontsize=8)
ax[1].set(yscale='log',xlabel=r'Frequency $-2\log(1-n^{-2})$',ylabel=r'Positive weight $n^{-4}$',title='Infinitely many frequencies approach zero')
save(fig,'03_complex_depth')

# Read the independently authored finite numerical record, while formulas in
# routes/arithmetic_polynomials.md prove the infinite statements.
data=json.loads((ROOT/'evidence/arithmetic_polynomial_checks.json').read_text())
record['arithmetic_record_keys']=list(data)
samples=data['sample_polynomials']
fig,ax=plt.subplots(1,2,figsize=(9.3,3.6),layout='constrained')
xx=np.linspace(0,1,250)
for k,entry in enumerate(samples):
 co=[float(v) for v in entry['p2_coefficients_ascending']]
 ax[0].plot(xx,np.polynomial.polynomial.polyval(xx,co),color=colors[k],lw=2,label=f"sieve strength {entry['strength']:g}")
ax[0].axhline(0,color='#475569',lw=.8)
ax[0].set(xlabel='Arithmetic spectral coordinate x',ylabel='Monic degree-two polynomial',title='Prime strength moves the exact polynomial')
ax[0].legend(fontsize=8)
nodes=[(1-nn**-2)**2 for nn in [1,2,3,5,6,7,10]]
for k,lam0 in enumerate([-1,0,1]):
 masses=[nn**-4*(1+lam0*(nn%2==0)) for nn in [1,2,3,5,6,7,10]]
 ax[1].scatter(nodes,masses,s=32,color=colors[k],label=f'strength {lam0}',alpha=.85)
ax[1].set_yscale('symlog',linthresh=.0001)
ax[1].set(xlabel='Atom location x',ylabel='Atom mass',title='Deletion changes an infinite prime shelf')
ax[1].legend(fontsize=8)
save(fig,'04_prime_polynomials')

root_entries=data['hankel_exceptional_strengths']
nearest=[]
for entry in root_entries:
 if entry['prime']==2:
  delta=min(-1-mp.mpf(v) for v in entry['lambda_roots']);nearest.append((entry['hankel_order'],float(delta)))
fig,ax=plt.subplots(figsize=(7.2,3.7),layout='constrained')
mm=np.arange(2,13);M0=105/math.pi**4
upper=4096/81*(16*M0/17-1)*(272/567)**(2*(mm-2))
ax.semilogy(mm,upper,lw=2,color=colors[0],label='proved upper bound')
ax.semilogy(*zip(*nearest),'o',ms=7,color=colors[1],label='computed nearest margin, orders 1–4')
ax.axhline(.001,color='#475569',ls='--',label='example negative weight: strength = −1.001')
ax.set(xlabel='Hankel matrix order m',ylabel=r'Positivity margin $\delta_m$',title='A hidden negative weight becomes visible at finite depth')
ax.legend(fontsize=8)
save(fig,'05_sieve_boundary')

fig,ax=plt.subplots(1,2,figsize=(9.0,3.8),layout='constrained')
t=np.arange(6)+.5
for j,tt in enumerate(t):
 rr=math.sqrt(2)*math.pi*tt
 zz=np.array([rr,-rr,1j*rr,-1j*rr])
 ax[0].scatter(zz.real,zz.imag,color=plt.cm.viridis(j/5),s=26)
 ax[1].scatter(j,(rr**4),color=plt.cm.viridis(j/5),s=36)
ax[0].set(aspect='equal',xlabel='Real z',ylabel='Imaginary z',title='Four D₄ zeros in each rotation orbit')
ax[1].set(yscale='log',xlabel='Orbit index j',ylabel=r'One zero $w_j=z^4$',title='One spectral address per orbit')
save(fig,'06_orbit_zeros')
(ROOT/'evidence/figure_computation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'figures':6,'curve_tail_bounds':[v['tail_float'] for v in record['curves']]}))

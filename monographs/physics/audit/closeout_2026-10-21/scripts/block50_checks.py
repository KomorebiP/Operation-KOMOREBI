#!/usr/bin/env python3
"""Block 50 numerical regression: free Dirac Fourier generator and centered symbols.

All calculations use finite sets of Fourier modes. They test, but do not prove,
full-space convergence or an unbounded-operator statement.
"""
import os, json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'figures').mkdir(exist_ok=True)

I2=np.eye(2,dtype=np.complex128); Z2=np.zeros((2,2),dtype=np.complex128)
sigma=[np.array([[0,1],[1,0]],complex),np.array([[0,-1j],[1j,0]],complex),np.array([[1,0],[0,-1]],complex)]
alpha=np.array([np.block([[Z2,s],[s,Z2]]) for s in sigma])
beta=np.block([[I2,Z2],[Z2,-I2]])
I4=np.eye(4,dtype=np.complex128)

N=7; m=0.82
modes=np.array([(i,j,k) for i in range(-N,N+1) for j in range(-N,N+1) for k in range(-N,N+1)],dtype=float)
k=2*np.pi*modes
K2=(k*k).sum(axis=1)
rng=np.random.default_rng(502026)
# Finite cutoff samples of a rapidly decaying Fourier coefficient profile.
phase=np.stack([np.exp(1j*(0.23*k[:,0]+a*0.17*k[:,1]+0.05*a*k[:,2])) for a in range(4)],axis=-1)
shape=np.array([1+.05j,0.4-.3j,-.2+.25j,.25+.04j],complex)
f=phase*shape[None,:]*(1+K2[:,None])**(-2.83)
f=f/np.linalg.norm(f)

def hamiltonian(q):
 return m*beta[None,:,:]+ np.einsum('nj,jab->nab',q,alpha)
H=hamiltonian(k)

def centered(h):
 return hamiltonian(k*np.sinc((h*k)/np.pi))

def act(A,psi):
 return np.einsum('nab,nb->na',A,psi)

def evolve(A, t, psi):
 # Exact modal formula H^2=E^2 I using Pauli/Clifford matrices.
 e2=np.maximum(np.real(np.einsum('nab,nba->n',A,A))/4,0)
 E=np.sqrt(e2)
 sinc_factor=np.where(E>1e-13,np.sin(t*E)/np.where(E>1e-13,E,1.),t)
 return np.cos(t*E)[:,None]*psi -1j*sinc_factor[:,None]*act(A,psi)

def c_norm(x): return float(np.linalg.norm(x))

# Matrix algebra and finite modal checks.
sel=[0,72,1000,1687,len(k)-1]
checks={}
checks['clifford_beta_square_max']=float(np.linalg.norm(beta@beta-I4))
checks['clifford_alpha_square_max']=float(max(np.linalg.norm(a@a-I4) for a in alpha))
checks['clifford_cross_anticommutator_max']=float(max(np.linalg.norm(alpha[i]@alpha[j]+alpha[j]@alpha[i]) for i in range(3) for j in range(i+1,3)))
checks['clifford_beta_anticommutator_max']=float(max(np.linalg.norm(alpha[i]@beta+beta@alpha[i]) for i in range(3)))
checks['mode_energy_identity_max']=float(max(np.linalg.norm(H[i]@H[i]-(m*m+K2[i])*I4) for i in sel))
checks['mode_hermiticity_max']=float(max(np.linalg.norm(H[i]-H[i].conj().T) for i in sel))
checks['unitarity_norm_max']=float(max(abs(c_norm(evolve(H,t,f))-1) for t in [-2.4,-.4,0,.1,1.2,2.0]))
checks['group_law_max']=c_norm(evolve(H,0.37,evolve(H,-.51,f))-evolve(H,-.14,f))
checks['zero_mode_mass_identity']=float(np.linalg.norm(H[np.argmin(K2)]-m*beta))

# Full-space proof concerns; finite cutoff tests below are illustrations only.
Hm=act(H,f)
H2m=act(H,Hm)
H2f=c_norm(H2m)
Hf=c_norm(Hm)
third_norm=np.sqrt(np.sum(np.sum(np.abs(k)**6,axis=1)*np.sum(np.abs(f)**2,axis=1)))
rows=[]
for h in [0.28,0.14,0.07,0.035,0.0175]:
 Ch=centered(h)
 diff=act(Ch-H,f)
 err_H=c_norm(diff)
 err_prop=c_norm(evolve(Ch,0.67,f)-evolve(H,0.67,f))
 theory_generator=h*h*third_norm/6
 theory_prop=0.67*theory_generator
 # Strong resolvent at z=i using the exact Clifford resolvent formula.
 def resolvent(A):
  EE=np.maximum(np.real(np.einsum('nab,nba->n',A,A))/4,0)
  return (act(A,f)+1j*f)/(EE[:,None]+1)
 err_R=c_norm(resolvent(Ch)-resolvent(H))
 # Residual right side: ||(H-Hh)(H-i)^-1 f||.
 Rf=resolvent(H)
 resolvent_identity_bound=c_norm(act(H-Ch,Rf))
 rows.append({'h':h,'generator_error':err_H,'generator_bound':theory_generator,
              'propagator_error_t067':err_prop,'propagator_bound_t067':theory_prop,
              'resolvent_error_i':err_R,'resolvent_bound_i':resolvent_identity_bound})
 assert err_H <= theory_generator*(1+1e-10)+1e-14
 assert err_prop <= theory_prop*(1+1e-10)+1e-14
 assert err_R <= resolvent_identity_bound*(1+1e-10)+1e-14

results={'version':'Block50 numerical regression 2026-10-20',
         'nature':'finite Fourier cutoff checks, NOT infinite-dimensional proofs',
         'mass':m,'N_per_axis':N,'mode_count':len(modes),
         'weighted_test_exponent':5.66,
         'Hf_norm':Hf,'H2f_norm':H2f,'H3_spatial_norm':float(third_norm),
         'matrix_checks':checks,'convergence':rows,
         'generator_quotients':[],'negative_control':{}}
for t in [0.16,0.08,0.04,0.02,0.01]:
 deriv=(evolve(H,t,f)-f)/t
 diff=c_norm(deriv+1j*Hm)
 bound=abs(t)*H2f/2
 assert diff <= bound*(1+1e-10)+1e-14
 results['generator_quotients'].append({'t':t,'derivative_residual':diff,'bound_H2':bound})
# Reversing the evolution sign gives an incompatible derivative.
t=.005
Uwrong=np.cos(t*np.sqrt(m*m+K2))[:,None]*f + 1j*(np.sin(t*np.sqrt(m*m+K2))/np.sqrt(m*m+K2))[:,None]*Hm
bad=c_norm((Uwrong-f)/t+1j*Hm)
results['negative_control']={'reversed_exponential_sign_residual':bad,'expected_as_t_to_0':2*Hf,'passes_rejection':bool(bad>.75*2*Hf)}
assert bad>.75*2*Hf
assert max(checks.values())<2e-10,checks

with open(ROOT/'results'/'numerical_audit.json','w') as g: json.dump(results,g,indent=2)
with open(ROOT/'results'/'convergence.csv','w',newline='') as g:
 w=csv.DictWriter(g,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
with open(ROOT/'results'/'generator_quotient.csv','w',newline='') as g:
 w=csv.DictWriter(g,fieldnames=results['generator_quotients'][0].keys());w.writeheader();w.writerows(results['generator_quotients'])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelcolor':'#1d3348',
                     'xtick.color':'#425a70','ytick.color':'#425a70','axes.edgecolor':'#8095a6',
                     'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
C='#088b94'; NAVY='#163756'; GOLD='#ce9751'
fig,ax=plt.subplots(figsize=(8.9,4.6))
arr=lambda name: np.array([r[name] for r in rows])
hs=arr('h')
ax.loglog(hs,arr('generator_error'),'o-',color=NAVY,label='Centered generator error',lw=2.0,ms=6)
ax.loglog(hs,arr('propagator_error_t067'),'s-',color=C,label='Evolution error, t = 0.67',lw=2.0,ms=6)
ax.loglog(hs,arr('generator_bound'),'--',color=GOLD,label='Rigorous H³ error envelope',lw=1.8)
ax.set_xlabel('Centered spacing parameter h')
ax.set_ylabel('L² error on the declared finite-mode test field')
ax.set_title('Quadratic convergence under third-order Fourier regularity',fontweight='medium',loc='left',pad=14)
ax.grid(alpha=.18)
ax.legend(frameon=False,fontsize=9,loc='upper left')
fig.tight_layout();fig.savefig(ROOT/'figures'/'block50_quadratic_convergence.png',dpi=190);plt.close(fig)

fig,ax=plt.subplots(figsize=(8.9,4.4))
ts=np.array([r['t'] for r in results['generator_quotients']]); ee=np.array([r['derivative_residual'] for r in results['generator_quotients']]);bb=np.array([r['bound_H2'] for r in results['generator_quotients']])
ax.plot(ts,ee,'o-',lw=2,color=C,ms=6,label='Strong derivative residual')
ax.plot(ts,bb,'--',lw=1.8,color=GOLD,label='t / 2 times ||H² f|| bound')
ax.set_xlabel('Time increment t')
ax.set_ylabel('Difference quotient residual')
ax.set_title('Generator identification on a regular Fourier test field',loc='left',pad=13)
ax.grid(alpha=.17);ax.legend(frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(ROOT/'figures'/'block50_generator_derivative.png',dpi=190);plt.close(fig)

print('Block 50 finite-mode regressions: PASS')
print('Modes:',len(modes),'weighted field exponent 5.66')
print('Clifford max:',max(checks.values()))
print('Generator h errors:',[(r['h'],round(r['generator_error'],9)) for r in rows])
print('Evolution h errors:',[(r['h'],round(r['propagator_error_t067'],9)) for r in rows])
print('Generator derivative errors:',[(r['t'],round(r['derivative_residual'],9)) for r in results['generator_quotients']])
print('Negative control rejected:',results['negative_control']['passes_rejection'])

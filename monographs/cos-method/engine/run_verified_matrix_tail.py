from pathlib import Path
import sys, time, json
import numpy as np
import pandas as pd
import mpmath as mp
from scipy import optimize

ROOT=Path('/mnt/data/Komorebi_Quadratic_Form_Engine_v1.9_Verified_Spectrum')
sys.path.insert(0,str(ROOT))
from verified_spectrum import certify_float64_factor_spectrum
from accuracy_driven import certified_positive_logsf
from kcos_v2_hardened import adaptive_kcos_logsf


def make_factor(seed,n,m):
    rng=np.random.default_rng(seed)
    A=rng.normal(size=(n,m))
    scales=np.geomspace(1.0,0.2,m)
    A=A*scales[None,:]/np.sqrt(m)
    return A.astype(np.float64)


def target_q(A,target=-16.0):
    lam=np.linalg.eigvalsh(A@A.T)[::-1]
    mean=float(lam.sum()); sd=float(np.sqrt(2*np.sum(lam*lam)))
    def f(q):
        return adaptive_kcos_logsf(q,lam,relative_tolerance=1e-11,max_K=262144).log10_p-target
    lo=mean+0.2*sd; hi=mean+8*sd
    while f(hi)>0: hi=mean+2*(hi-mean)
    return optimize.brentq(f,lo,hi,xtol=1e-12,rtol=1e-14,maxiter=100),lam


def parse_interval(s):
    a,b=s.strip()[1:-1].split(',',1)
    return mp.mpf(a.strip()),mp.mpf(b.strip())

A=make_factor(9137,32,40)
q,lam_float=target_q(A,-16.0)
print('q',q,flush=True)

t0=time.perf_counter()
spec=certify_float64_factor_spectrum(A,candidate_digits=65,interval_dps=80,working_dps=115)
print('spectrum seconds',time.perf_counter()-t0,flush=True)

# Reference containment check against high precision exact binary64 factor.
with mp.workdps(115):
    Amp=mp.matrix([[mp.mpf(float(A[i,j]).as_integer_ratio()[0])/float(A[i,j]).as_integer_ratio()[1]
                    for j in range(A.shape[1])] for i in range(A.shape[0])])
    vals,_=mp.eigsy(Amp*Amp.T)
    exact=[vals[i] for i in range(len(vals)-1,-1,-1)]
contained=[]; widths=[]
for lo_s,hi_s,e in zip(spec.lower,spec.upper,exact):
    lo=mp.mpf(lo_s); hi=mp.mpf(hi_s)
    contained.append(lo<=e<=hi)
    widths.append((hi-lo)/e)
print('contained',all(contained),'max rel spec width',mp.nstr(max(widths),12),flush=True)

lower=[x for x in spec.lower if mp.mpf(x)>0]
upper=[x for x in spec.upper if mp.mpf(x)>0]

tail_kwargs=dict(initial_K=128,initial_L='12',initial_interval_dps=60,max_K=4096,max_L=18,max_interval_dps=120,working_dps=190)

t0=time.perf_counter()
lo=certified_positive_logsf(repr(q),lower,relative_accuracy='1e-11',**tail_kwargs)
print('lower tail',lo.certified,lo.achieved_relative_ratio_minus_one,lo.K,lo.L,'sec',time.perf_counter()-t0,flush=True)
t0=time.perf_counter()
hi=certified_positive_logsf(repr(q),upper,relative_accuracy='1e-11',**tail_kwargs)
print('upper tail',hi.certified,hi.achieved_relative_ratio_minus_one,hi.K,hi.L,'sec',time.perf_counter()-t0,flush=True)

la,_=parse_interval(lo.log10_interval); _,hb=parse_interval(hi.log10_interval)
with mp.workdps(120):
    width=hb-la
    ratio=mp.expm1(mp.log(10)*width)
    mid=(la+hb)/2

row={
 'case':'dense_float64_rank32', 'n':32,'m':40,'q':repr(q),
 'target_near_log10_p':-16,
 'all_reference_eigenvalues_contained':all(contained),
 'orthogonality_defect_upper':spec.orthogonality_defect_upper,
 'reconstruction_residual_upper':spec.reconstruction_residual_upper,
 'max_relative_spectral_width':mp.nstr(max(widths),20),
 'lower_tail_certified':lo.certified,'upper_tail_certified':hi.certified,
 'lower_tail_interval':lo.log10_interval,'upper_tail_interval':hi.log10_interval,
 'combined_log10_interval':f'[{mp.nstr(la,50)}, {mp.nstr(hb,50)}]',
 'combined_log10_midpoint':mp.nstr(mid,40),
 'combined_width_decades':mp.nstr(width,20),
 'combined_ratio_minus_one':mp.nstr(ratio,20),
 'end_to_end_certified_1e_9': bool(lo.certified and hi.certified and ratio <= mp.mpf('1e-9')),
}
pd.DataFrame([row]).to_csv(ROOT/'verified_matrix_to_tail_controls.csv',index=False)
with open(ROOT/'verified_matrix_to_tail_controls.json','w') as f: json.dump(row,f,indent=2)
print(pd.DataFrame([row]).to_string(index=False),flush=True)

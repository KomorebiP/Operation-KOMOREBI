import sys,time
from pathlib import Path
import numpy as np,pandas as pd
from scipy.linalg import hadamard
from scipy import optimize
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from verified_spectrum import certified_float64_factor_logsf
from kcos_v2_hardened import adaptive_kcos_logsf

n=64
Q=hadamard(n,dtype=np.float64)/8.0
sing=np.repeat(np.array([1.0,.75,.5,.25]),16)
A=Q*sing[None,:]
lam=np.linalg.eigvalsh(A@A.T)[::-1]
mean=lam.sum(); sd=(2*(lam*lam).sum())**0.5
def f(q): return adaptive_kcos_logsf(q,lam,relative_tolerance=1e-11,max_K=262144).log10_p+16
lo=mean+.2*sd; hi=mean+8*sd
while f(hi)>0: hi=mean+2*(hi-mean)
q=optimize.brentq(f,lo,hi,xtol=1e-12,rtol=1e-14)
rows=[]
for eps in ['1e-10','1e-12']:
    t=time.perf_counter()
    r=certified_float64_factor_logsf(
        repr(q),A,relative_accuracy=eps,
        initial_candidate_digits=50,max_candidate_digits=80,candidate_step=30,
        interval_dps=65,tail_accuracy_fraction='0.05',
        tail_kwargs=dict(initial_K=64,initial_L='10',initial_interval_dps=50,
                         max_K=4096,max_L=18,max_interval_dps=120,working_dps=170))
    rows.append({
        'case':'dense_exact_binary_hadamard64','n':64,'m':64,'q':repr(q),
        'target_near_log10_p':-16,'requested_relative_accuracy':eps,
        'certified':r.certified,
        'achieved_ratio_minus_one':r.achieved_relative_ratio_minus_one,
        'combined_log10_interval':r.log10_interval,
        'combined_log10_midpoint':r.log10_midpoint,
        'candidate_digits':r.candidate_digits,
        'spectral_refinements':r.spectral_refinements,
        'orthogonality_defect_upper':r.spectral_enclosure.orthogonality_defect_upper,
        'reconstruction_residual_upper':r.spectral_enclosure.reconstruction_residual_upper,
        'leading_eigenvalue_lower':r.spectral_enclosure.lower[0],
        'leading_eigenvalue_upper':r.spectral_enclosure.upper[0],
        'runtime_seconds':time.perf_counter()-t,
    })
df=pd.DataFrame(rows)
df.to_csv(ROOT/'verified_matrix_to_tail_accuracy.csv',index=False)
print(df.to_string(index=False))

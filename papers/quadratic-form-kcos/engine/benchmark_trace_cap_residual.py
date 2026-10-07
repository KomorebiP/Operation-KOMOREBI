from pathlib import Path
import sys, math
import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from approximate_lightcone import block_transfer_matrix, phase_norm_vector
from budget_scheduler import edge_risks_depth
from spectral_tail_bridge import dual_budget_greedy_schedule
from residual_trace_cap import residual_spectrum_certificate, trace_moment_tail_bracket
from kcos_v2 import adaptive_kcos_logsf

rng=np.random.default_rng(20260923)
phases,width=10,5;widths=[width]*phases;m=50
L=np.zeros((m,m))
for h in range(phases):
    sh=slice(h*width,(h+1)*width)
    L[sh,sh]=1.8*np.eye(width)+0.04*rng.normal(size=(width,width))
    if h+1<phases:
        sg=slice((h+1)*width,(h+2)*width)
        L[sh,sg]=0.10*rng.normal(size=(width,width))
H=L.T@L
E=np.zeros_like(H)
for h in range(phases):
    for g in range(h+2,phases):
        sh=slice(h*width,(h+1)*width);sg=slice(g*width,(g+1)*width)
        C=rng.normal(size=(width,width));E[sh,sg]=C;E[sg,sh]=C.T
E/=np.linalg.norm(E,ord=2);H+=0.015*E
mi=np.linalg.eigvalsh(H).min()
if mi<=1e-8:H+=(abs(mi)+0.05)*np.eye(m)
H/=np.linalg.norm(H,ord=2)
A=np.linalg.cholesky(H).T
true_lam=np.linalg.eigvalsh(H)[::-1]

Bphase=block_transfer_matrix(H,widths)
X=np.zeros((m,2));X[:width]=rng.normal(size=(width,2))
rho=phase_norm_vector(X,widths)
risks=edge_risks_depth(Bphase,rho,5)
sched=dual_budget_greedy_schedule(Bphase,risks,query_budget=0.05,operator_budget=0.005)
starts=np.cumsum([0]+widths);H0=H.copy()
for h,g in sched.omitted_pairs:
    sh=slice(starts[h],starts[h+1]);sg=slice(starts[g],starts[g+1])
    H0[sh,sg]=0.;H0[sg,sh]=0.
H0=.5*(H0+H0.T)

V0=np.zeros((m,6));V0[:width,:5]=rng.normal(size=(width,5));V0[width:2*width,5:6]=rng.normal(size=(width,1))
def block_krylov_basis(depth):
    blocks=[];V=V0.copy()
    for _ in range(depth):
        if blocks:
            Q=np.column_stack(blocks);V-=Q@(Q.T@V);V-=Q@(Q.T@V)
        Qv,R=np.linalg.qr(V,mode='reduced')
        d=np.abs(np.diag(R)) if R.size else np.array([])
        scale=max(float(d.max()) if d.size else 0.,1.)
        Qv=Qv[:,d>1e-11*scale] if d.size else Qv
        if Qv.shape[1]==0:break
        blocks.append(Qv);V=H0@Qv
    return np.column_stack(blocks) if blocks else np.zeros((m,0))

def q_for_p(p):
    mean=float(np.sum(true_lam));sd=math.sqrt(2*np.sum(true_lam**2));logt=math.log(p)
    lo=mean*(1+1e-10);hi=mean+3*sd
    def f(q):return adaptive_kcos_logsf(q,true_lam,relative_tolerance=1e-10).log_p-logt
    while f(hi)>0:hi+=3*sd
    return brentq(f,lo,hi,xtol=1e-10,rtol=1e-11)

p=1e-8;q=q_for_p(p);true=adaptive_kcos_logsf(q,true_lam,relative_tolerance=1e-10)
rows=[]
for depth in range(2,10):
    V=block_krylov_basis(depth);U,_=np.linalg.qr(A@V,mode='reduced')
    cert=residual_spectrum_certificate(A,U,compute_square_trace=True)
    br=trace_moment_tail_bracket(q,cert,relative_tolerance=1e-8)
    rows.append({
        'depth':depth,'basis_dim':U.shape[1],
        'residual_trace':cert.residual_trace,
        'residual_trace_fraction':cert.residual_trace/np.sum(true_lam),
        'residual_cap':cert.residual_cap,
        'residual_square_trace':cert.residual_square_trace,
        'core_lower_log10_p':br.lower_log10_p,
        'true_log10_p':true.log10_p,
        'trace_cap_upper_log10_p':br.upper_log10_p,
        'two_sided_width_decades':br.bracket_width_decades,
        'upper_gap_decades':br.upper_log10_p-true.log10_p,
        'lower_gap_decades':true.log10_p-br.lower_log10_p if np.isfinite(br.lower_log10_p) else np.inf,
        'contained':br.lower_log_p<=true.log_p+1e-9 and br.upper_log_p>=true.log_p-1e-9,
        'optimized_theta':br.optimized_theta,
    })
df=pd.DataFrame(rows);df.to_csv(ROOT/'trace_cap_range_core_audit.csv',index=False)
old=pd.read_csv(ROOT/'certify_after_prune_range_core.csv')[['depth','bracket_width_decades']].rename(columns={'bracket_width_decades':'v07_weyl_width_decades'})
comp=df.merge(old,on='depth',how='left');comp['upper_improvement_vs_v07_width']=comp['v07_weyl_width_decades']/comp['upper_gap_decades']
comp.to_csv(ROOT/'trace_cap_vs_weyl.csv',index=False)
print(df.to_string(index=False))

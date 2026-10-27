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
from residual_completion import residual_rank_bounds, complete_residual_range
from kcos_v2 import adaptive_kcos_logsf

rng=np.random.default_rng(20260923)
phases,width=10,5;widths=[width]*phases;m=50
L=np.zeros((m,m))
for h in range(phases):
    sh=slice(h*width,(h+1)*width)
    L[sh,sh]=1.8*np.eye(width)+.04*rng.normal(size=(width,width))
    if h+1<phases:
        sg=slice((h+1)*width,(h+2)*width)
        L[sh,sg]=.10*rng.normal(size=(width,width))
H=L.T@L
E=np.zeros_like(H)
for h in range(phases):
    for g in range(h+2,phases):
        sh=slice(h*width,(h+1)*width);sg=slice(g*width,(g+1)*width)
        C=rng.normal(size=(width,width));E[sh,sg]=C;E[sg,sh]=C.T
E/=np.linalg.norm(E,2);H+=.015*E
mi=np.linalg.eigvalsh(H).min()
if mi<=1e-8:H+=(abs(mi)+.05)*np.eye(m)
H/=np.linalg.norm(H,2)
A=np.linalg.cholesky(H).T
true_sv=np.linalg.svd(A,compute_uv=False)
true_lam=true_sv**2

Bphase=block_transfer_matrix(H,widths)
X=np.zeros((m,2));X[:width]=rng.normal(size=(width,2))
rho=phase_norm_vector(X,widths)
risks=edge_risks_depth(Bphase,rho,5)
sched=dual_budget_greedy_schedule(Bphase,risks,query_budget=.05,operator_budget=.005)
starts=np.cumsum([0]+widths);H0=H.copy()
for h,g in sched.omitted_pairs:
    sh=slice(starts[h],starts[h+1]);sg=slice(starts[g],starts[g+1])
    H0[sh,sg]=0;H0[sg,sh]=0
H0=.5*(H0+H0.T)

V0=np.zeros((m,6));V0[:width,:5]=rng.normal(size=(width,5));V0[width:2*width,5:6]=rng.normal(size=(width,1))
def basis(depth):
    blocks=[];V=V0.copy()
    for _ in range(depth):
        if blocks:
            Q=np.column_stack(blocks);V-=Q@(Q.T@V);V-=Q@(Q.T@V)
        Qv,R=np.linalg.qr(V,mode='reduced')
        d=np.abs(np.diag(R)) if R.size else np.array([])
        sc=max(float(d.max()) if d.size else 0.,1.)
        Qv=Qv[:,d>1e-11*sc] if d.size else Qv
        if not Qv.shape[1]:break
        blocks.append(Qv);V=H0@Qv
    return np.column_stack(blocks) if blocks else np.zeros((m,0))

def q_for_p(p):
    mean=float(np.sum(true_lam));sd=math.sqrt(2*np.sum(true_lam**2));logt=math.log(p)
    lo=mean*(1+1e-10);hi=mean+3*sd
    def f(q):return adaptive_kcos_logsf(q,true_lam,relative_tolerance=1e-10).log_p-logt
    while f(hi)>0:hi+=3*sd
    return brentq(f,lo,hi,xtol=1e-10,rtol=1e-11)
q=q_for_p(1e-8)
true_tail=adaptive_kcos_logsf(q,true_lam,relative_tolerance=1e-10)

rows=[]
for depth in range(2,9):
    V=basis(depth);U,_=np.linalg.qr(A@V,mode='reduced')
    cert=residual_spectrum_certificate(A,U,compute_square_trace=True)
    b=residual_rank_bounds(A,U)
    comp=complete_residual_range(A,U)
    sv_comp=comp.completed_singular_values
    relspec=np.linalg.norm(sv_comp-true_sv)/np.linalg.norm(true_sv)
    lam_comp=sv_comp**2
    tail=adaptive_kcos_logsf(q,lam_comp,relative_tolerance=1e-10)
    pre=trace_moment_tail_bracket(q,cert,relative_tolerance=1e-8)
    rows.append({
        'depth':depth,
        'basis_dim':U.shape[1],
        'orthogonal_complement_dim':A.shape[0]-U.shape[1],
        'stable_rank_lower':b.stable_rank_lower,
        'second_moment_rank_lower':b.second_moment_rank_lower,
        'integer_rank_lower':b.integer_lower_bound,
        'rank_upper':b.orthogonal_complement_upper_bound,
        'rank_certified_from_moments':b.rank_certified,
        'certified_rank':b.certified_rank if b.certified_rank is not None else np.nan,
        'actual_residual_rank':comp.residual_rank,
        'completed_basis_dim':comp.completed_basis_dim,
        'precompletion_tail_width_decades':pre.bracket_width_decades,
        'completed_spectrum_rel_error':relspec,
        'completed_tail_log10_p':tail.log10_p,
        'completed_tail_abs_decade_error':abs(tail.log10_p-true_tail.log10_p),
    })

df=pd.DataFrame(rows)
df.to_csv(ROOT/'residual_completion_audit.csv',index=False)
print(df.to_string(index=False,formatters={
    'stable_rank_lower':lambda x:f'{x:.3f}',
    'second_moment_rank_lower':lambda x:f'{x:.3f}',
    'precompletion_tail_width_decades':lambda x:f'{x:.3f}',
    'completed_spectrum_rel_error':lambda x:f'{x:.3e}',
    'completed_tail_log10_p':lambda x:f'{x:.8f}',
    'completed_tail_abs_decade_error':lambda x:f'{x:.3e}',
}))

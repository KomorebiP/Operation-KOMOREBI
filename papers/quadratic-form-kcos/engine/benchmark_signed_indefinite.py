from __future__ import annotations
import math, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from quadratic_form_engine import SignedCentralQuadraticFormEngine
from generalized_tail import signed_cgf, signed_saddlepoint, signed_derivative, signed_central_logsf
from generalized_packets import packetized_signed_central_logsf

HERE=Path(__file__).resolve().parent


def tilted_importance_sampling(q,w,draws=50000,batch=1000,seed=1234):
    rng=np.random.default_rng(seed)
    w=np.asarray(w,dtype=np.float64)
    theta=signed_saddlepoint(q,w)
    Ktheta=float(np.real(signed_cgf(theta,w)))
    denom=1.0-2.0*theta*w
    total=0.0; total2=0.0; n=0
    while n<draws:
        b=min(batch,draws-n)
        z2=rng.chisquare(1.0,size=(b,w.size))
        qs=(z2*(w/denom)[None,:]).sum(axis=1)
        logw=Ktheta-theta*qs
        vals=np.exp(logw)*(qs>=q)
        total+=float(vals.sum()); total2+=float(np.dot(vals,vals)); n+=b
    mean=total/draws
    var=max(total2/draws-mean*mean,0.0)
    se=math.sqrt(var/draws)
    return mean,se,theta


def main():
    exact_rows=[]
    # Finite upper endpoint: Q=-0.02 chi2_80.
    eng=SignedCentralQuadraticFormEngine.from_spectrum(-0.02*np.ones(80),source='finite endpoint')
    for p in [1e-8,1e-30,1e-100,1e-200]:
        x=stats.chi2.ppf(p,80); q=-0.02*x
        r=eng.logsf(q,relative_tolerance=1e-9,max_K=262144)
        exact_rows.append(dict(family='-0.02 chi2_80',target_p=p,q=q,computed_log10_p=r.log10_p,
                               exact_log10_p=math.log10(p),error_decades=r.log10_p-math.log10(p),
                               certificate=r.certified_relative_bound,passed=r.certificate_passed))
    # Exact mixed-sign Laplace control: a(chi2_2-chi2_2) ~ Laplace(0,2a).
    a=.07; wlap=np.array([a,a,-a,-a]); englap=SignedCentralQuadraticFormEngine.from_spectrum(wlap,source='Laplace mixed control')
    for p in [1e-4,1e-8,1e-20,1e-50,1e-100,1e-200]:
        q=2*a*math.log(.5/p)
        r=englap.logsf(q,relative_tolerance=1e-9,max_K=262144,max_iter=40)
        exact_rows.append(dict(family='0.07*(chi2_2-chi2_2)',target_p=p,q=q,computed_log10_p=r.log10_p,
                               exact_log10_p=math.log10(p),error_decades=r.log10_p-math.log10(p),
                               certificate=r.certified_relative_bound,passed=r.certificate_passed))
    pd.DataFrame(exact_rows).to_csv(HERE/'signed_exact_controls.csv',index=False)

    # High-rank mixed multiscale spectrum.
    rng=np.random.default_rng(44)
    pos=np.exp(rng.uniform(math.log(.002),math.log(.08),180))
    neg=-np.exp(rng.uniform(math.log(.001),math.log(.04),160))
    w=np.r_[pos,neg]
    rows=[]
    for i,frac in enumerate([.90,.94,.97,.985,.995]):
        theta=frac/(2*np.max(pos)); q=signed_derivative(theta,w,1)
        t=time.perf_counter(); packet=packetized_signed_central_logsf(q,w,relative_tolerance=1e-8,max_K=262144,max_iter=28); packet_sec=time.perf_counter()-t
        # Unpacketized same-method reference for representation error.
        t=time.perf_counter(); exact=signed_central_logsf(q,w,relative_tolerance=1e-9,max_K=262144,max_iter=28); exact_sec=time.perf_counter()-t
        # Independent importance sampling check.
        est,se,_=tilted_importance_sampling(q,w,draws=50000,batch=1000,seed=500+i)
        ppacket=math.exp(packet.log_p) if packet.log_p>-745 else 0.0
        z=(ppacket-est)/se if se>0 and ppacket>0 else math.nan
        rows.append(dict(theta_fraction=frac,q=q,rank=w.size,packet_log10_p=packet.log10_p,
                         exact_grid_log10_p=exact.log10_p,difference_decades=packet.log10_p-exact.log10_p,
                         packet_certificate=packet.certified_relative_bound,packet_passed=packet.passed,
                         K=packet.K,L=packet.L,packet_count=packet.packet_count,packet_order=packet.packet_order,
                         packet_seconds=packet_sec,exact_seconds=exact_sec,importance_sampling_p=est,
                         importance_sampling_se=se,difference_in_mc_se=z))
    pd.DataFrame(rows).to_csv(HERE/'signed_mixed_highrank_audit.csv',index=False)

    print(pd.DataFrame(exact_rows).to_string(index=False))
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=='__main__': main()

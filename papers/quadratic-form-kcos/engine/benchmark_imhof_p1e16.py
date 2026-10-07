import sys, math, time, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq
import mpmath as mp

ROOT=Path('/mnt/data/_qf_v15_full')
sys.path.insert(0,str(ROOT))
from kcos_v2_hardened import adaptive_kcos_logsf

CASES=[
    dict(name='balanced_r80', weights=[0.04,0.06,0.09,0.12,0.16], mult=[16,16,16,16,16], U1=60, U2=80),
    dict(name='skewed_r80', weights=[0.02,0.035,0.07,0.16,0.40], mult=[20,20,16,16,8], U1=80, U2=100),
    dict(name='spiky_r80', weights=[0.015,0.025,0.05,0.10,0.25,0.80], mult=[24,18,14,10,8,6], U1=100, U2=120),
    dict(name='balanced_r120', weights=[0.04,0.06,0.09,0.12,0.16], mult=[24,24,24,24,24], U1=40, U2=60),
]
TARGET=-16.0

def kcos_log10(q, lam):
    r=adaptive_kcos_logsf(q,lam,relative_tolerance=1e-12,K_initial=128,L_initial=12,max_K=262144)
    return float(r.log10_p), float(r.certificate.certified_relative_bound)

def find_q(lam):
    mean=float(np.sum(lam)); sd=float(np.sqrt(2*np.sum(lam*lam)))
    lo=mean+1e-10*max(sd,1.0)
    hi=mean+12*sd
    while kcos_log10(hi,lam)[0] > TARGET:
        hi=mean+2*(hi-mean)
    f=lambda q: kcos_log10(q,lam)[0]-TARGET
    return brentq(f,lo,hi,xtol=5e-14,rtol=5e-15,maxiter=80)

def imhof_tail(q, weights, mult, U, dps=80, step=1.0):
    mp.mp.dps=dps
    w=[mp.mpf(str(x)) for x in weights]
    h=[int(x) for x in mult]
    qmp=mp.mpf(str(q))
    def fun(u):
        if u == 0:
            return mp.mpf('0.5')*(mp.fsum([hh*ww for hh,ww in zip(h,w)])-qmp)
        theta=mp.mpf('0.5')*mp.fsum([hh*mp.atan(ww*u) for hh,ww in zip(h,w)])-mp.mpf('0.5')*qmp*u
        logrho=mp.mpf('0.25')*mp.fsum([hh*mp.log1p((ww*u)**2) for hh,ww in zip(h,w)])
        return mp.sin(theta)/(u*mp.e**logrho)
    pts=[mp.mpf('0')]
    x=step
    while x < U:
        pts.append(mp.mpf(str(x)))
        x += step
    pts.append(mp.mpf(str(U)))
    t=time.perf_counter()
    integ=mp.quad(fun, pts)
    sf=mp.mpf('0.5')+integ/mp.pi
    elapsed=time.perf_counter()-t
    rank=sum(h); p=mp.mpf(rank)/2
    C=mp.mpf('1')
    for ww,hh in zip(w,h): C *= ww**(-mp.mpf(hh)/2)
    tail=C/(mp.pi*p)*(mp.mpf(str(U))**(-p))
    return sf, tail, elapsed

def run_case(case):
    weights=case['weights']; mult=case['mult']
    lam=np.concatenate([np.full(h,w,dtype=float) for w,h in zip(weights,mult)])
    q=find_q(lam)
    kr=kcos_log10(q,lam)
    sf1,b1,t1=imhof_tail(q,weights,mult,case['U1'],dps=70,step=1.0)
    sf2,b2,t2=imhof_tail(q,weights,mult,case['U2'],dps=90,step=1.0)
    with mp.workdps(90):
        log1=mp.log10(sf1); log2=mp.log10(sf2)
        diff=mp.mpf(str(kr[0]))-log2
        conv=log2-log1
        rel=mp.expm1(mp.log(10)*abs(diff))
        convrel=mp.expm1(mp.log(10)*abs(conv))
        tailrel=b2/sf2
    return {
        'case':case['name'], 'rank':int(lam.size), 'distinct_weights':len(weights),
        'q':q, 'kcos_log10_p':kr[0], 'kcos_certificate':kr[1],
        'imhof_U1':case['U1'], 'imhof_U2':case['U2'],
        'imhof_log10_p_U1':mp.nstr(log1,30), 'imhof_log10_p_U2':mp.nstr(log2,30),
        'kcos_minus_imhof_decades':mp.nstr(diff,20),
        'implied_relative_difference':mp.nstr(rel,20),
        'imhof_convergence_decades':mp.nstr(conv,20),
        'imhof_convergence_relative':mp.nstr(convrel,20),
        'imhof_tail_bound_abs_p':mp.nstr(b2,20),
        'imhof_tail_bound_relative_to_p':mp.nstr(tailrel,20),
        'imhof_seconds_U1':t1,'imhof_seconds_U2':t2,
    }

if __name__=='__main__':
    import concurrent.futures
    t0=time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as ex:
        results=list(ex.map(run_case,CASES))
    df=pd.DataFrame(results)
    out='/mnt/data/imhof_heterogeneous_p1e16_battery.csv'
    df.to_csv(out,index=False)
    print(df.to_string(index=False))
    print('TOTAL_SECONDS',time.perf_counter()-t0)
    print(out)

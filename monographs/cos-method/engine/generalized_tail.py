from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy import optimize


@dataclass(frozen=True)
class GeneralizedLogResult:
    log_p: float
    log10_p: float
    p_value: float
    certified_relative_bound: float
    support_alias_tilted_bound: float
    cos_series_tilted_bound: float
    tilted_sum: float
    theta: float
    lower: float
    upper: float
    K: int
    L: float
    passed: bool
    note: str


def _float_probability(logp):
    floor=math.log(np.nextafter(0.0,1.0))
    return math.exp(logp) if logp>floor else 0.0


# ------------------------------------------------------------------
# Noncentral positive generalized chi-square
# Q = sum_j lambda_j * chi2_{df_j}(nc_j), lambda_j > 0.
# ------------------------------------------------------------------

def nc_cgf(s, weights, df, nc):
    w=np.asarray(weights,dtype=np.float64)
    k=np.asarray(df,dtype=np.float64)
    d=np.asarray(nc,dtype=np.float64)
    sv=np.atleast_1d(np.asarray(s,dtype=np.complex128))
    den=1.0-2.0*sv[:,None]*w[None,:]
    out=-0.5*np.sum(k[None,:]*np.log(den),axis=1)
    out+=np.sum(d[None,:]*(sv[:,None]*w[None,:])/den,axis=1)
    return out if np.ndim(s) else out[0]


def nc_cgf_derivative(theta, weights, df, nc, order):
    w=np.asarray(weights,dtype=np.float64)
    k=np.asarray(df,dtype=np.float64)
    d=np.asarray(nc,dtype=np.float64)
    r=int(order)
    den=1.0-2.0*theta*w
    central=(2**(r-1))*math.factorial(r-1)*np.sum(k*w**r/den**r)
    noncentral=(2**(r-1))*math.factorial(r)*np.sum(d*w**r/den**(r+1))
    return float(central+noncentral)


def nc_saddlepoint(q, weights, df, nc):
    w=np.asarray(weights,dtype=np.float64)
    mean=nc_cgf_derivative(0.0,w,df,nc,1)
    if q<=mean:
        return 0.0
    hi=(1.0/(2.0*np.max(w)))*(1.0-1e-12)
    return float(optimize.brentq(lambda t:nc_cgf_derivative(t,w,df,nc,1)-q,
                                 0.0,hi,xtol=1e-14,rtol=1e-13))


def _positive_payoff_integrals(q,theta,upper,K):
    u=np.arange(K,dtype=np.float64)*math.pi/upper
    s=theta+1j*u
    ell=upper-q
    I=np.real(np.exp(1j*u*q)*(1.0-np.exp((-theta+1j*u)*ell))/(theta-1j*u))
    I[0]*=.5
    return u,s,I


def _nc_tilted_sum(q,w,k,nc,theta,upper,K,Ktheta):
    _,s,I=_positive_payoff_integrals(q,theta,upper,K)
    phi=np.exp(nc_cgf(s,w,k,nc)-Ktheta)
    S=(2.0/upper)*math.fsum(float(x) for x in I*np.real(phi))
    return float(S)


def _nc_chernoff_upper(w,k,nc,theta,b):
    hi=(1.0/(2.0*np.max(w)))*(1.0-1e-12)
    eta=float(optimize.brentq(lambda x:nc_cgf_derivative(x,w,k,nc,1)-b,
                              theta,hi,xtol=1e-14,rtol=1e-13))
    logb=float(np.real(nc_cgf(eta,w,k,nc)-nc_cgf(theta,w,k,nc)-(eta-theta)*b))
    return min(1.0,math.exp(logb))


def _nc_series_bound(w,k,nc,theta,upper,K):
    t0=K*math.pi/upper
    a=2.0*w/(1.0-2.0*theta*w)
    x=(a*t0)**2
    # Noncentrality adds extra damping, so the central envelope is conservative.
    logphi=-0.25*np.sum(k*np.log1p(x))
    beta=0.5*np.sum(k*x/(1+x))
    if beta<=0:return math.inf
    logb=math.log(4/math.pi)+float(logphi)+math.log(1/K+1/beta)
    return 0.0 if logb<-745 else math.exp(logb)


def noncentral_positive_logsf(q, weights, df=None, nc=None, *, relative_tolerance=1e-8,
                              K_initial=64,L_initial=10.0,max_K=262144,max_iter=24):
    w=np.asarray(weights,dtype=np.float64)
    if np.any(w<=0):raise ValueError('weights must be positive')
    if df is None: df=np.ones(w.size)
    if nc is None: nc=np.zeros(w.size)
    k=np.broadcast_to(np.asarray(df,dtype=np.float64),w.shape).copy()
    d=np.broadcast_to(np.asarray(nc,dtype=np.float64),w.shape).copy()
    if np.any(k<=0) or np.any(d<0):raise ValueError('invalid df/noncentrality')
    theta=nc_saddlepoint(q,w,k,d)
    if theta<=0:raise ValueError('q must exceed the mean')
    Ktheta=float(np.real(nc_cgf(theta,w,k,d)))
    logpref=Ktheta-theta*q
    c2=nc_cgf_derivative(theta,w,k,d,2); c4=nc_cgf_derivative(theta,w,k,d,4)
    scale=math.sqrt(c2+math.sqrt(c4))
    K=int(K_initial); L=float(L_initial); last=None
    for _ in range(max_iter):
        upper=q+L*scale
        S=_nc_tilted_sum(q,w,k,d,theta,upper,K,Ktheta)
        support=_nc_chernoff_upper(w,k,d,theta,upper)*(1+math.exp(-theta*(upper-q)))
        series=_nc_series_bound(w,k,d,theta,upper,K)
        total=support+series
        rel=total/(S-total) if S>total else math.inf
        last=(S,support,series,rel,upper,K,L)
        if rel<=relative_tolerance and S>0:
            logp=logpref+math.log(S)
            return GeneralizedLogResult(logp,logp/math.log(10),_float_probability(logp),rel,
                support,series,S,theta,0.0,upper,K,L,True,
                'Exact noncentral CGF; analytic support/COS truncation certificate; no packet compression.')
        if support>=series:L+=1
        else:
            if K>=max_K:break
            K=min(max_K,2*K)
    S,support,series,rel,upper,K,L=last
    logp=logpref+math.log(S) if S>0 else -math.inf
    return GeneralizedLogResult(logp,logp/math.log(10),_float_probability(logp),rel,
        support,series,S,theta,0.0,upper,K,L,False,'Refinement cap reached.')


# ------------------------------------------------------------------
# Signed central generalized chi-square
# Q = sum_j lambda_j Z_j^2, lambda_j may have either sign.
# ------------------------------------------------------------------

def signed_cgf(s,weights):
    w=np.asarray(weights,dtype=np.float64)
    sv=np.atleast_1d(np.asarray(s,dtype=np.complex128))
    out=-0.5*np.sum(np.log(1.0-2.0*sv[:,None]*w[None,:]),axis=1)
    return out if np.ndim(s) else out[0]


def signed_derivative(theta,weights,order):
    w=np.asarray(weights,dtype=np.float64); r=int(order)
    return float((2**(r-1))*math.factorial(r-1)*np.sum(w**r/(1-2*theta*w)**r))


def _signed_domain(w):
    pos=w[w>0]; neg=w[w<0]
    lo=max([1/(2*x) for x in neg],default=-math.inf)
    hi=min([1/(2*x) for x in pos],default=math.inf)
    return lo,hi


def signed_saddlepoint(q,w):
    w=np.asarray(w,dtype=np.float64); mean=float(np.sum(w)); lo,hi=_signed_domain(w)
    if q<=mean:raise ValueError('this implementation currently handles right tails q>mean')
    left=0.0
    if math.isfinite(hi): right=hi*(1-1e-12)
    else:
        right=1.0
        while signed_derivative(right,w,1)<q:right*=2
    return float(optimize.brentq(lambda t:signed_derivative(t,w,1)-q,left,right,
                                 xtol=1e-14,rtol=1e-13))


def _signed_payoff(q,theta,a,b,K):
    width=b-a
    u=np.arange(K,dtype=np.float64)*math.pi/width
    ell=b-q
    I=np.real(np.exp(1j*u*(q-a))*(1-np.exp((-theta+1j*u)*ell))/(theta-1j*u))
    I[0]*=.5
    return u,theta+1j*u,I,width


def _signed_tilted_sum(q,w,theta,a,b,K,Ktheta):
    u,s,I,width=_signed_payoff(q,theta,a,b,K)
    phi=np.exp(signed_cgf(s,w)-Ktheta)
    # phase shift belongs to the density coefficient.
    coeff=np.real(phi*np.exp(-1j*u*a))
    # I already uses cos(u(x-a)); do not apply the phase twice.  Therefore use
    # an equivalent unshifted complex integral directly instead.
    J=np.real(np.exp(1j*u*(q-a))*(1-np.exp((-theta+1j*u)*(b-q)))/(theta-1j*u))
    J[0]*=.5
    S=(2.0/width)*math.fsum(float(x) for x in coeff*J)
    return float(S)


def _signed_chernoff(w,theta,x,side):
    lo,hi=_signed_domain(w); Kt=float(np.real(signed_cgf(theta,w)))
    if side=='upper':
        # If all weights are nonpositive, support is <=0.
        if not np.any(w>0) and x>=0:return 0.0
        if math.isfinite(hi): end=hi*(1-1e-12)
        else:
            end=max(theta+1.0,1.0)
            while signed_derivative(end,w,1)<x:end*=2
        eta=float(optimize.brentq(lambda s:signed_derivative(s,w,1)-x,theta,end,
                                  xtol=1e-14,rtol=1e-13))
    else:
        if not np.any(w<0) and x<=0:return 0.0
        if math.isfinite(lo): end=lo+(theta-lo)*1e-12
        else:
            end=min(theta-1.0,-1.0)
            while signed_derivative(end,w,1)>x:end*=2
        eta=float(optimize.brentq(lambda s:signed_derivative(s,w,1)-x,end,theta,
                                  xtol=1e-14,rtol=1e-13))
    logb=float(np.real(signed_cgf(eta,w)-Kt-(eta-theta)*x))
    return min(1.0,math.exp(logb))


def _signed_series_bound(w,theta,a,b,K):
    width=b-a; t0=K*math.pi/width
    aa=2*w/(1-2*theta*w); x=(aa*t0)**2
    logphi=-.25*np.sum(np.log1p(x)); beta=.5*np.sum(x/(1+x))
    if beta<=0:return math.inf
    # |J_k| <= 2/u_k and width cancels as in the positive derivation.
    logb=math.log(4/math.pi)+float(logphi)+math.log(1/K+1/beta)
    return 0.0 if logb<-745 else math.exp(logb)


def signed_central_logsf(q,weights,*,relative_tolerance=1e-8,K_initial=64,L_initial=10,
                         max_K=262144,max_iter=24):
    w=np.asarray(weights,dtype=np.float64)
    if not np.any(w!=0):raise ValueError('nonzero weight required')
    theta=signed_saddlepoint(q,w)
    Ktheta=float(np.real(signed_cgf(theta,w))); logpref=Ktheta-theta*q
    c2=signed_derivative(theta,w,2); c4=signed_derivative(theta,w,4)
    scale=math.sqrt(c2+math.sqrt(abs(c4)))
    K=int(K_initial); L=float(L_initial); last=None
    for _ in range(max_iter):
        a=q-L*scale; b=q+L*scale
        # Respect finite one-sided support when present.
        if not np.any(w<0):a=max(0.0,a)
        if not np.any(w>0):b=min(0.0,b)
        S=_signed_tilted_sum(q,w,theta,a,b,K,Ktheta)
        pl=_signed_chernoff(w,theta,a,'lower')
        pu=_signed_chernoff(w,theta,b,'upper')
        support=pl+pu*(1+math.exp(-theta*(b-q)))
        series=_signed_series_bound(w,theta,a,b,K)
        total=support+series; rel=total/(S-total) if S>total else math.inf
        last=(S,support,series,rel,a,b,K,L)
        if rel<=relative_tolerance and S>0:
            logp=logpref+math.log(S)
            return GeneralizedLogResult(logp,logp/math.log(10),_float_probability(logp),rel,
                support,series,S,theta,a,b,K,L,True,
                'Exact signed central CGF; two-sided tilted support/alias plus COS-series certificate.')
        if support>=series:L+=1
        else:
            if K>=max_K:break
            K=min(max_K,2*K)
    S,support,series,rel,a,b,K,L=last
    logp=logpref+math.log(S) if S>0 else -math.inf
    return GeneralizedLogResult(logp,logp/math.log(10),_float_probability(logp),rel,
        support,series,S,theta,a,b,K,L,False,'Refinement cap reached.')

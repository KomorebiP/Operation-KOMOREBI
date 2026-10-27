from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from generalized_tail import (
    signed_cgf, signed_derivative, signed_saddlepoint,
    _signed_chernoff, _signed_series_bound,
    nc_cgf, nc_cgf_derivative, nc_saddlepoint,
    _nc_chernoff_upper, _nc_series_bound,
)


@dataclass
class _CentralNode:
    values: np.ndarray
    center: float
    moments: np.ndarray
    radius: float
    bound: np.ndarray

    @property
    def splittable(self):
        return self.values.size > 1


@dataclass
class _NCNode:
    w: np.ndarray
    df: np.ndarray
    nc: np.ndarray
    center: float
    df_moments: np.ndarray
    nc_moments: np.ndarray
    radius: float
    bound: np.ndarray

    @property
    def splittable(self):
        return self.w.size > 1


@dataclass(frozen=True)
class PacketizedGeneralizedResult:
    log_p: float
    log10_p: float
    p_value: float
    certified_relative_bound: float
    packet_tilted_bound: float
    support_alias_tilted_bound: float
    cos_series_tilted_bound: float
    tilted_sum: float
    theta: float
    lower: float
    upper: float
    K: int
    L: float
    packet_count: int
    packet_order: int
    original_rank: int
    passed: bool
    note: str


def _float_p(logp):
    return math.exp(logp) if logp > math.log(np.nextafter(0.0,1.0)) else 0.0


def _gap_split(values, gap_ratio=3.0):
    """Split a sorted same-sign array at large multiplicative gaps."""
    v=np.asarray(values,dtype=np.float64)
    if v.size <= 1:
        return [v]
    # For negative values use magnitudes but preserve ordering within block.
    a=np.abs(v)
    # sorted caller guarantees local monotonic magnitudes sufficiently for gap use.
    ratios=np.maximum(a[:-1],a[1:])/np.maximum(np.minimum(a[:-1],a[1:]),np.finfo(float).tiny)
    cuts=np.flatnonzero(ratios >= gap_ratio)+1
    return [x for x in np.split(v,cuts) if x.size]


def _initial_signed_blocks(weights, gap_ratio=3.0):
    w=np.asarray(weights,dtype=np.float64)
    pos=np.sort(w[w>0])[::-1]
    neg=np.sort(w[w<0])  # most negative to least negative
    blocks=[]
    if pos.size:
        blocks.extend(_gap_split(pos,gap_ratio))
    if neg.size:
        blocks.extend(_gap_split(neg,gap_ratio))
    return blocks


def _central_node(values, order, s_grid):
    values=np.asarray(values,dtype=np.float64)
    mu=float(np.mean(values))
    delta=values-mu
    moments=np.array([np.sum(delta**n) for n in range(order+1)],dtype=np.float64)
    radius=float(np.max(np.abs(delta))) if delta.size else 0.0
    if radius==0.0:
        bound=np.zeros(s_grid.size,dtype=np.float64)
    else:
        d=1-2*s_grid*mu
        alpha=2*s_grid/d
        rho=np.abs(alpha)*radius
        with np.errstate(over="ignore",divide="ignore",invalid="ignore"):
            bound=0.5*values.size*rho**(order+1)/((order+1)*np.maximum(1-rho,np.finfo(float).tiny))
        bound[rho>=1]=np.inf
    return _CentralNode(values,mu,moments,radius,bound)


def _central_packet_cgf(s_grid, nodes, order):
    s=np.asarray(s_grid,dtype=np.complex128)
    out=np.zeros(s.size,dtype=np.complex128)
    for node in nodes:
        mu=node.center
        d=1-2*s*mu
        alpha=2*s/d
        out += -0.5*node.moments[0]*np.log(d)
        for n in range(1,order+1):
            out += 0.5*(alpha**n)*node.moments[n]/n
    return out


def _nc_node(w,df,nc,order,s_grid):
    w=np.asarray(w,dtype=np.float64)
    df=np.asarray(df,dtype=np.float64)
    nc=np.asarray(nc,dtype=np.float64)
    mu=float(np.average(w,weights=np.maximum(df+nc,1e-300)))
    delta=w-mu
    dfm=np.array([np.sum(df*delta**n) for n in range(order+1)],dtype=np.float64)
    ncm=np.array([np.sum(nc*delta**n) for n in range(order+1)],dtype=np.float64)
    radius=float(np.max(np.abs(delta))) if delta.size else 0.0
    if radius==0:
        bound=np.zeros(s_grid.size,dtype=np.float64)
    else:
        d=1-2*s_grid*mu
        alpha=2*s_grid/d
        rho=np.abs(alpha)*radius
        den=np.maximum(1-rho,np.finfo(float).tiny)
        with np.errstate(over="ignore",divide="ignore",invalid="ignore"):
            bcentral=0.5*dfm[0]*rho**(order+1)/((order+1)*den)
            bnc=0.5*ncm[0]*rho**(order+1)/(np.abs(d)*den)
            bound=bcentral+bnc
        bound[rho>=1]=np.inf
    return _NCNode(w,df,nc,mu,dfm,ncm,radius,bound)


def _nc_packet_cgf(s_grid,nodes,order):
    s=np.asarray(s_grid,dtype=np.complex128)
    out=np.zeros(s.size,dtype=np.complex128)
    for node in nodes:
        mu=node.center
        d=1-2*s*mu
        alpha=2*s/d
        # central degrees-of-freedom contribution
        out += -0.5*node.df_moments[0]*np.log(d)
        for n in range(1,order+1):
            out += 0.5*alpha**n*node.df_moments[n]/n
        # noncentral contribution:
        # s lambda/(1-2s lambda) = -1/2 + [2(1-2s lambda)]^-1
        out += -0.5*node.nc_moments[0]
        series=np.zeros(s.size,dtype=np.complex128)
        for n in range(order+1):
            series += alpha**n*node.nc_moments[n]
        out += 0.5*series/d
    return out


def _signed_integrals(q,theta,a,b,K):
    width=b-a
    u=np.arange(K,dtype=np.float64)*math.pi/width
    J=np.real(np.exp(1j*u*(q-a))*(1-np.exp((-theta+1j*u)*(b-q)))/(theta-1j*u))
    weights=np.ones(K); weights[0]=0.5
    return u,theta+1j*u,weights*J,width


def _positive_integrals(q,theta,b,K):
    u=np.arange(K,dtype=np.float64)*math.pi/b
    J=np.real(np.exp(1j*u*q)*(1-np.exp((-theta+1j*u)*(b-q)))/(theta-1j*u))
    weights=np.ones(K); weights[0]=0.5
    return u,theta+1j*u,weights*J,b


def _logsumexp(values):
    values=np.asarray(values,dtype=np.float64)
    finite=np.isfinite(values)
    if not np.any(finite):
        return -math.inf
    vals=values[finite]
    m=float(np.max(vals))
    return m+math.log(float(np.sum(np.exp(vals-m))))


def _log_expm1_nonnegative(x):
    x=np.asarray(x,dtype=np.float64)
    out=np.full_like(x,-math.inf)
    pos=x>0.0
    moderate=pos & (x<=50.0)
    large=pos & (x>50.0)
    if np.any(moderate):
        out[moderate]=np.log(np.expm1(x[moderate]))
    if np.any(large):
        xl=x[large]
        out[large]=xl+np.log1p(-np.exp(-xl))
    return out


def _packet_error_log(bound,weighted_integrals,width):
    if np.any(~np.isfinite(bound)):
        return math.inf
    absw=np.abs(np.asarray(weighted_integrals,dtype=np.float64))
    logw=np.full_like(absw,-math.inf)
    nz=absw>0.0
    logw[nz]=np.log(absw[nz])
    loggrowth=_log_expm1_nonnegative(bound)
    logsum=_logsumexp(logw+loggrowth)
    if logsum==-math.inf:
        return -math.inf
    return math.log(2.0/width)+logsum


def _float_from_log(logv):
    if logv==-math.inf:
        return 0.0
    if not math.isfinite(logv):
        return math.inf
    if logv>math.log(np.finfo(float).max):
        return math.inf
    if logv<math.log(np.nextafter(0.0,1.0)):
        return 0.0
    return float(math.exp(logv))


def _packet_error(bound,weighted_integrals,width):
    return _float_from_log(_packet_error_log(bound,weighted_integrals,width))


def _split_worst_central(nodes,order,s_grid):
    candidates=[(float(np.max(n.bound)),i) for i,n in enumerate(nodes) if n.splittable]
    if not candidates:
        raise RuntimeError("no splittable packet remains")
    _,idx=max(candidates)
    node=nodes.pop(idx)
    vals=node.values
    # preserve sign/order and bisect
    mid=vals.size//2
    nodes.extend([_central_node(vals[:mid],order,s_grid),_central_node(vals[mid:],order,s_grid)])


def _split_worst_nc(nodes,order,s_grid):
    candidates=[(float(np.max(n.bound)),i) for i,n in enumerate(nodes) if n.splittable]
    if not candidates:
        raise RuntimeError("no splittable packet remains")
    _,idx=max(candidates)
    n=nodes.pop(idx)
    order_idx=np.argsort(n.w)[::-1]
    w=n.w[order_idx]; df=n.df[order_idx]; nc=n.nc[order_idx]
    mid=w.size//2
    nodes.extend([
        _nc_node(w[:mid],df[:mid],nc[:mid],order,s_grid),
        _nc_node(w[mid:],df[mid:],nc[mid:],order,s_grid),
    ])


def packetized_signed_central_logsf(
    q,weights,*,relative_tolerance=1e-8,K_initial=64,L_initial=10.0,
    packet_order=8,max_packets=None,gap_ratio=3.0,max_K=262144,max_iter=24,
):
    w=np.asarray(weights,dtype=np.float64)
    w=w[w!=0]
    if w.size==0: raise ValueError("nonzero weight required")
    theta=signed_saddlepoint(q,w)
    Ktheta=float(np.real(signed_cgf(theta,w)))
    logpref=Ktheta-theta*q
    c2=signed_derivative(theta,w,2); c4=signed_derivative(theta,w,4)
    scale=math.sqrt(c2+math.sqrt(abs(c4)))
    K=int(K_initial); L=float(L_initial); order=int(packet_order)
    max_packets=int(max_packets or w.size)
    last=None

    for _ in range(max_iter):
        a=q-L*scale; b=q+L*scale
        if not np.any(w<0): a=max(0.0,a)
        if not np.any(w>0): b=min(0.0,b)
        u,s_grid,I,width=_signed_integrals(q,theta,a,b,K)

        blocks=_initial_signed_blocks(w,gap_ratio=gap_ratio)
        nodes=[_central_node(block,order,s_grid) for block in blocks]

        while True:
            total_bound=np.sum(np.vstack([n.bound for n in nodes]),axis=0)
            Khat=_central_packet_cgf(s_grid,nodes,order)
            delta=Khat-Ktheta
            if np.any(np.real(delta)>math.log(np.finfo(float).max)-4.0):
                if len(nodes)>=max_packets:
                    raise RuntimeError("packet cap reached before stable exponentiation")
                _split_worst_central(nodes,order,s_grid)
                continue
            phi=np.exp(delta)
            coeff=np.real(phi*np.exp(-1j*u*a))
            S=float((2.0/width)*math.fsum(float(x) for x in coeff*I))
            log_pbound=_packet_error_log(total_bound,I,width)
            log_target=(math.log(relative_tolerance)-math.log(4.0)+math.log(max(S,1e-300)))
            if log_pbound <= log_target:
                pbound=_float_from_log(log_pbound)
                break
            if len(nodes)>=max_packets:
                raise RuntimeError("packet cap reached")
            _split_worst_central(nodes,order,s_grid)

        pl=_signed_chernoff(w,theta,a,'lower')
        pu=_signed_chernoff(w,theta,b,'upper')
        support=pl+pu*(1+math.exp(-theta*(b-q)))
        series=_signed_series_bound(w,theta,a,b,K)
        total=pbound+support+series
        rel=total/(S-total) if S>total else math.inf
        last=(S,pbound,support,series,rel,a,b,K,L,len(nodes),order)
        if rel<=relative_tolerance and S>0:
            logp=logpref+math.log(S)
            return PacketizedGeneralizedResult(
                logp,logp/math.log(10),_float_p(logp),rel,pbound,support,series,S,
                theta,a,b,K,L,len(nodes),order,int(w.size),True,
                "Signed central packetized CGF; exact saddlepoint/support geometry."
            )
        dominant=max((pbound,'packet'),(support,'support'),(series,'series'))[1]
        if dominant=='support': L+=1
        elif dominant=='series':
            if K>=max_K: break
            K=min(max_K,2*K)
        else:
            order+=2
            if order>16:
                max_packets=min(int(w.size),max(max_packets,2*len(nodes)))
    if last is None: raise RuntimeError("no refinement")
    S,pbound,support,series,rel,a,b,K,L,npack,order=last
    logp=logpref+math.log(S) if S>0 else -math.inf
    return PacketizedGeneralizedResult(
        logp,logp/math.log(10),_float_p(logp),rel,pbound,support,series,S,
        theta,a,b,K,L,npack,order,int(w.size),False,"resource cap reached"
    )


def packetized_noncentral_positive_logsf(
    q,weights,df=None,nc=None,*,relative_tolerance=1e-8,K_initial=64,L_initial=10.0,
    packet_order=8,max_packets=None,gap_ratio=3.0,max_K=262144,max_iter=24,
):
    w=np.asarray(weights,dtype=np.float64)
    if np.any(w<=0): raise ValueError("weights must be positive")
    k=np.ones(w.size) if df is None else np.broadcast_to(np.asarray(df,dtype=float),w.shape).copy()
    d=np.zeros(w.size) if nc is None else np.broadcast_to(np.asarray(nc,dtype=float),w.shape).copy()
    theta=nc_saddlepoint(q,w,k,d)
    Ktheta=float(np.real(nc_cgf(theta,w,k,d)))
    logpref=Ktheta-theta*q
    c2=nc_cgf_derivative(theta,w,k,d,2); c4=nc_cgf_derivative(theta,w,k,d,4)
    scale=math.sqrt(c2+math.sqrt(c4))
    K=int(K_initial); L=float(L_initial); order=int(packet_order)
    max_packets=int(max_packets or w.size)
    last=None

    # initial gap clusters retain aligned df/nc
    idx=np.argsort(w)[::-1]
    ws=w[idx]; ks=k[idx]; ds=d[idx]
    ratios=ws[:-1]/np.maximum(ws[1:],np.finfo(float).tiny)
    cuts=np.flatnonzero(ratios>=gap_ratio)+1
    index_blocks=np.split(np.arange(ws.size),cuts)

    for _ in range(max_iter):
        b=q+L*scale
        u,s_grid,I,width=_positive_integrals(q,theta,b,K)
        nodes=[_nc_node(ws[ii],ks[ii],ds[ii],order,s_grid) for ii in index_blocks if ii.size]

        while True:
            total_bound=np.sum(np.vstack([n.bound for n in nodes]),axis=0)
            Khat=_nc_packet_cgf(s_grid,nodes,order)
            delta=Khat-Ktheta
            if np.any(np.real(delta)>math.log(np.finfo(float).max)-4.0):
                if len(nodes)>=max_packets:
                    raise RuntimeError("packet cap reached before stable exponentiation")
                _split_worst_nc(nodes,order,s_grid)
                continue
            phi=np.exp(delta)
            S=float((2.0/width)*math.fsum(float(x) for x in I*np.real(phi)))
            log_pbound=_packet_error_log(total_bound,I,width)
            log_target=(math.log(relative_tolerance)-math.log(4.0)+math.log(max(S,1e-300)))
            if log_pbound<=log_target:
                pbound=_float_from_log(log_pbound)
                break
            if len(nodes)>=max_packets:
                raise RuntimeError("packet cap reached")
            _split_worst_nc(nodes,order,s_grid)

        support=_nc_chernoff_upper(w,k,d,theta,b)*(1+math.exp(-theta*(b-q)))
        series=_nc_series_bound(w,k,d,theta,b,K)
        total=pbound+support+series
        rel=total/(S-total) if S>total else math.inf
        last=(S,pbound,support,series,rel,b,K,L,len(nodes),order)
        if rel<=relative_tolerance and S>0:
            logp=logpref+math.log(S)
            return PacketizedGeneralizedResult(
                logp,logp/math.log(10),_float_p(logp),rel,pbound,support,series,S,
                theta,0.0,b,K,L,len(nodes),order,int(w.size),True,
                "Noncentral positive packetized CGF; exact saddlepoint/support geometry."
            )
        dominant=max((pbound,'packet'),(support,'support'),(series,'series'))[1]
        if dominant=='support': L+=1
        elif dominant=='series':
            if K>=max_K: break
            K=min(max_K,2*K)
        else:
            order+=2
            if order>16:
                max_packets=min(int(w.size),max(max_packets,2*len(nodes)))
    if last is None: raise RuntimeError("no refinement")
    S,pbound,support,series,rel,b,K,L,npack,order=last
    logp=logpref+math.log(S) if S>0 else -math.inf
    return PacketizedGeneralizedResult(
        logp,logp/math.log(10),_float_p(logp),rel,pbound,support,series,S,
        theta,0.0,b,K,L,npack,order,int(w.size),False,"resource cap reached"
    )

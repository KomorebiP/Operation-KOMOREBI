"""Small sequential-evidence and positive approximation reference utilities.

Bounds concern predictable conditional means. They do not identify a reset
population table from an arbitrary dependent trajectory. No coverage is
inferred from a realized sample path.
"""
from __future__ import annotations
import math
from numbers import Integral,Real
import numpy as np
import sympy as sp

V=sp.Symbol('v',real=True)
X=sp.Symbol('x',real=True)


def degree(n: int) -> int:
    if isinstance(n,bool) or not isinstance(n,(Integral,sp.Integer)) or not 0<=n<=128:
        raise ValueError('Degree must be an integer between zero and 128.')
    return int(n)


def bernstein(n: int,k: int,x=X):
    n=degree(n)
    if isinstance(k,bool) or not isinstance(k,(Integral,sp.Integer)) or not 0<=k<=n:
        raise ValueError('Invalid Bernstein index.')
    return sp.binomial(n,k)*x**k*(1-x)**(n-k)


def positive_coefficients(expr,n: int, *, split=None):
    """Exact scalar example coefficients on [0,1], optionally split into pieces."""
    n=degree(n)
    intervals=split or [(sp.Integer(0),sp.Integer(1),expr)]
    return [sp.simplify((n+1)*sum(sp.integrate(bernstein(n,k,V)*f,(V,a,b)) for a,b,f in intervals)) for k in range(n+1)]


def reconstruct_bernstein(co,n: int):
    n=degree(n)
    if len(co)!=n+1:raise ValueError('Coefficient count mismatch.')
    return sp.expand(sum(c*bernstein(n,k,X) for k,c in enumerate(co)))


def anytime_radius(n: int,delta: float, *, value_range: float=1.0) -> float:
    if isinstance(n,bool) or not isinstance(n,Integral) or n<1:raise ValueError('Sample count must be positive.')
    if isinstance(delta,bool) or not isinstance(delta,Real) or not math.isfinite(float(delta)) or not 0<delta<1:raise ValueError('delta must lie in (0,1).')
    if not isinstance(value_range,Real) or not math.isfinite(float(value_range)) or value_range<=0:raise ValueError('Value range must be positive and finite.')
    return float(value_range)*math.sqrt(n/2*math.log(2*n*(n+1)/float(delta)))


def dependent_example(n: int=4096,seed: int=20261009) -> dict:
    if isinstance(n,bool) or not isinstance(n,Integral) or n<1:raise ValueError('Invalid path length.')
    rng=np.random.default_rng(seed);prev=0
    rows=[];s_plain=s_gate=s_correct=0.0;d_plain=d_gate=0.0
    for t in range(1,n+1):
        p=.8 if prev else .2;y=int(rng.random()<p);gate=prev
        s_plain+=y-.5;s_gate+=gate*(y-.5);s_correct+=gate*(y-p)
        d_plain+=p-.5;d_gate+=gate*(p-.5)
        radius=anytime_radius(t,.05/3)
        rows.append([t,prev,y,p,s_plain,s_gate,s_correct,d_plain,d_gate,radius])
        prev=y
    a=np.asarray(rows,float)
    return {'seed':seed,'n':n,'delta_total':.05,'test_count':3,
            'columns':['t','previous_y','y','true_conditional_p','plain_residual','gated_residual','correct_gated_residual','plain_drift','gated_drift','radius'],
            'rows':a.tolist(),
            'summary':{'plain_mean_residual':s_plain/n,'gated_mean_residual':s_gate/n,
                       'correct_gated_mean_residual':s_correct/n,'radius_per_sample':radius/n,
                       'lower_average_conditional_tv':max(0.0,(abs(s_gate)-radius)/n),
                       'illustration_not_coverage_estimate':True,
                       'true_drift_inside_band_on_this_path':bool(np.all(np.abs(a[:,5]-a[:,8])<=a[:,9]))}}

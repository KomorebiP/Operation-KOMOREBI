"""Exact reference checks for a declared observable nonlinear signal model.

The confidence theorem is conditional on the specified moment model, predictable
regressors and parameter bounds. Arithmetic replay does not authenticate sensors,
verify those assumptions, or establish empirical statistical coverage.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt
import hashlib
import json
from typing import Any

NODES = (F(-1), F(-1,2), F(0), F(1,2), F(1))
WEIGHTS = (F(7,90), F(16,45), F(2,15), F(16,45), F(7,90))
SCHEMA = 'komorebi.dependent-moment-confidence.v1'
MODEL = 'p_ab(u|s)=1+a*s*u+b*s^2*(3*u^2-1)/2'
MEASURE = {'type':'discrete_reference_measure', 'nodes':[str(x) for x in NODES],
           'weights':[str(w) for w in WEIGHTS]}
ALPHA = F(1,20)

def rat(x:Any)->F:
    if isinstance(x,bool) or not isinstance(x,(str,int,F)):
        raise ValueError('Expected an exact rational value.')
    try:return F(x)
    except (ValueError,ZeroDivisionError) as exc:raise ValueError('Invalid rational.') from exc

def leg2(u:F)->F:return (3*u*u-1)/2

def probability_row(s:F,a:F,b:F)->tuple[F,...]:
    row=tuple(w*(1+a*s*u+b*s*s*leg2(u)) for u,w in zip(NODES,WEIGHTS))
    if min(row)<0 or sum(row)!=1:raise ValueError('Invalid probability row.')
    return row

def sqrt_up(x:F, places:int=12)->F:
    """Rational upper enclosure of sqrt(x), never a float calculation."""
    if x<0 or places<0:raise ValueError('Invalid square-root bound.')
    scale=10**places
    q=isqrt((x.numerator*scale*scale)//x.denominator)
    if F(q*q,scale*scale)<x:q+=1
    return F(q,scale)

def ceil_log2(x:F)->int:
    if x<1:raise ValueError('Log bound is for x >= 1.')
    k=max(0,x.numerator.bit_length()-x.denominator.bit_length())
    while F(2**k)<x:k+=1
    while k>0 and F(2**(k-1))>=x:k-=1
    return k

def radius(V:F,sigma:F,delta:F)->F:
    if V<1 or sigma<=0 or not 0<delta<1:raise ValueError('Invalid confidence inputs.')
    # log(2) < 7/10. Initial ridge=1 and the declared parameter bound is 1.
    c=F(7,10)*(ceil_log2(V)+2*ceil_log2(1/delta))
    return sigma*sqrt_up(c/V)+sqrt_up(1/V)

def down_grid(x:F,n:int=1000)->F:return F((x*n).__floor__(),n)
def up_grid(x:F,n:int=1000)->F:return -down_grid(-x,n)

def sufficient_statistics(path:list[int])->dict:
    if not isinstance(path,list) or not 2<=len(path)<=1000001:
        raise ValueError('A complete finite path of 1..1000000 transitions is required.')
    if any(type(i) is not int or not 0<=i<5 for i in path):raise ValueError('Invalid node index.')
    counts=[[0]*5 for _ in range(5)]
    for i,j in zip(path,path[1:]):counts[i][j]+=1
    V1=V2=F(1);q1=q2=F(0)
    for i,s in enumerate(NODES):
        for j,u in enumerate(NODES):
            n=counts[i][j];x=s/3;y=s*s/5
            V1+=n*x*x;V2+=n*y*y;q1+=n*x*u;q2+=n*y*leg2(u)
    return {'transitions':len(path)-1,'counts':counts,'V_a':str(V1),'V_b':str(V2),
            'score_a':str(q1),'score_b':str(q2)}

def confidence_box(stats:dict,alpha:F=ALPHA)->dict:
    if not 0<alpha<1:raise ValueError('Invalid total failure probability.')
    result={}
    for label,sigma in [('a',F(1)),('b',F(3,4))]:
        V=rat(stats['V_'+label]);q=rat(stats['score_'+label]);h=q/V;r=radius(V,sigma,alpha/2)
        lo=max(F(-1),down_grid(h-r));hi=min(F(1),up_grid(h+r))
        if lo>hi:raise ValueError('Empty declared parameter confidence interval.')
        result[label]={'estimate':str(h),'radius_upper':str(r),'lower':str(lo),'upper':str(hi),
                       'subgaussian_scale':str(sigma),'individual_failure_probability':str(alpha/2)}
    A=max(abs(rat(result['a']['lower'])),abs(rat(result['a']['upper'])))
    B=max(abs(rat(result['b']['lower'])),abs(rat(result['b']['upper'])))
    result['density_floor']=str(1-A-B)
    result['whole_box_certified']=1-A-B>=0
    return result

def path_hash(path:list[int])->str:
    return hashlib.sha256(json.dumps(path,separators=(',',':')).encode()).hexdigest()

def make_certificate(path:list[int])->dict:
    stats=sufficient_statistics(path);box=confidence_box(stats)
    aa=rat(box['a']['estimate']);bb=rat(box['b']['estimate'])
    # Named center is rounded; its actual distance to both endpoints is retained.
    center={'a':str(F(round(aa*1000),1000)),'b':str(F(round(bb*1000),1000))}
    da=max(abs(rat(center['a'])-rat(box['a'][x])) for x in ('lower','upper'))
    db=max(abs(rat(center['b'])-rat(box['b'][x])) for x in ('lower','upper'))
    delta=(F(23,45)*da+F(14,45)*db)/2
    rho=rat(box['density_floor'])
    law={'center':center,'parameter_error_a':str(da),'parameter_error_b':str(db),
         'one_step_TV_upper':str(delta),
         'marginal_TV_uniform_upper':str(min(F(1),delta/rho)) if rho>0 else None,
         'full_record_bound':'min(1, horizon * one_step_TV_upper)',
         'same_last_observation_initialization':True}
    return {'schema':SCHEMA,'model':MODEL,'reference_measure':MEASURE,'data_hash':path_hash(path),
            'parameter_bounds':{'a':['-1','1'],'b':['-1','1']},
            'statistics':stats,'confidence':box,'law':law,
            'coverage':{'type':'conditional_time_uniform_theorem','total_failure_probability':str(ALPHA),
                        'assumptions_independently_verified':False,
                        'empirical_coverage_estimated':False,
                        'requires_correct_declared_conditional_moments':True,
                        'requires_predictable_unmodified_observation_features':True}}

def replay_certificate(doc:dict,path:list[int])->dict:
    expected=make_certificate(path)
    if doc!=expected:raise ValueError('Certificate differs from exact recomputation of the path and protocol.')
    c=doc['confidence'];rho=rat(c['density_floor'])
    if not c['whole_box_certified']:raise ValueError('The whole confidence box is not certified by the density-floor test.')
    ca=rat(doc['law']['center']['a']);cb=rat(doc['law']['center']['b'])
    if not rat(c['a']['lower'])<=ca<=rat(c['a']['upper']) or not rat(c['b']['lower'])<=cb<=rat(c['b']['upper']):
        raise ValueError('The released center is outside its confidence intervals.')
    return {'passed':True,'transitions':len(path)-1,'density_floor':str(rho),
            'interval_a':[c['a']['lower'],c['a']['upper']],
            'interval_b':[c['b']['lower'],c['b']['upper']],
            'one_step_TV_upper':doc['law']['one_step_TV_upper'],
            'marginal_TV_uniform_upper':doc['law']['marginal_TV_uniform_upper'],
            'conditional_confidence_level':'19/20','structural_certificate':'entire rectangle, entire curved domain',
            'data_are_external_measurements':False,'coverage_assumptions_verified_by_replay':False}

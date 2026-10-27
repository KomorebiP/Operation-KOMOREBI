"""Exact generic inverse from coupled Taylor coefficients through degree seven."""
from fractions import Fraction as F
from math import isqrt

def rational_sqrt(value):
    value=F(value)
    if value<0:
        return None
    n,d=isqrt(value.numerator),isqrt(value.denominator)
    return F(n,d) if n*n==value.numerator and d*d==value.denominator else None

def roots_from_sum_product(total,product):
    disc=total*total-4*product
    square=rational_sqrt(disc)
    if square is None:
        raise ValueError('quadratic candidates are not rational or are not real')
    return sorted(set(((total-square)/2,(total+square)/2)))

def recover_squared_scales(u1,v1,u2,v2,u3,v3):
    """Recover q²,r²,a²,b² from six exact rational ordinary Taylor coefficients.

    The domain is the nonreduction regime D!=0. The squared scales returned
    are rational. The function raises when the data do not have unique
    admissible rational squared-scale candidates. It is an exact-data API.
    """
    u1,v1,u2,v2,u3,v3=map(F,(u1,v1,u2,v2,u3,v3))
    p,k=3*u1,3*v1
    if min(p,k,u2,v2,u3,v3)<=0:
        raise ValueError('positive coupled Taylor coefficients are required')
    D=k*k*u2-p*p*v2
    if D==0:
        raise ValueError('D=0 lies on the scalar reduction surfaces')
    q_candidates=roots_from_sum_product(15*u2/(p*p),k*p)
    a_candidates=roots_from_sum_product(15*v2/(p*k),k**3/p)
    q_selected=[]
    for x in q_candidates:
        if x>0 and 0<x<1 and 0<p*p/x<1:
            predicted=p*(x*x*u2+p*p*u1*v1+(p*p/x)**2*v2)/7
            if predicted==u3:
                q_selected.append(x)
    a_selected=[]
    for y in a_candidates:
        if y>0 and 0<y<1 and 0<k*k/y<1:
            predicted=k*(y*y*u2+k*k*u1*v1+(k*k/y)**2*v2)/7
            if predicted==v3:
                a_selected.append(y)
    if len(q_selected)!=1 or len(a_selected)!=1:
        raise ValueError('coefficients fail unique contraction-domain recovery')
    x,y=q_selected[0],a_selected[0]
    return x,p*p/x,y,k*k/y

def recover_rational_scales(*coefficients):
    squares=recover_squared_scales(*coefficients)
    result=tuple(rational_sqrt(x) for x in squares)
    if any(x is None for x in result):
        raise ValueError('recovered scales are not rational; use squared scales')
    return result

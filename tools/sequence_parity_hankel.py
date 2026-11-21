"""Exact parity-block compression of the published Hankel transfer.

Author: Komorebi P. All arithmetic is rational; no pivot minor is divided by.
"""
from fractions import Fraction as F
from math import comb

import sequence_rational_hankel as base
from sequence_differential_hankel import derivative_monomial_moment
from test_sequence_differential_hankel import direct_determinant


def metadata(weights,operator,parity):
    a,c,M=base.parameters(weights,operator)
    if parity not in (0,1) or any(c[1::2]) or not any(a) or not any(c) or M<1:
        raise ValueError('Requires parity 0/1, a nonzero even operator, and M>=1')
    width=2*M
    return a,c,M,width,comb(2*width,width),2*width+1,tuple(range(width))


def start(weights,operator,parity):
    a,c,M,w,count,K,initial=metadata(weights,operator,parity)
    vector={initial:F(1)}
    for i in range(K):
        diagonal=[base.band_entry(2*i+parity,2*(i-w+k)+parity,a,c)
                  if i-w+k>=0 else F(0) for k in range(2*w+1)]
        vector=base._step(vector,w,diagonal)
    diagonal=tuple(base.stationary_diagonal(2*(w-k),a,c) for k in range(2*w+1))
    return vector,diagonal


def determinants(weights,operator,parity,last):
    a,c,M,w,count,K,initial=metadata(weights,operator,parity)
    vector={initial:F(1)};values=[F(1)]
    tail=tuple(base.stationary_diagonal(2*(w-k),a,c) for k in range(2*w+1))
    for i in range(last):
        diagonal=tail if i>=K else [
            base.band_entry(2*i+parity,2*(i-w+k)+parity,a,c)
            if i-w+k>=0 else F(0) for k in range(2*w+1)]
        vector=base._step(vector,w,diagonal)
        values.append(vector.get(initial,F(0)))
    return values


def certify(weights,operator,parity,max_order=70):
    a,c,M,w,count,K,initial=metadata(weights,operator,parity)
    vector,diagonal=start(a,c,parity)
    echelon={}
    for degree in range(min(max_order,count)+1):
        reduced,relation=dict(vector),{degree:F(1)}
        for pivot in sorted(echelon):
            coefficient=reduced.get(pivot,F(0))
            if coefficient:
                basis,representation=echelon[pivot]
                base._add_scaled(reduced,basis,-coefficient)
                base._add_scaled(relation,representation,-coefficient)
        if not reduced:
            return {'parity':parity,'start':K,'states':count,'order':degree,
                    'coefficients':base._integer_relation(relation,degree)}
        pivot=min(reduced);scale=reduced[pivot]
        echelon[pivot]=({key:value/scale for key,value in reduced.items()},
                        {key:value/scale for key,value in relation.items()})
        vector=base._step(vector,w,diagonal)
    raise ValueError('Explicit order cap reached without a full-state relation')


def verify(weights,operator,certificate):
    try:
        parity=certificate['parity']
        a,c,M,w,count,K,initial=metadata(weights,operator,parity)
        coefficients=tuple(F(value) for value in certificate['coefficients'])
        if (not coefficients or not coefficients[-1]
                or certificate['order']!=len(coefficients)-1
                or certificate['start']!=K or certificate['states']!=count):
            return False
    except (KeyError,TypeError,ValueError,ZeroDivisionError):
        return False
    vector,diagonal=start(a,c,parity);residual={}
    for value in coefficients:
        base._add_scaled(residual,vector,value)
        vector=base._step(vector,w,diagonal)
    return not residual


def direct_block(weights,operator,parity,n):
    if not n:return F(1)
    matrix=[[derivative_monomial_moment(2*(i+j+parity),weights,operator)
             for j in range(n)] for i in range(n)]
    return (4 if parity==0 else 1)*direct_determinant(matrix)

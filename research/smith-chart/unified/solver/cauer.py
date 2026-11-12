"""Exact positive Cauer-I RC synthesis and its RL frequency inverse.

Author: Komorebi P. Classical constructions; no novelty claim.
The complete class is rational Stieltjes impedances and their frequency inverse.
"""
from __future__ import annotations
from fractions import Fraction as F
import json
from pathlib import Path
import sys
from first_order import normalize,rational_text
from composition_certificate import (element_node,series_node,parallel_node,
    frequency_invert_node,make_composition,verify_composition_certificate,_target)

MAX_DEGREE=15  # Existing expression-depth cap, including the RL wrapper.


class OutsideCauer(ValueError):pass


def trim(p):
    p=list(p)
    while len(p)>1 and p[-1]==0:p.pop()
    return p


def minus(p,q):
    return trim([(p[i] if i<len(p) else F(0))-(q[i] if i<len(q) else F(0))
                 for i in range(max(len(p),len(q)))])


def core(P,Q,steps):
    degree=max(len(P),len(Q))-1
    if degree==0:
        R=P[0]/Q[0]
        if R<=0:raise OutsideCauer('Nonpositive terminal resistance')
        return element_node('R',R)
    if len(P)>len(Q):raise OutsideCauer('RC impedance grows at infinity')
    R=P[-1]/Q[-1] if len(P)==len(Q) else F(0)
    if R<0:raise OutsideCauer('Negative extracted resistance')
    U=minus(P,[R*q for q in Q])
    if not any(U) or len(Q)!=len(U)+1 or U[-1]<=0:
        raise OutsideCauer('No positive first-order capacitive extraction')
    C=Q[-1]/U[-1]
    V=minus(Q,[F(0)]+[C*u for u in U])
    if C<=0:raise OutsideCauer('Nonpositive extracted capacitance')
    steps.append({'R':str(R),'C':str(C),'degree':degree})
    capacitor=element_node('C',C)
    if not any(V):
        arm=capacitor
    else:
        next_P,next_Q=_target({'P':rational_text(U),'Q':rational_text(V)})
        if max(len(next_P),len(next_Q))-1>=degree:
            raise RuntimeError('Cauer extraction failed its strict degree decrease')
        arm=parallel_node(capacitor,core(next_P,next_Q,steps))
    return series_node(element_node('R',R),arm) if R else arm


def synthesize(target,kind='RC'):
    if kind not in ('RC','RL'):
        return {'status':'INVALID_INPUT','reason':'Choose RC or RL'}
    try:P,Q=normalize(target)
    except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc:
        return {'status':'UNKNOWN' if 'limit' in str(exc).lower() else 'INVALID_INPUT','reason':str(exc)}
    degree=max(len(P),len(Q))-1
    if not any(P):return {'status':'IDEAL_SHORT_BOUNDARY','reactive_elements':0,'resistors':0}
    if degree>MAX_DEGREE:
        return {'status':'UNKNOWN','reason':'Cauer degree exceeds the existing consumer expression scope','maximum_degree':MAX_DEGREE}
    original={'P':rational_text(P),'Q':rational_text(Q)}
    if kind=='RL':
        power=max(len(P),len(Q))
        P=list(reversed(P+[F(0)]*(power-len(P))))
        Q=list(reversed(Q+[F(0)]*(power-len(Q))))
        P,Q=_target({'P':rational_text(P),'Q':rational_text(Q)})
    steps=[]
    try:
        expression=core(P,Q,steps)
        if kind=='RL':expression=frequency_invert_node(expression)
        cert=make_composition(expression,target=original,budget=degree)
        check=verify_composition_certificate(cert,expected_target=original,expected_budget=degree)
    except OutsideCauer as exc:
        return {'status':'OUTSIDE_CERTIFIED_CLASS','reason':str(exc),
            'not_an_impossibility_result_for_mixed_RLC':True}
    except (ValueError,ZeroDivisionError) as exc:
        return {'status':'UNKNOWN','reason':'Consumer/arithmetic limit: '+str(exc)}
    if check['actual_storage']!=degree:
        raise RuntimeError('Cauer output did not attain the degree lower bound')
    return {'status':'CERTIFIED','class':kind,'reduced_degree':degree,'certificate':cert,
        'verification':check,'extractions':steps,'reactive_minimum':degree,
        'scope':'Rational Stieltjes impedance (RC), or its frequency inverse (RL), within declared caps; no general minimum resistor claim'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target',type=Path)
    parser.add_argument('--kind',choices=('RC','RL'),default='RC')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=synthesize(json.loads(args.target.read_bytes()),args.kind)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    else:print(text)

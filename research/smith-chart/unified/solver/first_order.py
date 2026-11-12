"""Complete exact synthesis of reduced real-rational positive-real degree <= 1.

Author: Komorebi P. Classical first-order series/parallel constructions.
No novelty claim. All ordinary outputs use the unchanged composition consumer.
The zero function is identified explicitly as an ideal-short boundary case.
"""
from __future__ import annotations
from fractions import Fraction as F
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'kernel'))
from composition_certificate import (_preflight,_polynomial,_target,element_node,series_node,
    parallel_node,make_composition,verify_composition_certificate)


def rational_text(values):
    return list(map(str,values))


def _element(kind,value):
    return element_node(kind,value)


def _series_resistor(value,arm):
    return series_node(_element('R',value),arm) if value else arm


def normalize(target):
    _preflight(target)
    if not isinstance(target,dict) or 'P' not in target or 'Q' not in target:
        raise ValueError('Target must contain ascending P and Q arrays')
    raw_P,raw_Q=_polynomial(target['P'],'P',64),_polynomial(target['Q'],'Q',64)
    if not any(raw_Q):
        raise ValueError('A nonzero denominator is required')
    return _target(target) if any(raw_P) else ([F(0)],[F(1)])


def synthesize(target):
    try:
        P,Q=normalize(target)
    except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc:
        return {'status':'UNKNOWN' if 'limit' in str(exc).lower() else 'INVALID_INPUT','reason':str(exc)}
    degree=max(len(P),len(Q))-1
    if degree>1:
        return {'status':'UNKNOWN','reason':'Outside the complete first-order target class','not_an_impossibility_result':True}
    a=P[1] if len(P)>1 else F(0)
    b=P[0]
    c=Q[1] if len(Q)>1 else F(0)
    d=Q[0]
    if d<0 or a<0 or b<0:
        return {'status':'NOT_POSITIVE_REAL','reason':
            'Reduced monic first-order denominator has a right-half-plane pole' if d<0 else
            'A numerator endpoint coefficient is negative',
            'normalized_target':{'P':rational_text(P),'Q':rational_text(Q)},
            'scope':'Exact first-order classification; no higher-degree decision'}
    normalized={'P':rational_text(P),'Q':rational_text(Q)}
    if degree==0 and b==0:
        return {'status':'IDEAL_SHORT_BOUNDARY','target':normalized,
            'reactive_elements':0,'resistors':0,
            'scope':'Identified terminals, not a certificate containing a zero-valued physical element'}
    values={}
    if degree==0:
        expression=_element('R',b/d);case='positive_constant';minimum_R=1
        values={'R':str(b/d)}
    elif c==0:
        L,R=a/d,b/d
        expression=_series_resistor(R,_element('L',L))
        case='series_RL' if R else 'pure_L';minimum_R=int(R>0)
        values={'L':str(L),'R0':str(R)}
    elif d==0:
        C,R=c/b,a/c
        expression=_series_resistor(R,_element('C',C))
        case='series_RC' if R else 'pure_C';minimum_R=int(R>0)
        values={'C':str(C),'R0':str(R)}
    else:
        low,high=b/d,a/c
        determinant=a*d-b*c
        if determinant>0:
            R0,R1=low,high-low
            L=determinant/(d*d)
            arm=parallel_node(_element('R',R1),_element('L',L))
            expression=_series_resistor(R0,arm)
            case='rising_RL';values={'R0':str(R0),'R1':str(R1),'L':str(L)}
        elif determinant<0:
            R0,R1=high,low-high
            C=c*c/(-determinant)
            arm=parallel_node(_element('R',R1),_element('C',C))
            expression=_series_resistor(R0,arm)
            case='falling_RC';values={'R0':str(R0),'R1':str(R1),'C':str(C)}
        else:
            raise RuntimeError('A reduced degree-one target cannot have zero determinant')
        minimum_R=2 if a>0 and b>0 else 1
    try:
        cert=make_composition(expression,target=normalized,budget=degree)
        check=verify_composition_certificate(cert,expected_target=normalized,expected_budget=degree)
    except (ValueError,ZeroDivisionError) as exc:
        return {'status':'UNKNOWN','reason':'Consumer acceptance limit: '+str(exc)}
    if check['actual_storage']!=degree or check['resistors']!=minimum_R:
        raise RuntimeError('Constructed graph disagrees with the proved low-order budgets')
    return {'status':'CERTIFIED','case':case,'normalized_target':normalized,
        'component_values':values,'certificate':cert,'verification':check,
        'reactive_minimum':degree,'resistor_minimum':minimum_R,
        'resistor_minimum_basis':'Written one-resistor endpoint obstruction; not an additional theorem checked by the composition consumer',
        'scope':'Complete reduced real-rational positive-real class of degree at most one, within stated arithmetic/consumer caps; no arbitrary-degree or hardware measurement claim'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=synthesize(json.loads(args.target.read_bytes()))
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    else:print(text)

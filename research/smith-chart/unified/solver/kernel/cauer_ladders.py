"""Author: Komorebi P. Exact Cauer I RC/RL ladder inversion.

Classical continued-fraction network synthesis, not a novelty claim.
Uses only Fraction arithmetic for proposals; a separate exact nodal checker
establishes final physical positivity, minimal reactive count and rational identity.
"""
from fractions import Fraction as F
from real_algebraic import (trim,iszero,add,sub,mul,scale,divmod_poly,gcd)
from exact_biquadratic_templates import Leaf,Comp,R,C,series,parallel,frequency_inverse,dual,circuit_certificate
from algebraic_witness import verify_algebraic_circuit


def degree(p):return len(trim(p))-1

def cauer_rc_tree(P,Q,max_depth=64):
    P=trim(P);Q=trim(Q)
    if iszero(Q) or iszero(P):raise ValueError('Nonzero target required')
    if len(gcd(P,Q))!=1:raise ValueError('Target rational pair must be reduced')
    if max_depth<0:raise ValueError('Cauer recursion limit')
    n=max(degree(P),degree(Q))
    if degree(P)>degree(Q):raise ValueError('Improper target not in RC Cauer chart')
    if n==0:
        r=P[0]/Q[0]
        if r<=0:raise ValueError('RC ladder terminates at a nonpositive resistor')
        return R(r),[]
    r=P[-1]/Q[-1] if degree(P)==degree(Q) else F(0)
    if r<0:raise ValueError('Negative resistor')
    v=sub(P,scale(Q,r))
    if iszero(v):
        raise ValueError('No dynamic degree after resistor: nonreduced target')
    if degree(Q)-degree(v)!=1:
        raise ValueError('No linear high-frequency capacitor extraction')
    c=Q[-1]/v[-1]
    if c<=0:raise ValueError('Negative extracted capacitance')
    d=sub(Q,mul([F(0),c],v))
    if iszero(d):
        tail=C(c);more=[]
    else:
        if degree(d)>=degree(Q):raise ValueError('No degree reduction')
        tail,more=cauer_rc_tree(v,d,max_depth-1)
        tail=parallel(C(c),tail)
    result=series(R(r),tail) if r else tail
    return result,[{'series_resistance':str(r),'shunt_capacitance':str(c),'degree':n}]+more


def find_cauer(P,Q):
    P=trim(P);Q=trim(Q)
    n=max(degree(P),degree(Q))
    if len(gcd(P,Q))!=1:
        raise ValueError('Reduce the rational input before synthesis')
    for reciprocal in (False,True):
        a,b=(Q,P) if reciprocal else (P,Q)
        for kind in ('RC','RL'):
            pp,qq=(a,b) if kind=='RC' else (list(reversed(a)),list(reversed(b)))
            try:
                t,steps=cauer_rc_tree(pp,qq)
                if kind=='RL':t=frequency_inverse(t)
                if reciprocal:t=dual(t)
                cert=circuit_certificate(P,Q,t)
                check=verify_algebraic_circuit(cert,{'P':P,'Q':Q},n)
                if check['actual_storage']!=n or check['reduced_target_degree']!=n:continue
                return {'status':'CERTIFIED_MINIMUM','route':f'exact Cauer {kind} extraction' + (' (admittance dual)' if reciprocal else ''),
                        'minimum_reactive_count':n,'certificate':cert,'verification':check,'stages':steps}
            except (ValueError,ZeroDivisionError):continue
    return {'status':'UNKNOWN','reason':'Target outside verified RC/RL Cauer charts; no impossibility conclusion'}

if __name__=='__main__':
    import json,sys
    from pathlib import Path
    d=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(find_cauer(d['P'],d['Q']),indent=2))

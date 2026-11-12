"""Author: Komorebi P. Exact endpoint extraction before RC Cauer synthesis.

Recognizes Z=1/(g+1/(s L+Z_RC)) and scalar dual/frequency-inversion
orientations. This is a classical circuit-theoretic inverse construction,
not a complete minimum-order synthesis theorem and not claimed novel.

Unlike pole-factor routes, this recognizes some MIXED q=n networks with
irreducible denominators of arbitrarily large rational degree.
"""
from fractions import Fraction as F
from real_algebraic import trim,sub,scale,mul,gcd,iszero
from exact_biquadratic_templates import R,L,series,parallel,dual,frequency_inverse,circuit_certificate
from cauer_ladders import cauer_rc_tree
from algebraic_witness import verify_algebraic_circuit

def degree(p):return len(trim(p))-1

def extract_shunt_L(P,Q):
    P=trim(P);Q=trim(Q)
    if degree(P)!=degree(Q) or degree(P)<2 or degree(gcd(P,Q))!=0:
        raise ValueError('Requires reduced equal positive degree numerator/denominator')
    g=Q[-1]/P[-1]
    if g<=0:raise ValueError('Shunt conductance nonpositive')
    T=sub(Q,scale(P,g))
    if iszero(T) or degree(P)-degree(T)!=1:
        raise ValueError('No positive series inductance can be extracted from this endpoint')
    l=P[-1]/T[-1]
    if l<=0:raise ValueError('Negative extracted inductor')
    Pc=sub(P,mul([F(0),l],T))
    if iszero(Pc):raise ValueError('No positive lower-degree RC core')
    if max(degree(Pc),degree(T))!=degree(P)-1:
        raise ValueError('No single-step rational degree reduction')
    return g,l,Pc,T


def extract_series_R_C(P,Q):
    """Detect Z=R + 1/(s*C+1/Z_core) from high-frequency coefficients."""
    P=trim(P);Q=trim(Q)
    if degree(P)!=degree(Q) or degree(P)<2 or degree(gcd(P,Q))!=0:
        raise ValueError('Requires reduced equal-degree positive target')
    r=P[-1]/Q[-1]
    if r<=0:raise ValueError('Series resistance nonpositive')
    T=sub(P,scale(Q,r))
    if iszero(T) or degree(Q)-degree(T)!=1:
        raise ValueError('No linear shunt capacitance at infinity')
    c=Q[-1]/T[-1]
    if c<=0:raise ValueError('Shunt capacitance nonpositive')
    D=sub(Q,mul([F(0),c],T))
    if iszero(D) or max(degree(T),degree(D))!=degree(P)-1:
        raise ValueError('No reduced positive-order core')
    return r,c,T,D

def find_endpoint_cauer(P,Q):
    P,Q=trim(P),trim(Q);n=max(degree(P),degree(Q))
    if degree(gcd(P,Q))>0:raise ValueError('Provide a reduced rational target')
    for reciprocal in (False,True):
        a,b=(Q,P) if reciprocal else (P,Q)
        for invert_frequency in (False,True):
            pp,qq=(list(reversed(a)),list(reversed(b))) if invert_frequency else (a,b)
            try:
                g,l,cp,cq=extract_shunt_L(pp,qq)
                tcore,steps=cauer_rc_tree(cp,cq)
                t=parallel(R(1/g),series(L(l),tcore))
                if invert_frequency:t=frequency_inverse(t)
                if reciprocal:t=dual(t)
                cert=circuit_certificate(P,Q,t)
                check=verify_algebraic_circuit(cert,{'P':P,'Q':Q},n)
                if check['actual_storage']!=n or check['reduced_target_degree']!=n:continue
                return {'status':'CERTIFIED_MINIMUM',
                   'route':'exact endpoint shunt/series extraction + RC Cauer ladder',
                   'orientation':{'admittance_dual':reciprocal,'frequency_inverted':invert_frequency},
                   'minimum_reactive_count':n,'certificate':cert,'verification':check,
                   'extraction':{'conductance_g':str(g),'series_inductance_L':str(l),
                                 'core_P':list(map(str,cp)),'core_Q':list(map(str,cq))},
                   'cauer_stages':steps}
            except (ValueError,ZeroDivisionError):continue
    return {'status':'UNKNOWN','reason':'No positive endpoint extraction in four supported orientations; not a global impossibility'}

if __name__=='__main__':
    import json,sys
    from pathlib import Path
    d=json.loads(Path(sys.argv[1]).read_text());print(json.dumps(find_endpoint_cauer(d['P'],d['Q']),indent=2))

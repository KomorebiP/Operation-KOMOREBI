"""Author: Komorebi P. Exact-checking sparse four-node q=3 bridge charts.

A numerical optimizer only proposes positive conductances/inductances/caps.
Fractions are then reconstructed and the independent exact KCL checker MUST
certify the returned graph and full target. Unverified candidates and solver
failures are UNKNOWN, never UNSAT.

The two fixed seven-component shapes are full-rank mixed RLC four-node
networks. The charts were chosen after inspecting 2 failed cases in a 60-case
training corpus; that corpus MUST NOT be presented as a holdout success rate.
"""
from __future__ import annotations
from functools import lru_cache
from fractions import Fraction as F
from algebraic_witness import verify_algebraic_circuit
from real_algebraic import trim,gcd

# Branch tuples: type R/L/C, positive unordered vertex pair. Port1, ground0.
TEMPLATES={
 'bridgeA_2L1C_4R':(
    ('L',1,2),('L',1,3),('C',0,3),('R',2,3),('R',0,2),('R',1,3),('R',0,1)),
 'bridgeB_1L2C_4R':(
    ('L',0,3),('C',1,2),('C',2,3),('R',0,3),('R',0,2),('R',1,2),('R',1,3)),
}

@lru_cache(None)
def model(name):
    import sympy as S
    import numpy as np
    if name not in TEMPLATES:raise ValueError('Unknown restricted topology')
    x=S.Symbol('s');spec=TEMPLATES[name]
    v=S.symbols('v0:'+str(len(spec)));M=S.zeros(3)
    nl=sum(t=='L' for t,*_ in spec)
    for z,(typ,a,b) in zip(v,spec):
        y=z if typ=='R' else z*x if typ=='C' else z/x
        if a:M[a-1,a-1]+=y
        if b:M[b-1,b-1]+=y
        if a and b:M[a-1,b-1]-=y;M[b-1,a-1]-=y
    N=S.Poly(S.cancel(x**nl*M.minor_submatrix(0,0).det()),x)
    D=S.Poly(S.cancel(x**nl*M.det()),x)
    assert N.degree()==3 and D.degree()==3
    out=S.Matrix([N.nth(j)/N.nth(3) for j in range(3)]+[D.nth(j)/N.nth(3) for j in range(4)])
    return S.lambdify([v],out,'numpy'),S.lambdify([v],out.jacobian(v),'numpy')


def cert_from_parameters(name,values,P,Q):
    b=[]
    for (typ,a,c),v in zip(TEMPLATES[name],values):
        z={'R':'g','L':'h','C':'c'}[typ]
        b.append({'type':z,'nodes':[a,c],'coefficient':[str(F(v))]})
    return {'format':'komorebi-algebraic-circuit-v1',
            'target':{'P':list(map(str,P)),'Q':list(map(str,Q))},
            'storage_budget':3,'field':{'polynomial':['0','1'],'interval':['-1','1']},
            'branches':b}


def find_sparse_q3(P,Q,max_starts=5,max_nfev=300):
    import math
    import numpy as np
    from scipy.optimize import least_squares
    P=trim(P);Q=trim(Q)
    if len(P)!=4 or len(Q)!=4 or len(gcd(P,Q))>1 or not P[3]:
        return {'status':'UNKNOWN','reason':'Sparse bridge q3 chart requires reduced (3,3) target'}
    target=np.array([float(a/P[3]) for a in P[:3]]+[float(a/P[3]) for a in Q])
    scales=np.maximum(1,abs(target))
    starts=np.random.default_rng(1204)
    attempts=0
    for name in TEMPLATES:
        ff,jj=model(name)
        def calc(z):
            vals=np.exp(np.clip(z,-18,18))
            return np.ravel(ff(vals))/scales-target/scales
        def jac(z):
            vals=np.exp(np.clip(z,-18,18))
            return np.asarray(jj(vals),dtype=float)*vals[None,:]/scales[:,None]
        for i in range(max_starts):
            z0=np.zeros(len(TEMPLATES[name])) if i==0 else starts.normal(0,1.2,len(TEMPLATES[name]))
            attempts+=1
            try:
                res=least_squares(calc,z0,jac=jac,max_nfev=max_nfev,
                    ftol=1e-12,xtol=1e-12,gtol=1e-12)
            except (ValueError,OverflowError,FloatingPointError,ZeroDivisionError):continue
            vals=np.exp(np.clip(res.x,-18,18))
            if not np.all(np.isfinite(vals)) or not np.all(np.isfinite(calc(res.x))):continue
            if max(abs(calc(res.x)))>1e-9:continue
            # Numerical fitting is an UNTRUSTED proposal: no result is accepted
            # until an exact Fraction circuit is independently verified.
            for maxden in (8,16,32,100,1000,10000,100000):
                rational=[F(float(z)).limit_denominator(maxden) for z in vals]
                if min(rational)<=0:continue
                c=cert_from_parameters(name,rational,P,Q)
                try:check=verify_algebraic_circuit(c,{'P':P,'Q':Q},3)
                except (ValueError,ZeroDivisionError):continue
                if check['actual_storage']!=3 or check['reduced_target_degree']!=3:continue
                return {'status':'CERTIFIED_MINIMUM','route':'numerical topology proposal + independent exact rational graph certificate',
                    'minimum_reactive_count':3,'template':name,'starts_attempted':attempts,
                    'max_reconstruction_denominator':maxden,'certificate':c,'verification':check}
    return {'status':'UNKNOWN','reason':'No exact positive rational witness in two sparse bridge template charts; numerical misses are not impossibility proofs',
            'starts_attempted':attempts}

if __name__=='__main__':
    import json,sys
    from pathlib import Path
    data=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(find_sparse_q3(data['P'],data['Q']),indent=2))

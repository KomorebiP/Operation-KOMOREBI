"""Explicit quartic matching identities for the inherited Gaussian tower.
Original software: MIT. No physical model is selected by these identities.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import mpmath as mp
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
BENCH=json.loads((ROOT/'inputs/frozen_benchmark.json').read_text())
ETA=float(BENCH['calibrated_benchmark']['capture_normalization'])
A0=float(BENCH['calibrated_benchmark']['A_over_mu'])
S=float(BENCH['parameters']['gamma'])
D=1/(4*ETA*A0**4)
SE=2.18498795564
X=1e-4

def tower(depth:int):
    if not isinstance(depth,int) or not 1<=depth<=22:
        raise ValueError('depth must be an integer in [1,22]')
    h=np.arange(1,depth+1)
    return X*2.**h,2.**(h-1)

def Bcoef(depth:int)->float:
    y,d=tower(depth)
    return float(np.dot(d,y**4)/(64*np.pi**2))

def F(s):
    s=np.asarray(s,dtype=float)
    if np.any(s<0):raise ValueError('s must be nonnegative')
    p=np.zeros_like(s)
    for n in range(18,2,-1):p=p*s+2*(-1.)**(n-1)/(n*(n-1)*(n-2))
    return np.where(s<.05,p*s**3,(1+s)**2*np.log1p(s)-s-1.5*s*s)

def R(s,ref=S):
    """Third-order Taylor remainder of G at ref; stable on whole s>=0."""
    s=np.asarray(s,dtype=float)
    t=(s-ref)/(1+ref)
    # For negative t not too close to zero, exact identity is stable.
    p=np.zeros_like(t)
    for n in range(24,2,-1):p=p*t+2*(-1.)**(n-1)/(n*(n-1)*(n-2))
    ff=np.where(np.abs(t)<.05,p*t**3,(1+t)**2*np.log1p(t)-t-1.5*t*t)
    return (1+ref)**2*ff

def V_origin(q,depth):
    q=np.asarray(q,dtype=float)
    return D*(1-q*q/S)**2+Bcoef(depth)*F(q*q)

def dV_origin(q,depth):
    q=np.asarray(q,dtype=float);s=q*q
    p=np.zeros_like(s)
    for n in range(18,1,-1):p=p*s+(-1.)**n/(n*(n-1))
    term=np.where(s<.05,p*s*s,(1+s)*np.log1p(s)-s)
    return -4*D*q/S*(1-s/S)+4*Bcoef(depth)*q*term

def J(s):return s*s/2-s+np.log1p(s)
def K(s):return s*s/2+s-(1+s)*np.log1p(s)

def V_vacuum(q,depth,curvature):
    s=np.asarray(q,dtype=float)**2
    return curvature/(8*S)*(s-S)**2+Bcoef(depth)*R(s)

def derivative_obstruction_audit():
    """Return calculations, symbolic identities, and independent integral checks."""
    import sympy as sp
    s,t,B,a,b,c,ref,curv=sp.symbols('s t B a b c ref curv',positive=True)
    G=(1+s)**2*sp.log(1+s)
    U=a+b*s+c*s*s+B*G
    # Elementary derivatives in s are translated to background derivatives in q.
    # Stationarity at ref fixes b. Verify invariant for arbitrary a,c,B.
    br=sp.solve(sp.diff(U,s).subs(s,ref),b)[0]
    Ur=U.subs(b,br)
    Delta=sp.simplify(Ur.subs(s,0)-Ur.subs(s,ref))
    kappa=sp.simplify(4*ref*sp.diff(Ur,s,2).subs(s,ref))
    kappa0=sp.simplify(2*sp.diff(Ur,s).subs(s,0))
    JJ=ref**2/2-ref+sp.log(1+ref)
    KK=ref**2/2+ref-(1+ref)*sp.log(1+ref)
    identities={
      'barrier_curvature':str(sp.simplify(Delta-ref*kappa/8+B*JJ)),
      'origin_curvature':str(sp.simplify(kappa0-4*(B*KK-Delta)/ref)),
      'J_integral':str(sp.simplify(sp.integrate(t*t/(1+t),(t,0,ref))-JJ)),
      'K_derivative':str(sp.simplify(sp.diff(KK,ref)-(ref-sp.log(1+ref))))
    }
    epsilon=.01; E0=SE/epsilon; C=2*E0;kold=8*D/S
    rows=[]
    for H in [1,13,14,15,16,17,18]:
      Bv=Bcoef(H); JJv=float(J(S)); KKv=float(K(S))
      rows.append(dict(depth=H,B=Bv,tree_barrier=D,tree_curvature=kold,
          curvature_matched_origin_energy=D-Bv*JJv,
          curvature_matched_origin_over_budget=(D-Bv*JJv)/E0,
          barrier_matched_curvature=8*(D+Bv*JJv)/S,
          barrier_matched_curvature_ratio=1+Bv*JJv/D,
          barrier_matched_origin_curvature=4*(Bv*KKv-D)/S,
          origin_maximum_required_barrier=Bv*KKv,
          origin_maximum_barrier_over_budget=Bv*KKv/E0,
          origin_maximum_barrier_over_tree=Bv*KKv/D,
          threshold_wavefunction_normalized_mass=np.sqrt(8*Bv*(S-np.log1p(S))/C),
          sextic_delta_coefficient=-Bv*JJv/S**3))
    # Curvature-matched shifted remainder and independently integrated remainder.
    integral=[]
    for ss in [0.,.01,1.,4.,15.,15.9,16.,16.1,20.,64.]:
      val=quad(lambda tt:(ss-tt)**2/(1+tt),S,ss,epsabs=1e-12,epsrel=2e-13)[0]
      obs=float(R(ss)); integral.append(dict(s=ss,analytic=obs,quadrature=val,error=abs(obs-val)))
    # Numerical polynomial invariance for randomly chosen coefficients.
    rng=np.random.default_rng(714);
    inv_errors=[]
    for _ in range(200):
      Bv=10**rng.uniform(-4,4);sv=10**rng.uniform(-2,2);av=rng.normal();cv=rng.normal()
      gv=lambda x:(1+x)**2*np.log1p(x)
      g1=lambda x:2*(1+x)*np.log1p(x)+1+x
      g2=lambda x:2*np.log1p(x)+3
      bv=-2*cv*sv-Bv*g1(sv)
      uv=lambda x:av+bv*x+cv*x*x+Bv*gv(x)
      delt=uv(0)-uv(sv);kap=4*sv*(2*cv+Bv*g2(sv));k0=2*(bv+Bv)
      scale=max(1,abs(delt),abs(sv*kap/8),abs(Bv*J(sv)))
      inv_errors.append(abs(delt-sv*kap/8+Bv*J(sv))/scale)
    result=dict(scope='Quartic-counterterm Gaussian tower. Written derivation and symbolic checks; not a universal no-go.',
       inputs=dict(S=S,D=D,epsilon=epsilon,C=C,E0=E0),symbolic=identities,table=rows,
       independent_remainder_integrals=integral,max_scaled_matching_residual=max(inv_errors),
       physical_gates=dict(retain_old_vacuum_curvature_and_barrier=False,
                           retain_old_small_barrier_and_origin_maximum=False,
                           physical_alternative_selected=False))
    (ROOT/'results/matching_audit.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    r=derivative_obstruction_audit();print(json.dumps(r,indent=2))

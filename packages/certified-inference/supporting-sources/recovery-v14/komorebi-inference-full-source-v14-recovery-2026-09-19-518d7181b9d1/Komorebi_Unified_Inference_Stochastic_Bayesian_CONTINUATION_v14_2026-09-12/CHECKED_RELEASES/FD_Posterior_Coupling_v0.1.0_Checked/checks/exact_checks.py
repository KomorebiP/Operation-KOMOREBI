#!/usr/bin/env python3
"""Deterministic exact-rational diagnostics, not a universal proof or performance benchmark.

Checks covariance, coupling cost, and stopping-budget identities in 24 constructed
matrix cases. A separate finite Rademacher enumeration independently checks a
quadratic moment; it is not a Gaussian law verification. The Lean files supply
all universal probability claims.
"""
from __future__ import annotations
import argparse, itertools, json, time
from pathlib import Path
import sympy as sp

def ratmat(n: int, m: int, key: int) -> sp.Matrix:
    return sp.Matrix(n, m, lambda i,j: sp.Rational(((i+1)*(j+3)+key*(i+j+1))%7-3, 1+(key+j)%3))

def sqnorm(x: sp.Matrix) -> sp.Expr:
    return (x.T*x).trace()

def frob(x: sp.Matrix) -> sp.Expr:
    return sum(a*a for a in x)

def zero(A: sp.Matrix) -> bool:
    return all(sp.cancel(x)==0 for x in A)

def run() -> dict:
    t=time.monotonic(); rows=[]
    for k in range(24):
        n=1+k%3; d=1+(k//3)%3
        # Rank-one, deterministic, and full-rank priors all appear.
        L=ratmat(n, 1 if k%3==0 else n, k+1)
        if k%6==1: L=sp.zeros(n,n)
        if k%6==2: L=L.row_join(sp.eye(n))
        P=L*L.T; H=ratmat(d,n,k+2)
        sigroot=[sp.Rational(1,2),sp.Integer(1),sp.Integer(2)][k%3]
        sigma=sigroot**2; Q=ratmat(d,1,k+3)
        N=Q.row_join(sigroot*sp.eye(d)); R=N*N.T
        S=H*P*H.T+R; Si=S.inv(); K=P*H.T*Si
        m=ratmat(n,1,k+4); y=ratmat(d,1,k+5); v=y-H*m
        B=K if k%4==0 else (sp.zeros(n,d) if k%4==1 else K+ratmat(n,d,k+6)/7)
        I=sp.eye(n); G=I-K*H; Ghat=I-B*H; D=K-B
        C=P-K*H*P; J=Ghat*P*Ghat.T+B*R*B.T
        F=P*H.T-B*S; E=F*Si*F.T
        assert zero(D-F*Si)
        assert zero(J-C-E)
        assert zero(E-D*S*D.T)
        assert zero(C-G*P*G.T-K*R*K.T)
        # Independent computation from sampler coefficients, then residual identity.
        delta_a=D*v; U=(G-Ghat)*L; V=(K-B)*N
        sampler_cost=sqnorm(delta_a)+frob(U)+frob(V)
        residual_cost=sqnorm(F*Si*v)+E.trace()
        assert sp.cancel(sampler_cost-residual_cost)==0
        budget=frob(F)*(1/sigma+sqnorm(v)/sigma**2)
        assert sp.cancel(budget-residual_cost)>=0
        assert sp.cancel(budget*sigma**2-frob(F)*(sigma+sqnorm(v)))==0
        if F==sp.zeros(n,d): assert residual_cost==0
        else: assert budget>0
        # J is valid by an explicit factor, independently of the residual formula.
        Jfactor=(Ghat*L).row_join(B*N)
        assert zero(J-Jfactor*Jfactor.T)
        rows.append({'case':k,'state_dim':n,'observation_dim':d,'prior_rank':P.rank(),
                     'sigma':str(sigma),'exact_gain':B==K,'zero_gain':B==sp.zeros(n,d),
                     'cost':str(residual_cost),'majorant':str(budget),'passed':True})
    # Exact Rademacher enumeration checks the affine quadratic formula independently.
    a=sp.Matrix([sp.Rational(2,3),-1]); U=ratmat(2,2,2); V=ratmat(2,2,5)
    enumerated=sp.Rational(0)
    for signs in itertools.product([-1,1],repeat=4):
        enumerated+=sqnorm(a+U*sp.Matrix(signs[:2])+V*sp.Matrix(signs[2:]))/16
    formula=sqnorm(a)+frob(U)+frob(V)
    assert sp.cancel(enumerated-formula)==0
    # Same Gaussian covariance with opposite factors: cost can exceed exact W2=0.
    assert frob(sp.Matrix([[1]])-sp.Matrix([[-1]]))==4
    return {'status':'PASS','arithmetic':'exact rational matrix arithmetic',
            'sympy_version':sp.__version__,'constructed_matrix_cases':len(rows),
            'case_generation':'deterministic arithmetic formulas; no random seed',
            'state_dimensions':[1,2,3],'observation_dimensions':[1,2,3],
            'includes_singular_and_deterministic_priors':True,
            'identities':['residual gain recovery','Joseph excess covariance',
                          'actual sampler coefficient cost = residual formula',
                          'noise-floor Frobenius majorant','squared stopping-budget algebra',
                          'explicit factor validity of approximate covariance'],
            'finite_quadratic_moment_check':{'support_points':16,'value':str(formula),
              'nonclaim':'Rademacher enumeration verifies a quadratic moment only, not a Gaussian law'},
            'factor_gauge_boundary':{'identical_standard_gaussian_opposite_factors_cost':'4',
                                    'exact_distribution_distance':'0'},
            'cases':rows,'elapsed_seconds':round(time.monotonic()-t,4),
            'nonclaims':['No universal inference from bounded diagnostics',
                         'No numerical rounding certification','No performance benchmark',
                         'No proof that the chosen coupling is optimal']}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'EXACT_CHECKS.json')
    args=parser.parse_args(); result=run()
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','constructed_matrix_cases','elapsed_seconds')}))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""One exact rational convention check; not a substitute for the universal Lean proof."""
from pathlib import Path
import json, hashlib, sys
import sympy as sp

def main():
    I=sp.eye(2); P=sp.ones(2); P0=I; H=I; H0=I; R=I; R0=I
    S=H*P*H.T+R; S0=H0*P0*H0.T+R0
    K=P*H.T*S.inv(); K0=P0*H0.T*S0.inv()
    A=I-K*H; A0=I-K0*H0
    C=P-K*H*P; C0=P0-K0*H0*P0; D=C-C0
    terms=[(A-A0)*P*A.T, A0*(P-P0)*A.T, A0*P0*(A.T-A0.T),
           (K-K0)*R*K.T, K0*(R-R0)*K.T, K0*R0*(K.T-K0.T)]
    assert P.det()==0 and P.eigenvals()=={sp.Integer(2):1,sp.Integer(0):1}
    assert C==sp.ones(2)/3
    assert C0==I/2
    assert C==A*P*A.T+K*R*K.T
    assert D==sum(terms,sp.zeros(2))
    assert D==sp.Matrix([[-sp.Rational(1,6),sp.Rational(1,3)],
                         [sp.Rational(1,3),-sp.Rational(1,6)]])
    F=[sp.diag(1,0),sp.diag(0,1)]
    corners=[f*D*g for f in F for g in F]
    assert sum(corners,sp.zeros(2))==D and F[0]*D*F[1]!=sp.zeros(2)
    # All matrices here are real symmetric, so spectral norms are exact max abs eigenvalues.
    norm=lambda B:max(abs(x) for x in B.eigenvals())
    si,si0=norm(S.inv()),norm(S0.inv())
    bS=norm(H-H0)*norm(P)*norm(H)+norm(H0)*norm(P-P0)*norm(H)+norm(H0)*norm(P0)*norm(H-H0)+norm(R-R0)
    bK=norm(P-P0)*norm(H)*si+norm(P0)*norm(H-H0)*si+norm(P0)*norm(H0)*(si*bS*si0)
    bA=bK*norm(H)+norm(K0)*norm(H-H0)
    bC=bA*norm(P)*norm(A)+norm(A0)*norm(P-P0)*norm(A)+norm(A0)*norm(P0)*bA+bK*norm(R)*norm(K)+norm(K0)*norm(R-R0)*norm(K)+norm(K0)*norm(R0)*bK
    assert norm(D)==sp.Rational(1,2) and bC==6 and norm(D)<=bC
    out={'result':'PASS','arithmetic':'exact rational and exact symmetric spectra',
         'sympy_version':sp.__version__,'cases':1,'dimensions':[2,2],
         'seed':None,'singular_prior':True,'posterior_error':str(D),
         'nonzero_offdiagonal':str(D[0,1]),'error_operator_norm':str(norm(D)),
         'residual_budget':str(bC),'joseph_six_term_identity':True,
         'projector_reconstruction':True,'bound_is_conservative':True,
         'non_claim':'A single fixed exact diagnostic, not a universal proof or a benchmark.',
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    p=Path(__file__).resolve().parent/'EXACT_REGRESSION.json'
    p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

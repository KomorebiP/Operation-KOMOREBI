"""Noisy geometry proposal and exact robust acceptance.

The input file contains perturbed operators and an initial state, not a prior
certificate geometry or hidden generator. Fixture generation is separate.
Noise is not presented as a sampling confidence region.
"""
from pathlib import Path
import json
import sys
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import U,poly_matrices,propose_geometry,make_certificate,replay_certificate,enc,coeff_matrices



def main():
    data=json.loads((ROOT/'examples/noisy_operator_inputs.json').read_text())
    fitted={k:poly_matrices(v) for k,v in data['actions'].items()}
    initial=sp.Matrix([[sp.Rational(v) for v in row] for row in data['initial']]);delta=sp.Rational(data['metadata']['coefficient_scale'])
    T,diagnostics=propose_geometry(fitted,denominator=48)
    print('Proposed T:',T,flush=True)
    print('Metric:',diagnostics['metric'],flush=True)
    eta=sp.Rational(1,8)
    reset=sp.Matrix([1,sp.Rational(1,2),sp.Rational(1,2)])*sp.Matrix([[1,0,0]])
    # Reset to the center of the proposed domain, not to a supplied hidden state.
    reset=T.inv()*sp.diag(1,0,0)*T
    corrected={k:((1-eta)*B+eta*reset).applyfunc(sp.expand) for k,B in fitted.items()}
    certificate=make_certificate(corrected,initial,T,sp.Rational(1,16),sp.Rational(1,128),sp.Rational(1,128),max_depth=8)
    report=replay_certificate(certificate)
    (ROOT/'certificates/robust_curved_certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    results={'construction':'deterministic rational perturbation of inherited continuous operators','noise_coefficient_scale':str(delta),
             'noise_is_statistical_sample':False,'geometry_proposal':diagnostics,'reset_mixture':str(eta),
             'fitted_actions':{k:coeff_matrices(v) for k,v in fitted.items()},'corrected_actions':certificate['actions'],
             'reference':{'no_hidden_geometry_given_to_proposer':True,'certificate_covers_repaired_model_not_unrestricted_raw_confidence_set':True},
             'replay':report}
    (ROOT/'verification/noisy_geometry_example.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()

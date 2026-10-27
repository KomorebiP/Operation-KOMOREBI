"""A smaller certified repair of the unchanged 0.7.0 fitted family.

The old geometry is reused, not rediscovered. A separate reference-domain witness
is checked before comparing laws. The deterministic box is not a confidence set.
"""
from pathlib import Path
import json,sys
import sympy as sp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import *

def main():
    raw=json.loads((ROOT/'examples/noisy_operator_inputs.json').read_text())
    previous=json.loads((ROOT/'certificates/robust_curved_certificate.json').read_text())
    T=mat(previous['transform_to_lorentz']);initial=mat(raw['initial'])
    fitted={k:poly_matrices(v) for k,v in raw['actions'].items()}
    eta=sp.Rational(1,32);kappa=sp.Rational(1,64)
    N=T.inv()*sp.diag(1,0,0)*T
    corrected={k:((1-eta)*B+eta*N).applyfunc(sp.expand) for k,B in fitted.items()}
    primary=make_certificate(corrected,initial,T,kappa,sp.Rational(1,128),sp.Rational(1,128),8)
    T0=sp.Matrix([[1,0,0],[-sp.Rational(2,3),sp.Rational(10,3),-2],[-sp.Rational(4,3),0,sp.Rational(8,3)]])
    comparison=make_certificate(corrected,initial,T0,kappa,sp.Rational(1,128),sp.Rational(1,128),8)
    z=sp.Matrix([1,1,0]);ell=sp.Matrix([[1,sp.Rational(7,25),-sp.Rational(24,25)]])
    c=(ell*T*fitted['direct'].subs(U,-1)*T.inv()*z)[0]
    lower=sp.factor((kappa-c)/(1-c))
    noise=sp.Rational(241,40000);budget=(1-eta)*noise+2*eta
    out={'repair_weight':str(eta),'required_margin':str(kappa),
         'same_coefficient_box_as_070':True,'old_repair_weight':'1/8',
         'scalar_separation_value':str(c),'fixed_margin_repair_lower_bound':str(lower),
         'accepted_upper_bound':str(eta),'global_optimum_claimed':False,
         'raw_error_budget':str(noise),'repaired_instrument_error_upper':str(budget),
         'record_law_TV_slope':str(budget/2),'first_trivial_integer_horizon':int(sp.ceiling(2/budget)),
         'smaller_1_64_fails_required_margin_at_support_witness':bool((1-sp.Rational(1,64))*c+sp.Rational(1,64)<kappa),
         'primary_replay':replay_certificate(primary),'comparison_replay':replay_certificate(comparison),
         'statistical_coverage':False}
    for name,obj in [('reduced_repair_certificate',primary),('reduced_repair_comparison',comparison)]:
        (ROOT/f'certificates/{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    (ROOT/'verification/reduced_repair_result.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()

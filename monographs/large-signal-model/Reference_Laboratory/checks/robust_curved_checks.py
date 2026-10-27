"""Exact examples, certificate controls and a separately labeled numerical proposal.

These finite records are not formal verification of all quantified theorems.
Run examples/robust_noisy_example.py and robust_comparison_example.py first.
"""
from pathlib import Path
import copy,json
from fractions import Fraction
import sympy as sp
from robust_reference import *
from noisy_generator import noisy_fixture
ROOT=Path(__file__).resolve().parents[1]
records=[]

def check(name,condition,kind='exact',details=None):
    if not bool(condition):raise AssertionError(name)
    records.append({'name':name,'kind':kind,'passed':True,'details':details})

def reject(name,func):
    try:func()
    except (ValueError,ArithmeticError,TypeError,ZeroDivisionError) as exc:
        records.append({'name':name,'kind':'exact_rejection_control','passed':True,'reason':str(exc)});return
    raise AssertionError('Expected rejection: '+name)


def mutate(c,func):
    z=copy.deepcopy(c);func(z);return z


def main():
    cert=json.loads((ROOT/'certificates/robust_curved_certificate.json').read_text())
    comparison=json.loads((ROOT/'certificates/robust_comparison_certificate.json').read_text())
    report=replay_certificate(cert);report2=replay_certificate(comparison)
    check('complete_noisy_certificate_replay',report['passed'],details=report)
    check('separate_common_domain_replay',report2['passed'],details=report2)
    T=mat(cert['transform_to_lorentz']);z=mat(cert['initial'])
    check('geometry_invertible',T.det()!=0)
    check('mass_preserving_coordinates',list(T[0,:])==[1,0,0])
    check('initial_is_proposed_center',T*z==sp.Matrix([1,0,0]))
    L=T[1:,1:];H=L.T*L
    check('metric_exact_factor',H==sp.Matrix([[sp.Rational(15129,1369),-sp.Rational(246,37)],[-sp.Rational(246,37),sp.Rational(18605,1681)]]))
    check('metric_positive_leading_minor',H[0,0]>0)
    check('metric_positive_determinant',H.det()>0)
    check('new_metric_differs_from_predecessor',H!=sp.Matrix([[sp.Rational(100,9),-sp.Rational(20,3)],[-sp.Rational(20,3),sp.Rational(100,9)]]))
    r=sp.Rational(1,4096)
    check('coefficient_box_mass_envelope',9*r<=sp.Rational(1,128))
    check('coefficient_box_spatial_envelope',18*r<=sp.Rational(1,128))
    check('robust_margin_remaining',sp.Rational(1,16)-2*sp.Rational(1,128)==sp.Rational(3,64))
    # Both charts exactly cover unit-circle points.
    for sign in [-1,1]:
        v=sp.Matrix([sign*(1-V**2)/(1+V**2),sign*2*V/(1+V**2)])
        check(f'semicircle_unit_norm_{sign}',sp.factor((v.T*v)[0]-1)==0)
    # Exact tensor expansion identity, independently reconstructed.
    p=sp.Rational(1,7)+U**2+U*V/5+V**4
    b=root_bernstein(p);n=len(b)-1;m=len(b[0])-1
    x,y=sp.symbols('x y')
    rebuilt=sum(sp.Rational(v.numerator,v.denominator)*comb(n,i)*x**i*(1-x)**(n-i)*comb(m,j)*y**j*(1-y)**(m-j) for i,row in enumerate(b) for j,v in enumerate(row))
    check('tensor_bernstein_exact_identity',sp.expand(rebuilt-p.subs({U:2*x-1,V:2*y-1}))==0)
    # Lower coefficients can be negative even when the polynomial is positive.
    small=(U-sp.Rational(1,3))**2+sp.Rational(1,1000)
    check('strict_positive_polynomial_initial_bound_negative',minimum(root_bernstein(small))<0)
    proof=certify_polynomial(small,8)
    check('strict_positive_subdivision_replay',replay_polynomial(small,proof)[0]>1)
    neg=U**2-sp.Rational(1,4)
    reject('negative_polynomial_corner_rejected_after_subdivision',lambda:certify_polynomial(neg,8))
    # The all-zero polynomial is legitimate.
    check('zero_polynomial_certificate',replay_polynomial(sp.Integer(0),certify_polynomial(sp.Integer(0)))[0]==1)
    # Exact reset example and boundary perturbations.
    eta=sp.Rational(1,8);N=sp.diag(1,0,0);I=sp.eye(3)
    for eps in [sp.Rational(1,10),sp.Rational(1,100),sp.Rational(1,10000)]:
        Delta=sp.Matrix([[0,0,0],[eps,0,0],[0,0,0]])
        out=(I+Delta)*sp.Matrix([1,1,0])
        check('arbitrarily_small_boundary_violation_'+str(eps),out[0]**2-out[1]**2-out[2]**2<0)
        check('boundary_perturbation_preserves_mass_'+str(eps),list(Delta[0,:])==[0,0,0])
    corrected_identity=(1-eta)*I+eta*N
    for sign in [-1,1]:
        f,g=chart_polynomials(corrected_identity,sign,eta)
        check('exact_reset_boundary_margin_'+str(sign),sp.expand(g)==0 and sp.expand(f-(1-eta)*(1+V**2))==0)
    # The raw fitted family fails at a concrete rational state.
    original,fitted,initial,delta=noisy_fixture()
    w=(T*fitted['direct'].subs(U,-1)*T.inv())*sp.Matrix([1,1,0])
    q=sp.factor(w[0]**2-w[1]**2-w[2]**2)
    check('raw_fit_positive_mass',w[0]==sp.Rational(106321,82000))
    check('raw_fit_genuine_negative_quadratic_witness',q==-sp.Rational(12009932651317769,557059220496000000))
    for name,B in fitted.items():check('raw_fit_exact_mass_'+name,list(base_integral(B)[0,:])==[1,0,0])
    # Distinct noisy model, not hidden use of exact source operators.
    for name in original:check('perturbation_nonzero_'+name,fitted[name]!=original[name])
    # Exact envelope values and an elementary symbolic proposal-error identity.
    budget=sp.Rational(7,8)*sp.Rational(241,40000)+sp.Rational(1,4)
    check('repair_instrument_budget',budget==sp.Rational(81687,320000))
    check('horizon_seven_bound_nontrivial',7*budget/2<1)
    check('horizon_eight_bound_vacuous',8*budget/2>1)
    A=sp.Matrix([[sp.Rational(3,5),-sp.Rational(4,5)],[sp.Rational(4,5),sp.Rational(3,5)]])
    Ah=A+sp.Rational(1,100)*sp.Matrix([[1,0],[0,0]]);Hs=sp.eye(2)/2;Hh=sp.Matrix([[sp.Rational(51,100),0],[0,sp.Rational(49,100)]])
    M=lambda a,h:a.T*h*a-h
    residual=M(Ah,Hh)
    check('proposal_error_identity',M(A,Hh-Hs)==residual-(M(Ah,Hh)-M(A,Hh)))
    # A true interval-wide coefficient perturbation from the certified box.
    E0=sp.Matrix([[r/3,0,0],[r,-r,r],[-r,r,-r]])
    E1=sp.Matrix([[r,-r,r],[-r,r,r],[r,r,-r]])
    E2=sp.Matrix([[-r,0,0],[r,r,-r],[-r,-r,r]])
    D=E0+U*E1+U**2*E2
    check('coefficient_box_sample_exact_mass',list(base_integral(D)[0,:])==[0,0,0])
    check('coefficient_box_sample_entry_bounds',all(abs(x)<=r for E in [E0,E1,E2] for x in E))
    # Negative controls must reject incomplete proof coverage and false claims.
    first=sorted(cert['actions'])[0]
    controls=[
      ('unknown_schema',lambda c:c.update(schema='wrong')),
      ('wrong_reference_measure',lambda c:c['reference_measure'].update(density_wrt_lebesgue='1')),
      ('negative_margin',lambda c:c.update(margin='-1')),
      ('negative_error_budget',lambda c:c['uncertainty'].update(mass_output_bound='-1')),
      ('oversized_error_budget',lambda c:c['uncertainty'].update(spatial_output_bound='1')),
      ('oversized_coefficient_box',lambda c:c['uncertainty'].update(coefficient_box_radii_in_lorentz_coordinates=['1','1','1'])),
      ('false_statistical_claim',lambda c:c['uncertainty'].update(statistical_coverage_claimed=True)),
      ('missing_mass_restriction',lambda c:c['uncertainty'].update(exact_integrated_mass_required=False)),
      ('singular_transform',lambda c:c['transform_to_lorentz'].__setitem__(2,c['transform_to_lorentz'][1].copy())),
      ('wrong_mass_row_transform',lambda c:c['transform_to_lorentz'][0].__setitem__(0,'2')),
      ('outside_initial_state',lambda c:c['initial'][1].__setitem__(0,'100')),
      ('wrong_initial_mass',lambda c:c['initial'][0].__setitem__(0,'2')),
      ('missing_semicircle',lambda c:c['proofs'][first].pop('-1')),
      ('missing_orientation',lambda c:c['proofs'][first]['1'].pop('orientation')),
      ('missing_subdivision_leaf',lambda c:c['proofs'][first]['1']['cone_gap'].pop()),
      ('false_subdivision_bound',lambda c:c['proofs'][first]['1']['cone_gap'][0].update(lower_bound='999999')),
      ('overlapping_subdivision_leaf',lambda c:c['proofs'][first]['1']['cone_gap'].append(copy.deepcopy(c['proofs'][first]['1']['cone_gap'][0]))),
      ('broken_mass_operator',lambda c:c['actions'][first][0][0].__setitem__(0,'999')),
    ]
    for name,change in controls:reject(name,lambda change=change:replay_certificate(mutate(cert,change)))
    reject('float_input_rejected',lambda:rat(0.25))
    reject('nonrational_string_rejected',lambda:rat('sqrt(2)'))
    reject('unsafe_expression_rejected',lambda:rat('__import__("os")'))
    # Numerical proposal is expressly not exact evidence.
    Tnew,diag=propose_geometry(fitted,48)
    check('noisy_geometry_proposal_reproduced',Tnew==T,'numerical_proposal',diag)
    check('noisy_invariance_residual_nonzero',diag['least_squares_residual']>0,'numerical_diagnostic')
    counts={k:sum(r['kind']==k for r in records) for k in sorted({r['kind'] for r in records})}
    out={'suite':'robust_curved','passed':True,'records':len(records),'classification':counts,'checks':records,
         'claims':{'lean_verification':False,'statistical_coverage_estimated':False,'sample_grid_used_as_proof':False}}
    (ROOT/'verification/robust_curved_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':True,'records':len(records),'classification':counts},indent=2))

if __name__=='__main__':main()

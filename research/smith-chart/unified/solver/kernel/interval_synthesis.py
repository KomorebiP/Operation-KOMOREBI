"""Author: Komorebi P. Untrusted proposals, exact interval RLC acceptance.

Numerical fitting locates a candidate only. Rounded rational Newton steps
produce a rational center and preconditioner. An independent standard-library
checker reconstructs the graph equations and proves existence and uniqueness
of an exact positive circuit in its rational box. No tolerance accepts a circuit.
"""
from __future__ import annotations

from fractions import Fraction as F
import argparse
import json
from pathlib import Path
import time

from real_algebraic import trim, gcd
from interval_certificate import (
    build_coefficient_system, evaluate_system, evaluate_jacobian,
    invert_matrix, verify_interval_circuit,
)


def round_rational(value, digits=70):
    """Round exactly to a fixed decimal rational grid, no float conversion."""
    value = F(value)
    scale = 10 ** digits
    sign = -1 if value < 0 else 1
    a = abs(value.numerator) * scale
    n, r = divmod(a, value.denominator)
    return F(sign * (n + (2*r >= value.denominator)), scale)


def matrix_vector(A, x):
    return [sum((a*b for a, b in zip(row, x)), F(0)) for row in A]


def certify_candidate(P, Q, branches, values, *, fixed_parameters=None, digits=70, steps=7,
                      radius_digits=(10, 14, 18, 22, 28, 36, 44)):
    """Attempt a certificate around supplied untrusted positive parameters.

    Input branch parameters are conductance g, inverse inductance h, or
    capacitance c. Exact rational Newton is a proposal procedure, including
    rounding after each update. The independent verifier is the acceptance gate.
    """
    started = time.perf_counter()
    target = {'P': list(map(str, trim(P))), 'Q': list(map(str, trim(Q)))}
    try:
        system = build_coefficient_system(branches, target['P'], target['Q'], fixed_parameters)
        center = [round_rational(F(str(v)), digits) for v in values]
        if len(center) != len(branches) or any(v <= 0 for v in center):
            raise ValueError('Candidate parameters must be positive and match branch count')
        errors = []; updates = 0
        for step in range(steps):
            residual = evaluate_system(system, center)
            errors.append(str(max(map(abs, residual), default=F(0))))
            if not any(residual):
                break
            inv = invert_matrix(evaluate_jacobian(system, center))
            delta = matrix_vector(inv, residual)
            updated = [round_rational(a-b, digits) for a,b in zip(center, delta)]
            if any(v <= 0 for v in updated):
                raise ValueError('Rational Newton proposal left the positive domain')
            if updated == center:
                break
            center = updated; updates += 1
        inv = invert_matrix(evaluate_jacobian(system, center))
        # The rounded inverse is untrusted too. The checker verifies that it is
        # nonsingular and independently bounds I-YJ on the entire box.
        Y = [[round_rational(v, min(digits, 45)) for v in row] for row in inv]
        failures = []
        for exponent in radius_digits:
            radii = [max(abs(v), F(1)) / (10**exponent) for v in center]
            cert = {
                'format': 'komorebi-rlc-interval-v1',
                'target': target,
                'storage_budget': sum(b['type'] != 'g' for b in branches),
                'branches': [{'type':b['type'], 'nodes':list(b['nodes'])} for b in branches],
                'center': list(map(str, center)),
                'radii': list(map(str, radii)),
                'preconditioner': [list(map(str,row)) for row in Y],
            }
            if fixed_parameters:
                cert['fixed_parameters'] = fixed_parameters
            try:
                check = verify_interval_circuit(cert, expected_target=target,
                                                expected_budget=cert['storage_budget'])
            except (ValueError, ZeroDivisionError) as exc:
                failures.append({'radius_decimal_exponent':exponent,'reason':str(exc)})
                continue
            q = cert['storage_budget']
            minimum = q == system['reduced_target_degree']
            return {
                'status': 'CERTIFIED_MINIMUM' if minimum else 'CERTIFIED_REALIZATION',
                'route': 'positive numerical proposal + independent rational interval contraction',
                'minimum_reactive_count': q if minimum else None,
                'certificate':cert, 'verification':check,
                'proposal':{'digits':digits,'newton_steps':updates,'residual_evaluations':len(errors),
                            'radius_decimal_exponent':exponent,
                            'rational_residual_history':errors},
                'elapsed_seconds':time.perf_counter()-started,
            }
        return {'status':'UNKNOWN','reason':'No tested rational box certified the proposed root',
                'certificate_attempts':failures,'elapsed_seconds':time.perf_counter()-started}
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        return {'status':'UNKNOWN','reason':str(exc),'elapsed_seconds':time.perf_counter()-started}


def fit_existing_charts(P, Q, max_starts=8, max_nfev=500, seed=1204):
    """Target-only search in two archived charts. No completeness claim."""
    import numpy as np
    from scipy.optimize import least_squares
    from sparse_q3_templates import TEMPLATES, model
    P, Q = trim(P), trim(Q)
    if len(P)!=4 or len(Q)!=4 or len(gcd(P,Q))>1:
        return {'status':'UNKNOWN','reason':'Existing interval charts require a reduced (3,3) target'}
    target=np.array([float(a/P[3]) for a in P[:3]]+[float(a/P[3]) for a in Q])
    scales=np.maximum(1,np.abs(target));rng=np.random.default_rng(seed)
    attempts=[]
    for name, spec in TEMPLATES.items():
        ff,jj=model(name)
        branches=[{'type':{'R':'g','L':'h','C':'c'}[t],'nodes':[a,b]} for t,a,b in spec]
        def fun(z):
            return (np.ravel(ff(np.exp(z)))-target)/scales
        def jac(z):
            v=np.exp(z)
            return np.asarray(jj(v),dtype=float)*v[None,:]/scales[:,None]
        for i in range(max_starts):
            start=np.zeros(len(spec)) if i==0 else np.clip(rng.normal(0,1.4,len(spec)),-17,17)
            try:
                fit=least_squares(fun,start,jac=jac,bounds=(-18,18),max_nfev=max_nfev,
                                  ftol=1e-12,xtol=1e-12,gtol=1e-12)
                residual=float(max(abs(fun(fit.x))))
                attempts.append({'template':name,'start':i,'scaled_residual':residual})
                if not np.isfinite(residual) or residual>1e-8:
                    continue
                answer=certify_candidate(P,Q,branches,[str(float(x)) for x in np.exp(fit.x)])
            except (ValueError,ZeroDivisionError,FloatingPointError,OverflowError) as exc:
                attempts.append({'template':name,'start':i,'error':str(exc)})
                continue
            if answer['status']=='CERTIFIED_MINIMUM':
                answer['template']=name;answer['search_attempts']=attempts
                return answer
            attempts[-1]['certificate_rejection']=answer.get('reason')
    return {'status':'UNKNOWN','reason':'No certified root in the two searched charts',
            'search_attempts':attempts,'scope':'restricted charts, bounded starts; no impossibility conclusion'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--starts',type=int,default=8)
    parser.add_argument('--evaluations',type=int,default=500)
    args=parser.parse_args();data=json.loads(args.input.read_text())
    target=data.get('target',data)
    if 'branches' in data and 'values' in data:
        result=certify_candidate(target['P'],target['Q'],data['branches'],data['values'],
                                 fixed_parameters=data.get('fixed_parameters'))
    else:
        result=fit_existing_charts(target['P'],target['Q'],args.starts,args.evaluations)
    content=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(content)
    else:print(content)

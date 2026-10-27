#!/usr/bin/env python3
"""Check inexact discrepancy certificates for known rational Euclidean operators.

No inverse, parameter search, or true source is needed. The finite certificate
uses exact rational normal residuals and squared norm enclosures. The parser and
matrix implementation are tested Python, not extracted or formally verified Lean.
A valid external true-data noise allowance remains a theorem hypothesis.
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction as Q
from pathlib import Path
from typing import Any, Mapping
from observable_model import Matrix
from hilbert_certificate import dimension, transpose, add, scale, norm_sq
from tikhonov_certificate import coefficient, matrix, vector
from discrepancy_certificate import json_value


def nonnegative(value: Any, label: str) -> Q:
    q = coefficient(value)
    if q < 0:
        raise ValueError(label + ' must be nonnegative.')
    return q


def validate(a: Matrix, v: Matrix, x: Matrix, eta: Q, tau: Q, kappa: Q,
             measured: Q, omega: Q, *, lam: Q | None = None,
             rho: Q | None = None, xi: Q | None = None,
             normal_measurement: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return checked identities and budgets, or reject. No approximate floats."""
    dimension(a.nrows); dimension(a.ncols)
    eta, tau = coefficient(eta), coefficient(tau)
    kappa = nonnegative(kappa, 'source tolerance')
    measured = nonnegative(measured, 'measured residual')
    omega = nonnegative(omega, 'measurement error')
    if eta <= 0 or tau <= 1:
        raise ValueError('Require noise allowance > 0 and upper multiplier > 1.')
    if (v.nrows, v.ncols) != (a.nrows, 1) or (x.nrows, x.ncols) != (a.ncols, 1):
        raise ValueError('Source/data dimensions do not match A.')
    if lam is None:
        if rho is not None or xi is not None or normal_measurement is not None:
            raise ValueError('Small-data certificate does not take normal-equation budgets.')
        d2 = norm_sq(v)
        if not max(Q(0), measured-omega)**2 <= d2 <= (measured+omega)**2:
            raise ValueError('Small-data norm measurement enclosure failed.')
        if measured+omega > tau*eta:
            raise ValueError('Small-data threshold is not certified.')
        if norm_sq(x) > kappa**2:
            raise ValueError('Approximate zero source exceeds source tolerance.')
        return {'branch': 'small_data', 'source': x, 'source_tolerance': kappa,
                'data_squared': d2, 'source_squared': norm_sq(x),
                'exact_comparison_source': Matrix.zero(a.ncols, 1),
                'measured_data_norm': measured, 'measurement_error': omega,
                'source_error_bound_squared': kappa**2}
    lam = coefficient(lam)
    if lam <= 0:
        raise ValueError('lambda must be strictly positive.')
    if rho is None or xi is None:
        raise ValueError('Positive branch requires normal and image error budgets.')
    rho = nonnegative(rho, 'normal-residual envelope')
    xi = nonnegative(xi, 'image-correction tolerance')
    at = transpose(a)
    normal = add(at@a, scale(Matrix.eye(a.ncols), lam))
    r = add(normal@x, at@v, Q(-1)); r2 = norm_sq(r)
    if normal_measurement is not None:
        allowed = {'vector', 'error_bound', 'norm_bound'}
        if not isinstance(normal_measurement, Mapping) or set(normal_measurement) != allowed:
            raise ValueError('normal_measurement requires vector, error_bound, norm_bound.')
        rhat = vector(normal_measurement['vector'], a.ncols)
        nu = nonnegative(normal_measurement['error_bound'], 'normal evaluation error')
        rhohat = nonnegative(normal_measurement['norm_bound'], 'observed normal bound')
        if norm_sq(add(r, rhat, Q(-1))) > nu**2:
            raise ValueError('Normal-residual evaluation enclosure failed.')
        if norm_sq(rhat) > rhohat**2 or rhohat+nu > rho:
            raise ValueError('Normal-residual measurement envelope is inadequate.')
    if r2 > rho**2:
        raise ValueError('Actual normal residual exceeds its envelope.')
    if rho**2 > (lam*kappa)**2:
        raise ValueError('Source correction budget failed: rho > lambda*kappa.')
    if rho**2 > 4*lam*xi**2:
        raise ValueError('Image correction budget failed: rho^2 > 4*lambda*xi^2.')
    fit = add(a@x, v, Q(-1)); d2 = norm_sq(fit)
    if not max(Q(0), measured-omega)**2 <= d2 <= (measured+omega)**2:
        raise ValueError('Fitting-residual measurement enclosure failed.')
    lower = eta+omega+xi; upper = tau*eta-omega-xi
    if lower > upper:
        raise ValueError('Error budgets leave no protected discrepancy window.')
    if not lower <= measured <= upper:
        raise ValueError('Measured discrepancy lacks the required protected margins.')
    return {'branch': 'positive_parameter', 'lambda': lam, 'source': x,
            'normal_residual': r, 'normal_residual_squared': r2,
            'normal_envelope': rho, 'normal_envelope_squared': rho**2,
            'source_tolerance': kappa, 'source_error_bound_squared': kappa**2,
            'image_tolerance': xi, 'image_error_bound_squared': xi**2,
            'sharp_source_bound_squared': r2/(lam*lam),
            'sharp_image_bound_squared': r2/(4*lam),
            'fitting_residual_squared': d2, 'measured_residual': measured,
            'measurement_error': omega, 'protected_interval': [lower, upper],
            'implied_exact_discrepancy_squared_interval': [eta**2, (tau*eta)**2],
            'certificate_conditions': {
                'normal_envelope': True, 'scaled_source_tolerance': True,
                'sharp_image_tolerance': True, 'measurement_enclosure': True,
                'both_protected_margins': True}}


def run_document(doc: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(doc, Mapping):
        raise ValueError('Input must be an object.')
    allowed = {'schema_version','coefficient_domain','global_dimension','local_dimension',
               'A','local_vector','candidate_source','noise_allowance','upper_multiplier',
               'source_tolerance','branch','measured_residual','measurement_error',
               'lambda','normal_envelope','image_tolerance','normal_measurement'}
    if set(doc)-allowed:
        raise ValueError('Unknown input fields: '+repr(sorted(set(doc)-allowed)))
    if type(doc.get('schema_version')) is not int or doc['schema_version'] != 1:
        raise ValueError('Expected integer schema_version=1.')
    if doc.get('coefficient_domain') != 'Q':
        raise ValueError('Expected coefficient_domain=Q.')
    d,n = dimension(doc['global_dimension']), dimension(doc['local_dimension'])
    a = matrix(doc['A'], d)
    if a.nrows != n:
        raise ValueError('Declared local dimension mismatch.')
    v,x = vector(doc['local_vector'], n),vector(doc['candidate_source'], d)
    branch = doc['branch']
    if branch not in ('positive_parameter','small_data'):
        raise ValueError('Unknown certificate branch.')
    if branch == 'small_data' and any(k in doc for k in
        ('lambda','normal_envelope','image_tolerance','normal_measurement')):
        raise ValueError('Small-data branch cannot contain positive-branch fields.')
    c = validate(a,v,x,coefficient(doc['noise_allowance']),coefficient(doc['upper_multiplier']),
        coefficient(doc['source_tolerance']),coefficient(doc['measured_residual']),
        coefficient(doc['measurement_error']),
        lam=coefficient(doc['lambda']) if branch=='positive_parameter' else None,
        rho=coefficient(doc['normal_envelope']) if branch=='positive_parameter' else None,
        xi=coefficient(doc['image_tolerance']) if branch=='positive_parameter' else None,
        normal_measurement=doc.get('normal_measurement'))
    return json_value({'schema_version':1,'coefficient_domain':'Q','status':'certified_inexact',
        'certificate':c,'external_assumptions':[
          'The supplied noise allowance must bound error relative to the intended true source.',
          'For source consistency, use a fixed operator and noise/source tolerances tending to zero.'],
        'trust_boundary':'Exact rational known Euclidean matrices; no inverse or search needed. Python matrix arithmetic/parser are tested, not Lean-verified. Mathematical certificate soundness is proved separately.'})


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.input.stat().st_size>1_000_000:
            raise ValueError('Input exceeds 1 MB.')
        out=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(out,indent=2)+'\n')
        print('PASS inexact discrepancy certificate:',args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError) as e:
        ap.exit(2,'ERROR: '+str(e)+'\n')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Exact-rational discrepancy selection for known Euclidean matrix models.

Only A, observed data, a positive noise allowance, and discrepancy-band constants
are used. No true source or prechosen lambda is an input. The search and parser
are tested Python, not formally verified or extracted from Lean. A resource cap
raises an error, never a success certificate.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction as Q
from pathlib import Path
from typing import Any, Mapping
from observable_model import Matrix
from hilbert_certificate import dimension, transpose, add, scale, inverse, norm_sq
from reconstruction_certificate import construct as pseudoinverse
from tikhonov_certificate import coefficient, matrix, vector


def json_value(value: Any) -> Any:
    if isinstance(value, Matrix): return value.json()
    if isinstance(value, Q): return str(value)
    if isinstance(value, dict): return {key: json_value(v) for key, v in value.items()}
    if isinstance(value, (list, tuple)): return [json_value(v) for v in value]
    return value


def validate(a: Matrix, v: Matrix, eta: Q, upper: Q, x: Matrix,
             lam: Q | None) -> dict[str, Any]:
    eta, upper = coefficient(eta), coefficient(upper)
    if eta <= 0 or upper <= 1:
        raise ValueError('Require eta > 0 and upper > 1.')
    if (v.nrows, v.ncols) != (a.nrows, 1) or (x.nrows, x.ncols) != (a.ncols, 1):
        raise ValueError('Source or data dimensions do not match A.')
    r = add(a@x, v, Q(-1)); r2 = norm_sq(r)
    if lam is None:
        if x != Matrix.zero(a.ncols, 1) or norm_sq(v) > upper**2*eta**2:
            raise ValueError('Invalid small-data certificate.')
        return {'branch': 'small_data', 'lambda': None, 'source': x,
                'residual_squared': r2, 'data_squared': norm_sq(v)}
    lam = coefficient(lam)
    if lam <= 0:
        raise ValueError('Positive-parameter certificate requires lambda > 0.')
    n = add(transpose(a)@a, scale(Matrix.eye(a.ncols), lam))
    nr = add(n@x, transpose(a)@v, Q(-1))
    if nr != Matrix.zero(a.ncols, 1):
        raise ValueError('Exact normal equation failed.')
    if not eta**2 <= r2 <= upper**2*eta**2:
        raise ValueError('Actual discrepancy is outside the accepted interval.')
    return {'branch': 'positive_parameter', 'lambda': lam, 'source': x,
            'residual_squared': r2, 'normal_residual': nr,
            'accepted_residual_squared_interval': [eta**2, upper**2*eta**2]}


def select(a: Matrix, v: Matrix, eta: Q, lower: Q = Q(3, 2),
           upper: Q = Q(2), max_steps: int = 256) -> dict[str, Any]:
    dimension(a.nrows); dimension(a.ncols)
    if max(a.nrows, a.ncols) > 8:
        raise ValueError('This search caps source and data dimensions at 8.')
    if type(max_steps) is not int or not 1 <= max_steps <= 512:
        raise ValueError('max_steps must be an integer in 1..512.')
    eta, lower, upper = map(coefficient, (eta, lower, upper))
    if eta <= 0 or not 1 < lower < upper:
        raise ValueError('Require eta > 0 and 1 < lower < upper.')
    if (v.nrows, v.ncols) != (a.nrows, 1):
        raise ValueError('Data dimensions do not match A.')
    # In finite Euclidean spaces, this is an actual nearest feasible datum.
    witness = pseudoinverse(a)['recovery']@v
    floor2 = norm_sq(add(a@witness, v, Q(-1)))
    if floor2 > eta**2:
        raise ValueError('No global source fits within the stated noise allowance.')
    if norm_sq(v) <= upper**2*eta**2:
        c = validate(a, v, eta, upper, Matrix.zero(a.ncols, 1), None)
        c.update({'evaluations': 0, 'trace': [], 'feasible_witness': witness,
                  'feasible_residual_squared': floor2})
        return c
    at = transpose(a); gram = at@a; rhs = at@v
    lo = hi = None; lam = Q(1); trace = []
    for step in range(max_steps):
        coefficient(lam)  # enforce the rational-size resource cap
        x = inverse(add(gram, scale(Matrix.eye(a.ncols), lam)))@rhs
        r2 = norm_sq(add(a@x, v, Q(-1)))
        trace.append({'lambda': lam, 'residual_squared': r2})
        if lower**2*eta**2 <= r2 <= upper**2*eta**2:
            c = validate(a, v, eta, upper, x, lam)
            c.update({'evaluations': step+1, 'trace': trace, 'lower_multiplier': lower,
                      'upper_multiplier': upper, 'feasible_witness': witness,
                      'feasible_residual_squared': floor2})
            return c
        if r2 < lower**2*eta**2:
            lo = lam
            lam = 2*lam if hi is None else (lo+hi)/2
        else:
            hi = lam
            lam = lam/2 if lo is None else (lo+hi)/2
    raise RuntimeError('Discrepancy search resource cap reached; no certificate returned.')


def run_document(doc: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(doc, Mapping):
        raise ValueError('Input must be an object.')
    allowed = {'schema_version','coefficient_domain','global_dimension','local_dimension',
               'A','local_vector','noise_allowance','lower_multiplier','upper_multiplier','max_steps'}
    if set(doc)-allowed:
        raise ValueError('Unknown fields: '+repr(sorted(set(doc)-allowed)))
    if type(doc.get('schema_version')) is not int or doc['schema_version'] != 1 or doc.get('coefficient_domain') != 'Q':
        raise ValueError('Expected schema_version=1 and coefficient_domain=Q.')
    n, d = dimension(doc['local_dimension']), dimension(doc['global_dimension'])
    a = matrix(doc['A'], d)
    if a.nrows != n:
        raise ValueError('Declared local dimension mismatch.')
    v = vector(doc['local_vector'], n)
    c = select(a,v,coefficient(doc['noise_allowance']),
               coefficient(doc.get('lower_multiplier','3/2')),
               coefficient(doc.get('upper_multiplier',2)),doc.get('max_steps',256))
    return json_value({'schema_version':1,'coefficient_domain':'Q','certificate':c,
        'trust_boundary':'Exact rational known Euclidean matrices. Python search/parser and elimination are not Lean-verified. A discrepancy band is certified, not an exact real root. Source consistency uses a valid noise bound and a fixed operator.'})


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try:
        if args.input.stat().st_size>1_000_000:
            raise ValueError('Input exceeds 1 MB.')
        result=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print('PASS exact discrepancy certificate:', args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError,RuntimeError) as e:
        p.exit(2,'ERROR: '+str(e)+'\n')

if __name__=='__main__': main()

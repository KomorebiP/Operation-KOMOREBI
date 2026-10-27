#!/usr/bin/env python3
"""Exact rational quotient-metric checks for known Euclidean presentation matrices.

Two routes are compared: ambient orthogonal projection and constrained minimization
in a possibly nonorthogonal compatible basis with its actual Gram matrix. The
standard Euclidean metric is not imposed on those basis coefficients. This Python
implementation is tested, not extracted from or verified by Lean.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Mapping
from fractions import Fraction as Q
from hilbert_certificate import (Matrix, add, transpose, inverse, column_basis,
    kernel_basis, projector_from_basis, construct, evaluate, norm_sq, dimension, json_value)


def certificate(a: Matrix, delta: Matrix, v: Matrix,
                compatible_basis: Matrix | None = None) -> dict[str, Any]:
    c = construct(a, delta)
    e = evaluate(c, v)
    n = a.nrows
    b = kernel_basis(delta) if compatible_basis is None else compatible_basis
    if b.nrows != n or b.ncols != kernel_basis(delta).ncols:
        raise ValueError('Compatible basis must have the full kernel dimension.')
    if column_basis(b).ncols != b.ncols:
        raise ValueError('Compatible basis columns are dependent.')
    if delta @ b != Matrix.zero(delta.nrows, b.ncols):
        raise ValueError('Compatible basis contains an incompatible vector.')
    gram = transpose(b) @ b
    analysis = inverse(gram) @ transpose(b)
    compatible = c['kernel_projector'] @ v
    x = analysis @ compatible
    j = analysis @ column_basis(a)
    # Constrained minimum in the actual, generally nonidentity, Gram metric.
    correction = j @ inverse(transpose(j) @ gram @ j) @ transpose(j) @ gram @ x
    y = add(x, correction, Q(-1))
    minimum = b @ y
    energy = (transpose(y) @ gram @ y).rows[0][0]
    normal = transpose(j) @ gram @ y
    naive = add(x, projector_from_basis(j) @ x, Q(-1))
    if minimum != e['obstruction'] or energy != e['obstruction_squared']:
        raise ArithmeticError('Ambient and quotient-coordinate constructions disagree.')
    if normal != Matrix.zero(j.ncols, 1):
        raise ArithmeticError('Quotient minimizing normal equation failed.')
    if e['error_squared'] != energy + e['inconsistency_squared']:
        raise ArithmeticError('Intrinsic reconstruction identity failed.')
    return {'compatible_basis': b, 'gram_matrix': gram, 'compatible_coordinates': x,
            'realized_coordinate_basis': j, 'minimum_coordinates': y,
            'minimum_representative': minimum, 'quotient_norm_squared': energy,
            'naive_identity_metric_quotient_squared': norm_sq(naive),
            'realized': e['realized'], 'inconsistency': e['inconsistency'],
            'inconsistency_squared': e['inconsistency_squared'],
            'reconstruction_error_squared': e['error_squared'],
            'normal_equation_residual': normal}


def run_document(doc: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(doc, Mapping):
        raise ValueError('Input must be a JSON object.')
    if type(doc.get('schema_version')) is not int or doc['schema_version'] != 1:
        raise ValueError('Expected schema_version=1.')
    if doc.get('coefficient_domain') != 'Q':
        raise ValueError('Expected coefficient_domain=Q.')
    n,g,w = (dimension(doc[k]) for k in ('local_dimension','global_dimension','residual_dimension'))
    a, delta = Matrix.parse(doc['A'],g), Matrix.parse(doc['delta'],n)
    if a.nrows != n or delta.nrows != w:
        raise ValueError('Declared dimensions do not match matrices.')
    vals = doc['local_vector']
    if not isinstance(vals,list) or len(vals) != n:
        raise ValueError('Local vector has the wrong length.')
    v = Matrix.parse([[x] for x in vals],1)
    b = None
    if 'compatible_basis' in doc:
        k = dimension(doc['compatible_dimension'])
        b = Matrix.parse(doc['compatible_basis'], k)
    return json_value({'schema_version':1,'coefficient_domain':'Q',
        'evaluation':certificate(a,delta,v,b),
        'trust_boundary':'Finite exact rational checks; Python and parsing are not formally verified. '
        'The Gram matrix is inherited from the ambient Euclidean metric, not chosen to force an identity.'})


def verify_output(doc: Mapping[str, Any], proposed: Mapping[str, Any]) -> None:
    if run_document(doc) != proposed:
        raise ValueError('Proposed certificate differs from exact recomputation.')


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.input.stat().st_size > 1_000_000:
            raise ValueError('Input exceeds 1 MB.')
        result=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print('PASS exact quotient metric:',args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError) as exc:
        ap.exit(2,'ERROR: '+str(exc)+'\n')

if __name__=='__main__': main()

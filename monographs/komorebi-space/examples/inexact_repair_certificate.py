#!/usr/bin/env python3
"""Certify a proposed protected correction without computing the optimizer.

Usage:
  python examples/inexact_repair_certificate.py                 # worked examples
  python examples/inexact_repair_certificate.py --input p.json  # build certificate
  python examples/inexact_repair_certificate.py --verify c.json # check saved record

Input keys: d, p, f, alpha, correction; optional measured_residual, basis,
and dual_witness. Entries are integers or rational strings. The operator and
protected map are treated as exact. Uncertain models need separate error bounds.
The certificate's error bounds concern the regularized optimizer at this alpha,
not the existence of a zero-residual answer. No universal Python/Lean refinement
is asserted. All reported quantities are exact rationals or squared norm bounds.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from typing import Any, Sequence
from budgeted_repair import (Rational, Vector, Matrix, rational, vector, matrix,
    dot, mv, transpose, mm, sub, norm2, rref, kernel_basis, solve_square, jsonable)


def _basis(p: Matrix, n: int, supplied: Sequence[Sequence[Rational]] | None) -> Matrix:
    """Verify the full protected kernel, not just a convenient subspace of it."""
    canonical = kernel_basis(p, n)
    k = len(canonical[0])
    if supplied is None:
        return canonical
    b = matrix(supplied)
    if len(b) != n or any(len(row) != k for row in b):
        raise ValueError('basis must have n rows and exactly dim(ker p) columns')
    if len(rref(b, k)[1]) != k:
        raise ValueError('basis columns are linearly dependent')
    if any(x for row in mm(p, b) for x in row):
        raise ValueError('basis is not contained in the protected kernel')
    return b


def certify(d: Sequence[Sequence[Rational]], p: Sequence[Sequence[Rational]],
            f: Sequence[Rational], alpha: Rational,
            correction: Sequence[Rational],
            measured_residual: Sequence[Rational] | None = None,
            basis: Sequence[Sequence[Rational]] | None = None,
            dual_witness: Sequence[Rational] | None = None) -> dict[str, Any]:
    ff, aa = vector(f), vector(correction)
    n = len(ff)
    if not n or len(aa) != n:
        raise ValueError('f and correction must have the same positive dimension')
    dd, pp = matrix(d, n), matrix(p, n)
    if not dd:
        raise ValueError('d needs at least one residual coordinate')
    al = rational(alpha)
    if al <= 0:
        raise ValueError('alpha must be strictly positive')
    if any(mv(pp, aa)):
        raise ValueError('The proposed correction changes protected data')
    rr = mv(dd, ff) if measured_residual is None else vector(measured_residual)
    if len(rr) != len(dd):
        raise ValueError('Residual-data dimension mismatch')
    bb = _basis(pp, n, basis)
    k = len(bb[0])
    gg = mm(transpose(bb), bb) if k else []
    ss = mm(dd, bb)
    cc = solve_square(gg, mv(transpose(bb), aa)) if k else []
    if mv(bb, cc) != aa:
        raise ArithmeticError('The candidate is not represented by the verified kernel basis')
    vv = sub(rr, mv(dd, aa))
    zz = vv[:] if dual_witness is None else vector(dual_witness)
    if len(zz) != len(rr):
        raise ValueError('Dual-witness dimension mismatch')
    # q is a covector. The actual Hilbert normal residual is B G^{-1} q.
    q = sub([al*x for x in mv(gg, cc)], mv(transpose(ss), vv)) if k else []
    qsharp = solve_square(gg, q) if k else []
    grad = mv(bb, qsharp)
    eps2 = dot(q, qsharp)
    adjcoords = solve_square(gg, mv(transpose(ss), zz)) if k else []
    adjz = mv(bb, adjcoords)
    obj = norm2(vv) + al*norm2(aa)
    dual = 2*dot(rr, zz) - norm2(zz) - norm2(adjz)/al
    gap = obj-dual
    first = sub(zz, vv)
    second = sub(adjz, [al*x for x in aa])
    gap_check = norm2(first) + norm2(second)/al
    candidate = sub(ff, aa)
    before, after = mv(pp, ff), mv(pp, candidate)
    if eps2 < 0 or norm2(grad) != eps2 or gap != gap_check or gap < 0 or before != after:
        raise ArithmeticError('Exact certificate identity failed')
    cert = {
        'kernel_dimension': k, 'kernel_gram': gg, 'correction_coordinates': cc,
        'normal_coordinate_covector': q, 'normal_residual': grad,
        'normal_residual_norm_squared': eps2,
        'coordinate_covector_norm_squared_not_a_Hilbert_certificate': norm2(q),
        'candidate': candidate, 'protected_before': before, 'protected_after': after,
        'fit_residual': vv, 'actual_candidate_residual': mv(dd, candidate),
        'objective': obj, 'dual_value': dual, 'duality_gap': gap,
        'duality_gap_identity_residual': gap-gap_check,
        'correction_error_norm_squared_upper': eps2/(al*al),
        'fitted_error_norm_squared_upper': eps2/(4*al),
        'objective_suboptimality_upper': eps2/al,
        'dual_correction_error_norm_squared_upper': gap/al,
        'scope': 'Bounds to the exact regularized optimizer for these fixed maps, data, and positive alpha. Not bounds to an assumed exact realization.'}
    problem = {'d': dd, 'p': pp, 'f': ff, 'alpha': al, 'correction': aa,
               'measured_residual': rr, 'basis': bb, 'dual_witness': zz}
    return {'schema': 'komorebi-inexact-repair-certificate-v1', 'problem': problem, 'certificate': cert}


def verify_record(record: dict[str, Any]) -> bool:
    """Recompute all certificate claims from the supplied mathematical problem."""
    if not isinstance(record, dict) or set(record) != {'schema', 'problem', 'certificate'}:
        raise ValueError('Expected exactly schema, problem, and certificate')
    if record['schema'] != 'komorebi-inexact-repair-certificate-v1':
        raise ValueError('Unrecognized certificate schema')
    if not isinstance(record['problem'], dict):
        raise ValueError('problem must be an object')
    rebuilt = jsonable(certify(**record['problem']))
    if jsonable(record) != rebuilt:
        raise ValueError('A certificate claim differs from exact recomputation')
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--input', type=Path)
    group.add_argument('--verify', type=Path)
    args = parser.parse_args()
    try:
        if args.verify:
            obj = json.loads(args.verify.read_text())
            verify_record(obj)
            print(json.dumps({'status': 'PASS', 'scope': 'Exact finite certificate recomputation'}, indent=2))
        elif args.input:
            print(json.dumps(jsonable(certify(**json.loads(args.input.read_text()))), indent=2))
        else:
            rows = [certify([[1,0]], [[1,-1]], [1,0], 1, ['1/4','1/4']),
                    certify([[1,0]], [[1,-1]], [1,0], 1, ['1/4','1/4'], basis=[[7],[7]]),
                    certify([[0]], [], [0], '1/100', [1]),
                    certify([[1,0]], [[1,0],[0,1]], [1,2], 1, [0,0])]
            print(json.dumps(jsonable(rows), indent=2))
    except (TypeError, ValueError, ArithmeticError, OSError) as exc:
        parser.exit(2, f'certificate error: {exc}\n')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

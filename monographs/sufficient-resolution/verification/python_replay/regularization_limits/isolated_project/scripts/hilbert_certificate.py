#!/usr/bin/env python3
"""Exact-rational Euclidean globalization certificates for KNOWN matrices.

Input: A : Q^g -> Q^n, delta : Q^n -> Q^w, delta*A=0, and a local vector.
Output: actual orthogonal components, a best global preimage, and a squared
conditioning certificate. PSD is checked exactly by rational Schur complements.
No floating singular values are used. Python is NOT extracted or verified Lean.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from typing import Any, Mapping
from observable_model import Matrix, rational, row_basis

MAX_DIM = 16


def dimension(v: Any) -> int:
    if type(v) is not int or not 0 <= v <= MAX_DIM:
        raise ValueError(f'Dimensions must be integers in 0..{MAX_DIM}.')
    return v


def transpose(a: Matrix) -> Matrix:
    return Matrix(tuple(tuple(a.rows[i][j] for i in range(a.nrows))
                        for j in range(a.ncols)), a.nrows)


def add(a: Matrix, b: Matrix, sign: Q = Q(1)) -> Matrix:
    if (a.nrows, a.ncols) != (b.nrows, b.ncols):
        raise ValueError('Addition dimension mismatch.')
    return Matrix(tuple(tuple(x + sign*y for x,y in zip(r,s))
                        for r,s in zip(a.rows,b.rows)),a.ncols)


def scale(a: Matrix, c: Q) -> Matrix:
    return Matrix(tuple(tuple(c*x for x in row) for row in a.rows),a.ncols)


def rref(a: Matrix) -> tuple[Matrix, list[int]]:
    b, _, piv = row_basis(a, [{} for _ in a.rows])
    return b, piv


def inverse(a: Matrix) -> Matrix:
    if a.nrows != a.ncols:
        raise ValueError('Inverse requires a square matrix.')
    n = a.ncols
    augmented = Matrix(tuple(a.rows[i] + Matrix.eye(n).rows[i] for i in range(n)),2*n)
    rr, piv = rref(augmented)
    if piv != list(range(n)):
        raise ValueError('Singular matrix.')
    return Matrix(tuple(row[n:] for row in rr.rows),n)


def column_basis(a: Matrix) -> Matrix:
    _, piv = rref(a)
    return Matrix(tuple(tuple(row[j] for j in piv) for row in a.rows),len(piv))


def kernel_basis(a: Matrix) -> Matrix:
    rr, piv = rref(a)
    free = [j for j in range(a.ncols) if j not in piv]
    cols = []
    for j in free:
        v = [Q(0)] * a.ncols
        v[j] = Q(1)
        for i,k in enumerate(piv):
            v[k] = -rr.rows[i][j]
        cols.append(v)
    return Matrix(tuple(tuple(col[i] for col in cols) for i in range(a.ncols)),len(cols))


def projector_from_basis(b: Matrix) -> Matrix:
    return b @ inverse(transpose(b) @ b) @ transpose(b)


def positive_semidefinite(a: Matrix) -> bool:
    """Exact PSD criterion, including singular and empty matrices."""
    if a.nrows != a.ncols or transpose(a) != a:
        return False
    rows = [list(row) for row in a.rows]
    while rows:
        p = rows[0][0]
        if p < 0:
            return False
        if p == 0:
            if any(rows[0][j] != 0 for j in range(1,len(rows))):
                return False
            rows = [row[1:] for row in rows[1:]]
        else:
            rows = [[rows[i][j] - rows[i][0]*rows[0][j]/p
                     for j in range(1,len(rows))] for i in range(1,len(rows))]
    return True


def norm_sq(v: Matrix) -> Q:
    if v.ncols != 1:
        raise ValueError('Expected a column vector.')
    return sum((row[0]**2 for row in v.rows),Q(0))


def solve_consistent(a: Matrix, v: Matrix) -> Matrix:
    if v.nrows != a.nrows or v.ncols != 1:
        raise ValueError('Solve dimension mismatch.')
    rr, piv = rref(Matrix(tuple(a.rows[i]+v.rows[i] for i in range(a.nrows)),a.ncols+1))
    if a.ncols in piv:
        raise ValueError('Inconsistent global reconstruction.')
    x = [Q(0)] * a.ncols
    for i,j in enumerate(piv):
        x[j] = rr.rows[i][-1]
    return Matrix(tuple((t,) for t in x),1)


def construct(a: Matrix, delta: Matrix, sigma_sq: Q | None = None) -> dict[str, Any]:
    n = dimension(a.nrows)
    dimension(a.ncols); dimension(delta.nrows)
    if delta.ncols != n:
        raise ValueError('Compatibility operator has the wrong domain.')
    if delta @ a != Matrix.zero(delta.nrows,a.ncols):
        raise ValueError('Chain condition delta*A=0 fails.')
    br, bk = column_basis(a), kernel_basis(delta)
    pr, pk = projector_from_basis(br), projector_from_basis(bk)
    po, pi = add(pk,pr,Q(-1)), add(Matrix.eye(n),pk,Q(-1))
    # An exact lift of compatibility data on ker(delta)^perp.
    bi = column_basis(transpose(delta))
    f = delta @ bi
    j = bi @ inverse(transpose(f) @ f) @ transpose(f)
    if j @ delta != pi:
        raise ArithmeticError('Orthogonal-complement lift identity failed.')
    c2 = sum((x*x for row in j.rows for x in row),Q(0))
    if sigma_sq is None:
        sigma_sq = Q(1)/c2 if c2 else Q(1)
    sigma_sq = rational(sigma_sq)
    if sigma_sq <= 0:
        raise ValueError('sigma_squared must be strictly positive.')
    witness = add(transpose(delta) @ delta,scale(pi,sigma_sq),Q(-1))
    if not positive_semidefinite(witness):
        raise ValueError('Proposed whole-map coercivity certificate is false.')
    return {'A':a,'delta':delta,'realized_projector':pr,'kernel_projector':pk,
            'obstruction_projector':po,'inconsistency_projector':pi,
            'complement_lift':j,'sigma_squared':sigma_sq,'psd_witness':witness,
            'ranks':{'realized':br.ncols,'obstruction':bk.ncols-br.ncols,
                     'inconsistency':n-bk.ncols}}


def evaluate(cert: Mapping[str,Any], v: Matrix) -> dict[str,Any]:
    a, delta = cert['A'],cert['delta']
    if v.ncols != 1 or v.nrows != a.nrows:
        raise ValueError('Local-vector dimension mismatch.')
    r = cert['realized_projector'] @ v
    o = cert['obstruction_projector'] @ v
    i = cert['inconsistency_projector'] @ v
    g = solve_consistent(a,r)
    e2, o2, i2, res2 = norm_sq(add(v,r,Q(-1))),norm_sq(o),norm_sq(i),norm_sq(delta@v)
    b2 = o2 + res2/cert['sigma_squared']
    if a@g != r or add(add(r,o),i) != v or e2 != o2+i2 or e2>b2:
        raise ArithmeticError('Globalization certificate identity failed.')
    return {'realized':r,'obstruction':o,'inconsistency':i,'global_preimage':g,
            'error_squared':e2,'obstruction_squared':o2,'inconsistency_squared':i2,
            'residual_squared':res2,'bound_squared':b2}


def json_value(v: Any) -> Any:
    if isinstance(v,Matrix): return v.json()
    if isinstance(v,Q): return str(v)
    if isinstance(v,dict): return {k:json_value(x) for k,x in v.items()}
    return v


def run_document(doc: Mapping[str,Any]) -> dict[str,Any]:
    if doc.get('schema_version') != 1 or doc.get('coefficient_domain') != 'Q':
        raise ValueError('Expected schema_version=1 and coefficient_domain=Q.')
    n,g,w = (dimension(doc[k]) for k in ('local_dimension','global_dimension','residual_dimension'))
    a, delta = Matrix.parse(doc['A'],g),Matrix.parse(doc['delta'],n)
    if a.nrows != n or delta.nrows != w:
        raise ValueError('Declared matrix dimensions do not match the data.')
    vals = doc['local_vector']
    if len(vals) != n: raise ValueError('Local-vector length mismatch.')
    v = Matrix.parse([[t] for t in vals],1)
    s = rational(doc['sigma_squared']) if 'sigma_squared' in doc else None
    cert = construct(a,delta,s)
    return json_value({'schema_version':1,'coefficient_domain':'Q','certificate':cert,
        'evaluation':evaluate(cert,v),
        'trust_boundary':'Exact Python checks, not an extracted or formally verified Lean implementation. Known matrices and standard Euclidean inner products only. The certificate verifies sigma squared, not a floating singular value.'})


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.input.stat().st_size>1_000_000: raise ValueError('Input exceeds 1 MB.')
        result=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print('PASS exact rational certificate:',args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError) as exc:
        ap.exit(2,'ERROR: '+str(exc)+'\n')

if __name__=='__main__': main()

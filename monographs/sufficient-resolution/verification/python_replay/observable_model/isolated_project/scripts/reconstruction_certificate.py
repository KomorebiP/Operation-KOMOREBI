#!/usr/bin/env python3
"""Exact rational Moore-Penrose reconstruction and independent norm certificates.

Known rational matrices with standard Euclidean inner products only. The Python
elimination and parser are tested, not formally verified or extracted from Lean.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
from typing import Any, Mapping
from observable_model import Matrix, rational
from hilbert_certificate import (dimension,transpose,add,scale,inverse,column_basis,
    projector_from_basis,positive_semidefinite,norm_sq,json_value,construct as local_construct,
    evaluate as local_evaluate)


def validate_reconstruction(a: Matrix, b: Matrix, alpha_sq: Q) -> dict[str,Any]:
    """Check whole-map Penrose equations and a squared source-coercivity witness."""
    if b.nrows!=a.ncols or b.ncols!=a.nrows:
        raise ValueError('Reconstruction dimensions are incompatible.')
    alpha_sq=rational(alpha_sq)
    if alpha_sq<=0: raise ValueError('alpha_squared must be positive.')
    p, q=a@b,b@a
    checks={'ABA=A':p@a==a,'BAB=B':q@b==b,
            'AB symmetric':transpose(p)==p,'BA symmetric':transpose(q)==q}
    if not all(checks.values()): raise ValueError('Penrose certificate failed: '+str(checks))
    w=add(transpose(a)@a,scale(q,alpha_sq),Q(-1))
    if not positive_semidefinite(w):
        raise ValueError('Source coercivity certificate is false.')
    return {'recovery':b,'image_projector':p,'identifiable_projector':q,
            'source_kernel_projector':add(Matrix.eye(a.ncols),q,Q(-1)),
            'alpha_squared':alpha_sq,'source_psd_witness':w,'penrose_checks':checks}


def construct(a: Matrix, alpha_sq: Q|None=None) -> dict[str,Any]:
    dimension(a.nrows); dimension(a.ncols)
    j=column_basis(transpose(a))
    f=a@j
    b=j@inverse(transpose(f)@f)@transpose(f)
    b_frobenius_sq=sum((x*x for row in b.rows for x in row),Q(0))
    if alpha_sq is None: alpha_sq=Q(1)/b_frobenius_sq if b_frobenius_sq else Q(1)
    cert=validate_reconstruction(a,b,alpha_sq)
    cert.update({'A':a,'rank':j.ncols,'recovery_frobenius_squared':b_frobenius_sq})
    return cert


def evaluate(cert:Mapping[str,Any],v:Matrix,candidate:Matrix|None=None)->dict[str,Any]:
    a,b=cert['A'],cert['recovery']
    if v.ncols!=1 or v.nrows!=a.nrows: raise ValueError('Local vector dimension mismatch.')
    g=b@v; image=a@g; residual=add(v,image,Q(-1))
    result={'minimum_norm_source':g,'best_image':image,'residual':residual,
            'source_norm_squared':norm_sq(g),'local_error_squared':norm_sq(residual),
            'source_bound_squared':norm_sq(v)/cert['alpha_squared']}
    if norm_sq(g)>result['source_bound_squared']: raise ArithmeticError('Source bound failed.')
    if candidate is not None:
        if candidate.nrows!=a.ncols or candidate.ncols!=1: raise ValueError('Candidate dimension mismatch.')
        e=add(candidate,g,Q(-1)); hidden=cert['source_kernel_projector']@candidate
        image_error=add(a@candidate,image,Q(-1))
        cap=norm_sq(image_error)/cert['alpha_squared']+norm_sq(hidden)
        if norm_sq(e)>cap: raise ArithmeticError('Candidate source certificate failed.')
        if norm_sq(add(v,a@candidate,Q(-1)))!=norm_sq(residual)+norm_sq(image_error):
            raise ArithmeticError('Least-squares Pythagorean identity failed.')
        result['candidate']={'source':candidate,'source_error_squared':norm_sq(e),
            'image_error_squared':norm_sq(image_error),'kernel_ambiguity_squared':norm_sq(hidden),
            'source_error_bound_squared':cap}
    return result


def run_document(doc:Mapping[str,Any])->dict[str,Any]:
    if not isinstance(doc,Mapping): raise ValueError('Input must be an object.')
    if type(doc.get('schema_version')) is not int or doc['schema_version']!=1 or doc.get('coefficient_domain')!='Q':
        raise ValueError('Expected schema_version=1 and coefficient_domain=Q.')
    n,g=dimension(doc['local_dimension']),dimension(doc['global_dimension'])
    a=Matrix.parse(doc['A'],g)
    if a.nrows!=n: raise ValueError('Declared local dimension mismatch.')
    if not isinstance(doc['local_vector'],list) or len(doc['local_vector'])!=n:
        raise ValueError('Local vector length mismatch.')
    v=Matrix.parse([[x] for x in doc['local_vector']],1)
    alpha=rational(doc['alpha_squared']) if 'alpha_squared' in doc else None
    cert=construct(a,alpha)
    candidate=None
    if 'candidate_source' in doc:
        if not isinstance(doc['candidate_source'],list) or len(doc['candidate_source'])!=g:
            raise ValueError('Candidate source length mismatch.')
        candidate=Matrix.parse([[x] for x in doc['candidate_source']],1)
    result={'schema_version':1,'coefficient_domain':'Q','certificate':cert,
            'evaluation':evaluate(cert,v,candidate)}
    if 'delta' in doc:
        w=dimension(doc['residual_dimension']);d=Matrix.parse(doc['delta'],n)
        if d.nrows!=w: raise ValueError('Declared residual dimension mismatch.')
        sigma=rational(doc['sigma_squared']) if 'sigma_squared' in doc else None
        lc=local_construct(a,d,sigma); le=local_evaluate(lc,v)
        result['local_globalization']={'sigma_squared':lc['sigma_squared'],
            'obstruction':le['obstruction'],'inconsistency':le['inconsistency'],
            'error_squared':le['error_squared'],'bound_squared':le['bound_squared']}
    result['trust_boundary']='Exact rational known matrices and Euclidean metrics. Tested Python, not formally verified or extracted Lean. alpha conditions A; sigma conditions delta.'
    return json_value(result)


def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.input.stat().st_size>1_000_000: raise ValueError('Input exceeds 1 MB.')
        out=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(out,indent=2)+'\n')
        print('PASS exact minimum-norm source certificate:',args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError) as exc:
        ap.exit(2,'ERROR: '+str(exc)+'\n')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Exact rational Tikhonov reconstruction for KNOWN Euclidean matrix models.

The mathematical formulas are proved separately in Lean. This parser, elimination,
and PSD checker are tested Python, not extracted/formally verified code. Dimensions
are capped at 16, JSON at 1 MB, rational coefficient strings at 256 characters.
"""
from __future__ import annotations
import argparse, json, re
from fractions import Fraction as Q
from pathlib import Path
from typing import Any, Mapping
from observable_model import Matrix
from hilbert_certificate import (dimension,transpose,add,scale,inverse,norm_sq,
    positive_semidefinite,kernel_basis,projector_from_basis,json_value,
    construct as globalization_construct,evaluate as globalization_evaluate)
from reconstruction_certificate import construct as pseudoinverse_construct


def coefficient(x: Any) -> Q:
    if isinstance(x,bool) or not isinstance(x,(int,str,Q)):
        raise ValueError('Coefficients must be exact integers or rational strings.')
    if isinstance(x,str) and (len(x)>256 or re.fullmatch(r'[+-]?\d+(?:/[+-]?\d+)?',x) is None):
        raise ValueError('Invalid or oversized rational coefficient.')
    try: q=Q(x)
    except (ValueError,ZeroDivisionError) as e: raise ValueError('Invalid rational coefficient.') from e
    if max(q.numerator.bit_length(),q.denominator.bit_length())>2048:
        raise ValueError('Coefficient exceeds 2048-bit limit.')
    return q


def matrix(rows: Any,ncols:int)->Matrix:
    if not isinstance(rows,list) or any(not isinstance(row,list) for row in rows):
        raise ValueError('Expected a list of matrix rows.')
    return Matrix(tuple(tuple(coefficient(x) for x in row) for row in rows),ncols)


def vector(xs: Any,n:int)->Matrix:
    if not isinstance(xs,list) or len(xs)!=n: raise ValueError('Vector dimension mismatch.')
    return matrix([[x] for x in xs],1)


def validate(a:Matrix,lam:Q,r:Matrix,b:Matrix)->dict[str,Any]:
    dimension(a.nrows); dimension(a.ncols); lam=coefficient(lam)
    if lam<=0: raise ValueError('lambda must be strictly positive.')
    if (r.nrows,r.ncols)!=(a.ncols,a.ncols) or (b.nrows,b.ncols)!=(a.ncols,a.nrows):
        raise ValueError('Inverse or recovery dimensions are incompatible.')
    at=transpose(a);n=add(at@a,scale(Matrix.eye(a.ncols),lam))
    checks={'normal_left_inverse':n@r==Matrix.eye(a.ncols),
        'normal_right_inverse':r@n==Matrix.eye(a.ncols),
        'recovery_definition':b==r@at,'inverse_symmetric':r==transpose(r),
        'normal_equation':n@b==at}
    if not all(checks.values()): raise ValueError('Tikhonov identities failed: '+str(checks))
    sharp=add(Matrix.eye(a.nrows),scale(transpose(b)@b,4*lam),Q(-1))
    if not positive_semidefinite(sharp): raise ValueError('Sharp whole-map noise certificate failed.')
    return {'A':a,'lambda':lam,'normal':n,'inverse':r,'recovery':b,
        'identity_checks':checks,'sharp_noise_psd_witness':sharp}


def construct(a:Matrix,lam:Q)->dict[str,Any]:
    dimension(a.nrows);dimension(a.ncols);lam=coefficient(lam)
    if lam<=0: raise ValueError('lambda must be strictly positive.')
    n=add(transpose(a)@a,scale(Matrix.eye(a.ncols),lam));r=inverse(n)
    return validate(a,lam,r,r@transpose(a))


def objective(a:Matrix,lam:Q,v:Matrix,x:Matrix)->Q:
    return norm_sq(add(a@x,v,Q(-1)))+lam*norm_sq(x)


def evaluate(c:Mapping[str,Any],v:Matrix,candidate:Matrix|None=None,
             source:Matrix|None=None,noise:Matrix|None=None)->dict[str,Any]:
    a,lam,n,r,b=(c[k] for k in ('A','lambda','normal','inverse','recovery'))
    if v.nrows!=a.nrows or v.ncols!=1: raise ValueError('Data vector dimension mismatch.')
    x=b@v;av=a@x;res=add(av,v,Q(-1));energy=norm_sq(av)+lam*norm_sq(x)
    pairing=(transpose(v)@av).rows[0][0]
    if energy!=pairing: raise ArithmeticError('Solution energy identity failed.')
    if 4*lam*norm_sq(x)>norm_sq(v): raise ArithmeticError('Sharp data bound failed.')
    result={'regularized_source':x,'fitted_data':av,'residual':res,
        'objective':objective(a,lam,v,x),'source_norm_squared':norm_sq(x),
        'data_noise_bound_squared':norm_sq(v)/(4*lam),'energy_identity_value':energy}
    if candidate is not None:
        if candidate.nrows!=a.ncols or candidate.ncols!=1: raise ValueError('Candidate dimension mismatch.')
        d=add(candidate,x,Q(-1));normal_res=add(n@candidate,transpose(a)@v,Q(-1))
        gap=objective(a,lam,v,candidate)-result['objective']
        if gap!=norm_sq(a@d)+lam*norm_sq(d): raise ArithmeticError('Objective gap failed.')
        if norm_sq(d)>norm_sq(normal_res)/(lam*lam): raise ArithmeticError('Solver residual bound failed.')
        result['candidate']={'source':candidate,'objective_gap':gap,
            'source_error_squared':norm_sq(d),'normal_residual':normal_res,
            'solver_error_bound_squared':norm_sq(normal_res)/(lam*lam)}
    if (source is None)!=(noise is None): raise ValueError('Source and noise must be supplied together.')
    if source is not None:
        if source.nrows!=a.ncols or source.ncols!=1 or noise.nrows!=a.nrows or noise.ncols!=1:
            raise ValueError('Source/noise dimension mismatch.')
        pk=projector_from_basis(kernel_basis(a));ident=add(source,pk@source,Q(-1))
        bias=scale(r@ident,-lam);prop=b@noise
        err=add(b@add(a@source,noise),source,Q(-1))
        if norm_sq(err)!=norm_sq(add(bias,prop))+norm_sq(pk@source):
            raise ArithmeticError('Identifiable error/kernel split failed.')
        result['source_noise']={'identifiable_bias':bias,'propagated_noise':prop,
            'unrecoverable_kernel':pk@source,'error_squared':norm_sq(err),
            'identifiable_error_squared':norm_sq(add(bias,prop)),
            'kernel_ambiguity_squared':norm_sq(pk@source)}
    return result


def run_document(doc:Mapping[str,Any])->dict[str,Any]:
    if not isinstance(doc,Mapping): raise ValueError('Input must be an object.')
    allowed={'schema_version','coefficient_domain','global_dimension','local_dimension','A','lambda',
        'local_vector','candidate_source','true_source','noise','delta','residual_dimension','sigma_squared'}
    if set(doc)-allowed: raise ValueError('Unknown input field(s): '+repr(sorted(set(doc)-allowed)))
    if type(doc.get('schema_version')) is not int or doc['schema_version']!=1 or doc.get('coefficient_domain')!='Q':
        raise ValueError('Expected schema_version=1 and coefficient_domain=Q.')
    n,g=dimension(doc['local_dimension']),dimension(doc['global_dimension'])
    a=matrix(doc['A'],g)
    if a.nrows!=n: raise ValueError('Declared local dimension mismatch.')
    lam=coefficient(doc['lambda']);v=vector(doc['local_vector'],n);c=construct(a,lam)
    candidate=vector(doc['candidate_source'],g) if 'candidate_source' in doc else None
    source=vector(doc['true_source'],g) if 'true_source' in doc else None
    noise=vector(doc['noise'],n) if 'noise' in doc else None
    result={'schema_version':1,'coefficient_domain':'Q','certificate':c,
        'evaluation':evaluate(c,v,candidate,source,noise)}
    if 'delta' in doc:
        w=dimension(doc['residual_dimension']);d=matrix(doc['delta'],n)
        if d.nrows!=w: raise ValueError('Declared residual dimension mismatch.')
        sigma=coefficient(doc['sigma_squared']) if 'sigma_squared' in doc else None
        lc=globalization_construct(a,d,sigma);le=globalization_evaluate(lc,v)
        pinv=pseudoinverse_construct(a)['recovery'];dag=pinv@v;x=c['recovery']@v
        bias_sq=norm_sq(a@add(x,dag,Q(-1)))
        fit=norm_sq(add(v,a@x,Q(-1)))
        if fit!=norm_sq(le['obstruction'])+norm_sq(le['inconsistency'])+bias_sq:
            raise ArithmeticError('Globalization split failed.')
        result['globalization']={'obstruction_squared':norm_sq(le['obstruction']),
            'inconsistency_squared':norm_sq(le['inconsistency']),
            'regularization_image_bias_squared':bias_sq,'total_fit_error_squared':fit,
            'unregularized_minimum_norm_source':dag}
    result['trust_boundary']='Known rational Euclidean matrices. Exact finite tests; Python and parser not formally verified. lambda > 0 is required; kernel ambiguity and globalization obstruction remain.'
    return json_value(result)


def main()->None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    try:
        if args.input.stat().st_size>1_000_000: raise ValueError('Input exceeds 1 MB.')
        out=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(out,indent=2)+'\n')
        print('PASS exact Tikhonov certificate:',args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError) as e:
        p.exit(2,'ERROR: '+str(e)+'\n')
if __name__=='__main__':main()

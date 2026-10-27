#!/usr/bin/env python3
"""Exact-rational calibration-to-operator-allowance checker.

The executable does not know the true operator A.  It validates a calibration
synthesis/reconstruction pair, computes the model's calibration fit, and combines
that with an externally justified calibration-truth allowance.  Matrix bounds use
the entrywise l1 norm as a conservative finite-dimensional surrogate; the generic
Lean theorem is stated in the native operator norm.
"""
from __future__ import annotations
import argparse, json
from fractions import Fraction as Q
from pathlib import Path
from typing import Any, Mapping
from observable_model import Matrix, rational


def add(a:Matrix,b:Matrix,s:Q=Q(1))->Matrix:
    if a.nrows!=b.nrows or a.ncols!=b.ncols: raise ValueError('Matrix dimension mismatch.')
    return Matrix(tuple(tuple(x+s*y for x,y in zip(ra,rb)) for ra,rb in zip(a.rows,b.rows)),a.ncols)

def scale(a:Matrix,s:Q)->Matrix:
    return Matrix(tuple(tuple(s*x for x in r) for r in a.rows),a.ncols)

def l1(a:Matrix)->Q:
    return sum((abs(x) for r in a.rows for x in r),Q(0))

def nonneg(x:Any,name:str)->Q:
    q=rational(x)
    if q<0: raise ValueError(name+' must be nonnegative.')
    return q

def parse_matrix(value:Any,m:int,n:int,name:str)->Matrix:
    if not isinstance(value,list) or len(value)!=m: raise ValueError(name+' row count mismatch.')
    if any(not isinstance(r,list) for r in value): raise ValueError(name+' must be a matrix.')
    return Matrix.parse(value,n)

def run_document(doc:Mapping[str,Any])->dict[str,Any]:
    if not isinstance(doc,Mapping): raise ValueError('Input must be a JSON object.')
    allowed={'schema_version','coefficient_domain','source_dimension','calibration_dimension','data_dimension',
             'synthesis','analysis','measured_outputs','model_operator','calibration_truth_allowance'}
    if set(doc)-allowed: raise ValueError('Unknown fields: '+repr(sorted(set(doc)-allowed)))
    if doc.get('schema_version')!=1 or doc.get('coefficient_domain')!='Q': raise ValueError('Unsupported schema.')
    g=int(doc['source_dimension']);k=int(doc['calibration_dimension']);m=int(doc['data_dimension'])
    if min(g,k,m)<0 or max(g,k,m)>16: raise ValueError('Dimensions must lie in 0..16.')
    U=parse_matrix(doc['synthesis'],g,k,'synthesis')
    R=parse_matrix(doc['analysis'],k,g,'analysis')
    Y=parse_matrix(doc['measured_outputs'],m,k,'measured_outputs')
    C=parse_matrix(doc['model_operator'],m,g,'model_operator')
    eta=nonneg(doc['calibration_truth_allowance'],'calibration truth allowance')
    defect=add(Matrix.eye(g),U@R,Q(-1))
    rho=l1(defect)
    if rho>=1: raise ValueError('Calibration reconstruction bound is not < 1; no certificate.')
    fit=l1(add(Y,C@U,Q(-1)))
    rnorm=l1(R)
    delta=(eta+fit)*rnorm/(1-rho)
    return {'schema_version':1,'coefficient_domain':'Q','status':'calibration_operator_allowance_generated',
            'source_dimension':g,'calibration_dimension':k,'data_dimension':m,
            'reconstruction_defect_l1_bound':str(rho),'analysis_l1_bound':str(rnorm),
            'model_calibration_fit_l1_bound':str(fit),'calibration_truth_allowance':str(eta),
            'generated_operator_error_allowance':str(delta),
            'exact_split':rho==0,
            'externally_required_not_checked':[
              'The supplied calibration_truth_allowance bounds the true calibration operator error.',
              'The same source/data norms and calibration interpretation used to justify that allowance apply to the intended problem.'
            ],
            'trust_boundary':'Exact rational finite-matrix checker using conservative entrywise-l1 bounds. Python/parsing are tested, not Lean-verified. The generic Lean theorem uses native operator norms.'}

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    try:
        if args.input.stat().st_size>1_000_000: raise ValueError('Input exceeds 1 MB.')
        out=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS calibration certificate:',args.output)
    except (ValueError,TypeError,KeyError,ArithmeticError,OSError) as e:
        ap.exit(2,'ERROR: '+str(e)+'\n')
if __name__=='__main__': main()

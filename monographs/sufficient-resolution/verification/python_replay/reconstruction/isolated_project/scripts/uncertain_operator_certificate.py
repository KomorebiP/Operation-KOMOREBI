#!/usr/bin/env python3
"""Check squared discrepancy certificates using an approximate rational operator.

The checker receives C, not the unknown true A or source. It checks the computed
model's algebra and effective-noise margins. The asserted true operator/noise/source
bounds remain EXTERNAL. No inverse, numerical parameter search, or floating norm.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Mapping
from inexact_discrepancy_certificate import run_document as check_inexact, nonnegative
from tikhonov_certificate import coefficient


def run_document(doc: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(doc, Mapping):
        raise ValueError('Input must be a JSON object.')
    allowed = {'schema_version','coefficient_domain','global_dimension','local_dimension',
        'model_operator','local_vector','candidate_source','data_noise_allowance',
        'operator_error_allowance','source_norm_bound','upper_multiplier','source_tolerance',
        'branch','measured_residual','measurement_error','lambda','normal_envelope',
        'image_tolerance','normal_measurement'}
    if set(doc)-allowed:
        raise ValueError('Unknown fields: '+repr(sorted(set(doc)-allowed)))
    eta=nonnegative(doc['data_noise_allowance'],'data noise allowance')
    delta=nonnegative(doc['operator_error_allowance'],'operator error allowance')
    M=nonnegative(doc['source_norm_bound'],'source norm bound')
    effective=coefficient(eta+delta*M)
    if effective<=0:
        raise ValueError('Effective discrepancy allowance must be positive.')
    derived={key:value for key,value in doc.items() if key not in
        {'model_operator','data_noise_allowance','operator_error_allowance','source_norm_bound'}}
    derived['A']=doc['model_operator']
    derived['noise_allowance']=str(effective)
    checked=check_inexact(derived)
    kappa=coefficient(doc['source_tolerance'])
    return {'schema_version':1,'coefficient_domain':'Q',
        'status':'certificate_checks_passed_external_bounds_required',
        'data_noise_allowance':str(eta),'operator_error_allowance':str(delta),
        'source_norm_bound':str(M),'effective_noise_allowance':str(effective),
        'conditional_source_norm_upper_bound':str(M+kappa),
        'computed_model_certificate':checked['certificate'],
        'externally_required_not_checked':[
            'A fixed bounded true operator A between the same real Hilbert spaces.',
            '||C-A|| <= operator_error_allowance in the whole operator norm.',
            '||A g-v|| <= data_noise_allowance for the intended true source.',
            '||P_(ker A)^perp g|| <= source_norm_bound.',
            'For convergence: true data and operator allowances and source tolerance tend to zero, with fixed M and upper multiplier.'],
        'trust_boundary':'Exact rational Euclidean model checks only. A and the true source are not inputs. Python arithmetic/parsing are tested, not formally verified. The Lean theorem supplies the conditional mathematical guarantee.'}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    try:
        if args.input.stat().st_size>1_000_000:
            raise ValueError('Input exceeds 1 MB.')
        result=run_document(json.loads(args.input.read_text()))
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print('PASS model-side checks; external operator/noise bounds remain required:',args.output)
    except (ValueError,TypeError,KeyError,OSError,ArithmeticError) as e:
        ap.exit(2,'ERROR: '+str(e)+'\n')
if __name__=='__main__':main()

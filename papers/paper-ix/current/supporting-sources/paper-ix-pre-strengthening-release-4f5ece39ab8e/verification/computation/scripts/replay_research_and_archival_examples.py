#!/usr/bin/env python3
"""Replay preserved exact research programs safely; check two archival examples.

The kernel checker writes beside its own source, so run a byte-identical copy
inside the fresh runner output directory. No archived source or result changes.
Historical research labels remain checkpoint labels, not current proof status.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path
import subprocess
import sys

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
b=args.source_root;out=args.output_dir

period=b/'research/least_periods/check_period_candidates.py'
kernel=b/'research/mahler_kernel/check_kernel_formulas.py'
copied=out/'check_kernel_formulas.py'
copied.write_bytes(kernel.read_bytes())
commands=[
 [sys.executable,str(period),'--output',str(out/'period_candidates_results.json')],
 [sys.executable,str(copied)],
]
for command in commands:
    r=subprocess.run(command,capture_output=True,text=True,check=True,timeout=30)
    if r.stderr:raise AssertionError('Unexpected stderr')
    print(r.stdout.strip())

period_result=json.loads((out/'period_candidates_results.json').read_text())
kernel_result=json.loads((out/'kernel_check_results.json').read_text())
assert period_result['direct_difference_cases']==1088
assert kernel_result['binary_address_formula']['checked_cases']==861
assert kernel_result['top_edge']['checked_cases']==41
assert len(kernel_result['cancellation_examples'])==4
assert copied.read_bytes()==kernel.read_bytes()
assert (out/'period_candidates_results.json').read_bytes()==(b/'research/least_periods/period_candidates_results.json').read_bytes()
assert (out/'kernel_check_results.json').read_bytes()==(b/'research/mahler_kernel/kernel_check_results.json').read_bytes()

# The source's positive exponential section has binomial signs from sech.
e=[Fraction(1)]
for n in range(1,10):e.append(-sum(comb(2*n,2*q)*e[q] for q in range(n)))
residues=[int(v)%7 for v in e[1:]]
printed=[1,6,4]
actual=residues[:3]
assert actual==[6,5,2] and residues==actual*3 and actual!=printed
controls=[{'name':'compressed mod-seven printed positive-section values','claim_location':'ex:compressed_mod_seven','witness':{'modulus':7,'source_recurrence':'sum_q binom(2n,2q)e_q=delta_n0','printed_prefix':printed,'actual_positive_row_prefix':actual,'actual_rows1_through9':residues,'period3_in_tested_rows':True},'status':'REJECTED_PRINTED_PREFIX; PERIOD_THREE_RETAINED'}]

S31=sum((-1)**a*(2*a+1) for a in range(3))
dyadic_odd=0
even_kernel_transported_odd=0
assert S31==3 and S31!=even_kernel_transported_odd
controls.append({'name':'local source change must restrict to even subsequences','claim_location':'cor:local_source_change','witness':{'odd_source_length':3,'dyadic_source_length':2,'odd_degree':1,'S_1_3':S31,'dyadic_odd_coefficient':dyadic_odd,'even_kernel_transport_odd_coefficient':even_kernel_transported_odd},'status':'REJECTED_FULL_SOURCE_IDENTITY; EVEN_SUBSEQUENCE_IDENTITY_UNAFFECTED'})

report={'status':'PASS','coefficient_domain':'exact int and Fraction','historical_unchanged_replays':{'candidate_packet_displacement_cases':1088,'kernel_binary_formula_cases':861,'kernel_top_edges':41,'kernel_cancellation_examples':4,'result_bytes_match_preserved_outputs':True,'source_copy_is_byte_identical':True,'kernel_copy_sha256':hashlib.sha256(copied.read_bytes()).hexdigest(),'actual_child_argv':commands},'negative_controls_rejected':len(controls),'controls':controls,'scope_note':'The historical programs retain their original unformalized-candidate status wording. The later preserved Lean evidence, not this replay, determines final universal proof status. Both example corrections concern recovered historical exposition; consolidated and accepted Lean core are not refuted.','non_claims':['No universal proof by finite test','No fresh Lean compilation','No general exact Mahler-kernel valuation formula','No full-source chart identity']}
(out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: unchanged research result bytes plus two rejected archival examples')

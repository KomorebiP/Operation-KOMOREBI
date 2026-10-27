#!/usr/bin/env python3
"""Concrete exact controls for omitted hypotheses in the recovered Annals text.

These concern the broader recovered historical exposition. They do not refute
the consolidated manuscript's explicitly scoped theorems or any accepted Lean
declaration. No historical source is changed.
"""
import argparse
from fractions import Fraction
import json
from math import comb
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()

def coeff(f,k):return sum((-1)**(k-j)*comb(k,j)*f(j) for j in range(k+1))

controls=[]
# Scalar matrices are 1x1 exact matrices. At L=0, p^L B is not p-divisible.
power_difference=2**3-1
assert power_difference%3==1
controls.append({'name':'matrix amplification requires positive filtration depth','claim_location':'lem:matrix_power_amplification','witness':{'p':3,'L':0,'X':2,'B':1,'X_equals_1_plus_pL_B':True,'X_to_p_minus_1':power_difference,'residue_mod_p':1},'status':'REJECTED_INVALID_DEPTH_ZERO_EXTENSION'})

# A state with a denominator can cancel the filtration gained by C-I.
C=4;initial=Fraction(1,3);observable=1
difference=observable*(C*initial-initial)
assert C%3==1 and difference==1 and difference.numerator%3!=0
controls.append({'name':'matrix-state precision requires integral initial state and observable','claim_location':'thm:matrix_carmichael_mahler / thm:finite_adelic_transfer','witness':{'p':3,'L':1,'C':C,'initial_state':str(initial),'observable':observable,'unit_step_difference':str(difference),'required_depth':1,'actual_v3':0},'status':'REJECTED_UNTYPED_RATIONAL_INITIAL_STATE'})

# The binomial-kernel sparsification congruence cannot be multiplied by an
# arbitrary rational Mahler coefficient while retaining the modulus.
f=lambda x:Fraction(x,2)
g=lambda q:f(2*q)
c1=coeff(f,1);c2=coeff(f,2);d1=coeff(g,1)
assert c1==Fraction(1,2) and c2==0 and d1==1 and (d1-c2).numerator%2==1
controls.append({'name':'prime-power sparsification coefficient corollary requires integral Mahler coefficients','claim_location':'thm:prime_power_sparsification / thm:mahler_transfer','witness':{'p':2,'M':2,'s':0,'k':1,'f':'f(x)=x/2','g':'g(q)=f(2q)=q','c1':str(c1),'c2':str(c2),'d1':str(d1),'d1_minus_c2_mod2':1},'status':'REJECTED_UNTYPED_RATIONAL_MAHLER_COEFFICIENT'})

report={'status':'PASS','scope':'Three exact counterexamples to insufficient hypotheses in recovered historical Annals exposition; consolidated and accepted Lean core are not thereby refuted.','coefficient_domain':'exact int and fractions.Fraction','negative_controls_rejected':len(controls),'controls':controls,'historical_source':'source/consolidated/PRSC_IX_Consolidated_Manuscript/strengthening/recovery/PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex','non_claims':['No modification or exhaustive audit of historical proofs','No failure of the scoped consolidated theorem statements','No new Lean compilation']}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('PASS: three concrete recovered-hypothesis controls rejected')

#!/usr/bin/env python3
"""Freeze the independent raw-source audit after source and exposition review.

This script records reviewed revisions. It does not prove their mathematics.
A separate completed fresh Lean gate must be reconciled afterwards.
"""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p): return {'path':str(p.relative_to(WORK)), 'sha256':sha(p)}

new=['PolynomialAnalyticEvaluation','PolynomialAnalyticInverse','PolynomialAnalyticBlocks',
     'PolynomialAnalyticImplicit','PolynomialAnalyticSelection','PolynomialRegularityIntegral']
sources=[ROOT/'formalization'/f'{n}.lean' for n in new]
sources += [ROOT/'formalization'/f'{n}.lean' for n in
    ['PolynomialBlockInverse','PolynomialJointSystem','PolynomialParameterSystem','PolynomialWeightedInverse']]
sources += [ROOT/'controls/PolynomialRegularityControls.lean',
            ROOT/'controls/InvalidRegularityDerivativeSign.lean',
            ROOT/'contracts/PolynomialRegularityContracts.lean']
reviewed=[entry(p) for p in sources]
target=json.loads((ROOT/'TARGET_CONTRACT.json').read_text())
exposition={**entry(ROOT/'ANALYTIC_REGULARITY.md'),'verdict':'PASS',
 'scope':'Full exposition read against six new mathematical sources: actual derivative bridge, local analytic graph, strict derivative, continuous-selection transfer, integral coefficient/center inclusion, pointwise inverse assumptions, all-prime/zero-dimension and ambient-field scope. Inline delimiters repaired without mathematical change.'}
full={
 'audit_kind':'independent raw mathematical proof-source review',
 'reviewer':'/root/regularity_audit, separate from proof builders',
 'reviewed_at':datetime.now(timezone.utc).isoformat(),
 'verdict':'proved as written',
 'target_checkpoint':target['checkpoint_id'],
 'normalized_claim':target['target'],
 'authoritative_declaration':'Komorebi.PolynomialAnalyticImplicit.exists_analytic_implicit',
 'integral_declaration':'Komorebi.PolynomialRegularityIntegral.exists_analytic_integral_implicit',
 'selection_declarations':['Komorebi.PolynomialAnalyticSelection.continuous_selection_regularity',
   'Komorebi.PolynomialAnalyticSelection.continuous_selection_analyticOnNhd'],
 'exact_remaining_mathematical_gap':None,
 'route_audit':{'path':'audit/ROUTE_AUDIT.md','sha256':sha(ROOT/'audit/ROUTE_AUDIT.md')},
 'critical_implications':[
  'Actual evaluated formal partial derivatives are the strict derivative by polynomial induction and the finite pi rule.',
  'Actual augmented polynomial (F,T) is analytic and has derivative [[J,K],[0,I]].',
  'Both inverse block products prove an actual continuous linear equivalence with inverse [[J^-1,-J^-1 K],[0,I]].',
  'The same strict local inverse is analytic by the generic normed-field inverse power-series theorem.',
  'Projection of the inverse at (0,t) constructs the solution map and the chain rule gives -J^-1 K.',
  'An open product rectangle in the inverse source and open intersections produce neighborhoods containing both centers and both exact graph implications.',
  'Analyticity at every point implies differentiability throughout the parameter neighborhood.',
  'The original integral coefficients and center map into Q_p compatibly with evaluation and pderiv; the final graph evaluates the original polynomials via eval2.',
  'Continuity and the local graph identify any supplied continuous local root selection germ; regularity and actual derivative transfer without an analytic premise.'
 ],
 'obligations':{k:'passed' for k in ['actual_polynomial_data','actual_strict_derivative',
   'analytic_power_series_inverse','actual_block_inverse','constructed_solution_map',
   'open_neighborhoods','both_graph_directions','strict_derivative_sign_and_order',
   'differentiability_on_parameter_neighborhood','integral_coefficient_center_specialization',
   'continuous_selection_germ_comparison','expanded_statement_contracts','dyadic_prime_and_zero_dimensions']},
 'reviewed_sources':reviewed,
 'source_review_scope':'Six new mathematical modules, five expanded theorem contracts, new positive control and negative sign control, and exposition read in full. Inherited PolynomialBlockInverse and PolynomialJointSystem read in full. Relevant split/evaluated-Jacobian definitions rechecked in PolynomialParameterSystem and PolynomialWeightedInverse, not their entire transitive developments. Earlier Paper IX arithmetic is not independently re-audited.',
 'local_mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
 'local_source_record':{'path':'audit/LOCAL_SOURCE_CHECK.json','sha256':sha(ROOT/'audit/LOCAL_SOURCE_CHECK.json')},
 'external_paper_input':None,
 'novelty_claim':False,
 'scope_limits':['Local ambient-field analytic neighborhoods; no asserted global branch or new uniform explicit radius.',
  'Square solved block invertible over Q_p; no rationally rank-deficient singular persistence theorem.',
  'Integral specialization is ambient Q_p-valued, not a theorem treating Z_p as a Q_p vector space.',
  'No separately formalized identity with each historical subtype-valued chart.',
  'No native presentation invariance or global/completed descent.'],
 'control_examples':[
  {'data':'F(Y,T)=Y+T','conclusion':'Exact branch -T, actual J=K=1, strict derivative -I; +I rejected in characteristic zero, including Q_2.'},
  {'data':'F(Y,T)=Y+Y^2+T at (0,0)','conclusion':'Actual nonlinear full theorem invocation gives analytic local root graph and strict derivative -I.'},
  {'data':'e=0 or k=0','conclusion':'Universal proof includes empty coordinates; generic inverse construction explicitly handles subsingleton domains. This boundary review is structural, not a separately enumerated finite experiment.'}],
 'observed_development_distinctions':[
  'Coercion/simplification/finite-index elaboration fixes are recorded in dev; they do not change the target.',
  'A stale intermediate Implicit compiled dependency caused one selection compilation failure, followed by PASS with unchanged source and final dependency.',
  'The initial integral statement contract used a square-only mapMatrix API on rectangular K. Its expression was corrected to the intended entrywise inclusion; the target remained rectangular.',
  'Malformed inline math delimiters in exposition were repaired without changing mathematical tokens.',
  'Missing raw development outputs were not reconstructed as invented logs.'],
 'exposition_review':exposition
}
full['obligations'].update({'fresh_kernel_evidence':'separately reconciled after gate',
 'global_analyticity':'out of scope','uniform_radius':'out of scope',
 'rank_deficient_persistence':'out of scope','native_invariance_descent':'out of scope'})
fullpath=ROOT/'audit/regularity_source_audit.json'
fullpath.write_text(json.dumps(full,indent=2)+'\n')
review={'verdict':full['verdict'],'role':full['audit_kind']+' by a subagent separate from proof builders',
 'target_checkpoint':target['checkpoint_id'],'reviewed_project_sources':reviewed,
 'exposition_review':exposition,'target_contract':entry(ROOT/'TARGET_CONTRACT.json'),
 'full_record':'audit/regularity_source_audit.json','full_record_sha256':sha(fullpath),
 'scope':full['source_review_scope'],'remaining_target_gap':None,
 'fresh_release_gate_reconciliation':{'status':'PENDING'}}
(ROOT/'audit/REVIEWED_SOURCES.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'verdict':review['verdict'],'sources':len(reviewed),
 'review_sha256':sha(ROOT/'audit/REVIEWED_SOURCES.json'),'full_record_sha256':sha(fullpath)},indent=2))

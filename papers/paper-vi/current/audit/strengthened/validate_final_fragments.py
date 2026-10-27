"""Pin the reviewed final artifacts and check structural assertions.

The mathematical review is recorded in FINAL_FRAGMENT_VALIDATION.txt.
Substring checks and hashes here are preservation checks, not theorem proving.
"""
from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
TRAD=ROOT/'traditional'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# These are the exact revisions actually read in the final review. Updating
# SOURCE_FREEZE.json alone cannot authorize a new mathematical review verdict.
REVIEWED={
 'Paper_VI_Traditional_Final.tex':'8c802c7a9e10fd660d4cd372555b9b64b364c6bceb921426068ce5cdfce315f2',
 'extension_corrected.tex':'5e249e1057f934187ebf3d5e22ef7a97ce6c5a0f0b1ca575ae2b207dbf0fbf99',
 'earlier_corrected.tex':'be7183646d816070f707f7c6abd9e2a080ced378874660280c98f4851f1e1198',
 'migration_corrected.tex':'0aa6cb240b456ba6ebcfb8b1a38ef2e484d3ddcc3b423be83403728d14a9178b',
 'EARLIER_RESULT_DESTINATIONS.json':'0ff054c5860bebc5c36e4fd62591c033c2c1f19d89a8a9e7387f451e8011b4d7',
}
for name,wanted in REVIEWED.items():
    assert sha(TRAD/name)==wanted, f'Explicit mathematical re-review required: {name}'

freeze=json.loads((TRAD/'SOURCE_FREEZE.json').read_text())
for name,wanted in freeze['source_sha256'].items():
    assert sha(TRAD/name)==wanted, f'Frozen source changed: {name}'

text=(TRAD/'Paper_VI_Traditional_Final.tex').read_text()
cross=json.loads((TRAD/'EARLIER_RESULT_DESTINATIONS.json').read_text())
orig=json.loads((OUT/'ANNALS_SOURCE_INVENTORY.json').read_text())
results={r['label']:r for r in orig['records'] if r['kind'] in ('theorem','lemma','proposition','corollary')}
assert len(results)==63 and set(results)==set(cross)
retained=[k for k,v in cross.items() if v['status']=='complete-statement-and-proof-retained-in-Part-III']
mapped=[k for k in cross if k not in retained]
assert len(retained)==24 and len(mapped)==39
for key,item in cross.items():
    assert text.count('\\label{'+item['final_label']+'}')==1, key

check_strings={
 'F1_admissible_common_contour':'pairwise disjoint bounded Jordan domains',
 'F2_positive_decay_rate':r'\gamma>0',
 'F3_zero_hidden_space':r'If \(X_Q=\{0\}\)',
 'F3_bounded_growth_argument':r'\exp(\norm B+\max(0,-\beta))',
 'F4_finite_hidden_dimension':r'd=\dim X_Q<\infty',
 'F5_nontransient_killing':'killed, possibly nontransient chain',
 'F6_eventual_cause_stability':r'If the spectrum of \(A\) lies in the open left half-plane, the eventual probability',
 'F7_linear_connecting_maps':'sequence of Banach spaces and bounded linear maps',
 'F8_Laplace_kernel_class':'continuous kernels of exponential order',
 'F9_auxiliary_dimensions':r'\lambda_j I_{d_j}',
 'F10_continuous_mild_solutions':r'x,\widetilde x\in C([0,T],X)',
 'F10_integrable_forcing':r'g\in L^1((0,T),X)',
 'length_zero_paths':'length-zero path to itself',
 'one_phase_positive_rate':r'one-phase model has $\lambda>0$',
 'general_C0_scope':'The generator need not be bounded.',
 'strong_integral_scope':'take its Bochner integral in $X$',
 'sharper_bounded_compression':r'MT\delta\e^{(a+k)T}',
 'explicit_fractional_mode_coefficient':r'\frac{\alpha(4k^2)^{\alpha-1}(k\pi)^4}{12}h^2',
 'alternative_generator_recovery':r'forces $B=A_{PP}$ on the retained space',
 'complex_survival_Laplace':r'complex $s$ with $\operatorname{Re}s\geq0$',
 'sufficiency_scope_distinction':r"Part I's mass-only Bayesian commutation criterion assumes at least two coarse blocks",
 'migration_fixed_complex_branch':r'for complex $r$',
 'migration_accessible_primary_source':r'TaylorBanachAlgebras',
}
checks=[]
for name,needle in check_strings.items():
    assert needle in text, name
    checks.append({'id':name,'structural_presence':'passed','manual_scope_review':'passed'})

destinations={
 'thm:continuous_lumping_defect':'extended:thm:duhamel_defect',
 'thm:finite_feynman_kac':'extended:thm:continuous_feynman_kac',
 'thm:bayesian_sufficiency':'core:record:021',
}
for key,target in destinations.items(): assert cross[key]['final_label']==target

paths=[
 'traditional/Paper_VI_Traditional_Final.tex',
 'traditional/extension_corrected.tex','traditional/earlier_corrected.tex','traditional/migration_corrected.tex',
 'traditional/source/strengthened.tex','traditional/source/earlier_annals.tex',
 'traditional/source/paper_iv_operator_substitution.tex','traditional/source/strengthened.bib','traditional/source/migration.bib',
 'traditional/EARLIER_RESULT_DESTINATIONS.json','traditional/SOURCE_FREEZE.json',
 'audit/strengthened/INITIAL_SOURCE_AUDIT.txt','audit/strengthened/CROSSWALK_SCOPE_REVIEW.txt',
 'audit/strengthened/STRENGTHENED_SOURCE_INVENTORY.json','audit/strengthened/ANNALS_SOURCE_INVENTORY.json',
 'audit/strengthened/FINAL_FRAGMENT_VALIDATION.txt','audit/strengthened/validate_final_fragments.py',
 'audit/core/MIGRATED_BANACH_SOURCE_CHECK.json',
]
pins={name:sha(ROOT/name) for name in paths}

special={
 'thm:packet_convolution':'Retained arbitrary-C0 scope; insert finite projector identity, with no differentiation.',
 'prop:packet_resolvent':'Retained growth-half-plane scope and explicit X-valued strong Bochner interpretation; Engel-Nagel II.1.10 authenticated.',
 'cor:fractional_low_mode_dispersion':'Retained exact all-discrete-mode coefficient and proof, with h=1/M and 1<=k<=M-1 setup.',
 'thm:memory_compression_stability':'Retained sharper bounded-generator exponential constant, with classical-solution and integrability setup.',
 'thm:continuous_lumping_defect':'Corrected destination is continuous Duhamel, specialized to column-stochastic l1 contractions.',
 'thm:finite_feynman_kac':'Corrected destination is continuous-time Feynman-Kac, including the original nonnegative-potential case.',
 'thm:bayesian_sufficiency':'Corrected destination is core mass-only criterion with at least two blocks and positive likelihoods.',
 'thm:exact_local_closure':'PartII finite hidden criterion plus PartIII derivative-at-zero sentence handles every alternative bounded generator.',
 'thm:survival_laplace_moments':'PartII stable moments and PartIII explicit complex Re(s)>=0 extension preserve full earlier scope.',
 'prop:conditional_variance':'Block-mean and weighted-norm definitions next to the destination expand to the earlier displayed within-block sum.',
 'prop:discrete_dirichlet_spectrum':'Sine eigenpairs displayed immediately before destination theorem; sine-addition verification preserves finite grid formula.',
 'thm:exact_memory_equation':'Full memory equation, hidden initial-state forcing, and variation-of-constants derivation precede the destination theorem.',
 'thm:fractional_refinement_bound':'PartII resolvent-defect/Balakrishnan derivation and core exact integral preserve formula and common-gap coefficient.',
}
rows=[]
for key,item in cross.items():
    source=results[key]
    rows.append({'source_label':key,'kind':source['kind'],'title':source['title'],
     'source_statement_sha256':source['statement_sha256'],'source_proof_sha256':source['proof_sha256'],
     'final_label':item['final_label'],'treatment':'full record retained' if key in retained else 'covered by statement or surrounding derivation',
     'semantic_scope_status':'passed','note':special.get(key,source.get('review_note') if key in retained else 'Compared hypotheses, conclusions, signs, finite/bounded setting, and constants; scope is represented at the destination or its declared surrounding setup.')})

report={
 'audit_date_utc':'2026-10-06','edition_date':'2026-10-05',
 'primary_verdict':'proved as written',
 'normalized_audit_claim':'The final corrected fragments implement the documented mathematical restrictions and preserve the mathematical scope of all 63 earlier result records, subject to the explicit classical inputs and qualifications in the written audit.',
 'scope':'Correction and semantic-preservation validation of strengthened branch, retained earlier results, and migrated operator fragment; not fresh kernel certification or full reference verification.',
 'source_sha256':pins,'source_freeze_matched':True,
 'strengthened_written_results_reviewed':84,'earlier_correspondence_rows':63,
 'earlier_full_results_retained':24,'earlier_mapped_results':39,'earlier_examples_retained':5,
 'correction_checks':checks,'crosswalk_rows':rows,
 'remaining_open_local_correction_findings':[],
 'imported_inputs_not_independently_authenticated_here':['General martingale convergence as phrased under usual hypotheses','Gaussian-L2 polynomial density/Hermite completeness','The exact cited second-edition stable-subordination theorem','Elementary beta/Gaussian scalar integration identities and Gronwall background'],
 'external_input_checked_by_companion_audit':'Migrated holomorphic Banach calculus; see pinned audit/core/MIGRATED_BANACH_SOURCE_CHECK.json',
 'new_formal_proof_or_Lean_build':False,
 'staleness_rule':'If any pinned source changes, this validation is stale until an explicit follow-up review records the new bytes. Do not silently refresh hashes.',
}
(OUT/'FINAL_FRAGMENT_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'passed','frozen_final_tex_sha256':pins['traditional/Paper_VI_Traditional_Final.tex'],'crosswalk_rows':63,'retained':24,'mapped':39,'correction_checks':len(checks)},indent=2))

#!/usr/bin/env python3
"""Summarize the already recorded finite evidence, without executing new gates."""
from pathlib import Path
import hashlib,json,platform,shutil
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(root))
core={n:here/('run_'+n+'_20261009') for n in ('original','corrected','constructed')}
guide={n:root/'editable/visual_guide/checks/runs'/('monograph-'+n) for n in ('original','extended','plates')}
o=load(core['original']/'results.json');c=load(core['corrected']/'results.json');b=load(core['constructed']/'results.json')
g=load(guide['original']/'EXACT_CHECKS.json');e=load(guide['extended']/'EXTENDED_CHECKS.json');p=load(guide['plates']/'PLATE_REPLAY.json');i=load(here/'RETRIEVED_INTEGRITY.json')
assert o['original_pytest_cases']==o['original_direct_tests']==22
assert o['verifier_regression_tests']==16 and sum(v for k,v in o['verifier_test_classification'].items() if isinstance(v,int))==16
assert o['original_experiments']['all_fields']==o['original_experiments']['exactly_equal_fields']==1048
assert o['strengthened_finite_suite']['checks']==18049 and c['fresh_corrected']['total_checks']==17699
assert c['representative_assertions']==87 and c['correction']['occurrences_changed']==2
assert o['independent_exact_witnesses']['assertion_count']==o['independent_exact_witnesses']['passed_assertion_count']==269
assert o['fresh_static_formal']['module_count']==25 and o['fresh_static_formal']['theorem_count']==323
assert b['construction_count']==6 and b['check_count']==12 and b['theorem_count_addition']==0
assert g['checks_passed']==180 and len(g['invalid_controls_rejected'])==9
assert e['positive_assertions']==373 and e['negative_controls_rejected']==12
assert p['plate_count']==38 and p['exact_regeneration']
records=[]
for name,d in list(core.items())+[('guide_'+n,d) for n,d in guide.items()]:
 m=load(d/'manifest.json');assert m['schema_version']==2 and m['run']['status']=='completed' and m['run']['exit_status']==0
 records.append({'name':name,'manifest':rel(d/'manifest.json'),'manifest_sha256':sha(d/'manifest.json'),'validation':'PASS with validator --root at the appropriate execution root','execution_root':'.' if name in core else 'editable/visual_guide','actual_argv':m['command'],'run':m['run'],'environment':m['environment'],'execution_input_count':len(m['execution_artifacts']),'declared_outputs':m['outputs']})
checks=o['independent_exact_witnesses']['assertions']
negative=[x['name'] for x in checks if x['name'].startswith('negative_control.')]
assert len(negative)==3
report={
 'schema':'komorebi.paper_vii.monograph_computational_review.v1','date_utc':'2026-10-09','status':'PASS_FOR_STATED_SCOPE',
 'scope':'Current finite source-integrity, numerical, exact rational, SymPy, guide-plate and inherited formal-evidence consistency replays. Traditional new figure-model audit is a separately recorded report. No new Lean compilation or universal proof.',
 'gates':{
  'retrieved_integrity':{'status':'PASS','source_files':784,'archives':2,'source_and_archives_match_retrieved_baseline':True,'archive_payload_members_match':True,'historical_manifest_entries':1291,'historical_manifest_missing_files':0,'historical_manifest_preexisting_hash_mismatches':11,'report':rel(here/'RETRIEVED_INTEGRITY.json'),'report_sha256':sha(here/'RETRIEVED_INTEGRITY.json')},
  'original_integrity':{'status':'PASS','manifest_payload_entries':723,'checksum_entries':724,'interpretation':'File-integrity gate; no Lean kernel execution.'},
  'original_pytest':{'status':'PASS','collected_cases':22,'log':rel(core['original']/'original_pytest.log'),'software':'Actual pytest 9.1.1, plugin autoload disabled; cacheprovider disabled in isolated original companion copy.'},
  'original_direct_functions':{'status':'PASS','functions':22,'source_files':5,'overlap':'Same 22 functions as the pytest gate, so not 44 independent tests.'},
  'verifier_software':{'status':'PASS','methods':16,'positive_methods':9,'malformed_input_or_tamper_controls':7,'interpretation':'Parser/dependency/build-cache Python regressions. These are distinct from inherited Lean deliberate-rejection controls.'},
  'original_experiments':{'status':'PASS',**o['original_experiments'],'interpretation':'All 1048 stored leaf fields, including 1045 numeric fields, exactly matched. Comparison tolerances relative 1e-8 / absolute 1e-10 were recorded but unnecessary for equality in this run. The original experiment/test paths overlap.'},
  'strengthened_raw':{'status':'PASS','checks':18049,'groups':15,'group_results':load(core['original']/'strengthened_numerical_results.json')['groups'],'stored_result_exactly_equal':o['strengthened_finite_suite']['stored_structural_result_exactly_equal'],'interpretation':'Unchanged raw code in isolated copy; old odd-N representative bookkeeping remains inherited in this record. Shipped historical PDFs are read, not rebuilt by this gate.'},
  'strengthened_corrected':{'status':'PASS','checks':17699,'groups':15,'group_results':c['fresh_corrected']['groups'],'representative_assertions':87,'N_min':4,'N_max':32,'exact_changes':c['correction'],'difference_from_raw':-350,'interpretation':'Two lower endpoints only, -N//2 to -(N//2). Exactly N unique residue representatives for each N = 4..32. Raw and corrected suites overlap; totals are not summed.'},
  'independent_fraction':{'status':'PASS','assertions_total':269,'explicit_negative_controls_included':3,'negative_controls':negative,'additional_singular_inverse_rejection_benchmark_included':True,'arithmetic':'Exact fractions.Fraction over Q; fixed finite examples, no sampling or numerical tolerance. Explicit source benchmarks, matrix invariants and independent cofactor determinants are retained.'},
  'inherited_formal_static':{'status':'PASS','modules':25,'targets':323,'inherited_report_utc':o['fresh_static_formal']['inherited_report_utc'],'inherited_report_sha256':o['fresh_static_formal']['inherited_report_sha256'],'saved_negative_control_records_consistent':len(o['fresh_static_formal']['controls']),'fresh_negative_control_execution':False,'interpretation':'Current source/log hashes, inventory, dependency closure and parsed allowed axioms agree with inherited September 6 evidence. No fresh Lean compiler or kernel execution.'},
  'constructed_bindings':{'status':'PASS','objects':6,'binding_assertions':12,'theorem_count_addition':0,'interpretation':'Six constructed-object audit reports bound to inherited source, inventory, runner, log and cumulative report. Objects are separate from 323 theorem targets.'},
  'guide_original_sympy':{'status':'PASS','total_assertions_including_controls':180,'positive_assertions':171,'negative_controls_included':9,'worked_pages':[1,28],'arithmetic':'SymPy 1.14.0 exact rational/algebraic and symbolic expressions with stated variable assumptions; rational Taylor enclosures.'},
  'guide_extended_exact':{'status':'PASS','positive_assertions':373,'negative_controls':12,'total_assertions_including_controls':385,'worked_pages':[29,40],'arithmetic':'Exact Q and Q(i) with fractions.Fraction; fixed finite families; no numerical sampling or symbolic derivative execution.'},
  'guide_plates':{'status':'PASS','plate_sources':38,'original_plate_sources':26,'extended_plate_sources':12,'byte_identical_regeneration':True,'interpretation':'Deterministic vector source regeneration. Sampled geometry is presentation data, not analytic proof.'}},
 'records':records,
 'source_preservation':{'files':784,'archives':2,'raw_archive_crc_and_payload_checks':'PASS','before_after_source_inventory':'PASS','bytes_equal_retrieved_baseline':'PASS'},
 'arithmetic_and_conventions':{'numerical':'IEEE binary64 real/complex arrays; unchanged original rank, norm and tensor conventions. Strengthened channel code uses column vectorization, output tensor input Choi order and output partial trace. Fraction independent Choi construction records its own row-major vec convention.','hypotheses':'Orthogonal complete projector families, Hermitian Hamiltonians and required hidden/full block inverses. Strengthened Feshbach z=.4+.7i with finite Hermitian blocks satisfies the declared inverse regime.','tolerances':'Original tests typically 1e-12..1e-10; original moving-frame certificate 1e-6. Strengthened TOL 2e-9 with per-assertion bounds through 2e-7. Stored-field comparison absolute 1e-10 / relative 1e-8. Exact gates have no numerical tolerance.','seeds':{'original_experiments':20260727,'original_tests':[4,2],'strengthened':20260814},'bounds':'Exact contracts and full finite ranges are pinned in the six v2 manifests. Original numeric range/tolerance details also remain in verification/COMPUTATION_AUDIT.md as inherited documentation; its old dependency-unavailability statements are superseded by this current report.'},
 'not_run':[{'gate':'Fresh Lean/Lake kernel compilation and fresh deliberate rejection controls','reason':'lean, lake and elan executables unavailable; inherited interfaces and imported Mathlib proofs were not independently rebuilt.'},{'gate':'Original complete all-in-one companion chain','reason':'The current report records separate actual gates. It does not claim the original PowerShell runner, its figure-generation chain or its original manuscript TeX rebuild executed as one command.'}],
 'physical_targets':[{'target':n,'status':'OPEN'} for n in ['anomaly-free refinement','uniform Feshbach control for the proposed tower','Lorentzian reconstruction','Einstein infrared limit','positive physical massless spin-two sector']],
 'limitations':['Finite observed residuals/ranks/spectral curves are case-bound. No finite count establishes a universal theorem or any physical continuum target.','Floating rank decisions and residual tests are not conditioning or error certificates for every sampled matrix.','The raw odd-N list has N+1 entries and repeats a residue for odd N; only the separate corrected record supplies exact representative bookkeeping.','The bounded tower terminal-tail illustration is not proof of infinite convergence; the scalar perturbation does not test general anomaly closure.','The original bit-flip helper assumes nonnegative probabilities but does not explicitly reject them; the Euclidean helper casts Hamiltonians to real arrays. Passing intended inputs does not certify unrestricted helper behavior.','Symbolic-library correctness remains a dependency. Current SymPy availability and execution do not supply external theorem authentication.','Numerical-library thread caps are cooperative and may be ignored. POSIX memory/CPU caps are per process; exact effective caps and residual risks are in each run record.','Stored formal source/log matching establishes inherited record consistency, not current kernel checking or expanded formal coverage.'],
 'failures_and_corrections':{'current_failed_scientific_gates':[],'inherited_correction':'The previously isolated two-endpoint odd N correction is retained and freshly replayed, without changing the raw source.'},
 'non_claims':['No new proof route or theorem repair.','No fresh Lean compilation.','No added formal theorem targets from software or figure checks.','No continuum existence, interacting field theory, physical quantum-gravity or blanket novelty conclusion.','Counts from overlapping gates are never added as independent theorem evidence.'],
 'tooling':{n:sha(here/'tools'/n) for n in ['run_experiment.py','validate_manifest.py']},
 'report_dependency_pins':{rel(q):sha(q) for q in [here/'RETRIEVED_INTEGRITY.json',here/'replay_current.py',here/'run_current_checks.py',root/'verification/scripts/exact_rational_witnesses.py',root/'verification/scripts/replay_corrected.py',root/'verification/corrected_strengthened/verify_paper_vii.py',root/'verification/scripts/check_constructed_bindings.py']}
}
(here/'COMPUTATIONAL_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],sha(here/'COMPUTATIONAL_REVIEW.json'))

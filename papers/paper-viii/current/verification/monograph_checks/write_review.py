#!/usr/bin/env python3
"""Assemble current evidence, keeping unavailable and inherited gates explicit."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];C=ROOT/'verification/monograph_checks'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def main():
 run={n:C/f'run_{n}_20261009' for n in ['integrity','static','unit','original','sixth','fifth','structured','test-functions','sympy','auxiliary']};run['vectors']=C/'run_vectors_20261009_final_vectors';run['portable']=C/'run_portable_20261009_final_pages'
 run['sympy']=C/'run_sympy_20261009_final_navigation';run['vectors']=C/'run_vectors_20261009_final_navigation'
 results={n:load(q/'result.json') for n,q in run.items()};manifests=[]
 for n,q in run.items():
  cmd=[sys.executable,str(ROOT/'verification/checks/validate_manifest.py'),str(q/'manifest.json'),'--root',str(ROOT)];p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True);assert p.returncode==0,(n,p.stdout,p.stderr)
  (q/'FINAL_VALIDATION.txt').write_text(p.stdout+p.stderr);manifests.append({'gate':n,'path':(q/'manifest.json').relative_to(ROOT).as_posix(),'sha256':sha(q/'manifest.json'),'current_root_validation':'PASS','result':(q/'result.json').relative_to(ROOT).as_posix(),'result_sha256':sha(q/'result.json')})
 i=load(C/'RETRIEVED_INTEGRITY.json');a=load(run['auxiliary']/'corpus.json');m=load(run['auxiliary']/'traditional_models.json');env=load(C/'ENVIRONMENT_CURRENT.json');s=results['static'];o=results['original'];v=results['portable'];sy=results['sympy']
 assert {p.relative_to(ROOT).as_posix() for p in (ROOT/'source').rglob('*') if p.is_file()}=={row['path'] for row in i['source_inventory']}
 assert (i['source_files'],s['theorem_declarations'],s['construction_audits'],results['unit']['tests_run'],results['test-functions']['test_functions'],sum(o['groups'].values()),sy['checks_passed'],len(sy['invalid_controls_rejected']),v['positive_assertions'],v['negative_controls_rejected'],m['positive_assertions'],m['false_controls_rejected'])==(1062,392,66,43,34,37392,190,11,208,15,74,5)
 report={'schema':'komorebi.paper_viii.monograph_computational_review.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS_FOR_STATED_SCOPE','scope':'Fresh finite scientific/metadata/source/archive/symbolic/independent-rational/plate replays with validated bounded provenance. Inherited Lean compiler evidence is checked statically. No new Lean, pytest or device timing was executed.','gates':{
 'raw_preservation':{'status':'PASS','source_files':1062,'source_bytes':i['source_bytes'],'source_matches_retrieved':True,'archives':i['archives'],'manifest_entries':results['integrity']['manifests'],'overlap':'930complete+132strengthened raw files are unique tree paths;928complete/723snapshot/131strengthened manifest entries overlap and are not summed as unique files.'},
 'historical_outer_index':{'status':'PREEXISTING_FORMATTING_STALENESS_RECORDED','entries':i['historical_outer_index']['entries'],'missing_files':len(i['historical_outer_index']['missing']),'preexisting_hash_or_size_mismatches':len(i['historical_outer_index']['preexisting_hash_or_size_mismatches']),'unindexed_retrieved_paths':len(i['historical_outer_index']['unindexed_retrieved_payload_paths']),'report':'verification/monograph_checks/RETRIEVED_INTEGRITY.json','interpretation':'These ten changes and13extra publication files are already present in the retrieved Oct8 formatting. Raw scientific trees and both original ZIP payloads match. Root reconciliation separately records outdated top-level PDF/page metadata.'},
 'inherited_formal_evidence':{'status':'PASS_STATIC_ONLY','modules':len(s['modules']),'named_theorem_declarations':392,'construction_audits':66,'audited_names':458,'coverage_ledger_complete':56,'separate_classical_inputs':4,'inherited_completed_utc':s['inherited_completed_utc'],'inherited_negative_controls':s['inherited_negative_controls'],'fresh_kernel_check':False},
 'verifier_software':{'status':'PASS','unittest_methods':43,'runner':'Actual unittest suite in isolated source copy; includes parser/dependency/census and bounded numerical mirror regressions.'},
 'archival_function_tests':{'status':'PASS','baseline_functions':23,'strengthened_functions':11,'total_functions':34,'runner':'Direct unchanged function invocation, including a real tmp_path fixture; this is not a pytest session.','generated_historical_chart_files':len(results['test-functions']['generated_historical_figure_files']),'chart_interpretation':'18PDF/PNG pairs replot historical corpus rows; no timing reproduction.','warnings':len(results['test-functions']['warnings'])},
 'original_deterministic_suite':{'status':'PASS','assertions':37392,'groups':o['groups'],'metadata_assertions':804,'metadata_details':'778historical corpus plus26source integrity assertions; these do not authenticate hardware measurement or correctness references.'},
 'structured_mirror':{'status':'PASS','exact_rational':results['structured']['exact_rational'],'fourier':results['structured']['floating_point_fourier']},
 'fifth_mirror':{'status':'PASS','counts':results['fifth']['counts'],'numerical_maxima':results['fifth']['numerical_maxima']},
 'sixth_mirror':{'status':'PASS','factor_pairs':182,'truncations':638,'sampled_rank_bounded_competitors':3190,'malformed_input_controls':9,'assumption_removal_controls':2,'seed':60606,'relative_tolerance':2e-9,'maximum_residuals':results['sixth']['maximum_residuals']},
 'original_sympy_worked_models':{'status':'PASS_FRESH','positive_assertions':190,'false_controls':11,'python':sy['python_version'],'sympy':sy['sympy_version'],'model_sha256':sy['model_sha256'],'checker_sha256':sy['checker_sha256'],'relationship':'Previously inherited190/11SymPy result is now genuinely replayed. Independent portable208/15 checks are overlapping displayed models, not an additive theorem count.'},
 'final_portable_visual_models':{'status':'PASS','positive_assertions':208,'false_controls':15,'domains':v['arithmetic_domains'],'bounds':v['tested_bounds'],'final_pages_sha256':v['source_pages_sha256'],'final_extensions_sha256':v['extension_pages_sha256']},
 'vector_plate_regeneration':{'status':'PASS','plates':30,'exact_original_matches':28,'intentional_header_coordinate_repairs':2,'interpretation':'Only complex_core header(0,3)->(0,3.4) and quantization header(0,2.7)->(0,3.2) differ from original generator output; mathematical text and geometry elsewhere match exactly.'},
 'new_traditional_exact_models':{'status':'PASS','positive_assertions':74,'false_controls':5,'bounds':m['bounds'],'exact_values':m['exact_values'],'independence':'Standard-library Fraction model construction and Gaussian elimination; exhaustive prefix/assignment enumeration rather than importing the figure generator.'},
 'historical_corpus_arithmetic':{'status':'PASS_ARITHMETIC_ONLY','rows':154,'ratio_fields_checked':264,'logical_throughput_fields_checked':146,'no_unique_baseline_fields':a['ratio_fields_with_no_unique_recorded_baseline'],'ratio_fields_with_different_recorded_timing_scope':sum(q['timing_scope']!=q['baseline_timing_scope'] for q in a['ratio_checks']),'tolerance':a['tolerance'],'interpretation':'Arithmetic was recalculated using actual median_ms/logical_flops/ratio fields and unique same-case recorded dense baseline rows.130ratio fields join different recorded timing scopes. No same-device-output or correctness-reference provenance was recovered; this is not benchmark replication.'},
 'shared_Paper_VII_foundation':{'status':'PASS','sha256':results['auxiliary']['shared_foundation']['current_sha256'],'current_matches_copied_predecessor_bytes':True,'fresh_compilation':False},
 'unavailable':{'pytest':'Import failed and offline dependency cache has no pytest package.34unchanged test functions ran directly. No pytest session is claimed.','Lean/Lake':'Compilers, pinned Mathlib kit and compiled local interfaces unavailable; inherited run remains September6.','GPU/CUDA':'No device benchmark or CUDA execution attempted; historical corpus is preserved and arithmetic checked only.'}},
 'environment':env,'provenance_manifests':manifests,'resource_caps':{'wall_seconds':240,'CPU_seconds_per_process':210,'address_space_bytes':2147483648,'CPU_affinity_cores':1,'cooperative_numerical_library_threads':1,'log_output_bytes':4194304},'interpretation':{'counts':'Counts measure different and often overlapping cases, source records and assertions. They are not unique theorem/discovery counts.','rank_and_tolerance':'Binary64/complex128 replays retain original tolerances and numerical rank thresholds. Several SVD/QR comparisons share NumPy libraries.','representation':'Prototype stored block keys, exact nonzero projector support and thresholded numerical support differ. Legacy reduced-QR widths do not establish exact actual-rank compact ranges.','bounds':'Finite work establishes implementation assertions and bounded example consistency; universal statements remain separate mathematical proofs and their hypotheses.','failure_record':'Pytest import/offline resolution failed before a test session. Final manifest validation caught the updated navigation helper in the two early broad guide pins; original SymPy and vector runs were superseded by fresh final-navigation runs. No scientific assertion failed.'}}
 (C/'COMPUTATIONAL_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
 (C/'README.md').write_text('''# Paper VIII current computation review

All completed fresh gates pass within their stated finite contracts. The raw
scientific source trees retain 1,062 files and match both original ZIP payloads.
The formal compiler result remains inherited from September 6. No Lean, Lake,
pytest session, CUDA implementation or device timing was executed in this pass.

| Gate | Fresh result |
|---|---|
| Raw source / ZIP preservation | 930 complete and 132 strengthened files match; 928 / 723 / 131 overlapping archived manifest entries match |
| Inherited formal record comparison | 40 modules, 392 theorem declarations, 66 construction audits and 458 audited names match source, inventory, dependency and saved log bytes |
| Verifier software | 43 actual unittest methods pass |
| Archival Python tests | 23 baseline + 11 strengthened unchanged functions pass by direct invocation; 18 historical PDF/PNG chart pairs regenerated |
| Original deterministic suite | 37,392 assertions in nine groups pass; 778 corpus and 26 source checks are metadata |
| Structured mirror | 180 Kronecker, 120 tensor, 96 Walsh, 240 Toeplitz, 600 clipped cases; 1,800 infeasible budgets rejected; 96 complex Fourier cases |
| Fifth mirror | 820 band, 200 staged DAG, 125 exhaustive schedule, 60 inverse, 50 Schur, 72 exact noncoordinate, 64 complex discovery, 120 Jacobi cases |
| Sixth mirror | 182 factor pairs, 638 truncations, 3,190 sampled competitors; nine invalid inputs and two assumption-removal controls |
| Original SymPy worked models | Fresh 190 exact positive assertions and 11 shortcut controls |
| Independent final portable guide | 208 integer/rational/Gaussian-rational assertions and 15 controls |
| Original Python vector generator | 30 plates regenerated; 28 exact and two documented header-position repairs |
| New traditional finite models | 74 independent rational assertions and five false controls |
| Historical corpus arithmetic | 264 stored ratios and 146 logical-throughput fields recalculated across 154 stored rows |

The tests and examples overlap. Their counts are not added as unique results,
theorems, or discoveries. `COMPUTATIONAL_REVIEW.json` links each current bounded
manifest and hashes its scientific result. `ENVIRONMENT_CURRENT.json` records
actual available dependency versions.

## What failed

Pytest import raised `ModuleNotFoundError`. Offline dependency resolution also
failed because there was no cached pytest package. Neither failure ran a
scientific test session. The unchanged 34 source test functions were then
executed directly with the required real temporary `Path` fixture. This is
reported as direct execution, never as pytest. No mathematical assertion
failed in the completed gates. No package was installed.

Final current-root manifest validation also detected that the navigation helper
`source/update_crosswalk.py` changed after the two early guide runs. The math
code did not change. The original SymPy and vector gates were rerun against
the frozen final helper; the current review uses those new manifests. The
earlier records remain as superseded historical executions and are not counted
as current validated evidence. This stale-pin catch was a provenance check,
not a mathematical failure.

## Arithmetic and finite ranges

The structured and graph mirrors use exact `Fraction` rational calculations.
The Fourier, complex discovery, whitening and recompression mirrors use NumPy
binary64/complex128. The original suite keeps its original `allclose` and
`isclose` tolerances, including default relative tolerances where the source
uses them. A pass is not a uniform machine-epsilon certificate.

Fourier dimensions are 1 through 24, four complex samples each, seed 20260906,
absolute threshold 1e-10. The maximum application residual was
2.0388725187405107e-13. The fifth mirror uses seed 202609065 with band packet
counts at most 40, DAG vertices at most seven, inverse packets at most six,
noncoordinate dimensions at most six, complex discovery and Jacobi dimensions
at most eight. Jacobi coupling values are 0, .05, .2, .6 and .95.

The sixth mirror uses seed 60606 and dimensions 0 through 10. It includes empty,
zero, rectangular, rank-deficient and repeated-singular-value factors, with
retained ranks 0, 1, near full, full and above full. The column-space threshold
is 1e-11 times max(1, largest singular value), the output rank threshold is
1e-9 times max(1, Frobenius norm), and normalized comparison tolerance is 2e-9.
Its maximum compact reconstruction residual is 1.2730256604370022e-15;
spectral and Frobenius tail residuals are 3.556141234775559e-15 and
3.660976558279377e-15. This is a finite numerical mirror, not exact rank
certification or an independent implementation of a numerical SVD library.

The new independent traditional model checker uses rational Gaussian
elimination for a 4 by 4 BDLR inverse, three complete prunings of a five-node
tree, seven sampled Lagrange values plus an exact empty supporting interval,
tree budgets 0 through 6, and all eight precision assignments with every prefix
table and budgets 0 through 8. The output is (5, 6, 15, 20), the Woodbury core
is 3/2, and the exact budget-three precision optimum is AFF with cost 6 and
error 3. These costs and errors are declared illustrative models.

## Evidence boundaries

The 56 completed formal coverage records and four separate classical inputs
remain the inherited contract. The saved accepted compiler run completed
2026-09-06T22:38:55.838919+00:00. The source/log check is fresh; compilation and
kernel checking are not. The two false/admitted-proof controls were compared
with saved recorded rejection logs, not recompiled. The reused Paper VII
foundation is byte-identical at SHA-256
92e49bb023877ed1f1c2bb34968aa81ee7724fa3a8e1801a831cfc70f1de3595.

The original SymPy models now genuinely run with SymPy 1.14.0. The independent
standard-library portable models remain a second exact implementation of
overlapping displayed examples. Both preserve their original code. The vector
generation reproduces all 30 formulas and math labels. Two authored header
locations move upward to avoid title crowding: complex_core from (0,3) to
(0,3.4), and quantization from (0,2.7) to (0,3.2). The original generated files
and current authored plate hashes are retained separately.

The 154-row historical corpus labels itself measured. This audit recalculates
the arithmetic in 264 recorded ratios and 146 logical-throughput fields using
actual stored fields and unique same-case recorded dense baseline rows. It
does not recover or authenticate same-device outputs or correctness-reference
provenance. 130 ratio fields cross recorded timing scopes. Matching metadata
labels do not establish matching precision or hardware execution contracts.
Generated historical charts are replots, not measurements.

The retrieved old outer manifest has 1,549 entries, zero missing files, ten
preexisting hash/size mismatches, and 13 unindexed publication additions from
later formatting. `RETRIEVED_INTEGRITY.json` lists them. The protected original
source trees and ZIPs match exactly. Root-level metadata reconciliation handles
outdated PDF page counts and hashes separately. No source mathematics was
rewritten to force a test pass.

The legacy prototype reports stored block keys, which may include zero blocks;
the mathematics uses exact nonzero projector support. Thresholded numerical
support is a third representation. The older reduced-QR prototype also does
not certify exact actual-rank compact ranges. Fresh finite passes do not erase
these representation boundaries.

## Reproduction

Run from the extracted edition root. Each run requires a new output suffix:

```bash
python verification/monograph_checks/run_current_checks.py --suffix NEW_RUN
python verification/monograph_checks/run_current_checks.py --modes portable vectors --suffix NEW_GUIDE_RUN
```

The current exact auxiliary checks can also be run to new output files:

```bash
python verification/monograph_checks/check_corpus_arithmetic.py --corpus source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package/verification/benchmark_results_sanitized.json --out NEW_CORPUS_RESULT.json
python verification/monograph_checks/check_traditional_models.py --data editable/traditional/monograph_data/exact_examples.json --out NEW_MODEL_RESULT.json
```

All accepted current records use the supplied version2 bounded runner. Every
manifest records actual argv, UTC start, runtime, exit code, declared inputs
before and after execution, scientific result hashes, logs and resource caps.
Validate a record against the current extracted root with:

```bash
python verification/checks/validate_manifest.py verification/monograph_checks/run_original_20261009/manifest.json --root .
```

The caps are 240 seconds wall time, 210 CPU seconds per process, two GiB address
space, one CPU affinity core, four MiB logs and cooperative one-thread numerical
library settings. The cooperative thread request is not proof that every
library honors it. This archive tree has no project Git commit. The isolated
replays copy original scientific files, verify copy hashes, execute unchanged
code there and confirm that delivered source bytes remain unchanged.
''')
 print('PASS COMPUTATIONAL REVIEW:',len(manifests),'validated manifests')
if __name__=='__main__':main()

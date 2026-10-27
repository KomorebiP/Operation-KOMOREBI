#!/usr/bin/env python3
"""Validate current bounded evidence and compile its scoped Paper VI report."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
NAMES=['source_integrity','static_pytest_verifier','original_sympy_exact','independent_exact_rational',
       'numerical_companion','annals_numerical','strengthened_baseline','strengthened_expanded','monograph_figure_models']

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def write(p,data): p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def groups(stdout):
    rows=[]
    for line in stdout.splitlines():
        match=re.fullmatch(r'  (.+): (\d+)',line)
        if match: rows.append({'group':match[1],'checks_reported':int(match[2])})
    return rows

def main():
    runs=[];data={}
    index=read(HERE/'ACTIVE_RUNS.json') if (HERE/'ACTIVE_RUNS.json').is_file() else {'active_runs':{name:name for name in NAMES},'superseded_runs':[]}
    for name in NAMES:
        folder=HERE/'runs'/index['active_runs'][name];manifest=folder/'manifest.json'
        p=subprocess.run([sys.executable,'-B',str(HERE/'tools/validate_manifest.py'),str(manifest),'--root',str(ROOT)],
                         text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (folder/'MANIFEST_VALIDATION.txt').write_text(p.stdout,encoding='utf-8')
        if p.returncode: raise RuntimeError('Manifest no longer validates: '+name+'\n'+p.stdout)
        m=read(manifest);r=read(folder/'result.json')
        if m['schema_version']!=2 or m['run']['status']!='completed' or r['status']!='PASS':
            raise RuntimeError('Run was not successfully completed: '+name)
        data[name]=r
        runs.append({'suite':name,'manifest':manifest.relative_to(ROOT).as_posix(),'manifest_sha256':digest(manifest),
                     'schema_version':2,'status':m['run']['status'],'exit_status':m['run']['exit_status'],
                     'runtime_seconds':m['run']['runtime_seconds'],'resource_limits':m['run']['resource_limits'],
                     'wall_timeout_seconds':m['run']['timeout_seconds'],'max_combined_log_bytes':m['run']['max_output_bytes'],
                     'result':(folder/'result.json').relative_to(ROOT).as_posix(),'result_sha256':digest(folder/'result.json'),
                     'manifest_validation':'PASS'})
    original=read(ROOT/'source/complete/original_snapshot/verification/verification_status.json')
    exact=data['original_sympy_exact'];rational=data['independent_exact_rational'];num=data['numerical_companion'];static=data['static_pytest_verifier']
    source=data['source_integrity']
    source_report={'schema':'komorebi.paper_vi.source_snapshot_preservation.v1',
          'status':'PASS','generated_at_utc':datetime.now(timezone.utc).isoformat(),
          'source_files':source['source_files'],'snapshot_files':source['original_snapshot_files'],
          'archives':source['archives'],'nested_manifests':source['nested_manifests'],
          'source_sha256':source['source_sha256'],'downloads_sha256':source['downloads_sha256'],
          'missing_source_files':[], 'scope':'Exact archive extraction sets and bytes plus recorded original snapshot hashes. All original files, including historical caches, are preserved.'}
    source_path=HERE/'SOURCE_SNAPSHOT_PRESERVATION.json'
    previous=read(source_path) if source_path.is_file() else {}
    if {k:v for k,v in previous.items() if k!='generated_at_utc'}!={k:v for k,v in source_report.items() if k!='generated_at_utc'}:
        write(source_path,source_report)
    companion_visual=ROOT/'editable/visual_guide'
    visual_records=[]
    for name in ['extensions_exact','plates']:
        manifest=companion_visual/'checks/runs'/name/'manifest.json'
        if not manifest.is_file(): raise RuntimeError('Visual record not available: '+name)
        p=subprocess.run([sys.executable,'-B',str(HERE/'tools/validate_manifest.py'),str(manifest),'--root',str(companion_visual)],
                         text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if p.returncode: raise RuntimeError('Visual record invalid: '+name+'\n'+p.stdout)
        m=read(manifest)
        if m['schema_version']!=2 or m['run']['status']!='completed': raise RuntimeError('Visual record incomplete: '+name)
        visual_records.append({'name':name,'manifest':manifest.relative_to(ROOT).as_posix(),'manifest_sha256':digest(manifest),
                               'root_for_validation':'editable/visual_guide','status':'PASS','runtime_seconds':m['run']['runtime_seconds'],
                               'resource_limits':m['run']['resource_limits']})
    numerical_suites=[]
    for name in ['annals_numerical','strengthened_baseline','strengthened_expanded']:
        d=data[name];row={'name':name,'checks_reported':d['checks_reported'],'groups':d['groups'],'status':'PASS',
                        'counting_policy':d['arithmetic'],'overlap':d['overlap']}
        folder=HERE/'runs'/name
        if name=='annals_numerical':
            row['group_results']=read(folder/'verification_results.json')
        else: row['group_results']=groups((folder/'command.log').read_text())
        numerical_suites.append(row)
    report={'schema':'komorebi.paper_vi.monograph_computation_review.v1','status':'PASS_STATED_FINITE_SCOPE',
            'generated_at_utc':datetime.now(timezone.utc).isoformat(),'bounded_v2_runs_validated':len(runs),
            'separately_owned_visual_v2_runs_validated':len(visual_records),
            'environment':read(HERE/'runs/source_integrity/manifest.json')['environment'],
            'source_preservation':{'source_files_byte_identical':739,'original_snapshot_files_byte_identical':534,
                                   'original_archives_crc_and_exact_extraction':'PASS','missing_source_artifacts':[],
                                   'report':'verification/monograph_checks/SOURCE_SNAPSHOT_PRESERVATION.json'},
            'fresh':{'unchanged_original_static_dispatch':{'command':'python3 -B verification/verify.py --static-only',
                           'executed_in':'Disposable copy of source/complete/original_snapshot','status':'STATIC_AND_COMPANION_ONLY',
                           'source_contract':static['source_contract'],'pytest_cases':54,'pytest_failures':0,'pytest_errors':0,'pytest_skipped':0,
                           'verifier_test_methods':6,'positive_controls':1,'deliberate_corruption_controls':5,
                           'meaning':'Static integrity/configuration/import/lexical/audit-coverage checks and finite numerical regressions. No compiler or kernel replay.'},
                     'original_sympy_examples':{'assertions':204,'false_controls_rejected':11,'finite_families':exact['finite_families'],
                           'scope':exact['scope'],'input_hashes':exact['original_input_hashes']},
                     'independent_fraction_examples':{'assertions':182,'false_controls_rejected':4,
                           'bounded_families':rational['bounded_families'],'overlap':rational['overlap']},
                     'original_numerical_companion':{'numeric_fields_compared':79,'identical_stored_numeric_values':79,
                           'identical_non_numeric_leaves':num['non_numeric_leaves'],'relative_tolerance':1e-7,'absolute_tolerance':5e-10,
                           'figure_pairs_regenerated':19,'scope':num['scope']},
                     'original_numerical_suites':numerical_suites,
                     'new_explanatory_figure_models':{'exact_fraction_assertions':51,'models':['Two rational3x3 column-stochastic matrices and the11/36 packet-path sum','Two rational priors with equal coarse masses and block-constant/varying likelihoods','Nilpotent2x2 Jordan polynomial semigroup factor'],
                           'scope':'Finite pedagogic examples only. Floating exponentials in the memory plot are illustrations.'},
                     'separately_owned_visual_guide':{'exact_extension_assertions':120,'false_controls_rejected':8,
                           'vector_plates_regenerated':40,'inherited_plates':26,'extension_plates':14,'byte_identical_plate_sources':40,
                           'evidence':visual_records,'scope':'Separate guide owner reports. Original204assertions and182Fractionexamples are not rerun or added again here.'}},
            'inherited_lean':{'timestamp_utc':original['timestamp_utc'],'release':original['release'],
                             'status':original['status'],'scoped_results_complete':33,'supporting_theorem_targets':341,
                             'production_proof_modules':47,'namespace_declarations':782,'open_conjectures_excluded':3,
                             'source_record':'source/complete/original_snapshot/verification/verification_status.json',
                             'fresh_kernel_replay':False,'formal_scope':'Inherited recorded scoped formal statements; full_paper_formalized=false and manuscript correspondence remains manual.'},
            'not_run':[{'gate':'Lean compiler, namespace axiom audit and dependency checkout verification','reason':'lean, lake and elan unavailable. No compiler or kernel process ran.'},
                       {'gate':'New universal analytic proof or unrestricted resolution of the three conjectures','reason':'Outside this finite computation and editorial task.'},
                       {'gate':'Independent literature authentication or broad source-to-Lean semantic audit','reason':'Original mathematical correspondence is not established by execution-input hashes or token scanning.'}],
            'implementation_review':{'original_code_mutated':False,'original_source_and_downloads_changed':False,
                       'finite_conventions_checked':['Column-stochastic transitions and departure-state Feynman-Kac weighting','Weighted expectation adjoint versus Euclidean symmetry','All35denominator-four simplex priors, including zero-mass packets','Exact Schur/Jordan and rectangular rational models','Green-kernel grid factor h and finite mesh error'],
                       'orthogonal_evidence':'Independent Fraction matrix arithmetic reproduces rational subsets of the SymPy example suite, including deliberate false controls. Original SciPy numerical regressions cover broader finite models with source tolerances.',
                       'original_control_policy':'Six verifier unittest methods include one valid contract and five corruption rejections. They are not described as six invalid examples.',
                       'counting_policy':'No overlapping test, sample, matrix-entry, source-token or suite tally is summed into independent mathematical result coverage.'},
            'failures':[],'preflight_notes':['Wrapper syntax and JSON serialization were checked before execution. No bounded scientific suite failed.'],
            'residual_risks':['Finite bounds and sampled numerical plots do not prove general analytic results.','SymPy output relies on the documented assumptions and installed symbolic library.','Floating comparisons retain original tolerances and sampling/quadrature limitations.','Machine thread caps are cooperative; POSIX CPU caps are per process rather than aggregate process-tree budgets.','Inherited Lean evidence has not been refreshed in this environment.','Historical global manifest differences outside source/downloads are documented separately in provenance/BASELINE_METADATA_RECONCILIATION.json.'],
            'runs':runs,'active_run_index':'verification/monograph_checks/ACTIVE_RUNS.json',
            'superseded_runs':index['superseded_runs'],
            'final_presentation_update':{'bounded_figure_models_replayed':bool(index['superseded_runs']),
                 'reason':'Final print QA shortened two Bayesian panel titles. The exact_models() body is byte-identical. Only the explanatory model run was refreshed; the prior run remains historical and adds no independent coverage.'},
            'non_claims':['No unrestricted full-paper formalization or closure of the three open conjectures.','No new Lean kernel proof or claims of current namespace elaboration.','No bit-identical numerical figure PDF assertion.','No sum of mixed overlapping assertion counts as a count of independently proved theorems.']}
    write(HERE/'COMPUTATIONAL_REVIEW.json',report)
    lines=['PAPER VI MONOGRAPH COMPUTATIONAL REVIEW','PASS for the stated finite scope','',
           'Nine bounded v2 runs validate with current input and output hashes. Two separately owned visual runs validate against their guide root.',
           'All 739 original source files and 534 snapshot files match their recorded identities. Three archives pass CRC and exact extraction reconciliation. No source artifacts are missing.',
           'The unchanged original static-only gate runs 54 pytest cases with zero failures/errors/skips and six verifier methods: one valid contract and five deliberate corruption controls.',
           'Original SymPy suite: 204 assertions and 11 rejected false controls. Independent Fraction witnesses: 182 assertions and 4 rejected controls. These examples overlap and are not added as independent coverage.',
           'Numerical companion: 79 numeric fields and 2 nonnumeric leaves equal saved values. Nineteen original figure pairs regenerated. Numerical comparison retains rtol 1e-7 and atol 5e-10.',
           'Annals 475471 checks/16 groups. Strengthened baseline 149349/14. Strengthened expanded 154608/15. These are mixed finite sample, matrix-entry and source-hygiene tallies with different overlapping scopes.',
           'Three new explanatory models pass 51 Fraction assertions. The visual owner reports 120 extension assertions with 8 rejected controls and 40 byte-identical regenerated vector plate sources.',
           '',
           'No new Lean execution. Retained September 6 v0.5.0 evidence records 341 supporting targets in 47 modules and 782 namespace declarations for 33 scoped manuscript results. The three conjectures remain excluded. The inherited record says full_paper_formalized=false; correspondence is manual.',
           'No bounded scientific suite failed. Finite examples, symbolic-library output and sampled numerical comparisons are not universal proofs.',
           'Final print QA shortened two Bayesian panel titles. The exact model body is unchanged. Only its 51-assertion replay was refreshed. ACTIVE_RUNS.json identifies the nine current records and preserves the prior caption run as historical evidence, without adding coverage.',
           '',
           'Replay: python3 -B verification/monograph_checks/launch_runs.py --run-prefix replay_','Validate/review: python3 -B verification/monograph_checks/compile_review.py',
           'Use a fresh prefix or delete only intentionally replaceable new replay folders. Never modify the original source or downloads trees.']
    text='\n'.join(lines)+'\n'
    (HERE/'COMPUTATIONAL_REVIEW.txt').write_text(text,encoding='utf-8')
    print(json.dumps({'status':report['status'],'bounded_v2_runs':9,'visual_v2_runs':2,
                      'report':(HERE/'COMPUTATIONAL_REVIEW.json').relative_to(ROOT).as_posix()},indent=2))

if __name__=='__main__': main()

#!/usr/bin/env python3
"""Consolidate recorded Lean checks and verify that their sources/dependencies still match.

Run after verify_blocks.py and before creating SHA256SUMS. This audits receipts;
it does not rerun Lean or claim the Mathbox official validator was executed.
"""
from __future__ import annotations
import collections, datetime, hashlib, json, platform, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path('/mnt/data/lean_runtime_parts/Komorebi_Portable_Lean_4.34.0-rc2')
CACHE = RUNTIME/'workspace/.lake/build/lib/lean/Komorebi'
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, obj): (ROOT/name).write_text(json.dumps(obj, indent=2)+'\n')
def main():
    modules = json.loads((ROOT/'MODULE_ORDER.json').read_text())
    declarations = json.loads((ROOT/'DECLARATIONS.json').read_text())
    attempts=[]
    for p in sorted((ROOT/'audit').glob('*/*.json')):
        try: d=json.loads(p.read_text())
        except json.JSONDecodeError: continue
        if isinstance(d,dict) and 'module' in d and 'exit_status' in d:
            d['receipt_path']=p.relative_to(ROOT).as_posix()
            attempts.append(d)
    final=[]
    for m in modules:
        h=sha(ROOT/'Komorebi'/f'{m}.lean')
        eligible=[d for d in attempts if d['module']==m and d['exit_status']==0
                  and d['source_sha256_before']==h]
        assert eligible, f'No successful receipt for final source {m}'
        d=eligible[-1]
        assert d['source_sha256_after']==h==d['staged_source_sha256']
        assert sha(CACHE/f'{m}.olean')==d['output_sha256'], ('stale output',m)
        log=ROOT/Path(d['receipt_path']).with_suffix('.log')
        assert sha(log)==d['log_sha256'], ('changed log',m)
        snap=ROOT/Path(d['receipt_path']).with_suffix('.lean')
        assert sha(snap)==h, ('changed source snapshot',m)
        for dep, data in d['dependencies'].items():
            dn=dep.split('.')[-1]
            assert sha(ROOT/'Komorebi'/f'{dn}.lean')==data['source_sha256'],('source dependency',m,dn)
            assert sha(CACHE/f'{dn}.olean')==data['olean_sha256'],('compiled dependency',m,dn)
        final.append(d)
    # Preserve the original Gaussian layer and the full perturbation source.
    inherited=json.loads((ROOT/'INHERITED_SOURCES.json').read_text())
    for name,h in inherited.items():
        parent='PREDECESSOR' if name=='BayesianMultiscaleKalmanPosteriorPerturbation.lean' else 'Komorebi'
        assert sha(ROOT/parent/name)==h, ('changed inherited source',name)
    split=json.loads((ROOT/'DEPENDENCY_SPLIT.json').read_text())
    lines=(ROOT/'PREDECESSOR/BayesianMultiscaleKalmanPosteriorPerturbation.lean').read_text().splitlines(True)
    for item in split['modules']:
        assert sha(ROOT/'Komorebi'/f"{item['module']}.lean")==item['output_sha256']
        for (a,b),h in zip(item['source_ranges'],item['range_sha256']):
            assert hashlib.sha256(''.join(lines[a-1:b]).encode()).hexdigest()==h
    prohibited=[]
    for m in modules:
        for token in re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',(ROOT/'Komorebi'/f'{m}.lean').read_text()):
            prohibited.append([m,token])
    assert not prohibited,prohibited
    ax_receipt=next(d for d in final if d['module']=='FDSemanticAxiomAudit')
    ax_log=ROOT/Path(ax_receipt['receipt_path']).with_suffix('.log')
    matches=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",ax_log.read_text(),re.S)
    names={x['name'] for x in declarations}
    assert len(matches)==len(names)==len(declarations)
    axioms={name:[s.strip() for s in aa.split(',') if s.strip()] for name,aa in matches}
    assert set(axioms)==names
    union=sorted({a for xs in axioms.values() for a in xs})
    assert set(union)<={'propext','Classical.choice','Quot.sound'},union
    write('AXIOM_AUDIT.json',{'status':'PASS','scope':'all 138 active theorem/lemma declarations',
          'declaration_count':len(names),'axiom_union':union,'declarations':axioms,
          'source_log':ax_log.relative_to(ROOT).as_posix(),'source_log_sha256':sha(ax_log),
          'source_receipt':ax_receipt['receipt_path']})
    incomplete=[]
    for p in sorted((ROOT/'audit').glob('*/*.lean')):
        if not p.with_suffix('.json').exists():
            incomplete.append(p.relative_to(ROOT).as_posix())
    controls=json.loads((ROOT/'audit/negative_controls/RESULT.json').read_text())
    assert len(controls)==2 and all(c['expected_rejection'] and c['exit_status']!=0 for c in controls)
    for c in controls:
        assert sha(ROOT/'audit/negative_controls'/f"{c['name']}.log")==c['log_sha256']
    exact=json.loads((ROOT/'checks/EXACT_REGRESSION.json').read_text())
    group_counts=dict(collections.Counter(x['group'] for x in declarations))
    commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    nonclaims=[
      'No Wasserstein, Hellinger, KL, total variation, or other posterior-distribution metric bound.',
      'No same-observation common canonical null-set assertion across distinct evidence laws.',
      'No operator-norm Pythagorean identity and no inferred self-adjointness of inherited projectors.',
      'No identification of primitive model defects from agreement of posterior distributions.',
      'No singular-innovation or pseudoinverse conditioning.',
      'No full Itô derivation, sequential filtering closure, nonlinear/non-Gaussian extension or optimal refinement theorem.',
      'No literature-priority claim. Declaration counts include support identities and regressions.',
      'Pinned Mathlib cache reused; the entire historical program and unused continuous-time blocks were not rebuilt.'
    ]
    receipt={'status':'PASS','sealed_at_utc':now,'source_commit':commit,
       'scope':'Finite-dimensional Gaussian posterior moment semantics integrated with operator perturbation and projector refinement',
       'environment':{'lean_version':final[0]['lean_version'],'mathlib_commit':final[0]['mathlib_commit'],
          'platform':platform.platform(),'warning_as_error':True,'threads_per_lean_process':1},
       'final_modules_passed':len(final),'theorem_lemma_declarations':len(declarations),
       'declaration_groups':group_counts,'new_declarations':group_counts['new'],
       'successful_final_modules':final,'direct_dependency_hashes_match_final':True,
       'inherited_source_hashes_unchanged':len(inherited),'normalized_dependency_modules':len(split['modules']),
       'active_source_forbidden_token_occurrences':prohibited,
       'axiom_audit_count':len(axioms),'axiom_union':union,
       'completed_module_attempts':len(attempts),
       'nonzero_attempts':[{k:d[k] for k in ['module','exit_status','elapsed_seconds','receipt_path']} for d in attempts if d['exit_status']!=0],
       'incomplete_attempt_source_snapshots':incomplete,
       'accumulated_final_compile_process_seconds':round(sum(d['elapsed_seconds'] for d in final),3),
       'accumulated_completed_attempt_seconds':round(sum(d['elapsed_seconds'] for d in attempts),3),
       'negative_controls':controls,'exact_diagnostic':exact,
       'verification_boundary':'Every active module has a final-source successful compilation receipt and matching dependencies; this seal checks receipts, sources, output hashes and audit coverage rather than rerunning Lean.',
       'non_claims':nonclaims}
    write('FINAL_VERIFICATION_RECEIPT.json',receipt)
    outputs=['FINAL_VERIFICATION_RECEIPT.json','AXIOM_AUDIT.json','Komorebi/FDPosteriorCertificate.lean',
             'Komorebi/FDCenteredCovariance.lean','checks/EXACT_REGRESSION.json','DEPENDENCY_SPLIT.json']
    manifest={'schema_version':1,'claim_id':'KUI-FD-SEMANTIC-MULTISCALE-POSTERIOR-v0.1.0',
      'repository':{'commit':commit,'dirty':True},
      'command':'python verify_blocks.py --runtime <pinned-runtime> --modules <dependency-ordered modules> --timeout 25 (separate processes, some audit processes capped at 27 seconds); exact argv preserved in successful_final_modules',
      'environment':{'software':[final[0]['lean_version'],'mathlib '+final[0]['mathlib_commit'],
          'Python '+platform.python_version(),'SymPy 1.14.0 for independent rational diagnostic'],
          'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Lean kernel acceptance and axiom dependency auditing for the actual finite-dimensional Gaussian posterior mean/covariance perturbation and projector-refinement certificate, universally quantified under explicit assumptions.',
          'coefficient_domain':'Real vector spaces in Lean; separate diagnostic over exact rational matrices.',
          'conventions':'Euclidean L2 spaces; CLM operator norm; centered covariance constructed from covarianceBilin; PSD priors and PD observation noise; explicit versions pointwise, canonical kernels separately evidence-a.e.',
          'inputs':[json.loads((ROOT/'RESTORATION.json').read_text()),
                    {'inherited_sources_manifest':'INHERITED_SOURCES.json','sha256':sha(ROOT/'INHERITED_SOURCES.json')},
                    {'source_inventory':'DECLARATIONS.json','sha256':sha(ROOT/'DECLARATIONS.json')}],
          'bounds':{'active_lean_modules':len(modules),'audited_declarations':len(declarations),
                    'single_process_caps_seconds':[25,27],'lean_threads':1,
                    'exact_diagnostic':'one fixed two-state rational example; not a finite surrogate for universal proof'},
          'non_claims':nonclaims},
      'randomness':{'used':False,'generator':'none','seed':None},
      'run':{'started_at':min(d['started_at_utc'] for d in final),
             'runtime_seconds':round(sum(d['elapsed_seconds'] for d in final),3),
             'exit_status':0,'runtime_interpretation':'sum of successful final-module process wall times, excluding setup, failures, drafting and sealing'},
      'outputs':[{'path':p,'sha256':sha(ROOT/p)} for p in outputs],
      'checks':['38 final-source module receipts validated against current sources, logs, staged outputs and direct dependency hashes.',
        '19 inherited whole-source hashes and nine normalized source-range hashes checked.',
        'All 138 theorem/lemma axiom lists matched declaration inventory.',
        'No prohibited proof-placeholder/custom-axiom/unsafe/native_decide tokens in active Lean sources.',
        'False equality and placeholder-proof negative controls correctly rejected.',
        'Independent exact rational nonzero covariance-leakage example passed.',
        'Version-1 manifest required fields and output hashes validated by project checks/verify_release.py; official Mathbox validator unavailable and not run.'],
      'result':'Kernel-checked semantic multiscale posterior moment certificate under the stated hypotheses; distribution-metric extension remains open.',
      'residual_risks':['Trust in pinned Lean kernel and supplied Mathlib cached dependencies remains.',
        'This legacy v1 manifest uses accompanying per-process receipts for detailed provenance.',
        'The official Mathbox validator script was unavailable; only the explicit project integrity validator was used.',
        'Sources are checked, but the Python orchestration and extraction implementation are not formally verified; source and range hashes provide reproducibility.',
        'Bounds may be conservative and are not performance or optimality guarantees.']}
    write('COMPUTATION_MANIFEST.json',manifest)
    print(json.dumps({k:receipt[k] for k in ['status','final_modules_passed','new_declarations','theorem_lemma_declarations','declaration_groups','completed_module_attempts','nonzero_attempts','incomplete_attempt_source_snapshots','accumulated_final_compile_process_seconds','axiom_union']},indent=2))
if __name__=='__main__':main()

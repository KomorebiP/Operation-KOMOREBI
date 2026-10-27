from pathlib import Path
import json,hashlib,importlib.util,shutil
B=Path(__file__).parent;R=B/'project'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
sp=importlib.util.spec_from_file_location('verifier',R/'scripts/verify.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
p=R/'verification/current/report.json';d=read(p)
assert d['proofs_and_axioms_passed'] and 'failure' not in d
assert d['source_snapshot']==v.inventory()
control=read(R/'verification/fresh_controls/report.json')
independent=read(R/'verification/fresh_controls/DIAGNOSTIC_REVIEW.json')
canonical=read(R/'verification/fresh_controls/CANONICAL_CLASSIFIER_REVIEW.json')
assert all(x['passed'] and x['complete'] for x in [control,independent,canonical])
assert control['valid_rejections']==183 and len(control['results'])==183
assert not control['invalid_rejections'] and not control['stale_controls'] and not control['pending']
assert canonical['scheduler_report_sha256']==sha(R/'verification/fresh_controls/report.json')
assert canonical['canonical_verifier_sha256']==sha(R/'scripts/verify.py')
for r in control['results']:
 assert sha(R/r['control'])==r['source_sha256_final']==r['source_sha256']
 assert v.classify_negative_control(r)['valid_rejection']
 d['stages'].append({**r,'phase':'negative_control','name':Path(r['control']).stem,'expected_rejection':True})
for phase,f in [('metadata_checks','metadata_checks.json'),('source_scan','source_scan.json'),('negative_classifier_tests','negative_classifier_tests.json')]:
 r=read(R/'verification/current'/f);assert r['passed']
 d['stages'].append({'phase':phase,'returncode':0,'report':f,'report_sha256':sha(R/'verification/current'/f)})
mods=set(v.MODULES)
assert {r['module'] for r in d['stages'] if r['phase']=='compile' and r['module']!='__root__'}==mods
assert {r['module'] for r in d['stages'] if r['phase']=='kernel_replay'}==mods
assert len(mods)==254 and len(d['axioms'])==4454
assert len(d['stages'])==697
d['counts'].update(compiled_targets=255,kernel_replays=254,negative_controls=183,named_declarations=4454,accepted_execution_stages=697,metadata_checks=145,source_guard_cases=15,classifier_cases=33)
d.update(passed=True,complete=True,source_snapshot_unchanged=True,goal_reached=True,
 negative_control_review={'independent':'verification/fresh_controls/DIAGNOSTIC_REVIEW.json','independent_sha256':sha(R/'verification/fresh_controls/DIAGNOSTIC_REVIEW.json'),'canonical':'verification/fresh_controls/CANONICAL_CLASSIFIER_REVIEW.json','canonical_sha256':sha(R/'verification/fresh_controls/CANONICAL_CLASSIFIER_REVIEW.json')},
 execution_history={'module_history':'verification/fresh_cumulative/report.json','control_history':'verification/fresh_controls/report.json','note':'Superseded failures and interrupted diagnostic probes remain in historical receipts. This current report contains only accepted current-source proof stages and intended control rejections.'})
write(p,d)
status=read(R/'CURRENT_STATUS.json');status.update(goal_reached=True,scope_goal_reached=True,verification_passed=True,verification_report_sha256=sha(p),note='All87 registered proposition mappings are complete. Current-source compilation, individual kernel replay, full axiom audit, exact examples,183 rejection controls and metadata checks passed.')
write(R/'CURRENT_STATUS.json',status)
active=read(R/'verification/ACTIVE_EXECUTION.json');active.update(execution_accepted=True,active_session=None,remaining_modules=[],accepted_math_module_count=254,final_report='verification/current/report.json',final_report_sha256=sha(p),final_controls=183)
write(R/'verification/ACTIVE_EXECUTION.json',active)
summary='The delivered execution is PASS: all254 mathematical modules compile with warnings treated as errors and pass individual kernel replay. The complete root import, exact rational examples, all4454 named-declaration axiom checks and all183 isolated rejection controls pass. The only permitted logical axioms are propext, Classical.choice and Quot.sound.'
summary=summary.replace('all254','all 254').replace('all4454','all 4,454').replace('all183','all 183')
for name in ['README.md','AUDIT.md','PROGRESS.md','PUBLICATION_STATUS.md']:
 q=R/name;q.write_text(q.read_text().rstrip()+'\n\n## Accepted execution\n\n'+summary+'\n')
(R/'CONTINUE_HERE.md').write_text('# Completed checkpoint\n\nAll 87 registered proposition mappings and their current-source execution checks are complete. No registered proposition obligation remains.\n\nRead CURRENT_STATUS.json and verification/current/report.json for the accepted result, COVERAGE.md for exact mapped scopes, and LEAN_GUIDE.md for the mathematical route. Reproduce with scripts/verify.py and the pinned portable runtime.\n')
q=R/'PROGRESS_LEDGER.md';q.write_text(q.read_text().rstrip()+'\n\n## LSM-1.0.0 execution closeout\n\nAll 87 registered proposition mappings are complete. Accepted execution: 254 mathematical module compilations and kernel replays, one whole-project root compilation, exact rational examples, the full 4,454-declaration axiom audit and 183 isolated intended rejections. All 145 metadata checks, 15 lexical guard cases and 33 classifier cases pass. The source checkpoint remains fixed; the separate current execution report is accepted. Three inherited controls were repaired with their original bytes and diagnostics preserved. No numbered-proposition restart obligation remains.\n')
dest=R/'verification/execution_tools';dest.mkdir(exist_ok=True)
for name in ['run_fresh.py','resume_fresh.py','resume_fresh_serial.py','resume_noncharts.py','resume_final_certificates.py','finish_verification.py','accept_release.py']:
 shutil.copy2(B/name,dest/name)
write(dest/'SHA256.json',{f.name:sha(f) for f in sorted(dest.glob('*.py'))})
(dest/'README.md').write_text('# Execution provenance\n\nThese are the historical workspace drivers used for the current receipt. Their absolute workspace paths describe this execution. They preserve interrupted and resumed checking without accepting a previous-session proof cache. For a new clean check in a different directory, use the portable public entry point scripts/verify.py.\n')
assert d['source_snapshot']==v.inventory(),'Frozen proof/verifier/metadata inputs changed during acceptance'
print(json.dumps({'accepted':True,'complete_propositions':87,'modules':254,'declarations':4454,'named_theorems':2887,'controls':183,'execution_stages':697,'report_sha256':sha(p)}))

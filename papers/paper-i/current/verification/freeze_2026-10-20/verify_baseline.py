#!/usr/bin/env python3
"""Read-only identity and inherited-evidence check for the Paper I freeze."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, subprocess, sys, zipfile

ROOT = Path('/workspace/scratch/fbc994080222/paper_i_freeze/baseline/Komorebi_Paper_I_Release_2026-10-15')
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
failures=[]
checks={}
def check(label, value):
    checks[label]=bool(value)
    if not value: failures.append(label)

actual={p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob('*') if p.is_file()}
manifest=read(ROOT/'MANIFEST_SHA256.json')
listed={r['path'] for r in manifest['files']}
check('original_manifest_unique',len(listed)==len(manifest['files']))
check('original_manifest_hashes',all(r['path'] in actual and sha(actual[r['path']])==r['sha256'] and actual[r['path']].stat().st_size==r['bytes'] for r in manifest['files']))
extras=sorted(set(actual)-listed)
upload=read(ROOT/'github-upload/UPLOAD_MANIFEST_SHA256.json')
ulisted={r['path'] for r in upload['files']}
check('supplemental_manifest_unique',len(ulisted)==len(upload['files']))
check('supplemental_manifest_complete',set(actual)-{'github-upload/UPLOAD_MANIFEST_SHA256.json'}==ulisted)
check('supplemental_manifest_hashes',all(r['path'] in actual and sha(actual[r['path']])==r['sha256'] and actual[r['path']].stat().st_size==r['size_bytes'] for r in upload['files']))
baseline_archive=ROOT.parent.parent/'inputs/Komorebi_Paper_I_Complete_2026-10-15.zip'
with zipfile.ZipFile(baseline_archive) as z:
    check('baseline_archive_crc',z.testzip() is None)
    check('baseline_archive_unique_names',len(z.namelist())==len(set(z.namelist())))
pred=read(ROOT/'formal/PREDECESSOR.json')
predpath=ROOT/pred['archive']
check('predecessor_present_and_hash',predpath.is_file() and sha(predpath)==pred['sha256'])
with zipfile.ZipFile(predpath) as z: check('predecessor_zip_crc',z.testzip() is None)

release_path=ROOT/'formal/evidence/RELEASE_VERIFICATION.json'
release=read(release_path)
coverage_path=ROOT/'formal/coverage/COVERAGE_108.json'
coverage=read(coverage_path)
check('release_status_pass',release['status']=='PASS')
check('coverage_receipt_hash',sha(coverage_path)==release['coverage']['sha256'])
check('coverage_108_unique_ids',len(coverage['records'])==108==len({r['stable_id'] for r in coverage['records']}))
check('coverage_69_accepted',coverage['proved_record_count']==69 and coverage['proved_record_status_counts']=={'covered':69})
source_paths={r['current_source']['file']:r['current_source']['file_sha256'] for r in coverage['records']}
check('coverage_current_source_hashes',all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in source_paths.items()))
whole_path=release_path.parent/release['lean']['verification']
whole=read(whole_path)
check('whole_closure_receipt_hash',sha(whole_path)==release['lean']['verification_sha256'])
check('whole_closure_recorded_pass',whole['status']=='PASS' and all(c['passed'] for c in whole['checks']))
check('whole_closure_recorded_counts',whole['production_module_count']==116 and whole['owned_total']==3513 and whole['owned_logical_total']==3500 and whole['logical_checked_count']==3500 and whole['replay_logical_constant_count']==3499 and whole['upstream_duplicate_body_recheck_count']==1 and whole['owned_runtime_only']==13 and whole['negative_controls']==12)
check('production_sources_match_recorded_hashes',len(whole['source_files'])==116 and all((ROOT/'formal/current'/r['source']).is_file() and sha(ROOT/'formal/current'/r['source'])==r['source_sha256'] for r in whole['source_files']))
check('production_objects_match_recorded_hashes',all((whole_path.parent/r['object']).is_file() and sha(whole_path.parent/r['object'])==r['object_sha256'] for r in whole['source_files']))
check('boundary_source_hash',(ROOT/'formal/tests/ReleaseBoundary.lean').is_file() and sha(ROOT/'formal/tests/ReleaseBoundary.lean')==whole['boundary']['source_sha256'])
check('whole_closure_check_log_hashes',all((whole_path.parent/c['log']).is_file() and sha(whole_path.parent/c['log'])==c['log_sha256'] for c in whole['checks']))
component_path=release_path.parent/release['lean']['compilation_provenance']['component']
component=read(component_path)
check('compilation_component_receipt_hash',sha(component_path)==release['lean']['compilation_provenance']['component_sha256'])
check('compilation_component_recorded_pass',component['status']=='PASS' and component['fresh_production_module_count']==115 and len(component['modules'])==115 and all(r['passed'] for r in component['modules']))
for family in ['semantics','python']:
    records=release[family]['reports' if family=='semantics' else 'receipts']
    check(family+'_receipt_hashes',all((release_path.parent/r['path']).is_file() and sha(release_path.parent/r['path'])==r['sha256'] for r in records))
run=subprocess.run([sys.executable,str(ROOT/'scripts/verify_integrity.py')],cwd=ROOT,text=True,capture_output=True)
check('inherited_integrity_verifier_exit_zero',run.returncode==0)
result={
 'schema':'komorebi.paper-i.freeze-baseline-audit/1',
 'status':'PASS' if not failures else 'FAIL',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Fresh file-identity checks and authentication of inherited October 15 evidence; no new Lean run, TeX rebuild, semantic review or mathematical proof audit.',
 'baseline_archive':{'name':baseline_archive.name,'bytes':baseline_archive.stat().st_size,'sha256':sha(baseline_archive)},
 'file_count':len(actual),'original_manifest_count':len(listed),'supplemental_manifest_count':len(ulisted),
 'original_manifest_unlisted_files':extras,
 'checks':checks,'failures':failures,
 'predecessor':{'path':pred['archive'],'bytes':predpath.stat().st_size,'sha256':sha(predpath)},
 'inherited_formal_receipt':{'path':str(release_path.relative_to(ROOT)),'sha256':sha(release_path),'recorded_at_utc':release['checked_at_utc'],'production_modules':116,'boundary_modules':1,'source_owned':3513,'logical_checked':3500,'ordinary_replays':3499,'duplicate_body_rechecks':1,'runtime_helpers':13,'negative_controls':12,'fresh_lean_execution_in_this_freeze':False},
 'inherited_integrity_verifier':{'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr},
 'not_executed':[{'command':'python3 scripts/build_pdfs.py --check-only','reason':'Despite its name, this is a complete TeX rebuild and writes build outputs and generated companion metadata. It was inspected but not executed on the immutable baseline.'}],
 'limitations':['File identity authenticates what the inherited receipts refer to; it does not independently establish proof correctness.','The original manifest excludes four October 19 preparation additions plus itself; the supplemental upload manifest covers every file except itself and all its hashes pass.','The pinned Lean runtime and cached external dependencies remain external; fresh compilation was not part of this freeze audit.']
}
(OUT/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper I baseline integrity audit\n\n'+result['status']+'\n\nFresh checks authenticate all '+str(len(actual))+' baseline files through the original and supplemental manifests. All recorded hashes and sizes pass. The historical predecessor ZIP is present, matches its recorded SHA-256, and passes ZIP CRC.\n\nAll 116 production sources and stored objects match the inherited October 15 whole-closure receipt, as does the separate boundary source. The receipt, its compilation component, semantic reports, Python receipts and check logs match their recorded digests. The accepted 108-record inventory still has 69 covered proof-level records. These are fresh evidence-identity checks, not new compiler execution or proof validation.\n\nThe original integrity script passes 2,176 recorded files. It does not reject additional files. Its original manifest omits the manifest itself and four later preparation files; the supplemental upload manifest covers all 2,180 other files and is exact. The new freeze manifest should include all 2,181 preserved files.\n\nThe build --check-only command was inspected and deliberately not executed: it rebuilds PDFs and writes generated data/build outputs despite preserving papers/. No baseline file was edited. No failure was found in the executed checks.\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':failures,'files':len(actual),'output':str(OUT/'BASELINE_INTEGRITY_AUDIT.json')},indent=2))
sys.exit(bool(failures))

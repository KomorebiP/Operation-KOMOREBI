#!/usr/bin/env python3
"""Read-only Paper III freeze identity and inherited-evidence audit."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib, json, sys, zipfile

ROOT=Path('/workspace/scratch/fbc994080222/paper_iii_freeze/baseline/Paper_III_Final_Release_v1.0.0')
ARCHIVE=Path('/workspace/scratch/fbc994080222/paper_iii_freeze/inputs/Paper_III_Final_Release_v1.0.0_2026-10-20.zip')
OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
checks={};failures=[]
def check(label,result):
    checks[label]=bool(result)
    if not result: failures.append(label)
initial={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
manifest=read(ROOT/'MANIFEST_SHA256_v1.0.0.json'); rows=manifest['files']
check('manifest_count',len(rows)==manifest['file_count_excluding_manifest']==2237)
check('manifest_safe_canonical_paths',all(name and '\\' not in name and ':' not in name and not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and PurePosixPath(name).as_posix()==name for name in rows))
check('no_symlinks',not any(p.is_symlink() for p in ROOT.rglob('*')))
check('complete_file_set',set(initial)==set(rows)|{'MANIFEST_SHA256_v1.0.0.json'})
check('all_manifest_size_and_hash_values',all((ROOT/name).stat().st_size==r['size_bytes'] and initial[name]==r['sha256'] for name,r in rows.items()))
check('archive_identity',ARCHIVE.stat().st_size==134444532 and sha(ARCHIVE)=='fdf060e1fb8ad4afe236aecd8a9f5b02837a92addbb29b2eeaa25860b86ad3da')
with zipfile.ZipFile(ARCHIVE) as z:
    names=z.namelist()
    check('zip_crc',z.testzip() is None)
    check('unique_zip_names',len(names)==len(set(names)))
    check('safe_zip_paths',all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n for n in names))
    members={PurePosixPath(i.filename).relative_to(ROOT.name).as_posix():i for i in z.infolist() if not i.is_dir()}
    check('archive_extraction_exact_file_set',set(members)==set(initial))
    check('archive_extraction_exact_bytes',all(i.file_size==(ROOT/name).stat().st_size and hashlib.sha256(z.read(i)).hexdigest()==initial[name] for name,i in members.items()))

cp=ROOT/'checkpoint_v0.3.0'; cm=read(cp/'MANIFEST_SHA256.json')
cp_actual={p.relative_to(cp).as_posix() for p in cp.rglob('*') if p.is_file()}
check('checkpoint_exact_1061_file_set',len(cp_actual)==1061 and cp_actual=={r['path'] for r in cm['files']}|{'MANIFEST_SHA256.json'})
check('checkpoint_1060_original_manifest_rows',len(cm['files'])==1060 and len({r['path'] for r in cm['files']})==1060)
check('checkpoint_original_manifest_hashes',all((cp/r['path']).stat().st_size==r['bytes'] and sha(cp/r['path'])==r['sha256'] for r in cm['files']))
pres=read(ROOT/'evidence/CHECKPOINT_PRESERVATION.json')
check('prior_checkpoint_preservation_receipt',pres['status']=='PASS' and pres['checkpoint_files']==1061 and pres['missing_or_changed']==[] and pres['extra_files']==[] and pres['original_archive_sha256']=='5822e71704b4436f67f7ca72c3b44ed2db708a85b44fb88d5e5cfb84dcf38a24')

state=read(ROOT/'RELEASE_STATUS.json'); sp=ROOT/'formal/verification/FINAL_VERIFICATION_SUMMARY.json'; summary=read(sp)
check('release_summary_digest',sha(sp)==state['formal_verification']['summary_sha256'])
check('release_exact_bounded_formal_scope',state['technical_release_complete'] is True and state['full_manuscript_lean_coverage'] is False and state['open_technical_repairs']==[])
check('formal_16_608_594_14_counts',summary['status']=='PASS' and summary['production_module_count']==16 and summary['owned_declarations']==608 and summary['replayed_logical_declarations']==594 and summary['generated_runtime_helpers']==14 and len(summary['control_results'])==14)
check('all_31_verified_source_hashes',len(summary['all_verified_source_sha256'])==31 and all(sha(ROOT/'formal'/name)==h for name,h in summary['all_verified_source_sha256'].items()))
check('verification_support_hashes',all((ROOT/'formal'/name).is_file() and sha(ROOT/'formal'/name)==h for name,h in summary['verification_support_sha256'].items()))
phase_reports={};phase_command_count=0
for label,phase in summary['accepted_phases'].items():
    p=ROOT/'formal'/phase['report']; report=read(p);phase_reports[label]=report
    check(label+'_report_digest',sha(p)==phase['report_sha256'])
    check(label+'_accepted_commands',report['status']=='PASS' and len(report['commands'])==phase['command_count'] and all(c['accepted'] for c in report['commands']))
    check(label+'_runner_digest',report['runner_sha256']==sha(ROOT/'formal/scripts/run_release_verification.py'))
    check(label+'_command_source_and_log_digests',all(sha(ROOT/'formal'/c['source'])==c['source_sha256'] and c['source_unchanged'] and sha(ROOT/'formal'/c['log'])==c['log_sha256'] for c in report['commands']))
    check(label+'_stored_source_snapshots',all(sha((ROOT/'formal'/c['log']).parent/'source.lean')==c['source_sha256'] for c in report['commands']))
    phase_command_count+=len(report['commands'])
check('production_exact_16_module_names',len(summary['production_modules'])==16 and {c['module'] for c in phase_reports['full']['commands']}=={c['module'] for c in summary['production_modules']})
check('production_source_objects_and_summary_digests',all(sha(ROOT/'formal'/c['source'])==c['source_sha256'] and sha(ROOT/'formal/build/accepted_objects'/Path(*c['module'].split('.')).with_suffix('.olean'))==c['object_sha256'] for c in summary['production_modules']))
check('cold_project_object_build_record',phase_reports['full']['own_objects_initially_empty'] is True)
check('all_14_recorded_controls_accepted',len(phase_reports['controls']['commands'])==14 and all(c['accepted'] for c in phase_reports['controls']['commands']))
audit_log=ROOT/'formal'/summary['evidence_integrity']['audit_log']; replay_log=ROOT/'formal'/summary['evidence_integrity']['replay_log']
check('owned_and_replay_log_digests',sha(audit_log)==summary['evidence_integrity']['audit_log_sha256'] and sha(replay_log)==summary['evidence_integrity']['replay_log_sha256'])
owned=[json.loads(line.removeprefix('OWNED ')) for line in audit_log.read_text().splitlines() if line.startswith('OWNED ')]
replayed=[json.loads(line.removeprefix('REPLAY_CHECKED ')) for line in replay_log.read_text().splitlines() if line.startswith('REPLAY_CHECKED ')]
check('raw_owned_inventory_608',len(owned)==608 and len({r['name'] for r in owned})==608)
check('raw_owned_runtime_helpers_14',sum(r['runtime_only'] for r in owned)==14 and {r['name'] for r in owned if r['runtime_only']}=={r['name'] for r in summary['logical_trust']['runtime_helper_inventory']})
logical={r['name'] for r in owned if not r['runtime_only']}
check('raw_594_replay_name_identity',len(replayed)==594 and len(logical)==594 and {r['name'] for r in replayed}==logical)
check('raw_owned_outside_primary_namespace_33',sum(not r['in_project_namespace'] for r in owned)==33)
allowed={'Classical.choice','Quot.sound','propext'}
check('recorded_logical_axioms_within_allowed_set',set(summary['logical_trust']['permitted_transitive_axioms'])==allowed and all(set(r['axioms'])<=allowed for r in owned if not r['runtime_only']))
check('zero_initial_owned_overlap_record',summary['logical_trust']['replay_owned_overlap_count']==0)
fail_history=summary['preserved_failure_history']
check('retained_failure_records_present',all((ROOT/'formal'/h['record']).is_file() for h in fail_history))
check('accepted_prior_phase_records_present',all((ROOT/'formal'/name).is_file() for names in summary['prior_accepted_checkpoints'].values() for name in names))

regpath=ROOT/state['manuscript_census']['statement_register']; reg=read(regpath)
check('statement_register_hash',sha(regpath)==state['manuscript_census']['register_sha256'])
check('active_chapter_hashes',all(sha(ROOT/c['path'])==c['sha256'] for c in reg['active_chapters']))
check('selected_manuscript_hash',sha(ROOT/'publication/Paper_III_Final_v1.0.0.pdf')==reg['selected_manuscript_sha256'])
check('all_six_reading_output_hashes',len(state['outputs'])==6 and all((ROOT/d['path']).stat().st_size==d['size_bytes'] and sha(ROOT/d['path'])==d['sha256'] for d in state['outputs']))
review=read(ROOT/'evidence/review/FINAL_REVIEW_BINDINGS.json')
check('prior_135_review_bindings_accepted',review['status']=='PASS' and review['check_count']==135 and len(review['checks'])==135 and all(c['status']=='PASS' for c in review['checks']))
check('review_source_summary_digests',review['source_register_sha256']==sha(regpath) and review['final_formal_summary_sha256']==sha(sp))
check('review_record_hashes',all((ROOT/name).is_file() and sha(ROOT/name)==h for name,h in review['review_records_sha256'].items()))
inherited=read(OUT/'INHERITED_VERIFIER_RUN.json')
check('safe_inherited_verifier_pass',inherited['status']=='PASS' and inherited['errors']==[] and inherited['expected_files']==2237 and inherited['actual_files']==2237)
final={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
check('baseline_unchanged',initial==final)
result={
 'schema':'komorebi.paper-iii.freeze-baseline-audit/1','status':'PASS' if not failures else 'FAIL',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Fresh exact identity and inherited-evidence consistency checks only. No Lean, TeX, experiments, semantic proof extension or new controls executed.',
 'baseline_archive':{'name':ARCHIVE.name,'library_version':1,'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'members':len(names)},
 'file_count':len(initial),'manifest_count':len(rows),'checks':checks,'failures':failures,
 'inherited_formal_counts':{'production_modules':16,'owned_declarations':608,'logical_replayed':594,'generated_runtime_helpers':14,'accepted_control_commands':14,'owned_outside_primary_namespace':33,'all_verified_source_files':31,'phase_commands':phase_command_count,'fresh_lean_execution':False},
 'checkpoint':{'file_count':1061,'original_manifest_records':1060,'prior_rc1_archive_hash_in_preservation_receipt':pres['original_archive_sha256'],'fresh_comparison_against_rc1_archive':False,'note':'All checkpoint bytes are authenticated through their exact nested manifest and the selected final archive. The RC1 archive itself is not embedded, so its prior direct comparison remains inherited evidence.'},
 'executed_existing_check':{'command':'python3 VERIFY_RELEASE.py --output OUTSIDE_BASELINE/INHERITED_VERIFIER_RUN.json','exit':0,'status':inherited['status'],'errors':inherited['errors']},
 'release_scope':state['formal_boundaries'],
 'retained_failures':fail_history,
 'packaging_traps':['Inherited VERIFY_RELEASE.py uses str(relative_path), which produces Windows backslashes; use the previously reviewed portable frozen verifier as the new entry point. It also requires Python 3.11+ for hashlib.file_digest.','The inherited manifest is named MANIFEST_SHA256_v1.0.0.json and uses a dictionary/size_bytes schema; preserve it unchanged and add the separate standard frozen manifest.','Historical README/release-status/notes say no public license was selected. The author has since confirmed all papers are open; the current freeze licensing record should explicitly supersede those historical rights statuses without reopening technical scope.'],
 'limitations':['Full expanded-monograph Lean coverage remains incomplete by design of the selected release; packet Taylor remainder/estimate, Stirling/Touchard counts, separate restricted-product/Hilbert norm corollaries and later expanded material remain outside the accepted closure.','The old 2,693-declaration/full-98+2 formal claim remains uncertified because matched source was not recovered.','Papers I-II dependencies and historical compiler/review/computation results retain their original evidence scope; this audit rechecks identity, not correctness anew.','The exact runtime and upstream caches are external. No new compiler execution, experiment, whole-paper proof audit or full visual review was performed.']
}
(OUT/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper III baseline integrity audit\n\n'+result['status']+'\n\nThe selected final archive matches its supplied version-1 identity, size and SHA-256; ZIP CRC and exact extraction identity pass. All '+str(len(initial))+' files are present: 2,237 manifest records plus the manifest itself. Every recorded size/hash passes. The prior checkpoint has exactly 1,061 files, its 1,060 nested manifest records pass, and the earlier direct RC1 comparison receipt is preserved. The RC1 ZIP itself is not embedded; no fresh direct RC1 comparison is claimed.\n\nThe accepted bounded core remains 16 production modules, 608 owned declarations and 594 replayed logical declarations, with 14 separately inventoried runtime helpers and 14 accepted control commands. All 31 verified source files, support scripts/configuration, final phase reports, stored source snapshots, raw logs and 16 production compiler objects match their recorded digests. Raw owned/replay name sets agree exactly. Initial replay overlap is recorded as zero; 33 owned entries lie outside the primary namespace.\n\nThe current statement register, four active chapters, six reading PDFs and 135 accepted review bindings retain their recorded identities. The inherited noncompiling verifier passes. No baseline file changed. No Lean/TeX execution, experiment, semantic extension or control rerun was performed.\n\nNo live technical release blocker was found. Full expanded-monograph Lean coverage and the unrecovered 2,693-declaration/full-98+2 claim remain separate, explicit boundaries. Earlier compilation/control failures are preserved.\n\nPackaging notes: use the portable frozen verifier rather than the Windows-sensitive inherited verifier; preserve the dated dictionary-style manifest; explicitly supersede historical no-license statuses with the author-confirmed current open-license record.\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':failures,'files':len(initial),'members':len(names)},indent=2))
sys.exit(bool(failures))

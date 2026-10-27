#!/usr/bin/env python3
"""Read-only exact multi-root Paper IV bundle and inherited-evidence audit."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, sys, zipfile

ROOT=Path('/workspace/scratch/fbc994080222/paper_iv_freeze/baseline')
CORE=ROOT/'Paper_IV_Verification_Closeout_v1.1.0'
ARCHIVE=ROOT.parent/'inputs/Paper_IV_Complete_v1.1.0_2026-10-19.zip'
OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
checks={};failures=[]
def check(label,result):
    checks[label]=bool(result)
    if not result: failures.append(label)
def safe(s):
    return isinstance(s,str) and bool(s) and '\\' not in s and ':' not in s and not PurePosixPath(s).is_absolute() and '..' not in PurePosixPath(s).parts and PurePosixPath(s).as_posix()==s
initial={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
check('baseline_no_symlinks',not any(p.is_symlink() for p in ROOT.rglob('*')))
bundle=read(ROOT/'BUNDLE_MANIFEST.json'); brows=bundle['files']
check('bundle_manifest_1444_unique_safe_paths',len(brows)==1444==len({r['path'] for r in brows}) and all(safe(r['path']) for r in brows))
check('bundle_manifest_exact_file_set',set(initial)=={r['path'] for r in brows}|{'BUNDLE_MANIFEST.json'})
check('bundle_all_sizes_and_hashes',all((ROOT/r['path']).stat().st_size==r['bytes'] and sha(ROOT/r['path'])==r['sha256'] for r in brows))
cm=read(CORE/'MANIFEST.json'); crows=cm['files']
core_actual={p.relative_to(CORE).as_posix() for p in CORE.rglob('*') if p.is_file()}
check('core_manifest_1408_unique_safe_paths',len(crows)==1408==len({r['path'] for r in crows}) and all(safe(r['path']) for r in crows))
check('core_manifest_exact_1409_file_set',core_actual=={r['path'] for r in crows}|{'MANIFEST.json'})
check('core_all_sizes_and_hashes',all((CORE/r['path']).stat().st_size==r['bytes'] and sha(CORE/r['path'])==r['sha256'] for r in crows))
check('archive_selected_identity',ARCHIVE.stat().st_size==55023201 and sha(ARCHIVE)=='fc55f0092138f3fe805a1f89a8c92b05b15cd0db7de39169c503ea24ec5df40c')
with zipfile.ZipFile(ARCHIVE) as z:
    names=z.namelist();members={i.filename:i for i in z.infolist() if not i.is_dir()}
    check('archive_crc',z.testzip() is None)
    check('archive_1445_unique_safe_members',len(names)==1445==len(set(names)) and all(safe(n) for n in names))
    check('archive_extraction_exact_multiroot_set',set(members)==set(initial))
    check('archive_extraction_exact_member_bytes',all(i.file_size==(ROOT/name).stat().st_size and hashlib.sha256(z.read(i)).hexdigest()==initial[name] for name,i in members.items()))

source=read(CORE/'verification/SOURCE_CONTRACT.json')
replay=read(CORE/'verification/lean_primary/REPLAY.json')
spec=read(CORE/source['contract_relative'])
report=read(CORE/'verification/CLOSEOUT_REPORT.json')
check('closeout_report_accepted_counts',report['status']=='FORMAL_CORE_AND_RECORDED_CHECKS_PASSED' and report['production_modules']==118 and report['mathematical_source_files_preserved']==119 and report['scoped_manuscript_results']==68 and report['map_rows']==151 and report['mapped_declarations']==1164 and report['compiler_controls']==6)
check('closeout_receipt_hashes',all((CORE/name).is_file() and sha(CORE/name)==h for name,h in report['receipt_hashes'].items()))
check('source_contract_bound_to_replay',replay['status']=='PASS' and replay['source_contract_sha256']==sha(CORE/'verification/SOURCE_CONTRACT.json'))
check('production_118_modules_ordered',len(source['production_modules'])==118 and len(set(source['production_modules']))==118 and source['production_modules']==[x['module'] for x in replay['production_done']] and replay['production_count']==118)
check('all_119_mathematical_source_hashes',len(source['source_sha256'])==119 and all((CORE/'formalization/lean'/name).is_file() and sha(CORE/'formalization/lean'/name)==h for name,h in source['source_sha256'].items()))
check('all_3_formal_configuration_hashes',len(source['configuration_sha256'])==3 and all(sha(CORE/'formalization/lean'/name)==h for name,h in source['configuration_sha256'].items()))
check('reviewed_target_contract_hash',sha(CORE/source['contract_relative'])==source['contract_sha256'])
check('target_contract_1164_unique_names',len(spec['targets'])==1164 and len({r['declaration'] for r in spec['targets']})==1164 and replay['reviewed_kinds_passed']==1164)
check('target_contract_kind_split',Counter(r['kind'] for r in spec['targets'])=={'theorem':953,'definition':211})
check('target_contract_151_rows',len({r['row_id'] for r in spec['targets']})==151)
check('namespace_census_2234_1999',spec['namespace_declarations']==2234 and spec['namespace_theorems']==1999 and replay['kernel_audit']['namespace_declarations']==2234)
check('production_source_receipt_hashes',all(sha(CORE/r['source'])==r['source_sha256'] for r in replay['production_done']))
check('all_production_object_hashes',all(sha(CORE/'verification/lean_primary/objects'/name)==h for r in replay['production_done'] for name,h in r['objects'].items()))
labels=[r['label'] for r in replay['checks']]
control_names=['positive','false','sorry','missing-premise','custom-axiom','wrong-kind']
required={'lean_version','reviewed_kinds','original_kernel_audit'}|{'compile_'+n for n in source['production_modules']}|{'control_'+n for n in control_names}
check('all_127_expected_check_labels',len(labels)==127==len(set(labels)) and set(labels)==required)
check('all_127_recorded_check_logs',all(sha(CORE/r['log'])==r['log_sha256'] and not r['timed_out'] and (r['label'].startswith('control_') or r['returncode']==0) for r in replay['checks']))
check('six_control_sources_and_recorded_passes',[r['name'] for r in replay['controls']]==control_names and all(r['passed'] and sha(CORE/'verification/lean_primary'/('Control_'+r['name'].replace('-','_')+'.lean'))==r['source_sha256'] for r in replay['controls']))
axioms=read(CORE/'verification/lean_primary/AXIOM_REPORTS.json')
allowed={'Classical.choice','Quot.sound','propext'}
check('exact_1164_target_axiom_report_names',axioms['names']==1164 and set(axioms['reports'])=={r['declaration'] for r in spec['targets']})
check('all_target_axioms_allowed',set(axioms['allowed_union'])==allowed and all(set(a)<=allowed for a in axioms['reports'].values()))
mapping=read(CORE/'verification/SOURCE_MAP_CHECK.json')
check('recorded_68_result_mapping',mapping['status']=='PASS' and mapping['full_scoped_results']==68 and mapping['map_rows']==151 and mapping['mapped_targets']==1164 and mapping['mapped_theorems']==953 and mapping['mapped_definitions']==211)
mapgate=CORE/'publication_baseline/source/complete/original_snapshot/lean_release/PRSC_IV/verification/check_release.py'
check('recorded_mapping_verifier_digest',sha(mapgate)==mapping['verifier_sha256'])

finite=read(CORE/'verification/finite_primary/FINITE_REPLAY.json')
check('five_recorded_finite_gates',finite['status']=='PASS' and finite['baseline_files_unchanged']==836 and [r['name'] for r in finite['checks']]==['algebra_exact','exact_visual','original_tables','strengthened','original_paper'] and all(r['status']=='PASS' and r['returncode']==0 and not r['timed_out'] for r in finite['checks']))
check('finite_gate_log_and_result_hashes',all((sha(CORE/'verification/finite_primary'/r['log'])==r['log_sha256']) and ('result' not in r or sha(CORE/'verification/finite_primary'/r['result'])==r['result_sha256']) for r in finite['checks']))
check('finite_818_rows_4_brackets',finite['rational_tables_and_brackets']=={'status':'PASS','rows':818,'brackets':4})
for name,want in [('VERIFIER_TESTS.json',42),('INTEGRITY_TESTS.json',10)]:
    d=read(CORE/'verification'/name)
    check('recorded_'+name,d['status']=='PASS' and d['tests_run']==want and not(d['failures'] or d['errors'] or d['skipped']))
pres=read(CORE/'verification/BASELINE_PRESERVATION.json');pbase=CORE/'publication_baseline'
pactual={p.relative_to(pbase).as_posix() for p in pbase.rglob('*') if p.is_file()}
check('publication_baseline_exact_836_files',pres['status']=='PASS' and pres['count']==836==len(pres['files'])==len(pactual) and pactual=={r['path'] for r in pres['files']})
check('publication_baseline_preserved_hashes',all((pbase/r['path']).stat().st_size==r['bytes'] and sha(pbase/r['path'])==r['sha256'] for r in pres['files']))
old=read(pbase/'MANIFEST_SHA256.json');missing_old=[r for r in old['files'] if not (pbase/r['path']).is_file()]
check('obsolete_font_manifest_gap_exactly_retained',len(old['files'])==908 and len(missing_old)==73 and all(Path(r['path']).suffix.lower() in {'.otf','.ttf'} for r in missing_old))
check('all_surviving_old_manifest_entries_match',all((pbase/r['path']).stat().st_size==r['bytes'] and sha(pbase/r['path'])==r['sha256'] for r in old['files'] if (pbase/r['path']).is_file()))
historical_zips=list(pbase.rglob('*.zip'))
crc_results={}
for p in historical_zips:
    with zipfile.ZipFile(p) as z:crc_results[p.relative_to(CORE).as_posix()]=z.testzip() is None
check('historical_archives_present_and_crc_pass',len(historical_zips)==2 and all(crc_results.values()))

deliver=ROOT/'Delivery_Receipts';delivery_files=[p for p in deliver.rglob('*') if p.is_file()]
check('all_33_delivery_receipts_retained',len(delivery_files)==33)
for name in ['iv_extracted_integrity_before.json','iv_extracted_integrity_after.json','iv_original_integrity.json']:
    d=read(deliver/name)
    check('recorded_'+name,d['status']=='PASS' and d['integrity']['manifest_sha256']==sha(CORE/'MANIFEST.json') and d['integrity']['files']==1408 and d['evidence']['production_modules']==118 and d['evidence']['reviewed_targets']==1164)
failed_consumer=read(deliver/'failed_consumer_30s/RESULT.json');passed_consumer=read(deliver/'extracted_consumer_pass/RESULT.json')
check('failed_30s_consumer_preserved',failed_consumer['status']=='FAILED' and failed_consumer['timed_out'] is True)
check('successful_300s_consumer_preserved',passed_consumer['status']=='PASS' and passed_consumer['returncode']==0 and passed_consumer['timed_out'] is False and passed_consumer['timeout_seconds']==300)
check('same_consumer_source_and_pass_log_hash',sha(deliver/'failed_consumer_30s/ExtractedConsumer.lean')==sha(deliver/'extracted_consumer_pass/ExtractedConsumer.lean')==passed_consumer['source_sha256'] and sha(deliver/'extracted_consumer_pass/consumer.log')==passed_consumer['log_sha256'])
fresh=read(deliver/'fresh_extraction_tests/RESULT.json')
check('five_recorded_extraction_gates',fresh['status']=='PASS' and [r['name'] for r in fresh['checks']]==['frozen_records','typed_source_contract','verifier_controls','integrity_controls','finite_replay'] and all(r['returncode']==0 and not r['timed_out'] for r in fresh['checks']))
check('extraction_gate_log_hashes',all(sha(deliver/'fresh_extraction_tests'/r['log'])==r['log_sha256'] for r in fresh['checks']))
lineage=read(CORE/'verification/readers/LATEST_READER_LINEAGE.json')
check('latest_three_reader_lineage_digests',len(lineage)==3 and all(sha(CORE/'readers'/r['name'])==r['source_file_sha256'] and sha(CORE/r['baseline_path'])==r['baseline_sha256'] for r in lineage))
visual=next(r for r in lineage if 'Visual' in r['name'])
check('visual_editable_source_boundary_retained',visual['different_text_pages']==[1,14,28] and 'not recovered' in (CORE/'FAILURES_AND_LIMITATIONS.md').read_text() and 'Exact later editable source was not recovered.' in (CORE/'RELEASE_SCOPE.md').read_text())
runout=(OUT/'INHERITED_BUNDLE_VERIFIER_STDOUT.txt').read_text()
check('safe_noncompiling_bundle_verifier_pass','COMPLETE_DELIVERY_PASS 1445 files' in runout and '"fresh_compiler_execution_in_this_command": false' in runout and not (OUT/'INHERITED_BUNDLE_VERIFIER_STDERR.txt').read_text())
final={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
check('baseline_unchanged',initial==final)
result={
 'schema':'komorebi.paper-iv.freeze-baseline-audit/1','status':'PASS' if not failures else 'FAIL',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Fresh exact multi-root bundle identity and inherited compiler/finite/delivery receipt authentication only. No new Lean, TeX, experiments, semantic audit or control rerun.',
 'archive':{'name':ARCHIVE.name,'library_version':0,'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'members':len(names)},
 'bundle_files':len(initial),'bundle_manifest_records':len(brows),'core_files':len(core_actual),'core_manifest_records':len(crows),'delivery_receipt_files':len(delivery_files),
 'checks':checks,'failures':failures,
 'accepted_recorded_scope':{'scoped_results':68,'map_rows':151,'production_modules':118,'mathematical_source_files':119,'formal_configuration_files':3,'reviewed_targets':1164,'mapped_theorems':953,'mapped_constructions':211,'namespace_declarations':2234,'namespace_theorems':1999,'compiler_controls':6,'compiler_check_logs':127,'finite_gates':5,'rational_rows':818,'brackets':4,'verifier_tests':42,'distribution_controls':10,'fresh_compiler_execution':False},
 'preserved_publication_baseline':{'files':836,'historical_manifest_rows':908,'historical_missing_font_entries':len(missing_old),'historical_manifest_is_current_inventory':False,'historical_zip_crc':crc_results},
 'historical_source_recovery_gap':'The later October 16 visual PDF is present, with differences recorded on pages 1, 14 and 28; exact later editable source remains unrecovered. The older editable baseline remains present. This is an archival source-recovery limitation, not a live proof or package-integrity blocker.',
 'executed_existing_check':{'command':'python3 -B verify_bundle.py','exit':0,'result':'COMPLETE_DELIVERY_PASS 1445 files; inner recorded evidence PASS; no fresh compiler execution'},
 'retained_failures':['The old 908-row publication manifest names 73 excluded font files; the concrete unchanged 836-file baseline is authenticated separately.','Earlier warning flag, verifier-fixture startup race and historical dependency availability reporter failures remain documented under FAILURES_AND_LIMITATIONS.md.','A supplementary same-source extraction consumer timed out at 30 seconds, then passed under the 300-second budget; both attempts are retained.','The earlier unsaved fixture-control API failure was not recovered; its replacement typed-interface verification has separate evidence.'],
 'packaging_traps':['The source archive is multi-root. Preserve outer START_HERE.md, verify_bundle.py, BUNDLE_MANIFEST.json and all Delivery_Receipts alongside the inner core.','Preserve the inner core MANIFEST.json and all core bytes unchanged; add a separate outer freeze manifest and portable verifier.','The original outer bundle verifier expects BUNDLE_MANIFEST.json and its own exclusion; an administrative adaptation must point to the new full outer manifest and exclude only that new manifest. The inner core verifier can remain unchanged.','Existing no-license or next-Paper-X statements are historical; the new outer index/license/ledger can supersede them without rewriting historical records.'],
 'limitations':['Source and receipt identity checks do not provide a new mathematical correctness audit.','Compiler evidence is inherited from October 19 with pinned external runtime and reused dependencies; no cold Mathlib build, independent kernel or native Windows execution is claimed.','No universal zero simplicity, positivity of every reduced zero, full displacement expansion or zeta functional equation is asserted.','Standard fact 11.1 stays outside the 68-result mapping.']
}
(OUT/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper IV multi-root baseline integrity audit\n\n'+result['status']+'\n\nThe selected complete archive matches its version-0 size/hash, passes CRC, and all 1,445 members match the extracted multi-root baseline byte for byte. The outer manifest authenticates 1,444 records plus itself. The inner core has exactly 1,409 files: 1,408 manifest records plus MANIFEST.json. All 33 external delivery records are present and covered.\n\nAccepted recorded scope remains 68 manuscript results, 151 mapping rows, 118 production modules, 1,164 target declarations, six compiler controls and a 2,234-declaration namespace audit. All 119 mathematical sources, three configurations, production objects and 127 compiler logs match the preserved source/receipt contract. Five finite suites and their exact output hashes remain authenticated, including 818 rational rows and four brackets. No finite suite or compiler control was rerun.\n\nThe unchanged 836-file publication baseline is authenticated by the concrete preservation inventory. Its obsolete 908-row manifest still names exactly 73 excluded font files; every surviving recorded file matches. Both nested historical ZIPs pass CRC. The old missing-font failure is historical, not a failure of the selected complete bundle.\n\nFresh-extraction receipts and the failed 30-second consumer attempt followed by the successful same-source 300-second retry are preserved and authenticated. The later visual PDF remains present; its exact later editable source is unrecovered. Older editable sources remain present. That recovery gap is distinct from proof/package blockers.\n\nThe original complete-bundle verifier was inspected and passed without compilation. No baseline byte changed. No new Lean/TeX execution, experiments, semantic proof review or controls rerun occurred. No live technical or package-integrity blocker was found.\n\nFreeze the entire multi-root bundle, keep the inner core unchanged and add the new outer manifest/license/index. Only the outer verifier needs the new manifest name/self-exclusion; inner recorded checks can remain unchanged.\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':failures,'bundle_files':len(initial),'core_files':len(core_actual),'delivery_receipt_files':len(delivery_files)},indent=2))
sys.exit(bool(failures))

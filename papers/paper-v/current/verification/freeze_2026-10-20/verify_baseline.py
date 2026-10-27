#!/usr/bin/env python3
"""Read-only Paper V freeze identity and inherited scope/evidence audit."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib, json, re, sys, zipfile

ROOT=Path('/workspace/scratch/fbc994080222/paper_v_freeze/baseline/Paper_V_Final_Release_v1.2.0')
ARCHIVE=ROOT.parent.parent/'inputs/Paper_V_Final_Release_v1.2.0_2026-10-20.zip'
OUT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'verification/closeout_2026-10-20'
SNAPSHOT=ROOT/'source/complete/original_snapshot'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
checks={};failures=[]
def check(label,result):
    checks[label]=bool(result)
    if not result: failures.append(label)
def safe(name):
    return bool(name) and '\\' not in name and ':' not in name and not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and PurePosixPath(name).as_posix()==name
initial={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
manifest=read(ROOT/'MANIFEST_SHA256.json');rows=manifest['files']
check('strict_manifest_schema_retained',manifest['schema']=='komorebi.strict_manifest.v1' and set(manifest)<= {'schema','checkpoint','scope','edition','generated_at_utc','files'})
check('manifest_1518_unique_safe_rows',len(rows)==1518==len({r['path'] for r in rows}) and all(safe(r['path']) for r in rows))
check('exact_1519_file_set',set(initial)=={r['path'] for r in rows}|{'MANIFEST_SHA256.json'})
check('no_symlinks',not any(p.is_symlink() for p in ROOT.rglob('*')))
check('all_manifest_sizes_and_hashes',all((ROOT/r['path']).stat().st_size==r['bytes'] and sha(ROOT/r['path'])==r['sha256'] for r in rows))
check('archive_selected_identity',ARCHIVE.stat().st_size==92741315 and sha(ARCHIVE)=='17fc9943b602f9ff43acd33a98ff7978fceebcd92f283d4bf0cd1019732cae54')
with zipfile.ZipFile(ARCHIVE) as z:
    names=z.namelist()
    check('archive_crc',z.testzip() is None)
    check('archive_1519_safe_unique_members',len(names)==1519==len(set(names)) and all(safe(n) for n in names))
    members={PurePosixPath(i.filename).relative_to(ROOT.name).as_posix():i for i in z.infolist() if not i.is_dir()}
    check('archive_extraction_exact_file_set',set(members)==set(initial))
    check('archive_extraction_exact_bytes',all(i.file_size==(ROOT/n).stat().st_size and hashlib.sha256(z.read(i)).hexdigest()==initial[n] for n,i in members.items()))

edition=read(ROOT/'EDITION.json');status=read(EVIDENCE/'RELEASE_STATUS.json')
check('release_closed_no_live_blocker',status['status']=='CLOSED_WITHIN_STATED_SCOPE' and status['remaining_release_blockers']==[])
check('reader_hashes_pages_and_total',len(edition['documents'])==3 and sum(r['pages'] for r in edition['documents'])==edition['total_pages']==234 and all((ROOT/r['path']).stat().st_size==r['bytes'] and sha(ROOT/r['path'])==r['sha256'] for r in edition['documents']))
check('reader_all_delivered_copies_identical',all(sha(ROOT/'publication/pdfs'/Path(r['path']).name)==r['sha256'] and sha(ROOT/'editable'/r['role']/Path(r['path']).name)==r['sha256'] for r in edition['documents']))
pres=read(EVIDENCE/'SOURCE_PRESERVATION.json')
check('source_preservation_receipt_bound',pres['status']=='PASS' and all(sha(ROOT/pres[k]['path'])==pres[k]['sha256'] for k in ['baseline','current']))
check('source_preservation_119_118_83_scope',pres['numbered_records']==119 and pres['byte_identical_numbered_records']==118 and pres['proof_environments']==83 and pres['all83_proof_bodies_byte_identical'] and len(pres['changed_records'])==1 and pres['changed_records'][0]['label']==['sf:gibbs_behavior'])
proof_pattern=r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}'
before_proofs=re.findall(proof_pattern,(ROOT/pres['baseline']['path']).read_text(),re.S)
after_proofs=re.findall(proof_pattern,(ROOT/pres['current']['path']).read_text(),re.S)
check('all_83_proof_body_bytes_match_selected_predecessor',len(before_proofs)==len(after_proofs)==83 and before_proofs==after_proofs)
check('all_29_formal_project_files_preserved',len(pres['formal_files_unchanged'])==29 and all(sha(ROOT/r['path'])==r['sha256'] for r in pres['formal_files_unchanged']))
check('formal_20_result_scope_not_broader_83_proofs',edition['formal_contract']['scoped_manuscript_results']==20 and edition['formal_contract']['fresh_lean_execution'] is False and edition['traditional']['proof_records']==83 and edition['traditional']['core_proofs']==20 and edition['traditional']['development_proofs']==63 and status['formal_scope']==edition['formal_contract'])
candidate=read(SNAPSHOT/'verification/candidate_contract.json');scope=read(SNAPSHOT/'verification/scope_contract.json');manuscript=read(SNAPSHOT/'verification/manuscript_contract.json')
check('inherited_20_complete_scoped_statements',scope['manuscript_result_count']==20 and len(scope['results'])==20 and all(r['status']=='complete_scoped_statement' for r in scope['results']) and len(manuscript['result_numbers'])==20)
check('candidate_225_unique_targets',len(candidate['theorem_targets'])==225==len({r['declaration'] for r in candidate['theorem_targets']}))
check('candidate_28_frozen_source_config_hashes',len(candidate['source_sha256'])==28 and all(sha(SNAPSHOT/name)==h for name,h in candidate['source_sha256'].items()))
check('25_lean_files_23_proof_modules',len(list((SNAPSHOT/'formalization/lean').rglob('*.lean')))==25 and len(list((SNAPSHOT/'formalization/lean/KomorebiPaperV').glob('*.lean')))==23)
targets=read(ROOT/'editable/lean_guide/generated/targets.json');axioms=read(ROOT/'editable/lean_guide/generated/inherited_axiom_records.json')
check('guide_targets_match_inherited_candidate',targets==candidate['theorem_targets'])
check('all_225_inherited_axiom_records_allowed',len(axioms)==225 and set(axioms)=={r['declaration'] for r in candidate['theorem_targets']} and all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()))
audit_text=(SNAPSHOT/'verification/lean_axiom_audit.log').read_text()
check('inherited_827_namespace_audit_sentinel',audit_text.count('PAPER_V_CANDIDATE_TARGET_AUDIT_PASS: 225 theorem targets; 827 namespace declarations')==1)
check('inherited_225_audit_directives',len(re.findall(r'^#print axioms ',(SNAPSHOT/'formalization/lean/KernelAudit.lean').read_text(),re.M))==225)

finite_dir=EVIDENCE/'finite';finite=read(finite_dir/'REPLAY_SUMMARY.json')
expected={'readiness','verifier','exact_models','second_block','numeric_pytest','annals','visual_symbolic','visual_extension'}
check('eight_recorded_finite_suites_pass',finite['status']=='PASS' and finite['errors']==[] and len(finite['suites'])==8 and {r['name'] for r in finite['suites']}==expected and all(r['status']=='PASS' and r['returncode']==0 for r in finite['suites']))
check('finite_runner_bound_to_recorded_execution',sha(ROOT/'scripts/replay_finite.py')==finite['runner_sha256'])
artifacts=read(finite_dir/'ARTIFACT_SHA256.json')
check('all_42_finite_artifact_hashes',len(artifacts)==42 and all(sha(finite_dir/name)==h for name,h in artifacts.items()))
inputs=read(finite_dir/'INPUT_SHA256.json');input_count=sum(len(g['files']) for g in inputs.values())
check('all_696_recorded_finite_input_hashes',input_count==696 and all(sha(ROOT/g['root_relative']/name)==h for g in inputs.values() for name,h in g['files'].items()))
finite_pres=read(finite_dir/'SOURCE_PRESERVATION.json')
check('finite_source_preservation_records_pass',all(g['status']=='PASS' and not (g['changed'] or g['missing'] or g['added']) for g in finite_pres.values()))
controls=read(EVIDENCE/'integrity_controls/FINAL_VERIFIER_CONTROLS.json')
check('inherited_21_integrity_control_methods',controls['status']=='PASS' and controls['test_methods']==21 and not(controls['failures'] or controls['errors'] or controls['skips']))
check('integrity_controls_exact_current_script_bindings',all(sha(ROOT/'scripts'/name)==h for name,h in controls['source_sha256'].items()))
check('integrity_control_transcript_21_ok',controls['transcript'].count(' ... ok\n')==21 and 'Ran 21 tests' in controls['transcript'])

originals=read(ROOT/'verification/run/ORIGINAL_SOURCE_HASHES.json');archive_contents={};historical_archive_records=[]
for relative,prefix in [('downloads/Paper_V_Complete_v1.1.0_With_Visual_Appendix.zip','complete'),('downloads/PSC_Paper_V_Annals_Human_Edition_Package.zip','annals')]:
    p=ROOT/relative
    with zipfile.ZipFile(p) as z:
        check('historical_'+prefix+'_zip_crc',z.testzip() is None)
        zfiles=[i for i in z.infolist() if not i.is_dir()]
        for i in zfiles:
            relative_parts=PurePosixPath(i.filename).parts[1:]
            archive_contents[prefix+'/'+'/'.join(relative_parts)]=hashlib.sha256(z.read(i)).hexdigest()
        historical_archive_records.append({'path':relative,'bytes':p.stat().st_size,'sha256':sha(p),'file_members':len(zfiles)})
check('all_598_original_archive_source_identities',len(originals)==598 and set(archive_contents)==set(originals) and all(archive_contents[name]==h for name,h in originals.items()))
old_differences=[]
for name,h in originals.items():
    p=ROOT/'source'/name
    if not p.is_file() or sha(p)!=h:old_differences.append({'path':name,'state':'missing' if not p.is_file() else 'changed'})
check('unpacked_historical_differences_are_only_documented_bytecode_and_repairs',len(old_differences)==15 and sum(r['state']=='missing' and r['path'].endswith('.pyc') for r in old_differences)==13 and {r['path'] for r in old_differences if r['state']=='changed'}=={'complete/original_snapshot/tests/test_verifier.py','complete/original_snapshot/verification/verify.py'})
gaps=read(ROOT/'provenance/HISTORICAL_RECOVERY_GAPS.json')
check('17_historical_artifact_gaps_explicit',gaps['missing_members']==17==len(gaps['missing_files']) and all(safe(r['path']) for r in gaps['missing_files']) and gaps['exact_existing_matches_in_baseline']==0)
check('all_17_historical_named_artifacts_still_absent',all(not (ROOT/r['path']).is_file() for r in gaps['missing_files']))

pdf_replay=read(EVIDENCE/'ISOLATED_PDF_REPLAY.json');geometry=read(EVIDENCE/'FINAL_GEOMETRY_AND_LINKS.json')
check('isolated_three_reader_replay_record_pass',pdf_replay['status']=='PASS' and len(pdf_replay['documents'])==3 and all(r['page_count_match'] and r['extracted_text_match'] for r in pdf_replay['documents']))
check('final_geometry_reader_bindings',geometry['status']=='PASS' and all(sha(ROOT/'papers'/r['file'])==r['sha256'] for r in geometry['documents']))
license_status=read(ROOT/'LICENSE_STATUS.json')
check('current_open_license_status',license_status['status']=='OPEN_LICENSES_APPLIED')
verified=read(OUT/'INHERITED_RELEASE_VERIFIER_RUN.json')
check('existing_readonly_release_verifier_pass',verified['status']=='PASS' and verified['fresh_lean_execution'] is False)
final={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
check('baseline_unchanged',initial==final)
result={
 'schema':'komorebi.paper-v.freeze-baseline-audit/1','status':'PASS' if not failures else 'FAIL',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Fresh package/source/evidence identity checks only; no new Lean, TeX, finite suite, experiment or control execution.',
 'archive':{'name':ARCHIVE.name,'library_version':1,'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'members':len(names)},
 'file_count':len(initial),'manifest_records':len(rows),'checks':checks,'failures':failures,
 'formal_scope':{'scoped_results':20,'broader_prose_proof_records':63,'total_existing_proof_environments':83,'targets':225,'proof_modules':23,'lean_files':25,'formal_project_files':29,'namespace_declarations':827,'historical_lean_date':'2026-09-06','fresh_lean_execution':False},
 'recorded_bounded_evidence':{'finite_suites':8,'finite_input_hashes':input_count,'finite_artifact_hashes':42,'strict_verifier_control_methods':21,'control_source_sha256':controls['source_sha256'],'fresh_suites_or_control_rerun':False},
 'historical_original_source_archives':historical_archive_records,
 'historical_original_source_identity_count':598,
 'current_unpacked_differences_from_october6_inventory':old_differences,
 'unpacked_difference_interpretation':'Thirteen excluded Python bytecode-cache files and two subsequently repaired verifier/test files differ from the old inventory. The original 598 identities remain recoverable byte for byte inside the two preserved historical ZIPs. This is separate from the 17 October 5 recovery gaps.',
 'historical_recovery_gap_count':17,
 'executed_existing_check':{'command':'python3 -B scripts/verify_release.py --report OUTSIDE_BASELINE/INHERITED_RELEASE_VERIFIER_RUN.json','exit':0,'status':verified['status'],'fresh_lean_execution':False},
 'minimal_freeze_recommendation':'Keep both verifier scripts byte-identical and regenerate MANIFEST_SHA256.json using its existing komorebi.strict_manifest.v1 schema and allowed metadata keys. The evidence checker contains no hardcoded root-manifest digest. Do not add unsupported count/self_excluded keys or replace the schema with Paper I format. Preserve the old manifest under the dated before directory.',
 'limitations':['The 20-result inherited Lean contract does not formalize all 83 prose proof environments; the 63-record broader part is explicitly outside full Lean coverage.','Seventeen missing October 5 verification artifacts are historical raw runner/log/result/verification-figure gaps, not missing current authored manuscripts, mathematical figures or Lean sources. No replacements are relabeled as historical evidence.','Existing compiler, finite-suite, verifier-control and PDF-replay results retain their original dates; this audit authenticates their bindings, not correctness through new execution.','The two edge-recovery conjectures remain open.','No whole-paper semantic reproof, new proof scope or native Windows execution is claimed.']
}
(OUT/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper V baseline integrity audit\n\n'+result['status']+'\n\nThe selected version-1 archive matches its supplied size/hash, passes CRC, and matches all 1,519 extracted files. Its strict manifest authenticates 1,518 files plus itself. Existing read-only release verification passes, including reader copies, navigation, source preservation and recorded evidence.\n\nThe inherited formal contract remains 20 scoped results, 225 targets, 23 proof modules/25 Lean files and 827 namespace declarations, with no fresh Lean run. All 29 formal project files and 28 contract-bound source/configuration hashes match. All 83 current proof bodies match the selected repaired predecessor; 118/119 numbered records remain unchanged, with the contextual Gibbs statement separately repaired as recorded. The broader 63 prose proofs do not enlarge Lean coverage.\n\nThe eight accepted bounded suites retain 696 matching input hashes and 42 matching artifact hashes. The 21 strict-verifier controls bind the exact unchanged verifier/test sources. These suites and controls were not rerun.\n\nBoth preserved historical ZIPs pass CRC and authenticate all 598 original source identities. Current unpacked source intentionally omits 13 .pyc cache files and contains two subsequent verifier/test repairs; this is distinct from the 17 unrecovered October 5 verification artifacts. All 17 missing historical paths remain explicitly inventoried, and current authored/formal sources are present.\n\nNo live package or source blocker was found. Keep both existing verifier scripts unchanged and regenerate the root manifest in its current strict schema, which rejects unknown metadata fields. No old root-manifest digest adapter is needed. No baseline byte changed and no Lean/TeX/finite/control execution occurred.\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':failures,'files':len(initial),'original_archived_identities':len(originals)},indent=2))
sys.exit(bool(failures))

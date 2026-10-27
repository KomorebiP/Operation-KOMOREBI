#!/usr/bin/env python3
"""Read-only Paper VI freeze identity and inherited-evidence audit."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib, json, re, sys, zipfile

ROOT=Path('/workspace/scratch/fbc994080222/paper_vi_freeze/baseline/Paper_VI_Final_Release_v1.0.0')
ARCHIVE=ROOT.parent.parent/'inputs/Paper_VI_Final_Release_v1.0.0_2026-10-20.zip'
OUT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'verification/closeout_2026-10-20'
SNAPSHOT=ROOT/'source/complete/original_snapshot'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def sha_text(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def walk(value):
    if isinstance(value,dict):
        yield value
        for v in value.values(): yield from walk(v)
    elif isinstance(value,list):
        for v in value: yield from walk(v)
def safe(s):
    return isinstance(s,str) and bool(s) and '\\' not in s and ':' not in s and not PurePosixPath(s).is_absolute() and '..' not in PurePosixPath(s).parts and PurePosixPath(s).as_posix()==s
checks={};failures=[]
def check(label,result):
    checks[label]=bool(result)
    if not result: failures.append(label)
initial={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
manifest=read(ROOT/'MANIFEST_SHA256.json');rows=manifest['files']
check('strict_manifest_schema',manifest['schema']=='komorebi.strict_manifest.v1' and set(manifest)<= {'schema','checkpoint','scope','edition','generated_at_utc','files'})
check('2135_unique_safe_manifest_rows',len(rows)==2135==len({r['path'] for r in rows}) and all(safe(r['path']) for r in rows))
check('exact_2136_file_set',set(initial)=={r['path'] for r in rows}|{'MANIFEST_SHA256.json'})
check('no_symlinks',not any(p.is_symlink() for p in ROOT.rglob('*')))
check('all_manifest_sizes_hashes',all((ROOT/r['path']).stat().st_size==r['bytes'] and initial[r['path']]==r['sha256'] for r in rows))
sums=[]
for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
    if not line or line.startswith('#'):continue
    h,name=line.split('  ',1);sums.append((name,h))
check('checksum_list_exact_2134_payload_set',len(sums)==2134==len({n for n,h in sums}) and {n for n,h in sums}==set(initial)-{'SHA256SUMS.txt','MANIFEST_SHA256.json'})
check('checksum_list_all_hashes',all(initial[n]==h for n,h in sums))
check('selected_archive_identity',ARCHIVE.stat().st_size==121525754 and sha(ARCHIVE)=='494d9efd3c58180daed966a8aae35986b286c072c1700318cc870dc9fad8ad6b')
with zipfile.ZipFile(ARCHIVE) as z:
    names=z.namelist();members={PurePosixPath(i.filename).relative_to(ROOT.name).as_posix():i for i in z.infolist() if not i.is_dir()}
    check('archive_crc',z.testzip() is None)
    check('2136_safe_unique_archive_members',len(names)==2136==len(set(names)) and all(safe(n) for n in names))
    check('archive_extraction_exact_file_set',set(members)==set(initial))
    check('archive_extraction_exact_bytes',all(i.file_size==(ROOT/name).stat().st_size and hashlib.sha256(z.read(i)).hexdigest()==initial[name] for name,i in members.items()))

edition=read(ROOT/'EDITION.json');status=read(EVIDENCE/'RELEASE_STATUS.json');pres=read(EVIDENCE/'SOURCE_PRESERVATION.json')
check('release_closed_no_blockers',status['status']=='CLOSED_WITHIN_STATED_SCOPE' and status['remaining_release_blockers']==[])
check('preservation_184_records_140_proofs',pres['status']=='PASS' and pres['main_source_byte_identical'] and pres['numbered_records_byte_identical']==184 and pres['proof_bodies_byte_identical']==140 and pres['mathematical_token_changes']==[])
check('main_source_exact_predecessor_bytes',sha(ROOT/pres['baseline']['path'])==pres['baseline']['sha256']==pres['current']['sha256']==sha(ROOT/pres['current']['path']) and (ROOT/pres['baseline']['path']).read_bytes()==(ROOT/pres['current']['path']).read_bytes())
proofs=re.findall(r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',(ROOT/pres['current']['path']).read_text(),re.S)
check('current_140_proof_environments',len(proofs)==140)
check('all_739_original_scientific_file_hashes',len(pres['original_source_files_unchanged'])==739 and all((ROOT/r['path']).stat().st_size==r['bytes'] and initial[r['path']]==r['sha256'] for r in pres['original_source_files_unchanged']))
check('all_3_preserved_archive_hashes',len(pres['original_download_archives_unchanged'])==3 and all((ROOT/r['path']).stat().st_size==r['bytes'] and initial[r['path']]==r['sha256'] for r in pres['original_download_archives_unchanged']))
archive_crcs={}
for row in pres['original_download_archives_unchanged']:
    with zipfile.ZipFile(ROOT/row['path']) as z:archive_crcs[row['path']]=z.testzip() is None
check('all_3_preserved_archive_crcs',all(archive_crcs.values()))
check('figure_and_exact_excerpt_preservation_hashes',all(initial[r['path']]==r['sha256'] for r in pres['figures_and_exact_excerpts_unchanged']))

formal=status['formal_scope'];contract=read(SNAPSHOT/'verification/source_contract.json');ledger=read(SNAPSHOT/'THEOREM_LEDGER.json')
check('formal_33_341_47_scope',formal['scoped_results']==33 and formal['theorem_declarations']==341 and formal['proof_modules']==47 and formal['namespace_declarations']==782 and formal['fresh_lean_execution'] is False and formal['full_paper_formalized'] is False)
check('33_complete_endpoint_ledger',len(ledger)==33 and all(r['status']=='complete_scoped_statement' and r['remaining']=='' for r in ledger))
check('341_unique_target_declarations',len(contract['theorem_targets'])==341==len({r['declaration'] for r in contract['theorem_targets']}))
check('all_53_formal_contract_source_hashes',len(contract['source_sha256'])==53 and all(sha(SNAPSHOT/name)==h for name,h in contract['source_sha256'].items()))
check('47_proof_modules_49_lean_files',len(list((SNAPSHOT/'formalization/lean/KomorebiPaperVI').glob('*.lean')))==47 and len(list((SNAPSHOT/'formalization/lean').rglob('*.lean')))==49)
targets=read(ROOT/'editable/lean_guide/generated/targets.json');axiom_rows=read(ROOT/'editable/lean_guide/generated/inherited_axiom_records.json')
axioms={r['declaration']:r['axioms'] for r in axiom_rows}
check('guide_target_ledger_identity',targets==contract['theorem_targets'] and ledger==read(ROOT/'editable/lean_guide/generated/result_ledger.json'))
check('341_inherited_axiom_records',len(axiom_rows)==len(axioms)==341 and set(axioms)=={r['declaration'] for r in targets} and all(set(a)<={'Classical.choice','Quot.sound','propext'} for a in axioms.values()))
log=(SNAPSHOT/'verification/lean_axiom_audit.log').read_text()
check('inherited_782_namespace_audit_sentinel',log.count('PAPER_VI_TARGET_AUDIT_PASS: 341 theorem targets; 782 namespace declarations')==1)
static=read(EVIDENCE/'STATIC_SOURCE_RECONCILIATION.json')
check('accepted_static_formal_reconciliation',static['status']=='PASS' and static['fresh_lean_kernel_run'] is False and static['counts']['scoped_result_records']==33 and static['counts']['theorem_targets']==341 and static['counts']['proof_modules']==47)

audit=read(EVIDENCE/'INHERITED_AUDIT_RECONCILIATION.json')
check('inherited_audit_scope_exact',audit['status']=='PASS_FOR_PROVENANCE_AND_STATIC_SCOPE' and audit['mathematical_sources_modified'] is False and audit['assembled_source_boundary']['direct_current_whole_file_hash_match_claimed'] is False)
bound_rows=[r for r in walk(audit) if {'path','sha256'}<=r.keys()]
check('all_inherited_review_artifact_pin_hashes',all(initial[r['path']]==r['sha256'] for r in bound_rows))
observed=[r for r in walk(audit) if {'path','observed_sha256'}<=r.keys()]
check('monograph_observed_preservation_pins',all(initial[r['path']]==r['observed_sha256'] for r in observed))
reconstructions=[]
for item in audit['disclosure_only_reconstructions']:
    text=(ROOT/item['current_corrected_fragment']['path']).read_text();unique=True
    for op in item['operations']:
        unique=unique and text.count(op['match_literal'])==1
        text=text.replace(op['match_literal'],op['replacement_literal'],1)
    reconstructions.append({'path':item['current_corrected_fragment']['path'],'unique_replacements':unique,'sha256':sha_text(text),'matches':sha_text(text)==item['reconstructed_sha256']==item['historically_reviewed_sha256']})
check('two_disclosure_only_reconstructions',len(reconstructions)==2 and all(r['unique_replacements'] and r['matches'] for r in reconstructions))
check('three_direct_fragment_pin_matches',len(audit['direct_fragment_pin_matches'])==3 and all(initial[r['path']]==r['sha256']==r['historically_reviewed_sha256'] and r['match'] for r in audit['direct_fragment_pin_matches']))

finite=read(EVIDENCE/'finite/FINITE_REPLAY.json')
expected={'source_integrity','static_pytest_verifier','original_sympy_exact','independent_exact_rational','numerical_companion','annals_numerical','strengthened_baseline','strengthened_expanded','monograph_figure_models','guide_extensions_exact','guide_plates'}
check('11_recorded_bounded_suites',finite['status']=='PASS_STATED_FINITE_SCOPE' and len(finite['runs'])==11 and {r['suite'] for r in finite['runs']}==expected and all(r['execution_exit']==r['manifest_validation_exit']==0 and r['run_status']=='completed' and r['counts']['status']=='PASS' for r in finite['runs']))
check('recorded_finite_runner_hash',initial['scripts/replay_finite.py']==finite['script_sha256'])
input_rows=[];output_rows=[];count_matches=[]
for run in finite['runs']:
    p=ROOT/run['manifest'];m=read(p);result=read(p.parent/'result.json')
    input_rows.extend(m['input_artifacts']);output_rows.extend(m['outputs'])
    count_matches.append(all(k=='count_type' or result.get(k)==v for k,v in run['counts'].items()))
check('all_finite_raw_result_summary_bindings',all(count_matches))
check('all_recorded_finite_input_hashes',all(safe(r['path']) and initial[r['path']]==r['sha256']==r['sha256_after'] for r in input_rows))
check('all_recorded_finite_output_hashes',all(safe(r['path']) and initial[r['path']]==r['sha256'] for r in output_rows))
controls=read(EVIDENCE/'integrity_controls/CONTROLS.json')
check('21_recorded_integrity_controls',controls['status']=='PASS' and controls['test_methods']==21 and controls['failures']==controls['errors']==controls['skips']==0)
check('integrity_control_source_bindings',all(initial['scripts/'+name]==h for name,h in controls['source_sha256'].items()))

check('three_reader_hashes_and_260_pages',len(edition['documents'])==3 and sum(r['pages'] for r in edition['documents'])==edition['total_pages']==260 and all((ROOT/r['path']).stat().st_size==r['bytes'] and initial[r['path']]==r['sha256'] for r in edition['documents']))
check('all_nine_reader_copies_identical',all(initial['publication/pdfs/'+Path(r['path']).name]==r['sha256'] and initial['editable/'+r['role']+'/'+Path(r['path']).name]==r['sha256'] for r in edition['documents']))
replay=read(EVIDENCE/'ISOLATED_PDF_REPLAY.json')
check('recorded_three_reader_byte_identical_rebuild',replay['status']=='PASS' and len(replay['documents'])==3 and all(r['build_returncode']==0 and r['page_count_match'] and r['extracted_text_match'] and r['pdf_byte_identical'] and r['shipped_pdf_sha256']==r['pdf_sha256'] for r in replay['documents']))
license=read(ROOT/'LICENSE_STATUS.json')
check('current_open_license_file_bindings',license['status']=='OPEN_LICENSES_APPLIED' and all(initial[name]==h for name,h in license['files'].items()))
verified=read(OUT/'INHERITED_RELEASE_VERIFIER_RUN.json')
check('safe_existing_release_verifier_pass',verified['status']=='PASS' and verified['fresh_lean_execution'] is False)
final={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
check('baseline_unchanged',initial==final)
result={
 'schema':'komorebi.paper-vi.freeze-baseline-audit/1','status':'PASS' if not failures else 'FAIL',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Fresh exact package/source/evidence identity, static documentation reconciliation and recorded manifest validation only. No new Lean, TeX, bounded suite, experiment, control or semantic proof audit.',
 'archive':{'name':ARCHIVE.name,'library_version':1,'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'members':len(names)},
 'file_count':len(initial),'manifest_records':len(rows),'checksum_list_records':len(sums),'checks':checks,'failures':failures,
 'source_preservation':{'original_scientific_files':739,'preserved_archives':3,'archive_crc':archive_crcs,'numbered_source_records':184,'proof_bodies':140,'main_source_byte_identical':True},
 'formal_scope':{'endpoint_results':33,'targets':341,'proof_modules':47,'lean_files':49,'frozen_source_hash_entries':53,'inherited_namespace_declarations':782,'historical_compiler_date':'2026-09-06','fresh_lean_execution':False,'full_expanded_manuscript_formalized':False},
 'inherited_audit_reconciliation':{'disclosure_reconstructions':reconstructions,'direct_fragment_matches':3,'old_assembled_source_hash_recovered':False,'old_assembled_boundary':audit['assembled_source_boundary'],'classical_qualifiers':audit['classical_interface_qualifiers']},
 'recorded_bounded_evidence':{'suites':11,'input_artifact_rows':len(input_rows),'unique_input_paths':len({r['path'] for r in input_rows}),'output_artifact_rows':len(output_rows),'strict_controls':21,'fresh_suite_or_control_rerun':False},
 'executed_existing_check':{'command':'python3 -B scripts/verify_release.py --report OUTSIDE_BASELINE/INHERITED_RELEASE_VERIFIER_RUN.json','exit':0,'status':verified['status'],'scope':'Read-only integrity/source/publication/evidence validation, including temporary static reconciliation; no scientific suite execution.'},
 'audit_harness_history':'The first independent audit run stopped on a parser assumption: VI axiom records are a list, unlike the preceding paper dictionary. The harness was corrected to the actual VI schema before the complete accepted audit. A PDF replay field name was also aligned with the inspected schema. No baseline/evidence file changed.',
 'minimal_freeze_recommendation':'Keep both strict verifier and release checker byte-identical. Regenerate MANIFEST_SHA256.json with its exact existing komorebi.strict_manifest.v1 schema/allowed metadata keys. Regenerate SHA256SUMS.txt for new payloads excluding itself and the root manifest; preserve both original index files under before/. No hardcoded old root-manifest digest needs adaptation.',
 'limitations':['The 33-endpoint inherited Lean contract does not certify all 184 source records or 140 proof bodies. The broader 142 theorem-like records include conceptual overlap and are not additional formal coverage.','Two corrected branch hashes are recoverable exactly by restoring removed disclosure paragraphs in memory; three corrected fragments match directly. The older assembled whole-file audit hash is not claimed recovered. These are provenance checks, not new semantic reproof.','Classical conditional-expectation/martingale convergence, Gaussian Hermite completeness and stable-subordination statements retain their explicit hypotheses and inherited authentication boundaries; no fresh whole-reference audit is claimed.','Compiler evidence dates to September 6, with external pinned runtime and inherited cache evidence. No new Lean or native Windows execution occurred.','Transfer-semigroup completed-space realization, uniform refinement control and latent-packet closure for stable infinite systems remain separate open research.']
}
(OUT/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper VI baseline integrity audit\n\n'+result['status']+'\n\nAll 2,136 archive/extracted files authenticate. The strict manifest has 2,135 records, excluding only itself; the separate checksum list has 2,134 entries, excluding itself and the manifest. Selected archive size/hash and CRC pass.\n\nAll 739 original scientific source files and three historical archives retain exact recorded hashes; the archives pass CRC. The main manuscript is byte-identical to its selected predecessor and preserves 184 source records and 140 proof bodies.\n\nThe inherited formal scope remains 33 endpoints, 341 targets, 47 proof modules and 782 namespace declarations. All 53 frozen source/configuration/ledger hashes, 49 Lean files and current guide target/ledger records authenticate. No new Lean process ran. The broader 142 theorem-like records and 140 proof environments do not enlarge that contract.\n\nAll 11 recorded bounded-suite manifests, raw result counts, input/output identities and the 21-control verifier receipt authenticate without suite/control reruns. The existing source/publication/evidence checker passes; it freshly regenerates only a temporary static documentation-reconciliation record and validates recorded evidence manifests.\n\nHistorical provenance limits remain precise: two branch hashes are reconstructed exactly by restoring disclosure paragraphs in memory, three corrected fragments match directly, and the old assembled whole-file audit hash is not claimed recovered. Classical-source authentication limits and three open research routes remain explicit. No live package/source blocker was found.\n\nKeep both verifier scripts unchanged. Regenerate the strict JSON manifest in its current schema and the accompanying SHA256SUMS list, preserving both earlier index files under before/. No old-manifest digest adapter is needed. No baseline file changed and no Lean/TeX/finite/control execution occurred.\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':failures,'files':len(initial),'finite_input_rows':len(input_rows),'finite_output_rows':len(output_rows)},indent=2))
sys.exit(bool(failures))

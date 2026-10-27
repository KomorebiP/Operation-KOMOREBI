#!/usr/bin/env python3
"""Read-only CLI authentication of the selected Paper VII freeze baseline.

No compiler, PDF builder, mathematical experiment or control suite is invoked.
ZIP members are hashed as streams without extracting or copying source trees.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, hashlib, json, re, sys, zipfile

P=argparse.ArgumentParser(description=__doc__)
P.add_argument('--root',type=Path,default=Path('/workspace/scratch/fbc994080222/paper_vii_freeze/baseline/Komorebi_Paper_VII_Final_2026-10-18'))
P.add_argument('--archive',type=Path,default=Path('/workspace/scratch/fbc994080222/paper_vii_freeze/inputs/Komorebi_Paper_VII_Final_2026-10-18.zip'))
P.add_argument('--output',type=Path,default=Path('/workspace/scratch/fbc994080222/paper_vii_freeze/audit_integrity'))
A=P.parse_args();ROOT=A.root.resolve();ARCHIVE=A.archive.resolve();OUT=A.output.resolve()
if OUT==ROOT or ROOT in OUT.parents:P.error('--output must be outside the baseline')
OUT.mkdir(parents=True,exist_ok=True)
def digest_stream(stream):
    h=hashlib.sha256()
    for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def sha(p):
    with p.open('rb') as stream:return digest_stream(stream)
def read(p):return json.loads(p.read_text())
def safe(s):
    return isinstance(s,str) and bool(s) and '\\' not in s and ':' not in s and not PurePosixPath(s).is_absolute() and '..' not in PurePosixPath(s).parts and PurePosixPath(s).as_posix()==s
checks={};failures=[]
def check(label,result):
    checks[label]=bool(result)
    if not result:failures.append(label)
initial={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
m=read(ROOT/'MANIFEST_SHA256.json');rows=m['files']
check('3261_unique_safe_manifest_rows',len(rows)==3261==len({r['path'] for r in rows}) and all(safe(r['path']) for r in rows))
check('exact_3262_baseline_files',set(initial)=={r['path'] for r in rows}|{'MANIFEST_SHA256.json'})
check('no_symlinks',not any(p.is_symlink() for p in ROOT.rglob('*')))
check('all_manifest_bytes_and_hashes',all((ROOT/r['path']).stat().st_size==r['bytes'] and initial[r['path']]==r['sha256'] for r in rows))
check('selected_archive_identity',ARCHIVE.stat().st_size==91949498 and sha(ARCHIVE)=='b38a057a6a0841bb13e6ca602e854cdc68fc20d3ca2865195b535d53b6ea0536')
with zipfile.ZipFile(ARCHIVE) as z:
    names=z.namelist();members=[i for i in z.infolist() if not i.is_dir()]
    check('archive_3262_regular_unique_members',len(members)==3262 and len(names)==len(set(names)))
    check('safe_archive_members',all(safe(n.rstrip('/')) for n in names) and all((i.external_attr>>16)&0o170000!=0o120000 for i in z.infolist()))
    archived={PurePosixPath(i.filename).relative_to(ROOT.name).as_posix():i for i in members}
    check('archive_exact_extraction_inventory',set(archived)==set(initial))
    matches=[]
    for name,info in archived.items():
        with z.open(info) as stream:matches.append(info.file_size==(ROOT/name).stat().st_size and digest_stream(stream)==initial[name])
    check('archive_member_stream_hashes_and_crc',all(matches))

edition=read(ROOT/'EDITION.json');current=ROOT/'verification/final_prose_2026-10-18'
validation=read(current/'RELEASE_VALIDATION.json');assets=read(current/'INHERITED_ASSET_PRESERVATION.json');pres=read(current/'SOURCE_PRESERVATION.json')
check('accepted_final_prose_release',edition['editorial_status']=='FINAL_PROSE_AND_PROOFREADING_COMPLETE' and validation['status']=='PASS_FOR_STATED_SCOPE' and validation['fresh_lean_compilation'] is False and validation['scientific_symbolic_suites_reexecuted_this_revision'] is False)
check('all_481_approved_source_pins',len(validation['source_pins'])==481 and all(initial[r['path']]==r['sha256'] for r in validation['source_pins']))
check('all_113_current_report_pins',len(validation['report_pins'])==113 and all(initial[r['path']]==r['sha256'] for r in validation['report_pins']))
check('all_31_required_reports_accepted',len(validation['required_pass_reports'])==31 and all(read(ROOT/name)['status'].startswith('PASS') for name in validation['required_pass_reports']))
check('prose_preservation_147_142_5_107_1795',pres['status']=='PASS_FOR_STATED_SCOPE' and pres['failures']==[] and pres['record_environments']==147 and pres['numbered_records']==142 and pres['unnumbered_statements']==5 and pres['proof_bodies']==107 and pres['proof_bodies_byte_identical']==73 and pres['proof_bodies_with_reviewed_prose_edits']==34 and pres['extracted_mathematical_spans']==1795)
check('all_9_current_part_hashes',len(pres['baseline_parts'])==9 and all(initial['editable/traditional/parts/'+r['name']]==r['current_sha256'] and all(r['checks'].values()) for r in pres['baseline_parts']))
check('799_inherited_assets_exact_counts',assets['status']=='PASS_FOR_STATED_SCOPE' and assets['failures']==[] and assets['counts']=={'source':784,'downloads':2,'provenance/current_retrieved_baseline':13} and len(assets['files'])==799)
check('all_799_inherited_asset_identities',all(initial[r['path']]==r['baseline_sha256'] and (ROOT/r['path']).stat().st_size==r['bytes'] and r['current_identical'] for r in assets['files']))
check('121_inherited_lean_source_files_preserved',assets['lean_source_files_preserved']==121 and sum(r['path'].endswith('.lean') for r in assets['files'])==121)
nested=[]
for path,branch in [('downloads/PSC_Paper_VII_Strengthened_Annals_Edition_Package.zip','strengthened'),('downloads/Paper_VII_Complete_v0.6.0_With_Visual_Appendix.zip','complete')]:
    p=ROOT/path;stream_matches=[]
    with zipfile.ZipFile(p) as z:
        file_members=[i for i in z.infolist() if not i.is_dir()]
        for info in file_members:
            target='source/'+branch+'/'+info.filename
            with z.open(info) as stream:stream_matches.append(target in initial and digest_stream(stream)==initial[target])
        nested.append({'path':path,'bytes':p.stat().st_size,'sha256':sha(p),'regular_members':len(file_members),'all_payloads_match_unpacked_source':all(stream_matches)})
check('two_nested_archives_match_784_source_files',len(nested)==2 and sum(r['regular_members'] for r in nested)==784 and all(r['all_payloads_match_unpacked_source'] for r in nested))

S=ROOT/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot';F=S/'verification/final_finite_release_run'
summary=read(F/'SUMMARY.json');constructed=read(F/'CONSTRUCTED_OBJECTS_AUDIT.json');static=read(ROOT/'editable/lean_guide/generated/static_reconciliation.json')
ledger=read(S/'THEOREM_LEDGER.json');inventory=read(S/'verification/theorem_inventory.json');targets=read(ROOT/'editable/lean_guide/generated/targets.json')
allowed={'Classical.choice','Quot.sound','propext'}
check('inherited_19_item_contract',len(ledger)==19 and all(r['status']=='LEAN_CHECKED' for r in ledger) and edition['formal_scope']['ledger_items']==19)
check('25_module_323_named_theorem_summary',summary['complete'] is True and summary['pass'] is True and len(summary['modules'])==25 and summary['theorem_declarations']==323 and len(inventory)==25 and sum(len(v) for v in inventory.values())==323)
check('active_formal_module_set',set(p.stem for p in (S/'formalization').glob('*.lean'))=={r['module'] for r in summary['modules']})
check('all_25_active_sources_and_compile_log_hashes',all(sha(S/r['source'])==r['sha256'] and sha(F/r['log'])==r['log_sha256'] and r['exit_code']==0 and not r['unexpected_axioms'] for r in summary['modules']))
check('all_transitive_import_source_hashes',all(sha(S/'formalization'/(name+'.lean'))==h for r in summary['modules'] for name,h in r['dependency_source_sha256'].items()))
parsed={}
for row in summary['modules']:
    raw={name:[] if not values else [v.strip() for v in values.split(',') if v.strip()] for name,values in re.findall(r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$",(F/row['log']).read_text(),re.M)}
    current_names={n:raw[n] for n in row['axiom_audits'] if n in raw}
    check('saved_axiom_log_'+row['module'],current_names==row['axiom_audits'] and all(set(v)<=allowed for v in current_names.values()))
    parsed.update(current_names)
check('323_exact_saved_target_names',len(parsed)==323 and set(parsed)=={n for names in inventory.values() for n in names}=={r['declaration'] for r in targets})
check('guide_axiom_record_identity',parsed==read(ROOT/'editable/lean_guide/generated/inherited_axiom_records.json'))
check('summary_runner_verifier_inventory_pins',sha(S/'scripts/check_low_memory.py')==summary['runner_sha256'] and sha(S/'scripts/verify.py')==summary['verifier_sha256'] and sha(S/'verification/theorem_inventory.json')==summary['inventory_sha256'])
check('six_constructed_objects_separate_scope',constructed['pass'] is True and constructed['exit_code']==0 and constructed['construction_count']==6 and len(constructed['axiom_audits'])==6 and set(constructed['axiom_audits'])==set(read(S/'verification/constructed_objects_inventory.json')) and all(set(v)<=allowed for v in constructed['axiom_audits'].values()))
check('constructed_source_log_and_summary_bindings',sha(S/constructed['source'])==constructed['source_sha256'] and sha(F/'constructed_objects.log')==constructed['log_sha256'] and sha(S/'verification/constructed_objects_inventory.json')==constructed['inventory_sha256'] and sha(F/'SUMMARY.json')==constructed['cumulative_summary_sha256'])
check('two_inherited_negative_control_identities',len(summary['negative_controls'])==2 and all(r['pass'] and r['exit_code']==r['expected_exit_code']==1 and sha(S/r['source'])==r['sha256'] and sha(F/r['log'])==r['log_sha256'] for r in summary['negative_controls']))
check('static_reconciliation_exact_scope',static['status']=='PASS' and all(static['checks'].values()) and static['source_modules']==25 and static['theorem_targets']==323 and static['scoped_results']==19 and static['constructed_objects']==6 and static['dependency_pins']==9 and static['fresh_lean_compilation'] is False)
check('static_inherited_evidence_hashes',all(sha(S/name)==h for name,h in static['inherited_evidence_sha256'].items()))
declared_objects=[name for row in summary['modules'] for name in row['build_sha256']]
present_objects=sum((F/'build'/name).is_file() for name in declared_objects)
check('no_new_compiler_objects_claimed',len(declared_objects)==125 and present_objects==0)

check('three_readers_286_pages',len(edition['documents'])==3 and sum(d['pages'] for d in edition['documents'])==edition['total_pages']==286 and all(initial[d['path']]==d['sha256'] and (ROOT/d['path']).stat().st_size==d['bytes'] for d in edition['documents']))
check('all_nine_pdf_copies_match',all(initial['publication/pdfs/'+Path(d['path']).name]==d['sha256'] and initial['editable/'+d['role']+'/'+Path(d['path']).name]==d['sha256'] for d in edition['documents']))
pub=read(OUT/'PUBLICATION_SOURCE_BINDING_CHECK.json')
check('fresh_readonly_publication_preservation_check_pass',pub['status']=='PASS_FOR_STATED_SCOPE' and pub['inherited_files_byte_identical_to_retrieved_delivery']==799 and pub['fresh_lean_compilation'] is False)
old_integrity=read(OUT/'INHERITED_INTEGRITY_RUN_STDOUT.txt')
check('fresh_original_integrity_verifier_pass',old_integrity['status']=='PASS' and old_integrity['files_checked']==3261 and old_integrity['failures']==[])
check('Part_II_and_five_continuum_targets_remain_outside_contract',len(edition['open_continuum_targets'])==5 and static['open_continuum_conjectures']==5 and edition['fresh_checks']['mathematical_kernel_compilation'] is False)
final={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file()}
check('baseline_not_modified',initial==final)
result={
 'schema':'komorebi.paper-vii.freeze-baseline-audit/1','status':'PASS' if not failures else 'FAIL',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Fresh exact CLI file/archive/source/saved-evidence identity and closed prose-preservation checks. No Lean, TeX, mathematical experiment, finite suite or control suite execution. No copied or extracted nested trees.',
 'archive':{'name':ARCHIVE.name,'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'regular_members':len(members),'total_members':len(names)},
 'file_count':len(initial),'manifest_records':len(rows),'checks':checks,'failures':failures,
 'preserved_retrieved_assets':{'source':784,'archives':2,'comparison_baseline_files':13,'total':799,'inherited_lean_files':121,'nested_archives':nested},
 'formal_scope':{'finite_manuscript_items':19,'active_modules':25,'named_theorem_declarations':323,'separately_audited_constructed_objects':6,'dependency_pins':9,'inherited_compiler_release':'PRSC_VII_v0.6.0_Finite_Proofs_Complete','inherited_compiler_started':summary['started_utc'],'fresh_lean_execution':False,'Part_II_in_finite_contract':False,'compiled_object_hashes_in_historical_summary':125,'compiled_objects_retained_in_package':present_objects},
 'prose_preservation':{'record_environments':147,'numbered_records':142,'unnumbered_statements':5,'theorem_like_records':96,'proof_bodies':107,'proof_bodies_byte_identical':73,'proof_bodies_with_reviewed_prose_edits':34,'mathematical_spans_preserved':1795,'reviewed_line_hunks':206},
 'fresh_existing_readonly_checks':[{'command':'python3 -B scripts/verify_integrity.py','exit':0,'scope':'File membership, sizes and hashes relative to inherited list manifest on current Linux host.'},{'command':'python3 -B scripts/check_publication_consistency.py --report OUTSIDE_BASELINE/PUBLICATION_SOURCE_BINDING_CHECK.json','exit':0,'scope':'Nine PDF copies, current navigation, current source/report pins, exact closed preservation comparison and recorded packaged-PDF replay bindings. No PDF rebuild or math execution.'}],
 'verifier_reuse':'The original integrity script reads files rows without checking top-level schema and can consume the new strict-schema manifest unchanged. Its platform-native path strings and missing explicit duplicate/symlink defenses make it unsuitable as the primary portable freeze checker. Add the known strict verifier under a new name, preserve both original scripts unchanged, and identify reused controls by exact source/receipt hash.',
 'unsafe_default_cli_not_run':'editable/lean_guide/static_check.py writes generated JSON in place and offers no external-output option. It was inspected but not executed on the baseline. Its source/log/target/constructed-object evidence was independently authenticated here.',
 'boundaries':['All source/ZIP preservation comparisons bind the actual October 11 retrieved font-removed payload, not earlier original archives before that packaging change. No live top-level manifest or source-recovery defect was found.','The inherited compiler summary lists 125 generated object hashes, but those build binaries are not retained in this source package. No fresh object replay or compiler run is claimed. Pinned runtime/dependencies remain external.','Part II and the five physical continuum targets are outside the finite formal contract: anomaly-free refinement, uniform Feshbach control, Lorentzian reconstruction, Einstein infrared limit and a positive physical massless spin-two sector.','Earlier 16-method software controls, two compiler rejection controls and preservation-checker controls remain dated inherited evidence. None was rerun for this freeze.','The whole written monograph is not claimed Lean-formalized; prose preservation is not a new correctness audit or external peer review.']
}
(OUT/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper VII baseline integrity audit\n\n'+result['status']+'\n\nAll 3,262 baseline files authenticate against 3,261 manifest rows plus the manifest itself. The selected archive matches its supplied size/hash and every regular ZIP member matches the extracted tree by streaming hash/CRC checks. No nested archive was extracted or tree copied.\n\nAll 799 retrieved assets authenticate: 784 source files, two recovery ZIPs and thirteen comparison-baseline files, including 121 retained Lean files. The two nested ZIP payloads match all 784 unpacked source files. These are the actual October 11 font-removed payloads; earlier archive identities remain historical.\n\nThe inherited September 6 compiler contract remains 19 finite manuscript items, 323 named theorem declarations in 25 active modules and six separately audited constructed objects. Saved source/log/import and axiom records authenticate, including the two inherited negative-control records. The old summary contains 125 compiled-object hashes but those binaries are not retained; no fresh object replay or Lean process is claimed. Part II and the five physical continuum targets remain outside this finite contract.\n\nThe current prose edition retains 147 statements (142 numbered and five unnumbered), 107 proof bodies (73 byte-identical and 34 reviewed prose revisions), and 1,795 mathematical spans. Read-only publication consistency freshly rechecks the closed reviewed-edit comparison and current source/report/PDF bindings. It does not establish mathematical correctness anew or rebuild PDFs.\n\nBoth original read-only integrity/publication checks pass. The original integrity script accepts list rows in a new strict schema, but its Windows-sensitive path strings and weaker duplicate/symlink policy warrant the additional known portable checker. The static_check.py guide command was not run because it writes generated files in place. No baseline file was modified. No live package-integrity or source-recovery blocker was found.\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':failures,'files':len(initial),'formal_items':19,'active_modules':25,'named_theorem_declarations':323,'constructed_objects':6},indent=2))
sys.exit(bool(failures))

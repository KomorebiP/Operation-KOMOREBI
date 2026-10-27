#!/usr/bin/env python3
"""Static Paper X source, retained build-artifact and accepted census bindings.

Reads evidence only. Never imports/runs a project auditor, parser control,
compiler, generator, scientific suite or PDF builder.
"""
from pathlib import Path
import collections, hashlib, json, re
from datetime import datetime, timezone
TASK=Path('/dev/shm/komorebi_paper_x_freeze_fbc994080222')
BASE=TASK/'baseline/Paper_X_Final_Release_v1.0.0'
P=BASE/'production_replay'; A=BASE/'production_audit'; ACCEPT=A/'accepted_audit'
OUT=TASK/'audit_integrity/FORMAL_STATIC_AUDIT.json'
def load(path):return json.loads(path.read_text())
cache={}
def sha(path):
    path=Path(path)
    if path not in cache:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
        cache[path]=h.hexdigest()
    return cache[path]
checks=[]
def ck(name,value,detail=None):checks.append({'name':name,'pass':bool(value),'detail':detail})
manifest=load(P/'PUBLICATION_SOURCE_MANIFEST.json'); modules={r['module']:r for r in manifest['modules']}
manifest_sha=sha(P/'PUBLICATION_SOURCE_MANIFEST.json')
ck('selected_source_manifest_exact122',manifest['count']==122 and len(modules)==122 and not manifest['missing'])
source_fail=[]
for m in modules.values():
    if sha(P/m['source_relative'])!=m['source_sha256']:source_fail.append(m['module'])
ck('all122_selected_source_bytes',not source_fail,source_fail)

preservation=load(P/'SOURCE_PRESERVATION.json'); archive_map=load(BASE/'formal_preservation/ARCHIVE_MAP.json')
originals={}
for r in archive_map['leaf_occurrences']:
    restored='/'.join([c['member_path']+'.contents' for c in r['archive_chain'][1:]]+[r['member_path']])
    originals.setdefault((r['root_archive'],restored),[]).append(r)
origin_fail=[]
for r in preservation['sources']:
    m=modules[r['module']]
    candidates=originals.get(('conditional_checked',r['mapped_original_member']),[])
    matching=[x for x in candidates if x['sha256']==r['sha256']==m['source_sha256']]
    if not matching or r['mapped_original_member']!=m['origin_restored_relative'] or r['source_relative']!=m['source_relative']:
        origin_fail.append(r['module']);continue
    x=matching[0]
    if sha(BASE/'formal_preservation'/x['payload_path'])!=r['sha256']:origin_fail.append(r['module']+':payload')
ck('all122_source_origins_bind_compact_payloads',preservation['status']=='PASS' and preservation['modules_checked']==122 and len(preservation['sources'])==122 and not origin_fail,origin_fail)
ck('source_preservation_map_and_scope',sha(BASE/'formal_preservation/ARCHIVE_MAP.json')==preservation['preservation_map_sha256'] and preservation['production_source_edits']==0 and preservation['selected_source_bytes_match_original_payloads'] is True)

builds={}; inventories={}; build_fail=[];artifact_fail=[];log_count=output_count=0
for label in ['build_A1','build_B']:
    root=P/label; report=load(root/'BUILD_REPORT.json'); builds[label]=report
    inv=load(root/'ALL_ARTIFACTS.json');inventory={r['path']:r for r in inv['all_generated_files']};inventories[label]=inventory
    if report['status']!='PASS' or report['complete'] is not True or any(report[k]!=122 for k in ['expected_modules','compiled_modules','passed_modules']) or report['production_objects_seeded']!=0 or report['mathlib_cold_rebuild'] is not False or report['failed_modules'] or report['blocked_modules'] or report['source_unchanged'] is not True or report['source_manifest_sha256']!=manifest_sha:
        build_fail.append(label+':scope')
    rows={r['module']:r for r in report['results']}
    if set(rows)!=set(modules):build_fail.append(label+':modules')
    for name,row in rows.items():
        if row['source_sha256']!=modules[name]['source_sha256'] or row['returncode']!=0 or row['timed_out'] is not False or row['status']!='PASS':build_fail.append(label+':'+name)
        log_count+=1
        if (root/row['log']).read_text()!=row['stdout']+row['stderr']:build_fail.append(label+':log:'+name)
        for output in row['outputs']:
            output_count+=1;q=root/output['path']
            if q.stat().st_size!=output['bytes'] or sha(q)!=output['sha256']:artifact_fail.append(label+':compile output:'+output['path'])
    actual={q.relative_to(root).as_posix() for q in (root/'objects').rglob('*') if q.is_file()}
    if inv['count']!=392 or len(inventory)!=392 or set(inventory)!=actual:artifact_fail.append(label+':exact artifact set')
    for rel,r in inventory.items():
        q=root/rel
        if q.stat().st_size!=r['bytes'] or sha(q)!=r['sha256']:artifact_fail.append(label+':'+rel)
    if not all(d['actual_revision']==d['expected_revision'] and ((d['compiled_module_root'] is None and d['compiled_cache_present'] is False) or (d['compiled_module_root'] is not None and d['compiled_cache_present'] is True)) for d in report['dependencies']):build_fail.append(label+':dependency revision record')
ck('two_complete_saved122_module_builds_and244_logs',not build_fail,{'logs':log_count,'failures':build_fail})
ck('all784_retained_artifacts_and_compiler_outputs',not artifact_fail,{'artifact_files':sum(len(v) for v in inventories.values()),'compiler_output_rows':output_count,'failures':artifact_fail})
comparison=load(P/'BUILD_COMPARISON.json'); pairs=comparison['pairs'];pair_fail=[]
for r in pairs:
    ar=inventories['build_A1'].get(r['path']);br=inventories['build_B'].get(r['path'])
    if not ar or not br or ar['sha256']!=r['A_sha256'] or br['sha256']!=r['B_sha256'] or ar['bytes']!=r['A_bytes'] or br['bytes']!=r['B_bytes'] or r['A_sha256']!=r['B_sha256'] or r['A_bytes']!=r['B_bytes'] or r['identical'] is not True:pair_fail.append(r['path'])
ck('392_artifact_pairs_recomputed_from_retained_bytes',comparison['status']=='PASS' and len(pairs)==392 and len({r['path'] for r in pairs})==392 and comparison['all_pairs_byte_identical'] is True and not pair_fail,pair_fail)
ck('comparison_receipt_hash_crosslinks',sha(P/'build_A1/BUILD_REPORT.json')==comparison['A_report_sha256'] and sha(P/'build_B/BUILD_REPORT.json')==comparison['B_report_sha256'])
summary=load(P/'REPLAY_SUMMARY.json')
ck('two_build_summary_scope',summary['status']=='PASS' and summary['production_modules_per_run']==122 and summary['clean_source_build_runs']==2 and summary['all_generated_file_pairs']==392 and summary['production_objects_seeded_per_run']==0 and summary['source_edits']==0 and summary['all_generated_file_pairs_identical'] is True and summary['historical_olean_bit_identity_claimed'] is False)
terminal=load(P/'TERMINAL_SUBSET.json')
ck('97_module_terminal_is_subset',terminal['count']==97 and len(terminal['modules'])==97 and all(r['module'] in modules and modules[r['module']]['source_sha256']==r['source_sha256'] for r in terminal['modules']))

audit=load(ACCEPT/'REPORT.json'); selection=load(A/'PRODUCTION_SELECTION.json'); owned=load(ACCEPT/'OWNED_DECLARATIONS.json')
ck('accepted_audit_receipt_source_build_inventory_bindings',audit['status']=='PASS' and audit['selection_sha256']==sha(A/'PRODUCTION_SELECTION.json') and audit['compilation_receipt_sha256']==sha(P/'build_A1/BUILD_REPORT.json') and audit['artifact_inventory_sha256']==sha(P/'build_A1/ALL_ARTIFACTS.json') and audit['production_artifacts_pinned']==392 and selection['production_manifest_sha256']==manifest_sha)
ck('audit_selection_exact122_sources45_targets',len(selection['modules'])==122 and len(selection['targets'])==45 and {m['module']:m['source_sha256'] for m in selection['modules']}=={n:m['source_sha256'] for n,m in modules.items()})
tool_fail=[]
for name,h in audit['tooling'].items():
    for parent in [A/'tooling',ACCEPT/'common']:
        if sha(parent/name)!=h:tool_fail.append(str(parent/name))
if sha(ACCEPT/'AS_EXECUTED_RUNNER.py')!=audit['runner_sha256']:tool_fail.append('AS_EXECUTED_RUNNER.py')
for key in ['audit_source_pins','exact_type_source_pins']:
    for r in audit[key]:
        if sha(ACCEPT/'common'/Path(r['path']).name)!=r['sha256']:tool_fail.append(r['path'])
ck('as_executed_audit_tool_and_generated_source_pins',not tool_fail,tool_fail)
command_fail=[]
for r in audit['commands']:
    q=ACCEPT/'logs'/Path(r['log']).name
    if sha(q)!=r['log_sha256'] or r['timed_out'] is not False or r['spawn_error'] is not None:command_fail.append(q.name)
    if q.name.startswith('control_'):
        if r['returncode']!=1:command_fail.append(q.name+':exit')
    elif r['returncode']!=0:command_fail.append(q.name+':exit')
ck('eight_saved_audit_command_logs_including_historical_controls',len(audit['commands'])==8 and not command_fail,command_fail)

pin_fail=[]
pins=load(ACCEPT/'SOURCE_OBJECT_PINS_BEFORE.json')
if pins!=load(ACCEPT/'SOURCE_OBJECT_PINS_AFTER.json'):pin_fail.append('before/after differ')
for r in pins:
    src=P/modules[r['module']]['source_relative'];obj=P/'build_A1/objects'/Path(*r['module'].split('.')).with_suffix('.olean')
    if sha(src)!=r['source_sha256'] or sha(obj)!=r['object_sha256'] or src.stat().st_size!=r['source_bytes'] or obj.stat().st_size!=r['object_bytes']:pin_fail.append(r['module'])
ck('all122_audited_sources_and_objects_unchanged',len(pins)==122 and not pin_fail,pin_fail)
allpins=load(ACCEPT/'ALL_ARTIFACT_PINS_BEFORE.json');allpin_fail=[]
if allpins!=load(ACCEPT/'ALL_ARTIFACT_PINS_AFTER.json'):allpin_fail.append('before/after differ')
for r in allpins:
    if any(r[k]!=inventories['build_A1'][r['path']][k] for k in ['path','bytes','sha256']):allpin_fail.append(r['path'])
ck('all392_audit_artifact_pins_match_actual_build',len(allpins)==392 and not allpin_fail,allpin_fail)

raw=(ACCEPT/'logs/batch_01_owned_declarations_and_axioms.log').read_text()
events=[json.loads(line[len('P10AUDIT '):]) for line in raw.splitlines() if line.startswith('P10AUDIT ')]
rawrecords=[r for r in events if r['event']=='declaration'];rawtargets=[{k:v for k,v in r.items() if k!='event'} for r in events if r['event']=='target'];ends=[r for r in events if r['event']=='complete']
records=owned['records'];allowed={'Classical.choice','Quot.sound','propext'}
record_by_name={r['name']:r for r in records};raw_by_name={r['name']:r for r in rawrecords}
ck('raw_event_records_exactly_match_owned2846_census',len(records)==2846 and len(record_by_name)==2846 and len(rawrecords)==2846 and raw_by_name==record_by_name and len(ends)==1 and ends[0]['declarations']==2846 and ends[0]['theorems']==2127 and ends[0]['targets']==45)
ck('owned_theorem_private_and_kind_census',sum(r['kind']=='theorem' for r in records)==2127 and sum(r['name'].startswith('_private.') for r in records)==444 and dict(collections.Counter(r['kind'] for r in records))==audit['declaration_kinds'] and audit['private_declarations']==444 and audit['declarations']==2846 and audit['theorems']==2127)
ck('all122_owners_and_permitted_axiom_closures',set(owned['owners'])==set(modules) and dict(collections.Counter(r['owner'] for r in records))==audit['per_owner_declarations'] and all(r['owner'] in modules and not r['forbidden'] and set(r['axioms'])<=allowed for r in records) and set(owned['axiom_union'])==set(audit['axiom_union'])==allowed)
ck('raw45_targets_exact_kind_owner_contract',len(rawtargets)==45 and rawtargets==owned['targets_resolved']==selection['targets']==load(A/'contract_review/AUDIT_TARGETS.json'))
batch=load(ACCEPT/'batch_01_OWNED_DECLARATIONS.json')
ck('batch_and_combined_owned_evidence_equal',batch['records']==records and batch['targets_resolved']==owned['targets_resolved'] and batch['status']==owned['status']=='PASS')
types=(ACCEPT/'EXACT_TARGET_TYPES.txt').read_text();typelog=(ACCEPT/'logs/batch_01_exact_target_types.log').read_text()
ck('45_full_elaborated_type_outputs_retained',types=='=== batch_01 ===\n'+typelog and all(re.search(r'(?m)^@?'+re.escape(t['name'])+r'(?:\.\{|[ \t\n:])',types) for t in selection['targets']))
type_source=(ACCEPT/'common/batch_01_TargetTypes.lean').read_text()
ck('type_print_source_targets_exact',re.findall(r'^#check @(.+)$',type_source,re.M)==[t['name'] for t in selection['targets']])
resolved=load(ACCEPT/'RESOLVED_IMPORTS.json')[0];imports=[];import_fail=[]
for r in resolved['resolved']:
    if '/fresh_A1/objects/' in r['path']:
        rel=r['path'].split('/fresh_A1/',1)[1];imports.append(rel)
        if sha(P/'build_A1'/rel)!=r['sha256']:import_fail.append(rel)
ck('all122_direct_production_import_resolutions_bound',len(imports)==122 and not import_fail and set(resolved['owners'])==set(modules),import_fail)

contract=load(A/'contract_review/TARGET_CONTRACT.json');explicit=load(A/'contract_review/EXPLICIT_TARGETS.json')
target_fail=[]
for r in explicit['targets']:
    q=P/r['source_relative'];lines=q.read_text().splitlines();located='\n'.join(lines[r['source_line']-1:r['signature_end_line']]).strip()
    signature=r['source_declaration_signature'];suffix=located[len(signature):].lstrip() if located.startswith(signature) else ''
    if sha(q)!=r['source_sha256'] or sha(q)!=r['manifest_source_sha256'] or not located.startswith(signature) or not (suffix.startswith(':=') or re.match(r'where\b',suffix)):target_fail.append(r['name'])
ck('all45_static_target_source_locations_bind',len(explicit['targets'])==45 and explicit['targets']==contract['targets'] and contract['explicit_target_count']==45 and contract['record_count']==20 and contract['module_count']==122 and contract['source_manifest_sha256']==manifest_sha and not target_fail,target_fail)
review=load(BASE/'verification/2026-10-20/AMENDED_TERMINAL_AND_TARGET_REVIEW.json')
terminal_source=P/'publication_sources/PaperX/ConditionalOccupiedSystemCompletion.lean'
ck('accepted_terminal_identity_and_limited_review_scope',sha(terminal_source)==summary['terminal_source_sha256']==review['source_identity']['terminal_reader_sha256']==contract['terminal']['source_sha256'] and review['review_provenance']['whole_manuscript_proof_audit'] is False and review['review_provenance']['new_lean_compilation_performed'] is False and len(review['twenty_record_correspondence'])==20)

report={'schema':'komorebi.paper-x.freeze-formal-static-audit/1','created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','check_count':len(checks),'checks':checks,'baseline_read_only':True,'compiler_auditor_parser_or_control_reruns':False,'scientific_or_tex_reruns':False,
 'scope':{'accepted_evidence_date':'2026-10-20','sources_and_origins':122,'recorded_builds':2,'modules_per_build':122,'retained_generated_artifacts_per_build':392,'matching_artifact_pairs':392,'build_logs':244,'owning_modules':122,'owned_declarations':2846,'theorems':2127,'private_declarations':444,'exact_target_contracts':45,'terminal_subset_modules':97,'permitted_axioms':sorted(allowed)},
 'receipt_paths':{'source_manifest':'production_replay/PUBLICATION_SOURCE_MANIFEST.json','source_origins':'production_replay/SOURCE_PRESERVATION.json','build_A':'production_replay/build_A1/BUILD_REPORT.json','build_B':'production_replay/build_B/BUILD_REPORT.json','comparison':'production_replay/BUILD_COMPARISON.json','accepted_owning_audit':'production_audit/accepted_audit/REPORT.json','owned_census':'production_audit/accepted_audit/OWNED_DECLARATIONS.json','full_target_types':'production_audit/accepted_audit/EXACT_TARGET_TYPES.txt'},
 'accepted_receipt_sha256':sha(ACCEPT/'REPORT.json'),
 'audit_harness_history':{'initial_report':'AUDIT_HARNESS_INITIAL.json','initial_status':'FAIL','resolution':'Two local harness assumptions corrected: Cli explicitly has no compiled-module root/cache while its revision matches; saved declaration signatures exclude the :=/where body delimiter present on their final source line. No baseline or accepted evidence was changed. The corrected static pass is reported above.'},
 'limitations':['This freeze authenticates accepted October20 evidence statically. No Lean compilation, owning auditor, parser-control suite, scientific experiment, generator or TeX execution occurred.','The accepted two builds reuse pinned external Lean/Mathlib dependency objects. They do not establish a cold dependency rebuild or bit identity with historical project objects.','The recovered October10 amended conditional source contract supports its recorded 20/20 reading concordance. The later stronger residual-system attempt remains unpromoted at 19/20; October16–17 packages and their reported runs remain unrecovered.','The terminal conjunction has two independent existential outputs: a transported target family and carrier recovery at a distinguished place. Their identification requires a further comparison. Actual source members, local comparison data, carrier and constituent-copy presentations remain inputs.','The separator is literally over GQ. Zero multiplicities and empty constituent index are permitted; positive occupancy needs a separate premise. Universal occupancy, natural finite seed rank, unrestricted compatible-system/carrier existence and general arithmetic local attachment remain outside the accepted contract.','A source/name/type/owner/axiom audit is not a whole-manuscript proof audit. Classical Inputs3.1 and4.1 are outside the twenty-row reading concordance. Compiler/control fixture counts are not production theorem counts.','Compact preservation restores exact nonarchive leaf bytes. Original nested ZIP container byte streams are not reconstructed.']}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[x['name'] for x in checks if not x['pass']],'report':str(OUT)}))

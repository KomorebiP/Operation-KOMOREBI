#!/usr/bin/env python3
"""Read-only Paper XI accepted-baseline identity and saved-evidence audit.
Not Lean, auditor, scientific replay, fixture controls, PDF build or proof review.
Use --output-dir outside --root. Expanded frozen trees must be reconstructed
from the baseline preservation map before this baseline-only command is used.
"""
from pathlib import Path,PurePosixPath
from collections import Counter
import argparse,datetime,hashlib,importlib.util,json,os,stat,subprocess,sys,zipfile
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--archive',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
b=a.root.resolve();out=a.output_dir.resolve();assert not out.is_relative_to(b);out.mkdir(parents=True,exist_ok=True)
checks=[];counts={};jcache={};hcache={}
def J(p):
 p=Path(p)
 if p not in jcache:jcache[p]=json.loads(p.read_text())
 return jcache[p]
def H(p):
 p=Path(p)
 if p not in hcache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for q in iter(lambda:f.read(1024*1024),b''):h.update(q)
  hcache[p]=h.hexdigest()
 return hcache[p]
def need(x,msg='assertion failed'):
 if not x:raise AssertionError(msg)
def chk(n,f):
 try:checks.append({'check':n,'status':'PASS','details':f()})
 except Exception as e:checks.append({'check':n,'status':'FAIL','error':type(e).__name__+': '+str(e)})
def E(s):
 need(s.startswith('evidence/'),s);return b/'verification/lean'/s[len('evidence/'):]
def pin(p,h):need(p.is_file() and H(p)==h,str(p.relative_to(b) if p.is_relative_to(b) else p))
def safe(n):
 need(n and not n.startswith('/') and '\\' not in n and ':' not in n and '\x00' not in n and all(q not in ['.','..',''] for q in n.rstrip('/').split('/')),n)
receipt=J(a.receipt);man=J(b/'MANIFEST.json')
def arc():
 need(H(a.archive)==receipt['checks']['zip']['sha256']=='ed6dc23a8ff9b5227fab3fe71991dc7f5d5a635ff282bdd6dd29b04732ac5812');need(a.archive.stat().st_size==93363939)
 with zipfile.ZipFile(a.archive) as z:
  ns=z.namelist();need(len(ns)==len(set(ns))==2425);need(len({n.casefold() for n in ns})==len(ns));
  for i in z.infolist():safe(i.filename);need((i.external_attr>>16)&0o170000!=stat.S_IFLNK)
  need(z.testzip() is None)
  for i in z.infolist():
   p=b/i.filename;need(p.is_file());need(p.stat().st_size==i.file_size);need(H(p)==hashlib.sha256(z.read(i)).hexdigest(),i.filename)
 counts.update(baseline_files=2425,baseline_manifest_rows=2424)
 return {'files':2425,'bytes':a.archive.stat().st_size,'sha256':H(a.archive)}
chk('accepted_archive_and_all_extracted_members',arc)
def manifest():
 fs=man['files'];need(man['schema_version']==1 and len(fs)==2424);need(len({x['path'] for x in fs})==2424)
 actual={p.relative_to(b).as_posix() for p in b.rglob('*') if p.is_file()};need(actual=={r['path'] for r in fs}|{'MANIFEST.json'})
 for r in fs:safe(r['path']);pin(b/r['path'],r['sha256']);need((b/r['path']).stat().st_size==r['bytes'])
 need(H(b/'MANIFEST.json')==receipt['checks']['manifest']['manifest_sha256']);return {'files':len(actual),'manifest_sha256':H(b/'MANIFEST.json')}
chk('original_strict_manifest_and_external_receipt',manifest)
def tool():
 r=J(b/'evidence/release_1_1/VERIFIER_CONTROL_RECEIPT.json');pin(b/'tools/verify_release.py',r['tool_sha256']);need(len(r['results'])==23 and r['all_expected_outcomes_observed']);need(all(x['expected_pass']==x['observed_pass'] for x in r['results'] if 'expected_pass' in x));special=[x for x in r['results'] if 'expected_pass' not in x];need(len(special)==3);need(special[0]['expected_tokens']==special[0]['observed_tokens']);need(all(special[1]['matches'].values()));need(special[2]['expected_exit_code']==special[2]['observed_exit_code']==2 and not special[2]['file_created'])
 return {'accepted_fixture_cases':23,'fresh_controls_execution':False,'tool_sha256':H(b/'tools/verify_release.py'),'harness_sha256':H(b/'tools/test_verify_release.py'),'harness_binding':'original strict manifest; no separate receipt hash'}
chk('unchanged_own_verifier_and_accepted_controls',tool)
def existing():
 r=subprocess.run([sys.executable,'-B',str(b/'tools/verify_release.py'),'--root',str(b),'--zip',str(a.archive),'--output',str(out/'ORIGINAL_RELEASE_CHECK.json')],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 (out/'ORIGINAL_RELEASE_CHECK_STDOUT.txt').write_text(r.stdout);(out/'ORIGINAL_RELEASE_CHECK_STDERR.txt').write_text(r.stderr)
 need(r.returncode==0,r.stdout+r.stderr);d=J(out/'ORIGINAL_RELEASE_CHECK.json');need(d['status']=='passed' and not d['errors']);return {k:v['status'] for k,v in d['checks'].items()}
chk('fresh_unchanged_read_only_release_and_archive_checker',existing)
cat=J(b/'publication/source/lean_guide/SOURCE_CATALOG.json')['modules'];flat=J(b/'publication/source/lean_guide/DECLARATION_CATALOG.json');summary=J(b/'verification/lean/RELEASE_VERIFICATION.json');final=J(b/'verification/lean/replay_terminal_factored/RESULT.json')
def catalogue():
 need(len(cat)==423 and len(flat)==4342 and len({r['name'] for r in flat})==4342)
 for name,r in cat.items():need(r['module']==name);pin(b/'publication/source/lean_guide'/r['local_source_path'],r['sha256']);pin(b/'formalization'/Path(*name.split('.')).with_suffix('.lean'),r['sha256'])
 need({p.relative_to(b/'formalization').as_posix() for p in (b/'formalization/PaperXI').rglob('*.lean')}=={Path(*n.split('.')).with_suffix('.lean').as_posix() for n in cat}|{'PaperXI/ActualMonomialLocalGlobal.lean','PaperXI/SingleCandidateComparison.lean'})
 counts.update(selected_modules=423,lexical_catalogue_names=4342)
 return {'selected_sources':423,'unique_catalogue_names':4342,'additional_sources':2}
chk('selected_catalogue_and_portable_sources',catalogue)
def compact():
 d=J(b/'verification/lean/COMPACT_EVIDENCE_EXPORT.json');need(d['status']=='PASS' and d['file_count_excluding_this_manifest']==len(d['files'])==679)
 for r in d['files']:pin(b/'verification/lean'/r['path'],r['sha256']);need((b/'verification/lean'/r['path']).stat().st_size==r['bytes'])
 need(not list(b.rglob('*.olean')) and not list(b.rglob('*.ilean')))
 return {'compact_evidence_files':679,'retained_proof_object_binaries':0,'scope':'Saved object fingerprints, logs and receipts authenticated; omitted binary payloads are not rehashed'}
chk('compact_export_full_inventory_and_omitted_objects',compact)
def portable():
 d=J(b/'verification/lean/PORTABLE_PROJECT_RECEIPT.json');need(d['selected_modules']==423 and d['additional_modules']==2 and d['file_count']==449 and not d['compiled_objects_included'] and not d['runtime_and_dependencies_included'])
 for path,h in d['files'].items():pin(b/'formalization'/path,h)
 return {'portable_project_files':449,'runtime_dependencies_and_objects_external':True}
chk('portable_project_449_file_identity',portable)
def comp_manifest():
 d=J(b/'verification/lean/COMPUTATION_MANIFEST.json');need(len(d['input_artifacts'])==425 and len(d['outputs'])==7 and all(x['passed'] for x in d['checks']))
 for r in d['input_artifacts']:pin(b/'formalization'/r['path'],r['sha256']);need(r['sha256']==r['sha256_after'])
 for r in d['outputs']:pin(E(r['path']),r['sha256'])
 return {'input_sources':425,'result_outputs':7,'manifest_checks':len(d['checks'])}
chk('formal_computation_manifest_425_inputs_seven_results',comp_manifest)
def bridge():
 d=J(b/'evidence/release_1_1/FORMAL_SOURCE_BRIDGE.json');need(d['status']=='passed' and d['delivered_portable_project_exactly_matches']);need(len(d['records'])==425);pin(b/d['replay_result'],d['replay_result_sha256']);pin(b/'verification/lean/RELEASE_VERIFICATION.json',d['formal_report_sha256'])
 for r in d['records']:pin(b/'formalization'/r['path'],r['sha256']);need(r['fresh_compile_status']=='PASS')
 return dict(Counter(r['group'] for r in d['records']))
chk('formal_source_bridge_current_reader_and_portable_population',bridge)
def final_summary():
 need(summary['status']=='PASS');need(final['status']=='PASS' and final['selected_status']==final['terminal_status']==final['new_interface_status']=='PASS');need(final['selected_modules_passed']==423);need(final['all_sources_unchanged'] and final['runtime_inputs_unchanged']);need(not final['external_mathlib_rebuilt'])
 for n in ['selected','terminal','new_interface']:
  r=summary['scopes'][n];need(r['compile_status']==r['axiom_audit_status']=='PASS');pin(E(r['compilation_result']['path']),r['compilation_result']['sha256']);pin(E(r['axiom_audit_result']['path']),r['axiom_audit_result']['sha256'])
 need(summary['compile_lineage']['historical_paperxi_objects_used']==False and summary['compile_lineage']['external_mathlib_cache_used']==True)
 return {'selected_status':'PASS','terminal_status':'PASS','interface_status':'PASS','same_session_resumed_project_objects':True,'historical_project_objects_seeded':False,'cold_dependency_rebuild':False}
chk('final_compile_summary_exact_scope_and_cache_boundaries',final_summary)
def lineage():
 chain=summary['compile_lineage']['result_chain_newest_first'];need(len(chain)==5)
 for r in chain:
  pin(E(r['path']),r['sha256']);q=J(E(r['path']));need(q['status']==r['status'] and q['selected_modules_passed']==r['selected_modules_passed'])
 need(chain[0]['status']=='PASS' and all(r['status']=='PARTIAL_OR_FAIL' for r in chain[1:]));need(chain[-1]['selected_modules_passed']==421)
 return {'authenticated_result_chain':5,'failed_partial_ancestors_retained':4,'first_origin_selected_passes':421,'initial_missing_lake_manifest_fingerprint_not_inferred':chain[-1]['lake_manifest_sha256'] is None}
chk('all_five_compile_lineage_receipts_and_failed_ancestors',lineage)
def final_sources():
 before=final['source_hashes_before'];need(before==final['source_hashes_after'] and len(before)==425)
 for n,h in before.items():pin(b/'formalization'/n,h)
 rows=final['modules'];need(len(rows)==425 and len({r['module'] for r in rows})==425)
 for r in rows:need(r['status']=='PASS' and r['exit_code']==0 and r['source_unchanged']);pin(b/'formalization'/r['source_path'],r['source_sha256']);pin(E(r['log_path']),r['log_sha256']);need(len(r['artifacts'])==2)
 counts.update(final_compilation_source_targets=425,final_compilation_log_records=425)
 return {'final_source_hashes':425,'successful_module_records':425,'retained_module_logs':425,'object_fingerprints_only':850}
chk('final_425_source_records_and_retained_compile_logs',final_sources)
def aggregates():
 need(len(final['aggregates'])==3)
 for r in final['aggregates']:need(r['status']=='PASS' and r['exit_code']==0);pin(b/'formalization'/r['source_path'],r['source_sha256']);pin(E(r['log_path']),r['log_sha256'])
 return {'aggregate_imports':3}
chk('three_successful_aggregate_import_log_bindings',aggregates)
def axscope(folder,scope,n,c,kinds):
 d=J(b/'verification/lean'/folder/'RESULT.json');need(d['status']=='PASS' and d['exit_code']==0 and d['scope']==scope);need(d['owned_constant_count']==n and d['catalogued_name_count']==d['catalogued_names_resolved']==c and d['owned_constant_kinds']==kinds);need(d['sources_unchanged'] and d['objects_unchanged'] and d['catalogue_owner_checks_passed'] and d['catalogue_is_subset_of_owned_constants']);need(d['source_hashes_before']==d['source_hashes_after']);need(d['object_hashes_before']==d['object_hashes_after'])
 for s,h in d['source_hashes_before'].items():pin(b/'formalization'/s,h)
 pin(E(d['source_replay_result_path']),d['source_replay_result_sha256']);pin(b/'verification/lean'/folder/'OwningModuleAudit.lean',d['audit_source_sha256']);pin(b/'verification/lean'/folder/'AXIOMS.log',d['log_sha256'])
 owned=J(b/'verification/lean'/folder/'OWNED_CONSTANTS.json');res=J(b/'verification/lean'/folder/'CATALOGUE_RESOLUTION.json');aux=J(b/'verification/lean'/folder/'COMPILER_AUXILIARIES.json');need(len(owned)==n and len(res)==c and len(aux)==d['compiler_auxiliary_count']);need(len({r['name'] for r in owned})==n and dict(Counter(r['kind'] for r in owned))==kinds);need(all(not r['unsafe'] and not r['forbidden_axioms'] and set(r['axioms'])<={'Classical.choice','Quot.sound','propext'} for r in owned))
 need(set(r['module'] for r in owned)==set(d['requested_modules']));need(Counter(r['module'] for r in owned)==d['owned_constant_counts_by_module']);need(set().union(*(set(r['axioms']) for r in owned))==set(d['observed_axioms']))
 logs=[]
 for line in (b/'verification/lean'/folder/'AXIOMS.log').read_text().splitlines():
  if line.startswith('{'):logs.append(json.loads(line))
 need([r for r in logs if r.get('event')=='owned_constant']==owned);need([r for r in logs if r.get('event')=='catalogue']==res);need([r for r in logs if r.get('event')=='compiler_auxiliary']==aux)
 names={r['name']:r for r in owned}
 for r in res:need(r['kernel_name'] in names and names[r['kernel_name']]['module']==r['module'])
 return {'owned_logical_constants':n,'kind_census':kinds,'resolved_catalogue_names':c,'compiler_only_auxiliaries':len(aux),'private_owned_names':sum(r['name'].startswith('_private.') for r in owned),'source_pins':len(d['source_hashes_before']),'saved_object_fingerprints':len(d['object_hashes_before']),'owned_constant_log_records':len(owned)}
chk('selected_7672_constant_4342_name_full_axiom_log_population',lambda:axscope('axioms_selected_release','selected',7672,4342,{'constructor':22,'definition':1447,'inductive':22,'recursor':22,'theorem':6159}))
chk('repaired_terminal_51_constant_axiom_log_population',lambda:axscope('axioms_terminal','terminal',51,0,{'definition':13,'theorem':38}))
chk('separate_interface_one_theorem_axiom_log_population',lambda:axscope('axioms_interface_final','new_interface',1,1,{'theorem':1}))
def controls():
 d=J(b/'verification/lean/axiom_controls_final/RESULT.json');need(d['status']=='PASS' and len(d['controls'])==2)
 for r in d['controls']:
  need(r['status']=='PASS' and r['exit_code']!=0);pin(b/'verification/lean/axiom_controls_final'/(r['name']+'.lean'),r['audit_source_sha256']);pin(b/'verification/lean/axiom_controls_final'/(r['name']+'.log'),r['log_sha256']);need(r['expected_error_text'] in (b/'verification/lean/axiom_controls_final'/(r['name']+'.log')).read_text())
 return {'accepted_rejections':2,'fresh_control_execution':False}
chk('accepted_axiom_controls_sources_logs_and_expected_rejections',controls)
def finite():
 d=J(b/'verification/baseline_replay/REPLAY_SUMMARY.json');need(d['status']=='passed' and d['suite_count']==6);need([d['new_release_methods'],d['preserved_publication_methods'],*d['preserved_finite_methods']]==[24,15,28,23,15,12]);need(sum([24,15,28,23,15,12])==117)
 for r in d['records']:need(r['status']=='passed' and r['returncode']==0)
 r=J(b/'verification/baseline_replay/release_tests.json');need(r==d['records'][0]['result']);pin(b/'verification/baseline_replay/release_tests.json',d['records'][0]['result_sha256'])
 counts['bounded_methods']=117
 return {'bounded_suites':6,'method_counts':[24,15,28,23,15,12],'sum_methods':117,'separate_historical_seven_program_run_included':False,'fresh_execution':False}
chk('accepted_six_suite_117_method_receipt',finite)
def sourcechanges():
 d=J(b/'evidence/release_1_1/SOURCE_CHANGE_INDEX.json');need(d['main_proof_environments']=={'before':68,'after':68,'byte_identical_bodies':65,'revised_body_indices_one_based':[30,63,65]})
 for r in d['changes']:
  if r['status']!='deleted':pin(b/r['path'],r['after_sha256'])
 return {'main_proof_environments':68,'unchanged':65,'revised_indices':[30,63,65],'reviewed_ordinary_proofs_not_new_semantic_audit':True}
chk('current_source_change_index_and_68_65_3_proof_record',sourcechanges)
def admin():
 targets=['README.md','PROGRESS_LEDGER.md','PROGRESS_LEDGER.json','MANIFEST.json'];hits={n:[] for n in targets}
 for p in b.rglob('*'):
  if p.is_file() and p.suffix in ['.json','.jsonl','.md','.txt','.py','.log'] and p.relative_to(b).as_posix()!='MANIFEST.json':
   raw=p.read_bytes()
   for n in targets:
    if H(b/n).encode() in raw:hits[n].append(p.relative_to(b).as_posix())
 need(not any(hits.values()));return {'root_admin_exact_hash_references_excluding_authoritative_manifest':hits,'safe_replacements':['README.md','MANIFEST.json'],'preserve_unchanged_review_pinned':['CONTINUE_HERE.md','RELEASE_SCOPE.md'],'reader_build_fingerprints':'publication/source subtrees only'}
chk('administrative_pins_and_source_fingerprint_boundary',admin)
def historical():
 d=J(b/'historical/INDEX.json');pin(b/d['archive'],d['archive_sha256']);entries=d['entries']
 with zipfile.ZipFile(b/d['archive']) as z:
  ns=z.namelist();need(len(ns)==len(set(ns))==len(entries)==3967);need(z.testzip() is None)
  for n in ns:safe(n)
  pref='Paper_XI_Release_1.0.0_2026-10-10/';m=json.loads(z.read(pref+'MANIFEST_SHA256.json'));need(len(m['files'])==3966)
  need(set(ns)=={pref+n for n in m['files']}|{pref+'MANIFEST_SHA256.json'})
  for n,h in m['files'].items():need(hashlib.sha256(z.read(pref+n)).hexdigest()==h,n)
  zi={q.filename:q for q in z.infolist()}
  for r in entries:need(r['member'] in zi and zi[r['member']].file_size==r['bytes'] and format(zi[r['member']].CRC,'08x')==r['crc32'])
 counts['historical_archive_members']=3967
 return {'preserved_original_zip_sha256':H(b/d['archive']),'historical_manifest_payloads':3966,'historical_index_entries':3967,'full_Block02_editable_archive_recovered':False}
chk('complete_preserved_predecessor_zip_manifest_and_search_index',historical)
def suite_bindings():
 d=J(b/'verification/baseline_replay/REPLAY_SUMMARY.json');p=J(b/'verification/baseline_replay/predecessor/REPLAY_SUMMARY.json');need(d['records'][1]['result']==p)
 pin(b/'verification/baseline_replay/predecessor/publication.json',p['records'][0]['result_sha256'])
 q=J(b/'verification/baseline_replay/predecessor/finite/REPLAY_SUMMARY.json');need(p['records'][1]['result']==q)
 hist=J(b/'historical/INDEX.json')
 with zipfile.ZipFile(b/hist['archive']) as z:
  pref='Paper_XI_Release_1.0.0_2026-10-10/';m=json.loads(z.read(pref+'MANIFEST_SHA256.json'))['files']
  srcs=[(d['records'][0],''),(d['records'][1],''),(p['records'][0],'predecessor/block06/'),(p['records'][1],'predecessor/block06/')]
  for r,base in srcs:need(m[base+r['source']]==r['source_sha256'])
  for r in q['gates']:
   local=b/'verification/baseline_replay/predecessor/finite'
   pin(local/(r['gate']+'.json'),r['result_sha256']);need(J(local/(r['gate']+'.receipt.json'))==r)
   need(m['predecessor/block06/predecessor/block05/'+r['source']]==r['source_sha256'])
 return {'six_actual_suite_sources':6,'two_wrapper_sources':2,'result_binding_records':6,'bounded_methods':117,'new_suite_execution':False}
chk('all_six_bounded_suite_sources_and_result_hashes',suite_bindings)
failures=[x for x in checks if x['status']!='PASS']
report={'schema':'komorebi.paper-xi.baseline-audit/1','status':'FAIL' if failures else 'PASS','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_root':str(b),'archive':{'file_name':a.archive.name,'bytes':a.archive.stat().st_size,'sha256':H(a.archive)},'accepted_external_receipt':{'file_name':a.receipt.name,'sha256':H(a.receipt),'scope':'Accepted v1.1.0 delivery identity and observed reader/source checks'},'checks_passed':len(checks)-len(failures),'checks_total':len(checks),'counts':counts,'checks':checks,'failures':failures,'scope_and_limits':['This authenticates saved compiler/auditor evidence, not fresh execution.','No proof-object binaries are bundled; object hash maps are authenticated saved records, not new payload comparisons.','The selected423-source population, terminal51constant scope and interface1theorem scope remain separate.','Same-session project object resumption is not historical-project reuse or cold dependency rebuild.','The archive has no root grant files; authorization for additive open-license notices is a separate freeze action.','Conjecture66 and four arithmetic tasks plus Block02 source recovery remain open.'],'baseline_read_only':True,'no_compiler_auditor_tex_science_generator_or_control_execution':True}
(out/'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'BASELINE_INTEGRITY_AUDIT.txt').write_text('Paper XI accepted-baseline freeze audit\nStatus: '+report['status']+'\nChecks: '+str(report['checks_passed'])+'/'+str(report['checks_total'])+'\n\n'+'\n'.join(x['check']+': '+x['status']+(' | '+x.get('error','')) for x in checks)+'\n\n'+'\n'.join(report['scope_and_limits'])+'\n')
print(json.dumps({'status':report['status'],'checks_passed':report['checks_passed'],'checks_total':report['checks_total'],'failures':failures},indent=2));sys.exit(bool(failures))

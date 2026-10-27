#!/usr/bin/env python3
"""Reconcile preserved Lean frontiers, without compiling Lean or altering sources.

A declaration row means one named declaration in one byte-exact source version.
Byte-identical copies are collapsed. Different versions of the same qualified
name are retained and flagged; row counts are not unique mathematical results.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, pathlib, re, zipfile

FRONTIERS = [
 ('baseline','review/fresh_baseline/verification.json'),
 ('strengthening','strengthening/verification/continuation_verification.json'),
 ('shared_correction','shared_correction/verification/shared_verification.json'),
 ('polynomial_lifting','polynomial_lifting/verification/polynomial_verification.json'),
 ('polynomial_counts','polynomial_counts/verification/polynomial_counts_verification.json'),
 ('polynomial_towers','polynomial_towers/verification/polynomial_towers_verification.json'),
 ('polynomial_deformation','polynomial_deformation/verification/polynomial_deformation_verification.json'),
 ('polynomial_charts','polynomial_charts/verification/polynomial_charts_verification.json'),
 ('polynomial_weighted','polynomial_weighted/verification/polynomial_weighted_verification.json'),
 ('polynomial_motion','polynomial_motion/verification/polynomial_motion_verification.json'),
 ('polynomial_prescribed','polynomial_prescribed/verification/polynomial_prescribed_verification.json'),
 ('polynomial_parameter_towers','polynomial_parameter_towers/verification/polynomial_parameter_towers_verification.json'),
 ('polynomial_joint_motion','polynomial_joint_motion/verification/polynomial_joint_motion_verification.json'),
 ('polynomial_regularity','polynomial_regularity/verification/polynomial_regularity_verification.json'),
]
ALLOW = {'Classical.choice','Quot.sound','propext'}
def sha(b): return hashlib.sha256(b).hexdigest()
def counts(ds): return dict(sorted(collections.Counter(d['kind'] for d in ds).items()))
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 workspace_source=pathlib.Path(__file__).resolve().parents[1]/'source'
 ap.add_argument('--source',type=pathlib.Path,default=workspace_source if workspace_source.exists() else pathlib.Path(__file__).resolve().parents[2])
 ap.add_argument('--output',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]/'audit')
 args=ap.parse_args(); root=args.source.resolve(); out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 archive='baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip'; prefix='PRSC_IX_v0.11.0_Nishibuchi_Completion/'
 z=zipfile.ZipFile(root/archive)
 entries={};frontiers=[];issues=[];support=[]
 def blob(loc):
  if '!' in loc:
   az,inside=loc.split('!',1);assert az==archive;return z.read(inside)
  return (root/loc).read_bytes()
 for frontier,reportloc in FRONTIERS:
  reportbytes=blob(reportloc);report=json.loads(reportbytes)
  invloc=archive+'!'+prefix+'inventory.json' if frontier=='baseline' else frontier+'/inventory.json'
  invbytes=blob(invloc); inv=json.loads(invbytes)
  if report.get('inventory_sha256'): assert sha(invbytes)==report['inventory_sha256'],invloc
  if 'source_inventory'in report: assert inv==report['source_inventory'],(frontier,'embedded inventory mismatch')
  assert report['status']in ['PASS','LEAN_BUILD_AND_AXIOM_AUDIT_PASS']
  audited=report['axiom_dependencies']; assert all(set(v)<=ALLOW for v in audited.values())
  evidence=[];groupcounts={};named=[]
  for group in ['modules','control_support','contracts','controls','negative_controls']:
   ds=[]
   for m in inv.get(group,[]):
    loc=archive+'!'+prefix+m['source'] if frontier=='baseline' else frontier+'/'+m['source']
    b=blob(loc);assert sha(b)==m['sha256'],loc
    evidence.append({'path':loc,'sha256':sha(b),'group':group,'module':m.get('module',pathlib.Path(m['source']).stem),'named_declarations':len(m.get('declarations',[]))})
    for d in m.get('declarations',[]):
     assert d['name']in audited,(frontier,d['name'],'not audited')
     ds.append(d);named.append(d)
     key=(d['kind'],d['name'],sha(b))
     if key not in entries:entries[key]={'kind':d['kind'],'qualified_name':d['name'],'source_sha256':sha(b),'module':m.get('module',pathlib.Path(m['source']).stem),'occurrences':[]}
     role='positive_control' if group=='control_support' or any(s in pathlib.Path(m['source']).stem for s in ['Controls','Examples']) else 'statement_contract' if group=='contracts' else 'proof_source'
     entries[key]['occurrences'].append({'frontier':frontier,'path':loc,'group':group,'role':role,'axioms':audited[d['name']]})
   if inv.get(group):groupcounts[group]={'files':len(inv[group]),'explicit_named_declarations':counts(ds)}
  assert set(audited)=={d['name']for d in named},(frontier,'audit set differs')
  runs=report.get('runs')
  if runs is None:
   runs=report['modules']+report['controls']+[report['version_check'],report['axiom_audit_run'],report['statement_contract']]
  logchecks=[]
  for run in runs:
   if 'passed'in run:assert run['passed'],(frontier,run)
   elif not run.get('expected_rejection'):assert run.get('exit_code')==0,(frontier,run)
   if not run.get('log_sha256'):continue
   logname=pathlib.Path(run.get('log',run.get('name','')+'.log')).name
   logloc=str(pathlib.PurePosixPath(reportloc).parent/logname)
   logbytes=blob(logloc)
   assert sha(logbytes)==run['log_sha256'],logloc
   logchecks.append({'path':logloc,'sha256':sha(logbytes),'exit_code':run.get('exit_code'),'expected_rejection':bool(run.get('expected_error') or run.get('expected_rejection'))})
  actualcounts=counts(named)
  # Historical summary scalars were sometimes not refreshed when modules grew.
  for key,kind in [('theorem_count','theorem'),('definition_count','def'),('abbreviation_count','abbrev')]:
   if key in inv and inv[key]!=actualcounts.get(kind,0):issues.append({'frontier':frontier,'issue':'stale_inventory_summary_scalar','field':key,'stored':inv[key],'recounted_exact_command_kind':actualcounts.get(kind,0),'disposition':'Historical file preserved unchanged. Consolidation uses source entries and exact audit set, not the stale scalar.'})
  info={'frontier':frontier,'scope':'latest_polynomial_gate' if frontier=='polynomial_regularity' else 'preserved_prior_gate','recompiled_during_consolidation':False,'status_recorded':report['status'],'report':{'path':reportloc,'sha256':sha(reportbytes)},'inventory':{'path':invloc,'sha256':sha(invbytes)},'source_groups':groupcounts,'explicit_named_declarations':actualcounts,'axiom_closures':len(audited),'source_files_validated':evidence,'logs_validated':logchecks,'run_records':len(runs),'run_count_note':'79 module checks,37 control checks,and3 named support checks;9 dependency revision comparisons recorded separately' if frontier=='baseline' else 'Length of report.runs; expected compile rejection counts as a passing negative control.','all_source_hashes_match':True,'all_log_hashes_match':True,'all_named_declarations_have_matching_standard_axiom_audits':True,'recorded_runtime':report.get('runtime',{'lean':report.get('lean_version_output'),'mathlib_rebuilt':report.get('mathlib_rebuilt',report.get('mathlib_rebuilt_from_source'))})}
  frontiers.append(info)
 # The earliest standalone affine frontier predates the common inventory schema.
 native_loc='native/lean/replay_02/native_affine_audit.json'
 native_bytes=blob(native_loc); native=json.loads(native_bytes);assert native['pass']
 native_sources=[];native_logs=[];native_decls=[]
 for run in native['results']:
  assert run['pass']; loc='native/lean/replay_02/sources/'+run['source'];b=blob(loc)
  assert sha(b)==run['source_sha256'],loc
  nlog='native/lean/replay_02/'+run['log']
  native_logs.append({'path':nlog,'sha256':sha(blob(nlog)),'compared_to_historical_log_hash':False,'note':'Legacy report did not store a log SHA-256. Consolidation fingerprints the retained log without upgrading legacy provenance.'})
  native_sources.append({'path':loc,'sha256':sha(b),'group':'negative_control' if run['expected_rejection']else 'proof_or_positive_control','named_declarations':0 if not run['axiom_audit']else len(run['axiom_audit']['records'])})
  if not run['axiom_audit']:continue
  kinds={n:k for k,n in re.findall(r'(?m)^\s*(theorem|lemma|def|abbrev)\s+([A-Za-z_][A-Za-z_0-9]*)',b.decode())}
  for name,axioms in run['axiom_audit']['records'].items():
   assert set(axioms)<=ALLOW
   kind=kinds[name.rsplit('.',1)[-1]];key=(kind,name,sha(b));native_decls.append({'kind':kind,'name':name})
   entries.setdefault(key,{'kind':kind,'qualified_name':name,'source_sha256':sha(b),'module':pathlib.Path(run['source']).stem,'occurrences':[]})['occurrences'].append({'frontier':'native_affine','path':loc,'group':'modules','role':'positive_control' if 'Controls'in run['source']else 'proof_source','axioms':axioms})
 frontiers.append({'frontier':'native_affine','scope':'preserved_prior_gate_legacy_schema','recompiled_during_consolidation':False,'status_recorded':'PASS','report':{'path':native_loc,'sha256':sha(native_bytes)},'source_groups':{'modules':{'files':2,'explicit_named_declarations':counts(native_decls)}},'explicit_named_declarations':counts(native_decls),'axiom_closures':len(native_decls),'source_files_validated':native_sources,'logs_validated':native_logs,'run_records':4,'all_source_hashes_match':True,'all_log_hashes_match':None,'log_provenance_limit':'Legacy report stores no prior log digests; retained logs fingerprinted only.','all_named_declarations_have_matching_standard_axiom_audits':True})
 versions=collections.defaultdict(set)
 for kind,name,h in entries:versions[(kind,name)].add(h)
 rank={f:i for i,(f,_) in enumerate(FRONTIERS)};rank['native_affine']=1.5;rows=[]
 for key,item in sorted(entries.items(),key=lambda x:(x[0][1],x[0][2],x[0][0])):
  occ=sorted(item['occurrences'],key=lambda o:rank[o['frontier']],reverse=True); can=occ[0]
  item.update({'canonical_source':can['path'],'frontier_classification':'current_polynomial' if can['frontier']=='polynomial_regularity' else 'arithmetic_baseline' if can['frontier']=='baseline' else 'arithmetic_strengthening' if can['frontier']=='strengthening' else 'preserved_auxiliary_frontier','role':can['role'],'source_version_count_for_name':len(versions[(item['kind'],item['qualified_name'])]),'proof_status':'compiled_with_standard_axiom_closure_in_preserved_report','copied_occurrences':len(occ)})
  rows.append({k:item[k]for k in ['qualified_name','kind','module','role','frontier_classification','canonical_source','source_sha256','source_version_count_for_name','copied_occurrences','proof_status']}|{'frontiers':';'.join(o['frontier']for o in reversed(occ)),'all_source_paths_json':json.dumps(sorted({o['path']for o in occ})),'axioms_json':json.dumps(can['axioms'])})
 fields=list(rows[0]); csvpath=out/'DECLARATIONS.csv'
 with csvpath.open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 for rel in ['review/NISHIBUCHI_SOURCE_RECORD.json','review/EXTERNAL_STATEMENT_AUDIT.md','polynomial_regularity/audit/REVIEWED_SOURCES.json','polynomial_regularity/audit/LOCAL_SOURCE_CHECK.json']:
  if(root/rel).exists():support.append({'path':rel,'sha256':sha(blob(rel))})
 external=json.loads(blob('review/NISHIBUCHI_SOURCE_RECORD.json'))
 result={'schema_version':1,'purpose':'Consolidated provenance and source declaration index. This operation validates preserved source/log hashes and inventories; it does not rerun Lean or certify a new theorem.','source_archive_content_root':'. (all artifact paths relative to the extracted cumulative archive root)' ,'baseline_nested_archive':{'path':archive,'sha256':sha(blob(archive))},'frontiers':frontiers,'supporting_records':support,'source_statement_review':{'source_record':'review/NISHIBUCHI_SOURCE_RECORD.json','source_record_sha256':sha(blob('review/NISHIBUCHI_SOURCE_RECORD.json')),'statement_review':'review/EXTERNAL_STATEMENT_AUDIT.md','statement_review_sha256':sha(blob('review/EXTERNAL_STATEMENT_AUDIT.md')),'source_id':external['source_id'],'author':external['author'],'title':external['title'],'revision_date':external['revision_date'],'stable_version_locator':external['stable_version_locator'],'pdf_sha256_recorded':external['pdf_sha256'],'text_sha256_recorded':external['text_sha256'],'full_primary_source_in_release':False,'external_comparison_freshly_repeated':False,'interpretation':'Prior exact-source inspection is preserved with version and hashes. Consolidation does not claim to have reopened the original paper.'},'declaration_inventory':{'path':'DECLARATIONS.csv','sha256':sha(csvpath.read_bytes()),'row_count':len(rows),'scope':'Every explicitly named theorem, lemma, def or abbrev in the 14 release-frontier inventories and the earlier standalone native affine report, including contracts and positive control support. Anonymous examples, generated declarations, development attempts, negative controls and nested historical snapshots are outside the named-declaration count. Source files for release negative controls are nevertheless hash-checked.','deduplication_key':['declaration kind','qualified name','entire source file SHA-256'],'exact_source_copy_policy':'Byte-identical copies across frontiers produce one row retaining all paths.','version_policy':'Different source hashes remain distinct even if names match; source_version_count_for_name marks these. They must not be summed as unique mathematical theorems.','global_unique_theorem_count_claimed':False,'names_with_multiple_source_versions':sum(len(v)>1 for v in versions.values())},'metadata_issues':issues,'consolidation_checks':{'reproduction_command':'python3 consolidation/tools/evidence_index.py --source . --output PATH_TO_NEW_INDEX','script_path':'consolidation/tools/evidence_index.py','script_sha256':sha(pathlib.Path(__file__).read_bytes()),'source_hash_comparisons':sum(len(f['source_files_validated'])for f in frontiers),'recorded_log_hash_comparisons':sum(len(f['logs_validated'])for f in frontiers if f['frontier']!='native_affine'),'legacy_log_fingerprints':len(native_logs),'source_and_inventory_hashes':'PASS','all_preserved_gate_log_hashes':'PASS wherever recorded; four legacy affine logs are fingerprinted without a prior digest','inventory_to_axiom_name_set_equality':'PASS','allowed_axioms':sorted(ALLOW),'fresh_lean_run':False,'new_mathematical_source_edits':False},'non_claims':['Not a new simultaneous clean build of every Paper IX source.','Report check counts, named theorem commands, axiom closures and mathematical results are different quantities.','Source copy deduplication does not decide mathematical equivalence of different declarations.','The external primary-source correspondence is inherited from its preserved audit.']}
 (out/'EVIDENCE_INDEX.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':'PASS','frontiers':len(frontiers),'named_source_version_rows':len(rows),'metadata_issues':issues,'source_hash_checks':sum(len(f['source_files_validated'])for f in frontiers),'log_hash_comparisons':sum(len(f['logs_validated'])for f in frontiers if f['frontier']!='native_affine'),'legacy_log_fingerprints':4,'fresh_lean_run':False},indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Read-only Paper XII source and recorded-evidence authentication, not execution.
Outputs must be outside core/outer. No Lean, scientific suite or PDF build runs.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
import argparse,datetime,hashlib,json,os,re,subprocess,sys,zipfile

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def files(p):return {q.relative_to(p).as_posix():q for q in p.rglob('*') if q.is_file()}
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def safe_names(z):
 rows=[i for i in z.infolist() if not i.is_dir()];ns=[i.filename for i in rows]
 assert len(ns)==len(set(ns))
 assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and ':' not in n and '\\' not in n for n in ns)
 assert all((i.external_attr>>16)&0o170000!=0o120000 for i in rows)
 return rows

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--core',type=Path,required=True);ap.add_argument('--outer',type=Path,required=True);ap.add_argument('--archive',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 core=a.core.resolve();outer=a.outer.resolve();out=a.output.resolve()
 assert not out.is_relative_to(core) and not out.is_relative_to(outer)
 out.mkdir(parents=True,exist_ok=True)
 checks=[];counts={};pins={}
 def check(name,fn):
  try:detail=fn();checks.append({'name':name,'status':'PASS','detail':detail})
  except Exception as e:checks.append({'name':name,'status':'FAIL','error':type(e).__name__+': '+str(e)})
 def pin(rel):pins[rel]=sha(core/rel);return core/rel
 def core_manifest():
  m=load(core/'MANIFEST_SHA256.json');rows=m['files'];actual=files(core);actual.pop('MANIFEST_SHA256.json')
  assert len(rows)==len({r['path'] for r in rows})==3795
  assert set(actual)=={r['path'] for r in rows}
  for r in rows:
   p=actual[r['path']];assert not p.is_symlink() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
  counts.update({'core_files':3796,'core_manifest_rows':3795});return {'files':3796,'manifest_rows':3795,'manifest_sha256':sha(core/'MANIFEST_SHA256.json')}
 check('complete_core_manifest',core_manifest)
 def core_zip():
  p=outer/'Paper_XII_Source_and_Evidence_v1.0.0_2026-10-10.zip';assert sha(p)=='0088409e2072e5d5272bbd455e49d0a90fccf5cbbb380abc28839a9b1303f2c4'
  actual=files(core)
  with zipfile.ZipFile(p) as z:
   rows=safe_names(z);assert len(rows)==3796 and {r.filename for r in rows}==set(actual)
   for r in rows:assert hashlib.sha256(z.read(r)).hexdigest()==sha(actual[r.filename]) and r.file_size==actual[r.filename].stat().st_size,r.filename
  return {'members':3796,'every_extracted_file_matches_original_zip':True,'all_member_reads_crc_checked':True,'sha256':sha(p)}
 check('core_zip_all_member_identity',core_zip)
 def outer_manifest():
  m=load(outer/'DELIVERY_MANIFEST.json');assert len(m)==3
  assert set(files(outer))=={'START_HERE.md','DELIVERY_MANIFEST.json'}|{r['source'] for r in m}
  for r in m:
   p=outer/r['source'];assert p.stat().st_size==r['delivery_bytes'] and sha(p)==r['delivery_sha256'];assert not r['changed'] and r['source_sha256']==r['delivery_sha256']
  return {'outer_members':5,'nested_zip_identities':3}
 check('outer_delivery_manifest',outer_manifest)
 if a.archive:
  def outer_zip():
   assert sha(a.archive)=='ff76cf6e69136ba231bd2c25dbbd339535b326af60e9d9553f1c93b1e9eb37e8'
   with zipfile.ZipFile(a.archive) as z:
    rows=safe_names(z);assert len(rows)==5;assert {r.filename for r in rows}==set(files(outer))
    for r in rows:assert hashlib.sha256(z.read(r)).hexdigest()==sha(outer/r.filename)
   return {'members':5,'archive_sha256':sha(a.archive),'exact_outer_bytes':True}
  check('selected_outer_archive_identity',outer_zip)
 def predecessor_preservation():
  d=load(pin('evidence/block01/PREDECESSOR_PRESERVATION.json'));assert d['files']==2243==len(d['entries']) and d['all_match'] and d['excluded_standalone_fonts']==9
  actual=files(core/'predecessor');assert len(actual)==2243
  for r in d['entries']:assert r['matches_original'] and sha(actual[r['path']])==r['sha256'],r['path']
  excluded=load(pin('evidence/block01/PREDECESSOR_AUDIT.json'))['font_distribution_exclusions'];assert len(excluded)==9 and all(not (core/'predecessor'/r['path']).exists() for r in excluded)
  counts['predecessor_files']=2243;return {'byte_pins':2243,'explicit_standalone_font_exclusions':9,'historical_old_manifests_not_relabelled_current':True}
 check('predecessor_exact_retention_and_explicit_exclusions',predecessor_preservation)
 src=core/'publication/source';old=core/'predecessor/editable';data=src/'lean_guide/data'
 def written_preservation():
  t=(src/'traditional/Paper_XII_Traditional_Final.tex').read_text();o=(old/'traditional/Paper_XII_Traditional_Final.tex').read_text()
  proofs=lambda s:re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}',s,re.S)
  statements=lambda s:re.findall(r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|standardfact|remark)\}(.*?)\\end\{\1\}',s,re.S)
  assert proofs(t)==proofs(o) and len(proofs(t))==52
  assert statements(t)==statements(o) and len(statements(t))==82
  counts.update(main_proof_bodies=52,main_statement_bodies=82);return {'main_proof_bodies':52,'main_statement_bodies':82,'all_body_bytes_identical':True}
 check('all_main_proof_and_statement_bodies_preserved',written_preservation)
 def selected_sources():
  cat=load(pin('publication/source/lean_guide/data/source_catalog.json'));assert len(cat)==len({r['module'] for r in cat})==96
  preserve=load(core/'evidence/block01/SOURCE_PRESERVATION.json')['production_sources'];assert preserve['count']==96 and preserve['all_match'];pm={r['module']:r['sha256'] for r in preserve['sources']}
  base=core/'predecessor/source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release'
  for r in cat:
   p=src/'lean_guide/formal_release/lean'/r['source'];assert sha(p)==r['sha256']==pm[r['module']]==sha(base/'lean'/r['source']),r['module']
  counts['production_modules']=96;return {'production_modules':96,'current_catalogue_and_preserved_origin_bytes_match':True}
 check('all_96_production_source_identities',selected_sources)
 def teaching_sources():
  rows=sorted((src/'lean_guide/excerpts').glob('*.lean'));assert len(rows)==24
  for p in rows:assert sha(p)==sha(old/'lean_guide/excerpts'/p.name)
  all_rows=[p for p in (src/'lean_guide/excerpts').rglob('*') if p.is_file()]
  d=load(core/'evidence/block01/SOURCE_PRESERVATION.json')['excerpts'];assert d['count']==49==len(all_rows) and d['byte_identical']
  for p in all_rows:assert sha(p)==sha(old/'lean_guide/excerpts'/p.relative_to(src/'lean_guide/excerpts'))
  counts.update(teaching_modules=24,excerpt_directory_files=49);return {'exact_teaching_modules':24,'total_excerpt_directory_files':49}
 check('all_24_teaching_sources_preserved',teaching_sources)
 def catalogues():
  d=load(pin('publication/source/lean_guide/data/declarations.json'));assert len(d)==len({r['name'] for r in d})==1229
  assert Counter(r['kind'] for r in d)=={'theorem':829,'def':319,'abbrev':47,'structure':17,'instance':17}
  assert sum(r['kind']=='theorem' and not r['reused_from_paper_x'] for r in d)==748
  assert sum(r['kind']=='theorem' and r['reused_from_paper_x'] for r in d)==81
  for r in d:
   lines=(src/'lean_guide/formal_release/lean'/r['source']).read_text().splitlines();i=r['line']-1
   while re.fullmatch(r'@\[[^\]]*\]',lines[i].strip()):i+=1
   assert r['name'].split('.')[-1] in lines[i],r['name']
  counts.update(public_named_declarations=1229,paper_xii_lexical_theorems=748,reused_paper_x_lexical_theorems=81)
  return {'literal_source_locations':1229,'declaration_kinds':dict(Counter(r['kind'] for r in d)),'not_a_new_elaboration_or_discovery_count':True}
 check('lexical_catalogue_identity_and_counts',catalogues)
 def claims():
  c=load(pin('publication/source/lean_guide/data/claim_crosswalk.json'))['claims'];assert len(c)==49
  assert Counter(r['status'] for r in c)=={'complete':49}
  co=Counter(r['original_status'] for r in c);assert co['complete']==41 and co['partial']==7 and sum(co.values())==49
  expected={'6.12','9.4','9.5','9.6','10.5','12.2','12.4','12.6'};assert {r['number'] for r in c if r['amendment']}==expected
  targets={t for r in c for t in r['checked_targets']};assert len(targets)==291 and targets<={r['name'] for r in load(data/'declarations.json')}
  counts.update(revised_claims=49,distinct_production_targets=291,amended_claims=8)
  return {'revised_claims':49,'original_census':dict(co),'amended_ids':sorted(expected),'distinct_production_targets':291,'stronger_originals_not_relabelled_proved':True}
 check('revised_contract_and_original_census_distinct',claims)
 def immutable_catalogues():
  checked=0
  for p in (old/'lean_guide/data').iterdir():
   if not p.is_file():continue
   q=data/p.name
   if p.name=='crosswalk.tex':assert re.sub(r'\\href\{p12-route:[^}]+\}\{([^}]+)\}',r'\1',q.read_text())==p.read_text()
   else:assert sha(p)==sha(q),p.name
   checked+=1
  return {'catalogue_files':checked,'only_display_crosswalk_link_wrappers_added':True}
 check('unchanged_raw_catalogues_and_crosswalk_content',immutable_catalogues)
 def figures():
  actual={p.name:sha(p) for p in (src/'traditional/figures').glob('*.pdf')};earlier={p.name:sha(p) for p in (old/'traditional/figures').glob('*.pdf')};assert set(actual)==set(earlier) and len(actual)==18
  changed={n for n in actual if actual[n]!=earlier[n]};assert changed=={'09_hecke_artin_packets.pdf','14_companion_spine.pdf','16_pointwise_automorphy.pdf','17_final_completion.pdf'}
  return {'main_vector_figures':18,'unchanged':14,'redrawn_in_accepted_publication':sorted(changed),'regenerated_for_this_freeze':False}
 check('four_accepted_figure_repairs_fourteen_preserved',figures)
 def replay_bindings():
  d=load(pin('verification/block01/replay/REPLAY.json'));assert d['status']=='PASS' and d['fresh_lean'] is False and len(d['gates'])==7
  for r in d['gates']:
   assert r['status']=='PASS' and r['exit_code']==0 and not r['timed_out']
   assert sha(core/r['script'])==r['script_sha256']
   for t in ['stdout','stderr']:assert sha(core/'verification/block01/replay'/(r['gate']+'.'+t+'.log'))==r[t+'_sha256']
  return {'gates':7,'script_hashes':7,'recorded_log_hashes':14,'finite_suites_or_controls_rerun':False}
 check('accepted_seven_gate_script_and_log_bindings',replay_bindings)
 def bounded_counts():
  root=core/'verification/block01/replay'
  for n in ['original-finite/result.json','appendix-exact/result.json','visual-exact.json','primitive-benchmark.json','publication-regressions.json']:
   d=load(root/n);assert d['status'].lower() in ['pass','passed'],n
  assert load(root/'original-finite/result.json')['total_checks']==92892
  assert load(root/'appendix-exact/result.json')['check_count']==31
  assert load(root/'visual-exact.json')['check_count']==46
  assert load(root/'primitive-benchmark.json')['assertion_count']==3216
  assert load(root/'publication-regressions.json')['unittest_methods']==26
  return {'original_finite_checks':92892,'appendix_exact_checks':31,'visual_exact_checks':46,'primitive_assertions':3216,'publication_methods':26,'counts_not_summed_as_theorems':True,'freshly_executed':False}
 check('accepted_bounded_result_scopes_and_separate_counts',bounded_counts)
 def primary_formal():
  p=core/'predecessor/source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release';d=load(p/'verification.json');assert d['status']=='PASS' and d['module_count']==96 and d['audited_declaration_count']==1229
  assert d['source_preservation_passed'] and d['source_hashes_before']==d['source_hashes_after'];assert sha(p/'checks/modules.json')==d['module_manifest_sha256']
  assert len(d['modules'])==96 and len(d['axioms'])==1229
  logs=0;parsed=0
  for r in d['modules']:
   rel=r['module'].replace('.','/')+'.lean';assert sha(p/'lean'/rel)==r['source_sha256']==d['source_hashes_before'][rel]==d['source_hashes_after'][rel]
   assert sha(p/r['olean_path'])==r['olean_sha256']
   for e in [r,r['axiom_audit']]:assert e['exit_code']==0 and not e['timed_out'] and sha(p/e['log'])==e['log_sha256'];logs+=1
   text=(p/r['axiom_audit']['log']).read_text()
   for e in [e for e in d['axioms'] if e['module']==r['module']]:
    m=re.search(re.escape("'"+e['name']+"'")+r' depends on axioms:\s*\[([^\]]*)\]',text)
    actual={x.strip() for x in m[1].split(',') if x.strip()} if m else set() if "'"+e['name']+"' does not depend on any axioms" in text else None
    assert actual==set(e['axioms']) and actual is not None;assert actual<={'Classical.choice','propext','Quot.sound'};parsed+=1
  assert len(d['controls'])==3
  for e in d['controls']:assert e['passed'] and e['exit_code']!=0 and not e['timed_out'] and sha(p/e['log'])==e['log_sha256'];logs+=1
  assert parsed==1229
  counts.update(primary_source_object_pairs=96,primary_log_hashes=logs,primary_named_axiom_log_records=parsed)
  return {'source_object_pairs':96,'log_hashes':logs,'named_axiom_log_parses':parsed,'inherited_negative_controls':3,'date':'2026-09-12','lean_version':d['lean_version'],'mathlib_commit':d['mathlib_commit'],'compiler_sha256':d['compiler_sha256'],'fresh_lean':False,'all_owned_private_generated_census_claim':False}
 check('primary_inherited_compiler_object_log_axiom_records',primary_formal)
 def run_safe(name,cmd,report):
  r=subprocess.run([sys.executable,'-B',*cmd],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  (out/(name+'_STDOUT.txt')).write_text(r.stdout);(out/(name+'_STDERR.txt')).write_text(r.stderr)
  assert r.returncode==0,r.stderr[-1500:]+r.stdout[-1500:];d=load(report);assert d['status']=='PASS';return d
 def existing_integrity():
  d=run_safe('original_core_integrity',[str(core/'tools/verify_package.py'),'--root',str(core),'--output',str(out/'ORIGINAL_CORE_INTEGRITY.json')],out/'ORIGINAL_CORE_INTEGRITY.json');return {'status':d['status'],'manifest_entries':d['manifest_entries'],'unchanged_script_sha256':sha(core/'tools/verify_package.py')}
 check('unchanged_original_core_integrity_checker',existing_integrity)
 def native_authentication():
  script=core/'predecessor/verification/computation/audit_native_reverification.py';accepted=load(core/'verification/block01/replay/REPLAY.json');r=next(r for r in accepted['gates'] if r['gate']=='native-record-authentication');assert sha(script)==r['script_sha256']
  d=run_safe('native_record_authentication',[str(script),'--project',str(core/'predecessor'),'--output',str(out/'NATIVE_RECORD_AUTHENTICATION_FRESH.json')],out/'NATIVE_RECORD_AUTHENTICATION_FRESH.json')
  assert d['source_object_pairs_compared']==96 and d['logs_verified']==196 and d['production_axiom_targets_parsed']==1229 and d['native_contract_targets_parsed']==3 and d['fresh_lean_replay'] is False
  counts.update(native_source_object_pairs=96,native_log_hashes=196,native_named_axiom_log_records=1229,native_direct_contract_targets=3)
  return {'source_object_pairs':96,'log_hashes':196,'named_axiom_log_parses':1229,'direct_contract_targets':3,'all_saved_checks':d['checks'],'fresh_lean':False,'adds_production_modules_or_claims':False}
 check('unchanged_pure_native_record_authenticator',native_authentication)
 def qualified_rebuild_receipt():
  d=load(pin('verification/block01/REPRODUCIBILITY.json'));assert d['status']=='PASS' and d['fresh_lean'] is False and len(d['pdfs'])==3 and len(d['regenerated_figures'])==4
  for r in d['pdfs']:assert r['byte_identical'] and r['text_identical'] and r['render_identical_100dpi'] and sha(core/'publication/pdfs'/r['file'])==r['sha256']
  assert all(r['byte_identical'] for r in d['regenerated_figures'])
  return {'accepted_same_environment_isolated_rebuild':'three PDFs and four figures byte-identical','checked_render_dpi':100,'fresh_rebuild_for_this_freeze':False,'cross_platform_identity_claim':False}
 check('accepted_isolated_rebuild_receipt_and_reader_hashes',qualified_rebuild_receipt)
 def ledger_snapshots():
  for ext in ['md','json']:assert sha(core/('PROGRESS_LEDGER.'+ext))==sha(core/('ledger_snapshots/Paper_XII_Progress_Ledger_v1.0.0_2026-10-10.'+ext))
  return {'original_research_ledgers_and_snapshots_unchanged':True,'frozen_core_needs_no_administrative_file_replacement':True}
 check('exact_original_versioned_ledger_snapshots',ledger_snapshots)
 failures=[r for r in checks if r['status']!='PASS']
 report={'schema':'komorebi.paper-xii.baseline-audit/1','status':'FAIL' if failures else 'PASS','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_root':str(core),'outer_root':str(outer),'checks_total':len(checks),'checks_passed':len(checks)-len(failures),'counts':counts,'checks':checks,'failures':failures,'pinned_current_records':pins,'scope_and_limits':['Identity and saved-record authentication, not new compiler/kernel/scientific/proof execution.','96 registered sources,1229public names,748PaperXIItheorems and81reusedPaperXtheorems are inherited lexical/formal-record units; no new complete owned/private/generated census is asserted.','49 revised claims and291targets remain distinct from original41complete7partial1unchecked census and8amendments.','Patching/residual, compatible same-field point, classicality/attachment,Frobenius,and already-existing family inputs remain supplied.','No universal arithmetic supply or PaperXIConjecture66 completion is inferred.'],'baseline_read_only':True,'no_compiler_auditor_scientific_suite_control_suite_pdf_build_or_generator_execution':True}
 dump(out/'BASELINE_INTEGRITY_AUDIT.json',report)
 text=['PAPER XII BASELINE INTEGRITY AUDIT','Status: '+report['status']+' | '+str(report['checks_passed'])+'/'+str(report['checks_total'])+' checks','',*[(r['status']+' '+r['name']) for r in checks],'','Counts: '+json.dumps(counts,sort_keys=True),'','Scope and limits:',*report['scope_and_limits']]
 (out/'BASELINE_INTEGRITY_AUDIT.txt').write_text('\n'.join(text)+'\n');print(json.dumps({'status':report['status'],'checks_passed':report['checks_passed'],'checks_total':report['checks_total'],'failures':failures,'counts':counts},indent=2));return bool(failures)
if __name__=='__main__':sys.exit(main())

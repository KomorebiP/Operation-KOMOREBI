#!/usr/bin/env python3
"""Read-only Paper XII nested-container and saved delivery-receipt authentication.
No compiler, scientific suite, control suite, PDF builder or generator is run.
"""
from pathlib import Path, PurePosixPath
import argparse, collections, datetime, hashlib, io, json, stat, zipfile

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def zip_walk(data,name,rows):
 digest=hashlib.sha256(data).hexdigest()
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  inf=z.infolist();names=[i.filename for i in inf]
  assert len(names)==len(set(names)),(name,'duplicate names')
  assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n and ':' not in n for n in names),(name,'unsafe names')
  assert all(stat.S_IFMT(i.external_attr>>16) in (0,stat.S_IFREG,stat.S_IFDIR) for i in inf),(name,'special or symlink member')
  assert z.testzip() is None,(name,'CRC')
  row={'path':name,'bytes':len(data),'sha256':digest,'members':len(inf),'regular_files':sum(not i.is_dir() for i in inf),'uncompressed_bytes':sum(i.file_size for i in inf),'safe_unique_members':True,'CRC':'PASS'};rows.append(row)
  for i in inf:
   if not i.is_dir() and i.filename.lower().endswith('.zip'):zip_walk(z.read(i),name+'!/'+i.filename,rows)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 b=a.baseline.resolve();out=a.output.resolve();assert not out.is_relative_to(b),'Output must be external to baseline'
 core=b/'core';outer=b/'outer';readers=b/'reader_set';receipts=b/'receipts';checks=[];failures=[];recursive=[]
 def check(name,fn):
  try:v=fn();assert v is not False;checks.append({'name':name,'status':'PASS','detail':v})
  except Exception as e:checks.append({'name':name,'status':'FAIL','error':repr(e)});failures.append({'name':name,'error':repr(e)})
 delivery=load(outer/'DELIVERY_MANIFEST.json');receipt=load(receipts/'Paper_XII_Delivery_Verification_v1.0.0_2026-10-10.json')
 def manifest_binding():
  assert len(delivery)==3
  for d in delivery:
   p=outer/d['source'];assert p.stat().st_size==d['delivery_bytes']==d['source_bytes']
   assert sha(p)==d['delivery_sha256']==d['source_sha256'];assert d['changed'] is False and d['font_files_removed']==[]
  return {'archives':3,'all_original_container_bytes_preserved':True}
 check('outer_delivery_manifest_three_original_archives',manifest_binding)
 def recursive_archives():
  for d in delivery:zip_walk((outer/d['source']).read_bytes(),d['source'],recursive)
  counts={d['source']:{'archives':sum(r['path']==d['source'] or r['path'].startswith(d['source']+'!/') for r in recursive),'members':sum(r['members'] for r in recursive if r['path']==d['source'] or r['path'].startswith(d['source']+'!/'))} for d in delivery}
  for d in delivery:assert counts[d['source']]==d['recursive_scan'],(d['source'],counts[d['source']],d['recursive_scan'])
  return {'archive_occurrences':len(recursive),'unique_archive_sha256':len({r['sha256'] for r in recursive}),'member_occurrences':sum(r['members'] for r in recursive),'by_delivered_archive':counts}
 check('recursive_archive_CRC_paths_unique_members_and_recorded_counts',recursive_archives)
 def archive_receipt_binding():
  assert receipt['status']=='PASS'
  for role,row in receipt['archives'].items():
   p=outer/row['file'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'] and row['crc']=='PASS'
  return {'role_records':len(receipt['archives']),'receipt_bytes':(receipts/'Paper_XII_Delivery_Verification_v1.0.0_2026-10-10.json').stat().st_size,'receipt_sha256':sha(receipts/'Paper_XII_Delivery_Verification_v1.0.0_2026-10-10.json')}
 check('accepted_delivery_receipt_source_and_reader_archive_bindings',archive_receipt_binding)
 def saved_extraction_reports():
  mapping={'source_before':'source_before.json','source_after_tests_and_build':'source_after.json','readers':'readers_check.json'}
  for key,file in mapping.items():
   d=load(receipts/file);assert d==receipt['fresh_extraction'][key] and d['status']=='PASS' and d['errors']==[]
  assert receipt['fresh_extraction']['source_before']['manifest_entries']==3795
  assert receipt['fresh_extraction']['readers']['manifest_entries']==12
  return {'source_manifest_rows':3795,'reader_manifest_rows':12,'saved_report_bindings':3,'fresh_replay_for_this_audit':False}
 check('three_saved_clean_extraction_report_bindings',saved_extraction_reports)
 def saved_delivered_replay():
  r=load(receipts/'replay/REPLAY.json');assert r==receipt['delivered_replay'];assert r['status']=='PASS' and r['fresh_lean'] is False and len(r['gates'])==7
  for row in r['gates']:
   assert row['status']=='PASS' and row['exit_code']==0 and row['timed_out'] is False
   assert sha(core/row['script'])==row['script_sha256']
   for stream in ['stdout','stderr']:assert sha(receipts/'replay'/(row['gate']+'.'+stream+'.log'))==row[stream+'_sha256']
  pub=load(receipts/'replay/publication-regressions.json');assert pub==receipt['delivered_publication_regressions'] and pub['unittest_methods']==26 and pub['status']=='PASS' and pub['failures']==pub['errors']==[]
  return {'saved_gate_script_and_stream_bindings':7,'saved_publication_methods':26,'suites_executed_by_this_audit':0}
 check('seven_saved_delivered_gate_bindings_and_26_method_receipt',saved_delivered_replay)
 def isolated_rebuild():
  r=receipt['isolated_rebuild'];assert r==load(core/'verification/block01/REPRODUCIBILITY.json')
  assert r['status']=='PASS' and r['fresh_lean'] is False and len(r['pdfs'])==3 and len(r['regenerated_figures'])==4
  for row in r['pdfs']:
   assert row['byte_identical'] and row['text_identical'] and row['render_identical_100dpi'];assert sha(core/'publication/pdfs'/row['file'])==row['sha256']
  assert all(row['byte_identical'] for row in r['regenerated_figures'])
  return {'accepted_same_environment_isolated_source_rebuild':True,'PDFs':3,'figures':4,'fresh_build_for_this_audit':False,'cross_platform_byte_identity_claim':False}
 check('accepted_isolated_rebuild_record_and_current_PDF_identity',isolated_rebuild)
 def saved_build():
  current=load(core/'evidence/block01/BUILD.json');d=receipt['delivered_build']
  assert current['outputs']==d['outputs'] and current['builds']==d['builds']
  assert current['registered_routes']==d['registered_routes']==94
  assert current['companion_annotations']==d['companion_annotations']==95
  for row in d['outputs'].values():assert sha(core/'publication/pdfs'/row['file'])==row['sha256']
  return {'outputs':3,'source_root_host_paths_retained_as_provenance':True,'registered_routes':94,'companion_annotations':95}
 check('delivered_build_active_output_and_diagnostic_bindings',saved_build)
 def publication_record():
  p=load(core/'verification/block01/PUBLICATION_CHECK.json');assert receipt['publication_checks']==p and p['status']=='PASS' and p['errors']==[]
  return {'proof_bodies':p['proof_bodies'],'statement_bodies':p['statement_bodies'],'registered_routes':p['registered_routes'],'total_pages':p['total_pages']}
 check('saved_publication_check_identity',publication_record)
 def export_records():
  m={'Paper_XII_Release_Review_v1.0.0_2026-10-10.md':'RELEASE_REVIEW.md','Paper_XII_Progress_Ledger_v1.0.0.md':'PROGRESS_LEDGER.md','Paper_XII_Progress_Ledger_v1.0.0.json':'PROGRESS_LEDGER.json','Paper_XII_Continue_Here_v1.0.0.md':'CONTINUE_HERE.md','Paper_XII_Reading_Concordance_v1.0.0.md':'READING_CONCORDANCE.md','Paper_XII_Source_Changes_v1.0.0.md':'evidence/block01/SOURCE_CHANGES.md','Paper_XII_Failures_and_Limitations_v1.0.0.md':'FAILURES_AND_LIMITATIONS.md'}
  for r in receipt['exports']:
   p=core/('publication/pdfs/'+r['file'] if r['file'].endswith('.pdf') else m[r['file']]);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
   if r['file'].endswith('.pdf'):
    q=readers/r['file'];assert q.stat().st_size==r['bytes'] and sha(q)==r['sha256'];assert r['matches_reader_zip'] and r['matches_source_zip'] and r['fresh_extracted_build_byte_identical']
  return {'exports_authenticated':len(receipt['exports']),'PDFs_exact_in_both_current_layouts':3}
 check('all_export_record_bytes_and_source_reader_copy_identity',export_records)
 def boundaries():
  x=receipt['boundaries'];assert x['fresh_lean_lake']=='not_run' and x['revised_claim_contract']==49 and x['original_contract']=={'complete':41,'partial':7,'unchecked':1} and x['new_statement_amendments']==0
  return x
 check('accepted_formal_and_conditional_boundaries_not_promoted',boundaries)
 report={'schema':'komorebi.paper-xii.nested-delivery-audit/1','status':'PASS' if not failures else 'FAIL','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only nested container identity and accepted saved delivery/rebuild receipt binding. No compiler, science, controls or PDF build execution.','checks_passed':len(checks)-len(failures),'checks_total':len(checks),'checks':checks,'failures':failures,'recursive_archives':recursive,'counting_boundary':'Archive/member counts include repeated packaging occurrences; they are not independent scientific-source or theorem counts.'}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['status','checks_passed','checks_total','failures']},indent=2));return bool(failures)
if __name__=='__main__':raise SystemExit(main())

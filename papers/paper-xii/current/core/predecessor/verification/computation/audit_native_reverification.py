#!/usr/bin/env python3
"""Authenticate the separate native re-verification record; no Lean is executed."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
from replay_task import archive_audit,parse_sha_manifest,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 p=a.project.resolve();native=p/'source/native_reverification/PRSC_XII_v0.17.1_Completion_Reverified';core=p/'source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release'
 side=p/'verification/computation/native_archive_expected.sha256'
 arc=archive_audit(p/'downloads/recovery/PRSC_XII_v0.17.1_Completion_Reverified.zip',side,native)
 sm=parse_sha_manifest(native/'SHA256SUMS.txt',native)
 v=json.loads((native/'verification.json').read_text());cv=json.loads((core/'verification.json').read_text());audit=json.loads((native/'REVERIFICATION_AUDIT.json').read_text());contract=json.loads((native/'CONTRACT_REPLAY.json').read_text())
 errors=[];pairs=[];logs=[];parsed_audits=0
 for m in v['modules']:
  rel=Path(m['module'].replace('.','/'));src=rel.with_suffix('.lean');obj=rel.with_suffix('.olean')
  s=sha(native/'lean'/src);o=sha(native/'build'/obj)
  okay=s==v['source_hashes_before'][str(src)]==v['source_hashes_after'][str(src)]==m['source_sha256']==sha(core/'lean'/src) and o==m['olean_sha256']==sha(core/'build'/obj)
  pairs.append({'module':m['module'],'source_sha256':s,'object_sha256':o,'matches_native_record_and_core':okay})
  if not okay:errors.append('source/object mismatch: '+m['module'])
  for item in (m,m['axiom_audit']):
   okay=sha(native/item['log'])==item['log_sha256'];logs.append({'path':item['log'],'matches':okay})
   if not okay:errors.append('log changed: '+item['log'])
  text=(native/m['axiom_audit']['log']).read_text()
  for d in [x for x in v['axioms'] if x['module']==m['module']]:
   name=d['name'];match=re.search(re.escape("'"+name+"'")+r' depends on axioms:\s*\[([^\]]*)\]',text)
   actual=({x.strip() for x in match[1].split(',') if x.strip()} if match else set() if "'"+name+"' does not depend on any axioms" in text else None)
   if actual!=set(d['axioms']) or actual is None:errors.append('axiom record/log mismatch: '+name)
   else:parsed_audits+=1
 for item in v['controls']+[contract]:
  okay=sha(native/item['log'])==item['log_sha256'];logs.append({'path':item['log'],'matches':okay})
  if not okay:errors.append('log changed: '+item['log'])
 contract_text=(native/contract['log']).read_text();contract_parsed=0
 for d in contract['audits']:
  match=re.search(re.escape("'"+d['name']+"'")+r' depends on axioms:\s*\[([^\]]*)\]',contract_text)
  actual={x.strip() for x in match[1].split(',') if x.strip()} if match else None
  if actual!=set(d['axioms']):errors.append('contract axiom mismatch: '+d['name'])
  else:contract_parsed+=1
 checks={'native_cumulative_report_hash':sha(native/'verification.json')==audit['cumulative_replay']['verification_sha256'],
  'native_contract_report_hash':sha(native/'CONTRACT_REPLAY.json')==audit['direct_contract_replay']['report_sha256'],
  'contract_source_hash':sha(native/'checks/ManuscriptContractReplay.lean')==contract['source_sha256_before']==contract['source_sha256_after']==audit['direct_contract_replay']['source_sha256'],
  'production_module_inventory_same_as_core':{x['module'] for x in v['modules']}=={x['module'] for x in cv['modules']},
  'module_manifest_hash':sha(native/'checks/modules.json')==v['module_manifest_sha256'],
  'all_recorded_statuses_pass':v['status']==audit['status']==contract['status']=='PASS',
  'contract_execution_record':contract['exit_code']==0 and not contract['timed_out'],
  'negative_control_execution_records':len(v['controls'])==3 and all(x['passed'] and x['exit_code']!=0 and not x['timed_out'] for x in v['controls']),
  'allowed_recorded_axioms_only':all(set(d['axioms'])<={'propext','Classical.choice','Quot.sound'} for d in v['axioms']+contract['audits']),
  'full_named_axiom_log_parse':parsed_audits==1229,'three_contract_axiom_log_parse':contract_parsed==3}
 errors += [k for k,b in checks.items() if not b]
 report={'scope':'Fresh byte integrity and record/log consistency audit of inherited native replay; no fresh Lean compiler execution.',
  'archive':arc,'native_sha_manifest':sm,'checks':checks,'source_object_pairs':pairs,'source_object_pairs_compared':len(pairs),
  'logs_verified':len(logs),'logs':logs,'production_axiom_targets_parsed':parsed_audits,'native_contract_targets_parsed':contract_parsed,
  'native_cumulative_record_started_utc':v['started_utc'],'native_cumulative_record_finished_utc':v['finished_utc'],
  'native_contract_record_started_utc':contract['started_utc'],'native_contract_record_finished_utc':contract['finished_utc'],
  'native_contract_target_names':[d['name'] for d in contract['audits']],
  'errors':errors,'fresh_lean_replay':False,'status':'PASS' if not errors and arc['status']==sm['status']=='PASS' else 'FAIL',
  'interpretation':'The native archive supplies a second inherited cumulative replay and three separately named direct tests. It does not add production modules, public production theorems, or manuscript claims.'}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','source_object_pairs_compared','logs_verified','production_axiom_targets_parsed','native_contract_targets_parsed','errors')},indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())

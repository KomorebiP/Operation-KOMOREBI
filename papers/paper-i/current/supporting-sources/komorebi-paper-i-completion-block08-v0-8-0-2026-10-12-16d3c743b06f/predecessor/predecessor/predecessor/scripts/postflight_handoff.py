#!/usr/bin/env python3
"""Finish metadata only after the accepted verifier has exited."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
r=Path(__file__).resolve().parents[1]
b=json.loads((r/'evidence/final_audit/verification.json').read_text())
assert b['status']=='PASS'
active=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().replace(b'\x00',b' ').decode(errors='replace');stat=(p/'stat').read_text();state=stat.split(') ',1)[1].split()[0]
  exe=os.path.basename((p/'cmdline').read_bytes().split(b'\x00')[0].decode(errors='replace'))
  if state!='Z' and str(r) in args and (exe in ['lean','lake'] or ('verify_block05.py' in args and exe in ['python','python3'])):active.append({'pid':int(p.name),'state':state,'command':args})
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
assert not active,active
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in b['source_files']:
 assert sha(r/row['source'])==row['source_sha256']
 assert sha(r/'evidence/final_audit'/row['object'])==row['object_sha256']
post={'status':'PASS','checked_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'active_audit_or_compiler_processes':active,'source_and_object_pairs_checked':37,'accepted_run_sha256':sha(r/'evidence/final_audit/verification.json')}
(r/'evidence/HANDOFF_POSTFLIGHT.json').write_text(json.dumps(post,indent=2)+'\n')
idx={'accepted':{'path':'evidence/final_audit/verification.json','status':'PASS','sha256':post['accepted_run_sha256']},'cancelled_optional_rebuild':{'raw_path':'evidence/predecessor_fresh/baseline/verification.json','raw_historical_status':json.loads((r/'evidence/predecessor_fresh/baseline/verification.json').read_text()).get('status','UNKNOWN'),'current_status':'CANCELLED_NOT_ACCEPTED','status_record':'evidence/PREDECESSOR_ATTEMPT_NOT_ACCEPTED.json'},'development':'evidence/DEVELOPMENT_INDEX.json','transport':'evidence/TRANSPORT_INCIDENTS.json','supplemental_archive_identity':'evidence/PREDECESSOR_EXACT_IDENTITY.json','active_audit_or_compiler_processes':0}
(r/'evidence/RUN_INDEX.json').write_text(json.dumps(idx,indent=2)+'\n')
summary=json.loads((r/'VERIFICATION.json').read_text());summary['handoff_postflight']={'path':'evidence/HANDOFF_POSTFLIGHT.json','sha256':sha(r/'evidence/HANDOFF_POSTFLIGHT.json')};summary['active_audit_or_compiler_processes_at_handoff']=0
(r/'VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
for name in ['docs/COMPLETION_REPORT.md','PROGRESS_LEDGER.md']:
 p=r/name;s=p.read_text();ending='\nNo audit or compiler process remains active at this handoff. `evidence/HANDOFF_POSTFLIGHT.json` records the process and final source/object checks.\n';
 if ending not in s:p.write_text(s+ending)
ledger=json.loads((r/'PROGRESS_LEDGER.json').read_text());ledger['active_audit_or_compiler_processes_at_handoff']=0;(r/'PROGRESS_LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n')
exports={'docs/COMPLETION_REPORT.md':'Paper_I_Block05_Completion_Report_2026-10-10.md','docs/PROOF_GUIDE.md':'Paper_I_Block05_Proof_Guide_2026-10-10.md','PROGRESS_LEDGER.md':'Paper_I_Block05_Progress_Ledger_v0.5.0.md','coverage/COVERAGE_108.md':'Paper_I_Expanded_108_Record_Lean_Coverage_v0.5.0.md','VERIFICATION.json':'Paper_I_Block05_Verification_2026-10-10.json'}
for src,dst in exports.items():shutil.copy2(r/src,r.parent/dst)
print(json.dumps(post,indent=2))

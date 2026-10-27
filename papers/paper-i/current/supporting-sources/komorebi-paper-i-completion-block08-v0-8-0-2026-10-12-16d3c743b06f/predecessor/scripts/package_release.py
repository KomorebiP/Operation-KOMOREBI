#!/usr/bin/env python3
"""Final postflight, manifest, archive integrity and exact archived-payload validation."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,zipfile
import psutil
R=Path(__file__).resolve().parents[1];O=R.parent
K=Path('/mnt/data/runtime_restore/Komorebi_Portable_Lean_4.34.0-rc2')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
a=json.loads((R/'evidence/final_audit/verification.json').read_text());assert a['status']=='PASS'
for row in a['source_files']:
 assert sha(R/row['source'])==row['source_sha256']
 assert sha(R/'evidence/final_audit'/row['object'])==row['object_sha256']
for row in a['frozen_inputs']:assert sha(R/row['path'])==row['sha256']
for row in a['checks']:
 assert row['passed'] and sha(R/'evidence/final_audit'/row['log'])==row['log_sha256']
assert sha(R/'evidence/final_audit/test_objects/BoundaryConsumers.olean')==a['boundary_object_sha256']
active=[]
for p in psutil.process_iter(['pid','name','cmdline','status']):
 try:
  c=p.info['cmdline'] or []
  if p.info['status']!='zombie' and (p.info['name'] in ['lean','lake','leanchecker'] or
      any(s.endswith('/verify_block07.py') for s in c[1:3])):
   active.append(p.info)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not active,active
startup=[]
for label,args in [('usage_guard',[]),('existing_output_guard',[str(K),str(R/'evidence/final_audit')])]:
 cmd=['bash',str(R/'scripts/run_block07.sh'),*args]
 p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 assert p.returncode==2,(label,p.returncode,p.stdout)
 log=R/'evidence'/(label+'.log');log.write_text(p.stdout)
 startup.append({'label':label,'command':cmd,'expected_exit':2,'actual_exit':p.returncode,
  'log':str(log.relative_to(R)),'log_sha256':sha(log)})
assert sha(R/'evidence/final_audit/verification.json')==json.loads((R/'VERIFICATION.json').read_text())['accepted_run']['sha256']
post={'status':'PASS','checked_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'production_source_object_pairs_verified':len(a['source_files']),
 'accepted_command_logs_verified':len(a['checks']),'frozen_execution_inputs_verified':len(a['frozen_inputs']),
 'boundary_object_verified':True,'active_audit_or_compiler_processes':active,
 'startup_guards':startup,'startup_guard_checks_not_added_to_accepted_run_count':True,
 'logical_production_names_replayed':a['owned_logical_total'],
 'logical_boundary_names_replayed':a['boundary_owned_total'],
 'logical_replay_name_set_equals_ownership_set':a['replay_owned_exact_name_set_match']}
wr(R/'evidence/HANDOFF_POSTFLIGHT.json',post)
v=json.loads((R/'VERIFICATION.json').read_text())
v['handoff_postflight']={'path':'evidence/HANDOFF_POSTFLIGHT.json','sha256':sha(R/'evidence/HANDOFF_POSTFLIGHT.json')}
v['active_audit_or_compiler_processes_at_handoff']=0
wr(R/'VERIFICATION.json',v)
# Runtime-recovery receipts are small provenance files. Never bundle the large runtime.
for name in ['archive_receipt.json','restore.log']:
 p=Path('/mnt/data/runtime_restore')/name
 if p.exists():shutil.copy2(p,R/'evidence'/('runtime_recovery_'+name))
# These disposable directories are not accepted build inputs; retain all development snapshots/logs.
for sub in ['evidence/dev_objects','evidence/dev_imports','scripts/__pycache__']:
 p=R/sub
 if p.exists():shutil.rmtree(p)
font_exts={'.ttf','.otf','.woff','.woff2'}
assert not [p for p in R.rglob('*') if p.is_file() and p.suffix.lower() in font_exts]
files=sorted(p for p in R.rglob('*') if p.is_file() and p!=R/'MANIFEST_SHA256.json')
v['package_manifest_payload_count']=len(files)
wr(R/'VERIFICATION.json',v)
manifest={'schema':'sha256-manifest/1','count':len(files),'excludes':'MANIFEST_SHA256.json',
 'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
wr(R/'MANIFEST_SHA256.json',manifest)
archive=O/(R.name+'.zip')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in [*files,R/'MANIFEST_SHA256.json']:z.write(p,str(Path(R.name)/p.relative_to(R)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert len([i for i in z.infolist() if not i.is_dir()])==manifest['count']+1
 assert json.loads(z.read(R.name+'/MANIFEST_SHA256.json'))==manifest
 for row in manifest['files']:
  b=z.read(R.name+'/'+row['path'])
  assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
validation={'status':'PASS','archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),
 'crc_integrity_checked':True,'manifested_payloads_verified':manifest['count'],
 'archive_file_entries_including_manifest':manifest['count']+1,
 'verification':'Each archived payload compared with the manifest by byte length and SHA256.'}
wr(O/'Paper_I_Block07_Archive_Validation_2026-10-11.json',validation)
exports={
 'PROOF_GUIDE.md':'Paper_I_Block07_Proof_Guide_2026-10-11.md',
 'COMPLETION_REPORT.md':'Paper_I_Block07_Completion_Report_2026-10-11.md',
 'PROGRESS_LEDGER.md':'Paper_I_Block07_Progress_Ledger_v0.7.0.md',
 'VERIFICATION.json':'Paper_I_Block07_Verification_2026-10-11.json',
 'coverage/COVERAGE_108.md':'Paper_I_Expanded_108_Record_Lean_Coverage_v0.7.0.md'}
for src,dest in exports.items():shutil.copy2(R/src,O/dest);assert sha(R/src)==sha(O/dest)
print(json.dumps(validation,indent=2))
print('RELEASE_READY')

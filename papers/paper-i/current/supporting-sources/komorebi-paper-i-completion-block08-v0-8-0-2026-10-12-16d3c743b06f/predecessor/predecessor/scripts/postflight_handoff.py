#!/usr/bin/env python3
"""Confirm completed execution, immutable evidence, startup guards, and no live audit."""
from pathlib import Path
import hashlib,json,os,subprocess,time
r=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=r/'evidence/final_audit';b=json.loads((a/'verification.json').read_text())
assert b['status']=='PASS' and len(b['same_kernel_modules_replayed'])==42
assert all(x['passed'] for x in b['checks'])
v=json.loads((r/'VERIFICATION.json').read_text());assert v['status']=='PASS'
assert sha(r/v['accepted_run']['path'])==v['accepted_run']['sha256']
for row in b['source_files']:
 assert sha(r/row['source'])==row['source_sha256']
 assert sha(a/row['object'])==row['object_sha256']
for row in b['frozen_inputs']:assert sha(r/row['path'])==row['sha256']
for c in b['checks']:assert sha(a/c['log'])==c['log_sha256']
for row in json.loads((r/'predecessor/MANIFEST_SHA256.json').read_text())['files']:
 p=r/'predecessor'/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
# These checks are separate from the accepted command denominator.
checks=[]
for label,cmd,want,pattern in [
 ('launcher_syntax',['bash','-n',str(r/'scripts/run_block06.sh')],0,None),
 ('launcher_usage_guard',['bash',str(r/'scripts/run_block06.sh')],2,'Usage:'),
 ('launcher_existing_output_guard',['bash',str(r/'scripts/run_block06.sh'),
  '/mnt/data/Komorebi_Portable_Lean_4.34.0-rc2',str(a)],2,'Refusing existing output:')]:
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=15)
 assert p.returncode==want and (pattern is None or pattern in p.stdout)
 log=r/'evidence'/(label+'.log');log.write_text(p.stdout)
 checks.append({'label':label,'command':cmd,'actual_exit':p.returncode,
   'expected_exit':want,'passed':True,'log':str(log.relative_to(r)),'log_sha256':sha(log)})
for name in ['verify_block06.py','assemble_handoff.py','update_coverage.py','postflight_handoff.py','package_release.py']:
 p=r/'scripts'/name;compile(p.read_text(),str(p),'exec')
 checks.append({'label':'python_syntax_'+name,'passed':True,'source_sha256':sha(p)})
def active():
 hits=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   stat=(p/'stat').read_text();state=stat[stat.rfind(')')+2:].split()[0]
   if state=='Z':continue
   args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
   direct=any(Path(x).name in {'lean','leanchecker'} for x in args[:3] if x)
   own=any(x==str(r/'scripts'/s) for x in args for s in ['verify_block06.py','dev_check.py','run_block06.sh'])
   if direct or own:hits.append({'pid':int(p.name),'state':state,'args':args})
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 return hits
for _ in range(100):
 hits=active()
 if not hits:break
 time.sleep(.1)
assert not hits,hits
post={'status':'PASS','checked_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'source_object_pairs_verified':42,'command_logs_verified':len(b['checks']),
 'execution_inputs_unchanged':len(b['frozen_inputs']),
 'active_audit_or_compiler_processes':hits,'separate_tooling_checks':checks,
 'note':'The tooling checks above are not added to the main audit command denominator.'}
f=r/'evidence/HANDOFF_POSTFLIGHT.json';f.write_text(json.dumps(post,indent=2)+'\n')
v['handoff_postflight']={'path':str(f.relative_to(r)),'sha256':sha(f)}
v['active_audit_or_compiler_processes_at_handoff']=0
(r/'VERIFICATION.json').write_text(json.dumps(v,indent=2)+'\n')
l=json.loads((r/'PROGRESS_LEDGER.json').read_text());l['active_audit_or_compiler_processes_at_handoff']=0
(r/'PROGRESS_LEDGER.json').write_text(json.dumps(l,indent=2)+'\n')
note='No audit or compiler process remains active at this handoff. `evidence/HANDOFF_POSTFLIGHT.json` records the final source/object, log, startup-guard, and process checks.'
for p in [r/'docs/COMPLETION_REPORT.md',r/'PROGRESS_LEDGER.md']:
 s=p.read_text()
 if note not in s:p.write_text(s.rstrip()+'\n\n'+note+'\n')
print(json.dumps(post,indent=2))

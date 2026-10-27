#!/usr/bin/env python3
"""Additional Paper I audit; run within the pinned kit's Lake environment.
Read a successful fresh-main receipt, inspect module-owned declarations,
and replay each compiled module serially with the pinned official replay API.
Every attempt writes separate receipts and logs; never reuse an existing out.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,signal,subprocess,time
from pathlib import Path

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--main-run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 root=a.root.resolve();mr=a.main_run.resolve();out=a.out.resolve()
 if out.exists():raise SystemExit('Refusing existing output directory')
 out.mkdir(parents=True)
 baseline=json.loads((mr/'fresh_verification.json').read_text())
 if baseline['status']!='PASS':raise SystemExit('Fresh main receipt is not PASS')
 env=os.environ.copy();env['LEAN_PATH']=str(mr/'objects')+os.pathsep+env.get('LEAN_PATH','')
 flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false']
 report={'status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'main_receipt_sha256':sha(mr/'fresh_verification.json'),'checks':[], 'limits':['Official same-kernel replay is not an independently implemented verifier.','Pinned upstream compiled imports are reused; no fresh Mathlib proof replay is claimed.']}
 def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
 def run(label,cmd,marker,extra=None):
  e=env.copy();e.update(extra or {});log=out/(label+'.log');t=time.monotonic()
  with log.open('w') as f:
   p=subprocess.Popen(cmd,cwd=root,env=e,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:code=p.wait(timeout=600)
   except subprocess.TimeoutExpired:
    os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
  text=log.read_text(errors='replace');passed=code==0 and marker in text
  rec={'label':label,'command':cmd,'environment_additions':extra or {},'returncode':code,'seconds':round(time.monotonic()-t,3),'passed':passed,'required_marker':marker,'log':log.name,'log_sha256':sha(log)}
  report['checks'].append(rec);save();print(('PASS' if passed else 'FAIL')+' '+label,flush=True)
  if not passed:raise RuntimeError(label+' failed; log '+str(log))
  return text
 save()
 try:
  for m in baseline['modules']:
   p=root/'source/main'/Path(*m['module'].split('.')).with_suffix('.lean');obj=mr/'objects'/Path(*m['module'].split('.')).with_suffix('.olean')
   if sha(p)!=m['source_sha256'] or sha(obj)!=m['object_sha256']:raise RuntimeError('Source/object receipt mismatch: '+m['module'])
  text=run('owned_declaration_audit',['lean',*flags,str(root/'tests/OwnedDeclarationAudit.lean')],'OWNED_AUDIT_PASS ')
  rows=[json.loads(x[6:]) for x in text.splitlines() if x.startswith('OWNED ')]
  m=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
  if not m or len(rows)!=int(m.group(1)) or len({r['name'] for r in rows})!=len(rows):raise RuntimeError('Owned inventory count/uniqueness failed')
  (out/'owned_declarations.json').write_text(json.dumps(rows,indent=2)+'\n')
  report['owned_declarations']=len(rows);report['outside_project_namespaces']=int(m.group(2));save()
  for entry in baseline['modules']:
   mod=entry['module'];run('replay_'+mod.replace('.','_'),['lean',*flags,str(root/'tests/ReplayExact.lean')],'REPLAY_EXACT_PASS '+mod,{'KOMOREBI_REPLAY_MODULE':mod})
  report['replayed_modules']=len(baseline['modules']);report['status']='PASS';report['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
  return 0
 except Exception as ex:
  report['status']='FAIL';report['failure']=str(ex);save();print(str(ex),flush=True);return 1
if __name__=='__main__':raise SystemExit(main())

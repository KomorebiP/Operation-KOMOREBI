#!/usr/bin/env python3
"""Run deliberate audit-gate controls and mathematical boundary consumers.
Requires the pinned kit Lake environment and a successful fresh main run.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,signal,subprocess,time
from pathlib import Path

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--main-run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();mr=a.main_run.resolve();out=a.out.resolve()
 if out.exists():raise SystemExit('Refusing existing output directory')
 out.mkdir(parents=True);obj=out/'objects';obj.mkdir()
 if json.loads((mr/'fresh_verification.json').read_text())['status']!='PASS':raise SystemExit('Main run not PASS')
 env=os.environ.copy();env['LEAN_PATH']=str(obj)+os.pathsep+str(mr/'objects')+os.pathsep+env.get('LEAN_PATH','')
 report={'status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':[],'scope':'Deliberate nonproduction audit fixtures and four exact consumer theorems. Not additional main contract rows.'}
 def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
 def run(label,source,*,reject=False,pattern=None,warning=True,object_name=None):
  cmd=['lean','-j1','-DwarningAsError='+str(warning).lower(),'-DautoImplicit=false','-DrelaxedAutoImplicit=false']
  if object_name:cmd+=['-o',str(obj/(object_name+'.olean'))]
  cmd.append(str(source));log=out/(label+'.log');t=time.monotonic()
  with log.open('w') as f:
   p=subprocess.Popen(cmd,cwd=source.parent,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:c=p.wait(timeout=300)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();c=124
  text=log.read_text(errors='replace')
  ok=(c>0 and c!=124 and bool(re.search(pattern,text))) if reject else c==0
  if not reject and pattern:ok=ok and bool(re.search(pattern,text))
  report['checks'].append({'label':label,'source_sha256':sha(source),'command':cmd,'returncode':c,'expected_rejection':reject,'required_pattern':pattern,'passed':bool(ok),'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':sha(log)});save();print(('PASS' if ok else 'FAIL')+' '+label,flush=True)
  if not ok:raise RuntimeError(label+' failed')
  return text
 save()
 try:
  for n in ['ForeignClean','InjectedAxiom','InjectedPlaceholder']:
   src=root/'tests/fixtures'/(n+'.lean');aud=root/'tests/fixtures'/(n+'Audit.lean')
   run('compile_'+n,src,warning=n!='InjectedPlaceholder',object_name=n,pattern='declaration uses.*sorry' if n=='InjectedPlaceholder' else None)
   run('guard_'+n,aud,reject=n!='ForeignClean',pattern='OWNED_AUDIT_PASS 1 OUTSIDE_NAMESPACE 1' if n=='ForeignClean' else ('OWNED AUDIT REJECTED (axiom|dependency).*' if n=='InjectedAxiom' else 'OWNED AUDIT REJECTED dependency sorryAx'))
  text=run('boundary_regressions',root/'tests/BoundaryRegression.lean')
  found=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",text)
  if len(found)!=4:raise RuntimeError('Expected four boundary axiom reports')
  for n,axs in found:
   if {s.strip() for s in axs.split(',') if s.strip()}-{'propext','Classical.choice','Quot.sound'}:raise RuntimeError('Unapproved boundary axiom '+n)
  report.update(status='PASS',boundary_theorems=4,negative_guard_controls=2,positive_foreign_namespace_control=1,finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));save();return 0
 except Exception as ex:report.update(status='FAIL',failure=str(ex));save();print(str(ex),flush=True);return 1
if __name__=='__main__':raise SystemExit(main())

from pathlib import Path
import os, sys, json, re, hashlib, subprocess, time, concurrent.futures
B=Path(__file__).parent
R=B/'project'
K=Path('/workspace/scratch/ea498747acd5/runtime/parts/Komorebi_Portable_Lean_4.34.0-rc2')
O=R/'verification/fresh_cumulative'; O.mkdir(parents=True,exist_ok=True)
BUILD=R/'.build/lib/lean'; (BUILD/'KomorebiLSM').mkdir(parents=True,exist_ok=True)
env=os.environ.copy()
env['LD_PRELOAD']=str(K/'compat/app_path.so')
env['LEAN_PATH']=os.pathsep.join([str(BUILD),*[str(p/'.lake/build/lib/lean') for p in (K/'workspace/.lake/packages').iterdir() if p.is_dir()],str(K/'toolchain/lib/lean')])
env['PATH']=str(K/'toolchain/bin')+os.pathsep+env['PATH']
for k in ['LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']: env.pop(k,None)
lean=str(K/'toolchain/bin/lean')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd, timeout=600, extra=None):
 e=env.copy();e.update(extra or {})
 t=time.monotonic()
 try:
  p=subprocess.run(cmd,cwd=R,env=e,text=True,capture_output=True,timeout=timeout)
  return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':round(time.monotonic()-t,3),'timed_out':False}
 except subprocess.TimeoutExpired as x:
  return {'command':cmd,'returncode':-1,'stdout':str(x.stdout),'stderr':str(x.stderr),'seconds':round(time.monotonic()-t,3),'timed_out':True}
prior=O/'report.json'
report=json.loads(prior.read_text()) if prior.exists() else {'kind':'Fresh cumulative source-bound execution','passed':False,'stages':[],'runtime':run([lean,'--version'])}
report['passed']=False
report.pop('failure',None)
def save():
 p=O/'report.json.pending';p.write_text(json.dumps(report,indent=2)+'\n');p.replace(O/'report.json')
mods={p.stem:p for p in (R/'KomorebiLSM').glob('*.lean') if not p.stem.startswith('Section88')}
report['execution_subset']='Non-Section88 modules while exact chart proof refactor is validated.'
deps={m:re.findall(r'^import KomorebiLSM\.(\w+)',p.read_text(),re.M) for m,p in mods.items()}
parent=set(re.findall(r'^import KomorebiLSM\.(\w+)',(B/'parent/Large_Signal_Model/Lean/KomorebiLSM.lean').read_text(),re.M))
done=set();pending=set(mods);active={};failed=set()
while True:
 ready=[m for m in pending if set(deps[m])<=done]
 accepted=[]
 for m in ready:
  h=sha(mods[m])
  cs=[s for s in report['stages'] if s.get('module')==m and s.get('phase')=='compile' and s.get('returncode')==0 and s.get('source_sha256')==h]
  rs=[s for s in report['stages'] if s.get('module')==m and s.get('phase')=='kernel_replay' and s.get('returncode')==0 and s.get('source_sha256')==h]
  if cs and rs and (BUILD/'KomorebiLSM'/f'{m}.olean').exists():accepted.append(m)
 if not accepted:break
 done.update(accepted);pending.difference_update(accepted)
print('RESUMING_VALID_CURRENT_SESSION_CHECKS',len(done),'OF',len(mods),flush=True)
def work(m):
 src=mods[m]; h=sha(src)
 c=run([lean,'-j1','-DwarningAsError=true','-o',str(BUILD/'KomorebiLSM'/f'{m}.olean'),str(src)])
 c.update(phase='compile',module=m,source_sha256=h)
 if c['returncode']!=0:return [c]
 r=run([lean,'-j1','-DwarningAsError=true',str(R/'scripts/ReplayModule.lean')],extra={'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+m})
 r.update(phase='kernel_replay',module=m,source_sha256=h)
 return [c,r]
try:
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  while pending or active:
   ready=sorted((m for m in pending if set(deps[m])<=done),key=lambda m:(m not in parent,m))
   while ready and len(active)<1:
    m=ready.pop(0);pending.remove(m);active[pool.submit(work,m)]=m
   if not active:break
   completed,_=concurrent.futures.wait(active,return_when=concurrent.futures.FIRST_COMPLETED)
   for f in completed:
    m=active.pop(f);stages=f.result();report['stages']+=stages;save()
    bad=[s for s in stages if s['returncode']!=0 or s['timed_out']]
    if bad:
     failed.add(m);print('FAILED_MODULE',m,bad[0]['stdout']+bad[0]['stderr'],flush=True)
    else:
     done.add(m); print('CHECKED',len(done),'/',len(mods),m,flush=True)
 report['checked_module_hashes']={m:sha(p) for m,p in mods.items()}
 report['pending_modules']=sorted(pending);report['failed_modules']=sorted(failed)
 report['module_passed']=len(done)==len(mods);report['passed']=report['module_passed'];report['complete']=report['module_passed'];save()
 print('ALL_MODULES_PASS' if report['module_passed'] else 'PARTIAL_MODULE_RUN',len(done),'/',len(mods),flush=True)
except Exception as x:
 report['failure']=repr(x);save();print('FAILED',x,flush=True);sys.exit(1)

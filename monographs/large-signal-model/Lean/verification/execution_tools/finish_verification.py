from pathlib import Path
import importlib.util, json, hashlib, os, subprocess, sys, time
B=Path(__file__).parent; R=B/'project'
K=Path('/workspace/scratch/ea498747acd5/runtime/parts/Komorebi_Portable_Lean_4.34.0-rc2')
spec=importlib.util.spec_from_file_location('lsmverify',R/'scripts/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
O=R/'verification/current';O.mkdir(parents=True,exist_ok=True)
build=R/'.build/lib/lean'
env=os.environ.copy();env['LD_PRELOAD']=str(K/'compat/app_path.so')
env['LEAN_PATH']=os.pathsep.join([str(build),*[str(p/'.lake/build/lib/lean') for p in (K/'workspace/.lake/packages').iterdir() if p.is_dir()],str(K/'toolchain/lib/lean')])
env['PATH']=str(K/'toolchain/bin')+os.pathsep+env['PATH']
for k in ['LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(k,None)
lean=str(K/'toolchain/bin/lean')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=json.loads((R/'verification/fresh_cumulative/report.json').read_text())
report={'release':json.loads((R/'RELEASE_COUNTS.json').read_text())['release'],'passed':False,'complete':False,
 'method':'Fresh dependency-ordered warnings-as-errors source compilation and individual kernel replay in this session; new or changed source closures are compiled again before acceptance.',
 'source_snapshot':v.inventory(),'runtime_recovery':json.loads((B/'runtime/RUNTIME_RECOVERY.json').read_text()),'stages':[]}
def save():
 p=O/'report.json.pending';p.write_text(json.dumps(report,indent=2)+'\n');p.replace(O/'report.json')
def run(cmd,extra=None,timeout=600):
 e=env.copy();e.update(extra or {});t=time.monotonic()
 p=subprocess.run(cmd,cwd=R,env=e,text=True,capture_output=True,timeout=timeout)
 return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':round(time.monotonic()-t,6),'timed_out':False}
def add(rec):
 report['stages'].append(rec);save()
 if rec['returncode']!=0:raise RuntimeError(rec['phase']+' failed: '+rec['stdout']+rec['stderr'])
try:
 done=set(); rebuilt=set()
 for m in v.MODULES:
  src=R/'KomorebiLSM'/f'{m}.lean';h=sha(src)
  deps=__import__('re').findall(r'^import KomorebiLSM\.(\w+)',src.read_text(),__import__('re').M)
  if not set(deps)<=done:raise RuntimeError('Non-topological module list '+m)
  cs=[s for s in raw['stages'] if s.get('module')==m and s.get('phase')=='compile' and s.get('returncode')==0 and s.get('source_sha256')==h]
  rs=[s for s in raw['stages'] if s.get('module')==m and s.get('phase')=='kernel_replay' and s.get('returncode')==0 and s.get('source_sha256')==h and 'KERNEL_REPLAY_PASS KomorebiLSM.'+m in s.get('stdout','')]
  if cs and rs and not (set(deps)&rebuilt) and (build/'KomorebiLSM'/f'{m}.olean').exists():
   report['stages'] += [cs[-1],rs[-1]]
  else:
   c=run([lean,'-j1','-DwarningAsError=true','-o',str(build/'KomorebiLSM'/f'{m}.olean'),str(src)])
   c.update(phase='compile',module=m,source_sha256=h);add(c)
   rr=run([lean,'-j1','-DwarningAsError=true',str(R/'scripts/ReplayModule.lean')],{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+m})
   rr.update(phase='kernel_replay',module=m,source_sha256=h);add(rr)
   if 'KERNEL_REPLAY_PASS KomorebiLSM.'+m not in rr['stdout']:raise RuntimeError('Missing kernel marker '+m)
   rebuilt.add(m);print('FRESH_FINAL',m,flush=True)
  done.add(m)
 report['recompiled_final_closure']=sorted(rebuilt);save()
 c=run([lean,'-j1','-DwarningAsError=true','-o',str(build/'KomorebiLSM.olean'),str(R/'KomorebiLSM.lean')]);c.update(phase='compile',module='__root__',source_sha256=sha(R/'KomorebiLSM.lean'));add(c)
 c=run([lean,'-j1','-DwarningAsError=true',str(R/'scripts/RunRationalSearch.lean')]);c.update(phase='executable_examples');add(c)
 if c['stdout'].strip()!='true\ntrue\nfalse\ntrue\nfalse':raise RuntimeError('Wrong exact-example output')
 c=run([lean,'-j1','-DwarningAsError=true',str(R/'AxiomAudit.lean')]);c.update(phase='axiom_audit',source_sha256=sha(R/'AxiomAudit.lean'));add(c)
 decl=json.loads((R/'DECLARATIONS.json').read_text());report['axioms']=v.parse_axioms(c['stdout'],{d['name'] for d in decl})
 hits=[]
 for p in [R/'KomorebiLSM.lean',R/'AxiomAudit.lean',*(R/'KomorebiLSM').glob('*.lean')]:
  for hit in v.prohibited_source_hits(p.read_text()):hits.append({'file':str(p.relative_to(R)),**hit})
 report['prohibited_source_hits']=hits
 if hits:raise RuntimeError('Forbidden source tokens')
 
 if v.inventory()!=report['source_snapshot']:raise RuntimeError('Source snapshot changed during final proof/axiom checks')
 report['proofs_and_axioms_passed']=True;report['counts']=json.loads((R/'RELEASE_COUNTS.json').read_text());save()
 print('PROOFS_AXIOMS_ROOT_EXAMPLES_PASS',flush=True)
except Exception as x:
 report['failure']=repr(x);save();print('FAILED',x,flush=True);sys.exit(1)

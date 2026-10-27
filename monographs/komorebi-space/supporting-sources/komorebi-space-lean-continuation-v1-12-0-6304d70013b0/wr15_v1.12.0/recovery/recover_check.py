#!/usr/bin/env python3
"""Record only actual runtime recovery checks; no project evidence is rewritten."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, time

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
runtime = root / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
manifest = json.loads((runtime / 'workspace/lake-manifest.json').read_text())
packages = runtime / 'workspace/.lake/packages'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def call(argv, env=None):
    p = subprocess.run([str(x) for x in argv], capture_output=True, text=True, env=env)
    return {'argv':[str(x) for x in argv], 'exit_code':p.returncode, 'stdout':p.stdout, 'stderr':p.stderr}
pins=[]
for p in manifest['packages']:
    directory=packages / p['name']
    head=call(['git','-C',directory,'rev-parse','HEAD'])
    clean=call(['git','-C',directory,'status','--porcelain','--untracked-files=all'])
    pins.append({'name':p['name'],'expected':p['rev'],'actual':head['stdout'].strip(),
      'head_exit':head['exit_code'],'status_exit':clean['exit_code'],'status':clean['stdout'],
      'passed':head['exit_code']==0 and head['stdout'].strip()==p['rev'] and clean['exit_code']==0 and not clean['stdout']})
env=os.environ.copy()
for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME','LD_PRELOAD','LD_LIBRARY_PATH']:
    env.pop(key,None)
direct=call([runtime/'toolchain/bin/lean','--version'],env)
env['LD_PRELOAD']=str(runtime/'compat/app_path.so')
caches=sorted(p for p in packages.glob('*/.lake/build/lib/lean') if p.is_dir())
env['LEAN_PATH']=':'.join(str(p) for p in caches)
lean=call([runtime/'toolchain/bin/lean','--version'],env)
lake=call([runtime/'toolchain/bin/lake','--version'],env)
start=time.monotonic()
smoke=call([runtime/'toolchain/bin/lean','-DwarningAsError=true',out/'RecoverySmoke.lean'],env)
smoke['elapsed_seconds']=time.monotonic()-start
(out/'runtime_smoke.log').write_text(smoke['stdout']+smoke['stderr'])
report={
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Runtime recovery and targeted smoke only; not project compilation or declaration audit.',
 'runtime_root':str(runtime),
 'archive_sha256':'66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34',
 'archive_integrity_log':'runtime_assembly.log',
 'library_provenance':'runtime_library_sources.json',
 'pruned_skeleton_backup':str(runtime.with_name(runtime.name+'.pruned_skeleton')),
 'lean':lean,'lake':lake,'direct_without_adapter':direct,
 'adapter':{'path':str(runtime/'compat/app_path.so'),'sha256':sha(runtime/'compat/app_path.so'),
    'origin':'Unmodified adapter already present in verified original offline archive'},
 'compiler':{'path':str(runtime/'toolchain/bin/lean'),'sha256':sha(runtime/'toolchain/bin/lean')},
 'pins':pins,
 'environment':{k:env[k] for k in ['LD_PRELOAD','LEAN_PATH']},
 'cache_directories':[str(p.relative_to(runtime)) for p in caches],
 'cache_file_count':sum(1 for p in caches for f in p.rglob('*') if f.is_file()),
 'smoke':smoke,'smoke_source_sha256':sha(out/'RecoverySmoke.lean'),
 'smoke_log_sha256':sha(out/'runtime_smoke.log'),
 'status':'PASS' if all(p['passed'] for p in pins) and lean['exit_code']==0 and lake['exit_code']==0 and smoke['exit_code']==0 else 'FAIL'
}
(out/'runtime_recovery.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'pins':len(pins),'cache_file_count':report['cache_file_count'],'smoke_exit':smoke['exit_code']}))

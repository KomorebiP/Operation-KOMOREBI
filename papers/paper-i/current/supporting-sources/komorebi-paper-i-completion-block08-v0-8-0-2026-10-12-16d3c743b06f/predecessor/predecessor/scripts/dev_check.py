#!/usr/bin/env python3
"""Compile a development snapshot against hash-checked predecessor objects.
Not a replacement for the fresh final acceptance run.
"""
from pathlib import Path
import os,sys,subprocess,time,json,hashlib,signal
r=Path(__file__).resolve().parents[1]; env=os.environ.copy()
for line in Path('/mnt/data/lean_env.txt').read_text().splitlines():
 if '=' in line:
  key,val=line.split('=',1)
  if key in ['PATH','LEAN_PATH','LEAN_SYSROOT','LD_LIBRARY_PATH','LD_PRELOAD']:env[key]=val
if env.get('LD_PRELOAD'):env['LD_PRELOAD']='/mnt/data/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so'
objs=[r/'evidence/dev_objects',r/'evidence/inherited_objects',r/'predecessor/evidence/final_audit/test_objects']
env['LEAN_PATH']=':'.join(map(str,objs))+':'+env['LEAN_PATH']
src=Path(sys.argv[1]).resolve();build='--build' in sys.argv;testbuild='--test-build' in sys.argv
attempt=r/'evidence/development'/(time.strftime('%Y%m%dT%H%M%S')+'_'+str(time.time_ns()%1000000));attempt.mkdir(parents=True)
(attempt/src.name).write_bytes(src.read_bytes())
args=['lean','-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
cwd=r/'source/extension'
if build:
 rel=src.relative_to(cwd);out=objs[0]/rel.with_suffix('.olean');out.parent.mkdir(parents=True,exist_ok=True);args+=['-o',str(out)]
if testbuild:
 cwd=r/'tests';out=objs[0]/src.with_suffix('.olean').name;args+=['-o',str(out)]
args+=[str(src)];t=time.monotonic()
with (attempt/'compiler.log').open('w') as f:
 p=subprocess.Popen(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=p.wait(timeout=300)
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
rec={'command':args,'exit_code':code,'seconds':time.monotonic()-t,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'build':build}
(attempt/'receipt.json').write_text(json.dumps(rec,indent=2));print((attempt/'compiler.log').read_text());print('RECEIPT',attempt,code,round(rec['seconds'],2));sys.exit(code)

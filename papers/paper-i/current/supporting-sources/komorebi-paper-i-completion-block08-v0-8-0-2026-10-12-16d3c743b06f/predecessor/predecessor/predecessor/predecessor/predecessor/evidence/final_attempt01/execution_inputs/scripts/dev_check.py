#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,time,json,sys,hashlib
root=Path(__file__).resolve().parents[1]
env=os.environ.copy()
for line in Path('/mnt/data/lean_env.txt').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1)
  if k in ['PATH','LEAN_PATH','LEAN_SRC_PATH','LD_LIBRARY_PATH','LD_PRELOAD','LEAN_SYSROOT']:env[k]=v
# run.sh's temporary LD_PRELOAD path may have been removed after capture.
kit=Path('/mnt/data/runtime/Komorebi_Portable_Lean_4.34.0-rc2')
if env.get('LD_PRELOAD'):env['LD_PRELOAD']=str(kit/'compat/app_path.so')
base=root/'predecessor'
obj=root/'evidence/dev_objects';obj.mkdir(exist_ok=True)
env['LEAN_PATH']=':'.join(map(str,[obj,base/'evidence/extension_attempt01/objects',base/'evidence/baseline_replay/main/objects']))+':'+env.get('LEAN_PATH','')
source=Path(sys.argv[1]).resolve(); build='--build' in sys.argv
attempt=root/'evidence/development'/time.strftime('%Y%m%dT%H%M%S')
attempt.mkdir(exist_ok=False);snap=attempt/source.name;snap.write_bytes(source.read_bytes())
args=['lean','-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
if build:
 rel=source.relative_to(root/'source/extension');target=obj/rel.with_suffix('.olean');target.parent.mkdir(parents=True,exist_ok=True);args+=['-o',str(target)]
args+=[str(source)]
t=time.monotonic()
with (attempt/'compiler.log').open('w') as f:
 try:p=subprocess.run(args,env=env,cwd=root/'source/extension',stdout=f,stderr=subprocess.STDOUT,timeout=150);code=p.returncode
 except subprocess.TimeoutExpired:code=124
rec={'command':args,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'exit_code':code,'seconds':time.monotonic()-t,'build':build,'snapshot':snap.name}
(attempt/'receipt.json').write_text(json.dumps(rec,indent=2))
print((attempt/'compiler.log').read_text());print('RECEIPT',attempt,code,round(rec['seconds'],2));sys.exit(code)

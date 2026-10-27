#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,time,json,hashlib,sys
root=Path(__file__).resolve().parents[1]
kit=Path('/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2')
out=root/'development/olean';out.mkdir(exist_ok=True)
env=os.environ.copy();env['LEAN_PATH']=':'.join([str(out),str(root/'src'),str(root/'dependencies'),(root/'development/LEAN_PATH.txt').read_text().strip()])
env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
for name in sys.argv[1:]:
 p=next((root/d/(name+'.lean') for d in ['src','dependencies','audit','development'] if (root/d/(name+'.lean')).exists()))
 cmd=[str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-R',str(p.parent),'-o',str(out/(name+'.olean')),str(p)]
 t=time.monotonic()
 try:
  cp=subprocess.run(cmd,cwd=kit/'workspace',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=80)
  text=cp.stdout;rc=cp.returncode
 except subprocess.TimeoutExpired as e:
  text=e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or '';rc=124
 log=root/'development/logs'/f'{name}.{time.time_ns()}.log';log.write_text(text)
 with (root/'development/ATTEMPTS.jsonl').open('a') as f:f.write(json.dumps({'module':name,'rc':rc,'seconds':time.monotonic()-t,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'command':cmd,'log':str(log.relative_to(root))})+'\n')
 print(name,'RC',rc,round(time.monotonic()-t,2),text,flush=True)
 if rc:sys.exit(rc)

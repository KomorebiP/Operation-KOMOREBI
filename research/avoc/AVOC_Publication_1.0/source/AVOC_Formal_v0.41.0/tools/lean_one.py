#!/usr/bin/env python3
"""Bounded direct Lean check using exact-pin package cache; records each invocation."""
import argparse, hashlib, json, os, signal, subprocess, time, re
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('--seconds',type=int,default=90); p.add_argument('--no-output',action='store_true'); p.add_argument('--log',default=None)
a=p.parse_args(); root=Path(__file__).resolve().parents[1]
kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
build=root/'.lake/build/lib/lean'; build.mkdir(parents=True,exist_ok=True)
paths=[build]+[d/'.lake/build/lib/lean' for d in (kit/'workspace/.lake/packages').iterdir() if d.is_dir()]
env=os.environ.copy(); env['LEAN_PATH']=':'.join(map(str,paths));env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
source=root/a.source; out=build/Path(a.source).with_suffix('.olean');out.parent.mkdir(parents=True,exist_ok=True)
cmd=[str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true']
if not a.no_output: cmd+=['-o',str(out)]
cmd+=[str(source)]
log=root/(a.log or ('results/v0.35.0/'+source.stem+'.log')); log.parent.mkdir(parents=True,exist_ok=True)
def local_imports():
    result={}
    for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',source.read_text(),re.M):
        artifact=build/Path(name.replace('.','/')).with_suffix('.olean')
        result[name]=hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.exists() else None
    return result
source_before=hashlib.sha256(source.read_bytes()).hexdigest()
imports_before=local_imports()
t=time.monotonic();timeout=False
with log.open('w') as f:
 proc=subprocess.Popen(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=proc.wait(timeout=a.seconds)
 except subprocess.TimeoutExpired:
  timeout=True;os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
record=dict(command=cmd,returncode=code,timed_out=timeout,seconds=round(time.monotonic()-t,3),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),log=str(log.relative_to(root)),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
record['import_outputs']=imports_before
record['imports_unchanged']=imports_before==local_imports()
record['source_before_sha256']=source_before
record['source_unchanged']=source_before==record['source_sha256']
record['output_sha256']=hashlib.sha256(out.read_bytes()).hexdigest() if (not a.no_output and code==0 and out.exists()) else None
log.with_suffix('.json').write_text(json.dumps(record,indent=2)+'\n')
print(log.read_text());print(json.dumps(record));raise SystemExit(code if not timeout else 124)

#!/usr/bin/env python3
from pathlib import Path
import subprocess,os,sys,time,json,signal,hashlib
ROOT=Path(__file__).resolve().parents[1];K=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2');W=K/'workspace'
mod=sys.argv[1];src=ROOT/'lean'/Path(mod.replace('.','/')+'.lean');dst=ROOT/'build'/Path(mod.replace('.','/')+'.olean');dst.parent.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env['MALLOC_ARENA_MAX']='2';env['LEAN_PATH']=':'.join(map(str,[ROOT/'build',W/'.lake/build/lib/lean',*sorted((W/'.lake/packages').glob('*/.lake/build/lib/lean'))]))
base=ROOT/'development';n=len(list(base.glob(mod+'_attempt*.json')))+1;stem=f'{mod}_attempt{n:03d}'
(base/(stem+'.lean.txt')).write_bytes(src.read_bytes());cmd=[str(K/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-o',str(dst),str(src)];t=time.monotonic();p=subprocess.Popen(cmd,cwd=ROOT/'lean',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
try:out,_=p.communicate(timeout=160);timed=False
except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,_=p.communicate();timed=True
(base/(stem+'.log')).write_text(out);r=dict(module=mod,command=cmd,exit_code=p.returncode,timed_out=timed,seconds=round(time.monotonic()-t,3),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest());(base/(stem+'.json')).write_text(json.dumps(r,indent=2));print(out);print(json.dumps(r));sys.exit(1 if p.returncode or timed else 0)

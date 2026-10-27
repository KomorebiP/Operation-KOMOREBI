#!/usr/bin/env python3
"""Compile one source using the pinned kit; keep real compiler output and exit status."""
import argparse, hashlib, json, os, signal, subprocess, time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--kit',default=os.environ.get('KOMOREBI_LEAN_KIT'));p.add_argument('--timeout',type=int,default=150);a=p.parse_args()
if not a.kit: p.error('Supply --kit or set KOMOREBI_LEAN_KIT to the pinned offline runtime')
root=Path(__file__).resolve().parents[1]; src=Path(a.source)
if src.suffix!='.lean': src=Path('RealizationBoundaries')/(str(src)+'.lean')
out=root/'.lake/build/lib/lean'/src.with_suffix('.olean');out.parent.mkdir(parents=True,exist_ok=True)
logs=root/'verification/development'; logs.mkdir(exist_ok=True)
idx=len(list(logs.glob(src.stem+'_*.json')))+1;stem=logs/f'{src.stem}_{idx:03d}'
cmd=[str(Path(a.kit)/'toolchain/bin/lake'),'env','lean','-DwarningAsError=true','-DautoImplicit=false','-o',str(out),str(src)]
t=time.time(); proc=subprocess.Popen(cmd,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
try: stdout,_=proc.communicate(timeout=a.timeout)
except subprocess.TimeoutExpired:
 os.killpg(proc.pid,signal.SIGKILL);stdout,_=proc.communicate();stdout+='\nTIMEOUT\n'
rec={'command':cmd,'exit_code':proc.returncode,'seconds':time.time()-t,'source_sha256':hashlib.sha256((root/src).read_bytes()).hexdigest()}
stem.with_suffix('.log').write_text(stdout);stem.with_suffix('.json').write_text(json.dumps(rec,indent=2))
print(stdout,end=''); print('EXIT',proc.returncode,'SECONDS',round(rec['seconds'],2));raise SystemExit(proc.returncode)

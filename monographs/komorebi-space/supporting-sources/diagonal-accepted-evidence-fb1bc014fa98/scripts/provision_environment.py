#!/usr/bin/env python3
"""Provision the exact accepted Lean/mathlib pair in a separate local runtime."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,tarfile,hashlib,zstandard,sys
root=Path(__file__).resolve().parents[2]/'.lean_runtime'
root.mkdir(exist_ok=True);(root/'logs').mkdir(exist_ok=True);(root/'downloads').mkdir(exist_ok=True)
def run(cmd,log,cwd=None):
 print('COMMAND',cmd,file=log,flush=True)
 subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
def lean():
 with (root/'logs/compiler_setup.log').open('w',buffering=1) as log:
  archive=root/'downloads/lean.tar.zst'
  run(['curl','--fail','--location','--retry','2','--output',str(archive),'https://github.com/leanprover/lean4/releases/download/v4.34.0-rc2/lean-4.34.0-rc2-linux.tar.zst'],log)
  print('Downloaded',archive.stat().st_size,file=log,flush=True)
  with archive.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as r,tarfile.open(fileobj=r,mode='r|') as t:t.extractall(root,filter='data')
  binary=root/'lean-4.34.0-rc2-linux/bin/lean';run([str(binary),'--version'],log)
  return {'archive_sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'binary':str(binary)}
def mathlib():
 with (root/'logs/mathlib_setup.log').open('w',buffering=1) as log:
  m=root/'mathlib';m.mkdir(exist_ok=False)
  run(['git','init'],log,m);run(['git','remote','add','origin','https://github.com/leanprover-community/mathlib4.git'],log,m)
  run(['git','fetch','--depth','1','origin','aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],log,m);run(['git','checkout','--detach','FETCH_HEAD'],log,m)
  return {'path':str(m),'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=m,text=True).strip()}
results={}
with ThreadPoolExecutor(max_workers=2) as pool:
 jobs={'lean':pool.submit(lean),'mathlib':pool.submit(mathlib)}
 for key,job in jobs.items():
  try:results[key]={'status':'passed','result':job.result()}
  except Exception as e:results[key]={'status':'failed','error':repr(e)}
(root/'logs/setup_result.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
if any(v['status']!='passed' for v in results.values()):sys.exit(1)

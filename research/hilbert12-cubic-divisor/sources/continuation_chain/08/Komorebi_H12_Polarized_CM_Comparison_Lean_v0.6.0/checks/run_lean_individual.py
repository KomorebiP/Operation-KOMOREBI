#!/usr/bin/env python3
"""Bounded per-module compiler runs. Final audit authenticates every source."""
import os,pathlib,subprocess,time,sys,hashlib,json,re,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=pathlib.Path);ap.add_argument('modules',nargs='+');a=ap.parse_args();rt=a.runtime.resolve();src=ROOT/'formalization';logs=ROOT/'evidence/individual';logs.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['LEAN_PATH']=str(src)+':'+':'.join(str(p/'.lake/build/lib/lean') for p in (rt/'workspace/.lake/packages').iterdir() if p.is_dir())
 lean=rt/'toolchain/bin/lean';version=subprocess.check_output([str(lean),'--version'],text=True).strip();assert '4.34.0-rc2' in version
 for mod in a.modules:
  p=src/f'{mod}.lean';h=hashlib.sha256(p.read_bytes()).hexdigest();cmd=[str(lean),'-j1','-DwarningAsError=true','-o',mod+'.olean',mod+'.lean'];tic=time.monotonic()
  r=subprocess.run(cmd,cwd=src,env=env,capture_output=True,text=True,timeout=80)
  (logs/f'{mod}.log').write_text(r.stdout+r.stderr)
  rec={'module':mod,'command':cmd,'seconds':time.monotonic()-tic,'exit_status':r.returncode,'source_sha256':h,'lean_version':version}
  (logs/f'{mod}.json').write_text(json.dumps(rec,indent=2)+'\n');print(mod,r.returncode,round(rec['seconds'],2),flush=True)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==h
if __name__=='__main__':main()

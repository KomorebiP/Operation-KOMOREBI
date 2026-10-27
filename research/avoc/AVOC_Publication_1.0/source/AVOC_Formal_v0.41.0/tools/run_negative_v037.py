#!/usr/bin/env python3
from pathlib import Path
import argparse,json,os,re,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.37.0/negative_all';OUT.mkdir(parents=True,exist_ok=True)
FILES=sorted((ROOT/'tests/negative').glob('*.lean'))
ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=20);ns=ap.parse_args()
lean=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))/'toolchain/bin/lean'
for idx,f in enumerate(FILES[ns.start:ns.start+ns.count],start=ns.start):
 t=time.monotonic();cp=subprocess.run([str(lean),'-j1','-DwarningAsError=true',str(f)],cwd=ROOT,text=True,capture_output=True,timeout=180)
 text=cp.stdout+cp.stderr
 substantive=cp.returncode!=0 and not re.search(r'unknown module|object file .* does not exist|failed to locate|timeout',text,re.I)
 (OUT/(f.name+'.log')).write_text(text)
 rec={'index':idx,'file':f.name,'returncode':cp.returncode,'substantive':bool(substantive),'seconds':round(time.monotonic()-t,3)}
 (OUT/(f.name+'.json')).write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps(rec),flush=True)
 if not substantive: raise SystemExit(1)

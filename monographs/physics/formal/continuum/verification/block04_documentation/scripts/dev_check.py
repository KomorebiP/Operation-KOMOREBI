#!/usr/bin/env python3
"""Snapshot and compile one development module. Every attempt is retained."""
import sys, pathlib, subprocess, time, json, hashlib, argparse, os, re
from datetime import datetime, timezone
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('module')
parser.add_argument('--kit',type=pathlib.Path,default=os.environ.get('KOMOREBI_LEAN_KIT'))
args=parser.parse_args()
if args.kit is None:
 parser.error('--kit or KOMOREBI_LEAN_KIT is required')
mod=args.module
if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)*',mod):
 parser.error('Invalid Lean module name')
kit=pathlib.Path(args.kit).expanduser().resolve()
if not (kit/'run.sh').is_file():
 parser.error('Portable launcher not found in the supplied kit')
out=root/'verification/development/block04'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out.mkdir(parents=True)
src=root/(mod.replace('.', '/')+'.lean')
(out/src.name).write_bytes(src.read_bytes())
obj=root/'.lake/build/lib/lean'/(mod.replace('.', '/')+'.olean')
obj.parent.mkdir(parents=True,exist_ok=True)
argv=['bash',str(kit/'run.sh'),'lake','env','lean','-j1','-DwarningAsError=true','-o',str(obj),str(src.relative_to(root))]
t=time.monotonic()
try:
 r=subprocess.run(argv,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30)
 text=r.stdout; code=r.returncode
except subprocess.TimeoutExpired as e:
 text=str(e.stdout)+'\nTIMEOUT: not a proof.';code=124
(out/'compile.log').write_text(text)
(out/'receipt.json').write_text(json.dumps({'module':mod,'argv':argv,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'returncode':code,'seconds':time.monotonic()-t},indent=2)+'\n')
print(text, end='')
print(('PASS' if code==0 else 'FAIL'),mod,'log:',out,flush=True)
sys.exit(code)

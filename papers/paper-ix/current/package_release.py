#!/usr/bin/env python3
"""Package an already verified frozen edition. This does not renew proof audits."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=args.output.resolve()
    if out.is_relative_to(ROOT):raise SystemExit('Place the ZIP outside the source release directory.')
    if out.exists():raise SystemExit('Output already exists; use a new path.')
    check=subprocess.run([sys.executable,str(ROOT/'verify_release.py')],cwd=ROOT)
    if check.returncode:raise SystemExit('Integrity check failed. No ZIP created.')
    manifest=json.loads((ROOT/'MANIFEST_SHA256.json').read_text());paths=[r['path']for r in manifest['files']]+['MANIFEST_SHA256.json']
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel in sorted(paths):z.write(ROOT/rel,ROOT.name+'/'+rel)
    with zipfile.ZipFile(out) as z:
        bad=z.testzip()
        if bad:raise SystemExit('ZIP CRC failed: '+bad)
    h=hashlib.sha256(out.read_bytes()).hexdigest()
    print(json.dumps({'status':'PASS','archive':str(out),'bytes':out.stat().st_size,'sha256':h,'members':len(paths),'scope':'Frozen manifest integrity and ZIP CRC, not a new mathematical verification.'},indent=2))
if __name__=='__main__':main()

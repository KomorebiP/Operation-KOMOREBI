#!/usr/bin/env python3
"""Package checked Komorebi Physics v0.27.0 source without runtime/cache."""
from __future__ import annotations
import argparse, hashlib, json, os, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_DIRS={'.lake','.git','__pycache__'}
EXCLUDED_NAMES={'PACKAGE_MANIFEST.json','SHA256SUMS.txt','current_process.json'}
EXCLUDED_SUFFIXES={'.pyc','.olean','.ilean','.o','.so','.ttf','.otf','.woff','.woff2'}
ARCROOT=Path('Komorebi_Physics_Lean_v0.27.0_WORK')

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def payload_paths()->list[Path]:
    out=[]
    for base,dirs,names in os.walk(ROOT,followlinks=False):
        directory=Path(base)
        dirs[:]=sorted(d for d in dirs if d not in EXCLUDED_DIRS and not (directory/d).is_symlink())
        for name in sorted(names):
            p=directory/name
            if p.is_symlink() or name in EXCLUDED_NAMES or p.suffix in EXCLUDED_SUFFIXES or p.suffix=='.zip':
                continue
            out.append(p)
    return sorted(out)

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=ROOT.parent/'Komorebi_Physics_Lean_v0.27.0_Checked_Block_27.zip')
    args=ap.parse_args()
    report_path=ROOT/'verification/block27_final/report.json'
    report=json.loads(report_path.read_text())
    if report.get('status')!='PASS': raise SystemExit('Refusing to package an unchecked release.')
    for rel,expected in report['source_sha256'].items():
        p=ROOT/rel
        if not p.is_file() or sha256(p)!=expected:
            raise SystemExit(f'Verified proof input changed: {rel}')
    paths=payload_paths()
    records=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in paths]
    manifest={
      'schema_version':2,
      'release':'Komorebi Physics Lean v0.27.0 — Checked Block 27',
      'created_utc':datetime.now(timezone.utc).isoformat(),
      'verification_status':'PASS',
      'counts':report['counts'],
      'negative_controls':report['negative_controls'],
      'runtime_bundled':False,
      'compiler_and_mathlib_rebuilt_from_source':False,
      'hash_scope':'All payload files except PACKAGE_MANIFEST.json and SHA256SUMS.txt; SHA256SUMS also hashes PACKAGE_MANIFEST.json.',
      'verification_report':'verification/block27_final/report.json',
      'verification_report_sha256':sha256(report_path),
      'payload_file_count':len(records),
      'payload_bytes':sum(x['bytes'] for x in records),
      'files':records,
    }
    m=ROOT/'PACKAGE_MANIFEST.json'; m.write_text(json.dumps(manifest,indent=2)+'\n')
    paths.append(m)
    s=ROOT/'SHA256SUMS.txt'; s.write_text(''.join(f'{sha256(p)}  {p.relative_to(ROOT)}\n' for p in sorted(paths)))
    paths.append(s)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths): z.write(p,arcname=str(ARCROOT/p.relative_to(ROOT)))
    with zipfile.ZipFile(args.out) as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f'ZIP CRC failed: {bad}')
    print(json.dumps({'archive':str(args.out),'bytes':args.out.stat().st_size,'sha256':sha256(args.out),'files':len(paths),'zip_crc':'PASS'},indent=2))
if __name__=='__main__': main()

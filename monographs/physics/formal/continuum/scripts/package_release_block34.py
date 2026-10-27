#!/usr/bin/env python3
"""Package checked Komorebi Physics v0.34.0 source without runtime/cache."""
from __future__ import annotations
import argparse, hashlib, json, os, zipfile
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_DIRS={'.lake','.git','__pycache__'}
EXCLUDED_NAMES={'PACKAGE_MANIFEST.json','SHA256SUMS.txt','current_process.json'}
EXCLUDED_SUFFIXES={'.pyc','.olean','.ilean','.o','.so','.ttf','.otf','.woff','.woff2'}
ARCROOT=Path('Komorebi_Physics_Lean_v0.34.0_Checked_Block_34')
def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def payload_paths():
    out=[]
    for base,dirs,names in os.walk(ROOT,followlinks=False):
        d=Path(base)
        dirs[:]=sorted(x for x in dirs if x not in EXCLUDED_DIRS and not (d/x).is_symlink())
        for name in sorted(names):
            p=d/name
            if p.is_symlink() or name in EXCLUDED_NAMES or p.suffix in EXCLUDED_SUFFIXES or p.suffix=='.zip':
                continue
            out.append(p)
    return sorted(out)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=ROOT.parent/'Komorebi_Physics_Lean_v0.34.0_Checked_Block_34.zip')
    a=ap.parse_args()
    report_path=ROOT/'verification/block34_final/report.json'
    report=json.loads(report_path.read_text())
    if report.get('status')!='PASS': raise SystemExit('Refusing to package unchecked release.')
    for rel,expected in report['source_sha256'].items():
        p=ROOT/rel
        if not p.is_file() or sha256(p)!=expected:
            raise SystemExit(f'Verified proof input changed: {rel}')
    paths=payload_paths()
    rec=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in paths]
    manifest={
      'schema_version':2,
      'release':'Komorebi Physics Lean v0.34.0 — Checked Block 34',
      'created_utc':datetime.now(timezone.utc).isoformat(),
      'verification_status':'PASS',
      'verification_mode':report['verification_mode'],
      'counts':report['counts'],
      'negative_controls':report['negative_controls'],
      'runtime_bundled':False,
      'compiler_and_mathlib_rebuilt_from_source':False,
      'hash_scope':'All payload files except PACKAGE_MANIFEST.json and SHA256SUMS.txt; SHA256SUMS also hashes PACKAGE_MANIFEST.json.',
      'verification_report':'verification/block34_final/report.json',
      'verification_report_sha256':sha256(report_path),
      'payload_file_count':len(rec),
      'payload_bytes':sum(x['bytes'] for x in rec),
      'files':rec,
    }
    m=ROOT/'PACKAGE_MANIFEST.json'; m.write_text(json.dumps(manifest,indent=2)+'\n')
    paths.append(m)
    sums=ROOT/'SHA256SUMS.txt'
    sums.write_text(''.join(f'{sha256(p)}  {p.relative_to(ROOT)}\n' for p in sorted(paths)))
    paths.append(sums)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if a.out.exists(): a.out.unlink()
    with zipfile.ZipFile(a.out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths): z.write(p,arcname=str(ARCROOT/p.relative_to(ROOT)))
    with zipfile.ZipFile(a.out) as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f'ZIP CRC failed: {bad}')
        for n in z.namelist():
            pp=Path(n)
            if pp.is_absolute() or '..' in pp.parts:
                raise RuntimeError(f'unsafe ZIP member: {n}')
    print(json.dumps({'archive':str(a.out),'bytes':a.out.stat().st_size,'sha256':sha256(a.out),'files':len(paths),'zip_crc':'PASS'},indent=2))
if __name__=='__main__': main()

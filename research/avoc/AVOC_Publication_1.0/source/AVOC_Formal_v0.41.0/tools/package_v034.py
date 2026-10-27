#!/usr/bin/env python3
"""Package cumulative AVOC v0.34 sources/evidence and verify every payload."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_DIRS={'.lake','.git','__pycache__'}
EXCLUDED_SUFFIXES={'.pyc','.olean','.ilean','.pid','.ttf','.otf','.woff','.woff2'}
def sha(p):
 d=hashlib.sha256()
 with Path(p).open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):d.update(c)
 return d.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT.parent/'AVOC_Formal_v0.34.0.zip');a=p.parse_args();out=a.output.resolve()
 if out.is_relative_to(ROOT):p.error('archive must be outside source tree')
 out.parent.mkdir(parents=True,exist_ok=True);manifest=ROOT/'SHA256SUMS.txt';files=[]
 for f in sorted(ROOT.rglob('*')):
  rel=f.relative_to(ROOT)
  if any(x in EXCLUDED_DIRS for x in rel.parts):continue
  if f.is_symlink():raise RuntimeError(f'unexpected source-tree symlink: {rel}')
  if f.is_file() and f.suffix not in EXCLUDED_SUFFIXES and f!=manifest:files.append(f)
 hashes={f.relative_to(ROOT).as_posix():sha(f) for f in files}
 manifest.write_text(''.join(f'{d}  {n}\n' for n,d in hashes.items()));files.append(manifest);hashes[manifest.name]=sha(manifest)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in files:z.write(f,ROOT.name+'/'+f.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  expected={ROOT.name+'/'+n for n in hashes};assert len(z.namelist())==len(expected) and set(z.namelist())==expected
  for n,d in hashes.items():assert hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==d and sha(ROOT/n)==d
 digest=sha(out);Path(str(out)+'.sha256').write_text(f'{digest}  {out.name}\n')
 report=dict(archive=str(out),bytes=out.stat().st_size,sha256=digest,payload_files=len(files),manifest_entries=len(files)-1,zip_integrity=True,exact_payload_comparison=True,scope='Packaging integrity only; proof/runtime audit recorded separately.')
 (out.parent/'AVOC_v0.34.0_Package_Verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Strict SHA-256 integrity check. It does not write into the package."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path);args=ap.parse_args()
 root=(args.root or Path(__file__).resolve().parents[1]).resolve();manifest=root/'MANIFEST_SHA256.json'
 if not manifest.is_file():raise SystemExit(f'Manifest not found: {manifest}')
 data=json.loads(manifest.read_text());files=data['files'];errors=[]
 for name,expected in files.items():
  p=root/name
  if not p.resolve().is_relative_to(root):errors.append({'path':name,'error':'unsafe manifest path'});continue
  if not p.is_file():errors.append({'path':name,'error':'missing'})
  elif digest(p)!=expected:errors.append({'path':name,'error':'hash mismatch'})
 actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p!=manifest}
 extras=sorted(actual-set(files));errors.extend({'path':name,'error':'extra file'} for name in extras)
 report={'status':'passed' if not errors else 'failed','package_kind':data.get('package_kind'),'manifest_entries':len(files),'actual_files_excluding_manifest':len(actual),'errors':errors}
 print(json.dumps(report,indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(main())

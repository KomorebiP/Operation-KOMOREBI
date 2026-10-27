#!/usr/bin/env python3
"""Validate the exact file set, byte lengths and SHA256 hashes of a pristine delivery.
Also rejects symlinks, path traversal and font binaries. The manifest is an integrity
record, not a digital signature or proof of mathematical correctness.
"""
from __future__ import annotations
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,sys
FONT_EXT={'.otf','.ttf','.ttc','.woff','.woff2','.pfb','.pfa'}
FONT_MAGIC={b'OTTO',b'ttcf',b'wOFF',b'wOF2',b'\x00\x01\x00\x00'}

def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def inspect(root:Path)->dict:
 errors=[];manifest=root/'MANIFEST_SHA256.json'
 try:entries=json.loads(manifest.read_text())['files']
 except Exception as exc:return {'status':'FAIL','errors':['invalid_manifest: '+repr(exc)]}
 names=set()
 for entry in entries:
  n=entry.get('path','');p=PurePosixPath(n)
  if not n or p.is_absolute() or '..' in p.parts or '\\' in n or n in names or str(p)!=n or n=='MANIFEST_SHA256.json':
   errors.append('invalid_or_duplicate_path: '+n);continue
  names.add(n);f=root/n
  if f.is_symlink():errors.append('symlink: '+n);continue
  if not f.is_file():errors.append('missing: '+n);continue
  if f.stat().st_size!=entry['bytes'] or digest(f)!=entry['sha256']:errors.append('changed: '+n)
 actual={str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*') if p.is_file() and p!=manifest}
 for name in sorted(actual-names):errors.append('extra: '+name)
 for p in root.rglob('*'):
  if p.is_symlink():errors.append('symlink: '+str(p.relative_to(root)))
  if p.is_file():
   with p.open('rb') as f:head=f.read(4)
   if p.suffix.lower() in FONT_EXT or head in FONT_MAGIC:errors.append('font_binary: '+str(p.relative_to(root)))
 return {'status':'PASS' if not errors else 'FAIL','manifest_entries':len(entries),'actual_payload_files':len(actual),'errors':errors}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
 result=inspect(a.root.resolve());print(json.dumps(result,indent=2));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

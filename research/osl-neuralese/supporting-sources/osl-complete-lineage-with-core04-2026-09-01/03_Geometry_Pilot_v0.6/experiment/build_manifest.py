#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def main():
 root=Path(__file__).resolve().parents[1]
 excluded={'SHA256SUMS.txt','SHA256SUMS.txt.sha256'}
 files=[]
 for p in root.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(root).as_posix()
  if rel in excluded or '__pycache__' in p.parts or '.pytest_cache' in p.parts or p.suffix in {'.pyc','.pyo'}:continue
  files.append((rel,p))
 files.sort()
 manifest=root/'SHA256SUMS.txt'
 manifest.write_text(''.join(f'{sha(p)}  {rel}\n' for rel,p in files))
 digest=sha(manifest)
 (root/'SHA256SUMS.txt.sha256').write_text(f'{digest}  SHA256SUMS.txt\n')
 print(f'entries={len(files)} manifest_sha256={digest}')
if __name__=='__main__':main()

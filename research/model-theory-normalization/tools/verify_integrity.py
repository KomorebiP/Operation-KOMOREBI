#!/usr/bin/env python3
"""Check distributed bytes before rerunning any audit (which rewrites evidence)."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 manifest=json.loads((ROOT/'FILE_MANIFEST.json').read_text());bad=[]
 for r in manifest['files']:
  p=ROOT/r['path']
  if not p.is_file():bad.append('missing '+r['path']);continue
  with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
  if p.stat().st_size!=r['bytes'] or h!=r['sha256']:bad.append('changed '+r['path'])
 if bad:print('\n'.join(bad),file=sys.stderr);return 1
 print(f"PASS: {len(manifest['files'])} payload hashes");return 0
if __name__=='__main__':raise SystemExit(main())

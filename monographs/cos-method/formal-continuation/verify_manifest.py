#!/usr/bin/env python3
"""Verify the immutable file manifest delivered with this checkpoint."""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parent
bad=[];count=0
for line in (root/'SHA256SUMS.txt').read_text().splitlines():
    if not line:continue
    wanted,name=line.split('  ',1)
    path=root/name
    try:
        with path.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    except OSError as exc:
        bad.append(f'{name}: {exc}');continue
    count+=1
    if actual!=wanted:bad.append(f'{name}: checksum mismatch')
if bad:
    print('\n'.join(bad));sys.exit(1)
print(f'PASS: {count} manifest entries match.')

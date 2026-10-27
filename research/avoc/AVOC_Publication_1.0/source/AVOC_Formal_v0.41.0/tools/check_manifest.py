#!/usr/bin/env python3
"""Read-only integrity check of a delivered AVOC source/evidence manifest."""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parents[1]
failed=[];count=0
for line in (root/'SHA256SUMS.txt').read_text().splitlines():
    digest,name=line.split('  ',1);p=root/name;count+=1
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        failed.append(name)
print(f'{count-len(failed)}/{count} file hashes match')
for name in failed:print('MISMATCH',name)
sys.exit(1 if failed else 0)

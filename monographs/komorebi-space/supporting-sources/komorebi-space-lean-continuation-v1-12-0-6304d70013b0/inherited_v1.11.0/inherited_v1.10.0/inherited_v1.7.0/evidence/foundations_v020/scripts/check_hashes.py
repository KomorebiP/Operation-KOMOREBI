#!/usr/bin/env python3
"""Verify all packaged files listed in FILES.sha256; extra replay outputs are ignored."""
from pathlib import Path
import hashlib
import sys

root=Path(__file__).resolve().parents[1]
failed=[]
entries=(root/'FILES.sha256').read_text().splitlines()
for line in entries:
    digest,name=line.split('  ',1)
    file=root/name
    if not file.resolve().is_relative_to(root.resolve()) or not file.is_file():
        failed.append(name+': missing/invalid')
    elif hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
        failed.append(name+': changed')
if failed:
    print('\n'.join(failed),file=sys.stderr)
    sys.exit(1)
print(f'PASS: {len(entries)} packaged files match their recorded SHA-256 values.')

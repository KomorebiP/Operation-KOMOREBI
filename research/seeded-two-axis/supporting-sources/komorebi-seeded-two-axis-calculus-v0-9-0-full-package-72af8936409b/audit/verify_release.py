#!/usr/bin/env python3
"""Verify the supplied release checksum inventory. Reruns change recorded outputs."""
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[1]
failures=[]; count=0
for line in (root/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1);p=root/name;count+=1
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        failures.append(name)
print(f'Checked {count} files; mismatches: {failures}')
raise SystemExit(1 if failures else 0)

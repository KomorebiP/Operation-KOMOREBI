#!/usr/bin/env python3
"""Check the distributed package's recorded files, without asserting proof correctness."""
from pathlib import Path
import hashlib, json
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'MANIFEST_SHA256.json').read_text())
failures = []
for item in manifest['files']:
    p = root / item['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
        failures.append(item['path'])
if failures:
    raise SystemExit('Integrity FAILED: ' + ', '.join(failures))
print(f"Integrity PASS: {len(manifest['files'])} recorded files match.")
print('This checks file identity, not mathematical correctness.')

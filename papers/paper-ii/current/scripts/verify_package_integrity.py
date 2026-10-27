#!/usr/bin/env python3
"""Verify the extracted release's exact manifest inventory and SHA256 hashes."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'MANIFEST_SHA256.json').read_text())
expected = {row['path'] for row in manifest['files']}
actual = {str(p.relative_to(root)) for p in root.rglob('*')
          if p.is_file() and p != root / 'MANIFEST_SHA256.json'
          and '__pycache__' not in p.parts and p.suffix != '.pyc'}
errors = []
if actual != expected:
    errors.append({'missing': sorted(expected - actual), 'unexpected': sorted(actual - expected)})
for row in manifest['files']:
    path = root / row['path']
    if not path.is_file():
        continue
    data = path.read_bytes()
    if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
        errors.append({'hash_or_size_mismatch': row['path']})
print(json.dumps({'status': 'FAIL' if errors else 'PASS',
                  'files_checked': len(manifest['files']), 'errors': errors}, indent=2))
sys.exit(bool(errors))

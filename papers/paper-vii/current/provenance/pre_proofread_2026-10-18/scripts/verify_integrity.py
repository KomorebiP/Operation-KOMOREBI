#!/usr/bin/env python3
"""Verify every shipped file against the edition's size and SHA-256 manifest."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / 'MANIFEST_SHA256.json').read_text())
failures = []
expected = set()
for item in manifest['files']:
    relative = Path(item['path'])
    if relative.is_absolute() or '..' in relative.parts:
        failures.append({'path': item['path'], 'problem': 'unsafe manifest path'})
        continue
    expected.add(item['path'])
    path = root / relative
    if not path.is_file():
        failures.append({'path': item['path'], 'problem': 'missing'})
    elif path.stat().st_size != item['bytes']:
        failures.append({'path': item['path'], 'problem': 'size differs'})
    elif hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        failures.append({'path': item['path'], 'problem': 'checksum differs'})
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()
          and p != root / 'MANIFEST_SHA256.json'}
failures.extend({'path': p, 'problem': 'unlisted file'} for p in sorted(actual - expected))
print(json.dumps({'status': 'FAIL' if failures else 'PASS',
                  'files_checked': len(manifest['files']),
                  'failures': failures}, indent=2))
sys.exit(bool(failures))

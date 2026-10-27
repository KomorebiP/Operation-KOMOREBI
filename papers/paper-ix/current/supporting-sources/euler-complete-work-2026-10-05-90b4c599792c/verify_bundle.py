#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
data=json.loads((root/'MANIFEST.json').read_text())
for relative,record in data['files'].items():
 with (root/relative).open('rb') as stream:
  actual=hashlib.file_digest(stream,'sha256').hexdigest()
 if actual!=record['sha256']:raise SystemExit('Hash mismatch: '+relative)
print(str(len(data['files']))+' research and provenance files verified.')

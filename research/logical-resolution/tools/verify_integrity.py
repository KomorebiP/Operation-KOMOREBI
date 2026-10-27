"""Verify the released payload. Run before regenerating execution logs/results."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'FILE_MANIFEST.json').read_text())
errors=[]
for item in manifest['files']:
    p=ROOT/item['path']
    if not p.is_file(): errors.append('missing '+item['path']);continue
    data=p.read_bytes()
    if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
        errors.append('changed '+item['path'])
if errors: raise SystemExit('\n'.join(errors))
print(f"PASS: {len(manifest['files'])} payload files match size and SHA-256")

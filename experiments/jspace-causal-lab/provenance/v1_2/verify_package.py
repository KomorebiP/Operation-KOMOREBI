"""Integrity only: exact non-cache file set and SHA-256 against MANIFEST.json."""
from pathlib import Path
import hashlib,json,sys
r=Path(__file__).resolve().parent
m=json.loads((r/'MANIFEST.json').read_text())
def include(p):return p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and '.pytest_cache' not in p.parts
actual={str(p.relative_to(r)) for p in r.rglob('*') if include(p)}
if actual!=set(m['files']):raise AssertionError({'extra':sorted(actual-set(m['files'])),'missing':sorted(set(m['files'])-actual)})
for name,digest in m['files'].items():
 p=r/name
 assert not Path(name).is_absolute() and '..' not in Path(name).parts
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
print(json.dumps({'status':'PASS','exact_file_set':True,'files':len(actual),'scope':'File integrity, not scientific certification'},indent=2))

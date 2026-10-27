from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'validation/OVERCOMPLETE_PREOUTCOME_FREEZE.json';d=json.loads(p.read_text());failed=[]
for item in d['files']:
 q=ROOT/item['path'];h=hashlib.sha256(q.read_bytes()).hexdigest() if q.is_file() else None
 if h!=item['sha256'] or (q.stat().st_size if q.is_file() else None)!=item['size_bytes']:
  failed.append(item['path'])
out={'schema':'rrct.v055.overcomplete_freeze_verification.v1','all_checks_pass':not failed,'file_count':len(d['files']),'failed':failed,'manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
print(json.dumps(out,indent=2,sort_keys=True));raise SystemExit(0 if not failed else 1)

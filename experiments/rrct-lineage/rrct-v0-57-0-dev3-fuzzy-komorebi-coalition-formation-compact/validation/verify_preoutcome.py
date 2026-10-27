from __future__ import annotations
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
manifest=ROOT/'validation/PREOUTCOME_FREEZE.json'
payload=json.loads(manifest.read_text())
failed=[]
for entry in payload['files']:
    path=ROOT/entry['relative_path']
    if not path.is_file():
        failed.append({'path':entry['relative_path'],'reason':'missing'})
        continue
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=entry['sha256'] or path.stat().st_size!=entry['size_bytes']:
        failed.append({'path':entry['relative_path'],'reason':'digest_or_size'})
companion=manifest.with_suffix(manifest.suffix+'.sha256')
companion_ok=companion.is_file() and companion.read_text().split()[0]==hashlib.sha256(manifest.read_bytes()).hexdigest()
result={'schema':'rrct.v057.preoutcome_verification.v1','file_count':len(payload['files']),'companion_matches':companion_ok,'failed':failed,'all_checks_pass':companion_ok and not failed}
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(0 if result['all_checks_pass'] else 1)

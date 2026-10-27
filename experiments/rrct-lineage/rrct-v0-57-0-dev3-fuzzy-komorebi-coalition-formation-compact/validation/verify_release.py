from __future__ import annotations
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]

def sha(path:pathlib.Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

checks={}
# Pre-outcome seal.
freeze=ROOT/'validation/PREOUTCOME_FREEZE.json'
f=json.loads(freeze.read_text())
checks['preoutcome_file_count']=len(f['files'])==13
checks['preoutcome_files']=all((ROOT/e['relative_path']).is_file() and sha(ROOT/e['relative_path'])==e['sha256'] and (ROOT/e['relative_path']).stat().st_size==e['size_bytes'] for e in f['files'])
checks['preoutcome_companion']=(freeze.with_suffix(freeze.suffix+'.sha256').read_text().split()[0]==sha(freeze))
# Results.
result_manifest=ROOT/'results/RESULT_SHA256.json'
r=json.loads(result_manifest.read_text())
checks['result_file_count']=len(r['files'])==r['file_count']
checks['result_files']=all((ROOT/'results'/rel).is_file() and sha(ROOT/'results'/rel)==entry['sha256'] and (ROOT/'results'/rel).stat().st_size==entry['size_bytes'] for rel,entry in r['files'].items())
checks['summary_digest']=sha(ROOT/'results/HOLDOUT_SUMMARY.json')==r['canonical_summary_sha256']
checks['analysis_digest']=sha(ROOT/'results/HOLDOUT_ANALYSIS.json')==r['canonical_analysis_sha256']
# Models.
model_manifest=ROOT/'results/MODEL_SHA256.json'
m=json.loads(model_manifest.read_text())
checks['model_count']=len(m['files'])==32
checks['model_files']=all((ROOT/'models/holdout'/name).is_file() and sha(ROOT/'models/holdout'/name)==entry['sha256'] and (ROOT/'models/holdout'/name).stat().st_size==entry['size_bytes'] for name,entry in m['files'].items())
# Scientific status.
summary=json.loads((ROOT/'results/HOLDOUT_SUMMARY.json').read_text())
checks['scientific_status']=summary['status']=='V057_FROZEN_ENDPOINTS_MET'
checks['all_endpoints']=summary['all_endpoints_met'] and summary['passed_endpoint_count']==22 and summary['endpoint_count']==22
checks['replay']=json.loads((ROOT/'validation/REPLAY_VERIFICATION.json').read_text())['state_exact']
checks['release_status']=json.loads((ROOT/'V0_57_RELEASE_VERIFICATION.json').read_text())['status']=='V057_RELEASE_VERIFIED'
failed=sorted(name for name,value in checks.items() if not value)
payload={'schema':'rrct.v057.release_audit.v1','check_count':len(checks),'passed_count':sum(bool(v) for v in checks.values()),'failed_checks':failed,'all_checks_pass':not failed}
print(json.dumps(payload,indent=2,sort_keys=True))
raise SystemExit(0 if not failed else 1)

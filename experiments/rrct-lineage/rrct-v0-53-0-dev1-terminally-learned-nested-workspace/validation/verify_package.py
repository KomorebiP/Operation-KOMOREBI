from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
freeze=json.loads((ROOT/'PREOUTCOME_FREEZE.json').read_text())
for rel,m in freeze['files'].items():
 p=ROOT/rel;checks[f'freeze::{rel}']=p.is_file() and p.stat().st_size==m['size_bytes'] and sha(p)==m['sha256']
summary=json.loads((ROOT/'results/summary.json').read_text());analysis=json.loads((ROOT/'results/analysis.json').read_text());models=json.loads((ROOT/'results/MODEL_SHA256.json').read_text());replay=json.loads((ROOT/'validation/REPLAY_VERIFICATION.json').read_text())
checks['summary_endpoints']=summary['all_endpoints_met'];checks['analysis_endpoints']=analysis['all_endpoints_met'];checks['analysis_link']=summary['analysis_digest']==analysis['digest'];checks['model_count']=len(models)==12;checks['replay']=replay['all_checks_pass']
for n,m in models.items():
 p=ROOT/'models'/n;checks[f'model::{n}']=p.is_file() and p.stat().st_size==m['size_bytes'] and sha(p)==m['sha256']
manifest=ROOT/'BUILD_SHA256SUMS.txt';comp=ROOT/'BUILD_SHA256SUMS.txt.sha256'
if manifest.exists() and comp.exists():checks['manifest_companion']=comp.read_text().split()[0]==sha(manifest)
payload={'schema':'rrct.v053.package_verification.v1','status':'V053_PACKAGE_VERIFIED' if all(checks.values()) else 'V053_PACKAGE_FAILED','all_checks_pass':all(checks.values()),'failed_checks':sorted(k for k,v in checks.items() if not v),'check_count':len(checks),'summary_digest':summary['digest'],'analysis_digest':analysis['digest']}
print(json.dumps(payload,indent=2,sort_keys=True));raise SystemExit(0 if payload['all_checks_pass'] else 1)

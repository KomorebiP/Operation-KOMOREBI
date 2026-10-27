#!/usr/bin/env python3
"""Project validator for this release's computation-manifest v1 contract.
This is NOT a copy or an execution claim for the unmounted Mathbox validator.
"""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--root',type=Path,required=True);a=p.parse_args()
d=json.loads(a.manifest.read_text());root=a.root.resolve()
required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
assert required<=d.keys() and d['schema_version']==1
for k in ('claim_id','result'):assert isinstance(d[k],str) and d[k].strip()
assert d['command'] and isinstance(d['repository']['dirty'],bool)
assert d['environment']['software']
for k in ('assertion_tested','coefficient_domain','conventions'):assert d['mathematics'][k]
assert d['mathematics']['bounds'] and d['mathematics']['non_claims']
assert isinstance(d['randomness']['used'],bool) and d['run']['started_at']
assert d['run']['exit_status']==0 and math.isfinite(d['run']['runtime_seconds']) and d['run']['runtime_seconds']>=0
assert d['outputs'] and d['checks'] and d['residual_risks']
for item in d['outputs']+d.get('input_artifacts',[]):
    name=Path(item['path']);assert not name.is_absolute() and '..' not in name.parts
    target=(root/name).resolve();assert target.is_relative_to(root) and target.is_file()
    assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']
print('PASS_PROJECT_V1_MANIFEST',len(d['outputs']),len(d.get('input_artifacts',[])))

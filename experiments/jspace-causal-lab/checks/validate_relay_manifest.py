"""Local legacy-v1 structure/path/hash validation, not the canonical Mathbox CLI."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'checks/relay/COMPUTATION_MANIFEST.json').read_text())
required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
assert required.issubset(m) and m['schema_version']==1
assert m['run']['exit_status']==0 and m['run']['runtime_seconds']>=0
assert m['mathematics']['bounds'] and m['mathematics']['non_claims']
for x in m['outputs']:
    p=Path(x['path']);assert not p.is_absolute() and '..' not in p.parts
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==x['sha256'],p
for p,h in m['execution_source_hashes'].items():
    assert not Path(p).is_absolute() and '..' not in Path(p).parts
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
print(json.dumps({'status':'PASS','validator':'Local version-1 structure/path/SHA-256 check, not canonical Mathbox CLI','outputs_verified':len(m['outputs']),'input_hashes_verified':len(m['execution_source_hashes'])},indent=2))

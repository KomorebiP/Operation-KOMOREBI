"""Local legacy-v1 evidence structure and file-hash check. Not the Mathbox CLI."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];m=json.loads((ROOT/'checks/COMPUTATION_MANIFEST_1_3.json').read_text())
required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
assert required.issubset(m) and m['schema_version']==1
assert m['run']['exit_status']==0 and m['run']['runtime_seconds']>=0
assert m['mathematics']['bounds'] and m['mathematics']['non_claims']
for item in m['outputs']:
 p=Path(item['path']);assert not p.is_absolute() and '..' not in p.parts
 assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==item['sha256'],p
for name,h in m['execution_source_hashes'].items():
 p=Path(name);assert not p.is_absolute() and '..' not in p.parts
 assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
print(json.dumps({'status':'PASS','validator':'Local version-1 structure/path/SHA-256 check. Canonical Mathbox CLI not executed.','outputs_checked':len(m['outputs']),'input_hashes_checked':len(m['execution_source_hashes'])},indent=2))

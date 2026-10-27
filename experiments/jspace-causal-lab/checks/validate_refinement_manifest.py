"""Local legacy-v1 evidence structure/path/hash check, not the Mathbox CLI."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'checks/COMPUTATION_MANIFEST_1_2.json';m=json.loads(p.read_text())
required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
assert required.issubset(m)
assert m['schema_version']==1 and m['run']['exit_status']==0
assert m['run']['runtime_seconds']>=0 and m['mathematics']['bounds'] and m['mathematics']['non_claims']
for x in m['outputs']:
 q=Path(x['path']);assert not q.is_absolute() and '..' not in q.parts
 assert hashlib.sha256((ROOT/q).read_bytes()).hexdigest()==x['sha256'],q
for name,sha in m['execution_source_hashes'].items():
 q=Path(name);assert not q.is_absolute() and '..' not in q.parts
 assert hashlib.sha256((ROOT/q).read_bytes()).hexdigest()==sha,q
print(json.dumps({'status':'PASS','validator':'Local structure/path/SHA-256 checker; canonical Mathbox CLI not invoked','outputs':len(m['outputs']),'source_hashes':len(m['execution_source_hashes'])},indent=2))

#!/usr/bin/env python3
"""Verify the packaged release identities and the current proof-audit revision."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',default='MANIFEST_SHA256.json');a=p.parse_args()
obj=json.loads((ROOT/a.manifest).read_text())
errors=[]
for row in obj['files']:
 path=ROOT/row['path']
 if not path.is_file():errors.append('Missing '+row['path']);continue
 if path.stat().st_size!=row['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:errors.append('Changed '+row['path'])
release=json.loads((ROOT/'RELEASE.json').read_text())
proof=hashlib.sha256((ROOT/'sources/strengthening.tex').read_bytes()).hexdigest()
if release['source_revision']['strengthening.tex']!=proof:errors.append('Strengthening source revision mismatch')
audit=json.loads((ROOT/'evidence/FINAL_MATHEMATICAL_DELTA_AUDIT.json').read_text())
for row in audit['reviewed_files']:
 path=ROOT/row['path']
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:errors.append('Stale mathematical audit: '+row['path'])
for row in audit['underlying_proof_sources']:
 prefix='../euler_threshold_free_2026_10_06/'
 if row['path'].startswith(prefix):
  path=ROOT/'preserved/threshold_free'/row['path'][len(prefix):]
 elif row['path'].startswith('preserved/threshold_free/'):
  path=ROOT/row['path']
 else:errors.append('Unknown proof source mapping: '+row['path']);continue
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:errors.append('Changed underlying proof: '+row['path'])
print(json.dumps({'status':'PASS' if not errors else 'FAIL','files_checked':len(obj['files']),'errors':errors,'scope':'Byte integrity and declared revision consistency only; not an independent proof or authenticity signature'},indent=2))
raise SystemExit(bool(errors))

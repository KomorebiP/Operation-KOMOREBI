"""Saved-byte provenance check; this does not repeat the mathematical audit."""
import hashlib,json
from pathlib import Path
V=Path('verification/chemistry-stage17');ACTIVE=['study-001','audit-001']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify(root=Path('.')):
    records=[]
    for name in ACTIVE:
        r=json.loads((root/V/name/'manifest.json').read_bytes())
        if r['run']['status']!='completed':raise ValueError('Incomplete active run '+name)
        for x in r['input_artifacts']:
            if sha((root/x['path']).read_bytes())!=x['sha256'] or x['sha256']!=x['sha256_after']:raise ValueError('Changed input '+x['path'])
        for x in r['outputs']:
            if sha((root/x['path']).read_bytes())!=x['sha256']:raise ValueError('Changed output '+x['path'])
        records.append(r)
    return records
if __name__=='__main__':print(json.dumps(dict(status='passed',active_runs=len(verify()),scope='Saved-byte identity; analytic and endpoint assumptions remain separate')))

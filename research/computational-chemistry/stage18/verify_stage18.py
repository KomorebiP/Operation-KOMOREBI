import hashlib,json
from pathlib import Path
V=Path('verification/chemistry-stage18');ACTIVE=['study-001','audit-001']
def verify(root=Path('.')):
    records=[]
    for name in ACTIVE:
        r=json.loads((root/V/name/'manifest.json').read_bytes())
        if r['run']['status']!='completed':raise ValueError('Incomplete active run '+name)
        for x in r['input_artifacts']:
            if hashlib.sha256((root/x['path']).read_bytes()).hexdigest()!=x['sha256'] or x['sha256']!=x['sha256_after']:raise ValueError('Changed input '+x['path'])
        for x in r['outputs']:
            if hashlib.sha256((root/x['path']).read_bytes()).hexdigest()!=x['sha256']:raise ValueError('Changed output '+x['path'])
        records.append(r)
    return records
if __name__=='__main__':print(json.dumps(dict(status='passed',active_runs=len(verify()),scope='Saved-byte identity; not a fresh calculation or analytic proof')))

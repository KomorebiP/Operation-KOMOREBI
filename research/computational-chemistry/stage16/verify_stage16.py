"""Verify active evidence and the archived source states of superseded attempts."""
import hashlib,json,zipfile
from pathlib import Path
V=Path('verification/chemistry-stage16')
ACTIVE=['intervals-001','audit-003','narrow-003']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify(root=Path('.')):
    records=[]
    for name in ACTIVE:
        record=json.loads((root/V/name/'manifest.json').read_bytes())
        if record['run']['status']!='completed':raise ValueError('Incomplete active run '+name)
        for item in record['input_artifacts']:
            actual=sha((root/item['path']).read_bytes())
            if actual!=item['sha256'] or actual!=item['sha256_after']:raise ValueError('Changed input '+item['path'])
        for item in record['outputs']:
            if sha((root/item['path']).read_bytes())!=item['sha256']:raise ValueError('Changed output '+item['path'])
        records.append(record)
    history=json.loads((root/V/'ATTEMPTS.json').read_bytes())
    archives=[(history['historical_input_archive'],history['sha256'],['audit-001','narrow-001']),(history['second_input_archive']['path'],history['second_input_archive']['sha256'],['audit-002','narrow-002'])]
    for filename,digest,names in archives:
        raw=(root/V/filename).read_bytes()
        if sha(raw)!=digest:raise ValueError('Historical input archive changed')
        with zipfile.ZipFile(root/V/filename) as z:
            for name in names:
                record=json.loads((root/V/name/'manifest.json').read_bytes())
                for item in record['input_artifacts']:
                    if sha(z.read(item['path']))!=item['sha256'] or item['sha256']!=item['sha256_after']:raise ValueError('Historical source mismatch')
                for item in record['outputs']:
                    if sha((root/item['path']).read_bytes())!=item['sha256']:raise ValueError('Historical output changed')
    return records
if __name__=='__main__':print(json.dumps(dict(status='passed',active_runs=len(verify()),historical_runs=4,scope='Provenance identity only; separate analytic and arithmetic hypotheses are retained')))

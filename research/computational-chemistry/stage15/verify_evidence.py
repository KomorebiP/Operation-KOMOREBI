"""Verify recorded finite-run inputs and outputs without rerunning NumPy."""
import hashlib
import json
from pathlib import Path

RUNS=['reduction-001','kernel-001','responses-001']
AREA=Path('verification/chemistry-stage15')

def verify(root=Path('.')):
    records=[]
    for name in RUNS:
        record=json.loads((root/AREA/name/'manifest.json').read_bytes())
        if record['run']['status']!='completed':raise ValueError('Incomplete run '+name)
        for item in record['input_artifacts']:
            actual=hashlib.sha256((root/item['path']).read_bytes()).hexdigest()
            if actual!=item['sha256'] or actual!=item['sha256_after']:raise ValueError('Input changed: '+item['path'])
        for item in record['outputs']:
            if hashlib.sha256((root/item['path']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Output changed: '+item['path'])
        records.append(record)
    return records

if __name__=='__main__':
    records=verify();print(json.dumps(dict(status='passed',runs=len(records),qualification='Hash identity checks; analytic and physical claims require their separate obligations')))

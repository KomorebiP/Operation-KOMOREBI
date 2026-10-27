#!/usr/bin/env python3
"""Verify the six roots-route input/output hash records, without rerunning."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifests=sorted((HERE/'computation_records').glob('*.manifest.json'))
    assert len(manifests)==6
    for p in manifests:
        r=json.loads(p.read_text())
        assert r['schema_version']==2 and r['run']['status']=='completed' and r['run']['exit_status']==0
        for a in r['input_artifacts']:
            f=(ROOT/a['path']).resolve()
            assert f.is_relative_to(ROOT)
            assert sha(f)==a['sha256_after']==a['sha256'],a['path']
        for a in r['outputs']:
            f=(ROOT/a['path']).resolve()
            assert f.is_relative_to(ROOT) and sha(f)==a['sha256'],a['path']
        print(p.name+': completed, all hashes match')
    print('Finite evidence integrity does not certify ABC or the universal proofs.')
if __name__=='__main__':main()

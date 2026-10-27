#!/usr/bin/env python3
"""Check recorded run status and all pinned input/output hashes. Stdlib only."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifests=sorted((ROOT/'computation_records').glob('*.manifest.json'))
    assert len(manifests)==5,'Expected five finite computation records'
    for manifest in manifests:
        record=json.loads(manifest.read_text())
        assert record['schema_version']==2
        assert record['run']['status']=='completed' and record['run']['exit_status']==0
        for item in record['input_artifacts']:
            path=(ROOT/item['path']).resolve()
            assert path.is_relative_to(ROOT) and path.is_file()
            assert item['sha256']==item['sha256_after']==sha(path),item['path']
        for item in record['outputs']:
            path=(ROOT/item['path']).resolve()
            assert path.is_relative_to(ROOT) and path.is_file()
            assert item['sha256']==sha(path),item['path']
        print(manifest.name+': completed, all hashes match')
    print('Integrity checks do not certify the mathematical conclusions.')

if __name__=='__main__':
    main()

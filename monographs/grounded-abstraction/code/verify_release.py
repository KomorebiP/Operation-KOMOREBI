"""Project-local receipt and snapshot checks. This is not a proof verifier."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local(name: str) -> Path:
    p = Path(name)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError(f'Invalid relative path: {name}')
    resolved = (ROOT / p).resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError('Path leaves project root')
    return resolved

def require(condition: bool, message: str) -> None:
    if not condition: raise ValueError(message)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt-only', action='store_true')
    args = parser.parse_args()
    m = json.loads((ROOT/'validation/computation_manifest.json').read_text())
    required = {'schema_version','claim_id','repository','command','environment','mathematics',
                'randomness','run','outputs','checks','result','residual_risks'}
    require(required <= m.keys(), 'Missing v1 receipt fields')
    require(m['schema_version'] == 1, 'This local verifier supports the delivered v1 receipt')
    require(bool(m['claim_id']) and bool(m['command']), 'Missing execution identity')
    require(type(m['repository']['dirty']) is bool, 'Invalid repository status')
    require(m['environment']['software'] and m['environment']['hardware'], 'Missing environment')
    maths = m['mathematics']
    for field in ('assertion_tested','coefficient_domain','conventions','inputs','bounds','non_claims'):
        require(bool(maths.get(field)), 'Missing mathematical field: '+field)
    require(m['run']['exit_status'] == 0, 'Run did not complete successfully')
    seconds = m['run']['runtime_seconds']
    require(isinstance(seconds,(int,float)) and math.isfinite(seconds) and seconds >= 0, 'Invalid run time')
    require(bool(m['run']['started_at']), 'Missing start time')
    require(m['randomness']['used'] is False, 'Unexpected randomized execution')
    for output in m['outputs']:
        require(bool(re.fullmatch('[0-9a-f]{64}', output['sha256'])), 'Invalid output hash')
        require(sha(local(output['path'])) == output['sha256'], 'Changed output: '+output['path'])
    for item in m['input_artifacts']:
        require(item['sha256'] == item['sha256_after'] == sha(local(item['path'])), 'Changed input: '+item['path'])
    checks = json.loads((ROOT/'validation/aggregate_checks.json').read_text())
    require(checks['status'] == 'PASS', 'Exact checks did not pass')
    require(checks['group_count'] == checks['predecessor']['groups'] + checks['new']['groups'], 'Group count mismatch')
    require(checks['assertions'] == checks['predecessor']['assertions'] + checks['new']['assertions'], 'Assertion count mismatch')
    for name in ('exact_checks.json','observable_checks.json','quantitative_checks.json'):
        result=json.loads((ROOT/'validation'/name).read_text())
        require(result['status']=='PASS' and result['assertions']==sum(g['assertions'] for g in result['groups']), 'Inconsistent suite '+name)
    print('PASS: local v1 receipt fields, pinned inputs, output hashes, and finite-count consistency.')
    if not args.receipt_only:
        inv = json.loads((ROOT/'SHA256SUMS.json').read_text())
        for name, digest in inv['files'].items():
            require(sha(local(name)) == digest, 'Snapshot mismatch: '+name)
        print(f"PASS: {len(inv['files'])} frozen snapshot files.")
    print('Not a proof-kernel result, external attestation, or independent scientific replication.')

if __name__ == '__main__': main()

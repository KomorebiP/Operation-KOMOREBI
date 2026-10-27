#!/usr/bin/env python3
"""Check packaged integrity and recorded evidence. This does NOT rerun Lean.

This package-local validator supports its own version-1 evidence record and
all SHA256SUMS entries. It is not a copy of the Mathbox validator.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parent
    def require(test: bool, message: str) -> None:
        if not test:
            raise ValueError(message)
    def safe(name: str) -> Path:
        p = Path(name)
        require(not p.is_absolute() and '..' not in p.parts, 'Unsafe path: ' + name)
        q = (root / p).resolve()
        require(q.is_relative_to(root), 'Escaping path: ' + name)
        return q
    checked = 0
    names = set()
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        checksum, name = line.split('  ', 1)
        require(re.fullmatch(r'[0-9a-f]{64}', checksum) is not None, 'Invalid SHA256')
        require(name not in names, 'Duplicate manifest path')
        names.add(name)
        require(sha(safe(name)) == checksum, 'Changed artifact: ' + name)
        checked += 1
    receipt = json.loads((root / 'FINAL_VERIFICATION_RECEIPT.json').read_text())
    require(receipt['status'] == 'CHECKED', 'Receipt not checked')
    order = json.loads((root / 'MODULE_ORDER.json').read_text())
    require(len(order) == len(set(order)) == 18, 'Unexpected module inventory')
    records = receipt['execution_records']
    require([x['module'] for x in records] == order, 'Module order mismatch')
    for row in records:
        require(row['exit_status'] == 0, 'Failed final module: ' + row['module'])
        require(row['source_sha256_before'] == row['source_sha256_after'] ==
                sha(safe(row['source'])), 'Source evidence mismatch')
        require(sha(safe(row['log'])) == row['log_sha256'], 'Log evidence mismatch')
        original = json.loads(safe(row['receipt']).read_text())
        for key in ('module', 'source_sha256_before', 'source_sha256_after', 'exit_status',
                    'log_sha256', 'command', 'olean_sha256'):
            require(row[key] == original[key], 'Copied receipt mismatch: ' + key)
        require('-DwarningAsError=true' in row['command'], 'Missing strict checking')
    declaration_count = 0
    for name in order:
        text = (root / 'Komorebi' / (name + '.lean')).read_text()
        require(re.search(r'\b(?:sorry|admit|axiom|unsafe)\b', text) is None,
                'Forbidden source token: ' + name)
        declaration_count += len(re.findall(
            r'(?m)^\s*(?:@\[[^\n]*\]\s*)?(?:theorem|lemma)\s+', text))
    require(declaration_count == 51, 'Declaration count mismatch')
    audit = receipt['axiom_audit']
    log = safe(audit['log']).read_text()
    deps = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", log, re.S)
    require(len(deps) == len({name for name, _ in deps}) == 51, 'Incomplete axiom audit')
    found = {a.strip() for _, group in deps for a in group.split(',') if a.strip()}
    require(found <= {'propext', 'Classical.choice', 'Quot.sound'}, 'Extra axioms')
    manifest = json.loads((root / 'COMPUTATION_MANIFEST.json').read_text())
    required = {'schema_version','claim_id','repository','command','environment',
                'mathematics','randomness','run','outputs','checks','result','residual_risks'}
    require(required <= manifest.keys() and manifest['schema_version'] == 1,
            'Invalid evidence-manifest structure')
    for key in ('claim_id', 'command', 'result'):
        require(isinstance(manifest[key], str) and bool(manifest[key].strip()),
                'Missing manifest field: ' + key)
    maths = manifest['mathematics']
    for key in ('assertion_tested','coefficient_domain','conventions'):
        require(isinstance(maths[key], str) and bool(maths[key].strip()), 'Empty math field')
    require(isinstance(maths['inputs'], list) and isinstance(maths['bounds'], dict)
            and bool(maths['bounds']) and bool(maths['non_claims']), 'Missing scope')
    require(type(manifest['repository']['dirty']) is bool, 'Invalid repository record')
    require(bool(manifest['environment']['software']), 'Missing environment')
    require(type(manifest['randomness']['used']) is bool and not manifest['randomness']['used'],
            'Unexpected random computation')
    run = manifest['run']
    require(isinstance(run['started_at'], str) and bool(run['started_at']), 'Missing run timestamp')
    require(type(run['exit_status']) is int and run['exit_status'] == 0, 'Manifest run failed')
    require(type(run['runtime_seconds']) in (int, float) and
            math.isfinite(run['runtime_seconds']) and run['runtime_seconds'] >= 0, 'Invalid timing')
    require(bool(manifest['outputs']), 'Missing outputs')
    for output in manifest['outputs']:
        require(sha(safe(output['path'])) == output['sha256'], 'Evidence output changed')
    for source in manifest['mathematics']['inputs']:
        require(sha(safe(source['path'])) == source['sha256'], 'Evidence input changed')
    print(f'PASS: {checked} packaged hashes, 18 successful module receipts, '
          '51 audited declarations, and package-local evidence-manifest checks.')
    print('This verifies recorded evidence and byte integrity; use verify_blocks.py to rerun Lean.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('FAILED:', exc, file=sys.stderr)
        sys.exit(1)

"""Verify every declared file and the complete pre-replay bundle inventory.

Run before mutating examples. Python bytecode caches are ignored. Manifests are
integrity inventories, not signatures or proof that their contents are true.
"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def main() -> None:
    manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    rows=(ROOT/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
    declared={}
    for row in rows:
        expected,name=row.split('  ',1)
        if name in declared or not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('Malformed or duplicate checksum entry.')
        target=ROOT/name
        if target.is_symlink() or not target.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Invalid manifest path: '+name)
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=expected:
            raise ValueError('Hash mismatch: '+name)
        declared[name]=expected
    listed={x['path']:x['sha256'] for x in manifest['files']}
    if listed!=declared or len(listed)!=len(manifest['files']):raise ValueError('Manifest and checksums differ.')
    for item in manifest['files']:
        if (ROOT/item['path']).stat().st_size!=item['bytes']:raise ValueError('Size mismatch: '+item['path'])
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    expected=set(manifest['inventory'])
    if actual!=expected:
        raise ValueError(f'Inventory mismatch; extra={sorted(actual-expected)}, missing={sorted(expected-actual)}')
    if expected!=set(declared)|{'MANIFEST.json','SHA256SUMS.txt'}:raise ValueError('Unhashed unexpected inventory member.')
    print(f'PASS: {len(declared)} declared hashes and complete {len(actual)}-file inventory before replay.')

if __name__=='__main__':main()

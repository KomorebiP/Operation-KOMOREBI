#!/usr/bin/env python3
"""Verify exact historical proof snapshots against their current counterparts.

The original archives are identified by hash, not recursively bundled. This is
source-integrity checking, not authorship authentication or proof checking.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath

EXPECTED = {'0.2.0': 10, '0.3.0': 23, '0.4.0': 37, '0.5.0': 51}

def safe_file(root: Path, name: str) -> Path:
    if type(name) is not str:
        raise ValueError('A source path must be a string')
    rel = PurePosixPath(name)
    if not name or rel.is_absolute() or '..' in rel.parts or '\\' in name or str(rel) != name:
        raise ValueError('Unsafe source path: ' + name)
    base = root.resolve()
    path = base.joinpath(*rel.parts)
    if any(p.is_symlink() for p in (path, *path.parents) if p != base and p.is_relative_to(base)):
        raise ValueError('Symlink in source path: ' + name)
    if not path.is_file() or not path.resolve().is_relative_to(base):
        raise ValueError('Missing or escaping source: ' + name)
    return path

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def verify_lineage(root: Path) -> dict:
    data = json.loads(safe_file(root, 'provenance/lineage.json').read_text(encoding='utf-8'))
    if data['schema'] != 'komorebi.repair.source-lineage.v1':
        raise ValueError('Unknown lineage schema')
    releases = data['releases']
    if len(releases) != len(EXPECTED) or {r['version'] for r in releases} != set(EXPECTED):
        raise ValueError('Missing, duplicate, or unexpected lineage release')
    out = []
    for record in releases:
        version = record['version']
        files = record['files']
        prefix = 'provenance/v' + version
        if record['snapshots'] != prefix or len(files) != EXPECTED[version]:
            raise ValueError('Incorrect snapshot scope: ' + version)
        names = [f['path'] for f in files]
        if len(set(names)) != len(names):
            raise ValueError('Duplicate historical source path')
        for item in files:
            name = item['path']
            if not name.startswith('lean/KomorebiRepair/') or not name.endswith('.lean'):
                raise ValueError('Unexpected historical source')
            old = safe_file(root, prefix + '/' + name)
            new = safe_file(root, name)
            if old.stat().st_size != item['bytes'] or sha(old) != item['sha256']:
                raise ValueError('Historical snapshot changed: ' + version + '/' + name)
            if new.read_bytes() != old.read_bytes():
                raise ValueError('Current proof differs from snapshot: ' + version + '/' + name)
        out.append({'version': version, 'files': len(files), 'pass': True,
                    'original_archive_sha256': record['archive_sha256']})
    return {'status': 'PASS', 'releases': out, 'scope': 'Source integrity, not kernel replay'}

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    a = ap.parse_args()
    print(json.dumps(verify_lineage(a.root), indent=2))

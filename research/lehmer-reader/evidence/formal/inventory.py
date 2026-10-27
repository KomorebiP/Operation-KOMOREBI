#!/usr/bin/env python3
"""Inventory the recovered Lehmer source set without modifying it."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import zipfile


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def is_proof_file(name):
    p = Path(name)
    return (p.suffix in {'.lean', '.olean', '.ilean', '.v', '.vo', '.agda', '.thy'}
            or p.name in {'lean-toolchain', 'lakefile.lean', 'lakefile.toml',
                          'lake-manifest.json'})


def main():
    release = Path(__file__).resolve().parents[2]
    historical = release / 'historical'
    files = sorted(p for p in historical.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.suffix != '.pyc')
    archives = []
    for archive in files:
        if archive.suffix != '.zip':
            continue
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            archives.append({
                'path': str(archive.relative_to(release)),
                'sha256': sha256(archive.read_bytes()),
                'members': len(names),
                'proof_assistant_entries': [n for n in names if is_proof_file(n)],
            })
    record = {
        'audit_date': '2026-10-09',
        'scope': 'Six recovered source archives, extracted trees, and embedded parent archives.',
        'excluded_generated_files': 'Python __pycache__ and .pyc files produced by imports are excluded.',
        'file_count': len(files),
        'extension_counts': dict(sorted(Counter(p.suffix for p in files).items())),
        'proof_assistant_files': [str(p.relative_to(release)) for p in files
                                  if is_proof_file(str(p))],
        'archives': archives,
        'files': [{
            'path': str(p.relative_to(release)),
            'bytes': p.stat().st_size,
            'sha256': sha256(p.read_bytes()),
        } for p in files],
        'compile_status': 'Not attempted: no recovered proof-assistant source or project.',
        'conclusion': 'Written mathematical proofs and exact computations are present. No proof-assistant certificate is present.',
    }
    output = Path(__file__).with_name('formal_inventory.json')
    output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['file_count', 'extension_counts',
          'proof_assistant_files', 'compile_status', 'conclusion']}, indent=2))


if __name__ == '__main__':
    main()

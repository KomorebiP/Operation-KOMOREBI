#!/usr/bin/env python3
"""Bind the independent audit manifest to its existing local evidence files.

Run after final audit reports/logs are frozen. Production source hashes are
validated first and are never rewritten by this utility. The manifest itself
is excluded to avoid a recursive hash dependency.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'LOCAL_PROOF_AUDIT_SOURCES.json'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text())
    for key in ('new_production_sources', 'internal_dependency_source_closure',
                'reviewed_predecessor_definition_sources'):
        for entry in manifest[key]:
            path = ROOT / entry['path']
            if sha256(path) != entry['sha256']:
                raise RuntimeError(f"Frozen source changed: {entry['path']}")
    paths = [ROOT / 'LOCAL_PROOF_AUDIT.md']
    paths.extend(path for path in (ROOT / 'checks/local_audit').rglob('*')
                 if path.is_file() and '__pycache__' not in path.parts
                 and path.suffix in {'.py', '.lean', '.log', '.json'})
    manifest['evidence'] = [
        {'path': str(path.relative_to(ROOT)), 'sha256': sha256(path)}
        for path in sorted(set(paths))
    ]
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"Pinned {len(manifest['evidence'])} evidence files.")


if __name__ == '__main__':
    main()

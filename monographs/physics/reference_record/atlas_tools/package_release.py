#!/usr/bin/env python3
"""Package a reviewed physics edition and verify every archived file hash.

Run from any directory. This does not build documents, execute Lean, audit
proofs, or turn a missing publication review into a successful review.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def selected_files():
    build_suffixes = {'.aux', '.log', '.out', '.toc', '.xdv', '.pdf'}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if '__pycache__' in relative.parts or path.suffix == '.pyc':
            continue
        if relative.parent == Path('source') and path.suffix in build_suffixes:
            continue
        yield relative, path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('The output ZIP must be outside the packaged directory.')
    validation = json.loads((ROOT / 'editorial/edition_validation.json').read_text())
    if not validation.get('status', '').startswith('PASS'):
        raise RuntimeError('A completed scoped publication review is required.')
    for record in validation['pdfs']:
        path = ROOT / record['path']
        if not path.is_file() or sha256(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            raise RuntimeError('Publication validation is stale: ' + record['path'])
    records = [
        {'path': str(relative), 'bytes': path.stat().st_size, 'sha256': sha256(path)}
        for relative, path in selected_files() if relative != Path('MANIFEST.json')
    ]
    manifest = {
        'schema': 'komorebi.physics.package-manifest.v1',
        'edition': validation['edition'],
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'files': records,
    }
    (ROOT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative, path in selected_files():
            archive.write(path, str(Path(ROOT.name) / relative))
    with zipfile.ZipFile(output) as archive:
        failed = archive.testzip()
        if failed is not None:
            raise RuntimeError('ZIP CRC failure: ' + failed)
        prefix = ROOT.name + '/'
        archived = {name[len(prefix):] for name in archive.namelist()}
        expected = {record['path'] for record in records} | {'MANIFEST.json'}
        if archived != expected:
            raise RuntimeError('ZIP and manifest coverage differ.')
        for record in records:
            data = archive.read(prefix + record['path'])
            if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                raise RuntimeError('Archived identity mismatch: ' + record['path'])
    print(json.dumps({'path': str(output), 'bytes': output.stat().st_size,
                      'sha256': sha256(output), 'files': len(records) + 1,
                      'manifest_entries': len(records), 'crc_and_all_hashes': 'PASS'}, indent=2))


if __name__ == '__main__':
    main()

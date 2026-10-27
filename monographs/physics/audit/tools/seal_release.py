#!/usr/bin/env python3
"""Seal a frozen regular-file release tree and verify its clean ZIP extraction."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile

SCHEMA = 'komorebi.exact-file-set.sha256.v1'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def inventory(root):
    rows = []
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink(), 'Symlink in release: ' + str(p))
        if p.is_dir():
            continue
        require(p.is_file(), 'Nonregular release entry: ' + str(p))
        rel = p.relative_to(root).as_posix()
        require('__pycache__' not in p.parts and p.suffix != '.pyc', 'Bytecode cache in release: ' + rel)
        if rel != 'MANIFEST.json':
            rows.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': digest(p)})
    return rows

def verify(root):
    data = json.loads((root / 'MANIFEST.json').read_text())
    require(data['schema'] == SCHEMA, 'Unknown manifest schema')
    expected = data['files']
    require(len({x['path'] for x in expected}) == len(expected), 'Duplicate manifest entry')
    require(inventory(root) == expected, 'Exact file set, byte size, or hash mismatch')
    return {'status': 'PASS', 'payload_files': len(expected),
            'payload_bytes': sum(x['bytes'] for x in expected),
            'manifest_sha256': digest(root / 'MANIFEST.json')}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path)
    ap.add_argument('--verify-only', action='store_true')
    args = ap.parse_args()
    root = args.root.resolve(strict=True)
    if args.verify_only:
        print(json.dumps(verify(root), indent=2))
        return
    require(args.out_dir is not None, '--out-dir required when sealing')
    out = args.out_dir.resolve()
    require(not out.exists(), 'Output directory already exists')
    require(not out.is_relative_to(root), 'Output may not be within release')
    require(not (root / 'MANIFEST.json').exists(), 'Release is already sealed')
    out.mkdir(parents=True)
    try:
        rows = inventory(root)
        require(bool(rows), 'Empty release')
        manifest = {'schema': SCHEMA, 'release': 'Komorebi Physics continuum convergence',
                    'version': '0.51.0', 'files': rows}
        (root / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
        before = verify(root)
        archive = out / (root.name + '.zip')
        with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
            for p in sorted(root.rglob('*')):
                if p.is_file():
                    z.write(p, root.name + '/' + p.relative_to(root).as_posix(),
                            compress_type=zipfile.ZIP_STORED if p.suffix == '.zip' else zipfile.ZIP_DEFLATED)
        with tempfile.TemporaryDirectory(prefix='clean_extraction_', dir=out) as tmp:
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                expected = {root.name + '/' + x['path'] for x in rows} | {root.name + '/MANIFEST.json'}
                require(len(names) == len(set(names)) and set(names) == expected, 'ZIP file set differs')
                require(z.testzip() is None, 'ZIP CRC failed')
                for info in z.infolist():
                    p = PurePosixPath(info.filename)
                    require(not p.is_absolute() and '..' not in p.parts and p.parts[0] == root.name,
                            'Unsafe ZIP path')
                    require(stat.S_ISREG(info.external_attr >> 16), 'Nonregular ZIP entry')
                z.extractall(tmp)
            extracted = verify(Path(tmp) / root.name)
            require(extracted == before, 'Clean extraction differs')
        require(verify(root) == before, 'Source release changed during packaging')
        receipt = {'schema': 'komorebi.physics.delivery.v1', 'status': 'PASS',
                   'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                   'archive': archive.name, 'archive_bytes': archive.stat().st_size,
                   'archive_sha256': digest(archive), 'zip_members': len(names),
                   'source_integrity': before, 'clean_extraction_integrity': extracted,
                   'scope': 'Exact delivery integrity. Formal claims are supported by the separately included acceptance receipt.'}
        (out / 'Komorebi_Physics_Continuum_Delivery_Verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))
    except Exception as error:
        (out / 'PACKAGING_FAILURE.json').write_text(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2) + '\n')
        raise

if __name__ == '__main__':
    main()

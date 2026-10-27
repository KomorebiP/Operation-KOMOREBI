#!/usr/bin/env python3
"""Package a checked source release without its compiler or dependency cache.

Run from any directory. The final verifier report must pass and its hashed
proof inputs must still match. Manifest hashes cover every packaged file except
the manifest/checksum files themselves. SHA256SUMS also hashes the manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.lake', '.git', '__pycache__'}
EXCLUDED_NAMES = {'PACKAGE_MANIFEST.json', 'SHA256SUMS.txt', 'current_process.json'}
EXCLUDED_SUFFIXES = {'.pyc', '.olean', '.ilean', '.o', '.so', '.ttf', '.otf', '.woff', '.woff2'}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def payload_paths() -> list[Path]:
    result: list[Path] = []
    for base, directories, names in os.walk(ROOT, followlinks=False):
        directory = Path(base)
        directories[:] = sorted(d for d in directories
                                if d not in EXCLUDED_DIRS and not (directory / d).is_symlink())
        for name in sorted(names):
            p = directory / name
            if p.is_symlink() or name in EXCLUDED_NAMES or p.suffix in EXCLUDED_SUFFIXES:
                continue
            # These files are intentionally external to the source release.
            if p.suffix == '.zip':
                continue
            result.append(p)
    return sorted(result)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path,
                    default=ROOT.parent / 'Komorebi_Physics_Lean_v0.25.0_Checked_Block_25.zip')
    args = ap.parse_args()
    report = json.loads((ROOT / 'verification/block25_final/report.json').read_text())
    if report['status'] != 'PASS':
        raise SystemExit('Refusing to package an unchecked release.')
    for relative, expected in report['source_sha256'].items():
        if sha256(ROOT / relative) != expected:
            raise SystemExit(f'Verified proof input changed: {relative}')
    paths = payload_paths()
    records = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                'sha256': sha256(p)} for p in paths]
    manifest = {
        'schema_version': 2,
        'release': 'Komorebi Physics Lean v0.25.0 — Checked Block 25',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'verification_status': report['status'],
        'counts': report['counts'],
        'negative_controls': report['negative_controls'],
        'runtime_bundled': False,
        'imported_dependency_cache_rebuilt_wholesale': False,
        'hash_scope': 'All payload files except PACKAGE_MANIFEST.json and SHA256SUMS.txt; SHA256SUMS additionally hashes PACKAGE_MANIFEST.json.',
        'verification_report': 'verification/block25_final/report.json',
        'verification_report_sha256': sha256(ROOT / 'verification/block25_final/report.json'),
        'payload_file_count': len(records),
        'payload_bytes': sum(row['bytes'] for row in records),
        'files': records,
    }
    mpath = ROOT / 'PACKAGE_MANIFEST.json'
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    paths.append(mpath)
    cpath = ROOT / 'SHA256SUMS.txt'
    cpath.write_text(''.join(f'{sha256(p)}  {p.relative_to(ROOT)}\n' for p in sorted(paths)))
    paths.append(cpath)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(paths):
            z.write(p, arcname=str(Path('Komorebi_Physics_Lean_v0.25.0_WORK') / p.relative_to(ROOT)))
    with zipfile.ZipFile(args.out) as z:
        bad = z.testzip()
        if bad is not None:
            raise RuntimeError(f'ZIP CRC failed: {bad}')
    print(json.dumps({'archive': str(args.out.resolve()), 'bytes': args.out.stat().st_size,
                      'sha256': sha256(args.out), 'files': len(paths), 'zip_crc': 'PASS'}, indent=2))


if __name__ == '__main__':
    main()

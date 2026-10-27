#!/usr/bin/env python3
"""Package cumulative AVOC sources and evidence, then verify every ZIP payload.

This is an integrity operation, not a substitute for proof/runtime verification.
The external verification report is not included in the manifest it verifies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.lake', '.git', '__pycache__'}
EXCLUDED_SUFFIXES = {'.pyc', '.olean', '.ilean', '.pid', '.ttf', '.otf', '.woff', '.woff2'}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT.parent / 'AVOC_Formal_v0.31.0.zip')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Place the archive outside the source tree to avoid self-inclusion.')
    output.parent.mkdir(parents=True, exist_ok=True)

    manifest = ROOT / 'SHA256SUMS.txt'
    files: list[Path] = []
    for p in sorted(ROOT.rglob('*')):
        rel = p.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if p.is_symlink():
            raise RuntimeError(f'Unexpected source-tree symlink: {rel}')
        if p.is_file() and p.suffix not in EXCLUDED_SUFFIXES and p != manifest:
            files.append(p)
    hashes = {p.relative_to(ROOT).as_posix(): sha256(p) for p in files}
    manifest.write_text(''.join(f'{digest}  {name}\n'
                                for name, digest in hashes.items()), encoding='utf-8')
    files.append(manifest)
    hashes[manifest.name] = sha256(manifest)

    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as archive:
        for p in files:
            archive.write(p, ROOT.name + '/' + p.relative_to(ROOT).as_posix())

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP integrity failure.')
        expected = {ROOT.name + '/' + name for name in hashes}
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != expected:
            raise RuntimeError('ZIP payload inventory mismatch.')
        for name, digest in hashes.items():
            actual = hashlib.sha256(archive.read(ROOT.name + '/' + name)).hexdigest()
            if actual != digest or sha256(ROOT / name) != digest:
                raise RuntimeError(f'Payload changed or mismatched: {name}')

    digest = sha256(output)
    Path(str(output) + '.sha256').write_text(f'{digest}  {output.name}\n', encoding='utf-8')
    report = dict(archive=str(output), bytes=output.stat().st_size, sha256=digest,
                  payload_files=len(files), manifest_entries=len(files)-1,
                  zip_integrity=True, exact_payload_comparison=True,
                  scope='Packaging integrity only; current proof/runtime audit recorded separately.')
    (output.parent / 'AVOC_v0.31.0_Package_Verification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

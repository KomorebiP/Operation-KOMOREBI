#!/usr/bin/env python3
"""Assemble the five saved Lean_Compact ZIP parts without using a network.

The script refuses an existing output. It authenticates the exact member name,
length and SHA-256 of each chunk and the combined XZ archive. Optional extraction
uses Python's data filter and an otherwise empty destination. Linux x86-64 is
the tested compiler platform. The package does not include runtime binaries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import sys
import zipfile

TOTAL_BYTES = 2220147424
TOTAL_SHA = 'f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7'
CHUNKS = [
    (498073600, 'ada567494283c04289d975f48f287be8fb269aa0d451fa203e3fa63e2ea46faa'),
    (498073600, '330771c6018a166c413900579c65a80ed5e6455bc5c1eb591756922f0843ef1e'),
    (498073600, '1960f958a5bafe748cbaeb432e79df459bf0dca3f0bbab672e64b8902ce16652'),
    (498073600, 'cda43d29df98b2dd929922294dce3e2aa6d68d9afa44b22189c46e25391cffda'),
    (227853024, '9e5624d005dd02d813e961458483d8f630cc245a11578f8b95ea739354bb05bf'),
]


def assemble(parts: Path, output: Path, chunks=CHUNKS,
             total_bytes: int=TOTAL_BYTES, total_sha: str=TOTAL_SHA) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + '.partial')
    combined = hashlib.sha256()
    total = 0
    records = []
    with partial.open('xb') as stream:
        for i, (expected_size, expected_hash) in enumerate(chunks, 1):
            name = f'Lean_Compact_{i:02d}.zip'
            member = f'lean-compact-{i:02d}.chunk'
            h = hashlib.sha256()
            size = 0
            with zipfile.ZipFile(parts / name) as archive:
                infos = archive.infolist()
                if len(infos) != 1 or infos[0].filename != member or infos[0].is_dir():
                    raise ValueError(f'Unexpected ZIP members in {name}')
                if infos[0].file_size != expected_size:
                    raise ValueError(f'Incorrect declared chunk length: {name}')
                with archive.open(infos[0]) as source:
                    for block in iter(lambda: source.read(8 << 20), b''):
                        stream.write(block)
                        h.update(block)
                        combined.update(block)
                        size += len(block)
                        total += len(block)
            if size != expected_size or h.hexdigest() != expected_hash:
                raise ValueError(f'Incorrect chunk identity: {name}')
            records.append({'name': name, 'bytes': size, 'sha256': h.hexdigest()})
    if total != total_bytes or combined.hexdigest() != total_sha:
        raise ValueError('Incorrect combined archive identity')
    if output.exists():
        raise FileExistsError(output)
    partial.rename(output)
    return {'status': 'PASS', 'parts': records, 'archive_bytes': total,
            'archive_sha256': combined.hexdigest()}


def extract(archive: Path, destination: Path) -> int:
    if not hasattr(tarfile, 'data_filter'):
        raise RuntimeError('A Python version with tarfile.data_filter is required for extraction')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Extraction destination must be absent or empty')
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    with tarfile.open(archive, mode='r|xz') as tar:
        for member in tar:
            p = PurePosixPath(member.name)
            if p.is_absolute() or '..' in p.parts or '\\' in member.name:
                raise ValueError(f'Unsafe archive member: {member.name}')
            tar.extract(member, destination, filter='data')
            count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parts', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--extract-to', type=Path)
    a = ap.parse_args()
    try:
        result = assemble(a.parts, a.out)
        if a.extract_to is not None:
            result['extracted_members'] = extract(a.out, a.extract_to)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, tarfile.TarError) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        print('An incomplete .partial file or extraction may remain for diagnosis.', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

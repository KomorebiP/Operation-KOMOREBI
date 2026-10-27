#!/usr/bin/env python3
"""Verify the delivered SHA256 manifest without changing any package file.

Run before rebuilding. A successful build regenerates the manifest. Disposable
Python/TeX caches are ignored, but extra substantive files are reported.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FONT_SUFFIXES = {'.ttf', '.otf', '.woff', '.woff2', '.pfb', '.pfa', '.ttc'}
DISPOSABLE = {'.aux', '.out', '.toc', '.fls', '.fdb_latexmk', '.pyc'}


def excluded(path: Path) -> bool:
    return '__pycache__' in path.parts or '.lake' in path.parts or '.work' in path.parts or path.suffix in DISPOSABLE or path == ROOT / 'SHA256SUMS.txt'


def archived_fonts(data: bytes, prefix: str, depth: int = 0) -> list[str]:
    """Inspect names inside nested ZIPs; PDFs may contain embedded fonts."""
    if depth > 8:
        raise ValueError(f'Nested archive depth exceeds inspection limit: {prefix}')
    found: list[str] = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            suffix = PurePosixPath(item.filename).suffix.lower()
            label = f'{prefix}!/{item.filename}'
            if suffix in FONT_SUFFIXES:
                found.append(label)
            elif suffix == '.zip':
                found.extend(archived_fonts(archive.read(item), label, depth + 1))
    return found


def main() -> int:
    manifest = ROOT / 'SHA256SUMS.txt'
    if not manifest.is_file():
        print('Missing SHA256SUMS.txt', file=sys.stderr)
        return 2
    expected: dict[str, str] = {}
    errors: list[str] = []
    for lineno, line in enumerate(manifest.read_text().splitlines(), 1):
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None:
            errors.append(f'Malformed manifest line {lineno}')
            continue
        digest, name = match.groups()
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or name in expected:
            errors.append(f'Unsafe or duplicate manifest name: {name}')
            continue
        expected[name] = digest
    for name, digest in expected.items():
        path = ROOT / name
        if not path.is_file():
            errors.append(f'Missing file: {name}')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f'Hash mismatch: {name}')
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and not excluded(p)}
    for name in sorted(actual - expected.keys()):
        errors.append(f'Unlisted payload file: {name}')
    fonts: list[str] = []
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        relative = str(path.relative_to(ROOT))
        if path.suffix.lower() in FONT_SUFFIXES:
            fonts.append(relative)
        elif path.suffix.lower() == '.zip':
            try:
                fonts.extend(archived_fonts(path.read_bytes(), relative))
            except (ValueError, zipfile.BadZipFile, RuntimeError) as exc:
                errors.append(f'Archive inspection failed: {relative}: {exc}')
    if fonts:
        errors.append('Standalone font files found')
    print(json.dumps({'status': 'PASS' if not errors else 'FAIL',
                      'manifest_files': len(expected), 'font_files': fonts,
                      'errors': errors,
                      'scope': 'Payload integrity and standalone-font scan, not proof verification.'}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())

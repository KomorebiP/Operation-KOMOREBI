#!/usr/bin/env python3
"""Stage installed build fonts in a temporary directory, never in the release.

Searches Fontconfig, TeX's kpsewhich and KOMOREBI_FONT_DIR. The dependency
register records original byte hashes and a fingerprint of all meaningful
SFNT tables. Build-only timestamp and checksum differences are allowed, but
changed outlines, metrics, character maps or naming tables are not.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess


def semantic_hash(path: Path) -> str:
    from fontTools.ttLib import TTFont
    digest = hashlib.sha256()
    with TTFont(path, lazy=True) as font:
        for tag in sorted(font.reader.keys()):
            if tag == 'FFTM':
                continue
            data = font.reader[tag]
            if tag == 'head':
                data = data[:8] + b'\0' * 4 + data[12:]
            digest.update(tag.encode('ascii'))
            digest.update(len(data).to_bytes(8, 'big'))
            digest.update(data)
    return digest.hexdigest()


def candidates(name: str, fontconfig: list[str]) -> list[Path]:
    paths: list[Path] = []
    for folder in os.environ.get('KOMOREBI_FONT_DIR', '').split(os.pathsep):
        if folder:
            base = Path(folder).expanduser()
            if base.is_dir():
                paths.extend(base.rglob(name))
    paths.extend(Path(p) for p in fontconfig if Path(p).name == name)
    finder = shutil.which('kpsewhich')
    if finder:
        result = subprocess.run([finder, '--all', name], text=True,
                                capture_output=True, timeout=20)
        paths.extend(Path(p) for p in result.stdout.splitlines() if p)
    windows = os.environ.get('WINDIR')
    if windows:
        paths.append(Path(windows) / 'Fonts' / name)
    paths.extend([Path.home() / 'Library/Fonts' / name,
                  Path('/Library/Fonts') / name])
    return list(dict.fromkeys(p.resolve() for p in paths if p.is_file()))


def stage_fonts(register: Path, destination: Path) -> list[dict]:
    rows = json.loads(register.read_text(encoding='utf-8'))['fonts']
    listing: list[str] = []
    fc_list = shutil.which('fc-list')
    if fc_list:
        listing = subprocess.run([fc_list, '-f', '%{file}\n'], text=True,
                                 capture_output=True, timeout=20).stdout.splitlines()
    destination.mkdir(parents=True, exist_ok=True)
    report = []
    for row in rows:
        selected = None
        for path in candidates(row['filename'], listing):
            raw = hashlib.sha256(path.read_bytes()).hexdigest()
            if raw == row['sha256'] or semantic_hash(path) == row['semantic_sha256']:
                selected = (path, raw)
                break
        if selected is None:
            raise RuntimeError(
                f"Required compatible font not found: {row['filename']}. "
                'Install the documented URW Base35, Latin Modern and DejaVu '
                'families, or set KOMOREBI_FONT_DIR to their local directory. '
                'No file has been downloaded or installed by this builder.')
        path, raw = selected
        shutil.copyfile(path, destination / row['filename'])
        report.append({'filename': row['filename'], 'source': str(path),
                       'sha256': raw, 'original_sha256': row['sha256'],
                       'semantic_sha256': row['semantic_sha256'],
                       'byte_identical_to_original': raw == row['sha256']})
    (destination.parent / 'BUILD_FONT_RESOLUTION.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report

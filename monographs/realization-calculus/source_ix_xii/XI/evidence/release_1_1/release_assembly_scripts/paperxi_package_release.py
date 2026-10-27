#!/usr/bin/env python3
"""Freeze the completed release, create its exact archive, and extract for review."""
from pathlib import Path, PurePosixPath
import datetime, hashlib, json, os, stat, zipfile

BASE = Path('/workspace/scratch/604befec1954')
ROOT = BASE / 'paperxi_release'
OUT = BASE / 'paperxi_deliverables'
ZIP = OUT / 'Paper_XI_Complete_v1.1.0_2026-10-18.zip'
EXTRACT = BASE / 'paperxi_final_extraction'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

for relative in ['README.md', 'RELEASE_REVIEW.md', 'PROGRESS_LEDGER.md',
                 'PROGRESS_LEDGER.json', 'READING_CONCORDANCE.md']:
    assert (ROOT / relative).is_file(), relative
for relative, wanted in [
    ('verification/lean/RELEASE_VERIFICATION.json', 'PASS'),
    ('evidence/release_1_1/BUILD_RECORD.json', 'passed'),
    ('evidence/release_1_1/VISUAL_REVIEW.json', 'passed'),
    ('evidence/release_1_1/FORMAL_SOURCE_BRIDGE.json', 'passed')]:
    assert json.loads((ROOT / relative).read_text())['status'] == wanted
assert 'Provisional build only' not in (ROOT / 'publication/source/lean_guide/current_verification.tex').read_text()
assert not ZIP.exists(), 'Final archive already exists; preserve or explicitly replace only after review.'
assert not EXTRACT.exists(), 'Final extraction must be new.'

files = []
for path in sorted(ROOT.rglob('*')):
    assert not path.is_symlink(), str(path)
    if not path.is_file() or path.name == 'MANIFEST.json' and path.parent == ROOT:
        continue
    relative = path.relative_to(ROOT).as_posix()
    parts = PurePosixPath(relative).parts
    assert all(p not in ['', '.', '..'] and ':' not in p for p in parts)
    assert not any(p in ['__pycache__', '.runtime', '.lake', 'objects'] for p in parts), relative
    assert path.suffix not in ['.pyc', '.olean', '.ilean'], relative
    files.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': sha(path)})

manifest = {'schema_version': 1, 'release': 'Paper XI v1.1.0',
            'checkpoint': 'P11-RELEASE-1.1.0', 'edition_date': '2026-10-18',
            'hash_algorithm': 'sha256', 'scope': 'Every packaged file except this manifest itself.',
            'files': files}
(ROOT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
all_files = sorted([r['path'] for r in files] + ['MANIFEST.json'])
OUT.mkdir(exist_ok=True)
with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6,
                     allowZip64=True) as archive:
    for relative in all_files:
        path = ROOT / relative
        info = zipfile.ZipInfo(relative, date_time=(2026, 10, 18, 0, 0, 0))
        info.create_system = 3
        mode = 0o755 if os.access(path, os.X_OK) else 0o644
        info.external_attr = (stat.S_IFREG | mode) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, path.read_bytes())

EXTRACT.mkdir()
with zipfile.ZipFile(ZIP) as archive:
    assert archive.namelist() == all_files
    for info in archive.infolist():
        relative = PurePosixPath(info.filename)
        assert not relative.is_absolute() and '..' not in relative.parts
        assert not stat.S_ISLNK(info.external_attr >> 16)
        destination = EXTRACT.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as source, destination.open('wb') as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)

print(json.dumps({'status': 'created_for_independent_final_verification',
                  'zip': str(ZIP), 'bytes': ZIP.stat().st_size, 'sha256': sha(ZIP),
                  'manifest_entries': len(files), 'zip_members': len(all_files),
                  'extraction': str(EXTRACT)}, indent=2))

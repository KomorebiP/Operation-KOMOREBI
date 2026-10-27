#!/usr/bin/env python3
"""Seal a fully assembled Paper VIII edition, then verify the archive bytes."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

W = Path(__file__).resolve().parent
R = W.parent / 'output' / 'Komorebi_Paper_VIII_Final_Edition_2026-10-06'
Z = R.parent / 'Komorebi_Paper_VIII_Final_Traditional_Visual_Lean_2026-10-06.zip'

def sha(data):
    return hashlib.sha256(data).hexdigest()

payload = sorted(p for p in R.rglob('*') if p.is_file()
                 and p != R / 'MANIFEST_SHA256.json')
assert not any(p.is_symlink() for p in R.rglob('*')), 'Symlinks are not packaged'
files = [dict(path=str(p.relative_to(R)), bytes=p.stat().st_size,
              sha256=sha(p.read_bytes())) for p in payload]
manifest = dict(schema='komorebi.paper_viii.file_manifest.v1',
                scope='All payload files except this manifest itself; consistency, not an authenticity signature.',
                files=files)
(R/'MANIFEST_SHA256.json').write_text(json.dumps(manifest, indent=2)+'\n')
subprocess.run([sys.executable, str(R/'scripts/verify_integrity.py')], check=True)
handle = tempfile.NamedTemporaryFile(prefix='paper_viii_sealing_', suffix='.zip',
                                    dir=Z.parent, delete=False)
temporary_archive = Path(handle.name)
handle.close()
with zipfile.ZipFile(temporary_archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for p in sorted(p for p in R.rglob('*') if p.is_file()):
        relative = str(p.relative_to(R.parent))
        info = zipfile.ZipInfo(relative, date_time=(2026, 10, 6, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
with temporary_archive.open('rb') as completed:
    os.fsync(completed.fileno())
with zipfile.ZipFile(temporary_archive) as archive:
    assert archive.testzip() is None, 'CRC failure'
    expected = {str(p.relative_to(R.parent)):p for p in R.rglob('*') if p.is_file()}
    names = archive.namelist()
    assert len(names) == len(set(names)) == len(expected), 'Duplicate or missing ZIP entry'
    assert len(names) == len(files) + 1, 'Only the outer manifest may be excluded from its index'
    assert set(names) == set(expected), 'ZIP file set differs'
    for name, p in expected.items():
        assert archive.read(name) == p.read_bytes(), f'ZIP bytes differ: {name}'
os.replace(temporary_archive, Z)
directory_fd = os.open(Z.parent, os.O_RDONLY | os.O_DIRECTORY)
try:
    os.fsync(directory_fd)
finally:
    os.close(directory_fd)
report = dict(status='PASS', archive=str(Z), archive_bytes=Z.stat().st_size,
              archive_sha256=sha(Z.read_bytes()), manifest_payload_files=len(files),
              zip_files=len(names), crc_verified=True, every_zip_file_byte_compared=True)
(W/'ARCHIVE_VALIDATION.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))

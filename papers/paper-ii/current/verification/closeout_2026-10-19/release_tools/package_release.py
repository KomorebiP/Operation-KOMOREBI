#!/usr/bin/env python3
"""Create and independently verify the completed Paper II handoff archives."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
root = args.root.resolve()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, data):
    p.write_text(json.dumps(data, indent=2) + '\n')

status = json.loads((root / 'RELEASE_STATUS.json').read_text())
assert status['state'] == 'TECHNICALLY_READY_FOR_RELEASE'
assert status['formal']['accepted_complete_scopes'] == 53
assert status['formal']['partial_scopes'] == 0
for key in ['verification', 'correspondence']:
    item = status['formal'][key]
    assert sha(root / item['path']) == item['sha256']
for item in status['publication']['documents']:
    assert sha(root / item['path']) == item['sha256']
for file in root.rglob('*'):
    assert not file.is_symlink(), 'Package must not contain symlinks: ' + str(file)

files = sorted(p for p in root.rglob('*') if p.is_file() and p.name != 'MANIFEST_SHA256.json')
# Retained historical manifests are ordinary evidence and remain covered.
files = sorted(p for p in root.rglob('*') if p.is_file() and p != root / 'MANIFEST_SHA256.json')
assert not any('__pycache__' in p.parts or p.suffix == '.pyc' for p in files)
manifest = {'schema': 'komorebi.sha256_manifest.v1', 'edition_date': '2026-10-19',
            'notice': 'The root manifest excludes only itself. Retained historical manifests and failure receipts are covered.',
            'file_count': len(files),
            'files': [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size,
                       'sha256': sha(p)} for p in files]}
write(root / 'MANIFEST_SHA256.json', manifest)
prefix = 'Komorebi_Paper_II_Release_2026-10-19'
archive = out / 'Komorebi_Paper_II_Reviewed_Release_2026-10-19.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for file in sorted(p for p in root.rglob('*') if p.is_file()):
        z.write(file, prefix + '/' + str(file.relative_to(root)))

def verify_zip(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'Duplicate ZIP names'
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert z.testzip() is None, 'ZIP CRC failure'
        m = json.loads(z.read(prefix + '/MANIFEST_SHA256.json'))
        expected = {prefix + '/' + r['path'] for r in m['files']}
        assert set(names) == expected | {prefix + '/MANIFEST_SHA256.json'}
        for item in m['files']:
            data = z.read(prefix + '/' + item['path'])
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
        return {'entries': len(names), 'manifest_files_checked': len(m['files']),
                'crc': 'PASS', 'exact_inventory': 'PASS', 'all_sha256': 'PASS'}

result = verify_zip(archive)
for item in status['publication']['documents']:
    shutil.copy2(root / item['path'], out / Path(item['path']).name)
for name in ['READ_FIRST.txt', 'RELEASE_STATUS.json', 'CLOSEOUT_LEDGER.json', 'CONTINUE_HERE.txt']:
    shutil.copy2(root / name, out / name)
checksums = out / 'Paper_II_Release_SHA256.txt'
checksums.write_text(sha(archive) + '  ' + archive.name + '\n')
latest = out / 'Paper_II_Latest_2026-10-19.zip'
with zipfile.ZipFile(latest, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for file in [archive, out / 'READ_FIRST.txt', out / 'RELEASE_STATUS.json', checksums]:
        z.write(file, file.name)
with zipfile.ZipFile(latest) as z:
    assert z.testzip() is None
    assert hashlib.sha256(z.read(archive.name)).hexdigest() == sha(archive)
record = {'schema': 'komorebi.paper-ii.archive-verification/1',
          'verified_utc': datetime.now(timezone.utc).isoformat(),
          'full_archive': {'file': archive.name, 'bytes': archive.stat().st_size,
                           'sha256': sha(archive), **result},
          'latest_wrapper': {'file': latest.name, 'bytes': latest.stat().st_size,
                             'sha256': sha(latest), 'inner_archive_identity': 'PASS', 'crc': 'PASS'},
          'status': 'PASS',
          'boundary': 'Archive verification checks bytes, CRC, exact inventory and hashes. It does not rerun Lean or substitute for the formal/publication receipts inside.'}
write(out / 'PAPER_II_ARCHIVE_VERIFICATION.json', record)
print(json.dumps(record, indent=2))

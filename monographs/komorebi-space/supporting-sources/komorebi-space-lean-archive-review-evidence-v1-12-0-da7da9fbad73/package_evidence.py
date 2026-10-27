#!/usr/bin/env python3
"""Package only this frozen external evidence directory; verify every ZIP byte."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import zipfile

HERE = Path(__file__).resolve().parent


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory():
    result = {}
    for folder, dirs, files in os.walk(HERE):
        base = Path(folder)
        dirs[:] = sorted(d for d in dirs if d != '__pycache__')
        assert all(not (base / d).is_symlink() for d in dirs)
        for name in sorted(files):
            if name.endswith('.pyc'):
                continue
            path = base / name
            assert stat.S_ISREG(path.lstat().st_mode)
            relative = path.relative_to(HERE).as_posix()
            assert all(part not in ('', '.', '..') for part in relative.split('/'))
            result[relative] = sha(path)
    return dict(sorted(result.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    metadata = args.metadata.resolve()
    assert not metadata.is_relative_to(HERE) and not metadata.exists()
    # The versioned directory name contains dots; append, do not replace, suffix.
    archive = HERE.parent / (HERE.name + '.zip')
    assert not archive.exists()
    payload = inventory()
    assert 'SHA256SUMS.txt' not in payload
    assert payload['attempt_001_FAIL.json'] == '7d98d318942c90d2557c642ca72fe8c3253222476a8402cd641743f83ded0991'
    assert payload['attempt_002_PASS.json'] == '3208255df76431024a1c8184c308b06683fc349b28b90f6b7fdb68c537479e1f'
    manifest = ''.join(value + '  ' + name + '\n' for name, value in payload.items())
    with (HERE / 'SHA256SUMS.txt').open('x') as stream:
        stream.write(manifest)
    before = inventory()
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in before:
            z.write(HERE / name, HERE.name + '/' + name)
    actual = {}
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for entry in z.infolist():
            assert not entry.is_dir() and entry.filename.startswith(HERE.name + '/')
            relative = entry.filename[len(HERE.name) + 1:]
            assert relative not in actual and not stat.S_ISLNK(entry.external_attr >> 16)
            actual[relative] = hashlib.sha256(z.read(entry)).hexdigest()
        assert z.read(HERE.name + '/SHA256SUMS.txt').decode() == manifest
    assert actual == before == inventory()
    result = {'status': 'PASS', 'archive': str(archive), 'archive_sha256': sha(archive),
              'archive_bytes': archive.stat().st_size, 'payload_files': len(payload),
              'total_files_with_manifest': len(actual), 'zip_crc': 'PASS',
              'all_payload_sha256': 'PASS', 'expanded_directory_equality': True,
              'manifest_sha256': before['SHA256SUMS.txt'],
              'original_failure_report_sha256': payload['attempt_001_FAIL.json'],
              'final_independent_report_sha256': payload['attempt_002_PASS.json'],
              'scope': 'Supplemental external archive-review evidence only; no main release or project modifications.'}
    with metadata.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

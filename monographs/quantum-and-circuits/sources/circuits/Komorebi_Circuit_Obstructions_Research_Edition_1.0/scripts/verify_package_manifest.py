"""Verify this publication's extracted content or ZIP against its manifest.

This checks content consistency, not authorship, mathematical correctness,
or a Lean kernel certificate.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'PUBLICATION_MANIFEST.json', 'PUBLICATION_MANIFEST.sha256'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(read, names):
    data = read('PUBLICATION_MANIFEST.json')
    manifest = json.loads(data)
    seal = read('PUBLICATION_MANIFEST.sha256').decode().strip().split()
    if seal != [sha(data), 'PUBLICATION_MANIFEST.json']:
        raise ValueError('Manifest digest mismatch')
    entries = manifest['files']
    paths = [entry['path'] for entry in entries]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate manifest path')
    if set(names) != set(paths) | EXCLUDED:
        raise ValueError('Content inventory differs from the manifest')
    for entry in entries:
        path = PurePosixPath(entry['path'])
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Unsafe manifest path')
        data = read(entry['path'])
        if len(data) != entry['bytes'] or sha(data) != entry['sha256']:
            raise ValueError('Content mismatch: ' + entry['path'])
    return {'status': 'PASS', 'verified_files': len(entries),
            'meaning': 'Content consistency; no authorship or proof claim'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--zip', type=Path)
    group.add_argument('--directory', type=Path, default=ROOT)
    args = parser.parse_args()
    if args.zip:
        with zipfile.ZipFile(args.zip) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate ZIP member')
            roots = {name.split('/')[0] for name in names}
            if len(roots) != 1:
                raise ValueError('Expected one publication root')
            prefix = roots.pop() + '/'
            if archive.testzip() is not None:
                raise ValueError('ZIP CRC failure')
            result = check(lambda p: archive.read(prefix + p),
                           [p[len(prefix):] for p in names])
            result['zip_crc'] = 'PASS'
    else:
        directory = args.directory.resolve()
        result = check(lambda p: (directory / p).read_bytes(),
                       [p.relative_to(directory).as_posix()
                        for p in directory.rglob('*') if p.is_file()])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

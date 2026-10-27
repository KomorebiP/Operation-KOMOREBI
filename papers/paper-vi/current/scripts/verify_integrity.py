#!/usr/bin/env python3
"""Check exact package membership, sizes and SHA-256 hashes; strict by default.

The manifest excludes itself. This checks consistency with the supplied
manifest, not provenance, mathematical correctness or fresh Lean acceptance.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
MANIFEST = 'MANIFEST_SHA256.json'
SCHEMA = 'komorebi.strict_manifest.v1'
META_FIELDS = {'schema', 'checkpoint', 'scope', 'edition', 'generated_at_utc', 'files'}


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + repr(key))
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('non-finite JSON number: ' + value)


def safe_path(value):
    if not isinstance(value, str) or not value:
        return False
    if '\\' in value or ':' in value or any(ord(c) < 32 or ord(c) == 127 for c in value):
        return False
    path = PurePosixPath(value)
    return (not path.is_absolute() and path.as_posix() == value
            and all(part not in ('', '.', '..') for part in value.split('/')))


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_tree(root):
    root = Path(root).absolute()
    failures = []
    report = {'status': 'FAIL', 'schema': SCHEMA, 'strict': True,
              'files_checked': 0, 'files_expected': 0, 'failures': failures,
              'scope': 'Exact regular-file membership, sizes and SHA-256 consistency with the supplied manifest. Not provenance, proof review or Lean execution.'}

    def fail(problem, path=None):
        item = {'problem': problem}
        if path is not None:
            item['path'] = path
        failures.append(item)

    try:
        mode = root.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            fail('package root must be a real directory')
            return report
        manifest_path = root / MANIFEST
        if not stat.S_ISREG(manifest_path.lstat().st_mode):
            fail('manifest must be a regular file, not a symlink or special file', MANIFEST)
            return report
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'),
                              object_pairs_hook=no_duplicate_keys,
                              parse_constant=reject_constant)
    except (OSError, ValueError, UnicodeError) as error:
        fail('cannot read valid manifest: ' + str(error), MANIFEST)
        return report
    if not isinstance(manifest, dict):
        fail('manifest must be a JSON object')
        return report
    if manifest.get('schema') != SCHEMA:
        fail('unrecognized manifest schema')
    if set(manifest) - META_FIELDS:
        fail('unknown manifest fields: ' + ', '.join(sorted(set(manifest) - META_FIELDS)))
    for name in ('checkpoint', 'scope', 'edition', 'generated_at_utc'):
        if name in manifest and not isinstance(manifest[name], str):
            fail('metadata must be text: ' + name)
    rows = manifest.get('files')
    if not isinstance(rows, list) or not rows:
        fail('files must be a nonempty array')
        return report
    expected = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {'path', 'bytes', 'sha256'}:
            fail('manifest row must contain exactly path, bytes, sha256: row ' + str(index))
            continue
        name = row['path']
        if not safe_path(name):
            fail('unsafe or noncanonical manifest path: row ' + str(index))
            continue
        if name == MANIFEST:
            fail('manifest must exclude itself', name)
        if name in expected:
            fail('duplicate manifest path', name)
        expected[name] = row
        if type(row['bytes']) is not int or row['bytes'] < 0:
            fail('bytes must be a nonnegative integer', name)
        if not isinstance(row['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', row['sha256']):
            fail('sha256 must be exactly 64 lowercase hexadecimal characters', name)
    report['files_expected'] = len(expected)
    if failures:
        return report
    actual = set()

    def walk_error(error):
        fail('cannot enumerate package: ' + str(error))

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        for name in list(dirs) + files:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            try:
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode):
                    fail('symlink is forbidden', relative)
                    if name in dirs:
                        dirs.remove(name)
                elif stat.S_ISREG(mode):
                    if not safe_path(relative):
                        fail('unsafe or noncanonical payload path', relative)
                    actual.add(relative)
                elif not stat.S_ISDIR(mode):
                    fail('special file is forbidden', relative)
            except OSError as error:
                fail('cannot inspect payload: ' + str(error), relative)
    actual.discard(MANIFEST)
    for name in sorted(set(expected) - actual):
        fail('missing regular file', name)
    for name in sorted(actual - set(expected)):
        fail('unexpected file', name)
    for name in sorted(set(expected) & actual):
        row, path = expected[name], root / name
        try:
            if not stat.S_ISREG(path.lstat().st_mode):
                fail('payload is no longer a regular file', name)
                continue
            size, checksum = path.stat().st_size, digest_file(path)
            report['files_checked'] += 1
            if size != row['bytes']:
                fail('byte size differs', name)
            if checksum != row['sha256']:
                fail('SHA-256 differs', name)
        except OSError as error:
            fail('cannot read payload: ' + str(error), name)
    report['status'] = 'FAIL' if failures else 'PASS'
    return report


def write_report(destination, report):
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + destination.name + '.', dir=destination.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='Explicitly request the default exact-membership check.')
    parser.add_argument('--report', type=Path, help='Write JSON to a path outside the checked package.')
    args = parser.parse_args(argv)
    root = Path(os.path.abspath(__file__)).parent.parent
    destination = args.report.expanduser().resolve() if args.report else None
    if destination is not None and destination.is_relative_to(root.resolve()):
        parser.error('--report must be outside the checked package')
    report = verify_tree(root)
    if destination is not None:
        try:
            write_report(destination, report)
        except OSError as error:
            report['status'] = 'FAIL'
            report['failures'].append({'problem': 'cannot write external report: ' + str(error)})
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

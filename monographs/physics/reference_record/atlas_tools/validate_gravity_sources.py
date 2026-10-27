#!/usr/bin/env python3
"""Validate portable archive/member identities in gravity source maps.

This checks source preservation and correspondence, not mathematical truth.
Run after the gravity maps have been generated. It does not execute Lean.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def walk(value):
    if isinstance(value, dict):
        member = value.get('member', value.get('archive_member'))
        if isinstance(value.get('archive'), str) and isinstance(member, str):
            yield dict(value, member=member)
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main():
    maps = sorted((ROOT / 'editorial' / 'gravity').glob('*source_map.json'))
    if not maps:
        raise FileNotFoundError('No gravity source maps found')
    archives = {}
    records = []
    identities = {}
    try:
        for source_map in maps:
            for pointer in walk(json.loads(source_map.read_text())):
                archive, member = pointer['archive'], pointer['member']
                if archive not in archives:
                    path = ROOT / archive
                    archives[archive] = (zipfile.ZipFile(path), digest(path.read_bytes()))
                zfile, archive_hash = archives[archive]
                content = zfile.read(member)
                member_hash = digest(content)
                if pointer.get('archive_sha256') and archive_hash != pointer['archive_sha256']:
                    raise ValueError('Archive hash mismatch: ' + archive)
                if pointer.get('sha256') and member_hash != pointer['sha256']:
                    raise ValueError('Member hash mismatch: ' + archive + '::' + member)
                if pointer.get('bytes') is not None and len(content) != pointer['bytes']:
                    raise ValueError('Member size mismatch: ' + archive + '::' + member)
                key = (archive, member)
                if key in identities and identities[key] != member_hash:
                    raise ValueError('Conflicting source identity: ' + repr(key))
                identities[key] = member_hash
                records.append({'map': str(source_map.relative_to(ROOT)), 'archive': archive,
                                'member': member, 'sha256': member_hash, 'bytes': len(content)})
    finally:
        for zfile, _ in archives.values():
            zfile.close()
    result = {'schema': 'physics.gravity.portable-source-validation.v1', 'status': 'PASS',
              'maps': [str(p.relative_to(ROOT)) for p in maps],
              'pointer_records_checked': len(records), 'unique_members_checked': len(identities),
              'archives_checked': len(archives), 'fresh_lean_compilation': False,
              'scope': 'Exact archived byte identities only; no proof or physical validation.',
              'records': records}
    output = ROOT / 'editorial' / 'gravity' / 'portable_source_validation.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'records'}, indent=2))


if __name__ == '__main__':
    main()

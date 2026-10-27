#!/usr/bin/env python3
"""Verify or restore deduplicated extracted ZIP member content. Never runs payloads."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import shutil

BASE = pathlib.Path(__file__).resolve().parent

def safe_relative(value):
    path = pathlib.PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value:
        raise ValueError(f'Unsafe relative path: {value!r}')
    return pathlib.Path(*path.parts)

def file_hash(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()

def destination_path(row):
    pieces = [row['root_archive']]
    for container in row['archive_chain'][1:]:
        pieces.append(container['member_path'] + '.contents')
    pieces.append(row['member_path'])
    return safe_relative('/'.join(pieces))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Hash-check all retained payloads and mapping references.')
    parser.add_argument('--list', action='store_true', help='List original top-level archive keys.')
    parser.add_argument('--output', type=pathlib.Path, help='New or empty directory for restored extracted content.')
    parser.add_argument('--root', action='append', help='Restore only the named original archive key; repeat for several.')
    args = parser.parse_args()
    data = json.loads((BASE / 'ARCHIVE_MAP.json').read_text())
    known = {r['key']: r for r in data['root_archives']}
    selected = set(args.root or known)
    if not selected <= known.keys():
        raise ValueError(f'Unknown archive keys: {sorted(selected - known.keys())}')
    if args.list:
        for key, entry in known.items():
            print(f"{key}: {entry['filename']}")
    payloads = {r['sha256']: r for r in data['payloads']}
    paths = set()
    for row in data['payloads']:
        relative = safe_relative(row['payload_path'])
        if relative in paths:
            raise ValueError(f'Two hashes share one payload path: {relative}')
        paths.add(relative)
        if args.verify or args.output:
            path = BASE / relative
            if path.stat().st_size != row['bytes'] or file_hash(path) != row['sha256']:
                raise ValueError(f'Payload integrity failure: {relative}')
    for row in data['leaf_occurrences']:
        target = payloads[row['sha256']]
        if row['payload_path'] != target['payload_path'] or row['bytes'] != target['bytes']:
            raise ValueError(f'Mapping integrity failure: {row["member_path"]}')
        destination_path(row)
    if args.verify or args.output:
        print(f"Verified {len(payloads)} unique payloads and {len(data['leaf_occurrences'])} leaf occurrences.")
    if args.output:
        out = args.output.resolve()
        if out == BASE or BASE in out.parents:
            raise ValueError('Restore outside this preservation directory.')
        if out.exists() and any(out.iterdir()):
            raise ValueError('Output must be new or empty; existing content will not be overwritten.')
        out.mkdir(parents=True, exist_ok=True)
        restored = {}
        count = 0
        for row in data['leaf_occurrences']:
            if row['root_archive'] not in selected:
                continue
            relative = destination_path(row)
            if relative in restored:
                if restored[relative] == row['sha256']:
                    continue
                relative = relative.with_name(relative.name + f'.archive_entry_{row["member_index"]:06d}')
                if relative in restored:
                    raise ValueError(f'Duplicate ZIP-member collision: {relative}')
            path = out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BASE / safe_relative(row['payload_path']), path)
            restored[relative] = row['sha256']
            count += 1
        # Preserve empty directory entries independently of file content.
        containers = {r['sha256']: r for r in data['containers']}
        for occ in data['container_occurrences']:
            if occ['root_archive'] not in selected:
                continue
            prefix = [occ['root_archive']]
            for container in occ['archive_chain'][1:]:
                prefix.append(container['member_path'] + '.contents')
            for directory in containers[occ['container_sha256']]['directory_members']:
                (out / safe_relative('/'.join(prefix + [directory]))).mkdir(parents=True, exist_ok=True)
        (out / 'RESTORATION.json').write_text(json.dumps({'format': data['format'], 'root_archives': sorted(selected), 'restored_files': count, 'boundary': 'Nonarchive extracted bytes restored. Nested ZIPs are directories ending in .contents. Original ZIP byte streams are not reconstructed.'}, indent=2) + '\n')
        print(f'Restored {count} files to {out}. Original ZIP containers were not reconstructed.')
    if not (args.list or args.verify or args.output):
        parser.print_help()

if __name__ == '__main__':
    main()

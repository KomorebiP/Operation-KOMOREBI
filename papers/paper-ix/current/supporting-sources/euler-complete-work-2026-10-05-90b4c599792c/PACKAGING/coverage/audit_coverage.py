#!/usr/bin/env python3
"""Read-only, content-hash coverage audit of Euler packaging inputs."""
from pathlib import Path, PurePosixPath
from collections import Counter
import argparse, hashlib, io, json, zipfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
SOURCE_DIRS = (
    'Euler_Address_One_Continuation_2026-10-05',
    'Euler_Regular_Address_and_Critical_Phases_2026-10-05',
    'audit_helpers', 'carry_audit', 'independent_review', 'inputs',
    'local_parameter', 'next', 'recovered', 'sources', 'transversality',
)
SOURCE_FILES = (
    'Euler_Address_One_Continuation_2026-10-05.zip',
    'Euler_Regular_Address_and_Critical_Phases_2026-10-05.zip',
)
PRIVATE_COMPONENTS = {'library_helpers', 'library_helpers_current', '__pycache__'}

def excluded(name):
    parts = PurePosixPath(name).parts
    return (any(x.startswith('.') or x in PRIVATE_COMPONENTS for x in parts)
            or name.endswith(('.pyc', '.pyo'))
            or any(x.endswith('_LIBRARY_RESULT.json') for x in parts))

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def local_sources():
    out = []
    for prefix in SOURCE_DIRS:
        p = ROOT / prefix
        if p.exists():
            out.extend(q for q in p.rglob('*') if q.is_file()
                       and not excluded(q.relative_to(ROOT).as_posix()))
    out.extend(ROOT / p for p in SOURCE_FILES if (ROOT / p).is_file())
    return sorted(set(out))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkpoint')
    args = parser.parse_args()
    checkpoint = Path(args.checkpoint).resolve()
    archive_catalog = {}
    latest_objects = {}
    excluded_members = []
    unsafe_names = []
    errors = []

    def add_object(h, size, location, destination):
        rec = destination.setdefault(h, {'bytes': size, 'locations': []})
        if location not in rec['locations']:
            rec['locations'].append(location)

    def walk_zip(blob, location, destination, ancestors=()):
        h = digest(blob)
        add_object(h, len(blob), location, destination)
        existing = archive_catalog.get(h)
        if existing:
            if location not in existing['locations']:
                existing['locations'].append(location)
            for child_hash, child in existing['objects'].items():
                add_object(child_hash, child['bytes'], child['location'], destination)
            return h
        rec = {'sha256': h, 'bytes': len(blob), 'locations': [location],
               'member_count': 0, 'uncompressed_bytes': 0, 'zip_children': [],
               'objects': {}}
        archive_catalog[h] = rec
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                bad = z.testzip()
                if bad:
                    errors.append({'location': location, 'bad_crc_member': bad})
                for member in z.infolist():
                    if member.is_dir():
                        continue
                    rec['member_count'] += 1
                    rec['uncompressed_bytes'] += member.file_size
                    name = member.filename
                    loc = location + '!/' + name
                    if name.startswith('/') or '..' in PurePosixPath(name).parts:
                        unsafe_names.append(loc)
                    if excluded(name):
                        excluded_members.append({'location': loc,
                                                 'bytes': member.file_size})
                        continue
                    data = z.read(member)
                    mh = digest(data)
                    add_object(mh, len(data), loc, destination)
                    rec['objects'][mh] = {'bytes': len(data), 'location': loc}
                    if name.lower().endswith('.zip'):
                        if mh in ancestors:
                            errors.append({'location': loc, 'recursive_cycle': mh})
                            continue
                        before = set(destination)
                        child = walk_zip(data, loc, destination, ancestors + (h,))
                        rec['zip_children'].append(child)
                        for ch in set(destination) - before:
                            d = destination[ch]
                            rec['objects'][ch] = {'bytes': d['bytes'],
                                                  'location': d['locations'][0]}
        except Exception as exc:
            errors.append({'location': location, 'error': repr(exc)})
        return h

    expected = '19878d2553a5a5cbada8791e7751b37fdbe73422b6c0da9893a9d9e178c49c96'
    blob = checkpoint.read_bytes()
    actual = digest(blob)
    if actual != expected:
        raise SystemExit(f'Unexpected checkpoint hash: {actual}')
    walk_zip(blob, checkpoint.relative_to(ROOT).as_posix(), latest_objects)
    latest_archive_hashes = set(archive_catalog)
    records = []
    outside = {}
    local_archive_hashes = set()
    all_objects = {h: {'bytes': r['bytes'], 'locations': list(r['locations'])}
                   for h, r in latest_objects.items()}
    for p in local_sources():
        name = p.relative_to(ROOT).as_posix()
        data = p.read_bytes()
        h = digest(data)
        is_archive = p.suffix.lower() == '.zip'
        status = 'covered_by_latest_recursive_closure' if h in latest_objects else 'outside_latest'
        records.append({'path': name, 'bytes': len(data), 'sha256': h,
                        'kind': 'archive' if is_archive else 'file', 'status': status})
        if h not in latest_objects:
            add_object(h, len(data), name, outside)
        add_object(h, len(data), name, all_objects)
        if is_archive:
            local_archive_hashes.add(h)
            walk_zip(data, name, all_objects)
    outside_unique = [{'sha256': h, **r} for h, r in sorted(outside.items())]
    total_by_prefix = {}
    for prefix in SOURCE_DIRS + SOURCE_FILES:
        rows = [r for r in records if r['path'] == prefix or r['path'].startswith(prefix + '/')]
        missing = [r for r in rows if r['status'] == 'outside_latest']
        total_by_prefix[prefix] = {'files': len(rows), 'bytes': sum(r['bytes'] for r in rows),
                                  'outside_files': len(missing),
                                  'outside_bytes': sum(r['bytes'] for r in missing)}
    serial_catalog = [{k: v for k, v in r.items() if k != 'objects'}
                      for h, r in sorted(archive_catalog.items())]
    summary = {
        'scope': 'Local visible Euler project sources and exact latest checkpoint recursively. No Library-wide assertion.',
        'checkpoint': str(checkpoint.relative_to(ROOT)),
        'checkpoint_sha256': actual,
        'checkpoint_bytes': len(blob),
        'latest_unique_archives': len(latest_archive_hashes),
        'latest_unique_content_objects': len(latest_objects),
        'local_files': len(records),
        'local_bytes': sum(r['bytes'] for r in records),
        'outside_latest_files': sum(r['status'] == 'outside_latest' for r in records),
        'outside_latest_unique_objects': len(outside),
        'outside_latest_unique_bytes': sum(r['bytes'] for r in outside.values()),
        'all_unique_archives': len(archive_catalog),
        'all_unique_archive_bytes': sum(r['bytes'] for r in archive_catalog.values()),
        'outside_latest_unique_archives': sorted(set(archive_catalog) - latest_archive_hashes),
        'outside_latest_local_archive_hashes': sorted(local_archive_hashes - latest_archive_hashes),
        'all_unique_objects': len(all_objects),
        'all_unique_object_bytes': sum(r['bytes'] for r in all_objects.values()),
        'extensions': dict(sorted(Counter(Path(r['path']).suffix.lower() or '[none]' for r in records).items())),
        'by_prefix': total_by_prefix,
        'excluded_members': excluded_members,
        'unsafe_names': unsafe_names,
        'errors': errors,
        'minimal_extra_inclusion': [{'source': r['locations'][0], 'sha256': r['sha256'],
                                     'bytes': r['bytes'], 'aliases': r['locations'][1:]}
                                    for r in outside_unique],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, data in [('coverage_summary.json', summary), ('local_inventory.json', records),
                       ('archive_catalog.json', serial_catalog),
                       ('latest_content_catalog.json', latest_objects)]:
        (OUTPUT / name).write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in (
        'checkpoint_bytes', 'latest_unique_archives', 'latest_unique_content_objects',
        'local_files', 'outside_latest_files', 'outside_latest_unique_objects',
        'outside_latest_unique_bytes', 'all_unique_archives', 'all_unique_archive_bytes',
        'outside_latest_unique_archives', 'unsafe_names', 'errors')}, indent=2))

if __name__ == '__main__':
    main()

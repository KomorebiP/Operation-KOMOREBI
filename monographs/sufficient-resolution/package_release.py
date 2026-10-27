#!/usr/bin/env python3
"""Create a source ZIP with an independently verified payload index."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
ZIP = ROOT.with_suffix('.zip')
INDEX = 'BUNDLE_INDEX.json'
SUMS = 'SHA256SUMS.txt'
TRANSIENT_DIRS = {'__pycache__', 'qa', 'previews', 'rendered', '.git', '.lake'}
TEX_TRANSIENT = {'.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk', '.synctex.gz'}

def payload_files():
    result = []
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if p.name in {INDEX, SUMS} or any(part in TRANSIENT_DIRS for part in rel.parts):
            continue
        if p.suffix == '.pyc':
            continue
        if rel.parts[0] in {'traditional', 'visual', 'lean'}:
            if p.suffix in TEX_TRANSIENT or p.name.endswith('.synctex.gz'):
                continue
        result.append(p)
    return result

def main():
    files = payload_files()
    entries = [
        {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
         'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in files
    ]
    (ROOT / INDEX).write_text(json.dumps({
        'edition': ROOT.name,
        'payload_count': len(entries),
        'self_indexed_files_excluded': [INDEX, SUMS],
        'files': entries,
    }, indent=2) + '\n', encoding='utf-8')
    (ROOT / SUMS).write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in entries), encoding='utf-8')
    archive_files = files + [ROOT / INDEX, ROOT / SUMS]
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in archive_files:
            info = zipfile.ZipInfo(ROOT.name + '/' + p.relative_to(ROOT).as_posix(), (2026, 10, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = 0o100755 if p.suffix == '.sh' else 0o100644
            info.external_attr = mode << 16
            z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    with zipfile.ZipFile(ZIP) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f'ZIP CRC failure: {bad}')
        for entry in entries:
            data = z.read(ROOT.name + '/' + entry['path'])
            if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise RuntimeError(f"ZIP payload mismatch: {entry['path']}")
    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    ZIP.with_suffix('.zip.sha256').write_text(f'{digest}  {ZIP.name}\n', encoding='utf-8')
    print(json.dumps({'zip': str(ZIP), 'bytes': ZIP.stat().st_size,
                      'sha256': digest, 'members': len(archive_files),
                      'payload_hashes_verified': len(entries)}))

if __name__ == '__main__':
    main()

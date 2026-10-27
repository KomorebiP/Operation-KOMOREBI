#!/usr/bin/env python3
"""Create the Signal source ZIP and verify its CRC and every indexed payload."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
ZIP = ROOT.with_suffix('.zip')
INDEX = 'BUNDLE_INDEX.json'
SUMS = 'SHA256SUMS.txt'
TRANSIENT_DIRS = {'__pycache__', 'qa', 'previews', 'rendered', '.git', '.lake'}
TEX_TRANSIENT = {'.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk'}

def payload_files():
    files = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.as_posix() in {INDEX, SUMS}:
            continue
        protected = rel.parts[0] in {'sources', 'related_formal'}
        if not protected and any(p in TRANSIENT_DIRS for p in rel.parts):
            continue
        if path.suffix == '.pyc' or '.openai-download-' in path.name:
            continue
        if rel.parts[0] in {'traditional', 'visual', 'lean'} and (
            path.suffix in TEX_TRANSIENT or path.name.endswith('.synctex.gz')
        ):
            continue
        files.append(path)
    return files

def main():
    files = payload_files()
    entries = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    indexed = {e['path']: e for e in entries}
    preservation = json.loads((ROOT / 'verification/SOURCE_PRESERVATION.json').read_text())
    originals = [f for group in preservation['sources'] for f in group['files']]
    related = json.loads((ROOT / 'provenance/PAPER_V_CHECKED_CHECKPOINT.json').read_text())['copied_payloads']
    for original in originals + related:
        entry = indexed.get(original['release_path'])
        if entry is None or entry['sha256'] != original['sha256'] or entry['bytes'] != original['bytes']:
            raise RuntimeError(f"Preserved source omitted or altered: {original['release_path']}")
    (ROOT / INDEX).write_text(json.dumps({
        'edition': ROOT.name, 'payload_count': len(entries),
        'self_indexed_files_excluded': [INDEX, SUMS], 'files': entries,
    }, indent=2) + '\n', encoding='utf-8')
    (ROOT / SUMS).write_text(''.join(f"{e['sha256']}  {e['path']}\n" for e in entries), encoding='utf-8')
    archive_files = files + [ROOT / INDEX, ROOT / SUMS]
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in archive_files:
            info = zipfile.ZipInfo(ROOT.name + '/' + path.relative_to(ROOT).as_posix(),
                                   (2026, 10, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100755 if path.suffix == '.sh' else 0o100644) << 16
            z.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    with zipfile.ZipFile(ZIP) as z:
        if z.testzip() is not None:
            raise RuntimeError('Archive CRC verification failed')
        for e in entries:
            data = z.read(ROOT.name + '/' + e['path'])
            if len(data) != e['bytes'] or hashlib.sha256(data).hexdigest() != e['sha256']:
                raise RuntimeError(f"Payload verification failed: {e['path']}")
    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    ZIP.with_suffix('.zip.sha256').write_text(f'{digest}  {ZIP.name}\n', encoding='utf-8')
    print(json.dumps({'zip': str(ZIP), 'bytes': ZIP.stat().st_size, 'sha256': digest,
                      'members': len(archive_files), 'payload_hashes_verified': len(entries)}))

if __name__ == '__main__':
    main()

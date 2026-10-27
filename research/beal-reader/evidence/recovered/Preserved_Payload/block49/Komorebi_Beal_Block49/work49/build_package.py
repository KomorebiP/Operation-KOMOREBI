#!/usr/bin/env python3
"""Package Block 49 and its frozen ancestry; checksums certify bytes only."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work49'
OUT = ROOT / 'deliverables'
BASE = OUT / 'Komorebi_Beal_Block48_Arithmetic_Refinement_v4.8.0.zip'
BASE_HASH = 'bbf78879d4b5714c818dd1521053dcd6b80c0694799b120b440fa850efec091a'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert sha(BASE.read_bytes()) == BASE_HASH
    files = {}
    with zipfile.ZipFile(BASE) as z:
        for name in z.namelist():
            if name.endswith('/'):
                continue
            rel = name.removeprefix('Komorebi_Beal_Block48/')
            if rel not in {'README.md', 'PACKAGE_SHA256SUMS.txt'}:
                files[rel] = z.read(name)
    for p in sorted(WORK.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or any(s.endswith('_ocr') for s in p.parts):
            continue
        if p.suffix in {'.pyc', '.olean', '.pdf', '.png'}:
            continue
        # Preserve source locators/hashes, not full third-party paper text.
        if 'source_records' in p.parts and p.suffix == '.txt':
            continue
        if p.name == 'alt_x021_rational_j.html':
            continue
        files[str(p.relative_to(ROOT))] = p.read_bytes()
    files['predecessor/' + BASE.name] = BASE.read_bytes()
    files['README.md'] = (
        '# Komorebi Beal research checkpoint 49\n\n'
        'Start with work49/REPORT.md and work49/CONTINUE_HERE.md.\n'
        'Neither Beal nor the full (3,5,7) signature is proved here.\n'
        'Earlier work is preserved from the exact frozen Block48 archive.\n'
        'Third-party paper PDFs and full text, and the Lean runtime, are not bundled.\n'
        'Source versions, locators and available hashes are retained.\n'
        'Checksums certify bytes, not mathematical correctness.\n'
    ).encode()
    files['PACKAGE_SHA256SUMS.txt'] = ''.join(
        f'{sha(data)}  {name}\n' for name, data in sorted(files.items())
    ).encode()
    target = OUT / 'Komorebi_Beal_Block49_CM_and_Extensions_v4.9.0.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo('Komorebi_Beal_Block49/' + name, (2026, 9, 19, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name, data in files.items():
            assert z.read('Komorebi_Beal_Block49/' + name) == data
    report = OUT / 'Komorebi_Beal_Block49_Report.md'
    report.write_bytes((WORK / 'REPORT.md').read_bytes())
    checksums = OUT / 'Komorebi_Beal_Block49_SHA256SUMS.txt'
    checksums.write_text(''.join(f'{sha(p.read_bytes())}  {p.name}\n' for p in [target, report]))
    print(json.dumps({'archive': str(target), 'files': len(files),
                      'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes()),
                      'report': str(report), 'checksums': str(checksums)}, indent=2))


if __name__ == '__main__':
    main()

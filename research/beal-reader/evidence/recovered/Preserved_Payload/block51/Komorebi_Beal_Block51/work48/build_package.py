#!/usr/bin/env python3
"""Package Block 48 with exact frozen predecessor bytes; no mathematical claims."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work48'
OUT = ROOT / 'deliverables'
BASE = OUT / 'Komorebi_Beal_Block47_Polyphase_Closure_Attempt_v4.7.0.zip'
BASE_HASH = '6ff3719bb869cd262b42acd25ed4e768da23c4d6fda815440dc3b08135483466'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert sha(BASE.read_bytes()) == BASE_HASH
    files = {}
    for p in sorted(WORK.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.olean', '.pdf', '.png'}:
            files[str(p.relative_to(ROOT))] = p.read_bytes()
    with zipfile.ZipFile(BASE) as z:
        for name in z.namelist():
            if name.endswith('/'):
                continue
            rel = name.removeprefix('Komorebi_Beal_Block47/')
            files['work47/' + rel] = z.read(name)
            if rel.startswith('predecessor/') and rel.endswith('.md'):
                files['work46/' + Path(rel).name] = z.read(name)
    # This independent source audit was not in the earlier minimal predecessor set.
    for rel in ['work46/fixed_field_audit.md']:
        if (ROOT / rel).is_file():
            files[rel] = (ROOT / rel).read_bytes()
    files['predecessor/Komorebi_Beal_Block47_Polyphase_Closure_Attempt_v4.7.0.zip'] = BASE.read_bytes()
    files['README.md'] = (
        '# Komorebi Beal research checkpoint 48\n\n'
        'Start with work48/REPORT.md and work48/CONTINUE_HERE.md.\n'
        'The conjecture and the full (3,5,7) signature remain unresolved here.\n'
        'work47/ is extracted from the exact frozen predecessor archive.\n'
        'work46/ contains the inherited proof inputs needed by this continuation.\n'
        'The Lean runtime is not bundled; its exact version is documented.\n'
        'Checksums certify file bytes, not mathematics.\n'
    ).encode()
    files['PACKAGE_SHA256SUMS.txt'] = ''.join(
        f'{sha(data)}  {name}\n' for name, data in sorted(files.items())
    ).encode()
    target = OUT / 'Komorebi_Beal_Block48_Arithmetic_Refinement_v4.8.0.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo('Komorebi_Beal_Block48/' + name, (2026, 9, 19, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name, data in files.items():
            assert z.read('Komorebi_Beal_Block48/' + name) == data
    report = OUT / 'Komorebi_Beal_Block48_Report.md'
    report.write_bytes((WORK / 'REPORT.md').read_bytes())
    checksum = OUT / 'Komorebi_Beal_Block48_SHA256SUMS.txt'
    checksum.write_text(''.join(f'{sha(p.read_bytes())}  {p.name}\n' for p in [target, report]))
    print(json.dumps({'archive': str(target), 'files': len(files),
                      'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes()),
                      'report': str(report), 'checksums': str(checksum)}, indent=2))


if __name__ == '__main__':
    main()

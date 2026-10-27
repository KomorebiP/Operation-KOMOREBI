#!/usr/bin/env python3
"""Check the delivered manifest and every nested ZIP; standard library only."""
from __future__ import annotations
import argparse, hashlib, io, json, re, sys, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r'(^|/)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|/|$)', re.I)
FONTS = {'.ttf', '.otf', '.ttc', '.woff', '.woff2', '.pfb', '.pfa'}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def safe(name: str) -> bool:
    p = PurePosixPath(name)
    return (not p.is_absolute() and '..' not in p.parts and '\\' not in name
            and not any(c in name for c in '<>:"|?*') and not FORBIDDEN.search(name)
            and all(not part.endswith((' ', '.')) for part in p.parts))

def inspect_zip(source, label: str, errors: list[str], records: list[dict], depth: int = 0) -> None:
    if depth > 8:
        errors.append(f'{label}: nested ZIP depth exceeds 8')
        return
    try:
        with zipfile.ZipFile(source) as z:
            seen = set()
            for info in z.infolist():
                key = info.filename.casefold()
                if not safe(info.filename) or key in seen:
                    errors.append(f'{label}: unsafe or case-colliding member {info.filename}')
                seen.add(key)
                if info.flag_bits & 1:
                    errors.append(f'{label}: encrypted member {info.filename}')
                if info.is_dir():
                    continue
                data = z.read(info)  # Also checks the member CRC.
                if PurePosixPath(info.filename).suffix.lower() in FONTS:
                    errors.append(f'{label}: standalone font file {info.filename}')
                if info.filename.lower().endswith('.zip'):
                    inspect_zip(io.BytesIO(data), label + '!' + info.filename, errors, records, depth + 1)
            records.append({'archive': label, 'entries': len(z.infolist()), 'crc': 'passed'})
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        errors.append(f'{label}: {type(exc).__name__}: {exc}')

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='Reject unexpected payload files.')
    parser.add_argument('--json', type=Path, help='Optional report path outside the package.')
    args = parser.parse_args()
    errors: list[str] = []
    records: list[dict] = []
    try:
        manifest = json.loads((ROOT / 'MANIFEST.json').read_text(encoding='utf-8'))
        expected = {}
        folded = set()
        for row in manifest['files']:
            name = row['path']
            if not safe(name) or name.casefold() in folded:
                errors.append('Invalid manifest path: ' + name)
                continue
            expected[name] = row
            folded.add(name.casefold())
        actual = {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob('*') if p.is_file()}
        for name, row in expected.items():
            p = ROOT / name
            if p.is_symlink() or not p.is_file():
                errors.append('Missing or linked file: ' + name)
            elif p.stat().st_size != row['bytes'] or digest(p) != row['sha256']:
                errors.append('Size/SHA-256 mismatch: ' + name)
            elif p.suffix.lower() == '.zip':
                inspect_zip(p, name, errors, records)
            if p.suffix.lower() in FONTS:
                errors.append('Standalone font file: ' + name)
        extras = sorted(set(actual) - set(expected) - {'MANIFEST.json', 'SHA256SUMS'})
        if args.strict and extras:
            errors.extend('Unexpected file: ' + n for n in extras)
        if manifest['file_count'] != len(expected):
            errors.append('Manifest count mismatch')
        sums = ''.join(f"{expected[n]['sha256']}  {n}\n" for n in sorted(expected))
        if (ROOT / 'SHA256SUMS').read_text(encoding='utf-8') != sums:
            errors.append('SHA256SUMS disagrees with MANIFEST.json')
        report = {'status': 'passed' if not errors else 'failed', 'payload_files': len(expected),
                  'strict': args.strict, 'nested_zip_checks': records, 'extra_files': extras, 'errors': errors}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report = {'status': 'failed', 'errors': [str(exc)]}
    output = json.dumps(report, indent=2)
    print(output)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(output + '\n', encoding='utf-8')
    return 0 if report['status'] == 'passed' else 1

if __name__ == '__main__':
    raise SystemExit(main())

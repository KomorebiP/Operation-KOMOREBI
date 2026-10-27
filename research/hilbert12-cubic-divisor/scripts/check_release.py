#!/usr/bin/env python3
"""Check immutable intake, PDF readability, and manifest integrity of a ZIP."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PDFS = [
    'traditional/H12_Cubic_Divisor_Traditional.pdf',
    'visual/H12_Cubic_Divisor_Visual_Guide.pdf',
    'lean/H12_Cubic_Divisor_Lean_Guide.pdf',
]

def digest(content):
    return hashlib.sha256(content).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    intake = json.loads((ROOT/'provenance/SOURCE_INTAKE_MANIFEST.json').read_text())
    for entry in intake['files']:
        path = ROOT/entry['path']
        if path.stat().st_size != entry['bytes'] or digest(path.read_bytes()) != entry['sha256']:
            raise RuntimeError('Protected source changed: '+entry['path'])
    pdf_records = []
    for relative in PDFS:
        path = ROOT/relative
        info = subprocess.run(['pdfinfo', str(path)], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        fields = {line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                  for line in info.stdout.splitlines() if ':' in line}
        if fields.get('Author') != 'Komorebi P.':
            raise RuntimeError('Unexpected public author metadata: '+relative)
        text = subprocess.run(['pdftotext', str(path), '-'], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        if not text.strip() or b'\xef\xbf\xbd' in text:
            raise RuntimeError('Empty PDF or replacement characters: '+relative)
        if b'??' in text:
            raise RuntimeError('Unresolved cross-reference marker: '+relative)
        pdf_records.append({'path': relative, 'pages': int(fields['Pages']),
                            'bytes': path.stat().st_size, 'sha256': digest(path.read_bytes()),
                            'metadata_and_text': 'PASS'})
    result = {'protected_intake_files': len(intake['files']),
              'protected_intake': 'PASS', 'pdfs': pdf_records,
              'scope': 'Integrity and PDF readability only; native-page visual and mathematical audits are separate.'}
    if args.archive:
        with ZipFile(args.archive) as archive:
            bad = archive.testzip()
            if bad:
                raise RuntimeError('CRC failure: '+bad)
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise RuntimeError('Duplicate archive members')
            prefix = ROOT.name+'/'
            manifest = json.loads(archive.read(prefix+'SOURCE_MANIFEST.json'))
            for entry in manifest['files']:
                content = archive.read(prefix+entry['path'])
                if len(content) != entry['bytes'] or digest(content) != entry['sha256']:
                    raise RuntimeError('Archive manifest mismatch: '+entry['path'])
            expected = {prefix+entry['path'] for entry in manifest['files']} | {prefix+'SOURCE_MANIFEST.json'}
            if set(names) != expected:
                raise RuntimeError('Archive manifest member-set mismatch')
        result['archive'] = {'path': str(args.archive), 'bytes': args.archive.stat().st_size,
                             'sha256': digest(args.archive.read_bytes()), 'members': len(names),
                             'crc_manifest_and_member_set': 'PASS'}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()

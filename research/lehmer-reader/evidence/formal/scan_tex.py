#!/usr/bin/env python3
"""Detect control bytes and omitted backslashes in known spacing commands."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[2]
files = sorted([*root.joinpath('paper').glob('*.tex'),
                *root.joinpath('visual').glob('*.tex'),
                *root.joinpath('shared').glob('*preamble.tex')])
problems = []
records = []
bare_spacing = re.compile(r'(?<![\\A-Za-z])q?quad(?=\d|\\|\s)')
for path in files:
    data = path.read_bytes()
    rel = str(path.relative_to(root))
    records.append({'path': rel, 'sha256': hashlib.sha256(data).hexdigest()})
    for offset, byte in enumerate(data):
        if byte < 32 and byte not in (9, 10, 13):
            problems.append({'path': rel, 'line': data[:offset].count(b'\n') + 1,
                             'issue': 'Unexpected control byte', 'byte': byte})
    for line, text in enumerate(data.decode('utf-8').splitlines(), 1):
        if bare_spacing.search(text):
            problems.append({'path': rel, 'line': line,
                             'issue': 'Possible spacing command missing backslash'})

record = {'date': '2026-10-09', 'scope': 'Current paper and guide TeX plus both preambles',
          'file_count': len(files), 'files': records, 'issues': problems,
          'status': 'PASS' if not problems else 'FAIL',
          'limit': 'This byte/token scan does not parse TeX or prove mathematical statements.'}
Path(__file__).with_name('tex_token_scan.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'file_count': len(files), 'status': record['status'], 'issues': problems}, indent=2))
raise SystemExit(bool(problems))

"""Pin the shipped sources and audit records without claiming new verification."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
files = []
for folder, suffixes in [('paper', {'.tex'}), ('visual', {'.tex', '.py'}),
                         ('shared', {'.tex'}), ('audits', {'.json', '.md'}),
                         ('literature', {'.json', '.md'})]:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in suffixes)
files.extend(p for p in (ROOT/'output/pdf').glob('*.pdf'))
files.extend(p for p in (ROOT/'evidence/computation').rglob('*.json'))
files.extend(p for p in (ROOT/'visual/figures').glob('*.pdf'))
records = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))]
out = {'edition': '1.0', 'date': '2026-10-09', 'files': records,
       'scope': 'Content identities for the released source, figures, computation and audit records. A hash is provenance, not a mathematical verification.'}
(ROOT/'evidence/RELEASE_EVIDENCE_PINS.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({'pinned_files': len(records)}, indent=2))

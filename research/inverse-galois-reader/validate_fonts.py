"""Record font embedding and Unicode-map checks for the final Inverse_Galois readers."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
documents = {}
for path in sorted((ROOT / 'output' / 'pdf').glob('*.pdf')):
    result = subprocess.run(['pdffonts', str(path)], capture_output=True, text=True, check=True)
    lines = result.stdout.splitlines()
    rows = [line for line in lines[2:] if line.strip()]
    assert rows, path
    flags = [row.split()[-5:-2] for row in rows]
    assert all(row == ['yes', 'yes', 'yes'] for row in flags), (path, rows)
    assert all('Type 3' not in row for row in rows), (path, rows)
    documents[path.name] = {
        'path': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'command': ['pdffonts', str(path.relative_to(ROOT))],
        'font_rows': rows,
        'all_fonts_embedded': True,
        'all_fonts_subsetted': True,
        'all_fonts_have_unicode_maps': True,
        'type3_fonts': False,
    }
assert len(documents) == 2, documents
record = {'date': '2026-10-09', 'status': 'passed', 'documents': documents}
(ROOT / 'evidence/FONT_VALIDATION.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': 'passed', 'documents': list(documents)}, indent=2))

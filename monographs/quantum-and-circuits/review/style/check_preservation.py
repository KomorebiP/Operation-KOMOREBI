"""Verify this presentation revision leaves all generated mathematical text intact."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
baseline = json.loads((BASE / 'baseline.json').read_text())
manifest = json.loads((ROOT / 'volume/source_manifest.json').read_text())
errors = []
for scope, entries in [('consolidated content', baseline['content_files']), ('component source', manifest)]:
    for rel, expected in entries.items():
        path = ROOT / rel
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != expected:
            errors.append({'scope': scope, 'path': rel, 'expected': expected, 'actual': actual})
result = {
    'status': 'PASS' if not errors else 'FAIL',
    'generated_content_files_unchanged': len(baseline['content_files']),
    'component_source_files_unchanged': len(manifest),
    'prior_pdf_sha256': baseline['prior_pdf_sha256'],
    'errors': errors,
    'scope': 'Byte-for-byte content preservation across the presentation revision; not a new mathematical or Lean audit.'
}
(BASE / 'content_integrity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors))

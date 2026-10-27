"""Package the reviewed Hodge sources, evidence, and final PDFs."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'output'
OUT.mkdir(exist_ok=True)
NAME = 'Komorebi_Hodge_Source_and_Evidence_v1.0.zip'
PREFIX = 'Komorebi_Hodge_v1.0/'
SKIP_SUFFIX = {'.aux', '.out', '.toc', '.lof', '.lot', '.synctex.gz', '.pyc'}
SKIP_NAMES = {'MANIFEST.json'}

def eligible(p):
    rel = p.relative_to(ROOT)
    if len(rel.parts) > 1 and rel.parts[0] in {'paper', 'visual'} and rel.parts[1].startswith('qa'):
        return False
    if any(part in {'__pycache__', '.git', '.lake', 'node_modules'} for part in rel.parts):
        return False
    if p.name == 'main.pdf' or p.suffix in SKIP_SUFFIX:
        return False
    if len(rel.parts) == 1 and p.name in SKIP_NAMES:
        return False
    return True

files = [p for p in sorted(ROOT.rglob('*')) if p.is_file() and eligible(p)]
records = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest = {'title': 'Operation Komorebi / Hodge / Conjecture Series 06',
            'edition': '1.0', 'publication_date': '2026-10-09',
            'claim_boundary': 'The general rational Hodge conjecture is not proved here.',
            'files': records,
            'build': 'python3 build.py --figures',
            'historical_sources': 'evidence/originals and evidence/recovered preserve prior claims and are governed by the current audit reports.'}
mp = ROOT / 'MANIFEST.json'
mp.write_text(json.dumps(manifest, indent=2) + '\n')
with zipfile.ZipFile(OUT / NAME, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for p in files + [mp]:
        info = zipfile.ZipInfo(PREFIX + str(p.relative_to(ROOT)), (2026, 10, 9, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
with zipfile.ZipFile(OUT / NAME) as archive:
    assert archive.testzip() is None
    for record in records:
        payload = archive.read(PREFIX + record['path'])
        assert len(payload) == record['bytes']
        assert hashlib.sha256(payload).hexdigest() == record['sha256']
print(json.dumps({'file': str(OUT / NAME), 'members': len(files) + 1,
                  'bytes': (OUT / NAME).stat().st_size,
                  'sha256': hashlib.sha256((OUT / NAME).read_bytes()).hexdigest()}, indent=2))

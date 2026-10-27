"""Package the reviewed Inverse_Galois sources, evidence, and final PDFs."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
NAME = 'Komorebi_Inverse_Galois_Source_and_Evidence_v1.0.zip'
PREFIX = 'Komorebi_Inverse_Galois_v1.0/'
SKIP_SUFFIX = {'.aux', '.out', '.toc', '.lof', '.lot', '.synctex.gz', '.pyc'}
SKIP_NAMES = {'MANIFEST.json'}

def eligible(p):
    rel = p.relative_to(ROOT)
    if len(rel.parts) > 1 and rel.parts[0] in {'paper', 'visual'} and rel.parts[1].startswith('qa'):
        return False
    if any(part in {'__pycache__', '.git', '.lake', 'node_modules'} for part in rel.parts):
        return False
    if rel.parts[0] == 'output' and p.suffix == '.zip':
        return False
    if p.name == 'main.pdf' or p.suffix in SKIP_SUFFIX:
        return False
    if len(rel.parts) == 1 and p.name in SKIP_NAMES:
        return False
    return True

files = [p for p in sorted(ROOT.rglob('*')) if p.is_file() and eligible(p)]
records = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest = {'title': 'Operation Komorebi / inverse Galois problem / Conjecture Series 09',
            'edition': '1.0', 'publication_date': '2026-10-09',
            'claim_boundary': 'This edition proves specified field and subgroup-projector statements, explains conditional realization routes, and reproduces bounded exact examples. It does not establish inverse Galois realization over Q for every finite group.',
            'files': records,
            'build': 'python3 build.py --figures',
            'historical_sources': 'historical/ preserves four recovered Library-resolved inputs byte for byte. Current evidence reports govern claim scope.'}
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

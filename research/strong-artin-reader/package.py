"""Package and hash-verify the Strong Artin reader and evidence handoff."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / 'output'
PDF_OUTPUT = OUTPUT / 'pdf'
PDF_OUTPUT.mkdir(parents=True, exist_ok=True)
required = [
    'README.md', 'AUTHORING_REPORT.md', 'paper/SOURCES.md',
    'paper/PROOFREADING.md', 'visual/PROOFREADING.md',
    'evidence/LITERATURE_CHECK.md', 'evidence/LEAN_COVERAGE.md',
    'evidence/REVIEW.md', 'evidence/SOURCE_VALIDATION.json',
    'evidence/LAYOUT_VALIDATION.json',
    'pdf/Komorebi_Strong_Artin_Conjecture_Piece_v1.0.pdf',
    'pdf/Komorebi_Strong_Artin_Visual_Guide_v1.0.pdf',
]
for name in required:
    if not (ROOT / name).is_file():
        raise SystemExit(f'Required release file missing: {name}')

def include(path):
    rel = path.relative_to(ROOT)
    if rel.parts[:2] == ('evidence', 'literature'):
        return False  # External papers/text stay in the private working source cache.
    if '__pycache__' in rel.parts or path.name == 'MANIFEST.json':
        return False
    if '.openai-download-' in path.name:
        return False
    if path.suffix in {'.aux', '.log', '.out', '.toc', '.pyc'}:
        return False
    if len(rel.parts) == 2 and rel.parts[0] in {'paper', 'visual'} and path.name == 'main.pdf':
        return False
    return True

files = sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p))
entries = [{'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size,
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest = ROOT / 'MANIFEST.json'
manifest.write_text(json.dumps({'edition':'1.0', 'date':'2026-10-08',
    'author':'Komorebi P.', 'self_excluded':'MANIFEST.json',
    'scope':'Strong Artin monograph, visual guide, reproducible figures, exact checks, historical Lean sources and review evidence. Third party full papers excluded.',
    'files':entries}, indent=2)+'\n')
archive = OUTPUT / 'Komorebi_Strong_Artin_Source_and_Evidence_v1.0.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files + [manifest]:
        z.write(p, 'Komorebi_Strong_Artin_v1.0/' + str(p.relative_to(ROOT)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for e in entries:
        assert hashlib.sha256(z.read('Komorebi_Strong_Artin_v1.0/'+e['path'])).hexdigest()==e['sha256'],e['path']
for p in sorted((ROOT/'pdf').glob('*.pdf')):
    target = PDF_OUTPUT/p.name
    shutil.copyfile(p,target)
    print(target)
print(archive)
print(f'Verified {len(entries)} payload files, plus manifest')

"""Package the reviewed Beal readers, selected historical payloads, and evidence."""
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
    'README.md', 'AUTHORING_REPORT.md', 'paper/PROOFREADING.md',
    'visual/PROOFREADING.md', 'evidence/LITERATURE_CHECK.md',
    'evidence/PROOF_AUDIT.md', 'evidence/COMPUTATION_AUDIT.md',
    'evidence/FORMAL_STATUS.md', 'evidence/REVIEW_PINS.json',
    'evidence/SOURCE_VALIDATION.json', 'evidence/LAYOUT_VALIDATION.json',
    'evidence/FONT_VALIDATION.json', 'evidence/recovered/PAYLOAD_SELECTION.json',
    'pdf/Komorebi_Beal_Conjecture_Piece_v1.0.pdf',
    'pdf/Komorebi_Beal_Visual_Guide_v1.0.pdf',
]
for name in required:
    assert (ROOT / name).is_file(), name
for name in ['SOURCE_VALIDATION.json', 'LAYOUT_VALIDATION.json', 'FONT_VALIDATION.json']:
    assert json.loads((ROOT / 'evidence' / name).read_text())['status'] == 'passed', name

selection = json.loads((ROOT / 'evidence/recovered/PAYLOAD_SELECTION.json').read_text())
preserved = {row['release_path']: row for row in selection['included']}
for name, row in preserved.items():
    path = ROOT / name
    assert path.is_file(), name
    assert path.stat().st_size == row['bytes'], name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], name


def include(path):
    rel = path.relative_to(ROOT)
    if rel.parts[:2] == ('evidence', 'literature'):
        return False
    if '__pycache__' in rel.parts or rel == Path('MANIFEST.json'):
        return False
    if '.openai-download-' in path.name:
        return False
    if path.suffix in {'.pyc', '.aux', '.toc', '.out', '.tar', '.zst', '.so', '.olean', '.ilean'}:
        return False
    if len(rel.parts) == 2 and rel.parts[0] in {'paper', 'visual'} and path.name in {'main.pdf', 'main.log', 'build_stdout.log'}:
        return False
    return True


files = sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p))
included_names = {str(p.relative_to(ROOT)) for p in files}
assert set(preserved).issubset(included_names), sorted(set(preserved) - included_names)
figure_snapshots = {
    'visual/computations/superseded_atlas-v1.0.zip': '186ec67a8de60365827124438214327a48b6d3a5010880e9dd67f017cce5762e',
    'visual/computations/superseded_atlas-v1.0b.zip': 'd41bbfe7e01719d8c64fc30ddfc511a5bce7971cc40189516bf208c0c69cc642',
    'visual/computations/superseded_atlas-final-v1.0.zip': '2db5002c0cf01052bbb47440592d493ddc1ba0e2a8b115709925a592ee276c17',
}
for p in files:
    if p.suffix != '.zip':
        continue
    rel = str(p.relative_to(ROOT))
    assert rel in figure_snapshots, ('Whole historical archives are excluded', rel)
    assert hashlib.sha256(p.read_bytes()).hexdigest() == figure_snapshots[rel], rel
    with zipfile.ZipFile(p) as snapshot:
        assert snapshot.testzip() is None, rel
        members = snapshot.namelist()
        assert len(members) == 74 and not any(Path(x).is_absolute() or '..' in Path(x).parts for x in members), rel
        assert all(Path(x).suffix in {'.json', '.pdf', '.png', '.tex', '.py', '.md', '.txt'} for x in members), rel
        assert all('/figures/' in x for x in members if Path(x).suffix in {'.pdf', '.png'}), rel
        assert sum(Path(x).suffix == '.pdf' for x in members) == 24, rel
        assert sum(Path(x).suffix == '.png' for x in members) == 24, rel
for p in files:
    if p.stat().st_size >= 40 * 1024 * 1024:
        rel = str(p.relative_to(ROOT))
        assert rel in preserved and p.suffix == '.json', ('Unexpected large file', rel)
        # Some exact point-count tables exceed 40 MB. Their original bytes are
        # authenticated in the historical selection, unlike compiler caches.

entries = [
    {'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
     'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    for p in files
]
manifest = ROOT / 'MANIFEST.json'
manifest.write_text(json.dumps({
    'edition': '1.0', 'date': '2026-10-08', 'author': 'Komorebi P.',
    'self_excluded': 'MANIFEST.json',
    'scope': 'Beal readers, exact figure code and data, original selected historical non-paper payloads, and fresh literature, proof, computation, formal, and layout evidence. External complete papers, page captures, nested complete archives, and compiler/runtime caches excluded.',
    'files': entries,
}, indent=2) + '\n')

archive = OUTPUT / 'Komorebi_Beal_Source_and_Evidence_v1.0.zip'
prefix = 'Komorebi_Beal_v1.0/'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files + [manifest]:
        z.write(p, prefix + str(p.relative_to(ROOT)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for row in entries:
        assert hashlib.sha256(z.read(prefix + row['path'])).hexdigest() == row['sha256'], row['path']
for p in sorted((ROOT / 'pdf').glob('*.pdf')):
    target = PDF_OUTPUT / p.name
    shutil.copyfile(p, target)
    print(target)
print(archive)
print(f'Verified {len(entries)} payload files plus manifest, original selection hashes, SHA-256, and ZIP CRC.')

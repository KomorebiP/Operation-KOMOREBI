#!/usr/bin/env python3
"""Assemble the finalized Paper VI companions and preserved source evidence."""
from pathlib import Path
import hashlib, json, shutil
import fitz

W = Path(__file__).resolve().parent
R = W.parent / 'output' / 'Komorebi_Paper_VI_Final_Edition_2026-10-05'
R.mkdir(parents=True, exist_ok=True)

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cp(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

specs = [('traditional', 'Paper_VI_Traditional_Final', 'Traditional paper'),
         ('visual_guide', 'Paper_VI_Visual_Guide_Final', 'Visual guide'),
         ('lean_guide', 'Paper_VI_Lean_Guide_Final', 'Lean guide')]
documents = []
for role, stem, title in specs:
    src, dst = W / role, R / 'editable' / role
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        '__pycache__', 'qa', stem + '.pdf', '*.aux', '*.log', '*.out', '*.toc',
        '*.lof', '*.blg', '*.fdb_latexmk', '*.fls', '*.xdv', '*.synctex.gz',
        'build_pass_*.txt'))
    pdf = R / 'papers' / (stem + '.pdf')
    cp(src / (stem + '.pdf'), pdf)
    qa_dst = R / 'verification' / 'layout' / role
    if qa_dst.exists():
        shutil.rmtree(qa_dst)
    if (src / 'qa').is_dir():
        for p in (src / 'qa').rglob('*'):
            if p.is_file() and (p.suffix in ('.json', '.txt') or p.name.startswith('contact')):
                cp(p, qa_dst / p.relative_to(src / 'qa'))
    for p in list(src.glob('*.log')) + list(src.glob('build_pass_*.txt')):
        cp(p, R / 'verification' / 'pdf_build_logs' / role / p.name)
    with fitz.open(pdf) as doc:
        pages = len(doc)
    documents.append(dict(role=role, title=title, path=str(pdf.relative_to(R)),
                          pages=pages, bytes=pdf.stat().st_size, sha256=sha(pdf)))

for folder in ('source', 'downloads', 'provenance', 'audit', 'verification'):
    shutil.copytree(W / folder, R / folder, dirs_exist_ok=True)

metadata = json.loads((W / 'FINAL_METADATA.json').read_text())
metadata.update(documents=documents, total_pages=sum(d['pages'] for d in documents))
dump(R / 'EDITION.json', metadata)

# Exact companion inventories remain next to their editable sources. The index
# below points to all JSON navigation, scope and preservation records.
crosswalk_files = []
for role, _, _ in specs:
    for p in sorted((R / 'editable' / role).rglob('*.json')):
        crosswalk_files.append(str(p.relative_to(R)))
dump(R / 'COMPANION_MAP.json', dict(paper='VI', documents=documents,
                                    navigation_and_evidence_files=crosswalk_files))

previous = W / 'provenance' / 'PREVIOUS_SERIES_STATUS.json'
old = json.loads(previous.read_text())
status = json.loads(json.dumps(old))
entry = next(p for p in status['papers'] if p['paper'] == 'VI')
entry.update(traditional='finalized', visual_guide='finalized', lean_guide='finalized',
    machine_native='not_requested', source_refresh_before_editing=False,
    source_branches=metadata['source_branches'],
    source_scope=metadata['series_scope'],
    notes='Final traditional, visual and Lean companions. Current checks are distinguished from inherited Lean evidence. Papers I–V closed; VII–XII frozen.',
    documents=documents, total_pages=metadata['total_pages'])
status.update(finalized_papers=6, finalized_companion_documents=18,
    run_state='closed_after_Paper_VI', active_authoring_papers=[],
    freeze_instruction='Papers I–V remain closed. Paper VI finalized as traditional paper, visual guide and Lean guide. Papers VII–XII remain frozen; no further authoring is queued.')
assert all(a == b for a, b in zip(old['papers'], status['papers']) if a['paper'] != 'VI')
dump(R / 'SERIES_STATUS.json', status)
for name in ('README.txt', 'CORRECTIONS_AND_SCOPE.txt'):
    cp(W / name, R / name)
cp(W / 'build_packaged_pdfs.py', R / 'scripts' / 'build_pdfs.py')
cp(W / 'provenance' / 'VERIFY_INTEGRITY_RECIPE.py', R / 'scripts' / 'verify_integrity.py')
cp(W / 'assemble_release.py', R / 'provenance' / 'ASSEMBLY_RECIPE.py')
cp(W / 'FINAL_METADATA.json', R / 'provenance' / 'FINAL_METADATA_INPUT.json')
print(json.dumps(dict(root=str(R), documents=documents, total_pages=metadata['total_pages']), indent=2))

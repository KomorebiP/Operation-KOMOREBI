#!/usr/bin/env python3
"""Assemble the final Paper VIII set while preserving its raw recovery sources."""
from pathlib import Path
import hashlib
import json
import shutil
import fitz

W = Path(__file__).resolve().parent
R = W.parent / 'output' / 'Komorebi_Paper_VIII_Final_Edition_2026-10-06'

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cp(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

specs = [('traditional', 'Paper_VIII_Traditional_Final', 'Traditional paper'),
         ('visual_guide', 'Paper_VIII_Visual_Guide_Final', 'Visual guide'),
         ('lean_guide', 'Paper_VIII_Lean_Guide_Final', 'Lean guide')]
R.mkdir(parents=True, exist_ok=True)
documents = []
for role, stem, title in specs:
    src, dst = W / role, R / 'editable' / role
    entry_point = stem + '.tex' if (src / (stem + '.tex')).is_file() else 'appendix.tex'
    assert (src / entry_point).is_file(), (role, 'missing editable document')
    assert (src / 'build.py').is_file(), (role, 'missing portable builder')
    assert (src / (stem + '.pdf')).is_file(), (role, 'missing final PDF')
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        '__pycache__', 'qa', 'build', stem + '.pdf', '*.aux', '*.log',
        '*.out', '*.toc', '*.lof', '*.bbl', '*.blg', '*.fdb_latexmk',
        '*.fls', '*.xdv', '*.synctex.gz', 'build_pass_*.txt'))
    pdf = R / 'papers' / (stem + '.pdf')
    cp(src / (stem + '.pdf'), pdf)
    with fitz.open(pdf) as doc:
        assert len(doc) > 0 and not doc.is_encrypted
        pages = len(doc)
        assert all(len(page.get_text().strip()) > 0 for page in doc)
    documents.append(dict(role=role, title=title, path=str(pdf.relative_to(R)),
                          source_entry_point='editable/' + role + '/' + entry_point,
                          pages=pages, bytes=pdf.stat().st_size, sha256=sha(pdf)))
    for folder in ('qa', 'build'):
        if (src / folder).is_dir():
            for p in (src / folder).rglob('*'):
                if p.is_file() and (p.suffix in ('.json', '.txt', '.log')
                                   or p.name.startswith('contact')):
                    cp(p, R / 'verification' / 'layout' / role / p.relative_to(src / folder))
    for p in list(src.glob('*.log')) + list(src.glob('build_pass_*.txt')):
        cp(p, R / 'verification' / 'pdf_build_logs' / role / p.name)

for folder in ('source', 'downloads', 'provenance', 'audit', 'verification'):
    assert (W / folder).is_dir()
    shutil.copytree(W / folder, R / folder, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
assert len([p for p in (R / 'source').rglob('*') if p.is_file()]) == 1062

metadata = json.loads((W / 'FINAL_METADATA.json').read_text())
metadata.update(documents=documents, total_pages=sum(d['pages'] for d in documents))
dump(R / 'EDITION.json', metadata)

crosswalk_files = []
for role, _, _ in specs:
    for p in sorted((R / 'editable' / role).rglob('*.json')):
        crosswalk_files.append(str(p.relative_to(R)))
dump(R / 'COMPANION_MAP.json', dict(paper='VIII', documents=documents,
                                   navigation_and_evidence_files=crosswalk_files))

previous = W / 'provenance' / 'PREVIOUS_SERIES_STATUS.json'
old = json.loads(previous.read_text())
status = json.loads(json.dumps(old))
entry = next(p for p in status['papers'] if p['paper'] == 'VIII')
entry.update(traditional='finalized', visual_guide='finalized', lean_guide='finalized',
    machine_native='not_requested', source_refresh_before_editing=False,
    source_branches=metadata['source_branches'],
    source_scope=metadata['series_scope'],
    notes='Final traditional, visual and Lean companions. Current computations and static checks are distinguished from inherited Lean evidence. Papers I–VII closed; IX–XII frozen.',
    documents=documents, total_pages=metadata['total_pages'])
status.update(edition_date=metadata['edition_date'], finalized_papers=8,
    finalized_companion_documents=24, run_state='closed_after_Paper_VIII',
    active_authoring_papers=[],
    freeze_instruction='Papers I–VII remain closed. Paper VIII finalized as traditional paper, visual guide and Lean guide. Papers IX–XII remain frozen; no further authoring is queued.')
assert all(a == b for a, b in zip(old['papers'], status['papers']) if a['paper'] != 'VIII')
dump(R / 'SERIES_STATUS.json', status)

for name in ('README.txt', 'CORRECTIONS_AND_SCOPE.txt'):
    cp(W / name, R / name)
cp(W / 'build_packaged_pdfs.py', R / 'scripts' / 'build_pdfs.py')
cp(W / 'verify_integrity.py', R / 'scripts' / 'verify_integrity.py')
cp(W / 'preflight_pdfs.py', R / 'scripts' / 'preflight_pdfs.py')
cp(W / 'assemble_release.py', R / 'provenance' / 'ASSEMBLY_RECIPE.py')
cp(W / 'FINAL_METADATA.json', R / 'provenance' / 'FINAL_METADATA_INPUT.json')
print(json.dumps(dict(root=str(R), documents=documents,
                      total_pages=metadata['total_pages']), indent=2))

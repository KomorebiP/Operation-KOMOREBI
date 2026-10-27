#!/usr/bin/env python3
"""Assemble Paper V's final reading edition and preserved evidence."""
from pathlib import Path
import hashlib, json, shutil
import fitz

W = Path(__file__).resolve().parent
R = W.parent/'output'/'Komorebi_Paper_V_Final_Edition_2026-10-05'
R.mkdir(parents=True, exist_ok=True)
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def cp(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

specs = [('traditional','Paper_V_Traditional_Final','Traditional paper'),
         ('visual_guide','Paper_V_Visual_Guide_Final','Visual guide'),
         ('lean_guide','Paper_V_Lean_Guide_Final','Lean guide')]
documents = []
for role, stem, title in specs:
    src = W/role
    dst = R/'editable'/role
    # Preserve vector figure PDFs; omit only rendered manuscript and build files.
    shutil.copytree(src, dst, dirs_exist_ok=True,
      ignore=shutil.ignore_patterns('__pycache__','qa',stem+'.pdf','*.aux','*.log','*.out',
        '*.toc','*.lof','*.blg','*.fdb_latexmk','*.fls','*.xdv','*.synctex.gz','build_pass_*.txt'))
    pdf = R/'papers'/(stem+'.pdf')
    cp(src/(stem+'.pdf'), pdf)
    if (src/'qa').is_dir():
        for p in (src/'qa').rglob('*'):
            if p.is_file() and (p.suffix in ('.json','.txt') or p.name.startswith('contact')):
                # Superseded draft contact sheet; final sheet covers pages49–57.
                if role=='lean_guide' and p.name=='contact_049_055.png':
                    continue
                cp(p, R/'verification'/'layout'/role/p.relative_to(src/'qa'))
    for p in list(src.glob('*.log'))+list(src.glob('build_pass_*.txt')):
        cp(p, R/'verification'/'pdf_build_logs'/role/p.name)
    with fitz.open(pdf) as doc: pages = len(doc)
    documents.append(dict(role=role,title=title,path=str(pdf.relative_to(R)),pages=pages,
                          bytes=pdf.stat().st_size,sha256=sha(pdf)))

# Source snapshots are byte-preserved, including original cache/evidence files.
for folder in ('source','downloads','provenance','audit','verification'):
    shutil.copytree(W/folder, R/folder, dirs_exist_ok=True)

metadata = json.loads((W/'FINAL_METADATA.json').read_text())
metadata.update(documents=documents,total_pages=sum(d['pages'] for d in documents))
dump(R/'EDITION.json', metadata)
crosswalks = {}
for folder, names in {
 'traditional':['canonical_label_to_final.json','manuscript_record_to_final.json'],
 'visual_guide':['VISUAL_CROSSWALK.json'],
 'lean_guide':['generated/traditional_crosswalk.json','generated/result_ledger.json',
               'generated/targets.json']}.items():
    for name in names:
        p=W/folder/name
        if p.is_file():crosswalks[folder+'/'+name]=json.loads(p.read_text())
dump(R/'COMPANION_MAP.json',dict(paper='V',documents=documents,crosswalks=crosswalks))

previous = R.parent/'Komorebi_Paper_IV_Final_Edition_2026-10-05/SERIES_STATUS.json'
old = json.loads(previous.read_text())
status = json.loads(json.dumps(old))
entry = next(p for p in status['papers'] if p['paper']=='V')
entry.update(traditional='finalized',visual_guide='finalized',lean_guide='finalized',
 machine_native='not_requested',source_refresh_before_editing=False,
 source_branches='Latest corrected v1.1.0 formal core, complete Annals developments, and complete visual appendix.',
 source_scope='20 core proof records plus63 development proof records, with conceptual overlap. Separate20-result formal contract and225 mapped targets. Documented corrections in the development branch. No fresh Lean compilation.',
 notes='Final traditional, visual and Lean companions. Both divergent source branches retained. Fresh exact, numerical and static checks are distinguished from inherited Lean evidence. Papers I–IV closed; VI–XII frozen.',
 documents=documents,total_pages=metadata['total_pages'])
status.update(finalized_papers=5,finalized_companion_documents=15,
 run_state='closed_after_Paper_V',active_authoring_papers=[],
 freeze_instruction='Papers I–IV remain closed. Paper V finalized as traditional paper, visual guide and Lean guide. Papers VI–XII remain frozen; no further authoring is queued.')
assert all(a==b for a,b in zip(old['papers'],status['papers']) if a['paper']!='V')
dump(R/'SERIES_STATUS.json',status)

for name in ('README.txt','CORRECTIONS_AND_SCOPE.txt'):
    cp(W/name,R/name)
cp(W/'build_packaged_pdfs.py',R/'scripts/build_pdfs.py')
cp(previous.parent/'scripts/verify_integrity.py',R/'scripts/verify_integrity.py')
cp(W/'assemble_release.py',R/'provenance/ASSEMBLY_RECIPE.py')
cp(W/'FINAL_METADATA.json',R/'provenance/FINAL_METADATA_INPUT.json')
print(json.dumps(dict(root=str(R),documents=documents,total_pages=metadata['total_pages']),indent=2))

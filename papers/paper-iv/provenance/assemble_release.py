#!/usr/bin/env python3
"""Package the frozen final Paper IV companions, preserved source and evidence."""
from pathlib import Path
import hashlib,json,shutil
import fitz

W=Path(__file__).resolve().parent
R=W.parent/'output'/'Komorebi_Paper_IV_Final_Edition_2026-10-05'
R.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def cp(a,b):
    b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
specs=[('traditional','Paper_IV_Traditional_Final','Traditional paper'),
       ('visual_guide','Paper_IV_Visual_Guide_Final','Visual guide'),
       ('lean_guide','Paper_IV_Lean_Guide_Final','Lean guide')]
documents=[]
for role,stem,title in specs:
    src=W/role;dst=R/'editable'/role
    shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns(
        '__pycache__','qa','*.pdf','*.aux','*.log','*.out','*.toc','*.lof',
        '*.bbl','*.blg','*.fdb_latexmk','*.fls','*.xdv','*.synctex.gz','build_pass_*.txt'))
    pdf=R/'papers'/(stem+'.pdf');cp(src/(stem+'.pdf'),pdf)
    for p in (src/'qa').iterdir():
        if p.is_file() and (p.suffix in ('.json','.txt') or p.name.startswith('contact')):
            cp(p,R/'verification'/'layout'/role/p.name)
            if p.suffix=='.json':cp(p,dst/'qa'/p.name)
    for p in list(src.glob('*.log'))+list(src.glob('build_pass_*.txt')):
        cp(p,R/'verification'/'pdf_build_logs'/role/p.name)
    with fitz.open(pdf) as f:pages=len(f)
    documents.append(dict(role=role,title=title,path=str(pdf.relative_to(R)),
                          pages=pages,bytes=pdf.stat().st_size,sha256=sha(pdf)))

for name in ('source','downloads','provenance','audit','verification'):
    shutil.copytree(W/name,R/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))

traditional=R/'editable/traditional'
lean=R/'editable/lean_guide'
proof=json.loads((traditional/'PROOF_PRESERVATION.json').read_text())
reconciliation=json.loads((traditional/'EDITION_RECONCILIATION.json').read_text())
maprows=json.loads((lean/'generated/theorem_map.json').read_text())
completion=json.loads((lean/'generated/completion_ledger.json').read_text())
compute=json.loads((R/'verification/run/CURRENT_VERIFICATION.json').read_text())
edition={
 'schema':'komorebi.paper_iv.final_edition.v1','author':'Komorebi P.',
 'paper':'IV','edition_date':'2026-10-05','editorial_status':'finalized',
 'title':'Projector-Resolved Seed Calculus IV: Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data',
 'documents':documents,'total_pages':sum(d['pages'] for d in documents),
 'machine_native_companion':'not_requested',
 'traditional':{'numbered_records':95,'theorem_like_results':68,'proof_environments':68,
    'imported_standard_facts':1,'byte_identical_statements':proof['byte_identical_statements'],
    'byte_identical_proofs':proof['byte_identical_proofs'],'new_mathematical_token_changes':0,
    'selected_source':'Later proofread manuscript with all nine previous correction groups retained.'},
 'visual':{'worked_pages':26,'preserved_vector_plates':24},
 'formal_contract':{'version':'1.0.0','historical_release_date':'2026-09-05',
    'scoped_results':68,'map_rows':151,'mapped_targets':1164,'mapped_theorems':953,
    'mapped_constructions':211,'namespace_entries':2234,'namespace_theoremInfo':1999,
    'semantic_check_declarations':43,'fresh_lean_execution':False,
    'boundary':'Historical complete scoped coverage; imported standard fact and explicit open questions remain outside that denominator.'},
 'verification':{'current_status':'PASS_FOR_STATED_SCOPE',
    'fresh':['Source and archive identity, manifests, 95-record regeneration and formal static reconciliation.',
             '818 numeric CSV rows checked exactly with integers and rational arithmetic.',
             'Four existing cubic root brackets rechecked with exact endpoint and derivative enclosures.',
             'Separate independent algebra review: 1,008 bounded exact rational assertions.'],
    'not_run':['Fresh Lean build or kernel audit.','Original 147 visual checks and 5 false controls.',
               'Original 24-plate regeneration.','Original strengthened regression suites.'],
    'environment':'Lean/lake, SymPy and mpmath unavailable; no dependency installation attempted in this Paper IV run.',
    'mathematical_review':'No new repair required within the documented manuscript-argument and selected formal-interface review. Not an exhaustive semantic audit of 1,164 targets or a new kernel certificate.',
    'citation_limit':'Original Hadamard full-text retrieval timed out. Bibliographic identity and local formal specialization were checked separately.'}}
dump(R/'EDITION.json',edition)
dump(R/'COMPANION_MAP.json',{'paper':'IV','documents':documents,
 'traditional_labels':json.loads((traditional/'canonical_label_to_final.json').read_text()),
 'traditional_numbered_records':json.loads((traditional/'manuscript_record_to_final.json').read_text()),
 'visual':json.loads((R/'editable/visual_guide/VISUAL_CROSSWALK.json').read_text()),
 'formal_rows':maprows,'scoped_result_completion':completion,
 'historical_reconciliation':reconciliation})

previous=R.parent/'Komorebi_Paper_III_Final_Edition_2026-10-05/SERIES_STATUS.json'
old=json.loads(previous.read_text());status=json.loads(json.dumps(old))
p=next(p for p in status['papers'] if p['paper']=='IV')
p.update(traditional='finalized',visual_guide='finalized',lean_guide='finalized',
 machine_native='not_requested',source_refresh_before_editing=False,
 source_branches='Complete formal v1.0.0, later proofread manuscript, exact visual appendix; earlier strengthened branch retained for provenance.',
 source_scope='95 numbered records and 68 proofs preserved exactly. Historical complete coverage of 68 scoped results across 151 formal-map rows and 1,164 targets. No fresh Lean build.',
 notes='Final traditional, visual and Lean companions. Fresh checks passed for 818 exact CSV rows and four cubic brackets; a separate 1,008 algebra assertions also passed. Original dependency-requiring suites remain historical. Papers I–III closed; V–XII frozen.',
 documents=documents,total_pages=edition['total_pages'])
status.update(finalized_papers=4,finalized_companion_documents=12,
 run_state='closed_after_Paper_IV',active_authoring_papers=[],
 freeze_instruction='Papers I–III remain closed. Paper IV is finalized as traditional paper, visual guide and Lean guide. Papers V–XII remain frozen; no further authoring is queued.')
assert all(a==b for a,b in zip(old['papers'],status['papers']) if a['paper']!='IV')
dump(R/'SERIES_STATUS.json',status)

(R/'CORRECTIONS_AND_MIGRATION.txt').write_text('''Paper IV — final companion editorial record

This edition uses the later proofread manuscript, retaining all nine previous
correction groups P01–P09. All 95 numbered statement environments and all 68 proof
environments are byte-identical to that selected source. No additional
mathematical-token changes were made in this finalization.

The earlier corrections clarify the reciprocal logarithmic derivative,
normalized analytic power germ, determinant proof indices, local tangent
convergence, indicator notation/limsup, N>=2 zero-zeta scope, and notation or
unused macro cleanup. The complete earlier review and exact patch remain in
source/complete/original_snapshot/proofread_review/PRSC_IV_Review/.

The August strengthened source has 97 numbered records and 69 proofs. The latest
manuscript deliberately relocates the general holomorphic operator-substitution
section to Paper VI scope. Its section label, imported-standard-fact label and
proposition label are retained in the historical migration record. Five further
labels were renamed; 106 labels are shared. This is deliberate scope migration,
not a missing proof in the 68-result final Paper IV contract. Paper VI was not
edited during this task. The entire older source is preserved in source/strengthened.

Exact records:
editable/traditional/EDITORIAL_CHANGES.json
editable/traditional/EDITION_RECONCILIATION.json
editable/traditional/PROOF_PRESERVATION.json
editable/traditional/SOURCE_REVISION_DIFF.patch
audit/SCOPED_MATHEMATICAL_AUDIT.txt
''')
pages={d['role']:d['pages'] for d in documents}
(R/'README.txt').write_text(f'''KOMOREBI — PAPER IV FINAL COMPANION EDITION
Komorebi P. | 5 October 2026 (America/Chicago)
Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data

READING SET
papers/Paper_IV_Traditional_Final.pdf — {pages['traditional']} pages
papers/Paper_IV_Visual_Guide_Final.pdf — {pages['visual_guide']} pages
papers/Paper_IV_Lean_Guide_Final.pdf — {pages['lean_guide']} pages
Total: {edition['total_pages']} pages. No machine-native companion.

The traditional edition preserves the full selected proofread manuscript:
95 numbered statements, 68 proofs and one imported standard fact. It retains the
nine prior correction groups. The visual guide has 26 worked pages and 24 exact
vector plates. The Lean guide explains the actual source architecture, all
151 formal-map rows, all 1,164 mapped names, the 68-result completion ledger and
the nine final closure modules. Printed-page/statement references connect
the three companions.

FORMAL EVIDENCE
The original v1.0.0 release reports full scoped coverage of all 68 theorem-like
manuscript results, 953 mapped theorem declarations and 211 constructions.
Its raw kernel transcript, 119 Lean source files, exact toolchain pins and
original replay procedures are included. The saved namespace audit records
2,234 entries, including 1,999 theoremInfo declarations. These are distinct counts.
Current source/map/transcript checks are static. No new Lean compiler or
kernel audit was run. This is a new editorial companion edition, not a new
formal release or a broader theorem contract.

Imported standard fact 11.1 and the paper's explicit open questions remain
outside the 68-result contract. Fixed logarithms, normalized germs, positive
integral reciprocal orders, simple-nearest-zero hypotheses, multiplicities,
exceptional zeros and the specialized diagonal determinant remain explicit.

CURRENT CHECKS
All 291 preserved source files and both recovered archives match their original
bytes. Original manifest checks and 95-record regeneration passed. Exact
integer/rational comparisons passed for 818 numeric CSV rows. All four stored
cubic brackets were rechecked using rational Taylor remainder and derivative
enclosures. The separate algebra audit passed 1,008 bounded exact assertions.
These finite results are not added together as a universal theorem count.

The original 147-check visual suite, 5 false controls, 24-plate regeneration and
original strengthened regression scripts were not rerun: SymPy and mpmath
are unavailable. No dependency installation was attempted in this Paper IV
run. Historical results remain explicitly historical. Lean/lake are also
unavailable. See verification/README.txt for exact ranges and all boundaries.

The bounded mathematical review found no new repair necessary. It reviewed
manuscript argument chains and selected actual formal interfaces, not every
transitive dependency of all 1,164 targets. The original Hadamard full-text
retrieval timed out; the citation and local specialization are distinguished
in audit/SCOPED_MATHEMATICAL_AUDIT.txt. No novelty or priority judgment is made.

PACKAGE CONTENTS
editable/ — final TeX, guide excerpts, figures, crosswalks and portable builders
source/complete/ — original complete formal, proofread and visual release
source/strengthened/ — unchanged earlier strengthened edition
downloads/ — both original ZIPs, required by the exact archive-replay checker
audit/ — bounded argument review, source pins and independent algebra checks
verification/ — current bounded run, raw logs, PDF build/layout evidence
provenance/ — current source selection and complete recovered-source hashes
COMPANION_MAP.json — all current statement/page/formal-result connections
CORRECTIONS_AND_MIGRATION.txt — retained repairs and deliberate scope migration
SERIES_STATUS.json — only IV advanced; I–III closed and V–XII frozen
MANIFEST_SHA256.json — hashes of all shipped files except the manifest itself

REBUILD OR VERIFY
PDF compilation from packaged sources in temporary directories:
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-iv-build.json
Requires TeX Live with pdflatex, bibtex, xelatex, the packages in each preamble,
and PyMuPDF for comparison. The Lean guide uses P052, DejaVu Sans, DejaVu Sans
Mono and Latin Modern Math. This rebuild invokes no mathematics or Lean.
Without --check-only, the builder replaces PDFs; refresh metadata after edits.
Each editable companion has its own compile-only build.py.

Integrity only, using Python standard library:
  python3 scripts/verify_integrity.py
Fresh exact/static replay from this package root, using standard Python:
  python3 -B verification/scripts/verify_available.py --source source \\
    --downloads downloads --out verification/reproduced
Use a new output directory. See verification/README.txt for the full contract.
The independent algebra runner and its finite ranges are under audit/.
Lean replay instructions and pinned versions are in the guide and original
formal release. No supplied builder automatically installs dependencies.

Final PDFs live under papers/. Companion READMEs also use the basename of
their locally rebuilt PDF. Original source/status/reports describe their
historical snapshots. Keep them intact. No new license grant is introduced.
''')
previous_scripts=previous.parent/'scripts'
for name in ('build_pdfs.py','verify_integrity.py'):
    text=(previous_scripts/name).read_text().replace('Paper_III','Paper_IV').replace('paper-iii-','paper-iv-')
    text=text.replace("if folder=='traditional':", "if folder=='traditional' and (root/'editable'/folder/'figures').is_dir():")
    p=R/'scripts'/name;p.parent.mkdir(exist_ok=True);p.write_text(text)
print(json.dumps({'root':str(R),'documents':documents,'total_pages':edition['total_pages']},indent=2))

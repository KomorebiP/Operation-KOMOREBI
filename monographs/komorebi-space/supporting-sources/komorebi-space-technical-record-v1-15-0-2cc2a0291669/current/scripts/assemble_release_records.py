"""Assemble current release evidence after formal and book checks complete."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/'publication'
BUILD=sys.argv[1]
CURRENT=PUB/'verification/current'
CURRENT.mkdir(parents=True,exist_ok=True)
initial_current={'INTEGRATED_REPLAY.json','DECLARATIONS.json','THEOREM_MAP_CHECK.json'}
assert {p.name for p in CURRENT.iterdir()}==initial_current, 'Unexpected pre-assembly current records'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,indent=2)+'\n')
def copy(src,dst): dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)

r=json.loads((ROOT/'runs/clean_01/receipt.json').read_text())
assert r['status']=='PASS'
checks=json.loads((ROOT/f'build/review_{BUILD}/checks.json').read_text())
assert all(not c['final_latex_findings'] and not c['invalid_internal_links'] and not c['off_page_text'] for c in checks.values())
reconcile=json.loads((ROOT/'records/formal_reconciliation.json').read_text())
visual=json.loads((ROOT/'reviews/final_pdf_visual_review.json').read_text())
assert visual['status']=='PASS'

books={}
for key,stem in {'monograph':'Monograph','lean':'Lean_Guide','visual':'Visual_Guide'}.items():
    source=ROOT/f'build/{BUILD}/{key}/Komorebi_Space_{stem}.pdf'
    target=PUB/f'books/Komorebi_Space_{stem}_v1.15.0.pdf'
    copy(source,target)
    books[key]={'file':str(target.relative_to(PUB)),'sha256':sha(target),'pages':checks[key]['pages']}
for old in (PUB/'books').glob('*_v1.14.0.pdf'):
    # The immutable parent archive and parent technical record preserve these bytes.
    old.unlink()

copy(ROOT/f'build/{BUILD}/build_report.json',CURRENT/'BOOK_BUILD.json')
copy(ROOT/f'build/review_{BUILD}/checks.json',CURRENT/'PDF_CHECKS.json')
record_names=['formal_reconciliation.json','final_math_preservation.json','reader_bridge_review.json','formal_integration.json','VISUAL_REFERENCES.json','final_editorial_review.json','FINAL_TYPESETTING_AND_METADATA_CORRECTIONS.json','FINAL_ITERATION_PAGE_COMPARISON.json','FINAL_ITERATION_PAGE_COMPARISON_02_TO_03.json','FINAL_ITERATION_PAGE_COMPARISON_02_TO_04.json']
review_names=['inexact_math_audit.json','inexact_math_audit.md','range_math_audit.json','range_math_audit.md','runner_audit.json','runner_audit.md','book_proofread_source.json','book_proofread_source.md','final_pdf_visual_review.json','final_pdf_visual_review.md','replay_receipt_review.json','lean_pdf_visual_review.json','lean_pdf_visual_review.md','monograph_pdf_visual_review.json','monograph_pdf_visual_review.md','visual_pdf_review.json']
for name in record_names:
    copy(ROOT/'records'/name,CURRENT/name)
for name in review_names:
    copy(ROOT/'reviews'/name,CURRENT/name)
assert {p.name for p in CURRENT.iterdir()} == initial_current | set(record_names) | set(review_names) | {'BOOK_BUILD.json','PDF_CHECKS.json'}

counts={'production_modules':162,'import_entrypoints':4,'source_targets':166,
        'explicit_theorem_lemma_declarations':1859,'exported_declarations':r['exported_declarations'],
        'principal_groups':16,'principal_groups_formalized':16,'principal_groups_written_only':0,'selected_map_entries':114}
identity={}
for folder in ['source','lean']:
    for p in sorted((PUB/folder).rglob('*')):
        if p.is_file() and '.lake' not in p.parts and not p.is_symlink() and '__pycache__' not in p.parts:
            identity[str(p.relative_to(PUB))]=sha(p)
edition={'edition':'1.15.0','author':'Komorebi P.','date':'2026-10-15',
    'technical_status':'COMPLETE','reuse_license_status':'OWNER_CHOICE_PENDING_NO_NEW_GRANT',
    'scope':'Publication completion with two exact Lean connections, fresh integrated verification, a worked-example crosswalk, and reviewed books.',
    'counts':counts,'books':books,'source_identity':identity,
    'lean_version':'4.34.0-rc2','lean_revision':'6a10ac8c22beadecabdbb0919c2b50214762f91d',
    'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
    'permitted_axioms':r['axiom_union'],
    'fresh_integrated_replay':{'status':'PASS','record':'current/INTEGRATED_REPLAY.json','sha256':sha(CURRENT/'INTEGRATED_REPLAY.json'),
        'declarations':'current/DECLARATIONS.json','declarations_sha256':sha(CURRENT/'DECLARATIONS.json'),
        'controls':{'total':56,'accept':18,'elaboration_reject':35,'policy_reject':3,'all_expected_outcomes':True},
        'new_project_object_directory':True,'external_caches_rebuilt':False},
    'current_reviews':{str(p.relative_to(PUB/'verification')):sha(p) for p in sorted(CURRENT.iterdir()) if p.is_file()},
    'inherited_proofs':'All 160 inherited production modules are byte-identical to v1.14.0. Three roots are unchanged; the diagonal root adds two imports and updates its description.',
    'mathematical_preservation':'All 192 existing formal environments and 512 bracketed displays in 29 monograph chapters are byte-identical to the parent publication.',
    'trust_boundary':r['trust_boundary'],
    'limitations':[
      'The printed weak-subsequence proof route and separate protected product-space illustrative construction are not separately formalized by the two additions.',
      'Formal coverage of 16 principal groups is not a claim that every explanation, illustration, or alternate proof route has its own Lean counterpart.',
      'Finite Python examples are independently checked examples, not verified extraction of the Lean development.',
      'The 56 diagnostic controls are focused interface and policy checks, not exhaustive mutation testing.',
      'Public reuse licenses remain an owner decision; REUSE.md applies no new grant.',
      'Canonical PDF bytes inside the archive may differ from saved standalone PDFs that receive Content Credentials. Actual delivery identities and content comparison are recorded in the separate final delivery receipt.'
    ],
    'pdf_notice_disclosure':'Final unresolved-reference, overflow, missing-character, invalid-link, and off-page-text checks passed. Routine underfull-box notices and 16 visual-bookmark spacing notices remain recorded.',
    'historical_evidence':'history/v1.14.0 records the previous edition explicitly. DIAGONAL_* files and visual/* retain their own historical scope. The separate Technical Record preserves the exact parent technical archive and all current attempts.'}
save(PUB/'verification/EDITION_VERIFICATION.json',edition)
(PUB/'verification/README.md').write_text(f'''# Verification record

Publication edition1.15.0 has passed a fresh integrated Lean replay:166 targets,
{r['exported_declarations']:,} exported project declarations, and56 diagnostic controls.
The controls gave18 expected acceptances,35 intended elaboration rejections, and
three axiom-policy rejections. The1,859 explicit theorem/lemma count is a source
count; the declaration inventory also includes definitions and generated helpers.

`EDITION_VERIFICATION.json` binds the current books, sources, and reviews.
`current/INTEGRATED_REPLAY.json` records the fresh commands and outcomes.
`current/DECLARATIONS.json` is the complete project inventory, with defining
module, declaration kind, safety status, and recursive axiom dependencies.
`LEAN_THEOREM_MAP.json` identifies114 selected reader-facing declarations; its
names, modules, kinds, source hashes, and source lines were matched to that
inventory. Independent reviews of both new mathematical statements and the
portable runner are included in `current/`.

Run the complete check using the instructions in [runner/README.md](runner/README.md).
No previous project object files are used by a fresh run. The installed external
dependency caches are byte-recorded at both endpoints; they are trusted inputs,
not rebuilt or independently authenticated by the procedure. Endpoint checks
cannot exclude a transient change restored before the last snapshot.

The two additions retain the measured-data normal residual and rounded schedule,
and construct the actual diagonal unit witnesses and a datum in the range closure
without a preimage. Compiler acceptance and statement correspondence are separate
checks. Neither asserts a formal counterpart for every line of the books.

The29 monograph chapter files preserve all192 previous formal environments and 512
bracketed displays. Book build, structural, page-comparison, visual-review, and
worked-example records are in `current/`. The exact rational example is explained
in [WORKED_EXAMPLE.md](../examples/WORKED_EXAMPLE.md).

`history/v1.14.0/` retains the previous publication's records. The `DIAGONAL_*`
files preserve the earlier diagonal evidence, and `visual/` preserves the checks
for unchanged visual examples. These historical records are not relabeled as
current runs. The Technical Record preserves the complete parent technical
archive, current failed proof attempts, raw fresh replay logs, source snapshots,
compiler/cache identities, editorial records, and book-build attempts.

`SHA256SUMS` in the package binds the canonical archive bytes. Standalone PDFs may
receive embedded Content Credentials when saved, changing their bytes. The
separate `Komorebi_Space_Delivery_Verification_v1.15.0.json` records the hashes and
text/raster comparison of the actual downloaded copies. This does not authenticate
the Content Credentials signature. Reuse status is stated in [REUSE.md](../REUSE.md).
'''.replace('edition1.15','edition 1.15').replace('replay:166','replay: 166').replace('and56','and 56').replace('gave18','gave 18').replace('acceptances,35','acceptances, 35').replace('The1,859','The 1,859').replace('identifies114','identifies 114').replace('The29','The 29').replace('all192','all 192').replace('and 512','and 512'))
print(json.dumps({'edition':'1.15.0','counts':counts,'books':books},indent=2))

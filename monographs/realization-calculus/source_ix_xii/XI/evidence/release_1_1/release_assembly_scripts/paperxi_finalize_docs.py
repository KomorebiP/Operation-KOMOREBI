#!/usr/bin/env python3
"""One-time release-document assembly from completed, preserved result records."""
from pathlib import Path
import copy, datetime, hashlib, json
import fitz

BASE = Path('/workspace/scratch/604befec1954')
ROOT = BASE / 'paperxi_release'
CHECKPOINT = 'P11-RELEASE-1.1.0'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(path):
    return json.loads((ROOT / path).read_text())

def write(path, text):
    (ROOT / path).write_text(text.rstrip() + '\n')

def jswrite(path, obj):
    write(path, json.dumps(obj, indent=2, ensure_ascii=False))

def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')

formal = read('verification/lean/RELEASE_VERIFICATION.json')
build = read('evidence/release_1_1/BUILD_RECORD.json')
visual = read('evidence/release_1_1/VISUAL_REVIEW.json')
baseline = read('verification/BASELINE_INTEGRITY.json')
replay = read('verification/baseline_replay/REPLAY_SUMMARY.json')
terminal_review = read('evidence/release_1_1/terminal_repair_review_final.json')
source_bridge = read('evidence/release_1_1/FORMAL_SOURCE_BRIDGE.json')
assert formal['status'] == 'PASS'
assert formal['selected_423_sources_and_interface_unchanged_across_all_replays'] is True
assert formal['final_425_source_revision_hashes_unchanged_during_final_replay_and_reporting'] is True
assert formal['terminal_source_revised_between_failed_and_successful_replays'] is True
assert len(formal['catalogue_private_name_resolutions']) == 4
assert build['status'] == visual['status'] == baseline['result']['status'] == replay['status'] == 'passed'
assert terminal_review['status'] == 'passed_in_reviewed_scope'
assert not terminal_review['open_actionable_findings']
assert terminal_review['source_sha256'] == hashlib.sha256(
    (ROOT / 'formalization/PaperXI/ActualMonomialLocalGlobal.lean').read_bytes()).hexdigest()
assert terminal_review['source_sha256'] == formal['terminal_repaired_sha256']
assert terminal_review['original_kernel_declaration_comparison'] is False
assert source_bridge['status'] == 'passed'
assert source_bridge['selected_modules'] == 423
assert source_bridge['delivered_portable_project_exactly_matches'] is True
assert formal['catalogue_population'] == {'selected_modules': 423, 'unique_names': 4342}
scopes = formal['scopes']
assert all(s['compile_status'] == s['axiom_audit_status'] == 'PASS' for s in scopes.values())
selected = scopes['selected']; terminal = scopes['terminal']; interface = scopes['new_interface']
owned = selected['owned_constant_count']
term_owned = terminal['owned_constant_count']; add_owned = interface['owned_constant_count']

pdf_rows = [
    ('Main monograph', 'Paper_XI_Traditional_v1.1.0.pdf', 'Finite theory, restricted arithmetic results, fifteen construction appendices and references.'),
    ('Core visual guide', 'Paper_XI_Visual_Guide_v1.1.0.pdf', 'Diagrams, examples, conventions and the boundary of the comparison.'),
    ('Lean guide', 'Paper_XI_Lean_Guide_v1.1.0.pdf', 'Fresh verification, the supplementary implication, forty excerpts and the full selected source catalogue.'),
    ('Research progress paper', 'Paper_XI_Conjecture66_Progress_v0.4.0.pdf', 'Preserved Parts I–III: constructions, occurrence obstructions, conductors and marking contracts.'),
    ('Conjecture atlas', 'Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf', 'Thirty-two worked plates and the explicit remaining obligations.')
]
pages = {}
for label, name, purpose in pdf_rows:
    with fitz.open(ROOT / 'publication/pdfs' / name) as doc:
        pages[name] = len(doc)
total_pages = sum(pages.values())
routes = build['reading_routes']; routed_actions = len(build['companion_links'])

ledger = json.loads((BASE / 'paperxi_work/PROGRESS_LEDGER.json').read_text())
prior_ledger = copy.deepcopy(ledger)
ledger.update(schema_version='1.1', ledger_version='1.1.0', checkpoint_id=CHECKPOINT,
              edition_date='2026-10-18', last_updated_utc=NOW)
old_predecessor = ledger['predecessor']
index = read('historical/INDEX.json')
ledger['predecessor'] = {
    'immediate_recovered_release': {
        'filename': Path(index['archive']).name,
        'path': index['archive'],
        'sha256': index['archive_sha256'],
        'manifest_status': baseline['result']['status'],
        'manifest_entries': baseline['result']['manifest_entries'],
        'receipt': 'verification/BASELINE_INTEGRITY.json'},
    'block02_full_source_zip': 'not_recovered',
    'previous_predecessor_record': old_predecessor,
    'publication_strategy': 'Rebuild the three editable active readers; preserve the research companions with documented cover-only cleanup; retain the complete recovered source-and-evidence archive.'}

tasks = {t['id']: t for t in ledger['tasks']}
changes = []
def update_task(identifier, **fields):
    before = copy.deepcopy(tasks[identifier])
    tasks[identifier].update(fields, last_change_checkpoint=CHECKPOINT)
    changes.append({'id': identifier, 'before': before['status'],
                    'after': tasks[identifier]['status'], 'evidence': tasks[identifier]['evidence']})

update_task('P11-C66-001', evidence='Current main Section 16.1 and Proposition 16.3 reviewed against the supplied-candidate contract. The separate SingleCandidateComparison.source implication compiled and passed its axiom audit.',
            boundary_or_next='Conjecture 66 remains open. The comparison uses a supplied candidate, an admissible reference, a separating factor system and the full factor identity for that candidate.')
update_task('P11-C66-008', location='Research Part III Sections 22–25; current evidence/release_1_1/HL11_selected_source_review_2026-10-18.md',
            evidence='Earlier BH99/AP/BH13 selected-source and bounded normalization checks retained. Official full HL11 text retrieved and selected interface checked, with visual inspection of printed pages 143, 144, 147, 148, 149.',
            boundary_or_next='Selected HL11 access gap closed. Preserve exact characteristic, rank, genericity, orbit and normalization hypotheses. No arbitrary-twist H5 or corrected-character occurrence follows.')
update_task('P11-C66-009', boundary_or_next='No general realization or corrected-character occurrence. The original Block45 terminal receipt remains absent; this release supplies a separate fresh replay after reviewed compatibility and local proof repairs, recorded in P11-VERIFY-020.')
publication_evidence = (f'Revised release 1.1.0 has five PDFs and {total_pages} pages: '
    + '/'.join(str(pages[n]) for _,n,_ in pdf_rows)
    + f'. Three readers rebuilt from fingerprinted source; {routed_actions} companion actions resolved. Final page review and package integrity have separate receipts. Main proof-body comparison is 68 total, 65 unchanged, 3 revised. Research companions retain mathematical text with documented cover-only cleanup.')
update_task('P11-PUB-013', location='publication/pdfs; evidence/release_1_1; verification/publication', evidence=publication_evidence,
            boundary_or_next='Reader synchronization is complete. Four arithmetic tasks and the Block02 editable-source gap retain separate statuses.')
update_task('P11-VERIFY-014', location='verification/baseline_replay',
            evidence='Six inherited suites freshly replayed: 24 and 15 publication methods, plus 28/23/15/12 bounded finite methods; 117 methods passed. The exact test-source hashes and original scope limits are retained.',
            boundary_or_next='This bounded replay does not include the separate historical seven-program arithmetic run or establish a universal arithmetic statement. Fresh Lean checks are separately recorded in P11-VERIFY-015 and P11-VERIFY-025.')
update_task('P11-VERIFY-015', task='Fresh Lean compilation under pinned dependencies', status='passed',
            location='verification/lean/RELEASE_VERIFICATION.json and its authenticated per-scope replay lineage',
            evidence='All 423 selected modules freshly compiled with catalogue hashes unchanged. The first partial run passed 421 selected modules plus the interface. The first continuation authenticated those current-session objects and completed the selected sources before the terminal failed. Two subsequent terminal attempts reached the memory limit, including an unchanged-source synchronous retry. Bounded diagnostics isolated an expensive proof conversion. The final continuation authenticated the successful closure and compiled separately reviewed terminal proof repairs. All three aggregate imports passed.',
            boundary_or_next='Lean 4.34.0-rc2 and exact Mathlib/dependency pins. Pinned external caches imported, not a full Mathlib source rebuild. The initial resource-planning stop, diagnostic-driven terminal stop and both memory-limit kills remain failed records. Formal acceptance is conditional on each declaration’s stated hypotheses.')
update_task('P11-PUB-018', location='publication/pdfs; evidence/release_1_1; MANIFEST.json', evidence=publication_evidence,
            boundary_or_next='Publication and restart package complete in documented scope. The separate delivery receipt verifies the exact final archive and extraction; no external peer-review claim.')
update_task('P11-PUB-019', location='historical/INDEX.json and preserved research PDF',
            evidence='Fresh recovery retained the complete v1.0.0 source-and-evidence archive and its 3966-entry verified manifest. It does not contain the complete Block02 editable source archive; the original 33-page reader component remains preserved.',
            boundary_or_next='Actual archive recovery remains necessary. Do not reconstruct source from later claims or describe the preserved cumulative PDF as a unified source rebuild.')
update_task('P11-VERIFY-020', status='passed',
            location='formalization/terminal_original; verification/lean/terminal_repair; verification/lean/axioms_terminal; verification/lean/RELEASE_VERIFICATION.json',
            evidence=f'The recovered ActualMonomialLocalGlobal target freshly compiled after reviewed compatibility and local proof repairs. The missing import alone was insufficient. The final source makes implicit arguments and required standing hypotheses explicit and repairs local proofs. All {term_owned} target-owned logical declarations passed transitive axiom audit. Original, failed intermediate and repaired source fingerprints and exact diffs are retained.',
            boundary_or_next='The review checks intended mathematical conclusions and already-declared hypotheses. No successful original module build is available for a comparison of kernel declarations. This fresh repair/replay does not recover the absent historical receipt. The target remains a restricted tame Weil-side attachment, not a general wild automorphic realization.')

new_tasks = [
    {'id':'P11-PUB-024','task':'Local mathematical corrections and source restoration','status':'completed_selected_scope',
     'location':'CHANGES_v1.1.0.md; evidence/release_1_1/PUBLICATION_SOURCE.diff',
     'evidence':'Focused source and proof review: moving-space phase domain, direct twisted-algebra averaging, F_p pairing, carrier-versus-orbit dimension, scalar holonomy, tame edge cases, approximation index and transition bounds. 68 main proof environments, 65 unchanged bodies, 3 revised.',
     'boundary_or_next':'No blanket certification of every historical proof or classical source. Exact changed statements and proof bodies are separately recorded.'},
    {'id':'P11-VERIFY-025','task':'Complete selected ownership and transitive-axiom audit','status':'passed',
     'location':'verification/lean/axioms_selected_release; verification/lean/axiom_controls_final',
     'evidence':f'All 4342 unique catalogue names resolve to their recorded owners. All {owned} selected-owned logical declarations audited, including private/generated declarations. Compiler-only auxiliary names separately listed. Only Classical.choice, Quot.sound, propext allowed; no forbidden dependency. Two negative controls rejected as intended.',
     'boundary_or_next':'Axiom dependencies establish the formal declarations under their written assumptions. This is not an independent kernel implementation or a realization of uninstantiated arithmetic data.'},
    {'id':'P11-FORMAL-026','task':'One supplied-candidate comparison interface','status':'passed',
     'location':'formalization/PaperXI/SingleCandidateComparison.lean; Lean guide supplement; verification/lean/axioms_interface_final',
     'evidence':f'Additional module freshly compiled; {add_owned} target-owned logical declaration audited. Supplied admissible candidate/reference and equal declared profiles in a separating factor system imply equality in the quotient. No Realization.exists_atom field consumed.',
     'boundary_or_next':'Separate from 423 selected modules and 4342 lexical names. It supplies no arithmetic candidate or proof of H5.'},
    {'id':'P11-PUB-027','task':'Durable source, failure and restart concordance','status':'released_documented_scope',
     'location':'README.md; RELEASE_SCOPE.md; FAILURES_AND_LIMITATIONS.md; CONTINUE_HERE.md; historical/INDEX.json',
     'evidence':'Complete recovered predecessor archive, exact source diff, versioned ledger, current receipts, portable build/replay scripts and searchable historical-path index packaged. Earlier failed attempts and their original meanings preserved.',
     'boundary_or_next':'Append future work as a new checkpoint. General realization, same-candidate H5, corrected occurrence and prescribed native certificate remain distinct open tasks.'}
]
for task in new_tasks:
    task['last_change_checkpoint'] = CHECKPOINT
    ledger['tasks'].append(task)
    changes.append({'id':task['id'],'before':'not separately tracked','after':task['status'],'evidence':task['evidence']})

ledger['history'].append({'checkpoint':CHECKPOINT,'type':'fresh_revision_compile_axiom_audit_and_publication',
                         'date':'2026-10-18',
                         'summary':f'Revised five-reader publication, {total_pages} pages. Local mathematical defects corrected with 68/65/3 main proof-body comparison. Fresh 423-module compilation, {4342} catalogue resolutions and {owned} selected-owned logical declarations audited. Repaired terminal and one-candidate supplement separately compiled/audited. Initial resource-planning stop, terminal diagnostic failure, both later memory-limit kills, repair/retry history and failed audit pilots retained. 117 bounded methods passed; selected HL11 source gap closed; bibliography and final layouts reviewed. Four arithmetic tasks and Block02 source recovery remain open.',
                         'task_changes':changes})
ledger['restart'] = {
    'next_block':'A separately selected arithmetic obligation or Block02 source recovery',
    'priority':'Preserve this release. A concrete continuation is the corrected full-character occurrence problem in Continuation113’s characteristic-zero rank-three candidate. It is distinct from the characteristic-p rank-nine two-cubic-stage branch.',
    'start_with':'Read README.md, RELEASE_SCOPE.md, PROGRESS_LEDGER.md and CONTINUE_HERE.md; verify the manifest; append a new dated checkpoint without rewriting earlier receipts.'}
ledger['current_artifacts'] = {
    'traditional':'publication/pdfs/Paper_XI_Traditional_v1.1.0.pdf',
    'core_visual':'publication/pdfs/Paper_XI_Visual_Guide_v1.1.0.pdf',
    'lean_guide':'publication/pdfs/Paper_XI_Lean_Guide_v1.1.0.pdf',
    'progress_paper':'publication/pdfs/Paper_XI_Conjecture66_Progress_v0.4.0.pdf',
    'visual_atlas':'publication/pdfs/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf',
    'ledger':'PROGRESS_LEDGER.md','machine_ledger':'PROGRESS_LEDGER.json',
    'review':'RELEASE_REVIEW.md','restart':'CONTINUE_HERE.md','build':'tools/build_readers.py',
    'source_changes':'evidence/release_1_1/PUBLICATION_SOURCE.diff',
    'verification':'verification/lean/RELEASE_VERIFICATION.json',
    'package_verifier':'tools/verify_release.py','concordance':'READING_CONCORDANCE.md',
    'historical_index':'historical/INDEX.json'}
ledger['mathematical_completion_percentage'] = None
ledger['reason_no_percentage'] = 'Arithmetic realization, H5, occurrence, native data, formal verification and publication are different tasks; four mathematical tasks remain open.'
jswrite('PROGRESS_LEDGER.json',ledger)
jswrite('ledger/Paper_XI_Progress_Ledger_v1.1.0.json',ledger)

rows='\n'.join(f"| {t['id']} | **{cell(t['task'])}** — `{t['status']}` | {cell(t['location'])}. {cell(t['evidence'])} | {cell(t['boundary_or_next'])} |" for t in ledger['tasks'])
history='\n\n'.join(f"### {h['checkpoint']} — {h['date']}\n\nRecord type: `{h['type']}`.\n\n{h['summary']}" for h in ledger['history'])
status='\n\n'.join(f"**{k}:** {v}" for k,v in ledger['status_contract'].items())
ledger_md=f'''# Paper XI — progress ledger 1.1.0

**Checkpoint:** {CHECKPOINT}. **Date:** 18 October 2026. **Publication:** revised reader and verification release complete in documented scope.

## Current boundary

The five-reader publication contains **{total_pages} PDF pages**. The selected 423-module source population freshly compiled; all 4342 catalogue names resolved, and all {owned} selected-owned logical declarations passed the transitive-axiom audit. The terminal and one-candidate supplement have separate successful results. Six bounded suites passed 117 methods. The selected Henniart–Lemaire source-access gap is closed.

**Four arithmetic tasks remain open:** general realization, full H5 for the same candidate, corrected-character occurrence in the fixed Continuation113 candidate, and the actual native/phase certificate under the stronger prescribed contract. The complete Block02 editable archive remains unrecovered. The original terminal receipt remains unavailable even though a separately repaired target now passes a fresh replay.

The old 23 task IDs and earlier checkpoint history are preserved; four tasks record this edition’s new review and verification scopes. Earlier section/path references retain the context of their component unless this release explicitly updates them. `historical/INDEX.json` resolves those paths without guessing a current directory. The old ledger snapshot remains unchanged under `ledger/`.

## Stable task ledger

| ID | Task / status | Evidence | Boundary / next |
|---|---|---|---|
{rows}

## Checkpoint history

{history}

## Restart

{ledger['restart']['priority']} Read `CONTINUE_HERE.md` for the exact contracts and source locations.

## Status meanings

{status}

No mathematical completion percentage is assigned.
'''
write('PROGRESS_LEDGER.md',ledger_md)
write('ledger/Paper_XI_Progress_Ledger_v1.1.0.md',ledger_md)

pdf_table='\n'.join(f'| [{label}](publication/pdfs/{name}) | {pages[name]} | {purpose} |' for label,name,purpose in pdf_rows)
formal_table='\n'.join(f"| {label} | {s['module_count']} | {s['catalogued_names_resolved']:,} | {s['owned_constant_count']:,} | PASS |" for label,s in [('Selected publication sources',selected),('Recovered terminal',terminal),('One-candidate supplement',interface)])
underfull=len(build['records']['traditional']['diagnostics'])
write('README.md',f'''# Paper XI — complete revised release 1.1.0

## Tame and Wild Packet Geometry for Local Langlands

**Komorebi P. · Operation Komorebi · 18 October 2026**

This package completes the revised publication and verification work for Paper XI. It includes five readers totaling **{total_pages} pages**, their available editable sources, the portable formalization project, current verification evidence, the full recovered predecessor archive and a versioned research ledger. **Conjecture 66 remains open.** The exact surviving arithmetic tasks are stated below and in the paper.

## Start reading

| Reader | PDF pages | Purpose |
|---|---:|---|
{pdf_table}

Start with the main monograph. Its reading guide distinguishes the finite results, restricted arithmetic constructions and remaining general realization. Keep all five PDFs together with these filenames so their companion links work. `READING_CONCORDANCE.md` provides the exact route map. The research companions retain their historical mathematical version labels; this edition removes only the matching cover ornament from those files.

## What changed

The moving-phase statement now uses the correct moving spaces and explicit symplectic action. The twisted-algebra proof uses direct averaging. The pairing convention, carrier-versus-orbit distinction, scalar-holonomy assumptions, rank-one tame conductor and trivial-character Gauss-sum exception are explicit. Appendix notation and transition bounds are repaired. The bibliography, navigation and covers are revised. `CHANGES_v1.1.0.md` explains each change; `evidence/release_1_1/PUBLICATION_SOURCE.diff` records every active-source edit.

The main source contains 68 proof environments, with 65 byte-identical proof bodies and 3 revised bodies compared with v1.0.0. The 423 selected Lean modules and 40 inherited teaching excerpts are unchanged. The additional one-candidate comparison is printed in full in the Lean guide and counted separately.

## Formal verification

| Population | Modules | Catalogue names resolved | Owned logical declarations audited | Result |
|---|---:|---:|---:|---|
{formal_table}

All targets were freshly compiled in this release session using Lean 4.34.0-rc2 and the pinned Mathlib/dependency revisions. The continuations reused only authenticated successful objects from this session; no historical Paper XI objects were used. The first resource-planning stop, terminal diagnostic failure and two memory-limit kills remain recorded. Bounded diagnostics isolated an expensive conversion in the terminal proof. The separately reviewed local proof repairs passed the final compilation. All three aggregate imports and both axiom-audit negative controls passed. Only `Classical.choice`, `Quot.sound` and `propext` are allowed transitive axioms. Actual declaration-level results are in `verification/lean/RELEASE_VERIFICATION.md` and its companion JSON.

These checks establish the formal statements with their written hypotheses. The one-candidate lemma assumes the admissible candidate/reference and equal factor profiles; it supplies no arithmetic existence result. External Mathlib cache objects were imported, not rebuilt. No independent checker or fresh additional full `leanchecker` pass is claimed.

## Other completed checks

Six inherited replay suites passed 117 methods. The complete recovered predecessor passed its 3966-file manifest check. The selected Henniart–Lemaire interface was checked against the official full text. Bibliography provenance now covers the 29 active entries with explicit field-level access limits. All active reader pages received layout review, and source fingerprints, reference destinations, companion routes and package files have exact receipts.

## Remaining mathematics and source recovery

1. Construct the general actual arithmetic realization for all admitted H1–H4 data.
2. Prove the full characterizing H5 identities for that same candidate.
3. Prove corrected full-character occurrence in the fixed Continuation113 candidate and identify its required noncompact extension.
4. Compute the actual native square/section data and honest phases where the stronger fixed-native contract is prescribed.

The complete Block02 editable archive remains unrecovered. The original reader component is preserved in the cumulative research PDF. The original successful terminal receipt remains absent; this release supplies a separately dated successful replay after compatibility and local proof repairs. Its original and failed intermediate sources remain identifiable. `FAILURES_AND_LIMITATIONS.md` preserves these distinctions and the unsuccessful execution history.

## Files and reproduction

| Location | Contents |
|---|---|
| `publication/pdfs/` | The five final readers. |
| `publication/source/` | Editable active reader sources, vector figures, selected Lean catalogue and excerpts. |
| `formalization/` |425 separately scoped module sources, exact toolchain pins and portable bootstrap/replay/audit scripts. |
| `verification/` | Fresh formal, bounded replay, baseline integrity and reader-build records. |
| `evidence/release_1_1/` | Mathematical/source reviews, exact diff, navigation, cover and visual-review evidence. |
| `historical/` | Complete recovered v1.0.0 archive and searchable original-path index. |
| `ledger/` | Unchanged v1.0.0 and new v1.1.0 ledger snapshots. |
| `tools/` | Reader builder, release verifier, targeted cover edit and verifier control harness. |

Read `BUILD.md` for exact commands, `RELEASE_SCOPE.md` for the claim contract and `CONTINUE_HERE.md` for the next mathematical step. The root `MANIFEST.json` fingerprints every other packaged file. The final delivery-verification receipt is supplied outside the ZIP so it can identify and verify the exact archive without a circular self-hash. Preserve the release and append a new dated checkpoint for subsequent work.
''')

write('RELEASE_REVIEW.md',f'''# Paper XI — final internal release review

**Checkpoint:** {CHECKPOINT}. **Date:** 18 October 2026. **Result:** publication and verification complete in the stated scope. **Mathematical endpoint:** Conjecture 66 remains open.

## Executed evidence

| Check | Outcome | Authoritative record |
|---|---|---|
| Recovered predecessor integrity |3966 entries; exact files and SHA-256 match. | `verification/BASELINE_INTEGRITY.json` |
| Bounded inherited replay |6 suites; 117 methods passed. | `verification/baseline_replay/REPLAY_SUMMARY.json` |
| Selected source compilation |423/423 pass; selected sources unchanged. | `verification/lean/RELEASE_VERIFICATION.json` and authenticated replay lineage |
| Catalogue resolution |4342/4342 names resolve to recorded owners. | `verification/lean/axioms_selected_release/` |
| Complete selected logical-declaration audit |{owned} declarations; only the allowed foundational dependencies. | `verification/lean/axioms_selected_release/` |
| Terminal and supplement |Both compile; {term_owned} and {add_owned} logical declarations audited separately. | `verification/lean/RELEASE_VERIFICATION.json` |
| Aggregate imports and negative controls |3 aggregate imports pass; 2 isolated controls rejected as intended. | `verification/lean/` |
| Main mathematical corrections |Focused internal review complete; 68/65/3 proof-body comparison. | `evidence/release_1_1/staging_core_corrections_receipt.json` and source diff |
| Classical source interface |Selected HL11 full-text and page checks complete. | `evidence/release_1_1/HL11_selected_source_review_2026-10-18.md` |
| Bibliography |29 entries have named review provenance; unresolved primary-field limits explicit. | `evidence/release_1_1/BIBLIOGRAPHY_METADATA_REVIEW.md` and inherited B07 audit |
| Three active reader builds |{pages[pdf_rows[0][1]]}/{pages[pdf_rows[1][1]]}/{pages[pdf_rows[2][1]]} pages; source fingerprints and resolved routes recorded. | `evidence/release_1_1/BUILD_RECORD.json` |
| Final page review |Five readers; {total_pages} pages, with preserved companion pages checked for invariance. | `evidence/release_1_1/VISUAL_REVIEW.json` |
| Research cover cleanup |85 path-paint operators on 5 covers; mathematical text/navigation preserved. | `evidence/release_1_1/COVER_MOTIF_REMOVAL.json` |

## Diagnostic and failure handling

The monograph retains {underfull} underfull horizontal-box diagnostics, with final page review; the visual guide and Lean guide diagnostics are separately listed in the build record. Final builds contain no unresolved references or citations, missing characters or overfull boxes. The assembler's {routed_actions} companion link rewrites do not change the rendered page content.

The first source replay is explicitly `PARTIAL_OR_FAIL` after an early resource-planning stop. The first continuation completed the selected modules, then the terminal produced elaboration errors and was deliberately stopped after log inspection. That second run also remains `PARTIAL_OR_FAIL`. The source-revision continuation authenticated the successful closure and recorded the failed terminal's revision and invalidation, but its repaired terminal was killed at the memory limit. An unchanged-source synchronous retry also exhausted memory. Both failed runs and their cgroup evidence remain intact. Bounded diagnostics isolated an expensive conversion in the lower-inclusion witness. The final continuation authenticates the successful closure through all earlier runs and compiles separately reviewed local proof repairs; its separate axiom audit then passes. Audit harness pilots, intermediate terminal checks and runner controls retain their actual outcomes. The final required gates all pass, and no earlier unsuccessful attempt is relabeled. Exact commands, pins, timestamps, source/object fingerprints, declarations and transitive axioms are available in the formal evidence.

## Review boundaries

Source review and compiler acceptance have different scopes. The selected 423-module source population is fixed by the catalogue; the terminal and new comparison lemma are excluded from that count. The main manuscript's additional local corrections are fully shown in the diff; a claim that every old proof remained unchanged would be false. The selected HL11 review closes the specified access gap without asserting arbitrary-twist H5 or occurrence.

The manuscript retains four open arithmetic tasks and the incomplete Block02 editable-source recovery. The original successful terminal receipt is still absent even though the separate fresh replay now passes. The research companions are preserved readers with cover-only edits, not a claimed unified source rebuild. There is no mathematical completion percentage, external peer-review decision, independent kernel implementation or full Mathlib rebuild claim.

The root manifest and the portable verifier bind the final package files. The separate final delivery receipt records exact archive CRC, membership and file hashes after extraction. This internal release review supports the completed publication scope and leaves the open research tasks visible.
''')

route_rows='\n'.join(f"| `{cell(k)}` | [{cell(v['file'])}](publication/pdfs/{v['file']}#page={v['page']}) | {v['page']} | {cell(v.get('printed_page','—'))} | `{cell(v.get('label','fixed preserved-reader page'))}` |" for k,v in sorted(routes.items()))
write('READING_CONCORDANCE.md',f'''# Paper XI — reading and source concordance

All page numbers in the PDF-page column count the cover as page 1. Printed page labels can differ. The actual destinations were resolved from the final source build; historical obligation 66 and current comparison remain separate routes.

## Reader choices

| Reader | PDF pages | Purpose |
|---|---:|---|
{pdf_table}

The main manuscript's Section 16.1 states the realization contract. Conjecture 66 and the surviving one-candidate comparison are distinct statements within it. The research progress paper's opening contract and Parts II–III retain the later occurrence, conductor and native-marking analysis. Atlas plate V30 specifies the missing native certificate; V32 states the current frontier. The Lean guide's new supplement states exactly what its supplied-candidate implication assumes.

## Exact companion routes

The {len(routes)} declared route keys produce {routed_actions} resolved companion-link actions in the three rebuilt readers. Some keys are aliases for the same destination. Preserved-reader routes have fixed PDF pages; active-source routes also retain their TeX labels and printed page values. Keep all five PDFs together with their delivered filenames.

| Route key | Destination file | PDF page | Printed page | Source label or route type |
|---|---|---:|---|---|
{route_rows}

## Historical sources

`historical/INDEX.json` lists every member of the complete recovered v1.0.0 source-and-evidence archive and includes a `by_basename` map. Duplicate basenames retain all original component paths. Extract that archive separately when using its older scripts and relative links; those historical paths are not current workspace directories.

The current publication sources, source-change index and portable formalization project are directly available in this release. The missing complete Block02 editable archive is an explicit exception. The final ledger gives the current status without changing the meaning of earlier receipts.
''')
print(json.dumps({'status':'written_from_passed_receipts','total_pages':total_pages,'pdf_pages':pages,
                  'ledger_tasks':len(ledger['tasks']),'open_mathematical_tasks':[t['id'] for t in ledger['tasks'] if t['status']=='open'],
                  'selected_owned_logical_declarations':owned,'terminal_owned_logical_declarations':term_owned,
                  'supplement_owned_logical_declarations':add_owned,'companion_routes':len(routes),'companion_actions':routed_actions},indent=2))

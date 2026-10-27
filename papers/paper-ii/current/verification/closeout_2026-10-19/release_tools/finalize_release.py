#!/usr/bin/env python3
"""Finalize Paper II only after separate formal and publication gates pass."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--verification', type=Path, required=True)
args = parser.parse_args()
root = args.root.resolve()
receipt_path = args.verification.resolve()
assert receipt_path.is_relative_to(root)
receipt = read(receipt_path)
assert receipt['status'] == 'PASS'
assert all(row['passed'] for row in receipt['checks'])
assert receipt['production_module_count'] == 75
assert receipt['owned_logical_total'] == receipt['logical_checked_count']
assert receipt['replay_exact_name_match']
assert receipt['replay_starting_environment_excludes_project_modules']
correspondence = root / 'formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json'
scope = read(correspondence)
assert scope['status'] == 'FINAL_SOURCE_BOUND_CORRESPONDENCE_53_OF_53'
assert scope['final_proof_counts']['kernel_checked_semantically_accepted_scope'] == 53
assert not scope['known_open_bridge_labels']
assert scope['kernel_binding']['verification_sha256'] == sha(receipt_path)
frozen_manifest = root / scope['frozen_formal_binding']['manifest']
assert sha(frozen_manifest) == scope['frozen_formal_binding']['manifest_sha256']
formal_root = root / 'formal/current'
manifest_rows = read(frozen_manifest)
assert len(manifest_rows) == 75
assert {str(p.relative_to(formal_root)) for p in formal_root.rglob('*.lean')} == {r['source'] for r in manifest_rows}
for row in manifest_rows:
    assert sha(formal_root / row['source']) == row['source_sha256'], row['source']
for relative, expected in scope['current_chapter_sha256'].items():
    assert sha(root / relative) == expected, relative
publication_path = root / 'publication/FINAL_PUBLICATION_REVIEW.json'
publication = read(publication_path)
assert publication['state'] == 'PUBLICATION_READY_FOR_RECORDED_SCOPE'
assert publication['current_correspondence_sha256'] == sha(correspondence)
for row in publication['pdfs']:
    assert sha(root / row['path']) == row['sha256']
qa_path = root / publication['page_qa']['path']
assert sha(qa_path) == publication['page_qa']['sha256']
qa = read(qa_path)
assert qa['all_pages_rendered'] and qa['visual_review'] == 'PASS'

def binding(p):
    return {'path': str(p.relative_to(root)), 'sha256': sha(p)}


old = read(root / 'verification/closeout_2026-10-19/history/baseline_root/RELEASE_STATUS.json')
old_computation = root / old['bounded_computation']['path']
assert sha(old_computation) == old['bounded_computation']['sha256']
rebound = root / 'verification/closeout_2026-10-19/computation/COMPUTATION_REBIND.json'
assert rebound.is_file(), 'Current finite computation input rebind must be present'
rebound_data = read(rebound)
assert rebound_data['status'] == 'PASS_FOR_RETAINED_FINITE_EVIDENCE_BINDINGS'
assert rebound_data['current_input_hashes_rechecked'] == rebound_data['current_input_hashes_matched'] == 101
assert not rebound_data['fresh_numerical_run']
now = datetime.now(timezone.utc).isoformat()
status = {
    'schema': 'komorebi.paper-ii.reviewed-release/2',
    'edition_date': '2026-10-19', 'version': '1.1.0', 'created_utc': now,
    'author': 'Komorebi P.', 'state': 'TECHNICALLY_READY_FOR_RELEASE',
    'decision': 'All 53 enumerated proof-level manuscript scopes have accepted source correspondence and exact-source kernel replay. All three reading editions passed publication review.',
    'all_enumerated_proof_scopes_covered': True,
    'publication': dict(binding(publication_path), total_pages=publication['total_pages'],
                        all_page_visual_review='PASS', documents=publication['pdfs']),
    'formal': {
        'verification': binding(receipt_path), 'correspondence': binding(correspondence),
        'toolchain': receipt['lean_version'],
        'mathlib_revision': 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
        'fresh_production_modules': receipt['production_module_count'],
        'owned_declarations': receipt['owned_total'],
        'kernel_replayed_logical_declarations': receipt['logical_checked_count'],
        'reviewed_runtime_helpers': receipt['generated_runtime_helper_count'],
        'negative_controls': receipt['negative_controls'],
        'upstream_duplicate_fresh_body_rechecks': receipt['upstream_duplicate_body_recheck_count'],
        'manuscript_records': 81, 'proof_level_records': 53,
        'accepted_complete_scopes': 53, 'partial_scopes': 0,
        'mapped_owned_and_replayed_names': scope['kernel_binding']['mapped_declaration_count'],
        'open_statements': [], 'remaining_bridges_within_enumerated_scopes': [],
        'limitations': receipt['limits'],
        'scope_boundary': 'Counts cover the 53 enumerated proof-level records under their displayed hypotheses. They do not certify every explanatory sentence or assert a general admissible-contour existence theorem outside those records. Canonical values are defined whenever the relevant admissible data exist.'
    },
    'bounded_computation': dict(old['bounded_computation'], current_input_rebind=binding(rebound),
                               fresh_numerical_rerun=False),
    'license': {
        'project_license': 'NOT_SELECTED',
        'status': 'Existing copyright and permission status retained. No project license assigned by this closeout.',
        'source_status': 'source/canonical_v1.2.1/LICENSE_STATUS.md',
        'third_party_notices': 'LICENSES/THIRD_PARTY_NOTICES.md'
    },
    'historical_evidence': 'Predecessor maps, unrecovered October16 claims and failed development/replay attempts are retained and identified as history. The current decision uses only the successful exact-source receipt above.',
    'integrity_manifest': 'MANIFEST_SHA256.json',
    'packaging_exclusions': ['__pycache__ directories', '*.pyc']
}
write(root / 'RELEASE_STATUS.json', status)
ledger_path = root / 'CLOSEOUT_LEDGER.json'
ledger = read(ledger_path)
write(root / 'verification/closeout_2026-10-19/history/CLOSEOUT_LEDGER_v0.9.0.json', ledger)
ledger.update(version='1.1.0', status='TECHNICAL_CLOSEOUT_COMPLETE', completed_utc=now, pending=[],
              final_release=binding(root / 'RELEASE_STATUS.json'))
ledger['ordered_events'][-1]['result'] = 'PASS' if receipt_path.parent.name == 'attempt02_m4096' else 'SUPERSEDED; see subsequent recorded attempts'
ledger['ordered_events'] += [
    {'event': 'final_exact_source_replay', 'result': 'PASS', 'evidence': binding(receipt_path),
     'production_modules': receipt['production_module_count'], 'logical_replays': receipt['logical_checked_count'],
     'negative_controls': receipt['negative_controls']},
    {'event': 'source_correspondence_acceptance', 'result': 'PASS_53_OF_53', 'evidence': binding(correspondence)},
    {'event': 'publication_review', 'result': 'PASS_ALL_PAGES', 'evidence': binding(publication_path)}
]
ledger['next_unfinished_core_paper'] = 'III; identified from the October19 twelve-paper review, not modified by this closeout'
ledger['license_status'] = status['license']
integration = read(root / 'verification/closeout_2026-10-19/SOURCE_INTEGRATION.json')
ledger['new_module_bindings'] = [
    {'module': item['module'], 'path': item['target'], 'sha256': item['sha256'],
     'strict_aggregate_compile': 'PASS', 'owned_logical_kernel_replay': 'PASS'}
    for item in integration['new_modules']]
ledger['completed_obligations'] = [
    {'record_id': row['record_id'],
     'statement_sha256': row['current_source']['statement_sha256'],
     'proof_sha256': row['current_source']['proof_sha256'],
     'acceptance': row['current_exact_semantic_acceptance'],
     'current_evidence': row['current_evidence']}
    for row in scope['records']
    if row['record_id'] in ['thm:holomorphic_defect', 'cor:exact_compatibility']]
ledger['proof_route'] = [
    'Actual finite tagged Riemann–Stieltjes sums, arbitrary fine partitions and uniqueness.',
    'Continuous monotone transport, including flat intervals, and normalized arclength for every continuous BV path.',
    'Actual velocity integral bounded by original geometric length, including constant paths and empty cycles.',
    'Scalar primitive annihilation, winding local constancy and vanishing at infinity.',
    'Banach divided-difference holomorphy, exterior Cauchy transform decay and pair Dixon gluing.',
    'General equal-winding Cauchy comparison on arbitrary open domains.',
    'Canonical admissible-cycle independence, actual original-contour defect formula and separate supremum norm estimate.',
    'Canonical naturality with independent endpoint contours, followed by arbitrary-depth tower compatibility.'
]
ledger['review_provenance'] = {
    'retained_scopes': 51, 'newly_reviewed_scopes': 2,
    'semantic_acceptance': scope['semantic_acceptance_binding'],
    'source_and_runtime_summary': binding(root / 'verification/closeout_2026-10-19/FINAL_VERIFICATION_SUMMARY.json'),
    'finite_evidence_rebind': binding(rebound), 'all_page_publication_review': binding(publication_path)}
write(ledger_path, ledger)
summary = f"""PAPER II — COMPLETED REVIEWED EDITION, 19 OCTOBER 2026
Komorebi P. | version 1.1.0

Start with papers/Paper_II_Traditional_Final.pdf. The visual and Lean guides
are synchronized companion editions. Editable sources are under editable/.

All 53 enumerated proof-level records have accepted exact-source semantic
correspondence and kernel replay. There are zero partial scopes in this
denominator. The two newly completed scopes are Theorem 11.6 and the
holomorphic part of Corollary 11.10. The Lean guide explains the rectifiable
integral construction, Banach Cauchy comparison and canonical naturality.

Fresh strict verification: {receipt['production_module_count']} production modules,
{receipt['logical_checked_count']} logical declarations replayed, {receipt['negative_controls']} negative controls passed.
Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The pinned upstream cache was authenticated and reused. Replay uses Lean's
own kernel. Semantic correspondence is a separate reviewed gate.

Current formal map:
  formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json
Successful replay:
  {receipt_path.relative_to(root)}
Publication evidence:
  publication/FINAL_PUBLICATION_REVIEW.json

The exact declared hypotheses remain in force. Canonical values are defined
when relevant admissible data exist. No broader admissible-contour existence
theorem or certification of every explanatory sentence is claimed.

The original manuscript statements and proofs are unchanged. The geometric
bound uses integrated speed at most the original contour length; equality is
not needed. Compatibility permits independent admissible endpoint contours.

The earlier claim of a completed October16 source package could not be
recovered. It is preserved as historical context, not evidence. This closeout
reconstructed thirteen actual new source modules and replayed the resulting
75-module release. Failed checks are retained, including the first full run
that exceeded Lean's 3072 MiB interpreter budget.

All {publication['total_pages']} current PDF pages passed rendering and visual review.
The baseline finite computation contract is retained with current input hashes
rechecked; no new numerical experiment or universal computational proof is
claimed. Read RELEASE_STATUS.json and CLOSEOUT_LEDGER.json for exact bindings.

No project license has been selected. The existing permission status remains
in source/canonical_v1.2.1/LICENSE_STATUS.md. Third-party notices are retained.

Earlier dated source, maps, reports and status files are historical records.
The portable runtime is external and is not bundled into this archive.
No other paper was changed. Paper III is next chronologically.
"""
(root / 'READ_FIRST.txt').write_text(summary)
(root / 'CONTINUE_HERE.txt').write_text(summary + '\nREPRODUCTION\nSee verification/closeout_2026-10-19/ for the frozen manifest, strict driver,\nruntime identity, logs, semantic reviews and full source input bindings.\nPDF rebuild: python3 publication/build_current.py --map\nformal/coverage/Paper_II_Current_Correspondence_2026-10-19.json\n--edition-date 2026-10-19 (put the command on one line).\n')
# The publication builder owns its generated root README and edition state.
# Add the package closeout decision without overwriting build provenance.
with (root / 'README.txt').open('a') as f:
    f.write('\nTECHNICAL CLOSEOUT, 19 OCTOBER 2026\nAll 53 enumerated proof scopes are accepted. Read READ_FIRST.txt and\nRELEASE_STATUS.json for the final scope, reproduction and license status.\n')
with (root / 'MONOGRAPH_CHANGELOG.txt').open('a') as f:
    f.write('\n19 October 2026, v1.1.0: completed the two analytic proof scopes through\n13 additional Lean modules, independently reviewed and strictly replayed.\nRebuilt and visually reviewed all three editions. Manuscript theorem\nstatements and proof text unchanged. Historical failures retained.\n')
(root / 'REVIEW_NOTES.txt').write_text(
    'CURRENT CLOSEOUT REVIEW — 19 OCTOBER 2026\n\n'
    'All 53 enumerated proof-level manuscript scopes are accepted, with zero\n'
    'partial scopes. The previous 51 accepted scopes retain their prior\n'
    'semantic reviews and unchanged sources. Two analytic scopes received\n'
    'new independent reviews. All 75 production modules and all owned logical\n'
    'declarations passed the separate fresh strict aggregate kernel replay.\n\n'
    'Semantic reports, their exact source snapshots and compiler receipts are\n'
    'under verification/closeout_2026-10-19/semantic/. The new guide chapter\n'
    'also passed mathematical prose review. Publication review covers every\n'
    'page of the three exact reading PDFs. RELEASE_STATUS.json binds these\n'
    'separate gates. The root checksum manifest binds package bytes.\n\n'
    'Earlier root review notes are retained at\n'
    'verification/closeout_2026-10-19/history/baseline_root/REVIEW_NOTES.txt.\n'
    'Earlier statements of open bridges describe their original source state.\n')
for folder in list(root.rglob('__pycache__')):
    if folder.is_dir():
        shutil.rmtree(folder)
for file in root.rglob('*.pyc'):
    file.unlink()
print(json.dumps({'state': status['state'], 'formal': status['formal'],
                  'publication_pages': publication['total_pages']}, indent=2))

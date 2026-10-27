"""Generate release records only after the coordinator binds the final reviews."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'integration/runs/clean_limits_01'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

rec = read(RUN / 'receipt.json')
post = read(RUN / 'postflight.json')
signoff = read(ROOT / 'records/FINAL_AUDIT_SIGNOFF.json')
assert read(ROOT / 'PROGRESS_LEDGER.json')['status'] != 'ACCEPTED', 'Acceptance is immutable; do not rerun'
assert rec['status'] == post['status'] == signoff['status'] == 'PASS'
assert post['run_receipt_sha256'] == sha(RUN / 'receipt.json')
assert signoff['formal_receipt_sha256'] == sha(RUN / 'receipt.json')
assert signoff['postflight_sha256'] == sha(RUN / 'postflight.json')
assert all(post['gates'].values())
assert all(c['passed'] and not c['timeout'] for c in rec['commands'])
for name, digest in signoff['review_sha256'].items():
    assert sha(ROOT / name) == digest, name
frozen = read(ROOT / 'records/FROZEN_OVERLAY.json')['source_sha256']
assert {str(p.relative_to(ROOT / 'formal')): sha(p) for p in (ROOT / 'formal').rglob('*') if p.is_file()} == frozen
new_rows = read(RUN / 'new_declarations.json')
sources = {name: rec['source_snapshot_sha256'][name] for name in frozen if name.startswith('KomorebiSpace/')}
assert all(sha(RUN / 'source' / name) == digest for name, digest in sources.items())
explicit = sum(len(re.findall(r'^\s*(?:theorem|lemma)\s+', (RUN / 'source' / name).read_text(), re.M)) for name in sources)
definitions = sum(len(re.findall(r'^\s*def\s+', (RUN / 'source' / name).read_text(), re.M)) for name in sources)
assert (explicit, definitions) == (31, 2)
assert len(new_rows) == rec['new_axiom_declarations']
assert rec['inherited_declarations_preserved'] and rec['parent_declarations'] == 4935
assert rec['axiom_declarations'] == 4935 + len(new_rows)
counts = dict(Counter(c['kind'] for c in rec['controls']))
complete = [f'WR{i:02}' for i in [1,2,3,4,5,6,7,8,9,13,14,16]]
remaining = ['WR10', 'WR11', 'WR12', 'WR15']
now = datetime.now(timezone.utc).isoformat()
evidence_names = [
    'reviews/WR08_WR09_WR16_MATH_AUDIT.md', 'reviews/VERIFIER_REVIEW.md',
    'reviews/reviewed_helpers.json', 'reviews/PACKAGING_SCRIPT_REVIEW.md',
    'formal/tests/control_manifest.json', 'records/FINAL_AUDIT_SIGNOFF.json',
]
evidence = {name: sha(ROOT / name) for name in evidence_names}
summary = {
    'status': 'PASS', 'checkpoint': 'KS-v1.11.0-WR08-WR09-WR16-complete',
    'accepted_utc': now, 'formal_receipt_sha256': sha(RUN / 'receipt.json'),
    'postflight_sha256': sha(RUN / 'postflight.json'),
    'axiom_report_sha256': sha(RUN / 'axioms.json'),
    'new_declarations_sha256': sha(RUN / 'new_declarations.json'),
    'inventory_sha256': rec['inventory_sha256'],
    'runtime_snapshot_sha256': rec['runtime_snapshot_sha256'],
    'compile_targets': rec['compile_targets'], 'production_modules': rec['production_modules'],
    'entrypoints': rec['entrypoints'], 'explicit_theorem_lemma_count': rec['explicit_theorem_lemma_count'],
    'new_explicit_theorems': explicit, 'new_named_public_declarations': explicit + definitions,
    'axiom_declarations': rec['axiom_declarations'], 'new_axiom_declarations': len(new_rows),
    'inherited_declarations': 4935, 'axiom_union': rec['axiom_union'],
    'controls': counts, 'control_files': len(rec['controls']), 'recorded_commands': len(rec['commands']),
    'runtime_file_count': rec['runtime_file_count'], 'clean_project_build': True,
    'dependencies_rebuilt': False, 'new_source_sha256': sources,
    'acceptance_evidence_sha256': evidence,
    'scope': 'Complete named WR08, WR09 and WR16 statements and supporting interfaces; Lean-focused continuation.',
    'publication': 'The unchanged v1.10.0 PDF is historical; no new PDF is claimed.',
    'trust_boundary': rec['trust_boundary'],
}
write(ROOT / 'VERIFICATION_SUMMARY.json', summary)
write(ROOT / 'FORMAL_COVERAGE.json', {
    'status': 'PASS', 'complete': complete, 'partial': [], 'written_only': remaining,
    'new_groups': {'WR08': ['RegularizationLimits', 'RegularizationStrongLimit'],
                   'WR09': ['RegularizationNoiseLimits'], 'WR16': ['RegularizationNoiseLimits']},
    'new_statement_audit': 'reviews/WR08_WR09_WR16_MATH_AUDIT.md',
    'new_full_types': 'integration/runs/clean_limits_01/new_declarations.json',
    'new_source_sha256': sources, 'formal_receipt_sha256': summary['formal_receipt_sha256'],
    'scope': 'Every clause of the principal numbered theorem groups; adjacent diagonal applications and executable refinement remain separate.'})
write(ROOT / 'PROGRESS_LEDGER.json', {
    'checkpoint': summary['checkpoint'], 'parent': 'KS-v1.10.0-WR03-WR05-complete',
    'status': 'ACCEPTED', 'accepted_utc': now,
    'formal_receipt_sha256': summary['formal_receipt_sha256'], 'postflight_sha256': summary['postflight_sha256'],
    'complete_formal_groups': complete, 'partial_formal_groups': [], 'open_formal_groups': remaining,
    'acceptance_evidence_sha256': evidence,
    'completed': ['Full WR08 positive-parameter limit alternative',
                  'Full WR09 sharpness and noisy parameter-choice convergence',
                  'Full WR16 inexact stopping-rule limit and every-index certificate',
                  'Independent exact-statement and verification audits',
                  'Fresh cumulative project replay and all-declaration axiom audit'],
    'remaining_limits': [], 'next_restart': 'Freeze all WR15 coordinate-covector invariance clauses; then the connected WR10-WR12 infinite diagonal block. See NEXT_RESEARCH_BLOCK.md.',
    'separate_remaining_work': ['Global independent monograph audit', 'Executable certificate refinement',
                                'Application-specific operator/norm/kernel identification',
                                'Monograph and companion-guide synchronization'],
    'events': 'records/EVENTS.jsonl', 'failures_retained': True,
    'publication_unchanged': True,
})
progress = f'''# Komorebi Space — Lean progress v1.11.0

Accepted checkpoint: **{summary['checkpoint']}**. Parent: v1.10.0. Acceptance recorded {now}.

## Completed in Lean

| Group | Result |
| --- | --- |
| WR08 | Full regularization alternative: fitted images approach the projection, residual norms approach the floor, weighted penalty vanishes, corrections converge strongly to the constructed unique minimum-norm preimage when attained, and norms tend to infinity otherwise. |
| WR09 | Sharp coefficient proved with a scalar operator, plus convergence for the entire positive noise-level family under the stated parameter rule. |
| WR16 | Strong convergence of inexact proposals, with the full three-term error certificate at every index. |

The three modules add **{explicit} explicit theorems and {explicit + definitions} named public declarations**. They use the full positive real-parameter filter and the existing actual Hilbert norms. No closed-range, finite-dimensionality, separability, injectivity, or zero-floor assumption was added. WR09 includes the scalar sharpness clause; completing only its limiting statement would have left the group incomplete.

## Verification

- Fresh cumulative compilation: **{rec['compile_targets']} targets**, comprising **{rec['production_modules']} production modules and three roots**, from an empty project object directory.
- Cumulative explicit theorem/lemma count: **{rec['explicit_theorem_lemma_count']:,}**. Complete environment audit: **{rec['axiom_declarations']:,} declarations**, including **{len(new_rows)} new declarations** and every one of the {rec['parent_declarations']:,} inherited identities.
- Only `propext`, `Classical.choice`, and `Quot.sound` occur in the accepted axiom union.
- **{len(rec['controls'])} control files**: {counts['positive']} positive, {counts['negative']} intended compiler rejections, and {counts['policy']} policy rejections. All **{len(rec['commands'])} recorded commands** passed their required outcomes.
- Independent printed/source and complete exported-type review passed, followed by independent terminal evidence reconstruction. Sources, project objects and **{rec['runtime_file_count']:,} runtime/cache files** passed the recorded endpoint checks.

## Mistakes found and corrected

The mathematical arguments did not need weaker targets. Numbered attempts preserve compiler failures involving deprecated API names, type inference, strict linting, documentation placement, scalar simplification, and triangle-inequality expression order, followed by their corrected successful attempts. Positive controls also exposed simplification and lemma-name mistakes; those were corrected. Two control drafts were strengthened before freezing, including a parameter-choice test that now discharges the exact-data bias limit rather than assuming it.

The initial exporter probe put printer options in the wrong Lean monad and was rejected. The corrected probe succeeded. The new exporter still audits every declaration and fully prints every new type; selected inherited types use readable printing. This removes large inherited proof-term expansion while preserving the complete axiom check and the accepted historical full report. Probes remain explicitly labeled development evidence. The accepted cumulative replay was separate and began with no project objects.

The strong-convergence route uses the accepted energy identity to bound squared correction distance by the squared norm deficit. The frequently-bounded WR01 theorem proves the lower norm limit directly for the full filter. This closes the entire parameter-family statement without an unproved sequential-to-filter step.

## Remaining gaps and restart

**Twelve of sixteen principal WR groups are complete. No group remains partially formalized.** WR10–WR12 and WR15 remain written-only. WR15's invariant coordinate certificate is the proposed next bounded block; WR10–WR12 form the larger infinite-diagonal-model and rate block. Exact obligations are in `NEXT_RESEARCH_BLOCK.md`.

The independent global monograph audit, refinement of executable certificate code, application-specific model identification, and synchronized publication/companion-guide editions remain separate. This is a Lean-focused continuation: the accepted v1.10.0 PDF is preserved as historical material, not relabeled as a new edition.

## Evidence and trust

Formal receipt SHA-256: `{summary['formal_receipt_sha256']}`. Postflight SHA-256: `{summary['postflight_sha256']}`. `VERIFICATION_SUMMARY.json` binds the source, exports and reviews; `records/EVENTS.jsonl` retains the event history. Every predecessor archive file and every new development attempt are retained in the release package, excluding reproducible compiled objects and runtime binaries.

The Lean compiler/kernel, permitted standard axioms, pinned external caches and supporting runtime remain trusted. Dependencies were not rebuilt from source. Endpoint hashes cannot detect a temporary change restored between checks. The focused audit does not certify every sentence or executable example of the monograph.
'''
(ROOT / 'PROGRESS_LEDGER.md').write_text(progress)
with (ROOT / 'records/EVENTS.jsonl').open('a') as f:
    f.write(json.dumps({'event': 'E009', 'utc': now, 'kind': 'formal_block_accepted',
                       'checkpoint': summary['checkpoint'], 'formal_receipt_sha256': summary['formal_receipt_sha256'],
                       'postflight_sha256': summary['postflight_sha256'], 'acceptance_evidence_sha256': evidence,
                       'coverage_complete': complete, 'coverage_written_only': remaining}) + '\n')
print(json.dumps({k: summary[k] for k in ['status', 'checkpoint', 'compile_targets', 'axiom_declarations',
                                        'new_axiom_declarations', 'recorded_commands']}, indent=2))

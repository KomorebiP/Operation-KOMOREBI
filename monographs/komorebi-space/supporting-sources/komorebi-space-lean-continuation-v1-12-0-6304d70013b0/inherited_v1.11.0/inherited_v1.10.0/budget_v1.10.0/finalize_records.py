#!/usr/bin/env python3
"""Write the release ledger only after formal and publication gates have passed."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
RUN = ROOT/'integration/runs/clean_budget_01'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, data):
    (ROOT/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')

def main():
    events = ROOT/'records/EVENTS.jsonl'
    old = [json.loads(l) for l in events.read_text().splitlines() if l.strip()]
    if any(e['state'] == 'budget_release_accepted' for e in old):
        raise SystemExit('Acceptance event already exists; do not overwrite a released checkpoint')
    rec = json.loads((RUN/'receipt.json').read_text())
    post = json.loads((RUN/'postflight.json').read_text())
    publication = WORK/'monograph_v1.10.0/PUBLICATION_VERIFICATION.json'
    pub = json.loads(publication.read_text())
    if not rec['status'] == post['status'] == pub['status'] == 'PASS':
        raise SystemExit('Formal, terminal, and publication gates must all pass')
    rh, ph = sha(RUN/'receipt.json'), sha(RUN/'postflight.json')
    if not post['run_receipt_sha256'] == rh == pub['formal_receipt_sha256']:
        raise SystemExit('Acceptance evidence does not bind one run')
    freeze = json.loads((ROOT/'records/DEVELOPMENT_FREEZE.json').read_text())['source_sha256']
    if not all(sha(ROOT/p) == h for p,h in freeze.items()):
        raise SystemExit('Current source differs from the development freeze')
    if not all(rec['source_snapshot_sha256'][p.removeprefix('formal/')] == h for p,h in freeze.items()):
        raise SystemExit('Accepted source differs from the development freeze')
    counts = dict(collections.Counter(c['kind'] for c in rec['controls']))
    complete = ['WR01','WR02','WR03','WR04','WR05','WR06','WR07','WR13','WR14']
    partial = ['WR09','WR16']
    remaining = ['WR08','WR10','WR11','WR12','WR15']
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence_names = ['reviews/WR03_WR05_PRINTED_PROOF_AUDIT.md',
                      'reviews/WR03_WR05_FORMAL_STATEMENT_AUDIT.md',
                      'reviews/VERIFIER_REVIEW.md','reviews/reviewed_helpers.json',
                      'formal/tests/control_manifest.json']
    evidence = {p:sha(ROOT/p) for p in evidence_names}
    summary = {'status':'PASS','checkpoint':'KS-v1.10.0-WR03-WR05-complete',
               'formal_receipt':'budget_v1.10.0/integration/runs/clean_budget_01/receipt.json',
               'formal_receipt_sha256':rh,'postflight_sha256':ph,
               'production_modules':rec['production_modules'],'compile_targets':rec['compile_targets'],
               'entrypoints':rec['entrypoints'],'explicit_theorem_lemma_count':rec['explicit_theorem_lemma_count'],
               'new_explicit_theorems':39,'new_named_public_declarations':43,
               'axiom_declarations':rec['axiom_declarations'],'new_axiom_declarations':rec['new_axiom_declarations'],
               'axiom_union':rec['axiom_union'],'controls':counts,'control_files':len(rec['controls']),
               'command_count':len(rec['commands']),'runtime_files_hashed':rec['runtime_file_count'],
               'started_utc':rec.get('started_utc'),'finished_utc':rec.get('finished_utc'),
               'lean_executed':rec['lean_executed'],'initial_project_objects':rec['initial_project_objects'],
               'source_unchanged_during_run':rec['source_unchanged_during_run'],
               'runtime_unchanged_during_run':rec['runtime_unchanged_during_run'],
               'objects_unchanged_after_compile':rec['objects_unchanged_after_compile'],
               'new_source_sha256':freeze,'acceptance_evidence_sha256':evidence,
               'publication_verification_sha256':sha(publication),'pdf_sha256':pub['pdf_sha256'],
               'complete_formal_groups':complete,'partial_formal_groups':partial,'open_formal_groups':remaining,
               'trust_boundary':'Official Lean compiler/kernel, standard axioms, pinned precompiled external dependencies, system runtime and path adapter remain trusted. Project sources were rebuilt cleanly; dependencies were not rebuilt from source. Endpoint hashes do not detect transient restored changes.'}
    write('VERIFICATION_SUMMARY.json',summary)
    ledger = {'checkpoint':summary['checkpoint'],'parent':'KS-v1.9.0-full-monograph-proofread',
              'parent_archive_sha256':'f04fb35e1473800c604b25a1c883f6cdc937a31f9332d1ac99e8467c7a05fec9',
              'status':'ACCEPTED','accepted_utc':now,'formal_receipt_sha256':rh,'postflight_sha256':ph,
              'publication_verification_sha256':sha(publication),'publication_pdf_sha256':pub['pdf_sha256'],
              'complete_formal_groups':complete,'partial_formal_groups':partial,'open_formal_groups':remaining,
              'acceptance_evidence_sha256':evidence,
              'completed':['Full WR03 profile, attainment, shape, real-budget limit and equivalences',
                           'Full WR04 sharp attained dual maximum and strict exclusion',
                           'Full WR05 common-space perturbation bound and nominal certificates',
                           'Independent printed-proof and exact formal-statement audits',
                           'Fresh cumulative project compilation, all-declaration axiom audit, 30 intended control outcomes',
                           'Full monograph coverage synchronization and recorded projection/residual correction'],
              'remaining_limits':['WR09','WR16'],'next_restart':'Freeze and formalize every WR08 clause, especially strong convergence to the minimum-norm preimage versus norm divergence. Then finish WR09/WR16 limits. See budget_v1.10.0/NEXT_RESEARCH_BLOCK.md.',
              'separate_remaining_work':['Global independent monograph proof audit','Executable certificate refinement proof','Application-specific operator/norm/kernel identification','Updated historical companion guides'],
              'events':'budget_v1.10.0/records/EVENTS.jsonl','failures_retained':True}
    write('PROGRESS_LEDGER.json',ledger)
    write('FORMAL_COVERAGE.json',{'status':'PASS','complete':complete,'partial':partial,'written_only':remaining,
                                'new_groups':{'WR03':['BudgetProfile','BudgetProfileGeometry'],'WR04':['BudgetDuality'],'WR05':['BudgetRobustness']},
                                'new_statement_audit':'reviews/WR03_WR05_FORMAL_STATEMENT_AUDIT.md',
                                'new_full_types':'integration/runs/clean_budget_01/new_declarations.json',
                                'new_source_sha256':freeze,'formal_receipt_sha256':rh,
                                'scope':'Every principal numbered theorem clause. Adjacent explanatory uniqueness claims and illustrations are not all assigned new public declarations.'})
    text = f'''# Komorebi Space — progress v1.10.0

Accepted checkpoint: **{summary['checkpoint']}**. Parent: v1.9.0 full monograph. Acceptance recorded {now}.

## Completed in this block

| Group | Result |
| --- | --- |
| WR03 | Every nonnegative budget has an attained minimum; monotonicity, convexity, the full Lipschitz estimate, the real-budget limit, and both exact feasibility equivalences are formalized. |
| WR04 | The dual formula is an attained maximum at every budget, with a unit-ball witness and strict exclusion certificate. |
| WR05 | Both profiles use one correction space and ball; the full operator/data perturbation allowance and nominal witness certificates are formalized. |

The four modules add **39 explicit theorems and 43 named public declarations**. The actual complete types were independently reviewed. No finite-dimensionality, separability, closed-range, injectivity, positive-budget, or assumed-optimizer hypothesis was added. The printed proof audit also found all three target theorem groups valid as written.

## Verification

- Clean cumulative build: **{rec['compile_targets']} targets**, comprising **{rec['production_modules']} production modules and three roots**, starting with no project object files.
- Complete environment audit: **{rec['axiom_declarations']:,} declarations**; cumulative explicit theorem/lemma count **{rec['explicit_theorem_lemma_count']:,}**. Only `propext`, `Classical.choice`, and `Quot.sound` appear in the accepted axiom union.
- **{len(rec['controls'])} control files**: {counts['positive']} positive, {counts['negative']} intended compiler rejections, and {counts['policy']} policy rejections. Invalid cases must fail at the intended obligation, rather than from a missing import or resource failure.
- **{len(rec['commands'])} recorded commands** passed their required outcomes, followed by independent terminal validation. Sources, compiled project objects, and **{rec['runtime_file_count']:,} runtime/cache files** passed their recorded endpoint identity checks.
- Exact source, command, type, axiom, review, and runtime identities are retained in the handoff. The full monograph was rebuilt and visually checked after its status and erratum changes.

## Mistakes found and corrected

The printed text incorrectly called the residual the projection. The new edition distinguishes the nearest reachable image from the datum-minus-image residual. No theorem statement changed. The original source and explicit erratum are retained.

Development attempts exposed Lean API, notation, expression-order, strict-linter, documentation-placement, and object-path errors. All were corrected without weakening the target or disabling strict checks. Positive boundary tests initially exposed additional simplification/linter errors, also corrected. Every numbered failed source and diagnostic is preserved alongside the successful attempt.

Independent verification review caught provenance gaps in cached Python helper loading, runtime/cache endpoint checks, exporter binding, and terminal evidence binding. These were fixed before the accepted clean replay. Package review added explicit receipt/source/publication binding and direct comparison with the hash-pinned predecessor archive, and caught an omitted historical scripts directory before release. The records distinguish these corrected tooling failures from mathematical gaps.

The detailed type/axiom export took about 386 seconds, longer than estimated. A proposed interruption to optimize inherited type printing was overtaken by the export's successful completion: the signal attempt found no process and affected none. The original run and frozen helpers were retained. No interrupted replay or mathematical failure is claimed for this coordination event.

## Current coverage and next work

**Nine of sixteen WR groups are complete:** WR01–WR07, WR13, and WR14. **Two are partial:** WR09 and WR16 retain written limiting conclusions. **Five remain written-only:** WR08, WR10–WR12, and WR15.

The next major block is **WR08**, the complete regularization limit alternative: convergence of fitted data and residuals, vanishing weighted penalty, strong convergence in the attained case, and norm divergence otherwise. Its strong-convergence branch is the principal next obligation. WR09 and WR16 limits follow naturally after that block. The exact restart contract is `budget_v1.10.0/NEXT_RESEARCH_BLOCK.md`.

The global independent monograph audit, executable certificate refinement, application-specific model identification, and updated companion guides remain separate work. This release does not claim they are finished.

## Evidence and trust

The accepted formal receipt SHA-256 is `{rh}`; terminal postflight SHA-256 is `{ph}`. `VERIFICATION_SUMMARY.json` supplies the rest of the identities, and `budget_v1.10.0/records/EVENTS.jsonl` preserves the event history.

The Lean compiler/kernel, standard axioms, pinned precompiled dependencies, and supporting runtime remain trusted. All project sources were compiled afresh; the dependencies were not rebuilt from source. Endpoint hashes do not detect a temporary change restored between checks. The focused printed-proof and statement audits do not certify every sentence or executable example in the full monograph.
'''
    (ROOT/'PROGRESS_LEDGER.md').write_text(text)
    event = {'id':f'E{len(old)+1:04d}','state':'budget_release_accepted','created_utc':now,
             'checkpoint':summary['checkpoint'],'formal_receipt_sha256':rh,'postflight_sha256':ph,
             'publication_verification_sha256':sha(publication),
             'detail':'Full WR03–WR05 accepted after independent statement review, clean cumulative replay, intended controls, terminal integrity checks, and publication verification. Coverage is nine complete, two partial, five written-only.'}
    with events.open('a') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'ACCEPTED','summary':str(ROOT/'VERIFICATION_SUMMARY.json')},indent=2))

if __name__ == '__main__':
    main()

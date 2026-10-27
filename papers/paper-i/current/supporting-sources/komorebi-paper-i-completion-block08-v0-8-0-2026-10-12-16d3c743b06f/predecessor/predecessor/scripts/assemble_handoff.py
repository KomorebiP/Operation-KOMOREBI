#!/usr/bin/env python3
"""Assemble a handoff only after the recorded Block 06 audit has completed."""
from pathlib import Path
import collections,hashlib,json,re
r=Path(__file__).resolve().parents[1]
a=r/'evidence/final_audit';b=json.loads((a/'verification.json').read_text())
assert b['status']=='PASS'
assert b['fresh_new_production_modules']==5 and b['predecessor_module_pairs_authenticated']==37
assert len(b['same_kernel_modules_replayed'])==42 and b['new_boundary_module_replayed']
assert all(c['passed'] for c in b['checks'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exact=json.loads((r/'evidence/PREDECESSOR_EXACT_IDENTITY.json').read_text())
assert exact['status']=='PASS' and exact['files_name_and_byte_identical']==1326
coverage=json.loads((r/'coverage/COVERAGE_108.json').read_text())
assert coverage['proved_record_status_counts']=={'not_mapped':20,'partial':30,'covered':19}
old=json.loads((r/'predecessor/coverage/COVERAGE_108.json').read_text());changes=[]
for x,y in zip(old['records'],coverage['records'],strict=True):
 assert x['stable_id']==y['stable_id']
 for key in ('statement','source_proof','current_source'):assert x[key]==y[key]
 if x['status']!=y['status']:changes.append({'stable_id':y['stable_id'],'from':x['status'],'to':y['status']})
assert changes==[{'stable_id':'PSC-I-C-CYCLIC-MATRIX','from':'partial','to':'covered'}]
actual_names=set(re.findall(r"^#check ([\w.']+)",(a/'DeclarationTypes.lean').read_text(),re.M))
for d in json.loads((r/'coverage/DELTA_108.json').read_text())['updates']:
 assert set(d['add_declarations'])<=actual_names
cp=next((r/'predecessor').rglob('CONTRACT_ROWS.json'));contract=json.loads(cp.read_text())
cnames={n for row in contract for n in row['declarations']}
assert len(contract)==35 and len(cnames)==84 and cnames<=actual_names
continuity={'status':'PASS','contract_rows':35,'original_names_resolved':84,
 'source':str(cp.relative_to(r)),'sha256':sha(cp),'declarations':sorted(cnames)}
(r/'evidence/ORIGINAL_CONTRACT_CONTINUITY.json').write_text(json.dumps(continuity,indent=2)+'\n')
# Preserve unsuccessful drafts and receipts separately from accepted commands.
dev=[]
for p in sorted((r/'evidence/development').glob('*/receipt.json')):
 d=json.loads(p.read_text());dev.append({'receipt':str(p.relative_to(r)),'receipt_sha256':sha(p),
  'actual_exit':d['exit_code'],'seconds':d['seconds'],'accepted_as_final':False})
index={'schema':'paper-i-block06-development-index/0.6.0','recorded_compilations':len(dev),
 'zero_exit_drafts':sum(x['actual_exit']==0 for x in dev),
 'rejected_drafts':sum(x['actual_exit']!=0 for x in dev),'runs':dev,
 'unreceipted_interruption':'evidence/INTERRUPTIONS.json',
 'other_operational_incidents':'evidence/OPERATIONAL_INCIDENTS.json',
 'final_acceptance':'evidence/final_audit/verification.json'}
(r/'evidence/DEVELOPMENT_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
summary={'schema':'paper-i-completion-block06/0.6.0','status':'PASS','business_date':'2026-10-11',
 'audit_scope':b['scope'],'accepted_run':{'path':'evidence/final_audit/verification.json','sha256':sha(a/'verification.json')},
 'predecessor_payloads_authenticated':b['predecessor_payloads_authenticated'],
 'entire_predecessor_files_identical_to_zip':exact['files_name_and_byte_identical'],
 'predecessor_source_object_pairs_authenticated':37,'freshly_compiled_new_production_modules':5,
 'complete_production_modules':42,'complete_same_kernel_production_replays':42,
 'additional_boundary_module_replays':1,'source_owned_declarations':b['owned_total'],
 'source_owned_new_declarations':b['owned_new'],'new_public_declarations':b['new_public_count'],
 'new_public_kind_counts':b['new_public_kind_counts'],
 'resolved_public_or_coverage_names':b['declaration_names_resolved'],
 'new_boundary_assertions':b['new_boundary_assertions'],'negative_controls_rejected':b['negative_controls'],
 'positive_foreign_namespace_control':b['positive_foreign_namespace_control'],
 'accepted_expected_outcome_commands':len(b['checks']),
 'source_object_postflight_pairs':b['postflight_source_object_pairs_verified'],
 'transitive_axioms':b['axioms'],'original_normative_contract_rows':35,
 'original_mapped_declarations_resolved':84,'original_normative_contract_unchanged':True,
 'publication_records_unchanged':108,'proof_level_records':69,
 'proof_level_status':coverage['proved_record_status_counts'],'coverage_status_changes':changes,
 'failed_work_index':'evidence/DEVELOPMENT_INDEX.json','dependencies':b['dependencies'],
 'lean_version':b['lean_version'],'runtime_archive_sha256':b['runtime_archive_sha256'],
 'elapsed_seconds_of_accepted_run':b['elapsed_seconds'],'limits':b['limits'],
 'next_restart':'General noncommutative module-top/Nakayama lifting, then the local residue-division-ring formula; see CONTINUE_HERE.md.'}
(r/'VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
report=f'''# Paper I completion: Block 06

**Result: PASS for the full six-way cyclic-matrix criterion, the new scalar-extension/primary/companion constructions, the authenticated predecessor, and complete same-kernel project replay.**

**Date:** 11 October 2026. **Version:** 0.6.0.

This closes the expanded publication's cyclic-matrix corollary. It does not claim that the entire expanded monograph is formalized. Every predecessor mathematical source and dependency pin remains unchanged.

## Mathematical completion

For every finite-dimensional endomorphism T over an arbitrary field k and any field extension K, the new source proves the literal identity

    minpoly_K(T.baseChange K) = map_{{k→K}}(minpoly_k(T)).

It derives both preservation and reflection of cyclicity for the actual tensor-product operator on K ⊗_k V. Neither separability, algebraicity, finite extension degree, nor characteristic zero is required. The polynomial and cyclicity extension theorems include the zero space.

For nonzero V, the development proves the exact six-way equivalence between an actual cyclic vector, canonical seed rank one, cyclicity of every nonzero intrinsic primary component, an actual one-invariant-factor presentation, minpoly=charpoly, and geometric multiplicity one for every spectral value after the literal extension to an algebraic closure.

The one-factor result includes a constructed basis in which the original operator is the standard companion matrix. The monic factor is proved to be the minimal polynomial. A separate theorem proves that any actual nonconstant invariant-factor chain has exactly one factor iff the operator is cyclic. No decomposition, primary multiplicity, spectral, polynomial-preservation, or seed-number conclusion is an input to the final six-way theorem.

The construction supplies mathematical existence and equivalences, not an executable canonical-form algorithm. It does not construct a sorted invariant-factor decomposition for every noncyclic operator. The six-way statement retains its nonzero-space guard: the zero space is cyclic in the at-most-one-generator sense but has seed rank zero.

## Actual executed verification

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | {b['predecessor_payloads_authenticated']} / {b['predecessor_payloads_authenticated']} |
| Entire predecessor compared with supplied ZIP | {exact['files_name_and_byte_identical']} / {exact['files_name_and_byte_identical']} files |
| Predecessor source/object pairs authenticated | 37 / 37 |
| New production modules freshly compiled | 5 / 5 |
| Original formal-contract rows preserved | 35 / 35 |
| Original mapped declarations resolved | 84 / 84 |
| Public-or-coverage declaration names resolved | {b['declaration_names_resolved']} / {b['declaration_names_resolved']} |
| Complete source-owned declaration audit | {b['owned_total']} / {b['owned_total']} |
| Source-owned entries from new modules | {b['owned_new']} |
| Same-kernel production-module replays | 42 / 42 |
| Additional boundary-module replay | 1 / 1 |
| New exact mathematical boundary assertions | {b['new_boundary_assertions']} / {b['new_boundary_assertions']} |
| Deliberately invalid controls rejected | {b['negative_controls']} / {b['negative_controls']} |
| Positive foreign-namespace guard control | 1 / 1 |
| Accepted expected-outcome commands | {len(b['checks'])} / {len(b['checks'])} |
| Final production source/object identities | 42 / 42 |
| Exact dependency revisions checked | 9 / 9 |

The separate 1,326-file comparison includes the predecessor manifest itself.

The five new modules were compiled into an initially empty isolated object directory, using authenticated predecessor objects and pinned upstream imports. All 42 production modules were then replayed serially. **The 37 predecessor sources were not freshly recompiled in this block.** Their source and object bytes were authenticated. No development object was used to replace a fresh compilation of a new module.

The boundary suite was freshly compiled and replayed. Its three prior boundary-module imports were authenticated, not separately rebuilt or replayed as test suites here. The original 35-row contract was not silently expanded or rewritten. Its 84 mapped names are included in the resolved declaration list.

The new source has {b['new_public_kind_counts']['theorem']} public theorem declarations and {b['new_public_kind_counts']['def']} definitions in four mathematical modules plus an import-only root. The complete owned inventory also includes supporting and generated declarations. These counts are not counts of independent discoveries.

Only {', '.join('`'+x+'`' for x in b['axioms'])} appeared as transitive axioms. No production placeholder or additional custom axiom passed the ownership gate. The scope of that statement is production source, not intentionally invalid fixtures or archived failed drafts.

## Boundary checks

The rational test module is a one-coordinate product explicitly identified with Q[t]/((t²+1)²) by `squaredOneFactor`. Its actual polynomial-action operator has dimension four, exact minimal polynomial (t²+1)², and no rational eigenspaces of positive dimension. The new tests prove the exact mapped minimal polynomial after its actual complex extension, unchanged degree four, cyclicity, and geometric multiplicity one at every actual complex spectral value. This exercises scalar extension rather than substituting a theorem over an originally algebraically closed field.

The suite also verifies an actual companion basis and quotient-action intertwining, entrywise companion signs and orientation for t²+1, noncyclicity of repeated Jordan chains after extension, zero-space conventions, and characteristic-two instances of both extension identities and cyclicity descent.

The rejection suite detects missing finite-dimensionality, missing nontriviality, missing algebraic closure, the wrong companion sign, an invalid substitution of a cyclic operator for a repeated-chain operator, a false equality, and a placeholder. Imported custom-axiom and placeholder controls in foreign namespaces are correctly rejected, while the clean foreign-namespace control is accepted.

## Failed attempts and recovery

There are {index['recorded_compilations']} recorded development compiler runs: {index['rejected_drafts']} rejected drafts and {index['zero_exit_drafts']} zero-exit exploratory runs. Rejected drafts involved API names or argument order, tensor-endomorphism elaboration, polynomial map inference, a split qualified name, a local-instance style check, polynomial-module action rewriting, companion-matrix definitional equality, monic divisibility, dependent finite-index instances, a coefficient simplification, and the missing characteristic-two field import/instance. The preserved snapshots and compiler diagnostics show which error occurred in which attempt.

The initial foreground driver was interrupted by the tool's execution limit before an exit receipt could be collected. Its log remains explicitly unaccepted. A persistent driver with per-command receipts was used thereafter. One source-inspection command also addressed the AEval source under the wrong directory; it was corrected to the pinned polynomial-module path. No predecessor theorem or dependency pin was altered by these recoveries.

None of the exploratory, rejected, or interrupted runs is counted as final acceptance. The fresh accepted run, after the corrections, completed every required check. The final run's exact wall time was {b['elapsed_seconds']:.3f} seconds, excluding development, runtime recovery, and packaging.

## Publication coverage

All 108 stored statements, source proofs, and source-location/hash records are unchanged. Exactly one proof-level record changes status: `PSC-I-C-CYCLIC-MATRIX` moves from partial to covered.

The 69 proof-level records now have **19 covered, 30 partial, and 20 not mapped**. These are reviewed statement-correspondence categories, not an overall completion percentage. Legacy conditional wrappers are retained for compatibility; the new unconditional theorem provides the stronger publication-facing result.

## Trust and reproduction

The combined `run_block06.sh` launcher was actually executed. Its command-level receipts record observed exits, elapsed times, complete logs, source snapshots, and hashes. The exact Lean runtime and nine dependency revisions are authenticated.

Mathlib's pinned cache is reused rather than freshly rebuilt or fully replayed. Replay uses Lean's own official kernel, not an independently implemented verifier. The publication correspondence is reviewed semantic matching, not a kernel interpretation of TeX prose. All constructions here are noncomputable mathematical objects and proofs. Publication PDFs were not rebuilt. Prior license-status records remain unchanged. The large runtime is an external prerequisite.

## Next restart

Stay on Paper I. Prove the general noncommutative module-top/Nakayama lifting theorem, then the local residue-division-ring formula. A genuine noncommutative upstream Nakayama form was identified in the pinned Mathlib source and is recorded in `CONTINUE_HERE.md`; identifying that API is not counted as a new verified project theorem.

The nonsplit semisimple, expanded packet/functorial/topological, and executable-algorithm obligations remain. Papers II–XII have not been rerun in this sweep.
'''
(r/'docs/COMPLETION_REPORT.md').write_text(report)
ledger='''# Paper I completion ledger v0.6.0

## Accepted checkpoint

Block 06: PASS. Five new production modules freshly compiled, 37 predecessor source/object pairs authenticated, all 42 production modules replayed, complete source-owned axiom gate passed, and new boundary and rejection controls passed. This is incremental fresh compilation plus complete project replay, not a fresh recompilation of every predecessor source or Mathlib.

## Closed this block

Actual tensor-extension minimal-polynomial identity and degree preservation; cyclicity preservation and descent; actual extension to an algebraic closure in the geometric criterion; cyclicity of all nonzero intrinsic primary components; an actual one-factor presentation with its monic factor identified as the minimal polynomial; a constructed standard companion-matrix basis; any-chain invariant-factor count-one consequence; exact six-way List.TFAE with a literal AlgebraicClosure k instance.

No preservation, decomposition, multiplicity, spectral, or seed-number certificate is a premise of the final six-way theorem. The nonzero-space guard is retained for the rank-one/six-way criterion. The extension identities themselves include zero spaces.

## Publication status

108 unchanged records. Among 69 proof-level records: 19 covered, 30 partial, 20 not mapped. Only PSC-I-C-CYCLIC-MATRIX changes status. It is now covered at the printed scope. Other record statuses are not silently upgraded.

## Failure evidence

Rejected and successful exploratory compiler receipts remain in evidence/development and are indexed by evidence/DEVELOPMENT_INDEX.json. The initial unreceipted foreground interruption and operational path correction are separately recorded. None contributes to final acceptance. VERIFICATION.json and its hashed accepted receipt govern the PASS claim.

## Next restart

Continue with the general noncommutative module-top/Nakayama generator-lifting theorem and then the local residue-division-ring formula. The exact pinned upstream noncommutative Nakayama API and the commutative-only residue-field boundary are recorded in CONTINUE_HERE.md. This planning inspection does not mark either result proved.

Do not reconstruct the intrinsic primary quotient, geometric formula, scalar-extension bridge, or six-way cyclic criterion as though they were still missing. Retain earlier sources as the unchanged compatibility baseline.

## Other work

Nonsplit semisimple, expanded packet/functorial/topological, and executable-algorithm obligations remain in the coverage map. Papers II–XII have not been rerun in this sweep. Historical evidence remains preserved.
'''
(r/'PROGRESS_LEDGER.md').write_text(ledger)
(r/'PROGRESS_LEDGER.json').write_text(json.dumps({'version':'0.6.0','accepted_checkpoint':'Block06','status':'PASS',
 'verification':'VERIFICATION.json','proof_level_status':coverage['proved_record_status_counts'],
 'newly_covered_record':'PSC-I-C-CYCLIC-MATRIX','next_restart':'CONTINUE_HERE.md',
 'next_records':['PSC-I-CI-NAKAYAMA','PSC-I-T-MODULE-TOP','PSC-I-C-LOCAL-ALGEBRA-FORMULA'],
 'remaining_series_audits':['Paper '+x for x in ['II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']]},indent=2)+'\n')
(r/'README.md').write_text('''# Paper I completion Block 06 — v0.6.0

The full six-way cyclic-matrix criterion is verified at its stated arbitrary-field, nonzero finite-dimensional scope. The actual scalar-extension, intrinsic-primary, and companion-basis bridges are supplied. The expanded monograph is not yet entirely formalized.

Read `docs/COMPLETION_REPORT.md` for results and limits, `docs/PROOF_GUIDE.md` for the mathematics, and `CONTINUE_HERE.md` for the next restart. `VERIFICATION.json` points to the hashed accepted command receipt. `coverage/COVERAGE_108.md` accounts for every publication record. The versioned progress ledger records continuity.

## Reproduce

From Linux or WSL, with Python 3 and the exact external portable runtime:

```sh
bash scripts/run_block06.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output
```

The output directory must not already exist. Do not run `lake update`. The launcher authenticates all 37 predecessor source/object pairs and the runtime bindings, freshly compiles five new modules, checks ownership/types/controls, and serially replays all 42 current production modules. Cached upstream imports are reused. This is not a fresh dependency rebuild or an independent verifier.

## Contents

`predecessor/` is the complete byte-identical Block 05 package. `source/extension/` contains current mathematical sources. `tests/` contains boundary consumers, audit gates, a replay wrapper, and intentionally invalid controls. Failed development snapshots and invalid controls are evidence, not production mathematics. `evidence/final_audit/` contains the accepted isolated objects, command logs, source snapshots, declarations, and axiom inventory. `scripts/` contains reproduction and handoff tooling. The large runtime is external.

No executable eigensolver, factorization, or rational-canonical algorithm is claimed. Publication PDFs were not rebuilt. Previous license-status records are inherited unchanged; no new publication license is selected.
''')
print(json.dumps(summary,indent=2))

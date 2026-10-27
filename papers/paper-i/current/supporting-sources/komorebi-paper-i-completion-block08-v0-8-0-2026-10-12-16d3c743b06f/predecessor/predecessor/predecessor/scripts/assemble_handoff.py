#!/usr/bin/env python3
"""Assemble reports only from an accepted completed audit; never invent counts."""
from pathlib import Path
import collections,hashlib,json,re,shutil,time
r=Path(__file__).resolve().parents[1]
a=r/'evidence/final_audit'; b=json.loads((a/'verification.json').read_text())
assert b['status']=='PASS', 'Final audit is not accepted'
assert b['fresh_new_production_modules']==4
assert b['predecessor_module_pairs_authenticated']==33
assert len(b['same_kernel_modules_replayed'])==37
assert all(x['passed'] for x in b['checks'])
assert b['new_boundary_assertions']==23
assert json.loads((r/'evidence/PREDECESSOR_EXACT_IDENTITY.json').read_text())['status']=='PASS'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
coverage=json.loads((r/'coverage/COVERAGE_108.json').read_text())
assert coverage['proved_record_status_counts']=={'not_mapped':20,'partial':31,'covered':18}
old=json.loads((r/'predecessor/coverage/COVERAGE_108.json').read_text())
changes=[]
for x,y in zip(old['records'],coverage['records'],strict=True):
 assert x['stable_id']==y['stable_id']
 for k in ['statement','source_proof','current_source']:assert x[k]==y[k]
 if x['status']!=y['status']:changes.append({'stable_id':y['stable_id'],'from':x['status'],'to':y['status']})
assert len(changes)==1 and changes[0]['stable_id']=='PSC-I-C-ALGEBRAICALLY-CLOSED-SINGLE-OPERATOR'
actual_names=set(re.findall(r'^#check ([\w.\']+)',(a/'DeclarationTypes.lean').read_text(),re.M))
for update in json.loads((r/'coverage/DELTA_108.json').read_text())['updates']:
 assert set(update['add_declarations'])<=actual_names
# Retain failed and successful exploratory receipts without treating them as final acceptance.
dev=[]
for p in sorted((r/'evidence/development').glob('*/receipt.json')):
 d=json.loads(p.read_text());dev.append({'receipt':str(p.relative_to(r)),'receipt_sha256':sha(p),'actual_exit':d['exit_code'],'seconds':d['seconds'],'accepted_as_final':False})
index={'schema':'paper-i-block05-development-index/0.5.0','recorded_compilations':len(dev),'zero_exit_drafts':sum(x['actual_exit']==0 for x in dev),'rejected_drafts':sum(x['actual_exit']!=0 for x in dev),'runs':dev,'unreceipted_interruption':'evidence/development/20261011T002545_347998/INTERRUPTED_DRIVER.json','cancelled_optional_baseline_rebuild':'evidence/PREDECESSOR_ATTEMPT_NOT_ACCEPTED.json','transport_incidents':'evidence/TRANSPORT_INCIDENTS.json','final_acceptance':'evidence/final_audit/verification.json'}
(r/'evidence/DEVELOPMENT_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
owned=json.loads((a/'owned_declarations.json').read_text())
summary={'schema':'paper-i-completion-block05/0.5.0','status':'PASS','audit_scope':b['scope'],'business_date':'2026-10-10','accepted_run':{'path':'evidence/final_audit/verification.json','sha256':sha(a/'verification.json')},'predecessor_payloads_authenticated':b['predecessor_payloads_authenticated'],'predecessor_source_object_pairs_authenticated':33,'freshly_compiled_new_production_modules':4,'complete_production_modules':37,'complete_same_kernel_production_replays':37,'additional_boundary_module_replays':1,'source_owned_declarations':b['owned_total'],'source_owned_new_declarations':b['owned_new'],'new_public_declarations':b['new_public_count'],'new_public_kind_counts':b['new_public_kind_counts'],'resolved_public_or_coverage_names':b['declaration_names_resolved'],'new_boundary_assertions':b['new_boundary_assertions'],'negative_controls_rejected':b['negative_controls'],'positive_foreign_namespace_control':b['positive_foreign_namespace_control'],'accepted_expected_outcome_commands':len(b['checks']),'source_object_postflight_pairs':b['postflight_source_object_pairs_verified'],'transitive_axioms':b['axioms'],'original_normative_contract_unchanged':True,'publication_records_unchanged':108,'proof_level_records':69,'proof_level_status':coverage['proved_record_status_counts'],'coverage_status_changes':changes,'failed_work_index':'evidence/DEVELOPMENT_INDEX.json','dependencies':b['dependencies'],'lean_version':b['lean_version'],'runtime_archive_sha256':b['runtime_archive_sha256'],'elapsed_seconds_of_accepted_run':b['elapsed_seconds'],'limits':b['limits'],'next_restart':'Actual scalar-extension bridge and remaining exact assembly of the six-way cyclic criterion; see CONTINUE_HERE.md.'}
(r/'VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
report=f'''# Paper I completion: Block 05

**Result: PASS for the new geometric-multiplicity and cyclicity extension, authenticated predecessor, and complete same-kernel replay.**

This is not a claim that the expanded monograph is entirely formalized. The original 35-row component and all Block 02–04 mathematical sources and dependency pins remain unchanged.

## Mathematical completion

For every finite-dimensional endomorphism T over an algebraically closed field k, the new Lean sources prove

    seedRank_{{k[T]}}(V) = max_{{a in spectrum(k,T)}} dim_k ker(T-aI).

The natural-valued seedFinrank formula is proved as well. No diagonalizability, self-adjointness, eigenbasis, Jordan basis, supplied decomposition, multiplicity certificate, or assumed seed-rank equality is required. The empty-spectrum/zero-space maximum is zero. The spectral maximum is attained on nonzero spaces.

The key new bridge, valid over any field, is

    mu_{{t-a}}(T) = dim_k ker(T-aI).

It composes Block 04's natural primary-to-global quotient equivalence with a new actual cokernel equivalence, the one-dimensional evaluation residue field, and rank-nullity. The exact kernel and action on representatives are proved. This proof does not construct or assume a Jordan normal form.

For nonzero spaces whose original field is algebraically closed, cyclicity and minpoly=charpoly are each proved equivalent to geometric multiplicity one at every spectral value. For any field, cyclicity is also proved equivalent to an actual polynomial-module presentation by k[t]/(minpoly(T)). The latter is not an executable invariant-factor algorithm.

These are classical results completed inside Paper I's actual definitions, not claims of new classical discoveries.

## What actually ran

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | {b['predecessor_payloads_authenticated']} / {b['predecessor_payloads_authenticated']} |
| Preserved source/object pairs authenticated | 33 / 33 |
| New production modules freshly compiled | 4 / 4 |
| Complete source-owned declaration audit | {b['owned_total']} / {b['owned_total']} |
| Source-owned entries from the new modules | {b['owned_new']} |
| Public-or-coverage declaration names resolved | {b['declaration_names_resolved']} |
| Complete same-kernel production-module replays | 37 / 37 |
| Additional boundary-module replay | 1 / 1 |
| New exact mathematical boundary assertions | 23 / 23 |
| Deliberately invalid controls rejected | {b['negative_controls']} / {b['negative_controls']} |
| Positive foreign-namespace control | 1 / 1 |
| Accepted expected-outcome commands | {len(b['checks'])} / {len(b['checks'])} |
| Final source/object identity checks | 37 / 37 |
| Exact dependency revisions checked | 9 / 9 |

**The 33 predecessor modules were not freshly rebuilt in the accepted run.** Their actual source and object bytes were authenticated against the unchanged predecessor receipts, copied to an isolated import directory, and all replayed through the official Lean kernel. The four new production modules were freshly compiled into a separate empty output directory. No development object was accepted in place of those new compilations. The 23 new boundary assertions were also freshly compiled and their module replayed. Earlier boundary suites are authenticated imports, not separately rerun test suites in this block.

The new source contains {b['new_public_kind_counts']['theorem']} public theorem declarations and {b['new_public_kind_counts']['def']} definitions. Three new modules contain mathematics and one is import-only. The full owned inventory includes generated helpers, private declarations, constructors, and other supporting entries. These are not counts of independent discoveries.

The only reported transitive axioms were {', '.join('`'+x+'`' for x in b['axioms'])}. No production placeholder or additional custom axiom passed the source/ownership gates. Complete full public types, axioms, and source snapshots accompany the receipts.

## Tests

The literal X-action on C[t]/(t^2) has dimension two, is nonzero with square zero, has no Fin-2 eigenbasis, and has geometric multiplicity and seed maximum one. Two primary chains of lengths one and two have multiplicity and seed count two. The rational operator on Q[t]/((t^2+1)^2) has seed rank one but zero-dimensional eigenspaces for every rational scalar. This is an actual counterexample to dropping algebraic closure, not just a failed typeclass search.

Other assertions check zero spaces, quotient representatives, the exact scalar-image kernel, and the one-factor presentation. Negative controls reject a false equality, an authored placeholder, a missing algebraic-closure instance, a missing nonzero-space instance, the wrong Jordan multiplicity, surjectivity incorrectly used as injectivity, an imported custom axiom outside the project namespaces, and an imported placeholder compiled with warnings deliberately disabled. The clean foreign-namespace fixture passes.

## Failures and recoveries

The development index retains {index['recorded_compilations']} compiler receipts: {index['rejected_drafts']} rejected drafts/API probes and {index['zero_exit_drafts']} zero-exit development runs. Rejected drafts included unknown API names, a quotient representative simplification, a beta-reduced maximum expression, a missing `map_one`, quotient coefficient inference, missing complex algebraic-closure import, dependent-index inference, and an overbroad extensionality tactic that hit a heartbeat limit. These were corrected before the accepted run. A separate foreground driver was interrupted by the tool timeout and did not produce an accepted object or command exit receipt. An unavailable streaming execution mode failed before command execution.

A supplemental archive-identity diagnostic initially compared paths with and without the enclosing archive directory and failed that path comparison. After normalizing the single root directory, all 1,011 predecessor files matched in name and bytes. No predecessor content changed.

An optional full predecessor rebuild was paused to serialize compiler work under the container memory limit and then deliberately cancelled after three successful source compilations. Its raw partial logs remain, explicitly marked CANCELLED_NOT_ACCEPTED. The accepted run instead uses the authenticated-predecessor strategy described above. The cancelled run is not counted as a complete rebuild or added to PASS totals.

## Publication coverage

All 108 stored statement, source-proof, and source-location/hash records remain unchanged. Exactly one proof-level record moves from partial to covered: `PSC-I-C-ALGEBRAICALLY-CLOSED-SINGLE-OPERATOR`.

Among the 69 proof-level records: **18 covered, 31 partial, 20 not mapped**. The 35-row formal contract and the expanded monograph use different inventories. These figures are not an overall completion percentage.

`PSC-I-C-CYCLIC-MATRIX` remains partial. The native algebraically closed geometric criterion and an actual one-factor module presentation are added, but the full scalar-extension clause from an arbitrary base field and the exact remaining six-way assembly are not silently marked complete.

## Trust, reproduction, and next restart

The combined `run_block05.sh` launcher was actually executed. The accepted run recorded {b['elapsed_seconds']:.3f} seconds, excluding development, runtime recovery, and packaging. All detailed commands have observed outcomes, elapsed times, and hashed logs. The pinned Mathlib cache was reused, not rebuilt or fully replayed. Replay uses Lean's own kernel, not an independently implemented verifier. The correspondence between the manuscript and Lean types is a reviewed semantic artifact, not kernel interpretation of prose.

The mathematical constructions are noncomputable. There is no executable eigensolver, factorization routine, or canonical-form computation. Publication PDFs were not rebuilt. Prior license-status records are preserved without choosing a new license. The large pinned runtime remains an external prerequisite.

**Next restart:** the actual scalar-extension bridge for the six-way cyclic criterion, followed by its exact intrinsic-primary/rational-canonical assembly. Other recorded semisimple, module-top/Nakayama, packet/topological, and executable obligations remain. Papers II–XII have not been rerun in this sweep. See `CONTINUE_HERE.md`.
'''
(r/'docs/COMPLETION_REPORT.md').write_text(report)
ledger='''# Paper I completion ledger v0.5.0

## Accepted checkpoint

Block 05: PASS for four fresh production compilations, 33 authenticated predecessor source/object pairs, the complete source-owned axiom audit, and all 37 same-kernel production replays. All prior mathematical sources and dependency pins remain unchanged. The accepted run is incremental compilation plus complete project replay, not a fresh rebuild of all 37 sources or Mathlib.

## Closed this block

Natural polynomial scalar quotient/cokernel equivalence and representative theorem; exact scalar-image kernel; arbitrary-field linear-primary multiplicity/eigenspace identity; bounded attained geometric maximum; exact actual-spectrum maximum including the zero-space convention; full arbitrary non-diagonalizable algebraically closed seed-rank formula; native algebraically closed cyclic/minpoly geometric criteria; actual one-factor polynomial-module presentation from and to cyclicity.

## Publication status

108 unchanged records. Among 69 proof-level records: 18 covered, 31 partial, 20 not mapped. Only PSC-I-C-ALGEBRAICALLY-CLOSED-SINGLE-OPERATOR changes status. PSC-I-C-CYCLIC-MATRIX remains partial because actual scalar extension and exact remaining six-way assembly still need proof.

## Failures

Rejected development receipts, one unreceipted foreground interruption, the unavailable streaming mode, and a cancelled optional predecessor rebuild are indexed under evidence/. None contributes to final acceptance. VERIFICATION.json and its hashed accepted-run receipt govern the PASS claim.

## Next restart

Stay on Paper I. Prove the actual algebraic-closure scalar-extension bridge, then assemble the precise six-way cyclic criterion. Do not reconstruct the primary quotient or arbitrary geometric-multiplicity result as though it were still missing. See CONTINUE_HERE.md for actual APIs, source paths, and proof boundaries.

## Other work

Nonsplit semisimple, module-top/Nakayama, expanded packet/functorial/topological, and executable algorithm obligations remain in the coverage map. Papers II–XII have not been rerun in this sweep. Historical evidence remains preserved.
'''
(r/'PROGRESS_LEDGER.md').write_text(ledger)
(r/'PROGRESS_LEDGER.json').write_text(json.dumps({'version':'0.5.0','accepted_checkpoint':'Block05','status':'PASS','verification':'VERIFICATION.json','proof_level_status':coverage['proved_record_status_counts'],'next_restart':'CONTINUE_HERE.md','remaining_series_audits':['Paper '+x for x in ['II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']]},indent=2)+'\n')
(r/'README.md').write_text('''# Paper I completion Block 05 — v0.5.0

The new geometric-multiplicity corollary is verified for arbitrary finite-dimensional operators over algebraically closed fields, including non-diagonalizable operators. The expanded monograph is not yet fully formalized.

Read `docs/COMPLETION_REPORT.md` for actual results and trust boundaries, `docs/PROOF_GUIDE.md` for the mathematics, and `CONTINUE_HERE.md` for the exact restart. `VERIFICATION.json` points to the hashed accepted command receipt. `coverage/COVERAGE_108.md` tracks every publication record. `PROGRESS_LEDGER.md` records continuity.

## Reproduce

From Linux or WSL with Python 3 and the exact external portable runtime:

```sh
bash scripts/run_block05.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output
```

The output path must not already exist. Do not run `lake update`. The launcher authenticates the predecessor source/object bytes and exact runtime bindings, freshly compiles four new modules, and replays all 37 current production modules serially. Cached upstream dependencies are reused. This is not a fresh all-source/dependency rebuild or an independent verifier.

## Package contents

`predecessor/` is the full unchanged Block 04 package, including earlier sources and evidence. `source/extension/` contains the new mathematical modules. `tests/` includes exact theorem consumers, source-owned gates, replay wrapper, and deliberately invalid fixtures. Invalid fixtures and failed development snapshots are evidence, not production source. `evidence/final_audit/` contains the accepted isolated objects, logs, snapshots, types, and ownership inventory. Other evidence folders preserve unsuccessful or exploratory attempts with explicit status indexes. `scripts/` contains verification and handoff tooling. The large Lean/Mathlib runtime is external.

Mathematical declarations are noncomputable specifications and proofs, not an executable eigensolver or canonical-form algorithm. Prior license-status records are inherited unchanged. No new publication license is selected here.
''')
print(json.dumps(summary,indent=2))

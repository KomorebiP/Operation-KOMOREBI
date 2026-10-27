#!/usr/bin/env python3
"""Create source copies and a documented handoff only after actual accepted verification."""
from pathlib import Path
import collections, hashlib, json, re, shutil, subprocess
R=Path(__file__).resolve().parents[1]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
audit=R/'evidence/final_audit/verification.json';a=json.loads(audit.read_text())
assert a['status']=='PASS' and len(a['same_kernel_modules_replayed'])==54
assert a['replay_owned_exact_name_set_match'] and a['replay_starting_environment_excludes_all_project_modules']
assert all(c['passed'] for c in a['checks'])
subprocess.run(['python3',str(R/'scripts/update_coverage.py')],check=True)
paths=[R/'coverage/COVERAGE_108.json',R/'coverage/COVERAGE_108.md'];before=[sha(p) for p in paths]
subprocess.run(['python3',str(R/'scripts/update_coverage.py')],check=True);assert before==[sha(p) for p in paths]
write(R/'evidence/COVERAGE_REPRODUCTION.json',{'status':'PASS','byte_identical_rerun':True,'unchanged_records':108,'outputs':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in paths]})
cov=json.loads(paths[0].read_text());oldcov=json.loads((R/'predecessor/coverage/COVERAGE_108.json').read_text())
old={r['stable_id']:r for r in oldcov['records']};changes=[]
for rec in cov['records']:
 for k in ['statement','source_proof','current_source']:assert rec[k]==old[rec['stable_id']][k]
 if rec['status']!=old[rec['stable_id']]['status']:changes.append({'stable_id':rec['stable_id'],'from':old[rec['stable_id']]['status'],'to':rec['status']})
assert len(changes)==6
# Replay and ownership are exact name-set matches, not only equal counts.
owned=json.loads((R/'evidence/final_audit/owned_declarations.json').read_text())
assert len(owned)==a['owned_total'] and sum(not x['runtime_only'] for x in owned)==a['owned_logical_total']
# Freeze a byte-identical convenience source tree, without treating it as another build.
current=R/'source/current';current.mkdir(parents=True,exist_ok=True);idx=[]
for row in a['source_files']:
 target=(current/Path(*row['module'].split('.'))).with_suffix('.lean');target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(R/row['source'],target);assert sha(target)==row['source_sha256']
 idx.append({'module':row['module'],'path':str(target.relative_to(R)),'sha256':sha(target),'accepted_source':row['source']})
write(R/'source/CURRENT_SOURCE_INDEX.json',{'status':'PASS','count':len(idx),'scope':'Byte-identical convenience copies of every accepted production source, not a separately rebuilt project.','files':idx})
(current/'README.md').write_text('Complete current 54-module production source closure. Each Lean file is byte-identical to its accepted source. See ../CURRENT_SOURCE_INDEX.json and the root verification runner. This convenience copy is not a separate fresh build. The pinned runtime and Mathlib cache remain external.\n')
prev=json.loads((R/'predecessor/VERIFICATION.json').read_text())
identity=json.loads((R/'evidence/PREDECESSOR_ZIP_IDENTITY.json').read_text());assert identity['status']=='PASS'
dev=json.loads((R/'evidence/DEVELOPMENT_INDEX.json').read_text())
v={'schema':'paper-i-completion-block08/0.8.0','status':'PASS','business_date':'2026-10-12','audit_scope':a['scope'],
'accepted_run':{'path':str(audit.relative_to(R)),'sha256':sha(audit)},
'predecessor_payloads_authenticated':a['predecessor_payloads_authenticated'],
'entire_predecessor_files_identical_to_zip':identity['all_files_identical'],
'predecessor_source_object_pairs_authenticated':a['predecessor_module_pairs_authenticated'],
'freshly_compiled_new_production_modules':a['fresh_new_production_modules'],
'complete_production_modules':len(a['source_files']),
'complete_same_kernel_production_replays':len(a['same_kernel_modules_replayed']),
'additional_boundary_module_replays':1,'source_owned_declarations':a['owned_total'],
'logical_production_declarations_replayed':a['owned_logical_total'],
'separately_inventoried_generated_partial_runtime_helpers':a['owned_runtime_only'],
'source_owned_new_declarations':a['owned_new'],'new_public_declarations':a['new_public_count'],
'new_public_kind_counts':a['new_public_kind_counts'],'resolved_public_or_coverage_names':a['declaration_names_resolved'],
'new_boundary_assertions':a['new_boundary_assertions'],'new_boundary_owned_declarations':a['boundary_owned_total'],
'complete_replay_logical_declarations_including_boundaries':a['replay_checked_constants'],
'replay_starting_environment_excludes_project':True,'replay_owned_exact_name_set_match':True,
'identical_generated_theorem_duplicates':a['replay_identical_duplicate_entries'],
'negative_controls_rejected':a['negative_controls'],'positive_foreign_namespace_control':1,
'accepted_expected_outcome_commands':len(a['checks']),
'source_object_postflight_pairs':a['postflight_source_object_pairs_verified'],
'flat_current_source_copies_verified':len(idx),'transitive_axioms':a['axioms'],
'original_normative_contract_rows':prev['original_normative_contract_rows'],
'original_mapped_declarations_resolved':prev['original_mapped_declarations_resolved'],
'original_normative_contract_unchanged':True,'publication_records_unchanged':108,'proof_level_records':69,
'proof_level_status':cov['proved_record_status_counts'],'coverage_status_changes':changes,
'failed_work_index':'evidence/DEVELOPMENT_INDEX.json','development_status_counts':dev['counts'],
'dependencies':a['dependencies'],'lean_version':a['lean_version'],
'runtime_archive_sha256':a['runtime_archive_sha256'],'elapsed_seconds_of_accepted_run':a['elapsed_seconds'],
'limits':a['limits'],'next_restart':'Algebraic exact-sequence seed bounds, actual invariant-submodule packet restriction and quotient descent, then packetwise exactness and induced transfer blocks. Do not reconstruct the now-proved nonsplit semisimple block.'}
write(R/'VERIFICATION.json',v)
report=f'''# Paper I completion: Block 08

**Result: PASS for the nonsplit semisimple seed formulas, compatible abstract decomposition construction, authenticated predecessor and upstream-only whole-project logical kernel replay.**

**Date:** 12 October 2026. **Version:** 0.8.0.

Five further proof-level publication records are covered and the Wedderburn-Artin classical input is integrated. This does not claim complete formalization of the expanded monograph. All predecessor mathematical sources and dependency pins remain unchanged.

## Mathematical completion

For an arbitrary semisimple Artinian ring A and finitely generated left module M, the new development constructs actual compatible presentations

    A ≃ product_i M_(d_i)(D_i),
    M ≃ direct_sum_i (D_i^(d_i))^(m_i),

and proves

    seedRank_A(M) = max_i ceil(m_i / d_i).

The D_i are arbitrary division rings, not assumed commutative. Positive matrix sizes, absent factors and zero/empty cases are handled explicitly. The upper and lower generator bounds use the literal left span of seed-matrix rows. The constructed regular-module equivalence takes actual natural columns and is proved A-linear.

The abstract existence theorem does not take a decomposition, spectral/multiplicity certificate or seed-rank equality as an input. The proved ring decomposition is integrated from the pinned Mathlib. The compatible module decomposition is constructed by decomposing into finite simple summands, projecting nontrivially into regular-module columns, using simplicity to obtain isomorphisms and regrouping the actual factor fibres.

For any Artinian ring, the formula on the literal radical quotient and module top computes the original module's seed rank. The finite-dimensional-algebra clause derives Artinianity internally. The printed split corollary has an exact original-ring/top wrapper in addition to the quotient-ring variant. Once a split presentation is supplied, algebraic closure is unnecessary.

The natural-module rank-one result and the multiplicity obstruction are now proved over arbitrary division rings, with actual finite-direct-sum and column-model equivalences. These are classical mathematical completions, not claims of new classical discoveries or an executable decomposition algorithm.

## Actual executed verification

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | {a['predecessor_payloads_authenticated']} / {a['predecessor_payloads_authenticated']} |
| Complete predecessor compared with original ZIP | {identity['all_files_identical']} / {identity['all_files_identical']} files |
| Authenticated predecessor source/object pairs | 46 / 46 |
| New production modules freshly compiled | 8 / 8 |
| Original normative contract retained | 35 rows, 84 mapped declarations |
| Public-or-coverage names resolved with types and axioms | {a['declaration_names_resolved']} / {a['declaration_names_resolved']} |
| Source-owned entries inventoried and axiom-audited | {a['owned_total']} / {a['owned_total']} |
| Logical production declarations rechecked | {a['owned_logical_total']} / {a['owned_logical_total']} |
| Inherited generated partial runtime helpers separately inventoried | {a['owned_runtime_only']} |
| Complete production-module closure replayed | 54 modules |
| New boundary module freshly compiled and replayed | 1 / 1 |
| New public mathematical boundary assertions | {a['new_boundary_assertions']} / {a['new_boundary_assertions']} |
| Logical replay entries including boundary helpers | {a['replay_checked_constants']} |
| Deliberately invalid controls rejected | {a['negative_controls']} / {a['negative_controls']} |
| Clean foreign-namespace control | Passed |
| Accepted expected-outcome commands | {len(a['checks'])} / {len(a['checks'])} |
| Final production source/object identities | 54 / 54 |
| Exact dependency Git revisions checked | 9 / 9 |
| Flat current source copies checked | 54 / 54 |

The seven mathematical modules and import-only root contain 44 public theorem declarations, nine definitions, six abbreviations and one scoped instance. The larger owned inventory includes private/generated supporting declarations. These are not counts of independent discoveries.

Only `propext`, `Classical.choice` and `Quot.sound` appear as transitive axioms. No production placeholder or custom axiom passed the audit. Invalid fixtures, audit I/O instrumentation and archived failed drafts are not production proofs.

**The 46 predecessor sources were not freshly recompiled in this run.** Their source/object bytes were authenticated and copied into isolated imports. The eight additions and new boundary module were freshly compiled in initially empty output directories. No development object substituted for an accepted new compilation. Every logical production declaration and boundary declaration was then replayed from an upstream-only starting kernel environment. Exact replay/ownership name sets match; the seven runtime helper names match separately. The corrupt-proof control was rejected by the actual kernel. Duplicate generated theorem data are accepted only when their type, universe parameters, theorem group and proof expression are identical.

## Boundary checks

The rational quaternion tests exercise genuinely noncommutative scalars. Three natural copies for M_2(H) have rank two, five have rank three, and one generator cannot produce three copies. Right-division coefficient order is verified and a reversed quaternion order is proved to fail.

A heterogeneous product has one quaternion factor and one rational factor. Its seed bound is a maximum, not a sum. The tests check literal regular columns, A-linearity, inverse identities, natural-factor simplicity and zero action from another factor. Absent multiplicities, empty products and zero modules are covered.

The zero-size counterexample shows that d>0 is essential to the row criterion and natural rank-one statement. The finite-algebra theorem is also instantiated on a noncommutative square-zero quaternion extension, with rational finite-dimensionality proved via its actual equivalence to H × H.

All these are exact Lean assertions. Missing finite-generation and semisimplicity assumptions, the false positive-size application, wrong ceiling/product counts and reversed coefficient use are deliberately rejected. Foreign-namespace custom axioms and a placeholder compiled with warnings disabled are rejected by the ownership guard. A clean foreign-namespace theorem is accepted.

## Publication coverage

All 108 stored statements, prose proofs and source-location/hash records are unchanged. Among the 69 proof-level records: **26 covered, 25 partial and 18 not mapped**. These are reviewed correspondence categories, not a blanket completion percentage.

The regular-module multiplicities lemma, full nonsplit semisimple theorem, algebraically closed split formula, full-matrix corollary and multiplicity-obstruction corollary move from partial to covered. The Wedderburn-Artin classical input becomes integrated. The original 35-row contract is not rewritten. The coverage generator is gated on final acceptance and was rerun byte-identically.

The positive-size natural-module convention remains explicit in the coverage notes. The split corollary's original-ring wording is handled by its own theorem rather than silently replaced by a quotient-ring statement.

## Failures and recoveries

The development index records 30 compiler receipts: 18 zero-exit exploratory runs and 12 rejected drafts/API probes. Two additional foreground interruptions have preserved snapshots/logs but no accepted exit receipt. No exit code is invented for them.

Rejected drafts involved API names, warning-fatal unused assumptions and instance syntax, noncommutative scalar-action rewriting, quotient ring-hom inverse inference, cardinal ceiling casts, universe elaboration, and test scalar/finiteness instances. Corrections preserved the intended mathematical hypotheses rather than weakening the audit. A streaming execution mode failed before execution; ordinary execution recovered the offline runtime. Two source inspections used the wrong directory and were corrected.

None of these exploratory or interrupted attempts contributes to PASS. The accepted launcher completed every required check. Its recorded elapsed time is {a['elapsed_seconds']} seconds, excluding development, runtime recovery and final packaging.

## Trust and reproduction

The combined `run_block08.sh` launcher was actually executed. Every command has an observed outcome and preserved log/hash. The runtime and all nine dependency revisions are authenticated. Mathlib's pinned cache is reused, not rebuilt or fully replayed. Replay uses Lean's own kernel, not an independent verifier. The TeX-to-Lean map is reviewed semantic correspondence, not kernel parsing of prose.

The source/evidence package includes the complete unchanged predecessor and a byte-identical flat 54-module source tree. The large portable runtime remains external. Publication PDFs and prior license-status records are unchanged. The constructions remain noncomputable; no executable Wedderburn, canonical-form or numerical eigensolver is claimed.

## Next restart

Stay on Paper I. Proceed to algebraic exact-sequence generator bounds, actual invariant-submodule packet restriction and quotient descent, then packetwise exactness and induced transfer blocks. Construct the quotient projector family from invariance, rather than assuming an unrelated quotient family. The semisimple, radical-top, primary, geometric and cyclic-classification blocks are now established and must not be reconstructed as missing work.

Other packet/functorial/topological and executable obligations remain in the coverage map. Papers II–XII have not been rerun in this sweep. `evidence/HANDOFF_POSTFLIGHT.json` records final process and file checks.
'''
(R/'COMPLETION_REPORT.md').write_text(report)
ledger=f'''# Paper I completion ledger v0.8.0

## Accepted checkpoint

Block 08: PASS for eight fresh production compilations, 46 authenticated predecessor source/object pairs, complete source-owned axiom audit, 25 new boundary assertions, all rejection controls and upstream-only whole-closure logical kernel replay. The entire 54-module closure was replayed, not freshly recompiled. See the hashed accepted receipt in VERIFICATION.json.

## Closed this block

Arbitrary-division-ring row generation and exact ceiling minimum; dependent product maximum; actual natural-module simplicity and regular column/direct-sum multiplicities; compatible finite module decomposition through simple summands and nonzero natural-column projections; actual Wedderburn-Artin existence integration; certificate-free semisimple, Artinian radical-top and finite-dimensional-algebra existence/formulas; exact original-ring and quotient-ring split wrappers; natural and repeated-natural-module corollaries.

No supplied decomposition, generator count or rank equality appears as an input to the final existence theorems. Noncommutative multiplication order and positive matrix-size guards remain explicit. The constructions are noncomputable, not executable decomposition algorithms.

## Publication status

108 unchanged records. Among 69 proof-level records: 26 covered, 25 partial, 18 not mapped. Five proof-level records move to covered and the Wedderburn-Artin classical input is integrated. Other statuses are not silently upgraded.

## Audit classification

{a['owned_total']} source-owned production entries consist of {a['owned_logical_total']} logical declarations and {a['owned_runtime_only']} inherited generated partial runtime helpers. The latter are inventoried but not proof-replayed. All logical production and boundary declarations are replayed with exact ownership name-set matching and an upstream-only starting environment. Only the standard three permitted axioms occur transitively.

## Failures

Twelve rejected development runs and two foreground interruptions are preserved separately from the accepted run. The interruptions have no invented process exit receipt. Operational recovery and all snapshot/log hashes are indexed under evidence/. No failed or exploratory run contributes to final acceptance.

## Exact next restart

Start with PSC-I-T-EXACT-SEQUENCE-BOUNDS, then PSC-I-T-QUOTIENT-PACKET-DESCENT and PSC-I-T-PACKET-EXACT-SEQUENCE, plus the restriction/quotient transfer-block corollary. Use the actual LinearProjectorFamily and invariant submodule, construct restriction/quotient maps, prove exact kernels and packet range identifications, and remove zero packets explicitly. Detailed APIs and scope boundaries are in CONTINUE_HERE.md.

Do not reconstruct the nonsplit semisimple formulas, radical lifting, intrinsic primary quotient, geometric formula, scalar-extension bridge or six-way cyclic criterion as missing work. Preserve prior mathematical sources and dependency pins.

## Series status

Other packet, functorial, topological and executable-algorithm obligations remain. Papers II–XII are not rerun in this sweep; historical evidence is preserved. Check evidence/HANDOFF_POSTFLIGHT.json for the final no-active-audit-process condition.
'''
(R/'PROGRESS_LEDGER.md').write_text(ledger)
write(R/'PROGRESS_LEDGER.json',{'version':'0.8.0','status':'PASS','paper':'I','block':8,'verification':'VERIFICATION.json','coverage':cov['proved_record_status_counts'],'changed_records':changes,'next_restart':v['next_restart'],'other_papers_in_this_sweep':'Papers II–XII not yet rerun','limits':a['limits']})
(R/'README.md').write_text('''# Komorebi Paper I completion, Block 08

Version 0.8.0, 12 October 2026. The nonsplit semisimple formulas and compatible abstract decompositions are verified. The expanded monograph is not entirely formalized.

Start with COMPLETION_REPORT.md for exact scope and observed checks, PROOF_GUIDE.md for the constructions, coverage/COVERAGE_108.md for each publication record, and CONTINUE_HERE.md for the next restart. VERIFICATION.json points to the hashed accepted command receipt.

## Layout

`source/current/` is a flat, byte-identical copy of all 54 production source modules. `source/extension/` contains the eight newly compiled modules. `predecessor/` is the complete unchanged Block 07 package, including historical sources, evidence and license records. `tests/` contains the new exact boundary suite, intentionally invalid controls and audit instrumentation. `evidence/` preserves accepted logs/objects, source snapshots, development failures, identity checks and receipts. `audit/` explains semantic and trust boundaries.

## Reproduce the accepted audit

From Linux or WSL with Python 3 and the pinned offline runtime:

    bash scripts/run_block08.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output

The output directory must not already exist. Do not run `lake update`. Runtime binaries and the large upstream dependency cache are external prerequisites, not embedded in this source/evidence archive. The runner freshly compiles the eight additions, authenticates 46 predecessor source/object pairs and replays the entire logical project closure from upstream-only imports. It does not rebuild every predecessor source or Mathlib.

The development recorder `scripts/devrun.py` retains its original session-specific environment path for provenance. It is not the portable reproduction entry point; use the shell launcher above.

All mathematical constructions are noncomputable. No executable decomposition/eigensolver, external independent verifier or full-monograph completion is asserted. Existing publication license-status records are inherited without a new license selection. Publication PDFs were not rebuilt.
''')
print('HANDOFF_DOCS_PASS',json.dumps(v['proof_level_status']), 'new_public',v['new_public_kind_counts'])

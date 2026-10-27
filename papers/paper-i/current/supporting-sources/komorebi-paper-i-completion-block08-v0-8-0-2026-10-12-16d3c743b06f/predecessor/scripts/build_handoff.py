#!/usr/bin/env python3
"""Build the documentation only after an accepted run; preserve failed-run evidence."""
from pathlib import Path
import collections, hashlib, json, re, shutil, subprocess, time, zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
audit=ROOT/'evidence/final_audit/verification.json'
a=json.loads(audit.read_text());assert a['status']=='PASS'
assert len(a['same_kernel_modules_replayed'])==46 and a['replay_owned_exact_name_set_match']
subprocess.run(['python3',str(ROOT/'scripts/update_coverage.py')],check=True)
cov=json.loads((ROOT/'coverage/COVERAGE_108.json').read_text())
assert cov['proved_record_status_counts']=={'covered':21,'partial':30,'not_mapped':18}

# Record every development receipt and actual source/log snapshot, not just successful trials.
dev=[]
for p in sorted((ROOT/'evidence/development').glob('*/receipt.json')):
 d=json.loads(p.read_text());d['receipt']=str(p.relative_to(ROOT));d['receipt_sha256']=sha(p)
 log=p.parent/'compile.log';d['log']=str(log.relative_to(ROOT));d['log_sha256']=sha(log)
 snapshots=[s for s in p.parent.glob('*.lean')]
 assert len(snapshots)==1 and sha(snapshots[0])==d['sha256']
 d['snapshot']=str(snapshots[0].relative_to(ROOT));dev.append(d)
counts=collections.Counter(d['exit'] for d in dev)
incidents=[
 {'id':'OP01','event':'An attempted streaming execution mode returned StreamingExecNotEnabledContainerError before command execution. Ordinary process execution was used instead.','evidence':'Observed tool response; no executed-command receipt exists.'},
 {'id':'OP02','event':'One upstream source-inspection path for quaternion definitions was wrong. The correct Mathlib/Algebra/Quaternion.lean path was used afterward.','evidence':'Observed inspection-tool output; no production or accepted audit artifact changed.'},
 {'id':'OP03','event':'An exploratory coverage-display script attempted to slice a null classical-input prose-proof field. The nullable field was handled correctly in the subsequent inspection.','evidence':'Observed inspection-tool output; publication records remained unchanged.'}
]
write_json(ROOT/'evidence/DEVELOPMENT_INDEX.json',{'schema':'paper-i-block07-development/0.7.0',
 'total_compiler_receipts':len(dev),'zero_exit_exploratory_runs':counts[0],
 'rejected_compiler_runs':sum(n for code,n in counts.items() if 0<code<124),
 'timed_out_driver_runs':counts[124],'all_unaccepted_as_final':True,'runs':dev,'operational_incidents':incidents,
 'failure_notes':[
  'The seed-rank proof initially used a self-repeating rewrite and exceeded recursion depth; replaced by an explicit target change and one rewrite.',
  'A dependent module was tried before its prerequisite had compiled; the prerequisite was repaired and rebuilt first.',
  'Warning-fatal drafts used letI in proof bodies or had unused declarations/variables; these were corrected without weakening warning policy.',
  'Test drafts needed a typed quaternion coordinate projection, the integer unit criterion, and explicit fraction-ring injectivity.',
  'Replay instrumentation drafts had syntax/indexing issues, then exposed generated partial helpers and one identical generated-theorem duplication.',
  'Two development drivers reached their explicit 180-second timeout and killed the processes. Longer explicit limits were used for subsequent runs.',
  'A stricter ownership gate rejected a previously undifferentiated generated partial helper. The corrected audit separately inventories exactly seven inherited helpers and matches the full logical replay name set.'
 ]})

# The complete predecessor must agree with its original delivered ZIP, including its manifest.
pzip=ROOT.parent/'Komorebi_Paper_I_Completion_Block06_v0.6.0_2026-10-11.zip'
with zipfile.ZipFile(pzip) as z:
 entries=[i for i in z.infolist() if not i.is_dir()]
 prefix=entries[0].filename.split('/')[0]+'/'
 expected={i.filename[len(prefix):]:i for i in entries}
 actual={str(p.relative_to(ROOT/'predecessor')):p for p in (ROOT/'predecessor').rglob('*') if p.is_file()}
 assert set(expected)==set(actual)
 for name,info in expected.items():assert hashlib.sha256(z.read(info)).hexdigest()==sha(actual[name]),name
write_json(ROOT/'evidence/PREDECESSOR_ZIP_IDENTITY.json',{'original_zip_sha256':sha(pzip),
 'identical_files_including_manifest':len(actual),'comparison':'Exact relative file-name set and SHA256 of every uncompressed payload','status':'PASS'})

# Check the coverage generator is deterministic and only its allowed correspondence fields changed.
paths=[ROOT/'coverage/COVERAGE_108.json',ROOT/'coverage/COVERAGE_108.md']
oldhash=[sha(p) for p in paths]
subprocess.run(['python3',str(ROOT/'scripts/update_coverage.py')],check=True)
assert [sha(p) for p in paths]==oldhash
write_json(ROOT/'evidence/COVERAGE_REPRODUCTION.json',{'status':'PASS','unchanged_statement_records':108,
 'byte_identical_rerun':True,'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in paths]})

prev=json.loads((ROOT/'predecessor/VERIFICATION.json').read_text())
changes=[{'stable_id':'PSC-I-CI-NAKAYAMA','from':'classical_input_not_fully_integrated','to':'classical_input_integrated'},
 {'stable_id':'PSC-I-T-MODULE-TOP','from':'not_mapped','to':'covered'},
 {'stable_id':'PSC-I-C-LOCAL-ALGEBRA-FORMULA','from':'not_mapped','to':'covered'}]
v={'schema':'paper-i-completion-block07/0.7.0','status':'PASS','business_date':'2026-10-11',
 'audit_scope':a['scope'],'accepted_run':{'path':'evidence/final_audit/verification.json','sha256':sha(audit)},
 'predecessor_payloads_authenticated':a['predecessor_payloads_authenticated'],
 'entire_predecessor_files_identical_to_zip':len(actual),
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
 'replay_starting_environment_excludes_project':a['replay_starting_environment_excludes_all_project_modules'],
 'replay_owned_exact_name_set_match':True,'identical_generated_theorem_duplicates':a['replay_identical_duplicate_entries'],
 'negative_controls_rejected':a['negative_controls'],'positive_foreign_namespace_control':1,
 'accepted_expected_outcome_commands':len(a['checks']),'source_object_postflight_pairs':a['postflight_source_object_pairs_verified'],
 'transitive_axioms':a['axioms'],'original_normative_contract_rows':prev['original_normative_contract_rows'],
 'original_mapped_declarations_resolved':prev['original_mapped_declarations_resolved'],
 'original_normative_contract_unchanged':True,'publication_records_unchanged':108,'proof_level_records':69,
 'proof_level_status':cov['proved_record_status_counts'],'coverage_status_changes':changes,
 'failed_work_index':'evidence/DEVELOPMENT_INDEX.json','dependencies':a['dependencies'],
 'lean_version':a['lean_version'],'runtime_archive_sha256':a['runtime_archive_sha256'],
 'elapsed_seconds_of_accepted_run':a['elapsed_seconds'],'limits':a['limits'],
 'next_restart':'Nonsplit semisimple matrix/product seed-rank formula and regular-module multiplicities, then abstract decomposition integration. The radical/top reduction is now proved.'}
# A byte-identical flat source tree avoids traversing nested predecessor packages.
current=ROOT/'source/current';current.mkdir(parents=True,exist_ok=True)
source_index=[]
for row in a['source_files']:
 target=(current/Path(*row['module'].split('.'))).with_suffix('.lean')
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/row['source'],target)
 assert sha(target)==row['source_sha256']
 source_index.append({'module':row['module'],'path':str(target.relative_to(ROOT)),
  'sha256':sha(target),'accepted_source':row['source']})
write_json(ROOT/'source/CURRENT_SOURCE_INDEX.json',{'status':'PASS','count':len(source_index),
 'description':'Byte-identical convenience copies of every accepted production source, not a separately rerun build.',
 'files':source_index})
(current/'README.md').write_text('Complete current 46-module source closure. Each Lean file is byte-identical to its accepted source. See ../CURRENT_SOURCE_INDEX.json and the root verification runner. This convenience copy is not a separate fresh build. The pinned runtime and Mathlib cache remain external.\n')
v['flat_current_source_copies_verified']=len(source_index)
write_json(ROOT/'VERIFICATION.json',v)

report=f'''# Paper I completion: Block 07

**Result: PASS for the noncommutative Nakayama/module-top/local-residue development, the authenticated predecessor, and upstream-only whole-project logical kernel replay.**

**Date:** 11 October 2026. **Version:** 0.7.0.

This closes two proof-level publication records and integrates the noncommutative Nakayama classical input. It does not claim that the entire expanded monograph is formalized. All predecessor mathematical sources and dependency pins remain unchanged.

## Mathematical completion

For an arbitrary unital ring R and a finitely generated left module M, with J = Jac(R), the source proves the exact set/family equivalence and canonical equality

    S generates M iff its image generates M/JM over R/J,
    seedRank_R(M) = seedRank_{{R/J}}(M/JM).

Any chosen lifts of a generating quotient family generate upstairs. The actual quotient scalar action, surjectivity and exact kernel are proved separately. The rank equality uses the existing canonical minimum, with both cardinal inequalities derived from genuine generating sets. A natural seedFinrank equality is also proved. No commutativity, Noetherian, finite length or semisimplicity assumption is imposed.

The Nakayama theorem itself accepts ANY left ideal I contained in the Jacobson radical and proves N + IM = M implies N = M. Only the later ring-quotient statements need I to be two-sided.

For a genuinely noncommutative local ring, the source establishes uniqueness of the maximal left ideal and maximality of the actual Jacobson radical. It constructs the division-ring structure on R/J internally, then proves

    seedRank_R(M) = dim_{{R/J}}(M/JM),

where dimension is LEFT vector-space dimension. A commutative residue field is not substituted, and no division-ring or rank certificate is supplied by the caller. These are classical mathematical results integrated into Paper I, not claims of new classical discoveries.

## Actual executed verification

| Check | Accepted result |
|---|---:|
| Predecessor manifested payloads authenticated | {a['predecessor_payloads_authenticated']} / {a['predecessor_payloads_authenticated']} |
| Entire predecessor compared with original ZIP | {len(actual)} / {len(actual)} files |
| Unchanged predecessor source/object pairs authenticated | 42 / 42 |
| New production modules freshly compiled | 4 / 4 |
| Original normative contract preserved | 35 rows, 84 mapped declarations |
| Public-or-coverage names resolved with types and axioms | {a['declaration_names_resolved']} / {a['declaration_names_resolved']} |
| Source-owned entries inventoried and axiom-audited | {a['owned_total']} / {a['owned_total']} |
| Logical production declarations rechecked | {a['owned_logical_total']} / {a['owned_logical_total']} |
| Generated partial runtime helpers separately inventoried | {a['owned_runtime_only']} |
| Production module closure replayed | 46 modules |
| Additional boundary module freshly compiled and replayed | 1 / 1 |
| New public mathematical boundary assertions | {a['new_boundary_assertions']} / {a['new_boundary_assertions']} |
| Total logical replay entries including boundary helpers | {a['replay_checked_constants']} |
| Deliberately invalid controls rejected correctly | {a['negative_controls']} / {a['negative_controls']} |
| Clean foreign-namespace control accepted | 1 / 1 |
| Accepted expected-outcome commands | {len(a['checks'])} / {len(a['checks'])} |
| Final production source/object identity checks | 46 / 46 |
| Exact dependency revisions checked | 9 / 9 |

The new source has 23 public theorem declarations, one definition and three abbreviations in three mathematical modules and one import-only root. Its {a['owned_new']} compiler-owned entries include generated supporting declarations. None of these counts measures independent mathematical discoveries.

**The 42 predecessor sources were not freshly recompiled in this block.** Their source/object bytes were authenticated. The four additions and the new boundary module were freshly compiled into isolated initially empty output directories. Development objects were not substituted for accepted new compilations. Earlier boundary suites remain historical evidence, not newly rerun test suites here.

Only `propext`, `Classical.choice` and `Quot.sound` appeared as transitive axioms. No authored production placeholder, custom axiom or prohibited unsafe/partial declaration passed the source and ownership gates. Intentionally invalid fixtures and audit I/O instrumentation are outside that production-source claim.

## A substantive audit classification correction

The broader object audit identified seven inherited compiler-generated partial runtime helpers ending in `_unsafe_rec`. Previous inventories included them without distinguishing them from logical declarations. Lean's official replay excludes such runtime implementations, so it would be inaccurate to call every one of the {a['owned_total']} inventory entries a separately kernel-replayed logical declaration.

This block explicitly separates **{a['owned_logical_total']} logical production entries** from **seven generated runtime helpers**, while retaining the source ownership and axiom inventory for all of them. An unexpected partial declaration is rejected. The names and classification are preserved in the accepted receipt and raw object inventory. No predecessor mathematical source needed repair.

The new replay starts from authenticated UPSTREAM imports only. It verifies that none of the 46 production modules, the new boundary module, or any selected project constant is already trusted in that starting environment. It then replays the entire logical dependency closure. The exact set of {a['replay_checked_constants']} rechecked names matches the ownership audit's logical production-plus-boundary set. The seven runtime names also match separately. This is a name-set check, not merely matching totals.

One duplicate generated theorem is merged only after its type, universe parameters, theorem group and proof expression are all shown identical. Incompatible duplicates are rejected. A separate corrupted-proof control presents the well-typed false claim 0 = 1 with the proof `Eq.refl 0`; the kernel rejects it. The accepted logs preserve the injection and rejection.

This strengthens project-dependency replay but remains Lean's SAME kernel, not an independently implemented verifier. No executable runtime-correctness claim is made for the generated helpers.

## Boundary tests

The noncommutative example is the trivial square-zero extension of the rational quaternion division ring. Its actual Jacobson radical is identified with the kernel of first-coordinate projection. The tests prove that epsilon is nonzero, epsilon squared is zero, the ring is noncommutative, its regular module has seed rank one, and its actual module top has residue-division-ring dimension one. The set {{1 + epsilon}} generates via the new lifting theorem.

The integer example has N = 3Z and I = 2Z: N is proper but N + I Z = Z. It demonstrates why the radical-containment hypothesis cannot be discarded.

The fraction field of Q[[t]], regarded as a Q[[t]]-module, has radical times module equal to the whole nonzero module. Its radical quotient has seed rank zero while the original module has nonzero seed rank. The test proves that the original module is not finitely generated. Thus finite generation is tested against a real mathematical counterexample, not only a missing typeclass instance.

Other assertions check actual quotient kernels/actions and zero-module behavior. All are exact Lean assertions, not numerical experiments.

## Publication coverage

All 108 stored statements, source proofs and source-location/hash records are unchanged. Among the 69 proof-level records there are now **21 covered, 30 partial and 18 not mapped**. These are correspondence categories, not an overall completion percentage.

`PSC-I-T-MODULE-TOP` and `PSC-I-C-LOCAL-ALGEBRA-FORMULA` move from not mapped to covered. `PSC-I-CI-NAKAYAMA` becomes classical_input_integrated. The semisimple formula remains partial, with its radical/top reduction now explicitly discharged. The separate original 35-row contract is preserved unchanged.

The deterministic coverage generator was actually rerun and produced byte-identical JSON and Markdown.

## Failures and recoveries

The development index records {len(dev)} compiler runs: {counts[0]} zero-exit exploratory runs, {sum(n for code,n in counts.items() if 0<code<124)} rejected drafts/instrumentation runs, and {counts[124]} explicit 180-second driver timeouts. Failed source snapshots and logs are retained.

Failures included a looping rewrite, a missing prerequisite object, warning-fatal local-instance/unused-variable issues, test API/type corrections, and replay-wrapper syntax/indexing. The stricter object checks exposed generated partial helpers and an identical generated theorem duplication; the final audit classifies and checks those cases rather than pretending they were mathematical source repairs. Longer explicit execution limits replaced the interrupted development runs. A streaming execution mode was unavailable before command execution; ordinary execution was used. Minor source/coverage inspection errors are recorded separately.

None of those development or operational attempts contributes to final acceptance. The composed launcher was actually executed and all accepted checks completed. The accepted run recorded {a['elapsed_seconds']:.3f} seconds, excluding runtime recovery, development, coverage review and packaging.

## Trust, reproduction and next restart

The exact compiler and nine dependency revisions were authenticated. Mathlib's cached objects were reused, not rebuilt or fully replayed. Publication correspondence is reviewed semantic matching, not kernel interpretation of TeX prose. Mathematical constructions remain noncomputable. Publication PDFs were not rebuilt, and the existing license-status records were not changed. The large portable runtime remains an external prerequisite.

Run `bash scripts/run_block07.sh /absolute/path/to/pinned-runtime /absolute/path/to/new-output` from Linux or WSL. The output must not already exist. Do not update the dependency pins.

The next target is the nonsplit semisimple matrix/product seed-rank formula and regular-module multiplicities over arbitrary division rings, followed by abstract decomposition integration. The general radical/top reduction is now proved and must not be redone as though still missing. Packet/functorial/topological and executable-algorithm obligations remain in the map. Papers II–XII have not been rerun in this sweep.

Final process, source/object and artifact checks are recorded in `evidence/HANDOFF_POSTFLIGHT.json`. The full restart instructions are in `CONTINUE_HERE.md`.
'''
(ROOT/'COMPLETION_REPORT.md').write_text(report)
ledger='''# Paper I completion ledger v0.7.0

## Accepted checkpoint

Block 07: PASS for four fresh production compilations, 42 authenticated predecessor source/object pairs, source-owned axiom inventory, 19 fresh boundary assertions, rejection controls and complete logical closure replay from an upstream-only environment. See the hashed accepted receipt in VERIFICATION.json.

## Closed this block

General noncommutative Nakayama lifting for a left ideal inside the Jacobson radical; the actual scalar quotient map and exact kernel; equivalence of generating sets/families and arbitrary lift generation; canonical cardinal and natural seed-rank equality modulo the radical; noncommutative maximal-left-ideal uniqueness; internally constructed division ring on the actual radical quotient; local left-dimension formula.

No commutativity, semisimplicity or supplied rank/quotient/division-ring certificate is an input to the general module-top theorem. The local formula assumes IsLocalRing, not a commutative residue-field construction.

## Publication status

108 unchanged publication records. Among 69 proof-level records: 21 covered, 30 partial, 18 not mapped. The module-top theorem and local-algebra corollary are covered. The noncommutative Nakayama classical input is integrated. The semisimple formula remains partial, although its radical/top reduction is now available.

## Audit classification correction

The complete source-owned inventory has 1,544 entries: 1,537 logical production declarations and seven separately recorded inherited generated partial runtime helpers. The latter were previously not distinguished in the totals and are not proof-replayed. All logical production declarations and 45 boundary declarations were checked together from a starting kernel environment that contains no project modules. The exact replay name set matches the ownership inventory. The seven helper names match separately.

## Failures

All development compiler receipts and failed snapshots are indexed in evidence/DEVELOPMENT_INDEX.json. Rejected drafts, explicit driver timeouts and operational failures do not contribute to the accepted PASS. The replay's deliberately corrupted proof is an expected rejection control, not an unresolved failure.

## Next restart

Stay on Paper I. Prove the nonsplit semisimple matrix/product generator formula and the regular-module multiplicity equivalence over arbitrary division rings, then integrate the abstract decomposition inputs. Reuse the new module-top reduction. Preserve left/right multiplication order and do not use an Algebra instance requiring commutative scalars for a genuinely noncommutative division ring. See CONTINUE_HERE.md.

Do not reconstruct the already-proved intrinsic primary quotient, geometric formula, scalar extension, six-way cyclic criterion or radical lifting as missing work.

## Other work

Expanded packet/functorial/topological and executable algorithm obligations remain. Papers II–XII are not rerun in this sweep. Their historical evidence is preserved, not revoked. Final process and hash checks are in evidence/HANDOFF_POSTFLIGHT.json.
'''
(ROOT/'PROGRESS_LEDGER.md').write_text(ledger)
write_json(ROOT/'PROGRESS_LEDGER.json',{'version':'0.7.0','paper':'I','block':7,'status':'PASS',
 'verification':'VERIFICATION.json','coverage':'coverage/COVERAGE_108.json','proof_level_status':cov['proved_record_status_counts'],
 'completed_this_block':['noncommutative Nakayama','module-top generating-family and seed-rank equalities','local residue-division-ring formula'],
 'next_restart':v['next_restart'],'other_papers_rerun_in_this_sweep':[]})
(ROOT/'README.md').write_text('''# Komorebi Paper I completion, Block 07

This package contains the noncommutative Nakayama/module-top/local-residue completion and its actual verification evidence. It is not a claim that the whole expanded monograph is fully formalized.

Read COMPLETION_REPORT.md for executed results and limits, PROOF_GUIDE.md for mathematics, coverage/COVERAGE_108.md for record-level status, and CONTINUE_HERE.md for the exact restart. VERIFICATION.json points to the hashed accepted command receipt.

The complete unchanged Block 06 is under predecessor/. New mathematical sources are under source/extension/. The complete current 46-module source tree is available as byte-identical convenience copies under source/current/. Accepted objects and logs are under evidence/final_audit/. Rejected development snapshots and receipts are retained under evidence/development/. Disposable development objects are not release inputs and may be omitted; no such object substitutes for the accepted new compilations.

Run `bash scripts/run_block07.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output` on Linux or WSL. The output must be new. The exact large portable compiler/dependency cache is external. Do not run lake update.

The ownership inventory distinguishes 1,537 logical production entries from seven inherited generated partial runtime helpers. Whole-closure replay checks every logical entry from an upstream-only starting environment, not every serialized runtime implementation. Lean's own kernel is used, not an independent verifier. Upstream Mathlib is authenticated and reused, not rebuilt.

Existing publication-license status is preserved. No new license selection or publication-PDF rebuild is made in this Lean completion block.
''')
print('HANDOFF_DOCUMENTS_READY',v['accepted_expected_outcome_commands'],v['proof_level_status'])

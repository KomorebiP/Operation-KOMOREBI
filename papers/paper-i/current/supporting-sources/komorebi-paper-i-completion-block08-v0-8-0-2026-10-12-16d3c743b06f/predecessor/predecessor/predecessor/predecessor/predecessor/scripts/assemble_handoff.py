#!/usr/bin/env python3
"""Create final reports only from a completed successful execution receipt."""
from pathlib import Path
import collections,hashlib,json,re,time
root=Path(__file__).resolve().parents[1]
run=root/'evidence/final_attempt01'
r=json.loads((run/'verification.json').read_text())
if r['status']!='PASS':raise SystemExit('Refusing to publish a non-PASS run')
if len(r['source_files'])!=28 or r['replayed_production_modules']!=28:raise SystemExit('Incomplete source closure')
# All individual check logs must still match their actual receipts.
for c in r['checks']:
 if not c['passed']:raise SystemExit('Failed expected-outcome command')
 if hashlib.sha256((run/c['log']).read_bytes()).hexdigest()!=c['log_sha256']:raise SystemExit('Mutated command log')
for s in r['source_files']:
 if hashlib.sha256((root/s['source']).read_bytes()).hexdigest()!=s['source_sha256']:raise SystemExit('Mutated mathematical source')
 if hashlib.sha256((run/s['object']).read_bytes()).hexdigest()!=s['object_sha256']:raise SystemExit('Mutated compiled object')
# Final tests must equal the actual frozen pre-test snapshots.
for s in json.loads((run/'FINAL_TEST_INPUT_HASHES.json').read_text())['files']:
 if hashlib.sha256((root/s['path']).read_bytes()).hexdigest()!=s['sha256']:raise SystemExit('Mutated test input')
# The actual executed launcher and verification script were also snapshotted.
for name in ['scripts/run_block03.sh','scripts/verify_block03.py']:
 if (root/name).read_bytes()!=(run/'execution_inputs'/name).read_bytes():raise SystemExit('Executed runner source changed')

cov=json.loads((root/'coverage/COVERAGE_108.json').read_text())
assert cov['proved_record_status_counts']=={'not_mapped':20,'partial':33,'covered':16}
assert cov['proved_record_count']==69 and len(cov['records'])==108
assert hashlib.sha256((root/'coverage/COVERAGE_108.json').read_bytes()).hexdigest()==r['coverage_sha256']
new=[s for s in r['source_files'] if s['new_in_block03']]
development=json.loads((root/'evidence/DEVELOPMENT_INDEX.json').read_text())['attempts']
failed=[d for d in development if d['exit_code']!=0]
proofcount=r['boundary_theorems_original']+r['boundary_theorems_block02']+r['boundary_theorems_block03']
# Read process state rather than claiming that a running computation has stopped.
procfile=root/'evidence/final_attempt01_process.json';proc=json.loads(procfile.read_text());pid=proc['pid']
pstat=Path(f'/proc/{pid}/stat')
state=pstat.read_text().split(') ')[1].split()[0] if pstat.exists() else 'ABSENT'
if state not in ('ABSENT','Z','X'):raise SystemExit(f'Launcher is still active: {pid} {state}')
proc.update(state='FINISHED',observed_process_state=state,observed_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),final_receipt_status='PASS',exit_code_observed_directly=False)
procfile.write_text(json.dumps(proc,indent=2)+'\n')
(root/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n')
post={'status':'PASS','verified_command_logs':len(r['checks']),'source_and_object_identity_modules':len(r['source_files']),'frozen_test_inputs':len(json.loads((run/'FINAL_TEST_INPUT_HASHES.json').read_text())['files']),'executed_launcher_source_identical':True,'exact_coverage_counts_checked':True,'no_active_launcher':True,'process_observation':state}
(root/'evidence/POSTFLIGHT.json').write_text(json.dumps(post,indent=2)+'\n')
report=f'''# Paper I completion: Block 03

**Result: PASS for the full current 28-module source closure and the new primary-block/invariant-factor extension.**

This is a verified completion block, not full formalization of the expanded monograph. The original 35-row component and all Block 02 mathematical sources are unchanged.

## Mathematical results

For every finite-dimensional operator T over an arbitrary field, the new Lean code constructs the actual polynomial-module decomposition into positive irreducible-power quotients and proves

    seedRank_{{k[T]}}(V) = maximum number of primary blocks with the same irreducible ideal.

The proof supplies the decomposition, residue-field lower bounds and Chinese-remainder shared generators internally. It does not receive the desired rank equality, an eigenbasis, a Jordan basis or extraction certificates from the caller. Nonlinear irreducible factors are included. Associated irreducibles are grouped by their principal ideals. Exponent-zero factors are removed as zero modules.

The canonical rank is proved equal to this count, and the maximum is proved independent of the chosen actual primary presentation. Cyclicity is equivalent to having no repeated primary label. This criterion is linked to the already proved minimal-polynomial/characteristic-polynomial equivalence.

The conditional invariant-factor corollary is also proved: an actual nonconstant divisibility-chain presentation with r factors has seed rank r. Its count is derived from coordinate generators and a common irreducible residue-field quotient, not assumed. Existence or computation of a sorted invariant-factor presentation is not asserted by that conditional theorem.

These are classical mathematical results integrated into Paper I's actual objects and seed-rank definitions. Declaration counts are not claims of independent novelty.

## Actual executed verification

| Check | Result |
|---|---:|
| Preserved predecessor manifested payloads | {r['predecessor_payloads_verified']} / {r['predecessor_payloads_verified']} |
| Freshly compiled production source files | 28 / 28 |
| Original + Block 02 + Block 03 modules | 20 + 4 + 4 |
| New mathematical modules / import-only root | 3 / 1 |
| Original normative contract rows | 35 / 35 |
| Original mapped declarations resolved | {r['original_mapped_declarations']} / {r['original_mapped_declarations']} |
| Public-or-coverage declaration names resolved | {r['resolved_public_or_coverage']} |
| Complete compiler-owned declaration audit | {r['owned_total']} / {r['owned_total']} |
| Entries owned by new Block 03 modules | {r['owned_new']} |
| New public theorem / definition / structure declarations | 32 / 10 / 1 |
| Exact same-kernel production-module replays | 28 / 28 |
| Additional regression-module replay | 1 / 1 |
| Original + Block 02 + Block 03 mathematical assertions | 4 + 12 + {r['boundary_theorems_block03']} = {proofcount} |
| Deliberately invalid controls rejected as intended | {r['rejection_controls']} / {r['rejection_controls']} |
| Positive foreign-namespace audit control | 1 / 1 |
| Accepted expected-outcome commands, including environment checks | {len(r['checks'])} / {len(r['checks'])} |
| Post-replay source/object identity checks | 28 / 28 |
| Exact dependency Git revisions checked | {len(r['dependencies'])} / {len(r['dependencies'])} |

The only reported transitive axioms were {', '.join('`'+a+'`' for a in r['axioms'])}. No production placeholder or additional custom axiom passed the gate. The owned inventory includes definitions, private/generated proofs, structure fields, constructors and recursors. It is not a count of independent theorems.

The composed `run_block03.sh` launcher was actually executed. It built all project modules into a new, initially empty object directory and did not import saved predecessor project objects. Its recorded wall time was {r['elapsed_seconds']:.3f} seconds. This excludes development, runtime recovery and final packaging. Every command receipt, full log, source snapshot and final object is preserved.

## Exact mathematical boundaries

The full printed single-operator theorem defines each multiplicity as

    dim_{{k[t]/(p)}}(X_p / p(T)X_p).

This block proves the actual primary-block count formula and constructs surjective residue-field maps. It has not yet identified the grouped primary factor with the literal intrinsic X_p or proved that the residue map's kernel is exactly p(T)X_p. Surjectivity is not silently treated as that kernel/quotient identification. Individual intrinsic multiplicities are therefore not yet identified, even though their presentation maximum is proved invariant.

The arbitrary algebraically closed, non-diagonalizable eigenspace formula and the complete scalar-extension clause of the six-way cyclic criterion also remain. The earlier self-adjoint result remains verified and unchanged.

All new constructions are noncomputable. There is no executable factorization routine, invariant-factor algorithm, eigensolver or extraction/performance guarantee.

## Publication coverage delta

All 108 publication statements and their source-proof fields are unchanged. Exactly one proof-level record moves from partial to covered: `PSC-I-C-INVARIANT-FACTOR-COUNT`, at its printed conditional scope. Four other entries receive more precise progress and remaining-work notes without a status upgrade.

The 69 proof-level records now have **16 covered, 33 partial and 20 not mapped**. These are different units from the 35-row formal contract. The primary-count construction is substantive progress even though the more expansive intrinsic-quotient record remains partial. No blanket completion percentage is inferred from these counts.

The deterministic coverage generator was rerun, producing byte-identical JSON and Markdown maps. The original normative row sequence and all 84 declaration names were checked directly against the mapped-type file.

## Tests and failed development attempts

The new suite contains {r['boundary_theorems_block03']} exact Lean assertions. They cover nonlinear irreducibility over the rationals, repeated-primary lower bounds, one nonlinear squared block versus its larger base-field dimension, the zero module, empty label sets, dropped exponent-zero factors, associate labels, invariant-factor chains and shared CRT generation across coprime factors.

Four new invalid applications are rejected: treating a zero exponent as positive, using base-field residue dimension as the seed count, using a two-generator witness as a one-generator witness, and supplying reflexive divisibility where a full invariant-factor chain is required. The earlier seven rejection controls and their positive audit control were also rerun.

The development log records {len(failed)} rejected runs among {len(development)} recorded development compilations, including API probes and intermediate typing, simplification, dependent-index and proof-witness errors. The accepted sources were subsequently rerun cleanly. No rejected or exploratory run is counted toward PASS.

A separate foreground status-polling command was reported timed out by the tool. It did not interrupt the Lean verification process. The monitoring incident is retained separately and is not counted as a proof-check result.

Three negative fixture expressions were changed before their execution to use explicit applications, selecting the compiler's `Application type mismatch` diagnostic rather than a differently capitalized bare type-mismatch message. Their before/after hashes and snapshots are preserved. This adjusted the diagnostic form of the same invalid mathematical uses, not the production proofs or the required rejection outcomes.

## Trust, reproduction and next restart

The pinned Lean runtime was restored from the authenticated offline archive and bound to the same compiler and dependency versions as the predecessor. Cached upstream Mathlib objects were reused rather than rebuilt or fully replayed. The module replays use Lean's own kernel, not an independently implemented verifier. The TeX-to-Lean map is a reviewed semantic artifact, not a kernel interpretation of prose.

The compact package contains the complete predecessor, new source, tests, audit tools, compiled objects, logs, failed-development records, coverage map and progress ledger. The large runtime remains an external prerequisite. Publication PDFs were not rebuilt. License-status records are inherited unchanged.

**Next restart:** prove the intrinsic-primary and exact residue-kernel/quotient identification, then derive the arbitrary-operator geometric formula and complete the remaining cyclic-criterion clauses. Papers II–XII have not been rerun in this sweep.

No audit or compiler process remains active at this handoff. See `CONTINUE_HERE.md` for exact source paths and the next proof obligations.
'''
(root/'REPORT.md').write_text(report)
ledger={'schema':'paper-i-completion-ledger/0.3.0','block':3,'status':'VERIFIED_EXTENSION_NOT_FULL_MONOGRAPH_COMPLETION','verification_status':'PASS','source_closure_modules':28,'original_contract_rows':35,'predecessor_unchanged':True,'new_public_theorems':32,'new_public_definitions':10,'new_public_structures':1,'covered_proof_records':16,'partial_proof_records':33,'not_mapped_proof_records':20,'completed':['Actual arbitrary-field polynomial-module primary presentation with positive exponents','Residue-field lower bounds, including nonlinear irreducibles','CRT shared-generator upper bounds and exact minimum','Canonical operator-algebra seed-rank formula from primary block count','Presentation-independent primary maximum','Cyclicity iff distinct primary labels, composed with minpoly/charpoly equality','Conditional invariant-factor count at printed scope','Fresh 28-module compilation, ownership audit, serial replay and controls'], 'remaining_immediate':['Identify grouped primary factors with the intrinsic operator primary submodule X_p','Prove residue-map kernel equals p(T)X_p','Construct induced residue-field quotient equivalence and identify every intrinsic multiplicity','Derive arbitrary algebraically closed operator eigenspace formula','Assemble full six-way cyclic criterion including scalar extension'],'remaining_other':['Nonsplit semisimple and module-top/Nakayama constructions','Expanded packet, functorial and topological statements tracked record by record','Executable exact algorithms','Final audits of Papers II–XII'], 'restart_file':'CONTINUE_HERE.md','no_active_audit_process':True,'failures_retained':len(failed),'rejected_development_runs_count_toward_pass':False}
(root/'PROGRESS_LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n')
(root/'PROGRESS_LEDGER.md').write_text('''# Paper I completion ledger v0.3.0

## Accepted checkpoint

Block 03: PASS for the full current 28-module closure. The original 35-row contract and all Block 02 sources remain unchanged. New work proves the actual arbitrary-field primary-block generator formula, residue-field lower bounds, CRT generators, canonical seed-rank identification, presentation-independent maximum, primary cyclicity criterion and the displayed conditional invariant-factor count.

The new source contains 32 public theorem declarations, 10 definitions and one presentation structure. These counts are not counts of independent discoveries. See VERIFICATION.json for actual compiler-owned inventory and execution results.

## Publication map

108 unchanged records. Among 69 proof-level records, 16 are covered, 33 partial and 20 not mapped. Only the invariant-factor-count corollary changes status in this block. The more expansive general single-operator theorem still needs its intrinsic quotient identification.

## Next restart

Stay on Paper I. Identify the grouped primary product with the actual intrinsic X_p, prove the residue-map kernel is p(T)X_p, and derive the induced residue-field quotient equivalence. Then finish the arbitrary algebraically closed eigenspace formula and the scalar-extension clause of the cyclic criterion.

Do not repeat the primary existence, CRT or residue lower-bound work as though it were still missing. Those constructions are now proved. Do not treat residue-map surjectivity as an already-proved kernel equality.

## Other work

Nonsplit semisimple, module-top/Nakayama, expanded packet/functorial/topological and executable algorithm obligations remain in the coverage map. Papers II–XII have not been rerun in this sweep. Historical evidence is preserved, not revoked.

Rejected development and diagnostic attempts are retained separately from the accepted final run. No compiler or audit process remains active at handoff. Continue from CONTINUE_HERE.md.
''')
index={'schema':'paper-i-run-index/0.3.0','authoritative_current_run':{'path':'evidence/final_attempt01','status':'PASS','verification_sha256':hashlib.sha256((run/'verification.json').read_bytes()).hexdigest(),'composed_launcher_executed':True},'postflight':'evidence/POSTFLIGHT.json','development_index':'evidence/DEVELOPMENT_INDEX.json','development_runs':len(development),'development_rejected_runs':len(failed),'control_input_amendments':'evidence/final_attempt01/execution_inputs_amendment/AMENDMENTS.json','inherited_predecessor_runs':'predecessor/evidence/RUN_INDEX.json','no_active_process':True}
(root/'evidence/RUN_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
print('REPORTS_CREATED_FROM_ACCEPTED_PASS',len(r['checks']))

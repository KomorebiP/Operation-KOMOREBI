from __future__ import annotations
from pathlib import Path
import hashlib,json,collections,time,subprocess,shutil,zipfile,os
O=Path('/mnt/data/Komorebi_Paper_I_Final_Lean_Audit_v0.1.0_2026-10-10')
P=Path('/mnt/data/predecessor/Komorebi_Paper_I_Monograph_2026-10-08')
K=Path('/mnt/data/runtime/Komorebi_Portable_Lean_4.34.0-rc2')
archive=Path('/mnt/data/input/Komorebi_Paper_I_Final_Three_Companion_Set_2026-10-05.zip')
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads((O/p).read_text())
def write(p,obj): (O/p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
main=load('evidence/fresh_main_retry/fresh_verification.json')
extra=load('evidence/additional_attempt3/verification.json')
controls=load('evidence/controls_attempt1/verification.json')
assert main['status']==extra['status']==controls['status']=='PASS'
assert len(main['modules'])==20 and main['mapped_rows']==35 and main['mapped_declarations']==84
assert extra['owned_declarations']==1152 and extra['replayed_modules']==20
assert controls['boundary_theorems']==4 and controls['negative_guard_controls']==2
for d in (main,extra,controls):assert all(c['passed'] for c in d['checks'])
owned=load('evidence/additional_attempt3/owned_declarations.json')
assert len(owned)==1152
source_inv=load('evidence/static/source_inventory.json');assert source_inv['status']=='PASS'
post=[]
for m in main['modules']:
 rel=Path(*m['module'].split('.')).with_suffix('.lean');src=O/'source/main'/rel;obj=O/'evidence/fresh_main_retry/objects'/rel.with_suffix('.olean')
 rec={'module':m['module'],'source_sha256':sha(src),'source_matches_compile_receipt':sha(src)==m['source_sha256'],'source_matches_predecessor':sha(src)==sha(P/'source/traditional_v1.3.1/formalization/lean'/rel),'object_sha256':sha(obj),'object_matches_compile_receipt_after_replay':sha(obj)==m['object_sha256']}
 assert rec['source_matches_compile_receipt'] and rec['source_matches_predecessor'] and rec['object_matches_compile_receipt_after_replay'];post.append(rec)
write('evidence/static/post_audit_identity.json',{'status':'PASS','modules':post})
assert sha(archive)=='f5120627cc47a3cb255db1cc1cfd107f759f65658903f4da00bdf7760decd710'
paths=['run.sh','toolchain/bin/lean','toolchain/bin/lake','toolchain/bin/leanchecker','toolchain/lib/lean/LeanChecker.olean','toolchain/src/lean/LeanChecker.lean','workspace/lean-toolchain','workspace/lake-manifest.json']
runtime={'runtime_root':str(K),'kit_archive_sha256':'66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34','files':[{'path':p,'bytes':(K/p).stat().st_size,'sha256':sha(K/p)} for p in paths], 'lean_version':main['lean_version'],'dependencies':main['dependencies'],'memory_ceiling_bytes':int(Path('/sys/fs/cgroup/memory.max').read_text()),'memory_events_final':Path('/sys/fs/cgroup/memory.events').read_text(),'verification_scope':'Authenticated archived kit and exact dependency revisions. Pinned upstream cache reused, not rebuilt.'}
write('evidence/environment/runtime_bindings.json',runtime)
write('evidence/SUCCESSFUL_RUN_BINDINGS.json',{'main':'fresh_main_retry/fresh_verification.json','additional':'additional_attempt3/verification.json','controls':'controls_attempt1/verification.json','audit_source_hashes':{str(p.relative_to(O)):sha(p) for p in sorted((O/'tests').rglob('*.lean'))},'script_hashes':{str(p.relative_to(O)):sha(p) for p in sorted((O/'scripts').glob('*')) if p.is_file()}})
failures=[
 {'id':'E01','status':'ENVIRONMENT_DOWNLOAD_FAILURE','what':'Direct official compiler download could not resolve github.com.','recovery':'Authenticated and restored the matching seven-part offline kit from Library.','evidence':'evidence/environment/official_release_probe.log'},
 {'id':'E02','status':'INTERRUPTED_INITIAL_BUILD','what':'The first foreground invocation hit the 180-second container command limit after one module had compiled. No proof error was reported.','recovery':'Reran all 20 modules in a distinct empty output directory.','evidence':'evidence/fresh_main/INTERRUPTION.json'},
 {'id':'E03','status':'FAILED_DIAGNOSTIC_INVOCATION','what':'The pinned leanchecker does not implement --help. That invocation selected a broad default target, started concurrent replay, and was killed by the memory limit.','recovery':'Used the pinned replayFromImports API with one explicit module per serial process.','evidence':'evidence/environment/leanchecker_help_attempt.json'},
 {'id':'E04','status':'CONTROLLED_STOP_OF_AUDIT_INSTRUMENTATION','what':'Stopped the first extra-audit program to avoid recomputing the module-name array for each imported constant and removed a redundant blanket Lean import.','recovery':'Cached module names once and reran the audit. No production source changed.','evidence':'evidence/additional_attempt1/INSTRUMENTATION_CHANGE.json'},
 {'id':'E05','status':'REPLAY_WRAPPER_TYPE_ERROR','what':'The first exact-replay wrapper inferred BaseIO from IO.getEnv and did not typecheck with the IO replay operation.','recovery':'Added an explicit IO Unit annotation and reran the ownership audit plus all 20 replays.','evidence':'evidence/additional_attempt2/INSTRUMENTATION_CHANGE.json'}]
write('evidence/RUN_INDEX.json',{'active_processes_at_completion':False,'runs':[{'path':'fresh_main','effective_status':'INTERRUPTED','raw_receipt_note':'The raw pre-interruption receipt says RUNNING. INTERRUPTION.json records termination; it is not a current running job.'},{'path':'fresh_main_retry','effective_status':'PASS'},{'path':'additional_attempt1','effective_status':'CONTROLLED_STOP_RECORDED_AS_FAIL'},{'path':'additional_attempt2','effective_status':'OWNERSHIP_PASS_REPLAY_WRAPPER_FAIL'},{'path':'additional_attempt3','effective_status':'PASS'},{'path':'controls_attempt1','effective_status':'PASS'}],'incidents':failures})
# Verify Python syntax without depositing bytecode and validate the shell wrapper.
for p in (O/'scripts').glob('*.py'):compile(p.read_text(),str(p),'exec')
r=subprocess.run(['bash','-n',str(O/'scripts/run_audit.sh')],capture_output=True,text=True);assert r.returncode==0
write('evidence/static/runner_syntax.json',{'status':'PASS','python_files':[p.name for p in sorted((O/'scripts').glob('*.py'))],'shell_wrapper':'scripts/run_audit.sh','shell_syntax_returncode':r.returncode,'wrapper_execution_scope':'All three constituent verifiers ran successfully. The composed shell wrapper was syntax checked; it was not separately used to duplicate the full build.'})
checks=[*main['checks'],*extra['checks'],*controls['checks']]
verification={
 'schema':'komorebi.paper_i.final_lean_audit.v1','audit_version':'0.1.0','date':'2026-10-10','status':'PASS_SCOPED_PAPER_I_FORMAL_COMPONENT',
 'paper':'Projector-Resolved Seed Calculus I: Typed operator systems, seed rank, and exact packet coordinates','formal_component_version':'1.0.2',
 'authoritative_package':{'file_id':'file_000000000854820ea5ba38699f93b80f','version_id':'4','filename':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'predecessor_manifest_entries_verified':837},
 'metrics':{'production_lean_files':20,'production_source_lines':7125,'contract_rows':35,'mapped_declarations':84,'mapped_theorem_declarations':73,'mapped_definitions_or_equivalences':11,'namespace_entries_audited':1126,'source_owned_entries_audited':1152,'additional_private_entries':25,'additional_other_namespace_entry':1,'declaration_kind_counts':dict(collections.Counter(x['kind'] for x in owned)),'modules_recompiled_from_empty_local_output':20,'modules_same_kernel_replayed':20,'negative_controls_rejected_as_expected':4,'positive_foreign_namespace_control':1,'boundary_regression_theorems':4,'successful_expected_outcome_command_checks':len(checks),'successful_command_seconds':round(sum(c['seconds'] for c in checks),3),'pinned_dependency_revisions_checked':9},
 'observed_axioms':sorted({a for x in owned for a in x['axioms']}),
 'production_proofs_modified':False,'production_definitions_modified':False,'dependency_pins_modified':False,
 'stages':{'archive_and_source_identity':'PASS','clean_strict_compile':'PASS','all_mapped_types_and_axioms':'PASS','namespace_axiom_gate':'PASS','module_owned_axiom_gate':'PASS','serial_same_kernel_replay':'PASS','compiler_rejection_controls':'PASS','audit_gate_controls':'PASS','boundary_consumers':'PASS','semantic_scope_review':'COMPLETED_WITH_EXPLICIT_BOUNDARIES','post_replay_source_object_identity':'PASS'},
 'evidence':{s:{'path':p,'sha256':sha(O/p)} for s,p in {'main':'evidence/fresh_main_retry/fresh_verification.json','additional':'evidence/additional_attempt3/verification.json','controls':'evidence/controls_attempt1/verification.json','crosswalk':'audit/DECLARATION_CROSSWALK.json','semantics':'audit/SEMANTIC_REVIEW.md','post_identity':'evidence/static/post_audit_identity.json'}.items()},
 'certificate_explicit_contract_rows':[10,13,14,32,35],
 'limits':['The 35-row formal contract is not the expanded monograph\'s 108-record inventory.','Classical decomposition, canonical-form, and spectral certificates remain explicit inputs where stated.','Mathlib and upstream dependencies were authenticated and reused, not freshly rebuilt or independently re-proved.','Replay uses the pinned official Lean kernel, not an independently implemented verifier.','Mathematical algorithm specifications do not certify an extracted eigensolver, numerical tolerances, or performance.','No new compilation of the historical attached v0.2.0 ancestor tranche is claimed.','No audit of Papers II–XII was performed in this sweep yet.','Original publication licensing status remains unchanged; this is a formal-component audit, not blanket publication clearance.'],
 'failed_or_interrupted_attempts':failures,'remaining_in_scope_proof_obligations':[], 'next_restart':'Paper II: recover the latest authoritative source package and apply the same source-preserving audit workflow.',
 'finished_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
write('VERIFICATION.json',verification)
ledger={'schema':'komorebi.core_papers.final_lean_audit.progress.v1','version':'0.1.0','updated_utc':verification['finished_utc'],'current_block':'Paper I / Block 01','current_block_status':verification['status'],'verified_component':'Paper I formal v1.0.2, 20 source files, 35 rows, 84 mapped declarations','production_changes':[], 'completed':['Recovered and authenticated the current Paper I package and matching offline runtime.','Validated all 837 predecessor manifest entries and preserved all 20 Lean source hashes.','Freshly compiled all 20 source files with warnings as errors.','Resolved all 84 mapped declarations and audited all 35 contract rows.','Repeated the inherited 1126-entry gate and expanded it to 1152 source-owned entries.','Replayed all 20 compiled modules through the pinned official kernel.','Passed four intended rejection controls, one positive guard control, and four boundary theorems.','Retained interrupted/failed attempts and recorded exact recoveries.','Created declaration crosswalk, semantic review, run receipts, and replay instructions.'], 'papers':[{'paper':roman,'status':'PASS_SCOPED_CURRENT_CONTRACT' if i==0 else 'NOT_AUDITED_IN_THIS_SWEEP'} for i,roman in enumerate(['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'])], 'remaining_current_contract_obligations':[],'outside_current_contract':['Expanded 108-record formalization','Existence/classification input constructions beyond certificate-explicit statements','Executable extraction and numerical implementation correctness','Independent upstream/kernel re-verification','Publication license selection'], 'incidents':[x['id'] for x in failures],'next_restart':verification['next_restart'],'preserve_next_time':['Do not reinterpret 1152 inventory entries as 1152 novel theorems.','Do not promote scoped certificate results to unqualified classification proofs.','Use source-module ownership, not only namespace prefixes, for the axiom inventory.','Keep fresh output directories and preserve every failed attempt separately.','Avoid the pinned leanchecker no-argument or --help path under low memory.','No work remains running after this handoff.']}
write('PROGRESS_LEDGER.json',ledger)
(O/'PROGRESS_LEDGER.md').write_text('''# Final Lean audit sweep: progress ledger v0.1.0

## Current checkpoint

**Paper I, Block 01: PASS for the current 35-row formal contract.**

All 20 production files compiled from an empty local output directory. All 84 mapped declarations resolved. The namespace audit covered 1,126 entries; the expanded source-owned audit covered 1,152. All 20 modules passed same-kernel replay. Four rejection controls, one positive guard control, and four mathematical boundary theorems passed their expected outcomes. Production sources and dependency pins are unchanged.

## Remaining in-scope obligations

None for this Paper I formal-contract audit. The expanded 108-record monograph and the explicit classical existence/classification inputs are different scopes. They are not silently marked complete here. The inherited license status is unchanged.

## Series status

Paper I is audited in this sweep. Papers II–XII are not yet audited in this sweep. This ledger does not revoke or replace their historical evidence.

## Failed and interrupted work

E01: online compiler download failed DNS. E02: initial build hit the foreground command timeout. E03: unsupported checker help invocation triggered a broad replay and was memory-killed. E04: an inefficient extra-audit program was deliberately stopped and refactored. E05: the first exact-replay wrapper had an IO type-inference error and was corrected. All are retained in `evidence/RUN_INDEX.json` and the referenced logs. None required changes to a Paper I theorem or definition.

## Exact restart point

Start Paper II. Recover its latest authoritative source package, identify its contract denominator and dependency closure, and apply the same clean compile, complete source-owned axiom audit, explicit type review, serial kernel replay, and rejection-control workflow. Keep Paper I frozen as the source-identical audited baseline.

No audit process remains running. See `PROGRESS_LEDGER.json` for the machine-readable checkpoint and `VERIFICATION.json` for the authoritative result.
''')
report=f'''# Paper I: final Lean audit

**Result: PASS for the complete current 35-row formal contract.**  
**Date:** 10 October 2026  
**Component:** Projector-Resolved Seed Calculus I, formal v1.0.2  
**Source changes:** none

The current Paper I formalization was rebuilt from its actual source rather than accepted on the strength of an old PASS report. All twenty source files compiled into a previously empty local object directory under the pinned compiler and dependency state. The explicit audit, declaration inventory, same-kernel module replay, and negative controls also completed.

## Results

| Check | Actual result |
|---|---:|
| Predecessor manifest entries checked | 837 / 837 |
| Production Lean files rebuilt | 20 / 20 |
| Production source lines | 7,125 |
| Completion-contract rows | 35 / 35 |
| Mapped declaration names resolved | 84 / 84 |
| Mapped theorem declarations | 73 |
| Mapped definitions or equivalences | 11 |
| Inherited namespace gate | 1,126 entries passed |
| Expanded source-owned gate | 1,152 entries passed |
| Compiled modules replayed through the kernel | 20 / 20 |
| Intended rejection controls | 4 / 4 rejected correctly |
| Positive foreign-namespace gate control | Passed |
| Exact boundary-consumer theorems | 4 / 4 |
| Final source and object identity checks | 20 / 20 |
| Successful expected-outcome command checks | {len(checks)} |

Two source files are import-only modules. The 1,152-entry inventory includes definitions, constructors, recursors, and generated proof helpers. It is not a count of 1,152 independent or novel mathematical theorems. Its 720 theorem-kind entries also include generated helpers. The mapped public contract contains 73 theorem declarations and 11 definitions or equivalences.

## What improved in this audit

The existing fail-closed audit filtered names under the `Komorebi` and `KomorebiVerification` namespaces. That correctly inspected 1,126 entries but did not enumerate every declaration owned by the source modules. The new audit uses source-module ownership. It includes **25 private declarations and one generated declaration in another namespace**, bringing the checked inventory to 1,152. Every one passed.

This is an improvement to the axiom inventory, not a claim that 26 missing mathematical proofs were supplied. Their source already compiled. No production definition, statement, proof body, or dependency pin needed alteration.

The only reported transitive axioms were `propext`, `Classical.choice`, and `Quot.sound`. No production declaration depended on `sorryAx` or an additional custom axiom. The production-source policy found no active proof placeholders, unsafe declarations, opaque declarations, or native-decision proof shortcuts among the forbidden patterns. Deliberately invalid fixtures are kept separately under `tests/fixtures` and are not part of that production-source claim.

## What was actually executed

The exact compiler is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency manifest entries were checked against the actual cached Git HEADs. Source files were compiled serially with warnings treated as errors and automatic implicit-variable invention disabled.

The main build also compiled the root aggregator and the standalone audit module. All 84 mapped names were resolved in a separately elaborated file, and their types and axioms were printed. The standalone gate was then executed explicitly. This matters because the root library does not import that audit gate.

A subsequent run replayed the constants of each of the twenty compiled modules using the pinned official `replayFromImports` function. The wrapper selects exactly one module per process, avoiding the command-line checker's prefix-wide parallel behavior. This is a **same-kernel replay**, not an independently implemented external verifier. Upstream cached imports were reused. Mathlib was not freshly rebuilt or fully replayed.

The main successful run took {sum(x['seconds'] for x in main['checks']):.3f} seconds of recorded command time. The ownership and replay run took {sum(x['seconds'] for x in extra['checks']):.3f} seconds. The added guard and boundary controls took {sum(x['seconds'] for x in controls['checks']):.3f} seconds. These totals exclude recovery, inspection, packaging, and failed attempts.

## Controls and mathematical boundaries

The normal strict compiler rejected a false natural-number equality and a placeholder proof. The expanded gate then rejected a deliberately imported custom axiom in a nonproject namespace and an imported placeholder that had been compiled with warnings-as-errors deliberately disabled. A clean theorem in that same nonproject namespace was accepted. This checks that the new gate follows module ownership rather than rejecting names merely for being outside a prefix.

Four additional consumer theorems passed: every entry of the rational matrix `[[1,1],[-1,-1]]` is nonzero, that matrix squares to zero, the zero module has seed rank zero, and the natural two-dimensional full-matrix module has rank one. The first pair illustrates exact cancellation despite dense support. These are audit regressions, not new contract rows.

The type and source review confirms that generation uses actual submodule spans, packet coordinates use actual projector ranges, and transfer blocks are actual composed linear maps. The report retains the distinction between shared and independent actions, algebraic and topological results, and obstruction and sufficiency. See `audit/SEMANTIC_REVIEW.md` and the complete declaration crosswalk.

## Scope that must remain explicit

**The 35-row formal contract is not the expanded monograph's 108-record inventory.** Rows 10, 13, 14, 32, and 35 retain supplied decomposition, extraction, quotient, canonical-form, or spectral certificates as stated in the normative map.

In particular, the cyclic-matrix result takes the minpoly/charpoly bridge as an input and assembles the displayed equivalence. It does not independently construct that bridge for an arbitrary matrix. The split-semisimple result transports a concrete formula through supplied equivalences; it does not construct a Wedderburn decomposition or the nonsplit division-algebra case. The exact graph-rank specification does not provide a verified executable eigensolver.

These are declared scope boundaries, not newly discovered compiler failures. No unresolved proof obligation remains within the audited current contract. No completion claim is made for its excluded extensions, the historical v0.2.0 ancestor tranche, Python implementations, or Papers II–XII in this audit sweep.

## Failures and recovery

Not every attempt succeeded. The direct compiler download failed because the container could not resolve GitHub. The matching offline runtime was recovered from Library and authenticated against its archive hash.

The first foreground build was interrupted by the 180-second container command limit after one module compiled. The accepted build restarted from a separate empty output directory. A diagnostic `leanchecker --help` invocation also failed: that pinned checker has no help flag, so it selected a broad default target, launched concurrent replay, and was killed under the 4 GiB memory ceiling.

Two new audit-instrumentation attempts were not accepted as final runs. The first extra audit was deliberately stopped and refactored to cache module names. The first exact-replay wrapper then failed type inference between BaseIO and IO; adding an explicit IO result type fixed the wrapper. The final ownership audit and all twenty replays were rerun after that correction.

The original logs, source snapshots, and incident records remain in the package. None of these recoveries changed Paper I's mathematical sources. `evidence/RUN_INDEX.json` distinguishes raw interrupted receipts from current run status. No process remains running after this handoff.

## Reproduction and handoff

Run `bash scripts/run_audit.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output` from Linux or WSL with Python 3 available. The output path must not already exist. The matching compiler and dependency cache are external prerequisites, not included in this compact source/evidence ZIP. Do not run `lake update` when reproducing this pinned state.

The three constituent verifiers were actually executed. The composed shell launcher was syntax-checked but was not used to duplicate the entire accepted run. The original mathematical component and its license-status record are preserved without selecting a new publication license.

The package contains all twenty current Lean sources, project configuration and manifest, the normative contract, exact compiler logs and objects, complete source-owned inventory, all mapped declaration locators, semantic notes, controls, failed attempts, hashes, and the progress ledger.

**Next restart: Paper II. Paper I's audited formal component can remain frozen.**
'''
(O/'PAPER_I_FINAL_LEAN_AUDIT.md').write_text(report)
(O/'README.md').write_text('''# Paper I final Lean audit — 10 October 2026

**PASS for the complete current 35-row formal contract.** This is a fresh audit of formal component v1.0.2, not a new mathematical version.

Start with `PAPER_I_FINAL_LEAN_AUDIT.md`, then `VERIFICATION.json`. The source-owned audit covers 1,152 entries and the complete contract maps 84 declarations. All 20 production Lean files remain byte-identical to the authoritative package. All 20 were rebuilt and replayed.

## Contents

`source/main/` contains the complete current formal component and its pinned configuration. `audit/` contains semantic review and the exhaustive declaration crosswalk. `evidence/` contains successful runs, preserved failures, object files, and identity records. `tests/` contains audit programs, mathematical consumers, and deliberately invalid nonproduction fixtures. `scripts/` contains the replay tools. `PROGRESS_LEDGER.md` and `.json` record the next restart.

## Repeat the audit

Linux or WSL, Python 3, and the exact externally provisioned portable kit are required.

```bash
bash scripts/run_audit.sh \
  /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  /absolute/path/to/new-audit-output
```

The new output directory must not already exist. This rebuilds local sources and reuses pinned upstream objects. It does not rebuild Mathlib or use an independently implemented Lean kernel. The wrapper is serial to avoid concurrent memory-heavy Lean processes.

The 35-row contract does not equal the expanded monograph's 108-record inventory. Certificate inputs and noncomputable algorithm boundaries remain explicit. See the semantic review. The inherited license-status file remains unchanged.

The first interrupted build's raw JSON says RUNNING because it was written before interruption. It is not still running. `evidence/RUN_INDEX.json` and the interruption record give its effective status. No work is left running after this handoff.
''')
# Persist the finalizer for provenance; it is a record-specific report generator, not the portable replay entrypoint.
shutil.copy2(Path(__file__),O/'scripts/assemble_recorded_report.py')
# Bind final payload. Exclude only this manifest itself.
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='MANIFEST_SHA256.json':
  assert p.suffix.lower() not in {'.ttf','.otf','.woff','.woff2'},p
  manifest.append({'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)})
write('MANIFEST_SHA256.json',{'schema':'komorebi.audit_bundle.manifest.v1','algorithm':'sha256','excluded':['MANIFEST_SHA256.json'],'count':len(manifest),'files':manifest})
# External readable copies are exact copies of bundled artifacts.
for rel,name in [('PAPER_I_FINAL_LEAN_AUDIT.md','Paper_I_Final_Lean_Audit_Report_2026-10-10.md'),('VERIFICATION.json','Paper_I_Final_Lean_Audit_Verification_2026-10-10.json'),('PROGRESS_LEDGER.md','Komorebi_Core_Papers_Final_Lean_Audit_Progress_v0.1.0.md'),('PROGRESS_LEDGER.json','Komorebi_Core_Papers_Final_Lean_Audit_Progress_v0.1.0.json')]:shutil.copy2(O/rel,Path('/mnt/data')/name)
zip_path=Path('/mnt/data/Komorebi_Paper_I_Final_Lean_Audit_2026-10-10.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,str(Path(O.name)/p.relative_to(O)))
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 for r in manifest:
  b=z.read(O.name+'/'+r['path']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 delivery={'status':'PASS','zip_name':zip_path.name,'zip_bytes':zip_path.stat().st_size,'zip_sha256':sha(zip_path),'zip_members':len(z.namelist()),'manifest_payload_files_verified':len(manifest),'zip_crc':'PASS','member_hash_verification':'PASS','font_files_included':False,'top_level_folder':O.name}
Path('/mnt/data/Paper_I_Final_Lean_Audit_Delivery_Verification_2026-10-10.json').write_text(json.dumps(delivery,indent=2)+'\n')
Path('/mnt/data/Komorebi_Paper_I_Final_Lean_Audit_2026-10-10.sha256').write_text(delivery['zip_sha256']+'  '+zip_path.name+'\n')
print(json.dumps(delivery,indent=2));print('FINAL',verification['status'])

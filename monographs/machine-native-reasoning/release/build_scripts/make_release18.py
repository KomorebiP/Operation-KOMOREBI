from pathlib import Path
import json,hashlib,datetime,argparse,sys,shutil
sys.dont_write_bytecode=True
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--primary',type=Path,required=True);ap.add_argument('--fresh',type=Path,required=True);ap.add_argument('--comparison',type=Path,required=True);a=ap.parse_args()
 f=load(a.primary/'report.json');g=load(a.fresh/'report.json');c=load(a.comparison)
 assert f['status']==g['status']==c['status']=='PASS'
 assert all(s['passed'] and not s['timed_out'] for d in [f,g] for s in d['steps'])
 assert f['source_results_formalized']==26 and f['source_results_not_formalized']==1
 assert f['input_sha256_before']==f['input_sha256_after']==g['input_sha256_before']==g['input_sha256_after']
 assert all(sha(R/p)==h for p,h in f['input_sha256_after'].items())
 modules=load(R/'MODULES.json');new=load(R/'release/NEW_MODULES.json');dev=load(R/'release/DEVELOPMENT_INDEX.json');finite=load(a.primary/'core25_exact.json')
 supers=[]
 for p in [a.primary,a.fresh]:
  sp=p.parent/(p.name+'_supervisor.json');x=load(sp);assert x['status']=='completed' and x['exit_code']==0;supers.append({'path':str(sp.relative_to(R)),'sha256':sha(sp),'receipt':x})
 counts={'selected_source_results':26,'selected_source_total':27,'pending_source_results':1,
 'production_modules_per_gate':len(modules),'kernel_replays_per_gate':sum(s['name'].startswith('kernel_replay_') for s in f['steps']),
 'controls_per_gate':f['negative_controls'],'new_controls':11,'axiom_audited_declarations':f['axiom_audited_declarations'],
 'elaborated_theorem_constants':f['compiled_theorem_constants_including_generated'],'authored_declarations':f['authored_declaration_count'],
 'authored_theorems':f['authored_theorem_count'],'new_authored_declarations':sum(x['authored_declarations'] for x in new),'new_supporting_theorems':sum(x['supporting_theorems'] for x in new),
 'unchanged_source_inputs_per_gate':len(f['input_sha256_before']),'matched_upstream_artifacts_per_gate':f['matched_upstream_artifacts'],
 'preserved_predecessor_files':f['preserved_predecessor_files'],'commands_per_gate':len(f['steps']),
 'production_objects_identical':c['production_object_count'],'comparison_checks':len(c['comparisons'])}
 differences=[n for n,v in c['nonproduction_objects'].items() if not v['identical']]
 record={'schema':'komorebi.machine_reasoning.core25.admission.v1','status':'PASS','version':'0.18.0','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'counts':counts,'new_modules':new,'actual_axiom_union':f['actual_axiom_union'],
 'primary':{'path':str(a.primary.relative_to(R)),'report_sha256':sha(a.primary/'report.json'),'seconds':f['total_seconds']},
 'fresh':{'path':str(a.fresh.relative_to(R)),'report_sha256':sha(a.fresh/'report.json'),'seconds':g['total_seconds']},
 'supervisors':supers,'comparison':{'path':str(a.comparison.relative_to(R)),'sha256':sha(a.comparison)},
 'source_snapshot_sha256':c['source_snapshot_sha256'],'nonproduction_helper_differences':differences,'development':{'invocations':dev['invocations'],'passed':dev['passed'],'failed':dev['failed']},
 'exact_finite_regression':finite,'remaining_source_result':'3.2 / r:occupancy',
 'boundary':['Original source unchanged','No whole-book formalization','No new learned model or runtime soundness claim','Pinned upstream cache reused and hashed, not rebuilt','Same Lean kernel, not a second independent implementation','No native Windows execution','Monograph PDF not rebuilt']}
 out=R/'release';(out/'ADMISSION_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
 table='\n'.join(f'| {k} | {v:,} |' for k,v in [
 ('Production modules in each cold build',counts['production_modules_per_gate']),('Substantive same-kernel replays in each run',counts['kernel_replays_per_gate']),('Declarations in each transitive axiom audit',counts['axiom_audited_declarations']),('Elaborated theorem constants, including generated auxiliaries',counts['elaborated_theorem_constants']),('Expected control outcomes per run',counts['controls_per_gate']),('Unchanged proof-gate inputs per run',counts['unchanged_source_inputs_per_gate']),('Matched upstream artifacts per run',counts['matched_upstream_artifacts_per_gate']),('Preserved inherited substantive/source-book files',counts['preserved_predecessor_files']),('Production objects identical across the builds',counts['production_objects_identical']),('Rebuild comparisons passed',counts['comparison_checks'])])
 report=f'''# Machine-Native Reasoning — Core 2.5 Lean verification

**PASS · Selected-core correspondence 26/27 · Formal companion 0.18.0**

Author: Komorebi P. Date: 23 October 2026.

## Mathematical outcome

Core 2.5, *When complete packets are genuine probability components*, is now
formally mapped in both of its sectors. The original reviewed statement, setup,
proof and all five source-book files are unchanged.

For any real vector space, actual convex cone, strictly positive linear mass and
finite complete cone-preserving family, Lean proves nonnegative packet weights,
total weight one for a normalized input, zero weight exactly for zero packets,
unit-mass cone membership of every normalized positive packet, and exact mixture
reconstruction. Normalization takes a positive-index argument; a zero-mass packet
is not silently assigned an arbitrary normalized state. Idempotence and finite
dimension are not assumptions of this general mixture theorem.

For actual linear maps on the finite nonnegative coordinate cone, the new
classification derives diagonal form from positivity and completeness. Idempotence
then forces zero-or-one diagonal entries and exactly one owner per coordinate.
The original maps are represented by the constructed coordinate selectors.
Pairwise zero compositions are derived. The converse proves that selector families
satisfy all these input conditions. Zero coordinate dimension, empty indices and
zero operators are handled without accidental nonemptiness assumptions.

The supporting transport development pushes the cone forward, pulls the mass back
and conjugates the operators through a linear equivalence. It preserves weights
and normalized components. A real shear gives valid signed coordinates in the
transported cone. That example is distinguished from an ordinary Haar detail,
which has zero sum but is nonzero and lies outside the original positive cone.

Principal source-facing declarations:

```lean
Komorebi.MachineTheory.PositivePackets.source_core25
Komorebi.MachineTheory.PositivePackets.Coordinate.source_core25_coordinate
```

The separate `sum_positive_weights_one`, `classification_iff` and
`Transport.source_coordinate_change` endpoints record the active-weight identity,
classification converse and coordinate-covariance result. A direct raw-hypothesis
API checks both manuscript sectors, rather than assuming a mixture certificate or
diagonal representation as input.

## Complete current-source verification

Both complete gates terminated successfully, with successful supervisors. Each
started with an empty local proof-object directory. The second source tree was
separately extracted from the authenticated frozen source ZIP without project
objects. The runs were sequential and shared only the pinned external dependency
cache. Every required command passed and no command timed out.

| Check | Actual result |
|---|---:|
{table}

The actual transitive axiom union is `Classical.choice`, `Quot.sound`, `propext`.
Production code contains no proof placeholder, added trusted axiom, native-decision
shortcut, or unsafe/external implementation hook. The audit covers all authored
declarations and all theorem constants in the actual compiled project namespace,
including generated auxiliaries.

The four new modules contain **{counts['new_authored_declarations']} authored
declarations**, including **{counts['new_supporting_theorems']} supporting theorem
declarations**. Cumulative authored counts are {counts['authored_declarations']}
declarations and {counts['authored_theorems']} theorems. These are proof-code
inventories, not counts of independent discoveries or manuscript statements.

All 71 inherited substantive modules and five original source-book files retain
their exact bytes. All 170 inherited control contracts and fixture files are also
unchanged. Eleven new controls test the missing hypotheses and edge conditions.
The full suite has 180 invalid or unfinished fixtures rejected for their specified
proof diagnostics and one explicit added-axiom fixture rejected by the separate
axiom policy after compilation. Missing imports, unknown identifiers, parse errors
and timeouts never count as mathematical rejection evidence.

Nonproduction helper differences: **{', '.join(differences) if differences else 'none'}**.
Every production object matches byte for byte. Complete axiom records and generated
audit source match. A helper binary difference is not a production-identity success
and its cause is not inferred.

## Exact rational regression

The separate standard-library checker exhausts **{finite['counts']['families']:,}**
complete matrix families in declared rational grids. It identifies
**{finite['counts']['positive_complete']}** positive families and
**{finite['counts']['selector_families']}** selector families, checking actual matrix
idempotence, diagonal action, unique ownership and pairwise composition.

It checks **{finite['counts']['coordinate_mixture_inputs']:,}** normalized input/mass
contracts and observes **{finite['counts']['zero_weight_packets']:,}** zero packet
weights. It additionally checks **{finite['counts']['transported_mixture_inputs']:,}**
exact shear-transported mixture contracts, including
**{finite['counts']['signed_valid_transported_states']:,}** normalized component
occurrences with negative coordinates but valid transported-cone membership.
Eight further exact boundary checks distinguish the failed hypotheses.

Arithmetic uses integers and `Fraction` only, with no random sampling, tolerance,
training or empirical timing claim. These domains overlap and are not summed as
independent results. Both complete gates reproduce the same finite record. This is
a same-project reference checker, not a universal proof of Python correctness or
an independent external implementation. The arbitrary-real-space Lean result is
separate from these finite regression checks.

## Recovery and reproducibility

The intact predecessor archive has 62,071,022 bytes and SHA-256
`406c4b0f63e129025abb313f437c96ce25295add96afec31c58fae3832d804d3`.
All 2,176 manifest-covered files passed exact-set, byte-length and hash checks.
No new archive-recovery gap occurred. The earlier missing Core 8.3 historical
payload remains documented in predecessor history and is not relabeled recovered.

The exact offline runtime was reconstructed from the five saved Library parts.
The combined 2,220,147,424-byte archive matches SHA-256
`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`,
and extraction completed for 166,035 members. The compiler is Lean 4.34.0-rc2,
commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine repositories and actually
imported cache artifacts are checked. Cache hashes are not independent origin
attestation and the upstream sources were not rebuilt.

Compiler invocations use one worker, a 4,096 MiB internal limit and warnings as
errors. Every gate subprocess has the unchanged 45-second wall allowance. Each
supervisor allows 1,800 seconds. The host has a shared 4 GiB cgroup ceiling, not an
additional separately imposed per-command OS cap. Replays use Lean's own kernel,
not a second independent implementation. Native Windows execution is not claimed.
Actual gate durations in the receipts are execution records, not benchmarks.

## Failed attempts and corrections

There were **{dev['invocations']}** recorded development Lean invocations:
**{dev['passed']} succeeded and {dev['failed']} failed** before the accepted gates.
Their exact attempted source snapshots and diagnostics are retained. Corrections
addressed a deprecated real import and tactic names, strict linter diagnostics,
function extensionality on linear maps, placement of scoped `omit` declarations,
and explicit arithmetic for the real shear. The first raw API check also exposed
a finite-subtype instance mismatch. Using the same canonical subtype enumeration
made the external source statement and the general endpoint agree without changing
any mathematical premise or conclusion. No production proof was weakened.

Runtime title search initially returned no result and a named Library-path probe
failed. Size-based listing located all five parts. Container streaming launch was
unavailable before execution, and its uncreated directory caused an initial direct
launch failure. The directory was created explicitly and tracked restoration then
passed. These are tool/recovery failures, not mathematical evidence.

An administrative history-copy command initially expected a predecessor Markdown
map that was not shipped. The copy was restricted to actually present historical
files. A later metadata recheck correctly rejected a Python bytecode cache created
by importing the verifier. Only that newly generated cache was removed, bytecode
creation was disabled, and the full exact-set recheck passed. The archive and its
scientific payload were unchanged. The retained delivery tools passed all 28 small
fixtures in a fresh run. Those tests concern delivery mechanics, not proof truth.

## Remaining task and delivery boundary

The only remaining selected-core result is **Core 3.2**, the partition occupancy
classification, exact 2^r signature count and fixed-binary r-bit lower/upper bound.
`release/NEXT_CORE32_SPEC.md` gives the precise source anchor and restart contract.
Neither the theorem count nor the book's scope should be enlarged by merely
configuring an endpoint before its acceptance runs.

The monograph PDF is unchanged. A formal-status insertion is supplied for its next
build. The Large Signal Model's separate 39/87 inventory is unchanged. No learned
encoder, physical sensor semantics, deployed decision system, computational
complexity guarantee, hosted publication, independent review or full-book
formalization is established by this result.

The delivery manifest and external verification receipt separately authenticate
the supplied ZIPs, exact file sets and source inputs. No runtime or standalone font
binaries are distributed. See the archive-layout record for full versus compact
contents and the distinction between current and historical execution evidence.
'''
 (out/'REPORT.md').write_text(report,encoding='utf-8')
 ledger=f'''# Accepted formalization ledger — 0.18.0

Date: 23 October 2026. Status: **PASS**. Selected source correspondence: **26/27**.

Core 2.5 is newly mapped in four modules with {counts['new_supporting_theorems']}
supporting theorems. Both the general cone-mixture result and the coordinate
positive-idempotent classification are covered. All 71 inherited substantive
modules and five source-book files are unchanged.

Both complete current-source gates passed, sequentially. Each compiled
{counts['production_modules_per_gate']} production modules, replayed
{counts['kernel_replays_per_gate']} substantive modules, audited
{counts['axiom_audited_declarations']} declarations and passed
{counts['controls_per_gate']} expected controls. All
{counts['unchanged_source_inputs_per_gate']} proof-gate inputs remained unchanged.
Every production proof object matches across the two builds. Actual receipts and
`release/ADMISSION_RECORD.json` are the acceptance evidence, not this ledger alone.

## Failures retained

{dev['failed']} of {dev['invocations']} development Lean invocations failed before
acceptance and are preserved with source snapshots. Runtime-retrieval and launch
issues, a missing optional historical Markdown file, and a strict metadata recheck
rejecting an accidentally generated bytecode cache are recorded with corrections.
No required command failed or timed out in either accepted cumulative gate.
The current predecessor was intact; historical Core 8.3 missing files remain
historical and are not silently reconstructed.

## Exact next restart

Core 3.2 (`r:occupancy`) is the only unformalized selected result. Prove the exact
signature/occupancy equivalence, construct every attainable occupancy, establish
the powerset bijection and 2^r count, and prove the fixed-width r-bit necessity and
sufficiency using the actual partition event language. Keep all candidate subsets,
including empty, and do not require every value of the target codomain to occur.
See `NEXT_CORE32_SPEC.md`. Admission to 27/27 requires its own successful gates.

## Status layers

The root README, theorem map and preparation ledger are frozen proof-gate inputs.
Their prospective wording is preserved rather than changed after the runs. This
accepted ledger and `ADMISSION_RECORD.json` record the final current-source verdict.
The original book is unchanged; its next build can use `BOOK_FORMAL_STATUS_INSERT.tex`.
The separate Large Signal Model 39/87 contract remains outside this 27-result map.
'''
 (out/'ACCEPTED_PROGRESS_LEDGER.md').write_text(ledger)
 (out/'PROOF_GUIDE.md').write_text('# Accepted Core 2.5 formal companion\n\nThe cumulative verification passed at 26/27 selected source results. See `REPORT.md` for actual counts and boundaries.\n\n'+(R/'docs/CORE25_PROOF_GUIDE.md').read_text())
 (out/'BOOK_FORMAL_STATUS_INSERT.tex').write_text(r'''\paragraph{Formal correspondence.}
The selected finite reasoning core has formal counterparts for twenty-six of its
twenty-seven source results. The positive-packet theorem is covered both for a
general real cone with strictly positive mass and for complete positive
idempotents on the finite coordinate cone. Source-facing checks retain the
zero-weight and normalization conditions. The cumulative verification includes
cold builds, transitive axiom checks, same-kernel replay, rejection controls and a
separately extracted-source rebuild. The remaining selected result is the exact
partition correction-memory count. This correspondence does not certify every
specialist chapter or a learned or deployed reasoning system.
''')
 for src,dst in [('REPORT.md','Machine_Native_Reasoning_Lean_Core25_Report.md'),('PROOF_GUIDE.md','Machine_Native_Reasoning_Lean_Core25_Proof_Guide.md'),('ACCEPTED_PROGRESS_LEDGER.md','Machine_Native_Reasoning_Lean_Core25_Progress_Ledger.md')]:
  shutil.copy2(out/src,Path('/mnt/data')/dst)
 print(json.dumps(counts,indent=2))
if __name__=='__main__': main()

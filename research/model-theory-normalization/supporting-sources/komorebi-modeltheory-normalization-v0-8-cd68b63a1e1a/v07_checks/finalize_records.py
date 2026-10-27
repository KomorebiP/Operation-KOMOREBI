#!/usr/bin/env python3
"""Write public status only after all recorded verification tasks pass."""
from pathlib import Path
from datetime import datetime
from collections import Counter
import json,hashlib,platform,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 L=json.loads((ROOT/'results_v07/LEAN_AUDIT.json').read_text());P=json.loads((ROOT/'results_v07/PYTHON_AUDIT.json').read_text());S=json.loads((ROOT/'v07_evidence/COLD_STATE.json').read_text());E=S['environment'];parent=json.loads((ROOT/'v07_evidence/PARENT_PRESERVATION.json').read_text())
 assert L['status']==P['status']==S['status']=='PASS'
 for x in S['inputs']:assert sha(ROOT/x['path'])==x['sha256']
 for x in P['inputs']:assert sha(ROOT/x['path'])==x['sha256']
 for x in parent['files']:assert sha(ROOT/x['path'])==x['sha256']
 assert sha(ROOT/'history/Komorebi_ModelTheory_Normalization_v0.6.zip')==parent['parent_sha256']
 def manifest(cid,inputs,outputs,first,last,seconds,statement,bounds,command,seed=None):
  return {'schema_version':2,'claim_id':cid,'repository':{'commit':'Standalone v0.7; frozen v0.6 '+parent['parent_sha256'],'dirty':True},'command':command,'environment':{'software':[{'name':'Python','version':sys.version},{'name':'Lean','version':E['lean_version']},{'name':'Mathlib','version':E['mathlib_commit']}],'hardware':{'platform':platform.platform(),'cpu_cgroup':E['cpu_cgroup'],'memory_cgroup':E['memory_cgroup']}},'mathematics':{'assertion_tested':statement,'coefficient_domain':'Positive-pivot integer lattices; ZMod(m) for positive m; discovery enough-fuel endpoint ZMod(p^r) with p prime','conventions':'Fixed ambient columns; row-Hermite convention uses the pivot belonging to each column. Full modular preimage includes m Z^d. All initial source states; FIFO row extension prepends a word.','inputs':[x['path'] for x in inputs],'bounds':bounds,'non_claims':['No bound on all temporary arithmetic operands or total bit complexity','No verified Python extraction, parser, or exporter','No minimum modular generator/test count or formula-size theorem','Not a complete rebuild of all historical instances or upstream Mathlib','No held-out discovery, speedup benchmark, or historical-novelty claim']},'randomness':{'used':seed is not None,'generator':'Python random.Random' if seed is not None else 'none','seed':seed},'run':{'started_at':first,'finished_at':last,'runtime_seconds':seconds,'exit_status':0,'status':'completed','resource_limits':{'memory_bytes':int(E['memory_cgroup']),'cpu_seconds':None,'max_cores':None,'max_threads':1},'missing_results':[],'invalid_results':[]},'input_artifacts':[x|{'sha256_after':sha(ROOT/x['path'])} for x in inputs],'execution_artifacts':[x['path'] for x in inputs],'declared_results':[x['path'] for x in outputs if x['kind']=='result'],'outputs':outputs,'checks':[{'name':'all expected outcomes complete','status':'PASS'},{'name':'input hashes preserved','status':'PASS'}],'result':'PASS','residual_risks':['Mathematical interpretation is self-review, not external refereeing','The proof checks formal inputs, not an informal problem-to-matrix translation','Pinned upstream compiled Mathlib is reused']}
 outs=[{'path':'results_v07/LEAN_AUDIT.json','sha256':sha(ROOT/'results_v07/LEAN_AUDIT.json'),'kind':'result'}]+[{'path':x['log'],'sha256':x['sha256'],'kind':'log'} for x in L['tasks']]
 elapsed=(datetime.fromisoformat(L['finished_at'])-datetime.fromisoformat(L['started_at'])).total_seconds()
 lm=manifest('KMT-M7-CANONICAL-BOUNDED-DISCOVERY',S['inputs'],outs,L['started_at'],L['finished_at'],elapsed,'Exact executable normalizer; lattice preservation, uniqueness, residue-module canonical key, stored entry bound, normalized discovery/reference equality and logical correctness; direct kernel computations on 203 inherited profiles.',{'local_modules':L['modules'],'generated_cases':203,'audit_tasks':L['task_count'],'new_generic_theorems':L['new_generic_counts']['theorem']},'python v07_checks/audit_lean.py --runtime RUNTIME --init; --all (or repeated --batch calls and --finish)')
 lm['run']['completed_lean_commands']=[x['argv'] for x in L['tasks']];lm['run']['task_runtime_sum']=L['task_runtime_sum'];lm['run']['per_command_wall_cap_seconds']=90
 lm['run']['protocol_revisions']=['v07_evidence/protocol_revision/REVISION.json','v07_evidence/protocol_revision/REVISION2.json']
 lm['run']['failed_attempts_retained']=['v07_evidence/protocol_revision/COLD_STATE_attempt1.json','v07_evidence/protocol_revision/COLD_STATE_attempt2.json']
 lm['run']['resume_commands']=[[sys.executable,'v07_checks/resume_axiom_audit.py'],[sys.executable,'v07_checks/resume_module_audit.py']]
 dump(ROOT/'LEAN_MANIFEST_v07.json',lm);dump(ROOT/'LEAN_MANIFEST.json',lm)
 po=[{'path':'results_v07/PYTHON_AUDIT.json','sha256':sha(ROOT/'results_v07/PYTHON_AUDIT.json'),'kind':'result'}]
 pm=manifest('KMT-M7-NORMALIZED-PORT-AUDIT',P['inputs'],po,P['started_at'],P['finished_at'],P['runtime_seconds'],'Finite exact checks of normalized modular spans, reconstruction, canonical representative/order invariance, source transcription and persistent basis-entry measurements.',{'profiles':203,'exhaustive_configs':P['exhaustive_configs'],'maximum_generators':2,'general_integer_bases':150,'random_smith_cases':90,'random_queries_each':12},[sys.executable,'v07_checks/audit_normalized.py'],P['seed'])
 dump(ROOT/'COMPUTATION_MANIFEST_v07.json',pm);dump(ROOT/'COMPUTATION_MANIFEST.json',pm)
 (ROOT/'FORMALIZATION_COVERAGE.md').write_text(f'''# Formalization coverage — Model-Theory Normalization v0.7

PASS: {L['modules']} cold-built local modules, {L['task_count']} expected-outcome tasks,
{L['named_declarations']} explicit named declarations, all axiom-audited.
Counts: {L['counts']}.
Five new generic modules add {L['new_generic_counts']['theorem']} theorem declarations
and {L['new_generic_counts']['def']} definitions. NormalizedExamples adds 12 concrete
theorems. Seventeen generated batches directly execute all 203 inherited profiles
through normalizedPrimeDiscover and derive all-word code certificates. Generated
facts are not independent research discoveries.

The only recorded axioms are {', '.join(L['axioms'])}. No custom project axioms,
sorryAx or Lean.ofReduceBool. Every accepted source hash is unchanged. Warnings
are treated as errors. All seven false/placeholder/corrupted-claim controls reject,
and the positive control accepts. Rejections are not missing-module or resource failures.

| Module | Exact checked scope |
|---|---|
| EchelonNormalize | Euclidean residue; unique representative in the pivot box; exact lattice preservation; reducedness; idempotence |
| EchelonBounds | Every pivot divides m; persistent normalized entries lie in [0,m]; insertion preserves kernel and bound |
| EchelonCanonical | Reduced basis unique for its integer lattice; normalization equality iff lattice equality |
| EchelonModularNormal | Canonical normal form equality iff equality of actual residue row submodules; storage bound |
| NormalizedDiscovery | Actual cached normalized run; exact reference and v0.6 output; returned-cache invariant; total prime-power success and original-language logical definition |
| NormalizedExamples | Negative tails, coupling, insertion-order equivalence, composite and trivial moduli, zero dimension/precision and exhausted fuel |
| NormalizedComputed00–16 | 203 direct kernel computations plus logical code consequences |

## Boundaries

The normal form is relative to fixed ambient column coordinates and a fixed modulus
for residue comparisons. It is not canonical Smith extraction or a minimal modular
generating set. The stored bound does not bound every temporary extended-gcd,
insertion, or reduction operand, nor prove total bit complexity. The numerical fuel
bound remains prime-power-specific. The Python port/parser is not verified extraction.
No minimum formula/test theorem, learned policy, or held-out performance claim.

All {parent['count']} parent Lean files remain unchanged. The current cold build
rebuilds 21 inherited dependencies and 23 new modules; it is not a fresh replay of
all historical generated suites. Upstream Mathlib is reused. Standalone Case201/202
are duplicate convenience instances and are not counted as additional discoveries.

Lean: {E['lean_version']}
Mathlib pin: {E['mathlib_commit']}
Review is self-review, not independent refereeing or a historical-priority verdict.
''')
 (ROOT/'RESULTS.md').write_text(f'''# Retained results — Model-Theory Normalization v0.7

## Lean

PASS: {L['modules']} local modules, {L['task_count']} expected-outcome tasks,
{L['named_declarations']} named declarations. All 203 inherited profiles execute
the normalized algorithm by kernel reduction. All source hashes are unchanged.
Seven rejection controls and one positive control pass their required outcomes.
Only {', '.join(L['axioms'])} occur in the axiom audit.
Completed task runtime sum: {L['task_runtime_sum']:.6f} seconds. This is not a
comparative performance measurement. One 160-name axiom batch timed out at 90 seconds.
Its failed state and diagnostics are retained. The uncompleted axiom batches were
split to at most 80 names, with no changes to mathematical sources or completed
builds. The completed-task sum excludes that failed attempt, while elapsed protocol
time includes interruption and recovery. One split 80-name group also reached
its cap. Remaining drivers then used module-mode imports and completed with the
same declaration inventory and proof hashes. Both failed states are retained.
See v07_evidence/protocol_revision/.

## Exact Python port audit

PASS. Seed {P['seed']}; one recorded runtime {P['runtime_seconds']:.6f} seconds.
The baseline and new discovery use the same sources and queue policy.

| Check | Count |
|---|---:|
'''+''.join(f'| {k} | {v:,} |\n' for k,v in P['counts'].items())+f'''
All generating lists of length zero, one and two are exhausted for
{P['exhaustive_configs']}, with every candidate vector. General integer-basis
checks cover 150 additional triangular inputs, and 90 random prime-power cases
are compared with the inherited independent Smith solver (12 queries each).
There are no floating-point load-bearing computations.

## Basis-entry measurements, not total memory or runtime

| Measurement across the same 203 sources | Bits |
|---|---:|
| Old basis, between complete insertions | {P['peaks']['old_checkpoint_bits']} |
| Old basis, including partial updates | {P['peaks']['old_partial_basis_bits']} |
| New persistent normalized basis | {P['peaks']['new_checkpoint_bits']} |
| New partial pre-normalization basis | {P['peaks']['new_pre_normalization_basis_bits']} |

The particular source reaching 730 previously now has maximum persistent entry
length 12. The large 2^128-state source changes from 69 to 17, and the 2^24
one-dimensional stress case remains 25. These maxima are finite implementation
observations. The universal numeric range [0,m] is separately Lean-proved.
The pre-normalization counter is NOT a bound on every temporary arithmetic operand.

## Provenance and trust

The immediate parent v0.6 Python audit reran successfully in an isolated extracted
copy. Current local dependencies are rebuilt; no full historical Lean replay is
claimed. All predecessor source bytes remain in the immutable parent ZIP.
Fresh-extraction scope is recorded separately in the external replay JSON.
The Python code and transcription are tested, not formally verified extraction.
The mathematical interpretation audit is self-review.
''')
 failures=[]
 for p in sorted((ROOT/'v07_evidence').glob('dev_*.json')):
  rec=json.loads(p.read_text())
  if rec['exit_code']!=0:failures.append(rec)
 dump(ROOT/'v07_evidence/DEVELOPMENT_ATTEMPTS.json',{'failed_or_timed_out':failures,'count':len(failures),'note':'API probe failures are discovery diagnostics, not rejected mathematical claims. A first enclosing warmup command timed out before producing a per-command record; the complete repeat is separately retained.'})
 (ROOT/'DEVELOPMENT_FAILURES.md').write_text('''# Development failures — v0.7

1. The first enclosing warmup command hit its 20-second tool limit. No complete
command receipt was retained for that invocation. No process remained running.
The dependency was rerun separately and completed; it was also rebuilt in the final
cold audit. An unrecorded or partial invocation is not counted as successful evidence.

2. Five draft checks failed before correction: two EchelonNormalize checks
(elaboration/definitional rewriting and an unused simp argument under warnings as
errors), one EchelonCanonical check (simplification changed a membership goal),
one EchelonModularNormal check (an unnecessary namespace open), and one
NormalizedExamples check (a missing closing bracket). The final accepted sources
correct these issues without adding assumptions or weakening mathematical scope.
An API probe also tested names that were absent; its output is retained separately.

3. The retained cold audit and exact Python audit are the evidence of completion.
No field-rank approximation, modular nonunit division, or false membership flag
was used to repair these development failures. The negative controls are intentional
invalid claims and not solver counterexamples.

4. Runtime restoration completed with exit zero. Optional static/native artifacts
were excluded while required Lean/Mathlib execution artifacts were restored.
The compiler hash, reported version, Mathlib metadata pin, and selected exact source
hashes were checked. This is reuse of the pinned compiled cache, not a Mathlib rebuild.

5. After all 44 cold proof builds and five axiom groups passed, axiom group 05
reached its 90-second wall cap. The complete failed state and original driver log
are retained in v07_evidence/protocol_revision/. The uncompleted axiom groups were
split from at most 160 names to at most 80 names. All mathematical source, prior
artifact and completed-log hashes were verified unchanged before resuming. The
failed check is not counted among successful tasks. The revised plan still covers
every declaration and all negative controls.

6. The 80-name group 06_split1 also hit the same cap. A module-mode import probe
passed, and all unfinished audit/control drivers were changed to module-mode
imports while keeping the same standard #print axioms calls and declaration
inventory. No mathematical source or completed build changed. The second failed
state and full revised plan are preserved. The final records count only completed
expected outcomes, not either timed-out attempt.

Any later packaging or extraction failure must be appended with its actual outcome.
''')
 print('Final records written',L['modules'],L['named_declarations'],P['peaks'])
if __name__=='__main__':main()

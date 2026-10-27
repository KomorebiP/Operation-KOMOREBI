#!/usr/bin/env python3
"""Publish records only after successful frozen-source audits."""
from pathlib import Path
from datetime import datetime
import hashlib,json,platform,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 L=json.loads((ROOT/'results_v08/LEAN_AUDIT.json').read_text());P=json.loads((ROOT/'results_v08/PYTHON_AUDIT.json').read_text());S=json.loads((ROOT/'v08_evidence/COLD_STATE.json').read_text());E=S['environment'];parent=json.loads((ROOT/'v08_evidence/PARENT_PRESERVATION.json').read_text())
 assert L['status']==P['status']==S['status']=='PASS'
 for group in [S['inputs'],P['inputs'],parent['source_files']]:
  for x in group:assert sha(ROOT/x['path'])==x['sha256'],x
 assert sha(ROOT/parent['parent_zip'])==parent['parent_sha256']
 def manifest(cid,inputs,outputs,first,last,seconds,statement,bounds,command,seed=None):
  return {'schema_version':2,'claim_id':cid,'repository':{'commit':'Standalone v0.8; frozen v0.7 '+parent['parent_sha256'],'dirty':True},'command':command,
  'environment':{'software':[{'name':'Python','version':sys.version},{'name':'Lean','version':E['lean_version']},{'name':'Mathlib','version':E['mathlib_commit']}],'hardware':{'platform':platform.platform(),'cpu_cgroup':E['cpu_cgroup'],'memory_cgroup':E['memory_cgroup']}},
  'mathematics':{'assertion_tested':statement,'coefficient_domain':'Positive-pivot integer lattices containing m Z^d; discovery ZMod(p^r); exact signed integer arithmetic',
   'conventions':'Column-pivot reduced upper triangular bases; all source states; observation row right multiplication prepends a digit; peak of the explicit coefficient-arithmetic trace, excluding primitive implementation internals.',
   'inputs':[x['path'] for x in inputs],'bounds':bounds,'non_claims':['No formal costed big-integer runtime or proof-checker complexity theorem','No verified Python/parser/extraction','No historical novelty, speedup benchmark or held-out discovery','No full historical Lean/Mathlib replay','Not a minimal test-list or formula-size theorem']},
  'randomness':{'used':seed is not None,'generator':'Python random.Random' if seed is not None else 'none','seed':seed},
  'run':{'started_at':first,'finished_at':last,'runtime_seconds':seconds,'exit_status':0,'status':'completed','resource_limits':{'memory_bytes':int(E['memory_cgroup']),'cpu_seconds':None,'max_cores':None,'max_threads':1},'missing_results':[],'invalid_results':[]},
  'input_artifacts':[x|{'sha256_after':sha(ROOT/x['path'])} for x in inputs],'execution_artifacts':[x['path'] for x in inputs],
  'declared_results':[x['path'] for x in outputs if x['kind']=='result'],'outputs':outputs,
  'checks':[{'name':'all declared outcomes completed','status':'PASS'},{'name':'accepted input hashes preserved','status':'PASS'}],
  'result':'PASS','residual_risks':['Proof interpretation is self-review','Compiled upstream cache reused with pinned compiler/source','Finite tests do not prove universal software correctness','Cost model excludes the implementation of primitive big-integer arithmetic']}
 outs=[{'path':'results_v08/LEAN_AUDIT.json','sha256':sha(ROOT/'results_v08/LEAN_AUDIT.json'),'kind':'result'}]+[{'path':t['log'],'sha256':t['sha256'],'kind':'log'} for t in S['tasks']]
 lm=manifest('KMT-M8-TEMPORARY-COEFFICIENT-BOUNDS',S['inputs'],outs,S['started_at'],S['finished_at'],(datetime.fromisoformat(S['finished_at'])-datetime.fromisoformat(S['started_at'])).total_seconds(),
 'Exact bounded Bezout update; identical canonical insertion; explicit temporary arithmetic peaks through normalized discovery; power-of-two size bound; Euclidean recursion count; 203 direct kernel computations.',
 {'modules':L['modules'],'tasks':L['task_count'],'kernel_cases':203,'new_generic_theorems':37,'universal_cap':'m*(2*m*(m+1))^d','operand_exponent':'b+(2*b+2)*d for m<=2^b'},
 'python v08_checks/audit_lean.py --runtime RUNTIME --init; python v08_checks/audit_lean.py --run')
 lm['run']['completed_lean_commands']=[t['argv'] for t in S['tasks']];lm['run']['task_runtime_sum']=L['runtime_sum_seconds'];lm['run']['per_command_wall_cap_seconds']=100
 dump(ROOT/'LEAN_MANIFEST_v08.json',lm);dump(ROOT/'LEAN_MANIFEST.json',lm)
 pm=manifest('KMT-M8-BOUNDED-PORT-AUDIT',P['inputs'],[{'path':'results_v08/PYTHON_AUDIT.json','sha256':sha(ROOT/'results_v08/PYTHON_AUDIT.json'),'kind':'result'}],P['started_at'],P['finished_at'],P['runtime_seconds'],
 'Independent exact finite checks of Bezout outputs and trace bounds, signed/general inputs, modular spans, canonical basis equality, source transcription, all inherited discovery outputs and operation-count formulas.',
 {'source_cases':203,'exhaustive_configs':P['exhaustive_configs'],'maximum_generators':2,'bezout_q':P['bezout_q'],'bezout_a':P['bezout_a'],'signed_fibonacci_pairs':320,'random_smith_cases':90},[sys.executable,'v08_checks/audit_python.py'],P['seed'])
 dump(ROOT/'COMPUTATION_MANIFEST_v08.json',pm);dump(ROOT/'COMPUTATION_MANIFEST.json',pm)
 failures=[]
 for f in sorted((ROOT/'v08_evidence/development').glob('*.json')):
  rec=json.loads(f.read_text())
  if rec.get('exit_code',0)!=0:failures.append({'record':str(f.relative_to(ROOT)),**rec})
 dump(ROOT/'v08_evidence/DEVELOPMENT_ATTEMPTS.json',{'failed_draft_checks':failures,'count':len(failures),'interpretation':'Draft/API checks, not failed universal mathematical counterexamples. Only the final frozen-source cold run supports verification.'})
 (ROOT/'FORMALIZATION_COVERAGE.md').write_text(f'''# Formalization coverage — Model-Theory Normalization v0.8

PASS: {L['modules']} cold-built modules, {L['task_count']} completed expected-outcome tasks.
25 inherited dependencies and 24 new modules (six generic, one example, seventeen
computed batches). All {L['named_declarations']} explicit named declarations are
axiom-audited: {L['counts']}. Six new generic modules contain
{L['new_generic_counts']['theorem']} theorems and {L['new_generic_counts']['def']} definitions.
The 203 actual kernel computations are regressions, not 203 new discoveries.

Only {', '.join(L['axioms'])} occur. No additional project axiom,
sorryAx or Lean.ofReduceBool occurs. All source/input hashes stayed unchanged.
Warnings are errors. One positive and six deliberately false/placeholder controls
have their expected outcomes. All controls reject for proof reasons, not missing
imports, timeouts or memory exhaustion. Upstream Mathlib was reused, not rebuilt.

| Module | Exact new scope |
|---|---|
| BoundedBezout | Executable Euclidean coefficients, signed correctness, coefficient bounds, explicit high-level Euclidean arithmetic peak |
| EuclidCost | Recursion counter for the same Euclidean descent; second input <2^b implies at most 2b nonterminal calls |
| BoundedInsertion | Determinant-one integer insertion, exact span, equality to the inherited canonical normalized result |
| EchelonPeakCore | Explicit residue arithmetic trace and its bound; modular normalized caches meet the bounded-input hypotheses |
| EchelonTemporaryBounds | Raw insertion trace, normalization trace, universal update bound m[2m(m+1)]^d |
| BoundedDiscovery | Identical ordered discovery, total exact semantics, standard defining formula, complete worklist trace bound and power-of-two operand budget |
| BoundedArithmeticExamples | Actual negative Bezout, recursion, coupling, temporary>modulus and zero-dimensional calculations |
| BoundedComputed00–16 | 203 direct solver evaluations by ordinary kernel reduction and inherited all-word code consequences |

## Boundaries

The formal endpoint bounds the explicit high-level coefficient-arithmetic trace.
It does not bound every CPU temporary inside integer primitives, total allocation,
proof terms, kernel checking, source-row transcription or all queue metadata.
The residue trace conservatively covers the membership subtractions; an additional
compiler-level operation-trace refinement theorem is not supplied.

COST_MODEL.md is a written polynomial analysis for a specified schoolbook array
model, not a Lean runtime theorem. The Python port is not verified extraction.
No minimal raw test-list/formula size, new relational discovery, learned policy,
historical-novelty claim or held-out benchmark is added.

All {parent['lean_count']} inherited Lean and {parent['python_count']} Python sources are byte-preserved.
Only the 25 imported inherited Lean dependencies were newly cold rebuilt.
Standalone BoundedCase201/202 are convenience copies of cases already in the batches.

Lean: {E['lean_version']}
Mathlib: {E['mathlib_commit']}
Mathematical interpretation is self-review, not independent refereeing.
''')
 (ROOT/'RESULTS.md').write_text(f'''# Retained results — Model-Theory Normalization v0.8

## Completed cold Lean run

PASS: {L['modules']} local modules, {L['task_count']} tasks,
{L['named_declarations']} named declarations audited. All 203 fixtures directly
execute the bounded algorithm. Six intended false/placeholder controls reject and
one positive accepts. Only {', '.join(L['axioms'])} occur.
Completed task-time sum: {L['runtime_sum_seconds']:.6f} seconds, not a benchmark.
No final cold task timed out or failed. Input and retained output hashes were
verified unchanged. Development attempts are separate and documented.

## Exact independent Python port audit

PASS: seed {P['seed']}, one execution {P['runtime_seconds']:.6f} seconds.
Timing includes instrumentation and tests, not a comparison with another solver.

| Check | Count |
|---|---:|
'''+''.join(f'| {k} | {v:,} |\n' for k,v in P['counts'].items())+f'''
All lists of zero, one or two generating rows are exhausted for
{P['exhaustive_configs']}, and every candidate vector is checked. Bezout inputs
are q=1..64, a=-256..256; 320 additional signed Fibonacci pairs stress long
Euclidean recursions. Ninety random prime-power configurations receive twelve
independent Smith membership comparisons each. Arithmetic is exact.

## Measured temporaries versus proved budgets

Across all 203 sources, maximum instrumented core magnitude length is
{P['max_core_bits']} bits; persistent entries reach {P['max_stored_bits']} bits.
The large eight-coordinate source modulo 65536 returns two tests in five decisions:
42 measured temporary bits, 17 stored bits, and a conservative proved magnitude
budget of 289 bits. The one-coordinate modulus-2^24 stress source returns 24 tests
in 48 decisions: 25 measured temporary bits and conservative budget 75 bits.
These are finite measurements of the specified port's arithmetic, not universal
maxima or a wall-time speedup. Source row arithmetic is logged separately.

## Reproduction boundaries

The isolated v0.7 Python audit was rerun successfully; its record is retained in
v08_evidence/parent_replay. No full old Lean suite replay is claimed. All parent
sources and the immediate parent ZIP are preserved unchanged. Final distribution
integrity and fresh-extraction checks belong to the external replay report.
''')
 (ROOT/'DEVELOPMENT_FAILURES.md').write_text(f'''# Development failures — v0.8

1. The runtime parts were recovered from the retained Library files. A preliminary
zstandard import was unavailable. Archive inspection showed XZ, and the completed
restore used Python's standard lzma module. No mathematics depended on that import.

2. An interactive streaming execution request returned StreamingExecNotEnabledContainerError
before the requested script executed. The script was then created using the ordinary
container interface, run and polled during this interaction. The restore completed.
Runtime checks and part hashes are retained; compiler/cache payloads are not bundled.

3. One enclosing dependency-bootstrap call was interrupted before a complete run
receipt. No process remained running. The remaining dependencies were rebuilt and
all selected modules later passed the separate empty-build cold audit. This partial
bootstrap is not counted as successful full verification.

4. {len(failures)} recorded draft Lean checks returned nonzero before correction.
They concerned Euclidean recursion/termination elaboration, gcd/cast/order APIs,
absolute-value syntax and rewriting, and a queried missing API name. Per-attempt
source hashes and diagnostics are retained in v08_evidence/development and indexed
in DEVELOPMENT_ATTEMPTS.json. The final proofs contain no placeholder or extra axiom.

5. The final 82-task cold audit and the new Python audit both completed successfully.
The negative-control failures in that audit are intentional mathematical rejection
tests, not failed accepted theorems. No final mathematical task timeout was relabeled
as success. Any subsequent packaging failure must be separately recorded.
''')
 print('Records generated',L['modules'],L['task_count'],P['counts']['exhaustive_membership'])
if __name__=='__main__':main()

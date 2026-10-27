from pathlib import Path
import json,sys,hashlib,platform
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 lean=json.loads((ROOT/'results_v05/LEAN_AUDIT.json').read_text());py=json.loads((ROOT/'results_v05/BACKEND_AUDIT.json').read_text());st=json.loads((ROOT/'v05_evidence/COLD_STATE.json').read_text());env=st['environment']
 assert lean['status']==py['status']=='PASS'
 def manifest(label,inputs,outputs,start,finish,seconds,assertion,bounds,command):
  return {'schema_version':2,'claim_id':label,
   'repository':{'commit':'Standalone source; immediate immutable v0.4 archive fca8f85dbf1cff576e4461fc8a1f68e9933770c65c95b8b747ba9338d967243b','dirty':True},
   'command':command,
   'environment':{'software':[{'name':'Python','version':sys.version},{'name':'Lean','version':env['lean_version']}],
       'hardware':{'platform':platform.platform(),'memory_cgroup':env['memory_cgroup'],'cpu_cgroup':env['cpu_cgroup']}},
   'mathematics':{'assertion_tested':assertion,'coefficient_domain':'Decidable commutative rings for soundness; exact ZMod(p^r) for concrete prime-power instances',
      'conventions':'All source states; FIFO test discovery; right row multiplication prepends a word; None is invalid evidence; complete queue and evidence exhaustion required.',
      'inputs':[x['path'] for x in inputs],'bounds':bounds,
      'non_claims':['No verified fast Smith producer or verified Python parser/exporter.','Guarded fallback can be expensive; no unconditional efficiency guarantee.','Raw accepted-test count is not a minimum coordinate/formula count.','No all-historical or upstream Mathlib rebuild; not a learned or held-out performance evaluation.']},
   'randomness':{'used':False,'generator':'none; frozen and exhaustive fixtures','seed':None},
   'run':{'started_at':start,'finished_at':finish,'runtime_seconds':seconds,'exit_status':0,'status':'completed',
      'resource_limits':{'memory_bytes':int(env['memory_cgroup']),'cpu_seconds':None,'max_cores':None,'max_threads':1},
      'per_command_wall_timeout_seconds':90,'missing_results':[],'invalid_results':[]},
   'input_artifacts':inputs,'execution_artifacts':[x['path'] for x in inputs],
   'declared_results':[x['path'] for x in outputs if x['kind']=='result'],'outputs':outputs,
   'checks':[{'name':'all expected outcomes','status':'PASS'},{'name':'accepted input hashes unchanged','status':'PASS'}],
   'result':'PASS','residual_risks':['Mathematical interpretation is authoring-assistant self-review.','Proofs concern literal formal inputs; informal specification fidelity is not a kernel decision.','Pinned upstream compiled dependency cache is reused.']}
 ins=[x|{'sha256_after':sha(ROOT/x['path'])} for x in st['inputs']]
 outs=[{'path':'results_v05/LEAN_AUDIT.json','sha256':sha(ROOT/'results_v05/LEAN_AUDIT.json'),'kind':'result'}]
 outs += [{'path':x['log'],'sha256':x['sha256'],'kind':'log'} for x in lean['tasks']]
 elapsed=(datetime.fromisoformat(lean['finished_at'])-datetime.fromisoformat(lean['started_at'])).total_seconds()
 ml=manifest('KMT-M5-CHECKED-MEMBERSHIP-REPLAY',ins,outs,lean['started_at'],lean['finished_at'],elapsed,
   'Verified executable membership evidence checks, complete trace replay, guarded oracle/reference equality and 203 symbolic all-word logical definitions.',
   {'local_modules':39,'generated_sources':203,'expected_outcome_tasks':47,'universal_generic_theorems':15},
   'python v05_checks/audit_lean.py --runtime '+st['runtime']+' --init; successive synchronous --batch invocations; --finish')
 ml['run']['completed_lean_commands']=[x['argv'] for x in lean['tasks']]
 ml['run']['compile_seconds']=lean['compile_seconds'];ml['run']['timing_note']='runtime_seconds is full elapsed protocol time, including intervals between synchronous batches; compile_seconds sums individual completed tasks.'
 dump(ROOT/'LEAN_MANIFEST_v05.json',ml)
 pins=[{'path':p,'sha256':h,'sha256_after':sha(ROOT/p)} for p,h in py['input_hashes'].items()]
 pout=[{'path':'results_v05/BACKEND_AUDIT.json','sha256':sha(ROOT/'results_v05/BACKEND_AUDIT.json'),'kind':'result'}]
 mp=manifest('KMT-M5-BOUNDED-PRODUCER-AUDIT',pins,pout,py['started_at'],py['finished_at'],py['seconds'],
    '203 complete traces with raw witnesses and checked literal transcription; exhaustive small-ring membership and negative controls.',py['ranges'],
    [sys.executable,'v05_checks/audit_backend.py'])
 dump(ROOT/'COMPUTATION_MANIFEST_v05.json',mp)
 counts=py['counts']
 coverage=f'''# Formalization coverage — Model-Theory Normalization v0.5

PASS: **39 local modules**, including 18 inherited dependencies and 21 new modules.
**47 expected-outcome tasks** completed, including seven controls (one acceptance,
six deliberate rejections). All **2,130 named declarations** were axiom-audited.
Counts: 990 theorems, 915 definitions, 212 abbreviations, five structures, one named
instance and seven inductive declarations. Most new declarations are generated
certificate data and consequences, not independent discoveries.

Three new generic modules contribute **15 theorems, seven definitions and one
inductive data type**. CertifiedExamples adds 11 theorems. Seventeen generated
batches cover all **203 sources** (202 frozen profiles plus one new torsion stress
fixture), with four theorem applications per source.

Only Classical.choice, Quot.sound and propext occur. No custom project axiom,
sorryAx or Lean.ofReduceBool appears. The accepted sources pass warnings as errors,
and every accepted source/input hash was unchanged across the cold run.

| Module | Exact new checked scope |
|---|---|
| CertifiedMembership | Executable finite witness checking, positive/negative soundness, exact decision semantics, incompatibility of opposing valid evidence |
| CertifiedReplay | Data-driven FIFO replay, actual QueueTrace construction, complete observable span, all-word equivalence, standard logical definition, exact reference output and uniqueness |
| CertifiedOracle | Checked advice or proved enumerative fallback, arbitrary total proposer soundness, reference-result equality, universal successful return and standard defining formula |
| CertifiedExamples | Bad evidence rejection, incomplete/trailing data rejection, nonunit arithmetic, an always-wrong proposer, empty-state-coordinate boundary |
| CheckedBatch00–16 | 203 complete evidence DATA lists evaluated by ordinary kernel reduction, each with reference-result and all-word/formula theorems |

## Boundaries

The optimized Python Smith producer and exporter are not verified programs. Every
one of the 203 retained producer traces has a kernel-checked replay application;
that does not universally verify every future producer execution. The data checker
itself is a verified executable definition. The fallback's total correctness is
proved but it can enumerate exponentially many coefficients. The no-fallback replay
used by the large instances never performs that search.

The same commutative-ring membership soundness interface does not assert scalar
separators exist for every nonmember over every ring. The guarded finite-ring oracle
remains correct without that assertion. No minimum raw test-list, formula-size,
bit-complexity or relational first-order theorem is added.

Upstream runtime: {env['lean_version']}
Mathlib source metadata pin: `{env['mathlib_commit']}`. Required pinned sources and
compiler hash were checked. Local modules were cold rebuilt; Mathlib was not.
All inherited proof files are preserved, but only 18 inherited modules are rebuilt.
Review is self-review, not independent refereeing or a novelty verdict.
'''
 (ROOT/'FORMALIZATION_COVERAGE.md').write_text(coverage)
 result=f'''# Retained results — Model-Theory Normalization v0.5

## Lean

PASS: 39 local modules, 47 expected-outcome tasks, 2,130 audited names.
15 new universal generic theorems; 203 generated data-replay sources.
Only Classical.choice, Quot.sound and propext occur. All six rejection controls
failed for their intended proof statements, not missing dependencies or timeouts.
Accepted inputs stayed unchanged. Completed compilation/check tasks sum to
{lean['compile_seconds']:.6f} seconds. This is a run measurement, not a benchmark.
The elapsed batched protocol includes pauses and is recorded separately.

## Independent exact computation

PASS: 203 complete traces, **667 acceptances and 969 skips**, 1,636 decisions.
All 202 frozen ordered results agree. All 203 emitted source/evidence/modulus/result
literals were reparsed and compared with separately supplied expected inputs.

| Check | Count |
|---|---:|
'''+''.join(f'| {k} | {v:,} |\n' for k,v in counts.items())+f'''
The exhaustive membership set contains 549 generating lists of length zero, one or
two. It covers (p,r,d)=(2,1,2),(3,1,2),(2,2,2),(2,3,1),(3,2,1), all candidate rows.
Of 6,674 decisions, 4,323 have independently reconstructed positive witnesses and
2,351 have independently verified separating witnesses. There are 762 working-basis
provenance checks. All twelve malformed/misbound traces were rejected.

The new stress source has dimension one, modulus 2^24 and 24 descending-valuation
observations. It accepts 24 tests, makes 48 decisions, but each Smith problem has at
most two rows. The old raw-row strategy reaches 24 rows on this declared fixture.
This is a matrix-size comparison, not a measured wall-time speedup.

The inherited large source has 2^128 possible initial states. Its trace has two
acceptances and three skips. The kernel checks data without enumerating those states
or the reference algorithm's coefficient tuples. No new structural holdout is claimed.

## Parent and packaging scope

The original v0.4 archive is unchanged. Its documented 202-trace Python audit was
rerun in an isolated extraction and passed; raw result is retained under v05_evidence.
This is not a fresh audit of every older p-adic or representation-theory source.
Fresh-extraction checks of this release are recorded in the separate replay report.
The optimized Python producer, parser and exporter remain unverified executables.
'''
 (ROOT/'RESULTS.md').write_text(result)
 print('records written')
if __name__=='__main__':main()
